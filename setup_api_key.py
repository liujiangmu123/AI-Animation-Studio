#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Animation Studio - API Key 设置工具
用于设置Gemini API Key
"""

import json
from pathlib import Path

def setup_api_key():
    """设置API Key"""
    print("🔑 AI Animation Studio - API Key 设置")
    print("=" * 50)
    
    # 查找配置文件
    project_root = Path(__file__).parent.parent
    config_file = project_root / "config.json"
    
    print(f"📁 配置文件位置: {config_file}")
    
    # 读取现有配置
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("✅ 已读取现有配置")
        except Exception as e:
            print(f"❌ 读取配置失败: {e}")
            return False
    else:
        print("❌ 配置文件不存在")
        return False
    
    # 显示当前API Key状态
    current_key = config.get("ai", {}).get("gemini_api_key", "")
    if current_key:
        masked_key = current_key[:8] + "*" * (len(current_key) - 12) + current_key[-4:]
        print(f"🔍 当前API Key: {masked_key}")
    else:
        print("⚠️ 当前未设置API Key")
    
    print("\n💡 获取Gemini API Key:")
    print("   1. 访问 https://aistudio.google.com/")
    print("   2. 登录Google账号")
    print("   3. 点击 'Get API Key' 获取免费API Key")
    print("   4. 复制API Key并粘贴到下面")
    
    # 输入新的API Key
    print("\n🔑 请输入您的Gemini API Key:")
    print("   (输入 'skip' 跳过，输入 'clear' 清空)")
    
    new_key = input("API Key: ").strip()
    
    if new_key.lower() == 'skip':
        print("⏭️ 跳过API Key设置")
        return True
    elif new_key.lower() == 'clear':
        new_key = ""
        print("🗑️ 已清空API Key")
    elif new_key:
        # 简单验证API Key格式
        if not new_key.startswith('AIzaSy') or len(new_key) < 30:
            print("⚠️ API Key格式可能不正确，但仍将保存")
        print("✅ API Key已设置")
    else:
        print("⚠️ 未输入API Key")
        return True
    
    # 更新配置
    if "ai" not in config:
        config["ai"] = {}
    
    config["ai"]["gemini_api_key"] = new_key
    
    # 保存配置
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("💾 配置已保存")
        
        # 验证保存
        with open(config_file, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        
        saved_key = saved_config.get("ai", {}).get("gemini_api_key", "")
        if saved_key == new_key:
            print("✅ 配置验证成功")
        else:
            print("❌ 配置验证失败")
            return False
            
    except Exception as e:
        print(f"❌ 保存配置失败: {e}")
        return False
    
    print("\n🎉 API Key设置完成！")
    print("现在您可以运行 AI Animation Studio 并使用AI功能了")
    
    return True

def main():
    """主函数"""
    try:
        success = setup_api_key()
        if success:
            print("\n🚀 下一步:")
            print("   python start.py  # 启动应用程序")
        else:
            print("\n❌ 设置失败，请重试")
        
        input("\n按回车键退出...")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户取消操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        input("\n按回车键退出...")

if __name__ == "__main__":
    main()
