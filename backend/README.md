# P2L Backend Service

统一的P2L后端服务，整合了所有功能模块，提供清晰的项目结构和配置管理。

## 项目结构

```
p2l/backend/
├── __init__.py          # 包初始化文件
├── config.py            # 统一配置文件
├── service.py           # 主服务文件
├── main.py              # 启动入口
├── llm_client.py        # LLM API客户端
├── llm_handler.py       # LLM处理模块
├── p2l_engine.py        # P2L推理引擎
├── task_analyzer.py     # 任务分析模块
├── model_scorer.py      # 模型评分模块
├── requirements.txt     # 依赖列表
└── README.md           # 说明文档
```

## 配置管理

所有配置都集中在 `config.py` 文件中：

- **API配置**: API密钥、端点、超时设置
- **模型配置**: 模型参数、价格、性能指标
- **任务分析配置**: 任务权重、复杂度阈值
- **P2L引擎配置**: 推理参数、语义分析设置
- **服务配置**: 服务器、CORS、日志设置

## 启动服务

### 方法1: 直接启动
```bash
cd p2l/backend
python main.py
```

### 方法2: 模块启动
```bash
cd p2l
python -m backend.main
```

### 方法3: 使用uvicorn
```bash
cd p2l/backend
uvicorn service:create_app --host 0.0.0.0 --port 8080 --reload
```

## API接口

### 主要接口
- `POST /api/p2l/analyze` - P2L智能分析
- `POST /api/llm/generate` - LLM响应生成
- `POST /api/p2l/inference` - P2L推理
- `GET /api/models` - 获取模型列表
- `GET /health` - 健康检查

### 兼容性接口
- `POST /analyze` - P2L分析（兼容）
- `POST /generate` - LLM生成（兼容）
- `GET /models` - 模型列表（兼容）

## 配置文件

### 外置配置文件
配置文件已迁移到项目根目录的Python文件中：

#### API配置文件 (`../api_configs.py`)
包含所有API密钥和端点配置：

```python
API_CONFIGS = {
    "api_keys": {
        "openai": "your_openai_key",
        "anthropic": "your_claude_key",
        # ... 其他API密钥
    },
    "base_urls": {
        "openai": "https://api.openai.com/v1",
        # ... 其他API端点
    }
}
```

#### 模型配置文件 (`../model_configs.py`)
包含所有模型的详细配置：

```python
MODEL_CONFIGS = {
    "gpt-4o": {
        "provider": "openai",
        "cost_per_1k": 0.015,
        "quality_score": 0.94,
        "strengths": ["编程", "数学", "分析"],
        # ... 其他模型参数
    },
    # ... 42个模型配置
}
```

### 配置文件优势
- **集中管理**: 所有配置在项目根目录
- **类型安全**: Python字典格式，支持IDE智能提示
- **易于维护**: 结构化配置，便于批量修改
- **版本控制**: 可以跟踪配置变更历史
DASHSCOPE_API_KEY=your_dashscope_key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_key
```

## 模型配置

支持的模型及其配置：

### OpenAI模型
- `gpt-4o`: 高性能模型，适合复杂任务
- `gpt-4o-mini`: 快速响应，成本效益高

### Claude模型
- `claude-3-5-sonnet-20241022`: 创意写作专长
- `claude-3-7-sonnet-20250219`: 全能型模型

### Gemini模型
- `gemini-1.5-pro`: 多模态支持，长文本处理

### DeepSeek模型
- `deepseek-chat`: 对话优化
- `deepseek-coder`: 编程专用

### 千问模型
- `qwen2.5-72b-instruct`: 中文理解强
- `qwen-plus`: 复杂推理
- `qwen-turbo`: 快速响应

## 功能特性

### 1. 智能模型推荐
- P2L语义分析
- 任务类型识别
- 复杂度评估
- 语言检测
- 百分制评分系统

### 2. 统一API调用
- 多提供商支持
- 自动重试机制
- 错误处理
- 成本计算

### 3. 配置化管理
- 集中配置管理
- 环境变量支持
- 热重载配置
- 参数验证

### 4. 性能优化
- 异步处理
- 连接池管理
- 缓存机制
- 资源监控

## 开发指南

### 添加新模型
1. 在 `config.py` 的 `MODEL_CONFIGS` 中添加模型配置
2. 在 `llm_client.py` 中添加对应的API调用方法
3. 更新模型列表和路由

### 修改评分算法
1. 编辑 `model_scorer.py` 中的评分方法
2. 调整 `config.py` 中的任务权重配置
3. 测试评分结果

### 自定义任务分析
1. 修改 `task_analyzer.py` 中的分析逻辑
2. 更新 `config.py` 中的关键词配置
3. 验证分析准确性

## 故障排除

### 常见问题

1. **模型加载失败**
   - 检查模型路径配置
   - 确认模型文件完整性
   - 验证设备兼容性

2. **API调用失败**
   - 检查API密钥配置
   - 验证网络连接
   - 查看错误日志

3. **服务启动失败**
   - 检查端口占用
   - 验证依赖安装
   - 查看启动日志

### 日志查看
服务日志包含详细的调试信息，可以帮助定位问题：
- 模型加载状态
- API调用详情
- 错误堆栈信息
- 性能指标

## 部署建议

### 生产环境
- 使用 `gunicorn` 或 `uvicorn` 作为WSGI服务器
- 配置反向代理（Nginx）
- 设置环境变量
- 启用日志轮转
- 配置监控告警

### 开发环境
- 使用 `--reload` 参数启用热重载
- 设置详细日志级别
- 配置开发用API密钥
- 启用调试模式

## 版本信息

- **版本**: 3.0.0
- **Python**: 3.9+
- **FastAPI**: 0.104+
- **PyTorch**: 2.0+