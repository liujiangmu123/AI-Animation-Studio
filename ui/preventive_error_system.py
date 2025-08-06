"""
AI Animation Studio - 预防性错误设计系统
实现智能输入验证系统，防止用户犯错
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox,
                             QCheckBox, QSlider, QProgressBar, QFrame, QGroupBox,
                             QFormLayout, QScrollArea, QTabWidget, QListWidget,
                             QListWidgetItem, QTreeWidget, QTreeWidgetItem, QDialog,
                             QMessageBox, QToolTip, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QThread, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QBrush, QPen, QValidator, QRegularExpressionValidator

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, Set
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
import math

from core.logger import get_logger

logger = get_logger("preventive_error_system")


class ValidationLevel(Enum):
    """验证级别枚举"""
    SUCCESS = "success"     # 成功
    INFO = "info"          # 信息
    WARNING = "warning"    # 警告
    ERROR = "error"        # 错误
    CRITICAL = "critical"  # 严重错误


class ValidationTrigger(Enum):
    """验证触发时机枚举"""
    ON_INPUT = "on_input"           # 输入时
    ON_FOCUS_LOST = "on_focus_lost" # 失去焦点时
    ON_SUBMIT = "on_submit"         # 提交时
    ON_CHANGE = "on_change"         # 值改变时
    REAL_TIME = "real_time"         # 实时验证


class InputType(Enum):
    """输入类型枚举"""
    TEXT = "text"                   # 文本
    NUMBER = "number"               # 数字
    EMAIL = "email"                 # 邮箱
    URL = "url"                     # URL
    API_KEY = "api_key"            # API密钥
    FILE_PATH = "file_path"        # 文件路径
    TIME_DURATION = "time_duration" # 时间长度
    ANIMATION_DESC = "animation_desc" # 动画描述
    COLOR = "color"                 # 颜色
    PERCENTAGE = "percentage"       # 百分比
    EXPRESSION = "expression"       # 表达式


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    level: ValidationLevel
    message: str
    suggestions: List[str] = field(default_factory=list)
    auto_fix_available: bool = False
    auto_fix_function: Optional[Callable] = None
    field_name: str = ""
    error_code: str = ""
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationRule:
    """验证规则"""
    name: str
    description: str
    validator_function: Callable
    trigger: ValidationTrigger
    priority: int = 0
    enabled: bool = True
    error_message: str = ""
    suggestion_message: str = ""


class SmartValidator:
    """智能验证器基类"""
    
    def __init__(self, input_type: InputType):
        self.input_type = input_type
        self.rules: List[ValidationRule] = []
        self.context: Dict[str, Any] = {}
        
    def add_rule(self, rule: ValidationRule):
        """添加验证规则"""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def validate(self, value: Any, context: Dict[str, Any] = None) -> ValidationResult:
        """执行验证"""
        if context:
            self.context.update(context)
        
        # 按优先级执行规则
        for rule in self.rules:
            if not rule.enabled:
                continue
                
            try:
                result = rule.validator_function(value, self.context)
                if not result.is_valid:
                    result.field_name = self.context.get('field_name', '')
                    return result
            except Exception as e:
                logger.error(f"验证规则 {rule.name} 执行失败: {e}")
                continue
        
        return ValidationResult(True, ValidationLevel.SUCCESS, "验证通过")


class TextValidator(SmartValidator):
    """文本验证器"""
    
    def __init__(self):
        super().__init__(InputType.TEXT)
        self.setup_default_rules()
    
    def setup_default_rules(self):
        """设置默认规则"""
        # 非空验证
        self.add_rule(ValidationRule(
            name="not_empty",
            description="非空验证",
            validator_function=self.validate_not_empty,
            trigger=ValidationTrigger.ON_INPUT,
            priority=100
        ))
        
        # 长度验证
        self.add_rule(ValidationRule(
            name="length_check",
            description="长度验证",
            validator_function=self.validate_length,
            trigger=ValidationTrigger.ON_INPUT,
            priority=90
        ))
        
        # 特殊字符验证
        self.add_rule(ValidationRule(
            name="special_chars",
            description="特殊字符验证",
            validator_function=self.validate_special_chars,
            trigger=ValidationTrigger.ON_INPUT,
            priority=80
        ))
    
    def validate_not_empty(self, value: str, context: Dict[str, Any]) -> ValidationResult:
        """非空验证"""
        if not value or not value.strip():
            return ValidationResult(
                False, ValidationLevel.ERROR, "此字段不能为空",
                suggestions=["请输入有效内容"]
            )
        return ValidationResult(True, ValidationLevel.SUCCESS, "")
    
    def validate_length(self, value: str, context: Dict[str, Any]) -> ValidationResult:
        """长度验证"""
        min_length = context.get('min_length', 0)
        max_length = context.get('max_length', 1000)
        
        if len(value) < min_length:
            return ValidationResult(
                False, ValidationLevel.WARNING, f"内容过短，至少需要{min_length}个字符",
                suggestions=[f"当前{len(value)}个字符，还需要{min_length - len(value)}个字符"]
            )
        
        if len(value) > max_length:
            return ValidationResult(
                False, ValidationLevel.ERROR, f"内容过长，最多允许{max_length}个字符",
                suggestions=[f"当前{len(value)}个字符，需要删除{len(value) - max_length}个字符"]
            )
        
        return ValidationResult(True, ValidationLevel.SUCCESS, "")
    
    def validate_special_chars(self, value: str, context: Dict[str, Any]) -> ValidationResult:
        """特殊字符验证"""
        forbidden_chars = context.get('forbidden_chars', [])
        
        for char in forbidden_chars:
            if char in value:
                return ValidationResult(
                    False, ValidationLevel.ERROR, f"不允许包含字符: {char}",
                    suggestions=[f"请移除字符 '{char}'"]
                )
        
        return ValidationResult(True, ValidationLevel.SUCCESS, "")


class NumberValidator(SmartValidator):
    """数字验证器"""
    
    def __init__(self):
        super().__init__(InputType.NUMBER)
        self.setup_default_rules()
    
    def setup_default_rules(self):
        """设置默认规则"""
        # 数字格式验证
        self.add_rule(ValidationRule(
            name="number_format",
            description="数字格式验证",
            validator_function=self.validate_number_format,
            trigger=ValidationTrigger.ON_INPUT,
            priority=100
        ))
        
        # 范围验证
        self.add_rule(ValidationRule(
            name="range_check",
            description="数值范围验证",
            validator_function=self.validate_range,
            trigger=ValidationTrigger.ON_INPUT,
            priority=90
        ))
        
        # 精度验证
        self.add_rule(ValidationRule(
            name="precision_check",
            description="数字精度验证",
            validator_function=self.validate_precision,
            trigger=ValidationTrigger.ON_INPUT,
            priority=80
        ))
    
    def validate_number_format(self, value: str, context: Dict[str, Any]) -> ValidationResult:
        """数字格式验证"""
        if not value:
            return ValidationResult(True, ValidationLevel.SUCCESS, "")
        
        try:
            float(value)
            return ValidationResult(True, ValidationLevel.SUCCESS, "")
        except ValueError:
            return ValidationResult(
                False, ValidationLevel.ERROR, "请输入有效的数字",
                suggestions=["只能包含数字、小数点和负号", "示例: 123, -45.67, 0.5"]
            )
    
    def validate_range(self, value: str, context: Dict[str, Any]) -> ValidationResult:
        """范围验证"""
        if not value:
            return ValidationResult(True, ValidationLevel.SUCCESS, "")
        
        try:
            num_value = float(value)
            min_val = context.get('min_value', float('-inf'))
            max_val = context.get('max_value', float('inf'))
            
            if num_value < min_val:
                return ValidationResult(
                    False, ValidationLevel.ERROR, f"数值不能小于{min_val}",
                    suggestions=[f"请输入大于等于{min_val}的数值"]
                )
            
            if num_value > max_val:
                return ValidationResult(
                    False, ValidationLevel.ERROR, f"数值不能大于{max_val}",
                    suggestions=[f"请输入小于等于{max_val}的数值"]
                )
            
            # 警告范围
            warn_min = context.get('warn_min')
            warn_max = context.get('warn_max')
            
            if warn_min is not None and num_value < warn_min:
                return ValidationResult(
                    True, ValidationLevel.WARNING, f"建议数值不小于{warn_min}",
                    suggestions=[f"当前值{num_value}可能过小，建议使用{warn_min}以上的值"]
                )
            
            if warn_max is not None and num_value > warn_max:
                return ValidationResult(
                    True, ValidationLevel.WARNING, f"建议数值不大于{warn_max}",
                    suggestions=[f"当前值{num_value}可能过大，建议使用{warn_max}以下的值"]
                )
            
            return ValidationResult(True, ValidationLevel.SUCCESS, "")
            
        except ValueError:
            return ValidationResult(True, ValidationLevel.SUCCESS, "")  # 格式验证会处理
    
    def validate_precision(self, value: str, context: Dict[str, Any]) -> ValidationResult:
        """精度验证"""
        if not value or '.' not in value:
            return ValidationResult(True, ValidationLevel.SUCCESS, "")
        
        decimal_places = len(value.split('.')[1])
        max_precision = context.get('max_precision', 10)
        
        if decimal_places > max_precision:
            return ValidationResult(
                False, ValidationLevel.WARNING, f"小数位数过多，最多支持{max_precision}位",
                suggestions=[f"当前{decimal_places}位小数，建议保留{max_precision}位以内"]
            )
        
        return ValidationResult(True, ValidationLevel.SUCCESS, "")


class APIKeyValidator(SmartValidator):
    """API密钥验证器"""
    
    def __init__(self):
        super().__init__(InputType.API_KEY)
        self.setup_default_rules()
    
    def setup_default_rules(self):
        """设置默认规则"""
        # 格式验证
        self.add_rule(ValidationRule(
            name="format_check",
            description="API密钥格式验证",
            validator_function=self.validate_format,
            trigger=ValidationTrigger.ON_INPUT,
            priority=100
        ))
        
        # 长度验证
        self.add_rule(ValidationRule(
            name="length_check",
            description="API密钥长度验证",
            validator_function=self.validate_length,
            trigger=ValidationTrigger.ON_INPUT,
            priority=90
        ))
        
        # 服务特定验证
        self.add_rule(ValidationRule(
            name="service_specific",
            description="服务特定验证",
            validator_function=self.validate_service_specific,
            trigger=ValidationTrigger.ON_INPUT,
            priority=80
        ))
    
    def validate_format(self, value: str, context: Dict[str, Any]) -> ValidationResult:
        """格式验证"""
        if not value:
            return ValidationResult(True, ValidationLevel.SUCCESS, "")
        
        # 检查是否包含空格
        if ' ' in value:
            return ValidationResult(
                False, ValidationLevel.ERROR, "API密钥不应包含空格",
                suggestions=["请移除所有空格字符"],
                auto_fix_available=True,
                auto_fix_function=lambda: value.replace(' ', '')
            )
        
        # 检查是否包含特殊字符
        if not re.match(r'^[A-Za-z0-9_-]+$', value):
            return ValidationResult(
                False, ValidationLevel.WARNING, "API密钥包含异常字符",
                suggestions=["API密钥通常只包含字母、数字、下划线和连字符"]
            )
        
        return ValidationResult(True, ValidationLevel.SUCCESS, "")
    
    def validate_length(self, value: str, context: Dict[str, Any]) -> ValidationResult:
        """长度验证"""
        if not value:
            return ValidationResult(True, ValidationLevel.SUCCESS, "")
        
        if len(value) < 20:
            return ValidationResult(
                False, ValidationLevel.WARNING, "API密钥长度似乎过短",
                suggestions=["请确认API密钥是否完整"]
            )
        
        if len(value) > 200:
            return ValidationResult(
                False, ValidationLevel.WARNING, "API密钥长度似乎过长",
                suggestions=["请确认API密钥是否正确"]
            )
        
        return ValidationResult(True, ValidationLevel.SUCCESS, "")
    
    def validate_service_specific(self, value: str, context: Dict[str, Any]) -> ValidationResult:
        """服务特定验证"""
        if not value:
            return ValidationResult(True, ValidationLevel.SUCCESS, "")
        
        service = context.get('service', '').lower()
        
        if service == 'gemini':
            if not value.startswith('AIza'):
                return ValidationResult(
                    False, ValidationLevel.WARNING, "Gemini API密钥通常以'AIza'开头",
                    suggestions=["请确认是否为正确的Gemini API密钥"]
                )
        elif service == 'openai':
            if not value.startswith('sk-'):
                return ValidationResult(
                    False, ValidationLevel.WARNING, "OpenAI API密钥通常以'sk-'开头",
                    suggestions=["请确认是否为正确的OpenAI API密钥"]
                )
        elif service == 'claude':
            if not value.startswith('sk-ant-'):
                return ValidationResult(
                    False, ValidationLevel.WARNING, "Claude API密钥通常以'sk-ant-'开头",
                    suggestions=["请确认是否为正确的Claude API密钥"]
                )
        
        return ValidationResult(True, ValidationLevel.SUCCESS, "")


class AnimationDescriptionValidator(SmartValidator):
    """动画描述验证器"""
    
    def __init__(self):
        super().__init__(InputType.ANIMATION_DESC)
        self.setup_default_rules()
    
    def setup_default_rules(self):
        """设置默认规则"""
        # 完整性验证
        self.add_rule(ValidationRule(
            name="completeness_check",
            description="描述完整性验证",
            validator_function=self.validate_completeness,
            trigger=ValidationTrigger.ON_INPUT,
            priority=100
        ))
        
        # 清晰度验证
        self.add_rule(ValidationRule(
            name="clarity_check",
            description="描述清晰度验证",
            validator_function=self.validate_clarity,
            trigger=ValidationTrigger.ON_INPUT,
            priority=90
        ))
        
        # 技术可行性验证
        self.add_rule(ValidationRule(
            name="feasibility_check",
            description="技术可行性验证",
            validator_function=self.validate_feasibility,
            trigger=ValidationTrigger.ON_INPUT,
            priority=80
        ))
    
    def validate_completeness(self, value: str, context: Dict[str, Any]) -> ValidationResult:
        """完整性验证"""
        if not value or len(value.strip()) < 10:
            return ValidationResult(
                False, ValidationLevel.WARNING, "动画描述过于简短",
                suggestions=["建议添加更多细节，如动作、对象、效果等"]
            )
        
        # 检查必要元素
        required_elements = ["动作", "对象", "效果"]
        animation_keywords = {
            "动作": ["移动", "旋转", "缩放", "淡入", "淡出", "飞", "跳", "滑", "弹", "摇摆"],
            "对象": ["球", "方块", "文字", "图片", "按钮", "元素", "物体"],
            "效果": ["渐变", "阴影", "发光", "模糊", "透明", "颜色", "大小"]
        }
        
        missing_elements = []
        suggestions = []
        
        for element in required_elements:
            keywords = animation_keywords.get(element, [])
            if not any(keyword in value for keyword in keywords):
                missing_elements.append(element)
        
        if missing_elements:
            suggestions.append(f"建议添加{', '.join(missing_elements)}相关的描述")
            return ValidationResult(
                True, ValidationLevel.INFO, "可以让描述更完整",
                suggestions=suggestions
            )
        
        return ValidationResult(True, ValidationLevel.SUCCESS, "")
    
    def validate_clarity(self, value: str, context: Dict[str, Any]) -> ValidationResult:
        """清晰度验证"""
        if not value:
            return ValidationResult(True, ValidationLevel.SUCCESS, "")
        
        # 检查模糊词汇
        vague_words = ["那个", "这个", "某种", "一些", "好看的", "不错的", "合适的"]
        found_vague = [word for word in vague_words if word in value]
        
        if found_vague:
            return ValidationResult(
                True, ValidationLevel.INFO, "描述可以更具体",
                suggestions=[f"建议将'{', '.join(found_vague)}'替换为更具体的描述"]
            )
        
        return ValidationResult(True, ValidationLevel.SUCCESS, "")
    
    def validate_feasibility(self, value: str, context: Dict[str, Any]) -> ValidationResult:
        """技术可行性验证"""
        if not value:
            return ValidationResult(True, ValidationLevel.SUCCESS, "")
        
        # 检查复杂度
        complex_keywords = ["3D", "物理引擎", "粒子系统", "复杂路径", "多层嵌套"]
        found_complex = [keyword for keyword in complex_keywords if keyword in value]
        
        if found_complex:
            return ValidationResult(
                True, ValidationLevel.WARNING, "描述包含复杂效果",
                suggestions=[
                    f"检测到复杂效果: {', '.join(found_complex)}",
                    "建议确认技术实现的可行性",
                    "复杂效果可能需要更多渲染时间"
                ]
            )
        
        return ValidationResult(True, ValidationLevel.SUCCESS, "")


class SmartInputWidget(QWidget):
    """智能输入组件"""

    value_changed = pyqtSignal(str)
    validation_changed = pyqtSignal(ValidationResult)

    def __init__(self, input_type: InputType, validator: SmartValidator = None, parent=None):
        super().__init__(parent)
        self.input_type = input_type
        self.validator = validator or self.create_default_validator()
        self.validation_result = ValidationResult(True, ValidationLevel.SUCCESS, "")
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self.perform_validation)

        self.setup_ui()
        self.setup_connections()

    def create_default_validator(self) -> SmartValidator:
        """创建默认验证器"""
        validator_map = {
            InputType.TEXT: TextValidator,
            InputType.NUMBER: NumberValidator,
            InputType.API_KEY: APIKeyValidator,
            InputType.ANIMATION_DESC: AnimationDescriptionValidator
        }

        validator_class = validator_map.get(self.input_type, TextValidator)
        return validator_class()

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # 输入控件容器
        input_container = QFrame()
        input_container.setFrameStyle(QFrame.Shape.StyledPanel)
        input_container.setStyleSheet("""
            QFrame {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
            }
            QFrame:focus-within {
                border-color: #2196f3;
            }
        """)

        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(8, 6, 8, 6)

        # 创建输入控件
        self.input_widget = self.create_input_widget()
        input_layout.addWidget(self.input_widget)

        # 状态图标
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(20, 20)
        self.status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_layout.addWidget(self.status_icon)

        layout.addWidget(input_container)

        # 验证消息
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("color: #666; font-size: 11px; margin: 2px 4px;")
        self.message_label.hide()
        layout.addWidget(self.message_label)

        # 建议列表
        self.suggestions_widget = QFrame()
        self.suggestions_widget.setFrameStyle(QFrame.Shape.StyledPanel)
        self.suggestions_widget.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 4px;
                padding: 6px;
            }
        """)

        suggestions_layout = QVBoxLayout(self.suggestions_widget)
        suggestions_layout.setContentsMargins(6, 4, 6, 4)
        suggestions_layout.setSpacing(2)

        self.suggestions_label = QLabel("💡 建议:")
        self.suggestions_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        suggestions_layout.addWidget(self.suggestions_label)

        self.suggestions_list = QLabel()
        self.suggestions_list.setWordWrap(True)
        self.suggestions_list.setStyleSheet("color: #856404; font-size: 10px;")
        suggestions_layout.addWidget(self.suggestions_list)

        self.suggestions_widget.hide()
        layout.addWidget(self.suggestions_widget)

    def create_input_widget(self) -> QWidget:
        """创建输入控件"""
        if self.input_type in [InputType.TEXT, InputType.API_KEY, InputType.EMAIL, InputType.URL]:
            widget = QLineEdit()
            widget.textChanged.connect(self.on_input_changed)
            widget.editingFinished.connect(self.on_editing_finished)
            return widget

        elif self.input_type == InputType.ANIMATION_DESC:
            widget = QTextEdit()
            widget.setMaximumHeight(100)
            widget.textChanged.connect(self.on_text_edit_changed)
            return widget

        elif self.input_type == InputType.NUMBER:
            widget = QLineEdit()
            widget.setValidator(QRegularExpressionValidator(r'^-?\d*\.?\d*$'))
            widget.textChanged.connect(self.on_input_changed)
            widget.editingFinished.connect(self.on_editing_finished)
            return widget

        elif self.input_type == InputType.PERCENTAGE:
            widget = QSlider(Qt.Orientation.Horizontal)
            widget.setRange(0, 100)
            widget.valueChanged.connect(self.on_slider_changed)
            return widget

        else:
            widget = QLineEdit()
            widget.textChanged.connect(self.on_input_changed)
            return widget

    def setup_connections(self):
        """设置信号连接"""
        pass

    def on_input_changed(self, text: str):
        """输入改变处理"""
        self.value_changed.emit(text)

        # 延迟验证，避免频繁验证
        self.validation_timer.stop()
        self.validation_timer.start(300)  # 300ms延迟

    def on_text_edit_changed(self):
        """文本编辑器改变处理"""
        if isinstance(self.input_widget, QTextEdit):
            text = self.input_widget.toPlainText()
            self.value_changed.emit(text)

            self.validation_timer.stop()
            self.validation_timer.start(500)  # 文本编辑器延迟更长

    def on_slider_changed(self, value: int):
        """滑块改变处理"""
        self.value_changed.emit(str(value))
        self.perform_validation()

    def on_editing_finished(self):
        """编辑完成处理"""
        self.perform_validation()

    def perform_validation(self):
        """执行验证"""
        try:
            value = self.get_value()
            context = self.get_validation_context()

            self.validation_result = self.validator.validate(value, context)
            self.update_ui_state()
            self.validation_changed.emit(self.validation_result)

        except Exception as e:
            logger.error(f"验证执行失败: {e}")

    def get_value(self) -> str:
        """获取输入值"""
        if isinstance(self.input_widget, QLineEdit):
            return self.input_widget.text()
        elif isinstance(self.input_widget, QTextEdit):
            return self.input_widget.toPlainText()
        elif isinstance(self.input_widget, QSlider):
            return str(self.input_widget.value())
        else:
            return ""

    def set_value(self, value: str):
        """设置输入值"""
        if isinstance(self.input_widget, QLineEdit):
            self.input_widget.setText(value)
        elif isinstance(self.input_widget, QTextEdit):
            self.input_widget.setPlainText(value)
        elif isinstance(self.input_widget, QSlider):
            try:
                self.input_widget.setValue(int(value))
            except ValueError:
                pass

    def get_validation_context(self) -> Dict[str, Any]:
        """获取验证上下文"""
        return {
            'field_name': self.objectName(),
            'input_type': self.input_type.value
        }

    def set_validation_context(self, context: Dict[str, Any]):
        """设置验证上下文"""
        self.validator.context.update(context)

    def update_ui_state(self):
        """更新UI状态"""
        result = self.validation_result

        # 更新边框颜色
        border_colors = {
            ValidationLevel.SUCCESS: "#4caf50",
            ValidationLevel.INFO: "#2196f3",
            ValidationLevel.WARNING: "#ff9800",
            ValidationLevel.ERROR: "#f44336",
            ValidationLevel.CRITICAL: "#d32f2f"
        }

        border_color = border_colors.get(result.level, "#e0e0e0")

        # 更新输入容器样式
        input_container = self.findChild(QFrame)
        if input_container:
            input_container.setStyleSheet(f"""
                QFrame {{
                    border: 2px solid {border_color};
                    border-radius: 6px;
                    background-color: white;
                }}
                QFrame:focus-within {{
                    border-color: {border_color};
                    box-shadow: 0 0 0 2px {border_color}33;
                }}
            """)

        # 更新状态图标
        icons = {
            ValidationLevel.SUCCESS: "✅",
            ValidationLevel.INFO: "ℹ️",
            ValidationLevel.WARNING: "⚠️",
            ValidationLevel.ERROR: "❌",
            ValidationLevel.CRITICAL: "🚨"
        }

        if result.is_valid or result.level == ValidationLevel.INFO:
            self.status_icon.setText(icons.get(result.level, ""))
        else:
            self.status_icon.setText(icons.get(result.level, "❌"))

        # 更新消息
        if result.message:
            self.message_label.setText(result.message)
            self.message_label.setStyleSheet(f"""
                color: {border_color};
                font-size: 11px;
                margin: 2px 4px;
                font-weight: {'bold' if result.level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL] else 'normal'};
            """)
            self.message_label.show()
        else:
            self.message_label.hide()

        # 更新建议
        if result.suggestions:
            suggestions_text = "\n".join(f"• {suggestion}" for suggestion in result.suggestions)
            self.suggestions_list.setText(suggestions_text)
            self.suggestions_widget.show()
        else:
            self.suggestions_widget.hide()

    def is_valid(self) -> bool:
        """检查是否有效"""
        return self.validation_result.is_valid

    def get_validation_result(self) -> ValidationResult:
        """获取验证结果"""
        return self.validation_result

    def clear_validation(self):
        """清除验证状态"""
        self.validation_result = ValidationResult(True, ValidationLevel.SUCCESS, "")
        self.update_ui_state()


