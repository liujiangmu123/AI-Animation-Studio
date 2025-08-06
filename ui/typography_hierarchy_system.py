"""
AI Animation Studio - 字体层次规范系统
建立功能性字体系统，区分不同类型信息的字体样式
"""

from PyQt6.QtWidgets import QWidget, QApplication, QLabel, QPushButton, QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QFontMetrics, QColor, QFontDatabase

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import json
from dataclasses import dataclass
import platform

from core.logger import get_logger

logger = get_logger("typography_hierarchy_system")


class FontCategory(Enum):
    """字体分类枚举"""
    INTERFACE = "interface"     # 界面字体
    DATA = "data"              # 数据字体
    TITLE = "title"            # 标题字体
    CAPTION = "caption"        # 说明字体
    CODE = "code"              # 代码字体
    DISPLAY = "display"        # 展示字体


class FontWeight(Enum):
    """字体重量枚举"""
    THIN = 100
    EXTRA_LIGHT = 200
    LIGHT = 300
    REGULAR = 400
    MEDIUM = 500
    SEMI_BOLD = 600
    BOLD = 700
    EXTRA_BOLD = 800
    BLACK = 900


class FontSize(Enum):
    """字体大小枚举"""
    CAPTION = 10        # 说明文字
    SMALL = 11          # 小字体
    BODY = 12           # 正文
    INTERFACE = 13      # 界面
    SUBTITLE = 14       # 副标题
    TITLE = 16          # 标题
    LARGE_TITLE = 18    # 大标题
    DISPLAY = 20        # 展示
    HERO = 24           # 主标题


@dataclass
class FontDefinition:
    """字体定义"""
    name: str
    family: str
    size: int
    weight: FontWeight
    line_height: float
    letter_spacing: float
    description: str
    usage: str
    
    def to_qfont(self) -> QFont:
        """转换为QFont对象"""
        font = QFont(self.family, self.size)
        font.setWeight(QFont.Weight(self.weight.value))
        return font
    
    def to_css(self) -> str:
        """转换为CSS样式"""
        return f"""
        font-family: {self.family};
        font-size: {self.size}px;
        font-weight: {self.weight.value};
        line-height: {self.line_height};
        letter-spacing: {self.letter_spacing}em;
        """


