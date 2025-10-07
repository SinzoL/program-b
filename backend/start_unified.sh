#!/bin/bash
# P2L Backend 统一启动脚本
# 合并所有启动功能到一个脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    print_message "✅ Python3 环境检查通过"
}

# 检查依赖
check_dependencies() {
    print_message "🔍 检查Python依赖..."
    
    # 检查关键依赖
    python3 -c "import torch; print('✅ PyTorch:', torch.__version__)" || {
        print_error "PyTorch 未安装"
        exit 1
    }
    
    python3 -c "import transformers; print('✅ Transformers:', transformers.__version__)" || {
        print_error "Transformers 未安装"
        exit 1
    }
    
    python3 -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)" || {
        print_error "FastAPI 未安装"
        exit 1
    }
    
    # 检查可选依赖
    python3 -c "import cvxpy; print('✅ CVXPY:', cvxpy.__version__)" || {
        print_warning "CVXPY 未安装，成本优化功能将受限"
    }
}

# 检查模型文件
check_models() {
    print_message "🔍 检查P2L模型文件..."
    
    MODEL_PATH="model_p2l/models/p2l-135m-grk"
    if [ -d "$MODEL_PATH" ]; then
        print_message "✅ P2L模型目录存在: $MODEL_PATH"
        
        # 检查关键文件
        if [ -f "$MODEL_PATH/config.json" ]; then
            print_message "✅ 配置文件存在"
        else
            print_warning "配置文件缺失: config.json"
        fi
        
        if [ -f "$MODEL_PATH/pytorch_model.bin" ] || [ -f "$MODEL_PATH/model.safetensors" ]; then
            print_message "✅ 模型权重文件存在"
        else
            print_warning "模型权重文件缺失"
        fi
    else
        print_warning "P2L模型目录不存在: $MODEL_PATH"
    fi
}

# 启动服务
start_service() {
    local mode=${1:-"normal"}
    
    print_message "🚀 启动P2L Backend服务 (模式: $mode)"
    
    case $mode in
        "debug")
            print_message "🐛 调试模式启动..."
            export PYTHONPATH="${PYTHONPATH}:$(pwd)"
            python3 -u main.py 2>&1 | tee logs/debug_$(date +%Y%m%d_%H%M%S).log
            ;;
        "production")
            print_message "🏭 生产模式启动..."
            export PYTHONPATH="${PYTHONPATH}:$(pwd)"
            nohup python3 main.py > logs/production.log 2>&1 &
            echo $! > logs/backend.pid
            print_message "✅ 服务已在后台启动，PID: $(cat logs/backend.pid)"
            ;;
        *)
            print_message "🔄 标准模式启动..."
            export PYTHONPATH="${PYTHONPATH}:$(pwd)"
            python3 main.py
            ;;
    esac
}

# 停止服务
stop_service() {
    if [ -f "logs/backend.pid" ]; then
        local pid=$(cat logs/backend.pid)
        print_message "🛑 停止后台服务 (PID: $pid)"
        kill $pid 2>/dev/null || print_warning "进程可能已经停止"
        rm -f logs/backend.pid
    else
        print_warning "未找到后台服务PID文件"
    fi
}

# 创建日志目录
mkdir -p logs

# 主逻辑
case "${1:-start}" in
    "start")
        check_python
        check_dependencies
        check_models
        start_service "normal"
        ;;
    "debug")
        check_python
        check_dependencies
        check_models
        start_service "debug"
        ;;
    "production")
        check_python
        check_dependencies
        check_models
        start_service "production"
        ;;
    "stop")
        stop_service
        ;;
    "restart")
        stop_service
        sleep 2
        check_python
        check_dependencies
        check_models
        start_service "normal"
        ;;
    "status")
        if [ -f "logs/backend.pid" ]; then
            local pid=$(cat logs/backend.pid)
            if ps -p $pid > /dev/null 2>&1; then
                print_message "✅ 服务正在运行 (PID: $pid)"
            else
                print_warning "PID文件存在但进程未运行"
                rm -f logs/backend.pid
            fi
        else
            print_message "ℹ️  服务未在后台运行"
        fi
        ;;
    "help"|"-h"|"--help")
        echo "P2L Backend 统一启动脚本"
        echo ""
        echo "用法: $0 [命令]"
        echo ""
        echo "命令:"
        echo "  start       启动服务 (默认)"
        echo "  debug       调试模式启动"
        echo "  production  生产模式后台启动"
        echo "  stop        停止后台服务"
        echo "  restart     重启服务"
        echo "  status      查看服务状态"
        echo "  help        显示此帮助信息"
        ;;
    *)
        print_error "未知命令: $1"
        echo "使用 '$0 help' 查看帮助信息"
        exit 1
        ;;
esac