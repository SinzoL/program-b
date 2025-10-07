#!/usr/bin/env python3
"""
P2L原生路由器模块
实现基于Bradley-Terry系数的智能路由和成本优化
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod

try:
    import cvxpy as cp
    from scipy.special import expit
    CVXPY_AVAILABLE = True
except ImportError:
    CVXPY_AVAILABLE = False
    logging.warning("cvxpy或scipy未安装，成本优化功能将不可用")

logger = logging.getLogger(__name__)

class UnfulfillableException(Exception):
    """预算无法满足异常"""
    pass

class BaseCostOptimizer(ABC):
    """成本优化器基类"""
    
    @staticmethod
    @abstractmethod
    def select_model(
        cost: Optional[float],
        model_list: List[str],
        model_costs: np.ndarray,
        model_scores: np.ndarray,
        **kwargs,
    ) -> str:
        """选择最优模型"""
        pass

    @staticmethod
    def select_max_score_model(
        model_list: List[str], 
        model_scores: np.ndarray
    ) -> str:
        """选择评分最高的模型"""
        max_idx = np.argmax(model_scores)
        return model_list[max_idx]

class StrictCostOptimizer(BaseCostOptimizer):
    """严格成本约束优化器"""
    
    @staticmethod
    def select_model(
        cost: Optional[float],
        model_list: List[str],
        model_costs: np.ndarray,
        model_scores: np.ndarray,
        **kwargs,
    ) -> str:
        if cost is None:
            return StrictCostOptimizer.select_max_score_model(model_list, model_scores)

        best_model: Optional[str] = None
        best_score = -float("inf")

        for model, model_cost, model_score in zip(model_list, model_costs, model_scores):
            if model_cost > cost:
                continue
            elif model_score > best_score:
                best_model = model
                best_score = model_score

        if best_model is None:
            raise UnfulfillableException(
                f"预算 {cost} 无法满足，可用模型: {model_list}，成本: {model_costs}"
            )

        return best_model

class SimpleLPCostOptimizer(BaseCostOptimizer):
    """简单线性规划优化器"""
    
    @staticmethod
    def select_model(
        cost: Optional[float],
        model_list: List[str],
        model_costs: np.ndarray,
        model_scores: np.ndarray,
        **kwargs,
    ) -> str:
        if not CVXPY_AVAILABLE:
            logger.warning("cvxpy不可用，降级到严格成本优化")
            return StrictCostOptimizer.select_model(cost, model_list, model_costs, model_scores)
        
        if cost is None:
            return StrictCostOptimizer.select_max_score_model(model_list, model_scores)

        p = cp.Variable(len(model_costs))

        prob = cp.Problem(
            cp.Maximize(cp.sum(model_scores @ p)),
            [model_costs.T @ p <= cost, cp.sum(p) == 1, p >= 0],
        )

        status = prob.solve()

        if status < 0.0:
            raise UnfulfillableException(
                f"预算 {cost} 无法满足，可用模型: {model_list}，成本: {model_costs}"
            )

        ps = np.clip(p.value, a_min=0.0, a_max=1.0)
        ps = ps / ps.sum()

        return np.random.choice(model_list, p=ps)

class OptimalLPCostOptimizer(BaseCostOptimizer):
    """最优线性规划优化器（Bradley-Terry）"""
    
    @staticmethod
    def select_model(
        cost: Optional[float],
        model_list: List[str],
        model_costs: np.ndarray,
        model_scores: np.ndarray,
        opponent_scores: Optional[np.ndarray] = None,
        opponent_distribution: Optional[np.ndarray] = None,
        **kwargs,
    ) -> str:
        if not CVXPY_AVAILABLE:
            logger.warning("cvxpy不可用，降级到严格成本优化")
            return StrictCostOptimizer.select_model(cost, model_list, model_costs, model_scores)
        
        if cost is None:
            return StrictCostOptimizer.select_max_score_model(model_list, model_scores)

        # 如果没有对手信息，使用简化版本
        if opponent_scores is None or opponent_distribution is None:
            logger.info("缺少对手信息，使用简化线性规划")
            return SimpleLPCostOptimizer.select_model(cost, model_list, model_costs, model_scores)

        W = OptimalLPCostOptimizer._construct_W(model_scores, opponent_scores)
        Wq = W @ opponent_distribution

        p = cp.Variable(len(model_costs))

        prob = cp.Problem(
            cp.Maximize(p @ Wq), 
            [model_costs.T @ p <= cost, cp.sum(p) == 1, p >= 0]
        )

        status = prob.solve()

        if status < 0.0:
            raise UnfulfillableException(
                f"预算 {cost} 无法满足，可用模型: {model_list}，成本: {model_costs}"
            )

        ps = np.clip(p.value, a_min=0.0, a_max=1.0)
        ps = ps / ps.sum()

        return np.random.choice(model_list, p=ps)

    @staticmethod
    def _construct_W(
        router_model_scores: np.ndarray, 
        opponent_model_scores: np.ndarray
    ) -> np.ndarray:
        """构建Bradley-Terry胜率矩阵"""
        num_rows = router_model_scores.shape[-1]
        num_cols = opponent_model_scores.shape[-1]

        chosen = np.tile(router_model_scores, (num_cols, 1)).T
        rejected = np.tile(opponent_model_scores, (num_rows, 1))

        assert chosen.shape == rejected.shape, (chosen.shape, rejected.shape)

        diff_matrix = chosen - rejected
        W = expit(diff_matrix)

        return W

class P2LRouter:
    """P2L原生路由器"""
    
    # 采样权重配置 - 基于我们实际配置的模型能力和使用频率
    SAMPLING_WEIGHTS = {
        # ================== OpenAI 模型 ==================
        "gpt-4o-2024-08-06": 6,              # 高性能模型，最高权重
        "gpt-4o-mini-2024-07-18": 4,         # 高性价比模型，高权重
        "gpt-3.5-turbo-0125": 3,             # 经典模型，中等权重
        "gpt-4-turbo-2024-04-09": 5,         # 高性能但成本较高，高权重
        
        # ================== Anthropic 模型 ==================
        "claude-3-5-sonnet-20241022": 6,     # 顶级模型，最高权重
        "claude-3-5-haiku-20241022": 4,      # 快速模型，高权重
        "claude-3-5-sonnet-20240620": 5,     # 经典版本，高权重
        
        # ================== Google 模型 ==================
        "gemini-1.5-flash-001": 3,           # 快速模型，中等权重
        "gemini-1.5-pro-001": 5,             # 专业模型，高权重
        "gemini-1.5-pro-002": 5,             # 最新专业版，高权重
        
        # ================== DeepSeek 模型 ==================
        "deepseek-v2.5": 3,                  # 经济实用，中等权重
        "deepseek-v3": 4,                    # 最新版本，高权重
        
        # ================== DashScope (阿里云) 模型 ==================
        "qwen-max-0428": 5,                  # 顶级模型，高权重
        "qwen-max-0919": 5,                  # 最新顶级版，高权重
        "qwen1.5-110b-chat": 4,              # 大参数模型，高权重
        "qwen1.5-14b-chat": 2,               # 小模型，低权重
        "qwen1.5-32b-chat": 3,               # 中等模型，中等权重
        "qwen1.5-72b-chat": 4,               # 大模型，高权重
        "qwen2-72b-instruct": 4,             # 指令优化版，高权重
        "qwen2.5-72b-instruct": 4,           # 最新指令版，高权重
        "qwen2.5-coder-32b-instruct": 3,     # 代码专用，中等权重
    }
    
    def __init__(self):
        self.cost_optimizers = {
            'strict': StrictCostOptimizer(),
            'simple-lp': SimpleLPCostOptimizer(),
            'optimal-lp': OptimalLPCostOptimizer()
        }
        
        # 模式映射到优化策略
        self.mode_mapping = {
            'performance': 'max_score',      # 性能优先：选择最高分
            'cost': 'strict',                # 成本优先：严格成本约束
            'speed': 'speed_weighted',       # 速度优先：速度权重调整
            'balanced': 'simple-lp'          # 平衡模式：简单线性规划
        }
        
        # 初始化采样权重和对手分布
        self.opponent_distribution = None
        self.opponent_scores = None
    
    def setup_opponent_distribution(self, model_list: List[str], p2l_coefficients: np.ndarray):
        """
        设置对手分布，用于博弈论优化
        
        Args:
            model_list: 模型列表
            p2l_coefficients: P2L系数
        """
        print(f"\n🎲 【设置对手分布】")
        
        # 构建对手分布权重
        opponent_weights = []
        for model in model_list:
            weight = self.SAMPLING_WEIGHTS.get(model, 1)  # 默认权重为1
            opponent_weights.append(weight)
            print(f"   {model}: 权重={weight}")
        
        # 标准化为概率分布
        opponent_weights = np.array(opponent_weights, dtype=float)
        self.opponent_distribution = opponent_weights / opponent_weights.sum()
        self.opponent_scores = p2l_coefficients.copy()
        
        print(f"   🎯 对手分布: {self.opponent_distribution}")
        print(f"   📊 对手系数: {self.opponent_scores}")
        
        logger.info(f"🎲 对手分布设置完成，共{len(model_list)}个模型")
    
    def route_models(
        self,
        p2l_coefficients: np.ndarray,
        model_list: List[str],
        model_configs: Dict[str, Dict],
        mode: str = 'balanced',
        budget: Optional[float] = None,
        enabled_models: Optional[List[str]] = None
    ) -> Tuple[str, Dict]:
        """
        P2L原生路由主方法
        
        Args:
            p2l_coefficients: P2L模型输出的Bradley-Terry系数
            model_list: 可用模型列表
            model_configs: 模型配置信息
            mode: 路由模式 (performance/cost/speed/balanced)
            budget: 预算约束（可选）
            enabled_models: 启用的模型列表（可选）
        
        Returns:
            (selected_model, routing_info)
        """
        print(f"\n🎯 【P2L路由器】开始智能路由...")
        print(f"📊 输入系数: {p2l_coefficients}")
        print(f"📋 可用模型: {model_list}")
        print(f"🎛️ 路由模式: {mode}")
        print(f"💰 预算约束: {budget}")
        print(f"✅ 启用模型: {enabled_models}")
        
        logger.info(f"🎯 P2L路由开始: 模式={mode}, 预算={budget}")
        
        # 过滤启用的模型
        print(f"\n🔍 【模型过滤】")
        if enabled_models:
            filtered_indices = [i for i, model in enumerate(model_list) if model in enabled_models]
            if not filtered_indices:
                print(f"❌ 没有启用的模型可用！")
                raise ValueError("没有启用的模型可用")
            
            original_models = model_list.copy()
            original_coefficients = p2l_coefficients.copy()
            
            model_list = [model_list[i] for i in filtered_indices]
            p2l_coefficients = p2l_coefficients[filtered_indices]
            
            print(f"📋 原始模型: {original_models}")
            print(f"📊 原始系数: {original_coefficients}")
            print(f"✂️ 过滤后模型: {model_list}")
            print(f"📊 过滤后系数: {p2l_coefficients}")
            
            logger.info(f"🔍 过滤后的模型: {model_list}")
        else:
            print(f"📋 使用全部模型: {model_list}")
        
        print(f"✅ 最终可用模型数: {len(model_list)}")
        
        # 提取模型成本和其他属性
        print(f"\n📊 【模型属性提取】")
        model_costs = np.array([model_configs[model]["cost_per_1k"] for model in model_list])
        model_response_times = np.array([model_configs[model]["avg_response_time"] for model in model_list])
        
        print(f"💰 模型成本: {model_costs}")
        print(f"⚡ 响应时间: {model_response_times}")
        
        # 打印每个模型的详细信息
        for i, model in enumerate(model_list):
            config = model_configs[model]
            print(f"   {i+1}. {model}:")
            print(f"      P2L系数: {p2l_coefficients[i]:.3f}")
            print(f"      成本: ${model_costs[i]:.4f}/1k")
            print(f"      响应时间: {model_response_times[i]:.1f}s")
            print(f"      成本: ${config['cost_per_1k']:.4f}/1k")
        
        # 根据模式选择路由策略
        strategy = self.mode_mapping.get(mode, 'simple-lp')
        print(f"\n🎯 【路由策略选择】")
        print(f"🔄 模式映射: {mode} → {strategy}")
        
        try:
            print(f"\n🚀 【执行路由策略】: {strategy}")
            
            if strategy == 'max_score':
                print(f"🏆 执行性能优先策略...")
                # 性能优先：直接选择P2L评分最高的模型
                selected_model = self._select_max_score(model_list, p2l_coefficients)
                selected_score = float(p2l_coefficients[model_list.index(selected_model)])
                print(f"   🎯 选择模型: {selected_model}")
                print(f"   📊 P2L评分: {selected_score:.3f}")
                
                routing_info = {
                    "strategy": "max_score",
                    "p2l_scores": p2l_coefficients.tolist(),
                    "selected_score": selected_score
                }
                
            elif strategy == 'speed_weighted':
                print(f"⚡ 执行速度权重策略...")
                # 速度优先：P2L分数与速度权重结合
                selected_model = self._select_speed_weighted(
                    model_list, p2l_coefficients, model_response_times
                )
                print(f"   🎯 选择模型: {selected_model}")
                
                routing_info = {
                    "strategy": "speed_weighted",
                    "p2l_scores": p2l_coefficients.tolist(),
                    "response_times": model_response_times.tolist()
                }
                
            elif strategy in self.cost_optimizers:
                print(f"💰 执行成本优化策略: {strategy}")
                print(f"   💵 预算约束: {budget}")
                print(f"   🔧 优化器: {type(self.cost_optimizers[strategy]).__name__}")
                
                # 设置对手分布（用于博弈论优化）
                self.setup_opponent_distribution(model_list, p2l_coefficients)
                
                # 成本优化策略
                optimizer = self.cost_optimizers[strategy]
                
                # 为OptimalLPCostOptimizer提供对手分布信息
                if strategy == 'optimal-lp' and self.opponent_distribution is not None:
                    print(f"   🎲 使用对手分布优化")
                    selected_model = optimizer.select_model(
                        cost=budget,
                        model_list=model_list,
                        model_costs=model_costs,
                        model_scores=p2l_coefficients,
                        opponent_scores=self.opponent_scores,
                        opponent_distribution=self.opponent_distribution
                    )
                else:
                    selected_model = optimizer.select_model(
                        cost=budget,
                        model_list=model_list,
                        model_costs=model_costs,
                        model_scores=p2l_coefficients
                    )
                
                print(f"   🎯 优化结果: {selected_model}")
                
                routing_info = {
                    "strategy": strategy,
                    "budget": budget,
                    "p2l_scores": p2l_coefficients.tolist(),
                    "model_costs": model_costs.tolist(),
                    "opponent_distribution": self.opponent_distribution.tolist() if self.opponent_distribution is not None else None
                }
                
            else:
                print(f"❌ 未知的路由策略: {strategy}")
                raise ValueError(f"未知的路由策略: {strategy}")
            
            # 添加通用信息
            routing_info.update({
                "selected_model": selected_model,
                "mode": mode,
                "total_models": len(model_list),
                "cvxpy_available": CVXPY_AVAILABLE
            })
            
            logger.info(f"✅ P2L路由完成: 选择模型={selected_model}, 策略={strategy}")
            return selected_model, routing_info
            
        except Exception as e:
            logger.error(f"❌ P2L路由失败: {e}")
            # 降级到最高分模型
            fallback_model = self._select_max_score(model_list, p2l_coefficients)
            routing_info = {
                "strategy": "fallback_max_score",
                "error": str(e),
                "selected_model": fallback_model
            }
            return fallback_model, routing_info
    
    def _select_max_score(self, model_list: List[str], scores: np.ndarray) -> str:
        """选择评分最高的模型"""
        max_idx = np.argmax(scores)
        return model_list[max_idx]
    
    def _select_speed_weighted(
        self, 
        model_list: List[str], 
        p2l_scores: np.ndarray, 
        response_times: np.ndarray
    ) -> str:
        """速度权重选择：结合P2L分数和响应时间"""
        print(f"\n   ⚡ 【速度权重计算】")
        print(f"   📊 原始P2L分数: {p2l_scores}")
        print(f"   ⏱️ 响应时间: {response_times}")
        
        # 将响应时间转换为速度分数（时间越短分数越高）
        max_time = np.max(response_times)
        speed_scores = (max_time - response_times) / max_time
        print(f"   🚀 速度分数: {speed_scores}")
        
        # 结合P2L分数和速度分数（权重可调）
        p2l_weight = 0.6
        speed_weight = 0.4
        print(f"   ⚖️ 权重设置: P2L={p2l_weight}, 速度={speed_weight}")
        
        # 标准化P2L分数到0-1
        p2l_min, p2l_max = np.min(p2l_scores), np.max(p2l_scores)
        normalized_p2l = (p2l_scores - p2l_min) / (p2l_max - p2l_min + 1e-8)
        print(f"   📈 标准化P2L: {normalized_p2l}")
        
        combined_scores = p2l_weight * normalized_p2l + speed_weight * speed_scores
        print(f"   🎯 综合分数: {combined_scores}")
        
        # 打印每个模型的详细计算
        for i, model in enumerate(model_list):
            print(f"      {model}: P2L={p2l_scores[i]:.3f}→{normalized_p2l[i]:.3f}, "
                  f"速度={response_times[i]:.1f}s→{speed_scores[i]:.3f}, "
                  f"综合={combined_scores[i]:.3f}")
        
        max_idx = np.argmax(combined_scores)
        selected_model = model_list[max_idx]
        print(f"   🏆 速度权重选择结果: {selected_model} (综合分数: {combined_scores[max_idx]:.3f})")
        
        return selected_model
    
    def generate_model_ranking(
        self,
        p2l_coefficients: np.ndarray,
        model_list: List[str],
        model_configs: Dict[str, Dict],
        mode: str = 'balanced',
        enabled_models: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        生成基于优先模式调整的模型排名
        
        Args:
            p2l_coefficients: P2L系数
            model_list: 模型列表
            model_configs: 模型配置
            mode: 优先模式，影响评分计算
            enabled_models: 启用的模型列表
        
        Returns:
            排序后的模型列表，包含调整后的评分
        """
        print(f"\n📊 【生成模型排名】优先模式: {mode}")
        
        # 过滤启用的模型
        if enabled_models:
            filtered_data = [
                (model, coef, model_configs[model]) 
                for model, coef in zip(model_list, p2l_coefficients) 
                if model in enabled_models
            ]
            if not filtered_data:
                return []
            
            model_list, p2l_coefficients, configs = zip(*filtered_data)
            p2l_coefficients = np.array(p2l_coefficients)
        else:
            configs = [model_configs[model] for model in model_list]
        
        # 根据优先模式计算调整后的评分
        adjusted_scores = self._calculate_mode_adjusted_scores(
            p2l_coefficients, model_list, model_configs, mode
        )
        
        # 创建排名列表
        rankings = []
        for i, (model, p2l_coef, adj_score, config) in enumerate(zip(model_list, p2l_coefficients, adjusted_scores, configs)):
            rankings.append({
                "model": model,
                "score": float(adj_score),  # 调整后的综合评分
                "p2l_coefficient": float(p2l_coef),  # 原始P2L系数
                "config": config,
                "provider": config["provider"],
                "cost_per_1k": config["cost_per_1k"],
                "avg_response_time": config["avg_response_time"]
            })
        
        # 按调整后的评分排序
        rankings.sort(key=lambda x: x["score"], reverse=True)
        
        print(f"📈 排名调整完成:")
        for i, ranking in enumerate(rankings[:3], 1):
            print(f"  {i}. {ranking['model']}: 综合评分={ranking['score']:.3f}, P2L系数={ranking['p2l_coefficient']:.3f}")
        
        logger.info(f"📊 模式调整的模型排名生成完成，共{len(rankings)}个模型")
        return rankings
    
    def _calculate_mode_adjusted_scores(
        self,
        p2l_coefficients: np.ndarray,
        model_list: List[str],
        model_configs: Dict[str, Dict],
        mode: str
    ) -> np.ndarray:
        """
        根据优先模式计算调整后的模型评分
        
        Args:
            p2l_coefficients: 原始P2L系数
            model_list: 模型列表
            model_configs: 模型配置
            mode: 优先模式
            
        Returns:
            调整后的评分数组
        """
        print(f"🔧 【评分调整】模式: {mode}")
        
        # 提取模型属性
        costs = np.array([model_configs[model]["cost_per_1k"] for model in model_list])
        response_times = np.array([model_configs[model]["avg_response_time"] for model in model_list])
        
        # 标准化P2L系数到0-1范围
        p2l_min, p2l_max = np.min(p2l_coefficients), np.max(p2l_coefficients)
        if p2l_max > p2l_min:
            normalized_p2l = (p2l_coefficients - p2l_min) / (p2l_max - p2l_min)
        else:
            normalized_p2l = np.ones_like(p2l_coefficients) * 0.5
        
        # 标准化成本分数（成本越低分数越高）
        max_cost = np.max(costs)
        cost_scores = (max_cost - costs) / max_cost if max_cost > 0 else np.ones_like(costs)
        
        # 标准化速度分数（时间越短分数越高）
        max_time = np.max(response_times)
        speed_scores = (max_time - response_times) / max_time if max_time > 0 else np.ones_like(response_times)
        
        print(f"   📊 标准化P2L: {normalized_p2l}")
        print(f"   💰 成本分数: {cost_scores}")
        print(f"   ⚡ 速度分数: {speed_scores}")
        
        # 根据模式设置权重 - 极端差异化配置
        if mode == 'performance':
            # 性能优先：几乎完全依赖P2L系数
            weights = {'p2l': 0.95, 'cost': 0.025, 'speed': 0.025}
        elif mode == 'cost':
            # 成本优先：几乎完全依赖成本效益
            weights = {'p2l': 0.1, 'cost': 0.85, 'speed': 0.05}
        elif mode == 'speed':
            # 速度优先：几乎完全依赖响应速度
            weights = {'p2l': 0.1, 'cost': 0.05, 'speed': 0.85}
        elif mode == 'balanced':
            # 平衡模式：相对均衡但仍有侧重
            weights = {'p2l': 0.5, 'cost': 0.25, 'speed': 0.25}
        else:
            # 默认平衡模式
            weights = {'p2l': 0.5, 'cost': 0.25, 'speed': 0.25}
        
        print(f"   ⚖️ 权重设置: P2L={weights['p2l']}, 成本={weights['cost']}, 速度={weights['speed']}")
        
        # 计算综合评分
        adjusted_scores = (
            weights['p2l'] * normalized_p2l +
            weights['cost'] * cost_scores +
            weights['speed'] * speed_scores
        )
        
        print(f"   🎯 调整后评分: {adjusted_scores}")
        
        # 打印每个模型的详细计算
        for i, model in enumerate(model_list):
            print(f"      {model}: P2L={normalized_p2l[i]:.3f}*{weights['p2l']} + "
                  f"成本={cost_scores[i]:.3f}*{weights['cost']} + "
                  f"速度={speed_scores[i]:.3f}*{weights['speed']} = {adjusted_scores[i]:.3f}")
        
        return adjusted_scores
    
    def get_routing_explanation(self, routing_info: Dict) -> str:
        """生成路由选择的解释"""
        strategy = routing_info.get("strategy", "unknown")
        selected_model = routing_info.get("selected_model", "unknown")
        
        explanations = {
            "max_score": f"性能优先模式：选择P2L评分最高的模型 {selected_model}",
            "speed_weighted": f"速度优先模式：综合P2L评分和响应速度选择 {selected_model}",
            "strict": f"成本优先模式：在预算约束内选择最佳模型 {selected_model}",
            "simple-lp": f"平衡模式：使用线性规划优化选择 {selected_model}",
            "optimal-lp": f"最优模式：使用Bradley-Terry优化选择 {selected_model}",
            "fallback_max_score": f"降级模式：选择P2L评分最高的模型 {selected_model}"
        }
        
        return explanations.get(strategy, f"选择了模型 {selected_model}")
    
    def _strict_cost_optimization(
        self, 
        p2l_coefficients: np.ndarray, 
        model_list: List[str], 
        model_configs: Dict[str, Dict], 
        budget: float
    ) -> str:
        """
        严格成本优化：在预算约束内选择P2L评分最高的模型
        
        Args:
            p2l_coefficients: P2L系数
            model_list: 模型列表
            model_configs: 模型配置
            budget: 预算约束
            
        Returns:
            选择的模型名称
        """
        print(f"💰 严格成本优化: 预算=${budget:.4f}/1k")
        
        # 过滤符合预算的模型
        affordable_models = []
        for i, model in enumerate(model_list):
            cost = model_configs[model]["cost_per_1k"]
            if cost <= budget:
                affordable_models.append((model, p2l_coefficients[i], cost))
                print(f"   ✅ {model}: P2L={p2l_coefficients[i]:.3f}, 成本=${cost:.4f}")
            else:
                print(f"   ❌ {model}: 超预算 (${cost:.4f} > ${budget:.4f})")
        
        if not affordable_models:
            print(f"   ⚠️ 没有模型符合预算约束，选择最便宜的模型")
            # 如果没有符合预算的模型，选择最便宜的
            costs = [model_configs[model]["cost_per_1k"] for model in model_list]
            min_cost_idx = np.argmin(costs)
            return model_list[min_cost_idx]
        
        # 在符合预算的模型中选择P2L评分最高的
        best_model = max(affordable_models, key=lambda x: x[1])
        print(f"   🏆 选择: {best_model[0]} (P2L={best_model[1]:.3f}, 成本=${best_model[2]:.4f})")
        
        return best_model[0]
    
    def _simple_lp_optimization(
        self, 
        p2l_coefficients: np.ndarray, 
        model_list: List[str], 
        model_configs: Dict[str, Dict], 
        budget: Optional[float] = None
    ) -> str:
        """
        简单线性规划优化：使用cvxpy进行成本效益优化
        
        Args:
            p2l_coefficients: P2L系数
            model_list: 模型列表
            model_configs: 模型配置
            budget: 预算约束（可选）
            
        Returns:
            选择的模型名称
        """
        try:
            import cvxpy as cp
            print(f"💡 简单线性规划优化 (cvxpy可用)")
            
            n_models = len(model_list)
            costs = np.array([model_configs[model]["cost_per_1k"] for model in model_list])
            
            # 决策变量：每个模型的选择概率
            x = cp.Variable(n_models, boolean=True)
            
            # 目标函数：最大化P2L评分
            objective = cp.Maximize(p2l_coefficients @ x)
            
            # 约束条件
            constraints = [cp.sum(x) == 1]  # 只能选择一个模型
            
            if budget is not None:
                constraints.append(costs @ x <= budget)  # 预算约束
                print(f"   💰 预算约束: ${budget:.4f}/1k")
            
            # 求解
            problem = cp.Problem(objective, constraints)
            problem.solve()
            
            if problem.status == cp.OPTIMAL:
                selected_idx = np.argmax(x.value)
                selected_model = model_list[selected_idx]
                print(f"   🎯 LP优化结果: {selected_model}")
                print(f"   📊 P2L评分: {p2l_coefficients[selected_idx]:.3f}")
                print(f"   💰 成本: ${costs[selected_idx]:.4f}/1k")
                return selected_model
            else:
                print(f"   ⚠️ LP求解失败，使用降级方案")
                return self._strict_cost_optimization(p2l_coefficients, model_list, model_configs, budget or 1.0)
                
        except ImportError:
            print(f"   ⚠️ cvxpy未安装，使用严格成本优化")
            return self._strict_cost_optimization(p2l_coefficients, model_list, model_configs, budget or 1.0)
        except Exception as e:
            print(f"   ❌ LP优化失败: {e}")
            return self._strict_cost_optimization(p2l_coefficients, model_list, model_configs, budget or 1.0)
    
    def _optimal_lp_optimization(
        self, 
        p2l_coefficients: np.ndarray, 
        model_list: List[str], 
        model_configs: Dict[str, Dict], 
        budget: Optional[float] = None
    ) -> str:
        """
        最优线性规划优化：考虑Bradley-Terry概率的高级优化
        
        Args:
            p2l_coefficients: P2L系数
            model_list: 模型列表
            model_configs: 模型配置
            budget: 预算约束（可选）
            
        Returns:
            选择的模型名称
        """
        try:
            import cvxpy as cp
            print(f"🚀 最优线性规划优化 (Bradley-Terry)")
            
            n_models = len(model_list)
            costs = np.array([model_configs[model]["cost_per_1k"] for model in model_list])
            response_times = np.array([model_configs[model]["avg_response_time"] for model in model_list])
            
            # 计算Bradley-Terry概率矩阵
            bt_probs = np.zeros((n_models, n_models))
            for i in range(n_models):
                for j in range(n_models):
                    if i != j:
                        # Bradley-Terry胜率公式
                        exp_diff = np.exp(p2l_coefficients[i] - p2l_coefficients[j])
                        bt_probs[i, j] = exp_diff / (1 + exp_diff)
            
            # 决策变量
            x = cp.Variable(n_models, boolean=True)
            
            # 目标函数：最大化期望胜率 - 成本惩罚 - 时间惩罚
            expected_win_rate = cp.sum([x[i] * cp.sum(bt_probs[i, :]) for i in range(n_models)]) / (n_models - 1)
            cost_penalty = 0.1 * (costs @ x)  # 成本惩罚权重
            time_penalty = 0.05 * (response_times @ x)  # 时间惩罚权重
            
            objective = cp.Maximize(expected_win_rate - cost_penalty - time_penalty)
            
            # 约束条件
            constraints = [cp.sum(x) == 1]  # 只能选择一个模型
            
            if budget is not None:
                constraints.append(costs @ x <= budget)  # 预算约束
                print(f"   💰 预算约束: ${budget:.4f}/1k")
            
            # 求解
            problem = cp.Problem(objective, constraints)
            problem.solve()
            
            if problem.status == cp.OPTIMAL:
                selected_idx = np.argmax(x.value)
                selected_model = model_list[selected_idx]
                
                print(f"   🎯 最优LP结果: {selected_model}")
                print(f"   📊 P2L系数: {p2l_coefficients[selected_idx]:.3f}")
                print(f"   🏆 期望胜率: {np.sum(bt_probs[selected_idx, :])/(n_models-1):.3f}")
                print(f"   💰 成本: ${costs[selected_idx]:.4f}/1k")
                print(f"   ⏱️ 响应时间: {response_times[selected_idx]:.1f}s")
                
                return selected_model
            else:
                print(f"   ⚠️ 最优LP求解失败，使用简单LP")
                return self._simple_lp_optimization(p2l_coefficients, model_list, model_configs, budget)
                
        except ImportError:
            print(f"   ⚠️ cvxpy未安装，使用简单优化")
            return self._simple_lp_optimization(p2l_coefficients, model_list, model_configs, budget)
        except Exception as e:
            print(f"   ❌ 最优LP优化失败: {e}")
            return self._simple_lp_optimization(p2l_coefficients, model_list, model_configs, budget)