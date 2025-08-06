"""
AI Animation Studio - 实时反馈系统
实现所见即所得原则，提供即时的视觉反馈和实时预览功能
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGroupBox, QPushButton, QProgressBar,
                             QScrollArea, QSplitter, QStackedWidget, QSlider,
                             QSpinBox, QDoubleSpinBox, QColorDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QThread, QObject
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QPainter

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Callable
import json
import time

from core.logger import get_logger

logger = get_logger("realtime_feedback_system")


class FeedbackType(Enum):
    """反馈类型枚举"""
    AUDIO_POSITION = "audio_position"           # 音频位置反馈
    ELEMENT_SELECTION = "element_selection"     # 元素选择反馈
    PARAMETER_CHANGE = "parameter_change"       # 参数变化反馈
    AI_GENERATION = "ai_generation"             # AI生成进度反馈
    TIMELINE_UPDATE = "timeline_update"         # 时间轴更新反馈
    STAGE_PREVIEW = "stage_preview"             # 舞台预览反馈
    PROPERTY_EDIT = "property_edit"             # 属性编辑反馈
    ANIMATION_PLAY = "animation_play"           # 动画播放反馈


class FeedbackPriority(Enum):
    """反馈优先级枚举"""
    CRITICAL = "critical"       # 关键反馈（立即响应）
    HIGH = "high"              # 高优先级（50ms内响应）
    MEDIUM = "medium"          # 中优先级（100ms内响应）
    LOW = "low"                # 低优先级（200ms内响应）


class RealTimeFeedbackEvent:
    """实时反馈事件"""
    
    def __init__(self, feedback_type: FeedbackType, data: Dict[str, Any], 
                 priority: FeedbackPriority = FeedbackPriority.MEDIUM,
                 callback: Optional[Callable] = None):
        self.feedback_type = feedback_type
        self.data = data
        self.priority = priority
        self.callback = callback
        self.timestamp = time.time()
        self.processed = False


class DebounceTimer(QObject):
    """防抖定时器"""
    
    triggered = pyqtSignal(object)  # 触发信号
    
    def __init__(self, delay: int = 300):
        super().__init__()
        self.delay = delay
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.on_timeout)
        self.pending_event = None
    
    def trigger(self, event: RealTimeFeedbackEvent):
        """触发防抖"""
        self.pending_event = event
        self.timer.start(self.delay)
    
    def on_timeout(self):
        """超时处理"""
        if self.pending_event:
            self.triggered.emit(self.pending_event)
            self.pending_event = None


class VisualFeedbackIndicator(QWidget):
    """视觉反馈指示器"""
    
    def __init__(self, indicator_type: str, color: QColor = QColor("#2C5AA0")):
        super().__init__()
        self.indicator_type = indicator_type
        self.color = color
        self.is_active = False
        self.animation = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setFixedSize(20, 20)
        self.setStyleSheet(f"""
            VisualFeedbackIndicator {{
                background-color: {self.color.name()};
                border-radius: 10px;
                border: 2px solid transparent;
            }}
        """)
    
    def activate(self, duration: int = 1000):
        """激活指示器"""
        self.is_active = True
        
        # 添加脉冲动画
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(duration)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # 设置动画效果
        self.setStyleSheet(f"""
            VisualFeedbackIndicator {{
                background-color: {self.color.name()};
                border-radius: 10px;
                border: 2px solid {self.color.lighter(150).name()};
                box-shadow: 0 0 10px {self.color.name()};
            }}
        """)
        
        # 定时器自动取消激活
        QTimer.singleShot(duration, self.deactivate)
    
    def deactivate(self):
        """取消激活"""
        self.is_active = False
        self.setStyleSheet(f"""
            VisualFeedbackIndicator {{
                background-color: {self.color.name()};
                border-radius: 10px;
                border: 2px solid transparent;
            }}
        """)


class RealTimePreviewWidget(QWidget):
    """实时预览组件"""
    
    preview_updated = pyqtSignal(dict)  # 预览更新信号
    
    def __init__(self):
        super().__init__()
        self.preview_data = {}
        self.is_previewing = False
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.apply_preview)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 预览标题
        title_label = QLabel("实时预览")
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2C5AA0; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # 预览内容区域
        self.preview_area = QFrame()
        self.preview_area.setFrameStyle(QFrame.Shape.Box)
        self.preview_area.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #DEE2E6;
                border-radius: 4px;
                min-height: 200px;
            }
        """)
        
        preview_layout = QVBoxLayout(self.preview_area)
        
        # 预览状态标签
        self.status_label = QLabel("等待预览...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #6C757D; font-style: italic;")
        preview_layout.addWidget(self.status_label)
        
        layout.addWidget(self.preview_area)
        
        # 预览控制按钮
        control_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("应用预览")
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.apply_btn.clicked.connect(self.apply_preview)
        control_layout.addWidget(self.apply_btn)
        
        self.cancel_btn = QPushButton("取消预览")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_preview)
        control_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(control_layout)
    
    def start_preview(self, preview_data: Dict[str, Any]):
        """开始预览"""
        self.preview_data = preview_data
        self.is_previewing = True
        
        # 更新状态
        self.status_label.setText(f"预览中: {preview_data.get('description', '未知操作')}")
        
        # 启动预览定时器（防抖）
        self.preview_timer.start(500)  # 500ms后应用预览
    
    def apply_preview(self):
        """应用预览"""
        if self.is_previewing and self.preview_data:
            self.preview_updated.emit(self.preview_data)
            self.status_label.setText("预览已应用")
            self.is_previewing = False
            
            # 2秒后恢复等待状态
            QTimer.singleShot(2000, lambda: self.status_label.setText("等待预览..."))
    
    def cancel_preview(self):
        """取消预览"""
        self.is_previewing = False
        self.preview_data = {}
        self.preview_timer.stop()
        self.status_label.setText("预览已取消")
        
        # 2秒后恢复等待状态
        QTimer.singleShot(2000, lambda: self.status_label.setText("等待预览..."))


