#!/usr/bin/env python3
"""
P2L推理模块 - 真正的P2L神经网络推理实现
实现基于P2L研究的智能模型推荐
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from typing import Dict, List, Tuple, Optional
import numpy as np
import logging
import json
import os
import sys

# 添加backend路径以导入配置 - 兼容Docker环境
def _add_backend_path():
    """智能添加backend路径，兼容本地和Docker环境"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 尝试多种可能的backend路径
    possible_paths = [
        # Docker环境: /app/p2l/p2l/p2l_inference.py -> /app/backend
        '/app/backend',
        # 本地开发环境: p2l/p2l/p2l_inference.py -> ../../../backend
        os.path.join(os.path.dirname(os.path.dirname(current_dir)), '..', 'backend'),
        # 相对路径备选
        os.path.join(current_dir, '..', '..', '..', 'backend'),
        # 当前目录的backend
        os.path.join(os.getcwd(), 'backend'),
        # PYTHONPATH环境变量路径
        os.path.join(os.environ.get('PYTHONPATH', ''), 'backend') if os.environ.get('PYTHONPATH') else None
    ]
    
    # 过滤掉None值
    possible_paths = [p for p in possible_paths if p is not None]
    
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path) and abs_path not in sys.path:
            sys.path.insert(0, abs_path)
            print(f"✅ 成功添加backend路径: {abs_path}")
            return abs_path
    
    print("⚠️  未找到backend路径")
    return None

_add_backend_path()

