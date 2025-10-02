# P2L Backend Service - 项目结构说明

## 📁 统一后端架构

```
p2l/backend/
├── __init__.py              # 包初始化文件
├── main.py                  # 服务启动入口
├── service.py               # 主服务逻辑
├── config.py                # 统一配置管理
├── p2l_engine.py           # P2L推理引擎
├── task_analyzer.py        # 任务分析模块
├── model_scorer.py         # 模型评分模块
├── llm_handler.py          # LLM处理模块
├── llm_client.py           # LLM客户端
├── requirements.txt        # 依赖列表
├── start.sh               # 启动脚本
├── README.md              # 使用说明
└── PROJECT_STRUCTURE.md   # 项目结构说明
```

## 🔧 模块功能说明

### 1. 配置管理 (config.py)
- **功能**: 统一管理所有配置信息
- **包含**: 
  - 模型配置 (价格、速度、质量评分)
  - API配置 (密钥、端点、超时设置)
  - 服务配置 (CORS、日志、连接池)
  - 任务分析配置
  - 评分算法配置

### 2. P2L推理引擎 (p2l_engine.py)
- **功能**: P2L模型加载和语义分析
- **特性**:
  - 自动设备检测 (CUDA/MPS/CPU)
  - 语义特征提取
  - 复杂度和语言评分

### 3. 任务分析器 (task_analyzer.py)
- **功能**: 智能任务识别和分类
- **支持**:
  - 任务类型识别 (编程、创意写作、翻译、数学、分析)
  - 复杂度评估
  - 语言检测
  - 置信度计算

### 4. 模型评分器 (model_scorer.py)
- **功能**: 模型智能排序和推荐
- **算法**:
  - 基础质量分 (40分)
  - 任务匹配分 (25分)
  - 语言匹配分 (15分)
  - 优先级匹配分 (20分)
  - 总分100分制

### 5. LLM处理器 (llm_handler.py)
- **功能**: 统一LLM调用接口
- **支持**: 错误处理、重试机制、响应格式化

### 6. LLM客户端 (llm_client.py)
- **功能**: 多提供商API调用
- **支持**:
  - OpenAI (GPT-4o, GPT-4o-mini)
  - Anthropic (Claude-3.5-Sonnet, Claude-3-7-Sonnet)
  - Google (Gemini-1.5-Pro)
  - 阿里云 (Qwen2.5-72B, Qwen-Plus, Qwen-Turbo)
  - DeepSeek (DeepSeek-Chat, DeepSeek-Coder)

### 7. 主服务 (service.py)
- **功能**: FastAPI应用和路由管理
- **API端点**:
  - `GET /health` - 健康检查
  - `POST /api/p2l/analyze` - P2L智能分析
  - `POST /api/llm/generate` - LLM响应生成
  - `POST /api/p2l/inference` - P2L推理
  - `GET /api/models` - 获取模型列表

## 🚀 启动方式

### 方法1: 使用启动脚本
```bash
cd p2l/backend
./start.sh
```

### 方法2: 直接启动
```bash
cd p2l/backend
python3 main.py
```

### 方法3: 后台启动
```bash
cd p2l/backend
python3 main.py &
```

## 🔍 健康检查

```bash
curl http://localhost:8080/health
```

预期响应:
```json
{
  "status": "healthy",
  "p2l_models_loaded": 1,
  "llm_models_available": 10,
  "device": "mps",
  "p2l_available": true,
  "llm_client_available": true,
  "real_api_enabled": true
}
```

## 📊 API测试

### P2L智能分析
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"prompt":"测试推荐","priority":"balanced"}' \
  http://localhost:8080/api/p2l/analyze
```

### 获取模型列表
```bash
curl http://localhost:8080/api/models
```

## 🔧 配置文件

### API配置 (../api_config.env)
```env
# OpenAI
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxx
ANTHROPIC_BASE_URL=https://api.anthropic.com/v1

# 阿里云通义千问
DASHSCOPE_API_KEY=sk-xxx
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# DeepSeek
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Google Gemini
GOOGLE_API_KEY=xxx
GOOGLE_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

## 🎯 优势特性

1. **统一架构**: 所有功能模块集中在一个文件夹
2. **清晰依赖**: 使用绝对导入，避免相对导入问题
3. **配置分离**: 配置信息独立管理，便于维护
4. **模块化设计**: 功能模块分离，职责清晰
5. **易于部署**: 单一启动入口，简化部署流程
6. **完整文档**: 详细的使用说明和API文档

## 🔄 与前端集成

前端Vue应用无需修改，所有API接口保持兼容:
- `/api/p2l/analyze` - P2L分析接口
- `/api/llm/generate` - LLM调用接口
- `/api/models` - 模型列表接口

## 📝 日志输出

服务启动后会显示详细的日志信息:
- 模块加载状态
- 设备检测结果
- P2L模型加载情况
- API调用记录
- 错误信息和调试信息

## 🛠️ 故障排除

1. **导入错误**: 确保在backend目录下启动服务
2. **端口占用**: 使用 `pkill -f main.py` 停止已有服务
3. **依赖缺失**: 运行 `pip install -r requirements.txt`
4. **配置错误**: 检查 `../api_config.env` 文件是否存在
5. **模型加载失败**: 确保 `../models/` 目录下有P2L模型文件