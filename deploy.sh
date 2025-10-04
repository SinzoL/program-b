#!/bin/bash
# P2L 一键部署脚本 - 支持平滑升级

set -e

echo "🚀 P2L 项目部署"
echo "==============="

# 检查是否为升级模式
UPGRADE_MODE=false
if [ "$1" = "upgrade" ] || [ "$2" = "upgrade" ]; then
    UPGRADE_MODE=true
    echo "🔄 升级模式：将平滑更新现有服务"
fi

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查 Docker 权限
echo "🔐 检查 Docker 权限..."
if ! docker ps &> /dev/null; then
    echo "⚠️  Docker 权限不足，尝试修复..."
    
    # 检查当前用户是否在 docker 组中
    if ! groups $USER | grep -q docker; then
        echo "📝 将用户 $USER 添加到 docker 组..."
        sudo usermod -aG docker $USER
        echo "✅ 用户已添加到 docker 组"
        echo ""
        echo "🔄 请执行以下命令之一来刷新权限："
        echo "   方法1: newgrp docker"
        echo "   方法2: 退出并重新登录 SSH"
        echo "   方法3: 使用 sudo 运行此脚本: sudo ./deploy.sh"
        echo ""
        read -p "现在刷新权限吗？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🔄 刷新权限中..."
            exec newgrp docker
        else
            echo "⏸️  请手动刷新权限后重新运行脚本"
            exit 1
        fi
    else
        echo "❌ 用户已在 docker 组中，但仍无权限。请尝试："
        echo "   1. 重新登录 SSH"
        echo "   2. 或使用 sudo 运行: sudo ./deploy.sh"
        exit 1
    fi
fi

echo "✅ Docker 权限检查通过"

# 创建模型目录并预下载模型
echo "📁 准备模型目录..."
mkdir -p models
echo "✅ 模型目录已准备"

# 预下载模型（在容器启动前）
echo "🚀 预下载P2L模型..."
if [ -f "download_current_model.py" ]; then
    # 检查Python环境
    if command -v python3 &> /dev/null; then
        echo "⬇️  开始预下载模型..."
        if python3 download_current_model.py; then
            echo "✅ 模型预下载成功！"
            echo "🚀 Docker容器启动将更快"
        else
            echo "⚠️  模型预下载失败，将在容器启动时重试"
        fi
    else
        echo "⚠️  未找到Python3，跳过预下载"
        echo "💡 说明：容器启动时将自动下载模型"
    fi
else
    echo "⚠️  未找到下载脚本，跳过预下载"
    echo "💡 说明：容器启动时将自动下载模型"
fi

echo "💡 说明：模型下载策略"
echo "   - 优先使用预下载的模型"
echo "   - 容器启动时会自动检测并补充缺失的模型"
echo "   - 模型配置由 constants.py 中的 DEFAULT_MODEL 决定"
echo "   - 下载进度可通过日志查看: docker-compose logs -f backend"

# 检查配置文件
echo "⚙️  检查配置文件..."
if [ ! -f "backend/api_config.env" ]; then
    echo "⚠️  未找到 backend/api_config.env，创建示例文件..."
    cat > backend/api_config.env << EOF
# API 配置示例
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
EOF
    echo "请编辑 backend/api_config.env 添加您的 API 密钥"
fi

# 创建日志目录
mkdir -p logs

