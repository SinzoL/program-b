#!/usr/bin/env python3
"""
简单的千问客户端，使用requests库调用阿里云通义千问API
"""
import os
import requests
import json
import time
from typing import Dict, Any

class SimpleQwenClient:
    def __init__(self):
        self.api_key = self._load_qwen_key()
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
    def _load_qwen_key(self) -> str:
        """加载千问API密钥"""
        # 尝试从api_config.env文件加载
        env_file = os.path.join(os.path.dirname(__file__), 'api_config.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('DASHSCOPE_API_KEY=') and '=' in line:
                        key = line.strip().split('=', 1)[1]
                        if key:
                            return key
        
        # 从环境变量加载
        return os.getenv('DASHSCOPE_API_KEY', '')
    
    def generate_response(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成千问响应"""
        if not self.api_key:
            raise ValueError("千问API密钥未配置")
        
        start_time = time.time()
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 千问模型映射
        qwen_model = model
        if model.startswith('qwen'):
            qwen_model = model
        else:
            qwen_model = 'qwen2.5-72b-instruct'  # 默认模型
        
        data = {
            'model': qwen_model,
            'input': {
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            },
            'parameters': {
                'max_tokens': kwargs.get('max_tokens', 2000),
                'temperature': kwargs.get('temperature', 0.7),
                'top_p': kwargs.get('top_p', 0.8),
                'repetition_penalty': kwargs.get('repetition_penalty', 1.1)
            }
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=60
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # 检查API响应状态
                if result.get('code'):
                    raise Exception(f"千问API错误: {result.get('message', '未知错误')}")
                
                # 提取响应内容
                output = result.get('output', {})
                content = output.get('text', '')
                
                # 提取使用统计
                usage = result.get('usage', {})
                input_tokens = usage.get('input_tokens', 0)
                output_tokens = usage.get('output_tokens', 0)
                total_tokens = usage.get('total_tokens', input_tokens + output_tokens)
                
                # 千问定价 (根据实际价格调整)
                # qwen2.5-72b-instruct: ¥0.015/1K tokens
                cost_per_1k_cny = 0.015  # 人民币
                cost_cny = (total_tokens / 1000) * cost_per_1k_cny
                cost_usd = cost_cny * 0.14  # 大概汇率转换为美元
                
                return {
                    "model": qwen_model,
                    "response": content,
                    "content": content,
                    "response_time": round(response_time, 2),
                    "tokens": total_tokens,
                    "tokens_used": total_tokens,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost": round(cost_usd, 4),
                    "cost_cny": round(cost_cny, 4),
                    "provider": "qwen",
                    "is_real_api": True
                }
            else:
                error_msg = f"千问API错误 {response.status_code}: {response.text}"
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"千问API调用失败: {str(e)}")

def test_qwen_api():
    """测试千问API"""
    client = SimpleQwenClient()
    
    if not client.api_key:
        print("❌ 千问API密钥未配置")
        return
        
    print(f"API密钥: {client.api_key[:10]}...{client.api_key[-10:]}")
    
    try:
        response = client.generate_response(
            model='qwen2.5-72b-instruct',
            prompt='你好，请简单介绍一下你自己',
            max_tokens=200
        )
        print(f"✅ 测试成功: {response['content'][:100]}...")
        print(f"📊 tokens: {response['tokens']}, 耗时: {response['response_time']}s")
        print(f"💰 成本: ${response['cost']:.4f} (¥{response['cost_cny']:.4f})")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_qwen_api()