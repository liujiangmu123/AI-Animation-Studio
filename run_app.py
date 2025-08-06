#!/usr/bin/env python3
"""
AI Animation Studio - 应用程序启动脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 检查依赖
def check_dependencies():
    """检查必要的依赖"""
    required_packages = [
        "PyQt6",
        "requests"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装依赖:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True


def setup_environment():
    """设置环境"""
    try:
        # 创建必要的目录
        directories = [
            "solutions",
            "logs",
            "exports",
            "temp",
            "cache"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        # 检查是否有示例数据
        solutions_dir = Path("solutions")
        if not any(solutions_dir.glob("*.json")):
            print("检测到没有示例数据，正在生成...")
            
            try:
                from utils.sample_solutions_generator import SampleSolutionsGenerator
                from core.enhanced_solution_manager import EnhancedSolutionManager
                
                # 生成示例数据
                solution_manager = EnhancedSolutionManager()
                sample_generator = SampleSolutionsGenerator()
                
                # 生成基础示例
                basic_solutions = sample_generator.generate_sample_solutions()
                for solution in basic_solutions:
                    solution_manager.add_solution(solution, auto_evaluate=True)
                
                # 生成高级示例
                advanced_solutions = sample_generator.create_advanced_samples()
                for solution in advanced_solutions:
                    solution_manager.add_solution(solution, auto_evaluate=True)
                
                print(f"已生成 {len(basic_solutions) + len(advanced_solutions)} 个示例方案")
                
            except Exception as e:
                print(f"生成示例数据失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"设置环境失败: {e}")
        return False


def main():
    """主函数"""
    print("AI Animation Studio - 启动中...")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 设置环境
    if not setup_environment():
        print("环境设置失败")
        sys.exit(1)
    
    try:
        # 导入PyQt6
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QIcon
        
        # 创建应用程序
        app = QApplication(sys.argv)
        app.setApplicationName("AI Animation Studio")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("AI Animation Studio")
        
        # 设置应用程序图标（如果存在）
        icon_path = project_root / "assets" / "icon.png"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        
        # 设置样式
        app.setStyle("Fusion")
        
        # 导入主窗口
        from ui.main_window import MainWindow
        
        # 创建主窗口
        main_window = MainWindow()
        main_window.show()
        
        print("AI Animation Studio 启动成功！")
        print("享受您的动画创作之旅！")
        
        # 运行应用程序
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保已正确安装所有依赖")
        sys.exit(1)
        
    except Exception as e:
        print(f"启动应用程序失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
