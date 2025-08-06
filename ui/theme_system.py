"""
AI Animation Studio - 现代化主题系统
实现完整的色彩方案、字体系统和视觉设计规范
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette, QIcon
from PyQt6.QtWidgets import QApplication

from core.logger import get_logger

logger = get_logger("theme_system")


class ThemeType(Enum):
    """主题类型"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # 跟随系统


class ColorRole(Enum):
    """颜色角色"""
    # 主色调
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ACCENT = "accent"

    # 功能色彩
    AI_FUNCTION = "ai_function"
    COLLABORATION = "collaboration"
    DEBUG_TEST = "debug_test"
    PERFORMANCE = "performance"

    # 功能色彩系列 - 按照设计方案扩展
    AI_FUNCTION_LIGHT = "ai_function_light"
    AI_FUNCTION_LIGHTER = "ai_function_lighter"
    COLLABORATION_LIGHT = "collaboration_light"
    COLLABORATION_LIGHTER = "collaboration_lighter"
    DEBUG_TEST_LIGHT = "debug_test_light"
    DEBUG_TEST_LIGHTER = "debug_test_lighter"
    PERFORMANCE_LIGHT = "performance_light"
    PERFORMANCE_LIGHTER = "performance_lighter"

    # 状态色彩
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"

    # 界面色彩
    BACKGROUND = "background"
    SURFACE = "surface"
    ON_BACKGROUND = "on_background"
    ON_SURFACE = "on_surface"

    # 边框和分割线
    BORDER = "border"
    DIVIDER = "divider"

    # 文本色彩
    TEXT_PRIMARY = "text_primary"
    TEXT_SECONDARY = "text_secondary"
    TEXT_DISABLED = "text_disabled"


@dataclass
class ColorScheme:
    """色彩方案"""
    colors: Dict[ColorRole, str]
    
    def get_color(self, role: ColorRole) -> str:
        """获取颜色"""
        return self.colors.get(role, "#000000")
    
    def get_qcolor(self, role: ColorRole) -> QColor:
        """获取QColor对象"""
        return QColor(self.get_color(role))


@dataclass
class Typography:
    """字体系统"""
    # 字体族
    primary_font: str = "Microsoft YaHei"
    monospace_font: str = "Consolas"
    
    # 字体大小
    h1_size: int = 24
    h2_size: int = 20
    h3_size: int = 16
    h4_size: int = 14
    body_size: int = 12
    caption_size: int = 10
    
    # 字重
    light_weight: int = 300
    regular_weight: int = 400
    medium_weight: int = 500
    bold_weight: int = 700
    
    def get_font(self, size: int, weight: int = None, family: str = None) -> QFont:
        """获取字体对象"""
        font_family = family or self.primary_font
        font_weight = weight or self.regular_weight
        
        font = QFont(font_family, size)
        font.setWeight(font_weight)
        return font


@dataclass
class Spacing:
    """间距系统"""
    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48


@dataclass
class BorderRadius:
    """圆角系统"""
    none: int = 0
    sm: int = 4
    md: int = 8
    lg: int = 12
    xl: int = 16
    full: int = 9999


