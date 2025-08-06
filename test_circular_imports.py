#!/usr/bin/env python3
"""
检测循环导入问题
"""

import sys
import importlib
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_circular_imports():
    """测试循环导入问题"""
    modules_to_test = [
        # 核心模块
        'core.config',
        'core.project_manager', 
        'core.data_structures',
        'core.logger',
        'core.ai_service_manager',
        'core.video_exporter',
        'core.template_manager',
        'core.command_manager',
        'core.state_manager',
        
        # UI模块
        'ui.main_window',
        'ui.timeline_widget',
        'ui.preview_widget',
        'ui.stage_widget',
        'ui.properties_widget',
        'ui.elements_widget',
        'ui.ai_generator_widget',
        'ui.theme_system',
        'ui.color_scheme_manager',
        
        # AI模块
        'ai.gemini_generator',
    ]
    
    failed_imports = []
    successful_imports = []
    
    for module_name in modules_to_test:
        try:
            print(f"测试导入: {module_name}")
            module = importlib.import_module(module_name)
            successful_imports.append(module_name)
            print(f"✓ {module_name} 导入成功")
            
        except ImportError as e:
            failed_imports.append((module_name, str(e)))
            print(f"❌ {module_name} 导入失败: {e}")
            
        except Exception as e:
            failed_imports.append((module_name, str(e)))
            print(f"❌ {module_name} 其他错误: {e}")
    
    print(f"\n=== 导入测试结果 ===")
    print(f"成功导入: {len(successful_imports)}")
    print(f"失败导入: {len(failed_imports)}")
    
    if failed_imports:
        print(f"\n失败的模块:")
        for module_name, error in failed_imports:
            print(f"  - {module_name}: {error}")
        return False
    else:
        print(f"\n🎉 所有模块导入成功，没有循环导入问题！")
        return True

if __name__ == "__main__":
    success = test_circular_imports()
    sys.exit(0 if success else 1)
