#!/usr/bin/env python3
"""
运行AI Animation Studio整体实现度分析
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from analysis.overall_implementation_analysis import OverallImplementationAnalyzer
    from core.logger import get_logger
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有必要的模块都已正确安装")
    sys.exit(1)

logger = get_logger("run_overall_implementation_analysis")

def main():
    """主函数"""
    print("🎯 AI Animation Studio - 整体实现度分析")
    print("=" * 80)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"项目路径: {project_root}")
    print()
    
    try:
        # 创建分析器
        analyzer = OverallImplementationAnalyzer(project_root)
        
        # 执行分析
        print("🔍 开始分析...")
        report = analyzer.analyze_overall_implementation()
        
        # 显示分析结果
        print("\n📊 分析结果:")
        print("=" * 50)
        
        # 四大维度评估
        print("\n🏗️ 四大维度评估:")
        print(f"  基础框架完整度: {report.basic_framework_completeness:.1%}")
        print(f"  核心创新功能: {report.core_innovation_implementation:.1%}")
        print(f"  专业软件标准: {report.professional_software_standards:.1%}")
        print(f"  可用性状态: {report.usability_status:.1%}")
        
        # 技术架构评估
        print("\n⚙️ 技术架构评估:")
        print(f"  代码结构: {report.code_structure_score:.1%}")
        print(f"  扩展性: {report.extensibility_score:.1%}")
        print(f"  稳定性: {report.stability_score:.1%}")
        print(f"  性能: {report.performance_score:.1%}")
        
        # 用户界面评估
        print("\n🎨 用户界面评估:")
        print(f"  视觉设计: {report.visual_design_score:.1%}")
        print(f"  交互设计: {report.interaction_design_score:.1%}")
        print(f"  可访问性: {report.accessibility_score:.1%}")
        print(f"  适应性: {report.adaptability_score:.1%}")
        
        # 工作流程评估
        print("\n🔄 工作流程评估:")
        print(f"  基础工作流程: {report.basic_workflow_score:.1%}")
        print(f"  核心创新工作流程: {report.core_innovation_workflow_score:.1%}")
        print(f"  效率优化: {report.efficiency_optimization_score:.1%}")
        print(f"  专业功能: {report.professional_features_score:.1%}")
        
        # 综合评估
        print("\n🎯 综合评估:")
        print(f"  总体评分: {report.overall_score:.1%}")
        print(f"  质量级别: {report.overall_level.value}")
        
        # 关键发现
        if report.critical_issues:
            print("\n🚨 关键问题:")
            for issue in report.critical_issues:
                print(f"  ❌ {issue}")
        
        if report.major_strengths:
            print("\n💪 主要优势:")
            for strength in report.major_strengths:
                print(f"  ✅ {strength}")
        
        if report.priority_recommendations:
            print("\n🎯 优先级建议:")
            for i, recommendation in enumerate(report.priority_recommendations, 1):
                print(f"  {i}. {recommendation}")
        
        # 组件分析摘要
        print("\n📋 组件分析摘要:")
        print("=" * 30)
        
        total_components = len(report.component_analyses)
        if total_components > 0:
            # 按实现级别统计
            implementation_stats = {}
            quality_stats = {}
            
            for analysis in report.component_analyses.values():
                impl_level = analysis.implementation_level.value
                quality_level = analysis.quality_level.value
                
                implementation_stats[impl_level] = implementation_stats.get(impl_level, 0) + 1
                quality_stats[quality_level] = quality_stats.get(quality_level, 0) + 1
            
            print(f"总组件数: {total_components}")
            print("\n实现级别分布:")
            for level, count in implementation_stats.items():
                percentage = count / total_components * 100
                print(f"  {level}: {count}个 ({percentage:.1f}%)")
            
            print("\n质量级别分布:")
            for level, count in quality_stats.items():
                percentage = count / total_components * 100
                print(f"  {level}: {count}个 ({percentage:.1f}%)")
            
            # 平均分数
            avg_completeness = sum(a.completeness_score for a in report.component_analyses.values()) / total_components
            avg_functionality = sum(a.functionality_score for a in report.component_analyses.values()) / total_components
            avg_code_quality = sum(a.code_quality_score for a in report.component_analyses.values()) / total_components
            
            print(f"\n平均分数:")
            print(f"  完整度: {avg_completeness:.1%}")
            print(f"  功能性: {avg_functionality:.1%}")
            print(f"  代码质量: {avg_code_quality:.1%}")
        
        # 生成HTML报告
        print("\n📄 生成HTML报告...")
        html_content = analyzer.generate_html_report(report)
        
        # 保存HTML报告
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_filename = f"overall_implementation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path = reports_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML报告已保存: {report_path}")
        
        # 生成JSON报告
        import json
        json_filename = f"overall_implementation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_path = reports_dir / json_filename
        
        # 准备JSON数据
        json_data = {
            "analysis_date": report.analysis_date.isoformat(),
            "four_dimensions": {
                "basic_framework_completeness": report.basic_framework_completeness,
                "core_innovation_implementation": report.core_innovation_implementation,
                "professional_software_standards": report.professional_software_standards,
                "usability_status": report.usability_status
            },
            "technical_architecture": {
                "code_structure_score": report.code_structure_score,
                "extensibility_score": report.extensibility_score,
                "stability_score": report.stability_score,
                "performance_score": report.performance_score
            },
            "user_interface": {
                "visual_design_score": report.visual_design_score,
                "interaction_design_score": report.interaction_design_score,
                "accessibility_score": report.accessibility_score,
                "adaptability_score": report.adaptability_score
            },
            "workflow": {
                "basic_workflow_score": report.basic_workflow_score,
                "core_innovation_workflow_score": report.core_innovation_workflow_score,
                "efficiency_optimization_score": report.efficiency_optimization_score,
                "professional_features_score": report.professional_features_score
            },
            "overall": {
                "overall_score": report.overall_score,
                "overall_level": report.overall_level.value
            },
            "key_findings": {
                "critical_issues": report.critical_issues,
                "major_strengths": report.major_strengths,
                "priority_recommendations": report.priority_recommendations
            },
            "component_analyses": {
                name: {
                    "implementation_level": analysis.implementation_level.value,
                    "quality_level": analysis.quality_level.value,
                    "completeness_score": analysis.completeness_score,
                    "functionality_score": analysis.functionality_score,
                    "code_quality_score": analysis.code_quality_score,
                    "user_experience_score": analysis.user_experience_score,
                    "professional_standard_score": analysis.professional_standard_score,
                    "issues": analysis.issues,
                    "strengths": analysis.strengths,
                    "recommendations": analysis.recommendations
                }
                for name, analysis in report.component_analyses.items()
            }
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON报告已保存: {json_path}")
        
        # 总结
        print("\n" + "=" * 80)
        print("🎉 整体实现度分析完成！")
        print(f"📊 总体评分: {report.overall_score:.1%} ({report.overall_level.value})")
        
        if report.overall_score >= 0.8:
            print("✅ 系统实现度优秀，具备良好的基础和发展潜力")
        elif report.overall_score >= 0.6:
            print("⚠️ 系统实现度良好，但仍有改进空间")
        elif report.overall_score >= 0.4:
            print("🔶 系统实现度一般，需要重点改进核心功能")
        else:
            print("🔴 系统实现度较低，需要大幅改进")
        
        print(f"📄 详细报告: {report_path}")
        print(f"📊 数据报告: {json_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"分析失败: {e}")
        print(f"❌ 分析失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
