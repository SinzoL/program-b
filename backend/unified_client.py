#!/usr/bin/env python3
"""
统一LLM客户端 - 合并llm_client和llm_handler功能
简化的单一LLM调用接口
"""

import os
import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, Optional, Any
from dataclasses import dataclass

try:
    from .config import get_api_config, get_model_config
except ImportError:
    from config import get_api_config, get_model_config

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_used: int
    cost: float
    response_time: float
    provider: str

class UnifiedLLMClient:
    """统一的LLM客户端，整合所有API调用功能"""
    
    def __init__(self):
        self.session = None
        self.config = get_api_config()
        
    async def __aenter__(self):
        pool_config = self.config["connection_pool"]
        timeout_config = self.config["timeouts"]
        
        connector = aiohttp.TCPConnector(
            limit=pool_config["limit"],
            limit_per_host=pool_config["limit_per_host"],
            ttl_dns_cache=pool_config["ttl_dns_cache"],
            use_dns_cache=True,
        )
        
        timeout = aiohttp.ClientTimeout(
            total=timeout_config["total"], 
            connect=timeout_config["connect"]
        )
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate_response(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """统一的响应生成接口"""
        start_time = time.time()
        
        try:
            # 获取模型配置
            model_config = get_model_config(model)
            if not model_config:
                raise ValueError(f"不支持的模型: {model}")
            
            provider = model_config["provider"]
            
            # 根据提供商调用相应的API
            if provider == "openai":
                response = await self._call_openai(model, prompt, **kwargs)
            elif provider == "anthropic":
                response = await self._call_anthropic(model, prompt, **kwargs)
            elif provider == "google":
                response = await self._call_google(model, prompt, **kwargs)
            elif provider == "dashscope":
                response = await self._call_dashscope(model, prompt, **kwargs)
            elif provider == "deepseek":
                response = await self._call_deepseek(model, prompt, **kwargs)
            else:
                raise ValueError(f"不支持的提供商: {provider}")
            
            response.response_time = time.time() - start_time
            logger.info(f"✅ {provider} API调用成功: {model}")
            return response
            
        except Exception as e:
            logger.error(f"❌ LLM API调用失败: {model} - {e}")
            
            # 返回错误响应而不是抛出异常
            error_message = self._format_error_message(model, str(e))
            return LLMResponse(
                content=error_message,
                model=model,
                tokens_used=0,
                cost=0.0,
                response_time=time.time() - start_time,
                provider="error"
            )
    
    def _format_error_message(self, model: str, error: str) -> str:
        """格式化错误消息"""
        if "timeout" in error.lower():
            return f"请求超时：{model} 正在处理复杂问题，请稍后重试"
        elif "rate limit" in error.lower():
            return f"API调用频率限制：{model} 请稍后重试"
        elif "quota" in error.lower():
            return f"API配额不足：{model} 请检查账户余额"
        elif "unauthorized" in error.lower():
            return f"API密钥无效：{model} 请检查配置"
        else:
            return f"API暂时不可用: {error}"
    
    async def _call_openai(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """调用OpenAI API"""
        api_keys = self.config["api_keys"]
        base_urls = self.config["base_urls"]
        model_config = get_model_config(model)
        
        url = base_urls['openai'] + '/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_keys["openai"]}',
            'Content-Type': 'application/json'
        }
        
        messages = kwargs.get('messages', [{'role': 'user', 'content': prompt}])
        
        data = {
            'model': model,
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', model_config.get('max_tokens', 2000)),
            'temperature': kwargs.get('temperature', 0.7)
        }
        
        async with self.session.post(url, headers=headers, json=data) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"OpenAI API错误 {resp.status}: {error_text}")
            
            result = await resp.json()
            content = result['choices'][0]['message']['content']
            tokens_used = result['usage']['total_tokens']
            cost = (tokens_used / 1000) * model_config.get('cost_per_1k', 0.0015)
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                cost=cost,
                response_time=0,
                provider='openai'
            )
    
    async def _call_anthropic(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """调用Anthropic API（支持中转服务）"""
        api_keys = self.config["api_keys"]
        base_urls = self.config["base_urls"]
        base_url = base_urls['anthropic']
        
        # 检查是否使用中转服务
        if 'yinli.one' in base_url or 'openai' in base_url.lower():
            return await self._call_anthropic_proxy(model, prompt, base_url, **kwargs)
        else:
            return await self._call_anthropic_native(model, prompt, base_url, **kwargs)
    
    async def _call_anthropic_proxy(self, model: str, prompt: str, base_url: str, **kwargs) -> LLMResponse:
        """调用中转服务的Anthropic API"""
        api_keys = self.config["api_keys"]
        
        url = f'{base_url}/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_keys["anthropic"]}',
            'Content-Type': 'application/json'
        }
        
        messages = kwargs.get('messages', [{'role': 'user', 'content': prompt}])
        
        data = {
            'model': model,
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', 2000),
            'temperature': kwargs.get('temperature', 0.7)
        }
        
        async with self.session.post(url, headers=headers, json=data) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"Anthropic中转API错误 {resp.status}: {error_text}")
            
            result = await resp.json()
            content = result['choices'][0]['message']['content']
            tokens_used = result.get('usage', {}).get('total_tokens', len(content.split()) * 1.3)
            cost = (tokens_used / 1000) * (0.025 if 'sonnet' in model else 0.008)
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=int(tokens_used),
                cost=cost,
                response_time=0,
                provider='anthropic'
            )
    
    async def _call_anthropic_native(self, model: str, prompt: str, base_url: str, **kwargs) -> LLMResponse:
        """调用原生Anthropic API"""
        api_keys = self.config["api_keys"]
        
        url = f'{base_url}/messages'
        headers = {
            'x-api-key': api_keys['anthropic'],
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        messages = kwargs.get('messages', [{'role': 'user', 'content': prompt}])
        
        data = {
            'model': model,
            'max_tokens': kwargs.get('max_tokens', 2000),
            'temperature': kwargs.get('temperature', 0.7),
            'messages': messages
        }
        
        async with self.session.post(url, headers=headers, json=data) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"Anthropic原生API错误 {resp.status}: {error_text}")
            
            result = await resp.json()
            content = result['content'][0]['text']
            usage = result.get('usage', {})
            total_tokens = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
            cost = (total_tokens / 1000) * 0.025
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=total_tokens,
                cost=cost,
                response_time=0,
                provider='anthropic'
            )
    
    async def _call_google(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """调用Google Gemini API"""
        api_keys = self.config["api_keys"]
        base_urls = self.config["base_urls"]
        
        url = f'{base_urls["google"]}/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_keys["google"]}',
            'Content-Type': 'application/json'
        }
        
        messages = kwargs.get('messages', [{'role': 'user', 'content': prompt}])
        
        data = {
            'model': model,
            'messages': messages,
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
            cost = (tokens_used / 1000) * (0.025 if 'pro' in model else 0.015)
            
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
        api_keys = self.config["api_keys"]
        base_urls = self.config["base_urls"]
        model_config = get_model_config(model)
        
        url = f'{base_urls["dashscope"]}/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_keys["dashscope"]}',
            'Content-Type': 'application/json'
        }
        
        messages = kwargs.get('messages', [{'role': 'user', 'content': prompt}])
        qwen_model = model if model.startswith('qwen') else 'qwen2.5-72b-instruct'
        
        data = {
            'model': qwen_model,
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', model_config.get('max_tokens', 2000)),
            'temperature': kwargs.get('temperature', 0.7),
            'stream': False
        }
        
        async with self.session.post(url, headers=headers, json=data) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"千问API错误 {resp.status}: {error_text}")
            
            result = await resp.json()
            content = result['choices'][0]['message']['content']
            total_tokens = result.get('usage', {}).get('total_tokens', len(content.split()) * 1.3)
            cost = (total_tokens / 1000) * model_config.get('cost_per_1k', 0.002)
            
            return LLMResponse(
                content=content,
                model=qwen_model,
                tokens_used=int(total_tokens),
                cost=cost,
                response_time=0,
                provider='dashscope'
            )
    
    async def _call_deepseek(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """调用DeepSeek API"""
        api_keys = self.config["api_keys"]
        base_urls = self.config["base_urls"]
        model_config = get_model_config(model)
        
        url = f'{base_urls["deepseek"]}/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_keys["deepseek"]}',
            'Content-Type': 'application/json'
        }
        
        messages = kwargs.get('messages', [{'role': 'user', 'content': prompt}])
        
        data = {
            'model': model,
            'messages': messages,
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
            cost = (tokens_used / 1000) * model_config.get('cost_per_1k', 0.002)
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                cost=cost,
                response_time=0,
                provider='deepseek'
            )

# 全局客户端实例
unified_client = UnifiedLLMClient()