class RealTimeFeedbackSystem(QObject):
    """实时反馈系统"""
    
    feedback_processed = pyqtSignal(RealTimeFeedbackEvent)  # 反馈处理完成信号
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.feedback_handlers: Dict[FeedbackType, Callable] = {}
        self.feedback_queue: List[RealTimeFeedbackEvent] = []
        self.visual_indicators: Dict[str, VisualFeedbackIndicator] = {}
        self.debounce_timers: Dict[str, DebounceTimer] = {}
        self.preview_widget = None
        
        # 处理定时器
        self.process_timer = QTimer()
        self.process_timer.timeout.connect(self.process_feedback_queue)
        self.process_timer.start(16)  # 60 FPS
        
        self.initialize_feedback_handlers()
        self.setup_visual_indicators()
        self.setup_preview_widget()
        
        logger.info("实时反馈系统初始化完成")
    
    def initialize_feedback_handlers(self):
        """初始化反馈处理器"""
        self.feedback_handlers = {
            FeedbackType.AUDIO_POSITION: self.handle_audio_position_feedback,
            FeedbackType.ELEMENT_SELECTION: self.handle_element_selection_feedback,
            FeedbackType.PARAMETER_CHANGE: self.handle_parameter_change_feedback,
            FeedbackType.AI_GENERATION: self.handle_ai_generation_feedback,
            FeedbackType.TIMELINE_UPDATE: self.handle_timeline_update_feedback,
            FeedbackType.STAGE_PREVIEW: self.handle_stage_preview_feedback,
            FeedbackType.PROPERTY_EDIT: self.handle_property_edit_feedback,
            FeedbackType.ANIMATION_PLAY: self.handle_animation_play_feedback
        }
    
    def setup_visual_indicators(self):
        """设置视觉指示器"""
        indicator_configs = [
            ("audio_position", QColor("#FF6B6B")),      # 红色 - 音频位置
            ("element_selection", QColor("#4ECDC4")),   # 青色 - 元素选择
            ("parameter_change", QColor("#45B7D1")),    # 蓝色 - 参数变化
            ("ai_generation", QColor("#96CEB4")),       # 绿色 - AI生成
            ("timeline_update", QColor("#FFEAA7")),     # 黄色 - 时间轴更新
            ("stage_preview", QColor("#DDA0DD")),       # 紫色 - 舞台预览
            ("property_edit", QColor("#98D8C8")),       # 薄荷绿 - 属性编辑
            ("animation_play", QColor("#F7DC6F"))       # 金色 - 动画播放
        ]
        
        for indicator_id, color in indicator_configs:
            indicator = VisualFeedbackIndicator(indicator_id, color)
            self.visual_indicators[indicator_id] = indicator
    
    def setup_preview_widget(self):
        """设置预览组件"""
        self.preview_widget = RealTimePreviewWidget()
        self.preview_widget.preview_updated.connect(self.on_preview_applied)
    
    def add_feedback_event(self, feedback_type: FeedbackType, data: Dict[str, Any],
                          priority: FeedbackPriority = FeedbackPriority.MEDIUM,
                          callback: Optional[Callable] = None):
        """添加反馈事件"""
        event = RealTimeFeedbackEvent(feedback_type, data, priority, callback)
        
        # 根据优先级插入队列
        if priority == FeedbackPriority.CRITICAL:
            self.feedback_queue.insert(0, event)
        else:
            self.feedback_queue.append(event)
        
        logger.debug(f"添加反馈事件: {feedback_type.value}, 优先级: {priority.value}")
    
    def process_feedback_queue(self):
        """处理反馈队列"""
        if not self.feedback_queue:
            return
        
        # 获取最高优先级事件
        event = self.feedback_queue.pop(0)
        
        try:
            # 检查是否需要防抖处理
            if self.should_debounce(event):
                self.apply_debounce(event)
                return
            
            # 处理反馈事件
            handler = self.feedback_handlers.get(event.feedback_type)
            if handler:
                handler(event)
                event.processed = True
                
                # 激活视觉指示器
                self.activate_visual_indicator(event.feedback_type.value)
                
                # 发送处理完成信号
                self.feedback_processed.emit(event)
                
                # 执行回调
                if event.callback:
                    event.callback(event)
                    
        except Exception as e:
            logger.error(f"处理反馈事件失败: {e}")
    
    def should_debounce(self, event: RealTimeFeedbackEvent) -> bool:
        """判断是否需要防抖处理"""
        debounce_types = [
            FeedbackType.PARAMETER_CHANGE,
            FeedbackType.PROPERTY_EDIT,
            FeedbackType.STAGE_PREVIEW
        ]
        return event.feedback_type in debounce_types
    
    def apply_debounce(self, event: RealTimeFeedbackEvent):
        """应用防抖处理"""
        debounce_key = f"{event.feedback_type.value}_{event.data.get('element_id', 'global')}"
        
        if debounce_key not in self.debounce_timers:
            self.debounce_timers[debounce_key] = DebounceTimer(300)
            self.debounce_timers[debounce_key].triggered.connect(
                lambda e: self.process_debounced_event(e)
            )
        
        self.debounce_timers[debounce_key].trigger(event)
    
    def process_debounced_event(self, event: RealTimeFeedbackEvent):
        """处理防抖事件"""
        handler = self.feedback_handlers.get(event.feedback_type)
        if handler:
            handler(event)
            self.activate_visual_indicator(event.feedback_type.value)
    
    def activate_visual_indicator(self, indicator_id: str):
        """激活视觉指示器"""
        if indicator_id in self.visual_indicators:
            self.visual_indicators[indicator_id].activate()
    
    def handle_audio_position_feedback(self, event: RealTimeFeedbackEvent):
        """处理音频位置反馈"""
        position = event.data.get('position', 0.0)
        
        try:
            # 更新时间轴位置
            if hasattr(self.main_window, 'timeline_widget'):
                self.main_window.timeline_widget.update_playhead_position(position)
            
            # 高亮当前时间段
            current_segment = self.get_current_time_segment(position)
            if current_segment:
                self.highlight_time_segment(current_segment)
            
            # 更新舞台状态
            if hasattr(self.main_window, 'stage_widget'):
                self.main_window.stage_widget.update_to_time(position)
                
        except Exception as e:
            logger.error(f"处理音频位置反馈失败: {e}")
    
    def handle_element_selection_feedback(self, event: RealTimeFeedbackEvent):
        """处理元素选择反馈"""
        element_id = event.data.get('element_id')
        
        try:
            # 高亮选中元素
            if hasattr(self.main_window, 'stage_widget') and element_id:
                self.main_window.stage_widget.highlight_element(element_id)
            
            # 更新属性面板
            if hasattr(self.main_window, 'properties_widget') and element_id:
                self.main_window.properties_widget.load_element_properties(element_id)
                
        except Exception as e:
            logger.error(f"处理元素选择反馈失败: {e}")
    
    def handle_parameter_change_feedback(self, event: RealTimeFeedbackEvent):
        """处理参数变化反馈"""
        element_id = event.data.get('element_id')
        property_name = event.data.get('property')
        value = event.data.get('value')
        
        try:
            # 启动实时预览
            preview_data = {
                'type': 'parameter_change',
                'element_id': element_id,
                'property': property_name,
                'value': value,
                'description': f"修改 {property_name} 为 {value}"
            }
            
            if self.preview_widget:
                self.preview_widget.start_preview(preview_data)
                
        except Exception as e:
            logger.error(f"处理参数变化反馈失败: {e}")
    
    def handle_ai_generation_feedback(self, event: RealTimeFeedbackEvent):
        """处理AI生成反馈"""
        progress = event.data.get('progress', 0)
        status = event.data.get('status', '')
        
        try:
            # 更新状态栏进度
            if hasattr(self.main_window, 'status_notification_manager'):
                self.main_window.status_notification_manager.show_progress(progress, status)
                
        except Exception as e:
            logger.error(f"处理AI生成反馈失败: {e}")
    
    def handle_timeline_update_feedback(self, event: RealTimeFeedbackEvent):
        """处理时间轴更新反馈"""
        # 实现时间轴更新反馈逻辑
        pass
    
    def handle_stage_preview_feedback(self, event: RealTimeFeedbackEvent):
        """处理舞台预览反馈"""
        # 实现舞台预览反馈逻辑
        pass
    
    def handle_property_edit_feedback(self, event: RealTimeFeedbackEvent):
        """处理属性编辑反馈"""
        # 实现属性编辑反馈逻辑
        pass
    
    def handle_animation_play_feedback(self, event: RealTimeFeedbackEvent):
        """处理动画播放反馈"""
        # 实现动画播放反馈逻辑
        pass
    
    def get_current_time_segment(self, position: float):
        """获取当前时间段"""
        # 实现获取当前时间段的逻辑
        return None
    
    def highlight_time_segment(self, segment):
        """高亮时间段"""
        # 实现高亮时间段的逻辑
        pass
    
    def on_preview_applied(self, preview_data: Dict[str, Any]):
        """预览应用处理"""
        logger.info(f"预览已应用: {preview_data}")
    
    def get_feedback_summary(self) -> dict:
        """获取反馈系统摘要"""
        return {
            'queue_size': len(self.feedback_queue),
            'handlers_count': len(self.feedback_handlers),
            'indicators_count': len(self.visual_indicators),
            'debounce_timers': len(self.debounce_timers),
            'preview_active': self.preview_widget.is_previewing if self.preview_widget else False
        }


