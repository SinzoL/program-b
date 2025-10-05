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

# 导入项目核心模块（唯一依赖）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p2l_core import DEFAULT_MODEL, MODEL_MAPPING, get_backend_status, print_backend_status

# 配置日志
try:
    from .config import get_service_config, load_env_config
except ImportError:
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
    # 尝试相对导入
    from .config import get_all_models, get_model_config
    from .p2l_engine import P2LEngine
    from .task_analyzer import TaskAnalyzer
    from .model_scorer import ModelScorer
    from .llm_client import LLMClient
    logger.info("✅ 所有后端模块导入成功")
except ImportError as e:
    # 如果相对导入失败，尝试绝对导入（兼容直接运行）
    try:
        from config import get_all_models, get_model_config
        from p2l_engine import P2LEngine
        from task_analyzer import TaskAnalyzer
        from model_scorer import ModelScorer
        from llm_client import LLMClient
        logger.info("✅ 所有后端模块导入成功 (绝对导入)")
    except ImportError as e2:
        logger.error(f"❌ 后端模块导入失败: {e2}")
        # 设置默认值以避免NameError
        P2LEngine = None
        TaskAnalyzer = None
        ModelScorer = None
        LLMClient = None
        logger.warning("⚠️  部分模块导入失败，服务可能功能受限")

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
        
        # 初始化各个模块（不加载P2L模型）
        self.all_models = get_all_models()
        self.p2l_engine = None  # 延迟初始化
        self.task_analyzer = TaskAnalyzer()
        self.model_scorer = ModelScorer(self.all_models)
        
        # 初始化LLM客户端
        self.llm_client = None
        
        # 模型加载状态
        self.p2l_loading = False
        self.p2l_loaded = False
        
        logger.info("🚀 P2L后端服务初始化完成（P2L模型将在后台加载）")
        
        # 注意：不在这里启动异步任务，而是在FastAPI启动时处理
    
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
                None, lambda: P2LEngine(self.device)
            )
            
            self.p2l_loaded = True
            self.p2l_loading = False
            logger.info("✅ P2L模型加载完成")
            
        except Exception as e:
            self.p2l_loading = False
            self.p2l_loaded = False
            logger.error(f"❌ P2L模型加载失败: {e}")
            logger.info("💡 服务将以降级模式运行，部分功能可能不可用")
    
    async def _get_llm_client(self) -> LLMClient:
        """获取LLM客户端实例"""
        if self.llm_client is None:
            self.llm_client = LLMClient()
        return self.llm_client
    
    async def analyze_prompt(self, request: P2LAnalysisRequest) -> Dict:
        """P2L智能分析主接口"""
        logger.info(f"📝 收到P2L分析请求: {request.prompt[:50]}...")
        start_time = time.time()
        
        # 检查P2L模型状态
        if not self.p2l_loaded:
            if self.p2l_loading:
                raise HTTPException(status_code=503, detail="P2L模型正在加载中，请稍后重试")
            else:
                raise HTTPException(status_code=503, detail="P2L模型未加载，服务暂时不可用")
        
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
            p2l_models = self.p2l_engine.get_loaded_models()
            p2l_models_count = len(p2l_models["p2l_models"])
            p2l_available = p2l_models["p2l_available"]
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
    
    @app.get("/api/p2l/model-info")
    async def get_p2l_model_info():
        """获取P2L推理模型信息"""
        try:
            # 获取当前配置的默认模型信息
            current_model = DEFAULT_MODEL
            
            # 从MODEL_MAPPING获取local_name
            if current_model in MODEL_MAPPING:
                model_local_name = MODEL_MAPPING[current_model]["local_name"]
            else:
                # 备用方案：从模型名称推导local_name
                model_local_name = current_model.replace("-01112025", "")
            
            # 获取P2L推理引擎实例
            import sys
            import os
            
            # 添加P2L模块路径
            p2l_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'p2l')
            if p2l_path not in sys.path:
                sys.path.append(p2l_path)
            
            # 尝试导入P2L推理引擎
            try:
                from p2l.p2l_inference import P2LInferenceEngine
            except ImportError:
                # 如果上面失败，尝试直接导入
                import p2l.p2l_inference
                P2LInferenceEngine = p2l.p2l_inference.P2LInferenceEngine
            
            inference_engine = P2LInferenceEngine()
            
            # 获取模型详细信息
            model_info = {
                "model_name": model_local_name,  # 直接使用local_name
                "model_path": getattr(inference_engine, 'p2l_model_path', 'unknown'),
                "model_type": type(inference_engine.model).__name__ if inference_engine.model else "未加载",
                "tokenizer_type": type(inference_engine.tokenizer).__name__ if inference_engine.tokenizer else "未加载",
                "is_loaded": inference_engine.model is not None,
                "device": str(getattr(inference_engine, 'device', 'unknown')),
                "current_model_key": current_model
            }
            
            # 调试信息
            logger.info(f"🔍 调试信息 - 设置的model_name: {model_local_name}")
            
            # 如果模型已加载，获取更多详细信息
            if inference_engine.model and hasattr(inference_engine.model, 'config'):
                config = inference_engine.model.config
                model_info.update({
                    "architecture": getattr(config, 'architectures', ['未知'])[0] if hasattr(config, 'architectures') else "未知",
                    "hidden_size": getattr(config, 'hidden_size', 0),
                    "num_layers": getattr(config, 'num_hidden_layers', 0),
                    "num_attention_heads": getattr(config, 'num_attention_heads', 0),
                    "vocab_size": getattr(config, 'vocab_size', 0),
                    "max_position_embeddings": getattr(config, 'max_position_embeddings', 0)
                })
                
                # 计算参数量（但不用于显示名称）
                if hasattr(inference_engine.model, 'parameters'):
                    total_params = sum(p.numel() for p in inference_engine.model.parameters())
                    model_info["total_parameters"] = total_params
                    model_info["parameters_display"] = f"{total_params/1e6:.1f}M" if total_params > 1e6 else f"{total_params/1e3:.1f}K"
            
            # 确保model_name始终使用local_name，不被其他逻辑覆盖
            model_info["model_name"] = model_local_name
            logger.info(f"🔍 最终设置的model_name: {model_local_name}")
            
            return {
                "status": "success",
                "model_info": model_info,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"获取P2L模型信息失败: {e}")
            
            # 获取当前配置的默认模型信息作为备用
            current_model = DEFAULT_MODEL
            if current_model in MODEL_MAPPING:
                model_local_name = MODEL_MAPPING[current_model]["local_name"]
            else:
                model_local_name = current_model.replace("-01112025", "")
            
            return {
                "status": "error",
                "error": str(e),
                "model_info": {
                    "model_name": model_local_name,  # 直接使用local_name
                    "model_type": "未知",
                    "is_loaded": False,
                    "device": "unknown",
                    "current_model_key": current_model
                },
                "timestamp": time.time()
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

    # Nginx代理路由 (去掉/api前缀后的路由)
    @app.post("/p2l/analyze")
    async def p2l_analyze_nginx(request: P2LAnalysisRequest):
        """P2L智能分析接口 (Nginx代理)"""
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