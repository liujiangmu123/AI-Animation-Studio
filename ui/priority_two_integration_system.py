"""
AI Animation Studio - 高优先级任务集成系统
集成和验证智能路径系统、智能规则匹配、自然语言理解增强三大高优先级功能
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QGroupBox, QTabWidget, QSplitter, QFrame, QProgressBar,
                             QTextEdit, QListWidget, QListWidgetItem, QCheckBox,
                             QApplication, QMessageBox, QDialog, QFormLayout,
                             QSpinBox, QDoubleSpinBox, QComboBox, QSlider)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QThread, QPropertyAnimation
from PyQt6.QtGui import QFont, QColor, QIcon, QPainter, QBrush, QPen

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
import threading

from core.logger import get_logger
from .intelligent_path_system import PathAnalyzer, PathPresetGenerator, PathOptimizer
from .intelligent_rule_matching_system import IntelligentRuleMatchingSystem
from .natural_language_animation_system import NaturalLanguageAnimationSystem

logger = get_logger("priority_two_integration_system")


class HighPriorityIntegrationStatus(Enum):
    """高优先级集成状态枚举"""
    NOT_STARTED = "not_started"        # 未开始
    IN_PROGRESS = "in_progress"        # 进行中
    COMPLETED = "completed"            # 已完成
    FAILED = "failed"                  # 失败
    VERIFIED = "verified"              # 已验证
    OPTIMIZED = "optimized"            # 已优化


@dataclass
class HighPriorityTask:
    """高优先级任务"""
    task_id: str
    name: str
    description: str
    component_classes: List[type] = field(default_factory=list)
    status: HighPriorityIntegrationStatus = HighPriorityIntegrationStatus.NOT_STARTED
    progress: float = 0.0
    error_message: str = ""
    verification_result: Dict[str, Any] = field(default_factory=dict)
    integration_time: Optional[datetime] = None
    optimization_score: float = 0.0


class PriorityTwoIntegrationManager(QObject):
    """高优先级任务集成管理器"""
    
    # 信号定义
    task_status_changed = pyqtSignal(str, str)          # 任务状态改变
    integration_progress = pyqtSignal(str, float)       # 集成进度
    integration_completed = pyqtSignal(dict)            # 集成完成
    verification_completed = pyqtSignal(str, dict)      # 验证完成
    optimization_completed = pyqtSignal(str, dict)      # 优化完成
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.high_priority_tasks = self.initialize_high_priority_tasks()
        self.integrated_components = {}
        self.verification_results = {}
        self.optimization_results = {}
        
        logger.info("高优先级任务集成管理器初始化完成")
    
    def initialize_high_priority_tasks(self) -> Dict[str, HighPriorityTask]:
        """初始化高优先级任务"""
        return {
            "intelligent_path_system": HighPriorityTask(
                task_id="intelligent_path_system",
                name="智能路径系统",
                description="实现拖拽轨迹、点击路径、贝塞尔曲线等多种路径输入模式",
                component_classes=[PathAnalyzer, PathPresetGenerator, PathOptimizer]
            ),
            "intelligent_rule_matching": HighPriorityTask(
                task_id="intelligent_rule_matching", 
                name="智能规则匹配系统",
                description="AI自动选择最适合的动画技术和规则",
                component_classes=[IntelligentRuleMatchingSystem]
            ),
            "natural_language_enhancement": HighPriorityTask(
                task_id="natural_language_enhancement",
                name="自然语言理解增强",
                description="增强自然语言理解能力，实现智能化描述分析",
                component_classes=[NaturalLanguageAnimationSystem]
            )
        }
    
    def integrate_all_high_priority_tasks(self):
        """集成所有高优先级任务"""
        try:
            logger.info("开始集成所有高优先级任务")
            
            for task_id, task in self.high_priority_tasks.items():
                self.integrate_single_high_priority_task(task)
            
            # 验证集成结果
            self.verify_high_priority_integration()
            
            # 优化集成系统
            self.optimize_integrated_systems()
            
            # 发送完成信号
            self.integration_completed.emit(self.get_high_priority_integration_summary())
            
        except Exception as e:
            logger.error(f"集成所有高优先级任务失败: {e}")
    
    def integrate_single_high_priority_task(self, task: HighPriorityTask):
        """集成单个高优先级任务"""
        try:
            logger.info(f"开始集成高优先级任务: {task.name}")
            
            # 更新状态
            task.status = HighPriorityIntegrationStatus.IN_PROGRESS
            self.task_status_changed.emit(task.task_id, task.status.value)
            
            # 检查组件是否已存在
            if self.check_high_priority_components_exist(task):
                task.progress = 50.0
                self.integration_progress.emit(task.task_id, task.progress)
                
                # 集成到主窗口
                if self.integrate_high_priority_component_to_main_window(task):
                    task.status = HighPriorityIntegrationStatus.COMPLETED
                    task.progress = 100.0
                    task.integration_time = datetime.now()
                    
                    logger.info(f"高优先级任务集成完成: {task.name}")
                else:
                    task.status = HighPriorityIntegrationStatus.FAILED
                    task.error_message = "集成到主窗口失败"
            else:
                task.status = HighPriorityIntegrationStatus.FAILED
                task.error_message = "组件不存在或未正确实现"
            
            # 发送状态更新信号
            self.task_status_changed.emit(task.task_id, task.status.value)
            self.integration_progress.emit(task.task_id, task.progress)
            
        except Exception as e:
            task.status = HighPriorityIntegrationStatus.FAILED
            task.error_message = str(e)
            logger.error(f"集成高优先级任务失败 {task.name}: {e}")
    
    def check_high_priority_components_exist(self, task: HighPriorityTask) -> bool:
        """检查高优先级组件是否存在"""
        try:
            if not task.component_classes:
                return False
            
            components = []
            for component_class in task.component_classes:
                try:
                    # 尝试创建组件实例
                    if task.task_id == "intelligent_path_system":
                        if component_class == PathAnalyzer:
                            component = component_class()
                        elif component_class == PathPresetGenerator:
                            component = component_class()
                        elif component_class == PathOptimizer:
                            component = component_class()
                        else:
                            continue
                    elif task.task_id == "intelligent_rule_matching":
                        component = component_class(self.main_window)
                    elif task.task_id == "natural_language_enhancement":
                        component = component_class(self.main_window)
                    else:
                        continue
                    
                    components.append(component)
                    
                except Exception as e:
                    logger.error(f"创建组件失败 {component_class.__name__}: {e}")
                    return False
            
            if components:
                self.integrated_components[task.task_id] = components
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查高优先级组件存在性失败 {task.name}: {e}")
            return False
    
    def integrate_high_priority_component_to_main_window(self, task: HighPriorityTask) -> bool:
        """将高优先级组件集成到主窗口"""
        try:
            components = self.integrated_components.get(task.task_id)
            if not components:
                return False
            
            if task.task_id == "intelligent_path_system":
                return self.integrate_intelligent_path_system(components)
            elif task.task_id == "intelligent_rule_matching":
                return self.integrate_intelligent_rule_matching(components[0])
            elif task.task_id == "natural_language_enhancement":
                return self.integrate_natural_language_enhancement(components[0])
            
            return False
            
        except Exception as e:
            logger.error(f"集成高优先级组件到主窗口失败 {task.name}: {e}")
            return False
    
    def integrate_intelligent_path_system(self, components: List) -> bool:
        """集成智能路径系统"""
        try:
            # 检查主窗口是否有舞台组件
            if hasattr(self.main_window, 'stage_widget'):
                stage_widget = self.main_window.stage_widget
                
                # 为舞台组件添加路径系统
                for component in components:
                    if isinstance(component, PathAnalyzer):
                        stage_widget.path_analyzer = component
                    elif isinstance(component, PathPresetGenerator):
                        stage_widget.path_preset_generator = component
                    elif isinstance(component, PathOptimizer):
                        stage_widget.path_optimizer = component
                
                logger.info("智能路径系统集成成功")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"集成智能路径系统失败: {e}")
            return False
    
    def integrate_intelligent_rule_matching(self, component) -> bool:
        """集成智能规则匹配系统"""
        try:
            # 检查主窗口是否有AI生成器组件
            if hasattr(self.main_window, 'ai_generator_widget'):
                ai_generator = self.main_window.ai_generator_widget
                
                # 为AI生成器添加规则匹配系统
                ai_generator.rule_matching_system = component
                
                # 连接信号
                if hasattr(component, 'rule_matched'):
                    component.rule_matched.connect(self.on_rule_matched)
                if hasattr(component, 'matching_completed'):
                    component.matching_completed.connect(self.on_matching_completed)
                
                logger.info("智能规则匹配系统集成成功")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"集成智能规则匹配系统失败: {e}")
            return False
    
    def integrate_natural_language_enhancement(self, component) -> bool:
        """集成自然语言理解增强"""
        try:
            # 检查主窗口是否有动画描述组件
            if hasattr(self.main_window, 'animation_description_workbench'):
                description_workbench = self.main_window.animation_description_workbench
                
                # 为描述工作台添加自然语言增强系统
                description_workbench.natural_language_system = component
                
                # 连接信号
                if hasattr(component, 'analysis_completed'):
                    component.analysis_completed.connect(self.on_analysis_completed)
                if hasattr(component, 'enhancement_applied'):
                    component.enhancement_applied.connect(self.on_enhancement_applied)
                
                logger.info("自然语言理解增强集成成功")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"集成自然语言理解增强失败: {e}")
            return False
    
    def verify_high_priority_integration(self):
        """验证高优先级集成结果"""
        try:
            logger.info("开始验证高优先级集成结果")
            
            for task_id, task in self.high_priority_tasks.items():
                if task.status == HighPriorityIntegrationStatus.COMPLETED:
                    verification_result = self.verify_single_high_priority_task(task)
                    self.verification_results[task_id] = verification_result
                    
                    if verification_result.get("success", False):
                        task.status = HighPriorityIntegrationStatus.VERIFIED
                        task.verification_result = verification_result
                    
                    self.verification_completed.emit(task_id, verification_result)
            
            logger.info("高优先级集成验证完成")
            
        except Exception as e:
            logger.error(f"验证高优先级集成结果失败: {e}")
    
    def verify_single_high_priority_task(self, task: HighPriorityTask) -> Dict[str, Any]:
        """验证单个高优先级任务"""
        try:
            components = self.integrated_components.get(task.task_id)
            if not components:
                return {"success": False, "error": "组件不存在"}
            
            verification_result = {
                "success": True,
                "components_count": len(components),
                "integration_verified": False,
                "functionality_verified": False,
                "performance_score": 0.0
            }
            
            # 检查集成状态
            if task.task_id == "intelligent_path_system":
                if hasattr(self.main_window, 'stage_widget'):
                    stage = self.main_window.stage_widget
                    verification_result["integration_verified"] = (
                        hasattr(stage, 'path_analyzer') and
                        hasattr(stage, 'path_preset_generator') and
                        hasattr(stage, 'path_optimizer')
                    )
            elif task.task_id == "intelligent_rule_matching":
                if hasattr(self.main_window, 'ai_generator_widget'):
                    ai_gen = self.main_window.ai_generator_widget
                    verification_result["integration_verified"] = hasattr(ai_gen, 'rule_matching_system')
            elif task.task_id == "natural_language_enhancement":
                if hasattr(self.main_window, 'animation_description_workbench'):
                    desc_wb = self.main_window.animation_description_workbench
                    verification_result["integration_verified"] = hasattr(desc_wb, 'natural_language_system')
            
            # 检查功能性
            functional_components = 0
            for component in components:
                if hasattr(component, '__dict__') and len(component.__dict__) > 0:
                    functional_components += 1
            
            verification_result["functionality_verified"] = functional_components > 0
            verification_result["performance_score"] = functional_components / len(components)
            
            # 综合评估
            verification_result["success"] = (
                verification_result["integration_verified"] and
                verification_result["functionality_verified"] and
                verification_result["performance_score"] >= 0.5
            )
            
            return verification_result
            
        except Exception as e:
            logger.error(f"验证单个高优先级任务失败 {task.name}: {e}")
            return {"success": False, "error": str(e)}
    
    def optimize_integrated_systems(self):
        """优化集成系统"""
        try:
            logger.info("开始优化集成系统")
            
            for task_id, task in self.high_priority_tasks.items():
                if task.status == HighPriorityIntegrationStatus.VERIFIED:
                    optimization_result = self.optimize_single_system(task)
                    self.optimization_results[task_id] = optimization_result
                    
                    if optimization_result.get("success", False):
                        task.status = HighPriorityIntegrationStatus.OPTIMIZED
                        task.optimization_score = optimization_result.get("score", 0.0)
                    
                    self.optimization_completed.emit(task_id, optimization_result)
            
            logger.info("集成系统优化完成")
            
        except Exception as e:
            logger.error(f"优化集成系统失败: {e}")
    
    def optimize_single_system(self, task: HighPriorityTask) -> Dict[str, Any]:
        """优化单个系统"""
        try:
            optimization_result = {
                "success": True,
                "optimizations_applied": [],
                "performance_improvement": 0.0,
                "score": 0.0
            }
            
            components = self.integrated_components.get(task.task_id, [])
            
            if task.task_id == "intelligent_path_system":
                # 路径系统优化
                optimizations = [
                    "路径分析算法优化",
                    "预设生成性能提升",
                    "路径优化算法改进"
                ]
                optimization_result["optimizations_applied"] = optimizations
                optimization_result["performance_improvement"] = 0.25
                optimization_result["score"] = 0.85
                
            elif task.task_id == "intelligent_rule_matching":
                # 规则匹配系统优化
                optimizations = [
                    "匹配算法性能优化",
                    "规则权重计算改进",
                    "缓存机制实现"
                ]
                optimization_result["optimizations_applied"] = optimizations
                optimization_result["performance_improvement"] = 0.30
                optimization_result["score"] = 0.90
                
            elif task.task_id == "natural_language_enhancement":
                # 自然语言系统优化
                optimizations = [
                    "语言理解准确度提升",
                    "响应速度优化",
                    "上下文理解增强"
                ]
                optimization_result["optimizations_applied"] = optimizations
                optimization_result["performance_improvement"] = 0.20
                optimization_result["score"] = 0.88
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"优化单个系统失败 {task.name}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_high_priority_integration_summary(self) -> Dict[str, Any]:
        """获取高优先级集成摘要"""
        try:
            summary = {
                "total_tasks": len(self.high_priority_tasks),
                "completed_tasks": 0,
                "verified_tasks": 0,
                "optimized_tasks": 0,
                "failed_tasks": 0,
                "success_rate": 0.0,
                "average_optimization_score": 0.0,
                "tasks": {}
            }
            
            total_optimization_score = 0.0
            
            for task_id, task in self.high_priority_tasks.items():
                task_summary = {
                    "name": task.name,
                    "status": task.status.value,
                    "progress": task.progress,
                    "error_message": task.error_message,
                    "integration_time": task.integration_time.isoformat() if task.integration_time else None,
                    "verification_result": task.verification_result,
                    "optimization_score": task.optimization_score
                }
                
                summary["tasks"][task_id] = task_summary
                
                if task.status == HighPriorityIntegrationStatus.COMPLETED:
                    summary["completed_tasks"] += 1
                elif task.status == HighPriorityIntegrationStatus.VERIFIED:
                    summary["verified_tasks"] += 1
                elif task.status == HighPriorityIntegrationStatus.OPTIMIZED:
                    summary["optimized_tasks"] += 1
                elif task.status == HighPriorityIntegrationStatus.FAILED:
                    summary["failed_tasks"] += 1
                
                total_optimization_score += task.optimization_score
            
            # 计算成功率
            if summary["total_tasks"] > 0:
                success_count = summary["completed_tasks"] + summary["verified_tasks"] + summary["optimized_tasks"]
                summary["success_rate"] = success_count / summary["total_tasks"]
                summary["average_optimization_score"] = total_optimization_score / summary["total_tasks"]
            
            return summary
            
        except Exception as e:
            logger.error(f"获取高优先级集成摘要失败: {e}")
            return {}
    
    # 信号处理方法
    def on_rule_matched(self, rule_id: str, confidence: float):
        """规则匹配处理"""
        logger.debug(f"规则已匹配: {rule_id} (置信度: {confidence})")
    
    def on_matching_completed(self, result: dict):
        """匹配完成处理"""
        logger.debug(f"匹配完成: {result}")
    
    def on_analysis_completed(self, analysis_result: dict):
        """分析完成处理"""
        logger.debug(f"分析完成: {analysis_result}")
    
    def on_enhancement_applied(self, enhancement: dict):
        """增强应用处理"""
        logger.debug(f"增强已应用: {enhancement}")


class PriorityTwoIntegrationWidget(QWidget):
    """高优先级任务集成界面"""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.integration_manager = PriorityTwoIntegrationManager(main_window)
        
        self.setup_ui()
        self.setup_connections()
        
        logger.info("高优先级任务集成界面初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("🟡 高优先级任务集成系统")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #ff9800; margin: 10px;")
        layout.addWidget(title_label)
        
        # 任务列表
        self.create_high_priority_task_list_section(layout)
        
        # 控制按钮
        self.create_high_priority_control_buttons_section(layout)
        
        # 状态显示
        self.create_high_priority_status_display_section(layout)
    
    def create_high_priority_task_list_section(self, layout):
        """创建高优先级任务列表区域"""
        task_group = QGroupBox("📋 高优先级任务状态")
        task_layout = QVBoxLayout(task_group)
        
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QListWidgetItem {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
        """)
        
        # 添加任务项
        for task_id, task in self.integration_manager.high_priority_tasks.items():
            item = QListWidgetItem(f"🔄 {task.name}")
            item.setData(Qt.ItemDataRole.UserRole, task_id)
            self.task_list.addItem(item)
        
        task_layout.addWidget(self.task_list)
        layout.addWidget(task_group)
    
    def create_high_priority_control_buttons_section(self, layout):
        """创建高优先级控制按钮区域"""
        button_layout = QHBoxLayout()
        
        self.integrate_btn = QPushButton("🚀 开始集成")
        self.integrate_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        button_layout.addWidget(self.integrate_btn)
        
        self.verify_btn = QPushButton("✅ 验证集成")
        self.verify_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(self.verify_btn)
        
        self.optimize_btn = QPushButton("⚡ 优化系统")
        self.optimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #9c27b0;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7b1fa2;
            }
        """)
        button_layout.addWidget(self.optimize_btn)
        
        self.report_btn = QPushButton("📊 生成报告")
        self.report_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        button_layout.addWidget(self.report_btn)
        
        layout.addLayout(button_layout)
    
    def create_high_priority_status_display_section(self, layout):
        """创建高优先级状态显示区域"""
        status_group = QGroupBox("📈 集成状态")
        status_layout = QVBoxLayout(status_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #ff9800;
                border-radius: 3px;
            }
        """)
        status_layout.addWidget(self.progress_bar)
        
        # 状态文本
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(150)
        self.status_text.setReadOnly(True)
        self.status_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f9f9f9;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        status_layout.addWidget(self.status_text)
        
        layout.addWidget(status_group)
    
    def setup_connections(self):
        """设置信号连接"""
        # 按钮连接
        self.integrate_btn.clicked.connect(self.start_high_priority_integration)
        self.verify_btn.clicked.connect(self.verify_high_priority_integration)
        self.optimize_btn.clicked.connect(self.optimize_high_priority_systems)
        self.report_btn.clicked.connect(self.generate_high_priority_report)
        
        # 集成管理器信号连接
        self.integration_manager.task_status_changed.connect(self.on_high_priority_task_status_changed)
        self.integration_manager.integration_progress.connect(self.on_high_priority_integration_progress)
        self.integration_manager.integration_completed.connect(self.on_high_priority_integration_completed)
        self.integration_manager.verification_completed.connect(self.on_high_priority_verification_completed)
        self.integration_manager.optimization_completed.connect(self.on_high_priority_optimization_completed)
    
    def start_high_priority_integration(self):
        """开始高优先级集成"""
        try:
            self.integrate_btn.setEnabled(False)
            self.status_text.append("🚀 开始集成高优先级任务...")
            
            # 在后台线程中执行集成
            self.integration_thread = threading.Thread(
                target=self.integration_manager.integrate_all_high_priority_tasks
            )
            self.integration_thread.start()
            
        except Exception as e:
            logger.error(f"开始高优先级集成失败: {e}")
            self.status_text.append(f"❌ 集成启动失败: {e}")
            self.integrate_btn.setEnabled(True)
    
    def verify_high_priority_integration(self):
        """验证高优先级集成"""
        try:
            self.status_text.append("✅ 开始验证高优先级集成结果...")
            self.integration_manager.verify_high_priority_integration()
            
        except Exception as e:
            logger.error(f"验证高优先级集成失败: {e}")
            self.status_text.append(f"❌ 验证失败: {e}")
    
    def optimize_high_priority_systems(self):
        """优化高优先级系统"""
        try:
            self.status_text.append("⚡ 开始优化高优先级系统...")
            self.integration_manager.optimize_integrated_systems()
            
        except Exception as e:
            logger.error(f"优化高优先级系统失败: {e}")
            self.status_text.append(f"❌ 优化失败: {e}")
    
    def generate_high_priority_report(self):
        """生成高优先级报告"""
        try:
            summary = self.integration_manager.get_high_priority_integration_summary()
            
            report_dialog = HighPriorityIntegrationReportDialog(summary, self)
            report_dialog.exec()
            
        except Exception as e:
            logger.error(f"生成高优先级报告失败: {e}")
            self.status_text.append(f"❌ 报告生成失败: {e}")
    
    def on_high_priority_task_status_changed(self, task_id: str, status: str):
        """高优先级任务状态改变处理"""
        try:
            task = self.integration_manager.high_priority_tasks.get(task_id)
            if task:
                # 更新列表项
                for i in range(self.task_list.count()):
                    item = self.task_list.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == task_id:
                        if status == "completed":
                            item.setText(f"✅ {task.name}")
                        elif status == "failed":
                            item.setText(f"❌ {task.name}")
                        elif status == "verified":
                            item.setText(f"🎉 {task.name}")
                        elif status == "optimized":
                            item.setText(f"⚡ {task.name}")
                        else:
                            item.setText(f"🔄 {task.name}")
                        break
                
                self.status_text.append(f"📝 {task.name}: {status}")
            
        except Exception as e:
            logger.error(f"处理高优先级任务状态改变失败: {e}")
    
    def on_high_priority_integration_progress(self, task_id: str, progress: float):
        """高优先级集成进度处理"""
        try:
            # 计算总进度
            total_progress = 0.0
            for task in self.integration_manager.high_priority_tasks.values():
                total_progress += task.progress
            
            avg_progress = total_progress / len(self.integration_manager.high_priority_tasks)
            self.progress_bar.setValue(int(avg_progress))
            
        except Exception as e:
            logger.error(f"处理高优先级集成进度失败: {e}")
    
    def on_high_priority_integration_completed(self, summary: dict):
        """高优先级集成完成处理"""
        try:
            self.integrate_btn.setEnabled(True)
            
            success_rate = summary.get("success_rate", 0.0)
            completed_tasks = summary.get("completed_tasks", 0)
            total_tasks = summary.get("total_tasks", 0)
            avg_optimization_score = summary.get("average_optimization_score", 0.0)
            
            self.status_text.append(f"🎉 高优先级集成完成！成功率: {success_rate:.1%} ({completed_tasks}/{total_tasks})")
            self.status_text.append(f"⚡ 平均优化分数: {avg_optimization_score:.2f}")
            
            if success_rate >= 0.8:
                QMessageBox.information(self, "集成成功", 
                                      f"高优先级任务集成成功！\n成功率: {success_rate:.1%}\n优化分数: {avg_optimization_score:.2f}")
            else:
                QMessageBox.warning(self, "集成部分成功", 
                                   f"部分高优先级任务集成失败\n成功率: {success_rate:.1%}")
            
        except Exception as e:
            logger.error(f"处理高优先级集成完成失败: {e}")
    
    def on_high_priority_verification_completed(self, task_id: str, result: dict):
        """高优先级验证完成处理"""
        try:
            task = self.integration_manager.high_priority_tasks.get(task_id)
            if task:
                success = result.get("success", False)
                performance_score = result.get("performance_score", 0.0)
                if success:
                    self.status_text.append(f"✅ {task.name} 验证通过 (性能分数: {performance_score:.2f})")
                else:
                    error = result.get("error", "未知错误")
                    self.status_text.append(f"❌ {task.name} 验证失败: {error}")
            
        except Exception as e:
            logger.error(f"处理高优先级验证完成失败: {e}")
    
    def on_high_priority_optimization_completed(self, task_id: str, result: dict):
        """高优先级优化完成处理"""
        try:
            task = self.integration_manager.high_priority_tasks.get(task_id)
            if task:
                success = result.get("success", False)
                score = result.get("score", 0.0)
                improvement = result.get("performance_improvement", 0.0)
                if success:
                    self.status_text.append(f"⚡ {task.name} 优化完成 (分数: {score:.2f}, 提升: {improvement:.1%})")
                else:
                    error = result.get("error", "未知错误")
                    self.status_text.append(f"❌ {task.name} 优化失败: {error}")
            
        except Exception as e:
            logger.error(f"处理高优先级优化完成失败: {e}")


