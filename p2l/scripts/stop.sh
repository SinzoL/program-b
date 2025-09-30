#!/bin/bash

# P2L项目停止脚本

echo "⏹️  停止P2L智能路由系统..."

# 停止后端服务
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo "✅ 后端服务已停止"
    fi
    rm -f .backend.pid
fi

# 停止前端服务
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo "✅ 前端服务已停止"
    fi
    rm -f .frontend.pid
fi

# 清理其他相关进程
pkill -f "python.*backend_service.py" 2>/dev/null || true
pkill -f "node.*vite" 2>/dev/null || true

echo "🎯 所有服务已停止"