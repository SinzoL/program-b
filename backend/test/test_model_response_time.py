#!/usr/bin/env python3
"""
模型响应时间测试工具
测试多个模型对不同领域、不同难度问题的响应时间
进行三轮测试，计算平均响应时间，支持并发测试
"""

import asyncio
import aiohttp
import time
import json
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# 添加父目录到路径以导入模型配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_p2l.model_configs import MODEL_CONFIGS

@dataclass
class TestQuestion:
    """测试问题数据结构"""
    id: int
    category: str
    difficulty: str
    question: str
    description: str

@dataclass
class TestResult:
    """测试结果数据结构"""
    model: str
    question_id: int
    round_num: int
    response_time: float
    success: bool
    error_message: str = ""
    tokens: int = 0

class ModelResponseTimeTest:
    """模型响应时间测试类"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.test_questions = self._create_test_questions()
        self.results: List[TestResult] = []
        
    def _create_test_questions(self) -> List[TestQuestion]:
        """创建10个不同领域、不同难度的测试问题"""
        questions = [
            TestQuestion(
                id=1,
                category="编程基础",
                difficulty="简单",
                question="什么是Python中的列表推导式？请给出一个简单例子。",
                description="基础编程概念，预期回答简短"
            ),
            TestQuestion(
                id=2,
                category="数学计算",
                difficulty="中等",
                question="请解释什么是斐波那契数列，并用递归和迭代两种方法实现。",
                description="数学概念加算法实现，中等长度回答"
            ),
            TestQuestion(
                id=3,
                category="商业分析",
                difficulty="复杂",
                question="分析电商平台如何通过数据驱动的方式提高用户留存率，包括具体的策略、指标和实施步骤。",
                description="复杂商业问题，需要详细分析"
            ),
            TestQuestion(
                id=4,
                category="技术架构",
                difficulty="复杂",
                question="设计一个高并发的微服务架构，支持日活千万用户，包括技术选型、数据库设计、缓存策略等。",
                description="复杂技术设计问题"
            ),
            TestQuestion(
                id=5,
                category="文学创作",
                difficulty="中等",
                question="写一首关于秋天的现代诗，要求有意境和韵律感。",
                description="创意写作任务"
            ),
            TestQuestion(
                id=6,
                category="科学知识",
                difficulty="简单",
                question="请简单解释什么是光合作用？",
                description="基础科学概念"
            ),
            TestQuestion(
                id=7,
                category="历史分析",
                difficulty="中等",
                question="分析工业革命对现代社会发展的影响，从经济、社会、技术三个维度展开。",
                description="历史分析问题，需要多维度思考"
            ),
            TestQuestion(
                id=8,
                category="逻辑推理",
                difficulty="中等",
                question="有5个人坐成一排，A不坐在两端，B必须坐在C的左边，D和E不能相邻。请列出所有可能的排列。",
                description="逻辑推理问题"
            ),
            TestQuestion(
                id=9,
                category="实用建议",
                difficulty="简单",
                question="给出5个提高工作效率的实用建议。",
                description="实用性问题，简单直接"
            ),
            TestQuestion(
                id=10,
                category="深度思考",
                difficulty="复杂",
                question="从哲学角度分析人工智能的发展对人类社会的深层影响，包括伦理、就业、认知等方面的思考。",
                description="深度哲学思考问题"
            )
        ]
        return questions
    
    def get_model_api_config(self, model: str) -> Dict[str, str]:
        """获取模型的API配置"""
        model_config = MODEL_CONFIGS.get(model, {})
        provider = model_config.get('provider', '')
        
        # 根据提供商选择API配置
        if provider == 'openai':
            return {
                'base_url': 'https://yinli.one/v1',
                'api_key': 'sk-u3kUo5WN8Ezb3U3pEx1GWTeazL7xNzghFErxNO4pkJHa4QPl',
                'endpoint': '/chat/completions',
                'format': 'openai'
            }
        elif provider == 'anthropic':
            return {
                'base_url': 'https://yinli.one/v1',
                'api_key': 'sk-u3kUo5WN8Ezb3U3pEx1GWTeazL7xNzghFErxNO4pkJHa4QPl',
                'endpoint': '/messages',
                'format': 'anthropic'
            }
        elif provider == 'google':
            return {
                'base_url': 'https://yinli.one/v1',
                'api_key': 'sk-u3kUo5WN8Ezb3U3pEx1GWTeazL7xNzghFErxNO4pkJHa4QPl',
                'endpoint': '/chat/completions',
                'format': 'openai'
            }
        elif provider == 'deepseek':
            return {
                'base_url': 'https://api.probex.top/v1',
                'api_key': 'sk-LVXnQECvuyLW9kCpDLkGmw5nAi7zzJ6QcgofVi42Vy0CqVo9',
                'endpoint': '/chat/completions',
                'format': 'openai'
            }
        elif provider == 'dashscope':
            return {
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'api_key': 'sk-66c6ad44142f40f9999546608f7e70e6',
                'endpoint': '/chat/completions',
                'format': 'openai'
            }
        else:
            # 默认使用yinli.one
            return {
                'base_url': 'https://yinli.one/v1',
                'api_key': 'sk-u3kUo5WN8Ezb3U3pEx1GWTeazL7xNzghFErxNO4pkJHa4QPl',
                'endpoint': '/chat/completions',
                'format': 'openai'
            }

    async def test_single_model_question(
        self, 
        session: aiohttp.ClientSession, 
        model: str, 
        question: TestQuestion, 
        round_num: int
    ) -> TestResult:
        """测试单个模型对单个问题的响应"""
        start_time = time.time()
        
        try:
            # 获取模型API配置
            api_config = self.get_model_api_config(model)
            model_config = MODEL_CONFIGS.get(model, {})
            request_model = model_config.get('request_name', model)
            
            # 根据API格式构建请求数据
            if api_config.get('format') == 'anthropic':
                # Anthropic格式
                request_data = {
                    "model": request_model,
                    "max_tokens": 2000,
                    "messages": [
                        {
                            "role": "user",
                            "content": question.question
                        }
                    ]
                }
                headers = {
                    "Authorization": f"Bearer {api_config['api_key']}",
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
            else:
                # OpenAI格式（默认）
                request_data = {
                    "model": request_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": question.question
                        }
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
                headers = {
                    "Authorization": f"Bearer {api_config['api_key']}",
                    "Content-Type": "application/json"
                }
            
            # 发送请求
            url = f"{api_config['base_url']}{api_config['endpoint']}"
            async with session.post(
                url,
                json=request_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=120)  # 2分钟超时
            ) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status == 200:
                    result_data = await response.json()
                    
                    # 解析响应
                    content = ""
                    tokens = 0
                    
                    if 'choices' in result_data and len(result_data['choices']) > 0:
                        choice = result_data['choices'][0]
                        if 'message' in choice:
                            content = choice['message'].get('content', '')
                        elif 'text' in choice:
                            content = choice['text']
                    
                    if 'usage' in result_data:
                        tokens = result_data['usage'].get('total_tokens', 0)
                    
                    return TestResult(
                        model=model,
                        question_id=question.id,
                        round_num=round_num,
                        response_time=response_time,
                        success=True,
                        tokens=tokens
                    )
                else:
                    error_text = await response.text()
                    return TestResult(
                        model=model,
                        question_id=question.id,
                        round_num=round_num,
                        response_time=response_time,
                        success=False,
                        error_message=f"HTTP {response.status}: {error_text[:200]}"
                    )
                    
        except asyncio.TimeoutError:
            return TestResult(
                model=model,
                question_id=question.id,
                round_num=round_num,
                response_time=120.0,  # 超时时间
                success=False,
                error_message="请求超时"
            )
        except Exception as e:
            end_time = time.time()
            return TestResult(
                model=model,
                question_id=question.id,
                round_num=round_num,
                response_time=end_time - start_time,
                success=False,
                error_message=str(e)[:200]
            )
    
    async def test_round(self, models: List[str], round_num: int) -> List[TestResult]:
        """执行一轮测试（所有模型对所有问题）"""
        print(f"\n🔄 开始第 {round_num} 轮测试...")
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # 为每个模型和每个问题创建任务
            for model in models:
                for question in self.test_questions:
                    task = self.test_single_model_question(session, model, question, round_num)
                    tasks.append(task)
            
            # 并发执行所有任务
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤异常结果
            valid_results = []
            for result in results:
                if isinstance(result, TestResult):
                    valid_results.append(result)
                else:
                    print(f"❌ 任务执行异常: {result}")
            
            print(f"✅ 第 {round_num} 轮测试完成，共 {len(valid_results)} 个结果")
            return valid_results
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        models = []
        # 直接使用所有配置的模型，因为API密钥在环境变量中配置
        for model_name, config in MODEL_CONFIGS.items():
            # 只测试已验证的模型
            if config.get('verified', False):
                models.append(model_name)
        return models
    
    def analyze_results(self) -> Dict[str, Any]:
        """分析测试结果"""
        analysis = {
            'summary': {},
            'model_performance': {},
            'question_difficulty': {},
            'detailed_results': []
        }
        
        # 按模型分组分析
        model_results = {}
        for result in self.results:
            if result.model not in model_results:
                model_results[result.model] = []
            model_results[result.model].append(result)
        
        # 计算每个模型的统计数据
        for model, results in model_results.items():
            successful_results = [r for r in results if r.success]
            failed_results = [r for r in results if not r.success]
            
            if successful_results:
                response_times = [r.response_time for r in successful_results]
                tokens = [r.tokens for r in successful_results if r.tokens > 0]
                
                model_stats = {
                    'total_tests': len(results),
                    'successful_tests': len(successful_results),
                    'failed_tests': len(failed_results),
                    'success_rate': len(successful_results) / len(results) * 100,
                    'avg_response_time': statistics.mean(response_times),
                    'median_response_time': statistics.median(response_times),
                    'min_response_time': min(response_times),
                    'max_response_time': max(response_times),
                    'std_response_time': statistics.stdev(response_times) if len(response_times) > 1 else 0,
                    'avg_tokens': statistics.mean(tokens) if tokens else 0,
                    'total_tokens': sum(tokens) if tokens else 0
                }
            else:
                model_stats = {
                    'total_tests': len(results),
                    'successful_tests': 0,
                    'failed_tests': len(failed_results),
                    'success_rate': 0,
                    'avg_response_time': 0,
                    'median_response_time': 0,
                    'min_response_time': 0,
                    'max_response_time': 0,
                    'std_response_time': 0,
                    'avg_tokens': 0,
                    'total_tokens': 0
                }
            
            analysis['model_performance'][model] = model_stats
        
        # 按问题难度分析
        difficulty_results = {'简单': [], '中等': [], '复杂': []}
        for result in self.results:
            if result.success:
                question = next(q for q in self.test_questions if q.id == result.question_id)
                difficulty_results[question.difficulty].append(result.response_time)
        
        for difficulty, times in difficulty_results.items():
            if times:
                analysis['question_difficulty'][difficulty] = {
                    'count': len(times),
                    'avg_time': statistics.mean(times),
                    'median_time': statistics.median(times),
                    'min_time': min(times),
                    'max_time': max(times)
                }
        
        # 总体统计
        all_successful = [r for r in self.results if r.success]
        if all_successful:
            all_times = [r.response_time for r in all_successful]
            analysis['summary'] = {
                'total_tests': len(self.results),
                'successful_tests': len(all_successful),
                'overall_success_rate': len(all_successful) / len(self.results) * 100,
                'overall_avg_time': statistics.mean(all_times),
                'overall_median_time': statistics.median(all_times),
                'fastest_response': min(all_times),
                'slowest_response': max(all_times)
            }
        
        return analysis
    
    def print_results(self, analysis: Dict[str, Any]):
        """打印测试结果"""
        print("\n" + "="*80)
        print("🎯 模型响应时间测试报告")
        print("="*80)
        
        # 总体统计
        summary = analysis['summary']
        if summary:
            print(f"\n📊 总体统计:")
            print(f"   总测试数: {summary['total_tests']}")
            print(f"   成功测试: {summary['successful_tests']}")
            print(f"   成功率: {summary['overall_success_rate']:.1f}%")
            print(f"   平均响应时间: {summary['overall_avg_time']:.2f}秒")
            print(f"   中位数响应时间: {summary['overall_median_time']:.2f}秒")
            print(f"   最快响应: {summary['fastest_response']:.2f}秒")
            print(f"   最慢响应: {summary['slowest_response']:.2f}秒")
        
        # 模型性能排行
        print(f"\n🏆 模型性能排行 (按平均响应时间排序):")
        model_perf = analysis['model_performance']
        sorted_models = sorted(
            model_perf.items(), 
            key=lambda x: x[1]['avg_response_time'] if x[1]['successful_tests'] > 0 else float('inf')
        )
        
        print(f"{'排名':<4} {'模型名称':<25} {'成功率':<8} {'平均时间':<10} {'中位数':<10} {'标准差':<10} {'平均Token':<12}")
        print("-" * 85)
        
        for i, (model, stats) in enumerate(sorted_models, 1):
            if stats['successful_tests'] > 0:
                print(f"{i:<4} {model:<25} {stats['success_rate']:.1f}%{'':<3} "
                      f"{stats['avg_response_time']:.2f}s{'':<4} "
                      f"{stats['median_response_time']:.2f}s{'':<4} "
                      f"{stats['std_response_time']:.2f}s{'':<4} "
                      f"{stats['avg_tokens']:.0f}")
            else:
                print(f"{i:<4} {model:<25} {'失败':<8} {'--':<10} {'--':<10} {'--':<10} {'--':<12}")
        
        # 问题难度分析
        print(f"\n📈 问题难度分析:")
        difficulty_analysis = analysis['question_difficulty']
        for difficulty, stats in difficulty_analysis.items():
            print(f"   {difficulty}问题: 平均 {stats['avg_time']:.2f}秒 "
                  f"(范围: {stats['min_time']:.2f}s - {stats['max_time']:.2f}s)")
        
        # 详细的失败分析
        failed_results = [r for r in self.results if not r.success]
        if failed_results:
            print(f"\n❌ 失败测试分析:")
            failure_by_model = {}
            for result in failed_results:
                if result.model not in failure_by_model:
                    failure_by_model[result.model] = []
                failure_by_model[result.model].append(result)
            
            for model, failures in failure_by_model.items():
                print(f"   {model}: {len(failures)} 次失败")
                error_types = {}
                for failure in failures:
                    error_type = failure.error_message.split(':')[0] if failure.error_message else "未知错误"
                    error_types[error_type] = error_types.get(error_type, 0) + 1
                for error_type, count in error_types.items():
                    print(f"     - {error_type}: {count} 次")
    
    async def run_test(self, rounds: int = 3):
        """运行完整测试"""
        print("🚀 开始模型响应时间测试")
        print(f"📋 测试配置:")
        print(f"   - 测试轮数: {rounds}")
        print(f"   - 测试问题: {len(self.test_questions)} 个")
        print(f"   - 服务地址: {self.base_url}")
        
        # 获取可用模型
        available_models = self.get_available_models()
        print(f"   - 可用模型: {len(available_models)} 个")
        for model in available_models:
            print(f"     • {model}")
        
        if not available_models:
            print("❌ 没有找到可用的模型（需要有API密钥）")
            return
        
        # 显示测试问题
        print(f"\n📝 测试问题列表:")
        for q in self.test_questions:
            print(f"   {q.id}. [{q.category}] [{q.difficulty}] {q.question[:50]}...")
        
        # 执行测试轮次
        start_time = time.time()
        
        for round_num in range(1, rounds + 1):
            round_results = await self.test_round(available_models, round_num)
            self.results.extend(round_results)
            
            # 显示当前轮次的简要统计
            successful = len([r for r in round_results if r.success])
            total = len(round_results)
            print(f"   第 {round_num} 轮: {successful}/{total} 成功")
        
        total_time = time.time() - start_time
        print(f"\n⏱️  总测试时间: {total_time:.2f} 秒")
        
        # 分析和显示结果
        analysis = self.analyze_results()
        self.print_results(analysis)
        
        # 保存详细结果到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"model_response_time_test_{timestamp}.json"
        
        detailed_results = {
            'test_config': {
                'rounds': rounds,
                'questions_count': len(self.test_questions),
                'models_count': len(available_models),
                'total_time': total_time,
                'timestamp': timestamp
            },
            'questions': [
                {
                    'id': q.id,
                    'category': q.category,
                    'difficulty': q.difficulty,
                    'question': q.question,
                    'description': q.description
                } for q in self.test_questions
            ],
            'raw_results': [
                {
                    'model': r.model,
                    'question_id': r.question_id,
                    'round_num': r.round_num,
                    'response_time': r.response_time,
                    'success': r.success,
                    'error_message': r.error_message,
                    'tokens': r.tokens
                } for r in self.results
            ],
            'analysis': analysis
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细结果已保存到: {filename}")

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="模型响应时间测试工具")
    parser.add_argument("--rounds", type=int, default=3, help="测试轮数 (默认: 3)")
    parser.add_argument("--url", type=str, default="http://localhost:8080", help="API服务地址")
    
    args = parser.parse_args()
    
    # 创建测试实例并运行
    tester = ModelResponseTimeTest(base_url=args.url)
    await tester.run_test(rounds=args.rounds)

if __name__ == "__main__":
    asyncio.run(main())