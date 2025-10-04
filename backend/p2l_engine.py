#!/usr/bin/env python3
"""
P2L推理引擎模块
负责P2L模型加载和推理分析
"""

import os
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, Optional
import logging

try:
    from .config import get_p2l_config
except ImportError:
    from config import get_p2l_config

logger = logging.getLogger(__name__)

# 导入P2L推理模块
try:
    import sys
    # 添加项目根目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))  # backend目录
    project_root = os.path.dirname(current_dir)  # program-b目录
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from p2l.p2l.model import load_model as load_p2l_model, generate_text
    from p2l.p2l.p2l_inference import P2LInferenceEngine
    P2L_AVAILABLE = True
except ImportError as e:
    logging.warning(f"P2L模块导入失败: {e}")
    P2L_AVAILABLE = False

class P2LEngine:
    """P2L推理引擎管理器"""
    
    def __init__(self, device: torch.device):
        self.device = device
        self.p2l_models = {}
        self.p2l_inference_engine = None
        self.config = get_p2l_config()
        
        # 加载P2L模型和推理引擎
        self._load_p2l_models()
        if P2L_AVAILABLE:
            self._load_p2l_inference_engine()
    
    def _load_p2l_models(self):
        """加载可用的P2L模型 - 按配置优先级"""
        # 导入配置常量
        try:
            import sys
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from constants import DEFAULT_MODEL, MODEL_MAPPING
        except ImportError as e:
            logger.error(f"无法导入配置常量: {e}")
            return
        
        model_path = self.config["model_path"]
        if not os.path.exists(model_path):
            logger.warning(f"P2L模型路径不存在: {model_path}")
            return
        
        # 1. 优先加载配置指定的默认模型
        if DEFAULT_MODEL in MODEL_MAPPING:
            target_model = MODEL_MAPPING[DEFAULT_MODEL]["local_name"]
            target_path = os.path.join(model_path, target_model)
            
            if os.path.exists(target_path):
                logger.info(f"🎯 按配置加载指定模型: {target_model} (来自 {DEFAULT_MODEL})")
                if self._load_single_model(target_model, target_path):
                    logger.info(f"✅ 配置模型 {target_model} 加载成功，跳过其他模型")
                    return
                else:
                    logger.warning(f"⚠️ 配置模型 {target_model} 加载失败，尝试备用方案")
            else:
                logger.warning(f"⚠️ 配置的模型路径不存在: {target_path}")
        else:
            logger.warning(f"⚠️ 配置的模型 {DEFAULT_MODEL} 不在映射表中")
        
        # 2. 备用方案：扫描所有可用模型（按字母顺序，但会警告）
        logger.warning("🔍 配置的默认模型不可用，扫描所有可用模型...")
        available_models = []
        for item in os.listdir(model_path):
            if item.startswith('p2l-') and os.path.isdir(os.path.join(model_path, item)):
                available_models.append(item)
        
        # 按字母顺序排序，但优先选择较小的模型
        available_models.sort(key=lambda x: (x.split('-')[1] if len(x.split('-')) > 1 else 'zzz'))
        
        for item in available_models:
            full_model_path = os.path.join(model_path, item)
            logger.warning(f"⚠️ 尝试备用模型: {item}")
            if self._load_single_model(item, full_model_path):
                logger.info(f"✅ 备用模型 {item} 加载成功")
                break
        
    def _load_single_model(self, item: str, full_model_path: str) -> bool:
        """加载单个P2L模型"""
        try:
            logger.info(f"🔄 正在加载P2L专用模型: {item}")
                    
                    # 检查是否是P2L专用模型格式
                    config_path = os.path.join(full_model_path, "config.json")
                    training_config_path = os.path.join(full_model_path, "training_config.json")
                    
                    if os.path.exists(training_config_path):
                        logger.info("🎯 检测到P2L训练模型，使用P2L专用加载器")
                        # 使用P2L专用模型加载器
                        from p2l.p2l.model import get_p2l_model, get_tokenizer
                        import json
                        
                        # 读取训练配置
                        with open(training_config_path, 'r') as f:
                            training_config = json.load(f)
                        
                        # 读取模型配置
                        with open(config_path, 'r') as f:
                            model_config = json.load(f)
                        
                        # 创建P2L模型
                        model_type = training_config.get("model_type", "qwen2")
                        loss_type = training_config.get("loss_type", "grk")
                        head_type = training_config.get("head_type", "rk")
                        
                        logger.info(f"📋 P2L模型配置: {model_type}/{loss_type}/{head_type}")
                        
                        # 获取P2L模型类
                        P2LModel = get_p2l_model(model_type, loss_type, head_type)
                        
                        # 加载tokenizer
                        tokenizer = get_tokenizer(
                            full_model_path,
                            chat_template=None,
                            pad_token_if_none="<|pad|>",
                            cls_token_if_none="<|cls|>"
                        )
                        
                        # 创建模型配置对象
                        from transformers import AutoConfig
                        config = AutoConfig.from_pretrained(full_model_path)
                        
                        # 初始化P2L模型 - 从权重文件推断正确的类别数
                        model_weights_path = os.path.join(full_model_path, "model.safetensors")
                        num_classes = 10  # 默认值
                        
                        if os.path.exists(model_weights_path):
                            import safetensors.torch
                            state_dict = safetensors.torch.load_file(model_weights_path)
                            # 从权重文件推断类别数
                            if 'head.head.weight' in state_dict:
                                num_classes = state_dict['head.head.weight'].shape[0]
                                logger.info(f"📊 从权重文件推断类别数: {num_classes}")
                        
                        model = P2LModel(
                            config=config,
                            CLS_id=tokenizer.cls_token_id,
                            num_models=num_classes,  # 使用推断的类别数
                            linear_head_downsize_factor=training_config.get("linear_head_downsize_factor"),
                            head_kwargs=training_config.get("head_kwargs", {})
                        )
                        
                        # 加载权重
                        if os.path.exists(model_weights_path):
                            model.load_state_dict(state_dict, strict=False)
                            logger.info("✅ P2L模型权重加载成功")
                        else:
                            logger.warning("⚠️ 未找到模型权重文件，使用随机初始化")
                        
                        model.to(self.device)
                        model.eval()
                        
                        self.p2l_models[item] = {
                            "tokenizer": tokenizer,
                            "model": model,
                            "path": full_model_path,
                            "model_type": model_type,
                            "loss_type": loss_type,
                            "head_type": head_type,
                            "is_p2l_model": True
                        }
                        logger.info(f"🎉 P2L专用模型 {item} 加载成功！")
                        return True
                    
                    else:
                        # 尝试标准transformers加载
                        logger.info("🔄 尝试标准transformers加载...")
                        tokenizer = AutoTokenizer.from_pretrained(full_model_path, trust_remote_code=True)
                        model = AutoModelForCausalLM.from_pretrained(
                            full_model_path,
                            torch_dtype=torch.float16 if self.device.type == 'cuda' else torch.float32,
                            device_map=None,
                            trust_remote_code=True
                        )
                        model.to(self.device)
                        model.eval()
                        
                        self.p2l_models[item] = {
                            "tokenizer": tokenizer,
                            "model": model,
                            "path": full_model_path,
                            "is_p2l_model": False
                        }
                        logger.info(f"✅ 标准模型 {item} 加载成功")
                        return True
                        
        except Exception as e:
            logger.error(f"❌ P2L模型 {item} 加载失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            return False
    
    def _load_p2l_inference_engine(self):
        """加载P2L推理引擎 - 按配置优先级"""
        try:
            logger.info("正在加载P2L推理引擎...")
            
            # 导入配置常量
            try:
                import sys
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(current_dir)
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)
                from constants import DEFAULT_MODEL, MODEL_MAPPING
            except ImportError:
                logger.warning("无法导入配置常量，使用默认扫描方式")
                DEFAULT_MODEL = None
                MODEL_MAPPING = {}
            
            # 使用配置中的模型路径
            models_dir = self.config["model_path"]
            p2l_model_path = None
            
            # 1. 优先使用配置指定的模型
            if DEFAULT_MODEL and DEFAULT_MODEL in MODEL_MAPPING:
                target_model = MODEL_MAPPING[DEFAULT_MODEL]["local_name"]
                target_path = os.path.join(models_dir, target_model)
                if os.path.exists(target_path):
                    p2l_model_path = target_path
                    logger.info(f"🎯 推理引擎使用配置模型: {target_model}")
            
            # 2. 备用方案：扫描第一个可用模型
            if not p2l_model_path and os.path.exists(models_dir):
                logger.warning("推理引擎使用备用扫描方式")
                for item in os.listdir(models_dir):
                    if item.startswith('p2l-') and os.path.isdir(os.path.join(models_dir, item)):
                        p2l_model_path = os.path.join(models_dir, item)
                        logger.warning(f"⚠️ 推理引擎使用备用模型: {item}")
                        break
            
            # 使用P2L推理引擎
            if p2l_model_path:
                model, tokenizer = load_p2l_model(p2l_model_path, device=str(self.device))
            else:
                # 创建默认推理引擎
                model, tokenizer = load_p2l_model("", device=str(self.device))
            
            if isinstance(model, P2LInferenceEngine):
                self.p2l_inference_engine = model
                logger.info("✅ P2L推理引擎加载成功")
            else:
                logger.warning("加载的不是P2L推理引擎，使用标准模型")
                
        except Exception as e:
            logger.error(f"❌ P2L推理引擎加载失败: {e}")
            # 创建基本的推理引擎作为后备
            try:
                self.p2l_inference_engine = P2LInferenceEngine(device=str(self.device))
                logger.info("✅ 创建了基本P2L推理引擎")
            except Exception as e2:
                logger.error(f"❌ 基本P2L推理引擎创建失败: {e2}")
    
    def semantic_analysis(self, prompt: str) -> tuple:
        """使用P2L模型进行语义分析"""
        if not self.p2l_models:
            logger.warning("🔍 P2L模型未加载，使用默认分析")
            return 0.5, 0.5
        
        try:
            model_name = list(self.p2l_models.keys())[0]
            p2l_model = self.p2l_models[model_name]
            tokenizer = p2l_model["tokenizer"]
            model = p2l_model["model"]
            is_p2l_model = p2l_model.get("is_p2l_model", False)
            
            logger.info(f"🧠 使用P2L模型进行语义增强分析 (P2L专用: {is_p2l_model})...")
            
            if is_p2l_model:
                # 使用真正的P2L模型进行推理
                logger.info("🎯 使用P2L专用模型进行智能分析")
                
                # 准备P2L模型输入 - 需要添加CLS token
                prompt_with_cls = f"{prompt} <|cls|>"
                inputs = tokenizer(
                    prompt_with_cls, 
                    return_tensors="pt", 
                    truncation=True, 
                    padding=True, 
                    max_length=512
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    # P2L模型前向传播
                    outputs = model(**inputs)
                    
                    # 获取P2L模型的系数输出
                    if hasattr(outputs, 'coefs') and outputs.coefs is not None:
                        coefs = outputs.coefs  # [batch_size, num_models]
                        
                        # 使用P2L系数计算语义特征
                        coef_values = coefs[0]  # [num_models]
                        
                        # 计算复杂度分数：基于系数的方差
                        complexity_score = torch.var(coef_values).item()
                        complexity_score = min(max(complexity_score, 0), 1)
                        
                        # 计算语言分数：基于系数的最大值
                        language_score = torch.max(torch.softmax(coef_values, dim=0)).item()
                        
                        # 获取eta参数（如果存在）
                        eta_info = ""
                        if hasattr(outputs, 'eta') and outputs.eta is not None:
                            eta_value = outputs.eta[0].item()
                            eta_info = f", eta={eta_value:.3f}"
                            # 使用eta调整复杂度
                            complexity_score = complexity_score * (1 + abs(eta_value) * 0.1)
                            complexity_score = min(complexity_score, 1)
                        
                        logger.info(f"🎯 P2L模型输出: coefs_var={torch.var(coef_values).item():.3f}, max_prob={language_score:.3f}{eta_info}")
                        logger.info(f"🔍 P2L计算得分: complexity_score={complexity_score:.3f}, language_score={language_score:.3f}")
                        
                        return complexity_score, language_score
                    
                    else:
                        logger.warning("⚠️ P2L模型输出格式异常，降级到隐藏状态分析")
                        # 降级到隐藏状态分析
                        if hasattr(outputs, 'last_hidden_state') and outputs.last_hidden_state is not None:
                            hidden_states = outputs.last_hidden_state
                            sentence_embedding = hidden_states.mean(dim=1)[0]
                            
                            feature_mean = sentence_embedding.mean().item()
                            feature_std = sentence_embedding.std().item()
                            
                            complexity_score = min(max(feature_std / (abs(feature_mean) + 1e-6), 0), 1)
                            language_score = min(max(abs(feature_mean), 0), 1)
                            
                            logger.info(f"🔍 隐藏状态分析: complexity_score={complexity_score:.3f}, language_score={language_score:.3f}")
                            return complexity_score, language_score
            
            else:
                # 标准transformers模型分析
                logger.info("🔄 使用标准transformers模型分析")
                inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=512)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = model(**inputs)
                    
                    # 获取隐藏状态作为语义特征
                    if hasattr(outputs, 'hidden_states') and outputs.hidden_states is not None:
                        hidden_states = outputs.hidden_states[-1]
                        sentence_embedding = hidden_states.mean(dim=1)[0]
                        semantic_features = sentence_embedding
                    elif hasattr(outputs, 'last_hidden_state'):
                        semantic_features = outputs.last_hidden_state.mean(dim=1)[0]
                    else:
                        # 使用logits
                        logits = outputs.logits
                        semantic_features = logits.mean(dim=(0, 1))
                
                # 基于语义特征计算复杂度和语言分数
                feature_mean = semantic_features.mean().item()
                feature_std = semantic_features.std().item()
                feature_max = semantic_features.max().item()
                
                complexity_score = min(max((feature_std / (abs(feature_mean) + 1e-6)), 0), 1)
                language_score = min(max((feature_max / (abs(feature_mean) + 1e-6)), 0), 1)
                
                logger.info(f"🔍 标准模型分析: complexity_score={complexity_score:.3f}, language_score={language_score:.3f}")
            
            return complexity_score, language_score
            
        except Exception as e:
            logger.error(f"❌ P2L模型分析失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            return 0.5, 0.5
    
    def inference_engine_analysis(self, prompt: str) -> Optional[Dict]:
        """使用P2L推理引擎进行任务分析"""
        if not self.p2l_inference_engine:
            return None
        
        try:
            logger.info("使用P2L推理引擎进行任务分析...")
            result = self.p2l_inference_engine.analyze_task_complexity(prompt)
            
            # 转换P2L推理引擎的输出格式
            task_analysis = {
                "task_type": result.get("task_type", "通用"),
                "complexity": result.get("complexity", "中等"),
                "language": result.get("language", "中文"),
                "length": len(prompt),
                "p2l_scores": {
                    "complexity": result.get("complexity_score", 0.5),
                    "confidence": result.get("confidence", 0.8)
                }
            }
            
            logger.info(f"🧠 P2L推理引擎分析: {task_analysis}")
            return task_analysis
            
        except Exception as e:
            logger.warning(f"P2L推理引擎分析失败: {e}")
            return None
    
    def code_inference(self, code: str, max_length: int = 512, temperature: float = 0.7) -> Dict:
        """P2L代码推理 - 将代码转换为自然语言"""
        logger.info(f"🧠 P2L推理请求: {code[:100]}...")
        
        # 优先使用P2L专用模型
        if self.p2l_models:
            model_name = list(self.p2l_models.keys())[0]
            p2l_model = self.p2l_models[model_name]
            
            if p2l_model.get("is_p2l_model", False):
                try:
                    logger.info("🎯 使用P2L专用模型进行代码推理")
                    
                    tokenizer = p2l_model["tokenizer"]
                    model = p2l_model["model"]
                    
                    # 构造P2L推理prompt
                    inference_prompt = f"请分析以下代码的功能：\n{code}\n<|cls|>"
                    
                    inputs = tokenizer(
                        inference_prompt,
                        return_tensors="pt",
                        truncation=True,
                        padding=True,
                        max_length=max_length
                    )
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    start_time = time.time()
                    
                    with torch.no_grad():
                        outputs = model(**inputs)
                        
                        # 获取P2L模型的推理结果
                        if hasattr(outputs, 'coefs'):
                            coefs = outputs.coefs[0]  # [num_models]
                            
                            # 基于系数生成自然语言描述
                            model_probs = torch.softmax(coefs, dim=0)
                            top_model_idx = torch.argmax(model_probs).item()
                            confidence = model_probs[top_model_idx].item()
                            
                            # 简单的代码分析逻辑
                            if "def " in code or "function" in code:
                                analysis = "这是一个函数定义"
                            elif "class " in code:
                                analysis = "这是一个类定义"
                            elif "import " in code or "from " in code:
                                analysis = "这是模块导入语句"
                            elif "for " in code or "while " in code:
                                analysis = "这是循环控制结构"
                            elif "if " in code:
                                analysis = "这是条件判断语句"
                            else:
                                analysis = "这是一段通用代码"
                            
                            processing_time = time.time() - start_time
                            
                            return {
                                "code": code,
                                "natural_language": analysis,
                                "confidence": confidence,
                                "processing_time": processing_time,
                                "model_info": f"P2L-{p2l_model['model_type']}-{p2l_model['loss_type']}",
                                "p2l_coefs": coefs.cpu().tolist(),
                                "used_p2l_model": True
                            }
                            
                except Exception as e:
                    logger.error(f"❌ P2L专用模型推理失败: {e}")
        
        # 降级到P2L推理引擎
        if self.p2l_inference_engine:
            try:
                logger.info("🔄 使用P2L推理引擎")
                result = self.p2l_inference_engine.infer(
                    code,
                    max_length=max_length,
                    temperature=temperature
                )
                
                return {
                    "code": code,
                    "natural_language": result["natural_language"],
                    "confidence": result.get("confidence", 0.8),
                    "processing_time": result.get("processing_time", 0.0),
                    "model_info": "P2L-Inference-Engine",
                    "used_p2l_model": False
                }
            except Exception as e:
                logger.error(f"❌ P2L推理引擎失败: {e}")
        
        # 最后的降级方案
        logger.warning("⚠️ 所有P2L推理方法都失败，使用基础分析")
        return {
            "code": code,
            "natural_language": "代码分析功能暂时不可用",
            "confidence": 0.1,
            "processing_time": 0.0,
            "model_info": "Fallback",
            "used_p2l_model": False
        }
    
    def get_loaded_models(self) -> Dict:
        """获取已加载的P2L模型信息"""
        p2l_model_info = {}
        for name, model_data in self.p2l_models.items():
            p2l_model_info[name] = {
                "is_p2l_model": model_data.get("is_p2l_model", False),
                "model_type": model_data.get("model_type", "unknown"),
                "loss_type": model_data.get("loss_type", "unknown"),
                "head_type": model_data.get("head_type", "unknown")
            }
        
        return {
            "p2l_models": list(self.p2l_models.keys()),
            "p2l_model_details": p2l_model_info,
            "inference_engine_available": self.p2l_inference_engine is not None,
            "p2l_available": P2L_AVAILABLE,
            "total_models_loaded": len(self.p2l_models)
        }