# P2L Backend Service - 统一版本

## 概述

P2L Backend是一个统一的后端服务，整合了大模型API调用、P2L推理引擎和智能模型推荐功能。

## 功能特性

- 🤖 **多模型支持**: 支持OpenAI、Anthropic、Google、DeepSeek、阿里云等多个模型提供商
- 🧠 **P2L智能推理**: 基于神经网络的模型推荐和任务分析
- 🔄 **统一API接口**: 简化的RESTful API设计
- 🐳 **Docker支持**: 完整的容器化部署方案
- ⚡ **高性能**: 异步处理和连接池优化

## 项目结构

```
backend/
├── config.py              # 统一配置管理
├── service.py              # 主服务文件
├── unified_client.py       # 统一LLM客户端
├── p2l_engine.py          # P2L推理引擎
├── task_analyzer.py       # 任务分析器
├── model_scorer.py        # 模型评分器
├── main.py                # 启动入口
├── start.sh               # 启动脚本
├── requirements.txt       # 依赖文件
└── model_p2l/            # P2L核心模块
    ├── api_configs.py     # API配置
    ├── model_configs.py   # 模型配置
    ├── p2l_core.py       # P2L核心常量
    ├── p2l_inference.py  # P2L推理实现
    └── p2l_tools.py      # P2L工具
```

## 快速开始

### 本地运行

1. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

2. **启动服务**
```bash
./start.sh
# 或者
python3 service.py
```

3. **访问服务**
- 服务地址: http://localhost:8080
- API文档: http://localhost:8080/docs
- 健康检查: http://localhost:8080/health

### Docker部署

1. **构建镜像**
```bash
docker build -t p2l-backend .
```

2. **运行容器**
```bash
docker run -p 8080:8080 p2l-backend
```

3. **使用Docker Compose**
```bash
docker-compose up -d
```

## API接口

### 核心接口

- `POST /api/p2l/analyze` - P2L智能分析
- `POST /api/llm/generate` - LLM响应生成
- `POST /api/p2l/inference` - P2L推理
- `GET /api/models` - 获取模型列表
- `GET /health` - 健康检查

### 请求示例

```python
import requests

# P2L智能分析
response = requests.post("http://localhost:8080/api/p2l/analyze", json={
    "prompt": "写一个Python快速排序函数",
    "priority": "balanced"
})

# LLM响应生成
response = requests.post("http://localhost:8080/api/llm/generate", json={
    "model": "gpt-4o-mini-2024-07-18",
    "prompt": "Hello, how are you?",
    "max_tokens": 2000,
    "temperature": 0.7
})
```

## 配置说明

### API配置 (model_p2l/api_configs.py)

- **API密钥**: 配置各个模型提供商的API密钥
- **端点URL**: 配置API端点和中转服务
- **超时设置**: 配置请求超时参数
- **连接池**: 配置连接池参数

### 模型配置 (model_p2l/model_configs.py)

- **模型列表**: 所有支持的模型及其配置
- **成本信息**: 每个模型的调用成本
- **性能参数**: 响应时间、质量评分等
- **能力标签**: 模型擅长的任务类型

## 环境变量

```bash
# 服务配置
HOST=0.0.0.0
PORT=8080

# Python路径
PYTHONPATH=/app:/app/backend:/app/backend/model_p2l

# 日志级别
LOG_LEVEL=INFO
```

## 开发指南

### 添加新模型

1. 在 `model_configs.py` 中添加模型配置
2. 在 `api_configs.py` 中配置API密钥和端点
3. 在 `unified_client.py` 中添加调用逻辑（如需要）

### 自定义任务分析

1. 修改 `task_analyzer.py` 中的分析逻辑
2. 更新 `model_scorer.py` 中的评分算法
3. 调整 `api_configs.py` 中的任务权重配置

## 故障排除

### 常见问题

1. **模块导入失败**
   - 检查PYTHONPATH设置
   - 确认model_p2l目录存在

2. **API调用失败**
   - 检查API密钥配置
   - 验证网络连接
   - 查看错误日志

3. **P2L模型加载失败**
   - 检查models目录
   - 运行模型下载工具
   - 查看内存使用情况

### 日志查看

```bash
# 查看服务日志
docker logs p2l-backend

# 实时日志
docker logs -f p2l-backend
```

## 性能优化

- 使用连接池减少连接开销
- 异步处理提高并发性能
- 智能缓存减少重复计算
- 模型预加载加速响应

## 安全考虑

- API密钥安全存储
- 请求频率限制
- 输入验证和清理
- 错误信息脱敏

## 更新日志

### v3.0.0 (当前版本)
- 统一配置管理
- 简化模块结构
- 优化导入路径
- 完善Docker支持

## 许可证

MIT License

## 支持

如有问题，请提交Issue或联系开发团队。