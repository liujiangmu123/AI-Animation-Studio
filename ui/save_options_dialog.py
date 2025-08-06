"""
AI Animation Studio - 保存选项对话框
提供高级保存选项，包括格式选择、项目打包、导出设置等
"""

from typing import Dict, Any, Optional
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit,
    QTextEdit, QFileDialog, QProgressBar, QTabWidget, QWidget, QSlider,
    QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from core.logger import get_logger

logger = get_logger("save_options_dialog")


class SaveOptionsDialog(QDialog):
    """保存选项对话框"""
    
    def __init__(self, parent=None, current_project=None):
        super().__init__(parent)
        self.current_project = current_project
        self.save_options = {}
        
        self.setWindowTitle("保存选项")
        self.setMinimumSize(500, 600)
        self.resize(600, 700)
        
        self.setup_ui()
        self.load_default_options()
        
        logger.info("保存选项对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("项目保存选项")
        title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 基本选项选项卡
        self.setup_basic_options_tab()
        
        # 格式选项选项卡
        self.setup_format_options_tab()
        
        # 打包选项选项卡
        self.setup_package_options_tab()
        
        # 高级选项选项卡
        self.setup_advanced_options_tab()
        
        layout.addWidget(self.tab_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        # 预设按钮
        preset_button = QPushButton("加载预设")
        preset_button.clicked.connect(self.load_preset)
        button_layout.addWidget(preset_button)
        
        save_preset_button = QPushButton("保存预设")
        save_preset_button.clicked.connect(self.save_preset)
        button_layout.addWidget(save_preset_button)
        
        button_layout.addStretch()
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        self.save_button = QPushButton("保存")
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
    
    def setup_basic_options_tab(self):
        """设置基本选项选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 文件信息组
        file_group = QGroupBox("文件信息")
        file_layout = QGridLayout(file_group)
        
        # 项目名称
        file_layout.addWidget(QLabel("项目名称:"), 0, 0)
        self.project_name_edit = QLineEdit()
        if self.current_project:
            self.project_name_edit.setText(self.current_project.name)
        file_layout.addWidget(self.project_name_edit, 0, 1)
        
        # 项目描述
        file_layout.addWidget(QLabel("项目描述:"), 1, 0)
        self.project_description_edit = QTextEdit()
        self.project_description_edit.setMaximumHeight(80)
        if self.current_project:
            self.project_description_edit.setPlainText(self.current_project.description)
        file_layout.addWidget(self.project_description_edit, 1, 1)
        
        # 作者信息
        file_layout.addWidget(QLabel("作者:"), 2, 0)
        self.author_edit = QLineEdit()
        file_layout.addWidget(self.author_edit, 2, 1)
        
        # 版本号
        file_layout.addWidget(QLabel("版本:"), 3, 0)
        self.version_edit = QLineEdit("1.0")
        file_layout.addWidget(self.version_edit, 3, 1)
        
        layout.addWidget(file_group)
        
        # 保存选项组
        save_group = QGroupBox("保存选项")
        save_layout = QVBoxLayout(save_group)
        
        self.create_backup_checkbox = QCheckBox("创建备份文件")
        self.create_backup_checkbox.setChecked(True)
        save_layout.addWidget(self.create_backup_checkbox)
        
        self.incremental_save_checkbox = QCheckBox("使用增量保存")
        self.incremental_save_checkbox.setChecked(True)
        save_layout.addWidget(self.incremental_save_checkbox)
        
        self.generate_thumbnail_checkbox = QCheckBox("生成缩略图")
        self.generate_thumbnail_checkbox.setChecked(True)
        save_layout.addWidget(self.generate_thumbnail_checkbox)
        
        self.compress_data_checkbox = QCheckBox("压缩项目数据")
        self.compress_data_checkbox.setChecked(False)
        save_layout.addWidget(self.compress_data_checkbox)
        
        layout.addWidget(save_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "基本选项")
    
    def setup_format_options_tab(self):
        """设置格式选项选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 文件格式组
        format_group = QGroupBox("文件格式")
        format_layout = QVBoxLayout(format_group)
        
        self.format_button_group = QButtonGroup()
        
        # AAS格式（默认）
        aas_radio = QRadioButton("AAS格式 (推荐)")
        aas_radio.setChecked(True)
        aas_radio.setToolTip("AI Animation Studio原生格式，支持所有功能")
        self.format_button_group.addButton(aas_radio, 0)
        format_layout.addWidget(aas_radio)
        
        # JSON格式
        json_radio = QRadioButton("JSON格式")
        json_radio.setToolTip("通用JSON格式，便于其他工具读取")
        self.format_button_group.addButton(json_radio, 1)
        format_layout.addWidget(json_radio)
        
        # 压缩格式
        zip_radio = QRadioButton("压缩包格式")
        zip_radio.setToolTip("包含所有资源的压缩包")
        self.format_button_group.addButton(zip_radio, 2)
        format_layout.addWidget(zip_radio)
        
        layout.addWidget(format_group)
        
        # 编码选项组
        encoding_group = QGroupBox("编码选项")
        encoding_layout = QGridLayout(encoding_group)
        
        encoding_layout.addWidget(QLabel("字符编码:"), 0, 0)
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["UTF-8", "UTF-16", "ASCII"])
        encoding_layout.addWidget(self.encoding_combo, 0, 1)
        
        encoding_layout.addWidget(QLabel("换行符:"), 1, 0)
        self.line_ending_combo = QComboBox()
        self.line_ending_combo.addItems(["系统默认", "LF (Unix)", "CRLF (Windows)", "CR (Mac)"])
        encoding_layout.addWidget(self.line_ending_combo, 1, 1)
        
        layout.addWidget(encoding_group)
        
        # JSON格式化选项
        json_group = QGroupBox("JSON格式化")
        json_layout = QVBoxLayout(json_group)
        
        self.pretty_print_checkbox = QCheckBox("美化输出（缩进格式）")
        self.pretty_print_checkbox.setChecked(True)
        json_layout.addWidget(self.pretty_print_checkbox)
        
        indent_layout = QHBoxLayout()
        indent_layout.addWidget(QLabel("缩进空格数:"))
        self.indent_spinbox = QSpinBox()
        self.indent_spinbox.setRange(0, 8)
        self.indent_spinbox.setValue(2)
        indent_layout.addWidget(self.indent_spinbox)
        indent_layout.addStretch()
        json_layout.addLayout(indent_layout)
        
        layout.addWidget(json_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "格式选项")
    
    def setup_package_options_tab(self):
        """设置打包选项选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 打包内容组
        content_group = QGroupBox("打包内容")
        content_layout = QVBoxLayout(content_group)
        
        self.include_assets_checkbox = QCheckBox("包含资源文件")
        self.include_assets_checkbox.setChecked(True)
        self.include_assets_checkbox.setToolTip("包含图片、音频等资源文件")
        content_layout.addWidget(self.include_assets_checkbox)
        
        self.include_libraries_checkbox = QCheckBox("包含JavaScript库")
        self.include_libraries_checkbox.setChecked(False)
        self.include_libraries_checkbox.setToolTip("包含项目使用的JavaScript库文件")
        content_layout.addWidget(self.include_libraries_checkbox)
        
        self.include_templates_checkbox = QCheckBox("包含模板文件")
        self.include_templates_checkbox.setChecked(False)
        self.include_templates_checkbox.setToolTip("包含项目使用的模板文件")
        content_layout.addWidget(self.include_templates_checkbox)
        
        self.include_export_html_checkbox = QCheckBox("包含导出的HTML")
        self.include_export_html_checkbox.setChecked(False)
        self.include_export_html_checkbox.setToolTip("自动导出HTML并包含在包中")
        content_layout.addWidget(self.include_export_html_checkbox)
        
        layout.addWidget(content_group)
        
        # 压缩选项组
        compression_group = QGroupBox("压缩选项")
        compression_layout = QGridLayout(compression_group)
        
        compression_layout.addWidget(QLabel("压缩级别:"), 0, 0)
        self.compression_slider = QSlider(Qt.Orientation.Horizontal)
        self.compression_slider.setRange(0, 9)
        self.compression_slider.setValue(6)
        self.compression_slider.valueChanged.connect(self.update_compression_label)
        compression_layout.addWidget(self.compression_slider, 0, 1)
        
        self.compression_label = QLabel("标准")
        compression_layout.addWidget(self.compression_label, 0, 2)
        
        layout.addWidget(compression_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "打包选项")
    
    def setup_advanced_options_tab(self):
        """设置高级选项选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 性能选项组
        performance_group = QGroupBox("性能选项")
        performance_layout = QGridLayout(performance_group)
        
        performance_layout.addWidget(QLabel("内存限制 (MB):"), 0, 0)
        self.memory_limit_spinbox = QSpinBox()
        self.memory_limit_spinbox.setRange(128, 4096)
        self.memory_limit_spinbox.setValue(512)
        performance_layout.addWidget(self.memory_limit_spinbox, 0, 1)
        
        performance_layout.addWidget(QLabel("线程数:"), 1, 0)
        self.thread_count_spinbox = QSpinBox()
        self.thread_count_spinbox.setRange(1, 16)
        self.thread_count_spinbox.setValue(4)
        performance_layout.addWidget(self.thread_count_spinbox, 1, 1)
        
        layout.addWidget(performance_group)
        
        # 验证选项组
        validation_group = QGroupBox("验证选项")
        validation_layout = QVBoxLayout(validation_group)
        
        self.validate_data_checkbox = QCheckBox("保存前验证数据")
        self.validate_data_checkbox.setChecked(True)
        validation_layout.addWidget(self.validate_data_checkbox)
        
        self.check_references_checkbox = QCheckBox("检查资源引用")
        self.check_references_checkbox.setChecked(True)
        validation_layout.addWidget(self.check_references_checkbox)
        
        self.optimize_data_checkbox = QCheckBox("优化数据结构")
        self.optimize_data_checkbox.setChecked(False)
        validation_layout.addWidget(self.optimize_data_checkbox)
        
        layout.addWidget(validation_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "高级选项")
    
    def update_compression_label(self, value):
        """更新压缩级别标签"""
        labels = ["无压缩", "最快", "快速", "标准", "标准", "标准", "标准", "高压缩", "高压缩", "最高压缩"]
        self.compression_label.setText(labels[value])
    
    def load_default_options(self):
        """加载默认选项"""
        # 这里可以从配置文件加载默认选项
        pass
    
    def load_preset(self):
        """加载预设"""
        # 实现预设加载逻辑
        pass
    
    def save_preset(self):
        """保存预设"""
        # 实现预设保存逻辑
        pass
    
    def get_save_options(self) -> Dict[str, Any]:
        """获取保存选项"""
        options = {
            # 基本选项
            "project_name": self.project_name_edit.text(),
            "project_description": self.project_description_edit.toPlainText(),
            "author": self.author_edit.text(),
            "version": self.version_edit.text(),
            "create_backup": self.create_backup_checkbox.isChecked(),
            "incremental_save": self.incremental_save_checkbox.isChecked(),
            "generate_thumbnail": self.generate_thumbnail_checkbox.isChecked(),
            "compress_data": self.compress_data_checkbox.isChecked(),
            
            # 格式选项
            "file_format": self.format_button_group.checkedId(),
            "encoding": self.encoding_combo.currentText(),
            "line_ending": self.line_ending_combo.currentText(),
            "pretty_print": self.pretty_print_checkbox.isChecked(),
            "indent_size": self.indent_spinbox.value(),
            
            # 打包选项
            "include_assets": self.include_assets_checkbox.isChecked(),
            "include_libraries": self.include_libraries_checkbox.isChecked(),
            "include_templates": self.include_templates_checkbox.isChecked(),
            "include_export_html": self.include_export_html_checkbox.isChecked(),
            "compression_level": self.compression_slider.value(),
            
            # 高级选项
            "memory_limit": self.memory_limit_spinbox.value(),
            "thread_count": self.thread_count_spinbox.value(),
            "validate_data": self.validate_data_checkbox.isChecked(),
            "check_references": self.check_references_checkbox.isChecked(),
            "optimize_data": self.optimize_data_checkbox.isChecked(),
        }
        
        return options
