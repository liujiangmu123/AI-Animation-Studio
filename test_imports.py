#!/usr/bin/env python3
"""
测试主窗口的导入问题
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试主窗口的导入"""
    try:
        print("测试核心模块导入...")
        from core.config import AppConfig
        from core.project_manager import ProjectManager
        from core.logger import get_logger
        from core.video_exporter import VideoExporter
        from core.template_manager import TemplateManager
        from core.command_manager import CommandManager
        from core.data_structures import Project
        print("✓ 核心模块导入成功")
        
        print("测试UI模块导入...")
        from ui.theme_system import get_theme_manager
        from ui.color_scheme_manager import color_scheme_manager, ColorRole
        from ui.timeline_widget import TimelineWidget
        from ui.ai_generator_widget import AIGeneratorWidget
        from ui.preview_widget import PreviewWidget
        from ui.stage_widget import StageWidget
        from ui.properties_widget import PropertiesWidget
        from ui.elements_widget import ElementsWidget
        print("✓ 基础UI模块导入成功")
        
        print("测试高级UI模块导入...")
        from ui.value_hierarchy_layout import ValueHierarchyLayout
        from ui.progressive_disclosure_manager import ProgressiveDisclosureManager
        from ui.adaptive_interface_manager import AdaptiveInterfaceManager
        print("✓ 高级UI模块导入成功")
        
        print("所有导入测试通过！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

if __name__ == "__main__":
    test_imports()
