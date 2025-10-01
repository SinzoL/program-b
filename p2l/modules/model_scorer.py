#!/usr/bin/env python3
"""
模型评分排序模块
负责模型评分和智能排序
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ModelScorer:
    """模型评分器"""
    
    def __init__(self, model_configs: Dict):
        self.model_configs = model_configs
    
    def calculate_model_scores(self, task_analysis: Dict, priority: str, enabled_models: Optional[List[str]] = None) -> List[Dict]:
        """计算模型分数并排序 - 使用百分制评分"""
        scores = []
        
        # 如果指定了启用的模型列表，只计算这些模型的分数
        models_to_score = self.model_configs.items()
        if enabled_models:
            models_to_score = [(name, config) for name, config in self.model_configs.items() if name in enabled_models]
            logger.info(f"只计算启用模型的分数: {[name for name, _ in models_to_score]}")
        
        for model_name, config in models_to_score:
            # 基础分数 (40分)
            base_score = config["quality_score"] * 40
            
            # 任务匹配度 (25分)
            task_score = self._calculate_task_score(task_analysis, config)
            
            # 语言匹配度 (15分)
            language_score = self._calculate_language_score(task_analysis, config)
            
            # 优先级匹配度 (20分)
            priority_score = self._calculate_priority_score(priority, config)
            
            # 总分 = 基础分 + 任务分 + 语言分 + 优先级分 (满分100)
            final_score = base_score + task_score + language_score + priority_score
            
            # 确保分数在0-100之间
            final_score = max(0, min(100, final_score))
            
            scores.append({
                "model": model_name,
                "score": round(final_score, 1),
                "config": config
            })
        
        # 按分数排序
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores
    
    def _calculate_task_score(self, task_analysis: Dict, config: Dict) -> float:
        """计算任务匹配度分数"""
        task_score = 0
        if task_analysis["task_type"] in config["strengths"]:
            task_score = 25
        elif any(strength in task_analysis["task_type"] for strength in config["strengths"]):
            task_score = 15
        else:
            task_score = 5
        return task_score
    
    def _calculate_language_score(self, task_analysis: Dict, config: Dict) -> float:
        """计算语言匹配度分数"""
        language_score = 0
        if task_analysis["language"] == "中文" and "中文理解" in config["strengths"]:
            language_score = 15
        elif task_analysis["language"] == "中文":
            language_score = 8
        else:
            language_score = 10
        return language_score
    
    def _calculate_priority_score(self, priority: str, config: Dict) -> float:
        """计算优先级匹配度分数"""
        priority_score = 0
        if priority == "cost":
            if config["cost_per_1k"] < 0.005:
                priority_score = 20
            elif config["cost_per_1k"] < 0.015:
                priority_score = 15
            else:
                priority_score = 8
        elif priority == "speed":
            if config["avg_response_time"] < 1.5:
                priority_score = 20
            elif config["avg_response_time"] < 2.5:
                priority_score = 15
            else:
                priority_score = 8
        elif priority == "performance":
            if config["quality_score"] > 0.90:
                priority_score = 20
            elif config["quality_score"] > 0.85:
                priority_score = 15
            else:
                priority_score = 10
        else:  # balanced
            priority_score = 15
        return priority_score
    
    def generate_recommendation_reasoning(self, best_model: Dict, task_analysis: Dict, priority: str) -> str:
        """生成推荐理由"""
        reasoning_parts = []
        
        if task_analysis["task_type"] in best_model["config"]["strengths"]:
            reasoning_parts.append(f"擅长{task_analysis['task_type']}任务")
        
        if task_analysis["language"] == "中文" and "中文理解" in best_model["config"]["strengths"]:
            reasoning_parts.append("中文理解能力强")
        
        if priority == "cost" and best_model["config"]["cost_per_1k"] < 0.01:
            reasoning_parts.append("成本效益高")
        elif priority == "speed" and best_model["config"]["avg_response_time"] < 2.0:
            reasoning_parts.append("响应速度快")
        elif priority == "performance" and best_model["config"]["quality_score"] > 0.90:
            reasoning_parts.append("性能表现优秀")
        
        return "；".join(reasoning_parts) if reasoning_parts else "综合性能最佳"