#!/usr/bin/env python3
"""
P2L后端服务启动文件
统一的后端服务入口
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    print("🚀 P2L后端服务启动")
    print("=" * 50)
    
    # 启动服务
    try:
        from .service import main
    except ImportError:
        # 兼容直接运行的情况
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from service import main
    main()