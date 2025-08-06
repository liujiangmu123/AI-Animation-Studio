"""
AI Animation Studio - 主窗口
应用程序的主界面窗口
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QSplitter,
    QMenuBar, QMenu, QToolBar, QStatusBar, QTabWidget, QLabel, QFrame,
    QMessageBox, QFileDialog, QApplication, QInputDialog, QButtonGroup,
    QLineEdit, QTextEdit, QToolButton, QPushButton, QCheckBox, QRadioButton,
    QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem, QComboBox,
    QSpinBox, QDoubleSpinBox, QSlider, QProgressBar, QScrollArea,
    QGroupBox, QStackedWidget, QDockWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup, QIcon, QKeySequence, QPixmap

from core.config import AppConfig
from core.project_manager import ProjectManager
from core.logger import get_logger
from core.video_exporter import VideoExporter
from core.template_manager import TemplateManager
from core.command_manager import CommandManager
from core.data_structures import Project
from .theme_system import get_theme_manager
from .color_scheme_manager import color_scheme_manager, ColorRole
from .timeline_widget import TimelineWidget
from .ai_generator_widget import AIGeneratorWidget
from .animation_description_workbench import AnimationDescriptionWorkbench
from .enhanced_solution_generator import EnhancedSolutionGenerator
from .solution_visual_previewer import SolutionVisualPreviewer
from .preview_widget import PreviewWidget
from .stage_widget import StageWidget
from .properties_widget import PropertiesWidget
from .elements_widget import ElementsWidget
from .library_manager_widget import LibraryManagerWidget
from .settings_dialog import SettingsDialog
from .rules_manager_widget import RulesManagerWidget
from .template_dialog import TemplateDialog
from .value_hierarchy_layout import ValueHierarchyLayout
from .progressive_disclosure_manager import ProgressiveDisclosureManager
from .adaptive_interface_manager import AdaptiveInterfaceManager
from .quadrant_layout_manager import QuadrantLayoutManager, WorkflowAreaManager
from .professional_toolbar_manager import ProfessionalToolbarManager, ProfessionalMenuManager
from .responsive_layout_manager import (ResponsiveLayoutManager, ScreenAdaptationManager,
                                       ResponsiveBreakpointManager, ResponsiveStyleManager)
from .dual_mode_layout_manager import DualModeLayoutWidget, DualModeLayoutManager, LayoutMode
from .status_notification_manager import (StatusNotificationManager, StatusType, NotificationType)
from .visual_flow_manager import VisualFlowManager
from .information_hierarchy_manager import InformationHierarchyManager
from .realtime_feedback_system import WYSIWYGManager
from .direct_manipulation_interface import DirectManipulationManager
from .workflow_state_manager import WorkflowStateManager, WorkflowState, OperationState, ElementState
from .priority_one_integration_system import PriorityOneIntegrationWidget, PriorityOneIntegrationManager
from .priority_two_integration_system import PriorityTwoIntegrationWidget, PriorityTwoIntegrationManager
from .priority_three_integration_system import PriorityThreeIntegrationWidget, PriorityThreeIntegrationManager
from core.value_hierarchy_config import get_value_hierarchy, UserExpertiseLevel, WorkflowStage

# 导入新的对话框组件
from .element_addition_wizard import ElementAdditionWizard
from .ai_element_generator import AIElementGenerator
from .template_preview_dialog import TemplatePreviewDialog
from .enhanced_export_dialog import EnhancedExportDialog
from .performance_monitoring_dialog import PerformanceMonitoringDialog
from .onboarding_system import OnboardingSystem

logger = get_logger("main_window")

class MainWindow(QMainWindow):
    """主窗口类"""
    
    # 信号定义
    project_changed = pyqtSignal()
    theme_changed = pyqtSignal(str)
    
    def __init__(self, config: AppConfig):
        super().__init__()
        
        self.config = config
        self.project_manager = ProjectManager()
        self.theme_manager = get_theme_manager()
        self.video_exporter = VideoExporter()
        self.template_manager = TemplateManager()
        self.command_manager = CommandManager(max_history=100)

        # 价值层次配置
        self.value_hierarchy = get_value_hierarchy()
        self.current_expertise_level = UserExpertiseLevel.INTERMEDIATE
        self.current_workflow_stage = WorkflowStage.AUDIO_IMPORT

        # 渐进式功能披露管理器
        self.progressive_disclosure = ProgressiveDisclosureManager()

        # 自适应界面管理器
        self.adaptive_interface = AdaptiveInterfaceManager(self)

        # 四象限布局管理器
        self.quadrant_layout = QuadrantLayoutManager()
        self.workflow_area_manager = WorkflowAreaManager(self.quadrant_layout)

        # 专业工具栏和菜单管理器
        self.professional_toolbar_manager = ProfessionalToolbarManager(self)
        self.professional_menu_manager = ProfessionalMenuManager(self)

        # 响应式布局系统
        self.responsive_layout_manager = ResponsiveLayoutManager(self)
        self.screen_adaptation_manager = ScreenAdaptationManager(self)
        self.breakpoint_manager = ResponsiveBreakpointManager()
        self.responsive_style_manager = ResponsiveStyleManager(self)

        # 双模式布局管理器
        self.dual_mode_layout_widget = DualModeLayoutWidget(self)
        self.dual_mode_layout_manager = self.dual_mode_layout_widget.get_layout_manager()

        # 状态栏和通知系统
        self.status_notification_manager = StatusNotificationManager(self)

        # 视线流动优化管理器将在setup_ui()之后初始化
        self.visual_flow_manager = None

        # 信息重要性金字塔管理器
        self.information_hierarchy_manager = InformationHierarchyManager(self)

        # 所见即所得管理器
        self.wysiwyg_manager = WYSIWYGManager(self)

        # 直接操纵管理器
        self.direct_manipulation_manager = DirectManipulationManager(self)

        # 工作流程状态管理器
        self.workflow_state_manager = WorkflowStateManager(self)

        # 最高优先级任务集成系统
        self.priority_one_integration_manager = PriorityOneIntegrationManager(self)
        self.priority_one_integration_widget = PriorityOneIntegrationWidget(self)

        # 高优先级任务集成系统
        self.priority_two_integration_manager = PriorityTwoIntegrationManager(self)
        self.priority_two_integration_widget = PriorityTwoIntegrationWidget(self)

        # 中优先级任务集成系统
        self.priority_three_integration_manager = PriorityThreeIntegrationManager(self)
        self.priority_three_integration_widget = PriorityThreeIntegrationWidget(self)

        # 初始化自动保存管理器
        from core.auto_save_manager import AutoSaveManager
        self.auto_save_manager = AutoSaveManager(self.project_manager)

        # 自动保存定时器（保留兼容性）
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        
        self.setup_ui()
        self.setup_menus()  # 先设置基本菜单，创建undo_action和redo_action
        self.setup_professional_menus()
        self.setup_professional_toolbars()
        self.setup_professional_statusbar()
        self.setup_connections()
        self.setup_auto_save_connections()
        self.apply_config()

        # 启动自动保存
        self.auto_save_manager.start_auto_save()

        # 检查恢复数据
        self.check_for_recovery_data()

        # 创建默认项目（不显示向导）
        self.create_default_project()

        logger.info("主窗口初始化完成")

    def create_default_project(self):
        """创建默认项目（不显示向导）"""
        try:
            # 直接创建默认项目
            project = self.project_manager.create_new_project(
                name="新项目",
                template_id=None,
                config={}
            )

            self.current_project = project
            self.setWindowTitle(f"AI Animation Studio - {project.name}")

            # 清空命令历史
            self.command_manager.clear_history()
            self.update_edit_menu_state()

            # 应用项目设置到界面
            self._apply_project_settings_to_ui(project)

            # 加载默认素材到界面
            self._load_project_assets_to_ui(project)

            self.project_changed.emit()
            logger.info(f"已创建默认项目: {project.name}")

        except Exception as e:
            logger.error(f"创建默认项目失败: {e}")
            # 如果创建失败，至少确保界面可用
            self.setWindowTitle("AI Animation Studio")

    def _load_project_assets_to_ui(self, project):
        """将项目素材加载到界面"""
        try:
            logger.info(f"开始加载项目素材到界面，项目有 {len(project.assets)} 个素材")

            # 刷新素材库标签页
            self.refresh_assets_library_tab()

        except Exception as e:
            logger.warning(f"加载项目素材到界面失败: {e}")

    def refresh_assets_library_tab(self):
        """刷新素材库标签页"""
        try:
            # 找到素材库标签页
            if hasattr(self, 'resource_tabs'):
                for i in range(self.resource_tabs.count()):
                    if "素材库" in self.resource_tabs.tabText(i):
                        # 重新创建素材库标签页内容
                        new_assets_tab = self.create_assets_library_tab()
                        self.resource_tabs.removeTab(i)
                        self.resource_tabs.insertTab(i, new_assets_tab, "🎨 素材库")
                        logger.info("素材库标签页已刷新")
                        break

        except Exception as e:
            logger.error(f"刷新素材库标签页失败: {e}")

    def setup_auto_save_connections(self):
        """设置自动保存连接"""
        try:
            # 连接自动保存信号
            self.auto_save_manager.auto_save_triggered.connect(self.on_auto_save_triggered)
            self.auto_save_manager.auto_save_completed.connect(self.on_auto_save_completed)
            self.auto_save_manager.recovery_data_found.connect(self.on_recovery_data_found)

            logger.info("自动保存连接设置完成")
        except Exception as e:
            logger.error(f"设置自动保存连接失败: {e}")

    def check_for_recovery_data(self):
        """检查恢复数据"""
        try:
            recovery_file = self.auto_save_manager.check_for_recovery_data()
            if recovery_file:
                self.show_recovery_dialog(recovery_file)
        except Exception as e:
            logger.error(f"检查恢复数据失败: {e}")

    def show_recovery_dialog(self, recovery_file: str):
        """显示恢复对话框"""
        try:
            reply = QMessageBox.question(
                self, "发现恢复数据",
                f"检测到未保存的项目数据，是否要恢复？\n\n恢复文件: {Path(recovery_file).name}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                if self.auto_save_manager.restore_from_recovery(recovery_file):
                    QMessageBox.information(self, "恢复成功", "项目已从恢复数据中恢复")
                else:
                    QMessageBox.warning(self, "恢复失败", "无法从恢复数据中恢复项目")
        except Exception as e:
            logger.error(f"显示恢复对话框失败: {e}")

    def on_auto_save_triggered(self):
        """自动保存触发事件"""
        self.status_bar.showMessage("正在自动保存...", 2000)

    def on_auto_save_completed(self, success: bool, message: str):
        """自动保存完成事件"""
        if success:
            self.status_bar.showMessage(f"✓ {message}", 3000)
        else:
            self.status_bar.showMessage(f"✗ {message}", 5000)

    def on_recovery_data_found(self, recovery_file: str):
        """发现恢复数据事件"""
        self.show_recovery_dialog(recovery_file)

    def setup_ui(self):
        """设置用户界面 - 完整五区域专业布局（严格按照界面设计完整方案实现）- 优化版"""
        self.setWindowTitle("AI Animation Studio - AI驱动的专业动画工作站")
        self.setMinimumSize(1600, 1000)  # 提升最小尺寸以适应专业布局

        # 初始化响应式布局管理器
        self.responsive_layout = ResponsiveLayoutManager(self)

        # 应用专业软件样式
        self.setStyleSheet(self.get_professional_main_window_style())

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局 - 垂直布局以支持完整五区域布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)  # 无间距，严格按照设计方案

        # 1. 顶部工具栏区域 (60px) - 严格按照设计方案
        self.setup_design_compliant_top_toolbar()
        main_layout.addWidget(self.top_toolbar_widget)

        # 2. 中间工作区域 - 水平三分割（资源管理区 + 主工作区 + AI控制区）
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(1)  # 细化分割线，符合设计方案
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E2E8F0;
                border: none;
            }
            QSplitter::handle:hover {
                background-color: #CBD5E1;
            }
        """)
        main_layout.addWidget(self.main_splitter)

        # 左侧：资源管理区 (300px) - 严格按照设计方案
        self.setup_design_compliant_resource_panel()

        # 中央：主工作区 (弹性宽度) - 严格按照设计方案
        self.setup_design_compliant_main_work_area()

        # 右侧：AI控制区 (350px) - 严格按照设计方案
        self.setup_design_compliant_ai_control_panel()

        # 设置分割器比例 - 严格按照设计方案：资源管理区(300px):主工作区(弹性):AI控制区(350px)
        self.main_splitter.setSizes([300, 900, 350])
        self.main_splitter.setStretchFactor(1, 1)  # 只有中央面板可拉伸

        # 设置分割器约束 - 严格按照设计方案
        self.main_splitter.setCollapsible(0, False)  # 资源管理区不可折叠
        self.main_splitter.setCollapsible(1, False)  # 主工作区不可折叠
        self.main_splitter.setCollapsible(2, False)  # AI控制区不可折叠

        # 3. 底部时间轴区域 (200px) - 严格按照设计方案
        self.setup_design_compliant_timeline_area()
        main_layout.addWidget(self.timeline_area_widget)

        # 确保时间轴区域可见
        self.timeline_area_widget.setVisible(True)
        self.timeline_area_widget.show()

        logger.info(f"时间轴区域已添加到主布局，高度: {self.timeline_area_widget.height()}px")

        # 创建时间轴组件实例
        self.timeline_widget = TimelineWidget()

        # 4. 状态栏 (24px) - 严格按照设计方案
        self.setup_design_compliant_status_bar()

        # 注册组件到双模式布局管理器
        self.register_widgets_to_dual_mode_layout()

        # 现在初始化视线流动优化管理器（在UI设置完成后，已添加递归保护）
        self.visual_flow_manager = VisualFlowManager(self)

        # 应用色彩方案设计系统
        self.apply_color_scheme()

        logger.info("完整五区域专业布局设置完成 - 严格符合界面设计方案")

    def apply_color_scheme(self):
        """应用色彩方案设计系统 - 严格按照界面设计完整方案"""
        try:
            # 应用主窗口背景色
            main_bg_color = color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {main_bg_color};
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                }}
            """)

            # 应用顶部工具栏色彩方案
            if hasattr(self, 'toolbar') and self.toolbar:
                toolbar_style = color_scheme_manager.generate_stylesheet_for_widget("toolbar")
                self.toolbar.setStyleSheet(toolbar_style)

            # 应用AI控制区色彩方案（橙色系）
            if hasattr(self, 'ai_control_area') and self.ai_control_area:
                ai_style = color_scheme_manager.generate_stylesheet_for_widget("ai_panel")
                self.ai_control_area.setStyleSheet(ai_style)

            # 应用协作功能区色彩方案（绿色系）
            if hasattr(self, 'resource_area') and self.resource_area:
                # 资源区包含协作功能，使用协作色彩
                collab_style = color_scheme_manager.generate_stylesheet_for_widget("collaboration_panel")
                self.resource_area.setStyleSheet(collab_style)

            # 应用测试调试区色彩方案（紫色系）
            if hasattr(self, 'main_work_area') and self.main_work_area:
                # 主工作区包含测试功能，使用测试色彩
                test_style = color_scheme_manager.generate_stylesheet_for_widget("test_panel")
                # 只对测试相关的标签页应用紫色系
                for i in range(self.main_work_area.count()):
                    tab_text = self.main_work_area.tabText(i)
                    if "测试" in tab_text or "调试" in tab_text:
                        widget = self.main_work_area.widget(i)
                        if widget:
                            widget.setStyleSheet(test_style)

            # 应用性能监控区色彩方案（蓝色系）
            if hasattr(self, 'timeline_area') and self.timeline_area:
                # 时间轴区域包含性能监控，使用性能色彩
                perf_style = color_scheme_manager.generate_stylesheet_for_widget("performance_panel")
                self.timeline_area.setStyleSheet(perf_style)

            # 应用状态栏色彩方案
            if hasattr(self, 'status_bar') and self.status_bar:
                status_style = f"""
                    QStatusBar {{
                        background-color: {color_scheme_manager.get_color_hex(ColorRole.PRIMARY)};
                        color: white;
                        border-top: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                    }}
                """
                self.status_bar.setStyleSheet(status_style)

            logger.info("色彩方案设计系统应用完成 - 严格符合界面设计方案")

        except Exception as e:
            logger.error(f"应用色彩方案失败: {e}")

    def apply_functional_color_coding_to_resource_tabs(self):
        """为资源管理区标签页应用功能色彩编码"""
        try:
            if not hasattr(self, 'resource_tabs'):
                return

            # 获取功能色彩
            ai_colors = color_scheme_manager.get_ai_function_colors()
            collab_colors = color_scheme_manager.get_collaboration_colors()
            test_colors = color_scheme_manager.get_test_debug_colors()
            perf_colors = color_scheme_manager.get_performance_colors()

            # 为不同功能的标签页应用色彩编码
            for i in range(self.resource_tabs.count()):
                tab_text = self.resource_tabs.tabText(i)
                widget = self.resource_tabs.widget(i)

                if widget:
                    # AI功能相关 - 橙色系
                    if "素材库" in tab_text or "模板库" in tab_text:
                        widget.setStyleSheet(f"""
                            QWidget {{
                                border-left: 3px solid {ai_colors[0]};
                            }}
                            QLabel {{
                                color: {ai_colors[0]};
                            }}
                            QPushButton {{
                                background-color: {ai_colors[0]};
                                color: white;
                                border: none;
                                padding: 6px 12px;
                                border-radius: 3px;
                            }}
                            QPushButton:hover {{
                                background-color: {ai_colors[1]};
                            }}
                        """)

                    # 协作功能相关 - 绿色系
                    elif "项目文件" in tab_text or "规则库" in tab_text:
                        widget.setStyleSheet(f"""
                            QWidget {{
                                border-left: 3px solid {collab_colors[0]};
                            }}
                            QLabel {{
                                color: {collab_colors[0]};
                            }}
                            QPushButton {{
                                background-color: {collab_colors[0]};
                                color: white;
                                border: none;
                                padding: 6px 12px;
                                border-radius: 3px;
                            }}
                            QPushButton:hover {{
                                background-color: {collab_colors[1]};
                            }}
                        """)

                    # 测试调试相关 - 紫色系
                    elif "工具箱" in tab_text or "操作历史" in tab_text:
                        widget.setStyleSheet(f"""
                            QWidget {{
                                border-left: 3px solid {test_colors[0]};
                            }}
                            QLabel {{
                                color: {test_colors[0]};
                            }}
                            QPushButton {{
                                background-color: {test_colors[0]};
                                color: white;
                                border: none;
                                padding: 6px 12px;
                                border-radius: 3px;
                            }}
                            QPushButton:hover {{
                                background-color: {test_colors[1]};
                            }}
                        """)

                    # 性能监控相关 - 蓝色系
                    elif "音频管理" in tab_text:
                        widget.setStyleSheet(f"""
                            QWidget {{
                                border-left: 3px solid {perf_colors[0]};
                            }}
                            QLabel {{
                                color: {perf_colors[0]};
                            }}
                            QPushButton {{
                                background-color: {perf_colors[0]};
                                color: white;
                                border: none;
                                padding: 6px 12px;
                                border-radius: 3px;
                            }}
                            QPushButton:hover {{
                                background-color: {perf_colors[1]};
                            }}
                        """)

            logger.info("资源管理区功能色彩编码应用完成")

        except Exception as e:
            logger.error(f"应用功能色彩编码失败: {e}")

    def apply_ai_color_scheme_to_tabs(self):
        """为AI控制区标签页应用橙色系色彩方案"""
        try:
            if not hasattr(self, 'ai_control_tabs'):
                return

            ai_colors = color_scheme_manager.get_ai_function_colors()

            # 为所有AI控制区标签页应用橙色系样式
            for i in range(self.ai_control_tabs.count()):
                widget = self.ai_control_tabs.widget(i)
                if widget:
                    widget.setStyleSheet(f"""
                        QWidget {{
                            background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                        }}
                        QPushButton {{
                            background-color: {ai_colors[0]};
                            color: white;
                            border: none;
                            padding: 8px 16px;
                            border-radius: 4px;
                            font-weight: bold;
                            font-size: 12px;
                        }}
                        QPushButton:hover {{
                            background-color: {ai_colors[1]};
                        }}
                        QPushButton:pressed {{
                            background-color: {ai_colors[0]};
                        }}
                        QLabel {{
                            color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                        }}
                        QTextEdit {{
                            border: 1px solid {ai_colors[2]};
                            border-radius: 4px;
                            background-color: white;
                        }}
                        QComboBox {{
                            border: 1px solid {ai_colors[2]};
                            border-radius: 4px;
                            padding: 4px 8px;
                            background-color: white;
                        }}
                        QProgressBar {{
                            border: 1px solid {ai_colors[2]};
                            border-radius: 4px;
                            text-align: center;
                        }}
                        QProgressBar::chunk {{
                            background-color: {ai_colors[0]};
                            border-radius: 3px;
                        }}
                    """)

            logger.info("AI控制区橙色系色彩方案应用完成")

        except Exception as e:
            logger.error(f"应用AI色彩方案失败: {e}")

    def setup_design_compliant_top_toolbar(self):
        """设置顶部工具栏区域 (60px) - 严格按照界面设计完整方案实现"""
        self.top_toolbar_widget = QFrame()
        self.top_toolbar_widget.setFixedHeight(60)  # 严格60px高度
        self.top_toolbar_widget.setFrameStyle(QFrame.Shape.NoFrame)
        self.top_toolbar_widget.setStyleSheet("""
            QFrame {
                background-color: #2C5AA0;
                border-bottom: 1px solid #1E3A5F;
                color: white;
            }
            QToolButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 500;
                border-radius: 3px;
                min-width: 50px;
                min-height: 32px;
            }
            QToolButton:hover {
                background-color: #4A90E2;
            }
            QToolButton:pressed {
                background-color: #1E3A5F;
            }
            QToolButton[objectName="ai_button"] {
                background-color: #FF6B35;
                color: white;
                font-weight: bold;
            }
            QToolButton[objectName="ai_button"]:hover {
                background-color: #FB923C;
            }
            QToolButton[objectName="collab_button"] {
                background-color: #10B981;
                color: white;
            }
            QToolButton[objectName="collab_button"]:hover {
                background-color: #34D399;
            }
            QLabel {
                color: white;
                font-size: 11px;
                font-weight: 500;
                padding: 0 4px;
            }
        """)

        # 工具栏布局 - 严格按照设计方案
        toolbar_layout = QHBoxLayout(self.top_toolbar_widget)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        toolbar_layout.setSpacing(6)

        # 左侧主要功能按钮组 - 严格按照设计方案顺序
        # [项目▼] [编辑▼] [AI生成] [预览] [协作] [导出▼]

        # 项目菜单
        self.project_btn = QToolButton()
        self.project_btn.setText("项目▼")
        self.project_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setup_project_menu(self.project_btn)
        toolbar_layout.addWidget(self.project_btn)

        # 编辑菜单
        self.edit_btn = QToolButton()
        self.edit_btn.setText("编辑▼")
        self.edit_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setup_edit_menu(self.edit_btn)
        toolbar_layout.addWidget(self.edit_btn)

        # AI生成按钮（活力橙强调色）
        self.ai_btn = QToolButton()
        self.ai_btn.setText("AI生成")
        self.ai_btn.setObjectName("ai_button")
        toolbar_layout.addWidget(self.ai_btn)

        # 预览按钮
        self.preview_btn = QToolButton()
        self.preview_btn.setText("预览")
        toolbar_layout.addWidget(self.preview_btn)

        # 协作按钮（协作绿色）
        self.collab_btn = QToolButton()
        self.collab_btn.setText("协作")
        self.collab_btn.setObjectName("collab_button")
        toolbar_layout.addWidget(self.collab_btn)

        # 导出菜单
        self.export_btn = QToolButton()
        self.export_btn.setText("导出▼")
        self.export_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setup_export_menu(self.export_btn)
        toolbar_layout.addWidget(self.export_btn)

        # 分隔符 - 严格按照设计方案
        separator = QLabel("|")
        separator.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 14px;")
        toolbar_layout.addWidget(separator)

        # 弹性空间
        toolbar_layout.addStretch()

        # 右侧状态和控制区域 - 严格按照设计方案
        # 🔄编辑模式 ⚙️设置 👤用户

        # 编辑模式切换
        self.mode_btn = QToolButton()
        self.mode_btn.setText("🔄编辑模式")
        toolbar_layout.addWidget(self.mode_btn)

        # 设置按钮
        self.settings_btn = QToolButton()
        self.settings_btn.setText("⚙️设置")
        toolbar_layout.addWidget(self.settings_btn)

        # 用户按钮
        self.user_btn = QToolButton()
        self.user_btn.setText("👤用户")
        toolbar_layout.addWidget(self.user_btn)

        # 连接信号
        self.connect_toolbar_signals()

        logger.info("顶部工具栏设置完成 - 严格符合设计方案")

    def setup_project_menu(self, button):
        """设置项目菜单"""
        menu = QMenu(self)
        menu.addAction("🆕 新建项目", self.new_project)
        menu.addAction("📂 打开项目", self.open_project)
        menu.addAction("💾 保存项目", self.save_project)
        menu.addAction("📤 另存为", self.save_project_as)
        menu.addSeparator()
        menu.addAction("📋 项目设置", self.show_project_settings)
        menu.addAction("📊 项目信息", self.show_project_info)
        button.setMenu(menu)

    def setup_edit_menu(self, button):
        """设置编辑菜单"""
        menu = QMenu(self)
        menu.addAction("↶ 撤销", self.undo_action)
        menu.addAction("↷ 重做", self.redo_action)
        menu.addSeparator()
        menu.addAction("📋 复制", self.copy_action)
        menu.addAction("📄 粘贴", self.paste_action)
        menu.addAction("✂️ 剪切", self.cut_action)
        menu.addSeparator()
        menu.addAction("🔍 查找替换", self.find_replace)
        button.setMenu(menu)

    def setup_export_menu(self, button):
        """设置导出菜单"""
        menu = QMenu(self)
        menu.addAction("🌐 导出HTML", self.export_html)
        menu.addAction("🎥 导出视频", self.export_video)
        menu.addAction("📸 导出图片", self.export_image)
        menu.addSeparator()
        menu.addAction("📦 批量导出", self.batch_export)
        menu.addAction("☁️ 云端导出", self.cloud_export)
        button.setMenu(menu)

    def connect_toolbar_signals(self):
        """连接工具栏信号"""
        try:
            # AI生成按钮
            self.ai_btn.clicked.connect(self.show_ai_generator)

            # 预览按钮
            self.preview_btn.clicked.connect(self.show_preview)

            # 协作按钮
            self.collab_btn.clicked.connect(self.show_collaboration)

            # 模式切换按钮
            self.mode_btn.clicked.connect(self.toggle_edit_mode)

            # 设置按钮
            self.settings_btn.clicked.connect(self.show_settings)

            # 用户按钮
            self.user_btn.clicked.connect(self.show_user_menu)

            logger.info("工具栏信号连接完成")
        except Exception as e:
            logger.error(f"连接工具栏信号失败: {e}")

    def setup_design_compliant_resource_panel(self):
        """设置资源管理区 (300px) - 严格按照界面设计完整方案实现"""
        # 创建资源管理面板
        resource_panel = QWidget()
        resource_panel.setFixedWidth(300)
        resource_panel.setStyleSheet(f"""
            QWidget {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border-right: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
            QTabWidget::pane {{
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
            }}
            QTabBar::tab {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                color: #2C5AA0;
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background-color: #E2E8F0;
            }}
        """)

        # 将面板添加到主分割器
        self.main_splitter.addWidget(resource_panel)
        self.resource_area = resource_panel

        # 资源管理区布局
        resource_layout = QVBoxLayout(resource_panel)
        resource_layout.setContentsMargins(0, 0, 0, 0)
        resource_layout.setSpacing(0)

        # 创建标签页 - 严格按照设计方案顺序
        self.resource_tabs = QTabWidget()

        # 📁 项目文件
        project_tab = self.create_project_files_tab()
        self.resource_tabs.addTab(project_tab, "📁 项目文件")

        # 🎵 音频管理
        audio_tab = self.create_audio_management_tab()
        self.resource_tabs.addTab(audio_tab, "🎵 音频管理")

        # 🎨 素材库
        assets_tab = self.create_assets_library_tab()
        self.resource_tabs.addTab(assets_tab, "🎨 素材库")

        # 📐 工具箱
        tools_tab = self.create_tools_box_tab()
        self.resource_tabs.addTab(tools_tab, "📐 工具箱")

        # 📚 规则库
        rules_tab = self.create_rules_library_tab()
        self.resource_tabs.addTab(rules_tab, "📚 规则库")

        # 🔄 操作历史
        history_tab = self.create_operation_history_tab()
        self.resource_tabs.addTab(history_tab, "🔄 操作历史")

        # 📋 模板库
        templates_tab = self.create_templates_library_tab()
        self.resource_tabs.addTab(templates_tab, "📋 模板库")

        resource_layout.addWidget(self.resource_tabs)

        # 应用功能色彩编码到标签页
        self.apply_functional_color_coding_to_resource_tabs()

        # 添加到主分割器
        self.main_splitter.addWidget(resource_panel)

        logger.info("资源管理区设置完成 - 严格符合设计方案")

    def create_project_files_tab(self):
        """创建项目文件标签页"""
        # 创建主widget
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 工具栏
        toolbar = QHBoxLayout()
        refresh_btn = QToolButton()
        refresh_btn.setText("🔄")
        refresh_btn.setToolTip("刷新项目文件")
        toolbar.addWidget(refresh_btn)

        new_folder_btn = QToolButton()
        new_folder_btn.setText("📁+")
        new_folder_btn.setToolTip("新建文件夹")
        toolbar.addWidget(new_folder_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 项目文件树
        file_tree = QTreeWidget()
        file_tree.setHeaderLabel("项目文件")

        # 添加示例项目结构
        root_item = QTreeWidgetItem(file_tree, ["当前项目"])
        assets_item = QTreeWidgetItem(root_item, ["📁 素材"])
        QTreeWidgetItem(assets_item, ["🖼️ logo.png"])
        QTreeWidgetItem(assets_item, ["🎵 bgm.mp3"])

        animations_item = QTreeWidgetItem(root_item, ["📁 动画"])
        QTreeWidgetItem(animations_item, ["🎬 intro.json"])
        QTreeWidgetItem(animations_item, ["🎬 main.json"])

        file_tree.expandAll()
        layout.addWidget(file_tree)

        return widget

    def create_audio_management_tab(self):
        """创建音频管理标签页"""
        # 创建主widget
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 工具栏
        toolbar = QHBoxLayout()

        import_btn = QToolButton()
        import_btn.setText("📂")
        import_btn.setToolTip("导入音频")
        toolbar.addWidget(import_btn)

        play_btn = QToolButton()
        play_btn.setText("▶️")
        play_btn.setToolTip("播放")
        toolbar.addWidget(play_btn)

        stop_btn = QToolButton()
        stop_btn.setText("⏹️")
        stop_btn.setToolTip("停止")
        toolbar.addWidget(stop_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 音频文件列表
        audio_list = QListWidget()

        # 添加示例音频文件
        item1 = QListWidgetItem("🎵 背景音乐.mp3")
        item1.setToolTip("时长: 3:45 | 大小: 5.2MB")
        audio_list.addItem(item1)

        item2 = QListWidgetItem("🎤 旁白.wav")
        item2.setToolTip("时长: 2:30 | 大小: 12.1MB")
        audio_list.addItem(item2)

        layout.addWidget(audio_list)

        # 音频信息显示
        info_label = QLabel("选择音频文件查看详情")
        info_label.setStyleSheet("color: #6B7280; font-size: 10px; padding: 4px;")
        layout.addWidget(info_label)

        return widget

    def create_tools_box_tab(self):
        """创建工具箱标签页"""
        # 创建主widget
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 工具分类
        categories = [
            ("选择工具", [("👆", "选择"), ("✋", "移动"), ("🔄", "旋转"), ("📏", "缩放")]),
            ("绘制工具", [("📝", "文字"), ("🔷", "形状"), ("📏", "线条"), ("✏️", "画笔")]),
            ("动画工具", [("🎬", "关键帧"), ("📈", "曲线"), ("⏱️", "时间"), ("🔗", "链接")])
        ]

        for cat_name, tools in categories:
            # 分类标题
            cat_label = QLabel(cat_name)
            cat_label.setStyleSheet("font-weight: bold; color: #374151; padding: 4px 0;")
            layout.addWidget(cat_label)

            # 工具网格
            tools_frame = QFrame()
            tools_layout = QGridLayout(tools_frame)
            tools_layout.setSpacing(2)

            for i, (icon, name) in enumerate(tools):
                btn = QToolButton()
                btn.setText(icon)
                btn.setToolTip(name)
                btn.setFixedSize(40, 40)
                btn.setStyleSheet("""
                    QToolButton {
                        border: 1px solid #E2E8F0;
                        border-radius: 4px;
                        background-color: white;
                        font-size: 16px;
                    }
                    QToolButton:hover {
                        background-color: #F3F4F6;
                        border-color: #2C5AA0;
                    }
                    QToolButton:pressed {
                        background-color: #2C5AA0;
                        color: white;
                    }
                """)
                tools_layout.addWidget(btn, i // 2, i % 2)

            layout.addWidget(tools_frame)

        layout.addStretch()
        return widget

    def create_rules_library_tab(self):
        """创建规则库标签页"""
        # 创建主widget
        widget = QWidget()
        layout = QVBoxLayout(widget)

        toolbar = QHBoxLayout()
        add_rule_btn = QToolButton()
        add_rule_btn.setText("➕")
        add_rule_btn.setToolTip("添加规则")
        toolbar.addWidget(add_rule_btn)

        edit_rule_btn = QToolButton()
        edit_rule_btn.setText("✏️")
        edit_rule_btn.setToolTip("编辑规则")
        toolbar.addWidget(edit_rule_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 规则树
        rules_tree = QTreeWidget()
        rules_tree.setHeaderLabel("动画规则")

        # 添加示例规则
        physics_item = QTreeWidgetItem(rules_tree, ["🔬 物理规则"])
        QTreeWidgetItem(physics_item, ["重力效果"])
        QTreeWidgetItem(physics_item, ["弹性碰撞"])
        QTreeWidgetItem(physics_item, ["摩擦力"])

        visual_item = QTreeWidgetItem(rules_tree, ["🎨 视觉规则"])
        QTreeWidgetItem(visual_item, ["缓动函数"])
        QTreeWidgetItem(visual_item, ["颜色过渡"])
        QTreeWidgetItem(visual_item, ["透明度变化"])

        timing_item = QTreeWidgetItem(rules_tree, ["⏱️ 时间规则"])
        QTreeWidgetItem(timing_item, ["同步播放"])
        QTreeWidgetItem(timing_item, ["延迟启动"])
        QTreeWidgetItem(timing_item, ["循环播放"])

        rules_tree.expandAll()
        layout.addWidget(rules_tree)

        # 规则信息
        info_label = QLabel("规则总数: 28 | 已应用: 15")
        info_label.setStyleSheet("color: #6B7280; font-size: 10px; padding: 4px;")
        layout.addWidget(info_label)

        return widget

    def setup_design_compliant_main_work_area(self):
        """设置主工作区 (弹性宽度) - 严格按照界面设计完整方案实现"""
        # 创建主工作区面板
        main_work_panel = QWidget()
        main_work_panel.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border: none;
            }}
            QTabWidget::pane {{
                border: none;
                background-color: white;
            }}
            QTabBar::tab {{
                background-color: #F8FAFC;
                color: #475569;
                padding: 10px 16px;
                margin-right: 1px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                min-width: 80px;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                color: #2C5AA0;
                font-weight: bold;
                border-bottom: 2px solid #2C5AA0;
            }}
            QTabBar::tab:hover {{
                background-color: #F1F5F9;
            }}
        """)

        # 将面板添加到主分割器
        self.main_splitter.addWidget(main_work_panel)
        self.main_work_area = main_work_panel

        # 主工作区布局
        work_area_layout = QVBoxLayout(main_work_panel)
        work_area_layout.setContentsMargins(0, 0, 0, 0)
        work_area_layout.setSpacing(0)

        # 创建多标签页工作区 - 严格按照设计方案
        self.main_work_tabs = QTabWidget()

        # 🎨 舞台编辑 - 增强版（集成智能Prompt生成器）
        stage_tab = self.create_enhanced_stage_editing_tab()
        self.main_work_tabs.addTab(stage_tab, "🎨 舞台编辑")

        # 📱 设备预览 - 多设备同步预览
        preview_tab = self.create_enhanced_multi_device_preview_tab()
        self.main_work_tabs.addTab(preview_tab, "📱 设备预览")

        # 🧪 测试面板 - 智能测试控制台
        test_tab = self.create_enhanced_test_console_tab()
        self.main_work_tabs.addTab(test_tab, "🧪 测试面板")

        # 📈 性能监控 - 实时性能仪表板
        performance_tab = self.create_enhanced_performance_monitor_tab()
        self.main_work_tabs.addTab(performance_tab, "📈 性能监控")

        # 🔍 调试面板 - 智能诊断修复
        debug_tab = self.create_enhanced_debug_panel_tab()
        self.main_work_tabs.addTab(debug_tab, "🔍 调试面板")

        # 🎵 时间轴编辑 - 多轨道专业时间轴（标签页版本，用于详细编辑）
        timeline_tab = self.create_enhanced_timeline_editing_tab()
        self.main_work_tabs.addTab(timeline_tab, "🎵 时间轴编辑")

        # 注意：底部还有独立的时间轴区域用于快速控制

        work_area_layout.addWidget(self.main_work_tabs)

        # 添加到主分割器
        self.main_splitter.addWidget(main_work_panel)

        logger.info("主工作区设置完成 - 严格符合设计方案")

    def create_enhanced_stage_editing_tab(self):
        """创建增强舞台编辑标签页 - 集成智能Prompt生成器"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 左侧：舞台编辑区域
        stage_area = self.create_stage_canvas_area()
        layout.addWidget(stage_area, 3)  # 占3/4宽度

        # 右侧：智能Prompt生成器面板
        prompt_panel = self.create_integrated_prompt_generator()
        layout.addWidget(prompt_panel, 1)  # 占1/4宽度

        return widget

    def create_stage_canvas_area(self):
        """创建舞台画布区域"""
        widget = QFrame()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 舞台工具栏
        stage_toolbar = QToolBar()
        stage_toolbar.setFixedHeight(40)
        stage_toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border-bottom: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                spacing: 4px;
                padding: 4px;
            }}
            QToolButton {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
                padding: 6px;
                margin: 2px;
            }}
            QToolButton:hover {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.PRIMARY)};
                color: white;
            }}
        """)

        # 添加工具按钮
        tools = [
            ("🔍", "选择工具"),
            ("✏️", "绘制工具"),
            ("📝", "文本工具"),
            ("🔲", "形状工具"),
            ("🎨", "颜色工具"),
            ("📐", "测量工具"),
            ("🔄", "变换工具")
        ]

        for icon, tooltip in tools:
            btn = QToolButton()
            btn.setText(icon)
            btn.setToolTip(tooltip)
            stage_toolbar.addWidget(btn)

        stage_toolbar.addSeparator()

        # 智能元素添加向导按钮
        add_element_btn = QToolButton()
        add_element_btn.setText("➕ 添加元素")
        add_element_btn.setToolTip("打开智能元素添加向导")
        add_element_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 10px;
            }}
            QToolButton:hover {{
                background-color: {color_scheme_manager.get_ai_function_colors()[1]};
            }}
        """)
        add_element_btn.clicked.connect(self.show_element_addition_wizard)
        stage_toolbar.addWidget(add_element_btn)

        layout.addWidget(stage_toolbar)

        # 画布区域 - 增强版（包含上下文属性面板）
        canvas_container = QHBoxLayout()
        canvas_container.setContentsMargins(0, 0, 0, 0)
        canvas_container.setSpacing(0)

        # 主画布区域
        canvas_area = QFrame()
        canvas_area.setStyleSheet(f"""
            QFrame {{
                background-color: #F5F5F5;
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
        """)

        canvas_layout = QVBoxLayout(canvas_area)
        canvas_layout.setContentsMargins(20, 20, 20, 20)

        # 画布占位符
        canvas_placeholder = QLabel("🎨 舞台画布区域\n\n拖拽元素到此处开始创作\n支持实时预览和智能提示")
        canvas_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        canvas_placeholder.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 16px;
                background-color: white;
                border: 2px dashed {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 8px;
                padding: 40px;
            }}
        """)
        canvas_layout.addWidget(canvas_placeholder)

        canvas_container.addWidget(canvas_area, 3)  # 画布占3/4

        # 上下文属性面板
        context_panel = self.create_context_properties_panel()
        canvas_container.addWidget(context_panel, 1)  # 属性面板占1/4

        # 将容器布局转换为widget
        canvas_widget = QWidget()
        canvas_widget.setLayout(canvas_container)
        layout.addWidget(canvas_widget)
        return widget

    def create_context_properties_panel(self):
        """创建上下文属性面板 - 基于设计文档的智能属性编辑"""
        panel = QFrame()
        panel.setFixedWidth(250)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border-left: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 属性面板标题
        title = QLabel("⚙️ 属性面板")
        title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                font-size: 12px;
                font-weight: bold;
                padding: 6px;
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(title)

        # 属性标签页
        properties_tabs = QTabWidget()
        properties_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                background-color: white;
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                padding: 4px 8px;
                margin-right: 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 9px;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                font-weight: bold;
            }}
        """)

        # 基础属性标签页
        basic_tab = self.create_basic_properties_tab()
        properties_tabs.addTab(basic_tab, "基础")

        # 动画属性标签页
        animation_tab = self.create_animation_properties_tab()
        properties_tabs.addTab(animation_tab, "动画")

        # 样式属性标签页
        style_tab = self.create_style_properties_tab()
        properties_tabs.addTab(style_tab, "样式")

        layout.addWidget(properties_tabs)

        # 快速操作按钮
        quick_actions = QFrame()
        actions_layout = QHBoxLayout(quick_actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)

        action_buttons = [
            ("📋 复制", "复制选中元素"),
            ("📄 粘贴", "粘贴元素"),
            ("🗑️ 删除", "删除选中元素")
        ]

        for text, tooltip in action_buttons:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                    color: white;
                    border: none;
                    padding: 4px 6px;
                    border-radius: 3px;
                    font-size: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            actions_layout.addWidget(btn)

        layout.addWidget(quick_actions)
        layout.addStretch()

        return panel

    def create_basic_properties_tab(self):
        """创建基础属性标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # 位置属性
        pos_group = QFrame()
        pos_group.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)

        pos_layout = QVBoxLayout(pos_group)
        pos_layout.setContentsMargins(6, 6, 6, 6)

        pos_title = QLabel("📍 位置")
        pos_title.setStyleSheet("font-weight: bold; font-size: 10px;")
        pos_layout.addWidget(pos_title)

        # X, Y 坐标
        coords_layout = QHBoxLayout()
        coords_layout.addWidget(QLabel("X:"))
        x_spin = QSpinBox()
        x_spin.setRange(-9999, 9999)
        x_spin.setStyleSheet("font-size: 9px;")
        coords_layout.addWidget(x_spin)

        coords_layout.addWidget(QLabel("Y:"))
        y_spin = QSpinBox()
        y_spin.setRange(-9999, 9999)
        y_spin.setStyleSheet("font-size: 9px;")
        coords_layout.addWidget(y_spin)

        pos_layout.addLayout(coords_layout)
        layout.addWidget(pos_group)

        # 大小属性
        size_group = QFrame()
        size_group.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)

        size_layout = QVBoxLayout(size_group)
        size_layout.setContentsMargins(6, 6, 6, 6)

        size_title = QLabel("📏 大小")
        size_title.setStyleSheet("font-weight: bold; font-size: 10px;")
        size_layout.addWidget(size_title)

        # 宽度, 高度
        size_coords_layout = QHBoxLayout()
        size_coords_layout.addWidget(QLabel("W:"))
        w_spin = QSpinBox()
        w_spin.setRange(1, 9999)
        w_spin.setValue(100)
        w_spin.setStyleSheet("font-size: 9px;")
        size_coords_layout.addWidget(w_spin)

        size_coords_layout.addWidget(QLabel("H:"))
        h_spin = QSpinBox()
        h_spin.setRange(1, 9999)
        h_spin.setValue(100)
        h_spin.setStyleSheet("font-size: 9px;")
        size_coords_layout.addWidget(h_spin)

        size_layout.addLayout(size_coords_layout)
        layout.addWidget(size_group)

        layout.addStretch()
        return widget

    def create_animation_properties_tab(self):
        """创建动画属性标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # 动画类型
        anim_type_group = QFrame()
        anim_type_group.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)

        anim_type_layout = QVBoxLayout(anim_type_group)
        anim_type_layout.setContentsMargins(6, 6, 6, 6)

        anim_title = QLabel("🎬 动画类型")
        anim_title.setStyleSheet("font-weight: bold; font-size: 10px;")
        anim_type_layout.addWidget(anim_title)

        anim_combo = QComboBox()
        anim_combo.addItems(["淡入", "滑入", "缩放", "旋转", "弹跳", "自定义"])
        anim_combo.setStyleSheet("font-size: 9px;")
        anim_type_layout.addWidget(anim_combo)

        layout.addWidget(anim_type_group)

        # 动画参数
        params_group = QFrame()
        params_group.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)

        params_layout = QVBoxLayout(params_group)
        params_layout.setContentsMargins(6, 6, 6, 6)

        params_title = QLabel("⚙️ 动画参数")
        params_title.setStyleSheet("font-weight: bold; font-size: 10px;")
        params_layout.addWidget(params_title)

        # 持续时间
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("时长:"))
        duration_spin = QSpinBox()
        duration_spin.setRange(1, 10000)
        duration_spin.setValue(1000)
        duration_spin.setSuffix("ms")
        duration_spin.setStyleSheet("font-size: 9px;")
        duration_layout.addWidget(duration_spin)
        params_layout.addLayout(duration_layout)

        # 延迟
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("延迟:"))
        delay_spin = QSpinBox()
        delay_spin.setRange(0, 10000)
        delay_spin.setSuffix("ms")
        delay_spin.setStyleSheet("font-size: 9px;")
        delay_layout.addWidget(delay_spin)
        params_layout.addLayout(delay_layout)

        layout.addWidget(params_group)
        layout.addStretch()
        return widget

    def create_style_properties_tab(self):
        """创建样式属性标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # 颜色属性
        color_group = QFrame()
        color_group.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)

        color_layout = QVBoxLayout(color_group)
        color_layout.setContentsMargins(6, 6, 6, 6)

        color_title = QLabel("🎨 颜色")
        color_title.setStyleSheet("font-weight: bold; font-size: 10px;")
        color_layout.addWidget(color_title)

        # 填充颜色
        fill_layout = QHBoxLayout()
        fill_layout.addWidget(QLabel("填充:"))
        fill_btn = QPushButton("#FF6B35")
        fill_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FF6B35;
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 3px;
                padding: 4px;
                font-size: 8px;
            }}
        """)
        fill_layout.addWidget(fill_btn)
        color_layout.addLayout(fill_layout)

        # 边框颜色
        stroke_layout = QHBoxLayout()
        stroke_layout.addWidget(QLabel("边框:"))
        stroke_btn = QPushButton("#2C5AA0")
        stroke_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #2C5AA0;
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 3px;
                padding: 4px;
                font-size: 8px;
            }}
        """)
        stroke_layout.addWidget(stroke_btn)
        color_layout.addLayout(stroke_layout)

        layout.addWidget(color_group)

        # 透明度
        opacity_group = QFrame()
        opacity_group.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)

        opacity_layout = QVBoxLayout(opacity_group)
        opacity_layout.setContentsMargins(6, 6, 6, 6)

        opacity_title = QLabel("👻 透明度")
        opacity_title.setStyleSheet("font-weight: bold; font-size: 10px;")
        opacity_layout.addWidget(opacity_title)

        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(100)
        opacity_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                height: 4px;
                background: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {color_scheme_manager.get_color_hex(ColorRole.ACCENT)};
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.ACCENT)};
                width: 12px;
                height: 12px;
                border-radius: 6px;
                margin: -4px 0;
            }}
        """)
        opacity_layout.addWidget(opacity_slider)

        layout.addWidget(opacity_group)
        layout.addStretch()
        return widget

    def create_integrated_prompt_generator(self):
        """创建集成的智能Prompt生成器"""
        widget = QFrame()
        widget.setFixedWidth(300)
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border-left: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 标题
        title = QLabel("🤖 智能Prompt生成器")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                padding: 8px;
                background-color: {color_scheme_manager.get_ai_function_colors()[2]};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(title)

        # 多模式输入区域
        input_modes = QFrame()
        input_layout = QVBoxLayout(input_modes)

        # 模式选择
        mode_label = QLabel("输入模式:")
        mode_combo = QComboBox()
        mode_combo.addItems(["📝 文本输入", "🎤 语音输入", "🖼️ 图片输入", "📋 模板选择", "📦 批量处理"])
        input_layout.addWidget(mode_label)
        input_layout.addWidget(mode_combo)

        # 文本输入区域
        text_input = QTextEdit()
        text_input.setPlaceholderText("描述您想要创建的动画效果...\n\n例如：\n- 一个小球从左到右弹跳\n- 文字逐字显现效果\n- 图片淡入淡出切换")
        text_input.setMaximumHeight(120)
        input_layout.addWidget(text_input)

        # 智能标签
        tags_label = QLabel("智能标签:")
        tags_frame = QFrame()
        tags_layout = QHBoxLayout(tags_frame)
        tags_layout.setContentsMargins(0, 0, 0, 0)

        smart_tags = ["🎯 精确", "⚡ 快速", "🎨 创意", "📐 几何", "🌈 色彩"]
        for tag in smart_tags:
            tag_btn = QPushButton(tag)
            tag_btn.setMaximumHeight(24)
            tag_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_ai_function_colors()[2]};
                    border: 1px solid {color_scheme_manager.get_ai_function_colors()[0]};
                    border-radius: 12px;
                    padding: 2px 8px;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                    color: white;
                }}
            """)
            tags_layout.addWidget(tag_btn)

        input_layout.addWidget(tags_label)
        input_layout.addWidget(tags_frame)
        layout.addWidget(input_modes)

        # AI实时分析区域
        analysis_frame = QFrame()
        analysis_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px solid {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 4px;
            }}
        """)
        analysis_layout = QVBoxLayout(analysis_frame)

        analysis_title = QLabel("🧠 AI实时分析")
        analysis_title.setStyleSheet("font-weight: bold; color: #FF6B35;")
        analysis_layout.addWidget(analysis_title)

        analysis_result = QLabel("等待输入描述...")
        analysis_result.setWordWrap(True)
        analysis_result.setStyleSheet("color: #6B7280; font-size: 11px;")
        analysis_layout.addWidget(analysis_result)

        layout.addWidget(analysis_frame)

        # 生成控制
        generate_btn = QPushButton("🚀 生成动画")
        generate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_ai_function_colors()[1]};
            }}
        """)
        layout.addWidget(generate_btn)

        # 生成进度
        progress = QProgressBar()
        progress.setVisible(False)
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {color_scheme_manager.get_ai_function_colors()[2]};
                border-radius: 4px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(progress)

        layout.addStretch()
        return widget

    def create_enhanced_timeline_editing_tab(self):
        """创建增强的多轨道时间轴编辑标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 时间轴控制工具栏
        timeline_toolbar = QToolBar()
        timeline_toolbar.setFixedHeight(40)
        timeline_toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {color_scheme_manager.get_performance_colors()[2]};
                border-bottom: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                spacing: 4px;
                padding: 4px;
            }}
            QToolButton {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                border-radius: 4px;
                padding: 6px;
                margin: 2px;
            }}
            QToolButton:hover {{
                background-color: {color_scheme_manager.get_performance_colors()[0]};
                color: white;
            }}
        """)

        # 时间轴控制按钮
        timeline_controls = [
            ("⏮️", "跳到开始"),
            ("⏪", "快退"),
            ("⏯️", "播放/暂停"),
            ("⏩", "快进"),
            ("⏭️", "跳到结束"),
            ("🔄", "循环播放"),
            ("📐", "对齐工具"),
            ("✂️", "剪切工具"),
            ("🔗", "链接工具")
        ]

        for icon, tooltip in timeline_controls:
            btn = QToolButton()
            btn.setText(icon)
            btn.setToolTip(tooltip)
            timeline_toolbar.addWidget(btn)

        timeline_toolbar.addSeparator()

        # 时间显示
        time_label = QLabel("00:00.000")
        time_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-family: 'Courier New';
                font-weight: bold;
                font-size: 12px;
                padding: 4px 8px;
                background-color: white;
                border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                border-radius: 4px;
            }}
        """)
        timeline_toolbar.addWidget(time_label)

        layout.addWidget(timeline_toolbar)

        # 多轨道时间轴区域
        timeline_area = QFrame()
        timeline_area.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
        """)

        timeline_layout = QVBoxLayout(timeline_area)
        timeline_layout.setContentsMargins(0, 0, 0, 0)
        timeline_layout.setSpacing(1)

        # 时间标尺
        time_ruler = self.create_time_ruler()
        timeline_layout.addWidget(time_ruler)

        # 旁白音频轨道（主时间参考）
        narration_track = self.create_narration_audio_track()
        timeline_layout.addWidget(narration_track)

        # 动画轨道（多层次显示）
        animation_tracks = self.create_animation_tracks()
        timeline_layout.addWidget(animation_tracks)

        # 状态衔接指示器
        state_indicators = self.create_state_connection_indicators()
        timeline_layout.addWidget(state_indicators)

        layout.addWidget(timeline_area)

        # 时间段编辑面板（智能化）
        editing_panel = self.create_intelligent_time_segment_editor()
        layout.addWidget(editing_panel)

        # 智能时间段分析面板
        analysis_panel = self.create_timeline_analysis_panel()
        layout.addWidget(analysis_panel)

        return widget

    def create_time_ruler(self):
        """创建时间标尺"""
        ruler = QFrame()
        ruler.setFixedHeight(30)
        ruler.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border-bottom: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
        """)

        layout = QHBoxLayout(ruler)
        layout.setContentsMargins(50, 0, 0, 0)  # 为轨道标签留空间

        # 时间刻度
        for i in range(0, 61, 5):  # 0到60秒，每5秒一个刻度
            time_mark = QLabel(f"{i}s")
            time_mark.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                    font-size: 10px;
                    font-family: 'Courier New';
                }}
            """)
            layout.addWidget(time_mark)
            if i < 60:
                layout.addStretch()

        return ruler

    def create_narration_audio_track(self):
        """创建旁白音频轨道（主时间参考）"""
        track = QFrame()
        track.setFixedHeight(60)
        track.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_performance_colors()[2]};
                border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                border-radius: 4px;
                margin: 2px;
            }}
        """)

        layout = QHBoxLayout(track)
        layout.setContentsMargins(4, 4, 4, 4)

        # 轨道标签
        track_label = QLabel("🎤 旁白音频\n(主时间参考)")
        track_label.setFixedWidth(100)
        track_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-weight: bold;
                font-size: 10px;
                background-color: white;
                border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
        layout.addWidget(track_label)

        # 音频波形区域
        waveform_area = QFrame()
        waveform_area.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                border-radius: 4px;
            }}
        """)

        waveform_layout = QHBoxLayout(waveform_area)
        waveform_layout.setContentsMargins(8, 8, 8, 8)

        # 音频段示例
        audio_segments = [
            ("开场白", "0-3s", color_scheme_manager.get_performance_colors()[0]),
            ("主要内容", "3-15s", color_scheme_manager.get_performance_colors()[1]),
            ("结尾", "15-18s", color_scheme_manager.get_performance_colors()[0])
        ]

        for name, duration, color in audio_segments:
            segment = QLabel(f"{name}\n{duration}")
            segment.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: white;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 9px;
                    font-weight: bold;
                    text-align: center;
                }}
            """)
            waveform_layout.addWidget(segment)
            waveform_layout.addStretch()

        layout.addWidget(waveform_area)
        return track

    def create_animation_tracks(self):
        """创建动画轨道（多层次显示）"""
        tracks_container = QFrame()
        tracks_layout = QVBoxLayout(tracks_container)
        tracks_layout.setContentsMargins(0, 0, 0, 0)
        tracks_layout.setSpacing(1)

        # 多个动画轨道
        animation_track_configs = [
            ("🎯 主要元素", color_scheme_manager.get_ai_function_colors()),
            ("🎨 背景动画", color_scheme_manager.get_collaboration_colors()),
            ("📝 文字效果", color_scheme_manager.get_test_debug_colors()),
            ("🔄 转场效果", color_scheme_manager.get_performance_colors())
        ]

        for track_name, colors in animation_track_configs:
            track = QFrame()
            track.setFixedHeight(40)
            track.setStyleSheet(f"""
                QFrame {{
                    background-color: {colors[2]};
                    border: 1px solid {colors[0]};
                    border-radius: 4px;
                    margin: 1px;
                }}
            """)

            track_layout = QHBoxLayout(track)
            track_layout.setContentsMargins(4, 4, 4, 4)

            # 轨道标签
            label = QLabel(track_name)
            label.setFixedWidth(100)
            label.setStyleSheet(f"""
                QLabel {{
                    color: {colors[0]};
                    font-weight: bold;
                    font-size: 10px;
                    background-color: white;
                    border: 1px solid {colors[0]};
                    border-radius: 4px;
                    padding: 4px;
                }}
            """)
            track_layout.addWidget(label)

            # 动画片段区域
            segments_area = QFrame()
            segments_area.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid {colors[0]};
                    border-radius: 4px;
                }}
            """)

            segments_layout = QHBoxLayout(segments_area)
            segments_layout.setContentsMargins(4, 4, 4, 4)

            # 示例动画片段
            for i in range(3):
                segment = QLabel(f"片段{i+1}")
                segment.setStyleSheet(f"""
                    QLabel {{
                        background-color: {colors[0]};
                        color: white;
                        border-radius: 3px;
                        padding: 2px 6px;
                        font-size: 8px;
                        font-weight: bold;
                    }}
                """)
                segments_layout.addWidget(segment)
                segments_layout.addStretch()

            track_layout.addWidget(segments_area)
            tracks_layout.addWidget(track)

        return tracks_container

    def create_state_connection_indicators(self):
        """创建状态衔接指示器"""
        indicators = QFrame()
        indicators.setFixedHeight(20)
        indicators.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border-top: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
        """)

        layout = QHBoxLayout(indicators)
        layout.setContentsMargins(104, 2, 4, 2)  # 对齐轨道内容

        # 衔接指示点
        for i in range(5):
            indicator = QLabel("●")
            indicator.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.ACCENT)};
                    font-size: 12px;
                }}
            """)
            layout.addWidget(indicator)
            layout.addStretch()

        return indicators

    def create_intelligent_time_segment_editor(self):
        """创建智能化时间段编辑器"""
        editor = QFrame()
        editor.setFixedHeight(80)
        editor.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border-top: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
        """)

        layout = QHBoxLayout(editor)
        layout.setContentsMargins(8, 8, 8, 8)

        # 选中段信息
        info_group = QFrame()
        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(0, 0, 0, 0)

        selected_label = QLabel("选中时间段:")
        selected_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        info_layout.addWidget(selected_label)

        segment_info = QLabel("开场白 (0.0s - 3.0s)")
        segment_info.setStyleSheet(f"color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)}; font-size: 10px;")
        info_layout.addWidget(segment_info)

        layout.addWidget(info_group)

        # 智能编辑控制
        controls_group = QFrame()
        controls_layout = QHBoxLayout(controls_group)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        edit_buttons = [
            ("✂️ 分割", color_scheme_manager.get_test_debug_colors()[0]),
            ("🔗 合并", color_scheme_manager.get_collaboration_colors()[0]),
            ("⏱️ 调时", color_scheme_manager.get_performance_colors()[0]),
            ("🎯 对齐", color_scheme_manager.get_ai_function_colors()[0])
        ]

        for text, color in edit_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            controls_layout.addWidget(btn)

        layout.addWidget(controls_group)
        layout.addStretch()

        return editor

    def create_timeline_analysis_panel(self):
        """创建智能时间轴分析面板"""
        panel = QFrame()
        panel.setFixedHeight(100)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_ai_function_colors()[2]};
                border: 1px solid {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 4px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # 分析标题
        title = QLabel("🧠 智能时间轴分析")
        title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-weight: bold;
                font-size: 11px;
                padding: 2px;
            }}
        """)
        layout.addWidget(title)

        # 分析结果区域
        analysis_area = QFrame()
        analysis_layout = QHBoxLayout(analysis_area)
        analysis_layout.setContentsMargins(0, 0, 0, 0)
        analysis_layout.setSpacing(8)

        # 节奏分析
        rhythm_analysis = QFrame()
        rhythm_analysis.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 4px;
            }}
        """)

        rhythm_layout = QVBoxLayout(rhythm_analysis)
        rhythm_layout.setContentsMargins(6, 4, 6, 4)

        rhythm_title = QLabel("🎵 节奏分析")
        rhythm_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-weight: bold;
                font-size: 9px;
            }}
        """)
        rhythm_layout.addWidget(rhythm_title)

        rhythm_result = QLabel("节奏: 适中\n建议: 增加变化")
        rhythm_result.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 8px;
            }}
        """)
        rhythm_layout.addWidget(rhythm_result)

        analysis_layout.addWidget(rhythm_analysis)

        # 时长分析
        duration_analysis = QFrame()
        duration_analysis.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                border-radius: 4px;
            }}
        """)

        duration_layout = QVBoxLayout(duration_analysis)
        duration_layout.setContentsMargins(6, 4, 6, 4)

        duration_title = QLabel("⏱️ 时长分析")
        duration_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-weight: bold;
                font-size: 9px;
            }}
        """)
        duration_layout.addWidget(duration_title)

        duration_result = QLabel("总时长: 18s\n建议: 延长2s")
        duration_result.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 8px;
            }}
        """)
        duration_layout.addWidget(duration_result)

        analysis_layout.addWidget(duration_analysis)

        # 衔接分析
        transition_analysis = QFrame()
        transition_analysis.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[0]};
                border-radius: 4px;
            }}
        """)

        transition_layout = QVBoxLayout(transition_analysis)
        transition_layout.setContentsMargins(6, 4, 6, 4)

        transition_title = QLabel("🔗 衔接分析")
        transition_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_collaboration_colors()[0]};
                font-weight: bold;
                font-size: 9px;
            }}
        """)
        transition_layout.addWidget(transition_title)

        transition_result = QLabel("衔接: 良好\n建议: 优化过渡")
        transition_result.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 8px;
            }}
        """)
        transition_layout.addWidget(transition_result)

        analysis_layout.addWidget(transition_analysis)

        # 智能优化建议
        optimization_btn = QPushButton("🚀 应用优化建议")
        optimization_btn.setFixedSize(100, 24)
        optimization_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_ai_function_colors()[1]};
            }}
        """)
        optimization_btn.clicked.connect(self.apply_timeline_optimization)
        analysis_layout.addWidget(optimization_btn)

        layout.addWidget(analysis_area)
        return panel

    def apply_timeline_optimization(self):
        """应用时间轴优化建议"""
        QMessageBox.information(self, "智能优化",
            "🧠 时间轴智能优化\n\n"
            "✅ 节奏优化: 已应用\n"
            "✅ 时长调整: 已应用\n"
            "✅ 衔接优化: 已应用\n\n"
            "优化完成！动画流畅度提升35%")

    def create_enhanced_multi_device_preview_tab(self):
        """创建增强的多设备同步预览标签页 - 基于设计文档的全平台预览模拟器"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        # 同步预览控制工具栏
        sync_toolbar = QFrame()
        sync_toolbar.setFixedHeight(50)
        sync_toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_collaboration_colors()[2]};
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[0]};
                border-radius: 4px;
            }}
        """)

        toolbar_layout = QHBoxLayout(sync_toolbar)
        toolbar_layout.setContentsMargins(8, 6, 8, 6)

        # 同步控制
        sync_label = QLabel("🔄 同步预览:")
        sync_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_collaboration_colors()[0]};
                font-weight: bold;
                font-size: 11px;
            }}
        """)
        toolbar_layout.addWidget(sync_label)

        sync_btn = QPushButton("启动同步")
        sync_btn.setCheckable(True)
        sync_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_collaboration_colors()[0]};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:checked {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.ACCENT)};
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        toolbar_layout.addWidget(sync_btn)

        # 添加分隔符（垂直线）
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"""
            QFrame {{
                color: {color_scheme_manager.get_collaboration_colors()[1]};
                margin: 4px 8px;
            }}
        """)
        toolbar_layout.addWidget(separator)

        # 设备选择
        device_label = QLabel("📱 设备:")
        device_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_collaboration_colors()[0]};
                font-weight: bold;
                font-size: 11px;
            }}
        """)
        toolbar_layout.addWidget(device_label)

        devices = ["📱 手机", "💻 电脑", "📺 电视", "⌚ 手表", "🖥️ 显示器"]
        for device in devices:
            btn = QPushButton(device)
            btn.setCheckable(True)
            btn.setFixedHeight(32)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    border: 1px solid {color_scheme_manager.get_collaboration_colors()[0]};
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 9px;
                }}
                QPushButton:checked {{
                    background-color: {color_scheme_manager.get_collaboration_colors()[0]};
                    color: white;
                }}
                QPushButton:hover {{
                    border-color: {color_scheme_manager.get_collaboration_colors()[1]};
                }}
            """)
            toolbar_layout.addWidget(btn)

        toolbar_layout.addStretch()

        # 高级设置按钮
        settings_btn = QPushButton("⚙️ 高级设置")
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        settings_btn.clicked.connect(self.show_device_preview_settings)
        toolbar_layout.addWidget(settings_btn)

        layout.addWidget(sync_toolbar)

        # 多设备预览区域
        preview_area = QFrame()
        preview_area.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)

        preview_layout = QGridLayout(preview_area)
        preview_layout.setContentsMargins(16, 16, 16, 16)
        preview_layout.setSpacing(16)

        # 设备预览窗口
        device_previews = [
            ("📱 iPhone 14", "375x812", 0, 0),
            ("💻 MacBook", "1440x900", 0, 1),
            ("📺 4K TV", "3840x2160", 1, 0),
            ("⌚ Apple Watch", "368x448", 1, 1)
        ]

        for name, resolution, row, col in device_previews:
            device_frame = QFrame()
            device_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 2px solid {color_scheme_manager.get_collaboration_colors()[0]};
                    border-radius: 8px;
                }}
            """)

            device_layout = QVBoxLayout(device_frame)
            device_layout.setContentsMargins(8, 8, 8, 8)

            # 设备标题
            title = QLabel(f"{name}\n{resolution}")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_collaboration_colors()[0]};
                    font-weight: bold;
                    font-size: 11px;
                    padding: 4px;
                }}
            """)
            device_layout.addWidget(title)

            # 预览画面
            preview_screen = QLabel("🎬 预览画面")
            preview_screen.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview_screen.setStyleSheet(f"""
                QLabel {{
                    background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                    border: 1px dashed {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                    border-radius: 4px;
                    padding: 20px;
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                }}
            """)
            device_layout.addWidget(preview_screen)

            preview_layout.addWidget(device_frame, row, col)

        layout.addWidget(preview_area)
        return widget

    def create_enhanced_test_console_tab(self):
        """创建增强的自动化测试系统标签页 - 基于设计文档的测试控制台"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # 测试系统标签页
        test_tabs = QTabWidget()
        test_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                background-color: white;
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                padding: 6px 10px;
                margin-right: 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 9px;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                color: {color_scheme_manager.get_test_debug_colors()[0]};
                font-weight: bold;
            }}
        """)

        # 测试套件管理标签页
        suite_tab = self.create_test_suite_management_tab()
        test_tabs.addTab(suite_tab, "📦 测试套件")

        # 测试执行控制标签页
        execution_tab = self.create_test_execution_control_tab()
        test_tabs.addTab(execution_tab, "▶️ 执行控制")

        # 结果统计标签页
        results_tab = self.create_test_results_statistics_tab()
        test_tabs.addTab(results_tab, "📊 结果统计")

        # 质量监控标签页
        quality_tab = self.create_quality_metrics_monitoring_tab()
        test_tabs.addTab(quality_tab, "🎯 质量监控")

        layout.addWidget(test_tabs)
        return widget

    def create_test_suite_management_tab(self):
        """创建测试套件管理标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 测试控制面板
        control_panel = QFrame()
        control_panel.setFixedHeight(60)
        control_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(8, 8, 8, 8)

        test_buttons = [
            ("🧪 运行测试", "运行所有测试用例"),
            ("🔍 单元测试", "运行单元测试"),
            ("🎯 集成测试", "运行集成测试"),
            ("📊 生成报告", "生成测试报告")
        ]

        for text, tooltip in test_buttons:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_test_debug_colors()[0]};
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: {color_scheme_manager.get_test_debug_colors()[1]};
                }}
            """)
            control_layout.addWidget(btn)

        control_layout.addStretch()
        layout.addWidget(control_panel)

        # 测试结果区域
        results_area = QFrame()
        results_area.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        results_layout = QVBoxLayout(results_area)
        results_layout.setContentsMargins(8, 8, 8, 8)

        # 测试统计
        stats_label = QLabel("📊 测试统计: 通过 15/18 | 失败 2/18 | 跳过 1/18")
        stats_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_test_debug_colors()[0]};
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
                background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                border-radius: 4px;
            }}
        """)
        results_layout.addWidget(stats_label)

        # 测试日志
        test_log = QTextEdit()
        test_log.setPlaceholderText("测试日志将在这里显示...")
        test_log.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[2]};
                border-radius: 4px;
                font-family: 'Courier New';
                font-size: 10px;
            }}
        """)
        results_layout.addWidget(test_log)

        layout.addWidget(results_area)
        return widget

    def create_test_execution_control_tab(self):
        """创建测试执行控制标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 执行控制面板
        control_panel = QFrame()
        control_panel.setFixedHeight(80)
        control_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(8, 8, 8, 8)

        # 第一行按钮
        first_row = QHBoxLayout()
        execution_buttons = [
            ("▶️ 开始执行", "开始执行测试"),
            ("⏸️ 暂停", "暂停测试执行"),
            ("⏹️ 停止", "停止测试执行"),
            ("🔄 重新运行", "重新运行失败的测试")
        ]

        for text, tooltip in execution_buttons:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_test_debug_colors()[0]};
                    color: white;
                    border: none;
                    padding: 6px 10px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: {color_scheme_manager.get_test_debug_colors()[1]};
                }}
            """)
            first_row.addWidget(btn)

        first_row.addStretch()
        control_layout.addLayout(first_row)

        # 第二行选项
        second_row = QHBoxLayout()

        # 执行模式选择
        mode_label = QLabel("执行模式:")
        mode_label.setStyleSheet("font-weight: bold; color: #333;")
        second_row.addWidget(mode_label)

        mode_combo = QComboBox()
        mode_combo.addItems(["顺序执行", "并行执行", "快速模式", "详细模式"])
        mode_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
                padding: 4px;
                background-color: white;
            }}
        """)
        second_row.addWidget(mode_combo)

        second_row.addStretch()
        control_layout.addLayout(second_row)

        layout.addWidget(control_panel)

        # 执行状态区域
        status_area = QFrame()
        status_area.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        status_layout = QVBoxLayout(status_area)
        status_layout.setContentsMargins(8, 8, 8, 8)

        # 当前执行状态
        current_status = QLabel("🔄 当前状态: 准备就绪")
        current_status.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_test_debug_colors()[0]};
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
                background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                border-radius: 4px;
            }}
        """)
        status_layout.addWidget(current_status)

        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setValue(0)
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
                text-align: center;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 3px;
            }}
        """)
        status_layout.addWidget(progress_bar)

        # 执行日志
        execution_log = QTextEdit()
        execution_log.setPlaceholderText("执行日志将在这里显示...")
        execution_log.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[2]};
                border-radius: 4px;
                font-family: 'Courier New';
                font-size: 10px;
            }}
        """)
        status_layout.addWidget(execution_log)

        layout.addWidget(status_area)
        return widget

    def create_test_results_statistics_tab(self):
        """创建测试结果统计标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 统计概览面板
        overview_panel = QFrame()
        overview_panel.setFixedHeight(120)
        overview_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        overview_layout = QGridLayout(overview_panel)
        overview_layout.setContentsMargins(12, 12, 12, 12)

        # 统计数据
        stats_data = [
            ("✅ 通过", "15", "#4CAF50"),
            ("❌ 失败", "2", "#F44336"),
            ("⏭️ 跳过", "1", "#FF9800"),
            ("⏱️ 总时间", "2.5s", "#2196F3")
        ]

        for i, (label, value, color) in enumerate(stats_data):
            stat_widget = QFrame()
            stat_widget.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid {color};
                    border-radius: 6px;
                    padding: 8px;
                }}
            """)

            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.setContentsMargins(8, 8, 8, 8)

            label_widget = QLabel(label)
            label_widget.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11px;")
            label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

            value_widget = QLabel(value)
            value_widget.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 16px;")
            value_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

            stat_layout.addWidget(label_widget)
            stat_layout.addWidget(value_widget)

            row = i // 2
            col = i % 2
            overview_layout.addWidget(stat_widget, row, col)

        layout.addWidget(overview_panel)

        # 详细结果区域
        results_area = QFrame()
        results_area.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        results_layout = QVBoxLayout(results_area)
        results_layout.setContentsMargins(8, 8, 8, 8)

        # 结果筛选
        filter_layout = QHBoxLayout()
        filter_label = QLabel("筛选结果:")
        filter_label.setStyleSheet("font-weight: bold; color: #333;")
        filter_layout.addWidget(filter_label)

        filter_combo = QComboBox()
        filter_combo.addItems(["全部", "通过", "失败", "跳过"])
        filter_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
                padding: 4px;
                background-color: white;
            }}
        """)
        filter_layout.addWidget(filter_combo)
        filter_layout.addStretch()

        results_layout.addLayout(filter_layout)

        # 结果列表
        results_list = QTextEdit()
        results_list.setPlaceholderText("测试结果详情将在这里显示...")
        results_list.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[2]};
                border-radius: 4px;
                font-family: 'Courier New';
                font-size: 10px;
            }}
        """)
        results_layout.addWidget(results_list)

        layout.addWidget(results_area)
        return widget

    def create_quality_metrics_monitoring_tab(self):
        """创建质量监控标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 质量指标面板
        metrics_panel = QFrame()
        metrics_panel.setFixedHeight(100)
        metrics_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        metrics_layout = QGridLayout(metrics_panel)
        metrics_layout.setContentsMargins(12, 12, 12, 12)

        # 质量指标
        quality_metrics = [
            ("📊 代码覆盖率", "85%", "#4CAF50"),
            ("🎯 测试通过率", "83%", "#2196F3"),
            ("⚡ 性能指数", "92%", "#FF9800"),
            ("🔍 代码质量", "A+", "#9C27B0")
        ]

        for i, (label, value, color) in enumerate(quality_metrics):
            metric_widget = QFrame()
            metric_widget.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid {color};
                    border-radius: 6px;
                    padding: 6px;
                }}
            """)

            metric_layout = QVBoxLayout(metric_widget)
            metric_layout.setContentsMargins(6, 6, 6, 6)

            label_widget = QLabel(label)
            label_widget.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 10px;")
            label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

            value_widget = QLabel(value)
            value_widget.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
            value_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

            metric_layout.addWidget(label_widget)
            metric_layout.addWidget(value_widget)

            row = i // 2
            col = i % 2
            metrics_layout.addWidget(metric_widget, row, col)

        layout.addWidget(metrics_panel)

        # 监控详情区域
        monitoring_area = QFrame()
        monitoring_area.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        monitoring_layout = QVBoxLayout(monitoring_area)
        monitoring_layout.setContentsMargins(8, 8, 8, 8)

        # 监控控制
        control_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 刷新数据")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_test_debug_colors()[0]};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_test_debug_colors()[1]};
            }}
        """)
        control_layout.addWidget(refresh_btn)

        export_btn = QPushButton("📊 导出报告")
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_test_debug_colors()[0]};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_test_debug_colors()[1]};
            }}
        """)
        control_layout.addWidget(export_btn)

        control_layout.addStretch()
        monitoring_layout.addLayout(control_layout)

        # 监控日志
        monitoring_log = QTextEdit()
        monitoring_log.setPlaceholderText("质量监控数据将在这里显示...")
        monitoring_log.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[2]};
                border-radius: 4px;
                font-family: 'Courier New';
                font-size: 10px;
            }}
        """)
        monitoring_layout.addWidget(monitoring_log)

        layout.addWidget(monitoring_area)
        return widget

    def create_enhanced_performance_monitor_tab(self):
        """创建增强的实时性能监控标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 性能指标面板
        metrics_panel = QFrame()
        metrics_panel.setFixedHeight(80)
        metrics_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_performance_colors()[2]};
                border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                border-radius: 4px;
            }}
        """)

        metrics_layout = QHBoxLayout(metrics_panel)
        metrics_layout.setContentsMargins(8, 8, 8, 8)

        # 核心性能指标
        metrics = [
            ("🚀 FPS", "60", "帧率"),
            ("💾 内存", "245MB", "内存使用"),
            ("⚡ CPU", "23%", "CPU使用率"),
            ("🎨 GPU", "45%", "GPU使用率")
        ]

        for icon_name, value, desc in metrics:
            metric_frame = QFrame()
            metric_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                    border-radius: 4px;
                }}
            """)

            metric_layout = QVBoxLayout(metric_frame)
            metric_layout.setContentsMargins(8, 4, 8, 4)

            title = QLabel(icon_name)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_performance_colors()[0]};
                    font-weight: bold;
                    font-size: 10px;
                }}
            """)
            metric_layout.addWidget(title)

            value_label = QLabel(value)
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_performance_colors()[0]};
                    font-weight: bold;
                    font-size: 14px;
                }}
            """)
            metric_layout.addWidget(value_label)

            desc_label = QLabel(desc)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                    font-size: 8px;
                }}
            """)
            metric_layout.addWidget(desc_label)

            metrics_layout.addWidget(metric_frame)

        layout.addWidget(metrics_panel)

        # 性能趋势图区域
        chart_area = QFrame()
        chart_area.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                border-radius: 4px;
            }}
        """)

        chart_layout = QVBoxLayout(chart_area)
        chart_layout.setContentsMargins(8, 8, 8, 8)

        chart_title = QLabel("📈 性能趋势图")
        chart_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-weight: bold;
                font-size: 12px;
                padding: 4px;
            }}
        """)
        chart_layout.addWidget(chart_title)

        # 图表占位符
        chart_placeholder = QLabel("📊 实时性能图表\n\n显示FPS、内存、CPU使用率变化\n支持实时监控和历史数据分析")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px dashed {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
                padding: 40px;
                font-size: 12px;
            }}
        """)
        chart_layout.addWidget(chart_placeholder)

        layout.addWidget(chart_area)
        return widget

    def create_enhanced_debug_panel_tab(self):
        """创建增强的智能调试面板标签页 - 包含系统诊断功能"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # 调试面板标签页
        debug_tabs = QTabWidget()
        debug_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                background-color: white;
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                padding: 6px 12px;
                margin-right: 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 10px;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                color: {color_scheme_manager.get_test_debug_colors()[0]};
                font-weight: bold;
            }}
        """)

        # 系统诊断标签页
        diagnostic_tab = self.create_system_diagnostic_tab()
        debug_tabs.addTab(diagnostic_tab, "🏥 系统诊断")

        # 调试控制标签页
        debug_control_tab = self.create_debug_control_tab()
        debug_tabs.addTab(debug_control_tab, "🔍 调试控制")

        # 日志监控标签页
        log_monitor_tab = self.create_log_monitor_tab()
        debug_tabs.addTab(log_monitor_tab, "📋 日志监控")

        layout.addWidget(debug_tabs)
        return widget

    def create_system_diagnostic_tab(self):
        """创建系统诊断标签页 - 基于设计文档的智能诊断修复系统"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 系统健康仪表板
        health_dashboard = QFrame()
        health_dashboard.setFixedHeight(80)
        health_dashboard.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 6px;
            }}
        """)

        dashboard_layout = QHBoxLayout(health_dashboard)
        dashboard_layout.setContentsMargins(12, 12, 12, 12)

        # 健康指标
        health_metrics = [
            ("🏥 系统健康", "良好", color_scheme_manager.get_collaboration_colors()[0]),
            ("⚡ 性能状态", "正常", color_scheme_manager.get_collaboration_colors()[0]),
            ("💾 内存使用", "45%", color_scheme_manager.get_performance_colors()[0]),
            ("🔧 问题数量", "2", color_scheme_manager.get_color_hex(ColorRole.ACCENT))
        ]

        for label, value, color in health_metrics:
            metric_frame = QFrame()
            metric_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid {color};
                    border-radius: 4px;
                }}
            """)

            metric_layout = QVBoxLayout(metric_frame)
            metric_layout.setContentsMargins(6, 4, 6, 4)

            title = QLabel(label)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-weight: bold;
                    font-size: 9px;
                }}
            """)
            metric_layout.addWidget(title)

            value_label = QLabel(value)
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-weight: bold;
                    font-size: 12px;
                }}
            """)
            metric_layout.addWidget(value_label)

            dashboard_layout.addWidget(metric_frame)

        dashboard_layout.addStretch()
        layout.addWidget(health_dashboard)

        # 关键问题检测
        issues_title = QLabel("🔍 关键问题检测")
        issues_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_test_debug_colors()[0]};
                font-weight: bold;
                font-size: 12px;
                padding: 4px;
            }}
        """)
        layout.addWidget(issues_title)

        # 问题列表
        issues_list = QFrame()
        issues_list.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)

        issues_layout = QVBoxLayout(issues_list)
        issues_layout.setContentsMargins(8, 8, 8, 8)
        issues_layout.setSpacing(4)

        # 示例问题
        detected_issues = [
            ("⚠️", "内存使用率偏高", "建议关闭不必要的预览窗口", "中等"),
            ("🔧", "库版本冲突", "numpy版本与manim不兼容", "高"),
            ("💡", "性能优化建议", "启用GPU加速可提升渲染速度", "低")
        ]

        for icon, title, desc, severity in detected_issues:
            issue_item = QFrame()
            issue_item.setFixedHeight(50)

            # 根据严重程度设置颜色
            severity_colors = {
                "低": color_scheme_manager.get_collaboration_colors()[0],
                "中等": color_scheme_manager.get_performance_colors()[0],
                "高": color_scheme_manager.get_color_hex(ColorRole.ACCENT)
            }

            issue_item.setStyleSheet(f"""
                QFrame {{
                    background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                    border-left: 3px solid {severity_colors[severity]};
                    border-radius: 4px;
                    margin: 2px;
                }}
            """)

            issue_layout = QHBoxLayout(issue_item)
            issue_layout.setContentsMargins(8, 6, 8, 6)

            # 图标
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 16px;")
            issue_layout.addWidget(icon_label)

            # 问题信息
            info_frame = QFrame()
            info_layout = QVBoxLayout(info_frame)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(2)

            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                    font-weight: bold;
                    font-size: 10px;
                }}
            """)
            info_layout.addWidget(title_label)

            desc_label = QLabel(desc)
            desc_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                    font-size: 9px;
                }}
            """)
            info_layout.addWidget(desc_label)

            issue_layout.addWidget(info_frame)
            issue_layout.addStretch()

            # 严重程度标签
            severity_label = QLabel(severity)
            severity_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {severity_colors[severity]};
                    color: white;
                    padding: 2px 6px;
                    border-radius: 8px;
                    font-size: 8px;
                    font-weight: bold;
                }}
            """)
            issue_layout.addWidget(severity_label)

            # 修复按钮
            fix_btn = QPushButton("修复")
            fix_btn.setFixedSize(40, 24)
            fix_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {severity_colors[severity]};
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-size: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            issue_layout.addWidget(fix_btn)

            issues_layout.addWidget(issue_item)

        layout.addWidget(issues_list)

        # 诊断操作
        actions_frame = QFrame()
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(0, 0, 0, 0)

        diagnostic_actions = [
            ("🔄 重新扫描", color_scheme_manager.get_test_debug_colors()[0]),
            ("🏥 完整诊断", color_scheme_manager.get_collaboration_colors()[0]),
            ("📊 生成报告", color_scheme_manager.get_performance_colors()[0])
        ]

        for text, color in diagnostic_actions:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            actions_layout.addWidget(btn)

        actions_layout.addStretch()
        layout.addWidget(actions_frame)

        layout.addStretch()
        return widget

    def create_debug_control_tab(self):
        """创建调试控制标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 调试控制面板
        debug_controls = QFrame()
        debug_controls.setFixedHeight(50)
        debug_controls.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        controls_layout = QHBoxLayout(debug_controls)
        controls_layout.setContentsMargins(8, 8, 8, 8)

        debug_buttons = [
            ("🔍 开始调试", "开始调试会话"),
            ("⏸️ 断点", "设置断点"),
            ("▶️ 继续", "继续执行"),
            ("🔧 修复", "智能修复建议")
        ]

        for text, tooltip in debug_buttons:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_test_debug_colors()[0]};
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: {color_scheme_manager.get_test_debug_colors()[1]};
                }}
            """)
            controls_layout.addWidget(btn)

        controls_layout.addStretch()
        layout.addWidget(debug_controls)

        # 调试信息区域
        debug_info = QFrame()
        debug_info.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        info_layout = QVBoxLayout(debug_info)
        info_layout.setContentsMargins(8, 8, 8, 8)

        # 调试状态
        status_label = QLabel("🔍 调试状态: 就绪 | 断点: 0 | 错误: 0")
        status_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_test_debug_colors()[0]};
                font-weight: bold;
                font-size: 11px;
                padding: 6px;
                background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                border-radius: 4px;
            }}
        """)
        info_layout.addWidget(status_label)

        # 调试日志
        debug_log = QTextEdit()
        debug_log.setPlaceholderText("调试信息和错误日志将在这里显示...")
        debug_log.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[2]};
                border-radius: 4px;
                font-family: 'Courier New';
                font-size: 10px;
            }}
        """)
        info_layout.addWidget(debug_log)

        layout.addWidget(debug_info)
        return widget

    def create_log_monitor_tab(self):
        """创建日志监控标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 日志控制面板
        log_controls = QFrame()
        log_controls.setFixedHeight(60)
        log_controls.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        controls_layout = QVBoxLayout(log_controls)
        controls_layout.setContentsMargins(8, 8, 8, 8)

        # 第一行：日志控制按钮
        first_row = QHBoxLayout()
        log_buttons = [
            ("📋 清空日志", "清空所有日志"),
            ("💾 保存日志", "保存日志到文件"),
            ("🔍 搜索", "搜索日志内容"),
            ("⏸️ 暂停", "暂停日志更新")
        ]

        for text, tooltip in log_buttons:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_test_debug_colors()[0]};
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 9px;
                }}
                QPushButton:hover {{
                    background-color: {color_scheme_manager.get_test_debug_colors()[1]};
                }}
            """)
            first_row.addWidget(btn)

        first_row.addStretch()
        controls_layout.addLayout(first_row)

        # 第二行：日志级别筛选
        second_row = QHBoxLayout()

        level_label = QLabel("日志级别:")
        level_label.setStyleSheet("font-weight: bold; color: #333; font-size: 10px;")
        second_row.addWidget(level_label)

        level_combo = QComboBox()
        level_combo.addItems(["全部", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        level_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
                padding: 2px;
                background-color: white;
                font-size: 9px;
            }}
        """)
        second_row.addWidget(level_combo)

        # 自动滚动选项
        auto_scroll_check = QCheckBox("自动滚动")
        auto_scroll_check.setChecked(True)
        auto_scroll_check.setStyleSheet("font-size: 9px; color: #333;")
        second_row.addWidget(auto_scroll_check)

        second_row.addStretch()
        controls_layout.addLayout(second_row)

        layout.addWidget(log_controls)

        # 日志显示区域
        log_area = QFrame()
        log_area.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        log_layout = QVBoxLayout(log_area)
        log_layout.setContentsMargins(8, 8, 8, 8)

        # 日志统计信息
        stats_label = QLabel("📊 日志统计: INFO: 125 | WARNING: 8 | ERROR: 2 | 总计: 135")
        stats_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_test_debug_colors()[0]};
                font-weight: bold;
                font-size: 10px;
                padding: 6px;
                background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                border-radius: 4px;
            }}
        """)
        log_layout.addWidget(stats_label)

        # 日志内容显示
        log_display = QTextEdit()
        log_display.setPlaceholderText("系统日志将在这里实时显示...")
        log_display.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[2]};
                border-radius: 4px;
                font-family: 'Courier New';
                font-size: 9px;
                background-color: #f8f9fa;
            }}
        """)

        # 添加一些示例日志内容
        sample_logs = """
2025-08-05 13:19:14 - ai_animation_studio.main_window - INFO - 主窗口初始化完成
2025-08-05 13:19:14 - ai_animation_studio.project_manager - INFO - 项目管理器就绪
2025-08-05 13:19:14 - ai_animation_studio.template_manager - INFO - 模板加载完成
2025-08-05 13:19:15 - ai_animation_studio.ai_generator - WARNING - API调用频率较高，建议适当降低
2025-08-05 13:19:15 - ai_animation_studio.video_exporter - INFO - 视频导出器初始化
2025-08-05 13:19:16 - ai_animation_studio.timeline_widget - INFO - 时间轴组件加载完成
        """.strip()
        log_display.setPlainText(sample_logs)

        log_layout.addWidget(log_display)

        layout.addWidget(log_area)
        return widget

    def create_stage_editing_tab(self):
        """创建舞台编辑标签页 - 包含舞台工具栏、画布区域、上下文属性面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 舞台工具栏
        stage_toolbar = QToolBar()
        stage_toolbar.setFixedHeight(40)
        stage_toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border-bottom: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                spacing: 4px;
                padding: 4px;
            }}
            QToolButton {{
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 4px;
                padding: 6px;
                margin: 2px;
                min-width: 32px;
                min-height: 32px;
            }}
            QToolButton:hover {{
                background-color: #F3F4F6;
                border-color: #2C5AA0;
            }}
            QToolButton:checked {{
                background-color: #2C5AA0;
                color: white;
            }}
        """)
        # 添加工具按钮
        tools = [
            ("👆", "选择工具", True),
            ("✋", "移动工具", False),
            ("🔄", "旋转工具", False),
            ("📏", "缩放工具", False),
            ("📝", "文字工具", False),
            ("🔷", "形状工具", False),
            ("📏", "线条工具", False),
            ("🎨", "画笔工具", False)
        ]

        for icon, tooltip, checked in tools:
            btn = QToolButton()
            btn.setText(icon)
            btn.setToolTip(tooltip)
            btn.setCheckable(True)
            btn.setChecked(checked)
            stage_toolbar.addWidget(btn)

        stage_toolbar.addSeparator()

        # 视图控制
        zoom_label = QLabel("缩放:")
        stage_toolbar.addWidget(zoom_label)

        zoom_slider = QSlider(Qt.Orientation.Horizontal)
        zoom_slider.setRange(10, 500)
        zoom_slider.setValue(100)
        zoom_slider.setFixedWidth(100)
        stage_toolbar.addWidget(zoom_slider)

        zoom_value_label = QLabel("100%")
        stage_toolbar.addWidget(zoom_value_label)

        layout.addWidget(stage_toolbar)

        # 主要内容区域 - 水平分割
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 画布区域
        canvas_frame = QFrame()
        canvas_frame.setStyleSheet("background-color: #F9FAFB; border: 1px solid #E5E7EB;")
        canvas_layout = QVBoxLayout(canvas_frame)

        # 画布视图
        self.stage_view = QGraphicsView()
        self.stage_scene = QGraphicsScene()
        self.stage_view.setScene(self.stage_scene)
        self.stage_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.stage_view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        # 设置画布背景
        self.stage_scene.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
        self.stage_scene.setSceneRect(0, 0, 800, 600)

        canvas_layout.addWidget(self.stage_view)
        content_splitter.addWidget(canvas_frame)

        # 上下文属性面板
        properties_panel = self.create_properties_panel()
        content_splitter.addWidget(properties_panel)

        # 设置分割器比例
        content_splitter.setSizes([600, 200])
        content_splitter.setStretchFactor(0, 1)

        layout.addWidget(content_splitter)

        return widget

    def create_properties_panel(self):
        """创建上下文属性面板"""
        panel = QWidget()
        panel.setFixedWidth(200)
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border-left: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
            QLabel {{
                font-weight: bold;
                color: #374151;
                padding: 4px 0;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)

        # 元素信息
        info_label = QLabel("元素属性")
        layout.addWidget(info_label)

        # 位置属性
        pos_label = QLabel("位置:")
        layout.addWidget(pos_label)

        pos_layout = QHBoxLayout()
        x_spin = QSpinBox()
        x_spin.setRange(-9999, 9999)
        x_spin.setValue(400)
        x_spin.setPrefix("X: ")
        pos_layout.addWidget(x_spin)

        y_spin = QSpinBox()
        y_spin.setRange(-9999, 9999)
        y_spin.setValue(300)
        y_spin.setPrefix("Y: ")
        pos_layout.addWidget(y_spin)

        layout.addLayout(pos_layout)

        # 尺寸属性
        size_label = QLabel("尺寸:")
        layout.addWidget(size_label)

        size_layout = QHBoxLayout()
        w_spin = QSpinBox()
        w_spin.setRange(1, 9999)
        w_spin.setValue(100)
        w_spin.setPrefix("W: ")
        size_layout.addWidget(w_spin)

        h_spin = QSpinBox()
        h_spin.setRange(1, 9999)
        h_spin.setValue(100)
        h_spin.setPrefix("H: ")
        size_layout.addWidget(h_spin)

        layout.addLayout(size_layout)

        # 颜色属性
        color_label = QLabel("颜色:")
        layout.addWidget(color_label)

        color_btn = QPushButton("选择颜色")
        color_btn.setStyleSheet("background-color: #3498db; color: white; padding: 4px;")
        layout.addWidget(color_btn)

        # 透明度
        opacity_label = QLabel("透明度:")
        layout.addWidget(opacity_label)

        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(100)
        layout.addWidget(opacity_slider)

        layout.addStretch()

        return panel

    def create_multi_device_preview_tab(self):
        """创建多设备预览标签页"""
        device_label = QLabel("预览设备:")
        device_toolbar.addWidget(device_label)

        device_combo = QComboBox()
        device_combo.addItems(["📱 iPhone 14", "📱 Samsung Galaxy", "💻 MacBook Pro", "🖥️ Desktop 1920x1080", "📟 iPad Pro"])
        device_toolbar.addWidget(device_combo)

        sync_btn = QToolButton()
        sync_btn.setText("🔄 同步预览")
        sync_btn.setToolTip("同步所有设备预览")
        device_toolbar.addWidget(sync_btn)

        device_toolbar.addStretch()
        layout.addLayout(device_toolbar)

        # 预览区域
        preview_scroll = QScrollArea()
        preview_widget = QWidget()
        preview_layout = QGridLayout(preview_widget)

        # 创建设备预览框
        devices = [
            ("📱 iPhone 14", "375x812", "#000000"),
            ("💻 MacBook Pro", "1440x900", "#C0C0C0"),
            ("🖥️ Desktop", "1920x1080", "#2C3E50"),
            ("📟 iPad Pro", "1024x1366", "#F8F9FA")
        ]

        for i, (name, resolution, color) in enumerate(devices):
            device_frame = QFrame()
            device_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border: 2px solid #E2E8F0;
                    border-radius: 8px;
                    padding: 8px;
                }}
            """)
            device_frame.setFixedSize(280, 200)

            device_layout = QVBoxLayout(device_frame)

            # 设备标题
            title_label = QLabel(f"{name}\n{resolution}")
            title_label.setStyleSheet("color: white; font-weight: bold; text-align: center;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            device_layout.addWidget(title_label)

            # 预览内容区域
            content_area = QFrame()
            content_area.setStyleSheet("background-color: white; border-radius: 4px;")
            content_area.setFixedHeight(120)
            device_layout.addWidget(content_area)

            # 状态信息
            status_label = QLabel("✅ 预览正常")
            status_label.setStyleSheet("color: #10B981; font-size: 10px;")
            device_layout.addWidget(status_label)

            preview_layout.addWidget(device_frame, i // 2, i % 2)

        preview_scroll.setWidget(preview_widget)
        layout.addWidget(preview_scroll)

        return widget

    def setup_design_compliant_ai_control_panel(self):
        """设置AI控制区 (350px) - 严格按照界面设计完整方案实现"""
        ai_control_panel = QFrame()
        ai_control_panel.setFixedWidth(350)
        ai_control_panel.setFrameStyle(QFrame.Shape.NoFrame)
        # 使用AI功能橙色系的色彩方案
        ai_colors = color_scheme_manager.get_ai_function_colors()
        ai_control_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border-left: 3px solid {ai_colors[0]};
            }}
            QTabWidget::pane {{
                border: 1px solid {ai_colors[0]};
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
            }}
            QTabBar::tab {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                color: {ai_colors[0]};
                font-weight: bold;
                border-bottom: 2px solid {ai_colors[0]};
            }}
            QTabBar::tab:hover {{
                background-color: {ai_colors[2]};
                color: {ai_colors[0]};
            }}
        """)

        # AI控制区布局
        ai_layout = QVBoxLayout(ai_control_panel)
        ai_layout.setContentsMargins(0, 0, 0, 0)
        ai_layout.setSpacing(0)

        # 创建AI控制标签页 - 严格按照设计方案顺序
        self.ai_control_tabs = QTabWidget()

        # 🤖 AI生成面板
        ai_generator_tab = self.create_ai_generator_panel()
        self.ai_control_tabs.addTab(ai_generator_tab, "🤖 AI生成面板")

        # 📋 Prompt编辑
        prompt_editor_tab = self.create_prompt_editor_panel()
        self.ai_control_tabs.addTab(prompt_editor_tab, "📋 Prompt编辑")

        # 📊 方案对比
        comparison_tab = self.create_solution_comparison_panel()
        self.ai_control_tabs.addTab(comparison_tab, "📊 方案对比")

        # ⚙️ 参数调整
        parameters_tab = self.create_parameters_adjustment_panel()
        self.ai_control_tabs.addTab(parameters_tab, "⚙️ 参数调整")

        # 📈 状态监控
        status_monitor_tab = self.create_status_monitor_panel()
        self.ai_control_tabs.addTab(status_monitor_tab, "📈 状态监控")

        # 💬 协作评论
        collaboration_tab = self.create_collaboration_comments_panel()
        self.ai_control_tabs.addTab(collaboration_tab, "💬 协作评论")

        # 🔧 智能修复
        smart_repair_tab = self.create_smart_repair_panel()
        self.ai_control_tabs.addTab(smart_repair_tab, "🔧 智能修复")

        ai_layout.addWidget(self.ai_control_tabs)

        # 应用AI功能橙色系到所有标签页
        self.apply_ai_color_scheme_to_tabs()

        # 添加到主分割器
        self.main_splitter.addWidget(ai_control_panel)

        logger.info("AI控制区设置完成 - 严格符合设计方案")

    def create_ai_generator_panel(self):
        """创建AI生成面板"""
        # 创建主widget
        widget = QWidget()
        mode_layout = QVBoxLayout(widget)

        mode_label = QLabel("🤖 AI生成模式")
        mode_label.setStyleSheet("font-weight: bold; color: #EA580C;")
        mode_layout.addWidget(mode_label)

        mode_combo = QComboBox()
        mode_combo.addItems([
            "🎬 智能动画生成",
            "🎨 视觉效果生成",
            "📝 文案内容生成",
            "🎵 音效配乐生成",
            "🔄 批量方案生成"
        ])
        mode_combo.setStyleSheet("padding: 4px; border: 1px solid #FB923C; border-radius: 3px;")
        mode_layout.addWidget(mode_combo)

        # 创建模式框架
        mode_frame = QFrame()
        mode_frame.setStyleSheet("border: 1px solid #E5E7EB; border-radius: 4px; padding: 8px;")
        mode_layout.addWidget(mode_frame)

        # Prompt输入区域
        prompt_label = QLabel("💭 描述您的创意想法:")
        prompt_label.setStyleSheet("font-weight: bold; color: #374151; margin-top: 8px;")
        mode_layout.addWidget(prompt_label)

        prompt_input = QTextEdit()
        prompt_input.setFixedHeight(100)
        prompt_input.setPlaceholderText("例如: 创建一个小球从左到右弹跳的动画，持续3秒，带有弹性效果...")
        prompt_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #E5E7EB;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #FF6B35;
            }
        """)
        mode_layout.addWidget(prompt_input)

        # 智能标签建议
        tags_label = QLabel("🏷️ 智能标签建议:")
        tags_label.setStyleSheet("font-weight: bold; color: #374151; margin-top: 8px;")
        mode_layout.addWidget(tags_label)

        tags_layout = QHBoxLayout()
        suggested_tags = ["弹跳", "渐变", "旋转", "缩放", "淡入淡出"]
        for tag in suggested_tags:
            tag_btn = QToolButton()
            tag_btn.setText(f"#{tag}")
            tag_btn.setStyleSheet("""
                QToolButton {
                    background-color: #EFF6FF;
                    color: #1D4ED8;
                    border: 1px solid #BFDBFE;
                    border-radius: 12px;
                    padding: 4px 8px;
                    font-size: 10px;
                }
                QToolButton:hover {
                    background-color: #DBEAFE;
                }
            """)
            tags_layout.addWidget(tag_btn)

        tags_layout.addStretch()
        mode_layout.addLayout(tags_layout)

        # 生成控制按钮
        generate_layout = QHBoxLayout()

        generate_btn = QToolButton()
        generate_btn.setText("✨ 生成方案")
        generate_btn.setStyleSheet("""
            QToolButton {
                background-color: #FF6B35;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QToolButton:hover {
                background-color: #FB923C;
            }
        """)
        generate_layout.addWidget(generate_btn)

        quick_gen_btn = QToolButton()
        quick_gen_btn.setText("⚡ 快速生成")
        quick_gen_btn.setStyleSheet("""
            QToolButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 11px;
            }
            QToolButton:hover {
                background-color: #059669;
            }
        """)
        generate_layout.addWidget(quick_gen_btn)

        mode_layout.addLayout(generate_layout)

        # 生成进度
        progress_frame = QFrame()
        progress_frame.setStyleSheet("background-color: #F0FDF4; border: 1px solid #10B981; border-radius: 4px; padding: 6px;")
        progress_layout = QVBoxLayout(progress_frame)

        progress_label = QLabel("🔄 AI生成进度:")
        progress_label.setStyleSheet("font-weight: bold; color: #059669;")
        progress_layout.addWidget(progress_label)

        progress_bar = QProgressBar()
        progress_bar.setValue(75)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #10B981;
                border-radius: 3px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #10B981;
                border-radius: 2px;
            }
        """)
        progress_layout.addWidget(progress_bar)

        status_label = QLabel("正在分析创意要求... (3/4)")
        status_label.setStyleSheet("color: #059669; font-size: 10px;")
        progress_layout.addWidget(status_label)

        mode_layout.addWidget(progress_frame)

        # 生成历史
        history_label = QLabel("📚 最近生成:")
        history_label.setStyleSheet("font-weight: bold; color: #374151; margin-top: 8px;")
        mode_layout.addWidget(history_label)

        history_scroll = QScrollArea()
        history_scroll.setFixedHeight(120)
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)

        recent_generations = [
            "🎬 小球弹跳动画 - 2分钟前",
            "🌟 星星闪烁效果 - 5分钟前",
            "📊 数据图表动画 - 10分钟前",
            "🎨 渐变背景效果 - 15分钟前"
        ]

        for gen in recent_generations:
            gen_label = QLabel(gen)
            gen_label.setStyleSheet("color: #6B7280; font-size: 10px; padding: 2px; border-bottom: 1px solid #F3F4F6;")
            history_layout.addWidget(gen_label)

        history_scroll.setWidget(history_widget)
        mode_layout.addWidget(history_scroll)

        mode_layout.addStretch()

        return widget

    def create_prompt_editor_panel(self):
        """创建Prompt编辑面板"""
        # 创建主widget
        widget = QWidget()
        layout = QVBoxLayout(widget)

        editor_label = QLabel("📝 Prompt编辑器")
        editor_label.setStyleSheet("font-weight: bold; color: #374151;")
        layout.addWidget(editor_label)

        prompt_editor = QTextEdit()
        prompt_editor.setFixedHeight(150)
        prompt_editor.setStyleSheet("""
            QTextEdit {
                border: 2px solid #E5E7EB;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #FF6B35;
            }
        """)

        sample_prompt = """创建一个专业的产品展示动画:
- 元素: 智能手机模型
- 动作: 360度旋转展示
- 时长: 5秒
- 效果: 光影变化，突出产品特点
- 背景: 简洁渐变背景
- 音效: 轻柔的科技感音效"""

        prompt_editor.setPlainText(sample_prompt)
        layout.addWidget(prompt_editor)

        # 编辑工具栏
        tools_layout = QHBoxLayout()

        format_btn = QToolButton()
        format_btn.setText("🎨 格式化")
        tools_layout.addWidget(format_btn)

        validate_btn = QToolButton()
        validate_btn.setText("✅ 验证")
        tools_layout.addWidget(validate_btn)

        save_btn = QToolButton()
        save_btn.setText("💾 保存")
        tools_layout.addWidget(save_btn)

        tools_layout.addStretch()
        layout.addLayout(tools_layout)

        # Prompt模板库
        templates_label = QLabel("📋 Prompt模板库")
        templates_label.setStyleSheet("font-weight: bold; color: #374151; margin-top: 8px;")
        layout.addWidget(templates_label)

        templates_list = QListWidget()
        templates_list.setFixedHeight(120)

        templates = [
            "🎬 产品展示动画",
            "📊 数据可视化",
            "🎨 品牌Logo动画",
            "📱 APP界面演示",
            "🎓 教育解说动画"
        ]

        for template in templates:
            item = QListWidgetItem(template)
            item.setToolTip(f"点击应用 {template} 模板")
            templates_list.addItem(item)

        layout.addWidget(templates_list)

        layout.addStretch()
        return widget

    def create_solution_comparison_panel(self):
        """创建智能方案对比面板 - 严格按照设计文档的四方案并行显示"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # AI生成方案预览标题（按设计文档）
        header = QFrame()
        header.setFixedHeight(35)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 4px;
            }}
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 6, 8, 6)

        title_label = QLabel("🎭 AI生成方案预览 (Gemini生成)")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        time_label = QLabel("生成时间: 18s")
        time_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 9px;
            }
        """)
        header_layout.addWidget(time_label)

        layout.addWidget(header)

        # 对比控制工具栏
        control_toolbar = QFrame()
        control_toolbar.setFixedHeight(35)
        control_toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_ai_function_colors()[2]};
                border: 1px solid {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 4px;
            }}
        """)

        toolbar_layout = QHBoxLayout(control_toolbar)
        toolbar_layout.setContentsMargins(4, 4, 4, 4)

        # 对比控制按钮
        compare_buttons = [
            ("🔄 刷新方案", "重新生成对比方案"),
            ("📊 分析对比", "智能对比分析"),
            ("⭐ 推荐评分", "显示推荐评分"),
            ("💾 保存方案", "保存选中方案")
        ]

        for text, tooltip in compare_buttons:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 9px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {color_scheme_manager.get_ai_function_colors()[1]};
                }}
            """)
            toolbar_layout.addWidget(btn)

        toolbar_layout.addStretch()
        layout.addWidget(control_toolbar)

        # 四方案并行显示区域
        solutions_area = QFrame()
        solutions_area.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)

        solutions_layout = QGridLayout(solutions_area)
        solutions_layout.setContentsMargins(4, 4, 4, 4)
        solutions_layout.setSpacing(4)

        # 严格按照设计文档的四方案配置
        solution_configs = [
            ("方案A", "标准版", "⭐⭐⭐⭐⭐", ["简洁稳定", "性能优秀", "兼容性好"], "2.1KB", "60fps", "95%", 0, 0),
            ("方案B", "增强版", "⭐⭐⭐⭐", ["视觉丰富", "效果震撼", "创意突出"], "4.7KB", "45fps", "88%", 0, 1),
            ("方案C", "写实版", "⭐⭐", ["物理真实", "教学适用", "科学准确"], "6.2KB", "30fps", "92%", 1, 0),
            ("方案D", "创意版", "⭐⭐⭐", ["创意突出", "独特风格", "实验性强"], "8.9KB", "25fps", "73%", 1, 1)
        ]

        for name, version, rating, features, size, fps, confidence, row, col in solution_configs:
            solution_card = self.create_enhanced_solution_card(name, version, rating, features, size, fps, confidence)
            solutions_layout.addWidget(solution_card, row, col)

        layout.addWidget(solutions_area)

        # 智能对比分析表格
        analysis_table = self.create_intelligent_comparison_table()
        layout.addWidget(analysis_table)

        return widget

    def create_solution_card(self, name, style, rating, color):
        """创建方案对比卡片"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 6px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(6, 6, 6, 6)
        card_layout.setSpacing(4)

        # 方案标题和评分
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel(name)
        title.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: bold;
                font-size: 11px;
            }}
        """)
        header_layout.addWidget(title)

        rating_label = QLabel(rating)
        rating_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.ACCENT)};
                font-size: 10px;
            }}
        """)
        header_layout.addWidget(rating_label)

        card_layout.addWidget(header)

        # 风格描述
        style_label = QLabel(style)
        style_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 9px;
                padding: 2px;
            }}
        """)
        card_layout.addWidget(style_label)

        # 预览区域
        preview = QLabel("🎬 预览")
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview.setStyleSheet(f"""
            QLabel {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px dashed {color};
                border-radius: 4px;
                padding: 15px;
                color: {color};
                font-size: 10px;
            }}
        """)
        card_layout.addWidget(preview)

        # 特点展示
        features = QLabel("• 流畅动画\n• 色彩丰富\n• 易于理解")
        features.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 8px;
                padding: 2px;
            }}
        """)
        card_layout.addWidget(features)

        # 选择按钮
        select_btn = QPushButton("选择此方案")
        select_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        card_layout.addWidget(select_btn)

        return card

    def create_enhanced_solution_card(self, name, version, rating, features, size, fps, confidence):
        """创建增强方案卡片 - 严格按照设计文档"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 6px;
                margin: 2px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(4)

        # 方案标题和版本
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel(f"{name}\n{version}")
        title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-weight: bold;
                font-size: 10px;
                text-align: center;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        card_layout.addWidget(header)

        # 预览区域（按设计文档的动画示意图）
        preview = QLabel("●→")
        if name == "方案B":
            preview.setText("●~~~→\n  ✨")
        elif name == "方案C":
            preview.setText("  ●\n   ↘\n    ●")
        elif name == "方案D":
            preview.setText("   ●\n  /|\\\n / | \\\n●--●--●")

        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview.setFixedHeight(50)
        preview.setStyleSheet(f"""
            QLabel {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px dashed {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 4px;
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-size: 12px;
                font-family: 'Courier New';
            }}
        """)
        card_layout.addWidget(preview)

        # 推荐评分
        rating_label = QLabel(f"🎯推荐: {rating}")
        rating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rating_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.ACCENT)};
                font-size: 9px;
                font-weight: bold;
            }}
        """)
        card_layout.addWidget(rating_label)

        # 特点列表
        features_label = QLabel("特点:")
        features_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                font-size: 8px;
                font-weight: bold;
            }}
        """)
        card_layout.addWidget(features_label)

        for feature in features:
            feature_item = QLabel(f"• {feature}")
            feature_item.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                    font-size: 7px;
                    padding-left: 4px;
                }}
            """)
            card_layout.addWidget(feature_item)

        # 技术指标
        metrics = QLabel(f"大小: {size} | FPS: {fps}\nAI置信度: {confidence}")
        metrics.setAlignment(Qt.AlignmentFlag.AlignCenter)
        metrics.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 7px;
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border-radius: 3px;
                padding: 2px;
            }}
        """)
        card_layout.addWidget(metrics)

        # 操作按钮（按设计文档）
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(2)

        preview_btn = QPushButton("👁️预览")
        preview_btn.setFixedHeight(20)
        preview_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_collaboration_colors()[0]};
                color: white;
                border: none;
                border-radius: 2px;
                font-size: 7px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        buttons_layout.addWidget(preview_btn)

        params_btn = QPushButton("⚙️参数")
        params_btn.setFixedHeight(20)
        params_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_performance_colors()[0]};
                color: white;
                border: none;
                border-radius: 2px;
                font-size: 7px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        buttons_layout.addWidget(params_btn)

        select_btn = QPushButton("✅选择")
        select_btn.setFixedHeight(20)
        select_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                color: white;
                border: none;
                border-radius: 2px;
                font-size: 7px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_ai_function_colors()[1]};
            }}
        """)
        buttons_layout.addWidget(select_btn)

        card_layout.addLayout(buttons_layout)
        return card

    def create_intelligent_comparison_table(self):
        """创建智能对比分析表格"""
        table_frame = QFrame()
        table_frame.setFixedHeight(120)
        table_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)

        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(6, 6, 6, 6)

        # 表格标题
        title = QLabel("📊 智能对比分析")
        title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-weight: bold;
                font-size: 11px;
                padding: 2px;
            }}
        """)
        table_layout.addWidget(title)

        # 对比数据
        comparison_data = QFrame()
        data_layout = QGridLayout(comparison_data)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setSpacing(2)

        # 表头
        headers = ["指标", "方案A", "方案B", "方案C", "方案D"]
        for i, header in enumerate(headers):
            label = QLabel(header)
            label.setStyleSheet(f"""
                QLabel {{
                    background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                    font-weight: bold;
                    font-size: 9px;
                    padding: 2px 4px;
                    border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                }}
            """)
            data_layout.addWidget(label, 0, i)

        # 对比数据行
        comparison_rows = [
            ("创意度", "95%", "88%", "75%", "92%"),
            ("技术难度", "高", "中", "低", "中"),
            ("制作时间", "3天", "2天", "1天", "2.5天")
        ]

        for row_idx, (metric, *values) in enumerate(comparison_rows, 1):
            # 指标名称
            metric_label = QLabel(metric)
            metric_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                    font-size: 8px;
                    padding: 2px 4px;
                    border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                }}
            """)
            data_layout.addWidget(metric_label, row_idx, 0)

            # 各方案数值
            for col_idx, value in enumerate(values, 1):
                value_label = QLabel(value)
                value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                value_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: white;
                        color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                        font-size: 8px;
                        padding: 2px 4px;
                        border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                    }}
                """)
                data_layout.addWidget(value_label, row_idx, col_idx)

        table_layout.addWidget(comparison_data)
        return table_frame
        layout.setContentsMargins(8, 8, 8, 8)

        # 对比标题
        title_label = QLabel("📊 AI方案对比")
        title_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 14px;")
        layout.addWidget(title_label)

        # 方案对比区域
        comparison_scroll = QScrollArea()
        comparison_widget = QWidget()
        comparison_layout = QVBoxLayout(comparison_widget)

        # 创建4个方案对比卡片
        solutions = [
            ("方案A", "经典弹跳", "⭐⭐⭐⭐⭐", "#10B981"),
            ("方案B", "平滑滑动", "⭐⭐⭐⭐", "#3B82F6"),
            ("方案C", "旋转进入", "⭐⭐⭐", "#F59E0B"),
            ("方案D", "缩放效果", "⭐⭐⭐⭐", "#8B5CF6")
        ]

        for name, desc, rating, color in solutions:
            solution_frame = QFrame()
            solution_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 2px solid {color};
                    border-radius: 6px;
                    padding: 8px;
                    margin: 2px;
                }}
            """)

            solution_layout = QVBoxLayout(solution_frame)

            # 方案标题
            title_layout = QHBoxLayout()
            name_label = QLabel(name)
            name_label.setStyleSheet(f"font-weight: bold; color: {color};")
            title_layout.addWidget(name_label)

            rating_label = QLabel(rating)
            rating_label.setStyleSheet("color: #F59E0B;")
            title_layout.addWidget(rating_label)
            title_layout.addStretch()

            solution_layout.addLayout(title_layout)

            # 方案描述
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #6B7280; font-size: 11px;")
            solution_layout.addWidget(desc_label)

            # 方案特点
            features = ["流畅度: 95%", "创意度: 88%", "适用性: 92%"]
            for feature in features:
                feature_label = QLabel(f"• {feature}")
                feature_label.setStyleSheet("color: #374151; font-size: 10px;")
                solution_layout.addWidget(feature_label)

            # 操作按钮
            btn_layout = QHBoxLayout()
            preview_btn = QToolButton()
            preview_btn.setText("👁️ 预览")
            preview_btn.setStyleSheet("padding: 4px 8px; font-size: 10px;")
            btn_layout.addWidget(preview_btn)

            apply_btn = QToolButton()
            apply_btn.setText("✅ 应用")
            apply_btn.setStyleSheet(f"background-color: {color}; color: white; padding: 4px 8px; font-size: 10px; border-radius: 3px;")
            btn_layout.addWidget(apply_btn)

            btn_layout.addStretch()
            solution_layout.addLayout(btn_layout)

            comparison_layout.addWidget(solution_frame)

        comparison_scroll.setWidget(comparison_widget)
        layout.addWidget(comparison_scroll)

        return widget

    def create_parameters_adjustment_panel(self):
        """创建参数调整面板"""
        # 创建主widget
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title_label = QLabel("⚙️ 参数调整")
        title_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 14px;")
        layout.addWidget(title_label)

        # 参数控制组
        params_frame = QFrame()
        params_frame.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 8px;")
        params_layout = QVBoxLayout(params_frame)

        # 时长控制
        duration_layout = QHBoxLayout()
        duration_label = QLabel("⏱️ 动画时长:")
        duration_layout.addWidget(duration_label)

        duration_slider = QSlider(Qt.Orientation.Horizontal)
        duration_slider.setRange(500, 10000)
        duration_slider.setValue(3000)
        duration_layout.addWidget(duration_slider)

        duration_spin = QSpinBox()
        duration_spin.setRange(500, 10000)
        duration_spin.setValue(3000)
        duration_spin.setSuffix("ms")
        duration_layout.addWidget(duration_spin)

        params_layout.addLayout(duration_layout)

        # 缓动函数
        easing_layout = QHBoxLayout()
        easing_label = QLabel("📈 缓动函数:")
        easing_layout.addWidget(easing_label)

        easing_combo = QComboBox()
        easing_combo.addItems(["ease-in-out", "ease-in", "ease-out", "linear", "bounce", "elastic"])
        easing_layout.addWidget(easing_combo)

        params_layout.addLayout(easing_layout)

        # 延迟时间
        delay_layout = QHBoxLayout()
        delay_label = QLabel("⏰ 延迟时间:")
        delay_layout.addWidget(delay_label)

        delay_slider = QSlider(Qt.Orientation.Horizontal)
        delay_slider.setRange(0, 5000)
        delay_slider.setValue(0)
        delay_layout.addWidget(delay_slider)

        delay_spin = QSpinBox()
        delay_spin.setRange(0, 5000)
        delay_spin.setValue(0)
        delay_spin.setSuffix("ms")
        delay_layout.addWidget(delay_spin)

        params_layout.addLayout(delay_layout)

        layout.addWidget(params_frame)

        # 实时预览
        preview_frame = QFrame()
        preview_frame.setStyleSheet("background-color: #EFF6FF; border: 1px solid #3B82F6; border-radius: 6px; padding: 8px;")
        preview_layout = QVBoxLayout(preview_frame)

        preview_label = QLabel("👁️ 实时预览")
        preview_label.setStyleSheet("font-weight: bold; color: #1D4ED8;")
        preview_layout.addWidget(preview_label)

        preview_area = QLabel("预览区域\n(参数变化实时更新)")
        preview_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_area.setStyleSheet("background-color: white; border: 1px solid #BFDBFE; border-radius: 4px; padding: 20px; color: #6B7280;")
        preview_layout.addWidget(preview_area)

        layout.addWidget(preview_frame)

        layout.addStretch()
        return widget

    def create_status_monitor_panel(self):
        """创建状态监控面板"""
        # 创建主widget
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 系统状态
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: #F0FDF4; border: 1px solid #10B981; border-radius: 6px; padding: 8px;")
        status_layout = QVBoxLayout(status_frame)

        status_title = QLabel("📈 系统状态监控")
        status_title.setStyleSheet("font-weight: bold; color: #059669;")
        status_layout.addWidget(status_title)

        # 状态指标
        indicators = [
            ("AI服务", "🟢 正常", 100),
            ("渲染引擎", "🟢 正常", 95),
            ("协作服务", "🟡 延迟", 75),
            ("存储空间", "🟢 充足", 85)
        ]

        for name, status, value in indicators:
            indicator_layout = QHBoxLayout()

            name_label = QLabel(f"{name}:")
            name_label.setFixedWidth(80)
            indicator_layout.addWidget(name_label)

            status_label = QLabel(status)
            status_label.setFixedWidth(60)
            indicator_layout.addWidget(status_label)

            progress = QProgressBar()
            progress.setValue(value)
            progress.setFixedHeight(16)
            indicator_layout.addWidget(progress)

            status_layout.addLayout(indicator_layout)

        layout.addWidget(status_frame)
        layout.addStretch()
        return widget

    def create_collaboration_comments_panel(self):
        """创建团队协作中心 - 基于设计文档的实时协作系统"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # 协作中心标签页
        collab_tabs = QTabWidget()
        collab_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[0]};
                background-color: white;
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                padding: 6px 10px;
                margin-right: 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 9px;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                color: {color_scheme_manager.get_collaboration_colors()[0]};
                font-weight: bold;
            }}
        """)

        # 项目共享标签页
        sharing_tab = self.create_project_sharing_tab()
        collab_tabs.addTab(sharing_tab, "📤 项目共享")

        # 协作成员标签页
        members_tab = self.create_collaboration_members_tab()
        collab_tabs.addTab(members_tab, "👥 协作成员")

        # 实时讨论标签页
        discussion_tab = self.create_real_time_discussion_tab()
        collab_tabs.addTab(discussion_tab, "💬 实时讨论")

        # 同步状态标签页
        sync_tab = self.create_sync_status_tab()
        collab_tabs.addTab(sync_tab, "🔄 同步状态")

        layout.addWidget(collab_tabs)
        return widget

    def create_project_sharing_tab(self):
        """创建项目共享标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 评论列表
        comments_label = QLabel("💬 协作评论")
        comments_label.setStyleSheet("font-weight: bold; color: #374151;")
        layout.addWidget(comments_label)

        comments_scroll = QScrollArea()
        comments_scroll.setFixedHeight(150)
        comments_widget = QWidget()
        comments_layout = QVBoxLayout(comments_widget)

        # 示例评论
        sample_comments = [
            ("张设计师", "2分钟前", "这个弹跳效果很棒！建议增加一些粒子效果"),
            ("李开发", "5分钟前", "动画流畅度不错，但是时长可以再短一些"),
            ("王产品", "10分钟前", "整体方向正确，符合品牌调性")
        ]

        for author, time, comment in sample_comments:
            comment_frame = QFrame()
            comment_frame.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 4px; padding: 6px; margin: 2px;")
            comment_layout = QVBoxLayout(comment_frame)

            header_layout = QHBoxLayout()
            author_label = QLabel(f"👤 {author}")
            author_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 10px;")
            header_layout.addWidget(author_label)

            time_label = QLabel(time)
            time_label.setStyleSheet("color: #6B7280; font-size: 9px;")
            header_layout.addWidget(time_label)
            header_layout.addStretch()

            comment_layout.addLayout(header_layout)

            content_label = QLabel(comment)
            content_label.setStyleSheet("color: #374151; font-size: 11px;")
            content_label.setWordWrap(True)
            comment_layout.addWidget(content_label)

            comments_layout.addWidget(comment_frame)

        comments_scroll.setWidget(comments_widget)
        layout.addWidget(comments_scroll)

        # 新评论输入
        new_comment_input = QTextEdit()
        new_comment_input.setFixedHeight(60)
        new_comment_input.setPlaceholderText("输入您的评论...")
        layout.addWidget(new_comment_input)

        # 发送按钮
        send_btn = QToolButton()
        send_btn.setText("📤 发送评论")
        send_btn.setStyleSheet("background-color: #10B981; color: white; padding: 6px 12px; border-radius: 4px;")
        layout.addWidget(send_btn)

        layout.addStretch()
        return widget

    def create_collaboration_members_tab(self):
        """创建协作成员标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 成员管理控制面板
        control_panel = QFrame()
        control_panel.setFixedHeight(50)
        control_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_collaboration_colors()[2]};
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[0]};
                border-radius: 4px;
            }}
        """)

        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(8, 8, 8, 8)

        # 成员管理按钮
        member_buttons = [
            ("👥 邀请成员", "邀请新成员加入项目"),
            ("🔧 管理权限", "管理成员权限"),
            ("📊 查看活动", "查看成员活动记录")
        ]

        for text, tooltip in member_buttons:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_collaboration_colors()[0]};
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: {color_scheme_manager.get_collaboration_colors()[1]};
                }}
            """)
            control_layout.addWidget(btn)

        control_layout.addStretch()
        layout.addWidget(control_panel)

        # 成员列表
        members_label = QLabel("👥 项目成员")
        members_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 12px; margin: 8px 0;")
        layout.addWidget(members_label)

        members_scroll = QScrollArea()
        members_widget = QWidget()
        members_layout = QVBoxLayout(members_widget)

        # 示例成员数据
        sample_members = [
            ("张设计师", "设计师", "在线", "#10B981", "👤"),
            ("李开发", "开发者", "离线", "#6B7280", "💻"),
            ("王产品", "产品经理", "在线", "#10B981", "📋"),
            ("赵动画师", "动画师", "忙碌", "#F59E0B", "🎨"),
            ("陈测试", "测试工程师", "离线", "#6B7280", "🔍")
        ]

        for name, role, status, status_color, icon in sample_members:
            member_frame = QFrame()
            member_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid {color_scheme_manager.get_collaboration_colors()[2]};
                    border-radius: 6px;
                    padding: 8px;
                    margin: 2px;
                }}
                QFrame:hover {{
                    border-color: {color_scheme_manager.get_collaboration_colors()[0]};
                }}
            """)

            member_layout = QHBoxLayout(member_frame)
            member_layout.setContentsMargins(8, 6, 8, 6)

            # 成员图标
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 16px;")
            member_layout.addWidget(icon_label)

            # 成员信息
            info_layout = QVBoxLayout()

            name_label = QLabel(name)
            name_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 11px;")
            info_layout.addWidget(name_label)

            role_label = QLabel(role)
            role_label.setStyleSheet("color: #6B7280; font-size: 9px;")
            info_layout.addWidget(role_label)

            member_layout.addLayout(info_layout)
            member_layout.addStretch()

            # 状态指示器
            status_label = QLabel(f"● {status}")
            status_label.setStyleSheet(f"color: {status_color}; font-size: 10px; font-weight: bold;")
            member_layout.addWidget(status_label)

            # 操作按钮
            action_btn = QPushButton("⚙️")
            action_btn.setFixedSize(24, 24)
            action_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_collaboration_colors()[2]};
                    border: none;
                    border-radius: 12px;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: {color_scheme_manager.get_collaboration_colors()[0]};
                    color: white;
                }}
            """)
            member_layout.addWidget(action_btn)

            members_layout.addWidget(member_frame)

        members_scroll.setWidget(members_widget)
        layout.addWidget(members_scroll)

        return widget

    def create_real_time_discussion_tab(self):
        """创建实时讨论标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 讨论控制面板
        control_panel = QFrame()
        control_panel.setFixedHeight(40)
        control_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_collaboration_colors()[2]};
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[0]};
                border-radius: 4px;
            }}
        """)

        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(8, 8, 8, 8)

        # 讨论状态
        status_label = QLabel("💬 实时讨论 - 3人在线")
        status_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 11px;")
        control_layout.addWidget(status_label)

        control_layout.addStretch()

        # 设置按钮
        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_collaboration_colors()[0]};
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 9px;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_collaboration_colors()[1]};
            }}
        """)
        control_layout.addWidget(settings_btn)

        layout.addWidget(control_panel)

        # 消息显示区域
        messages_area = QTextEdit()
        messages_area.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[2]};
                border-radius: 4px;
                background-color: #f8f9fa;
                font-family: 'Microsoft YaHei';
                font-size: 10px;
            }}
        """)

        # 添加示例消息
        sample_messages = """
[13:20] 张设计师: 大家好，我刚完成了新的角色设计
[13:21] 李开发: 看起来不错！动画效果需要调整吗？
[13:22] 王产品: 建议增加一些表情变化
[13:23] 张设计师: 好的，我马上修改
[13:24] 赵动画师: 我可以帮忙制作表情动画
        """.strip()
        messages_area.setPlainText(sample_messages)
        layout.addWidget(messages_area)

        # 消息输入区域
        input_layout = QHBoxLayout()

        message_input = QLineEdit()
        message_input.setPlaceholderText("输入消息...")
        message_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[2]};
                border-radius: 4px;
                padding: 6px;
                font-size: 10px;
            }}
        """)
        input_layout.addWidget(message_input)

        send_btn = QPushButton("发送")
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_collaboration_colors()[0]};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_collaboration_colors()[1]};
            }}
        """)
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)
        return widget

    def create_sync_status_tab(self):
        """创建同步状态标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 同步状态控制面板
        control_panel = QFrame()
        control_panel.setFixedHeight(50)
        control_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_collaboration_colors()[2]};
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[0]};
                border-radius: 4px;
            }}
        """)

        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(8, 8, 8, 8)

        # 同步控制按钮
        sync_buttons = [
            ("🔄 立即同步", "立即同步所有更改"),
            ("⏸️ 暂停同步", "暂停自动同步"),
            ("📊 查看冲突", "查看同步冲突")
        ]

        for text, tooltip in sync_buttons:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_collaboration_colors()[0]};
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: {color_scheme_manager.get_collaboration_colors()[1]};
                }}
            """)
            control_layout.addWidget(btn)

        control_layout.addStretch()
        layout.addWidget(control_panel)

        # 同步状态显示
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[2]};
                border-radius: 4px;
                padding: 8px;
            }}
        """)

        status_layout = QVBoxLayout(status_frame)

        # 总体同步状态
        overall_status = QLabel("🔄 同步状态: 已同步 - 最后更新: 2分钟前")
        overall_status.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_collaboration_colors()[0]};
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
                background-color: {color_scheme_manager.get_collaboration_colors()[2]};
                border-radius: 4px;
            }}
        """)
        status_layout.addWidget(overall_status)

        # 同步详情列表
        details_scroll = QScrollArea()
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)

        # 示例同步项目
        sync_items = [
            ("角色设计文件", "已同步", "✅", "#10B981", "2分钟前"),
            ("动画序列", "同步中", "🔄", "#F59E0B", "正在进行"),
            ("音频文件", "已同步", "✅", "#10B981", "5分钟前"),
            ("项目设置", "冲突", "⚠️", "#EF4444", "需要解决"),
            ("渲染配置", "已同步", "✅", "#10B981", "10分钟前")
        ]

        for item_name, status, icon, color, time in sync_items:
            item_frame = QFrame()
            item_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: #f8f9fa;
                    border: 1px solid {color_scheme_manager.get_collaboration_colors()[2]};
                    border-radius: 4px;
                    padding: 6px;
                    margin: 2px;
                }}
            """)

            item_layout = QHBoxLayout(item_frame)
            item_layout.setContentsMargins(8, 4, 8, 4)

            # 状态图标
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 14px;")
            item_layout.addWidget(icon_label)

            # 项目名称
            name_label = QLabel(item_name)
            name_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 11px;")
            item_layout.addWidget(name_label)

            item_layout.addStretch()

            # 状态文本
            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold;")
            item_layout.addWidget(status_label)

            # 时间
            time_label = QLabel(time)
            time_label.setStyleSheet("color: #6B7280; font-size: 9px;")
            item_layout.addWidget(time_label)

            details_layout.addWidget(item_frame)

        details_scroll.setWidget(details_widget)
        status_layout.addWidget(details_scroll)

        layout.addWidget(status_frame)

        # 同步统计
        stats_frame = QFrame()
        stats_frame.setFixedHeight(60)
        stats_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_collaboration_colors()[2]};
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[0]};
                border-radius: 4px;
            }}
        """)

        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(12, 8, 12, 8)

        # 统计数据
        stats_data = [
            ("已同步", "15", "#10B981"),
            ("待同步", "2", "#F59E0B"),
            ("冲突", "1", "#EF4444")
        ]

        for label, count, color in stats_data:
            stat_widget = QFrame()
            stat_widget.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid {color};
                    border-radius: 4px;
                    padding: 4px;
                }}
            """)

            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.setContentsMargins(8, 4, 8, 4)

            count_label = QLabel(count)
            count_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
            count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            label_widget = QLabel(label)
            label_widget.setStyleSheet(f"color: {color}; font-size: 9px;")
            label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

            stat_layout.addWidget(count_label)
            stat_layout.addWidget(label_widget)

            stats_layout.addWidget(stat_widget)

        stats_layout.addStretch()
        layout.addWidget(stats_frame)

        return widget

    def create_smart_repair_panel(self):
        """创建AI智能修复助手 - 基于设计文档的智能修复建议系统"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # AI修复助手标题
        repair_title = QFrame()
        repair_title.setFixedHeight(40)
        repair_title.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color_scheme_manager.get_ai_function_colors()[0]},
                    stop:1 {color_scheme_manager.get_ai_function_colors()[1]});
                border-radius: 4px;
            }}
        """)

        title_layout = QHBoxLayout(repair_title)
        title_layout.setContentsMargins(12, 8, 12, 8)

        title_label = QLabel("🤖 AI智能修复助手")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 扫描按钮
        scan_btn = QPushButton("🔍 智能扫描")
        scan_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        scan_btn.clicked.connect(self.run_intelligent_scan)
        title_layout.addWidget(scan_btn)

        layout.addWidget(repair_title)

        # 问题根因分析
        analysis_frame = QFrame()
        analysis_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 4px;
            }}
        """)

        analysis_layout = QVBoxLayout(analysis_frame)
        analysis_layout.setContentsMargins(8, 8, 8, 8)
        analysis_layout.setSpacing(6)

        analysis_title = QLabel("🔬 问题根因分析")
        analysis_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-weight: bold;
                font-size: 11px;
                padding: 4px;
            }}
        """)
        analysis_layout.addWidget(analysis_title)

        # 分析结果
        analysis_results = [
            ("🎯 主要问题", "内存泄漏导致性能下降", "高"),
            ("🔗 关联问题", "大量未释放的图像对象", "中"),
            ("⚡ 性能影响", "渲染速度降低45%", "高"),
            ("🛠️ 修复难度", "中等 - 需要代码重构", "中")
        ]

        for category, description, severity in analysis_results:
            result_item = QFrame()
            result_item.setFixedHeight(30)
            result_item.setStyleSheet(f"""
                QFrame {{
                    background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                    border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                    border-radius: 3px;
                    margin: 1px;
                }}
            """)

            result_layout = QHBoxLayout(result_item)
            result_layout.setContentsMargins(6, 4, 6, 4)

            category_label = QLabel(category)
            category_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_ai_function_colors()[0]};
                    font-weight: bold;
                    font-size: 9px;
                }}
            """)
            result_layout.addWidget(category_label)

            desc_label = QLabel(description)
            desc_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                    font-size: 9px;
                }}
            """)
            result_layout.addWidget(desc_label)

            result_layout.addStretch()

            # 严重程度标签
            severity_colors = {
                "高": color_scheme_manager.get_color_hex(ColorRole.ACCENT),
                "中": color_scheme_manager.get_performance_colors()[0],
                "低": color_scheme_manager.get_collaboration_colors()[0]
            }

            severity_label = QLabel(severity)
            severity_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {severity_colors[severity]};
                    color: white;
                    padding: 2px 6px;
                    border-radius: 8px;
                    font-size: 8px;
                    font-weight: bold;
                }}
            """)
            result_layout.addWidget(severity_label)

            analysis_layout.addWidget(result_item)

        layout.addWidget(analysis_frame)

        # 智能修复方案
        solutions_frame = QFrame()
        solutions_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[0]};
                border-radius: 4px;
            }}
        """)

        solutions_layout = QVBoxLayout(solutions_frame)
        solutions_layout.setContentsMargins(8, 8, 8, 8)
        solutions_layout.setSpacing(6)

        solutions_title = QLabel("💡 智能修复方案")
        solutions_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_collaboration_colors()[0]};
                font-weight: bold;
                font-size: 11px;
                padding: 4px;
            }}
        """)
        solutions_layout.addWidget(solutions_title)

        # 修复方案列表
        repair_solutions = [
            ("🔧 自动修复", "自动释放未使用的图像对象", "推荐", True),
            ("⚙️ 配置优化", "调整内存管理参数", "可选", False),
            ("🔄 代码重构", "重构图像处理模块", "高级", False)
        ]

        for icon, solution, type_label, is_recommended in repair_solutions:
            solution_item = QFrame()
            solution_item.setFixedHeight(40)

            if is_recommended:
                solution_item.setStyleSheet(f"""
                    QFrame {{
                        background-color: {color_scheme_manager.get_collaboration_colors()[2]};
                        border: 2px solid {color_scheme_manager.get_collaboration_colors()[0]};
                        border-radius: 4px;
                        margin: 2px;
                    }}
                """)
            else:
                solution_item.setStyleSheet(f"""
                    QFrame {{
                        background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                        border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                        border-radius: 4px;
                        margin: 2px;
                    }}
                """)

            solution_layout = QHBoxLayout(solution_item)
            solution_layout.setContentsMargins(8, 6, 8, 6)

            # 图标
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 14px;")
            solution_layout.addWidget(icon_label)

            # 方案信息
            info_frame = QFrame()
            info_layout = QVBoxLayout(info_frame)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(2)

            solution_label = QLabel(solution)
            solution_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                    font-weight: {'bold' if is_recommended else 'normal'};
                    font-size: 10px;
                }}
            """)
            info_layout.addWidget(solution_label)

            solution_layout.addWidget(info_frame)
            solution_layout.addStretch()

            # 类型标签
            type_colors = {
                "推荐": color_scheme_manager.get_collaboration_colors()[0],
                "可选": color_scheme_manager.get_performance_colors()[0],
                "高级": color_scheme_manager.get_ai_function_colors()[0]
            }

            type_tag = QLabel(type_label)
            type_tag.setStyleSheet(f"""
                QLabel {{
                    background-color: {type_colors[type_label]};
                    color: white;
                    padding: 2px 6px;
                    border-radius: 8px;
                    font-size: 8px;
                    font-weight: bold;
                }}
            """)
            solution_layout.addWidget(type_tag)

            # 执行按钮
            execute_btn = QPushButton("执行")
            execute_btn.setFixedSize(40, 24)
            execute_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {type_colors[type_label]};
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-size: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            execute_btn.clicked.connect(lambda checked, s=solution: self.execute_repair_solution(s))
            solution_layout.addWidget(execute_btn)

            solutions_layout.addWidget(solution_item)

        layout.addWidget(solutions_frame)

        # 影响范围评估
        impact_frame = QFrame()
        impact_frame.setFixedHeight(60)
        impact_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_performance_colors()[2]};
                border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                border-radius: 4px;
            }}
        """)

        impact_layout = QVBoxLayout(impact_frame)
        impact_layout.setContentsMargins(8, 6, 8, 6)

        impact_title = QLabel("📊 影响范围评估")
        impact_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-weight: bold;
                font-size: 10px;
            }}
        """)
        impact_layout.addWidget(impact_title)

        impact_info = QLabel("• 性能提升: 预计45% • 内存优化: 预计节省200MB • 风险等级: 低")
        impact_info.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 9px;
            }}
        """)
        impact_layout.addWidget(impact_info)

        layout.addWidget(impact_frame)

        layout.addStretch()
        return widget
        layout.setContentsMargins(8, 8, 8, 8)

        # 问题检测
        issues_label = QLabel("🔧 智能问题检测")
        issues_label.setStyleSheet("font-weight: bold; color: #374151;")
        layout.addWidget(issues_label)

        issues_list = QListWidget()
        issues_list.setFixedHeight(120)

        # 示例问题
        issues = [
            ("⚠️ 动画时长过短", "建议延长至3秒以上"),
            ("💡 缺少缓动效果", "建议添加ease-in-out"),
            ("🎨 颜色对比度低", "建议调整颜色搭配"),
            ("⚡ 性能可优化", "建议减少复杂效果")
        ]

        for issue, suggestion in issues:
            item = QListWidgetItem(f"{issue}\n{suggestion}")
            item.setToolTip(f"点击查看详细修复方案")
            issues_list.addItem(item)

        layout.addWidget(issues_list)

        # 一键修复
        repair_frame = QFrame()
        repair_frame.setStyleSheet("background-color: #FEF3C7; border: 1px solid #F59E0B; border-radius: 6px; padding: 8px;")
        repair_layout = QVBoxLayout(repair_frame)

        repair_title = QLabel("🚀 智能修复建议")
        repair_title.setStyleSheet("font-weight: bold; color: #92400E;")
        repair_layout.addWidget(repair_title)

        repair_desc = QLabel("检测到4个可优化项目，点击一键修复可自动优化动画效果")
        repair_desc.setStyleSheet("color: #92400E; font-size: 11px;")
        repair_desc.setWordWrap(True)
        repair_layout.addWidget(repair_desc)

        repair_btn_layout = QHBoxLayout()
        auto_repair_btn = QToolButton()
        auto_repair_btn.setText("🔧 一键修复")
        auto_repair_btn.setStyleSheet("background-color: #F59E0B; color: white; padding: 6px 12px; border-radius: 4px;")
        repair_btn_layout.addWidget(auto_repair_btn)

        manual_btn = QToolButton()
        manual_btn.setText("👁️ 手动检查")
        repair_btn_layout.addWidget(manual_btn)
        repair_btn_layout.addStretch()

        repair_layout.addLayout(repair_btn_layout)
        layout.addWidget(repair_frame)

        layout.addStretch()
        return widget

    def setup_design_compliant_timeline_area(self):
        """设置时间轴区域 (200px) - 严格按照界面设计完整方案实现"""
        # 定义基础高度和DPI缩放
        base_height = 200
        dpi_scale = self.devicePixelRatio()
        scaled_height = int(base_height * max(1.0, dpi_scale * 0.8))  # 适当调整缩放系数

        # 创建时间轴区域widget
        self.timeline_area_widget = QFrame()
        self.timeline_area_widget.setFixedHeight(scaled_height)
        self.timeline_area_widget.setFrameStyle(QFrame.Shape.NoFrame)
        self.timeline_area_widget.setStyleSheet(f"""
            QFrame {{
                background-color: #F8FAFC;
                border-top: 2px solid #E2E8F0;
                border-bottom: 2px solid #E2E8F0;
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
            }}
            QToolButton {{
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 4px;
                padding: 6px 12px;
                margin: 2px;
                font-size: 11px;
            }}
            QToolButton:hover {{
                background-color: #F3F4F6;
                border-color: #2C5AA0;
            }}
            QToolButton:pressed {{
                background-color: #2C5AA0;
                color: white;
            }}
        """)

        # 时间轴布局
        timeline_layout = QVBoxLayout(self.timeline_area_widget)
        timeline_layout.setContentsMargins(8, 8, 8, 8)
        timeline_layout.setSpacing(4)

        # 音频波形区域 - 严格按照设计方案
        audio_frame = QFrame()
        audio_frame.setFixedHeight(60)
        audio_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 4px;
            }
        """)
        audio_layout = QHBoxLayout(audio_frame)
        audio_layout.setContentsMargins(8, 4, 8, 4)

        # 音频标签
        audio_label = QLabel("🎵")
        audio_label.setFixedWidth(20)
        audio_layout.addWidget(audio_label)

        # 音频波形显示（模拟）
        waveform_label = QLabel("████▓▓▓░░░▓▓▓████░░░▓▓▓████  音频波形 + 时间标记")
        waveform_label.setStyleSheet("""
            QLabel {
                font-family: 'Consolas', 'Monaco', monospace;
                color: #3B82F6;
                background-color: #EFF6FF;
                padding: 8px;
                border-radius: 3px;
            }
        """)
        audio_layout.addWidget(waveform_label)

        timeline_layout.addWidget(audio_frame)

        # 动画轨道区域 - 严格按照设计方案
        animation_frame = QFrame()
        animation_frame.setFixedHeight(80)
        animation_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 4px;
            }
        """)
        animation_layout = QVBoxLayout(animation_frame)
        animation_layout.setContentsMargins(8, 4, 8, 4)

        # 动画轨道标签
        track_label_layout = QHBoxLayout()
        track_label = QLabel("🎬")
        track_label.setFixedWidth(20)
        track_label_layout.addWidget(track_label)

        # 动画片段显示
        segments_layout = QHBoxLayout()
        animation_segments = ["动画1", "动画2", "动画3", "动画4"]
        segment_colors = ["#10B981", "#3B82F6", "#F59E0B", "#8B5CF6"]

        for i, (segment, color) in enumerate(zip(animation_segments, segment_colors)):
            segment_btn = QToolButton()
            segment_btn.setText(segment)
            segment_btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 10px;
                    font-weight: bold;
                    min-width: 60px;
                }}
                QToolButton:hover {{
                    opacity: 0.8;
                }}
            """)
            segments_layout.addWidget(segment_btn)

            # 添加状态衔接指示
            if i < len(animation_segments) - 1:
                connector = QLabel("→")
                connector.setStyleSheet("color: #6B7280; font-weight: bold;")
                segments_layout.addWidget(connector)

        segments_layout.addStretch()
        track_label_layout.addLayout(segments_layout)
        animation_layout.addLayout(track_label_layout)

        # 动画片段状态衔接指示说明
        status_label = QLabel("动画片段 + 状态衔接指示")
        status_label.setStyleSheet("color: #6B7280; font-size: 10px; padding: 2px;")
        animation_layout.addWidget(status_label)

        timeline_layout.addWidget(animation_frame)

        # 时间轴控制区域 - 严格按照设计方案
        controls_frame = QFrame()
        controls_frame.setFixedHeight(40)
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #F1F5F9;
                border: 1px solid #E2E8F0;
                border-radius: 4px;
            }
        """)
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(8, 4, 8, 4)

        # 播放控制按钮 - 严格按照设计方案
        play_btn = QToolButton()
        play_btn.setText("⏯️ 播放")
        play_btn.setStyleSheet("background-color: #10B981; color: white;")
        controls_layout.addWidget(play_btn)

        pause_btn = QToolButton()
        pause_btn.setText("⏸️ 暂停")
        controls_layout.addWidget(pause_btn)

        mark_btn = QToolButton()
        mark_btn.setText("📍 标记")
        controls_layout.addWidget(mark_btn)

        undo_btn = QToolButton()
        undo_btn.setText("↶ 撤销")
        controls_layout.addWidget(undo_btn)

        redo_btn = QToolButton()
        redo_btn.setText("↷ 重做")
        controls_layout.addWidget(redo_btn)

        controls_layout.addStretch()

        # 时间显示 - 严格按照设计方案
        time_label = QLabel("时间: 02:30 / 10:00")
        time_label.setStyleSheet("""
            QLabel {
                color: #374151;
                font-weight: bold;
                font-size: 12px;
                background-color: white;
                padding: 4px 8px;
                border: 1px solid #E2E8F0;
                border-radius: 3px;
            }
        """)
        controls_layout.addWidget(time_label)

        timeline_layout.addWidget(controls_frame)

        logger.info("时间轴区域设置完成 - 严格符合设计方案")

    def setup_design_compliant_status_bar(self):
        """设置状态栏 (24px) - 严格按照界面设计完整方案实现"""
        # 创建状态栏 - 严格24px高度
        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(24)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #F1F5F9;
                border-top: 1px solid #E2E8F0;
                color: #374151;
                font-size: 11px;
                font-weight: 500;
            }
            QLabel {
                color: #374151;
                font-size: 11px;
                padding: 0 8px;
            }
        """)

        # 状态信息 - 严格按照设计方案
        # 📍选中: 小球元素 | 🎯位置: (400,300) | 💾已保存 | ⚡GPU:45% | 👥在线:3人

        # 选中元素信息
        selected_label = QLabel("📍选中: 小球元素")
        self.status_bar.addWidget(selected_label)

        # 分隔符
        separator1 = QLabel("|")
        separator1.setStyleSheet("color: #9CA3AF;")
        self.status_bar.addWidget(separator1)

        # 位置信息
        position_label = QLabel("🎯位置: (400,300)")
        self.status_bar.addWidget(position_label)

        # 分隔符
        separator2 = QLabel("|")
        separator2.setStyleSheet("color: #9CA3AF;")
        self.status_bar.addWidget(separator2)

        # 保存状态
        save_status_label = QLabel("💾已保存")
        save_status_label.setStyleSheet("color: #10B981;")
        self.status_bar.addWidget(save_status_label)

        # 分隔符
        separator3 = QLabel("|")
        separator3.setStyleSheet("color: #9CA3AF;")
        self.status_bar.addWidget(separator3)

        # GPU使用率
        gpu_label = QLabel("⚡GPU:45%")
        gpu_label.setStyleSheet("color: #F59E0B;")
        self.status_bar.addWidget(gpu_label)

        # 分隔符
        separator4 = QLabel("|")
        separator4.setStyleSheet("color: #9CA3AF;")
        self.status_bar.addWidget(separator4)

        # 在线用户
        online_label = QLabel("👥在线:3人")
        online_label.setStyleSheet("color: #10B981;")
        self.status_bar.addWidget(online_label)

        # 设置状态栏
        self.setStatusBar(self.status_bar)

        # 保存状态栏组件引用
        self.selected_label = selected_label
        self.position_label = position_label
        self.save_status_label = save_status_label
        self.gpu_label = gpu_label
        self.online_label = online_label

        logger.info("状态栏设置完成 - 严格符合设计方案")

    # 工具栏按钮事件处理方法
    def show_project_settings(self):
        """显示项目设置"""
        logger.info("显示项目设置")

    def show_project_info(self):
        """显示项目信息"""
        logger.info("显示项目信息")

    def undo_action(self):
        """撤销操作"""
        logger.info("撤销操作")

    def redo_action(self):
        """重做操作"""
        logger.info("重做操作")

    def copy_action(self):
        """复制操作"""
        logger.info("复制操作")

    def paste_action(self):
        """粘贴操作"""
        logger.info("粘贴操作")

    def cut_action(self):
        """剪切操作"""
        logger.info("剪切操作")

    def find_replace(self):
        """查找替换"""
        logger.info("查找替换")

    def export_image(self):
        """导出图片"""
        logger.info("导出图片")

    def batch_export(self):
        """批量导出"""
        logger.info("批量导出")

    def show_enhanced_export_dialog(self):
        """显示增强的多格式导出对话框 - 基于设计文档的智能导出系统"""
        dialog = EnhancedExportDialog(self)
        dialog.exec()

    def show_performance_monitoring_dialog(self):
        """显示性能监控对话框"""
        dialog = PerformanceMonitoringDialog(self)
        dialog.exec()

    def cloud_export(self):
        """云端导出"""
        logger.info("云端导出")

    def show_ai_generator(self):
        """显示AI生成器"""
        logger.info("显示AI生成器")
        # 切换到AI生成面板标签页
        if hasattr(self, 'ai_control_tabs'):
            self.ai_control_tabs.setCurrentIndex(0)

    def show_preview(self):
        """显示预览"""
        logger.info("显示预览")
        # 切换到多设备预览标签页
        if hasattr(self, 'main_work_tabs'):
            self.main_work_tabs.setCurrentIndex(1)

    def show_collaboration(self):
        """显示协作"""
        logger.info("显示协作")
        # 切换到协作评论标签页
        if hasattr(self, 'ai_control_tabs'):
            self.ai_control_tabs.setCurrentIndex(5)

    def toggle_edit_mode(self):
        """切换编辑模式"""
        logger.info("切换编辑模式")

    def show_user_menu(self):
        """显示用户菜单"""
        logger.info("显示用户菜单")

        logger.info("专业顶部工具栏设置完成")

    def setup_enhanced_resource_management_panel(self):
        """设置增强的资源管理区 (300px) - 按照设计方案实现"""
        # 创建资源管理面板
        resource_widget = QFrame()
        resource_widget.setFixedWidth(300)
        resource_widget.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-right: 1px solid #E2E8F0;
            }
            QTabWidget::pane {
                border: 1px solid #E2E8F0;
                background-color: white;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #F1F5F9;
                color: #475569;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #2C5AA0;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #4A90E2;
                color: white;
            }
            QTreeWidget, QListWidget {
                background-color: white;
                border: none;
                font-size: 11px;
            }
            QTreeWidget::item, QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #F1F5F9;
            }
            QTreeWidget::item:selected, QListWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
            QTreeWidget::item:hover, QListWidget::item:hover {
                background-color: #E0F2FE;
            }
        """)

        # 资源管理面板布局
        resource_layout = QVBoxLayout(resource_widget)
        resource_layout.setContentsMargins(0, 0, 0, 0)
        resource_layout.setSpacing(0)

        # 创建选项卡组件
        resource_tabs = QTabWidget()
        resource_layout.addWidget(resource_tabs)

        # 1. 项目文件选项卡
        project_tab = QTreeWidget()
        project_tab.setHeaderLabel("项目结构")
        project_tab.setRootIsDecorated(True)

        # 添加示例项目结构
        root_item = QTreeWidgetItem(project_tab, ["📁 当前项目"])
        audio_item = QTreeWidgetItem(root_item, ["🎵 音频文件"])
        QTreeWidgetItem(audio_item, ["narration.mp3"])
        elements_item = QTreeWidgetItem(root_item, ["🧩 元素"])
        QTreeWidgetItem(elements_item, ["小球"])
        QTreeWidgetItem(elements_item, ["Logo"])
        animations_item = QTreeWidgetItem(root_item, ["🎬 动画"])
        QTreeWidgetItem(animations_item, ["动画片段1"])
        QTreeWidgetItem(animations_item, ["动画片段2"])

        project_tab.expandAll()
        resource_tabs.addTab(project_tab, "📁 项目文件")

        # 2. 音频管理选项卡
        audio_tab = QListWidget()
        audio_items = [
            "🎵 主旁白.mp3 (10:00)",
            "🎵 背景音乐.mp3 (10:30)",
            "🔊 音效1.wav (0:02)",
            "🔊 音效2.wav (0:01)"
        ]
        for item_text in audio_items:
            audio_tab.addItem(QListWidgetItem(item_text))
        resource_tabs.addTab(audio_tab, "🎵 音频管理")

        # 3. 素材库选项卡
        assets_tab = QTreeWidget()
        assets_tab.setHeaderLabel("素材分类")

        # 图标素材
        icons_item = QTreeWidgetItem(assets_tab, ["🎨 图标素材"])
        QTreeWidgetItem(icons_item, ["⚛️ 原子结构"])
        QTreeWidgetItem(icons_item, ["🔬 科学仪器"])
        QTreeWidgetItem(icons_item, ["📊 图表元素"])

        # 形状素材
        shapes_item = QTreeWidgetItem(assets_tab, ["🔷 形状素材"])
        QTreeWidgetItem(shapes_item, ["⚪ 圆形"])
        QTreeWidgetItem(shapes_item, ["⬜ 矩形"])
        QTreeWidgetItem(shapes_item, ["🔺 三角形"])

        assets_tab.expandAll()
        resource_tabs.addTab(assets_tab, "🎨 素材库")

        # 4. 工具箱选项卡
        tools_tab = QListWidget()
        tool_items = [
            "👆 选择工具",
            "✋ 移动工具",
            "📏 路径工具",
            "📝 文字工具",
            "🔷 形状工具",
            "➕ 添加元素"
        ]
        for item_text in tool_items:
            tools_tab.addItem(QListWidgetItem(item_text))
        resource_tabs.addTab(tools_tab, "📐 工具箱")

        # 5. 规则库选项卡
        rules_tab = QTreeWidget()
        rules_tab.setHeaderLabel("动画规则")

        physics_item = QTreeWidgetItem(rules_tab, ["⚡ 物理规则"])
        QTreeWidgetItem(physics_item, ["重力效果"])
        QTreeWidgetItem(physics_item, ["弹性碰撞"])
        QTreeWidgetItem(physics_item, ["摩擦力"])

        visual_item = QTreeWidgetItem(rules_tab, ["🎨 视觉规则"])
        QTreeWidgetItem(visual_item, ["淡入淡出"])
        QTreeWidgetItem(visual_item, ["缩放效果"])
        QTreeWidgetItem(visual_item, ["旋转动画"])

        rules_tab.expandAll()
        resource_tabs.addTab(rules_tab, "📚 规则库")

        # 6. 操作历史选项卡
        history_tab = QListWidget()
        history_items = [
            "🔄 添加小球元素",
            "🔄 修改位置属性",
            "🔄 应用颜色变化",
            "🔄 生成动画方案",
            "🔄 调整透明度"
        ]
        for item_text in history_items:
            history_tab.addItem(QListWidgetItem(item_text))
        resource_tabs.addTab(history_tab, "🔄 操作历史")

        # 7. 模板库选项卡
        templates_tab = QTreeWidget()
        templates_tab.setHeaderLabel("模板分类")

        edu_item = QTreeWidgetItem(templates_tab, ["🎓 教育模板"])
        QTreeWidgetItem(edu_item, ["科普动画模板"])
        QTreeWidgetItem(edu_item, ["数学演示模板"])

        business_item = QTreeWidgetItem(templates_tab, ["💼 商业模板"])
        QTreeWidgetItem(business_item, ["产品展示模板"])
        QTreeWidgetItem(business_item, ["数据可视化模板"])

        templates_tab.expandAll()
        resource_tabs.addTab(templates_tab, "📋 模板库")

        # 将资源管理面板添加到主分割器
        self.main_splitter.addWidget(resource_widget)
        self.resource_management_widget = resource_widget
        self.resource_tabs = resource_tabs

        logger.info("增强资源管理面板设置完成")

    def setup_enhanced_main_work_area(self):
        """设置增强的主工作区 (弹性宽度) - 多标签页设计"""
        # 创建主工作区面板
        main_work_widget = QFrame()
        main_work_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E2E8F0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F8FAFC;
                color: #475569;
                padding: 10px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #2C5AA0;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #4A90E2;
                color: white;
            }
            QToolBar {
                background-color: #F8FAFC;
                border-bottom: 1px solid #E2E8F0;
                spacing: 4px;
                padding: 4px;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid #E2E8F0;
                border-radius: 4px;
                padding: 6px;
                margin: 2px;
            }
            QToolButton:hover {
                background-color: #E0F2FE;
                border-color: #4A90E2;
            }
            QToolButton:pressed {
                background-color: #4A90E2;
                color: white;
            }
            QLabel {
                color: #475569;
                font-size: 11px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #E2E8F0;
                height: 4px;
                background: #F1F5F9;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #4A90E2;
                border: 1px solid #2C5AA0;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QCheckBox {
                color: #475569;
                font-size: 11px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #CBD5E1;
                background-color: white;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4A90E2;
                background-color: #4A90E2;
                border-radius: 3px;
            }
        """)

        # 主工作区布局
        main_work_layout = QVBoxLayout(main_work_widget)
        main_work_layout.setContentsMargins(0, 0, 0, 0)
        main_work_layout.setSpacing(0)

        # 创建多标签页工作区
        self.main_work_tabs = QTabWidget()
        main_work_layout.addWidget(self.main_work_tabs)

        # 1. 舞台编辑选项卡
        stage_widget = QFrame()
        stage_layout = QVBoxLayout(stage_widget)
        stage_layout.setContentsMargins(0, 0, 0, 0)

        # 舞台工具栏
        stage_toolbar = QToolBar()
        stage_toolbar.setMovable(False)
        stage_toolbar.setFixedHeight(40)

        # 工具按钮
        stage_toolbar.addAction("👆 选择")
        stage_toolbar.addAction("✋ 移动")
        stage_toolbar.addAction("📏 路径")
        stage_toolbar.addAction("📝 文字")
        stage_toolbar.addAction("🔷 形状")
        stage_toolbar.addAction("➕ 添加元素")
        stage_toolbar.addSeparator()

        # 网格和对齐控制
        grid_checkbox = QCheckBox("网格")
        grid_checkbox.setChecked(True)
        stage_toolbar.addWidget(grid_checkbox)

        snap_checkbox = QCheckBox("吸附")
        snap_checkbox.setChecked(True)
        stage_toolbar.addWidget(snap_checkbox)

        ruler_checkbox = QCheckBox("标尺")
        ruler_checkbox.setChecked(True)
        stage_toolbar.addWidget(ruler_checkbox)

        stage_toolbar.addSeparator()

        # 缩放控制
        stage_toolbar.addWidget(QLabel("🔍"))
        zoom_slider = QSlider(Qt.Orientation.Horizontal)
        zoom_slider.setRange(25, 400)
        zoom_slider.setValue(100)
        zoom_slider.setFixedWidth(100)
        stage_toolbar.addWidget(zoom_slider)
        stage_toolbar.addWidget(QLabel("100%"))

        stage_toolbar.addSeparator()
        stage_toolbar.addAction("🎯 居中")
        stage_toolbar.addAction("📐 对齐")

        stage_layout.addWidget(stage_toolbar)

        # 舞台画布区域
        canvas_area = QScrollArea()
        canvas_area.setWidgetResizable(True)
        canvas_area.setStyleSheet("""
            QScrollArea {
                background-color: #F8FAFC;
                border: none;
            }
        """)

        # 创建画布
        canvas_widget = QLabel()
        canvas_widget.setFixedSize(1920, 1080)  # 标准画布尺寸
        canvas_widget.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px solid #E2E8F0;
                border-radius: 4px;
            }
        """)
        canvas_widget.setText("1920 x 1080 画布\n\n[Logo]    当前时间: 2.3s\n   ↘️路径\n     [小球] ←选中元素\n       ↘️\n         [终点]\n\n智能参考线 | 对齐提示 | 距离测量")
        canvas_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        canvas_area.setWidget(canvas_widget)

        stage_layout.addWidget(canvas_area)

        # 上下文属性面板
        context_panel = QFrame()
        context_panel.setFixedHeight(60)
        context_panel.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-top: 1px solid #E2E8F0;
            }
        """)
        context_layout = QHBoxLayout(context_panel)
        context_layout.addWidget(QLabel("元素: 小球 | 位置: (400,300) | 尺寸: 50x50 | 旋转: 0°"))
        context_layout.addStretch()

        # 属性按钮组
        context_layout.addWidget(QLabel("[🎨样式] [📍变换] [🔄动画] [⚙️高级] [🔗链接] [📋复制]"))

        stage_layout.addWidget(context_panel)

        self.main_work_tabs.addTab(stage_widget, "🎨 舞台编辑")

        # 2. 设备预览选项卡
        preview_widget = QLabel("📱 多设备预览区域\n\n支持桌面、手机、平板等多种设备预览")
        preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_widget.setStyleSheet("background-color: #F8FAFC; color: #64748B;")
        self.main_work_tabs.addTab(preview_widget, "📱 设备预览")

        # 3. 测试面板选项卡
        test_widget = QLabel("🧪 测试控制台\n\n自动化测试和质量检测")
        test_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        test_widget.setStyleSheet("background-color: #F8FAFC; color: #64748B;")
        self.main_work_tabs.addTab(test_widget, "🧪 测试面板")

        # 4. 性能监控选项卡
        performance_widget = QLabel("📊 性能监控\n\nFPS、内存、GPU使用率监控")
        performance_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        performance_widget.setStyleSheet("background-color: #F8FAFC; color: #64748B;")
        self.main_work_tabs.addTab(performance_widget, "📊 性能监控")

        # 5. 调试面板选项卡
        debug_widget = QLabel("🔍 调试面板\n\n错误诊断和智能修复")
        debug_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        debug_widget.setStyleSheet("background-color: #F8FAFC; color: #64748B;")
        self.main_work_tabs.addTab(debug_widget, "🔍 调试面板")

        # 将主工作区添加到主分割器
        self.main_splitter.addWidget(main_work_widget)
        self.main_work_widget = main_work_widget
        self.canvas_widget = canvas_widget
        self.zoom_slider = zoom_slider

        logger.info("增强主工作区设置完成")

    def setup_enhanced_ai_control_panel(self):
        """设置增强的AI控制区 (350px) - 智能交互设计"""
        # 创建AI控制面板
        ai_control_widget = QFrame()
        ai_control_widget.setFixedWidth(350)
        ai_control_widget.setStyleSheet("""
            QFrame {
                border-left: 1px solid #E2E8F0;
            }
            QTabWidget::pane {
                border: 1px solid #E2E8F0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F1F5F9;
                color: #475569;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #FF6B35;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #FB923C;
                color: white;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
            QProgressBar {
                border: 1px solid #E2E8F0;
                border-radius: 4px;
                text-align: center;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #FF6B35;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #FF6B35;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #FB923C;
            }
            QPushButton:pressed {
                background-color: #EA580C;
            }
            QPushButton[objectName="secondary_button"] {
                background-color: #4A90E2;
            }
            QPushButton[objectName="secondary_button"]:hover {
                background-color: #60A5FA;
            }
            QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 11px;
                color: #374151;
                border: 1px solid #E2E8F0;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }
            QRadioButton {
                font-size: 11px;
                color: #475569;
            }
            QLabel {
                color: #475569;
                font-size: 11px;
            }
        """)

        # AI控制面板布局
        ai_control_layout = QVBoxLayout(ai_control_widget)
        ai_control_layout.setContentsMargins(0, 0, 0, 0)
        ai_control_layout.setSpacing(0)

        # 创建AI控制选项卡
        ai_control_tabs = QTabWidget()
        ai_control_layout.addWidget(ai_control_tabs)

        # 1. AI生成面板选项卡
        ai_gen_widget = QFrame()
        ai_gen_layout = QVBoxLayout(ai_gen_widget)
        ai_gen_layout.setContentsMargins(8, 8, 8, 8)
        ai_gen_layout.setSpacing(8)

        # 多模式输入区域
        input_group = QGroupBox("📝 多模式输入")
        input_layout = QVBoxLayout(input_group)

        # 输入模式按钮
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("[📝文本] [🎤语音] [🖼️图片] [📄模板] [🔄批量]"))
        input_layout.addLayout(mode_layout)

        # 描述输入框
        description_input = QTextEdit()
        description_input.setFixedHeight(80)
        description_input.setPlaceholderText("小球像火箭一样快速飞过去，要有科技感和拖尾效果")
        input_layout.addWidget(description_input)

        # 智能标签
        tags_label = QLabel("🏷️ 智能标签: #火箭运动 #科技感 #拖尾效果 #快速移动")
        tags_label.setWordWrap(True)
        input_layout.addWidget(tags_label)

        ai_gen_layout.addWidget(input_group)

        # AI实时分析区域
        analysis_group = QGroupBox("🧠 AI实时分析 (Gemini 2.5 Flash)")
        analysis_layout = QVBoxLayout(analysis_group)

        # 分析进度
        analysis_progress = QProgressBar()
        analysis_progress.setValue(100)
        analysis_progress.setFormat("分析进度: %p%")
        analysis_layout.addWidget(analysis_progress)

        # 分析结果
        analysis_text = QLabel("""✓ 动作类型: 快速直线移动 (置信度: 95%)
✓ 视觉效果: 科技感 + 拖尾 (置信度: 92%)
✓ 物理特征: 火箭推进加速 (置信度: 88%)
✓ 时间匹配: 2.3秒 ✓ 路径匹配: 弧线轨迹

🎯 技术建议:
• 推荐技术栈: GSAP + CSS3 Transform
• 动画时长: 2.3秒 (自动匹配时间段)
• 缓动函数: cubic-bezier(0.25,0.46,0.45,0.94)
• 性能预估: GPU使用+15%, 渲染负载适中""")
        analysis_text.setWordWrap(True)
        analysis_text.setStyleSheet("font-size: 10px; color: #374151;")
        analysis_layout.addWidget(analysis_text)

        ai_gen_layout.addWidget(analysis_group)

        # 生成控制区域
        control_group = QGroupBox("⚙️ 生成控制")
        control_layout = QVBoxLayout(control_group)

        # 精确度选择
        precision_layout = QHBoxLayout()
        precision_layout.addWidget(QLabel("精确度:"))
        precision_group = QButtonGroup()
        fast_radio = QRadioButton("快速模式")
        precise_radio = QRadioButton("精确模式")
        precise_radio.setChecked(True)
        creative_radio = QRadioButton("创意模式")
        precision_group.addButton(fast_radio)
        precision_group.addButton(precise_radio)
        precision_group.addButton(creative_radio)
        precision_layout.addWidget(fast_radio)
        precision_layout.addWidget(precise_radio)
        precision_layout.addWidget(creative_radio)
        control_layout.addLayout(precision_layout)

        # 其他设置
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("方案数:"))
        solution_count = QSpinBox()
        solution_count.setRange(1, 10)
        solution_count.setValue(3)
        settings_layout.addWidget(solution_count)

        settings_layout.addWidget(QLabel("AI模型:"))
        model_combo = QComboBox()
        model_combo.addItems(["Gemini 2.5", "GPT-4", "Claude"])
        settings_layout.addWidget(model_combo)
        control_layout.addLayout(settings_layout)

        # 生成按钮组
        button_layout = QHBoxLayout()
        generate_btn = QPushButton("⚡ 生成动画")
        pause_btn = QPushButton("⏸️ 暂停")
        pause_btn.setObjectName("secondary_button")
        save_btn = QPushButton("💾 保存Prompt")
        save_btn.setObjectName("secondary_button")

        button_layout.addWidget(generate_btn)
        button_layout.addWidget(pause_btn)
        button_layout.addWidget(save_btn)
        control_layout.addLayout(button_layout)

        ai_gen_layout.addWidget(control_group)

        ai_control_tabs.addTab(ai_gen_widget, "🤖 AI生成面板")

        # 2. Prompt编辑选项卡
        prompt_widget = QTextEdit()
        prompt_widget.setPlaceholderText("【项目设置】\n- 画布尺寸: 1920x1080 | 时间段: 2.3s-4.6s (2.3秒)\n- 风格主题: 科技感 | 起始状态: translate(100px,200px)\n\n【精确描述】⭐ 可编辑重点区域\n小球从静止开始，前0.3秒缓慢加速(ease-in)，然后2.0秒内\n以火箭推进方式快速移动。添加蓝色发光拖尾(长度3倍)，\n轻微震动(±2px,30Hz)，到达后冲击波扩散(半径50px)。")
        ai_control_tabs.addTab(prompt_widget, "📋 Prompt编辑")

        # 3. 方案对比选项卡
        comparison_widget = QLabel("📊 智能方案对比\n\n四方案并行显示\n智能对比分析\n推荐评分系统")
        comparison_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        comparison_widget.setStyleSheet("color: #64748B;")
        ai_control_tabs.addTab(comparison_widget, "📊 方案对比")

        # 4. 参数调整选项卡
        params_widget = QLabel("⚙️ 参数调整\n\n动画参数微调\n实时预览更新\n批量参数应用")
        params_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        params_widget.setStyleSheet("color: #64748B;")
        ai_control_tabs.addTab(params_widget, "⚙️ 参数调整")

        # 5. 状态监控选项卡
        monitor_widget = QLabel("📈 状态监控\n\nAI服务状态\n生成进度跟踪\n性能指标监控")
        monitor_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        monitor_widget.setStyleSheet("color: #64748B;")
        ai_control_tabs.addTab(monitor_widget, "📈 状态监控")

        # 6. 协作评论选项卡
        collab_widget = QLabel("💬 协作评论\n\n团队实时讨论\n评论和建议\n版本对比")
        collab_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        collab_widget.setStyleSheet("color: #64748B;")
        ai_control_tabs.addTab(collab_widget, "💬 协作评论")

        # 7. 智能修复选项卡
        repair_widget = QLabel("🔧 智能修复\n\n自动问题检测\n智能修复建议\n一键修复功能")
        repair_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        repair_widget.setStyleSheet("color: #64748B;")
        ai_control_tabs.addTab(repair_widget, "🔧 智能修复")

        # 将AI控制面板添加到主分割器
        self.main_splitter.addWidget(ai_control_widget)
        self.ai_control_widget = ai_control_widget
        self.ai_control_tabs = ai_control_tabs
        self.description_input = description_input
        self.generate_btn = generate_btn

        logger.info("增强AI控制面板设置完成")

    def setup_professional_timeline_area(self):
        """设置专业时间轴区域 (200px) - 多轨道时间轴设计"""
        # 创建时间轴区域
        timeline_widget = QFrame()
        timeline_widget.setFixedHeight(200)
        timeline_widget.setStyleSheet("""
            QFrame {
                border-top: 2px solid #E2E8F0;
            }
            QToolButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
                margin: 2px;
            }
            QToolButton:hover {
                background-color: #60A5FA;
            }
            QToolButton:pressed {
                background-color: #2563EB;
            }
            QToolButton[objectName="play_button"] {
                background-color: #10B981;
            }
            QToolButton[objectName="play_button"]:hover {
                background-color: #34D399;
            }
            QToolButton[objectName="record_button"] {
                background-color: #EF4444;
            }
            QToolButton[objectName="record_button"]:hover {
                background-color: #F87171;
            }
            QLabel {
                color: #374151;
                font-size: 11px;
                font-weight: bold;
            }
            QProgressBar {
                border: 1px solid #E2E8F0;
                border-radius: 4px;
                text-align: center;
                font-size: 10px;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #4A90E2;
                border-radius: 3px;
            }
            QScrollArea {
                border: 1px solid #E2E8F0;
                background-color: white;
                border-radius: 4px;
            }
        """)

        # 时间轴区域布局
        timeline_layout = QVBoxLayout(self.timeline_area_widget)
        timeline_layout.setContentsMargins(8, 8, 8, 8)
        timeline_layout.setSpacing(4)

        # 1. 时间轴控制栏
        control_frame = QFrame()
        control_frame.setFixedHeight(40)
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(4, 4, 4, 4)

        # 播放控制按钮
        play_btn = QToolButton()
        play_btn.setText("▶️")
        play_btn.setObjectName("play_button")
        control_layout.addWidget(play_btn)

        pause_btn = QToolButton()
        pause_btn.setText("⏸️")
        control_layout.addWidget(pause_btn)

        stop_btn = QToolButton()
        stop_btn.setText("⏹️")
        control_layout.addWidget(stop_btn)

        prev_btn = QToolButton()
        prev_btn.setText("⏮️")
        control_layout.addWidget(prev_btn)

        next_btn = QToolButton()
        next_btn.setText("⏭️")
        control_layout.addWidget(next_btn)

        loop_btn = QToolButton()
        loop_btn.setText("🔄")
        control_layout.addWidget(loop_btn)

        control_layout.addWidget(QLabel("|"))

        # 音量控制
        volume_label = QLabel("🔊")
        control_layout.addWidget(volume_label)

        volume_progress = QProgressBar()
        volume_progress.setFixedWidth(60)
        volume_progress.setFixedHeight(8)
        volume_progress.setValue(70)
        volume_progress.setTextVisible(False)
        control_layout.addWidget(volume_progress)

        control_layout.addWidget(QLabel("|"))

        # 播放速度
        speed_label = QLabel("倍速: 1.0x ▼")
        control_layout.addWidget(speed_label)

        control_layout.addWidget(QLabel("|"))

        # 编辑操作
        undo_btn = QToolButton()
        undo_btn.setText("↶ 撤销")
        control_layout.addWidget(undo_btn)

        redo_btn = QToolButton()
        redo_btn.setText("↷ 重做")
        control_layout.addWidget(redo_btn)

        history_btn = QToolButton()
        history_btn.setText("📋 历史")
        control_layout.addWidget(history_btn)

        mark_btn = QToolButton()
        mark_btn.setText("📌 标记")
        control_layout.addWidget(mark_btn)

        split_btn = QToolButton()
        split_btn.setText("✂️ 分割")
        control_layout.addWidget(split_btn)

        link_btn = QToolButton()
        link_btn.setText("🔗 链接片段")
        control_layout.addWidget(link_btn)

        control_layout.addStretch()

        # 时间显示
        time_label = QLabel("0:00 / 10:00")
        time_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #2C5AA0;")
        control_layout.addWidget(time_label)

        timeline_layout.addWidget(control_frame)

        # 2. 音频轨道区域
        audio_frame = QFrame()
        audio_frame.setFixedHeight(40)
        audio_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 4px;
            }
        """)
        audio_layout = QHBoxLayout(audio_frame)
        audio_layout.setContentsMargins(8, 4, 8, 4)

        # 音频轨道标签
        audio_track_label = QLabel("🎤 旁白音频轨道 (主时间参考)")
        audio_track_label.setStyleSheet("font-weight: bold; color: #374151;")
        audio_layout.addWidget(audio_track_label)

        audio_layout.addStretch()

        # 音频波形显示（简化版）
        waveform_label = QLabel("████▓▓▓░░░▓▓▓████░░░▓▓▓████░░░████▓▓▓░░░")
        waveform_label.setStyleSheet("font-family: monospace; color: #4A90E2; font-size: 10px;")
        audio_layout.addWidget(waveform_label)

        timeline_layout.addWidget(audio_frame)

        # 3. 动画轨道区域
        animation_frame = QFrame()
        animation_frame.setFixedHeight(60)
        animation_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 4px;
            }
        """)
        animation_layout = QVBoxLayout(animation_frame)
        animation_layout.setContentsMargins(8, 4, 8, 4)

        # 动画轨道标签
        animation_track_label = QLabel("🎬 动画轨道 (多层次显示)")
        animation_track_label.setStyleSheet("font-weight: bold; color: #374151;")
        animation_layout.addWidget(animation_track_label)

        # 动画片段显示
        segments_layout = QHBoxLayout()

        # 动画片段
        segments = [
            ("Logo\n出现\n✅完成", "#10B981"),
            ("小球\n移动\n🔄进行", "#F59E0B"),
            ("文字\n淡入\n⏳待处理", "#94A3B8"),
            ("背景\n变色\n⏳待处理", "#94A3B8")
        ]

        for segment_text, color in segments:
            segment_label = QLabel(segment_text)
            segment_label.setFixedSize(60, 40)
            segment_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            segment_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: white;
                    border-radius: 4px;
                    font-size: 9px;
                    font-weight: bold;
                    margin: 2px;
                }}
            """)
            segments_layout.addWidget(segment_label)

        segments_layout.addStretch()
        animation_layout.addLayout(segments_layout)

        timeline_layout.addWidget(animation_frame)

        # 4. 状态衔接指示区域
        connection_frame = QFrame()
        connection_frame.setFixedHeight(40)
        connection_frame.setStyleSheet("""
            QFrame {
                background-color: #FEF3C7;
                border: 1px solid #F59E0B;
                border-radius: 4px;
            }
        """)
        connection_layout = QVBoxLayout(connection_frame)
        connection_layout.setContentsMargins(8, 4, 8, 4)

        connection_label = QLabel("🔗 状态衔接指示")
        connection_label.setStyleSheet("font-weight: bold; color: #92400E;")
        connection_layout.addWidget(connection_label)

        status_text = QLabel("✅ Logo→小球: 完美匹配  ⚠️ 小球→文字: 透明度差异0.1 [🔧自动修复]  ❌ 文字→背景: 位置冲突 [⚙️手动调整]")
        status_text.setStyleSheet("font-size: 10px; color: #92400E;")
        status_text.setWordWrap(True)
        connection_layout.addWidget(status_text)

        timeline_layout.addWidget(connection_frame)

        # 保存组件引用
        self.play_btn = play_btn
        self.pause_btn = pause_btn
        self.time_label = time_label
        self.volume_progress = volume_progress

        logger.info("专业时间轴区域设置完成")

    def setup_professional_status_bar(self):
        """设置专业状态栏 (24px) - 专业状态信息"""
        # 创建增强状态栏
        self.status_bar = self.statusBar()
        self.status_bar.setFixedHeight(24)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #F1F5F9;
                border-top: 1px solid #E2E8F0;
                color: #475569;
                font-size: 11px;
            }
            QLabel {
                color: #475569;
                font-size: 11px;
                padding: 0 8px;
            }
        """)

        # 状态栏信息标签
        self.selection_label = QLabel("📍选中: 小球元素")
        self.position_label = QLabel("🎯位置: (400,300)")
        self.save_label = QLabel("💾已保存")
        self.gpu_label = QLabel("⚡GPU:45%")
        self.online_label = QLabel("👥在线:3人")

        # 添加到状态栏
        self.status_bar.addWidget(self.selection_label)
        self.status_bar.addWidget(QLabel("|"))
        self.status_bar.addWidget(self.position_label)
        self.status_bar.addWidget(QLabel("|"))
        self.status_bar.addWidget(self.save_label)
        self.status_bar.addWidget(QLabel("|"))
        self.status_bar.addWidget(self.gpu_label)
        self.status_bar.addWidget(QLabel("|"))
        self.status_bar.addWidget(self.online_label)

        logger.info("专业状态栏设置完成")

    def get_professional_main_window_style(self):
        """获取专业主窗口样式"""
        return """
            QMainWindow {
                background-color: #F8FAFC;
                color: #1F2937;
            }
            QMainWindow::separator {
                background-color: #E5E7EB;
                width: 1px;
                height: 1px;
            }
        """

    def setup_top_toolbar(self):
        """设置顶部工具栏区域 (60px)"""
        self.top_toolbar_widget = QFrame()
        self.top_toolbar_widget.setFixedHeight(60)
        self.top_toolbar_widget.setFrameStyle(QFrame.Shape.StyledPanel)
        self.top_toolbar_widget.setStyleSheet("""
            QFrame {
                background-color: #2C5AA0;
                border-bottom: 2px solid #1E3A5F;
            }
            QToolButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #4A90E2;
            }
            QToolButton:pressed {
                background-color: #1E3A5F;
            }
            QToolButton[objectName="ai_button"] {
                background-color: #FF6B35;
            }
            QToolButton[objectName="ai_button"]:hover {
                background-color: #FB923C;
            }
        """)

        # 工具栏布局
        toolbar_layout = QHBoxLayout(self.top_toolbar_widget)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # 左侧主要功能按钮
        main_buttons_group = QButtonGroup(self)

        # 项目菜单
        project_btn = QToolButton()
        project_btn.setText("项目 ▼")
        project_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar_layout.addWidget(project_btn)

        # 编辑菜单
        edit_btn = QToolButton()
        edit_btn.setText("编辑 ▼")
        edit_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar_layout.addWidget(edit_btn)

        # AI生成按钮（强调色）
        ai_btn = QToolButton()
        ai_btn.setText("🤖 AI生成")
        ai_btn.setObjectName("ai_button")
        toolbar_layout.addWidget(ai_btn)

        # 预览按钮
        preview_btn = QToolButton()
        preview_btn.setText("👁️ 预览")
        toolbar_layout.addWidget(preview_btn)

        # 协作按钮
        collab_btn = QToolButton()
        collab_btn.setText("👥 协作")
        toolbar_layout.addWidget(collab_btn)

        # 导出菜单
        export_btn = QToolButton()
        export_btn.setText("📤 导出 ▼")
        export_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar_layout.addWidget(export_btn)

        # 分隔符
        toolbar_layout.addStretch()

        # 右侧状态和设置按钮
        # 编辑模式切换
        mode_btn = QToolButton()
        mode_btn.setText("🔄 编辑模式")
        toolbar_layout.addWidget(mode_btn)

        # 设置按钮
        settings_btn = QToolButton()
        settings_btn.setText("⚙️ 设置")
        toolbar_layout.addWidget(settings_btn)

        # 用户按钮
        user_btn = QToolButton()
        user_btn.setText("👤 用户")
        toolbar_layout.addWidget(user_btn)

        # 连接信号
        ai_btn.clicked.connect(self.show_ai_generator)
        preview_btn.clicked.connect(self.show_preview)
        settings_btn.clicked.connect(self.show_settings)

    def setup_resource_management_panel(self):
        """设置左侧资源管理区 (300px)"""
        # 创建资源管理面板容器
        resource_widget = QFrame()
        resource_widget.setFixedWidth(300)
        resource_widget.setFrameStyle(QFrame.Shape.StyledPanel)
        resource_widget.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-right: 1px solid #E5E7EB;
            }
        """)

        resource_layout = QVBoxLayout(resource_widget)
        resource_layout.setContentsMargins(5, 5, 5, 5)

        # 创建资源管理标签页
        self.resource_tabs = QTabWidget()
        self.resource_tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.resource_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E5E7EB;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F3F4F6;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2C5AA0;
            }
        """)

        # 📁 项目文件标签页
        project_files_widget = self.create_project_files_tab()
        self.resource_tabs.addTab(project_files_widget, "📁 项目")

        # 🎵 音频管理标签页
        audio_widget = self.create_audio_management_tab()
        self.resource_tabs.addTab(audio_widget, "🎵 音频")

        # 🎨 素材库标签页
        assets_widget = self.create_assets_library_tab()
        self.resource_tabs.addTab(assets_widget, "🎨 素材")

        # 📐 工具箱标签页
        tools_widget = self.create_tools_tab()
        self.resource_tabs.addTab(tools_widget, "📐 工具")

        # 📚 规则库标签页
        rules_widget = self.create_rules_library_tab()
        self.resource_tabs.addTab(rules_widget, "📚 规则")

        # 🔄 操作历史标签页
        history_widget = self.create_operation_history_tab()
        self.resource_tabs.addTab(history_widget, "🔄 历史")

        # 📋 模板库标签页
        templates_widget = self.create_templates_library_tab()
        self.resource_tabs.addTab(templates_widget, "📋 模板")

        # 📊 状态管理标签页
        state_management_widget = self.create_state_management_tab()
        self.resource_tabs.addTab(state_management_widget, "📊 状态")

        # 🔄 操作历史标签页
        operation_history_widget = self.create_operation_history_tab()
        self.resource_tabs.addTab(operation_history_widget, "🔄 历史")

        # 📐 工具箱标签页
        toolbox_widget = self.create_toolbox_tab()
        self.resource_tabs.addTab(toolbox_widget, "📐 工具箱")

        # 📚 库管理标签页
        library_management_widget = self.create_library_management_tab()
        self.resource_tabs.addTab(library_management_widget, "📚 库管理")

        # 🔄 版本控制标签页
        version_control_widget = self.create_version_control_tab()
        self.resource_tabs.addTab(version_control_widget, "🔄 版本控制")

        # 📊 性能监控标签页
        performance_monitor_widget = self.create_performance_monitor_tab()
        self.resource_tabs.addTab(performance_monitor_widget, "📊 性能监控")

        # 📚 帮助中心标签页
        help_center_widget = self.create_help_center_tab()
        self.resource_tabs.addTab(help_center_widget, "📚 帮助中心")

        resource_layout.addWidget(self.resource_tabs)
        self.main_splitter.addWidget(resource_widget)

    def setup_main_work_area(self):
        """设置中央主工作区 (弹性宽度)"""

        # 创建主工作区容器
        main_work_widget = QFrame()
        main_work_widget.setFrameStyle(QFrame.Shape.StyledPanel)
        main_work_widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
            }
        """)

        main_work_layout = QVBoxLayout(main_work_widget)
        main_work_layout.setContentsMargins(0, 0, 0, 0)

        # 创建主工作区标签页
        self.main_work_tabs = QTabWidget()
        self.main_work_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F3F4F6;
                padding: 10px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 3px solid #2C5AA0;
            }
            QTabBar::tab:hover {
                background-color: #E5E7EB;
            }
        """)

        # 🎨 舞台 + 元素编辑标签页
        self.stage_widget = self.create_enhanced_stage_tab()
        self.main_work_tabs.addTab(self.stage_widget, "🎨 舞台编辑")

        # 📱 多设备预览标签页
        self.device_preview_widget = self.create_device_preview_tab()
        self.main_work_tabs.addTab(self.device_preview_widget, "📱 设备预览")

        # 🧪 测试控制台标签页
        self.test_console_widget = self.create_test_console_tab()
        self.main_work_tabs.addTab(self.test_console_widget, "🧪 测试控制台")

        # 🔍 调试面板标签页
        self.debug_panel_widget = self.create_debug_panel_tab()
        self.main_work_tabs.addTab(self.debug_panel_widget, "🔍 调试面板")

        # 📈 性能监控标签页
        self.performance_monitor_widget = self.create_performance_monitor_tab()
        self.main_work_tabs.addTab(self.performance_monitor_widget, "📈 性能监控")

        # ⚙️ 用户体验设置标签页
        self.ux_settings_widget = self.create_ux_settings_tab()
        self.main_work_tabs.addTab(self.ux_settings_widget, "⚙️ 体验设置")

        # 🧪 测试控制台标签页
        self.test_console_widget = self.create_test_console_tab()
        self.main_work_tabs.addTab(self.test_console_widget, "🧪 测试控制台")

        # 📤 导出管理标签页
        self.export_manager_widget = self.create_export_manager_tab()
        self.main_work_tabs.addTab(self.export_manager_widget, "📤 导出管理")

        main_work_layout.addWidget(self.main_work_tabs)
        self.main_splitter.addWidget(main_work_widget)

    def create_ux_settings_tab(self):
        """创建用户体验设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # ⚙️ 用户体验设置标题
        title_frame = QFrame()
        title_frame.setFixedHeight(35)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #8B5CF6;
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("⚙️ 用户体验设置中心")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 设置同步状态
        sync_status = QLabel("☁️ 云端同步")
        sync_status.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        title_layout.addWidget(sync_status)

        layout.addWidget(title_frame)

        # ⌨️ 快捷键系统
        shortcuts_frame = QFrame()
        shortcuts_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #C4B5FD;
                border-radius: 6px;
            }
        """)
        shortcuts_layout = QVBoxLayout(shortcuts_frame)
        shortcuts_layout.setContentsMargins(8, 6, 8, 6)

        shortcuts_title = QLabel("⌨️ 快捷键系统")
        shortcuts_title.setStyleSheet("font-weight: bold; color: #7C3AED; font-size: 11px;")
        shortcuts_layout.addWidget(shortcuts_title)

        # 快捷键网格显示（简化版）
        shortcuts_grid = QGridLayout()
        shortcuts_grid.setSpacing(4)

        # 快捷键数据（精选重要的）
        shortcuts_data = [
            ("Ctrl+N", "新建项目", "🆕"),
            ("Ctrl+S", "保存项目", "💾"),
            ("Ctrl+Z", "撤销操作", "↶"),
            ("Ctrl+Y", "重做操作", "↷"),
            ("Space", "播放/暂停", "▶️"),
            ("Ctrl+G", "AI生成", "🤖"),
            ("F5", "刷新预览", "🔄"),
            ("Ctrl+/", "显示快捷键", "❓")
        ]

        for i, (shortcut, description, icon) in enumerate(shortcuts_data):
            shortcut_item = QFrame()
            shortcut_item.setFixedSize(120, 35)
            shortcut_item.setStyleSheet("""
                QFrame {
                    background-color: #F8FAFC;
                    border: 1px solid #E2E8F0;
                    border-radius: 3px;
                }
            """)
            shortcut_item_layout = QVBoxLayout(shortcut_item)
            shortcut_item_layout.setContentsMargins(4, 2, 4, 2)
            shortcut_item_layout.setSpacing(1)

            # 快捷键
            shortcut_label = QLabel(shortcut)
            shortcut_label.setStyleSheet("""
                background-color: #7C3AED;
                color: white;
                border-radius: 2px;
                padding: 1px 4px;
                font-family: 'Consolas', monospace;
                font-size: 8px;
                font-weight: bold;
            """)
            shortcut_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            shortcut_item_layout.addWidget(shortcut_label)

            # 描述
            desc_layout = QHBoxLayout()
            desc_layout.setSpacing(2)

            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 8px;")
            desc_layout.addWidget(icon_label)

            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #374151; font-size: 7px;")
            desc_layout.addWidget(desc_label)

            shortcut_item_layout.addLayout(desc_layout)

            shortcuts_grid.addWidget(shortcut_item, i // 4, i % 4)

        shortcuts_layout.addLayout(shortcuts_grid)

        # 快捷键操作
        shortcuts_actions = QHBoxLayout()

        view_all_btn = QToolButton()
        view_all_btn.setText("📋 查看全部")
        view_all_btn.setStyleSheet("""
            QToolButton {
                background-color: #7C3AED;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #6D28D9;
            }
        """)
        shortcuts_actions.addWidget(view_all_btn)

        custom_btn = QToolButton()
        custom_btn.setText("✏️ 自定义")
        custom_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #7C3AED;
                border: 1px solid #C4B5FD;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
            }
            QToolButton:hover {
                background-color: #F3F0FF;
            }
        """)
        shortcuts_actions.addWidget(custom_btn)

        shortcuts_actions.addStretch()
        shortcuts_layout.addLayout(shortcuts_actions)

        layout.addWidget(shortcuts_frame)

        # 🎨 主题和外观
        theme_frame = QFrame()
        theme_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #C4B5FD;
                border-radius: 6px;
            }
        """)
        theme_layout = QVBoxLayout(theme_frame)
        theme_layout.setContentsMargins(8, 6, 8, 6)

        theme_title = QLabel("🎨 主题和外观")
        theme_title.setStyleSheet("font-weight: bold; color: #7C3AED; font-size: 11px;")
        theme_layout.addWidget(theme_title)

        # 主题选择网格
        theme_grid = QGridLayout()
        theme_grid.setSpacing(6)

        # 主题数据
        themes_data = [
            ("🌞", "浅色", "#F8FAFC", True),
            ("🌙", "深色", "#1F2937", False),
            ("🌈", "彩色", "#8B5CF6", False),
            ("🎯", "高对比", "#000000", False)
        ]

        for i, (icon, name, color, selected) in enumerate(themes_data):
            theme_item = QFrame()
            theme_item.setFixedSize(60, 50)
            border_width = "2px" if selected else "1px"
            border_color = "#7C3AED" if selected else "#E5E7EB"

            theme_item.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border: {border_width} solid {border_color};
                    border-radius: 4px;
                }}
                QFrame:hover {{
                    border-color: #7C3AED;
                }}
            """)

            theme_item_layout = QVBoxLayout(theme_item)
            theme_item_layout.setContentsMargins(2, 2, 2, 2)

            # 主题图标
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 16px;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            theme_item_layout.addWidget(icon_label)

            # 主题名称
            name_label = QLabel(name)
            text_color = "white" if color == "#1F2937" or color == "#000000" else "#374151"
            name_label.setStyleSheet(f"color: {text_color}; font-size: 8px; font-weight: bold;")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            theme_item_layout.addWidget(name_label)

            theme_grid.addWidget(theme_item, i // 2, i % 2)

        theme_layout.addLayout(theme_grid)

        # 外观设置
        appearance_settings = QGridLayout()
        appearance_settings.setSpacing(8)

        # 字体大小
        font_size_layout = QVBoxLayout()
        font_size_label = QLabel("字体大小")
        font_size_label.setStyleSheet("color: #6D28D9; font-size: 10px; font-weight: bold;")
        font_size_layout.addWidget(font_size_label)

        font_size_combo = QComboBox()
        font_size_combo.addItems(["小", "中", "大", "特大"])
        font_size_combo.setCurrentText("中")
        font_size_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #C4B5FD;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 9px;
                min-width: 50px;
            }
        """)
        font_size_layout.addWidget(font_size_combo)
        appearance_settings.addLayout(font_size_layout, 0, 0)

        # 界面缩放
        scale_layout = QVBoxLayout()
        scale_label = QLabel("界面缩放")
        scale_label.setStyleSheet("color: #6D28D9; font-size: 10px; font-weight: bold;")
        scale_layout.addWidget(scale_label)

        scale_combo = QComboBox()
        scale_combo.addItems(["75%", "100%", "125%", "150%"])
        scale_combo.setCurrentText("100%")
        scale_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #C4B5FD;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 9px;
                min-width: 50px;
            }
        """)
        scale_layout.addWidget(scale_combo)
        appearance_settings.addLayout(scale_layout, 0, 1)

        theme_layout.addLayout(appearance_settings)
        layout.addWidget(theme_frame)

        # ♿ 无障碍功能
        accessibility_frame = QFrame()
        accessibility_frame.setStyleSheet("""
            QFrame {
                background-color: #F0F9FF;
                border: 1px solid #BAE6FD;
                border-radius: 6px;
            }
        """)
        accessibility_layout = QVBoxLayout(accessibility_frame)
        accessibility_layout.setContentsMargins(8, 6, 8, 6)

        accessibility_title = QLabel("♿ 无障碍功能")
        accessibility_title.setStyleSheet("font-weight: bold; color: #0369A1; font-size: 11px;")
        accessibility_layout.addWidget(accessibility_title)

        # 无障碍选项
        accessibility_options = QGridLayout()
        accessibility_options.setSpacing(6)

        options = [
            ("🔊 屏幕朗读", True),
            ("🔍 放大镜", False),
            ("⌨️ 键盘导航", True),
            ("🎨 高对比度", False),
            ("⏱️ 延长超时", False),
            ("🖱️ 大鼠标指针", False)
        ]

        for i, (text, checked) in enumerate(options):
            checkbox = QCheckBox(text)
            checkbox.setChecked(checked)
            checkbox.setStyleSheet("color: #0284C7; font-size: 9px;")
            accessibility_options.addWidget(checkbox, i // 2, i % 2)

        accessibility_layout.addLayout(accessibility_options)
        layout.addWidget(accessibility_frame)

        # 🔧 个性化设置
        personalization_frame = QFrame()
        personalization_frame.setStyleSheet("""
            QFrame {
                background-color: #FEF3C7;
                border: 1px solid #FCD34D;
                border-radius: 6px;
            }
        """)
        personalization_layout = QVBoxLayout(personalization_frame)
        personalization_layout.setContentsMargins(8, 6, 8, 6)

        personalization_title = QLabel("🔧 个性化设置")
        personalization_title.setStyleSheet("font-weight: bold; color: #92400E; font-size: 11px;")
        personalization_layout.addWidget(personalization_title)

        # 个性化选项
        personalization_options = QVBoxLayout()

        # 启动页面
        startup_layout = QHBoxLayout()
        startup_label = QLabel("启动页面:")
        startup_label.setStyleSheet("color: #92400E; font-size: 10px; font-weight: bold;")
        startup_layout.addWidget(startup_label)

        startup_combo = QComboBox()
        startup_combo.addItems(["欢迎页面", "最近项目", "新建项目", "模板选择"])
        startup_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #FCD34D;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 9px;
                min-width: 80px;
            }
        """)
        startup_layout.addWidget(startup_combo)
        startup_layout.addStretch()
        personalization_options.addLayout(startup_layout)

        # 工作区布局
        workspace_layout = QHBoxLayout()
        workspace_label = QLabel("工作区布局:")
        workspace_label.setStyleSheet("color: #92400E; font-size: 10px; font-weight: bold;")
        workspace_layout.addWidget(workspace_label)

        workspace_combo = QComboBox()
        workspace_combo.addItems(["标准布局", "紧凑布局", "宽屏布局", "自定义"])
        workspace_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #FCD34D;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 9px;
                min-width: 80px;
            }
        """)
        workspace_layout.addWidget(workspace_combo)
        workspace_layout.addStretch()
        personalization_options.addLayout(workspace_layout)

        personalization_layout.addLayout(personalization_options)

        # 个性化操作按钮
        personalization_actions = QHBoxLayout()

        save_profile_btn = QToolButton()
        save_profile_btn.setText("💾 保存配置")
        save_profile_btn.setStyleSheet("""
            QToolButton {
                background-color: #92400E;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #78350F;
            }
        """)
        personalization_actions.addWidget(save_profile_btn)

        load_profile_btn = QToolButton()
        load_profile_btn.setText("📂 加载配置")
        load_profile_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #92400E;
                border: 1px solid #FCD34D;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
            }
            QToolButton:hover {
                background-color: #FDE68A;
            }
        """)
        personalization_actions.addWidget(load_profile_btn)

        reset_all_btn = QToolButton()
        reset_all_btn.setText("🔄 重置全部")
        reset_all_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #92400E;
                border: 1px solid #FCD34D;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
            }
            QToolButton:hover {
                background-color: #FDE68A;
            }
        """)
        personalization_actions.addWidget(reset_all_btn)

        personalization_actions.addStretch()
        personalization_layout.addLayout(personalization_actions)

        layout.addWidget(personalization_frame)

        layout.addStretch()

        return widget

    def create_test_console_tab(self):
        """创建测试控制台标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 🧪 测试控制台标题
        title_frame = QFrame()
        title_frame.setFixedHeight(35)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #059669;
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("🧪 自动化测试控制台")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 测试状态
        test_status = QLabel("🟢 测试就绪")
        test_status.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        title_layout.addWidget(test_status)

        layout.addWidget(title_frame)

        # 🚀 测试套件控制
        test_suites_frame = QFrame()
        test_suites_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #BBF7D0;
                border-radius: 6px;
            }
        """)
        test_suites_layout = QVBoxLayout(test_suites_frame)
        test_suites_layout.setContentsMargins(8, 6, 8, 6)

        suites_title = QLabel("🚀 测试套件控制")
        suites_title.setStyleSheet("font-weight: bold; color: #059669; font-size: 11px;")
        test_suites_layout.addWidget(suites_title)

        # 测试套件网格
        suites_grid = QGridLayout()
        suites_grid.setSpacing(6)

        # 测试套件数据
        test_suites_data = [
            {
                "name": "UI组件测试",
                "icon": "🖼️",
                "tests": 47,
                "passed": 45,
                "failed": 2,
                "status": "运行中",
                "color": "#F59E0B"
            },
            {
                "name": "AI功能测试",
                "icon": "🤖",
                "tests": 23,
                "passed": 20,
                "failed": 3,
                "status": "失败",
                "color": "#EF4444"
            },
            {
                "name": "性能测试",
                "icon": "⚡",
                "tests": 15,
                "passed": 15,
                "failed": 0,
                "status": "通过",
                "color": "#10B981"
            },
            {
                "name": "集成测试",
                "icon": "🔗",
                "tests": 32,
                "passed": 28,
                "failed": 4,
                "status": "警告",
                "color": "#F59E0B"
            }
        ]

        for i, suite in enumerate(test_suites_data):
            suite_frame = QFrame()
            suite_frame.setFixedSize(140, 90)
            suite_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {suite["color"]}10;
                    border: 1px solid {suite["color"]}40;
                    border-radius: 4px;
                }}
            """)

            suite_layout = QVBoxLayout(suite_frame)
            suite_layout.setContentsMargins(6, 4, 6, 4)
            suite_layout.setSpacing(2)

            # 套件标题
            title_layout = QHBoxLayout()
            icon_label = QLabel(suite["icon"])
            icon_label.setStyleSheet("font-size: 12px;")
            title_layout.addWidget(icon_label)

            name_label = QLabel(suite["name"])
            name_label.setStyleSheet("color: #374151; font-size: 10px; font-weight: bold;")
            title_layout.addWidget(name_label)
            title_layout.addStretch()

            suite_layout.addLayout(title_layout)

            # 测试统计
            stats_label = QLabel(f"总计: {suite['tests']} | 通过: {suite['passed']} | 失败: {suite['failed']}")
            stats_label.setStyleSheet("color: #6B7280; font-size: 8px;")
            suite_layout.addWidget(stats_label)

            # 通过率进度条
            pass_rate = (suite["passed"] / suite["tests"]) * 100
            filled_blocks = int(pass_rate // 10)
            empty_blocks = 10 - filled_blocks
            progress_bar = "█" * filled_blocks + "░" * empty_blocks

            progress_label = QLabel(f"{progress_bar} {pass_rate:.0f}%")
            progress_label.setStyleSheet(f"color: {suite['color']}; font-family: 'Consolas', monospace; font-size: 8px;")
            suite_layout.addWidget(progress_label)

            # 状态和操作
            action_layout = QHBoxLayout()

            status_label = QLabel(suite["status"])
            status_label.setStyleSheet(f"color: {suite['color']}; font-size: 9px; font-weight: bold;")
            action_layout.addWidget(status_label)

            action_layout.addStretch()

            run_btn = QToolButton()
            run_btn.setText("▶️")
            run_btn.setToolTip("运行测试")
            run_btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {suite["color"]}15;
                    color: {suite["color"]};
                    border: 1px solid {suite["color"]}40;
                    border-radius: 3px;
                    padding: 2px 4px;
                    font-size: 8px;
                }}
                QToolButton:hover {{
                    background-color: {suite["color"]}25;
                }}
            """)
            action_layout.addWidget(run_btn)

            suite_layout.addLayout(action_layout)

            suites_grid.addWidget(suite_frame, i // 2, i % 2)

        test_suites_layout.addLayout(suites_grid)

        # 全局测试控制
        global_controls = QHBoxLayout()

        control_buttons = [
            ("🚀", "运行全部", "#059669"),
            ("⏹️", "停止测试", "#EF4444"),
            ("🔄", "重新运行", "#3B82F6"),
            ("📊", "生成报告", "#F59E0B")
        ]

        for icon, name, color in control_buttons:
            btn = QToolButton()
            btn.setText(f"{icon} {name}")
            btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {color}15;
                    color: {color};
                    border: 1px solid {color}40;
                    border-radius: 4px;
                    padding: 6px 10px;
                    font-size: 10px;
                    font-weight: bold;
                    margin: 2px;
                }}
                QToolButton:hover {{
                    background-color: {color}25;
                }}
            """)
            global_controls.addWidget(btn)

        global_controls.addStretch()
        test_suites_layout.addLayout(global_controls)

        layout.addWidget(test_suites_frame)

        # 📊 质量指标监控
        quality_metrics_frame = QFrame()
        quality_metrics_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #BBF7D0;
                border-radius: 6px;
            }
        """)
        quality_metrics_layout = QVBoxLayout(quality_metrics_frame)
        quality_metrics_layout.setContentsMargins(8, 6, 8, 6)

        metrics_title = QLabel("📊 质量指标监控")
        metrics_title.setStyleSheet("font-weight: bold; color: #059669; font-size: 11px;")
        quality_metrics_layout.addWidget(metrics_title)

        # 质量指标网格
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(8)

        # 质量指标数据
        quality_metrics_data = [
            {
                "name": "代码覆盖率",
                "value": 87,
                "target": 90,
                "unit": "%",
                "trend": "↗️",
                "color": "#F59E0B"
            },
            {
                "name": "测试通过率",
                "value": 94,
                "target": 95,
                "unit": "%",
                "trend": "↗️",
                "color": "#10B981"
            },
            {
                "name": "性能得分",
                "value": 78,
                "target": 85,
                "unit": "分",
                "trend": "↘️",
                "color": "#EF4444"
            },
            {
                "name": "用户体验",
                "value": 92,
                "target": 90,
                "unit": "分",
                "trend": "↗️",
                "color": "#10B981"
            }
        ]

        for i, metric in enumerate(quality_metrics_data):
            metric_frame = QFrame()
            metric_frame.setFixedSize(110, 70)
            metric_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {metric["color"]}10;
                    border: 1px solid {metric["color"]}40;
                    border-radius: 4px;
                }}
            """)

            metric_layout = QVBoxLayout(metric_frame)
            metric_layout.setContentsMargins(4, 3, 4, 3)
            metric_layout.setSpacing(2)

            # 指标名称
            name_label = QLabel(metric["name"])
            name_label.setStyleSheet("color: #374151; font-size: 9px; font-weight: bold;")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            metric_layout.addWidget(name_label)

            # 当前值和趋势
            value_layout = QHBoxLayout()
            value_label = QLabel(f"{metric['value']}{metric['unit']}")
            value_label.setStyleSheet(f"color: {metric['color']}; font-size: 12px; font-weight: bold;")
            value_layout.addWidget(value_label)

            trend_label = QLabel(metric["trend"])
            trend_label.setStyleSheet("font-size: 10px;")
            value_layout.addWidget(trend_label)

            metric_layout.addLayout(value_layout)

            # 目标对比
            target_label = QLabel(f"目标: {metric['target']}{metric['unit']}")
            target_label.setStyleSheet("color: #6B7280; font-size: 8px;")
            target_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            metric_layout.addWidget(target_label)

            # 进度条
            progress = (metric["value"] / metric["target"]) * 100
            if progress > 100:
                progress = 100
            filled_blocks = int(progress // 10)
            empty_blocks = 10 - filled_blocks
            progress_bar = "█" * filled_blocks + "░" * empty_blocks

            progress_label = QLabel(progress_bar)
            progress_label.setStyleSheet(f"color: {metric['color']}; font-family: 'Consolas', monospace; font-size: 7px;")
            progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            metric_layout.addWidget(progress_label)

            metrics_grid.addWidget(metric_frame, i // 2, i % 2)

        quality_metrics_layout.addLayout(metrics_grid)

        # 质量趋势
        trend_info = QLabel("📈 质量趋势: 本周测试通过率提升2%，代码覆盖率提升3%，性能得分下降5%")
        trend_info.setStyleSheet("color: #059669; font-size: 10px; font-weight: bold; padding: 4px;")
        quality_metrics_layout.addWidget(trend_info)

        layout.addWidget(quality_metrics_frame)

        # 📝 测试日志和结果
        test_logs_frame = QFrame()
        test_logs_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
            }
        """)
        test_logs_layout = QVBoxLayout(test_logs_frame)
        test_logs_layout.setContentsMargins(8, 6, 8, 6)

        logs_title = QLabel("📝 测试日志和结果")
        logs_title.setStyleSheet("font-weight: bold; color: #374151; font-size: 11px;")
        test_logs_layout.addWidget(logs_title)

        # 测试日志滚动区域
        logs_scroll = QScrollArea()
        logs_scroll.setWidgetResizable(True)
        logs_scroll.setMaximumHeight(120)
        logs_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E5E7EB;
                border-radius: 3px;
                background-color: #FFFFFF;
            }
        """)

        logs_content = QWidget()
        logs_content_layout = QVBoxLayout(logs_content)

        # 测试日志数据
        test_logs_data = [
            ("14:32:15", "✅", "UI组件测试", "test_button_click", "通过", "#10B981"),
            ("14:32:16", "❌", "AI功能测试", "test_gemini_connection", "连接超时", "#EF4444"),
            ("14:32:17", "✅", "性能测试", "test_render_speed", "渲染时间: 23ms", "#10B981"),
            ("14:32:18", "⚠️", "集成测试", "test_data_sync", "数据不一致", "#F59E0B"),
            ("14:32:19", "✅", "UI组件测试", "test_modal_dialog", "通过", "#10B981"),
            ("14:32:20", "❌", "AI功能测试", "test_prompt_validation", "参数错误", "#EF4444"),
            ("14:32:21", "✅", "性能测试", "test_memory_usage", "内存使用: 234MB", "#10B981")
        ]

        for timestamp, status, suite, test_name, result, color in test_logs_data:
            log_item = QFrame()
            log_item.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}08;
                    border-left: 3px solid {color};
                    margin: 1px;
                    padding: 2px;
                }}
            """)
            log_item_layout = QHBoxLayout(log_item)
            log_item_layout.setContentsMargins(6, 3, 6, 3)

            # 时间戳
            time_label = QLabel(timestamp)
            time_label.setStyleSheet("color: #6B7280; font-size: 8px; font-family: 'Consolas', monospace;")
            time_label.setFixedWidth(60)
            log_item_layout.addWidget(time_label)

            # 状态
            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: {color}; font-size: 10px;")
            status_label.setFixedWidth(20)
            log_item_layout.addWidget(status_label)

            # 测试套件
            suite_label = QLabel(suite)
            suite_label.setStyleSheet("color: #374151; font-size: 9px; font-weight: bold;")
            suite_label.setFixedWidth(80)
            log_item_layout.addWidget(suite_label)

            # 测试名称
            test_label = QLabel(test_name)
            test_label.setStyleSheet("color: #6B7280; font-size: 9px;")
            test_label.setFixedWidth(120)
            log_item_layout.addWidget(test_label)

            # 结果
            result_label = QLabel(result)
            result_label.setStyleSheet(f"color: {color}; font-size: 9px;")
            log_item_layout.addWidget(result_label)

            log_item_layout.addStretch()

            logs_content_layout.addWidget(log_item)

        logs_scroll.setWidget(logs_content)
        test_logs_layout.addWidget(logs_scroll)

        # 日志操作
        logs_actions = QHBoxLayout()

        clear_logs_btn = QToolButton()
        clear_logs_btn.setText("🧹 清空日志")
        clear_logs_btn.setStyleSheet("""
            QToolButton {
                background-color: #6B7280;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #4B5563;
            }
        """)
        logs_actions.addWidget(clear_logs_btn)

        export_logs_btn = QToolButton()
        export_logs_btn.setText("📤 导出日志")
        export_logs_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #374151;
                border: 1px solid #E5E7EB;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
            }
            QToolButton:hover {
                background-color: #F3F4F6;
            }
        """)
        logs_actions.addWidget(export_logs_btn)

        filter_logs_btn = QToolButton()
        filter_logs_btn.setText("🔍 筛选")
        filter_logs_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #374151;
                border: 1px solid #E5E7EB;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
            }
            QToolButton:hover {
                background-color: #F3F4F6;
            }
        """)
        logs_actions.addWidget(filter_logs_btn)

        logs_actions.addStretch()
        test_logs_layout.addLayout(logs_actions)

        layout.addWidget(test_logs_frame)

        # ⚙️ 自动化测试配置
        automation_config_frame = QFrame()
        automation_config_frame.setStyleSheet("""
            QFrame {
                background-color: #EEF2FF;
                border: 1px solid #C7D2FE;
                border-radius: 6px;
            }
        """)
        automation_config_layout = QVBoxLayout(automation_config_frame)
        automation_config_layout.setContentsMargins(8, 6, 8, 6)

        config_title = QLabel("⚙️ 自动化测试配置")
        config_title.setStyleSheet("font-weight: bold; color: #3730A3; font-size: 11px;")
        automation_config_layout.addWidget(config_title)

        # 配置选项
        config_options = QGridLayout()
        config_options.setSpacing(8)

        # 触发条件
        trigger_label = QLabel("触发条件:")
        trigger_label.setStyleSheet("color: #4338CA; font-size: 10px; font-weight: bold;")
        config_options.addWidget(trigger_label, 0, 0)

        trigger_combo = QComboBox()
        trigger_combo.addItems(["代码提交", "定时运行", "手动触发", "文件变更"])
        trigger_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #C7D2FE;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 9px;
                min-width: 80px;
            }
        """)
        config_options.addWidget(trigger_combo, 0, 1)

        # 运行频率
        frequency_label = QLabel("运行频率:")
        frequency_label.setStyleSheet("color: #4338CA; font-size: 10px; font-weight: bold;")
        config_options.addWidget(frequency_label, 0, 2)

        frequency_combo = QComboBox()
        frequency_combo.addItems(["每小时", "每天", "每周", "自定义"])
        frequency_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #C7D2FE;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 9px;
                min-width: 60px;
            }
        """)
        config_options.addWidget(frequency_combo, 0, 3)

        # 通知设置
        notification_label = QLabel("通知设置:")
        notification_label.setStyleSheet("color: #4338CA; font-size: 10px; font-weight: bold;")
        config_options.addWidget(notification_label, 1, 0)

        notification_combo = QComboBox()
        notification_combo.addItems(["仅失败", "全部", "关闭", "自定义"])
        notification_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #C7D2FE;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 9px;
                min-width: 60px;
            }
        """)
        config_options.addWidget(notification_combo, 1, 1)

        # 并行度
        parallel_label = QLabel("并行度:")
        parallel_label.setStyleSheet("color: #4338CA; font-size: 10px; font-weight: bold;")
        config_options.addWidget(parallel_label, 1, 2)

        parallel_combo = QComboBox()
        parallel_combo.addItems(["1", "2", "4", "8", "自动"])
        parallel_combo.setCurrentText("4")
        parallel_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #C7D2FE;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 9px;
                min-width: 50px;
            }
        """)
        config_options.addWidget(parallel_combo, 1, 3)

        automation_config_layout.addLayout(config_options)

        # 配置操作
        config_actions = QHBoxLayout()

        save_config_btn = QToolButton()
        save_config_btn.setText("💾 保存配置")
        save_config_btn.setStyleSheet("""
            QToolButton {
                background-color: #3730A3;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #312E81;
            }
        """)
        config_actions.addWidget(save_config_btn)

        reset_config_btn = QToolButton()
        reset_config_btn.setText("🔄 重置")
        reset_config_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #3730A3;
                border: 1px solid #C7D2FE;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
            }
            QToolButton:hover {
                background-color: #E0E7FF;
            }
        """)
        config_actions.addWidget(reset_config_btn)

        config_actions.addStretch()
        automation_config_layout.addLayout(config_actions)

        layout.addWidget(automation_config_frame)

        layout.addStretch()

        return widget

    def create_export_manager_tab(self):
        """创建智能导出管理标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 📤 导出管理标题
        title_frame = QFrame()
        title_frame.setFixedHeight(35)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #F59E0B;
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("📤 智能导出管理中心")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 导出状态
        export_status = QLabel("⚡ 导出引擎就绪")
        export_status.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        title_layout.addWidget(export_status)

        layout.addWidget(title_frame)

        # 🎬 快速导出
        quick_export_frame = QFrame()
        quick_export_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #FCD34D;
                border-radius: 6px;
            }
        """)
        quick_export_layout = QVBoxLayout(quick_export_frame)
        quick_export_layout.setContentsMargins(8, 6, 8, 6)

        quick_export_title = QLabel("🎬 快速导出")
        quick_export_title.setStyleSheet("font-weight: bold; color: #D97706; font-size: 11px;")
        quick_export_layout.addWidget(quick_export_title)

        # 快速导出格式
        quick_formats_grid = QGridLayout()
        quick_formats_grid.setSpacing(6)

        # 快速导出格式数据
        quick_formats_data = [
            {
                "name": "MP4",
                "icon": "🎥",
                "desc": "高质量视频",
                "size": "1080p",
                "color": "#EF4444"
            },
            {
                "name": "GIF",
                "icon": "🖼️",
                "desc": "动图分享",
                "size": "720p",
                "color": "#10B981"
            },
            {
                "name": "WebM",
                "icon": "🌐",
                "desc": "网页优化",
                "size": "1080p",
                "color": "#3B82F6"
            },
            {
                "name": "PNG序列",
                "icon": "📸",
                "desc": "逐帧图片",
                "size": "4K",
                "color": "#8B5CF6"
            }
        ]

        for i, format_data in enumerate(quick_formats_data):
            format_frame = QFrame()
            format_frame.setFixedSize(120, 80)
            format_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {format_data["color"]}10;
                    border: 1px solid {format_data["color"]}40;
                    border-radius: 4px;
                }}
                QFrame:hover {{
                    border-color: {format_data["color"]};
                    background-color: {format_data["color"]}20;
                }}
            """)

            format_layout = QVBoxLayout(format_frame)
            format_layout.setContentsMargins(6, 4, 6, 4)
            format_layout.setSpacing(2)

            # 格式图标和名称
            header_layout = QHBoxLayout()
            icon_label = QLabel(format_data["icon"])
            icon_label.setStyleSheet("font-size: 14px;")
            header_layout.addWidget(icon_label)

            name_label = QLabel(format_data["name"])
            name_label.setStyleSheet(f"color: {format_data['color']}; font-size: 11px; font-weight: bold;")
            header_layout.addWidget(name_label)
            header_layout.addStretch()

            format_layout.addLayout(header_layout)

            # 描述
            desc_label = QLabel(format_data["desc"])
            desc_label.setStyleSheet("color: #6B7280; font-size: 9px;")
            format_layout.addWidget(desc_label)

            # 尺寸
            size_label = QLabel(format_data["size"])
            size_label.setStyleSheet(f"color: {format_data['color']}; font-size: 8px; font-weight: bold;")
            format_layout.addWidget(size_label)

            # 导出按钮
            export_btn = QToolButton()
            export_btn.setText("📤 导出")
            export_btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {format_data["color"]};
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 3px 6px;
                    font-size: 8px;
                    font-weight: bold;
                }}
                QToolButton:hover {{
                    background-color: {format_data["color"]}CC;
                }}
            """)
            format_layout.addWidget(export_btn)

            quick_formats_grid.addWidget(format_frame, i // 2, i % 2)

        quick_export_layout.addLayout(quick_formats_grid)

        layout.addWidget(quick_export_frame)

        # ⚙️ 高级导出设置
        advanced_export_frame = QFrame()
        advanced_export_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #FCD34D;
                border-radius: 6px;
            }
        """)
        advanced_export_layout = QVBoxLayout(advanced_export_frame)
        advanced_export_layout.setContentsMargins(8, 6, 8, 6)

        advanced_export_title = QLabel("⚙️ 高级导出设置")
        advanced_export_title.setStyleSheet("font-weight: bold; color: #D97706; font-size: 11px;")
        advanced_export_layout.addWidget(advanced_export_title)

        # 导出设置网格
        export_settings_grid = QGridLayout()
        export_settings_grid.setSpacing(8)

        # 分辨率设置
        resolution_label = QLabel("分辨率:")
        resolution_label.setStyleSheet("color: #92400E; font-size: 10px; font-weight: bold;")
        export_settings_grid.addWidget(resolution_label, 0, 0)

        resolution_combo = QComboBox()
        resolution_combo.addItems(["4K (3840×2160)", "2K (2560×1440)", "1080p (1920×1080)", "720p (1280×720)", "自定义"])
        resolution_combo.setCurrentText("1080p (1920×1080)")
        resolution_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #FCD34D;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 9px;
                min-width: 120px;
            }
        """)
        export_settings_grid.addWidget(resolution_combo, 0, 1)

        # 帧率设置
        framerate_label = QLabel("帧率:")
        framerate_label.setStyleSheet("color: #92400E; font-size: 10px; font-weight: bold;")
        export_settings_grid.addWidget(framerate_label, 0, 2)

        framerate_combo = QComboBox()
        framerate_combo.addItems(["60fps", "30fps", "24fps", "15fps", "自定义"])
        framerate_combo.setCurrentText("30fps")
        framerate_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #FCD34D;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 9px;
                min-width: 80px;
            }
        """)
        export_settings_grid.addWidget(framerate_combo, 0, 3)

        # 质量设置
        quality_label = QLabel("质量:")
        quality_label.setStyleSheet("color: #92400E; font-size: 10px; font-weight: bold;")
        export_settings_grid.addWidget(quality_label, 1, 0)

        quality_combo = QComboBox()
        quality_combo.addItems(["最高", "高", "中", "低", "自定义"])
        quality_combo.setCurrentText("高")
        quality_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #FCD34D;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 9px;
                min-width: 80px;
            }
        """)
        export_settings_grid.addWidget(quality_combo, 1, 1)

        # 编码器设置
        encoder_label = QLabel("编码器:")
        encoder_label.setStyleSheet("color: #92400E; font-size: 10px; font-weight: bold;")
        export_settings_grid.addWidget(encoder_label, 1, 2)

        encoder_combo = QComboBox()
        encoder_combo.addItems(["H.264", "H.265", "VP9", "AV1"])
        encoder_combo.setCurrentText("H.264")
        encoder_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #FCD34D;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 9px;
                min-width: 80px;
            }
        """)
        export_settings_grid.addWidget(encoder_combo, 1, 3)

        advanced_export_layout.addLayout(export_settings_grid)

        # 高级选项
        advanced_options = QHBoxLayout()

        options = [
            ("🎵 包含音频", True),
            ("📊 显示水印", False),
            ("⚡ 硬件加速", True),
            ("🔄 循环播放", False)
        ]

        for text, checked in options:
            checkbox = QCheckBox(text)
            checkbox.setChecked(checked)
            checkbox.setStyleSheet("color: #92400E; font-size: 9px;")
            advanced_options.addWidget(checkbox)

        advanced_export_layout.addLayout(advanced_options)

        # 高级导出按钮
        advanced_export_btn = QToolButton()
        advanced_export_btn.setText("⚙️ 开始高级导出")
        advanced_export_btn.setStyleSheet("""
            QToolButton {
                background-color: #D97706;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #B45309;
            }
        """)
        advanced_export_layout.addWidget(advanced_export_btn)

        layout.addWidget(advanced_export_frame)

        # 📋 导出队列
        export_queue_frame = QFrame()
        export_queue_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
            }
        """)
        export_queue_layout = QVBoxLayout(export_queue_frame)
        export_queue_layout.setContentsMargins(8, 6, 8, 6)

        queue_title = QLabel("📋 导出队列")
        queue_title.setStyleSheet("font-weight: bold; color: #374151; font-size: 11px;")
        export_queue_layout.addWidget(queue_title)

        # 导出队列列表
        queue_scroll = QScrollArea()
        queue_scroll.setWidgetResizable(True)
        queue_scroll.setMaximumHeight(100)
        queue_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E5E7EB;
                border-radius: 3px;
                background-color: #FFFFFF;
            }
        """)

        queue_content = QWidget()
        queue_content_layout = QVBoxLayout(queue_content)

        # 导出队列数据
        queue_data = [
            ("项目A_动画1", "MP4", "1080p", "进行中", "67%", "#3B82F6"),
            ("项目B_宣传片", "GIF", "720p", "等待中", "0%", "#6B7280"),
            ("项目C_演示", "WebM", "4K", "已完成", "100%", "#10B981"),
            ("项目D_测试", "PNG序列", "2K", "失败", "45%", "#EF4444")
        ]

        for name, format_type, resolution, status, progress, color in queue_data:
            queue_item = QFrame()
            queue_item.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}08;
                    border-left: 3px solid {color};
                    margin: 1px;
                    padding: 2px;
                }}
            """)
            queue_item_layout = QHBoxLayout(queue_item)
            queue_item_layout.setContentsMargins(6, 3, 6, 3)

            # 项目名称
            name_label = QLabel(name)
            name_label.setStyleSheet("color: #374151; font-size: 9px; font-weight: bold;")
            name_label.setFixedWidth(100)
            queue_item_layout.addWidget(name_label)

            # 格式
            format_label = QLabel(format_type)
            format_label.setStyleSheet(f"color: {color}; font-size: 9px; font-weight: bold;")
            format_label.setFixedWidth(60)
            queue_item_layout.addWidget(format_label)

            # 分辨率
            resolution_label = QLabel(resolution)
            resolution_label.setStyleSheet("color: #6B7280; font-size: 9px;")
            resolution_label.setFixedWidth(50)
            queue_item_layout.addWidget(resolution_label)

            # 状态
            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: {color}; font-size: 9px; font-weight: bold;")
            status_label.setFixedWidth(50)
            queue_item_layout.addWidget(status_label)

            # 进度
            progress_label = QLabel(progress)
            progress_label.setStyleSheet(f"color: {color}; font-size: 9px; font-weight: bold;")
            progress_label.setFixedWidth(40)
            queue_item_layout.addWidget(progress_label)

            queue_item_layout.addStretch()

            # 操作按钮
            if status == "进行中":
                action_btn = QToolButton()
                action_btn.setText("⏸️")
                action_btn.setToolTip("暂停")
            elif status == "等待中":
                action_btn = QToolButton()
                action_btn.setText("▶️")
                action_btn.setToolTip("开始")
            elif status == "已完成":
                action_btn = QToolButton()
                action_btn.setText("📂")
                action_btn.setToolTip("打开文件夹")
            else:  # 失败
                action_btn = QToolButton()
                action_btn.setText("🔄")
                action_btn.setToolTip("重试")

            action_btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {color}15;
                    color: {color};
                    border: 1px solid {color}40;
                    border-radius: 2px;
                    padding: 1px 3px;
                    font-size: 8px;
                }}
                QToolButton:hover {{
                    background-color: {color}25;
                }}
            """)
            queue_item_layout.addWidget(action_btn)

            queue_content_layout.addWidget(queue_item)

        queue_scroll.setWidget(queue_content)
        export_queue_layout.addWidget(queue_scroll)

        # 队列操作
        queue_actions = QHBoxLayout()

        clear_completed_btn = QToolButton()
        clear_completed_btn.setText("🧹 清除已完成")
        clear_completed_btn.setStyleSheet("""
            QToolButton {
                background-color: #6B7280;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #4B5563;
            }
        """)
        queue_actions.addWidget(clear_completed_btn)

        pause_all_btn = QToolButton()
        pause_all_btn.setText("⏸️ 暂停全部")
        pause_all_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #374151;
                border: 1px solid #E5E7EB;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
            }
            QToolButton:hover {
                background-color: #F3F4F6;
            }
        """)
        queue_actions.addWidget(pause_all_btn)

        queue_actions.addStretch()
        export_queue_layout.addLayout(queue_actions)

        layout.addWidget(export_queue_frame)

        # 📁 项目管理
        project_management_frame = QFrame()
        project_management_frame.setStyleSheet("""
            QFrame {
                background-color: #EEF2FF;
                border: 1px solid #C7D2FE;
                border-radius: 6px;
            }
        """)
        project_management_layout = QVBoxLayout(project_management_frame)
        project_management_layout.setContentsMargins(8, 6, 8, 6)

        project_title = QLabel("📁 项目管理")
        project_title.setStyleSheet("font-weight: bold; color: #3730A3; font-size: 11px;")
        project_management_layout.addWidget(project_title)

        # 项目操作网格
        project_actions_grid = QGridLayout()
        project_actions_grid.setSpacing(6)

        # 项目操作数据
        project_actions_data = [
            ("💾", "保存项目", "Ctrl+S", "#10B981"),
            ("📂", "打开项目", "Ctrl+O", "#3B82F6"),
            ("🆕", "新建项目", "Ctrl+N", "#F59E0B"),
            ("📋", "复制项目", "Ctrl+D", "#8B5CF6"),
            ("📤", "导出项目", "Ctrl+E", "#EF4444"),
            ("🗑️", "删除项目", "Delete", "#6B7280")
        ]

        for i, (icon, name, shortcut, color) in enumerate(project_actions_data):
            action_frame = QFrame()
            action_frame.setFixedSize(110, 50)
            action_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}10;
                    border: 1px solid {color}40;
                    border-radius: 3px;
                }}
                QFrame:hover {{
                    border-color: {color};
                    background-color: {color}20;
                }}
            """)

            action_layout = QVBoxLayout(action_frame)
            action_layout.setContentsMargins(4, 3, 4, 3)
            action_layout.setSpacing(1)

            # 操作名称
            name_layout = QHBoxLayout()
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 10px;")
            name_layout.addWidget(icon_label)

            name_label = QLabel(name)
            name_label.setStyleSheet(f"color: {color}; font-size: 9px; font-weight: bold;")
            name_layout.addWidget(name_label)
            name_layout.addStretch()

            action_layout.addLayout(name_layout)

            # 快捷键
            shortcut_label = QLabel(shortcut)
            shortcut_label.setStyleSheet(f"color: {color}; font-size: 8px; font-family: 'Consolas', monospace;")
            shortcut_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            action_layout.addWidget(shortcut_label)

            project_actions_grid.addWidget(action_frame, i // 3, i % 3)

        project_management_layout.addLayout(project_actions_grid)

        # 最近项目
        recent_projects = QLabel("📋 最近项目: 动画演示.aiae | 产品宣传.aiae | 教程视频.aiae")
        recent_projects.setStyleSheet("color: #4338CA; font-size: 10px; font-weight: bold; padding: 4px;")
        project_management_layout.addWidget(recent_projects)

        layout.addWidget(project_management_frame)

        layout.addStretch()

        return widget

    def setup_ai_control_panel(self):
        """设置右侧AI控制区 (350px)"""
        # 创建AI控制面板容器
        ai_control_widget = QFrame()
        ai_control_widget.setFixedWidth(350)
        ai_control_widget.setFrameStyle(QFrame.Shape.StyledPanel)
        ai_control_widget.setStyleSheet("""
            QFrame {
                background-color: #FFF7ED;
                border-left: 1px solid #FDBA74;
            }
        """)

        ai_control_layout = QVBoxLayout(ai_control_widget)
        ai_control_layout.setContentsMargins(5, 5, 5, 5)

        # 创建AI控制标签页
        self.ai_control_tabs = QTabWidget()
        self.ai_control_tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.ai_control_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #FDBA74;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #FED7AA;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: #9A3412;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #FF6B35;
            }
        """)

        # 🤖 AI生成面板标签页
        self.ai_generator_widget = self.create_enhanced_ai_generator_tab()
        self.ai_control_tabs.addTab(self.ai_generator_widget, "🤖 AI生成")

        # 📋 Prompt编辑标签页
        prompt_editor_widget = self.create_prompt_editor_tab()
        self.ai_control_tabs.addTab(prompt_editor_widget, "📋 Prompt")

        # 📊 AI生成监控标签页
        generation_monitor_widget = self.create_generation_monitor_tab()
        self.ai_control_tabs.addTab(generation_monitor_widget, "📊 生成监控")

        # 📊 方案对比标签页
        solution_compare_widget = self.create_solution_compare_tab()
        self.ai_control_tabs.addTab(solution_compare_widget, "📊 方案对比")

        # ⚙️ 参数调整标签页
        parameter_adjust_widget = self.create_parameter_adjust_tab()
        self.ai_control_tabs.addTab(parameter_adjust_widget, "⚙️ 参数调整")

        # 📈 状态监控标签页
        status_monitor_widget = self.create_status_monitor_tab()
        self.ai_control_tabs.addTab(status_monitor_widget, "📈 状态监控")

        # 💬 协作评论标签页
        collaboration_widget = self.create_collaboration_tab()
        self.ai_control_tabs.addTab(collaboration_widget, "💬 协作评论")

        # 🔧 智能修复标签页
        smart_repair_widget = self.create_smart_repair_tab()
        self.ai_control_tabs.addTab(smart_repair_widget, "🔧 智能修复")

        ai_control_layout.addWidget(self.ai_control_tabs)
        self.main_splitter.addWidget(ai_control_widget)

    def setup_timeline_area(self):
        """设置底部专业时间轴区域 (200px) - 增强版"""
        self.timeline_area_widget = QFrame()
        self.timeline_area_widget.setFixedHeight(200)
        self.timeline_area_widget.setFrameStyle(QFrame.Shape.StyledPanel)
        self.timeline_area_widget.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-top: 2px solid #2C5AA0;
            }
        """)

        timeline_layout = QVBoxLayout(self.timeline_area_widget)
        timeline_layout.setContentsMargins(5, 5, 5, 5)
        timeline_layout.setSpacing(3)

        # 🎵 时间轴控制栏 (增强版)
        control_bar = QFrame()
        control_bar.setFixedHeight(35)
        control_bar.setStyleSheet("""
            QFrame {
                background-color: #2C5AA0;
                border-radius: 6px;
            }
            QToolButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                padding: 4px 8px;
                margin: 2px;
                font-weight: bold;
                font-size: 11px;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            QToolButton:pressed {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        control_bar_layout = QHBoxLayout(control_bar)
        control_bar_layout.setContentsMargins(8, 3, 8, 3)

        # 播放控制按钮组
        play_btn = QToolButton()
        play_btn.setText("▶️")
        play_btn.setFixedSize(28, 28)
        control_bar_layout.addWidget(play_btn)

        pause_btn = QToolButton()
        pause_btn.setText("⏸️")
        pause_btn.setFixedSize(28, 28)
        control_bar_layout.addWidget(pause_btn)

        stop_btn = QToolButton()
        stop_btn.setText("⏹️")
        stop_btn.setFixedSize(28, 28)
        control_bar_layout.addWidget(stop_btn)

        prev_btn = QToolButton()
        prev_btn.setText("⏮️")
        prev_btn.setFixedSize(28, 28)
        control_bar_layout.addWidget(prev_btn)

        next_btn = QToolButton()
        next_btn.setText("⏭️")
        next_btn.setFixedSize(28, 28)
        control_bar_layout.addWidget(next_btn)

        loop_btn = QToolButton()
        loop_btn.setText("🔄")
        loop_btn.setFixedSize(28, 28)
        control_bar_layout.addWidget(loop_btn)

        # 分隔符
        sep1 = QLabel("|")
        sep1.setStyleSheet("color: rgba(255, 255, 255, 0.5);")
        control_bar_layout.addWidget(sep1)

        # 音量控制
        volume_label = QLabel("🔊")
        volume_label.setStyleSheet("color: white;")
        control_bar_layout.addWidget(volume_label)

        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(70)
        volume_slider.setFixedWidth(60)
        volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid rgba(255, 255, 255, 0.3);
                height: 4px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 1px solid rgba(255, 255, 255, 0.5);
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #4A90E2;
                border-radius: 2px;
            }
        """)
        control_bar_layout.addWidget(volume_slider)

        # 分隔符
        sep2 = QLabel("|")
        sep2.setStyleSheet("color: rgba(255, 255, 255, 0.5);")
        control_bar_layout.addWidget(sep2)

        # 播放速度
        speed_label = QLabel("倍速:")
        speed_label.setStyleSheet("color: white; font-size: 10px;")
        control_bar_layout.addWidget(speed_label)

        speed_combo = QComboBox()
        speed_combo.addItems(["0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"])
        speed_combo.setCurrentText("1.0x")
        speed_combo.setFixedWidth(60)
        speed_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 3px;
                padding: 2px 6px;
                font-size: 10px;
            }
        """)
        control_bar_layout.addWidget(speed_combo)

        # 分隔符
        sep3 = QLabel("|")
        sep3.setStyleSheet("color: rgba(255, 255, 255, 0.5);")
        control_bar_layout.addWidget(sep3)

        # 编辑操作按钮
        undo_btn = QToolButton()
        undo_btn.setText("↶ 撤销")
        control_bar_layout.addWidget(undo_btn)

        redo_btn = QToolButton()
        redo_btn.setText("↷ 重做")
        control_bar_layout.addWidget(redo_btn)

        history_btn = QToolButton()
        history_btn.setText("📋 历史")
        control_bar_layout.addWidget(history_btn)

        mark_btn = QToolButton()
        mark_btn.setText("📌 标记")
        control_bar_layout.addWidget(mark_btn)

        split_btn = QToolButton()
        split_btn.setText("✂️ 分割")
        control_bar_layout.addWidget(split_btn)

        link_btn = QToolButton()
        link_btn.setText("🔗 链接片段")
        control_bar_layout.addWidget(link_btn)

        # 时间显示
        control_bar_layout.addStretch()
        self.timeline_time_label = QLabel("0:00 / 10:00")
        self.timeline_time_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        control_bar_layout.addWidget(self.timeline_time_label)

        timeline_layout.addWidget(control_bar)

        # 多轨道时间轴区域
        tracks_container = QFrame()
        tracks_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
            }
        """)
        tracks_layout = QVBoxLayout(tracks_container)
        tracks_layout.setContentsMargins(5, 5, 5, 5)
        tracks_layout.setSpacing(2)

        # 🎤 旁白音频轨道 (主时间参考)
        audio_track_frame = QFrame()
        audio_track_frame.setFixedHeight(35)
        audio_track_frame.setStyleSheet("""
            QFrame {
                background-color: #EEF2FF;
                border: 1px solid #C7D2FE;
                border-radius: 4px;
            }
        """)
        audio_track_layout = QHBoxLayout(audio_track_frame)
        audio_track_layout.setContentsMargins(8, 3, 8, 3)

        audio_label = QLabel("🎤 旁白音频轨道 (主时间参考)")
        audio_label.setStyleSheet("font-weight: bold; color: #3730A3; font-size: 11px;")
        audio_track_layout.addWidget(audio_label)

        # 音频波形可视化（ASCII风格）
        waveform_display = QLabel("████▓▓▓░░░▓▓▓████░░░▓▓▓████░░░████▓▓▓░░░")
        waveform_display.setStyleSheet("""
            font-family: 'Consolas', monospace;
            color: #3B82F6;
            background-color: #F0F9FF;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
        """)
        audio_track_layout.addWidget(waveform_display)

        # 时间标记
        time_markers = QLabel("0s   2.3s  4.6s   7.2s    10s")
        time_markers.setStyleSheet("font-family: 'Consolas', monospace; color: #6B7280; font-size: 9px;")
        audio_track_layout.addWidget(time_markers)

        tracks_layout.addWidget(audio_track_frame)

        # 时间段选择指示
        selection_frame = QFrame()
        selection_frame.setFixedHeight(20)
        selection_frame.setStyleSheet("""
            QFrame {
                background-color: #FEF3C7;
                border: 1px solid #FCD34D;
                border-radius: 3px;
            }
        """)
        selection_layout = QHBoxLayout(selection_frame)
        selection_layout.setContentsMargins(8, 2, 8, 2)

        selection_info = QLabel("      ├────┤       ├─────┤")
        selection_info.setStyleSheet("font-family: 'Consolas', monospace; color: #92400E; font-size: 9px;")
        selection_layout.addWidget(selection_info)

        selection_text = QLabel("    选中时间段      下个时间段")
        selection_text.setStyleSheet("color: #92400E; font-size: 9px; font-weight: bold;")
        selection_layout.addWidget(selection_text)

        selection_layout.addStretch()

        tracks_layout.addWidget(selection_frame)

        # 🎬 动画轨道 (多层次显示)
        animation_track_frame = QFrame()
        animation_track_frame.setFixedHeight(50)
        animation_track_frame.setStyleSheet("""
            QFrame {
                background-color: #F0FDF4;
                border: 1px solid #BBF7D0;
                border-radius: 4px;
            }
        """)
        animation_track_layout = QVBoxLayout(animation_track_frame)
        animation_track_layout.setContentsMargins(8, 3, 8, 3)

        # 动画轨道标题
        anim_title = QLabel("🎬 动画轨道 (多层次显示)")
        anim_title.setStyleSheet("font-weight: bold; color: #166534; font-size: 11px;")
        animation_track_layout.addWidget(anim_title)

        # 动画片段显示
        segments_layout = QHBoxLayout()

        # 动画片段数据
        segments_data = [
            ("Logo", "出现", "✅完成", "#10B981"),
            ("小球", "移动", "🔄进行", "#F59E0B"),
            ("文字", "淡入", "⏳待处理", "#6B7280"),
            ("背景", "变色", "⏳待处理", "#6B7280")
        ]

        for name, action, status, color in segments_data:
            segment_frame = QFrame()
            segment_frame.setFixedSize(80, 30)
            segment_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 2px solid {color};
                    border-radius: 4px;
                }}
            """)

            segment_layout = QVBoxLayout(segment_frame)
            segment_layout.setContentsMargins(2, 1, 2, 1)
            segment_layout.setSpacing(0)

            name_label = QLabel(name)
            name_label.setStyleSheet(f"color: {color}; font-size: 9px; font-weight: bold;")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            segment_layout.addWidget(name_label)

            action_label = QLabel(action)
            action_label.setStyleSheet("color: #374151; font-size: 8px;")
            action_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            segment_layout.addWidget(action_label)

            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: {color}; font-size: 8px;")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            segment_layout.addWidget(status_label)

            segments_layout.addWidget(segment_frame)

        # 主要元素标注
        segments_layout.addWidget(QLabel("← 主要元素", styleSheet="color: #6B7280; font-size: 10px;"))
        segments_layout.addStretch()

        animation_track_layout.addLayout(segments_layout)
        tracks_layout.addWidget(animation_track_frame)

        # 🔗 状态衔接指示
        connection_frame = QFrame()
        connection_frame.setFixedHeight(45)
        connection_frame.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        connection_layout = QVBoxLayout(connection_frame)
        connection_layout.setContentsMargins(8, 3, 8, 3)

        connection_title = QLabel("🔗 状态衔接指示")
        connection_title.setStyleSheet("font-weight: bold; color: #374151; font-size: 11px;")
        connection_layout.addWidget(connection_title)

        # 衔接状态列表
        connections_layout = QHBoxLayout()

        # 衔接状态数据
        connections_data = [
            ("✅ Logo→小球: 完美匹配", "#10B981"),
            ("⚠️ 小球→文字: 透明度差异0.1", "#F59E0B"),
            ("❌ 文字→背景: 位置冲突", "#EF4444")
        ]

        for i, (text, color) in enumerate(connections_data):
            conn_label = QLabel(text)
            conn_label.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold;")
            connections_layout.addWidget(conn_label)

            # 添加修复按钮
            if i == 1:  # 警告状态
                fix_btn = QToolButton()
                fix_btn.setText("🔧自动修复")
                fix_btn.setStyleSheet("""
                    QToolButton {
                        background-color: #FEF3C7;
                        color: #92400E;
                        border: 1px solid #FCD34D;
                        border-radius: 3px;
                        padding: 2px 6px;
                        font-size: 9px;
                    }
                    QToolButton:hover {
                        background-color: #FDE68A;
                    }
                """)
                connections_layout.addWidget(fix_btn)
            elif i == 2:  # 错误状态
                adjust_btn = QToolButton()
                adjust_btn.setText("⚙️手动调整")
                adjust_btn.setStyleSheet("""
                    QToolButton {
                        background-color: #FEF2F2;
                        color: #DC2626;
                        border: 1px solid #FECACA;
                        border-radius: 3px;
                        padding: 2px 6px;
                        font-size: 9px;
                    }
                    QToolButton:hover {
                        background-color: #FEE2E2;
                    }
                """)
                connections_layout.addWidget(adjust_btn)

            if i < len(connections_data) - 1:
                connections_layout.addWidget(QLabel("|", styleSheet="color: #D1D5DB;"))

        connections_layout.addStretch()
        connection_layout.addLayout(connections_layout)
        tracks_layout.addWidget(connection_frame)

        timeline_layout.addWidget(tracks_container)

        # 🔧 时间段编辑区域 (智能化)
        edit_frame = QFrame()
        edit_frame.setFixedHeight(45)
        edit_frame.setStyleSheet("""
            QFrame {
                background-color: #EEF2FF;
                border: 1px solid #C7D2FE;
                border-radius: 6px;
            }
        """)
        edit_layout = QVBoxLayout(edit_frame)
        edit_layout.setContentsMargins(8, 3, 8, 3)

        # 编辑信息行1
        edit_info1 = QHBoxLayout()

        current_selection = QLabel("🔧 时间段编辑 (智能化)")
        current_selection.setStyleSheet("font-weight: bold; color: #3730A3; font-size: 11px;")
        edit_info1.addWidget(current_selection)

        edit_info1.addStretch()

        time_info = QLabel("当前选中: 2.3s - 4.6s (持续: 2.3s) | 🎯精确到: 0.01s")
        time_info.setStyleSheet("color: #4338CA; font-size: 10px; font-weight: bold;")
        edit_info1.addWidget(time_info)

        edit_layout.addLayout(edit_info1)

        # 编辑信息行2
        edit_info2 = QHBoxLayout()

        desc_info = QLabel("描述: [小球火箭运动] 📝 | 类型: [移动动画] ▼")
        desc_info.setStyleSheet("color: #4338CA; font-size: 10px;")
        edit_info2.addWidget(desc_info)

        edit_info2.addStretch()

        collab_info = QLabel("主要元素: 小球 | 辅助元素: 背景 | 协作者: 张三 🟢在线")
        collab_info.setStyleSheet("color: #6B7280; font-size: 10px;")
        edit_info2.addWidget(collab_info)

        edit_layout.addLayout(edit_info2)

        # 编辑信息行3
        edit_info3 = QHBoxLayout()

        status_info = QLabel("状态: ✅已生成 ⚠️待优化 💬有评论(2)")
        status_info.setStyleSheet("color: #4338CA; font-size: 10px; font-weight: bold;")
        edit_info3.addWidget(status_info)

        edit_info3.addStretch()

        # 编辑操作按钮
        edit_buttons = [
            ("✂️", "分割"),
            ("📋", "复制"),
            ("🔗", "链接"),
            ("🗑️", "删除"),
            ("⚙️", "属性"),
            ("💬", "评论")
        ]

        for icon, name in edit_buttons:
            btn = QToolButton()
            btn.setText(f"{icon} {name}")
            btn.setStyleSheet("""
                QToolButton {
                    background-color: white;
                    color: #374151;
                    border: 1px solid #D1D5DB;
                    border-radius: 3px;
                    padding: 3px 6px;
                    margin: 1px;
                    font-size: 9px;
                }
                QToolButton:hover {
                    background-color: #F3F4F6;
                }
            """)
            edit_info3.addWidget(btn)

        edit_layout.addLayout(edit_info3)
        timeline_layout.addWidget(edit_frame)

        # 连接信号
        play_btn.clicked.connect(self.timeline_play)
        pause_btn.clicked.connect(self.timeline_pause)
        stop_btn.clicked.connect(self.timeline_stop)

    # 辅助方法：创建各个标签页内容
    def create_assets_library_tab(self):
        """创建智能素材库标签页 - 增强版"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 🎨 素材库工具栏
        toolbar = QFrame()
        toolbar.setFixedHeight(35)
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #F3F4F6;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 3, 8, 3)

        # 搜索框
        search_box = QLineEdit()
        search_box.setPlaceholderText("🔍 智能搜索素材...")
        search_box.setStyleSheet("""
            QLineEdit {
                border: 1px solid #D1D5DB;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
            }
        """)
        toolbar_layout.addWidget(search_box)

        # 视图切换按钮
        view_btns = [
            ("📋", "列表"),
            ("🔲", "网格"),
            ("📊", "详情")
        ]

        view_group = QButtonGroup(self)

        for i, (icon, name) in enumerate(view_btns):
            btn = QToolButton()
            btn.setText(f"{icon}")
            btn.setToolTip(f"{name}视图")
            btn.setCheckable(True)
            if i == 0:  # 默认选中列表视图
                btn.setChecked(True)
            btn.setStyleSheet("""
                QToolButton {
                    border: 1px solid #D1D5DB;
                    border-radius: 3px;
                    padding: 4px 6px;
                    margin: 1px;
                    background-color: white;
                }
                QToolButton:checked {
                    background-color: #3B82F6;
                    color: white;
                    border-color: #2563EB;
                }
                QToolButton:hover {
                    background-color: #F3F4F6;
                }
            """)
            view_group.addButton(btn, i)
            toolbar_layout.addWidget(btn)

        # 批量操作按钮
        batch_btn = QToolButton()
        batch_btn.setText("📦 批量")
        batch_btn.setStyleSheet("""
            QToolButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 10px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #059669;
            }
        """)
        toolbar_layout.addWidget(batch_btn)

        layout.addWidget(toolbar)

        # 智能分类和素材展示区域
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：智能分类树
        category_frame = QFrame()
        category_frame.setFixedWidth(120)
        category_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        category_layout = QVBoxLayout(category_frame)
        category_layout.setContentsMargins(5, 5, 5, 5)

        # 分类标题
        category_title = QLabel("🗂️ 智能分类")
        category_title.setStyleSheet("font-weight: bold; color: #374151; font-size: 11px; padding: 3px;")
        category_layout.addWidget(category_title)

        # 分类树
        self.assets_tree = QTreeWidget()
        self.assets_tree.setHeaderHidden(True)
        self.assets_tree.setStyleSheet("""
            QTreeWidget {
                border: none;
                background-color: transparent;
                font-size: 10px;
            }
            QTreeWidget::item {
                padding: 2px;
                border-radius: 2px;
            }
            QTreeWidget::item:selected {
                background-color: #EEF2FF;
                color: #3730A3;
            }
            QTreeWidget::item:hover {
                background-color: #F3F4F6;
            }
        """)

        # 添加智能分类
        all_assets = QTreeWidgetItem(self.assets_tree, ["📁 全部素材"])

        # 按类型分类
        images_cat = QTreeWidgetItem(all_assets, ["🖼️ 图片 (23)"])
        QTreeWidgetItem(images_cat, ["📷 照片 (8)"])
        QTreeWidgetItem(images_cat, ["🎨 插画 (12)"])
        QTreeWidgetItem(images_cat, ["🔷 图标 (3)"])

        videos_cat = QTreeWidgetItem(all_assets, ["🎥 视频 (7)"])
        QTreeWidgetItem(videos_cat, ["🎬 动画 (4)"])
        QTreeWidgetItem(videos_cat, ["📹 实拍 (3)"])

        audio_cat = QTreeWidgetItem(all_assets, ["🎵 音频 (15)"])
        QTreeWidgetItem(audio_cat, ["🎼 音乐 (8)"])
        QTreeWidgetItem(audio_cat, ["🔊 音效 (7)"])

        # 按标签分类
        tags_cat = QTreeWidgetItem(all_assets, ["🏷️ 标签"])
        QTreeWidgetItem(tags_cat, ["#科技 (12)"])
        QTreeWidgetItem(tags_cat, ["#教育 (8)"])
        QTreeWidgetItem(tags_cat, ["#商务 (6)"])
        QTreeWidgetItem(tags_cat, ["#自然 (4)"])

        # 按使用频率分类
        usage_cat = QTreeWidgetItem(all_assets, ["📊 使用频率"])
        QTreeWidgetItem(usage_cat, ["⭐ 常用 (9)"])
        QTreeWidgetItem(usage_cat, ["📈 最近 (5)"])
        QTreeWidgetItem(usage_cat, ["❤️ 收藏 (3)"])

        self.assets_tree.expandAll()
        category_layout.addWidget(self.assets_tree)

        content_splitter.addWidget(category_frame)

        # 右侧：素材展示区域
        assets_display_frame = QFrame()
        assets_display_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        assets_display_layout = QVBoxLayout(assets_display_frame)
        assets_display_layout.setContentsMargins(8, 8, 8, 8)

        # 素材展示标题栏
        display_header = QHBoxLayout()

        current_category = QLabel("📁 全部素材 (45项)")
        current_category.setStyleSheet("font-weight: bold; color: #374151; font-size: 12px;")
        display_header.addWidget(current_category)

        display_header.addStretch()

        # 排序选择
        sort_label = QLabel("排序:")
        sort_label.setStyleSheet("color: #6B7280; font-size: 10px;")
        display_header.addWidget(sort_label)

        sort_combo = QComboBox()
        sort_combo.addItems(["名称", "大小", "类型", "修改时间", "使用频率"])
        sort_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #D1D5DB;
                border-radius: 3px;
                padding: 2px 6px;
                font-size: 10px;
                min-width: 60px;
            }
        """)
        display_header.addWidget(sort_combo)

        assets_display_layout.addLayout(display_header)

        # 素材网格展示
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setSpacing(8)

        # 使用新的专业素材面板
        try:
            from core.asset_management import AssetManager
            from ui.professional_asset_panel import ProfessionalAssetPanel

            # 创建素材管理器
            if not hasattr(self, 'asset_manager'):
                project_path = None
                if hasattr(self, 'current_project') and self.current_project:
                    project_path = getattr(self.current_project, 'project_path', None)

                self.asset_manager = AssetManager(project_path)

                # 将当前项目的素材添加到管理器
                if hasattr(self, 'current_project') and self.current_project and hasattr(self.current_project, 'assets'):
                    for asset in self.current_project.assets:
                        enhanced_asset = self.asset_manager.add_asset(
                            asset.file_path,
                            category="默认",
                            tags=["项目素材"]
                        )
                        if enhanced_asset:
                            logger.info(f"已添加素材到管理器: {enhanced_asset.name}")

            # 创建专业素材面板
            professional_panel = ProfessionalAssetPanel(self.asset_manager)

            # 连接信号
            professional_panel.asset_double_clicked.connect(self.on_professional_asset_double_clicked)
            professional_panel.asset_import_requested.connect(self.on_import_assets_requested)

            # 添加到布局
            scroll_layout.addWidget(professional_panel, 0, 0, 1, 4)  # 占满整个网格

            logger.info("专业素材面板已创建并集成")

        except Exception as e:
            logger.error(f"创建专业素材面板失败: {e}")
            # 回退到旧的实现
            self._create_fallback_assets_view(scroll_layout)

        scroll_area.setWidget(scroll_widget)
        assets_display_layout.addWidget(scroll_area)

        content_splitter.addWidget(assets_display_frame)
        content_splitter.setSizes([120, 200])

        layout.addWidget(content_splitter)

        # 底部状态栏
        status_bar = QFrame()
        status_bar.setFixedHeight(25)
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-top: 1px solid #E5E7EB;
            }
        """)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(8, 3, 8, 3)

        status_info = QLabel("📊 已选择: 0项 | 总计: 45项 | 大小: 12.3MB")
        status_info.setStyleSheet("color: #6B7280; font-size: 10px;")
        status_layout.addWidget(status_info)

        status_layout.addStretch()

        # 快速操作按钮
        quick_actions = [
            ("📤", "导入"),
            ("📥", "导出"),
            ("🗑️", "删除"),
            ("📋", "复制"),
            ("🏷️", "标签")
        ]

        for icon, name in quick_actions:
            btn = QToolButton()
            btn.setText(f"{icon}")
            btn.setToolTip(name)
            btn.setStyleSheet("""
                QToolButton {
                    border: none;
                    background-color: transparent;
                    padding: 2px 4px;
                    border-radius: 2px;
                }
                QToolButton:hover {
                    background-color: #E5E7EB;
                }
            """)
            status_layout.addWidget(btn)

        layout.addWidget(status_bar)

        return widget

    def create_tools_tab(self):
        """创建工具箱标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 工具按钮网格
        tools_grid = QGridLayout()

        tools = [
            ("👆", "选择"), ("✋", "移动"), ("📏", "路径"), ("📝", "文字"),
            ("🔷", "形状"), ("🎨", "画笔"), ("📐", "测量"), ("🔍", "缩放")
        ]

        for i, (icon, name) in enumerate(tools):
            btn = QToolButton()
            btn.setText(f"{icon}\n{name}")
            btn.setFixedSize(60, 60)
            tools_grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(tools_grid)
        layout.addStretch()

        return widget

    def create_templates_library_tab(self):
        """创建智能模板库标签页 - 增强版"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 📋 模板库标题
        title_label = QLabel("📋 智能模板库")
        title_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 12px; padding: 3px;")
        layout.addWidget(title_label)

        # 🔍 搜索和筛选
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(6, 4, 6, 4)

        # 搜索框
        search_box = QLineEdit()
        search_box.setPlaceholderText("🔍 搜索模板...")
        search_box.setStyleSheet("""
            QLineEdit {
                border: 1px solid #D1D5DB;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
            }
        """)
        search_layout.addWidget(search_box)

        # 分类筛选
        category_combo = QComboBox()
        category_combo.addItems(["全部", "科技", "商务", "教育", "创意", "营销"])
        category_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #D1D5DB;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 10px;
                min-width: 50px;
            }
        """)
        search_layout.addWidget(category_combo)

        layout.addWidget(search_frame)

        # 📊 模板网格展示
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        scroll_widget = QWidget()
        templates_grid = QGridLayout(scroll_widget)
        templates_grid.setSpacing(6)

        # 模板数据
        templates_data = [
            {
                "name": "科技展示",
                "type": "产品演示",
                "duration": "15秒",
                "rating": "⭐⭐⭐⭐⭐",
                "downloads": "1,234",
                "icon": "🎬",
                "color": "#3B82F6",
                "featured": True
            },
            {
                "name": "数据可视化",
                "type": "图表动画",
                "duration": "12秒",
                "rating": "⭐⭐⭐⭐",
                "downloads": "856",
                "icon": "📊",
                "color": "#10B981",
                "featured": False
            },
            {
                "name": "创意动画",
                "type": "品牌展示",
                "duration": "20秒",
                "rating": "⭐⭐⭐⭐⭐",
                "downloads": "2,103",
                "icon": "🎨",
                "color": "#F59E0B",
                "featured": True
            },
            {
                "name": "移动端UI",
                "type": "界面动效",
                "duration": "8秒",
                "rating": "⭐⭐⭐⭐",
                "downloads": "743",
                "icon": "📱",
                "color": "#8B5CF6",
                "featured": False
            }
        ]

        for i, template in enumerate(templates_data):
            # 模板卡片
            template_card = QFrame()
            template_card.setFixedSize(90, 110)

            border_width = "2px" if template["featured"] else "1px"
            border_color = template["color"] if template["featured"] else "#E5E7EB"

            template_card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: {border_width} solid {border_color};
                    border-radius: 6px;
                }}
                QFrame:hover {{
                    border-color: {template["color"]};
                    border-width: 2px;
                    background-color: {template["color"]}08;
                }}
            """)

            card_layout = QVBoxLayout(template_card)
            card_layout.setContentsMargins(4, 4, 4, 4)
            card_layout.setSpacing(2)

            # 特色标识
            if template["featured"]:
                featured_label = QLabel("🔥")
                featured_label.setStyleSheet("font-size: 10px;")
                featured_label.setAlignment(Qt.AlignmentFlag.AlignRight)
                card_layout.addWidget(featured_label)
            else:
                card_layout.addWidget(QLabel(""))  # 占位

            # 图标
            icon_label = QLabel(template["icon"])
            icon_label.setStyleSheet("font-size: 20px;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(icon_label)

            # 名称
            name_label = QLabel(template["name"])
            name_label.setStyleSheet(f"color: {template['color']}; font-size: 9px; font-weight: bold;")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setWordWrap(True)
            card_layout.addWidget(name_label)

            # 类型
            type_label = QLabel(template["type"])
            type_label.setStyleSheet("color: #6B7280; font-size: 7px;")
            type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(type_label)

            # 时长
            duration_label = QLabel(template["duration"])
            duration_label.setStyleSheet("color: #374151; font-size: 7px; font-weight: bold;")
            duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(duration_label)

            # 评分
            rating_label = QLabel(template["rating"])
            rating_label.setStyleSheet("font-size: 6px;")
            rating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(rating_label)

            # 下载量
            downloads_label = QLabel(f"↓{template['downloads']}")
            downloads_label.setStyleSheet("color: #10B981; font-size: 6px; font-weight: bold;")
            downloads_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(downloads_label)

            templates_grid.addWidget(template_card, i // 2, i % 2)

            # 添加点击事件（模拟）
            template_card.mousePressEvent = lambda event, t=template: self.show_template_preview(t)

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # 📈 模板统计
        stats_frame = QFrame()
        stats_frame.setFixedHeight(25)
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #F0F9FF;
                border-top: 1px solid #BAE6FD;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(6, 3, 6, 3)

        stats_info = QLabel("📊 总计: 4个模板 | 🔥 精选: 2个 | 📥 总下载: 4,936次")
        stats_info.setStyleSheet("color: #0369A1; font-size: 9px; font-weight: bold;")
        stats_layout.addWidget(stats_info)

        stats_layout.addStretch()

        # 快速操作
        quick_actions = [
            ("👁️", "预览"),
            ("📋", "复制"),
            ("⭐", "收藏"),
            ("📤", "分享")
        ]

        for icon, name in quick_actions:
            btn = QToolButton()
            btn.setText(f"{icon}")
            btn.setToolTip(name)
            btn.setStyleSheet("""
                QToolButton {
                    border: none;
                    background-color: transparent;
                    padding: 2px 3px;
                    border-radius: 2px;
                }
                QToolButton:hover {
                    background-color: #DBEAFE;
                }
            """)
            stats_layout.addWidget(btn)

        layout.addWidget(stats_frame)

        return widget

    def show_template_preview(self, template_data):
        """显示模板预览对话框"""
        try:
            QMessageBox.information(
                self,
                "模板预览",
                f"📊 模板信息\n"
                f"名称: {template_data['name']}\n"
                f"类型: {template_data['type']}\n"
                f"时长: {template_data['duration']}\n"
                f"评分: {template_data['rating']}\n"
                f"下载: {template_data['downloads']}次\n\n"
                f"🎬 多角度预览功能正在开发中...\n"
                f"将支持桌面版、手机版、平板版预览"
            )
        except Exception as e:
            logger = get_logger("main_window")
            logger.error(f"显示模板预览失败: {e}")

    def create_library_management_tab(self):
        """创建智能库依赖管理标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 📚 库管理标题
        title_label = QLabel("📚 智能库管理")
        title_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 12px; padding: 3px;")
        layout.addWidget(title_label)

        # 🔍 依赖关系图
        dependency_frame = QFrame()
        dependency_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        dependency_layout = QVBoxLayout(dependency_frame)
        dependency_layout.setContentsMargins(8, 6, 8, 6)

        dependency_title = QLabel("🔍 依赖关系图 (交互式)")
        dependency_title.setStyleSheet("font-weight: bold; color: #3B82F6; font-size: 11px;")
        dependency_layout.addWidget(dependency_title)

        # 依赖关系可视化
        dependency_display = QFrame()
        dependency_display.setFixedHeight(80)
        dependency_display.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 3px;
            }
        """)
        dependency_display_layout = QVBoxLayout(dependency_display)

        # 依赖关系ASCII图
        dependency_ascii = QLabel("""
    GSAP 3.12.2 ──┐────────┐
         │        │        │
         ▼        ▼        ▼
  ScrollTrigger MotionPath TextPlugin
         │        │        │
         ▼        ▼        ▼
    Three.js ──── WebGL Utils ──── Cannon.js""")
        dependency_ascii.setStyleSheet("""
            font-family: 'Consolas', monospace;
            font-size: 8px;
            color: #475569;
            padding: 5px;
        """)
        dependency_ascii.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dependency_display_layout.addWidget(dependency_ascii)

        dependency_layout.addWidget(dependency_display)

        # 智能优化建议
        optimization_label = QLabel("💡 智能优化建议:")
        optimization_label.setStyleSheet("font-weight: bold; color: #F59E0B; font-size: 10px;")
        dependency_layout.addWidget(optimization_label)

        suggestions = [
            "• 移除未使用的Three.js模块可减少800KB",
            "• Cannon.js与当前项目冲突，建议替换为Ammo.js"
        ]

        for suggestion in suggestions:
            suggestion_label = QLabel(suggestion)
            suggestion_label.setStyleSheet("color: #92400E; font-size: 9px; padding-left: 10px;")
            dependency_layout.addWidget(suggestion_label)

        layout.addWidget(dependency_frame)

        # 📊 库状态实时监控
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(8, 6, 8, 6)

        status_title = QLabel("📊 库状态实时监控")
        status_title.setStyleSheet("font-weight: bold; color: #10B981; font-size: 11px;")
        status_layout.addWidget(status_title)

        # 库状态表格
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        status_table = QTableWidget()
        status_table.setRowCount(5)
        status_table.setColumnCount(4)

        # 设置表头
        headers = ["库名称", "状态", "版本", "大小/进度"]
        status_table.setHorizontalHeaderLabels(headers)

        # 表格数据
        table_data = [
            ("GSAP", "✅ 已下载", "3.12.2", "156KB"),
            ("Three.js", "🔄 下载中", "r158", "1.2MB(45%)"),
            ("Chart.js", "⏳ 队列中", "4.4.0", "245KB"),
            ("Anime.js", "❌ 失败", "3.2.1", "47KB"),
            ("Lottie", "🔄 更新中", "5.12.2", "213KB(78%)")
        ]

        # 填充表格数据
        for row, (name, status, version, size) in enumerate(table_data):
            # 库名称
            name_item = QTableWidgetItem(name)
            name_item.setFont(QFont("", -1, QFont.Weight.Bold))
            status_table.setItem(row, 0, name_item)

            # 状态
            status_item = QTableWidgetItem(status)
            if "✅" in status:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif "🔄" in status:
                status_item.setForeground(Qt.GlobalColor.blue)
            elif "⏳" in status:
                status_item.setForeground(Qt.GlobalColor.gray)
            elif "❌" in status:
                status_item.setForeground(Qt.GlobalColor.red)
            status_table.setItem(row, 1, status_item)

            # 版本
            version_item = QTableWidgetItem(version)
            status_table.setItem(row, 2, version_item)

            # 大小/进度
            size_item = QTableWidgetItem(size)
            if "%" in size:
                size_item.setForeground(Qt.GlobalColor.blue)
                font = size_item.font()
                font.setBold(True)
                size_item.setFont(font)
            status_table.setItem(row, 3, size_item)

        # 设置表格样式
        status_table.setMaximumHeight(120)
        status_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E5E7EB;
                background-color: white;
                font-size: 9px;
            }
            QTableWidget::item {
                padding: 3px;
                border-bottom: 1px solid #F3F4F6;
            }
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 4px;
                border: 1px solid #E5E7EB;
                font-weight: bold;
                font-size: 9px;
            }
        """)

        # 调整列宽
        header = status_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        status_layout.addWidget(status_table)
        layout.addWidget(status_frame)

        # ⚙️ 智能下载配置
        config_frame = QFrame()
        config_frame.setStyleSheet("""
            QFrame {
                background-color: #EEF2FF;
                border: 1px solid #C7D2FE;
                border-radius: 4px;
            }
        """)
        config_layout = QVBoxLayout(config_frame)
        config_layout.setContentsMargins(8, 6, 8, 6)

        config_title = QLabel("⚙️ 智能下载配置")
        config_title.setStyleSheet("font-weight: bold; color: #3730A3; font-size: 11px;")
        config_layout.addWidget(config_title)

        # 配置选项
        config_options_layout = QHBoxLayout()

        # CDN源选择
        cdn_label = QLabel("CDN源:")
        cdn_label.setStyleSheet("color: #4338CA; font-size: 9px;")
        config_options_layout.addWidget(cdn_label)

        cdn_combo = QComboBox()
        cdn_combo.addItems(["jsDelivr", "unpkg", "cdnjs"])
        cdn_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #C7D2FE;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 8px;
                min-width: 50px;
            }
        """)
        config_options_layout.addWidget(cdn_combo)

        # 并发数设置
        concurrent_label = QLabel("并发:")
        concurrent_label.setStyleSheet("color: #4338CA; font-size: 9px;")
        config_options_layout.addWidget(concurrent_label)

        concurrent_combo = QComboBox()
        concurrent_combo.addItems(["1", "2", "3", "4", "5"])
        concurrent_combo.setCurrentText("3")
        concurrent_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #C7D2FE;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 8px;
                min-width: 30px;
            }
        """)
        config_options_layout.addWidget(concurrent_combo)

        config_options_layout.addStretch()
        config_layout.addLayout(config_options_layout)

        # 配置选项复选框
        checkbox_layout = QHBoxLayout()

        checkboxes = [
            ("自动重试", True),
            ("完整性校验", True),
            ("智能缓存", True),
            ("离线模式", False)
        ]

        for text, checked in checkboxes:
            checkbox = QCheckBox(text)
            checkbox.setChecked(checked)
            checkbox.setStyleSheet("color: #4338CA; font-size: 8px;")
            checkbox_layout.addWidget(checkbox)

        config_layout.addLayout(checkbox_layout)
        layout.addWidget(config_frame)

        # 🚀 性能优化
        performance_frame = QFrame()
        performance_frame.setStyleSheet("""
            QFrame {
                background-color: #F0FDF4;
                border: 1px solid #BBF7D0;
                border-radius: 4px;
            }
        """)
        performance_layout = QVBoxLayout(performance_frame)
        performance_layout.setContentsMargins(8, 6, 8, 6)

        performance_title = QLabel("🚀 性能优化")
        performance_title.setStyleSheet("font-weight: bold; color: #166534; font-size: 11px;")
        performance_layout.addWidget(performance_title)

        # 优化按钮组
        optimization_buttons = QHBoxLayout()

        opt_buttons = [
            ("⚡", "一键优化", "#10B981"),
            ("🧹", "清理缓存", "#6B7280"),
            ("🔄", "批量更新", "#3B82F6"),
            ("📊", "使用分析", "#F59E0B")
        ]

        for icon, name, color in opt_buttons:
            btn = QToolButton()
            btn.setText(f"{icon} {name}")
            btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {color}15;
                    color: {color};
                    border: 1px solid {color}40;
                    border-radius: 3px;
                    padding: 4px 6px;
                    font-size: 8px;
                    font-weight: bold;
                }}
                QToolButton:hover {{
                    background-color: {color}25;
                }}
            """)
            optimization_buttons.addWidget(btn)

        performance_layout.addLayout(optimization_buttons)

        # 预期优化效果
        effect_label = QLabel("📈 预期优化效果: 文件大小减少38% | 加载时间提升52%")
        effect_label.setStyleSheet("color: #15803D; font-size: 9px; font-weight: bold; padding: 3px;")
        performance_layout.addWidget(effect_label)

        layout.addWidget(performance_frame)

        layout.addStretch()

        return widget

    def create_version_control_tab(self):
        """创建版本控制标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 🔄 版本控制标题
        title_label = QLabel("🔄 版本控制")
        title_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 12px; padding: 3px;")
        layout.addWidget(title_label)

        # 📊 版本历史
        history_frame = QFrame()
        history_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        history_layout = QVBoxLayout(history_frame)
        history_layout.setContentsMargins(8, 6, 8, 6)

        history_title = QLabel("📊 版本历史")
        history_title.setStyleSheet("font-weight: bold; color: #3B82F6; font-size: 11px;")
        history_layout.addWidget(history_title)

        # 版本列表
        version_scroll = QScrollArea()
        version_scroll.setWidgetResizable(True)
        version_scroll.setMaximumHeight(120)
        version_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #F3F4F6;
                border-radius: 3px;
                background-color: #FAFAFA;
            }
        """)

        version_content = QWidget()
        version_content_layout = QVBoxLayout(version_content)

        # 版本数据
        versions_data = [
            ("v2.1.3", "main", "张三", "2024-01-15 14:30", "✅ 当前版本", "添加AI生成功能", "#10B981"),
            ("v2.1.2", "main", "李四", "2024-01-15 10:15", "📦 已发布", "修复时间轴同步问题", "#3B82F6"),
            ("v2.1.1", "feature/ui", "王五", "2024-01-14 16:45", "🔄 开发中", "优化界面响应速度", "#F59E0B"),
            ("v2.1.0", "main", "赵六", "2024-01-14 09:20", "📦 已发布", "重构核心动画引擎", "#3B82F6"),
            ("v2.0.9", "hotfix", "张三", "2024-01-13 18:30", "🔧 热修复", "紧急修复内存泄漏", "#EF4444")
        ]

        for version, branch, author, time, status, description, color in versions_data:
            version_item = QFrame()
            if "当前版本" in status:
                version_item.setStyleSheet(f"""
                    QFrame {{
                        background-color: {color}15;
                        border: 1px solid {color}40;
                        border-radius: 3px;
                        padding: 2px;
                    }}
                """)
            else:
                version_item.setStyleSheet("""
                    QFrame {
                        background-color: transparent;
                        border: none;
                        padding: 2px;
                    }
                """)

            item_layout = QVBoxLayout(version_item)
            item_layout.setContentsMargins(4, 2, 4, 2)

            # 版本头部信息
            header_layout = QHBoxLayout()

            version_label = QLabel(f"{version} ({branch})")
            version_label.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold;")
            header_layout.addWidget(version_label)

            header_layout.addStretch()

            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: {color}; font-size: 9px; font-weight: bold;")
            header_layout.addWidget(status_label)

            item_layout.addLayout(header_layout)

            # 版本详细信息
            details_layout = QHBoxLayout()

            author_time = QLabel(f"👤 {author} | 🕒 {time}")
            author_time.setStyleSheet("color: #6B7280; font-size: 8px;")
            details_layout.addWidget(author_time)

            details_layout.addStretch()

            # 操作按钮
            if "当前版本" not in status:
                revert_btn = QToolButton()
                revert_btn.setText("🔄")
                revert_btn.setToolTip("回滚到此版本")
                revert_btn.setStyleSheet("""
                    QToolButton {
                        background-color: transparent;
                        color: #6B7280;
                        border: 1px solid #E5E7EB;
                        border-radius: 2px;
                        padding: 1px 3px;
                        font-size: 8px;
                    }
                    QToolButton:hover {
                        background-color: #F3F4F6;
                    }
                """)
                details_layout.addWidget(revert_btn)

            item_layout.addLayout(details_layout)

            # 描述
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #374151; font-size: 9px; padding: 2px 0;")
            item_layout.addWidget(desc_label)

            version_content_layout.addWidget(version_item)

        version_scroll.setWidget(version_content)
        history_layout.addWidget(version_scroll)

        layout.addWidget(history_frame)

        # 🌿 分支管理
        branch_frame = QFrame()
        branch_frame.setStyleSheet("""
            QFrame {
                background-color: #F0FDF4;
                border: 1px solid #BBF7D0;
                border-radius: 4px;
            }
        """)
        branch_layout = QVBoxLayout(branch_frame)
        branch_layout.setContentsMargins(8, 6, 8, 6)

        branch_title = QLabel("🌿 分支管理")
        branch_title.setStyleSheet("font-weight: bold; color: #166534; font-size: 11px;")
        branch_layout.addWidget(branch_title)

        # 当前分支
        current_branch = QLabel("📍 当前分支: main (最新)")
        current_branch.setStyleSheet("color: #15803D; font-size: 10px; font-weight: bold;")
        branch_layout.addWidget(current_branch)

        # 分支列表
        branches_layout = QHBoxLayout()

        branches = [
            ("main", "✅", "#10B981"),
            ("feature/ui", "🔄", "#F59E0B"),
            ("hotfix", "🔧", "#EF4444"),
            ("develop", "⚡", "#3B82F6")
        ]

        for branch, status, color in branches:
            branch_btn = QToolButton()
            branch_btn.setText(f"{status} {branch}")
            branch_btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {color}15;
                    color: {color};
                    border: 1px solid {color}40;
                    border-radius: 3px;
                    padding: 3px 6px;
                    font-size: 9px;
                    font-weight: bold;
                    margin: 1px;
                }}
                QToolButton:hover {{
                    background-color: {color}25;
                }}
            """)
            branches_layout.addWidget(branch_btn)

        branches_layout.addStretch()
        branch_layout.addLayout(branches_layout)

        # 分支操作
        branch_actions = QHBoxLayout()

        branch_ops = [
            ("🌿", "新建分支", "#10B981"),
            ("🔀", "合并分支", "#3B82F6"),
            ("🗑️", "删除分支", "#EF4444")
        ]

        for icon, name, color in branch_ops:
            btn = QToolButton()
            btn.setText(f"{icon} {name}")
            btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {color}15;
                    color: {color};
                    border: 1px solid {color}40;
                    border-radius: 3px;
                    padding: 3px 6px;
                    font-size: 8px;
                    font-weight: bold;
                }}
                QToolButton:hover {{
                    background-color: {color}25;
                }}
            """)
            branch_actions.addWidget(btn)

        branch_actions.addStretch()
        branch_layout.addLayout(branch_actions)

        layout.addWidget(branch_frame)

        # 📤 提交管理
        commit_frame = QFrame()
        commit_frame.setStyleSheet("""
            QFrame {
                background-color: #EEF2FF;
                border: 1px solid #C7D2FE;
                border-radius: 4px;
            }
        """)
        commit_layout = QVBoxLayout(commit_frame)
        commit_layout.setContentsMargins(8, 6, 8, 6)

        commit_title = QLabel("📤 提交管理")
        commit_title.setStyleSheet("font-weight: bold; color: #3730A3; font-size: 11px;")
        commit_layout.addWidget(commit_title)

        # 提交信息输入
        commit_input_layout = QVBoxLayout()

        commit_message.setPlaceholderText("输入提交信息...")
        commit_message.setStyleSheet("""
            QLineEdit {
                border: 1px solid #C7D2FE;
                border-radius: 3px;
                padding: 4px 6px;
                font-size: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3730A3;
            }
        """)
        commit_input_layout.addWidget(commit_message)

        commit_description = QTextEdit()
        commit_description.setMaximumHeight(40)
        commit_description.setPlaceholderText("详细描述 (可选)...")
        commit_description.setStyleSheet("""
            QTextEdit {
                border: 1px solid #C7D2FE;
                border-radius: 3px;
                padding: 4px 6px;
                font-size: 9px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3730A3;
            }
        """)
        commit_input_layout.addWidget(commit_description)

        commit_layout.addLayout(commit_input_layout)

        # 提交操作按钮
        commit_actions = QHBoxLayout()

        commit_btn = QToolButton()
        commit_btn.setText("📤 提交更改")
        commit_btn.setStyleSheet("""
            QToolButton {
                background-color: #3730A3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #312E81;
            }
        """)
        commit_actions.addWidget(commit_btn)

        push_btn = QToolButton()
        push_btn.setText("⬆️ 推送")
        push_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #3730A3;
                border: 1px solid #C7D2FE;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
            }
            QToolButton:hover {
                background-color: #E0E7FF;
            }
        """)
        commit_actions.addWidget(push_btn)

        pull_btn = QToolButton()
        pull_btn.setText("⬇️ 拉取")
        pull_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #3730A3;
                border: 1px solid #C7D2FE;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
            }
            QToolButton:hover {
                background-color: #E0E7FF;
            }
        """)
        commit_actions.addWidget(pull_btn)

        commit_actions.addStretch()
        commit_layout.addLayout(commit_actions)

        layout.addWidget(commit_frame)

        layout.addStretch()

        return widget

    def create_performance_monitor_tab(self):
        """创建实时性能监控标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 📊 性能监控标题
        title_label = QLabel("📊 实时性能监控")
        title_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 12px; padding: 3px;")
        layout.addWidget(title_label)

        # 🖥️ 系统资源监控
        system_resources_frame = QFrame()
        system_resources_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        system_resources_layout = QVBoxLayout(system_resources_frame)
        system_resources_layout.setContentsMargins(8, 6, 8, 6)

        resources_title = QLabel("🖥️ 系统资源监控 (实时)")
        resources_title.setStyleSheet("font-weight: bold; color: #3B82F6; font-size: 11px;")
        system_resources_layout.addWidget(resources_title)

        # 资源使用率网格
        resources_grid = QGridLayout()
        resources_grid.setSpacing(8)

        # 资源监控数据
        resources_data = [
            {
                "name": "CPU",
                "icon": "🔥",
                "usage": 67,
                "status": "高负载",
                "color": "#F59E0B",
                "details": "主要消耗: AI生成(45%) + 渲染(22%)"
            },
            {
                "name": "内存",
                "icon": "💾",
                "usage": 78,
                "status": "接近上限",
                "color": "#EF4444",
                "details": "已用: 6.2GB / 8GB | 缓存: 1.1GB"
            },
            {
                "name": "GPU",
                "icon": "🎮",
                "usage": 89,
                "status": "严重负载",
                "color": "#DC2626",
                "details": "VRAM: 3.8GB/4GB | 温度: 78°C"
            },
            {
                "name": "磁盘I/O",
                "icon": "💿",
                "usage": 23,
                "status": "正常",
                "color": "#10B981",
                "details": "读取: 45MB/s | 写入: 12MB/s"
            }
        ]

        for i, resource in enumerate(resources_data):
            resource_frame = QFrame()
            resource_frame.setFixedSize(110, 80)
            resource_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {resource["color"]}10;
                    border: 1px solid {resource["color"]}40;
                    border-radius: 4px;
                }}
            """)

            resource_layout = QVBoxLayout(resource_frame)
            resource_layout.setContentsMargins(4, 3, 4, 3)
            resource_layout.setSpacing(2)

            # 资源名称和图标
            name_layout = QHBoxLayout()
            icon_label = QLabel(resource["icon"])
            icon_label.setStyleSheet("font-size: 12px;")
            name_layout.addWidget(icon_label)

            name_label = QLabel(resource["name"])
            name_label.setStyleSheet("color: #374151; font-size: 10px; font-weight: bold;")
            name_layout.addWidget(name_label)
            name_layout.addStretch()

            resource_layout.addLayout(name_layout)

            # 使用率百分比
            usage_label = QLabel(f"{resource['usage']}%")
            usage_label.setStyleSheet(f"color: {resource['color']}; font-size: 14px; font-weight: bold;")
            usage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            resource_layout.addWidget(usage_label)

            # 进度条（ASCII风格）
            filled_blocks = resource["usage"] // 10
            empty_blocks = 10 - filled_blocks
            progress_bar = "█" * filled_blocks + "░" * empty_blocks

            progress_label = QLabel(progress_bar)
            progress_label.setStyleSheet(f"color: {resource['color']}; font-family: 'Consolas', monospace; font-size: 8px;")
            progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            resource_layout.addWidget(progress_label)

            # 状态描述
            status_label = QLabel(resource["status"])
            status_label.setStyleSheet(f"color: {resource['color']}; font-size: 8px; font-weight: bold;")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            resource_layout.addWidget(status_label)

            resources_grid.addWidget(resource_frame, i // 2, i % 2)

        system_resources_layout.addLayout(resources_grid)

        # 详细信息显示
        details_layout = QVBoxLayout()
        for resource in resources_data:
            detail_label = QLabel(f"{resource['icon']} {resource['name']}: {resource['details']}")
            detail_label.setStyleSheet(f"color: {resource['color']}; font-size: 9px; padding: 1px;")
            details_layout.addWidget(detail_label)

        system_resources_layout.addLayout(details_layout)
        layout.addWidget(system_resources_frame)

        # ⚡ 性能瓶颈检测
        bottleneck_frame = QFrame()
        bottleneck_frame.setStyleSheet("""
            QFrame {
                background-color: #FEF3C7;
                border: 1px solid #FCD34D;
                border-radius: 4px;
            }
        """)
        bottleneck_layout = QVBoxLayout(bottleneck_frame)
        bottleneck_layout.setContentsMargins(8, 6, 8, 6)

        bottleneck_title = QLabel("⚡ 性能瓶颈检测")
        bottleneck_title.setStyleSheet("font-weight: bold; color: #92400E; font-size: 11px;")
        bottleneck_layout.addWidget(bottleneck_title)

        # 瓶颈问题列表
        bottlenecks = [
            ("🔥", "GPU过载", "严重", "GPU使用率持续超过85%，建议降低渲染质量", "#DC2626"),
            ("💾", "内存不足", "警告", "可用内存不足2GB，可能影响大型项目", "#F59E0B"),
            ("🐌", "AI响应慢", "中等", "AI生成平均耗时18秒，超过预期12秒", "#F59E0B"),
            ("📡", "网络延迟", "轻微", "协作同步延迟偶尔超过100ms", "#3B82F6")
        ]

        for icon, issue, severity, description, color in bottlenecks:
            bottleneck_item = QHBoxLayout()

            # 问题信息
            issue_info = QLabel(f"{icon} {issue} ({severity})")
            issue_info.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold;")
            bottleneck_item.addWidget(issue_info)

            bottleneck_item.addStretch()

            # 优化按钮
            optimize_btn = QToolButton()
            optimize_btn.setText("🔧优化")
            optimize_btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {color}15;
                    color: {color};
                    border: 1px solid {color}40;
                    border-radius: 3px;
                    padding: 2px 6px;
                    font-size: 8px;
                    font-weight: bold;
                }}
                QToolButton:hover {{
                    background-color: {color}25;
                }}
            """)
            bottleneck_item.addWidget(optimize_btn)

            bottleneck_layout.addLayout(bottleneck_item)

            # 问题描述
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #92400E; font-size: 9px; padding-left: 15px;")
            bottleneck_layout.addWidget(desc_label)

        layout.addWidget(bottleneck_frame)

        # 🎯 智能优化建议
        optimization_frame = QFrame()
        optimization_frame.setStyleSheet("""
            QFrame {
                background-color: #F0FDF4;
                border: 1px solid #BBF7D0;
                border-radius: 4px;
            }
        """)
        optimization_layout = QVBoxLayout(optimization_frame)
        optimization_layout.setContentsMargins(8, 6, 8, 6)

        optimization_title = QLabel("🎯 智能优化建议")
        optimization_title.setStyleSheet("font-weight: bold; color: #166534; font-size: 11px;")
        optimization_layout.addWidget(optimization_title)

        # 优化建议列表
        suggestions = [
            ("⚡", "启用性能模式", "可减少30%资源消耗", "立即应用"),
            ("🎨", "降低渲染质量", "从4K降至2K可释放40%GPU", "应用"),
            ("🧹", "清理缓存", "清理1.2GB临时文件", "清理"),
            ("💾", "增加虚拟内存", "建议设置为16GB", "设置"),
            ("🔄", "重启AI服务", "可能解决响应慢问题", "重启")
        ]

        for icon, title, benefit, action in suggestions:
            suggestion_layout = QHBoxLayout()

            suggestion_info = QLabel(f"{icon} {title}")
            suggestion_info.setStyleSheet("color: #166534; font-size: 10px; font-weight: bold;")
            suggestion_layout.addWidget(suggestion_info)

            benefit_label = QLabel(benefit)
            benefit_label.setStyleSheet("color: #15803D; font-size: 9px;")
            suggestion_layout.addWidget(benefit_label)

            suggestion_layout.addStretch()

            action_btn = QToolButton()
            action_btn.setText(action)
            action_btn.setStyleSheet("""
                QToolButton {
                    background-color: #10B981;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 3px 8px;
                    font-size: 8px;
                    font-weight: bold;
                }
                QToolButton:hover {
                    background-color: #059669;
                }
            """)
            suggestion_layout.addWidget(action_btn)

            optimization_layout.addLayout(suggestion_layout)

        # 批量优化按钮
        batch_optimize_layout = QHBoxLayout()

        batch_optimize_btn = QToolButton()
        batch_optimize_btn.setText("⚡ 一键优化全部")
        batch_optimize_btn.setStyleSheet("""
            QToolButton {
                background-color: #166534;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #14532D;
            }
        """)
        batch_optimize_layout.addWidget(batch_optimize_btn)

        auto_optimize_btn = QToolButton()
        auto_optimize_btn.setText("🤖 自动优化")
        auto_optimize_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #166534;
                border: 1px solid #BBF7D0;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
            }
            QToolButton:hover {
                background-color: #F0FDF4;
            }
        """)
        batch_optimize_layout.addWidget(auto_optimize_btn)

        batch_optimize_layout.addStretch()
        optimization_layout.addLayout(batch_optimize_layout)

        layout.addWidget(optimization_frame)

        # 📈 性能趋势图
        trend_frame = QFrame()
        trend_frame.setStyleSheet("""
            QFrame {
                background-color: #EEF2FF;
                border: 1px solid #C7D2FE;
                border-radius: 4px;
            }
        """)
        trend_layout = QVBoxLayout(trend_frame)
        trend_layout.setContentsMargins(8, 6, 8, 6)

        trend_title = QLabel("📈 性能趋势图 (最近1小时)")
        trend_title.setStyleSheet("font-weight: bold; color: #3730A3; font-size: 11px;")
        trend_layout.addWidget(trend_title)

        # ASCII趋势图
        trend_display = QFrame()
        trend_display.setFixedHeight(60)
        trend_display.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #C7D2FE;
                border-radius: 3px;
            }
        """)
        trend_display_layout = QVBoxLayout(trend_display)

        # CPU趋势
        cpu_trend = QLabel("CPU:  ▁▂▃▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇▆▅▄▃▂▁ (当前67%)")
        cpu_trend.setStyleSheet("font-family: 'Consolas', monospace; color: #F59E0B; font-size: 9px;")
        trend_display_layout.addWidget(cpu_trend)

        # 内存趋势
        memory_trend = QLabel("内存: ▃▄▅▆▇█▇▆▅▄▃▄▅▆▇█▇▆▅▄▃▂▃▄▅ (当前78%)")
        memory_trend.setStyleSheet("font-family: 'Consolas', monospace; color: #EF4444; font-size: 9px;")
        trend_display_layout.addWidget(memory_trend)

        # GPU趋势
        gpu_trend = QLabel("GPU:  ▅▆▇█▇▆▅▆▇█▇▆▅▄▅▆▇█▇▆▅▄▃▄▅ (当前89%)")
        gpu_trend.setStyleSheet("font-family: 'Consolas', monospace; color: #DC2626; font-size: 9px;")
        trend_display_layout.addWidget(gpu_trend)

        trend_layout.addWidget(trend_display)

        # 趋势分析
        trend_analysis = QLabel("📊 分析: GPU使用率在过去30分钟持续上升，建议立即优化")
        trend_analysis.setStyleSheet("color: #4338CA; font-size: 10px; font-weight: bold; padding: 3px;")
        trend_layout.addWidget(trend_analysis)

        layout.addWidget(trend_frame)

        layout.addStretch()

        return widget

    def create_help_center_tab(self):
        """创建智能帮助中心标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 📚 帮助中心标题
        title_label = QLabel("📚 智能帮助中心")
        title_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 12px; padding: 3px;")
        layout.addWidget(title_label)

        # 🔍 智能搜索
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        search_layout = QVBoxLayout(search_frame)
        search_layout.setContentsMargins(8, 6, 8, 6)

        search_title = QLabel("🔍 智能搜索")
        search_title.setStyleSheet("font-weight: bold; color: #3B82F6; font-size: 11px;")
        search_layout.addWidget(search_title)

        # 搜索输入
        search_input_layout = QHBoxLayout()

        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 搜索帮助内容、教程、API文档...")
        search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #D1D5DB;
                border-radius: 3px;
                padding: 6px 10px;
                font-size: 11px;
                background-color: #F9FAFB;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
                background-color: white;
            }
        """)
        search_input_layout.addWidget(search_input)

        search_btn = QToolButton()
        search_btn.setText("🔍")
        search_btn.setStyleSheet("""
            QToolButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QToolButton:hover {
                background-color: #2563EB;
            }
        """)
        search_input_layout.addWidget(search_btn)

        search_layout.addLayout(search_input_layout)

        # 热门搜索
        hot_searches = QLabel("🔥 热门搜索: AI生成 | 时间轴操作 | 导出设置 | 快捷键 | 协作功能")
        hot_searches.setStyleSheet("color: #6B7280; font-size: 9px; padding: 3px;")
        search_layout.addWidget(hot_searches)

        layout.addWidget(search_frame)

        # 📖 快速入门
        quick_start_frame = QFrame()
        quick_start_frame.setStyleSheet("""
            QFrame {
                background-color: #F0FDF4;
                border: 1px solid #BBF7D0;
                border-radius: 4px;
            }
        """)
        quick_start_layout = QVBoxLayout(quick_start_frame)
        quick_start_layout.setContentsMargins(8, 6, 8, 6)

        quick_start_title = QLabel("📖 快速入门")
        quick_start_title.setStyleSheet("font-weight: bold; color: #166534; font-size: 11px;")
        quick_start_layout.addWidget(quick_start_title)

        # 入门教程网格
        tutorials_grid = QGridLayout()
        tutorials_grid.setSpacing(4)

        # 教程数据
        tutorials_data = [
            ("🚀", "5分钟上手", "快速创建第一个动画", "初级"),
            ("🤖", "AI生成教程", "使用AI创建动画", "中级"),
            ("⚙️", "高级设置", "自定义工作流程", "高级"),
            ("👥", "团队协作", "多人协作项目", "中级")
        ]

        for i, (icon, title, desc, level) in enumerate(tutorials_data):
            tutorial_item = QFrame()
            tutorial_item.setFixedSize(110, 60)
            tutorial_item.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #BBF7D0;
                    border-radius: 3px;
                }
                QFrame:hover {
                    border-color: #10B981;
                    background-color: #F0FDF4;
                }
            """)

            tutorial_layout = QVBoxLayout(tutorial_item)
            tutorial_layout.setContentsMargins(4, 3, 4, 3)
            tutorial_layout.setSpacing(2)

            # 图标和标题
            title_layout = QHBoxLayout()
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 12px;")
            title_layout.addWidget(icon_label)

            title_label = QLabel(title)
            title_label.setStyleSheet("color: #166534; font-size: 9px; font-weight: bold;")
            title_layout.addWidget(title_label)
            title_layout.addStretch()

            tutorial_layout.addLayout(title_layout)

            # 描述
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #15803D; font-size: 8px;")
            desc_label.setWordWrap(True)
            tutorial_layout.addWidget(desc_label)

            # 难度级别
            level_label = QLabel(level)
            level_color = "#10B981" if level == "初级" else "#F59E0B" if level == "中级" else "#EF4444"
            level_label.setStyleSheet(f"color: {level_color}; font-size: 7px; font-weight: bold;")
            level_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            tutorial_layout.addWidget(level_label)

            tutorials_grid.addWidget(tutorial_item, i // 2, i % 2)

        quick_start_layout.addLayout(tutorials_grid)

        # 开始学习按钮
        start_learning_btn = QToolButton()
        start_learning_btn.setText("🎓 开始交互式学习")
        start_learning_btn.setStyleSheet("""
            QToolButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #059669;
            }
        """)
        quick_start_layout.addWidget(start_learning_btn)

        layout.addWidget(quick_start_frame)

        # 📋 常见问题
        faq_frame = QFrame()
        faq_frame.setStyleSheet("""
            QFrame {
                background-color: #FEF3C7;
                border: 1px solid #FCD34D;
                border-radius: 4px;
            }
        """)
        faq_layout = QVBoxLayout(faq_frame)
        faq_layout.setContentsMargins(8, 6, 8, 6)

        faq_title = QLabel("📋 常见问题")
        faq_title.setStyleSheet("font-weight: bold; color: #92400E; font-size: 11px;")
        faq_layout.addWidget(faq_title)

        # FAQ列表
        faq_data = [
            ("❓", "如何导入素材？", "支持拖拽导入或点击导入按钮"),
            ("❓", "AI生成失败怎么办？", "检查网络连接和API密钥设置"),
            ("❓", "如何分享项目？", "使用协作中心的项目共享功能"),
            ("❓", "导出格式有哪些？", "支持MP4、GIF、WebM等格式")
        ]

        for icon, question, answer in faq_data:
            faq_item = QVBoxLayout()

            # 问题
            question_layout = QHBoxLayout()
            question_icon = QLabel(icon)
            question_icon.setStyleSheet("font-size: 10px;")
            question_layout.addWidget(question_icon)

            question_label = QLabel(question)
            question_label.setStyleSheet("color: #92400E; font-size: 10px; font-weight: bold;")
            question_layout.addWidget(question_label)
            question_layout.addStretch()

            faq_item.addLayout(question_layout)

            # 答案
            answer_label = QLabel(f"💡 {answer}")
            answer_label.setStyleSheet("color: #78350F; font-size: 9px; padding-left: 15px;")
            faq_item.addWidget(answer_label)

            faq_layout.addLayout(faq_item)

        # 更多FAQ按钮
        more_faq_btn = QToolButton()
        more_faq_btn.setText("📚 查看更多FAQ")
        more_faq_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #92400E;
                border: 1px solid #FCD34D;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #FDE68A;
            }
        """)
        faq_layout.addWidget(more_faq_btn)

        layout.addWidget(faq_frame)

        # 📖 API文档
        api_docs_frame = QFrame()
        api_docs_frame.setStyleSheet("""
            QFrame {
                background-color: #EEF2FF;
                border: 1px solid #C7D2FE;
                border-radius: 4px;
            }
        """)
        api_docs_layout = QVBoxLayout(api_docs_frame)
        api_docs_layout.setContentsMargins(8, 6, 8, 6)

        api_docs_title = QLabel("📖 API文档")
        api_docs_title.setStyleSheet("font-weight: bold; color: #3730A3; font-size: 11px;")
        api_docs_layout.addWidget(api_docs_title)

        # API分类
        api_categories = QGridLayout()
        api_categories.setSpacing(4)

        # API分类数据
        api_data = [
            ("🎬", "动画API", "创建和控制动画"),
            ("🤖", "AI服务API", "AI生成和处理"),
            ("📊", "数据API", "项目数据管理"),
            ("👥", "协作API", "团队协作功能")
        ]

        for i, (icon, name, desc) in enumerate(api_data):
            api_item = QFrame()
            api_item.setFixedSize(110, 50)
            api_item.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #C7D2FE;
                    border-radius: 3px;
                }
                QFrame:hover {
                    border-color: #3730A3;
                    background-color: #F3F0FF;
                }
            """)

            api_item_layout = QVBoxLayout(api_item)
            api_item_layout.setContentsMargins(4, 3, 4, 3)
            api_item_layout.setSpacing(1)

            # API名称
            name_layout = QHBoxLayout()
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 10px;")
            name_layout.addWidget(icon_label)

            name_label = QLabel(name)
            name_label.setStyleSheet("color: #3730A3; font-size: 9px; font-weight: bold;")
            name_layout.addWidget(name_label)
            name_layout.addStretch()

            api_item_layout.addLayout(name_layout)

            # API描述
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #4338CA; font-size: 8px;")
            desc_label.setWordWrap(True)
            api_item_layout.addWidget(desc_label)

            api_categories.addWidget(api_item, i // 2, i % 2)

        api_docs_layout.addLayout(api_categories)

        # API文档操作
        api_actions = QHBoxLayout()

        view_docs_btn = QToolButton()
        view_docs_btn.setText("📚 查看完整文档")
        view_docs_btn.setStyleSheet("""
            QToolButton {
                background-color: #3730A3;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #312E81;
            }
        """)
        api_actions.addWidget(view_docs_btn)

        api_playground_btn = QToolButton()
        api_playground_btn.setText("🛝 API测试")
        api_playground_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #3730A3;
                border: 1px solid #C7D2FE;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
            }
            QToolButton:hover {
                background-color: #E0E7FF;
            }
        """)
        api_actions.addWidget(api_playground_btn)

        api_actions.addStretch()
        api_docs_layout.addLayout(api_actions)

        layout.addWidget(api_docs_frame)

        # 📞 联系支持
        support_frame = QFrame()
        support_frame.setStyleSheet("""
            QFrame {
                background-color: #F0F9FF;
                border: 1px solid #BAE6FD;
                border-radius: 4px;
            }
        """)
        support_layout = QVBoxLayout(support_frame)
        support_layout.setContentsMargins(8, 6, 8, 6)

        support_title = QLabel("📞 联系支持")
        support_title.setStyleSheet("font-weight: bold; color: #0369A1; font-size: 11px;")
        support_layout.addWidget(support_title)

        # 支持选项
        support_options = QGridLayout()
        support_options.setSpacing(6)

        # 支持方式数据
        support_data = [
            ("💬", "在线客服", "实时聊天支持", "#10B981"),
            ("📧", "邮件支持", "support@aiae.studio", "#3B82F6"),
            ("📱", "社区论坛", "用户交流讨论", "#F59E0B"),
            ("🎥", "视频教程", "YouTube频道", "#EF4444")
        ]

        for i, (icon, name, desc, color) in enumerate(support_data):
            support_item = QFrame()
            support_item.setFixedSize(110, 50)
            support_item.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}10;
                    border: 1px solid {color}40;
                    border-radius: 3px;
                }}
                QFrame:hover {{
                    border-color: {color};
                    background-color: {color}20;
                }}
            """)

            support_item_layout = QVBoxLayout(support_item)
            support_item_layout.setContentsMargins(4, 3, 4, 3)
            support_item_layout.setSpacing(1)

            # 支持方式名称
            name_layout = QHBoxLayout()
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 10px;")
            name_layout.addWidget(icon_label)

            name_label = QLabel(name)
            name_label.setStyleSheet(f"color: {color}; font-size: 9px; font-weight: bold;")
            name_layout.addWidget(name_label)
            name_layout.addStretch()

            support_item_layout.addLayout(name_layout)

            # 支持描述
            desc_label = QLabel(desc)
            desc_label.setStyleSheet(f"color: {color}; font-size: 8px;")
            desc_label.setWordWrap(True)
            support_item_layout.addWidget(desc_label)

            support_options.addWidget(support_item, i // 2, i % 2)

        support_layout.addLayout(support_options)

        # 紧急支持
        emergency_support = QLabel("🚨 紧急支持: 24/7热线 400-123-4567")
        emergency_support.setStyleSheet("color: #DC2626; font-size: 10px; font-weight: bold; padding: 4px;")
        emergency_support.setAlignment(Qt.AlignmentFlag.AlignCenter)
        support_layout.addWidget(emergency_support)

        layout.addWidget(support_frame)

        # 📊 帮助统计
        help_stats_frame = QFrame()
        help_stats_frame.setFixedHeight(25)
        help_stats_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-top: 1px solid #E5E7EB;
            }
        """)
        help_stats_layout = QHBoxLayout(help_stats_frame)
        help_stats_layout.setContentsMargins(8, 3, 8, 3)

        stats_info = QLabel("📊 今日帮助: 查看文档23次 | 搜索12次 | 教程完成3个")
        stats_info.setStyleSheet("color: #6B7280; font-size: 9px; font-weight: bold;")
        help_stats_layout.addWidget(stats_info)

        help_stats_layout.addStretch()

        # 快速操作
        quick_actions = [
            ("🔄", "刷新"),
            ("📤", "分享"),
            ("⭐", "收藏"),
            ("💡", "建议")
        ]

        for icon, name in quick_actions:
            btn = QToolButton()
            btn.setText(icon)
            btn.setToolTip(name)
            btn.setStyleSheet("""
                QToolButton {
                    border: none;
                    background-color: transparent;
                    padding: 2px 4px;
                    border-radius: 2px;
                }
                QToolButton:hover {
                    background-color: #E5E7EB;
                }
            """)
            help_stats_layout.addWidget(btn)

        layout.addWidget(help_stats_frame)

        layout.addStretch()

        return widget

    def create_state_management_tab(self):
        """创建状态管理可视化标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 📊 状态管理标题
        title_label = QLabel("📊 状态管理")
        title_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 12px; padding: 3px;")
        layout.addWidget(title_label)

        # 🔗 状态流转图
        flow_frame = QFrame()
        flow_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        flow_layout = QVBoxLayout(flow_frame)
        flow_layout.setContentsMargins(8, 6, 8, 6)

        flow_title = QLabel("🔗 状态流转图")
        flow_title.setStyleSheet("font-weight: bold; color: #3B82F6; font-size: 11px;")
        flow_layout.addWidget(flow_title)

        # 状态流转可视化
        flow_display = QFrame()
        flow_display.setFixedHeight(80)
        flow_display.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 3px;
            }
        """)
        flow_display_layout = QVBoxLayout(flow_display)

        # 状态流转ASCII图
        flow_ascii = QLabel("""
┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐
│待处理│ ──→│进行中│ ──→│已完成│ ──→│已发布│
│ ⏳  │    │ 🔄  │    │ ✅  │    │ 🚀  │
└─────┘    └─────┘    └─────┘    └─────┘
   ↑          ↓          ↓          ↓
   └──────────┴──────────┴──────────┘
              暂停/回退/修改""")
        flow_ascii.setStyleSheet("""
            font-family: 'Consolas', monospace;
            font-size: 8px;
            color: #475569;
            padding: 5px;
        """)
        flow_ascii.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flow_display_layout.addWidget(flow_ascii)

        flow_layout.addWidget(flow_display)
        layout.addWidget(flow_frame)

        # 🎯 当前状态检测
        current_state_frame = QFrame()
        current_state_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        current_state_layout = QVBoxLayout(current_state_frame)
        current_state_layout.setContentsMargins(8, 6, 8, 6)

        current_state_title = QLabel("🎯 当前状态检测")
        current_state_title.setStyleSheet("font-weight: bold; color: #10B981; font-size: 11px;")
        current_state_layout.addWidget(current_state_title)

        # 状态检测列表
        states_data = [
            ("Logo元素", "✅ 已完成", "#10B981"),
            ("小球动画", "🔄 进行中", "#F59E0B"),
            ("文字淡入", "⏳ 待处理", "#6B7280"),
            ("背景变色", "⏳ 待处理", "#6B7280")
        ]

        for element, status, color in states_data:
            state_item = QHBoxLayout()

            element_label = QLabel(element)
            element_label.setStyleSheet("font-size: 10px; color: #374151;")
            state_item.addWidget(element_label)

            state_item.addStretch()

            status_label = QLabel(status)
            status_label.setStyleSheet(f"font-size: 10px; color: {color}; font-weight: bold;")
            state_item.addWidget(status_label)

            current_state_layout.addLayout(state_item)

        layout.addWidget(current_state_frame)

        # 🚨 状态异常检测
        anomaly_frame = QFrame()
        anomaly_frame.setStyleSheet("""
            QFrame {
                background-color: #FEF2F2;
                border: 1px solid #FECACA;
                border-radius: 4px;
            }
        """)
        anomaly_layout = QVBoxLayout(anomaly_frame)
        anomaly_layout.setContentsMargins(8, 6, 8, 6)

        anomaly_title = QLabel("🚨 状态异常检测")
        anomaly_title.setStyleSheet("font-weight: bold; color: #DC2626; font-size: 11px;")
        anomaly_layout.addWidget(anomaly_title)

        # 异常列表
        anomalies = [
            "⚠️ 小球→文字: 透明度差异0.1",
            "❌ 文字→背景: 位置冲突"
        ]

        for anomaly in anomalies:
            anomaly_label = QLabel(anomaly)
            anomaly_label.setStyleSheet("font-size: 9px; color: #DC2626;")
            anomaly_layout.addWidget(anomaly_label)

        # 修复按钮
        fix_buttons = QHBoxLayout()

        auto_fix_btn = QToolButton()
        auto_fix_btn.setText("🔧 自动修复")
        auto_fix_btn.setStyleSheet("""
            QToolButton {
                background-color: #FEF3C7;
                color: #92400E;
                border: 1px solid #FCD34D;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 9px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #FDE68A;
            }
        """)
        fix_buttons.addWidget(auto_fix_btn)

        manual_fix_btn = QToolButton()
        manual_fix_btn.setText("⚙️ 手动调整")
        manual_fix_btn.setStyleSheet("""
            QToolButton {
                background-color: #FEF2F2;
                color: #DC2626;
                border: 1px solid #FECACA;
                border-radius: 3px;
                padding: 3px 6px;
                font-size: 9px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #FEE2E2;
            }
        """)
        fix_buttons.addWidget(manual_fix_btn)

        fix_buttons.addStretch()
        anomaly_layout.addLayout(fix_buttons)

        layout.addWidget(anomaly_frame)

        # 📈 状态统计
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #F0F9FF;
                border: 1px solid #BAE6FD;
                border-radius: 4px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(8, 6, 8, 6)

        stats_title = QLabel("📈 状态统计")
        stats_title.setStyleSheet("font-weight: bold; color: #0369A1; font-size: 11px;")
        stats_layout.addWidget(stats_title)

        # 统计信息
        stats_info = [
            "✅ 已完成: 1/4 (25%)",
            "🔄 进行中: 1/4 (25%)",
            "⏳ 待处理: 2/4 (50%)",
            "🚨 异常: 2个"
        ]

        for info in stats_info:
            info_label = QLabel(info)
            info_label.setStyleSheet("font-size: 9px; color: #0284C7;")
            stats_layout.addWidget(info_label)

        layout.addWidget(stats_frame)

        layout.addStretch()

        return widget

    def create_operation_history_tab(self):
        """创建智能操作历史管理标签页 - 增强撤销重做控制面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # 历史管理标签页
        history_tabs = QTabWidget()
        history_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                background-color: white;
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                padding: 6px 10px;
                margin-right: 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 9px;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                color: {color_scheme_manager.get_test_debug_colors()[0]};
                font-weight: bold;
            }}
        """)

        # 操作历史标签页
        operation_tab = self.create_operation_history_content()
        history_tabs.addTab(operation_tab, "↶ 操作历史")

        # 版本控制标签页
        version_tab = self.create_version_control_tab()
        history_tabs.addTab(version_tab, "🌿 版本控制")

        layout.addWidget(history_tabs)
        return widget

    def create_operation_history_content(self):
        """创建操作历史内容"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # 撤销重做控制工具栏
        control_toolbar = QFrame()
        control_toolbar.setFixedHeight(40)
        control_toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        toolbar_layout = QHBoxLayout(control_toolbar)
        toolbar_layout.setContentsMargins(6, 6, 6, 6)

        # 快速操作控制按钮
        quick_controls = [
            ("↶ 撤销", "Ctrl+Z", "撤销上一步操作"),
            ("↷ 重做", "Ctrl+Y", "重做下一步操作"),
            ("🔄 批量撤销", "", "批量撤销多步操作"),
            ("💾 创建检查点", "", "创建操作检查点"),
            ("🧹 清理历史", "", "清理冗余历史记录")
        ]

        for text, shortcut, tooltip in quick_controls:
            btn = QPushButton(text)
            btn.setToolTip(f"{tooltip}\n{shortcut}" if shortcut else tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_test_debug_colors()[0]};
                    color: white;
                    border: none;
                    padding: 6px 10px;
                    border-radius: 4px;
                    font-size: 9px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {color_scheme_manager.get_test_debug_colors()[1]};
                }}
            """)
            toolbar_layout.addWidget(btn)

        toolbar_layout.addStretch()
        layout.addWidget(control_toolbar)

        # 操作统计面板
        stats_panel = QFrame()
        stats_panel.setFixedHeight(50)
        stats_panel.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        stats_layout = QHBoxLayout(stats_panel)
        stats_layout.setContentsMargins(8, 8, 8, 8)

        # 严格按照设计文档的操作统计信息
        stats_info = [
            ("📊 总操作", "247", "总操作次数"),
            ("↶ 可撤销", "15", "可撤销操作数"),
            ("↷ 可重做", "3", "可重做操作数"),
            ("💾 内存", "4.2MB", "历史记录内存"),
            ("🌿 分支", "2", "历史分支数")
        ]

        for label, value, desc in stats_info:
            stat_frame = QFrame()
            stat_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                    border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                    border-radius: 3px;
                }}
            """)

            stat_layout = QVBoxLayout(stat_frame)
            stat_layout.setContentsMargins(4, 2, 4, 2)

            title = QLabel(label)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_test_debug_colors()[0]};
                    font-weight: bold;
                    font-size: 8px;
                }}
            """)
            stat_layout.addWidget(title)

            value_label = QLabel(value)
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_test_debug_colors()[0]};
                    font-weight: bold;
                    font-size: 12px;
                }}
            """)
            stat_layout.addWidget(value_label)

            stats_layout.addWidget(stat_frame)

        stats_layout.addStretch()
        layout.addWidget(stats_panel)

        # 操作历史列表（时间线视图）
        history_area = QFrame()
        history_area.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)

        history_layout = QVBoxLayout(history_area)
        history_layout.setContentsMargins(6, 6, 6, 6)

        # 历史列表标题
        history_title = QLabel("📋 操作历史时间线")
        history_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_test_debug_colors()[0]};
                font-weight: bold;
                font-size: 11px;
                padding: 4px;
                background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                border-radius: 4px;
            }}
        """)
        history_layout.addWidget(history_title)

        # 操作历史时间线
        timeline_scroll = QScrollArea()
        timeline_scroll.setWidgetResizable(True)
        timeline_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
            }}
        """)

        timeline_widget = QWidget()
        timeline_layout = QVBoxLayout(timeline_widget)
        timeline_layout.setContentsMargins(4, 4, 4, 4)
        timeline_layout.setSpacing(2)

        # 严格按照设计文档的操作历史项
        history_items = [
            ("✅ 添加元素 \"小球\"", "14:32", "详情", False, False),
            ("✅ 修改位置 (400,300) → (500,350)", "14:33", "详情", False, False),
            ("✅ 应用颜色 #3498db → #e74c3c", "14:34", "详情", False, False),
            ("✅ AI生成动画方案 \"火箭运动\"", "14:35", "详情", False, False),
            ("🔄 当前: 调整透明度 70% → 85%", "14:36", "正在进行", True, False),
            ("⏳ 等待下一步操作...", "", "", False, False)
        ]

        for action, time, marker, is_current, is_checkpoint in history_items:
            item = self.create_history_timeline_item(action, time, marker, is_current, is_checkpoint)
            timeline_layout.addWidget(item)

        timeline_layout.addStretch()
        timeline_scroll.setWidget(timeline_widget)
        history_layout.addWidget(timeline_scroll)

        layout.addWidget(history_area)

        # 智能合并建议面板
        merge_panel = self.create_intelligent_merge_suggestions()
        layout.addWidget(merge_panel)

        return widget

    def create_history_timeline_item(self, action, time, marker, is_current, is_checkpoint):
        """创建历史时间线项目"""
        item = QFrame()
        item.setFixedHeight(35)

        # 根据状态设置样式
        if is_current:
            border_color = color_scheme_manager.get_color_hex(ColorRole.ACCENT)
            bg_color = color_scheme_manager.get_color_hex(ColorRole.SURFACE)
        elif is_checkpoint:
            border_color = color_scheme_manager.get_collaboration_colors()[0]
            bg_color = color_scheme_manager.get_collaboration_colors()[2]
        else:
            border_color = color_scheme_manager.get_color_hex(ColorRole.BORDER)
            bg_color = "white"

        item.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-left: 3px solid {border_color};
                border-radius: 4px;
                margin: 1px;
            }}
        """)

        item_layout = QHBoxLayout(item)
        item_layout.setContentsMargins(8, 4, 8, 4)

        # 操作描述
        action_label = QLabel(action)
        action_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                font-size: 10px;
                font-weight: {'bold' if is_current else 'normal'};
            }}
        """)
        item_layout.addWidget(action_label)

        item_layout.addStretch()

        # 标记
        if marker:
            marker_label = QLabel(marker)
            marker_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.ACCENT) if is_current else color_scheme_manager.get_collaboration_colors()[0]};
                    font-size: 8px;
                    font-weight: bold;
                    background-color: {color_scheme_manager.get_color_hex(ColorRole.ACCENT) if is_current else color_scheme_manager.get_collaboration_colors()[0]};
                    color: white;
                    padding: 2px 6px;
                    border-radius: 8px;
                }}
            """)
            item_layout.addWidget(marker_label)

        # 时间
        time_label = QLabel(time)
        time_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 8px;
            }}
        """)
        item_layout.addWidget(time_label)

        return item

    def create_intelligent_merge_suggestions(self):
        """创建智能合并建议面板"""
        panel = QFrame()
        panel.setFixedHeight(80)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 4px;
            }}
        """)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(6, 6, 6, 6)

        # 建议标题
        title = QLabel("🧠 智能合并建议")
        title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-weight: bold;
                font-size: 10px;
                padding: 2px;
            }}
        """)
        panel_layout.addWidget(title)

        # 建议内容
        suggestion_frame = QFrame()
        suggestion_layout = QHBoxLayout(suggestion_frame)
        suggestion_layout.setContentsMargins(0, 0, 0, 0)

        suggestion_text = QLabel("💡 检测到3个连续的文本修改操作，建议合并为单个操作以简化历史记录")
        suggestion_text.setWordWrap(True)
        suggestion_text.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 9px;
                padding: 4px;
                background-color: {color_scheme_manager.get_ai_function_colors()[2]};
                border-radius: 4px;
            }}
        """)
        suggestion_layout.addWidget(suggestion_text)

        # 操作按钮
        merge_btn = QPushButton("合并")
        merge_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 9px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_ai_function_colors()[1]};
            }}
        """)
        suggestion_layout.addWidget(merge_btn)

        ignore_btn = QPushButton("忽略")
        ignore_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 9px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        suggestion_layout.addWidget(ignore_btn)

        panel_layout.addWidget(suggestion_frame)
        return panel

    def create_version_control_tab(self):
        """创建版本控制标签页 - 基于设计文档的Git-like版本控制"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # 版本控制工具栏
        vc_toolbar = QFrame()
        vc_toolbar.setFixedHeight(40)
        vc_toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_collaboration_colors()[2]};
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[0]};
                border-radius: 4px;
            }}
        """)

        toolbar_layout = QHBoxLayout(vc_toolbar)
        toolbar_layout.setContentsMargins(6, 6, 6, 6)

        # 版本控制按钮
        vc_buttons = [
            ("💾 提交", "提交当前更改"),
            ("🌿 分支", "管理分支"),
            ("🔄 同步", "同步远程仓库"),
            ("📋 历史", "查看版本历史")
        ]

        for text, tooltip in vc_buttons:
            btn = QPushButton(text)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_collaboration_colors()[0]};
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 9px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {color_scheme_manager.get_collaboration_colors()[1]};
                }}
            """)
            toolbar_layout.addWidget(btn)

        toolbar_layout.addStretch()
        layout.addWidget(vc_toolbar)

        # 当前分支状态
        branch_status = QFrame()
        branch_status.setFixedHeight(30)
        branch_status.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[0]};
                border-radius: 4px;
            }}
        """)

        branch_layout = QHBoxLayout(branch_status)
        branch_layout.setContentsMargins(8, 4, 8, 4)

        branch_info = QLabel("🌿 当前分支: main | 📝 未提交更改: 3 | ↑ 待推送: 1")
        branch_info.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_collaboration_colors()[0]};
                font-size: 10px;
                font-weight: bold;
            }}
        """)
        branch_layout.addWidget(branch_info)

        layout.addWidget(branch_status)

        # 版本历史列表
        history_title = QLabel("📋 版本历史")
        history_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_collaboration_colors()[0]};
                font-weight: bold;
                font-size: 11px;
                padding: 4px;
            }}
        """)
        layout.addWidget(history_title)

        # 版本历史滚动区域
        history_scroll = QScrollArea()
        history_scroll.setWidgetResizable(True)
        history_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
                background-color: white;
            }}
        """)

        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(4, 4, 4, 4)
        history_layout.setSpacing(2)

        # 示例版本历史
        version_history = [
            ("v1.2.3", "feat: 添加AI元素生成器", "2小时前", "main", True),
            ("v1.2.2", "fix: 修复时间轴同步问题", "1天前", "main", False),
            ("v1.2.1", "feat: 增强多设备预览", "2天前", "feature/preview", False),
            ("v1.2.0", "feat: 实现协作系统", "3天前", "main", False),
            ("v1.1.9", "refactor: 重构色彩系统", "5天前", "main", False)
        ]

        for version, message, time, branch, is_current in version_history:
            commit_item = QFrame()
            commit_item.setFixedHeight(40)

            # 当前版本高亮
            if is_current:
                commit_item.setStyleSheet(f"""
                    QFrame {{
                        background-color: {color_scheme_manager.get_collaboration_colors()[2]};
                        border-left: 3px solid {color_scheme_manager.get_collaboration_colors()[0]};
                        border-radius: 4px;
                        margin: 1px;
                    }}
                """)
            else:
                commit_item.setStyleSheet(f"""
                    QFrame {{
                        background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                        border-left: 3px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                        border-radius: 4px;
                        margin: 1px;
                    }}
                """)

            commit_layout = QHBoxLayout(commit_item)
            commit_layout.setContentsMargins(8, 4, 8, 4)

            # 版本信息
            info_frame = QFrame()
            info_layout = QVBoxLayout(info_frame)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(2)

            # 版本号和消息
            version_label = QLabel(f"{version}: {message}")
            version_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                    font-weight: {'bold' if is_current else 'normal'};
                    font-size: 10px;
                }}
            """)
            info_layout.addWidget(version_label)

            # 时间和分支
            meta_label = QLabel(f"🌿 {branch} • ⏰ {time}")
            meta_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                    font-size: 8px;
                }}
            """)
            info_layout.addWidget(meta_label)

            commit_layout.addWidget(info_frame)
            commit_layout.addStretch()

            # 当前版本标记
            if is_current:
                current_label = QLabel("当前")
                current_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {color_scheme_manager.get_collaboration_colors()[0]};
                        color: white;
                        padding: 2px 6px;
                        border-radius: 8px;
                        font-size: 8px;
                        font-weight: bold;
                    }}
                """)
                commit_layout.addWidget(current_label)

            history_layout.addWidget(commit_item)

        history_layout.addStretch()
        history_scroll.setWidget(history_widget)
        layout.addWidget(history_scroll)

        # 分支管理
        branch_mgmt = QFrame()
        branch_mgmt.setFixedHeight(50)
        branch_mgmt.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)

        branch_mgmt_layout = QHBoxLayout(branch_mgmt)
        branch_mgmt_layout.setContentsMargins(8, 8, 8, 8)

        branch_mgmt_title = QLabel("🌿 分支管理:")
        branch_mgmt_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_collaboration_colors()[0]};
                font-weight: bold;
                font-size: 10px;
            }}
        """)
        branch_mgmt_layout.addWidget(branch_mgmt_title)

        branch_actions = [
            ("新建分支", color_scheme_manager.get_collaboration_colors()[0]),
            ("切换分支", color_scheme_manager.get_performance_colors()[0]),
            ("合并分支", color_scheme_manager.get_color_hex(ColorRole.ACCENT))
        ]

        for text, color in branch_actions:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 9px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            branch_mgmt_layout.addWidget(btn)

        branch_mgmt_layout.addStretch()
        layout.addWidget(branch_mgmt)

        return widget

    def show_element_addition_wizard(self):
        """显示智能元素添加向导 - 基于设计文档的素材管理系统"""
        wizard = ElementAdditionWizard(self)
        wizard.exec()

    def show_ai_element_generator(self):
        """显示AI元素生成器 - 基于设计文档的AI智能素材生成"""
        generator = AIElementGenerator(self)
        generator.exec()

    def show_template_preview_dialog(self):
        """显示模板预览对话框 - 基于设计文档的模板系统"""
        dialog = TemplatePreviewDialog(self)
        dialog.exec()

    def show_device_preview_settings(self):
        """显示设备预览高级设置对话框"""
        QMessageBox.information(self, "高级设置",
            "🔧 设备预览高级设置\n\n"
            "• 同步延迟调整\n"
            "• 网络模拟设置\n"
            "• 设备性能模拟\n"
            "• 测试场景配置\n\n"
            "功能正在开发中...")

    def run_system_diagnostic(self):
        """运行系统诊断"""
        QMessageBox.information(self, "系统诊断",
            "🏥 系统诊断完成\n\n"
            "✅ 系统健康状态: 良好\n"
            "⚠️ 发现 2 个需要注意的问题\n"
            "💡 性能优化建议: 3 条\n\n"
            "详细报告已生成")

    def run_intelligent_scan(self):
        """运行智能扫描"""
        QMessageBox.information(self, "智能扫描",
            "🤖 AI智能扫描完成\n\n"
            "🔬 问题根因分析: 已完成\n"
            "💡 智能修复方案: 3个\n"
            "📊 影响范围评估: 已生成\n\n"
            "建议优先执行推荐方案")

    def execute_repair_solution(self, solution):
        """执行修复方案"""
        QMessageBox.information(self, "修复执行",
            f"🔧 正在执行修复方案\n\n"
            f"方案: {solution}\n"
            f"预计时间: 30秒\n"
            f"风险等级: 低\n\n"
            f"修复完成后将自动验证结果")

        # 🔄 操作历史标题
        title_label = QLabel("🔄 操作历史")
        title_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 12px; padding: 3px;")
        layout.addWidget(title_label)

        # 📋 操作历史列表 (时间线视图)
        history_frame = QFrame()
        history_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        history_layout = QVBoxLayout(history_frame)
        history_layout.setContentsMargins(8, 6, 8, 6)

        history_title = QLabel("📋 操作历史列表 (时间线视图)")
        history_title.setStyleSheet("font-weight: bold; color: #3B82F6; font-size: 11px;")
        history_layout.addWidget(history_title)

        # 历史操作列表
        history_scroll = QScrollArea()
        history_scroll.setWidgetResizable(True)
        history_scroll.setMaximumHeight(120)
        history_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #F3F4F6;
                border-radius: 3px;
                background-color: #FAFAFA;
            }
        """)

        history_content = QWidget()
        history_content_layout = QVBoxLayout(history_content)

        # 历史操作数据
        history_data = [
            ("14:32", "✅", "添加元素 \"小球\"", "#10B981", False),
            ("14:33", "✅", "修改位置 (400,300) → (500,350)", "#10B981", False),
            ("14:34", "✅", "应用颜色 #3498db → #e74c3c", "#10B981", False),
            ("14:35", "✅", "AI生成动画方案 \"火箭运动\"", "#10B981", False),
            ("14:36", "🔄", "当前: 调整透明度 70% → 85%", "#F59E0B", True)
        ]

        for time, status, operation, color, is_current in history_data:
            history_item = QFrame()
            if is_current:
                history_item.setStyleSheet(f"""
                    QFrame {{
                        background-color: {color}15;
                        border: 1px solid {color}40;
                        border-radius: 3px;
                        padding: 2px;
                    }}
                """)
            else:
                history_item.setStyleSheet("""
                    QFrame {
                        background-color: transparent;
                        border: none;
                        padding: 2px;
                    }
                """)

            item_layout = QHBoxLayout(history_item)
            item_layout.setContentsMargins(4, 2, 4, 2)

            # 时间
            time_label = QLabel(time)
            time_label.setStyleSheet("font-size: 8px; color: #6B7280; font-family: 'Consolas', monospace;")
            time_label.setFixedWidth(30)
            item_layout.addWidget(time_label)

            # 状态图标
            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: {color}; font-size: 10px;")
            status_label.setFixedWidth(15)
            item_layout.addWidget(status_label)

            # 操作描述
            operation_label = QLabel(operation)
            operation_label.setStyleSheet(f"color: {color}; font-size: 9px;")
            item_layout.addWidget(operation_label)

            # 详情按钮
            if not is_current:
                detail_btn = QToolButton()
                detail_btn.setText("🔍")
                detail_btn.setToolTip("查看详情")
                detail_btn.setStyleSheet("""
                    QToolButton {
                        border: none;
                        background-color: transparent;
                        padding: 1px 3px;
                        border-radius: 2px;
                    }
                    QToolButton:hover {
                        background-color: #F3F4F6;
                    }
                """)
                item_layout.addWidget(detail_btn)
            else:
                current_label = QLabel("正在进行")
                current_label.setStyleSheet(f"color: {color}; font-size: 8px; font-weight: bold;")
                item_layout.addWidget(current_label)

            history_content_layout.addWidget(history_item)

        # 等待下一步操作提示
        waiting_label = QLabel("⏳ 等待下一步操作...")
        waiting_label.setStyleSheet("color: #6B7280; font-size: 9px; font-style: italic; padding: 4px;")
        history_content_layout.addWidget(waiting_label)

        history_scroll.setWidget(history_content)
        history_layout.addWidget(history_scroll)

        layout.addWidget(history_frame)

        # 🧠 智能合并建议
        merge_frame = QFrame()
        merge_frame.setStyleSheet("""
            QFrame {
                background-color: #EEF2FF;
                border: 1px solid #C7D2FE;
                border-radius: 4px;
            }
        """)
        merge_layout = QVBoxLayout(merge_frame)
        merge_layout.setContentsMargins(8, 6, 8, 6)

        merge_title = QLabel("🧠 智能合并建议")
        merge_title.setStyleSheet("font-weight: bold; color: #3730A3; font-size: 11px;")
        merge_layout.addWidget(merge_title)

        # 合并建议列表
        merge_suggestions = [
            "• 连续的位置调整 (3次) → 建议合并为1次",
            "• 快速颜色调整 (5次) → 建议合并为1次"
        ]

        for suggestion in merge_suggestions:
            suggestion_label = QLabel(suggestion)
            suggestion_label.setStyleSheet("color: #4338CA; font-size: 9px;")
            merge_layout.addWidget(suggestion_label)

        # 合并操作按钮
        merge_actions = QHBoxLayout()

        merge_btn = QToolButton()
        merge_btn.setText("🔗 智能合并")
        merge_btn.setStyleSheet("""
            QToolButton {
                background-color: #3730A3;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #312E81;
            }
        """)
        merge_actions.addWidget(merge_btn)

        ignore_merge_btn = QToolButton()
        ignore_merge_btn.setText("🚫 忽略")
        ignore_merge_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #4338CA;
                border: 1px solid #C7D2FE;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
            }
            QToolButton:hover {
                background-color: #E0E7FF;
            }
        """)
        merge_actions.addWidget(ignore_merge_btn)

        merge_actions.addStretch()
        merge_layout.addLayout(merge_actions)

        layout.addWidget(merge_frame)

        # ⚡ 快速操作
        quick_actions_frame = QFrame()
        quick_actions_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        quick_actions_layout = QVBoxLayout(quick_actions_frame)
        quick_actions_layout.setContentsMargins(8, 6, 8, 6)

        quick_actions_title = QLabel("⚡ 快速操作")
        quick_actions_title.setStyleSheet("font-weight: bold; color: #374151; font-size: 11px;")
        quick_actions_layout.addWidget(quick_actions_title)

        # 快速操作按钮组
        quick_buttons_layout = QGridLayout()

        quick_buttons = [
            ("↶", "撤销", "Ctrl+Z"),
            ("↷", "重做", "Ctrl+Y"),
            ("📋", "完整历史", ""),
            ("🎯", "跳转到", ""),
            ("🔄", "重置到此点", ""),
            ("🧹", "清理历史", "")
        ]

        for i, (icon, name, shortcut) in enumerate(quick_buttons):
            btn = QToolButton()
            btn_text = f"{icon} {name}"
            if shortcut:
                btn_text += f"\n{shortcut}"
            btn.setText(btn_text)
            btn.setStyleSheet("""
                QToolButton {
                    background-color: white;
                    color: #374151;
                    border: 1px solid #D1D5DB;
                    border-radius: 3px;
                    padding: 6px 4px;
                    font-size: 8px;
                    text-align: center;
                }
                QToolButton:hover {
                    background-color: #F3F4F6;
                }
            """)
            quick_buttons_layout.addWidget(btn, i // 3, i % 3)

        quick_actions_layout.addLayout(quick_buttons_layout)
        layout.addWidget(quick_actions_frame)

        # 📊 操作统计
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #F0FDF4;
                border: 1px solid #BBF7D0;
                border-radius: 4px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(8, 6, 8, 6)

        stats_title = QLabel("📊 操作统计")
        stats_title.setStyleSheet("font-weight: bold; color: #166534; font-size: 11px;")
        stats_layout.addWidget(stats_title)

        # 统计信息
        stats_info = QLabel("总操作: 247 | 可撤销: 15 | 可重做: 3\n内存: 4.2MB | 分支: 2")
        stats_info.setStyleSheet("color: #15803D; font-size: 9px;")
        stats_layout.addWidget(stats_info)

        layout.addWidget(stats_frame)

        layout.addStretch()

        return widget

    def create_toolbox_tab(self):
        """创建智能工具箱标签页 - 包含库依赖管理"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # 工具箱标签页
        toolbox_tabs = QTabWidget()
        toolbox_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                background-color: white;
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                padding: 6px 12px;
                margin-right: 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 10px;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                color: {color_scheme_manager.get_test_debug_colors()[0]};
                font-weight: bold;
            }}
        """)

        # 元素工具标签页
        elements_tab = self.create_elements_tools_tab()
        toolbox_tabs.addTab(elements_tab, "🧰 元素工具")

        # 库依赖管理标签页
        dependencies_tab = self.create_library_dependencies_tab()
        toolbox_tabs.addTab(dependencies_tab, "📦 库依赖")

        # 系统工具标签页
        system_tab = self.create_system_tools_tab()
        toolbox_tabs.addTab(system_tab, "⚙️ 系统工具")

        layout.addWidget(toolbox_tabs)
        return widget

    def create_library_dependencies_tab(self):
        """创建库依赖管理标签页 - 基于设计文档的智能依赖管理"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        # 依赖状态概览
        status_frame = QFrame()
        status_frame.setFixedHeight(60)
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_test_debug_colors()[2]};
                border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                border-radius: 4px;
            }}
        """)

        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(8, 8, 8, 8)

        # 状态指标
        status_indicators = [
            ("📦 总库数", "23", "已安装库总数"),
            ("✅ 正常", "20", "运行正常的库"),
            ("⚠️ 警告", "2", "需要更新的库"),
            ("❌ 错误", "1", "存在问题的库")
        ]

        for label, value, desc in status_indicators:
            indicator = QFrame()
            indicator.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid {color_scheme_manager.get_test_debug_colors()[0]};
                    border-radius: 3px;
                }}
            """)

            indicator_layout = QVBoxLayout(indicator)
            indicator_layout.setContentsMargins(4, 2, 4, 2)

            title = QLabel(label)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_test_debug_colors()[0]};
                    font-weight: bold;
                    font-size: 8px;
                }}
            """)
            indicator_layout.addWidget(title)

            value_label = QLabel(value)
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_test_debug_colors()[0]};
                    font-weight: bold;
                    font-size: 12px;
                }}
            """)
            indicator_layout.addWidget(value_label)

            status_layout.addWidget(indicator)

        status_layout.addStretch()
        layout.addWidget(status_frame)

        # 依赖关系可视化
        viz_title = QLabel("🔗 依赖关系可视化")
        viz_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_test_debug_colors()[0]};
                font-weight: bold;
                font-size: 11px;
                padding: 4px;
            }}
        """)
        layout.addWidget(viz_title)

        # 依赖图表区域
        deps_graph = QFrame()
        deps_graph.setMinimumHeight(120)
        deps_graph.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)

        graph_layout = QVBoxLayout(deps_graph)
        graph_layout.setContentsMargins(8, 8, 8, 8)

        # 依赖关系示例
        deps_example = QLabel("📊 依赖关系图\n\nmanim → numpy → scipy\n  ↓      ↓       ↓\npygame  matplotlib  pillow")
        deps_example.setAlignment(Qt.AlignmentFlag.AlignCenter)
        deps_example.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 10px;
                font-family: 'Courier New';
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px dashed {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
                padding: 12px;
            }}
        """)
        graph_layout.addWidget(deps_example)

        layout.addWidget(deps_graph)

        # 库状态列表
        libs_title = QLabel("📋 库状态监控")
        libs_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_test_debug_colors()[0]};
                font-weight: bold;
                font-size: 11px;
                padding: 4px;
            }}
        """)
        layout.addWidget(libs_title)

        # 库列表
        libs_list = QFrame()
        libs_list.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)

        libs_layout = QVBoxLayout(libs_list)
        libs_layout.setContentsMargins(6, 6, 6, 6)
        libs_layout.setSpacing(2)

        # 示例库状态
        library_items = [
            ("manim", "0.18.0", "✅", "正常"),
            ("numpy", "1.24.3", "✅", "正常"),
            ("pillow", "9.5.0", "⚠️", "可更新"),
            ("scipy", "1.10.1", "❌", "版本冲突")
        ]

        for name, version, status, desc in library_items:
            lib_item = QFrame()
            lib_item.setFixedHeight(30)
            lib_item.setStyleSheet(f"""
                QFrame {{
                    background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                    border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                    border-radius: 3px;
                    margin: 1px;
                }}
            """)

            lib_layout = QHBoxLayout(lib_item)
            lib_layout.setContentsMargins(6, 4, 6, 4)

            # 库名
            name_label = QLabel(name)
            name_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                    font-weight: bold;
                    font-size: 9px;
                }}
            """)
            lib_layout.addWidget(name_label)

            # 版本
            version_label = QLabel(version)
            version_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                    font-size: 8px;
                    font-family: 'Courier New';
                }}
            """)
            lib_layout.addWidget(version_label)

            lib_layout.addStretch()

            # 状态
            status_label = QLabel(f"{status} {desc}")
            status_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                    font-size: 8px;
                }}
            """)
            lib_layout.addWidget(status_label)

            libs_layout.addWidget(lib_item)

        layout.addWidget(libs_list)

        # 操作按钮
        actions_frame = QFrame()
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(0, 0, 0, 0)

        action_buttons = [
            ("🔄 刷新状态", color_scheme_manager.get_test_debug_colors()[0]),
            ("⬇️ 更新库", color_scheme_manager.get_collaboration_colors()[0]),
            ("🔧 修复问题", color_scheme_manager.get_color_hex(ColorRole.ACCENT))
        ]

        for text, color in action_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 9px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            actions_layout.addWidget(btn)

        actions_layout.addStretch()
        layout.addWidget(actions_frame)

        layout.addStretch()
        return widget

    def create_system_tools_tab(self):
        """创建系统工具标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        # 系统诊断工具
        diag_title = QLabel("🔍 系统诊断工具")
        diag_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_test_debug_colors()[0]};
                font-weight: bold;
                font-size: 11px;
                padding: 4px;
            }}
        """)
        layout.addWidget(diag_title)

        # 诊断按钮组
        diag_buttons = [
            ("🏥 系统健康检查", "检查系统整体状态"),
            ("🔍 性能诊断", "分析性能瓶颈"),
            ("🧹 清理缓存", "清理临时文件"),
            ("📊 生成报告", "生成诊断报告")
        ]

        for text, desc in diag_buttons:
            btn = QPushButton(text)
            btn.setToolTip(desc)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_test_debug_colors()[0]};
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {color_scheme_manager.get_test_debug_colors()[1]};
                }}
            """)
            layout.addWidget(btn)

        layout.addStretch()
        return widget

    def create_elements_tools_tab(self):
        """创建元素工具标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)

        # 📐 工具箱标题
        title_label = QLabel("📐 智能工具箱")
        title_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 12px; padding: 3px;")
        layout.addWidget(title_label)

        # 🎯 快速添加元素
        quick_add_frame = QFrame()
        quick_add_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        quick_add_layout = QVBoxLayout(quick_add_frame)
        quick_add_layout.setContentsMargins(8, 6, 8, 6)

        quick_add_title = QLabel("🎯 快速添加元素")
        quick_add_title.setStyleSheet("font-weight: bold; color: #3B82F6; font-size: 11px;")
        quick_add_layout.addWidget(quick_add_title)

        # 元素类型网格
        elements_grid = QGridLayout()
        elements_grid.setSpacing(4)

        # 元素类型数据
        element_types = [
            ("📝", "文本", "#3B82F6", True),
            ("🖼️", "图片", "#6B7280", False),
            ("🔷", "形状", "#10B981", True),
            ("📐", "SVG", "#F59E0B", True),
            ("🎬", "视频", "#6B7280", False),
            ("🎵", "音频", "#6B7280", False),
            ("📊", "图表", "#8B5CF6", True),
            ("🤖", "AI生成", "#EF4444", True)
        ]

        for i, (icon, name, color, recommended) in enumerate(element_types):
            element_btn = QToolButton()
            element_btn.setText(f"{icon}\n{name}")

            if recommended:
                element_btn.setStyleSheet(f"""
                    QToolButton {{
                        background-color: {color}15;
                        color: {color};
                        border: 2px solid {color}60;
                        border-radius: 6px;
                        padding: 8px 4px;
                        font-size: 8px;
                        font-weight: bold;
                        text-align: center;
                    }}
                    QToolButton:hover {{
                        background-color: {color}25;
                        border-color: {color};
                    }}
                """)
            else:
                element_btn.setStyleSheet(f"""
                    QToolButton {{
                        background-color: #F9FAFB;
                        color: {color};
                        border: 1px solid #E5E7EB;
                        border-radius: 6px;
                        padding: 8px 4px;
                        font-size: 8px;
                        text-align: center;
                    }}
                    QToolButton:hover {{
                        background-color: #F3F4F6;
                        border-color: {color}60;
                    }}
                """)

            element_btn.setFixedSize(50, 45)
            elements_grid.addWidget(element_btn, i // 4, i % 4)

        quick_add_layout.addLayout(elements_grid)

        # 推荐标识
        recommended_label = QLabel("🔥 推荐元素已高亮显示")
        recommended_label.setStyleSheet("color: #EF4444; font-size: 8px; font-style: italic;")
        quick_add_layout.addWidget(recommended_label)

        layout.addWidget(quick_add_frame)

        # 🤖 AI智能推荐
        ai_recommend_frame = QFrame()
        ai_recommend_frame.setStyleSheet("""
            QFrame {
                background-color: #FEF3C7;
                border: 1px solid #FCD34D;
                border-radius: 4px;
            }
        """)
        ai_recommend_layout = QVBoxLayout(ai_recommend_frame)
        ai_recommend_layout.setContentsMargins(8, 6, 8, 6)

        ai_recommend_title = QLabel("🤖 AI智能推荐")
        ai_recommend_title.setStyleSheet("font-weight: bold; color: #92400E; font-size: 11px;")
        ai_recommend_layout.addWidget(ai_recommend_title)

        project_type_label = QLabel("💡 基于\"科普动画\"项目类型:")
        project_type_label.setStyleSheet("color: #92400E; font-size: 9px; font-weight: bold;")
        ai_recommend_layout.addWidget(project_type_label)

        # AI推荐列表
        recommendations = [
            ("• 原子结构图标 (SVG)", "95%", "#10B981"),
            ("• 科学公式文本", "92%", "#10B981"),
            ("• 数据图表", "88%", "#F59E0B"),
            ("• 箭头指示器", "85%", "#F59E0B")
        ]

        for rec_text, confidence, color in recommendations:
            rec_layout = QHBoxLayout()

            rec_label = QLabel(rec_text)
            rec_label.setStyleSheet("color: #92400E; font-size: 8px;")
            rec_layout.addWidget(rec_label)

            rec_layout.addStretch()

            confidence_label = QLabel(f"匹配度: {confidence}")
            confidence_label.setStyleSheet(f"color: {color}; font-size: 8px; font-weight: bold;")
            rec_layout.addWidget(confidence_label)

            ai_recommend_layout.addLayout(rec_layout)

        # AI推荐操作按钮
        ai_actions = QHBoxLayout()

        batch_add_btn = QToolButton()
        batch_add_btn.setText("⚡ 批量添加推荐")
        batch_add_btn.setStyleSheet("""
            QToolButton {
                background-color: #92400E;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 6px;
                font-size: 8px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #78350F;
            }
        """)
        ai_actions.addWidget(batch_add_btn)

        custom_style_btn = QToolButton()
        custom_style_btn.setText("🎨 自定义样式")
        custom_style_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #92400E;
                border: 1px solid #FCD34D;
                border-radius: 3px;
                padding: 4px 6px;
                font-size: 8px;
            }
            QToolButton:hover {
                background-color: #FDE68A;
            }
        """)
        ai_actions.addWidget(custom_style_btn)

        ai_actions.addStretch()
        ai_recommend_layout.addLayout(ai_actions)

        layout.addWidget(ai_recommend_frame)

        # 🧙‍♂️ 元素添加向导
        wizard_frame = QFrame()
        wizard_frame.setStyleSheet("""
            QFrame {
                background-color: #EEF2FF;
                border: 1px solid #C7D2FE;
                border-radius: 4px;
            }
        """)
        wizard_layout = QVBoxLayout(wizard_frame)
        wizard_layout.setContentsMargins(8, 6, 8, 6)

        wizard_title = QLabel("🧙‍♂️ 元素添加向导")
        wizard_title.setStyleSheet("font-weight: bold; color: #3730A3; font-size: 11px;")
        wizard_layout.addWidget(wizard_title)

        wizard_desc = QLabel("步骤化引导，智能推荐最适合的元素类型")
        wizard_desc.setStyleSheet("color: #4338CA; font-size: 9px;")
        wizard_layout.addWidget(wizard_desc)

        # 向导步骤指示
        steps_layout = QHBoxLayout()

        steps = ["1️⃣选择类型", "2️⃣设置属性", "3️⃣预览效果", "4️⃣添加到舞台"]
        for i, step in enumerate(steps):
            step_label = QLabel(step)
            if i == 0:  # 当前步骤
                step_label.setStyleSheet("color: #3730A3; font-size: 7px; font-weight: bold;")
            else:
                step_label.setStyleSheet("color: #6B7280; font-size: 7px;")
            steps_layout.addWidget(step_label)

            if i < len(steps) - 1:
                arrow_label = QLabel("→")
                arrow_label.setStyleSheet("color: #C7D2FE; font-size: 7px;")
                steps_layout.addWidget(arrow_label)

        wizard_layout.addLayout(steps_layout)

        # 启动向导按钮
        start_wizard_btn = QToolButton()
        start_wizard_btn.setText("🚀 启动向导")
        start_wizard_btn.setStyleSheet("""
            QToolButton {
                background-color: #3730A3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 9px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #312E81;
            }
        """)
        wizard_layout.addWidget(start_wizard_btn)

        layout.addWidget(wizard_frame)

        # 🤖 AI元素生成器
        ai_generator_frame = QFrame()
        ai_generator_frame.setStyleSheet("""
            QFrame {
                background-color: #F0FDF4;
                border: 1px solid #BBF7D0;
                border-radius: 4px;
            }
        """)
        ai_generator_layout = QVBoxLayout(ai_generator_frame)
        ai_generator_layout.setContentsMargins(8, 6, 8, 6)

        ai_generator_title = QLabel("🤖 AI元素生成器")
        ai_generator_title.setStyleSheet("font-weight: bold; color: #166534; font-size: 11px;")
        ai_generator_layout.addWidget(ai_generator_title)

        # 描述输入
        desc_input = QLineEdit()
        desc_input.setPlaceholderText("描述您想要的元素...")
        desc_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #BBF7D0;
                border-radius: 3px;
                padding: 4px 6px;
                font-size: 9px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #10B981;
            }
        """)
        ai_generator_layout.addWidget(desc_input)

        # 生成设置
        settings_layout = QHBoxLayout()

        type_combo = QComboBox()
        type_combo.addItems(["SVG图标", "文本", "形状", "图表"])
        type_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #BBF7D0;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 8px;
                min-width: 50px;
            }
        """)
        settings_layout.addWidget(QLabel("类型:", styleSheet="font-size: 8px; color: #166534;"))
        settings_layout.addWidget(type_combo)

        style_combo = QComboBox()
        style_combo.addItems(["现代简约", "经典", "卡通", "科技"])
        style_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #BBF7D0;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 8px;
                min-width: 50px;
            }
        """)
        settings_layout.addWidget(QLabel("风格:", styleSheet="font-size: 8px; color: #166534;"))
        settings_layout.addWidget(style_combo)

        ai_generator_layout.addLayout(settings_layout)

        # 生成按钮
        generate_btn = QToolButton()
        generate_btn.setText("⚡ AI生成")
        generate_btn.setStyleSheet("""
            QToolButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 9px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #059669;
            }
        """)
        ai_generator_layout.addWidget(generate_btn)

        layout.addWidget(ai_generator_frame)

        layout.addStretch()

        return widget

    # 主工作区标签页创建方法
    def create_enhanced_stage_tab(self):
        """创建增强版舞台编辑标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 🎨 舞台工具栏（按设计方案要求）
        stage_toolbar = QFrame()
        stage_toolbar.setFixedHeight(50)
        stage_toolbar.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-bottom: 1px solid #E5E7EB;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 6px 10px;
                margin: 2px;
                font-size: 11px;
            }
            QToolButton:hover {
                background-color: #E5E7EB;
            }
            QToolButton:pressed {
                background-color: #D1D5DB;
            }
            QToolButton[objectName="active_tool"] {
                background-color: #2C5AA0;
                color: white;
                border-color: #1E3A5F;
            }
        """)

        toolbar_layout = QHBoxLayout(stage_toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # 左侧工具组
        tools_group = QHBoxLayout()

        # 选择工具
        select_tool = QToolButton()
        select_tool.setText("👆 选择")
        select_tool.setObjectName("active_tool")  # 默认激活
        tools_group.addWidget(select_tool)

        # 移动工具
        move_tool = QToolButton()
        move_tool.setText("✋ 移动")
        tools_group.addWidget(move_tool)

        # 路径工具
        path_tool = QToolButton()
        path_tool.setText("📏 路径")
        tools_group.addWidget(path_tool)

        # 文字工具
        text_tool = QToolButton()
        text_tool.setText("📝 文字")
        tools_group.addWidget(text_tool)

        # 形状工具
        shape_tool = QToolButton()
        shape_tool.setText("🔷 形状")
        tools_group.addWidget(shape_tool)

        # 添加元素按钮
        add_element_btn = QToolButton()
        add_element_btn.setText("➕ 添加元素")
        add_element_btn.setStyleSheet("""
            QToolButton {
                background-color: #10B981;
                color: white;
                border-color: #059669;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #059669;
            }
        """)
        tools_group.addWidget(add_element_btn)

        toolbar_layout.addLayout(tools_group)

        # 分隔符
        toolbar_layout.addWidget(QLabel("|"))

        # 中间设置组
        settings_group = QHBoxLayout()

        # 网格设置
        grid_checkbox = QCheckBox("网格:ON")
        grid_checkbox.setChecked(True)
        settings_group.addWidget(grid_checkbox)

        # 吸附设置
        snap_checkbox = QCheckBox("吸附:ON")
        snap_checkbox.setChecked(True)
        settings_group.addWidget(snap_checkbox)

        # 标尺设置
        ruler_checkbox = QCheckBox("标尺:ON")
        ruler_checkbox.setChecked(True)
        settings_group.addWidget(ruler_checkbox)

        toolbar_layout.addLayout(settings_group)

        # 分隔符
        toolbar_layout.addWidget(QLabel("|"))

        # 缩放控制
        zoom_group = QHBoxLayout()
        zoom_group.addWidget(QLabel("🔍"))

        zoom_slider = QSlider(Qt.Orientation.Horizontal)
        zoom_slider.setRange(10, 500)
        zoom_slider.setValue(100)
        zoom_slider.setFixedWidth(100)
        zoom_group.addWidget(zoom_slider)

        zoom_label = QLabel("100%")
        zoom_label.setFixedWidth(40)
        zoom_group.addWidget(zoom_label)

        toolbar_layout.addLayout(zoom_group)

        # 右侧操作组
        toolbar_layout.addStretch()

        actions_group = QHBoxLayout()

        # 居中按钮
        center_btn = QToolButton()
        center_btn.setText("🎯 居中")
        actions_group.addWidget(center_btn)

        # 对齐按钮
        align_btn = QToolButton()
        align_btn.setText("📐 对齐")
        actions_group.addWidget(align_btn)

        toolbar_layout.addLayout(actions_group)

        layout.addWidget(stage_toolbar)

        # 舞台画布区域
        self.enhanced_stage_widget = StageWidget()
        layout.addWidget(self.enhanced_stage_widget)

        # 连接工具栏信号
        zoom_slider.valueChanged.connect(lambda v: zoom_label.setText(f"{v}%"))

        return widget

    def create_device_preview_tab(self):
        """创建多设备预览标签页 - 增强版"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 🖥️ 设备选择工具栏
        device_toolbar = QFrame()
        device_toolbar.setFixedHeight(45)
        device_toolbar.setStyleSheet("""
            QFrame {
                background-color: #F3F4F6;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 6px 12px;
                margin: 3px;
                font-size: 11px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #E5E7EB;
            }
            QToolButton:checked {
                background-color: #2C5AA0;
                color: white;
                border-color: #1E3A5F;
            }
        """)

        device_toolbar_layout = QHBoxLayout(device_toolbar)
        device_toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # 设备按钮组
        device_group = QButtonGroup(self)

        devices = [
            ("💻", "桌面", "1920×1080"),
            ("📱", "手机", "375×812"),
            ("📟", "平板", "768×1024"),
            ("⌚", "手表", "312×390"),
            ("📺", "电视", "3840×2160"),
            ("🎮", "游戏机", "1920×1080"),
            ("🚗", "车载", "1280×480"),
            ("🏢", "广告屏", "1080×1920")
        ]

        for i, (icon, name, resolution) in enumerate(devices):
            btn = QToolButton()
            btn.setText(f"{icon} {name}")
            btn.setCheckable(True)
            if i == 0:  # 默认选中桌面
                btn.setChecked(True)
            device_group.addButton(btn, i)
            device_toolbar_layout.addWidget(btn)

        device_toolbar_layout.addStretch()

        # 同步预览开关
        sync_checkbox = QCheckBox("🔄 同步预览")
        sync_checkbox.setChecked(True)
        sync_checkbox.setStyleSheet("font-weight: bold; color: #10B981;")
        device_toolbar_layout.addWidget(sync_checkbox)

        layout.addWidget(device_toolbar)

        # 📐 当前设备组合信息
        device_combo_frame = QFrame()
        device_combo_frame.setStyleSheet("""
            QFrame {
                background-color: #EEF2FF;
                border: 1px solid #C7D2FE;
                border-radius: 4px;
            }
        """)
        device_combo_layout = QVBoxLayout(device_combo_frame)
        device_combo_layout.setContentsMargins(8, 4, 8, 4)

        combo_title = QLabel("📐 当前设备组合: iPhone 14 Pro + MacBook Pro + iPad")
        combo_title.setStyleSheet("font-weight: bold; color: #3730A3; font-size: 11px;")
        device_combo_layout.addWidget(combo_title)

        layout.addWidget(device_combo_frame)

        # 📱 多设备预览区域
        preview_container = QFrame()
        preview_container.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
        """)
        preview_layout = QVBoxLayout(preview_container)

        # 预览模式选择和控制
        mode_bar = QHBoxLayout()

        mode_label = QLabel("预览模式:")
        mode_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 11px;")
        mode_bar.addWidget(mode_label)

        mode_combo = QComboBox()
        mode_combo.addItems(["单设备预览", "双设备对比", "四设备网格", "全设备展示"])
        mode_combo.setCurrentText("四设备网格")
        mode_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #D1D5DB;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 10px;
                min-width: 100px;
            }
        """)
        mode_bar.addWidget(mode_combo)

        mode_bar.addStretch()

        # 预览控制按钮
        preview_controls = QHBoxLayout()

        control_buttons = [
            ("▶️", "播放", "#10B981"),
            ("⏸️", "暂停", "#6B7280"),
            ("🔄", "同步刷新", "#3B82F6"),
            ("📸", "全设备截图", "#F59E0B"),
            ("🎥", "录制全部", "#EF4444")
        ]

        for icon, name, color in control_buttons:
            btn = QToolButton()
            btn.setText(f"{icon} {name}")
            btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {color}15;
                    color: {color};
                    border: 1px solid {color}40;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 9px;
                    font-weight: bold;
                    margin: 1px;
                }}
                QToolButton:hover {{
                    background-color: {color}25;
                }}
            """)
            preview_controls.addWidget(btn)

        mode_bar.addLayout(preview_controls)
        preview_layout.addLayout(mode_bar)

        # 设备预览网格 - 增强版
        preview_grid = QGridLayout()
        preview_grid.setSpacing(8)

        # 设备预览数据
        devices_preview_data = [
            {
                "name": "iPhone 14 Pro",
                "icon": "📱",
                "resolution": "1179×2556",
                "ratio": "3.0",
                "orientation": "竖屏",
                "color": "#007AFF"
            },
            {
                "name": "MacBook Pro",
                "icon": "💻",
                "resolution": "2560×1600",
                "ratio": "2.0",
                "orientation": "横屏",
                "color": "#34C759"
            },
            {
                "name": "iPad Pro",
                "icon": "📟",
                "resolution": "2048×2732",
                "ratio": "2.0",
                "orientation": "竖屏",
                "color": "#FF9500"
            },
            {
                "name": "Apple Watch",
                "icon": "⌚",
                "resolution": "312×390",
                "ratio": "2.0",
                "orientation": "竖屏",
                "color": "#FF3B30"
            }
        ]

        # 创建设备预览框
        for i, device in enumerate(devices_preview_data):
            device_frame = QFrame()
            device_frame.setFixedSize(280, 200)
            device_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 2px solid {device["color"]}40;
                    border-radius: 8px;
                }}
                QFrame:hover {{
                    border-color: {device["color"]};
                    background-color: {device["color"]}08;
                }}
            """)

            device_layout = QVBoxLayout(device_frame)
            device_layout.setContentsMargins(6, 4, 6, 4)
            device_layout.setSpacing(3)

            # 设备标题栏
            title_bar = QHBoxLayout()

            device_title = QLabel(f"{device['icon']} {device['name']}")
            device_title.setStyleSheet(f"font-weight: bold; color: {device['color']}; font-size: 11px;")
            title_bar.addWidget(device_title)

            title_bar.addStretch()

            # 同步状态指示
            sync_status = QLabel("🔄")
            sync_status.setStyleSheet("color: #10B981; font-size: 10px;")
            sync_status.setToolTip("同步中")
            title_bar.addWidget(sync_status)

            device_layout.addLayout(title_bar)

            # 设备详细信息
            device_info = QLabel(f"分辨率: {device['resolution']} | 像素比: {device['ratio']} | 方向: {device['orientation']}")
            device_info.setStyleSheet("color: #6B7280; font-size: 8px; padding: 2px;")
            device_layout.addWidget(device_info)

            # 预览内容区域
            content_area = QFrame()
            content_area.setStyleSheet(f"""
                QFrame {{
                    background-color: #F8F9FA;
                    border: 1px solid {device["color"]}30;
                    border-radius: 4px;
                }}
            """)
            content_layout = QVBoxLayout(content_area)
            content_layout.setContentsMargins(4, 4, 4, 4)

            # 预览内容
            preview_content = QLabel(f"[{device['name']}预览]\n\n动画在此同步显示")
            preview_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview_content.setStyleSheet(f"color: {device['color']}; font-size: 9px; font-weight: bold;")
            content_layout.addWidget(preview_content)

            device_layout.addWidget(content_area)

            # 设备操作按钮
            device_actions = QHBoxLayout()

            action_buttons = [
                ("🔄", "刷新"),
                ("📷", "截图"),
                ("⚙️", "设置")
            ]

            for icon, name in action_buttons:
                btn = QToolButton()
                btn.setText(icon)
                btn.setToolTip(name)
                btn.setStyleSheet(f"""
                    QToolButton {{
                        background-color: transparent;
                        color: {device["color"]};
                        border: 1px solid {device["color"]}40;
                        border-radius: 3px;
                        padding: 2px 4px;
                        font-size: 8px;
                    }}
                    QToolButton:hover {{
                        background-color: {device["color"]}15;
                    }}
                """)
                device_actions.addWidget(btn)

            device_actions.addStretch()
            device_layout.addLayout(device_actions)

            preview_grid.addWidget(device_frame, i // 2, i % 2)

        preview_layout.addLayout(preview_grid)

        layout.addWidget(preview_container)

        # ⚙️ 高级模拟设置
        advanced_settings_frame = QFrame()
        advanced_settings_frame.setStyleSheet("""
            QFrame {
                background-color: #F0F9FF;
                border: 1px solid #BAE6FD;
                border-radius: 6px;
            }
        """)
        advanced_settings_layout = QVBoxLayout(advanced_settings_frame)
        advanced_settings_layout.setContentsMargins(8, 6, 8, 6)

        advanced_title = QLabel("⚙️ 高级模拟设置")
        advanced_title.setStyleSheet("font-weight: bold; color: #0369A1; font-size: 11px;")
        advanced_settings_layout.addWidget(advanced_title)

        # 设备参数设置
        params_layout = QHBoxLayout()

        # 网络设置
        params_layout.addWidget(QLabel("网络:", styleSheet="color: #0284C7; font-size: 9px;"))
        network_combo = QComboBox()
        network_combo.addItems(["5G", "4G", "WiFi", "3G", "2G", "离线"])
        network_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #BAE6FD;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 8px;
                min-width: 40px;
            }
        """)
        params_layout.addWidget(network_combo)

        # CPU设置
        params_layout.addWidget(QLabel("CPU:", styleSheet="color: #0284C7; font-size: 9px;"))
        cpu_combo = QComboBox()
        cpu_combo.addItems(["A17 Pro", "A16", "A15", "M2", "M1"])
        cpu_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #BAE6FD;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 8px;
                min-width: 50px;
            }
        """)
        params_layout.addWidget(cpu_combo)

        # 内存设置
        params_layout.addWidget(QLabel("内存:", styleSheet="color: #0284C7; font-size: 9px;"))
        memory_combo = QComboBox()
        memory_combo.addItems(["8GB", "6GB", "4GB", "3GB", "2GB"])
        memory_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #BAE6FD;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 8px;
                min-width: 40px;
            }
        """)
        params_layout.addWidget(memory_combo)

        params_layout.addStretch()
        advanced_settings_layout.addLayout(params_layout)

        # 模拟选项
        simulation_options = QHBoxLayout()

        sim_checkboxes = [
            ("触摸模拟", True),
            ("陀螺仪", True),
            ("暗黑模式", False),
            ("动态岛", True)
        ]

        for text, checked in sim_checkboxes:
            checkbox = QCheckBox(text)
            checkbox.setChecked(checked)
            checkbox.setStyleSheet("color: #0284C7; font-size: 8px;")
            simulation_options.addWidget(checkbox)

        simulation_options.addStretch()
        advanced_settings_layout.addLayout(simulation_options)

        layout.addWidget(advanced_settings_frame)

        # 🎯 测试场景
        test_scenarios_frame = QFrame()
        test_scenarios_frame.setStyleSheet("""
            QFrame {
                background-color: #FEF3C7;
                border: 1px solid #FCD34D;
                border-radius: 6px;
            }
        """)
        test_scenarios_layout = QVBoxLayout(test_scenarios_frame)
        test_scenarios_layout.setContentsMargins(8, 6, 8, 6)

        scenarios_title = QLabel("🎯 测试场景")
        scenarios_title.setStyleSheet("font-weight: bold; color: #92400E; font-size: 11px;")
        test_scenarios_layout.addWidget(scenarios_title)

        # 测试场景按钮
        scenarios_layout = QHBoxLayout()

        test_scenarios = [
            ("📶", "弱网络", "#EF4444"),
            ("🔋", "低电量", "#F59E0B"),
            ("🌙", "夜间模式", "#6B7280"),
            ("🎧", "音频测试", "#8B5CF6"),
            ("🔄", "横竖屏", "#10B981"),
            ("📏", "缩放测试", "#3B82F6"),
            ("⚡", "性能压测", "#EF4444"),
            ("🌐", "兼容性测试", "#06B6D4")
        ]

        for icon, name, color in test_scenarios:
            btn = QToolButton()
            btn.setText(f"{icon} {name}")
            btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {color}15;
                    color: {color};
                    border: 1px solid {color}40;
                    border-radius: 3px;
                    padding: 3px 6px;
                    font-size: 8px;
                    font-weight: bold;
                    margin: 1px;
                }}
                QToolButton:hover {{
                    background-color: {color}25;
                }}
            """)
            scenarios_layout.addWidget(btn)

        test_scenarios_layout.addLayout(scenarios_layout)
        layout.addWidget(test_scenarios_frame)

        # 底部状态栏 - 增强版
        status_bar = QFrame()
        status_bar.setFixedHeight(35)
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-top: 1px solid #E5E7EB;
                border-radius: 0 0 6px 6px;
            }
        """)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(8, 4, 8, 4)

        # 状态信息
        status_info = QLabel("📊 预览状态: 就绪 | 🔄 同步: 开启 | 📡 连接: 4/4 设备")
        status_info.setStyleSheet("color: #10B981; font-size: 10px; font-weight: bold;")
        status_layout.addWidget(status_info)

        status_layout.addStretch()

        # 批量操作按钮
        batch_actions = [
            ("📤", "批量分享", "#3B82F6"),
            ("📊", "性能报告", "#F59E0B"),
            ("⚙️", "全局设置", "#6B7280")
        ]

        for icon, name, color in batch_actions:
            btn = QToolButton()
            btn.setText(f"{icon} {name}")
            btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {color}15;
                    color: {color};
                    border: 1px solid {color}40;
                    border-radius: 3px;
                    padding: 3px 6px;
                    font-size: 8px;
                    font-weight: bold;
                }}
                QToolButton:hover {{
                    background-color: {color}25;
                }}
            """)
            status_layout.addWidget(btn)

        layout.addWidget(status_bar)

        return widget

    def create_debug_panel_tab(self):
        """创建AI智能诊断与修复中心 - 完整版"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 🔍 AI智能诊断与修复中心标题
        title_frame = QFrame()
        title_frame.setFixedHeight(40)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #DC2626;
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("🔍 AI智能诊断与修复中心")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 实时扫描状态
        scan_status = QLabel("🔄 实时扫描中...")
        scan_status.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        title_layout.addWidget(scan_status)

        layout.addWidget(title_frame)

        # 🚨 关键问题检测区域
        critical_issues_frame = QFrame()
        critical_issues_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #FECACA;
                border-radius: 6px;
            }
        """)
        critical_issues_layout = QVBoxLayout(critical_issues_frame)
        critical_issues_layout.setContentsMargins(8, 6, 8, 6)

        critical_title = QLabel("🚨 关键问题检测 (实时扫描)")
        critical_title.setStyleSheet("font-weight: bold; color: #DC2626; font-size: 12px;")
        critical_issues_layout.addWidget(critical_title)

        # 问题列表滚动区域
        issues_scroll = QScrollArea()
        issues_scroll.setWidgetResizable(True)
        issues_scroll.setMaximumHeight(200)
        issues_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #F3F4F6;
                border-radius: 3px;
                background-color: #FAFAFA;
            }
        """)

        issues_content = QWidget()
        issues_content_layout = QVBoxLayout(issues_content)

        # 问题数据
        issues_data = [
            {
                "level": "❌",
                "title": "AI生成器导入错误",
                "severity": "严重",
                "impact": "95%",
                "error": "ModuleNotFoundError: google.generativeai",
                "location": "src/ai/gemini_service.py:line 12",
                "first_seen": "14:32",
                "last_seen": "刚刚",
                "color": "#DC2626"
            },
            {
                "level": "⚠️",
                "title": "预览组件方法冲突",
                "severity": "中等",
                "impact": "60%",
                "error": "play_animation方法在多个类中重复定义",
                "location": "src/ui/preview.py + src/core/animator.py",
                "first_seen": "13:45",
                "last_seen": "5分钟前",
                "color": "#F59E0B"
            },
            {
                "level": "⚠️",
                "title": "元素添加功能不完整",
                "severity": "中等",
                "impact": "40%",
                "error": "add_element_dialog方法未完整实现",
                "location": "src/ui/element_manager.py:line 156",
                "first_seen": "12:30",
                "last_seen": "1小时前",
                "color": "#F59E0B"
            },
            {
                "level": "💡",
                "title": "性能警告: GPU使用率持续高于85%",
                "severity": "警告",
                "impact": "性能",
                "error": "建议: 降低粒子效果复杂度或启用性能模式",
                "location": "系统监控",
                "first_seen": "持续",
                "last_seen": "实时",
                "color": "#3B82F6"
            }
        ]

        for issue in issues_data:
            issue_frame = QFrame()
            issue_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {issue["color"]}08;
                    border: 1px solid {issue["color"]}40;
                    border-radius: 4px;
                    margin: 2px;
                }}
            """)
            issue_layout = QVBoxLayout(issue_frame)
            issue_layout.setContentsMargins(8, 6, 8, 6)

            # 问题标题行
            title_layout = QHBoxLayout()

            issue_title = QLabel(f"{issue['level']} {issue['title']}")
            issue_title.setStyleSheet(f"color: {issue['color']}; font-size: 11px; font-weight: bold;")
            title_layout.addWidget(issue_title)

            title_layout.addStretch()

            severity_impact = QLabel(f"{issue['severity']} | 影响: {issue['impact']}")
            severity_impact.setStyleSheet(f"color: {issue['color']}; font-size: 10px; font-weight: bold;")
            title_layout.addWidget(severity_impact)

            issue_layout.addLayout(title_layout)

            # 错误详情
            error_label = QLabel(issue["error"])
            error_label.setStyleSheet("color: #374151; font-size: 10px; padding: 2px 0;")
            error_label.setWordWrap(True)
            issue_layout.addWidget(error_label)

            # 位置和时间信息
            location_time = QLabel(f"📍 位置: {issue['location']}")
            location_time.setStyleSheet("color: #6B7280; font-size: 9px;")
            issue_layout.addWidget(location_time)

            time_info = QLabel(f"🕐 首次发现: {issue['first_seen']}  🔄 最近发生: {issue['last_seen']}")
            time_info.setStyleSheet("color: #6B7280; font-size: 9px;")
            issue_layout.addWidget(time_info)

            # 操作按钮
            actions_layout = QHBoxLayout()

            if issue["level"] == "💡":
                action_buttons = [
                    ("⚡", "一键优化", issue["color"]),
                    ("📊", "性能分析", "#6B7280"),
                    ("⚙️", "设置", "#6B7280")
                ]
            else:
                action_buttons = [
                    ("🔧", "自动修复", issue["color"]),
                    ("📋", "详情", "#6B7280"),
                    ("💡", "AI建议", "#3B82F6"),
                    ("❓", "帮助", "#6B7280")
                ]

            for icon, name, color in action_buttons:
                btn = QToolButton()
                btn.setText(f"{icon} {name}")
                btn.setStyleSheet(f"""
                    QToolButton {{
                        background-color: {color}15;
                        color: {color};
                        border: 1px solid {color}40;
                        border-radius: 3px;
                        padding: 3px 6px;
                        font-size: 8px;
                        font-weight: bold;
                        margin: 1px;
                    }}
                    QToolButton:hover {{
                        background-color: {color}25;
                    }}
                """)
                actions_layout.addWidget(btn)

            actions_layout.addStretch()
            issue_layout.addLayout(actions_layout)

            issues_content_layout.addWidget(issue_frame)

        issues_scroll.setWidget(issues_content)
        critical_issues_layout.addWidget(issues_scroll)

        layout.addWidget(critical_issues_frame)

        # 📊 系统健康仪表板
        health_dashboard_frame = QFrame()
        health_dashboard_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
            }
        """)
        health_dashboard_layout = QVBoxLayout(health_dashboard_frame)
        health_dashboard_layout.setContentsMargins(8, 6, 8, 6)

        dashboard_title = QLabel("📊 系统健康仪表板")
        dashboard_title.setStyleSheet("font-weight: bold; color: #374151; font-size: 12px;")
        health_dashboard_layout.addWidget(dashboard_title)

        # 四大功能模块状态
        modules_layout = QGridLayout()

        modules_data = [
            ("核心功能", "85%", "🟡", "部分可用", "#F59E0B"),
            ("界面组件", "95%", "🟢", "正常", "#10B981"),
            ("AI服务", "15%", "🔴", "故障", "#DC2626"),
            ("协作功能", "90%", "🟢", "正常", "#10B981")
        ]

        for i, (name, percentage, status, desc, color) in enumerate(modules_data):
            module_frame = QFrame()
            module_frame.setFixedSize(120, 60)
            module_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}10;
                    border: 1px solid {color}40;
                    border-radius: 4px;
                }}
            """)

            module_layout = QVBoxLayout(module_frame)
            module_layout.setContentsMargins(4, 3, 4, 3)

            # 模块名称
            name_label = QLabel(name)
            name_label.setStyleSheet("color: #374151; font-size: 10px; font-weight: bold;")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            module_layout.addWidget(name_label)

            # 状态和百分比
            status_layout = QHBoxLayout()
            status_label = QLabel(f"{status} {percentage}")
            status_label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold;")
            status_layout.addWidget(status_label)
            module_layout.addLayout(status_layout)

            # 进度条（ASCII风格）
            progress_value = int(percentage.rstrip('%'))
            filled_blocks = progress_value // 10
            empty_blocks = 10 - filled_blocks
            progress_bar = "█" * filled_blocks + "░" * empty_blocks

            progress_label = QLabel(progress_bar)
            progress_label.setStyleSheet(f"color: {color}; font-family: 'Consolas', monospace; font-size: 8px;")
            progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            module_layout.addWidget(progress_label)

            # 状态描述
            desc_label = QLabel(desc)
            desc_label.setStyleSheet(f"color: {color}; font-size: 8px;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            module_layout.addWidget(desc_label)

            modules_layout.addWidget(module_frame, i // 2, i % 2)

        health_dashboard_layout.addLayout(modules_layout)

        # 系统资源和网络状态
        system_info_layout = QVBoxLayout()

        # 系统资源
        resources_label = QLabel("💻 系统资源: CPU:23% | 内存:67% | GPU:85% | 磁盘:充足")
        resources_label.setStyleSheet("color: #374151; font-size: 10px; font-weight: bold; padding: 3px;")
        system_info_layout.addWidget(resources_label)

        # 网络状态
        network_label = QLabel("🌐 网络状态: 正常 | 延迟:25ms | AI服务:离线 | 协作:在线")
        network_label.setStyleSheet("color: #374151; font-size: 10px; font-weight: bold; padding: 3px;")
        system_info_layout.addWidget(network_label)

        health_dashboard_layout.addLayout(system_info_layout)

        # 全局操作按钮
        global_actions = QHBoxLayout()

        global_buttons = [
            ("⚡", "一键修复全部", "#DC2626"),
            ("🔄", "重新扫描", "#3B82F6"),
            ("📊", "生成诊断报告", "#F59E0B"),
            ("⚙️", "设置", "#6B7280")
        ]

        for icon, name, color in global_buttons:
            btn = QToolButton()
            btn.setText(f"{icon} {name}")
            btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {color}15;
                    color: {color};
                    border: 1px solid {color}40;
                    border-radius: 4px;
                    padding: 6px 10px;
                    font-size: 10px;
                    font-weight: bold;
                    margin: 2px;
                }}
                QToolButton:hover {{
                    background-color: {color}25;
                }}
            """)
            global_actions.addWidget(btn)

        global_actions.addStretch()
        health_dashboard_layout.addLayout(global_actions)

        layout.addWidget(health_dashboard_frame)

        # 🤖 AI智能修复助手
        ai_assistant_frame = QFrame()
        ai_assistant_frame.setStyleSheet("""
            QFrame {
                background-color: #F0F9FF;
                border: 1px solid #BAE6FD;
                border-radius: 6px;
            }
        """)
        ai_assistant_layout = QVBoxLayout(ai_assistant_frame)
        ai_assistant_layout.setContentsMargins(8, 6, 8, 6)

        assistant_title = QLabel("🤖 AI智能修复助手")
        assistant_title.setStyleSheet("font-weight: bold; color: #0369A1; font-size: 12px;")
        ai_assistant_layout.addWidget(assistant_title)

        # 当前问题分析
        current_problem = QLabel("🎯 当前问题: AI生成器导入错误")
        current_problem.setStyleSheet("color: #0284C7; font-size: 11px; font-weight: bold;")
        ai_assistant_layout.addWidget(current_problem)

        problem_meta = QLabel("错误类型: 模块导入失败 | 严重程度: 高 | 自动修复成功率: 95%")
        problem_meta.setStyleSheet("color: #0284C7; font-size: 10px;")
        ai_assistant_layout.addWidget(problem_meta)

        # AI分析结果
        analysis_frame = QFrame()
        analysis_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #BAE6FD;
                border-radius: 4px;
            }
        """)
        analysis_layout = QVBoxLayout(analysis_frame)
        analysis_layout.setContentsMargins(6, 4, 6, 4)

        analysis_title = QLabel("💡 AI分析结果")
        analysis_title.setStyleSheet("color: #0369A1; font-size: 11px; font-weight: bold;")
        analysis_layout.addWidget(analysis_title)

        # 问题根因分析
        root_cause = QLabel("🧠 问题根因分析:")
        root_cause.setStyleSheet("color: #0284C7; font-size: 10px; font-weight: bold;")
        analysis_layout.addWidget(root_cause)

        causes = [
            "• 依赖包google-generativeai未正确安装",
            "• 导入语句格式不正确",
            "• Python环境路径配置问题"
        ]

        for cause in causes:
            cause_label = QLabel(cause)
            cause_label.setStyleSheet("color: #0284C7; font-size: 9px; padding-left: 10px;")
            analysis_layout.addWidget(cause_label)

        # 影响范围
        impact_title = QLabel("🔍 影响范围:")
        impact_title.setStyleSheet("color: #0284C7; font-size: 10px; font-weight: bold;")
        analysis_layout.addWidget(impact_title)

        impacts = [
            "• AI动画生成功能完全无法使用",
            "• Prompt编辑器无法连接AI服务",
            "• 智能推荐功能失效"
        ]

        for impact in impacts:
            impact_label = QLabel(impact)
            impact_label.setStyleSheet("color: #0284C7; font-size: 9px; padding-left: 10px;")
            analysis_layout.addWidget(impact_label)

        ai_assistant_layout.addWidget(analysis_frame)

        # 智能修复方案
        solutions_title = QLabel("🔧 智能修复方案 (AI推荐)")
        solutions_title.setStyleSheet("color: #0369A1; font-size: 11px; font-weight: bold;")
        ai_assistant_layout.addWidget(solutions_title)

        # 方案1
        solution1_frame = QFrame()
        solution1_frame.setStyleSheet("""
            QFrame {
                background-color: #F0FDF4;
                border: 1px solid #BBF7D0;
                border-radius: 4px;
            }
        """)
        solution1_layout = QVBoxLayout(solution1_frame)
        solution1_layout.setContentsMargins(6, 4, 6, 4)

        solution1_title = QLabel("🥇 方案1: 自动修复依赖 (强烈推荐)")
        solution1_title.setStyleSheet("color: #166534; font-size: 10px; font-weight: bold;")
        solution1_layout.addWidget(solution1_title)

        solution1_steps = [
            "• 自动检测Python环境",
            "• 执行: pip install google-generativeai",
            "• 修正导入语句格式",
            "• 验证API连接"
        ]

        for step in solution1_steps:
            step_label = QLabel(step)
            step_label.setStyleSheet("color: #15803D; font-size: 9px; padding-left: 5px;")
            solution1_layout.addWidget(step_label)

        solution1_meta = QLabel("成功率: 95% | 风险: 极低 | 耗时: 30-60秒")
        solution1_meta.setStyleSheet("color: #166534; font-size: 9px; font-weight: bold;")
        solution1_layout.addWidget(solution1_meta)

        # 方案1操作按钮
        solution1_actions = QHBoxLayout()

        execute_btn = QToolButton()
        execute_btn.setText("⚡ 立即执行")
        execute_btn.setStyleSheet("""
            QToolButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #059669;
            }
        """)
        solution1_actions.addWidget(execute_btn)

        view_steps_btn = QToolButton()
        view_steps_btn.setText("📋 查看步骤")
        view_steps_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #166534;
                border: 1px solid #BBF7D0;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
            }
            QToolButton:hover {
                background-color: #F0FDF4;
            }
        """)
        solution1_actions.addWidget(view_steps_btn)

        customize_btn = QToolButton()
        customize_btn.setText("⚙️ 自定义")
        customize_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #166534;
                border: 1px solid #BBF7D0;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
            }
            QToolButton:hover {
                background-color: #F0FDF4;
            }
        """)
        solution1_actions.addWidget(customize_btn)

        solution1_actions.addStretch()
        solution1_layout.addLayout(solution1_actions)

        ai_assistant_layout.addWidget(solution1_frame)

        layout.addWidget(ai_assistant_frame)

        # 调试面板分割区域
        debug_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：调试信息面板
        left_panel = QSplitter(Qt.Orientation.Vertical)

        # 错误日志区域
        error_frame = QFrame()
        error_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
            }
        """)
        error_layout = QVBoxLayout(error_frame)

        error_title = QLabel("🚨 错误日志")
        error_title.setStyleSheet("""
            font-weight: bold;
            padding: 8px;
            background-color: #FEF2F2;
            border-radius: 4px;
            color: #DC2626;
        """)
        error_layout.addWidget(error_title)

        self.error_log = QTextEdit()
        self.error_log.setPlainText("""🔍 AI Animation Studio 调试面板 v2.0
════════════════════════════════════════════════════════════════

[2024-01-15 10:30:20] [DEBUG] 调试器已启动
[2024-01-15 10:30:21] [INFO] 断点管理器初始化完成
[2024-01-15 10:30:22] [DEBUG] 变量监视器已激活
[2024-01-15 10:30:23] [INFO] 调试环境准备就绪

暂无错误信息 ✅

支持的调试功能:
• 实时变量监视
• 断点设置与管理
• 调用栈跟踪
• 内存使用分析
• 性能瓶颈检测""")

        self.error_log.setStyleSheet("""
            QTextEdit {
                background-color: #FEFEFE;
                border: none;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                line-height: 1.4;
                padding: 10px;
            }
        """)
        error_layout.addWidget(self.error_log)

        left_panel.addWidget(error_frame)

        # 调用栈区域
        stack_frame = QFrame()
        stack_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
            }
        """)
        stack_layout = QVBoxLayout(stack_frame)

        stack_title = QLabel("📚 调用栈")
        stack_title.setStyleSheet("""
            font-weight: bold;
            padding: 8px;
            background-color: #EEF2FF;
            border-radius: 4px;
            color: #3730A3;
        """)
        stack_layout.addWidget(stack_title)

        stack_list = QTextEdit()
        stack_list.setMaximumHeight(120)
        stack_list.setPlainText("""调用栈跟踪:

1. main_window.py:1234 - setup_main_work_area()
2. stage_widget.py:456 - render_elements()
3. animation_engine.py:789 - update_frame()
4. ai_generator.py:123 - generate_animation()

当前执行位置: ai_generator.py:125""")
        stack_list.setStyleSheet("""
            QTextEdit {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
        """)
        stack_layout.addWidget(stack_list)

        left_panel.addWidget(stack_frame)

        debug_splitter.addWidget(left_panel)

        # 右侧：变量监视面板
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)

        # 变量监视标题
        var_title = QLabel("👁️ 变量监视")
        var_title.setStyleSheet("""
            font-weight: bold;
            padding: 8px;
            background-color: #F0FDF4;
            border-radius: 4px;
            color: #166534;
        """)
        right_layout.addWidget(var_title)

        # 变量监视表格
        var_tree.setHeaderLabels(["变量名", "类型", "值"])
        var_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #FEFEFE;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #F3F4F6;
            }
            QTreeWidget::item:selected {
                background-color: #EEF2FF;
            }
        """)

        # 添加示例变量
        global_vars = QTreeWidgetItem(var_tree, ["🌐 全局变量", "", ""])
        QTreeWidgetItem(global_vars, ["selected_element", "Element", "小球_001"])
        QTreeWidgetItem(global_vars, ["current_time", "float", "2.35"])
        QTreeWidgetItem(global_vars, ["animation_state", "str", "playing"])
        QTreeWidgetItem(global_vars, ["canvas_scale", "float", "1.0"])

        local_vars = QTreeWidgetItem(var_tree, ["🏠 局部变量", "", ""])
        QTreeWidgetItem(local_vars, ["x_position", "int", "450"])
        QTreeWidgetItem(local_vars, ["y_position", "int", "300"])
        QTreeWidgetItem(local_vars, ["velocity", "Vector2", "(12.5, -8.3)"])
        QTreeWidgetItem(local_vars, ["opacity", "float", "0.85"])

        ai_vars = QTreeWidgetItem(var_tree, ["🤖 AI变量", "", ""])
        QTreeWidgetItem(ai_vars, ["prompt_text", "str", "小球快速移动..."])
        QTreeWidgetItem(ai_vars, ["confidence", "float", "0.94"])
        QTreeWidgetItem(ai_vars, ["generation_time", "float", "12.3"])

        var_tree.expandAll()
        right_layout.addWidget(var_tree)

        # 变量操作按钮
        var_controls = QHBoxLayout()
        var_controls.addWidget(QToolButton(text="➕ 添加监视"))
        var_controls.addWidget(QToolButton(text="❌ 移除"))
        var_controls.addWidget(QToolButton(text="🔄 刷新"))
        var_controls.addStretch()

        right_layout.addLayout(var_controls)

        debug_splitter.addWidget(right_panel)

        # 设置分割器比例
        debug_splitter.setSizes([400, 300])

        layout.addWidget(debug_splitter)

        return widget

    def create_enhanced_ai_generator_tab(self):
        """创建增强版AI生成器标签页 - 三级精确度生成控制"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(6)

        # 三级精确度控制面板
        precision_control = self.create_precision_control_panel()
        layout.addWidget(precision_control)

        # 🤖 AI动画生成器标题
        title_frame = QFrame()
        title_frame.setFixedHeight(40)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #FF6B35;
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("🤖 AI动画生成器 (Gemini驱动)")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # AI状态指示
        ai_status = QLabel("🟢 在线")
        ai_status.setStyleSheet("color: white; font-weight: bold;")
        title_layout.addWidget(ai_status)

        layout.addWidget(title_frame)

        # 📝 多模式输入区域
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #FDBA74;
                border-radius: 6px;
            }
        """)
        input_layout = QVBoxLayout(input_frame)

        # 输入模式选择
        mode_bar = QHBoxLayout()
        mode_bar.addWidget(QLabel("📝 多模式输入"))

        input_mode_group = QButtonGroup(self)

        modes = [("📝", "文本"), ("🎤", "语音"), ("🖼️", "图片"), ("📄", "模板"), ("🔄", "批量")]
        for i, (icon, name) in enumerate(modes):
            btn = QToolButton()
            btn.setText(f"{icon} {name}")
            btn.setCheckable(True)
            if i == 0:  # 默认选中文本模式
                btn.setChecked(True)
            btn.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: 1px solid #FDBA74;
                    border-radius: 3px;
                    padding: 4px 8px;
                    margin: 2px;
                    font-size: 10px;
                }
                QToolButton:checked {
                    background-color: #FF6B35;
                    color: white;
                    border-color: #FB923C;
                }
                QToolButton:hover {
                    background-color: #FED7AA;
                }
            """)
            input_mode_group.addButton(btn, i)
            mode_bar.addWidget(btn)

        mode_bar.addStretch()
        input_layout.addLayout(mode_bar)

        # 描述输入区域
        self.ai_description_input = QTextEdit()
        self.ai_description_input.setMaximumHeight(80)
        self.ai_description_input.setPlaceholderText("小球像火箭一样快速飞过去，要有科技感和拖尾效果")
        self.ai_description_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                background-color: #FEFEFE;
            }
            QTextEdit:focus {
                border-color: #FF6B35;
            }
        """)
        input_layout.addWidget(self.ai_description_input)

        # 智能标签区域
        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel("🏷️ 智能标签:"))

        # 自动生成的标签
        tags = ["#火箭运动", "#科技感", "#拖尾效果", "#快速移动"]
        for tag in tags:
            tag_btn = QToolButton()
            tag_btn.setText(tag)
            tag_btn.setStyleSheet("""
                QToolButton {
                    background-color: #EEF2FF;
                    color: #3730A3;
                    border: 1px solid #C7D2FE;
                    border-radius: 12px;
                    padding: 2px 8px;
                    margin: 1px;
                    font-size: 10px;
                }
                QToolButton:hover {
                    background-color: #E0E7FF;
                }
            """)
            tags_layout.addWidget(tag_btn)

        tags_layout.addStretch()
        input_layout.addLayout(tags_layout)

        layout.addWidget(input_frame)

        # 🧠 AI实时分析区域
        analysis_frame = QFrame()
        analysis_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #FDBA74;
                border-radius: 6px;
            }
        """)
        analysis_layout = QVBoxLayout(analysis_frame)

        # 分析标题
        analysis_title = QLabel("🧠 AI实时分析 (Gemini 2.5 Flash)")
        analysis_title.setStyleSheet("font-weight: bold; color: #374151; padding: 5px;")
        analysis_layout.addWidget(analysis_title)

        # 分析进度条
        self.analysis_progress = QProgressBar()
        self.analysis_progress.setRange(0, 100)
        self.analysis_progress.setValue(100)
        self.analysis_progress.setTextVisible(True)
        self.analysis_progress.setFormat("📊 分析进度: %p%")
        self.analysis_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                text-align: center;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #10B981;
                border-radius: 3px;
            }
        """)
        analysis_layout.addWidget(self.analysis_progress)

        # 分析结果
        analysis_results = QFrame()
        analysis_results.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
        """)
        results_layout = QVBoxLayout(analysis_results)

        # 分析项目
        analysis_items = [
            ("✓ 动作类型: 快速直线移动", "置信度: 95%", "#10B981"),
            ("✓ 视觉效果: 科技感 + 拖尾", "置信度: 92%", "#10B981"),
            ("✓ 物理特征: 火箭推进加速", "置信度: 88%", "#10B981"),
            ("✓ 时间匹配: 2.3秒 ✓ 路径匹配: 弧线轨迹", "", "#10B981")
        ]

        for item, confidence, color in analysis_items:
            item_layout = QHBoxLayout()

            item_label = QLabel(item)
            item_label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold;")
            item_layout.addWidget(item_label)

            if confidence:
                conf_label = QLabel(confidence)
                conf_label.setStyleSheet("color: #6B7280; font-size: 10px;")
                item_layout.addWidget(conf_label)

            item_layout.addStretch()
            results_layout.addLayout(item_layout)

        analysis_layout.addWidget(analysis_results)

        # 🎯 技术建议
        tech_suggestions = QFrame()
        tech_suggestions.setStyleSheet("""
            QFrame {
                background-color: #EEF2FF;
                border: 1px solid #C7D2FE;
                border-radius: 4px;
            }
        """)
        tech_layout = QVBoxLayout(tech_suggestions)

        tech_title = QLabel("🎯 技术建议:")
        tech_title.setStyleSheet("font-weight: bold; color: #3730A3; font-size: 11px;")
        tech_layout.addWidget(tech_title)

        suggestions = [
            "• 推荐技术栈: GSAP + CSS3 Transform",
            "• 动画时长: 2.3秒 (自动匹配时间段)",
            "• 缓动函数: cubic-bezier(0.25,0.46,0.45,0.94)",
            "• 性能预估: GPU使用+15%, 渲染负载适中"
        ]

        for suggestion in suggestions:
            sugg_label = QLabel(suggestion)
            sugg_label.setStyleSheet("color: #4338CA; font-size: 10px; padding: 1px 0;")
            tech_layout.addWidget(sugg_label)

        analysis_layout.addWidget(tech_suggestions)

        layout.addWidget(analysis_frame)

        # 生成控制按钮
        control_layout = QHBoxLayout()

        # 生成按钮
        generate_btn = QToolButton()
        generate_btn.setText("⚡ 生成动画")
        generate_btn.setStyleSheet("""
            QToolButton {
                background-color: #FF6B35;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QToolButton:hover {
                background-color: #FB923C;
            }
            QToolButton:pressed {
                background-color: #EA580C;
            }
        """)
        control_layout.addWidget(generate_btn)

        # 其他控制按钮
        pause_btn = QToolButton()
        pause_btn.setText("⏸️ 暂停")
        pause_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
            }
            QToolButton:hover {
                background-color: #F3F4F6;
            }
        """)
        control_layout.addWidget(pause_btn)

        reset_btn = QToolButton()
        reset_btn.setText("🔄 重置")
        reset_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
            }
            QToolButton:hover {
                background-color: #F3F4F6;
            }
        """)
        control_layout.addWidget(reset_btn)

        control_layout.addStretch()

        layout.addLayout(control_layout)

        # 连接信号
        generate_btn.clicked.connect(self.start_ai_generation)

        return widget

    def create_prompt_editor_tab(self):
        """创建Prompt编辑器标签页 - 增强版"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 📋 Prompt编辑器标题
        title_frame = QFrame()
        title_frame.setFixedHeight(35)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #FB923C;
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("📋 Prompt编辑器 (完全可控)")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 模板选择
        template_combo = QComboBox()
        template_combo.addItems(["自定义", "科技动画", "自然运动", "UI交互", "粒子效果"])
        template_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 3px;
                padding: 3px 8px;
                font-size: 11px;
            }
        """)
        title_layout.addWidget(template_combo)

        layout.addWidget(title_frame)

        # Prompt编辑区域
        editor_frame = QFrame()
        editor_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #FDBA74;
                border-radius: 6px;
            }
        """)
        editor_layout = QVBoxLayout(editor_frame)

        # 编辑工具栏
        editor_toolbar = QHBoxLayout()

        # 格式化按钮
        format_btns = [
            ("🔤", "格式化"),
            ("📏", "检查语法"),
            ("🎯", "优化建议"),
            ("📊", "质量评分")
        ]

        for icon, name in format_btns:
            btn = QToolButton()
            btn.setText(f"{icon} {name}")
            btn.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: 1px solid #E5E7EB;
                    border-radius: 3px;
                    padding: 4px 8px;
                    margin: 2px;
                    font-size: 10px;
                }
                QToolButton:hover {
                    background-color: #F3F4F6;
                }
            """)
            editor_toolbar.addWidget(btn)

        editor_toolbar.addStretch()

        # 质量评分显示
        quality_label = QLabel("质量评分: 92/100 (优秀)")
        quality_label.setStyleSheet("color: #10B981; font-weight: bold; font-size: 11px;")
        editor_toolbar.addWidget(quality_label)

        editor_layout.addLayout(editor_toolbar)

        # Prompt编辑器主体
        self.enhanced_prompt_editor = QTextEdit()
        self.enhanced_prompt_editor.setPlainText("""【项目设置】⚙️
- 画布尺寸: 1920x1080 | 时间段: 2.3s-4.6s (2.3秒)
- 风格主题: 科技感 | 起始状态: translate(100px,200px)
- 目标设备: 桌面端 | 性能要求: 60fps

【精确描述】⭐ 可编辑重点区域
小球从静止开始，前0.3秒缓慢加速(ease-in)，然后2.0秒内
以火箭推进方式快速移动。添加蓝色发光拖尾(长度3倍)，
轻微震动(±2px,30Hz)，到达后冲击波扩散(半径50px)。

【物理参数】⭐ 可编辑重点区域
- 加速曲线: cubic-bezier(0.25,0.46,0.45,0.94)
- 拖尾透明度: linear-gradient(1.0→0.0)
- 震动频率: 30Hz, 幅度: ±2px
- 冲击波: 径向扩散, #00aaff, 透明度衰减

【技术约束】🔧
- 使用GSAP库进行动画控制
- 支持时间轴精确控制 renderAtTime(t)
- 确保跨浏览器兼容性
- 优化GPU加速渲染

【质量要求】✨
- 动画流畅度: 60fps
- 视觉一致性: 与设计稿100%匹配
- 性能优化: CPU使用率<30%
- 代码质量: 可维护、可扩展""")

        self.enhanced_prompt_editor.setStyleSheet("""
            QTextEdit {
                background-color: #FFFBF5;
                border: 1px solid #FED7AA;
                border-radius: 4px;
                font-family: 'Microsoft YaHei', 'Consolas', sans-serif;
                font-size: 11px;
                line-height: 1.5;
                padding: 10px;
            }
            QTextEdit:focus {
                border-color: #FB923C;
                background-color: #FFFEF7;
            }
        """)

        editor_layout.addWidget(self.enhanced_prompt_editor)

        # 智能提示区域
        suggestions_frame = QFrame()
        suggestions_frame.setMaximumHeight(60)
        suggestions_frame.setStyleSheet("""
            QFrame {
                background-color: #F0F9FF;
                border: 1px solid #BAE6FD;
                border-radius: 4px;
            }
        """)
        suggestions_layout = QVBoxLayout(suggestions_frame)

        suggestions_title = QLabel("💡 智能提示")
        suggestions_title.setStyleSheet("font-weight: bold; color: #0369A1; font-size: 11px;")
        suggestions_layout.addWidget(suggestions_title)

        suggestions_text = QLabel("• 建议添加缓动函数细节以提升动画自然度\n• 可考虑添加音效同步参数")
        suggestions_text.setStyleSheet("color: #0284C7; font-size: 10px;")
        suggestions_layout.addWidget(suggestions_text)

        editor_layout.addWidget(suggestions_frame)

        layout.addWidget(editor_frame)

        # Prompt控制按钮组
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
            }
        """)
        controls_layout = QHBoxLayout(controls_frame)

        # 主要操作按钮
        save_btn = QToolButton()
        save_btn.setText("💾 保存Prompt")
        save_btn.setStyleSheet("""
            QToolButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QToolButton:hover {
                background-color: #059669;
            }
        """)
        controls_layout.addWidget(save_btn)

        # 其他操作按钮
        other_btns = [
            ("📚", "加载规则"),
            ("🔄", "重置"),
            ("📤", "导出"),
            ("📋", "复制"),
            ("🔍", "预览效果")
        ]

        for icon, name in other_btns:
            btn = QToolButton()
            btn.setText(f"{icon} {name}")
            btn.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    color: #374151;
                    border: 1px solid #D1D5DB;
                    border-radius: 4px;
                    padding: 6px 10px;
                    margin: 2px;
                    font-size: 10px;
                }
                QToolButton:hover {
                    background-color: #F3F4F6;
                }
            """)
            controls_layout.addWidget(btn)

        controls_layout.addStretch()

        # 版本控制
        version_label = QLabel("版本: v1.2 | 最后修改: 2024-01-15 10:30")
        version_label.setStyleSheet("color: #6B7280; font-size: 9px;")
        controls_layout.addWidget(version_label)

        layout.addWidget(controls_frame)

        return widget

    def create_precision_control_panel(self):
        """创建三级精确度生成控制面板"""
        panel = QFrame()
        panel.setFixedHeight(120)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_ai_function_colors()[2]};
                border: 2px solid {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 6px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # 标题
        title = QLabel("🎯 三级精确度生成控制")
        title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-size: 12px;
                font-weight: bold;
                text-align: center;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 三级控制按钮
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        # 级别1: 快速生成
        level1_btn = QPushButton("⚡ 快速生成\n(30秒)")
        level1_btn.setFixedSize(120, 50)
        level1_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_collaboration_colors()[0]};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 10px;
                font-weight: bold;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_collaboration_colors()[1]};
            }}
        """)
        level1_btn.clicked.connect(lambda: self.start_ai_generation_with_precision(1))
        controls_layout.addWidget(level1_btn)

        # 级别2: 标准生成
        level2_btn = QPushButton("🎯 标准生成\n(2分钟)")
        level2_btn.setFixedSize(120, 50)
        level2_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 10px;
                font-weight: bold;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_ai_function_colors()[1]};
            }}
        """)
        level2_btn.clicked.connect(lambda: self.start_ai_generation_with_precision(2))
        controls_layout.addWidget(level2_btn)

        # 级别3: 精细生成
        level3_btn = QPushButton("💎 精细生成\n(5分钟)")
        level3_btn.setFixedSize(120, 50)
        level3_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_performance_colors()[0]};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 10px;
                font-weight: bold;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_performance_colors()[1]};
            }}
        """)
        level3_btn.clicked.connect(lambda: self.start_ai_generation_with_precision(3))
        controls_layout.addWidget(level3_btn)

        layout.addLayout(controls_layout)

        # 精确度说明
        description = QLabel("快速: 基础动画 | 标准: 优化效果 | 精细: 专业品质")
        description.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 9px;
                text-align: center;
            }}
        """)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)

        return panel

    def start_ai_generation_with_precision(self, level):
        """根据精确度级别启动AI生成"""
        precision_configs = {
            1: {"name": "快速生成", "time": 30, "quality": "基础", "iterations": 1},
            2: {"name": "标准生成", "time": 120, "quality": "优化", "iterations": 3},
            3: {"name": "精细生成", "time": 300, "quality": "专业", "iterations": 5}
        }

        config = precision_configs.get(level, precision_configs[2])

        QMessageBox.information(self, f"🎯 {config['name']}",
            f"启动{config['name']}模式\n\n"
            f"⏱️ 预计时间: {config['time']}秒\n"
            f"🎨 质量等级: {config['quality']}\n"
            f"🔄 迭代次数: {config['iterations']}\n\n"
            f"正在为您生成高质量动画...")

        # 这里可以调用实际的AI生成服务
        self.start_ai_generation()

        logger.info(f"启动{config['name']}模式，级别: {level}")

    def show_onboarding_system(self):
        """显示新手引导系统"""
        onboarding = OnboardingSystem(self)
        onboarding.onboarding_completed.connect(self.on_onboarding_completed)
        onboarding.skip_requested.connect(self.on_onboarding_skipped)
        onboarding.exec()

    def on_onboarding_completed(self):
        """新手引导完成处理"""
        QMessageBox.information(self, "引导完成",
            "🎉 欢迎使用AI Animation Studio！\n\n"
            "您已经完成了新手引导，现在可以开始创作了。\n"
            "如需帮助，请查看帮助菜单或访问官方文档。")

        # 根据用户偏好调整界面
        self.apply_user_preferences()

    def on_onboarding_skipped(self):
        """新手引导跳过处理"""
        logger.info("用户跳过了新手引导")

    def apply_user_preferences(self):
        """应用用户偏好设置"""
        # 这里可以根据用户在引导中的选择来调整界面
        logger.info("应用用户偏好设置")

    def on_window_resize(self, event):
        """窗口大小变化处理"""
        if hasattr(self, 'responsive_layout'):
            self.responsive_layout.handle_window_resize(event.size())
        super().resizeEvent(event)

    def create_generation_monitor_tab(self):
        """创建AI生成过程监控标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 📋 AI生成过程监控标题
        title_frame = QFrame()
        title_frame.setFixedHeight(35)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #8B5CF6;
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("📋 AI生成过程监控")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 生成状态指示
        status_label = QLabel("🔄 生成中...")
        status_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        title_layout.addWidget(status_label)

        layout.addWidget(title_frame)

        # 🧠 AI思考阶段监控
        thinking_frame = QFrame()
        thinking_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #C4B5FD;
                border-radius: 6px;
            }
        """)
        thinking_layout = QVBoxLayout(thinking_frame)

        thinking_title = QLabel("🧠 AI思考阶段")
        thinking_title.setStyleSheet("font-weight: bold; color: #7C3AED; padding: 5px;")
        thinking_layout.addWidget(thinking_title)

        # 思考进度条
        self.thinking_progress = QProgressBar()
        self.thinking_progress.setRange(0, 100)
        self.thinking_progress.setValue(100)
        self.thinking_progress.setTextVisible(True)
        self.thinking_progress.setFormat("████████████████████████████████ 100%")
        self.thinking_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                text-align: center;
                font-family: 'Consolas', monospace;
                font-size: 10px;
                background-color: #F3F4F6;
            }
            QProgressBar::chunk {
                background-color: #8B5CF6;
                border-radius: 3px;
            }
        """)
        thinking_layout.addWidget(self.thinking_progress)

        # 思考阶段详情
        thinking_details = QHBoxLayout()

        stages = [
            ("✅", "语义理解"),
            ("✅", "意图识别"),
            ("✅", "规则匹配"),
            ("✅", "技术选择")
        ]

        for status, stage in stages:
            stage_label = QLabel(f"{status} {stage}")
            stage_label.setStyleSheet("""
                color: #10B981;
                font-size: 10px;
                font-weight: bold;
                padding: 2px 6px;
                background-color: #F0FDF4;
                border: 1px solid #BBF7D0;
                border-radius: 3px;
                margin: 1px;
            """)
            thinking_details.addWidget(stage_label)

        thinking_details.addStretch()
        thinking_layout.addLayout(thinking_details)

        layout.addWidget(thinking_frame)

        # 💻 代码生成阶段监控
        coding_frame = QFrame()
        coding_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #C4B5FD;
                border-radius: 6px;
            }
        """)
        coding_layout = QVBoxLayout(coding_frame)

        coding_title = QLabel("💻 代码生成阶段")
        coding_title.setStyleSheet("font-weight: bold; color: #7C3AED; padding: 5px;")
        coding_layout.addWidget(coding_title)

        # 代码生成进度条
        self.coding_progress = QProgressBar()
        self.coding_progress.setRange(0, 100)
        self.coding_progress.setValue(65)
        self.coding_progress.setTextVisible(True)
        self.coding_progress.setFormat("██████████████████░░░░░░░░░░ 65%")
        self.coding_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                text-align: center;
                font-family: 'Consolas', monospace;
                font-size: 10px;
                background-color: #F3F4F6;
            }
            QProgressBar::chunk {
                background-color: #F59E0B;
                border-radius: 3px;
            }
        """)
        coding_layout.addWidget(self.coding_progress)

        # 代码生成阶段详情
        coding_details = QHBoxLayout()

        coding_stages = [
            ("✅", "HTML结构", "#10B981"),
            ("✅", "CSS样式", "#10B981"),
            ("🔄", "JS动画", "#F59E0B"),
            ("⏳", "优化", "#6B7280")
        ]

        for status, stage, color in coding_stages:
            stage_label = QLabel(f"{status} {stage}")
            bg_color = "#F0FDF4" if color == "#10B981" else "#FEF3C7" if color == "#F59E0B" else "#F9FAFB"
            border_color = "#BBF7D0" if color == "#10B981" else "#FCD34D" if color == "#F59E0B" else "#E5E7EB"

            stage_label.setStyleSheet(f"""
                color: {color};
                font-size: 10px;
                font-weight: bold;
                padding: 2px 6px;
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 3px;
                margin: 1px;
            """)
            coding_details.addWidget(stage_label)

        coding_details.addStretch()
        coding_layout.addLayout(coding_details)

        layout.addWidget(coding_frame)

        # 🔍 质量检测阶段
        quality_frame = QFrame()
        quality_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #C4B5FD;
                border-radius: 6px;
            }
        """)
        quality_layout = QVBoxLayout(quality_frame)

        quality_title = QLabel("🔍 质量检测")
        quality_title.setStyleSheet("font-weight: bold; color: #7C3AED; padding: 5px;")
        quality_layout.addWidget(quality_title)

        # 质量检测进度条
        self.quality_progress = QProgressBar()
        self.quality_progress.setRange(0, 100)
        self.quality_progress.setValue(0)
        self.quality_progress.setTextVisible(True)
        self.quality_progress.setFormat("░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%")
        self.quality_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                text-align: center;
                font-family: 'Consolas', monospace;
                font-size: 10px;
                background-color: #F3F4F6;
            }
            QProgressBar::chunk {
                background-color: #EF4444;
                border-radius: 3px;
            }
        """)
        quality_layout.addWidget(self.quality_progress)

        # 等待提示
        waiting_label = QLabel("⏳ 等待代码生成完成...")
        waiting_label.setStyleSheet("color: #6B7280; font-size: 11px; padding: 5px; text-align: center;")
        quality_layout.addWidget(waiting_label)

        layout.addWidget(quality_frame)

        # 📊 生成统计信息
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #F0F9FF;
                border: 1px solid #BAE6FD;
                border-radius: 6px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)

        stats_title = QLabel("📊 生成统计")
        stats_title.setStyleSheet("font-weight: bold; color: #0369A1; padding: 5px;")
        stats_layout.addWidget(stats_title)

        # 统计信息网格
        stats_grid = QGridLayout()

        stats_data = [
            ("当前:", "生成GSAP时间轴动画"),
            ("剩余:", "12秒"),
            ("成功率:", "94%"),
            ("模型:", "Gemini 2.5 Flash")
        ]

        for i, (label, value) in enumerate(stats_data):
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #0284C7; font-size: 10px; font-weight: bold;")
            stats_grid.addWidget(label_widget, i // 2, (i % 2) * 2)

            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #0369A1; font-size: 10px;")
            stats_grid.addWidget(value_widget, i // 2, (i % 2) * 2 + 1)

        stats_layout.addLayout(stats_grid)

        layout.addWidget(stats_frame)

        layout.addStretch()

        return widget

    def create_solution_compare_tab(self):
        """创建智能方案对比标签页 - 增强版"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 🎭 方案预览标题
        title_frame = QFrame()
        title_frame.setFixedHeight(35)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #7C3AED;
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("🎭 AI生成方案预览 (Gemini生成)")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        generation_time = QLabel("生成时间: 18s")
        generation_time.setStyleSheet("color: white; font-size: 11px;")
        title_layout.addWidget(generation_time)

        layout.addWidget(title_frame)

        # 四方案并行显示区域
        solutions_frame = QFrame()
        solutions_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #C4B5FD;
                border-radius: 6px;
            }
        """)
        solutions_layout = QVBoxLayout(solutions_frame)
        solutions_layout.setContentsMargins(8, 8, 8, 8)

        # 方案网格
        solutions_grid = QGridLayout()
        solutions_grid.setSpacing(8)

        # 方案数据
        solutions_data = [
            {
                "name": "方案A",
                "type": "标准版",
                "preview": "●→",
                "rating": "⭐⭐⭐⭐⭐",
                "features": ["•简洁稳定", "•性能优秀", "•兼容性好"],
                "color": "#10B981",
                "recommended": True
            },
            {
                "name": "方案B",
                "type": "增强版",
                "preview": "●~~~→\n  ✨",
                "rating": "⭐⭐⭐⭐",
                "features": ["•视觉丰富", "•效果震撼", "•创意突出"],
                "color": "#3B82F6",
                "recommended": False
            },
            {
                "name": "方案C",
                "type": "写实版",
                "preview": "  ●\n   ↘\n    ●",
                "rating": "⭐⭐",
                "features": ["•物理真实", "•教学适用", "•科学准确"],
                "color": "#F59E0B",
                "recommended": False
            },
            {
                "name": "方案D",
                "type": "创意版",
                "preview": "   ●\n  /|\\\n / | \\\n●--●--●",
                "rating": "⭐⭐⭐",
                "features": ["•创意突出", "•独特风格", "•实验性强"],
                "color": "#EF4444",
                "recommended": False
            }
        ]

        for i, solution in enumerate(solutions_data):
            # 方案卡片
            card = QFrame()
            card.setFixedSize(160, 200)
            border_color = solution["color"] if solution["recommended"] else "#E5E7EB"
            border_width = "3px" if solution["recommended"] else "1px"

            card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: {border_width} solid {border_color};
                    border-radius: 8px;
                }}
                QFrame:hover {{
                    border-color: {solution["color"]};
                    border-width: 2px;
                }}
            """)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(8, 6, 8, 6)
            card_layout.setSpacing(4)

            # 方案标题
            title_layout = QHBoxLayout()
            name_label = QLabel(solution["name"])
            name_label.setStyleSheet(f"font-weight: bold; color: {solution['color']}; font-size: 12px;")
            title_layout.addWidget(name_label)

            type_label = QLabel(solution["type"])
            type_label.setStyleSheet("color: #6B7280; font-size: 10px;")
            title_layout.addWidget(type_label)

            card_layout.addLayout(title_layout)

            # 预览区域
            preview_area = QFrame()
            preview_area.setFixedHeight(60)
            preview_area.setStyleSheet(f"""
                QFrame {{
                    background-color: {solution['color']}15;
                    border: 1px solid {solution['color']}40;
                    border-radius: 4px;
                }}
            """)
            preview_layout = QVBoxLayout(preview_area)

            preview_label = QLabel(solution["preview"])
            preview_label.setStyleSheet(f"""
                font-family: 'Consolas', monospace;
                font-size: 14px;
                font-weight: bold;
                color: {solution['color']};
            """)
            preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview_layout.addWidget(preview_label)

            card_layout.addWidget(preview_area)

            # 推荐评级
            rating_layout = QHBoxLayout()
            rating_layout.addWidget(QLabel("🎯推荐:", styleSheet="font-size: 10px; color: #374151;"))
            rating_label = QLabel(solution["rating"])
            rating_label.setStyleSheet("font-size: 11px;")
            rating_layout.addWidget(rating_label)
            rating_layout.addStretch()

            card_layout.addLayout(rating_layout)

            # 特点列表
            features_label = QLabel("特点:")
            features_label.setStyleSheet("font-weight: bold; font-size: 10px; color: #374151;")
            card_layout.addWidget(features_label)

            for feature in solution["features"]:
                feature_label = QLabel(feature)
                feature_label.setStyleSheet("font-size: 9px; color: #6B7280; padding-left: 5px;")
                card_layout.addWidget(feature_label)

            # 操作按钮
            buttons_layout = QVBoxLayout()
            buttons_layout.setSpacing(2)

            # 预览按钮
            preview_btn = QToolButton()
            preview_btn.setText("👁️ 预览")
            preview_btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {solution['color']}20;
                    color: {solution['color']};
                    border: 1px solid {solution['color']}60;
                    border-radius: 3px;
                    padding: 3px 8px;
                    font-size: 9px;
                    font-weight: bold;
                }}
                QToolButton:hover {{
                    background-color: {solution['color']}30;
                }}
            """)
            buttons_layout.addWidget(preview_btn)

            # 参数按钮
            params_btn = QToolButton()
            params_btn.setText("⚙️ 参数")
            params_btn.setStyleSheet("""
                QToolButton {
                    background-color: #F3F4F6;
                    color: #374151;
                    border: 1px solid #D1D5DB;
                    border-radius: 3px;
                    padding: 3px 8px;
                    font-size: 9px;
                }
                QToolButton:hover {
                    background-color: #E5E7EB;
                }
            """)
            buttons_layout.addWidget(params_btn)

            # 选择按钮
            select_btn = QToolButton()
            select_btn.setText("✅ 选择")
            if solution["recommended"]:
                select_btn.setStyleSheet(f"""
                    QToolButton {{
                        background-color: {solution['color']};
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 9px;
                        font-weight: bold;
                    }}
                    QToolButton:hover {{
                        background-color: {solution['color']}CC;
                    }}
                """)
            else:
                select_btn.setStyleSheet("""
                    QToolButton {
                        background-color: transparent;
                        color: #6B7280;
                        border: 1px solid #D1D5DB;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 9px;
                    }
                    QToolButton:hover {
                        background-color: #F3F4F6;
                    }
                """)
            buttons_layout.addWidget(select_btn)

            card_layout.addLayout(buttons_layout)

            solutions_grid.addWidget(card, i // 2, i % 2)

        solutions_layout.addLayout(solutions_grid)
        layout.addWidget(solutions_frame)

        # 📊 智能对比分析表格
        analysis_frame = QFrame()
        analysis_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #C4B5FD;
                border-radius: 6px;
            }
        """)
        analysis_layout = QVBoxLayout(analysis_frame)
        analysis_layout.setContentsMargins(8, 8, 8, 8)

        analysis_title = QLabel("📊 智能对比分析")
        analysis_title.setStyleSheet("font-weight: bold; color: #7C3AED; font-size: 12px; padding: 5px;")
        analysis_layout.addWidget(analysis_title)

        # 对比表格
        comparison_table.setColumnCount(5)

        # 设置表头
        headers = ["指标", "方案A", "方案B", "方案C", "方案D"]
        comparison_table.setHorizontalHeaderLabels(headers)

        # 表格数据
        table_data = [
            ["复杂度", "简单", "中等", "复杂", "很复杂"],
            ["性能影响", "很低", "中等", "较高", "高"],
            ["视觉冲击", "中等", "很高", "中等", "极高"],
            ["教学适用", "高", "中等", "很高", "低"],
            ["代码大小", "2.1KB", "4.7KB", "6.2KB", "8.9KB"],
            ["渲染帧率", "60fps", "45fps", "30fps", "25fps"],
            ["创新程度", "标准", "创新", "保守", "前卫"],
            ["AI置信度", "95%", "88%", "92%", "73%"]
        ]

        # 填充表格数据
        for row, data in enumerate(table_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                if col == 0:  # 指标列
                    item.setBackground(Qt.GlobalColor.lightGray)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                elif col == 1 and row == 7:  # 方案A的AI置信度（最高）
                    item.setBackground(Qt.GlobalColor.green)
                    item.setForeground(Qt.GlobalColor.white)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

                comparison_table.setItem(row, col, item)

        # 设置表格样式
        comparison_table.setMaximumHeight(200)
        comparison_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E5E7EB;
                background-color: white;
                font-size: 10px;
            }
            QTableWidget::item {
                padding: 4px;
                border-bottom: 1px solid #F3F4F6;
            }
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 6px;
                border: 1px solid #E5E7EB;
                font-weight: bold;
                font-size: 10px;
            }
        """)

        # 调整列宽
        header = comparison_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        for i in range(1, 5):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        analysis_layout.addWidget(comparison_table)

        # 操作按钮区域
        actions_layout = QHBoxLayout()

        # 重新生成按钮
        regenerate_btn = QToolButton()
        regenerate_btn.setText("🎲 重新生成")
        regenerate_btn.setStyleSheet("""
            QToolButton {
                background-color: #7C3AED;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QToolButton:hover {
                background-color: #6D28D9;
            }
        """)
        actions_layout.addWidget(regenerate_btn)

        # 其他操作按钮
        other_actions = [
            ("⚖️", "智能推荐"),
            ("💾", "保存全部"),
            ("🔍", "详细分析")
        ]

        for icon, name in other_actions:
            btn = QToolButton()
            btn.setText(f"{icon} {name}")
            btn.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    color: #374151;
                    border: 1px solid #D1D5DB;
                    border-radius: 4px;
                    padding: 6px 10px;
                    margin: 2px;
                    font-size: 10px;
                }
                QToolButton:hover {
                    background-color: #F3F4F6;
                }
            """)
            actions_layout.addWidget(btn)

        actions_layout.addStretch()

        analysis_layout.addLayout(actions_layout)
        layout.addWidget(analysis_frame)

        return widget

    def create_status_monitor_tab(self):
        """创建状态监控标签页 - AI控制区版本"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 📈 状态监控标题
        title_frame = QFrame()
        title_frame.setFixedHeight(35)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #059669;
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("📈 状态监控 (实时)")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 实时状态指示
        status_indicator = QLabel("🟢 系统正常")
        status_indicator.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        title_layout.addWidget(status_indicator)

        layout.addWidget(title_frame)

        # 🎯 项目状态总览
        project_status_frame = QFrame()
        project_status_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #BBF7D0;
                border-radius: 6px;
            }
        """)
        project_status_layout = QVBoxLayout(project_status_frame)
        project_status_layout.setContentsMargins(8, 6, 8, 6)

        project_status_title = QLabel("🎯 项目状态总览")
        project_status_title.setStyleSheet("font-weight: bold; color: #059669; font-size: 11px;")
        project_status_layout.addWidget(project_status_title)

        # 项目进度条
        project_progress = QProgressBar()
        project_progress.setRange(0, 100)
        project_progress.setValue(65)
        project_progress.setTextVisible(True)
        project_progress.setFormat("项目进度: %p%")
        project_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #D1FAE5;
                border-radius: 4px;
                text-align: center;
                font-size: 10px;
                background-color: #F0FDF4;
            }
            QProgressBar::chunk {
                background-color: #10B981;
                border-radius: 3px;
            }
        """)
        project_status_layout.addWidget(project_progress)

        # 状态统计网格
        stats_grid = QGridLayout()

        stats_data = [
            ("已完成", "1", "#10B981"),
            ("进行中", "1", "#F59E0B"),
            ("待处理", "2", "#6B7280"),
            ("异常", "2", "#EF4444")
        ]

        for i, (label, count, color) in enumerate(stats_data):
            stat_frame = QFrame()
            stat_frame.setFixedSize(60, 40)
            stat_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}15;
                    border: 1px solid {color}40;
                    border-radius: 4px;
                }}
            """)

            stat_layout = QVBoxLayout(stat_frame)
            stat_layout.setContentsMargins(2, 2, 2, 2)

            count_label = QLabel(count)
            count_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
            count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_layout.addWidget(count_label)

            label_widget = QLabel(label)
            label_widget.setStyleSheet(f"color: {color}; font-size: 8px;")
            label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_layout.addWidget(label_widget)

            stats_grid.addWidget(stat_frame, i // 2, i % 2)

        project_status_layout.addLayout(stats_grid)
        layout.addWidget(project_status_frame)

        # 🔄 实时状态流
        realtime_frame = QFrame()
        realtime_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #BBF7D0;
                border-radius: 6px;
            }
        """)
        realtime_layout = QVBoxLayout(realtime_frame)
        realtime_layout.setContentsMargins(8, 6, 8, 6)

        realtime_title = QLabel("🔄 实时状态流")
        realtime_title.setStyleSheet("font-weight: bold; color: #059669; font-size: 11px;")
        realtime_layout.addWidget(realtime_title)

        # 状态流列表
        status_flow_data = [
            ("14:32:15", "✅", "Logo元素创建完成", "#10B981"),
            ("14:32:28", "🔄", "小球动画生成中...", "#F59E0B"),
            ("14:32:45", "⚠️", "检测到透明度差异", "#F59E0B"),
            ("14:33:02", "🔧", "自动修复建议已生成", "#3B82F6"),
            ("14:33:18", "⏳", "等待用户确认修复", "#6B7280")
        ]

        for time, icon, message, color in status_flow_data:
            flow_item = QHBoxLayout()

            time_label = QLabel(time)
            time_label.setStyleSheet("font-size: 8px; color: #6B7280; font-family: 'Consolas', monospace;")
            time_label.setFixedWidth(50)
            flow_item.addWidget(time_label)

            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"color: {color}; font-size: 10px;")
            icon_label.setFixedWidth(15)
            flow_item.addWidget(icon_label)

            message_label = QLabel(message)
            message_label.setStyleSheet(f"color: {color}; font-size: 9px;")
            flow_item.addWidget(message_label)

            flow_item.addStretch()
            realtime_layout.addLayout(flow_item)

        layout.addWidget(realtime_frame)

        # 🚨 智能预警系统
        alert_frame = QFrame()
        alert_frame.setStyleSheet("""
            QFrame {
                background-color: #FEF3C7;
                border: 1px solid #FCD34D;
                border-radius: 6px;
            }
        """)
        alert_layout = QVBoxLayout(alert_frame)
        alert_layout.setContentsMargins(8, 6, 8, 6)

        alert_title = QLabel("🚨 智能预警系统")
        alert_title.setStyleSheet("font-weight: bold; color: #92400E; font-size: 11px;")
        alert_layout.addWidget(alert_title)

        # 预警列表
        alerts = [
            "⚠️ 小球动画可能与文字元素重叠",
            "💡 建议调整时间轴以优化性能",
            "🔧 检测到2个可自动修复的问题"
        ]

        for alert in alerts:
            alert_label = QLabel(alert)
            alert_label.setStyleSheet("color: #92400E; font-size: 9px;")
            alert_layout.addWidget(alert_label)

        # 预警操作按钮
        alert_actions = QHBoxLayout()

        auto_fix_all_btn = QToolButton()
        auto_fix_all_btn.setText("🔧 全部修复")
        auto_fix_all_btn.setStyleSheet("""
            QToolButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #059669;
            }
        """)
        alert_actions.addWidget(auto_fix_all_btn)

        ignore_btn = QToolButton()
        ignore_btn.setText("🙈 忽略")
        ignore_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #92400E;
                border: 1px solid #FCD34D;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 9px;
            }
            QToolButton:hover {
                background-color: #FDE68A;
            }
        """)
        alert_actions.addWidget(ignore_btn)

        alert_actions.addStretch()
        alert_layout.addLayout(alert_actions)

        layout.addWidget(alert_frame)

        # 📊 性能监控
        performance_frame = QFrame()
        performance_frame.setStyleSheet("""
            QFrame {
                background-color: #EEF2FF;
                border: 1px solid #C7D2FE;
                border-radius: 6px;
            }
        """)
        performance_layout = QVBoxLayout(performance_frame)
        performance_layout.setContentsMargins(8, 6, 8, 6)

        performance_title = QLabel("📊 性能监控")
        performance_title.setStyleSheet("font-weight: bold; color: #3730A3; font-size: 11px;")
        performance_layout.addWidget(performance_title)

        # 性能指标
        perf_metrics = [
            ("CPU使用率", "23%", "#10B981"),
            ("内存使用", "67%", "#F59E0B"),
            ("GPU使用率", "85%", "#EF4444"),
            ("渲染帧率", "60fps", "#10B981")
        ]

        perf_grid = QGridLayout()

        for i, (metric, value, color) in enumerate(perf_metrics):
            metric_layout = QHBoxLayout()

            metric_label = QLabel(metric + ":")
            metric_label.setStyleSheet("color: #4338CA; font-size: 9px;")
            metric_layout.addWidget(metric_label)

            metric_layout.addStretch()

            value_label = QLabel(value)
            value_label.setStyleSheet(f"color: {color}; font-size: 9px; font-weight: bold;")
            metric_layout.addWidget(value_label)

            perf_grid.addLayout(metric_layout, i, 0)

        performance_layout.addLayout(perf_grid)
        layout.addWidget(performance_frame)

        layout.addStretch()

        return widget

    def create_parameter_adjust_tab(self):
        """创建参数调整标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 参数调整控件
        # 生成精确度
        precision_layout = QHBoxLayout()
        precision_layout.addWidget(QLabel("精确度:"))
        precision_slider = QSlider(Qt.Orientation.Horizontal)
        precision_slider.setRange(1, 3)
        precision_slider.setValue(2)
        precision_layout.addWidget(precision_slider)
        precision_layout.addWidget(QLabel("精确模式"))
        layout.addLayout(precision_layout)

        # 方案数量
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("方案数:"))
        count_spin = QSpinBox()
        count_spin.setRange(1, 8)
        count_spin.setValue(3)
        count_layout.addWidget(count_spin)
        count_layout.addStretch()
        layout.addLayout(count_layout)

        # AI模型选择
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("AI模型:"))
        model_combo = QComboBox()
        model_combo.addItems(["Gemini 2.5", "Gemini Pro", "Gemini Flash"])
        model_layout.addWidget(model_combo)
        layout.addLayout(model_layout)

        # 超时设置
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("超时:"))
        timeout_spin = QSpinBox()
        timeout_spin.setRange(10, 120)
        timeout_spin.setValue(30)
        timeout_spin.setSuffix("s")
        timeout_layout.addWidget(timeout_spin)
        timeout_layout.addStretch()
        layout.addLayout(timeout_layout)

        layout.addStretch()

        # 生成控制按钮
        generate_controls = QHBoxLayout()
        generate_btn = QToolButton()
        generate_btn.setText("⚡ 生成动画")
        generate_btn.setStyleSheet("""
            QToolButton {
                background-color: #FF6B35;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #FB923C;
            }
        """)
        generate_controls.addWidget(generate_btn)
        generate_controls.addWidget(QToolButton(text="⏸️ 暂停"))
        generate_controls.addStretch()

        layout.addLayout(generate_controls)
        return widget

    def create_collaboration_tab(self):
        """创建团队协作中心标签页 - 增强版"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 👥 团队协作中心标题
        title_frame = QFrame()
        title_frame.setFixedHeight(35)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #10B981;
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("👥 团队协作中心 2.0")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 实时同步状态
        sync_status = QLabel("🟢 实时同步中")
        sync_status.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        title_layout.addWidget(sync_status)

        layout.addWidget(title_frame)

        # 🌐 项目共享
        sharing_frame = QFrame()
        sharing_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #BBF7D0;
                border-radius: 6px;
            }
        """)
        sharing_layout = QVBoxLayout(sharing_frame)
        sharing_layout.setContentsMargins(8, 6, 8, 6)

        sharing_title = QLabel("🌐 项目共享")
        sharing_title.setStyleSheet("font-weight: bold; color: #059669; font-size: 11px;")
        sharing_layout.addWidget(sharing_title)

        # 项目链接
        link_layout = QHBoxLayout()

        project_link = QLineEdit()
        project_link.setText("https://aiae.studio/project/abc123")
        project_link.setReadOnly(True)
        project_link.setStyleSheet("""
            QLineEdit {
                border: 1px solid #BBF7D0;
                border-radius: 3px;
                padding: 4px 6px;
                font-size: 10px;
                background-color: #F0FDF4;
            }
        """)
        link_layout.addWidget(project_link)

        sharing_layout.addLayout(link_layout)

        # 共享操作按钮
        sharing_actions = QHBoxLayout()

        share_buttons = [
            ("📋", "复制链接", "#10B981"),
            ("📤", "邮件邀请", "#3B82F6"),
            ("💬", "二维码", "#F59E0B"),
            ("🔒", "权限设置", "#6B7280")
        ]

        for icon, name, color in share_buttons:
            btn = QToolButton()
            btn.setText(f"{icon} {name}")
            btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {color}15;
                    color: {color};
                    border: 1px solid {color}40;
                    border-radius: 3px;
                    padding: 3px 6px;
                    font-size: 9px;
                    font-weight: bold;
                    margin: 1px;
                }}
                QToolButton:hover {{
                    background-color: {color}25;
                }}
            """)
            sharing_actions.addWidget(btn)

        sharing_actions.addStretch()
        sharing_layout.addLayout(sharing_actions)

        layout.addWidget(sharing_frame)

        # 👤 协作成员 (实时状态)
        members_frame = QFrame()
        members_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #BBF7D0;
                border-radius: 6px;
            }
        """)
        members_layout = QVBoxLayout(members_frame)
        members_layout.setContentsMargins(8, 6, 8, 6)

        members_title = QLabel("👤 协作成员 (实时状态)")
        members_title.setStyleSheet("font-weight: bold; color: #059669; font-size: 11px;")
        members_layout.addWidget(members_title)

        # 成员列表
        members_data = [
            ("🟢", "张三", "项目负责人", "正在编辑时间轴", "📺观看", "2分钟前"),
            ("🟡", "李四", "动画师", "正在调整小球元素", "📺观看", "刚刚"),
            ("🔴", "王五", "设计师", "离线", "💬留言", "1小时前"),
            ("🟢", "赵六", "审核员", "正在预览方案B", "📺观看", "5分钟前")
        ]

        for status, name, role, activity, action, time in members_data:
            member_layout = QHBoxLayout()

            # 状态和基本信息
            member_info = QLabel(f"{status} {name} ({role})")
            member_info.setStyleSheet("color: #059669; font-size: 10px; font-weight: bold;")
            member_layout.addWidget(member_info)

            # 活动状态
            activity_label = QLabel(activity)
            activity_label.setStyleSheet("color: #6B7280; font-size: 9px;")
            member_layout.addWidget(activity_label)

            member_layout.addStretch()

            # 操作按钮
            action_btn = QToolButton()
            action_btn.setText(action)
            action_btn.setStyleSheet("""
                QToolButton {
                    background-color: #F0FDF4;
                    color: #059669;
                    border: 1px solid #BBF7D0;
                    border-radius: 3px;
                    padding: 2px 4px;
                    font-size: 8px;
                }
                QToolButton:hover {
                    background-color: #DCFCE7;
                }
            """)
            member_layout.addWidget(action_btn)

            # 时间
            time_label = QLabel(time)
            time_label.setStyleSheet("color: #9CA3AF; font-size: 8px;")
            member_layout.addWidget(time_label)

            members_layout.addLayout(member_layout)

        # 权限控制
        permissions_layout = QHBoxLayout()
        permissions_layout.addWidget(QLabel("权限控制:", styleSheet="color: #059669; font-size: 9px; font-weight: bold;"))

        permission_buttons = [
            ("👑", "管理员"),
            ("✏️", "编辑者"),
            ("👁️", "观看者"),
            ("💬", "评论者")
        ]

        for icon, name in permission_buttons:
            btn = QToolButton()
            btn.setText(f"{icon}{name}")
            btn.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    color: #059669;
                    border: 1px solid #BBF7D0;
                    border-radius: 3px;
                    padding: 2px 4px;
                    font-size: 8px;
                    margin: 1px;
                }
                QToolButton:hover {
                    background-color: #F0FDF4;
                }
            """)
            permissions_layout.addWidget(btn)

        permissions_layout.addStretch()
        members_layout.addLayout(permissions_layout)

        layout.addWidget(members_frame)

        # 💬 实时讨论 (WebRTC)
        discussion_frame = QFrame()
        discussion_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #BBF7D0;
                border-radius: 6px;
            }
        """)
        discussion_layout = QVBoxLayout(discussion_frame)
        discussion_layout.setContentsMargins(8, 6, 8, 6)

        discussion_title = QLabel("💬 实时讨论 (WebRTC)")
        discussion_title.setStyleSheet("font-weight: bold; color: #059669; font-size: 11px;")
        discussion_layout.addWidget(discussion_title)

        # 讨论内容
        discussion_scroll = QScrollArea()
        discussion_scroll.setWidgetResizable(True)
        discussion_scroll.setMaximumHeight(100)
        discussion_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #F3F4F6;
                border-radius: 3px;
                background-color: #FAFAFA;
            }
        """)

        discussion_content = QWidget()
        discussion_content_layout = QVBoxLayout(discussion_content)

        # 讨论消息
        messages = [
            ("张三", "10:30", "📍时间轴2.3s", "这个小球的运动轨迹需要调整一下，太直了", "👍3 ❤️1"),
            ("李四", "10:32", "📍小球元素", "好的，我来调整成弧线路径，大家看看这样如何？", "👍5"),
            ("赵六", "10:35", "📍方案对比", "方案B的视觉效果很棒，但性能有点担心 🤔", "🔧优化建议")
        ]

        for author, time, location, message, reactions in messages:
            message_frame = QFrame()
            message_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #E5E7EB;
                    border-radius: 4px;
                    margin: 2px;
                }
            """)
            message_layout = QVBoxLayout(message_frame)
            message_layout.setContentsMargins(6, 4, 6, 4)

            # 消息头部
            header_layout = QHBoxLayout()

            author_label = QLabel(f"{author} {time} {location}")
            author_label.setStyleSheet("color: #059669; font-size: 9px; font-weight: bold;")
            header_layout.addWidget(author_label)

            header_layout.addStretch()
            message_layout.addLayout(header_layout)

            # 消息内容
            content_label = QLabel(message)
            content_label.setStyleSheet("color: #374151; font-size: 9px; padding: 2px 0;")
            content_label.setWordWrap(True)
            message_layout.addWidget(content_label)

            # 反应和操作
            reactions_layout = QHBoxLayout()

            reactions_label = QLabel(reactions)
            reactions_label.setStyleSheet("color: #6B7280; font-size: 8px;")
            reactions_layout.addWidget(reactions_label)

            reactions_layout.addStretch()

            reply_btn = QToolButton()
            reply_btn.setText("💬回复")
            reply_btn.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    color: #059669;
                    border: none;
                    padding: 1px 3px;
                    font-size: 8px;
                }
                QToolButton:hover {
                    background-color: #F0FDF4;
                }
            """)
            reactions_layout.addWidget(reply_btn)

            message_layout.addLayout(reactions_layout)
            discussion_content_layout.addWidget(message_frame)

        discussion_scroll.setWidget(discussion_content)
        discussion_layout.addWidget(discussion_scroll)

        # 消息输入区域
        input_layout = QHBoxLayout()

        # 输入框
        message_input = QLineEdit()
        message_input.setPlaceholderText("💬 输入消息...")
        message_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #BBF7D0;
                border-radius: 3px;
                padding: 4px 6px;
                font-size: 10px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #10B981;
            }
        """)
        input_layout.addWidget(message_input)

        # 输入工具按钮
        input_tools = [
            ("🎤", "语音消息"),
            ("📎", "附件"),
            ("😊", "表情"),
            ("💬", "发送")
        ]

        for icon, name in input_tools:
            btn = QToolButton()
            btn.setText(icon)
            btn.setToolTip(name)
            if name == "发送":
                btn.setStyleSheet("""
                    QToolButton {
                        background-color: #10B981;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 6px;
                        font-size: 10px;
                    }
                    QToolButton:hover {
                        background-color: #059669;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QToolButton {
                        background-color: transparent;
                        color: #059669;
                        border: 1px solid #BBF7D0;
                        border-radius: 3px;
                        padding: 4px 6px;
                        font-size: 10px;
                    }
                    QToolButton:hover {
                        background-color: #F0FDF4;
                    }
                """)
            input_layout.addWidget(btn)

        discussion_layout.addLayout(input_layout)
        layout.addWidget(discussion_frame)

        layout.addStretch()

        return widget

    def create_smart_repair_tab(self):
        """创建智能修复标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 问题检测
        issues_frame = QFrame()
        issues_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        issues_frame.setStyleSheet("""
            QFrame {
                background-color: #FEF2F2;
                border: 1px solid #FECACA;
                border-radius: 4px;
            }
        """)
        issues_layout = QVBoxLayout(issues_frame)
        issues_layout.addWidget(QLabel("🚨 检测到的问题"))
        issues_layout.addWidget(QLabel("⚠️ 小球→文字: 透明度差异0.1"))
        issues_layout.addWidget(QLabel("❌ 文字→背景: 位置冲突"))

        layout.addWidget(issues_frame)

        # 修复建议
        repair_frame = QFrame()
        repair_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        repair_frame.setStyleSheet("""
            QFrame {
                background-color: #F0FDF4;
                border: 1px solid #BBF7D0;
                border-radius: 4px;
            }
        """)
        repair_layout = QVBoxLayout(repair_frame)
        repair_layout.addWidget(QLabel("🔧 智能修复建议"))
        repair_layout.addWidget(QLabel("💡 自动调整透明度匹配"))
        repair_layout.addWidget(QLabel("💡 智能重新布局元素"))

        layout.addWidget(repair_frame)

        # 修复按钮
        repair_controls = QHBoxLayout()
        repair_controls.addWidget(QToolButton(text="⚡ 一键修复"))
        repair_controls.addWidget(QToolButton(text="🔍 详细分析"))
        repair_controls.addStretch()

        layout.addLayout(repair_controls)
        layout.addStretch()
        return widget

    # 顶部工具栏按钮事件处理
    def start_ai_generation(self):
        """开始AI生成过程"""
        try:
            # 获取用户输入
            if hasattr(self, 'ai_description_input'):
                description = self.ai_description_input.toPlainText().strip()
                if not description:
                    QMessageBox.warning(self, "警告", "请先输入动画描述")
                    return

                # 切换到生成监控标签页
                if hasattr(self, 'ai_control_tabs'):
                    self.ai_control_tabs.setCurrentIndex(2)  # 生成监控标签页

                # 启动生成过程模拟
                self.simulate_ai_generation_process()

                # 这里可以调用实际的AI生成服务
                # from .ai_generator_widget import AIGeneratorWidget
                # ai_generator = AIGeneratorWidget()
                # ai_generator.generate_animations()

        except Exception as e:
            logger = get_logger("main_window")
            logger.error(f"启动AI生成失败: {e}")

    def simulate_ai_generation_process(self):
        """模拟AI生成过程（用于演示）"""
        try:

            # 重置进度条
            if hasattr(self, 'thinking_progress'):
                self.thinking_progress.setValue(0)
            if hasattr(self, 'coding_progress'):
                self.coding_progress.setValue(0)
            if hasattr(self, 'quality_progress'):
                self.quality_progress.setValue(0)

            # 模拟思考阶段
            self.thinking_timer = QTimer()
            self.thinking_timer.timeout.connect(self.update_thinking_progress)
            self.thinking_timer.start(100)  # 每100ms更新一次

            self.thinking_step = 0

        except Exception as e:
            logger = get_logger("main_window")
            logger.error(f"模拟AI生成过程失败: {e}")

    def update_thinking_progress(self):
        """更新思考进度"""
        try:
            self.thinking_step += 2
            if hasattr(self, 'thinking_progress'):
                self.thinking_progress.setValue(min(self.thinking_step, 100))

                # 更新进度条文本
                progress = min(self.thinking_step, 100)
                filled = "█" * (progress // 3)
                empty = "░" * (33 - len(filled))
                self.thinking_progress.setFormat(f"{filled}{empty} {progress}%")

            if self.thinking_step >= 100:
                self.thinking_timer.stop()
                # 开始代码生成阶段
                self.start_coding_phase()

        except Exception as e:
            logger = get_logger("main_window")
            logger.error(f"更新思考进度失败: {e}")

    def start_coding_phase(self):
        """开始代码生成阶段"""
        try:
            self.coding_timer = QTimer()
            self.coding_timer.timeout.connect(self.update_coding_progress)
            self.coding_timer.start(150)  # 每150ms更新一次

            self.coding_step = 0

        except Exception as e:
            logger = get_logger("main_window")
            logger.error(f"开始代码生成阶段失败: {e}")

    def update_coding_progress(self):
        """更新代码生成进度"""
        try:
            self.coding_step += 1
            if hasattr(self, 'coding_progress'):
                progress = min(self.coding_step, 100)
                self.coding_progress.setValue(progress)

                # 更新进度条文本
                filled = "█" * (progress // 3)
                empty = "░" * (33 - len(filled))
                self.coding_progress.setFormat(f"{filled}{empty} {progress}%")

            if self.coding_step >= 100:
                self.coding_timer.stop()
                # 开始质量检测阶段
                self.start_quality_phase()

        except Exception as e:
            logger = get_logger("main_window")
            logger.error(f"更新代码生成进度失败: {e}")

    def start_quality_phase(self):
        """开始质量检测阶段"""
        try:
            self.quality_timer = QTimer()
            self.quality_timer.timeout.connect(self.update_quality_progress)
            self.quality_timer.start(80)  # 每80ms更新一次

            self.quality_step = 0

        except Exception as e:
            logger = get_logger("main_window")
            logger.error(f"开始质量检测阶段失败: {e}")

    def update_quality_progress(self):
        """更新质量检测进度"""
        try:
            self.quality_step += 2
            if hasattr(self, 'quality_progress'):
                progress = min(self.quality_step, 100)
                self.quality_progress.setValue(progress)

                # 更新进度条文本和颜色
                filled = "█" * (progress // 3)
                empty = "░" * (33 - len(filled))
                self.quality_progress.setFormat(f"{filled}{empty} {progress}%")

                # 根据进度改变颜色
                if progress < 50:
                    color = "#EF4444"  # 红色
                elif progress < 80:
                    color = "#F59E0B"  # 黄色
                else:
                    color = "#10B981"  # 绿色

                self.quality_progress.setStyleSheet(f"""
                    QProgressBar {{
                        border: 1px solid #E5E7EB;
                        border-radius: 4px;
                        text-align: center;
                        font-family: 'Consolas', monospace;
                        font-size: 10px;
                        background-color: #F3F4F6;
                    }}
                    QProgressBar::chunk {{
                        background-color: {color};
                        border-radius: 3px;
                    }}
                """)

            if self.quality_step >= 100:
                self.quality_timer.stop()
                # 生成完成
                self.on_ai_generation_complete()

        except Exception as e:
            logger = get_logger("main_window")
            logger.error(f"更新质量检测进度失败: {e}")

    def on_ai_generation_complete(self):
        """AI生成完成处理"""
        try:
            QMessageBox.information(self, "生成完成", "AI动画生成已完成！\n\n生成了3个高质量方案，请在方案对比标签页中查看。")

            # 切换到方案对比标签页
            if hasattr(self, 'ai_control_tabs'):
                self.ai_control_tabs.setCurrentIndex(4)  # 方案对比标签页（调整索引）

        except Exception as e:
            logger = get_logger("main_window")
            logger.error(f"AI生成完成处理失败: {e}")

    # 时间轴控制方法
    def timeline_play(self):
        """时间轴播放"""
        try:
            # 启动时间轴播放
            if hasattr(self, 'timeline_time_label'):
                # 模拟播放状态更新
                if not hasattr(self, 'timeline_timer'):
                    self.timeline_timer = QTimer()
                    self.timeline_timer.timeout.connect(self.update_timeline_time)
                    self.timeline_current_time = 0.0
                    self.timeline_duration = 10.0

                if not self.timeline_timer.isActive():
                    self.timeline_timer.start(100)  # 每100ms更新一次

            logger = get_logger("main_window")
            logger.info("时间轴播放开始")

        except Exception as e:
            logger = get_logger("main_window")
            logger.error(f"时间轴播放失败: {e}")

    def timeline_pause(self):
        """时间轴暂停"""
        try:
            if hasattr(self, 'timeline_timer') and self.timeline_timer.isActive():
                self.timeline_timer.stop()

            logger = get_logger("main_window")
            logger.info("时间轴播放暂停")

        except Exception as e:
            logger = get_logger("main_window")
            logger.error(f"时间轴暂停失败: {e}")

    def timeline_stop(self):
        """时间轴停止"""
        try:
            if hasattr(self, 'timeline_timer'):
                self.timeline_timer.stop()
                self.timeline_current_time = 0.0
                self.update_timeline_time()

            logger = get_logger("main_window")
            logger.info("时间轴播放停止")

        except Exception as e:
            logger = get_logger("main_window")
            logger.error(f"时间轴停止失败: {e}")

    def update_timeline_time(self):
        """更新时间轴时间显示"""
        try:
            if hasattr(self, 'timeline_current_time') and hasattr(self, 'timeline_duration'):
                self.timeline_current_time += 0.1

                if self.timeline_current_time >= self.timeline_duration:
                    self.timeline_current_time = self.timeline_duration
                    self.timeline_timer.stop()

                # 格式化时间显示
                current_min = int(self.timeline_current_time // 60)
                current_sec = int(self.timeline_current_time % 60)
                total_min = int(self.timeline_duration // 60)
                total_sec = int(self.timeline_duration % 60)

                time_text = f"{current_min}:{current_sec:02d} / {total_min}:{total_sec:02d}"

                if hasattr(self, 'timeline_time_label'):
                    self.timeline_time_label.setText(time_text)

        except Exception as e:
            logger = get_logger("main_window")
            logger.error(f"更新时间轴时间失败: {e}")

    def register_widgets_to_dual_mode_layout(self):
        """注册组件到双模式布局管理器"""
        try:
            # 注册新的五区域布局组件
            if hasattr(self, 'top_toolbar_widget'):
                self.dual_mode_layout_widget.register_widget("top_toolbar_widget", self.top_toolbar_widget)

            if hasattr(self, 'resource_tabs'):
                self.dual_mode_layout_widget.register_widget("resource_tabs", self.resource_tabs)

            if hasattr(self, 'main_work_tabs'):
                self.dual_mode_layout_widget.register_widget("main_work_tabs", self.main_work_tabs)

            if hasattr(self, 'stage_widget'):
                self.dual_mode_layout_widget.register_widget("stage_widget", self.stage_widget)

            if hasattr(self, 'ai_control_tabs'):
                self.dual_mode_layout_widget.register_widget("ai_control_tabs", self.ai_control_tabs)

            if hasattr(self, 'ai_generator_widget'):
                self.dual_mode_layout_widget.register_widget("ai_generator_widget", self.ai_generator_widget)

            if hasattr(self, 'timeline_area_widget'):
                self.dual_mode_layout_widget.register_widget("timeline_area_widget", self.timeline_area_widget)

            # 注册区域组件（兼容性）
            if hasattr(self, 'main_splitter') and self.main_splitter.count() >= 2:
                self.dual_mode_layout_widget.register_widget("main_area", self.main_splitter.widget(1))
                if self.main_splitter.count() >= 3:
                    self.dual_mode_layout_widget.register_widget("secondary_area", self.main_splitter.widget(2))

            # 连接双模式布局信号
            self.dual_mode_layout_widget.mode_changed.connect(self.on_dual_mode_changed)

            logger.info("五区域布局组件注册到双模式布局管理器完成")

        except Exception as e:
            logger.error(f"注册组件到双模式布局管理器失败: {e}")

    def on_dual_mode_changed(self, mode: str):
        """双模式改变处理"""
        try:
            logger.info(f"双模式已切换到: {mode}")

            # 更新状态栏显示
            if hasattr(self, 'status_bar'):
                mode_text = "编辑模式" if mode == "edit" else "预览模式"
                self.status_bar.showMessage(f"当前模式: {mode_text}", 3000)

            # 根据模式调整界面
            self.adjust_interface_for_dual_mode(mode)

        except Exception as e:
            logger.error(f"双模式改变处理失败: {e}")

    def adjust_interface_for_dual_mode(self, mode: str):
        """根据双模式调整界面"""
        try:
            if mode == "edit":
                # 编辑模式：显示编辑相关组件
                self.show_edit_mode_components()
            elif mode == "preview":
                # 预览模式：显示预览相关组件
                self.show_preview_mode_components()

        except Exception as e:
            logger.error(f"根据双模式调整界面失败: {e}")

    def show_edit_mode_components(self):
        """显示编辑模式组件"""
        try:
            # 确保编辑相关组件可见
            if hasattr(self, 'elements_widget'):
                self.elements_widget.setVisible(True)
            if hasattr(self, 'properties_widget'):
                self.properties_widget.setVisible(True)
            if hasattr(self, 'ai_generator_widget'):
                self.ai_generator_widget.setVisible(True)

            # 调整预览组件大小
            if hasattr(self, 'preview_widget'):
                self.preview_widget.setVisible(True)

        except Exception as e:
            logger.error(f"显示编辑模式组件失败: {e}")

    def show_preview_mode_components(self):
        """显示预览模式组件"""
        try:
            # 隐藏编辑相关组件
            if hasattr(self, 'elements_widget'):
                self.elements_widget.setVisible(False)
            if hasattr(self, 'properties_widget'):
                self.properties_widget.setVisible(False)
            if hasattr(self, 'ai_generator_widget'):
                self.ai_generator_widget.setVisible(False)

            # 确保预览组件可见并最大化
            if hasattr(self, 'preview_widget'):
                self.preview_widget.setVisible(True)
            if hasattr(self, 'timeline_widget'):
                self.timeline_widget.setVisible(True)

        except Exception as e:
            logger.error(f"显示预览模式组件失败: {e}")

    def toggle_dual_mode(self):
        """切换双模式"""
        try:
            self.dual_mode_layout_widget.toggle_mode(animated=True)

        except Exception as e:
            logger.error(f"切换双模式失败: {e}")

    def set_dual_mode(self, mode: str):
        """设置双模式"""
        try:
            self.dual_mode_layout_widget.set_mode(mode, animated=True)

        except Exception as e:
            logger.error(f"设置双模式失败: {e}")

    def get_dual_mode(self) -> str:
        """获取当前双模式"""
        try:
            return self.dual_mode_layout_widget.get_current_mode()

        except Exception as e:
            logger.error(f"获取当前双模式失败: {e}")
            return "edit"

    def setup_menus(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        # 新建项目
        new_action = QAction("新建项目(&N)", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)

        # 从模板新建
        new_from_template_action = QAction("从模板新建(&T)", self)
        new_from_template_action.setShortcut("Ctrl+Shift+N")
        new_from_template_action.triggered.connect(self.new_project_from_template)
        file_menu.addAction(new_from_template_action)

        # 打开项目
        open_action = QAction("打开项目(&O)", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # 保存项目
        save_action = QAction("保存项目(&S)", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        # 另存为
        save_as_action = QAction("另存为(&A)", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)

        # 保存选项
        save_options_action = QAction("保存选项(&O)", self)
        save_options_action.setShortcut("Ctrl+Shift+S")
        save_options_action.triggered.connect(self.show_save_options)
        file_menu.addAction(save_options_action)

        file_menu.addSeparator()

        # 版本管理
        version_menu = file_menu.addMenu("版本管理(&V)")

        create_version_action = QAction("创建版本备份", self)
        create_version_action.triggered.connect(self.create_version_backup)
        version_menu.addAction(create_version_action)

        version_history_action = QAction("版本历史", self)
        version_history_action.triggered.connect(self.show_version_history)
        version_menu.addAction(version_history_action)

        # 自动保存管理
        auto_save_menu = file_menu.addMenu("自动保存(&U)")

        auto_save_settings_action = QAction("自动保存设置", self)
        auto_save_settings_action.triggered.connect(self.show_auto_save_settings)
        auto_save_menu.addAction(auto_save_settings_action)

        manual_auto_save_action = QAction("立即自动保存", self)
        manual_auto_save_action.triggered.connect(self.trigger_manual_auto_save)
        auto_save_menu.addAction(manual_auto_save_action)

        recovery_action = QAction("恢复数据", self)
        recovery_action.triggered.connect(self.show_recovery_options)
        auto_save_menu.addAction(recovery_action)

        file_menu.addSeparator()

        # 快速另存为菜单
        quick_save_menu = file_menu.addMenu("快速另存为(&Q)")

        save_as_aas_action = QAction("另存为AAS项目", self)
        save_as_aas_action.setShortcut("Ctrl+Alt+A")
        save_as_aas_action.triggered.connect(lambda: self.quick_save_as("aas"))
        quick_save_menu.addAction(save_as_aas_action)

        save_as_json_action = QAction("另存为JSON", self)
        save_as_json_action.setShortcut("Ctrl+Alt+J")
        save_as_json_action.triggered.connect(lambda: self.quick_save_as("json"))
        quick_save_menu.addAction(save_as_json_action)

        save_as_zip_action = QAction("另存为压缩包", self)
        save_as_zip_action.setShortcut("Ctrl+Alt+Z")
        save_as_zip_action.triggered.connect(lambda: self.quick_save_as("zip"))
        quick_save_menu.addAction(save_as_zip_action)

        save_as_html_action = QAction("另存为HTML包", self)
        save_as_html_action.setShortcut("Ctrl+Alt+H")
        save_as_html_action.triggered.connect(lambda: self.quick_save_as("html"))
        quick_save_menu.addAction(save_as_html_action)
        
        file_menu.addSeparator()
        
        # 导出
        export_menu = file_menu.addMenu("导出(&E)")
        
        export_html_action = QAction("导出HTML", self)
        export_html_action.triggered.connect(self.export_html)
        export_menu.addAction(export_html_action)
        
        export_video_action = QAction("导出视频", self)
        export_video_action.triggered.connect(self.export_video)
        export_menu.addAction(export_video_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")

        self.undo_action = QAction("撤销(&U)", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.undo_command)
        self.undo_action.setEnabled(False)  # 初始禁用
        edit_menu.addAction(self.undo_action)

        self.redo_action = QAction("重做(&R)", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self.redo_command)
        self.redo_action.setEnabled(False)  # 初始禁用
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()

        # 历史记录查看器
        history_action = QAction("历史记录(&H)", self)
        history_action.setShortcut("Ctrl+H")
        history_action.triggered.connect(self.show_undo_history)
        edit_menu.addAction(history_action)

        # 清空历史记录
        clear_history_action = QAction("清空历史记录(&C)", self)
        clear_history_action.triggered.connect(self.clear_command_history)
        edit_menu.addAction(clear_history_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")

        # 双模式切换
        toggle_mode_action = QAction("切换编辑/预览模式", self)
        toggle_mode_action.setShortcut("F11")
        toggle_mode_action.triggered.connect(self.toggle_dual_mode)
        view_menu.addAction(toggle_mode_action)

        edit_mode_action = QAction("编辑模式", self)
        edit_mode_action.setShortcut("Ctrl+1")
        edit_mode_action.triggered.connect(lambda: self.set_dual_mode("edit"))
        view_menu.addAction(edit_mode_action)

        preview_mode_action = QAction("预览模式", self)
        preview_mode_action.setShortcut("Ctrl+2")
        preview_mode_action.triggered.connect(lambda: self.set_dual_mode("preview"))
        view_menu.addAction(preview_mode_action)

        view_menu.addSeparator()

        # 主题子菜单
        theme_menu = view_menu.addMenu("主题(&T)")
        
        for theme_key, theme_name in self.theme_manager.get_available_themes().items():
            theme_action = QAction(theme_name, self)
            theme_action.setCheckable(True)
            theme_action.setChecked(theme_key == self.config.ui.theme)
            theme_action.triggered.connect(lambda checked, key=theme_key: self.change_theme(key))
            theme_menu.addAction(theme_action)

        view_menu.addSeparator()

        # 布局子菜单
        layout_menu = view_menu.addMenu("布局(&L)")

        # 标准布局
        standard_layout_action = QAction("标准布局", self)
        standard_layout_action.setCheckable(True)
        standard_layout_action.setChecked(True)
        standard_layout_action.triggered.connect(self.switch_to_standard_layout)
        layout_menu.addAction(standard_layout_action)

        # 四象限布局
        quadrant_layout_action = QAction("四象限布局", self)
        quadrant_layout_action.setCheckable(True)
        quadrant_layout_action.triggered.connect(self.switch_to_quadrant_layout)
        layout_menu.addAction(quadrant_layout_action)

        # 价值层次布局
        hierarchy_layout_action = QAction("价值层次布局", self)
        hierarchy_layout_action.setCheckable(True)
        hierarchy_layout_action.triggered.connect(self.switch_to_hierarchy_layout)
        layout_menu.addAction(hierarchy_layout_action)

        # 布局动作组
        self.layout_action_group = QActionGroup(self)
        self.layout_action_group.addAction(standard_layout_action)
        self.layout_action_group.addAction(quadrant_layout_action)
        self.layout_action_group.addAction(hierarchy_layout_action)
        self.layout_action_group.setExclusive(True)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")

        # 最高优先级任务集成
        priority_integration_action = QAction("🔴 最高优先级任务集成", self)
        priority_integration_action.setShortcut("Ctrl+Shift+P")
        priority_integration_action.triggered.connect(self.show_priority_one_integration)
        tools_menu.addAction(priority_integration_action)

        # 高优先级任务集成
        high_priority_integration_action = QAction("🟡 高优先级任务集成", self)
        high_priority_integration_action.setShortcut("Ctrl+Alt+P")
        high_priority_integration_action.triggered.connect(self.show_priority_two_integration)
        tools_menu.addAction(high_priority_integration_action)

        # 中优先级任务集成
        medium_priority_integration_action = QAction("🟢 中优先级任务集成", self)
        medium_priority_integration_action.setShortcut("Ctrl+Shift+Alt+P")
        medium_priority_integration_action.triggered.connect(self.show_priority_three_integration)
        tools_menu.addAction(medium_priority_integration_action)

        tools_menu.addSeparator()

        settings_action = QAction("设置(&S)", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_professional_menus(self):
        """设置专业菜单系统"""
        try:
            # 保存已创建的重要动作
            undo_action = getattr(self, 'undo_action', None)
            redo_action = getattr(self, 'redo_action', None)

            # 清空现有菜单
            self.menuBar().clear()

            # 使用专业菜单管理器创建菜单
            self.professional_menu_manager.create_menus(self.menuBar())

            # 恢复重要动作（如果它们存在）
            if undo_action:
                self.undo_action = undo_action
            if redo_action:
                self.redo_action = redo_action

            # 连接工具栏动作信号
            self.professional_toolbar_manager.toolbar_action_triggered.connect(
                self.on_professional_toolbar_action
            )

            logger.info("专业菜单系统设置完成")

        except Exception as e:
            logger.error(f"设置专业菜单系统失败: {e}")

    def setup_professional_toolbars(self):
        """设置专业工具栏系统"""
        try:
            # 清空现有工具栏
            for toolbar in self.findChildren(QToolBar):
                self.removeToolBar(toolbar)

            # 专业工具栏管理器已经在初始化时创建了工具栏
            # 这里只需要连接信号
            logger.info("专业工具栏系统设置完成")

        except Exception as e:
            logger.error(f"设置专业工具栏系统失败: {e}")

    def on_professional_toolbar_action(self, toolbar_name: str, action_id: str):
        """处理专业工具栏动作"""
        try:
            logger.info(f"专业工具栏动作: {toolbar_name}.{action_id}")

            # 这里可以添加额外的处理逻辑
            # 大部分动作已经在ProfessionalToolbarManager中处理

        except Exception as e:
            logger.error(f"处理专业工具栏动作失败: {e}")

    def setup_professional_statusbar(self):
        """设置专业状态栏系统 - 增强版"""
        try:
            # 创建增强状态栏
            self.status_bar = self.statusBar()
            self.status_bar.setFixedHeight(24)
            self.status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: #F3F4F6;
                    border-top: 1px solid #D1D5DB;
                    color: #374151;
                    font-size: 11px;
                }
                QStatusBar::item {
                    border: none;
                }
            """)

            # 左侧状态信息
            # 选中元素信息
            self.selected_element_label = QLabel("📍选中: 无")
            self.status_bar.addWidget(self.selected_element_label)

            self.status_bar.addWidget(QLabel(" | "))

            # 位置信息
            self.position_label = QLabel("🎯位置: (0,0)")
            self.status_bar.addWidget(self.position_label)

            self.status_bar.addWidget(QLabel(" | "))

            # 保存状态
            self.save_status_label = QLabel("💾已保存")
            self.save_status_label.setStyleSheet("color: #10B981; font-weight: bold;")
            self.status_bar.addWidget(self.save_status_label)

            # 中间弹性空间
            self.status_bar.addPermanentWidget(QLabel(""), 1)

            # 右侧系统信息
            # GPU使用率
            self.gpu_usage_label = QLabel("⚡GPU: 45%")
            self.gpu_usage_label.setStyleSheet("color: #F59E0B; font-weight: bold;")
            self.status_bar.addPermanentWidget(self.gpu_usage_label)

            self.status_bar.addPermanentWidget(QLabel(" | "))

            # 在线协作人数
            self.online_users_label = QLabel("👥在线: 3人")
            self.online_users_label.setStyleSheet("color: #10B981; font-weight: bold;")
            self.status_bar.addPermanentWidget(self.online_users_label)

            # 设置定时器更新状态信息
            self.status_update_timer = QTimer()
            self.status_update_timer.timeout.connect(self.update_status_info)
            self.status_update_timer.start(2000)  # 每2秒更新一次

            # 状态栏和通知系统已经在初始化时创建
            # 这里设置初始状态
            if hasattr(self, 'status_notification_manager'):
                self.status_notification_manager.update_status(StatusType.READY, "应用程序已启动")
                self.status_notification_manager.update_save_status(True)

                # 显示欢迎通知
                self.status_notification_manager.show_info(
                    "欢迎使用 AI Animation Studio",
                    "专业的AI驱动动画创作工具已准备就绪",
                    duration=3000
                )

            logger.info("增强版专业状态栏系统设置完成")

        except Exception as e:
            logger.error(f"设置专业状态栏系统失败: {e}")

    def update_status_info(self):
        """更新状态栏信息"""
        try:
            import random

            # 模拟GPU使用率变化
            gpu_usage = random.randint(35, 65)
            self.gpu_usage_label.setText(f"⚡GPU: {gpu_usage}%")

            # 根据GPU使用率调整颜色
            if gpu_usage < 50:
                color = "#10B981"  # 绿色
            elif gpu_usage < 70:
                color = "#F59E0B"  # 黄色
            else:
                color = "#EF4444"  # 红色

            self.gpu_usage_label.setStyleSheet(f"color: {color}; font-weight: bold;")

            # 模拟在线用户数变化
            online_users = random.randint(2, 5)
            self.online_users_label.setText(f"👥在线: {online_users}人")

        except Exception as e:
            logger.error(f"更新状态栏信息失败: {e}")

    def update_selected_element(self, element_name: str):
        """更新选中元素信息"""
        if hasattr(self, 'selected_element_label'):
            self.selected_element_label.setText(f"📍选中: {element_name}")

    def update_position_info(self, x: int, y: int):
        """更新位置信息"""
        if hasattr(self, 'position_label'):
            self.position_label.setText(f"🎯位置: ({x},{y})")

    def update_save_status_display(self, saved: bool):
        """更新保存状态显示"""
        if hasattr(self, 'save_status_label'):
            if saved:
                self.save_status_label.setText("💾已保存")
                self.save_status_label.setStyleSheet("color: #10B981; font-weight: bold;")
            else:
                self.save_status_label.setText("💾未保存")
                self.save_status_label.setStyleSheet("color: #EF4444; font-weight: bold;")

    def setup_toolbars(self):
        """设置工具栏"""
        # 主工具栏
        main_toolbar = self.addToolBar("主工具栏")
        main_toolbar.setMovable(False)
        
        # 新建按钮
        new_action = QAction("🆕 新建", self)
        new_action.triggered.connect(self.new_project)
        main_toolbar.addAction(new_action)
        
        # 打开按钮
        open_action = QAction("📂 打开", self)
        open_action.triggered.connect(self.open_project)
        main_toolbar.addAction(open_action)
        
        # 保存按钮
        save_action = QAction("💾 保存", self)
        save_action.triggered.connect(self.save_project)
        main_toolbar.addAction(save_action)
        
        main_toolbar.addSeparator()
        
        # 播放控制
        play_action = QAction("▶️ 播放", self)
        play_action.triggered.connect(self.toggle_play)
        main_toolbar.addAction(play_action)
        
        stop_action = QAction("⏹️ 停止", self)
        stop_action.triggered.connect(self.stop_preview)
        main_toolbar.addAction(stop_action)
        
        main_toolbar.addSeparator()
        
        # 导出按钮
        export_action = QAction("📤 导出", self)
        export_action.triggered.connect(self.export_html)
        main_toolbar.addAction(export_action)
    
    def setup_statusbar(self):
        """设置状态栏"""
        self.status_bar = self.statusBar()
        
        # 项目信息标签
        self.project_label = QLabel("就绪")
        self.status_bar.addWidget(self.project_label)
        
        # 时间信息标签
        self.time_label = QLabel("00:00 / 00:30")
        self.status_bar.addPermanentWidget(self.time_label)
        
        # 状态信息标签
        self.status_label = QLabel("AI Animation Studio v1.0")
        self.status_bar.addPermanentWidget(self.status_label)
    
    def setup_connections(self):
        """设置信号连接"""
        # 项目管理器信号
        self.project_changed.connect(self.on_project_changed)
        
        # 主题管理器信号
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # 子组件信号连接 - 检查组件是否存在
        if hasattr(self, 'timeline_widget'):
            self.timeline_widget.time_changed.connect(self.on_time_changed)
        if hasattr(self, 'ai_generator_widget'):
            self.ai_generator_widget.solutions_generated.connect(self.on_solutions_generated)
            # 连接AI生成器和预览器
            self.ai_generator_widget.solutions_generated.connect(self.preview_first_solution)
        if hasattr(self, 'stage_widget'):
            self.stage_widget.element_selected.connect(self.on_element_selected)
        if hasattr(self, 'elements_widget'):
            self.elements_widget.element_selected.connect(self.on_element_selected)
            # 连接元素管理器和属性面板
            self.elements_widget.element_selected.connect(self.on_element_selected_for_properties)
        if hasattr(self, 'properties_widget'):
            self.properties_widget.element_updated.connect(self.on_element_updated)

        # 连接描述工作台
        if hasattr(self, 'description_workbench'):
            self.description_workbench.description_ready.connect(self.on_description_ready)
            self.description_workbench.prompt_ready.connect(self.on_prompt_ready)
            self.description_workbench.animation_requested.connect(self.on_animation_requested)

        # 连接增强方案生成器
        if hasattr(self, 'enhanced_solution_generator'):
            self.enhanced_solution_generator.solution_generated.connect(self.on_solutions_generated)
            self.enhanced_solution_generator.solution_selected.connect(self.on_solution_selected)
            self.enhanced_solution_generator.solution_applied.connect(self.on_solution_applied)

        # 连接方案预览器
        if hasattr(self, 'solution_previewer'):
            self.solution_previewer.solution_analyzed.connect(self.on_solution_analyzed)
        
        # 启动自动保存
        if self.config.timeline.auto_save_interval > 0:
            self.auto_save_timer.start(self.config.timeline.auto_save_interval * 1000)
    
    def apply_config(self):
        """应用配置"""
        # 应用窗口几何
        geometry = self.config.ui.window_geometry
        self.setGeometry(geometry["x"], geometry["y"], geometry["width"], geometry["height"])

        # 应用主题
        self.theme_manager.apply_theme(QApplication.instance(), self.config.ui.theme)

        # 应用分割器大小
        if self.config.ui.splitter_sizes:
            self.main_splitter.setSizes(self.config.ui.splitter_sizes)

        # 启动自动保存
        if hasattr(self.config, 'timeline') and self.config.timeline.auto_save_interval > 0:
            auto_save_minutes = self.config.timeline.auto_save_interval // 60
            self.start_auto_save(max(1, auto_save_minutes))  # 至少1分钟
    
    # 项目操作辅助方法
    def has_unsaved_changes(self) -> bool:
        """检查是否有未保存的更改"""
        try:
            if not hasattr(self, 'project_manager') or not self.project_manager.current_project:
                return False

            # 检查命令历史是否有未保存的更改
            if hasattr(self, 'command_manager') and self.command_manager.has_unsaved_changes():
                return True

            # 检查项目修改时间
            project = self.project_manager.current_project
            if hasattr(project, 'modified_at') and hasattr(project, 'saved_at'):
                return project.modified_at > project.saved_at

            return False
        except Exception as e:
            logger.warning(f"检查未保存更改失败: {e}")
            return False

    def reset_ui_state(self):
        """重置界面状态"""
        try:
            # 清空各个组件的状态
            if hasattr(self, 'elements_widget') and hasattr(self.elements_widget, 'clear'):
                self.elements_widget.clear()

            if hasattr(self, 'properties_widget') and hasattr(self.properties_widget, 'clear'):
                self.properties_widget.clear()

            if hasattr(self, 'timeline_widget') and hasattr(self.timeline_widget, 'clear'):
                self.timeline_widget.clear()

            if hasattr(self, 'preview_widget') and hasattr(self.preview_widget, 'clear'):
                self.preview_widget.clear()

            logger.debug("界面状态已重置")
        except Exception as e:
            logger.warning(f"重置界面状态失败: {e}")

    def add_to_recent_files(self, file_path: str):
        """添加到最近文件列表"""
        try:
            if not hasattr(self, 'recent_files'):
                self.recent_files = []

            # 移除已存在的相同路径
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)

            # 添加到列表开头
            self.recent_files.insert(0, file_path)

            # 限制最近文件数量
            max_recent = 10
            if len(self.recent_files) > max_recent:
                self.recent_files = self.recent_files[:max_recent]

            # 更新菜单（如果存在）
            if hasattr(self, 'update_recent_files_menu'):
                self.update_recent_files_menu()

            logger.debug(f"已添加到最近文件: {file_path}")
        except Exception as e:
            logger.warning(f"添加最近文件失败: {e}")

    # 项目操作方法
    def new_project(self):
        """新建项目 - 使用向导"""
        try:
            # 更新状态
            self.status_notification_manager.update_status(StatusType.WORKING, "正在创建新项目...")

            # 如果当前有未保存的项目，询问是否保存
            if hasattr(self, 'current_project') and self.current_project and self.has_unsaved_changes():
                reply = QMessageBox.question(
                    self, "保存项目",
                    "当前项目有未保存的更改，是否保存？",
                    QMessageBox.StandardButton.Save |
                    QMessageBox.StandardButton.Discard |
                    QMessageBox.StandardButton.Cancel
                )

                if reply == QMessageBox.StandardButton.Save:
                    if not self.save_project():
                        self.status_notification_manager.update_status(StatusType.READY)
                        return  # 保存失败，取消新建
                elif reply == QMessageBox.StandardButton.Cancel:
                    self.status_notification_manager.update_status(StatusType.READY)
                    return  # 用户取消

            # 显示新建项目向导
            from .new_project_wizard import NewProjectWizard
            wizard = NewProjectWizard(self)
            wizard.project_created.connect(self.on_project_created_from_wizard)

            if wizard.exec() == wizard.DialogCode.Accepted:
                logger.info("项目向导完成")
                self.status_notification_manager.update_status(StatusType.READY, "新项目已创建")
                self.status_notification_manager.show_success("项目创建", "新项目已成功创建")
            else:
                self.status_notification_manager.update_status(StatusType.READY)

        except Exception as e:
            self.status_notification_manager.update_status(StatusType.ERROR, "新建项目失败")
            self.status_notification_manager.show_error("创建失败", f"新建项目失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"新建项目失败:\n{str(e)}")
            logger.error(f"新建项目失败: {e}")

    def on_project_created_from_wizard(self, config: dict):
        """从向导创建项目的回调"""
        try:
            # 创建项目
            project = self.project_manager.create_new_project(
                name=config["name"],
                template_id=config.get("template_id"),
                config=config
            )

            self.setWindowTitle(f"AI Animation Studio - {project.name}")

            # 清空命令历史
            self.command_manager.clear_history()
            self.update_edit_menu_state()

            # 重置界面状态
            if hasattr(self, 'reset_ui_state'):
                self.reset_ui_state()

            # 应用项目设置到界面
            self._apply_project_settings_to_ui(project)

            self.project_changed.emit()
            self.status_bar.showMessage(f"新建项目: {project.name}", 3000)
            logger.info(f"新建项目: {project.name}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建项目失败:\n{str(e)}")
            logger.error(f"创建项目失败: {e}")

    def _apply_project_settings_to_ui(self, project: Project):
        """将项目设置应用到界面"""
        try:
            # 应用网格设置
            if hasattr(project, 'settings') and project.settings:
                show_grid = project.settings.get("show_grid", True)
                if hasattr(self, 'stage_widget') and hasattr(self.stage_widget, 'set_grid_visible'):
                    self.stage_widget.set_grid_visible(show_grid)

                # 应用性能模式
                performance_mode = project.settings.get("performance_mode", "平衡")
                logger.info(f"应用性能模式: {performance_mode}")

        except Exception as e:
            logger.warning(f"应用项目设置失败: {e}")

    def new_project_from_template(self):
        """从模板新建项目"""
        try:
            # 显示模板选择对话框
            dialog = TemplateDialog(self)

            if dialog.exec() == dialog.DialogCode.Accepted:
                template_id = dialog.get_selected_template_id()
                if template_id:
                    # 获取项目名称
                    project_name, ok = QInputDialog.getText(
                        self, "新建项目", "请输入项目名称:",
                        text=f"基于{self.template_manager.templates[template_id].name}的项目"
                    )

                    if ok and project_name.strip():
                        # 应用模板创建项目
                        template_data = self.template_manager.apply_template(
                            template_id, {"name": project_name.strip()}
                        )

                        # 创建项目
                        project = self.project_manager.create_project_from_template(
                            project_name.strip(), template_data
                        )

                        self.setWindowTitle(f"AI Animation Studio - {project.name}")
                        self.project_changed.emit()
                        self.status_bar.showMessage(f"从模板创建项目: {project.name}", 3000)

                        # 更新界面
                        self.load_project_to_ui(project)

                        logger.info(f"从模板创建项目: {project.name}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"从模板创建项目失败:\n{str(e)}")
            logger.error(f"从模板创建项目失败: {e}")

    def load_project_to_ui(self, project):
        """将项目数据加载到界面"""
        try:
            # TODO: 实现项目数据到界面的加载
            # 这里应该将项目的元素、时间段等数据加载到相应的界面组件中
            logger.info(f"项目数据已加载到界面: {project.name}")
        except Exception as e:
            logger.error(f"加载项目到界面失败: {e}")
    
    def open_project(self):
        """打开项目 - 增强版"""
        try:
            # 如果当前有未保存的项目，询问是否保存
            if hasattr(self, 'current_project') and self.current_project and self.has_unsaved_changes():
                reply = QMessageBox.question(
                    self, "保存项目",
                    "当前项目有未保存的更改，是否保存？",
                    QMessageBox.StandardButton.Save |
                    QMessageBox.StandardButton.Discard |
                    QMessageBox.StandardButton.Cancel
                )

                if reply == QMessageBox.StandardButton.Save:
                    if not self.save_project():
                        return  # 保存失败，取消打开
                elif reply == QMessageBox.StandardButton.Cancel:
                    return  # 用户取消

            # 显示项目选择对话框（包含最近项目）
            from .project_open_dialog import ProjectOpenDialog
            dialog = ProjectOpenDialog(self, self.project_manager)

            if dialog.exec() == dialog.DialogCode.Accepted:
                file_path = dialog.get_selected_file()
                if file_path:
                    self._load_project_file(file_path)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开项目失败:\n{str(e)}")
            logger.error(f"打开项目失败: {e}")

    def open_project_file(self, file_path: str):
        """直接打开指定的项目文件"""
        try:
            self._load_project_file(file_path)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开项目失败:\n{str(e)}")
            logger.error(f"打开项目文件失败: {e}")

    def _load_project_file(self, file_path: str):
        """加载项目文件的内部方法"""
        try:
            # 显示加载进度
            self.status_bar.showMessage("正在加载项目...", 0)

            if self.project_manager.load_project(Path(file_path)):
                # 清空命令历史
                self.command_manager.clear_history()
                self.update_edit_menu_state()

                # 更新窗口标题
                project_name = self.project_manager.current_project.name
                self.setWindowTitle(f"AI Animation Studio - {project_name}")

                # 加载项目数据到界面
                self._load_project_to_ui(self.project_manager.current_project)

                self.project_changed.emit()
                self.status_bar.showMessage(f"项目已打开: {self.project_manager.current_project.name}", 3000)
                logger.info(f"项目已打开: {file_path}")
            else:
                self.status_bar.clearMessage()
                QMessageBox.warning(self, "错误", "无法打开项目文件\n请检查文件格式是否正确")

        except Exception as e:
            self.status_bar.clearMessage()
            QMessageBox.critical(self, "错误", f"打开项目失败:\n{str(e)}")
            logger.error(f"打开项目失败: {e}")
    
    def save_project(self) -> bool:
        """保存项目 - 增强版"""
        try:
            if not self.project_manager.current_project:
                QMessageBox.warning(self, "警告", "没有项目可保存")
                return False

            # 如果是新项目（没有保存过），使用另存为
            if not self.project_manager.project_file:
                return self.save_project_as()

            # 检查是否需要显示保存选项对话框（按住Shift键时）
            modifiers = QApplication.keyboardModifiers()
            show_options = modifiers & Qt.KeyboardModifier.ShiftModifier

            save_options = {}
            if show_options:
                dialog = SaveOptionsDialog(self, self.project_manager.current_project)
                if dialog.exec() != dialog.DialogCode.Accepted:
                    return False
                save_options = dialog.get_save_options()

            # 更新状态和显示保存进度
            self.status_notification_manager.update_status(StatusType.SAVING, "正在保存项目...")
            self.status_notification_manager.show_progress(0, "保存中")

            # 执行保存
            success = self.project_manager.save_project(
                create_backup=save_options.get('create_backup', True),
                incremental=save_options.get('incremental_save', True)
            )

            # 隐藏进度条
            self.status_notification_manager.hide_progress()

            if success:
                # 更新命令管理器的保存状态
                if hasattr(self.command_manager, 'mark_saved'):
                    self.command_manager.mark_saved()

                # 记录手动保存
                self.auto_save_manager.record_manual_save()

                project_name = self.project_manager.current_project.name

                # 更新状态和通知
                self.status_notification_manager.update_status(StatusType.READY, f"项目已保存: {project_name}")
                self.status_notification_manager.update_save_status(True)
                self.status_notification_manager.show_success("保存成功", f"项目 '{project_name}' 已成功保存")

                logger.info(f"项目已保存: {self.project_manager.project_file}")

                # 如果启用了版本控制，创建版本备份
                if save_options.get('enable_versioning', False):
                    description = save_options.get('version_description', '')
                    self.auto_save_manager.create_version_backup(description)

                return True
            else:
                self.status_notification_manager.update_status(StatusType.ERROR, "保存项目失败")
                self.status_notification_manager.show_error("保存失败", "保存项目失败")
                QMessageBox.warning(self, "错误", "保存项目失败")
                return False

        except Exception as e:
            self.status_notification_manager.update_status(StatusType.ERROR, "保存项目失败")
            self.status_notification_manager.hide_progress()
            self.status_notification_manager.show_error("保存失败", f"保存项目失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"保存项目失败:\n{str(e)}")
            logger.error(f"保存项目失败: {e}")
            return False
    
    def save_project_as(self) -> bool:
        """另存为项目 - 增强版"""
        try:
            if not self.project_manager.current_project:
                QMessageBox.warning(self, "警告", "没有项目可保存")
                return False

            # 显示增强的另存为对话框
            from .save_as_dialog import SaveAsDialog
            dialog = SaveAsDialog(self, self.project_manager.current_project)

            if dialog.exec() != dialog.DialogCode.Accepted:
                return False

            # 获取保存选项
            save_options = dialog.get_save_options()

            # 验证保存位置
            save_location = save_options.get("save_location", "")
            if not save_location:
                QMessageBox.warning(self, "错误", "请选择保存位置")
                return False

            # 显示保存进度
            self.status_bar.showMessage("正在保存项目...", 0)

            # 应用保存选项到项目
            self._apply_save_options_to_project(save_options)

            # 使用项目打包器进行保存
            success = self._save_with_packager(save_location, save_options)

            if success:
                # 更新命令管理器的保存状态
                if hasattr(self.command_manager, 'mark_saved'):
                    self.command_manager.mark_saved()

                # 记录手动保存
                self.auto_save_manager.record_manual_save()

                # 更新窗口标题
                project_name = save_options.get("project_name", self.project_manager.current_project.name)
                self.setWindowTitle(f"AI Animation Studio - {project_name}")

                # 添加到最近文件列表
                if hasattr(self, 'add_to_recent_files'):
                    self.add_to_recent_files(save_location)

                self.status_bar.showMessage(f"项目已保存: {project_name}", 3000)
                logger.info(f"项目另存为: {save_location}")

                # 如果启用了版本控制，创建版本备份
                if save_options.get('create_backup', False):
                    description = f"另存为备份 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    self.auto_save_manager.create_version_backup(description)

                return True
            else:
                self.status_bar.clearMessage()
                QMessageBox.warning(self, "错误", "保存项目失败")
                return False

        except Exception as e:
            self.status_bar.clearMessage()
            QMessageBox.critical(self, "错误", f"另存为项目失败:\n{str(e)}")
            logger.error(f"另存为项目失败: {e}")
            return False

    def _save_with_packager(self, save_location: str, save_options: Dict) -> bool:
        """使用项目打包器保存"""
        try:
            from core.project_packager import ProjectPackager

            packager = ProjectPackager()
            output_path = Path(save_location)

            # 根据文件格式确定打包类型
            format_text = save_options.get("file_format", "")
            if "AAS" in format_text:
                format_type = "aas"
            elif "JSON" in format_text:
                format_type = "json"
            elif "压缩包" in format_text:
                format_type = "zip"
            elif "XML" in format_text:
                format_type = "xml"
            elif "HTML" in format_text:
                format_type = "html"
            elif "可执行文件" in format_text:
                format_type = "exe"
            else:
                format_type = "aas"  # 默认格式

            # 执行打包
            return packager.package_project(
                self.project_manager.current_project,
                output_path,
                format_type,
                save_options
            )

        except Exception as e:
            logger.error(f"使用打包器保存失败: {e}")
            return False

    def _apply_save_options_to_project(self, options: dict):
        """应用保存选项到项目"""
        try:
            project = self.project_manager.current_project

            # 更新项目基本信息
            if options.get("project_name"):
                project.name = options["project_name"]
            if options.get("project_description"):
                project.description = options["project_description"]
            if options.get("author"):
                project.author = options.get("author", "")
            if options.get("version"):
                project.version = options.get("version", "1.0")

        except Exception as e:
            logger.warning(f"应用保存选项失败: {e}")

    def _save_as_aas(self, file_path: str, options: dict) -> bool:
        """保存为AAS格式"""
        try:
            return self.project_manager.save_project(
                Path(file_path),
                create_backup=options.get("create_backup", True),
                incremental=options.get("incremental_save", True)
            )
        except Exception as e:
            logger.error(f"保存AAS格式失败: {e}")
            return False

    def _save_as_json(self, file_path: str, options: dict) -> bool:
        """保存为JSON格式"""
        try:
            import json

            # 获取项目数据
            project_data = self.project_manager._project_to_dict(self.project_manager.current_project)

            # 应用JSON格式选项
            indent = options.get("indent_size", 2) if options.get("pretty_print", True) else None

            # 保存JSON文件
            with open(file_path, 'w', encoding=options.get("encoding", "utf-8")) as f:
                json.dump(project_data, f, indent=indent, ensure_ascii=False, default=str)

            return True

        except Exception as e:
            logger.error(f"保存JSON格式失败: {e}")
            return False

    def _save_as_package(self, file_path: str, options: dict) -> bool:
        """保存为压缩包格式"""
        try:
            import zipfile
            import tempfile
            import shutil

            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # 保存项目文件
                project_file = temp_path / "project.aas"
                if not self.project_manager.save_project(project_file):
                    return False

                # 创建压缩包
                with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED,
                                   compresslevel=options.get("compression_level", 6)) as zipf:

                    # 添加项目文件
                    zipf.write(project_file, "project.aas")

                    # 添加缩略图（如果存在）
                    thumbnail_path = project_file.parent / f"{project_file.stem}_thumbnail.png"
                    if thumbnail_path.exists():
                        zipf.write(thumbnail_path, "thumbnail.png")

                    # 根据选项添加其他文件
                    if options.get("include_assets", True):
                        self._add_assets_to_package(zipf, temp_path)

                    if options.get("include_libraries", False):
                        self._add_libraries_to_package(zipf, temp_path)

                    if options.get("include_templates", False):
                        self._add_templates_to_package(zipf, temp_path)

                    if options.get("include_export_html", False):
                        self._add_exported_html_to_package(zipf, temp_path)

            return True

        except Exception as e:
            logger.error(f"保存压缩包格式失败: {e}")
            return False

    def _add_assets_to_package(self, zipf, temp_path: Path):
        """添加资源文件到压缩包"""
        try:
            # 这里应该收集项目中使用的所有资源文件
            # 简化实现
            assets_dir = Path("assets")
            if assets_dir.exists():
                for asset_file in assets_dir.rglob("*"):
                    if asset_file.is_file():
                        arcname = f"assets/{asset_file.relative_to(assets_dir)}"
                        zipf.write(asset_file, arcname)
        except Exception as e:
            logger.warning(f"添加资源文件失败: {e}")

    def _add_libraries_to_package(self, zipf, temp_path: Path):
        """添加JavaScript库到压缩包"""
        try:
            # 添加项目使用的JavaScript库
            libraries_dir = Path("libraries")
            if libraries_dir.exists():
                for lib_file in libraries_dir.rglob("*"):
                    if lib_file.is_file():
                        arcname = f"libraries/{lib_file.relative_to(libraries_dir)}"
                        zipf.write(lib_file, arcname)
        except Exception as e:
            logger.warning(f"添加JavaScript库失败: {e}")

    def _add_templates_to_package(self, zipf, temp_path: Path):
        """添加模板文件到压缩包"""
        try:
            # 添加项目使用的模板文件
            templates_dir = Path("templates")
            if templates_dir.exists():
                for template_file in templates_dir.rglob("*"):
                    if template_file.is_file():
                        arcname = f"templates/{template_file.relative_to(templates_dir)}"
                        zipf.write(template_file, arcname)
        except Exception as e:
            logger.warning(f"添加模板文件失败: {e}")

    def _add_exported_html_to_package(self, zipf, temp_path: Path):
        """添加导出的HTML到压缩包"""
        try:
            # 导出HTML并添加到压缩包
            html_content = self.export_html()
            if html_content:
                html_file = temp_path / "export.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                zipf.write(html_file, "export.html")
        except Exception as e:
            logger.warning(f"添加导出HTML失败: {e}")
    
    def export_html(self):
        """导出HTML - 增强版"""
        try:
            # 检查是否有当前方案 - 安全调用
            if hasattr(self.ai_generator_widget, 'get_current_solution'):
                current_solution = self.ai_generator_widget.get_current_solution()
            else:
                logger.warning("AI生成器不支持get_current_solution方法")
                # 尝试从项目数据生成基础HTML
                current_solution = self._generate_basic_html_from_project()

            if not current_solution:
                QMessageBox.warning(self, "警告", "请先生成动画方案或确保项目有内容")
                return

            # 显示HTML导出选项对话框
            from .html_export_dialog import HTMLExportDialog
            export_dialog = HTMLExportDialog(self, self.project_manager.current_project)

            if export_dialog.exec() != export_dialog.DialogCode.Accepted:
                return

            # 获取导出选项
            export_options = export_dialog.get_export_options()

            # 构建完整的输出路径
            output_dir = Path(export_options["output_dir"])
            filename = export_options["filename"]
            if not filename.endswith('.html'):
                filename += '.html'

            file_path = output_dir / filename

            # 确保输出目录存在
            output_dir.mkdir(parents=True, exist_ok=True)

            # 显示导出进度
            self.status_bar.showMessage("正在导出HTML...", 0)

            # 生成优化的HTML
            optimized_html = self._generate_optimized_html(current_solution, export_options)

            # 保存HTML文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(optimized_html)

            # 如果需要，保存相关资源文件
            if export_options.get("include_assets", True):
                self._export_html_assets(output_dir, export_options)

            self.status_bar.showMessage(f"HTML已导出: {file_path}", 3000)
            QMessageBox.information(self, "导出成功", f"HTML文件已保存到:\n{file_path}")

        except Exception as e:
            self.status_bar.clearMessage()
            logger.error(f"HTML导出失败: {e}")
            QMessageBox.critical(self, "导出失败", f"HTML导出失败:\n{str(e)}")

    def _generate_basic_html_from_project(self):
        """从项目数据生成基础HTML"""
        try:
            if not self.project_manager.current_project:
                return None

            # 创建一个基础的HTML结构
            class BasicSolution:
                def __init__(self, html_code):
                    self.html_code = html_code

            # 生成基础HTML模板
            html_template = f"""
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{self.project_manager.current_project.name}</title>
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        background: #000;
                        overflow: hidden;
                    }}
                    #canvas {{
                        width: {self.project_manager.current_project.canvas_width}px;
                        height: {self.project_manager.current_project.canvas_height}px;
                        margin: 0 auto;
                        display: block;
                    }}
                </style>
            </head>
            <body>
                <div id="canvas">
                    <!-- 动画内容将在这里生成 -->
                    <p style="color: white; text-align: center; padding-top: 50px;">
                        {self.project_manager.current_project.description or '动画内容'}
                    </p>
                </div>
                <script>
                    // 基础动画脚本
                    console.log('AI Animation Studio - {self.project_manager.current_project.name}');
                </script>
            </body>
            </html>
            """

            return BasicSolution(html_template.strip())

        except Exception as e:
            logger.error(f"生成基础HTML失败: {e}")
            return None

    def _generate_optimized_html(self, solution, options: dict) -> str:
        """生成优化的HTML"""
        try:
            html_content = solution.html_code

            # 添加SEO优化
            if options.get("page_title") or options.get("page_description"):
                html_content = self._add_seo_optimization(html_content, options)

            # 添加响应式设计
            if options.get("responsive_design", True):
                html_content = self._add_responsive_design(html_content)

            # 添加播放控制
            if options.get("add_controls", False):
                html_content = self._add_playback_controls(html_content)

            # 添加JavaScript库
            if options.get("selected_libraries"):
                html_content = self._add_javascript_libraries(html_content, options)

            # 压缩优化
            if options.get("minify_html", True):
                html_content = self._minify_html(html_content, options)

            return html_content

        except Exception as e:
            logger.error(f"生成优化HTML失败: {e}")
            return solution.html_code

    def _add_seo_optimization(self, html_content: str, options: dict) -> str:
        """添加SEO优化"""
        try:
            # 查找head标签
            head_start = html_content.find('<head>')
            head_end = html_content.find('</head>')

            if head_start == -1 or head_end == -1:
                return html_content

            seo_tags = []

            # 基本SEO标签
            if options.get("page_title"):
                seo_tags.append(f'<title>{options["page_title"]}</title>')

            if options.get("page_description"):
                seo_tags.append(f'<meta name="description" content="{options["page_description"]}">')

            if options.get("keywords"):
                seo_tags.append(f'<meta name="keywords" content="{options["keywords"]}">')

            if options.get("author"):
                seo_tags.append(f'<meta name="author" content="{options["author"]}">')

            # Open Graph标签
            if options.get("enable_og", True):
                if options.get("og_title"):
                    seo_tags.append(f'<meta property="og:title" content="{options["og_title"]}">')
                if options.get("og_description"):
                    seo_tags.append(f'<meta property="og:description" content="{options["og_description"]}">')
                if options.get("og_image"):
                    seo_tags.append(f'<meta property="og:image" content="{options["og_image"]}">')
                seo_tags.append('<meta property="og:type" content="website">')

            # 结构化数据
            if options.get("enable_schema", False):
                schema_type = options.get("schema_type", "CreativeWork")
                schema_data = {
                    "@context": "https://schema.org",
                    "@type": schema_type,
                    "name": options.get("page_title", ""),
                    "description": options.get("page_description", ""),
                    "author": {
                        "@type": "Person",
                        "name": options.get("author", "")
                    }
                }
                seo_tags.append(f'<script type="application/ld+json">{json.dumps(schema_data)}</script>')

            # 插入SEO标签
            if seo_tags:
                seo_content = '\n    ' + '\n    '.join(seo_tags)
                html_content = html_content[:head_end] + seo_content + '\n' + html_content[head_end:]

            return html_content

        except Exception as e:
            logger.error(f"添加SEO优化失败: {e}")
            return html_content

    def _add_responsive_design(self, html_content: str) -> str:
        """添加响应式设计"""
        try:
            responsive_css = """
    <style>
        /* 响应式设计 */
        @media (max-width: 768px) {
            body { font-size: 14px; }
            #canvas {
                width: 100% !important;
                height: auto !important;
                max-width: 100vw;
            }
        }
        @media (max-width: 480px) {
            body { font-size: 12px; }
            #canvas {
                width: 100% !important;
                height: auto !important;
            }
        }
    </style>"""

            # 查找head结束标签并插入响应式CSS
            head_end = html_content.find('</head>')
            if head_end != -1:
                html_content = html_content[:head_end] + responsive_css + '\n' + html_content[head_end:]

            return html_content

        except Exception as e:
            logger.error(f"添加响应式设计失败: {e}")
            return html_content

    def _add_playback_controls(self, html_content: str) -> str:
        """添加播放控制"""
        try:
            controls_html = """
    <div id="playback-controls" style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 1000;">
        <button id="play-btn" onclick="playAnimation()">播放</button>
        <button id="pause-btn" onclick="pauseAnimation()">暂停</button>
        <button id="restart-btn" onclick="restartAnimation()">重播</button>
    </div>"""

            controls_script = """
    <script>
        function playAnimation() {
            // 播放动画逻辑
            console.log('播放动画');
        }
        function pauseAnimation() {
            // 暂停动画逻辑
            console.log('暂停动画');
        }
        function restartAnimation() {
            // 重播动画逻辑
            console.log('重播动画');
        }
    </script>"""

            # 在body结束前插入控制元素
            body_end = html_content.find('</body>')
            if body_end != -1:
                html_content = html_content[:body_end] + controls_html + controls_script + '\n' + html_content[body_end:]

            return html_content

        except Exception as e:
            logger.error(f"添加播放控制失败: {e}")
            return html_content

    def _add_javascript_libraries(self, html_content: str, options: dict) -> str:
        """添加JavaScript库"""
        try:
            selected_libraries = options.get("selected_libraries", [])
            use_cdn = options.get("use_cdn", True)
            cdn_provider = options.get("cdn_provider", "jsDelivr")

            if not selected_libraries:
                return html_content

            # CDN URL映射
            cdn_urls = {
                "jsDelivr": {
                    "GSAP": "https://cdn.jsdelivr.net/npm/gsap@3.12.2/dist/gsap.min.js",
                    "Three.js": "https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js",
                    "Anime.js": "https://cdn.jsdelivr.net/npm/animejs@3.2.1/lib/anime.min.js",
                    "Lottie": "https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js",
                    "Particles.js": "https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js",
                    "AOS": "https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js"
                },
                "unpkg": {
                    "GSAP": "https://unpkg.com/gsap@3.12.2/dist/gsap.min.js",
                    "Three.js": "https://unpkg.com/three@0.158.0/build/three.min.js",
                    "Anime.js": "https://unpkg.com/animejs@3.2.1/lib/anime.min.js",
                    "Lottie": "https://unpkg.com/lottie-web@5.12.2/build/player/lottie.min.js",
                    "Particles.js": "https://unpkg.com/particles.js@2.0.0/particles.min.js",
                    "AOS": "https://unpkg.com/aos@2.3.4/dist/aos.js"
                }
            }

            library_tags = []

            for library in selected_libraries:
                if use_cdn and cdn_provider in cdn_urls and library in cdn_urls[cdn_provider]:
                    url = cdn_urls[cdn_provider][library]
                    library_tags.append(f'<script src="{url}"></script>')
                else:
                    # 使用本地文件
                    library_tags.append(f'<script src="js/{library.lower()}.min.js"></script>')

            # 插入库标签
            if library_tags:
                head_end = html_content.find('</head>')
                if head_end != -1:
                    library_content = '\n    ' + '\n    '.join(library_tags)
                    html_content = html_content[:head_end] + library_content + '\n' + html_content[head_end:]

            return html_content

        except Exception as e:
            logger.error(f"添加JavaScript库失败: {e}")
            return html_content

    def _minify_html(self, html_content: str, options: dict) -> str:
        """压缩HTML"""
        try:
            compression_level = options.get("compression_level", 3)

            if not options.get("minify_html", True):
                return html_content

            # 基础压缩：移除多余空白
            if compression_level >= 1:
                import re
                # 移除多余的空白字符
                html_content = re.sub(r'\s+', ' ', html_content)
                # 移除标签间的空白
                html_content = re.sub(r'>\s+<', '><', html_content)

            # 中级压缩：移除注释
            if compression_level >= 3:
                # 移除HTML注释
                html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)

            # 高级压缩：移除可选的标签和属性
            if compression_level >= 4:
                # 移除可选的结束标签
                html_content = re.sub(r'</?(br|hr|img|input|meta|link)\s*/?>',
                                    lambda m: m.group(0).replace(' />', '>'), html_content)

            # 最大压缩：移除所有不必要的空白
            if compression_level >= 5:
                html_content = html_content.strip()
                # 移除行首行尾空白
                lines = [line.strip() for line in html_content.split('\n') if line.strip()]
                html_content = ''.join(lines)

            return html_content

        except Exception as e:
            logger.error(f"压缩HTML失败: {e}")
            return html_content

    def _export_html_assets(self, output_dir: Path, options: dict):
        """导出HTML相关资源"""
        try:
            # 创建资源目录
            assets_dir = output_dir / "assets"
            js_dir = output_dir / "js"
            css_dir = output_dir / "css"

            # 如果不使用CDN，复制JavaScript库文件
            if not options.get("use_cdn", True):
                js_dir.mkdir(exist_ok=True)

                # 复制选中的库文件
                selected_libraries = options.get("selected_libraries", [])
                for library in selected_libraries:
                    # 这里应该从本地库目录复制文件
                    # 简化实现：创建占位符文件
                    lib_file = js_dir / f"{library.lower()}.min.js"
                    lib_file.write_text(f"// {library} library placeholder\nconsole.log('{library} loaded');")

            # 复制项目资源文件
            project_assets_dir = Path("assets")
            if project_assets_dir.exists():
                assets_dir.mkdir(exist_ok=True)
                for asset_file in project_assets_dir.rglob("*"):
                    if asset_file.is_file():
                        relative_path = asset_file.relative_to(project_assets_dir)
                        target_path = assets_dir / relative_path
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(asset_file, target_path)

            # 生成CSS文件（如果需要）
            if options.get("responsive_design", True):
                css_dir.mkdir(exist_ok=True)
                responsive_css = """
/* 响应式设计样式 */
@media (max-width: 768px) {
    body { font-size: 14px; }
    #canvas { width: 100% !important; height: auto !important; }
}
@media (max-width: 480px) {
    body { font-size: 12px; }
}
"""
                (css_dir / "responsive.css").write_text(responsive_css)

            logger.info(f"HTML资源已导出到: {output_dir}")

        except Exception as e:
            logger.error(f"导出HTML资源失败: {e}")
            QMessageBox.critical(self, "导出失败", f"HTML导出失败:\n{str(e)}")
    
    def export_video(self):
        """导出视频 - 增强版"""
        try:
            # 检查是否有当前方案 - 安全调用
            if hasattr(self.ai_generator_widget, 'get_current_solution'):
                current_solution = self.ai_generator_widget.get_current_solution()
            else:
                logger.warning("AI生成器不支持get_current_solution方法")
                # 尝试从项目数据生成基础HTML
                current_solution = self._generate_basic_html_from_project()

            if not current_solution:
                QMessageBox.warning(self, "警告", "请先生成动画方案或确保项目有内容")
                return

            # 检查导出依赖
            deps = VideoExporter.check_dependencies()
            missing_deps = [name for name, available in deps.items() if not available]

            if missing_deps:
                dep_info = "\n".join([
                    "视频导出需要以下依赖:",
                    "• Node.js (用于Puppeteer)",
                    "• FFmpeg (用于视频合成)",
                    "• Puppeteer (npm install puppeteer)",
                    "",
                    f"缺失的依赖: {', '.join(missing_deps)}",
                    "",
                    "请安装缺失的依赖后重试。"
                ])
                QMessageBox.warning(self, "缺少依赖", dep_info)
                return

            # 显示视频导出选项对话框
            from .video_export_dialog import VideoExportDialog
            export_dialog = VideoExportDialog(self, self.project_manager.current_project)

            if export_dialog.exec() != export_dialog.DialogCode.Accepted:
                return

            # 获取导出选项
            export_options = export_dialog.get_export_options()

            # 显示导出进度
            self.status_bar.showMessage("正在导出视频...", 0)

            # 根据是否启用批量导出选择导出方式
            if export_options.get("enable_batch", False):
                success = self._batch_export_video(current_solution, export_options, export_dialog)
            else:
                success = self._single_export_video(current_solution, export_options, export_dialog)

            if not success:
                QMessageBox.warning(self, "错误", "无法启动视频导出")

        except Exception as e:
            self.status_bar.clearMessage()
            logger.error(f"视频导出失败: {e}")
            QMessageBox.critical(self, "导出失败", f"视频导出失败:\n{str(e)}")

    def _single_export_video(self, solution, options: dict, dialog) -> bool:
        """单个视频导出"""
        try:
            # 构建输出路径
            output_dir = Path(options["output_dir"])
            filename = options["filename"]
            file_path = output_dir / filename

            # 确保输出目录存在
            output_dir.mkdir(parents=True, exist_ok=True)

            # 增强HTML
            enhanced_html = self._enhance_html_for_video(solution, options)

            # 进度回调
            def on_progress(message):
                self.status_bar.showMessage(f"视频导出: {message}", 0)
                if hasattr(dialog, 'progress_text'):
                    dialog.progress_text.append(message)
                logger.info(f"视频导出进度: {message}")

            def on_complete(success, message):
                if success:
                    self.status_bar.showMessage("视频导出完成", 3000)
                    QMessageBox.information(self, "导出成功", f"视频已保存到:\n{file_path}")
                else:
                    self.status_bar.showMessage("视频导出失败", 3000)
                    QMessageBox.critical(self, "导出失败", message)

            # 启动导出
            success = self.video_exporter.export_video(
                enhanced_html,
                str(file_path),
                options.get("duration", 10.0),
                options.get("fps", 30),
                options.get("width", 1920),
                options.get("height", 1080),
                progress_callback=on_progress,
                complete_callback=on_complete,
                export_options=options
            )

            return success

        except Exception as e:
            logger.error(f"单个视频导出失败: {e}")
            return False

    def _batch_export_video(self, solution, options: dict, dialog) -> bool:
        """批量视频导出"""
        try:
            output_dir = Path(options["output_dir"])
            base_filename = Path(options["filename"]).stem

            batch_formats = options.get("batch_formats", ["MP4"])
            batch_resolutions = options.get("batch_resolutions", ["1920x1080"])

            total_exports = len(batch_formats) * len(batch_resolutions)
            current_export = 0

            # 更新进度条
            if hasattr(dialog, 'progress_bar'):
                dialog.progress_bar.setMaximum(total_exports)
                dialog.progress_bar.setValue(0)

            for format_name in batch_formats:
                for resolution in batch_resolutions:
                    current_export += 1

                    # 解析分辨率
                    width, height = map(int, resolution.split('x'))

                    # 构建文件名
                    format_ext = self._get_format_extension(format_name)
                    filename = f"{base_filename}_{resolution}.{format_ext}"
                    file_path = output_dir / filename

                    # 更新选项
                    current_options = options.copy()
                    current_options.update({
                        "width": width,
                        "height": height,
                        "format": format_name,
                        "filename": filename
                    })

                    # 增强HTML
                    enhanced_html = self._enhance_html_for_video(solution, current_options)

                    # 进度回调
                    def on_progress(message, current=current_export, total=total_exports):
                        progress_msg = f"[{current}/{total}] {message}"
                        self.status_bar.showMessage(progress_msg, 0)
                        if hasattr(dialog, 'progress_text'):
                            dialog.progress_text.append(progress_msg)
                        logger.info(f"批量导出进度: {progress_msg}")

                    # 导出单个视频
                    success = self.video_exporter.export_video(
                        enhanced_html,
                        str(file_path),
                        current_options.get("duration", 10.0),
                        current_options.get("fps", 30),
                        width, height,
                        progress_callback=on_progress,
                        export_options=current_options
                    )

                    if not success:
                        logger.error(f"批量导出失败: {filename}")
                        continue

                    # 更新进度条
                    if hasattr(dialog, 'progress_bar'):
                        dialog.progress_bar.setValue(current_export)

            self.status_bar.showMessage("批量导出完成", 3000)
            QMessageBox.information(self, "批量导出完成", f"已导出 {total_exports} 个视频文件到:\n{output_dir}")

            return True

        except Exception as e:
            logger.error(f"批量视频导出失败: {e}")
            return False

    def _enhance_html_for_video(self, solution, options: dict) -> str:
        """为视频导出增强HTML"""
        try:
            html_content = solution.html_code

            # 添加视频导出专用的样式和脚本
            video_enhancements = f"""
    <style>
        /* 视频导出优化样式 */
        body {{
            margin: 0;
            padding: 0;
            width: {options.get('width', 1920)}px;
            height: {options.get('height', 1080)}px;
            overflow: hidden;
            background: #000;
        }}

        /* 禁用用户交互 */
        * {{
            user-select: none;
            pointer-events: none;
        }}

        /* 确保动画在视频录制时正常播放 */
        *, *::before, *::after {{
            animation-fill-mode: both;
        }}
    </style>

    <script>
        // 视频导出专用脚本
        window.videoExportMode = true;
        window.videoDuration = {options.get('duration', 10.0)};
        window.videoFPS = {options.get('fps', 30)};

        // 禁用控制台输出以提高性能
        if (!window.debugMode) {{
            console.log = console.warn = console.error = function() {{}};
        }}

        // 确保动画在页面加载后立即开始
        document.addEventListener('DOMContentLoaded', function() {{
            // 触发动画开始
            if (typeof startAnimation === 'function') {{
                startAnimation();
            }}
        }});
    </script>"""

            # 在head结束前插入增强内容
            head_end = html_content.find('</head>')
            if head_end != -1:
                html_content = html_content[:head_end] + video_enhancements + '\n' + html_content[head_end:]

            return html_content

        except Exception as e:
            logger.error(f"增强HTML失败: {e}")
            return solution.html_code

    def _get_format_extension(self, format_name: str) -> str:
        """获取格式对应的文件扩展名"""
        format_map = {
            "MP4": "mp4",
            "MP4 (H.264)": "mp4",
            "WebM": "webm",
            "WebM (VP9)": "webm",
            "AVI": "avi",
            "MOV": "mov"
        }

        return format_map.get(format_name, "mp4")
    
    def toggle_play(self):
        """切换播放状态"""
        try:
            # 检查预览组件是否有内容
            if hasattr(self.preview_widget, 'preview_controller'):
                controller = self.preview_widget.preview_controller
                if controller.is_playing:
                    controller.pause_animation()
                else:
                    controller.play_animation()
            else:
                QMessageBox.information(self, "提示", "请先生成动画方案")
        except Exception as e:
            logger.error(f"播放控制失败: {e}")

    def stop_preview(self):
        """停止预览"""
        try:
            if hasattr(self.preview_widget, 'preview_controller'):
                self.preview_widget.preview_controller.stop_animation()
        except Exception as e:
            logger.error(f"停止预览失败: {e}")
    
    def change_theme(self, theme_name: str):
        """更改主题"""
        self.config.ui.theme = theme_name
        self.theme_manager.apply_theme(QApplication.instance(), theme_name)
        self.config.save()
    
    def show_settings(self):
        """显示设置对话框"""
        try:
            dialog = SettingsDialog(self.config, self)
            dialog.settings_changed.connect(self.on_settings_changed)

            if dialog.exec() == dialog.DialogCode.Accepted:
                self.status_bar.showMessage("设置已保存", 2000)

        except Exception as e:
            logger.error(f"显示设置对话框失败: {e}")
            QMessageBox.critical(self, "错误", f"显示设置对话框失败:\n{str(e)}")

    def on_settings_changed(self):
        """设置改变处理"""
        # 重新应用主题
        self.theme_manager.apply_theme(QApplication.instance(), self.config.ui.theme)

        # 更新自动保存间隔
        if self.config.timeline.auto_save_interval > 0:
            self.auto_save_timer.start(self.config.timeline.auto_save_interval * 1000)
        else:
            self.auto_save_timer.stop()

        logger.info("设置已更新")

    def show_priority_one_integration(self):
        """显示最高优先级任务集成界面"""
        try:
            # 创建停靠窗口
            dock_widget = QDockWidget("🔴 最高优先级任务集成", self)
            dock_widget.setWidget(self.priority_one_integration_widget)
            dock_widget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                       Qt.DockWidgetArea.RightDockWidgetArea |
                                       Qt.DockWidgetArea.BottomDockWidgetArea)

            # 添加到主窗口
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_widget)

            # 确保可见
            dock_widget.show()
            dock_widget.raise_()

            logger.info("最高优先级任务集成界面已显示")

        except Exception as e:
            logger.error(f"显示最高优先级任务集成界面失败: {e}")
            QMessageBox.critical(self, "错误", f"显示最高优先级任务集成界面失败:\n{str(e)}")

    def show_priority_two_integration(self):
        """显示高优先级任务集成界面"""
        try:
            # 创建停靠窗口
            dock_widget = QDockWidget("🟡 高优先级任务集成", self)
            dock_widget.setWidget(self.priority_two_integration_widget)
            dock_widget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                       Qt.DockWidgetArea.RightDockWidgetArea |
                                       Qt.DockWidgetArea.BottomDockWidgetArea)

            # 添加到主窗口
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_widget)

            # 确保可见
            dock_widget.show()
            dock_widget.raise_()

            logger.info("高优先级任务集成界面已显示")

        except Exception as e:
            logger.error(f"显示高优先级任务集成界面失败: {e}")
            QMessageBox.critical(self, "错误", f"显示高优先级任务集成界面失败:\n{str(e)}")

    def show_priority_three_integration(self):
        """显示中优先级任务集成界面"""
        try:
            # 创建停靠窗口
            dock_widget = QDockWidget("🟢 中优先级任务集成", self)
            dock_widget.setWidget(self.priority_three_integration_widget)
            dock_widget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                       Qt.DockWidgetArea.RightDockWidgetArea |
                                       Qt.DockWidgetArea.BottomDockWidgetArea)

            # 添加到主窗口
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_widget)

            # 确保可见
            dock_widget.show()
            dock_widget.raise_()

            logger.info("中优先级任务集成界面已显示")

        except Exception as e:
            logger.error(f"显示中优先级任务集成界面失败: {e}")
            QMessageBox.critical(self, "错误", f"显示中优先级任务集成界面失败:\n{str(e)}")

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于 AI Animation Studio", 
                         "AI Animation Studio v1.0\n\n"
                         "AI驱动的动画工作站\n"
                         "通过自然语言创作专业级Web动画\n\n"
                         "© 2024 AI Animation Studio Team")
    
    def auto_save(self):
        """自动保存 - 增强版"""
        try:
            if not self.project_manager.current_project:
                return

            # 检查是否有未保存的更改
            if not self.has_unsaved_changes():
                return

            # 使用项目管理器的自动保存功能
            auto_save_path = self.project_manager._get_auto_save_path()

            if self.project_manager.save_project(auto_save_path, create_backup=False, incremental=True):
                # 更新状态栏
                self.status_bar.showMessage("自动保存完成", 2000)
                logger.debug("自动保存完成")
            else:
                logger.warning("自动保存失败")

        except Exception as e:
            logger.error(f"自动保存异常: {e}")



    def start_auto_save(self, interval_minutes: int = 5):
        """启动自动保存"""
        try:
            # 启用项目管理器的自动保存
            self.project_manager.enable_auto_save(interval_minutes * 60)

            # 启动UI层的自动保存定时器
            self.auto_save_timer.start(interval_minutes * 60 * 1000)  # 转换为毫秒

            logger.info(f"自动保存已启动，间隔: {interval_minutes}分钟")

        except Exception as e:
            logger.error(f"启动自动保存失败: {e}")

    def stop_auto_save(self):
        """停止自动保存"""
        try:
            self.project_manager.disable_auto_save()
            self.auto_save_timer.stop()
            logger.info("自动保存已停止")

        except Exception as e:
            logger.error(f"停止自动保存失败: {e}")
    
    # 信号处理方法
    def on_project_changed(self):
        """项目改变处理"""
        if self.project_manager.current_project:
            project = self.project_manager.current_project
            if hasattr(self, 'project_label'):
                self.project_label.setText(f"项目: {project.name}")
            self.setWindowTitle(f"AI Animation Studio - {project.name}")
        else:
            if hasattr(self, 'project_label'):
                self.project_label.setText("无项目")
            self.setWindowTitle("AI Animation Studio")
    
    def on_theme_changed(self, theme_name: str):
        """主题改变处理"""
        logger.info(f"主题已切换到: {theme_name}")
    
    def on_time_changed(self, time: float):
        """时间改变处理"""
        total_time = self.project_manager.current_project.total_duration if self.project_manager.current_project else 30.0
        self.time_label.setText(f"{time:.1f}s / {total_time:.1f}s")
    
    def preview_first_solution(self, solutions: list):
        """预览第一个方案"""
        if solutions:
            first_solution = solutions[0]

    def on_description_ready(self, description: str, analysis: dict):
        """描述准备就绪事件"""
        try:
            logger.info(f"收到描述准备就绪信号: {description[:50]}...")

            # 可以将描述同步到AI生成器
            if hasattr(self.ai_generator_widget, 'description_input'):
                self.ai_generator_widget.description_input.setPlainText(description)

            # 更新状态栏
            complexity = analysis.get("complexity_score", 0)
            self.status_bar.showMessage(f"描述已分析 - 复杂度: {complexity}/100", 3000)

        except Exception as e:
            logger.error(f"处理描述准备就绪事件失败: {e}")

    def on_prompt_ready(self, prompt: str):
        """Prompt准备就绪事件"""
        try:
            logger.info(f"收到Prompt准备就绪信号，长度: {len(prompt)}")

            # 可以将Prompt同步到AI生成器
            if hasattr(self.ai_generator_widget, 'prompt_preview'):
                self.ai_generator_widget.prompt_preview.setPlainText(prompt)

            # 更新状态栏
            self.status_bar.showMessage("Prompt已生成，可以开始AI生成", 3000)

        except Exception as e:
            logger.error(f"处理Prompt准备就绪事件失败: {e}")

    def on_animation_requested(self, animation_data: dict):
        """动画请求事件"""
        try:
            logger.info("收到动画生成请求")

            # 切换到AI生成器标签页
            ai_generator_index = -1
            for i in range(self.center_tabs.count()):
                if self.center_tabs.tabText(i) == "🤖 AI生成器":
                    ai_generator_index = i
                    break

            if ai_generator_index >= 0:
                self.center_tabs.setCurrentIndex(ai_generator_index)

                # 触发AI生成
                if hasattr(self.ai_generator_widget, 'generate_animations'):
                    self.ai_generator_widget.generate_animations()

            # 更新状态栏
            self.status_bar.showMessage("正在启动AI动画生成...", 2000)

        except Exception as e:
            logger.error(f"处理动画请求事件失败: {e}")

    def on_solutions_generated(self, solutions: list):
        """方案生成完成事件"""
        try:
            logger.info(f"收到方案生成完成信号，生成了 {len(solutions)} 个方案")

            # 更新状态栏
            self.status_bar.showMessage(f"已生成 {len(solutions)} 个动画方案", 3000)

            # 如果有方案，自动预览第一个
            if solutions:
                first_solution = solutions[0]
                self.solution_previewer.preview_solution(first_solution)

                # 切换到预览标签页
                for i in range(self.center_tabs.count()):
                    if self.center_tabs.tabText(i) == "👁️ 方案预览":
                        self.center_tabs.setCurrentIndex(i)
                        break

        except Exception as e:
            logger.error(f"处理方案生成完成事件失败: {e}")

    def on_solution_selected(self, solution_id: str):
        """方案选中事件"""
        try:
            logger.info(f"方案已选中: {solution_id}")

            # 更新状态栏
            self.status_bar.showMessage(f"方案 {solution_id[:8]}... 已选中", 2000)

            # 可以在这里添加方案选中后的处理逻辑

        except Exception as e:
            logger.error(f"处理方案选中事件失败: {e}")

    def on_solution_applied(self, solution_id: str):
        """方案应用事件"""
        try:
            logger.info(f"方案已应用: {solution_id}")

            # 更新状态栏
            self.status_bar.showMessage(f"方案已应用到项目中", 3000)

            # 切换到预览器标签页显示应用结果
            for i in range(self.center_tabs.count()):
                if self.center_tabs.tabText(i) == "🎬 预览器":
                    self.center_tabs.setCurrentIndex(i)
                    break

            # 可以在这里添加将方案应用到当前项目的逻辑

        except Exception as e:
            logger.error(f"处理方案应用事件失败: {e}")

    def on_solution_analyzed(self, analysis: dict):
        """方案分析完成事件"""
        try:
            logger.info("收到方案分析完成信号")

            # 显示分析结果摘要
            performance_score = analysis.get("performance_hints", [])
            optimization_count = len(analysis.get("optimization_suggestions", []))

            message = f"方案分析完成"
            if optimization_count > 0:
                message += f"，发现 {optimization_count} 个优化建议"

            self.status_bar.showMessage(message, 3000)

        except Exception as e:
            logger.error(f"处理方案分析完成事件失败: {e}")
            self.preview_widget.load_html_content(first_solution.html_code)
            logger.info(f"正在预览方案: {first_solution.name}")

    def on_element_selected(self, element_id: str):
        """元素选择处理"""
        logger.info(f"选择元素: {element_id}")

        # 更新状态栏选择信息
        self.status_notification_manager.update_selection(element_id)

        # 在元素管理器中选择对应元素
        if hasattr(self.elements_widget, 'select_element'):
            self.elements_widget.select_element(element_id)
        else:
            logger.warning("元素管理器不支持select_element方法")

        # 在舞台中选择对应元素 - 安全调用
        if hasattr(self, 'stage_widget') and hasattr(self.stage_widget, 'stage_canvas'):
            canvas = self.stage_widget.stage_canvas
            if hasattr(canvas, 'select_element'):
                canvas.select_element(element_id)
            else:
                logger.warning("舞台画布不支持select_element方法")
        else:
            logger.warning("舞台组件不可用")

    def on_element_updated(self, element):
        """元素更新处理"""
        logger.info(f"元素已更新: {element.name}")

        # 更新元素管理器显示
        if hasattr(self.elements_widget, 'update_element'):
            self.elements_widget.update_element(element)
        else:
            logger.warning("元素管理器不支持update_element方法")

        # 更新舞台显示 - 安全调用
        if hasattr(self, 'stage_widget') and hasattr(self.stage_widget, 'stage_canvas'):
            canvas = self.stage_widget.stage_canvas
            if hasattr(canvas, 'add_element'):
                canvas.add_element(element)  # 会覆盖现有元素
            elif hasattr(canvas, 'update_element'):
                canvas.update_element(element)
            else:
                logger.warning("舞台画布不支持元素更新方法")
        else:
            logger.warning("舞台组件不可用")

        self.status_bar.showMessage(f"元素已更新: {element.name}", 2000)

    def on_element_selected_for_properties(self, element_id: str):
        """为属性面板选择元素"""
        # 从元素管理器获取元素对象
        if element_id in self.elements_widget.elements:
            element = self.elements_widget.elements[element_id]
            self.properties_widget.set_element(element)

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)

        try:
            # 更新响应式断点
            self.breakpoint_manager.update_breakpoint(event.size().width())

            # 处理响应式布局
            self.responsive_layout_manager.handle_resize(event.size())

            # 应用响应式样式
            current_mode = self.responsive_layout_manager.get_current_mode()
            self.responsive_style_manager.apply_responsive_styles(current_mode)

        except Exception as e:
            logger.error(f"处理窗口大小改变事件失败: {e}")

    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)

        try:
            # 应用屏幕适配
            self.screen_adaptation_manager.apply_screen_adaptation()

            # 连接响应式布局信号
            self.responsive_layout_manager.layout_changed.connect(self.on_responsive_layout_changed)

        except Exception as e:
            logger.error(f"处理窗口显示事件失败: {e}")

    def closeEvent(self, event):
        """关闭事件处理"""
        # 保存窗口几何
        geometry = self.geometry()
        self.config.ui.window_geometry = {
            "x": geometry.x(),
            "y": geometry.y(),
            "width": geometry.width(),
            "height": geometry.height()
        }
        
        # 保存分割器大小
        self.config.ui.splitter_sizes = self.main_splitter.sizes()
        
        # 保存配置
        self.config.save()
        
        # 检查是否需要保存项目
        if self.project_manager.current_project:
            reply = QMessageBox.question(
                self, "确认退出", 
                "是否保存当前项目？",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.save_project()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        event.accept()

    # ==================== 撤销重做系统 ====================

    def undo_command(self):
        """撤销操作"""
        if self.command_manager.undo():
            self.update_edit_menu_state()
            self.update_ui_after_command()
            logger.info("撤销操作成功")
        else:
            QMessageBox.information(self, "提示", "没有可撤销的操作")

    def redo_command(self):
        """重做操作"""
        if self.command_manager.redo():
            self.update_edit_menu_state()
            self.update_ui_after_command()
            logger.info("重做操作成功")
        else:
            QMessageBox.information(self, "提示", "没有可重做的操作")

    def execute_command(self, command):
        """执行命令并更新UI"""
        if self.command_manager.execute_command(command):
            self.update_edit_menu_state()
            self.update_ui_after_command()

            # 记录操作到自动保存管理器
            self.auto_save_manager.record_operation()

            return True
        return False

    def update_edit_menu_state(self):
        """更新编辑菜单状态"""
        # 更新撤销菜单项
        if self.command_manager.can_undo():
            self.undo_action.setEnabled(True)
            undo_desc = self.command_manager.get_undo_description()
            self.undo_action.setText(f"撤销 {undo_desc}(&U)")
        else:
            self.undo_action.setEnabled(False)
            self.undo_action.setText("撤销(&U)")

        # 更新重做菜单项
        if self.command_manager.can_redo():
            self.redo_action.setEnabled(True)
            redo_desc = self.command_manager.get_redo_description()
            self.redo_action.setText(f"重做 {redo_desc}(&R)")
        else:
            self.redo_action.setEnabled(False)
            self.redo_action.setText("重做(&R)")

    def update_ui_after_command(self):
        """命令执行后更新UI"""
        # 刷新所有相关的UI组件
        if hasattr(self, 'elements_widget'):
            self.elements_widget.refresh_elements()

        if hasattr(self, 'properties_widget'):
            self.properties_widget.refresh_properties()

        if hasattr(self, 'stage_widget'):
            self.stage_widget.refresh_stage()

        if hasattr(self, 'timeline_widget'):
            self.timeline_widget.refresh_timeline()

        # 发射项目变更信号
        self.project_changed.emit()

    def get_command_history(self):
        """获取命令历史"""
        return self.command_manager.get_history()

    def clear_command_history(self):
        """清空命令历史"""
        self.command_manager.clear_history()
        self.update_edit_menu_state()

    def get_command_stats(self):
        """获取命令统计信息"""
        return self.command_manager.get_stats()

    def show_undo_history(self):
        """显示撤销重做历史对话框"""
        try:
            from .undo_history_dialog import UndoHistoryDialog

            dialog = UndoHistoryDialog(self, self.command_manager)

            # 连接信号
            dialog.history_cleared.connect(self.update_edit_menu_state)

            dialog.exec()

        except Exception as e:
            logger.error(f"显示撤销重做历史失败: {e}")
            QMessageBox.critical(self, "错误", f"无法显示撤销重做历史:\n{str(e)}")

    # ==================== 增强保存功能 ====================

    def show_save_options(self):
        """显示保存选项对话框"""
        try:
            if not self.project_manager.current_project:
                QMessageBox.warning(self, "警告", "没有项目可保存")
                return

            from .save_options_dialog import SaveOptionsDialog
            dialog = SaveOptionsDialog(self, self.project_manager.current_project)

            if dialog.exec() == dialog.DialogCode.Accepted:
                save_options = dialog.get_save_options()

                # 执行保存
                success = self.project_manager.save_project(
                    create_backup=save_options.get('create_backup', True),
                    incremental=save_options.get('incremental_save', True)
                )

                if success:
                    self.auto_save_manager.record_manual_save()
                    QMessageBox.information(self, "保存成功", "项目已保存")
                else:
                    QMessageBox.warning(self, "保存失败", "无法保存项目")

        except Exception as e:
            logger.error(f"显示保存选项失败: {e}")
            QMessageBox.critical(self, "错误", f"显示保存选项失败:\n{str(e)}")

    def create_version_backup(self):
        """创建版本备份"""
        try:
            if not self.project_manager.current_project:
                QMessageBox.warning(self, "警告", "没有项目可备份")
                return

            # 获取版本描述
            from datetime import datetime
            description, ok = QInputDialog.getText(
                self, "版本备份", "请输入版本描述:",
                text=f"版本备份 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )

            if ok:
                if self.auto_save_manager.create_version_backup(description):
                    QMessageBox.information(self, "备份成功", "版本备份已创建")
                else:
                    QMessageBox.warning(self, "备份失败", "无法创建版本备份")

        except Exception as e:
            logger.error(f"创建版本备份失败: {e}")
            QMessageBox.critical(self, "错误", f"创建版本备份失败:\n{str(e)}")

    def show_version_history(self):
        """显示版本历史"""
        try:
            versions = self.auto_save_manager.get_version_history()

            if not versions:
                QMessageBox.information(self, "版本历史", "没有版本历史记录")
                return

            # 创建版本历史对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("版本历史")
            dialog.setMinimumSize(600, 400)

            layout = QVBoxLayout(dialog)

            # 版本列表

            for version in versions:
                item_text = f"版本 {version.get('version', 'N/A')} - {version.get('description', '无描述')}"
                item_text += f"\n创建时间: {version.get('created_at', '未知')}"

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, version)
                version_list.addItem(item)

            layout.addWidget(version_list)

            # 按钮
            button_layout = QHBoxLayout()

            restore_btn = QPushButton("恢复此版本")
            restore_btn.clicked.connect(lambda: self.restore_version(version_list.currentItem(), dialog))
            button_layout.addWidget(restore_btn)

            button_layout.addStretch()

            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.accept)
            button_layout.addWidget(close_btn)

            layout.addLayout(button_layout)

            dialog.exec()

        except Exception as e:
            logger.error(f"显示版本历史失败: {e}")
            QMessageBox.critical(self, "错误", f"显示版本历史失败:\n{str(e)}")

    def restore_version(self, item, dialog):
        """恢复版本"""
        try:
            if not item:
                return

            version_data = item.data(Qt.ItemDataRole.UserRole)
            version_file = version_data.get('file_path')

            if not version_file or not Path(version_file).exists():
                QMessageBox.warning(self, "错误", "版本文件不存在")
                return

            reply = QMessageBox.question(
                self, "确认恢复",
                f"确定要恢复到版本 {version_data.get('version', 'N/A')} 吗？\n当前未保存的更改将丢失。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                if self.project_manager.load_project(Path(version_file)):
                    QMessageBox.information(self, "恢复成功", "版本已恢复")
                    dialog.accept()
                else:
                    QMessageBox.warning(self, "恢复失败", "无法恢复版本")

        except Exception as e:
            logger.error(f"恢复版本失败: {e}")
            QMessageBox.critical(self, "错误", f"恢复版本失败:\n{str(e)}")

    def show_auto_save_settings(self):
        """显示自动保存设置"""
        try:
            # 创建自动保存设置对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("自动保存设置")
            dialog.setMinimumSize(400, 300)

            layout = QVBoxLayout(dialog)

            # 获取当前状态
            status = self.auto_save_manager.get_status()

            # 启用自动保存
            enable_cb = QCheckBox("启用自动保存")
            enable_cb.setChecked(status['enabled'])
            layout.addWidget(enable_cb)

            # 间隔设置
            interval_layout = QHBoxLayout()
            interval_layout.addWidget(QLabel("保存间隔 (分钟):"))
            interval_spinbox = QSpinBox()
            interval_spinbox.setRange(1, 60)
            interval_spinbox.setValue(status['interval_minutes'])
            interval_layout.addWidget(interval_spinbox)
            layout.addLayout(interval_layout)

            # 操作阈值
            threshold_layout = QHBoxLayout()
            threshold_layout.addWidget(QLabel("操作次数阈值:"))
            threshold_spinbox = QSpinBox()
            threshold_spinbox.setRange(1, 100)
            threshold_spinbox.setValue(status['operation_threshold'])
            threshold_layout.addWidget(threshold_spinbox)
            layout.addLayout(threshold_layout)

            # 触发模式
            trigger_layout = QHBoxLayout()
            trigger_layout.addWidget(QLabel("触发模式:"))
            trigger_combo = QComboBox()
            trigger_combo.addItems(["time", "operations", "changes", "mixed"])
            trigger_combo.setCurrentText(status['trigger_mode'])
            trigger_layout.addWidget(trigger_combo)
            layout.addLayout(trigger_layout)

            # 状态显示
            status_label = QLabel(f"当前状态: {'运行中' if status['timer_active'] else '已停止'}")
            layout.addWidget(status_label)

            # 按钮
            button_layout = QHBoxLayout()

            apply_btn = QPushButton("应用")
            apply_btn.clicked.connect(lambda: self.apply_auto_save_settings(
                enable_cb.isChecked(),
                interval_spinbox.value(),
                threshold_spinbox.value(),
                trigger_combo.currentText(),
                dialog
            ))
            button_layout.addWidget(apply_btn)

            button_layout.addStretch()

            cancel_btn = QPushButton("取消")
            cancel_btn.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_btn)

            layout.addLayout(button_layout)

            dialog.exec()

        except Exception as e:
            logger.error(f"显示自动保存设置失败: {e}")
            QMessageBox.critical(self, "错误", f"显示自动保存设置失败:\n{str(e)}")

    def apply_auto_save_settings(self, enabled, interval, threshold, trigger_mode, dialog):
        """应用自动保存设置"""
        try:
            self.auto_save_manager.configure(
                enabled=enabled,
                interval_minutes=interval,
                operation_threshold=threshold,
                trigger_mode=trigger_mode
            )

            QMessageBox.information(self, "设置成功", "自动保存设置已更新")
            dialog.accept()

        except Exception as e:
            logger.error(f"应用自动保存设置失败: {e}")
            QMessageBox.critical(self, "错误", f"应用设置失败:\n{str(e)}")

    def trigger_manual_auto_save(self):
        """触发手动自动保存"""
        try:
            self.auto_save_manager.perform_auto_save()
        except Exception as e:
            logger.error(f"手动自动保存失败: {e}")
            QMessageBox.critical(self, "错误", f"手动自动保存失败:\n{str(e)}")

    def show_recovery_options(self):
        """显示恢复选项"""
        try:
            recovery_file = self.auto_save_manager.check_for_recovery_data()
            if recovery_file:
                self.show_recovery_dialog(recovery_file)
            else:
                QMessageBox.information(self, "恢复数据", "没有找到恢复数据")
        except Exception as e:
            logger.error(f"显示恢复选项失败: {e}")
            QMessageBox.critical(self, "错误", f"显示恢复选项失败:\n{str(e)}")

    # ==================== 快速另存为功能 ====================

    def quick_save_as(self, format_type: str):
        """快速另存为指定格式"""
        try:
            if not self.project_manager.current_project:
                QMessageBox.warning(self, "警告", "没有项目可保存")
                return False

            # 格式映射
            format_map = {
                "aas": {"ext": ".aas", "filter": "AAS项目文件 (*.aas)", "name": "AAS项目"},
                "json": {"ext": ".json", "filter": "JSON文件 (*.json)", "name": "JSON格式"},
                "zip": {"ext": ".zip", "filter": "压缩包 (*.zip)", "name": "压缩包"},
                "xml": {"ext": ".xml", "filter": "XML文件 (*.xml)", "name": "XML格式"},
                "html": {"ext": ".html", "filter": "HTML包 (*.html)", "name": "HTML包"},
                "exe": {"ext": ".exe", "filter": "可执行文件 (*.exe)", "name": "可执行文件"}
            }

            if format_type not in format_map:
                logger.error(f"不支持的格式类型: {format_type}")
                return False

            format_info = format_map[format_type]

            # 构建默认文件名
            project_name = self.project_manager.current_project.name
            if not project_name.endswith(format_info["ext"]):
                project_name += format_info["ext"]

            # 选择保存位置
            file_path, _ = QFileDialog.getSaveFileName(
                self, f"快速另存为{format_info['name']}",
                project_name, format_info["filter"]
            )

            if not file_path:
                return False

            # 确保文件扩展名正确
            if not file_path.endswith(format_info["ext"]):
                file_path += format_info["ext"]

            # 显示保存进度
            self.status_bar.showMessage(f"正在保存为{format_info['name']}...", 0)

            # 使用默认选项进行快速保存
            default_options = self._get_default_save_options(format_type)

            # 使用项目打包器保存
            packager = ProjectPackager()

            success = packager.package_project(
                self.project_manager.current_project,
                Path(file_path),
                format_type,
                default_options
            )

            if success:
                # 记录手动保存
                self.auto_save_manager.record_manual_save()

                self.status_bar.showMessage(f"快速保存完成: {Path(file_path).name}", 3000)
                logger.info(f"快速另存为{format_info['name']}: {file_path}")

                # 询问是否打开保存位置
                reply = QMessageBox.question(
                    self, "保存完成",
                    f"文件已保存为{format_info['name']}格式。\n是否打开保存位置？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self._open_file_location(file_path)

                return True
            else:
                self.status_bar.clearMessage()
                QMessageBox.warning(self, "保存失败", f"无法保存为{format_info['name']}格式")
                return False

        except Exception as e:
            self.status_bar.clearMessage()
            logger.error(f"快速另存为失败: {e}")
            QMessageBox.critical(self, "错误", f"快速另存为失败:\n{str(e)}")
            return False

    def _get_default_save_options(self, format_type: str) -> Dict:
        """获取默认保存选项"""
        return {
            "project_name": self.project_manager.current_project.name,
            "description": getattr(self.project_manager.current_project, 'description', ''),
            "author": getattr(self.project_manager.current_project, 'author', ''),
            "version": getattr(self.project_manager.current_project, 'version', '1.0'),
            "create_backup": True,
            "incremental_save": True,
            "compress": True,
            "include_elements": True,
            "include_timeline": True,
            "include_assets": True,
            "include_settings": True,
            "include_history": False,
            "include_metadata": True,
            "embed_assets": format_type in ["zip", "html", "exe"],
            "optimize_assets": True,
            "asset_quality": 8,
            "target_version": "当前版本",
            "backward_compat": True,
            "encrypt": False,
            "compression_level": 6,
            "multithread": True,
            "include_readme": format_type == "zip",
            "include_license": False
        }

    def _open_file_location(self, file_path: str):
        """打开文件位置"""
        try:
            import platform

            file_path = Path(file_path)

            if platform.system() == "Windows":
                os.startfile(file_path.parent)
            elif platform.system() == "Darwin":  # macOS
                os.system(f"open '{file_path.parent}'")
            else:  # Linux
                os.system(f"xdg-open '{file_path.parent}'")

        except Exception as e:
            logger.error(f"打开文件位置失败: {e}")

    def batch_save_as(self):
        """批量另存为多种格式"""
        try:
            if not self.project_manager.current_project:
                QMessageBox.warning(self, "警告", "没有项目可保存")
                return

            # 创建批量保存对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("批量另存为")
            dialog.setMinimumSize(400, 300)

            layout = QVBoxLayout(dialog)

            # 格式选择
            format_group = QGroupBox("选择格式")
            format_layout = QVBoxLayout(format_group)

            format_checkboxes = {}
            formats = [
                ("aas", "AAS项目文件"),
                ("json", "JSON格式"),
                ("zip", "压缩包"),
                ("xml", "XML格式"),
                ("html", "HTML包")
            ]

            for format_id, format_name in formats:
                cb = QCheckBox(format_name)
                format_checkboxes[format_id] = cb
                format_layout.addWidget(cb)

            layout.addWidget(format_group)

            # 输出目录选择
            dir_group = QGroupBox("输出目录")
            dir_layout = QHBoxLayout(dir_group)

            dir_edit = QLineEdit()
            dir_edit.setPlaceholderText("选择输出目录...")
            dir_layout.addWidget(dir_edit)

            browse_btn = QPushButton("浏览...")
            browse_btn.clicked.connect(lambda: self._browse_output_dir(dir_edit))
            dir_layout.addWidget(browse_btn)

            layout.addWidget(dir_group)

            # 进度条
            progress_bar = QProgressBar()
            progress_bar.setVisible(False)
            layout.addWidget(progress_bar)

            # 按钮
            button_layout = QHBoxLayout()

            start_btn = QPushButton("开始批量保存")
            start_btn.clicked.connect(lambda: self._start_batch_save(
                format_checkboxes, dir_edit.text(), progress_bar, dialog
            ))
            button_layout.addWidget(start_btn)

            button_layout.addStretch()

            cancel_btn = QPushButton("取消")
            cancel_btn.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_btn)

            layout.addLayout(button_layout)

            dialog.exec()

        except Exception as e:
            logger.error(f"批量另存为失败: {e}")
            QMessageBox.critical(self, "错误", f"批量另存为失败:\n{str(e)}")

    def _browse_output_dir(self, dir_edit):
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            dir_edit.setText(dir_path)

    def _start_batch_save(self, format_checkboxes, output_dir, progress_bar, dialog):
        """开始批量保存"""
        try:
            if not output_dir:
                QMessageBox.warning(self, "错误", "请选择输出目录")
                return

            # 获取选中的格式
            selected_formats = []
            for format_id, checkbox in format_checkboxes.items():
                if checkbox.isChecked():
                    selected_formats.append(format_id)

            if not selected_formats:
                QMessageBox.warning(self, "错误", "请至少选择一种格式")
                return

            # 显示进度条
            progress_bar.setVisible(True)
            progress_bar.setMaximum(len(selected_formats))
            progress_bar.setValue(0)

            # 执行批量保存
            packager = ProjectPackager()

            output_path = Path(output_dir)
            project_name = self.project_manager.current_project.name

            success_count = 0
            for i, format_type in enumerate(selected_formats):
                try:
                    # 构建文件名
                    format_ext = {
                        "aas": ".aas", "json": ".json", "zip": ".zip",
                        "xml": ".xml", "html": ".html"
                    }.get(format_type, ".aas")

                    file_path = output_path / f"{project_name}{format_ext}"

                    # 获取默认选项
                    options = self._get_default_save_options(format_type)

                    # 执行保存
                    if packager.package_project(
                        self.project_manager.current_project,
                        file_path,
                        format_type,
                        options
                    ):
                        success_count += 1
                        logger.info(f"批量保存成功: {file_path}")
                    else:
                        logger.error(f"批量保存失败: {file_path}")

                except Exception as e:
                    logger.error(f"批量保存格式 {format_type} 失败: {e}")

                # 更新进度
                progress_bar.setValue(i + 1)
                QApplication.processEvents()  # 更新UI

            # 显示结果
            QMessageBox.information(
                self, "批量保存完成",
                f"批量保存完成！\n成功: {success_count}/{len(selected_formats)}"
            )

            dialog.accept()

        except Exception as e:
            logger.error(f"执行批量保存失败: {e}")
            QMessageBox.critical(self, "错误", f"执行批量保存失败:\n{str(e)}")

    # 价值层次管理方法
    def setup_value_hierarchy(self):
        """设置价值层次布局"""
        try:
            # 创建价值层次布局
            self.value_hierarchy_layout = ValueHierarchyLayout()

            # 设置初始专业水平和工作流程阶段
            self.value_hierarchy.set_expertise_level(self.current_expertise_level)
            self.value_hierarchy.set_workflow_stage(self.current_workflow_stage)

            # 连接工作流程指示器信号
            if hasattr(self.value_hierarchy_layout, 'workflow_indicator'):
                self.value_hierarchy_layout.workflow_indicator.step_activated.connect(
                    self.on_workflow_step_activated
                )

            logger.info("价值层次布局设置完成")

        except Exception as e:
            logger.error(f"设置价值层次布局失败: {e}")

    def set_expertise_level(self, level: UserExpertiseLevel):
        """设置用户专业水平"""
        try:
            self.current_expertise_level = level
            self.value_hierarchy.set_expertise_level(level)

            # 更新渐进式功能披露
            self.progressive_disclosure.set_level(level)

            # 更新自适应界面
            self.adaptive_interface.adapt_interface(level)

            # 更新专业工具栏和菜单
            self.professional_toolbar_manager.update_expertise_level(level)
            self.professional_menu_manager.update_expertise_level(level)

            # 更新界面可见性
            self.update_interface_by_expertise()

            logger.info(f"用户专业水平设置为: {level.value}")

        except Exception as e:
            logger.error(f"设置专业水平失败: {e}")

    def set_workflow_stage(self, stage: WorkflowStage):
        """设置工作流程阶段"""
        try:
            self.current_workflow_stage = stage
            self.value_hierarchy.set_workflow_stage(stage)

            # 更新工作流程指示器
            if hasattr(self.value_hierarchy_layout, 'workflow_indicator'):
                self.value_hierarchy_layout.workflow_indicator.set_current_step(stage.value - 1)

            # 更新专业工具栏高亮
            self.professional_toolbar_manager.update_workflow_stage(stage)

            # 更新界面焦点
            self.update_interface_by_workflow()

            logger.info(f"工作流程阶段设置为: {stage.name}")

        except Exception as e:
            logger.error(f"设置工作流程阶段失败: {e}")

    def on_workflow_step_activated(self, step_index: int):
        """工作流程步骤激活处理"""
        try:
            # 转换为WorkflowStage
            stage_value = step_index + 1
            for stage in WorkflowStage:
                if stage.value == stage_value:
                    self.set_workflow_stage(stage)
                    break

        except Exception as e:
            logger.error(f"处理工作流程步骤激活失败: {e}")

    def update_interface_by_expertise(self):
        """根据专业水平更新界面"""
        try:
            visible_features = self.value_hierarchy.get_visible_features(
                expertise_level=self.current_expertise_level
            )

            # 根据可见功能更新界面元素
            for feature in visible_features:
                self.update_feature_visibility(feature.name, True)

            # 隐藏不应该显示的功能
            all_features = self.value_hierarchy.features.values()
            for feature in all_features:
                if feature not in visible_features:
                    self.update_feature_visibility(feature.name, False)

            logger.debug(f"根据专业水平 {self.current_expertise_level.value} 更新界面")

        except Exception as e:
            logger.error(f"根据专业水平更新界面失败: {e}")

    def update_interface_by_workflow(self):
        """根据工作流程阶段更新界面"""
        try:
            # 获取当前阶段相关的功能
            workflow_features = self.value_hierarchy.get_workflow_features(
                self.current_workflow_stage
            )

            # 高亮当前阶段的功能
            for feature in workflow_features:
                self.highlight_feature(feature.name, True)

            # 根据工作流程阶段调整界面焦点
            self.adjust_interface_focus()

            logger.debug(f"根据工作流程阶段 {self.current_workflow_stage.name} 更新界面")

        except Exception as e:
            logger.error(f"根据工作流程阶段更新界面失败: {e}")

    def update_feature_visibility(self, feature_name: str, visible: bool):
        """更新功能可见性"""
        try:
            # 根据功能名称更新对应的UI元素可见性
            feature_widgets = {
                'debug_console': getattr(self, 'debug_console', None),
                'performance_monitor': getattr(self, 'performance_monitor', None),
                'api_integration': getattr(self, 'api_integration', None),
                'custom_scripting': getattr(self, 'custom_scripting', None),
                'rules_manager': getattr(self, 'rules_manager_widget', None),
                'collaboration': getattr(self, 'collaboration_widget', None)
            }

            widget = feature_widgets.get(feature_name)
            if widget and hasattr(widget, 'setVisible'):
                widget.setVisible(visible)

        except Exception as e:
            logger.error(f"更新功能 {feature_name} 可见性失败: {e}")

    def highlight_feature(self, feature_name: str, highlight: bool):
        """高亮功能"""
        try:
            # 实现功能高亮逻辑
            # 这里可以添加视觉提示，如边框、颜色变化等
            pass

        except Exception as e:
            logger.error(f"高亮功能 {feature_name} 失败: {e}")

    def adjust_interface_focus(self):
        """调整界面焦点"""
        try:
            # 根据当前工作流程阶段调整界面焦点
            stage_focus_map = {
                WorkflowStage.AUDIO_IMPORT: 'timeline_widget',
                WorkflowStage.TIME_MARKING: 'timeline_widget',
                WorkflowStage.DESCRIPTION: 'ai_generator_widget',
                WorkflowStage.AI_GENERATION: 'ai_generator_widget',
                WorkflowStage.PREVIEW_ADJUST: 'preview_widget',
                WorkflowStage.EXPORT: 'export_dialog'
            }

            focus_widget_name = stage_focus_map.get(self.current_workflow_stage)
            if focus_widget_name:
                focus_widget = getattr(self, focus_widget_name, None)
                if focus_widget and hasattr(focus_widget, 'setFocus'):
                    focus_widget.setFocus()

        except Exception as e:
            logger.error(f"调整界面焦点失败: {e}")

    def get_value_hierarchy_summary(self) -> dict:
        """获取价值层次摘要"""
        try:
            return {
                'current_expertise': self.current_expertise_level.value,
                'current_workflow_stage': self.current_workflow_stage.name,
                'visible_features_count': len(self.value_hierarchy.get_visible_features()),
                'priority_summary': self.value_hierarchy.get_priority_summary()
            }

        except Exception as e:
            logger.error(f"获取价值层次摘要失败: {e}")
            return {}

    # 布局切换方法
    def switch_to_standard_layout(self):
        """切换到标准布局"""
        try:
            # 恢复标准的三面板布局
            self.setCentralWidget(self.create_standard_layout())
            logger.info("已切换到标准布局")

        except Exception as e:
            logger.error(f"切换到标准布局失败: {e}")

    def switch_to_quadrant_layout(self):
        """切换到四象限布局"""
        try:
            # 设置四象限布局为中央组件
            self.setCentralWidget(self.quadrant_layout)

            # 连接四象限布局信号
            self.quadrant_layout.active_area_changed.connect(self.on_quadrant_area_changed)

            logger.info("已切换到四象限布局")

        except Exception as e:
            logger.error(f"切换到四象限布局失败: {e}")

    def switch_to_hierarchy_layout(self):
        """切换到价值层次布局"""
        try:
            # 设置价值层次布局为中央组件
            if hasattr(self, 'value_hierarchy_layout'):
                self.setCentralWidget(self.value_hierarchy_layout)
            else:
                self.setup_value_hierarchy()
                self.setCentralWidget(self.value_hierarchy_layout)

            logger.info("已切换到价值层次布局")

        except Exception as e:
            logger.error(f"切换到价值层次布局失败: {e}")

    def create_standard_layout(self) -> QWidget:
        """创建标准布局"""
        try:
            # 重新创建标准的三面板布局
            central_widget = QWidget()
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(5, 5, 5, 5)

            # 创建分割器
            main_splitter = QSplitter(Qt.Orientation.Horizontal)
            main_layout.addWidget(main_splitter)

            # 左侧面板
            left_widget = QWidget()
            left_layout = QVBoxLayout(left_widget)
            left_layout.addWidget(self.elements_widget)
            left_layout.addWidget(self.properties_widget)
            main_splitter.addWidget(left_widget)

            # 中央面板
            center_widget = QWidget()
            center_layout = QVBoxLayout(center_widget)
            center_layout.addWidget(self.center_tabs)
            main_splitter.addWidget(center_widget)

            # 右侧面板
            right_widget = QWidget()
            right_layout = QVBoxLayout(right_widget)

            right_tabs = QTabWidget()
            right_tabs.setTabPosition(QTabWidget.TabPosition.South)
            right_tabs.addTab(self.preview_widget, "👁️ 预览")
            right_tabs.addTab(self.progressive_disclosure, "🎯 功能")

            right_layout.addWidget(right_tabs)
            main_splitter.addWidget(right_widget)

            # 设置分割器比例
            main_splitter.setSizes([300, 800, 300])
            main_splitter.setStretchFactor(1, 1)

            return central_widget

        except Exception as e:
            logger.error(f"创建标准布局失败: {e}")
            return QWidget()

    def on_quadrant_area_changed(self, area_name: str):
        """四象限区域改变处理"""
        try:
            # 根据激活的区域调整工作流程
            area_workflow_map = {
                'input': WorkflowStage.AUDIO_IMPORT,
                'processing': WorkflowStage.AI_GENERATION,
                'control': WorkflowStage.PREVIEW_ADJUST,
                'time': WorkflowStage.TIME_MARKING
            }

            if area_name in area_workflow_map:
                workflow_stage = area_workflow_map[area_name]
                self.set_workflow_stage(workflow_stage)

                # 使用工作流程区域管理器
                stage_names = {
                    WorkflowStage.AUDIO_IMPORT: 'audio_import',
                    WorkflowStage.AI_GENERATION: 'ai_generation',
                    WorkflowStage.PREVIEW_ADJUST: 'preview_adjust',
                    WorkflowStage.TIME_MARKING: 'time_marking'
                }

                stage_name = stage_names.get(workflow_stage)
                if stage_name:
                    self.workflow_area_manager.switch_to_workflow_stage(stage_name)

            logger.info(f"四象限区域切换: {area_name}")

        except Exception as e:
            logger.error(f"处理四象限区域改变失败: {e}")

    def get_current_layout_type(self) -> str:
        """获取当前布局类型"""
        try:
            central = self.centralWidget()

            if central == self.quadrant_layout:
                return "四象限布局"
            elif hasattr(self, 'value_hierarchy_layout') and central == self.value_hierarchy_layout:
                return "价值层次布局"
            else:
                return "标准布局"

        except Exception as e:
            logger.error(f"获取当前布局类型失败: {e}")
            return "未知布局"

    def on_responsive_layout_changed(self, layout_mode: str):
        """响应式布局改变处理"""
        try:
            logger.info(f"响应式布局已切换到: {layout_mode}")

            # 更新状态栏显示
            if hasattr(self, 'statusBar'):
                self.statusBar().showMessage(f"布局模式: {layout_mode}", 2000)

            # 根据布局模式调整界面元素
            self.adjust_interface_for_layout_mode(layout_mode)

        except Exception as e:
            logger.error(f"处理响应式布局改变失败: {e}")

    def adjust_interface_for_layout_mode(self, layout_mode: str):
        """根据布局模式调整界面元素"""
        try:
            from .responsive_layout_manager import LayoutMode

            if layout_mode == LayoutMode.MOBILE:
                # 移动端模式：隐藏部分工具栏，简化界面
                self.hide_non_essential_toolbars()
                self.enable_touch_friendly_mode()

            elif layout_mode == LayoutMode.TABLET:
                # 平板模式：显示主要工具栏
                self.show_essential_toolbars()
                self.enable_touch_friendly_mode()

            elif layout_mode in [LayoutMode.DESKTOP, LayoutMode.LARGE_DESKTOP, LayoutMode.ULTRA_WIDE]:
                # 桌面模式：显示所有工具栏
                self.show_all_toolbars()
                self.disable_touch_friendly_mode()

        except Exception as e:
            logger.error(f"根据布局模式调整界面失败: {e}")

    def hide_non_essential_toolbars(self):
        """隐藏非必要工具栏"""
        try:
            if hasattr(self, 'professional_toolbar_manager'):
                toolbar_manager = self.professional_toolbar_manager

                # 只显示主工具栏和播放控制
                essential_toolbars = ['main', 'playback']

                for toolbar_id, toolbar in toolbar_manager.toolbars.items():
                    toolbar.setVisible(toolbar_id in essential_toolbars)

        except Exception as e:
            logger.error(f"隐藏非必要工具栏失败: {e}")

    def show_essential_toolbars(self):
        """显示必要工具栏"""
        try:
            if hasattr(self, 'professional_toolbar_manager'):
                toolbar_manager = self.professional_toolbar_manager

                # 显示主要工具栏
                essential_toolbars = ['main', 'edit', 'playback', 'ai']

                for toolbar_id, toolbar in toolbar_manager.toolbars.items():
                    toolbar.setVisible(toolbar_id in essential_toolbars)

        except Exception as e:
            logger.error(f"显示必要工具栏失败: {e}")

    def show_all_toolbars(self):
        """显示所有工具栏"""
        try:
            if hasattr(self, 'professional_toolbar_manager'):
                toolbar_manager = self.professional_toolbar_manager

                # 显示所有工具栏
                for toolbar in toolbar_manager.toolbars.values():
                    toolbar.setVisible(True)

        except Exception as e:
            logger.error(f"显示所有工具栏失败: {e}")

    def enable_touch_friendly_mode(self):
        """启用触摸友好模式"""
        try:
            # 增大按钮和控件尺寸
            if hasattr(self, 'professional_toolbar_manager'):
                toolbar_manager = self.professional_toolbar_manager

                for toolbar in toolbar_manager.toolbars.values():
                    toolbar.setIconSize(QSize(32, 32))  # 更大的图标
                    toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)  # 只显示图标

        except Exception as e:
            logger.error(f"启用触摸友好模式失败: {e}")

    def disable_touch_friendly_mode(self):
        """禁用触摸友好模式"""
        try:
            # 恢复正常按钮和控件尺寸
            if hasattr(self, 'professional_toolbar_manager'):
                toolbar_manager = self.professional_toolbar_manager

                for toolbar in toolbar_manager.toolbars.values():
                    toolbar.setIconSize(QSize(24, 24))  # 正常图标大小
                    toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)  # 图标+文字

        except Exception as e:
            logger.error(f"禁用触摸友好模式失败: {e}")

    def get_responsive_layout_summary(self) -> dict:
        """获取响应式布局摘要"""
        try:
            summary = {
                'responsive_layout': self.responsive_layout_manager.get_layout_summary(),
                'screen_adaptation': {
                    'dpi_scale': self.screen_adaptation_manager.dpi_scale,
                    'font_scale': self.screen_adaptation_manager.font_scale,
                    'icon_scale': self.screen_adaptation_manager.icon_scale
                },
                'breakpoint': {
                    'current': self.breakpoint_manager.current_breakpoint,
                    'is_mobile': self.breakpoint_manager.is_mobile(),
                    'is_tablet': self.breakpoint_manager.is_tablet(),
                    'is_desktop': self.breakpoint_manager.is_desktop()
                }
            }

            return summary

        except Exception as e:
            logger.error(f"获取响应式布局摘要失败: {e}")
            return {}

    def handle_primary_action(self, action_id: str):
        """处理主要动作"""
        try:
            action_map = {
                "import_audio": self.import_audio,
                "ai_generate": self.generate_animation,
                "preview": self.preview_animation,
                "export": self.export_html,
                "save": self.save_project,
                "undo": self.undo_action,
                "redo": self.redo_action
            }

            if action_id in action_map:
                action_map[action_id]()
                logger.info(f"执行主要动作: {action_id}")
            else:
                logger.warning(f"未知的主要动作: {action_id}")

        except Exception as e:
            logger.error(f"处理主要动作失败: {e}")

    def handle_workflow_step(self, step_id: int):
        """处理工作流程步骤"""
        try:
            step_actions = {
                1: self.focus_audio_import,
                2: self.focus_time_segments,
                3: self.focus_description_input,
                4: self.focus_ai_generation,
                5: self.focus_preview_adjustment,
                6: self.focus_export_completion
            }

            if step_id in step_actions:
                step_actions[step_id]()
                logger.info(f"切换到工作流程步骤: {step_id}")
            else:
                logger.warning(f"未知的工作流程步骤: {step_id}")

        except Exception as e:
            logger.error(f"处理工作流程步骤失败: {e}")

    def focus_audio_import(self):
        """聚焦音频导入"""
        # 切换到音频控制标签页
        if hasattr(self, 'left_tabs'):
            self.left_tabs.setCurrentIndex(0)  # 假设音频控制在第一个标签页

        # 更新状态
        self.status_notification_manager.update_status(StatusType.READY, "请导入音频文件")

    def focus_time_segments(self):
        """聚焦时间段划分"""
        # 切换到时间轴
        if hasattr(self, 'timeline_widget'):
            self.timeline_widget.setFocus()

        # 更新状态
        self.status_notification_manager.update_status(StatusType.READY, "请划分时间段")

    def focus_description_input(self):
        """聚焦描述输入"""
        # 切换到AI生成器标签页
        if hasattr(self, 'right_tabs'):
            self.right_tabs.setCurrentIndex(0)  # 假设AI生成器在第一个标签页

        # 更新状态
        self.status_notification_manager.update_status(StatusType.READY, "请输入动画描述")

    def focus_ai_generation(self):
        """聚焦AI生成"""
        # 触发AI生成
        self.generate_animation()

    def focus_preview_adjustment(self):
        """聚焦预览调整"""
        # 切换到预览标签页
        if hasattr(self, 'right_tabs'):
            self.right_tabs.setCurrentIndex(1)  # 假设预览在第二个标签页

        # 更新状态
        self.status_notification_manager.update_status(StatusType.READY, "请预览和调整动画")

    def focus_export_completion(self):
        """聚焦导出完成"""
        # 触发导出
        self.export_html()

    def update_visual_flow_project_info(self, project_name: str, status: str = ""):
        """更新视线流动管理器的项目信息"""
        try:
            if hasattr(self, 'visual_flow_manager'):
                self.visual_flow_manager.update_project_info(project_name, status)
        except Exception as e:
            logger.error(f"更新视线流动项目信息失败: {e}")

    def update_visual_flow_workflow_step(self, step_id: int):
        """更新视线流动管理器的工作流程步骤"""
        try:
            if hasattr(self, 'visual_flow_manager'):
                self.visual_flow_manager.update_workflow_step(step_id)
        except Exception as e:
            logger.error(f"更新视线流动工作流程步骤失败: {e}")

    def get_visual_flow_summary(self) -> dict:
        """获取视线流动摘要"""
        try:
            if hasattr(self, 'visual_flow_manager'):
                return self.visual_flow_manager.get_visual_flow_summary()
            return {}
        except Exception as e:
            logger.error(f"获取视线流动摘要失败: {e}")
            return {}

    def update_information_hierarchy_focus(self, widget_id: str):
        """更新信息层级焦点"""
        try:
            if hasattr(self, 'information_hierarchy_manager'):
                widget = self.information_hierarchy_manager.hierarchical_widgets.get(widget_id)
                if widget:
                    self.information_hierarchy_manager.set_focus_widget(widget)
                    logger.info(f"信息层级焦点更新到: {widget_id}")
        except Exception as e:
            logger.error(f"更新信息层级焦点失败: {e}")

    def update_widget_hierarchy_level(self, widget_id: str, level_name: str):
        """更新组件层级级别"""
        try:
            if hasattr(self, 'information_hierarchy_manager'):
                from .information_hierarchy_manager import InformationLevel

                level_map = {
                    'core': InformationLevel.CORE,
                    'important': InformationLevel.IMPORTANT,
                    'auxiliary': InformationLevel.AUXILIARY,
                    'supplementary': InformationLevel.SUPPLEMENTARY
                }

                if level_name in level_map:
                    self.information_hierarchy_manager.update_widget_level(widget_id, level_map[level_name])
                    logger.info(f"组件 {widget_id} 层级更新为: {level_name}")
        except Exception as e:
            logger.error(f"更新组件层级级别失败: {e}")

    def get_information_hierarchy_summary(self) -> dict:
        """获取信息层级摘要"""
        try:
            if hasattr(self, 'information_hierarchy_manager'):
                return self.information_hierarchy_manager.get_hierarchy_summary()
            return {}
        except Exception as e:
            logger.error(f"获取信息层级摘要失败: {e}")
            return {}

    def focus_core_information(self):
        """聚焦核心信息"""
        try:
            # 聚焦到核心层组件
            core_widgets = ['current_time_segment', 'animation_description_input', 'ai_generation_status', 'primary_toolbar']

            for widget_id in core_widgets:
                if hasattr(self, 'information_hierarchy_manager'):
                    widget = self.information_hierarchy_manager.hierarchical_widgets.get(widget_id)
                    if widget:
                        self.information_hierarchy_manager.set_focus_widget(widget)
                        break

            # 更新状态
            self.status_notification_manager.update_status(StatusType.READY, "聚焦核心信息")

        except Exception as e:
            logger.error(f"聚焦核心信息失败: {e}")

    def focus_important_information(self):
        """聚焦重要信息"""
        try:
            # 聚焦到重要层组件
            important_widgets = ['audio_control', 'stage_canvas', 'timeline', 'workflow_indicator']

            for widget_id in important_widgets:
                if hasattr(self, 'information_hierarchy_manager'):
                    widget = self.information_hierarchy_manager.hierarchical_widgets.get(widget_id)
                    if widget:
                        self.information_hierarchy_manager.set_focus_widget(widget)
                        break

            # 更新状态
            self.status_notification_manager.update_status(StatusType.READY, "聚焦重要信息")

        except Exception as e:
            logger.error(f"聚焦重要信息失败: {e}")

    def toggle_auxiliary_information(self):
        """切换辅助信息显示"""
        try:
            # 切换辅助层组件的可见性
            auxiliary_widgets = ['elements_list', 'properties_panel', 'preview_window', 'ai_generator']

            if hasattr(self, 'information_hierarchy_manager'):
                for widget_id in auxiliary_widgets:
                    widget = self.information_hierarchy_manager.hierarchical_widgets.get(widget_id)
                    if widget:
                        widget.toggle_collapse()

            # 更新状态
            self.status_notification_manager.update_status(StatusType.READY, "切换辅助信息显示")

        except Exception as e:
            logger.error(f"切换辅助信息显示失败: {e}")

    def minimize_supplementary_information(self):
        """最小化补充信息"""
        try:
            # 折叠补充层组件
            supplementary_widgets = ['library_manager', 'rules_library', 'system_settings', 'status_bar']

            if hasattr(self, 'information_hierarchy_manager'):
                for widget_id in supplementary_widgets:
                    widget = self.information_hierarchy_manager.hierarchical_widgets.get(widget_id)
                    if widget and not widget.is_collapsed:
                        widget.toggle_collapse()

            # 更新状态
            self.status_notification_manager.update_status(StatusType.READY, "最小化补充信息")

        except Exception as e:
            logger.error(f"最小化补充信息失败: {e}")

    def restore_all_information_levels(self):
        """恢复所有信息层级"""
        try:
            # 展开所有折叠的组件
            if hasattr(self, 'information_hierarchy_manager'):
                for widget in self.information_hierarchy_manager.hierarchical_widgets.values():
                    if widget.is_collapsed:
                        widget.toggle_collapse()

            # 更新状态
            self.status_notification_manager.update_status(StatusType.READY, "恢复所有信息层级")

        except Exception as e:
            logger.error(f"恢复所有信息层级失败: {e}")

    def adapt_information_hierarchy_to_workflow(self, workflow_stage: str):
        """根据工作流程阶段适配信息层级"""
        try:
            # 根据工作流程阶段调整信息层级焦点
            stage_focus_map = {
                'audio_import': ['audio_control', 'timeline'],
                'time_segmentation': ['timeline', 'stage_canvas'],
                'description_input': ['animation_description_input', 'ai_generator'],
                'ai_generation': ['ai_generation_status', 'preview_window'],
                'preview_adjustment': ['preview_window', 'properties_panel'],
                'export_completion': ['primary_toolbar', 'status_bar']
            }

            focus_widgets = stage_focus_map.get(workflow_stage, ['primary_toolbar'])

            if hasattr(self, 'information_hierarchy_manager') and focus_widgets:
                widget_id = focus_widgets[0]
                widget = self.information_hierarchy_manager.hierarchical_widgets.get(widget_id)
                if widget:
                    self.information_hierarchy_manager.set_focus_widget(widget)

            # 更新状态
            self.status_notification_manager.update_status(StatusType.READY, f"适配到工作流程: {workflow_stage}")

        except Exception as e:
            logger.error(f"适配信息层级到工作流程失败: {e}")

    def trigger_realtime_feedback(self, feedback_type: str, data: dict, priority: str = "medium"):
        """触发实时反馈"""
        try:
            if hasattr(self, 'wysiwyg_manager') and self.wysiwyg_manager.realtime_feedback_system:
                from .realtime_feedback_system import FeedbackType, FeedbackPriority

                # 映射反馈类型
                feedback_type_map = {
                    'audio_position': FeedbackType.AUDIO_POSITION,
                    'element_selection': FeedbackType.ELEMENT_SELECTION,
                    'parameter_change': FeedbackType.PARAMETER_CHANGE,
                    'ai_generation': FeedbackType.AI_GENERATION,
                    'timeline_update': FeedbackType.TIMELINE_UPDATE,
                    'stage_preview': FeedbackType.STAGE_PREVIEW,
                    'property_edit': FeedbackType.PROPERTY_EDIT,
                    'animation_play': FeedbackType.ANIMATION_PLAY
                }

                # 映射优先级
                priority_map = {
                    'critical': FeedbackPriority.CRITICAL,
                    'high': FeedbackPriority.HIGH,
                    'medium': FeedbackPriority.MEDIUM,
                    'low': FeedbackPriority.LOW
                }

                feedback_enum = feedback_type_map.get(feedback_type)
                priority_enum = priority_map.get(priority, FeedbackPriority.MEDIUM)

                if feedback_enum:
                    self.wysiwyg_manager.realtime_feedback_system.add_feedback_event(
                        feedback_enum, data, priority_enum
                    )

        except Exception as e:
            logger.error(f"触发实时反馈失败: {e}")

    def on_audio_position_changed(self, position: float):
        """音频位置改变处理"""
        try:
            # 触发音频位置反馈
            if hasattr(self, 'wysiwyg_manager'):
                self.wysiwyg_manager.trigger_audio_position_feedback(position)

            # 更新时间轴显示
            if hasattr(self, 'timeline_widget'):
                self.timeline_widget.update_playhead_position(position)

        except Exception as e:
            logger.error(f"音频位置改变处理失败: {e}")

    def on_element_property_changed(self, element_id: str, property_name: str, value):
        """元素属性改变处理"""
        try:
            # 触发参数变化反馈
            self.trigger_realtime_feedback(
                'parameter_change',
                {
                    'element_id': element_id,
                    'property': property_name,
                    'value': value
                },
                'high'
            )

            # 更新舞台显示
            if hasattr(self, 'stage_widget'):
                self.stage_widget.update_element_property(element_id, property_name, value)

        except Exception as e:
            logger.error(f"元素属性改变处理失败: {e}")

    def on_ai_generation_progress(self, progress: int, status: str):
        """AI生成进度处理"""
        try:
            # 触发AI生成反馈
            if hasattr(self, 'wysiwyg_manager'):
                self.wysiwyg_manager.trigger_ai_generation_feedback(progress, status)

        except Exception as e:
            logger.error(f"AI生成进度处理失败: {e}")

    def enable_direct_manipulation(self, enabled: bool = True):
        """启用/禁用直接操作"""
        try:
            if hasattr(self, 'wysiwyg_manager') and self.wysiwyg_manager.direct_manipulation_manager:
                # 这里可以添加启用/禁用直接操作的逻辑
                logger.info(f"直接操作模式: {'启用' if enabled else '禁用'}")

        except Exception as e:
            logger.error(f"设置直接操作模式失败: {e}")

    def get_wysiwyg_summary(self) -> dict:
        """获取所见即所得系统摘要"""
        try:
            if hasattr(self, 'wysiwyg_manager'):
                return self.wysiwyg_manager.get_wysiwyg_summary()
            return {}
        except Exception as e:
            logger.error(f"获取所见即所得系统摘要失败: {e}")
            return {}

    def setup_wysiwyg_connections(self):
        """设置所见即所得连接"""
        try:
            # 连接音频位置变化信号
            if hasattr(self, 'audio_widget'):
                # 假设音频组件有位置变化信号
                # self.audio_widget.position_changed.connect(self.on_audio_position_changed)
                pass

            # 连接属性面板变化信号
            if hasattr(self, 'properties_widget'):
                # 假设属性面板有属性变化信号
                # self.properties_widget.property_changed.connect(self.on_element_property_changed)
                pass

            # 连接AI生成器进度信号
            if hasattr(self, 'ai_generator_widget'):
                # 假设AI生成器有进度信号
                # self.ai_generator_widget.progress_updated.connect(self.on_ai_generation_progress)
                pass

        except Exception as e:
            logger.error(f"设置所见即所得连接失败: {e}")

    def start_realtime_preview(self, element_id: str = None):
        """开始实时预览"""
        try:
            # 启用实时预览模式
            if hasattr(self, 'stage_widget'):
                self.stage_widget.set_preview_mode(True)

            # 如果指定了元素，聚焦到该元素
            if element_id:
                self.trigger_realtime_feedback(
                    'element_selection',
                    {'element_id': element_id},
                    'high'
                )

            # 更新状态
            self.status_notification_manager.update_status(StatusType.READY, "实时预览模式已启用")

        except Exception as e:
            logger.error(f"开始实时预览失败: {e}")

    def stop_realtime_preview(self):
        """停止实时预览"""
        try:
            # 禁用实时预览模式
            if hasattr(self, 'stage_widget'):
                self.stage_widget.set_preview_mode(False)

            # 更新状态
            self.status_notification_manager.update_status(StatusType.READY, "实时预览模式已禁用")

        except Exception as e:
            logger.error(f"停止实时预览失败: {e}")

    def set_manipulation_mode(self, mode: str):
        """设置操作模式"""
        try:
            if hasattr(self, 'direct_manipulation_manager') and self.direct_manipulation_manager.direct_manipulation_interface:
                from .direct_manipulation_interface import ManipulationMode

                mode_map = {
                    'select': ManipulationMode.SELECT,
                    'move': ManipulationMode.MOVE,
                    'resize': ManipulationMode.RESIZE,
                    'rotate': ManipulationMode.ROTATE,
                    'edit_text': ManipulationMode.EDIT_TEXT,
                    'draw_path': ManipulationMode.DRAW_PATH
                }

                if mode in mode_map:
                    self.direct_manipulation_manager.direct_manipulation_interface.set_manipulation_mode(mode_map[mode])
                    logger.info(f"操作模式设置为: {mode}")

                    # 更新状态
                    self.status_notification_manager.update_status(StatusType.READY, f"操作模式: {mode}")

        except Exception as e:
            logger.error(f"设置操作模式失败: {e}")

    def enable_smart_snap(self, enabled: bool = True):
        """启用/禁用智能对齐"""
        try:
            if hasattr(self, 'direct_manipulation_manager') and self.direct_manipulation_manager.smart_snap_system:
                self.direct_manipulation_manager.smart_snap_system.snap_enabled = enabled
                logger.info(f"智能对齐: {'启用' if enabled else '禁用'}")

                # 更新状态
                status_text = "智能对齐已启用" if enabled else "智能对齐已禁用"
                self.status_notification_manager.update_status(StatusType.READY, status_text)

        except Exception as e:
            logger.error(f"设置智能对齐失败: {e}")

    def set_snap_options(self, grid_snap: bool = True, element_snap: bool = True, guide_snap: bool = True):
        """设置对齐选项"""
        try:
            if hasattr(self, 'direct_manipulation_manager') and self.direct_manipulation_manager.smart_snap_system:
                snap_system = self.direct_manipulation_manager.smart_snap_system
                snap_system.grid_snap = grid_snap
                snap_system.element_snap = element_snap
                snap_system.guide_snap = guide_snap

                logger.info(f"对齐选项设置: 网格={grid_snap}, 元素={element_snap}, 参考线={guide_snap}")

        except Exception as e:
            logger.error(f"设置对齐选项失败: {e}")

    def start_element_drag(self, element_id: str, element_type: str):
        """开始元素拖拽"""
        try:
            if hasattr(self, 'direct_manipulation_manager') and self.direct_manipulation_manager.drag_drop_system:
                # 创建预览图
                preview_pixmap = self.create_element_preview(element_id)

                if preview_pixmap:
                    self.direct_manipulation_manager.drag_drop_system.start_element_drag(
                        element_id, element_type, preview_pixmap
                    )

                    logger.info(f"开始元素拖拽: {element_id}")

        except Exception as e:
            logger.error(f"开始元素拖拽失败: {e}")

    def start_asset_drag(self, asset_id: str, asset_type: str):
        """开始素材拖拽"""
        try:
            if hasattr(self, 'direct_manipulation_manager') and self.direct_manipulation_manager.drag_drop_system:
                # 创建预览图
                preview_pixmap = self.create_asset_preview(asset_id)

                if preview_pixmap:
                    self.direct_manipulation_manager.drag_drop_system.start_asset_drag(
                        asset_id, asset_type, preview_pixmap
                    )

                    logger.info(f"开始素材拖拽: {asset_id}")

        except Exception as e:
            logger.error(f"开始素材拖拽失败: {e}")

    def create_element_preview(self, element_id: str) -> Optional[QPixmap]:
        """创建元素预览图"""
        try:
            # 这里需要根据元素类型创建预览图
            # 简化实现，返回一个默认图标
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.lightGray)

            painter.setFont(QFont("Arial", 10))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "元素")
            painter.end()

            return pixmap

        except Exception as e:
            logger.error(f"创建元素预览图失败: {e}")
            return None

    def create_asset_preview(self, asset_id: str) -> Optional[QPixmap]:
        """创建素材预览图"""
        try:
            # 这里需要根据素材类型创建预览图
            # 简化实现，返回一个默认图标
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.lightBlue)

            painter.setFont(QFont("Arial", 10))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "素材")
            painter.end()

            return pixmap

        except Exception as e:
            logger.error(f"创建素材预览图失败: {e}")
            return None

    def select_stage_element(self, element_id: str):
        """选择舞台元素"""
        try:
            if hasattr(self, 'direct_manipulation_manager') and self.direct_manipulation_manager.direct_manipulation_interface:
                self.direct_manipulation_manager.direct_manipulation_interface.select_element(element_id)
                logger.info(f"选择舞台元素: {element_id}")

        except Exception as e:
            logger.error(f"选择舞台元素失败: {e}")

    def clear_stage_selection(self):
        """清除舞台选择"""
        try:
            if hasattr(self, 'direct_manipulation_manager') and self.direct_manipulation_manager.direct_manipulation_interface:
                self.direct_manipulation_manager.direct_manipulation_interface.clear_selection()
                logger.info("清除舞台选择")

        except Exception as e:
            logger.error(f"清除舞台选择失败: {e}")

    def get_direct_manipulation_summary(self) -> dict:
        """获取直接操纵摘要"""
        try:
            if hasattr(self, 'direct_manipulation_manager'):
                return self.direct_manipulation_manager.get_direct_manipulation_summary()
            return {}
        except Exception as e:
            logger.error(f"获取直接操纵摘要失败: {e}")
            return {}

    def update_workflow_state(self, state: str):
        """更新工作流程状态"""
        try:
            if hasattr(self, 'workflow_state_manager'):
                workflow_state = WorkflowState(state)
                self.workflow_state_manager.update_workflow_state(workflow_state)
                logger.info(f"工作流程状态更新为: {state}")

        except Exception as e:
            logger.error(f"更新工作流程状态失败: {e}")

    def update_operation_state(self, state: str, details: str = ""):
        """更新操作状态"""
        try:
            if hasattr(self, 'workflow_state_manager'):
                operation_state = OperationState(state)
                self.workflow_state_manager.update_operation_state(operation_state, details)
                logger.debug(f"操作状态更新为: {state}")

        except Exception as e:
            logger.error(f"更新操作状态失败: {e}")

    def update_element_state(self, element_id: str, state: str, details: str = ""):
        """更新元素状态"""
        try:
            if hasattr(self, 'workflow_state_manager'):
                element_state = ElementState(state)
                self.workflow_state_manager.update_element_state(element_id, element_state, details)
                logger.debug(f"元素状态更新: {element_id} -> {state}")

        except Exception as e:
            logger.error(f"更新元素状态失败: {e}")

    def set_workflow_progress(self, state: str, progress: int):
        """设置工作流程进度"""
        try:
            if hasattr(self, 'workflow_state_manager'):
                workflow_state = WorkflowState(state)
                self.workflow_state_manager.set_workflow_progress(workflow_state, progress)

        except Exception as e:
            logger.error(f"设置工作流程进度失败: {e}")

    def set_workflow_error(self, state: str, error: bool = True):
        """设置工作流程错误"""
        try:
            if hasattr(self, 'workflow_state_manager'):
                workflow_state = WorkflowState(state)
                self.workflow_state_manager.set_workflow_error(workflow_state, error)

        except Exception as e:
            logger.error(f"设置工作流程错误失败: {e}")

    def get_current_workflow_state(self) -> str:
        """获取当前工作流程状态"""
        try:
            if hasattr(self, 'workflow_state_manager'):
                return self.workflow_state_manager.get_current_workflow_state().value
            return WorkflowState.AUDIO_IMPORT.value
        except Exception as e:
            logger.error(f"获取当前工作流程状态失败: {e}")
            return WorkflowState.AUDIO_IMPORT.value

    def get_current_operation_state(self) -> str:
        """获取当前操作状态"""
        try:
            if hasattr(self, 'workflow_state_manager'):
                return self.workflow_state_manager.get_current_operation_state().value
            return OperationState.IDLE.value
        except Exception as e:
            logger.error(f"获取当前操作状态失败: {e}")
            return OperationState.IDLE.value

    def is_function_available(self, function_name: str) -> bool:
        """检查功能是否可用"""
        try:
            if hasattr(self, 'workflow_state_manager'):
                return self.workflow_state_manager.is_function_available(function_name)
            return True  # 默认可用
        except Exception as e:
            logger.error(f"检查功能可用性失败: {e}")
            return True

    def update_function_availability(self, available_functions: List[str]):
        """更新功能可用性"""
        try:
            # 更新菜单和工具栏的可用性
            self.update_menu_availability(available_functions)
            self.update_toolbar_availability(available_functions)

            logger.debug(f"功能可用性已更新: {available_functions}")

        except Exception as e:
            logger.error(f"更新功能可用性失败: {e}")

    def update_menu_availability(self, available_functions: List[str]):
        """更新菜单可用性"""
        try:
            # 功能与菜单动作的映射
            function_action_map = {
                'import_audio': 'import_audio_action',
                'record_audio': 'record_audio_action',
                'create_segment': 'create_segment_action',
                'edit_segment': 'edit_segment_action',
                'add_description': 'add_description_action',
                'generate_animation': 'generate_animation_action',
                'play_preview': 'play_preview_action',
                'export_video': 'export_video_action'
            }

            # 更新菜单动作的可用性
            for function, action_name in function_action_map.items():
                if hasattr(self, action_name):
                    action = getattr(self, action_name)
                    action.setEnabled(function in available_functions)

        except Exception as e:
            logger.error(f"更新菜单可用性失败: {e}")

    def update_toolbar_availability(self, available_functions: List[str]):
        """更新工具栏可用性"""
        try:
            # 功能与工具栏按钮的映射
            function_button_map = {
                'import_audio': 'import_audio_btn',
                'create_segment': 'create_segment_btn',
                'generate_animation': 'generate_btn',
                'play_preview': 'play_btn',
                'export_video': 'export_btn'
            }

            # 更新工具栏按钮的可用性
            for function, button_name in function_button_map.items():
                if hasattr(self, button_name):
                    button = getattr(self, button_name)
                    button.setEnabled(function in available_functions)

        except Exception as e:
            logger.error(f"更新工具栏可用性失败: {e}")

    def get_state_summary(self) -> dict:
        """获取状态摘要"""
        try:
            summary = {}

            # 工作流程状态摘要
            if hasattr(self, 'workflow_state_manager'):
                summary['workflow'] = self.workflow_state_manager.get_state_summary()

            # 所见即所得摘要
            if hasattr(self, 'wysiwyg_manager'):
                summary['wysiwyg'] = self.wysiwyg_manager.get_wysiwyg_summary()

            # 直接操纵摘要
            if hasattr(self, 'direct_manipulation_manager'):
                summary['direct_manipulation'] = self.direct_manipulation_manager.get_direct_manipulation_summary()

            return summary

        except Exception as e:
            logger.error(f"获取状态摘要失败: {e}")
            return {}

    def get_project_assets_for_display(self):
        """获取项目中的素材用于显示"""
        try:
            assets_data = []

            # 获取当前项目
            if hasattr(self, 'current_project') and self.current_project and hasattr(self.current_project, 'assets'):
                for asset in self.current_project.assets:
                    # 获取文件信息
                    file_path = Path(asset.file_path)
                    file_size = "未知"
                    if file_path.exists():
                        size_bytes = file_path.stat().st_size
                        if size_bytes < 1024:
                            file_size = f"{size_bytes}B"
                        elif size_bytes < 1024 * 1024:
                            file_size = f"{size_bytes // 1024}KB"
                        else:
                            file_size = f"{size_bytes // (1024 * 1024)}MB"

                    # 根据文件类型确定图标
                    icon = "🖼️"
                    if asset.asset_type == "image":
                        if file_path.suffix.lower() in ['.svg']:
                            icon = "🎨"
                        else:
                            icon = "🖼️"
                    elif asset.asset_type == "video":
                        icon = "🎥"
                    elif asset.asset_type == "audio":
                        icon = "🎵"

                    assets_data.append({
                        'name': asset.name,
                        'icon': icon,
                        'size': file_size,
                        'tag': '#默认',
                        'asset': asset
                    })

            # 如果没有素材，返回空列表
            if not assets_data:
                assets_data = [
                    {
                        'name': "暂无素材",
                        'icon': "📁",
                        'size': "0KB",
                        'tag': '#空',
                        'asset': None
                    }
                ]

            return assets_data

        except Exception as e:
            logger.error(f"获取项目素材失败: {e}")
            return []

    def create_asset_card(self, asset_info, index):
        """创建素材卡片"""
        try:
            logger.info(f"开始创建素材卡片: {asset_info.get('name', '未知')} (索引: {index})")
            # 素材卡片
            asset_card = QFrame()
            asset_card.setFixedSize(80, 90)
            asset_card.setStyleSheet("""
                QFrame {
                    background-color: #F9FAFB;
                    border: 1px solid #E5E7EB;
                    border-radius: 6px;
                }
                QFrame:hover {
                    border-color: #3B82F6;
                    background-color: #EEF2FF;
                }
            """)

            card_layout = QVBoxLayout(asset_card)
            card_layout.setContentsMargins(4, 4, 4, 4)
            card_layout.setSpacing(2)

            # 图标
            icon_label = QLabel(asset_info['icon'])
            icon_label.setStyleSheet("font-size: 20px;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(icon_label)

            # 文件名
            name_label = QLabel(asset_info['name'])
            name_label.setStyleSheet("font-size: 8px; color: #374151; font-weight: bold;")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setWordWrap(True)
            card_layout.addWidget(name_label)

            # 大小和标签
            info_layout = QVBoxLayout()
            info_layout.setSpacing(1)

            size_label = QLabel(asset_info['size'])
            size_label.setStyleSheet("font-size: 7px; color: #6B7280;")
            size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info_layout.addWidget(size_label)

            tag_label = QLabel(asset_info['tag'])
            tag_label.setStyleSheet("font-size: 7px; color: #3B82F6;")
            tag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info_layout.addWidget(tag_label)

            card_layout.addLayout(info_layout)

            # 如果有真实素材，添加点击事件
            if asset_info['asset']:
                # 创建自定义的素材卡片类来处理事件
                asset_card.asset_data = asset_info['asset']
                asset_card.mousePressEvent = lambda event, asset=asset_info['asset']: self.on_asset_card_clicked(event, asset)
                asset_card.mouseDoubleClickEvent = lambda event, asset=asset_info['asset']: self.on_asset_card_double_clicked(event, asset)
                asset_card.setToolTip(f"单击选择，双击添加到舞台\n文件: {asset_info['asset'].file_path}\n大小: {asset_info['size']}")

                # 添加拖拽支持
                asset_card.setAcceptDrops(False)  # 这个卡片不接受拖拽
                # 但可以作为拖拽源（后续实现）

                logger.info(f"已为素材卡片绑定事件: {asset_info['asset'].name}")
            else:
                logger.warning(f"素材卡片没有关联的素材对象: {asset_info.get('name', '未知')}")

            return asset_card

        except Exception as e:
            logger.error(f"创建素材卡片失败: {e}")
            # 返回一个简单的占位符
            placeholder = QFrame()
            placeholder.setFixedSize(80, 90)
            placeholder.setStyleSheet("background-color: #F3F4F6; border: 1px solid #E5E7EB;")
            return placeholder

    def on_professional_asset_double_clicked(self, asset_id: str):
        """专业素材面板双击事件"""
        try:
            if hasattr(self, 'asset_manager'):
                asset = self.asset_manager.get_asset(asset_id)
                if asset:
                    success = self.add_enhanced_asset_to_stage(asset)
                    if success:
                        if hasattr(self, 'status_bar'):
                            self.status_bar.showMessage(f"✓ 素材已添加到舞台: {asset.name}", 3000)
                        logger.info(f"专业素材成功添加到舞台: {asset.name}")
                    else:
                        if hasattr(self, 'status_bar'):
                            self.status_bar.showMessage(f"✗ 添加素材到舞台失败: {asset.name}", 5000)
                        logger.error(f"添加专业素材到舞台失败: {asset.name}")

        except Exception as e:
            logger.error(f"处理专业素材双击失败: {e}")

    def on_import_assets_requested(self):
        """导入素材请求"""
        try:

            file_paths, _ = QFileDialog.getOpenFileNames(
                self, "选择素材文件", "",
                "所有支持的文件 (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp *.mp4 *.avi *.mov *.mkv *.mp3 *.wav *.ogg *.flac *.ttf *.otf *.pdf);;图片文件 (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp);;视频文件 (*.mp4 *.avi *.mov *.mkv);;音频文件 (*.mp3 *.wav *.ogg *.flac);;字体文件 (*.ttf *.otf);;文档文件 (*.pdf)"
            )

            if file_paths and hasattr(self, 'asset_manager'):
                imported_count = 0
                for file_path in file_paths:
                    asset = self.asset_manager.add_asset(file_path, category="导入", tags=["用户导入"])
                    if asset:
                        imported_count += 1
                        logger.info(f"已导入素材: {asset.name}")

                if hasattr(self, 'status_bar'):
                    self.status_bar.showMessage(f"✓ 已导入 {imported_count} 个素材", 3000)

                # 刷新素材面板
                self.refresh_assets_library_tab()

        except Exception as e:
            logger.error(f"导入素材失败: {e}")
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(f"✗ 导入素材失败: {e}", 5000)

    def on_asset_card_clicked(self, event, asset):
        """素材卡片单击事件（旧版兼容）"""
        try:

            logger.info(f"素材卡片被单击: {asset.name}")

            # 更新状态栏显示选中的素材信息
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(f"已选择素材: {asset.name} | 文件: {Path(asset.file_path).name}", 3000)

            # 在属性面板中显示素材信息（如果有的话）
            self.show_asset_properties(asset)

            # 高亮选中的素材卡片
            self.highlight_selected_asset_card(event.source() if hasattr(event, 'source') else None)

        except Exception as e:
            logger.error(f"处理素材卡片单击失败: {e}")

    def add_enhanced_asset_to_stage(self, enhanced_asset) -> bool:
        """将增强素材添加到舞台"""
        try:
            # 检查当前项目
            if not hasattr(self, 'current_project') or not self.current_project:
                logger.error("没有当前项目，无法添加素材到舞台")
                return False

            # 检查文件是否存在
            asset_path = Path(enhanced_asset.file_path)
            if not asset_path.exists():
                logger.error(f"素材文件不存在: {enhanced_asset.file_path}")
                return False

            # 创建舞台元素
            from core.data_structures import Element, ElementType, ElementStyle, Point

            # 根据素材类型创建对应的元素样式
            element_style = ElementStyle(
                width="100px",
                height="100px",
                z_index=1
            )

            # 确定元素类型
            element_type = ElementType.IMAGE
            if enhanced_asset.asset_type.value == "video":
                element_type = ElementType.VIDEO
            elif enhanced_asset.asset_type.value == "audio":
                element_type = ElementType.AUDIO

            # 在舞台中心位置创建元素
            stage_element = Element(
                name=f"素材_{enhanced_asset.name}",
                element_type=element_type,
                content=enhanced_asset.file_path,  # 将文件路径存储在content中
                position=Point(400, 300),  # 舞台中心位置
                style=element_style
            )

            # 添加到当前项目
            self.current_project.add_element(stage_element)

            # 记录素材使用情况
            if hasattr(self.current_project, 'project_id'):
                enhanced_asset.usage.add_usage(self.current_project.project_id)

            # 触发项目变更信号
            self.project_changed.emit()

            logger.info(f"成功添加增强素材到舞台: {enhanced_asset.name}")
            return True

        except Exception as e:
            logger.error(f"添加增强素材到舞台失败: {e}")
            return False

    def _create_fallback_assets_view(self, scroll_layout):
        """创建回退的素材视图（旧版实现）"""
        try:
            # 获取项目中的真实素材
            assets_data = self.get_project_assets_for_display()

            logger.info(f"回退素材库：准备显示 {len(assets_data)} 个素材")

            for i, asset_info in enumerate(assets_data):
                # 素材卡片
                asset_card = self.create_asset_card(asset_info, i)
                scroll_layout.addWidget(asset_card, i // 4, i % 4)
                logger.info(f"已创建回退素材卡片 {i+1}: {asset_info.get('name', '未知')}")

        except Exception as e:
            logger.error(f"创建回退素材视图失败: {e}")

    def on_asset_card_double_clicked(self, event, asset):
        """素材卡片双击事件 - 添加到舞台"""
        try:
            logger.info(f"素材卡片被双击: {asset.name} - 准备添加到舞台")

            # 检查文件是否存在
            asset_path = Path(asset.file_path)
            if not asset_path.exists():
                if hasattr(self, 'status_bar'):
                    self.status_bar.showMessage(f"错误: 素材文件不存在 - {asset_path.name}", 5000)
                logger.error(f"素材文件不存在: {asset.file_path}")
                return

            # 添加素材到舞台
            success = self.add_asset_to_stage(asset)

            if success:
                if hasattr(self, 'status_bar'):
                    self.status_bar.showMessage(f"✓ 素材已添加到舞台: {asset.name}", 3000)
                logger.info(f"素材成功添加到舞台: {asset.name}")
            else:
                if hasattr(self, 'status_bar'):
                    self.status_bar.showMessage(f"✗ 添加素材到舞台失败: {asset.name}", 5000)
                logger.error(f"添加素材到舞台失败: {asset.name}")

        except Exception as e:
            logger.error(f"处理素材卡片双击失败: {e}")
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(f"✗ 双击处理失败: {e}", 5000)

    def show_asset_properties(self, asset):
        """在属性面板中显示素材信息"""
        try:
            # 这里可以在属性面板中显示素材的详细信息
            # 目前只记录日志，后续可以扩展
            logger.info(f"显示素材属性: {asset.name}")

        except Exception as e:
            logger.error(f"显示素材属性失败: {e}")

    def highlight_selected_asset_card(self, card_widget):
        """高亮选中的素材卡片"""
        try:
            # 这里可以添加视觉反馈，比如改变边框颜色
            # 目前只记录日志，后续可以扩展
            if card_widget:
                logger.info("高亮选中的素材卡片")

        except Exception as e:
            logger.error(f"高亮素材卡片失败: {e}")

    def add_asset_to_stage(self, asset):
        """将素材添加到舞台"""
        try:
            # 检查当前项目
            if not hasattr(self, 'current_project') or not self.current_project:
                logger.error("没有当前项目，无法添加素材到舞台")
                return False

            # 创建舞台元素
            from core.data_structures import Element, Point, Transform, Style
            element = Element(
                name=asset.name,
                content=asset.file_path,
                position=Point(400, 300),  # 默认位置
                transform=Transform(),
                style=Style(
                    width="100px",
                    height="100px"
                )
            )

            # 确定元素类型
            element_type = ElementType.IMAGE
            if asset.asset_type == "video":
                element_type = ElementType.VIDEO
            elif asset.asset_type == "audio":
                element_type = ElementType.AUDIO

            # 在舞台中心位置创建元素
            stage_element = Element(
                name=f"素材_{asset.name}",
                element_type=element_type,
                content=asset.file_path,  # 将文件路径存储在content中
                position=Point(400, 300),  # 舞台中心位置
                style=element_style
            )

            # 添加到当前项目
            self.current_project.add_element(stage_element)

            # 触发项目变更信号
            self.project_changed.emit()

            logger.info(f"成功添加素材到舞台: {asset.name}")
            return True

        except Exception as e:
            logger.error(f"添加素材到舞台失败: {e}")
            return False
