#!/usr/bin/env python3
"""
P2L模型管理工具
独立的模型检查、下载和管理模块
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional, List

# 导入项目常量
from constants import DEFAULT_MODEL, MODEL_MAPPING

class ModelManager:
    """P2L模型管理器"""
    
    def __init__(self):
        # 智能检测环境，支持Docker容器
        if os.path.exists('/app') and os.getcwd().startswith('/app'):
            # Docker容器环境
            self.models_dir = Path("/app/models")
        else:
            # 本地开发环境
            self.models_dir = Path("models")
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
    
    def download_model(self, model_name: str) -> bool:
        """下载指定模型"""
        config = self.get_model_config(model_name)
        if not config:
            print(f"❌ 未找到模型配置: {model_name}")
            return False
        
        model_path = self.get_model_path(model_name)
        
        # 检查是否已存在
        if self.check_model_exists(model_name):
            print(f"✅ 模型已存在: {model_path}")
            return True
        
        print(f"🚀 开始下载模型: {model_name}")
        print(f"📦 仓库地址: {config['repo_id']}")
        print(f"💾 本地路径: {model_path}")
        print(f"📊 模型参数: {config['parameters']}")
        print(f"💡 模型描述: {config['description']}")
        
        try:
            from huggingface_hub import snapshot_download
            
            start_time = time.time()
            
            # 下载模型
            snapshot_download(
                repo_id=config['repo_id'],
                local_dir=str(model_path),
                local_dir_use_symlinks=False,
                resume_download=True
            )
            
            download_time = time.time() - start_time
            minutes = int(download_time // 60)
            seconds = int(download_time % 60)
            
            print(f"✅ 模型下载成功! 耗时: {minutes}分{seconds}秒")
            return True
            
        except ImportError:
            print("❌ 缺少依赖: pip install huggingface_hub")
            return False
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return False
    
    def ensure_default_model(self) -> bool:
        """确保默认模型存在"""
        print(f"🔍 检查默认模型: {DEFAULT_MODEL}")
        
        if self.check_model_exists(DEFAULT_MODEL):
            print("✅ 默认模型已存在")
            return True
        
        print("⚠️  默认模型不存在，开始下载...")
        return self.download_model(DEFAULT_MODEL)
    
    def list_available_models(self) -> List[str]:
        """列出所有可用的模型"""
        return list(MODEL_MAPPING.keys())
    
    def list_downloaded_models(self) -> List[str]:
        """列出已下载的模型"""
        downloaded = []
        for model_name in MODEL_MAPPING.keys():
            if self.check_model_exists(model_name):
                downloaded.append(model_name)
        return downloaded
    
    def get_model_status(self) -> Dict:
        """获取模型状态信息"""
        available = self.list_available_models()
        downloaded = self.list_downloaded_models()
        default_exists = self.check_model_exists(DEFAULT_MODEL)
        
        return {
            'default_model': DEFAULT_MODEL,
            'default_exists': default_exists,
            'available_models': available,
            'downloaded_models': downloaded,
            'total_available': len(available),
            'total_downloaded': len(downloaded)
        }
    
    def print_status(self):
        """打印模型状态"""
        status = self.get_model_status()
        
        print("\n" + "=" * 50)
        print("🚀 P2L模型状态")
        print("=" * 50)
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
            print(f"\n⚠️  建议运行: python ensure_model.py")
        
        print("=" * 50 + "\n")

def main():
    """主函数 - 用于测试"""
    manager = ModelManager()
    manager.print_status()

if __name__ == "__main__":
    main()