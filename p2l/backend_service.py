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
    priority: str = "performance"  # performance, cost, speed, balanced

class LLMGenerateRequest(BaseModel):
    model: str
    prompt: str
    analysis: Optional[Dict] = None

class P2LBackendService:
    def __init__(self):
        self.p2l_models = {}
        self.model_configs = self._load_model_configs()
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        logger.info(f"使用设备: {self.device}")
        
        # 尝试加载P2L模型
        self._load_p2l_models()
    
    def _load_model_configs(self) -> Dict:
        """加载模型配置信息"""
        return {
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
            "claude-3-5-sonnet-20241022": {
                "provider": "anthropic",
                "cost_per_1k": 0.025,
                "avg_response_time": 2.8,
                "strengths": ["创意写作", "文学分析"],
                "quality_score": 0.93
            },
            "claude-3-5-haiku-20241022": {
                "provider": "anthropic",
                "cost_per_1k": 0.008,
                "avg_response_time": 1.5,
                "strengths": ["快速响应", "简洁回答"],
                "quality_score": 0.85
            },
            "gemini-1.5-pro-002": {
                "provider": "google",
                "cost_per_1k": 0.02,
                "avg_response_time": 2.2,
                "strengths": ["多模态", "长文本"],
                "quality_score": 0.90
            },
            "gemini-1.5-flash-002": {
                "provider": "google",
                "cost_per_1k": 0.005,
                "avg_response_time": 1.0,
                "strengths": ["快速处理"],
                "quality_score": 0.80
            },
            "qwen2.5-72b-instruct": {
                "provider": "alibaba",
                "cost_per_1k": 0.015,
                "avg_response_time": 2.0,
                "strengths": ["中文理解", "中文创作"],
                "quality_score": 0.88
            },
            "llama-3.1-70b-instruct": {
                "provider": "meta",
                "cost_per_1k": 0.01,
                "avg_response_time": 2.3,
                "strengths": ["开源", "可控"],
                "quality_score": 0.86
            },
            "deepseek-v3": {
                "provider": "deepseek",
                "cost_per_1k": 0.012,
                "avg_response_time": 1.8,
                "strengths": ["数学", "逻辑推理"],
                "quality_score": 0.87
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
    
    def analyze_task(self, prompt: str) -> Dict:
        """使用P2L神经网络模型分析任务特征"""
        # 如果有P2L模型，使用神经网络推理
        if self.p2l_models:
            try:
                model_name = list(self.p2l_models.keys())[0]
                p2l_model = self.p2l_models[model_name]
                tokenizer = p2l_model["tokenizer"]
                model = p2l_model["model"]
                
                # 使用P2L模型进行推理
                inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=512)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = model(**inputs)
                    logits = outputs.logits
                    logger.info(f"🔍 P2L模型输出调试: logits.shape={logits.shape}, logits={logits}")
                    
                # 解释P2L模型输出 (2个输出：复杂度和语言类型)
                probs = torch.softmax(logits, dim=-1)
                logger.info(f"🔍 概率分布调试: probs.shape={probs.shape}, probs={probs}")
                
                # 取第一个样本的概率分布 - shape: [2]
                sample_probs = probs[0]
                logger.info(f"🔍 样本概率调试: sample_probs.shape={sample_probs.shape}, sample_probs={sample_probs}")
                
                # 使用第一个输出作为复杂度分数，第二个作为语言分数
                complexity_score = sample_probs[0].item()
                language_score = sample_probs[1].item() if sample_probs.size(0) > 1 else 0.5
                
                # 基于神经网络输出确定任务特征
                task_analysis = self._interpret_p2l_output(prompt, complexity_score, language_score)
                logger.info(f"🧠 P2L神经网络推理: 复杂度={complexity_score:.3f}, 语言={language_score:.3f}")
                
                return task_analysis
                
            except Exception as e:
                logger.warning(f"P2L模型推理失败，使用规则方法: {e}")
        
        # 备用规则方法
        return self._rule_based_analysis(prompt)
    
    def _interpret_p2l_output(self, prompt: str, complexity_score: float, language_score: float) -> Dict:
        """解释P2L模型输出"""
        prompt_lower = prompt.lower()
        
        # 基于神经网络输出和提示词内容确定任务类型
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
        
        # 基于神经网络输出确定复杂度
        if complexity_score > 0.7:
            complexity = "复杂"
        elif complexity_score < 0.3:
            complexity = "简单"
        else:
            complexity = "中等"
        
        # 基于神经网络输出确定语言
        language = "中文" if language_score > 0.5 else "英文"
        
        return {
            "task_type": task_type,
            "complexity": complexity,
            "language": language,
            "length": len(prompt),
            "p2l_scores": {
                "complexity": complexity_score,
                "language": language_score
            }
        }
    
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
    
    def calculate_model_scores(self, task_analysis: Dict, priority: str) -> List[Dict]:
        """计算模型分数并排序"""
        scores = []
        
        for model_name, config in self.model_configs.items():
            base_score = config["quality_score"]
            
            # 任务类型匹配
            task_bonus = 0
            if task_analysis["task_type"] in config["strengths"]:
                task_bonus = 0.15
            
            # 语言匹配
            language_bonus = 0
            if task_analysis["language"] == "中文" and "中文" in config["strengths"]:
                language_bonus = 0.20
            
            # 复杂度匹配
            complexity_bonus = 0
            if task_analysis["complexity"] == "复杂" and config["quality_score"] > 0.90:
                complexity_bonus = 0.10
            elif task_analysis["complexity"] == "简单" and config["avg_response_time"] < 2.0:
                complexity_bonus = 0.05
            
            # 优先级调整
            priority_bonus = 0
            if priority == "cost" and config["cost_per_1k"] < 0.01:
                priority_bonus = 0.20
            elif priority == "speed" and config["avg_response_time"] < 2.0:
                priority_bonus = 0.15
            elif priority == "performance" and config["quality_score"] > 0.90:
                priority_bonus = 0.10
            
            final_score = base_score + task_bonus + language_bonus + complexity_bonus + priority_bonus
            
            scores.append({
                "model": model_name,
                "score": round(final_score, 4),
                "config": config
            })
        
        # 按分数排序
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores
    
    async def p2l_analyze(self, request: P2LAnalysisRequest) -> Dict:
        """P2L智能分析"""
        logger.info(f"P2L分析请求: {request.prompt[:50]}...")
        
        # 分析任务
        task_analysis = self.analyze_task(request.prompt)
        
        # 计算模型分数
        model_scores = self.calculate_model_scores(task_analysis, request.priority)
        
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
                for item in model_scores[:5]
            ],
            "model_rankings": [
                {"model": item["model"], "score": item["score"]} 
                for item in model_scores[:5]
            ],
            "priority_mode": request.priority
        }
        
        logger.info(f"P2L推荐: {result['recommended_model']}")
        return result
    
    async def generate_llm_response(self, request: LLMGenerateRequest) -> Dict:
        """模拟LLM响应生成"""
        logger.info(f"调用LLM: {request.model}")
        
        start_time = time.time()
        
        # 模拟不同模型的响应时间
        model_config = self.model_configs.get(request.model, {})
        response_time = model_config.get("avg_response_time", 2.0)
        
        # 模拟网络延迟
        await asyncio.sleep(min(response_time * 0.3, 2.0))
        
        # 生成模拟响应
        response_content = self._generate_mock_response(request.model, request.prompt)
        
        actual_time = time.time() - start_time
        
        return {
            "model": request.model,
            "content": response_content,
            "response_time": round(actual_time, 2),
            "tokens_used": len(response_content.split()) * 1.3,  # 估算token数
            "cost": round(model_config.get("cost_per_1k", 0.02) * len(response_content.split()) * 1.3 / 1000, 4)
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
        
        # 其他类型的响应
        return f"这是 {model} 对您问题的回答：\n\n{prompt}\n\n[模拟响应内容]"

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
        "llm_models_available": len(p2l_service.model_configs),
        "device": str(p2l_service.device)
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