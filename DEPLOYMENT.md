# P2L 项目部署指南

## 快速部署

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd program-b
```

### 2. 一键部署

**开发环境（推荐）：**
```bash
./deploy.sh
```

**生产环境（包含Nginx反向代理）：**
```bash
./deploy.sh production
```

## 部署要求

### 最低配置
- **CPU**: 2核
- **内存**: 4GB（推荐8GB）
- **存储**: 20GB可用空间
- **系统**: Ubuntu 20.04+ / CentOS 8+ / macOS

### 必需软件
- Docker 20.10+
- Docker Compose 2.0+
- curl
- Python 3.8+（用于下载模型）

## 配置说明

### 环境变量配置
在首次部署前，请配置 `backend/api_config.env`：

```env
# API 配置
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# 其他配置（可选）
P2L_DEBUG=false
P2L_LOG_LEVEL=INFO
```

### 端口配置
- **前端**: 3000 (开发环境) / 80 (生产环境)
- **后端**: 8080
- **Nginx**: 80 (仅生产环境)

## 部署模式

### 开发模式
```bash
./deploy.sh
```
- 直接访问前端和后端服务
- 适合开发和测试
- 资源占用较少

### 生产模式
```bash
./deploy.sh production
```
- 通过Nginx反向代理
- 更好的性能和安全性
- 适合生产环境

## 常用命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 停止服务
```bash
docker-compose down
```

### 更新部署
```bash
# 停止服务
docker-compose down

# 拉取最新代码
git pull

# 重新部署
./deploy.sh
```

## 故障排除

### 常见问题

1. **模型下载失败**
   ```bash
   # 手动下载模型
   pip3 install huggingface_hub
   python3 -c "
   from huggingface_hub import snapshot_download
   import os
   os.makedirs('models', exist_ok=True)
   snapshot_download(
       repo_id='lmarena-ai/p2l-0.5b-grk-01112025',
       local_dir='./models/p2l-0.5b-grk',
       repo_type='model'
   )"
   ```

2. **内存不足**
   ```bash
   # 检查内存使用
   docker stats
   
   # 清理Docker缓存
   docker system prune -f
   ```

3. **端口被占用**
   ```bash
   # 检查端口占用
   sudo netstat -tlnp | grep :8080
   sudo netstat -tlnp | grep :3000
   
   # 修改docker-compose.yml中的端口映射
   ```

### 健康检查
```bash
# 检查后端健康状态
curl http://localhost:8080/health

# 检查前端访问
curl http://localhost:3000
```

## 性能优化

### 轻量服务器优化
项目已针对2核4G服务器进行优化：

- 设置了内存限制（后端2.5G，前端512M）
- 优化了日志大小和保留策略
- 配置了合适的健康检查间隔
- 使用了轻量化的基础镜像

### 监控资源使用
```bash
# 实时监控容器资源
docker stats

# 查看系统资源
free -h
df -h
```

## 安全建议

1. **防火墙配置**
   ```bash
   # 只开放必要端口
   sudo ufw allow ssh
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

2. **定期更新**
   ```bash
   # 更新系统
   sudo apt update && sudo apt upgrade -y
   
   # 更新Docker镜像
   docker-compose pull
   ```

3. **备份重要数据**
   ```bash
   # 备份模型和配置
   tar -czf backup-$(date +%Y%m%d).tar.gz models/ backend/api_config.env logs/
   ```

## 支持

如遇到问题，请检查：
1. Docker和Docker Compose版本
2. 系统资源使用情况
3. 网络连接状态
4. 日志文件内容

更多帮助请查看项目文档或提交Issue。