# P2L 核心模块

P2L (Prompt-to-LLM) 核心模块包含了智能路由系统的所有核心功能，包括模型训练、评估、后端服务和前端界面。

## 📁 目录结构

```
p2l/
├── backend_service.py          # 🔥 后端API服务
├── serve_requirements.txt      # 后端Python依赖
├── frontend-vue/               # 🎨 前端Vue界面
│   ├── src/                    # Vue源码
│   │   ├── components/         # Vue组件
│   │   ├── views/              # 页面视图
│   │   ├── stores/             # 状态管理
│   │   └── router/             # 路由配置
│   ├── package.json            # 前端依赖
│   ├── vite.config.js          # Vite配置
│   └── index.html              # HTML模板
├── model.py                    # P2L模型定义
├── train.py                    # 训练脚本
├── eval.py                     # 评估脚本
├── dataset.py                  # 数据集处理
├── auto_eval_utils.py          # 自动评估工具
├── auto_evals.py               # 自动评估脚本
└── endpoint.py                 # API端点定义
```

## 🚀 快速启动

### 启动完整服务

#### 1. 启动后端服务

```bash
cd p2l
pip install -r serve_requirements.txt
python backend_service.py
```

服务将在 http://localhost:8080 启动，提供：
- 🌐 Web界面: http://localhost:8080
- 📚 API文档: http://localhost:8080/docs
- 🔍 健康检查: http://localhost:8080/health

#### 2. 启动前端开发服务器 (可选)

如果需要前端热重载开发：

```bash
cd p2l/frontend-vue
npm install
npm run dev
```

前端开发服务器将在 http://localhost:3000 启动

## 🧠 P2L模型训练

### 训练新模型

```bash
cd p2l
python train.py --config ../training_configs/your_config.yaml
```

### 支持的训练配置

- `Qwen2.5-1.5B-full-train.yaml`: Qwen 1.5B全量训练
- `Qwen2.5-3B-full-train.yaml`: Qwen 3B全量训练
- `Qwen2.5-7B-full-train.yaml`: Qwen 7B全量训练
- `Llama3.1-8B-full-train.yaml`: Llama 8B全量训练

### 训练参数说明

```yaml
model_name: "Qwen2.5-1.5B"
base_model: "Qwen/Qwen2.5-1.5B-Instruct"
output_dir: "./models/p2l-1.5b"
num_train_epochs: 3
learning_rate: 2e-5
batch_size: 8
```

## 📊 模型评估

### 评估训练好的模型

```bash
cd p2l
python eval.py --model_path ../models/p2l-1.5b
```

### 自动评估

```bash
cd p2l
python auto_evals.py --model_path ../models/p2l-1.5b
```

## 🔧 后端服务配置

### 主要功能

- **智能模型推荐**: 基于任务特征推荐最适合的LLM
- **多模型支持**: 支持9+个主流LLM模型
- **优化策略**: 性能、成本、速度等多维度优化
- **RESTful API**: 完整的HTTP API接口

### 配置模型

在 `backend_service.py` 中的 `_load_model_configs()` 方法中配置支持的模型：

```python
"new-model": {
    "provider": "provider_name",
    "cost_per_1k": 0.01,
    "avg_response_time": 2.0,
    "strengths": ["特长1", "特长2"],
    "quality_score": 0.85
}
```

### API端点

- `POST /api/p2l/analyze`: P2L智能分析
- `POST /api/llm/generate`: LLM生成调用
- `GET /api/models`: 获取支持的模型列表
- `GET /health`: 健康检查

## 🎨 前端界面

### 技术栈

- **框架**: Vue 3 + Composition API
- **构建工具**: Vite
- **路由**: Vue Router
- **状态管理**: Pinia
- **样式**: 原生CSS

### 主要组件

- **ModelCard.vue**: 模型推荐卡片
- **Home.vue**: 主页面
- **p2l.js**: P2L状态管理

### 开发命令

```bash
cd p2l/frontend-vue

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 🔄 数据处理

### 数据集处理

```bash
cd p2l
python dataset.py --input_file your_data.json --output_dir ./processed_data
```

### 支持的数据格式

```json
{
  "prompt": "用户输入的提示词",
  "task_type": "编程",
  "language": "中文",
  "complexity": "中等",
  "recommended_model": "gpt-4o"
}
```

## 🛠️ 开发指南

### 添加新的任务类型

在 `backend_service.py` 的 `analyze_task()` 方法中添加识别规则：

```python
elif any(word in prompt_lower for word in ["new_task", "新任务"]):
    task_type = "新任务类型"
```

### 自定义评分算法

修改 `calculate_model_scores()` 方法中的评分逻辑：

```python
def calculate_model_scores(self, task_analysis: Dict, priority: str) -> List[Dict]:
    # 自定义评分逻辑
    for model_name, config in self.model_configs.items():
        # 计算分数
        score = custom_scoring_function(task_analysis, config, priority)
```

### 扩展前端功能

1. 在 `src/components/` 中添加新组件
2. 在 `src/views/` 中添加新页面
3. 在 `src/stores/p2l.js` 中添加新的状态管理
4. 在 `src/router/index.js` 中配置路由

## 📈 性能优化

### 模型加载优化

- 使用模型缓存避免重复加载
- 支持模型懒加载
- GPU内存管理

### API性能优化

- 异步处理提高并发
- 请求缓存减少重复计算
- 响应压缩减少传输时间

## 🐛 故障排除

### 常见问题

1. **模型加载失败**
   ```bash
   # 检查模型目录
   ls -la ../models/
   
   # 检查模型文件完整性
   python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('../models/p2l-1.5b')"
   ```

2. **前端连接失败**
   ```bash
   # 检查后端服务状态
   curl http://localhost:8080/health
   
   # 检查CORS配置
   # 在backend_service.py中确认前端地址在allow_origins中
   ```

3. **训练过程中断**
   ```bash
   # 检查GPU内存
   nvidia-smi
   
   # 检查训练日志
   tail -f training.log
   ```

### 日志查看

```bash
# 后端服务日志
python backend_service.py 2>&1 | tee backend.log

# 训练日志
python train.py --config config.yaml 2>&1 | tee training.log
```

## 📄 许可证

本模块采用 MIT 许可证。