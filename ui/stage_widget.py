"""
AI Animation Studio - 舞台组件
提供可视化的舞台布局和元素管理功能
"""

from typing import List, Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QScrollArea, QFrame, QComboBox, QSpinBox, QSlider, QCheckBox,
    QToolButton, QButtonGroup, QSplitter, QMenu, QToolBar,
    QStatusBar, QProgressBar, QLineEdit, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QTimer, QPropertyAnimation
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPixmap, QCursor,
    QMouseEvent, QWheelEvent, QKeyEvent, QPainterPath, QLinearGradient, QAction
)

from core.data_structures import Element, Point
from core.logger import get_logger

logger = get_logger("stage_widget")

class StageCanvas(QWidget):
    """舞台画布"""

    element_selected = pyqtSignal(str)  # 元素选择信号
    element_moved = pyqtSignal(str, Point)  # 元素移动信号
    scale_changed = pyqtSignal(float)  # 缩放改变信号
    guide_added = pyqtSignal(str, float)  # 参考线添加信号

    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.canvas_width = 1920
        self.canvas_height = 1080
        self.scale_factor = 0.4  # 缩放比例
        self.min_scale = 0.1
        self.max_scale = 5.0

        # 网格设置
        self.grid_enabled = True
        self.grid_size = 20
        self.grid_color = QColor("#e0e0e0")
        self.major_grid_enabled = True
        self.major_grid_interval = 5  # 每5个小网格一个大网格
        self.major_grid_color = QColor("#c0c0c0")

        # 网格样式选项
        self.grid_style = "solid"  # solid, dotted, dashed
        self.grid_opacity = 0.8
        self.adaptive_grid = True  # 根据缩放自动调整网格密度
        self.snap_to_grid = True   # 元素对齐到网格
        self.snap_threshold = 10   # 对齐阈值（像素）

        # 网格预设
        self.grid_presets = {
            "fine": {"size": 10, "major_interval": 5},
            "normal": {"size": 20, "major_interval": 5},
            "coarse": {"size": 50, "major_interval": 4},
            "custom": {"size": self.grid_size, "major_interval": self.major_grid_interval}
        }

        # 标尺设置
        self.rulers_enabled = True
        self.ruler_size = 20
        self.ruler_color = QColor("#d0d0d0")
        self.ruler_text_color = QColor("#666666")

        # 参考线设置
        self.guides_enabled = True
        self.horizontal_guides = []  # 水平参考线
        self.vertical_guides = []    # 垂直参考线
        self.guide_color = QColor("#ff6b6b")
        self.guide_width = 1

        # 元素管理
        self.elements = {}
        self.selected_element = None
        self.selected_elements = set()  # 多选支持

        # 交互状态
        self.dragging = False
        self.drag_start_pos = QPoint()
        self.drag_element = None
        self.pan_mode = False
        self.pan_start_pos = QPoint()
        self.canvas_offset = QPoint(0, 0)

        # 选择框
        self.selection_rect = QRect()
        self.selecting = False

        # 背景设置
        self.background_color = QColor("#ffffff")
        self.canvas_border_color = QColor("#333333")
        self.canvas_border_width = 2

        # 设置样式
        self.setStyleSheet("background-color: #f0f0f0;")
        self.setMouseTracking(True)  # 启用鼠标跟踪
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # 启用键盘焦点
    
    def set_canvas_size(self, width: int, height: int):
        """设置画布大小"""
        self.canvas_width = width
        self.canvas_height = height
        self.update()
    
    def set_scale_factor(self, scale: float):
        """设置缩放比例"""
        scale = max(self.min_scale, min(self.max_scale, scale))
        if abs(self.scale_factor - scale) > 0.001:  # 避免微小变化
            self.scale_factor = scale
            self.scale_changed.emit(scale)
            self.update()
            logger.debug(f"缩放比例设置为: {scale:.2f}")

    def zoom_in(self):
        """放大"""
        new_scale = self.scale_factor * 1.2
        self.set_scale_factor(new_scale)

    def zoom_out(self):
        """缩小"""
        new_scale = self.scale_factor / 1.2
        self.set_scale_factor(new_scale)

    def zoom_to_fit(self):
        """缩放到适合"""
        widget_rect = self.rect()
        if widget_rect.width() <= 0 or widget_rect.height() <= 0:
            return

        # 计算适合的缩放比例
        scale_x = (widget_rect.width() - 100) / self.canvas_width
        scale_y = (widget_rect.height() - 100) / self.canvas_height
        scale = min(scale_x, scale_y)

        self.set_scale_factor(scale)

    def zoom_to_actual_size(self):
        """缩放到实际大小"""
        self.set_scale_factor(1.0)

    # 网格控制
    def set_grid_enabled(self, enabled: bool):
        """设置网格显示"""
        self.grid_enabled = enabled
        self.update()
        logger.debug(f"网格显示设置为: {enabled}")

    def set_grid_size(self, size: int):
        """设置网格大小"""
        old_size = self.grid_size
        self.grid_size = max(5, min(200, size))
        if old_size != self.grid_size:
            self.update()
            logger.debug(f"网格大小从 {old_size} 更改为 {self.grid_size}")

    def set_major_grid_enabled(self, enabled: bool):
        """设置主网格显示"""
        self.major_grid_enabled = enabled
        self.update()
        logger.debug(f"主网格显示设置为: {enabled}")

    def set_major_grid_interval(self, interval: int):
        """设置主网格间隔"""
        old_interval = self.major_grid_interval
        self.major_grid_interval = max(2, min(20, interval))
        if old_interval != self.major_grid_interval:
            self.update()
            logger.debug(f"主网格间隔从 {old_interval} 更改为 {self.major_grid_interval}")

    def set_grid_color(self, color: QColor):
        """设置网格颜色"""
        self.grid_color = color
        self.update()
        logger.debug(f"网格颜色设置为: {color.name()}")

    def set_major_grid_color(self, color: QColor):
        """设置主网格颜色"""
        self.major_grid_color = color
        self.update()
        logger.debug(f"主网格颜色设置为: {color.name()}")

    def set_grid_style(self, style: str):
        """设置网格样式"""
        if style in ["solid", "dotted", "dashed"]:
            self.grid_style = style
            self.update()
            logger.debug(f"网格样式设置为: {style}")

    def set_grid_opacity(self, opacity: float):
        """设置网格透明度"""
        self.grid_opacity = max(0.1, min(1.0, opacity))
        self.update()
        logger.debug(f"网格透明度设置为: {self.grid_opacity}")

    def set_adaptive_grid(self, enabled: bool):
        """设置自适应网格"""
        self.adaptive_grid = enabled
        self.update()
        logger.debug(f"自适应网格设置为: {enabled}")

    def set_snap_to_grid(self, enabled: bool):
        """设置网格对齐"""
        self.snap_to_grid = enabled
        logger.debug(f"网格对齐设置为: {enabled}")

    def set_snap_threshold(self, threshold: int):
        """设置对齐阈值"""
        self.snap_threshold = max(1, min(50, threshold))
        logger.debug(f"对齐阈值设置为: {self.snap_threshold}")

    def apply_grid_preset(self, preset_name: str):
        """应用网格预设"""
        if preset_name in self.grid_presets:
            preset = self.grid_presets[preset_name]
            self.set_grid_size(preset["size"])
            self.set_major_grid_interval(preset["major_interval"])
            logger.info(f"应用网格预设: {preset_name}")
        else:
            logger.warning(f"未知的网格预设: {preset_name}")

    def get_grid_settings(self) -> dict:
        """获取当前网格设置"""
        return {
            "enabled": self.grid_enabled,
            "size": self.grid_size,
            "color": self.grid_color.name(),
            "major_enabled": self.major_grid_enabled,
            "major_interval": self.major_grid_interval,
            "major_color": self.major_grid_color.name(),
            "style": self.grid_style,
            "opacity": self.grid_opacity,
            "adaptive": self.adaptive_grid,
            "snap_enabled": self.snap_to_grid,
            "snap_threshold": self.snap_threshold
        }

    def load_grid_settings(self, settings: dict):
        """加载网格设置"""
        try:
            if "enabled" in settings:
                self.set_grid_enabled(settings["enabled"])
            if "size" in settings:
                self.set_grid_size(settings["size"])
            if "color" in settings:
                self.set_grid_color(QColor(settings["color"]))
            if "major_enabled" in settings:
                self.set_major_grid_enabled(settings["major_enabled"])
            if "major_interval" in settings:
                self.set_major_grid_interval(settings["major_interval"])
            if "major_color" in settings:
                self.set_major_grid_color(QColor(settings["major_color"]))
            if "style" in settings:
                self.set_grid_style(settings["style"])
            if "opacity" in settings:
                self.set_grid_opacity(settings["opacity"])
            if "adaptive" in settings:
                self.set_adaptive_grid(settings["adaptive"])
            if "snap_enabled" in settings:
                self.set_snap_to_grid(settings["snap_enabled"])
            if "snap_threshold" in settings:
                self.set_snap_threshold(settings["snap_threshold"])

            logger.info("网格设置加载完成")
        except Exception as e:
            logger.error(f"加载网格设置失败: {e}")

    # 标尺控制
    def set_rulers_enabled(self, enabled: bool):
        """设置标尺显示"""
        self.rulers_enabled = enabled
        self.update()

    # 参考线控制
    def set_guides_enabled(self, enabled: bool):
        """设置参考线显示"""
        self.guides_enabled = enabled
        self.update()

    def add_horizontal_guide(self, y: float):
        """添加水平参考线"""
        if y not in self.horizontal_guides:
            self.horizontal_guides.append(y)
            self.horizontal_guides.sort()
            self.guide_added.emit("horizontal", y)
            self.update()
            logger.debug(f"添加水平参考线: {y}")

    def add_vertical_guide(self, x: float):
        """添加垂直参考线"""
        if x not in self.vertical_guides:
            self.vertical_guides.append(x)
            self.vertical_guides.sort()
            self.guide_added.emit("vertical", x)
            self.update()
            logger.debug(f"添加垂直参考线: {x}")

    def remove_guide(self, orientation: str, position: float):
        """移除参考线"""
        if orientation == "horizontal" and position in self.horizontal_guides:
            self.horizontal_guides.remove(position)
            self.update()
        elif orientation == "vertical" and position in self.vertical_guides:
            self.vertical_guides.remove(position)
            self.update()

    def clear_guides(self):
        """清除所有参考线"""
        self.horizontal_guides.clear()
        self.vertical_guides.clear()
        self.update()
    
    def add_element(self, element: Element):
        """安全地添加元素"""
        try:
            if not element:
                logger.warning("尝试添加空元素")
                return False

            # 验证元素属性
            if not hasattr(element, 'element_id') or not element.element_id:
                logger.warning("元素缺少有效的element_id")
                return False

            if not self.is_valid_element(element):
                logger.warning(f"元素无效，无法添加: {element.element_id}")
                return False

            # 添加元素
            self.elements[element.element_id] = element
            self.update()

            logger.info(f"成功添加元素: {element.element_id}")
            return True

        except Exception as e:
            logger.error(f"添加元素失败: {e}")
            return False

    def remove_element(self, element_id: str):
        """安全地移除元素"""
        try:
            if not element_id or not isinstance(element_id, str):
                logger.warning(f"无效的元素ID: {element_id}")
                return False

            if element_id not in self.elements:
                logger.warning(f"元素不存在，无法移除: {element_id}")
                return False

            # 移除元素
            del self.elements[element_id]

            # 如果移除的是当前选中的元素，清除选择
            if self.selected_element == element_id:
                self.clear_selection_safely()

            self.update()

            logger.info(f"成功移除元素: {element_id}")
            return True

        except Exception as e:
            logger.error(f"移除元素失败: {e}")
            return False
    
    def select_element(self, element_id: str):
        """选择元素 - 使用安全方法"""
        self.select_element_safely(element_id)
    
    def paintEvent(self, event):
        """绘制舞台"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 计算画布在widget中的位置和大小
        widget_rect = self.rect()
        canvas_w = int(self.canvas_width * self.scale_factor)
        canvas_h = int(self.canvas_height * self.scale_factor)

        # 考虑标尺空间
        ruler_offset_x = self.ruler_size if self.rulers_enabled else 0
        ruler_offset_y = self.ruler_size if self.rulers_enabled else 0

        # 居中显示（考虑标尺偏移）
        available_width = widget_rect.width() - ruler_offset_x
        available_height = widget_rect.height() - ruler_offset_y
        canvas_x = ruler_offset_x + (available_width - canvas_w) // 2
        canvas_y = ruler_offset_y + (available_height - canvas_h) // 2
        canvas_rect = QRect(canvas_x, canvas_y, canvas_w, canvas_h)

        # 绘制标尺
        if self.rulers_enabled:
            self.draw_rulers(painter, canvas_rect, widget_rect)

        # 绘制画布背景
        painter.fillRect(canvas_rect, self.background_color)
        painter.setPen(QPen(self.canvas_border_color, self.canvas_border_width))
        painter.drawRect(canvas_rect)

        # 绘制网格
        if self.grid_enabled:
            self.draw_enhanced_grid(painter, canvas_rect)

        # 绘制参考线
        if self.guides_enabled:
            self.draw_guides(painter, canvas_rect)

        # 绘制元素
        for element_id, element in self.elements.items():
            self.draw_element(painter, element, canvas_rect)

        # 绘制选择框
        if self.selecting and not self.selection_rect.isEmpty():
            self.draw_selection_rect(painter)

        # 绘制画布信息
        self.draw_canvas_info(painter, canvas_rect)
    
    def draw_enhanced_grid(self, painter: QPainter, canvas_rect: QRect):
        """绘制增强网格"""
        if not self.grid_enabled:
            return

        # 计算自适应网格大小
        effective_grid_size = self.get_effective_grid_size()
        grid_size_scaled = int(effective_grid_size * self.scale_factor)

        if grid_size_scaled < 2:  # 网格太小时不绘制
            return

        # 设置透明度
        grid_color = QColor(self.grid_color)
        grid_color.setAlphaF(self.grid_opacity)

        major_grid_color = QColor(self.major_grid_color)
        major_grid_color.setAlphaF(self.grid_opacity)

        # 设置画笔样式
        pen_style = Qt.PenStyle.SolidLine
        if self.grid_style == "dotted":
            pen_style = Qt.PenStyle.DotLine
        elif self.grid_style == "dashed":
            pen_style = Qt.PenStyle.DashLine

        # 绘制小网格
        minor_pen = QPen(grid_color, 1, pen_style)
        major_pen = QPen(major_grid_color, 1, pen_style)

        # 优化绘制：只绘制可见区域的网格线
        start_x = canvas_rect.left() - (canvas_rect.left() % grid_size_scaled)
        start_y = canvas_rect.top() - (canvas_rect.top() % grid_size_scaled)

        # 垂直线
        x = start_x
        line_count = 0
        while x <= canvas_rect.right():
            if self.major_grid_enabled and line_count % self.major_grid_interval == 0:
                # 主网格线
                painter.setPen(major_pen)
            else:
                painter.setPen(minor_pen)

            painter.drawLine(x, canvas_rect.top(), x, canvas_rect.bottom())
            x += grid_size_scaled
            line_count += 1

        # 水平线
        y = start_y
        line_count = 0
        while y <= canvas_rect.bottom():
            if self.major_grid_enabled and line_count % self.major_grid_interval == 0:
                # 主网格线
                painter.setPen(major_pen)
            else:
                painter.setPen(minor_pen)

            painter.drawLine(canvas_rect.left(), y, canvas_rect.right(), y)
            y += grid_size_scaled
            line_count += 1

    def get_effective_grid_size(self) -> int:
        """获取有效网格大小（考虑自适应）"""
        if not self.adaptive_grid:
            return self.grid_size

        # 根据缩放级别自动调整网格密度
        if self.scale_factor < 0.25:
            # 缩放很小时，使用更大的网格
            return self.grid_size * 4
        elif self.scale_factor < 0.5:
            return self.grid_size * 2
        elif self.scale_factor > 2.0:
            # 放大很多时，使用更小的网格
            return max(5, self.grid_size // 2)
        else:
            return self.grid_size

    def snap_point_to_grid(self, point: QPoint) -> QPoint:
        """将点对齐到网格"""
        if not self.snap_to_grid:
            return point

        effective_grid_size = self.get_effective_grid_size()

        # 转换到画布坐标
        canvas_point = self.widget_to_canvas(point)

        # 对齐到网格
        snapped_x = round(canvas_point.x() / effective_grid_size) * effective_grid_size
        snapped_y = round(canvas_point.y() / effective_grid_size) * effective_grid_size

        # 转换回组件坐标
        snapped_canvas_point = QPoint(int(snapped_x), int(snapped_y))
        return self.canvas_to_widget(snapped_canvas_point)

    def is_near_grid_line(self, point: QPoint) -> bool:
        """检查点是否接近网格线"""
        if not self.snap_to_grid:
            return False

        effective_grid_size = self.get_effective_grid_size()
        canvas_point = self.widget_to_canvas(point)

        # 检查是否接近垂直网格线
        x_remainder = canvas_point.x() % effective_grid_size
        x_distance = min(x_remainder, effective_grid_size - x_remainder)

        # 检查是否接近水平网格线
        y_remainder = canvas_point.y() % effective_grid_size
        y_distance = min(y_remainder, effective_grid_size - y_remainder)

        # 转换阈值到画布坐标
        threshold_canvas = self.snap_threshold / self.scale_factor

        return x_distance <= threshold_canvas or y_distance <= threshold_canvas

    def draw_rulers(self, painter: QPainter, canvas_rect: QRect, widget_rect: QRect):
        """绘制标尺"""
        if not self.rulers_enabled:
            return

        # 标尺背景
        painter.fillRect(0, 0, widget_rect.width(), self.ruler_size, self.ruler_color)
        painter.fillRect(0, 0, self.ruler_size, widget_rect.height(), self.ruler_color)

        # 标尺刻度
        painter.setPen(QPen(self.ruler_text_color, 1))
        painter.setFont(QFont("Arial", 8))

        # 水平标尺
        ruler_step = max(10, int(50 / self.scale_factor))  # 动态调整刻度间距
        ruler_step_scaled = int(ruler_step * self.scale_factor)

        x = canvas_rect.left()
        canvas_x = 0
        while x <= canvas_rect.right():
            # 绘制刻度线
            if canvas_x % (ruler_step * 5) == 0:  # 长刻度
                painter.drawLine(x, self.ruler_size - 8, x, self.ruler_size)
                # 绘制数字
                painter.drawText(x + 2, self.ruler_size - 2, str(canvas_x))
            elif canvas_x % ruler_step == 0:  # 短刻度
                painter.drawLine(x, self.ruler_size - 4, x, self.ruler_size)

            x += ruler_step_scaled
            canvas_x += ruler_step

        # 垂直标尺
        y = canvas_rect.top()
        canvas_y = 0
        while y <= canvas_rect.bottom():
            # 绘制刻度线
            if canvas_y % (ruler_step * 5) == 0:  # 长刻度
                painter.drawLine(self.ruler_size - 8, y, self.ruler_size, y)
                # 绘制数字（旋转90度）
                painter.save()
                painter.translate(self.ruler_size - 12, y - 2)
                painter.rotate(-90)
                painter.drawText(0, 0, str(canvas_y))
                painter.restore()
            elif canvas_y % ruler_step == 0:  # 短刻度
                painter.drawLine(self.ruler_size - 4, y, self.ruler_size, y)

            y += ruler_step_scaled
            canvas_y += ruler_step

    def draw_guides(self, painter: QPainter, canvas_rect: QRect):
        """绘制参考线"""
        if not self.guides_enabled:
            return

        painter.setPen(QPen(self.guide_color, self.guide_width))

        # 水平参考线
        for guide_y in self.horizontal_guides:
            y = canvas_rect.top() + int(guide_y * self.scale_factor)
            if canvas_rect.top() <= y <= canvas_rect.bottom():
                painter.drawLine(canvas_rect.left(), y, canvas_rect.right(), y)

        # 垂直参考线
        for guide_x in self.vertical_guides:
            x = canvas_rect.left() + int(guide_x * self.scale_factor)
            if canvas_rect.left() <= x <= canvas_rect.right():
                painter.drawLine(x, canvas_rect.top(), x, canvas_rect.bottom())

    def draw_selection_rect(self, painter: QPainter):
        """绘制选择框"""
        painter.setPen(QPen(QColor("#007bff"), 1, Qt.PenStyle.DashLine))
        painter.setBrush(QBrush(QColor(0, 123, 255, 30)))
        painter.drawRect(self.selection_rect)
    
    def draw_element(self, painter: QPainter, element: Element, canvas_rect: QRect):
        """安全地绘制元素"""
        try:
            # 验证输入参数
            if not painter or not element or not canvas_rect:
                return

            # 检查元素有效性
            if not self.is_valid_element(element):
                return

            # 检查元素是否可见
            if not getattr(element, 'visible', True):
                return

            # 安全地获取位置
            position = getattr(element, 'position', None)
            if not position or not hasattr(position, 'x') or not hasattr(position, 'y'):
                logger.warning(f"元素位置无效: {getattr(element, 'element_id', 'unknown')}")
                return

            # 计算元素在画布中的位置
            try:
                x = canvas_rect.left() + int(position.x * self.scale_factor)
                y = canvas_rect.top() + int(position.y * self.scale_factor)
            except (TypeError, ValueError) as e:
                logger.warning(f"位置计算失败: {e}")
                return

            # 检查位置是否在可见范围内
            if not self.is_position_visible(x, y, canvas_rect):
                return

            # 安全地获取元素类型
            element_type = getattr(element, 'element_type', None)
            if not element_type:
                logger.warning(f"元素类型未定义: {getattr(element, 'element_id', 'unknown')}")
                self.draw_generic_element(painter, element, x, y)
                return

            # 根据元素类型绘制
            type_value = getattr(element_type, 'value', str(element_type))

            if type_value == "text":
                self.draw_text_element_safely(painter, element, x, y)
            elif type_value == "image":
                self.draw_image_element_safely(painter, element, x, y)
            elif type_value == "shape":
                self.draw_shape_element_safely(painter, element, x, y)
            else:
                self.draw_generic_element_safely(painter, element, x, y)

            # 绘制选择框
            if hasattr(element, 'element_id') and element.element_id == self.selected_element:
                bounds = self.get_element_bounds_safely(element)
                if bounds:
                    self.draw_selection_box_safely(painter, x, y, bounds['width'], bounds['height'])

        except Exception as e:
            logger.error(f"绘制元素失败: {e}")
            # 尝试绘制错误指示器
            try:
                self.draw_error_indicator(painter, canvas_rect)
            except:
                pass

    def is_position_visible(self, x: int, y: int, canvas_rect: QRect) -> bool:
        """检查位置是否在可见范围内"""
        try:
            margin = 100  # 允许一定的边界外绘制
            return (x >= canvas_rect.left() - margin and
                    x <= canvas_rect.right() + margin and
                    y >= canvas_rect.top() - margin and
                    y <= canvas_rect.bottom() + margin)
        except Exception as e:
            logger.error(f"可见性检查失败: {e}")
            return True  # 默认认为可见

    def draw_text_element_safely(self, painter: QPainter, element: Element, x: int, y: int):
        """安全地绘制文本元素"""
        try:
            painter.setPen(QPen(QColor("#333333"), 1))
            painter.setFont(QFont("Microsoft YaHei", 12))

            # 安全地获取文本内容
            text = getattr(element, 'content', '') or getattr(element, 'name', '未命名')
            if not isinstance(text, str):
                text = str(text)

            # 限制文本长度以避免显示问题
            if len(text) > 20:
                text = text[:17] + "..."

            painter.drawText(x, y + 15, text)  # 调整y位置使文本更好显示

        except Exception as e:
            logger.error(f"绘制文本元素失败: {e}")
            self.draw_error_indicator(painter, QRect(x, y, 100, 20))

    def draw_image_element_safely(self, painter: QPainter, element: Element, x: int, y: int):
        """安全地绘制图片元素"""
        try:
            painter.fillRect(x, y, 100, 80, QColor("#e3f2fd"))
            painter.setPen(QPen(QColor("#2196f3"), 2))
            painter.drawRect(x, y, 100, 80)
            painter.drawText(x + 35, y + 45, "图片")

        except Exception as e:
            logger.error(f"绘制图片元素失败: {e}")
            self.draw_error_indicator(painter, QRect(x, y, 100, 80))

    def draw_shape_element_safely(self, painter: QPainter, element: Element, x: int, y: int):
        """安全地绘制形状元素"""
        try:
            painter.fillRect(x, y, 80, 60, QColor("#fff3e0"))
            painter.setPen(QPen(QColor("#ff9800"), 2))
            painter.drawRect(x, y, 80, 60)
            painter.drawText(x + 25, y + 35, "形状")

        except Exception as e:
            logger.error(f"绘制形状元素失败: {e}")
            self.draw_error_indicator(painter, QRect(x, y, 80, 60))

    def draw_generic_element_safely(self, painter: QPainter, element: Element, x: int, y: int):
        """安全地绘制通用元素"""
        try:
            painter.fillRect(x, y, 60, 40, QColor("#f3e5f5"))
            painter.setPen(QPen(QColor("#9c27b0"), 2))
            painter.drawRect(x, y, 60, 40)

            # 安全地获取名称
            name = getattr(element, 'name', '元素')
            if not isinstance(name, str):
                name = str(name)

            # 限制名称长度
            if len(name) > 6:
                name = name[:5] + "…"

            painter.drawText(x + 5, y + 25, name)

        except Exception as e:
            logger.error(f"绘制通用元素失败: {e}")
            self.draw_error_indicator(painter, QRect(x, y, 60, 40))

    def draw_selection_box_safely(self, painter: QPainter, x: int, y: int, w: float, h: float):
        """安全地绘制选择框"""
        try:
            # 确保尺寸为正数
            width = max(int(w), 10)
            height = max(int(h), 10)

            painter.setPen(QPen(QColor("#2196f3"), 2, Qt.PenStyle.DashLine))
            painter.drawRect(x - 5, y - 5, width + 10, height + 10)

            # 绘制控制点
            self.draw_control_points_safely(painter, x, y, width, height)

            # 绘制智能参考线
            self.draw_smart_guides_safely(painter, x, y, width, height)

            # 绘制对齐提示
            self.draw_alignment_hints_safely(painter, x, y, width, height)

        except Exception as e:
            logger.error(f"绘制选择框失败: {e}")

    def draw_control_points_safely(self, painter: QPainter, x: int, y: int, w: int, h: int):
        """安全地绘制控制点"""
        try:
            painter.setPen(QPen(QColor("#2196f3"), 1))
            painter.setBrush(QBrush(QColor("#ffffff")))

            # 四个角的控制点
            points = [
                (x - 5, y - 5),      # 左上
                (x + w + 5, y - 5),  # 右上
                (x - 5, y + h + 5),  # 左下
                (x + w + 5, y + h + 5)  # 右下
            ]

            for px, py in points:
                painter.drawRect(px - 3, py - 3, 6, 6)

        except Exception as e:
            logger.error(f"绘制控制点失败: {e}")

    def draw_error_indicator(self, painter: QPainter, rect: QRect):
        """绘制错误指示器"""
        try:
            painter.fillRect(rect, QColor("#ffebee"))
            painter.setPen(QPen(QColor("#f44336"), 2))
            painter.drawRect(rect)
            painter.drawText(rect.center().x() - 10, rect.center().y(), "错误")

        except Exception as e:
            logger.error(f"绘制错误指示器失败: {e}")
    
    def draw_text_element(self, painter: QPainter, element: Element, x: int, y: int):
        """绘制文本元素"""
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.setFont(QFont("Microsoft YaHei", 12))
        
        text = element.content or element.name
        painter.drawText(x, y, text)
    
    def draw_image_element(self, painter: QPainter, element: Element, x: int, y: int):
        """绘制图片元素"""
        painter.fillRect(x, y, 100, 80, QColor("#e3f2fd"))
        painter.setPen(QPen(QColor("#2196f3"), 2))
        painter.drawRect(x, y, 100, 80)
        painter.drawText(x + 10, y + 45, "图片")
    
    def draw_shape_element(self, painter: QPainter, element: Element, x: int, y: int):
        """绘制形状元素"""
        painter.fillRect(x, y, 80, 80, QColor("#fff3e0"))
        painter.setPen(QPen(QColor("#ff9800"), 2))
        painter.drawRect(x, y, 80, 80)
        painter.drawText(x + 20, y + 45, "形状")
    
    def draw_generic_element(self, painter: QPainter, element: Element, x: int, y: int):
        """绘制通用元素"""
        painter.fillRect(x, y, 60, 40, QColor("#f3e5f5"))
        painter.setPen(QPen(QColor("#9c27b0"), 2))
        painter.drawRect(x, y, 60, 40)
        painter.drawText(x + 5, y + 25, element.name[:6])
    
    def draw_selection_box(self, painter: QPainter, x: int, y: int, w: int, h: int):
        """绘制选择框"""
        painter.setPen(QPen(QColor("#2196f3"), 2, Qt.PenStyle.DashLine))
        painter.drawRect(x - 5, y - 5, w + 10, h + 10)
        
        # 绘制控制点
        painter.fillRect(x - 3, y - 3, 6, 6, QColor("#2196f3"))
        painter.fillRect(x + w - 3, y - 3, 6, 6, QColor("#2196f3"))
        painter.fillRect(x - 3, y + h - 3, 6, 6, QColor("#2196f3"))
        painter.fillRect(x + w - 3, y + h - 3, 6, 6, QColor("#2196f3"))
    
    def draw_canvas_info(self, painter: QPainter, canvas_rect: QRect):
        """绘制画布信息"""
        painter.setPen(QPen(QColor("#666666"), 1))
        painter.setFont(QFont("Arial", 10))
        
        info_text = f"{self.canvas_width}×{self.canvas_height} ({self.scale_factor:.0%})"
        painter.drawText(canvas_rect.left() + 10, canvas_rect.top() + 20, info_text)
    
    def mousePressEvent(self, event):
        """鼠标点击事件 - 安全的元素选择"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                # 获取点击位置
                click_pos = event.position()
                if hasattr(click_pos, 'x') and hasattr(click_pos, 'y'):
                    x, y = click_pos.x(), click_pos.y()
                else:
                    # 兼容旧版本PyQt
                    x, y = event.x(), event.y()

                # 查找被点击的元素
                clicked_element = self.find_element_at_position(x, y)

                if clicked_element:
                    self.select_element_safely(clicked_element)
                else:
                    # 点击空白区域，取消选择
                    self.clear_selection_safely()

        except Exception as e:
            logger.error(f"鼠标点击事件处理失败: {e}")

    def find_element_at_position(self, x: float, y: float) -> str:
        """安全地查找指定位置的元素"""
        try:
            # 转换屏幕坐标到画布坐标
            canvas_x = x / self.scale_factor
            canvas_y = y / self.scale_factor

            # 遍历所有元素，查找被点击的元素
            for element_id, element in self.elements.items():
                if not self.is_valid_element(element):
                    continue

                # 获取元素边界
                bounds = self.get_element_bounds_safely(element)
                if bounds and self.point_in_bounds(canvas_x, canvas_y, bounds):
                    return element_id

            return None

        except Exception as e:
            logger.error(f"查找位置元素失败: {e}")
            return None

    def is_valid_element(self, element) -> bool:
        """检查元素是否有效"""
        try:
            if not element:
                return False

            # 检查必要属性是否存在
            required_attrs = ['element_id', 'position', 'visible']
            for attr in required_attrs:
                if not hasattr(element, attr):
                    logger.warning(f"元素缺少必要属性: {attr}")
                    return False

            # 检查元素是否可见
            if not getattr(element, 'visible', True):
                return False

            # 检查位置是否有效
            position = getattr(element, 'position', None)
            if not position or not hasattr(position, 'x') or not hasattr(position, 'y'):
                logger.warning(f"元素位置无效: {element.element_id}")
                return False

            return True

        except Exception as e:
            logger.error(f"验证元素有效性失败: {e}")
            return False

    def get_element_bounds_safely(self, element) -> dict:
        """安全地获取元素边界"""
        try:
            if not self.is_valid_element(element):
                return None

            position = element.position
            x, y = position.x, position.y

            # 根据元素类型确定大小
            width = height = 60  # 默认大小

            if hasattr(element, 'style') and element.style:
                style = element.style
                # 尝试从样式获取尺寸
                if hasattr(style, 'width') and style.width != 'auto':
                    try:
                        width = float(str(style.width).replace('px', ''))
                    except:
                        pass

                if hasattr(style, 'height') and style.height != 'auto':
                    try:
                        height = float(str(style.height).replace('px', ''))
                    except:
                        pass

            return {
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }

        except Exception as e:
            logger.error(f"获取元素边界失败: {e}")
            return None

    def point_in_bounds(self, x: float, y: float, bounds: dict) -> bool:
        """检查点是否在边界内"""
        try:
            return (bounds['x'] <= x <= bounds['x'] + bounds['width'] and
                    bounds['y'] <= y <= bounds['y'] + bounds['height'])
        except Exception as e:
            logger.error(f"边界检查失败: {e}")
            return False

    def select_element_safely(self, element_id: str):
        """安全地选择元素"""
        try:
            # 验证元素ID
            if not element_id or not isinstance(element_id, str):
                logger.warning(f"无效的元素ID: {element_id}")
                return

            # 检查元素是否存在
            if element_id not in self.elements:
                logger.warning(f"元素不存在: {element_id}")
                return

            # 检查元素是否有效
            element = self.elements[element_id]
            if not self.is_valid_element(element):
                logger.warning(f"元素无效，无法选择: {element_id}")
                return

            # 执行选择
            self.selected_element = element_id

            # 安全地发射信号
            try:
                self.element_selected.emit(element_id)
            except Exception as e:
                logger.error(f"发射元素选择信号失败: {e}")

            # 更新显示
            self.update()

            logger.info(f"成功选择元素: {element_id}")

        except Exception as e:
            logger.error(f"选择元素失败: {e}")

    def clear_selection_safely(self):
        """安全地清除选择"""
        try:
            if self.selected_element:
                logger.info(f"清除元素选择: {self.selected_element}")
                self.selected_element = None

                # 更新显示
                self.update()

        except Exception as e:
            logger.error(f"清除选择失败: {e}")

    def draw_smart_guides_safely(self, painter: QPainter, x: int, y: int, w: int, h: int):
        """安全地绘制智能参考线"""
        try:
            painter.setPen(QPen(QColor("#ff6b6b"), 1, Qt.PenStyle.DotLine))

            # 中心线
            center_x = x + w // 2
            center_y = y + h // 2

            # 垂直中心线
            painter.drawLine(center_x, 0, center_x, self.height())

            # 水平中心线
            painter.drawLine(0, center_y, self.width(), center_y)

            # 边界对齐线
            painter.drawLine(x, 0, x, self.height())  # 左边界
            painter.drawLine(x + w, 0, x + w, self.height())  # 右边界
            painter.drawLine(0, y, self.width(), y)  # 上边界
            painter.drawLine(0, y + h, self.width(), y + h)  # 下边界

        except Exception as e:
            logger.error(f"绘制智能参考线失败: {e}")

    def draw_alignment_hints_safely(self, painter: QPainter, x: int, y: int, w: int, h: int):
        """安全地绘制对齐提示"""
        try:
            # 设置字体
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)

            # 显示位置信息
            pos_text = f"位置: ({x}, {y})"
            size_text = f"尺寸: {w}×{h}"

            # 计算信息框位置
            info_x = min(x + w + 10, self.width() - 130)
            info_y = max(y, 10)
            info_rect = QRect(info_x, info_y, 120, 40)

            # 绘制信息背景
            painter.fillRect(info_rect, QColor(255, 255, 255, 200))
            painter.setPen(QPen(QColor("#cccccc")))
            painter.drawRect(info_rect)

            # 绘制文本
            painter.setPen(QPen(QColor("#333333")))
            painter.drawText(info_rect.adjusted(5, 5, -5, -20), pos_text)
            painter.drawText(info_rect.adjusted(5, 20, -5, -5), size_text)

        except Exception as e:
            logger.error(f"绘制对齐提示失败: {e}")

