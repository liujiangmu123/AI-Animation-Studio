"""
AI Animation Studio - 渐进式功能披露系统
基于用户专业水平和使用情况的智能功能披露实现
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QScrollArea, QGroupBox, QTabWidget, QToolBar,
                             QMenuBar, QStatusBar, QSplitter, QCheckBox, QSlider,
                             QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QIcon, QAction

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
import json
from dataclasses import dataclass
from datetime import datetime, timedelta

from core.value_hierarchy_config import UserExpertiseLevel, PriorityLevel, WorkflowStage
from core.logger import get_logger

logger = get_logger("progressive_function_disclosure_system")


class DisclosureStrategy(Enum):
    """披露策略枚举"""
    IMMEDIATE = "immediate"         # 立即显示
    ON_DEMAND = "on_demand"        # 按需显示
    CONTEXTUAL = "contextual"      # 上下文相关
    PROGRESSIVE = "progressive"    # 渐进式显示
    ADAPTIVE = "adaptive"          # 自适应显示


class FunctionComplexity(Enum):
    """功能复杂度枚举"""
    SIMPLE = 1          # 简单功能
    MODERATE = 2        # 中等复杂度
    COMPLEX = 3         # 复杂功能
    EXPERT_ONLY = 4     # 专家级功能


class UsageFrequency(Enum):
    """使用频率枚举"""
    NEVER = 0           # 从未使用
    RARE = 1            # 很少使用
    OCCASIONAL = 2      # 偶尔使用
    FREQUENT = 3        # 经常使用
    CONSTANT = 4        # 持续使用


@dataclass
class FunctionMetadata:
    """功能元数据"""
    function_id: str
    name: str
    description: str
    category: str
    complexity: FunctionComplexity
    min_expertise: UserExpertiseLevel
    workflow_stage: Optional[WorkflowStage]
    disclosure_strategy: DisclosureStrategy
    priority: int = 1
    icon: str = ""
    tooltip: str = ""
    shortcut: str = ""
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class UsageStatistics:
    """使用统计"""
    function_id: str
    usage_count: int = 0
    last_used: Optional[datetime] = None
    total_time_used: float = 0.0  # 秒
    success_rate: float = 1.0
    user_rating: float = 0.0
    frequency: UsageFrequency = UsageFrequency.NEVER


class ProgressiveFunctionDisclosureEngine:
    """渐进式功能披露引擎"""
    
    def __init__(self):
        self.functions_metadata = self.initialize_functions_metadata()
        self.usage_statistics: Dict[str, UsageStatistics] = {}
        self.current_user_level = UserExpertiseLevel.INTERMEDIATE
        self.current_workflow_stage = WorkflowStage.AUDIO_IMPORT
        self.disclosed_functions: Set[str] = set()
        self.learning_enabled = True
        
        logger.info("渐进式功能披露引擎初始化完成")
    
    def initialize_functions_metadata(self) -> Dict[str, FunctionMetadata]:
        """初始化功能元数据"""
        return {
            # 核心功能 - 始终可见
            "audio_import": FunctionMetadata(
                "audio_import", "音频导入", "导入音频文件作为动画基础",
                "核心功能", FunctionComplexity.SIMPLE, UserExpertiseLevel.BEGINNER,
                WorkflowStage.AUDIO_IMPORT, DisclosureStrategy.IMMEDIATE,
                priority=10, icon="🎵", tooltip="点击导入音频文件"
            ),
            "time_segment_basic": FunctionMetadata(
                "time_segment_basic", "基础时间段", "创建基本时间段标记",
                "核心功能", FunctionComplexity.SIMPLE, UserExpertiseLevel.BEGINNER,
                WorkflowStage.TIME_MARKING, DisclosureStrategy.IMMEDIATE,
                priority=9, icon="⏱️", tooltip="在时间轴上标记时间段"
            ),
            "simple_description": FunctionMetadata(
                "simple_description", "简单描述", "添加简单的动画描述",
                "核心功能", FunctionComplexity.SIMPLE, UserExpertiseLevel.BEGINNER,
                WorkflowStage.DESCRIPTION, DisclosureStrategy.IMMEDIATE,
                priority=8, icon="📝", tooltip="描述想要的动画效果"
            ),
            "ai_generate_basic": FunctionMetadata(
                "ai_generate_basic", "AI生成", "使用AI生成基础动画",
                "核心功能", FunctionComplexity.SIMPLE, UserExpertiseLevel.BEGINNER,
                WorkflowStage.AI_GENERATION, DisclosureStrategy.IMMEDIATE,
                priority=7, icon="🤖", tooltip="让AI为您生成动画"
            ),
            "preview_basic": FunctionMetadata(
                "preview_basic", "基础预览", "预览生成的动画效果",
                "核心功能", FunctionComplexity.SIMPLE, UserExpertiseLevel.BEGINNER,
                WorkflowStage.PREVIEW_ADJUST, DisclosureStrategy.IMMEDIATE,
                priority=6, icon="👁️", tooltip="预览动画效果"
            ),
            
            # 中级功能 - 渐进披露
            "audio_advanced": FunctionMetadata(
                "audio_advanced", "高级音频", "高级音频处理和分析",
                "音频处理", FunctionComplexity.MODERATE, UserExpertiseLevel.INTERMEDIATE,
                WorkflowStage.AUDIO_IMPORT, DisclosureStrategy.PROGRESSIVE,
                priority=5, icon="🎚️", tooltip="高级音频处理选项",
                dependencies=["audio_import"]
            ),
            "time_segment_advanced": FunctionMetadata(
                "time_segment_advanced", "高级时间段", "精确的时间段控制",
                "时间控制", FunctionComplexity.MODERATE, UserExpertiseLevel.INTERMEDIATE,
                WorkflowStage.TIME_MARKING, DisclosureStrategy.ON_DEMAND,
                priority=5, icon="⏰", tooltip="精确控制时间段",
                dependencies=["time_segment_basic"]
            ),
            "element_editing": FunctionMetadata(
                "element_editing", "元素编辑", "编辑动画元素属性",
                "编辑工具", FunctionComplexity.MODERATE, UserExpertiseLevel.INTERMEDIATE,
                WorkflowStage.PREVIEW_ADJUST, DisclosureStrategy.CONTEXTUAL,
                priority=4, icon="✏️", tooltip="编辑动画元素"
            ),
            "ai_generate_advanced": FunctionMetadata(
                "ai_generate_advanced", "高级AI生成", "高级AI生成选项",
                "AI功能", FunctionComplexity.MODERATE, UserExpertiseLevel.INTERMEDIATE,
                WorkflowStage.AI_GENERATION, DisclosureStrategy.PROGRESSIVE,
                priority=4, icon="🧠", tooltip="高级AI生成选项",
                dependencies=["ai_generate_basic"]
            ),
            "preview_advanced": FunctionMetadata(
                "preview_advanced", "高级预览", "高级预览和调试功能",
                "预览工具", FunctionComplexity.MODERATE, UserExpertiseLevel.INTERMEDIATE,
                WorkflowStage.PREVIEW_ADJUST, DisclosureStrategy.ON_DEMAND,
                priority=4, icon="🔍", tooltip="高级预览选项",
                dependencies=["preview_basic"]
            ),
            "export_basic": FunctionMetadata(
                "export_basic", "基础导出", "基本的导出功能",
                "导出工具", FunctionComplexity.MODERATE, UserExpertiseLevel.INTERMEDIATE,
                WorkflowStage.EXPORT, DisclosureStrategy.CONTEXTUAL,
                priority=3, icon="📤", tooltip="导出动画作品"
            ),
            
            # 专家功能 - 按需披露
            "custom_rules": FunctionMetadata(
                "custom_rules", "自定义规则", "创建自定义动画规则",
                "高级工具", FunctionComplexity.EXPERT_ONLY, UserExpertiseLevel.EXPERT,
                None, DisclosureStrategy.ADAPTIVE,
                priority=2, icon="⚙️", tooltip="创建自定义动画规则"
            ),
            "script_editing": FunctionMetadata(
                "script_editing", "脚本编辑", "直接编辑动画脚本",
                "开发工具", FunctionComplexity.EXPERT_ONLY, UserExpertiseLevel.EXPERT,
                WorkflowStage.AI_GENERATION, DisclosureStrategy.ON_DEMAND,
                priority=2, icon="📜", tooltip="编辑动画脚本代码"
            ),
            "performance_monitoring": FunctionMetadata(
                "performance_monitoring", "性能监控", "监控动画性能",
                "开发工具", FunctionComplexity.EXPERT_ONLY, UserExpertiseLevel.EXPERT,
                None, DisclosureStrategy.ADAPTIVE,
                priority=1, icon="📊", tooltip="监控动画性能"
            ),
            "batch_operations": FunctionMetadata(
                "batch_operations", "批量操作", "批量处理多个对象",
                "效率工具", FunctionComplexity.COMPLEX, UserExpertiseLevel.ADVANCED,
                None, DisclosureStrategy.ADAPTIVE,
                priority=2, icon="📋", tooltip="批量处理操作"
            ),
            "developer_tools": FunctionMetadata(
                "developer_tools", "开发者工具", "开发者调试工具",
                "开发工具", FunctionComplexity.EXPERT_ONLY, UserExpertiseLevel.EXPERT,
                None, DisclosureStrategy.ON_DEMAND,
                priority=1, icon="🔧", tooltip="开发者调试工具"
            )
        }
    
    def should_disclose_function(self, function_id: str) -> bool:
        """判断是否应该披露某个功能"""
        try:
            metadata = self.functions_metadata.get(function_id)
            if not metadata:
                return False
            
            # 检查用户专业水平要求
            if not self._meets_expertise_requirement(metadata):
                return False
            
            # 检查依赖关系
            if not self._dependencies_satisfied(metadata):
                return False
            
            # 根据披露策略判断
            return self._evaluate_disclosure_strategy(metadata)
            
        except Exception as e:
            logger.error(f"判断功能披露失败 {function_id}: {e}")
            return False
    
    def _meets_expertise_requirement(self, metadata: FunctionMetadata) -> bool:
        """检查是否满足专业水平要求"""
        level_values = {
            UserExpertiseLevel.BEGINNER: 1,
            UserExpertiseLevel.INTERMEDIATE: 2,
            UserExpertiseLevel.ADVANCED: 3,
            UserExpertiseLevel.EXPERT: 4
        }
        
        current_level = level_values.get(self.current_user_level, 1)
        required_level = level_values.get(metadata.min_expertise, 1)
        
        return current_level >= required_level
    
    def _dependencies_satisfied(self, metadata: FunctionMetadata) -> bool:
        """检查依赖关系是否满足"""
        for dep_id in metadata.dependencies:
            if dep_id not in self.disclosed_functions:
                # 检查依赖是否已被使用过
                dep_stats = self.usage_statistics.get(dep_id)
                if not dep_stats or dep_stats.usage_count == 0:
                    return False
        return True
    
    def _evaluate_disclosure_strategy(self, metadata: FunctionMetadata) -> bool:
        """评估披露策略"""
        strategy = metadata.disclosure_strategy
        
        if strategy == DisclosureStrategy.IMMEDIATE:
            return True
        
        elif strategy == DisclosureStrategy.ON_DEMAND:
            # 已经被明确请求或使用过
            return metadata.function_id in self.disclosed_functions
        
        elif strategy == DisclosureStrategy.CONTEXTUAL:
            # 根据当前工作流程阶段判断
            return metadata.workflow_stage == self.current_workflow_stage
        
        elif strategy == DisclosureStrategy.PROGRESSIVE:
            # 基于使用统计渐进披露
            return self._should_progressively_disclose(metadata)
        
        elif strategy == DisclosureStrategy.ADAPTIVE:
            # 自适应披露
            return self._should_adaptively_disclose(metadata)
        
        return False
    
    def _should_progressively_disclose(self, metadata: FunctionMetadata) -> bool:
        """判断是否应该渐进披露"""
        # 检查依赖功能的使用情况
        for dep_id in metadata.dependencies:
            dep_stats = self.usage_statistics.get(dep_id)
            if dep_stats and dep_stats.usage_count >= 3:  # 依赖功能使用3次以上
                return True
        
        # 检查相同类别功能的使用情况
        category_usage = self._get_category_usage(metadata.category)
        return category_usage >= 5  # 同类别功能总使用次数5次以上
    
    def _should_adaptively_disclose(self, metadata: FunctionMetadata) -> bool:
        """判断是否应该自适应披露"""
        if not self.learning_enabled:
            return False
        
        # 基于用户行为模式判断
        user_pattern = self._analyze_user_pattern()
        
        # 如果用户是探索型，更容易披露新功能
        if user_pattern.get('exploration_tendency', 0) > 0.7:
            return True
        
        # 如果用户在相关领域很活跃
        if metadata.category in user_pattern.get('active_categories', []):
            return True
        
        # 如果功能与用户常用功能相关
        related_usage = self._get_related_functions_usage(metadata)
        return related_usage > 10
    
    def _get_category_usage(self, category: str) -> int:
        """获取分类使用次数"""
        total_usage = 0
        for func_id, metadata in self.functions_metadata.items():
            if metadata.category == category:
                stats = self.usage_statistics.get(func_id)
                if stats:
                    total_usage += stats.usage_count
        return total_usage
    
    def _analyze_user_pattern(self) -> Dict[str, Any]:
        """分析用户使用模式"""
        pattern = {
            'exploration_tendency': 0.0,
            'active_categories': [],
            'preferred_complexity': FunctionComplexity.SIMPLE,
            'usage_consistency': 0.0
        }
        
        if not self.usage_statistics:
            return pattern
        
        # 计算探索倾向
        total_functions = len(self.functions_metadata)
        used_functions = len([s for s in self.usage_statistics.values() if s.usage_count > 0])
        pattern['exploration_tendency'] = used_functions / total_functions if total_functions > 0 else 0
        
        # 分析活跃分类
        category_usage = {}
        for func_id, stats in self.usage_statistics.items():
            if stats.usage_count > 0:
                metadata = self.functions_metadata.get(func_id)
                if metadata:
                    category = metadata.category
                    category_usage[category] = category_usage.get(category, 0) + stats.usage_count
        
        # 取使用次数最多的前3个分类
        sorted_categories = sorted(category_usage.items(), key=lambda x: x[1], reverse=True)
        pattern['active_categories'] = [cat for cat, _ in sorted_categories[:3]]
        
        return pattern
    
    def _get_related_functions_usage(self, metadata: FunctionMetadata) -> int:
        """获取相关功能使用次数"""
        related_usage = 0
        
        # 同分类功能
        for func_id, func_metadata in self.functions_metadata.items():
            if func_metadata.category == metadata.category:
                stats = self.usage_statistics.get(func_id)
                if stats:
                    related_usage += stats.usage_count
        
        # 同工作流程阶段功能
        if metadata.workflow_stage:
            for func_id, func_metadata in self.functions_metadata.items():
                if func_metadata.workflow_stage == metadata.workflow_stage:
                    stats = self.usage_statistics.get(func_id)
                    if stats:
                        related_usage += stats.usage_count
        
        return related_usage
    
    def record_function_usage(self, function_id: str, duration: float = 0.0, success: bool = True):
        """记录功能使用"""
        try:
            if function_id not in self.usage_statistics:
                self.usage_statistics[function_id] = UsageStatistics(function_id)
            
            stats = self.usage_statistics[function_id]
            stats.usage_count += 1
            stats.last_used = datetime.now()
            stats.total_time_used += duration
            
            # 更新成功率
            if success:
                stats.success_rate = (stats.success_rate * (stats.usage_count - 1) + 1.0) / stats.usage_count
            else:
                stats.success_rate = (stats.success_rate * (stats.usage_count - 1) + 0.0) / stats.usage_count
            
            # 更新使用频率
            stats.frequency = self._calculate_usage_frequency(stats)
            
            # 自动披露相关功能
            if self.learning_enabled:
                self._auto_disclose_related_functions(function_id)
            
            logger.debug(f"记录功能使用: {function_id}, 成功: {success}")
            
        except Exception as e:
            logger.error(f"记录功能使用失败 {function_id}: {e}")
    
    def _calculate_usage_frequency(self, stats: UsageStatistics) -> UsageFrequency:
        """计算使用频率"""
        if not stats.last_used:
            return UsageFrequency.NEVER
        
        days_since_last_use = (datetime.now() - stats.last_used).days
        
        if stats.usage_count == 0:
            return UsageFrequency.NEVER
        elif stats.usage_count < 3 or days_since_last_use > 30:
            return UsageFrequency.RARE
        elif stats.usage_count < 10 or days_since_last_use > 7:
            return UsageFrequency.OCCASIONAL
        elif stats.usage_count < 50 or days_since_last_use > 1:
            return UsageFrequency.FREQUENT
        else:
            return UsageFrequency.CONSTANT
    
    def _auto_disclose_related_functions(self, function_id: str):
        """自动披露相关功能"""
        metadata = self.functions_metadata.get(function_id)
        if not metadata:
            return
        
        # 披露依赖此功能的功能
        for func_id, func_metadata in self.functions_metadata.items():
            if function_id in func_metadata.dependencies:
                if self.should_disclose_function(func_id):
                    self.disclosed_functions.add(func_id)
                    logger.info(f"自动披露相关功能: {func_id}")
    
    def request_function_disclosure(self, function_id: str):
        """请求披露功能"""
        if function_id in self.functions_metadata:
            self.disclosed_functions.add(function_id)
            logger.info(f"用户请求披露功能: {function_id}")
    
    def set_user_level(self, level: UserExpertiseLevel):
        """设置用户专业水平"""
        if level != self.current_user_level:
            self.current_user_level = level
            # 重新评估所有功能的披露状态
            self._reevaluate_all_disclosures()
            logger.info(f"用户专业水平更新为: {level.value}")
    
    def set_workflow_stage(self, stage: WorkflowStage):
        """设置当前工作流程阶段"""
        if stage != self.current_workflow_stage:
            self.current_workflow_stage = stage
            # 重新评估上下文相关功能
            self._reevaluate_contextual_disclosures()
            logger.info(f"工作流程阶段更新为: {stage.value}")
    
    def _reevaluate_all_disclosures(self):
        """重新评估所有功能披露"""
        for function_id in self.functions_metadata.keys():
            if self.should_disclose_function(function_id):
                self.disclosed_functions.add(function_id)
            else:
                self.disclosed_functions.discard(function_id)
    
    def _reevaluate_contextual_disclosures(self):
        """重新评估上下文相关功能披露"""
        for function_id, metadata in self.functions_metadata.items():
            if metadata.disclosure_strategy == DisclosureStrategy.CONTEXTUAL:
                if self.should_disclose_function(function_id):
                    self.disclosed_functions.add(function_id)
                else:
                    self.disclosed_functions.discard(function_id)
    
    def get_disclosed_functions(self) -> List[FunctionMetadata]:
        """获取当前应该披露的功能"""
        disclosed = []
        for function_id in self.functions_metadata.keys():
            if self.should_disclose_function(function_id):
                disclosed.append(self.functions_metadata[function_id])
        
        # 按优先级排序
        disclosed.sort(key=lambda f: f.priority, reverse=True)
        return disclosed
    
    def get_function_metadata(self, function_id: str) -> Optional[FunctionMetadata]:
        """获取功能元数据"""
        return self.functions_metadata.get(function_id)
    
    def get_usage_statistics(self, function_id: str) -> Optional[UsageStatistics]:
        """获取使用统计"""
        return self.usage_statistics.get(function_id)
    
    def export_disclosure_state(self) -> Dict[str, Any]:
        """导出披露状态"""
        return {
            "user_level": self.current_user_level.value,
            "workflow_stage": self.current_workflow_stage.value,
            "disclosed_functions": list(self.disclosed_functions),
            "usage_statistics": {
                func_id: {
                    "usage_count": stats.usage_count,
                    "last_used": stats.last_used.isoformat() if stats.last_used else None,
                    "total_time_used": stats.total_time_used,
                    "success_rate": stats.success_rate,
                    "frequency": stats.frequency.value
                }
                for func_id, stats in self.usage_statistics.items()
            }
        }
    
    def import_disclosure_state(self, state: Dict[str, Any]):
        """导入披露状态"""
        try:
            self.current_user_level = UserExpertiseLevel(state.get("user_level", "intermediate"))
            self.current_workflow_stage = WorkflowStage(state.get("workflow_stage", 1))
            self.disclosed_functions = set(state.get("disclosed_functions", []))
            
            # 导入使用统计
            stats_data = state.get("usage_statistics", {})
            for func_id, stats_dict in stats_data.items():
                stats = UsageStatistics(func_id)
                stats.usage_count = stats_dict.get("usage_count", 0)
                if stats_dict.get("last_used"):
                    stats.last_used = datetime.fromisoformat(stats_dict["last_used"])
                stats.total_time_used = stats_dict.get("total_time_used", 0.0)
                stats.success_rate = stats_dict.get("success_rate", 1.0)
                stats.frequency = UsageFrequency(stats_dict.get("frequency", 0))
                
                self.usage_statistics[func_id] = stats
            
            logger.info("披露状态导入完成")
            
        except Exception as e:
            logger.error(f"导入披露状态失败: {e}")
    
    def get_disclosure_summary(self) -> Dict[str, Any]:
        """获取披露摘要"""
        disclosed_functions = self.get_disclosed_functions()
        
        return {
            "user_level": self.current_user_level.value,
            "workflow_stage": self.current_workflow_stage.value,
            "total_functions": len(self.functions_metadata),
            "disclosed_functions": len(disclosed_functions),
            "disclosure_rate": len(disclosed_functions) / len(self.functions_metadata) if self.functions_metadata else 0,
            "functions_by_complexity": {
                complexity.name: len([f for f in disclosed_functions if f.complexity == complexity])
                for complexity in FunctionComplexity
            },
            "functions_by_category": {
                category: len([f for f in disclosed_functions if f.category == category])
                for category in set(f.category for f in disclosed_functions)
            },
            "learning_enabled": self.learning_enabled
        }


class ProgressiveDisclosureUIManager(QObject):
    """渐进式披露UI管理器"""

    function_requested = pyqtSignal(str)  # 功能请求信号
    disclosure_changed = pyqtSignal()     # 披露状态改变信号

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.disclosure_engine = ProgressiveFunctionDisclosureEngine()
        self.ui_elements: Dict[str, QWidget] = {}
        self.disclosure_animations: Dict[str, QPropertyAnimation] = {}

        logger.info("渐进式披露UI管理器初始化完成")

    def register_ui_element(self, function_id: str, widget: QWidget):
        """注册UI元素"""
        self.ui_elements[function_id] = widget

        # 初始设置可见性
        should_show = self.disclosure_engine.should_disclose_function(function_id)
        widget.setVisible(should_show)

        logger.debug(f"注册UI元素: {function_id}, 可见: {should_show}")

    def update_ui_disclosure(self):
        """更新UI披露状态"""
        try:
            disclosed_functions = self.disclosure_engine.get_disclosed_functions()
            disclosed_ids = {f.function_id for f in disclosed_functions}

            for function_id, widget in self.ui_elements.items():
                should_show = function_id in disclosed_ids
                current_visible = widget.isVisible()

                if should_show != current_visible:
                    if should_show:
                        self.animate_show_element(function_id, widget)
                    else:
                        self.animate_hide_element(function_id, widget)

            self.disclosure_changed.emit()
            logger.debug("UI披露状态已更新")

        except Exception as e:
            logger.error(f"更新UI披露状态失败: {e}")

    def animate_show_element(self, function_id: str, widget: QWidget):
        """动画显示元素"""
        try:
            # 停止现有动画
            if function_id in self.disclosure_animations:
                self.disclosure_animations[function_id].stop()

            # 设置初始状态
            widget.setVisible(True)
            widget.setMaximumHeight(0)

            # 创建动画
            animation = QPropertyAnimation(widget, b"maximumHeight")
            animation.setDuration(300)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            animation.setStartValue(0)
            animation.setEndValue(widget.sizeHint().height())

            # 动画完成后恢复正常高度
            animation.finished.connect(lambda: widget.setMaximumHeight(16777215))

            # 启动动画
            animation.start()
            self.disclosure_animations[function_id] = animation

            logger.debug(f"动画显示元素: {function_id}")

        except Exception as e:
            logger.error(f"动画显示元素失败 {function_id}: {e}")
            widget.setVisible(True)

    def animate_hide_element(self, function_id: str, widget: QWidget):
        """动画隐藏元素"""
        try:
            # 停止现有动画
            if function_id in self.disclosure_animations:
                self.disclosure_animations[function_id].stop()

            # 创建动画
            animation = QPropertyAnimation(widget, b"maximumHeight")
            animation.setDuration(200)
            animation.setEasingCurve(QEasingCurve.Type.InCubic)
            animation.setStartValue(widget.height())
            animation.setEndValue(0)

            # 动画完成后隐藏元素
            animation.finished.connect(lambda: widget.setVisible(False))

            # 启动动画
            animation.start()
            self.disclosure_animations[function_id] = animation

            logger.debug(f"动画隐藏元素: {function_id}")

        except Exception as e:
            logger.error(f"动画隐藏元素失败 {function_id}: {e}")
            widget.setVisible(False)

    def request_function_disclosure(self, function_id: str):
        """请求功能披露"""
        self.disclosure_engine.request_function_disclosure(function_id)
        self.update_ui_disclosure()
        self.function_requested.emit(function_id)

        logger.info(f"请求功能披露: {function_id}")

    def record_function_usage(self, function_id: str, duration: float = 0.0, success: bool = True):
        """记录功能使用"""
        self.disclosure_engine.record_function_usage(function_id, duration, success)

        # 延迟更新UI以避免频繁更新
        QTimer.singleShot(1000, self.update_ui_disclosure)

    def set_user_level(self, level: UserExpertiseLevel):
        """设置用户专业水平"""
        self.disclosure_engine.set_user_level(level)
        self.update_ui_disclosure()

    def set_workflow_stage(self, stage: WorkflowStage):
        """设置工作流程阶段"""
        self.disclosure_engine.set_workflow_stage(stage)
        self.update_ui_disclosure()

    def create_disclosure_control_panel(self) -> QWidget:
        """创建披露控制面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(panel)

        # 标题
        title = QLabel("功能披露控制")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #495057; margin-bottom: 10px;")
        layout.addWidget(title)

        # 用户级别选择
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("用户级别:"))

        level_combo = QComboBox()
        level_combo.addItems([
            "初学者", "中级用户", "高级用户", "专家用户"
        ])
        level_combo.setCurrentIndex(1)  # 默认中级用户
        level_combo.currentIndexChanged.connect(self.on_level_changed)
        level_layout.addWidget(level_combo)

        layout.addLayout(level_layout)

        # 学习模式开关
        learning_checkbox = QCheckBox("启用智能学习")
        learning_checkbox.setChecked(self.disclosure_engine.learning_enabled)
        learning_checkbox.toggled.connect(self.on_learning_toggled)
        layout.addWidget(learning_checkbox)

        # 披露统计
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #6c757d; font-size: 10px; margin-top: 10px;")
        layout.addWidget(self.stats_label)

        # 更新统计
        self.update_stats_display()

        return panel

    def on_level_changed(self, index: int):
        """用户级别改变处理"""
        levels = [
            UserExpertiseLevel.BEGINNER,
            UserExpertiseLevel.INTERMEDIATE,
            UserExpertiseLevel.ADVANCED,
            UserExpertiseLevel.EXPERT
        ]

        if 0 <= index < len(levels):
            self.set_user_level(levels[index])
            self.update_stats_display()

    def on_learning_toggled(self, enabled: bool):
        """学习模式切换处理"""
        self.disclosure_engine.learning_enabled = enabled
        logger.info(f"智能学习模式: {'启用' if enabled else '禁用'}")

    def update_stats_display(self):
        """更新统计显示"""
        try:
            summary = self.disclosure_engine.get_disclosure_summary()

            stats_text = (
                f"可见功能: {summary['disclosed_functions']}/{summary['total_functions']} "
                f"({summary['disclosure_rate']:.1%})\n"
                f"用户级别: {summary['user_level']}\n"
                f"工作流程: {summary['workflow_stage']}"
            )

            self.stats_label.setText(stats_text)

        except Exception as e:
            logger.error(f"更新统计显示失败: {e}")

    def create_function_discovery_widget(self) -> QWidget:
        """创建功能发现组件"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        widget.setStyleSheet("""
            QFrame {
                background-color: #e3f2fd;
                border: 1px solid #2196f3;
                border-radius: 6px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(widget)

        # 标题
        title = QLabel("💡 发现新功能")
        title.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2; margin-bottom: 8px;")
        layout.addWidget(title)

        # 描述
        desc = QLabel("基于您的使用情况，我们为您推荐以下功能：")
        desc.setStyleSheet("color: #424242; margin-bottom: 10px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # 推荐功能列表
        self.recommendations_layout = QVBoxLayout()
        layout.addLayout(self.recommendations_layout)

        # 更新推荐
        self.update_recommendations()

        return widget

    def update_recommendations(self):
        """更新功能推荐"""
        try:
            # 清空现有推荐
            while self.recommendations_layout.count():
                child = self.recommendations_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # 获取可以披露但尚未披露的功能
            all_functions = self.disclosure_engine.functions_metadata.values()
            disclosed_ids = {f.function_id for f in self.disclosure_engine.get_disclosed_functions()}

            recommendations = []
            for func in all_functions:
                if func.function_id not in disclosed_ids:
                    if self.disclosure_engine._meets_expertise_requirement(func):
                        if self.disclosure_engine._dependencies_satisfied(func):
                            recommendations.append(func)

            # 按优先级排序，取前3个
            recommendations.sort(key=lambda f: f.priority, reverse=True)
            recommendations = recommendations[:3]

            if not recommendations:
                no_rec_label = QLabel("暂无新功能推荐")
                no_rec_label.setStyleSheet("color: #757575; font-style: italic;")
                self.recommendations_layout.addWidget(no_rec_label)
                return

            # 创建推荐项
            for func in recommendations:
                rec_widget = self.create_recommendation_item(func)
                self.recommendations_layout.addWidget(rec_widget)

        except Exception as e:
            logger.error(f"更新功能推荐失败: {e}")

    def create_recommendation_item(self, func: FunctionMetadata) -> QWidget:
        """创建推荐项"""
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                margin: 2px 0;
            }
            QFrame:hover {
                border-color: #2196f3;
                background-color: #f5f5f5;
            }
        """)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(8, 6, 8, 6)

        # 图标
        icon_label = QLabel(func.icon)
        icon_label.setFixedSize(20, 20)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # 信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_label = QLabel(func.name)
        name_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #333333;")
        info_layout.addWidget(name_label)

        desc_label = QLabel(func.description)
        desc_label.setFont(QFont("Microsoft YaHei", 8))
        desc_label.setStyleSheet("color: #666666;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        # 尝试按钮
        try_btn = QPushButton("尝试")
        try_btn.setFixedSize(50, 24)
        try_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 8px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        try_btn.clicked.connect(lambda: self.request_function_disclosure(func.function_id))
        layout.addWidget(try_btn)

        return item

    def get_disclosure_engine(self) -> ProgressiveFunctionDisclosureEngine:
        """获取披露引擎"""
        return self.disclosure_engine

    def export_disclosure_state(self, file_path: str):
        """导出披露状态"""
        try:
            state = self.disclosure_engine.export_disclosure_state()

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)

            logger.info(f"披露状态已导出到: {file_path}")

        except Exception as e:
            logger.error(f"导出披露状态失败: {e}")

    def import_disclosure_state(self, file_path: str):
        """导入披露状态"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                state = json.load(f)

            self.disclosure_engine.import_disclosure_state(state)
            self.update_ui_disclosure()
            self.update_stats_display()

            logger.info(f"披露状态已从文件导入: {file_path}")

        except Exception as e:
            logger.error(f"导入披露状态失败: {e}")


class ProgressiveDisclosureIntegrator:
    """渐进式功能披露集成器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.ui_manager = ProgressiveDisclosureUIManager(main_window)
        self.function_widgets: Dict[str, QWidget] = {}
        self.toolbar_actions: Dict[str, QAction] = {}
        self.menu_actions: Dict[str, QAction] = {}

        # 连接信号
        self.ui_manager.function_requested.connect(self.handle_function_request)
        self.ui_manager.disclosure_changed.connect(self.handle_disclosure_change)

        logger.info("渐进式功能披露集成器初始化完成")

    def integrate_progressive_disclosure(self):
        """集成渐进式功能披露系统"""
        try:
            # 集成到各个UI组件
            self.integrate_toolbar_disclosure()
            self.integrate_menu_disclosure()
            self.integrate_panel_disclosure()
            self.integrate_widget_disclosure()

            # 设置初始披露状态
            self.ui_manager.update_ui_disclosure()

            # 添加披露控制面板
            self.add_disclosure_control_panel()

            logger.info("渐进式功能披露系统集成完成")
            return True

        except Exception as e:
            logger.error(f"渐进式功能披露系统集成失败: {e}")
            return False

    def integrate_toolbar_disclosure(self):
        """集成工具栏披露"""
        try:
            if hasattr(self.main_window, 'toolbar'):
                toolbar = self.main_window.toolbar

                # 为工具栏动作注册披露控制
                for action in toolbar.actions():
                    action_id = action.data() if action.data() else action.text().replace('&', '')

                    # 映射到功能ID
                    function_id = self.map_action_to_function(action_id)
                    if function_id:
                        self.toolbar_actions[function_id] = action
                        self.ui_manager.register_ui_element(function_id, action)

                logger.debug("工具栏披露集成完成")

        except Exception as e:
            logger.error(f"工具栏披露集成失败: {e}")

    def integrate_menu_disclosure(self):
        """集成菜单披露"""
        try:
            if hasattr(self.main_window, 'menuBar'):
                menubar = self.main_window.menuBar()

                # 遍历所有菜单和动作
                for menu in menubar.findChildren(QMenuBar):
                    for action in menu.actions():
                        if action.menu():
                            # 子菜单
                            self.process_submenu_actions(action.menu())
                        else:
                            # 普通动作
                            action_id = action.data() if action.data() else action.text().replace('&', '')
                            function_id = self.map_action_to_function(action_id)
                            if function_id:
                                self.menu_actions[function_id] = action
                                self.ui_manager.register_ui_element(function_id, action)

                logger.debug("菜单披露集成完成")

        except Exception as e:
            logger.error(f"菜单披露集成失败: {e}")

    def process_submenu_actions(self, menu):
        """处理子菜单动作"""
        for action in menu.actions():
            if action.menu():
                self.process_submenu_actions(action.menu())
            else:
                action_id = action.data() if action.data() else action.text().replace('&', '')
                function_id = self.map_action_to_function(action_id)
                if function_id:
                    self.menu_actions[function_id] = action
                    self.ui_manager.register_ui_element(function_id, action)

    def integrate_panel_disclosure(self):
        """集成面板披露"""
        try:
            # 音频面板
            if hasattr(self.main_window, 'audio_widget'):
                self.register_panel_functions('audio_widget', [
                    'audio_import', 'audio_advanced'
                ])

            # 时间段面板
            if hasattr(self.main_window, 'timeline_widget'):
                self.register_panel_functions('timeline_widget', [
                    'time_segment_basic', 'time_segment_advanced'
                ])

            # 描述面板
            if hasattr(self.main_window, 'description_widget'):
                self.register_panel_functions('description_widget', [
                    'simple_description', 'ai_generate_basic', 'ai_generate_advanced'
                ])

            # 预览面板
            if hasattr(self.main_window, 'preview_widget'):
                self.register_panel_functions('preview_widget', [
                    'preview_basic', 'preview_advanced'
                ])

            # 元素编辑面板
            if hasattr(self.main_window, 'elements_widget'):
                self.register_panel_functions('elements_widget', [
                    'element_editing'
                ])

            # 导出面板
            if hasattr(self.main_window, 'export_widget'):
                self.register_panel_functions('export_widget', [
                    'export_basic'
                ])

            logger.debug("面板披露集成完成")

        except Exception as e:
            logger.error(f"面板披露集成失败: {e}")

    def register_panel_functions(self, panel_name: str, function_ids: List[str]):
        """注册面板功能"""
        try:
            panel = getattr(self.main_window, panel_name, None)
            if panel:
                for function_id in function_ids:
                    self.ui_manager.register_ui_element(function_id, panel)
                    self.function_widgets[function_id] = panel

        except Exception as e:
            logger.error(f"注册面板功能失败 {panel_name}: {e}")

    def integrate_widget_disclosure(self):
        """集成组件披露"""
        try:
            # 高级功能组件
            advanced_widgets = [
                ('custom_rules', 'rule_editor_widget'),
                ('script_editing', 'code_editor_widget'),
                ('performance_monitoring', 'performance_widget'),
                ('batch_operations', 'batch_widget'),
                ('developer_tools', 'developer_widget')
            ]

            for function_id, widget_name in advanced_widgets:
                if hasattr(self.main_window, widget_name):
                    widget = getattr(self.main_window, widget_name)
                    self.ui_manager.register_ui_element(function_id, widget)
                    self.function_widgets[function_id] = widget

            logger.debug("组件披露集成完成")

        except Exception as e:
            logger.error(f"组件披露集成失败: {e}")

    def map_action_to_function(self, action_id: str) -> Optional[str]:
        """映射动作到功能ID"""
        action_mapping = {
            # 基础功能映射
            "导入音频": "audio_import",
            "Import Audio": "audio_import",
            "添加时间段": "time_segment_basic",
            "Add Time Segment": "time_segment_basic",
            "动画描述": "simple_description",
            "Animation Description": "simple_description",
            "AI生成": "ai_generate_basic",
            "AI Generate": "ai_generate_basic",
            "预览": "preview_basic",
            "Preview": "preview_basic",

            # 高级功能映射
            "高级音频": "audio_advanced",
            "Advanced Audio": "audio_advanced",
            "精确时间段": "time_segment_advanced",
            "Precise Time Segment": "time_segment_advanced",
            "元素编辑": "element_editing",
            "Element Editing": "element_editing",
            "高级AI": "ai_generate_advanced",
            "Advanced AI": "ai_generate_advanced",
            "高级预览": "preview_advanced",
            "Advanced Preview": "preview_advanced",
            "导出": "export_basic",
            "Export": "export_basic",

            # 专家功能映射
            "自定义规则": "custom_rules",
            "Custom Rules": "custom_rules",
            "脚本编辑": "script_editing",
            "Script Editing": "script_editing",
            "性能监控": "performance_monitoring",
            "Performance Monitor": "performance_monitoring",
            "批量操作": "batch_operations",
            "Batch Operations": "batch_operations",
            "开发者工具": "developer_tools",
            "Developer Tools": "developer_tools"
        }

        return action_mapping.get(action_id)

    def add_disclosure_control_panel(self):
        """添加披露控制面板"""
        try:
            # 创建控制面板
            control_panel = self.ui_manager.create_disclosure_control_panel()

            # 创建功能发现组件
            discovery_widget = self.ui_manager.create_function_discovery_widget()

            # 添加到主窗口
            if hasattr(self.main_window, 'add_dock_widget'):
                # 如果有dock系统，添加为dock widget
                self.main_window.add_dock_widget("功能披露控制", control_panel, Qt.DockWidgetArea.RightDockWidgetArea)
                self.main_window.add_dock_widget("功能发现", discovery_widget, Qt.DockWidgetArea.RightDockWidgetArea)
            else:
                # 否则添加到状态栏或其他位置
                if hasattr(self.main_window, 'statusBar'):
                    status_bar = self.main_window.statusBar()
                    status_bar.addPermanentWidget(control_panel)

            logger.debug("披露控制面板已添加")

        except Exception as e:
            logger.error(f"添加披露控制面板失败: {e}")

    def handle_function_request(self, function_id: str):
        """处理功能请求"""
        try:
            # 记录用户主动请求功能
            self.ui_manager.record_function_usage(function_id, 0.0, True)

            # 如果有对应的动作，触发它
            if function_id in self.toolbar_actions:
                self.toolbar_actions[function_id].trigger()
            elif function_id in self.menu_actions:
                self.menu_actions[function_id].trigger()

            logger.info(f"处理功能请求: {function_id}")

        except Exception as e:
            logger.error(f"处理功能请求失败 {function_id}: {e}")

    def handle_disclosure_change(self):
        """处理披露状态改变"""
        try:
            # 更新推荐
            self.ui_manager.update_recommendations()

            # 更新统计显示
            self.ui_manager.update_stats_display()

            logger.debug("披露状态改变处理完成")

        except Exception as e:
            logger.error(f"处理披露状态改变失败: {e}")

    def track_function_usage(self, function_id: str, start_time: datetime, success: bool = True):
        """跟踪功能使用"""
        try:
            duration = (datetime.now() - start_time).total_seconds()
            self.ui_manager.record_function_usage(function_id, duration, success)

        except Exception as e:
            logger.error(f"跟踪功能使用失败 {function_id}: {e}")

    def set_user_expertise_level(self, level: UserExpertiseLevel):
        """设置用户专业水平"""
        self.ui_manager.set_user_level(level)
        logger.info(f"用户专业水平设置为: {level.value}")

    def set_workflow_stage(self, stage: WorkflowStage):
        """设置工作流程阶段"""
        self.ui_manager.set_workflow_stage(stage)
        logger.info(f"工作流程阶段设置为: {stage.value}")

    def get_ui_manager(self) -> ProgressiveDisclosureUIManager:
        """获取UI管理器"""
        return self.ui_manager

    def get_disclosure_engine(self) -> ProgressiveFunctionDisclosureEngine:
        """获取披露引擎"""
        return self.ui_manager.get_disclosure_engine()

    def export_configuration(self, file_path: str):
        """导出配置"""
        try:
            config = {
                "integration_summary": self.get_integration_summary(),
                "disclosure_state": self.ui_manager.get_disclosure_engine().export_disclosure_state()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            logger.info(f"渐进式披露配置已导出到: {file_path}")

        except Exception as e:
            logger.error(f"导出配置失败: {e}")

    def get_integration_summary(self) -> Dict[str, Any]:
        """获取集成摘要"""
        engine = self.ui_manager.get_disclosure_engine()
        summary = engine.get_disclosure_summary()

        return {
            "total_functions": summary["total_functions"],
            "disclosed_functions": summary["disclosed_functions"],
            "disclosure_rate": summary["disclosure_rate"],
            "user_level": summary["user_level"],
            "workflow_stage": summary["workflow_stage"],
            "registered_widgets": len(self.function_widgets),
            "toolbar_actions": len(self.toolbar_actions),
            "menu_actions": len(self.menu_actions),
            "learning_enabled": summary["learning_enabled"],
            "integration_status": "completed"
        }
