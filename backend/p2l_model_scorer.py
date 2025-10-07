#!/usr/bin/env python3
"""
P2L原生模型评分器
完全基于P2L模型的Bradley-Terry系数进行评分和路由
"""

from typing import Dict, List, Optional, Tuple
import logging
import numpy as np

try:
    from .config import get_task_config, get_model_config
    from .p2l_router import P2LRouter
except ImportError:
    from config import get_task_config, get_model_config
    from p2l_router import P2LRouter

logger = logging.getLogger(__name__)

class P2LModelScorer:
    """P2L原生模型评分器"""
    
    def __init__(self, model_configs: Dict, p2l_engine=None):
        self.model_configs = model_configs
        self.task_config = get_task_config()
        self.p2l_router = P2LRouter()
        
        # 模型列表（按固定顺序）
        self.model_list = list(model_configs.keys())
        logger.info(f"🎯 P2L评分器初始化，支持模型: {self.model_list}")
        
        # 初始化P2L引擎
        if p2l_engine is None:
            try:
                # 添加路径以确保能找到P2L模块
                import sys
                import os
                from pathlib import Path
                
                # 添加p2l项目路径
                current_dir = Path(__file__).parent
                p2l_project_dir = current_dir.parent / 'p2l'
                if str(p2l_project_dir) not in sys.path:
                    sys.path.insert(0, str(p2l_project_dir))
                
                from p2l_engine import P2LEngine
                self.p2l_engine = P2LEngine(device='cpu')  # 明确指定设备
                logger.info(f"✅ P2L引擎创建成功，加载状态: {self.p2l_engine.is_loaded}")
                
                if self.p2l_engine.is_loaded:
                    logger.info(f"🎉 真实P2L模型已加载，支持{len(self.p2l_engine.model_list)}个模型")
                else:
                    logger.warning(f"⚠️ P2L模型未加载，将使用模拟系数")
                    
            except Exception as e:
                logger.error(f"❌ P2L引擎创建失败: {e}")
                import traceback
                traceback.print_exc()
                self.p2l_engine = None
        else:
            self.p2l_engine = p2l_engine
    
    def calculate_p2l_scores(
        self, 
        prompt: str, 
        priority: str, 
        enabled_models: Optional[List[str]] = None,
        budget: Optional[float] = None
    ) -> Tuple[List[Dict], Dict]:
        """
        使用P2L模型计算原生评分
        
        Args:
            prompt: 用户输入的提示词
            priority: 优先级模式 (performance/cost/speed/balanced)
            enabled_models: 启用的模型列表
            budget: 预算约束（可选）
        
        Returns:
            (rankings, routing_info)
        """
        print("\n" + "="*80)
        print(f"🧠 【P2L评分开始】")
        print(f"📝 提示词: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        print(f"🎯 优先级模式: {priority}")
        print(f"🔧 启用模型: {enabled_models}")
        print(f"💰 预算约束: {budget}")
        print("="*80)
        
        logger.info(f"🧠 开始P2L原生评分: 模式={priority}")
        
        try:
            # 1. 获取P2L模型的Bradley-Terry系数
            print(f"\n🔍 【步骤1】获取P2L模型的Bradley-Terry系数...")
            p2l_coefficients = self._get_p2l_coefficients(prompt)
            print(f"📊 Bradley-Terry系数: {p2l_coefficients}")
            print(f"📈 系数统计: 最大={p2l_coefficients.max():.3f}, 最小={p2l_coefficients.min():.3f}, 平均={p2l_coefficients.mean():.3f}")
            
            # 2. 使用P2L路由器进行智能路由
            print(f"\n🎯 【步骤2】P2L路由器智能路由...")
            print(f"🔄 路由模式: {priority}")
            selected_model, routing_info = self.p2l_router.route_models(
                p2l_coefficients=p2l_coefficients,
                model_list=self.model_list,
                model_configs=self.model_configs,
                mode=priority,
                budget=budget,
                enabled_models=enabled_models
            )
            print(f"🏆 路由结果: {selected_model}")
            print(f"📋 路由信息: {routing_info}")
            
            # 3. 生成完整的模型排名（根据优先模式调整）
            print(f"\n📊 【步骤3】生成完整模型排名...")
            rankings = self.p2l_router.generate_model_ranking(
                p2l_coefficients=p2l_coefficients,
                model_list=self.model_list,
                model_configs=self.model_configs,
                mode=priority,  # 传递优先模式
                enabled_models=enabled_models
            )
            print(f"📈 排名生成完成，共{len(rankings)}个模型")
            
            # 打印详细排名
            print(f"\n🏅 【模型排名详情】")
            for i, ranking in enumerate(rankings[:5], 1):  # 只显示前5名
                print(f"  {i}. {ranking['model']}: 评分={ranking['score']:.2f}, P2L系数={ranking.get('p2l_coefficient', 0):.3f}")
            
            # 4. 添加路由解释
            routing_info["explanation"] = self.p2l_router.get_routing_explanation(routing_info)
            routing_info["prompt_length"] = len(prompt)
            
            print(f"\n✅ 【P2L评分完成】")
            print(f"🎯 推荐模型: {selected_model}")
            print(f"📊 总排名数: {len(rankings)}")
            print(f"🔍 路由策略: {routing_info.get('strategy', 'unknown')}")
            print(f"💡 解释: {routing_info.get('explanation', 'N/A')}")
            print("="*80)
            
            logger.info(f"✅ P2L评分完成: 推荐模型={selected_model}, 总排名={len(rankings)}")
            return rankings, routing_info
            
        except Exception as e:
            print(f"\n❌ 【P2L评分失败】: {e}")
            print(f"🔄 启用降级评分...")
            logger.error(f"❌ P2L评分失败: {e}")
            # 降级到基础评分
            fallback_result = self._fallback_scoring(enabled_models)
            print(f"✅ 降级评分完成，共{len(fallback_result)}个模型")
            return fallback_result, {
                "strategy": "fallback",
                "error": str(e),
                "explanation": "P2L评分失败，使用降级评分"
            }
    
    def _get_p2l_coefficients(self, prompt: str) -> np.ndarray:
        """获取P2L模型的Bradley-Terry系数"""
        print(f"\n🔍 【获取P2L系数】")
        print(f"📝 提示词长度: {len(prompt)} 字符")
        
        if not self.p2l_engine:
            print(f"⚠️ P2L引擎未加载，使用模拟系数")
            logger.warning("⚠️ P2L引擎未加载，使用模拟系数")
            coefficients = self._generate_mock_coefficients()
            print(f"🎲 模拟系数: {coefficients}")
            return coefficients
        
        try:
            print(f"🎯 调用P2L引擎获取Bradley-Terry系数...")
            logger.info("🎯 调用P2L模型获取Bradley-Terry系数")
            
            # 使用P2L引擎计算系数
            coefficients = self.p2l_engine.get_bradley_terry_coefficients(
                prompt=prompt,
                model_list=self.model_list
            )
            
            print(f"✅ P2L引擎返回{len(coefficients)}个系数")
            return coefficients
            
        except Exception as e:
            print(f"❌ P2L系数获取失败: {e}")
            print(f"🔄 使用模拟系数作为备用...")
            logger.error(f"❌ P2L系数获取失败: {e}")
            coefficients = self._generate_mock_coefficients()
            print(f"🎲 备用模拟系数: {coefficients}")
            return coefficients
    
    def _generate_mock_coefficients(self) -> np.ndarray:
        """生成模拟的Bradley-Terry系数（用于测试和降级）"""
        print(f"🎲 【生成模拟P2L系数】")
        
        # 生成基于模型质量的模拟系数
        coefficients = []
        
        # 预设的模型质量评分（基于真实模型表现）
        model_quality_scores = {
            "claude-3-5-sonnet-20241022": 0.85,  # 顶级模型
            "gpt-4o-2024-08-06": 0.80,          # 顶级模型
            "claude-3-opus-20240229": 0.78,      # 高质量模型
            "gpt-4-turbo-2024-04-09": 0.75,     # 高质量模型
            "gemini-1.5-pro-002": 0.70,         # 中高质量模型
            "claude-3-sonnet-20240229": 0.65,   # 中等模型
            "gpt-4o-mini-2024-07-18": 0.60,     # 轻量但高效模型
            "claude-3-haiku-20240307": 0.55,    # 快速模型
            "gemini-1.5-flash-002": 0.50,       # 快速模型
            "gpt-3.5-turbo-0125": 0.45          # 基础模型
        }
        
        for model_name in self.model_list:
            config = self.model_configs[model_name]
            
            # 获取基础质量评分
            base_quality = model_quality_scores.get(model_name, 0.5)
            
            # 根据成本效益调整（成本越低相对优势越大）
            cost_efficiency = max(0.1, min(2.0, 0.01 / config["cost_per_1k"]))
            cost_factor = min(1.2, 1.0 + (cost_efficiency - 1.0) * 0.1)  # 轻微成本优势
            
            # 根据响应速度调整（速度越快相对优势越大）
            speed_efficiency = max(0.1, min(2.0, 3.0 / config["avg_response_time"]))
            speed_factor = min(1.2, 1.0 + (speed_efficiency - 1.0) * 0.1)  # 轻微速度优势
            
            # 计算最终系数
            adjusted_quality = base_quality * cost_factor * speed_factor
            
            # 转换为Bradley-Terry系数范围 [0.1, 2.0]，避免负数
            # Bradley-Terry系数应该是正数，表示相对强度
            coef = max(0.1, min(2.0, adjusted_quality * 2.0))
            
            # 添加小量随机噪声，但保持正数
            noise = np.random.normal(0, 0.05)
            coef = max(0.1, coef + noise)
            
            coefficients.append(coef)
            
            print(f"   {model_name}: 基础质量={base_quality:.2f}, "
                  f"成本因子={cost_factor:.2f}, 速度因子={speed_factor:.2f}, "
                  f"最终系数={coef:.3f}")
        
        coefficients = np.array(coefficients)
        print(f"✅ 模拟系数生成完成: 范围[{coefficients.min():.3f}, {coefficients.max():.3f}]")
        
        logger.info("🔄 生成改进的模拟P2L系数")
        return coefficients
    
    def _fallback_scoring(self, enabled_models: Optional[List[str]] = None) -> List[Dict]:
        """降级评分方法"""
        scores = []
        
        models_to_score = self.model_list
        if enabled_models:
            models_to_score = [m for m in self.model_list if m in enabled_models]
        
        for model_name in models_to_score:
            config = self.model_configs[model_name]
            
            # 基于P2L系数的分数
            cost_factor = max(0.1, min(1.0, 0.05 / config["cost_per_1k"]))
            speed_factor = max(0.1, min(1.0, 5.0 / config["avg_response_time"]))
            score = (cost_factor * speed_factor) * 100
            
            scores.append({
                "model": model_name,
                "score": score,
                "p2l_coefficient": score / 100 - 0.5,  # 转换为系数格式
                "config": config,
                "provider": config["provider"],
                "cost_per_1k": config["cost_per_1k"],
                "avg_response_time": config["avg_response_time"],
                "cost_per_1k": config["cost_per_1k"],
                "avg_response_time": config["avg_response_time"]
            })
        
        # 按分数排序
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores
    
    def generate_recommendation_reasoning(
        self, 
        best_model: Dict, 
        routing_info: Dict, 
        priority: str
    ) -> str:
        """生成P2L推荐理由"""
        model_name = best_model["model"]
        strategy = routing_info.get("strategy", "unknown")
        p2l_score = best_model.get("p2l_coefficient", 0)
        
        reasoning_parts = []
        
        # 基于P2L系数的推荐理由
        if p2l_score > 0.3:
            reasoning_parts.append("P2L模型高度推荐")
        elif p2l_score > 0:
            reasoning_parts.append("P2L模型推荐")
        else:
            reasoning_parts.append("P2L模型中等推荐")
        
        # 基于路由策略的理由
        strategy_reasons = {
            "max_score": "性能表现最优",
            "speed_weighted": "速度与性能平衡最佳",
            "strict": "成本效益最优",
            "simple-lp": "综合优化最佳",
            "optimal-lp": "Bradley-Terry最优",
            "fallback": "降级选择"
        }
        
        if strategy in strategy_reasons:
            reasoning_parts.append(strategy_reasons[strategy])
        
        # 基于模型特性的理由
        config = best_model["config"]
        if priority == "cost" and config["cost_per_1k"] < 0.01:
            reasoning_parts.append("成本效益高")
        elif priority == "speed" and config["avg_response_time"] < 2.0:
            reasoning_parts.append("响应速度快")
        elif priority == "performance" and config["cost_per_1k"] < 0.01:
            reasoning_parts.append("性能表现优秀")
        
        return "；".join(reasoning_parts) if reasoning_parts else "P2L智能推荐"