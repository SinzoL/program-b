#!/usr/bin/env python3
"""
完整的模型排序系统测试
验证从后端配置到前端显示的整个流程
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from model_p2l.model_configs import get_model_names, get_model_config
from p2l_router import P2LRouter

def test_backend_api_ordering():
    """测试后端API返回的模型顺序"""
    print("🧪 测试后端API模型排序")
    print("=" * 80)
    
    try:
        # 调用后端API
        response = requests.get("http://localhost:8080/models")
        
        if response.status_code != 200:
            print(f"❌ API调用失败: {response.status_code}")
            return False
        
        data = response.json()
        api_models = data.get("models", [])
        
        # 获取配置文件中的模型顺序
        config_models = get_model_names()
        
        print(f"📋 API返回模型数量: {len(api_models)}")
        print(f"📋 配置文件模型数量: {len(config_models)}")
        
        # 验证顺序一致性
        if api_models == config_models:
            print("✅ API返回的模型顺序与配置文件完全一致")
            
            # 显示前10个模型及其权重
            print(f"\n📊 前10个模型 (按采样权重排序):")
            for i, model_name in enumerate(api_models[:10]):
                config = get_model_config(model_name)
                weight = config.get("sampling_weight", 1)
                provider = config.get("provider", "unknown")
                verified = "✅" if config.get("verified", False) else "⚠️"
                print(f"  {i+1:2d}. {model_name:<35} 权重={weight} 提供商={provider} {verified}")
            
            return True
        else:
            print("❌ API返回的模型顺序与配置文件不一致")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务 (http://localhost:8080)")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_p2l_analysis_with_ordered_models():
    """测试P2L分析使用排序后的模型"""
    print("\n🧪 测试P2L分析模型排序")
    print("=" * 80)
    
    try:
        # 调用P2L分析API
        test_prompt = "如何实现一个高效的排序算法？"
        
        response = requests.post("http://localhost:8080/p2l/analyze", json={
            "prompt": test_prompt,
            "priority": "balanced"
        })
        
        if response.status_code != 200:
            print(f"❌ P2L分析API调用失败: {response.status_code}")
            return False
        
        data = response.json()
        recommendations = data.get("recommendations", [])
        
        if not recommendations:
            print("❌ 没有返回推荐结果")
            return False
        
        print(f"📊 P2L分析返回 {len(recommendations)} 个推荐模型")
        
        # 检查推荐结果是否按score排序
        scores = [rec.get("score", 0) for rec in recommendations]
        is_score_ordered = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
        
        print(f"🎯 推荐结果按score排序: {'✅ 正确' if is_score_ordered else '❌ 错误'}")
        
        # 显示前5个推荐结果
        print(f"\n📈 前5个推荐结果:")
        for i, rec in enumerate(recommendations[:5]):
            model = rec.get("model", "unknown")
            score = rec.get("score", 0)
            p2l_coeff = rec.get("p2l_coefficient", 0)
            config = get_model_config(model)
            weight = config.get("sampling_weight", 1)
            
            print(f"  {i+1}. {model:<35} score={score:.4f} P2L={p2l_coeff:.4f} 权重={weight}")
        
        return is_score_ordered
        
    except Exception as e:
        print(f"❌ P2L分析测试失败: {e}")
        return False

def test_sampling_weights_integration():
    """测试采样权重系统集成"""
    print("\n🧪 测试采样权重系统集成")
    print("=" * 80)
    
    router = P2LRouter()
    model_names = get_model_names()
    
    # 验证采样权重配置完整性
    missing_weights = []
    for model in model_names:
        if model not in router.SAMPLING_WEIGHTS:
            missing_weights.append(model)
    
    if missing_weights:
        print(f"❌ 发现 {len(missing_weights)} 个模型缺少采样权重配置:")
        for model in missing_weights:
            print(f"  - {model}")
        return False
    else:
        print(f"✅ 所有 {len(model_names)} 个模型都有采样权重配置")
    
    # 验证权重分布合理性
    weights = [router.SAMPLING_WEIGHTS[model] for model in model_names]
    weight_distribution = {}
    for weight in weights:
        weight_distribution[weight] = weight_distribution.get(weight, 0) + 1
    
    print(f"\n📊 采样权重分布:")
    for weight in sorted(weight_distribution.keys(), reverse=True):
        count = weight_distribution[weight]
        percentage = (count / len(model_names)) * 100
        print(f"  权重 {weight}: {count:2d} 个模型 ({percentage:5.1f}%)")
    
    # 检查是否有合理的权重梯度
    unique_weights = sorted(set(weights), reverse=True)
    has_gradient = len(unique_weights) >= 3  # 至少3个不同权重级别
    
    print(f"\n🎯 权重梯度检查: {'✅ 合理' if has_gradient else '❌ 不足'}")
    print(f"   权重级别数: {len(unique_weights)}")
    print(f"   权重范围: {min(weights)} - {max(weights)}")
    
    return has_gradient

def test_frontend_model_selector_order():
    """测试前端模型选择器的排序逻辑"""
    print("\n🧪 测试前端模型选择器排序")
    print("=" * 80)
    
    model_names = get_model_names()
    
    # 模拟前端模型选择器的逻辑
    frontend_models = []
    
    for name in model_names:
        config = get_model_config(name)
        
        # 模拟前端模型对象
        frontend_model = {
            "name": name,
            "provider": config.get("provider", "unknown"),
            "sampling_weight": config.get("sampling_weight", 1),
            "cost_per_1k": config.get("cost_per_1k", 0),
            "verified": config.get("verified", False),
            "avg_response_time": config.get("avg_response_time", 1.0)
        }
        frontend_models.append(frontend_model)
    
    # 检查前端模型是否按权重排序
    frontend_weights = [m["sampling_weight"] for m in frontend_models]
    is_ordered = all(frontend_weights[i] >= frontend_weights[i+1] for i in range(len(frontend_weights)-1))
    
    print(f"🎯 前端模型权重排序: {'✅ 正确' if is_ordered else '❌ 错误'}")
    
    # 模拟推荐配置选择
    recommended = []
    for model in frontend_models:
        # 推荐条件：权重>=4 且 已验证 且 成本合理
        if (model["sampling_weight"] >= 4 and 
            model["verified"] and 
            model["cost_per_1k"] <= 0.025):
            recommended.append(model)
    
    print(f"\n📋 推荐配置模型: {len(recommended)} 个")
    
    # 显示推荐配置的前5个模型
    for i, model in enumerate(recommended[:5]):
        print(f"  {i+1}. {model['name']:<35} 权重={model['sampling_weight']} 成本=${model['cost_per_1k']:.4f}")
    
    # 检查推荐模型是否按权重排序
    if recommended:
        rec_weights = [m["sampling_weight"] for m in recommended]
        rec_ordered = all(rec_weights[i] >= rec_weights[i+1] for i in range(len(rec_weights)-1))
        print(f"\n🎯 推荐模型排序: {'✅ 正确' if rec_ordered else '❌ 错误'}")
        return is_ordered and rec_ordered
    else:
        print("⚠️ 没有符合推荐条件的模型")
        return is_ordered

def test_different_priority_modes():
    """测试不同优先模式下的模型排序"""
    print("\n🧪 测试不同优先模式排序")
    print("=" * 80)
    
    test_prompt = "请帮我分析一下机器学习的发展趋势"
    modes = ["performance", "cost", "speed", "balanced"]
    
    results = {}
    
    for mode in modes:
        try:
            response = requests.post("http://localhost:8080/p2l/analyze", json={
                "prompt": test_prompt,
                "priority": mode
            })
            
            if response.status_code == 200:
                data = response.json()
                recommendations = data.get("recommendations", [])
                
                if recommendations:
                    # 获取前3个推荐模型
                    top3 = [rec.get("model") for rec in recommendations[:3]]
                    results[mode] = top3
                    
                    print(f"🎯 {mode:11} 模式前3名: {', '.join(top3[:2])}...")
                else:
                    print(f"❌ {mode} 模式没有返回推荐结果")
                    results[mode] = []
            else:
                print(f"❌ {mode} 模式API调用失败: {response.status_code}")
                results[mode] = []
                
        except Exception as e:
            print(f"❌ {mode} 模式测试失败: {e}")
            results[mode] = []
    
    # 检查不同模式是否产生不同的排序
    unique_rankings = set()
    for mode, ranking in results.items():
        if ranking:
            unique_rankings.add(tuple(ranking[:2]))  # 只比较前2名
    
    has_variation = len(unique_rankings) > 1
    print(f"\n🎯 不同模式产生不同排序: {'✅ 是' if has_variation else '❌ 否'}")
    
    return has_variation and len(results) == len(modes)

def main():
    """运行完整的模型排序系统测试"""
    print("🚀 完整模型排序系统测试套件")
    print("=" * 80)
    
    tests = [
        ("后端API模型排序", test_backend_api_ordering),
        ("P2L分析模型排序", test_p2l_analysis_with_ordered_models),
        ("采样权重系统集成", test_sampling_weights_integration),
        ("前端模型选择器排序", test_frontend_model_selector_order),
        ("不同优先模式排序", test_different_priority_modes)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试失败: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n📊 完整系统测试总结")
    print("=" * 80)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！模型排序系统完全正常工作")
        print("\n✨ 系统特性:")
        print("   - 模型按采样权重从高到低排序")
        print("   - 前端显示与后端配置一致")
        print("   - P2L分析结果按综合评分排序")
        print("   - 不同优先模式产生不同推荐")
        print("   - 采样权重系统完整集成")
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)