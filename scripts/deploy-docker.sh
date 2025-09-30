#!/bin/bash

# P2L Docker部署脚本

echo "🐳 使用Docker部署P2L智能路由系统"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查是否在项目根目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 健康检查
echo "🏥 执行健康检查..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ 后端服务健康"
else
    echo "❌ 后端服务异常"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ 前端服务健康"
else
    echo "❌ 前端服务异常"
fi

echo ""
echo "🎉 P2L系统部署完成！"
echo "🌐 前端地址: http://localhost:3000"
echo "📡 后端地址: http://localhost:8080"
echo "📚 API文档: http://localhost:8080/docs"
echo ""
echo "💡 查看日志: docker-compose logs -f"
echo "💡 停止服务: docker-compose down"