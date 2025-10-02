#!/bin/bash
# P2L Backend Service 启动脚本

echo "🚀 启动P2L统一后端服务..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import fastapi, uvicorn, torch, transformers, aiohttp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少必要依赖，请运行: pip install -r requirements.txt"
    exit 1
fi

# 检查环境配置
if [ ! -f "api_config.env" ]; then
    echo "❌ 未找到API配置文件: api_config.env"
    exit 1
fi

# 停止已有服务
echo "🛑 停止已有服务..."
pkill -f "main.py" 2>/dev/null || true
pkill -f "service.py" 2>/dev/null || true

# 等待端口释放
sleep 2

# 启动服务
echo "🚀 启动统一后端服务..."
cd "$(dirname "$0")"
python3 main.py

echo "✅ P2L后端服务已启动"
echo "🌐 健康检查: curl http://localhost:8080/health"
echo "📊 API文档: http://localhost:8080/docs"