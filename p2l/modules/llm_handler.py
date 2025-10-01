#!/usr/bin/env python3
"""
LLM调用处理模块
负责统一的LLM API调用接口
"""

import time
from typing import Dict
import logging

logger = logging.getLogger(__name__)

# 导入LLM客户端
try:
    from llm_client import LLMClient
    LLM_CLIENT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LLM客户端导入失败: {e}")
    LLM_CLIENT_AVAILABLE = False

class LLMHandler:
    """LLM调用处理器"""
    
    def __init__(self):
        self.llm_client = None
        if LLM_CLIENT_AVAILABLE:
            self.llm_client = LLMClient()
            logger.info("✅ LLM客户端初始化成功")
        else:
            logger.warning("❌ LLM客户端不可用")
    
    async def generate_response(self, model: str, prompt: str, analysis: Dict = None) -> Dict:
        """生成LLM响应"""
        logger.info(f"调用LLM: {model}")
        
        start_time = time.time()
        
        try:
            # 使用统一的LLM客户端处理所有模型
            if self.llm_client:
                async with self.llm_client as client:
                    llm_response = await client.generate_response(
                        model=model,
                        prompt=prompt,
                        max_tokens=2000,
                        temperature=0.7
                    )
                    
                    logger.info(f"✅ 真实API调用成功: {model}")
                    
                    return {
                        "model": llm_response.model,
                        "response": llm_response.content,
                        "content": llm_response.content,
                        "response_time": round(llm_response.response_time, 2),
                        "tokens": llm_response.tokens_used,
                        "tokens_used": llm_response.tokens_used,
                        "cost": round(llm_response.cost, 4),
                        "provider": llm_response.provider,
                        "is_real_api": True
                    }
            else:
                raise Exception("LLM客户端不可用")
                
        except Exception as e:
            logger.error(f"❌ LLM API调用失败: {model} - {e}")
            return {
                "model": model,
                "response": f"抱歉，{model} 模型API暂时不可用，请稍后重试。",
                "content": f"抱歉，{model} 模型API暂时不可用，请稍后重试。",
                "response_time": 0.1,
                "tokens": 0,
                "tokens_used": 0,
                "cost": 0.0,
                "provider": "error",
                "is_real_api": False
            }
    
    def is_available(self) -> bool:
        """检查LLM客户端是否可用"""
        return self.llm_client is not None
    
    def get_client_info(self) -> Dict:
        """获取客户端信息"""
        return {
            "llm_client_available": LLM_CLIENT_AVAILABLE,
            "real_api_enabled": self.llm_client is not None
        }