class TypographyHierarchy:
    """字体层次系统"""
    
    def __init__(self):
        self.font_definitions: Dict[str, FontDefinition] = {}
        self.font_fallbacks = self.get_system_font_fallbacks()
        
        self.initialize_font_hierarchy()
        logger.info("字体层次系统初始化完成")
    
    def get_system_font_fallbacks(self) -> Dict[str, List[str]]:
        """获取系统字体回退方案"""
        system = platform.system()
        
        if system == "Windows":
            return {
                "sans_serif": ["Segoe UI", "Microsoft YaHei", "SimHei", "Arial", "sans-serif"],
                "serif": ["Times New Roman", "SimSun", "serif"],
                "monospace": ["Consolas", "Courier New", "SimSun", "monospace"],
                "display": ["Segoe UI", "Microsoft YaHei", "SimHei", "Arial", "sans-serif"]
            }
        elif system == "Darwin":  # macOS
            return {
                "sans_serif": ["SF Pro Display", "PingFang SC", "Helvetica Neue", "Arial", "sans-serif"],
                "serif": ["Times New Roman", "STSong", "serif"],
                "monospace": ["SF Mono", "Monaco", "Menlo", "monospace"],
                "display": ["SF Pro Display", "PingFang SC", "Helvetica Neue", "sans-serif"]
            }
        else:  # Linux
            return {
                "sans_serif": ["Ubuntu", "Noto Sans CJK SC", "DejaVu Sans", "Arial", "sans-serif"],
                "serif": ["Ubuntu", "Noto Serif CJK SC", "DejaVu Serif", "serif"],
                "monospace": ["Ubuntu Mono", "Noto Sans Mono CJK SC", "DejaVu Sans Mono", "monospace"],
                "display": ["Ubuntu", "Noto Sans CJK SC", "DejaVu Sans", "sans-serif"]
            }
    
    def initialize_font_hierarchy(self):
        """初始化字体层次"""
        # 界面字体 - 用于按钮、菜单、标签等界面元素
        self.font_definitions["interface_primary"] = FontDefinition(
            name="界面主要字体",
            family=", ".join(self.font_fallbacks["sans_serif"]),
            size=FontSize.INTERFACE.value,
            weight=FontWeight.REGULAR,
            line_height=1.4,
            letter_spacing=0.0,
            description="用于界面主要文本，如按钮、菜单项、标签",
            usage="按钮文字、菜单项、工具栏标签、面板标题"
        )
        
        self.font_definitions["interface_secondary"] = FontDefinition(
            name="界面次要字体",
            family=", ".join(self.font_fallbacks["sans_serif"]),
            size=FontSize.SMALL.value,
            weight=FontWeight.REGULAR,
            line_height=1.3,
            letter_spacing=0.0,
            description="用于界面次要文本，如状态栏、工具提示",
            usage="状态栏文字、工具提示、次要标签"
        )
        
        # 数据字体 - 用于显示数值、时间码、坐标等数据
        self.font_definitions["data_primary"] = FontDefinition(
            name="数据主要字体",
            family=", ".join(self.font_fallbacks["monospace"]),
            size=FontSize.BODY.value,
            weight=FontWeight.REGULAR,
            line_height=1.2,
            letter_spacing=0.05,
            description="用于显示数值、时间码、坐标等精确数据",
            usage="时间码显示、数值输入框、坐标显示、帧数显示"
        )
        
        self.font_definitions["data_small"] = FontDefinition(
            name="数据小字体",
            family=", ".join(self.font_fallbacks["monospace"]),
            size=FontSize.CAPTION.value,
            weight=FontWeight.REGULAR,
            line_height=1.2,
            letter_spacing=0.05,
            description="用于显示小尺寸的数据信息",
            usage="时间轴刻度、小数值标签、单位显示"
        )
        
        # 标题字体 - 用于面板标题、对话框标题等
        self.font_definitions["title_large"] = FontDefinition(
            name="大标题字体",
            family=", ".join(self.font_fallbacks["display"]),
            size=FontSize.LARGE_TITLE.value,
            weight=FontWeight.SEMI_BOLD,
            line_height=1.3,
            letter_spacing=-0.02,
            description="用于主要标题和重要面板标题",
            usage="对话框标题、主面板标题、欢迎页标题"
        )
        
        self.font_definitions["title_medium"] = FontDefinition(
            name="中标题字体",
            family=", ".join(self.font_fallbacks["sans_serif"]),
            size=FontSize.TITLE.value,
            weight=FontWeight.SEMI_BOLD,
            line_height=1.3,
            letter_spacing=-0.01,
            description="用于次级标题和分组标题",
            usage="属性面板分组标题、设置页面标题、工具面板标题"
        )
        
        self.font_definitions["title_small"] = FontDefinition(
            name="小标题字体",
            family=", ".join(self.font_fallbacks["sans_serif"]),
            size=FontSize.SUBTITLE.value,
            weight=FontWeight.MEDIUM,
            line_height=1.3,
            letter_spacing=0.0,
            description="用于小节标题和子分组标题",
            usage="属性子分组、列表标题、卡片标题"
        )
        
        # 说明字体 - 用于帮助文本、描述信息等
        self.font_definitions["caption_primary"] = FontDefinition(
            name="说明主要字体",
            family=", ".join(self.font_fallbacks["sans_serif"]),
            size=FontSize.CAPTION.value,
            weight=FontWeight.REGULAR,
            line_height=1.4,
            letter_spacing=0.0,
            description="用于说明文字和帮助信息",
            usage="工具提示、帮助文本、状态描述、版权信息"
        )
        
        self.font_definitions["caption_secondary"] = FontDefinition(
            name="说明次要字体",
            family=", ".join(self.font_fallbacks["sans_serif"]),
            size=9,
            weight=FontWeight.REGULAR,
            line_height=1.3,
            letter_spacing=0.0,
            description="用于次要说明文字",
            usage="版本号、构建信息、调试信息"
        )
        
        # 代码字体 - 用于代码显示、日志等
        self.font_definitions["code_primary"] = FontDefinition(
            name="代码主要字体",
            family=", ".join(self.font_fallbacks["monospace"]),
            size=FontSize.BODY.value,
            weight=FontWeight.REGULAR,
            line_height=1.5,
            letter_spacing=0.0,
            description="用于代码显示和编辑",
            usage="代码编辑器、生成的代码显示、JSON数据"
        )
        
        self.font_definitions["code_small"] = FontDefinition(
            name="代码小字体",
            family=", ".join(self.font_fallbacks["monospace"]),
            size=FontSize.SMALL.value,
            weight=FontWeight.REGULAR,
            line_height=1.4,
            letter_spacing=0.0,
            description="用于小尺寸代码显示",
            usage="行号、代码片段、内联代码"
        )
        
        # 展示字体 - 用于重要信息展示
        self.font_definitions["display_hero"] = FontDefinition(
            name="主展示字体",
            family=", ".join(self.font_fallbacks["display"]),
            size=FontSize.HERO.value,
            weight=FontWeight.BOLD,
            line_height=1.2,
            letter_spacing=-0.03,
            description="用于最重要的展示信息",
            usage="欢迎页主标题、重要数值显示、品牌标题"
        )
        
        self.font_definitions["display_large"] = FontDefinition(
            name="大展示字体",
            family=", ".join(self.font_fallbacks["display"]),
            size=FontSize.DISPLAY.value,
            weight=FontWeight.SEMI_BOLD,
            line_height=1.3,
            letter_spacing=-0.02,
            description="用于重要信息展示",
            usage="统计数字、进度百分比、重要状态"
        )
    
    def get_font_definition(self, font_key: str) -> Optional[FontDefinition]:
        """获取字体定义"""
        return self.font_definitions.get(font_key)
    
    def get_qfont(self, font_key: str) -> QFont:
        """获取QFont对象"""
        definition = self.get_font_definition(font_key)
        if definition:
            return definition.to_qfont()
        
        # 返回默认字体
        return QFont("Microsoft YaHei", 12)
    
    def get_font_css(self, font_key: str) -> str:
        """获取字体CSS样式"""
        definition = self.get_font_definition(font_key)
        if definition:
            return definition.to_css()
        
        return "font-family: sans-serif; font-size: 12px;"
    
    def get_fonts_by_category(self, category: FontCategory) -> Dict[str, FontDefinition]:
        """按分类获取字体"""
        category_fonts = {}
        
        category_mapping = {
            FontCategory.INTERFACE: ["interface_primary", "interface_secondary"],
            FontCategory.DATA: ["data_primary", "data_small"],
            FontCategory.TITLE: ["title_large", "title_medium", "title_small"],
            FontCategory.CAPTION: ["caption_primary", "caption_secondary"],
            FontCategory.CODE: ["code_primary", "code_small"],
            FontCategory.DISPLAY: ["display_hero", "display_large"]
        }
        
        font_keys = category_mapping.get(category, [])
        for key in font_keys:
            if key in self.font_definitions:
                category_fonts[key] = self.font_definitions[key]
        
        return category_fonts
    
    def generate_font_stylesheet(self) -> str:
        """生成字体样式表"""
        css_rules = ["/* AI Animation Studio - 字体层次样式表 */\n"]
        
        for font_key, definition in self.font_definitions.items():
            css_class = font_key.replace("_", "-")
            css_rules.append(f".font-{css_class} {{")
            css_rules.append(f"  font-family: {definition.family};")
            css_rules.append(f"  font-size: {definition.size}px;")
            css_rules.append(f"  font-weight: {definition.weight.value};")
            css_rules.append(f"  line-height: {definition.line_height};")
            css_rules.append(f"  letter-spacing: {definition.letter_spacing}em;")
            css_rules.append("}")
            css_rules.append("")
        
        return "\n".join(css_rules)
    
    def export_font_definitions(self) -> Dict[str, Any]:
        """导出字体定义"""
        export_data = {
            "version": "1.0",
            "system": platform.system(),
            "font_fallbacks": self.font_fallbacks,
            "definitions": {}
        }
        
        for key, definition in self.font_definitions.items():
            export_data["definitions"][key] = {
                "name": definition.name,
                "family": definition.family,
                "size": definition.size,
                "weight": definition.weight.value,
                "line_height": definition.line_height,
                "letter_spacing": definition.letter_spacing,
                "description": definition.description,
                "usage": definition.usage
            }
        
        return export_data


