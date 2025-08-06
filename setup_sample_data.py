"""
AI Animation Studio - 示例数据设置脚本
初始化系统并生成示例方案数据
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.enhanced_solution_manager import EnhancedSolutionManager
from utils.sample_solutions_generator import SampleSolutionsGenerator
from core.logger import get_logger

logger = get_logger("setup_sample_data")


def setup_sample_data():
    """设置示例数据"""
    try:
        logger.info("开始设置示例数据...")
        
        # 创建方案管理器
        solution_manager = EnhancedSolutionManager()
        
        # 创建示例方案生成器
        sample_generator = SampleSolutionsGenerator()
        
        # 检查是否已有方案
        existing_count = len(solution_manager.solutions)
        
        if existing_count > 0:
            print(f"检测到已有 {existing_count} 个方案")
            response = input("是否要添加示例数据？(y/n): ")
            
            if response.lower() != 'y':
                print("取消添加示例数据")
                return
        
        # 生成并添加示例方案
        print("正在生成示例方案...")
        
        # 生成基础示例
        basic_solutions = sample_generator.generate_sample_solutions()
        print(f"生成了 {len(basic_solutions)} 个基础示例方案")
        
        for solution in basic_solutions:
            solution_manager.add_solution(solution, auto_evaluate=True)
        
        # 生成高级示例
        advanced_solutions = sample_generator.create_advanced_samples()
        print(f"生成了 {len(advanced_solutions)} 个高级示例方案")
        
        for solution in advanced_solutions:
            solution_manager.add_solution(solution, auto_evaluate=True)
        
        # 显示统计信息
        stats = solution_manager.get_statistics()
        
        print("\n=== 示例数据设置完成 ===")
        print(f"总方案数: {stats.get('total_solutions', 0)}")
        print(f"平均质量: {stats.get('average_quality', 0):.1f}")
        
        # 分类分布
        print("\n分类分布:")
        category_dist = stats.get('category_distribution', {})
        for category, count in category_dist.items():
            print(f"  {category}: {count}")
        
        # 技术栈分布
        print("\n技术栈分布:")
        tech_dist = stats.get('tech_distribution', {})
        for tech, count in tech_dist.items():
            print(f"  {tech}: {count}")
        
        # 质量分布
        print("\n质量分布:")
        quality_dist = stats.get('quality_distribution', {})
        for quality, count in quality_dist.items():
            print(f"  {quality}: {count}")
        
        logger.info("示例数据设置完成")
        
    except Exception as e:
        logger.error(f"设置示例数据失败: {e}")
        print(f"错误: {e}")


def reset_all_data():
    """重置所有数据"""
    try:
        response = input("确定要重置所有数据吗？这将删除所有现有方案！(yes/no): ")
        
        if response.lower() != 'yes':
            print("取消重置操作")
            return
        
        # 删除存储目录
        storage_path = "solutions"
        if os.path.exists(storage_path):
            import shutil
            shutil.rmtree(storage_path)
            print("已删除现有数据")
        
        # 重新设置示例数据
        setup_sample_data()
        
    except Exception as e:
        logger.error(f"重置数据失败: {e}")
        print(f"错误: {e}")


def show_current_data():
    """显示当前数据"""
    try:
        solution_manager = EnhancedSolutionManager()
        stats = solution_manager.get_statistics()
        
        print("\n=== 当前数据统计 ===")
        print(f"总方案数: {stats.get('total_solutions', 0)}")
        print(f"收藏数: {stats.get('total_favorites', 0)}")
        print(f"总使用次数: {stats.get('total_usage', 0)}")
        print(f"平均质量: {stats.get('average_quality', 0):.1f}")
        print(f"平均评分: {stats.get('average_rating', 0):.1f}")
        
        if stats.get('top_solution'):
            top_solution = stats['top_solution']
            print(f"最佳方案: {top_solution.name} (质量: {top_solution.metrics.overall_score:.1f})")
        
        # 最近创建的方案
        solutions = list(solution_manager.solutions.values())
        if solutions:
            recent_solutions = sorted(solutions, key=lambda x: x.created_at, reverse=True)[:5]
            
            print("\n最近的方案:")
            for i, solution in enumerate(recent_solutions, 1):
                print(f"  {i}. {solution.name} (质量: {solution.metrics.overall_score:.1f})")
        
    except Exception as e:
        logger.error(f"显示当前数据失败: {e}")
        print(f"错误: {e}")


def main():
    """主函数"""
    print("AI Animation Studio - 示例数据设置工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 设置示例数据")
        print("2. 显示当前数据")
        print("3. 重置所有数据")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == "1":
            setup_sample_data()
        elif choice == "2":
            show_current_data()
        elif choice == "3":
            reset_all_data()
        elif choice == "4":
            print("再见！")
            break
        else:
            print("无效选择，请重试")


if __name__ == "__main__":
    main()
