"""
AI Animation Studio - 增强时间段管理器
提供可视化时间轴、拖拽调整、颜色编码等专业时间段管理功能
"""

from typing import List, Dict, Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QComboBox, QSpinBox, QDoubleSpinBox,
    QColorDialog, QInputDialog, QMessageBox, QMenu, QAction, QFrame,
    QScrollArea, QSplitter, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QCheckBox, QSlider, QLineEdit, QTextEdit, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QTimer
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QLinearGradient, QPolygon,
    QMouseEvent, QContextMenuEvent, QDragEnterEvent, QDropEvent, QCursor
)

from core.data_structures import TimeSegment, AnimationType
from core.logger import get_logger

logger = get_logger("enhanced_timeline_manager")


class TimelineSegment:
    """时间轴段对象"""
    
    def __init__(self, start_time: float, end_time: float, name: str = "", 
                 segment_type: str = "animation", color: QColor = None):
        self.start_time = start_time
        self.end_time = end_time
        self.name = name or f"段 {id(self)}"
        self.segment_type = segment_type  # animation, pause, transition, marker
        self.color = color or self.get_default_color(segment_type)
        self.description = ""
        self.locked = False
        self.visible = True
        self.animation_type = AnimationType.FADE_IN
        self.properties = {}
        self.id = id(self)
    
    @staticmethod
    def get_default_color(segment_type: str) -> QColor:
        """获取段类型的默认颜色"""
        color_map = {
            "animation": QColor("#2196F3"),    # 蓝色
            "pause": QColor("#FF9800"),        # 橙色
            "transition": QColor("#4CAF50"),   # 绿色
            "marker": QColor("#F44336"),       # 红色
            "audio": QColor("#9C27B0"),        # 紫色
            "video": QColor("#00BCD4"),        # 青色
        }
        return color_map.get(segment_type, QColor("#757575"))
    
    @property
    def duration(self) -> float:
        """获取段持续时间"""
        return self.end_time - self.start_time
    
    def contains_time(self, time: float) -> bool:
        """检查时间是否在段内"""
        return self.start_time <= time <= self.end_time
    
    def overlaps_with(self, other: 'TimelineSegment') -> bool:
        """检查是否与另一个段重叠"""
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)


