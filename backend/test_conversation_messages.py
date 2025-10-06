#!/usr/bin/env python3
"""
测试长对话消息格式 - 验证修复效果
模拟前端发送的消息格式，确保不会出现空内容错误
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from unified_client import UnifiedLLMClient

async def test_conversation_messages():
    """测试对话消息格式"""
    print("🧪 测试长对话消息格式")
    print("=" * 50)
    
    # 模拟前端可能发送的消息格式（包含潜在的空内容问题）
    test_cases = [
        {
            "name": "正常对话",
            "messages": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"},
                {"role": "user", "content": "请介绍一下Python"}
            ]
        },
        {
            "name": "包含空内容的消息（修复前会出错）",
            "messages": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": ""},  # 空内容
                {"role": "user", "content": "请介绍一下Python"}
            ]
        },
        {
            "name": "包含空白字符的消息",
            "messages": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "   "},  # 只有空格
                {"role": "user", "content": "请介绍一下Python"}
            ]
        },
        {
            "name": "混合空内容的复杂对话",
            "messages": [
                {"role": "user", "content": "第一个问题"},
                {"role": "assistant", "content": "第一个回答"},
                {"role": "user", "content": ""},  # 空用户消息
                {"role": "assistant", "content": "第二个回答"},
                {"role": "user", "content": "第三个问题"}
            ]
        }
    ]
    
    async with UnifiedLLMClient() as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 测试案例 {i}: {test_case['name']}")
            print(f"📋 消息数量: {len(test_case['messages'])}")
            
            # 显示消息内容
            for j, msg in enumerate(test_case['messages']):
                content_preview = repr(msg['content'][:30]) if msg['content'] else "''"
                print(f"  {j+1}. {msg['role']}: {content_preview}")
            
            try:
                # 测试Claude模型（之前出问题的模型）
                response = await client.generate_response(
                    "claude-3-5-sonnet-20240620",
                    "请简单回答这个问题",
                    messages=test_case['messages']
                )
                
                if response.provider == "error":
                    print(f"❌ 测试失败: {response.content}")
                else:
                    print(f"✅ 测试成功")
                    print(f"📊 响应时间: {response.response_time:.2f}s")
                    print(f"📝 响应内容: {response.content[:50]}...")
                
            except Exception as e:
                print(f"❌ 测试异常: {e}")
            
            # 添加延迟避免频率限制
            await asyncio.sleep(1)
    
    print("\n" + "=" * 50)
    print("🎯 测试完成")

if __name__ == "__main__":
    asyncio.run(test_conversation_messages())