# P2L 后端系统 - FastAPI 技术文档

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**P2L智能路由后端服务 - 基于Bradley-Terry系数的多策略路由引擎**

</div>

## 🎯 后端概述

P2L后端系统基于FastAPI构建，核心实现了**P2L神经网络推理**和**多策略智能路由**功能。通过Bradley-Terry系数计算和多种优化算法，为20+大语言模型提供智能选择和成本优化服务。

### 🌟 核心特色

- **🧠 P2L神经网络**: 135M参数模型，Bradley-Terry配对比较算法
- **🎯 多策略路由**: 4种路由模式 × 3种优化算法 = 12种路由策略
- **💰 成本优化**: 线性规划、严格约束、博弈论优化
- **⚡ 异步架构**: FastAPI + asyncio，高并发处理
- **🌐 统一API**: 20+模型统一接口，智能错误处理

## 🏗️ 技术架构

### 📋 核心技术栈

| 层级 | 组件 | 技术栈 | 核心功能 | 算法实现 |
|------|------|--------|----------|----------|
| 🌐 **API层** | Web服务 | FastAPI + Uvicorn | RESTful接口、自动文档、CORS支持 | 异步处理、自动验证 |
| 🎯 **路由层** | 智能选择 | P2L Router + 多策略 | 性能优先、成本优先、速度优先、平衡模式 | 线性规划、博弈论优化 |
| 🧠 **推理层** | AI引擎 | P2L Engine + Bradley-Terry | P2L神经网络、系数计算、语义分析 | 135M参数模型、配对比较 |
| 🤖 **模型层** | LLM集成 | 统一客户端 | OpenAI、Anthropic、Google、千问、DeepSeek | 统一接口、智能重试 |

### 🎯 路由策略矩阵

| 优化目标 | 算法类型 | 适用场景 | 性能特点 |
|----------|----------|----------|----------|
| **性能优先** | Bradley-Terry评分 | 追求最佳回答质量 | 高准确度、中等成本 |
| **成本优先** | 线性规划优化 | 预算敏感应用 | 低成本、可接受质量 |
| **速度优先** | 延迟最小化 | 实时交互场景 | 快响应、中等质量 |
| **平衡模式** | 多目标优化 | 通用场景 | 综合最优、推荐使用 |

### 🧠 P2L神经网络架构

| 组件 | 参数规模 | 功能描述 | 技术细节 |
|------|----------|----------|----------|
| **输入层** | - | Prompt编码 | 文本向量化、语义提取 |
| **隐藏层** | 135M | 特征学习 | Transformer架构、注意力机制 |
| **输出层** | 20+ | 模型评分 | Bradley-Terry系数、概率分布 |
| **优化器** | - | 训练优化 | Adam优化器、学习率调度 |

### 📁 项目结构

```
backend/
├── 🚀 main.py                      # 启动入口
├── ⚙️ config.py                    # 统一配置管理
├── 🧠 service_p2l_native.py        # P2L原生服务 (核心)
│
├── 🎯 p2l_router.py                # P2L智能路由器 (核心路由策略)
├── 📊 p2l_model_scorer.py          # P2L模型评分器
├── 🧠 p2l_engine.py                # P2L推理引擎
├── 🌐 unified_client.py            # 统一LLM客户端
│
├── 🔑 model_p2l/                   # P2L核心模块
│   ├── 📋 api_configs.py           # API配置管理
│   ├── 🤖 model_configs.py         # 模型配置定义
│   ├── 🧠 p2l_core.py              # P2L核心算法
│   └── 🛠️ p2l_tools.py             # P2L工具函数
│
└── 📦 requirements.txt             # Python依赖
```

## 🎯 核心路由策略实现

### 1. 🧠 P2L Bradley-Terry 系数计算