class ValidationManager(QObject):
    """验证管理器"""

    validation_changed = pyqtSignal(str, ValidationResult)  # 字段名, 验证结果
    form_validation_changed = pyqtSignal(bool)  # 表单是否有效

    def __init__(self):
        super().__init__()
        self.widgets: Dict[str, SmartInputWidget] = {}
        self.validation_results: Dict[str, ValidationResult] = {}
        self.global_validators: List[Callable] = []

        logger.info("验证管理器初始化完成")

    def register_widget(self, field_name: str, widget: SmartInputWidget):
        """注册输入组件"""
        self.widgets[field_name] = widget
        widget.validation_changed.connect(
            lambda result, name=field_name: self.on_widget_validation_changed(name, result)
        )

        logger.debug(f"注册输入组件: {field_name}")

    def unregister_widget(self, field_name: str):
        """注销输入组件"""
        if field_name in self.widgets:
            del self.widgets[field_name]
            if field_name in self.validation_results:
                del self.validation_results[field_name]

            logger.debug(f"注销输入组件: {field_name}")

    def on_widget_validation_changed(self, field_name: str, result: ValidationResult):
        """组件验证状态改变"""
        self.validation_results[field_name] = result
        self.validation_changed.emit(field_name, result)

        # 检查整体表单有效性
        is_form_valid = self.is_form_valid()
        self.form_validation_changed.emit(is_form_valid)

    def is_form_valid(self) -> bool:
        """检查表单是否有效"""
        # 检查所有组件验证结果
        for result in self.validation_results.values():
            if not result.is_valid:
                return False

        # 执行全局验证
        for validator in self.global_validators:
            try:
                if not validator(self.get_form_data()):
                    return False
            except Exception as e:
                logger.error(f"全局验证器执行失败: {e}")
                return False

        return True

    def get_form_data(self) -> Dict[str, str]:
        """获取表单数据"""
        data = {}
        for field_name, widget in self.widgets.items():
            data[field_name] = widget.get_value()
        return data

    def set_form_data(self, data: Dict[str, str]):
        """设置表单数据"""
        for field_name, value in data.items():
            if field_name in self.widgets:
                self.widgets[field_name].set_value(value)

    def validate_all(self) -> Dict[str, ValidationResult]:
        """验证所有字段"""
        results = {}
        for field_name, widget in self.widgets.items():
            widget.perform_validation()
            results[field_name] = widget.get_validation_result()

        return results

    def get_validation_summary(self) -> Dict[str, Any]:
        """获取验证摘要"""
        total_fields = len(self.widgets)
        valid_fields = sum(1 for result in self.validation_results.values() if result.is_valid)

        error_count = sum(1 for result in self.validation_results.values()
                         if not result.is_valid and result.level == ValidationLevel.ERROR)
        warning_count = sum(1 for result in self.validation_results.values()
                           if result.level == ValidationLevel.WARNING)

        return {
            'total_fields': total_fields,
            'valid_fields': valid_fields,
            'invalid_fields': total_fields - valid_fields,
            'error_count': error_count,
            'warning_count': warning_count,
            'is_form_valid': self.is_form_valid(),
            'completion_rate': valid_fields / total_fields if total_fields > 0 else 0
        }

    def add_global_validator(self, validator: Callable):
        """添加全局验证器"""
        self.global_validators.append(validator)

    def clear_all_validation(self):
        """清除所有验证状态"""
        for widget in self.widgets.values():
            widget.clear_validation()

        self.validation_results.clear()

    def get_first_invalid_field(self) -> Optional[str]:
        """获取第一个无效字段"""
        for field_name, result in self.validation_results.items():
            if not result.is_valid:
                return field_name
        return None

    def focus_first_invalid_field(self):
        """聚焦到第一个无效字段"""
        field_name = self.get_first_invalid_field()
        if field_name and field_name in self.widgets:
            widget = self.widgets[field_name]
            widget.input_widget.setFocus()


