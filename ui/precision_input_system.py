"""
AI Animation Studio - 多精度输入支持系统
实现专业级数值控制，支持多种精度输入方式
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QSlider, QSpinBox, QDoubleSpinBox, QComboBox,
                             QFrame, QGroupBox, QFormLayout, QDialog, QTextEdit,
                             QCheckBox, QButtonGroup, QRadioButton, QTabWidget,
                             QScrollArea, QSplitter, QApplication, QMenu, QAction)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PyQt6.QtGui import (QValidator, QDoubleValidator, QIntValidator, QFont, QColor,
                         QPainter, QPen, QBrush, QCursor, QKeySequence, QAction as QGuiAction)

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
import math
import re
from dataclasses import dataclass

from core.logger import get_logger

logger = get_logger("precision_input_system")


class InputPrecisionLevel(Enum):
    """输入精度级别枚举"""
    COARSE = "coarse"           # 粗调 - 整数或1位小数
    NORMAL = "normal"           # 普通 - 2位小数
    FINE = "fine"               # 精调 - 3-4位小数
    ULTRA_FINE = "ultra_fine"   # 超精调 - 5+位小数


class InputMethod(Enum):
    """输入方法枚举"""
    DIRECT_INPUT = "direct_input"       # 直接输入
    SLIDER = "slider"                   # 滑块控制
    STEP_BUTTONS = "step_buttons"       # 步进按钮
    DRAG_ADJUST = "drag_adjust"         # 拖拽调整
    EXPRESSION = "expression"           # 表达式计算
    PRESET = "preset"                   # 预设值
    RELATIVE = "relative"               # 相对调整


class ValueType(Enum):
    """数值类型枚举"""
    INTEGER = "integer"         # 整数
    FLOAT = "float"            # 浮点数
    PERCENTAGE = "percentage"   # 百分比
    ANGLE = "angle"            # 角度
    TIME = "time"              # 时间
    PIXEL = "pixel"            # 像素
    RATIO = "ratio"            # 比例


@dataclass
class PrecisionConfig:
    """精度配置"""
    value_type: ValueType
    min_value: float
    max_value: float
    default_value: float
    precision_level: InputPrecisionLevel
    step_size: float
    unit: str = ""
    description: str = ""
    allowed_methods: List[InputMethod] = None
    
    def __post_init__(self):
        if self.allowed_methods is None:
            self.allowed_methods = list(InputMethod)


class ExpressionValidator(QValidator):
    """表达式验证器"""
    
    def __init__(self, min_val: float = -999999, max_val: float = 999999):
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val
    
    def validate(self, input_str: str, pos: int) -> Tuple[QValidator.State, str, int]:
        """验证输入"""
        if not input_str:
            return QValidator.State.Intermediate, input_str, pos
        
        # 允许数字、小数点、运算符、括号、常用函数
        allowed_pattern = r'^[0-9+\-*/().\s]*$|^[0-9+\-*/().\s]*[a-zA-Z]+[0-9+\-*/().\s]*$'
        
        if re.match(allowed_pattern, input_str):
            try:
                # 尝试计算表达式
                result = self.evaluate_expression(input_str)
                if result is not None and self.min_val <= result <= self.max_val:
                    return QValidator.State.Acceptable, input_str, pos
                else:
                    return QValidator.State.Intermediate, input_str, pos
            except:
                return QValidator.State.Intermediate, input_str, pos
        
        return QValidator.State.Invalid, input_str, pos
    
    def evaluate_expression(self, expression: str) -> Optional[float]:
        """安全计算表达式"""
        try:
            # 替换常用数学函数
            safe_expr = expression.replace('pi', str(math.pi))
            safe_expr = safe_expr.replace('e', str(math.e))
            
            # 只允许安全的数学运算
            allowed_names = {
                "__builtins__": {},
                "abs": abs, "round": round, "min": min, "max": max,
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "sqrt": math.sqrt, "pow": pow, "log": math.log,
                "pi": math.pi, "e": math.e
            }
            
            result = eval(safe_expr, allowed_names)
            return float(result)
        except:
            return None


class DragAdjustWidget(QWidget):
    """拖拽调整组件"""
    
    value_changed = pyqtSignal(float)
    
    def __init__(self, config: PrecisionConfig):
        super().__init__()
        self.config = config
        self.current_value = config.default_value
        self.is_dragging = False
        self.drag_start_pos = QPoint()
        self.drag_start_value = 0.0
        self.sensitivity = 1.0
        
        self.setFixedSize(60, 20)
        self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        self.setToolTip("拖拽调整数值")
    
    def paintEvent(self, event):
        """绘制组件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 背景
        rect = self.rect()
        if self.is_dragging:
            painter.fillRect(rect, QColor(200, 230, 255))
        else:
            painter.fillRect(rect, QColor(240, 240, 240))
        
        # 边框
        painter.setPen(QPen(QColor(180, 180, 180), 1))
        painter.drawRect(rect)
        
        # 拖拽指示器
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        center_y = rect.height() // 2
        for i in range(3):
            x = rect.width() // 2 - 6 + i * 6
            painter.drawLine(x, center_y - 3, x, center_y + 3)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_start_pos = event.position().toPoint()
            self.drag_start_value = self.current_value
            self.update()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_dragging:
            delta_x = event.position().toPoint().x() - self.drag_start_pos.x()
            
            # 根据精度级别调整敏感度
            sensitivity_map = {
                InputPrecisionLevel.COARSE: 1.0,
                InputPrecisionLevel.NORMAL: 0.1,
                InputPrecisionLevel.FINE: 0.01,
                InputPrecisionLevel.ULTRA_FINE: 0.001
            }
            
            sensitivity = sensitivity_map.get(self.config.precision_level, 0.1)
            delta_value = delta_x * sensitivity * self.config.step_size
            
            new_value = self.drag_start_value + delta_value
            new_value = max(self.config.min_value, min(self.config.max_value, new_value))
            
            if new_value != self.current_value:
                self.current_value = new_value
                self.value_changed.emit(new_value)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.update()
    
    def set_value(self, value: float):
        """设置数值"""
        self.current_value = value
        self.update()


