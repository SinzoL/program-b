#!/bin/bash

# P2L项目一键启动脚本

set -e

echo "🚀 启动P2L智能路由系统..."

# 检查虚拟环境
if [ ! -d ".env" ]; then
    echo "❌ 请先运行安装脚本: ./scripts/install.sh"
    exit 1
fi

# 激活虚拟环境
source .env/bin/activate

# 检查模型
if [ ! -d "models/p2l-0.5b-grk" ]; then
    echo "❌ P2L模型未找到，请先运行安装脚本"
    exit 1
fi

# 启动后端服务
echo "🔧 启动后端服务..."
python backend_service.py &
BACKEND_PID=$!

# 等待后端启动
sleep 5

# 启动前端服务
echo "🌐 启动前端服务..."
cd frontend-vue
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ 服务启动成功！"
echo ""
echo "🌐 访问地址："
echo "   前端界面: http://localhost:3000"
echo "   API文档: http://localhost:8080/docs"
echo ""
echo "⏹️  停止服务: ./scripts/stop.sh"
echo ""

# 保存PID
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# 等待用户中断
wait