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
            raise ValueError(f"不支持的模型: {model}")
        
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
        
        base_url = os.getenv('ANTHROPIC_BASE_URL', 'https://api.anthropic.com/v1')
        
        # 检查是否使用中转服务（通过URL判断）
        is_proxy_service = 'yinli.one' in base_url or 'openai' in base_url.lower()
        
        if is_proxy_service:
            # 中转服务使用OpenAI兼容格式
            return await self._call_anthropic_proxy(model, prompt, base_url, **kwargs)
        else:
            # 原生Anthropic API格式
            return await self._call_anthropic_native(model, prompt, base_url, **kwargs)
    
    async def _call_anthropic_native(self, model: str, prompt: str, base_url: str, **kwargs) -> LLMResponse:
        """调用原生Anthropic API"""
        url = f'{base_url}/messages'
        headers = {
            'x-api-key': self.api_keys['anthropic'],
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': model,
            'max_tokens': kwargs.get('max_tokens', 2000),
            'temperature': kwargs.get('temperature', 0.7),
            'messages': [{'role': 'user', 'content': prompt}]
        }
        
        try:
            async with self.session.post(url, headers=headers, json=data) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"Anthropic原生API错误 {resp.status}: {error_text}")
                    raise Exception(f"Anthropic原生API错误 {resp.status}: {error_text}")
                
                result = await resp.json()
                content = result['content'][0]['text']
                
                # 提取token使用量
                usage = result.get('usage', {})
                input_tokens = usage.get('input_tokens', 0)
                output_tokens = usage.get('output_tokens', 0)
                total_tokens = input_tokens + output_tokens
                
                # 计算成本
                cost_per_1k = 0.025 if 'sonnet' in model else 0.008
                cost = (total_tokens / 1000) * cost_per_1k
                
                return LLMResponse(
                    content=content,
                    model=model,
                    tokens_used=total_tokens,
                    cost=cost,
                    response_time=0,
                    provider='anthropic'
                )
        except Exception as e:
            logger.error(f"Anthropic原生API调用失败: {str(e)}")
            raise Exception(f"Anthropic原生API调用失败: {str(e)}")
    
    async def _call_anthropic_proxy(self, model: str, prompt: str, base_url: str, **kwargs) -> LLMResponse:
        """调用中转服务的Anthropic API（OpenAI兼容格式）"""
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
        
        try:
            async with self.session.post(url, headers=headers, json=data) as resp:
                error_text = await resp.text()
                
                if resp.status != 200:
                    logger.error(f"中转服务错误 {resp.status}: {error_text}")
                    
                    # 如果中转服务失败，尝试使用原生API作为fallback
                    logger.info("中转服务失败，尝试使用原生Anthropic API...")
                    return await self._call_anthropic_native(model, prompt, 'https://api.anthropic.com/v1', **kwargs)
                
                # 尝试解析JSON响应
                try:
                    result = json.loads(error_text)
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
                except json.JSONDecodeError:
                    logger.error(f"中转服务响应解析失败: {error_text[:200]}...")
                    # 如果解析失败，也尝试原生API
                    logger.info("响应解析失败，尝试使用原生Anthropic API...")
                    return await self._call_anthropic_native(model, prompt, 'https://api.anthropic.com/v1', **kwargs)
                    
        except Exception as e:
            logger.error(f"中转服务调用失败: {str(e)}")
            # 最后的fallback：尝试原生API
            logger.info("中转服务完全失败，尝试使用原生Anthropic API...")
            try:
                return await self._call_anthropic_native(model, prompt, 'https://api.anthropic.com/v1', **kwargs)
            except Exception as native_error:
                logger.error(f"原生API也失败了: {str(native_error)}")
                raise Exception(f"Claude API调用失败 - 中转服务: {str(e)}, 原生API: {str(native_error)}")
    
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
    


# 全局客户端实例
llm_client = LLMClient()