class TypographyManager(QObject):
    """字体管理器"""
    
    font_changed = pyqtSignal(str)  # 字体改变信号
    
    def __init__(self):
        super().__init__()
        self.typography_hierarchy = TypographyHierarchy()
        self.applied_fonts: Dict[str, QWidget] = {}
        
        logger.info("字体管理器初始化完成")
    
    def apply_font_to_widget(self, widget: QWidget, font_key: str):
        """应用字体到组件"""
        try:
            font = self.typography_hierarchy.get_qfont(font_key)
            widget.setFont(font)
            
            # 记录应用的字体
            widget_id = id(widget)
            self.applied_fonts[str(widget_id)] = widget
            
            logger.debug(f"应用字体 {font_key} 到组件")
            
        except Exception as e:
            logger.error(f"应用字体失败: {e}")
    
    def apply_font_hierarchy_to_application(self):
        """应用字体层次到应用程序"""
        try:
            app = QApplication.instance()
            if not app:
                return
            
            # 设置应用程序默认字体
            default_font = self.typography_hierarchy.get_qfont("interface_primary")
            app.setFont(default_font)
            
            # 生成全局样式表
            stylesheet = self.generate_global_font_stylesheet()
            current_stylesheet = app.styleSheet()
            app.setStyleSheet(current_stylesheet + "\n" + stylesheet)
            
            logger.info("字体层次已应用到应用程序")
            
        except Exception as e:
            logger.error(f"应用字体层次失败: {e}")
    
    def generate_global_font_stylesheet(self) -> str:
        """生成全局字体样式表"""
        return f"""
        /* 全局字体样式 */
        QLabel {{
            font-family: {self.typography_hierarchy.font_fallbacks["sans_serif"][0]};
        }}
        
        QPushButton {{
            {self.typography_hierarchy.get_font_css("interface_primary")}
        }}
        
        QLineEdit, QTextEdit, QPlainTextEdit {{
            {self.typography_hierarchy.get_font_css("data_primary")}
        }}
        
        QGroupBox::title {{
            {self.typography_hierarchy.get_font_css("title_small")}
        }}
        
        QTabWidget::tab-bar {{
            {self.typography_hierarchy.get_font_css("interface_primary")}
        }}
        
        QStatusBar {{
            {self.typography_hierarchy.get_font_css("caption_primary")}
        }}
        
        QToolTip {{
            {self.typography_hierarchy.get_font_css("caption_primary")}
        }}
        """
    
    def get_font_metrics(self, font_key: str) -> QFontMetrics:
        """获取字体度量"""
        font = self.typography_hierarchy.get_qfont(font_key)
        return QFontMetrics(font)
    
    def calculate_text_size(self, text: str, font_key: str) -> Tuple[int, int]:
        """计算文本尺寸"""
        metrics = self.get_font_metrics(font_key)
        width = metrics.horizontalAdvance(text)
        height = metrics.height()
        return width, height
    
    def get_typography_summary(self) -> Dict[str, Any]:
        """获取字体摘要"""
        return {
            "total_definitions": len(self.typography_hierarchy.font_definitions),
            "applied_widgets": len(self.applied_fonts),
            "system": platform.system(),
            "categories": {
                category.name: len(self.typography_hierarchy.get_fonts_by_category(category))
                for category in FontCategory
            }
        }


