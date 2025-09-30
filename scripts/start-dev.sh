#!/bin/bash

# P2L开发环境启动脚本

echo "🚀 启动P2L智能路由系统 - 开发环境"

# 检查是否在项目根目录
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 设置环境变量
export P2L_ENV=development

# 启动后端服务
echo "📡 启动后端服务..."
cd backend
if [ ! -d "venv" ]; then
    echo "🔧 创建Python虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# 后台启动后端
python start.py &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

cd ..

# 启动前端服务
echo "🎨 启动前端服务..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "🔧 安装前端依赖..."
    npm install
fi

# 后台启动前端
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"

cd ..

# 保存PID到文件
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "🎉 P2L系统启动完成！"
echo "🌐 前端地址: http://localhost:3000"
echo "📡 后端地址: http://localhost:8080"
echo "📚 API文档: http://localhost:8080/docs"
echo ""
echo "💡 使用 './scripts/stop-dev.sh' 停止服务"
echo "📝 查看日志: tail -f backend/logs/*.log"

# 等待用户输入停止
echo "按 Ctrl+C 停止所有服务..."
trap 'kill $BACKEND_PID $FRONTEND_PID; rm -f .backend.pid .frontend.pid; echo "🛑 服务已停止"; exit' INT
wait