"""
AI Animation Studio - 灵活的工作空间定制系统
实现模块化界面配置，支持个性化工作空间定制
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QDialog, QTabWidget, QGroupBox, QFormLayout, QCheckBox,
                             QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QTextEdit,
                             QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
                             QSplitter, QFrame, QScrollArea, QSlider, QButtonGroup,
                             QRadioButton, QColorDialog, QFontDialog, QMessageBox,
                             QApplication, QMenu, QToolButton, QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QPropertyAnimation, QEasingCurve, QRect, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QBrush, QPen, QPalette

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
import json
import time
from dataclasses import dataclass, field
from datetime import datetime

from core.logger import get_logger

logger = get_logger("workspace_customization_system")


class WorkspaceMode(Enum):
    """工作空间模式枚举"""
    BEGINNER = "beginner"           # 新手模式
    PROFESSIONAL = "professional"   # 专业模式
    CREATIVE = "creative"           # 创作模式
    PREVIEW_FOCUSED = "preview_focused"  # 预览模式
    MINIMAL = "minimal"             # 极简模式
    CUSTOM = "custom"               # 自定义模式


class PanelType(Enum):
    """面板类型枚举"""
    AUDIO_CONTROL = "audio_control"         # 音频控制
    TIME_SEGMENT = "time_segment"           # 时间段标记
    AI_GENERATOR = "ai_generator"           # AI生成器
    STAGE_EDITOR = "stage_editor"           # 舞台编辑器
    ELEMENTS_MANAGER = "elements_manager"   # 元素管理器
    PROPERTIES_PANEL = "properties_panel"  # 属性面板
    TIMELINE = "timeline"                   # 时间轴
    PREVIEW = "preview"                     # 预览
    LIBRARY_MANAGER = "library_manager"    # 库管理
    RULES_MANAGER = "rules_manager"         # 规则管理
    SETTINGS = "settings"                   # 设置
    DEVELOPER_TOOLS = "developer_tools"    # 开发者工具


class PanelPosition(Enum):
    """面板位置枚举"""
    LEFT = "left"           # 左侧
    RIGHT = "right"         # 右侧
    TOP = "top"             # 顶部
    BOTTOM = "bottom"       # 底部
    CENTER = "center"       # 中央
    FLOATING = "floating"   # 浮动


class ThemeStyle(Enum):
    """主题样式枚举"""
    LIGHT = "light"         # 浅色主题
    DARK = "dark"           # 深色主题
    AUTO = "auto"           # 自动主题
    CUSTOM = "custom"       # 自定义主题


@dataclass
class PanelConfig:
    """面板配置"""
    panel_type: PanelType
    position: PanelPosition
    visible: bool = True
    width: int = 300
    height: int = 200
    min_width: int = 200
    max_width: int = 800
    min_height: int = 150
    max_height: int = 600
    collapsible: bool = True
    resizable: bool = True
    dockable: bool = True
    priority: int = 0  # 优先级，用于空间不足时的处理
    custom_properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkspaceConfig:
    """工作空间配置"""
    name: str
    description: str
    mode: WorkspaceMode
    panels: Dict[str, PanelConfig] = field(default_factory=dict)
    layout_ratios: Dict[str, float] = field(default_factory=dict)  # 布局比例
    theme: ThemeStyle = ThemeStyle.LIGHT
    shortcuts: Dict[str, str] = field(default_factory=dict)
    toolbar_config: Dict[str, Any] = field(default_factory=dict)
    menu_config: Dict[str, Any] = field(default_factory=dict)
    created_time: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    is_default: bool = False
    tags: List[str] = field(default_factory=list)


class WorkspacePresetManager:
    """工作空间预设管理器"""
    
    def __init__(self):
        self.presets: Dict[str, WorkspaceConfig] = {}
        self.initialize_default_presets()
        
        logger.info("工作空间预设管理器初始化完成")
    
    def initialize_default_presets(self):
        """初始化默认预设"""
        # 新手模式
        beginner_config = WorkspaceConfig(
            name="新手模式",
            description="简化界面，突出核心功能，适合初学者使用",
            mode=WorkspaceMode.BEGINNER,
            panels={
                "audio_control": PanelConfig(PanelType.AUDIO_CONTROL, PanelPosition.LEFT, True, 280, 200),
                "time_segment": PanelConfig(PanelType.TIME_SEGMENT, PanelPosition.LEFT, True, 280, 150),
                "ai_generator": PanelConfig(PanelType.AI_GENERATOR, PanelPosition.CENTER, True, 600, 400),
                "preview": PanelConfig(PanelType.PREVIEW, PanelPosition.RIGHT, True, 300, 250),
                "timeline": PanelConfig(PanelType.TIMELINE, PanelPosition.BOTTOM, True, 800, 120),
                # 隐藏高级功能
                "library_manager": PanelConfig(PanelType.LIBRARY_MANAGER, PanelPosition.RIGHT, False),
                "rules_manager": PanelConfig(PanelType.RULES_MANAGER, PanelPosition.RIGHT, False),
                "developer_tools": PanelConfig(PanelType.DEVELOPER_TOOLS, PanelPosition.RIGHT, False)
            },
            layout_ratios={"left": 0.25, "center": 0.50, "right": 0.25, "bottom": 0.15},
            theme=ThemeStyle.LIGHT,
            is_default=True,
            tags=["简单", "新手", "核心功能"]
        )
        
        # 专业模式
        professional_config = WorkspaceConfig(
            name="专业模式",
            description="完整功能界面，最大化工作效率，适合专业用户",
            mode=WorkspaceMode.PROFESSIONAL,
            panels={
                "audio_control": PanelConfig(PanelType.AUDIO_CONTROL, PanelPosition.LEFT, True, 250, 180),
                "time_segment": PanelConfig(PanelType.TIME_SEGMENT, PanelPosition.LEFT, True, 250, 120),
                "elements_manager": PanelConfig(PanelType.ELEMENTS_MANAGER, PanelPosition.LEFT, True, 250, 200),
                "ai_generator": PanelConfig(PanelType.AI_GENERATOR, PanelPosition.CENTER, True, 500, 300),
                "stage_editor": PanelConfig(PanelType.STAGE_EDITOR, PanelPosition.CENTER, True, 500, 300),
                "properties_panel": PanelConfig(PanelType.PROPERTIES_PANEL, PanelPosition.RIGHT, True, 280, 250),
                "preview": PanelConfig(PanelType.PREVIEW, PanelPosition.RIGHT, True, 280, 200),
                "library_manager": PanelConfig(PanelType.LIBRARY_MANAGER, PanelPosition.RIGHT, True, 280, 150),
                "timeline": PanelConfig(PanelType.TIMELINE, PanelPosition.BOTTOM, True, 800, 140)
            },
            layout_ratios={"left": 0.20, "center": 0.50, "right": 0.30, "bottom": 0.18},
            theme=ThemeStyle.DARK,
            is_default=True,
            tags=["专业", "完整功能", "高效"]
        )
        
        # 创作模式
        creative_config = WorkspaceConfig(
            name="创作模式",
            description="突出创作工具，优化创意工作流程",
            mode=WorkspaceMode.CREATIVE,
            panels={
                "ai_generator": PanelConfig(PanelType.AI_GENERATOR, PanelPosition.LEFT, True, 350, 400),
                "stage_editor": PanelConfig(PanelType.STAGE_EDITOR, PanelPosition.CENTER, True, 600, 450),
                "elements_manager": PanelConfig(PanelType.ELEMENTS_MANAGER, PanelPosition.RIGHT, True, 250, 200),
                "properties_panel": PanelConfig(PanelType.PROPERTIES_PANEL, PanelPosition.RIGHT, True, 250, 200),
                "library_manager": PanelConfig(PanelType.LIBRARY_MANAGER, PanelPosition.RIGHT, True, 250, 150),
                "timeline": PanelConfig(PanelType.TIMELINE, PanelPosition.BOTTOM, True, 800, 120),
                # 简化音频控制
                "audio_control": PanelConfig(PanelType.AUDIO_CONTROL, PanelPosition.BOTTOM, True, 200, 80),
                "preview": PanelConfig(PanelType.PREVIEW, PanelPosition.FLOATING, True, 300, 200)
            },
            layout_ratios={"left": 0.25, "center": 0.50, "right": 0.25, "bottom": 0.15},
            theme=ThemeStyle.DARK,
            is_default=True,
            tags=["创作", "设计", "艺术"]
        )
        
        # 预览模式
        preview_config = WorkspaceConfig(
            name="预览模式",
            description="突出预览功能，适合演示和展示",
            mode=WorkspaceMode.PREVIEW_FOCUSED,
            panels={
                "preview": PanelConfig(PanelType.PREVIEW, PanelPosition.CENTER, True, 800, 600),
                "timeline": PanelConfig(PanelType.TIMELINE, PanelPosition.BOTTOM, True, 800, 100),
                "audio_control": PanelConfig(PanelType.AUDIO_CONTROL, PanelPosition.LEFT, True, 200, 150),
                # 隐藏编辑工具
                "ai_generator": PanelConfig(PanelType.AI_GENERATOR, PanelPosition.LEFT, False),
                "stage_editor": PanelConfig(PanelType.STAGE_EDITOR, PanelPosition.CENTER, False),
                "elements_manager": PanelConfig(PanelType.ELEMENTS_MANAGER, PanelPosition.RIGHT, False),
                "properties_panel": PanelConfig(PanelType.PROPERTIES_PANEL, PanelPosition.RIGHT, False)
            },
            layout_ratios={"left": 0.15, "center": 0.70, "right": 0.15, "bottom": 0.12},
            theme=ThemeStyle.DARK,
            is_default=True,
            tags=["预览", "演示", "展示"]
        )
        
        # 极简模式
        minimal_config = WorkspaceConfig(
            name="极简模式",
            description="最小化界面元素，专注核心工作流程",
            mode=WorkspaceMode.MINIMAL,
            panels={
                "ai_generator": PanelConfig(PanelType.AI_GENERATOR, PanelPosition.CENTER, True, 600, 400),
                "preview": PanelConfig(PanelType.PREVIEW, PanelPosition.RIGHT, True, 300, 300),
                "timeline": PanelConfig(PanelType.TIMELINE, PanelPosition.BOTTOM, True, 800, 80),
                # 隐藏大部分面板
                "audio_control": PanelConfig(PanelType.AUDIO_CONTROL, PanelPosition.LEFT, False),
                "time_segment": PanelConfig(PanelType.TIME_SEGMENT, PanelPosition.LEFT, False),
                "elements_manager": PanelConfig(PanelType.ELEMENTS_MANAGER, PanelPosition.RIGHT, False),
                "properties_panel": PanelConfig(PanelType.PROPERTIES_PANEL, PanelPosition.RIGHT, False),
                "library_manager": PanelConfig(PanelType.LIBRARY_MANAGER, PanelPosition.RIGHT, False)
            },
            layout_ratios={"left": 0.10, "center": 0.65, "right": 0.25, "bottom": 0.10},
            theme=ThemeStyle.LIGHT,
            is_default=True,
            tags=["极简", "专注", "简洁"]
        )
        
        # 注册预设
        self.presets["beginner"] = beginner_config
        self.presets["professional"] = professional_config
        self.presets["creative"] = creative_config
        self.presets["preview_focused"] = preview_config
        self.presets["minimal"] = minimal_config
        
        logger.info(f"初始化了 {len(self.presets)} 个默认工作空间预设")
    
    def get_preset(self, preset_name: str) -> Optional[WorkspaceConfig]:
        """获取预设配置"""
        return self.presets.get(preset_name)
    
    def get_all_presets(self) -> Dict[str, WorkspaceConfig]:
        """获取所有预设"""
        return self.presets.copy()
    
    def add_custom_preset(self, config: WorkspaceConfig):
        """添加自定义预设"""
        config.mode = WorkspaceMode.CUSTOM
        config.is_default = False
        config.last_modified = datetime.now()
        
        self.presets[config.name] = config
        logger.info(f"添加自定义工作空间预设: {config.name}")
    
    def remove_preset(self, preset_name: str) -> bool:
        """移除预设"""
        if preset_name in self.presets:
            config = self.presets[preset_name]
            if config.is_default:
                logger.warning(f"无法删除默认预设: {preset_name}")
                return False
            
            del self.presets[preset_name]
            logger.info(f"移除工作空间预设: {preset_name}")
            return True
        
        return False
    
    def export_preset(self, preset_name: str, file_path: str) -> bool:
        """导出预设"""
        try:
            if preset_name not in self.presets:
                return False
            
            config = self.presets[preset_name]
            
            # 转换为可序列化的字典
            export_data = {
                "name": config.name,
                "description": config.description,
                "mode": config.mode.value,
                "panels": {
                    name: {
                        "panel_type": panel.panel_type.value,
                        "position": panel.position.value,
                        "visible": panel.visible,
                        "width": panel.width,
                        "height": panel.height,
                        "min_width": panel.min_width,
                        "max_width": panel.max_width,
                        "min_height": panel.min_height,
                        "max_height": panel.max_height,
                        "collapsible": panel.collapsible,
                        "resizable": panel.resizable,
                        "dockable": panel.dockable,
                        "priority": panel.priority,
                        "custom_properties": panel.custom_properties
                    }
                    for name, panel in config.panels.items()
                },
                "layout_ratios": config.layout_ratios,
                "theme": config.theme.value,
                "shortcuts": config.shortcuts,
                "toolbar_config": config.toolbar_config,
                "menu_config": config.menu_config,
                "tags": config.tags,
                "export_time": datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"工作空间预设已导出: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出工作空间预设失败: {e}")
            return False
    
    def import_preset(self, file_path: str) -> bool:
        """导入预设"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 重建配置对象
            panels = {}
            for name, panel_data in data.get("panels", {}).items():
                panels[name] = PanelConfig(
                    panel_type=PanelType(panel_data["panel_type"]),
                    position=PanelPosition(panel_data["position"]),
                    visible=panel_data.get("visible", True),
                    width=panel_data.get("width", 300),
                    height=panel_data.get("height", 200),
                    min_width=panel_data.get("min_width", 200),
                    max_width=panel_data.get("max_width", 800),
                    min_height=panel_data.get("min_height", 150),
                    max_height=panel_data.get("max_height", 600),
                    collapsible=panel_data.get("collapsible", True),
                    resizable=panel_data.get("resizable", True),
                    dockable=panel_data.get("dockable", True),
                    priority=panel_data.get("priority", 0),
                    custom_properties=panel_data.get("custom_properties", {})
                )
            
            config = WorkspaceConfig(
                name=data["name"],
                description=data["description"],
                mode=WorkspaceMode(data["mode"]),
                panels=panels,
                layout_ratios=data.get("layout_ratios", {}),
                theme=ThemeStyle(data.get("theme", "light")),
                shortcuts=data.get("shortcuts", {}),
                toolbar_config=data.get("toolbar_config", {}),
                menu_config=data.get("menu_config", {}),
                tags=data.get("tags", [])
            )
            
            self.add_custom_preset(config)
            logger.info(f"工作空间预设已导入: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"导入工作空间预设失败: {e}")
            return False


class WorkspaceCustomizationDialog(QDialog):
    """工作空间定制对话框"""

    workspace_applied = pyqtSignal(str)  # 工作空间应用信号

    def __init__(self, preset_manager: WorkspacePresetManager, current_config: WorkspaceConfig = None, parent=None):
        super().__init__(parent)
        self.preset_manager = preset_manager
        self.current_config = current_config
        self.preview_config = None

        self.setup_ui()
        self.setup_connections()
        self.load_presets()

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("工作空间定制")
        self.setMinimumSize(900, 700)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel("🎨 工作空间定制")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c5aa0; margin: 10px;")
        layout.addWidget(title_label)

        # 主要内容区域
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：预设列表
        self.create_presets_panel(content_splitter)

        # 右侧：配置详情
        self.create_config_panel(content_splitter)

        # 设置分割器比例
        content_splitter.setSizes([300, 600])
        layout.addWidget(content_splitter)

        # 底部按钮
        self.create_action_buttons(layout)

    def create_presets_panel(self, parent):
        """创建预设面板"""
        presets_frame = QFrame()
        presets_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        presets_layout = QVBoxLayout(presets_frame)

        # 预设列表标题
        presets_title = QLabel("📋 工作空间预设")
        presets_title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        presets_layout.addWidget(presets_title)

        # 预设列表
        self.presets_list = QListWidget()
        self.presets_list.setMinimumWidth(280)
        presets_layout.addWidget(self.presets_list)

        # 预设操作按钮
        preset_buttons_layout = QHBoxLayout()

        self.import_btn = QPushButton("📥 导入")
        self.import_btn.clicked.connect(self.import_preset)
        preset_buttons_layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("📤 导出")
        self.export_btn.clicked.connect(self.export_preset)
        preset_buttons_layout.addWidget(self.export_btn)

        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.clicked.connect(self.delete_preset)
        preset_buttons_layout.addWidget(self.delete_btn)

        presets_layout.addLayout(preset_buttons_layout)

        parent.addWidget(presets_frame)

    def create_config_panel(self, parent):
        """创建配置面板"""
        config_frame = QFrame()
        config_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        config_layout = QVBoxLayout(config_frame)

        # 配置标签页
        self.config_tabs = QTabWidget()

        # 基本信息标签页
        self.create_basic_info_tab()

        # 面板配置标签页
        self.create_panels_config_tab()

        # 布局配置标签页
        self.create_layout_config_tab()

        # 主题配置标签页
        self.create_theme_config_tab()

        config_layout.addWidget(self.config_tabs)

        # 预览按钮
        preview_layout = QHBoxLayout()

        self.preview_btn = QPushButton("👁️ 预览配置")
        self.preview_btn.clicked.connect(self.preview_configuration)
        preview_layout.addWidget(self.preview_btn)

        self.reset_btn = QPushButton("🔄 重置配置")
        self.reset_btn.clicked.connect(self.reset_configuration)
        preview_layout.addWidget(self.reset_btn)

        config_layout.addLayout(preview_layout)

        parent.addWidget(config_frame)

    def create_basic_info_tab(self):
        """创建基本信息标签页"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # 工作空间名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入工作空间名称")
        layout.addRow("名称:", self.name_edit)

        # 描述
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("输入工作空间描述")
        layout.addRow("描述:", self.description_edit)

        # 模式选择
        self.mode_combo = QComboBox()
        for mode in WorkspaceMode:
            self.mode_combo.addItem(mode.value.replace('_', ' ').title(), mode.value)
        layout.addRow("模式:", self.mode_combo)

        # 标签
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("输入标签，用逗号分隔")
        layout.addRow("标签:", self.tags_edit)

        self.config_tabs.addTab(tab, "📝 基本信息")

    def create_panels_config_tab(self):
        """创建面板配置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 面板列表
        panels_label = QLabel("面板配置:")
        panels_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        layout.addWidget(panels_label)

        # 面板配置树
        self.panels_tree = QTreeWidget()
        self.panels_tree.setHeaderLabels(["面板", "位置", "可见", "尺寸"])
        self.panels_tree.setMinimumHeight(300)
        layout.addWidget(self.panels_tree)

        # 面板操作按钮
        panel_buttons_layout = QHBoxLayout()

        self.add_panel_btn = QPushButton("➕ 添加面板")
        self.add_panel_btn.clicked.connect(self.add_panel_config)
        panel_buttons_layout.addWidget(self.add_panel_btn)

        self.edit_panel_btn = QPushButton("✏️ 编辑面板")
        self.edit_panel_btn.clicked.connect(self.edit_panel_config)
        panel_buttons_layout.addWidget(self.edit_panel_btn)

        self.remove_panel_btn = QPushButton("➖ 移除面板")
        self.remove_panel_btn.clicked.connect(self.remove_panel_config)
        panel_buttons_layout.addWidget(self.remove_panel_btn)

        layout.addLayout(panel_buttons_layout)

        self.config_tabs.addTab(tab, "🎛️ 面板配置")

    def create_layout_config_tab(self):
        """创建布局配置标签页"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # 布局比例配置
        layout_label = QLabel("布局比例配置:")
        layout_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        layout.addRow(layout_label)

        # 左侧比例
        self.left_ratio_slider = QSlider(Qt.Orientation.Horizontal)
        self.left_ratio_slider.setRange(10, 50)
        self.left_ratio_slider.setValue(25)
        self.left_ratio_label = QLabel("25%")
        left_layout = QHBoxLayout()
        left_layout.addWidget(self.left_ratio_slider)
        left_layout.addWidget(self.left_ratio_label)
        layout.addRow("左侧区域:", left_layout)

        # 中央比例
        self.center_ratio_slider = QSlider(Qt.Orientation.Horizontal)
        self.center_ratio_slider.setRange(30, 70)
        self.center_ratio_slider.setValue(50)
        self.center_ratio_label = QLabel("50%")
        center_layout = QHBoxLayout()
        center_layout.addWidget(self.center_ratio_slider)
        center_layout.addWidget(self.center_ratio_label)
        layout.addRow("中央区域:", center_layout)

        # 右侧比例
        self.right_ratio_slider = QSlider(Qt.Orientation.Horizontal)
        self.right_ratio_slider.setRange(10, 50)
        self.right_ratio_slider.setValue(25)
        self.right_ratio_label = QLabel("25%")
        right_layout = QHBoxLayout()
        right_layout.addWidget(self.right_ratio_slider)
        right_layout.addWidget(self.right_ratio_label)
        layout.addRow("右侧区域:", right_layout)

        # 底部比例
        self.bottom_ratio_slider = QSlider(Qt.Orientation.Horizontal)
        self.bottom_ratio_slider.setRange(10, 30)
        self.bottom_ratio_slider.setValue(15)
        self.bottom_ratio_label = QLabel("15%")
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.bottom_ratio_slider)
        bottom_layout.addWidget(self.bottom_ratio_label)
        layout.addRow("底部区域:", bottom_layout)

        # 连接滑块信号
        self.left_ratio_slider.valueChanged.connect(lambda v: self.left_ratio_label.setText(f"{v}%"))
        self.center_ratio_slider.valueChanged.connect(lambda v: self.center_ratio_label.setText(f"{v}%"))
        self.right_ratio_slider.valueChanged.connect(lambda v: self.right_ratio_label.setText(f"{v}%"))
        self.bottom_ratio_slider.valueChanged.connect(lambda v: self.bottom_ratio_label.setText(f"{v}%"))

        self.config_tabs.addTab(tab, "📐 布局配置")

    def create_theme_config_tab(self):
        """创建主题配置标签页"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # 主题选择
        self.theme_combo = QComboBox()
        for theme in ThemeStyle:
            self.theme_combo.addItem(theme.value.replace('_', ' ').title(), theme.value)
        layout.addRow("主题样式:", self.theme_combo)

        # 自定义颜色（当选择自定义主题时启用）
        self.primary_color_btn = QPushButton("选择主色调")
        self.primary_color_btn.clicked.connect(self.choose_primary_color)
        layout.addRow("主色调:", self.primary_color_btn)

        self.secondary_color_btn = QPushButton("选择辅助色")
        self.secondary_color_btn.clicked.connect(self.choose_secondary_color)
        layout.addRow("辅助色:", self.secondary_color_btn)

        # 字体设置
        self.font_btn = QPushButton("选择字体")
        self.font_btn.clicked.connect(self.choose_font)
        layout.addRow("界面字体:", self.font_btn)

        self.config_tabs.addTab(tab, "🎨 主题配置")

    def create_action_buttons(self, layout):
        """创建操作按钮"""
        buttons_layout = QHBoxLayout()

        # 保存为新预设
        self.save_as_btn = QPushButton("💾 保存为新预设")
        self.save_as_btn.clicked.connect(self.save_as_preset)
        buttons_layout.addWidget(self.save_as_btn)

        buttons_layout.addStretch()

        # 应用配置
        self.apply_btn = QPushButton("✅ 应用配置")
        self.apply_btn.clicked.connect(self.apply_configuration)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        buttons_layout.addWidget(self.apply_btn)

        # 取消
        self.cancel_btn = QPushButton("❌ 取消")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addLayout(buttons_layout)

    def setup_connections(self):
        """设置信号连接"""
        self.presets_list.currentItemChanged.connect(self.on_preset_selected)
        self.panels_tree.itemDoubleClicked.connect(self.edit_panel_config)

    def load_presets(self):
        """加载预设列表"""
        self.presets_list.clear()

        for name, config in self.preset_manager.get_all_presets().items():
            item = QListWidgetItem()

            # 设置显示文本
            display_text = f"{config.name}"
            if config.is_default:
                display_text += " (默认)"

            item.setText(display_text)
            item.setData(Qt.ItemDataRole.UserRole, name)

            # 设置工具提示
            tooltip = f"描述: {config.description}\n"
            tooltip += f"模式: {config.mode.value}\n"
            tooltip += f"面板数量: {len(config.panels)}\n"
            tooltip += f"标签: {', '.join(config.tags)}"
            item.setToolTip(tooltip)

            self.presets_list.addItem(item)

        # 选择当前配置
        if self.current_config:
            for i in range(self.presets_list.count()):
                item = self.presets_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == self.current_config.name:
                    self.presets_list.setCurrentItem(item)
                    break

    def on_preset_selected(self, current, previous):
        """预设选择改变"""
        if not current:
            return

        preset_name = current.data(Qt.ItemDataRole.UserRole)
        config = self.preset_manager.get_preset(preset_name)

        if config:
            self.load_config_to_ui(config)

    def load_config_to_ui(self, config: WorkspaceConfig):
        """加载配置到UI"""
        try:
            # 基本信息
            self.name_edit.setText(config.name)
            self.description_edit.setPlainText(config.description)

            # 设置模式
            for i in range(self.mode_combo.count()):
                if self.mode_combo.itemData(i) == config.mode.value:
                    self.mode_combo.setCurrentIndex(i)
                    break

            # 标签
            self.tags_edit.setText(", ".join(config.tags))

            # 面板配置
            self.load_panels_to_tree(config.panels)

            # 布局比例
            ratios = config.layout_ratios
            self.left_ratio_slider.setValue(int(ratios.get("left", 0.25) * 100))
            self.center_ratio_slider.setValue(int(ratios.get("center", 0.50) * 100))
            self.right_ratio_slider.setValue(int(ratios.get("right", 0.25) * 100))
            self.bottom_ratio_slider.setValue(int(ratios.get("bottom", 0.15) * 100))

            # 主题
            for i in range(self.theme_combo.count()):
                if self.theme_combo.itemData(i) == config.theme.value:
                    self.theme_combo.setCurrentIndex(i)
                    break

        except Exception as e:
            logger.error(f"加载配置到UI失败: {e}")

    def load_panels_to_tree(self, panels: Dict[str, PanelConfig]):
        """加载面板配置到树"""
        self.panels_tree.clear()

        for name, panel in panels.items():
            item = QTreeWidgetItem()
            item.setText(0, panel.panel_type.value.replace('_', ' ').title())
            item.setText(1, panel.position.value.title())
            item.setText(2, "是" if panel.visible else "否")
            item.setText(3, f"{panel.width}x{panel.height}")

            item.setData(0, Qt.ItemDataRole.UserRole, name)
            item.setCheckState(2, Qt.CheckState.Checked if panel.visible else Qt.CheckState.Unchecked)

            self.panels_tree.addTopLevelItem(item)

    def add_panel_config(self):
        """添加面板配置"""
        # 这里可以实现添加面板的对话框
        pass

    def edit_panel_config(self):
        """编辑面板配置"""
        # 这里可以实现编辑面板的对话框
        pass

    def remove_panel_config(self):
        """移除面板配置"""
        current_item = self.panels_tree.currentItem()
        if current_item:
            self.panels_tree.takeTopLevelItem(self.panels_tree.indexOfTopLevelItem(current_item))

    def choose_primary_color(self):
        """选择主色调"""
        color = QColorDialog.getColor(QColor("#2c5aa0"), self, "选择主色调")
        if color.isValid():
            self.primary_color_btn.setStyleSheet(f"background-color: {color.name()};")

    def choose_secondary_color(self):
        """选择辅助色"""
        color = QColorDialog.getColor(QColor("#4caf50"), self, "选择辅助色")
        if color.isValid():
            self.secondary_color_btn.setStyleSheet(f"background-color: {color.name()};")

    def choose_font(self):
        """选择字体"""
        font, ok = QFontDialog.getFont(QFont("Microsoft YaHei", 9), self, "选择界面字体")
        if ok:
            self.font_btn.setText(f"{font.family()} {font.pointSize()}pt")

    def preview_configuration(self):
        """预览配置"""
        try:
            config = self.build_config_from_ui()
            if config:
                self.preview_config = config
                QMessageBox.information(self, "预览", f"配置预览已准备就绪\n\n{config.description}")
        except Exception as e:
            logger.error(f"预览配置失败: {e}")
            QMessageBox.warning(self, "错误", f"预览配置失败: {str(e)}")

    def reset_configuration(self):
        """重置配置"""
        current_item = self.presets_list.currentItem()
        if current_item:
            preset_name = current_item.data(Qt.ItemDataRole.UserRole)
            config = self.preset_manager.get_preset(preset_name)
            if config:
                self.load_config_to_ui(config)

    def save_as_preset(self):
        """保存为新预设"""
        try:
            config = self.build_config_from_ui()
            if config:
                self.preset_manager.add_custom_preset(config)
                self.load_presets()
                QMessageBox.information(self, "成功", f"工作空间预设 '{config.name}' 已保存")
        except Exception as e:
            logger.error(f"保存预设失败: {e}")
            QMessageBox.warning(self, "错误", f"保存预设失败: {str(e)}")

    def apply_configuration(self):
        """应用配置"""
        try:
            config = self.build_config_from_ui()
            if config:
                self.workspace_applied.emit(config.name)
                self.accept()
        except Exception as e:
            logger.error(f"应用配置失败: {e}")
            QMessageBox.warning(self, "错误", f"应用配置失败: {str(e)}")

    def build_config_from_ui(self) -> Optional[WorkspaceConfig]:
        """从UI构建配置"""
        try:
            name = self.name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "警告", "请输入工作空间名称")
                return None

            description = self.description_edit.toPlainText().strip()
            mode = WorkspaceMode(self.mode_combo.currentData())
            tags = [tag.strip() for tag in self.tags_edit.text().split(",") if tag.strip()]

            # 构建面板配置
            panels = {}
            for i in range(self.panels_tree.topLevelItemCount()):
                item = self.panels_tree.topLevelItem(i)
                panel_name = item.data(0, Qt.ItemDataRole.UserRole)
                if panel_name:
                    # 这里需要从UI获取完整的面板配置
                    # 简化实现，使用默认值
                    panels[panel_name] = PanelConfig(
                        panel_type=PanelType.AI_GENERATOR,  # 需要从UI获取
                        position=PanelPosition.CENTER,      # 需要从UI获取
                        visible=item.checkState(2) == Qt.CheckState.Checked
                    )

            # 布局比例
            layout_ratios = {
                "left": self.left_ratio_slider.value() / 100.0,
                "center": self.center_ratio_slider.value() / 100.0,
                "right": self.right_ratio_slider.value() / 100.0,
                "bottom": self.bottom_ratio_slider.value() / 100.0
            }

            # 主题
            theme = ThemeStyle(self.theme_combo.currentData())

            config = WorkspaceConfig(
                name=name,
                description=description,
                mode=mode,
                panels=panels,
                layout_ratios=layout_ratios,
                theme=theme,
                tags=tags
            )

            return config

        except Exception as e:
            logger.error(f"从UI构建配置失败: {e}")
            return None

    def import_preset(self):
        """导入预设"""
        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入工作空间预设", "", "JSON文件 (*.json)"
        )

        if file_path:
            if self.preset_manager.import_preset(file_path):
                self.load_presets()
                QMessageBox.information(self, "成功", "工作空间预设导入成功")
            else:
                QMessageBox.warning(self, "错误", "工作空间预设导入失败")

    def export_preset(self):
        """导出预设"""
        current_item = self.presets_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要导出的预设")
            return

        from PyQt6.QtWidgets import QFileDialog

        preset_name = current_item.data(Qt.ItemDataRole.UserRole)
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出工作空间预设", f"{preset_name}.json", "JSON文件 (*.json)"
        )

        if file_path:
            if self.preset_manager.export_preset(preset_name, file_path):
                QMessageBox.information(self, "成功", "工作空间预设导出成功")
            else:
                QMessageBox.warning(self, "错误", "工作空间预设导出失败")

    def delete_preset(self):
        """删除预设"""
        current_item = self.presets_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的预设")
            return

        preset_name = current_item.data(Qt.ItemDataRole.UserRole)
        config = self.preset_manager.get_preset(preset_name)

        if config and config.is_default:
            QMessageBox.warning(self, "警告", "无法删除默认预设")
            return

        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除工作空间预设 '{config.name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.preset_manager.remove_preset(preset_name):
                self.load_presets()
                QMessageBox.information(self, "成功", "工作空间预设删除成功")
            else:
                QMessageBox.warning(self, "错误", "工作空间预设删除失败")


