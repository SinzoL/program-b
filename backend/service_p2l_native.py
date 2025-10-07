#!/usr/bin/env python3
"""
P2L原生后端服务
完全基于P2L模型的Bradley-Terry系数进行智能路由
"""

import os
import sys
import asyncio
import logging
import time
import torch
import warnings

# 抑制urllib3的OpenSSL警告
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional

# 导入项目核心模块
try:
    from model_p2l.p2l_core import DEFAULT_MODEL, MODEL_MAPPING, get_backend_status, print_backend_status
except ImportError:
    # 备用导入路径
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from p2l_core import DEFAULT_MODEL, MODEL_MAPPING, get_backend_status, print_backend_status
    except ImportError:
        # 最后的备用方案
        DEFAULT_MODEL = "p2l-135m-grk-01112025"
        MODEL_MAPPING = {}
        def get_backend_status(): return {"p2l_ready": False}
        def print_backend_status(): print("⚠️ P2L核心模块未找到")

# 配置日志
try:
    from .config import get_service_config, load_env_config, get_all_models, get_model_config
except ImportError:
    from config import get_service_config, load_env_config, get_all_models, get_model_config

# 加载环境配置
load_env_config()

service_config = get_service_config()
logging.basicConfig(
    level=getattr(logging, service_config["logging"]["level"]),
    format=service_config["logging"]["format"]
)
logger = logging.getLogger(__name__)

# 导入P2L原生模块
try:
    # 尝试相对导入
    from .p2l_engine import P2LEngine
    from .p2l_model_scorer import P2LModelScorer  # 新的P2L原生评分器
    from .unified_client import UnifiedLLMClient
    logger.info("✅ P2L原生模块导入成功")
except ImportError as e:
    # 如果相对导入失败，尝试绝对导入
    try:
        from p2l_engine import P2LEngine
        from p2l_model_scorer import P2LModelScorer
        from unified_client import UnifiedLLMClient
        logger.info("✅ P2L原生模块导入成功 (绝对导入)")
    except ImportError as e2:
        logger.error(f"❌ P2L原生模块导入失败: {e2}")
        # 设置默认值以避免NameError
        P2LEngine = None
        P2LModelScorer = None
        UnifiedLLMClient = None
        logger.warning("⚠️  部分模块导入失败，服务可能功能受限")

# 请求模型
class P2LAnalysisRequest(BaseModel):
    prompt: str
    priority: str = "balanced"
    enabled_models: Optional[List[str]] = None
    budget: Optional[float] = None  # 新增：预算约束

class LLMRequest(BaseModel):
    model: str
    prompt: str
    messages: Optional[List[dict]] = None
    max_tokens: Optional[int] = 2000
    temperature: Optional[float] = 0.7

class P2LInferenceRequest(BaseModel):
    code: str
    max_length: int = 512
    temperature: float = 0.7

