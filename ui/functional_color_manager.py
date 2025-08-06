"""
AI Animation Studio - 功能色彩管理器
按照设计方案实现完整的功能色彩编码系统
"""

from enum import Enum
from typing import Dict, List, Tuple
from dataclasses import dataclass
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QObject, pyqtSignal

from ui.theme_system import get_theme_manager, ColorRole
from core.logger import get_logger

logger = get_logger("functional_color_manager")


class FunctionCategory(Enum):
    """功能类别"""
    AI_FUNCTION = "ai_function"
    COLLABORATION = "collaboration"
    DEBUG_TEST = "debug_test"
    PERFORMANCE = "performance"


@dataclass
class ColorPalette:
    """色彩调色板"""
    primary: str
    light: str
    lighter: str
    
    def get_colors(self) -> List[str]:
        """获取所有颜色"""
        return [self.primary, self.light, self.lighter]
    
    def get_qcolors(self) -> List[QColor]:
        """获取QColor对象列表"""
        return [QColor(color) for color in self.get_colors()]


class FunctionalColorManager(QObject):
    """功能色彩管理器"""
    
    color_scheme_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.theme_manager = get_theme_manager()
        self.color_palettes = self._initialize_color_palettes()
        
        # 连接主题变更信号
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        logger.info("功能色彩管理器初始化完成")
    
    def _initialize_color_palettes(self) -> Dict[FunctionCategory, ColorPalette]:
        """初始化色彩调色板"""
        return {
            FunctionCategory.AI_FUNCTION: ColorPalette(
                primary=self.theme_manager.get_color(ColorRole.AI_FUNCTION),
                light=self.theme_manager.get_color(ColorRole.AI_FUNCTION_LIGHT),
                lighter=self.theme_manager.get_color(ColorRole.AI_FUNCTION_LIGHTER)
            ),
            FunctionCategory.COLLABORATION: ColorPalette(
                primary=self.theme_manager.get_color(ColorRole.COLLABORATION),
                light=self.theme_manager.get_color(ColorRole.COLLABORATION_LIGHT),
                lighter=self.theme_manager.get_color(ColorRole.COLLABORATION_LIGHTER)
            ),
            FunctionCategory.DEBUG_TEST: ColorPalette(
                primary=self.theme_manager.get_color(ColorRole.DEBUG_TEST),
                light=self.theme_manager.get_color(ColorRole.DEBUG_TEST_LIGHT),
                lighter=self.theme_manager.get_color(ColorRole.DEBUG_TEST_LIGHTER)
            ),
            FunctionCategory.PERFORMANCE: ColorPalette(
                primary=self.theme_manager.get_color(ColorRole.PERFORMANCE),
                light=self.theme_manager.get_color(ColorRole.PERFORMANCE_LIGHT),
                lighter=self.theme_manager.get_color(ColorRole.PERFORMANCE_LIGHTER)
            )
        }
    
    def get_palette(self, category: FunctionCategory) -> ColorPalette:
        """获取指定功能类别的色彩调色板"""
        return self.color_palettes.get(category, self.color_palettes[FunctionCategory.AI_FUNCTION])
    
    def get_primary_color(self, category: FunctionCategory) -> str:
        """获取主色"""
        return self.get_palette(category).primary
    
    def get_light_color(self, category: FunctionCategory) -> str:
        """获取浅色"""
        return self.get_palette(category).light
    
    def get_lighter_color(self, category: FunctionCategory) -> str:
        """获取更浅色"""
        return self.get_palette(category).lighter
    
    def get_gradient_colors(self, category: FunctionCategory) -> List[str]:
        """获取渐变色彩列表"""
        palette = self.get_palette(category)
        return [palette.primary, palette.light, palette.lighter]
    
    def generate_component_stylesheet(self, category: FunctionCategory, component_type: str = "button") -> str:
        """生成组件样式表"""
        palette = self.get_palette(category)
        
        if component_type == "button":
            return f"""
                QPushButton {{
                    background-color: {palette.primary};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {palette.light};
                }}
                QPushButton:pressed {{
                    background-color: {palette.primary};
                }}
                QPushButton:disabled {{
                    background-color: {palette.lighter};
                    color: #94A3B8;
                }}
            """
        elif component_type == "panel":
            return f"""
                QWidget {{
                    background-color: {palette.lighter};
                    border: 1px solid {palette.light};
                    border-radius: 8px;
                }}
                QWidget::title {{
                    background-color: {palette.primary};
                    color: white;
                    padding: 8px;
                    font-weight: 600;
                }}
            """
        elif component_type == "tab":
            return f"""
                QTabWidget::pane {{
                    border: 1px solid {palette.light};
                    border-radius: 4px;
                }}
                QTabBar::tab {{
                    background-color: {palette.lighter};
                    color: {palette.primary};
                    padding: 8px 16px;
                    margin-right: 2px;
                }}
                QTabBar::tab:selected {{
                    background-color: {palette.primary};
                    color: white;
                }}
                QTabBar::tab:hover {{
                    background-color: {palette.light};
                    color: white;
                }}
            """
        
        return ""
    
    def apply_functional_colors_to_widget(self, widget, category: FunctionCategory, component_type: str = "button"):
        """应用功能色彩到组件"""
        try:
            stylesheet = self.generate_component_stylesheet(category, component_type)
            widget.setStyleSheet(stylesheet)
            logger.debug(f"已应用{category.value}色彩到{component_type}组件")
        except Exception as e:
            logger.error(f"应用功能色彩失败: {e}")
    
    def get_status_color(self, status: str) -> str:
        """获取状态色彩"""
        status_colors = {
            "success": self.theme_manager.get_color(ColorRole.SUCCESS),
            "warning": self.theme_manager.get_color(ColorRole.WARNING),
            "error": self.theme_manager.get_color(ColorRole.ERROR),
            "info": self.theme_manager.get_color(ColorRole.INFO)
        }
        return status_colors.get(status, self.theme_manager.get_color(ColorRole.INFO))
    
    def _on_theme_changed(self):
        """主题变更处理"""
        self.color_palettes = self._initialize_color_palettes()
        self.color_scheme_changed.emit()
        logger.info("功能色彩方案已更新")


# 全局功能色彩管理器实例
_functional_color_manager = None

def get_functional_color_manager() -> FunctionalColorManager:
    """获取功能色彩管理器实例"""
    global _functional_color_manager
    if _functional_color_manager is None:
        _functional_color_manager = FunctionalColorManager()
    return _functional_color_manager
