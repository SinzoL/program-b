#!/bin/bash
# Docker部署问题诊断脚本

echo "🔍 P2L Docker部署诊断"
echo "=" * 50

# 检查Docker服务状态
echo "📊 检查Docker服务状态..."
if command -v docker &> /dev/null; then
    echo "✅ Docker已安装"
    
    # 检查容器状态
    echo ""
    echo "📋 容器状态:"
    docker ps -a --filter "name=p2l"
    
    echo ""
    echo "🏥 健康检查状态:"
    docker inspect p2l-backend --format='{{.State.Health.Status}}' 2>/dev/null || echo "❌ backend容器不存在或无健康检查"
    docker inspect p2l-frontend --format='{{.State.Health.Status}}' 2>/dev/null || echo "❌ frontend容器不存在或无健康检查"
    
    # 检查端口占用
    echo ""
    echo "🔌 端口占用检查:"
    echo "端口8080 (backend):"
    lsof -i :8080 2>/dev/null || echo "  端口8080未被占用"
    echo "端口3000 (frontend):"
    lsof -i :3000 2>/dev/null || echo "  端口3000未被占用"
    
    # 检查后端日志
    echo ""
    echo "📝 后端容器日志 (最近20行):"
    docker logs --tail=20 p2l-backend 2>/dev/null || echo "❌ 无法获取backend日志"
    
    # 检查前端日志
    echo ""
    echo "📝 前端容器日志 (最近10行):"
    docker logs --tail=10 p2l-frontend 2>/dev/null || echo "❌ 无法获取frontend日志"
    
    # 检查网络连接
    echo ""
    echo "🌐 网络连接测试:"
    echo "测试后端健康检查:"
    curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health 2>/dev/null || echo "❌ 后端服务无响应"
    echo ""
    echo "测试前端服务:"
    curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "❌ 前端服务无响应"
    
else
    echo "❌ Docker未安装或不在PATH中"
fi

# 检查配置文件
echo ""
echo "📁 配置文件检查:"
if [ -f "backend/api_config.env" ]; then
    echo "✅ API配置文件存在"
    echo "配置文件内容 (隐藏敏感信息):"
    grep -v "^#" backend/api_config.env | sed 's/=.*/=***/' 2>/dev/null || echo "配置文件为空或格式错误"
else
    echo "❌ API配置文件不存在: backend/api_config.env"
fi

if [ -f "constants.py" ]; then
    echo "✅ 常量配置文件存在"
    echo "默认模型配置:"
    grep "DEFAULT_MODEL" constants.py 2>/dev/null || echo "❌ 未找到DEFAULT_MODEL配置"
else
    echo "❌ 常量配置文件不存在: constants.py"
fi

# 检查模型目录
echo ""
echo "📂 模型目录检查:"
if [ -d "models" ]; then
    echo "✅ models目录存在"
    echo "目录内容:"
    ls -la models/ 2>/dev/null || echo "models目录为空"
else
    echo "❌ models目录不存在"
fi

echo ""
echo "🔧 建议的解决步骤:"
echo "1. 检查后端容器日志: docker logs -f p2l-backend"
echo "2. 检查API配置文件: cat backend/api_config.env"
echo "3. 重新部署: ./deploy.sh"
echo "4. 如果模型下载失败，手动运行: python3 ensure_model.py"