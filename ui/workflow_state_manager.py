"""
AI Animation Studio - 工作流程状态管理系统
实现清晰的状态指示设计和工作流程状态管理
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGroupBox, QPushButton, QProgressBar,
                             QScrollArea, QSplitter, QStackedWidget, QSlider,
                             QSpinBox, QDoubleSpinBox, QColorDialog, QMenu,
                             QLineEdit, QTextEdit, QComboBox, QCheckBox,
                             QToolButton, QButtonGroup, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint, QPointF, QRectF, QParallelAnimationGroup
from PyQt6.QtGui import (QFont, QColor, QPalette, QPixmap, QPainter, QPen, QBrush,
                         QCursor, QMouseEvent, QWheelEvent, QKeyEvent, QAction, QLinearGradient)

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import json
import time

from core.logger import get_logger

logger = get_logger("workflow_state_manager")


class WorkflowState(Enum):
    """工作流程状态枚举"""
    AUDIO_IMPORT = "audio_import"               # 音频导入
    TIME_SEGMENT = "time_segment"               # 时间段标记
    ANIMATION_DESCRIPTION = "animation_description"  # 动画描述
    AI_GENERATION = "ai_generation"             # AI生成
    PREVIEW_ADJUST = "preview_adjust"           # 预览调整
    EXPORT_RENDER = "export_render"             # 导出渲染


class OperationState(Enum):
    """操作状态枚举"""
    IDLE = "idle"                   # 空闲
    SELECTING = "selecting"         # 选择中
    EDITING = "editing"             # 编辑中
    DRAGGING = "dragging"           # 拖拽中
    RESIZING = "resizing"           # 缩放中
    ROTATING = "rotating"           # 旋转中
    ANIMATING = "animating"         # 动画中
    PROCESSING = "processing"       # 处理中
    SAVING = "saving"               # 保存中
    LOADING = "loading"             # 加载中


class ElementState(Enum):
    """元素状态枚举"""
    PENDING = "pending"             # 待处理
    PROCESSING = "processing"       # 处理中
    COMPLETED = "completed"         # 已完成
    ERROR = "error"                 # 错误
    MODIFIED = "modified"           # 已修改


class StateIndicator(QWidget):
    """状态指示器组件"""
    
    state_clicked = pyqtSignal(str)  # 状态点击信号
    
    def __init__(self, state_id: str, title: str, description: str = ""):
        super().__init__()
        self.state_id = state_id
        self.title = title
        self.description = description
        self.is_active = False
        self.is_completed = False
        self.is_error = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setFixedSize(200, 60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)
        
        # 标题标签
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        layout.addWidget(self.title_label)
        
        # 描述标签
        if self.description:
            self.desc_label = QLabel(self.description)
            self.desc_label.setFont(QFont("Microsoft YaHei", 8))
            self.desc_label.setStyleSheet("color: #666666;")
            layout.addWidget(self.desc_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.update_style()
    
    def update_style(self):
        """更新样式"""
        if self.is_error:
            # 错误状态
            self.setStyleSheet("""
                StateIndicator {
                    background-color: #FFEBEE;
                    border: 2px solid #F44336;
                    border-radius: 8px;
                }
                StateIndicator:hover {
                    background-color: #FFCDD2;
                }
            """)
            self.title_label.setStyleSheet("color: #D32F2F;")
            
        elif self.is_completed:
            # 完成状态
            self.setStyleSheet("""
                StateIndicator {
                    background-color: #E8F5E8;
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                }
                StateIndicator:hover {
                    background-color: #C8E6C9;
                }
            """)
            self.title_label.setStyleSheet("color: #388E3C;")
            
        elif self.is_active:
            # 激活状态
            self.setStyleSheet("""
                StateIndicator {
                    background-color: #E3F2FD;
                    border: 2px solid #2196F3;
                    border-radius: 8px;
                }
                StateIndicator:hover {
                    background-color: #BBDEFB;
                }
            """)
            self.title_label.setStyleSheet("color: #1976D2;")
            
        else:
            # 默认状态
            self.setStyleSheet("""
                StateIndicator {
                    background-color: #F5F5F5;
                    border: 2px solid #E0E0E0;
                    border-radius: 8px;
                }
                StateIndicator:hover {
                    background-color: #EEEEEE;
                }
            """)
            self.title_label.setStyleSheet("color: #757575;")
    
    def set_active(self, active: bool = True):
        """设置激活状态"""
        self.is_active = active
        if active:
            self.is_completed = False
            self.is_error = False
        self.update_style()
    
    def set_completed(self, completed: bool = True):
        """设置完成状态"""
        self.is_completed = completed
        if completed:
            self.is_active = False
            self.is_error = False
        self.update_style()
    
    def set_error(self, error: bool = True):
        """设置错误状态"""
        self.is_error = error
        if error:
            self.is_active = False
            self.is_completed = False
        self.update_style()
    
    def show_progress(self, value: int):
        """显示进度"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(value)
    
    def hide_progress(self):
        """隐藏进度"""
        self.progress_bar.setVisible(False)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.state_clicked.emit(self.state_id)


