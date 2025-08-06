"""
AI Animation Studio - 用户引导系统设计
实现新手引导、功能提示、操作指导等用户体验功能
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QScrollArea, QDialog, QTextEdit, QProgressBar,
                             QStackedWidget, QGroupBox, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QPainter, QPen, QBrush, QPolygon

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Callable
import json
from dataclasses import dataclass

from core.logger import get_logger

logger = get_logger("user_guidance_system")


class UserLevel(Enum):
    """用户级别枚举"""
    BEGINNER = 1        # 初学者
    INTERMEDIATE = 2    # 中级用户
    EXPERT = 3          # 专家用户


class GuideType(Enum):
    """引导类型枚举"""
    WELCOME = "welcome"             # 欢迎引导
    FEATURE_INTRO = "feature_intro" # 功能介绍
    WORKFLOW = "workflow"           # 工作流程引导
    TOOLTIP = "tooltip"             # 工具提示
    SPOTLIGHT = "spotlight"         # 聚光灯引导
    OVERLAY = "overlay"             # 覆盖层引导


class GuideStep(Enum):
    """引导步骤枚举"""
    AUDIO_IMPORT = "audio_import"
    TIME_SEGMENT = "time_segment"
    ANIMATION_DESC = "animation_desc"
    AI_GENERATION = "ai_generation"
    PREVIEW_ADJUST = "preview_adjust"
    EXPORT_RENDER = "export_render"


@dataclass
class GuideContent:
    """引导内容"""
    title: str
    description: str
    target_element: str
    position: str  # top, bottom, left, right
    action_text: str = "下一步"
    skip_enabled: bool = True
    highlight_element: bool = True
    animation_type: str = "fade_in"


class WelcomeGuideDialog(QDialog):
    """欢迎引导对话框"""
    
    guide_started = pyqtSignal(str)  # 引导开始信号
    guide_skipped = pyqtSignal()     # 引导跳过信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("欢迎使用 AI Animation Studio")
        self.setFixedSize(600, 400)
        self.setModal(True)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 欢迎标题
        title_label = QLabel("欢迎使用 AI Animation Studio")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2C5AA0; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 描述文本
        desc_label = QLabel(
            "AI Animation Studio 是一款智能动画创作工具，"
            "通过简单的音频导入和描述，即可生成精美的动画作品。\n\n"
            "让我们通过快速引导，帮助您了解基本的创作流程。"
        )
        desc_label.setFont(QFont("Microsoft YaHei", 12))
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("color: #666666; line-height: 1.5;")
        layout.addWidget(desc_label)
        
        # 功能特色
        features_group = QGroupBox("主要功能特色")
        features_group.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        features_layout = QVBoxLayout(features_group)
        
        features = [
            "🎵 智能音频分析 - 自动识别音频节拍和情感",
            "⏱️ 可视化时间轴 - 直观的时间段标记和编辑",
            "🤖 AI动画生成 - 基于描述自动生成动画代码",
            "👁️ 实时预览 - 所见即所得的动画预览",
            "📤 多格式导出 - 支持视频、GIF、HTML等格式"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setFont(QFont("Microsoft YaHei", 10))
            feature_label.setStyleSheet("color: #333333; margin: 5px 0;")
            features_layout.addWidget(feature_label)
        
        layout.addWidget(features_group)
        
        # 用户级别选择
        level_group = QGroupBox("选择您的使用经验")
        level_group.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        level_layout = QVBoxLayout(level_group)
        
        self.level_combo = QComboBox()
        self.level_combo.addItems([
            "初学者 - 我是第一次使用类似工具",
            "中级用户 - 我有一些动画制作经验",
            "专家用户 - 我是专业的动画制作人员"
        ])
        self.level_combo.setFont(QFont("Microsoft YaHei", 10))
        level_layout.addWidget(self.level_combo)
        
        layout.addWidget(level_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 跳过按钮
        skip_btn = QPushButton("跳过引导")
        skip_btn.setFont(QFont("Microsoft YaHei", 10))
        skip_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                color: #666666;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        skip_btn.clicked.connect(self.skip_guide)
        button_layout.addWidget(skip_btn)
        
        button_layout.addStretch()
        
        # 开始引导按钮
        start_btn = QPushButton("开始引导")
        start_btn.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2C5AA0;
                border: none;
                border-radius: 6px;
                padding: 10px 30px;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        start_btn.clicked.connect(self.start_guide)
        button_layout.addWidget(start_btn)
        
        layout.addWidget(button_layout)
    
    def start_guide(self):
        """开始引导"""
        level_index = self.level_combo.currentIndex()
        level_map = {0: "beginner", 1: "intermediate", 2: "expert"}
        user_level = level_map.get(level_index, "beginner")
        
        self.guide_started.emit(user_level)
        self.accept()
    
    def skip_guide(self):
        """跳过引导"""
        self.guide_skipped.emit()
        self.reject()


class GuideTooltip(QWidget):
    """引导工具提示"""
    
    next_clicked = pyqtSignal()      # 下一步信号
    skip_clicked = pyqtSignal()      # 跳过信号
    close_clicked = pyqtSignal()     # 关闭信号
    
    def __init__(self, content: GuideContent, parent=None):
        super().__init__(parent)
        self.content = content
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 主容器
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #2C5AA0;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel(self.content.title)
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2C5AA0;")
        container_layout.addWidget(title_label)
        
        # 描述
        desc_label = QLabel(self.content.description)
        desc_label.setFont(QFont("Microsoft YaHei", 11))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #333333; line-height: 1.4;")
        container_layout.addWidget(desc_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        if self.content.skip_enabled:
            skip_btn = QPushButton("跳过")
            skip_btn.setFont(QFont("Microsoft YaHei", 9))
            skip_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #CCCCCC;
                    border-radius: 4px;
                    padding: 6px 12px;
                    color: #666666;
                }
                QPushButton:hover {
                    background-color: #F5F5F5;
                }
            """)
            skip_btn.clicked.connect(self.skip_clicked.emit)
            button_layout.addWidget(skip_btn)
        
        button_layout.addStretch()
        
        # 下一步按钮
        next_btn = QPushButton(self.content.action_text)
        next_btn.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #2C5AA0;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        next_btn.clicked.connect(self.next_clicked.emit)
        button_layout.addWidget(next_btn)
        
        container_layout.addLayout(button_layout)
        layout.addWidget(container)
        
        # 绘制指向箭头
        self.draw_arrow()
    
    def draw_arrow(self):
        """绘制指向箭头"""
        # 这里可以根据position参数绘制不同方向的箭头
        pass
    
    def show_at_position(self, target_rect: QRect):
        """在指定位置显示"""
        # 计算工具提示位置
        tooltip_width = 300
        tooltip_height = 150
        
        if self.content.position == "top":
            x = target_rect.center().x() - tooltip_width // 2
            y = target_rect.top() - tooltip_height - 10
        elif self.content.position == "bottom":
            x = target_rect.center().x() - tooltip_width // 2
            y = target_rect.bottom() + 10
        elif self.content.position == "left":
            x = target_rect.left() - tooltip_width - 10
            y = target_rect.center().y() - tooltip_height // 2
        elif self.content.position == "right":
            x = target_rect.right() + 10
            y = target_rect.center().y() - tooltip_height // 2
        else:
            x = target_rect.center().x() - tooltip_width // 2
            y = target_rect.bottom() + 10
        
        self.setGeometry(x, y, tooltip_width, tooltip_height)
        self.show()


