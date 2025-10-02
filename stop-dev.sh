#!/bin/bash
# P2L 开发环境停止脚本

echo "🛑 P2L智能路由系统 - 停止开发环境"
echo "=================================="

# 读取保存的进程ID
BACKEND_PID=""
FRONTEND_PID=""

if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
fi

# 停止后端服务
echo "🔧 停止后端服务..."
if [ ! -z "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
    echo "  - 停止后端进程: $BACKEND_PID"
    kill $BACKEND_PID
else
    echo "  - 通过进程名停止后端服务"
    pkill -f "main.py" 2>/dev/null || true
    pkill -f "service.py" 2>/dev/null || true
fi

# 停止前端服务
echo "🎨 停止前端服务..."
if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "  - 停止前端进程: $FRONTEND_PID"
    kill $FRONTEND_PID
else
    echo "  - 通过进程名停止前端服务"
    pkill -f "vite.*--port 3000" 2>/dev/null || true
    pkill -f "npm.*dev" 2>/dev/null || true
fi

# 强制清理端口
echo "🧹 清理端口占用..."
if lsof -i :8080 &> /dev/null; then
    echo "  - 强制释放端口8080"
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
fi

if lsof -i :3000 &> /dev/null; then
    echo "  - 强制释放端口3000"
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
fi

# 等待进程完全停止
sleep 3

# 清理进程ID文件
rm -f .backend.pid .frontend.pid

# 检查服务状态
echo "🔍 检查服务状态..."
if ! curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ 后端服务已停止"
else
    echo "⚠️  后端服务可能仍在运行"
fi

if ! curl -s http://localhost:3000 > /dev/null; then
    echo "✅ 前端服务已停止"
else
    echo "⚠️  前端服务可能仍在运行"
fi

echo ""
echo "🎯 所有服务已停止"
echo "🚀 重新启动: ./start-dev.sh"
echo ""

# 显示剩余的相关进程
REMAINING_PROCESSES=$(ps aux | grep -E "(main\.py|service\.py|vite.*3000|npm.*dev)" | grep -v grep | wc -l)
if [ $REMAINING_PROCESSES -gt 0 ]; then
    echo "⚠️  发现残留进程:"
    ps aux | grep -E "(main\.py|service\.py|vite.*3000|npm.*dev)" | grep -v grep
    echo ""
    echo "💡 如需强制清理，请运行:"
    echo "   pkill -f 'main.py|service.py|vite.*3000|npm.*dev'"
fi