class WorkflowProgressWidget(QWidget):
    """工作流程进度组件"""
    
    state_changed = pyqtSignal(str)  # 状态改变信号
    
    def __init__(self):
        super().__init__()
        self.current_state = WorkflowState.AUDIO_IMPORT
        self.state_indicators: Dict[WorkflowState, StateIndicator] = {}
        
        self.setup_ui()
        self.setup_workflow_steps()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("工作流程进度")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2C5AA0; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # 步骤容器
        self.steps_container = QWidget()
        self.steps_layout = QVBoxLayout(self.steps_container)
        self.steps_layout.setSpacing(5)
        layout.addWidget(self.steps_container)
        
        layout.addStretch()
    
    def setup_workflow_steps(self):
        """设置工作流程步骤"""
        workflow_steps = [
            (WorkflowState.AUDIO_IMPORT, "1. 导入音频", "选择或录制音频文件"),
            (WorkflowState.TIME_SEGMENT, "2. 标记时间段", "划分音频时间段"),
            (WorkflowState.ANIMATION_DESCRIPTION, "3. 描述动画", "为每个时间段描述动画"),
            (WorkflowState.AI_GENERATION, "4. AI生成", "AI生成动画代码"),
            (WorkflowState.PREVIEW_ADJUST, "5. 预览调整", "预览并调整动画"),
            (WorkflowState.EXPORT_RENDER, "6. 导出渲染", "导出最终动画")
        ]
        
        for state, title, description in workflow_steps:
            indicator = StateIndicator(state.value, title, description)
            indicator.state_clicked.connect(self.on_state_clicked)
            self.state_indicators[state] = indicator
            self.steps_layout.addWidget(indicator)
        
        # 设置初始状态
        self.update_workflow_state(self.current_state)
    
    def update_workflow_state(self, new_state: WorkflowState):
        """更新工作流程状态"""
        old_state = self.current_state
        self.current_state = new_state
        
        # 更新指示器状态
        for state, indicator in self.state_indicators.items():
            if state == new_state:
                indicator.set_active(True)
            elif self.is_state_completed(state, new_state):
                indicator.set_completed(True)
            else:
                indicator.set_active(False)
                indicator.set_completed(False)
        
        # 发送状态改变信号
        self.state_changed.emit(new_state.value)
        
        logger.info(f"工作流程状态更新: {old_state.value} -> {new_state.value}")
    
    def is_state_completed(self, state: WorkflowState, current_state: WorkflowState) -> bool:
        """判断状态是否已完成"""
        state_order = [
            WorkflowState.AUDIO_IMPORT,
            WorkflowState.TIME_SEGMENT,
            WorkflowState.ANIMATION_DESCRIPTION,
            WorkflowState.AI_GENERATION,
            WorkflowState.PREVIEW_ADJUST,
            WorkflowState.EXPORT_RENDER
        ]
        
        try:
            state_index = state_order.index(state)
            current_index = state_order.index(current_state)
            return state_index < current_index
        except ValueError:
            return False
    
    def on_state_clicked(self, state_id: str):
        """状态点击处理"""
        try:
            state = WorkflowState(state_id)
            self.update_workflow_state(state)
        except ValueError:
            logger.warning(f"无效的状态ID: {state_id}")
    
    def set_state_progress(self, state: WorkflowState, progress: int):
        """设置状态进度"""
        if state in self.state_indicators:
            self.state_indicators[state].show_progress(progress)
    
    def set_state_error(self, state: WorkflowState, error: bool = True):
        """设置状态错误"""
        if state in self.state_indicators:
            self.state_indicators[state].set_error(error)


