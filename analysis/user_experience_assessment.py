"""
AI Animation Studio - 用户体验评估系统
评估界面设计、交互设计、视觉设计、适应性等方面
"""

import os
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from core.logger import get_logger

logger = get_logger("user_experience_assessment")


class UXQuality(Enum):
    """用户体验质量级别枚举"""
    POOR = "poor"                          # 差
    BASIC = "basic"                        # 基础
    GOOD = "good"                          # 良好
    EXCELLENT = "excellent"                # 优秀
    WORLD_CLASS = "world_class"            # 世界级


class DesignMaturity(Enum):
    """设计成熟度枚举"""
    PROTOTYPE = "prototype"                # 原型阶段
    BASIC_FUNCTIONAL = "basic_functional"  # 基础功能
    PROFESSIONAL = "professional"         # 专业级
    ENTERPRISE = "enterprise"              # 企业级
    INDUSTRY_LEADING = "industry_leading"  # 行业领先


@dataclass
class InterfaceDesignMetrics:
    """界面设计指标"""
    layout_consistency_score: float = 0.0
    information_architecture_score: float = 0.0
    navigation_clarity_score: float = 0.0
    content_organization_score: float = 0.0
    responsive_design_score: float = 0.0
    accessibility_compliance_score: float = 0.0


@dataclass
class InteractionDesignMetrics:
    """交互设计指标"""
    user_control_score: float = 0.0
    feedback_quality_score: float = 0.0
    error_prevention_score: float = 0.0
    task_efficiency_score: float = 0.0
    learning_curve_score: float = 0.0
    workflow_optimization_score: float = 0.0


@dataclass
class VisualDesignMetrics:
    """视觉设计指标"""
    color_system_score: float = 0.0
    typography_score: float = 0.0
    iconography_score: float = 0.0
    visual_hierarchy_score: float = 0.0
    brand_consistency_score: float = 0.0
    aesthetic_appeal_score: float = 0.0


@dataclass
class AdaptabilityMetrics:
    """适应性指标"""
    personalization_score: float = 0.0
    customization_score: float = 0.0
    context_awareness_score: float = 0.0
    multi_device_support_score: float = 0.0
    internationalization_score: float = 0.0
    scalability_score: float = 0.0


@dataclass
class UsabilityMetrics:
    """可用性指标"""
    learnability_score: float = 0.0
    efficiency_score: float = 0.0
    memorability_score: float = 0.0
    error_tolerance_score: float = 0.0
    satisfaction_score: float = 0.0
    task_completion_rate: float = 0.0


@dataclass
class UserExperienceReport:
    """用户体验评估报告"""
    analysis_date: datetime = field(default_factory=datetime.now)
    
    # 五大评估维度
    interface_design_quality: UXQuality = UXQuality.BASIC
    interaction_design_quality: UXQuality = UXQuality.BASIC
    visual_design_quality: UXQuality = UXQuality.BASIC
    adaptability_quality: UXQuality = UXQuality.BASIC
    usability_quality: UXQuality = UXQuality.BASIC
    
    # 详细指标
    interface_design_metrics: InterfaceDesignMetrics = field(default_factory=InterfaceDesignMetrics)
    interaction_design_metrics: InteractionDesignMetrics = field(default_factory=InteractionDesignMetrics)
    visual_design_metrics: VisualDesignMetrics = field(default_factory=VisualDesignMetrics)
    adaptability_metrics: AdaptabilityMetrics = field(default_factory=AdaptabilityMetrics)
    usability_metrics: UsabilityMetrics = field(default_factory=UsabilityMetrics)
    
    # 综合评估
    overall_ux_score: float = 0.0
    overall_ux_quality: UXQuality = UXQuality.BASIC
    design_maturity: DesignMaturity = DesignMaturity.BASIC_FUNCTIONAL
    
    # 关键发现
    ux_strengths: List[str] = field(default_factory=list)
    ux_weaknesses: List[str] = field(default_factory=list)
    usability_issues: List[str] = field(default_factory=list)
    accessibility_issues: List[str] = field(default_factory=list)
    design_inconsistencies: List[str] = field(default_factory=list)
    
    # 改进建议
    critical_ux_fixes: List[str] = field(default_factory=list)
    interface_improvements: List[str] = field(default_factory=list)
    interaction_enhancements: List[str] = field(default_factory=list)
    visual_refinements: List[str] = field(default_factory=list)
    adaptability_upgrades: List[str] = field(default_factory=list)


