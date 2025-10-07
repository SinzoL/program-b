#!/usr/bin/env python3
"""
测试修复后的优先模式评分逻辑
验证不同优先模式下模型评分计算的差异
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from p2l_model_scorer import P2LModelScorer
from config import get_all_models

def test_mode_scoring_differences():
    """测试不同优先模式下的评分差异"""
    print("🧪 测试优先模式评分差异")
    print("=" * 80)
    
    # 获取模型配置
    model_configs = get_all_models()
    
    # 创建评分器
    scorer = P2LModelScorer(model_configs)
    
    # 使用固定的测试提示词
    test_prompt = "请帮我写一个复杂的机器学习算法来处理大规模数据"
    
    # 测试的模型（选择有代表性的几个）
    enabled_models = [
        "gpt-4o-2024-08-06",        # 高性能高成本
        "claude-3-5-sonnet-20241022", # 高性能高成本
        "gpt-4o-mini-2024-07-18",   # 中性能低成本
        "claude-3-haiku-20240307"    # 低性能低成本快速
    ]
    
    # 测试所有优先模式
    modes = ['performance', 'cost', 'speed', 'balanced']
    
    all_results = {}
    
    for mode in modes:
        print(f"\n🎯 测试模式: {mode.upper()}")
        print("-" * 60)
        
        try:
            rankings, routing_info = scorer.calculate_p2l_scores(
                prompt=test_prompt,
                priority=mode,
                enabled_models=enabled_models
            )
            
            all_results[mode] = {
                'rankings': rankings,
                'routing_info': routing_info
            }
            
            print(f"✅ {mode}模式排名:")
            for i, ranking in enumerate(rankings[:4], 1):
                model_name = ranking['model']
                adjusted_score = ranking['score']
                p2l_coef = ranking['p2l_coefficient']
                cost = ranking['cost_per_1k']
                response_time = ranking['avg_response_time']
                
                print(f"  {i}. {model_name}")
                print(f"     综合评分: {adjusted_score:.4f}")
                print(f"     P2L系数: {p2l_coef:.4f}")
                print(f"     成本: ${cost:.4f}/1k")
                print(f"     响应时间: {response_time:.1f}s")
                
        except Exception as e:
            print(f"❌ {mode}模式测试失败: {e}")
            all_results[mode] = {'error': str(e)}
    
    # 分析评分差异
    print("\n" + "=" * 80)
    print("📊 评分差异分析")
    print("=" * 80)
    
    # 检查每个模型在不同模式下的排名变化
    model_rankings = {}
    
    for mode, result in all_results.items():
        if 'rankings' in result:
            for i, ranking in enumerate(result['rankings']):
                model_name = ranking['model']
                if model_name not in model_rankings:
                    model_rankings[model_name] = {}
                model_rankings[model_name][mode] = {
                    'rank': i + 1,
                    'score': ranking['score'],
                    'p2l_coef': ranking['p2l_coefficient']
                }
    
    print("🏆 各模型在不同模式下的排名:")
    print(f"{'模型':<30} {'性能模式':<12} {'成本模式':<12} {'速度模式':<12} {'平衡模式':<12}")
    print("-" * 90)
    
    for model_name, mode_data in model_rankings.items():
        row = f"{model_name[:28]:<30}"
        for mode in modes:
            if mode in mode_data:
                rank = mode_data[mode]['rank']
                score = mode_data[mode]['score']
                row += f" #{rank}({score:.3f})"
                row += " " * (12 - len(f"#{rank}({score:.3f})"))
            else:
                row += " N/A        "
        print(row)
    
    # 检查评分变化程度
    print(f"\n📈 评分变化分析:")
    
    for model_name, mode_data in model_rankings.items():
        scores = [mode_data[mode]['score'] for mode in modes if mode in mode_data]
        if len(scores) >= 2:
            score_range = max(scores) - min(scores)
            score_std = np.std(scores)
            print(f"  {model_name[:30]}: 评分范围={score_range:.4f}, 标准差={score_std:.4f}")
    
    # 检查推荐模型的多样性
    recommended_models = []
    for mode, result in all_results.items():
        if 'rankings' in result and result['rankings']:
            recommended_models.append((mode, result['rankings'][0]['model']))
    
    print(f"\n🎯 推荐模型多样性:")
    unique_recommendations = set([model for _, model in recommended_models])
    
    for mode, model in recommended_models:
        print(f"  {mode:12}: {model}")
    
    print(f"\n📊 总结:")
    print(f"  测试模式数: {len(modes)}")
    print(f"  成功测试数: {len([r for r in all_results.values() if 'rankings' in r])}")
    print(f"  推荐模型种类: {len(unique_recommendations)}")
    
    if len(unique_recommendations) == 1:
        print(f"  ⚠️  所有模式都推荐同一模型: {list(unique_recommendations)[0]}")
        print(f"  💡 建议: 增加权重差异或调整评分算法")
    elif len(unique_recommendations) == len(modes):
        print(f"  ✅ 理想情况: 每个模式推荐不同模型")
    else:
        print(f"  🔄 部分差异: {len(unique_recommendations)}/{len(modes)} 个不同推荐")
    
    return all_results

def test_weight_sensitivity():
    """测试权重敏感性"""
    print("\n🧪 测试权重敏感性")
    print("=" * 80)
    
    # 模拟不同的模型数据
    model_list = ["model_a", "model_b", "model_c"]
    p2l_coefficients = np.array([0.8, 0.5, 0.3])  # A最高P2L
    
    model_configs = {
        "model_a": {"cost_per_1k": 0.03, "avg_response_time": 3.0},  # 高成本慢速
        "model_b": {"cost_per_1k": 0.015, "avg_response_time": 2.0}, # 中成本中速
        "model_c": {"cost_per_1k": 0.001, "avg_response_time": 1.0}  # 低成本快速
    }
    
    from p2l_router import P2LRouter
    router = P2LRouter()
    
    modes = ['performance', 'cost', 'speed', 'balanced']
    
    print("🔍 权重敏感性测试:")
    print(f"{'模式':<12} {'Model A':<15} {'Model B':<15} {'Model C':<15} {'推荐':<10}")
    print("-" * 70)
    
    for mode in modes:
        adjusted_scores = router._calculate_mode_adjusted_scores(
            p2l_coefficients, model_list, model_configs, mode
        )
        
        recommended_idx = np.argmax(adjusted_scores)
        recommended_model = model_list[recommended_idx]
        
        row = f"{mode:<12}"
        for i, score in enumerate(adjusted_scores):
            row += f" {score:.4f}        "
        row += f" {recommended_model}"
        
        print(row)
    
    print("\n💡 权重敏感性分析:")
    print("  - performance模式应该推荐Model A (最高P2L)")
    print("  - cost模式应该推荐Model C (最低成本)")
    print("  - speed模式应该推荐Model C (最快响应)")
    print("  - balanced模式应该综合考虑所有因素")

def main():
    """主函数"""
    print("🚀 优先模式评分差异测试")
    print("=" * 80)
    
    # 测试实际评分差异
    results = test_mode_scoring_differences()
    
    # 测试权重敏感性
    test_weight_sensitivity()
    
    print("\n" + "=" * 80)
    print("📋 测试完成")
    print("=" * 80)
    print("✅ 优先模式评分差异测试完成")
    print("💡 如果仍然存在问题，可能需要:")
    print("   1. 调整权重设置，增加差异")
    print("   2. 检查P2L系数的分布范围")
    print("   3. 优化标准化算法")

if __name__ == "__main__":
    main()