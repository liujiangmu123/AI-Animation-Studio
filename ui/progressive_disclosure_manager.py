"""
AI Animation Studio - 渐进式功能披露管理器
实现三层功能可见性设计：基础层、进阶层、专家层
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QButtonGroup, QFrame, QScrollArea,
                             QGroupBox, QCheckBox, QSlider, QComboBox,
                             QTabWidget, QStackedWidget, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon

from core.value_hierarchy_config import get_value_hierarchy, UserExpertiseLevel, PriorityLevel
from core.logger import get_logger

logger = get_logger("progressive_disclosure_manager")


class DisclosureLevelIndicator(QWidget):
    """功能披露级别指示器"""
    
    level_changed = pyqtSignal(UserExpertiseLevel)
    
    def __init__(self):
        super().__init__()
        self.current_level = UserExpertiseLevel.INTERMEDIATE
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 标题
        title = QLabel("🎯 功能级别:")
        title.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 级别按钮组
        self.level_group = QButtonGroup()
        
        levels = [
            (UserExpertiseLevel.BEGINNER, "🌱 基础", "显示核心功能，隐藏复杂选项"),
            (UserExpertiseLevel.INTERMEDIATE, "🌿 进阶", "显示常用功能，部分高级选项"),
            (UserExpertiseLevel.ADVANCED, "🌳 高级", "显示大部分功能，专业工具可见"),
            (UserExpertiseLevel.EXPERT, "🔬 专家", "显示所有功能，包括调试工具")
        ]
        
        for i, (level, name, tooltip) in enumerate(levels):
            btn = QPushButton(name)
            btn.setToolTip(tooltip)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    border: 2px solid #dee2e6;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:checked {
                    background-color: #2C5AA0;
                    color: white;
                    border-color: #2C5AA0;
                }
                QPushButton:hover {
                    border-color: #4A90E2;
                }
            """)
            
            if level == self.current_level:
                btn.setChecked(True)
            
            btn.clicked.connect(lambda checked, l=level: self.set_level(l))
            self.level_group.addButton(btn, i)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # 功能统计
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #6c757d; font-size: 10px;")
        layout.addWidget(self.stats_label)
        
        self.update_stats()
    
    def set_level(self, level: UserExpertiseLevel):
        """设置功能级别"""
        if level != self.current_level:
            self.current_level = level
            self.update_stats()
            self.level_changed.emit(level)
            logger.info(f"功能披露级别切换到: {level.value}")
    
    def update_stats(self):
        """更新功能统计"""
        try:
            hierarchy = get_value_hierarchy()
            visible_features = hierarchy.get_visible_features(self.current_level)
            total_features = len(hierarchy.features)
            
            self.stats_label.setText(f"可见功能: {len(visible_features)}/{total_features}")
            
        except Exception as e:
            logger.error(f"更新功能统计失败: {e}")


class ProgressivePanel(QWidget):
    """渐进式面板基类"""
    
    def __init__(self, title: str, priority: PriorityLevel):
        super().__init__()
        self.title = title
        self.priority = priority
        self.is_disclosed = False
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题栏
        self.header = self.create_header()
        layout.addWidget(self.header)
        
        # 内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.setup_content()
        
        # 可折叠容器
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVisible(False)  # 初始隐藏
        layout.addWidget(self.scroll_area)
    
    def create_header(self) -> QWidget:
        """创建标题栏"""
        header = QFrame()
        header.setFrameStyle(QFrame.Shape.Box)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {self.get_priority_color()};
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 2px;
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # 展开/折叠按钮
        self.toggle_btn = QPushButton("▶")
        self.toggle_btn.setFixedSize(20, 20)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_disclosure)
        layout.addWidget(self.toggle_btn)
        
        # 标题
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # 优先级标识
        priority_label = QLabel(f"P{self.priority.value}")
        priority_label.setStyleSheet("color: white; font-size: 10px; font-weight: bold;")
        layout.addWidget(priority_label)
        
        return header
    
    def get_priority_color(self) -> str:
        """获取优先级颜色"""
        colors = {
            PriorityLevel.CORE: "#2C5AA0",      # 深蓝色
            PriorityLevel.PRIMARY: "#4A90E2",   # 蓝色
            PriorityLevel.SECONDARY: "#7B68EE", # 紫色
            PriorityLevel.ADVANCED: "#9370DB"   # 深紫色
        }
        return colors.get(self.priority, "#6c757d")
    
    def setup_content(self):
        """设置内容 - 子类重写"""
        pass
    
    def toggle_disclosure(self):
        """切换披露状态"""
        self.is_disclosed = not self.is_disclosed
        
        # 更新按钮图标
        self.toggle_btn.setText("▼" if self.is_disclosed else "▶")
        
        # 显示/隐藏内容
        self.scroll_area.setVisible(self.is_disclosed)
        
        # 动画效果
        self.animate_disclosure()
    
    def animate_disclosure(self):
        """披露动画"""
        if hasattr(self, 'animation'):
            self.animation.stop()
        
        self.animation = QPropertyAnimation(self.scroll_area, b"maximumHeight")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        if self.is_disclosed:
            self.animation.setStartValue(0)
            self.animation.setEndValue(300)  # 最大高度
        else:
            self.animation.setStartValue(self.scroll_area.height())
            self.animation.setEndValue(0)
        
        self.animation.start()
    
    def set_disclosed(self, disclosed: bool):
        """设置披露状态"""
        if disclosed != self.is_disclosed:
            self.toggle_disclosure()


