#!/usr/bin/env python3
"""
测试qwen-plus模型
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_qwen_plus():
    """测试qwen-plus模型"""
    print("🧪 测试qwen-plus模型...")
    
    try:
        from simple_qwen_client import SimpleQwenClient
        
        client = SimpleQwenClient()
        if not client.api_key:
            print("❌ 千问API密钥未配置")
            return False
            
        response = client.generate_response(
            model='qwen-plus',
            prompt='展示js实现字符串中下划线转化为驼峰',
            max_tokens=300
        )
        
        print(f"✅ qwen-plus测试成功")
        print(f"📝 响应: {response['content'][:200]}...")
        print(f"📊 Token数: {response['tokens']}, 成本: ${response['cost']:.4f}")
        print(f"⏱️ 响应时间: {response['response_time']}s")
        return True
        
    except Exception as e:
        print(f"❌ qwen-plus测试失败: {e}")
        return False

if __name__ == "__main__":
    test_qwen_plus()