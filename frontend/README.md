# P2L 前端界面

P2L智能路由系统的Vue.js前端界面，提供直观的模型推荐和对话功能。

## 🌟 功能特性

- 🎨 **现代化UI**: 基于Vue 3 + Vite + Element Plus构建的响应式界面
- 🧠 **智能推荐**: 可视化展示P2L模型推荐结果和评分
- 💬 **实时对话**: 支持与推荐模型进行实时对话交互
- 📊 **性能监控**: 显示响应时间、Token使用量、成本等关键指标
- 🎯 **优先级选择**: 支持性能、成本、速度、平衡等不同优化策略
- 🔄 **系统状态**: 实时监控后端服务健康状态
- 📱 **响应式设计**: 适配桌面和移动设备
- 🎭 **示例对话**: 内置示例问题，快速体验功能

## 🛠️ 技术栈

- **框架**: Vue 3.5.22 (Composition API)
- **构建工具**: Vite 6.3.6
- **UI组件库**: Element Plus 2.11.4
- **图标库**: @element-plus/icons-vue 2.3.2
- **路由**: Vue Router 4.5.1
- **状态管理**: Pinia 2.3.1
- **HTTP客户端**: Axios 1.12.2
- **自动导入**: unplugin-auto-import + unplugin-vue-components

## 🚀 快速开始

### 环境要求

- Node.js >= 16.0.0
- npm >= 8.0.0

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问: http://localhost:3000

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产版本

```bash
npm run preview
```

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/              # 组件目录
│   │   ├── AnalysisResult.vue  # P2L分析结果展示
│   │   ├── ChatHistory.vue     # 对话历史记录
│   │   ├── ExampleDialog.vue   # 示例对话弹窗
│   │   ├── InputPanel.vue      # 输入面板组件
│   │   ├── ModelCard.vue       # 模型推荐卡片
│   │   ├── ModelSelector.vue   # 模型选择器
│   │   └── SystemStatus.vue    # 系统状态组件
│   ├── views/                  # 页面目录
│   │   └── Home.vue           # 主页面
│   ├── stores/                # 状态管理
│   │   └── p2l.js            # P2L状态store
│   ├── router/                # 路由配置
│   │   └── index.js          # 路由定义
│   ├── App.vue               # 根组件
│   └── main.js               # 入口文件
├── index.html                # HTML模板
├── package.json              # 项目配置
├── vite.config.js           # Vite配置
├── Dockerfile               # Docker配置
├── nginx.conf               # Nginx配置
└── README.md                # 说明文档
```

## ⚙️ 配置说明

### API代理配置

开发环境通过Vite代理转发API请求到后端：

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,
      secure: false
    }
  }
}
```

### 后端API地址

在 `src/stores/p2l.js` 中配置：

```javascript
const api = axios.create({
  baseURL: 'http://localhost:8080',
  timeout: 60000
})
```

### Element Plus自动导入

配置了Element Plus组件和API的自动导入：

```javascript
// vite.config.js
AutoImport({
  resolvers: [ElementPlusResolver()],
  imports: ['vue', 'vue-router', 'pinia']
}),
Components({
  resolvers: [ElementPlusResolver()]
})
```

## 🧩 主要组件

### AnalysisResult.vue
P2L分析结果展示组件：
- 任务分析详情
- 模型推荐列表
- 推荐理由说明

### ModelCard.vue
模型推荐卡片组件：
- 模型名称和提供商
- 推荐分数和排名
- 成本和响应时间预估
- 模型特点和优势

### InputPanel.vue
输入面板组件：
- 问题输入区域
- 优先级选择器
- 提交和清空按钮

### ChatHistory.vue
对话历史组件：
- 对话记录展示
- 消息时间戳
- 清空历史功能

### SystemStatus.vue
系统状态监控：
- 后端服务状态
- 可用模型数量
- 连接状态指示

## 📊 状态管理

使用Pinia进行状态管理，主要状态包括：

```javascript
state: () => ({
  // 系统状态
  backendHealth: false,
  loading: false,
  configVersion: '2.0.1',
  
  // P2L分析
  currentAnalysis: null,
  recommendations: [],
  
  // 对话管理
  conversations: [],
  currentConversation: null,
  
  // 用户配置
  selectedPriority: 'balanced',
  enabledModels: []
})
```

## 🎨 开发指南

### 添加新组件

1. 在 `src/components/` 目录下创建Vue组件
2. 使用Composition API编写组件逻辑
3. 利用Element Plus组件库构建UI
4. 在需要的地方导入使用

### 样式规范

- 使用Element Plus主题系统
- 组件样式写在 `<style scoped>` 中
- 遵循响应式设计原则

### API调用规范

所有API调用封装在Pinia store中：

```javascript
// 示例API调用
async analyzePrompt(prompt, priority) {
  this.loading = true
  try {
    const response = await api.post('/api/p2l/analyze', {
      prompt,
      priority
    })
    this.currentAnalysis = response.data
  } catch (error) {
    console.error('分析失败:', error)
  } finally {
    this.loading = false
  }
}
```

## 🐳 部署

### Docker部署

```bash
# 构建镜像
docker build -t p2l-frontend .

# 运行容器
docker run -p 3000:80 p2l-frontend
```

### 静态部署

```bash
npm run build
# 将 dist/ 目录部署到静态服务器
```

### Nginx配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 🔧 故障排除

### 常见问题

1. **API连接失败**
   - 检查后端服务是否在 http://localhost:8080 运行
   - 确认防火墙设置允许端口访问

2. **CORS错误**
   - 确认后端CORS配置包含前端域名
   - 检查代理配置是否正确

3. **构建失败**
   - 检查Node.js版本 (需要 >= 16.0.0)
   - 清除缓存: `npm cache clean --force`
   - 重新安装依赖: `rm -rf node_modules && npm install`

4. **Element Plus组件未自动导入**
   - 检查 `vite.config.js` 配置
   - 重启开发服务器

### 开发调试

- **Vue DevTools**: 调试Vue组件和Pinia状态
- **浏览器控制台**: 查看错误日志和API请求
- **Network面板**: 检查API请求和响应
- **Vite HMR**: 热更新功能加速开发

## 📈 性能优化

- 组件懒加载
- Element Plus按需导入
- Vite构建优化
- 图片资源压缩
- 代码分割

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -m 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 提交Pull Request

## 📄 许可证

MIT License

---

**项目状态**: 开发中 (95%完成度)
**最后更新**: 2025年10月2日