class PrecisionSlider(QWidget):
    """精度滑块"""
    
    value_changed = pyqtSignal(float)
    
    def __init__(self, config: PrecisionConfig):
        super().__init__()
        self.config = config
        self.current_value = config.default_value
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 滑块
        self.slider = QSlider(Qt.Orientation.Horizontal)
        
        # 根据精度级别设置滑块范围
        precision_multiplier = {
            InputPrecisionLevel.COARSE: 1,
            InputPrecisionLevel.NORMAL: 100,
            InputPrecisionLevel.FINE: 1000,
            InputPrecisionLevel.ULTRA_FINE: 10000
        }
        
        multiplier = precision_multiplier.get(self.config.precision_level, 100)
        self.slider.setRange(
            int(self.config.min_value * multiplier),
            int(self.config.max_value * multiplier)
        )
        self.slider.setValue(int(self.config.default_value * multiplier))
        
        self.slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.slider)
        
        # 刻度标签
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel(f"{self.config.min_value}"))
        scale_layout.addStretch()
        scale_layout.addWidget(QLabel(f"{(self.config.min_value + self.config.max_value) / 2}"))
        scale_layout.addStretch()
        scale_layout.addWidget(QLabel(f"{self.config.max_value}"))
        
        layout.addLayout(scale_layout)
    
    def on_slider_changed(self, value: int):
        """滑块值改变"""
        precision_multiplier = {
            InputPrecisionLevel.COARSE: 1,
            InputPrecisionLevel.NORMAL: 100,
            InputPrecisionLevel.FINE: 1000,
            InputPrecisionLevel.ULTRA_FINE: 10000
        }
        
        multiplier = precision_multiplier.get(self.config.precision_level, 100)
        real_value = value / multiplier
        
        if real_value != self.current_value:
            self.current_value = real_value
            self.value_changed.emit(real_value)
    
    def set_value(self, value: float):
        """设置数值"""
        precision_multiplier = {
            InputPrecisionLevel.COARSE: 1,
            InputPrecisionLevel.NORMAL: 100,
            InputPrecisionLevel.FINE: 1000,
            InputPrecisionLevel.ULTRA_FINE: 10000
        }
        
        multiplier = precision_multiplier.get(self.config.precision_level, 100)
        self.slider.setValue(int(value * multiplier))
        self.current_value = value


