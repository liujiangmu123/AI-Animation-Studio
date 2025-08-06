#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Animation Studio - 主程序入口
AI驱动的动画工作站，通过自然语言创作专业级Web动画

Author: AI Animation Studio Team
Version: 1.0.0
"""

import sys
import os
import traceback
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# PyQt6 imports
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QIcon, QFont

# 项目模块
from ui.main_window import MainWindow
from core.config import AppConfig
from core.logger import setup_logger

def setup_application():
    """设置应用程序"""
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("AI Animation Studio")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AI Animation Studio Team")
    app.setOrganizationDomain("ai-animation-studio.com")
    
    # 设置高DPI支持（PyQt6兼容性处理）
    try:
        # PyQt6早期版本
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        # PyQt6新版本中高DPI缩放默认启用，无需手动设置
        pass
    
    # 设置默认字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    # 设置应用程序图标
    icon_path = project_root / "assets" / "icons" / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    return app

def check_dependencies():
    """检查依赖项"""
    missing_deps = []
    
    try:
        import PyQt6
    except ImportError:
        missing_deps.append("PyQt6")
    
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
    except ImportError:
        missing_deps.append("PyQt6-WebEngine")
    
    try:
        from google import genai
    except ImportError:
        missing_deps.append("google-generativeai")
    
    if missing_deps:
        error_msg = f"缺少以下依赖项：\n{', '.join(missing_deps)}\n\n"
        error_msg += "请运行以下命令安装：\n"
        error_msg += f"pip install {' '.join(missing_deps)}"
        
        QMessageBox.critical(None, "依赖项错误", error_msg)
        return False
    
    return True

def main():
    """主函数"""
    try:
        # 设置日志
        logger = setup_logger()
        logger.info("启动 AI Animation Studio...")
        
        # 检查依赖项
        if not check_dependencies():
            sys.exit(1)
        
        # 创建应用程序
        app = setup_application()
        
        # 加载配置
        config = AppConfig.load()
        
        # 创建主窗口
        main_window = MainWindow(config)
        main_window.show()
        
        logger.info("AI Animation Studio 启动成功")
        
        # 运行应用程序
        sys.exit(app.exec())
        
    except Exception as e:
        error_msg = f"启动失败：{str(e)}\n\n详细错误：\n{traceback.format_exc()}"
        print(error_msg)
        
        # 尝试显示错误对话框
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            QMessageBox.critical(None, "启动错误", error_msg)
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
