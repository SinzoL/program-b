#!/bin/bash

# P2L开发环境停止脚本

echo "🛑 停止P2L智能路由系统..."

# 停止后端服务
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo "✅ 后端服务已停止 (PID: $BACKEND_PID)"
    else
        echo "⚠️  后端服务进程不存在"
    fi
    rm -f .backend.pid
fi

# 停止前端服务
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo "✅ 前端服务已停止 (PID: $FRONTEND_PID)"
    else
        echo "⚠️  前端服务进程不存在"
    fi
    rm -f .frontend.pid
fi

# 清理可能残留的进程
pkill -f "python.*backend_service"
pkill -f "npm.*run.*dev"
pkill -f "vite"

echo "🎉 所有服务已停止"