class ProgressiveDisclosureManager(QWidget):
    """渐进式功能披露管理器"""
    
    def __init__(self):
        super().__init__()
        self.current_level = UserExpertiseLevel.INTERMEDIATE
        self.panels = {}
        self.setup_ui()
        logger.info("渐进式功能披露管理器初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 级别指示器
        self.level_indicator = DisclosureLevelIndicator()
        self.level_indicator.level_changed.connect(self.on_level_changed)
        layout.addWidget(self.level_indicator)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #dee2e6;")
        layout.addWidget(separator)
        
        # 功能面板容器
        self.panels_container = QWidget()
        self.panels_layout = QVBoxLayout(self.panels_container)
        self.panels_layout.setSpacing(3)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidget(self.panels_container)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        layout.addWidget(scroll)
        
        # 创建功能面板
        self.create_feature_panels()
        
        # 初始化披露状态
        self.update_disclosure_state()
    
    def create_feature_panels(self):
        """创建功能面板"""
        try:
            hierarchy = get_value_hierarchy()
            
            # 按优先级分组创建面板
            for priority in PriorityLevel:
                features = hierarchy.get_features_by_priority(priority)
                if features:
                    panel = self.create_priority_panel(priority, features)
                    self.panels[priority] = panel
                    self.panels_layout.addWidget(panel)
            
            self.panels_layout.addStretch()
            
        except Exception as e:
            logger.error(f"创建功能面板失败: {e}")
    
    def create_priority_panel(self, priority: PriorityLevel, features: list) -> ProgressivePanel:
        """创建优先级面板"""
        priority_names = {
            PriorityLevel.CORE: "🎯 核心功能",
            PriorityLevel.PRIMARY: "⭐ 主要功能", 
            PriorityLevel.SECONDARY: "🔧 次要功能",
            PriorityLevel.ADVANCED: "🔬 专家功能"
        }
        
        panel = ProgressivePanel(priority_names[priority], priority)
        
        # 添加功能项
        for feature in features:
            feature_item = self.create_feature_item(feature)
            panel.content_layout.addWidget(feature_item)
        
        return panel
    
    def create_feature_item(self, feature) -> QWidget:
        """创建功能项"""
        item = QFrame()
        item.setFrameStyle(QFrame.Shape.Box)
        item.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 2px;
            }
            QFrame:hover {
                border-color: #4A90E2;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(8, 6, 8, 6)
        
        # 功能图标
        icon_label = QLabel(feature.icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 14))
        layout.addWidget(icon_label)
        
        # 功能信息
        info_layout = QVBoxLayout()
        
        # 功能名称
        name_label = QLabel(feature.description)
        name_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        info_layout.addWidget(name_label)
        
        # 功能描述
        if feature.tooltip:
            desc_label = QLabel(feature.tooltip)
            desc_label.setStyleSheet("color: #6c757d; font-size: 10px;")
            desc_label.setWordWrap(True)
            info_layout.addWidget(desc_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # 快捷键
        if feature.shortcut:
            shortcut_label = QLabel(feature.shortcut)
            shortcut_label.setStyleSheet("""
                background-color: #e9ecef;
                border: 1px solid #ced4da;
                border-radius: 3px;
                padding: 2px 6px;
                font-size: 10px;
                font-family: monospace;
            """)
            layout.addWidget(shortcut_label)
        
        return item
    
    def on_level_changed(self, level: UserExpertiseLevel):
        """级别改变处理"""
        self.current_level = level
        self.update_disclosure_state()
        logger.info(f"功能披露级别已切换到: {level.value}")
    
    def update_disclosure_state(self):
        """更新披露状态"""
        try:
            hierarchy = get_value_hierarchy()
            hierarchy.set_expertise_level(self.current_level)
            
            # 根据用户级别决定面板的披露状态
            disclosure_rules = {
                UserExpertiseLevel.BEGINNER: {
                    PriorityLevel.CORE: True,      # 核心功能始终显示
                    PriorityLevel.PRIMARY: False,  # 主要功能折叠
                    PriorityLevel.SECONDARY: False, # 次要功能隐藏
                    PriorityLevel.ADVANCED: False   # 高级功能隐藏
                },
                UserExpertiseLevel.INTERMEDIATE: {
                    PriorityLevel.CORE: True,      # 核心功能展开
                    PriorityLevel.PRIMARY: True,   # 主要功能展开
                    PriorityLevel.SECONDARY: False, # 次要功能折叠
                    PriorityLevel.ADVANCED: False   # 高级功能隐藏
                },
                UserExpertiseLevel.ADVANCED: {
                    PriorityLevel.CORE: True,      # 核心功能展开
                    PriorityLevel.PRIMARY: True,   # 主要功能展开
                    PriorityLevel.SECONDARY: True, # 次要功能展开
                    PriorityLevel.ADVANCED: False  # 高级功能折叠
                },
                UserExpertiseLevel.EXPERT: {
                    PriorityLevel.CORE: True,      # 所有功能都展开
                    PriorityLevel.PRIMARY: True,
                    PriorityLevel.SECONDARY: True,
                    PriorityLevel.ADVANCED: True
                }
            }
            
            rules = disclosure_rules.get(self.current_level, {})
            
            for priority, panel in self.panels.items():
                should_disclose = rules.get(priority, False)
                should_show = self.should_show_panel(priority)
                
                # 设置面板可见性
                panel.setVisible(should_show)
                
                # 设置披露状态
                if should_show:
                    panel.set_disclosed(should_disclose)
            
        except Exception as e:
            logger.error(f"更新披露状态失败: {e}")
    
    def should_show_panel(self, priority: PriorityLevel) -> bool:
        """判断是否应该显示面板"""
        show_rules = {
            UserExpertiseLevel.BEGINNER: [PriorityLevel.CORE, PriorityLevel.PRIMARY],
            UserExpertiseLevel.INTERMEDIATE: [PriorityLevel.CORE, PriorityLevel.PRIMARY, PriorityLevel.SECONDARY],
            UserExpertiseLevel.ADVANCED: list(PriorityLevel),
            UserExpertiseLevel.EXPERT: list(PriorityLevel)
        }
        
        return priority in show_rules.get(self.current_level, [])
    
    def get_current_level(self) -> UserExpertiseLevel:
        """获取当前级别"""
        return self.current_level
    
    def set_level(self, level: UserExpertiseLevel):
        """设置级别"""
        self.level_indicator.set_level(level)
    
    def get_disclosed_features(self) -> list:
        """获取当前披露的功能"""
        try:
            hierarchy = get_value_hierarchy()
            return hierarchy.get_visible_features(self.current_level)
        except Exception as e:
            logger.error(f"获取披露功能失败: {e}")
            return []
    
    def export_disclosure_state(self) -> dict:
        """导出披露状态"""
        return {
            'current_level': self.current_level.value,
            'panel_states': {
                priority.name: panel.is_disclosed 
                for priority, panel in self.panels.items()
            },
            'visible_panels': {
                priority.name: panel.isVisible()
                for priority, panel in self.panels.items()
            }
        }
