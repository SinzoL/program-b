#!/usr/bin/env python3
"""
API配置文件 - 项目外层配置
包含所有API密钥和端点配置，供backend模块使用
基于API测试结果更新 (2025-01-06)

重构说明：
- API密钥已移至 api_key.env 文件中
- 支持从环境变量读取配置
- 提供默认值以保证系统稳定性
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量文件
env_path = Path(__file__).parent / "api_key.env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ 已加载环境配置: {env_path}")
else:
    print(f"⚠️ 环境配置文件不存在: {env_path}")
    print("📋 请复制 api_key.env.example 为 api_key.env 并配置你的API密钥")

# ================== API配置 ==================
API_CONFIGS = {
    # API密钥配置 - 从环境变量读取
    "api_keys": {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "google": os.getenv("GOOGLE_API_KEY"),
        "deepseek": os.getenv("DEEPSEEK_API_KEY"),
        "meta": os.getenv("META_API_KEY"),
        "dashscope": os.getenv("DASHSCOPE_API_KEY"),
    },
    
    # API端点配置 - 从环境变量读取，提供默认值
    "base_urls": {
        "openai": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "anthropic": os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
        "google": os.getenv("GOOGLE_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"),
        "deepseek": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        "meta": os.getenv("META_BASE_URL", "https://api.meta.com/v1"),
        "dashscope": os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
    },
    
    # 请求超时配置
    "timeouts": {
        "connect": 30,
        "total": 180,  # 增加到180秒，适应复杂编程问题
        "read": 150    # 增加读取超时
    },
    
    # 连接池配置
    "connection_pool": {
        "limit": 100,
        "limit_per_host": 30,
        "ttl_dns_cache": 300
    }
}

# ================== 任务分析配置 ==================
TASK_ANALYSIS_CONFIG = {
    # 任务类型权重
    "task_weights": {
        "coding": {
            "quality_weight": 0.4,
            "speed_weight": 0.3,
            "cost_weight": 0.3
        },
        "creative": {
            "quality_weight": 0.6,
            "speed_weight": 0.2,
            "cost_weight": 0.2
        },
        "analysis": {
            "quality_weight": 0.5,
            "speed_weight": 0.3,
            "cost_weight": 0.2
        },
        "conversation": {
            "quality_weight": 0.3,
            "speed_weight": 0.4,
            "cost_weight": 0.3
        },
        "translation": {
            "quality_weight": 0.4,
            "speed_weight": 0.4,
            "cost_weight": 0.2
        }
    },
    
    # 复杂度阈值
    "complexity_thresholds": {
        "simple": 0.3,
        "medium": 0.6,
        "complex": 0.8
    },
    
    # 语言检测关键词
    "language_keywords": {
        "chinese": ["中文", "汉语", "普通话", "简体", "繁体", "中国", "翻译成中文"],
        "english": ["english", "translate to english", "in english"],
        "code": ["代码", "编程", "函数", "class", "def", "import", "return", "if", "for", "while"]
    }
}

# ================== 服务配置 ==================
SERVICE_CONFIG = {
    # 服务器配置 - 从环境变量读取，提供默认值
    "server": {
        "host": os.getenv("P2L_HOST", "0.0.0.0"),
        "port": int(os.getenv("P2L_PORT", "8080")),
        "log_level": os.getenv("P2L_LOG_LEVEL", "info"),
        "reload": os.getenv("P2L_RELOAD", "false").lower() == "true"
    },
    
    # CORS配置
    "cors": {
        "allow_origins": ["*"],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"]
    },
    
    # 日志配置
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}

# ================== 默认配置 ==================
DEFAULT_CONFIG = {
    "DEFAULT_MODEL": os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
    "MAX_TOKENS": int(os.getenv("MAX_TOKENS", "2000")),
    "TEMPERATURE": float(os.getenv("TEMPERATURE", "0.7"))
}

# ================== 工具函数 ==================
def load_env_config(env_file_path: str = None) -> None:
    """从环境配置文件加载配置 (保持兼容性，但主要配置已直接写入)"""
    # 设置环境变量以保持兼容性
    for provider, key in API_CONFIGS["api_keys"].items():
        if key:
            os.environ[f"{provider.upper()}_API_KEY"] = key
    
    for provider, url in API_CONFIGS["base_urls"].items():
        if url:
            os.environ[f"{provider.upper()}_BASE_URL"] = url
    
    # 设置默认配置
    for key, value in DEFAULT_CONFIG.items():
        os.environ[key] = str(value)

def get_default_config():
    """获取默认配置"""
    return DEFAULT_CONFIG

def get_api_config():
    """获取API配置"""
    return API_CONFIGS

def get_task_config():
    """获取任务分析配置"""
    return TASK_ANALYSIS_CONFIG

def get_service_config():
    """获取服务配置"""
    return SERVICE_CONFIG

# 初始化时加载环境配置
load_env_config()

if __name__ == "__main__":
    print("✅ API配置加载完成")
    print(f"📋 配置的API提供商:")
    for provider, key in API_CONFIGS["api_keys"].items():
        status = "✅ 已配置" if key else "❌ 未配置"
        print(f"  - {provider}: {status}")
    
    print(f"\n📋 默认配置:")
    for key, value in DEFAULT_CONFIG.items():
        print(f"  - {key}: {value}")