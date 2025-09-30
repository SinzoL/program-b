import os
import requests
import json
import time
from dotenv import load_dotenv

class SimpleDeepSeekClient:
    def __init__(self):
        # 尝试多种方式加载配置
        load_dotenv('api_config.env')
        load_dotenv()  # 也尝试加载默认.env文件
        
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        
        # 如果环境变量没有，直接从文件读取
        if not self.api_key:
            try:
                with open('api_config.env', 'r') as f:
                    for line in f:
                        if line.startswith('DEEPSEEK_API_KEY='):
                            self.api_key = line.split('=', 1)[1].strip()
                            break
            except FileNotFoundError:
                pass
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        
    def generate_response(self, model, prompt, max_tokens=2000, temperature=0.7):
        """调用DeepSeek API生成响应"""
        if not self.api_key:
            raise Exception("DeepSeek API密钥未配置")
            
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # DeepSeek模型映射
        deepseek_model = model
        if model.startswith('deepseek'):
            deepseek_model = model
        else:
            deepseek_model = 'deepseek-chat'  # 默认模型
            
        data = {
            'model': deepseek_model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': max_tokens,
            'temperature': temperature,
            'stream': False
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=60  # 增加到60秒
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                content = result['choices'][0]['message']['content']
                tokens_used = result.get('usage', {}).get('total_tokens', 0)
                
                # DeepSeek定价 (假设价格，需要根据实际情况调整)
                cost = tokens_used * 0.00002  # 假设每1K tokens $0.02
                
                return {
                    "model": deepseek_model,
                    "response": content,
                    "content": content,
                    "response_time": round(response_time, 2),
                    "tokens": tokens_used,
                    "tokens_used": tokens_used,
                    "cost": round(cost, 4),
                    "provider": "deepseek",
                    "is_real_api": True
                }
            else:
                error_msg = f"DeepSeek API错误 {response.status_code}: {response.text}"
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"DeepSeek API调用失败: {str(e)}")

def test_deepseek_api():
    """测试DeepSeek API"""
    client = SimpleDeepSeekClient()
    
    if not client.api_key:
        print("❌ DeepSeek API密钥未配置")
        return
        
    print(f"API密钥: {client.api_key[:10]}...{client.api_key[-10:]}")
    
    try:
        response = client.generate_response(
            model='deepseek-chat',
            prompt='你好，请简单回答',
            max_tokens=100
        )
        print(f"✅ 测试成功: {response['content'][:50]}...")
        print(f"📊 tokens: {response['tokens']}, 耗时: {response['response_time']}s")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_deepseek_api()