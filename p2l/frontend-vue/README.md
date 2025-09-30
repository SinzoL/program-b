# P2L 前端界面

P2L智能路由系统的Vue.js前端界面，提供直观的模型推荐和对话功能。

## 功能特性

- 🎨 **现代化UI**: 基于Vue 3 + Vite构建的响应式界面
- 🧠 **智能推荐**: 可视化展示P2L模型推荐结果
- 💬 **实时对话**: 支持与推荐模型进行实时对话
- 📊 **性能监控**: 显示响应时间、成本等关键指标
- 🎯 **优先级选择**: 支持性能、成本、速度等不同优化策略

## 技术栈

- **框架**: Vue 3
- **构建工具**: Vite
- **路由**: Vue Router
- **状态管理**: Pinia
- **UI组件**: 自定义组件
- **HTTP客户端**: Fetch API

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产版本

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── components/          # 组件目录
│   │   └── ModelCard.vue   # 模型卡片组件
│   ├── views/              # 页面目录
│   │   └── Home.vue        # 主页面
│   ├── stores/             # 状态管理
│   │   └── p2l.js         # P2L状态store
│   ├── router/             # 路由配置
│   │   └── index.js       # 路由定义
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── index.html             # HTML模板
├── package.json           # 项目配置
├── vite.config.js         # Vite配置
└── README.md             # 说明文档
```

## 配置说明

### API地址配置

在 `src/stores/p2l.js` 中配置后端API地址：

```javascript
const API_BASE = 'http://localhost:8080'
```

### 开发环境配置

在 `vite.config.js` 中配置开发服务器：

```javascript
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    host: true
  }
})
```

## 主要组件

### ModelCard.vue
模型推荐卡片组件，显示：
- 模型名称和提供商
- 推荐分数和理由
- 成本和响应时间
- 模型优势特点

### Home.vue
主页面组件，包含：
- 问题输入区域
- 优先级选择器
- 推荐结果展示
- 对话界面

## 状态管理

使用Pinia进行状态管理，主要状态包括：
- `currentPrompt`: 当前输入的问题
- `priority`: 选择的优先级模式
- `analysis`: P2L分析结果
- `conversation`: 对话历史
- `loading`: 加载状态

## 开发指南

### 添加新组件

1. 在 `src/components/` 目录下创建组件文件
2. 在需要的地方导入并使用
3. 遵循Vue 3 Composition API规范

### 修改样式

项目使用原生CSS，样式文件直接写在组件的 `<style>` 标签中。

### API调用

所有API调用都封装在Pinia store中，使用统一的错误处理。

## 部署

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
    }
}
```

## 故障排除

### 常见问题

1. **API连接失败**: 检查后端服务是否启动
2. **CORS错误**: 确认后端CORS配置正确
3. **构建失败**: 检查Node.js版本是否兼容

### 开发调试

使用浏览器开发者工具进行调试：
- Console: 查看错误日志
- Network: 检查API请求
- Vue DevTools: 调试Vue组件状态

## 许可证

MIT License