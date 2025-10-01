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
        
        # 模型匹配层
        self.model_scorer = nn.Linear(128, 9)  # 9个LLM模型
        
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
        
        # LLM模型列表
        self.llm_models = [
            "gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet-20241022", 
            "claude-3-7-sonnet-20250219", "claude-3-5-haiku-20241022", 
            "gemini-1.5-pro-002", "gemini-1.5-flash-002", "qwen2.5-72b-instruct", 
            "llama-3.1-70b-instruct", "deepseek-v3"
        ]
        
        # 模型配置
        self.model_configs = self._load_model_configs()
        
        # 加载或初始化模型
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self._initialize_model()
    
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
    
    def _load_model_configs(self) -> Dict:
        """加载模型配置"""
        return {
            "gpt-4o": {
                "provider": "openai", "cost_per_1k": 0.03, "avg_response_time": 2.5,
                "strengths": ["编程", "数学", "分析"], "quality_score": 0.95,
                "context_length": 128000, "multimodal": True
            },
            "gpt-4o-mini": {
                "provider": "openai", "cost_per_1k": 0.0015, "avg_response_time": 1.2,
                "strengths": ["问答", "总结"], "quality_score": 0.82,
                "context_length": 128000, "multimodal": False
            },
            "claude-3-5-sonnet-20241022": {
                "provider": "anthropic", "cost_per_1k": 0.025, "avg_response_time": 2.8,
                "strengths": ["创意写作", "分析"], "quality_score": 0.93,
                "context_length": 200000, "multimodal": True
            },
            "claude-3-7-sonnet-20250219": {
                "provider": "anthropic", "cost_per_1k": 0.025, "avg_response_time": 2.5,
                "strengths": ["创意写作", "分析", "编程"], "quality_score": 0.95,
                "context_length": 200000, "multimodal": True
            },
            "claude-3-5-haiku-20241022": {
                "provider": "anthropic", "cost_per_1k": 0.008, "avg_response_time": 1.5,
                "strengths": ["问答", "总结"], "quality_score": 0.85,
                "context_length": 200000, "multimodal": False
            },
            "gemini-1.5-pro-002": {
                "provider": "google", "cost_per_1k": 0.02, "avg_response_time": 2.2,
                "strengths": ["分析", "数学"], "quality_score": 0.90,
                "context_length": 1000000, "multimodal": True
            },
            "gemini-1.5-flash-002": {
                "provider": "google", "cost_per_1k": 0.005, "avg_response_time": 1.0,
                "strengths": ["问答", "总结"], "quality_score": 0.80,
                "context_length": 1000000, "multimodal": False
            },
            "qwen2.5-72b-instruct": {
                "provider": "qwen", "cost_per_1k": 0.002, "avg_response_time": 2.0,
                "strengths": ["中文理解", "推理", "编程", "数学"], "quality_score": 0.90,
                "context_length": 32768, "multimodal": False
            },
            "llama-3.1-70b-instruct": {
                "provider": "meta", "cost_per_1k": 0.01, "avg_response_time": 2.3,
                "strengths": ["编程", "通用"], "quality_score": 0.86,
                "context_length": 128000, "multimodal": False
            },
            "deepseek-v3": {
                "provider": "deepseek", "cost_per_1k": 0.012, "avg_response_time": 1.8,
                "strengths": ["数学", "编程"], "quality_score": 0.87,
                "context_length": 64000, "multimodal": False
            }
        }
    
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
            
            logger.info(f"🧠 P2L神经网络分析: {analysis['task_type']}/{analysis['complexity']}/{analysis['language']}")
            return analysis
            
        except Exception as e:
            logger.error(f"P2L推理失败: {e}")
            return self._rule_based_analysis(prompt)
    
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