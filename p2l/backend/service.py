#!/usr/bin/env python3
"""
P2L后端服务主文件
统一的后端服务，整合所有功能模块
"""

import os
import sys
import asyncio
import logging
import time
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional

# 配置日志
from config import get_service_config, load_env_config

# 加载环境配置
load_env_config()

service_config = get_service_config()
logging.basicConfig(
    level=getattr(logging, service_config["logging"]["level"]),
    format=service_config["logging"]["format"]
)
logger = logging.getLogger(__name__)

# 导入后端模块
try:
    from config import get_all_models, get_model_config
    from p2l_engine import P2LEngine
    from task_analyzer import TaskAnalyzer
    from model_scorer import ModelScorer
    from llm_client import LLMClient
    logger.info("✅ 所有后端模块导入成功")
except ImportError as e:
    logger.error(f"❌ 后端模块导入失败: {e}")
    sys.exit(1)

# 请求模型
class P2LAnalysisRequest(BaseModel):
    prompt: str
    priority: str = "balanced"
    enabled_models: Optional[List[str]] = None

class LLMRequest(BaseModel):
    model: str
    prompt: str

class P2LInferenceRequest(BaseModel):
    code: str
    max_length: int = 512
    temperature: float = 0.7

# 主服务类
class P2LBackendService:
    """P2L后端服务 - 统一版本"""
    
    def __init__(self):
        # 设备检测
        self.device = self._detect_device()
        logger.info(f"🖥️  使用设备: {self.device}")
        
        # 初始化各个模块
        self.all_models = get_all_models()
        self.p2l_engine = P2LEngine(self.device)
        self.task_analyzer = TaskAnalyzer()
        self.model_scorer = ModelScorer(self.all_models)
        
        # 初始化LLM客户端
        self.llm_client = None
        
        logger.info("🚀 P2L后端服务初始化完成")
    
    def _detect_device(self) -> torch.device:
        """检测可用设备"""
        if torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info("🚀 检测到CUDA，使用GPU加速")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = torch.device("mps")
            logger.info("🚀 检测到MPS，使用Apple Silicon加速")
        else:
            device = torch.device("cpu")
            logger.info("💻 使用CPU运行")
        return device
    
    async def _get_llm_client(self) -> LLMClient:
        """获取LLM客户端实例"""
        if self.llm_client is None:
            self.llm_client = LLMClient()
        return self.llm_client
    
    async def analyze_prompt(self, request: P2LAnalysisRequest) -> Dict:
        """P2L智能分析主接口"""
        logger.info(f"📝 收到P2L分析请求: {request.prompt[:50]}...")
        start_time = time.time()
        
        try:
            # 1. P2L语义分析
            complexity_score, language_score = self.p2l_engine.semantic_analysis(request.prompt)
            
            # 2. 任务分析
            task_analysis = self.task_analyzer.analyze_task(
                request.prompt, 
                complexity_score, 
                language_score
            )
            
            # 3. 模型评分和排序
            model_scores = self.model_scorer.calculate_model_scores(
                task_analysis, 
                request.priority, 
                request.enabled_models
            )
            
            # 4. 生成推荐理由
            if model_scores:
                best_model = model_scores[0]
                reasoning = self.model_scorer.generate_recommendation_reasoning(
                    best_model, task_analysis, request.priority
                )
            else:
                reasoning = "无可用模型"
            
            processing_time = round(time.time() - start_time, 3)
            
            # 转换为前端期望的格式
            recommendations = []
            for score_data in model_scores:
                model_config = get_model_config(score_data["model"])
                recommendations.append({
                    "model": score_data["model"],
                    "score": score_data["score"],
                    "provider": model_config["provider"],
                    "cost_per_1k": model_config["cost_per_1k"],
                    "avg_response_time": model_config["avg_response_time"],
                    "strengths": model_config["strengths"],
                    "quality_score": model_config["quality_score"]
                })
            
            result = {
                "task_analysis": task_analysis,
                "model_ranking": model_scores,
                "recommendations": recommendations,  # 前端期望的字段
                "recommended_model": model_scores[0]["model"] if model_scores else None,
                "confidence": model_scores[0]["score"] if model_scores else 0,
                "reasoning": reasoning,
                "processing_time": processing_time,
                "device": str(self.device),
                # 兼容旧版本前端
                "recommendation": {
                    "model": model_scores[0]["model"] if model_scores else None,
                    "score": model_scores[0]["score"] if model_scores else 0,
                    "reasoning": reasoning
                }
            }
            
            logger.info(f"✅ P2L分析完成，耗时: {processing_time}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ P2L分析失败: {e}")
            raise HTTPException(status_code=500, detail=f"P2L分析失败: {str(e)}")
    
    async def generate_llm_response(self, request: LLMRequest) -> Dict:
        """LLM响应生成接口"""
        logger.info(f"🤖 LLM请求: {request.model}")
        
        try:
            client = await self._get_llm_client()
            async with client:
                response = await client.generate_response(
                    request.model, 
                    request.prompt
                )
                
                return {
                    "content": response.content,
                    "model": response.model,
                    "tokens_used": response.tokens_used,
                    "cost": response.cost,
                    "response_time": response.response_time,
                    "provider": response.provider
                }
            
        except Exception as e:
            logger.error(f"❌ LLM调用失败: {e}")
            return {
                "content": f"API暂时不可用: {str(e)}",
                "model": request.model,
                "tokens_used": 0,
                "cost": 0.0,
                "response_time": 0.0,
                "provider": "error"
            }
    
    async def p2l_inference(self, request: P2LInferenceRequest) -> Dict:
        """P2L推理接口"""
        logger.info(f"🧠 P2L推理请求")
        
        try:
            result = self.p2l_engine.code_inference(
                request.code,
                request.max_length,
                request.temperature
            )
            return result
            
        except Exception as e:
            logger.error(f"❌ P2L推理失败: {e}")
            raise HTTPException(status_code=500, detail=f"P2L推理失败: {str(e)}")
    
    def get_health_status(self) -> Dict:
        """健康检查"""
        p2l_models = self.p2l_engine.get_loaded_models()
        
        return {
            "status": "healthy",
            "p2l_models_loaded": len(p2l_models["p2l_models"]),
            "llm_models_available": len(self.all_models),
            "device": str(self.device),
            "p2l_available": p2l_models["p2l_available"],
            "llm_client_available": True,
            "real_api_enabled": True
        }