class FontApplicator:
    """字体应用器"""

    def __init__(self, typography_manager: TypographyManager):
        self.typography_manager = typography_manager
        self.widget_font_mapping = self.create_widget_font_mapping()

        logger.info("字体应用器初始化完成")

    def create_widget_font_mapping(self) -> Dict[str, str]:
        """创建组件字体映射"""
        return {
            # 界面组件
            "QPushButton": "interface_primary",
            "QToolButton": "interface_primary",
            "QCheckBox": "interface_primary",
            "QRadioButton": "interface_primary",
            "QComboBox": "interface_primary",
            "QTabWidget": "interface_primary",
            "QMenuBar": "interface_primary",
            "QMenu": "interface_primary",

            # 标题组件
            "QGroupBox": "title_small",
            "QDialog": "title_medium",
            "QMainWindow": "title_large",

            # 数据输入组件
            "QLineEdit": "data_primary",
            "QSpinBox": "data_primary",
            "QDoubleSpinBox": "data_primary",
            "QTimeEdit": "data_primary",
            "QDateEdit": "data_primary",

            # 文本显示组件
            "QLabel": "interface_primary",
            "QTextEdit": "code_primary",
            "QPlainTextEdit": "code_primary",

            # 状态组件
            "QStatusBar": "caption_primary",
            "QProgressBar": "caption_primary",

            # 列表和树组件
            "QListWidget": "interface_primary",
            "QTreeWidget": "interface_primary",
            "QTableWidget": "interface_primary"
        }

    def apply_fonts_to_widget_hierarchy(self, root_widget: QWidget):
        """应用字体到组件层次"""
        try:
            # 应用到根组件
            self.apply_font_to_widget(root_widget)

            # 递归应用到所有子组件
            self.apply_fonts_recursive(root_widget)

            logger.info(f"字体层次已应用到组件: {root_widget.__class__.__name__}")

        except Exception as e:
            logger.error(f"应用字体层次失败: {e}")

    def apply_fonts_recursive(self, widget: QWidget):
        """递归应用字体"""
        for child in widget.findChildren(QWidget):
            self.apply_font_to_widget(child)

    def apply_font_to_widget(self, widget: QWidget):
        """应用字体到单个组件"""
        try:
            widget_class = widget.__class__.__name__

            # 检查特殊对象名称映射
            object_name = widget.objectName()
            if object_name:
                font_key = self.get_font_key_by_object_name(object_name)
                if font_key:
                    self.typography_manager.apply_font_to_widget(widget, font_key)
                    return

            # 使用类名映射
            font_key = self.widget_font_mapping.get(widget_class)
            if font_key:
                self.typography_manager.apply_font_to_widget(widget, font_key)

        except Exception as e:
            logger.error(f"应用字体到组件失败: {e}")

    def get_font_key_by_object_name(self, object_name: str) -> Optional[str]:
        """根据对象名称获取字体键"""
        # 特殊对象名称映射
        special_mappings = {
            # 标题相关
            "main_title": "display_hero",
            "panel_title": "title_medium",
            "group_title": "title_small",
            "dialog_title": "title_large",

            # 数据相关
            "time_display": "data_primary",
            "coordinate_display": "data_primary",
            "frame_counter": "data_small",
            "timeline_scale": "data_small",

            # 代码相关
            "code_editor": "code_primary",
            "code_viewer": "code_primary",
            "json_display": "code_small",

            # 状态相关
            "status_label": "caption_primary",
            "help_text": "caption_primary",
            "version_info": "caption_secondary",

            # 展示相关
            "welcome_title": "display_hero",
            "progress_text": "display_large"
        }

        return special_mappings.get(object_name)

    def apply_semantic_fonts(self, widget: QWidget):
        """应用语义化字体"""
        try:
            # 根据组件的语义角色应用字体
            if hasattr(widget, 'property'):
                semantic_role = widget.property("semantic_role")
                if semantic_role:
                    font_key = self.get_font_key_by_semantic_role(semantic_role)
                    if font_key:
                        self.typography_manager.apply_font_to_widget(widget, font_key)
                        return

            # 根据样式类应用字体
            if hasattr(widget, 'property'):
                style_class = widget.property("style_class")
                if style_class:
                    font_key = self.get_font_key_by_style_class(style_class)
                    if font_key:
                        self.typography_manager.apply_font_to_widget(widget, font_key)

        except Exception as e:
            logger.error(f"应用语义化字体失败: {e}")

    def get_font_key_by_semantic_role(self, role: str) -> Optional[str]:
        """根据语义角色获取字体键"""
        role_mappings = {
            "primary_title": "title_large",
            "secondary_title": "title_medium",
            "section_title": "title_small",
            "body_text": "interface_primary",
            "data_display": "data_primary",
            "code_display": "code_primary",
            "help_text": "caption_primary",
            "status_text": "caption_primary",
            "hero_text": "display_hero"
        }

        return role_mappings.get(role)

    def get_font_key_by_style_class(self, style_class: str) -> Optional[str]:
        """根据样式类获取字体键"""
        class_mappings = {
            "font-interface-primary": "interface_primary",
            "font-interface-secondary": "interface_secondary",
            "font-data-primary": "data_primary",
            "font-data-small": "data_small",
            "font-title-large": "title_large",
            "font-title-medium": "title_medium",
            "font-title-small": "title_small",
            "font-caption-primary": "caption_primary",
            "font-caption-secondary": "caption_secondary",
            "font-code-primary": "code_primary",
            "font-code-small": "code_small",
            "font-display-hero": "display_hero",
            "font-display-large": "display_large"
        }

        return class_mappings.get(style_class)


