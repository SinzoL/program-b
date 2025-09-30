#!/bin/bash

# P2L项目一键安装脚本
# 适用于 macOS (Apple Silicon) 和 Linux

set -e

echo "🚀 开始安装P2L智能路由系统..."

# 检查Python版本
echo "📋 检查Python环境..."
PYTHON_CMD="python3.10"
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ 需要Python 3.10+，请先安装："
    echo "   macOS: brew install python@3.10"
    echo "   Ubuntu: sudo apt install python3.10 python3.10-venv"
    exit 1
fi

# 检查Node.js
echo "📋 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "❌ 需要Node.js 16+，请先安装："
    echo "   macOS: brew install node"
    echo "   Ubuntu: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
    exit 1
fi

# 创建Python虚拟环境
echo "🐍 创建Python虚拟环境..."
if [ ! -d ".env" ]; then
    $PYTHON_CMD -m venv .env
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .env/bin/activate

# 确保pip可用
echo "📦 确保pip可用..."
if ! python -m pip --version &> /dev/null; then
    echo "🔧 安装pip到虚拟环境..."
    python -m ensurepip --upgrade
fi

# 安装Python依赖
echo "📦 安装Python依赖..."
python -m pip install --upgrade pip
python -m pip install -r serve_requirements.txt

# 安装前端依赖
echo "🌐 安装前端依赖..."
cd frontend-vue
npm install --no-audit --no-fund
cd ..

# 下载P2L模型
echo "🧠 下载P2L模型..."
mkdir -p models
python -c "
from huggingface_hub import snapshot_download
import os

model_name = 'lmarena-ai/p2l-135m-grk-01112025'
local_dir = 'models/p2l-0.5b-grk'

if not os.path.exists(local_dir):
    print(f'下载P2L模型: {model_name}')
    print('模型大小: ~958MB')
    snapshot_download(
        repo_id=model_name,
        local_dir=local_dir,
        local_dir_use_symlinks=False
    )
    print('✅ P2L模型下载完成')
else:
    print('✅ P2L模型已存在')
"

echo ""
echo "🎉 安装完成！"
echo ""
echo "📚 使用方法："
echo "   启动服务: ./scripts/start.sh"
echo "   停止服务: ./scripts/stop.sh"
echo ""
echo "🌐 访问地址："
echo "   前端界面: http://localhost:3000"
echo "   API文档: http://localhost:8080/docs"
echo ""