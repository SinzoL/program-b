#!/usr/bin/env python3
"""
P2L核心模块 - 统一的常量定义和模型管理
这是backend和p2l项目的唯一依赖文件
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Optional, List

# ================== P2L核心常量 ==================

# 默认P2L模型
DEFAULT_MODEL = "p2l-135m-grk-01112025"

# 模型映射关系
MODEL_MAPPING = {
    "p2l-135m-grk-01112025": {
        "repo_id": "lmarena-ai/p2l-135m-grk-01112025",
        "local_name": "p2l-135m-grk",
        "description": "轻量级模型，适合资源受限环境",
        "memory_required": 512,
        "parameters": "135M"
    },
    "p2l-360m-grk-01112025": {
        "repo_id": "lmarena-ai/p2l-360m-grk-01112025", 
        "local_name": "p2l-360m-grk",
        "description": "中等规模模型，平衡性能和资源",
        "memory_required": 1024,
        "parameters": "360M"
    },
    "p2l-0.5b-grk-01112025": {
        "repo_id": "lmarena-ai/p2l-0.5b-grk-01112025",
        "local_name": "p2l-0.5b-grk",
        "description": "标准模型，平衡性能和资源消耗",
        "memory_required": 2048,
        "parameters": "0.5B"
    },
    "p2l-1.5b-grk-01112025": {
        "repo_id": "lmarena-ai/p2l-1.5b-grk-01112025",
        "local_name": "p2l-1.5b-grk", 
        "description": "高性能模型，需要更多资源",
        "memory_required": 4096,
        "parameters": "1.5B"
    },
    "p2l-3b-grk-01112025": {
        "repo_id": "lmarena-ai/p2l-3b-grk-01112025",
        "local_name": "p2l-3b-grk",
        "description": "大型模型，最佳性能",
        "memory_required": 8192,
        "parameters": "3B"
    },
    "p2l-7b-grk-01112025": {
        "repo_id": "lmarena-ai/p2l-7b-grk-01112025",
        "local_name": "p2l-7b-grk",
        "description": "超大型模型，顶级性能",
        "memory_required": 16384,
        "parameters": "7B"
    }
}

# 服务配置常量
DEFAULT_PORT = 8080
DEFAULT_HOST = "0.0.0.0"
MODELS_DIR_NAME = "models"
BACKEND_DIR_NAME = "backend"
P2L_DIR_NAME = "p2l"

# ================== 核心模型管理器 ==================

class P2LModelManager:
    """P2L模型管理器 - 核心功能类"""
    
    def __init__(self):
        # 智能检测环境
        if os.path.exists('/app') and os.getcwd().startswith('/app'):
            self.models_dir = Path("/app/models")
            self.is_docker = True
        else:
            self.models_dir = Path("models")
            self.is_docker = False
        
        self.models_dir.mkdir(exist_ok=True)
    
    def get_model_config(self, model_name: str) -> Optional[Dict]:
        """获取模型配置"""
        return MODEL_MAPPING.get(model_name)
    
    def get_model_path(self, model_name: str) -> Optional[Path]:
        """获取模型本地路径"""
        config = self.get_model_config(model_name)
        if not config:
            return None
        return self.models_dir / config['local_name']
    
    def check_model_exists(self, model_name: str) -> bool:
        """检查模型是否存在"""
        model_path = self.get_model_path(model_name)
        if not model_path:
            return False
        return model_path.exists() and any(model_path.iterdir())
    
    def install_dependencies(self) -> bool:
        """安装必要的依赖"""
        try:
            import huggingface_hub
            return True
        except ImportError:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
                    "huggingface_hub"
                ])
                return True
            except subprocess.CalledProcessError:
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", "huggingface_hub"
                    ])
                    return True
                except subprocess.CalledProcessError:
                    return False
    
    def download_model(self, model_name: str, force: bool = False, verbose: bool = True) -> bool:
        """下载指定模型"""
        config = self.get_model_config(model_name)
        if not config:
            if verbose:
                print(f"❌ 未找到模型配置: {model_name}")
            return False
        
        if not force and self.check_model_exists(model_name):
            if verbose:
                print(f"✅ 模型已存在: {config['local_name']}")
            return True
        
        if verbose:
            print(f"🚀 开始下载模型: {model_name}")
            print(f"📦 仓库地址: {config['repo_id']}")
            print(f"📊 模型参数: {config['parameters']}")
        
        try:
            from huggingface_hub import snapshot_download
            
            start_time = time.time()
            model_path = self.get_model_path(model_name)
            
            snapshot_download(
                repo_id=config['repo_id'],
                local_dir=str(model_path),
                local_dir_use_symlinks=False,
                resume_download=True
            )
            
            if verbose:
                download_time = time.time() - start_time
                minutes = int(download_time // 60)
                seconds = int(download_time % 60)
                print(f"✅ 模型下载成功! 耗时: {minutes}分{seconds}秒")
            
            return True
            
        except ImportError:
            if verbose:
                print("❌ 缺少依赖: pip install huggingface_hub")
            return False
        except Exception as e:
            if verbose:
                print(f"❌ 下载失败: {e}")
            return False
    
    def ensure_default_model(self, verbose: bool = True) -> bool:
        """确保默认模型存在"""
        if verbose:
            print("🚀 P2L模型检查工具")
            print("=" * 40)
        
        if not self.install_dependencies():
            if verbose:
                print("⚠️  依赖安装失败，但继续尝试模型检查...")
        
        if verbose:
            print(f"🔍 检查默认模型: {DEFAULT_MODEL}")
        
        if self.check_model_exists(DEFAULT_MODEL):
            if verbose:
                print(f"✅ 默认模型 {DEFAULT_MODEL} 已存在")
            return True
        
        if verbose:
            print(f"⚠️  默认模型 {DEFAULT_MODEL} 不存在，尝试下载...")
        
        success = self.download_model(DEFAULT_MODEL, verbose=verbose)
        
        if verbose:
            if success:
                print("\n🎉 模型下载完成!")
                print("✅ 服务可以正常启动")
            else:
                print("\n❌ 模型下载失败!")
                print("💡 请检查网络连接或手动下载模型")
        
        return success
    
    def get_status(self) -> Dict:
        """获取模型状态信息"""
        available = list(MODEL_MAPPING.keys())
        downloaded = [name for name in available if self.check_model_exists(name)]
        default_exists = self.check_model_exists(DEFAULT_MODEL)
        
        return {
            'default_model': DEFAULT_MODEL,
            'default_exists': default_exists,
            'available_models': available,
            'downloaded_models': downloaded,
            'total_available': len(available),
            'total_downloaded': len(downloaded),
            'environment': 'docker' if self.is_docker else 'local',
            'models_dir': str(self.models_dir)
        }
    
    def print_status(self):
        """打印详细的模型状态"""
        status = self.get_status()
        
        print("\n" + "=" * 50)
        print("🚀 P2L模型状态")
        print("=" * 50)
        print(f"🌍 运行环境: {status['environment']}")
        print(f"📁 模型目录: {status['models_dir']}")
        print(f"📋 默认模型: {status['default_model']}")
        print(f"✅ 默认模型存在: {'是' if status['default_exists'] else '否'}")
        print(f"📊 可用模型: {status['total_available']} 个")
        print(f"💾 已下载: {status['total_downloaded']} 个")
        
        if status['downloaded_models']:
            print("\n📁 已下载的模型:")
            for model in status['downloaded_models']:
                config = self.get_model_config(model)
                print(f"  - {model} ({config['parameters']})")
        
        if not status['default_exists']:
            print(f"\n⚠️  建议运行: python p2l_tools.py download")
        
        print("=" * 50 + "\n")

# ================== 便捷接口函数 ==================

# 全局管理器实例（单例模式）
_manager = None

def get_manager() -> P2LModelManager:
    """获取全局模型管理器实例"""
    global _manager
    if _manager is None:
        _manager = P2LModelManager()
    return _manager

def check_model_exists(model_name: str = None) -> bool:
    """检查模型是否存在"""
    if model_name is None:
        model_name = DEFAULT_MODEL
    return get_manager().check_model_exists(model_name)

def get_model_status() -> Dict:
    """获取模型状态"""
    return get_manager().get_status()

def ensure_default_model(verbose: bool = True) -> bool:
    """确保默认模型存在"""
    return get_manager().ensure_default_model(verbose)

def download_model(model_name: str = None, force: bool = False, verbose: bool = True) -> bool:
    """下载模型"""
    if model_name is None:
        model_name = DEFAULT_MODEL
    return get_manager().download_model(model_name, force, verbose)

def print_status():
    """打印模型状态"""
    get_manager().print_status()

# ================== Backend专用接口 ==================

def get_backend_status() -> Dict:
    """获取后端服务状态信息"""
    status = get_model_status()
    return {
        'p2l_ready': status['default_exists'],
        'models_available': status['total_downloaded'],
        'environment': status['environment'],
        'default_model': status['default_model']
    }

def print_backend_status():
    """为后端服务打印状态信息"""
    status = get_backend_status()
    
    print("\n🚀 " + "=" * 50)
    print("🚀 Backend服务初始化")
    print("=" * 52)
    
    if status['p2l_ready']:
        print("✅ 服务状态: 完全就绪")
        print("🎉 P2L模型已加载，所有功能可正常使用")
    else:
        print("⚠️  服务状态: 降级模式")
        print("💡 说明: P2L模型未准备就绪，部分功能可能受限")
        print("🔧 建议: python p2l_tools.py download")
    
    print("=" * 52 + "\n")

if __name__ == "__main__":
    # 直接运行时显示状态
    print_status()