#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Animation Studio - 快速启动脚本
用于开发和测试
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查依赖项"""
    missing_deps = []
    
    try:
        import PyQt6
        print("✅ PyQt6 已安装")
    except ImportError:
        missing_deps.append("PyQt6")
        print("❌ PyQt6 未安装")
    
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        print("✅ PyQt6-WebEngine 已安装")
    except ImportError:
        missing_deps.append("PyQt6-WebEngine")
        print("❌ PyQt6-WebEngine 未安装")
    
    try:
        from google import genai
        print("✅ google-generativeai 已安装")
    except ImportError:
        missing_deps.append("google-generativeai")
        print("⚠️ google-generativeai 未安装（AI功能将不可用）")
    
    if missing_deps:
        print(f"\n缺少依赖项：{', '.join(missing_deps)}")
        print("请运行以下命令安装：")
        print(f"pip install {' '.join(missing_deps)}")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 启动 AI Animation Studio...")
    print(f"📁 项目路径: {project_root}")
    
    # 检查依赖项
    if not check_dependencies():
        input("\n按回车键退出...")
        return
    
    # 导入并运行主程序
    try:
        from main import main as run_main
        run_main()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")

if __name__ == "__main__":
    main()