#### P2L神经网络推理
```python
# p2l_engine.py - 实际的Bradley-Terry系数计算
class P2LEngine:
    def get_bradley_terry_coefficients(self, prompt: str, model_list: List[str]) -> np.ndarray:
        """获取P2L模型的Bradley-Terry系数"""
        
        # 1. 提示词编码
        embedding = self.encode_prompt(prompt)
        
        # 2. 神经网络推理
        with torch.no_grad():
            coefficients = self.model(**inputs)
        
        # 3. Bradley-Terry系数计算
        # P(i beats j) = exp(θ_i) / (exp(θ_i) + exp(θ_j))
        bt_coefficients = self._compute_bradley_terry_coefficient(embedding, model_configs)
        
        return bt_coefficients
```

#### 模拟系数生成 (降级模式)
```python
# p2l_model_scorer.py - 实际的模拟系数实现
def _generate_mock_coefficients(self) -> np.ndarray:
    """基于模型质量的模拟Bradley-Terry系数"""
    
    # 预设模型质量评分
    model_quality_scores = {
        "claude-3-5-sonnet-20241022": 0.85,  # 顶级模型
        "gpt-4o-2024-08-06": 0.80,          # 顶级模型
        "claude-3-opus-20240229": 0.78,      # 高质量模型
        "gpt-4-turbo-2024-04-09": 0.75,     # 高质量模型
        # ... 更多模型配置
    }
    
    for model_name in self.model_list:
        config = self.model_configs[model_name]
        
        # 基础质量评分
        base_quality = model_quality_scores.get(model_name, 0.5)
        
        # 成本效益调整
        cost_efficiency = max(0.1, min(2.0, 0.01 / config["cost_per_1k"]))
        cost_factor = min(1.2, 1.0 + (cost_efficiency - 1.0) * 0.1)
        
        # 速度效益调整
        speed_efficiency = max(0.1, min(2.0, 3.0 / config["avg_response_time"]))
        speed_factor = min(1.2, 1.0 + (speed_efficiency - 1.0) * 0.1)
        
        # 最终Bradley-Terry系数
        coef = max(0.1, min(2.0, base_quality * cost_factor * speed_factor * 2.0))
        coefficients.append(coef)
    
    return np.array(coefficients)
```

### 2. 🎯 四种路由模式实现

#### 模式映射策略
```python
# p2l_router.py - 实际的模式映射实现
class P2LRouter:
    def __init__(self):
        # 模式映射到优化策略
        self.mode_mapping = {
            'performance': 'max_score',      # 性能优先：选择最高分
            'cost': 'strict',                # 成本优先：严格成本约束
            'speed': 'speed_weighted',       # 速度优先：速度权重调整
            'balanced': 'simple-lp'          # 平衡模式：简单线性规划
        }
```

#### 🏆 性能优先模式 (Performance)
```python
def _select_max_score(self, model_list: List[str], scores: np.ndarray) -> str:
    """性能优先：直接选择P2L评分最高的模型"""
    max_idx = np.argmax(scores)
    return model_list[max_idx]

# 权重配置：几乎完全依赖P2L系数
weights = {'p2l': 0.95, 'cost': 0.025, 'speed': 0.025}
```

#### ⚡ 速度优先模式 (Speed)
```python
def _select_speed_weighted(self, model_list: List[str], p2l_scores: np.ndarray, response_times: np.ndarray) -> str:
    """速度优先：结合P2L分数和响应时间"""
    
    # 将响应时间转换为速度分数（时间越短分数越高）
    max_time = np.max(response_times)
    speed_scores = (max_time - response_times) / max_time
    
    # 结合P2L分数和速度分数
    p2l_weight = 0.6
    speed_weight = 0.4
    
    # 标准化P2L分数到0-1
    normalized_p2l = (p2l_scores - np.min(p2l_scores)) / (np.max(p2l_scores) - np.min(p2l_scores) + 1e-8)
    
    combined_scores = p2l_weight * normalized_p2l + speed_weight * speed_scores
    
    max_idx = np.argmax(combined_scores)
    return model_list[max_idx]

# 权重配置：几乎完全依赖响应速度
weights = {'p2l': 0.1, 'cost': 0.05, 'speed': 0.85}
```

