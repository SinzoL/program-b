# P2L 智能路由系统

P2L (Prompt-to-LLM) 是一个智能的大语言模型路由系统，能够根据用户的提示词自动推荐最适合的LLM模型，并提供统一的调用接口。

## 🌟 项目特色

- 🧠 **智能推荐**: 基于P2L神经网络模型进行语义分析，智能推荐最适合的LLM模型
- 📊 **多模型支持**: 集成OpenAI、Anthropic、Google、阿里千问、DeepSeek等10+主流模型
- ⚡ **灵活优化**: 支持性能、成本、速度等不同维度的优化策略
- 🎨 **现代化界面**: 基于Vue 3 + Element Plus的响应式Web界面
- 🔧 **易于扩展**: 模块化设计，方便添加新模型和功能
- 🚀 **生产就绪**: 统一的后端服务，支持Docker部署

## 🏗️ 项目结构

```
program-b/
├── README.md                       # 项目主文档
├── .gitignore                      # Git忽略文件
├── docker-compose.yml              # Docker编排配置
├── start-dev.sh                    # 🚀 一键启动开发环境
├── stop-dev.sh                     # 🛑 一键停止开发环境
├── backend/                        # 🔥 统一后端服务
│   ├── main.py                     # 服务入口点
│   ├── service.py                  # 主服务文件
│   ├── config.py                   # 配置管理
│   ├── llm_client.py               # LLM客户端
│   ├── p2l_engine.py               # P2L推理引擎
│   ├── task_analyzer.py            # 任务分析器
│   ├── model_scorer.py             # 模型评分器
│   ├── llm_handler.py              # LLM处理器
│   ├── api_config.env              # 🔑 API密钥配置
│   ├── requirements.txt            # 后端依赖
│   └── start.sh                    # 后端启动脚本
├── frontend/                       # 🎨 Vue前端界面
│   ├── src/                        # Vue源码
│   │   ├── components/             # Vue组件
│   │   ├── stores/                 # Pinia状态管理
│   │   └── views/                  # 页面视图
│   ├── package.json                # 前端依赖
│   ├── vite.config.js              # Vite配置
│   └── start.sh                    # 前端启动脚本
├── p2l/                            # 🧠 P2L核心系统
│   ├── serve_requirements.txt      # 后端依赖
│   ├── train_requirements.txt      # 训练依赖
│   ├── models/                     # 🤖 P2L模型存储
│   │   ├── demo_model_list.json    # 演示模型配置
│   │   └── p2l-0.5b-grk/           # P2L神经网络模型
│   ├── p2l/                        # 🧠 P2L核心算法
│   │   ├── model.py                # P2L模型定义
│   │   ├── train.py                # 训练脚本
│   │   ├── eval.py                 # 评估脚本
│   │   ├── dataset.py              # 数据集处理
│   │   └── p2l_inference.py        # P2L推理接口
│   ├── route/                      # 🛣️ 路由相关功能
│   │   ├── routers.py              # 路由器实现
│   │   ├── cost_optimizers.py      # 成本优化器
│   │   └── openai_server.py        # OpenAI兼容服务
│   └── scripts/                    # 🛠️ 管理脚本
│       ├── install.sh              # 安装脚本
│       ├── start.sh                # 启动脚本
│       └── stop.sh                 # 停止脚本
└── scripts/                        # 🚀 部署脚本 (已废弃)
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- CUDA (可选，用于GPU加速)
- 至少8GB内存（推荐16GB）

### 方式一：一键启动脚本 (推荐)

```bash
# 🚀 一键启动前后端服务
./start-dev.sh

# 🛑 停止所有服务
./stop-dev.sh
```

启动后访问：
- 🎨 **前端界面**: http://localhost:3000
- 🔧 **后端API**: http://localhost:8080
- 📚 **API文档**: http://localhost:8080/docs

### 方式二：手动启动

#### 1. 配置API密钥

```bash
# 编辑配置文件，添加你的API密钥
vim backend/api_config.env
```

#### 2. 启动后端服务

```bash
cd backend
./start.sh
```

后端服务将在 http://localhost:8080 启动

#### 3. 启动前端界面

```bash
cd frontend
./start.sh
```

前端界面将在 http://localhost:3000 启动

### 方式三：Docker部署

```bash
# Docker一键部署
docker-compose up -d
```

## 🔧 API密钥配置

在 `backend/api_config.env` 文件中配置各厂商的API密钥：

```bash
# OpenAI
OPENAI_API_KEY=sk-your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
ANTHROPIC_BASE_URL=https://api.anthropic.com

