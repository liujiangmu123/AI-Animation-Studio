"""
AI Animation Studio - 另存为对话框
提供增强的另存为功能，支持多种格式和选项
"""

from typing import Dict, Any, Optional
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QComboBox, QLineEdit, QTabWidget, QWidget,
    QFileDialog, QTextEdit, QSpinBox, QProgressBar, QListWidget,
    QListWidgetItem, QFrame, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QIcon

from core.logger import get_logger

logger = get_logger("save_as_dialog")


class SaveAsDialog(QDialog):
    """增强的另存为对话框"""
    
    def __init__(self, parent=None, current_project=None):
        super().__init__(parent)
        self.current_project = current_project
        self.save_options = {}
        
        self.setWindowTitle("另存为")
        self.setMinimumSize(600, 700)
        self.resize(700, 800)
        
        self.setup_ui()
        self.load_default_options()
        
        logger.info("另存为对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("另存为项目")
        title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 文件信息组
        file_group = QGroupBox("文件信息")
        file_layout = QGridLayout(file_group)
        
        # 项目名称
        file_layout.addWidget(QLabel("项目名称:"), 0, 0)
        self.project_name_edit = QLineEdit()
        if self.current_project:
            self.project_name_edit.setText(self.current_project.name)
        file_layout.addWidget(self.project_name_edit, 0, 1)
        
        # 保存位置
        file_layout.addWidget(QLabel("保存位置:"), 1, 0)
        location_layout = QHBoxLayout()
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("选择保存位置...")
        location_layout.addWidget(self.location_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_location)
        location_layout.addWidget(browse_btn)
        
        file_layout.addLayout(location_layout, 1, 1)
        
        # 文件格式
        file_layout.addWidget(QLabel("文件格式:"), 2, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "AAS项目文件 (*.aas)",
            "JSON格式 (*.json)", 
            "压缩包 (*.zip)",
            "XML格式 (*.xml)",
            "HTML包 (*.html)",
            "可执行文件 (*.exe)"
        ])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        file_layout.addWidget(self.format_combo, 2, 1)
        
        layout.addWidget(file_group)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 基本选项
        self.setup_basic_options_tab()
        
        # 内容选项
        self.setup_content_options_tab()
        
        # 高级选项
        self.setup_advanced_options_tab()
        
        # 格式特定选项
        self.setup_format_specific_tab()
        
        layout.addWidget(self.tab_widget)
        
        # 预览区域
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        # 预览按钮
        preview_button = QPushButton("预览")
        preview_button.clicked.connect(self.update_preview)
        button_layout.addWidget(preview_button)
        
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
        """设置基本选项"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 项目信息组
        info_group = QGroupBox("项目信息")
        info_layout = QGridLayout(info_group)
        
        info_layout.addWidget(QLabel("描述:"), 0, 0)
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        if self.current_project and hasattr(self.current_project, 'description'):
            self.description_edit.setPlainText(self.current_project.description)
        info_layout.addWidget(self.description_edit, 0, 1)
        
        info_layout.addWidget(QLabel("作者:"), 1, 0)
        self.author_edit = QLineEdit()
        if self.current_project and hasattr(self.current_project, 'author'):
            self.author_edit.setText(self.current_project.author)
        info_layout.addWidget(self.author_edit, 1, 1)
        
        info_layout.addWidget(QLabel("版本:"), 2, 0)
        self.version_edit = QLineEdit()
        self.version_edit.setText("1.0")
        if self.current_project and hasattr(self.current_project, 'version'):
            self.version_edit.setText(self.current_project.version)
        info_layout.addWidget(self.version_edit, 2, 1)
        
        layout.addWidget(info_group)
        
        # 保存选项组
        save_group = QGroupBox("保存选项")
        save_layout = QVBoxLayout(save_group)
        
        self.create_backup_cb = QCheckBox("创建备份")
        self.create_backup_cb.setChecked(True)
        save_layout.addWidget(self.create_backup_cb)
        
        self.incremental_save_cb = QCheckBox("增量保存")
        self.incremental_save_cb.setChecked(True)
        save_layout.addWidget(self.incremental_save_cb)
        
        self.compress_cb = QCheckBox("压缩文件")
        self.compress_cb.setChecked(True)
        save_layout.addWidget(self.compress_cb)
        
        layout.addWidget(save_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "基本选项")
    
    def setup_content_options_tab(self):
        """设置内容选项"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 包含内容组
        content_group = QGroupBox("包含内容")
        content_layout = QVBoxLayout(content_group)
        
        self.include_elements_cb = QCheckBox("包含元素")
        self.include_elements_cb.setChecked(True)
        content_layout.addWidget(self.include_elements_cb)
        
        self.include_timeline_cb = QCheckBox("包含时间轴")
        self.include_timeline_cb.setChecked(True)
        content_layout.addWidget(self.include_timeline_cb)
        
        self.include_assets_cb = QCheckBox("包含资源文件")
        self.include_assets_cb.setChecked(True)
        content_layout.addWidget(self.include_assets_cb)
        
        self.include_settings_cb = QCheckBox("包含项目设置")
        self.include_settings_cb.setChecked(True)
        content_layout.addWidget(self.include_settings_cb)
        
        self.include_history_cb = QCheckBox("包含操作历史")
        self.include_history_cb.setChecked(False)
        content_layout.addWidget(self.include_history_cb)
        
        self.include_metadata_cb = QCheckBox("包含元数据")
        self.include_metadata_cb.setChecked(True)
        content_layout.addWidget(self.include_metadata_cb)
        
        layout.addWidget(content_group)
        
        # 资源处理组
        assets_group = QGroupBox("资源处理")
        assets_layout = QVBoxLayout(assets_group)
        
        self.embed_assets_cb = QCheckBox("嵌入资源文件")
        self.embed_assets_cb.setChecked(False)
        assets_layout.addWidget(self.embed_assets_cb)
        
        self.optimize_assets_cb = QCheckBox("优化资源文件")
        self.optimize_assets_cb.setChecked(True)
        assets_layout.addWidget(self.optimize_assets_cb)
        
        # 资源质量
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("资源质量:"))
        self.asset_quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.asset_quality_slider.setRange(1, 10)
        self.asset_quality_slider.setValue(8)
        self.asset_quality_slider.valueChanged.connect(self.update_quality_label)
        quality_layout.addWidget(self.asset_quality_slider)
        
        self.quality_label = QLabel("高 (8)")
        quality_layout.addWidget(self.quality_label)
        
        assets_layout.addLayout(quality_layout)
        
        layout.addWidget(assets_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "内容选项")
    
    def setup_advanced_options_tab(self):
        """设置高级选项"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 兼容性组
        compat_group = QGroupBox("兼容性")
        compat_layout = QVBoxLayout(compat_group)
        
        compat_layout.addWidget(QLabel("目标版本:"))
        self.target_version_combo = QComboBox()
        self.target_version_combo.addItems([
            "当前版本", "1.0", "0.9", "0.8"
        ])
        compat_layout.addWidget(self.target_version_combo)
        
        self.backward_compat_cb = QCheckBox("向后兼容")
        self.backward_compat_cb.setChecked(True)
        compat_layout.addWidget(self.backward_compat_cb)
        
        layout.addWidget(compat_group)
        
        # 安全选项组
        security_group = QGroupBox("安全选项")
        security_layout = QVBoxLayout(security_group)
        
        self.encrypt_cb = QCheckBox("加密文件")
        self.encrypt_cb.setChecked(False)
        security_layout.addWidget(self.encrypt_cb)
        
        # 密码设置
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("密码:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setEnabled(False)
        password_layout.addWidget(self.password_edit)
        
        self.encrypt_cb.toggled.connect(self.password_edit.setEnabled)
        
        security_layout.addLayout(password_layout)
        
        layout.addWidget(security_group)
        
        # 性能选项组
        performance_group = QGroupBox("性能选项")
        performance_layout = QVBoxLayout(performance_group)
        
        # 压缩级别
        compression_layout = QHBoxLayout()
        compression_layout.addWidget(QLabel("压缩级别:"))
        self.compression_slider = QSlider(Qt.Orientation.Horizontal)
        self.compression_slider.setRange(1, 9)
        self.compression_slider.setValue(6)
        self.compression_slider.valueChanged.connect(self.update_compression_label)
        compression_layout.addWidget(self.compression_slider)
        
        self.compression_label = QLabel("标准 (6)")
        compression_layout.addWidget(self.compression_label)
        
        performance_layout.addLayout(compression_layout)
        
        # 多线程处理
        self.multithread_cb = QCheckBox("多线程处理")
        self.multithread_cb.setChecked(True)
        performance_layout.addWidget(self.multithread_cb)
        
        layout.addWidget(performance_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "高级选项")
    
    def setup_format_specific_tab(self):
        """设置格式特定选项"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 格式特定选项组
        self.format_options_group = QGroupBox("格式选项")
        self.format_options_layout = QVBoxLayout(self.format_options_group)
        
        # 默认显示AAS选项
        self.setup_aas_options()
        
        layout.addWidget(self.format_options_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "格式选项")
    
    def setup_aas_options(self):
        """设置AAS格式选项"""
        # 清除现有选项
        self.clear_format_options()
        
        self.aas_version_combo = QComboBox()
        self.aas_version_combo.addItems(["2.0", "1.5", "1.0"])
        
        layout = QHBoxLayout()
        layout.addWidget(QLabel("AAS版本:"))
        layout.addWidget(self.aas_version_combo)
        layout.addStretch()
        
        self.format_options_layout.addLayout(layout)
    
    def clear_format_options(self):
        """清除格式选项"""
        while self.format_options_layout.count():
            child = self.format_options_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def browse_location(self):
        """浏览保存位置"""
        current_format = self.format_combo.currentText()
        
        # 根据格式设置文件过滤器
        if "AAS" in current_format:
            file_filter = "AAS项目文件 (*.aas)"
            default_ext = ".aas"
        elif "JSON" in current_format:
            file_filter = "JSON文件 (*.json)"
            default_ext = ".json"
        elif "压缩包" in current_format:
            file_filter = "压缩包 (*.zip)"
            default_ext = ".zip"
        elif "XML" in current_format:
            file_filter = "XML文件 (*.xml)"
            default_ext = ".xml"
        elif "HTML" in current_format:
            file_filter = "HTML包 (*.html)"
            default_ext = ".html"
        else:
            file_filter = "所有文件 (*.*)"
            default_ext = ""
        
        # 构建默认文件名
        project_name = self.project_name_edit.text() or "untitled"
        if not project_name.endswith(default_ext):
            project_name += default_ext
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "选择保存位置", project_name, file_filter
        )
        
        if file_path:
            self.location_edit.setText(file_path)
    
    def on_format_changed(self, format_text):
        """格式改变事件"""
        # 根据格式更新特定选项
        if "AAS" in format_text:
            self.setup_aas_options()
        elif "JSON" in format_text:
            self.setup_json_options()
        elif "压缩包" in format_text:
            self.setup_zip_options()
        elif "XML" in format_text:
            self.setup_xml_options()
        elif "HTML" in format_text:
            self.setup_html_options()
        elif "可执行文件" in format_text:
            self.setup_exe_options()
    
    def setup_json_options(self):
        """设置JSON格式选项"""
        self.clear_format_options()
        
        self.json_indent_cb = QCheckBox("格式化输出")
        self.json_indent_cb.setChecked(True)
        self.format_options_layout.addWidget(self.json_indent_cb)
        
        self.json_minify_cb = QCheckBox("压缩JSON")
        self.json_minify_cb.setChecked(False)
        self.format_options_layout.addWidget(self.json_minify_cb)
    
    def setup_zip_options(self):
        """设置ZIP格式选项"""
        self.clear_format_options()
        
        self.include_readme_cb = QCheckBox("包含README文件")
        self.include_readme_cb.setChecked(True)
        self.format_options_layout.addWidget(self.include_readme_cb)
        
        self.include_license_cb = QCheckBox("包含许可证文件")
        self.include_license_cb.setChecked(False)
        self.format_options_layout.addWidget(self.include_license_cb)
    
    def setup_xml_options(self):
        """设置XML格式选项"""
        self.clear_format_options()
        
        self.xml_pretty_cb = QCheckBox("格式化XML")
        self.xml_pretty_cb.setChecked(True)
        self.format_options_layout.addWidget(self.xml_pretty_cb)
    
    def setup_html_options(self):
        """设置HTML格式选项"""
        self.clear_format_options()
        
        self.html_standalone_cb = QCheckBox("独立HTML文件")
        self.html_standalone_cb.setChecked(True)
        self.format_options_layout.addWidget(self.html_standalone_cb)
        
        self.html_minify_cb = QCheckBox("压缩HTML")
        self.html_minify_cb.setChecked(False)
        self.format_options_layout.addWidget(self.html_minify_cb)
    
    def setup_exe_options(self):
        """设置可执行文件选项"""
        self.clear_format_options()
        
        self.exe_console_cb = QCheckBox("显示控制台")
        self.exe_console_cb.setChecked(False)
        self.format_options_layout.addWidget(self.exe_console_cb)
    
    def update_quality_label(self, value):
        """更新质量标签"""
        labels = {
            1: "最低", 2: "低", 3: "较低", 4: "中下", 5: "中等",
            6: "中上", 7: "较高", 8: "高", 9: "很高", 10: "最高"
        }
        self.quality_label.setText(f"{labels.get(value, '未知')} ({value})")
    
    def update_compression_label(self, value):
        """更新压缩标签"""
        labels = {
            1: "最快", 2: "快速", 3: "快速", 4: "平衡", 5: "平衡",
            6: "标准", 7: "高压缩", 8: "高压缩", 9: "最高压缩"
        }
        self.compression_label.setText(f"{labels.get(value, '未知')} ({value})")
    
    def update_preview(self):
        """更新预览"""
        try:
            options = self.get_save_options()
            
            preview_text = f"项目名称: {options.get('project_name', 'N/A')}\n"
            preview_text += f"保存位置: {options.get('save_location', 'N/A')}\n"
            preview_text += f"文件格式: {options.get('file_format', 'N/A')}\n"
            preview_text += f"包含元素: {'是' if options.get('include_elements', False) else '否'}\n"
            preview_text += f"包含时间轴: {'是' if options.get('include_timeline', False) else '否'}\n"
            preview_text += f"包含资源: {'是' if options.get('include_assets', False) else '否'}\n"
            preview_text += f"创建备份: {'是' if options.get('create_backup', False) else '否'}\n"
            preview_text += f"压缩文件: {'是' if options.get('compress', False) else '否'}\n"
            
            self.preview_text.setPlainText(preview_text)
            
        except Exception as e:
            logger.error(f"更新预览失败: {e}")
    
    def load_default_options(self):
        """加载默认选项"""
        # 从配置文件加载默认选项
        pass
    
    def get_save_options(self) -> Dict[str, Any]:
        """获取保存选项"""
        options = {
            # 基本信息
            "project_name": self.project_name_edit.text(),
            "save_location": self.location_edit.text(),
            "file_format": self.format_combo.currentText(),
            "description": self.description_edit.toPlainText(),
            "author": self.author_edit.text(),
            "version": self.version_edit.text(),
            
            # 保存选项
            "create_backup": self.create_backup_cb.isChecked(),
            "incremental_save": self.incremental_save_cb.isChecked(),
            "compress": self.compress_cb.isChecked(),
            
            # 内容选项
            "include_elements": self.include_elements_cb.isChecked(),
            "include_timeline": self.include_timeline_cb.isChecked(),
            "include_assets": self.include_assets_cb.isChecked(),
            "include_settings": self.include_settings_cb.isChecked(),
            "include_history": self.include_history_cb.isChecked(),
            "include_metadata": self.include_metadata_cb.isChecked(),
            
            # 资源处理
            "embed_assets": self.embed_assets_cb.isChecked(),
            "optimize_assets": self.optimize_assets_cb.isChecked(),
            "asset_quality": self.asset_quality_slider.value(),
            
            # 高级选项
            "target_version": self.target_version_combo.currentText(),
            "backward_compat": self.backward_compat_cb.isChecked(),
            "encrypt": self.encrypt_cb.isChecked(),
            "password": self.password_edit.text(),
            "compression_level": self.compression_slider.value(),
            "multithread": self.multithread_cb.isChecked(),
        }
        
        return options
