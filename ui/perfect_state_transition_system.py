"""
AI Animation Studio - 完美状态衔接系统
实现最关键的状态衔接系统，自动处理时间轴连接问题
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTextEdit, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
                             QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
                             QProgressBar, QFrame, QScrollArea, QGroupBox, QFormLayout,
                             QCheckBox, QTabWidget, QSplitter, QMessageBox, QDialog,
                             QApplication, QMenu, QToolButton, QStackedWidget, QSlider)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QThread, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QBrush, QPen, QSyntaxHighlighter, QTextCharFormat

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, Set
import json
import time
import re
import math
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, Counter
import numpy as np
from pathlib import Path

from core.logger import get_logger
from core.data_structures import AnimationSolution, TechStack, AnimationType

logger = get_logger("perfect_state_transition_system")


class StateValidationLevel(Enum):
    """状态验证级别枚举"""
    STRICT = "strict"           # 严格验证，所有属性必须匹配
    STANDARD = "standard"       # 标准验证，核心属性必须匹配
    RELAXED = "relaxed"         # 宽松验证，允许较大差异
    ADAPTIVE = "adaptive"       # 自适应验证，根据上下文调整


class TransitionStrategy(Enum):
    """过渡策略枚举"""
    DIRECT = "direct"           # 直接连接
    INTERPOLATED = "interpolated"  # 插值过渡
    SMOOTH = "smooth"           # 平滑过渡
    PHYSICS_BASED = "physics_based"  # 基于物理的过渡
    AI_GENERATED = "ai_generated"   # AI生成过渡


class StateProperty(Enum):
    """状态属性枚举"""
    POSITION = "position"       # 位置
    ROTATION = "rotation"       # 旋转
    SCALE = "scale"            # 缩放
    OPACITY = "opacity"        # 透明度
    COLOR = "color"            # 颜色
    SIZE = "size"              # 尺寸
    TRANSFORM = "transform"    # 变换矩阵
    FILTER = "filter"          # 滤镜效果
    ANIMATION = "animation"    # 动画状态


@dataclass
class CoreState:
    """核心状态定义"""
    element_id: str
    timestamp: float
    segment_id: str
    
    # 核心属性（必须验证）
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    rotation: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    scale: Dict[str, float] = field(default_factory=lambda: {"x": 1, "y": 1, "z": 1})
    opacity: float = 1.0
    
    # 扩展属性（可选验证）
    color: Optional[str] = None
    size: Optional[Dict[str, float]] = None
    transform_matrix: Optional[List[float]] = None
    filters: Optional[List[str]] = None
    
    # 元数据
    confidence: float = 1.0
    source: str = "ai_generated"  # ai_generated, live_captured, user_defined, interpolated
    validation_level: StateValidationLevel = StateValidationLevel.STANDARD
    
    # 状态快照
    css_snapshot: Optional[str] = None
    dom_snapshot: Optional[Dict] = None


@dataclass
class StateTransitionResult:
    """状态转换结果"""
    success: bool
    transition_strategy: TransitionStrategy
    start_state: CoreState
    end_state: CoreState
    intermediate_states: List[CoreState] = field(default_factory=list)
    transition_code: str = ""
    validation_report: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    estimated_duration: float = 0.0
    performance_impact: float = 0.0


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    validation_level: StateValidationLevel
    property_checks: Dict[StateProperty, Dict[str, Any]] = field(default_factory=dict)
    overall_score: float = 0.0
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    auto_fix_available: bool = False


class CoreStateManager:
    """核心状态管理器"""
    
    def __init__(self):
        self.states: Dict[str, Dict[str, CoreState]] = {}  # element_id -> segment_id -> state
        self.tolerance_settings = {
            StateProperty.POSITION: {"x": 5.0, "y": 5.0, "z": 5.0},  # 像素
            StateProperty.ROTATION: {"x": 2.0, "y": 2.0, "z": 2.0},  # 度
            StateProperty.SCALE: {"x": 0.05, "y": 0.05, "z": 0.05},  # 比例
            StateProperty.OPACITY: 0.1,  # 透明度
        }
        
        logger.info("核心状态管理器初始化完成")
    
    def record_state(self, state: CoreState) -> bool:
        """记录状态"""
        try:
            if state.element_id not in self.states:
                self.states[state.element_id] = {}
            
            self.states[state.element_id][state.segment_id] = state
            
            logger.debug(f"记录状态: {state.element_id}@{state.segment_id}")
            return True
            
        except Exception as e:
            logger.error(f"记录状态失败: {e}")
            return False
    
    def get_state(self, element_id: str, segment_id: str) -> Optional[CoreState]:
        """获取状态"""
        return self.states.get(element_id, {}).get(segment_id)
    
    def get_element_states(self, element_id: str) -> Dict[str, CoreState]:
        """获取元素的所有状态"""
        return self.states.get(element_id, {})
    
    def validate_state_continuity(self, element_id: str, from_segment: str, 
                                 to_segment: str, validation_level: StateValidationLevel = None) -> ValidationResult:
        """验证状态连续性"""
        try:
            from_state = self.get_state(element_id, from_segment)
            to_state = self.get_state(element_id, to_segment)
            
            if not from_state or not to_state:
                return ValidationResult(
                    is_valid=False,
                    validation_level=validation_level or StateValidationLevel.STANDARD,
                    issues=["缺少必要的状态数据"]
                )
            
            validation_level = validation_level or from_state.validation_level
            
            # 执行属性检查
            property_checks = {}
            overall_score = 0.0
            issues = []
            suggestions = []
            
            # 位置检查
            pos_check = self.validate_position_continuity(from_state, to_state, validation_level)
            property_checks[StateProperty.POSITION] = pos_check
            overall_score += pos_check["score"] * 0.3
            
            if not pos_check["valid"]:
                issues.append(f"位置不连续: {pos_check['message']}")
                suggestions.append(f"建议调整位置: {pos_check['suggestion']}")
            
            # 旋转检查
            rot_check = self.validate_rotation_continuity(from_state, to_state, validation_level)
            property_checks[StateProperty.ROTATION] = rot_check
            overall_score += rot_check["score"] * 0.2
            
            if not rot_check["valid"]:
                issues.append(f"旋转不连续: {rot_check['message']}")
                suggestions.append(f"建议调整旋转: {rot_check['suggestion']}")
            
            # 缩放检查
            scale_check = self.validate_scale_continuity(from_state, to_state, validation_level)
            property_checks[StateProperty.SCALE] = scale_check
            overall_score += scale_check["score"] * 0.2
            
            if not scale_check["valid"]:
                issues.append(f"缩放不连续: {scale_check['message']}")
                suggestions.append(f"建议调整缩放: {scale_check['suggestion']}")
            
            # 透明度检查
            opacity_check = self.validate_opacity_continuity(from_state, to_state, validation_level)
            property_checks[StateProperty.OPACITY] = opacity_check
            overall_score += opacity_check["score"] * 0.3
            
            if not opacity_check["valid"]:
                issues.append(f"透明度不连续: {opacity_check['message']}")
                suggestions.append(f"建议调整透明度: {opacity_check['suggestion']}")
            
            # 判断整体有效性
            is_valid = overall_score >= self.get_validation_threshold(validation_level)
            auto_fix_available = len(suggestions) > 0 and overall_score >= 0.6
            
            return ValidationResult(
                is_valid=is_valid,
                validation_level=validation_level,
                property_checks=property_checks,
                overall_score=overall_score,
                issues=issues,
                suggestions=suggestions,
                auto_fix_available=auto_fix_available
            )
            
        except Exception as e:
            logger.error(f"验证状态连续性失败: {e}")
            return ValidationResult(
                is_valid=False,
                validation_level=validation_level or StateValidationLevel.STANDARD,
                issues=[f"验证过程出错: {str(e)}"]
            )
    
    def validate_position_continuity(self, from_state: CoreState, to_state: CoreState, 
                                   validation_level: StateValidationLevel) -> Dict[str, Any]:
        """验证位置连续性"""
        try:
            tolerance = self.tolerance_settings[StateProperty.POSITION]
            
            # 计算位置差异
            diff_x = abs(from_state.position["x"] - to_state.position["x"])
            diff_y = abs(from_state.position["y"] - to_state.position["y"])
            diff_z = abs(from_state.position.get("z", 0) - to_state.position.get("z", 0))
            
            # 根据验证级别调整容差
            level_multiplier = {
                StateValidationLevel.STRICT: 0.5,
                StateValidationLevel.STANDARD: 1.0,
                StateValidationLevel.RELAXED: 2.0,
                StateValidationLevel.ADAPTIVE: 1.5
            }
            
            multiplier = level_multiplier[validation_level]
            
            # 检查是否在容差范围内
            x_valid = diff_x <= tolerance["x"] * multiplier
            y_valid = diff_y <= tolerance["y"] * multiplier
            z_valid = diff_z <= tolerance["z"] * multiplier
            
            valid = x_valid and y_valid and z_valid
            
            # 计算分数
            x_score = max(0, 1 - diff_x / (tolerance["x"] * multiplier * 2))
            y_score = max(0, 1 - diff_y / (tolerance["y"] * multiplier * 2))
            z_score = max(0, 1 - diff_z / (tolerance["z"] * multiplier * 2))
            score = (x_score + y_score + z_score) / 3
            
            # 生成消息和建议
            if valid:
                message = "位置连续性良好"
                suggestion = ""
            else:
                message = f"位置差异过大: X={diff_x:.1f}px, Y={diff_y:.1f}px, Z={diff_z:.1f}px"
                suggestion = f"建议调整到: X={to_state.position['x']:.1f}, Y={to_state.position['y']:.1f}"
            
            return {
                "valid": valid,
                "score": score,
                "message": message,
                "suggestion": suggestion,
                "details": {
                    "diff_x": diff_x,
                    "diff_y": diff_y,
                    "diff_z": diff_z,
                    "tolerance": tolerance,
                    "multiplier": multiplier
                }
            }
            
        except Exception as e:
            logger.error(f"验证位置连续性失败: {e}")
            return {
                "valid": False,
                "score": 0.0,
                "message": f"位置验证出错: {str(e)}",
                "suggestion": "请检查位置数据格式",
                "details": {}
            }
    
    def validate_rotation_continuity(self, from_state: CoreState, to_state: CoreState, 
                                   validation_level: StateValidationLevel) -> Dict[str, Any]:
        """验证旋转连续性"""
        try:
            tolerance = self.tolerance_settings[StateProperty.ROTATION]
            
            # 计算旋转差异（考虑角度周期性）
            def angle_diff(a1, a2):
                diff = abs(a1 - a2)
                return min(diff, 360 - diff)
            
            diff_x = angle_diff(from_state.rotation["x"], to_state.rotation["x"])
            diff_y = angle_diff(from_state.rotation["y"], to_state.rotation["y"])
            diff_z = angle_diff(from_state.rotation.get("z", 0), to_state.rotation.get("z", 0))
            
            # 根据验证级别调整容差
            level_multiplier = {
                StateValidationLevel.STRICT: 0.5,
                StateValidationLevel.STANDARD: 1.0,
                StateValidationLevel.RELAXED: 2.0,
                StateValidationLevel.ADAPTIVE: 1.5
            }
            
            multiplier = level_multiplier[validation_level]
            
            # 检查是否在容差范围内
            x_valid = diff_x <= tolerance["x"] * multiplier
            y_valid = diff_y <= tolerance["y"] * multiplier
            z_valid = diff_z <= tolerance["z"] * multiplier
            
            valid = x_valid and y_valid and z_valid
            
            # 计算分数
            x_score = max(0, 1 - diff_x / (tolerance["x"] * multiplier * 2))
            y_score = max(0, 1 - diff_y / (tolerance["y"] * multiplier * 2))
            z_score = max(0, 1 - diff_z / (tolerance["z"] * multiplier * 2))
            score = (x_score + y_score + z_score) / 3
            
            # 生成消息和建议
            if valid:
                message = "旋转连续性良好"
                suggestion = ""
            else:
                message = f"旋转差异过大: X={diff_x:.1f}°, Y={diff_y:.1f}°, Z={diff_z:.1f}°"
                suggestion = f"建议调整到: X={to_state.rotation['x']:.1f}°, Y={to_state.rotation['y']:.1f}°"
            
            return {
                "valid": valid,
                "score": score,
                "message": message,
                "suggestion": suggestion,
                "details": {
                    "diff_x": diff_x,
                    "diff_y": diff_y,
                    "diff_z": diff_z,
                    "tolerance": tolerance,
                    "multiplier": multiplier
                }
            }
            
        except Exception as e:
            logger.error(f"验证旋转连续性失败: {e}")
            return {
                "valid": False,
                "score": 0.0,
                "message": f"旋转验证出错: {str(e)}",
                "suggestion": "请检查旋转数据格式",
                "details": {}
            }
    
    def validate_scale_continuity(self, from_state: CoreState, to_state: CoreState, 
                                validation_level: StateValidationLevel) -> Dict[str, Any]:
        """验证缩放连续性"""
        try:
            tolerance = self.tolerance_settings[StateProperty.SCALE]
            
            # 计算缩放差异
            diff_x = abs(from_state.scale["x"] - to_state.scale["x"])
            diff_y = abs(from_state.scale["y"] - to_state.scale["y"])
            diff_z = abs(from_state.scale.get("z", 1) - to_state.scale.get("z", 1))
            
            # 根据验证级别调整容差
            level_multiplier = {
                StateValidationLevel.STRICT: 0.5,
                StateValidationLevel.STANDARD: 1.0,
                StateValidationLevel.RELAXED: 2.0,
                StateValidationLevel.ADAPTIVE: 1.5
            }
            
            multiplier = level_multiplier[validation_level]
            
            # 检查是否在容差范围内
            x_valid = diff_x <= tolerance["x"] * multiplier
            y_valid = diff_y <= tolerance["y"] * multiplier
            z_valid = diff_z <= tolerance["z"] * multiplier
            
            valid = x_valid and y_valid and z_valid
            
            # 计算分数
            x_score = max(0, 1 - diff_x / (tolerance["x"] * multiplier * 2))
            y_score = max(0, 1 - diff_y / (tolerance["y"] * multiplier * 2))
            z_score = max(0, 1 - diff_z / (tolerance["z"] * multiplier * 2))
            score = (x_score + y_score + z_score) / 3
            
            # 生成消息和建议
            if valid:
                message = "缩放连续性良好"
                suggestion = ""
            else:
                message = f"缩放差异过大: X={diff_x:.3f}, Y={diff_y:.3f}, Z={diff_z:.3f}"
                suggestion = f"建议调整到: X={to_state.scale['x']:.3f}, Y={to_state.scale['y']:.3f}"
            
            return {
                "valid": valid,
                "score": score,
                "message": message,
                "suggestion": suggestion,
                "details": {
                    "diff_x": diff_x,
                    "diff_y": diff_y,
                    "diff_z": diff_z,
                    "tolerance": tolerance,
                    "multiplier": multiplier
                }
            }
            
        except Exception as e:
            logger.error(f"验证缩放连续性失败: {e}")
            return {
                "valid": False,
                "score": 0.0,
                "message": f"缩放验证出错: {str(e)}",
                "suggestion": "请检查缩放数据格式",
                "details": {}
            }
    
    def validate_opacity_continuity(self, from_state: CoreState, to_state: CoreState, 
                                  validation_level: StateValidationLevel) -> Dict[str, Any]:
        """验证透明度连续性"""
        try:
            tolerance = self.tolerance_settings[StateProperty.OPACITY]
            
            # 计算透明度差异
            diff = abs(from_state.opacity - to_state.opacity)
            
            # 根据验证级别调整容差
            level_multiplier = {
                StateValidationLevel.STRICT: 0.5,
                StateValidationLevel.STANDARD: 1.0,
                StateValidationLevel.RELAXED: 2.0,
                StateValidationLevel.ADAPTIVE: 1.5
            }
            
            multiplier = level_multiplier[validation_level]
            
            # 检查是否在容差范围内
            valid = diff <= tolerance * multiplier
            
            # 计算分数
            score = max(0, 1 - diff / (tolerance * multiplier * 2))
            
            # 生成消息和建议
            if valid:
                message = "透明度连续性良好"
                suggestion = ""
            else:
                message = f"透明度差异过大: {diff:.3f}"
                suggestion = f"建议调整到: {to_state.opacity:.3f}"
            
            return {
                "valid": valid,
                "score": score,
                "message": message,
                "suggestion": suggestion,
                "details": {
                    "diff": diff,
                    "tolerance": tolerance,
                    "multiplier": multiplier
                }
            }
            
        except Exception as e:
            logger.error(f"验证透明度连续性失败: {e}")
            return {
                "valid": False,
                "score": 0.0,
                "message": f"透明度验证出错: {str(e)}",
                "suggestion": "请检查透明度数据格式",
                "details": {}
            }
    
    def get_validation_threshold(self, validation_level: StateValidationLevel) -> float:
        """获取验证阈值"""
        thresholds = {
            StateValidationLevel.STRICT: 0.95,
            StateValidationLevel.STANDARD: 0.8,
            StateValidationLevel.RELAXED: 0.6,
            StateValidationLevel.ADAPTIVE: 0.7
        }
        return thresholds[validation_level]
    
    def set_tolerance(self, property_type: StateProperty, tolerance: Union[float, Dict[str, float]]):
        """设置容差"""
        self.tolerance_settings[property_type] = tolerance
        logger.debug(f"设置容差: {property_type.value} = {tolerance}")
    
    def clear_states(self, element_id: str = None):
        """清空状态"""
        if element_id:
            if element_id in self.states:
                del self.states[element_id]
                logger.debug(f"清空元素状态: {element_id}")
        else:
            self.states.clear()
            logger.debug("清空所有状态")


class AIStateFunction:
    """AI状态函数 - 重新定义AI职责"""

    def __init__(self):
        self.state_templates = self.initialize_state_templates()
        self.interpolation_strategies = self.initialize_interpolation_strategies()

        logger.info("AI状态函数初始化完成")

    def initialize_state_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化状态模板"""
        return {
            "default": {
                "position": {"x": 0, "y": 0, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "scale": {"x": 1, "y": 1, "z": 1},
                "opacity": 1.0
            },
            "hidden": {
                "position": {"x": 0, "y": 0, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "scale": {"x": 1, "y": 1, "z": 1},
                "opacity": 0.0
            },
            "scaled_down": {
                "position": {"x": 0, "y": 0, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "scale": {"x": 0.1, "y": 0.1, "z": 0.1},
                "opacity": 1.0
            },
            "rotated": {
                "position": {"x": 0, "y": 0, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 180},
                "scale": {"x": 1, "y": 1, "z": 1},
                "opacity": 1.0
            }
        }

    def initialize_interpolation_strategies(self) -> Dict[str, Callable]:
        """初始化插值策略"""
        return {
            "linear": self.linear_interpolation,
            "ease_in": self.ease_in_interpolation,
            "ease_out": self.ease_out_interpolation,
            "ease_in_out": self.ease_in_out_interpolation,
            "bounce": self.bounce_interpolation,
            "elastic": self.elastic_interpolation
        }

    def generate_transition_state(self, from_state: CoreState, to_state: CoreState,
                                 progress: float = 0.5, strategy: str = "linear") -> CoreState:
        """生成过渡状态"""
        try:
            if strategy not in self.interpolation_strategies:
                strategy = "linear"

            interpolation_func = self.interpolation_strategies[strategy]

            # 插值各个属性
            interpolated_position = self.interpolate_position(
                from_state.position, to_state.position, progress, interpolation_func
            )

            interpolated_rotation = self.interpolate_rotation(
                from_state.rotation, to_state.rotation, progress, interpolation_func
            )

            interpolated_scale = self.interpolate_scale(
                from_state.scale, to_state.scale, progress, interpolation_func
            )

            interpolated_opacity = interpolation_func(from_state.opacity, to_state.opacity, progress)

            # 创建过渡状态
            transition_state = CoreState(
                element_id=from_state.element_id,
                timestamp=time.time(),
                segment_id=f"{from_state.segment_id}_to_{to_state.segment_id}_transition",
                position=interpolated_position,
                rotation=interpolated_rotation,
                scale=interpolated_scale,
                opacity=interpolated_opacity,
                source="interpolated",
                confidence=min(from_state.confidence, to_state.confidence) * 0.9
            )

            return transition_state

        except Exception as e:
            logger.error(f"生成过渡状态失败: {e}")
            return from_state

    def interpolate_position(self, from_pos: Dict[str, float], to_pos: Dict[str, float],
                           progress: float, interpolation_func: Callable) -> Dict[str, float]:
        """插值位置"""
        return {
            "x": interpolation_func(from_pos["x"], to_pos["x"], progress),
            "y": interpolation_func(from_pos["y"], to_pos["y"], progress),
            "z": interpolation_func(from_pos.get("z", 0), to_pos.get("z", 0), progress)
        }

    def interpolate_rotation(self, from_rot: Dict[str, float], to_rot: Dict[str, float],
                           progress: float, interpolation_func: Callable) -> Dict[str, float]:
        """插值旋转（考虑角度周期性）"""
        def interpolate_angle(a1, a2, t):
            # 处理角度的周期性
            diff = a2 - a1
            if diff > 180:
                a2 -= 360
            elif diff < -180:
                a2 += 360
            return interpolation_func(a1, a2, t)

        return {
            "x": interpolate_angle(from_rot["x"], to_rot["x"], progress),
            "y": interpolate_angle(from_rot["y"], to_rot["y"], progress),
            "z": interpolate_angle(from_rot.get("z", 0), to_rot.get("z", 0), progress)
        }

    def interpolate_scale(self, from_scale: Dict[str, float], to_scale: Dict[str, float],
                        progress: float, interpolation_func: Callable) -> Dict[str, float]:
        """插值缩放"""
        return {
            "x": interpolation_func(from_scale["x"], to_scale["x"], progress),
            "y": interpolation_func(from_scale["y"], to_scale["y"], progress),
            "z": interpolation_func(from_scale.get("z", 1), to_scale.get("z", 1), progress)
        }

    def linear_interpolation(self, start: float, end: float, progress: float) -> float:
        """线性插值"""
        return start + (end - start) * progress

    def ease_in_interpolation(self, start: float, end: float, progress: float) -> float:
        """缓入插值"""
        t = progress * progress
        return start + (end - start) * t

    def ease_out_interpolation(self, start: float, end: float, progress: float) -> float:
        """缓出插值"""
        t = 1 - (1 - progress) * (1 - progress)
        return start + (end - start) * t

    def ease_in_out_interpolation(self, start: float, end: float, progress: float) -> float:
        """缓入缓出插值"""
        if progress < 0.5:
            t = 2 * progress * progress
        else:
            t = 1 - 2 * (1 - progress) * (1 - progress)
        return start + (end - start) * t

    def bounce_interpolation(self, start: float, end: float, progress: float) -> float:
        """弹跳插值"""
        if progress < 1/2.75:
            t = 7.5625 * progress * progress
        elif progress < 2/2.75:
            progress -= 1.5/2.75
            t = 7.5625 * progress * progress + 0.75
        elif progress < 2.5/2.75:
            progress -= 2.25/2.75
            t = 7.5625 * progress * progress + 0.9375
        else:
            progress -= 2.625/2.75
            t = 7.5625 * progress * progress + 0.984375

        return start + (end - start) * t

    def elastic_interpolation(self, start: float, end: float, progress: float) -> float:
        """弹性插值"""
        if progress == 0 or progress == 1:
            return start + (end - start) * progress

        p = 0.3
        s = p / 4
        t = 2 * math.pow(2, -10 * progress) * math.sin((progress - s) * (2 * math.pi) / p) + 1

        return start + (end - start) * t

    def create_state_from_template(self, element_id: str, segment_id: str,
                                  template_name: str = "default") -> CoreState:
        """从模板创建状态"""
        try:
            if template_name not in self.state_templates:
                template_name = "default"

            template = self.state_templates[template_name]

            state = CoreState(
                element_id=element_id,
                timestamp=time.time(),
                segment_id=segment_id,
                position=template["position"].copy(),
                rotation=template["rotation"].copy(),
                scale=template["scale"].copy(),
                opacity=template["opacity"],
                source="ai_generated",
                confidence=0.9
            )

            return state

        except Exception as e:
            logger.error(f"从模板创建状态失败: {e}")
            return self.create_default_state(element_id, segment_id)

    def create_default_state(self, element_id: str, segment_id: str) -> CoreState:
        """创建默认状态"""
        return CoreState(
            element_id=element_id,
            timestamp=time.time(),
            segment_id=segment_id,
            source="ai_generated",
            confidence=0.8
        )

    def generate_intermediate_states(self, from_state: CoreState, to_state: CoreState,
                                   count: int = 5, strategy: str = "ease_in_out") -> List[CoreState]:
        """生成中间状态序列"""
        try:
            intermediate_states = []

            for i in range(1, count + 1):
                progress = i / (count + 1)
                intermediate_state = self.generate_transition_state(
                    from_state, to_state, progress, strategy
                )
                intermediate_state.segment_id = f"{from_state.segment_id}_intermediate_{i}"
                intermediate_states.append(intermediate_state)

            return intermediate_states

        except Exception as e:
            logger.error(f"生成中间状态序列失败: {e}")
            return []


class StateTransitionValidator:
    """状态转换验证器"""

    def __init__(self):
        self.validation_rules = self.initialize_validation_rules()
        self.performance_thresholds = {
            "max_position_change": 1000,  # 最大位置变化（像素）
            "max_rotation_change": 360,   # 最大旋转变化（度）
            "max_scale_change": 5.0,      # 最大缩放变化
            "max_opacity_change": 1.0,    # 最大透明度变化
            "min_transition_duration": 0.1,  # 最小过渡时长（秒）
            "max_transition_duration": 5.0   # 最大过渡时长（秒）
        }

        logger.info("状态转换验证器初始化完成")

    def initialize_validation_rules(self) -> Dict[str, Callable]:
        """初始化验证规则"""
        return {
            "position_continuity": self.validate_position_continuity_rule,
            "rotation_continuity": self.validate_rotation_continuity_rule,
            "scale_continuity": self.validate_scale_continuity_rule,
            "opacity_continuity": self.validate_opacity_continuity_rule,
            "performance_impact": self.validate_performance_impact_rule,
            "visual_coherence": self.validate_visual_coherence_rule
        }

    def validate_transition(self, transition_result: StateTransitionResult) -> ValidationResult:
        """验证状态转换"""
        try:
            validation_results = []
            overall_score = 0.0
            issues = []
            suggestions = []

            # 执行所有验证规则
            for rule_name, rule_func in self.validation_rules.items():
                try:
                    rule_result = rule_func(transition_result)
                    validation_results.append((rule_name, rule_result))
                    overall_score += rule_result["score"] * rule_result.get("weight", 1.0)

                    if not rule_result["valid"]:
                        issues.append(f"{rule_name}: {rule_result['message']}")

                    if rule_result.get("suggestion"):
                        suggestions.append(rule_result["suggestion"])

                except Exception as e:
                    logger.error(f"验证规则 {rule_name} 执行失败: {e}")
                    issues.append(f"{rule_name}: 验证失败")

            # 计算总权重
            total_weight = sum(result[1].get("weight", 1.0) for result in validation_results)
            if total_weight > 0:
                overall_score /= total_weight

            # 判断整体有效性
            is_valid = overall_score >= 0.7 and len(issues) == 0
            auto_fix_available = overall_score >= 0.5 and len(suggestions) > 0

            # 构建属性检查结果
            property_checks = {}
            for rule_name, rule_result in validation_results:
                if "property" in rule_result:
                    property_checks[rule_result["property"]] = rule_result

            return ValidationResult(
                is_valid=is_valid,
                validation_level=StateValidationLevel.STANDARD,
                property_checks=property_checks,
                overall_score=overall_score,
                issues=issues,
                suggestions=suggestions,
                auto_fix_available=auto_fix_available
            )

        except Exception as e:
            logger.error(f"验证状态转换失败: {e}")
            return ValidationResult(
                is_valid=False,
                validation_level=StateValidationLevel.STANDARD,
                issues=[f"验证过程出错: {str(e)}"]
            )

    def validate_position_continuity_rule(self, transition_result: StateTransitionResult) -> Dict[str, Any]:
        """验证位置连续性规则"""
        try:
            from_pos = transition_result.start_state.position
            to_pos = transition_result.end_state.position

            # 计算位置变化
            pos_change = math.sqrt(
                (to_pos["x"] - from_pos["x"]) ** 2 +
                (to_pos["y"] - from_pos["y"]) ** 2 +
                (to_pos.get("z", 0) - from_pos.get("z", 0)) ** 2
            )

            # 检查是否超过阈值
            max_change = self.performance_thresholds["max_position_change"]
            valid = pos_change <= max_change

            # 计算分数
            score = max(0, 1 - pos_change / (max_change * 2))

            # 生成消息和建议
            if valid:
                message = f"位置变化合理: {pos_change:.1f}px"
                suggestion = ""
            else:
                message = f"位置变化过大: {pos_change:.1f}px (最大: {max_change}px)"
                suggestion = "建议分解为多个较小的位置变化"

            return {
                "valid": valid,
                "score": score,
                "weight": 0.3,
                "property": StateProperty.POSITION,
                "message": message,
                "suggestion": suggestion,
                "details": {
                    "position_change": pos_change,
                    "max_change": max_change
                }
            }

        except Exception as e:
            logger.error(f"位置连续性规则验证失败: {e}")
            return {
                "valid": False,
                "score": 0.0,
                "weight": 0.3,
                "property": StateProperty.POSITION,
                "message": f"位置验证出错: {str(e)}",
                "suggestion": "请检查位置数据",
                "details": {}
            }

    def validate_rotation_continuity_rule(self, transition_result: StateTransitionResult) -> Dict[str, Any]:
        """验证旋转连续性规则"""
        try:
            from_rot = transition_result.start_state.rotation
            to_rot = transition_result.end_state.rotation

            # 计算旋转变化（考虑角度周期性）
            def angle_diff(a1, a2):
                diff = abs(a1 - a2)
                return min(diff, 360 - diff)

            rot_change = max(
                angle_diff(from_rot["x"], to_rot["x"]),
                angle_diff(from_rot["y"], to_rot["y"]),
                angle_diff(from_rot.get("z", 0), to_rot.get("z", 0))
            )

            # 检查是否超过阈值
            max_change = self.performance_thresholds["max_rotation_change"]
            valid = rot_change <= max_change

            # 计算分数
            score = max(0, 1 - rot_change / (max_change * 2))

            # 生成消息和建议
            if valid:
                message = f"旋转变化合理: {rot_change:.1f}°"
                suggestion = ""
            else:
                message = f"旋转变化过大: {rot_change:.1f}° (最大: {max_change}°)"
                suggestion = "建议分解为多个较小的旋转变化"

            return {
                "valid": valid,
                "score": score,
                "weight": 0.2,
                "property": StateProperty.ROTATION,
                "message": message,
                "suggestion": suggestion,
                "details": {
                    "rotation_change": rot_change,
                    "max_change": max_change
                }
            }

        except Exception as e:
            logger.error(f"旋转连续性规则验证失败: {e}")
            return {
                "valid": False,
                "score": 0.0,
                "weight": 0.2,
                "property": StateProperty.ROTATION,
                "message": f"旋转验证出错: {str(e)}",
                "suggestion": "请检查旋转数据",
                "details": {}
            }

    def validate_scale_continuity_rule(self, transition_result: StateTransitionResult) -> Dict[str, Any]:
        """验证缩放连续性规则"""
        try:
            from_scale = transition_result.start_state.scale
            to_scale = transition_result.end_state.scale

            # 计算缩放变化
            scale_change = max(
                abs(to_scale["x"] - from_scale["x"]),
                abs(to_scale["y"] - from_scale["y"]),
                abs(to_scale.get("z", 1) - from_scale.get("z", 1))
            )

            # 检查是否超过阈值
            max_change = self.performance_thresholds["max_scale_change"]
            valid = scale_change <= max_change

            # 计算分数
            score = max(0, 1 - scale_change / (max_change * 2))

            # 生成消息和建议
            if valid:
                message = f"缩放变化合理: {scale_change:.3f}"
                suggestion = ""
            else:
                message = f"缩放变化过大: {scale_change:.3f} (最大: {max_change})"
                suggestion = "建议分解为多个较小的缩放变化"

            return {
                "valid": valid,
                "score": score,
                "weight": 0.2,
                "property": StateProperty.SCALE,
                "message": message,
                "suggestion": suggestion,
                "details": {
                    "scale_change": scale_change,
                    "max_change": max_change
                }
            }

        except Exception as e:
            logger.error(f"缩放连续性规则验证失败: {e}")
            return {
                "valid": False,
                "score": 0.0,
                "weight": 0.2,
                "property": StateProperty.SCALE,
                "message": f"缩放验证出错: {str(e)}",
                "suggestion": "请检查缩放数据",
                "details": {}
            }

    def validate_opacity_continuity_rule(self, transition_result: StateTransitionResult) -> Dict[str, Any]:
        """验证透明度连续性规则"""
        try:
            from_opacity = transition_result.start_state.opacity
            to_opacity = transition_result.end_state.opacity

            # 计算透明度变化
            opacity_change = abs(to_opacity - from_opacity)

            # 检查是否超过阈值
            max_change = self.performance_thresholds["max_opacity_change"]
            valid = opacity_change <= max_change

            # 计算分数
            score = max(0, 1 - opacity_change / (max_change * 2))

            # 生成消息和建议
            if valid:
                message = f"透明度变化合理: {opacity_change:.3f}"
                suggestion = ""
            else:
                message = f"透明度变化过大: {opacity_change:.3f} (最大: {max_change})"
                suggestion = "建议使用渐变透明度过渡"

            return {
                "valid": valid,
                "score": score,
                "weight": 0.2,
                "property": StateProperty.OPACITY,
                "message": message,
                "suggestion": suggestion,
                "details": {
                    "opacity_change": opacity_change,
                    "max_change": max_change
                }
            }

        except Exception as e:
            logger.error(f"透明度连续性规则验证失败: {e}")
            return {
                "valid": False,
                "score": 0.0,
                "weight": 0.2,
                "property": StateProperty.OPACITY,
                "message": f"透明度验证出错: {str(e)}",
                "suggestion": "请检查透明度数据",
                "details": {}
            }

    def validate_performance_impact_rule(self, transition_result: StateTransitionResult) -> Dict[str, Any]:
        """验证性能影响规则"""
        try:
            # 估算性能影响
            performance_score = 1.0 - transition_result.performance_impact

            # 检查过渡时长
            duration = transition_result.estimated_duration
            min_duration = self.performance_thresholds["min_transition_duration"]
            max_duration = self.performance_thresholds["max_transition_duration"]

            duration_valid = min_duration <= duration <= max_duration

            # 综合评估
            valid = performance_score >= 0.5 and duration_valid
            score = performance_score * 0.7 + (0.3 if duration_valid else 0.0)

            # 生成消息和建议
            if valid:
                message = f"性能影响可接受: {transition_result.performance_impact:.2f}"
                suggestion = ""
            else:
                issues = []
                if performance_score < 0.5:
                    issues.append(f"性能影响过高: {transition_result.performance_impact:.2f}")
                if not duration_valid:
                    issues.append(f"过渡时长不合理: {duration:.2f}s")

                message = "; ".join(issues)
                suggestion = "建议优化动画复杂度或调整过渡时长"

            return {
                "valid": valid,
                "score": score,
                "weight": 0.1,
                "property": StateProperty.ANIMATION,
                "message": message,
                "suggestion": suggestion,
                "details": {
                    "performance_impact": transition_result.performance_impact,
                    "duration": duration,
                    "duration_valid": duration_valid
                }
            }

        except Exception as e:
            logger.error(f"性能影响规则验证失败: {e}")
            return {
                "valid": False,
                "score": 0.0,
                "weight": 0.1,
                "property": StateProperty.ANIMATION,
                "message": f"性能验证出错: {str(e)}",
                "suggestion": "请检查性能数据",
                "details": {}
            }

    def validate_visual_coherence_rule(self, transition_result: StateTransitionResult) -> Dict[str, Any]:
        """验证视觉连贯性规则"""
        try:
            # 基于置信度评估视觉连贯性
            confidence = transition_result.confidence

            # 检查中间状态的连贯性
            intermediate_coherence = 1.0
            if transition_result.intermediate_states:
                # 简化的连贯性检查
                for i, state in enumerate(transition_result.intermediate_states):
                    if state.confidence < 0.5:
                        intermediate_coherence *= 0.8

            # 综合评估
            overall_coherence = confidence * intermediate_coherence
            valid = overall_coherence >= 0.6
            score = overall_coherence

            # 生成消息和建议
            if valid:
                message = f"视觉连贯性良好: {overall_coherence:.2f}"
                suggestion = ""
            else:
                message = f"视觉连贯性不足: {overall_coherence:.2f}"
                suggestion = "建议调整过渡策略或增加中间状态"

            return {
                "valid": valid,
                "score": score,
                "weight": 0.1,
                "property": StateProperty.ANIMATION,
                "message": message,
                "suggestion": suggestion,
                "details": {
                    "confidence": confidence,
                    "intermediate_coherence": intermediate_coherence,
                    "overall_coherence": overall_coherence
                }
            }

        except Exception as e:
            logger.error(f"视觉连贯性规则验证失败: {e}")
            return {
                "valid": False,
                "score": 0.0,
                "weight": 0.1,
                "property": StateProperty.ANIMATION,
                "message": f"连贯性验证出错: {str(e)}",
                "suggestion": "请检查连贯性数据",
                "details": {}
            }


class PerfectStateTransitionSystem(QWidget):
    """完美状态衔接系统主组件"""

    # 信号定义
    state_recorded = pyqtSignal(str, str)           # 状态记录信号 (element_id, segment_id)
    validation_completed = pyqtSignal(dict)         # 验证完成信号
    transition_generated = pyqtSignal(dict)         # 转换生成信号
    auto_fix_applied = pyqtSignal(str, dict)        # 自动修复应用信号

    def __init__(self, parent=None):
        super().__init__(parent)

        # 核心组件
        self.state_manager = CoreStateManager()
        self.ai_state_function = AIStateFunction()
        self.transition_validator = StateTransitionValidator()

        # 状态管理
        self.current_element = None
        self.current_segment = None
        self.validation_results = {}
        self.transition_results = {}

        self.setup_ui()
        self.setup_connections()

        logger.info("完美状态衔接系统初始化完成")

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 创建标题
        title_label = QLabel("🔗 完美状态衔接系统")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c5aa0; margin: 10px;")
        layout.addWidget(title_label)

        # 创建主要内容区域
        self.create_state_recording_section(layout)
        self.create_validation_section(layout)
        self.create_transition_section(layout)
        self.create_auto_fix_section(layout)

    def create_state_recording_section(self, layout):
        """创建状态记录区域"""
        recording_group = QGroupBox("📝 状态记录")
        recording_layout = QVBoxLayout(recording_group)

        # 元素和段落选择
        selection_layout = QHBoxLayout()

        selection_layout.addWidget(QLabel("元素:"))
        self.element_combo = QComboBox()
        self.element_combo.setEditable(True)
        self.element_combo.addItems(["小球", "文字", "背景", "按钮", "图片"])
        selection_layout.addWidget(self.element_combo)

        selection_layout.addWidget(QLabel("段落:"))
        self.segment_combo = QComboBox()
        self.segment_combo.setEditable(True)
        self.segment_combo.addItems(["段落1", "段落2", "段落3", "段落4", "段落5"])
        selection_layout.addWidget(self.segment_combo)

        recording_layout.addLayout(selection_layout)

        # 状态属性输入
        properties_layout = QFormLayout()

        # 位置输入
        position_layout = QHBoxLayout()
        self.pos_x_spin = QDoubleSpinBox()
        self.pos_x_spin.setRange(-9999, 9999)
        self.pos_x_spin.setSuffix("px")
        position_layout.addWidget(self.pos_x_spin)

        self.pos_y_spin = QDoubleSpinBox()
        self.pos_y_spin.setRange(-9999, 9999)
        self.pos_y_spin.setSuffix("px")
        position_layout.addWidget(self.pos_y_spin)

        self.pos_z_spin = QDoubleSpinBox()
        self.pos_z_spin.setRange(-9999, 9999)
        self.pos_z_spin.setSuffix("px")
        position_layout.addWidget(self.pos_z_spin)

        properties_layout.addRow("位置 (X,Y,Z):", position_layout)

        # 旋转输入
        rotation_layout = QHBoxLayout()
        self.rot_x_spin = QDoubleSpinBox()
        self.rot_x_spin.setRange(-360, 360)
        self.rot_x_spin.setSuffix("°")
        rotation_layout.addWidget(self.rot_x_spin)

        self.rot_y_spin = QDoubleSpinBox()
        self.rot_y_spin.setRange(-360, 360)
        self.rot_y_spin.setSuffix("°")
        rotation_layout.addWidget(self.rot_y_spin)

        self.rot_z_spin = QDoubleSpinBox()
        self.rot_z_spin.setRange(-360, 360)
        self.rot_z_spin.setSuffix("°")
        rotation_layout.addWidget(self.rot_z_spin)

        properties_layout.addRow("旋转 (X,Y,Z):", rotation_layout)

        # 缩放输入
        scale_layout = QHBoxLayout()
        self.scale_x_spin = QDoubleSpinBox()
        self.scale_x_spin.setRange(0.01, 10.0)
        self.scale_x_spin.setValue(1.0)
        self.scale_x_spin.setSingleStep(0.1)
        scale_layout.addWidget(self.scale_x_spin)

        self.scale_y_spin = QDoubleSpinBox()
        self.scale_y_spin.setRange(0.01, 10.0)
        self.scale_y_spin.setValue(1.0)
        self.scale_y_spin.setSingleStep(0.1)
        scale_layout.addWidget(self.scale_y_spin)

        self.scale_z_spin = QDoubleSpinBox()
        self.scale_z_spin.setRange(0.01, 10.0)
        self.scale_z_spin.setValue(1.0)
        self.scale_z_spin.setSingleStep(0.1)
        scale_layout.addWidget(self.scale_z_spin)

        properties_layout.addRow("缩放 (X,Y,Z):", scale_layout)

        # 透明度输入
        self.opacity_spin = QDoubleSpinBox()
        self.opacity_spin.setRange(0.0, 1.0)
        self.opacity_spin.setValue(1.0)
        self.opacity_spin.setSingleStep(0.1)
        properties_layout.addRow("透明度:", self.opacity_spin)

        recording_layout.addLayout(properties_layout)

        # 记录控制
        record_control_layout = QHBoxLayout()

        self.record_btn = QPushButton("📝 记录状态")
        self.record_btn.clicked.connect(self.record_current_state)
        self.record_btn.setStyleSheet("""
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
        record_control_layout.addWidget(self.record_btn)

        self.template_combo = QComboBox()
        self.template_combo.addItems(["default", "hidden", "scaled_down", "rotated"])
        record_control_layout.addWidget(QLabel("模板:"))
        record_control_layout.addWidget(self.template_combo)

        self.use_template_btn = QPushButton("📋 使用模板")
        self.use_template_btn.clicked.connect(self.use_state_template)
        record_control_layout.addWidget(self.use_template_btn)

        record_control_layout.addStretch()

        recording_layout.addLayout(record_control_layout)

        layout.addWidget(recording_group)

    def create_validation_section(self, layout):
        """创建验证区域"""
        validation_group = QGroupBox("✅ 状态验证")
        validation_layout = QVBoxLayout(validation_group)

        # 验证控制
        validation_control_layout = QHBoxLayout()

        validation_control_layout.addWidget(QLabel("从段落:"))
        self.from_segment_combo = QComboBox()
        self.from_segment_combo.setEditable(True)
        self.from_segment_combo.addItems(["段落1", "段落2", "段落3", "段落4"])
        validation_control_layout.addWidget(self.from_segment_combo)

        validation_control_layout.addWidget(QLabel("到段落:"))
        self.to_segment_combo = QComboBox()
        self.to_segment_combo.setEditable(True)
        self.to_segment_combo.addItems(["段落2", "段落3", "段落4", "段落5"])
        validation_control_layout.addWidget(self.to_segment_combo)

        self.validation_level_combo = QComboBox()
        self.validation_level_combo.addItems(["strict", "standard", "relaxed", "adaptive"])
        self.validation_level_combo.setCurrentText("standard")
        validation_control_layout.addWidget(QLabel("验证级别:"))
        validation_control_layout.addWidget(self.validation_level_combo)

        self.validate_btn = QPushButton("🔍 验证连续性")
        self.validate_btn.clicked.connect(self.validate_state_continuity)
        validation_control_layout.addWidget(self.validate_btn)

        validation_layout.addLayout(validation_control_layout)

        # 验证结果显示
        self.validation_results_text = QTextEdit()
        self.validation_results_text.setMaximumHeight(150)
        self.validation_results_text.setReadOnly(True)
        validation_layout.addWidget(self.validation_results_text)

        # 验证指标
        metrics_layout = QHBoxLayout()

        self.overall_score_bar = QProgressBar()
        self.overall_score_bar.setRange(0, 100)
        metrics_layout.addWidget(QLabel("总分:"))
        metrics_layout.addWidget(self.overall_score_bar)

        self.position_score_bar = QProgressBar()
        self.position_score_bar.setRange(0, 100)
        metrics_layout.addWidget(QLabel("位置:"))
        metrics_layout.addWidget(self.position_score_bar)

        self.rotation_score_bar = QProgressBar()
        self.rotation_score_bar.setRange(0, 100)
        metrics_layout.addWidget(QLabel("旋转:"))
        metrics_layout.addWidget(self.rotation_score_bar)

        validation_layout.addLayout(metrics_layout)

        layout.addWidget(validation_group)

    def create_transition_section(self, layout):
        """创建转换区域"""
        transition_group = QGroupBox("🔄 状态转换")
        transition_layout = QVBoxLayout(transition_group)

        # 转换控制
        transition_control_layout = QHBoxLayout()

        self.transition_strategy_combo = QComboBox()
        self.transition_strategy_combo.addItems(["direct", "interpolated", "smooth", "physics_based", "ai_generated"])
        self.transition_strategy_combo.setCurrentText("smooth")
        transition_control_layout.addWidget(QLabel("转换策略:"))
        transition_control_layout.addWidget(self.transition_strategy_combo)

        self.interpolation_combo = QComboBox()
        self.interpolation_combo.addItems(["linear", "ease_in", "ease_out", "ease_in_out", "bounce", "elastic"])
        self.interpolation_combo.setCurrentText("ease_in_out")
        transition_control_layout.addWidget(QLabel("插值方式:"))
        transition_control_layout.addWidget(self.interpolation_combo)

        self.intermediate_count_spin = QSpinBox()
        self.intermediate_count_spin.setRange(0, 10)
        self.intermediate_count_spin.setValue(3)
        transition_control_layout.addWidget(QLabel("中间状态数:"))
        transition_control_layout.addWidget(self.intermediate_count_spin)

        self.generate_transition_btn = QPushButton("⚡ 生成转换")
        self.generate_transition_btn.clicked.connect(self.generate_state_transition)
        transition_control_layout.addWidget(self.generate_transition_btn)

        transition_layout.addLayout(transition_control_layout)

        # 转换结果显示
        self.transition_results_text = QTextEdit()
        self.transition_results_text.setMaximumHeight(120)
        self.transition_results_text.setReadOnly(True)
        transition_layout.addWidget(self.transition_results_text)

        # 转换预览
        preview_layout = QHBoxLayout()

        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)
        preview_layout.addWidget(QLabel("置信度:"))
        preview_layout.addWidget(self.confidence_bar)

        self.performance_bar = QProgressBar()
        self.performance_bar.setRange(0, 100)
        preview_layout.addWidget(QLabel("性能影响:"))
        preview_layout.addWidget(self.performance_bar)

        transition_layout.addLayout(preview_layout)

        layout.addWidget(transition_group)

    def create_auto_fix_section(self, layout):
        """创建自动修复区域"""
        auto_fix_group = QGroupBox("🔧 智能修复")
        auto_fix_layout = QVBoxLayout(auto_fix_group)

        # 修复建议列表
        self.fix_suggestions_list = QListWidget()
        self.fix_suggestions_list.setMaximumHeight(100)
        auto_fix_layout.addWidget(self.fix_suggestions_list)

        # 修复控制
        fix_control_layout = QHBoxLayout()

        self.apply_fix_btn = QPushButton("✅ 应用修复")
        self.apply_fix_btn.clicked.connect(self.apply_auto_fix)
        self.apply_fix_btn.setEnabled(False)
        fix_control_layout.addWidget(self.apply_fix_btn)

        self.preview_fix_btn = QPushButton("👁️ 预览修复")
        self.preview_fix_btn.clicked.connect(self.preview_auto_fix)
        self.preview_fix_btn.setEnabled(False)
        fix_control_layout.addWidget(self.preview_fix_btn)

        self.clear_fixes_btn = QPushButton("🗑️ 清空建议")
        self.clear_fixes_btn.clicked.connect(self.clear_fix_suggestions)
        fix_control_layout.addWidget(self.clear_fixes_btn)

        fix_control_layout.addStretch()

        # 状态统计
        self.states_count_label = QLabel("已记录状态: 0")
        self.validation_count_label = QLabel("验证次数: 0")
        self.fix_count_label = QLabel("修复次数: 0")

        fix_control_layout.addWidget(self.states_count_label)
        fix_control_layout.addWidget(self.validation_count_label)
        fix_control_layout.addWidget(self.fix_count_label)

        auto_fix_layout.addLayout(fix_control_layout)

        layout.addWidget(auto_fix_group)

    def setup_connections(self):
        """设置信号连接"""
        # 内部信号连接
        self.state_recorded.connect(self.on_state_recorded)
        self.validation_completed.connect(self.on_validation_completed)
        self.transition_generated.connect(self.on_transition_generated)
        self.auto_fix_applied.connect(self.on_auto_fix_applied)

    def record_current_state(self):
        """记录当前状态"""
        try:
            element_id = self.element_combo.currentText().strip()
            segment_id = self.segment_combo.currentText().strip()

            if not element_id or not segment_id:
                QMessageBox.warning(self, "警告", "请选择元素和段落")
                return

            # 创建状态对象
            state = CoreState(
                element_id=element_id,
                timestamp=time.time(),
                segment_id=segment_id,
                position={
                    "x": self.pos_x_spin.value(),
                    "y": self.pos_y_spin.value(),
                    "z": self.pos_z_spin.value()
                },
                rotation={
                    "x": self.rot_x_spin.value(),
                    "y": self.rot_y_spin.value(),
                    "z": self.rot_z_spin.value()
                },
                scale={
                    "x": self.scale_x_spin.value(),
                    "y": self.scale_y_spin.value(),
                    "z": self.scale_z_spin.value()
                },
                opacity=self.opacity_spin.value(),
                source="user_defined",
                confidence=1.0
            )

            # 记录状态
            success = self.state_manager.record_state(state)

            if success:
                self.state_recorded.emit(element_id, segment_id)
                QMessageBox.information(self, "成功", f"状态已记录: {element_id}@{segment_id}")
            else:
                QMessageBox.critical(self, "错误", "状态记录失败")

        except Exception as e:
            logger.error(f"记录当前状态失败: {e}")
            QMessageBox.critical(self, "错误", f"记录状态失败: {str(e)}")

    def use_state_template(self):
        """使用状态模板"""
        try:
            element_id = self.element_combo.currentText().strip()
            segment_id = self.segment_combo.currentText().strip()
            template_name = self.template_combo.currentText()

            if not element_id or not segment_id:
                QMessageBox.warning(self, "警告", "请选择元素和段落")
                return

            # 从模板创建状态
            state = self.ai_state_function.create_state_from_template(
                element_id, segment_id, template_name
            )

            # 更新UI
            self.pos_x_spin.setValue(state.position["x"])
            self.pos_y_spin.setValue(state.position["y"])
            self.pos_z_spin.setValue(state.position["z"])

            self.rot_x_spin.setValue(state.rotation["x"])
            self.rot_y_spin.setValue(state.rotation["y"])
            self.rot_z_spin.setValue(state.rotation["z"])

            self.scale_x_spin.setValue(state.scale["x"])
            self.scale_y_spin.setValue(state.scale["y"])
            self.scale_z_spin.setValue(state.scale["z"])

            self.opacity_spin.setValue(state.opacity)

            # 记录状态
            success = self.state_manager.record_state(state)

            if success:
                self.state_recorded.emit(element_id, segment_id)
                QMessageBox.information(self, "成功", f"模板状态已应用: {template_name}")

        except Exception as e:
            logger.error(f"使用状态模板失败: {e}")
            QMessageBox.critical(self, "错误", f"使用模板失败: {str(e)}")

    def validate_state_continuity(self):
        """验证状态连续性"""
        try:
            element_id = self.element_combo.currentText().strip()
            from_segment = self.from_segment_combo.currentText().strip()
            to_segment = self.to_segment_combo.currentText().strip()
            validation_level_str = self.validation_level_combo.currentText()

            if not element_id or not from_segment or not to_segment:
                QMessageBox.warning(self, "警告", "请选择元素和段落")
                return

            # 转换验证级别
            validation_level = StateValidationLevel(validation_level_str)

            # 执行验证
            validation_result = self.state_manager.validate_state_continuity(
                element_id, from_segment, to_segment, validation_level
            )

            self.validation_results[f"{element_id}_{from_segment}_{to_segment}"] = validation_result

            # 发送信号
            self.validation_completed.emit({
                "element_id": element_id,
                "from_segment": from_segment,
                "to_segment": to_segment,
                "result": validation_result
            })

        except Exception as e:
            logger.error(f"验证状态连续性失败: {e}")
            QMessageBox.critical(self, "错误", f"验证失败: {str(e)}")

    def generate_state_transition(self):
        """生成状态转换"""
        try:
            element_id = self.element_combo.currentText().strip()
            from_segment = self.from_segment_combo.currentText().strip()
            to_segment = self.to_segment_combo.currentText().strip()
            strategy_str = self.transition_strategy_combo.currentText()
            interpolation_str = self.interpolation_combo.currentText()
            intermediate_count = self.intermediate_count_spin.value()

            if not element_id or not from_segment or not to_segment:
                QMessageBox.warning(self, "警告", "请选择元素和段落")
                return

            # 获取状态
            from_state = self.state_manager.get_state(element_id, from_segment)
            to_state = self.state_manager.get_state(element_id, to_segment)

            if not from_state or not to_state:
                QMessageBox.warning(self, "警告", "缺少必要的状态数据")
                return

            # 生成中间状态
            intermediate_states = []
            if intermediate_count > 0:
                intermediate_states = self.ai_state_function.generate_intermediate_states(
                    from_state, to_state, intermediate_count, interpolation_str
                )

            # 创建转换结果
            transition_result = StateTransitionResult(
                success=True,
                transition_strategy=TransitionStrategy(strategy_str),
                start_state=from_state,
                end_state=to_state,
                intermediate_states=intermediate_states,
                confidence=0.85,
                estimated_duration=2.0,
                performance_impact=0.3
            )

            # 验证转换
            validation_result = self.transition_validator.validate_transition(transition_result)
            transition_result.validation_report = validation_result.__dict__

            self.transition_results[f"{element_id}_{from_segment}_{to_segment}"] = transition_result

            # 发送信号
            self.transition_generated.emit({
                "element_id": element_id,
                "from_segment": from_segment,
                "to_segment": to_segment,
                "result": transition_result
            })

        except Exception as e:
            logger.error(f"生成状态转换失败: {e}")
            QMessageBox.critical(self, "错误", f"生成转换失败: {str(e)}")

    def apply_auto_fix(self):
        """应用自动修复"""
        try:
            current_item = self.fix_suggestions_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请选择修复建议")
                return

            suggestion_data = current_item.data(Qt.ItemDataRole.UserRole)
            if not suggestion_data:
                return

            # 应用修复（这里是示例实现）
            element_id = suggestion_data.get("element_id")
            fix_type = suggestion_data.get("fix_type")
            fix_data = suggestion_data.get("fix_data")

            # 发送信号
            self.auto_fix_applied.emit(fix_type, {
                "element_id": element_id,
                "fix_data": fix_data,
                "applied": True
            })

            QMessageBox.information(self, "成功", f"自动修复已应用: {fix_type}")

        except Exception as e:
            logger.error(f"应用自动修复失败: {e}")
            QMessageBox.critical(self, "错误", f"应用修复失败: {str(e)}")

    def preview_auto_fix(self):
        """预览自动修复"""
        try:
            current_item = self.fix_suggestions_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请选择修复建议")
                return

            suggestion_data = current_item.data(Qt.ItemDataRole.UserRole)
            if not suggestion_data:
                return

            # 显示预览对话框
            preview_text = f"""
修复类型: {suggestion_data.get('fix_type', '未知')}
元素: {suggestion_data.get('element_id', '未知')}
修复内容: {suggestion_data.get('description', '无描述')}

修复前状态:
{json.dumps(suggestion_data.get('before_state', {}), indent=2, ensure_ascii=False)}

修复后状态:
{json.dumps(suggestion_data.get('after_state', {}), indent=2, ensure_ascii=False)}
"""

            QMessageBox.information(self, "修复预览", preview_text)

        except Exception as e:
            logger.error(f"预览自动修复失败: {e}")
            QMessageBox.critical(self, "错误", f"预览修复失败: {str(e)}")

    def clear_fix_suggestions(self):
        """清空修复建议"""
        self.fix_suggestions_list.clear()
        self.apply_fix_btn.setEnabled(False)
        self.preview_fix_btn.setEnabled(False)

    def on_state_recorded(self, element_id, segment_id):
        """状态记录处理"""
        try:
            # 更新统计
            total_states = sum(len(states) for states in self.state_manager.states.values())
            self.states_count_label.setText(f"已记录状态: {total_states}")

            logger.info(f"状态记录完成: {element_id}@{segment_id}")

        except Exception as e:
            logger.error(f"处理状态记录失败: {e}")

    def on_validation_completed(self, result):
        """验证完成处理"""
        try:
            validation_result = result["result"]

            # 更新验证结果显示
            result_text = f"验证结果: {'✅ 通过' if validation_result.is_valid else '❌ 失败'}\n"
            result_text += f"总分: {validation_result.overall_score:.2f}\n"
            result_text += f"验证级别: {validation_result.validation_level.value}\n\n"

            if validation_result.issues:
                result_text += "问题:\n"
                for issue in validation_result.issues:
                    result_text += f"• {issue}\n"

            if validation_result.suggestions:
                result_text += "\n建议:\n"
                for suggestion in validation_result.suggestions:
                    result_text += f"• {suggestion}\n"

            self.validation_results_text.setPlainText(result_text)

            # 更新进度条
            self.overall_score_bar.setValue(int(validation_result.overall_score * 100))

            # 更新属性分数
            if StateProperty.POSITION in validation_result.property_checks:
                pos_score = validation_result.property_checks[StateProperty.POSITION]["score"]
                self.position_score_bar.setValue(int(pos_score * 100))

            if StateProperty.ROTATION in validation_result.property_checks:
                rot_score = validation_result.property_checks[StateProperty.ROTATION]["score"]
                self.rotation_score_bar.setValue(int(rot_score * 100))

            # 添加修复建议
            if validation_result.auto_fix_available:
                for suggestion in validation_result.suggestions:
                    self.add_fix_suggestion("状态连续性修复", suggestion, {
                        "element_id": result["element_id"],
                        "fix_type": "continuity_fix",
                        "description": suggestion
                    })

            # 更新统计
            validation_count = len(self.validation_results)
            self.validation_count_label.setText(f"验证次数: {validation_count}")

        except Exception as e:
            logger.error(f"处理验证完成失败: {e}")

    def on_transition_generated(self, result):
        """转换生成处理"""
        try:
            transition_result = result["result"]

            # 更新转换结果显示
            result_text = f"转换策略: {transition_result.transition_strategy.value}\n"
            result_text += f"成功: {'✅ 是' if transition_result.success else '❌ 否'}\n"
            result_text += f"置信度: {transition_result.confidence:.2f}\n"
            result_text += f"预计时长: {transition_result.estimated_duration:.2f}s\n"
            result_text += f"性能影响: {transition_result.performance_impact:.2f}\n"
            result_text += f"中间状态数: {len(transition_result.intermediate_states)}\n"

            self.transition_results_text.setPlainText(result_text)

            # 更新进度条
            self.confidence_bar.setValue(int(transition_result.confidence * 100))
            self.performance_bar.setValue(int((1.0 - transition_result.performance_impact) * 100))

        except Exception as e:
            logger.error(f"处理转换生成失败: {e}")

    def on_auto_fix_applied(self, fix_type, fix_data):
        """自动修复应用处理"""
        try:
            # 更新统计
            fix_count = self.fix_suggestions_list.count()
            self.fix_count_label.setText(f"修复次数: {fix_count}")

            logger.info(f"自动修复应用: {fix_type}")

        except Exception as e:
            logger.error(f"处理自动修复应用失败: {e}")

    def add_fix_suggestion(self, title: str, description: str, data: Dict[str, Any]):
        """添加修复建议"""
        try:
            item = QListWidgetItem(f"{title}: {description}")
            item.setData(Qt.ItemDataRole.UserRole, data)
            self.fix_suggestions_list.addItem(item)

            # 启用修复按钮
            self.apply_fix_btn.setEnabled(True)
            self.preview_fix_btn.setEnabled(True)

        except Exception as e:
            logger.error(f"添加修复建议失败: {e}")

    def get_state_manager(self) -> CoreStateManager:
        """获取状态管理器"""
        return self.state_manager

    def get_validation_results(self) -> Dict[str, ValidationResult]:
        """获取验证结果"""
        return self.validation_results.copy()

    def get_transition_results(self) -> Dict[str, StateTransitionResult]:
        """获取转换结果"""
        return self.transition_results.copy()

    def clear_all_data(self):
        """清空所有数据"""
        try:
            self.state_manager.clear_states()
            self.validation_results.clear()
            self.transition_results.clear()

            # 重置UI
            self.validation_results_text.clear()
            self.transition_results_text.clear()
            self.clear_fix_suggestions()

            # 重置进度条
            self.overall_score_bar.setValue(0)
            self.position_score_bar.setValue(0)
            self.rotation_score_bar.setValue(0)
            self.confidence_bar.setValue(0)
            self.performance_bar.setValue(0)

            # 重置统计
            self.states_count_label.setText("已记录状态: 0")
            self.validation_count_label.setText("验证次数: 0")
            self.fix_count_label.setText("修复次数: 0")

            logger.info("所有数据已清空")

        except Exception as e:
            logger.error(f"清空所有数据失败: {e}")
