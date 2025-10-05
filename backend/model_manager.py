#!/usr/bin/env python3
"""
Backend模型管理器 - 简化包装器
使用p2l_core作为唯一依赖
"""

import os
import sys
from typing import Dict

# 添加根目录到路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

def check_model_exists() -> bool:
    """快速检查默认模型文件是否存在"""
    try:
        from p2l_core import check_model_exists as _check
        return _check()
    except Exception:
        return False

def get_model_status() -> Dict:
    """获取当前模型状态"""
    try:
        from p2l_core import get_model_status as _get_status
        return _get_status()
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def print_model_status():
    """打印后端模型状态信息"""
    try:
        from p2l_core import print_backend_status
        print_backend_status()
    except Exception as e:
        print(f"❌ 无法获取模型状态: {e}")

# 为了保持向后兼容，导入核心类
try:
    from p2l_core import P2LModelManager as ModelManager, get_manager
    __all__ = ['ModelManager', 'get_manager', 'check_model_exists', 'get_model_status', 'print_model_status']
except ImportError:
    __all__ = ['check_model_exists', 'get_model_status', 'print_model_status']