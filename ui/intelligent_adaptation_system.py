"""
AI Animation Studio - 智能适应功能系统
实现基于用户行为的智能学习和界面适应
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QDialog, QTabWidget, QGroupBox, QFormLayout, QCheckBox,
                             QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QTextEdit,
                             QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
                             QProgressBar, QFrame, QScrollArea, QSlider, QMessageBox,
                             QApplication, QMenu, QToolButton, QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QThread, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QBrush, QPen

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, Set
import json
import time
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

from core.logger import get_logger

logger = get_logger("intelligent_adaptation_system")


class UserLevel(Enum):
    """用户水平枚举"""
    BEGINNER = "beginner"           # 新手
    INTERMEDIATE = "intermediate"   # 中级
    ADVANCED = "advanced"           # 高级
    EXPERT = "expert"               # 专家


class ActionType(Enum):
    """动作类型枚举"""
    CLICK = "click"                 # 点击
    HOVER = "hover"                 # 悬停
    KEYBOARD = "keyboard"           # 键盘操作
    DRAG = "drag"                   # 拖拽
    SCROLL = "scroll"               # 滚动
    MENU_ACCESS = "menu_access"     # 菜单访问
    FUNCTION_USE = "function_use"   # 功能使用
    ERROR_ENCOUNTER = "error_encounter"  # 遇到错误
    HELP_REQUEST = "help_request"   # 请求帮助


class AdaptationType(Enum):
    """适应类型枚举"""
    TOOLBAR_CUSTOMIZATION = "toolbar_customization"     # 工具栏定制
    MENU_OPTIMIZATION = "menu_optimization"             # 菜单优化
    SHORTCUT_SUGGESTION = "shortcut_suggestion"         # 快捷键建议
    WORKFLOW_OPTIMIZATION = "workflow_optimization"     # 工作流程优化
    UI_SIMPLIFICATION = "ui_simplification"             # 界面简化
    FEATURE_PROMOTION = "feature_promotion"             # 功能推广
    TUTORIAL_SUGGESTION = "tutorial_suggestion"         # 教程建议
    THEME_ADAPTATION = "theme_adaptation"               # 主题适应


@dataclass
class UserAction:
    """用户动作数据"""
    action_id: str
    action_type: ActionType
    component: str
    function_name: str
    timestamp: datetime
    duration: float = 0.0  # 动作持续时间（秒）
    success: bool = True   # 动作是否成功
    context: Dict[str, Any] = field(default_factory=dict)
    user_level: UserLevel = UserLevel.BEGINNER
    session_id: str = ""


@dataclass
class UsagePattern:
    """使用模式"""
    pattern_id: str
    pattern_type: str
    frequency: int
    confidence: float
    components: List[str]
    time_patterns: Dict[str, int] = field(default_factory=dict)  # 时间模式
    sequence_patterns: List[List[str]] = field(default_factory=list)  # 序列模式
    context_patterns: Dict[str, Any] = field(default_factory=dict)  # 上下文模式


@dataclass
class AdaptationSuggestion:
    """适应建议"""
    suggestion_id: str
    adaptation_type: AdaptationType
    title: str
    description: str
    confidence: float
    impact_score: float
    implementation_difficulty: float
    target_components: List[str]
    suggested_changes: Dict[str, Any]
    reasoning: str
    auto_applicable: bool = False


class UsageBehaviorTracker:
    """使用行为跟踪器"""
    
    def __init__(self):
        self.actions: deque = deque(maxlen=10000)  # 最多保存10000个动作
        self.session_actions: List[UserAction] = []
        self.current_session_id = self.generate_session_id()
        self.component_usage: Dict[str, int] = defaultdict(int)
        self.function_usage: Dict[str, int] = defaultdict(int)
        self.error_patterns: Dict[str, int] = defaultdict(int)
        self.time_patterns: Dict[int, int] = defaultdict(int)  # 按小时统计
        self.sequence_buffer: deque = deque(maxlen=50)  # 序列缓冲区
        
        logger.info("使用行为跟踪器初始化完成")
    
    def track_action(self, action_type: ActionType, component: str, 
                    function_name: str, duration: float = 0.0, 
                    success: bool = True, context: Dict[str, Any] = None):
        """跟踪用户动作"""
        try:
            action = UserAction(
                action_id=f"{action_type.value}_{component}_{int(time.time())}",
                action_type=action_type,
                component=component,
                function_name=function_name,
                timestamp=datetime.now(),
                duration=duration,
                success=success,
                context=context or {},
                user_level=self.estimate_user_level(),
                session_id=self.current_session_id
            )
            
            # 添加到记录
            self.actions.append(action)
            self.session_actions.append(action)
            
            # 更新统计
            self.component_usage[component] += 1
            self.function_usage[function_name] += 1
            self.time_patterns[action.timestamp.hour] += 1
            
            # 更新序列缓冲区
            self.sequence_buffer.append(f"{component}:{function_name}")
            
            # 记录错误
            if not success:
                error_key = f"{component}:{function_name}"
                self.error_patterns[error_key] += 1
            
            logger.debug(f"跟踪用户动作: {action.action_id}")
            
        except Exception as e:
            logger.error(f"跟踪用户动作失败: {e}")
    
    def generate_session_id(self) -> str:
        """生成会话ID"""
        return f"session_{int(time.time())}_{hash(str(datetime.now()))}"
    
    def estimate_user_level(self) -> UserLevel:
        """估算用户水平"""
        try:
            if len(self.actions) < 50:
                return UserLevel.BEGINNER
            
            # 计算指标
            total_actions = len(self.actions)
            unique_functions = len(set(action.function_name for action in self.actions))
            error_rate = sum(1 for action in self.actions if not action.success) / total_actions
            avg_duration = statistics.mean(action.duration for action in self.actions if action.duration > 0)
            
            # 高级功能使用率
            advanced_functions = ["batch_operation", "custom_animation", "advanced_settings", "scripting"]
            advanced_usage = sum(1 for action in self.actions 
                               if any(func in action.function_name for func in advanced_functions))
            advanced_rate = advanced_usage / total_actions
            
            # 评估水平
            if unique_functions > 50 and error_rate < 0.1 and advanced_rate > 0.3:
                return UserLevel.EXPERT
            elif unique_functions > 30 and error_rate < 0.2 and advanced_rate > 0.2:
                return UserLevel.ADVANCED
            elif unique_functions > 15 and error_rate < 0.3:
                return UserLevel.INTERMEDIATE
            else:
                return UserLevel.BEGINNER
                
        except Exception as e:
            logger.error(f"估算用户水平失败: {e}")
            return UserLevel.BEGINNER
    
    def get_frequent_functions(self, limit: int = 10) -> List[Tuple[str, int]]:
        """获取常用功能"""
        return sorted(self.function_usage.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_frequent_components(self, limit: int = 10) -> List[Tuple[str, int]]:
        """获取常用组件"""
        return sorted(self.component_usage.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_error_prone_functions(self, limit: int = 10) -> List[Tuple[str, int]]:
        """获取容易出错的功能"""
        return sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_time_usage_pattern(self) -> Dict[int, int]:
        """获取时间使用模式"""
        return dict(self.time_patterns)
    
    def get_recent_sequence_patterns(self, min_length: int = 3) -> List[List[str]]:
        """获取最近的序列模式"""
        try:
            sequences = []
            buffer_list = list(self.sequence_buffer)
            
            # 查找重复序列
            for length in range(min_length, min(len(buffer_list) // 2, 10)):
                for i in range(len(buffer_list) - length * 2 + 1):
                    sequence = buffer_list[i:i + length]
                    
                    # 检查是否在后续位置重复出现
                    for j in range(i + length, len(buffer_list) - length + 1):
                        if buffer_list[j:j + length] == sequence:
                            if sequence not in sequences:
                                sequences.append(sequence)
                            break
            
            return sequences
            
        except Exception as e:
            logger.error(f"获取序列模式失败: {e}")
            return []
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """获取会话统计"""
        try:
            if not self.session_actions:
                return {}
            
            session_duration = (datetime.now() - self.session_actions[0].timestamp).total_seconds()
            total_actions = len(self.session_actions)
            successful_actions = sum(1 for action in self.session_actions if action.success)
            error_rate = (total_actions - successful_actions) / total_actions if total_actions > 0 else 0
            
            return {
                "session_id": self.current_session_id,
                "duration": session_duration,
                "total_actions": total_actions,
                "successful_actions": successful_actions,
                "error_rate": error_rate,
                "actions_per_minute": total_actions / (session_duration / 60) if session_duration > 0 else 0,
                "unique_functions": len(set(action.function_name for action in self.session_actions)),
                "unique_components": len(set(action.component for action in self.session_actions))
            }
            
        except Exception as e:
            logger.error(f"获取会话统计失败: {e}")
            return {}


class PatternAnalyzer:
    """模式分析器"""
    
    def __init__(self, behavior_tracker: UsageBehaviorTracker):
        self.behavior_tracker = behavior_tracker
        self.detected_patterns: List[UsagePattern] = []
        
        logger.info("模式分析器初始化完成")
    
    def analyze_patterns(self) -> List[UsagePattern]:
        """分析使用模式"""
        try:
            patterns = []
            
            # 分析频率模式
            patterns.extend(self.analyze_frequency_patterns())
            
            # 分析时间模式
            patterns.extend(self.analyze_time_patterns())
            
            # 分析序列模式
            patterns.extend(self.analyze_sequence_patterns())
            
            # 分析错误模式
            patterns.extend(self.analyze_error_patterns())
            
            self.detected_patterns = patterns
            return patterns
            
        except Exception as e:
            logger.error(f"分析使用模式失败: {e}")
            return []
    
    def analyze_frequency_patterns(self) -> List[UsagePattern]:
        """分析频率模式"""
        patterns = []
        
        try:
            # 高频功能模式
            frequent_functions = self.behavior_tracker.get_frequent_functions(5)
            if frequent_functions:
                pattern = UsagePattern(
                    pattern_id="high_frequency_functions",
                    pattern_type="frequency",
                    frequency=sum(count for _, count in frequent_functions),
                    confidence=0.9,
                    components=[func for func, _ in frequent_functions]
                )
                patterns.append(pattern)
            
            # 高频组件模式
            frequent_components = self.behavior_tracker.get_frequent_components(5)
            if frequent_components:
                pattern = UsagePattern(
                    pattern_id="high_frequency_components",
                    pattern_type="frequency",
                    frequency=sum(count for _, count in frequent_components),
                    confidence=0.8,
                    components=[comp for comp, _ in frequent_components]
                )
                patterns.append(pattern)
                
        except Exception as e:
            logger.error(f"分析频率模式失败: {e}")
        
        return patterns
    
    def analyze_time_patterns(self) -> List[UsagePattern]:
        """分析时间模式"""
        patterns = []
        
        try:
            time_usage = self.behavior_tracker.get_time_usage_pattern()
            if not time_usage:
                return patterns
            
            # 找出使用高峰时段
            max_usage = max(time_usage.values())
            peak_hours = [hour for hour, usage in time_usage.items() 
                         if usage > max_usage * 0.7]
            
            if peak_hours:
                pattern = UsagePattern(
                    pattern_id="peak_usage_hours",
                    pattern_type="time",
                    frequency=sum(time_usage[hour] for hour in peak_hours),
                    confidence=0.7,
                    components=peak_hours,
                    time_patterns=time_usage
                )
                patterns.append(pattern)
                
        except Exception as e:
            logger.error(f"分析时间模式失败: {e}")
        
        return patterns
    
    def analyze_sequence_patterns(self) -> List[UsagePattern]:
        """分析序列模式"""
        patterns = []
        
        try:
            sequences = self.behavior_tracker.get_recent_sequence_patterns()
            
            for i, sequence in enumerate(sequences):
                pattern = UsagePattern(
                    pattern_id=f"sequence_pattern_{i}",
                    pattern_type="sequence",
                    frequency=1,  # 简化处理
                    confidence=0.6,
                    components=sequence,
                    sequence_patterns=[sequence]
                )
                patterns.append(pattern)
                
        except Exception as e:
            logger.error(f"分析序列模式失败: {e}")
        
        return patterns
    
    def analyze_error_patterns(self) -> List[UsagePattern]:
        """分析错误模式"""
        patterns = []
        
        try:
            error_functions = self.behavior_tracker.get_error_prone_functions(3)
            
            if error_functions:
                pattern = UsagePattern(
                    pattern_id="error_prone_functions",
                    pattern_type="error",
                    frequency=sum(count for _, count in error_functions),
                    confidence=0.8,
                    components=[func for func, _ in error_functions]
                )
                patterns.append(pattern)
                
        except Exception as e:
            logger.error(f"分析错误模式失败: {e}")

        return patterns


class AdaptationRecommendationEngine:
    """适应建议引擎"""

    def __init__(self, pattern_analyzer: PatternAnalyzer):
        self.pattern_analyzer = pattern_analyzer
        self.suggestion_history: List[AdaptationSuggestion] = []
        self.applied_suggestions: Set[str] = set()

        logger.info("适应建议引擎初始化完成")

    def generate_suggestions(self, patterns: List[UsagePattern]) -> List[AdaptationSuggestion]:
        """生成适应建议"""
        try:
            suggestions = []

            for pattern in patterns:
                if pattern.pattern_type == "frequency":
                    suggestions.extend(self.generate_frequency_suggestions(pattern))
                elif pattern.pattern_type == "time":
                    suggestions.extend(self.generate_time_suggestions(pattern))
                elif pattern.pattern_type == "sequence":
                    suggestions.extend(self.generate_sequence_suggestions(pattern))
                elif pattern.pattern_type == "error":
                    suggestions.extend(self.generate_error_suggestions(pattern))

            # 过滤已应用的建议
            suggestions = [s for s in suggestions if s.suggestion_id not in self.applied_suggestions]

            # 按影响分数排序
            suggestions.sort(key=lambda x: x.impact_score, reverse=True)

            self.suggestion_history.extend(suggestions)
            return suggestions

        except Exception as e:
            logger.error(f"生成适应建议失败: {e}")
            return []

    def generate_frequency_suggestions(self, pattern: UsagePattern) -> List[AdaptationSuggestion]:
        """生成频率相关建议"""
        suggestions = []

        try:
            if pattern.pattern_id == "high_frequency_functions":
                # 建议添加到工具栏
                suggestion = AdaptationSuggestion(
                    suggestion_id=f"toolbar_add_{pattern.pattern_id}",
                    adaptation_type=AdaptationType.TOOLBAR_CUSTOMIZATION,
                    title="添加常用功能到工具栏",
                    description=f"将您经常使用的功能添加到工具栏以便快速访问",
                    confidence=pattern.confidence,
                    impact_score=0.8,
                    implementation_difficulty=0.3,
                    target_components=pattern.components,
                    suggested_changes={
                        "action": "add_to_toolbar",
                        "functions": pattern.components[:3]  # 最多3个
                    },
                    reasoning="基于使用频率分析，这些功能值得快速访问",
                    auto_applicable=True
                )
                suggestions.append(suggestion)

                # 建议创建快捷键
                suggestion = AdaptationSuggestion(
                    suggestion_id=f"shortcut_create_{pattern.pattern_id}",
                    adaptation_type=AdaptationType.SHORTCUT_SUGGESTION,
                    title="为常用功能创建快捷键",
                    description=f"为您最常用的功能设置键盘快捷键",
                    confidence=pattern.confidence,
                    impact_score=0.9,
                    implementation_difficulty=0.2,
                    target_components=pattern.components,
                    suggested_changes={
                        "action": "create_shortcuts",
                        "functions": pattern.components[:5]
                    },
                    reasoning="快捷键可以显著提高操作效率",
                    auto_applicable=False
                )
                suggestions.append(suggestion)

            elif pattern.pattern_id == "high_frequency_components":
                # 建议优化组件布局
                suggestion = AdaptationSuggestion(
                    suggestion_id=f"layout_optimize_{pattern.pattern_id}",
                    adaptation_type=AdaptationType.UI_SIMPLIFICATION,
                    title="优化界面布局",
                    description=f"调整界面布局以突出您常用的组件",
                    confidence=pattern.confidence,
                    impact_score=0.7,
                    implementation_difficulty=0.5,
                    target_components=pattern.components,
                    suggested_changes={
                        "action": "optimize_layout",
                        "components": pattern.components,
                        "priority": "high"
                    },
                    reasoning="基于组件使用频率优化布局可以提升效率"
                )
                suggestions.append(suggestion)

        except Exception as e:
            logger.error(f"生成频率建议失败: {e}")

        return suggestions

    def generate_time_suggestions(self, pattern: UsagePattern) -> List[AdaptationSuggestion]:
        """生成时间相关建议"""
        suggestions = []

        try:
            if pattern.pattern_id == "peak_usage_hours":
                peak_hours = pattern.components

                # 建议主题适应
                if any(hour in [20, 21, 22, 23, 0, 1, 2, 3, 4, 5] for hour in peak_hours):
                    suggestion = AdaptationSuggestion(
                        suggestion_id="theme_dark_night",
                        adaptation_type=AdaptationType.THEME_ADAPTATION,
                        title="夜间模式建议",
                        description="检测到您经常在夜间使用软件，建议启用深色主题保护视力",
                        confidence=0.8,
                        impact_score=0.6,
                        implementation_difficulty=0.1,
                        target_components=["theme_manager"],
                        suggested_changes={
                            "action": "enable_dark_theme",
                            "schedule": "auto",
                            "hours": peak_hours
                        },
                        reasoning="夜间使用深色主题可以减少眼部疲劳",
                        auto_applicable=True
                    )
                    suggestions.append(suggestion)

        except Exception as e:
            logger.error(f"生成时间建议失败: {e}")

        return suggestions

    def generate_sequence_suggestions(self, pattern: UsagePattern) -> List[AdaptationSuggestion]:
        """生成序列相关建议"""
        suggestions = []

        try:
            if pattern.sequence_patterns:
                sequence = pattern.sequence_patterns[0]

                # 建议工作流程优化
                suggestion = AdaptationSuggestion(
                    suggestion_id=f"workflow_optimize_{pattern.pattern_id}",
                    adaptation_type=AdaptationType.WORKFLOW_OPTIMIZATION,
                    title="工作流程优化",
                    description=f"检测到您经常按顺序使用这些功能，建议创建快速工作流程",
                    confidence=pattern.confidence,
                    impact_score=0.7,
                    implementation_difficulty=0.6,
                    target_components=sequence,
                    suggested_changes={
                        "action": "create_workflow",
                        "sequence": sequence,
                        "name": f"工作流程_{len(self.suggestion_history)}"
                    },
                    reasoning="自动化重复的操作序列可以节省时间"
                )
                suggestions.append(suggestion)

        except Exception as e:
            logger.error(f"生成序列建议失败: {e}")

        return suggestions

    def generate_error_suggestions(self, pattern: UsagePattern) -> List[AdaptationSuggestion]:
        """生成错误相关建议"""
        suggestions = []

        try:
            if pattern.pattern_id == "error_prone_functions":
                # 建议教程
                suggestion = AdaptationSuggestion(
                    suggestion_id=f"tutorial_{pattern.pattern_id}",
                    adaptation_type=AdaptationType.TUTORIAL_SUGGESTION,
                    title="功能使用教程",
                    description=f"检测到您在使用某些功能时遇到困难，建议查看相关教程",
                    confidence=pattern.confidence,
                    impact_score=0.8,
                    implementation_difficulty=0.2,
                    target_components=pattern.components,
                    suggested_changes={
                        "action": "show_tutorial",
                        "functions": pattern.components,
                        "type": "interactive"
                    },
                    reasoning="学习正确的使用方法可以减少错误",
                    auto_applicable=False
                )
                suggestions.append(suggestion)

        except Exception as e:
            logger.error(f"生成错误建议失败: {e}")

        return suggestions

    def mark_suggestion_applied(self, suggestion_id: str):
        """标记建议已应用"""
        self.applied_suggestions.add(suggestion_id)
        logger.info(f"适应建议已应用: {suggestion_id}")

    def get_suggestion_statistics(self) -> Dict[str, Any]:
        """获取建议统计"""
        try:
            total_suggestions = len(self.suggestion_history)
            applied_count = len(self.applied_suggestions)

            # 按类型统计
            type_stats = defaultdict(int)
            for suggestion in self.suggestion_history:
                type_stats[suggestion.adaptation_type.value] += 1

            # 按影响分数统计
            high_impact = sum(1 for s in self.suggestion_history if s.impact_score > 0.7)
            medium_impact = sum(1 for s in self.suggestion_history if 0.4 <= s.impact_score <= 0.7)
            low_impact = sum(1 for s in self.suggestion_history if s.impact_score < 0.4)

            return {
                "total_suggestions": total_suggestions,
                "applied_suggestions": applied_count,
                "application_rate": applied_count / total_suggestions if total_suggestions > 0 else 0,
                "type_distribution": dict(type_stats),
                "impact_distribution": {
                    "high": high_impact,
                    "medium": medium_impact,
                    "low": low_impact
                },
                "auto_applicable": sum(1 for s in self.suggestion_history if s.auto_applicable)
            }

        except Exception as e:
            logger.error(f"获取建议统计失败: {e}")
            return {}


class IntelligentAdaptationManager(QObject):
    """智能适应管理器"""

    # 信号定义
    adaptation_suggested = pyqtSignal(list)  # 适应建议信号
    adaptation_applied = pyqtSignal(str)     # 适应应用信号
    pattern_detected = pyqtSignal(list)      # 模式检测信号

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.behavior_tracker = UsageBehaviorTracker()
        self.pattern_analyzer = PatternAnalyzer(self.behavior_tracker)
        self.recommendation_engine = AdaptationRecommendationEngine(self.pattern_analyzer)

        # 分析定时器
        self.analysis_timer = QTimer()
        self.analysis_timer.timeout.connect(self.perform_periodic_analysis)
        self.analysis_timer.start(300000)  # 5分钟分析一次

        # 自动应用设置
        self.auto_apply_enabled = True
        self.auto_apply_threshold = 0.8  # 自动应用阈值

        logger.info("智能适应管理器初始化完成")

    def track_user_action(self, action_type: ActionType, component: str,
                         function_name: str, duration: float = 0.0,
                         success: bool = True, context: Dict[str, Any] = None):
        """跟踪用户动作"""
        try:
            self.behavior_tracker.track_action(
                action_type, component, function_name,
                duration, success, context
            )

            # 检查是否需要立即分析
            if len(self.behavior_tracker.actions) % 100 == 0:
                self.perform_immediate_analysis()

        except Exception as e:
            logger.error(f"跟踪用户动作失败: {e}")

    def perform_periodic_analysis(self):
        """执行定期分析"""
        try:
            patterns = self.pattern_analyzer.analyze_patterns()
            if patterns:
                self.pattern_detected.emit(patterns)

                # 生成建议
                suggestions = self.recommendation_engine.generate_suggestions(patterns)
                if suggestions:
                    self.adaptation_suggested.emit(suggestions)

                    # 自动应用高置信度建议
                    if self.auto_apply_enabled:
                        self.auto_apply_suggestions(suggestions)

        except Exception as e:
            logger.error(f"定期分析失败: {e}")

    def perform_immediate_analysis(self):
        """执行即时分析"""
        try:
            # 只分析最近的模式
            recent_patterns = self.pattern_analyzer.analyze_patterns()
            if recent_patterns:
                # 生成紧急建议（如错误模式）
                urgent_suggestions = []
                for pattern in recent_patterns:
                    if pattern.pattern_type == "error" and pattern.confidence > 0.7:
                        suggestions = self.recommendation_engine.generate_error_suggestions(pattern)
                        urgent_suggestions.extend(suggestions)

                if urgent_suggestions:
                    self.adaptation_suggested.emit(urgent_suggestions)

        except Exception as e:
            logger.error(f"即时分析失败: {e}")

    def auto_apply_suggestions(self, suggestions: List[AdaptationSuggestion]):
        """自动应用建议"""
        try:
            for suggestion in suggestions:
                if (suggestion.auto_applicable and
                    suggestion.confidence >= self.auto_apply_threshold and
                    suggestion.implementation_difficulty <= 0.3):

                    success = self.apply_suggestion(suggestion)
                    if success:
                        self.recommendation_engine.mark_suggestion_applied(suggestion.suggestion_id)
                        self.adaptation_applied.emit(suggestion.suggestion_id)
                        logger.info(f"自动应用建议: {suggestion.title}")

        except Exception as e:
            logger.error(f"自动应用建议失败: {e}")

    def apply_suggestion(self, suggestion: AdaptationSuggestion) -> bool:
        """应用建议"""
        try:
            changes = suggestion.suggested_changes

            if suggestion.adaptation_type == AdaptationType.TOOLBAR_CUSTOMIZATION:
                return self.apply_toolbar_customization(changes)
            elif suggestion.adaptation_type == AdaptationType.THEME_ADAPTATION:
                return self.apply_theme_adaptation(changes)
            elif suggestion.adaptation_type == AdaptationType.UI_SIMPLIFICATION:
                return self.apply_ui_simplification(changes)
            elif suggestion.adaptation_type == AdaptationType.SHORTCUT_SUGGESTION:
                return self.apply_shortcut_suggestion(changes)
            elif suggestion.adaptation_type == AdaptationType.WORKFLOW_OPTIMIZATION:
                return self.apply_workflow_optimization(changes)
            else:
                logger.warning(f"未支持的适应类型: {suggestion.adaptation_type}")
                return False

        except Exception as e:
            logger.error(f"应用建议失败: {e}")
            return False

    def apply_toolbar_customization(self, changes: Dict[str, Any]) -> bool:
        """应用工具栏定制"""
        try:
            if changes.get("action") == "add_to_toolbar":
                functions = changes.get("functions", [])

                # 获取主窗口工具栏
                if hasattr(self.main_window, 'toolbar_manager'):
                    toolbar_manager = self.main_window.toolbar_manager

                    for function in functions:
                        toolbar_manager.add_function_to_toolbar(function)

                    return True

        except Exception as e:
            logger.error(f"应用工具栏定制失败: {e}")

        return False

    def apply_theme_adaptation(self, changes: Dict[str, Any]) -> bool:
        """应用主题适应"""
        try:
            if changes.get("action") == "enable_dark_theme":
                # 获取工作空间管理器
                if hasattr(self.main_window, 'workspace_manager'):
                    workspace_manager = self.main_window.workspace_manager
                    workspace_manager.apply_dark_theme()
                    return True

        except Exception as e:
            logger.error(f"应用主题适应失败: {e}")

        return False

    def apply_ui_simplification(self, changes: Dict[str, Any]) -> bool:
        """应用界面简化"""
        try:
            if changes.get("action") == "optimize_layout":
                components = changes.get("components", [])
                priority = changes.get("priority", "normal")

                # 调整组件优先级
                for component in components:
                    if hasattr(self.main_window, component):
                        widget = getattr(self.main_window, component)
                        if hasattr(widget, 'set_priority'):
                            widget.set_priority(priority)

                return True

        except Exception as e:
            logger.error(f"应用界面简化失败: {e}")

        return False

    def apply_shortcut_suggestion(self, changes: Dict[str, Any]) -> bool:
        """应用快捷键建议"""
        try:
            # 这里需要用户确认，不能自动应用
            return False

        except Exception as e:
            logger.error(f"应用快捷键建议失败: {e}")

        return False

    def apply_workflow_optimization(self, changes: Dict[str, Any]) -> bool:
        """应用工作流程优化"""
        try:
            # 工作流程优化需要用户确认
            return False

        except Exception as e:
            logger.error(f"应用工作流程优化失败: {e}")

        return False

    def show_adaptation_dialog(self, suggestions: List[AdaptationSuggestion]):
        """显示适应建议对话框"""
        try:
            dialog = AdaptationSuggestionDialog(suggestions, self.main_window)
            dialog.suggestion_accepted.connect(self.on_suggestion_accepted)
            dialog.suggestion_rejected.connect(self.on_suggestion_rejected)
            dialog.exec()

        except Exception as e:
            logger.error(f"显示适应对话框失败: {e}")

    def on_suggestion_accepted(self, suggestion_id: str):
        """建议被接受"""
        try:
            # 查找建议
            suggestion = None
            for s in self.recommendation_engine.suggestion_history:
                if s.suggestion_id == suggestion_id:
                    suggestion = s
                    break

            if suggestion:
                success = self.apply_suggestion(suggestion)
                if success:
                    self.recommendation_engine.mark_suggestion_applied(suggestion_id)
                    self.adaptation_applied.emit(suggestion_id)

        except Exception as e:
            logger.error(f"处理建议接受失败: {e}")

    def on_suggestion_rejected(self, suggestion_id: str):
        """建议被拒绝"""
        try:
            # 标记为已处理（拒绝）
            self.recommendation_engine.mark_suggestion_applied(suggestion_id)
            logger.info(f"用户拒绝建议: {suggestion_id}")

        except Exception as e:
            logger.error(f"处理建议拒绝失败: {e}")

    def get_adaptation_statistics(self) -> Dict[str, Any]:
        """获取适应统计"""
        try:
            behavior_stats = self.behavior_tracker.get_session_statistics()
            suggestion_stats = self.recommendation_engine.get_suggestion_statistics()

            return {
                "behavior_tracking": behavior_stats,
                "suggestions": suggestion_stats,
                "user_level": self.behavior_tracker.estimate_user_level().value,
                "auto_apply_enabled": self.auto_apply_enabled,
                "analysis_interval": self.analysis_timer.interval() // 1000  # 转换为秒
            }

        except Exception as e:
            logger.error(f"获取适应统计失败: {e}")
            return {}

    def set_auto_apply_enabled(self, enabled: bool):
        """设置自动应用"""
        self.auto_apply_enabled = enabled
        logger.info(f"自动应用设置: {enabled}")

    def set_analysis_interval(self, seconds: int):
        """设置分析间隔"""
        self.analysis_timer.setInterval(seconds * 1000)
        logger.info(f"分析间隔设置: {seconds}秒")


class AdaptationSuggestionDialog(QDialog):
    """适应建议对话框"""

    suggestion_accepted = pyqtSignal(str)  # 建议接受信号
    suggestion_rejected = pyqtSignal(str)  # 建议拒绝信号

    def __init__(self, suggestions: List[AdaptationSuggestion], parent=None):
        super().__init__(parent)
        self.suggestions = suggestions
        self.current_suggestion_index = 0

        self.setup_ui()
        self.load_current_suggestion()

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("智能适应建议")
        self.setMinimumSize(600, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel("🧠 智能适应建议")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c5aa0; margin: 10px;")
        layout.addWidget(title_label)

        # 建议计数
        self.count_label = QLabel()
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.count_label)

        # 建议内容区域
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        content_layout = QVBoxLayout(content_frame)

        # 建议标题
        self.suggestion_title = QLabel()
        self.suggestion_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        self.suggestion_title.setWordWrap(True)
        content_layout.addWidget(self.suggestion_title)

        # 建议描述
        self.suggestion_description = QLabel()
        self.suggestion_description.setWordWrap(True)
        self.suggestion_description.setMinimumHeight(60)
        content_layout.addWidget(self.suggestion_description)

        # 建议详情
        details_group = QGroupBox("建议详情")
        details_layout = QFormLayout(details_group)

        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)
        details_layout.addRow("置信度:", self.confidence_bar)

        self.impact_bar = QProgressBar()
        self.impact_bar.setRange(0, 100)
        details_layout.addRow("影响程度:", self.impact_bar)

        self.difficulty_bar = QProgressBar()
        self.difficulty_bar.setRange(0, 100)
        details_layout.addRow("实施难度:", self.difficulty_bar)

        self.reasoning_label = QLabel()
        self.reasoning_label.setWordWrap(True)
        details_layout.addRow("建议理由:", self.reasoning_label)

        content_layout.addWidget(details_group)
        layout.addWidget(content_frame)

        # 导航按钮
        nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("⬅️ 上一个")
        self.prev_btn.clicked.connect(self.previous_suggestion)
        nav_layout.addWidget(self.prev_btn)

        nav_layout.addStretch()

        self.next_btn = QPushButton("下一个 ➡️")
        self.next_btn.clicked.connect(self.next_suggestion)
        nav_layout.addWidget(self.next_btn)

        layout.addLayout(nav_layout)

        # 操作按钮
        action_layout = QHBoxLayout()

        self.reject_btn = QPushButton("❌ 拒绝")
        self.reject_btn.clicked.connect(self.reject_current_suggestion)
        action_layout.addWidget(self.reject_btn)

        self.accept_btn = QPushButton("✅ 接受")
        self.accept_btn.clicked.connect(self.accept_current_suggestion)
        self.accept_btn.setStyleSheet("""
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
        action_layout.addWidget(self.accept_btn)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        action_layout.addWidget(self.close_btn)

        layout.addLayout(action_layout)

    def load_current_suggestion(self):
        """加载当前建议"""
        if not self.suggestions or self.current_suggestion_index >= len(self.suggestions):
            return

        suggestion = self.suggestions[self.current_suggestion_index]

        # 更新计数
        self.count_label.setText(f"建议 {self.current_suggestion_index + 1} / {len(self.suggestions)}")

        # 更新内容
        self.suggestion_title.setText(suggestion.title)
        self.suggestion_description.setText(suggestion.description)

        # 更新详情
        self.confidence_bar.setValue(int(suggestion.confidence * 100))
        self.impact_bar.setValue(int(suggestion.impact_score * 100))
        self.difficulty_bar.setValue(int(suggestion.implementation_difficulty * 100))
        self.reasoning_label.setText(suggestion.reasoning)

        # 更新导航按钮状态
        self.prev_btn.setEnabled(self.current_suggestion_index > 0)
        self.next_btn.setEnabled(self.current_suggestion_index < len(self.suggestions) - 1)

    def previous_suggestion(self):
        """上一个建议"""
        if self.current_suggestion_index > 0:
            self.current_suggestion_index -= 1
            self.load_current_suggestion()

    def next_suggestion(self):
        """下一个建议"""
        if self.current_suggestion_index < len(self.suggestions) - 1:
            self.current_suggestion_index += 1
            self.load_current_suggestion()

    def accept_current_suggestion(self):
        """接受当前建议"""
        if self.suggestions and self.current_suggestion_index < len(self.suggestions):
            suggestion = self.suggestions[self.current_suggestion_index]
            self.suggestion_accepted.emit(suggestion.suggestion_id)

            # 移除已接受的建议
            self.suggestions.pop(self.current_suggestion_index)

            # 调整索引
            if self.current_suggestion_index >= len(self.suggestions):
                self.current_suggestion_index = max(0, len(self.suggestions) - 1)

            # 更新显示
            if self.suggestions:
                self.load_current_suggestion()
            else:
                self.accept()  # 关闭对话框

    def reject_current_suggestion(self):
        """拒绝当前建议"""
        if self.suggestions and self.current_suggestion_index < len(self.suggestions):
            suggestion = self.suggestions[self.current_suggestion_index]
            self.suggestion_rejected.emit(suggestion.suggestion_id)

            # 移除已拒绝的建议
            self.suggestions.pop(self.current_suggestion_index)

            # 调整索引
            if self.current_suggestion_index >= len(self.suggestions):
                self.current_suggestion_index = max(0, len(self.suggestions) - 1)

            # 更新显示
            if self.suggestions:
                self.load_current_suggestion()
            else:
                self.accept()  # 关闭对话框
