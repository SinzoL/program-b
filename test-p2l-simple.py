#!/usr/bin/env python3
"""
简化版P2L模型测试脚本
专注于核心功能测试
"""

import sys
import os
import time

def main():
    print("🚀 P2L模型简化测试")
    print("=" * 40)
    
    # 1. 基础导入测试
    print("\n🔍 1. 测试基础模块导入")
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        
        # 设备检测
        if torch.cuda.is_available():
            device = torch.device('cuda')
            print(f"✅ 设备: CUDA - {torch.cuda.get_device_name()}")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = torch.device('mps')
            print("✅ 设备: MPS (Apple Silicon)")
        else:
            device = torch.device('cpu')
            print("✅ 设备: CPU")
            
    except Exception as e:
        print(f"❌ 基础导入失败: {e}")
        return
    
    # 2. 检查文件结构
    print("\n🔍 2. 检查文件结构")
    
    # 检查模型目录
    if os.path.exists("models/p2l-0.5b-grk"):
        print("✅ P2L模型目录存在")
        
        # 检查关键文件
        key_files = ["config.json", "training_config.json", "model.safetensors"]
        for file in key_files:
            file_path = f"models/p2l-0.5b-grk/{file}"
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"  ✅ {file} ({size:,} bytes)")
            else:
                print(f"  ❌ {file} 缺失")
    else:
        print("❌ P2L模型目录不存在")
        return
    
    # 检查P2L模块
    if os.path.exists("p2l"):
        print("✅ P2L模块目录存在")
    else:
        print("❌ P2L模块目录不存在")
        return
    
    # 3. 测试P2L模块导入
    print("\n🔍 3. 测试P2L模块导入")
    try:
        sys.path.insert(0, "p2l")
        from p2l.model import get_p2l_model, get_tokenizer
        print("✅ P2L模块导入成功")
    except Exception as e:
        print(f"❌ P2L模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. 测试P2L引擎
    print("\n🔍 4. 测试P2L引擎")
    try:
        sys.path.insert(0, "backend")
        from p2l_engine import P2LEngine
        
        print("✅ P2L引擎导入成功")
        
        # 初始化引擎
        print(f"🖥️  初始化引擎，设备: {device}")
        start_time = time.time()
        engine = P2LEngine(device)
        init_time = time.time() - start_time
        
        print(f"✅ P2L引擎初始化完成 (耗时: {init_time:.2f}s)")
        
        # 检查模型状态
        models_info = engine.get_loaded_models()
        print("\n📊 模型加载状态:")
        for key, value in models_info.items():
            print(f"  {key}: {value}")
        
        # 判断P2L模型是否正确加载
        p2l_models = models_info.get('p2l_models', [])
        total_models = models_info.get('total_models_loaded', 0)
        
        if total_models > 0 and p2l_models:
            print("🎉 P2L模型加载成功！")
            print(f"  已加载模型: {', '.join(p2l_models)}")
        else:
            print("⚠️  P2L模型未正确加载")
        
    except Exception as e:
        print(f"❌ P2L引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 5. 快速语义分析测试
    print("\n🔍 5. 快速语义分析测试")
    try:
        test_prompt = "写一首关于人工智能的现代诗"# "你是谁？" # "写一个Python快速排序函数"
        print(f"测试提示: {test_prompt}")
        
        start_time = time.time()
        complexity, language = engine.semantic_analysis(test_prompt)
        analysis_time = time.time() - start_time
        
        print(f"复杂度分数: {complexity:.4f}")
        print(f"语言分数: {language:.4f}")
        print(f"分析时间: {analysis_time:.3f}s")
        
        # 检查是否使用了真实P2L模型
        if complexity == 0.5 and language == 0.5:
            print("⚠️  使用了默认值，P2L模型可能未工作")
        else:
            print("✅ 使用了P2L神经网络分析")
            
    except Exception as e:
        print(f"❌ 语义分析测试失败: {e}")
    
    # 6. 测试总结
    print("\n" + "=" * 40)
    print("🏁 测试总结")
    
    try:
        if engine:
            models_info = engine.get_loaded_models()
            total_models = models_info.get('total_models_loaded', 0)
            p2l_models = models_info.get('p2l_models', [])
            
            if total_models > 0 and p2l_models:
                print("🎉 P2L模型测试完全成功！")
                print("✅ P2L神经网络正常工作")
                print(f"✅ 已加载 {total_models} 个P2L模型: {', '.join(p2l_models)}")
            else:
                print("⚠️  P2L模型部分工作")
                print("❌ 可能存在配置问题")
        else:
            print("❌ P2L引擎未初始化")
    except Exception as e:
        print(f"❌ P2L模型测试失败: {e}")
    
    print(f"📅 测试完成: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()