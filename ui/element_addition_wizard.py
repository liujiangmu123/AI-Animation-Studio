"""
AI Animation Studio - 智能元素添加向导
严格按照设计文档的素材管理系统实现
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QPushButton, QFrame, QScrollArea, QWidget,
                             QLineEdit, QTextEdit, QComboBox, QSpinBox, QCheckBox,
                             QButtonGroup, QTabWidget, QProgressBar, QListWidget,
                             QListWidgetItem, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QFont

from .color_scheme_manager import color_scheme_manager, ColorRole
from core.logger import get_logger

logger = get_logger("element_addition_wizard")


class ElementAdditionWizard(QDialog):
    """智能元素添加向导 - 基于设计文档的素材管理系统"""
    
    element_added = pyqtSignal(dict)  # 元素添加完成信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧙‍♂️ 智能元素添加向导")
        self.setFixedSize(800, 600)
        self.setModal(True)
        
        # 当前选择的元素类型和配置
        self.current_element_type = None
        self.element_config = {}
        
        self.setup_ui()
        self.apply_color_scheme()
        
        logger.info("智能元素添加向导初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 向导标题
        self.create_wizard_header(layout)
        
        # 主要内容区域
        content_area = QFrame()
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 左侧：元素类型选择
        self.create_element_type_panel(content_layout)
        
        # 右侧：元素配置面板
        self.create_element_config_panel(content_layout)
        
        layout.addWidget(content_area)
        
        # 底部：操作按钮
        self.create_action_buttons(layout)
    
    def create_wizard_header(self, layout):
        """创建向导标题"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color_scheme_manager.get_ai_function_colors()[0]},
                    stop:1 {color_scheme_manager.get_ai_function_colors()[1]});
                border: none;
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题和描述
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("🧙‍♂️ 智能元素添加向导")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title)
        
        subtitle = QLabel("选择元素类型，AI将帮助您快速创建专业动画元素")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 12px;
            }
        """)
        title_layout.addWidget(subtitle)
        
        header_layout.addWidget(title_frame)
        header_layout.addStretch()
        
        layout.addWidget(header)
    
    def create_element_type_panel(self, layout):
        """创建元素类型选择面板"""
        type_panel = QFrame()
        type_panel.setFixedWidth(280)
        type_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border-right: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
        """)
        
        type_layout = QVBoxLayout(type_panel)
        type_layout.setContentsMargins(12, 12, 12, 12)
        type_layout.setSpacing(8)
        
        # 类型选择标题
        type_title = QLabel("📦 选择元素类型")
        type_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border-radius: 4px;
            }}
        """)
        type_layout.addWidget(type_title)
        
        # 严格按照设计文档的元素类型（第一行）
        first_row_group = self.create_element_group(
            "🎯 基础元素类型 (AI智能推荐)",
            [
                ("📝", "文本", "🔥推荐 - 创建文本标题说明", True),
                ("🖼️", "图片", "导入图片背景装饰", False),
                ("🔷", "形状", "🔥推荐 - 绘制形状几何元素", True),
                ("📐", "SVG", "🔥推荐 - 矢量图形图标符号", True)
            ]
        )
        type_layout.addWidget(first_row_group)

        # 严格按照设计文档的第二行元素类型
        second_row_group = self.create_element_group(
            "🎬 高级元素类型",
            [
                ("🎬", "视频", "视频素材动态内容", False),
                ("🎵", "音频", "音效配乐背景音乐", False),
                ("📊", "图表", "🔥推荐 - 数据可视化统计图表", True),
                ("🤖", "AI生成", "💡智能 - 智能创建AI辅助", True)
            ]
        )
        type_layout.addWidget(second_row_group)

        # AI智能推荐面板（严格按照设计文档）
        ai_recommendations = self.create_ai_recommendations_panel()
        type_layout.addWidget(ai_recommendations)
        
        type_layout.addStretch()
        layout.addWidget(type_panel)

    def create_ai_recommendations_panel(self):
        """创建AI智能推荐面板 - 严格按照设计文档"""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_ai_function_colors()[2]};
                border: 2px solid {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 6px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # 推荐标题
        title = QLabel("🤖 基于当前项目的AI推荐")
        title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-weight: bold;
                font-size: 11px;
            }}
        """)
        layout.addWidget(title)

        # 智能建议内容
        suggestions_frame = QFrame()
        suggestions_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 4px;
            }}
        """)

        suggestions_layout = QVBoxLayout(suggestions_frame)
        suggestions_layout.setContentsMargins(8, 6, 8, 6)
        suggestions_layout.setSpacing(4)

        # 建议标题
        suggestions_title = QLabel("💡 智能建议 (基于\"科普动画\"项目类型):")
        suggestions_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-weight: bold;
                font-size: 10px;
            }}
        """)
        suggestions_layout.addWidget(suggestions_title)

        # 推荐项目列表（严格按照设计文档）
        recommendations = [
            ("• 原子结构图标 (SVG)", "与主题高度匹配", "95%"),
            ("• 科学公式文本", "增强教育效果", "92%"),
            ("• 数据图表", "展示科学数据", "88%"),
            ("• 箭头指示器", "突出关键信息", "85%")
        ]

        for item, desc, match in recommendations:
            rec_item = QFrame()
            rec_layout = QHBoxLayout(rec_item)
            rec_layout.setContentsMargins(0, 2, 0, 2)

            item_label = QLabel(item)
            item_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                    font-size: 9px;
                    min-width: 120px;
                }}
            """)
            rec_layout.addWidget(item_label)

            desc_label = QLabel(f"- {desc}")
            desc_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                    font-size: 9px;
                }}
            """)
            rec_layout.addWidget(desc_label)

            rec_layout.addStretch()

            match_label = QLabel(match)
            match_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_ai_function_colors()[0]};
                    font-weight: bold;
                    font-size: 9px;
                }}
            """)
            rec_layout.addWidget(match_label)

            suggestions_layout.addWidget(rec_item)

        layout.addWidget(suggestions_frame)

        # 操作按钮（严格按照设计文档）
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(4)

        batch_add_btn = QPushButton("⚡ 批量添加推荐")
        batch_add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_ai_function_colors()[1]};
            }}
        """)
        actions_layout.addWidget(batch_add_btn)

        custom_style_btn = QPushButton("🎨 自定义样式")
        custom_style_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_collaboration_colors()[0]};
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        actions_layout.addWidget(custom_style_btn)

        view_more_btn = QPushButton("📋 查看更多")
        view_more_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_performance_colors()[0]};
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        actions_layout.addWidget(view_more_btn)

        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        return panel

    def create_element_group(self, title, elements):
        """创建元素组 - 支持推荐标记"""
        group = QFrame()
        group.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 6px;
            }}
        """)

        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 8, 8, 8)
        group_layout.setSpacing(4)

        # 组标题
        group_title = QLabel(title)
        group_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-size: 12px;
                font-weight: bold;
                padding: 4px;
            }}
        """)
        group_layout.addWidget(group_title)

        # 创建网格布局（2x2）
        grid_frame = QFrame()
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(4)

        # 元素按钮（支持推荐标记）
        for i, element_data in enumerate(elements):
            if len(element_data) == 4:  # 包含推荐标记
                icon, name, desc, is_recommended = element_data
            else:  # 兼容旧格式
                icon, name, desc = element_data
                is_recommended = False

            btn = self.create_element_button(icon, name, desc, is_recommended)
            row, col = i // 2, i % 2
            grid_layout.addWidget(btn, row, col)

        group_layout.addWidget(grid_frame)
        return group

    def create_element_button(self, icon, name, description, is_recommended=False):
        """创建元素选择按钮 - 支持推荐标记"""
        btn = QPushButton()
        btn.setFixedHeight(60)  # 增加高度以容纳推荐标记
        btn.setCheckable(True)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(8, 8, 8, 8)

        # 图标
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 16px;")
        btn_layout.addWidget(icon_label)

        # 文本信息
        text_frame = QFrame()
        text_layout = QVBoxLayout(text_frame)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        text_layout.addWidget(name_label)

        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #6B7280; font-size: 9px;")
        text_layout.addWidget(desc_label)

        btn_layout.addWidget(text_frame)
        btn_layout.addStretch()

        # 设置布局到按钮（这里需要用widget包装）
        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)

        # 按钮样式（支持推荐标记）
        if is_recommended:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_ai_function_colors()[2]};
                    border: 2px solid {color_scheme_manager.get_ai_function_colors()[0]};
                    border-radius: 4px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    border-color: {color_scheme_manager.get_ai_function_colors()[1]};
                    background-color: {color_scheme_manager.get_ai_function_colors()[1]};
                }}
                QPushButton:checked {{
                    border-color: {color_scheme_manager.get_ai_function_colors()[0]};
                    background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                    color: white;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                    border-radius: 4px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    border-color: {color_scheme_manager.get_ai_function_colors()[0]};
                    background-color: {color_scheme_manager.get_ai_function_colors()[2]};
                }}
                QPushButton:checked {{
                    border-color: {color_scheme_manager.get_ai_function_colors()[0]};
                    background-color: {color_scheme_manager.get_ai_function_colors()[1]};
                    color: white;
                }}
            """)

        # 连接点击事件
        btn.clicked.connect(lambda: self.on_element_type_selected(name))

        return btn

    def create_element_config_panel(self, layout):
        """创建元素配置面板"""
        config_panel = QFrame()
        config_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
            }}
        """)

        config_layout = QVBoxLayout(config_panel)
        config_layout.setContentsMargins(20, 20, 20, 20)
        config_layout.setSpacing(12)

        # 配置标题
        config_title = QLabel("⚙️ 元素配置")
        config_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }}
        """)
        config_layout.addWidget(config_title)

        # 配置内容区域（动态更新）
        self.config_content = QFrame()
        self.config_content.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 6px;
            }}
        """)

        self.config_content_layout = QVBoxLayout(self.config_content)
        self.config_content_layout.setContentsMargins(16, 16, 16, 16)

        # 默认提示
        default_hint = QLabel("👈 请先选择元素类型")
        default_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        default_hint.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 14px;
                padding: 40px;
            }}
        """)
        self.config_content_layout.addWidget(default_hint)

        config_layout.addWidget(self.config_content)
        config_layout.addStretch()

        layout.addWidget(config_panel)

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

        # 添加元素按钮
        self.add_btn = QPushButton("添加元素")
        self.add_btn.setFixedSize(100, 36)
        self.add_btn.setEnabled(False)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover:enabled {{
                background-color: {color_scheme_manager.get_ai_function_colors()[1]};
            }}
            QPushButton:disabled {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
            }}
        """)
        self.add_btn.clicked.connect(self.add_element)
        button_layout.addWidget(self.add_btn)

        layout.addWidget(button_frame)

    def on_element_type_selected(self, element_type):
        """元素类型选择处理"""
        self.current_element_type = element_type
        self.update_config_panel(element_type)
        self.add_btn.setEnabled(True)

        logger.info(f"选择元素类型: {element_type}")

    def update_config_panel(self, element_type):
        """更新配置面板"""
        # 清空现有内容
        for i in reversed(range(self.config_content_layout.count())):
            self.config_content_layout.itemAt(i).widget().setParent(None)

        # 根据元素类型创建配置界面
        if element_type == "文本":
            self.create_text_config()
        elif element_type == "图片":
            self.create_image_config()
        elif element_type == "图表":
            self.create_chart_config()
        else:
            self.create_generic_config(element_type)

    def create_text_config(self):
        """创建文本配置界面"""
        # 文本内容
        text_label = QLabel("📝 文本内容:")
        self.config_content_layout.addWidget(text_label)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("输入文本内容...")
        self.text_input.setMaximumHeight(80)
        self.config_content_layout.addWidget(self.text_input)

        # 字体大小
        size_label = QLabel("📏 字体大小:")
        self.config_content_layout.addWidget(size_label)

        self.font_size = QSpinBox()
        self.font_size.setRange(12, 72)
        self.font_size.setValue(24)
        self.config_content_layout.addWidget(self.font_size)

        self.config_content_layout.addStretch()

    def create_image_config(self):
        """创建图片配置界面"""
        # 文件选择
        file_label = QLabel("🖼️ 选择图片文件:")
        self.config_content_layout.addWidget(file_label)

        file_frame = QFrame()
        file_layout = QHBoxLayout(file_frame)
        file_layout.setContentsMargins(0, 0, 0, 0)

        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("点击选择图片文件...")
        file_layout.addWidget(self.file_path)

        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_image_file)
        file_layout.addWidget(browse_btn)

        self.config_content_layout.addWidget(file_frame)
        self.config_content_layout.addStretch()

    def create_chart_config(self):
        """创建图表配置界面"""
        # 图表类型
        type_label = QLabel("📊 图表类型:")
        self.config_content_layout.addWidget(type_label)

        self.chart_type = QComboBox()
        self.chart_type.addItems(["柱状图", "折线图", "饼图", "散点图", "雷达图"])
        self.config_content_layout.addWidget(self.chart_type)

        # 数据输入
        data_label = QLabel("📈 数据输入:")
        self.config_content_layout.addWidget(data_label)

        self.chart_data = QTextEdit()
        self.chart_data.setPlaceholderText("输入图表数据，每行一个数据点...")
        self.chart_data.setMaximumHeight(100)
        self.config_content_layout.addWidget(self.chart_data)

        self.config_content_layout.addStretch()

    def create_generic_config(self, element_type):
        """创建通用配置界面"""
        info_label = QLabel(f"⚙️ {element_type} 配置")
        info_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.config_content_layout.addWidget(info_label)

        desc_label = QLabel(f"正在为 {element_type} 准备配置选项...")
        desc_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        self.config_content_layout.addWidget(desc_label)

        self.config_content_layout.addStretch()

    def browse_image_file(self):
        """浏览图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片文件", "",
            "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp *.svg)"
        )
        if file_path:
            self.file_path.setText(file_path)

    def add_element(self):
        """添加元素"""
        if not self.current_element_type:
            return

        # 收集配置信息
        config = {
            "type": self.current_element_type,
            "timestamp": "now"
        }

        # 根据元素类型收集特定配置
        if self.current_element_type == "文本" and hasattr(self, 'text_input'):
            config["text"] = self.text_input.toPlainText()
            config["font_size"] = self.font_size.value()
        elif self.current_element_type == "图片" and hasattr(self, 'file_path'):
            config["file_path"] = self.file_path.text()
        elif self.current_element_type == "图表" and hasattr(self, 'chart_type'):
            config["chart_type"] = self.chart_type.currentText()
            config["data"] = self.chart_data.toPlainText()

        # 发射信号
        self.element_added.emit(config)

        # 显示成功消息
        QMessageBox.information(self, "成功", f"已成功添加 {self.current_element_type} 元素！")

        logger.info(f"添加元素: {config}")
        self.accept()

    def apply_color_scheme(self):
        """应用色彩方案"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
            }}
        """)
