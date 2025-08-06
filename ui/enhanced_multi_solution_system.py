"""
AI Animation Studio - 增强多方案生成系统
优化多方案生成系统，添加质量评估和用户偏好学习
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTextEdit, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
                             QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
                             QProgressBar, QFrame, QScrollArea, QGroupBox, QFormLayout,
                             QCheckBox, QTabWidget, QSplitter, QMessageBox, QDialog,
                             QApplication, QMenu, QToolButton, QStackedWidget, QSlider,
                             QTableWidget, QTableWidgetItem, QHeaderView)
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
from core.enhanced_solution_manager import EnhancedAnimationSolution, SolutionMetrics, SolutionEvaluator
from core.solution_recommendation_engine import SolutionRecommendationEngine, UserPreference

logger = get_logger("enhanced_multi_solution_system")


class QualityDimension(Enum):
    """质量维度枚举"""
    VISUAL_APPEAL = "visual_appeal"         # 视觉吸引力
    ANIMATION_SMOOTHNESS = "smoothness"     # 动画流畅度
    CODE_QUALITY = "code_quality"           # 代码质量
    PERFORMANCE = "performance"             # 性能表现
    CREATIVITY = "creativity"               # 创意程度
    USABILITY = "usability"                 # 易用性
    COMPATIBILITY = "compatibility"         # 兼容性


class SolutionRanking(Enum):
    """方案排名枚举"""
    RECOMMENDED = "recommended"             # 推荐方案
    POPULAR = "popular"                     # 热门方案
    CREATIVE = "creative"                   # 创意方案
    PERFORMANCE = "performance"             # 性能方案
    SIMPLE = "simple"                       # 简单方案


@dataclass
class QualityAssessment:
    """质量评估结果"""
    overall_score: float = 0.0
    dimension_scores: Dict[QualityDimension, float] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    confidence: float = 0.0
    assessment_time: datetime = field(default_factory=datetime.now)


@dataclass
class UserFeedback:
    """用户反馈数据"""
    solution_id: str
    rating: float  # 1-5星评分
    feedback_text: str = ""
    usage_duration: float = 0.0  # 使用时长（秒）
    applied: bool = False  # 是否应用了方案
    shared: bool = False   # 是否分享了方案
    bookmarked: bool = False  # 是否收藏了方案
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationRequest:
    """生成请求"""
    description: str
    count: int = 3
    tech_stacks: List[TechStack] = field(default_factory=list)
    quality_focus: List[QualityDimension] = field(default_factory=list)
    user_preferences: Optional[UserPreference] = None
    context: Dict[str, Any] = field(default_factory=dict)


class AdvancedQualityEvaluator:
    """高级质量评估器"""
    
    def __init__(self):
        self.evaluation_weights = {
            QualityDimension.VISUAL_APPEAL: 0.25,
            QualityDimension.ANIMATION_SMOOTHNESS: 0.20,
            QualityDimension.CODE_QUALITY: 0.15,
            QualityDimension.PERFORMANCE: 0.15,
            QualityDimension.CREATIVITY: 0.10,
            QualityDimension.USABILITY: 0.10,
            QualityDimension.COMPATIBILITY: 0.05
        }
        
        self.quality_criteria = self.initialize_quality_criteria()
        
        logger.info("高级质量评估器初始化完成")
    
    def initialize_quality_criteria(self) -> Dict[QualityDimension, Dict[str, Any]]:
        """初始化质量标准"""
        return {
            QualityDimension.VISUAL_APPEAL: {
                "color_harmony": {"weight": 0.3, "threshold": 0.7},
                "composition": {"weight": 0.3, "threshold": 0.6},
                "visual_hierarchy": {"weight": 0.2, "threshold": 0.6},
                "aesthetic_consistency": {"weight": 0.2, "threshold": 0.7}
            },
            QualityDimension.ANIMATION_SMOOTHNESS: {
                "frame_rate": {"weight": 0.4, "threshold": 60},
                "easing_quality": {"weight": 0.3, "threshold": 0.8},
                "transition_continuity": {"weight": 0.3, "threshold": 0.7}
            },
            QualityDimension.CODE_QUALITY: {
                "structure": {"weight": 0.3, "threshold": 0.8},
                "readability": {"weight": 0.3, "threshold": 0.7},
                "maintainability": {"weight": 0.2, "threshold": 0.7},
                "best_practices": {"weight": 0.2, "threshold": 0.8}
            },
            QualityDimension.PERFORMANCE: {
                "load_time": {"weight": 0.4, "threshold": 2.0},  # 秒
                "memory_usage": {"weight": 0.3, "threshold": 50},  # MB
                "cpu_usage": {"weight": 0.3, "threshold": 30}  # %
            },
            QualityDimension.CREATIVITY: {
                "originality": {"weight": 0.4, "threshold": 0.7},
                "innovation": {"weight": 0.3, "threshold": 0.6},
                "artistic_value": {"weight": 0.3, "threshold": 0.6}
            },
            QualityDimension.USABILITY: {
                "ease_of_use": {"weight": 0.4, "threshold": 0.8},
                "learning_curve": {"weight": 0.3, "threshold": 0.7},
                "accessibility": {"weight": 0.3, "threshold": 0.7}
            },
            QualityDimension.COMPATIBILITY: {
                "browser_support": {"weight": 0.5, "threshold": 0.9},
                "device_compatibility": {"weight": 0.3, "threshold": 0.8},
                "version_stability": {"weight": 0.2, "threshold": 0.8}
            }
        }
    
    def evaluate_solution(self, solution: EnhancedAnimationSolution) -> QualityAssessment:
        """评估方案质量"""
        try:
            assessment = QualityAssessment()
            
            # 评估各个维度
            for dimension in QualityDimension:
                score = self.evaluate_dimension(solution, dimension)
                assessment.dimension_scores[dimension] = score
            
            # 计算综合分数
            assessment.overall_score = self.calculate_overall_score(assessment.dimension_scores)
            
            # 分析优缺点
            assessment.strengths = self.identify_strengths(assessment.dimension_scores)
            assessment.weaknesses = self.identify_weaknesses(assessment.dimension_scores)
            
            # 生成改进建议
            assessment.improvement_suggestions = self.generate_improvement_suggestions(
                assessment.dimension_scores, assessment.weaknesses
            )
            
            # 计算置信度
            assessment.confidence = self.calculate_confidence(solution, assessment.dimension_scores)
            
            return assessment
            
        except Exception as e:
            logger.error(f"评估方案质量失败: {e}")
            return QualityAssessment()
    
    def evaluate_dimension(self, solution: EnhancedAnimationSolution, dimension: QualityDimension) -> float:
        """评估单个维度"""
        try:
            if dimension == QualityDimension.VISUAL_APPEAL:
                return self.evaluate_visual_appeal(solution)
            elif dimension == QualityDimension.ANIMATION_SMOOTHNESS:
                return self.evaluate_animation_smoothness(solution)
            elif dimension == QualityDimension.CODE_QUALITY:
                return self.evaluate_code_quality(solution)
            elif dimension == QualityDimension.PERFORMANCE:
                return self.evaluate_performance(solution)
            elif dimension == QualityDimension.CREATIVITY:
                return self.evaluate_creativity(solution)
            elif dimension == QualityDimension.USABILITY:
                return self.evaluate_usability(solution)
            elif dimension == QualityDimension.COMPATIBILITY:
                return self.evaluate_compatibility(solution)
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"评估维度 {dimension.value} 失败: {e}")
            return 0.5
    
    def evaluate_visual_appeal(self, solution: EnhancedAnimationSolution) -> float:
        """评估视觉吸引力"""
        try:
            score = 0.0
            criteria = self.quality_criteria[QualityDimension.VISUAL_APPEAL]
            
            # 色彩和谐度
            color_score = self.analyze_color_harmony(solution.css_code)
            score += color_score * criteria["color_harmony"]["weight"]
            
            # 构图质量
            composition_score = self.analyze_composition(solution.html_code, solution.css_code)
            score += composition_score * criteria["composition"]["weight"]
            
            # 视觉层次
            hierarchy_score = self.analyze_visual_hierarchy(solution.css_code)
            score += hierarchy_score * criteria["visual_hierarchy"]["weight"]
            
            # 美学一致性
            consistency_score = self.analyze_aesthetic_consistency(solution.css_code)
            score += consistency_score * criteria["aesthetic_consistency"]["weight"]
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"评估视觉吸引力失败: {e}")
            return 0.5
    
    def evaluate_animation_smoothness(self, solution: EnhancedAnimationSolution) -> float:
        """评估动画流畅度"""
        try:
            score = 0.0
            criteria = self.quality_criteria[QualityDimension.ANIMATION_SMOOTHNESS]
            
            # 帧率分析
            frame_rate_score = self.analyze_frame_rate(solution.css_code, solution.js_code)
            score += frame_rate_score * criteria["frame_rate"]["weight"]
            
            # 缓动质量
            easing_score = self.analyze_easing_quality(solution.css_code, solution.js_code)
            score += easing_score * criteria["easing_quality"]["weight"]
            
            # 过渡连续性
            continuity_score = self.analyze_transition_continuity(solution.css_code)
            score += continuity_score * criteria["transition_continuity"]["weight"]
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"评估动画流畅度失败: {e}")
            return 0.5
    
    def evaluate_code_quality(self, solution: EnhancedAnimationSolution) -> float:
        """评估代码质量"""
        try:
            score = 0.0
            criteria = self.quality_criteria[QualityDimension.CODE_QUALITY]
            
            # 代码结构
            structure_score = self.analyze_code_structure(solution.html_code, solution.css_code, solution.js_code)
            score += structure_score * criteria["structure"]["weight"]
            
            # 可读性
            readability_score = self.analyze_code_readability(solution.css_code, solution.js_code)
            score += readability_score * criteria["readability"]["weight"]
            
            # 可维护性
            maintainability_score = self.analyze_maintainability(solution.css_code, solution.js_code)
            score += maintainability_score * criteria["maintainability"]["weight"]
            
            # 最佳实践
            best_practices_score = self.analyze_best_practices(solution.css_code, solution.js_code)
            score += best_practices_score * criteria["best_practices"]["weight"]
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"评估代码质量失败: {e}")
            return 0.5
    
    def evaluate_performance(self, solution: EnhancedAnimationSolution) -> float:
        """评估性能表现"""
        try:
            score = 0.0
            criteria = self.quality_criteria[QualityDimension.PERFORMANCE]
            
            # 加载时间估算
            load_time_score = self.estimate_load_time(solution.html_code, solution.css_code, solution.js_code)
            score += load_time_score * criteria["load_time"]["weight"]
            
            # 内存使用估算
            memory_score = self.estimate_memory_usage(solution.css_code, solution.js_code)
            score += memory_score * criteria["memory_usage"]["weight"]
            
            # CPU使用估算
            cpu_score = self.estimate_cpu_usage(solution.css_code, solution.js_code)
            score += cpu_score * criteria["cpu_usage"]["weight"]
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"评估性能表现失败: {e}")
            return 0.5
    
    def evaluate_creativity(self, solution: EnhancedAnimationSolution) -> float:
        """评估创意程度"""
        try:
            score = 0.0
            criteria = self.quality_criteria[QualityDimension.CREATIVITY]
            
            # 原创性
            originality_score = self.analyze_originality(solution.css_code, solution.js_code)
            score += originality_score * criteria["originality"]["weight"]
            
            # 创新性
            innovation_score = self.analyze_innovation(solution.css_code, solution.js_code)
            score += innovation_score * criteria["innovation"]["weight"]
            
            # 艺术价值
            artistic_score = self.analyze_artistic_value(solution.css_code)
            score += artistic_score * criteria["artistic_value"]["weight"]
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"评估创意程度失败: {e}")
            return 0.5
    
    def evaluate_usability(self, solution: EnhancedAnimationSolution) -> float:
        """评估易用性"""
        try:
            score = 0.0
            criteria = self.quality_criteria[QualityDimension.USABILITY]
            
            # 易用性
            ease_score = self.analyze_ease_of_use(solution.html_code, solution.css_code)
            score += ease_score * criteria["ease_of_use"]["weight"]
            
            # 学习曲线
            learning_score = self.analyze_learning_curve(solution.css_code, solution.js_code)
            score += learning_score * criteria["learning_curve"]["weight"]
            
            # 可访问性
            accessibility_score = self.analyze_accessibility(solution.html_code, solution.css_code)
            score += accessibility_score * criteria["accessibility"]["weight"]
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"评估易用性失败: {e}")
            return 0.5
    
    def evaluate_compatibility(self, solution: EnhancedAnimationSolution) -> float:
        """评估兼容性"""
        try:
            score = 0.0
            criteria = self.quality_criteria[QualityDimension.COMPATIBILITY]
            
            # 浏览器支持
            browser_score = self.analyze_browser_support(solution.css_code, solution.js_code)
            score += browser_score * criteria["browser_support"]["weight"]
            
            # 设备兼容性
            device_score = self.analyze_device_compatibility(solution.css_code)
            score += device_score * criteria["device_compatibility"]["weight"]
            
            # 版本稳定性
            version_score = self.analyze_version_stability(solution.css_code, solution.js_code)
            score += version_score * criteria["version_stability"]["weight"]
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"评估兼容性失败: {e}")
            return 0.5
    
    # 简化的分析方法（实际实现中会更复杂）
    def analyze_color_harmony(self, css_code: str) -> float:
        """分析色彩和谐度"""
        # 简化实现：检查颜色使用
        color_count = len(re.findall(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|rgb\(|rgba\(|hsl\(', css_code))
        return min(1.0, max(0.3, 1.0 - color_count / 20))  # 颜色数量适中得分更高
    
    def analyze_composition(self, html_code: str, css_code: str) -> float:
        """分析构图质量"""
        # 简化实现：检查布局复杂度
        layout_properties = len(re.findall(r'(position|display|flex|grid|float)', css_code))
        return min(1.0, max(0.4, layout_properties / 10))
    
    def analyze_visual_hierarchy(self, css_code: str) -> float:
        """分析视觉层次"""
        # 简化实现：检查z-index和层次结构
        z_index_count = len(re.findall(r'z-index', css_code))
        return min(1.0, max(0.5, z_index_count / 5))
    
    def analyze_aesthetic_consistency(self, css_code: str) -> float:
        """分析美学一致性"""
        # 简化实现：检查样式一致性
        class_count = len(re.findall(r'\.[a-zA-Z][a-zA-Z0-9_-]*', css_code))
        return min(1.0, max(0.4, class_count / 15))
    
    def analyze_frame_rate(self, css_code: str, js_code: str) -> float:
        """分析帧率"""
        # 简化实现：检查动画属性
        animation_count = len(re.findall(r'animation|transition', css_code))
        return min(1.0, max(0.5, 1.0 - animation_count / 20))  # 动画数量适中
    
    def analyze_easing_quality(self, css_code: str, js_code: str) -> float:
        """分析缓动质量"""
        # 简化实现：检查缓动函数
        easing_functions = len(re.findall(r'ease|cubic-bezier|linear', css_code + js_code))
        return min(1.0, max(0.3, easing_functions / 10))
    
    def analyze_transition_continuity(self, css_code: str) -> float:
        """分析过渡连续性"""
        # 简化实现：检查过渡属性
        transition_count = len(re.findall(r'transition', css_code))
        return min(1.0, max(0.4, transition_count / 8))
    
    def analyze_code_structure(self, html_code: str, css_code: str, js_code: str) -> float:
        """分析代码结构"""
        # 简化实现：检查代码组织
        total_lines = len(html_code.split('\n')) + len(css_code.split('\n')) + len(js_code.split('\n'))
        return min(1.0, max(0.3, 1.0 - total_lines / 200))  # 代码长度适中
    
    def analyze_code_readability(self, css_code: str, js_code: str) -> float:
        """分析代码可读性"""
        # 简化实现：检查注释和格式
        comment_count = len(re.findall(r'/\*.*?\*/|//.*', css_code + js_code, re.DOTALL))
        return min(1.0, max(0.2, comment_count / 5))
    
    def analyze_maintainability(self, css_code: str, js_code: str) -> float:
        """分析可维护性"""
        # 简化实现：检查模块化程度
        function_count = len(re.findall(r'function|const.*=.*=>', js_code))
        return min(1.0, max(0.3, function_count / 8))
    
    def analyze_best_practices(self, css_code: str, js_code: str) -> float:
        """分析最佳实践"""
        # 简化实现：检查现代语法使用
        modern_features = len(re.findall(r'const|let|arrow|async|await', js_code))
        return min(1.0, max(0.4, modern_features / 10))
    
    def estimate_load_time(self, html_code: str, css_code: str, js_code: str) -> float:
        """估算加载时间"""
        # 简化实现：基于代码大小估算
        total_size = len(html_code) + len(css_code) + len(js_code)
        estimated_time = total_size / 10000  # 假设10KB/s
        return max(0.0, 1.0 - estimated_time / 5.0)  # 5秒内加载完成得满分
    
    def estimate_memory_usage(self, css_code: str, js_code: str) -> float:
        """估算内存使用"""
        # 简化实现：基于复杂度估算
        complexity = len(re.findall(r'animation|transform|filter', css_code))
        estimated_memory = complexity * 2  # MB
        return max(0.0, 1.0 - estimated_memory / 100)
    
    def estimate_cpu_usage(self, css_code: str, js_code: str) -> float:
        """估算CPU使用"""
        # 简化实现：基于动画复杂度
        heavy_operations = len(re.findall(r'filter|transform3d|perspective', css_code))
        estimated_cpu = heavy_operations * 5  # %
        return max(0.0, 1.0 - estimated_cpu / 50)
    
    def analyze_originality(self, css_code: str, js_code: str) -> float:
        """分析原创性"""
        # 简化实现：检查独特特征
        unique_features = len(re.findall(r'custom|unique|special', css_code + js_code, re.IGNORECASE))
        return min(1.0, max(0.3, unique_features / 3))
    
    def analyze_innovation(self, css_code: str, js_code: str) -> float:
        """分析创新性"""
        # 简化实现：检查新技术使用
        new_features = len(re.findall(r'grid|flexbox|custom-properties|clip-path', css_code))
        return min(1.0, max(0.2, new_features / 5))
    
    def analyze_artistic_value(self, css_code: str) -> float:
        """分析艺术价值"""
        # 简化实现：检查艺术元素
        artistic_elements = len(re.findall(r'gradient|shadow|border-radius|opacity', css_code))
        return min(1.0, max(0.3, artistic_elements / 8))
    
    def analyze_ease_of_use(self, html_code: str, css_code: str) -> float:
        """分析易用性"""
        # 简化实现：检查简洁性
        complexity = len(html_code.split('\n')) + len(css_code.split('\n'))
        return max(0.2, 1.0 - complexity / 100)
    
    def analyze_learning_curve(self, css_code: str, js_code: str) -> float:
        """分析学习曲线"""
        # 简化实现：检查技术难度
        advanced_features = len(re.findall(r'transform3d|animation-fill-mode|keyframes', css_code))
        return max(0.3, 1.0 - advanced_features / 10)
    
    def analyze_accessibility(self, html_code: str, css_code: str) -> float:
        """分析可访问性"""
        # 简化实现：检查可访问性特征
        a11y_features = len(re.findall(r'aria-|alt=|role=|tabindex', html_code))
        return min(1.0, max(0.2, a11y_features / 3))
    
    def analyze_browser_support(self, css_code: str, js_code: str) -> float:
        """分析浏览器支持"""
        # 简化实现：检查兼容性问题
        compatibility_issues = len(re.findall(r'-webkit-|-moz-|-ms-', css_code))
        return min(1.0, max(0.4, 1.0 - compatibility_issues / 10))
    
    def analyze_device_compatibility(self, css_code: str) -> float:
        """分析设备兼容性"""
        # 简化实现：检查响应式设计
        responsive_features = len(re.findall(r'@media|vw|vh|%', css_code))
        return min(1.0, max(0.3, responsive_features / 8))
    
    def analyze_version_stability(self, css_code: str, js_code: str) -> float:
        """分析版本稳定性"""
        # 简化实现：检查稳定特性使用
        stable_features = len(re.findall(r'display|position|margin|padding', css_code))
        return min(1.0, max(0.5, stable_features / 15))
    
    def calculate_overall_score(self, dimension_scores: Dict[QualityDimension, float]) -> float:
        """计算综合分数"""
        try:
            total_score = 0.0
            total_weight = 0.0
            
            for dimension, score in dimension_scores.items():
                weight = self.evaluation_weights.get(dimension, 0.1)
                total_score += score * weight
                total_weight += weight
            
            return total_score / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            logger.error(f"计算综合分数失败: {e}")
            return 0.0
    
    def identify_strengths(self, dimension_scores: Dict[QualityDimension, float]) -> List[str]:
        """识别优势"""
        strengths = []
        
        try:
            for dimension, score in dimension_scores.items():
                if score >= 0.8:
                    strengths.append(f"{dimension.value}: 表现优秀 ({score:.2f})")
                elif score >= 0.7:
                    strengths.append(f"{dimension.value}: 表现良好 ({score:.2f})")
            
            return strengths
            
        except Exception as e:
            logger.error(f"识别优势失败: {e}")
            return []
    
    def identify_weaknesses(self, dimension_scores: Dict[QualityDimension, float]) -> List[str]:
        """识别弱点"""
        weaknesses = []
        
        try:
            for dimension, score in dimension_scores.items():
                if score < 0.4:
                    weaknesses.append(f"{dimension.value}: 需要改进 ({score:.2f})")
                elif score < 0.6:
                    weaknesses.append(f"{dimension.value}: 有待提升 ({score:.2f})")
            
            return weaknesses
            
        except Exception as e:
            logger.error(f"识别弱点失败: {e}")
            return []
    
    def generate_improvement_suggestions(self, dimension_scores: Dict[QualityDimension, float], 
                                       weaknesses: List[str]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        try:
            for dimension, score in dimension_scores.items():
                if score < 0.6:
                    if dimension == QualityDimension.VISUAL_APPEAL:
                        suggestions.append("建议优化色彩搭配和视觉层次")
                    elif dimension == QualityDimension.ANIMATION_SMOOTHNESS:
                        suggestions.append("建议使用更平滑的缓动函数")
                    elif dimension == QualityDimension.CODE_QUALITY:
                        suggestions.append("建议重构代码结构，提高可读性")
                    elif dimension == QualityDimension.PERFORMANCE:
                        suggestions.append("建议优化动画性能，减少资源消耗")
                    elif dimension == QualityDimension.CREATIVITY:
                        suggestions.append("建议增加创意元素和独特设计")
                    elif dimension == QualityDimension.USABILITY:
                        suggestions.append("建议简化使用方式，提高易用性")
                    elif dimension == QualityDimension.COMPATIBILITY:
                        suggestions.append("建议增强浏览器和设备兼容性")
            
            return suggestions[:5]  # 最多返回5个建议
            
        except Exception as e:
            logger.error(f"生成改进建议失败: {e}")
            return []
    
    def calculate_confidence(self, solution: EnhancedAnimationSolution, 
                           dimension_scores: Dict[QualityDimension, float]) -> float:
        """计算评估置信度"""
        try:
            # 基于代码完整性和分数一致性计算置信度
            code_completeness = 0.0
            if solution.html_code:
                code_completeness += 0.3
            if solution.css_code:
                code_completeness += 0.4
            if solution.js_code:
                code_completeness += 0.3
            
            # 分数一致性（方差越小，置信度越高）
            scores = list(dimension_scores.values())
            if scores:
                score_variance = np.var(scores)
                consistency = max(0.0, 1.0 - score_variance)
            else:
                consistency = 0.0
            
            confidence = (code_completeness + consistency) / 2
            return min(1.0, max(0.1, confidence))
            
        except Exception as e:
            logger.error(f"计算置信度失败: {e}")
            return 0.5


class UserPreferenceLearningEngine:
    """用户偏好学习引擎"""

    def __init__(self):
        self.feedback_history: List[UserFeedback] = []
        self.preference_weights = {
            "rating": 0.4,          # 用户评分权重
            "usage_duration": 0.2,  # 使用时长权重
            "applied": 0.2,         # 应用行为权重
            "shared": 0.1,          # 分享行为权重
            "bookmarked": 0.1       # 收藏行为权重
        }

        self.learned_preferences = {
            "quality_dimensions": defaultdict(float),
            "tech_stacks": defaultdict(float),
            "solution_types": defaultdict(float),
            "complexity_levels": defaultdict(float)
        }

        logger.info("用户偏好学习引擎初始化完成")

    def record_feedback(self, feedback: UserFeedback):
        """记录用户反馈"""
        try:
            self.feedback_history.append(feedback)

            # 实时更新偏好
            self.update_preferences(feedback)

            logger.debug(f"记录用户反馈: {feedback.solution_id}, 评分: {feedback.rating}")

        except Exception as e:
            logger.error(f"记录用户反馈失败: {e}")

    def update_preferences(self, feedback: UserFeedback):
        """更新用户偏好"""
        try:
            # 计算反馈权重
            feedback_weight = self.calculate_feedback_weight(feedback)

            # 更新质量维度偏好
            if "quality_assessment" in feedback.context:
                assessment = feedback.context["quality_assessment"]
                for dimension, score in assessment.dimension_scores.items():
                    if feedback.rating >= 4.0:  # 高评分表示喜欢
                        self.learned_preferences["quality_dimensions"][dimension.value] += feedback_weight * 0.1
                    elif feedback.rating <= 2.0:  # 低评分表示不喜欢
                        self.learned_preferences["quality_dimensions"][dimension.value] -= feedback_weight * 0.05

            # 更新技术栈偏好
            if "tech_stack" in feedback.context:
                tech_stack = feedback.context["tech_stack"]
                if feedback.rating >= 4.0:
                    self.learned_preferences["tech_stacks"][tech_stack] += feedback_weight * 0.2
                elif feedback.rating <= 2.0:
                    self.learned_preferences["tech_stacks"][tech_stack] -= feedback_weight * 0.1

            # 更新方案类型偏好
            if "solution_type" in feedback.context:
                solution_type = feedback.context["solution_type"]
                if feedback.rating >= 4.0:
                    self.learned_preferences["solution_types"][solution_type] += feedback_weight * 0.15
                elif feedback.rating <= 2.0:
                    self.learned_preferences["solution_types"][solution_type] -= feedback_weight * 0.08

            # 更新复杂度偏好
            if "complexity_level" in feedback.context:
                complexity = feedback.context["complexity_level"]
                if feedback.rating >= 4.0:
                    self.learned_preferences["complexity_levels"][complexity] += feedback_weight * 0.1
                elif feedback.rating <= 2.0:
                    self.learned_preferences["complexity_levels"][complexity] -= feedback_weight * 0.05

        except Exception as e:
            logger.error(f"更新用户偏好失败: {e}")

    def calculate_feedback_weight(self, feedback: UserFeedback) -> float:
        """计算反馈权重"""
        try:
            weight = 0.0

            # 评分权重
            rating_weight = (feedback.rating - 3.0) / 2.0  # 转换为-1到1的范围
            weight += abs(rating_weight) * self.preference_weights["rating"]

            # 使用时长权重
            duration_weight = min(1.0, feedback.usage_duration / 300)  # 5分钟为满分
            weight += duration_weight * self.preference_weights["usage_duration"]

            # 应用行为权重
            if feedback.applied:
                weight += self.preference_weights["applied"]

            # 分享行为权重
            if feedback.shared:
                weight += self.preference_weights["shared"]

            # 收藏行为权重
            if feedback.bookmarked:
                weight += self.preference_weights["bookmarked"]

            return min(1.0, weight)

        except Exception as e:
            logger.error(f"计算反馈权重失败: {e}")
            return 0.1

    def get_user_preferences(self) -> Dict[str, Any]:
        """获取用户偏好"""
        try:
            # 归一化偏好值
            normalized_preferences = {}

            for category, preferences in self.learned_preferences.items():
                if preferences:
                    # 计算总权重
                    total_weight = sum(abs(weight) for weight in preferences.values())

                    if total_weight > 0:
                        # 归一化
                        normalized = {
                            key: weight / total_weight
                            for key, weight in preferences.items()
                        }
                        normalized_preferences[category] = normalized
                    else:
                        normalized_preferences[category] = {}
                else:
                    normalized_preferences[category] = {}

            return normalized_preferences

        except Exception as e:
            logger.error(f"获取用户偏好失败: {e}")
            return {}

    def predict_user_rating(self, solution: EnhancedAnimationSolution,
                           assessment: QualityAssessment) -> float:
        """预测用户评分"""
        try:
            predicted_rating = 3.0  # 基础评分

            preferences = self.get_user_preferences()

            # 基于质量维度偏好预测
            if "quality_dimensions" in preferences:
                for dimension, score in assessment.dimension_scores.items():
                    dimension_preference = preferences["quality_dimensions"].get(dimension.value, 0.0)
                    predicted_rating += dimension_preference * score * 2.0  # 最大影响2分

            # 基于技术栈偏好预测
            if "tech_stacks" in preferences and hasattr(solution, 'tech_stack'):
                tech_preference = preferences["tech_stacks"].get(solution.tech_stack.value, 0.0)
                predicted_rating += tech_preference * 1.0  # 最大影响1分

            # 限制在1-5范围内
            return max(1.0, min(5.0, predicted_rating))

        except Exception as e:
            logger.error(f"预测用户评分失败: {e}")
            return 3.0

    def get_learning_insights(self) -> Dict[str, Any]:
        """获取学习洞察"""
        try:
            insights = {
                "total_feedback": len(self.feedback_history),
                "average_rating": 0.0,
                "most_preferred": {},
                "least_preferred": {},
                "learning_confidence": 0.0
            }

            if self.feedback_history:
                # 平均评分
                insights["average_rating"] = sum(f.rating for f in self.feedback_history) / len(self.feedback_history)

                # 最偏好的特征
                preferences = self.get_user_preferences()
                for category, prefs in preferences.items():
                    if prefs:
                        most_preferred = max(prefs.items(), key=lambda x: x[1])
                        least_preferred = min(prefs.items(), key=lambda x: x[1])

                        insights["most_preferred"][category] = most_preferred
                        insights["least_preferred"][category] = least_preferred

                # 学习置信度（基于反馈数量）
                insights["learning_confidence"] = min(1.0, len(self.feedback_history) / 50)

            return insights

        except Exception as e:
            logger.error(f"获取学习洞察失败: {e}")
            return {}


class EnhancedMultiSolutionGenerator:
    """增强多方案生成器"""

    def __init__(self):
        self.quality_evaluator = AdvancedQualityEvaluator()
        self.preference_engine = UserPreferenceLearningEngine()

        self.generation_strategies = {
            "diverse": self.generate_diverse_solutions,
            "quality_focused": self.generate_quality_focused_solutions,
            "user_preferred": self.generate_user_preferred_solutions,
            "creative": self.generate_creative_solutions,
            "performance": self.generate_performance_solutions
        }

        logger.info("增强多方案生成器初始化完成")

    def generate_solutions(self, request: GenerationRequest) -> List[EnhancedAnimationSolution]:
        """生成多个方案"""
        try:
            solutions = []

            # 选择生成策略
            strategy = self.select_generation_strategy(request)

            # 生成方案
            generated_solutions = strategy(request)

            # 评估质量
            for solution in generated_solutions:
                assessment = self.quality_evaluator.evaluate_solution(solution)
                solution.quality_assessment = assessment

                # 预测用户评分
                predicted_rating = self.preference_engine.predict_user_rating(solution, assessment)
                solution.predicted_rating = predicted_rating

                solutions.append(solution)

            # 排序和排名
            ranked_solutions = self.rank_solutions(solutions, request)

            logger.info(f"生成了 {len(ranked_solutions)} 个方案")
            return ranked_solutions

        except Exception as e:
            logger.error(f"生成方案失败: {e}")
            return []

    def select_generation_strategy(self, request: GenerationRequest) -> Callable:
        """选择生成策略"""
        try:
            # 基于用户偏好和请求选择策略
            if request.user_preferences and len(self.preference_engine.feedback_history) > 10:
                return self.generation_strategies["user_preferred"]
            elif request.quality_focus:
                if QualityDimension.CREATIVITY in request.quality_focus:
                    return self.generation_strategies["creative"]
                elif QualityDimension.PERFORMANCE in request.quality_focus:
                    return self.generation_strategies["performance"]
                else:
                    return self.generation_strategies["quality_focused"]
            else:
                return self.generation_strategies["diverse"]

        except Exception as e:
            logger.error(f"选择生成策略失败: {e}")
            return self.generation_strategies["diverse"]

    def generate_diverse_solutions(self, request: GenerationRequest) -> List[EnhancedAnimationSolution]:
        """生成多样化方案"""
        solutions = []

        try:
            # 使用不同技术栈生成方案
            tech_stacks = request.tech_stacks or [TechStack.CSS_ANIMATION, TechStack.GSAP, TechStack.THREE_JS]

            for i, tech_stack in enumerate(tech_stacks[:request.count]):
                solution = self.create_solution_with_tech_stack(request.description, tech_stack, i)
                if solution:
                    solutions.append(solution)

            # 如果需要更多方案，使用变化策略
            while len(solutions) < request.count:
                variation_solution = self.create_variation_solution(request.description, len(solutions))
                if variation_solution:
                    solutions.append(variation_solution)
                else:
                    break

            return solutions

        except Exception as e:
            logger.error(f"生成多样化方案失败: {e}")
            return solutions

    def generate_quality_focused_solutions(self, request: GenerationRequest) -> List[EnhancedAnimationSolution]:
        """生成质量导向方案"""
        solutions = []

        try:
            # 生成更多候选方案，然后选择质量最高的
            candidate_count = request.count * 2
            candidates = self.generate_diverse_solutions(
                GenerationRequest(
                    description=request.description,
                    count=candidate_count,
                    tech_stacks=request.tech_stacks,
                    context=request.context
                )
            )

            # 评估并选择最佳方案
            evaluated_candidates = []
            for candidate in candidates:
                assessment = self.quality_evaluator.evaluate_solution(candidate)
                candidate.quality_assessment = assessment
                evaluated_candidates.append(candidate)

            # 按质量排序
            evaluated_candidates.sort(key=lambda s: s.quality_assessment.overall_score, reverse=True)

            return evaluated_candidates[:request.count]

        except Exception as e:
            logger.error(f"生成质量导向方案失败: {e}")
            return solutions

    def generate_user_preferred_solutions(self, request: GenerationRequest) -> List[EnhancedAnimationSolution]:
        """生成用户偏好方案"""
        solutions = []

        try:
            user_preferences = self.preference_engine.get_user_preferences()

            # 基于用户偏好调整生成参数
            preferred_tech_stacks = []
            if "tech_stacks" in user_preferences:
                # 选择用户偏好的技术栈
                tech_prefs = user_preferences["tech_stacks"]
                sorted_techs = sorted(tech_prefs.items(), key=lambda x: x[1], reverse=True)
                preferred_tech_stacks = [TechStack(tech) for tech, _ in sorted_techs[:request.count]]

            if not preferred_tech_stacks:
                preferred_tech_stacks = request.tech_stacks or [TechStack.CSS_ANIMATION, TechStack.GSAP]

            # 生成基于偏好的方案
            for i, tech_stack in enumerate(preferred_tech_stacks[:request.count]):
                solution = self.create_preference_based_solution(
                    request.description, tech_stack, user_preferences, i
                )
                if solution:
                    solutions.append(solution)

            return solutions

        except Exception as e:
            logger.error(f"生成用户偏好方案失败: {e}")
            return solutions

    def generate_creative_solutions(self, request: GenerationRequest) -> List[EnhancedAnimationSolution]:
        """生成创意方案"""
        solutions = []

        try:
            # 使用创意增强的描述生成方案
            creative_variations = [
                f"{request.description} with artistic flair",
                f"{request.description} with innovative effects",
                f"{request.description} with unique visual style"
            ]

            for i, creative_desc in enumerate(creative_variations[:request.count]):
                solution = self.create_creative_solution(creative_desc, i)
                if solution:
                    solutions.append(solution)

            return solutions

        except Exception as e:
            logger.error(f"生成创意方案失败: {e}")
            return solutions

    def generate_performance_solutions(self, request: GenerationRequest) -> List[EnhancedAnimationSolution]:
        """生成性能优化方案"""
        solutions = []

        try:
            # 使用性能优化的技术栈
            performance_tech_stacks = [TechStack.CSS_ANIMATION, TechStack.GSAP]

            for i, tech_stack in enumerate(performance_tech_stacks[:request.count]):
                solution = self.create_performance_optimized_solution(
                    request.description, tech_stack, i
                )
                if solution:
                    solutions.append(solution)

            return solutions

        except Exception as e:
            logger.error(f"生成性能优化方案失败: {e}")
            return solutions

    def create_solution_with_tech_stack(self, description: str, tech_stack: TechStack,
                                      variation_index: int) -> Optional[EnhancedAnimationSolution]:
        """使用指定技术栈创建方案"""
        try:
            # 这里是简化的实现，实际中会调用AI服务
            solution = EnhancedAnimationSolution(
                solution_id=f"solution_{tech_stack.value}_{variation_index}_{int(time.time())}",
                name=f"{tech_stack.value.title()} Animation Solution {variation_index + 1}",
                description=f"Animation solution using {tech_stack.value} for: {description}",
                tech_stack=tech_stack,
                html_code=self.generate_sample_html(description, tech_stack),
                css_code=self.generate_sample_css(description, tech_stack),
                js_code=self.generate_sample_js(description, tech_stack) if tech_stack != TechStack.CSS_ANIMATION else ""
            )

            return solution

        except Exception as e:
            logger.error(f"创建方案失败: {e}")
            return None

    def create_variation_solution(self, description: str, variation_index: int) -> Optional[EnhancedAnimationSolution]:
        """创建变化方案"""
        try:
            # 添加变化元素
            variations = [
                "with smooth transitions",
                "with bounce effects",
                "with fade animations",
                "with scale transformations",
                "with rotation effects"
            ]

            variation_desc = f"{description} {variations[variation_index % len(variations)]}"
            tech_stack = [TechStack.CSS_ANIMATION, TechStack.GSAP, TechStack.JAVASCRIPT][variation_index % 3]

            return self.create_solution_with_tech_stack(variation_desc, tech_stack, variation_index)

        except Exception as e:
            logger.error(f"创建变化方案失败: {e}")
            return None

    def create_preference_based_solution(self, description: str, tech_stack: TechStack,
                                       user_preferences: Dict[str, Any], variation_index: int) -> Optional[EnhancedAnimationSolution]:
        """创建基于偏好的方案"""
        try:
            # 根据用户偏好调整方案特征
            adjusted_description = description

            # 基于质量维度偏好调整
            if "quality_dimensions" in user_preferences:
                quality_prefs = user_preferences["quality_dimensions"]

                if quality_prefs.get("creativity", 0) > 0.5:
                    adjusted_description += " with creative elements"
                if quality_prefs.get("performance", 0) > 0.5:
                    adjusted_description += " optimized for performance"
                if quality_prefs.get("visual_appeal", 0) > 0.5:
                    adjusted_description += " with enhanced visual appeal"

            return self.create_solution_with_tech_stack(adjusted_description, tech_stack, variation_index)

        except Exception as e:
            logger.error(f"创建基于偏好的方案失败: {e}")
            return None

    def create_creative_solution(self, description: str, variation_index: int) -> Optional[EnhancedAnimationSolution]:
        """创建创意方案"""
        try:
            # 使用创意技术栈
            creative_tech_stacks = [TechStack.THREE_JS, TechStack.GSAP, TechStack.SVG_ANIMATION]
            tech_stack = creative_tech_stacks[variation_index % len(creative_tech_stacks)]

            return self.create_solution_with_tech_stack(description, tech_stack, variation_index)

        except Exception as e:
            logger.error(f"创建创意方案失败: {e}")
            return None

    def create_performance_optimized_solution(self, description: str, tech_stack: TechStack,
                                            variation_index: int) -> Optional[EnhancedAnimationSolution]:
        """创建性能优化方案"""
        try:
            # 添加性能优化描述
            optimized_description = f"{description} with performance optimization"

            return self.create_solution_with_tech_stack(optimized_description, tech_stack, variation_index)

        except Exception as e:
            logger.error(f"创建性能优化方案失败: {e}")
            return None

    def rank_solutions(self, solutions: List[EnhancedAnimationSolution],
                      request: GenerationRequest) -> List[EnhancedAnimationSolution]:
        """对方案进行排名"""
        try:
            # 计算综合排名分数
            for solution in solutions:
                ranking_score = self.calculate_ranking_score(solution, request)
                solution.ranking_score = ranking_score

            # 按排名分数排序
            solutions.sort(key=lambda s: s.ranking_score, reverse=True)

            # 分配排名标签
            for i, solution in enumerate(solutions):
                if i == 0:
                    solution.ranking = SolutionRanking.RECOMMENDED
                elif hasattr(solution, 'quality_assessment') and solution.quality_assessment.dimension_scores.get(QualityDimension.CREATIVITY, 0) > 0.8:
                    solution.ranking = SolutionRanking.CREATIVE
                elif hasattr(solution, 'quality_assessment') and solution.quality_assessment.dimension_scores.get(QualityDimension.PERFORMANCE, 0) > 0.8:
                    solution.ranking = SolutionRanking.PERFORMANCE
                elif solution.tech_stack == TechStack.CSS_ANIMATION:
                    solution.ranking = SolutionRanking.SIMPLE
                else:
                    solution.ranking = SolutionRanking.POPULAR

            return solutions

        except Exception as e:
            logger.error(f"方案排名失败: {e}")
            return solutions

    def calculate_ranking_score(self, solution: EnhancedAnimationSolution,
                              request: GenerationRequest) -> float:
        """计算排名分数"""
        try:
            score = 0.0

            # 质量分数权重 40%
            if hasattr(solution, 'quality_assessment'):
                score += solution.quality_assessment.overall_score * 0.4

            # 预测用户评分权重 30%
            if hasattr(solution, 'predicted_rating'):
                score += (solution.predicted_rating / 5.0) * 0.3

            # 技术栈匹配权重 20%
            if request.tech_stacks and solution.tech_stack in request.tech_stacks:
                score += 0.2

            # 质量焦点匹配权重 10%
            if request.quality_focus and hasattr(solution, 'quality_assessment'):
                focus_score = 0.0
                for focus_dimension in request.quality_focus:
                    dimension_score = solution.quality_assessment.dimension_scores.get(focus_dimension, 0.0)
                    focus_score += dimension_score

                if request.quality_focus:
                    focus_score /= len(request.quality_focus)
                    score += focus_score * 0.1

            return min(1.0, max(0.0, score))

        except Exception as e:
            logger.error(f"计算排名分数失败: {e}")
            return 0.5

    # 简化的代码生成方法（实际实现中会更复杂）
    def generate_sample_html(self, description: str, tech_stack: TechStack) -> str:
        """生成示例HTML代码"""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Animation: {description}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="animation-container">
        <div class="animated-element" id="element">
            Animation Element
        </div>
    </div>
    {f'<script src="script.js"></script>' if tech_stack != TechStack.CSS_ANIMATION else ''}
</body>
</html>"""

    def generate_sample_css(self, description: str, tech_stack: TechStack) -> str:
        """生成示例CSS代码"""
        if tech_stack == TechStack.CSS_ANIMATION:
            return f"""/* CSS Animation for: {description} */
.animation-container {{
    width: 100%;
    height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}}

.animated-element {{
    width: 100px;
    height: 100px;
    background: #ff6b6b;
    border-radius: 50%;
    animation: customAnimation 2s ease-in-out infinite;
}}

@keyframes customAnimation {{
    0% {{ transform: translateX(-50px) scale(1); }}
    50% {{ transform: translateX(50px) scale(1.2); }}
    100% {{ transform: translateX(-50px) scale(1); }}
}}"""
        else:
            return f"""/* Styles for: {description} */
.animation-container {{
    width: 100%;
    height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}}

.animated-element {{
    width: 100px;
    height: 100px;
    background: #ff6b6b;
    border-radius: 50%;
}}"""

    def generate_sample_js(self, description: str, tech_stack: TechStack) -> str:
        """生成示例JavaScript代码"""
        if tech_stack == TechStack.GSAP:
            return f"""// GSAP Animation for: {description}
gsap.registerPlugin(ScrollTrigger);

const element = document.getElementById('element');

gsap.timeline({{repeat: -1, yoyo: true}})
    .to(element, {{
        x: 100,
        scale: 1.2,
        rotation: 360,
        duration: 1,
        ease: "power2.inOut"
    }})
    .to(element, {{
        x: -100,
        scale: 0.8,
        rotation: -360,
        duration: 1,
        ease: "bounce.out"
    }});"""
        elif tech_stack == TechStack.THREE_JS:
            return f"""// Three.js Animation for: {description}
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();

renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshBasicMaterial({{ color: 0xff6b6b }});
const cube = new THREE.Mesh(geometry, material);

scene.add(cube);
camera.position.z = 5;

function animate() {{
    requestAnimationFrame(animate);

    cube.rotation.x += 0.01;
    cube.rotation.y += 0.01;

    renderer.render(scene, camera);
}}

animate();"""
        else:
            return f"""// JavaScript Animation for: {description}
const element = document.getElementById('element');

function animateElement() {{
    element.style.transition = 'transform 1s ease-in-out';
    element.style.transform = 'translateX(100px) scale(1.2)';

    setTimeout(() => {{
        element.style.transform = 'translateX(-100px) scale(0.8)';
    }}, 1000);

    setTimeout(() => {{
        element.style.transform = 'translateX(0) scale(1)';
    }}, 2000);
}}

setInterval(animateElement, 3000);
animateElement();"""

    def record_user_feedback(self, feedback: UserFeedback):
        """记录用户反馈"""
        self.preference_engine.record_feedback(feedback)

    def get_learning_insights(self) -> Dict[str, Any]:
        """获取学习洞察"""
        return self.preference_engine.get_learning_insights()