class ModernTheme:
    """现代化主题"""
    
    def __init__(self, theme_type: ThemeType):
        self.theme_type = theme_type
        self.color_scheme = self._create_color_scheme()
        self.typography = Typography()
        self.spacing = Spacing()
        self.border_radius = BorderRadius()
    
    def _create_color_scheme(self) -> ColorScheme:
        """创建色彩方案"""
        if self.theme_type == ThemeType.LIGHT:
            return self._create_light_scheme()
        elif self.theme_type == ThemeType.DARK:
            return self._create_dark_scheme()
        else:
            # AUTO模式，根据系统设置决定
            return self._create_light_scheme()  # 默认浅色
    
    def _create_light_scheme(self) -> ColorScheme:
        """创建浅色主题方案"""
        colors = {
            # 主色调系统
            ColorRole.PRIMARY: "#2C5AA0",
            ColorRole.SECONDARY: "#4A90E2",
            ColorRole.ACCENT: "#FF6B35",
            
            # 功能色彩编码
            ColorRole.AI_FUNCTION: "#FF6B35",
            ColorRole.COLLABORATION: "#10B981",
            ColorRole.DEBUG_TEST: "#8B5CF6",
            ColorRole.PERFORMANCE: "#3B82F6",

            # 功能色彩系列 - 按照设计方案的色彩系统
            ColorRole.AI_FUNCTION_LIGHT: "#FB923C",
            ColorRole.AI_FUNCTION_LIGHTER: "#FDBA74",
            ColorRole.COLLABORATION_LIGHT: "#34D399",
            ColorRole.COLLABORATION_LIGHTER: "#6EE7B7",
            ColorRole.DEBUG_TEST_LIGHT: "#A78BFA",
            ColorRole.DEBUG_TEST_LIGHTER: "#C4B5FD",
            ColorRole.PERFORMANCE_LIGHT: "#60A5FA",
            ColorRole.PERFORMANCE_LIGHTER: "#93C5FD",
            
            # 状态色彩
            ColorRole.SUCCESS: "#10B981",
            ColorRole.WARNING: "#F59E0B",
            ColorRole.ERROR: "#EF4444",
            ColorRole.INFO: "#3B82F6",
            
            # 界面色彩
            ColorRole.BACKGROUND: "#FFFFFF",
            ColorRole.SURFACE: "#F8FAFC",
            ColorRole.ON_BACKGROUND: "#1E293B",
            ColorRole.ON_SURFACE: "#334155",
            
            # 边框和分割线
            ColorRole.BORDER: "#E2E8F0",
            ColorRole.DIVIDER: "#CBD5E1",
            
            # 文本色彩
            ColorRole.TEXT_PRIMARY: "#1E293B",
            ColorRole.TEXT_SECONDARY: "#64748B",
            ColorRole.TEXT_DISABLED: "#94A3B8",
        }
        
        return ColorScheme(colors)
    
    def _create_dark_scheme(self) -> ColorScheme:
        """创建深色主题方案"""
        colors = {
            # 主色调系统
            ColorRole.PRIMARY: "#4A90E2",
            ColorRole.SECONDARY: "#60A5FA",
            ColorRole.ACCENT: "#FB923C",
            
            # 功能色彩编码
            ColorRole.AI_FUNCTION: "#FB923C",
            ColorRole.COLLABORATION: "#34D399",
            ColorRole.DEBUG_TEST: "#A78BFA",
            ColorRole.PERFORMANCE: "#60A5FA",

            # 功能色彩系列 - 深色主题版本
            ColorRole.AI_FUNCTION_LIGHT: "#FDBA74",
            ColorRole.AI_FUNCTION_LIGHTER: "#FED7AA",
            ColorRole.COLLABORATION_LIGHT: "#6EE7B7",
            ColorRole.COLLABORATION_LIGHTER: "#A7F3D0",
            ColorRole.DEBUG_TEST_LIGHT: "#C4B5FD",
            ColorRole.DEBUG_TEST_LIGHTER: "#DDD6FE",
            ColorRole.PERFORMANCE_LIGHT: "#93C5FD",
            ColorRole.PERFORMANCE_LIGHTER: "#BFDBFE",
            
            # 状态色彩
            ColorRole.SUCCESS: "#34D399",
            ColorRole.WARNING: "#FBBF24",
            ColorRole.ERROR: "#F87171",
            ColorRole.INFO: "#60A5FA",
            
            # 界面色彩
            ColorRole.BACKGROUND: "#0F172A",
            ColorRole.SURFACE: "#1E293B",
            ColorRole.ON_BACKGROUND: "#F1F5F9",
            ColorRole.ON_SURFACE: "#E2E8F0",
            
            # 边框和分割线
            ColorRole.BORDER: "#334155",
            ColorRole.DIVIDER: "#475569",
            
            # 文本色彩
            ColorRole.TEXT_PRIMARY: "#F1F5F9",
            ColorRole.TEXT_SECONDARY: "#CBD5E1",
            ColorRole.TEXT_DISABLED: "#64748B",
        }
        
        return ColorScheme(colors)


