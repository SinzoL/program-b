#!/usr/bin/env python3
"""
测试前端模型配置是否正确
"""

import requests
import json

def test_frontend_models():
    """测试前端可用的模型列表"""
    print("🧪 测试前端模型配置...")
    
    try:
        # 模拟前端发送的分析请求
        url = "http://localhost:8080/api/p2l/analyze"
        data = {
            "prompt": "测试千问模型",
            "mode": "balanced",
            "models": ["qwen-plus", "qwen2.5-72b-instruct", "qwen-turbo"]
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ P2L分析成功")
            print(f"📊 推荐模型数量: {len(result.get('recommendations', []))}")
            
            # 检查推荐的模型
            for rec in result.get('recommendations', []):
                model_name = rec.get('model', 'unknown')
                score = rec.get('score', 0)
                print(f"   • {model_name}: {score:.3f}")
            
            return True
        else:
            print(f"❌ P2L分析失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_qwen_plus_call():
    """测试qwen-plus模型调用"""
    print("\n🧪 测试qwen-plus模型调用...")
    
    try:
        url = "http://localhost:8080/api/llm/generate"
        data = {
            "model": "qwen-plus",
            "prompt": "展示js实现字符串中下划线转化为驼峰",
            "max_tokens": 200
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ qwen-plus调用成功")
            print(f"📝 响应: {result.get('response', '')[:100]}...")
            print(f"📊 Token数: {result.get('tokens', 0)}")
            print(f"💰 成本: ${result.get('cost', 0):.4f}")
            print(f"🏷️ 提供商: {result.get('provider', 'unknown')}")
            print(f"🔧 真实API: {result.get('is_real_api', False)}")
            return True
        else:
            print(f"❌ qwen-plus调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 前端模型配置测试\n")
    
    results = []
    
    # 测试P2L分析
    results.append(test_frontend_models())
    
    # 测试qwen-plus调用
    results.append(test_qwen_plus_call())
    
    # 汇总结果
    print(f"\n📊 测试结果:")
    print(f"✅ 成功: {sum(results)}/{len(results)}")
    print(f"❌ 失败: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 前端模型配置测试全部通过！")
        print("现在可以在前端正常使用qwen-plus模型了。")
    else:
        print("\n⚠️ 部分测试失败，请检查配置")

if __name__ == "__main__":
    main()