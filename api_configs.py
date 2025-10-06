#!/usr/bin/env python3
"""
API配置文件 - 项目外层配置
包含所有API密钥和端点配置，供backend模块使用
基于API测试结果更新 (2025-01-06)
"""

import os

# ================== API配置 ==================
API_CONFIGS = {
    "api_keys": {
        "openai": "sk-u3kUo5WN8Ezb3U3pEx1GWTeazL7xNzghFErxNO4pkJHa4QPl",     # 使用yinli密钥
        "anthropic": "sk-u3kUo5WN8Ezb3U3pEx1GWTeazL7xNzghFErxNO4pkJHa4QPl",  # 使用yinli密钥
        "google": "sk-u3kUo5WN8Ezb3U3pEx1GWTeazL7xNzghFErxNO4pkJHa4QPl",     # 使用yinli密钥
        "deepseek": "sk-LVXnQECvuyLW9kCpDLkGmw5nAi7zzJ6QcgofVi42Vy0CqVo9",   # 使用probex密钥
        "meta": "sk-LVXnQECvuyLW9kCpDLkGmw5nAi7zzJ6QcgofVi42Vy0CqVo9",      # 使用probex密钥
        "dashscope": "sk-66c6ad44142f40f9999546608f7e70e6", # 使用alibaba密钥
    },
    
    # API端点配置 - 基于测试结果的中转服务配置
    "base_urls": {
        "openai": "https://yinli.one/v1",       # OpenAI模型使用yinli
        "anthropic": "https://yinli.one/v1",    # Anthropic模型使用yinli  
        "google": "https://yinli.one/v1",       # Google模型使用yinli
        "deepseek": "https://api.probex.top/v1", # DeepSeek模型使用probex
        "meta": "https://api.probex.top/v1",    # Meta模型使用probex
        "dashscope": "https://dashscope.aliyuncs.com/compatible-mode/v1",    # Qwen模型使用alibaba
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
    # 服务器配置
    "server": {
        "host": "0.0.0.0",
        "port": 8080,
        "log_level": "info",
        "reload": False
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
    "DEFAULT_MODEL": "gpt-4o-mini",
    "MAX_TOKENS": 2000,
    "TEMPERATURE": 0.7
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
    
    print(f"\n📋 中转服务配置:")
    print(f"  - yinli.one: OpenAI, Anthropic, Google")
    print(f"  - probex.top: DeepSeek, Qwen, Meta")