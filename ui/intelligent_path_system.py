"""
AI Animation Studio - 智能路径系统
实现拖拽轨迹、点击路径、贝塞尔曲线等多种路径输入模式
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsPathItem,
                             QGraphicsEllipseItem, QToolButton, QButtonGroup, QFrame,
                             QSlider, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
                             QApplication, QMenu, QSizePolicy, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QPointF, QRectF, QPropertyAnimation
from PyQt6.QtGui import (QFont, QColor, QIcon, QPainter, QBrush, QPen, QPainterPath,
                         QPolygonF, QCursor, QPixmap, QTransform)

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
import json
import time
import math
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np

from core.logger import get_logger
from core.data_structures import Point, AnimationPath, PathType

logger = get_logger("intelligent_path_system")


class PathInputMode(Enum):
    """路径输入模式枚举"""
    DRAG_TRACE = "drag_trace"           # 拖拽轨迹模式
    CLICK_PATH = "click_path"           # 点击路径模式
    BEZIER_CURVE = "bezier_curve"       # 贝塞尔曲线模式
    PRESET_PATH = "preset_path"         # 预设路径模式


class PathPresetType(Enum):
    """预设路径类型枚举"""
    LINEAR = "linear"                   # 直线
    PARABOLIC = "parabolic"            # 抛物线
    SPIRAL = "spiral"                  # 螺旋线
    WAVE = "wave"                      # 波浪线
    BOUNCE = "bounce"                  # 弹跳线
    CIRCLE = "circle"                  # 圆形
    FIGURE_EIGHT = "figure_eight"      # 8字形
    ZIGZAG = "zigzag"                  # 锯齿线


@dataclass
class PathAnalysisResult:
    """路径分析结果"""
    motion_intent: str = ""             # 运动意图
    rhythm_pattern: str = ""            # 节奏模式
    geometric_shape: str = ""           # 几何形状
    suggested_easing: str = "ease"      # 建议缓动
    complexity_level: str = "medium"    # 复杂度级别
    estimated_duration: float = 2.0     # 预估时长
    natural_description: str = ""       # 自然语言描述
    confidence: float = 0.8             # 分析置信度


@dataclass
class PathCreationContext:
    """路径创建上下文"""
    mode: PathInputMode
    canvas_size: Tuple[int, int]
    element_size: Tuple[int, int] = (50, 50)
    start_position: Optional[Point] = None
    target_position: Optional[Point] = None
    creation_time: datetime = field(default_factory=datetime.now)
    user_preferences: Dict[str, Any] = field(default_factory=dict)


class PathAnalyzer:
    """路径分析器"""
    
    def __init__(self):
        self.motion_patterns = self.initialize_motion_patterns()
        self.geometric_analyzers = self.initialize_geometric_analyzers()
        
        logger.info("路径分析器初始化完成")
    
    def initialize_motion_patterns(self) -> Dict[str, Dict[str, Any]]:
        """初始化运动模式"""
        return {
            "linear": {
                "description": "直线运动",
                "characteristics": ["constant_direction", "uniform_spacing"],
                "suggested_easing": "linear",
                "typical_duration": 1.5
            },
            "accelerated": {
                "description": "加速运动",
                "characteristics": ["increasing_spacing", "forward_direction"],
                "suggested_easing": "ease-in",
                "typical_duration": 2.0
            },
            "decelerated": {
                "description": "减速运动",
                "characteristics": ["decreasing_spacing", "forward_direction"],
                "suggested_easing": "ease-out",
                "typical_duration": 2.0
            },
            "bouncing": {
                "description": "弹跳运动",
                "characteristics": ["vertical_oscillation", "parabolic_segments"],
                "suggested_easing": "bounce",
                "typical_duration": 3.0
            },
            "circular": {
                "description": "圆周运动",
                "characteristics": ["curved_path", "consistent_radius"],
                "suggested_easing": "ease-in-out",
                "typical_duration": 4.0
            },
            "oscillating": {
                "description": "振荡运动",
                "characteristics": ["back_and_forth", "wave_pattern"],
                "suggested_easing": "elastic",
                "typical_duration": 3.5
            }
        }
    
    def initialize_geometric_analyzers(self) -> Dict[str, Callable]:
        """初始化几何分析器"""
        return {
            "linearity": self.analyze_linearity,
            "curvature": self.analyze_curvature,
            "symmetry": self.analyze_symmetry,
            "periodicity": self.analyze_periodicity,
            "complexity": self.analyze_complexity
        }
    
    def analyze_path(self, path: AnimationPath, context: PathCreationContext) -> PathAnalysisResult:
        """分析路径"""
        try:
            if not path.points or len(path.points) < 2:
                return PathAnalysisResult(
                    motion_intent="静止",
                    natural_description="无有效路径数据",
                    confidence=0.0
                )
            
            result = PathAnalysisResult()
            
            # 几何分析
            geometric_features = self.analyze_geometric_features(path.points)
            
            # 运动分析
            motion_features = self.analyze_motion_features(path.points)
            
            # 综合分析
            result.geometric_shape = self.determine_geometric_shape(geometric_features)
            result.motion_intent = self.determine_motion_intent(motion_features)
            result.rhythm_pattern = self.determine_rhythm_pattern(motion_features)
            result.suggested_easing = self.suggest_easing(motion_features)
            result.complexity_level = self.determine_complexity(geometric_features, motion_features)
            result.estimated_duration = self.estimate_duration(path, motion_features)
            result.natural_description = self.generate_natural_description(result, path)
            result.confidence = self.calculate_confidence(geometric_features, motion_features)
            
            return result
            
        except Exception as e:
            logger.error(f"路径分析失败: {e}")
            return PathAnalysisResult(
                motion_intent="未知",
                natural_description="路径分析失败",
                confidence=0.0
            )
    
    def analyze_geometric_features(self, points: List[Point]) -> Dict[str, float]:
        """分析几何特征"""
        try:
            features = {}
            
            # 线性度分析
            features["linearity"] = self.analyze_linearity(points)
            
            # 曲率分析
            features["curvature"] = self.analyze_curvature(points)
            
            # 对称性分析
            features["symmetry"] = self.analyze_symmetry(points)
            
            # 周期性分析
            features["periodicity"] = self.analyze_periodicity(points)
            
            # 复杂度分析
            features["complexity"] = self.analyze_complexity(points)
            
            return features
            
        except Exception as e:
            logger.error(f"几何特征分析失败: {e}")
            return {}
    
    def analyze_motion_features(self, points: List[Point]) -> Dict[str, float]:
        """分析运动特征"""
        try:
            features = {}
            
            if len(points) < 3:
                return features
            
            # 计算速度变化
            velocities = []
            for i in range(1, len(points)):
                dx = points[i].x - points[i-1].x
                dy = points[i].y - points[i-1].y
                velocity = math.sqrt(dx*dx + dy*dy)
                velocities.append(velocity)
            
            if velocities:
                # 速度统计
                avg_velocity = sum(velocities) / len(velocities)
                max_velocity = max(velocities)
                min_velocity = min(velocities)
                
                features["avg_velocity"] = avg_velocity
                features["velocity_variation"] = (max_velocity - min_velocity) / avg_velocity if avg_velocity > 0 else 0
                
                # 加速度分析
                if len(velocities) > 1:
                    accelerations = []
                    for i in range(1, len(velocities)):
                        acceleration = velocities[i] - velocities[i-1]
                        accelerations.append(acceleration)
                    
                    if accelerations:
                        features["avg_acceleration"] = sum(accelerations) / len(accelerations)
                        features["acceleration_consistency"] = 1.0 - (max(accelerations) - min(accelerations)) / (max(accelerations) + 0.001)
            
            # 方向变化分析
            direction_changes = 0
            for i in range(2, len(points)):
                v1 = (points[i-1].x - points[i-2].x, points[i-1].y - points[i-2].y)
                v2 = (points[i].x - points[i-1].x, points[i].y - points[i-1].y)
                
                # 计算角度变化
                dot_product = v1[0]*v2[0] + v1[1]*v2[1]
                mag1 = math.sqrt(v1[0]*v1[0] + v1[1]*v1[1])
                mag2 = math.sqrt(v2[0]*v2[0] + v2[1]*v2[1])
                
                if mag1 > 0 and mag2 > 0:
                    cos_angle = dot_product / (mag1 * mag2)
                    cos_angle = max(-1, min(1, cos_angle))  # 限制范围
                    angle = math.acos(cos_angle)
                    
                    if angle > math.pi / 4:  # 45度以上认为是方向变化
                        direction_changes += 1
            
            features["direction_changes"] = direction_changes / max(1, len(points) - 2)
            
            return features
            
        except Exception as e:
            logger.error(f"运动特征分析失败: {e}")
            return {}
    
    def analyze_linearity(self, points: List[Point]) -> float:
        """分析线性度"""
        try:
            if len(points) < 3:
                return 1.0
            
            # 计算起点到终点的直线
            start, end = points[0], points[-1]
            line_length = math.sqrt((end.x - start.x)**2 + (end.y - start.y)**2)
            
            if line_length == 0:
                return 0.0
            
            # 计算所有点到直线的距离
            total_deviation = 0.0
            for point in points[1:-1]:
                # 点到直线距离公式
                A = end.y - start.y
                B = start.x - end.x
                C = end.x * start.y - start.x * end.y
                
                distance = abs(A * point.x + B * point.y + C) / math.sqrt(A*A + B*B)
                total_deviation += distance
            
            # 归一化线性度分数
            avg_deviation = total_deviation / max(1, len(points) - 2)
            linearity = max(0.0, 1.0 - avg_deviation / (line_length * 0.1))
            
            return min(1.0, linearity)
            
        except Exception as e:
            logger.error(f"线性度分析失败: {e}")
            return 0.5


class PathPresetGenerator:
    """预设路径生成器"""

    def __init__(self):
        self.preset_generators = {
            PathPresetType.LINEAR: self.generate_linear_path,
            PathPresetType.PARABOLIC: self.generate_parabolic_path,
            PathPresetType.SPIRAL: self.generate_spiral_path,
            PathPresetType.WAVE: self.generate_wave_path,
            PathPresetType.BOUNCE: self.generate_bounce_path,
            PathPresetType.CIRCLE: self.generate_circle_path,
            PathPresetType.FIGURE_EIGHT: self.generate_figure_eight_path,
            PathPresetType.ZIGZAG: self.generate_zigzag_path
        }

        logger.info("预设路径生成器初始化完成")

    def generate_preset_path(self, preset_type: PathPresetType,
                           start_point: Point, end_point: Point,
                           parameters: Dict[str, Any] = None) -> AnimationPath:
        """生成预设路径"""
        try:
            if preset_type not in self.preset_generators:
                raise ValueError(f"不支持的预设类型: {preset_type}")

            generator = self.preset_generators[preset_type]
            path = generator(start_point, end_point, parameters or {})

            path.path_type = PathType.PRESET
            path.creation_method = "preset"

            return path

        except Exception as e:
            logger.error(f"生成预设路径失败: {e}")
            return AnimationPath()

    def generate_linear_path(self, start: Point, end: Point, params: Dict[str, Any]) -> AnimationPath:
        """生成直线路径"""
        path = AnimationPath()
        path.points = [start, end]
        path.path_type = PathType.LINEAR
        path._calculate_length()
        return path

    def generate_parabolic_path(self, start: Point, end: Point, params: Dict[str, Any]) -> AnimationPath:
        """生成抛物线路径"""
        path = AnimationPath()

        # 抛物线参数
        height = params.get("height", 100)  # 抛物线高度
        segments = params.get("segments", 20)  # 分段数

        # 计算抛物线路径
        dx = end.x - start.x
        dy = end.y - start.y

        for i in range(segments + 1):
            t = i / segments

            # 抛物线公式: y = -4h*t*(t-1) + start_y + t*dy
            x = start.x + t * dx
            y = start.y + t * dy - 4 * height * t * (t - 1)

            path.points.append(Point(x, y))

        path.path_type = PathType.CURVED
        path._calculate_length()
        return path

    def generate_spiral_path(self, start: Point, end: Point, params: Dict[str, Any]) -> AnimationPath:
        """生成螺旋路径"""
        path = AnimationPath()

        # 螺旋参数
        turns = params.get("turns", 2)  # 圈数
        segments = params.get("segments", 50)  # 分段数

        # 计算螺旋中心和半径
        center_x = (start.x + end.x) / 2
        center_y = (start.y + end.y) / 2
        max_radius = math.sqrt((end.x - start.x)**2 + (end.y - start.y)**2) / 2

        for i in range(segments + 1):
            t = i / segments
            angle = t * turns * 2 * math.pi
            radius = max_radius * (1 - t)  # 半径逐渐减小

            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            path.points.append(Point(x, y))

        path.path_type = PathType.CURVED
        path._calculate_length()
        return path

    def generate_wave_path(self, start: Point, end: Point, params: Dict[str, Any]) -> AnimationPath:
        """生成波浪路径"""
        path = AnimationPath()

        # 波浪参数
        amplitude = params.get("amplitude", 50)  # 振幅
        frequency = params.get("frequency", 2)   # 频率
        segments = params.get("segments", 30)    # 分段数

        dx = end.x - start.x
        dy = end.y - start.y

        for i in range(segments + 1):
            t = i / segments

            x = start.x + t * dx
            y = start.y + t * dy + amplitude * math.sin(t * frequency * 2 * math.pi)

            path.points.append(Point(x, y))

        path.path_type = PathType.CURVED
        path._calculate_length()
        return path

    def generate_bounce_path(self, start: Point, end: Point, params: Dict[str, Any]) -> AnimationPath:
        """生成弹跳路径"""
        path = AnimationPath()

        # 弹跳参数
        bounces = params.get("bounces", 3)       # 弹跳次数
        height = params.get("height", 80)        # 弹跳高度
        segments = params.get("segments", 40)    # 分段数

        dx = end.x - start.x
        dy = end.y - start.y

        for i in range(segments + 1):
            t = i / segments

            # 弹跳效果：使用正弦函数模拟
            bounce_factor = abs(math.sin(t * bounces * math.pi))
            bounce_height = height * bounce_factor * (1 - t)  # 高度逐渐减小

            x = start.x + t * dx
            y = start.y + t * dy - bounce_height

            path.points.append(Point(x, y))

        path.path_type = PathType.CURVED
        path._calculate_length()
        return path

    def generate_circle_path(self, start: Point, end: Point, params: Dict[str, Any]) -> AnimationPath:
        """生成圆形路径"""
        path = AnimationPath()

        # 圆形参数
        segments = params.get("segments", 36)  # 分段数
        clockwise = params.get("clockwise", True)  # 顺时针

        # 计算圆心和半径
        center_x = (start.x + end.x) / 2
        center_y = (start.y + end.y) / 2
        radius = math.sqrt((end.x - start.x)**2 + (end.y - start.y)**2) / 2

        # 起始角度
        start_angle = math.atan2(start.y - center_y, start.x - center_x)

        for i in range(segments + 1):
            t = i / segments
            angle_offset = t * 2 * math.pi
            if not clockwise:
                angle_offset = -angle_offset

            angle = start_angle + angle_offset
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            path.points.append(Point(x, y))

        path.path_type = PathType.CURVED
        path._calculate_length()
        return path

    def generate_figure_eight_path(self, start: Point, end: Point, params: Dict[str, Any]) -> AnimationPath:
        """生成8字形路径"""
        path = AnimationPath()

        # 8字形参数
        segments = params.get("segments", 50)  # 分段数
        width = params.get("width", abs(end.x - start.x))
        height = params.get("height", abs(end.y - start.y))

        center_x = (start.x + end.x) / 2
        center_y = (start.y + end.y) / 2

        for i in range(segments + 1):
            t = i / segments * 2 * math.pi

            # 8字形参数方程
            x = center_x + (width / 2) * math.sin(t)
            y = center_y + (height / 2) * math.sin(2 * t)

            path.points.append(Point(x, y))

        path.path_type = PathType.CURVED
        path._calculate_length()
        return path

    def generate_zigzag_path(self, start: Point, end: Point, params: Dict[str, Any]) -> AnimationPath:
        """生成锯齿路径"""
        path = AnimationPath()

        # 锯齿参数
        peaks = params.get("peaks", 4)           # 锯齿数
        amplitude = params.get("amplitude", 50)   # 振幅

        dx = end.x - start.x
        dy = end.y - start.y

        # 每个锯齿包含上升和下降两个点
        segments = peaks * 2

        for i in range(segments + 1):
            t = i / segments

            # 锯齿波形
            zigzag_t = (i % 2) * 2 - 1  # -1 或 1
            zigzag_offset = amplitude * zigzag_t

            x = start.x + t * dx
            y = start.y + t * dy + zigzag_offset

            path.points.append(Point(x, y))

        # 确保终点正确
        path.points[-1] = end

        path.path_type = PathType.CURVED
        path._calculate_length()
        return path

    def get_preset_parameters(self, preset_type: PathPresetType) -> Dict[str, Dict[str, Any]]:
        """获取预设参数定义"""
        return {
            PathPresetType.LINEAR: {},
            PathPresetType.PARABOLIC: {
                "height": {"type": "float", "default": 100, "min": 0, "max": 500, "description": "抛物线高度"},
                "segments": {"type": "int", "default": 20, "min": 5, "max": 50, "description": "分段数"}
            },
            PathPresetType.SPIRAL: {
                "turns": {"type": "float", "default": 2, "min": 0.5, "max": 10, "description": "螺旋圈数"},
                "segments": {"type": "int", "default": 50, "min": 10, "max": 100, "description": "分段数"}
            },
            PathPresetType.WAVE: {
                "amplitude": {"type": "float", "default": 50, "min": 10, "max": 200, "description": "波浪振幅"},
                "frequency": {"type": "float", "default": 2, "min": 0.5, "max": 10, "description": "波浪频率"},
                "segments": {"type": "int", "default": 30, "min": 10, "max": 100, "description": "分段数"}
            },
            PathPresetType.BOUNCE: {
                "bounces": {"type": "int", "default": 3, "min": 1, "max": 10, "description": "弹跳次数"},
                "height": {"type": "float", "default": 80, "min": 20, "max": 300, "description": "弹跳高度"},
                "segments": {"type": "int", "default": 40, "min": 10, "max": 100, "description": "分段数"}
            },
            PathPresetType.CIRCLE: {
                "segments": {"type": "int", "default": 36, "min": 8, "max": 72, "description": "分段数"},
                "clockwise": {"type": "bool", "default": True, "description": "顺时针方向"}
            },
            PathPresetType.FIGURE_EIGHT: {
                "segments": {"type": "int", "default": 50, "min": 20, "max": 100, "description": "分段数"},
                "width": {"type": "float", "default": 200, "min": 50, "max": 500, "description": "宽度"},
                "height": {"type": "float", "default": 100, "min": 50, "max": 300, "description": "高度"}
            },
            PathPresetType.ZIGZAG: {
                "peaks": {"type": "int", "default": 4, "min": 2, "max": 20, "description": "锯齿数"},
                "amplitude": {"type": "float", "default": 50, "min": 10, "max": 200, "description": "振幅"}
            }
        }.get(preset_type, {})


class PathOptimizer:
    """路径优化器"""

    def __init__(self):
        self.optimization_methods = {
            "smooth": self.smooth_path,
            "simplify": self.simplify_path,
            "interpolate": self.interpolate_path,
            "bezier_fit": self.fit_bezier_curve
        }

        logger.info("路径优化器初始化完成")

    def optimize_path(self, path: AnimationPath, method: str = "smooth",
                     parameters: Dict[str, Any] = None) -> AnimationPath:
        """优化路径"""
        try:
            if method not in self.optimization_methods:
                logger.warning(f"未知的优化方法: {method}")
                return path

            optimizer = self.optimization_methods[method]
            optimized_path = optimizer(path, parameters or {})

            # 重新计算路径长度
            optimized_path._calculate_length()

            return optimized_path

        except Exception as e:
            logger.error(f"路径优化失败: {e}")
            return path

    def smooth_path(self, path: AnimationPath, params: Dict[str, Any]) -> AnimationPath:
        """平滑路径"""
        try:
            if len(path.points) < 3:
                return path

            smoothed_path = AnimationPath()
            smoothed_path.path_id = path.path_id
            smoothed_path.path_type = path.path_type
            smoothed_path.creation_method = path.creation_method

            # 平滑参数
            window_size = params.get("window_size", 3)
            iterations = params.get("iterations", 1)

            points = path.points.copy()

            for _ in range(iterations):
                smoothed_points = [points[0]]  # 保留起点

                for i in range(1, len(points) - 1):
                    # 计算窗口范围
                    start_idx = max(0, i - window_size // 2)
                    end_idx = min(len(points), i + window_size // 2 + 1)

                    # 计算平均位置
                    window_points = points[start_idx:end_idx]
                    avg_x = sum(p.x for p in window_points) / len(window_points)
                    avg_y = sum(p.y for p in window_points) / len(window_points)

                    smoothed_points.append(Point(avg_x, avg_y))

                smoothed_points.append(points[-1])  # 保留终点
                points = smoothed_points

            smoothed_path.points = points
            return smoothed_path

        except Exception as e:
            logger.error(f"路径平滑失败: {e}")
            return path

    def simplify_path(self, path: AnimationPath, params: Dict[str, Any]) -> AnimationPath:
        """简化路径（道格拉斯-普克算法）"""
        try:
            if len(path.points) < 3:
                return path

            simplified_path = AnimationPath()
            simplified_path.path_id = path.path_id
            simplified_path.path_type = path.path_type
            simplified_path.creation_method = path.creation_method

            # 简化参数
            tolerance = params.get("tolerance", 5.0)

            # 道格拉斯-普克算法
            simplified_points = self.douglas_peucker(path.points, tolerance)
            simplified_path.points = simplified_points

            return simplified_path

        except Exception as e:
            logger.error(f"路径简化失败: {e}")
            return path

    def douglas_peucker(self, points: List[Point], tolerance: float) -> List[Point]:
        """道格拉斯-普克算法实现"""
        try:
            if len(points) <= 2:
                return points

            # 找到距离起点终点连线最远的点
            start, end = points[0], points[-1]
            max_distance = 0
            max_index = 0

            for i in range(1, len(points) - 1):
                distance = self.point_to_line_distance(points[i], start, end)
                if distance > max_distance:
                    max_distance = distance
                    max_index = i

            # 如果最大距离小于容差，简化为直线
            if max_distance < tolerance:
                return [start, end]

            # 递归处理两段
            left_points = self.douglas_peucker(points[:max_index + 1], tolerance)
            right_points = self.douglas_peucker(points[max_index:], tolerance)

            # 合并结果（去除重复点）
            return left_points[:-1] + right_points

        except Exception as e:
            logger.error(f"道格拉斯-普克算法失败: {e}")
            return points

    def point_to_line_distance(self, point: Point, line_start: Point, line_end: Point) -> float:
        """计算点到直线的距离"""
        try:
            # 直线方程 Ax + By + C = 0
            A = line_end.y - line_start.y
            B = line_start.x - line_end.x
            C = line_end.x * line_start.y - line_start.x * line_end.y

            # 点到直线距离公式
            distance = abs(A * point.x + B * point.y + C) / math.sqrt(A * A + B * B)
            return distance

        except Exception as e:
            logger.error(f"点到直线距离计算失败: {e}")
            return 0.0

    def interpolate_path(self, path: AnimationPath, params: Dict[str, Any]) -> AnimationPath:
        """插值路径"""
        try:
            if len(path.points) < 2:
                return path

            interpolated_path = AnimationPath()
            interpolated_path.path_id = path.path_id
            interpolated_path.path_type = path.path_type
            interpolated_path.creation_method = path.creation_method

            # 插值参数
            density = params.get("density", 2)  # 插值密度

            interpolated_points = []

            for i in range(len(path.points) - 1):
                current = path.points[i]
                next_point = path.points[i + 1]

                interpolated_points.append(current)

                # 在两点间插值
                for j in range(1, density):
                    t = j / density
                    x = current.x + t * (next_point.x - current.x)
                    y = current.y + t * (next_point.y - current.y)
                    interpolated_points.append(Point(x, y))

            interpolated_points.append(path.points[-1])  # 添加终点
            interpolated_path.points = interpolated_points

            return interpolated_path

        except Exception as e:
            logger.error(f"路径插值失败: {e}")
            return path

    def fit_bezier_curve(self, path: AnimationPath, params: Dict[str, Any]) -> AnimationPath:
        """拟合贝塞尔曲线"""
        try:
            if len(path.points) < 3:
                return path

            bezier_path = AnimationPath()
            bezier_path.path_id = path.path_id
            bezier_path.path_type = PathType.BEZIER
            bezier_path.creation_method = path.creation_method

            # 贝塞尔拟合参数
            segments = params.get("segments", 50)

            # 简化的贝塞尔拟合：使用起点、终点和中间控制点
            start = path.points[0]
            end = path.points[-1]

            # 计算控制点（使用路径中点的平均位置）
            if len(path.points) >= 3:
                mid_points = path.points[1:-1]
                control_x = sum(p.x for p in mid_points) / len(mid_points)
                control_y = sum(p.y for p in mid_points) / len(mid_points)
                control_point = Point(control_x, control_y)

                bezier_path.control_points = [control_point]

            # 生成贝塞尔曲线点
            bezier_points = []
            for i in range(segments + 1):
                t = i / segments

                if bezier_path.control_points:
                    # 二次贝塞尔曲线
                    control = bezier_path.control_points[0]
                    x = (1-t)**2 * start.x + 2*(1-t)*t * control.x + t**2 * end.x
                    y = (1-t)**2 * start.y + 2*(1-t)*t * control.y + t**2 * end.y
                else:
                    # 线性插值
                    x = start.x + t * (end.x - start.x)
                    y = start.y + t * (end.y - start.y)

                bezier_points.append(Point(x, y))

            bezier_path.points = bezier_points
            return bezier_path

        except Exception as e:
            logger.error(f"贝塞尔曲线拟合失败: {e}")
            return path
    
    def analyze_curvature(self, points: List[Point]) -> float:
        """分析曲率"""
        try:
            if len(points) < 3:
                return 0.0
            
            total_curvature = 0.0
            valid_points = 0
            
            for i in range(1, len(points) - 1):
                p1, p2, p3 = points[i-1], points[i], points[i+1]
                
                # 计算三点形成的角度
                v1 = (p2.x - p1.x, p2.y - p1.y)
                v2 = (p3.x - p2.x, p3.y - p2.y)
                
                mag1 = math.sqrt(v1[0]*v1[0] + v1[1]*v1[1])
                mag2 = math.sqrt(v2[0]*v2[0] + v2[1]*v2[1])
                
                if mag1 > 0 and mag2 > 0:
                    cos_angle = (v1[0]*v2[0] + v1[1]*v2[1]) / (mag1 * mag2)
                    cos_angle = max(-1, min(1, cos_angle))
                    angle = math.acos(cos_angle)
                    
                    # 曲率近似为角度变化
                    curvature = angle / (mag1 + mag2) * 2
                    total_curvature += curvature
                    valid_points += 1
            
            return total_curvature / max(1, valid_points)
            
        except Exception as e:
            logger.error(f"曲率分析失败: {e}")
            return 0.0
    
    def analyze_symmetry(self, points: List[Point]) -> float:
        """分析对称性"""
        try:
            if len(points) < 4:
                return 0.0
            
            # 计算路径中心点
            center_x = sum(p.x for p in points) / len(points)
            center_y = sum(p.y for p in points) / len(points)
            
            # 检查点对称性
            symmetry_score = 0.0
            comparisons = 0
            
            for i in range(len(points) // 2):
                p1 = points[i]
                p2 = points[-(i+1)]
                
                # 计算点到中心的距离
                d1 = math.sqrt((p1.x - center_x)**2 + (p1.y - center_y)**2)
                d2 = math.sqrt((p2.x - center_x)**2 + (p2.y - center_y)**2)
                
                # 对称性评分
                if d1 + d2 > 0:
                    similarity = 1.0 - abs(d1 - d2) / (d1 + d2)
                    symmetry_score += similarity
                    comparisons += 1
            
            return symmetry_score / max(1, comparisons)
            
        except Exception as e:
            logger.error(f"对称性分析失败: {e}")
            return 0.0
    
    def analyze_periodicity(self, points: List[Point]) -> float:
        """分析周期性"""
        try:
            if len(points) < 6:
                return 0.0
            
            # 简化的周期性检测
            # 检查Y坐标的周期性变化
            y_values = [p.y for p in points]
            
            # 寻找局部极值
            peaks = []
            valleys = []
            
            for i in range(1, len(y_values) - 1):
                if y_values[i] > y_values[i-1] and y_values[i] > y_values[i+1]:
                    peaks.append(i)
                elif y_values[i] < y_values[i-1] and y_values[i] < y_values[i+1]:
                    valleys.append(i)
            
            # 计算周期性分数
            if len(peaks) >= 2 or len(valleys) >= 2:
                # 检查峰值间距的一致性
                if len(peaks) >= 2:
                    intervals = [peaks[i+1] - peaks[i] for i in range(len(peaks)-1)]
                    if intervals:
                        avg_interval = sum(intervals) / len(intervals)
                        interval_consistency = 1.0 - (max(intervals) - min(intervals)) / max(1, avg_interval)
                        return max(0.0, interval_consistency)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"周期性分析失败: {e}")
            return 0.0
    
    def analyze_complexity(self, points: List[Point]) -> float:
        """分析复杂度"""
        try:
            if len(points) < 2:
                return 0.0
            
            # 基于路径长度和点数的复杂度
            path_length = 0.0
            for i in range(1, len(points)):
                dx = points[i].x - points[i-1].x
                dy = points[i].y - points[i-1].y
                path_length += math.sqrt(dx*dx + dy*dy)
            
            # 直线距离
            start, end = points[0], points[-1]
            direct_distance = math.sqrt((end.x - start.x)**2 + (end.y - start.y)**2)
            
            # 复杂度 = 路径长度 / 直线距离
            if direct_distance > 0:
                complexity = path_length / direct_distance
                return min(1.0, (complexity - 1.0) / 2.0)  # 归一化到0-1
            
            return 0.0
            
        except Exception as e:
            logger.error(f"复杂度分析失败: {e}")
            return 0.0
    
    def determine_geometric_shape(self, features: Dict[str, float]) -> str:
        """确定几何形状"""
        try:
            linearity = features.get("linearity", 0.0)
            curvature = features.get("curvature", 0.0)
            symmetry = features.get("symmetry", 0.0)
            periodicity = features.get("periodicity", 0.0)
            
            if linearity > 0.8:
                return "直线"
            elif periodicity > 0.6:
                return "波浪线"
            elif symmetry > 0.7 and curvature > 0.3:
                return "圆弧"
            elif curvature > 0.5:
                return "曲线"
            else:
                return "复合路径"
                
        except Exception as e:
            logger.error(f"几何形状确定失败: {e}")
            return "未知形状"
    
    def determine_motion_intent(self, features: Dict[str, float]) -> str:
        """确定运动意图"""
        try:
            velocity_variation = features.get("velocity_variation", 0.0)
            avg_acceleration = features.get("avg_acceleration", 0.0)
            direction_changes = features.get("direction_changes", 0.0)
            
            if abs(avg_acceleration) < 0.1 and velocity_variation < 0.3:
                return "匀速运动"
            elif avg_acceleration > 0.2:
                return "加速运动"
            elif avg_acceleration < -0.2:
                return "减速运动"
            elif direction_changes > 0.3:
                return "变向运动"
            else:
                return "自然运动"
                
        except Exception as e:
            logger.error(f"运动意图确定失败: {e}")
            return "未知运动"
    
    def determine_rhythm_pattern(self, features: Dict[str, float]) -> str:
        """确定节奏模式"""
        try:
            velocity_variation = features.get("velocity_variation", 0.0)
            acceleration_consistency = features.get("acceleration_consistency", 0.0)
            
            if velocity_variation < 0.2:
                return "稳定节奏"
            elif acceleration_consistency > 0.7:
                return "渐变节奏"
            elif velocity_variation > 0.6:
                return "跳跃节奏"
            else:
                return "自然节奏"
                
        except Exception as e:
            logger.error(f"节奏模式确定失败: {e}")
            return "未知节奏"
    
    def suggest_easing(self, features: Dict[str, float]) -> str:
        """建议缓动函数"""
        try:
            avg_acceleration = features.get("avg_acceleration", 0.0)
            velocity_variation = features.get("velocity_variation", 0.0)
            
            if abs(avg_acceleration) < 0.1:
                return "linear"
            elif avg_acceleration > 0.2:
                return "ease-in"
            elif avg_acceleration < -0.2:
                return "ease-out"
            elif velocity_variation > 0.5:
                return "bounce"
            else:
                return "ease-in-out"
                
        except Exception as e:
            logger.error(f"缓动建议失败: {e}")
            return "ease"
    
    def determine_complexity(self, geometric_features: Dict[str, float], 
                           motion_features: Dict[str, float]) -> str:
        """确定复杂度级别"""
        try:
            geometric_complexity = geometric_features.get("complexity", 0.0)
            direction_changes = motion_features.get("direction_changes", 0.0)
            
            total_complexity = (geometric_complexity + direction_changes) / 2
            
            if total_complexity < 0.3:
                return "简单"
            elif total_complexity < 0.7:
                return "中等"
            else:
                return "复杂"
                
        except Exception as e:
            logger.error(f"复杂度确定失败: {e}")
            return "中等"
    
    def estimate_duration(self, path: AnimationPath, features: Dict[str, float]) -> float:
        """估算动画时长"""
        try:
            base_duration = 2.0
            
            # 根据路径长度调整
            if path.total_length > 0:
                length_factor = min(2.0, path.total_length / 500.0)  # 500px为基准
                base_duration *= length_factor
            
            # 根据复杂度调整
            direction_changes = features.get("direction_changes", 0.0)
            complexity_factor = 1.0 + direction_changes
            base_duration *= complexity_factor
            
            return max(0.5, min(10.0, base_duration))
            
        except Exception as e:
            logger.error(f"时长估算失败: {e}")
            return 2.0
    
    def generate_natural_description(self, result: PathAnalysisResult, path: AnimationPath) -> str:
        """生成自然语言描述"""
        try:
            description_parts = []
            
            # 起始描述
            if len(path.points) >= 2:
                start = path.points[0]
                end = path.points[-1]
                
                if start.x < end.x:
                    direction = "从左到右"
                elif start.x > end.x:
                    direction = "从右到左"
                else:
                    direction = "垂直"
                
                description_parts.append(direction)
            
            # 形状描述
            if result.geometric_shape:
                description_parts.append(f"沿{result.geometric_shape}")
            
            # 运动描述
            if result.motion_intent:
                description_parts.append(f"进行{result.motion_intent}")
            
            # 节奏描述
            if result.rhythm_pattern and result.rhythm_pattern != "未知节奏":
                description_parts.append(f"呈现{result.rhythm_pattern}")
            
            # 时长描述
            duration_desc = f"历时约{result.estimated_duration:.1f}秒"
            description_parts.append(duration_desc)
            
            return "，".join(description_parts) if description_parts else "路径运动"
            
        except Exception as e:
            logger.error(f"自然语言描述生成失败: {e}")
            return "路径运动"
    
    def calculate_confidence(self, geometric_features: Dict[str, float], 
                           motion_features: Dict[str, float]) -> float:
        """计算分析置信度"""
        try:
            # 基于特征完整性和一致性计算置信度
            feature_count = len(geometric_features) + len(motion_features)
            max_features = 10  # 预期最大特征数
            
            completeness = min(1.0, feature_count / max_features)
            
            # 基于特征值的一致性
            all_values = list(geometric_features.values()) + list(motion_features.values())
            if all_values:
                consistency = 1.0 - (max(all_values) - min(all_values)) / max(1.0, max(all_values))
            else:
                consistency = 0.0
            
            confidence = (completeness + consistency) / 2
            return max(0.1, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"置信度计算失败: {e}")
            return 0.5
