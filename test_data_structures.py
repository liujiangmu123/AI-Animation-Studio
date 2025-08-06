#!/usr/bin/env python3
"""
测试数据结构
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_data_structures():
    """测试数据结构"""
    try:
        print("开始测试数据结构...")
        
        # 导入数据结构模块
        from core.data_structures import Project, Element, TimeSegment, Asset, ProjectTemplate
        print("✓ 数据结构模块导入成功")
        
        # 测试Project类
        project = Project()
        print(f"✓ Project创建成功")
        print(f"  - 项目名称: {project.name}")
        print(f"  - 画布尺寸: {project.canvas_width}x{project.canvas_height}")
        print(f"  - 项目时长: {project.duration}秒")
        print(f"  - 帧率: {project.fps}")
        
        # 验证没有字段冲突
        if hasattr(project, 'total_duration'):
            print("❌ 发现字段冲突: total_duration字段仍然存在")
            return False
        else:
            print("✓ 字段冲突已修复: total_duration字段已移除")
        
        # 测试Element类
        element = Element()
        print(f"✓ Element创建成功")
        print(f"  - 元素ID: {element.element_id}")
        print(f"  - 元素类型: {element.element_type}")
        
        # 测试TimeSegment类
        segment = TimeSegment()
        print(f"✓ TimeSegment创建成功")
        print(f"  - 开始时间: {segment.start_time}")
        print(f"  - 结束时间: {segment.end_time}")
        print(f"  - 时间段长度: {segment.duration}")
        
        # 测试Asset类
        asset = Asset()
        print(f"✓ Asset创建成功")
        print(f"  - 资产ID: {asset.asset_id}")
        print(f"  - 资产类型: {asset.asset_type}")
        
        # 测试ProjectTemplate类
        template = ProjectTemplate()
        print(f"✓ ProjectTemplate创建成功")
        print(f"  - 模板ID: {template.id}")
        print(f"  - 模板时长: {template.duration}")
        
        print("数据结构测试完成！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 数据结构错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_structures()
    if success:
        print("\n🎉 数据结构测试通过！")
        sys.exit(0)
    else:
        print("\n💥 数据结构测试失败！")
        sys.exit(1)
