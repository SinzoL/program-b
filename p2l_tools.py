#!/usr/bin/env python3
"""
P2L工具脚本集合
提供所有模型管理的便捷命令行工具
"""

import sys
import argparse
from p2l_core import get_manager, DEFAULT_MODEL

def cmd_check():
    """检查P2L模型状态"""
    print("🔍 P2L模型状态检查")
    manager = get_manager()
    manager.print_status()

def cmd_download(model_name=None, force=False):
    """下载P2L模型"""
    if model_name is None:
        model_name = DEFAULT_MODEL
    
    print(f"🚀 下载P2L模型: {model_name}")
    print("=" * 40)
    
    manager = get_manager()
    success = manager.download_model(model_name, force=force)
    
    if success:
        print("\n🎉 下载成功!")
        print("✅ 现在可以重启服务")
    else:
        print("\n❌ 下载失败，请检查网络连接")
    
    return success

def cmd_ensure():
    """确保默认模型存在（用于服务启动前检查）"""
    manager = get_manager()
    success = manager.ensure_default_model()
    
    if success:
        print("✅ 服务可以正常启动")
        sys.exit(0)
    else:
        print("❌ 模型准备失败!")
        print("💡 建议运行: python p2l_tools.py download")
        sys.exit(1)

def cmd_list():
    """列出所有可用模型"""
    from p2l_core import MODEL_MAPPING
    
    print("📋 可用的P2L模型:")
    print("=" * 50)
    
    for model_name, config in MODEL_MAPPING.items():
        manager = get_manager()
        exists = manager.check_model_exists(model_name)
        status = "✅ 已下载" if exists else "⬜ 未下载"
        
        print(f"{status} {model_name}")
        print(f"    📊 参数量: {config['parameters']}")
        print(f"    💾 内存需求: {config['memory_required']}MB")
        print(f"    📝 描述: {config['description']}")
        print()

def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(
        description="P2L模型管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python p2l_tools.py check              # 检查模型状态
  python p2l_tools.py download           # 下载默认模型
  python p2l_tools.py download --force   # 强制重新下载
  python p2l_tools.py ensure             # 确保模型存在（用于脚本）
  python p2l_tools.py list               # 列出所有模型
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # check命令
    subparsers.add_parser('check', help='检查模型状态')
    
    # download命令
    download_parser = subparsers.add_parser('download', help='下载模型')
    download_parser.add_argument('--model', help='指定模型名称（默认为当前配置的模型）')
    download_parser.add_argument('--force', action='store_true', help='强制重新下载')
    
    # ensure命令
    subparsers.add_parser('ensure', help='确保默认模型存在（用于服务启动前检查）')
    
    # list命令
    subparsers.add_parser('list', help='列出所有可用模型')
    
    args = parser.parse_args()
    
    if args.command == 'check':
        cmd_check()
    elif args.command == 'download':
        cmd_download(args.model, args.force)
    elif args.command == 'ensure':
        cmd_ensure()
    elif args.command == 'list':
        cmd_list()
    else:
        # 没有指定命令时，显示帮助和状态
        parser.print_help()
        print("\n" + "="*50)
        cmd_check()

if __name__ == "__main__":
    main()