class WorkspaceManager(QObject):
    """工作空间管理器"""

    workspace_changed = pyqtSignal(str)  # 工作空间改变信号
    layout_updated = pyqtSignal()        # 布局更新信号

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.preset_manager = WorkspacePresetManager()
        self.current_config = None
        self.panel_widgets = {}
        self.layout_animations = []

        # 初始化默认工作空间
        self.apply_workspace("beginner")

        logger.info("工作空间管理器初始化完成")

    def show_customization_dialog(self):
        """显示定制对话框"""
        try:
            dialog = WorkspaceCustomizationDialog(
                self.preset_manager,
                self.current_config,
                self.main_window
            )
            dialog.workspace_applied.connect(self.apply_workspace)
            dialog.exec()

        except Exception as e:
            logger.error(f"显示定制对话框失败: {e}")

    def apply_workspace(self, workspace_name: str):
        """应用工作空间"""
        try:
            config = self.preset_manager.get_preset(workspace_name)
            if not config:
                logger.warning(f"未找到工作空间配置: {workspace_name}")
                return False

            # 保存当前配置
            self.current_config = config

            # 应用面板配置
            self.apply_panel_configuration(config.panels)

            # 应用布局配置
            self.apply_layout_configuration(config.layout_ratios)

            # 应用主题配置
            self.apply_theme_configuration(config.theme)

            # 发送信号
            self.workspace_changed.emit(workspace_name)
            self.layout_updated.emit()

            logger.info(f"工作空间已应用: {config.name}")
            return True

        except Exception as e:
            logger.error(f"应用工作空间失败: {e}")
            return False

    def apply_panel_configuration(self, panels: Dict[str, PanelConfig]):
        """应用面板配置"""
        try:
            # 获取主窗口的面板
            main_panels = self.get_main_window_panels()

            for panel_name, panel_config in panels.items():
                if panel_name in main_panels:
                    panel_widget = main_panels[panel_name]

                    # 设置可见性
                    panel_widget.setVisible(panel_config.visible)

                    # 设置尺寸
                    if panel_config.resizable:
                        panel_widget.resize(panel_config.width, panel_config.height)

                    # 设置位置（如果是浮动面板）
                    if panel_config.position == PanelPosition.FLOATING:
                        if hasattr(panel_widget, 'setFloating'):
                            panel_widget.setFloating(True)

                    # 设置折叠状态
                    if hasattr(panel_widget, 'setCollapsed') and panel_config.collapsible:
                        panel_widget.setCollapsed(False)

            logger.debug("面板配置已应用")

        except Exception as e:
            logger.error(f"应用面板配置失败: {e}")

    def apply_layout_configuration(self, layout_ratios: Dict[str, float]):
        """应用布局配置"""
        try:
            if hasattr(self.main_window, 'main_splitter'):
                splitter = self.main_window.main_splitter

                # 计算分割器尺寸
                total_width = splitter.width()
                sizes = []

                for area in ['left', 'center', 'right']:
                    ratio = layout_ratios.get(area, 0.33)
                    size = int(total_width * ratio)
                    sizes.append(size)

                # 应用分割器尺寸
                splitter.setSizes(sizes)

            # 应用垂直分割器配置
            if hasattr(self.main_window, 'vertical_splitter'):
                v_splitter = self.main_window.vertical_splitter
                total_height = v_splitter.height()

                main_ratio = 1.0 - layout_ratios.get('bottom', 0.15)
                bottom_ratio = layout_ratios.get('bottom', 0.15)

                v_sizes = [
                    int(total_height * main_ratio),
                    int(total_height * bottom_ratio)
                ]

                v_splitter.setSizes(v_sizes)

            logger.debug("布局配置已应用")

        except Exception as e:
            logger.error(f"应用布局配置失败: {e}")

    def apply_theme_configuration(self, theme: ThemeStyle):
        """应用主题配置"""
        try:
            if theme == ThemeStyle.LIGHT:
                self.apply_light_theme()
            elif theme == ThemeStyle.DARK:
                self.apply_dark_theme()
            elif theme == ThemeStyle.AUTO:
                self.apply_auto_theme()

            logger.debug(f"主题配置已应用: {theme.value}")

        except Exception as e:
            logger.error(f"应用主题配置失败: {e}")

    def apply_light_theme(self):
        """应用浅色主题"""
        light_style = """
        QMainWindow {
            background-color: #f5f5f5;
            color: #333333;
        }
        QWidget {
            background-color: #ffffff;
            color: #333333;
        }
        QFrame {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
        }
        QPushButton {
            background-color: #2196f3;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #1976d2;
        }
        QTabWidget::pane {
            border: 1px solid #e0e0e0;
            background-color: #ffffff;
        }
        QTabBar::tab {
            background-color: #f0f0f0;
            color: #333333;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #2196f3;
            color: white;
        }
        """

        self.main_window.setStyleSheet(light_style)

    def apply_dark_theme(self):
        """应用深色主题"""
        dark_style = """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QWidget {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QFrame {
            background-color: #3c3c3c;
            border: 1px solid #555555;
        }
        QPushButton {
            background-color: #4caf50;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #3c3c3c;
        }
        QTabBar::tab {
            background-color: #2b2b2b;
            color: #ffffff;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #4caf50;
            color: white;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #4a4a4a;
            color: #ffffff;
            border: 1px solid #666666;
            padding: 4px;
        }
        """

        self.main_window.setStyleSheet(dark_style)

    def apply_auto_theme(self):
        """应用自动主题"""
        # 根据系统时间或系统主题设置
        import datetime
        current_hour = datetime.datetime.now().hour

        if 6 <= current_hour <= 18:
            self.apply_light_theme()
        else:
            self.apply_dark_theme()

    def get_main_window_panels(self) -> Dict[str, QWidget]:
        """获取主窗口面板"""
        panels = {}

        try:
            # 音频控制面板
            if hasattr(self.main_window, 'audio_control_widget'):
                panels['audio_control'] = self.main_window.audio_control_widget

            # 时间段标记面板
            if hasattr(self.main_window, 'time_segment_widget'):
                panels['time_segment'] = self.main_window.time_segment_widget

            # AI生成器面板
            if hasattr(self.main_window, 'ai_generator_widget'):
                panels['ai_generator'] = self.main_window.ai_generator_widget

            # 舞台编辑器面板
            if hasattr(self.main_window, 'stage_editor_widget'):
                panels['stage_editor'] = self.main_window.stage_editor_widget

            # 元素管理器面板
            if hasattr(self.main_window, 'elements_manager_widget'):
                panels['elements_manager'] = self.main_window.elements_manager_widget

            # 属性面板
            if hasattr(self.main_window, 'properties_panel_widget'):
                panels['properties_panel'] = self.main_window.properties_panel_widget

            # 时间轴面板
            if hasattr(self.main_window, 'timeline_widget'):
                panels['timeline'] = self.main_window.timeline_widget

            # 预览面板
            if hasattr(self.main_window, 'preview_widget'):
                panels['preview'] = self.main_window.preview_widget

            # 库管理面板
            if hasattr(self.main_window, 'library_manager_widget'):
                panels['library_manager'] = self.main_window.library_manager_widget

            # 规则管理面板
            if hasattr(self.main_window, 'rules_manager_widget'):
                panels['rules_manager'] = self.main_window.rules_manager_widget

        except Exception as e:
            logger.error(f"获取主窗口面板失败: {e}")

        return panels

    def get_current_config(self) -> Optional[WorkspaceConfig]:
        """获取当前配置"""
        return self.current_config

    def save_current_workspace(self, name: str, description: str = ""):
        """保存当前工作空间"""
        try:
            if not self.current_config:
                return False

            # 创建新配置
            new_config = WorkspaceConfig(
                name=name,
                description=description or f"基于 {self.current_config.name} 的自定义工作空间",
                mode=WorkspaceMode.CUSTOM,
                panels=self.current_config.panels.copy(),
                layout_ratios=self.current_config.layout_ratios.copy(),
                theme=self.current_config.theme,
                tags=["自定义", "用户创建"]
            )

            self.preset_manager.add_custom_preset(new_config)
            logger.info(f"当前工作空间已保存为: {name}")
            return True

        except Exception as e:
            logger.error(f"保存当前工作空间失败: {e}")
            return False

    def reset_to_default(self):
        """重置为默认工作空间"""
        self.apply_workspace("beginner")

    def get_workspace_list(self) -> List[Tuple[str, str]]:
        """获取工作空间列表"""
        workspaces = []
        for name, config in self.preset_manager.get_all_presets().items():
            workspaces.append((name, config.name))
        return workspaces

    def export_current_workspace(self, file_path: str) -> bool:
        """导出当前工作空间"""
        if self.current_config:
            return self.preset_manager.export_preset(self.current_config.name, file_path)
        return False

    def import_workspace(self, file_path: str) -> bool:
        """导入工作空间"""
        return self.preset_manager.import_preset(file_path)
