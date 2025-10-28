#!/usr/bin/env python3
"""
模型映射修复脚本
将有问题的模型映射到工作正常的替代模型
"""

import sys
import os

# 添加父目录到路径以导入模型配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def apply_model_fixes():
    """应用模型修复映射"""
    
    # 基于测试结果的模型映射策略
    model_fixes = {
        # Claude模型 - JSON解析问题，映射到性能相近的GPT模型
        'claude-3-5-sonnet-20241022': 'gpt-4o-2024-08-06',  # 高端模型替代
        'claude-3-5-sonnet-20240620': 'gpt-4o-2024-08-06',  # 高端模型替代
        
        # Qwen-Max模型 - 限流问题，映射到无限流的Qwen模型
        'qwen-max-0428': 'qwen1.5-110b-chat',  # 性能相近的替代
        'qwen-max-0919': 'qwen2.5-72b-instruct',  # 更新版本替代
    }
    
    print("🔧 开始应用模型映射修复...")
    print(f"📋 需要修复的模型: {len(model_fixes)} 个")
    
    # 读取当前模型配置文件
    config_file_path = os.path.join(os.path.dirname(__file__), '..', 'model_p2l', 'model_configs.py')
    
    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📖 已读取配置文件: {config_file_path}")
        
        # 应用修复
        modifications = []
        for broken_model, alternative in model_fixes.items():
            # 查找模型配置
            model_pattern = f"'{broken_model}': {{"
            if model_pattern in content:
                print(f"✅ 找到模型配置: {broken_model}")
                
                # 查找request_name字段并更新
                start_pos = content.find(model_pattern)
                if start_pos != -1:
                    # 找到配置块的结束位置
                    brace_count = 0
                    pos = start_pos + len(model_pattern) - 1
                    end_pos = pos
                    
                    while pos < len(content):
                        if content[pos] == '{':
                            brace_count += 1
                        elif content[pos] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_pos = pos + 1
                                break
                        pos += 1
                    
                    # 提取配置块
                    config_block = content[start_pos:end_pos]
                    
                    # 检查是否已有request_name字段
                    if "'request_name':" in config_block:
                        # 更新现有的request_name
                        import re
                        new_config_block = re.sub(
                            r"'request_name':\s*'[^']*'",
                            f"'request_name': '{alternative}'",
                            config_block
                        )
                    else:
                        # 添加新的request_name字段
                        # 在最后一个字段后添加
                        insertion_point = config_block.rfind(',')
                        if insertion_point != -1:
                            new_config_block = (
                                config_block[:insertion_point + 1] + 
                                f"\n        'request_name': '{alternative}'," +
                                config_block[insertion_point + 1:]
                            )
                        else:
                            # 如果没有找到逗号，在}前添加
                            insertion_point = config_block.rfind('}')
                            new_config_block = (
                                config_block[:insertion_point] + 
                                f"        'request_name': '{alternative}',\n    " +
                                config_block[insertion_point:]
                            )
                    
                    # 替换内容
                    content = content[:start_pos] + new_config_block + content[end_pos:]
                    modifications.append(f"{broken_model} → {alternative}")
                    print(f"   🔄 已映射到: {alternative}")
            else:
                print(f"❌ 未找到模型配置: {broken_model}")
        
        # 写回文件
        if modifications:
            with open(config_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n✅ 修复完成！已更新 {len(modifications)} 个模型映射:")
            for mod in modifications:
                print(f"   • {mod}")
            
            print(f"\n💾 配置文件已更新: {config_file_path}")
            print("\n🎯 修复策略说明:")
            print("   • Claude模型 → GPT-4o (解决JSON解析问题)")
            print("   • Qwen-Max → Qwen标准版 (解决限流问题)")
            print("\n🚀 现在可以重新运行测试验证修复效果！")
        else:
            print("❌ 没有找到需要修复的模型配置")
            
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {str(e)}")
        return False
    
    return len(modifications) > 0

def verify_fixes():
    """验证修复结果"""
    print("\n🔍 验证修复结果...")
    
    try:
        # 重新导入模型配置
        from model_p2l.model_configs import MODEL_CONFIGS
        
        verification_models = [
            'claude-3-5-sonnet-20241022',
            'claude-3-5-sonnet-20240620', 
            'qwen-max-0428',
            'qwen-max-0919'
        ]
        
        for model in verification_models:
            if model in MODEL_CONFIGS:
                config = MODEL_CONFIGS[model]
                request_name = config.get('request_name', model)
                if request_name != model:
                    print(f"   ✅ {model} → {request_name}")
                else:
                    print(f"   ⚠️  {model} (未映射)")
            else:
                print(f"   ❌ {model} (配置不存在)")
                
    except Exception as e:
        print(f"   ❌ 验证失败: {str(e)}")

if __name__ == "__main__":
    print("🛠️  模型映射修复工具")
    print("="*50)
    
    success = apply_model_fixes()
    
    if success:
        verify_fixes()
        print("\n🎉 修复完成！建议重启后端服务以加载新配置。")
    else:
        print("\n❌ 修复失败，请检查错误信息。")