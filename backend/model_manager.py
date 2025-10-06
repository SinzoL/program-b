#!/usr/bin/env python3
"""
Backend模型管理器 - 智能模型选择
整合P2L引擎和模型配置，提供智能模型选择功能
"""

import os
import sys
from typing import Dict, Optional
import logging

# 添加model_p2l目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
model_p2l_dir = os.path.join(current_dir, "model_p2l")
if model_p2l_dir not in sys.path:
    sys.path.insert(0, model_p2l_dir)

logger = logging.getLogger(__name__)

class ModelManager:
    """智能模型管理器"""
    
    def __init__(self):
        self.p2l_engine = None
        self._init_p2l_engine()
        self._load_configs()
    
    def _init_p2l_engine(self):
        """初始化P2L引擎"""
        try:
            from p2l_engine import P2LEngine
            import torch
            device = torch.device('cpu')
            self.p2l_engine = P2LEngine(device)
            logger.info("✅ P2L引擎初始化成功")
        except Exception as e:
            logger.warning(f"⚠️ P2L引擎初始化失败: {e}")
    
    def _load_configs(self):
        """加载模型配置"""
        try:
            from model_configs import MODEL_CONFIGS, get_model_config
            from api_configs import API_CONFIGS
            self.model_configs = MODEL_CONFIGS
            self.api_configs = API_CONFIGS
            logger.info(f"✅ 加载了 {len(MODEL_CONFIGS)} 个模型配置")
        except Exception as e:
            logger.error(f"❌ 配置加载失败: {e}")
            self.model_configs = {}
            self.api_configs = {}
    
    def select_model(self, prompt: str, task_type: str = "general") -> str:
        """智能选择最适合的模型"""
        try:
            # 使用P2L引擎进行语义分析
            if self.p2l_engine:
                complexity, language = self.p2l_engine.semantic_analysis(prompt)
                logger.info(f"🔍 语义分析: 复杂度={complexity:.3f}, 语言={language:.3f}")
            else:
                complexity, language = 0.5, 0.5
            
            # 基于分析结果选择模型
            if complexity > 0.8:
                # 高复杂度任务，选择强力模型
                candidates = ["claude-3-5-sonnet-20241022", "gpt-4o-2024-08-06", "qwen2.5-72b-instruct"]
            elif complexity > 0.5:
                # 中等复杂度任务
                candidates = ["gpt-4o-mini-2024-07-18", "claude-3-5-haiku-20241022", "qwen2.5-32b-instruct"]
            else:
                # 简单任务
                candidates = ["gpt-3.5-turbo-0125", "qwen2.5-7b-instruct", "deepseek-chat"]
            
            # 选择第一个可用的模型
            for model in candidates:
                if model in self.model_configs:
                    logger.info(f"🎯 选择模型: {model} (复杂度: {complexity:.3f})")
                    return model
            
            # 如果没有找到合适的模型，返回默认模型
            default_model = "gpt-3.5-turbo-0125"
            logger.warning(f"⚠️ 使用默认模型: {default_model}")
            return default_model
            
        except Exception as e:
            logger.error(f"❌ 模型选择失败: {e}")
            return "gpt-3.5-turbo-0125"
    
    def get_model_config(self, model_name: str) -> Optional[Dict]:
        """获取模型配置"""
        return self.model_configs.get(model_name)
    
    def get_api_config(self, provider: str) -> Optional[Dict]:
        """获取API配置"""
        return {
            "api_key": self.api_configs.get("api_keys", {}).get(provider),
            "base_url": self.api_configs.get("base_urls", {}).get(provider)
        }

def check_model_exists() -> bool:
    """快速检查默认模型文件是否存在"""
    try:
        from model_p2l.p2l_core import check_model_exists as _check
        return _check()
    except Exception:
        return False

def get_model_status() -> Dict:
    """获取当前模型状态"""
    try:
        from model_p2l.p2l_core import get_model_status as _get_status
        return _get_status()
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def print_model_status():
    """打印后端模型状态信息"""
    try:
        from model_p2l.p2l_core import print_backend_status
        print_backend_status()
    except Exception as e:
        print(f"❌ 无法获取模型状态: {e}")

__all__ = ['ModelManager', 'check_model_exists', 'get_model_status', 'print_model_status']