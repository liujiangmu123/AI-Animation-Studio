"""
AI Animation Studio - 价值层次配置
定义清晰的功能优先级体系和设计价值层次
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
from core.logger import get_logger

logger = get_logger("value_hierarchy_config")


class PriorityLevel(Enum):
    """优先级级别"""
    CORE = 1        # 核心功能 - 必须立即可见
    PRIMARY = 2     # 主要功能 - 默认可见
    SECONDARY = 3   # 次要功能 - 可折叠
    ADVANCED = 4    # 高级功能 - 专家模式


class UserExpertiseLevel(Enum):
    """用户专业水平"""
    BEGINNER = "beginner"       # 初学者
    INTERMEDIATE = "intermediate"  # 中级用户
    ADVANCED = "advanced"       # 高级用户
    EXPERT = "expert"          # 专家用户


class WorkflowStage(Enum):
    """工作流程阶段"""
    AUDIO_IMPORT = 1      # 音频导入
    TIME_MARKING = 2      # 时间段标记
    DESCRIPTION = 3       # 动画描述
    AI_GENERATION = 4     # AI生成
    PREVIEW_ADJUST = 5    # 预览调整
    EXPORT = 6           # 导出完成


@dataclass
class FeatureConfig:
    """功能配置"""
    name: str
    priority: PriorityLevel
    workflow_stage: Optional[WorkflowStage]
    min_expertise: UserExpertiseLevel
    description: str
    icon: str
    shortcut: Optional[str] = None
    tooltip: str = ""
    category: str = ""


class ValueHierarchyConfig:
    """价值层次配置管理器"""
    
    def __init__(self):
        self.features = self._initialize_features()
        self.current_expertise = UserExpertiseLevel.INTERMEDIATE
        self.current_workflow_stage = WorkflowStage.AUDIO_IMPORT
        logger.info("价值层次配置初始化完成")
    
    def _initialize_features(self) -> Dict[str, FeatureConfig]:
        """初始化功能配置"""
        features = {}
        
        # 核心功能 (优先级1) - 始终可见
        core_features = [
            FeatureConfig(
                name="audio_import",
                priority=PriorityLevel.CORE,
                workflow_stage=WorkflowStage.AUDIO_IMPORT,
                min_expertise=UserExpertiseLevel.BEGINNER,
                description="导入旁白音频文件",
                icon="🎵",
                shortcut="Ctrl+O",
                tooltip="导入音频文件作为动画制作的基础",
                category="媒体管理"
            ),
            FeatureConfig(
                name="time_marking",
                priority=PriorityLevel.CORE,
                workflow_stage=WorkflowStage.TIME_MARKING,
                min_expertise=UserExpertiseLevel.BEGINNER,
                description="标记关键时间点",
                icon="📍",
                shortcut="Ctrl+M",
                tooltip="在音频时间轴上标记关键动画节点",
                category="时间轴控制"
            ),
            FeatureConfig(
                name="ai_generation",
                priority=PriorityLevel.CORE,
                workflow_stage=WorkflowStage.AI_GENERATION,
                min_expertise=UserExpertiseLevel.BEGINNER,
                description="AI动画生成",
                icon="🤖",
                shortcut="Ctrl+G",
                tooltip="使用AI生成动画内容",
                category="AI功能"
            ),
            FeatureConfig(
                name="preview",
                priority=PriorityLevel.CORE,
                workflow_stage=WorkflowStage.PREVIEW_ADJUST,
                min_expertise=UserExpertiseLevel.BEGINNER,
                description="实时预览",
                icon="👁️",
                shortcut="Space",
                tooltip="预览动画效果",
                category="预览控制"
            ),
            FeatureConfig(
                name="export",
                priority=PriorityLevel.CORE,
                workflow_stage=WorkflowStage.EXPORT,
                min_expertise=UserExpertiseLevel.BEGINNER,
                description="导出作品",
                icon="📤",
                shortcut="Ctrl+E",
                tooltip="导出最终动画作品",
                category="输出管理"
            )
        ]
        
        # 主要功能 (优先级2) - 默认可见
        primary_features = [
            FeatureConfig(
                name="stage_editing",
                priority=PriorityLevel.PRIMARY,
                workflow_stage=None,
                min_expertise=UserExpertiseLevel.BEGINNER,
                description="舞台编辑",
                icon="🎨",
                tooltip="编辑动画舞台和元素",
                category="编辑工具"
            ),
            FeatureConfig(
                name="element_management",
                priority=PriorityLevel.PRIMARY,
                workflow_stage=None,
                min_expertise=UserExpertiseLevel.BEGINNER,
                description="元素管理",
                icon="📁",
                tooltip="管理动画元素",
                category="资源管理"
            ),
            FeatureConfig(
                name="properties_panel",
                priority=PriorityLevel.PRIMARY,
                workflow_stage=None,
                min_expertise=UserExpertiseLevel.INTERMEDIATE,
                description="属性面板",
                icon="📐",
                tooltip="编辑元素属性",
                category="编辑工具"
            ),
            FeatureConfig(
                name="undo_redo",
                priority=PriorityLevel.PRIMARY,
                workflow_stage=None,
                min_expertise=UserExpertiseLevel.BEGINNER,
                description="撤销重做",
                icon="↶",
                shortcut="Ctrl+Z",
                tooltip="撤销或重做操作",
                category="编辑工具"
            )
        ]
        
        # 次要功能 (优先级3) - 可折叠
        secondary_features = [
            FeatureConfig(
                name="template_library",
                priority=PriorityLevel.SECONDARY,
                workflow_stage=None,
                min_expertise=UserExpertiseLevel.INTERMEDIATE,
                description="模板库",
                icon="📚",
                tooltip="使用预设模板",
                category="资源管理"
            ),
            FeatureConfig(
                name="asset_library",
                priority=PriorityLevel.SECONDARY,
                workflow_stage=None,
                min_expertise=UserExpertiseLevel.INTERMEDIATE,
                description="素材库",
                icon="🎨",
                tooltip="管理素材资源",
                category="资源管理"
            ),
            FeatureConfig(
                name="rules_manager",
                priority=PriorityLevel.SECONDARY,
                workflow_stage=None,
                min_expertise=UserExpertiseLevel.ADVANCED,
                description="规则管理",
                icon="📋",
                tooltip="管理动画规则",
                category="高级工具"
            ),
            FeatureConfig(
                name="collaboration",
                priority=PriorityLevel.SECONDARY,
                workflow_stage=None,
                min_expertise=UserExpertiseLevel.INTERMEDIATE,
                description="协作功能",
                icon="👥",
                tooltip="团队协作工具",
                category="协作工具"
            )
        ]
        
        # 高级功能 (优先级4) - 专家模式
        advanced_features = [
            FeatureConfig(
                name="debug_console",
                priority=PriorityLevel.ADVANCED,
                workflow_stage=None,
                min_expertise=UserExpertiseLevel.EXPERT,
                description="调试控制台",
                icon="🔍",
                tooltip="开发调试工具",
                category="开发工具"
            ),
            FeatureConfig(
                name="performance_monitor",
                priority=PriorityLevel.ADVANCED,
                workflow_stage=None,
                min_expertise=UserExpertiseLevel.EXPERT,
                description="性能监控",
                icon="📈",
                tooltip="监控系统性能",
                category="开发工具"
            ),
            FeatureConfig(
                name="api_integration",
                priority=PriorityLevel.ADVANCED,
                workflow_stage=None,
                min_expertise=UserExpertiseLevel.EXPERT,
                description="API集成",
                icon="🔌",
                tooltip="第三方API集成",
                category="开发工具"
            ),
            FeatureConfig(
                name="custom_scripting",
                priority=PriorityLevel.ADVANCED,
                workflow_stage=None,
                min_expertise=UserExpertiseLevel.EXPERT,
                description="自定义脚本",
                icon="📝",
                tooltip="编写自定义脚本",
                category="开发工具"
            )
        ]
        
        # 合并所有功能
        all_features = core_features + primary_features + secondary_features + advanced_features
        
        for feature in all_features:
            features[feature.name] = feature
        
        return features
    
    def get_visible_features(self, expertise_level: Optional[UserExpertiseLevel] = None,
                           workflow_stage: Optional[WorkflowStage] = None) -> List[FeatureConfig]:
        """获取当前应该可见的功能"""
        if expertise_level is None:
            expertise_level = self.current_expertise
        if workflow_stage is None:
            workflow_stage = self.current_workflow_stage
        
        visible_features = []
        
        for feature in self.features.values():
            # 检查专业水平要求
            if self._meets_expertise_requirement(feature, expertise_level):
                # 检查工作流程相关性
                if self._is_workflow_relevant(feature, workflow_stage):
                    visible_features.append(feature)
        
        # 按优先级排序
        visible_features.sort(key=lambda f: f.priority.value)
        
        return visible_features
    
    def get_features_by_priority(self, priority: PriorityLevel) -> List[FeatureConfig]:
        """获取指定优先级的功能"""
        return [f for f in self.features.values() if f.priority == priority]
    
    def get_features_by_category(self, category: str) -> List[FeatureConfig]:
        """获取指定分类的功能"""
        return [f for f in self.features.values() if f.category == category]
    
    def get_workflow_features(self, stage: WorkflowStage) -> List[FeatureConfig]:
        """获取指定工作流程阶段的功能"""
        return [f for f in self.features.values() if f.workflow_stage == stage]
    
    def set_expertise_level(self, level: UserExpertiseLevel):
        """设置用户专业水平"""
        self.current_expertise = level
        logger.info(f"用户专业水平设置为: {level.value}")
    
    def set_workflow_stage(self, stage: WorkflowStage):
        """设置当前工作流程阶段"""
        self.current_workflow_stage = stage
        logger.info(f"工作流程阶段设置为: {stage.name}")
    
    def _meets_expertise_requirement(self, feature: FeatureConfig, 
                                   user_level: UserExpertiseLevel) -> bool:
        """检查是否满足专业水平要求"""
        expertise_order = {
            UserExpertiseLevel.BEGINNER: 1,
            UserExpertiseLevel.INTERMEDIATE: 2,
            UserExpertiseLevel.ADVANCED: 3,
            UserExpertiseLevel.EXPERT: 4
        }
        
        return expertise_order[user_level] >= expertise_order[feature.min_expertise]
    
    def _is_workflow_relevant(self, feature: FeatureConfig, 
                            current_stage: WorkflowStage) -> bool:
        """检查功能是否与当前工作流程阶段相关"""
        # 核心功能始终相关
        if feature.priority == PriorityLevel.CORE:
            return True
        
        # 没有特定工作流程阶段的功能始终相关
        if feature.workflow_stage is None:
            return True
        
        # 检查是否为当前阶段或相邻阶段的功能
        if feature.workflow_stage == current_stage:
            return True
        
        # 相邻阶段的功能也显示（提前准备或回顾）
        stage_values = [stage.value for stage in WorkflowStage]
        current_index = stage_values.index(current_stage.value)
        feature_index = stage_values.index(feature.workflow_stage.value)
        
        # 显示前一个和后一个阶段的功能
        return abs(current_index - feature_index) <= 1
    
    def get_priority_summary(self) -> Dict[str, int]:
        """获取优先级统计摘要"""
        summary = {}
        for priority in PriorityLevel:
            count = len(self.get_features_by_priority(priority))
            summary[priority.name] = count
        
        return summary
    
    def export_config(self) -> Dict:
        """导出配置"""
        return {
            "current_expertise": self.current_expertise.value,
            "current_workflow_stage": self.current_workflow_stage.value,
            "features": {
                name: {
                    "priority": feature.priority.value,
                    "workflow_stage": feature.workflow_stage.value if feature.workflow_stage else None,
                    "min_expertise": feature.min_expertise.value,
                    "category": feature.category
                }
                for name, feature in self.features.items()
            }
        }


# 全局配置实例
value_hierarchy = ValueHierarchyConfig()


def get_value_hierarchy() -> ValueHierarchyConfig:
    """获取价值层次配置实例"""
    return value_hierarchy
