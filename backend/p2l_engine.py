#!/usr/bin/env python3
"""
P2L引擎 - 加载并使用真实的P2L模型
基于下载的 p2l-135m-grk 模型进行Bradley-Terry系数计算
"""

import json
import logging
import numpy as np
import torch
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import os
import sys
from pathlib import Path

# 添加p2l路径到系统路径
current_dir = Path(__file__).parent
p2l_project_dir = current_dir.parent / 'p2l'
if str(p2l_project_dir) not in sys.path:
    sys.path.insert(0, str(p2l_project_dir))

logger = logging.getLogger(__name__)

@dataclass
class P2LCoefficients:
    """P2L系数数据结构"""
    model_coefficients: Dict[str, float]  # Bradley-Terry系数
    eta: Optional[float] = None  # 平局参数
    gamma: Optional[float] = None  # 质量参数
    confidence_scores: Optional[Dict[str, float]] = None  # 置信度分数
    model_list: List[str] = None  # 模型列表

class P2LEngine:
    """P2L引擎 - 使用下载的真实P2L模型"""
    
    def __init__(self, model_path: str = None, device: str = "cpu"):
        """
        初始化P2L引擎
        
        Args:
            model_path: P2L模型路径
            device: 计算设备
        """
        self.device = device
        self.is_loaded = False
        
        # 设置模型路径
        if model_path is None:
            self.model_path = current_dir / "model_p2l" / "models" / "p2l-135m-grk"
        else:
            self.model_path = Path(model_path)
        
        logger.info(f"🔍 P2L模型路径: {self.model_path}")
        
        # 尝试加载P2L模型
        try:
            self._load_p2l_model()
        except Exception as e:
            logger.warning(f"⚠️ P2L模型加载失败，将使用模拟模式: {e}")
            self.is_loaded = False
        
    def _load_model_config(self) -> Dict:
        """加载模型配置"""
        config_path = self.model_path / "config.json"
        training_config_path = self.model_path / "training_config.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                model_config = json.load(f)
            
            # 加载训练配置
            if training_config_path.exists():
                with open(training_config_path, 'r', encoding='utf-8') as f:
                    training_config = json.load(f)
                model_config.update(training_config)
            
            logger.info(f"✅ 模型配置加载成功")
            return model_config
            
        except Exception as e:
            logger.error(f"❌ 模型配置加载失败: {e}")
            raise
    
    def _load_model_list(self) -> List[str]:
        """加载模型列表"""
        model_list_path = self.model_path / "model_list.json"
        
        try:
            with open(model_list_path, 'r', encoding='utf-8') as f:
                model_list = json.load(f)
            
            logger.info(f"✅ 模型列表加载成功，共 {len(model_list)} 个模型")
            return model_list
            
        except Exception as e:
            logger.error(f"❌ 模型列表加载失败: {e}")
            raise
    
    def _load_p2l_model(self):
        """加载P2L模型和tokenizer"""
        # 检查模型是否存在
        if not self.model_path.exists():
            raise FileNotFoundError(f"P2L模型路径不存在: {self.model_path}")
        
        # 加载模型配置和模型列表
        self.model_config = self._load_model_config()
        self.model_list = self._load_model_list()
        self.num_models = len(self.model_list)
        
        try:
            # 导入P2L模型相关模块
            from p2l.model import get_p2l_model
            from transformers import AutoTokenizer
            
            logger.info(f"🔍 开始加载P2L模型...")
            
            # 加载tokenizer
            tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))
            tokenizer.truncation_side = "left"
            tokenizer.padding_side = "right"
            
            # 添加特殊token
            if "pad_token" not in tokenizer.special_tokens_map:
                tokenizer.add_special_tokens({"pad_token": "<|pad|>"})
            if "cls_token" not in tokenizer.special_tokens_map:
                tokenizer.add_special_tokens({"cls_token": "<|cls|>"})
            
            logger.info(f"✅ Tokenizer加载成功")
            
            # 获取P2L模型类
            model_type = self.model_config.get("model_type", "llama")
            head_type = self.model_config.get("head_type", "rk")
            loss_type = self.model_config.get("loss_type", "bag")
            
            logger.info(f"🎯 模型参数: type={model_type}, head={head_type}, loss={loss_type}")
            
            P2LModelClass = get_p2l_model(model_type, loss_type, head_type)
            
            # 加载模型
            model = P2LModelClass.from_pretrained(
                str(self.model_path),
                CLS_id=tokenizer.cls_token_id,
                num_models=self.num_models,
                dtype=torch.bfloat16 if self.device != "cpu" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
            if self.device != "cuda":
                model = model.to(self.device)
            
            model.eval()
            
            self.model = model
            self.tokenizer = tokenizer
            self.is_loaded = True
            
            logger.info(f"✅ P2L模型加载成功")
            logger.info(f"📊 支持模型数量: {self.num_models}")
            logger.info(f"🎯 模型设备: {next(model.parameters()).device}")
            logger.info(f"🎯 模型精度: {next(model.parameters()).dtype}")
            
        except Exception as e:
            logger.error(f"❌ P2L模型加载失败: {e}")
            raise
    
    def get_bradley_terry_coefficients(self, prompt: str, model_list: List[str]) -> np.ndarray:
        """
        获取Bradley-Terry系数
        
        Args:
            prompt: 用户提示词
            model_list: 要评估的模型列表
            
        Returns:
            np.ndarray: Bradley-Terry系数数组
        """
        print(f"🎯 【P2L引擎】计算Bradley-Terry系数...")
        print(f"📝 提示词: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
        print(f"📋 目标模型数量: {len(model_list)}")
        
        if not self.is_loaded:
            print(f"⚠️ P2L模型未加载，使用模拟系数")
            logger.warning("P2L模型未加载，使用模拟系数")
            return self._generate_mock_coefficients(len(model_list))
        
        try:
            # 获取完整的P2L系数对象
            coefficients = self.get_coefficients_for_prompt(prompt, model_list)
            
            # 提取系数数组
            coef_array = np.array([
                coefficients.model_coefficients.get(model, 0.5) 
                for model in model_list
            ])
            
            print(f"✅ P2L推理成功，获得{len(coef_array)}个系数")
            print(f"📊 系数范围: [{coef_array.min():.3f}, {coef_array.max():.3f}]")
            
            return coef_array
            
        except Exception as e:
            print(f"❌ P2L推理失败: {e}")
            logger.error(f"P2L推理失败: {e}")
            return self._generate_mock_coefficients(len(model_list))
    
    def get_coefficients_for_prompt(self, prompt: str, models: List[str] = None) -> P2LCoefficients:
        """
        使用真实P2L模型计算Bradley-Terry系数
        
        Args:
            prompt: 用户提示词
            models: 要评估的模型列表，如果为None则使用所有模型
            
        Returns:
            P2LCoefficients: P2L系数对象
        """
        if not self.is_loaded:
            # 如果模型未加载，返回模拟系数
            if models is None:
                models = ["gpt-4o", "claude-3.5-sonnet", "gemini-pro"]
            
            mock_coefs = self._generate_mock_coefficients(len(models))
            model_coefficients = {model: float(coef) for model, coef in zip(models, mock_coefs)}
            confidence_scores = {model: 0.5 for model in models}
            
            return P2LCoefficients(
                model_coefficients=model_coefficients,
                eta=0.1,
                gamma=1.0,
                confidence_scores=confidence_scores,
                model_list=models
            )
        
        try:
            logger.info(f"🔍 开始P2L推理...")
            logger.info(f"📝 提示词长度: {len(prompt)}")
            
            # 准备输入
            messages = [{"role": "user", "content": prompt}]
            
            # 使用chat template格式化
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False,
                add_special_tokens=False,
            )
            
            # 添加CLS token
            formatted_prompt = formatted_prompt + self.tokenizer.cls_token
            
            logger.info(f"🎯 格式化提示词: {formatted_prompt[:100]}...")
            
            # Tokenize
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                max_length=8192,
                padding=True,
                truncation=True,
                add_special_tokens=False
            )
            
            # 移动到设备
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            logger.info(f"🎯 输入形状: {inputs['input_ids'].shape}")
            
            # 模型推理
            with torch.no_grad():
                outputs = self.model(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"]
                )
            
            # 提取系数
            coefs = outputs.coefs.cpu().float().numpy()[0]  # [num_models]
            eta = outputs.eta.cpu().float().item() if outputs.eta is not None else None
            gamma = outputs.gamma.cpu().float().item() if outputs.gamma is not None else None
            
            logger.info(f"✅ P2L推理完成")
            logger.info(f"🎯 系数形状: {coefs.shape}")
            logger.info(f"🎯 Eta参数: {eta}")
            logger.info(f"🎯 Gamma参数: {gamma}")
            
            # 创建模型系数字典
            if models is None:
                target_models = self.model_list
            else:
                target_models = models
            
            model_coefficients = {}
            confidence_scores = {}
            
            for model_name in target_models:
                if model_name in self.model_list:
                    model_idx = self.model_list.index(model_name)
                    coef_value = float(coefs[model_idx])
                    model_coefficients[model_name] = coef_value
                    
                    # 计算置信度分数（基于系数的sigmoid变换）
                    confidence = float(torch.sigmoid(torch.tensor(coef_value)).item())
                    confidence_scores[model_name] = confidence
                else:
                    logger.warning(f"⚠️ 模型 {model_name} 不在P2L模型列表中")
            
            logger.info(f"📊 成功计算 {len(model_coefficients)} 个模型的系数")
            
            # 显示前5个系数用于调试
            sorted_coefs = sorted(model_coefficients.items(), key=lambda x: x[1], reverse=True)
            logger.info(f"🏆 前5名模型系数:")
            for i, (model, coef) in enumerate(sorted_coefs[:5]):
                logger.info(f"   {i+1}. {model}: {coef:.4f}")
            
            return P2LCoefficients(
                model_coefficients=model_coefficients,
                eta=eta,
                gamma=gamma,
                confidence_scores=confidence_scores,
                model_list=target_models
            )
            
        except Exception as e:
            logger.error(f"❌ P2L推理失败: {e}")
            raise
    
    def calculate_win_probabilities(self, coefficients: P2LCoefficients, 
                                  model_pairs: List[Tuple[str, str]]) -> Dict[Tuple[str, str], Dict[str, float]]:
        """
        使用P2L系数计算模型对之间的胜率概率
        使用GRK (Generalized Rao-Kupper) 模型
        """
        probabilities = {}
        
        # 使用真实的eta参数
        eta = coefficients.eta if coefficients.eta is not None else 0.1
        theta = np.exp(eta) + 1.000001
        
        for model_a, model_b in model_pairs:
            if model_a in coefficients.model_coefficients and model_b in coefficients.model_coefficients:
                coef_a = coefficients.model_coefficients[model_a]
                coef_b = coefficients.model_coefficients[model_b]
                
                # GRK模型计算概率
                pi_a = np.exp(coef_a)
                pi_b = np.exp(coef_b)
                pi_gamma = 1.0  # bag模型中gamma固定为1
                
                # 计算各种结果的概率
                p_win = pi_a / (pi_a + theta * pi_b + pi_gamma)
                p_lose = pi_b / (pi_b + theta * pi_a + pi_gamma)
                p_tie_bb = pi_gamma / (pi_gamma + pi_a + pi_b)  # 双方都不好的平局
                p_tie = 1.0 - p_win - p_lose - p_tie_bb  # 正常平局
                
                probabilities[(model_a, model_b)] = {
                    "win": float(p_win),
                    "lose": float(p_lose),
                    "tie": float(p_tie),
                    "tie_bothbad": float(p_tie_bb)
                }
        
        return probabilities
    
    def get_model_rankings(self, coefficients: P2LCoefficients) -> List[Tuple[str, float]]:
        """获取基于P2L系数的模型排名"""
        rankings = [(model, coef) for model, coef in coefficients.model_coefficients.items()]
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"📊 模型排名计算完成，前3名:")
        for i, (model, coef) in enumerate(rankings[:3]):
            logger.info(f"   {i+1}. {model}: {coef:.4f}")
        
        return rankings
    
    def _generate_mock_coefficients(self, num_models: int) -> np.ndarray:
        """生成模拟的Bradley-Terry系数"""
        print(f"🎲 生成{num_models}个模拟Bradley-Terry系数...")
        
        # 设置随机种子以确保可重现性
        np.random.seed(42)
        
        # 生成符合实际分布的系数
        # Bradley-Terry系数通常在0.2-1.5之间，大多数在0.4-1.2之间
        coefficients = np.random.beta(2, 2, num_models) * 1.0 + 0.2
        
        # 添加一些随机性，但保持合理范围
        coefficients += np.random.normal(0, 0.1, num_models)
        coefficients = np.clip(coefficients, 0.2, 1.5)
        
        print(f"📊 模拟系数统计: 最小={coefficients.min():.3f}, 最大={coefficients.max():.3f}, 平均={coefficients.mean():.3f}")
        
        return coefficients
    
    def get_supported_models(self) -> List[str]:
        """获取P2L模型支持的所有模型列表"""
        if self.is_loaded:
            return self.model_list.copy()
        else:
            return []
    
    def check_model_support(self, model_name: str) -> bool:
        """检查模型是否被P2L支持"""
        if self.is_loaded:
            return model_name in self.model_list
        else:
            return False
    
    def get_debug_info(self, prompt: str, models: List[str] = None) -> Dict:
        """获取调试信息"""
        if not self.is_loaded:
            return {
                "engine_status": "模拟模式",
                "model_loaded": False,
                "prompt_length": len(prompt),
                "target_models": len(models) if models else 0
            }
        
        coefficients = self.get_coefficients_for_prompt(prompt, models)
        
        return {
            "model_path": str(self.model_path),
            "model_type": self.model_config.get("model_type", "unknown"),
            "head_type": self.model_config.get("head_type", "unknown"),
            "loss_type": self.model_config.get("loss_type", "unknown"),
            "total_models_supported": self.num_models,
            "prompt_length": len(prompt),
            "eta": coefficients.eta,
            "gamma": coefficients.gamma,
            "model_count": len(coefficients.model_coefficients),
            "coefficients": coefficients.model_coefficients,
            "confidence_scores": coefficients.confidence_scores,
            "device": str(self.device),
            "model_device": str(next(self.model.parameters()).device) if self.is_loaded else "N/A",
            "model_dtype": str(next(self.model.parameters()).dtype) if self.is_loaded else "N/A"
        }
    
    def get_model_info(self) -> Dict:
        """获取P2L模型信息"""
        if not self.is_loaded:
            return {
                "engine_type": "P2L Engine (模拟模式)",
                "model_loaded": False,
                "status": "P2L模型未加载，使用模拟系数"
            }
        
        return {
            "engine_type": "P2L Engine (真实模式)",
            "model_path": str(self.model_path),
            "base_model": self.model_config.get("_name_or_path", "unknown"),
            "model_type": self.model_config.get("model_type", "unknown"),
            "head_type": self.model_config.get("head_type", "unknown"),
            "loss_type": self.model_config.get("loss_type", "unknown"),
            "supported_models": self.num_models,
            "device": self.device,
            "parameters": "135M",
            "architecture": "SmolLM2 + P2L Head",
            "features": [
                "真实Bradley-Terry系数计算",
                "GRK概率模型",
                "130+个模型支持",
                "Rao-Kupper头部",
                "BAG损失函数"
            ]
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取P2L引擎状态"""
        return {
            "is_loaded": self.is_loaded,
            "model_path": str(self.model_path) if hasattr(self, 'model_path') else None,
            "supported_models": len(self.model_list) if self.is_loaded else 0,
            "device": self.device,
            "model_info": self.get_model_info()
        }
    
    def print_status(self):
        """打印P2L引擎状态"""
        status = self.get_status()
        
        print(f"\n🔧 【P2L引擎状态】")
        print(f"✅ 加载状态: {'已加载' if status['is_loaded'] else '未加载'}")
        print(f"📁 模型路径: {status['model_path']}")
        print(f"📊 支持模型: {status['supported_models']} 个")
        print(f"🖥️ 设备: {status['device']}")
        
        model_info = status['model_info']
        print(f"🎯 引擎类型: {model_info['engine_type']}")
        
        if status['is_loaded']:
            print(f"🏗️ 架构: {model_info['architecture']}")
            print(f"🎯 特性: {', '.join(model_info['features'][:3])}...")

# 全局P2L引擎实例
_p2l_engine = None

def get_p2l_engine() -> P2LEngine:
    """获取全局P2L引擎实例"""
    global _p2l_engine
    if _p2l_engine is None:
        _p2l_engine = P2LEngine()
    return _p2l_engine

def create_p2l_engine(model_path: str = None, device: str = "cpu") -> P2LEngine:
    """创建新的P2L引擎实例"""
    return P2LEngine(model_path, device)

# 测试函数
def test_p2l_engine():
    """测试P2L引擎"""
    print("🧪 测试P2L引擎...")
    
    try:
        engine = P2LEngine()
        engine.print_status()
        
        # 测试提示词
        test_prompts = [
            "写一个Python快速排序算法",
            "解释机器学习的基本概念",
            "帮我翻译这段英文：Hello World"
        ]
        
        # 测试模型列表
        test_models = ["gpt-4o-2024-08-06", "claude-3-5-sonnet-20241022", "gemini-1.5-pro-002"]
        
        for prompt in test_prompts:
            print(f"\n📝 测试提示词: {prompt}")
            print("-" * 50)
            
            # 测试Bradley-Terry系数计算
            coefficients_array = engine.get_bradley_terry_coefficients(prompt, test_models)
            print(f"📊 Bradley-Terry系数: {coefficients_array}")
            
            # 测试完整系数对象
            if engine.is_loaded:
                coefficients = engine.get_coefficients_for_prompt(prompt, test_models)
                rankings = engine.get_model_rankings(coefficients)
                
                print(f"🏆 前3名模型:")
                for i, (model, coef) in enumerate(rankings[:3]):
                    confidence = coefficients.confidence_scores.get(model, 0.5)
                    print(f"   {i+1}. {model}: 系数={coef:.4f}, 置信度={confidence:.3f}")
        
        print(f"\n✅ P2L引擎测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_p2l_engine()