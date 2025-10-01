#!/usr/bin/env python3
"""
P2L后端服务
提供P2L智能路由和LLM调用的完整后端API
"""

import asyncio
import json
import time
import os
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import uvicorn
import logging

# 导入P2L推理模块
try:
    from p2l.model import load_model as load_p2l_model, generate_text
    from p2l.p2l_inference import P2LInferenceEngine
    P2L_AVAILABLE = True
except ImportError as e:
    logging.warning(f"P2L模块导入失败: {e}")
    P2L_AVAILABLE = False

# 导入LLM客户端
try:
    from llm_client import LLMClient
    LLM_CLIENT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LLM客户端导入失败: {e}")
    LLM_CLIENT_AVAILABLE = False

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="P2L智能路由后端服务",
    description="提供P2L分析和LLM调用的完整后端API",
    version="2.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://192.168.117.66:3000",
        "http://192.168.255.10:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 请求模型
class P2LAnalysisRequest(BaseModel):
    prompt: str
    mode: str = "balanced"  # performance, cost, speed, balanced
    models: Optional[List[str]] = None  # 启用的模型列表
    priority: str = "performance"  # 兼容旧字段

class LLMGenerateRequest(BaseModel):
    model: str
    prompt: str
    analysis: Optional[Dict] = None

class P2LInferenceRequest(BaseModel):
    code: str
    max_length: Optional[int] = 512
    temperature: Optional[float] = 0.7