class TypographyValidator:
    """字体验证器"""

    def __init__(self, typography_hierarchy: TypographyHierarchy):
        self.typography_hierarchy = typography_hierarchy

    def validate_font_availability(self) -> Dict[str, bool]:
        """验证字体可用性"""
        font_db = QFontDatabase()
        available_families = font_db.families()

        validation_results = {}

        for font_key, definition in self.typography_hierarchy.font_definitions.items():
            # 检查主要字体族
            primary_family = definition.family.split(",")[0].strip().strip("'\"")
            is_available = primary_family in available_families

            validation_results[font_key] = {
                "available": is_available,
                "primary_family": primary_family,
                "fallback_available": self.check_fallback_availability(definition.family, available_families)
            }

        return validation_results

    def check_fallback_availability(self, font_family_string: str, available_families: List[str]) -> bool:
        """检查回退字体可用性"""
        families = [f.strip().strip("'\"") for f in font_family_string.split(",")]

        for family in families:
            if family in ["sans-serif", "serif", "monospace"]:
                return True  # 通用字体族总是可用
            if family in available_families:
                return True

        return False

    def generate_font_report(self) -> Dict[str, Any]:
        """生成字体报告"""
        validation_results = self.validate_font_availability()

        total_fonts = len(validation_results)
        available_fonts = sum(1 for result in validation_results.values() if result["available"])
        fallback_fonts = sum(1 for result in validation_results.values() if result["fallback_available"])

        return {
            "total_fonts": total_fonts,
            "available_fonts": available_fonts,
            "fallback_fonts": fallback_fonts,
            "availability_rate": available_fonts / total_fonts if total_fonts > 0 else 0,
            "fallback_rate": fallback_fonts / total_fonts if total_fonts > 0 else 0,
            "details": validation_results,
            "recommendations": self.generate_recommendations(validation_results)
        }

    def generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """生成字体建议"""
        recommendations = []

        unavailable_fonts = [
            key for key, result in validation_results.items()
            if not result["available"] and not result["fallback_available"]
        ]

        if unavailable_fonts:
            recommendations.append(f"以下字体定义缺少可用的字体族: {', '.join(unavailable_fonts)}")
            recommendations.append("建议安装推荐的字体或更新字体回退列表")

        primary_unavailable = [
            key for key, result in validation_results.items()
            if not result["available"] and result["fallback_available"]
        ]

        if primary_unavailable:
            recommendations.append(f"以下字体使用回退字体: {', '.join(primary_unavailable)}")
            recommendations.append("建议安装主要字体以获得最佳显示效果")

        return recommendations


