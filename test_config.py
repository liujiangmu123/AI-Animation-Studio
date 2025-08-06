#!/usr/bin/env python3
"""
测试配置系统
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_system():
    """测试配置系统"""
    try:
        print("开始测试配置系统...")
        
        # 导入配置模块
        from core.config import AppConfig, ThemeType, LanguageType
        print("✓ 配置模块导入成功")
        
        # 创建默认配置
        config = AppConfig()
        print("✓ 默认配置创建成功")
        
        # 测试配置属性
        print(f"✓ 画布尺寸: {config.canvas.width}x{config.canvas.height}")
        print(f"✓ 时间轴时长: {config.timeline.total_duration}秒")
        print(f"✓ 音频音量: {config.audio.volume}")
        print(f"✓ 主题类型: {config.ui.theme}")
        print(f"✓ 语言: {config.ui.language}")
        
        # 测试配置验证
        errors = config.validate()
        if errors:
            print(f"⚠️ 配置验证发现问题: {errors}")
        else:
            print("✓ 配置验证通过")
        
        # 测试配置保存和加载
        test_config_file = Path("test_config.json")
        try:
            config.save(test_config_file)
            print("✓ 配置保存成功")
            
            loaded_config = AppConfig.load(test_config_file)
            print("✓ 配置加载成功")
            
            # 清理测试文件
            if test_config_file.exists():
                test_config_file.unlink()
                print("✓ 测试文件清理完成")
                
        except Exception as e:
            print(f"❌ 配置保存/加载测试失败: {e}")
            return False
        
        print("配置系统测试完成！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 配置系统错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_config_system()
    if success:
        print("\n🎉 配置系统测试通过！")
        sys.exit(0)
    else:
        print("\n💥 配置系统测试失败！")
        sys.exit(1)
