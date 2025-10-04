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

def ensure_p2l_model():
    """确保P2L默认模型存在，如果不存在则自动下载"""
    try:
        # 导入配置
        config = get_p2l_config()
        models_dir = config['model_path']
        default_model = config.get('default_model', DEFAULT_MODEL)
        available_models = config.get('available_models', [])
        
        # 查找默认模型对应的配置
        default_model_config = None
        for model in available_models:
            if model['name'] == default_model:
                default_model_config = model
                break
        
        if not default_model_config:
            print(f"⚠️  未找到默认模型配置: {default_model}")
            return False
        
        # 检查本地模型路径
        local_model_path = os.path.join(models_dir, default_model_config['local_name'])
        
        if os.path.exists(local_model_path):
            print(f"✅ P2L模型已存在: {local_model_path}")
            return True
        
        print(f"🔍 未找到P2L模型: {local_model_path}")
        print(f"🔄 开始下载默认模型: {default_model_config['repo_id']}")
        
        # 尝试下载模型
        try:
            from huggingface_hub import snapshot_download
            
            # 确保models目录存在
            os.makedirs(models_dir, exist_ok=True)
            
            # 下载模型
            downloaded_path = snapshot_download(
                repo_id=default_model_config['repo_id'],
                local_dir=local_model_path,
                local_dir_use_symlinks=False,
                resume_download=True
            )
            
            print(f"✅ P2L模型下载成功: {downloaded_path}")
            return True
            
        except ImportError:
            print("❌ 缺少huggingface_hub依赖，无法下载模型")
            print("   请运行: pip install huggingface_hub")
            return False
        except Exception as e:
            print(f"❌ P2L模型下载失败: {e}")
            print(f"   尝试手动下载: git clone https://huggingface.co/{default_model_config['repo_id']} {local_model_path}")
            return False
            
    except Exception as e:
        print(f"❌ P2L模型检查失败: {e}")
        return False

# 在backend初始化时检查P2L模型
print("🚀 初始化Backend服务...")
model_ready = ensure_p2l_model()

if not model_ready:
    print("⚠️  P2L模型未准备就绪，服务将以降级模式运行")
else:
    print("🎉 P2L模型准备完成，服务可正常运行")