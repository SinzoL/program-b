# Docker部署适配说明

## 概述

为了支持Docker容器化部署，我们对模型管理系统进行了适配，确保在容器环境中也能正常工作。

## Docker适配修改

### 1. 修改的文件

#### `Dockerfile.backend`
- 添加模型管理脚本的执行权限
- 使用自定义启动脚本 `docker-entrypoint.sh`
- 调整健康检查时间，适应模型下载需求

#### `docker-compose.yml`
- 修改健康检查命令，使用Python而不是curl
- 增加启动等待时间（start_period: 300s）
- 增加重试次数，适应首次启动的模型下载

#### `model_utils.py`
- 添加Docker环境检测
- 自动适配容器内的路径（/app/models）

#### `deploy.sh`
- 更新模型管理说明
- 增加健康检查等待时间和重试次数
- 添加日志查看提示

## Docker部署流程

### 1. 容器启动流程
```
Docker容器启动
├── 设置环境变量 (PYTHONPATH=/app)
├── 运行 ensure_model.py
│   ├── 检查默认模型是否存在
│   ├── 自动安装 huggingface_hub 依赖
│   └── 下载缺失的模型
└── 启动 backend 服务
```

### 2. 模型管理
- **自动下载**: 容器首次启动时自动下载配置的默认模型
- **持久化**: 模型存储在挂载的 `./models` 目录中
- **配置**: 通过 `constants.py` 中的 `DEFAULT_MODEL` 配置

### 3. 部署命令
```bash
# 开发环境部署
./deploy.sh

# 生产环境部署
./deploy.sh production

# 平滑升级
./deploy.sh upgrade
```

## 环境差异处理

### 本地开发环境
- 模型路径: `./models/`
- 启动方式: `./start-dev.sh`
- 模型管理: 直接运行 `python3 ensure_model.py`

### Docker容器环境
- 模型路径: `/app/models/`
- 启动方式: Dockerfile中的CMD命令
- 模型管理: 容器启动时自动执行

## 监控和调试

### 查看模型下载进度
```bash
# 查看backend容器日志
docker-compose logs -f backend

# 查看最近50行日志
docker-compose logs --tail=50 backend
```

### 健康检查
- **检查间隔**: 60秒
- **启动等待**: 300秒（5分钟）
- **超时时间**: 15秒
- **重试次数**: 5次

### 常见问题

1. **首次启动时间长**
   - 原因: 需要下载模型文件
   - 解决: 耐心等待，查看日志了解进度

2. **健康检查失败**
   - 原因: 模型下载时间超过预期
   - 解决: 检查网络连接，查看容器日志

3. **模型路径问题**
   - 原因: 容器内外路径不一致
   - 解决: 使用 `ModelManager` 类自动处理路径

## 性能优化

### 资源配置
```yaml
deploy:
  resources:
    limits:
      memory: 2.5G      # 适合模型加载
      cpus: '1.5'
    reservations:
      memory: 1G
      cpus: '0.5'
```

### 模型缓存
- 模型文件持久化存储在 `./models` 目录
- 容器重启不会重新下载已有模型
- 支持多个模型版本共存

## 升级和维护

### 模型更新
1. 修改 `constants.py` 中的 `DEFAULT_MODEL`
2. 重新部署: `./deploy.sh upgrade`
3. 容器会自动下载新模型

### 平滑升级
- 支持零停机升级
- 自动备份旧版本镜像
- 失败时自动回滚

## 总结

通过这些适配，Docker部署现在支持：
- ✅ 自动模型管理
- ✅ 环境路径适配
- ✅ 健康检查优化
- ✅ 日志监控
- ✅ 平滑升级
- ✅ 资源优化

部署更加简单可靠，适合生产环境使用。