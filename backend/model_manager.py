#!/usr/bin/env python3
"""
P2L模型管理器
统一处理模型检查、下载和管理
"""

import os
import sys
import time
from pathlib import Path

def ensure_p2l_model(force_check=False):
    """
    确保P2L默认模型存在，如果不存在则自动下载
    
    Args:
        force_check (bool): 是否强制重新检查模型配置
        
    Returns:
        bool: 模型是否准备就绪
    """
    try:
        # 导入配置
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 重新导入配置以获取最新的DEFAULT_MODEL
        if force_check and 'constants' in sys.modules:
            import importlib
            importlib.reload(sys.modules['constants'])
        
        from constants import DEFAULT_MODEL
        from backend.config import get_p2l_config
        
        print("🔍 检查P2L模型状态...")
        print(f"🎯 当前默认模型: {DEFAULT_MODEL}")
        
        # 获取配置
        config = get_p2l_config()
        models_dir = Path(config['model_path'])
        available_models = config.get('available_models', [])
        
        # 查找默认模型对应的配置
        default_model_config = None
        for model in available_models:
            if model['name'] == DEFAULT_MODEL:
                default_model_config = model
                break
        
        if not default_model_config:
            print(f"⚠️  未找到默认模型配置: {DEFAULT_MODEL}")
            print("💡 请检查constants.py中的MODEL_MAPPING配置")
            return False
        
        # 检查本地模型路径
        local_model_path = models_dir / default_model_config['local_name']
        
        # 检查模型是否存在且非空
        if local_model_path.exists() and any(local_model_path.iterdir()):
            files_count = len(list(local_model_path.glob("*")))
            print(f"✅ P2L模型已存在: {local_model_path}")
            print(f"📊 模型信息: {default_model_config['description']}")
            print(f"📁 包含文件: {files_count} 个")
            return True
        
        # 模型不存在，开始下载
        return _download_model(default_model_config, local_model_path, DEFAULT_MODEL)
        
    except Exception as e:
        print("=" * 60)
        print("❌ 模型检查失败")
        print("=" * 60)
        print(f"🚫 错误信息: {e}")
        print("💡 请检查配置文件和目录权限")
        print("=" * 60)
        return False

def _download_model(model_config, local_path, model_name):
    """
    下载指定模型
    
    Args:
        model_config (dict): 模型配置信息
        local_path (Path): 本地存储路径
        model_name (str): 模型名称
        
    Returns:
        bool: 下载是否成功
    """
    print("=" * 60)
    print("🚀 开始下载P2L模型")
    print("=" * 60)
    print(f"🏷️  模型名称: {model_name}")
    print(f"📦 仓库地址: {model_config['repo_id']}")
    print(f"💾 本地路径: {local_path}")
    print(f"📊 模型参数: {model_config['parameters']}")
    print(f"💾 内存需求: {model_config['memory_required']}MB")
    print(f"💡 模型描述: {model_config['description']}")
    print("⏳ 正在下载中，请耐心等待...")
    print("   (首次下载可能需要几分钟时间)")
    print("=" * 60)
    
    try:
        from huggingface_hub import snapshot_download
        
        # 确保目录存在
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 记录开始时间
        start_time = time.time()
        
        # 下载模型
        downloaded_path = snapshot_download(
            repo_id=model_config['repo_id'],
            local_dir=str(local_path),
            local_dir_use_symlinks=False,
            resume_download=True
        )
        
        # 计算下载时间
        download_time = time.time() - start_time
        minutes = int(download_time // 60)
        seconds = int(download_time % 60)
        
        print("=" * 60)
        print("🎉 模型下载成功!")
        print("=" * 60)
        print(f"📂 模型位置: {downloaded_path}")
        print(f"⏱️  下载耗时: {minutes}分{seconds}秒")
        print(f"💾 内存需求: {model_config['memory_required']}MB")
        print("✅ 模型已准备就绪")
        print("=" * 60)
        
        return True
        
    except ImportError:
        print("=" * 60)
        print("❌ 缺少依赖")
        print("=" * 60)
        print("🔧 请安装 huggingface_hub:")
        print("   pip install huggingface_hub")
        print("💡 或手动下载模型后重启服务")
        print("=" * 60)
        return False
        
    except Exception as e:
        print("=" * 60)
        print("❌ 下载失败")
        print("=" * 60)
        print(f"🚫 错误信息: {e}")
        print("💡 可能的解决方案:")
        print("   1. 检查网络连接")
        print("   2. 检查磁盘空间")
        print(f"   3. 手动下载: git clone https://huggingface.co/{model_config['repo_id']} {local_path}")
        print("   4. 或稍后重试")
        print("=" * 60)
        return False

def get_model_status():
    """
    获取当前模型状态
    
    Returns:
        dict: 模型状态信息
    """
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from constants import DEFAULT_MODEL
        from backend.config import get_p2l_config
        
        config = get_p2l_config()
        models_dir = Path(config['model_path'])
        
        # 查找默认模型配置
        default_model_config = None
        for model in config.get('available_models', []):
            if model['name'] == DEFAULT_MODEL:
                default_model_config = model
                break
        
        if not default_model_config:
            return {
                'status': 'error',
                'message': f'未找到默认模型配置: {DEFAULT_MODEL}'
            }
        
        local_model_path = models_dir / default_model_config['local_name']
        
        if local_model_path.exists() and any(local_model_path.iterdir()):
            files_count = len(list(local_model_path.glob("*")))
            return {
                'status': 'ready',
                'model_name': DEFAULT_MODEL,
                'local_path': str(local_model_path),
                'files_count': files_count,
                'description': default_model_config['description']
            }
        else:
            return {
                'status': 'missing',
                'model_name': DEFAULT_MODEL,
                'local_path': str(local_model_path),
                'repo_id': default_model_config['repo_id']
            }
            
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
    
    if status['status'] == 'ready':
        print("✅ 服务状态: 完全就绪")
        print("🎉 P2L模型已加载，所有功能可正常使用")
    elif status['status'] == 'missing':
        print("⚠️  服务状态: 降级模式")
        print("💡 说明: P2L模型未准备就绪，部分功能可能受限")
        print("🔧 建议: 运行 python download_current_model.py 下载模型")
    else:
        print("❌ 服务状态: 配置错误")
        print(f"🚫 错误: {status.get('message', '未知错误')}")
    
    print("=" * 52 + "\n")