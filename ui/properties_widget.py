"""
AI Animation Studio - 属性面板组件
提供元素属性编辑功能
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QSlider,
    QColorDialog, QTextEdit, QFormLayout, QTabWidget, QScrollArea,
    QFrame, QSplitter, QMenu, QMessageBox, QProgressBar, QToolButton,
    QButtonGroup, QRadioButton, QFontComboBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QPixmap, QPainter, QAction

from core.data_structures import Element, ElementType, Transform, ElementStyle
from core.logger import get_logger

logger = get_logger("properties_widget")

class ColorButton(QPushButton):
    """颜色选择按钮"""

    color_changed = pyqtSignal(str)  # 颜色改变信号

    def __init__(self, color: str = "#000000"):
        super().__init__()
        self.current_color = color
        self.setMaximumWidth(50)
        self.setMaximumHeight(30)
        self.clicked.connect(self.choose_color)
        self.update_button_color()

    def choose_color(self):
        """选择颜色"""
        color = QColorDialog.getColor(QColor(self.current_color), self)
        if color.isValid():
            self.current_color = color.name()
            self.update_button_color()
            self.color_changed.emit(self.current_color)

    def update_button_color(self):
        """更新按钮颜色"""
        self.setStyleSheet(f"background-color: {self.current_color}; border: 1px solid #ccc;")

    def set_color(self, color: str):
        """设置颜色"""
        self.current_color = color
        self.update_button_color()


class AdvancedColorButton(QPushButton):
    """高级颜色选择按钮"""

    color_changed = pyqtSignal(str)  # 颜色改变信号
    gradient_changed = pyqtSignal(dict)  # 渐变改变信号

    def __init__(self, color: str = "#000000", tooltip: str = ""):
        super().__init__()
        self.current_color = color
        self.gradient_data = None
        self.setMaximumWidth(60)
        self.setMaximumHeight(35)
        self.setToolTip(tooltip)
        self.clicked.connect(self.choose_color)
        self.update_button_display()

    def choose_color(self):
        """选择颜色"""
        try:
            from .advanced_color_picker import AdvancedColorPicker

            dialog = AdvancedColorPicker(self, QColor(self.current_color))
            if dialog.exec() == dialog.DialogCode.Accepted:
                # 检查是否选择了渐变
                gradient_data = dialog.get_gradient_data()
                if gradient_data:
                    self.gradient_data = gradient_data
                    self.gradient_changed.emit(gradient_data)
                else:
                    # 普通颜色
                    selected_color = dialog.get_selected_color()
                    self.current_color = selected_color.name()
                    self.gradient_data = None
                    self.color_changed.emit(self.current_color)

                self.update_button_display()

        except Exception as e:
            logger.error(f"打开高级颜色选择器失败: {e}")
            # 回退到系统颜色选择器
            color = QColorDialog.getColor(QColor(self.current_color), self)
            if color.isValid():
                self.current_color = color.name()
                self.gradient_data = None
                self.update_button_display()
                self.color_changed.emit(self.current_color)

    def update_button_display(self):
        """更新按钮显示"""
        if self.gradient_data:
            # 显示渐变预览
            self.setText("渐变")
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #ff0000, stop:0.5 #00ff00, stop:1 #0000ff);
                    border: 1px solid #ccc;
                    color: white;
                    font-weight: bold;
                }
            """)
        else:
            # 显示纯色
            self.setText("")
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.current_color};
                    border: 1px solid #ccc;
                }}
            """)

    def set_color(self, color: str):
        """设置颜色"""
        self.current_color = color
        self.gradient_data = None
        self.update_button_display()

    def set_gradient(self, gradient_data: dict):
        """设置渐变"""
        self.gradient_data = gradient_data
        self.update_button_display()

    def get_current_value(self):
        """获取当前值（颜色或渐变）"""
        if self.gradient_data:
            return self.gradient_data
        else:
            return self.current_color

class PropertiesWidget(QWidget):
    """属性面板组件"""

    element_updated = pyqtSignal(Element)  # 元素更新信号
    batch_update_requested = pyqtSignal(list, dict)  # 批量更新信号
    preset_applied = pyqtSignal(str, dict)  # 预设应用信号

    def __init__(self):
        super().__init__()
        self.current_element = None
        self.selected_elements = []  # 多选元素
        self.updating = False  # 防止循环更新
        self.real_time_preview = True  # 实时预览
        self.update_timer = QTimer()  # 延迟更新定时器
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.apply_delayed_update)

        # 预设管理
        from core.property_presets import PropertyPresetManager
        self.preset_manager = PropertyPresetManager()
        self.style_presets = {}
        self.load_style_presets()

        self.setup_ui()
        self.setup_connections()

        logger.info("属性面板组件初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 顶部工具栏
        toolbar_layout = QHBoxLayout()

        # 多选模式指示
        self.multi_select_label = QLabel("单选模式")
        self.multi_select_label.setStyleSheet("color: blue; font-weight: bold;")
        toolbar_layout.addWidget(self.multi_select_label)

        toolbar_layout.addStretch()

        # 实时预览开关
        self.preview_checkbox = QCheckBox("实时预览")
        self.preview_checkbox.setChecked(True)
        toolbar_layout.addWidget(self.preview_checkbox)

        # 重置按钮
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setMaximumWidth(60)
        toolbar_layout.addWidget(self.reset_btn)

        layout.addLayout(toolbar_layout)

        # 预设工具栏
        preset_toolbar = self.create_preset_toolbar()
        layout.addWidget(preset_toolbar)

        # 创建标签页
        self.tab_widget = QTabWidget()

        # 基本属性标签页
        basic_tab = self.create_basic_tab()
        self.tab_widget.addTab(basic_tab, "📝 基本")

        # 位置变换标签页
        transform_tab = self.create_transform_tab()
        self.tab_widget.addTab(transform_tab, "📐 变换")

        # 样式属性标签页
        style_tab = self.create_style_tab()
        self.tab_widget.addTab(style_tab, "🎨 样式")

        # 高级属性标签页
        advanced_tab = self.create_advanced_tab()
        self.tab_widget.addTab(advanced_tab, "⚙️ 高级")

        layout.addWidget(self.tab_widget)

        # 底部操作区
        bottom_layout = QHBoxLayout()

        # 预设管理
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("选择预设...")
        bottom_layout.addWidget(QLabel("预设:"))
        bottom_layout.addWidget(self.preset_combo)

        self.save_preset_btn = QPushButton("保存")
        self.save_preset_btn.setMaximumWidth(50)
        bottom_layout.addWidget(self.save_preset_btn)

        bottom_layout.addStretch()

        # 批量操作按钮
        self.batch_apply_btn = QPushButton("批量应用")
        self.batch_apply_btn.setEnabled(False)
        bottom_layout.addWidget(self.batch_apply_btn)

        layout.addLayout(bottom_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

    def create_basic_tab(self):
        """创建基本属性标签页"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # 元素名称
        self.name_input = QLineEdit()
        layout.addRow("名称:", self.name_input)

        # 元素类型
        self.type_combo = QComboBox()
        for element_type in ElementType:
            self.type_combo.addItem(element_type.value, element_type)
        layout.addRow("类型:", self.type_combo)

        # 内容
        self.content_input = QTextEdit()
        self.content_input.setMaximumHeight(80)
        layout.addRow("内容:", self.content_input)

        # 可见性和锁定
        visibility_layout = QHBoxLayout()
        self.visible_checkbox = QCheckBox("可见")
        self.locked_checkbox = QCheckBox("锁定")
        visibility_layout.addWidget(self.visible_checkbox)
        visibility_layout.addWidget(self.locked_checkbox)
        layout.addRow("状态:", visibility_layout)

        # ID显示（只读）
        self.id_label = QLabel()
        self.id_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addRow("ID:", self.id_label)

        return tab

    def create_transform_tab(self):
        """创建位置变换标签页 - 增强版"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)

        # 可视化控制器
        from .transform_visualizer import TransformVisualizer
        self.transform_visualizer = TransformVisualizer()
        self.transform_visualizer.setMaximumHeight(200)
        self.transform_visualizer.transform_changed.connect(self.on_visual_transform_changed)
        main_layout.addWidget(self.transform_visualizer)

        # 数值控制区域
        controls_widget = QWidget()
        layout = QFormLayout(controls_widget)

        # 位置控制 - 增强版
        position_layout = QHBoxLayout()
        self.pos_x_spin = QDoubleSpinBox()
        self.pos_x_spin.setRange(-9999, 9999)
        self.pos_x_spin.setDecimals(1)
        self.pos_x_spin.setToolTip("X坐标位置")
        self.pos_y_spin = QDoubleSpinBox()
        self.pos_y_spin.setRange(-9999, 9999)
        self.pos_y_spin.setDecimals(1)
        self.pos_y_spin.setToolTip("Y坐标位置")

        position_layout.addWidget(QLabel("X:"))
        position_layout.addWidget(self.pos_x_spin)
        position_layout.addWidget(QLabel("Y:"))
        position_layout.addWidget(self.pos_y_spin)

        # 位置快捷按钮 - 增强版
        pos_shortcuts = QHBoxLayout()
        self.center_btn = QPushButton("居中")
        self.center_btn.setMaximumWidth(40)
        self.center_btn.setToolTip("移动到画布中心")

        self.top_left_btn = QPushButton("左上")
        self.top_left_btn.setMaximumWidth(35)
        self.top_left_btn.setToolTip("移动到左上角")

        self.top_right_btn = QPushButton("右上")
        self.top_right_btn.setMaximumWidth(35)
        self.top_right_btn.setToolTip("移动到右上角")

        self.bottom_left_btn = QPushButton("左下")
        self.bottom_left_btn.setMaximumWidth(35)
        self.bottom_left_btn.setToolTip("移动到左下角")

        self.bottom_right_btn = QPushButton("右下")
        self.bottom_right_btn.setMaximumWidth(35)
        self.bottom_right_btn.setToolTip("移动到右下角")

        pos_shortcuts.addWidget(self.center_btn)
        pos_shortcuts.addWidget(self.top_left_btn)
        pos_shortcuts.addWidget(self.top_right_btn)
        pos_shortcuts.addWidget(self.bottom_left_btn)
        pos_shortcuts.addWidget(self.bottom_right_btn)
        position_layout.addLayout(pos_shortcuts)

        layout.addRow("位置:", position_layout)

        # 旋转控制 - 增强版
        rotation_layout = QHBoxLayout()

        # 旋转滑块
        self.rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.rotation_slider.setRange(-360, 360)
        self.rotation_slider.setValue(0)
        self.rotation_slider.setToolTip("拖拽调整旋转角度")
        rotation_layout.addWidget(self.rotation_slider)

        self.rotation_spin = QDoubleSpinBox()
        self.rotation_spin.setRange(-360, 360)
        self.rotation_spin.setSuffix("°")
        self.rotation_spin.setDecimals(1)
        self.rotation_spin.setToolTip("精确输入旋转角度")
        rotation_layout.addWidget(self.rotation_spin)

        # 旋转快捷按钮 - 增强版
        rotation_shortcuts = QHBoxLayout()
        for angle in [0, 45, 90, 180, 270]:
            btn = QPushButton(f"{angle}°")
            btn.setMaximumWidth(35)
            btn.clicked.connect(lambda checked, a=angle: self.rotation_spin.setValue(a))
            rotation_shortcuts.addWidget(btn)

        reset_rotation_btn = QPushButton("重置")
        reset_rotation_btn.setMaximumWidth(35)
        reset_rotation_btn.clicked.connect(lambda: self.rotation_spin.setValue(0))
        rotation_shortcuts.addWidget(reset_rotation_btn)

        rotation_layout.addLayout(rotation_shortcuts)
        layout.addRow("旋转:", rotation_layout)

        # 缩放控制 - 增强版
        scale_layout = QHBoxLayout()
        self.scale_x_spin = QDoubleSpinBox()
        self.scale_x_spin.setRange(0.01, 100.0)
        self.scale_x_spin.setValue(1.0)
        self.scale_x_spin.setSingleStep(0.1)
        self.scale_x_spin.setDecimals(2)
        self.scale_x_spin.setToolTip("X轴缩放比例")

        self.scale_y_spin = QDoubleSpinBox()
        self.scale_y_spin.setRange(0.01, 100.0)
        self.scale_y_spin.setValue(1.0)
        self.scale_y_spin.setSingleStep(0.1)
        self.scale_y_spin.setDecimals(2)
        self.scale_y_spin.setToolTip("Y轴缩放比例")

        # 锁定比例按钮
        self.lock_aspect_checkbox = QCheckBox("🔗")
        self.lock_aspect_checkbox.setToolTip("锁定宽高比")
        self.lock_aspect_checkbox.setMaximumWidth(30)
        self.lock_aspect_checkbox.setChecked(True)

        scale_layout.addWidget(QLabel("X:"))
        scale_layout.addWidget(self.scale_x_spin)
        scale_layout.addWidget(self.lock_aspect_checkbox)
        scale_layout.addWidget(QLabel("Y:"))
        scale_layout.addWidget(self.scale_y_spin)

        # 缩放快捷按钮 - 增强版
        scale_shortcuts = QHBoxLayout()
        for scale in [0.25, 0.5, 1.0, 1.5, 2.0, 4.0]:
            btn = QPushButton(f"{scale}x")
            btn.setMaximumWidth(35)
            btn.clicked.connect(lambda checked, s=scale: self.set_uniform_scale(s))
            scale_shortcuts.addWidget(btn)

        scale_layout.addLayout(scale_shortcuts)
        layout.addRow("缩放:", scale_layout)

        # 锚点
        anchor_layout = QHBoxLayout()
        self.anchor_combo = QComboBox()
        anchor_options = [
            ("左上", "top-left"), ("上中", "top-center"), ("右上", "top-right"),
            ("左中", "middle-left"), ("中心", "center"), ("右中", "middle-right"),
            ("左下", "bottom-left"), ("下中", "bottom-center"), ("右下", "bottom-right")
        ]
        for name, value in anchor_options:
            self.anchor_combo.addItem(name, value)
        self.anchor_combo.setCurrentText("中心")
        anchor_layout.addWidget(self.anchor_combo)
        layout.addRow("锚点:", anchor_layout)

        # 3D变换控制（高级功能）
        transform_3d_layout = QHBoxLayout()

        # Z轴旋转
        transform_3d_layout.addWidget(QLabel("Z轴:"))
        self.rotate_z_spin = QDoubleSpinBox()
        self.rotate_z_spin.setRange(-360, 360)
        self.rotate_z_spin.setDecimals(1)
        self.rotate_z_spin.setSuffix("°")
        self.rotate_z_spin.setToolTip("Z轴旋转角度")
        transform_3d_layout.addWidget(self.rotate_z_spin)

        # 透视
        transform_3d_layout.addWidget(QLabel("透视:"))
        self.perspective_spin = QDoubleSpinBox()
        self.perspective_spin.setRange(0, 2000)
        self.perspective_spin.setValue(1000)
        self.perspective_spin.setSuffix("px")
        self.perspective_spin.setToolTip("透视距离")
        transform_3d_layout.addWidget(self.perspective_spin)

        layout.addRow("3D变换:", transform_3d_layout)

        main_layout.addWidget(controls_widget)

        return tab

    def create_style_tab(self):
        """创建样式属性标签页 - 增强版"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)

        # 样式预设工具栏
        style_toolbar = self.create_style_preset_toolbar()
        main_layout.addWidget(style_toolbar)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)

        # 尺寸控制 - 增强版
        size_group = QGroupBox("尺寸")
        size_layout = QVBoxLayout(size_group)

        # 基本尺寸
        basic_size_layout = QHBoxLayout()
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("auto")
        self.width_input.setToolTip("元素宽度，支持px、%、em等单位")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("auto")
        self.height_input.setToolTip("元素高度，支持px、%、em等单位")

        # 锁定宽高比
        self.size_lock_btn = QPushButton("🔗")
        self.size_lock_btn.setMaximumWidth(30)
        self.size_lock_btn.setCheckable(True)
        self.size_lock_btn.setToolTip("锁定宽高比例")

        basic_size_layout.addWidget(QLabel("宽:"))
        basic_size_layout.addWidget(self.width_input)
        basic_size_layout.addWidget(self.size_lock_btn)
        basic_size_layout.addWidget(QLabel("高:"))
        basic_size_layout.addWidget(self.height_input)
        size_layout.addLayout(basic_size_layout)

        # 尺寸预设
        size_presets_layout = QHBoxLayout()
        size_presets = [("小", "100x75"), ("中", "200x150"), ("大", "400x300"), ("全屏", "100%x100%")]
        for name, size in size_presets:
            btn = QPushButton(name)
            btn.setMaximumWidth(40)
            btn.setToolTip(f"设置为{size}")
            btn.clicked.connect(lambda checked, s=size: self.apply_size_preset(s))
            size_presets_layout.addWidget(btn)
        size_layout.addLayout(size_presets_layout)

        main_layout.addWidget(size_group)

        # 颜色控制 - 增强版
        color_group = QGroupBox("颜色")
        color_layout = QVBoxLayout(color_group)

        # 基本颜色
        basic_color_layout = QHBoxLayout()
        self.bg_color_btn = AdvancedColorButton("#ffffff", "背景颜色")
        self.text_color_btn = AdvancedColorButton("#000000", "文字颜色")
        self.border_color_btn = AdvancedColorButton("#cccccc", "边框颜色")

        basic_color_layout.addWidget(QLabel("背景:"))
        basic_color_layout.addWidget(self.bg_color_btn)
        basic_color_layout.addWidget(QLabel("文字:"))
        basic_color_layout.addWidget(self.text_color_btn)
        basic_color_layout.addWidget(QLabel("边框:"))
        basic_color_layout.addWidget(self.border_color_btn)
        color_layout.addLayout(basic_color_layout)

        # 渐变背景
        gradient_layout = QHBoxLayout()
        self.enable_gradient_cb = QCheckBox("启用渐变背景")
        gradient_layout.addWidget(self.enable_gradient_cb)

        self.gradient_editor_btn = QPushButton("编辑渐变")
        self.gradient_editor_btn.setEnabled(False)
        self.gradient_editor_btn.clicked.connect(self.edit_gradient)
        gradient_layout.addWidget(self.gradient_editor_btn)

        self.enable_gradient_cb.toggled.connect(self.gradient_editor_btn.setEnabled)
        color_layout.addLayout(gradient_layout)

        main_layout.addWidget(color_group)

        # 透明度控制 - 增强版
        opacity_group = QGroupBox("透明度")
        opacity_layout = QVBoxLayout(opacity_group)

        opacity_controls_layout = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setToolTip("拖拽调整透明度")
        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(0, 100)
        self.opacity_spin.setValue(100)
        self.opacity_spin.setSuffix("%")
        self.opacity_spin.setToolTip("精确输入透明度值")

        opacity_controls_layout.addWidget(self.opacity_slider)
        opacity_controls_layout.addWidget(self.opacity_spin)
        opacity_layout.addLayout(opacity_controls_layout)

        # 透明度预设
        opacity_presets_layout = QHBoxLayout()
        opacity_presets = [("0%", 0), ("25%", 25), ("50%", 50), ("75%", 75), ("100%", 100)]
        for name, value in opacity_presets:
            btn = QPushButton(name)
            btn.setMaximumWidth(35)
            btn.clicked.connect(lambda checked, v=value: self.opacity_slider.setValue(v))
            opacity_presets_layout.addWidget(btn)
        opacity_layout.addLayout(opacity_presets_layout)

        main_layout.addWidget(opacity_group)

        # 边框控制 - 增强版
        border_group = QGroupBox("边框")
        border_layout = QVBoxLayout(border_group)

        # 基本边框设置
        basic_border_layout = QHBoxLayout()
        self.border_width_spin = QSpinBox()
        self.border_width_spin.setRange(0, 50)
        self.border_width_spin.setSuffix("px")
        self.border_width_spin.setToolTip("边框宽度")

        self.border_style_combo = QComboBox()
        border_styles = ["none", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"]
        self.border_style_combo.addItems(border_styles)
        self.border_style_combo.setToolTip("边框样式")

        basic_border_layout.addWidget(QLabel("宽度:"))
        basic_border_layout.addWidget(self.border_width_spin)
        basic_border_layout.addWidget(QLabel("样式:"))
        basic_border_layout.addWidget(self.border_style_combo)
        border_layout.addLayout(basic_border_layout)

        # 独立边框控制
        individual_border_cb = QCheckBox("独立设置各边")
        border_layout.addWidget(individual_border_cb)

        self.individual_border_widget = QWidget()
        individual_border_layout = QGridLayout(self.individual_border_widget)

        # 上边框
        individual_border_layout.addWidget(QLabel("上:"), 0, 0)
        self.border_top_spin = QSpinBox()
        self.border_top_spin.setRange(0, 50)
        self.border_top_spin.setSuffix("px")
        individual_border_layout.addWidget(self.border_top_spin, 0, 1)

        # 右边框
        individual_border_layout.addWidget(QLabel("右:"), 0, 2)
        self.border_right_spin = QSpinBox()
        self.border_right_spin.setRange(0, 50)
        self.border_right_spin.setSuffix("px")
        individual_border_layout.addWidget(self.border_right_spin, 0, 3)

        # 下边框
        individual_border_layout.addWidget(QLabel("下:"), 1, 0)
        self.border_bottom_spin = QSpinBox()
        self.border_bottom_spin.setRange(0, 50)
        self.border_bottom_spin.setSuffix("px")
        individual_border_layout.addWidget(self.border_bottom_spin, 1, 1)

        # 左边框
        individual_border_layout.addWidget(QLabel("左:"), 1, 2)
        self.border_left_spin = QSpinBox()
        self.border_left_spin.setRange(0, 50)
        self.border_left_spin.setSuffix("px")
        individual_border_layout.addWidget(self.border_left_spin, 1, 3)

        self.individual_border_widget.setEnabled(False)
        individual_border_cb.toggled.connect(self.individual_border_widget.setEnabled)
        border_layout.addWidget(self.individual_border_widget)

        main_layout.addWidget(border_group)

        # 圆角控制 - 增强版
        radius_group = QGroupBox("圆角")
        radius_layout = QVBoxLayout(radius_group)

        # 统一圆角
        uniform_radius_layout = QHBoxLayout()
        self.border_radius_spin = QSpinBox()
        self.border_radius_spin.setRange(0, 100)
        self.border_radius_spin.setSuffix("px")
        self.border_radius_spin.setToolTip("统一圆角半径")
        uniform_radius_layout.addWidget(self.border_radius_spin)

        # 圆角预设
        radius_presets = [("0", 0), ("5", 5), ("10", 10), ("20", 20), ("50", 50)]
        for name, value in radius_presets:
            btn = QPushButton(name)
            btn.setMaximumWidth(30)
            btn.clicked.connect(lambda checked, v=value: self.border_radius_spin.setValue(v))
            uniform_radius_layout.addWidget(btn)

        radius_layout.addLayout(uniform_radius_layout)

        # 独立圆角控制
        individual_radius_cb = QCheckBox("独立设置各角")
        radius_layout.addWidget(individual_radius_cb)

        self.individual_radius_widget = QWidget()
        individual_radius_layout = QGridLayout(self.individual_radius_widget)

        # 左上角
        individual_radius_layout.addWidget(QLabel("左上:"), 0, 0)
        self.radius_tl_spin = QSpinBox()
        self.radius_tl_spin.setRange(0, 100)
        self.radius_tl_spin.setSuffix("px")
        individual_radius_layout.addWidget(self.radius_tl_spin, 0, 1)

        # 右上角
        individual_radius_layout.addWidget(QLabel("右上:"), 0, 2)
        self.radius_tr_spin = QSpinBox()
        self.radius_tr_spin.setRange(0, 100)
        self.radius_tr_spin.setSuffix("px")
        individual_radius_layout.addWidget(self.radius_tr_spin, 0, 3)

        # 左下角
        individual_radius_layout.addWidget(QLabel("左下:"), 1, 0)
        self.radius_bl_spin = QSpinBox()
        self.radius_bl_spin.setRange(0, 100)
        self.radius_bl_spin.setSuffix("px")
        individual_radius_layout.addWidget(self.radius_bl_spin, 1, 1)

        # 右下角
        individual_radius_layout.addWidget(QLabel("右下:"), 1, 2)
        self.radius_br_spin = QSpinBox()
        self.radius_br_spin.setRange(0, 100)
        self.radius_br_spin.setSuffix("px")
        individual_radius_layout.addWidget(self.radius_br_spin, 1, 3)

        self.individual_radius_widget.setEnabled(False)
        individual_radius_cb.toggled.connect(self.individual_radius_widget.setEnabled)
        radius_layout.addWidget(self.individual_radius_widget)

        main_layout.addWidget(radius_group)

        # 阴影控制 - 增强版
        shadow_group = QGroupBox("阴影")
        shadow_layout = QVBoxLayout(shadow_group)

        self.shadow_checkbox = QCheckBox("启用阴影")
        shadow_layout.addWidget(self.shadow_checkbox)

        self.shadow_controls_widget = QWidget()
        shadow_controls_layout = QVBoxLayout(self.shadow_controls_widget)

        # 基本阴影控制
        basic_shadow_layout = QGridLayout()

        basic_shadow_layout.addWidget(QLabel("X偏移:"), 0, 0)
        self.shadow_x_spin = QSpinBox()
        self.shadow_x_spin.setRange(-100, 100)
        self.shadow_x_spin.setSuffix("px")
        basic_shadow_layout.addWidget(self.shadow_x_spin, 0, 1)

        basic_shadow_layout.addWidget(QLabel("Y偏移:"), 0, 2)
        self.shadow_y_spin = QSpinBox()
        self.shadow_y_spin.setRange(-100, 100)
        self.shadow_y_spin.setSuffix("px")
        basic_shadow_layout.addWidget(self.shadow_y_spin, 0, 3)

        basic_shadow_layout.addWidget(QLabel("模糊:"), 1, 0)
        self.shadow_blur_spin = QSpinBox()
        self.shadow_blur_spin.setRange(0, 100)
        self.shadow_blur_spin.setSuffix("px")
        basic_shadow_layout.addWidget(self.shadow_blur_spin, 1, 1)

        basic_shadow_layout.addWidget(QLabel("扩散:"), 1, 2)
        self.shadow_spread_spin = QSpinBox()
        self.shadow_spread_spin.setRange(-50, 50)
        self.shadow_spread_spin.setSuffix("px")
        basic_shadow_layout.addWidget(self.shadow_spread_spin, 1, 3)

        shadow_controls_layout.addLayout(basic_shadow_layout)

        # 阴影颜色
        shadow_color_layout = QHBoxLayout()
        shadow_color_layout.addWidget(QLabel("颜色:"))
        self.shadow_color_btn = AdvancedColorButton("#000000", "阴影颜色")
        shadow_color_layout.addWidget(self.shadow_color_btn)
        shadow_color_layout.addStretch()
        shadow_controls_layout.addLayout(shadow_color_layout)

        # 阴影预设
        shadow_presets_layout = QHBoxLayout()
        shadow_presets = [
            ("柔和", (2, 2, 8, 0)),
            ("锐利", (1, 1, 0, 0)),
            ("浮起", (0, 4, 8, 0)),
            ("内阴影", (-2, -2, 4, 0))
        ]
        for name, (x, y, blur, spread) in shadow_presets:
            btn = QPushButton(name)
            btn.setMaximumWidth(50)
            btn.clicked.connect(lambda checked, params=(x,y,blur,spread): self.apply_shadow_preset(params))
            shadow_presets_layout.addWidget(btn)
        shadow_controls_layout.addLayout(shadow_presets_layout)

        self.shadow_controls_widget.setEnabled(False)
        self.shadow_checkbox.toggled.connect(self.shadow_controls_widget.setEnabled)
        shadow_layout.addWidget(self.shadow_controls_widget)

        main_layout.addWidget(shadow_group)

        # 设置滚动区域
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        return tab

    def create_advanced_tab(self):
        """创建高级属性标签页"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # 字体设置（文本元素）
        font_layout = QVBoxLayout()

        font_family_layout = QHBoxLayout()
        self.font_family_combo = QFontComboBox()
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 200)
        self.font_size_spin.setValue(16)
        self.font_size_spin.setSuffix("px")
        font_family_layout.addWidget(self.font_family_combo)
        font_family_layout.addWidget(self.font_size_spin)
        font_layout.addLayout(font_family_layout)

        font_style_layout = QHBoxLayout()
        self.bold_checkbox = QCheckBox("粗体")
        self.italic_checkbox = QCheckBox("斜体")
        self.underline_checkbox = QCheckBox("下划线")
        font_style_layout.addWidget(self.bold_checkbox)
        font_style_layout.addWidget(self.italic_checkbox)
        font_style_layout.addWidget(self.underline_checkbox)
        font_layout.addLayout(font_style_layout)

        layout.addRow("字体:", font_layout)

        # 文本对齐
        align_layout = QHBoxLayout()
        self.align_group = QButtonGroup()
        align_options = [("左对齐", "left"), ("居中", "center"), ("右对齐", "right"), ("两端对齐", "justify")]
        for i, (name, value) in enumerate(align_options):
            radio = QRadioButton(name)
            radio.setProperty("align_value", value)
            self.align_group.addButton(radio, i)
            align_layout.addWidget(radio)
        self.align_group.button(1).setChecked(True)  # 默认居中
        layout.addRow("对齐:", align_layout)

        # 层级
        z_index_layout = QHBoxLayout()
        self.z_index_spin = QSpinBox()
        self.z_index_spin.setRange(-1000, 1000)
        self.z_index_spin.setValue(0)
        z_index_layout.addWidget(self.z_index_spin)
        layout.addRow("层级:", z_index_layout)

        # 混合模式
        blend_layout = QHBoxLayout()
        self.blend_mode_combo = QComboBox()
        blend_modes = ["normal", "multiply", "screen", "overlay", "darken", "lighten", "color-dodge", "color-burn"]
        self.blend_mode_combo.addItems(blend_modes)
        blend_layout.addWidget(self.blend_mode_combo)
        layout.addRow("混合模式:", blend_layout)

        # 自定义CSS
        css_layout = QVBoxLayout()
        self.custom_css_input = QTextEdit()
        self.custom_css_input.setMaximumHeight(100)
        self.custom_css_input.setPlaceholderText("输入自定义CSS样式...")
        css_layout.addWidget(self.custom_css_input)
        layout.addRow("自定义CSS:", css_layout)

        return tab

    # 辅助方法
    def set_uniform_scale(self, scale: float):
        """设置统一缩放"""
        self.scale_x_spin.setValue(scale)
        self.scale_y_spin.setValue(scale)

    def load_style_presets(self):
        """加载样式预设"""
        # 默认预设
        self.style_presets = {
            "标题样式": {
                "font_size": 24,
                "font_weight": "bold",
                "color": "#333333",
                "text_align": "center"
            },
            "正文样式": {
                "font_size": 16,
                "color": "#666666",
                "line_height": "1.5"
            },
            "按钮样式": {
                "background_color": "#007bff",
                "color": "#ffffff",
                "border_radius": "5px",
                "padding": "10px 20px"
            },
            "卡片样式": {
                "background_color": "#ffffff",
                "border": "1px solid #e0e0e0",
                "border_radius": "8px",
                "box_shadow": "0 2px 4px rgba(0,0,0,0.1)"
            }
        }

        # 更新预设下拉框
        self.update_preset_combo()

    def update_preset_combo(self):
        """更新预设下拉框"""
        if hasattr(self, 'preset_combo'):
            self.preset_combo.clear()
            self.preset_combo.addItem("选择预设...")
            for preset_name in self.style_presets.keys():
                self.preset_combo.addItem(preset_name)

    
    def setup_connections(self):
        """设置信号连接"""
        # 基本属性
        self.name_input.textChanged.connect(self.on_property_changed)
        self.type_combo.currentTextChanged.connect(self.on_property_changed)
        self.content_input.textChanged.connect(self.on_property_changed)
        self.visible_checkbox.toggled.connect(self.on_property_changed)
        self.locked_checkbox.toggled.connect(self.on_property_changed)
        
        # 位置和变换
        self.pos_x_spin.valueChanged.connect(self.on_property_changed)
        self.pos_y_spin.valueChanged.connect(self.on_property_changed)
        self.rotation_spin.valueChanged.connect(self.on_property_changed)
        self.scale_x_spin.valueChanged.connect(self.on_property_changed)
        self.scale_y_spin.valueChanged.connect(self.on_property_changed)
        
        # 样式属性
        self.width_input.textChanged.connect(self.on_property_changed)
        self.height_input.textChanged.connect(self.on_property_changed)
        self.bg_color_btn.color_changed.connect(self.on_property_changed)
        self.text_color_btn.color_changed.connect(self.on_property_changed)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        self.font_family_combo.currentTextChanged.connect(self.on_property_changed)
        self.font_size_spin.valueChanged.connect(self.on_property_changed)
        
        # 操作按钮
        self.reset_btn.clicked.connect(self.reset_properties)
        self.apply_btn.clicked.connect(self.apply_properties)
    
    def set_element(self, element: Element):
        """设置当前编辑的元素"""
        self.current_element = element
        if element:
            self.load_element_properties()
            self.set_enabled(True)
        else:
            self.set_enabled(False)
    
    def load_element_properties(self):
        """加载元素属性到界面"""
        if not self.current_element:
            return
        
        self.updating = True
        
        try:
            # 基本属性
            self.name_input.setText(self.current_element.name)
            
            # 设置类型下拉框
            for i in range(self.type_combo.count()):
                if self.type_combo.itemData(i) == self.current_element.element_type:
                    self.type_combo.setCurrentIndex(i)
                    break
            
            self.content_input.setPlainText(self.current_element.content)
            self.visible_checkbox.setChecked(self.current_element.visible)
            self.locked_checkbox.setChecked(self.current_element.locked)
            
            # 位置和变换
            self.pos_x_spin.setValue(self.current_element.position.x)
            self.pos_y_spin.setValue(self.current_element.position.y)
            self.rotation_spin.setValue(self.current_element.transform.rotate_z)
            self.scale_x_spin.setValue(self.current_element.transform.scale_x)
            self.scale_y_spin.setValue(self.current_element.transform.scale_y)
            
            # 样式属性
            self.width_input.setText(self.current_element.style.width)
            self.height_input.setText(self.current_element.style.height)
            self.bg_color_btn.set_color(self.current_element.style.background_color)
            self.text_color_btn.set_color(self.current_element.style.color)
            
            opacity_percent = int(self.current_element.style.opacity * 100)
            self.opacity_slider.setValue(opacity_percent)
            self.opacity_label.setText(f"{opacity_percent}%")
            
            # 字体设置
            font_family = self.current_element.style.font_family
            if font_family != "inherit":
                index = self.font_family_combo.findText(font_family)
                if index >= 0:
                    self.font_family_combo.setCurrentIndex(index)
            
            font_size = self.current_element.style.font_size
            if font_size.endswith("px"):
                try:
                    size = int(font_size[:-2])
                    self.font_size_spin.setValue(size)
                except ValueError:
                    pass
            
        finally:
            self.updating = False

            # 更新变换可视化控制器
            self.update_transform_visualizer()
    
    def on_property_changed(self):
        """属性改变处理"""
        if self.updating or not self.current_element:
            return

        # 如果启用实时预览，使用延迟更新避免频繁更新
        if self.real_time_preview:
            # 停止之前的定时器
            self.update_timer.stop()
            # 启动新的延迟更新（300ms后执行）
            self.update_timer.start(300)
        else:
            # 不启用实时预览时，只标记为已修改
            self.mark_as_modified()
    
    def on_opacity_changed(self, value: int):
        """透明度改变处理"""
        self.opacity_label.setText(f"{value}%")
        self.on_property_changed()
    
    def apply_properties(self):
        """应用属性更改"""
        if not self.current_element:
            return

        # 验证属性值
        if not self.validate_properties():
            logger.warning("属性验证失败，取消应用")
            return

        try:
            # 基本属性
            self.current_element.name = self.name_input.text()
            self.current_element.element_type = self.type_combo.currentData()
            self.current_element.content = self.content_input.toPlainText()
            self.current_element.visible = self.visible_checkbox.isChecked()
            self.current_element.locked = self.locked_checkbox.isChecked()
            
            # 位置和变换
            from core.data_structures import Point
            self.current_element.position = Point(
                self.pos_x_spin.value(),
                self.pos_y_spin.value()
            )
            
            self.current_element.transform.rotate_z = self.rotation_spin.value()
            self.current_element.transform.scale_x = self.scale_x_spin.value()
            self.current_element.transform.scale_y = self.scale_y_spin.value()
            
            # 样式属性
            self.current_element.style.width = self.width_input.text() or "auto"
            self.current_element.style.height = self.height_input.text() or "auto"
            self.current_element.style.background_color = self.bg_color_btn.current_color
            self.current_element.style.color = self.text_color_btn.current_color
            self.current_element.style.opacity = self.opacity_slider.value() / 100.0
            self.current_element.style.font_family = self.font_family_combo.currentText()
            self.current_element.style.font_size = f"{self.font_size_spin.value()}px"
            
            # 发射更新信号
            self.element_updated.emit(self.current_element)

            # 清除修改标记
            self.clear_modified_mark()

            logger.info(f"应用元素属性: {self.current_element.name}")

        except Exception as e:
            logger.error(f"应用属性失败: {e}")
            # 应用失败时保持修改标记
            self.mark_as_modified()
    
    def reset_properties(self):
        """重置属性"""
        if self.current_element:
            self.load_element_properties()
            logger.info(f"重置元素属性: {self.current_element.name}")
    
    def set_enabled(self, enabled: bool):
        """设置控件启用状态"""
        for widget in self.findChildren(QWidget):
            if widget != self:
                widget.setEnabled(enabled)

        if not enabled:
            # 清空显示
            self.name_input.clear()
            self.content_input.clear()
            self.width_input.clear()
            self.height_input.clear()

    def apply_delayed_update(self):
        """应用延迟更新"""
        try:
            if self.current_element and not self.updating:
                self.apply_properties()
                logger.debug("应用延迟更新完成")
        except Exception as e:
            logger.error(f"延迟更新失败: {e}")

    def mark_as_modified(self):
        """标记为已修改"""
        try:
            # 可以在界面上显示修改标记
            if hasattr(self, 'apply_btn'):
                self.apply_btn.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")
                self.apply_btn.setText("应用*")

        except Exception as e:
            logger.error(f"标记修改状态失败: {e}")

    def clear_modified_mark(self):
        """清除修改标记"""
        try:
            if hasattr(self, 'apply_btn'):
                self.apply_btn.setStyleSheet("")
                self.apply_btn.setText("应用")

        except Exception as e:
            logger.error(f"清除修改标记失败: {e}")

    def toggle_real_time_preview(self, enabled: bool):
        """切换实时预览模式"""
        try:
            self.real_time_preview = enabled

            if enabled:
                # 启用实时预览时，立即应用当前更改
                if self.current_element and not self.updating:
                    self.apply_properties()

            logger.info(f"实时预览模式: {'启用' if enabled else '禁用'}")

        except Exception as e:
            logger.error(f"切换实时预览模式失败: {e}")

    def batch_update_properties(self, properties: dict):
        """批量更新属性"""
        try:
            if not self.current_element:
                return

            # 暂停实时更新
            old_updating = self.updating
            self.updating = True

            # 批量设置属性
            for prop_name, value in properties.items():
                if hasattr(self, prop_name):
                    widget = getattr(self, prop_name)

                    # 根据控件类型设置值
                    if hasattr(widget, 'setValue'):
                        widget.setValue(value)
                    elif hasattr(widget, 'setText'):
                        widget.setText(str(value))
                    elif hasattr(widget, 'setChecked'):
                        widget.setChecked(bool(value))
                    elif hasattr(widget, 'setCurrentText'):
                        widget.setCurrentText(str(value))

            # 恢复更新状态
            self.updating = old_updating

            # 应用所有更改
            if not self.updating:
                self.apply_properties()

            logger.info(f"批量更新了 {len(properties)} 个属性")

        except Exception as e:
            logger.error(f"批量更新属性失败: {e}")

    def sync_with_element(self, element):
        """与元素同步"""
        try:
            if element and element == self.current_element:
                # 重新加载元素属性，保持界面同步
                self.load_element_properties()
                logger.debug(f"与元素同步: {element.name}")

        except Exception as e:
            logger.error(f"与元素同步失败: {e}")

    def validate_properties(self) -> bool:
        """验证属性值"""
        try:
            # 验证数值范围
            if hasattr(self, 'pos_x_spin') and hasattr(self, 'pos_y_spin'):
                x = self.pos_x_spin.value()
                y = self.pos_y_spin.value()

                # 检查位置是否在合理范围内
                if abs(x) > 10000 or abs(y) > 10000:
                    logger.warning("位置值超出合理范围")
                    return False

            # 验证缩放值
            if hasattr(self, 'scale_x_spin') and hasattr(self, 'scale_y_spin'):
                scale_x = self.scale_x_spin.value()
                scale_y = self.scale_y_spin.value()

                if scale_x <= 0 or scale_y <= 0:
                    logger.warning("缩放值必须大于0")
                    return False

            # 验证尺寸值
            if hasattr(self, 'width_input') and hasattr(self, 'height_input'):
                width_text = self.width_input.text().strip()
                height_text = self.height_input.text().strip()

                # 如果不是auto，检查是否为有效数值
                if width_text and width_text != "auto":
                    try:
                        width_val = float(width_text.replace('px', '').replace('%', ''))
                        if width_val < 0:
                            logger.warning("宽度值不能为负数")
                            return False
                    except ValueError:
                        logger.warning("宽度值格式无效")
                        return False

                if height_text and height_text != "auto":
                    try:
                        height_val = float(height_text.replace('px', '').replace('%', ''))
                        if height_val < 0:
                            logger.warning("高度值不能为负数")
                            return False
                    except ValueError:
                        logger.warning("高度值格式无效")
                        return False

            return True

        except Exception as e:
            logger.error(f"属性验证失败: {e}")
            return False

    # ==================== 预设管理功能 ====================

    def create_preset_toolbar(self) -> QWidget:
        """创建预设工具栏"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar.setMaximumHeight(50)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(5, 5, 5, 5)

        # 预设选择下拉菜单
        preset_label = QLabel("预设:")
        layout.addWidget(preset_label)

        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(150)
        self.preset_combo.setPlaceholderText("选择预设...")
        self.preset_combo.currentTextChanged.connect(self.on_preset_selected)
        layout.addWidget(self.preset_combo)

        # 应用预设按钮
        apply_preset_btn = QPushButton("应用")
        apply_preset_btn.setMaximumWidth(50)
        apply_preset_btn.clicked.connect(self.apply_selected_preset)
        layout.addWidget(apply_preset_btn)

        layout.addWidget(QFrame())  # 分隔符

        # 保存预设按钮
        save_preset_btn = QPushButton("保存预设")
        save_preset_btn.setMaximumWidth(80)
        save_preset_btn.clicked.connect(self.save_current_as_preset)
        layout.addWidget(save_preset_btn)

        # 管理预设按钮
        manage_preset_btn = QPushButton("管理")
        manage_preset_btn.setMaximumWidth(60)
        manage_preset_btn.clicked.connect(self.show_preset_manager)
        layout.addWidget(manage_preset_btn)

        layout.addStretch()

        # 批量编辑按钮
        batch_edit_btn = QPushButton("批量编辑")
        batch_edit_btn.setMaximumWidth(80)
        batch_edit_btn.clicked.connect(self.show_batch_edit_dialog)
        layout.addWidget(batch_edit_btn)

        return toolbar

    def update_preset_combo(self):
        """更新预设下拉菜单"""
        try:
            self.preset_combo.clear()

            if not self.current_element:
                return

            # 获取适用于当前元素类型的预设
            applicable_presets = self.preset_manager.get_presets_by_element_type(
                self.current_element.element_type
            )

            # 按分类分组显示
            categories = {}
            for preset_name, preset_data in applicable_presets.items():
                category = preset_data.get("category", "custom")
                if category not in categories:
                    categories[category] = []
                categories[category].append(preset_name)

            # 添加到下拉菜单
            for category, preset_names in categories.items():
                category_name = self.preset_manager.categories.get(category, category)

                # 添加分类标题
                self.preset_combo.addItem(f"--- {category_name} ---")
                self.preset_combo.setItemData(self.preset_combo.count() - 1, None)

                # 添加预设项
                for preset_name in sorted(preset_names):
                    self.preset_combo.addItem(preset_name)

        except Exception as e:
            logger.error(f"更新预设下拉菜单失败: {e}")

    def on_preset_selected(self, preset_name: str):
        """预设选择事件"""
        if not preset_name or preset_name.startswith("---"):
            return

        # 更新预设描述（如果有的话）
        preset = self.preset_manager.get_preset(preset_name)
        if preset:
            description = preset.get("description", "")
            self.preset_combo.setToolTip(description)

    def apply_selected_preset(self):
        """应用选中的预设"""
        try:
            preset_name = self.preset_combo.currentText()
            if not preset_name or preset_name.startswith("---"):
                return

            preset = self.preset_manager.get_preset(preset_name)
            if not preset:
                QMessageBox.warning(self, "错误", f"预设不存在: {preset_name}")
                return

            # 应用预设到当前元素
            if self.current_element:
                self.apply_preset_to_element(self.current_element, preset)
                self.preset_applied.emit(preset_name, preset["properties"])
                logger.info(f"预设应用成功: {preset_name}")

        except Exception as e:
            logger.error(f"应用预设失败: {e}")
            QMessageBox.critical(self, "错误", f"应用预设失败:\n{str(e)}")

    def apply_preset_to_element(self, element, preset):
        """将预设应用到元素"""
        try:
            properties = preset["properties"]

            # 应用基本属性
            if hasattr(element, 'name') and "name" in properties:
                element.name = properties["name"]

            # 应用样式属性
            if not hasattr(element, 'style'):
                element.style = ElementStyle()

            style_properties = ["color", "background", "font_size", "font_weight",
                              "text_align", "border_radius", "padding", "margin",
                              "box_shadow", "text_shadow", "line_height"]

            for prop in style_properties:
                if prop in properties:
                    setattr(element.style, prop, properties[prop])

            # 应用变换属性
            if not hasattr(element, 'transform'):
                element.transform = Transform()

            transform_properties = ["position", "left", "top", "right", "bottom",
                                  "transform", "rotation", "scale_x", "scale_y"]

            for prop in transform_properties:
                if prop in properties:
                    if prop in ["left", "top", "right", "bottom"]:
                        # 位置属性需要特殊处理
                        if prop == "left":
                            element.position.x = properties[prop]
                        elif prop == "top":
                            element.position.y = properties[prop]
                    else:
                        setattr(element.transform, prop, properties[prop])

            # 更新UI显示
            self.update_ui_from_element()

        except Exception as e:
            logger.error(f"应用预设到元素失败: {e}")

    def save_current_as_preset(self):
        """将当前属性保存为预设"""
        try:
            if not self.current_element:
                QMessageBox.warning(self, "警告", "没有选中的元素")
                return

            # 显示保存预设对话框
            dialog = SavePresetDialog(self, self.current_element, self.preset_manager)
            if dialog.exec() == dialog.DialogCode.Accepted:
                self.update_preset_combo()
                QMessageBox.information(self, "成功", "预设保存成功")

        except Exception as e:
            logger.error(f"保存预设失败: {e}")
            QMessageBox.critical(self, "错误", f"保存预设失败:\n{str(e)}")

    def show_preset_manager(self):
        """显示预设管理器"""
        try:
            dialog = PresetManagerDialog(self, self.preset_manager)
            if dialog.exec() == dialog.DialogCode.Accepted:
                self.update_preset_combo()

        except Exception as e:
            logger.error(f"显示预设管理器失败: {e}")
            QMessageBox.critical(self, "错误", f"显示预设管理器失败:\n{str(e)}")

    def show_batch_edit_dialog(self):
        """显示批量编辑对话框"""
        try:
            if len(self.selected_elements) < 2:
                QMessageBox.warning(self, "警告", "批量编辑需要选择至少2个元素")
                return

            dialog = BatchEditDialog(self, self.selected_elements)
            if dialog.exec() == dialog.DialogCode.Accepted:
                changes = dialog.get_changes()
                self.batch_update_requested.emit(self.selected_elements, changes)

        except Exception as e:
            logger.error(f"显示批量编辑对话框失败: {e}")
            QMessageBox.critical(self, "错误", f"显示批量编辑对话框失败:\n{str(e)}")

    # ==================== 可视化变换控制 ====================

    def on_visual_transform_changed(self, transform_data: dict):
        """可视化变换改变事件"""
        try:
            if not self.current_element or self.updating:
                return

            # 更新数值控件
            self.updating = True

            if 'position_x' in transform_data:
                self.pos_x_spin.setValue(transform_data['position_x'])
            if 'position_y' in transform_data:
                self.pos_y_spin.setValue(transform_data['position_y'])
            if 'rotation' in transform_data:
                self.rotation_spin.setValue(transform_data['rotation'])
                self.rotation_slider.setValue(int(transform_data['rotation']))
            if 'scale_x' in transform_data:
                self.scale_x_spin.setValue(transform_data['scale_x'])
            if 'scale_y' in transform_data:
                self.scale_y_spin.setValue(transform_data['scale_y'])

            self.updating = False

            # 发送属性改变信号
            self.property_changed.emit()

        except Exception as e:
            logger.error(f"处理可视化变换改变失败: {e}")
            self.updating = False

    def apply_transform_preset(self):
        """应用变换预设"""
        try:
            if not self.current_element:
                return

            preset_name = self.transform_preset_combo.currentText()

            if preset_name == "居中":
                self.pos_x_spin.setValue(0)
                self.pos_y_spin.setValue(0)
            elif preset_name == "左上角":
                self.pos_x_spin.setValue(-400)
                self.pos_y_spin.setValue(-300)
            elif preset_name == "右上角":
                self.pos_x_spin.setValue(400)
                self.pos_y_spin.setValue(-300)
            elif preset_name == "左下角":
                self.pos_x_spin.setValue(-400)
                self.pos_y_spin.setValue(300)
            elif preset_name == "右下角":
                self.pos_x_spin.setValue(400)
                self.pos_y_spin.setValue(300)
            elif preset_name == "放大2倍":
                self.scale_x_spin.setValue(2.0)
                self.scale_y_spin.setValue(2.0)
            elif preset_name == "缩小50%":
                self.scale_x_spin.setValue(0.5)
                self.scale_y_spin.setValue(0.5)
            elif preset_name == "旋转45°":
                self.rotation_spin.setValue(45)
            elif preset_name == "旋转90°":
                self.rotation_spin.setValue(90)
            elif preset_name == "翻转":
                self.scale_x_spin.setValue(-1.0)
                self.scale_y_spin.setValue(1.0)

            # 应用更改
            self.apply_properties()

        except Exception as e:
            logger.error(f"应用变换预设失败: {e}")

    def set_uniform_scale(self, scale_value: float):
        """设置统一缩放"""
        try:
            self.scale_x_spin.setValue(scale_value)
            self.scale_y_spin.setValue(scale_value)
            self.apply_properties()
        except Exception as e:
            logger.error(f"设置统一缩放失败: {e}")

    def update_transform_visualizer(self):
        """更新变换可视化控制器"""
        try:
            if hasattr(self, 'transform_visualizer') and self.current_element:
                self.transform_visualizer.set_element(self.current_element)
        except Exception as e:
            logger.error(f"更新变换可视化控制器失败: {e}")

    # ==================== 样式控制功能 ====================

    def apply_size_preset(self, size_preset: str):
        """应用尺寸预设"""
        try:
            if "x" in size_preset:
                width, height = size_preset.split("x")
                self.width_input.setText(width)
                self.height_input.setText(height)
                self.apply_properties()
        except Exception as e:
            logger.error(f"应用尺寸预设失败: {e}")

    def edit_gradient(self):
        """编辑渐变"""
        try:
            from .advanced_color_picker import AdvancedColorPicker

            dialog = AdvancedColorPicker(self)
            dialog.tab_widget.setCurrentIndex(1)  # 切换到渐变标签页

            if dialog.exec() == dialog.DialogCode.Accepted:
                gradient_data = dialog.get_gradient_data()
                if gradient_data:
                    # 应用渐变到背景
                    self.bg_color_btn.set_gradient(gradient_data)
                    self.apply_properties()

        except Exception as e:
            logger.error(f"编辑渐变失败: {e}")

    def apply_shadow_preset(self, shadow_params: tuple):
        """应用阴影预设"""
        try:
            x, y, blur, spread = shadow_params
            self.shadow_x_spin.setValue(x)
            self.shadow_y_spin.setValue(y)
            self.shadow_blur_spin.setValue(blur)
            self.shadow_spread_spin.setValue(spread)

            if not self.shadow_checkbox.isChecked():
                self.shadow_checkbox.setChecked(True)

            self.apply_properties()

        except Exception as e:
            logger.error(f"应用阴影预设失败: {e}")

    def create_style_preset_toolbar(self) -> QWidget:
        """创建样式预设工具栏"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar.setMaximumHeight(40)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(5, 5, 5, 5)

        # 样式预设下拉菜单
        style_label = QLabel("样式预设:")
        layout.addWidget(style_label)

        self.style_preset_combo = QComboBox()
        self.style_preset_combo.setMinimumWidth(120)
        style_presets = [
            "无预设", "卡片样式", "按钮样式", "标题样式", "强调样式",
            "透明玻璃", "霓虹效果", "阴影浮起", "扁平设计", "材质设计"
        ]
        self.style_preset_combo.addItems(style_presets)
        layout.addWidget(self.style_preset_combo)

        # 应用预设按钮
        apply_style_btn = QPushButton("应用")
        apply_style_btn.setMaximumWidth(50)
        apply_style_btn.clicked.connect(self.apply_style_preset)
        layout.addWidget(apply_style_btn)

        layout.addWidget(QFrame())  # 分隔符

        # 保存样式预设
        save_style_btn = QPushButton("保存样式")
        save_style_btn.setMaximumWidth(80)
        save_style_btn.clicked.connect(self.save_current_style)
        layout.addWidget(save_style_btn)

        # 复制样式
        copy_style_btn = QPushButton("复制")
        copy_style_btn.setMaximumWidth(50)
        copy_style_btn.clicked.connect(self.copy_current_style)
        layout.addWidget(copy_style_btn)

        # 粘贴样式
        paste_style_btn = QPushButton("粘贴")
        paste_style_btn.setMaximumWidth(50)
        paste_style_btn.clicked.connect(self.paste_style)
        layout.addWidget(paste_style_btn)

        layout.addStretch()

        return toolbar

    def apply_style_preset(self):
        """应用样式预设"""
        try:
            preset_name = self.style_preset_combo.currentText()

            if preset_name == "卡片样式":
                self.bg_color_btn.set_color("#ffffff")
                self.border_width_spin.setValue(1)
                self.border_color_btn.set_color("#e0e0e0")
                self.border_radius_spin.setValue(8)
                self.shadow_checkbox.setChecked(True)
                self.apply_shadow_preset((0, 2, 8, 0))

            elif preset_name == "按钮样式":
                self.bg_color_btn.set_color("#2196f3")
                self.text_color_btn.set_color("#ffffff")
                self.border_radius_spin.setValue(4)
                self.shadow_checkbox.setChecked(True)
                self.apply_shadow_preset((0, 2, 4, 0))

            elif preset_name == "标题样式":
                self.text_color_btn.set_color("#333333")
                self.border_bottom_spin.setValue(2)
                self.border_color_btn.set_color("#2196f3")

            elif preset_name == "强调样式":
                self.bg_color_btn.set_color("#ff5722")
                self.text_color_btn.set_color("#ffffff")
                self.border_radius_spin.setValue(20)

            elif preset_name == "透明玻璃":
                self.bg_color_btn.set_color("#ffffff")
                self.opacity_slider.setValue(20)
                self.border_radius_spin.setValue(10)

            elif preset_name == "霓虹效果":
                self.text_color_btn.set_color("#00ffff")
                self.shadow_checkbox.setChecked(True)
                self.shadow_color_btn.set_color("#00ffff")
                self.apply_shadow_preset((0, 0, 10, 0))

            elif preset_name == "阴影浮起":
                self.shadow_checkbox.setChecked(True)
                self.apply_shadow_preset((0, 8, 16, 0))

            elif preset_name == "扁平设计":
                self.border_width_spin.setValue(0)
                self.border_radius_spin.setValue(0)
                self.shadow_checkbox.setChecked(False)

            elif preset_name == "材质设计":
                self.border_radius_spin.setValue(4)
                self.shadow_checkbox.setChecked(True)
                self.apply_shadow_preset((0, 2, 4, 0))

            self.apply_properties()

        except Exception as e:
            logger.error(f"应用样式预设失败: {e}")

    def save_current_style(self):
        """保存当前样式"""
        try:
            if not self.current_element:
                QMessageBox.warning(self, "警告", "没有选中的元素")
                return

            # 创建样式预设保存对话框
            from .save_preset_dialog import SavePresetDialog

            dialog = SavePresetDialog(self, self.current_element, self.preset_manager)
            dialog.category_combo.setCurrentText("样式属性")

            if dialog.exec() == dialog.DialogCode.Accepted:
                QMessageBox.information(self, "成功", "样式预设保存成功")

        except Exception as e:
            logger.error(f"保存当前样式失败: {e}")

    def copy_current_style(self):
        """复制当前样式"""
        try:
            if not self.current_element:
                return

            # 收集样式数据
            style_data = {
                'background_color': self.bg_color_btn.current_color,
                'text_color': self.text_color_btn.current_color,
                'border_color': self.border_color_btn.current_color,
                'border_width': self.border_width_spin.value(),
                'border_style': self.border_style_combo.currentText(),
                'border_radius': self.border_radius_spin.value(),
                'opacity': self.opacity_slider.value(),
                'shadow_enabled': self.shadow_checkbox.isChecked(),
                'shadow_x': self.shadow_x_spin.value(),
                'shadow_y': self.shadow_y_spin.value(),
                'shadow_blur': self.shadow_blur_spin.value(),
                'shadow_color': self.shadow_color_btn.current_color,
            }

            # 保存到剪贴板（简化实现）
            self.copied_style = style_data
            logger.info("样式已复制到剪贴板")

        except Exception as e:
            logger.error(f"复制样式失败: {e}")

    def paste_style(self):
        """粘贴样式"""
        try:
            if not hasattr(self, 'copied_style') or not self.copied_style:
                QMessageBox.information(self, "提示", "剪贴板中没有样式数据")
                return

            # 应用样式数据
            style_data = self.copied_style

            self.bg_color_btn.set_color(style_data.get('background_color', '#ffffff'))
            self.text_color_btn.set_color(style_data.get('text_color', '#000000'))
            self.border_color_btn.set_color(style_data.get('border_color', '#cccccc'))
            self.border_width_spin.setValue(style_data.get('border_width', 0))
            self.border_style_combo.setCurrentText(style_data.get('border_style', 'none'))
            self.border_radius_spin.setValue(style_data.get('border_radius', 0))
            self.opacity_slider.setValue(style_data.get('opacity', 100))
            self.shadow_checkbox.setChecked(style_data.get('shadow_enabled', False))
            self.shadow_x_spin.setValue(style_data.get('shadow_x', 0))
            self.shadow_y_spin.setValue(style_data.get('shadow_y', 0))
            self.shadow_blur_spin.setValue(style_data.get('shadow_blur', 0))
            self.shadow_color_btn.set_color(style_data.get('shadow_color', '#000000'))

            self.apply_properties()
            logger.info("样式粘贴成功")

        except Exception as e:
            logger.error(f"粘贴样式失败: {e}")
            QMessageBox.critical(self, "错误", f"粘贴样式失败:\n{str(e)}")