class UserExperienceAssessor:
    """用户体验评估器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ui_files = []
        self.style_files = []
        self.analysis_cache = {}
        
        # 扫描UI相关文件
        self.scan_ui_files()
        
        logger.info("用户体验评估器初始化完成")
    
    def scan_ui_files(self):
        """扫描UI相关文件"""
        try:
            # 扫描Python UI文件
            self.ui_files = list(self.project_root.rglob("*ui*.py")) + \
                           list(self.project_root.rglob("*widget*.py")) + \
                           list(self.project_root.rglob("*window*.py")) + \
                           list(self.project_root.rglob("*dialog*.py"))
            
            # 扫描样式文件
            self.style_files = list(self.project_root.rglob("*.css")) + \
                              list(self.project_root.rglob("*.qss"))
            
            logger.info(f"发现 {len(self.ui_files)} 个UI文件，{len(self.style_files)} 个样式文件")
            
        except Exception as e:
            logger.error(f"扫描UI文件失败: {e}")
    
    def assess_user_experience(self) -> UserExperienceReport:
        """评估用户体验"""
        try:
            logger.info("开始用户体验评估")
            
            report = UserExperienceReport()
            
            # 评估界面设计
            self.assess_interface_design(report)
            
            # 评估交互设计
            self.assess_interaction_design(report)
            
            # 评估视觉设计
            self.assess_visual_design(report)
            
            # 评估适应性
            self.assess_adaptability(report)
            
            # 评估可用性
            self.assess_usability(report)
            
            # 计算综合评分
            self.calculate_overall_ux_score(report)
            
            # 生成关键发现和建议
            self.generate_ux_findings_and_recommendations(report)
            
            logger.info("用户体验评估完成")
            return report
            
        except Exception as e:
            logger.error(f"用户体验评估失败: {e}")
            return UserExperienceReport()
    
    def assess_interface_design(self, report: UserExperienceReport):
        """评估界面设计"""
        try:
            metrics = report.interface_design_metrics
            
            # 布局一致性评分
            metrics.layout_consistency_score = self.evaluate_layout_consistency()
            
            # 信息架构评分
            metrics.information_architecture_score = self.evaluate_information_architecture()
            
            # 导航清晰度评分
            metrics.navigation_clarity_score = self.evaluate_navigation_clarity()
            
            # 内容组织评分
            metrics.content_organization_score = self.evaluate_content_organization()
            
            # 响应式设计评分
            metrics.responsive_design_score = self.evaluate_responsive_design()
            
            # 可访问性合规评分
            metrics.accessibility_compliance_score = self.evaluate_accessibility_compliance()
            
            # 计算综合界面设计质量
            interface_score = (
                metrics.layout_consistency_score * 0.2 +
                metrics.information_architecture_score * 0.2 +
                metrics.navigation_clarity_score * 0.15 +
                metrics.content_organization_score * 0.15 +
                metrics.responsive_design_score * 0.15 +
                metrics.accessibility_compliance_score * 0.15
            )
            
            report.interface_design_quality = self.score_to_ux_quality(interface_score)
            
        except Exception as e:
            logger.error(f"评估界面设计失败: {e}")
    
    def assess_interaction_design(self, report: UserExperienceReport):
        """评估交互设计"""
        try:
            metrics = report.interaction_design_metrics
            
            # 用户控制评分
            metrics.user_control_score = self.evaluate_user_control()
            
            # 反馈质量评分
            metrics.feedback_quality_score = self.evaluate_feedback_quality()
            
            # 错误预防评分
            metrics.error_prevention_score = self.evaluate_error_prevention()
            
            # 任务效率评分
            metrics.task_efficiency_score = self.evaluate_task_efficiency()
            
            # 学习曲线评分
            metrics.learning_curve_score = self.evaluate_learning_curve()
            
            # 工作流程优化评分
            metrics.workflow_optimization_score = self.evaluate_workflow_optimization()
            
            # 计算综合交互设计质量
            interaction_score = (
                metrics.user_control_score * 0.2 +
                metrics.feedback_quality_score * 0.2 +
                metrics.error_prevention_score * 0.15 +
                metrics.task_efficiency_score * 0.2 +
                metrics.learning_curve_score * 0.1 +
                metrics.workflow_optimization_score * 0.15
            )
            
            report.interaction_design_quality = self.score_to_ux_quality(interaction_score)
            
        except Exception as e:
            logger.error(f"评估交互设计失败: {e}")
    
    def assess_visual_design(self, report: UserExperienceReport):
        """评估视觉设计"""
        try:
            metrics = report.visual_design_metrics
            
            # 色彩系统评分
            metrics.color_system_score = self.evaluate_color_system()
            
            # 字体排版评分
            metrics.typography_score = self.evaluate_typography()
            
            # 图标系统评分
            metrics.iconography_score = self.evaluate_iconography()
            
            # 视觉层次评分
            metrics.visual_hierarchy_score = self.evaluate_visual_hierarchy()
            
            # 品牌一致性评分
            metrics.brand_consistency_score = self.evaluate_brand_consistency()
            
            # 美学吸引力评分
            metrics.aesthetic_appeal_score = self.evaluate_aesthetic_appeal()
            
            # 计算综合视觉设计质量
            visual_score = (
                metrics.color_system_score * 0.2 +
                metrics.typography_score * 0.15 +
                metrics.iconography_score * 0.15 +
                metrics.visual_hierarchy_score * 0.2 +
                metrics.brand_consistency_score * 0.15 +
                metrics.aesthetic_appeal_score * 0.15
            )
            
            report.visual_design_quality = self.score_to_ux_quality(visual_score)
            
        except Exception as e:
            logger.error(f"评估视觉设计失败: {e}")
    
    def assess_adaptability(self, report: UserExperienceReport):
        """评估适应性"""
        try:
            metrics = report.adaptability_metrics
            
            # 个性化评分
            metrics.personalization_score = self.evaluate_personalization()
            
            # 定制化评分
            metrics.customization_score = self.evaluate_customization()
            
            # 上下文感知评分
            metrics.context_awareness_score = self.evaluate_context_awareness()
            
            # 多设备支持评分
            metrics.multi_device_support_score = self.evaluate_multi_device_support()
            
            # 国际化评分
            metrics.internationalization_score = self.evaluate_internationalization()
            
            # 可扩展性评分
            metrics.scalability_score = self.evaluate_scalability()
            
            # 计算综合适应性质量
            adaptability_score = (
                metrics.personalization_score * 0.2 +
                metrics.customization_score * 0.2 +
                metrics.context_awareness_score * 0.15 +
                metrics.multi_device_support_score * 0.15 +
                metrics.internationalization_score * 0.15 +
                metrics.scalability_score * 0.15
            )
            
            report.adaptability_quality = self.score_to_ux_quality(adaptability_score)
            
        except Exception as e:
            logger.error(f"评估适应性失败: {e}")
    
    def assess_usability(self, report: UserExperienceReport):
        """评估可用性"""
        try:
            metrics = report.usability_metrics
            
            # 易学性评分
            metrics.learnability_score = self.evaluate_learnability()
            
            # 效率评分
            metrics.efficiency_score = self.evaluate_efficiency()
            
            # 易记性评分
            metrics.memorability_score = self.evaluate_memorability()
            
            # 错误容忍度评分
            metrics.error_tolerance_score = self.evaluate_error_tolerance()
            
            # 满意度评分
            metrics.satisfaction_score = self.evaluate_satisfaction()
            
            # 任务完成率评分
            metrics.task_completion_rate = self.evaluate_task_completion_rate()
            
            # 计算综合可用性质量
            usability_score = (
                metrics.learnability_score * 0.2 +
                metrics.efficiency_score * 0.2 +
                metrics.memorability_score * 0.15 +
                metrics.error_tolerance_score * 0.15 +
                metrics.satisfaction_score * 0.15 +
                metrics.task_completion_rate * 0.15
            )
            
            report.usability_quality = self.score_to_ux_quality(usability_score)
            
        except Exception as e:
            logger.error(f"评估可用性失败: {e}")

    def evaluate_layout_consistency(self) -> float:
        """评估布局一致性"""
        try:
            consistency_score = 0.0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查布局模式一致性
                    layout_patterns = [
                        'QVBoxLayout', 'QHBoxLayout', 'QGridLayout',
                        'QFormLayout', 'QStackedLayout'
                    ]

                    used_layouts = sum(1 for pattern in layout_patterns if pattern in content)
                    if used_layouts > 0:
                        consistency_score += min(1.0, used_layouts / 3)  # 适度使用布局

                    # 检查边距和间距一致性
                    if 'setContentsMargins' in content or 'setSpacing' in content:
                        consistency_score += 0.2

                    # 检查组件对齐
                    if 'setAlignment' in content:
                        consistency_score += 0.1

                except Exception:
                    continue

            return min(1.0, consistency_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估布局一致性失败: {e}")
            return 0.0

    def evaluate_information_architecture(self) -> float:
        """评估信息架构"""
        try:
            architecture_score = 0.0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查层次结构
                    if 'QTabWidget' in content:
                        architecture_score += 0.3  # 标签页组织

                    if 'QTreeWidget' in content or 'QTreeView' in content:
                        architecture_score += 0.3  # 树形结构

                    if 'QGroupBox' in content:
                        architecture_score += 0.2  # 分组组织

                    if 'QSplitter' in content:
                        architecture_score += 0.2  # 分割面板

                except Exception:
                    continue

            return min(1.0, architecture_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估信息架构失败: {e}")
            return 0.0

    def evaluate_navigation_clarity(self) -> float:
        """评估导航清晰度"""
        try:
            navigation_score = 0.0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查导航元素
                    if 'QMenuBar' in content or 'createMenuBar' in content:
                        navigation_score += 0.4  # 菜单栏

                    if 'QToolBar' in content or 'addToolBar' in content:
                        navigation_score += 0.3  # 工具栏

                    if 'QStatusBar' in content or 'statusBar' in content:
                        navigation_score += 0.2  # 状态栏

                    if 'QPushButton' in content and 'clicked.connect' in content:
                        navigation_score += 0.1  # 按钮导航

                except Exception:
                    continue

            return min(1.0, navigation_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估导航清晰度失败: {e}")
            return 0.0

    def evaluate_content_organization(self) -> float:
        """评估内容组织"""
        try:
            organization_score = 0.0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查内容组织模式
                    if 'QScrollArea' in content:
                        organization_score += 0.2  # 滚动区域

                    if 'QListWidget' in content or 'QListView' in content:
                        organization_score += 0.3  # 列表组织

                    if 'QTableWidget' in content or 'QTableView' in content:
                        organization_score += 0.3  # 表格组织

                    if 'QLabel' in content and 'setText' in content:
                        organization_score += 0.2  # 标签说明

                except Exception:
                    continue

            return min(1.0, organization_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估内容组织失败: {e}")
            return 0.0

    def evaluate_responsive_design(self) -> float:
        """评估响应式设计"""
        try:
            responsive_score = 0.0

            # 检查响应式布局管理器
            responsive_files = [
                "responsive_layout_manager.py",
                "adaptive_interface_manager.py",
                "screen_adaptation_manager.py"
            ]

            for file_name in responsive_files:
                file_paths = list(self.project_root.rglob(file_name))
                if file_paths:
                    responsive_score += 0.3

            # 检查UI文件中的响应式特性
            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if 'resize' in content.lower() or 'sizeHint' in content:
                        responsive_score += 0.1

                except Exception:
                    continue

            return min(1.0, responsive_score)

        except Exception as e:
            logger.error(f"评估响应式设计失败: {e}")
            return 0.0

    def evaluate_accessibility_compliance(self) -> float:
        """评估可访问性合规"""
        try:
            accessibility_score = 0.0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查可访问性特性
                    if 'setToolTip' in content:
                        accessibility_score += 0.3  # 工具提示

                    if 'setWhatsThis' in content:
                        accessibility_score += 0.2  # 帮助文本

                    if 'setShortcut' in content:
                        accessibility_score += 0.3  # 键盘快捷键

                    if 'setAccessibleName' in content or 'setAccessibleDescription' in content:
                        accessibility_score += 0.2  # 可访问性标签

                except Exception:
                    continue

            return min(1.0, accessibility_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估可访问性合规失败: {e}")
            return 0.0

    def evaluate_user_control(self) -> float:
        """评估用户控制"""
        try:
            control_score = 0.0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查用户控制元素
                    if 'QSlider' in content or 'QSpinBox' in content:
                        control_score += 0.2  # 数值控制

                    if 'QCheckBox' in content or 'QRadioButton' in content:
                        control_score += 0.2  # 选择控制

                    if 'QComboBox' in content:
                        control_score += 0.2  # 下拉选择

                    if 'QTextEdit' in content or 'QLineEdit' in content:
                        control_score += 0.2  # 文本输入

                    if 'undo' in content.lower() or 'redo' in content.lower():
                        control_score += 0.2  # 撤销重做

                except Exception:
                    continue

            return min(1.0, control_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估用户控制失败: {e}")
            return 0.0

    def evaluate_feedback_quality(self) -> float:
        """评估反馈质量"""
        try:
            feedback_score = 0.0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查反馈机制
                    if 'QProgressBar' in content:
                        feedback_score += 0.3  # 进度反馈

                    if 'QMessageBox' in content:
                        feedback_score += 0.3  # 消息反馈

                    if 'QStatusBar' in content or 'showMessage' in content:
                        feedback_score += 0.2  # 状态反馈

                    if 'pyqtSignal' in content:
                        feedback_score += 0.2  # 信号反馈

                except Exception:
                    continue

            return min(1.0, feedback_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估反馈质量失败: {e}")
            return 0.0

    def evaluate_error_prevention(self) -> float:
        """评估错误预防"""
        try:
            prevention_score = 0.0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查错误预防机制
                    if 'QValidator' in content:
                        prevention_score += 0.3  # 输入验证

                    if 'try:' in content and 'except' in content:
                        prevention_score += 0.3  # 异常处理

                    if 'setEnabled(False)' in content:
                        prevention_score += 0.2  # 状态控制

                    if 'confirm' in content.lower() or 'warning' in content.lower():
                        prevention_score += 0.2  # 确认对话框

                except Exception:
                    continue

            return min(1.0, prevention_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估错误预防失败: {e}")
            return 0.0

    def evaluate_task_efficiency(self) -> float:
        """评估任务效率"""
        try:
            efficiency_score = 0.0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查效率特性
                    if 'setShortcut' in content:
                        efficiency_score += 0.3  # 快捷键

                    if 'QAction' in content:
                        efficiency_score += 0.2  # 动作系统

                    if 'batch' in content.lower() or 'bulk' in content.lower():
                        efficiency_score += 0.3  # 批量操作

                    if 'template' in content.lower() or 'preset' in content.lower():
                        efficiency_score += 0.2  # 模板预设

                except Exception:
                    continue

            return min(1.0, efficiency_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估任务效率失败: {e}")
            return 0.0

    def evaluate_learning_curve(self) -> float:
        """评估学习曲线"""
        try:
            learning_score = 0.0

            # 检查学习辅助功能
            help_files = list(self.project_root.rglob("*help*.py")) + \
                        list(self.project_root.rglob("*tutorial*.py")) + \
                        list(self.project_root.rglob("*guide*.py"))

            if help_files:
                learning_score += 0.4

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查学习辅助
                    if 'setToolTip' in content:
                        learning_score += 0.3  # 工具提示

                    if 'wizard' in content.lower() or 'guide' in content.lower():
                        learning_score += 0.3  # 向导引导

                except Exception:
                    continue

            return min(1.0, learning_score)

        except Exception as e:
            logger.error(f"评估学习曲线失败: {e}")
            return 0.0

    def evaluate_workflow_optimization(self) -> float:
        """评估工作流程优化"""
        try:
            workflow_score = 0.0

            # 检查工作流程相关文件
            workflow_files = list(self.project_root.rglob("*workflow*.py")) + \
                           list(self.project_root.rglob("*process*.py"))

            if workflow_files:
                workflow_score += 0.4

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查工作流程优化
                    if 'QTabWidget' in content:
                        workflow_score += 0.2  # 标签页工作流

                    if 'QWizard' in content:
                        workflow_score += 0.3  # 向导工作流

                    if 'pipeline' in content.lower():
                        workflow_score += 0.1  # 管道处理

                except Exception:
                    continue

            return min(1.0, workflow_score)

        except Exception as e:
            logger.error(f"评估工作流程优化失败: {e}")
            return 0.0

    def evaluate_color_system(self) -> float:
        """评估色彩系统"""
        try:
            color_score = 0.0

            # 检查主题管理器
            theme_files = list(self.project_root.rglob("*theme*.py")) + \
                         list(self.project_root.rglob("*color*.py"))

            if theme_files:
                color_score += 0.5

            # 检查样式文件
            for file_path in self.style_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查色彩使用
                    color_count = len(re.findall(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|rgb\(|rgba\(', content))
                    if color_count > 5:
                        color_score += 0.3

                    if 'color:' in content:
                        color_score += 0.2

                except Exception:
                    continue

            return min(1.0, color_score)

        except Exception as e:
            logger.error(f"评估色彩系统失败: {e}")
            return 0.0

    def evaluate_typography(self) -> float:
        """评估字体排版"""
        try:
            typography_score = 0.0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查字体设置
                    if 'QFont' in content:
                        typography_score += 0.4

                    if 'setFont' in content:
                        typography_score += 0.3

                    if 'font-family' in content or 'font-size' in content:
                        typography_score += 0.3

                except Exception:
                    continue

            return min(1.0, typography_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估字体排版失败: {e}")
            return 0.0

    def evaluate_iconography(self) -> float:
        """评估图标系统"""
        try:
            icon_score = 0.0

            # 检查图标文件
            icon_files = list(self.project_root.rglob("*icon*.py")) + \
                        list(self.project_root.rglob("*.png")) + \
                        list(self.project_root.rglob("*.svg"))

            if icon_files:
                icon_score += 0.4

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查图标使用
                    if 'QIcon' in content or 'setIcon' in content:
                        icon_score += 0.3

                    if '🎨' in content or '⏱️' in content or '🤖' in content:
                        icon_score += 0.3  # 表情符号图标

                except Exception:
                    continue

            return min(1.0, icon_score)

        except Exception as e:
            logger.error(f"评估图标系统失败: {e}")
            return 0.0

    def evaluate_visual_hierarchy(self) -> float:
        """评估视觉层次"""
        try:
            hierarchy_score = 0.0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查层次结构
                    if 'QGroupBox' in content:
                        hierarchy_score += 0.3  # 分组层次

                    if 'QSplitter' in content:
                        hierarchy_score += 0.3  # 分割层次

                    if 'QTabWidget' in content:
                        hierarchy_score += 0.2  # 标签层次

                    if 'QFrame' in content:
                        hierarchy_score += 0.2  # 框架层次

                except Exception:
                    continue

            return min(1.0, hierarchy_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估视觉层次失败: {e}")
            return 0.0

    def evaluate_brand_consistency(self) -> float:
        """评估品牌一致性"""
        try:
            consistency_score = 0.0

            # 检查品牌元素
            brand_elements = 0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查品牌一致性
                    if 'AI Animation Studio' in content:
                        brand_elements += 1

                    if 'setWindowTitle' in content:
                        consistency_score += 0.2

                    if 'setStyleSheet' in content:
                        consistency_score += 0.3

                except Exception:
                    continue

            if brand_elements > 0:
                consistency_score += 0.5

            return min(1.0, consistency_score)

        except Exception as e:
            logger.error(f"评估品牌一致性失败: {e}")
            return 0.0

    def evaluate_aesthetic_appeal(self) -> float:
        """评估美学吸引力"""
        try:
            aesthetic_score = 0.0

            # 检查美学元素
            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查美学特性
                    if 'gradient' in content.lower():
                        aesthetic_score += 0.2

                    if 'shadow' in content.lower():
                        aesthetic_score += 0.2

                    if 'border-radius' in content or 'rounded' in content.lower():
                        aesthetic_score += 0.2

                    if 'animation' in content.lower() or 'transition' in content.lower():
                        aesthetic_score += 0.2

                    if 'opacity' in content.lower():
                        aesthetic_score += 0.2

                except Exception:
                    continue

            return min(1.0, aesthetic_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估美学吸引力失败: {e}")
            return 0.0

    def evaluate_personalization(self) -> float:
        """评估个性化"""
        try:
            personalization_score = 0.0

            # 检查个性化功能
            personalization_files = list(self.project_root.rglob("*preference*.py")) + \
                                   list(self.project_root.rglob("*setting*.py")) + \
                                   list(self.project_root.rglob("*config*.py"))

            if personalization_files:
                personalization_score += 0.6

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if 'QSettings' in content:
                        personalization_score += 0.4

                except Exception:
                    continue

            return min(1.0, personalization_score)

        except Exception as e:
            logger.error(f"评估个性化失败: {e}")
            return 0.0

    def evaluate_customization(self) -> float:
        """评估定制化"""
        try:
            customization_score = 0.0

            # 检查定制化功能
            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查定制化特性
                    if 'customize' in content.lower() or 'custom' in content.lower():
                        customization_score += 0.3

                    if 'QDockWidget' in content:
                        customization_score += 0.3  # 可停靠面板

                    if 'QSplitter' in content:
                        customization_score += 0.2  # 可调整分割

                    if 'resize' in content.lower():
                        customization_score += 0.2  # 可调整大小

                except Exception:
                    continue

            return min(1.0, customization_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估定制化失败: {e}")
            return 0.0

    def evaluate_context_awareness(self) -> float:
        """评估上下文感知"""
        try:
            context_score = 0.0

            # 检查上下文感知功能
            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查上下文特性
                    if 'context' in content.lower():
                        context_score += 0.3

                    if 'QContextMenuEvent' in content or 'contextMenuEvent' in content:
                        context_score += 0.4  # 右键菜单

                    if 'state' in content.lower() and 'change' in content.lower():
                        context_score += 0.3  # 状态感知

                except Exception:
                    continue

            return min(1.0, context_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估上下文感知失败: {e}")
            return 0.0

    def evaluate_multi_device_support(self) -> float:
        """评估多设备支持"""
        try:
            device_score = 0.0

            # 检查响应式设计文件
            responsive_files = list(self.project_root.rglob("*responsive*.py")) + \
                              list(self.project_root.rglob("*adaptive*.py"))

            if responsive_files:
                device_score += 0.7

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if 'screen' in content.lower() or 'device' in content.lower():
                        device_score += 0.3

                except Exception:
                    continue

            return min(1.0, device_score)

        except Exception as e:
            logger.error(f"评估多设备支持失败: {e}")
            return 0.0

    def evaluate_internationalization(self) -> float:
        """评估国际化"""
        try:
            i18n_score = 0.0

            # 检查国际化文件
            i18n_files = list(self.project_root.rglob("*i18n*.py")) + \
                        list(self.project_root.rglob("*locale*.py")) + \
                        list(self.project_root.rglob("*.po")) + \
                        list(self.project_root.rglob("*.mo"))

            if i18n_files:
                i18n_score += 0.6

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if 'tr(' in content or 'translate(' in content:
                        i18n_score += 0.4  # 翻译函数

                except Exception:
                    continue

            return min(1.0, i18n_score)

        except Exception as e:
            logger.error(f"评估国际化失败: {e}")
            return 0.0

    def evaluate_scalability(self) -> float:
        """评估可扩展性"""
        try:
            scalability_score = 0.0

            # 检查可扩展性设计
            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查可扩展性特性
                    if 'QScrollArea' in content:
                        scalability_score += 0.3  # 滚动支持

                    if 'QAbstractItemModel' in content or 'QStandardItemModel' in content:
                        scalability_score += 0.4  # 数据模型

                    if 'pagination' in content.lower() or 'lazy' in content.lower():
                        scalability_score += 0.3  # 分页/懒加载

                except Exception:
                    continue

            return min(1.0, scalability_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估可扩展性失败: {e}")
            return 0.0

    def evaluate_learnability(self) -> float:
        """评估易学性"""
        try:
            learnability_score = 0.0

            # 检查学习辅助
            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查易学性特性
                    if 'setToolTip' in content:
                        learnability_score += 0.4  # 工具提示

                    if 'help' in content.lower() or 'tutorial' in content.lower():
                        learnability_score += 0.3  # 帮助系统

                    if 'wizard' in content.lower():
                        learnability_score += 0.3  # 向导

                except Exception:
                    continue

            return min(1.0, learnability_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估易学性失败: {e}")
            return 0.0

    def evaluate_efficiency(self) -> float:
        """评估效率"""
        try:
            efficiency_score = 0.0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查效率特性
                    if 'setShortcut' in content:
                        efficiency_score += 0.4  # 快捷键

                    if 'batch' in content.lower():
                        efficiency_score += 0.3  # 批量操作

                    if 'template' in content.lower():
                        efficiency_score += 0.3  # 模板

                except Exception:
                    continue

            return min(1.0, efficiency_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估效率失败: {e}")
            return 0.0

    def evaluate_memorability(self) -> float:
        """评估易记性"""
        try:
            memorability_score = 0.0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查易记性特性
                    if 'QIcon' in content:
                        memorability_score += 0.3  # 图标辅助记忆

                    if 'consistent' in content.lower():
                        memorability_score += 0.3  # 一致性

                    if 'pattern' in content.lower():
                        memorability_score += 0.2  # 模式化

                    if 'familiar' in content.lower():
                        memorability_score += 0.2  # 熟悉性

                except Exception:
                    continue

            return min(1.0, memorability_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估易记性失败: {e}")
            return 0.0

    def evaluate_error_tolerance(self) -> float:
        """评估错误容忍度"""
        try:
            tolerance_score = 0.0

            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查错误容忍特性
                    if 'undo' in content.lower() or 'redo' in content.lower():
                        tolerance_score += 0.4  # 撤销重做

                    if 'try:' in content and 'except' in content:
                        tolerance_score += 0.3  # 异常处理

                    if 'recover' in content.lower() or 'restore' in content.lower():
                        tolerance_score += 0.3  # 恢复功能

                except Exception:
                    continue

            return min(1.0, tolerance_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估错误容忍度失败: {e}")
            return 0.0

    def evaluate_satisfaction(self) -> float:
        """评估满意度"""
        try:
            satisfaction_score = 0.0

            # 基于整体设计质量估算满意度
            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查满意度相关特性
                    if 'animation' in content.lower():
                        satisfaction_score += 0.2  # 动画效果

                    if 'smooth' in content.lower():
                        satisfaction_score += 0.2  # 流畅性

                    if 'beautiful' in content.lower() or 'elegant' in content.lower():
                        satisfaction_score += 0.2  # 美观性

                    if 'responsive' in content.lower():
                        satisfaction_score += 0.2  # 响应性

                    if 'intuitive' in content.lower():
                        satisfaction_score += 0.2  # 直观性

                except Exception:
                    continue

            return min(1.0, satisfaction_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估满意度失败: {e}")
            return 0.0

    def evaluate_task_completion_rate(self) -> float:
        """评估任务完成率"""
        try:
            completion_score = 0.0

            # 基于功能完整性估算任务完成率
            for file_path in self.ui_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查任务完成相关特性
                    if 'complete' in content.lower():
                        completion_score += 0.3

                    if 'finish' in content.lower():
                        completion_score += 0.2

                    if 'success' in content.lower():
                        completion_score += 0.3

                    if 'done' in content.lower():
                        completion_score += 0.2

                except Exception:
                    continue

            return min(1.0, completion_score / max(len(self.ui_files), 1))

        except Exception as e:
            logger.error(f"评估任务完成率失败: {e}")
            return 0.0

    def score_to_ux_quality(self, score: float) -> UXQuality:
        """将评分转换为用户体验质量级别"""
        if score >= 0.9:
            return UXQuality.WORLD_CLASS
        elif score >= 0.8:
            return UXQuality.EXCELLENT
        elif score >= 0.6:
            return UXQuality.GOOD
        elif score >= 0.4:
            return UXQuality.BASIC
        else:
            return UXQuality.POOR

    def calculate_overall_ux_score(self, report: UserExperienceReport):
        """计算综合用户体验评分"""
        try:
            # 五大维度权重
            weights = {
                "interface_design": 0.25,
                "interaction_design": 0.25,
                "visual_design": 0.2,
                "adaptability": 0.15,
                "usability": 0.15
            }

            # 将质量级别转换为数值
            quality_scores = {
                UXQuality.POOR: 0.2,
                UXQuality.BASIC: 0.4,
                UXQuality.GOOD: 0.6,
                UXQuality.EXCELLENT: 0.8,
                UXQuality.WORLD_CLASS: 1.0
            }

            # 计算加权平均分
            overall_score = (
                quality_scores[report.interface_design_quality] * weights["interface_design"] +
                quality_scores[report.interaction_design_quality] * weights["interaction_design"] +
                quality_scores[report.visual_design_quality] * weights["visual_design"] +
                quality_scores[report.adaptability_quality] * weights["adaptability"] +
                quality_scores[report.usability_quality] * weights["usability"]
            )

            report.overall_ux_score = overall_score
            report.overall_ux_quality = self.score_to_ux_quality(overall_score)

            # 确定设计成熟度
            if overall_score >= 0.9:
                report.design_maturity = DesignMaturity.INDUSTRY_LEADING
            elif overall_score >= 0.8:
                report.design_maturity = DesignMaturity.ENTERPRISE
            elif overall_score >= 0.6:
                report.design_maturity = DesignMaturity.PROFESSIONAL
            elif overall_score >= 0.4:
                report.design_maturity = DesignMaturity.BASIC_FUNCTIONAL
            else:
                report.design_maturity = DesignMaturity.PROTOTYPE

        except Exception as e:
            logger.error(f"计算综合用户体验评分失败: {e}")

    def generate_ux_findings_and_recommendations(self, report: UserExperienceReport):
        """生成用户体验关键发现和建议"""
        try:
            # 用户体验优势
            if report.interface_design_quality in [UXQuality.EXCELLENT, UXQuality.WORLD_CLASS]:
                report.ux_strengths.append("界面设计优秀，布局清晰，信息架构合理")

            if report.interaction_design_quality in [UXQuality.EXCELLENT, UXQuality.WORLD_CLASS]:
                report.ux_strengths.append("交互设计出色，用户控制良好，反馈及时")

            if report.visual_design_quality in [UXQuality.EXCELLENT, UXQuality.WORLD_CLASS]:
                report.ux_strengths.append("视觉设计精美，色彩搭配协调，视觉层次清晰")

            if report.adaptability_quality in [UXQuality.EXCELLENT, UXQuality.WORLD_CLASS]:
                report.ux_strengths.append("适应性强，支持个性化定制和多设备使用")

            if report.usability_quality in [UXQuality.EXCELLENT, UXQuality.WORLD_CLASS]:
                report.ux_strengths.append("可用性优秀，易学易用，用户满意度高")

            # 用户体验弱点
            if report.interface_design_quality == UXQuality.POOR:
                report.ux_weaknesses.append("界面设计需要重大改进，布局混乱，导航不清")

            if report.interaction_design_quality == UXQuality.POOR:
                report.ux_weaknesses.append("交互设计存在严重问题，用户控制不足，反馈缺失")

            if report.visual_design_quality == UXQuality.POOR:
                report.ux_weaknesses.append("视觉设计质量低，缺乏美感，品牌一致性差")

            if report.adaptability_quality == UXQuality.POOR:
                report.ux_weaknesses.append("适应性不足，缺乏个性化功能，多设备支持差")

            if report.usability_quality == UXQuality.POOR:
                report.ux_weaknesses.append("可用性问题严重，学习成本高，用户体验差")

            # 可用性问题
            if report.usability_metrics.learnability_score < 0.5:
                report.usability_issues.append("学习曲线陡峭，新用户上手困难")

            if report.usability_metrics.efficiency_score < 0.5:
                report.usability_issues.append("操作效率低，缺乏快捷方式和批量操作")

            if report.usability_metrics.error_tolerance_score < 0.5:
                report.usability_issues.append("错误容忍度低，缺乏撤销和恢复功能")

            # 可访问性问题
            if report.interface_design_metrics.accessibility_compliance_score < 0.5:
                report.accessibility_issues.append("可访问性合规性不足，缺乏键盘导航和屏幕阅读器支持")

            if report.adaptability_metrics.internationalization_score < 0.3:
                report.accessibility_issues.append("国际化支持不足，多语言功能缺失")

            # 设计不一致性
            if report.interface_design_metrics.layout_consistency_score < 0.6:
                report.design_inconsistencies.append("布局一致性问题，不同页面设计风格不统一")

            if report.visual_design_metrics.brand_consistency_score < 0.6:
                report.design_inconsistencies.append("品牌一致性问题，视觉元素使用不规范")

            # 关键用户体验修复
            if report.overall_ux_score < 0.5:
                report.critical_ux_fixes.append("立即进行用户体验重构，解决核心可用性问题")

            if report.interaction_design_quality == UXQuality.POOR:
                report.critical_ux_fixes.append("紧急修复交互设计问题，完善用户反馈机制")

            if report.usability_metrics.task_completion_rate < 0.5:
                report.critical_ux_fixes.append("优化核心任务流程，提高任务完成率")

            # 界面改进建议
            if report.interface_design_metrics.navigation_clarity_score < 0.6:
                report.interface_improvements.append("改进导航设计，增强导航清晰度和可发现性")

            if report.interface_design_metrics.responsive_design_score < 0.5:
                report.interface_improvements.append("实现响应式设计，支持多种屏幕尺寸")

            if report.interface_design_metrics.information_architecture_score < 0.6:
                report.interface_improvements.append("优化信息架构，改善内容组织和层次结构")

            # 交互增强建议
            if report.interaction_design_metrics.feedback_quality_score < 0.6:
                report.interaction_enhancements.append("增强用户反馈机制，提供更及时和明确的操作反馈")

            if report.interaction_design_metrics.error_prevention_score < 0.5:
                report.interaction_enhancements.append("加强错误预防设计，减少用户操作错误")

            if report.interaction_design_metrics.workflow_optimization_score < 0.6:
                report.interaction_enhancements.append("优化工作流程设计，提升任务执行效率")

            # 视觉精化建议
            if report.visual_design_metrics.color_system_score < 0.6:
                report.visual_refinements.append("建立统一的色彩系统，提升视觉一致性")

            if report.visual_design_metrics.typography_score < 0.5:
                report.visual_refinements.append("改进字体排版设计，提升文本可读性")

            if report.visual_design_metrics.aesthetic_appeal_score < 0.6:
                report.visual_refinements.append("提升视觉美感，增加现代化设计元素")

            # 适应性升级建议
            if report.adaptability_metrics.personalization_score < 0.5:
                report.adaptability_upgrades.append("增加个性化功能，支持用户偏好设置")

            if report.adaptability_metrics.customization_score < 0.5:
                report.adaptability_upgrades.append("提供更多定制化选项，增强用户控制能力")

            if report.adaptability_metrics.context_awareness_score < 0.4:
                report.adaptability_upgrades.append("增强上下文感知能力，提供智能化交互体验")

        except Exception as e:
            logger.error(f"生成用户体验关键发现和建议失败: {e}")

    def generate_html_report(self, report: UserExperienceReport) -> str:
        """生成HTML报告"""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>AI Animation Studio - 用户体验评估报告</title>
                <style>
                    body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                    .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
                    .header {{ text-align: center; color: #2c3e50; margin-bottom: 30px; }}
                    .header h1 {{ color: #667eea; margin-bottom: 10px; }}
                    .section {{ margin: 25px 0; padding: 20px; border-left: 4px solid #667eea; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 8px; }}
                    .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin: 20px 0; }}
                    .metric-card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: transform 0.3s ease; }}
                    .metric-card:hover {{ transform: translateY(-5px); }}
                    .score {{ font-size: 28px; font-weight: bold; margin: 15px 0; text-align: center; }}
                    .world-class {{ color: #e74c3c; background: linear-gradient(45deg, #ff6b6b, #ee5a24); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
                    .excellent {{ color: #27ae60; }}
                    .good {{ color: #2ecc71; }}
                    .basic {{ color: #f39c12; }}
                    .poor {{ color: #e74c3c; }}
                    .progress-bar {{ width: 100%; height: 25px; background: #ecf0f1; border-radius: 15px; overflow: hidden; margin: 15px 0; position: relative; }}
                    .progress-fill {{ height: 100%; transition: width 0.8s ease; border-radius: 15px; }}
                    .progress-text {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-weight: bold; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }}
                    .strengths {{ color: #27ae60; }}
                    .weaknesses {{ color: #e74c3c; }}
                    .recommendations {{ color: #3498db; }}
                    .critical {{ background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); border-left: 4px solid #f44336; }}
                    .interface {{ background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-left: 4px solid #2196f3; }}
                    .interaction {{ background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); border-left: 4px solid #9c27b0; }}
                    .visual {{ background: linear-gradient(135deg, #fff3e0 0%, #ffcc02 100%); border-left: 4px solid #ff9800; }}
                    .adaptability {{ background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); border-left: 4px solid #4caf50; }}
                    .detailed-metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                    .metric-item {{ background: rgba(255,255,255,0.8); padding: 15px; border-radius: 8px; text-align: center; }}
                    .metric-value {{ font-size: 20px; font-weight: bold; color: #2c3e50; }}
                    .metric-label {{ font-size: 12px; color: #7f8c8d; margin-top: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎨 AI Animation Studio 用户体验评估报告</h1>
                        <p>评估时间: {report.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <div class="score {self.get_ux_quality_class(report.overall_ux_quality)}">
                            综合评分: {report.overall_ux_score:.1%} ({report.overall_ux_quality.value})
                        </div>
                        <p><strong>设计成熟度:</strong> {report.design_maturity.value}</p>
                    </div>

                    <div class="section">
                        <h2>📊 五大维度评估</h2>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <h3>🏗️ 界面设计质量</h3>
                                <div class="score {self.get_ux_quality_class(report.interface_design_quality)}">{report.interface_design_quality.value}</div>
                                <div class="progress-bar">
                                    <div class="progress-fill {self.get_ux_quality_class(report.interface_design_quality)}"
                                         style="width: {self.ux_quality_to_percentage(report.interface_design_quality)}%; background: linear-gradient(45deg, #3498db, #2980b9);"></div>
                                    <div class="progress-text">{self.ux_quality_to_percentage(report.interface_design_quality)}%</div>
                                </div>
                                <div class="detailed-metrics">
                                    <div class="metric-item">
                                        <div class="metric-value">{report.interface_design_metrics.layout_consistency_score:.1%}</div>
                                        <div class="metric-label">布局一致性</div>
                                    </div>
                                    <div class="metric-item">
                                        <div class="metric-value">{report.interface_design_metrics.navigation_clarity_score:.1%}</div>
                                        <div class="metric-label">导航清晰度</div>
                                    </div>
                                    <div class="metric-item">
                                        <div class="metric-value">{report.interface_design_metrics.accessibility_compliance_score:.1%}</div>
                                        <div class="metric-label">可访问性</div>
                                    </div>
                                </div>
                            </div>

                            <div class="metric-card">
                                <h3>🎯 交互设计质量</h3>
                                <div class="score {self.get_ux_quality_class(report.interaction_design_quality)}">{report.interaction_design_quality.value}</div>
                                <div class="progress-bar">
                                    <div class="progress-fill {self.get_ux_quality_class(report.interaction_design_quality)}"
                                         style="width: {self.ux_quality_to_percentage(report.interaction_design_quality)}%; background: linear-gradient(45deg, #9c27b0, #7b1fa2);"></div>
                                    <div class="progress-text">{self.ux_quality_to_percentage(report.interaction_design_quality)}%</div>
                                </div>
                                <div class="detailed-metrics">
                                    <div class="metric-item">
                                        <div class="metric-value">{report.interaction_design_metrics.user_control_score:.1%}</div>
                                        <div class="metric-label">用户控制</div>
                                    </div>
                                    <div class="metric-item">
                                        <div class="metric-value">{report.interaction_design_metrics.feedback_quality_score:.1%}</div>
                                        <div class="metric-label">反馈质量</div>
                                    </div>
                                    <div class="metric-item">
                                        <div class="metric-value">{report.interaction_design_metrics.task_efficiency_score:.1%}</div>
                                        <div class="metric-label">任务效率</div>
                                    </div>
                                </div>
                            </div>

                            <div class="metric-card">
                                <h3>🎨 视觉设计质量</h3>
                                <div class="score {self.get_ux_quality_class(report.visual_design_quality)}">{report.visual_design_quality.value}</div>
                                <div class="progress-bar">
                                    <div class="progress-fill {self.get_ux_quality_class(report.visual_design_quality)}"
                                         style="width: {self.ux_quality_to_percentage(report.visual_design_quality)}%; background: linear-gradient(45deg, #ff9800, #f57c00);"></div>
                                    <div class="progress-text">{self.ux_quality_to_percentage(report.visual_design_quality)}%</div>
                                </div>
                                <div class="detailed-metrics">
                                    <div class="metric-item">
                                        <div class="metric-value">{report.visual_design_metrics.color_system_score:.1%}</div>
                                        <div class="metric-label">色彩系统</div>
                                    </div>
                                    <div class="metric-item">
                                        <div class="metric-value">{report.visual_design_metrics.visual_hierarchy_score:.1%}</div>
                                        <div class="metric-label">视觉层次</div>
                                    </div>
                                    <div class="metric-item">
                                        <div class="metric-value">{report.visual_design_metrics.aesthetic_appeal_score:.1%}</div>
                                        <div class="metric-label">美学吸引力</div>
                                    </div>
                                </div>
                            </div>

                            <div class="metric-card">
                                <h3>🔄 适应性质量</h3>
                                <div class="score {self.get_ux_quality_class(report.adaptability_quality)}">{report.adaptability_quality.value}</div>
                                <div class="progress-bar">
                                    <div class="progress-fill {self.get_ux_quality_class(report.adaptability_quality)}"
                                         style="width: {self.ux_quality_to_percentage(report.adaptability_quality)}%; background: linear-gradient(45deg, #4caf50, #388e3c);"></div>
                                    <div class="progress-text">{self.ux_quality_to_percentage(report.adaptability_quality)}%</div>
                                </div>
                                <div class="detailed-metrics">
                                    <div class="metric-item">
                                        <div class="metric-value">{report.adaptability_metrics.personalization_score:.1%}</div>
                                        <div class="metric-label">个性化</div>
                                    </div>
                                    <div class="metric-item">
                                        <div class="metric-value">{report.adaptability_metrics.customization_score:.1%}</div>
                                        <div class="metric-label">定制化</div>
                                    </div>
                                    <div class="metric-item">
                                        <div class="metric-value">{report.adaptability_metrics.scalability_score:.1%}</div>
                                        <div class="metric-label">可扩展性</div>
                                    </div>
                                </div>
                            </div>

                            <div class="metric-card">
                                <h3>✅ 可用性质量</h3>
                                <div class="score {self.get_ux_quality_class(report.usability_quality)}">{report.usability_quality.value}</div>
                                <div class="progress-bar">
                                    <div class="progress-fill {self.get_ux_quality_class(report.usability_quality)}"
                                         style="width: {self.ux_quality_to_percentage(report.usability_quality)}%; background: linear-gradient(45deg, #607d8b, #455a64);"></div>
                                    <div class="progress-text">{self.ux_quality_to_percentage(report.usability_quality)}%</div>
                                </div>
                                <div class="detailed-metrics">
                                    <div class="metric-item">
                                        <div class="metric-value">{report.usability_metrics.learnability_score:.1%}</div>
                                        <div class="metric-label">易学性</div>
                                    </div>
                                    <div class="metric-item">
                                        <div class="metric-value">{report.usability_metrics.efficiency_score:.1%}</div>
                                        <div class="metric-label">效率</div>
                                    </div>
                                    <div class="metric-item">
                                        <div class="metric-value">{report.usability_metrics.satisfaction_score:.1%}</div>
                                        <div class="metric-label">满意度</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
            """

            # 用户体验优势
            if report.ux_strengths:
                html += """
                    <div class="section">
                        <h2>💪 用户体验优势</h2>
                        <ul class="strengths">
                """
                for strength in report.ux_strengths:
                    html += f"<li>✅ {strength}</li>"
                html += """
                        </ul>
                    </div>
                """

            # 用户体验弱点
            if report.ux_weaknesses:
                html += """
                    <div class="section">
                        <h2>⚠️ 用户体验弱点</h2>
                        <ul class="weaknesses">
                """
                for weakness in report.ux_weaknesses:
                    html += f"<li>❌ {weakness}</li>"
                html += """
                        </ul>
                    </div>
                """

            # 关键用户体验修复
            if report.critical_ux_fixes:
                html += """
                    <div class="section critical">
                        <h2>🚨 关键用户体验修复</h2>
                        <ul class="recommendations">
                """
                for fix in report.critical_ux_fixes:
                    html += f"<li>🔥 {fix}</li>"
                html += """
                        </ul>
                    </div>
                """

            # 界面改进建议
            if report.interface_improvements:
                html += """
                    <div class="section interface">
                        <h2>🏗️ 界面改进建议</h2>
                        <ul class="recommendations">
                """
                for improvement in report.interface_improvements:
                    html += f"<li>🔧 {improvement}</li>"
                html += """
                        </ul>
                    </div>
                """

            # 交互增强建议
            if report.interaction_enhancements:
                html += """
                    <div class="section interaction">
                        <h2>🎯 交互增强建议</h2>
                        <ul class="recommendations">
                """
                for enhancement in report.interaction_enhancements:
                    html += f"<li>⚡ {enhancement}</li>"
                html += """
                        </ul>
                    </div>
                """

            # 视觉精化建议
            if report.visual_refinements:
                html += """
                    <div class="section visual">
                        <h2>🎨 视觉精化建议</h2>
                        <ul class="recommendations">
                """
                for refinement in report.visual_refinements:
                    html += f"<li>🌟 {refinement}</li>"
                html += """
                        </ul>
                    </div>
                """

            # 适应性升级建议
            if report.adaptability_upgrades:
                html += """
                    <div class="section adaptability">
                        <h2>🔄 适应性升级建议</h2>
                        <ul class="recommendations">
                """
                for upgrade in report.adaptability_upgrades:
                    html += f"<li>🚀 {upgrade}</li>"
                html += """
                        </ul>
                    </div>
                """

            html += """
                </div>
            </body>
            </html>
            """

            return html

        except Exception as e:
            logger.error(f"生成HTML报告失败: {e}")
            return f"<html><body><h1>报告生成失败: {e}</h1></body></html>"

    def get_ux_quality_class(self, quality: UXQuality) -> str:
        """获取用户体验质量样式类"""
        quality_classes = {
            UXQuality.WORLD_CLASS: "world-class",
            UXQuality.EXCELLENT: "excellent",
            UXQuality.GOOD: "good",
            UXQuality.BASIC: "basic",
            UXQuality.POOR: "poor"
        }
        return quality_classes.get(quality, "poor")

    def ux_quality_to_percentage(self, quality: UXQuality) -> int:
        """将用户体验质量级别转换为百分比"""
        quality_percentages = {
            UXQuality.WORLD_CLASS: 100,
            UXQuality.EXCELLENT: 85,
            UXQuality.GOOD: 70,
            UXQuality.BASIC: 50,
            UXQuality.POOR: 25
        }
        return quality_percentages.get(quality, 25)
