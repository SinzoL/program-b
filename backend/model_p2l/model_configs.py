#!/usr/bin/env python3
"""
统一模型配置文件 - 项目外层配置
包含所有模型的详细配置信息，供backend和p2l模块共同使用
基于API测试结果更新 (2025-01-06)
"""

# ================== 模型配置 ==================
MODEL_CONFIGS = {
    # ================== OpenAI 模型 ==================
    "gpt-4o-2024-08-06": {
        "provider": "openai",
        "request_name": "gpt-4o-2024-08-06",
        "cost_per_1k": 0.0015,
        "max_tokens": 16384,
        "context_window": 128000,
        "avg_response_time": 1.2
    },
    "gpt-3.5-turbo-0125": {
        "provider": "openai",
        "request_name": "gpt-3.5-turbo-0125",
        "cost_per_1k": 0.001,
        "max_tokens": 4096,
        "context_window": 16385,
        "avg_response_time": 1.2,
        "verified": True
    },
    "gpt-4o-mini-2024-07-18": {
        "provider": "openai",
        "request_name": "gpt-4o-mini-2024-07-18",
        "cost_per_1k": 0.0015,
        "max_tokens": 16384,
        "context_window": 128000,
        "avg_response_time": 1.0,
        "verified": True
    },
    "gpt-4-turbo-2024-04-09": {
        "provider": "openai",
        "request_name": "gpt-4-turbo-2024-04-09",
        "cost_per_1k": 0.02,
        "max_tokens": 4096,
        "context_window": 128000,
        "avg_response_time": 2.5,
        "verified": True
    },
    
    # ================== Anthropic 模型 ==================
    "claude-3-5-sonnet-20241022": {
        "provider": "anthropic",
        "request_name": "claude-3-5-sonnet-20241022",
        "cost_per_1k": 0.025,
        "max_tokens": 4096,
        "context_window": 200000,
        "avg_response_time": 2.8,
        "verified": True
    },
    "claude-3-5-haiku-20241022": {
        "provider": "anthropic",
        "request_name": "claude-3-5-haiku-20241022",
        "cost_per_1k": 0.008,
        "max_tokens": 4096,
        "context_window": 200000,
        "avg_response_time": 1.5,
        "verified": True
    },
    "claude-3-5-sonnet-20240620": {
        "provider": "anthropic",
        "request_name": "claude-3-5-sonnet-20240620",
        "cost_per_1k": 0.025,
        "max_tokens": 4096,
        "context_window": 200000,
        "avg_response_time": 2.8
    },

    
    # ================== Google 模型 ==================
    "gemini-1.5-flash-001": {
        "provider": "google",
        "request_name": "gemini-1.5-flash-latest",
        "cost_per_1k": 0.015,
        "max_tokens": 8192,
        "context_window": 1000000,
        "avg_response_time": 5.3,
        "verified": True
    },
    "gemini-1.5-pro-001": {
        "provider": "google",
        "request_name": "gemini-1.5-pro",
        "cost_per_1k": 0.025,
        "max_tokens": 8192,
        "context_window": 1000000,
        "avg_response_time": 5.5,
        "verified": True
    },
    "gemini-1.5-pro-002": {
        "provider": "google",
        "request_name": "gemini-1.5-pro-latest",
        "cost_per_1k": 0.025,
        "max_tokens": 8192,
        "context_window": 1000000,
        "avg_response_time": 5.3,
        "verified": True
    },
    
    # ================== DeepSeek 模型 ==================
    "deepseek-v2.5": {
        "provider": "deepseek",
        "request_name": "deepseek-chat",
        "cost_per_1k": 0.002,
        "max_tokens": 4096,
        "context_window": 32000,
        "avg_response_time": 1.8
    },
    "deepseek-v3": {
        "provider": "deepseek",
        "request_name": "deepseek-v3",
        "cost_per_1k": 0.002,
        "max_tokens": 4096,
        "context_window": 32000,
        "avg_response_time": 1.8,
        "verified": True
    },
    
    # ================== DashScope (阿里云) 模型 ==================
    "qwen-max-0428": {
        "provider": "dashscope",
        "request_name": "qwen-max-0428",
        "cost_per_1k": 0.02,
        "max_tokens": 8192,
        "context_window": 200000,
        "avg_response_time": 2.5
    },
    "qwen-max-0919": {
        "provider": "dashscope",
        "request_name": "qwen-max-0919",
        "cost_per_1k": 0.02,
        "max_tokens": 8192,
        "context_window": 200000,
        "avg_response_time": 2.3
    },
    "qwen1.5-110b-chat": {
        "provider": "dashscope",
        "request_name": "qwen1.5-110b-chat",
        "cost_per_1k": 0.008,
        "max_tokens": 8192,
        "context_window": 32000,
        "avg_response_time": 3.2
    },
    "qwen1.5-14b-chat": {
        "provider": "dashscope",
        "request_name": "qwen1.5-14b-chat",
        "cost_per_1k": 0.001,
        "max_tokens": 8192,
        "context_window": 32000,
        "avg_response_time": 1.5
    },
    "qwen1.5-32b-chat": {
        "provider": "dashscope",
        "request_name": "qwen1.5-32b-chat",
        "cost_per_1k": 0.002,
        "max_tokens": 8192,
        "context_window": 32000,
        "avg_response_time": 2.0
    },
    "qwen1.5-72b-chat": {
        "provider": "dashscope",
        "request_name": "qwen1.5-72b-chat",
        "cost_per_1k": 0.004,
        "max_tokens": 8192,
        "context_window": 32000,
        "avg_response_time": 2.3
    },
    "qwen2-72b-instruct": {
        "provider": "dashscope",
        "request_name": "qwen2-72b-instruct",
        "cost_per_1k": 0.003,
        "max_tokens": 8192,
        "context_window": 32000,
        "avg_response_time": 2.2
    },
    "qwen2.5-72b-instruct": {
        "provider": "dashscope",
        "request_name": "qwen2.5-72b-instruct",
        "cost_per_1k": 0.002,
        "max_tokens": 8192,
        "context_window": 32000,
        "avg_response_time": 2.0
    },
    "qwen2.5-coder-32b-instruct": {
        "provider": "dashscope",
        "request_name": "qwen2.5-coder-32b-instruct",
        "cost_per_1k": 0.002,
        "max_tokens": 8192,
        "context_window": 32000,
        "avg_response_time": 1.8
    }
}