class OperationStatusWidget(QWidget):
    """操作状态组件"""
    
    def __init__(self):
        super().__init__()
        self.current_operation = OperationState.IDLE
        self.operation_start_time = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 操作图标
        self.operation_icon = QLabel("📍")
        self.operation_icon.setFixedSize(20, 20)
        layout.addWidget(self.operation_icon)
        
        # 操作文本
        self.operation_text = QLabel("就绪")
        self.operation_text.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self.operation_text)
        
        # 操作时间
        self.operation_time = QLabel("")
        self.operation_time.setFont(QFont("Microsoft YaHei", 8))
        self.operation_time.setStyleSheet("color: #666666;")
        layout.addWidget(self.operation_time)
        
        layout.addStretch()
        
        # 定时器更新时间显示
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time_display)
        self.timer.start(1000)  # 每秒更新
    
    def update_operation_state(self, operation: OperationState, details: str = ""):
        """更新操作状态"""
        self.current_operation = operation
        self.operation_start_time = time.time()
        
        # 状态图标和文本映射
        operation_info = {
            OperationState.IDLE: ("📍", "就绪"),
            OperationState.SELECTING: ("🎯", "选择中"),
            OperationState.EDITING: ("✏️", "编辑中"),
            OperationState.DRAGGING: ("🖱️", "拖拽中"),
            OperationState.RESIZING: ("📏", "缩放中"),
            OperationState.ROTATING: ("🔄", "旋转中"),
            OperationState.ANIMATING: ("🎬", "动画中"),
            OperationState.PROCESSING: ("⚙️", "处理中"),
            OperationState.SAVING: ("💾", "保存中"),
            OperationState.LOADING: ("📂", "加载中")
        }
        
        icon, text = operation_info.get(operation, ("❓", "未知状态"))
        
        self.operation_icon.setText(icon)
        if details:
            self.operation_text.setText(f"{text}: {details}")
        else:
            self.operation_text.setText(text)
        
        logger.debug(f"操作状态更新: {operation.value}")
    
    def update_time_display(self):
        """更新时间显示"""
        if self.operation_start_time and self.current_operation != OperationState.IDLE:
            elapsed = time.time() - self.operation_start_time
            if elapsed < 60:
                self.operation_time.setText(f"{elapsed:.0f}s")
            else:
                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)
                self.operation_time.setText(f"{minutes}m {seconds}s")
        else:
            self.operation_time.setText("")


class ElementStatusWidget(QWidget):
    """元素状态组件"""
    
    def __init__(self):
        super().__init__()
        self.element_states: Dict[str, ElementState] = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 标题
        title_label = QLabel("元素状态")
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2C5AA0;")
        layout.addWidget(title_label)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        
        self.elements_container = QWidget()
        self.elements_layout = QVBoxLayout(self.elements_container)
        self.elements_layout.setSpacing(2)
        
        scroll_area.setWidget(self.elements_container)
        layout.addWidget(scroll_area)
    
    def update_element_state(self, element_id: str, state: ElementState, details: str = ""):
        """更新元素状态"""
        self.element_states[element_id] = state
        
        # 查找或创建元素状态显示
        element_widget = self.find_element_widget(element_id)
        if not element_widget:
            element_widget = self.create_element_widget(element_id)
        
        # 更新状态显示
        self.update_element_widget(element_widget, state, details)
        
        logger.debug(f"元素状态更新: {element_id} -> {state.value}")
    
    def find_element_widget(self, element_id: str) -> Optional[QWidget]:
        """查找元素组件"""
        for i in range(self.elements_layout.count()):
            widget = self.elements_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'element_id') and widget.element_id == element_id:
                return widget
        return None
    
    def create_element_widget(self, element_id: str) -> QWidget:
        """创建元素组件"""
        widget = QWidget()
        widget.element_id = element_id
        widget.setFixedHeight(30)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # 状态图标
        widget.status_icon = QLabel("⏳")
        widget.status_icon.setFixedSize(16, 16)
        layout.addWidget(widget.status_icon)
        
        # 元素名称
        widget.name_label = QLabel(element_id)
        widget.name_label.setFont(QFont("Microsoft YaHei", 8))
        layout.addWidget(widget.name_label)
        
        # 状态文本
        widget.status_label = QLabel("待处理")
        widget.status_label.setFont(QFont("Microsoft YaHei", 8))
        widget.status_label.setStyleSheet("color: #666666;")
        layout.addWidget(widget.status_label)
        
        layout.addStretch()
        
        self.elements_layout.addWidget(widget)
        return widget
    
    def update_element_widget(self, widget: QWidget, state: ElementState, details: str):
        """更新元素组件"""
        # 状态图标和文本映射
        state_info = {
            ElementState.PENDING: ("⏳", "待处理", "#FFA726"),
            ElementState.PROCESSING: ("⚙️", "处理中", "#42A5F5"),
            ElementState.COMPLETED: ("✅", "已完成", "#66BB6A"),
            ElementState.ERROR: ("❌", "错误", "#EF5350"),
            ElementState.MODIFIED: ("📝", "已修改", "#AB47BC")
        }
        
        icon, text, color = state_info.get(state, ("❓", "未知", "#757575"))
        
        widget.status_icon.setText(icon)
        if details:
            widget.status_label.setText(f"{text}: {details}")
        else:
            widget.status_label.setText(text)
        
        widget.status_label.setStyleSheet(f"color: {color};")
    
    def remove_element(self, element_id: str):
        """移除元素"""
        widget = self.find_element_widget(element_id)
        if widget:
            self.elements_layout.removeWidget(widget)
            widget.deleteLater()
            
        if element_id in self.element_states:
            del self.element_states[element_id]