#### 💰 成本优先模式 (Cost)
```python
# 权重配置：几乎完全依赖成本效益
weights = {'p2l': 0.1, 'cost': 0.85, 'speed': 0.05}

# 使用严格成本约束优化器
def _strict_cost_optimization(self, p2l_coefficients: np.ndarray, model_list: List[str], model_configs: Dict, budget: float) -> str:
    """严格成本优化：在预算约束内选择P2L评分最高的模型"""
    
    # 过滤符合预算的模型
    affordable_models = []
    for i, model in enumerate(model_list):
        cost = model_configs[model]["cost_per_1k"]
        if cost <= budget:
            affordable_models.append((model, p2l_coefficients[i], cost))
    
    if not affordable_models:
        # 选择最便宜的模型
        costs = [model_configs[model]["cost_per_1k"] for model in model_list]
        min_cost_idx = np.argmin(costs)
        return model_list[min_cost_idx]
    
    # 在符合预算的模型中选择P2L评分最高的
    best_model = max(affordable_models, key=lambda x: x[1])
    return best_model[0]
```

#### ⚖️ 平衡模式 (Balanced)
```python
# 权重配置：相对均衡但仍有侧重
weights = {'p2l': 0.5, 'cost': 0.25, 'speed': 0.25}

# 使用简单线性规划优化
def _simple_lp_optimization(self, p2l_coefficients: np.ndarray, model_list: List[str], model_configs: Dict, budget: Optional[float] = None) -> str:
    """简单线性规划优化：使用cvxpy进行成本效益优化"""
    
    import cvxpy as cp
    
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
    
    # 求解
    problem = cp.Problem(objective, constraints)
    problem.solve()
    
    if problem.status == cp.OPTIMAL:
        selected_idx = np.argmax(x.value)
        return model_list[selected_idx]
```

### 3. 🔧 三种成本优化算法

#### 📊 严格成本约束 (StrictCostOptimizer)
```python
class StrictCostOptimizer(BaseCostOptimizer):
    """严格成本约束优化器"""
    
    @staticmethod
    def select_model(cost: Optional[float], model_list: List[str], model_costs: np.ndarray, model_scores: np.ndarray) -> str:
        if cost is None:
            return StrictCostOptimizer.select_max_score_model(model_list, model_scores)

        best_model: Optional[str] = None
        best_score = -float("inf")

        for model, model_cost, model_score in zip(model_list, model_costs, model_scores):
            if model_cost > cost:
                continue  # 超预算，跳过
            elif model_score > best_score:
                best_model = model
                best_score = model_score

        if best_model is None:
            raise UnfulfillableException(f"预算 {cost} 无法满足")

        return best_model
```

#### 🧮 简单线性规划 (SimpleLPCostOptimizer)
```python
class SimpleLPCostOptimizer(BaseCostOptimizer):
    """简单线性规划优化器"""
    
    @staticmethod
    def select_model(cost: Optional[float], model_list: List[str], model_costs: np.ndarray, model_scores: np.ndarray) -> str:
        import cvxpy as cp
        
        if cost is None:
            return StrictCostOptimizer.select_max_score_model(model_list, model_scores)

        p = cp.Variable(len(model_costs))

        # 线性规划问题
        prob = cp.Problem(
            cp.Maximize(cp.sum(model_scores @ p)),           # 最大化评分
            [model_costs.T @ p <= cost,                      # 成本约束
             cp.sum(p) == 1,                                 # 概率和为1
             p >= 0]                                         # 非负约束
        )

        status = prob.solve()

        if status < 0.0:
            raise UnfulfillableException(f"预算 {cost} 无法满足")

        # 概率采样选择
        ps = np.clip(p.value, a_min=0.0, a_max=1.0)
        ps = ps / ps.sum()

        return np.random.choice(model_list, p=ps)
```

