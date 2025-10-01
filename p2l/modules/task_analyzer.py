#!/usr/bin/env python3
"""
任务分析模块
负责任务识别、分类和特征提取
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)

class TaskAnalyzer:
    """任务分析器"""
    
    def __init__(self):
        pass
    
    def analyze_task(self, prompt: str, complexity_score: float = None, language_score: float = None) -> Dict:
        """综合任务分析"""
        if complexity_score is not None and language_score is not None:
            # 使用语义增强分析
            return self._enhanced_task_analysis(prompt, complexity_score, language_score)
        else:
            # 使用规则分析
            return self._rule_based_analysis(prompt)
    
    def _enhanced_task_analysis(self, prompt: str, complexity_score: float, language_score: float) -> Dict:
        """增强的任务分析方法，结合规则和语义特征"""
        prompt_lower = prompt.lower()
        
        # 更精确的任务类型识别
        task_type = "通用"
        confidence = 0.5
        
        # 编程相关关键词检测（权重更高）
        programming_keywords = [
            "code", "python", "javascript", "js", "function", "method", "class",
            "程序", "代码", "编程", "函数", "方法", "类", "算法", "实现",
            "下划线", "驼峰", "camelcase", "underscore", "转换", "转化",
            "变量", "命名", "格式", "string", "字符串"
        ]
        programming_score = sum(1 for word in programming_keywords if word in prompt_lower)
        
        # 创意写作关键词
        creative_keywords = ["story", "poem", "creative", "故事", "诗歌", "创意", "写作", "小说", "散文"]
        creative_score = sum(1 for word in creative_keywords if word in prompt_lower)
        
        # 翻译关键词
        translation_keywords = ["translate", "翻译", "中文", "english", "french", "语言", "转译"]
        translation_score = sum(1 for word in translation_keywords if word in prompt_lower)
        
        # 数学关键词
        math_keywords = ["math", "calculate", "数学", "计算", "solve", "equation", "公式", "求解"]
        math_score = sum(1 for word in math_keywords if word in prompt_lower)
        
        # 分析关键词
        analysis_keywords = ["analyze", "explain", "分析", "解释", "describe", "描述", "评价"]
        analysis_score = sum(1 for word in analysis_keywords if word in prompt_lower)
        
        # 确定任务类型和置信度
        scores = {
            "编程": programming_score,
            "创意写作": creative_score,
            "翻译": translation_score,
            "数学": math_score,
            "分析": analysis_score
        }
        
        max_score = max(scores.values())
        if max_score > 0:
            task_type = max(scores, key=scores.get)
            confidence = min(0.9, 0.5 + max_score * 0.1)
        
        # 特殊模式检测：下划线转驼峰
        if any(word in prompt_lower for word in ["下划线", "驼峰", "camelcase", "underscore"]):
            task_type = "编程"
            confidence = 0.95
            logger.info("🎯 检测到字符串格式转换任务，高置信度识别为编程类型")
        
        # 基于语义特征和关键词调整复杂度
        base_complexity = complexity_score
        if task_type == "编程" and max_score >= 2:
            base_complexity = max(base_complexity, 0.6)  # 编程任务通常较复杂
        
        if base_complexity > 0.7:
            complexity = "复杂"
        elif base_complexity < 0.3:
            complexity = "简单"
        else:
            complexity = "中等"
        
        # 语言检测（中文字符比例）
        chinese_chars = sum(1 for char in prompt if '\u4e00' <= char <= '\u9fff')
        total_chars = len(prompt)
        chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0
        
        language = "中文" if chinese_ratio > 0.3 else "英文"
        
        result = {
            "task_type": task_type,
            "complexity": complexity,
            "language": language,
            "length": len(prompt),
            "confidence": confidence,
            "p2l_scores": {
                "complexity": base_complexity,
                "language": language_score,
                "keyword_scores": scores,
                "chinese_ratio": chinese_ratio
            }
        }
        
        logger.info(f"📊 任务分析详情: {result}")
        return result
    
    def _rule_based_analysis(self, prompt: str) -> Dict:
        """备用的规则分析方法"""
        prompt_lower = prompt.lower()
        
        # 任务类型识别
        task_type = "通用"
        if any(word in prompt_lower for word in ["code", "python", "javascript", "程序", "代码", "编程", "function"]):
            task_type = "编程"
        elif any(word in prompt_lower for word in ["story", "poem", "creative", "故事", "诗歌", "创意", "写作"]):
            task_type = "创意写作"
        elif any(word in prompt_lower for word in ["translate", "翻译", "中文", "english", "french"]):
            task_type = "翻译"
        elif any(word in prompt_lower for word in ["math", "calculate", "数学", "计算", "solve", "equation"]):
            task_type = "数学"
        elif any(word in prompt_lower for word in ["analyze", "explain", "分析", "解释", "describe"]):
            task_type = "分析"
        
        # 复杂度评估
        complexity = "简单"
        if len(prompt) > 100 or any(word in prompt_lower for word in ["complex", "advanced", "详细", "完整"]):
            complexity = "复杂"
        elif len(prompt) > 50:
            complexity = "中等"
        
        # 语言检测
        language = "英文"
        chinese_chars = sum(1 for char in prompt if '\u4e00' <= char <= '\u9fff')
        if chinese_chars > len(prompt) * 0.3:
            language = "中文"
        
        return {
            "task_type": task_type,
            "complexity": complexity,
            "language": language,
            "length": len(prompt)
        }