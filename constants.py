#!/usr/bin/env python3
"""
项目全局常量定义
包含默认模型配置和其他共享常量
"""

# ================== P2L模型常量 ==================

# 默认P2L模型
DEFAULT_MODEL = "p2l-135m-grk-01112025"

# 模型映射关系
MODEL_MAPPING = {
    "p2l-135m-grk-01112025": {
        "repo_id": "lmarena-ai/p2l-135m-grk-01112025",
        "local_name": "p2l-135m-grk",
        "description": "轻量级模型，适合资源受限环境",
        "memory_required": 512,
        "parameters": "135M"
    },
    "p2l-360m-grk-01112025": {
        "repo_id": "lmarena-ai/p2l-360m-grk-01112025", 
        "local_name": "p2l-360m-grk",
        "description": "中等规模模型，平衡性能和资源",
        "memory_required": 1024,
        "parameters": "360M"
    },
    "p2l-0.5b-grk-01112025": {
        "repo_id": "lmarena-ai/p2l-0.5b-grk-01112025",
        "local_name": "p2l-0.5b-grk",
        "description": "标准模型，平衡性能和资源消耗",
        "memory_required": 2048,
        "parameters": "0.5B"
    },
    "p2l-1.5b-grk-01112025": {
        "repo_id": "lmarena-ai/p2l-1.5b-grk-01112025",
        "local_name": "p2l-1.5b-grk", 
        "description": "高性能模型，需要更多资源",
        "memory_required": 4096,
        "parameters": "1.5B"
    },
    "p2l-3b-grk-01112025": {
        "repo_id": "lmarena-ai/p2l-3b-grk-01112025",
        "local_name": "p2l-3b-grk",
        "description": "大型模型，最佳性能",
        "memory_required": 8192,
        "parameters": "3B"
    },
    "p2l-7b-grk-01112025": {
        "repo_id": "lmarena-ai/p2l-7b-grk-01112025",
        "local_name": "p2l-7b-grk",
        "description": "超大型模型，顶级性能",
        "memory_required": 16384,
        "parameters": "7B"
    }
}

# ================== 其他常量 ==================

# 服务配置
DEFAULT_PORT = 8080
DEFAULT_HOST = "0.0.0.0"

# 路径常量
MODELS_DIR_NAME = "models"
BACKEND_DIR_NAME = "backend"
P2L_DIR_NAME = "p2l"