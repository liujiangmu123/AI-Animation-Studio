"""
AI Animation Studio - 新手引导系统
基于设计文档的交互式新手引导流程
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QWidget, QStackedWidget,
                             QProgressBar, QCheckBox, QTextEdit, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont, QPainter, QPen, QBrush, QColor

from .color_scheme_manager import color_scheme_manager, ColorRole
from core.logger import get_logger

logger = get_logger("onboarding_system")


class OnboardingSystem(QDialog):
    """新手引导系统 - 基于设计文档的交互式引导流程"""
    
    onboarding_completed = pyqtSignal()  # 引导完成信号
    skip_requested = pyqtSignal()  # 跳过引导信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎓 AI Animation Studio 新手引导")
        self.setFixedSize(900, 600)
        self.setModal(True)
        
        # 引导步骤
        self.current_step = 0
        self.total_steps = 6
        self.user_preferences = {}
        
        self.setup_ui()
        self.apply_color_scheme()
        
        logger.info("新手引导系统初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 引导标题
        self.create_header(layout)
        
        # 进度指示器
        self.create_progress_indicator(layout)
        
        # 引导内容区域
        self.create_content_area(layout)
        
        # 导航按钮
        self.create_navigation_buttons(layout)
    
    def create_header(self, layout):
        """创建引导标题"""
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
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        # 标题信息
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("🎓 欢迎使用 AI Animation Studio")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title)
        
        subtitle = QLabel("让我们通过简单的步骤，帮您快速上手专业动画创作")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 12px;
            }
        """)
        title_layout.addWidget(subtitle)
        
        header_layout.addWidget(title_frame)
        header_layout.addStretch()
        
        # 跳过按钮
        skip_btn = QPushButton("跳过引导")
        skip_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        skip_btn.clicked.connect(self.skip_onboarding)
        header_layout.addWidget(skip_btn)
        
        layout.addWidget(header)
    
    def create_progress_indicator(self, layout):
        """创建进度指示器"""
        progress_frame = QFrame()
        progress_frame.setFixedHeight(60)
        progress_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border-bottom: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
        """)
        
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(30, 15, 30, 15)
        
        # 步骤标题
        self.step_title = QLabel("步骤 1/6: 欢迎")
        self.step_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        progress_layout.addWidget(self.step_title)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.total_steps)
        self.progress_bar.setValue(1)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {color_scheme_manager.get_ai_function_colors()[2]};
                border-radius: 4px;
                text-align: center;
                font-size: 10px;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 3px;
            }}
        """)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_frame)
    
    def create_content_area(self, layout):
        """创建引导内容区域"""
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
            }}
        """)
        
        # 创建各个引导步骤
        self.create_welcome_step()
        self.create_interface_overview_step()
        self.create_ai_features_step()
        self.create_workflow_step()
        self.create_preferences_step()
        self.create_completion_step()
        
        layout.addWidget(self.content_stack)
    
    def create_welcome_step(self):
        """创建欢迎步骤"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 欢迎图标
        welcome_icon = QLabel("🎬")
        welcome_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_icon.setStyleSheet("font-size: 64px;")
        layout.addWidget(welcome_icon)
        
        # 欢迎标题
        welcome_title = QLabel("欢迎来到AI动画创作的新时代")
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-size: 24px;
                font-weight: bold;
                margin: 20px 0;
            }}
        """)
        layout.addWidget(welcome_title)
        
        # 欢迎描述
        welcome_desc = QLabel(
            "AI Animation Studio 是一款革命性的动画创作工具，\n"
            "结合了人工智能的强大能力和专业的动画制作功能。\n\n"
            "无论您是动画新手还是专业创作者，\n"
            "我们都将帮助您轻松创作出令人惊艳的动画作品。"
        )
        welcome_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_desc.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                font-size: 14px;
                line-height: 1.6;
            }}
        """)
        layout.addWidget(welcome_desc)
        
        # 特性列表
        features_frame = QFrame()
        features_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        
        features_layout = QVBoxLayout(features_frame)
        features_layout.setSpacing(10)
        
        features = [
            "🤖 AI智能生成 - 描述想法，AI帮您实现",
            "🎨 专业工具 - 完整的动画制作工具链",
            "⚡ 高效工作流 - 从创意到成品的流畅体验",
            "🌐 多格式导出 - 支持Web、视频等多种格式"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setStyleSheet(f"""
                QLabel {{
                    color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                    font-size: 12px;
                    padding: 5px 0;
                }}
            """)
            features_layout.addWidget(feature_label)
        
        layout.addWidget(features_frame)
        layout.addStretch()
        
        self.content_stack.addWidget(widget)

    def create_interface_overview_step(self):
        """创建界面概览步骤"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("🖥️ 界面布局概览")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 20px;
            }}
        """)
        layout.addWidget(title)

        # 界面布局图
        layout_desc = QLabel(
            "AI Animation Studio 采用专业的五区域布局：\n\n"
            "📁 左侧：资源管理区 - 项目文件、素材库、工具箱\n"
            "🎨 中央：主工作区 - 舞台编辑、预览控制\n"
            "🤖 右侧：AI控制区 - 智能生成、参数调整\n"
            "🎵 底部：时间轴区 - 音频管理、动画序列\n"
            "📊 状态栏：实时信息显示"
        )
        layout_desc.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                font-size: 14px;
                line-height: 1.8;
                background-color: white;
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 6px;
                padding: 20px;
            }}
        """)
        layout.addWidget(layout_desc)

        layout.addStretch()
        self.content_stack.addWidget(widget)

    def create_ai_features_step(self):
        """创建AI功能介绍步骤"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("🤖 AI智能功能")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 20px;
            }}
        """)
        layout.addWidget(title)

        ai_features = QLabel(
            "🎯 智能元素生成 - 描述需求，AI自动创建动画元素\n"
            "📝 智能脚本编写 - AI辅助生成动画代码\n"
            "🎨 风格化建议 - 根据内容推荐最佳视觉风格\n"
            "⚡ 自动优化 - 智能优化动画性能和效果\n"
            "🔧 智能修复 - 自动检测并修复常见问题"
        )
        ai_features.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                font-size: 14px;
                line-height: 2.0;
                background-color: white;
                border: 1px solid {color_scheme_manager.get_ai_function_colors()[0]};
                border-radius: 6px;
                padding: 20px;
            }}
        """)
        layout.addWidget(ai_features)

        layout.addStretch()
        self.content_stack.addWidget(widget)

    def create_workflow_step(self):
        """创建工作流程步骤"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("🔄 创作工作流程")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 20px;
            }}
        """)
        layout.addWidget(title)

        workflow = QLabel(
            "1️⃣ 项目创建 - 选择模板或从空白项目开始\n\n"
            "2️⃣ 音频导入 - 上传旁白音频作为时间参考\n\n"
            "3️⃣ AI生成 - 描述场景，让AI生成动画元素\n\n"
            "4️⃣ 精细调整 - 使用专业工具优化动画效果\n\n"
            "5️⃣ 预览测试 - 多设备预览确保效果完美\n\n"
            "6️⃣ 导出分享 - 多格式导出，轻松分享作品"
        )
        workflow.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                font-size: 14px;
                line-height: 1.8;
                background-color: white;
                border: 1px solid {color_scheme_manager.get_collaboration_colors()[0]};
                border-radius: 6px;
                padding: 20px;
            }}
        """)
        layout.addWidget(workflow)

        layout.addStretch()
        self.content_stack.addWidget(widget)

    def create_preferences_step(self):
        """创建偏好设置步骤"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("⚙️ 个性化设置")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_ai_function_colors()[0]};
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 20px;
            }}
        """)
        layout.addWidget(title)

        # 经验水平选择
        exp_label = QLabel("您的动画制作经验水平：")
        exp_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(exp_label)

        self.experience_combo = QComboBox()
        self.experience_combo.addItems([
            "🌱 新手 - 刚开始接触动画制作",
            "🌿 初级 - 有一些基础经验",
            "🌳 中级 - 熟悉动画制作流程",
            "🏆 高级 - 专业动画制作者"
        ])
        layout.addWidget(self.experience_combo)

        # 主要用途
        purpose_label = QLabel("主要用途：")
        purpose_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                font-size: 12px;
                font-weight: bold;
                margin-top: 20px;
            }}
        """)
        layout.addWidget(purpose_label)

        self.purpose_combo = QComboBox()
        self.purpose_combo.addItems([
            "📚 教育内容 - 制作教学动画",
            "💼 商业宣传 - 产品介绍、广告",
            "🎨 艺术创作 - 个人艺术表达",
            "📱 社交媒体 - 短视频内容"
        ])
        layout.addWidget(self.purpose_combo)

        layout.addStretch()
        self.content_stack.addWidget(widget)

    def create_completion_step(self):
        """创建完成步骤"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)

        # 完成图标
        completion_icon = QLabel("🎉")
        completion_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        completion_icon.setStyleSheet("font-size: 64px;")
        layout.addWidget(completion_icon)

        title = QLabel("恭喜！引导完成")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_collaboration_colors()[0]};
                font-size: 24px;
                font-weight: bold;
                margin: 20px 0;
            }}
        """)
        layout.addWidget(title)

        completion_desc = QLabel(
            "您已经完成了新手引导！\n\n"
            "现在您可以开始创作您的第一个动画项目了。\n"
            "如果需要帮助，随时可以在帮助菜单中找到相关资源。"
        )
        completion_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        completion_desc.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_PRIMARY)};
                font-size: 14px;
                line-height: 1.6;
            }}
        """)
        layout.addWidget(completion_desc)

        layout.addStretch()
        self.content_stack.addWidget(widget)

    def create_navigation_buttons(self, layout):
        """创建导航按钮"""
        button_frame = QFrame()
        button_frame.setFixedHeight(70)
        button_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border-top: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
        """)

        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(30, 15, 30, 15)

        # 上一步按钮
        self.prev_btn = QPushButton("← 上一步")
        self.prev_btn.setFixedSize(100, 40)
        self.prev_btn.setEnabled(False)
        self.prev_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover:enabled {{
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
            }}
        """)
        self.prev_btn.clicked.connect(self.previous_step)
        button_layout.addWidget(self.prev_btn)

        button_layout.addStretch()

        # 下一步/完成按钮
        self.next_btn = QPushButton("下一步 →")
        self.next_btn.setFixedSize(100, 40)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_ai_function_colors()[0]};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_ai_function_colors()[1]};
            }}
        """)
        self.next_btn.clicked.connect(self.next_step)
        button_layout.addWidget(self.next_btn)

        layout.addWidget(button_frame)

    def next_step(self):
        """下一步"""
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            self.update_step()
        else:
            self.complete_onboarding()

    def previous_step(self):
        """上一步"""
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step()

    def update_step(self):
        """更新步骤显示"""
        self.content_stack.setCurrentIndex(self.current_step)
        self.progress_bar.setValue(self.current_step + 1)

        # 更新步骤标题
        step_titles = [
            "步骤 1/6: 欢迎",
            "步骤 2/6: 界面概览",
            "步骤 3/6: AI功能",
            "步骤 4/6: 工作流程",
            "步骤 5/6: 个性化设置",
            "步骤 6/6: 完成"
        ]
        self.step_title.setText(step_titles[self.current_step])

        # 更新按钮状态
        self.prev_btn.setEnabled(self.current_step > 0)

        if self.current_step == self.total_steps - 1:
            self.next_btn.setText("开始使用 🚀")
        else:
            self.next_btn.setText("下一步 →")

    def skip_onboarding(self):
        """跳过引导"""
        self.skip_requested.emit()
        self.accept()

    def complete_onboarding(self):
        """完成引导"""
        # 保存用户偏好
        if hasattr(self, 'experience_combo'):
            self.user_preferences['experience'] = self.experience_combo.currentText()
        if hasattr(self, 'purpose_combo'):
            self.user_preferences['purpose'] = self.purpose_combo.currentText()

        logger.info(f"新手引导完成，用户偏好: {self.user_preferences}")

        self.onboarding_completed.emit()
        self.accept()

    def apply_color_scheme(self):
        """应用色彩方案"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
            }}
        """)
