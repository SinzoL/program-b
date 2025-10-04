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
        print("✅ huggingface_hub 已安装")
    except ImportError:
        print("📦 安装huggingface_hub...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
                "huggingface_hub"
            ])
            print("✅ 依赖安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            print("💡 尝试使用默认源...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "huggingface_hub"
                ])
                print("✅ 依赖安装成功（默认源）")
            except subprocess.CalledProcessError:
                print("❌ 依赖安装彻底失败")
                return False
    return True

def main():
    """主函数"""
    print("🚀 P2L模型检查工具")
    print("=" * 40)
    
    # 安装依赖
    if not install_dependencies():
        print("⚠️  依赖安装失败，但继续尝试模型检查...")
    
    # 创建模型管理器
    manager = ModelManager()
    
    # 先检查模型是否已存在
    from constants import DEFAULT_MODEL
    if manager.check_model_exists(DEFAULT_MODEL):
        print(f"✅ 默认模型 {DEFAULT_MODEL} 已存在")
        print("🎉 模型检查完成!")
        print("✅ 服务可以正常启动")
        sys.exit(0)
    
    # 模型不存在，尝试下载
    print(f"⚠️  默认模型 {DEFAULT_MODEL} 不存在，尝试下载...")
    
    # 检查网络连接
    try:
        import urllib.request
        urllib.request.urlopen('https://huggingface.co', timeout=10)
        print("✅ 网络连接正常")
    except Exception as e:
        print(f"⚠️  网络连接可能有问题: {e}")
        print("💡 如果下载失败，请检查网络或手动下载模型")
    
    # 尝试下载模型
    success = manager.ensure_default_model()
    
    if success:
        print("\n🎉 模型下载完成!")
        print("✅ 服务可以正常启动")
        sys.exit(0)
    else:
        print("\n❌ 模型下载失败!")
        print("💡 请检查网络连接或手动下载模型")
        print("💡 建议运行: python download_current_model.py")
        sys.exit(1)  # 退出并报错

if __name__ == "__main__":
    main()