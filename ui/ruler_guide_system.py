"""
AI Animation Studio - 标尺和参考线系统
提供专业的标尺显示和参考线管理功能
"""

from typing import List, Tuple, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMenu, QInputDialog, QMessageBox, QListWidget,
    QListWidgetItem, QGroupBox, QCheckBox, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QFontMetrics,
    QMouseEvent, QContextMenuEvent, QAction
)

from core.logger import get_logger

logger = get_logger("ruler_guide_system")


class RulerWidget(QWidget):
    """标尺控件"""
    
    guide_added = pyqtSignal(str, float)  # 参考线添加信号 (orientation, position)
    
    def __init__(self, orientation: str = "horizontal", parent=None):
        super().__init__(parent)
        self.orientation = orientation  # "horizontal" or "vertical"
        self.scale_factor = 1.0
        self.offset = 0
        self.canvas_size = 1920 if orientation == "horizontal" else 1080
        
        # 标尺设置
        self.ruler_size = 25
        self.background_color = QColor("#f0f0f0")
        self.border_color = QColor("#c0c0c0")
        self.text_color = QColor("#666666")
        self.tick_color = QColor("#999999")
        
        # 刻度设置
        self.major_tick_interval = 100  # 主刻度间隔
        self.minor_tick_interval = 20   # 次刻度间隔
        self.micro_tick_interval = 5    # 微刻度间隔
        
        # 单位设置
        self.unit = "px"  # px, cm, mm, in
        self.unit_scale = 1.0  # 单位转换比例
        
        # 参考线
        self.guides = []
        self.dragging_guide = None
        self.guide_color = QColor("#ff6b6b")
        
        if orientation == "horizontal":
            self.setFixedHeight(self.ruler_size)
            self.setMinimumWidth(200)
        else:
            self.setFixedWidth(self.ruler_size)
            self.setMinimumHeight(200)
        
        self.setMouseTracking(True)
        
        logger.debug(f"{orientation}标尺初始化完成")
    
    def paintEvent(self, event):
        """绘制标尺"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制背景
        painter.fillRect(self.rect(), self.background_color)
        
        # 绘制边框
        painter.setPen(QPen(self.border_color, 1))
        if self.orientation == "horizontal":
            painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        else:
            painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        
        # 绘制刻度
        self.draw_ticks(painter)
        
        # 绘制参考线指示器
        self.draw_guide_indicators(painter)
    
    def draw_ticks(self, painter: QPainter):
        """绘制刻度"""
        painter.setPen(QPen(self.tick_color, 1))
        painter.setFont(QFont("Arial", 8))
        
        # 计算可见范围
        if self.orientation == "horizontal":
            start_pos = -self.offset / self.scale_factor
            end_pos = start_pos + self.width() / self.scale_factor
            ruler_length = self.width()
        else:
            start_pos = -self.offset / self.scale_factor
            end_pos = start_pos + self.height() / self.scale_factor
            ruler_length = self.height()
        
        # 动态调整刻度间隔
        pixel_per_unit = self.scale_factor * self.unit_scale
        
        if pixel_per_unit < 10:
            # 缩放很小时，增大刻度间隔
            major_interval = self.major_tick_interval * 5
            minor_interval = self.minor_tick_interval * 5
        elif pixel_per_unit > 200:
            # 缩放很大时，减小刻度间隔
            major_interval = self.major_tick_interval // 2
            minor_interval = self.minor_tick_interval // 2
        else:
            major_interval = self.major_tick_interval
            minor_interval = self.minor_tick_interval
        
        # 绘制主刻度
        major_start = int(start_pos // major_interval) * major_interval
        for pos in range(major_start, int(end_pos) + major_interval, major_interval):
            if pos < 0 or pos > self.canvas_size:
                continue
            
            screen_pos = self.offset + pos * self.scale_factor
            
            if self.orientation == "horizontal":
                if 0 <= screen_pos <= self.width():
                    painter.drawLine(int(screen_pos), self.height() - 15, int(screen_pos), self.height())
                    # 绘制数字
                    text = str(int(pos / self.unit_scale))
                    text_rect = painter.fontMetrics().boundingRect(text)
                    text_x = screen_pos - text_rect.width() // 2
                    painter.setPen(QPen(self.text_color))
                    painter.drawText(int(text_x), self.height() - 18, text)
                    painter.setPen(QPen(self.tick_color))
            else:
                if 0 <= screen_pos <= self.height():
                    painter.drawLine(self.width() - 15, int(screen_pos), self.width(), int(screen_pos))
                    # 绘制数字
                    text = str(int(pos / self.unit_scale))
                    text_rect = painter.fontMetrics().boundingRect(text)
                    text_y = screen_pos + text_rect.height() // 2
                    painter.setPen(QPen(self.text_color))
                    painter.drawText(self.width() - text_rect.width() - 18, int(text_y), text)
                    painter.setPen(QPen(self.tick_color))
        
        # 绘制次刻度
        minor_start = int(start_pos // minor_interval) * minor_interval
        for pos in range(minor_start, int(end_pos) + minor_interval, minor_interval):
            if pos < 0 or pos > self.canvas_size or pos % major_interval == 0:
                continue
            
            screen_pos = self.offset + pos * self.scale_factor
            
            if self.orientation == "horizontal":
                if 0 <= screen_pos <= self.width():
                    painter.drawLine(int(screen_pos), self.height() - 8, int(screen_pos), self.height())
            else:
                if 0 <= screen_pos <= self.height():
                    painter.drawLine(self.width() - 8, int(screen_pos), self.width(), int(screen_pos))
    
    def draw_guide_indicators(self, painter: QPainter):
        """绘制参考线指示器"""
        painter.setPen(QPen(self.guide_color, 2))
        
        for guide_pos in self.guides:
            screen_pos = self.offset + guide_pos * self.scale_factor
            
            if self.orientation == "horizontal":
                if 0 <= screen_pos <= self.width():
                    # 绘制三角形指示器
                    points = [
                        QPoint(int(screen_pos), self.height()),
                        QPoint(int(screen_pos - 5), self.height() - 10),
                        QPoint(int(screen_pos + 5), self.height() - 10)
                    ]
                    painter.setBrush(QBrush(self.guide_color))
                    painter.drawPolygon(points)
            else:
                if 0 <= screen_pos <= self.height():
                    # 绘制三角形指示器
                    points = [
                        QPoint(self.width(), int(screen_pos)),
                        QPoint(self.width() - 10, int(screen_pos - 5)),
                        QPoint(self.width() - 10, int(screen_pos + 5))
                    ]
                    painter.setBrush(QBrush(self.guide_color))
                    painter.drawPolygon(points)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 创建新参考线
            if self.orientation == "horizontal":
                canvas_pos = (event.position().x() - self.offset) / self.scale_factor
            else:
                canvas_pos = (event.position().y() - self.offset) / self.scale_factor
            
            if 0 <= canvas_pos <= self.canvas_size:
                self.guides.append(canvas_pos)
                self.guide_added.emit(self.orientation, canvas_pos)
                self.update()
                logger.debug(f"添加{self.orientation}参考线: {canvas_pos}")
    
    def contextMenuEvent(self, event: QContextMenuEvent):
        """右键菜单事件"""
        menu = QMenu(self)
        
        # 清除所有参考线
        clear_action = QAction("清除所有参考线", self)
        clear_action.triggered.connect(self.clear_all_guides)
        menu.addAction(clear_action)
        
        # 添加参考线
        add_action = QAction("添加参考线...", self)
        add_action.triggered.connect(self.add_guide_dialog)
        menu.addAction(add_action)
        
        menu.exec(event.globalPos())
    
    def clear_all_guides(self):
        """清除所有参考线"""
        self.guides.clear()
        self.update()
        logger.debug(f"清除所有{self.orientation}参考线")
    
    def add_guide_dialog(self):
        """添加参考线对话框"""
        position, ok = QInputDialog.getDouble(
            self, "添加参考线", 
            f"输入{self.orientation}参考线位置:", 
            0, 0, self.canvas_size, 1
        )
        
        if ok:
            self.guides.append(position)
            self.guide_added.emit(self.orientation, position)
            self.update()
    
    def set_scale_factor(self, scale: float):
        """设置缩放因子"""
        self.scale_factor = scale
        self.update()
    
    def set_offset(self, offset: float):
        """设置偏移量"""
        self.offset = offset
        self.update()
    
    def set_canvas_size(self, size: int):
        """设置画布大小"""
        self.canvas_size = size
        self.update()
    
    def add_guide(self, position: float):
        """添加参考线"""
        if position not in self.guides:
            self.guides.append(position)
            self.guides.sort()
            self.update()
    
    def remove_guide(self, position: float):
        """移除参考线"""
        if position in self.guides:
            self.guides.remove(position)
            self.update()
    
    def get_guides(self) -> List[float]:
        """获取所有参考线位置"""
        return self.guides.copy()


class GuideManager(QWidget):
    """参考线管理器"""
    
    guide_visibility_changed = pyqtSignal(bool)
    guide_removed = pyqtSignal(str, float)  # orientation, position
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.horizontal_guides = []
        self.vertical_guides = []
        
        self.setup_ui()
        
        logger.info("参考线管理器初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("参考线管理")
        title_label.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 显示控制
        self.show_guides_cb = QCheckBox("显示参考线")
        self.show_guides_cb.setChecked(True)
        self.show_guides_cb.toggled.connect(self.guide_visibility_changed.emit)
        layout.addWidget(self.show_guides_cb)
        
        # 参考线列表
        guides_group = QGroupBox("参考线列表")
        guides_layout = QVBoxLayout(guides_group)
        
        self.guides_list = QListWidget()
        self.guides_list.setMaximumHeight(150)
        guides_layout.addWidget(self.guides_list)
        
        # 操作按钮
        buttons_layout = QHBoxLayout()
        
        remove_btn = QPushButton("删除")
        remove_btn.clicked.connect(self.remove_selected_guide)
        buttons_layout.addWidget(remove_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear_all_guides)
        buttons_layout.addWidget(clear_btn)
        
        guides_layout.addLayout(buttons_layout)
        layout.addWidget(guides_group)
        
        layout.addStretch()
    
    def add_guide(self, orientation: str, position: float):
        """添加参考线"""
        if orientation == "horizontal":
            if position not in self.horizontal_guides:
                self.horizontal_guides.append(position)
                self.horizontal_guides.sort()
        else:
            if position not in self.vertical_guides:
                self.vertical_guides.append(position)
                self.vertical_guides.sort()
        
        self.update_guides_list()
    
    def remove_guide(self, orientation: str, position: float):
        """移除参考线"""
        if orientation == "horizontal" and position in self.horizontal_guides:
            self.horizontal_guides.remove(position)
        elif orientation == "vertical" and position in self.vertical_guides:
            self.vertical_guides.remove(position)
        
        self.update_guides_list()
        self.guide_removed.emit(orientation, position)
    
    def clear_all_guides(self):
        """清空所有参考线"""
        self.horizontal_guides.clear()
        self.vertical_guides.clear()
        self.update_guides_list()
    
    def remove_selected_guide(self):
        """删除选中的参考线"""
        current_item = self.guides_list.currentItem()
        if current_item:
            text = current_item.text()
            if text.startswith("水平"):
                position = float(text.split(":")[1].strip().replace("px", ""))
                self.remove_guide("horizontal", position)
            elif text.startswith("垂直"):
                position = float(text.split(":")[1].strip().replace("px", ""))
                self.remove_guide("vertical", position)
    
    def update_guides_list(self):
        """更新参考线列表"""
        self.guides_list.clear()
        
        # 添加水平参考线
        for pos in self.horizontal_guides:
            item = QListWidgetItem(f"水平: {pos:.1f}px")
            item.setData(Qt.ItemDataRole.UserRole, ("horizontal", pos))
            self.guides_list.addItem(item)
        
        # 添加垂直参考线
        for pos in self.vertical_guides:
            item = QListWidgetItem(f"垂直: {pos:.1f}px")
            item.setData(Qt.ItemDataRole.UserRole, ("vertical", pos))
            self.guides_list.addItem(item)
    
    def get_horizontal_guides(self) -> List[float]:
        """获取水平参考线"""
        return self.horizontal_guides.copy()
    
    def get_vertical_guides(self) -> List[float]:
        """获取垂直参考线"""
        return self.vertical_guides.copy()
