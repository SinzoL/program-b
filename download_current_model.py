#!/usr/bin/env python3
"""
下载当前配置的默认P2L模型 - 使用新的模型管理系统
"""

from model_utils import ModelManager
from constants import DEFAULT_MODEL

def main():
    print("🚀 下载当前默认P2L模型")
    print("=" * 40)
    
    print(f"🎯 当前默认模型: {DEFAULT_MODEL}")
    
    manager = ModelManager()
    success = manager.download_model(DEFAULT_MODEL)
    
    if success:
        print("\n🎉 下载成功!")
        print("✅ 现在可以重启服务")
    else:
        print("\n❌ 下载失败，请检查网络连接")
    
    return success

if __name__ == "__main__":
    main()