class SmartSuggestionSystem:
    """智能建议系统"""

    def __init__(self):
        self.suggestion_templates = self.initialize_suggestion_templates()
        self.context_analyzers = self.setup_context_analyzers()

        logger.info("智能建议系统初始化完成")

    def initialize_suggestion_templates(self) -> Dict[str, List[str]]:
        """初始化建议模板"""
        return {
            "api_key_format": [
                "API密钥格式通常为: 服务前缀 + 随机字符串",
                "Gemini: AIza... | OpenAI: sk-... | Claude: sk-ant-...",
                "确保复制完整的密钥，不要包含多余的空格"
            ],
            "animation_description": [
                "描述动画时，建议包含: 对象 + 动作 + 效果",
                "示例: '小球从左到右移动，带有弹跳效果'",
                "添加时间信息: '在2秒内完成动画'",
                "指定视觉效果: '带有渐变色彩变化'"
            ],
            "number_range": [
                "数值超出推荐范围可能影响效果",
                "建议使用常见的数值范围",
                "可以尝试使用百分比或相对单位"
            ],
            "file_path": [
                "确保文件路径存在且可访问",
                "使用正斜杠(/)或双反斜杠(\\\\)作为路径分隔符",
                "避免使用包含特殊字符的路径"
            ],
            "performance_optimization": [
                "复杂动画可能影响性能",
                "建议分解为多个简单动画",
                "考虑使用硬件加速选项"
            ]
        }

    def setup_context_analyzers(self) -> Dict[str, Callable]:
        """设置上下文分析器"""
        return {
            "api_key": self.analyze_api_key_context,
            "animation_desc": self.analyze_animation_context,
            "number": self.analyze_number_context,
            "file_path": self.analyze_file_path_context
        }

    def generate_suggestions(self, input_type: InputType, value: str,
                           validation_result: ValidationResult,
                           context: Dict[str, Any] = None) -> List[str]:
        """生成智能建议"""
        suggestions = []

        try:
            # 基于验证结果的建议
            if validation_result.suggestions:
                suggestions.extend(validation_result.suggestions)

            # 基于输入类型的建议
            type_key = input_type.value
            if type_key in self.suggestion_templates:
                suggestions.extend(self.suggestion_templates[type_key])

            # 基于上下文的建议
            analyzer = self.context_analyzers.get(type_key)
            if analyzer and context:
                context_suggestions = analyzer(value, context)
                suggestions.extend(context_suggestions)

            # 去重并限制数量
            unique_suggestions = list(dict.fromkeys(suggestions))
            return unique_suggestions[:5]  # 最多5个建议

        except Exception as e:
            logger.error(f"生成建议失败: {e}")
            return []

    def analyze_api_key_context(self, value: str, context: Dict[str, Any]) -> List[str]:
        """分析API密钥上下文"""
        suggestions = []

        service = context.get('service', '').lower()
        if service and value:
            if service == 'gemini' and not value.startswith('AIza'):
                suggestions.append("Gemini API密钥应以'AIza'开头")
            elif service == 'openai' and not value.startswith('sk-'):
                suggestions.append("OpenAI API密钥应以'sk-'开头")
            elif service == 'claude' and not value.startswith('sk-ant-'):
                suggestions.append("Claude API密钥应以'sk-ant-'开头")

        return suggestions

    def analyze_animation_context(self, value: str, context: Dict[str, Any]) -> List[str]:
        """分析动画描述上下文"""
        suggestions = []

        if value:
            # 检查描述长度
            if len(value) < 20:
                suggestions.append("建议提供更详细的动画描述")

            # 检查关键词
            action_words = ["移动", "旋转", "缩放", "淡入", "淡出"]
            if not any(word in value for word in action_words):
                suggestions.append("建议添加具体的动作描述")

            # 检查时间信息
            time_words = ["秒", "毫秒", "快速", "慢速", "持续"]
            if not any(word in value for word in time_words):
                suggestions.append("建议添加时间相关的描述")

        return suggestions

    def analyze_number_context(self, value: str, context: Dict[str, Any]) -> List[str]:
        """分析数字上下文"""
        suggestions = []

        try:
            if value:
                num_value = float(value)
                field_type = context.get('field_type', '')

                if field_type == 'duration' and num_value > 10:
                    suggestions.append("动画时长超过10秒可能过长")
                elif field_type == 'opacity' and (num_value < 0 or num_value > 1):
                    suggestions.append("透明度值应在0-1之间")
                elif field_type == 'angle' and abs(num_value) > 360:
                    suggestions.append("角度值通常在-360到360度之间")

        except ValueError:
            pass

        return suggestions

    def analyze_file_path_context(self, value: str, context: Dict[str, Any]) -> List[str]:
        """分析文件路径上下文"""
        suggestions = []

        if value:
            # 检查路径格式
            if '\\' in value and '/' in value:
                suggestions.append("建议统一使用一种路径分隔符")

            # 检查文件扩展名
            expected_ext = context.get('expected_extension')
            if expected_ext and not value.lower().endswith(expected_ext.lower()):
                suggestions.append(f"建议使用{expected_ext}格式的文件")

        return suggestions


