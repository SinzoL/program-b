#!/usr/bin/env python3
"""
P2L Backend Package - 简化版本
统一的后端服务包，移除冗余依赖
"""

import os
import sys

# 导入项目核心模块
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from p2l_core import DEFAULT_MODEL, MODEL_MAPPING
except ImportError:
    # 备用方案
    DEFAULT_MODEL = "p2l-135m-grk-01112025"
    MODEL_MAPPING = {}

# 核心配置导入
from .config import (
    get_model_config, get_all_models, get_models_by_provider,
    get_api_config, get_task_config, get_p2l_config, get_service_config,
    load_env_config
)

# 核心组件导入
from .unified_client import UnifiedLLMClient, LLMResponse
from .p2l_engine import P2LEngine
from .p2l_model_scorer import P2LModelScorer
from .service_p2l_native import P2LNativeBackendService

__version__ = "3.0.0"
__all__ = [
    # 配置函数
    "get_model_config", "get_all_models", "get_models_by_provider",
    "get_api_config", "get_task_config", "get_p2l_config", "get_service_config",
    "load_env_config",
    
    # 核心组件
    "UnifiedLLMClient", "LLMResponse",
    "P2LEngine", "P2LModelScorer",
    "P2LNativeBackendService"
]

# 初始化环境配置
load_env_config()

print(f"✅ P2L Backend v{__version__} 初始化完成")