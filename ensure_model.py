#!/usr/bin/env python3
"""
确保P2L模型存在的脚本
在启动服务前运行，确保默认模型已下载
"""

import sys
import subprocess
from model_utils import ModelManager

def install_dependencies():
    """安装必要的依赖"""
    try:
        import huggingface_hub
    except ImportError:
        print("📦 安装huggingface_hub...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "huggingface_hub"
            ])
            print("✅ 依赖安装成功")
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败")
            return False
    return True

def main():
    """主函数"""
    print("🚀 P2L模型检查工具")
    print("=" * 40)
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 创建模型管理器
    manager = ModelManager()
    
    # 检查并确保默认模型存在
    success = manager.ensure_default_model()
    
    if success:
        print("\n🎉 模型检查完成!")
        print("✅ 服务可以正常启动")
        sys.exit(0)
    else:
        print("\n❌ 模型检查失败!")
        print("💡 请检查网络连接或手动下载模型")
        sys.exit(1)

if __name__ == "__main__":
    main()