class ExpressionDialog(QDialog):
    """表达式输入对话框"""
    
    def __init__(self, config: PrecisionConfig, current_value: float, parent=None):
        super().__init__(parent)
        self.config = config
        self.current_value = current_value
        self.result_value = current_value
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("表达式计算器")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 说明
        info_label = QLabel("支持基本数学运算和函数：+, -, *, /, (), sin, cos, tan, sqrt, log, pi, e")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # 当前值显示
        current_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("当前值:"))
        current_value_label = QLabel(f"{self.current_value}")
        current_value_label.setStyleSheet("font-weight: bold; color: #2C5AA0;")
        current_layout.addWidget(current_value_label)
        current_layout.addStretch()
        layout.addLayout(current_layout)
        
        # 表达式输入
        layout.addWidget(QLabel("表达式:"))
        self.expression_input = QLineEdit()
        self.expression_input.setValidator(ExpressionValidator(self.config.min_value, self.config.max_value))
        self.expression_input.setText(str(self.current_value))
        self.expression_input.textChanged.connect(self.on_expression_changed)
        layout.addWidget(self.expression_input)
        
        # 结果显示
        layout.addWidget(QLabel("计算结果:"))
        self.result_label = QLabel(str(self.current_value))
        self.result_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2C5AA0; padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
        layout.addWidget(self.result_label)
        
        # 常用函数按钮
        functions_group = QGroupBox("常用函数")
        functions_layout = QHBoxLayout(functions_group)
        
        functions = [
            ("π", "pi"), ("e", "e"), ("√", "sqrt("), ("sin", "sin("),
            ("cos", "cos("), ("tan", "tan("), ("log", "log("), ("abs", "abs(")
        ]
        
        for display, func in functions:
            btn = QPushButton(display)
            btn.clicked.connect(lambda checked, f=func: self.insert_function(f))
            functions_layout.addWidget(btn)
        
        layout.addWidget(functions_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
        # 设置焦点
        self.expression_input.setFocus()
        self.expression_input.selectAll()
    
    def insert_function(self, func: str):
        """插入函数"""
        cursor_pos = self.expression_input.cursorPosition()
        current_text = self.expression_input.text()
        new_text = current_text[:cursor_pos] + func + current_text[cursor_pos:]
        self.expression_input.setText(new_text)
        self.expression_input.setCursorPosition(cursor_pos + len(func))
    
    def on_expression_changed(self, text: str):
        """表达式改变"""
        try:
            validator = ExpressionValidator(self.config.min_value, self.config.max_value)
            result = validator.evaluate_expression(text)
            
            if result is not None:
                self.result_value = result
                self.result_label.setText(f"{result:.6f}".rstrip('0').rstrip('.'))
                self.result_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2C5AA0; padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
            else:
                self.result_label.setText("无效表达式")
                self.result_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #d32f2f; padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
        except Exception as e:
            self.result_label.setText(f"错误: {str(e)}")
            self.result_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #d32f2f; padding: 5px; border: 1px solid #ddd; border-radius: 3px;")
    
    def get_result(self) -> float:
        """获取计算结果"""
        return self.result_value


class PrecisionInputWidget(QWidget):
    """多精度输入组件"""
    
    value_changed = pyqtSignal(float)
    precision_changed = pyqtSignal(InputPrecisionLevel)
    
    def __init__(self, config: PrecisionConfig):
        super().__init__()
        self.config = config
        self.current_value = config.default_value
        self.current_precision = config.precision_level
        
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题和精度选择
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.config.description or "数值输入")
        title_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 精度选择
        precision_combo = QComboBox()
        precision_combo.addItems(["粗调", "普通", "精调", "超精调"])
        precision_combo.setCurrentIndex(list(InputPrecisionLevel).index(self.current_precision))
        precision_combo.currentIndexChanged.connect(self.on_precision_changed)
        header_layout.addWidget(precision_combo)
        
        layout.addLayout(header_layout)
        
        # 主输入区域
        main_layout = QHBoxLayout()
        
        # 直接输入
        self.value_input = QLineEdit()
        self.value_input.setFixedWidth(80)
        self.setup_value_input()
        main_layout.addWidget(self.value_input)
        
        # 单位标签
        if self.config.unit:
            unit_label = QLabel(self.config.unit)
            unit_label.setStyleSheet("color: #666; margin-left: 2px;")
            main_layout.addWidget(unit_label)
        
        # 拖拽调整
        if InputMethod.DRAG_ADJUST in self.config.allowed_methods:
            self.drag_widget = DragAdjustWidget(self.config)
            self.drag_widget.value_changed.connect(self.on_drag_value_changed)
            main_layout.addWidget(self.drag_widget)
        
        # 步进按钮
        if InputMethod.STEP_BUTTONS in self.config.allowed_methods:
            step_layout = QVBoxLayout()
            step_layout.setSpacing(1)
            
            self.step_up_btn = QPushButton("▲")
            self.step_up_btn.setFixedSize(20, 12)
            self.step_up_btn.clicked.connect(self.step_up)
            step_layout.addWidget(self.step_up_btn)
            
            self.step_down_btn = QPushButton("▼")
            self.step_down_btn.setFixedSize(20, 12)
            self.step_down_btn.clicked.connect(self.step_down)
            step_layout.addWidget(self.step_down_btn)
            
            main_layout.addLayout(step_layout)
        
        # 表达式按钮
        if InputMethod.EXPRESSION in self.config.allowed_methods:
            self.expression_btn = QPushButton("fx")
            self.expression_btn.setFixedSize(24, 24)
            self.expression_btn.setToolTip("表达式计算器")
            self.expression_btn.clicked.connect(self.show_expression_dialog)
            main_layout.addWidget(self.expression_btn)
        
        # 预设按钮
        if InputMethod.PRESET in self.config.allowed_methods:
            self.preset_btn = QPushButton("⚙")
            self.preset_btn.setFixedSize(24, 24)
            self.preset_btn.setToolTip("预设值")
            self.preset_btn.clicked.connect(self.show_preset_menu)
            main_layout.addWidget(self.preset_btn)
        
        layout.addLayout(main_layout)
        
        # 滑块控制
        if InputMethod.SLIDER in self.config.allowed_methods:
            self.precision_slider = PrecisionSlider(self.config)
            self.precision_slider.value_changed.connect(self.on_slider_value_changed)
            layout.addWidget(self.precision_slider)
        
        # 设置初始值
        self.set_value(self.current_value)
    
    def setup_value_input(self):
        """设置数值输入框"""
        if self.config.value_type == ValueType.INTEGER:
            validator = QIntValidator(int(self.config.min_value), int(self.config.max_value))
        else:
            precision = {
                InputPrecisionLevel.COARSE: 1,
                InputPrecisionLevel.NORMAL: 2,
                InputPrecisionLevel.FINE: 4,
                InputPrecisionLevel.ULTRA_FINE: 6
            }.get(self.current_precision, 2)
            
            validator = QDoubleValidator(self.config.min_value, self.config.max_value, precision)
        
        self.value_input.setValidator(validator)
        self.value_input.setText(str(self.current_value))
    
    def connect_signals(self):
        """连接信号"""
        self.value_input.textChanged.connect(self.on_direct_input_changed)
        self.value_input.editingFinished.connect(self.on_editing_finished)
    
    def on_precision_changed(self, index: int):
        """精度改变"""
        precision_levels = list(InputPrecisionLevel)
        if 0 <= index < len(precision_levels):
            self.current_precision = precision_levels[index]
            self.precision_changed.emit(self.current_precision)
            
            # 更新验证器
            self.setup_value_input()
            
            # 更新滑块
            if hasattr(self, 'precision_slider'):
                self.precision_slider.config.precision_level = self.current_precision
    
    def on_direct_input_changed(self, text: str):
        """直接输入改变"""
        try:
            if self.config.value_type == ValueType.INTEGER:
                value = int(text) if text else 0
            else:
                value = float(text) if text else 0.0
            
            if self.config.min_value <= value <= self.config.max_value:
                self.current_value = value
                self.update_other_controls()
        except ValueError:
            pass
    
    def on_editing_finished(self):
        """编辑完成"""
        self.value_changed.emit(self.current_value)
    
    def on_drag_value_changed(self, value: float):
        """拖拽值改变"""
        self.set_value(value)
        self.value_changed.emit(value)
    
    def on_slider_value_changed(self, value: float):
        """滑块值改变"""
        self.set_value(value)
        self.value_changed.emit(value)
    
    def step_up(self):
        """步进增加"""
        new_value = self.current_value + self.config.step_size
        new_value = min(self.config.max_value, new_value)
        self.set_value(new_value)
        self.value_changed.emit(new_value)
    
    def step_down(self):
        """步进减少"""
        new_value = self.current_value - self.config.step_size
        new_value = max(self.config.min_value, new_value)
        self.set_value(new_value)
        self.value_changed.emit(new_value)
    
    def show_expression_dialog(self):
        """显示表达式对话框"""
        dialog = ExpressionDialog(self.config, self.current_value, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            self.set_value(result)
            self.value_changed.emit(result)
    
    def show_preset_menu(self):
        """显示预设菜单"""
        menu = QMenu(self)
        
        # 常用预设值
        presets = self.get_common_presets()
        for name, value in presets.items():
            action = menu.addAction(f"{name}: {value}")
            action.triggered.connect(lambda checked, v=value: self.set_preset_value(v))
        
        menu.addSeparator()
        
        # 重置到默认值
        reset_action = menu.addAction("重置到默认值")
        reset_action.triggered.connect(lambda: self.set_preset_value(self.config.default_value))
        
        menu.exec(self.preset_btn.mapToGlobal(self.preset_btn.rect().bottomLeft()))
    
    def get_common_presets(self) -> Dict[str, float]:
        """获取常用预设值"""
        presets = {}
        
        if self.config.value_type == ValueType.PERCENTAGE:
            presets = {"0%": 0, "25%": 25, "50%": 50, "75%": 75, "100%": 100}
        elif self.config.value_type == ValueType.ANGLE:
            presets = {"0°": 0, "45°": 45, "90°": 90, "180°": 180, "270°": 270, "360°": 360}
        elif self.config.value_type == ValueType.RATIO:
            presets = {"1:1": 1.0, "4:3": 1.333, "16:9": 1.778, "21:9": 2.333}
        else:
            # 基于范围生成预设
            range_size = self.config.max_value - self.config.min_value
            presets = {
                "最小值": self.config.min_value,
                "1/4": self.config.min_value + range_size * 0.25,
                "中间值": self.config.min_value + range_size * 0.5,
                "3/4": self.config.min_value + range_size * 0.75,
                "最大值": self.config.max_value
            }
        
        return presets
    
    def set_preset_value(self, value: float):
        """设置预设值"""
        self.set_value(value)
        self.value_changed.emit(value)
    
    def set_value(self, value: float):
        """设置数值"""
        value = max(self.config.min_value, min(self.config.max_value, value))
        self.current_value = value
        
        # 更新输入框
        if self.config.value_type == ValueType.INTEGER:
            self.value_input.setText(str(int(value)))
        else:
            precision = {
                InputPrecisionLevel.COARSE: 1,
                InputPrecisionLevel.NORMAL: 2,
                InputPrecisionLevel.FINE: 4,
                InputPrecisionLevel.ULTRA_FINE: 6
            }.get(self.current_precision, 2)
            
            self.value_input.setText(f"{value:.{precision}f}".rstrip('0').rstrip('.'))
        
        self.update_other_controls()
    
    def update_other_controls(self):
        """更新其他控件"""
        # 更新拖拽组件
        if hasattr(self, 'drag_widget'):
            self.drag_widget.set_value(self.current_value)
        
        # 更新滑块
        if hasattr(self, 'precision_slider'):
            self.precision_slider.set_value(self.current_value)
    
    def get_value(self) -> float:
        """获取当前值"""
        return self.current_value
    
    def get_precision_level(self) -> InputPrecisionLevel:
        """获取精度级别"""
        return self.current_precision


class PrecisionInputManager(QObject):
    """多精度输入管理器"""

    value_changed = pyqtSignal(str, float)  # 参数ID, 新值
    batch_values_changed = pyqtSignal(dict)  # 批量值改变

    def __init__(self):
        super().__init__()
        self.input_widgets: Dict[str, PrecisionInputWidget] = {}
        self.parameter_configs: Dict[str, PrecisionConfig] = {}
        self.parameter_groups: Dict[str, List[str]] = {}
        self.linked_parameters: Dict[str, List[str]] = {}

        self.initialize_default_configs()

        logger.info("多精度输入管理器初始化完成")

    def initialize_default_configs(self):
        """初始化默认配置"""
        self.parameter_configs = {
            # 位置参数
            "position_x": PrecisionConfig(
                ValueType.PIXEL, -9999, 9999, 0, InputPrecisionLevel.NORMAL, 1.0,
                "px", "X坐标位置"
            ),
            "position_y": PrecisionConfig(
                ValueType.PIXEL, -9999, 9999, 0, InputPrecisionLevel.NORMAL, 1.0,
                "px", "Y坐标位置"
            ),

            # 尺寸参数
            "width": PrecisionConfig(
                ValueType.PIXEL, 1, 9999, 100, InputPrecisionLevel.NORMAL, 1.0,
                "px", "宽度"
            ),
            "height": PrecisionConfig(
                ValueType.PIXEL, 1, 9999, 100, InputPrecisionLevel.NORMAL, 1.0,
                "px", "高度"
            ),

            # 变换参数
            "scale_x": PrecisionConfig(
                ValueType.RATIO, 0.01, 10.0, 1.0, InputPrecisionLevel.FINE, 0.01,
                "", "水平缩放"
            ),
            "scale_y": PrecisionConfig(
                ValueType.RATIO, 0.01, 10.0, 1.0, InputPrecisionLevel.FINE, 0.01,
                "", "垂直缩放"
            ),
            "rotation": PrecisionConfig(
                ValueType.ANGLE, 0, 360, 0, InputPrecisionLevel.NORMAL, 1.0,
                "°", "旋转角度"
            ),
            "skew_x": PrecisionConfig(
                ValueType.ANGLE, -45, 45, 0, InputPrecisionLevel.FINE, 0.1,
                "°", "水平倾斜"
            ),
            "skew_y": PrecisionConfig(
                ValueType.ANGLE, -45, 45, 0, InputPrecisionLevel.FINE, 0.1,
                "°", "垂直倾斜"
            ),

            # 透明度和颜色
            "opacity": PrecisionConfig(
                ValueType.PERCENTAGE, 0, 100, 100, InputPrecisionLevel.NORMAL, 1.0,
                "%", "透明度"
            ),

            # 时间参数
            "start_time": PrecisionConfig(
                ValueType.TIME, 0, 3600, 0, InputPrecisionLevel.FINE, 0.1,
                "s", "开始时间"
            ),
            "end_time": PrecisionConfig(
                ValueType.TIME, 0, 3600, 1, InputPrecisionLevel.FINE, 0.1,
                "s", "结束时间"
            ),
            "duration": PrecisionConfig(
                ValueType.TIME, 0.1, 3600, 1, InputPrecisionLevel.FINE, 0.1,
                "s", "持续时间"
            ),

            # 动画参数
            "ease_strength": PrecisionConfig(
                ValueType.FLOAT, 0.0, 2.0, 1.0, InputPrecisionLevel.FINE, 0.01,
                "", "缓动强度"
            ),
            "delay": PrecisionConfig(
                ValueType.TIME, 0, 60, 0, InputPrecisionLevel.FINE, 0.01,
                "s", "延迟时间"
            ),

            # 边框和阴影
            "border_width": PrecisionConfig(
                ValueType.PIXEL, 0, 50, 1, InputPrecisionLevel.NORMAL, 0.5,
                "px", "边框宽度"
            ),
            "border_radius": PrecisionConfig(
                ValueType.PIXEL, 0, 100, 0, InputPrecisionLevel.NORMAL, 1.0,
                "px", "圆角半径"
            ),
            "shadow_blur": PrecisionConfig(
                ValueType.PIXEL, 0, 50, 0, InputPrecisionLevel.NORMAL, 1.0,
                "px", "阴影模糊"
            ),
            "shadow_offset_x": PrecisionConfig(
                ValueType.PIXEL, -50, 50, 0, InputPrecisionLevel.NORMAL, 1.0,
                "px", "阴影X偏移"
            ),
            "shadow_offset_y": PrecisionConfig(
                ValueType.PIXEL, -50, 50, 0, InputPrecisionLevel.NORMAL, 1.0,
                "px", "阴影Y偏移"
            )
        }

        # 参数分组
        self.parameter_groups = {
            "位置": ["position_x", "position_y"],
            "尺寸": ["width", "height"],
            "缩放": ["scale_x", "scale_y"],
            "变换": ["rotation", "skew_x", "skew_y"],
            "时间": ["start_time", "end_time", "duration", "delay"],
            "样式": ["opacity", "border_width", "border_radius"],
            "阴影": ["shadow_blur", "shadow_offset_x", "shadow_offset_y"],
            "动画": ["ease_strength"]
        }

        # 参数链接（一个参数改变时同步改变其他参数）
        self.linked_parameters = {
            "scale_x": ["scale_y"],  # 等比缩放
        }

    def create_input_widget(self, parameter_id: str, config: PrecisionConfig = None) -> PrecisionInputWidget:
        """创建输入组件"""
        if config is None:
            config = self.parameter_configs.get(parameter_id)
            if config is None:
                logger.warning(f"未找到参数配置: {parameter_id}")
                config = PrecisionConfig(ValueType.FLOAT, 0, 100, 0, InputPrecisionLevel.NORMAL, 1.0)

        widget = PrecisionInputWidget(config)
        widget.value_changed.connect(lambda value: self.on_value_changed(parameter_id, value))
        widget.precision_changed.connect(lambda precision: self.on_precision_changed(parameter_id, precision))

        self.input_widgets[parameter_id] = widget

        logger.debug(f"创建输入组件: {parameter_id}")
        return widget

    def on_value_changed(self, parameter_id: str, value: float):
        """参数值改变"""
        try:
            # 发送单个参数改变信号
            self.value_changed.emit(parameter_id, value)

            # 处理链接参数
            if parameter_id in self.linked_parameters:
                linked_values = {}
                for linked_id in self.linked_parameters[parameter_id]:
                    if linked_id in self.input_widgets:
                        self.input_widgets[linked_id].set_value(value)
                        linked_values[linked_id] = value

                # 发送批量改变信号
                if linked_values:
                    linked_values[parameter_id] = value
                    self.batch_values_changed.emit(linked_values)

            logger.debug(f"参数值改变: {parameter_id} = {value}")

        except Exception as e:
            logger.error(f"处理参数值改变失败 {parameter_id}: {e}")

    def on_precision_changed(self, parameter_id: str, precision: InputPrecisionLevel):
        """精度改变"""
        logger.debug(f"参数精度改变: {parameter_id} = {precision.value}")

    def set_parameter_value(self, parameter_id: str, value: float):
        """设置参数值"""
        if parameter_id in self.input_widgets:
            self.input_widgets[parameter_id].set_value(value)

    def get_parameter_value(self, parameter_id: str) -> Optional[float]:
        """获取参数值"""
        if parameter_id in self.input_widgets:
            return self.input_widgets[parameter_id].get_value()
        return None

    def set_parameter_values(self, values: Dict[str, float]):
        """批量设置参数值"""
        for parameter_id, value in values.items():
            self.set_parameter_value(parameter_id, value)

    def get_parameter_values(self, parameter_ids: List[str] = None) -> Dict[str, float]:
        """获取参数值"""
        if parameter_ids is None:
            parameter_ids = list(self.input_widgets.keys())

        values = {}
        for parameter_id in parameter_ids:
            value = self.get_parameter_value(parameter_id)
            if value is not None:
                values[parameter_id] = value

        return values

    def create_parameter_group_widget(self, group_name: str) -> QWidget:
        """创建参数组组件"""
        if group_name not in self.parameter_groups:
            logger.warning(f"未找到参数组: {group_name}")
            return QWidget()

        group_widget = QGroupBox(group_name)
        layout = QFormLayout(group_widget)

        for parameter_id in self.parameter_groups[group_name]:
            config = self.parameter_configs.get(parameter_id)
            if config:
                input_widget = self.create_input_widget(parameter_id, config)
                layout.addRow(config.description + ":", input_widget)

        return group_widget

    def create_complete_properties_panel(self) -> QWidget:
        """创建完整属性面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # 创建各个参数组
        for group_name in self.parameter_groups.keys():
            group_widget = self.create_parameter_group_widget(group_name)
            scroll_layout.addWidget(group_widget)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        return panel

    def create_tabbed_properties_panel(self) -> QWidget:
        """创建分标签页属性面板"""
        tab_widget = QTabWidget()

        # 基础属性标签页
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)

        for group_name in ["位置", "尺寸", "变换"]:
            if group_name in self.parameter_groups:
                group_widget = self.create_parameter_group_widget(group_name)
                basic_layout.addWidget(group_widget)

        basic_layout.addStretch()
        tab_widget.addTab(basic_tab, "基础")

        # 样式属性标签页
        style_tab = QWidget()
        style_layout = QVBoxLayout(style_tab)

        for group_name in ["样式", "阴影"]:
            if group_name in self.parameter_groups:
                group_widget = self.create_parameter_group_widget(group_name)
                style_layout.addWidget(group_widget)

        style_layout.addStretch()
        tab_widget.addTab(style_tab, "样式")

        # 动画属性标签页
        animation_tab = QWidget()
        animation_layout = QVBoxLayout(animation_tab)

        for group_name in ["时间", "动画"]:
            if group_name in self.parameter_groups:
                group_widget = self.create_parameter_group_widget(group_name)
                animation_layout.addWidget(group_widget)

        animation_layout.addStretch()
        tab_widget.addTab(animation_tab, "动画")

        return tab_widget

    def enable_parameter_linking(self, parameter_id: str, linked_ids: List[str]):
        """启用参数链接"""
        self.linked_parameters[parameter_id] = linked_ids
        logger.info(f"启用参数链接: {parameter_id} -> {linked_ids}")

    def disable_parameter_linking(self, parameter_id: str):
        """禁用参数链接"""
        if parameter_id in self.linked_parameters:
            del self.linked_parameters[parameter_id]
            logger.info(f"禁用参数链接: {parameter_id}")

    def add_custom_parameter(self, parameter_id: str, config: PrecisionConfig, group_name: str = "自定义"):
        """添加自定义参数"""
        self.parameter_configs[parameter_id] = config

        if group_name not in self.parameter_groups:
            self.parameter_groups[group_name] = []

        self.parameter_groups[group_name].append(parameter_id)

        logger.info(f"添加自定义参数: {parameter_id} 到组 {group_name}")

    def remove_parameter(self, parameter_id: str):
        """移除参数"""
        # 移除输入组件
        if parameter_id in self.input_widgets:
            del self.input_widgets[parameter_id]

        # 移除配置
        if parameter_id in self.parameter_configs:
            del self.parameter_configs[parameter_id]

        # 从组中移除
        for group_name, parameter_ids in self.parameter_groups.items():
            if parameter_id in parameter_ids:
                parameter_ids.remove(parameter_id)

        # 移除链接
        if parameter_id in self.linked_parameters:
            del self.linked_parameters[parameter_id]

        logger.info(f"移除参数: {parameter_id}")

    def export_parameter_values(self) -> Dict[str, Any]:
        """导出参数值"""
        return {
            "parameter_values": self.get_parameter_values(),
            "precision_levels": {
                param_id: widget.get_precision_level().value
                for param_id, widget in self.input_widgets.items()
            },
            "linked_parameters": self.linked_parameters.copy()
        }

    def import_parameter_values(self, data: Dict[str, Any]):
        """导入参数值"""
        try:
            # 导入参数值
            if "parameter_values" in data:
                self.set_parameter_values(data["parameter_values"])

            # 导入精度级别
            if "precision_levels" in data:
                for param_id, precision_str in data["precision_levels"].items():
                    if param_id in self.input_widgets:
                        precision = InputPrecisionLevel(precision_str)
                        # 这里可以设置精度级别，但需要在PrecisionInputWidget中添加相应方法

            # 导入链接关系
            if "linked_parameters" in data:
                self.linked_parameters.update(data["linked_parameters"])

            logger.info("参数值导入完成")

        except Exception as e:
            logger.error(f"导入参数值失败: {e}")

    def get_manager_summary(self) -> Dict[str, Any]:
        """获取管理器摘要"""
        return {
            "total_parameters": len(self.parameter_configs),
            "active_widgets": len(self.input_widgets),
            "parameter_groups": len(self.parameter_groups),
            "linked_parameters": len(self.linked_parameters),
            "parameter_types": {
                value_type.value: len([
                    config for config in self.parameter_configs.values()
                    if config.value_type == value_type
                ])
                for value_type in ValueType
            }


class PrecisionInputIntegrator:
    """多精度输入集成器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.input_manager = PrecisionInputManager()
        self.integrated_panels: Dict[str, QWidget] = {}
        self.element_bindings: Dict[str, Dict[str, str]] = {}  # element_id -> {param_id: widget_param_id}

        # 连接信号
        self.input_manager.value_changed.connect(self.handle_parameter_change)
        self.input_manager.batch_values_changed.connect(self.handle_batch_parameter_change)

        logger.info("多精度输入集成器初始化完成")

    def integrate_precision_input_system(self):
        """集成多精度输入系统"""
        try:
            # 替换现有属性面板
            self.replace_properties_panels()

            # 集成到时间轴控制
            self.integrate_timeline_controls()

            # 集成到变换控制
            self.integrate_transform_controls()

            # 集成到动画控制
            self.integrate_animation_controls()

            # 添加精度控制面板
            self.add_precision_control_panel()

            logger.info("多精度输入系统集成完成")
            return True

        except Exception as e:
            logger.error(f"多精度输入系统集成失败: {e}")
            return False

    def replace_properties_panels(self):
        """替换属性面板"""
        try:
            # 替换主属性面板
            if hasattr(self.main_window, 'properties_widget'):
                old_properties = self.main_window.properties_widget

                # 创建新的精度属性面板
                new_properties = self.create_enhanced_properties_panel()

                # 替换面板
                parent = old_properties.parent()
                if parent:
                    layout = parent.layout()
                    if layout:
                        layout.replaceWidget(old_properties, new_properties)
                        old_properties.deleteLater()
                        self.main_window.properties_widget = new_properties
                        self.integrated_panels['properties'] = new_properties

                logger.debug("主属性面板已替换")

            # 替换元素属性面板
            if hasattr(self.main_window, 'elements_widget'):
                elements_widget = self.main_window.elements_widget
                if hasattr(elements_widget, 'properties_panel'):
                    old_panel = elements_widget.properties_panel
                    new_panel = self.input_manager.create_tabbed_properties_panel()

                    parent = old_panel.parent()
                    if parent and parent.layout():
                        parent.layout().replaceWidget(old_panel, new_panel)
                        old_panel.deleteLater()
                        elements_widget.properties_panel = new_panel
                        self.integrated_panels['elements_properties'] = new_panel

                logger.debug("元素属性面板已替换")

        except Exception as e:
            logger.error(f"替换属性面板失败: {e}")

    def create_enhanced_properties_panel(self) -> QWidget:
        """创建增强属性面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
        """)

        layout = QVBoxLayout(panel)

        # 标题
        title = QLabel("精确属性控制")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #495057; margin-bottom: 10px;")
        layout.addWidget(title)

        # 创建分标签页面板
        tab_panel = self.input_manager.create_tabbed_properties_panel()
        layout.addWidget(tab_panel)

        # 添加批量操作按钮
        batch_layout = QHBoxLayout()

        reset_btn = QPushButton("重置所有")
        reset_btn.clicked.connect(self.reset_all_parameters)
        batch_layout.addWidget(reset_btn)

        copy_btn = QPushButton("复制参数")
        copy_btn.clicked.connect(self.copy_parameters)
        batch_layout.addWidget(copy_btn)

        paste_btn = QPushButton("粘贴参数")
        paste_btn.clicked.connect(self.paste_parameters)
        batch_layout.addWidget(paste_btn)

        layout.addLayout(batch_layout)

        return panel

    def integrate_timeline_controls(self):
        """集成时间轴控制"""
        try:
            if hasattr(self.main_window, 'timeline_widget'):
                timeline_widget = self.main_window.timeline_widget

                # 创建时间参数控制
                time_controls = QWidget()
                time_layout = QHBoxLayout(time_controls)

                # 当前时间控制
                current_time_widget = self.input_manager.create_input_widget(
                    "current_time",
                    PrecisionConfig(
                        ValueType.TIME, 0, 3600, 0, InputPrecisionLevel.FINE, 0.01,
                        "s", "当前时间"
                    )
                )
                time_layout.addWidget(QLabel("时间:"))
                time_layout.addWidget(current_time_widget)

                # 缩放控制
                zoom_widget = self.input_manager.create_input_widget(
                    "timeline_zoom",
                    PrecisionConfig(
                        ValueType.PERCENTAGE, 10, 1000, 100, InputPrecisionLevel.NORMAL, 10,
                        "%", "时间轴缩放"
                    )
                )
                time_layout.addWidget(QLabel("缩放:"))
                time_layout.addWidget(zoom_widget)

                # 添加到时间轴
                if hasattr(timeline_widget, 'layout') and timeline_widget.layout():
                    timeline_widget.layout().addWidget(time_controls)

                self.integrated_panels['timeline_controls'] = time_controls
                logger.debug("时间轴控制已集成")

        except Exception as e:
            logger.error(f"集成时间轴控制失败: {e}")

    def integrate_transform_controls(self):
        """集成变换控制"""
        try:
            if hasattr(self.main_window, 'stage_widget'):
                stage_widget = self.main_window.stage_widget

                # 创建变换控制面板
                transform_panel = QFrame()
                transform_panel.setFrameStyle(QFrame.Shape.StyledPanel)
                transform_panel.setMaximumHeight(120)

                layout = QHBoxLayout(transform_panel)

                # 位置控制
                pos_group = self.input_manager.create_parameter_group_widget("位置")
                layout.addWidget(pos_group)

                # 缩放控制
                scale_group = self.input_manager.create_parameter_group_widget("缩放")
                layout.addWidget(scale_group)

                # 旋转控制
                rotation_widget = self.input_manager.create_input_widget("rotation")
                rotation_group = QGroupBox("旋转")
                rotation_layout = QVBoxLayout(rotation_group)
                rotation_layout.addWidget(rotation_widget)
                layout.addWidget(rotation_group)

                # 添加到舞台
                if hasattr(stage_widget, 'layout') and stage_widget.layout():
                    stage_widget.layout().addWidget(transform_panel)

                self.integrated_panels['transform_controls'] = transform_panel
                logger.debug("变换控制已集成")

        except Exception as e:
            logger.error(f"集成变换控制失败: {e}")

    def integrate_animation_controls(self):
        """集成动画控制"""
        try:
            if hasattr(self.main_window, 'animation_widget'):
                animation_widget = self.main_window.animation_widget

                # 创建动画参数控制
                animation_controls = self.input_manager.create_parameter_group_widget("动画")

                # 添加到动画面板
                if hasattr(animation_widget, 'layout') and animation_widget.layout():
                    animation_widget.layout().addWidget(animation_controls)

                self.integrated_panels['animation_controls'] = animation_controls
                logger.debug("动画控制已集成")

        except Exception as e:
            logger.error(f"集成动画控制失败: {e}")

    def add_precision_control_panel(self):
        """添加精度控制面板"""
        try:
            # 创建精度控制面板
            precision_panel = QFrame()
            precision_panel.setFrameStyle(QFrame.Shape.StyledPanel)
            precision_panel.setStyleSheet("""
                QFrame {
                    background-color: #e3f2fd;
                    border: 1px solid #2196f3;
                    border-radius: 6px;
                    padding: 10px;
                }
            """)

            layout = QVBoxLayout(precision_panel)

            # 标题
            title = QLabel("🎯 精度控制")
            title.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
            title.setStyleSheet("color: #1976d2; margin-bottom: 8px;")
            layout.addWidget(title)

            # 全局精度设置
            global_precision_layout = QHBoxLayout()
            global_precision_layout.addWidget(QLabel("全局精度:"))

            precision_combo = QComboBox()
            precision_combo.addItems(["粗调", "普通", "精调", "超精调"])
            precision_combo.setCurrentIndex(1)  # 默认普通精度
            precision_combo.currentIndexChanged.connect(self.set_global_precision)
            global_precision_layout.addWidget(precision_combo)

            layout.addLayout(global_precision_layout)

            # 链接控制
            link_layout = QHBoxLayout()

            link_scale_checkbox = QCheckBox("等比缩放")
            link_scale_checkbox.setChecked(True)
            link_scale_checkbox.toggled.connect(self.toggle_scale_linking)
            link_layout.addWidget(link_scale_checkbox)

            link_position_checkbox = QCheckBox("锁定位置")
            link_position_checkbox.toggled.connect(self.toggle_position_linking)
            link_layout.addWidget(link_position_checkbox)

            layout.addLayout(link_layout)

            # 快捷操作
            shortcuts_layout = QHBoxLayout()

            snap_btn = QPushButton("吸附网格")
            snap_btn.setCheckable(True)
            snap_btn.toggled.connect(self.toggle_grid_snap)
            shortcuts_layout.addWidget(snap_btn)

            relative_btn = QPushButton("相对模式")
            relative_btn.setCheckable(True)
            relative_btn.toggled.connect(self.toggle_relative_mode)
            shortcuts_layout.addWidget(relative_btn)

            layout.addLayout(shortcuts_layout)

            # 添加到主窗口
            if hasattr(self.main_window, 'add_dock_widget'):
                self.main_window.add_dock_widget("精度控制", precision_panel, Qt.DockWidgetArea.RightDockWidgetArea)
            else:
                # 添加到状态栏
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().addPermanentWidget(precision_panel)

            self.integrated_panels['precision_control'] = precision_panel
            logger.debug("精度控制面板已添加")

        except Exception as e:
            logger.error(f"添加精度控制面板失败: {e}")

    def handle_parameter_change(self, parameter_id: str, value: float):
        """处理参数改变"""
        try:
            # 更新对应的元素属性
            if hasattr(self.main_window, 'current_element'):
                current_element = self.main_window.current_element
                if current_element:
                    self.apply_parameter_to_element(current_element, parameter_id, value)

            # 更新时间轴
            if parameter_id in ["current_time", "start_time", "end_time", "duration"]:
                self.update_timeline_display()

            # 更新舞台显示
            if parameter_id in ["position_x", "position_y", "scale_x", "scale_y", "rotation"]:
                self.update_stage_display()

            logger.debug(f"处理参数改变: {parameter_id} = {value}")

        except Exception as e:
            logger.error(f"处理参数改变失败 {parameter_id}: {e}")

    def handle_batch_parameter_change(self, values: Dict[str, float]):
        """处理批量参数改变"""
        try:
            # 批量更新元素属性
            if hasattr(self.main_window, 'current_element'):
                current_element = self.main_window.current_element
                if current_element:
                    for parameter_id, value in values.items():
                        self.apply_parameter_to_element(current_element, parameter_id, value)

            # 批量更新显示
            self.update_all_displays()

            logger.debug(f"处理批量参数改变: {len(values)}个参数")

        except Exception as e:
            logger.error(f"处理批量参数改变失败: {e}")

    def apply_parameter_to_element(self, element, parameter_id: str, value: float):
        """应用参数到元素"""
        try:
            # 根据参数类型应用到元素
            if parameter_id == "position_x":
                element.position.x = value
            elif parameter_id == "position_y":
                element.position.y = value
            elif parameter_id == "width":
                element.size.width = value
            elif parameter_id == "height":
                element.size.height = value
            elif parameter_id == "scale_x":
                element.transform.scale_x = value
            elif parameter_id == "scale_y":
                element.transform.scale_y = value
            elif parameter_id == "rotation":
                element.transform.rotation = value
            elif parameter_id == "opacity":
                element.style.opacity = value / 100.0  # 转换为0-1范围

            # 标记元素已修改
            element.modified = True

        except Exception as e:
            logger.error(f"应用参数到元素失败 {parameter_id}: {e}")

    def update_timeline_display(self):
        """更新时间轴显示"""
        try:
            if hasattr(self.main_window, 'timeline_widget'):
                timeline_widget = self.main_window.timeline_widget
                if hasattr(timeline_widget, 'update_display'):
                    timeline_widget.update_display()
        except Exception as e:
            logger.error(f"更新时间轴显示失败: {e}")

    def update_stage_display(self):
        """更新舞台显示"""
        try:
            if hasattr(self.main_window, 'stage_widget'):
                stage_widget = self.main_window.stage_widget
                if hasattr(stage_widget, 'update_display'):
                    stage_widget.update_display()
        except Exception as e:
            logger.error(f"更新舞台显示失败: {e}")

    def update_all_displays(self):
        """更新所有显示"""
        self.update_timeline_display()
        self.update_stage_display()

    def set_global_precision(self, index: int):
        """设置全局精度"""
        precision_levels = list(InputPrecisionLevel)
        if 0 <= index < len(precision_levels):
            precision = precision_levels[index]

            # 更新所有输入组件的精度
            for widget in self.input_manager.input_widgets.values():
                widget.current_precision = precision
                widget.setup_value_input()

            logger.info(f"全局精度设置为: {precision.value}")

    def toggle_scale_linking(self, enabled: bool):
        """切换缩放链接"""
        if enabled:
            self.input_manager.enable_parameter_linking("scale_x", ["scale_y"])
        else:
            self.input_manager.disable_parameter_linking("scale_x")

        logger.info(f"等比缩放: {'启用' if enabled else '禁用'}")

    def toggle_position_linking(self, enabled: bool):
        """切换位置链接"""
        if enabled:
            self.input_manager.enable_parameter_linking("position_x", ["position_y"])
        else:
            self.input_manager.disable_parameter_linking("position_x")

        logger.info(f"位置锁定: {'启用' if enabled else '禁用'}")

    def toggle_grid_snap(self, enabled: bool):
        """切换网格吸附"""
        # 实现网格吸附逻辑
        logger.info(f"网格吸附: {'启用' if enabled else '禁用'}")

    def toggle_relative_mode(self, enabled: bool):
        """切换相对模式"""
        # 实现相对模式逻辑
        logger.info(f"相对模式: {'启用' if enabled else '禁用'}")

    def reset_all_parameters(self):
        """重置所有参数"""
        try:
            for parameter_id, config in self.input_manager.parameter_configs.items():
                if parameter_id in self.input_manager.input_widgets:
                    self.input_manager.set_parameter_value(parameter_id, config.default_value)

            logger.info("所有参数已重置")

        except Exception as e:
            logger.error(f"重置参数失败: {e}")

    def copy_parameters(self):
        """复制参数"""
        try:
            values = self.input_manager.get_parameter_values()

            # 将参数值复制到剪贴板
            import json
            clipboard = QApplication.clipboard()
            clipboard.setText(json.dumps(values))

            logger.info("参数已复制到剪贴板")

        except Exception as e:
            logger.error(f"复制参数失败: {e}")

    def paste_parameters(self):
        """粘贴参数"""
        try:
            clipboard = QApplication.clipboard()
            text = clipboard.text()

            if text:
                import json
                values = json.loads(text)
                self.input_manager.set_parameter_values(values)

                logger.info("参数已从剪贴板粘贴")

        except Exception as e:
            logger.error(f"粘贴参数失败: {e}")

    def bind_element_parameters(self, element_id: str, parameter_bindings: Dict[str, str]):
        """绑定元素参数"""
        self.element_bindings[element_id] = parameter_bindings
        logger.info(f"绑定元素参数: {element_id}")

    def load_element_parameters(self, element_id: str):
        """加载元素参数"""
        if element_id in self.element_bindings:
            # 从元素加载参数值
            # 这里需要根据实际的元素数据结构实现
            pass

    def get_input_manager(self) -> PrecisionInputManager:
        """获取输入管理器"""
        return self.input_manager

    def export_integration_config(self, file_path: str):
        """导出集成配置"""
        try:
            config = {
                "integrated_panels": list(self.integrated_panels.keys()),
                "element_bindings": self.element_bindings,
                "parameter_values": self.input_manager.export_parameter_values(),
                "integration_summary": self.get_integration_summary()
            }

            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            logger.info(f"集成配置已导出到: {file_path}")

        except Exception as e:
            logger.error(f"导出集成配置失败: {e}")

    def get_integration_summary(self) -> Dict[str, Any]:
        """获取集成摘要"""
        manager_summary = self.input_manager.get_manager_summary()

        return {
            "integrated_panels": len(self.integrated_panels),
            "element_bindings": len(self.element_bindings),
            "total_parameters": manager_summary["total_parameters"],
            "active_widgets": manager_summary["active_widgets"],
            "parameter_groups": manager_summary["parameter_groups"],
            "linked_parameters": manager_summary["linked_parameters"],
            "integration_status": "completed"
        }
        }
