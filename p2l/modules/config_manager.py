#!/usr/bin/env python3
"""
配置管理模块
负责加载和管理模型配置信息
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.model_configs = self._load_model_configs()
    
    def _load_model_configs(self) -> Dict:
        """加载模型配置信息 - 只包含有API密钥的主流模型"""
        return {
            # OpenAI 主流模型
            "gpt-4o": {
                "provider": "openai",
                "cost_per_1k": 0.03,
                "avg_response_time": 2.5,
                "strengths": ["编程", "复杂推理", "数学"],
                "quality_score": 0.95
            },
            "gpt-4o-mini": {
                "provider": "openai", 
                "cost_per_1k": 0.0015,
                "avg_response_time": 1.2,
                "strengths": ["快速响应", "成本效益"],
                "quality_score": 0.82
            },
            # Claude 主流模型
            "claude-3-5-sonnet-20241022": {
                "provider": "anthropic",
                "cost_per_1k": 0.025,
                "avg_response_time": 2.8,
                "strengths": ["创意写作", "文学分析"],
                "quality_score": 0.93
            },
            "claude-3-7-sonnet-20250219": {
                "provider": "anthropic",
                "cost_per_1k": 0.025,
                "avg_response_time": 2.5,
                "strengths": ["创意写作", "分析", "编程", "推理"],
                "quality_score": 0.95
            },
            # Gemini 主流模型
            "gemini-1.5-pro": {
                "provider": "google",
                "cost_per_1k": 0.015,
                "avg_response_time": 2.0,
                "strengths": ["多模态", "长文本", "推理"],
                "quality_score": 0.89
            },
            # DeepSeek 主流模型
            "deepseek-chat": {
                "provider": "deepseek",
                "cost_per_1k": 0.002,
                "avg_response_time": 1.8,
                "strengths": ["对话", "中文理解", "快速响应"],
                "quality_score": 0.86
            },
            "deepseek-coder": {
                "provider": "deepseek",
                "cost_per_1k": 0.002,
                "avg_response_time": 1.6,
                "strengths": ["编程", "代码生成", "技术问答"],
                "quality_score": 0.88
            },
            # 千问主流模型
            "qwen2.5-72b-instruct": {
                "provider": "qwen",
                "cost_per_1k": 0.002,  # 约$0.002 (¥0.015转换)
                "avg_response_time": 2.0,
                "strengths": ["中文理解", "推理", "编程", "数学"],
                "quality_score": 0.90
            },
            "qwen-plus": {
                "provider": "qwen", 
                "cost_per_1k": 0.004,
                "avg_response_time": 2.5,
                "strengths": ["复杂推理", "长文本", "多轮对话"],
                "quality_score": 0.92
            },
            "qwen-turbo": {
                "provider": "qwen",
                "cost_per_1k": 0.001,
                "avg_response_time": 1.0,
                "strengths": ["快速响应", "成本效益", "日常对话"],
                "quality_score": 0.85
            }
        }
    
    def get_model_config(self, model_name: str) -> Dict:
        """获取指定模型的配置"""
        return self.model_configs.get(model_name, {})
    
    def get_all_models(self) -> Dict:
        """获取所有模型配置"""
        return self.model_configs
    
    def get_models_by_provider(self, provider: str) -> Dict:
        """根据提供商获取模型"""
        return {
            name: config for name, config in self.model_configs.items()
            if config.get("provider") == provider
        }