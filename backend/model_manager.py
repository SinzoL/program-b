#!/usr/bin/env python3
"""
P2L模型管理器 - 简化版
只负责模型检查，不处理下载逻辑
"""

import os
import sys
from pathlib import Path

def check_model_exists():
    """
    快速检查默认模型文件是否存在
    
    Returns:
        bool: 模型文件是否存在
    """
    try:
        # 使用外部模型管理工具
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from model_utils import ModelManager
        from constants import DEFAULT_MODEL
        
        manager = ModelManager()
        return manager.check_model_exists(DEFAULT_MODEL)
        
    except Exception:
        return False

def get_model_status():
    """
    获取当前模型状态
    
    Returns:
        dict: 模型状态信息
    """
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from model_utils import ModelManager
        
        manager = ModelManager()
        return manager.get_model_status()
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def print_model_status():
    """打印模型状态信息"""
    status = get_model_status()
    
    print("\n" + "🚀 " + "=" * 50)
    print("🚀 Backend服务初始化")
    print("=" * 52)
    
    if status.get('default_exists'):
        print("✅ 服务状态: 完全就绪")
        print("🎉 P2L模型已加载，所有功能可正常使用")
    else:
        print("⚠️  服务状态: 降级模式")
        print("💡 说明: P2L模型未准备就绪，部分功能可能受限")
        print("🔧 建议: 运行 python ensure_model.py 下载模型")
    
    print("=" * 52 + "\n")