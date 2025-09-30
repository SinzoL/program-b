#!/usr/bin/env python3
"""
快速千问API测试
验证千问API基本功能，不依赖HuggingFace模型
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

def test_qwen_api_key():
    """测试千问API密钥配置"""
    print("🔑 检查千问API密钥配置...")
    
    try:
        from simple_qwen_client import SimpleQwenClient
        
        client = SimpleQwenClient()
        if client.api_key:
            print(f"✅ 千问API密钥已配置: {client.api_key[:10]}...{client.api_key[-10:]}")
            return True
        else:
            print("❌ 千问API密钥未配置")
            return False
            
    except Exception as e:
        print(f"❌ 千问客户端初始化失败: {e}")
        return False

def test_qwen_api_call():
    """测试千问API调用"""
    print("\n🧪 测试千问API调用...")
    
    try:
        from simple_qwen_client import SimpleQwenClient
        
        client = SimpleQwenClient()
        if not client.api_key:
            print("❌ 跳过API调用测试（无API密钥）")
            return False
            
        response = client.generate_response(
            model='qwen2.5-72b-instruct',
            prompt='请用一句话介绍你自己',
            max_tokens=100
        )
        
        print(f"✅ 千问API调用成功")
        print(f"📝 响应: {response['content'][:100]}...")
        print(f"📊 Token数: {response['tokens']}, 成本: ${response['cost']:.4f}")
        print(f"⏱️ 响应时间: {response['response_time']}s")
        return True
        
    except Exception as e:
        print(f"❌ 千问API调用失败: {e}")
        return False

def test_backend_config():
    """测试后端配置"""
    print("\n⚙️ 检查后端配置...")
    
    try:
        # 检查API配置文件
        config_file = 'api_config.env'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                content = f.read()
                if 'DASHSCOPE_API_KEY' in content:
                    print("✅ api_config.env 中包含千问API密钥配置")
                else:
                    print("❌ api_config.env 中未找到千问API密钥配置")
                    return False
        else:
            print("❌ api_config.env 文件不存在")
            return False
        
        # 检查后端服务配置
        try:
            with open('backend_service.py', 'r') as f:
                content = f.read()
                if 'qwen' in content and 'simple_qwen_client' in content:
                    print("✅ backend_service.py 包含千问支持")
                else:
                    print("❌ backend_service.py 缺少千问支持")
                    return False
        except Exception as e:
            print(f"❌ 无法读取 backend_service.py: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 后端配置检查失败: {e}")
        return False

def test_frontend_config():
    """测试前端配置"""
    print("\n🎨 检查前端配置...")
    
    try:
        frontend_store = 'frontend-vue/src/stores/p2l.js'
        if os.path.exists(frontend_store):
            with open(frontend_store, 'r') as f:
                content = f.read()
                if 'qwen' in content:
                    print("✅ 前端store包含千问模型配置")
                    return True
                else:
                    print("❌ 前端store缺少千问模型配置")
                    return False
        else:
            print("❌ 前端store文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ 前端配置检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 千问API快速测试\n")
    
    results = []
    
    # 测试API密钥配置
    results.append(test_qwen_api_key())
    
    # 测试API调用
    results.append(test_qwen_api_call())
    
    # 测试后端配置
    results.append(test_backend_config())
    
    # 测试前端配置
    results.append(test_frontend_config())
    
    # 汇总结果
    print(f"\n📊 测试结果:")
    print(f"✅ 成功: {sum(results)}/{len(results)}")
    print(f"❌ 失败: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 千问API集成完成！所有测试通过")
        print("\n📋 支持的千问模型:")
        print("   • qwen2.5-72b-instruct (主力模型)")
        print("   • qwen-plus (高级模型)")
        print("   • qwen-turbo (快速模型)")
        print("\n🔧 使用方法:")
        print("   1. 确保 api_config.env 中配置了 DASHSCOPE_API_KEY")
        print("   2. 启动后端服务: python3 backend_service.py")
        print("   3. 在前端选择千问模型进行对话")
    else:
        print("\n⚠️ 部分测试失败，请检查配置")

if __name__ == "__main__":
    main()