class TypographyIntegrator:
    """字体集成器 - 整合字体系统到现有应用"""

    def __init__(self):
        self.typography_manager = TypographyManager()
        self.font_applicator = FontApplicator(self.typography_manager)
        self.validator = TypographyValidator(self.typography_manager.typography_hierarchy)

        logger.info("字体集成器初始化完成")

    def integrate_typography_system(self, main_window):
        """集成字体系统到主窗口"""
        try:
            # 1. 验证字体可用性
            font_report = self.validator.generate_font_report()
            logger.info(f"字体可用性: {font_report['availability_rate']:.1%}")

            # 2. 应用字体层次到应用程序
            self.typography_manager.apply_font_hierarchy_to_application()

            # 3. 应用字体到主窗口组件层次
            self.font_applicator.apply_fonts_to_widget_hierarchy(main_window)

            # 4. 设置特殊组件的字体
            self.apply_special_fonts(main_window)

            logger.info("字体系统集成完成")
            return True

        except Exception as e:
            logger.error(f"字体系统集成失败: {e}")
            return False

    def apply_special_fonts(self, main_window):
        """应用特殊组件的字体"""
        try:
            # 时间轴组件使用数据字体
            if hasattr(main_window, 'timeline_widget'):
                timeline = main_window.timeline_widget
                self.typography_manager.apply_font_to_widget(timeline, "data_primary")

                # 时间轴刻度使用小数据字体
                for child in timeline.findChildren(QLabel):
                    if "scale" in child.objectName().lower():
                        self.typography_manager.apply_font_to_widget(child, "data_small")

            # 代码查看器使用代码字体
            if hasattr(main_window, 'code_viewer'):
                code_viewer = main_window.code_viewer
                self.typography_manager.apply_font_to_widget(code_viewer, "code_primary")

            # 属性面板标题使用标题字体
            if hasattr(main_window, 'properties_widget'):
                properties = main_window.properties_widget
                for group_box in properties.findChildren(QGroupBox):
                    self.typography_manager.apply_font_to_widget(group_box, "title_small")

            # 状态栏使用说明字体
            if hasattr(main_window, 'statusBar'):
                status_bar = main_window.statusBar()
                self.typography_manager.apply_font_to_widget(status_bar, "caption_primary")

        except Exception as e:
            logger.error(f"应用特殊字体失败: {e}")

    def export_typography_config(self, file_path: str):
        """导出字体配置"""
        try:
            config = self.typography_manager.typography_hierarchy.export_font_definitions()

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            logger.info(f"字体配置已导出到: {file_path}")

        except Exception as e:
            logger.error(f"导出字体配置失败: {e}")

    def generate_typography_css(self, file_path: str):
        """生成字体CSS文件"""
        try:
            css_content = self.typography_manager.typography_hierarchy.generate_font_stylesheet()

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(css_content)

            logger.info(f"字体CSS已生成到: {file_path}")

        except Exception as e:
            logger.error(f"生成字体CSS失败: {e}")

    def get_integration_summary(self) -> Dict[str, Any]:
        """获取集成摘要"""
        font_report = self.validator.generate_font_report()
        typography_summary = self.typography_manager.get_typography_summary()

        return {
            "font_availability": font_report,
            "typography_system": typography_summary,
            "integration_status": "completed",
            "recommendations": font_report.get("recommendations", [])
        }
