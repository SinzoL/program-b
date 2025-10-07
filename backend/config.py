#!/usr/bin/env python3
"""
Backend配置文件 - 统一版本
所有配置从 model_p2l 目录导入，保持简洁
"""

import os
import sys
import logging
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

# ================== 环境配置管理 ==================
def get_environment():
    """检测当前运行环境"""
    return os.getenv("P2L_ENV", "development").lower()

def get_production_service_config() -> Dict[str, Any]:
    """生产环境配置 - Docker部署优化"""
    return {
        "server": {
            "host": os.getenv("P2L_HOST", "0.0.0.0"),
            "port": int(os.getenv("P2L_PORT", 8080)),
            "log_level": "info",
            "reload": False,  # 生产环境不启用热重载
            "workers": 1,     # 单worker避免资源竞争
        },
        "cors": {
            "allow_origins": ["*"],  # 生产环境可以配置具体域名
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"],
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "/app/logs/backend.log",
        },
        "p2l": {
            "model_path": os.getenv("P2L_MODEL_PATH", "/app/backend/model_p2l/models/p2l-135m-grk"),
            "device": os.getenv("P2L_DEVICE", "cpu"),
            "mock_mode": False,  # 生产环境使用真实P2L模型
            "timeout": 60,  # 增加超时时间
            "max_retries": 3,
        },
        "resources": {
            "max_memory_mb": 3000,  # 最大内存使用
            "max_cpu_percent": 80,  # 最大CPU使用率
            "cleanup_interval": 300,  # 5分钟清理一次
        }
    }

def get_development_service_config() -> Dict[str, Any]:
    """开发环境配置"""
    return {
        "server": {
            "host": "127.0.0.1",
            "port": 8080,
            "log_level": "debug",
            "reload": True,  # 开发环境启用热重载
        },
        "cors": {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        },
        "logging": {
            "level": "DEBUG",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "p2l": {
            "model_path": os.path.join(current_dir, "model_p2l", "models", "p2l-135m-grk"),
            "device": "cpu",
            "mock_mode": False,
            "timeout": 30,
            "max_retries": 2,
        }
    }

def setup_logging():
    """根据环境设置日志配置"""
    config = get_service_config()
    log_config = config["logging"]
    
    handlers = [logging.StreamHandler()]
    
    # 生产环境添加文件日志
    if get_environment() == "production" and "file" in log_config:
        log_file = log_config["file"]
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_config["level"]),
        format=log_config["format"],
        handlers=handlers
    )
    
    # 生产环境设置第三方库日志级别
    if get_environment() == "production":
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("transformers").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

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
    """根据环境自动获取服务配置"""
    env = get_environment()
    
    if env == "production":
        config = get_production_service_config()
        print(f"🐳 使用生产环境配置 (P2L_ENV={env})")
        return config
    else:
        # 开发环境优先使用外部配置，如果失败则使用内置配置
        try:
            from api_configs import get_service_config as external_get_service_config
            config = external_get_service_config()
            print(f"🛠️ 使用开发环境外部配置 (P2L_ENV={env})")
            return config
        except ImportError:
            config = get_development_service_config()
            print(f"🛠️ 使用开发环境内置配置 (P2L_ENV={env})")
            return config

# 初始化环境配置
load_env_config()

# 环境信息输出
env = get_environment()
print(f"✅ Backend配置加载完成，共 {len(MODEL_CONFIGS)} 个模型")
print(f"🔑 API配置加载完成，共 {len([k for k, v in API_CONFIGS['api_keys'].items() if v])} 个API密钥")
print(f"🌍 当前环境: {env}")

# 自动设置日志（如果需要）
if os.getenv("AUTO_SETUP_LOGGING", "false").lower() == "true":
    setup_logging()