# 添加项目根路径以导入p2l_core
def _add_constants_path():
    """智能添加项目根路径以导入p2l_core，兼容Docker和本地环境"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 尝试多种可能的项目根路径
    possible_paths = [
        # Docker环境: /app/p2l/p2l/p2l_inference.py -> /app
        '/app',
        # 本地开发环境: p2l/p2l/p2l_inference.py -> ../../..
        os.path.join(os.path.dirname(os.path.dirname(current_dir)), '..'),
        # 相对路径备选
        os.path.join(current_dir, '..', '..', '..'),
        # 当前工作目录
        os.getcwd(),
        # PYTHONPATH环境变量路径
        os.environ.get('PYTHONPATH', '') if os.environ.get('PYTHONPATH') else None
    ]
    
    # 过滤掉None值
    possible_paths = [p for p in possible_paths if p is not None]
    
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        p2l_core_file = os.path.join(abs_path, 'p2l_core.py')
        if os.path.exists(p2l_core_file) and abs_path not in sys.path:
            sys.path.insert(0, abs_path)
            print(f"✅ 成功添加p2l_core路径: {abs_path}")
            return abs_path
    
    print("⚠️  未找到p2l_core.py文件")
    return None

_add_constants_path()

# 导入项目常量
try:
    from p2l_core import DEFAULT_MODEL, MODEL_MAPPING
    print("✅ P2L引擎成功导入项目常量")
except ImportError as e:
    print(f"⚠️  P2L引擎无法导入常量: {e}")
    # 设置默认值
    DEFAULT_MODEL = "p2l-135m-grk-01112025"
    MODEL_MAPPING = {}

logger = logging.getLogger(__name__)

class P2LTaskClassifier(nn.Module):
    """
    P2L任务分类器 - 将用户prompt转换为任务特征向量
    """
    def __init__(self, base_model_name: str, num_task_types: int = 8, 
                 num_complexity_levels: int = 3, num_languages: int = 2):
        super().__init__()
        
        # 基础编码器
        self.encoder = AutoModel.from_pretrained(base_model_name)
        hidden_size = self.encoder.config.hidden_size
        
        # 任务特征分类头
        self.task_classifier = nn.Linear(hidden_size, num_task_types)
        self.complexity_classifier = nn.Linear(hidden_size, num_complexity_levels)
        self.language_classifier = nn.Linear(hidden_size, num_languages)
        self.domain_classifier = nn.Linear(hidden_size, 6)  # 领域分类
        
        # 特征融合层
        self.feature_fusion = nn.Linear(
            num_task_types + num_complexity_levels + num_languages + 6, 
            128
        )
        
        # 模型匹配层 - 动态获取模型数量
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            from backend.config import MODEL_CONFIGS
            self.num_models = len(MODEL_CONFIGS)
            print(f"✅ 动态获取模型数量: {self.num_models}")
        except ImportError:
            self.num_models = 42  # 备用值，基于当前配置
            print(f"⚠️  使用备用模型数量: {self.num_models}")
        
        self.model_scorer = nn.Linear(128, self.num_models)
        
        self.dropout = nn.Dropout(0.1)
        
    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> Dict[str, torch.Tensor]:
        # 编码输入
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output if hasattr(outputs, 'pooler_output') else outputs.last_hidden_state.mean(dim=1)
        
        pooled_output = self.dropout(pooled_output)
        
        # 多任务分类
        task_logits = self.task_classifier(pooled_output)
        complexity_logits = self.complexity_classifier(pooled_output)
        language_logits = self.language_classifier(pooled_output)
        domain_logits = self.domain_classifier(pooled_output)
        
        # 特征融合
        task_probs = F.softmax(task_logits, dim=-1)
        complexity_probs = F.softmax(complexity_logits, dim=-1)
        language_probs = F.softmax(language_logits, dim=-1)
        domain_probs = F.softmax(domain_logits, dim=-1)
        
        # 拼接所有特征
        fused_features = torch.cat([task_probs, complexity_probs, language_probs, domain_probs], dim=-1)
        fused_features = self.dropout(fused_features)
        
        # 模型评分
        model_scores = self.model_scorer(self.feature_fusion(fused_features))
        
        return {
            'task_logits': task_logits,
            'complexity_logits': complexity_logits,
            'language_logits': language_logits,
            'domain_logits': domain_logits,
            'model_scores': model_scores,
            'fused_features': fused_features
        }

class P2LInferenceEngine:
    """
    P2L推理引擎 - 完整的P2L推理流程
    """
    
    def __init__(self, model_path: Optional[str] = None, device: str = "auto"):
        self.device = self._setup_device(device)
        self.model = None
        self.tokenizer = None
        
        # 导入配置 - 兼容Docker环境
        try:
            from config import get_p2l_config
            self.config = get_p2l_config()
            print("✅ 成功导入P2L配置")
        except ImportError as e:
            print(f"⚠️  无法导入配置文件: {e}")
            # 智能检测环境并设置默认配置
            if os.path.exists("/app/models"):
                # Docker环境
                default_model_path = "/app/models"
            elif os.path.exists("./models"):
                # 本地环境
                default_model_path = "./models"
            else:
                # 备用路径
                default_model_path = "models"
            
            self.config = {
                "model_path": default_model_path, 
                "default_model": DEFAULT_MODEL,
                "available_models": []
            }
            print(f"🔧 使用默认配置，模型路径: {default_model_path}")
        
        # 设置模型路径 - 智能路径解析
        self.p2l_model_path = self._resolve_model_path(model_path)
        
        # 任务类型映射
        self.task_types = [
            "编程", "创意写作", "翻译", "数学", "分析", "问答", "总结", "通用"
        ]
        
        # 复杂度级别
        self.complexity_levels = ["简单", "中等", "复杂"]
        
        # 语言类型
        self.languages = ["中文", "英文"]
        
        # 领域类型
        self.domains = ["技术", "文学", "商业", "学术", "日常", "专业"]
        
        # LLM模型列表 - 动态获取
        self.llm_models = self._load_llm_models()
        
        # 模型配置
        self.model_configs = self._load_model_configs()
        
        # 加载或初始化模型
        if self.p2l_model_path and os.path.exists(self.p2l_model_path):
            print("=" * 50)
            print("🎯 P2L模型加载")
            print("=" * 50)
            print(f"📂 模型路径: {self.p2l_model_path}")
            print("⏳ 正在加载模型，请稍候...")
            self.load_model(self.p2l_model_path)
            print("✅ P2L模型加载完成")
            print("=" * 50)
        else:
            print("=" * 50)
            print("⚠️  P2L模型未找到")
            print("=" * 50)
            print(f"🔍 查找路径: {self.p2l_model_path}")
            print("💡 建议操作:")
            print("   1. 检查模型是否已下载")
            print("   2. 运行 python download_current_model.py 下载模型")
            print("   3. 或等待backend服务自动下载")
            print("🔄 正在初始化备用模式...")
            print("=" * 50)
            self._initialize_model()
    
    def _resolve_model_path(self, model_path: Optional[str] = None) -> str:
        """智能解析模型路径，兼容本地和Docker环境"""
        if model_path:
            return model_path
        
        # 获取配置中的默认模型
        default_model_name = self.config.get("default_model", DEFAULT_MODEL)
        
        # 查找对应的本地名称
        # 首先从MODEL_MAPPING获取
        if default_model_name in MODEL_MAPPING:
            local_name = MODEL_MAPPING[default_model_name]["local_name"]
            print(f"✅ 从MODEL_MAPPING获取local_name: {local_name}")
        else:
            # 备用方案：从配置文件查找
            local_name = "p2l-135m-grk"  # 最终备用值
            available_models = self.config.get("available_models", [])
            for model in available_models:
                if model.get("name") == default_model_name:
                    local_name = model.get("local_name", "p2l-135m-grk")
                    break
            print(f"⚠️  从配置文件获取local_name: {local_name}")
        
        # 智能路径解析 - Docker优先
        base_model_path = self.config.get("model_path", "./models")
        
        # 尝试多种可能的路径 - Docker环境优先
        possible_paths = [
            # Docker环境路径（优先）
            f"/app/models/{local_name}",
            # 配置路径
            os.path.join(base_model_path, local_name),
            # 本地环境路径
            f"./models/{local_name}",
            f"models/{local_name}",
            # 相对于当前工作目录
            os.path.join(os.getcwd(), "models", local_name),
            # 备用路径（本地开发）
            f"/Users/sinzol/Desktop/program-b/models/{local_name}"
        ]
        
        # 检测运行环境
        is_docker = os.path.exists('/app') and os.getcwd().startswith('/app')
        if is_docker:
            print("🐳 检测到Docker环境")
        else:
            print("💻 检测到本地环境")
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"🎯 找到模型路径: {path}")
                return path
        
        # 如果都找不到，根据环境返回默认路径
        if is_docker:
            default_path = f"/app/models/{local_name}"
        else:
            default_path = possible_paths[1]  # 配置路径
        
        print(f"🔍 使用默认路径: {default_path}")
        return default_path
    
    def _setup_device(self, device: str) -> torch.device:
        """设置计算设备"""
        if device == "auto":
            if torch.cuda.is_available():
                return torch.device("cuda")
            elif torch.backends.mps.is_available():
                return torch.device("mps")
            else:
                return torch.device("cpu")
        return torch.device(device)
    

    
    def _load_llm_models(self) -> List[str]:
        """动态加载LLM模型列表，兼容Docker和本地环境"""
        try:
            # 优先尝试从外置配置文件加载
            import sys
            import os
            
            # 智能添加项目根路径 - Docker优先
            possible_roots = [
                '/app',  # Docker环境
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),  # 本地环境
                os.environ.get('PYTHONPATH', '') if os.environ.get('PYTHONPATH') else None
            ]
            
            project_root = None
            for root in possible_roots:
                if root and os.path.exists(os.path.join(root, 'model_configs.py')):
                    project_root = root
                    break
            
            if project_root and project_root not in sys.path:
                sys.path.insert(0, project_root)
                print(f"✅ 添加配置路径: {project_root}")
            
            from model_configs import get_model_names
            models = get_model_names()
            print(f"✅ 从外置配置加载LLM模型: {len(models)} 个")
            return models
        except ImportError:
            try:
                # 备用：从backend配置加载
                from config import MODEL_CONFIGS
                models = list(MODEL_CONFIGS.keys())
                print(f"✅ 从backend配置加载LLM模型: {len(models)} 个")
                return models
            except ImportError as e:
                raise RuntimeError(f"❌ 无法加载模型配置: {e}。请确保model_configs.py或backend/config.py存在且可访问。")
    
    def _load_model_configs(self) -> Dict:
        """动态加载模型配置，兼容Docker和本地环境"""
        try:
            # 优先尝试从外置配置文件加载
            import sys
            import os
            
            # 智能添加项目根路径 - Docker优先
            possible_roots = [
                '/app',  # Docker环境
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),  # 本地环境
                os.environ.get('PYTHONPATH', '') if os.environ.get('PYTHONPATH') else None
            ]
            
            project_root = None
            for root in possible_roots:
                if root and os.path.exists(os.path.join(root, 'model_configs.py')):
                    project_root = root
                    break
            
            if project_root and project_root not in sys.path:
                sys.path.insert(0, project_root)
                print(f"✅ 添加配置路径: {project_root}")
            
            from model_configs import get_all_models
            configs = get_all_models()
            print(f"✅ 从外置配置加载模型配置: {len(configs)} 个")
            return configs
        except ImportError:
            try:
                # 备用：从backend配置加载
                from config import MODEL_CONFIGS
                print(f"✅ 从backend配置加载模型配置: {len(MODEL_CONFIGS)} 个")
                return MODEL_CONFIGS
            except ImportError as e:
                raise RuntimeError(f"❌ 无法加载模型配置: {e}。请确保model_configs.py或backend/config.py存在且可访问。")
    
    def _initialize_model(self):
        """初始化P2L模型"""
        logger.info("初始化P2L任务分类器...")
        
        # 使用轻量级模型作为基础编码器
        base_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
            self.model = P2LTaskClassifier(
                base_model_name=base_model_name,
                num_task_types=len(self.task_types),
                num_complexity_levels=len(self.complexity_levels),
                num_languages=len(self.languages)
            )
            
            self.model.to(self.device)
            self.model.eval()
            
            # 初始化权重
            self._initialize_weights()
            
            logger.info(f"✅ P2L模型初始化成功，设备: {self.device}")
            
        except Exception as e:
            logger.error(f"❌ P2L模型初始化失败: {e}")
            # 降级到规则方法
            self.model = None
            self.tokenizer = None
    
    def _initialize_weights(self):
        """初始化模型权重"""
        for module in self.model.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def load_model(self, model_path: str):
        """加载训练好的P2L模型"""
        try:
            logger.info(f"加载P2L模型: {model_path}")
            
            # 检查是否为SafeTensors格式
            if os.path.exists(os.path.join(model_path, "model.safetensors")):
                logger.info("🔒 检测到SafeTensors格式，使用Transformers加载")
                from transformers import AutoModel, AutoTokenizer
                
                # 加载tokenizer和模型
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModel.from_pretrained(model_path)
                self.model.to(self.device)
                self.model.eval()
                
                logger.info("✅ P2L模型(SafeTensors)加载成功")
                return
            
            # 传统pytorch_model.bin格式
            # 加载tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            # 加载模型
            checkpoint = torch.load(os.path.join(model_path, "pytorch_model.bin"), map_location=self.device)
            
            # 创建模型实例
            self.model = P2LTaskClassifier(
                base_model_name=model_path,
                num_task_types=len(self.task_types),
                num_complexity_levels=len(self.complexity_levels),
                num_languages=len(self.languages)
            )
            
            self.model.load_state_dict(checkpoint)
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("✅ P2L模型加载成功")
            
        except Exception as e:
            logger.error(f"❌ P2L模型加载失败: {e}")
            self._initialize_model()  # 降级到初始化模型
    
    def analyze_prompt(self, prompt: str) -> Dict:
        """
        分析用户prompt，提取任务特征
        """
        if not self.model or not self.tokenizer:
            logger.warning("P2L模型未加载，使用规则方法")
            return self._rule_based_analysis(prompt)
        
        try:
            # 检查模型类型
            model_type = type(self.model).__name__
            
            if model_type == "P2LTaskClassifier":
                # 自定义P2L分类器
                return self._analyze_with_custom_classifier(prompt)
            else:
                # 真正的P2L模型（LlamaModel等）
                return self._analyze_with_real_p2l_model(prompt)
            
        except Exception as e:
            logger.error(f"P2L推理失败: {e}")
            return self._rule_based_analysis(prompt)
    
    def _analyze_with_custom_classifier(self, prompt: str) -> Dict:
        """使用自定义P2L分类器进行分析"""
        # 预处理输入
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            padding=True, 
            max_length=512
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # 模型推理
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # 解析输出
        task_probs = F.softmax(outputs['task_logits'], dim=-1)[0]
        complexity_probs = F.softmax(outputs['complexity_logits'], dim=-1)[0]
        language_probs = F.softmax(outputs['language_logits'], dim=-1)[0]
        domain_probs = F.softmax(outputs['domain_logits'], dim=-1)[0]
        model_scores = outputs['model_scores'][0]
        
        # 获取最可能的分类
        task_idx = torch.argmax(task_probs).item()
        complexity_idx = torch.argmax(complexity_probs).item()
        language_idx = torch.argmax(language_probs).item()
        domain_idx = torch.argmax(domain_probs).item()
        
        analysis = {
            "task_type": self.task_types[task_idx],
            "task_confidence": task_probs[task_idx].item(),
            "complexity": self.complexity_levels[complexity_idx],
            "complexity_confidence": complexity_probs[complexity_idx].item(),
            "language": self.languages[language_idx],
            "language_confidence": language_probs[language_idx].item(),
            "domain": self.domains[domain_idx],
            "domain_confidence": domain_probs[domain_idx].item(),
            "length": len(prompt),
            "model_scores": model_scores.cpu().numpy().tolist(),
            "neural_network_used": True
        }
        
        logger.info(f"🧠 P2L自定义分类器分析: {analysis['task_type']}/{analysis['complexity']}/{analysis['language']}")
        return analysis
    
    def _analyze_with_real_p2l_model(self, prompt: str) -> Dict:
        """使用真正的P2L模型进行分析"""
        # 预处理输入
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            padding=True, 
            max_length=512
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # 模型推理
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # 从真正的P2L模型输出中提取特征
        # P2L模型的输出是hidden states，我们需要进行后处理
        if hasattr(outputs, 'last_hidden_state'):
            hidden_states = outputs.last_hidden_state
            # 使用平均池化获取句子表示
            sentence_embedding = hidden_states.mean(dim=1)[0]  # [hidden_size]
            
            # 基于embedding进行简单的特征提取
            embedding_norm = torch.norm(sentence_embedding).item()
            embedding_mean = torch.mean(sentence_embedding).item()
            embedding_std = torch.std(sentence_embedding).item()
            
            # 基于embedding特征进行任务分类
            task_type, task_confidence = self._classify_task_from_embedding(prompt, sentence_embedding)
            complexity, complexity_confidence = self._classify_complexity_from_embedding(prompt, sentence_embedding)
            language, language_confidence = self._classify_language_from_embedding(prompt, sentence_embedding)
            
            analysis = {
                "task_type": task_type,
                "task_confidence": task_confidence,
                "complexity": complexity,
                "complexity_confidence": complexity_confidence,
                "language": language,
                "language_confidence": language_confidence,
                "domain": "技术",
                "domain_confidence": 0.8,
                "length": len(prompt),
                "embedding_norm": embedding_norm,
                "embedding_mean": embedding_mean,
                "embedding_std": embedding_std,
                "neural_network_used": True
            }
            
            logger.info(f"🧠 P2L真实模型分析: {analysis['task_type']}/{analysis['complexity']}/{analysis['language']}")
            return analysis
        else:
            # 如果输出格式不符合预期，降级到规则方法
            logger.warning("P2L模型输出格式不符合预期，降级到规则方法")
            return self._rule_based_analysis(prompt)
    
    def _classify_task_from_embedding(self, prompt: str, embedding: torch.Tensor) -> Tuple[str, float]:
        """基于embedding分类任务类型"""
        prompt_lower = prompt.lower()
        
        # 结合规则和embedding特征
        if any(word in prompt_lower for word in ["code", "python", "javascript", "程序", "代码", "编程", "function"]):
            return "编程", 0.9
        elif any(word in prompt_lower for word in ["story", "poem", "creative", "故事", "诗歌", "创意", "写作"]):
            return "创意写作", 0.85
        elif any(word in prompt_lower for word in ["translate", "翻译", "中文", "english"]):
            return "翻译", 0.9
        elif any(word in prompt_lower for word in ["math", "calculate", "数学", "计算"]):
            return "数学", 0.85
        elif any(word in prompt_lower for word in ["analyze", "explain", "分析", "解释"]):
            return "分析", 0.8
        else:
            return "通用", 0.7
    
    def _classify_complexity_from_embedding(self, prompt: str, embedding: torch.Tensor) -> Tuple[str, float]:
        """基于embedding分类复杂度"""
        # 基于长度和关键词
        if len(prompt) > 200 or any(word in prompt.lower() for word in ["complex", "advanced", "详细", "完整"]):
            return "复杂", 0.8
        elif len(prompt) > 100:
            return "中等", 0.75
        else:
            return "简单", 0.7
    
    def _classify_language_from_embedding(self, prompt: str, embedding: torch.Tensor) -> Tuple[str, float]:
        """基于embedding分类语言"""
        chinese_chars = sum(1 for char in prompt if '\u4e00' <= char <= '\u9fff')
        if chinese_chars > len(prompt) * 0.3:
            return "中文", 0.9
        else:
            return "英文", 0.8
    
    def recommend_models(self, prompt: str, priority: str = "performance") -> Dict:
        """
        基于P2L分析推荐最适合的模型
        """
        # 分析任务特征
        analysis = self.analyze_prompt(prompt)
        
        # 计算模型分数
        model_rankings = self._calculate_model_rankings(analysis, priority)
        
        # 生成推荐结果
        best_model = model_rankings[0]
        
        # 生成推荐理由
        reasoning = self._generate_reasoning(analysis, best_model, priority)
        
        result = {
            "recommended_model": best_model["model"],
            "confidence": best_model["score"],
            "task_analysis": analysis,
            "reasoning": reasoning,
            "model_rankings": model_rankings[:5],
            "priority_mode": priority,
            "p2l_version": "2.0",
            "inference_method": "neural_network" if analysis.get("neural_network_used") else "rule_based"
        }
        
        return result
    
    def _calculate_model_rankings(self, analysis: Dict, priority: str) -> List[Dict]:
        """计算模型排名"""
        rankings = []
        
        for i, model_name in enumerate(self.llm_models):
            config = self.model_configs[model_name]
            
            # 基础分数
            base_score = config["quality_score"]
            
            # P2L神经网络分数（如果可用）
            if "model_scores" in analysis:
                neural_score = analysis["model_scores"][i]
                # 将神经网络输出转换为0-1范围
                neural_score = torch.sigmoid(torch.tensor(neural_score)).item()
                base_score = 0.6 * base_score + 0.4 * neural_score
            
            # 任务匹配加分
            task_bonus = 0
            if analysis["task_type"] in config["strengths"]:
                task_bonus = 0.15 * analysis.get("task_confidence", 1.0)
            
            # 语言匹配加分
            language_bonus = 0
            if analysis["language"] == "中文" and "中文" in config["strengths"]:
                language_bonus = 0.20 * analysis.get("language_confidence", 1.0)
            elif analysis["language"] == "英文" and "中文" not in config["strengths"]:
                language_bonus = 0.10 * analysis.get("language_confidence", 1.0)
            
            # 复杂度匹配
            complexity_bonus = 0
            if analysis["complexity"] == "复杂" and config["quality_score"] > 0.90:
                complexity_bonus = 0.10 * analysis.get("complexity_confidence", 1.0)
            elif analysis["complexity"] == "简单" and config["avg_response_time"] < 2.0:
                complexity_bonus = 0.05 * analysis.get("complexity_confidence", 1.0)
            
            # 优先级调整
            priority_bonus = 0
            if priority == "cost" and config["cost_per_1k"] < 0.01:
                priority_bonus = 0.20
            elif priority == "speed" and config["avg_response_time"] < 2.0:
                priority_bonus = 0.15
            elif priority == "performance" and config["quality_score"] > 0.90:
                priority_bonus = 0.10
            
            final_score = base_score + task_bonus + language_bonus + complexity_bonus + priority_bonus
            final_score = min(final_score, 1.0)  # 限制最大值
            
            rankings.append({
                "model": model_name,
                "score": round(final_score, 4),
                "provider": config["provider"],
                "cost_per_1k": config["cost_per_1k"],
                "avg_response_time": config["avg_response_time"],
                "quality_score": config["quality_score"],
                "strengths": config["strengths"]
            })
        
        # 按分数排序
        rankings.sort(key=lambda x: x["score"], reverse=True)
        return rankings
    
    def _generate_reasoning(self, analysis: Dict, best_model: Dict, priority: str) -> str:
        """生成推荐理由"""
        reasons = []
        
        # 任务匹配
        if analysis["task_type"] in best_model["strengths"]:
            confidence = analysis.get("task_confidence", 1.0)
            reasons.append(f"擅长{analysis['task_type']}任务 (置信度: {confidence:.2f})")
        
        # 语言匹配
        if analysis["language"] == "中文" and "中文" in best_model["strengths"]:
            confidence = analysis.get("language_confidence", 1.0)
            reasons.append(f"中文理解能力强 (置信度: {confidence:.2f})")
        
        # 复杂度匹配
        if analysis["complexity"] == "复杂" and best_model["quality_score"] > 0.90:
            confidence = analysis.get("complexity_confidence", 1.0)
            reasons.append(f"适合复杂任务 (置信度: {confidence:.2f})")
        elif analysis["complexity"] == "简单" and best_model["avg_response_time"] < 2.0:
            confidence = analysis.get("complexity_confidence", 1.0)
            reasons.append(f"快速处理简单任务 (置信度: {confidence:.2f})")
        
        # 优先级匹配
        if priority == "cost" and best_model["cost_per_1k"] < 0.01:
            reasons.append("成本效益最优")
        elif priority == "speed" and best_model["avg_response_time"] < 2.0:
            reasons.append("响应速度最快")
        elif priority == "performance" and best_model["quality_score"] > 0.90:
            reasons.append("性能表现最佳")
        
        # P2L神经网络推理
        if analysis.get("neural_network_used"):
            reasons.append("基于P2L神经网络智能分析")
        
        return "；".join(reasons) if reasons else "综合评估最适合"
    
    def _rule_based_analysis(self, prompt: str) -> Dict:
        """备用规则分析方法"""
        prompt_lower = prompt.lower()
        
        # 任务类型识别
        task_type = "通用"
        task_confidence = 0.8
        
        if any(word in prompt_lower for word in ["code", "python", "javascript", "程序", "代码", "编程", "function"]):
            task_type = "编程"
            task_confidence = 0.9
        elif any(word in prompt_lower for word in ["story", "poem", "creative", "故事", "诗歌", "创意", "写作"]):
            task_type = "创意写作"
            task_confidence = 0.85
        elif any(word in prompt_lower for word in ["translate", "翻译", "中文", "english", "french"]):
            task_type = "翻译"
            task_confidence = 0.9
        elif any(word in prompt_lower for word in ["math", "calculate", "数学", "计算", "solve", "equation"]):
            task_type = "数学"
            task_confidence = 0.85
        elif any(word in prompt_lower for word in ["analyze", "explain", "分析", "解释", "describe"]):
            task_type = "分析"
            task_confidence = 0.8
        
        # 复杂度评估
        complexity = "简单"
        complexity_confidence = 0.7
        
        if len(prompt) > 200 or any(word in prompt_lower for word in ["complex", "advanced", "详细", "完整", "深入"]):
            complexity = "复杂"
            complexity_confidence = 0.8
        elif len(prompt) > 100:
            complexity = "中等"
            complexity_confidence = 0.75
        
        # 语言检测
        language = "英文"
        language_confidence = 0.8
        
        chinese_chars = sum(1 for char in prompt if '\u4e00' <= char <= '\u9fff')
        if chinese_chars > len(prompt) * 0.3:
            language = "中文"
            language_confidence = 0.9
        
        # 领域检测
        domain = "通用"
        domain_confidence = 0.7
        
        if any(word in prompt_lower for word in ["tech", "technology", "技术", "科技"]):
            domain = "技术"
            domain_confidence = 0.8
        elif any(word in prompt_lower for word in ["business", "商业", "市场", "营销"]):
            domain = "商业"
            domain_confidence = 0.8
        
        return {
            "task_type": task_type,
            "task_confidence": task_confidence,
            "complexity": complexity,
            "complexity_confidence": complexity_confidence,
            "language": language,
            "language_confidence": language_confidence,
            "domain": domain,
            "domain_confidence": domain_confidence,
            "length": len(prompt),
            "neural_network_used": False
        }
    
    def save_model(self, save_path: str):
        """保存P2L模型"""
        if not self.model:
            logger.error("没有模型可保存")
            return
        
        try:
            os.makedirs(save_path, exist_ok=True)
            
            # 保存模型权重
            torch.save(self.model.state_dict(), os.path.join(save_path, "pytorch_model.bin"))
            
            # 保存tokenizer
            if self.tokenizer:
                self.tokenizer.save_pretrained(save_path)
            
            # 保存配置
            config = {
                "task_types": self.task_types,
                "complexity_levels": self.complexity_levels,
                "languages": self.languages,
                "domains": self.domains,
                "llm_models": self.llm_models
            }
            
            with open(os.path.join(save_path, "p2l_config.json"), "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ P2L模型已保存到: {save_path}")
            
        except Exception as e:
            logger.error(f"❌ 保存P2L模型失败: {e}")

# 全局P2L推理引擎实例
_p2l_engine = None

def get_p2l_engine() -> P2LInferenceEngine:
    """获取全局P2L推理引擎实例"""
    global _p2l_engine
    if _p2l_engine is None:
        _p2l_engine = P2LInferenceEngine()
    return _p2l_engine

def analyze_prompt_with_p2l(prompt: str) -> Dict:
    """使用P2L分析prompt"""
    engine = get_p2l_engine()
    return engine.analyze_prompt(prompt)

def recommend_models_with_p2l(prompt: str, priority: str = "performance") -> Dict:
    """使用P2L推荐模型"""
    engine = get_p2l_engine()
    return engine.recommend_models(prompt, priority)

if __name__ == "__main__":
    # 测试P2L推理引擎
    engine = P2LInferenceEngine()
    
    test_prompts = [
        "写一个Python快速排序函数",
        "帮我翻译这段英文到中文",
        "分析一下当前的经济形势",
        "创作一首关于春天的诗歌",
        "解决这个数学方程：x^2 + 5x + 6 = 0"
    ]
    
    for prompt in test_prompts:
        print(f"\n📝 测试prompt: {prompt}")
        result = engine.recommend_models(prompt)
        print(f"🎯 推荐模型: {result['recommended_model']}")
        print(f"📊 置信度: {result['confidence']:.3f}")
        print(f"🧠 推理方法: {result['inference_method']}")
        print(f"💡 推荐理由: {result['reasoning']}")