class VisualTimelineWidget(QWidget):
    """可视化时间轴组件"""
    
    # 信号定义
    segment_selected = pyqtSignal(int)           # 段选择信号
    segment_moved = pyqtSignal(int, float, float) # 段移动信号
    segment_resized = pyqtSignal(int, float, float) # 段大小调整信号
    time_clicked = pyqtSignal(float)             # 时间点击信号
    segment_double_clicked = pyqtSignal(int)     # 段双击信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        self.setAcceptDrops(True)
        
        # 时间轴数据
        self.segments = []
        self.total_duration = 30.0
        self.current_time = 0.0
        self.selected_segment = None
        
        # 显示设置
        self.pixels_per_second = 50
        self.track_height = 40
        self.track_spacing = 5
        self.ruler_height = 30
        
        # 交互状态
        self.dragging_segment = None
        self.resizing_segment = None
        self.resize_edge = None  # 'start' or 'end'
        self.drag_start_pos = QPoint()
        self.drag_start_time = 0.0
        
        # 颜色设置
        self.background_color = QColor("#FAFAFA")
        self.ruler_color = QColor("#E0E0E0")
        self.grid_color = QColor("#F0F0F0")
        self.playhead_color = QColor("#FF5722")
        self.selection_color = QColor("#2196F3")
        
        # 轨道设置
        self.tracks = ["主轨道", "音频轨道", "效果轨道", "标记轨道"]
        self.track_colors = [
            QColor("#E3F2FD"),  # 浅蓝
            QColor("#F3E5F5"),  # 浅紫
            QColor("#E8F5E8"),  # 浅绿
            QColor("#FFF3E0"),  # 浅橙
        ]
        
        self.setMouseTracking(True)
        
        logger.info("可视化时间轴组件初始化完成")
    
    def add_segment(self, segment: TimelineSegment, track_index: int = 0):
        """添加时间段"""
        segment.track_index = track_index
        self.segments.append(segment)
        self.update()
        logger.debug(f"添加时间段: {segment.name}")
    
    def remove_segment(self, segment_id: int):
        """移除时间段"""
        self.segments = [s for s in self.segments if s.id != segment_id]
        if self.selected_segment == segment_id:
            self.selected_segment = None
        self.update()
    
    def get_segment_by_id(self, segment_id: int) -> Optional[TimelineSegment]:
        """根据ID获取时间段"""
        for segment in self.segments:
            if segment.id == segment_id:
                return segment
        return None
    
    def paintEvent(self, event):
        """绘制时间轴"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # 绘制背景
        painter.fillRect(rect, self.background_color)
        
        # 绘制标尺
        self.draw_ruler(painter, rect)
        
        # 绘制轨道
        self.draw_tracks(painter, rect)
        
        # 绘制时间段
        self.draw_segments(painter, rect)
        
        # 绘制播放头
        self.draw_playhead(painter, rect)
        
        # 绘制选择框
        if self.selected_segment is not None:
            self.draw_selection(painter, rect)
    
    def draw_ruler(self, painter: QPainter, rect: QRect):
        """绘制时间标尺"""
        painter.setPen(QPen(self.ruler_color, 1))
        painter.fillRect(0, 0, rect.width(), self.ruler_height, QColor("#F5F5F5"))
        
        # 绘制时间刻度
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setFont(QFont("Arial", 8))
        
        # 计算刻度间隔
        if self.pixels_per_second >= 100:
            interval = 1.0  # 1秒
        elif self.pixels_per_second >= 50:
            interval = 2.0  # 2秒
        else:
            interval = 5.0  # 5秒
        
        for time in range(0, int(self.total_duration) + 1, int(interval)):
            x = int(time * self.pixels_per_second)
            if x <= rect.width():
                # 绘制刻度线
                painter.drawLine(x, self.ruler_height - 10, x, self.ruler_height)
                
                # 绘制时间标签
                time_text = f"{time}s"
                painter.drawText(x + 2, self.ruler_height - 2, time_text)
    
    def draw_tracks(self, painter: QPainter, rect: QRect):
        """绘制轨道背景"""
        y_offset = self.ruler_height
        
        for i, track_name in enumerate(self.tracks):
            track_rect = QRect(
                0, y_offset + i * (self.track_height + self.track_spacing),
                rect.width(), self.track_height
            )
            
            # 绘制轨道背景
            painter.fillRect(track_rect, self.track_colors[i % len(self.track_colors)])
            
            # 绘制轨道边框
            painter.setPen(QPen(QColor("#CCCCCC"), 1))
            painter.drawRect(track_rect)
            
            # 绘制轨道名称
            painter.setPen(QPen(Qt.GlobalColor.black))
            painter.setFont(QFont("Arial", 9))
            painter.drawText(track_rect.adjusted(5, 0, 0, 0), 
                           Qt.AlignmentFlag.AlignVCenter, track_name)
    
    def draw_segments(self, painter: QPainter, rect: QRect):
        """绘制时间段"""
        y_offset = self.ruler_height
        
        for segment in self.segments:
            if not segment.visible:
                continue
            
            # 计算段的位置和大小
            start_x = int(segment.start_time * self.pixels_per_second)
            end_x = int(segment.end_time * self.pixels_per_second)
            width = end_x - start_x
            
            track_index = getattr(segment, 'track_index', 0)
            y = y_offset + track_index * (self.track_height + self.track_spacing)
            
            segment_rect = QRect(start_x, y + 2, width, self.track_height - 4)
            
            # 绘制段背景
            if segment.locked:
                # 锁定的段使用斜线纹理
                painter.setBrush(QBrush(segment.color.lighter(150)))
            else:
                painter.setBrush(QBrush(segment.color))
            
            # 选中状态的边框
            if self.selected_segment == segment.id:
                painter.setPen(QPen(self.selection_color, 3))
            else:
                painter.setPen(QPen(segment.color.darker(120), 1))
            
            painter.drawRoundedRect(segment_rect, 3, 3)
            
            # 绘制段名称
            painter.setPen(QPen(Qt.GlobalColor.white if segment.color.lightness() < 128 else Qt.GlobalColor.black))
            painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            
            # 文本裁剪
            text_rect = segment_rect.adjusted(5, 0, -5, 0)
            text = segment.name
            if painter.fontMetrics().horizontalAdvance(text) > text_rect.width():
                text = painter.fontMetrics().elidedText(text, Qt.TextElideMode.ElideRight, text_rect.width())
            
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, text)
            
            # 绘制段类型图标
            self.draw_segment_icon(painter, segment, segment_rect)
            
            # 绘制调整手柄
            if self.selected_segment == segment.id and not segment.locked:
                self.draw_resize_handles(painter, segment_rect)
    
    def draw_segment_icon(self, painter: QPainter, segment: TimelineSegment, rect: QRect):
        """绘制段类型图标"""
        icon_size = 12
        icon_rect = QRect(rect.right() - icon_size - 5, rect.top() + 5, icon_size, icon_size)
        
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        
        if segment.segment_type == "animation":
            # 绘制播放图标
            points = [
                QPoint(icon_rect.left() + 2, icon_rect.top() + 2),
                QPoint(icon_rect.right() - 2, icon_rect.center().y()),
                QPoint(icon_rect.left() + 2, icon_rect.bottom() - 2)
            ]
            painter.drawPolygon(QPolygon(points))
        elif segment.segment_type == "pause":
            # 绘制暂停图标
            painter.drawRect(icon_rect.left() + 2, icon_rect.top() + 2, 3, icon_size - 4)
            painter.drawRect(icon_rect.right() - 5, icon_rect.top() + 2, 3, icon_size - 4)
        elif segment.segment_type == "marker":
            # 绘制标记图标
            painter.drawEllipse(icon_rect.adjusted(2, 2, -2, -2))
    
    def draw_resize_handles(self, painter: QPainter, rect: QRect):
        """绘制调整手柄"""
        handle_size = 6
        
        # 左侧手柄
        left_handle = QRect(rect.left() - handle_size // 2, rect.center().y() - handle_size // 2,
                           handle_size, handle_size)
        painter.setBrush(QBrush(self.selection_color))
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawEllipse(left_handle)
        
        # 右侧手柄
        right_handle = QRect(rect.right() - handle_size // 2, rect.center().y() - handle_size // 2,
                            handle_size, handle_size)
        painter.drawEllipse(right_handle)
    
    def draw_playhead(self, painter: QPainter, rect: QRect):
        """绘制播放头"""
        x = int(self.current_time * self.pixels_per_second)
        
        if 0 <= x <= rect.width():
            # 绘制播放线
            painter.setPen(QPen(self.playhead_color, 2))
            painter.drawLine(x, 0, x, rect.height())
            
            # 绘制播放头三角形
            painter.setBrush(QBrush(self.playhead_color))
            points = [
                QPoint(x, 0),
                QPoint(x - 8, 16),
                QPoint(x + 8, 16)
            ]
            painter.drawPolygon(QPolygon(points))
    
    def draw_selection(self, painter: QPainter, rect: QRect):
        """绘制选择框"""
        segment = self.get_segment_by_id(self.selected_segment)
        if not segment:
            return
        
        # 选择框已在draw_segments中绘制
        pass
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            
            # 检查是否点击了段
            clicked_segment = self.get_segment_at_position(pos)
            
            if clicked_segment:
                self.selected_segment = clicked_segment.id
                
                # 检查是否点击了调整手柄
                resize_edge = self.get_resize_edge_at_position(pos, clicked_segment)
                if resize_edge and not clicked_segment.locked:
                    self.resizing_segment = clicked_segment
                    self.resize_edge = resize_edge
                    self.setCursor(Qt.CursorShape.SizeHorCursor)
                else:
                    # 开始拖拽
                    if not clicked_segment.locked:
                        self.dragging_segment = clicked_segment
                        self.drag_start_pos = pos
                        self.drag_start_time = clicked_segment.start_time
                        self.setCursor(Qt.CursorShape.SizeAllCursor)
                
                self.segment_selected.emit(clicked_segment.id)
            else:
                # 点击空白区域
                self.selected_segment = None
                time = pos.x() / self.pixels_per_second
                self.time_clicked.emit(time)
            
            self.update()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        pos = event.position().toPoint()
        
        if self.dragging_segment:
            # 拖拽段
            delta_x = pos.x() - self.drag_start_pos.x()
            delta_time = delta_x / self.pixels_per_second
            
            new_start_time = max(0, self.drag_start_time + delta_time)
            new_end_time = new_start_time + self.dragging_segment.duration
            
            if new_end_time <= self.total_duration:
                self.dragging_segment.start_time = new_start_time
                self.dragging_segment.end_time = new_end_time
                self.update()
        
        elif self.resizing_segment:
            # 调整段大小
            time = pos.x() / self.pixels_per_second
            
            if self.resize_edge == 'start':
                new_start_time = max(0, min(time, self.resizing_segment.end_time - 0.1))
                self.resizing_segment.start_time = new_start_time
            else:  # 'end'
                new_end_time = min(self.total_duration, max(time, self.resizing_segment.start_time + 0.1))
                self.resizing_segment.end_time = new_end_time
            
            self.update()
        
        else:
            # 更新鼠标光标
            segment = self.get_segment_at_position(pos)
            if segment and not segment.locked:
                resize_edge = self.get_resize_edge_at_position(pos, segment)
                if resize_edge:
                    self.setCursor(Qt.CursorShape.SizeHorCursor)
                else:
                    self.setCursor(Qt.CursorShape.SizeAllCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.dragging_segment:
                self.segment_moved.emit(
                    self.dragging_segment.id,
                    self.dragging_segment.start_time,
                    self.dragging_segment.end_time
                )
                self.dragging_segment = None
            
            elif self.resizing_segment:
                self.segment_resized.emit(
                    self.resizing_segment.id,
                    self.resizing_segment.start_time,
                    self.resizing_segment.end_time
                )
                self.resizing_segment = None
                self.resize_edge = None
            
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """鼠标双击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            segment = self.get_segment_at_position(pos)
            
            if segment:
                self.segment_double_clicked.emit(segment.id)
    
    def contextMenuEvent(self, event: QContextMenuEvent):
        """右键菜单事件"""
        pos = event.pos()
        segment = self.get_segment_at_position(pos)
        
        menu = QMenu(self)
        
        if segment:
            # 段相关菜单
            edit_action = QAction("编辑段", self)
            edit_action.triggered.connect(lambda: self.segment_double_clicked.emit(segment.id))
            menu.addAction(edit_action)
            
            duplicate_action = QAction("复制段", self)
            duplicate_action.triggered.connect(lambda: self.duplicate_segment(segment))
            menu.addAction(duplicate_action)
            
            menu.addSeparator()
            
            lock_action = QAction("锁定" if not segment.locked else "解锁", self)
            lock_action.triggered.connect(lambda: self.toggle_segment_lock(segment))
            menu.addAction(lock_action)
            
            delete_action = QAction("删除段", self)
            delete_action.triggered.connect(lambda: self.remove_segment(segment.id))
            menu.addAction(delete_action)
        else:
            # 空白区域菜单
            time = pos.x() / self.pixels_per_second
            
            add_animation_action = QAction("添加动画段", self)
            add_animation_action.triggered.connect(lambda: self.add_segment_at_time(time, "animation"))
            menu.addAction(add_animation_action)
            
            add_pause_action = QAction("添加暂停段", self)
            add_pause_action.triggered.connect(lambda: self.add_segment_at_time(time, "pause"))
            menu.addAction(add_pause_action)
            
            add_marker_action = QAction("添加标记", self)
            add_marker_action.triggered.connect(lambda: self.add_segment_at_time(time, "marker"))
            menu.addAction(add_marker_action)
        
        menu.exec(event.globalPos())
    
    def get_segment_at_position(self, pos: QPoint) -> Optional[TimelineSegment]:
        """获取指定位置的段"""
        if pos.y() < self.ruler_height:
            return None
        
        time = pos.x() / self.pixels_per_second
        track_index = (pos.y() - self.ruler_height) // (self.track_height + self.track_spacing)
        
        for segment in self.segments:
            if (segment.contains_time(time) and 
                getattr(segment, 'track_index', 0) == track_index):
                return segment
        
        return None
    
    def get_resize_edge_at_position(self, pos: QPoint, segment: TimelineSegment) -> Optional[str]:
        """获取调整边缘"""
        start_x = int(segment.start_time * self.pixels_per_second)
        end_x = int(segment.end_time * self.pixels_per_second)
        
        if abs(pos.x() - start_x) < 8:
            return 'start'
        elif abs(pos.x() - end_x) < 8:
            return 'end'
        
        return None
    
    def add_segment_at_time(self, time: float, segment_type: str):
        """在指定时间添加段"""
        duration = 2.0 if segment_type != "marker" else 0.1
        end_time = min(time + duration, self.total_duration)
        
        segment = TimelineSegment(time, end_time, f"新{segment_type}", segment_type)
        self.add_segment(segment)
    
    def duplicate_segment(self, segment: TimelineSegment):
        """复制段"""
        new_start = segment.end_time
        new_end = min(new_start + segment.duration, self.total_duration)
        
        if new_end > new_start:
            new_segment = TimelineSegment(
                new_start, new_end,
                f"{segment.name} 副本",
                segment.segment_type,
                segment.color
            )
            new_segment.track_index = getattr(segment, 'track_index', 0)
            self.add_segment(new_segment)
    
    def toggle_segment_lock(self, segment: TimelineSegment):
        """切换段锁定状态"""
        segment.locked = not segment.locked
        self.update()
    
    def set_current_time(self, time: float):
        """设置当前时间"""
        self.current_time = max(0, min(time, self.duration))
        self.update()
    
    def set_total_duration(self, duration: float):
        """设置总时长"""
        self.duration = max(1.0, duration)
        self.update()
    
    def set_zoom_level(self, pixels_per_second: float):
        """设置缩放级别"""
        self.pixels_per_second = max(10, min(200, pixels_per_second))
        self.update()


