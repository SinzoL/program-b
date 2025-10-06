#!/usr/bin/env python3
"""
Backend配置文件 - 简化版
导入外置配置文件，保持向后兼容
"""

import os
import sys
from typing import Dict, Any

# 导入项目常量
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p2l_core import DEFAULT_MODEL, MODEL_MAPPING

# 导入外置配置
try:
    from model_configs import MODEL_CONFIGS, get_model_config, get_all_models, get_models_by_provider
    from api_configs import API_CONFIGS, TASK_ANALYSIS_CONFIG, SERVICE_CONFIG, load_env_config, DEFAULT_CONFIG
    print("✅ 成功导入外置配置文件")
except ImportError as e:
    raise RuntimeError(f"❌ 无法导入外置配置文件: {e}。请确保 model_configs.py 和 api_configs.py 文件存在且可访问。")

# 保持向后兼容的别名
API_CONFIG = API_CONFIGS

# ================== 原有的大量模型配置已移至 model_configs.py ==================
# 验证外置配置是否成功加载
if not MODEL_CONFIGS:
    raise RuntimeError("❌ 模型配置加载失败！请确保 model_configs.py 文件存在且可访问。")

# ================== P2L引擎配置 ==================
def _get_model_path():
    """智能获取模型路径，兼容本地和Docker环境"""
    # 检查是否在Docker容器内运行
    if os.path.exists('/app') and os.getcwd().startswith('/app'):
        # Docker容器环境
        model_path = "/app/models"
    else:
        # 本地开发环境
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    
    return model_path

P2L_CONFIG = {
    # 模型路径 - 智能检测环境
    "model_path": _get_model_path(),
    
    # 默认模型 - 从外置配置获取
    "default_model": DEFAULT_CONFIG.get("DEFAULT_MODEL", DEFAULT_MODEL),
    
    # 推理参数 - 从外置配置获取
    "inference_params": {
        "max_length": 512,
        "temperature": DEFAULT_CONFIG.get("TEMPERATURE", 0.7),
        "top_p": 0.9,
        "top_k": 50,
        "repetition_penalty": 1.1,
        "do_sample": True,
        "max_tokens": DEFAULT_CONFIG.get("MAX_TOKENS", 2000)
    },
    
    # 语义分析参数
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

# ================== 工具函数 ==================
# 保持向后兼容的函数
def get_model_config(model_name: str) -> Dict[str, Any]:
    """获取指定模型的配置"""
    try:
        from model_configs import get_model_config as external_get_model_config
        return external_get_model_config(model_name)
    except ImportError as e:
        raise RuntimeError(f"❌ 无法加载模型配置: {e}。请确保 model_configs.py 文件存在且可访问。")

def get_all_models() -> Dict[str, Dict[str, Any]]:
    """获取所有模型配置"""
    try:
        from model_configs import get_all_models as external_get_all_models
        return external_get_all_models()
    except ImportError as e:
        raise RuntimeError(f"❌ 无法加载模型配置: {e}。请确保 model_configs.py 文件存在且可访问。")

def get_models_by_provider(provider: str) -> Dict[str, Dict[str, Any]]:
    """根据提供商获取模型"""
    try:
        from model_configs import get_models_by_provider as external_get_models_by_provider
        return external_get_models_by_provider(provider)
    except ImportError as e:
        raise RuntimeError(f"❌ 无法加载模型配置: {e}。请确保 model_configs.py 文件存在且可访问。")

def get_api_config() -> Dict[str, Any]:
    """获取API配置"""
    try:
        from api_configs import get_api_config as external_get_api_config
        return external_get_api_config()
    except ImportError as e:
        raise RuntimeError(f"❌ 无法加载API配置: {e}。请确保 api_configs.py 文件存在且可访问。")

def get_task_config() -> Dict[str, Any]:
    """获取任务分析配置"""
    try:
        from api_configs import get_task_config as external_get_task_config
        return external_get_task_config()
    except ImportError as e:
        raise RuntimeError(f"❌ 无法加载任务配置: {e}。请确保 api_configs.py 文件存在且可访问。")

def get_p2l_config() -> Dict[str, Any]:
    """获取P2L引擎配置"""
    return P2L_CONFIG

def get_service_config() -> Dict[str, Any]:
    """获取服务配置"""
    try:
        from api_configs import get_service_config as external_get_service_config
        return external_get_service_config()
    except ImportError as e:
        raise RuntimeError(f"❌ 无法加载服务配置: {e}。请确保 api_configs.py 文件存在且可访问。")

# 初始化时加载环境配置
load_env_config()

print(f"✅ Backend配置加载完成，共 {len(MODEL_CONFIGS)} 个模型")
print(f"🔑 API配置加载完成，共 {len([k for k, v in API_CONFIGS['api_keys'].items() if v])} 个API密钥")