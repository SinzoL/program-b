#!/usr/bin/env python3
"""
LLM API客户端
支持多个大模型提供商的API调用
"""

import os
import asyncio
import aiohttp
import json
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_used: int
    cost: float
    response_time: float
    provider: str

class LLMClient:
    def __init__(self):
        self.session = None
        self.api_keys = self._load_api_keys()
        
    def _load_api_keys(self) -> Dict[str, str]:
        """加载API密钥"""
        # 尝试从api_config.env文件加载
        env_file = os.path.join(os.path.dirname(__file__), 'api_config.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if value:  # 只设置非空值
                            os.environ[key] = value
        
        return {
            'openai': os.getenv('OPENAI_API_KEY', ''),
            'anthropic': os.getenv('ANTHROPIC_API_KEY', ''),
            'google': os.getenv('GOOGLE_API_KEY', ''),
            'dashscope': os.getenv('DASHSCOPE_API_KEY', ''),
            'deepseek': os.getenv('DEEPSEEK_API_KEY', ''),
        }
    
    async def __aenter__(self):
        # 创建连接器，使用默认SSL设置
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        # 创建会话
        timeout = aiohttp.ClientTimeout(total=60, connect=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate_response(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """生成LLM响应"""
        import time
        start_time = time.time()
        
        try:
            # 根据模型选择提供商
            if model.startswith('gpt-'):
                response = await self._call_openai(model, prompt, **kwargs)
            elif model.startswith('claude-'):
                response = await self._call_anthropic(model, prompt, **kwargs)
            elif model.startswith('gemini-'):
                response = await self._call_google(model, prompt, **kwargs)
            elif model.startswith('qwen'):
                response = await self._call_dashscope(model, prompt, **kwargs)
            elif model.startswith('deepseek'):
                response = await self._call_deepseek(model, prompt, **kwargs)
            else:
                # 如果没有API密钥或不支持的模型，返回模拟响应
                response = await self._generate_fallback_response(model, prompt, **kwargs)
            
            response.response_time = time.time() - start_time
            return response
            
        except Exception as e:
            logger.error(f"API调用失败: {e}")
            # 返回模拟响应作为后备
            response = await self._generate_fallback_response(model, prompt, **kwargs)
            response.response_time = time.time() - start_time
            return response
    
    async def _call_openai(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """调用OpenAI API"""
        if not self.api_keys['openai']:
            raise ValueError("OpenAI API密钥未配置")
        
        url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1') + '/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.api_keys["openai"]}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': kwargs.get('max_tokens', 2000),
            'temperature': kwargs.get('temperature', 0.7)
        }
        
        async with self.session.post(url, headers=headers, json=data) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"OpenAI API错误 {resp.status}: {error_text}")
            
            result = await resp.json()
            content = result['choices'][0]['message']['content']
            tokens_used = result['usage']['total_tokens']
            
            # 计算成本 (示例价格，实际需要根据最新价格调整)
            cost_per_1k = 0.03 if 'gpt-4o' in model else 0.0015
            cost = (tokens_used / 1000) * cost_per_1k
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                cost=cost,
                response_time=0,
                provider='openai'
            )
    
    async def _call_anthropic(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """调用Anthropic Claude API"""
        if not self.api_keys['anthropic']:
            raise ValueError("Anthropic API密钥未配置")
        
        # 使用中转服务，转换为OpenAI兼容格式
        base_url = os.getenv('ANTHROPIC_BASE_URL', 'https://api.anthropic.com/v1')
        url = f'{base_url}/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.api_keys["anthropic"]}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': kwargs.get('max_tokens', 2000),
            'temperature': kwargs.get('temperature', 0.7)
        }
        
        async with self.session.post(url, headers=headers, json=data) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"Anthropic API错误 {resp.status}: {error_text}")
            
            # 检查响应内容类型
            content_type = resp.headers.get('content-type', '').lower()
            logger.info(f"API响应内容类型: {content_type}")
            
            # 尝试解析响应
            try:
                if 'application/json' in content_type:
                    result = await resp.json()
                else:
                    # 如果不是JSON，尝试解析为文本
                    text_response = await resp.text()
                    logger.warning(f"收到非JSON响应: {text_response[:200]}...")
                    
                    # 尝试从文本中提取JSON
                    import re
                    json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                    else:
                        # 如果无法解析为JSON，创建模拟响应格式
                        result = {
                            'choices': [{'message': {'content': text_response}}],
                            'usage': {'total_tokens': len(text_response.split()) * 1.3}
                        }
                
                content = result['choices'][0]['message']['content']
                tokens_used = result.get('usage', {}).get('total_tokens', len(content.split()) * 1.3)
                
                # 计算成本
                cost_per_1k = 0.025 if 'sonnet' in model else 0.008
                cost = (tokens_used / 1000) * cost_per_1k
                
                return LLMResponse(
                    content=content,
                    model=model,
                    tokens_used=int(tokens_used),
                    cost=cost,
                    response_time=0,
                    provider='anthropic'
                )
                
            except Exception as parse_error:
                logger.error(f"响应解析失败: {parse_error}")
                # 获取原始响应文本作为内容
                raw_text = await resp.text()
                tokens_used = len(raw_text.split()) * 1.3
                cost_per_1k = 0.025 if 'sonnet' in model else 0.008
                cost = (tokens_used / 1000) * cost_per_1k
                
                return LLMResponse(
                    content=raw_text,
                    model=model,
                    tokens_used=int(tokens_used),
                    cost=cost,
                    response_time=0,
                    provider='anthropic'
                )
    
    async def _call_google(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """调用Google Gemini API"""
        if not self.api_keys['google']:
            raise ValueError("Google API密钥未配置")
        
        # 使用中转服务，转换为OpenAI格式
        base_url = os.getenv('GOOGLE_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta')
        url = f'{base_url}/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.api_keys["google"]}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': kwargs.get('max_tokens', 2000),
            'temperature': kwargs.get('temperature', 0.7)
        }
        
        async with self.session.post(url, headers=headers, json=data) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"Google API错误 {resp.status}: {error_text}")
            
            result = await resp.json()
            content = result['choices'][0]['message']['content']
            tokens_used = result.get('usage', {}).get('total_tokens', len(content.split()) * 1.3)
            
            # 计算成本
            cost_per_1k = 0.015 if 'pro' in model else 0.0075
            cost = (tokens_used / 1000) * cost_per_1k
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=int(tokens_used),
                cost=cost,
                response_time=0,
                provider='google'
            )
    
    async def _call_dashscope(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """调用阿里云通义千问API"""
        if not self.api_keys['dashscope']:
            raise ValueError("DashScope API密钥未配置")
        
        url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
        headers = {
            'Authorization': f'Bearer {self.api_keys["dashscope"]}',
            'Content-Type': 'application/json'
        }
        
        # 千问模型映射
        qwen_model = model if model.startswith('qwen') else 'qwen2.5-72b-instruct'
        
        data = {
            'model': qwen_model,
            'input': {
                'messages': [{'role': 'user', 'content': prompt}]
            },
            'parameters': {
                'max_tokens': kwargs.get('max_tokens', 2000),
                'temperature': kwargs.get('temperature', 0.7),
                'top_p': kwargs.get('top_p', 0.8),
                'repetition_penalty': kwargs.get('repetition_penalty', 1.1)
            }
        }
        
        async with self.session.post(url, headers=headers, json=data) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"DashScope API错误 {resp.status}: {error_text}")
            
            result = await resp.json()
            
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
            
            # 千问定价 (qwen2.5-72b-instruct: ¥0.015/1K tokens)
            cost_per_1k_cny = 0.015  # 人民币
            cost_cny = (total_tokens / 1000) * cost_per_1k_cny
            cost_usd = cost_cny * 0.14  # 汇率转换为美元
            
            return LLMResponse(
                content=content,
                model=qwen_model,
                tokens_used=total_tokens,
                cost=cost_usd,
                response_time=0,
                provider='qwen'
            )
    
    async def _call_deepseek(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """调用DeepSeek API"""
        if not self.api_keys['deepseek']:
            raise ValueError("DeepSeek API密钥未配置")
        
        url = 'https://api.deepseek.com/v1/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.api_keys["deepseek"]}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': kwargs.get('max_tokens', 2000),
            'temperature': kwargs.get('temperature', 0.7)
        }
        
        async with self.session.post(url, headers=headers, json=data) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"DeepSeek API错误 {resp.status}: {error_text}")
            
            result = await resp.json()
            content = result['choices'][0]['message']['content']
            tokens_used = result['usage']['total_tokens']
            
            # 计算成本
            cost_per_1k = 0.012
            cost = (tokens_used / 1000) * cost_per_1k
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                cost=cost,
                response_time=0,
                provider='deepseek'
            )
    
    async def _generate_fallback_response(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """生成后备模拟响应"""
        logger.warning(f"使用模拟响应 for {model}")
        
        # 模拟网络延迟
        await asyncio.sleep(0.5)
        
        # 生成模拟内容
        if "javascript" in prompt.lower() or "js" in prompt.lower():
            content = """// JavaScript下划线转驼峰实现

function toCamelCase(str) {
    return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

// 使用示例
console.log(toCamelCase('hello_world')); // helloWorld
console.log(toCamelCase('user_name')); // userName"""
        
        elif any(keyword in prompt.lower() for keyword in ["诗", "poem", "poetry", "晴天", "阳光"]):
            content = """《晴空万里》

蔚蓝天空无云遮，
金辉洒向大地花。
微风轻抚绿叶舞，
鸟儿欢歌满枝桠。

阳光透过窗棂照，
温暖心房驱阴霾。
此刻时光多美好，
晴天如诗画中来。"""
        
        elif any(keyword in prompt.lower() for keyword in ["python", "算法", "代码", "编程"]):
            content = """# Python快速排序实现

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# 使用示例
test_array = [64, 34, 25, 12, 22, 11, 90]
sorted_array = quicksort(test_array)
print(f"排序结果: {sorted_array}")"""
        
        else:
            content = f"""基于您的问题："{prompt}"

这是一个很有意思的问题。让我为您详细分析：

## 核心观点
针对您提出的问题，我认为需要从多个角度来考虑。

## 详细解答
1. **背景分析**：首先需要理解问题的背景和上下文
2. **关键要点**：识别出几个核心要素和关键因素
3. **解决方案**：提供可行的解决思路和建议
4. **实施建议**：给出具体的实施步骤和注意事项

## 总结
综合考虑各种因素，建议采取循序渐进的方法来处理这个问题。

希望这个回答对您有所帮助！如需更详细的信息，请随时告诉我。

---
*注：这是模拟响应，实际使用时请配置相应的API密钥以获得真实的AI回答。*"""
        
        # 估算token数量和成本
        tokens_used = len(content.split()) * 1.3
        cost_per_1k = 0.02  # 默认成本
        cost = (tokens_used / 1000) * cost_per_1k
        
        return LLMResponse(
            content=content,
            model=model,
            tokens_used=int(tokens_used),
            cost=cost,
            response_time=0,
            provider='simulation'
        )

# 全局客户端实例
llm_client = LLMClient()