"""
AI Animation Studio - 高级颜色选择器
提供专业的颜色选择功能，支持渐变色、调色板等
"""

import colorsys
from typing import Optional, List, Tuple, Callable
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QSlider, QSpinBox, QLineEdit, QTabWidget, QWidget, QColorDialog,
    QListWidget, QListWidgetItem, QGroupBox, QComboBox, QCheckBox,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QLinearGradient, QRadialGradient,
    QConicalGradient, QPixmap, QFont, QPalette
)

from core.logger import get_logger

logger = get_logger("advanced_color_picker")


class ColorWheel(QWidget):
    """颜色轮控件"""
    
    color_changed = pyqtSignal(QColor)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.current_color = QColor(255, 0, 0)
        self.wheel_radius = 80
        self.triangle_radius = 60
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # 绘制色相环
        self.draw_hue_wheel(painter, center_x, center_y)
        
        # 绘制饱和度-亮度三角形
        self.draw_sv_triangle(painter, center_x, center_y)
        
        # 绘制当前颜色指示器
        self.draw_color_indicator(painter, center_x, center_y)
    
    def draw_hue_wheel(self, painter, center_x, center_y):
        """绘制色相环"""
        for angle in range(360):
            color = QColor.fromHsv(angle, 255, 255)
            painter.setPen(QPen(color, 2))
            
            x1 = center_x + (self.wheel_radius - 10) * colorsys.cos(colorsys.radians(angle))
            y1 = center_y + (self.wheel_radius - 10) * colorsys.sin(colorsys.radians(angle))
            x2 = center_x + self.wheel_radius * colorsys.cos(colorsys.radians(angle))
            y2 = center_y + self.wheel_radius * colorsys.sin(colorsys.radians(angle))
            
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
    
    def draw_sv_triangle(self, painter, center_x, center_y):
        """绘制饱和度-亮度三角形"""
        # 简化实现，绘制一个渐变矩形
        rect_size = self.triangle_radius
        rect_x = center_x - rect_size // 2
        rect_y = center_y - rect_size // 2
        
        # 创建饱和度-亮度渐变
        gradient = QLinearGradient(rect_x, rect_y, rect_x + rect_size, rect_y + rect_size)
        gradient.setColorAt(0, QColor(255, 255, 255))
        gradient.setColorAt(1, QColor(self.current_color.hue(), 255, 255, QColor.Spec.Hsv))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect_x, rect_y, rect_size, rect_size)
    
    def draw_color_indicator(self, painter, center_x, center_y):
        """绘制当前颜色指示器"""
        painter.setBrush(QBrush(self.current_color))
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawEllipse(center_x - 8, center_y - 8, 16, 16)


class GradientEditor(QWidget):
    """渐变编辑器"""
    
    gradient_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gradient_stops = [(0.0, QColor(255, 0, 0)), (1.0, QColor(0, 0, 255))]
        self.gradient_type = "linear"
        self.setMinimumHeight(60)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 绘制渐变预览
        if self.gradient_type == "linear":
            gradient = QLinearGradient(0, 0, self.width(), 0)
        elif self.gradient_type == "radial":
            gradient = QRadialGradient(self.width()//2, self.height()//2, self.width()//2)
        else:  # conical
            gradient = QConicalGradient(self.width()//2, self.height()//2, 0)
        
        for position, color in self.gradient_stops:
            gradient.setColorAt(position, color)
        
        painter.setBrush(QBrush(gradient))
        painter.drawRect(0, 0, self.width(), self.height() - 20)
        
        # 绘制停止点
        for position, color in self.gradient_stops:
            x = int(position * self.width())
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawRect(x - 5, self.height() - 20, 10, 20)


class ColorPalette(QWidget):
    """调色板"""
    
    color_selected = pyqtSignal(QColor)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors = []
        self.load_default_palette()
        self.setMinimumHeight(100)
        
    def load_default_palette(self):
        """加载默认调色板"""
        # 基础颜色
        basic_colors = [
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",
            "#000000", "#FFFFFF", "#808080", "#800000", "#008000", "#000080",
            "#808000", "#800080", "#008080", "#C0C0C0", "#FFA500", "#A52A2A"
        ]
        
        # 材质设计调色板
        material_colors = [
            "#F44336", "#E91E63", "#9C27B0", "#673AB7", "#3F51B5", "#2196F3",
            "#03A9F4", "#00BCD4", "#009688", "#4CAF50", "#8BC34A", "#CDDC39",
            "#FFEB3B", "#FFC107", "#FF9800", "#FF5722", "#795548", "#9E9E9E"
        ]
        
        self.colors = [QColor(color) for color in basic_colors + material_colors]
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        cols = 6
        cell_width = self.width() // cols
        cell_height = 20
        
        for i, color in enumerate(self.colors):
            row = i // cols
            col = i % cols
            
            x = col * cell_width
            y = row * cell_height
            
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.GlobalColor.gray, 1))
            painter.drawRect(x, y, cell_width, cell_height)
    
    def mousePressEvent(self, event):
        cols = 6
        cell_width = self.width() // cols
        cell_height = 20
        
        col = event.position().x() // cell_width
        row = event.position().y() // cell_height
        index = int(row * cols + col)
        
        if 0 <= index < len(self.colors):
            self.color_selected.emit(self.colors[index])