# 创建FastAPI应用
def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    app = FastAPI(title="P2L Backend Service - Unified", version="3.0.0")
    
    # 添加CORS中间件
    cors_config = service_config["cors"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config["allow_origins"],
        allow_credentials=cors_config["allow_credentials"],
        allow_methods=cors_config["allow_methods"],
        allow_headers=cors_config["allow_headers"],
    )
    
    # 初始化服务
    service = P2LBackendService()
    
    # API路由
    @app.get("/health")
    async def health_check():
        """健康检查接口"""
        return service.get_health_status()
    
    @app.post("/api/p2l/analyze")
    async def analyze_prompt(request: P2LAnalysisRequest):
        """P2L智能分析接口"""
        return await service.analyze_prompt(request)
    
    @app.post("/api/llm/generate")
    async def generate_response(request: LLMRequest):
        """LLM响应生成接口"""
        return await service.generate_llm_response(request)
    
    @app.post("/api/p2l/inference")
    async def p2l_inference(request: P2LInferenceRequest):
        """P2L推理接口"""
        return await service.p2l_inference(request)
    
    @app.get("/api/models")
    async def get_models():
        """获取可用模型列表"""
        return {
            "models": list(service.all_models.keys()),
            "total": len(service.all_models)
        }
    
    # 兼容性路由 (保持向后兼容)
    @app.post("/analyze")
    async def analyze_prompt_compat(request: P2LAnalysisRequest):
        """P2L智能分析接口 (兼容性)"""
        return await service.analyze_prompt(request)
    
    @app.post("/generate")
    async def generate_response_compat(request: LLMRequest):
        """LLM响应生成接口 (兼容性)"""
        return await service.generate_llm_response(request)
    
    @app.get("/models")
    async def get_models_compat():
        """获取可用模型列表 (兼容性)"""
        return {
            "models": list(service.all_models.keys()),
            "total": len(service.all_models)
        }
    
    return app

# 主函数
def main():
    """主函数"""
    import uvicorn
    
    logger.info("🚀 启动P2L后端服务 (统一版本)")
    
    server_config = service_config["server"]
    app = create_app()
    
    uvicorn.run(
        app, 
        host=server_config["host"], 
        port=server_config["port"], 
        log_level=server_config["log_level"],
        reload=server_config["reload"]
    )

if __name__ == "__main__":
    main()