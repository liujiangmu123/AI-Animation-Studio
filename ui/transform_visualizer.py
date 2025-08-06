"""
AI Animation Studio - 变换可视化控制器
提供直观的变换属性可视化编辑功能
"""

import math
from typing import Optional, Tuple, Callable
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF, QTimer
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPolygonF, QTransform

from core.data_structures import Element, Transform, Point
from core.logger import get_logger

logger = get_logger("transform_visualizer")


class TransformVisualizer(QWidget):
    """变换可视化控制器"""
    
    # 信号定义
    transform_changed = pyqtSignal(dict)  # 变换改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.element = None
        self.scale_factor = 1.0
        self.grid_size = 20
        
        # 控制状态
        self.dragging = False
        self.rotating = False
        self.scaling = False
        self.drag_start_pos = QPointF()
        self.initial_transform = None
        
        # 控制手柄
        self.handles = {
            'move': QRectF(),
            'rotate': QRectF(),
            'scale_tl': QRectF(),  # 左上角缩放
            'scale_tr': QRectF(),  # 右上角缩放
            'scale_bl': QRectF(),  # 左下角缩放
            'scale_br': QRectF(),  # 右下角缩放
            'scale_t': QRectF(),   # 顶部缩放
            'scale_b': QRectF(),   # 底部缩放
            'scale_l': QRectF(),   # 左侧缩放
            'scale_r': QRectF(),   # 右侧缩放
        }
        
        self.setMinimumSize(300, 300)
        self.setMouseTracking(True)
        
        # 预览更新定时器
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)
        
        logger.info("变换可视化控制器初始化完成")
    
    def set_element(self, element: Element):
        """设置要编辑的元素"""
        self.element = element
        self.update()
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制背景网格
        self.draw_grid(painter)
        
        # 绘制坐标轴
        self.draw_axes(painter)
        
        if self.element:
            # 绘制元素预览
            self.draw_element_preview(painter)
            
            # 绘制变换控制手柄
            self.draw_transform_handles(painter)
            
            # 绘制变换信息
            self.draw_transform_info(painter)
    
    def draw_grid(self, painter: QPainter):
        """绘制网格"""
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.PenStyle.DotLine))
        
        width = self.width()
        height = self.height()
        
        # 垂直线
        for x in range(0, width, self.grid_size):
            painter.drawLine(x, 0, x, height)
        
        # 水平线
        for y in range(0, height, self.grid_size):
            painter.drawLine(0, y, width, y)
    
    def draw_axes(self, painter: QPainter):
        """绘制坐标轴"""
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # X轴
        painter.drawLine(0, center_y, self.width(), center_y)
        painter.drawText(self.width() - 20, center_y - 5, "X")
        
        # Y轴
        painter.drawLine(center_x, 0, center_x, self.height())
        painter.drawText(center_x + 5, 15, "Y")
        
        # 原点
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.drawEllipse(center_x - 3, center_y - 3, 6, 6)
    
    def draw_element_preview(self, painter: QPainter):
        """绘制元素预览"""
        if not self.element:
            return
        
        # 计算元素在画布上的位置
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # 元素基础大小
        element_width = 80
        element_height = 60
        
        # 应用变换
        transform = QTransform()
        
        # 平移到中心
        transform.translate(center_x, center_y)
        
        # 应用元素位置偏移
        transform.translate(self.element.position.x * self.scale_factor, 
                          self.element.position.y * self.scale_factor)
        
        # 应用旋转
        if hasattr(self.element, 'transform') and self.element.transform:
            transform.rotate(self.element.transform.rotate_z)
            transform.scale(self.element.transform.scale_x, self.element.transform.scale_y)
        
        painter.setTransform(transform)
        
        # 绘制元素矩形
        element_rect = QRectF(-element_width/2, -element_height/2, element_width, element_height)
        
        # 根据元素类型设置颜色
        if self.element.element_type.value == "text":
            color = QColor(100, 150, 255, 100)
        elif self.element.element_type.value == "image":
            color = QColor(255, 150, 100, 100)
        elif self.element.element_type.value == "shape":
            color = QColor(150, 255, 100, 100)
        else:
            color = QColor(200, 200, 200, 100)
        
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color.darker(), 2))
        painter.drawRect(element_rect)
        
        # 绘制元素名称
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(element_rect, Qt.AlignmentFlag.AlignCenter, self.element.name)
        
        # 重置变换
        painter.resetTransform()
        
        # 更新控制手柄位置
        self.update_handle_positions(transform, element_rect)
    
    def update_handle_positions(self, transform: QTransform, element_rect: QRectF):
        """更新控制手柄位置"""
        handle_size = 8
        
        # 变换元素矩形的四个角点
        corners = [
            transform.map(element_rect.topLeft()),
            transform.map(element_rect.topRight()),
            transform.map(element_rect.bottomLeft()),
            transform.map(element_rect.bottomRight())
        ]
        
        # 边的中点
        edges = [
            transform.map(QPointF(element_rect.center().x(), element_rect.top())),    # 顶部
            transform.map(QPointF(element_rect.center().x(), element_rect.bottom())), # 底部
            transform.map(QPointF(element_rect.left(), element_rect.center().y())),   # 左侧
            transform.map(QPointF(element_rect.right(), element_rect.center().y()))   # 右侧
        ]
        
        # 更新缩放手柄
        self.handles['scale_tl'] = QRectF(corners[0].x() - handle_size/2, corners[0].y() - handle_size/2, handle_size, handle_size)
        self.handles['scale_tr'] = QRectF(corners[1].x() - handle_size/2, corners[1].y() - handle_size/2, handle_size, handle_size)
        self.handles['scale_bl'] = QRectF(corners[2].x() - handle_size/2, corners[2].y() - handle_size/2, handle_size, handle_size)
        self.handles['scale_br'] = QRectF(corners[3].x() - handle_size/2, corners[3].y() - handle_size/2, handle_size, handle_size)
        
        self.handles['scale_t'] = QRectF(edges[0].x() - handle_size/2, edges[0].y() - handle_size/2, handle_size, handle_size)
        self.handles['scale_b'] = QRectF(edges[1].x() - handle_size/2, edges[1].y() - handle_size/2, handle_size, handle_size)
        self.handles['scale_l'] = QRectF(edges[2].x() - handle_size/2, edges[2].y() - handle_size/2, handle_size, handle_size)
        self.handles['scale_r'] = QRectF(edges[3].x() - handle_size/2, edges[3].y() - handle_size/2, handle_size, handle_size)
        
        # 移动手柄（元素中心）
        center = transform.map(element_rect.center())
        self.handles['move'] = QRectF(center.x() - handle_size/2, center.y() - handle_size/2, handle_size, handle_size)
        
        # 旋转手柄（顶部外侧）
        rotate_pos = transform.map(QPointF(element_rect.center().x(), element_rect.top() - 20))
        self.handles['rotate'] = QRectF(rotate_pos.x() - handle_size/2, rotate_pos.y() - handle_size/2, handle_size, handle_size)
    
    def draw_transform_handles(self, painter: QPainter):
        """绘制变换控制手柄"""
        if not self.element:
            return
        
        # 缩放手柄（蓝色方块）
        painter.setBrush(QBrush(QColor(0, 120, 255)))
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        
        scale_handles = ['scale_tl', 'scale_tr', 'scale_bl', 'scale_br', 
                        'scale_t', 'scale_b', 'scale_l', 'scale_r']
        
        for handle_name in scale_handles:
            painter.drawRect(self.handles[handle_name])
        
        # 移动手柄（绿色圆圈）
        painter.setBrush(QBrush(QColor(0, 200, 0)))
        painter.drawEllipse(self.handles['move'])
        
        # 旋转手柄（红色圆圈）
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.drawEllipse(self.handles['rotate'])
        
        # 绘制旋转连接线
        if 'move' in self.handles and 'rotate' in self.handles:
            painter.setPen(QPen(QColor(255, 0, 0), 1, Qt.PenStyle.DashLine))
            painter.drawLine(self.handles['move'].center(), self.handles['rotate'].center())
    
    def draw_transform_info(self, painter: QPainter):
        """绘制变换信息"""
        if not self.element:
            return
        
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.setFont(QFont("Arial", 9))
        
        info_lines = []
        info_lines.append(f"位置: ({self.element.position.x:.1f}, {self.element.position.y:.1f})")
        
        if hasattr(self.element, 'transform') and self.element.transform:
            info_lines.append(f"旋转: {self.element.transform.rotate_z:.1f}°")
            info_lines.append(f"缩放: {self.element.transform.scale_x:.2f} × {self.element.transform.scale_y:.2f}")
        
        # 绘制信息文本
        y_offset = 15
        for line in info_lines:
            painter.drawText(10, y_offset, line)
            y_offset += 15
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if not self.element:
            return
        
        pos = QPointF(event.position())
        
        # 检查点击的手柄
        for handle_name, handle_rect in self.handles.items():
            if handle_rect.contains(pos):
                self.dragging = True
                self.drag_start_pos = pos
                
                # 保存初始变换状态
                if hasattr(self.element, 'transform') and self.element.transform:
                    self.initial_transform = {
                        'position_x': self.element.position.x,
                        'position_y': self.element.position.y,
                        'rotation': self.element.transform.rotate_z,
                        'scale_x': self.element.transform.scale_x,
                        'scale_y': self.element.transform.scale_y
                    }
                else:
                    self.initial_transform = {
                        'position_x': self.element.position.x,
                        'position_y': self.element.position.y,
                        'rotation': 0,
                        'scale_x': 1,
                        'scale_y': 1
                    }
                
                # 设置操作类型
                if handle_name == 'move':
                    self.setCursor(Qt.CursorShape.SizeAllCursor)
                elif handle_name == 'rotate':
                    self.rotating = True
                    self.setCursor(Qt.CursorShape.CrossCursor)
                elif handle_name.startswith('scale_'):
                    self.scaling = True
                    self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                
                break
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        pos = QPointF(event.position())
        
        if self.dragging and self.element:
            delta = pos - self.drag_start_pos
            
            if self.rotating:
                # 旋转操作
                self.handle_rotation(delta)
            elif self.scaling:
                # 缩放操作
                self.handle_scaling(delta)
            else:
                # 移动操作
                self.handle_movement(delta)
            
            self.update()
            self.schedule_preview_update()
        else:
            # 更新鼠标光标
            self.update_cursor(pos)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.dragging:
            self.dragging = False
            self.rotating = False
            self.scaling = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
            # 发送变换改变信号
            self.emit_transform_changed()
    
    def handle_movement(self, delta: QPointF):
        """处理移动操作"""
        if not self.element:
            return
        
        # 转换屏幕坐标到逻辑坐标
        logical_delta_x = delta.x() / self.scale_factor
        logical_delta_y = delta.y() / self.scale_factor
        
        self.element.position.x = self.initial_transform['position_x'] + logical_delta_x
        self.element.position.y = self.initial_transform['position_y'] + logical_delta_y
    
    def handle_rotation(self, delta: QPointF):
        """处理旋转操作"""
        if not self.element:
            return
        
        # 计算旋转角度
        angle_delta = delta.x() * 0.5  # 调整旋转敏感度
        
        if not hasattr(self.element, 'transform') or not self.element.transform:
            from core.data_structures import Transform
            self.element.transform = Transform()
        
        self.element.transform.rotate_z = self.initial_transform['rotation'] + angle_delta
        
        # 限制角度范围
        while self.element.transform.rotate_z > 360:
            self.element.transform.rotate_z -= 360
        while self.element.transform.rotate_z < -360:
            self.element.transform.rotate_z += 360
    
    def handle_scaling(self, delta: QPointF):
        """处理缩放操作"""
        if not self.element:
            return
        
        # 计算缩放因子
        scale_delta = 1.0 + (delta.x() + delta.y()) * 0.01  # 调整缩放敏感度
        
        if not hasattr(self.element, 'transform') or not self.element.transform:
            from core.data_structures import Transform
            self.element.transform = Transform()
        
        self.element.transform.scale_x = max(0.1, self.initial_transform['scale_x'] * scale_delta)
        self.element.transform.scale_y = max(0.1, self.initial_transform['scale_y'] * scale_delta)
    
    def update_cursor(self, pos: QPointF):
        """更新鼠标光标"""
        for handle_name, handle_rect in self.handles.items():
            if handle_rect.contains(pos):
                if handle_name == 'move':
                    self.setCursor(Qt.CursorShape.SizeAllCursor)
                elif handle_name == 'rotate':
                    self.setCursor(Qt.CursorShape.CrossCursor)
                elif handle_name.startswith('scale_'):
                    self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                return
        
        self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def schedule_preview_update(self):
        """安排预览更新"""
        self.preview_timer.start(100)  # 100ms延迟
    
    def update_preview(self):
        """更新预览"""
        self.emit_transform_changed()
    
    def emit_transform_changed(self):
        """发送变换改变信号"""
        if not self.element:
            return
        
        transform_data = {
            'position_x': self.element.position.x,
            'position_y': self.element.position.y,
        }
        
        if hasattr(self.element, 'transform') and self.element.transform:
            transform_data.update({
                'rotation': self.element.transform.rotate_z,
                'scale_x': self.element.transform.scale_x,
                'scale_y': self.element.transform.scale_y
            })
        
        self.transform_changed.emit(transform_data)
    
    def reset_transform(self):
        """重置变换"""
        if not self.element:
            return
        
        self.element.position.x = 0
        self.element.position.y = 0
        
        if hasattr(self.element, 'transform') and self.element.transform:
            self.element.transform.rotate_z = 0
            self.element.transform.scale_x = 1
            self.element.transform.scale_y = 1
        
        self.update()
        self.emit_transform_changed()
    
    def set_scale_factor(self, factor: float):
        """设置缩放因子"""
        self.scale_factor = factor
        self.update()