class StageWidget(QWidget):
    """舞台组件"""
    
    element_selected = pyqtSignal(str)  # 元素选择信号
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        
        # 添加一些示例元素
        self.add_sample_elements()
        
        logger.info("舞台组件初始化完成")

    # ==================== 导航器和标尺事件处理 ====================

    def on_navigator_viewport_changed(self, rect):
        """导航器视口改变事件"""
        try:
            # 更新舞台画布视口
            if hasattr(self, 'stage_canvas'):
                self.stage_canvas.update()
        except Exception as e:
            logger.error(f"处理导航器视口改变失败: {e}")

    def on_navigator_zoom_requested(self, scale):
        """导航器缩放请求事件"""
        try:
            if scale == -1:  # 适合窗口
                self.stage_canvas.zoom_to_fit()
            else:
                self.stage_canvas.set_scale_factor(scale)

            # 更新UI
            self.scale_slider.setValue(int(self.stage_canvas.scale_factor * 100))
            self.scale_label.setText(f"{int(self.stage_canvas.scale_factor * 100)}%")

        except Exception as e:
            logger.error(f"处理导航器缩放请求失败: {e}")

    def on_navigator_pan_requested(self, position):
        """导航器平移请求事件"""
        try:
            # 更新画布偏移
            self.stage_canvas.canvas_offset = position
            self.stage_canvas.update()

            # 更新标尺
            self.horizontal_ruler.set_offset(position.x())
            self.vertical_ruler.set_offset(position.y())

        except Exception as e:
            logger.error(f"处理导航器平移请求失败: {e}")

    def on_guide_added(self, orientation, position):
        """参考线添加事件"""
        try:
            self.guide_manager.add_guide(orientation, position)

            # 添加到画布
            if orientation == "horizontal":
                self.stage_canvas.horizontal_guides.append(position)
            else:
                self.stage_canvas.vertical_guides.append(position)

            self.stage_canvas.update()
            logger.debug(f"添加{orientation}参考线: {position}")

        except Exception as e:
            logger.error(f"处理参考线添加失败: {e}")

    def on_guide_visibility_changed(self, visible):
        """参考线可见性改变事件"""
        try:
            self.stage_canvas.guides_enabled = visible
            self.stage_canvas.update()
            logger.debug(f"参考线可见性设置为: {visible}")

        except Exception as e:
            logger.error(f"处理参考线可见性改变失败: {e}")

    def on_guide_removed(self, orientation, position):
        """参考线移除事件"""
        try:
            # 从画布移除
            if orientation == "horizontal" and position in self.stage_canvas.horizontal_guides:
                self.stage_canvas.horizontal_guides.remove(position)
            elif orientation == "vertical" and position in self.stage_canvas.vertical_guides:
                self.stage_canvas.vertical_guides.remove(position)

            # 从标尺移除
            if orientation == "horizontal":
                self.horizontal_ruler.remove_guide(position)
            else:
                self.vertical_ruler.remove_guide(position)

            self.stage_canvas.update()
            logger.debug(f"移除{orientation}参考线: {position}")

        except Exception as e:
            logger.error(f"处理参考线移除失败: {e}")

    def update_navigator_elements(self):
        """更新导航器中的元素显示"""
        try:
            if hasattr(self, 'navigator') and hasattr(self, 'stage_canvas'):
                self.navigator.set_elements(self.stage_canvas.elements)

        except Exception as e:
            logger.error(f"更新导航器元素失败: {e}")

    def sync_rulers_with_canvas(self):
        """同步标尺与画布"""
        try:
            if hasattr(self, 'stage_canvas'):
                scale = self.stage_canvas.scale_factor
                offset_x = self.stage_canvas.canvas_offset.x()
                offset_y = self.stage_canvas.canvas_offset.y()

                # 更新标尺
                self.horizontal_ruler.set_scale_factor(scale)
                self.horizontal_ruler.set_offset(offset_x)
                self.horizontal_ruler.set_canvas_size(self.stage_canvas.canvas_width)

                self.vertical_ruler.set_scale_factor(scale)
                self.vertical_ruler.set_offset(offset_y)
                self.vertical_ruler.set_canvas_size(self.stage_canvas.canvas_height)

                # 更新导航器
                self.navigator.set_scale_factor(scale)
                self.navigator.set_canvas_size(
                    self.stage_canvas.canvas_width,
                    self.stage_canvas.canvas_height
                )

        except Exception as e:
            logger.error(f"同步标尺与画布失败: {e}")
    
    def setup_ui(self):
        """设置用户界面 - 增强版"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 左侧面板（导航器和工具）
        left_panel = QWidget()
        left_panel.setMaximumWidth(260)
        left_panel_layout = QVBoxLayout(left_panel)

        # 画布导航器
        from .canvas_navigator import CanvasNavigator
        self.navigator = CanvasNavigator()
        self.navigator.viewport_changed.connect(self.on_navigator_viewport_changed)
        self.navigator.zoom_requested.connect(self.on_navigator_zoom_requested)
        self.navigator.pan_requested.connect(self.on_navigator_pan_requested)
        left_panel_layout.addWidget(self.navigator)

        # 参考线管理器
        from .ruler_guide_system import GuideManager
        self.guide_manager = GuideManager()
        self.guide_manager.guide_visibility_changed.connect(self.on_guide_visibility_changed)
        self.guide_manager.guide_removed.connect(self.on_guide_removed)
        left_panel_layout.addWidget(self.guide_manager)

        left_panel_layout.addStretch()
        main_layout.addWidget(left_panel)

        # 主要舞台区域
        stage_area = QWidget()
        stage_layout = QVBoxLayout(stage_area)
        stage_layout.setContentsMargins(0, 0, 0, 0)

        # 工具栏
        toolbar_group = QGroupBox("🎨 舞台工具")
        toolbar_layout = QHBoxLayout(toolbar_group)

        # 画布设置
        toolbar_layout.addWidget(QLabel("画布:"))
        self.canvas_size_combo = QComboBox()
        self.canvas_size_combo.addItems([
            "1920×1080 (Full HD)",
            "1280×720 (HD)",
            "800×600 (4:3)",
            "1024×768 (4:3)"
        ])
        toolbar_layout.addWidget(self.canvas_size_combo)

        # 缩放控制
        toolbar_layout.addWidget(QLabel("缩放:"))
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(10, 500)  # 扩大缩放范围
        self.scale_slider.setValue(40)
        self.scale_slider.setMaximumWidth(100)
        toolbar_layout.addWidget(self.scale_slider)

        self.scale_label = QLabel("40%")
        toolbar_layout.addWidget(self.scale_label)

        # 网格控制
        grid_layout = QHBoxLayout()
        self.grid_checkbox = QCheckBox("网格")
        self.grid_checkbox.setChecked(True)
        self.grid_settings_btn = QPushButton("⚙️")
        self.grid_settings_btn.setToolTip("网格设置")
        self.grid_settings_btn.setMaximumWidth(30)

        grid_layout.addWidget(self.grid_checkbox)
        grid_layout.addWidget(self.grid_settings_btn)
        toolbar_layout.addLayout(grid_layout)

        # 标尺控制
        self.ruler_checkbox = QCheckBox("标尺")
        self.ruler_checkbox.setChecked(True)
        toolbar_layout.addWidget(self.ruler_checkbox)

        toolbar_layout.addStretch()

        # 元素操作按钮
        self.add_text_btn = QPushButton("📝 添加文本")
        self.add_image_btn = QPushButton("🖼️ 添加图片")
        self.add_shape_btn = QPushButton("🔷 添加形状")

        toolbar_layout.addWidget(self.add_text_btn)
        toolbar_layout.addWidget(self.add_image_btn)
        toolbar_layout.addWidget(self.add_shape_btn)

        stage_layout.addWidget(toolbar_group)

        # 舞台画布区域（包含标尺）
        canvas_area = QWidget()
        canvas_layout = QVBoxLayout(canvas_area)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)

        # 顶部标尺区域
        top_ruler_area = QHBoxLayout()
        top_ruler_area.setContentsMargins(0, 0, 0, 0)
        top_ruler_area.setSpacing(0)

        # 左上角空白区域
        corner_widget = QWidget()
        corner_widget.setFixedSize(25, 25)
        corner_widget.setStyleSheet("background-color: #f0f0f0; border: 1px solid #c0c0c0;")
        top_ruler_area.addWidget(corner_widget)

        # 水平标尺
        from .ruler_guide_system import RulerWidget
        self.horizontal_ruler = RulerWidget("horizontal")
        self.horizontal_ruler.guide_added.connect(self.on_guide_added)
        top_ruler_area.addWidget(self.horizontal_ruler)

        canvas_layout.addLayout(top_ruler_area)

        # 主画布区域
        main_canvas_area = QHBoxLayout()
        main_canvas_area.setContentsMargins(0, 0, 0, 0)
        main_canvas_area.setSpacing(0)

        # 垂直标尺
        self.vertical_ruler = RulerWidget("vertical")
        self.vertical_ruler.guide_added.connect(self.on_guide_added)
        main_canvas_area.addWidget(self.vertical_ruler)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.stage_canvas = StageCanvas()
        scroll_area.setWidget(self.stage_canvas)

        main_canvas_area.addWidget(scroll_area)
        canvas_layout.addLayout(main_canvas_area)

        stage_layout.addWidget(canvas_area)
        main_layout.addWidget(stage_area)
    
    def setup_connections(self):
        """设置信号连接 - 增强版"""
        # 画布控制
        self.canvas_size_combo.currentTextChanged.connect(self.on_canvas_size_changed)
        self.scale_slider.valueChanged.connect(self.on_scale_changed)

        # 网格和标尺控制
        self.grid_checkbox.toggled.connect(self.on_grid_toggled)
        self.grid_settings_btn.clicked.connect(self.show_grid_settings)
        self.ruler_checkbox.toggled.connect(self.on_ruler_toggled)

        # 元素操作
        self.add_text_btn.clicked.connect(self.add_text_element)
        self.add_image_btn.clicked.connect(self.add_image_element)
        self.add_shape_btn.clicked.connect(self.add_shape_element)

        # 画布信号
        self.stage_canvas.element_selected.connect(self.element_selected.emit)
        self.stage_canvas.scale_changed.connect(self.on_canvas_scale_changed)

        # 同步更新
        self.stage_canvas.element_moved.connect(self.update_navigator_elements)

    def on_grid_toggled(self, enabled: bool):
        """网格显示切换"""
        try:
            self.stage_canvas.set_grid_enabled(enabled)
            logger.debug(f"网格显示设置为: {enabled}")
        except Exception as e:
            logger.error(f"切换网格显示失败: {e}")

    def on_ruler_toggled(self, enabled: bool):
        """标尺显示切换"""
        try:
            self.horizontal_ruler.setVisible(enabled)
            self.vertical_ruler.setVisible(enabled)
            logger.debug(f"标尺显示设置为: {enabled}")
        except Exception as e:
            logger.error(f"切换标尺显示失败: {e}")

    def show_grid_settings(self):
        """显示网格设置对话框"""
        try:
            from ui.grid_settings_dialog import GridSettingsDialog

            # 获取当前网格设置
            current_settings = self.stage_canvas.get_grid_settings()

            # 创建并显示对话框
            dialog = GridSettingsDialog(current_settings, self)
            dialog.settings_changed.connect(self.on_grid_settings_changed)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 应用最终设置
                final_settings = dialog.get_settings()
                self.stage_canvas.load_grid_settings(final_settings)

                # 更新网格复选框状态
                self.grid_checkbox.setChecked(final_settings.get("enabled", True))

                logger.info("网格设置已更新")

        except ImportError as e:
            logger.error(f"无法导入网格设置对话框: {e}")
            QMessageBox.warning(self, "错误", "网格设置对话框不可用")
        except Exception as e:
            logger.error(f"显示网格设置对话框失败: {e}")
            QMessageBox.critical(self, "错误", f"无法打开网格设置: {str(e)}")

    def on_grid_settings_changed(self, settings: dict):
        """网格设置改变处理"""
        try:
            # 应用预览设置
            self.stage_canvas.load_grid_settings(settings)

            # 更新网格复选框状态（但不触发信号）
            self.grid_checkbox.blockSignals(True)
            self.grid_checkbox.setChecked(settings.get("enabled", True))
            self.grid_checkbox.blockSignals(False)

            logger.debug("网格设置预览已应用")

        except Exception as e:
            logger.error(f"应用网格设置失败: {e}")

    def on_canvas_scale_changed(self, scale: float):
        """画布缩放改变事件"""
        try:
            # 同步标尺和导航器
            self.sync_rulers_with_canvas()

            # 更新UI
            self.scale_slider.setValue(int(scale * 100))
            self.scale_label.setText(f"{int(scale * 100)}%")

        except Exception as e:
            logger.error(f"处理画布缩放改变失败: {e}")
    
    def on_canvas_size_changed(self, size_text: str):
        """画布大小改变"""
        if "1920×1080" in size_text:
            self.stage_canvas.set_canvas_size(1920, 1080)
        elif "1280×720" in size_text:
            self.stage_canvas.set_canvas_size(1280, 720)
        elif "800×600" in size_text:
            self.stage_canvas.set_canvas_size(800, 600)
        elif "1024×768" in size_text:
            self.stage_canvas.set_canvas_size(1024, 768)
    
    def on_scale_changed(self, value: int):
        """缩放改变"""
        scale = value / 100.0
        self.stage_canvas.set_scale_factor(scale)
        self.scale_label.setText(f"{value}%")
    
    def add_text_element(self):
        """添加文本元素"""
        from core.data_structures import ElementType
        element = Element(
            name="文本元素",
            element_type=ElementType.TEXT,
            content="示例文本",
            position=Point(100, 100)
        )
        self.stage_canvas.add_element(element)
        logger.info(f"添加文本元素: {element.element_id}")
    
    def add_image_element(self):
        """添加图片元素"""
        from core.data_structures import ElementType
        element = Element(
            name="图片元素",
            element_type=ElementType.IMAGE,
            content="image.png",
            position=Point(200, 150)
        )
        self.stage_canvas.add_element(element)
        logger.info(f"添加图片元素: {element.element_id}")
    
    def add_shape_element(self):
        """添加形状元素"""
        from core.data_structures import ElementType
        element = Element(
            name="形状元素",
            element_type=ElementType.SHAPE,
            content="rectangle",
            position=Point(300, 200)
        )
        self.stage_canvas.add_element(element)
        logger.info(f"添加形状元素: {element.element_id}")
    
    def add_sample_elements(self):
        """添加示例元素"""
        from core.data_structures import ElementType
        
        # 标题文本
        title = Element(
            name="标题",
            element_type=ElementType.TEXT,
            content="AI Animation Studio",
            position=Point(400, 50)
        )
        self.stage_canvas.add_element(title)
        
        # 示例图片
        image = Element(
            name="Logo",
            element_type=ElementType.IMAGE,
            content="logo.png",
            position=Point(100, 200)
        )
        self.stage_canvas.add_element(image)
        
        # 示例形状
        shape = Element(
            name="背景",
            element_type=ElementType.SHAPE,
            content="circle",
            position=Point(600, 300)
        )
        self.stage_canvas.add_element(shape)

    # ========== 完整的鼠标事件处理 ==========

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        try:
            pos = event.position()
            x, y = pos.x(), pos.y()

            # 如果正在拖拽元素
            if hasattr(self, '_dragging') and self._dragging and hasattr(self, '_selected_element'):
                self.handle_element_drag(x, y)

            # 如果正在拖拽选择框
            elif hasattr(self, '_selection_dragging') and self._selection_dragging:
                self.handle_selection_drag(x, y)

            # 更新鼠标位置信息
            self.update_mouse_position(x, y)

            super().mouseMoveEvent(event)

        except Exception as e:
            logger.error(f"鼠标移动事件处理失败: {e}")

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                # 结束拖拽操作
                if hasattr(self, '_dragging'):
                    self._dragging = False

                if hasattr(self, '_selection_dragging'):
                    self._selection_dragging = False
                    self.complete_selection_drag()

            super().mouseReleaseEvent(event)

        except Exception as e:
            logger.error(f"鼠标释放事件处理失败: {e}")

    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                pos = event.position()
                x, y = pos.x(), pos.y()

                # 查找双击的元素
                clicked_element = self.find_element_at_position(x, y)

                if clicked_element:
                    # 双击元素进入编辑模式
                    self.enter_edit_mode(clicked_element)
                else:
                    # 双击空白区域添加新元素
                    self.add_element_at_position(x, y)

            super().mouseDoubleClickEvent(event)

        except Exception as e:
            logger.error(f"鼠标双击事件处理失败: {e}")

    def wheelEvent(self, event):
        """鼠标滚轮事件"""
        try:
            delta = event.angleDelta().y()

            # Ctrl + 滚轮：缩放画布
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                if delta > 0:
                    self.zoom_in()
                else:
                    self.zoom_out()
            # Shift + 滚轮：水平滚动
            elif event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.scroll_horizontal(delta)
            # 普通滚轮：垂直滚动
            else:
                self.scroll_vertical(delta)

            super().wheelEvent(event)

        except Exception as e:
            logger.error(f"滚轮事件处理失败: {e}")

    def contextMenuEvent(self, event):
        """右键菜单事件"""
        try:
            pos = event.pos()
            clicked_element = self.find_element_at_position(pos.x(), pos.y())

            self.show_context_menu(event.globalPos(), clicked_element)

        except Exception as e:
            logger.error(f"右键菜单事件处理失败: {e}")

    def handle_element_drag(self, x: float, y: float):
        """处理元素拖拽"""
        try:
            if hasattr(self, '_drag_start_pos') and hasattr(self, '_selected_element'):
                # 计算拖拽偏移
                delta_x = x - self._drag_start_pos[0]
                delta_y = y - self._drag_start_pos[1]

                # 更新元素位置
                self.move_element(self._selected_element, delta_x, delta_y)

                # 更新拖拽起始位置
                self._drag_start_pos = (x, y)

                # 重绘画布
                self.update()

        except Exception as e:
            logger.error(f"元素拖拽处理失败: {e}")

    def handle_selection_drag(self, x: float, y: float):
        """处理选择框拖拽"""
        try:
            if hasattr(self, '_selection_start_pos'):
                # 更新选择框
                self._selection_end_pos = (x, y)
                self.update()

        except Exception as e:
            logger.error(f"选择框拖拽处理失败: {e}")

    def complete_selection_drag(self):
        """完成选择框拖拽"""
        try:
            if hasattr(self, '_selection_start_pos') and hasattr(self, '_selection_end_pos'):
                # 计算选择区域
                start_x, start_y = self._selection_start_pos
                end_x, end_y = self._selection_end_pos

                # 查找选择区域内的元素
                selected_elements = self.find_elements_in_rect(
                    min(start_x, end_x), min(start_y, end_y),
                    abs(end_x - start_x), abs(end_y - start_y)
                )

                # 选择这些元素
                self.select_multiple_elements(selected_elements)

                # 清除选择框
                delattr(self, '_selection_start_pos')
                delattr(self, '_selection_end_pos')

        except Exception as e:
            logger.error(f"完成选择框拖拽失败: {e}")

    def update_mouse_position(self, x: float, y: float):
        """更新鼠标位置信息"""
        try:
            # 转换为画布坐标
            canvas_x = x / self.scale_factor
            canvas_y = y / self.scale_factor

            # 更新工具提示
            self.setToolTip(f"位置: ({canvas_x:.0f}, {canvas_y:.0f})")

            # 发射位置变化信号
            if hasattr(self, 'mouse_position_changed'):
                self.mouse_position_changed.emit(canvas_x, canvas_y)

        except Exception as e:
            logger.error(f"更新鼠标位置失败: {e}")

    def enter_edit_mode(self, element_id: str):
        """进入元素编辑模式"""
        try:
            logger.info(f"进入编辑模式: {element_id}")
            # TODO: 实现元素编辑模式

        except Exception as e:
            logger.error(f"进入编辑模式失败: {e}")

    def add_element_at_position(self, x: float, y: float):
        """在指定位置添加元素"""
        try:
            # 转换为画布坐标
            canvas_x = x / self.scale_factor
            canvas_y = y / self.scale_factor

            logger.info(f"在位置 ({canvas_x:.0f}, {canvas_y:.0f}) 添加元素")
            # TODO: 实现元素添加逻辑

        except Exception as e:
            logger.error(f"添加元素失败: {e}")

    def zoom_in(self):
        """放大画布"""
        try:
            self.scale_factor = min(self.scale_factor * 1.2, 5.0)
            self.update()
            logger.info(f"放大画布: {self.scale_factor:.1f}x")

        except Exception as e:
            logger.error(f"放大画布失败: {e}")

    def zoom_out(self):
        """缩小画布"""
        try:
            self.scale_factor = max(self.scale_factor / 1.2, 0.1)
            self.update()
            logger.info(f"缩小画布: {self.scale_factor:.1f}x")

        except Exception as e:
            logger.error(f"缩小画布失败: {e}")

    def scroll_horizontal(self, delta: int):
        """水平滚动"""
        try:
            # TODO: 实现水平滚动逻辑
            logger.info(f"水平滚动: {delta}")

        except Exception as e:
            logger.error(f"水平滚动失败: {e}")

    def scroll_vertical(self, delta: int):
        """垂直滚动"""
        try:
            # TODO: 实现垂直滚动逻辑
            logger.info(f"垂直滚动: {delta}")

        except Exception as e:
            logger.error(f"垂直滚动失败: {e}")

    def show_context_menu(self, global_pos, element_id: str = None):
        """显示上下文菜单"""
        try:
            from PyQt6.QtWidgets import QMenu

            menu = QMenu(self)

            if element_id:
                # 元素相关菜单
                edit_action = menu.addAction("编辑元素")
                edit_action.triggered.connect(lambda: self.enter_edit_mode(element_id))

                copy_action = menu.addAction("复制元素")
                copy_action.triggered.connect(lambda: self.copy_element(element_id))

                delete_action = menu.addAction("删除元素")
                delete_action.triggered.connect(lambda: self.delete_element(element_id))

                menu.addSeparator()

                # 层级控制
                bring_front_action = menu.addAction("置于顶层")
                bring_front_action.triggered.connect(lambda: self.bring_to_front(element_id))

                send_back_action = menu.addAction("置于底层")
                send_back_action.triggered.connect(lambda: self.send_to_back(element_id))
            else:
                # 画布相关菜单
                add_text_action = menu.addAction("添加文本")
                add_text_action.triggered.connect(self.add_text_element)

                add_shape_action = menu.addAction("添加形状")
                add_shape_action.triggered.connect(self.add_shape_element)

                add_image_action = menu.addAction("添加图片")
                add_image_action.triggered.connect(self.add_image_element)

                menu.addSeparator()

                paste_action = menu.addAction("粘贴")
                paste_action.triggered.connect(self.paste_element)

            menu.addSeparator()

            # 视图控制
            zoom_in_action = menu.addAction("放大")
            zoom_in_action.triggered.connect(self.zoom_in)

            zoom_out_action = menu.addAction("缩小")
            zoom_out_action.triggered.connect(self.zoom_out)

            reset_zoom_action = menu.addAction("重置缩放")
            reset_zoom_action.triggered.connect(self.reset_zoom)

            menu.exec(global_pos)

        except Exception as e:
            logger.error(f"显示上下文菜单失败: {e}")

    def find_elements_in_rect(self, x: float, y: float, width: float, height: float) -> List[str]:
        """查找矩形区域内的元素"""
        try:
            selected_elements = []

            for element_id, element in self.elements.items():
                if not self.is_valid_element(element):
                    continue

                # 获取元素边界
                bounds = self.get_element_bounds_safely(element)
                if bounds:
                    # 检查是否与选择区域相交
                    if self.rect_intersects(bounds, (x, y, width, height)):
                        selected_elements.append(element_id)

            return selected_elements

        except Exception as e:
            logger.error(f"查找矩形区域内元素失败: {e}")
            return []

    def rect_intersects(self, rect1, rect2) -> bool:
        """检查两个矩形是否相交"""
        try:
            # rect1: (x, y, width, height)
            # rect2: (x, y, width, height)
            x1, y1, w1, h1 = rect1
            x2, y2, w2, h2 = rect2

            return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

        except Exception as e:
            logger.error(f"矩形相交检测失败: {e}")
            return False

    def select_multiple_elements(self, element_ids: List[str]):
        """选择多个元素"""
        try:
            self.selected_elements = element_ids
            self.update()
            logger.info(f"选择了 {len(element_ids)} 个元素")

        except Exception as e:
            logger.error(f"选择多个元素失败: {e}")

    def copy_element(self, element_id: str):
        """复制元素"""
        try:
            logger.info(f"复制元素: {element_id}")
            # TODO: 实现元素复制逻辑

        except Exception as e:
            logger.error(f"复制元素失败: {e}")

    def delete_element(self, element_id: str):
        """删除元素"""
        try:
            if element_id in self.elements:
                del self.elements[element_id]
                self.update()
                logger.info(f"删除元素: {element_id}")

        except Exception as e:
            logger.error(f"删除元素失败: {e}")

    def bring_to_front(self, element_id: str):
        """置于顶层"""
        try:
            logger.info(f"置于顶层: {element_id}")
            # TODO: 实现层级控制逻辑

        except Exception as e:
            logger.error(f"置于顶层失败: {e}")

    def send_to_back(self, element_id: str):
        """置于底层"""
        try:
            logger.info(f"置于底层: {element_id}")
            # TODO: 实现层级控制逻辑

        except Exception as e:
            logger.error(f"置于底层失败: {e}")

    def add_text_element(self):
        """添加文本元素"""
        try:
            logger.info("添加文本元素")
            # TODO: 实现文本元素添加逻辑

        except Exception as e:
            logger.error(f"添加文本元素失败: {e}")

    def add_shape_element(self):
        """添加形状元素"""
        try:
            logger.info("添加形状元素")
            # TODO: 实现形状元素添加逻辑

        except Exception as e:
            logger.error(f"添加形状元素失败: {e}")

    def add_image_element(self):
        """添加图片元素"""
        try:
            logger.info("添加图片元素")
            # TODO: 实现图片元素添加逻辑

        except Exception as e:
            logger.error(f"添加图片元素失败: {e}")

    def paste_element(self):
        """粘贴元素"""
        try:
            logger.info("粘贴元素")
            # TODO: 实现元素粘贴逻辑

        except Exception as e:
            logger.error(f"粘贴元素失败: {e}")

    def reset_zoom(self):
        """重置缩放"""
        try:
            self.scale_factor = 1.0
            self.update()
            logger.info("重置缩放")

        except Exception as e:
            logger.error(f"重置缩放失败: {e}")

    def move_element(self, element_id: str, delta_x: float, delta_y: float):
        """移动元素"""
        try:
            if element_id in self.elements:
                element = self.elements[element_id]
                if hasattr(element, 'position'):
                    element.position.x += delta_x / self.scale_factor
                    element.position.y += delta_y / self.scale_factor
                    logger.info(f"移动元素 {element_id}: ({delta_x:.1f}, {delta_y:.1f})")

        except Exception as e:
            logger.error(f"移动元素失败: {e}")