class TimeSegmentManager(QWidget):
    """时间段管理器"""

    # 信号定义
    segment_created = pyqtSignal(dict)      # 段创建信号
    segment_updated = pyqtSignal(int, dict) # 段更新信号
    segment_deleted = pyqtSignal(int)       # 段删除信号
    playback_requested = pyqtSignal(float)  # 播放请求信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.segments = []
        self.current_segment = None

        self.setup_ui()
        self.setup_connections()

        logger.info("时间段管理器初始化完成")

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 创建标签页
        self.tab_widget = QTabWidget()

        # 可视化时间轴标签页
        timeline_tab = self.create_timeline_tab()
        self.tab_widget.addTab(timeline_tab, "时间轴")

        # 段列表标签页
        segments_tab = self.create_segments_tab()
        self.tab_widget.addTab(segments_tab, "段列表")

        # 段属性标签页
        properties_tab = self.create_properties_tab()
        self.tab_widget.addTab(properties_tab, "属性")

        layout.addWidget(self.tab_widget)

    def create_timeline_tab(self):
        """创建时间轴标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 时间轴控制工具栏
        toolbar = QHBoxLayout()

        # 播放控制
        self.play_btn = QPushButton("▶️")
        self.play_btn.setMaximumWidth(40)
        self.play_btn.setToolTip("播放")
        toolbar.addWidget(self.play_btn)

        self.pause_btn = QPushButton("⏸️")
        self.pause_btn.setMaximumWidth(40)
        self.pause_btn.setToolTip("暂停")
        toolbar.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("⏹️")
        self.stop_btn.setMaximumWidth(40)
        self.stop_btn.setToolTip("停止")
        toolbar.addWidget(self.stop_btn)

        toolbar.addWidget(QFrame())  # 分隔符

        # 时间显示
        toolbar.addWidget(QLabel("时间:"))
        self.time_display = QLabel("00:00.0")
        self.time_display.setMinimumWidth(60)
        self.time_display.setStyleSheet("font-family: monospace; font-weight: bold;")
        toolbar.addWidget(self.time_display)

        toolbar.addWidget(QFrame())  # 分隔符

        # 缩放控制
        toolbar.addWidget(QLabel("缩放:"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 200)  # 10-200 像素/秒
        self.zoom_slider.setValue(50)
        self.zoom_slider.setMaximumWidth(100)
        toolbar.addWidget(self.zoom_slider)

        self.zoom_label = QLabel("50px/s")
        toolbar.addWidget(self.zoom_label)

        toolbar.addStretch()

        # 添加段按钮
        add_segment_btn = QPushButton("➕ 添加段")
        add_segment_btn.clicked.connect(self.show_add_segment_dialog)
        toolbar.addWidget(add_segment_btn)

        layout.addLayout(toolbar)

        # 可视化时间轴
        self.visual_timeline = VisualTimelineWidget()
        self.visual_timeline.segment_selected.connect(self.on_segment_selected)
        self.visual_timeline.segment_moved.connect(self.on_segment_moved)
        self.visual_timeline.segment_resized.connect(self.on_segment_resized)
        self.visual_timeline.time_clicked.connect(self.on_time_clicked)
        self.visual_timeline.segment_double_clicked.connect(self.on_segment_double_clicked)

        layout.addWidget(self.visual_timeline)

        return tab

    def create_segments_tab(self):
        """创建段列表标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 段列表工具栏
        toolbar = QHBoxLayout()

        # 搜索框
        toolbar.addWidget(QLabel("搜索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索段名称...")
        self.search_edit.textChanged.connect(self.filter_segments)
        toolbar.addWidget(self.search_edit)

        # 排序选项
        toolbar.addWidget(QLabel("排序:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["时间", "名称", "类型", "时长"])
        self.sort_combo.currentTextChanged.connect(self.sort_segments)
        toolbar.addWidget(self.sort_combo)

        # 筛选选项
        toolbar.addWidget(QLabel("筛选:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部", "动画", "暂停", "过渡", "标记"])
        self.filter_combo.currentTextChanged.connect(self.filter_segments)
        toolbar.addWidget(self.filter_combo)

        toolbar.addStretch()

        layout.addLayout(toolbar)

        # 段列表
        self.segments_tree = QTreeWidget()
        self.segments_tree.setHeaderLabels(["名称", "类型", "开始时间", "结束时间", "时长", "状态"])
        self.segments_tree.setRootIsDecorated(False)
        self.segments_tree.setAlternatingRowColors(True)
        self.segments_tree.itemSelectionChanged.connect(self.on_tree_selection_changed)
        self.segments_tree.itemDoubleClicked.connect(self.on_tree_item_double_clicked)

        # 设置列宽
        header = self.segments_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.segments_tree)

        # 段操作按钮
        buttons_layout = QHBoxLayout()

        edit_btn = QPushButton("编辑")
        edit_btn.clicked.connect(self.edit_selected_segment)
        buttons_layout.addWidget(edit_btn)

        duplicate_btn = QPushButton("复制")
        duplicate_btn.clicked.connect(self.duplicate_selected_segment)
        buttons_layout.addWidget(duplicate_btn)

        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_selected_segment)
        buttons_layout.addWidget(delete_btn)

        buttons_layout.addStretch()

        # 批量操作
        batch_btn = QPushButton("批量操作")
        batch_btn.clicked.connect(self.show_batch_operations)
        buttons_layout.addWidget(batch_btn)

        layout.addLayout(buttons_layout)

        return tab

    def create_properties_tab(self):
        """创建属性标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 段信息显示
        info_group = QGroupBox("段信息")
        info_layout = QFormLayout(info_group)

        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self.on_property_changed)
        info_layout.addRow("名称:", self.name_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["animation", "pause", "transition", "marker", "audio", "video"])
        self.type_combo.currentTextChanged.connect(self.on_property_changed)
        info_layout.addRow("类型:", self.type_combo)

        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.textChanged.connect(self.on_property_changed)
        info_layout.addRow("描述:", self.description_edit)

        layout.addWidget(info_group)

        # 时间设置
        time_group = QGroupBox("时间设置")
        time_layout = QFormLayout(time_group)

        self.start_time_spin = QDoubleSpinBox()
        self.start_time_spin.setRange(0, 3600)
        self.start_time_spin.setDecimals(1)
        self.start_time_spin.setSuffix("s")
        self.start_time_spin.valueChanged.connect(self.on_time_changed)
        time_layout.addRow("开始时间:", self.start_time_spin)

        self.end_time_spin = QDoubleSpinBox()
        self.end_time_spin.setRange(0, 3600)
        self.end_time_spin.setDecimals(1)
        self.end_time_spin.setSuffix("s")
        self.end_time_spin.valueChanged.connect(self.on_time_changed)
        time_layout.addRow("结束时间:", self.end_time_spin)

        self.duration_label = QLabel("0.0s")
        time_layout.addRow("时长:", self.duration_label)

        layout.addWidget(time_group)

        # 外观设置
        appearance_group = QGroupBox("外观设置")
        appearance_layout = QFormLayout(appearance_group)

        # 颜色选择
        color_layout = QHBoxLayout()
        self.color_btn = QPushButton()
        self.color_btn.setMaximumWidth(50)
        self.color_btn.setMaximumHeight(30)
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_btn)

        self.color_preset_combo = QComboBox()
        self.color_preset_combo.addItems(["自定义", "蓝色", "绿色", "橙色", "红色", "紫色", "青色"])
        self.color_preset_combo.currentTextChanged.connect(self.on_color_preset_changed)
        color_layout.addWidget(self.color_preset_combo)

        appearance_layout.addRow("颜色:", color_layout)

        # 可见性和锁定
        visibility_layout = QHBoxLayout()

        self.visible_cb = QCheckBox("可见")
        self.visible_cb.setChecked(True)
        self.visible_cb.toggled.connect(self.on_property_changed)
        visibility_layout.addWidget(self.visible_cb)

        self.locked_cb = QCheckBox("锁定")
        self.locked_cb.toggled.connect(self.on_property_changed)
        visibility_layout.addWidget(self.locked_cb)

        visibility_layout.addStretch()

        appearance_layout.addRow("状态:", visibility_layout)

        layout.addWidget(appearance_group)

        # 动画设置（仅动画段）
        self.animation_group = QGroupBox("动画设置")
        animation_layout = QFormLayout(self.animation_group)

        self.animation_type_combo = QComboBox()
        self.animation_type_combo.addItems([
            "淡入", "淡出", "滑入", "滑出", "缩放", "旋转", "弹跳", "自定义"
        ])
        self.animation_type_combo.currentTextChanged.connect(self.on_property_changed)
        animation_layout.addRow("动画类型:", self.animation_type_combo)

        self.easing_combo = QComboBox()
        self.easing_combo.addItems([
            "线性", "缓入", "缓出", "缓入缓出", "弹性", "回弹"
        ])
        animation_layout.addRow("缓动函数:", self.easing_combo)

        layout.addWidget(self.animation_group)

        layout.addStretch()

        # 应用按钮
        apply_btn = QPushButton("应用更改")
        apply_btn.clicked.connect(self.apply_changes)
        layout.addWidget(apply_btn)

        return tab

    def setup_connections(self):
        """设置信号连接"""
        # 缩放控制
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)

        # 播放控制
        self.play_btn.clicked.connect(self.play_timeline)
        self.pause_btn.clicked.connect(self.pause_timeline)
        self.stop_btn.clicked.connect(self.stop_timeline)

    def on_zoom_changed(self, value: int):
        """缩放改变事件"""
        self.visual_timeline.set_zoom_level(value)
        self.zoom_label.setText(f"{value}px/s")

    def on_segment_selected(self, segment_id: int):
        """段选择事件"""
        segment = self.visual_timeline.get_segment_by_id(segment_id)
        if segment:
            self.current_segment = segment
            self.load_segment_properties(segment)

    def on_segment_moved(self, segment_id: int, start_time: float, end_time: float):
        """段移动事件"""
        self.segment_updated.emit(segment_id, {
            'start_time': start_time,
            'end_time': end_time
        })
        self.update_segments_tree()

    def on_segment_resized(self, segment_id: int, start_time: float, end_time: float):
        """段大小调整事件"""
        self.segment_updated.emit(segment_id, {
            'start_time': start_time,
            'end_time': end_time
        })
        self.update_segments_tree()

    def on_time_clicked(self, time: float):
        """时间点击事件"""
        self.visual_timeline.set_current_time(time)
        self.time_display.setText(f"{time:.1f}s")

    def on_segment_double_clicked(self, segment_id: int):
        """段双击事件"""
        segment = self.visual_timeline.get_segment_by_id(segment_id)
        if segment:
            self.edit_segment(segment)

    def show_add_segment_dialog(self):
        """显示添加段对话框"""
        # 简化实现
        current_time = self.visual_timeline.current_time
        segment = TimelineSegment(current_time, current_time + 2.0, "新段", "animation")
        self.visual_timeline.add_segment(segment)
        self.update_segments_tree()

    def load_segment_properties(self, segment: TimelineSegment):
        """加载段属性到属性面板"""
        try:
            self.name_edit.setText(segment.name)
            self.type_combo.setCurrentText(segment.segment_type)
            self.description_edit.setPlainText(segment.description)

            self.start_time_spin.setValue(segment.start_time)
            self.end_time_spin.setValue(segment.end_time)
            self.duration_label.setText(f"{segment.duration:.1f}s")

            # 设置颜色按钮
            self.color_btn.setStyleSheet(f"background-color: {segment.color.name()};")

            self.visible_cb.setChecked(segment.visible)
            self.locked_cb.setChecked(segment.locked)

            # 显示/隐藏动画设置
            self.animation_group.setVisible(segment.segment_type == "animation")

        except Exception as e:
            logger.error(f"加载段属性失败: {e}")

    def update_segments_tree(self):
        """更新段列表树"""
        self.segments_tree.clear()

        for segment in self.visual_timeline.segments:
            item = QTreeWidgetItem([
                segment.name,
                segment.segment_type,
                f"{segment.start_time:.1f}s",
                f"{segment.end_time:.1f}s",
                f"{segment.duration:.1f}s",
                "锁定" if segment.locked else ("隐藏" if not segment.visible else "正常")
            ])

            # 设置颜色
            item.setBackground(0, QBrush(segment.color.lighter(180)))
            item.setData(0, Qt.ItemDataRole.UserRole, segment.id)

            self.segments_tree.addTopLevelItem(item)

    def on_property_changed(self):
        """属性改变事件"""
        if self.current_segment:
            # 实时更新段属性
            self.apply_changes()

    def on_time_changed(self):
        """时间改变事件"""
        if self.current_segment:
            start_time = self.start_time_spin.value()
            end_time = self.end_time_spin.value()

            if end_time > start_time:
                self.current_segment.start_time = start_time
                self.current_segment.end_time = end_time
                self.duration_label.setText(f"{end_time - start_time:.1f}s")
                self.visual_timeline.update()

    def choose_color(self):
        """选择颜色"""
        if self.current_segment:
            color = QColorDialog.getColor(self.current_segment.color, self)
            if color.isValid():
                self.current_segment.color = color
                self.color_btn.setStyleSheet(f"background-color: {color.name()};")
                self.visual_timeline.update()

    def on_color_preset_changed(self, preset_name: str):
        """颜色预设改变"""
        if preset_name != "自定义" and self.current_segment:
            color_map = {
                "蓝色": QColor("#2196F3"),
                "绿色": QColor("#4CAF50"),
                "橙色": QColor("#FF9800"),
                "红色": QColor("#F44336"),
                "紫色": QColor("#9C27B0"),
                "青色": QColor("#00BCD4")
            }

            if preset_name in color_map:
                color = color_map[preset_name]
                self.current_segment.color = color
                self.color_btn.setStyleSheet(f"background-color: {color.name()};")
                self.visual_timeline.update()

    def apply_changes(self):
        """应用更改"""
        if self.current_segment:
            self.current_segment.name = self.name_edit.text()
            self.current_segment.segment_type = self.type_combo.currentText()
            self.current_segment.description = self.description_edit.toPlainText()
            self.current_segment.visible = self.visible_cb.isChecked()
            self.current_segment.locked = self.locked_cb.isChecked()

            self.visual_timeline.update()
            self.update_segments_tree()

    def play_timeline(self):
        """播放时间轴"""
        current_time = self.visual_timeline.current_time
        self.playback_requested.emit(current_time)

    def pause_timeline(self):
        """暂停时间轴"""
        pass

    def stop_timeline(self):
        """停止时间轴"""
        self.visual_timeline.set_current_time(0)
        self.time_display.setText("00:00.0")

    def filter_segments(self):
        """筛选段"""
        # TODO: 实现段筛选功能
        pass

    def sort_segments(self):
        """排序段"""
        # TODO: 实现段排序功能
        pass

    def edit_selected_segment(self):
        """编辑选中的段"""
        # TODO: 实现段编辑功能
        pass

    def duplicate_selected_segment(self):
        """复制选中的段"""
        # TODO: 实现段复制功能
        pass

    def delete_selected_segment(self):
        """删除选中的段"""
        # TODO: 实现段删除功能
        pass

    def show_batch_operations(self):
        """显示批量操作"""
        # TODO: 实现批量操作功能
        pass

    def on_tree_selection_changed(self):
        """树选择改变事件"""
        # TODO: 实现树选择同步
        pass

    def on_tree_item_double_clicked(self, item, column):
        """树项双击事件"""
        # TODO: 实现树项双击编辑
        pass

    def edit_segment(self, segment: TimelineSegment):
        """编辑段"""
        # TODO: 实现段编辑对话框
        pass