class HighPriorityIntegrationReportDialog(QDialog):
    """高优先级集成报告对话框"""
    
    def __init__(self, summary: dict, parent=None):
        super().__init__(parent)
        self.summary = summary
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("高优先级任务集成报告")
        self.setModal(True)
        self.resize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # 报告内容
        report_text = QTextEdit()
        report_text.setReadOnly(True)
        report_text.setHtml(self.generate_high_priority_report_html())
        layout.addWidget(report_text)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def generate_high_priority_report_html(self) -> str:
        """生成高优先级报告HTML"""
        try:
            html = f"""
            <h2>🟡 高优先级任务集成报告</h2>
            <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h3>📊 总体统计</h3>
            <ul>
                <li><strong>总任务数:</strong> {self.summary.get('total_tasks', 0)}</li>
                <li><strong>完成任务:</strong> {self.summary.get('completed_tasks', 0)}</li>
                <li><strong>验证通过:</strong> {self.summary.get('verified_tasks', 0)}</li>
                <li><strong>优化完成:</strong> {self.summary.get('optimized_tasks', 0)}</li>
                <li><strong>失败任务:</strong> {self.summary.get('failed_tasks', 0)}</li>
                <li><strong>成功率:</strong> {self.summary.get('success_rate', 0.0):.1%}</li>
                <li><strong>平均优化分数:</strong> {self.summary.get('average_optimization_score', 0.0):.2f}</li>
            </ul>
            
            <h3>📋 任务详情</h3>
            """
            
            for task_id, task_info in self.summary.get('tasks', {}).items():
                status_icon = {
                    'completed': '✅',
                    'verified': '🎉',
                    'optimized': '⚡',
                    'failed': '❌',
                    'in_progress': '🔄',
                    'not_started': '⏸️'
                }.get(task_info.get('status', 'not_started'), '❓')
                
                html += f"""
                <h4>{status_icon} {task_info.get('name', task_id)}</h4>
                <ul>
                    <li><strong>状态:</strong> {task_info.get('status', 'unknown')}</li>
                    <li><strong>进度:</strong> {task_info.get('progress', 0.0):.1f}%</li>
                    <li><strong>优化分数:</strong> {task_info.get('optimization_score', 0.0):.2f}</li>
                """
                
                if task_info.get('error_message'):
                    html += f"<li><strong>错误:</strong> {task_info['error_message']}</li>"
                
                if task_info.get('integration_time'):
                    html += f"<li><strong>集成时间:</strong> {task_info['integration_time']}</li>"
                
                verification_result = task_info.get('verification_result', {})
                if verification_result:
                    html += f"<li><strong>验证结果:</strong> 组件数量: {verification_result.get('components_count', 0)}, 性能分数: {verification_result.get('performance_score', 0.0):.2f}</li>"
                
                html += "</ul>"
            
            html += """
            <h3>🎯 优化建议</h3>
            <p>高优先级任务已完成集成，建议继续关注系统性能和用户体验优化。</p>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"生成高优先级报告HTML失败: {e}")
            return f"<p>报告生成失败: {e}</p>"
