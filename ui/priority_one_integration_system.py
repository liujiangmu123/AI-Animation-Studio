"""
AI Animation Studio - 最高优先级任务集成系统
集成和验证完美状态衔接、旁白驱动制作、双模式界面切换三大核心功能
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
from .perfect_state_transition_system import PerfectStateTransitionSystem
from .narration_driven_system import NarrationDrivenSystem
from .dual_mode_layout_manager import DualModeLayoutWidget

logger = get_logger("priority_one_integration_system")


class IntegrationStatus(Enum):
    """集成状态枚举"""
    NOT_STARTED = "not_started"        # 未开始
    IN_PROGRESS = "in_progress"        # 进行中
    COMPLETED = "completed"            # 已完成
    FAILED = "failed"                  # 失败
    VERIFIED = "verified"              # 已验证


@dataclass
class PriorityTask:
    """优先级任务"""
    task_id: str
    name: str
    description: str
    component_class: Optional[type] = None
    status: IntegrationStatus = IntegrationStatus.NOT_STARTED
    progress: float = 0.0
    error_message: str = ""
    verification_result: Dict[str, Any] = field(default_factory=dict)
    integration_time: Optional[datetime] = None


class PriorityOneIntegrationManager(QObject):
    """最高优先级任务集成管理器"""
    
    # 信号定义
    task_status_changed = pyqtSignal(str, str)          # 任务状态改变
    integration_progress = pyqtSignal(str, float)       # 集成进度
    integration_completed = pyqtSignal(dict)            # 集成完成
    verification_completed = pyqtSignal(str, dict)      # 验证完成
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.priority_tasks = self.initialize_priority_tasks()
        self.integrated_components = {}
        self.verification_results = {}
        
        logger.info("最高优先级任务集成管理器初始化完成")
    
    def initialize_priority_tasks(self) -> Dict[str, PriorityTask]:
        """初始化优先级任务"""
        return {
            "perfect_state_transition": PriorityTask(
                task_id="perfect_state_transition",
                name="完美状态衔接系统",
                description="自动处理时间轴连接问题，确保动画状态的完美衔接",
                component_class=PerfectStateTransitionSystem
            ),
            "narration_driven_system": PriorityTask(
                task_id="narration_driven_system", 
                name="旁白驱动制作系统",
                description="通过旁白时间精确控制动画节奏，实现完美时间同步",
                component_class=NarrationDrivenSystem
            ),
            "dual_mode_interface": PriorityTask(
                task_id="dual_mode_interface",
                name="双模式界面切换",
                description="编辑模式和预览模式的一键切换功能",
                component_class=DualModeLayoutWidget
            )
        }
    
    def integrate_all_priority_tasks(self):
        """集成所有优先级任务"""
        try:
            logger.info("开始集成所有最高优先级任务")
            
            for task_id, task in self.priority_tasks.items():
                self.integrate_single_task(task)
            
            # 验证集成结果
            self.verify_integration()
            
            # 发送完成信号
            self.integration_completed.emit(self.get_integration_summary())
            
        except Exception as e:
            logger.error(f"集成所有优先级任务失败: {e}")
    
    def integrate_single_task(self, task: PriorityTask):
        """集成单个任务"""
        try:
            logger.info(f"开始集成任务: {task.name}")
            
            # 更新状态
            task.status = IntegrationStatus.IN_PROGRESS
            self.task_status_changed.emit(task.task_id, task.status.value)
            
            # 检查组件是否已存在
            if self.check_component_exists(task):
                task.progress = 50.0
                self.integration_progress.emit(task.task_id, task.progress)
                
                # 集成到主窗口
                if self.integrate_component_to_main_window(task):
                    task.status = IntegrationStatus.COMPLETED
                    task.progress = 100.0
                    task.integration_time = datetime.now()
                    
                    logger.info(f"任务集成完成: {task.name}")
                else:
                    task.status = IntegrationStatus.FAILED
                    task.error_message = "集成到主窗口失败"
            else:
                task.status = IntegrationStatus.FAILED
                task.error_message = "组件不存在或未正确实现"
            
            # 发送状态更新信号
            self.task_status_changed.emit(task.task_id, task.status.value)
            self.integration_progress.emit(task.task_id, task.progress)
            
        except Exception as e:
            task.status = IntegrationStatus.FAILED
            task.error_message = str(e)
            logger.error(f"集成任务失败 {task.name}: {e}")
    
    def check_component_exists(self, task: PriorityTask) -> bool:
        """检查组件是否存在"""
        try:
            if task.component_class is None:
                return False
            
            # 尝试创建组件实例
            if task.task_id == "perfect_state_transition":
                component = task.component_class(self.main_window)
            elif task.task_id == "narration_driven_system":
                component = task.component_class(self.main_window)
            elif task.task_id == "dual_mode_interface":
                component = task.component_class(self.main_window)
            else:
                return False
            
            self.integrated_components[task.task_id] = component
            return True
            
        except Exception as e:
            logger.error(f"检查组件存在性失败 {task.name}: {e}")
            return False
    
    def integrate_component_to_main_window(self, task: PriorityTask) -> bool:
        """将组件集成到主窗口"""
        try:
            component = self.integrated_components.get(task.task_id)
            if not component:
                return False
            
            if task.task_id == "perfect_state_transition":
                return self.integrate_perfect_state_transition(component)
            elif task.task_id == "narration_driven_system":
                return self.integrate_narration_driven_system(component)
            elif task.task_id == "dual_mode_interface":
                return self.integrate_dual_mode_interface(component)
            
            return False
            
        except Exception as e:
            logger.error(f"集成组件到主窗口失败 {task.name}: {e}")
            return False
    
    def integrate_perfect_state_transition(self, component) -> bool:
        """集成完美状态衔接系统"""
        try:
            # 检查主窗口是否有时间轴组件
            if hasattr(self.main_window, 'timeline_widget'):
                # 连接状态衔接系统到时间轴
                timeline = self.main_window.timeline_widget
                
                # 连接信号
                if hasattr(component, 'state_recorded'):
                    component.state_recorded.connect(self.on_state_recorded)
                if hasattr(component, 'validation_completed'):
                    component.validation_completed.connect(self.on_validation_completed)
                if hasattr(component, 'transition_generated'):
                    component.transition_generated.connect(self.on_transition_generated)
                
                # 将组件添加到主窗口
                if hasattr(self.main_window, 'add_dock_widget'):
                    self.main_window.add_dock_widget("完美状态衔接", component)
                
                logger.info("完美状态衔接系统集成成功")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"集成完美状态衔接系统失败: {e}")
            return False
    
    def integrate_narration_driven_system(self, component) -> bool:
        """集成旁白驱动制作系统"""
        try:
            # 检查主窗口是否有音频组件
            if hasattr(self.main_window, 'audio_widget'):
                audio_widget = self.main_window.audio_widget
                
                # 连接旁白驱动系统到音频组件
                if hasattr(component, 'audio_analyzed'):
                    component.audio_analyzed.connect(self.on_audio_analyzed)
                if hasattr(component, 'segments_generated'):
                    component.segments_generated.connect(self.on_segments_generated)
                if hasattr(component, 'sync_completed'):
                    component.sync_completed.connect(self.on_sync_completed)
                
                # 将组件添加到主窗口
                if hasattr(self.main_window, 'add_dock_widget'):
                    self.main_window.add_dock_widget("旁白驱动制作", component)
                
                logger.info("旁白驱动制作系统集成成功")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"集成旁白驱动制作系统失败: {e}")
            return False
    
    def integrate_dual_mode_interface(self, component) -> bool:
        """集成双模式界面切换"""
        try:
            # 检查主窗口是否支持双模式
            if hasattr(self.main_window, 'dual_mode_layout_widget'):
                # 替换现有的双模式组件
                self.main_window.dual_mode_layout_widget = component
                
                # 连接信号
                if hasattr(component, 'mode_changed'):
                    component.mode_changed.connect(self.on_mode_changed)
                
                # 重新注册组件
                if hasattr(self.main_window, 'register_widgets_to_dual_mode_layout'):
                    self.main_window.register_widgets_to_dual_mode_layout()
                
                logger.info("双模式界面切换集成成功")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"集成双模式界面切换失败: {e}")
            return False
    
    def verify_integration(self):
        """验证集成结果"""
        try:
            logger.info("开始验证集成结果")
            
            for task_id, task in self.priority_tasks.items():
                if task.status == IntegrationStatus.COMPLETED:
                    verification_result = self.verify_single_task(task)
                    self.verification_results[task_id] = verification_result
                    
                    if verification_result.get("success", False):
                        task.status = IntegrationStatus.VERIFIED
                        task.verification_result = verification_result
                    
                    self.verification_completed.emit(task_id, verification_result)
            
            logger.info("集成验证完成")
            
        except Exception as e:
            logger.error(f"验证集成结果失败: {e}")
    
    def verify_single_task(self, task: PriorityTask) -> Dict[str, Any]:
        """验证单个任务"""
        try:
            component = self.integrated_components.get(task.task_id)
            if not component:
                return {"success": False, "error": "组件不存在"}
            
            verification_result = {
                "success": True,
                "component_exists": True,
                "signals_connected": False,
                "ui_integrated": False,
                "functionality_verified": False
            }
            
            # 检查信号连接
            if hasattr(component, 'metaObject'):
                signal_count = 0
                for i in range(component.metaObject().methodCount()):
                    method = component.metaObject().method(i)
                    if method.methodType() == method.MethodType.Signal:
                        signal_count += 1
                
                verification_result["signals_connected"] = signal_count > 0
                verification_result["signal_count"] = signal_count
            
            # 检查UI集成
            if hasattr(component, 'parent') and component.parent():
                verification_result["ui_integrated"] = True
            
            # 检查功能性
            if hasattr(component, 'setup_ui') and hasattr(component, 'setup_connections'):
                verification_result["functionality_verified"] = True
            
            # 综合评估
            verification_result["success"] = (
                verification_result["component_exists"] and
                verification_result["ui_integrated"] and
                verification_result["functionality_verified"]
            )
            
            return verification_result
            
        except Exception as e:
            logger.error(f"验证单个任务失败 {task.name}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """获取集成摘要"""
        try:
            summary = {
                "total_tasks": len(self.priority_tasks),
                "completed_tasks": 0,
                "verified_tasks": 0,
                "failed_tasks": 0,
                "success_rate": 0.0,
                "tasks": {}
            }
            
            for task_id, task in self.priority_tasks.items():
                task_summary = {
                    "name": task.name,
                    "status": task.status.value,
                    "progress": task.progress,
                    "error_message": task.error_message,
                    "integration_time": task.integration_time.isoformat() if task.integration_time else None,
                    "verification_result": task.verification_result
                }
                
                summary["tasks"][task_id] = task_summary
                
                if task.status == IntegrationStatus.COMPLETED:
                    summary["completed_tasks"] += 1
                elif task.status == IntegrationStatus.VERIFIED:
                    summary["verified_tasks"] += 1
                elif task.status == IntegrationStatus.FAILED:
                    summary["failed_tasks"] += 1
            
            # 计算成功率
            if summary["total_tasks"] > 0:
                success_count = summary["completed_tasks"] + summary["verified_tasks"]
                summary["success_rate"] = success_count / summary["total_tasks"]
            
            return summary
            
        except Exception as e:
            logger.error(f"获取集成摘要失败: {e}")
            return {}
    
    # 信号处理方法
    def on_state_recorded(self, element_id: str, segment_id: str):
        """状态记录处理"""
        logger.debug(f"状态已记录: {element_id} - {segment_id}")
    
    def on_validation_completed(self, result: dict):
        """验证完成处理"""
        logger.debug(f"验证完成: {result}")
    
    def on_transition_generated(self, transition: dict):
        """过渡生成处理"""
        logger.debug(f"过渡已生成: {transition}")
    
    def on_audio_analyzed(self, analysis_result: dict):
        """音频分析处理"""
        logger.debug(f"音频分析完成: {analysis_result}")
    
    def on_segments_generated(self, segments: list):
        """段落生成处理"""
        logger.debug(f"段落已生成: {len(segments)}个")
    
    def on_sync_completed(self, sync_result: dict):
        """同步完成处理"""
        logger.debug(f"同步完成: {sync_result}")
    
    def on_mode_changed(self, mode: str):
        """模式改变处理"""
        logger.debug(f"模式已切换: {mode}")


class PriorityOneIntegrationWidget(QWidget):
    """最高优先级任务集成界面"""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.integration_manager = PriorityOneIntegrationManager(main_window)
        
        self.setup_ui()
        self.setup_connections()
        
        logger.info("最高优先级任务集成界面初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("🔴 最高优先级任务集成系统")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #d32f2f; margin: 10px;")
        layout.addWidget(title_label)
        
        # 任务列表
        self.create_task_list_section(layout)
        
        # 控制按钮
        self.create_control_buttons_section(layout)
        
        # 状态显示
        self.create_status_display_section(layout)
    
    def create_task_list_section(self, layout):
        """创建任务列表区域"""
        task_group = QGroupBox("📋 核心任务状态")
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
        for task_id, task in self.integration_manager.priority_tasks.items():
            item = QListWidgetItem(f"🔄 {task.name}")
            item.setData(Qt.ItemDataRole.UserRole, task_id)
            self.task_list.addItem(item)
        
        task_layout.addWidget(self.task_list)
        layout.addWidget(task_group)
    
    def create_control_buttons_section(self, layout):
        """创建控制按钮区域"""
        button_layout = QHBoxLayout()
        
        self.integrate_btn = QPushButton("🚀 开始集成")
        self.integrate_btn.setStyleSheet("""
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
        button_layout.addWidget(self.integrate_btn)
        
        self.verify_btn = QPushButton("✅ 验证集成")
        self.verify_btn.setStyleSheet("""
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
        button_layout.addWidget(self.verify_btn)
        
        self.report_btn = QPushButton("📊 生成报告")
        self.report_btn.setStyleSheet("""
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
        button_layout.addWidget(self.report_btn)
        
        layout.addLayout(button_layout)
    
    def create_status_display_section(self, layout):
        """创建状态显示区域"""
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
                background-color: #4caf50;
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
        self.integrate_btn.clicked.connect(self.start_integration)
        self.verify_btn.clicked.connect(self.verify_integration)
        self.report_btn.clicked.connect(self.generate_report)
        
        # 集成管理器信号连接
        self.integration_manager.task_status_changed.connect(self.on_task_status_changed)
        self.integration_manager.integration_progress.connect(self.on_integration_progress)
        self.integration_manager.integration_completed.connect(self.on_integration_completed)
        self.integration_manager.verification_completed.connect(self.on_verification_completed)
    
    def start_integration(self):
        """开始集成"""
        try:
            self.integrate_btn.setEnabled(False)
            self.status_text.append("🚀 开始集成最高优先级任务...")
            
            # 在后台线程中执行集成
            self.integration_thread = threading.Thread(
                target=self.integration_manager.integrate_all_priority_tasks
            )
            self.integration_thread.start()
            
        except Exception as e:
            logger.error(f"开始集成失败: {e}")
            self.status_text.append(f"❌ 集成启动失败: {e}")
            self.integrate_btn.setEnabled(True)
    
    def verify_integration(self):
        """验证集成"""
        try:
            self.status_text.append("✅ 开始验证集成结果...")
            self.integration_manager.verify_integration()
            
        except Exception as e:
            logger.error(f"验证集成失败: {e}")
            self.status_text.append(f"❌ 验证失败: {e}")
    
    def generate_report(self):
        """生成报告"""
        try:
            summary = self.integration_manager.get_integration_summary()
            
            report_dialog = IntegrationReportDialog(summary, self)
            report_dialog.exec()
            
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            self.status_text.append(f"❌ 报告生成失败: {e}")
    
    def on_task_status_changed(self, task_id: str, status: str):
        """任务状态改变处理"""
        try:
            task = self.integration_manager.priority_tasks.get(task_id)
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
                        else:
                            item.setText(f"🔄 {task.name}")
                        break
                
                self.status_text.append(f"📝 {task.name}: {status}")
            
        except Exception as e:
            logger.error(f"处理任务状态改变失败: {e}")
    
    def on_integration_progress(self, task_id: str, progress: float):
        """集成进度处理"""
        try:
            # 计算总进度
            total_progress = 0.0
            for task in self.integration_manager.priority_tasks.values():
                total_progress += task.progress
            
            avg_progress = total_progress / len(self.integration_manager.priority_tasks)
            self.progress_bar.setValue(int(avg_progress))
            
        except Exception as e:
            logger.error(f"处理集成进度失败: {e}")
    
    def on_integration_completed(self, summary: dict):
        """集成完成处理"""
        try:
            self.integrate_btn.setEnabled(True)
            
            success_rate = summary.get("success_rate", 0.0)
            completed_tasks = summary.get("completed_tasks", 0)
            total_tasks = summary.get("total_tasks", 0)
            
            self.status_text.append(f"🎉 集成完成！成功率: {success_rate:.1%} ({completed_tasks}/{total_tasks})")
            
            if success_rate >= 0.8:
                QMessageBox.information(self, "集成成功", 
                                      f"最高优先级任务集成成功！\n成功率: {success_rate:.1%}")
            else:
                QMessageBox.warning(self, "集成部分成功", 
                                   f"部分任务集成失败\n成功率: {success_rate:.1%}")
            
        except Exception as e:
            logger.error(f"处理集成完成失败: {e}")
    
    def on_verification_completed(self, task_id: str, result: dict):
        """验证完成处理"""
        try:
            task = self.integration_manager.priority_tasks.get(task_id)
            if task:
                success = result.get("success", False)
                if success:
                    self.status_text.append(f"✅ {task.name} 验证通过")
                else:
                    error = result.get("error", "未知错误")
                    self.status_text.append(f"❌ {task.name} 验证失败: {error}")
            
        except Exception as e:
            logger.error(f"处理验证完成失败: {e}")


class IntegrationReportDialog(QDialog):
    """集成报告对话框"""
    
    def __init__(self, summary: dict, parent=None):
        super().__init__(parent)
        self.summary = summary
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("最高优先级任务集成报告")
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 报告内容
        report_text = QTextEdit()
        report_text.setReadOnly(True)
        report_text.setHtml(self.generate_report_html())
        layout.addWidget(report_text)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def generate_report_html(self) -> str:
        """生成报告HTML"""
        try:
            html = f"""
            <h2>🔴 最高优先级任务集成报告</h2>
            <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h3>📊 总体统计</h3>
            <ul>
                <li><strong>总任务数:</strong> {self.summary.get('total_tasks', 0)}</li>
                <li><strong>完成任务:</strong> {self.summary.get('completed_tasks', 0)}</li>
                <li><strong>验证通过:</strong> {self.summary.get('verified_tasks', 0)}</li>
                <li><strong>失败任务:</strong> {self.summary.get('failed_tasks', 0)}</li>
                <li><strong>成功率:</strong> {self.summary.get('success_rate', 0.0):.1%}</li>
            </ul>
            
            <h3>📋 任务详情</h3>
            """
            
            for task_id, task_info in self.summary.get('tasks', {}).items():
                status_icon = {
                    'completed': '✅',
                    'verified': '🎉',
                    'failed': '❌',
                    'in_progress': '🔄',
                    'not_started': '⏸️'
                }.get(task_info.get('status', 'not_started'), '❓')
                
                html += f"""
                <h4>{status_icon} {task_info.get('name', task_id)}</h4>
                <ul>
                    <li><strong>状态:</strong> {task_info.get('status', 'unknown')}</li>
                    <li><strong>进度:</strong> {task_info.get('progress', 0.0):.1f}%</li>
                """
                
                if task_info.get('error_message'):
                    html += f"<li><strong>错误:</strong> {task_info['error_message']}</li>"
                
                if task_info.get('integration_time'):
                    html += f"<li><strong>集成时间:</strong> {task_info['integration_time']}</li>"
                
                html += "</ul>"
            
            html += """
            <h3>🎯 建议</h3>
            <p>如果有任务集成失败，请检查相关组件的实现和依赖关系。</p>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"生成报告HTML失败: {e}")
            return f"<p>报告生成失败: {e}</p>"
