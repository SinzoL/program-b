#!/usr/bin/env python3
"""
测试所有模型排名显示
验证P2L分析是否返回所有9个模型的分数
"""

import requests
import json

def test_all_models_ranking():
    """测试所有模型排名"""
    print("🧪 测试所有模型排名显示...")
    
    try:
        # 发送P2L分析请求
        url = "http://localhost:8080/api/p2l/analyze"
        data = {
            "prompt": "展示js实现字符串中下划线转化为驼峰",
            "mode": "balanced",
            "models": ["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet-20241022", "gemini-1.5-pro", 
                      "deepseek-chat", "deepseek-coder", "qwen2.5-72b-instruct", "qwen-plus", "qwen-turbo"]
        }
        
        response = requests.post(url, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            recommendations = result.get('recommendations', [])
            
            print(f"✅ P2L分析成功")
            print(f"📊 返回的模型数量: {len(recommendations)}")
            print(f"🎯 推荐的模型: {result.get('recommended_model', 'unknown')}")
            
            print(f"\n🏆 完整模型排名:")
            for i, rec in enumerate(recommendations, 1):
                model_name = rec.get('model', 'unknown')
                score = rec.get('score', 0)
                print(f"   {i:2d}. {model_name:<30} {score:5.1f}分")
            
            # 检查是否包含所有期望的模型
            expected_models = {
                "gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet-20241022", 
                "gemini-1.5-pro", "deepseek-chat", "deepseek-coder", 
                "qwen2.5-72b-instruct", "qwen-plus", "qwen-turbo"
            }
            
            returned_models = {rec.get('model') for rec in recommendations}
            missing_models = expected_models - returned_models
            extra_models = returned_models - expected_models
            
            if missing_models:
                print(f"\n⚠️ 缺失的模型: {missing_models}")
            
            if extra_models:
                print(f"\n➕ 额外的模型: {extra_models}")
            
            if len(recommendations) == 9 and not missing_models:
                print(f"\n🎉 成功！返回了所有9个模型的排名")
                return True
            else:
                print(f"\n❌ 失败！期望9个模型，实际返回{len(recommendations)}个")
                return False
            
        else:
            print(f"❌ P2L分析失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_frontend_display():
    """测试前端是否正确显示所有模型"""
    print("\n🧪 测试前端模型显示...")
    
    try:
        # 模拟前端获取推荐结果
        url = "http://localhost:8080/api/p2l/analyze"
        data = {
            "prompt": "写一个Python函数计算斐波那契数列",
            "mode": "performance",
            "models": ["gpt-4o", "claude-3-5-sonnet-20241022", "qwen-plus"]  # 只启用3个模型
        }
        
        response = requests.post(url, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            recommendations = result.get('recommendations', [])
            
            print(f"✅ 前端测试成功")
            print(f"📊 启用3个模型，返回的模型数量: {len(recommendations)}")
            
            if len(recommendations) == 9:
                print(f"🎉 成功！即使只启用3个模型，仍然返回了所有9个模型的排名")
                return True
            else:
                print(f"❌ 失败！应该返回所有9个模型，实际返回{len(recommendations)}个")
                return False
            
        else:
            print(f"❌ 前端测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 前端测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 所有模型排名显示测试\n")
    
    results = []
    
    # 测试所有模型排名
    results.append(test_all_models_ranking())
    
    # 测试前端显示
    results.append(test_frontend_display())
    
    # 汇总结果
    print(f"\n📊 测试结果:")
    print(f"✅ 成功: {sum(results)}/{len(results)}")
    print(f"❌ 失败: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 所有测试通过！前端现在应该显示全部9个模型的排名。")
    else:
        print("\n⚠️ 部分测试失败，请检查配置")

if __name__ == "__main__":
    main()