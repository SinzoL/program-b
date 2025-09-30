# P2L 智能路由系统

P2L (Prompt-to-LLM) 是一个智能的大语言模型路由系统，能够根据用户的提示词自动推荐最适合的LLM模型，并提供统一的调用接口。

## 🌟 项目特色

- 🧠 **智能推荐**: 基于任务特征、语言类型、复杂度等因素智能推荐最适合的LLM模型
- 📊 **多模型支持**: 集成OpenAI、Anthropic、Google、阿里巴巴等多家厂商的主流模型
- ⚡ **灵活优化**: 支持性能、成本、速度等不同维度的优化策略
- 🎨 **现代化界面**: 基于Vue 3的响应式Web界面
- 🔧 **易于扩展**: 模块化设计，方便添加新模型和功能

## 🏗️ 项目结构

```
program-b/
├── README.md                       # 项目主文档
├── .env.example                    # 环境变量配置示例
├── .gitignore                      # Git忽略文件
├── docker-compose.yml              # Docker编排配置
├── p2l/                            # 🧠 P2L核心模块
│   ├── backend_service.py          # 🔥 后端API服务
│   ├── serve_requirements.txt      # 后端依赖
│   ├── frontend-vue/               # 🎨 前端Vue界面
│   │   ├── src/                    # Vue源码
│   │   ├── package.json            # 前端依赖
│   │   └── ...                     # 其他前端文件
│   ├── model.py                    # P2L模型定义
│   ├── train.py                    # 训练脚本
│   ├── eval.py                     # 评估脚本
│   └── ...                         # 其他核心文件
├── backend/                        # 🔄 独立后端服务 (可选)
├── frontend/                       # 🔄 独立前端服务 (可选)
├── models/                         # 🤖 预训练模型存储
├── route/                          # 🛣️ 路由相关代码
├── scripts/                        # 🛠️ 部署和管理脚本
└── training_configs/               # ⚙️ 训练配置文件
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- CUDA (可选，用于GPU加速)

### 方式一：使用p2l目录中的服务 (推荐)

#### 1. 启动后端服务

```bash
cd p2l
pip install -r serve_requirements.txt
python backend_service.py
```

后端服务将在 http://localhost:8080 启动

#### 2. 启动前端界面

```bash
cd p2l/frontend-vue
npm install
npm run dev
```

前端界面将在 http://localhost:3000 启动

### 方式二：使用独立的前后端服务

#### 1. 启动独立后端

```bash
cd backend
pip install -r requirements.txt
python start.py
```

#### 2. 启动独立前端

```bash
cd frontend
npm install
npm run dev
```

### 方式三：一键启动脚本

```bash
# 开发环境一键启动
./scripts/start-dev.sh

# 停止服务
./scripts/stop-dev.sh
```

### 方式四：Docker部署

```bash
# Docker一键部署
./scripts/deploy-docker.sh

# 或使用docker-compose
docker-compose up -d
```

## 📋 支持的模型

### OpenAI
- **gpt-4o**: 最新的GPT-4模型，适合复杂推理和编程任务
- **gpt-4o-mini**: 轻量版GPT-4，成本更低，响应更快

### Anthropic
- **claude-3-5-sonnet-20241022**: Claude 3.5 Sonnet，擅长创意写作和分析
- **claude-3-5-haiku-20241022**: Claude 3.5 Haiku，快速响应的轻量模型

### Google
- **gemini-1.5-pro-002**: Gemini Pro，支持多模态和长文本处理
- **gemini-1.5-flash-002**: Gemini Flash，快速处理的轻量版本

### 其他厂商
- **qwen2.5-72b-instruct**: 阿里巴巴通义千问，中文理解能力强
- **llama-3.1-70b-instruct**: Meta Llama 3.1，开源大模型
- **deepseek-v3**: DeepSeek V3，擅长数学和逻辑推理

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

## 🔧 配置说明

### 环境变量配置

复制 `.env.example` 为 `.env` 并根据需要修改：

```bash
# 环境设置
P2L_ENV=development

# 服务配置
P2L_HOST=0.0.0.0
P2L_PORT=8080

# 模型配置
P2L_MODELS_DIR=./models
```

### 后端配置

在 `p2l/backend_service.py` 中可以配置：

- 支持的模型列表和参数
- CORS允许的前端地址
- 服务端口和主机地址

### 前端配置

在 `p2l/frontend-vue/src/stores/p2l.js` 中可以配置：

- 后端API地址
- 默认优先级设置
- UI显示选项

## 🛠️ 开发指南

### P2L模型训练

```bash
cd p2l
python train.py --config ../training_configs/your_config.yaml
```

### 模型评估

```bash
cd p2l
python eval.py --model_path ../models/your_model
```

### 添加新的LLM模型

1. 在 `p2l/backend_service.py` 的 `_load_model_configs()` 方法中添加模型配置
2. 实现对应的API调用逻辑
3. 更新前端的模型显示组件

### 自定义评分算法

在 `P2LBackendService.calculate_model_scores()` 方法中修改评分逻辑。

## 🚀 部署指南

### 开发环境

使用提供的脚本快速启动开发环境：

```bash
./scripts/start-dev.sh
```

### 生产环境

1. **使用Docker**: 推荐使用Docker进行生产部署
2. **传统部署**: 使用gunicorn + nginx部署后端，构建前端静态文件
3. **云服务**: 可部署到AWS、阿里云等云平台

### Docker部署

```bash
# 一键Docker部署
./scripts/deploy-docker.sh

# 或手动使用docker-compose
docker-compose up -d
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