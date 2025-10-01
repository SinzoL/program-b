#!/usr/bin/env python3
"""
P2L训练数据生成器
生成用于训练P2L模型的prompt-model性能配对数据
"""

import json
import random
import numpy as np
from typing import Dict, List, Tuple
import os
from datasets import Dataset
import logging

logger = logging.getLogger(__name__)

class P2LTrainingDataGenerator:
    """P2L训练数据生成器"""
    
    def __init__(self):
        self.task_templates = self._load_task_templates()
        self.model_performance_profiles = self._load_model_profiles()
        
    def _load_task_templates(self) -> Dict:
        """加载任务模板"""
        return {
            "编程": [
                "写一个{language}函数来{function_desc}",
                "实现{algorithm}算法的{language}代码",
                "创建一个{language}类来{class_desc}",
                "编写{language}代码解决{problem_desc}问题",
                "优化这段{language}代码：{code_snippet}",
                "调试这个{language}程序中的错误",
                "设计一个{language}API来{api_desc}",
                "编写单元测试来验证{function_name}函数"
            ],
            "创意写作": [
                "写一篇关于{topic}的{style}",
                "创作一首{theme}的诗歌",
                "编写一个{genre}故事，主题是{theme}",
                "写一段{tone}的{content_type}",
                "创作一个{character}的角色描述",
                "写一篇{length}的{topic}文章",
                "编写一个{setting}背景的场景描述",
                "创作一个{emotion}情感的{format}作品"
            ],
            "翻译": [
                "将这段{source_lang}翻译成{target_lang}：{text}",
                "翻译这个{domain}领域的{source_lang}文档",
                "把这句{source_lang}谚语翻译成{target_lang}",
                "翻译这段{style}{source_lang}文本",
                "将{source_lang}的{content_type}翻译成{target_lang}",
                "翻译这个{technical_field}的专业术语",
                "把这段{source_lang}对话翻译成{target_lang}",
                "翻译这首{source_lang}诗歌，保持韵律"
            ],
            "数学": [
                "解这个{math_type}方程：{equation}",
                "计算{calculation_type}：{expression}",
                "证明这个{theorem_type}定理",
                "求解这个{problem_type}问题",
                "分析这个{function_type}函数的性质",
                "计算{geometry_shape}的{property}",
                "解释{concept}的数学原理",
                "求{optimization_type}的最优解"
            ],
            "分析": [
                "分析{topic}的{aspect}",
                "解释{phenomenon}的原因",
                "评估{subject}的{criteria}",
                "比较{item1}和{item2}的{dimension}",
                "总结{content}的要点",
                "分析{data_type}数据的趋势",
                "解读{chart_type}图表的含义",
                "评价{work}的{evaluation_aspect}"
            ],
            "问答": [
                "什么是{concept}？",
                "如何{action}？",
                "为什么{phenomenon}会发生？",
                "哪种{category}最{criteria}？",
                "什么时候应该{action}？",
                "在哪里可以{find_what}？",
                "谁是{field}领域的{role}？",
                "{topic}有什么{aspect}？"
            ],
            "总结": [
                "总结这篇{content_type}的主要观点",
                "概括{topic}的核心内容",
                "提炼{document}的关键信息",
                "归纳{discussion}的要点",
                "简述{process}的步骤",
                "概要{report}的结论",
                "总结{meeting}的决议",
                "梳理{topic}的发展历程"
            ],
            "通用": [
                "帮我{general_task}",
                "请{polite_request}",
                "我想了解{topic}",
                "能否{capability_request}",
                "关于{subject}，你怎么看？",
                "给我一些{advice_type}建议",
                "推荐一些{recommendation_type}",
                "解释一下{explanation_target}"
            ]
        }
    
    def _load_model_profiles(self) -> Dict:
        """加载模型性能档案"""
        return {
            "gpt-4o": {
                "编程": {"quality": 0.95, "speed": 0.7, "cost": 0.3},
                "创意写作": {"quality": 0.90, "speed": 0.7, "cost": 0.3},
                "翻译": {"quality": 0.88, "speed": 0.7, "cost": 0.3},
                "数学": {"quality": 0.93, "speed": 0.7, "cost": 0.3},
                "分析": {"quality": 0.92, "speed": 0.7, "cost": 0.3},
                "问答": {"quality": 0.89, "speed": 0.7, "cost": 0.3},
                "总结": {"quality": 0.87, "speed": 0.7, "cost": 0.3},
                "通用": {"quality": 0.90, "speed": 0.7, "cost": 0.3}
            },
            "gpt-4o-mini": {
                "编程": {"quality": 0.82, "speed": 0.9, "cost": 0.95},
                "创意写作": {"quality": 0.78, "speed": 0.9, "cost": 0.95},
                "翻译": {"quality": 0.80, "speed": 0.9, "cost": 0.95},
                "数学": {"quality": 0.79, "speed": 0.9, "cost": 0.95},
                "分析": {"quality": 0.81, "speed": 0.9, "cost": 0.95},
                "问答": {"quality": 0.85, "speed": 0.9, "cost": 0.95},
                "总结": {"quality": 0.83, "speed": 0.9, "cost": 0.95},
                "通用": {"quality": 0.82, "speed": 0.9, "cost": 0.95}
            },
            "claude-3-5-sonnet-20241022": {
                "编程": {"quality": 0.88, "speed": 0.6, "cost": 0.4},
                "创意写作": {"quality": 0.95, "speed": 0.6, "cost": 0.4},
                "翻译": {"quality": 0.85, "speed": 0.6, "cost": 0.4},
                "数学": {"quality": 0.86, "speed": 0.6, "cost": 0.4},
                "分析": {"quality": 0.93, "speed": 0.6, "cost": 0.4},
                "问答": {"quality": 0.87, "speed": 0.6, "cost": 0.4},
                "总结": {"quality": 0.90, "speed": 0.6, "cost": 0.4},
                "通用": {"quality": 0.89, "speed": 0.6, "cost": 0.4}
            },
            "claude-3-7-sonnet-20250219": {
                "编程": {"quality": 0.92, "speed": 0.65, "cost": 0.4},
                "创意写作": {"quality": 0.97, "speed": 0.65, "cost": 0.4},
                "翻译": {"quality": 0.88, "speed": 0.65, "cost": 0.4},
                "数学": {"quality": 0.89, "speed": 0.65, "cost": 0.4},
                "分析": {"quality": 0.95, "speed": 0.65, "cost": 0.4},
                "问答": {"quality": 0.90, "speed": 0.65, "cost": 0.4},
                "总结": {"quality": 0.92, "speed": 0.65, "cost": 0.4},
                "通用": {"quality": 0.91, "speed": 0.65, "cost": 0.4}
            },
            "claude-3-5-haiku-20241022": {
                "编程": {"quality": 0.80, "speed": 0.85, "cost": 0.8},
                "创意写作": {"quality": 0.82, "speed": 0.85, "cost": 0.8},
                "翻译": {"quality": 0.78, "speed": 0.85, "cost": 0.8},
                "数学": {"quality": 0.76, "speed": 0.85, "cost": 0.8},
                "分析": {"quality": 0.81, "speed": 0.85, "cost": 0.8},
                "问答": {"quality": 0.84, "speed": 0.85, "cost": 0.8},
                "总结": {"quality": 0.86, "speed": 0.85, "cost": 0.8},
                "通用": {"quality": 0.82, "speed": 0.85, "cost": 0.8}
            },
            "gemini-1.5-pro-002": {
                "编程": {"quality": 0.87, "speed": 0.75, "cost": 0.5},
                "创意写作": {"quality": 0.85, "speed": 0.75, "cost": 0.5},
                "翻译": {"quality": 0.88, "speed": 0.75, "cost": 0.5},
                "数学": {"quality": 0.90, "speed": 0.75, "cost": 0.5},
                "分析": {"quality": 0.89, "speed": 0.75, "cost": 0.5},
                "问答": {"quality": 0.86, "speed": 0.75, "cost": 0.5},
                "总结": {"quality": 0.84, "speed": 0.75, "cost": 0.5},
                "通用": {"quality": 0.87, "speed": 0.75, "cost": 0.5}
            },
            "gemini-1.5-flash-002": {
                "编程": {"quality": 0.75, "speed": 0.95, "cost": 0.9},
                "创意写作": {"quality": 0.73, "speed": 0.95, "cost": 0.9},
                "翻译": {"quality": 0.76, "speed": 0.95, "cost": 0.9},
                "数学": {"quality": 0.78, "speed": 0.95, "cost": 0.9},
                "分析": {"quality": 0.74, "speed": 0.95, "cost": 0.9},
                "问答": {"quality": 0.80, "speed": 0.95, "cost": 0.9},
                "总结": {"quality": 0.82, "speed": 0.95, "cost": 0.9},
                "通用": {"quality": 0.77, "speed": 0.95, "cost": 0.9}
            },
            "qwen2.5-72b-instruct": {
                "编程": {"quality": 0.85, "speed": 0.8, "cost": 0.7},
                "创意写作": {"quality": 0.90, "speed": 0.8, "cost": 0.7},
                "翻译": {"quality": 0.92, "speed": 0.8, "cost": 0.7},
                "数学": {"quality": 0.83, "speed": 0.8, "cost": 0.7},
                "分析": {"quality": 0.87, "speed": 0.8, "cost": 0.7},
                "问答": {"quality": 0.88, "speed": 0.8, "cost": 0.7},
                "总结": {"quality": 0.86, "speed": 0.8, "cost": 0.7},
                "通用": {"quality": 0.87, "speed": 0.8, "cost": 0.7}
            },
            "llama-3.1-70b-instruct": {
                "编程": {"quality": 0.84, "speed": 0.7, "cost": 0.8},
                "创意写作": {"quality": 0.81, "speed": 0.7, "cost": 0.8},
                "翻译": {"quality": 0.79, "speed": 0.7, "cost": 0.8},
                "数学": {"quality": 0.82, "speed": 0.7, "cost": 0.8},
                "分析": {"quality": 0.83, "speed": 0.7, "cost": 0.8},
                "问答": {"quality": 0.85, "speed": 0.7, "cost": 0.8},
                "总结": {"quality": 0.84, "speed": 0.7, "cost": 0.8},
                "通用": {"quality": 0.83, "speed": 0.7, "cost": 0.8}
            },
            "deepseek-v3": {
                "编程": {"quality": 0.89, "speed": 0.85, "cost": 0.75},
                "创意写作": {"quality": 0.78, "speed": 0.85, "cost": 0.75},
                "翻译": {"quality": 0.80, "speed": 0.85, "cost": 0.75},
                "数学": {"quality": 0.91, "speed": 0.85, "cost": 0.75},
                "分析": {"quality": 0.85, "speed": 0.85, "cost": 0.75},
                "问答": {"quality": 0.82, "speed": 0.85, "cost": 0.75},
                "总结": {"quality": 0.81, "speed": 0.85, "cost": 0.75},
                "通用": {"quality": 0.84, "speed": 0.85, "cost": 0.75}
            }
        }
    
    def generate_prompt(self, task_type: str, complexity: str = "中等", language: str = "中文") -> str:
        """生成特定类型的prompt"""
        templates = self.task_templates.get(task_type, self.task_templates["通用"])
        template = random.choice(templates)
        
        # 根据任务类型填充模板
        if task_type == "编程":
            return self._fill_programming_template(template, complexity, language)
        elif task_type == "创意写作":
            return self._fill_creative_template(template, complexity, language)
        elif task_type == "翻译":
            return self._fill_translation_template(template, complexity, language)
        elif task_type == "数学":
            return self._fill_math_template(template, complexity, language)
        elif task_type == "分析":
            return self._fill_analysis_template(template, complexity, language)
        elif task_type == "问答":
            return self._fill_qa_template(template, complexity, language)
        elif task_type == "总结":
            return self._fill_summary_template(template, complexity, language)
        else:
            return self._fill_general_template(template, complexity, language)
    
    def _fill_programming_template(self, template: str, complexity: str, language: str) -> str:
        """填充编程模板"""
        languages = ["Python", "JavaScript", "Java", "C++", "Go"]
        functions = ["排序数组", "查找元素", "计算斐波那契数列", "反转字符串", "合并列表"]
        algorithms = ["快速排序", "二分查找", "动态规划", "深度优先搜索", "广度优先搜索"]
        
        replacements = {
            "language": random.choice(languages),
            "function_desc": random.choice(functions),
            "algorithm": random.choice(algorithms),
            "class_desc": "管理用户数据",
            "problem_desc": "最短路径",
            "code_snippet": "def func(): pass",
            "api_desc": "处理HTTP请求",
            "function_name": "calculate_sum"
        }
        
        for key, value in replacements.items():
            template = template.replace(f"{{{key}}}", value)
        
        return template
    
    def _fill_creative_template(self, template: str, complexity: str, language: str) -> str:
        """填充创意写作模板"""
        topics = ["春天", "友谊", "梦想", "家乡", "未来"]
        styles = ["散文", "小说", "诗歌", "日记", "故事"]
        themes = ["爱情", "成长", "冒险", "友谊", "希望"]
        
        replacements = {
            "topic": random.choice(topics),
            "style": random.choice(styles),
            "theme": random.choice(themes),
            "genre": "科幻",
            "tone": "温暖",
            "content_type": "短文",
            "character": "勇敢的探险家",
            "length": "500字",
            "setting": "未来世界",
            "emotion": "喜悦",
            "format": "诗歌"
        }
        
        for key, value in replacements.items():
            template = template.replace(f"{{{key}}}", value)
        
        return template
    
    def _fill_translation_template(self, template: str, complexity: str, language: str) -> str:
        """填充翻译模板"""
        source_langs = ["英文", "中文", "日文", "法文", "德文"]
        target_langs = ["中文", "英文", "日文", "法文", "德文"]
        
        replacements = {
            "source_lang": random.choice(source_langs),
            "target_lang": random.choice(target_langs),
            "text": "Hello, how are you?",
            "domain": "技术",
            "style": "正式",
            "content_type": "文档",
            "technical_field": "计算机科学"
        }
        
        for key, value in replacements.items():
            template = template.replace(f"{{{key}}}", value)
        
        return template
    
    def _fill_math_template(self, template: str, complexity: str, language: str) -> str:
        """填充数学模板"""
        math_types = ["线性", "二次", "三角", "指数", "对数"]
        expressions = ["2x + 3 = 7", "x² - 5x + 6 = 0", "sin(x) = 0.5"]
        
        replacements = {
            "math_type": random.choice(math_types),
            "equation": random.choice(expressions),
            "calculation_type": "积分",
            "expression": "∫x²dx",
            "theorem_type": "勾股",
            "problem_type": "优化",
            "function_type": "二次",
            "geometry_shape": "圆形",
            "property": "面积",
            "concept": "导数",
            "optimization_type": "线性规划"
        }
        
        for key, value in replacements.items():
            template = template.replace(f"{{{key}}}", value)
        
        return template
    
    def _fill_analysis_template(self, template: str, complexity: str, language: str) -> str:
        """填充分析模板"""
        topics = ["市场趋势", "用户行为", "技术发展", "经济形势", "社会现象"]
        aspects = ["优势", "劣势", "机会", "威胁", "特点"]
        
        replacements = {
            "topic": random.choice(topics),
            "aspect": random.choice(aspects),
            "phenomenon": "通胀",
            "subject": "新产品",
            "criteria": "性价比",
            "item1": "方案A",
            "item2": "方案B",
            "dimension": "成本效益",
            "content": "报告内容",
            "data_type": "销售",
            "chart_type": "柱状",
            "work": "这部作品",
            "evaluation_aspect": "艺术价值"
        }
        
        for key, value in replacements.items():
            template = template.replace(f"{{{key}}}", value)
        
        return template
    
    def _fill_qa_template(self, template: str, complexity: str, language: str) -> str:
        """填充问答模板"""
        concepts = ["人工智能", "区块链", "量子计算", "机器学习", "云计算"]
        actions = ["学习编程", "提高效率", "管理时间", "保持健康", "投资理财"]
        
        replacements = {
            "concept": random.choice(concepts),
            "action": random.choice(actions),
            "phenomenon": "全球变暖",
            "category": "编程语言",
            "criteria": "适合初学者",
            "find_what": "学习资源",
            "field": "科技",
            "role": "领导者",
            "topic": "人工智能",
            "aspect": "应用前景"
        }
        
        for key, value in replacements.items():
            template = template.replace(f"{{{key}}}", value)
        
        return template
    
    def _fill_summary_template(self, template: str, complexity: str, language: str) -> str:
        """填充总结模板"""
        content_types = ["文章", "报告", "论文", "新闻", "研究"]
        topics = ["技术发展", "市场分析", "用户研究", "产品评估", "行业趋势"]
        
        replacements = {
            "content_type": random.choice(content_types),
            "topic": random.choice(topics),
            "document": "技术文档",
            "discussion": "会议讨论",
            "process": "开发流程",
            "report": "季度报告",
            "meeting": "项目会议"
        }
        
        for key, value in replacements.items():
            template = template.replace(f"{{{key}}}", value)
        
        return template
    
    def _fill_general_template(self, template: str, complexity: str, language: str) -> str:
        """填充通用模板"""
        tasks = ["解决问题", "制定计划", "学习新技能", "改进流程", "优化性能"]
        requests = ["帮助我理解", "给我建议", "提供信息", "解释概念", "分析情况"]
        
        replacements = {
            "general_task": random.choice(tasks),
            "polite_request": random.choice(requests),
            "topic": "人工智能",
            "subject": "这个话题",
            "capability_request": "帮我分析",
            "advice_type": "学习",
            "recommendation_type": "书籍",
            "explanation_target": "这个概念"
        }
        
        for key, value in replacements.items():
            template = template.replace(f"{{{key}}}", value)
        
        return template
    
    def calculate_model_performance(self, prompt: str, model: str, task_type: str, 
                                  complexity: str, priority: str = "performance") -> float:
        """计算模型在特定prompt上的性能分数"""
        base_performance = self.model_performance_profiles[model][task_type]
        
        # 基础分数
        if priority == "performance":
            score = base_performance["quality"]
        elif priority == "speed":
            score = base_performance["speed"]
        elif priority == "cost":
            score = base_performance["cost"]
        else:  # balanced
            score = (base_performance["quality"] + base_performance["speed"] + base_performance["cost"]) / 3
        
        # 复杂度调整
        if complexity == "复杂":
            if model in ["gpt-4o", "claude-3-5-sonnet-20241022", "claude-3-7-sonnet-20250219", "gemini-1.5-pro-002"]:
                score += 0.05  # 高端模型在复杂任务上表现更好
            else:
                score -= 0.03  # 其他模型在复杂任务上表现下降
        elif complexity == "简单":
            if model in ["gpt-4o-mini", "claude-3-5-haiku-20241022", "gemini-1.5-flash-002"]:
                score += 0.03  # 轻量模型在简单任务上更有优势
        
        # 添加随机噪声模拟真实场景
        noise = np.random.normal(0, 0.02)
        score = max(0.1, min(1.0, score + noise))
        
        return score
    
    def generate_training_sample(self) -> Dict:
        """生成一个训练样本"""
        # 随机选择任务参数
        task_type = random.choice(list(self.task_templates.keys()))
        complexity = random.choice(["简单", "中等", "复杂"])
        language = random.choice(["中文", "英文"])
        priority = random.choice(["performance", "speed", "cost", "balanced"])
        
        # 生成prompt
        prompt = self.generate_prompt(task_type, complexity, language)
        
        # 计算所有模型的性能
        model_performances = {}
        for model in self.model_performance_profiles.keys():
            score = self.calculate_model_performance(prompt, model, task_type, complexity, priority)
            model_performances[model] = score
        
        # 找出最佳模型
        best_model = max(model_performances.items(), key=lambda x: x[1])
        
        # 创建标签 - 多分类标签
        task_label = list(self.task_templates.keys()).index(task_type)
        complexity_label = ["简单", "中等", "复杂"].index(complexity)
        language_label = ["中文", "英文"].index(language)
        
        # 模型排名标签
        sorted_models = sorted(model_performances.items(), key=lambda x: x[1], reverse=True)
        model_rankings = [model for model, _ in sorted_models]
        
        return {
            "prompt": prompt,
            "task_type": task_type,
            "task_label": task_label,
            "complexity": complexity,
            "complexity_label": complexity_label,
            "language": language,
            "language_label": language_label,
            "priority": priority,
            "best_model": best_model[0],
            "best_score": best_model[1],
            "model_performances": model_performances,
            "model_rankings": model_rankings,
            "labels": [task_label, complexity_label, language_label]  # 多任务标签
        }
    
    def generate_dataset(self, num_samples: int = 10000, save_path: str = None) -> Dataset:
        """生成完整的训练数据集"""
        logger.info(f"生成 {num_samples} 个训练样本...")
        
        samples = []
        for i in range(num_samples):
            if i % 1000 == 0:
                logger.info(f"已生成 {i}/{num_samples} 个样本")
            
            sample = self.generate_training_sample()
            samples.append(sample)
        
        # 转换为Dataset格式
        dataset_dict = {
            "prompt": [s["prompt"] for s in samples],
            "task_type": [s["task_type"] for s in samples],
            "task_label": [s["task_label"] for s in samples],
            "complexity": [s["complexity"] for s in samples],
            "complexity_label": [s["complexity_label"] for s in samples],
            "language": [s["language"] for s in samples],
            "language_label": [s["language_label"] for s in samples],
            "priority": [s["priority"] for s in samples],
            "best_model": [s["best_model"] for s in samples],
            "best_score": [s["best_score"] for s in samples],
            "labels": [s["labels"] for s in samples]
        }
        
        dataset = Dataset.from_dict(dataset_dict)
        
        if save_path:
            logger.info(f"保存数据集到: {save_path}")
            dataset.save_to_disk(save_path)
            
            # 同时保存JSON格式用于检查
            with open(os.path.join(save_path, "samples.json"), "w", encoding="utf-8") as f:
                json.dump(samples[:100], f, ensure_ascii=False, indent=2)  # 保存前100个样本用于检查
        
        logger.info(f"✅ 数据集生成完成，共 {len(dataset)} 个样本")
        return dataset
    
    def generate_validation_dataset(self, num_samples: int = 2000, save_path: str = None) -> Dataset:
        """生成验证数据集"""
        logger.info(f"生成 {num_samples} 个验证样本...")
        return self.generate_dataset(num_samples, save_path)

if __name__ == "__main__":
    # 测试训练数据生成器
    generator = P2LTrainingDataGenerator()
    
    # 生成少量样本进行测试
    print("🧪 测试样本生成...")
    for i in range(5):
        sample = generator.generate_training_sample()
        print(f"\n样本 {i+1}:")
        print(f"Prompt: {sample['prompt']}")
        print(f"任务类型: {sample['task_type']}")
        print(f"复杂度: {sample['complexity']}")
        print(f"语言: {sample['language']}")
        print(f"最佳模型: {sample['best_model']} (分数: {sample['best_score']:.3f})")
    
    # 生成完整数据集
    print(f"\n📊 生成训练数据集...")
    train_dataset = generator.generate_dataset(
        num_samples=1000,  # 测试用小数据集
        save_path="./p2l_training_data"
    )
    
    print(f"\n📊 生成验证数据集...")
    val_dataset = generator.generate_validation_dataset(
        num_samples=200,  # 测试用小数据集
        save_path="./p2l_validation_data"
    )
    
    print(f"\n✅ 数据生成完成!")
    print(f"训练集: {len(train_dataset)} 样本")
    print(f"验证集: {len(val_dataset)} 样本")