"""
AI Animation Studio - AI元素智能生成器
严格按照设计文档的AI智能素材生成功能实现
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QFrame, QScrollArea, QWidget,
                             QLineEdit, QTextEdit, QComboBox, QSpinBox, QSlider,
                             QProgressBar, QTabWidget, QCheckBox, QButtonGroup,
                             QMessageBox, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt6.QtGui import QPixmap, QFont, QMovie

from .color_scheme_manager import color_scheme_manager, ColorRole
from core.logger import get_logger

logger = get_logger("ai_element_generator")


class AIElementGenerator(QDialog):
    """AI元素智能生成器 - 基于设计文档的AI智能素材生成"""
    
    element_generated = pyqtSignal(dict)  # 元素生成完成信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🤖 AI元素智能生成器")
        self.setFixedSize(900, 700)
        self.setModal(True)
        
        # 生成状态
        self.is_generating = False
        self.current_solutions = []
        
        self.setup_ui()
        self.apply_color_scheme()
        
        logger.info("AI元素智能生成器初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 生成器标题
        self.create_generator_header(layout)
        
        # 主要内容区域
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：描述输入和设置
        self.create_input_panel(main_splitter)
        
        # 右侧：生成预览和结果
        self.create_preview_panel(main_splitter)
        
        main_splitter.setSizes([400, 500])
        layout.addWidget(main_splitter)
        
        # 底部：操作按钮
        self.create_action_buttons(layout)
    
    def create_generator_header(self, layout):
        """创建生成器标题"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color_scheme_manager.get_ai_function_colors()[0]},
                    stop:1 {color_scheme_manager.get_ai_function_colors()[1]});
                border: none;
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # 标题信息
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("🤖 AI元素智能生成器")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title)
        
        subtitle = QLabel("描述您想要的元素，AI将为您生成多种专业方案")
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
    
    def create_input_panel(self, splitter):
        """创建输入面板"""
        input_panel = QFrame()
        input_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border-right: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
        """)
        
        input_layout = QVBoxLayout(input_panel)
        input_layout.setContentsMargins(16, 16, 16, 16)
        input_layout.setSpacing(12)
        
        # 元素描述输入
        self.create_description_input(input_layout)
        
        # 生成设置
        self.create_generation_settings(input_layout)
        
        # 高级设置
        self.create_advanced_settings(input_layout)
        
        input_layout.addStretch()
        splitter.addWidget(input_panel)
    
    def create_description_input(self, layout):
        """创建描述输入区域"""
        desc_group = QFrame()
        desc_group.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 6px;
            }}
        """)
        
        desc_layout = QVBoxLayout(desc_group)
        desc_layout.setContentsMargins(12, 12, 12, 12)
        desc_layout.setSpacing(8)
        
        # 标题
        desc_title = QLabel("📝 元素描述")
        desc_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        desc_layout.addWidget(desc_title)
        
        # 描述输入框
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "详细描述您想要的元素...\n\n例如：\n"
            "• 一个显示销售数据的柱状图，蓝色渐变，带动画效果\n"
            "• 科技感的原子结构图，电子轨道会旋转\n"
            "• 流程图连接线，带箭头，从左到右的动画"
        )
        self.description_input.setMaximumHeight(120)
        self.description_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }}
        """)
        desc_layout.addWidget(self.description_input)
        
        # 快速标签
        tags_label = QLabel("🏷️ 快速标签:")
        tags_label.setStyleSheet("font-size: 10px; color: #6B7280;")
        desc_layout.addWidget(tags_label)
        
        tags_frame = QFrame()
        tags_layout = QHBoxLayout(tags_frame)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(4)
        
        quick_tags = ["📊 图表", "🔬 科学", "🎨 艺术", "💼 商务", "🎯 重点"]
        for tag in quick_tags:
            tag_btn = QPushButton(tag)
            tag_btn.setMaximumHeight(24)
            tag_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_scheme_manager.get_ai_function_colors()[2]};
                    border: 1px solid {color_scheme_manager.get_ai_function_colors()[0]};
                    border-radius: 12px;
                    padding: 2px 8px;
                    font-size: 9px;
                }}
                QPushButton:hover {{
                    background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                    color: white;
                }}
            """)
            tag_btn.clicked.connect(lambda checked, t=tag: self.add_tag_to_description(t))
            tags_layout.addWidget(tag_btn)
        
        tags_layout.addStretch()
        desc_layout.addWidget(tags_frame)
        
        layout.addWidget(desc_group)
    
    def create_generation_settings(self, layout):
        """创建生成设置"""
        settings_group = QFrame()
        settings_group.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 6px;
            }}
        """)
        
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setContentsMargins(12, 12, 12, 12)
        settings_layout.setSpacing(8)
        
        # 标题
        settings_title = QLabel("⚙️ 生成设置")
        settings_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        settings_layout.addWidget(settings_title)
        
        # 元素类型选择
        type_label = QLabel("🎯 元素类型:")
        settings_layout.addWidget(type_label)
        
        self.element_type = QComboBox()
        self.element_type.addItems([
            "📊 数据可视化图表",
            "✨ 动态文字效果", 
            "🔷 几何图形",
            "🧪 科普专用元素",
            "🔗 连接线和流程",
            "🎨 装饰性元素"
        ])
        settings_layout.addWidget(self.element_type)
        
        # 方案数量
        count_label = QLabel("📈 生成方案数量:")
        settings_layout.addWidget(count_label)
        
        self.solution_count = QSpinBox()
        self.solution_count.setRange(1, 6)
        self.solution_count.setValue(3)
        settings_layout.addWidget(self.solution_count)
        
        # 创意程度
        creativity_label = QLabel("🎨 创意程度:")
        settings_layout.addWidget(creativity_label)

        self.creativity_slider = QSlider(Qt.Orientation.Horizontal)
        self.creativity_slider.setRange(1, 10)
        self.creativity_slider.setValue(7)
        self.creativity_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                height: 6px;
                background: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {color_scheme_manager.get_ai_function_colors()[0]};
                border: 1px solid {color_scheme_manager.get_ai_function_colors()[0]};
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }}
            QSlider::sub-page:horizontal {{
                background: {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 3px;
            }}
        """)
        settings_layout.addWidget(self.creativity_slider)

        creativity_hint = QLabel("保守 ←→ 创新")
        creativity_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        creativity_hint.setStyleSheet("font-size: 9px; color: #6B7280;")
        settings_layout.addWidget(creativity_hint)

        layout.addWidget(settings_group)

    def create_advanced_settings(self, layout):
        """创建高级设置"""
        advanced_group = QFrame()
        advanced_group.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 6px;
            }}
        """)

        advanced_layout = QVBoxLayout(advanced_group)
        advanced_layout.setContentsMargins(12, 12, 12, 12)
        advanced_layout.setSpacing(8)

        # 标题
        advanced_title = QLabel("🔧 高级设置")
        advanced_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        advanced_layout.addWidget(advanced_title)

        # 动画效果
        self.enable_animation = QCheckBox("启用动画效果")
        self.enable_animation.setChecked(True)
        advanced_layout.addWidget(self.enable_animation)

        # 响应式设计
        self.responsive_design = QCheckBox("响应式设计")
        self.responsive_design.setChecked(True)
        advanced_layout.addWidget(self.responsive_design)

        # 可交互性
        self.interactive = QCheckBox("支持交互")
        advanced_layout.addWidget(self.interactive)

        layout.addWidget(advanced_group)

    def create_preview_panel(self, splitter):
        """创建预览面板"""
        preview_panel = QFrame()
        preview_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
            }}
        """)

        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(16, 16, 16, 16)
        preview_layout.setSpacing(12)

        # 预览标题
        preview_title = QLabel("🔍 生成预览")
        preview_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }}
        """)
        preview_layout.addWidget(preview_title)

        # 生成按钮
        self.generate_btn = QPushButton("🚀 开始生成")
        self.generate_btn.setFixedHeight(40)
        self.generate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_ai_function_colors()[1]};
            }}
        """)
        self.generate_btn.clicked.connect(self.start_generation)
        preview_layout.addWidget(self.generate_btn)

        # 生成进度
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {color_scheme_manager.get_ai_function_colors()[2]};
                border-radius: 4px;
                text-align: center;
                font-size: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 3px;
            }}
        """)
        preview_layout.addWidget(self.progress_bar)

        # 多方案生成结果
        self.results_area = QScrollArea()
        self.results_area.setWidgetResizable(True)
        self.results_area.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 6px;
                background-color: white;
            }}
        """)

        # 结果容器
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(8, 8, 8, 8)
        self.results_layout.setSpacing(8)

        # 默认提示
        default_hint = QLabel("👆 点击生成按钮开始创建AI元素")
        default_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        default_hint.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 12px;
                padding: 40px;
            }}
        """)
        self.results_layout.addWidget(default_hint)

        self.results_area.setWidget(self.results_widget)
        preview_layout.addWidget(self.results_area)

        splitter.addWidget(preview_panel)

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

        # 应用元素按钮
        self.apply_btn = QPushButton("应用元素")
        self.apply_btn.setFixedSize(100, 36)
        self.apply_btn.setEnabled(False)
        self.apply_btn.setStyleSheet(f"""
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
        self.apply_btn.clicked.connect(self.apply_element)
        button_layout.addWidget(self.apply_btn)

        layout.addWidget(button_frame)

    def add_tag_to_description(self, tag):
        """添加标签到描述"""
        current_text = self.description_input.toPlainText()
        if current_text:
            self.description_input.setPlainText(current_text + f" {tag}")
        else:
            self.description_input.setPlainText(tag)

    def start_generation(self):
        """开始生成"""
        description = self.description_input.toPlainText().strip()
        if not description:
            QMessageBox.warning(self, "警告", "请先输入元素描述！")
            return

        self.is_generating = True
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("🔄 生成中...")
        self.progress_bar.setVisible(True)

        # 清空之前的结果
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().setParent(None)

        # 模拟AI生成过程
        self.simulate_generation()

        logger.info(f"开始AI元素生成: {description}")

    def simulate_generation(self):
        """模拟生成过程"""
        # 使用定时器模拟生成进度
        self.generation_timer = QTimer()
        self.generation_timer.timeout.connect(self.update_generation_progress)
        self.generation_progress = 0
        self.generation_timer.start(100)  # 每100ms更新一次

    def update_generation_progress(self):
        """更新生成进度"""
        self.generation_progress += 2
        self.progress_bar.setValue(self.generation_progress)

        if self.generation_progress >= 100:
            self.generation_timer.stop()
            self.complete_generation()

    def complete_generation(self):
        """完成生成"""
        self.is_generating = False
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("🚀 重新生成")
        self.progress_bar.setVisible(False)
        self.apply_btn.setEnabled(True)

        # 生成示例结果
        solution_count = self.solution_count.value()
        element_type = self.element_type.currentText()

        for i in range(solution_count):
            solution_card = self.create_solution_card(f"方案 {i+1}", element_type, i)
            self.results_layout.addWidget(solution_card)

        self.results_layout.addStretch()

        logger.info(f"AI元素生成完成，生成了 {solution_count} 个方案")

    def create_solution_card(self, name, element_type, index):
        """创建方案卡片"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 6px;
                margin: 2px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(6)

        # 方案标题
        title = QLabel(f"✨ {name}")
        title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-weight: bold;
                font-size: 11px;
            }}
        """)
        card_layout.addWidget(title)

        # 预览区域
        preview = QLabel("🎨 AI生成预览")
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview.setFixedHeight(80)
        preview.setStyleSheet(f"""
            QLabel {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px dashed {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 4px;
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-size: 10px;
            }}
        """)
        card_layout.addWidget(preview)

        # 方案描述
        desc = QLabel(f"基于 {element_type} 的智能生成方案")
        desc.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 9px;
            }}
        """)
        card_layout.addWidget(desc)

        # 选择按钮
        select_btn = QPushButton("选择此方案")
        select_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 9px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_ai_function_colors()[1]};
            }}
        """)
        select_btn.clicked.connect(lambda: self.select_solution(index))
        card_layout.addWidget(select_btn)

        return card

    def select_solution(self, index):
        """选择方案"""
        self.selected_solution = index
        logger.info(f"选择方案: {index}")

    def apply_element(self):
        """应用元素"""
        if not hasattr(self, 'selected_solution'):
            QMessageBox.warning(self, "警告", "请先选择一个方案！")
            return

        # 构建元素配置
        config = {
            "type": "ai_generated",
            "element_type": self.element_type.currentText(),
            "description": self.description_input.toPlainText(),
            "solution_index": self.selected_solution,
            "settings": {
                "creativity": self.creativity_slider.value(),
                "animation": self.enable_animation.isChecked(),
                "responsive": self.responsive_design.isChecked(),
                "interactive": self.interactive.isChecked()
            }
        }

        # 发射信号
        self.element_generated.emit(config)

        # 显示成功消息
        QMessageBox.information(self, "成功", "AI元素已成功生成并应用！")

        logger.info(f"应用AI生成元素: {config}")
        self.accept()

    def apply_color_scheme(self):
        """应用色彩方案"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
            }}
        """)