class DirectManipulationManager(QObject):
    """直接操作管理器"""

    element_moved = pyqtSignal(str, float, float)      # 元素移动信号
    element_resized = pyqtSignal(str, float, float)    # 元素缩放信号
    element_rotated = pyqtSignal(str, float)           # 元素旋转信号
    element_edited = pyqtSignal(str, str)              # 元素编辑信号

    def __init__(self, stage_widget):
        super().__init__()
        self.stage_widget = stage_widget
        self.selected_element = None
        self.manipulation_mode = None
        self.drag_start_pos = None
        self.original_geometry = None

        self.setup_manipulation_handlers()
        logger.info("直接操作管理器初始化完成")

    def setup_manipulation_handlers(self):
        """设置操作处理器"""
        if self.stage_widget:
            # 连接鼠标事件
            self.stage_widget.mousePressEvent = self.on_mouse_press
            self.stage_widget.mouseMoveEvent = self.on_mouse_move
            self.stage_widget.mouseReleaseEvent = self.on_mouse_release
            self.stage_widget.mouseDoubleClickEvent = self.on_mouse_double_click

    def on_mouse_press(self, event):
        """鼠标按下事件"""
        try:
            pos = event.position()
            self.drag_start_pos = (pos.x(), pos.y())

            # 检测点击的元素
            element = self.get_element_at_position(pos.x(), pos.y())

            if element:
                self.select_element(element)

                # 检测操作模式
                self.manipulation_mode = self.detect_manipulation_mode(element, pos.x(), pos.y())

                # 记录原始几何信息
                self.original_geometry = self.get_element_geometry(element)

        except Exception as e:
            logger.error(f"鼠标按下事件处理失败: {e}")

    def on_mouse_move(self, event):
        """鼠标移动事件"""
        try:
            if not self.selected_element or not self.drag_start_pos:
                return

            pos = event.position()
            dx = pos.x() - self.drag_start_pos[0]
            dy = pos.y() - self.drag_start_pos[1]

            if self.manipulation_mode == "move":
                self.move_element(self.selected_element, dx, dy)
            elif self.manipulation_mode == "resize":
                self.resize_element(self.selected_element, dx, dy)
            elif self.manipulation_mode == "rotate":
                self.rotate_element(self.selected_element, dx, dy)

        except Exception as e:
            logger.error(f"鼠标移动事件处理失败: {e}")

    def on_mouse_release(self, event):
        """鼠标释放事件"""
        try:
            if self.selected_element and self.manipulation_mode:
                # 完成操作，发送信号
                if self.manipulation_mode == "move":
                    pos = event.position()
                    self.element_moved.emit(self.selected_element, pos.x(), pos.y())
                elif self.manipulation_mode == "resize":
                    geometry = self.get_element_geometry(self.selected_element)
                    self.element_resized.emit(self.selected_element, geometry['width'], geometry['height'])
                elif self.manipulation_mode == "rotate":
                    rotation = self.get_element_rotation(self.selected_element)
                    self.element_rotated.emit(self.selected_element, rotation)

            # 重置状态
            self.manipulation_mode = None
            self.drag_start_pos = None
            self.original_geometry = None

        except Exception as e:
            logger.error(f"鼠标释放事件处理失败: {e}")

    def on_mouse_double_click(self, event):
        """鼠标双击事件"""
        try:
            pos = event.position()
            element = self.get_element_at_position(pos.x(), pos.y())

            if element and self.is_text_element(element):
                # 进入文本编辑模式
                self.enter_text_edit_mode(element)

        except Exception as e:
            logger.error(f"鼠标双击事件处理失败: {e}")

    def select_element(self, element_id: str):
        """选择元素"""
        self.selected_element = element_id

        # 显示选择框和操作手柄
        self.show_selection_handles(element_id)

    def show_selection_handles(self, element_id: str):
        """显示选择手柄"""
        # 实现选择手柄显示逻辑
        pass

    def detect_manipulation_mode(self, element_id: str, x: float, y: float) -> str:
        """检测操作模式"""
        # 检测是否点击在缩放手柄上
        if self.is_on_resize_handle(element_id, x, y):
            return "resize"

        # 检测是否点击在旋转手柄上
        if self.is_on_rotate_handle(element_id, x, y):
            return "rotate"

        # 默认为移动模式
        return "move"

    def move_element(self, element_id: str, dx: float, dy: float):
        """移动元素"""
        # 实现元素移动逻辑
        pass

    def resize_element(self, element_id: str, dx: float, dy: float):
        """缩放元素"""
        # 实现元素缩放逻辑
        pass

    def rotate_element(self, element_id: str, dx: float, dy: float):
        """旋转元素"""
        # 实现元素旋转逻辑
        pass

    def enter_text_edit_mode(self, element_id: str):
        """进入文本编辑模式"""
        # 实现文本编辑模式
        pass

    def get_element_at_position(self, x: float, y: float) -> Optional[str]:
        """获取指定位置的元素"""
        # 实现位置检测逻辑
        return None

    def get_element_geometry(self, element_id: str) -> Dict[str, float]:
        """获取元素几何信息"""
        # 实现几何信息获取逻辑
        return {'x': 0, 'y': 0, 'width': 100, 'height': 100}

    def get_element_rotation(self, element_id: str) -> float:
        """获取元素旋转角度"""
        # 实现旋转角度获取逻辑
        return 0.0

    def is_text_element(self, element_id: str) -> bool:
        """判断是否为文本元素"""
        # 实现文本元素判断逻辑
        return False

    def is_on_resize_handle(self, element_id: str, x: float, y: float) -> bool:
        """判断是否点击在缩放手柄上"""
        # 实现缩放手柄检测逻辑
        return False

    def is_on_rotate_handle(self, element_id: str, x: float, y: float) -> bool:
        """判断是否点击在旋转手柄上"""
        # 实现旋转手柄检测逻辑
        return False


