#!/usr/bin/env python3
"""
P2L后端服务启动文件
统一的后端服务入口
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    print("🚀 P2L后端服务启动")
    print("=" * 50)
    
    # 使用统一的模型管理器检查模型
    from model_manager import ensure_p2l_model
    
    model_ready = ensure_p2l_model(force_check=True)
    
    if model_ready:
        print("✅ 模型检查完成，启动服务...")
    else:
        print("⚠️  模型未完全准备就绪，服务将以降级模式启动")
    
    print("=" * 50)
    
    # 启动服务
    from service import main
    main()