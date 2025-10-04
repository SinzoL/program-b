#!/usr/bin/env python3
"""
P2L Backend Package
统一的后端服务包
"""

import os
import sys

# 导入项目常量
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import DEFAULT_MODEL, MODEL_MAPPING

from .config import (
    MODEL_CONFIGS, API_CONFIG, TASK_ANALYSIS_CONFIG, 
    P2L_CONFIG, SERVICE_CONFIG,
    get_model_config, get_all_models, get_models_by_provider,
    get_api_config, get_task_config, get_p2l_config, get_service_config,
    load_env_config
)

from .llm_client import LLMClient, LLMResponse
from .p2l_engine import P2LEngine
from .task_analyzer import TaskAnalyzer
from .model_scorer import ModelScorer
from .service import P2LBackendService

__version__ = "2.0.0"
__all__ = [
    # 配置
    "MODEL_CONFIGS", "API_CONFIG", "TASK_ANALYSIS_CONFIG", 
    "P2L_CONFIG", "SERVICE_CONFIG",
    "get_model_config", "get_all_models", "get_models_by_provider",
    "get_api_config", "get_task_config", "get_p2l_config", "get_service_config",
    "load_env_config",
    
    # 核心组件
    "LLMClient", "LLMResponse",
    "P2LEngine", "TaskAnalyzer", "ModelScorer",
    "P2LBackendService"
]

# ================== P2L模型自动下载 ==================

# 使用统一的模型管理器
from .model_manager import print_model_status

# 在backend包导入时显示模型状态
print_model_status()