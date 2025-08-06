"""
AI Animation Studio - 直接操纵界面系统
实现舞台上的直接拖拽、缩放、旋转、就地编辑等操作
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGroupBox, QPushButton, QProgressBar,
                             QScrollArea, QSplitter, QStackedWidget, QSlider,
                             QSpinBox, QDoubleSpinBox, QColorDialog, QMenu,
                             QLineEdit, QTextEdit, QComboBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint, QPointF, QRectF
from PyQt6.QtGui import (QFont, QColor, QPalette, QPixmap, QPainter, QPen, QBrush,
                         QCursor, QMouseEvent, QWheelEvent, QKeyEvent, QAction)

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import json
import math

from core.logger import get_logger

logger = get_logger("direct_manipulation_interface")


class ManipulationMode(Enum):
    """操作模式枚举"""
    SELECT = "select"           # 选择模式
    MOVE = "move"              # 移动模式
    RESIZE = "resize"          # 缩放模式
    ROTATE = "rotate"          # 旋转模式
    EDIT_TEXT = "edit_text"    # 文本编辑模式
    DRAW_PATH = "draw_path"    # 路径绘制模式


class HandleType(Enum):
    """手柄类型枚举"""
    TOP_LEFT = "top_left"           # 左上角
    TOP_CENTER = "top_center"       # 上中
    TOP_RIGHT = "top_right"         # 右上角
    MIDDLE_LEFT = "middle_left"     # 左中
    MIDDLE_RIGHT = "middle_right"   # 右中
    BOTTOM_LEFT = "bottom_left"     # 左下角
    BOTTOM_CENTER = "bottom_center" # 下中
    BOTTOM_RIGHT = "bottom_right"   # 右下角
    ROTATE = "rotate"               # 旋转手柄


class SelectionHandle(QWidget):
    """选择手柄组件"""
    
    handle_dragged = pyqtSignal(str, QPointF)  # 手柄拖拽信号
    
    def __init__(self, handle_type: HandleType, size: int = 8):
        super().__init__()
        self.handle_type = handle_type
        self.size = size
        self.is_dragging = False
        self.drag_start_pos = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setFixedSize(self.size, self.size)
        self.setCursor(self.get_cursor_for_handle())
        
        # 设置样式
        style = f"""
        SelectionHandle {{
            background-color: #2C5AA0;
            border: 1px solid white;
            border-radius: {self.size // 2}px;
        }}
        SelectionHandle:hover {{
            background-color: #1976D2;
            border: 2px solid white;
        }}
        """
        self.setStyleSheet(style)
    
    def get_cursor_for_handle(self) -> Qt.CursorShape:
        """获取手柄对应的光标"""
        cursor_map = {
            HandleType.TOP_LEFT: Qt.CursorShape.SizeFDiagCursor,
            HandleType.TOP_CENTER: Qt.CursorShape.SizeVerCursor,
            HandleType.TOP_RIGHT: Qt.CursorShape.SizeBDiagCursor,
            HandleType.MIDDLE_LEFT: Qt.CursorShape.SizeHorCursor,
            HandleType.MIDDLE_RIGHT: Qt.CursorShape.SizeHorCursor,
            HandleType.BOTTOM_LEFT: Qt.CursorShape.SizeBDiagCursor,
            HandleType.BOTTOM_CENTER: Qt.CursorShape.SizeVerCursor,
            HandleType.BOTTOM_RIGHT: Qt.CursorShape.SizeFDiagCursor,
            HandleType.ROTATE: Qt.CursorShape.CrossCursor
        }
        return cursor_map.get(self.handle_type, Qt.CursorShape.ArrowCursor)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_start_pos = event.globalPosition()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        if self.is_dragging and self.drag_start_pos:
            delta = event.globalPosition() - self.drag_start_pos
            self.handle_dragged.emit(self.handle_type.value, delta)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        self.is_dragging = False
        self.drag_start_pos = None


class SelectionBox(QWidget):
    """选择框组件"""
    
    element_moved = pyqtSignal(str, QPointF)      # 元素移动信号
    element_resized = pyqtSignal(str, QRectF)     # 元素缩放信号
    element_rotated = pyqtSignal(str, float)      # 元素旋转信号
    
    def __init__(self, element_id: str, bounds: QRectF):
        super().__init__()
        self.element_id = element_id
        self.bounds = bounds
        self.handles: Dict[HandleType, SelectionHandle] = {}
        self.rotation_angle = 0.0
        
        self.setup_ui()
        self.setup_handles()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setGeometry(self.bounds.toRect())
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        
        # 设置选择框样式
        self.setStyleSheet("""
            SelectionBox {
                border: 2px dashed #2C5AA0;
                background-color: transparent;
            }
        """)
    
    def setup_handles(self):
        """设置选择手柄"""
        handle_types = [
            HandleType.TOP_LEFT, HandleType.TOP_CENTER, HandleType.TOP_RIGHT,
            HandleType.MIDDLE_LEFT, HandleType.MIDDLE_RIGHT,
            HandleType.BOTTOM_LEFT, HandleType.BOTTOM_CENTER, HandleType.BOTTOM_RIGHT,
            HandleType.ROTATE
        ]
        
        for handle_type in handle_types:
            handle = SelectionHandle(handle_type)
            handle.handle_dragged.connect(self.on_handle_dragged)
            handle.setParent(self)
            self.handles[handle_type] = handle
        
        self.update_handle_positions()
    
    def update_handle_positions(self):
        """更新手柄位置"""
        w, h = self.bounds.width(), self.bounds.height()
        handle_size = 8
        offset = handle_size // 2
        
        positions = {
            HandleType.TOP_LEFT: (-offset, -offset),
            HandleType.TOP_CENTER: (w//2 - offset, -offset),
            HandleType.TOP_RIGHT: (w - offset, -offset),
            HandleType.MIDDLE_LEFT: (-offset, h//2 - offset),
            HandleType.MIDDLE_RIGHT: (w - offset, h//2 - offset),
            HandleType.BOTTOM_LEFT: (-offset, h - offset),
            HandleType.BOTTOM_CENTER: (w//2 - offset, h - offset),
            HandleType.BOTTOM_RIGHT: (w - offset, h - offset),
            HandleType.ROTATE: (w//2 - offset, -30)  # 旋转手柄在上方
        }
        
        for handle_type, (x, y) in positions.items():
            if handle_type in self.handles:
                self.handles[handle_type].move(x, y)
    
    def on_handle_dragged(self, handle_type: str, delta: QPointF):
        """手柄拖拽处理"""
        handle_enum = HandleType(handle_type)
        
        if handle_enum == HandleType.ROTATE:
            # 旋转处理
            angle = self.calculate_rotation_angle(delta)
            self.rotation_angle += angle
            self.element_rotated.emit(self.element_id, self.rotation_angle)
        else:
            # 缩放处理
            new_bounds = self.calculate_new_bounds(handle_enum, delta)
            self.bounds = new_bounds
            self.setGeometry(new_bounds.toRect())
            self.update_handle_positions()
            self.element_resized.emit(self.element_id, new_bounds)
    
    def calculate_rotation_angle(self, delta: QPointF) -> float:
        """计算旋转角度"""
        # 简化的旋转角度计算
        return delta.x() * 0.5  # 每像素0.5度
    
    def calculate_new_bounds(self, handle_type: HandleType, delta: QPointF) -> QRectF:
        """计算新的边界"""
        new_bounds = QRectF(self.bounds)
        
        if handle_type == HandleType.TOP_LEFT:
            new_bounds.setTopLeft(new_bounds.topLeft() + delta)
        elif handle_type == HandleType.TOP_CENTER:
            new_bounds.setTop(new_bounds.top() + delta.y())
        elif handle_type == HandleType.TOP_RIGHT:
            new_bounds.setTopRight(new_bounds.topRight() + delta)
        elif handle_type == HandleType.MIDDLE_LEFT:
            new_bounds.setLeft(new_bounds.left() + delta.x())
        elif handle_type == HandleType.MIDDLE_RIGHT:
            new_bounds.setRight(new_bounds.right() + delta.x())
        elif handle_type == HandleType.BOTTOM_LEFT:
            new_bounds.setBottomLeft(new_bounds.bottomLeft() + delta)
        elif handle_type == HandleType.BOTTOM_CENTER:
            new_bounds.setBottom(new_bounds.bottom() + delta.y())
        elif handle_type == HandleType.BOTTOM_RIGHT:
            new_bounds.setBottomRight(new_bounds.bottomRight() + delta)
        
        # 确保最小尺寸
        min_size = 20
        if new_bounds.width() < min_size:
            new_bounds.setWidth(min_size)
        if new_bounds.height() < min_size:
            new_bounds.setHeight(min_size)
        
        return new_bounds


class InPlaceTextEditor(QTextEdit):
    """就地文本编辑器"""
    
    editing_finished = pyqtSignal(str, str)  # 编辑完成信号
    editing_cancelled = pyqtSignal(str)      # 编辑取消信号
    
    def __init__(self, element_id: str, initial_text: str, bounds: QRectF):
        super().__init__()
        self.element_id = element_id
        self.initial_text = initial_text
        self.bounds = bounds
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setGeometry(self.bounds.toRect())
        self.setPlainText(self.initial_text)
        self.selectAll()
        
        # 设置样式
        self.setStyleSheet("""
            QTextEdit {
                border: 2px solid #2C5AA0;
                border-radius: 4px;
                background-color: white;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
                padding: 4px;
            }
        """)
        
        # 设置焦点
        self.setFocus()
    
    def keyPressEvent(self, event: QKeyEvent):
        """键盘事件处理"""
        if event.key() == Qt.Key.Key_Escape:
            # ESC键取消编辑
            self.editing_cancelled.emit(self.element_id)
            self.hide()
        elif event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Ctrl+Enter完成编辑
            self.finish_editing()
        else:
            super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        """失去焦点事件"""
        super().focusOutEvent(event)
        self.finish_editing()
    
    def finish_editing(self):
        """完成编辑"""
        new_text = self.toPlainText()
        self.editing_finished.emit(self.element_id, new_text)
        self.hide()


class ContextMenu(QMenu):
    """上下文菜单"""
    
    action_triggered = pyqtSignal(str, str)  # 动作触发信号
    
    def __init__(self, element_id: str, element_type: str):
        super().__init__()
        self.element_id = element_id
        self.element_type = element_type
        
        self.setup_menu()
    
    def setup_menu(self):
        """设置菜单"""
        # 通用操作
        copy_action = QAction("📋 复制", self)
        copy_action.triggered.connect(lambda: self.action_triggered.emit(self.element_id, "copy"))
        self.addAction(copy_action)
        
        cut_action = QAction("✂️ 剪切", self)
        cut_action.triggered.connect(lambda: self.action_triggered.emit(self.element_id, "cut"))
        self.addAction(cut_action)
        
        delete_action = QAction("🗑️ 删除", self)
        delete_action.triggered.connect(lambda: self.action_triggered.emit(self.element_id, "delete"))
        self.addAction(delete_action)
        
        self.addSeparator()
        
        # 层级操作
        bring_front_action = QAction("⬆️ 置于顶层", self)
        bring_front_action.triggered.connect(lambda: self.action_triggered.emit(self.element_id, "bring_to_front"))
        self.addAction(bring_front_action)
        
        send_back_action = QAction("⬇️ 置于底层", self)
        send_back_action.triggered.connect(lambda: self.action_triggered.emit(self.element_id, "send_to_back"))
        self.addAction(send_back_action)
        
        self.addSeparator()
        
        # 特定类型操作
        if self.element_type == "text":
            edit_text_action = QAction("✏️ 编辑文本", self)
            edit_text_action.triggered.connect(lambda: self.action_triggered.emit(self.element_id, "edit_text"))
            self.addAction(edit_text_action)
        
        # 属性操作
        properties_action = QAction("⚙️ 属性", self)
        properties_action.triggered.connect(lambda: self.action_triggered.emit(self.element_id, "properties"))
        self.addAction(properties_action)


class DirectManipulationInterface(QWidget):
    """直接操纵界面主类"""
    
    element_selected = pyqtSignal(str)              # 元素选择信号
    element_moved = pyqtSignal(str, QPointF)        # 元素移动信号
    element_resized = pyqtSignal(str, QRectF)       # 元素缩放信号
    element_rotated = pyqtSignal(str, float)        # 元素旋转信号
    element_text_edited = pyqtSignal(str, str)      # 文本编辑信号
    element_action = pyqtSignal(str, str)           # 元素动作信号
    
    def __init__(self, stage_canvas):
        super().__init__()
        self.stage_canvas = stage_canvas
        self.current_mode = ManipulationMode.SELECT
        self.selected_element = None
        self.selection_box = None
        self.text_editor = None
        self.is_dragging = False
        self.drag_start_pos = None
        self.drag_start_element_pos = None
        
        self.setup_ui()
        self.setup_connections()
        
        logger.info("直接操纵界面初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        # 设置为透明背景，覆盖在舞台画布上
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background-color: transparent;")
    
    def setup_connections(self):
        """设置信号连接"""
        if self.stage_canvas:
            # 连接舞台画布的鼠标事件
            self.stage_canvas.mousePressEvent = self.on_canvas_mouse_press
            self.stage_canvas.mouseMoveEvent = self.on_canvas_mouse_move
            self.stage_canvas.mouseReleaseEvent = self.on_canvas_mouse_release
            self.stage_canvas.mouseDoubleClickEvent = self.on_canvas_double_click
            self.stage_canvas.contextMenuEvent = self.on_canvas_context_menu
    
    def set_manipulation_mode(self, mode: ManipulationMode):
        """设置操作模式"""
        self.current_mode = mode
        self.update_cursor()
    
    def update_cursor(self):
        """更新光标"""
        cursor_map = {
            ManipulationMode.SELECT: Qt.CursorShape.ArrowCursor,
            ManipulationMode.MOVE: Qt.CursorShape.SizeAllCursor,
            ManipulationMode.RESIZE: Qt.CursorShape.SizeFDiagCursor,
            ManipulationMode.ROTATE: Qt.CursorShape.CrossCursor,
            ManipulationMode.EDIT_TEXT: Qt.CursorShape.IBeamCursor,
            ManipulationMode.DRAW_PATH: Qt.CursorShape.CrossCursor
        }
        
        cursor = cursor_map.get(self.current_mode, Qt.CursorShape.ArrowCursor)
        self.stage_canvas.setCursor(cursor)
    
    def on_canvas_mouse_press(self, event: QMouseEvent):
        """画布鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            element_id = self.find_element_at_position(pos)
            
            if element_id:
                self.select_element(element_id)
                
                if self.current_mode == ManipulationMode.MOVE:
                    self.start_drag_operation(pos, element_id)
            else:
                self.clear_selection()
    
    def on_canvas_mouse_move(self, event: QMouseEvent):
        """画布鼠标移动事件"""
        if self.is_dragging and self.selected_element:
            pos = event.position()
            delta = pos - self.drag_start_pos
            
            # 发送移动信号
            self.element_moved.emit(self.selected_element, delta)
    
    def on_canvas_mouse_release(self, event: QMouseEvent):
        """画布鼠标释放事件"""
        self.is_dragging = False
        self.drag_start_pos = None
        self.drag_start_element_pos = None
    
    def on_canvas_double_click(self, event: QMouseEvent):
        """画布双击事件"""
        pos = event.position()
        element_id = self.find_element_at_position(pos)
        
        if element_id:
            element_type = self.get_element_type(element_id)
            if element_type == "text":
                self.start_text_editing(element_id)
    
    def on_canvas_context_menu(self, event):
        """画布右键菜单事件"""
        pos = event.pos()
        element_id = self.find_element_at_position(pos)
        
        if element_id:
            element_type = self.get_element_type(element_id)
            menu = ContextMenu(element_id, element_type)
            menu.action_triggered.connect(self.on_context_action)
            menu.exec(event.globalPos())
    
    def select_element(self, element_id: str):
        """选择元素"""
        self.clear_selection()
        
        self.selected_element = element_id
        bounds = self.get_element_bounds(element_id)
        
        if bounds:
            self.selection_box = SelectionBox(element_id, bounds)
            self.selection_box.element_moved.connect(self.element_moved.emit)
            self.selection_box.element_resized.connect(self.element_resized.emit)
            self.selection_box.element_rotated.connect(self.element_rotated.emit)
            self.selection_box.setParent(self)
            self.selection_box.show()
        
        self.element_selected.emit(element_id)
    
    def clear_selection(self):
        """清除选择"""
        self.selected_element = None
        
        if self.selection_box:
            self.selection_box.hide()
            self.selection_box.deleteLater()
            self.selection_box = None
        
        if self.text_editor:
            self.text_editor.hide()
            self.text_editor.deleteLater()
            self.text_editor = None
    
    def start_drag_operation(self, pos: QPointF, element_id: str):
        """开始拖拽操作"""
        self.is_dragging = True
        self.drag_start_pos = pos
        self.drag_start_element_pos = self.get_element_position(element_id)
    
    def start_text_editing(self, element_id: str):
        """开始文本编辑"""
        bounds = self.get_element_bounds(element_id)
        text = self.get_element_text(element_id)
        
        if bounds and text is not None:
            self.text_editor = InPlaceTextEditor(element_id, text, bounds)
            self.text_editor.editing_finished.connect(self.on_text_editing_finished)
            self.text_editor.editing_cancelled.connect(self.on_text_editing_cancelled)
            self.text_editor.setParent(self)
            self.text_editor.show()
    
    def on_text_editing_finished(self, element_id: str, new_text: str):
        """文本编辑完成"""
        self.element_text_edited.emit(element_id, new_text)
        self.clear_text_editor()
    
    def on_text_editing_cancelled(self, element_id: str):
        """文本编辑取消"""
        self.clear_text_editor()
    
    def clear_text_editor(self):
        """清除文本编辑器"""
        if self.text_editor:
            self.text_editor.hide()
            self.text_editor.deleteLater()
            self.text_editor = None
    
    def on_context_action(self, element_id: str, action: str):
        """上下文动作处理"""
        self.element_action.emit(element_id, action)
    
    def find_element_at_position(self, pos: QPointF) -> Optional[str]:
        """查找指定位置的元素"""
        # 这里需要与舞台画布的元素查找逻辑集成
        if hasattr(self.stage_canvas, 'find_element_at_position'):
            return self.stage_canvas.find_element_at_position(pos.x(), pos.y())
        return None
    
    def get_element_bounds(self, element_id: str) -> Optional[QRectF]:
        """获取元素边界"""
        # 这里需要与舞台画布的元素边界获取逻辑集成
        if hasattr(self.stage_canvas, 'get_element_bounds_safely'):
            bounds = self.stage_canvas.get_element_bounds_safely(
                self.stage_canvas.elements.get(element_id)
            )
            if bounds:
                return QRectF(bounds['x'], bounds['y'], bounds['width'], bounds['height'])
        return None
    
    def get_element_position(self, element_id: str) -> Optional[QPointF]:
        """获取元素位置"""
        bounds = self.get_element_bounds(element_id)
        return bounds.topLeft() if bounds else None
    
    def get_element_type(self, element_id: str) -> str:
        """获取元素类型"""
        if hasattr(self.stage_canvas, 'elements') and element_id in self.stage_canvas.elements:
            element = self.stage_canvas.elements[element_id]
            if hasattr(element, 'element_type'):
                return getattr(element.element_type, 'value', str(element.element_type))
        return "unknown"
    
    def get_element_text(self, element_id: str) -> Optional[str]:
        """获取元素文本"""
        if hasattr(self.stage_canvas, 'elements') and element_id in self.stage_canvas.elements:
            element = self.stage_canvas.elements[element_id]
            return getattr(element, 'content', getattr(element, 'name', ''))
        return None


class DragDropSystem(QWidget):
    """拖拽系统"""

    element_dropped = pyqtSignal(str, QPointF)      # 元素拖拽到舞台信号
    element_reordered = pyqtSignal(str, int)        # 元素重新排序信号
    asset_dropped = pyqtSignal(str, QPointF)        # 素材拖拽到舞台信号

    def __init__(self):
        super().__init__()
        self.drag_data = None
        self.drag_preview = None
        self.drop_zones = []

        self.setup_drag_drop()
        logger.info("拖拽系统初始化完成")

    def setup_drag_drop(self):
        """设置拖拽功能"""
        self.setAcceptDrops(True)

    def start_element_drag(self, element_id: str, element_type: str, preview_pixmap: QPixmap):
        """开始元素拖拽"""
        self.drag_data = {
            'type': 'element',
            'element_id': element_id,
            'element_type': element_type
        }

        # 创建拖拽预览
        self.create_drag_preview(preview_pixmap)

    def start_asset_drag(self, asset_id: str, asset_type: str, preview_pixmap: QPixmap):
        """开始素材拖拽"""
        self.drag_data = {
            'type': 'asset',
            'asset_id': asset_id,
            'asset_type': asset_type
        }

        # 创建拖拽预览
        self.create_drag_preview(preview_pixmap)

    def create_drag_preview(self, pixmap: QPixmap):
        """创建拖拽预览"""
        # 创建半透明的预览图
        preview = QPixmap(pixmap.size())
        preview.fill(Qt.GlobalColor.transparent)

        painter = QPainter(preview)
        painter.setOpacity(0.7)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        self.drag_preview = preview

    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if self.drag_data:
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        if self.drag_data:
            event.acceptProposedAction()

            # 更新拖拽预览位置
            self.update_drag_preview(event.position())

    def dropEvent(self, event):
        """拖拽放下事件"""
        if self.drag_data:
            pos = event.position()

            if self.drag_data['type'] == 'element':
                self.element_dropped.emit(self.drag_data['element_id'], pos)
            elif self.drag_data['type'] == 'asset':
                self.asset_dropped.emit(self.drag_data['asset_id'], pos)

            event.acceptProposedAction()
            self.clear_drag_data()

    def update_drag_preview(self, pos: QPointF):
        """更新拖拽预览"""
        # 这里可以添加拖拽预览的视觉反馈
        pass

    def clear_drag_data(self):
        """清除拖拽数据"""
        self.drag_data = None
        self.drag_preview = None

    def add_drop_zone(self, widget: QWidget, zone_type: str):
        """添加拖拽放置区域"""
        self.drop_zones.append({
            'widget': widget,
            'type': zone_type
        })

        # 为组件启用拖拽接受
        widget.setAcceptDrops(True)


class SmartSnapSystem:
    """智能对齐系统"""

    def __init__(self, stage_canvas):
        self.stage_canvas = stage_canvas
        self.snap_enabled = True
        self.snap_threshold = 10  # 对齐阈值（像素）
        self.grid_snap = True
        self.element_snap = True
        self.guide_snap = True

        # 对齐线
        self.snap_lines = []

        logger.info("智能对齐系统初始化完成")

    def calculate_snap_position(self, element_id: str, target_pos: QPointF) -> QPointF:
        """计算对齐位置"""
        if not self.snap_enabled:
            return target_pos

        snapped_pos = QPointF(target_pos)

        # 网格对齐
        if self.grid_snap:
            snapped_pos = self.snap_to_grid(snapped_pos)

        # 元素对齐
        if self.element_snap:
            snapped_pos = self.snap_to_elements(element_id, snapped_pos)

        # 参考线对齐
        if self.guide_snap:
            snapped_pos = self.snap_to_guides(snapped_pos)

        return snapped_pos

    def snap_to_grid(self, pos: QPointF) -> QPointF:
        """网格对齐"""
        if not hasattr(self.stage_canvas, 'grid_size'):
            return pos

        grid_size = self.stage_canvas.grid_size

        x = round(pos.x() / grid_size) * grid_size
        y = round(pos.y() / grid_size) * grid_size

        return QPointF(x, y)

    def snap_to_elements(self, element_id: str, pos: QPointF) -> QPointF:
        """元素对齐"""
        if not hasattr(self.stage_canvas, 'elements'):
            return pos

        snapped_pos = QPointF(pos)
        min_distance = self.snap_threshold

        for other_id, other_element in self.stage_canvas.elements.items():
            if other_id == element_id:
                continue

            other_bounds = self.stage_canvas.get_element_bounds_safely(other_element)
            if not other_bounds:
                continue

            # 检查水平对齐
            h_distance = abs(pos.x() - other_bounds['x'])
            if h_distance < min_distance:
                snapped_pos.setX(other_bounds['x'])
                min_distance = h_distance

            # 检查垂直对齐
            v_distance = abs(pos.y() - other_bounds['y'])
            if v_distance < min_distance:
                snapped_pos.setY(other_bounds['y'])

        return snapped_pos

    def snap_to_guides(self, pos: QPointF) -> QPointF:
        """参考线对齐"""
        # 这里可以添加参考线对齐逻辑
        return pos

    def show_snap_lines(self, pos: QPointF):
        """显示对齐线"""
        # 这里可以添加对齐线的显示逻辑
        pass

    def hide_snap_lines(self):
        """隐藏对齐线"""
        self.snap_lines.clear()


class GestureRecognizer:
    """手势识别器"""

    def __init__(self):
        self.gesture_points = []
        self.gesture_start_time = None
        self.min_gesture_points = 5
        self.gesture_timeout = 2000  # 2秒超时

        logger.info("手势识别器初始化完成")

    def start_gesture(self, start_point: QPointF):
        """开始手势识别"""
        self.gesture_points = [start_point]
        self.gesture_start_time = QTimer()
        self.gesture_start_time.start()

    def add_gesture_point(self, point: QPointF):
        """添加手势点"""
        if self.gesture_points:
            self.gesture_points.append(point)

    def end_gesture(self) -> Optional[str]:
        """结束手势识别"""
        if len(self.gesture_points) < self.min_gesture_points:
            return None

        # 简单的手势识别逻辑
        gesture = self.recognize_gesture()
        self.clear_gesture()
        return gesture

    def recognize_gesture(self) -> Optional[str]:
        """识别手势"""
        if len(self.gesture_points) < 2:
            return None

        # 计算总体移动方向
        start_point = self.gesture_points[0]
        end_point = self.gesture_points[-1]

        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()

        # 判断手势类型
        if abs(dx) > abs(dy):
            if dx > 50:
                return "swipe_right"
            elif dx < -50:
                return "swipe_left"
        else:
            if dy > 50:
                return "swipe_down"
            elif dy < -50:
                return "swipe_up"

        # 检查圆形手势
        if self.is_circular_gesture():
            return "circle"

        return None

    def is_circular_gesture(self) -> bool:
        """检查是否为圆形手势"""
        if len(self.gesture_points) < 8:
            return False

        # 简化的圆形检测
        center = self.calculate_center()
        if not center:
            return False

        # 检查点到中心的距离变化
        distances = []
        for point in self.gesture_points:
            distance = math.sqrt((point.x() - center.x())**2 + (point.y() - center.y())**2)
            distances.append(distance)

        # 如果距离变化不大，可能是圆形
        avg_distance = sum(distances) / len(distances)
        variance = sum((d - avg_distance)**2 for d in distances) / len(distances)

        return variance < avg_distance * 0.2  # 20%的变化阈值

    def calculate_center(self) -> Optional[QPointF]:
        """计算手势中心点"""
        if not self.gesture_points:
            return None

        x_sum = sum(p.x() for p in self.gesture_points)
        y_sum = sum(p.y() for p in self.gesture_points)

        return QPointF(x_sum / len(self.gesture_points), y_sum / len(self.gesture_points))

    def clear_gesture(self):
        """清除手势数据"""
        self.gesture_points = []
        self.gesture_start_time = None


class DirectManipulationManager:
    """直接操纵管理器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.direct_manipulation_interface = None
        self.drag_drop_system = None
        self.smart_snap_system = None
        self.gesture_recognizer = None

        self.initialize_direct_manipulation()
        logger.info("直接操纵管理器初始化完成")

    def initialize_direct_manipulation(self):
        """初始化直接操纵系统"""
        try:
            # 获取舞台画布
            stage_canvas = self.get_stage_canvas()

            if stage_canvas:
                # 初始化直接操纵界面
                self.direct_manipulation_interface = DirectManipulationInterface(stage_canvas)
                self.setup_direct_manipulation_connections()

                # 初始化拖拽系统
                self.drag_drop_system = DragDropSystem()
                self.setup_drag_drop_connections()

                # 初始化智能对齐系统
                self.smart_snap_system = SmartSnapSystem(stage_canvas)

                # 初始化手势识别器
                self.gesture_recognizer = GestureRecognizer()

        except Exception as e:
            logger.error(f"初始化直接操纵系统失败: {e}")

    def get_stage_canvas(self):
        """获取舞台画布"""
        if hasattr(self.main_window, 'stage_widget'):
            stage_widget = self.main_window.stage_widget
            if hasattr(stage_widget, 'stage_canvas'):
                return stage_widget.stage_canvas
        return None

    def setup_direct_manipulation_connections(self):
        """设置直接操纵连接"""
        if self.direct_manipulation_interface:
            self.direct_manipulation_interface.element_selected.connect(self.on_element_selected)
            self.direct_manipulation_interface.element_moved.connect(self.on_element_moved)
            self.direct_manipulation_interface.element_resized.connect(self.on_element_resized)
            self.direct_manipulation_interface.element_rotated.connect(self.on_element_rotated)
            self.direct_manipulation_interface.element_text_edited.connect(self.on_element_text_edited)
            self.direct_manipulation_interface.element_action.connect(self.on_element_action)

    def setup_drag_drop_connections(self):
        """设置拖拽连接"""
        if self.drag_drop_system:
            self.drag_drop_system.element_dropped.connect(self.on_element_dropped)
            self.drag_drop_system.element_reordered.connect(self.on_element_reordered)
            self.drag_drop_system.asset_dropped.connect(self.on_asset_dropped)

    def on_element_selected(self, element_id: str):
        """元素选择处理"""
        logger.info(f"元素选择: {element_id}")

        # 更新属性面板
        if hasattr(self.main_window, 'properties_widget'):
            self.main_window.properties_widget.load_element_properties(element_id)

    def on_element_moved(self, element_id: str, new_pos: QPointF):
        """元素移动处理"""
        # 应用智能对齐
        if self.smart_snap_system:
            snapped_pos = self.smart_snap_system.calculate_snap_position(element_id, new_pos)
            new_pos = snapped_pos

        logger.info(f"元素移动: {element_id} -> ({new_pos.x()}, {new_pos.y()})")

        # 更新元素位置
        self.update_element_position(element_id, new_pos)

    def on_element_resized(self, element_id: str, new_bounds: QRectF):
        """元素缩放处理"""
        logger.info(f"元素缩放: {element_id} -> {new_bounds}")

        # 更新元素大小
        self.update_element_size(element_id, new_bounds)

    def on_element_rotated(self, element_id: str, rotation: float):
        """元素旋转处理"""
        logger.info(f"元素旋转: {element_id} -> {rotation}°")

        # 更新元素旋转
        self.update_element_rotation(element_id, rotation)

    def on_element_text_edited(self, element_id: str, new_text: str):
        """元素文本编辑处理"""
        logger.info(f"文本编辑: {element_id} -> {new_text}")

        # 更新元素文本
        self.update_element_text(element_id, new_text)

    def on_element_action(self, element_id: str, action: str):
        """元素动作处理"""
        logger.info(f"元素动作: {element_id} -> {action}")

        # 处理不同的动作
        if action == "copy":
            self.copy_element(element_id)
        elif action == "cut":
            self.cut_element(element_id)
        elif action == "delete":
            self.delete_element(element_id)
        elif action == "bring_to_front":
            self.bring_element_to_front(element_id)
        elif action == "send_to_back":
            self.send_element_to_back(element_id)
        elif action == "properties":
            self.show_element_properties(element_id)

    def on_element_dropped(self, element_id: str, pos: QPointF):
        """元素拖拽到舞台处理"""
        logger.info(f"元素拖拽到舞台: {element_id} -> ({pos.x()}, {pos.y()})")

    def on_element_reordered(self, element_id: str, new_index: int):
        """元素重新排序处理"""
        logger.info(f"元素重新排序: {element_id} -> {new_index}")

    def on_asset_dropped(self, asset_id: str, pos: QPointF):
        """素材拖拽到舞台处理"""
        logger.info(f"素材拖拽到舞台: {asset_id} -> ({pos.x()}, {pos.y()})")

    def update_element_position(self, element_id: str, pos: QPointF):
        """更新元素位置"""
        # 这里需要与数据模型集成
        pass

    def update_element_size(self, element_id: str, bounds: QRectF):
        """更新元素大小"""
        # 这里需要与数据模型集成
        pass

    def update_element_rotation(self, element_id: str, rotation: float):
        """更新元素旋转"""
        # 这里需要与数据模型集成
        pass

    def update_element_text(self, element_id: str, text: str):
        """更新元素文本"""
        # 这里需要与数据模型集成
        pass

    def copy_element(self, element_id: str):
        """复制元素"""
        # 这里需要实现复制逻辑
        pass

    def cut_element(self, element_id: str):
        """剪切元素"""
        # 这里需要实现剪切逻辑
        pass

    def delete_element(self, element_id: str):
        """删除元素"""
        # 这里需要实现删除逻辑
        pass

    def bring_element_to_front(self, element_id: str):
        """置于顶层"""
        # 这里需要实现层级调整逻辑
        pass

    def send_element_to_back(self, element_id: str):
        """置于底层"""
        # 这里需要实现层级调整逻辑
        pass

    def show_element_properties(self, element_id: str):
        """显示元素属性"""
        if hasattr(self.main_window, 'properties_widget'):
            self.main_window.properties_widget.load_element_properties(element_id)

    def get_direct_manipulation_summary(self) -> dict:
        """获取直接操纵摘要"""
        return {
            'interface_active': self.direct_manipulation_interface is not None,
            'drag_drop_active': self.drag_drop_system is not None,
            'snap_enabled': self.smart_snap_system.snap_enabled if self.smart_snap_system else False,
            'gesture_recognition_active': self.gesture_recognizer is not None,
            'selected_element': self.direct_manipulation_interface.selected_element if self.direct_manipulation_interface else None
        }
