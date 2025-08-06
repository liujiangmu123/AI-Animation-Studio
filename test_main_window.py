#!/usr/bin/env python3
"""
测试主窗口初始化
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_main_window_init():
    """测试主窗口初始化"""
    try:
        print("开始测试主窗口初始化...")
        
        # 导入必要的模块
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from core.config import AppConfig

        # 设置WebEngine共享OpenGL上下文（必须在创建QApplication之前）
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

        # 创建应用程序实例
        app = QApplication(sys.argv)
        
        print("✓ QApplication创建成功")
        
        # 创建配置
        config = AppConfig()
        print("✓ AppConfig创建成功")
        
        # 尝试导入主窗口
        from ui.main_window import MainWindow
        print("✓ MainWindow导入成功")
        
        # 创建主窗口实例
        print("正在创建主窗口实例...")
        main_window = MainWindow(config)
        print("✓ MainWindow实例创建成功")
        
        # 检查关键组件是否存在
        components_to_check = [
            'project_manager',
            'theme_manager', 
            'video_exporter',
            'template_manager',
            'command_manager',
            'auto_save_manager'
        ]
        
        for component in components_to_check:
            if hasattr(main_window, component):
                print(f"✓ {component} 存在")
            else:
                print(f"❌ {component} 不存在")
        
        # 检查UI组件是否存在
        ui_components_to_check = [
            'top_toolbar_widget',
            'main_splitter',
            'timeline_area_widget',
            'status_bar'
        ]
        
        for component in ui_components_to_check:
            if hasattr(main_window, component):
                print(f"✓ UI组件 {component} 存在")
            else:
                print(f"❌ UI组件 {component} 不存在")
        
        # 显示主窗口
        main_window.show()
        print("✓ 主窗口显示成功")
        
        # 简单测试窗口大小
        size = main_window.size()
        print(f"✓ 窗口大小: {size.width()}x{size.height()}")
        
        print("主窗口初始化测试完成！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 初始化错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_main_window_init()
    if success:
        print("\n🎉 主窗口初始化测试通过！")
        sys.exit(0)
    else:
        print("\n💥 主窗口初始化测试失败！")
        sys.exit(1)