class AdvancedColorPicker(QDialog):
    """高级颜色选择器对话框"""
    
    def __init__(self, parent=None, initial_color=QColor(255, 255, 255)):
        super().__init__(parent)
        self.current_color = initial_color
        self.gradient_data = None
        
        self.setWindowTitle("高级颜色选择器")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
        self.setup_ui()
        self.update_color_display()
        
        logger.info("高级颜色选择器初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 颜色选择标签页
        self.setup_color_tab()
        
        # 渐变标签页
        self.setup_gradient_tab()
        
        # 调色板标签页
        self.setup_palette_tab()
        
        layout.addWidget(self.tab_widget)
        
        # 当前颜色显示
        color_display_layout = QHBoxLayout()
        
        # 颜色预览
        self.color_preview = QFrame()
        self.color_preview.setMinimumSize(100, 50)
        self.color_preview.setFrameStyle(QFrame.Shape.StyledPanel)
        color_display_layout.addWidget(self.color_preview)
        
        # 颜色值显示
        color_values_layout = QVBoxLayout()
        
        # RGB值
        rgb_layout = QHBoxLayout()
        rgb_layout.addWidget(QLabel("RGB:"))
        self.rgb_edit = QLineEdit()
        self.rgb_edit.setReadOnly(True)
        rgb_layout.addWidget(self.rgb_edit)
        color_values_layout.addLayout(rgb_layout)
        
        # HEX值
        hex_layout = QHBoxLayout()
        hex_layout.addWidget(QLabel("HEX:"))
        self.hex_edit = QLineEdit()
        self.hex_edit.textChanged.connect(self.on_hex_changed)
        hex_layout.addWidget(self.hex_edit)
        color_values_layout.addLayout(hex_layout)
        
        # HSV值
        hsv_layout = QHBoxLayout()
        hsv_layout.addWidget(QLabel("HSV:"))
        self.hsv_edit = QLineEdit()
        self.hsv_edit.setReadOnly(True)
        hsv_layout.addWidget(self.hsv_edit)
        color_values_layout.addLayout(hsv_layout)
        
        color_display_layout.addLayout(color_values_layout)
        
        layout.addLayout(color_display_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        # 系统颜色选择器
        system_picker_btn = QPushButton("系统选择器")
        system_picker_btn.clicked.connect(self.open_system_picker)
        button_layout.addWidget(system_picker_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("确定")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def setup_color_tab(self):
        """设置颜色选择标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # 颜色轮
        self.color_wheel = ColorWheel()
        self.color_wheel.color_changed.connect(self.on_color_changed)
        layout.addWidget(self.color_wheel)
        
        # 颜色调整控件
        controls_layout = QVBoxLayout()
        
        # RGB滑块
        rgb_group = QGroupBox("RGB")
        rgb_layout = QVBoxLayout(rgb_group)
        
        # R滑块
        r_layout = QHBoxLayout()
        r_layout.addWidget(QLabel("R:"))
        self.r_slider = QSlider(Qt.Orientation.Horizontal)
        self.r_slider.setRange(0, 255)
        self.r_slider.valueChanged.connect(self.on_rgb_changed)
        r_layout.addWidget(self.r_slider)
        self.r_spin = QSpinBox()
        self.r_spin.setRange(0, 255)
        self.r_spin.valueChanged.connect(self.on_rgb_changed)
        r_layout.addWidget(self.r_spin)
        rgb_layout.addLayout(r_layout)
        
        # G滑块
        g_layout = QHBoxLayout()
        g_layout.addWidget(QLabel("G:"))
        self.g_slider = QSlider(Qt.Orientation.Horizontal)
        self.g_slider.setRange(0, 255)
        self.g_slider.valueChanged.connect(self.on_rgb_changed)
        g_layout.addWidget(self.g_slider)
        self.g_spin = QSpinBox()
        self.g_spin.setRange(0, 255)
        self.g_spin.valueChanged.connect(self.on_rgb_changed)
        g_layout.addWidget(self.g_spin)
        rgb_layout.addLayout(g_layout)
        
        # B滑块
        b_layout = QHBoxLayout()
        b_layout.addWidget(QLabel("B:"))
        self.b_slider = QSlider(Qt.Orientation.Horizontal)
        self.b_slider.setRange(0, 255)
        self.b_slider.valueChanged.connect(self.on_rgb_changed)
        b_layout.addWidget(self.b_slider)
        self.b_spin = QSpinBox()
        self.b_spin.setRange(0, 255)
        self.b_spin.valueChanged.connect(self.on_rgb_changed)
        b_layout.addWidget(self.b_spin)
        rgb_layout.addLayout(b_layout)
        
        controls_layout.addWidget(rgb_group)
        
        # HSV滑块
        hsv_group = QGroupBox("HSV")
        hsv_layout = QVBoxLayout(hsv_group)
        
        # H滑块
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("H:"))
        self.h_slider = QSlider(Qt.Orientation.Horizontal)
        self.h_slider.setRange(0, 359)
        self.h_slider.valueChanged.connect(self.on_hsv_changed)
        h_layout.addWidget(self.h_slider)
        self.h_spin = QSpinBox()
        self.h_spin.setRange(0, 359)
        self.h_spin.valueChanged.connect(self.on_hsv_changed)
        h_layout.addWidget(self.h_spin)
        hsv_layout.addLayout(h_layout)
        
        # S滑块
        s_layout = QHBoxLayout()
        s_layout.addWidget(QLabel("S:"))
        self.s_slider = QSlider(Qt.Orientation.Horizontal)
        self.s_slider.setRange(0, 255)
        self.s_slider.valueChanged.connect(self.on_hsv_changed)
        s_layout.addWidget(self.s_slider)
        self.s_spin = QSpinBox()
        self.s_spin.setRange(0, 255)
        self.s_spin.valueChanged.connect(self.on_hsv_changed)
        s_layout.addWidget(self.s_spin)
        hsv_layout.addLayout(s_layout)
        
        # V滑块
        v_layout = QHBoxLayout()
        v_layout.addWidget(QLabel("V:"))
        self.v_slider = QSlider(Qt.Orientation.Horizontal)
        self.v_slider.setRange(0, 255)
        self.v_slider.valueChanged.connect(self.on_hsv_changed)
        v_layout.addWidget(self.v_slider)
        self.v_spin = QSpinBox()
        self.v_spin.setRange(0, 255)
        self.v_spin.valueChanged.connect(self.on_hsv_changed)
        v_layout.addWidget(self.v_spin)
        hsv_layout.addLayout(v_layout)
        
        controls_layout.addWidget(hsv_group)
        
        # Alpha滑块
        alpha_group = QGroupBox("透明度")
        alpha_layout = QHBoxLayout(alpha_group)
        alpha_layout.addWidget(QLabel("Alpha:"))
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(0, 255)
        self.alpha_slider.setValue(255)
        self.alpha_slider.valueChanged.connect(self.on_alpha_changed)
        alpha_layout.addWidget(self.alpha_slider)
        self.alpha_spin = QSpinBox()
        self.alpha_spin.setRange(0, 255)
        self.alpha_spin.setValue(255)
        self.alpha_spin.valueChanged.connect(self.on_alpha_changed)
        alpha_layout.addWidget(self.alpha_spin)
        controls_layout.addWidget(alpha_group)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        self.tab_widget.addTab(tab, "颜色")
    
    def setup_gradient_tab(self):
        """设置渐变标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 渐变类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("渐变类型:"))
        self.gradient_type_combo = QComboBox()
        self.gradient_type_combo.addItems(["线性渐变", "径向渐变", "角度渐变"])
        type_layout.addWidget(self.gradient_type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # 渐变编辑器
        self.gradient_editor = GradientEditor()
        layout.addWidget(self.gradient_editor)
        
        # 渐变控制
        gradient_controls = QHBoxLayout()
        
        add_stop_btn = QPushButton("添加停止点")
        add_stop_btn.clicked.connect(self.add_gradient_stop)
        gradient_controls.addWidget(add_stop_btn)
        
        remove_stop_btn = QPushButton("删除停止点")
        remove_stop_btn.clicked.connect(self.remove_gradient_stop)
        gradient_controls.addWidget(remove_stop_btn)
        
        gradient_controls.addStretch()
        
        layout.addLayout(gradient_controls)
        
        # 预设渐变
        presets_group = QGroupBox("预设渐变")
        presets_layout = QGridLayout(presets_group)
        
        gradient_presets = [
            ("红到蓝", [(0, QColor(255, 0, 0)), (1, QColor(0, 0, 255))]),
            ("彩虹", [(0, QColor(255, 0, 0)), (0.33, QColor(0, 255, 0)), (0.66, QColor(0, 0, 255)), (1, QColor(255, 0, 255))]),
            ("日落", [(0, QColor(255, 94, 77)), (1, QColor(255, 154, 0))]),
            ("海洋", [(0, QColor(0, 119, 190)), (1, QColor(0, 180, 216))]),
        ]
        
        for i, (name, stops) in enumerate(gradient_presets):
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, s=stops: self.apply_gradient_preset(s))
            presets_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addWidget(presets_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "渐变")
    
    def setup_palette_tab(self):
        """设置调色板标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 调色板
        self.color_palette = ColorPalette()
        self.color_palette.color_selected.connect(self.on_color_changed)
        layout.addWidget(self.color_palette)
        
        # 最近使用的颜色
        recent_group = QGroupBox("最近使用")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_colors = QListWidget()
        self.recent_colors.setMaximumHeight(60)
        self.recent_colors.setFlow(QListWidget.Flow.LeftToRight)
        recent_layout.addWidget(self.recent_colors)
        
        layout.addWidget(recent_group)
        
        # 自定义调色板
        custom_group = QGroupBox("自定义调色板")
        custom_layout = QVBoxLayout(custom_group)
        
        custom_controls = QHBoxLayout()
        add_color_btn = QPushButton("添加当前颜色")
        add_color_btn.clicked.connect(self.add_to_custom_palette)
        custom_controls.addWidget(add_color_btn)
        
        save_palette_btn = QPushButton("保存调色板")
        save_palette_btn.clicked.connect(self.save_custom_palette)
        custom_controls.addWidget(save_palette_btn)
        
        load_palette_btn = QPushButton("加载调色板")
        load_palette_btn.clicked.connect(self.load_custom_palette)
        custom_controls.addWidget(load_palette_btn)
        
        custom_layout.addLayout(custom_controls)
        
        self.custom_palette = QListWidget()
        self.custom_palette.setMaximumHeight(100)
        self.custom_palette.setFlow(QListWidget.Flow.LeftToRight)
        custom_layout.addWidget(self.custom_palette)
        
        layout.addWidget(custom_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "调色板")
    
    def on_color_changed(self, color):
        """颜色改变事件"""
        self.current_color = color
        self.update_color_display()
        self.update_sliders()
    
    def on_rgb_changed(self):
        """RGB值改变事件"""
        r = self.r_slider.value()
        g = self.g_slider.value()
        b = self.b_slider.value()
        
        self.current_color = QColor(r, g, b, self.current_color.alpha())
        self.update_color_display()
        
        # 同步数值框
        self.r_spin.setValue(r)
        self.g_spin.setValue(g)
        self.b_spin.setValue(b)
    
    def on_hsv_changed(self):
        """HSV值改变事件"""
        h = self.h_slider.value()
        s = self.s_slider.value()
        v = self.v_slider.value()
        
        self.current_color = QColor.fromHsv(h, s, v, self.current_color.alpha())
        self.update_color_display()
        
        # 同步数值框
        self.h_spin.setValue(h)
        self.s_spin.setValue(s)
        self.v_spin.setValue(v)
    
    def on_alpha_changed(self):
        """透明度改变事件"""
        alpha = self.alpha_slider.value()
        self.current_color.setAlpha(alpha)
        self.update_color_display()
        self.alpha_spin.setValue(alpha)
    
    def on_hex_changed(self, hex_text):
        """HEX值改变事件"""
        try:
            if hex_text.startswith('#') and len(hex_text) == 7:
                color = QColor(hex_text)
                if color.isValid():
                    self.current_color = color
                    self.update_color_display()
                    self.update_sliders()
        except:
            pass
    
    def update_color_display(self):
        """更新颜色显示"""
        # 更新预览
        palette = self.color_preview.palette()
        palette.setColor(QPalette.ColorRole.Window, self.current_color)
        self.color_preview.setPalette(palette)
        self.color_preview.setAutoFillBackground(True)
        
        # 更新颜色值显示
        self.rgb_edit.setText(f"rgb({self.current_color.red()}, {self.current_color.green()}, {self.current_color.blue()})")
        self.hex_edit.setText(self.current_color.name().upper())
        self.hsv_edit.setText(f"hsv({self.current_color.hue()}, {self.current_color.saturation()}, {self.current_color.value()})")
    
    def update_sliders(self):
        """更新滑块值"""
        # RGB滑块
        self.r_slider.setValue(self.current_color.red())
        self.g_slider.setValue(self.current_color.green())
        self.b_slider.setValue(self.current_color.blue())
        
        # HSV滑块
        self.h_slider.setValue(self.current_color.hue())
        self.s_slider.setValue(self.current_color.saturation())
        self.v_slider.setValue(self.current_color.value())
        
        # Alpha滑块
        self.alpha_slider.setValue(self.current_color.alpha())
    
    def open_system_picker(self):
        """打开系统颜色选择器"""
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.on_color_changed(color)
    
    def add_gradient_stop(self):
        """添加渐变停止点"""
        # 简化实现
        pass
    
    def remove_gradient_stop(self):
        """删除渐变停止点"""
        # 简化实现
        pass
    
    def apply_gradient_preset(self, stops):
        """应用渐变预设"""
        self.gradient_editor.gradient_stops = stops
        self.gradient_editor.update()
    
    def add_to_custom_palette(self):
        """添加到自定义调色板"""
        # 简化实现
        pass
    
    def save_custom_palette(self):
        """保存自定义调色板"""
        # 简化实现
        pass
    
    def load_custom_palette(self):
        """加载自定义调色板"""
        # 简化实现
        pass
    
    def get_selected_color(self):
        """获取选中的颜色"""
        return self.current_color
    
    def get_gradient_data(self):
        """获取渐变数据"""
        if self.tab_widget.currentIndex() == 1:  # 渐变标签页
            return {
                'type': 'gradient',
                'gradient_type': self.gradient_type_combo.currentText(),
                'stops': self.gradient_editor.gradient_stops
            }
        return None
