#!/usr/bin/env python3
"""
简单的OpenAI客户端，使用requests库避免SSL问题
"""
import os
import requests
import time
from typing import Dict, Any

class SimpleOpenAIClient:
    def __init__(self):
        self.api_key = self._load_openai_key()
        self.base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        
    def _load_openai_key(self) -> str:
        """加载OpenAI API密钥"""
        # 尝试从api_config.env文件加载
        env_file = os.path.join(os.path.dirname(__file__), 'api_config.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY=') and '=' in line:
                        key = line.strip().split('=', 1)[1]
                        if key:
                            return key
        
        # 从环境变量加载
        return os.getenv('OPENAI_API_KEY', '')
    
    def generate_response(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成OpenAI响应"""
        if not self.api_key:
            raise ValueError("OpenAI API密钥未配置")
        
        start_time = time.time()
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': kwargs.get('max_tokens', 2000),
            'temperature': kwargs.get('temperature', 0.7)
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API错误 {response.status_code}: {response.text}")
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            tokens_used = result['usage']['total_tokens']
            
            # 计算成本
            cost_per_1k = 0.03 if 'gpt-4o' in model else 0.0015
            cost = (tokens_used / 1000) * cost_per_1k
            
            response_time = time.time() - start_time
            
            return {
                'content': content,
                'response': content,  # 兼容字段
                'model': model,
                'tokens': tokens_used,
                'tokens_used': tokens_used,
                'cost': cost,
                'response_time': response_time,
                'provider': 'openai',
                'is_real_api': True
            }
            
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {e}")

# 测试函数
if __name__ == "__main__":
    client = SimpleOpenAIClient()
    if client.api_key:
        print(f"API密钥: {client.api_key[:10]}...{client.api_key[-10:]}")
        try:
            result = client.generate_response('gpt-4o-mini', '你好，请简单回答')
            print(f"✅ 测试成功: {result['content'][:100]}...")
            print(f"Token数: {result['tokens']}, 成本: ${result['cost']:.4f}")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    else:
        print("❌ API密钥未配置")