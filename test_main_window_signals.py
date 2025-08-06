#!/usr/bin/env python3
"""
测试主窗口信号连接
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_main_window_signals():
    """测试主窗口信号连接"""
    try:
        print("开始测试主窗口信号连接...")
        
        # 导入PyQt6
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        
        # 创建应用程序
        app = QApplication(sys.argv)
        print("✓ PyQt6应用程序创建成功")
        
        # 导入主窗口
        from ui.main_window import MainWindow
        print("✓ 主窗口模块导入成功")
        
        # 创建主窗口
        main_window = MainWindow()
        print("✓ 主窗口创建成功")
        
        # 检查信号处理方法是否存在
        signal_methods = [
            'on_project_changed',
            'on_theme_changed', 
            'on_time_changed',
            'on_solutions_generated',
            'on_element_selected',
            'on_element_selected_for_properties',
            'on_element_updated',
            'on_description_ready',
            'on_prompt_ready',
            'on_animation_requested',
            'on_solution_selected',
            'on_solution_applied',
            'on_solution_analyzed'
        ]
        
        missing_methods = []
        for method_name in signal_methods:
            if hasattr(main_window, method_name):
                print(f"✓ 信号处理方法存在: {method_name}")
            else:
                missing_methods.append(method_name)
                print(f"❌ 信号处理方法缺失: {method_name}")
        
        if missing_methods:
            print(f"⚠️ 发现 {len(missing_methods)} 个缺失的信号处理方法")
        else:
            print("✓ 所有信号处理方法都存在")
        
        # 检查主要组件是否存在
        components = [
            'timeline_widget',
            'ai_generator_widget', 
            'stage_widget',
            'elements_widget',
            'properties_widget',
            'preview_widget'
        ]
        
        existing_components = []
        for component_name in components:
            if hasattr(main_window, component_name):
                existing_components.append(component_name)
                print(f"✓ 组件存在: {component_name}")
            else:
                print(f"⚠️ 组件不存在: {component_name}")
        
        print(f"✓ 存在的组件数量: {len(existing_components)}/{len(components)}")
        
        # 检查信号是否存在
        signals = [
            'project_changed',
            'theme_changed'
        ]
        
        for signal_name in signals:
            if hasattr(main_window, signal_name):
                print(f"✓ 信号存在: {signal_name}")
            else:
                print(f"⚠️ 信号不存在: {signal_name}")
        
        # 检查管理器是否存在
        managers = [
            'project_manager',
            'theme_manager',
            'config'
        ]
        
        for manager_name in managers:
            if hasattr(main_window, manager_name):
                print(f"✓ 管理器存在: {manager_name}")
            else:
                print(f"❌ 管理器不存在: {manager_name}")
        
        print("主窗口信号连接测试完成！")
        
        # 清理
        app.quit()
        return len(missing_methods) == 0
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 主窗口信号连接错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_main_window_signals()
    if success:
        print("\n🎉 主窗口信号连接测试通过！")
        sys.exit(0)
    else:
        print("\n💥 主窗口信号连接测试失败！")
        sys.exit(1)
