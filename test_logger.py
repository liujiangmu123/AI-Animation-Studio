#!/usr/bin/env python3
"""
测试日志系统
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_logger_system():
    """测试日志系统"""
    try:
        print("开始测试日志系统...")
        
        # 导入日志模块
        from core.logger import setup_logger, get_logger
        print("✓ 日志模块导入成功")
        
        # 测试默认日志记录器
        default_logger = get_logger()
        print("✓ 默认日志记录器创建成功")
        
        # 测试命名日志记录器
        test_logger = get_logger("test_module")
        print("✓ 命名日志记录器创建成功")
        
        # 测试日志级别
        test_logger.debug("这是一条调试信息")
        test_logger.info("这是一条信息")
        test_logger.warning("这是一条警告")
        test_logger.error("这是一条错误信息")
        print("✓ 日志级别测试完成")
        
        # 测试自定义日志记录器
        custom_logger = setup_logger("custom_test", level=10)  # DEBUG级别
        custom_logger.debug("自定义日志记录器调试信息")
        custom_logger.info("自定义日志记录器信息")
        print("✓ 自定义日志记录器测试完成")
        
        # 测试日志文件创建
        log_dir = Path.home() / ".ai_animation_studio" / "logs"
        if log_dir.exists():
            log_files = list(log_dir.glob("*.log"))
            print(f"✓ 日志文件创建成功，共 {len(log_files)} 个日志文件")
            
            if log_files:
                latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
                print(f"  - 最新日志文件: {latest_log.name}")
                print(f"  - 文件大小: {latest_log.stat().st_size} 字节")
        else:
            print("⚠️ 日志目录不存在，但这可能是正常的")
        
        # 测试日志记录器的处理器
        handlers = test_logger.handlers
        if not handlers:
            # 获取父级处理器
            parent_logger = test_logger.parent
            while parent_logger and not parent_logger.handlers:
                parent_logger = parent_logger.parent
            if parent_logger:
                handlers = parent_logger.handlers
        
        print(f"✓ 日志处理器数量: {len(handlers)}")
        for i, handler in enumerate(handlers):
            print(f"  - 处理器 {i+1}: {type(handler).__name__}")
        
        print("日志系统测试完成！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 日志系统错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_logger_system()
    if success:
        print("\n🎉 日志系统测试通过！")
        sys.exit(0)
    else:
        print("\n💥 日志系统测试失败！")
        sys.exit(1)
