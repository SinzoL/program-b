#!/usr/bin/env python3
"""
统一配置文件
包含所有模型配置、API设置、性能参数等
"""

import os
from typing import Dict, Any

# ================== API配置 ==================
API_CONFIG = {
    # API密钥配置 (从环境变量或配置文件加载)
    "api_keys": {
        "openai": os.getenv('OPENAI_API_KEY', ''),
        "anthropic": os.getenv('ANTHROPIC_API_KEY', ''),
        "google": os.getenv('GOOGLE_API_KEY', ''),
        "dashscope": os.getenv('DASHSCOPE_API_KEY', ''),
        "deepseek": os.getenv('DEEPSEEK_API_KEY', ''),
    },
    
    # API端点配置
    "base_urls": {
        "openai": os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
        "anthropic": os.getenv('ANTHROPIC_BASE_URL', 'https://api.anthropic.com/v1'),
        "google": os.getenv('GOOGLE_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta'),
        "dashscope": os.getenv('DASHSCOPE_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
        "deepseek": os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1'),
    },
    
    # 请求超时配置
    "timeouts": {
        "connect": 30,
        "total": 60,
        "read": 45
    },
    
    # 连接池配置
    "connection_pool": {
        "limit": 100,
        "limit_per_host": 30,
        "ttl_dns_cache": 300
    }
}

# ================== 模型配置 ==================
MODEL_CONFIGS = {
    # OpenAI 模型
    "gpt-4o": {
        "provider": "openai",
        "cost_per_1k": 0.03,
        "max_tokens": 4096,
        "context_window": 128000,
        "avg_response_time": 2.5,
        "strengths": ["编程", "复杂推理", "数学", "多语言"],
        "quality_score": 0.95,
        "speed_score": 0.75,
        "cost_score": 0.60
    },
    "gpt-4o-mini": {
        "provider": "openai", 
        "cost_per_1k": 0.0015,
        "max_tokens": 16384,
        "context_window": 128000,
        "avg_response_time": 1.2,
        "strengths": ["快速响应", "成本效益", "日常对话"],
        "quality_score": 0.82,
        "speed_score": 0.90,
        "cost_score": 0.95
    },
    
    # Claude 模型
    "claude-3-5-sonnet-20241022": {
        "provider": "anthropic",
        "cost_per_1k": 0.025,
        "max_tokens": 4096,
        "context_window": 200000,
        "avg_response_time": 2.8,
        "strengths": ["创意写作", "文学分析", "代码审查"],
        "quality_score": 0.93,
        "speed_score": 0.70,
        "cost_score": 0.65
    },
    "claude-3-7-sonnet-20250219": {
        "provider": "anthropic",
        "cost_per_1k": 0.025,
        "max_tokens": 4096,
        "context_window": 200000,
        "avg_response_time": 2.5,
        "strengths": ["创意写作", "分析", "编程", "推理"],
        "quality_score": 0.95,
        "speed_score": 0.75,
        "cost_score": 0.65
    },
    
    # Gemini 模型
    "gemini-1.5-pro": {
        "provider": "google",
        "cost_per_1k": 0.015,
        "max_tokens": 8192,
        "context_window": 1000000,
        "avg_response_time": 2.0,
        "strengths": ["多模态", "长文本", "推理", "数据分析"],
        "quality_score": 0.89,
        "speed_score": 0.80,
        "cost_score": 0.75
    },
    
    # DeepSeek 模型
    "deepseek-chat": {
        "provider": "deepseek",
        "cost_per_1k": 0.002,
        "max_tokens": 4096,
        "context_window": 32000,
        "avg_response_time": 1.8,
        "strengths": ["对话", "中文理解", "快速响应"],
        "quality_score": 0.86,
        "speed_score": 0.85,
        "cost_score": 0.98
    },
    "deepseek-coder": {
        "provider": "deepseek",
        "cost_per_1k": 0.002,
        "max_tokens": 4096,
        "context_window": 16000,
        "avg_response_time": 1.6,
        "strengths": ["编程", "代码生成", "技术问答"],
        "quality_score": 0.88,
        "speed_score": 0.88,
        "cost_score": 0.98
    },
    
    # 千问模型
    "qwen2.5-72b-instruct": {
        "provider": "qwen",
        "cost_per_1k": 0.002,
        "max_tokens": 8192,
        "context_window": 32000,
        "avg_response_time": 2.0,
        "strengths": ["中文理解", "推理", "编程", "数学"],
        "quality_score": 0.90,
        "speed_score": 0.80,
        "cost_score": 0.98
    },
    "qwen-plus": {
        "provider": "qwen", 
        "cost_per_1k": 0.004,
        "max_tokens": 6144,
        "context_window": 32000,
        "avg_response_time": 2.5,
        "strengths": ["复杂推理", "长文本", "多轮对话"],
        "quality_score": 0.92,
        "speed_score": 0.75,
        "cost_score": 0.90
    },
    "qwen-turbo": {
        "provider": "qwen",
        "cost_per_1k": 0.001,
        "max_tokens": 1500,
        "context_window": 8000,
        "avg_response_time": 1.0,
        "strengths": ["快速响应", "成本效益", "日常对话"],
        "quality_score": 0.85,
        "speed_score": 0.95,
        "cost_score": 0.99
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

# ================== P2L引擎配置 ==================
P2L_CONFIG = {
    # 模型路径
    "model_path": "models/p2l-0.5b-grk",
    
    # 推理参数
    "inference_params": {
        "max_length": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 50,
        "repetition_penalty": 1.1,
        "do_sample": True
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

# ================== 工具函数 ==================
def load_env_config(env_file_path: str = None) -> None:
    """从环境配置文件加载配置"""
    if env_file_path is None:
        env_file_path = os.path.join(os.path.dirname(__file__), '..', 'api_config.env')
    
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if value:  # 只设置非空值
                        os.environ[key] = value
                        # 更新API配置
                        if key.endswith('_API_KEY'):
                            provider = key.lower().replace('_api_key', '')
                            API_CONFIG["api_keys"][provider] = value
                        elif key.endswith('_BASE_URL'):
                            provider = key.lower().replace('_base_url', '')
                            API_CONFIG["base_urls"][provider] = value

def get_model_config(model_name: str) -> Dict[str, Any]:
    """获取指定模型的配置"""
    return MODEL_CONFIGS.get(model_name, {})

def get_all_models() -> Dict[str, Dict[str, Any]]:
    """获取所有模型配置"""
    return MODEL_CONFIGS

def get_models_by_provider(provider: str) -> Dict[str, Dict[str, Any]]:
    """根据提供商获取模型"""
    return {
        name: config for name, config in MODEL_CONFIGS.items()
        if config.get("provider") == provider
    }

def get_api_config() -> Dict[str, Any]:
    """获取API配置"""
    return API_CONFIG

def get_task_config() -> Dict[str, Any]:
    """获取任务分析配置"""
    return TASK_ANALYSIS_CONFIG

def get_p2l_config() -> Dict[str, Any]:
    """获取P2L引擎配置"""
    return P2L_CONFIG

def get_service_config() -> Dict[str, Any]:
    """获取服务配置"""
    return SERVICE_CONFIG

# 初始化时加载环境配置
load_env_config()