class EnhancedMultiSolutionWidget(QWidget):
    """增强多方案生成系统主组件"""

    # 信号定义
    solution_generated = pyqtSignal(list)               # 方案生成信号
    solution_selected = pyqtSignal(str)                 # 方案选择信号
    feedback_recorded = pyqtSignal(dict)                # 反馈记录信号
    quality_assessed = pyqtSignal(str, dict)            # 质量评估信号

    def __init__(self, parent=None):
        super().__init__(parent)

        # 核心组件
        self.solution_generator = EnhancedMultiSolutionGenerator()
        self.current_solutions: List[EnhancedAnimationSolution] = []
        self.selected_solution: Optional[EnhancedAnimationSolution] = None

        self.setup_ui()
        self.setup_connections()

        logger.info("增强多方案生成系统主组件初始化完成")

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 创建标题
        title_label = QLabel("🎯 增强多方案生成系统")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c5aa0; margin: 10px;")
        layout.addWidget(title_label)

        # 创建主要内容区域
        self.create_generation_section(layout)
        self.create_solutions_display_section(layout)
        self.create_quality_assessment_section(layout)
        self.create_user_feedback_section(layout)
        self.create_learning_insights_section(layout)

    def create_generation_section(self, layout):
        """创建生成区域"""
        generation_group = QGroupBox("🚀 方案生成配置")
        generation_layout = QVBoxLayout(generation_group)

        # 描述输入
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("动画描述:"))
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("请输入动画描述，例如：小球从左到右移动")
        desc_layout.addWidget(self.description_edit)
        generation_layout.addLayout(desc_layout)

        # 生成配置
        config_layout = QFormLayout()

        # 方案数量
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 10)
        self.count_spin.setValue(3)
        config_layout.addRow("方案数量:", self.count_spin)

        # 生成策略
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["diverse", "quality_focused", "user_preferred", "creative", "performance"])
        self.strategy_combo.setCurrentText("diverse")
        config_layout.addRow("生成策略:", self.strategy_combo)

        # 技术栈选择
        tech_layout = QHBoxLayout()
        self.css_check = QCheckBox("CSS Animation")
        self.css_check.setChecked(True)
        self.gsap_check = QCheckBox("GSAP")
        self.gsap_check.setChecked(True)
        self.threejs_check = QCheckBox("Three.js")
        self.js_check = QCheckBox("JavaScript")

        tech_layout.addWidget(self.css_check)
        tech_layout.addWidget(self.gsap_check)
        tech_layout.addWidget(self.threejs_check)
        tech_layout.addWidget(self.js_check)
        tech_layout.addStretch()

        config_layout.addRow("技术栈:", tech_layout)

        # 质量焦点
        quality_layout = QHBoxLayout()
        self.visual_check = QCheckBox("视觉吸引力")
        self.performance_check = QCheckBox("性能表现")
        self.creativity_check = QCheckBox("创意程度")
        self.usability_check = QCheckBox("易用性")

        quality_layout.addWidget(self.visual_check)
        quality_layout.addWidget(self.performance_check)
        quality_layout.addWidget(self.creativity_check)
        quality_layout.addWidget(self.usability_check)
        quality_layout.addStretch()

        config_layout.addRow("质量焦点:", quality_layout)

        generation_layout.addLayout(config_layout)

        # 生成按钮
        generate_btn = QPushButton("🎯 生成多方案")
        generate_btn.clicked.connect(self.generate_solutions)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        generation_layout.addWidget(generate_btn)

        layout.addWidget(generation_group)
