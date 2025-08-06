"""
AI Animation Studio - 色彩方案管理器
严格按照界面设计完整方案实现色彩系统
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

from core.logger import get_logger

logger = get_logger("color_scheme_manager")


class ColorRole(Enum):
    """色彩角色枚举"""
    # 主色调系统
    PRIMARY = "primary"              # 主色 #2C5AA0 专业蓝
    SECONDARY = "secondary"          # 辅助色 #4A90E2 亮蓝
    ACCENT = "accent"               # 强调色 #FF6B35 活力橙
    COLLABORATION = "collaboration"  # 协作色 #10B981 绿色
    WARNING = "warning"             # 警告色 #F59E0B 黄色
    ERROR = "error"                 # 错误色 #EF4444 红色
    
    # 功能色彩编码
    AI_FUNCTION = "ai_function"     # AI功能橙色系
    COLLAB_FUNCTION = "collab_function"  # 协作功能绿色系
    TEST_DEBUG = "test_debug"       # 测试调试紫色系
    PERFORMANCE = "performance"     # 性能监控蓝色系
    
    # 界面基础色
    BACKGROUND = "background"       # 背景色
    SURFACE = "surface"            # 表面色
    TEXT_PRIMARY = "text_primary"   # 主要文字
    TEXT_SECONDARY = "text_secondary"  # 次要文字
    BORDER = "border"              # 边框色
    DIVIDER = "divider"            # 分割线色


@dataclass
class ColorPalette:
    """色彩调色板"""
    name: str
    colors: Dict[ColorRole, str]
    description: str = ""
    
    def get_color(self, role: ColorRole) -> QColor:
        """获取指定角色的颜色"""
        hex_color = self.colors.get(role, "#000000")
        return QColor(hex_color)
    
    def get_color_variants(self, role: ColorRole, count: int = 3) -> List[QColor]:
        """获取颜色变体（深浅不同的同色系）"""
        base_color = self.get_color(role)
        variants = []
        
        for i in range(count):
            factor = 0.7 + (i * 0.3 / (count - 1))  # 从70%到100%亮度
            variant = QColor(base_color)
            variant = variant.lighter(int(factor * 100))
            variants.append(variant)
            
        return variants


class ColorSchemeManager(QObject):
    """色彩方案管理器 - 严格按照界面设计完整方案实现 (增强版)"""

    # 信号定义
    color_scheme_changed = pyqtSignal(str)  # 色彩方案改变信号
    theme_changed = pyqtSignal(str)  # 主题改变信号
    accessibility_mode_changed = pyqtSignal(bool)  # 无障碍模式改变信号
    
    def __init__(self):
        super().__init__()
        self.current_scheme = "professional"
        self.color_palettes = self._initialize_color_palettes()
        logger.info("色彩方案管理器初始化完成")
    
    def _initialize_color_palettes(self) -> Dict[str, ColorPalette]:
        """初始化色彩调色板 - 严格按照设计方案"""
        palettes = {}
        
        # 专业色彩方案（默认）- 严格按照设计方案
        professional_colors = {
            # 主色调系统
            ColorRole.PRIMARY: "#2C5AA0",        # 专业蓝
            ColorRole.SECONDARY: "#4A90E2",      # 亮蓝
            ColorRole.ACCENT: "#FF6B35",         # 活力橙
            ColorRole.COLLABORATION: "#10B981",   # 协作绿
            ColorRole.WARNING: "#F59E0B",        # 警告黄
            ColorRole.ERROR: "#EF4444",          # 错误红
            
            # 功能色彩编码
            ColorRole.AI_FUNCTION: "#FF6B35",    # AI功能橙色系
            ColorRole.COLLAB_FUNCTION: "#10B981", # 协作功能绿色系
            ColorRole.TEST_DEBUG: "#8B5CF6",     # 测试调试紫色系
            ColorRole.PERFORMANCE: "#3B82F6",    # 性能监控蓝色系
            
            # 界面基础色
            ColorRole.BACKGROUND: "#F8FAFC",     # 背景色
            ColorRole.SURFACE: "#FFFFFF",        # 表面色
            ColorRole.TEXT_PRIMARY: "#1F2937",   # 主要文字
            ColorRole.TEXT_SECONDARY: "#6B7280", # 次要文字
            ColorRole.BORDER: "#E5E7EB",         # 边框色
            ColorRole.DIVIDER: "#F3F4F6",        # 分割线色
        }
        
        palettes["professional"] = ColorPalette(
            name="专业色彩方案",
            colors=professional_colors,
            description="严格按照界面设计完整方案的专业色彩系统"
        )
        
        # 深色主题（可选）
        dark_colors = {
            ColorRole.PRIMARY: "#4A90E2",
            ColorRole.SECONDARY: "#60A5FA",
            ColorRole.ACCENT: "#FB923C",
            ColorRole.COLLABORATION: "#34D399",
            ColorRole.WARNING: "#FBBF24",
            ColorRole.ERROR: "#F87171",
            
            ColorRole.AI_FUNCTION: "#FB923C",
            ColorRole.COLLAB_FUNCTION: "#34D399",
            ColorRole.TEST_DEBUG: "#A78BFA",
            ColorRole.PERFORMANCE: "#60A5FA",
            
            ColorRole.BACKGROUND: "#1F2937",
            ColorRole.SURFACE: "#374151",
            ColorRole.TEXT_PRIMARY: "#F9FAFB",
            ColorRole.TEXT_SECONDARY: "#D1D5DB",
            ColorRole.BORDER: "#4B5563",
            ColorRole.DIVIDER: "#374151",
        }
        
        palettes["dark"] = ColorPalette(
            name="深色主题",
            colors=dark_colors,
            description="深色主题色彩方案"
        )
        
        return palettes
    
    def get_current_palette(self) -> ColorPalette:
        """获取当前色彩调色板"""
        return self.color_palettes[self.current_scheme]
    
    def get_color(self, role: ColorRole) -> QColor:
        """获取指定角色的颜色"""
        return self.get_current_palette().get_color(role)
    
    def get_color_hex(self, role: ColorRole) -> str:
        """获取指定角色的十六进制颜色值"""
        return self.get_current_palette().colors.get(role, "#000000")
    
    def get_ai_function_colors(self) -> List[str]:
        """获取AI功能橙色系 - 严格按照设计方案"""
        return ["#FF6B35", "#FB923C", "#FDBA74"]
    
    def get_collaboration_colors(self) -> List[str]:
        """获取协作功能绿色系 - 严格按照设计方案"""
        return ["#10B981", "#34D399", "#6EE7B7"]
    
    def get_test_debug_colors(self) -> List[str]:
        """获取测试调试紫色系 - 严格按照设计方案"""
        return ["#8B5CF6", "#A78BFA", "#C4B5FD"]
    
    def get_performance_colors(self) -> List[str]:
        """获取性能监控蓝色系 - 严格按照设计方案"""
        return ["#3B82F6", "#60A5FA", "#93C5FD"]
    
    def set_color_scheme(self, scheme_name: str):
        """设置色彩方案"""
        if scheme_name in self.color_palettes:
            self.current_scheme = scheme_name
            self.color_scheme_changed.emit(scheme_name)
            logger.info(f"色彩方案已切换到: {scheme_name}")
        else:
            logger.warning(f"未知的色彩方案: {scheme_name}")
    
    def get_available_schemes(self) -> List[str]:
        """获取可用的色彩方案列表"""
        return list(self.color_palettes.keys())
    
    def generate_stylesheet_for_widget(self, widget_type: str) -> str:
        """为指定组件类型生成样式表"""
        palette = self.get_current_palette()
        
        if widget_type == "toolbar":
            return self._generate_toolbar_stylesheet(palette)
        elif widget_type == "ai_panel":
            return self._generate_ai_panel_stylesheet(palette)
        elif widget_type == "collaboration_panel":
            return self._generate_collaboration_panel_stylesheet(palette)
        elif widget_type == "test_panel":
            return self._generate_test_panel_stylesheet(palette)
        elif widget_type == "performance_panel":
            return self._generate_performance_panel_stylesheet(palette)
        else:
            return self._generate_default_stylesheet(palette)
    
    def _generate_toolbar_stylesheet(self, palette: ColorPalette) -> str:
        """生成工具栏样式表"""
        return f"""
        QToolBar {{
            background-color: {palette.colors[ColorRole.PRIMARY]};
            border: none;
            color: white;
        }}
        QToolButton {{
            background-color: transparent;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
        }}
        QToolButton:hover {{
            background-color: {palette.colors[ColorRole.SECONDARY]};
        }}
        QToolButton:pressed {{
            background-color: {palette.colors[ColorRole.ACCENT]};
        }}
        """
    
    def _generate_ai_panel_stylesheet(self, palette: ColorPalette) -> str:
        """生成AI面板样式表"""
        ai_colors = self.get_ai_function_colors()
        return f"""
        QFrame {{
            background-color: {palette.colors[ColorRole.SURFACE]};
            border: 1px solid {ai_colors[0]};
            border-radius: 6px;
        }}
        QPushButton {{
            background-color: {ai_colors[0]};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {ai_colors[1]};
        }}
        """
    
    def _generate_collaboration_panel_stylesheet(self, palette: ColorPalette) -> str:
        """生成协作面板样式表"""
        collab_colors = self.get_collaboration_colors()
        return f"""
        QFrame {{
            background-color: {palette.colors[ColorRole.SURFACE]};
            border: 1px solid {collab_colors[0]};
            border-radius: 6px;
        }}
        QPushButton {{
            background-color: {collab_colors[0]};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {collab_colors[1]};
        }}
        """
    
    def _generate_test_panel_stylesheet(self, palette: ColorPalette) -> str:
        """生成测试面板样式表"""
        test_colors = self.get_test_debug_colors()
        return f"""
        QFrame {{
            background-color: {palette.colors[ColorRole.SURFACE]};
            border: 1px solid {test_colors[0]};
            border-radius: 6px;
        }}
        QPushButton {{
            background-color: {test_colors[0]};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {test_colors[1]};
        }}
        """
    
    def _generate_performance_panel_stylesheet(self, palette: ColorPalette) -> str:
        """生成性能面板样式表"""
        perf_colors = self.get_performance_colors()
        return f"""
        QFrame {{
            background-color: {palette.colors[ColorRole.SURFACE]};
            border: 1px solid {perf_colors[0]};
            border-radius: 6px;
        }}
        QPushButton {{
            background-color: {perf_colors[0]};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {perf_colors[1]};
        }}
        """
    
    def _generate_default_stylesheet(self, palette: ColorPalette) -> str:
        """生成默认样式表"""
        return f"""
        QWidget {{
            background-color: {palette.colors[ColorRole.BACKGROUND]};
            color: {palette.colors[ColorRole.TEXT_PRIMARY]};
        }}
        QFrame {{
            background-color: {palette.colors[ColorRole.SURFACE]};
            border: 1px solid {palette.colors[ColorRole.BORDER]};
        }}
        """


# 全局色彩方案管理器实例
color_scheme_manager = ColorSchemeManager()
