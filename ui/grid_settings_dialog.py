"""
AI Animation Studio - 网格设置对话框
提供专业的网格显示控制和配置功能
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QLabel, QPushButton, QCheckBox, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QGridLayout, QComboBox, QSlider, QColorDialog,
                             QFrame, QButtonGroup, QRadioButton, QFormLayout,
                             QMessageBox, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

from core.logger import get_logger

logger = get_logger("grid_settings_dialog")


class GridSettingsDialog(QDialog):
    """网格设置对话框 - 专业版"""
    
    settings_changed = pyqtSignal(dict)  # 设置改变信号
    
    def __init__(self, current_settings: dict, parent=None):
        super().__init__(parent)
        self.current_settings = current_settings.copy()
        self.preview_settings = current_settings.copy()
        
        self.setup_ui()
        self.load_current_settings()
        self.setup_connections()
        
        logger.info("网格设置对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("🔲 网格设置")
        self.setMinimumSize(500, 600)
        self.resize(600, 700)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 基本设置选项卡
        self.create_basic_tab()
        
        # 外观设置选项卡
        self.create_appearance_tab()
        
        # 行为设置选项卡
        self.create_behavior_tab()
        
        # 预设选项卡
        self.create_presets_tab()
        
        # 按钮区域
        self.create_button_area(main_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #495057;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
    
    def create_basic_tab(self):
        """创建基本设置选项卡"""
        basic_widget = QWidget()
        layout = QVBoxLayout(basic_widget)
        
        # 网格显示组
        display_group = QGroupBox("🔲 网格显示")
        display_layout = QFormLayout(display_group)
        
        self.grid_enabled_cb = QCheckBox("启用网格显示")
        display_layout.addRow("显示:", self.grid_enabled_cb)
        
        self.major_grid_enabled_cb = QCheckBox("启用主网格线")
        display_layout.addRow("主网格:", self.major_grid_enabled_cb)
        
        layout.addWidget(display_group)
        
        # 网格尺寸组
        size_group = QGroupBox("📏 网格尺寸")
        size_layout = QFormLayout(size_group)
        
        self.grid_size_spin = QSpinBox()
        self.grid_size_spin.setRange(5, 200)
        self.grid_size_spin.setSuffix(" px")
        size_layout.addRow("网格大小:", self.grid_size_spin)
        
        self.major_interval_spin = QSpinBox()
        self.major_interval_spin.setRange(2, 20)
        self.major_interval_spin.setSuffix(" 格")
        size_layout.addRow("主网格间隔:", self.major_interval_spin)
        
        layout.addWidget(size_group)
        
        # 自适应网格组
        adaptive_group = QGroupBox("🔄 自适应网格")
        adaptive_layout = QFormLayout(adaptive_group)
        
        self.adaptive_grid_cb = QCheckBox("根据缩放自动调整网格密度")
        adaptive_layout.addRow("自适应:", self.adaptive_grid_cb)
        
        layout.addWidget(adaptive_group)
        
        layout.addStretch()
        self.tab_widget.addTab(basic_widget, "基本设置")
    
    def create_appearance_tab(self):
        """创建外观设置选项卡"""
        appearance_widget = QWidget()
        layout = QVBoxLayout(appearance_widget)
        
        # 颜色设置组
        color_group = QGroupBox("🎨 颜色设置")
        color_layout = QFormLayout(color_group)
        
        # 网格颜色
        grid_color_layout = QHBoxLayout()
        self.grid_color_btn = QPushButton("选择颜色")
        self.grid_color_preview = QLabel()
        self.grid_color_preview.setFixedSize(30, 20)
        self.grid_color_preview.setStyleSheet("border: 1px solid #ccc;")
        grid_color_layout.addWidget(self.grid_color_btn)
        grid_color_layout.addWidget(self.grid_color_preview)
        grid_color_layout.addStretch()
        color_layout.addRow("网格颜色:", grid_color_layout)
        
        # 主网格颜色
        major_color_layout = QHBoxLayout()
        self.major_color_btn = QPushButton("选择颜色")
        self.major_color_preview = QLabel()
        self.major_color_preview.setFixedSize(30, 20)
        self.major_color_preview.setStyleSheet("border: 1px solid #ccc;")
        major_color_layout.addWidget(self.major_color_btn)
        major_color_layout.addWidget(self.major_color_preview)
        major_color_layout.addStretch()
        color_layout.addRow("主网格颜色:", major_color_layout)
        
        layout.addWidget(color_group)
        
        # 样式设置组
        style_group = QGroupBox("✨ 样式设置")
        style_layout = QFormLayout(style_group)
        
        self.grid_style_combo = QComboBox()
        self.grid_style_combo.addItems(["实线", "点线", "虚线"])
        style_layout.addRow("线条样式:", self.grid_style_combo)
        
        # 透明度滑块
        opacity_layout = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_label = QLabel("80%")
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        style_layout.addRow("透明度:", opacity_layout)
        
        layout.addWidget(style_group)
        
        layout.addStretch()
        self.tab_widget.addTab(appearance_widget, "外观设置")
    
    def create_behavior_tab(self):
        """创建行为设置选项卡"""
        behavior_widget = QWidget()
        layout = QVBoxLayout(behavior_widget)
        
        # 对齐设置组
        snap_group = QGroupBox("🧲 对齐设置")
        snap_layout = QFormLayout(snap_group)
        
        self.snap_to_grid_cb = QCheckBox("启用网格对齐")
        snap_layout.addRow("网格对齐:", self.snap_to_grid_cb)
        
        self.snap_threshold_spin = QSpinBox()
        self.snap_threshold_spin.setRange(1, 50)
        self.snap_threshold_spin.setSuffix(" px")
        snap_layout.addRow("对齐阈值:", self.snap_threshold_spin)
        
        layout.addWidget(snap_group)
        
        layout.addStretch()
        self.tab_widget.addTab(behavior_widget, "行为设置")
    
    def create_presets_tab(self):
        """创建预设选项卡"""
        presets_widget = QWidget()
        layout = QVBoxLayout(presets_widget)
        
        # 预设选择组
        presets_group = QGroupBox("📋 网格预设")
        presets_layout = QVBoxLayout(presets_group)
        
        # 预设按钮组
        self.preset_group = QButtonGroup()
        
        self.fine_preset_rb = QRadioButton("精细网格 (10px)")
        self.normal_preset_rb = QRadioButton("标准网格 (20px)")
        self.coarse_preset_rb = QRadioButton("粗糙网格 (50px)")
        self.custom_preset_rb = QRadioButton("自定义设置")
        
        self.preset_group.addButton(self.fine_preset_rb, 0)
        self.preset_group.addButton(self.normal_preset_rb, 1)
        self.preset_group.addButton(self.coarse_preset_rb, 2)
        self.preset_group.addButton(self.custom_preset_rb, 3)
        
        presets_layout.addWidget(self.fine_preset_rb)
        presets_layout.addWidget(self.normal_preset_rb)
        presets_layout.addWidget(self.coarse_preset_rb)
        presets_layout.addWidget(self.custom_preset_rb)
        
        # 预设操作按钮
        preset_btn_layout = QHBoxLayout()
        self.apply_preset_btn = QPushButton("应用预设")
        self.save_preset_btn = QPushButton("保存为预设")
        self.reset_preset_btn = QPushButton("重置为默认")
        
        preset_btn_layout.addWidget(self.apply_preset_btn)
        preset_btn_layout.addWidget(self.save_preset_btn)
        preset_btn_layout.addWidget(self.reset_preset_btn)
        presets_layout.addLayout(preset_btn_layout)
        
        layout.addWidget(presets_group)
        
        layout.addStretch()
        self.tab_widget.addTab(presets_widget, "预设管理")
    
    def create_button_area(self, parent_layout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("🔍 预览")
        self.apply_btn = QPushButton("✅ 应用")
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        
        # 设置按钮样式
        self.preview_btn.setStyleSheet("background-color: #17a2b8;")
        self.apply_btn.setStyleSheet("background-color: #28a745;")
        self.cancel_btn.setStyleSheet("background-color: #6c757d;")
        
        button_layout.addWidget(self.preview_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        parent_layout.addLayout(button_layout)
    
    def setup_connections(self):
        """设置信号连接"""
        # 基本设置
        self.grid_enabled_cb.toggled.connect(self.on_setting_changed)
        self.major_grid_enabled_cb.toggled.connect(self.on_setting_changed)
        self.grid_size_spin.valueChanged.connect(self.on_setting_changed)
        self.major_interval_spin.valueChanged.connect(self.on_setting_changed)
        self.adaptive_grid_cb.toggled.connect(self.on_setting_changed)
        
        # 外观设置
        self.grid_color_btn.clicked.connect(self.choose_grid_color)
        self.major_color_btn.clicked.connect(self.choose_major_color)
        self.grid_style_combo.currentTextChanged.connect(self.on_setting_changed)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        
        # 行为设置
        self.snap_to_grid_cb.toggled.connect(self.on_setting_changed)
        self.snap_threshold_spin.valueChanged.connect(self.on_setting_changed)
        
        # 预设管理
        self.preset_group.buttonClicked.connect(self.on_preset_selected)
        self.apply_preset_btn.clicked.connect(self.apply_preset)
        self.save_preset_btn.clicked.connect(self.save_preset)
        self.reset_preset_btn.clicked.connect(self.reset_to_default)
        
        # 按钮操作
        self.preview_btn.clicked.connect(self.preview_settings)
        self.apply_btn.clicked.connect(self.apply_settings)
        self.ok_btn.clicked.connect(self.accept_settings)
        self.cancel_btn.clicked.connect(self.reject)
    
    def load_current_settings(self):
        """加载当前设置"""
        try:
            settings = self.current_settings
            
            # 基本设置
            self.grid_enabled_cb.setChecked(settings.get("enabled", True))
            self.major_grid_enabled_cb.setChecked(settings.get("major_enabled", True))
            self.grid_size_spin.setValue(settings.get("size", 20))
            self.major_interval_spin.setValue(settings.get("major_interval", 5))
            self.adaptive_grid_cb.setChecked(settings.get("adaptive", True))
            
            # 外观设置
            self.update_color_preview(self.grid_color_preview, QColor(settings.get("color", "#e0e0e0")))
            self.update_color_preview(self.major_color_preview, QColor(settings.get("major_color", "#c0c0c0")))
            
            style_map = {"solid": "实线", "dotted": "点线", "dashed": "虚线"}
            style_text = style_map.get(settings.get("style", "solid"), "实线")
            self.grid_style_combo.setCurrentText(style_text)
            
            opacity_value = int(settings.get("opacity", 0.8) * 100)
            self.opacity_slider.setValue(opacity_value)
            self.opacity_label.setText(f"{opacity_value}%")
            
            # 行为设置
            self.snap_to_grid_cb.setChecked(settings.get("snap_enabled", True))
            self.snap_threshold_spin.setValue(settings.get("snap_threshold", 10))
            
            # 预设选择
            grid_size = settings.get("size", 20)
            if grid_size == 10:
                self.fine_preset_rb.setChecked(True)
            elif grid_size == 20:
                self.normal_preset_rb.setChecked(True)
            elif grid_size == 50:
                self.coarse_preset_rb.setChecked(True)
            else:
                self.custom_preset_rb.setChecked(True)
            
            logger.info("网格设置加载完成")
            
        except Exception as e:
            logger.error(f"加载网格设置失败: {e}")
    
    def update_color_preview(self, preview_label, color):
        """更新颜色预览"""
        preview_label.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
    
    def choose_grid_color(self):
        """选择网格颜色"""
        current_color = QColor(self.current_settings.get("color", "#e0e0e0"))
        color = QColorDialog.getColor(current_color, self, "选择网格颜色")
        if color.isValid():
            self.update_color_preview(self.grid_color_preview, color)
            self.on_setting_changed()
    
    def choose_major_color(self):
        """选择主网格颜色"""
        current_color = QColor(self.current_settings.get("major_color", "#c0c0c0"))
        color = QColorDialog.getColor(current_color, self, "选择主网格颜色")
        if color.isValid():
            self.update_color_preview(self.major_color_preview, color)
            self.on_setting_changed()
    
    def on_opacity_changed(self, value):
        """透明度改变"""
        self.opacity_label.setText(f"{value}%")
        self.on_setting_changed()
    
    def on_setting_changed(self):
        """设置改变"""
        # 更新预览设置
        self.update_preview_settings()
        
        # 如果不是预设，选择自定义
        if not self.custom_preset_rb.isChecked():
            self.custom_preset_rb.setChecked(True)
    
    def update_preview_settings(self):
        """更新预览设置"""
        style_map = {"实线": "solid", "点线": "dotted", "虚线": "dashed"}
        
        self.preview_settings = {
            "enabled": self.grid_enabled_cb.isChecked(),
            "size": self.grid_size_spin.value(),
            "color": self.grid_color_preview.styleSheet().split("background-color: ")[1].split(";")[0],
            "major_enabled": self.major_grid_enabled_cb.isChecked(),
            "major_interval": self.major_interval_spin.value(),
            "major_color": self.major_color_preview.styleSheet().split("background-color: ")[1].split(";")[0],
            "style": style_map.get(self.grid_style_combo.currentText(), "solid"),
            "opacity": self.opacity_slider.value() / 100.0,
            "adaptive": self.adaptive_grid_cb.isChecked(),
            "snap_enabled": self.snap_to_grid_cb.isChecked(),
            "snap_threshold": self.snap_threshold_spin.value()
        }
    
    def on_preset_selected(self, button):
        """预设选择"""
        preset_id = self.preset_group.id(button)
        if preset_id == 0:  # 精细
            self.apply_preset_values(10, 5)
        elif preset_id == 1:  # 标准
            self.apply_preset_values(20, 5)
        elif preset_id == 2:  # 粗糙
            self.apply_preset_values(50, 4)
        # 自定义不做任何操作
    
    def apply_preset_values(self, size, interval):
        """应用预设值"""
        self.grid_size_spin.setValue(size)
        self.major_interval_spin.setValue(interval)
    
    def apply_preset(self):
        """应用预设"""
        selected_button = self.preset_group.checkedButton()
        if selected_button:
            self.on_preset_selected(selected_button)
            QMessageBox.information(self, "预设应用", "预设已应用到当前设置")
    
    def save_preset(self):
        """保存为预设"""
        # 这里可以实现保存用户自定义预设的功能
        QMessageBox.information(self, "保存预设", "自定义预设保存功能正在开发中...")
    
    def reset_to_default(self):
        """重置为默认"""
        default_settings = {
            "enabled": True,
            "size": 20,
            "color": "#e0e0e0",
            "major_enabled": True,
            "major_interval": 5,
            "major_color": "#c0c0c0",
            "style": "solid",
            "opacity": 0.8,
            "adaptive": True,
            "snap_enabled": True,
            "snap_threshold": 10
        }
        
        self.current_settings = default_settings
        self.load_current_settings()
        QMessageBox.information(self, "重置设置", "已重置为默认设置")
    
    def preview_settings(self):
        """预览设置"""
        self.update_preview_settings()
        self.settings_changed.emit(self.preview_settings)
        logger.info("预览网格设置")
    
    def apply_settings(self):
        """应用设置"""
        self.update_preview_settings()
        self.current_settings = self.preview_settings.copy()
        self.settings_changed.emit(self.current_settings)
        logger.info("应用网格设置")
    
    def accept_settings(self):
        """确定设置"""
        self.apply_settings()
        self.accept()
    
    def get_settings(self):
        """获取当前设置"""
        return self.current_settings.copy()
