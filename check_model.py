#!/usr/bin/env python3
"""
检查P2L模型状态的脚本
快速查看模型下载情况
"""

from model_utils import ModelManager

def main():
    """主函数"""
    manager = ModelManager()
    manager.print_status()

if __name__ == "__main__":
    main()