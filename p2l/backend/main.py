#!/usr/bin/env python3
"""
P2L后端服务启动文件
统一的后端服务入口
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service import main

if __name__ == "__main__":
    main()