class WYSIWYGManager:
    """所见即所得管理器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.realtime_feedback_system = None
        self.direct_manipulation_manager = None

        self.initialize_wysiwyg_system()
        logger.info("所见即所得管理器初始化完成")

    def initialize_wysiwyg_system(self):
        """初始化所见即所得系统"""
        try:
            # 初始化实时反馈系统
            self.realtime_feedback_system = RealTimeFeedbackSystem(self.main_window)

            # 初始化直接操作管理器
            if hasattr(self.main_window, 'stage_widget'):
                self.direct_manipulation_manager = DirectManipulationManager(
                    self.main_window.stage_widget
                )

                # 连接直接操作信号
                self.connect_direct_manipulation_signals()

            # 设置实时反馈连接
            self.setup_realtime_feedback_connections()

        except Exception as e:
            logger.error(f"初始化所见即所得系统失败: {e}")

    def connect_direct_manipulation_signals(self):
        """连接直接操作信号"""
        if self.direct_manipulation_manager:
            self.direct_manipulation_manager.element_moved.connect(self.on_element_moved)
            self.direct_manipulation_manager.element_resized.connect(self.on_element_resized)
            self.direct_manipulation_manager.element_rotated.connect(self.on_element_rotated)
            self.direct_manipulation_manager.element_edited.connect(self.on_element_edited)

    def setup_realtime_feedback_connections(self):
        """设置实时反馈连接"""
        if self.realtime_feedback_system:
            # 连接音频播放位置更新
            if hasattr(self.main_window, 'audio_widget'):
                # 假设音频组件有位置更新信号
                pass

            # 连接属性面板变化
            if hasattr(self.main_window, 'properties_widget'):
                # 假设属性面板有属性变化信号
                pass

    def on_element_moved(self, element_id: str, x: float, y: float):
        """元素移动处理"""
        # 添加实时反馈事件
        self.realtime_feedback_system.add_feedback_event(
            FeedbackType.ELEMENT_SELECTION,
            {'element_id': element_id, 'x': x, 'y': y, 'action': 'moved'},
            FeedbackPriority.HIGH
        )

    def on_element_resized(self, element_id: str, width: float, height: float):
        """元素缩放处理"""
        # 添加实时反馈事件
        self.realtime_feedback_system.add_feedback_event(
            FeedbackType.PARAMETER_CHANGE,
            {'element_id': element_id, 'property': 'size', 'value': f"{width}x{height}"},
            FeedbackPriority.HIGH
        )

    def on_element_rotated(self, element_id: str, rotation: float):
        """元素旋转处理"""
        # 添加实时反馈事件
        self.realtime_feedback_system.add_feedback_event(
            FeedbackType.PARAMETER_CHANGE,
            {'element_id': element_id, 'property': 'rotation', 'value': rotation},
            FeedbackPriority.HIGH
        )

    def on_element_edited(self, element_id: str, content: str):
        """元素编辑处理"""
        # 添加实时反馈事件
        self.realtime_feedback_system.add_feedback_event(
            FeedbackType.PROPERTY_EDIT,
            {'element_id': element_id, 'property': 'content', 'value': content},
            FeedbackPriority.MEDIUM
        )

    def trigger_audio_position_feedback(self, position: float):
        """触发音频位置反馈"""
        self.realtime_feedback_system.add_feedback_event(
            FeedbackType.AUDIO_POSITION,
            {'position': position},
            FeedbackPriority.CRITICAL
        )

    def trigger_ai_generation_feedback(self, progress: int, status: str):
        """触发AI生成反馈"""
        self.realtime_feedback_system.add_feedback_event(
            FeedbackType.AI_GENERATION,
            {'progress': progress, 'status': status},
            FeedbackPriority.HIGH
        )

    def get_wysiwyg_summary(self) -> dict:
        """获取所见即所得系统摘要"""
        summary = {
            'realtime_feedback': self.realtime_feedback_system.get_feedback_summary() if self.realtime_feedback_system else {},
            'direct_manipulation_active': self.direct_manipulation_manager is not None,
            'selected_element': self.direct_manipulation_manager.selected_element if self.direct_manipulation_manager else None
        }

        return summary