#### 🎯 最优线性规划 (OptimalLPCostOptimizer)
```python
class OptimalLPCostOptimizer(BaseCostOptimizer):
    """最优线性规划优化器（Bradley-Terry博弈论）"""
    
    @staticmethod
    def select_model(cost: Optional[float], model_list: List[str], model_costs: np.ndarray, model_scores: np.ndarray, 
                    opponent_scores: Optional[np.ndarray] = None, opponent_distribution: Optional[np.ndarray] = None) -> str:
        
        # 构建Bradley-Terry胜率矩阵
        W = OptimalLPCostOptimizer._construct_W(model_scores, opponent_scores)
        Wq = W @ opponent_distribution

        p = cp.Variable(len(model_costs))

        # 博弈论优化问题
        prob = cp.Problem(
            cp.Maximize(p @ Wq),                             # 最大化期望胜率
            [model_costs.T @ p <= cost,                      # 成本约束
             cp.sum(p) == 1,                                 # 概率和为1
             p >= 0]                                         # 非负约束
        )

        status = prob.solve()
        
        # 概率采样选择
        ps = np.clip(p.value, a_min=0.0, a_max=1.0)
        ps = ps / ps.sum()

        return np.random.choice(model_list, p=ps)

    @staticmethod
    def _construct_W(router_model_scores: np.ndarray, opponent_model_scores: np.ndarray) -> np.ndarray:
        """构建Bradley-Terry胜率矩阵"""
        num_rows = router_model_scores.shape[-1]
        num_cols = opponent_model_scores.shape[-1]

        chosen = np.tile(router_model_scores, (num_cols, 1)).T
        rejected = np.tile(opponent_model_scores, (num_rows, 1))

        diff_matrix = chosen - rejected
        W = expit(diff_matrix)  # sigmoid函数，计算胜率

        return W
```

### 4. 🎲 采样权重配置

#### 模型采样权重 (实际配置)
```python
# p2l_router.py - 实际的采样权重配置
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
    # ... 更多模型配置
}
```

#### 对手分布设置
```python
def setup_opponent_distribution(self, model_list: List[str], p2l_coefficients: np.ndarray):
    """设置对手分布，用于博弈论优化"""
    
    # 构建对手分布权重
    opponent_weights = []
    for model in model_list:
        weight = self.SAMPLING_WEIGHTS.get(model, 1)  # 默认权重为1
        opponent_weights.append(weight)
    
    # 标准化为概率分布
    opponent_weights = np.array(opponent_weights, dtype=float)
    self.opponent_distribution = opponent_weights / opponent_weights.sum()
    self.opponent_scores = p2l_coefficients.copy()
```

## 🚀 API接口

### 核心接口

- `POST /api/p2l/analyze` - P2L智能分析 (核心路由接口)
- `POST /api/llm/generate` - LLM响应生成
- `GET /api/p2l/model-info` - P2L模型信息
- `GET /api/models` - 获取模型列表
- `GET /health` - 健康检查

### P2L智能分析请求示例

```python
import requests

# P2L智能分析 - 展示所有路由模式
response = requests.post("http://localhost:8080/api/p2l/analyze", json={
    "prompt": "写一个Python快速排序函数",
    "priority": "performance",        # 性能优先模式
    "enabled_models": ["gpt-4o-2024-08-06", "claude-3-5-sonnet-20241022"],
    "budget": 0.05                   # 预算约束 $0.05/1k tokens
})

# 成本优先模式
response = requests.post("http://localhost:8080/api/p2l/analyze", json={
    "prompt": "简单的问答任务",
    "priority": "cost",              # 成本优先模式
    "budget": 0.001                  # 严格预算约束
})

# 速度优先模式
response = requests.post("http://localhost:8080/api/p2l/analyze", json={
    "prompt": "快速响应需求",
    "priority": "speed"              # 速度优先模式
})

# 平衡模式 (默认)
response = requests.post("http://localhost:8080/api/p2l/analyze", json={
    "prompt": "综合考虑的任务",
    "priority": "balanced"           # 平衡模式
})
```

### 响应格式

