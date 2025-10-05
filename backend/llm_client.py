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

class LLMClient:
    def __init__(self):
        self.session = None
        self.config = get_api_config()
        
    def _get_api_keys(self) -> Dict[str, str]:
        """获取API密钥"""
        return self.config["api_keys"]
    
    def _get_base_urls(self) -> Dict[str, str]:
        """获取API端点"""
        return self.config["base_urls"]
    
    async def __aenter__(self):
        # 使用配置文件中的连接池设置
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
        """生成LLM响应"""
        start_time = time.time()
        
        # 获取模型配置
        model_config = get_model_config(model)
        if not model_config:
            raise ValueError(f"不支持的模型: {model}")
        
        provider = model_config["provider"]
        
        # 根据提供商选择调用方法
        if provider == "openai":
            response = await self._call_openai(model, prompt, **kwargs)
        elif provider == "anthropic":
            response = await self._call_anthropic(model, prompt, **kwargs)
        elif provider == "google":
            response = await self._call_google(model, prompt, **kwargs)
        elif provider == "qwen":
            response = await self._call_dashscope(model, prompt, **kwargs)
        elif provider == "deepseek":
            response = await self._call_deepseek(model, prompt, **kwargs)
        else:
            raise ValueError(f"不支持的提供商: {provider}")
        
        response.response_time = time.time() - start_time
        return response
    
    async def _call_openai(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """调用OpenAI API"""
        api_keys = self._get_api_keys()
        base_urls = self._get_base_urls()
        model_config = get_model_config(model)
        
        if not api_keys['openai']:
            raise ValueError("OpenAI API密钥未配置")
        
        url = base_urls['openai'] + '/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_keys["openai"]}',
            'Content-Type': 'application/json'
        }
        
        # 构建消息列表，优先使用传入的messages参数
        messages = kwargs.get('messages')
        if not messages:
            messages = [{'role': 'user', 'content': prompt}]
        
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
            
            # 使用配置文件中的价格
            cost_per_1k = model_config.get('cost_per_1k', 0.0015)
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
        api_keys = self._get_api_keys()
        base_urls = self._get_base_urls()
        model_config = get_model_config(model)
        
        if not api_keys['anthropic']:
            raise ValueError("Anthropic API密钥未配置")
        
        # 检查API密钥格式
        api_key = api_keys['anthropic']
        logger.info(f"Claude API密钥格式: {api_key[:10]}...")
        
        base_url = base_urls['anthropic']
        logger.info(f"Claude API端点: {base_url}")
        
        # 检查是否使用中转服务（通过URL判断）
        is_proxy_service = 'yinli.one' in base_url or 'openai' in base_url.lower()
        
        # 中转服务通常使用统一的API密钥格式，不需要sk-ant-前缀
        if not api_key.startswith('sk-ant-') and not is_proxy_service:
            logger.warning("警告：Anthropic API密钥通常以'sk-ant-'开头，当前密钥格式可能不正确")
        elif is_proxy_service:
            logger.info("使用中转服务，API密钥格式已确认")
        
        if is_proxy_service:
            # 中转服务使用OpenAI兼容格式
            logger.info("使用中转服务调用Claude API")
            return await self._call_anthropic_proxy(model, prompt, base_url, **kwargs)
        else:
            # 原生Anthropic API格式
            logger.info("使用原生Anthropic API")
            return await self._call_anthropic_native(model, prompt, base_url, **kwargs)
    
    async def _call_anthropic_native(self, model: str, prompt: str, base_url: str, **kwargs) -> LLMResponse:
        """调用原生Anthropic API"""
        api_keys = self._get_api_keys()
        model_config = get_model_config(model)
        
        url = f'{base_url}/messages'
        headers = {
            'x-api-key': api_keys['anthropic'],
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        # 构建消息列表，优先使用传入的messages参数
        raw_messages = kwargs.get('messages')
        if not raw_messages:
            messages = [{'role': 'user', 'content': prompt}]
        else:
            # Claude API要求：
            # 1. 消息必须严格按照user/assistant交替
            # 2. 最后一条消息必须是user
            # 3. 不能有连续的相同角色消息
            messages = []
            last_role = None
            
            for msg in raw_messages:
                current_role = msg.get('role')
                content = msg.get('content', '')
                
                if not content.strip():
                    continue
                    
                # 如果有连续的相同角色，合并内容
                if current_role == last_role and messages:
                    messages[-1]['content'] += '\n\n' + content
                else:
                    messages.append({
                        'role': current_role,
                        'content': content
                    })
                    last_role = current_role
            
            # 确保最后一条消息是user角色
            if messages and messages[-1]['role'] != 'user':
                messages.append({'role': 'user', 'content': prompt})
        
        data = {
            'model': model,
            'max_tokens': kwargs.get('max_tokens', model_config.get('max_tokens', 2000)),
            'temperature': kwargs.get('temperature', 0.7),
            'messages': messages
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
                
                # 使用配置文件中的价格
                cost_per_1k = model_config.get('cost_per_1k', 0.025)
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
        api_keys = self._get_api_keys()
        
        url = f'{base_url}/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_keys["anthropic"]}',
            'Content-Type': 'application/json'
        }
        
        # 构建消息列表，优先使用传入的messages参数
        raw_messages = kwargs.get('messages')
        if not raw_messages:
            messages = [{'role': 'user', 'content': prompt}]
        else:
            # 中转服务通常使用OpenAI格式，但也需要确保消息格式正确
            messages = []
            for msg in raw_messages:
                content = msg.get('content', '')
                if content.strip():  # 只添加非空消息
                    messages.append({
                        'role': msg.get('role'),
                        'content': content
                    })
            
            # 如果处理后没有消息，添加当前prompt
            if not messages:
                messages = [{'role': 'user', 'content': prompt}]
        
        data = {
            'model': model,
            'messages': messages,
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
                
                # 临时fallback：返回模拟响应，但明确标注
                logger.warning("所有Claude API调用都失败，返回模拟响应")
                return LLMResponse(
                    content=f"[模拟响应] 抱歉，Claude API当前不可用。错误信息：{str(e)[:100]}...\n\n建议检查：\n1. API密钥是否正确（应以sk-ant-开头）\n2. 中转服务是否支持Claude\n3. 网络连接是否正常",
                    model=model,
                    tokens_used=50,
                    cost=0.001,
                    response_time=0,
                    provider='anthropic_mock'
                )
    
    async def _call_google(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """调用Google Gemini API"""
        api_keys = self._get_api_keys()
        base_urls = self._get_base_urls()
        model_config = get_model_config(model)
        
        if not api_keys['google']:
            raise ValueError("Google API密钥未配置")
        
        # 使用中转服务，转换为OpenAI格式
        base_url = base_urls['google']
        url = f'{base_url}/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_keys["google"]}',
            'Content-Type': 'application/json'
        }
        
        # 构建消息列表，优先使用传入的messages参数
        messages = kwargs.get('messages')
        if not messages:
            messages = [{'role': 'user', 'content': prompt}]
        
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
        """调用阿里云通义千问API (兼容模式)"""
        api_keys = self._get_api_keys()
        base_urls = self._get_base_urls()
        model_config = get_model_config(model)
        
        if not api_keys['dashscope']:
            raise ValueError("DashScope API密钥未配置")
        
        # 使用兼容模式URL (OpenAI格式)
        base_url = base_urls['dashscope']
        url = f'{base_url}/chat/completions'
        
        headers = {
            'Authorization': f'Bearer {api_keys["dashscope"]}',
            'Content-Type': 'application/json'
        }
        
        # 千问模型映射
        qwen_model = model if model.startswith('qwen') else 'qwen2.5-72b-instruct'
        
        # 构建消息列表，优先使用传入的messages参数
        messages = kwargs.get('messages')
        if not messages:
            messages = [{'role': 'user', 'content': prompt}]
        
        data = {
            'model': qwen_model,
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', model_config.get('max_tokens', 2000)),
            'temperature': kwargs.get('temperature', 0.7),
            'top_p': kwargs.get('top_p', 0.8),
            'stream': False
        }
        
        try:
            async with self.session.post(url, headers=headers, json=data) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"千问API错误 {resp.status}: {error_text}")
                    raise Exception(f"千问API错误 {resp.status}: {error_text}")
                
                result = await resp.json()
                
                # OpenAI兼容格式响应
                content = result['choices'][0]['message']['content']
                
                # 提取使用统计
                usage = result.get('usage', {})
                total_tokens = usage.get('total_tokens', len(content.split()) * 1.3)
                
                # 使用配置文件中的价格
                cost_per_1k = model_config.get('cost_per_1k', 0.002)
                cost = (total_tokens / 1000) * cost_per_1k
                
                return LLMResponse(
                    content=content,
                    model=qwen_model,
                    tokens_used=int(total_tokens),
                    cost=cost,
                    response_time=0,
                    provider='qwen'
                )
                
        except Exception as e:
            logger.error(f"千问API调用失败: {str(e)}")
            # 返回错误信息而不是模拟响应
            raise Exception(f"千问API调用失败: {str(e)}")
    
    async def _call_deepseek(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """调用DeepSeek API"""
        api_keys = self._get_api_keys()
        base_urls = self._get_base_urls()
        model_config = get_model_config(model)
        
        if not api_keys['deepseek']:
            raise ValueError("DeepSeek API密钥未配置")
        
        url = f'{base_urls["deepseek"]}/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_keys["deepseek"]}',
            'Content-Type': 'application/json'
        }
        
        # 构建消息列表，优先使用传入的messages参数
        messages = kwargs.get('messages')
        if not messages:
            messages = [{'role': 'user', 'content': prompt}]
        
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
            
            # 使用配置文件中的价格
            cost_per_1k = model_config.get('cost_per_1k', 0.002)
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