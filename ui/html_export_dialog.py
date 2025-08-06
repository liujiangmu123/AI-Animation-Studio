"""
AI Animation Studio - HTML导出选项对话框
提供HTML导出的高级选项，包括优化、SEO、压缩等功能
"""

from typing import Dict, Any, Optional
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QComboBox, QSpinBox, QLineEdit, QTextEdit,
    QTabWidget, QWidget, QSlider, QFileDialog, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from core.logger import get_logger

logger = get_logger("html_export_dialog")


class HTMLExportDialog(QDialog):
    """HTML导出选项对话框"""
    
    def __init__(self, parent=None, current_project=None):
        super().__init__(parent)
        self.current_project = current_project
        self.export_options = {}
        
        self.setWindowTitle("HTML导出选项")
        self.setMinimumSize(600, 700)
        self.resize(700, 800)
        
        self.setup_ui()
        self.load_default_options()
        
        logger.info("HTML导出选项对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("HTML导出选项")
        title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 基本选项选项卡
        self.setup_basic_options_tab()
        
        # 优化选项选项卡
        self.setup_optimization_tab()
        
        # SEO选项选项卡
        self.setup_seo_tab()
        
        # 库管理选项卡
        self.setup_libraries_tab()
        
        layout.addWidget(self.tab_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        preview_button = QPushButton("预览")
        preview_button.clicked.connect(self.preview_html)
        button_layout.addWidget(preview_button)
        
        button_layout.addStretch()
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        self.export_button = QPushButton("导出")
        self.export_button.setDefault(True)
        self.export_button.clicked.connect(self.accept)
        button_layout.addWidget(self.export_button)
        
        layout.addLayout(button_layout)
    
    def setup_basic_options_tab(self):
        """设置基本选项选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 文件选项组
        file_group = QGroupBox("文件选项")
        file_layout = QGridLayout(file_group)
        
        # 文件名
        file_layout.addWidget(QLabel("文件名:"), 0, 0)
        self.filename_edit = QLineEdit()
        if self.current_project:
            self.filename_edit.setText(f"{self.current_project.name}.html")
        else:
            self.filename_edit.setText("animation.html")
        file_layout.addWidget(self.filename_edit, 0, 1)
        
        # 输出目录
        file_layout.addWidget(QLabel("输出目录:"), 1, 0)
        output_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setText(str(Path.cwd()))
        output_layout.addWidget(self.output_dir_edit)
        
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(browse_button)
        
        file_layout.addLayout(output_layout, 1, 1)
        
        layout.addWidget(file_group)
        
        # 内容选项组
        content_group = QGroupBox("内容选项")
        content_layout = QVBoxLayout(content_group)
        
        self.include_css_checkbox = QCheckBox("内联CSS样式")
        self.include_css_checkbox.setChecked(True)
        self.include_css_checkbox.setToolTip("将CSS样式直接嵌入HTML中")
        content_layout.addWidget(self.include_css_checkbox)
        
        self.include_js_checkbox = QCheckBox("内联JavaScript")
        self.include_js_checkbox.setChecked(True)
        self.include_js_checkbox.setToolTip("将JavaScript代码直接嵌入HTML中")
        content_layout.addWidget(self.include_js_checkbox)
        
        self.responsive_design_checkbox = QCheckBox("响应式设计")
        self.responsive_design_checkbox.setChecked(True)
        self.responsive_design_checkbox.setToolTip("添加响应式设计的CSS")
        content_layout.addWidget(self.responsive_design_checkbox)
        
        self.add_controls_checkbox = QCheckBox("添加播放控制")
        self.add_controls_checkbox.setChecked(False)
        self.add_controls_checkbox.setToolTip("添加播放、暂停、重播等控制按钮")
        content_layout.addWidget(self.add_controls_checkbox)
        
        layout.addWidget(content_group)
        
        # 兼容性选项组
        compatibility_group = QGroupBox("兼容性选项")
        compatibility_layout = QGridLayout(compatibility_group)
        
        compatibility_layout.addWidget(QLabel("目标浏览器:"), 0, 0)
        self.browser_combo = QComboBox()
        self.browser_combo.addItems([
            "现代浏览器 (ES6+)",
            "兼容模式 (ES5)",
            "IE11兼容",
            "移动端优化"
        ])
        compatibility_layout.addWidget(self.browser_combo, 0, 1)
        
        compatibility_layout.addWidget(QLabel("CSS前缀:"), 1, 0)
        self.css_prefix_combo = QComboBox()
        self.css_prefix_combo.addItems([
            "自动添加",
            "仅Webkit",
            "仅Mozilla",
            "不添加"
        ])
        compatibility_layout.addWidget(self.css_prefix_combo, 1, 1)
        
        layout.addWidget(compatibility_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "基本选项")
    
    def setup_optimization_tab(self):
        """设置优化选项选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 压缩选项组
        compression_group = QGroupBox("压缩选项")
        compression_layout = QVBoxLayout(compression_group)
        
        self.minify_html_checkbox = QCheckBox("压缩HTML")
        self.minify_html_checkbox.setChecked(True)
        self.minify_html_checkbox.setToolTip("移除HTML中的空白字符和注释")
        compression_layout.addWidget(self.minify_html_checkbox)
        
        self.minify_css_checkbox = QCheckBox("压缩CSS")
        self.minify_css_checkbox.setChecked(True)
        self.minify_css_checkbox.setToolTip("压缩CSS代码，移除空白和注释")
        compression_layout.addWidget(self.minify_css_checkbox)
        
        self.minify_js_checkbox = QCheckBox("压缩JavaScript")
        self.minify_js_checkbox.setChecked(True)
        self.minify_js_checkbox.setToolTip("压缩JavaScript代码")
        compression_layout.addWidget(self.minify_js_checkbox)
        
        # 压缩级别
        compression_level_layout = QHBoxLayout()
        compression_level_layout.addWidget(QLabel("压缩级别:"))
        self.compression_slider = QSlider(Qt.Orientation.Horizontal)
        self.compression_slider.setRange(1, 5)
        self.compression_slider.setValue(3)
        self.compression_slider.valueChanged.connect(self.update_compression_label)
        compression_level_layout.addWidget(self.compression_slider)
        
        self.compression_label = QLabel("标准")
        compression_level_layout.addWidget(self.compression_label)
        compression_layout.addLayout(compression_level_layout)
        
        layout.addWidget(compression_group)
        
        # 性能优化组
        performance_group = QGroupBox("性能优化")
        performance_layout = QVBoxLayout(performance_group)
        
        self.lazy_loading_checkbox = QCheckBox("延迟加载资源")
        self.lazy_loading_checkbox.setChecked(False)
        self.lazy_loading_checkbox.setToolTip("延迟加载图片和其他资源")
        performance_layout.addWidget(self.lazy_loading_checkbox)
        
        self.preload_critical_checkbox = QCheckBox("预加载关键资源")
        self.preload_critical_checkbox.setChecked(True)
        self.preload_critical_checkbox.setToolTip("预加载关键的CSS和JavaScript")
        performance_layout.addWidget(self.preload_critical_checkbox)
        
        self.optimize_images_checkbox = QCheckBox("优化图片")
        self.optimize_images_checkbox.setChecked(True)
        self.optimize_images_checkbox.setToolTip("压缩和优化图片资源")
        performance_layout.addWidget(self.optimize_images_checkbox)
        
        layout.addWidget(performance_group)
        
        # 缓存选项组
        cache_group = QGroupBox("缓存选项")
        cache_layout = QGridLayout(cache_group)
        
        cache_layout.addWidget(QLabel("缓存策略:"), 0, 0)
        self.cache_strategy_combo = QComboBox()
        self.cache_strategy_combo.addItems([
            "无缓存",
            "短期缓存 (1小时)",
            "中期缓存 (1天)",
            "长期缓存 (1周)"
        ])
        self.cache_strategy_combo.setCurrentIndex(2)
        cache_layout.addWidget(self.cache_strategy_combo, 0, 1)
        
        layout.addWidget(cache_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "优化选项")
    
    def setup_seo_tab(self):
        """设置SEO选项选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 基本SEO组
        basic_seo_group = QGroupBox("基本SEO")
        basic_seo_layout = QGridLayout(basic_seo_group)
        
        # 页面标题
        basic_seo_layout.addWidget(QLabel("页面标题:"), 0, 0)
        self.page_title_edit = QLineEdit()
        if self.current_project:
            self.page_title_edit.setText(f"{self.current_project.name} - AI动画")
        basic_seo_layout.addWidget(self.page_title_edit, 0, 1)
        
        # 页面描述
        basic_seo_layout.addWidget(QLabel("页面描述:"), 1, 0)
        self.page_description_edit = QTextEdit()
        self.page_description_edit.setMaximumHeight(60)
        self.page_description_edit.setPlainText("由AI Animation Studio创建的精美动画")
        basic_seo_layout.addWidget(self.page_description_edit, 1, 1)
        
        # 关键词
        basic_seo_layout.addWidget(QLabel("关键词:"), 2, 0)
        self.keywords_edit = QLineEdit()
        self.keywords_edit.setText("动画, AI, 网页动画, 创意")
        basic_seo_layout.addWidget(self.keywords_edit, 2, 1)
        
        # 作者
        basic_seo_layout.addWidget(QLabel("作者:"), 3, 0)
        self.author_edit = QLineEdit()
        basic_seo_layout.addWidget(self.author_edit, 3, 1)
        
        layout.addWidget(basic_seo_group)
        
        # Open Graph组
        og_group = QGroupBox("Open Graph (社交媒体)")
        og_layout = QVBoxLayout(og_group)
        
        self.enable_og_checkbox = QCheckBox("启用Open Graph标签")
        self.enable_og_checkbox.setChecked(True)
        og_layout.addWidget(self.enable_og_checkbox)
        
        og_details_layout = QGridLayout()
        
        og_details_layout.addWidget(QLabel("OG标题:"), 0, 0)
        self.og_title_edit = QLineEdit()
        og_details_layout.addWidget(self.og_title_edit, 0, 1)
        
        og_details_layout.addWidget(QLabel("OG描述:"), 1, 0)
        self.og_description_edit = QLineEdit()
        og_details_layout.addWidget(self.og_description_edit, 1, 1)
        
        og_details_layout.addWidget(QLabel("OG图片:"), 2, 0)
        og_image_layout = QHBoxLayout()
        self.og_image_edit = QLineEdit()
        og_image_layout.addWidget(self.og_image_edit)
        
        og_image_button = QPushButton("选择...")
        og_image_button.clicked.connect(self.browse_og_image)
        og_image_layout.addWidget(og_image_button)
        
        og_details_layout.addLayout(og_image_layout, 2, 1)
        
        og_layout.addLayout(og_details_layout)
        
        layout.addWidget(og_group)
        
        # 结构化数据组
        structured_group = QGroupBox("结构化数据")
        structured_layout = QVBoxLayout(structured_group)
        
        self.enable_schema_checkbox = QCheckBox("添加Schema.org标记")
        self.enable_schema_checkbox.setChecked(False)
        structured_layout.addWidget(self.enable_schema_checkbox)
        
        schema_layout = QGridLayout()
        schema_layout.addWidget(QLabel("内容类型:"), 0, 0)
        self.schema_type_combo = QComboBox()
        self.schema_type_combo.addItems([
            "CreativeWork",
            "VideoObject",
            "WebPage",
            "Article"
        ])
        schema_layout.addWidget(self.schema_type_combo, 0, 1)
        
        structured_layout.addLayout(schema_layout)
        
        layout.addWidget(structured_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "SEO优化")
    
    def setup_libraries_tab(self):
        """设置库管理选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 库选择组
        library_group = QGroupBox("JavaScript库")
        library_layout = QVBoxLayout(library_group)
        
        # 库列表
        self.library_list = QListWidget()
        
        # 添加常用库选项
        libraries = [
            ("GSAP", "高性能动画库", True),
            ("Three.js", "3D图形库", False),
            ("Anime.js", "轻量级动画库", False),
            ("Lottie", "After Effects动画", False),
            ("Particles.js", "粒子效果", False),
            ("AOS", "滚动动画", False)
        ]
        
        for name, desc, checked in libraries:
            item = QListWidgetItem(f"{name} - {desc}")
            item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.library_list.addItem(item)
        
        library_layout.addWidget(self.library_list)
        
        layout.addWidget(library_group)
        
        # CDN选项组
        cdn_group = QGroupBox("CDN选项")
        cdn_layout = QVBoxLayout(cdn_group)
        
        self.use_cdn_checkbox = QCheckBox("使用CDN链接")
        self.use_cdn_checkbox.setChecked(True)
        self.use_cdn_checkbox.setToolTip("使用CDN链接而不是本地文件")
        cdn_layout.addWidget(self.use_cdn_checkbox)
        
        cdn_provider_layout = QHBoxLayout()
        cdn_provider_layout.addWidget(QLabel("CDN提供商:"))
        self.cdn_provider_combo = QComboBox()
        self.cdn_provider_combo.addItems([
            "jsDelivr",
            "unpkg",
            "cdnjs",
            "自定义"
        ])
        cdn_provider_layout.addWidget(self.cdn_provider_combo)
        cdn_provider_layout.addStretch()
        cdn_layout.addLayout(cdn_provider_layout)
        
        layout.addWidget(cdn_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "库管理")
    
    def browse_output_dir(self):
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir_edit.setText(dir_path)
    
    def browse_og_image(self):
        """浏览OG图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择OG图片", "", 
            "图片文件 (*.png *.jpg *.jpeg *.gif *.webp);;所有文件 (*.*)"
        )
        if file_path:
            self.og_image_edit.setText(file_path)
    
    def update_compression_label(self, value):
        """更新压缩级别标签"""
        labels = ["", "最小", "轻度", "标准", "高度", "最大"]
        self.compression_label.setText(labels[value])
    
    def preview_html(self):
        """预览HTML"""
        # 实现HTML预览功能
        pass
    
    def load_default_options(self):
        """加载默认选项"""
        # 从配置文件加载默认选项
        pass
    
    def get_export_options(self) -> Dict[str, Any]:
        """获取导出选项"""
        # 获取选中的库
        selected_libraries = []
        for i in range(self.library_list.count()):
            item = self.library_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_libraries.append(item.data(Qt.ItemDataRole.UserRole))
        
        options = {
            # 基本选项
            "filename": self.filename_edit.text(),
            "output_dir": self.output_dir_edit.text(),
            "include_css": self.include_css_checkbox.isChecked(),
            "include_js": self.include_js_checkbox.isChecked(),
            "responsive_design": self.responsive_design_checkbox.isChecked(),
            "add_controls": self.add_controls_checkbox.isChecked(),
            "target_browser": self.browser_combo.currentText(),
            "css_prefix": self.css_prefix_combo.currentText(),
            
            # 优化选项
            "minify_html": self.minify_html_checkbox.isChecked(),
            "minify_css": self.minify_css_checkbox.isChecked(),
            "minify_js": self.minify_js_checkbox.isChecked(),
            "compression_level": self.compression_slider.value(),
            "lazy_loading": self.lazy_loading_checkbox.isChecked(),
            "preload_critical": self.preload_critical_checkbox.isChecked(),
            "optimize_images": self.optimize_images_checkbox.isChecked(),
            "cache_strategy": self.cache_strategy_combo.currentText(),
            
            # SEO选项
            "page_title": self.page_title_edit.text(),
            "page_description": self.page_description_edit.toPlainText(),
            "keywords": self.keywords_edit.text(),
            "author": self.author_edit.text(),
            "enable_og": self.enable_og_checkbox.isChecked(),
            "og_title": self.og_title_edit.text(),
            "og_description": self.og_description_edit.text(),
            "og_image": self.og_image_edit.text(),
            "enable_schema": self.enable_schema_checkbox.isChecked(),
            "schema_type": self.schema_type_combo.currentText(),
            
            # 库管理选项
            "selected_libraries": selected_libraries,
            "use_cdn": self.use_cdn_checkbox.isChecked(),
            "cdn_provider": self.cdn_provider_combo.currentText(),
        }
        
        return options