# ================== 工具函数 ==================
def get_model_config(model_name: str):
    """获取指定模型的配置"""
    return MODEL_CONFIGS.get(model_name, {})

def get_all_models():
    """获取所有模型配置"""
    return MODEL_CONFIGS

def get_models_by_provider(provider: str):
    """根据提供商获取模型"""
    return {
        name: config for name, config in MODEL_CONFIGS.items()
        if config.get("provider") == provider
    }

def get_verified_models():
    """获取已验证可用的模型"""
    return {
        name: config for name, config in MODEL_CONFIGS.items()
        if config.get("verified", False)
    }

def get_model_count():
    """获取模型总数"""
    return len(MODEL_CONFIGS)

def get_model_names():
    """获取所有模型名称列表"""
    return list(MODEL_CONFIGS.keys())

def get_request_name(model_name: str):
    """获取模型的API请求名称"""
    config = MODEL_CONFIGS.get(model_name, {})
    return config.get("request_name", model_name)  # 如果没有配置request_name，则使用模型名本身

def get_model_with_request_info(model_name: str):
    """获取模型配置和请求信息"""
    config = get_model_config(model_name)
    if config:
        return {
            "display_name": model_name,  # 展示用的模型名
            "request_name": get_request_name(model_name),  # API请求用的模型名
            "provider": config.get("provider", "unknown"),
            "config": config
        }
    return None

def get_model_provider_info(model_name: str):
    """获取模型的提供商信息"""
    config = MODEL_CONFIGS.get(model_name, {})
    provider = config.get("provider", "unknown")
    return {
        "provider": provider,
        "request_name": config.get("request_name", model_name),
        "display_name": model_name
    }

def update_model_providers():
    """更新所有模型的提供商信息（占位函数）"""
    pass

if __name__ == "__main__":
    print(f"✅ 模型配置加载完成，共 {get_model_count()} 个模型")
    
    # 统计已验证的模型
    verified_models = get_verified_models()
    print(f"🔍 已验证可用模型: {len(verified_models)} 个")
    
    print(f"\n📋 提供商分布:")
    providers = {}
    
    for config in MODEL_CONFIGS.values():
        provider = config.get("provider", "unknown")
        providers[provider] = providers.get(provider, 0) + 1
    
    for provider, count in providers.items():
        print(f"  - {provider}: {count} 个模型")
    
    print(f"\n🧪 测试request_name功能:")
    test_models = ['deepseek-v2.5', 'qwen-max-0428', 'gpt-3.5-turbo-0125']
    for model in test_models:
        info = get_model_with_request_info(model)
        if info:
            print(f"  {model}:")
            print(f"    展示名: {info['display_name']}")
            print(f"    请求名: {info['request_name']}")
            print(f"    提供商: {info['provider']}")
        else:
            print(f"  {model}: 未找到配置")
    
    print(f"\n✅ DashScope模型:")
    dashscope_models = get_models_by_provider("dashscope")
    for name, config in dashscope_models.items():
        request_name = config.get("request_name", name)
        print(f"  - {name} -> {request_name}")