# P2L原生后端服务
class P2LNativeBackendService:
    """P2L原生后端服务 - 完全基于Bradley-Terry系数的智能路由"""
    
    def __init__(self):
        # 设备检测
        self.device = self._detect_device()
        logger.info(f"🖥️  使用设备: {self.device}")
        
        # 初始化各个模块
        self.all_models = get_all_models()
        self.p2l_engine = None  # 延迟初始化
        self.p2l_model_scorer = None  # P2L原生评分器，需要p2l_engine初始化后创建
        
        # 初始化统一LLM客户端
        self.llm_client = None
        
        # 模型加载状态
        self.p2l_loading = False
        self.p2l_loaded = False
        
        logger.info("🚀 P2L原生后端服务初始化完成（P2L模型将在后台加载）")
    
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
    
    async def _load_p2l_model_async(self):
        """异步加载P2L模型"""
        try:
            self.p2l_loading = True
            logger.info("🔄 开始后台加载P2L模型...")
            
            # 在后台线程中加载模型，避免阻塞主线程
            loop = asyncio.get_event_loop()
            self.p2l_engine = await loop.run_in_executor(
                None, lambda: P2LEngine(device=str(self.device))
            )
            
            # 初始化P2L原生评分器
            self.p2l_model_scorer = P2LModelScorer(
                model_configs=self.all_models,
                p2l_engine=self.p2l_engine
            )
            
            self.p2l_loaded = True
            self.p2l_loading = False
            logger.info("✅ P2L原生模型和评分器加载完成")
            
        except Exception as e:
            self.p2l_loading = False
            self.p2l_loaded = False
            logger.error(f"❌ P2L模型加载失败: {e}")
            logger.info("💡 服务将以降级模式运行，部分功能可能不可用")
    
    async def _get_llm_client(self) -> UnifiedLLMClient:
        """获取统一LLM客户端实例"""
        if self.llm_client is None:
            self.llm_client = UnifiedLLMClient()
        return self.llm_client
    
    async def analyze_prompt(self, request: P2LAnalysisRequest) -> Dict:
        """P2L原生智能分析主接口"""
        logger.info(f"🧠 收到P2L原生分析请求: {request.prompt[:50]}...")
        start_time = time.time()
        
        # 检查P2L模型状态
        if not self.p2l_loaded:
            if self.p2l_loading:
                raise HTTPException(status_code=503, detail="P2L模型正在加载中，请稍后重试")
            else:
                raise HTTPException(status_code=503, detail="P2L模型未加载，服务暂时不可用")
        
        try:
            # 使用P2L原生评分器进行分析
            model_rankings, routing_info = self.p2l_model_scorer.calculate_p2l_scores(
                prompt=request.prompt,
                priority=request.priority,
                enabled_models=request.enabled_models,
                budget=request.budget
            )
            
            # 生成推荐理由
            if model_rankings:
                best_model = model_rankings[0]
                reasoning = self.p2l_model_scorer.generate_recommendation_reasoning(
                    best_model, routing_info, request.priority
                )
            else:
                reasoning = "无可用模型"
            
            processing_time = round(time.time() - start_time, 3)
            
            # 转换为前端期望的格式
            recommendations = []
            for ranking in model_rankings:
                recommendations.append({
                    "model": ranking["model"],
                    "score": ranking["score"],
                    "p2l_coefficient": ranking.get("p2l_coefficient", 0),
                    "provider": ranking["provider"],
                    "cost_per_1k": ranking["cost_per_1k"],
                    "avg_response_time": ranking["avg_response_time"]
                })
            
            result = {
                "model_ranking": model_rankings,
                "recommendations": recommendations,
                "recommended_model": model_rankings[0]["model"] if model_rankings else None,
                "confidence": model_rankings[0]["score"] if model_rankings else 0,
                "reasoning": reasoning,
                "processing_time": processing_time,
                "device": str(self.device),
                "p2l_native": True,  # 标识这是P2L原生结果
                "routing_info": routing_info,  # 完整的路由信息
                # 兼容旧版本前端
                "recommendation": {
                    "model": model_rankings[0]["model"] if model_rankings else None,
                    "score": model_rankings[0]["score"] if model_rankings else 0,
                    "reasoning": reasoning
                }
            }
            
            logger.info(f"✅ P2L原生分析完成，策略: {routing_info.get('strategy', 'unknown')}, 耗时: {processing_time}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ P2L原生分析失败: {e}")
            raise HTTPException(status_code=500, detail=f"P2L原生分析失败: {str(e)}")
    
    async def generate_llm_response(self, request: LLMRequest) -> Dict:
        """LLM响应生成接口（保持不变）"""
        logger.info(f"🤖 LLM请求: {request.model}")
        
        try:
            client = await self._get_llm_client()
            async with client:
                # 构建kwargs参数
                kwargs = {
                    'max_tokens': request.max_tokens,
                    'temperature': request.temperature
                }
                
                # 如果有messages参数，传递给客户端
                if request.messages:
                    kwargs['messages'] = request.messages
                
                response = await client.generate_response(
                    request.model, 
                    request.prompt,
                    **kwargs
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
            
            # 根据错误类型提供更详细的错误信息
            error_message = str(e)
            if "timeout" in error_message.lower():
                error_message = f"请求超时：{request.model} 正在处理复杂问题，请稍后重试"
            elif "rate limit" in error_message.lower():
                error_message = f"API调用频率限制：{request.model} 请稍后重试"
            elif "quota" in error_message.lower():
                error_message = f"API配额不足：{request.model} 请检查账户余额"
            elif "unauthorized" in error_message.lower():
                error_message = f"API密钥无效：{request.model} 请检查配置"
            else:
                error_message = f"API暂时不可用: {error_message}"
            
            return {
                "content": error_message,
                "response": error_message,  # 兼容前端
                "model": request.model,
                "tokens_used": 0,
                "cost": 0.0,
                "response_time": 0.0,
                "provider": "error",
                "error_type": "api_error",
                "original_error": str(e)
            }
    
    async def p2l_inference(self, request: P2LInferenceRequest) -> Dict:
        """P2L推理接口（保持不变）"""
        logger.info(f"🧠 P2L推理请求")
        
        # 检查P2L模型状态
        if not self.p2l_loaded:
            if self.p2l_loading:
                raise HTTPException(status_code=503, detail="P2L模型正在加载中，请稍后重试")
            else:
                raise HTTPException(status_code=503, detail="P2L模型未加载，服务暂时不可用")
        
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
        if self.p2l_loaded and self.p2l_engine:
            p2l_status = self.p2l_engine.get_status()
            p2l_models_count = p2l_status.get("supported_models", 0)
            p2l_available = p2l_status.get("is_loaded", False)
        else:
            p2l_models_count = 0
            p2l_available = False
        
        return {
            "status": "healthy",
            "p2l_models_loaded": p2l_models_count,
            "llm_models_available": len(self.all_models),
            "device": str(self.device),
            "p2l_available": p2l_available,
            "p2l_loading": self.p2l_loading,
            "p2l_loaded": self.p2l_loaded,
            "llm_client_available": True,
            "real_api_enabled": True,
            "p2l_native_scorer": self.p2l_model_scorer is not None,
            "service_type": "p2l_native"  # 标识服务类型
        }
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return list(self.all_models.keys())

# 创建FastAPI应用
def create_app() -> FastAPI:
    """创建P2L原生FastAPI应用实例"""
    app = FastAPI(
        title="P2L Native Backend Service", 
        version="4.0.0",
        description="完全基于P2L模型Bradley-Terry系数的智能路由服务"
    )
    
    # 添加CORS中间件
    cors_config = service_config["cors"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config["allow_origins"],
        allow_credentials=cors_config["allow_credentials"],
        allow_methods=cors_config["allow_methods"],
        allow_headers=cors_config["allow_headers"],
    )
    
    # 初始化P2L原生服务
    service = P2LNativeBackendService()
    
    # 启动事件：开始异步加载P2L模型
    @app.on_event("startup")
    async def startup_event():
        """应用启动时的异步任务"""
        if service.p2l_engine is None and not service.p2l_loading:
            asyncio.create_task(service._load_p2l_model_async())
    
    # API路由
    @app.get("/health")
    async def health_check():
        """健康检查接口"""
        return service.get_health_status()
    
    @app.get("/api/health")
    async def api_health_check():
        """API健康检查接口 (带/api前缀)"""
        return service.get_health_status()
    
    @app.post("/api/p2l/analyze")
    async def analyze_prompt(request: P2LAnalysisRequest):
        """P2L原生智能分析接口"""
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
    
    @app.get("/api/p2l/model-info")
    async def get_p2l_model_info():
        """获取P2L推理模型信息"""
        try:
            # 使用当前P2L引擎的信息
            if service.p2l_engine:
                p2l_status = service.p2l_engine.get_status()
                model_info = {
                    "model_name": "p2l-135m-grk",
                    "model_path": str(service.p2l_engine.model_path),
                    "model_type": "P2L",
                    "tokenizer_type": "AutoTokenizer",
                    "is_loaded": p2l_status.get("is_loaded", False),
                    "device": service.p2l_engine.device,
                    "current_model_key": "p2l-135m-grk",
                    "service_type": "p2l_native",
                    "native_scorer_loaded": service.p2l_model_scorer is not None,
                    "supported_models_count": p2l_status.get("supported_models", 0)
                }
            else:
                model_info = {
                    "model_name": "p2l-135m-grk",
                    "model_path": "未加载",
                    "model_type": "P2L",
                    "tokenizer_type": "未加载",
                    "is_loaded": False,
                    "device": "unknown",
                    "current_model_key": "p2l-135m-grk",
                    "service_type": "p2l_native",
                    "native_scorer_loaded": False,
                    "supported_models_count": 0
                }
            
            return {
                "status": "success",
                "model_info": model_info,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"获取P2L模型信息失败: {e}")
            
            return {
                "status": "error",
                "error": str(e),
                "model_info": {
                    "model_name": "p2l-135m-grk",
                    "model_type": "P2L",
                    "is_loaded": False,
                    "device": "unknown",
                    "current_model_key": "p2l-135m-grk",
                    "service_type": "p2l_native"
                },
                "timestamp": time.time()
            }
    
    # 兼容性路由 (保持向后兼容)
    @app.post("/analyze")
    async def analyze_prompt_compat(request: P2LAnalysisRequest):
        """P2L原生智能分析接口 (兼容性)"""
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

    # Nginx代理路由 (去掉/api前缀后的路由)
    @app.post("/p2l/analyze")
    async def p2l_analyze_nginx(request: P2LAnalysisRequest):
        """P2L原生智能分析接口 (Nginx代理)"""
        return await service.analyze_prompt(request)

    @app.post("/llm/generate")
    async def llm_generate_nginx(request: LLMRequest):
        """LLM响应生成接口 (Nginx代理)"""
        return await service.generate_llm_response(request)

    @app.post("/p2l/inference")
    async def p2l_inference_nginx(request: P2LInferenceRequest):
        """P2L推理接口 (Nginx代理)"""
        return await service.p2l_inference(request)

    @app.get("/p2l/model-info")
    async def p2l_model_info_nginx():
        """获取P2L推理模型信息 (Nginx代理)"""
        return await get_p2l_model_info()
    
    return app

# 主函数
def main():
    """主函数"""
    import uvicorn
    
    logger.info("🚀 启动P2L原生后端服务")
    
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