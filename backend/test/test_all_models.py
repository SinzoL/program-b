#!/usr/bin/env python3
"""
测试model_configs.py中的所有模型
验证每个模型的API配置是否正确
"""

import requests
import json
import time
import threading
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加backend目录到Python路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# 导入model_p2l配置
sys.path.insert(0, os.path.join(backend_dir, 'model_p2l'))
from api_configs import API_CONFIGS
from model_configs import MODEL_CONFIGS, get_request_name, get_model_provider_info

def test_single_model(model_name, timeout=30):
    """测试单个模型"""
    try:
        # 获取模型配置
        model_info = get_model_provider_info(model_name)
        provider = model_info["provider"]
        request_name = model_info["request_name"]
        
        # 获取API配置
        api_key = API_CONFIGS["api_keys"].get(provider)
        base_url = API_CONFIGS["base_urls"].get(provider)
        
        if not api_key or not base_url:
            return {
                "model": model_name,
                "status": "config_error",
                "error": f"API密钥或Base URL未配置 (provider: {provider})",
                "provider": provider,
                "request_name": request_name
            }
        
        # 构建请求
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": request_name,
            "messages": [{"role": "user", "content": "Hello, test"}],
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        # 发送请求
        start_time = time.time()
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout
        )
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            response_data = response.json()
            content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                "model": model_name,
                "status": "success",
                "response_time": response_time,
                "content": content[:100],  # 限制内容长度
                "provider": provider,
                "request_name": request_name
            }
        else:
            return {
                "model": model_name,
                "status": "api_error",
                "status_code": response.status_code,
                "error": response.text[:300],  # 限制错误信息长度
                "provider": provider,
                "request_name": request_name,
                "response_time": response_time
            }
            
    except Exception as e:
        return {
            "model": model_name,
            "status": "connection_error",
            "error": str(e)[:200],
            "provider": provider if 'provider' in locals() else "unknown",
            "request_name": request_name if 'request_name' in locals() else model_name
        }

def test_all_models():
    """测试所有模型"""
    print("🚀 开始测试所有模型...")
    print(f"📋 总共需要测试 {len(MODEL_CONFIGS)} 个模型")
    
    # 按提供商分组显示
    providers = {}
    for model_name, config in MODEL_CONFIGS.items():
        provider = config.get("provider", "unknown")
        if provider not in providers:
            providers[provider] = []
        providers[provider].append(model_name)
    
    print(f"\n📊 按提供商分组:")
    for provider, models in providers.items():
        api_key = API_CONFIGS["api_keys"].get(provider, "未配置")
        base_url = API_CONFIGS["base_urls"].get(provider, "未配置")
        print(f"  {provider} ({len(models)}个): {base_url}")
    
    print(f"\n🧪 开始并发测试...")
    
    results = {}
    start_time = time.time()
    
    # 使用线程池并发测试，但限制并发数避免过载
    with ThreadPoolExecutor(max_workers=8) as executor:
        # 提交所有任务
        future_to_model = {
            executor.submit(test_single_model, model_name): model_name 
            for model_name in MODEL_CONFIGS.keys()
        }
        
        # 收集结果
        completed = 0
        for future in as_completed(future_to_model):
            model_name = future_to_model[future]
            try:
                result = future.result()
                results[model_name] = result
                completed += 1
                
                # 显示进度
                status_icon = "✅" if result["status"] == "success" else "❌"
                print(f"  {status_icon} [{completed:2d}/{len(MODEL_CONFIGS)}] {model_name} ({result['provider']}) - {result['status']}")
                
            except Exception as e:
                results[model_name] = {
                    "model": model_name,
                    "status": "test_error",
                    "error": str(e)
                }
                completed += 1
                print(f"  ❌ [{completed:2d}/{len(MODEL_CONFIGS)}] {model_name} - 测试异常: {str(e)[:50]}")
    
    total_time = time.time() - start_time
    
    # 统计结果
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    config_error_count = sum(1 for r in results.values() if r["status"] == "config_error")
    api_error_count = sum(1 for r in results.values() if r["status"] == "api_error")
    connection_error_count = sum(1 for r in results.values() if r["status"] == "connection_error")
    
    print(f"\n📊 测试结果汇总 (耗时: {total_time:.1f}s):")
    print(f"  ✅ 成功: {success_count}/{len(MODEL_CONFIGS)} ({success_count/len(MODEL_CONFIGS)*100:.1f}%)")
    print(f"  ⚙️  配置错误: {config_error_count}")
    print(f"  🌐 API错误: {api_error_count}")
    print(f"  🔌 连接错误: {connection_error_count}")
    
    # 按提供商统计
    print(f"\n📋 按提供商统计:")
    provider_stats = {}
    
    for result in results.values():
        provider = result.get("provider", "unknown")
        if provider not in provider_stats:
            provider_stats[provider] = {"success": 0, "total": 0, "models": []}
        
        provider_stats[provider]["total"] += 1
        provider_stats[provider]["models"].append(result)
        if result["status"] == "success":
            provider_stats[provider]["success"] += 1
    
    for provider, stats in provider_stats.items():
        success_rate = stats["success"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"\n  {provider}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        # 显示失败的模型
        failed_models = [m for m in stats["models"] if m["status"] != "success"]
        if failed_models:
            print(f"    失败模型:")
            for model in failed_models:
                error_msg = model.get("error", "未知错误")[:80]
                print(f"      ❌ {model['model']}: {model['status']} - {error_msg}")
        
        # 显示成功的模型（仅显示前3个）
        success_models = [m for m in stats["models"] if m["status"] == "success"]
        if success_models:
            print(f"    成功模型 (显示前3个):")
            for model in success_models[:3]:
                response_time = model.get("response_time", 0)
                print(f"      ✅ {model['model']}: {response_time:.2f}s")
            if len(success_models) > 3:
                print(f"      ... 还有 {len(success_models) - 3} 个成功")
    
    # 保存详细结果
    detailed_results = {
        "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_time": total_time,
        "summary": {
            "total_models": len(MODEL_CONFIGS),
            "success_count": success_count,
            "config_error_count": config_error_count,
            "api_error_count": api_error_count,
            "connection_error_count": connection_error_count,
            "success_rate": success_count/len(MODEL_CONFIGS)*100
        },
        "provider_stats": {
            provider: {
                "success": stats["success"],
                "total": stats["total"],
                "success_rate": stats["success"] / stats["total"] * 100 if stats["total"] > 0 else 0
            }
            for provider, stats in provider_stats.items()
        },
        "detailed_results": results
    }
    
    # with open("all_models_test_results.json", "w", encoding="utf-8") as f:
    #    json.dump(detailed_results, f, indent=2, ensure_ascii=False)
    
    # print(f"\n💾 详细结果已保存到 all_models_test_results.json")
    
    return results

if __name__ == "__main__":
    results = test_all_models()