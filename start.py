#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Animation Studio - 简化启动脚本
兼容性更好的启动方式
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_basic_imports():
    """检查基本导入"""
    print("📦 检查基本依赖...")
    
    # 检查PyQt6
    try:
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6 可用")
    except ImportError as e:
        print(f"❌ PyQt6 导入失败: {e}")
        print("请安装: pip install PyQt6")
        return False
    
    # 检查WebEngine（可选）
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        print("✅ PyQt6-WebEngine 可用")
    except ImportError:
        print("⚠️ PyQt6-WebEngine 不可用，预览功能将受限")
        print("建议安装: pip install PyQt6-WebEngine")
    
    # 检查AI库（可选）
    try:
        from google import genai
        print("✅ google-generativeai 可用")
    except ImportError:
        print("⚠️ google-generativeai 不可用，AI功能将受限")
        print("建议安装: pip install google-generativeai")
    
    return True

def start_application():
    """启动应用程序"""
    print("🚀 启动 AI Animation Studio...")
    
    try:
        # 导入核心模块
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont
        
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 设置应用程序属性
        app.setApplicationName("AI Animation Studio")
        app.setApplicationVersion("1.0.0")
        
        # 设置字体
        try:
            font = QFont("Microsoft YaHei", 9)
            app.setFont(font)
        except:
            pass
        
        # 导入主窗口
        from core.config import AppConfig
        from ui.main_window import MainWindow
        
        # 加载配置
        config = AppConfig.load()
        
        # 验证配置
        errors = config.validate()
        if errors:
            print("配置验证警告:")
            for error in errors:
                print(f"  - {error}")

            # 如果缺少API Key，提示用户设置
            if "Gemini API密钥不能为空" in errors:
                print("\n💡 提示: 运行 'python setup_api_key.py' 来设置API Key")
        
        # 创建主窗口
        main_window = MainWindow(config)
        main_window.show()
        
        print("✅ 应用程序启动成功")
        print("💡 提示: 在AI生成器中设置Gemini API Key以使用AI功能")
        
        # 运行应用程序
        return app.exec()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所有必需的依赖项")
        return 1
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """主函数"""
    print("=" * 50)
    print("🎨 AI Animation Studio")
    print("AI驱动的动画工作站")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        input("\n按回车键退出...")
        return 1
    
    # 检查基本导入
    if not check_basic_imports():
        print("\n❌ 依赖检查失败")
        print("请安装必需的依赖项后重试")
        input("\n按回车键退出...")
        return 1
    
    print("\n🎯 所有检查通过，正在启动应用...")
    
    # 启动应用程序
    exit_code = start_application()
    
    if exit_code != 0:
        input("\n按回车键退出...")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
