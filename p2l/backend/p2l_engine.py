#!/usr/bin/env python3
"""
P2L推理引擎模块
负责P2L模型加载和推理分析
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, Optional
import logging

from config import get_p2l_config

logger = logging.getLogger(__name__)

# 导入P2L推理模块
try:
    from p2l.model import load_model as load_p2l_model, generate_text
    from p2l.p2l_inference import P2LInferenceEngine
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
        """加载可用的P2L模型"""
        model_path = self.config["model_path"]
        if not os.path.exists(model_path):
            logger.warning(f"P2L模型路径不存在: {model_path}")
            return
        
        for item in os.listdir(models_dir):
            if item.startswith('p2l-') and os.path.isdir(os.path.join(models_dir, item)):
                model_path = os.path.join(models_dir, item)
                try:
                    logger.info(f"加载P2L模型: {item}")
                    tokenizer = AutoTokenizer.from_pretrained(model_path)
                    model = AutoModelForCausalLM.from_pretrained(
                        model_path,
                        torch_dtype=torch.float32,
                        device_map=None
                    )
                    model.to(self.device)
                    model.eval()
                    
                    self.p2l_models[item] = {
                        "tokenizer": tokenizer,
                        "model": model,
                        "path": model_path
                    }
                    logger.info(f"✅ P2L模型 {item} 加载成功")
                    break  # 只加载第一个可用模型
                except Exception as e:
                    logger.error(f"❌ P2L模型 {item} 加载失败: {e}")
    
    def _load_p2l_inference_engine(self):
        """加载P2L推理引擎"""
        try:
            logger.info("正在加载P2L推理引擎...")
            
            # 尝试从models目录加载
            models_dir = "./models"
            p2l_model_path = None
            
            if os.path.exists(models_dir):
                for item in os.listdir(models_dir):
                    if item.startswith('p2l-') and os.path.isdir(os.path.join(models_dir, item)):
                        p2l_model_path = os.path.join(models_dir, item)
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
            return 0.5, 0.5
        
        try:
            model_name = list(self.p2l_models.keys())[0]
            p2l_model = self.p2l_models[model_name]
            tokenizer = p2l_model["tokenizer"]
            model = p2l_model["model"]
            
            logger.info(f"🧠 使用P2L模型进行语义增强分析...")
            
            # 使用P2L模型进行语义特征提取
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = model(**inputs)
                
                # 获取隐藏状态作为语义特征
                if hasattr(outputs, 'hidden_states') and outputs.hidden_states is not None:
                    # 使用最后一层的隐藏状态
                    hidden_states = outputs.hidden_states[-1]  # [batch_size, seq_len, hidden_size]
                    # 平均池化得到句子级别的表示
                    sentence_embedding = hidden_states.mean(dim=1)  # [batch_size, hidden_size]
                    semantic_features = sentence_embedding[0]  # [hidden_size]
                else:
                    # 如果没有隐藏状态，使用logits的统计特征
                    logits = outputs.logits  # [batch_size, seq_len, vocab_size]
                    # 计算logits的统计特征作为语义表示
                    semantic_features = logits.mean(dim=(0, 1))  # [vocab_size] -> 平均到标量特征
            
            # 基于语义特征计算复杂度和语言分数
            if semantic_features.dim() == 1:
                # 使用语义特征的统计信息
                feature_mean = semantic_features.mean().item()
                feature_std = semantic_features.std().item()
                feature_max = semantic_features.max().item()
                
                # 将统计特征映射到0-1范围
                complexity_score = min(max((feature_std / (abs(feature_mean) + 1e-6)), 0), 1)
                language_score = min(max((feature_max / (abs(feature_mean) + 1e-6)), 0), 1)
            else:
                complexity_score = 0.5
                language_score = 0.5
            
            logger.info(f"🔍 语义特征分析: mean={feature_mean:.3f}, std={feature_std:.3f}, max={feature_max:.3f}")
            logger.info(f"🔍 计算得分: complexity_score={complexity_score:.3f}, language_score={language_score:.3f}")
            
            return complexity_score, language_score
            
        except Exception as e:
            logger.warning(f"P2L模型分析失败: {e}")
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
        if not self.p2l_inference_engine:
            raise Exception("P2L推理引擎未加载")
        
        logger.info(f"P2L推理请求: {code[:100]}...")
        
        # 使用P2L推理引擎
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
            "model_info": "P2L-Inference-Engine"
        }
    
    def get_loaded_models(self) -> Dict:
        """获取已加载的P2L模型信息"""
        return {
            "p2l_models": list(self.p2l_models.keys()),
            "inference_engine_available": self.p2l_inference_engine is not None,
            "p2l_available": P2L_AVAILABLE
        }