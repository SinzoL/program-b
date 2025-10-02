#!/bin/bash
# P2L 开发环境一键启动脚本

echo "🚀 P2L智能路由系统 - 开发环境启动"
echo "=================================="

# 检查系统环境
echo "🔍 检查系统环境..."

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python 3.8+"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装Node.js 16+"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装，请先安装npm"
    exit 1
fi

echo "✅ 系统环境检查通过"

# 检查配置文件
if [ ! -f "backend/api_config.env" ]; then
    echo "❌ 未找到API配置文件: backend/api_config.env"
    echo "💡 请先配置API密钥，参考README.md中的配置说明"
    exit 1
fi

echo "✅ 配置文件检查通过"

# 停止已有服务
echo "🛑 停止已有服务..."
pkill -f "main.py" 2>/dev/null || true
pkill -f "service.py" 2>/dev/null || true
pkill -f "vite.*--port 3000" 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true

sleep 3

# 检查端口占用
if lsof -i :8080 &> /dev/null; then
    echo "⚠️  端口8080被占用，尝试释放..."
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

if lsof -i :3000 &> /dev/null; then
    echo "⚠️  端口3000被占用，尝试释放..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# 创建日志目录
mkdir -p logs

# 启动后端服务
echo "🔧 启动后端服务..."
cd backend

# 检查Python依赖
echo "📦 检查后端依赖..."
python3 -c "import fastapi, uvicorn, torch, transformers, aiohttp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "🔄 安装后端依赖..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 后端依赖安装失败"
        exit 1
    fi
fi

# 启动后端
echo "🚀 启动后端服务 (端口8080)..."
chmod +x start.sh
./start.sh > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

cd ..

# 等待后端启动
echo "⏳ 等待后端服务启动..."
for i in {1..30}; do
    if curl -s http://localhost:8080/health > /dev/null; then
        echo "✅ 后端服务启动成功！"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ 后端服务启动超时"
        echo "📋 查看日志: tail -f logs/backend.log"
        exit 1
    fi
    sleep 2
done

# 启动前端服务
echo "🎨 启动前端服务..."
cd frontend

# 检查前端依赖
echo "📦 检查前端依赖..."
if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
    echo "🔄 安装前端依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 前端依赖安装失败"
        exit 1
    fi
fi

# 启动前端
echo "🚀 启动前端服务 (端口3000)..."
chmod +x start.sh
./start.sh > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# 等待前端启动
echo "⏳ 等待前端服务启动..."
for i in {1..20}; do
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ 前端服务启动成功！"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "⚠️  前端服务可能还在启动中..."
        break
    fi
    sleep 3
done

# 保存进程ID
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "🎉 P2L开发环境启动完成！"
echo "=================================="
echo "🎨 前端界面: http://localhost:3000"
echo "🔧 后端API:  http://localhost:8080"
echo "📚 API文档:  http://localhost:8080/docs"
echo "📋 健康检查: http://localhost:8080/health"
echo ""
echo "📊 服务状态:"
echo "  - 后端进程ID: $BACKEND_PID"
echo "  - 前端进程ID: $FRONTEND_PID"
echo ""
echo "📝 日志文件:"
echo "  - 后端日志: tail -f logs/backend.log"
echo "  - 前端日志: tail -f logs/frontend.log"
echo ""
echo "🛑 停止服务: ./stop-dev.sh"
echo "🔄 重启服务: ./stop-dev.sh && ./start-dev.sh"
echo ""
echo "💡 提示: 首次启动可能需要几分钟来下载依赖和初始化模型"

# 打开浏览器 (可选)
if command -v open &> /dev/null; then
    echo "🌐 正在打开浏览器..."
    sleep 3
    open http://localhost:3000
elif command -v xdg-open &> /dev/null; then
    echo "🌐 正在打开浏览器..."
    sleep 3
    xdg-open http://localhost:3000
fi