# 升级模式处理
if [ "$UPGRADE_MODE" = true ]; then
    echo "🔄 开始平滑升级..."
    
    # 检查当前运行的服务
    if docker-compose ps | grep -q "Up"; then
        echo "📊 当前服务状态："
        docker-compose ps
        
        # 备份当前运行的容器（以防回滚）
        echo "💾 创建服务备份..."
        BACKUP_TAG=$(date +%Y%m%d_%H%M%S)
        
        # 为当前运行的镜像打标签备份
        if docker images | grep -q "program-b[_-]backend"; then
            docker tag program-b_backend:latest program-b_backend:backup_$BACKUP_TAG || true
        fi
        if docker images | grep -q "program-b[_-]frontend"; then
            docker tag program-b_frontend:latest program-b_frontend:backup_$BACKUP_TAG || true
        fi
        
        echo "✅ 备份完成，标签: backup_$BACKUP_TAG"
        
        # 构建新镜像（不停止服务）
        echo "🔨 构建新版本镜像..."
        if [ "$1" = "production" ] || [ "$2" = "production" ]; then
            docker-compose --profile production build
        else
            docker-compose build
        fi
        
        # 滚动更新：先更新后端
        echo "🔄 更新后端服务..."
        docker-compose up -d --no-deps backend
        
        # 等待后端健康检查
        echo "⏳ 等待后端服务就绪..."
        for i in {1..60}; do
            if curl -s http://localhost:8080/health > /dev/null; then
                echo "✅ 后端服务更新成功！"
                break
            fi
            if [ $i -eq 60 ]; then
                echo "❌ 后端服务更新失败，开始回滚..."
                docker tag program-b_backend:backup_$BACKUP_TAG program-b_backend:latest
                docker-compose up -d --no-deps backend
                exit 1
            fi
            sleep 2
        done
        
        # 更新前端服务
        echo "🔄 更新前端服务..."
        docker-compose up -d --no-deps frontend
        
        # 等待前端健康检查
        echo "⏳ 等待前端服务就绪..."
        for i in {1..30}; do
            if curl -s http://localhost:3000 > /dev/null; then
                echo "✅ 前端服务更新成功！"
                break
            fi
            if [ $i -eq 30 ]; then
                echo "❌ 前端服务更新失败，开始回滚..."
                docker tag program-b_frontend:backup_$BACKUP_TAG program-b_frontend:latest
                docker-compose up -d --no-deps frontend
                exit 1
            fi
            sleep 2
        done
        
        # 如果启用了nginx，也更新它
        if [ "$1" = "production" ] || [ "$2" = "production" ]; then
            echo "🔄 更新Nginx服务..."
            docker-compose --profile production up -d --no-deps nginx
        fi
        
        # 清理旧的备份镜像（保留最近3个）
        echo "🧹 清理旧备份..."
        docker images | grep "backup_" | tail -n +4 | awk '{print $1":"$2}' | xargs -r docker rmi || true
        
        echo "🎉 平滑升级完成！"
        
    else
        echo "⚠️  未检测到运行中的服务，执行全新部署..."
        UPGRADE_MODE=false
    fi
fi

# 常规部署模式
if [ "$UPGRADE_MODE" = false ]; then
    # 停止现有服务
    echo "🛑 停止现有服务..."
    docker-compose down || true

    # 清理旧镜像
    echo "🧹 清理旧镜像..."
    docker system prune -f

    # 构建并启动服务
    echo "🔨 构建并启动服务..."
    if [ "$1" = "production" ] || [ "$2" = "production" ]; then
        echo "🏭 启动生产环境（包含 Nginx）..."
        docker-compose --profile production up -d --build
    else
        echo "🚀 启动开发环境..."
        docker-compose up -d --build
    fi
fi

