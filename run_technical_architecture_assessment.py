#!/usr/bin/env python3
"""
运行AI Animation Studio技术架构评估
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from analysis.technical_architecture_assessment import TechnicalArchitectureAssessor
    from core.logger import get_logger
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有必要的模块都已正确安装")
    sys.exit(1)

logger = get_logger("run_technical_architecture_assessment")

def main():
    """主函数"""
    print("🏗️ AI Animation Studio - 技术架构评估")
    print("=" * 80)
    print(f"评估时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"项目路径: {project_root}")
    print()
    
    try:
        # 创建评估器
        assessor = TechnicalArchitectureAssessor(project_root)
        
        # 执行评估
        print("🔍 开始技术架构评估...")
        report = assessor.assess_technical_architecture()
        
        # 显示评估结果
        print("\n📊 评估结果:")
        print("=" * 50)
        
        # 综合评估
        print(f"\n🎯 综合评估:")
        print(f"  总体评分: {report.overall_architecture_score:.1%}")
        print(f"  架构质量: {report.overall_architecture_quality.value}")
        
        # 四大维度评估
        print(f"\n🏗️ 四大维度评估:")
        print(f"  代码结构质量: {report.code_structure_quality.value}")
        print(f"  扩展性质量: {report.extensibility_quality.value}")
        print(f"  稳定性质量: {report.stability_quality.value}")
        print(f"  性能质量: {report.performance_quality.value}")
        
        # 代码结构指标
        print(f"\n📋 代码结构指标:")
        metrics = report.code_structure_metrics
        print(f"  总文件数: {metrics.total_files}")
        print(f"  总代码行数: {metrics.total_lines}")
        print(f"  总类数: {metrics.total_classes}")
        print(f"  总函数数: {metrics.total_functions}")
        print(f"  平均文件大小: {metrics.average_file_size:.1f} 行")
        print(f"  文档覆盖率: {metrics.documentation_coverage:.1%}")
        print(f"  类型注解覆盖率: {metrics.type_annotation_coverage:.1%}")
        print(f"  代码重复率: {metrics.code_duplication_rate:.1%}")
        
        # 扩展性指标
        print(f"\n🔧 扩展性指标:")
        ext_metrics = report.extensibility_metrics
        print(f"  接口抽象评分: {ext_metrics.interface_abstraction_score:.1%}")
        print(f"  插件架构评分: {ext_metrics.plugin_architecture_score:.1%}")
        print(f"  配置灵活性评分: {ext_metrics.configuration_flexibility_score:.1%}")
        print(f"  API设计评分: {ext_metrics.api_design_score:.1%}")
        print(f"  依赖注入评分: {ext_metrics.dependency_injection_score:.1%}")
        print(f"  模块化设计评分: {ext_metrics.modular_design_score:.1%}")
        
        # 稳定性指标
        print(f"\n🛡️ 稳定性指标:")
        stab_metrics = report.stability_metrics
        print(f"  错误处理覆盖率: {stab_metrics.error_handling_coverage:.1%}")
        print(f"  异常安全性评分: {stab_metrics.exception_safety_score:.1%}")
        print(f"  资源管理评分: {stab_metrics.resource_management_score:.1%}")
        print(f"  线程安全性评分: {stab_metrics.thread_safety_score:.1%}")
        print(f"  内存安全性评分: {stab_metrics.memory_safety_score:.1%}")
        print(f"  优雅降级评分: {stab_metrics.graceful_degradation_score:.1%}")
        
        # 性能指标
        print(f"\n⚡ 性能指标:")
        perf_metrics = report.performance_metrics
        print(f"  启动时间评分: {perf_metrics.startup_time_score:.1%}")
        print(f"  内存效率评分: {perf_metrics.memory_efficiency_score:.1%}")
        print(f"  CPU效率评分: {perf_metrics.cpu_efficiency_score:.1%}")
        print(f"  I/O效率评分: {perf_metrics.io_efficiency_score:.1%}")
        print(f"  算法复杂度评分: {perf_metrics.algorithm_complexity_score:.1%}")
        print(f"  缓存策略评分: {perf_metrics.caching_strategy_score:.1%}")
        print(f"  异步编程评分: {perf_metrics.async_programming_score:.1%}")
        
        # 架构优势
        if report.architecture_strengths:
            print(f"\n💪 架构优势:")
            for strength in report.architecture_strengths:
                print(f"  ✅ {strength}")
        
        # 架构弱点
        if report.architecture_weaknesses:
            print(f"\n⚠️ 架构弱点:")
            for weakness in report.architecture_weaknesses:
                print(f"  ❌ {weakness}")
        
        # 性能瓶颈
        if report.performance_bottlenecks:
            print(f"\n🚨 性能瓶颈:")
            for bottleneck in report.performance_bottlenecks:
                print(f"  🔥 {bottleneck}")
        
        # 立即行动建议
        if report.immediate_actions:
            print(f"\n🚨 立即行动建议:")
            for action in report.immediate_actions:
                print(f"  🔥 {action}")
        
        # 短期改进建议
        if report.short_term_improvements:
            print(f"\n📅 短期改进建议:")
            for improvement in report.short_term_improvements:
                print(f"  ⚡ {improvement}")
        
        # 长期优化建议
        if report.long_term_optimizations:
            print(f"\n🎯 长期优化建议:")
            for optimization in report.long_term_optimizations:
                print(f"  🚀 {optimization}")
        
        # 生成HTML报告
        print(f"\n📄 生成HTML报告...")
        html_content = assessor.generate_html_report(report)
        
        # 保存HTML报告
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_filename = f"technical_architecture_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path = reports_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML报告已保存: {report_path}")
        
        # 生成JSON报告
        import json
        json_filename = f"technical_architecture_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_path = reports_dir / json_filename
        
        # 准备JSON数据
        json_data = {
            "analysis_date": report.analysis_date.isoformat(),
            "overall_assessment": {
                "overall_architecture_score": report.overall_architecture_score,
                "overall_architecture_quality": report.overall_architecture_quality.value
            },
            "four_dimensions": {
                "code_structure_quality": report.code_structure_quality.value,
                "extensibility_quality": report.extensibility_quality.value,
                "stability_quality": report.stability_quality.value,
                "performance_quality": report.performance_quality.value
            },
            "code_structure_metrics": {
                "total_files": metrics.total_files,
                "total_lines": metrics.total_lines,
                "total_classes": metrics.total_classes,
                "total_functions": metrics.total_functions,
                "average_file_size": metrics.average_file_size,
                "documentation_coverage": metrics.documentation_coverage,
                "type_annotation_coverage": metrics.type_annotation_coverage,
                "code_duplication_rate": metrics.code_duplication_rate
            },
            "extensibility_metrics": {
                "interface_abstraction_score": ext_metrics.interface_abstraction_score,
                "plugin_architecture_score": ext_metrics.plugin_architecture_score,
                "configuration_flexibility_score": ext_metrics.configuration_flexibility_score,
                "api_design_score": ext_metrics.api_design_score,
                "dependency_injection_score": ext_metrics.dependency_injection_score,
                "modular_design_score": ext_metrics.modular_design_score
            },
            "stability_metrics": {
                "error_handling_coverage": stab_metrics.error_handling_coverage,
                "exception_safety_score": stab_metrics.exception_safety_score,
                "resource_management_score": stab_metrics.resource_management_score,
                "thread_safety_score": stab_metrics.thread_safety_score,
                "memory_safety_score": stab_metrics.memory_safety_score,
                "graceful_degradation_score": stab_metrics.graceful_degradation_score
            },
            "performance_metrics": {
                "startup_time_score": perf_metrics.startup_time_score,
                "memory_efficiency_score": perf_metrics.memory_efficiency_score,
                "cpu_efficiency_score": perf_metrics.cpu_efficiency_score,
                "io_efficiency_score": perf_metrics.io_efficiency_score,
                "algorithm_complexity_score": perf_metrics.algorithm_complexity_score,
                "caching_strategy_score": perf_metrics.caching_strategy_score,
                "async_programming_score": perf_metrics.async_programming_score
            },
            "key_findings": {
                "architecture_strengths": report.architecture_strengths,
                "architecture_weaknesses": report.architecture_weaknesses,
                "performance_bottlenecks": report.performance_bottlenecks,
                "scalability_concerns": report.scalability_concerns,
                "security_issues": report.security_issues
            },
            "recommendations": {
                "immediate_actions": report.immediate_actions,
                "short_term_improvements": report.short_term_improvements,
                "long_term_optimizations": report.long_term_optimizations
            }
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON报告已保存: {json_path}")
        
        # 总结
        print("\n" + "=" * 80)
        print("🎉 技术架构评估完成！")
        print(f"🏗️ 总体架构评分: {report.overall_architecture_score:.1%} ({report.overall_architecture_quality.value})")
        
        if report.overall_architecture_score >= 0.8:
            print("✅ 技术架构优秀，具备企业级软件开发标准")
        elif report.overall_architecture_score >= 0.6:
            print("⚠️ 技术架构良好，但仍有优化空间")
        elif report.overall_architecture_score >= 0.4:
            print("🔶 技术架构一般，需要重点改进关键问题")
        else:
            print("🔴 技术架构需要大幅改进")
        
        print(f"📄 详细报告: {report_path}")
        print(f"📊 数据报告: {json_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"技术架构评估失败: {e}")
        print(f"❌ 评估失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
