#!/usr/bin/env python3
"""
模型问题诊断工具
检查各个模型在不同中转节点上的可用性，并提供修复建议
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sys
import os

# 添加父目录到路径以导入模型配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_p2l.model_configs import MODEL_CONFIGS

@dataclass
class DiagnosisResult:
    """诊断结果"""
    model: str
    provider: str
    base_url: str
    status_code: int
    success: bool
    response_time: float
    error_message: str = ""
    response_content: str = ""

class ModelDiagnoser:
    """模型诊断器"""
    
    def __init__(self):
        # 中转服务配置
        self.api_endpoints = {
            'yinli.one': {
                'base_url': 'https://yinli.one/v1',
                'api_key': 'sk-u3kUo5WN8Ezb3U3pEx1GWTeazL7xNzghFErxNO4pkJHa4QPl',
                'supports': ['openai', 'anthropic', 'google']
            },
            'probex.top': {
                'base_url': 'https://api.probex.top/v1',
                'api_key': 'sk-LVXnQECvuyLW9kCpDLkGmw5nAi7zzJ6QcgofVi42Vy0CqVo9',
                'supports': ['deepseek', 'openai']
            },
            'dashscope': {
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'api_key': 'sk-66c6ad44142f40f9999546608f7e70e6',
                'supports': ['dashscope']
            }
        }
        
        # 问题模型列表（从测试结果中提取）
        self.problematic_models = [
            'claude-3-5-sonnet-20241022',
            'claude-3-5-sonnet-20240620', 
            'qwen-max-0428',
            'qwen-max-0919'
        ]
        
        # 简单测试消息
        self.test_message = "Hello, please respond with 'OK' to confirm you're working."

    def get_model_endpoints(self, model: str) -> List[Tuple[str, Dict]]:
        """获取模型可能的API端点"""
        model_config = MODEL_CONFIGS.get(model, {})
        provider = model_config.get('provider', '')
        
        endpoints = []
        for service_name, config in self.api_endpoints.items():
            if provider in config['supports'] or provider == '':
                endpoints.append((service_name, config))
        
        return endpoints

    async def test_model_on_endpoint(
        self, 
        session: aiohttp.ClientSession,
        model: str, 
        service_name: str, 
        config: Dict
    ) -> DiagnosisResult:
        """在特定端点测试模型"""
        start_time = time.time()
        
        model_config = MODEL_CONFIGS.get(model, {})
        request_model = model_config.get('request_name', model)
        provider = model_config.get('provider', 'openai')
        
        try:
            # 根据提供商构建不同的请求格式
            if provider == 'anthropic':
                # Anthropic格式
                request_data = {
                    "model": request_model,
                    "max_tokens": 100,
                    "messages": [
                        {
                            "role": "user",
                            "content": self.test_message
                        }
                    ]
                }
                endpoint = '/messages'
            else:
                # OpenAI格式（适用于大多数模型）
                request_data = {
                    "model": request_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": self.test_message
                        }
                    ],
                    "max_tokens": 100,
                    "temperature": 0.1
                }
                endpoint = '/chat/completions'
            
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json"
            }
            
            # 特殊处理Anthropic
            if provider == 'anthropic':
                headers["anthropic-version"] = "2023-06-01"
            
            url = f"{config['base_url']}{endpoint}"
            
            async with session.post(
                url,
                json=request_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                response_text = await response.text()
                
                return DiagnosisResult(
                    model=model,
                    provider=provider,
                    base_url=config['base_url'],
                    status_code=response.status,
                    success=response.status == 200,
                    response_time=response_time,
                    error_message="" if response.status == 200 else f"HTTP {response.status}",
                    response_content=response_text[:500]  # 限制长度
                )
                
        except asyncio.TimeoutError:
            return DiagnosisResult(
                model=model,
                provider=provider,
                base_url=config['base_url'],
                status_code=0,
                success=False,
                response_time=30.0,
                error_message="Timeout"
            )
        except Exception as e:
            end_time = time.time()
            return DiagnosisResult(
                model=model,
                provider=provider,
                base_url=config['base_url'],
                status_code=0,
                success=False,
                response_time=end_time - start_time,
                error_message=str(e)[:200]
            )

    async def diagnose_all_models(self) -> Dict[str, List[DiagnosisResult]]:
        """诊断所有问题模型"""
        results = {}
        
        async with aiohttp.ClientSession() as session:
            for model in self.problematic_models:
                print(f"\n🔍 诊断模型: {model}")
                model_results = []
                
                endpoints = self.get_model_endpoints(model)
                if not endpoints:
                    print(f"   ❌ 未找到支持的端点")
                    continue
                
                # 测试所有可能的端点
                tasks = []
                for service_name, config in endpoints:
                    print(f"   📡 测试端点: {service_name} ({config['base_url']})")
                    task = self.test_model_on_endpoint(session, model, service_name, config)
                    tasks.append(task)
                
                # 并发执行测试
                endpoint_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(endpoint_results):
                    if isinstance(result, Exception):
                        service_name = endpoints[i][0]
                        print(f"      ❌ {service_name}: 异常 - {str(result)[:100]}")
                    else:
                        model_results.append(result)
                        status = "✅ 成功" if result.success else f"❌ 失败 ({result.error_message})"
                        print(f"      {status} - {result.response_time:.2f}s")
                
                results[model] = model_results
        
        return results

    def find_working_alternatives(self, results: Dict[str, List[DiagnosisResult]]) -> Dict[str, str]:
        """为失败的模型找到可工作的替代方案"""
        alternatives = {}
        
        # 已知的工作良好的模型（从测试结果中提取）
        working_models = {
            'claude': ['gpt-4o-2024-08-06', 'gpt-4o-mini-2024-07-18'],  # Claude替代
            'qwen-max': ['qwen1.5-110b-chat', 'qwen2.5-72b-instruct'],  # Qwen-Max替代
        }
        
        for model, diagnosis_results in results.items():
            # 检查是否有任何端点工作
            has_working_endpoint = any(r.success for r in diagnosis_results)
            
            if not has_working_endpoint:
                # 根据模型类型选择替代方案
                if 'claude' in model.lower():
                    alternatives[model] = working_models['claude'][0]  # 使用GPT-4o作为Claude替代
                elif 'qwen-max' in model.lower():
                    alternatives[model] = working_models['qwen-max'][0]  # 使用Qwen1.5-110b作为替代
                else:
                    alternatives[model] = 'gpt-4o-mini-2024-07-18'  # 默认替代
        
        return alternatives

    def generate_fix_script(self, alternatives: Dict[str, str]) -> str:
        """生成修复脚本"""
        if not alternatives:
            return "# 所有模型都工作正常，无需修复"
        
        script_lines = [
            "# 模型映射修复脚本",
            "# 将有问题的模型映射到工作正常的替代模型",
            "",
            "from model_p2l.model_configs import MODEL_CONFIGS",
            "",
            "# 更新模型配置中的request_name字段",
            "model_fixes = {"
        ]
        
        for broken_model, alternative in alternatives.items():
            script_lines.append(f"    '{broken_model}': '{alternative}',")
        
        script_lines.extend([
            "}",
            "",
            "# 应用修复",
            "for broken_model, alternative in model_fixes.items():",
            "    if broken_model in MODEL_CONFIGS:",
            "        MODEL_CONFIGS[broken_model]['request_name'] = alternative",
            "        print(f'✅ 已将 {broken_model} 映射到 {alternative}')",
            "    else:",
            "        print(f'❌ 未找到模型配置: {broken_model}')",
            "",
            "print('🎉 模型修复完成！')"
        ])
        
        return "\n".join(script_lines)

    async def run_diagnosis(self):
        """运行完整诊断"""
        print("🏥 开始模型诊断...")
        print(f"📋 待诊断模型: {', '.join(self.problematic_models)}")
        
        # 执行诊断
        results = await self.diagnose_all_models()
        
        # 生成报告
        print("\n" + "="*80)
        print("📊 诊断报告")
        print("="*80)
        
        working_models = []
        broken_models = []
        
        for model, diagnosis_results in results.items():
            print(f"\n🔍 {model}:")
            
            has_working = False
            for result in diagnosis_results:
                status_icon = "✅" if result.success else "❌"
                service_name = result.base_url.split('//')[1].split('/')[0]
                
                print(f"   {status_icon} {service_name}: ", end="")
                if result.success:
                    print(f"成功 ({result.response_time:.2f}s)")
                    has_working = True
                else:
                    print(f"失败 - {result.error_message}")
                    if result.response_content:
                        # 显示错误详情的前100个字符
                        error_preview = result.response_content[:100].replace('\n', ' ')
                        print(f"      详情: {error_preview}...")
            
            if has_working:
                working_models.append(model)
            else:
                broken_models.append(model)
        
        # 生成修复建议
        print(f"\n📈 诊断总结:")
        print(f"   ✅ 可修复模型: {len(working_models)} 个")
        print(f"   ❌ 需要替换模型: {len(broken_models)} 个")
        
        if broken_models:
            print(f"\n🔧 需要替换的模型: {', '.join(broken_models)}")
            alternatives = self.find_working_alternatives(results)
            
            print(f"\n💡 建议的替代方案:")
            for broken, alternative in alternatives.items():
                print(f"   {broken} → {alternative}")
            
            # 生成修复脚本
            fix_script = self.generate_fix_script(alternatives)
            
            # 保存修复脚本
            script_filename = f"fix_model_mappings_{int(time.time())}.py"
            with open(script_filename, 'w', encoding='utf-8') as f:
                f.write(fix_script)
            
            print(f"\n💾 修复脚本已保存到: {script_filename}")
            print("   运行该脚本来应用修复:")
            print(f"   python {script_filename}")
        
        # 保存详细诊断结果
        diagnosis_data = {
            'timestamp': time.time(),
            'problematic_models': self.problematic_models,
            'results': {
                model: [
                    {
                        'model': r.model,
                        'provider': r.provider,
                        'base_url': r.base_url,
                        'status_code': r.status_code,
                        'success': r.success,
                        'response_time': r.response_time,
                        'error_message': r.error_message,
                        'response_content': r.response_content
                    }
                    for r in diagnosis_results
                ]
                for model, diagnosis_results in results.items()
            }
        }
        
        diagnosis_filename = f"model_diagnosis_{int(time.time())}.json"
        with open(diagnosis_filename, 'w', encoding='utf-8') as f:
            json.dump(diagnosis_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 详细诊断结果已保存到: {diagnosis_filename}")

async def main():
    """主函数"""
    diagnoser = ModelDiagnoser()
    await diagnoser.run_diagnosis()

if __name__ == "__main__":
    asyncio.run(main())