"""
AI Animation Studio - 增强的多格式导出对话框
严格按照设计文档的智能导出系统实现
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QFrame, QScrollArea, QWidget,
                             QLineEdit, QTextEdit, QComboBox, QSpinBox, QSlider,
                             QCheckBox, QProgressBar, QTabWidget, QFileDialog,
                             QMessageBox, QButtonGroup, QRadioButton)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QPixmap, QFont

from .color_scheme_manager import color_scheme_manager, ColorRole
from core.logger import get_logger

logger = get_logger("enhanced_export_dialog")


class EnhancedExportDialog(QDialog):
    """增强的多格式导出对话框 - 基于设计文档的智能导出系统"""
    
    export_completed = pyqtSignal(dict)  # 导出完成信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📤 智能导出系统")
        self.setFixedSize(800, 600)
        self.setModal(True)
        
        # 导出配置
        self.export_config = {}
        self.selected_formats = []
        
        self.setup_ui()
        self.apply_color_scheme()
        
        logger.info("增强导出对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 对话框标题
        self.create_dialog_header(layout)
        
        # 主要内容区域
        content_tabs = QTabWidget()
        content_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                background-color: white;
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11px;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-weight: bold;
            }}
        """)
        
        # 格式选择标签页
        format_tab = self.create_format_selection_tab()
        content_tabs.addTab(format_tab, "📋 格式选择")
        
        # 高级设置标签页
        settings_tab = self.create_advanced_settings_tab()
        content_tabs.addTab(settings_tab, "⚙️ 高级设置")
        
        # 导出预览标签页
        preview_tab = self.create_export_preview_tab()
        content_tabs.addTab(preview_tab, "🔍 导出预览")
        
        layout.addWidget(content_tabs)
        
        # 底部：操作按钮
        self.create_action_buttons(layout)
    
    def create_dialog_header(self, layout):
        """创建对话框标题"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color_scheme_manager.get_performance_colors()[0]},
                    stop:1 {color_scheme_manager.get_performance_colors()[1]});
                border: none;
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # 标题信息
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("📤 智能导出系统")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title)
        
        subtitle = QLabel("支持多格式导出，智能优化设置，预览分析结果")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 11px;
            }
        """)
        title_layout.addWidget(subtitle)
        
        header_layout.addWidget(title_frame)
        header_layout.addStretch()
        
        layout.addWidget(header)
    
    def create_format_selection_tab(self):
        """创建格式选择标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 格式选择标题
        format_title = QLabel("📋 选择导出格式")
        format_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }}
        """)
        layout.addWidget(format_title)
        
        # 格式选择网格
        formats_grid = QFrame()
        grid_layout = QGridLayout(formats_grid)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(8)
        
        # 支持的导出格式
        export_formats = [
            ("🌐 HTML", "交互式网页动画", "适合网页展示", True),
            ("🎬 MP4", "标准视频格式", "通用视频播放", False),
            ("📹 WebM", "Web优化视频", "网页视频播放", False),
            ("🖼️ PNG序列", "图片序列", "逐帧图片导出", False),
            ("✨ Lottie", "矢量动画", "移动端优化", False),
            ("📊 GIF", "动态图片", "简单动画展示", False)
        ]
        
        self.format_checkboxes = {}
        
        for i, (name, desc, usage, default) in enumerate(export_formats):
            row, col = i // 2, i % 2
            
            format_card = QFrame()
            format_card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 2px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                    border-radius: 6px;
                    padding: 8px;
                }}
                QFrame:hover {{
                    border-color: {color_scheme_manager.get_performance_colors()[0]};
                }}
            """)
            
            card_layout = QVBoxLayout(format_card)
            card_layout.setContentsMargins(8, 8, 8, 8)
            card_layout.setSpacing(4)
            
            # 格式选择框
            format_checkbox = QCheckBox(name)
            format_checkbox.setChecked(default)
            format_checkbox.setStyleSheet(f"""
                QCheckBox {{
                    font-weight: bold;
                    font-size: 12px;
                    color: {color_scheme_manager.get_performance_colors()[0]};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {color_scheme_manager.get_performance_colors()[0]};
                    border: 2px solid {color_scheme_manager.get_performance_colors()[0]};
                }}
            """)
            card_layout.addWidget(format_checkbox)
            
            # 格式描述
            desc_label = QLabel(desc)
            desc_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                    font-size: 10px;
                    font-weight: bold;
                }}
            """)
            card_layout.addWidget(desc_label)
            
            # 使用场景
            usage_label = QLabel(usage)
            usage_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                    font-size: 9px;
                }}
            """)
            card_layout.addWidget(usage_label)
            
            self.format_checkboxes[name] = format_checkbox
            grid_layout.addWidget(format_card, row, col)
        
        layout.addWidget(formats_grid)
        
        # 输出目录选择
        output_frame = QFrame()
        output_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
            }}
        """)
        
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(12, 12, 12, 12)
        
        output_title = QLabel("📁 输出目录")
        output_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-weight: bold;
                font-size: 12px;
            }}
        """)
        output_layout.addWidget(output_title)
        
        output_path_frame = QFrame()
        output_path_layout = QHBoxLayout(output_path_frame)
        output_path_layout.setContentsMargins(0, 0, 0, 0)
        
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("选择导出目录...")
        self.output_path.setText("./exports")
        output_path_layout.addWidget(self.output_path)
        
        browse_btn = QPushButton("浏览")
        browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_performance_colors()[0]};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_performance_colors()[1]};
            }}
        """)
        browse_btn.clicked.connect(self.browse_output_directory)
        output_path_layout.addWidget(browse_btn)
        
        output_layout.addWidget(output_path_frame)
        layout.addWidget(output_frame)
        
        layout.addStretch()
        return widget

    def create_advanced_settings_tab(self):
        """创建高级设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 质量设置
        quality_frame = QFrame()
        quality_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                border-radius: 6px;
            }}
        """)

        quality_layout = QVBoxLayout(quality_frame)
        quality_layout.setContentsMargins(12, 12, 12, 12)

        quality_title = QLabel("🎯 质量设置")
        quality_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-weight: bold;
                font-size: 12px;
            }}
        """)
        quality_layout.addWidget(quality_title)

        # 分辨率设置
        resolution_label = QLabel("📐 分辨率:")
        quality_layout.addWidget(resolution_label)

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "1920x1080 (Full HD)",
            "1280x720 (HD)",
            "3840x2160 (4K)",
            "自定义"
        ])
        quality_layout.addWidget(self.resolution_combo)

        # 帧率设置
        fps_label = QLabel("🎬 帧率:")
        quality_layout.addWidget(fps_label)

        self.fps_slider = QSlider(Qt.Orientation.Horizontal)
        self.fps_slider.setRange(15, 60)
        self.fps_slider.setValue(30)
        self.fps_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                height: 6px;
                background: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {color_scheme_manager.get_performance_colors()[0]};
                border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }}
            QSlider::sub-page:horizontal {{
                background: {color_scheme_manager.get_performance_colors()[0]};
                border-radius: 3px;
            }}
        """)
        quality_layout.addWidget(self.fps_slider)

        fps_hint = QLabel("15 FPS ←→ 60 FPS")
        fps_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fps_hint.setStyleSheet("font-size: 9px; color: #6B7280;")
        quality_layout.addWidget(fps_hint)

        layout.addWidget(quality_frame)

        # 优化选项
        optimization_frame = QFrame()
        optimization_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[0]};
                border-radius: 6px;
            }}
        """)

        opt_layout = QVBoxLayout(optimization_frame)
        opt_layout.setContentsMargins(12, 12, 12, 12)

        opt_title = QLabel("⚡ 优化选项")
        opt_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_collaboration_colors()[0]};
                font-weight: bold;
                font-size: 12px;
            }}
        """)
        opt_layout.addWidget(opt_title)

        # 优化选项复选框
        self.optimize_size = QCheckBox("文件大小优化")
        self.optimize_size.setChecked(True)
        opt_layout.addWidget(self.optimize_size)

        self.optimize_quality = QCheckBox("质量优化")
        self.optimize_quality.setChecked(True)
        opt_layout.addWidget(self.optimize_quality)

        self.enable_compression = QCheckBox("启用压缩")
        self.enable_compression.setChecked(True)
        opt_layout.addWidget(self.enable_compression)

        layout.addWidget(optimization_frame)

        layout.addStretch()
        return widget

    def create_export_preview_tab(self):
        """创建导出预览标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)

        # 预览标题
        preview_title = QLabel("🔍 导出预览与分析")
        preview_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }}
        """)
        layout.addWidget(preview_title)

        # 预览区域
        preview_area = QFrame()
        preview_area.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 2px dashed {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 8px;
            }}
        """)

        preview_layout = QVBoxLayout(preview_area)
        preview_layout.setContentsMargins(20, 20, 20, 20)

        preview_placeholder = QLabel("📊 导出预览\n\n点击'生成预览'查看导出效果\n支持实时预览和文件大小估算")
        preview_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_placeholder.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 12px;
                padding: 40px;
            }}
        """)
        preview_layout.addWidget(preview_placeholder)

        layout.addWidget(preview_area)

        # 预览控制
        preview_controls = QFrame()
        preview_controls_layout = QHBoxLayout(preview_controls)
        preview_controls_layout.setContentsMargins(0, 0, 0, 0)

        generate_preview_btn = QPushButton("🔄 生成预览")
        generate_preview_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_performance_colors()[0]};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_performance_colors()[1]};
            }}
        """)
        preview_controls_layout.addWidget(generate_preview_btn)

        preview_controls_layout.addStretch()

        layout.addWidget(preview_controls)
        return widget

    def create_action_buttons(self, layout):
        """创建操作按钮"""
        button_frame = QFrame()
        button_frame.setFixedHeight(60)
        button_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border-top: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
        """)

        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(20, 12, 20, 12)

        button_layout.addStretch()

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(80, 36)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # 开始导出按钮
        self.export_btn = QPushButton("🚀 开始导出")
        self.export_btn.setFixedSize(120, 36)
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_performance_colors()[0]};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_performance_colors()[1]};
            }}
        """)
        self.export_btn.clicked.connect(self.start_export)
        button_layout.addWidget(self.export_btn)

        layout.addWidget(button_frame)

    def browse_output_directory(self):
        """浏览输出目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if directory:
            self.output_path.setText(directory)

    def start_export(self):
        """开始导出"""
        # 收集选中的格式
        selected_formats = []
        for name, checkbox in self.format_checkboxes.items():
            if checkbox.isChecked():
                selected_formats.append(name)

        if not selected_formats:
            QMessageBox.warning(self, "警告", "请至少选择一种导出格式！")
            return

        # 构建导出配置
        export_config = {
            "formats": selected_formats,
            "output_path": self.output_path.text(),
            "resolution": self.resolution_combo.currentText(),
            "fps": self.fps_slider.value(),
            "optimize_size": self.optimize_size.isChecked(),
            "optimize_quality": self.optimize_quality.isChecked(),
            "enable_compression": self.enable_compression.isChecked()
        }

        # 发射信号
        self.export_completed.emit(export_config)

        # 显示成功消息
        QMessageBox.information(self, "导出开始",
            f"导出任务已开始！\n\n"
            f"格式: {', '.join(selected_formats)}\n"
            f"输出目录: {export_config['output_path']}")

        logger.info(f"开始导出: {export_config}")
        self.accept()

    def apply_color_scheme(self):
        """应用色彩方案"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
            }}
        """)