class PreventiveErrorIntegrator:
    """预防性错误系统集成器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.validation_manager = ValidationManager()
        self.suggestion_system = SmartSuggestionSystem()
        self.integrated_forms: Dict[str, ValidationManager] = {}

        # 连接信号
        self.validation_manager.form_validation_changed.connect(self.handle_form_validation_changed)

        logger.info("预防性错误系统集成器初始化完成")

    def integrate_preventive_error_system(self):
        """集成预防性错误系统"""
        try:
            # 集成到现有表单
            self.integrate_existing_forms()

            # 集成智能建议
            self.integrate_smart_suggestions()

            # 集成实时验证
            self.integrate_real_time_validation()

            # 集成错误预防提示
            self.integrate_error_prevention_tips()

            logger.info("预防性错误系统集成完成")
            return True

        except Exception as e:
            logger.error(f"预防性错误系统集成失败: {e}")
            return False

    def integrate_existing_forms(self):
        """集成现有表单"""
        try:
            # AI配置表单
            self.integrate_ai_config_form()

            # 项目设置表单
            self.integrate_project_settings_form()

            # 动画参数表单
            self.integrate_animation_params_form()

            logger.info("现有表单集成完成")

        except Exception as e:
            logger.error(f"现有表单集成失败: {e}")

    def integrate_ai_config_form(self):
        """集成AI配置表单"""
        try:
            if hasattr(self.main_window, 'ai_config_widget'):
                config_widget = self.main_window.ai_config_widget
                form_manager = ValidationManager()

                # 查找API密钥输入框
                api_key_inputs = config_widget.findChildren(QLineEdit)
                for input_widget in api_key_inputs:
                    if 'api_key' in input_widget.objectName().lower():
                        # 替换为智能输入组件
                        smart_widget = SmartInputWidget(InputType.API_KEY)
                        smart_widget.set_validation_context({
                            'service': self.extract_service_from_name(input_widget.objectName())
                        })

                        # 替换原始组件
                        self.replace_widget(input_widget, smart_widget)
                        form_manager.register_widget(input_widget.objectName(), smart_widget)

                self.integrated_forms['ai_config'] = form_manager
                logger.info("AI配置表单集成完成")

        except Exception as e:
            logger.error(f"AI配置表单集成失败: {e}")

    def integrate_project_settings_form(self):
        """集成项目设置表单"""
        try:
            if hasattr(self.main_window, 'project_settings_widget'):
                settings_widget = self.main_window.project_settings_widget
                form_manager = ValidationManager()

                # 查找数字输入框
                number_inputs = settings_widget.findChildren(QSpinBox) + settings_widget.findChildren(QDoubleSpinBox)
                for input_widget in number_inputs:
                    smart_widget = SmartInputWidget(InputType.NUMBER)
                    smart_widget.set_validation_context({
                        'min_value': input_widget.minimum(),
                        'max_value': input_widget.maximum(),
                        'field_type': self.extract_field_type_from_name(input_widget.objectName())
                    })

                    self.replace_widget(input_widget, smart_widget)
                    form_manager.register_widget(input_widget.objectName(), smart_widget)

                self.integrated_forms['project_settings'] = form_manager
                logger.info("项目设置表单集成完成")

        except Exception as e:
            logger.error(f"项目设置表单集成失败: {e}")

    def integrate_animation_params_form(self):
        """集成动画参数表单"""
        try:
            if hasattr(self.main_window, 'animation_params_widget'):
                params_widget = self.main_window.animation_params_widget
                form_manager = ValidationManager()

                # 查找动画描述输入框
                text_inputs = params_widget.findChildren(QTextEdit)
                for input_widget in text_inputs:
                    if 'description' in input_widget.objectName().lower():
                        smart_widget = SmartInputWidget(InputType.ANIMATION_DESC)

                        self.replace_widget(input_widget, smart_widget)
                        form_manager.register_widget(input_widget.objectName(), smart_widget)

                self.integrated_forms['animation_params'] = form_manager
                logger.info("动画参数表单集成完成")

        except Exception as e:
            logger.error(f"动画参数表单集成失败: {e}")

    def integrate_smart_suggestions(self):
        """集成智能建议"""
        try:
            # 为所有智能输入组件添加建议功能
            for form_name, form_manager in self.integrated_forms.items():
                for field_name, widget in form_manager.widgets.items():
                    widget.validation_changed.connect(
                        lambda result, w=widget: self.update_widget_suggestions(w, result)
                    )

            logger.info("智能建议集成完成")

        except Exception as e:
            logger.error(f"智能建议集成失败: {e}")

    def integrate_real_time_validation(self):
        """集成实时验证"""
        try:
            # 设置实时验证触发器
            for form_manager in self.integrated_forms.values():
                form_manager.form_validation_changed.connect(self.handle_form_validation_changed)

            logger.info("实时验证集成完成")

        except Exception as e:
            logger.error(f"实时验证集成失败: {e}")

    def integrate_error_prevention_tips(self):
        """集成错误预防提示"""
        try:
            # 添加预防性提示到主界面
            if hasattr(self.main_window, 'add_prevention_tips'):
                self.main_window.add_prevention_tips(self.create_prevention_tips())

            logger.info("错误预防提示集成完成")

        except Exception as e:
            logger.error(f"错误预防提示集成失败: {e}")

    def replace_widget(self, old_widget: QWidget, new_widget: QWidget):
        """替换组件"""
        try:
            parent = old_widget.parent()
            if parent and hasattr(parent, 'layout') and parent.layout():
                layout = parent.layout()

                # 找到旧组件的位置
                for i in range(layout.count()):
                    if layout.itemAt(i).widget() == old_widget:
                        # 移除旧组件
                        layout.removeWidget(old_widget)
                        old_widget.setParent(None)

                        # 插入新组件
                        layout.insertWidget(i, new_widget)
                        break

        except Exception as e:
            logger.error(f"替换组件失败: {e}")

    def extract_service_from_name(self, name: str) -> str:
        """从名称提取服务类型"""
        name_lower = name.lower()
        if 'gemini' in name_lower:
            return 'gemini'
        elif 'openai' in name_lower:
            return 'openai'
        elif 'claude' in name_lower:
            return 'claude'
        return ''

    def extract_field_type_from_name(self, name: str) -> str:
        """从名称提取字段类型"""
        name_lower = name.lower()
        if 'duration' in name_lower or 'time' in name_lower:
            return 'duration'
        elif 'opacity' in name_lower or 'alpha' in name_lower:
            return 'opacity'
        elif 'angle' in name_lower or 'rotation' in name_lower:
            return 'angle'
        return ''

    def update_widget_suggestions(self, widget: SmartInputWidget, result: ValidationResult):
        """更新组件建议"""
        try:
            suggestions = self.suggestion_system.generate_suggestions(
                widget.input_type, widget.get_value(), result, widget.get_validation_context()
            )

            # 更新建议显示
            if suggestions:
                result.suggestions = suggestions
                widget.validation_result = result
                widget.update_ui_state()

        except Exception as e:
            logger.error(f"更新组件建议失败: {e}")

    def handle_form_validation_changed(self, is_valid: bool):
        """处理表单验证状态改变"""
        try:
            # 更新主界面状态
            if hasattr(self.main_window, 'update_form_validation_status'):
                self.main_window.update_form_validation_status(is_valid)

            # 启用/禁用提交按钮
            self.update_submit_buttons(is_valid)

        except Exception as e:
            logger.error(f"处理表单验证状态改变失败: {e}")

    def update_submit_buttons(self, is_valid: bool):
        """更新提交按钮状态"""
        try:
            # 查找所有提交按钮
            submit_buttons = self.main_window.findChildren(QPushButton)
            for button in submit_buttons:
                if any(keyword in button.text().lower() for keyword in ['提交', '确定', '保存', '应用']):
                    button.setEnabled(is_valid)

                    # 更新按钮样式
                    if is_valid:
                        button.setStyleSheet("QPushButton { background-color: #4caf50; color: white; }")
                    else:
                        button.setStyleSheet("QPushButton { background-color: #cccccc; color: #666666; }")

        except Exception as e:
            logger.error(f"更新提交按钮状态失败: {e}")

    def create_prevention_tips(self) -> List[str]:
        """创建预防提示"""
        return [
            "💡 输入API密钥时，确保复制完整且无多余空格",
            "🎯 描述动画时，包含对象、动作和效果三要素",
            "📊 数值输入支持表达式计算，如 '100*0.8' 或 'sin(45)'",
            "⚠️ 文件路径建议使用绝对路径，避免特殊字符",
            "🔍 实时验证会在输入时提供即时反馈和建议"
        ]

    def get_validation_summary(self) -> Dict[str, Any]:
        """获取验证摘要"""
        total_forms = len(self.integrated_forms)
        valid_forms = sum(1 for manager in self.integrated_forms.values() if manager.is_form_valid())

        all_results = {}
        for form_name, manager in self.integrated_forms.items():
            all_results[form_name] = manager.get_validation_summary()

        return {
            'total_forms': total_forms,
            'valid_forms': valid_forms,
            'form_details': all_results,
            'overall_valid': valid_forms == total_forms
        }

    def export_validation_config(self, file_path: str):
        """导出验证配置"""
        try:
            config = {
                'integrated_forms': list(self.integrated_forms.keys()),
                'validation_summary': self.get_validation_summary(),
                'suggestion_templates': self.suggestion_system.suggestion_templates,
                'export_time': datetime.now().isoformat()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            logger.info(f"验证配置已导出到: {file_path}")

        except Exception as e:
            logger.error(f"导出验证配置失败: {e}")
