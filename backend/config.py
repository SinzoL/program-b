#!/usr/bin/env python3
"""
Backend配置文件 - 统一版本
所有配置从 model_p2l 目录导入，保持简洁
"""

import os
import sys
from typing import Dict, Any

# 添加model_p2l目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
model_p2l_dir = os.path.join(current_dir, "model_p2l")
if model_p2l_dir not in sys.path:
    sys.path.insert(0, model_p2l_dir)

# 导入项目核心常量
try:
    from p2l_core import DEFAULT_MODEL, MODEL_MAPPING
except ImportError:
    # 如果无法导入，设置默认值
    DEFAULT_MODEL = "p2l-135m-grk-01112025"
    MODEL_MAPPING = {}

# 导入所有配置
try:
    from model_configs import MODEL_CONFIGS, get_model_config, get_all_models, get_models_by_provider
    from api_configs import API_CONFIGS, TASK_ANALYSIS_CONFIG, SERVICE_CONFIG, load_env_config, DEFAULT_CONFIG
    print("✅ 成功导入model_p2l配置文件")
except ImportError as e:
    raise RuntimeError(f"❌ 无法导入model_p2l配置文件: {e}。请确保 model_p2l 目录中的配置文件存在且可访问。")

# 验证配置加载
if not MODEL_CONFIGS:
    raise RuntimeError("❌ 模型配置加载失败！")

# ================== P2L引擎配置 ==================
def _get_model_path():
    """智能获取模型路径，兼容本地和Docker环境"""
    if os.path.exists('/app') and os.getcwd().startswith('/app'):
        return "/app/models"
    else:
        # 新的模型路径：backend/model_p2l/models
        return os.path.join(current_dir, "model_p2l", "models")

P2L_CONFIG = {
    "model_path": _get_model_path(),
    "default_model": DEFAULT_CONFIG.get("DEFAULT_MODEL", DEFAULT_MODEL),
    "inference_params": {
        "max_length": 512,
        "temperature": DEFAULT_CONFIG.get("TEMPERATURE", 0.7),
        "top_p": 0.9,
        "top_k": 50,
        "repetition_penalty": 1.1,
        "do_sample": True,
        "max_tokens": DEFAULT_CONFIG.get("MAX_TOKENS", 2000)
    },
    "semantic_analysis": {
        "complexity_factors": {
            "length_weight": 0.2,
            "keyword_weight": 0.3,
            "structure_weight": 0.3,
            "domain_weight": 0.2
        },
        "language_factors": {
            "chinese_boost": 0.1,
            "code_boost": 0.15,
            "mixed_penalty": 0.05
        }
    }
}

# ================== 统一接口函数 ==================
def get_model_config(model_name: str) -> Dict[str, Any]:
    """获取指定模型的配置"""
    from model_configs import get_model_config as external_get_model_config
    return external_get_model_config(model_name)

def get_all_models() -> Dict[str, Dict[str, Any]]:
    """获取所有模型配置"""
    from model_configs import get_all_models as external_get_all_models
    return external_get_all_models()

def get_models_by_provider(provider: str) -> Dict[str, Dict[str, Any]]:
    """根据提供商获取模型"""
    from model_configs import get_models_by_provider as external_get_models_by_provider
    return external_get_models_by_provider(provider)

def get_api_config() -> Dict[str, Any]:
    """获取API配置"""
    from api_configs import get_api_config as external_get_api_config
    return external_get_api_config()

def get_task_config() -> Dict[str, Any]:
    """获取任务分析配置"""
    from api_configs import get_task_config as external_get_task_config
    return external_get_task_config()

def get_p2l_config() -> Dict[str, Any]:
    """获取P2L引擎配置"""
    return P2L_CONFIG

def get_service_config() -> Dict[str, Any]:
    """获取服务配置"""
    from api_configs import get_service_config as external_get_service_config
    return external_get_service_config()

# 初始化环境配置
load_env_config()

print(f"✅ Backend配置加载完成，共 {len(MODEL_CONFIGS)} 个模型")
print(f"🔑 API配置加载完成，共 {len([k for k, v in API_CONFIGS['api_keys'].items() if v])} 个API密钥")