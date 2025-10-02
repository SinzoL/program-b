#!/bin/bash
# P2L Frontend 启动脚本

echo "🎨 启动P2L前端服务..."

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装Node.js 16+"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装，请先安装npm"
    exit 1
fi

# 检查Node.js版本
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js版本过低，需要16+，当前版本: $(node -v)"
    exit 1
fi

# 进入前端目录
cd "$(dirname "$0")"

# 检查package.json
if [ ! -f "package.json" ]; then
    echo "❌ 未找到package.json文件"
    exit 1
fi

# 安装依赖
echo "📦 检查并安装依赖..."
if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
    echo "🔄 安装npm依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
else
    echo "✅ 依赖已是最新"
fi

# 停止已有服务
echo "🛑 停止已有前端服务..."
pkill -f "vite.*--port 3000" 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true

# 等待端口释放
sleep 2

# 启动开发服务器
echo "🚀 启动前端开发服务器..."
npm run dev &

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ P2L前端服务启动成功！"
    echo "🌐 访问地址: http://localhost:3000"
    echo "📱 移动端访问: http://$(hostname -I | awk '{print $1}'):3000"
else
    echo "⚠️  服务可能还在启动中，请稍等片刻后访问 http://localhost:3000"
fi

echo ""
echo "🎯 使用说明:"
echo "  - 前端界面: http://localhost:3000"
echo "  - 确保后端服务在 http://localhost:8080 运行"
echo "  - 按 Ctrl+C 停止服务"