class StateTransitionAnimation(QWidget):
    """状态转换动画组件"""

    def __init__(self):
        super().__init__()
        self.animation_group = None
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        self.setFixedSize(300, 100)
        self.setStyleSheet("background-color: transparent;")

        # 动画标签
        self.animation_label = QLabel("状态转换中...")
        self.animation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.animation_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.animation_label.setStyleSheet("""
            QLabel {
                color: #2196F3;
                background-color: rgba(255, 255, 255, 200);
                border-radius: 10px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.addWidget(self.animation_label)

    def animate_state_transition(self, from_state: str, to_state: str):
        """播放状态转换动画"""
        self.animation_label.setText(f"从 {from_state} 转换到 {to_state}")

        # 创建动画组
        self.animation_group = QParallelAnimationGroup()

        # 透明度动画
        opacity_effect = QGraphicsOpacityEffect()
        self.animation_label.setGraphicsEffect(opacity_effect)

        opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
        opacity_animation.setDuration(2000)
        opacity_animation.setStartValue(0.0)
        opacity_animation.setKeyValueAt(0.5, 1.0)
        opacity_animation.setEndValue(0.0)
        opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.animation_group.addAnimation(opacity_animation)

        # 位置动画
        geometry_animation = QPropertyAnimation(self, b"geometry")
        geometry_animation.setDuration(2000)
        start_rect = QRect(100, 50, 300, 100)
        end_rect = QRect(100, 20, 300, 100)
        geometry_animation.setStartValue(start_rect)
        geometry_animation.setEndValue(end_rect)
        geometry_animation.setEasingCurve(QEasingCurve.Type.OutBounce)

        self.animation_group.addAnimation(geometry_animation)

        # 动画完成后隐藏
        self.animation_group.finished.connect(self.hide)

        # 显示并开始动画
        self.show()
        self.animation_group.start()


class WorkflowStateManager(QWidget):
    """工作流程状态管理器"""

    workflow_state_changed = pyqtSignal(str)        # 工作流程状态改变信号
    operation_state_changed = pyqtSignal(str, str)  # 操作状态改变信号
    element_state_changed = pyqtSignal(str, str)    # 元素状态改变信号

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_workflow_state = WorkflowState.AUDIO_IMPORT
        self.current_operation_state = OperationState.IDLE
        self.available_functions: Dict[WorkflowState, List[str]] = {}

        self.setup_ui()
        self.setup_available_functions()
        self.setup_connections()

        logger.info("工作流程状态管理器初始化完成")

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # 工作流程进度组件
        self.workflow_progress = WorkflowProgressWidget()
        layout.addWidget(self.workflow_progress)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # 操作状态组件
        self.operation_status = OperationStatusWidget()
        layout.addWidget(self.operation_status)

        # 元素状态组件
        self.element_status = ElementStatusWidget()
        layout.addWidget(self.element_status)

        # 状态转换动画组件
        self.transition_animation = StateTransitionAnimation()
        self.transition_animation.hide()

    def setup_available_functions(self):
        """设置可用功能"""
        self.available_functions = {
            WorkflowState.AUDIO_IMPORT: [
                "import_audio", "record_audio", "audio_settings"
            ],
            WorkflowState.TIME_SEGMENT: [
                "create_segment", "edit_segment", "delete_segment", "segment_settings"
            ],
            WorkflowState.ANIMATION_DESCRIPTION: [
                "add_description", "edit_description", "ai_suggest", "description_templates"
            ],
            WorkflowState.AI_GENERATION: [
                "generate_animation", "generation_settings", "preview_generation", "cancel_generation"
            ],
            WorkflowState.PREVIEW_ADJUST: [
                "play_preview", "edit_elements", "adjust_timing", "export_preview"
            ],
            WorkflowState.EXPORT_RENDER: [
                "export_video", "export_gif", "export_html", "render_settings"
            ]
        }

    def setup_connections(self):
        """设置信号连接"""
        self.workflow_progress.state_changed.connect(self.on_workflow_state_changed)

    def update_workflow_state(self, new_state: WorkflowState):
        """更新工作流程状态"""
        old_state = self.current_workflow_state
        self.current_workflow_state = new_state

        # 更新工作流程进度组件
        self.workflow_progress.update_workflow_state(new_state)

        # 更新可用功能
        self.update_available_functions(new_state)

        # 显示状态转换动画
        self.animate_state_transition(old_state.value, new_state.value)

        # 发送信号
        self.workflow_state_changed.emit(new_state.value)

        logger.info(f"工作流程状态更新: {old_state.value} -> {new_state.value}")

    def update_operation_state(self, new_state: OperationState, details: str = ""):
        """更新操作状态"""
        self.current_operation_state = new_state

        # 更新操作状态组件
        self.operation_status.update_operation_state(new_state, details)

        # 发送信号
        self.operation_state_changed.emit(new_state.value, details)

        logger.debug(f"操作状态更新: {new_state.value}")

    def update_element_state(self, element_id: str, state: ElementState, details: str = ""):
        """更新元素状态"""
        # 更新元素状态组件
        self.element_status.update_element_state(element_id, state, details)

        # 发送信号
        self.element_state_changed.emit(element_id, state.value)

        logger.debug(f"元素状态更新: {element_id} -> {state.value}")

    def update_available_functions(self, state: WorkflowState):
        """更新可用功能"""
        available = self.available_functions.get(state, [])

        # 通知主窗口更新功能可用性
        if hasattr(self.main_window, 'update_function_availability'):
            self.main_window.update_function_availability(available)

        logger.debug(f"可用功能更新: {available}")

    def animate_state_transition(self, from_state: str, to_state: str):
        """播放状态转换动画"""
        if self.transition_animation:
            self.transition_animation.animate_state_transition(from_state, to_state)

    def on_workflow_state_changed(self, state_id: str):
        """工作流程状态改变处理"""
        try:
            new_state = WorkflowState(state_id)
            if new_state != self.current_workflow_state:
                self.update_workflow_state(new_state)
        except ValueError:
            logger.warning(f"无效的工作流程状态: {state_id}")

    def set_workflow_progress(self, state: WorkflowState, progress: int):
        """设置工作流程进度"""
        self.workflow_progress.set_state_progress(state, progress)

    def set_workflow_error(self, state: WorkflowState, error: bool = True):
        """设置工作流程错误"""
        self.workflow_progress.set_state_error(state, error)

    def remove_element(self, element_id: str):
        """移除元素"""
        self.element_status.remove_element(element_id)

    def get_current_workflow_state(self) -> WorkflowState:
        """获取当前工作流程状态"""
        return self.current_workflow_state

    def get_current_operation_state(self) -> OperationState:
        """获取当前操作状态"""
        return self.current_operation_state

    def get_available_functions(self) -> List[str]:
        """获取当前可用功能"""
        return self.available_functions.get(self.current_workflow_state, [])

    def is_function_available(self, function_name: str) -> bool:
        """检查功能是否可用"""
        return function_name in self.get_available_functions()

    def get_state_summary(self) -> dict:
        """获取状态摘要"""
        return {
            'workflow_state': self.current_workflow_state.value,
            'operation_state': self.current_operation_state.value,
            'available_functions': self.get_available_functions(),
            'element_count': len(self.element_status.element_states)
        }