# 健康检查（仅在非升级模式下执行，升级模式已经检查过了）
if [ "$UPGRADE_MODE" = false ]; then
    # 等待服务启动（首次启动需要下载模型，时间较长）
    echo "⏳ 等待服务启动（首次启动需要下载模型，请耐心等待）..."
    sleep 60

    # 健康检查
    echo "🏥 健康检查..."
    
    # 根据部署模式选择不同的健康检查方式
    if [ "$1" = "production" ] || [ "$2" = "production" ]; then
        # 生产环境：通过 Nginx 检查
        echo "🔍 检查 Nginx 服务..."
        for i in {1..30}; do
            if curl -s http://localhost:80 > /dev/null 2>&1; then
                echo "✅ Nginx 服务启动成功！"
                break
            fi
            if [ $i -eq 30 ]; then
                echo "❌ Nginx 服务启动失败"
                docker-compose logs nginx
                exit 1
            fi
            sleep 2
        done
        
        echo "🔍 检查后端服务（通过 Nginx 代理）..."
        for i in {1..30}; do
            if curl -s http://localhost:80/health > /dev/null 2>&1; then
                echo "✅ 后端服务（通过 Nginx）启动成功！"
                break
            fi
            if [ $i -eq 30 ]; then
                echo "❌ 后端服务启动失败"
                docker-compose logs backend
                exit 1
            fi
            sleep 2
        done
    else
        # 开发环境：直接检查服务端口
        echo "🔍 检查后端服务..."
        for i in {1..60}; do
            if curl -s http://localhost:8080/health > /dev/null; then
                echo "✅ 后端服务启动成功！"
                break
            fi
            if [ $i -eq 60 ]; then
                echo "❌ 后端服务启动失败"
                echo "📋 查看日志以了解详情:"
                docker-compose logs --tail=50 backend
                exit 1
            fi
            if [ $((i % 10)) -eq 0 ]; then
                echo "⏳ 仍在等待后端服务启动... ($i/60)"
            fi
            sleep 5
        done

        echo "🔍 检查前端服务..."
        for i in {1..15}; do
            if curl -s http://localhost:3000 > /dev/null; then
                echo "✅ 前端服务启动成功！"
                break
            fi
            if [ $i -eq 15 ]; then
                echo "❌ 前端服务启动失败"
                docker-compose logs frontend
                exit 1
            fi
            sleep 2
        done
    fi
fi

# 显示服务状态
echo ""
echo "📊 服务状态："
docker-compose ps

echo ""
if [ "$UPGRADE_MODE" = true ]; then
    echo "🎉 服务升级完成！"
    echo ""
    echo "📊 升级后服务状态："
    docker-compose ps
    echo ""
    echo "💡 升级说明："
    echo "  ✅ 服务已平滑升级，无停机时间"
    echo "  ✅ 自动备份了旧版本镜像"
    echo "  ✅ 如有问题可快速回滚"
else
    echo "🎉 部署完成！"
fi
echo ""
echo "🌐 访问地址："
if [ "$1" = "production" ] || [ "$2" = "production" ]; then
    echo "  🏭 生产环境 (Nginx 反向代理)："
    echo "    主页: http://43.136.17.170/"
    echo "    API: http://43.136.17.170/api/"
    echo "    健康检查: http://43.136.17.170/health"
    echo "    API文档: http://43.136.17.170/docs"
    echo ""
    echo "  🔧 Nginx 配置："
    echo "    - 前端: / → frontend:80"
    echo "    - API: /api/ → backend:8080"
    echo "    - 健康检查: /health → backend:8080/health"
    echo "    - 文档: /docs → backend:8080/docs"
    echo ""
    echo "  ✅ 优势："
    echo "    - 统一域名访问，无跨域问题"
    echo "    - 只需开放 80 端口"
    echo "    - 生产级 Nginx 反向代理"
else
    echo "  🚀 开发环境："
    echo "    前端: http://localhost:3000"
    echo "    后端: http://localhost:8080"
    echo "    API文档: http://localhost:8080/docs"
fi
echo ""
echo "📋 管理命令："
echo "  查看日志: docker-compose logs -f"
echo "  查看后端日志: docker-compose logs -f backend"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  查看状态: docker-compose ps"
echo ""
echo "🚀 部署命令："
echo "  开发环境: ./deploy.sh"
echo "  生产环境: ./deploy.sh production"
echo "  平滑升级: ./deploy.sh upgrade"
echo "  生产升级: ./deploy.sh production upgrade"
if [ "$UPGRADE_MODE" = true ]; then
    echo "  查看备份: docker images | grep backup"
fi
echo ""
echo "🤖 模型管理："
echo "  - 模型配置: 编辑 constants.py 中的 DEFAULT_MODEL"
echo "  - 自动下载: backend服务启动时自动检测并下载模型"
echo "  - 模型位置: ./models/ 目录"
echo "  - 切换模型: 修改 constants.py 后重启服务即可"