class P2LBackendService:
    def __init__(self):
        self.p2l_models = {}
        self.p2l_inference_engine = None
        self.model_configs = self._load_model_configs()
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.llm_client = None
        logger.info(f"使用设备: {self.device}")
        
        # 尝试加载P2L模型
        self._load_p2l_models()
        
        # 尝试加载P2L推理引擎
        if P2L_AVAILABLE:
            self._load_p2l_inference_engine()
        
        # 初始化LLM客户端
        if LLM_CLIENT_AVAILABLE:
            self.llm_client = LLMClient()
            logger.info("✅ LLM客户端初始化成功")
        else:
            logger.warning("❌ LLM客户端不可用，将使用模拟响应")
    
    def _load_model_configs(self) -> Dict:
        """加载模型配置信息 - 只包含有API密钥的主流模型"""
        return {
            # OpenAI 主流模型
            "gpt-4o": {
                "provider": "openai",
                "cost_per_1k": 0.03,
                "avg_response_time": 2.5,
                "strengths": ["编程", "复杂推理", "数学"],
                "quality_score": 0.95
            },
            "gpt-4o-mini": {
                "provider": "openai", 
                "cost_per_1k": 0.0015,
                "avg_response_time": 1.2,
                "strengths": ["快速响应", "成本效益"],
                "quality_score": 0.82
            },
            # Claude 主流模型
            "claude-3-5-sonnet-20241022": {
                "provider": "anthropic",
                "cost_per_1k": 0.025,
                "avg_response_time": 2.8,
                "strengths": ["创意写作", "文学分析"],
                "quality_score": 0.93
            },
            # Gemini 主流模型
            "gemini-1.5-pro": {
                "provider": "google",
                "cost_per_1k": 0.015,
                "avg_response_time": 2.0,
                "strengths": ["多模态", "长文本", "推理"],
                "quality_score": 0.89
            },
            # DeepSeek 主流模型
            "deepseek-chat": {
                "provider": "deepseek",
                "cost_per_1k": 0.002,
                "avg_response_time": 1.8,
                "strengths": ["对话", "中文理解", "快速响应"],
                "quality_score": 0.86
            },
            "deepseek-coder": {
                "provider": "deepseek",
                "cost_per_1k": 0.002,
                "avg_response_time": 1.6,
                "strengths": ["编程", "代码生成", "技术问答"],
                "quality_score": 0.88
            },
            # 千问主流模型
            "qwen2.5-72b-instruct": {
                "provider": "qwen",
                "cost_per_1k": 0.002,  # 约$0.002 (¥0.015转换)
                "avg_response_time": 2.0,
                "strengths": ["中文理解", "推理", "编程", "数学"],
                "quality_score": 0.90
            },
            "qwen-plus": {
                "provider": "qwen", 
                "cost_per_1k": 0.004,
                "avg_response_time": 2.5,
                "strengths": ["复杂推理", "长文本", "多轮对话"],
                "quality_score": 0.92
            },
            "qwen-turbo": {
                "provider": "qwen",
                "cost_per_1k": 0.001,
                "avg_response_time": 1.0,
                "strengths": ["快速响应", "成本效益", "日常对话"],
                "quality_score": 0.85
            }
        }
    
    def _load_p2l_models(self):
        """加载可用的P2L模型"""
        models_dir = "./models"
        if not os.path.exists(models_dir):
            logger.warning("模型目录不存在")
            return
        
        for item in os.listdir(models_dir):
            if item.startswith('p2l-') and os.path.isdir(os.path.join(models_dir, item)):
                model_path = os.path.join(models_dir, item)
                try:
                    logger.info(f"加载P2L模型: {item}")
                    tokenizer = AutoTokenizer.from_pretrained(model_path)
                    model = AutoModelForCausalLM.from_pretrained(
                        model_path,
                        torch_dtype=torch.float32,
                        device_map=None
                    )
                    model.to(self.device)
                    model.eval()
                    
                    self.p2l_models[item] = {
                        "tokenizer": tokenizer,
                        "model": model,
                        "path": model_path
                    }
                    logger.info(f"✅ P2L模型 {item} 加载成功")
                    break  # 只加载第一个可用模型
                except Exception as e:
                    logger.error(f"❌ P2L模型 {item} 加载失败: {e}")
    
    def _load_p2l_inference_engine(self):
        """加载P2L推理引擎"""
        try:
            logger.info("正在加载P2L推理引擎...")
            
            # 尝试从models目录加载
            models_dir = "./models"
            p2l_model_path = None
            
            if os.path.exists(models_dir):
                for item in os.listdir(models_dir):
                    if item.startswith('p2l-') and os.path.isdir(os.path.join(models_dir, item)):
                        p2l_model_path = os.path.join(models_dir, item)
                        break
            
            # 使用P2L推理引擎
            if p2l_model_path:
                model, tokenizer = load_p2l_model(p2l_model_path, device=str(self.device))
            else:
                # 创建默认推理引擎
                model, tokenizer = load_p2l_model("", device=str(self.device))
            
            if isinstance(model, P2LInferenceEngine):
                self.p2l_inference_engine = model
                logger.info("✅ P2L推理引擎加载成功")
            else:
                logger.warning("加载的不是P2L推理引擎，使用标准模型")
                
        except Exception as e:
            logger.error(f"❌ P2L推理引擎加载失败: {e}")
            # 创建基本的推理引擎作为后备
            try:
                self.p2l_inference_engine = P2LInferenceEngine(device=str(self.device))
                logger.info("✅ 创建了基本P2L推理引擎")
            except Exception as e2:
                logger.error(f"❌ 基本P2L推理引擎创建失败: {e2}")
    
    def analyze_task(self, prompt: str) -> Dict:
        """使用P2L神经网络模型分析任务特征"""
        # 优先使用P2L推理引擎
        if self.p2l_inference_engine:
            try:
                logger.info("使用P2L推理引擎进行任务分析...")
                result = self.p2l_inference_engine.analyze_task_complexity(prompt)
                
                # 转换P2L推理引擎的输出格式
                task_analysis = {
                    "task_type": result.get("task_type", "通用"),
                    "complexity": result.get("complexity", "中等"),
                    "language": result.get("language", "中文"),
                    "length": len(prompt),
                    "p2l_scores": {
                        "complexity": result.get("complexity_score", 0.5),
                        "confidence": result.get("confidence", 0.8)
                    }
                }
                
                logger.info(f"🧠 P2L推理引擎分析: {task_analysis}")
                return task_analysis
                
            except Exception as e:
                logger.warning(f"P2L推理引擎分析失败，使用传统方法: {e}")
        
        # 如果有传统P2L模型，使用增强的规则+语义分析
        elif self.p2l_models:
            try:
                model_name = list(self.p2l_models.keys())[0]
                p2l_model = self.p2l_models[model_name]
                tokenizer = p2l_model["tokenizer"]
                model = p2l_model["model"]
                
                logger.info(f"🧠 使用P2L模型进行语义增强分析...")
                
                # 使用P2L模型进行语义特征提取
                inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=512)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = model(**inputs)
                    
                    # 获取隐藏状态作为语义特征
                    if hasattr(outputs, 'hidden_states') and outputs.hidden_states is not None:
                        # 使用最后一层的隐藏状态
                        hidden_states = outputs.hidden_states[-1]  # [batch_size, seq_len, hidden_size]
                        # 平均池化得到句子级别的表示
                        sentence_embedding = hidden_states.mean(dim=1)  # [batch_size, hidden_size]
                        semantic_features = sentence_embedding[0]  # [hidden_size]
                    else:
                        # 如果没有隐藏状态，使用logits的统计特征
                        logits = outputs.logits  # [batch_size, seq_len, vocab_size]
                        # 计算logits的统计特征作为语义表示
                        semantic_features = logits.mean(dim=(0, 1))  # [vocab_size] -> 平均到标量特征
                
                # 基于语义特征计算复杂度和语言分数
                if semantic_features.dim() == 1:
                    # 使用语义特征的统计信息
                    feature_mean = semantic_features.mean().item()
                    feature_std = semantic_features.std().item()
                    feature_max = semantic_features.max().item()
                    
                    # 将统计特征映射到0-1范围
                    complexity_score = min(max((feature_std / (abs(feature_mean) + 1e-6)), 0), 1)
                    language_score = min(max((feature_max / (abs(feature_mean) + 1e-6)), 0), 1)
                else:
                    complexity_score = 0.5
                    language_score = 0.5
                
                logger.info(f"🔍 语义特征分析: mean={feature_mean:.3f}, std={feature_std:.3f}, max={feature_max:.3f}")
                logger.info(f"🔍 计算得分: complexity_score={complexity_score:.3f}, language_score={language_score:.3f}")
                
                # 结合规则方法和语义分析
                task_analysis = self._enhanced_task_analysis(prompt, complexity_score, language_score)
                logger.info(f"🧠 P2L增强分析完成: {task_analysis}")
                
                return task_analysis
                
            except Exception as e:
                logger.warning(f"P2L模型分析失败，使用规则方法: {e}")
        
        # 备用规则方法
        return self._rule_based_analysis(prompt)
    
    def _enhanced_task_analysis(self, prompt: str, complexity_score: float, language_score: float) -> Dict:
        """增强的任务分析方法，结合规则和语义特征"""
        prompt_lower = prompt.lower()
        
        # 更精确的任务类型识别
        task_type = "通用"
        confidence = 0.5
        
        # 编程相关关键词检测（权重更高）
        programming_keywords = [
            "code", "python", "javascript", "js", "function", "method", "class",
            "程序", "代码", "编程", "函数", "方法", "类", "算法", "实现",
            "下划线", "驼峰", "camelcase", "underscore", "转换", "转化",
            "变量", "命名", "格式", "string", "字符串"
        ]
        programming_score = sum(1 for word in programming_keywords if word in prompt_lower)
        
        # 创意写作关键词
        creative_keywords = ["story", "poem", "creative", "故事", "诗歌", "创意", "写作", "小说", "散文"]
        creative_score = sum(1 for word in creative_keywords if word in prompt_lower)
        
        # 翻译关键词
        translation_keywords = ["translate", "翻译", "中文", "english", "french", "语言", "转译"]
        translation_score = sum(1 for word in translation_keywords if word in prompt_lower)
        
        # 数学关键词
        math_keywords = ["math", "calculate", "数学", "计算", "solve", "equation", "公式", "求解"]
        math_score = sum(1 for word in math_keywords if word in prompt_lower)
        
        # 分析关键词
        analysis_keywords = ["analyze", "explain", "分析", "解释", "describe", "描述", "评价"]
        analysis_score = sum(1 for word in analysis_keywords if word in prompt_lower)
        
        # 确定任务类型和置信度
        scores = {
            "编程": programming_score,
            "创意写作": creative_score,
            "翻译": translation_score,
            "数学": math_score,
            "分析": analysis_score
        }
        
        max_score = max(scores.values())
        if max_score > 0:
            task_type = max(scores, key=scores.get)
            confidence = min(0.9, 0.5 + max_score * 0.1)
        
        # 特殊模式检测：下划线转驼峰
        if any(word in prompt_lower for word in ["下划线", "驼峰", "camelcase", "underscore"]):
            task_type = "编程"
            confidence = 0.95
            logger.info("🎯 检测到字符串格式转换任务，高置信度识别为编程类型")
        
        # 基于语义特征和关键词调整复杂度
        base_complexity = complexity_score
        if task_type == "编程" and max_score >= 2:
            base_complexity = max(base_complexity, 0.6)  # 编程任务通常较复杂
        
        if base_complexity > 0.7:
            complexity = "复杂"
        elif base_complexity < 0.3:
            complexity = "简单"
        else:
            complexity = "中等"
        
        # 语言检测（中文字符比例）
        chinese_chars = sum(1 for char in prompt if '\u4e00' <= char <= '\u9fff')
        total_chars = len(prompt)
        chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0
        
        language = "中文" if chinese_ratio > 0.3 else "英文"
        
        result = {
            "task_type": task_type,
            "complexity": complexity,
            "language": language,
            "length": len(prompt),
            "confidence": confidence,
            "p2l_scores": {
                "complexity": base_complexity,
                "language": language_score,
                "keyword_scores": scores,
                "chinese_ratio": chinese_ratio
            }
        }
        
        logger.info(f"📊 任务分析详情: {result}")
        return result

    def _interpret_p2l_output(self, prompt: str, complexity_score: float, language_score: float) -> Dict:
        """解释P2L模型输出（保留兼容性）"""
        return self._enhanced_task_analysis(prompt, complexity_score, language_score)
    
    def _rule_based_analysis(self, prompt: str) -> Dict:
        """备用的规则分析方法"""
        prompt_lower = prompt.lower()
        
        # 任务类型识别
        task_type = "通用"
        if any(word in prompt_lower for word in ["code", "python", "javascript", "程序", "代码", "编程", "function"]):
            task_type = "编程"
        elif any(word in prompt_lower for word in ["story", "poem", "creative", "故事", "诗歌", "创意", "写作"]):
            task_type = "创意写作"
        elif any(word in prompt_lower for word in ["translate", "翻译", "中文", "english", "french"]):
            task_type = "翻译"
        elif any(word in prompt_lower for word in ["math", "calculate", "数学", "计算", "solve", "equation"]):
            task_type = "数学"
        elif any(word in prompt_lower for word in ["analyze", "explain", "分析", "解释", "describe"]):
            task_type = "分析"
        
        # 复杂度评估
        complexity = "简单"
        if len(prompt) > 100 or any(word in prompt_lower for word in ["complex", "advanced", "详细", "完整"]):
            complexity = "复杂"
        elif len(prompt) > 50:
            complexity = "中等"
        
        # 语言检测
        language = "英文"
        chinese_chars = sum(1 for char in prompt if '\u4e00' <= char <= '\u9fff')
        if chinese_chars > len(prompt) * 0.3:
            language = "中文"
        
        return {
            "task_type": task_type,
            "complexity": complexity,
            "language": language,
            "length": len(prompt)
        }
    
    def calculate_model_scores(self, task_analysis: Dict, priority: str, enabled_models: Optional[List[str]] = None) -> List[Dict]:
        """计算模型分数并排序 - 使用百分制评分"""
        scores = []
        
        # 如果指定了启用的模型列表，只计算这些模型的分数
        models_to_score = self.model_configs.items()
        if enabled_models:
            models_to_score = [(name, config) for name, config in self.model_configs.items() if name in enabled_models]
            logger.info(f"只计算启用模型的分数: {[name for name, _ in models_to_score]}")
        
        for model_name, config in models_to_score:
            # 基础分数 (40分)
            base_score = config["quality_score"] * 40
            
            # 任务匹配度 (25分)
            task_score = 0
            if task_analysis["task_type"] in config["strengths"]:
                task_score = 25
            elif any(strength in task_analysis["task_type"] for strength in config["strengths"]):
                task_score = 15
            else:
                task_score = 5
            
            # 语言匹配度 (15分)
            language_score = 0
            if task_analysis["language"] == "中文" and "中文" in config["strengths"]:
                language_score = 15
            elif task_analysis["language"] == "中文":
                language_score = 8
            else:
                language_score = 10
            
            # 优先级匹配度 (20分)
            priority_score = 0
            if priority == "cost":
                if config["cost_per_1k"] < 0.005:
                    priority_score = 20
                elif config["cost_per_1k"] < 0.015:
                    priority_score = 15
                else:
                    priority_score = 8
            elif priority == "speed":
                if config["avg_response_time"] < 1.5:
                    priority_score = 20
                elif config["avg_response_time"] < 2.5:
                    priority_score = 15
                else:
                    priority_score = 8
            elif priority == "performance":
                if config["quality_score"] > 0.90:
                    priority_score = 20
                elif config["quality_score"] > 0.85:
                    priority_score = 15
                else:
                    priority_score = 10
            else:  # balanced
                priority_score = 15
            
            # 总分 = 基础分 + 任务分 + 语言分 + 优先级分 (满分100)
            final_score = base_score + task_score + language_score + priority_score
            
            # 确保分数在0-100之间
            final_score = max(0, min(100, final_score))
            
            scores.append({
                "model": model_name,
                "score": round(final_score, 1),
                "config": config
            })
        
        # 按分数排序
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores
    
    async def p2l_analyze(self, request: P2LAnalysisRequest) -> Dict:
        """P2L智能分析"""
        logger.info(f"P2L分析请求: {request.prompt[:50]}...")
        logger.info(f"启用的模型: {request.models}")
        
        # 分析任务
        task_analysis = self.analyze_task(request.prompt)
        
        # 使用mode字段，如果没有则使用priority字段
        priority_mode = request.mode or request.priority
        
        # 计算所有模型的分数（不再限制为启用的模型）
        model_scores = self.calculate_model_scores(task_analysis, priority_mode, enabled_models=None)
        
        # 生成推荐理由
        best_model = model_scores[0]
        reasoning_parts = []
        
        if task_analysis["task_type"] in best_model["config"]["strengths"]:
            reasoning_parts.append(f"擅长{task_analysis['task_type']}任务")
        
        if task_analysis["language"] == "中文" and "中文" in best_model["config"]["strengths"]:
            reasoning_parts.append("中文理解能力强")
        
        if request.priority == "cost" and best_model["config"]["cost_per_1k"] < 0.01:
            reasoning_parts.append("成本效益高")
        elif request.priority == "speed" and best_model["config"]["avg_response_time"] < 2.0:
            reasoning_parts.append("响应速度快")
        elif request.priority == "performance" and best_model["config"]["quality_score"] > 0.90:
            reasoning_parts.append("性能表现优秀")
        
        reasoning = "；".join(reasoning_parts) if reasoning_parts else "综合性能最佳"
        
        result = {
            "recommended_model": best_model["model"],
            "confidence": best_model["score"],
            "estimated_cost": f"${best_model['config']['cost_per_1k']}/1K tokens",
            "estimated_time": f"{best_model['config']['avg_response_time']}s",
            "task_analysis": task_analysis,
            "reasoning": reasoning,
            "recommendations": [
                {
                    "model": item["model"], 
                    "score": item["score"],
                    "provider": item["config"]["provider"],
                    "cost_per_1k": item["config"]["cost_per_1k"],
                    "avg_response_time": item["config"]["avg_response_time"],
                    "strengths": item["config"]["strengths"],
                    "quality_score": item["config"]["quality_score"]
                } 
                for item in model_scores
            ],
            "model_rankings": [
                {"model": item["model"], "score": item["score"]} 
                for item in model_scores
            ],
            "priority_mode": request.priority
        }
        
        logger.info(f"P2L推荐: {result['recommended_model']}")
        return result
    
    async def generate_llm_response(self, request: LLMGenerateRequest) -> Dict:
        """真实LLM响应生成"""
        logger.info(f"调用LLM: {request.model}")
        
        start_time = time.time()
        
        try:
            # 对于DeepSeek模型，使用DeepSeek客户端
            if request.model.startswith('deepseek'):

                
                if deepseek_client.api_key:
                    logger.info(f"使用DeepSeek API调用: {request.model}")
                    llm_response = deepseek_client.generate_response(
                        model=request.model,
                        prompt=request.prompt,
                        max_tokens=2000,
                        temperature=0.7
                    )
                    
                    logger.info(f"✅ DeepSeek API调用成功: {request.model}")
                    return llm_response
                else:
                    raise Exception("DeepSeek API密钥未配置")
            

            
            # 尝试使用其他LLM API
            elif self.llm_client:
                async with self.llm_client as client:
                    llm_response = await client.generate_response(
                        model=request.model,
                        prompt=request.prompt,
                        max_tokens=2000,
                        temperature=0.7
                    )
                    
                    logger.info(f"✅ 真实API调用成功: {request.model}")
                    
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
            error_msg = str(e)
            
            # 检查是否是配额不足错误
            if "insufficient_quota" in error_msg or "exceeded your current quota" in error_msg:
                logger.error(f"❌ OpenAI API配额不足: {e}")
                # 返回配额不足的明确提示
                return {
                    "model": request.model,
                    "response": "⚠️ **OpenAI API配额不足**\n\n您的OpenAI API密钥配额已用完，请：\n1. 检查您的OpenAI账户余额\n2. 升级您的付费计划\n3. 或等待配额重置\n\n当前使用模拟响应代替真实API调用。",
                    "content": "⚠️ OpenAI API配额不足，请检查账户余额",
                    "response_time": 0.1,
                    "tokens": 50,
                    "tokens_used": 50,
                    "cost": 0.0,
                    "provider": "openai",
                    "is_real_api": False,
                    "error_type": "quota_exceeded"
                }
            else:
                logger.warning(f"真实API调用失败，使用模拟响应: {e}")
            
            # 回退到模拟响应
            model_config = self.model_configs.get(request.model, {})
            response_time = model_config.get("avg_response_time", 2.0)
            
            # 模拟网络延迟
            await asyncio.sleep(min(response_time * 0.3, 1.0))
            
            # 生成模拟响应
            response_content = self._generate_mock_response(request.model, request.prompt)
            
            actual_time = time.time() - start_time
            
            return {
                "model": request.model,
                "response": response_content,
                "content": response_content,
                "response_time": round(actual_time, 2),
                "tokens": int(len(response_content.split()) * 1.3),
                "tokens_used": int(len(response_content.split()) * 1.3),
                "cost": round(model_config.get("cost_per_1k", 0.02) * len(response_content.split()) * 1.3 / 1000, 4),
                "provider": "simulation",
                "is_real_api": False
            }
    
    def _generate_mock_response(self, model: str, prompt: str) -> str:
        """生成模拟的LLM响应"""
        if "javascript" in prompt.lower() or "js" in prompt.lower():
            if "gpt-4o" in model:
                return """// 高质量的JavaScript下划线转驼峰实现

/**
 * 将下划线命名转换为驼峰命名
 * @param {string} str - 包含下划线的字符串
 * @returns {string} 转换后的驼峰命名字符串
 */
function toCamelCase(str) {
    if (!str || typeof str !== 'string') return '';
    
    return str
        .toLowerCase()
        .split('_')
        .map((word, index) => 
            index === 0 ? word : word.charAt(0).toUpperCase() + word.slice(1)
        )
        .join('');
}

// 使用示例
console.log(toCamelCase('hello_world_example')); // helloWorldExample
console.log(toCamelCase('user_name')); // userName
console.log(toCamelCase('api_response_data')); // apiResponseData

// 处理边界情况的增强版本
function toCamelCaseAdvanced(str) {
    if (!str || typeof str !== 'string') return '';
    
    return str
        .trim()
        .toLowerCase()
        .replace(/[_-]+(.)?/g, (_, char) => char ? char.toUpperCase() : '');
}

// 测试用例
const testCases = [
    'hello_world',
    'user_name_field', 
    'api_response_data',
    '_leading_underscore',
    'trailing_underscore_',
    'multiple___underscores'
];

testCases.forEach(test => {
    console.log(`${test} -> ${toCamelCaseAdvanced(test)}`);
});"""
            elif "claude" in model:
                return """// 优雅的下划线转驼峰解决方案

// 简洁的实现方式
const toCamelCase = str => 
    str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());

// 更完整的实现，处理各种边界情况
function convertToCamelCase(input) {
    return input
        .toLowerCase()
        .replace(/[^a-zA-Z0-9]+(.)/g, (_, chr) => chr.toUpperCase());
}

// 使用示例
console.log(toCamelCase('my_variable_name')); // myVariableName
console.log(toCamelCase('hello_world')); // helloWorld
console.log(convertToCamelCase('user-name_field')); // userNameField

// 函数式编程风格
const camelCase = str => str
    .split(/[_-]+/)
    .map((word, i) => i === 0 ? word.toLowerCase() : 
         word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');"""
            else:
                return f"""// {model} 生成的下划线转驼峰实现

function underscoreToCamelCase(inputString) {{
    return inputString
        .split('_')
        .map((word, index) => {{
            if (index === 0) return word.toLowerCase();
            return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
        }})
        .join('');
}}

// 使用示例
const examples = ['hello_world', 'user_name', 'convert_this_string'];
examples.forEach(example => {{
    console.log(`${{example}} -> ${{underscoreToCamelCase(example)}}`);
}});

// 输出:
// hello_world -> helloWorld
// user_name -> userName  
// convert_this_string -> convertThisString"""
        
        # 处理诗歌创作类问题
        elif any(keyword in prompt.lower() for keyword in ["诗", "poem", "poetry", "晴天", "阳光", "天气"]):
            if "gpt-4o" in model:
                return """《晴空万里》

蔚蓝天空无云遮，
金辉洒向大地花。
微风轻抚绿叶舞，
鸟儿欢歌满枝桠。

阳光透过窗棂照，
温暖心房驱阴霾。
此刻时光多美好，
晴天如诗画中来。

清晨露珠映朝阳，
午后光影长又长。
黄昏彩霞染天际，
一日晴好胜春光。"""
            elif "claude" in model:
                return """《阳光诗篇》

天空澄澈如水晶，
白云悠悠自在行。
暖阳轻吻大地面，
万物生辉显精神。

清风徐来花香浓，
蝴蝶翩翩舞其中。
此时此刻心情好，
晴天带来无限情。

光影斑驳树荫下，
孩童嬉戏笑声哗。
美好时光如诗句，
晴朗天气胜画家。"""
            else:
                return f"""《{model}创作 - 晴天颂》

碧空如洗万里晴，
朝阳初升照大地。
微风习习花儿笑，
鸟语花香满园春。

午后阳光暖如酒，
树影婆娑舞翩翩。
此情此景多美妙，
晴天如梦似神仙。

黄昏时分霞满天，
金辉洒向人间路。
一日晴好心欢畅，
诗意盎然在心头。"""
        
        # 处理编程问题
        elif any(keyword in prompt.lower() for keyword in ["python", "算法", "代码", "编程", "函数", "排序"]):
            if "gpt-4o" in model:
                return """# Python快速排序算法实现

def quicksort(arr):
    \"\"\"
    快速排序算法 - 高效的分治排序方法
    时间复杂度: 平均 O(n log n), 最坏 O(n²)
    空间复杂度: O(log n)
    \"\"\"
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# 使用示例
test_array = [64, 34, 25, 12, 22, 11, 90]
print(f"原数组: {test_array}")
sorted_array = quicksort(test_array)
print(f"排序后: {sorted_array}")

# 性能优化版本
def quicksort_inplace(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pi = partition(arr, low, high)
        quicksort_inplace(arr, low, pi - 1)
        quicksort_inplace(arr, pi + 1, high)

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1"""
            else:
                return f"""# {model} - Python快速排序实现

def quick_sort(numbers):
    if len(numbers) < 2:
        return numbers
    
    pivot_index = len(numbers) // 2
    pivot = numbers[pivot_index]
    
    less = [num for num in numbers if num < pivot]
    equal = [num for num in numbers if num == pivot]
    greater = [num for num in numbers if num > pivot]
    
    return quick_sort(less) + equal + quick_sort(greater)

# 测试
data = [3, 6, 8, 10, 1, 2, 1]
result = quick_sort(data)
print(f"排序结果: {result}")"""
        
        # 处理技术解释类问题
        elif any(keyword in prompt.lower() for keyword in ["什么是", "解释", "原理", "技术", "区块链", "ai", "人工智能"]):
            return f"""{model} 专业解答：

{prompt}

这是一个很好的技术问题。让我为您详细解释：

## 核心概念
这个概念涉及多个技术层面，包括底层原理、实现机制和应用场景。

## 技术原理
从技术架构角度来看，主要包含以下几个关键组件：
1. 基础设施层
2. 核心算法层  
3. 应用接口层
4. 用户交互层

## 实际应用
在实际应用中，这项技术被广泛应用于：
- 企业级解决方案
- 消费者产品
- 科研领域
- 教育培训

## 发展趋势
未来发展方向主要集中在性能优化、安全性提升和用户体验改进等方面。

希望这个解释对您有帮助！如有更多问题，欢迎继续交流。"""
        
        # 处理数据分析类问题
        elif any(keyword in prompt.lower() for keyword in ["分析", "数据", "指标", "统计", "报告"]):
            return f"""{model} 数据分析报告：

## 关于 "{prompt}" 的分析

### 1. 数据概览
- 数据来源：多渠道整合
- 时间范围：近期趋势分析
- 样本规模：具有统计意义

### 2. 关键指标
| 指标名称 | 数值 | 趋势 | 重要性 |
|---------|------|------|--------|
| 核心指标1 | 85.2% | ↗️ | 高 |
| 核心指标2 | 1,234 | ↘️ | 中 |
| 核心指标3 | 67.8% | → | 高 |

### 3. 深度洞察
通过数据分析发现以下关键趋势：
- 趋势1：整体表现稳定向好
- 趋势2：某些细分领域需要关注
- 趋势3：用户行为模式发生变化

### 4. 建议措施
基于分析结果，建议采取以下行动：
1. 优化核心流程
2. 加强监控机制
3. 提升用户体验
4. 持续数据跟踪

### 5. 结论
综合分析表明，当前状况总体良好，但仍有优化空间。"""
        
        # 默认通用响应
        else:
            return f"""{model} 智能回答：

感谢您的提问："{prompt}"

这是一个很有意思的问题。基于我的理解，我可以从以下几个角度来回答：

## 主要观点
针对您的问题，我认为关键在于理解其核心本质和实际应用价值。

## 详细分析
1. **背景分析**：这个问题涉及多个层面的考量
2. **核心要点**：主要包含几个关键要素
3. **实践建议**：在实际应用中需要注意的事项
4. **延伸思考**：相关的深入思考方向

## 总结建议
综合考虑各种因素，我建议采取平衡的方法来处理这个问题，既要考虑理论基础，也要结合实际情况。

希望这个回答对您有所帮助！如果您需要更具体的信息，请随时告诉我。"""

