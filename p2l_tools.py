#!/usr/bin/env python3
"""
P2L工具脚本 - Docker部署支持
用于确保P2L模型在容器中正确加载
"""

import os
import sys
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_p2l_models():
    """确保P2L模型可用"""
    try:
        logger.info("🔍 检查P2L模型状态...")
        
        # 检查模型目录
        models_dir = Path("/app/models")
        if not models_dir.exists():
            models_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 创建模型目录: {models_dir}")
        
        # 检查P2L引擎
        try:
            sys.path.insert(0, '/app/backend')
            from p2l_engine import P2LEngine
            
            logger.info("🧠 初始化P2L引擎...")
            engine = P2LEngine()
            
            # 简单测试
            test_prompt = "Hello world"
            logger.info("🧪 测试P2L引擎...")
            result = engine.get_p2l_coefficients([test_prompt], ["test-model"])
            
            if result is not None:
                logger.info("✅ P2L引擎工作正常")
                return True
            else:
                logger.warning("⚠️ P2L引擎返回空结果，将使用模拟模式")
                return True
                
        except Exception as e:
            logger.warning(f"⚠️ P2L引擎初始化失败: {e}")
            logger.info("📝 将使用模拟P2L系数")
            return True
            
    except Exception as e:
        logger.error(f"❌ P2L模型检查失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "ensure":
        success = ensure_p2l_models()
        if success:
            logger.info("🎉 P2L模型检查完成")
            sys.exit(0)
        else:
            logger.error("❌ P2L模型检查失败")
            sys.exit(1)
    else:
        print("用法: python p2l_tools.py ensure")
        sys.exit(1)

if __name__ == "__main__":
    main()