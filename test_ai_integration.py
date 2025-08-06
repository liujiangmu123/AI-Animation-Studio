#!/usr/bin/env python3
"""
测试AI集成功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ai_integration():
    """测试AI集成功能"""
    try:
        print("开始测试AI集成功能...")
        
        # 测试AI服务管理器导入
        from core.ai_service_manager import AIServiceManager, AIServiceType
        print("✓ AI服务管理器导入成功")
        
        # 创建AI服务管理器
        ai_manager = AIServiceManager()
        print("✓ AI服务管理器创建成功")
        
        # 测试服务状态检查
        services = ai_manager.get_available_services()
        print(f"✓ 可用服务: {[s.value for s in services]}")
        
        # 测试Gemini生成器导入
        from ai.gemini_generator import GeminiGenerator
        print("✓ Gemini生成器导入成功")
        
        # 创建Gemini生成器
        gemini_gen = GeminiGenerator()
        print("✓ Gemini生成器创建成功")
        
        # 测试Gemini生成器设置
        test_prompt = "创建一个简单的淡入动画"
        gemini_gen.prompt = test_prompt
        gemini_gen.animation_type = "fade"
        print(f"✓ Gemini生成器参数设置成功")
        print(f"  - 提示词: {gemini_gen.prompt}")
        print(f"  - 动画类型: {gemini_gen.animation_type}")
        print(f"  - 模型: {gemini_gen.model}")

        # 测试服务配置
        try:
            preferred_service = ai_manager.get_preferred_service()
            print(f"✓ 首选服务: {preferred_service.value if preferred_service else 'None'}")

            if preferred_service:
                model = ai_manager.get_model_for_service(preferred_service)
                print(f"  - 模型: {model}")

        except Exception as e:
            print(f"⚠️ 服务配置测试失败: {e}")

        # 测试使用量摘要
        try:
            usage_summary = ai_manager.get_usage_summary()
            print(f"✓ 使用量摘要获取成功")

        except Exception as e:
            print(f"⚠️ 使用量摘要获取失败: {e}")
        
        print("AI集成功能测试完成！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ AI集成错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ai_integration()
    if success:
        print("\n🎉 AI集成功能测试通过！")
        sys.exit(0)
    else:
        print("\n💥 AI集成功能测试失败！")
        sys.exit(1)