# 阿里千问
DASHSCOPE_API_KEY=sk-your-dashscope-key

# DeepSeek
DEEPSEEK_API_KEY=sk-your-deepseek-key

# Google Gemini
GOOGLE_API_KEY=your-google-api-key
```

**首次使用请确保配置至少一个API密钥！**

## 📋 支持的模型

### OpenAI 🤖
- **gpt-4o**: 最新的GPT-4模型，适合复杂推理和编程任务
- **gpt-4o-mini**: 轻量版GPT-4，成本更低，响应更快

### Anthropic 🧠
- **claude-3-5-sonnet-20241022**: Claude 3.5 Sonnet，擅长创意写作和分析
- **claude-3-5-haiku-20241022**: Claude 3.5 Haiku，快速响应的轻量模型

### Google 🔍
- **gemini-1.5-pro-002**: Gemini Pro，支持多模态和长文本处理
- **gemini-1.5-flash-002**: Gemini Flash，快速处理的轻量版本

### 阿里千问 🇨🇳
- **qwen2.5-72b-instruct**: 通义千问2.5，中文理解能力强，编程能力优秀
- **qwen-plus**: 高质量模型，适合复杂推理任务
- **qwen-turbo**: 快速响应模型，成本低廉

### DeepSeek 🧮
- **deepseek-chat**: DeepSeek对话模型，擅长中文对话和快速响应
- **deepseek-coder**: DeepSeek编程模型，专门优化编程任务

### 其他模型 🌐
- **llama-3.1-70b-instruct**: Meta Llama 3.1，开源大模型

## 🎯 核心功能

### 智能模型推荐

P2L系统会分析用户的提示词，考虑以下因素：

- **任务类型**: 编程、创意写作、翻译、数学、分析等
- **语言类型**: 中文、英文等不同语言的处理能力
- **复杂度**: 简单、中等、复杂任务的匹配度
- **用户优先级**: 性能、成本、速度的权衡

### 优化策略

- **性能优先**: 选择质量分数最高的模型
- **成本优先**: 选择单位成本最低的模型
- **速度优先**: 选择响应时间最快的模型
- **平衡模式**: 综合考虑各项指标

### API接口

提供完整的RESTful API：

- `POST /api/p2l/analyze`: P2L智能分析
- `POST /api/llm/generate`: LLM生成调用
- `GET /api/models`: 获取支持的模型列表
- `GET /health`: 健康检查

## 📊 使用示例

### 1. 编程任务

**输入**: "写一个JavaScript函数将下划线转换为驼峰命名"

**P2L推荐**: gpt-4o (擅长编程任务，代码质量高)

### 2. 创意写作

**输入**: "写一首关于春天的诗"

**P2L推荐**: claude-3-5-sonnet (擅长创意写作和文学创作)

### 3. 中文任务

**输入**: "解释一下量子计算的基本原理"

**P2L推荐**: qwen2.5-72b-instruct (中文理解能力强)

## 📈 开发进度

### ✅ 已完成功能

#### 后端核心 (100%)
- ✅ **统一后端服务**: 基于FastAPI的高性能后端
- ✅ **P2L智能推理**: 基于神经网络的语义分析和模型推荐
- ✅ **多模型集成**: 支持10+主流LLM模型
- ✅ **API密钥管理**: 统一的配置文件管理
- ✅ **任务分析器**: 智能识别任务类型、复杂度、语言
- ✅ **模型评分器**: 多维度模型评分算法
- ✅ **成本计算**: 精确的token使用量和费用计算
- ✅ **错误处理**: 完善的异常处理和日志记录

#### 前端界面 (95%)
- ✅ **Vue 3 + Element Plus**: 现代化响应式界面
- ✅ **智能推荐展示**: 直观的模型推荐结果
- ✅ **实时对话**: 支持多轮对话和历史记录
- ✅ **模型选择器**: 手动选择和切换模型
- ✅ **系统状态监控**: 实时显示系统健康状态
- 🔄 **用户设置**: 个性化配置选项 (90%)

#### API接口 (100%)
- ✅ **RESTful API**: 完整的API接口设计
- ✅ **P2L分析接口**: `/api/p2l/analyze`
- ✅ **LLM生成接口**: `/api/llm/generate`
- ✅ **模型列表接口**: `/api/models`
- ✅ **健康检查接口**: `/health`
- ✅ **CORS支持**: 跨域请求支持

### 🔄 进行中功能

#### 高级功能 (70%)
- 🔄 **模型缓存**: 提升响应速度 (80%)
- 🔄 **请求限流**: 防止API滥用 (60%)
- 🔄 **用户认证**: 多用户支持 (50%)
- 🔄 **长对话**: 支持长上下文 (30%)

#### 部署优化 (80%)
- 🔄 **Docker容器化**: 完整的Docker支持 (90%)
- 🔄 **生产环境配置**: 性能优化配置 (70%)
- 🔄 **监控和日志**: 完善的监控体系 (60%)
- 🔄 **模型参数**: 目前可能不够准确 (30%)

### 📋 待开发功能

#### 扩展功能
- ⏳ **插件系统**: 支持自定义插件
- ⏳ **A/B测试**: 模型效果对比
- ⏳ **数据分析**: 使用统计和分析
- ⏳ **API网关**: 统一的API管理

#### 模型优化
- ⏳ **P2L模型微调**: 针对特定领域优化
- ⏳ **在线学习**: 根据用户反馈优化推荐
- ⏳ **多模态支持**: 图像、音频等多模态输入

## 🔧 配置说明

### API密钥配置

在 `p2l/api_config.env` 文件中配置各厂商的API密钥：

```bash
# OpenAI
OPENAI_API_KEY=sk-your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1

