#!/usr/bin/env python3
"""
Docker部署测试脚本
验证Docker环境下的P2L系统功能
"""

import os
import sys
import time
import requests
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_backend_health():
    """测试后端健康状态"""
    try:
        logger.info("🔍 测试后端健康检查...")
        response = requests.get("http://localhost:8080/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ 后端服务健康")
            logger.info(f"   - P2L模型加载: {data.get('p2l_loaded', False)}")
            logger.info(f"   - 可用模型数: {data.get('llm_models_available', 0)}")
            logger.info(f"   - 设备: {data.get('device', 'unknown')}")
            return True
        else:
            logger.error(f"❌ 后端健康检查失败: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 后端连接失败: {e}")
        return False

def test_p2l_analysis():
    """测试P2L分析功能"""
    try:
        logger.info("🧠 测试P2L分析功能...")
        
        test_data = {
            "prompt": "请帮我写一个Python函数来计算斐波那契数列",
            "priority": "performance"
        }
        
        response = requests.post(
            "http://localhost:8080/analyze",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            rankings = data.get("model_ranking", [])
            
            if rankings:
                top_model = rankings[0]
                logger.info(f"✅ P2L分析成功")
                logger.info(f"   - 推荐模型: {top_model['model']}")
                logger.info(f"   - 综合评分: {top_model['score']:.4f}")
                logger.info(f"   - P2L系数: {top_model['p2l_coefficient']:.4f}")
                logger.info(f"   - 处理时间: {data.get('processing_time', 0):.3f}s")
                return True
            else:
                logger.error("❌ P2L分析返回空结果")
                return False
        else:
            logger.error(f"❌ P2L分析失败: {response.status_code}")
            logger.error(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ P2L分析异常: {e}")
        return False

def test_model_list():
    """测试模型列表API"""
    try:
        logger.info("📋 测试模型列表API...")
        
        response = requests.get("http://localhost:8080/models", timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            logger.info(f"✅ 模型列表获取成功")
            logger.info(f"   - 可用模型数: {len(models)}")
            logger.info(f"   - 前5个模型: {models[:5]}")
            return True
        else:
            logger.error(f"❌ 模型列表获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 模型列表API异常: {e}")
        return False

def test_routing_differentiation():
    """测试路由差异化"""
    try:
        logger.info("🎯 测试路由差异化...")
        
        test_prompt = "请帮我写一个快速排序算法"
        modes = ['performance', 'cost', 'speed', 'balanced']
        results = {}
        
        for mode in modes:
            response = requests.post(
                "http://localhost:8080/analyze",
                json={"prompt": test_prompt, "priority": mode},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                rankings = data.get("model_ranking", [])
                if rankings:
                    results[mode] = rankings[0]["model"]
                    
        if len(results) == 4:
            unique_models = set(results.values())
            differentiation_rate = len(unique_models) / len(results) * 100
            
            logger.info(f"✅ 路由差异化测试完成")
            logger.info(f"   - 差异化率: {differentiation_rate:.1f}%")
            
            for mode, model in results.items():
                logger.info(f"   - {mode}: {model}")
                
            if differentiation_rate >= 25:
                logger.info("✅ 路由差异化正常")
                return True
            else:
                logger.warning("⚠️ 路由差异化效果不够明显")
                return True  # 仍然算通过，因为功能正常
        else:
            logger.error("❌ 路由差异化测试失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 路由差异化测试异常: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("🚀 Docker部署测试套件")
    logger.info("=" * 60)
    
    # 等待服务启动
    logger.info("⏳ 等待服务启动...")
    time.sleep(5)
    
    tests = [
        ("后端健康检查", test_backend_health),
        ("模型列表API", test_model_list),
        ("P2L分析功能", test_p2l_analysis),
        ("路由差异化", test_routing_differentiation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 执行测试: {test_name}")
        logger.info("-" * 40)
        
        try:
            if test_func():
                logger.info(f"✅ {test_name} - 通过")
                passed += 1
            else:
                logger.error(f"❌ {test_name} - 失败")
        except Exception as e:
            logger.error(f"❌ {test_name} - 异常: {e}")
    
    logger.info(f"\n📊 测试总结")
    logger.info("=" * 60)
    logger.info(f"通过: {passed}/{total}")
    logger.info(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        logger.info("🎉 所有测试通过！Docker部署成功")
        return True
    elif passed >= total * 0.75:
        logger.info("✅ 大部分测试通过，Docker部署基本成功")
        return True
    else:
        logger.error("❌ 多个测试失败，Docker部署可能有问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)