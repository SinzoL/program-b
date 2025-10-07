#!/usr/bin/env python3
"""
Backend主启动文件 - 简化版本
统一的后端服务入口
"""

import os
import sys
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    try:
        # 设置Python路径
        backend_path = os.path.dirname(os.path.abspath(__file__))
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # 导入并启动P2L原生服务
        from service_p2l_native import main as service_main
        logger.info("🚀 启动P2L原生Backend服务...")
        service_main()
        
    except ImportError as e:
        logger.error(f"❌ P2L原生服务模块导入失败: {e}")
        logger.error("请确保所有依赖已正确安装")
        logger.error(f"当前Python路径: {sys.path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()