class ThemeManager(QObject):
    """主题管理器"""
    
    theme_changed = pyqtSignal(str)  # 主题变更信号
    
    def __init__(self):
        super().__init__()
        self.current_theme_type = ThemeType.LIGHT
        self.current_theme = ModernTheme(self.current_theme_type)
        self.custom_stylesheets = {}
        
        logger.info("主题管理器初始化完成")
    
    def set_theme(self, theme_type: ThemeType):
        """设置主题"""
        try:
            if theme_type != self.current_theme_type:
                self.current_theme_type = theme_type
                self.current_theme = ModernTheme(theme_type)
                
                # 应用主题到应用程序
                self.apply_theme_to_application()
                
                # 发射主题变更信号
                self.theme_changed.emit(theme_type.value)
                
                logger.info(f"主题已切换到: {theme_type.value}")
                
        except Exception as e:
            logger.error(f"设置主题失败: {e}")
    
    def get_current_theme(self) -> ModernTheme:
        """获取当前主题"""
        return self.current_theme
    
    def get_color(self, role: ColorRole) -> str:
        """获取颜色"""
        return self.current_theme.color_scheme.get_color(role)
    
    def get_qcolor(self, role: ColorRole) -> QColor:
        """获取QColor对象"""
        return self.current_theme.color_scheme.get_qcolor(role)
    
    def get_font(self, size: int, weight: int = None, family: str = None) -> QFont:
        """获取字体"""
        return self.current_theme.typography.get_font(size, weight, family)
    
    def apply_theme_to_application(self):
        """应用主题到应用程序"""
        try:
            app = QApplication.instance()
            if not app:
                return
            
            # 创建调色板
            palette = self.create_palette()
            app.setPalette(palette)
            
            # 应用全局样式表
            stylesheet = self.generate_global_stylesheet()
            app.setStyleSheet(stylesheet)
            
            logger.info("主题已应用到应用程序")
            
        except Exception as e:
            logger.error(f"应用主题失败: {e}")
    
    def create_palette(self) -> QPalette:
        """创建调色板"""
        palette = QPalette()
        
        # 设置基础颜色
        palette.setColor(QPalette.ColorRole.Window, self.get_qcolor(ColorRole.BACKGROUND))
        palette.setColor(QPalette.ColorRole.WindowText, self.get_qcolor(ColorRole.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Base, self.get_qcolor(ColorRole.SURFACE))
        palette.setColor(QPalette.ColorRole.AlternateBase, self.get_qcolor(ColorRole.SURFACE))
        palette.setColor(QPalette.ColorRole.Text, self.get_qcolor(ColorRole.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Button, self.get_qcolor(ColorRole.SURFACE))
        palette.setColor(QPalette.ColorRole.ButtonText, self.get_qcolor(ColorRole.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Highlight, self.get_qcolor(ColorRole.PRIMARY))
        palette.setColor(QPalette.ColorRole.HighlightedText, self.get_qcolor(ColorRole.ON_SURFACE))
        
        return palette

    def generate_global_stylesheet(self) -> str:
        """生成全局样式表"""
        theme = self.current_theme

        stylesheet = f"""
        /* AI Animation Studio - 全局样式表 */

        /* 基础样式 */
        QWidget {{
            background-color: {self.get_color(ColorRole.BACKGROUND)};
            color: {self.get_color(ColorRole.TEXT_PRIMARY)};
            font-family: "{theme.typography.primary_font}";
            font-size: {theme.typography.body_size}px;
        }}

        /* 主窗口 */
        QMainWindow {{
            background-color: {self.get_color(ColorRole.BACKGROUND)};
            border: none;
        }}

        /* 工具栏 */
        QToolBar {{
            background-color: {self.get_color(ColorRole.SURFACE)};
            border: 1px solid {self.get_color(ColorRole.BORDER)};
            border-radius: {theme.border_radius.sm}px;
            padding: {theme.spacing.sm}px;
            spacing: {theme.spacing.sm}px;
        }}

        /* 按钮样式 */
        QPushButton {{
            background-color: {self.get_color(ColorRole.SURFACE)};
            color: {self.get_color(ColorRole.TEXT_PRIMARY)};
            border: 1px solid {self.get_color(ColorRole.BORDER)};
            border-radius: {theme.border_radius.md}px;
            padding: {theme.spacing.sm}px {theme.spacing.md}px;
            font-weight: {theme.typography.medium_weight};
            min-height: 24px;
        }}

        QPushButton:hover {{
            background-color: {self.get_color(ColorRole.PRIMARY)};
            color: white;
            border-color: {self.get_color(ColorRole.PRIMARY)};
        }}

        QPushButton:pressed {{
            background-color: {self.get_color(ColorRole.SECONDARY)};
        }}

        QPushButton:disabled {{
            background-color: {self.get_color(ColorRole.SURFACE)};
            color: {self.get_color(ColorRole.TEXT_DISABLED)};
            border-color: {self.get_color(ColorRole.BORDER)};
        }}

        /* AI功能按钮 */
        QPushButton[class="ai-button"] {{
            background-color: {self.get_color(ColorRole.AI_FUNCTION)};
            color: white;
            border: none;
            font-weight: {theme.typography.bold_weight};
        }}

        QPushButton[class="ai-button"]:hover {{
            background-color: #FB923C;
        }}

        /* 协作功能按钮 */
        QPushButton[class="collaboration-button"] {{
            background-color: {self.get_color(ColorRole.COLLABORATION)};
            color: white;
            border: none;
        }}

        /* 输入框样式 */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {self.get_color(ColorRole.SURFACE)};
            color: {self.get_color(ColorRole.TEXT_PRIMARY)};
            border: 1px solid {self.get_color(ColorRole.BORDER)};
            border-radius: {theme.border_radius.md}px;
            padding: {theme.spacing.sm}px;
            selection-background-color: {self.get_color(ColorRole.PRIMARY)};
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {self.get_color(ColorRole.PRIMARY)};
            border-width: 2px;
        }}

        /* 标签样式 */
        QLabel {{
            color: {self.get_color(ColorRole.TEXT_PRIMARY)};
            background: transparent;
        }}

        QLabel[class="title"] {{
            font-size: {theme.typography.h3_size}px;
            font-weight: {theme.typography.bold_weight};
            color: {self.get_color(ColorRole.TEXT_PRIMARY)};
        }}

        QLabel[class="subtitle"] {{
            font-size: {theme.typography.h4_size}px;
            font-weight: {theme.typography.medium_weight};
            color: {self.get_color(ColorRole.TEXT_SECONDARY)};
        }}

        QLabel[class="caption"] {{
            font-size: {theme.typography.caption_size}px;
            color: {self.get_color(ColorRole.TEXT_SECONDARY)};
        }}

        /* 分组框样式 */
        QGroupBox {{
            background-color: {self.get_color(ColorRole.SURFACE)};
            border: 1px solid {self.get_color(ColorRole.BORDER)};
            border-radius: {theme.border_radius.lg}px;
            margin-top: {theme.spacing.md}px;
            padding-top: {theme.spacing.sm}px;
            font-weight: {theme.typography.medium_weight};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {theme.spacing.md}px;
            padding: 0 {theme.spacing.sm}px 0 {theme.spacing.sm}px;
            color: {self.get_color(ColorRole.TEXT_PRIMARY)};
            background-color: {self.get_color(ColorRole.SURFACE)};
        }}

        /* 列表和树形控件 */
        QListWidget, QTreeWidget, QTableWidget {{
            background-color: {self.get_color(ColorRole.SURFACE)};
            border: 1px solid {self.get_color(ColorRole.BORDER)};
            border-radius: {theme.border_radius.md}px;
            alternate-background-color: {self.get_color(ColorRole.BACKGROUND)};
        }}

        QListWidget::item, QTreeWidget::item, QTableWidget::item {{
            padding: {theme.spacing.sm}px;
            border-bottom: 1px solid {self.get_color(ColorRole.DIVIDER)};
        }}

        QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {{
            background-color: {self.get_color(ColorRole.PRIMARY)};
            color: white;
        }}

        QListWidget::item:hover, QTreeWidget::item:hover, QTableWidget::item:hover {{
            background-color: {self.get_color(ColorRole.SURFACE)};
        }}

        /* 滚动条样式 */
        QScrollBar:vertical {{
            background-color: {self.get_color(ColorRole.SURFACE)};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {self.get_color(ColorRole.BORDER)};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {self.get_color(ColorRole.PRIMARY)};
        }}

        QScrollBar:horizontal {{
            background-color: {self.get_color(ColorRole.SURFACE)};
            height: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {self.get_color(ColorRole.BORDER)};
            border-radius: 6px;
            min-width: 20px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {self.get_color(ColorRole.PRIMARY)};
        }}

        /* 选项卡样式 */
        QTabWidget::pane {{
            border: 1px solid {self.get_color(ColorRole.BORDER)};
            border-radius: {theme.border_radius.md}px;
            background-color: {self.get_color(ColorRole.SURFACE)};
        }}

        QTabBar::tab {{
            background-color: {self.get_color(ColorRole.BACKGROUND)};
            color: {self.get_color(ColorRole.TEXT_SECONDARY)};
            border: 1px solid {self.get_color(ColorRole.BORDER)};
            padding: {theme.spacing.sm}px {theme.spacing.md}px;
            margin-right: 2px;
        }}

        QTabBar::tab:selected {{
            background-color: {self.get_color(ColorRole.PRIMARY)};
            color: white;
            border-bottom-color: {self.get_color(ColorRole.PRIMARY)};
        }}

        QTabBar::tab:hover {{
            background-color: {self.get_color(ColorRole.SURFACE)};
        }}

        /* 进度条样式 */
        QProgressBar {{
            background-color: {self.get_color(ColorRole.SURFACE)};
            border: 1px solid {self.get_color(ColorRole.BORDER)};
            border-radius: {theme.border_radius.sm}px;
            text-align: center;
            height: 20px;
        }}

        QProgressBar::chunk {{
            background-color: {self.get_color(ColorRole.PRIMARY)};
            border-radius: {theme.border_radius.sm}px;
        }}

        /* 状态栏样式 */
        QStatusBar {{
            background-color: {self.get_color(ColorRole.SURFACE)};
            border-top: 1px solid {self.get_color(ColorRole.BORDER)};
            color: {self.get_color(ColorRole.TEXT_SECONDARY)};
        }}

        /* 菜单样式 */
        QMenuBar {{
            background-color: {self.get_color(ColorRole.SURFACE)};
            border-bottom: 1px solid {self.get_color(ColorRole.BORDER)};
        }}

        QMenuBar::item {{
            background: transparent;
            padding: {theme.spacing.sm}px {theme.spacing.md}px;
        }}

        QMenuBar::item:selected {{
            background-color: {self.get_color(ColorRole.PRIMARY)};
            color: white;
        }}

        QMenu {{
            background-color: {self.get_color(ColorRole.SURFACE)};
            border: 1px solid {self.get_color(ColorRole.BORDER)};
            border-radius: {theme.border_radius.md}px;
        }}

        QMenu::item {{
            padding: {theme.spacing.sm}px {theme.spacing.md}px;
        }}

        QMenu::item:selected {{
            background-color: {self.get_color(ColorRole.PRIMARY)};
            color: white;
        }}
        """

        return stylesheet

    def get_component_stylesheet(self, component_name: str) -> str:
        """获取组件特定样式表"""
        if component_name in self.custom_stylesheets:
            return self.custom_stylesheets[component_name]
        return ""

    def register_component_stylesheet(self, component_name: str, stylesheet: str):
        """注册组件样式表"""
        self.custom_stylesheets[component_name] = stylesheet
        logger.info(f"注册组件样式表: {component_name}")

    def toggle_theme(self):
        """切换主题"""
        if self.current_theme_type == ThemeType.LIGHT:
            self.set_theme(ThemeType.DARK)
        else:
            self.set_theme(ThemeType.LIGHT)

    def get_available_themes(self) -> Dict[str, str]:
        """获取可用主题列表"""
        return {
            ThemeType.LIGHT.value: "浅色主题",
            ThemeType.DARK.value: "深色主题"
        }

    def apply_theme(self, app, theme_name: str):
        """应用主题到应用程序"""
        try:
            # 根据主题名称设置主题类型
            if theme_name == "dark":
                self.set_theme(ThemeType.DARK)
            else:
                self.set_theme(ThemeType.LIGHT)

            logger.info(f"应用主题: {theme_name}")

        except Exception as e:
            logger.error(f"应用主题失败: {e}")


# 全局主题管理器实例
_theme_manager = None

def get_theme_manager() -> ThemeManager:
    """获取全局主题管理器"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
