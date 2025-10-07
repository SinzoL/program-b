#!/bin/bash
# Backend启动脚本 - 统一版本

set -e

echo "🚀 启动P2L Backend服务..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未找到，请先安装Python3"
    exit 1
fi

# 检查当前目录
if [ ! -f "service.py" ]; then
    echo "❌ 请在backend目录下运行此脚本"
    exit 1
fi

# 检查依赖
echo "🔍 检查依赖..."
python3 -c "import fastapi, uvicorn, torch, transformers" 2>/dev/null || {
    echo "⚠️  缺少依赖，尝试安装..."
    pip3 install -r requirements.txt || {
        echo "❌ 依赖安装失败"
        exit 1
    }
}

# 检查配置文件
echo "🔍 检查配置文件..."
if [ ! -d "model_p2l" ]; then
    echo "❌ model_p2l 目录不存在"
    exit 1
fi

if [ ! -f "model_p2l/api_configs.py" ] || [ ! -f "model_p2l/model_configs.py" ]; then
    echo "❌ 配置文件缺失"
    exit 1
fi

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/model_p2l"

# 启动服务
echo "✅ 环境检查完成，启动服务..."
echo "📡 服务地址: http://localhost:8080"
echo "📋 API文档: http://localhost:8080/docs"
echo "❤️  健康检查: http://localhost:8080/health"
echo ""

# 使用P2L原生服务
python3 service_p2l_native.py