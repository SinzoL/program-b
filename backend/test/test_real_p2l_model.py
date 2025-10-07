#!/usr/bin/env python3
"""
测试真实P2L模型引擎
使用下载的p2l-135m-grk模型进行Bradley-Terry系数计算
"""

import asyncio
import json
import sys
import os
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加backend目录到Python路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# 添加p2l项目路径
p2l_dir = os.path.join(os.path.dirname(backend_dir), 'p2l')
sys.path.insert(0, p2l_dir)

async def test_real_p2l_model():
    """测试真实P2L模型的完整流程"""
    
    print("🚀 真实P2L模型测试")
    print("=" * 80)
    
    try:
        # 导入P2L引擎
        from p2l_engine import P2LEngine
        from config import get_all_models
        
        print("✅ 模块导入成功")
        
        # 创建P2L引擎
        print("🔍 正在加载P2L模型...")
        engine = P2LEngine()
        
        print("✅ 真实P2L模型引擎创建成功！")
        
        # 显示模型信息
        model_info = engine.get_model_info()
        print(f"\n📊 【P2L模型信息】")
        for key, value in model_info.items():
            if isinstance(value, list):
                print(f"   {key}: {len(value)} 项")
                for item in value[:3]:  # 只显示前3项
                    print(f"     - {item}")
                if len(value) > 3:
                    print(f"     ... 还有 {len(value) - 3} 项")
            else:
                print(f"   {key}: {value}")
        
        # 获取我们配置的模型
        our_models = get_all_models()
        our_model_names = list(our_models.keys())
        
        print(f"\n📋 【模型对比】")
        print(f"我们配置的模型: {len(our_model_names)} 个")
        print(f"P2L支持的模型: {len(engine.get_supported_models())} 个")
        
        # 检查我们的模型哪些被P2L支持
        supported_models = []
        unsupported_models = []
        
        for model_name in our_model_names:
            if engine.check_model_support(model_name):
                supported_models.append(model_name)
            else:
                unsupported_models.append(model_name)
        
        print(f"✅ 被P2L支持的模型: {len(supported_models)} 个")
        for model in supported_models[:5]:  # 显示前5个
            print(f"   - {model}")
        if len(supported_models) > 5:
            print(f"   ... 还有 {len(supported_models) - 5} 个")
        
        if unsupported_models:
            print(f"⚠️ 不被P2L支持的模型: {len(unsupported_models)} 个")
            for model in unsupported_models[:3]:  # 显示前3个
                print(f"   - {model}")
            if len(unsupported_models) > 3:
                print(f"   ... 还有 {len(unsupported_models) - 3} 个")
        
        # 测试不同类型的提示词
        test_cases = [
            {
                "prompt": "写一个Python快速排序算法，要求代码简洁高效",
                "description": "编程任务",
                "models": supported_models[:6] if len(supported_models) >= 6 else supported_models
            },
            {
                "prompt": "请解释量子计算的基本原理，包括量子比特、叠加态和纠缠现象",
                "description": "科学解释",
                "models": supported_models[:5] if len(supported_models) >= 5 else supported_models
            },
            {
                "prompt": "帮我翻译这段话：The future of artificial intelligence is bright.",
                "description": "翻译任务",
                "models": supported_models[:4] if len(supported_models) >= 4 else supported_models
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            if not test_case["models"]:
                print(f"\n⚠️ 跳过测试用例 {i}：没有支持的模型")
                continue
                
            print(f"\n" + "🧪" + "=" * 79)
            print(f"🧪 测试用例 {i}: {test_case['description']}")
            print(f"📝 提示词: {test_case['prompt']}")
            print(f"🎯 测试模型: {len(test_case['models'])} 个")
            print("🧪" + "=" * 79)
            
            try:
                # 使用真实P2L模型计算系数
                print(f"🔍 正在使用真实P2L模型计算Bradley-Terry系数...")
                
                coefficients = engine.get_coefficients_for_prompt(
                    prompt=test_case["prompt"],
                    models=test_case["models"]
                )
                
                print(f"✅ P2L推理完成！")
                print(f"📊 计算了 {len(coefficients.model_coefficients)} 个模型的系数")
                print(f"🎯 Eta参数: {coefficients.eta}")
                print(f"🎯 Gamma参数: {coefficients.gamma}")
                
                # 获取排名
                rankings = engine.get_model_rankings(coefficients)
                
                print(f"\n🏆 【模型排名】(基于真实P2L系数)")
                for j, (model, coef) in enumerate(rankings[:5], 1):
                    confidence = coefficients.confidence_scores.get(model, 0.5)
                    print(f"   {j}. {model}")
                    print(f"      Bradley-Terry系数: {coef:.4f}")
                    print(f"      置信度分数: {confidence:.3f}")
                
                # 计算前两名的对战概率
                if len(rankings) >= 2:
                    model_a, coef_a = rankings[0]
                    model_b, coef_b = rankings[1]
                    
                    probs = engine.calculate_win_probabilities(
                        coefficients, 
                        [(model_a, model_b)]
                    )
                    
                    prob_data = probs[(model_a, model_b)]
                    
                    print(f"\n🆚 【对战分析】{model_a} vs {model_b}")
                    print(f"   {model_a} 胜率: {prob_data['win']:.1%}")
                    print(f"   {model_b} 胜率: {prob_data['lose']:.1%}")
                    print(f"   平局概率: {prob_data['tie']:.1%}")
                    print(f"   双方都不好: {prob_data['tie_bothbad']:.1%}")
                
                # 获取调试信息
                debug_info = engine.get_debug_info(test_case["prompt"], test_case["models"])
                print(f"\n🐛 【调试信息】")
                print(f"   模型设备: {debug_info['model_device']}")
                print(f"   模型精度: {debug_info['model_dtype']}")
                print(f"   提示词长度: {debug_info['prompt_length']}")
                print(f"   处理模型数: {debug_info['model_count']}")
                
            except Exception as e:
                print(f"❌ 测试用例 {i} 失败: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n" + "=" * 80)
        print(f"🎉 真实P2L模型测试完成！")
        print(f"💡 现在你可以看到真正的P2L Bradley-Terry系数了")
        print(f"🚀 这些系数是由训练好的P2L模型根据提示词动态计算的")
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print(f"💡 请确保P2L项目路径正确，并且已安装所需依赖")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 真实P2L模型测试套件")
    print("🎯 此脚本将使用下载的p2l-135m-grk模型进行真实的Bradley-Terry系数计算")
    print("=" * 80)
    
    # 运行测试
    asyncio.run(test_real_p2l_model())
    
    print(f"\n🎯 测试完成！")
    print(f"💡 如果测试成功，说明真实P2L模型已经可以正常工作")