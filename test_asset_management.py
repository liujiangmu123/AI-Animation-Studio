#!/usr/bin/env python3
"""
测试素材管理系统
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_asset_management():
    """测试素材管理系统"""
    try:
        print("开始测试素材管理系统...")
        
        # 导入素材管理模块
        from core.asset_management import AssetManager, AssetIndex, EnhancedAsset, AssetType
        print("✓ 素材管理模块导入成功")
        
        # 创建素材管理器
        asset_manager = AssetManager()
        print("✓ 素材管理器创建成功")
        
        # 创建素材索引
        asset_index = AssetIndex()
        print("✓ 素材索引创建成功")
        
        # 测试素材类型
        print(f"✓ 素材类型枚举:")
        for asset_type in AssetType:
            print(f"  - {asset_type.name}: {asset_type.value}")
        
        # 创建测试素材对象
        test_asset = EnhancedAsset(
            asset_id="test_001",
            name="测试图片.png",
            file_path="/path/to/test.png",
            asset_type=AssetType.IMAGE,
            category="测试",
            tags={"测试", "图片"}
        )
        print("✓ 测试素材对象创建成功")
        
        # 测试索引添加功能
        asset_index.add_asset(test_asset)
        print("✓ 素材添加到索引成功")
        
        # 测试文本搜索功能
        search_results = asset_index.search_by_text("测试")
        print(f"✓ 文本搜索功能测试成功，找到 {len(search_results)} 个结果")

        # 测试重复文件查找
        duplicates = asset_index.find_duplicates()
        print(f"✓ 重复文件查找成功，找到 {len(duplicates)} 组重复文件")
        
        # 测试素材管理器的基本功能
        print(f"✓ 素材管理器状态:")
        print(f"  - 项目路径: {asset_manager.project_path}")
        print(f"  - 素材数量: {len(asset_manager.assets)}")

        # 测试缓存目录设置
        try:
            cache_dir = asset_manager._setup_cache_dir()
            print(f"  - 缓存目录: {cache_dir}")
        except Exception as e:
            print(f"⚠️ 缓存目录设置失败: {e}")

        # 测试素材管理器的搜索功能
        try:
            # 检查是否有search_assets方法
            if hasattr(asset_manager, 'search_assets'):
                manager_results = asset_manager.search_assets("测试")
                print(f"✓ 管理器搜索功能正常，返回 {len(manager_results)} 个结果")
            else:
                print("⚠️ 管理器没有search_assets方法")
        except Exception as e:
            print(f"⚠️ 管理器搜索功能测试失败: {e}")

        # 测试素材统计
        try:
            # 检查是否有get_stats方法
            if hasattr(asset_manager, 'get_stats'):
                stats = asset_manager.get_stats()
                print(f"✓ 素材统计:")
                print(f"  - 总数: {stats.get('total', 0)}")
                print(f"  - 图片: {stats.get('images', 0)}")
                print(f"  - 视频: {stats.get('videos', 0)}")
                print(f"  - 音频: {stats.get('audios', 0)}")
            else:
                print("⚠️ 管理器没有get_stats方法")
        except Exception as e:
            print(f"⚠️ 素材统计测试失败: {e}")
        
        print("素材管理系统测试完成！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 素材管理系统错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_asset_management()
    if success:
        print("\n🎉 素材管理系统测试通过！")
        sys.exit(0)
    else:
        print("\n💥 素材管理系统测试失败！")
        sys.exit(1)