```json
{
  "model_ranking": [
    {
      "model": "claude-3-5-sonnet-20241022",
      "score": 0.8945,
      "p2l_coefficient": 0.8234,
      "provider": "anthropic",
      "cost_per_1k": 0.015,
      "avg_response_time": 2.1
    }
  ],
  "recommended_model": "claude-3-5-sonnet-20241022",
  "confidence": 0.8945,
  "reasoning": "P2L模型高度推荐；性能表现最优；检测到编程相关任务，推荐具有强编程能力的模型",
  "processing_time": 0.156,
  "p2l_native": true,
  "routing_info": {
    "strategy": "max_score",
    "mode": "performance",
    "total_models": 20,
    "explanation": "性能优先模式：选择P2L评分最高的模型 claude-3-5-sonnet-20241022"
  }
}
```

## 🔧 配置管理

### 环境变量

```bash
# 服务配置
P2L_ENV=production
P2L_HOST=0.0.0.0
P2L_PORT=8080

# Python路径
PYTHONPATH=/app:/app/backend:/app/backend/model_p2l

# P2L模型配置
P2L_MODEL_PATH=/app/backend/model_p2l/models/p2l-135m-grk
P2L_DEVICE=cpu

# 日志级别
LOG_LEVEL=INFO
```

### 模型配置 (model_p2l/model_configs.py)

- **模型列表**: 所有支持的20+模型及其配置
- **成本信息**: 每个模型的调用成本 (cost_per_1k)
- **性能参数**: 响应时间、质量评分等
- **采样权重**: P2L路由器使用的模型权重


### 健康检查

```bash
# 检查服务状态
curl http://localhost:8080/health

# 检查P2L模型信息
curl http://localhost:8080/api/p2l/model-info
```

## 🎯 路由策略总结

### 🏆 12种路由策略组合

| 路由模式 | 优化算法 | 适用场景 | 权重配置 |
|---------|---------|---------|---------|
| **Performance** | Max Score | 质量要求高 | P2L:95%, Cost:2.5%, Speed:2.5% |
| **Performance** | Simple LP | 质量+预算 | P2L系数最大化 + 预算约束 |
| **Performance** | Optimal LP | 质量+博弈 | Bradley-Terry胜率最大化 |
| **Cost** | Strict | 严格预算 | 预算内P2L最高分 |
| **Cost** | Simple LP | 成本优化 | P2L:10%, Cost:85%, Speed:5% |
| **Cost** | Optimal LP | 成本+博弈 | 成本约束 + 胜率优化 |
| **Speed** | Speed Weighted | 响应速度 | P2L:10%, Cost:5%, Speed:85% |
| **Speed** | Simple LP | 速度+预算 | 速度权重 + 线性规划 |
| **Speed** | Optimal LP | 速度+博弈 | 时间惩罚 + 胜率优化 |
| **Balanced** | Simple LP | 综合平衡 | P2L:50%, Cost:25%, Speed:25% |
| **Balanced** | Optimal LP | 最优平衡 | 博弈论 + 多目标优化 |
| **Fallback** | Max Score | 降级模式 | P2L系数最高分 |

### 🎯 路由策略选择建议

- **🏆 高质量任务**: `performance` + `max_score` - 直接选择P2L评分最高
- **💰 成本敏感**: `cost` + `strict` - 严格预算约束内最优选择  
- **⚡ 实时响应**: `speed` + `speed_weighted` - 响应时间权重优化
- **⚖️ 日常使用**: `balanced` + `simple-lp` - 线性规划综合优化
- **🎲 高级优化**: `balanced` + `optimal-lp` - Bradley-Terry博弈论

### 🔧 技术难点解决

1. **P2L模型集成**: 异步加载 + 降级模式 + 模拟系数
2. **多策略路由**: 模式映射 + 权重配置 + 动态调整
3. **成本优化**: 线性规划 + 博弈论 + 约束求解
4. **性能优化**: 异步处理 + 缓存机制 + 批处理推理
5. **容错机制**: 降级策略 + 错误恢复 + 健康检查

这套P2L后端系统通过**多策略智能路由**和**Bradley-Terry系数优化**，为大语言模型选择提供了科学、高效、可配置的解决方案。