class SpotlightOverlay(QWidget):
    """聚光灯覆盖层"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.target_rect = None
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        if parent:
            self.setGeometry(parent.geometry())
    
    def set_target(self, rect: QRect):
        """设置目标区域"""
        self.target_rect = rect
        self.update()
    
    def paintEvent(self, event):
        """绘制事件"""
        if not self.target_rect:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制半透明遮罩
        painter.fillRect(self.rect(), QColor(0, 0, 0, 150))
        
        # 清除目标区域（创建聚光灯效果）
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.fillRect(self.target_rect, Qt.GlobalColor.transparent)
        
        # 绘制高亮边框
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.setPen(QPen(QColor(44, 90, 160), 3))
        painter.drawRect(self.target_rect)


class UserGuidanceManager(QObject):
    """用户引导管理器"""
    
    guide_completed = pyqtSignal(str)    # 引导完成信号
    guide_skipped = pyqtSignal()         # 引导跳过信号
    step_changed = pyqtSignal(str, int)  # 步骤改变信号
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.user_level = UserLevel.BEGINNER
        self.current_guide_type = None
        self.current_step = 0
        self.guide_steps = []
        self.active_tooltip = None
        self.spotlight_overlay = None
        
        self.setup_guide_content()
        logger.info("用户引导管理器初始化完成")
    
    def setup_guide_content(self):
        """设置引导内容"""
        self.guide_contents = {
            GuideStep.AUDIO_IMPORT: GuideContent(
                title="第1步：导入音频",
                description="首先，让我们导入一个音频文件。点击"导入音频"按钮，选择您想要制作动画的音频文件。",
                target_element="import_audio_btn",
                position="bottom",
                action_text="我知道了"
            ),
            GuideStep.TIME_SEGMENT: GuideContent(
                title="第2步：标记时间段",
                description="音频导入后，您可以在时间轴上标记不同的时间段。每个时间段可以设置不同的动画内容。",
                target_element="timeline_widget",
                position="top",
                action_text="继续"
            ),
            GuideStep.ANIMATION_DESC: GuideContent(
                title="第3步：描述动画",
                description="为每个时间段添加动画描述。用简单的文字描述您想要的动画效果，AI会帮您生成相应的动画。",
                target_element="description_panel",
                position="left",
                action_text="下一步"
            ),
            GuideStep.AI_GENERATION: GuideContent(
                title="第4步：AI生成动画",
                description="点击"生成动画"按钮，AI将根据您的描述和音频特征，自动生成动画代码。",
                target_element="generate_btn",
                position="top",
                action_text="继续"
            ),
            GuideStep.PREVIEW_ADJUST: GuideContent(
                title="第5步：预览和调整",
                description="在预览窗口中查看生成的动画效果。您可以实时调整参数，直到满意为止。",
                target_element="preview_widget",
                position="left",
                action_text="下一步"
            ),
            GuideStep.EXPORT_RENDER: GuideContent(
                title="第6步：导出作品",
                description="最后，将您的动画作品导出为视频、GIF或其他格式。恭喜您完成了第一个AI动画作品！",
                target_element="export_btn",
                position="top",
                action_text="完成引导"
            )
        }
    
    def show_welcome_guide(self):
        """显示欢迎引导"""
        welcome_dialog = WelcomeGuideDialog(self.main_window)
        welcome_dialog.guide_started.connect(self.start_workflow_guide)
        welcome_dialog.guide_skipped.connect(self.guide_skipped.emit)
        welcome_dialog.exec()
    
    def start_workflow_guide(self, user_level: str):
        """开始工作流程引导"""
        level_map = {"beginner": UserLevel.BEGINNER, "intermediate": UserLevel.INTERMEDIATE, "expert": UserLevel.EXPERT}
        self.user_level = level_map.get(user_level, UserLevel.BEGINNER)
        
        # 根据用户级别设置引导步骤
        if self.user_level == UserLevel.BEGINNER:
            self.guide_steps = list(GuideStep)
        elif self.user_level == UserLevel.INTERMEDIATE:
            self.guide_steps = [GuideStep.AI_GENERATION, GuideStep.PREVIEW_ADJUST, GuideStep.EXPORT_RENDER]
        else:  # EXPERT
            self.guide_steps = [GuideStep.EXPORT_RENDER]
        
        self.current_step = 0
        self.current_guide_type = GuideType.WORKFLOW
        
        self.show_next_step()
    
    def show_next_step(self):
        """显示下一步"""
        if self.current_step >= len(self.guide_steps):
            self.complete_guide()
            return
        
        step = self.guide_steps[self.current_step]
        content = self.guide_contents[step]
        
        # 获取目标元素
        target_widget = self.find_target_widget(content.target_element)
        if not target_widget:
            logger.warning(f"未找到目标元素: {content.target_element}")
            self.current_step += 1
            self.show_next_step()
            return
        
        # 显示聚光灯效果
        if content.highlight_element:
            self.show_spotlight(target_widget.geometry())
        
        # 显示工具提示
        self.show_tooltip(content, target_widget.geometry())
        
        # 发送步骤改变信号
        self.step_changed.emit(step.value, self.current_step + 1)
        
        logger.info(f"显示引导步骤: {step.value} ({self.current_step + 1}/{len(self.guide_steps)})")
    
    def find_target_widget(self, element_name: str) -> Optional[QWidget]:
        """查找目标组件"""
        if hasattr(self.main_window, element_name):
            return getattr(self.main_window, element_name)
        
        # 递归查找子组件
        for child in self.main_window.findChildren(QWidget):
            if child.objectName() == element_name:
                return child
        
        return None
    
    def show_spotlight(self, target_rect: QRect):
        """显示聚光灯效果"""
        if not self.spotlight_overlay:
            self.spotlight_overlay = SpotlightOverlay(self.main_window)
        
        self.spotlight_overlay.set_target(target_rect)
        self.spotlight_overlay.show()
    
    def show_tooltip(self, content: GuideContent, target_rect: QRect):
        """显示工具提示"""
        if self.active_tooltip:
            self.active_tooltip.close()
        
        self.active_tooltip = GuideTooltip(content, self.main_window)
        self.active_tooltip.next_clicked.connect(self.on_next_step)
        self.active_tooltip.skip_clicked.connect(self.skip_guide)
        self.active_tooltip.show_at_position(target_rect)
    
    def on_next_step(self):
        """下一步处理"""
        self.current_step += 1
        self.hide_current_guide()
        self.show_next_step()
    
    def skip_guide(self):
        """跳过引导"""
        self.hide_current_guide()
        self.guide_skipped.emit()
    
    def complete_guide(self):
        """完成引导"""
        self.hide_current_guide()
        self.guide_completed.emit(self.current_guide_type.value if self.current_guide_type else "unknown")
        
        logger.info("用户引导完成")
    
    def hide_current_guide(self):
        """隐藏当前引导"""
        if self.active_tooltip:
            self.active_tooltip.close()
            self.active_tooltip = None
        
        if self.spotlight_overlay:
            self.spotlight_overlay.hide()
    
    def show_feature_tooltip(self, element_name: str, title: str, description: str):
        """显示功能提示"""
        target_widget = self.find_target_widget(element_name)
        if not target_widget:
            return
        
        content = GuideContent(
            title=title,
            description=description,
            target_element=element_name,
            position="bottom",
            action_text="知道了",
            skip_enabled=False
        )
        
        self.show_tooltip(content, target_widget.geometry())
    
    def get_guidance_summary(self) -> Dict[str, Any]:
        """获取引导摘要"""
        return {
            "user_level": self.user_level.name,
            "current_guide_type": self.current_guide_type.value if self.current_guide_type else None,
            "current_step": self.current_step,
            "total_steps": len(self.guide_steps),
            "guide_active": self.active_tooltip is not None
        }