# 全局服务实例
p2l_service = P2LBackendService()

# API路由
@app.post("/api/p2l/analyze")
async def analyze_with_p2l(request: P2LAnalysisRequest):
    """P2L智能分析API"""
    try:
        result = await p2l_service.p2l_analyze(request)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"P2L分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/p2l/inference")
async def p2l_inference(request: P2LInferenceRequest):
    """P2L代码推理API - 将代码转换为自然语言"""
    try:
        if not p2l_service.p2l_inference_engine:
            raise HTTPException(status_code=503, detail="P2L推理引擎未加载")
        
        logger.info(f"P2L推理请求: {request.code[:100]}...")
        
        # 使用P2L推理引擎
        result = p2l_service.p2l_inference_engine.infer(
            request.code,
            max_length=request.max_length,
            temperature=request.temperature
        )
        
        return JSONResponse(content={
            "code": request.code,
            "natural_language": result["natural_language"],
            "confidence": result.get("confidence", 0.8),
            "processing_time": result.get("processing_time", 0.0),
            "model_info": "P2L-Inference-Engine"
        })
        
    except Exception as e:
        logger.error(f"P2L推理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/llm/generate")
async def generate_with_llm(request: LLMGenerateRequest):
    """LLM生成API"""
    try:
        result = await p2l_service.generate_llm_response(request)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"LLM生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def get_available_models():
    """获取可用模型列表"""
    return JSONResponse(content={
        "p2l_models": list(p2l_service.p2l_models.keys()),
        "llm_models": list(p2l_service.model_configs.keys()),
        "total_models": len(p2l_service.model_configs)
    })

