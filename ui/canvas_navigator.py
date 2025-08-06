"""
AI Animation Studio - 画布导航器
提供画布的缩略图导航和快速定位功能
"""

from typing import Optional, Dict, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QSpinBox, QComboBox, QFrame, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QTimer
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPixmap, QCursor,
    QMouseEvent, QWheelEvent
)

from core.data_structures import Element
from core.logger import get_logger

logger = get_logger("canvas_navigator")


class CanvasNavigator(QWidget):
    """画布导航器"""
    
    # 信号定义
    viewport_changed = pyqtSignal(QRect)  # 视口改变信号
    zoom_requested = pyqtSignal(float)    # 缩放请求信号
    pan_requested = pyqtSignal(QPoint)    # 平移请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas_width = 1920
        self.canvas_height = 1080
        self.scale_factor = 0.4
        self.viewport_rect = QRect(0, 0, 800, 600)
        self.elements = {}
        
        # 导航器设置
        self.navigator_width = 200
        self.navigator_height = 150
        self.navigator_scale = 0.1
        
        # 交互状态
        self.dragging_viewport = False
        self.drag_start_pos = QPoint()
        
        self.setMinimumSize(220, 200)
        self.setMaximumSize(250, 230)
        
        self.setup_ui()
        
        # 更新定时器
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update)
        
        logger.info("画布导航器初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题
        title_label = QLabel("导航器")
        title_label.setFont(QFont("", 10, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 导航器画布
        self.navigator_canvas = QFrame()
        self.navigator_canvas.setFrameStyle(QFrame.Shape.StyledPanel)
        self.navigator_canvas.setMinimumSize(self.navigator_width, self.navigator_height)
        self.navigator_canvas.setMaximumSize(self.navigator_width, self.navigator_height)
        self.navigator_canvas.paintEvent = self.paint_navigator
        self.navigator_canvas.mousePressEvent = self.navigator_mouse_press
        self.navigator_canvas.mouseMoveEvent = self.navigator_mouse_move
        self.navigator_canvas.mouseReleaseEvent = self.navigator_mouse_release
        layout.addWidget(self.navigator_canvas)
        
        # 缩放控制
        zoom_group = QGroupBox("缩放")
        zoom_layout = QVBoxLayout(zoom_group)
        
        # 缩放滑块
        zoom_slider_layout = QHBoxLayout()
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 500)  # 10% - 500%
        self.zoom_slider.setValue(int(self.scale_factor * 100))
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        
        self.zoom_label = QLabel(f"{int(self.scale_factor * 100)}%")
        self.zoom_label.setMinimumWidth(40)
        
        zoom_slider_layout.addWidget(self.zoom_slider)
        zoom_slider_layout.addWidget(self.zoom_label)
        zoom_layout.addLayout(zoom_slider_layout)
        
        # 缩放预设按钮
        zoom_presets_layout = QHBoxLayout()
        zoom_presets = [("适合", "fit"), ("100%", 1.0), ("200%", 2.0)]
        
        for name, value in zoom_presets:
            btn = QPushButton(name)
            btn.setMaximumWidth(50)
            if isinstance(value, float):
                btn.clicked.connect(lambda checked, v=value: self.zoom_requested.emit(v))
            else:
                btn.clicked.connect(lambda checked: self.zoom_requested.emit(-1))  # -1表示适合窗口
            zoom_presets_layout.addWidget(btn)
        
        zoom_layout.addLayout(zoom_presets_layout)
        layout.addWidget(zoom_group)
        
        # 视图控制
        view_group = QGroupBox("视图")
        view_layout = QVBoxLayout(view_group)
        
        # 居中按钮
        center_btn = QPushButton("居中视图")
        center_btn.clicked.connect(self.center_view)
        view_layout.addWidget(center_btn)
        
        # 重置视图按钮
        reset_btn = QPushButton("重置视图")
        reset_btn.clicked.connect(self.reset_view)
        view_layout.addWidget(reset_btn)
        
        layout.addWidget(view_group)
        
        layout.addStretch()
    
    def paint_navigator(self, event):
        """绘制导航器"""
        painter = QPainter(self.navigator_canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 计算导航器中的画布矩形
        canvas_rect = self.get_canvas_rect_in_navigator()
        
        # 绘制画布背景
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(canvas_rect)
        
        # 绘制元素（简化表示）
        self.draw_elements_in_navigator(painter, canvas_rect)
        
        # 绘制视口矩形
        viewport_rect = self.get_viewport_rect_in_navigator(canvas_rect)
        painter.setBrush(QBrush(QColor(0, 120, 255, 50)))
        painter.setPen(QPen(QColor(0, 120, 255), 2))
        painter.drawRect(viewport_rect)
        
        # 绘制视口边框
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 120, 255), 1, Qt.PenStyle.DashLine))
        painter.drawRect(viewport_rect)
    
    def get_canvas_rect_in_navigator(self) -> QRect:
        """获取画布在导航器中的矩形"""
        # 计算缩放比例以适应导航器
        scale_x = (self.navigator_width - 20) / self.canvas_width
        scale_y = (self.navigator_height - 20) / self.canvas_height
        scale = min(scale_x, scale_y)
        
        # 计算画布大小
        canvas_w = int(self.canvas_width * scale)
        canvas_h = int(self.canvas_height * scale)
        
        # 居中显示
        x = (self.navigator_width - canvas_w) // 2
        y = (self.navigator_height - canvas_h) // 2
        
        return QRect(x, y, canvas_w, canvas_h)
    
    def get_viewport_rect_in_navigator(self, canvas_rect: QRect) -> QRect:
        """获取视口在导航器中的矩形"""
        # 计算视口在画布中的相对位置
        canvas_scale = canvas_rect.width() / self.canvas_width
        
        # 视口在导航器中的位置和大小
        viewport_x = canvas_rect.x() + int(self.viewport_rect.x() * canvas_scale)
        viewport_y = canvas_rect.y() + int(self.viewport_rect.y() * canvas_scale)
        viewport_w = int(self.viewport_rect.width() * canvas_scale)
        viewport_h = int(self.viewport_rect.height() * canvas_scale)
        
        return QRect(viewport_x, viewport_y, viewport_w, viewport_h)
    
    def draw_elements_in_navigator(self, painter: QPainter, canvas_rect: QRect):
        """在导航器中绘制元素"""
        if not self.elements:
            return
        
        canvas_scale = canvas_rect.width() / self.canvas_width
        
        for element_id, element in self.elements.items():
            # 计算元素在导航器中的位置
            elem_x = canvas_rect.x() + int(element.position.x * canvas_scale)
            elem_y = canvas_rect.y() + int(element.position.y * canvas_scale)
            elem_w = max(2, int(50 * canvas_scale))  # 最小2像素宽度
            elem_h = max(2, int(30 * canvas_scale))  # 最小2像素高度
            
            # 根据元素类型设置颜色
            if element.element_type.value == "text":
                color = QColor(100, 150, 255)
            elif element.element_type.value == "image":
                color = QColor(255, 150, 100)
            elif element.element_type.value == "shape":
                color = QColor(150, 255, 100)
            else:
                color = QColor(200, 200, 200)
            
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(), 1))
            painter.drawRect(elem_x, elem_y, elem_w, elem_h)
    
    def navigator_mouse_press(self, event: QMouseEvent):
        """导航器鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            canvas_rect = self.get_canvas_rect_in_navigator()
            
            if canvas_rect.contains(event.position().toPoint()):
                self.dragging_viewport = True
                self.drag_start_pos = event.position().toPoint()
                
                # 计算点击位置对应的画布坐标
                canvas_scale = canvas_rect.width() / self.canvas_width
                canvas_x = (event.position().x() - canvas_rect.x()) / canvas_scale
                canvas_y = (event.position().y() - canvas_rect.y()) / canvas_scale
                
                # 发送平移请求
                self.pan_requested.emit(QPoint(int(canvas_x), int(canvas_y)))
    
    def navigator_mouse_move(self, event: QMouseEvent):
        """导航器鼠标移动事件"""
        if self.dragging_viewport:
            canvas_rect = self.get_canvas_rect_in_navigator()
            canvas_scale = canvas_rect.width() / self.canvas_width
            
            # 计算移动距离
            delta = event.position().toPoint() - self.drag_start_pos
            canvas_delta_x = delta.x() / canvas_scale
            canvas_delta_y = delta.y() / canvas_scale
            
            # 更新视口位置
            new_x = self.viewport_rect.x() + canvas_delta_x
            new_y = self.viewport_rect.y() + canvas_delta_y
            
            self.pan_requested.emit(QPoint(int(new_x), int(new_y)))
            self.drag_start_pos = event.position().toPoint()
    
    def navigator_mouse_release(self, event: QMouseEvent):
        """导航器鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging_viewport = False
    
    def on_zoom_slider_changed(self, value: int):
        """缩放滑块改变事件"""
        scale = value / 100.0
        self.zoom_label.setText(f"{value}%")
        self.zoom_requested.emit(scale)
    
    def center_view(self):
        """居中视图"""
        center_x = self.canvas_width // 2 - self.viewport_rect.width() // 2
        center_y = self.canvas_height // 2 - self.viewport_rect.height() // 2
        self.pan_requested.emit(QPoint(center_x, center_y))
    
    def reset_view(self):
        """重置视图"""
        self.zoom_requested.emit(-1)  # 适合窗口
        self.center_view()
    
    def set_canvas_size(self, width: int, height: int):
        """设置画布大小"""
        self.canvas_width = width
        self.canvas_height = height
        self.schedule_update()
    
    def set_scale_factor(self, scale: float):
        """设置缩放因子"""
        self.scale_factor = scale
        self.zoom_slider.setValue(int(scale * 100))
        self.zoom_label.setText(f"{int(scale * 100)}%")
        self.schedule_update()
    
    def set_viewport_rect(self, rect: QRect):
        """设置视口矩形"""
        self.viewport_rect = rect
        self.schedule_update()
    
    def set_elements(self, elements: Dict[str, Element]):
        """设置元素列表"""
        self.elements = elements
        self.schedule_update()
    
    def schedule_update(self):
        """安排更新"""
        self.update_timer.start(50)  # 50ms延迟，避免频繁更新
    
    def update_navigator(self):
        """更新导航器显示"""
        self.navigator_canvas.update()
