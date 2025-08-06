"""
AI Animation Studio - 整体实现度分析系统
评估基础框架完整度、核心创新功能、专业软件标准、可用性状态
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from core.logger import get_logger

logger = get_logger("overall_implementation_analysis")


class ImplementationLevel(Enum):
    """实现级别枚举"""
    NOT_IMPLEMENTED = "not_implemented"     # 未实现
    BASIC_FRAMEWORK = "basic_framework"     # 基础框架
    PARTIAL_IMPLEMENTATION = "partial"      # 部分实现
    MOSTLY_IMPLEMENTED = "mostly"           # 大部分实现
    FULLY_IMPLEMENTED = "fully"             # 完全实现
    ENHANCED = "enhanced"                   # 增强实现


class QualityLevel(Enum):
    """质量级别枚举"""
    POOR = "poor"                          # 差
    BASIC = "basic"                        # 基础
    GOOD = "good"                          # 良好
    EXCELLENT = "excellent"                # 优秀
    PROFESSIONAL = "professional"          # 专业级


@dataclass
class ComponentAnalysis:
    """组件分析结果"""
    component_name: str
    implementation_level: ImplementationLevel
    quality_level: QualityLevel
    completeness_score: float = 0.0
    functionality_score: float = 0.0
    code_quality_score: float = 0.0
    user_experience_score: float = 0.0
    professional_standard_score: float = 0.0
    issues: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class OverallImplementationReport:
    """整体实现度报告"""
    analysis_date: datetime = field(default_factory=datetime.now)
    
    # 四大评估维度
    basic_framework_completeness: float = 0.0
    core_innovation_implementation: float = 0.0
    professional_software_standards: float = 0.0
    usability_status: float = 0.0
    
    # 详细分析
    component_analyses: Dict[str, ComponentAnalysis] = field(default_factory=dict)
    
    # 技术架构评估
    code_structure_score: float = 0.0
    extensibility_score: float = 0.0
    stability_score: float = 0.0
    performance_score: float = 0.0
    
    # 用户界面评估
    visual_design_score: float = 0.0
    interaction_design_score: float = 0.0
    accessibility_score: float = 0.0
    adaptability_score: float = 0.0
    
    # 工作流程评估
    basic_workflow_score: float = 0.0
    core_innovation_workflow_score: float = 0.0
    efficiency_optimization_score: float = 0.0
    professional_features_score: float = 0.0
    
    # 综合评分
    overall_score: float = 0.0
    overall_level: QualityLevel = QualityLevel.BASIC
    
    # 关键发现
    critical_issues: List[str] = field(default_factory=list)
    major_strengths: List[str] = field(default_factory=list)
    priority_recommendations: List[str] = field(default_factory=list)


class OverallImplementationAnalyzer:
    """整体实现度分析器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.analysis_results = {}
        
        # 核心组件定义
        self.core_components = {
            "基础框架": [
                "main_window.py",
                "data_structures.py", 
                "project_manager.py",
                "theme_manager.py"
            ],
            "核心创新功能": [
                "perfect_state_transition_system.py",
                "narration_driven_system.py",
                "intelligent_path_system.py",
                "intelligent_rule_matching_system.py"
            ],
            "专业软件功能": [
                "enhanced_multi_solution_system.py",
                "advanced_template_system.py",
                "intelligent_adaptation_system.py",
                "natural_language_animation_system.py"
            ],
            "用户界面系统": [
                "dual_mode_layout_manager.py",
                "progressive_disclosure_manager.py",
                "adaptive_interface_manager.py",
                "modern_main_window.py"
            ]
        }
        
        logger.info("整体实现度分析器初始化完成")
    
    def analyze_overall_implementation(self) -> OverallImplementationReport:
        """分析整体实现度"""
        try:
            logger.info("开始整体实现度分析")
            
            report = OverallImplementationReport()
            
            # 分析各个组件
            self.analyze_components(report)
            
            # 评估四大维度
            self.evaluate_four_dimensions(report)
            
            # 评估技术架构
            self.evaluate_technical_architecture(report)
            
            # 评估用户界面
            self.evaluate_user_interface(report)
            
            # 评估工作流程
            self.evaluate_workflow(report)
            
            # 计算综合评分
            self.calculate_overall_score(report)
            
            # 生成关键发现
            self.generate_key_findings(report)
            
            logger.info("整体实现度分析完成")
            return report
            
        except Exception as e:
            logger.error(f"整体实现度分析失败: {e}")
            return OverallImplementationReport()
    
    def analyze_components(self, report: OverallImplementationReport):
        """分析各个组件"""
        try:
            for category, components in self.core_components.items():
                for component in components:
                    analysis = self.analyze_single_component(component, category)
                    report.component_analyses[component] = analysis
            
        except Exception as e:
            logger.error(f"组件分析失败: {e}")
    
    def analyze_single_component(self, component_file: str, category: str) -> ComponentAnalysis:
        """分析单个组件"""
        try:
            # 查找文件
            file_path = self.find_component_file(component_file)
            
            analysis = ComponentAnalysis(
                component_name=component_file,
                implementation_level=ImplementationLevel.NOT_IMPLEMENTED,
                quality_level=QualityLevel.POOR
            )
            
            if not file_path or not file_path.exists():
                analysis.issues.append("文件不存在")
                return analysis
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分析实现级别
            analysis.implementation_level = self.determine_implementation_level(content, component_file)
            
            # 分析质量级别
            analysis.quality_level = self.determine_quality_level(content, component_file)
            
            # 计算各项分数
            analysis.completeness_score = self.calculate_completeness_score(content, component_file)
            analysis.functionality_score = self.calculate_functionality_score(content, component_file)
            analysis.code_quality_score = self.calculate_code_quality_score(content, component_file)
            analysis.user_experience_score = self.calculate_user_experience_score(content, component_file)
            analysis.professional_standard_score = self.calculate_professional_standard_score(content, component_file)
            
            # 识别问题和优势
            analysis.issues = self.identify_component_issues(content, component_file)
            analysis.strengths = self.identify_component_strengths(content, component_file)
            analysis.recommendations = self.generate_component_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"分析组件失败 {component_file}: {e}")
            return ComponentAnalysis(
                component_name=component_file,
                implementation_level=ImplementationLevel.NOT_IMPLEMENTED,
                quality_level=QualityLevel.POOR,
                issues=[f"分析失败: {str(e)}"]
            )
    
    def find_component_file(self, component_file: str) -> Optional[Path]:
        """查找组件文件"""
        try:
            # 在多个目录中搜索
            search_dirs = [
                self.project_root / "ui",
                self.project_root / "core", 
                self.project_root / "analysis",
                self.project_root
            ]
            
            for search_dir in search_dirs:
                if search_dir.exists():
                    file_path = search_dir / component_file
                    if file_path.exists():
                        return file_path
                    
                    # 递归搜索子目录
                    for sub_file in search_dir.rglob(component_file):
                        return sub_file
            
            return None
            
        except Exception as e:
            logger.error(f"查找组件文件失败 {component_file}: {e}")
            return None
    
    def determine_implementation_level(self, content: str, component_file: str) -> ImplementationLevel:
        """确定实现级别"""
        try:
            if not content.strip():
                return ImplementationLevel.NOT_IMPLEMENTED
            
            # 基于文件内容判断实现级别
            class_count = content.count("class ")
            function_count = content.count("def ")
            import_count = content.count("import ")
            
            if class_count == 0 and function_count < 3:
                return ImplementationLevel.BASIC_FRAMEWORK
            elif class_count < 3 and function_count < 10:
                return ImplementationLevel.PARTIAL_IMPLEMENTATION
            elif class_count < 5 and function_count < 20:
                return ImplementationLevel.MOSTLY_IMPLEMENTED
            elif "logger" in content and "try:" in content and "except:" in content:
                return ImplementationLevel.ENHANCED
            else:
                return ImplementationLevel.FULLY_IMPLEMENTED
                
        except Exception as e:
            logger.error(f"确定实现级别失败: {e}")
            return ImplementationLevel.NOT_IMPLEMENTED
    
    def determine_quality_level(self, content: str, component_file: str) -> QualityLevel:
        """确定质量级别"""
        try:
            quality_indicators = {
                "docstring": '"""' in content,
                "type_hints": ": str" in content or ": int" in content or ": float" in content,
                "error_handling": "try:" in content and "except:" in content,
                "logging": "logger" in content,
                "dataclass": "@dataclass" in content,
                "enum": "Enum" in content,
                "comments": "#" in content,
                "proper_imports": "from typing import" in content
            }
            
            quality_score = sum(quality_indicators.values()) / len(quality_indicators)
            
            if quality_score >= 0.8:
                return QualityLevel.PROFESSIONAL
            elif quality_score >= 0.6:
                return QualityLevel.EXCELLENT
            elif quality_score >= 0.4:
                return QualityLevel.GOOD
            elif quality_score >= 0.2:
                return QualityLevel.BASIC
            else:
                return QualityLevel.POOR
                
        except Exception as e:
            logger.error(f"确定质量级别失败: {e}")
            return QualityLevel.POOR
    
    def calculate_completeness_score(self, content: str, component_file: str) -> float:
        """计算完整度分数"""
        try:
            # 基于文件大小和内容复杂度
            lines = len(content.split('\n'))
            if lines < 50:
                return 0.3
            elif lines < 200:
                return 0.6
            elif lines < 500:
                return 0.8
            else:
                return 1.0
                
        except Exception as e:
            logger.error(f"计算完整度分数失败: {e}")
            return 0.0
    
    def calculate_functionality_score(self, content: str, component_file: str) -> float:
        """计算功能性分数"""
        try:
            # 基于方法数量和复杂度
            method_count = content.count("def ")
            class_count = content.count("class ")
            
            functionality_score = min(1.0, (method_count * 0.05 + class_count * 0.1))
            return functionality_score
            
        except Exception as e:
            logger.error(f"计算功能性分数失败: {e}")
            return 0.0
    
    def calculate_code_quality_score(self, content: str, component_file: str) -> float:
        """计算代码质量分数"""
        try:
            quality_factors = {
                "has_docstrings": '"""' in content,
                "has_type_hints": ": str" in content or ": int" in content,
                "has_error_handling": "try:" in content and "except:" in content,
                "has_logging": "logger" in content,
                "has_proper_structure": "class " in content and "def " in content,
                "has_imports": "import " in content,
                "has_comments": "#" in content
            }
            
            return sum(quality_factors.values()) / len(quality_factors)
            
        except Exception as e:
            logger.error(f"计算代码质量分数失败: {e}")
            return 0.0
    
    def calculate_user_experience_score(self, content: str, component_file: str) -> float:
        """计算用户体验分数"""
        try:
            ux_indicators = {
                "has_ui_components": "QWidget" in content or "QMainWindow" in content,
                "has_signals": "pyqtSignal" in content,
                "has_styling": "setStyleSheet" in content,
                "has_layouts": "Layout" in content,
                "has_user_feedback": "QMessageBox" in content or "status" in content.lower(),
                "has_progress_indication": "QProgressBar" in content or "progress" in content.lower()
            }
            
            return sum(ux_indicators.values()) / len(ux_indicators)
            
        except Exception as e:
            logger.error(f"计算用户体验分数失败: {e}")
            return 0.0
    
    def calculate_professional_standard_score(self, content: str, component_file: str) -> float:
        """计算专业软件标准分数"""
        try:
            professional_indicators = {
                "has_comprehensive_docstrings": content.count('"""') >= 3,
                "has_type_annotations": content.count(": ") >= 5,
                "has_error_handling": content.count("except") >= 2,
                "has_logging": "logger" in content,
                "has_data_validation": "validate" in content.lower(),
                "has_configuration": "config" in content.lower(),
                "has_testing_support": "test" in content.lower(),
                "has_modular_design": content.count("class ") >= 2
            }
            
            return sum(professional_indicators.values()) / len(professional_indicators)
            
        except Exception as e:
            logger.error(f"计算专业软件标准分数失败: {e}")
            return 0.0
    
    def identify_component_issues(self, content: str, component_file: str) -> List[str]:
        """识别组件问题"""
        issues = []
        
        try:
            if '"""' not in content:
                issues.append("缺少文档字符串")
            
            if "try:" not in content or "except:" not in content:
                issues.append("缺少错误处理")
            
            if "logger" not in content:
                issues.append("缺少日志记录")
            
            if ": str" not in content and ": int" not in content:
                issues.append("缺少类型注解")
            
            if len(content.split('\n')) < 50:
                issues.append("实现过于简单")
            
            return issues
            
        except Exception as e:
            logger.error(f"识别组件问题失败: {e}")
            return ["分析失败"]
    
    def identify_component_strengths(self, content: str, component_file: str) -> List[str]:
        """识别组件优势"""
        strengths = []
        
        try:
            if '"""' in content:
                strengths.append("有完整的文档字符串")
            
            if "try:" in content and "except:" in content:
                strengths.append("有错误处理机制")
            
            if "logger" in content:
                strengths.append("有日志记录功能")
            
            if "@dataclass" in content:
                strengths.append("使用现代Python特性")
            
            if "pyqtSignal" in content:
                strengths.append("有信号机制")
            
            if len(content.split('\n')) > 200:
                strengths.append("实现较为完整")
            
            return strengths
            
        except Exception as e:
            logger.error(f"识别组件优势失败: {e}")
            return []
    
    def generate_component_recommendations(self, analysis: ComponentAnalysis) -> List[str]:
        """生成组件建议"""
        recommendations = []
        
        try:
            if analysis.code_quality_score < 0.5:
                recommendations.append("改进代码质量，添加文档和类型注解")
            
            if analysis.functionality_score < 0.5:
                recommendations.append("增加功能实现，提升组件完整度")
            
            if analysis.user_experience_score < 0.5:
                recommendations.append("改善用户体验，添加反馈机制")
            
            if analysis.professional_standard_score < 0.5:
                recommendations.append("提升专业标准，完善错误处理和配置")
            
            if analysis.implementation_level == ImplementationLevel.NOT_IMPLEMENTED:
                recommendations.append("立即实现基础功能")
            elif analysis.implementation_level == ImplementationLevel.BASIC_FRAMEWORK:
                recommendations.append("扩展功能实现")
            
            return recommendations

        except Exception as e:
            logger.error(f"生成组件建议失败: {e}")
            return ["需要进一步分析"]

    def evaluate_four_dimensions(self, report: OverallImplementationReport):
        """评估四大维度"""
        try:
            # 1. 基础框架完整度
            framework_components = [
                analysis for name, analysis in report.component_analyses.items()
                if any(comp in name for comp in self.core_components["基础框架"])
            ]

            if framework_components:
                report.basic_framework_completeness = sum(
                    analysis.completeness_score for analysis in framework_components
                ) / len(framework_components)

            # 2. 核心创新功能实现
            innovation_components = [
                analysis for name, analysis in report.component_analyses.items()
                if any(comp in name for comp in self.core_components["核心创新功能"])
            ]

            if innovation_components:
                report.core_innovation_implementation = sum(
                    analysis.functionality_score for analysis in innovation_components
                ) / len(innovation_components)

            # 3. 专业软件标准
            professional_components = [
                analysis for name, analysis in report.component_analyses.items()
                if any(comp in name for comp in self.core_components["专业软件功能"])
            ]

            if professional_components:
                report.professional_software_standards = sum(
                    analysis.professional_standard_score for analysis in professional_components
                ) / len(professional_components)

            # 4. 可用性状态
            ui_components = [
                analysis for name, analysis in report.component_analyses.items()
                if any(comp in name for comp in self.core_components["用户界面系统"])
            ]

            if ui_components:
                report.usability_status = sum(
                    analysis.user_experience_score for analysis in ui_components
                ) / len(ui_components)

        except Exception as e:
            logger.error(f"评估四大维度失败: {e}")

    def evaluate_technical_architecture(self, report: OverallImplementationReport):
        """评估技术架构"""
        try:
            all_analyses = list(report.component_analyses.values())

            if all_analyses:
                # 代码结构分数
                report.code_structure_score = sum(
                    analysis.code_quality_score for analysis in all_analyses
                ) / len(all_analyses)

                # 扩展性分数
                report.extensibility_score = sum(
                    1.0 if analysis.implementation_level in [
                        ImplementationLevel.FULLY_IMPLEMENTED,
                        ImplementationLevel.ENHANCED
                    ] else 0.5 for analysis in all_analyses
                ) / len(all_analyses)

                # 稳定性分数
                report.stability_score = sum(
                    1.0 if "错误处理" not in analysis.issues else 0.3
                    for analysis in all_analyses
                ) / len(all_analyses)

                # 性能分数
                report.performance_score = sum(
                    analysis.functionality_score for analysis in all_analyses
                ) / len(all_analyses)

        except Exception as e:
            logger.error(f"评估技术架构失败: {e}")

    def evaluate_user_interface(self, report: OverallImplementationReport):
        """评估用户界面"""
        try:
            ui_analyses = [
                analysis for name, analysis in report.component_analyses.items()
                if "ui" in name.lower() or "window" in name.lower() or "widget" in name.lower()
            ]

            if ui_analyses:
                # 视觉设计分数
                report.visual_design_score = sum(
                    analysis.user_experience_score for analysis in ui_analyses
                ) / len(ui_analyses)

                # 交互设计分数
                report.interaction_design_score = sum(
                    1.0 if "pyqtSignal" in str(analysis.strengths) else 0.5
                    for analysis in ui_analyses
                ) / len(ui_analyses)

                # 可访问性分数
                report.accessibility_score = sum(
                    analysis.professional_standard_score for analysis in ui_analyses
                ) / len(ui_analyses)

                # 适应性分数
                report.adaptability_score = sum(
                    1.0 if analysis.implementation_level == ImplementationLevel.ENHANCED else 0.6
                    for analysis in ui_analyses
                ) / len(ui_analyses)

        except Exception as e:
            logger.error(f"评估用户界面失败: {e}")

    def evaluate_workflow(self, report: OverallImplementationReport):
        """评估工作流程"""
        try:
            # 基础工作流程分数
            basic_workflow_components = ["main_window.py", "project_manager.py"]
            basic_analyses = [
                analysis for name, analysis in report.component_analyses.items()
                if any(comp in name for comp in basic_workflow_components)
            ]

            if basic_analyses:
                report.basic_workflow_score = sum(
                    analysis.functionality_score for analysis in basic_analyses
                ) / len(basic_analyses)

            # 核心创新工作流程分数
            innovation_workflow_components = [
                "perfect_state_transition_system.py",
                "narration_driven_system.py"
            ]
            innovation_analyses = [
                analysis for name, analysis in report.component_analyses.items()
                if any(comp in name for comp in innovation_workflow_components)
            ]

            if innovation_analyses:
                report.core_innovation_workflow_score = sum(
                    analysis.functionality_score for analysis in innovation_analyses
                ) / len(innovation_analyses)

            # 效率优化分数
            efficiency_components = [
                "intelligent_adaptation_system.py",
                "progressive_disclosure_manager.py"
            ]
            efficiency_analyses = [
                analysis for name, analysis in report.component_analyses.items()
                if any(comp in name for comp in efficiency_components)
            ]

            if efficiency_analyses:
                report.efficiency_optimization_score = sum(
                    analysis.functionality_score for analysis in efficiency_analyses
                ) / len(efficiency_analyses)

            # 专业功能分数
            professional_workflow_components = [
                "enhanced_multi_solution_system.py",
                "advanced_template_system.py"
            ]
            professional_analyses = [
                analysis for name, analysis in report.component_analyses.items()
                if any(comp in name for comp in professional_workflow_components)
            ]

            if professional_analyses:
                report.professional_features_score = sum(
                    analysis.functionality_score for analysis in professional_analyses
                ) / len(professional_analyses)

        except Exception as e:
            logger.error(f"评估工作流程失败: {e}")

    def calculate_overall_score(self, report: OverallImplementationReport):
        """计算综合评分"""
        try:
            # 四大维度权重
            dimension_weights = {
                "basic_framework": 0.25,
                "core_innovation": 0.30,
                "professional_standards": 0.25,
                "usability": 0.20
            }

            # 计算加权平均分
            weighted_score = (
                report.basic_framework_completeness * dimension_weights["basic_framework"] +
                report.core_innovation_implementation * dimension_weights["core_innovation"] +
                report.professional_software_standards * dimension_weights["professional_standards"] +
                report.usability_status * dimension_weights["usability"]
            )

            report.overall_score = weighted_score

            # 确定整体质量级别
            if weighted_score >= 0.9:
                report.overall_level = QualityLevel.PROFESSIONAL
            elif weighted_score >= 0.75:
                report.overall_level = QualityLevel.EXCELLENT
            elif weighted_score >= 0.6:
                report.overall_level = QualityLevel.GOOD
            elif weighted_score >= 0.4:
                report.overall_level = QualityLevel.BASIC
            else:
                report.overall_level = QualityLevel.POOR

        except Exception as e:
            logger.error(f"计算综合评分失败: {e}")

    def generate_key_findings(self, report: OverallImplementationReport):
        """生成关键发现"""
        try:
            # 关键问题
            if report.basic_framework_completeness < 0.7:
                report.critical_issues.append("基础框架完整度不足，影响系统稳定性")

            if report.core_innovation_implementation < 0.5:
                report.critical_issues.append("核心创新功能实现严重不足，缺乏竞争优势")

            if report.professional_software_standards < 0.6:
                report.critical_issues.append("专业软件标准不达标，影响商业化可行性")

            if report.usability_status < 0.5:
                report.critical_issues.append("可用性问题严重，用户体验需要大幅改善")

            # 主要优势
            if report.basic_framework_completeness >= 0.8:
                report.major_strengths.append("基础框架完整，为功能扩展提供良好基础")

            if report.code_structure_score >= 0.7:
                report.major_strengths.append("代码结构良好，具备良好的可维护性")

            if report.extensibility_score >= 0.7:
                report.major_strengths.append("系统扩展性强，支持功能模块化开发")

            # 优先级建议
            if report.core_innovation_implementation < 0.3:
                report.priority_recommendations.append("立即实现完美状态衔接和旁白驱动制作系统")

            if report.stability_score < 0.6:
                report.priority_recommendations.append("优先修复稳定性问题，完善错误处理机制")

            if report.usability_status < 0.5:
                report.priority_recommendations.append("改善用户界面设计，提升用户体验")

            if report.professional_software_standards < 0.5:
                report.priority_recommendations.append("提升代码质量，完善文档和测试")

        except Exception as e:
            logger.error(f"生成关键发现失败: {e}")

    def generate_html_report(self, report: OverallImplementationReport) -> str:
        """生成HTML报告"""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>AI Animation Studio - 整体实现度分析报告</title>
                <style>
                    body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 20px; }}
                    .header {{ text-align: center; color: #2c3e50; }}
                    .dimension {{ margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; background: #f8f9fa; }}
                    .score {{ font-size: 24px; font-weight: bold; color: #e74c3c; }}
                    .good {{ color: #27ae60; }}
                    .warning {{ color: #f39c12; }}
                    .critical {{ color: #e74c3c; }}
                    .component {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                    .issues {{ color: #e74c3c; }}
                    .strengths {{ color: #27ae60; }}
                    .recommendations {{ color: #3498db; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🎯 AI Animation Studio 整体实现度分析报告</h1>
                    <p>分析时间: {report.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>

                <div class="dimension">
                    <h2>📊 四大维度评估</h2>
                    <p><strong>基础框架完整度:</strong> <span class="score {'good' if report.basic_framework_completeness >= 0.7 else 'warning' if report.basic_framework_completeness >= 0.5 else 'critical'}">{report.basic_framework_completeness:.1%}</span></p>
                    <p><strong>核心创新功能:</strong> <span class="score {'good' if report.core_innovation_implementation >= 0.7 else 'warning' if report.core_innovation_implementation >= 0.5 else 'critical'}">{report.core_innovation_implementation:.1%}</span></p>
                    <p><strong>专业软件标准:</strong> <span class="score {'good' if report.professional_software_standards >= 0.7 else 'warning' if report.professional_software_standards >= 0.5 else 'critical'}">{report.professional_software_standards:.1%}</span></p>
                    <p><strong>可用性状态:</strong> <span class="score {'good' if report.usability_status >= 0.7 else 'warning' if report.usability_status >= 0.5 else 'critical'}">{report.usability_status:.1%}</span></p>
                </div>

                <div class="dimension">
                    <h2>🏗️ 技术架构评估</h2>
                    <p><strong>代码结构:</strong> {report.code_structure_score:.1%}</p>
                    <p><strong>扩展性:</strong> {report.extensibility_score:.1%}</p>
                    <p><strong>稳定性:</strong> {report.stability_score:.1%}</p>
                    <p><strong>性能:</strong> {report.performance_score:.1%}</p>
                </div>

                <div class="dimension">
                    <h2>🎨 用户界面评估</h2>
                    <p><strong>视觉设计:</strong> {report.visual_design_score:.1%}</p>
                    <p><strong>交互设计:</strong> {report.interaction_design_score:.1%}</p>
                    <p><strong>可访问性:</strong> {report.accessibility_score:.1%}</p>
                    <p><strong>适应性:</strong> {report.adaptability_score:.1%}</p>
                </div>

                <div class="dimension">
                    <h2>🔄 工作流程评估</h2>
                    <p><strong>基础工作流程:</strong> {report.basic_workflow_score:.1%}</p>
                    <p><strong>核心创新工作流程:</strong> {report.core_innovation_workflow_score:.1%}</p>
                    <p><strong>效率优化:</strong> {report.efficiency_optimization_score:.1%}</p>
                    <p><strong>专业功能:</strong> {report.professional_features_score:.1%}</p>
                </div>

                <div class="dimension">
                    <h2>🎯 综合评估</h2>
                    <p><strong>总体评分:</strong> <span class="score {'good' if report.overall_score >= 0.7 else 'warning' if report.overall_score >= 0.5 else 'critical'}">{report.overall_score:.1%}</span></p>
                    <p><strong>质量级别:</strong> {report.overall_level.value}</p>
                </div>

                <div class="dimension">
                    <h2>🚨 关键问题</h2>
                    <ul class="issues">
            """

            for issue in report.critical_issues:
                html += f"<li>{issue}</li>"

            html += """
                    </ul>
                </div>

                <div class="dimension">
                    <h2>💪 主要优势</h2>
                    <ul class="strengths">
            """

            for strength in report.major_strengths:
                html += f"<li>{strength}</li>"

            html += """
                    </ul>
                </div>

                <div class="dimension">
                    <h2>🎯 优先级建议</h2>
                    <ul class="recommendations">
            """

            for recommendation in report.priority_recommendations:
                html += f"<li>{recommendation}</li>"

            html += """
                    </ul>
                </div>

                <div class="dimension">
                    <h2>📋 组件详细分析</h2>
            """

            for component_name, analysis in report.component_analyses.items():
                html += f"""
                    <div class="component">
                        <h3>{component_name}</h3>
                        <p><strong>实现级别:</strong> {analysis.implementation_level.value}</p>
                        <p><strong>质量级别:</strong> {analysis.quality_level.value}</p>
                        <p><strong>完整度:</strong> {analysis.completeness_score:.1%}</p>
                        <p><strong>功能性:</strong> {analysis.functionality_score:.1%}</p>
                        <p><strong>代码质量:</strong> {analysis.code_quality_score:.1%}</p>
                """

                if analysis.issues:
                    html += "<p><strong>问题:</strong></p><ul class='issues'>"
                    for issue in analysis.issues:
                        html += f"<li>{issue}</li>"
                    html += "</ul>"

                if analysis.strengths:
                    html += "<p><strong>优势:</strong></p><ul class='strengths'>"
                    for strength in analysis.strengths:
                        html += f"<li>{strength}</li>"
                    html += "</ul>"

                if analysis.recommendations:
                    html += "<p><strong>建议:</strong></p><ul class='recommendations'>"
                    for recommendation in analysis.recommendations:
                        html += f"<li>{recommendation}</li>"
                    html += "</ul>"

                html += "</div>"

            html += """
                </div>
            </body>
            </html>
            """

            return html

        except Exception as e:
            logger.error(f"生成HTML报告失败: {e}")
            return f"<html><body><h1>报告生成失败: {e}</h1></body></html>"