# Anthropic  
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
ANTHROPIC_BASE_URL=https://api.anthropic.com

# 阿里千问
DASHSCOPE_API_KEY=sk-your-dashscope-key

# DeepSeek
DEEPSEEK_API_KEY=sk-your-deepseek-key

# Google Gemini
GOOGLE_API_KEY=your-google-api-key
```

### 后端配置

在 `backend/config.py` 中可以配置：

- 支持的模型列表和参数
- 服务端口和主机地址
- P2L模型路径和设备设置
- 日志级别和输出格式

### 前端配置

在 `frontend/src/stores/p2l.js` 中可以配置：

- 后端API地址
- 默认优先级设置
- UI显示选项和主题

## 🛠️ 开发指南

### P2L模型训练

```bash
cd p2l/p2l
python train.py --config your_config.yaml
```

### 模型评估

```bash
cd p2l/p2l
python eval.py --model_path ../models/p2l-0.5b-grk
```

### 添加新的LLM模型

1. 在 `backend/config.py` 的模型配置中添加新模型
2. 在 `backend/llm_client.py` 中实现对应的API调用逻辑
3. 更新 `backend/model_scorer.py` 中的评分规则
4. 在前端 `frontend/src/components/ModelCard.vue` 中添加显示支持

### 自定义评分算法

在 `backend/model_scorer.py` 的 `ModelScorer.calculate_scores()` 方法中修改评分逻辑。

### 开发环境设置

```bash
# 方式一：一键启动 (推荐)
./start-dev.sh

# 方式二：手动启动
# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install

# 启动开发服务
cd backend && ./start.sh &
cd frontend && ./start.sh
```

## 🚀 部署指南

### 开发环境

使用提供的脚本快速启动开发环境：

```bash
./start-dev.sh
```

### 生产环境部署

#### 方式一：Docker部署 (推荐)

```bash
# 使用docker-compose
docker-compose up -d
```

#### 方式二：传统部署

1. **后端部署**:
```bash
cd backend
pip install -r requirements.txt
gunicorn -w 4 -k uvicorn.workers.UvicornWorker service:app --bind 0.0.0.0:8080
```

2. **前端部署**:
```bash
cd frontend
npm install
npm run build
# 将dist目录部署到nginx或其他静态文件服务器
```

#### 方式三：云服务部署

- **阿里云**: 支持ECS、容器服务ACK
- **AWS**: 支持EC2、EKS、Lambda
- **腾讯云**: 支持CVM、TKE
- **华为云**: 支持ECS、CCE

### 环境变量配置

生产环境建议使用环境变量而非配置文件：

```bash
export OPENAI_API_KEY=sk-your-key
export ANTHROPIC_API_KEY=sk-ant-your-key
export DASHSCOPE_API_KEY=sk-your-key
export P2L_ENV=production
export P2L_HOST=0.0.0.0
export P2L_PORT=8080
```

## 📈 性能优化

- **模型缓存**: 缓存已加载的模型避免重复加载
- **请求缓存**: 缓存相似请求的分析结果
- **异步处理**: 使用异步IO提高并发性能
- **负载均衡**: 多实例部署分散请求压力

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和研究人员！

## 📞 联系我们

如有问题或建议，请通过以下方式联系：

- 提交Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**P2L智能路由系统 - 让AI模型选择更智能！** 🚀