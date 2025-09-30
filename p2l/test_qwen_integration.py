#!/usr/bin/env python3
"""
测试千问API集成
验证千问模型在整个系统中的集成情况
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

async def test_qwen_llm_client():
    """测试LLM客户端中的千问支持"""
    print("🧪 测试LLM客户端中的千问支持...")
    
    try:
        from llm_client import LLMClient
        
        async with LLMClient() as client:
            response = await client.generate_response(
                model='qwen2.5-72b-instruct',
                prompt='你好，请简单介绍一下你自己',
                max_tokens=200
            )
            
            print(f"✅ LLM客户端测试成功")
            print(f"📝 响应: {response.content[:100]}...")
            print(f"📊 Token数: {response.tokens_used}, 成本: ${response.cost:.4f}")
            print(f"🏷️ 提供商: {response.provider}")
            return True
            
    except Exception as e:
        print(f"❌ LLM客户端测试失败: {e}")
        return False

def test_simple_qwen_client():
    """测试简单千问客户端"""
    print("\n🧪 测试简单千问客户端...")
    
    try:
        from simple_qwen_client import SimpleQwenClient
        
        client = SimpleQwenClient()
        if not client.api_key:
            print("❌ 千问API密钥未配置")
            return False
            
        response = client.generate_response(
            model='qwen2.5-72b-instruct',
            prompt='写一个Python函数计算斐波那契数列',
            max_tokens=300
        )
        
        print(f"✅ 简单客户端测试成功")
        print(f"📝 响应: {response['content'][:100]}...")
        print(f"📊 Token数: {response['tokens']}, 成本: ${response['cost']:.4f}")
        print(f"🏷️ 提供商: {response['provider']}")
        return True
        
    except Exception as e:
        print(f"❌ 简单客户端测试失败: {e}")
        return False

def test_backend_service_config():
    """测试后端服务配置"""
    print("\n🧪 测试后端服务配置...")
    
    try:
        from backend_service import P2LBackendService
        
        service = P2LBackendService()
        
        # 检查千问模型配置
        qwen_models = [model for model in service.model_configs.keys() if model.startswith('qwen')]
        
        if qwen_models:
            print(f"✅ 发现千问模型配置: {qwen_models}")
            
            for model in qwen_models:
                config = service.model_configs[model]
                print(f"📋 {model}: 提供商={config['provider']}, 成本=${config['cost_per_1k']}/1K tokens")
            
            return True
        else:
            print("❌ 未找到千问模型配置")
            return False
            
    except Exception as e:
        print(f"❌ 后端服务配置测试失败: {e}")
        return False

def test_p2l_inference_config():
    """测试P2L推理引擎配置"""
    print("\n🧪 测试P2L推理引擎配置...")
    
    try:
        from p2l.p2l_inference import P2LInferenceEngine
        
        # 创建推理引擎实例
        engine = P2LInferenceEngine()
        
        # 检查千问模型配置
        qwen_models = [model for model in engine.model_configs.keys() if model.startswith('qwen')]
        
        if qwen_models:
            print(f"✅ P2L推理引擎中发现千问模型: {qwen_models}")
            
            for model in qwen_models:
                config = engine.model_configs[model]
                print(f"📋 {model}: 提供商={config['provider']}, 质量分数={config['quality_score']}")
            
            return True
        else:
            print("❌ P2L推理引擎中未找到千问模型配置")
            return False
            
    except Exception as e:
        print(f"❌ P2L推理引擎配置测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始千问API集成测试...\n")
    
    results = []
    
    # 测试简单客户端
    results.append(test_simple_qwen_client())
    
    # 测试LLM客户端
    results.append(await test_qwen_llm_client())
    
    # 测试后端服务配置
    results.append(test_backend_service_config())
    
    # 测试P2L推理引擎配置
    results.append(test_p2l_inference_config())
    
    # 汇总结果
    print(f"\n📊 测试结果汇总:")
    print(f"✅ 成功: {sum(results)}/{len(results)}")
    print(f"❌ 失败: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 千问API集成测试全部通过！")
    else:
        print("\n⚠️ 部分测试失败，请检查配置")

if __name__ == "__main__":
    asyncio.run(main())