@app.get("/health")
async def health_check():
    """健康检查"""
    return JSONResponse(content={
        "status": "healthy",
        "p2l_models_loaded": len(p2l_service.p2l_models),
        "p2l_inference_engine": p2l_service.p2l_inference_engine is not None,
        "llm_models_available": len(p2l_service.model_configs),
        "device": str(p2l_service.device),
        "p2l_available": P2L_AVAILABLE,
        "llm_client_available": LLM_CLIENT_AVAILABLE,
        "real_api_enabled": p2l_service.llm_client is not None
    })

# 静态文件服务
# 静态文件服务已移除 - 使用独立的Vue前端

@app.get("/", response_class=HTMLResponse)
async def serve_root():
    """根路径信息页面"""
    return HTMLResponse(
        content="""
        <html>
        <head><title>P2L智能路由后端</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1>🧠 P2L智能路由后端服务</h1>
            <p>后端服务运行正常</p>
            <div style="margin: 20px;">
                <a href="/docs" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📚 API文档</a>
                <a href="/api/health" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-left: 10px;">🔍 健康检查</a>
            </div>
            <p style="color: #666; margin-top: 30px;">
                前端界面请访问: <a href="http://localhost:3000">http://localhost:3000</a>
            </p>
        </body>
        </html>
        """,
        status_code=200
    )

if __name__ == "__main__":
    print("🚀 启动P2L智能路由后端服务...")
    print(f"📊 支持 {len(p2l_service.model_configs)} 个LLM模型")
    print(f"🧠 加载 {len(p2l_service.p2l_models)} 个P2L模型")
    print("🌐 前端访问: http://localhost:8080")
    print("📚 API文档: http://localhost:8080/docs")
    
    uvicorn.run(
        "backend_service:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )