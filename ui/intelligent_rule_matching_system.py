"""
AI Animation Studio - 智能规则匹配系统
实现AI自动选择最适合的动画技术和规则
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

logger = get_logger("intelligent_rule_matching_system")


class RuleCategory(Enum):
    """规则类别枚举"""
    EMOTION = "emotion"         # 情感类规则
    PHYSICS = "physics"         # 物理类规则
    MOTION = "motion"           # 运动类规则
    VISUAL = "visual"           # 视觉类规则
    TIMING = "timing"           # 时间类规则
    INTERACTION = "interaction" # 交互类规则
    PERFORMANCE = "performance" # 性能类规则
    STYLE = "style"            # 样式类规则


class MatchingStrategy(Enum):
    """匹配策略枚举"""
    SEMANTIC_SIMILARITY = "semantic_similarity"    # 语义相似度
    KEYWORD_MATCHING = "keyword_matching"          # 关键词匹配
    CONTEXT_AWARE = "context_aware"                # 上下文感知
    LEARNING_BASED = "learning_based"              # 学习基础
    HYBRID = "hybrid"                              # 混合策略


class RuleComplexity(Enum):
    """规则复杂度枚举"""
    SIMPLE = 1      # 简单
    MEDIUM = 2      # 中等
    COMPLEX = 3     # 复杂
    ADVANCED = 4    # 高级


@dataclass
class AnimationRule:
    """动画规则数据类"""
    rule_id: str
    name: str
    category: RuleCategory
    description: str
    keywords: List[str]
    tech_stacks: List[TechStack]
    complexity: RuleComplexity
    css_template: str = ""
    js_template: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    usage_count: int = 0
    success_rate: float = 0.0
    user_rating: float = 0.0
    created_time: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class RuleMatch:
    """规则匹配结果"""
    rule: AnimationRule
    confidence: float
    matching_reasons: List[str]
    weight: float
    tech_stack_compatibility: float
    context_relevance: float
    user_preference_score: float
    performance_impact: float
    estimated_quality: float


@dataclass
class MatchingContext:
    """匹配上下文"""
    description: str
    project_type: str = "general"
    target_audience: str = "general"
    performance_requirements: str = "balanced"
    preferred_tech_stacks: List[TechStack] = field(default_factory=list)
    existing_elements: List[str] = field(default_factory=list)
    timeline_constraints: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    historical_choices: List[str] = field(default_factory=list)


class SemanticMatcher:
    """语义匹配器"""
    
    def __init__(self):
        self.semantic_vectors = {}
        self.keyword_weights = {}
        self.context_patterns = {}
        
        self.initialize_semantic_data()
        logger.info("语义匹配器初始化完成")
    
    def initialize_semantic_data(self):
        """初始化语义数据"""
        # 情感类关键词权重
        self.keyword_weights[RuleCategory.EMOTION] = {
            "稳定": 0.9, "动态": 0.9, "科技": 0.8, "亲和": 0.8,
            "现代": 0.7, "优雅": 0.7, "活力": 0.8, "温暖": 0.7,
            "冷酷": 0.6, "神秘": 0.6, "明亮": 0.7, "沉稳": 0.8
        }
        
        # 物理类关键词权重
        self.keyword_weights[RuleCategory.PHYSICS] = {
            "弹性": 0.9, "重力": 0.9, "惯性": 0.8, "摩擦": 0.7,
            "碰撞": 0.8, "反弹": 0.8, "流体": 0.7, "磁力": 0.6,
            "振动": 0.7, "波动": 0.7, "扭曲": 0.6, "拉伸": 0.6
        }
        
        # 运动类关键词权重
        self.keyword_weights[RuleCategory.MOTION] = {
            "移动": 0.9, "旋转": 0.9, "缩放": 0.8, "跳跃": 0.8,
            "滑动": 0.8, "飞行": 0.8, "弹跳": 0.8, "摇摆": 0.7,
            "螺旋": 0.7, "波浪": 0.7, "直线": 0.6, "曲线": 0.7
        }
        
        # 视觉类关键词权重
        self.keyword_weights[RuleCategory.VISUAL] = {
            "发光": 0.9, "阴影": 0.8, "渐变": 0.8, "透明": 0.8,
            "模糊": 0.7, "锐化": 0.6, "色彩": 0.8, "纹理": 0.7,
            "反射": 0.7, "折射": 0.6, "粒子": 0.8, "拖尾": 0.8
        }
        
        # 时间类关键词权重
        self.keyword_weights[RuleCategory.TIMING] = {
            "快速": 0.9, "缓慢": 0.9, "瞬间": 0.8, "持续": 0.8,
            "延迟": 0.8, "同步": 0.8, "异步": 0.7, "循环": 0.8,
            "节拍": 0.7, "韵律": 0.7, "间歇": 0.6, "连续": 0.7
        }
    
    def find_matching_rules(self, description: str, available_rules: List[AnimationRule],
                           context: MatchingContext) -> List[RuleMatch]:
        """查找匹配的规则"""
        try:
            matches = []
            description_lower = description.lower()
            
            for rule in available_rules:
                # 计算各种匹配分数
                keyword_score = self.calculate_keyword_score(description_lower, rule)
                semantic_score = self.calculate_semantic_score(description, rule)
                context_score = self.calculate_context_score(context, rule)
                tech_compatibility = self.calculate_tech_compatibility(context, rule)
                
                # 综合置信度
                confidence = (keyword_score * 0.3 + semantic_score * 0.3 + 
                            context_score * 0.2 + tech_compatibility * 0.2)
                
                if confidence > 0.3:  # 置信度阈值
                    matching_reasons = self.generate_matching_reasons(
                        description_lower, rule, keyword_score, semantic_score, context_score
                    )
                    
                    match = RuleMatch(
                        rule=rule,
                        confidence=confidence,
                        matching_reasons=matching_reasons,
                        weight=confidence,
                        tech_stack_compatibility=tech_compatibility,
                        context_relevance=context_score,
                        user_preference_score=0.5,  # 待实现用户偏好
                        performance_impact=self.estimate_performance_impact(rule),
                        estimated_quality=self.estimate_quality(rule, confidence)
                    )
                    matches.append(match)
            
            # 按置信度排序
            matches.sort(key=lambda m: m.confidence, reverse=True)
            return matches
            
        except Exception as e:
            logger.error(f"查找匹配规则失败: {e}")
            return []
    
    def calculate_keyword_score(self, description: str, rule: AnimationRule) -> float:
        """计算关键词匹配分数"""
        try:
            score = 0.0
            total_weight = 0.0
            
            # 检查规则关键词
            for keyword in rule.keywords:
                if keyword.lower() in description:
                    weight = self.keyword_weights.get(rule.category, {}).get(keyword, 0.5)
                    score += weight
                    total_weight += weight
            
            # 检查规则名称
            if rule.name.lower() in description:
                score += 0.8
                total_weight += 0.8
            
            # 检查标签
            for tag in rule.tags:
                if tag.lower() in description:
                    score += 0.3
                    total_weight += 0.3
            
            return score / max(total_weight, 1.0) if total_weight > 0 else 0.0
            
        except Exception as e:
            logger.error(f"计算关键词分数失败: {e}")
            return 0.0
    
    def calculate_semantic_score(self, description: str, rule: AnimationRule) -> float:
        """计算语义相似度分数"""
        try:
            # 简化的语义相似度计算
            # 在实际应用中可以使用更复杂的NLP模型
            
            desc_words = set(description.lower().split())
            rule_words = set((rule.name + " " + rule.description + " " + " ".join(rule.keywords)).lower().split())
            
            # 计算Jaccard相似度
            intersection = len(desc_words.intersection(rule_words))
            union = len(desc_words.union(rule_words))
            
            jaccard_similarity = intersection / union if union > 0 else 0.0
            
            # 考虑规则类别的语义相关性
            category_bonus = 0.0
            if rule.category == RuleCategory.EMOTION and any(word in description.lower() for word in ["感觉", "情感", "氛围", "风格"]):
                category_bonus = 0.2
            elif rule.category == RuleCategory.MOTION and any(word in description.lower() for word in ["移动", "运动", "动作"]):
                category_bonus = 0.2
            elif rule.category == RuleCategory.PHYSICS and any(word in description.lower() for word in ["物理", "真实", "自然"]):
                category_bonus = 0.2
            
            return min(1.0, jaccard_similarity + category_bonus)
            
        except Exception as e:
            logger.error(f"计算语义分数失败: {e}")
            return 0.0
    
    def calculate_context_score(self, context: MatchingContext, rule: AnimationRule) -> float:
        """计算上下文相关性分数"""
        try:
            score = 0.0
            
            # 项目类型匹配
            project_type_mapping = {
                "animation": [RuleCategory.MOTION, RuleCategory.PHYSICS, RuleCategory.VISUAL],
                "ui": [RuleCategory.INTERACTION, RuleCategory.TIMING, RuleCategory.EMOTION],
                "game": [RuleCategory.PHYSICS, RuleCategory.MOTION, RuleCategory.PERFORMANCE],
                "presentation": [RuleCategory.VISUAL, RuleCategory.TIMING, RuleCategory.EMOTION]
            }
            
            if context.project_type in project_type_mapping:
                if rule.category in project_type_mapping[context.project_type]:
                    score += 0.3
            
            # 性能要求匹配
            if context.performance_requirements == "high_performance":
                if rule.category == RuleCategory.PERFORMANCE or rule.complexity == RuleComplexity.SIMPLE:
                    score += 0.2
            elif context.performance_requirements == "high_quality":
                if rule.complexity in [RuleComplexity.COMPLEX, RuleComplexity.ADVANCED]:
                    score += 0.2
            
            # 技术栈偏好匹配
            if context.preferred_tech_stacks:
                tech_match = any(tech in rule.tech_stacks for tech in context.preferred_tech_stacks)
                if tech_match:
                    score += 0.3
            
            # 历史选择偏好
            if rule.rule_id in context.historical_choices:
                score += 0.2
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"计算上下文分数失败: {e}")
            return 0.0
    
    def calculate_tech_compatibility(self, context: MatchingContext, rule: AnimationRule) -> float:
        """计算技术栈兼容性"""
        try:
            if not context.preferred_tech_stacks:
                return 0.8  # 默认兼容性
            
            # 检查技术栈匹配
            compatible_stacks = set(context.preferred_tech_stacks).intersection(set(rule.tech_stacks))
            compatibility_ratio = len(compatible_stacks) / len(context.preferred_tech_stacks)
            
            # 考虑技术栈的复杂度匹配
            complexity_bonus = 0.0
            if context.performance_requirements == "high_performance":
                if TechStack.CSS_ANIMATION in rule.tech_stacks:
                    complexity_bonus = 0.2
            elif context.performance_requirements == "high_quality":
                if TechStack.THREE_JS in rule.tech_stacks or TechStack.GSAP in rule.tech_stacks:
                    complexity_bonus = 0.2
            
            return min(1.0, compatibility_ratio + complexity_bonus)
            
        except Exception as e:
            logger.error(f"计算技术栈兼容性失败: {e}")
            return 0.5
    
    def generate_matching_reasons(self, description: str, rule: AnimationRule,
                                keyword_score: float, semantic_score: float, context_score: float) -> List[str]:
        """生成匹配原因"""
        reasons = []
        
        try:
            if keyword_score > 0.7:
                matched_keywords = [kw for kw in rule.keywords if kw.lower() in description]
                if matched_keywords:
                    reasons.append(f"关键词高度匹配: {', '.join(matched_keywords[:3])}")
            
            if semantic_score > 0.6:
                reasons.append(f"语义相似度高 ({semantic_score:.2f})")
            
            if context_score > 0.5:
                reasons.append("上下文高度相关")
            
            if rule.success_rate > 0.8:
                reasons.append(f"历史成功率高 ({rule.success_rate:.1%})")
            
            if rule.user_rating > 4.0:
                reasons.append(f"用户评分优秀 ({rule.user_rating:.1f}/5.0)")
            
            if not reasons:
                reasons.append("基础匹配")
            
            return reasons
            
        except Exception as e:
            logger.error(f"生成匹配原因失败: {e}")
            return ["匹配分析"]
    
    def estimate_performance_impact(self, rule: AnimationRule) -> float:
        """估算性能影响"""
        try:
            # 基于规则复杂度和技术栈估算性能影响
            complexity_impact = {
                RuleComplexity.SIMPLE: 0.1,
                RuleComplexity.MEDIUM: 0.3,
                RuleComplexity.COMPLEX: 0.6,
                RuleComplexity.ADVANCED: 0.8
            }
            
            tech_impact = {
                TechStack.CSS_ANIMATION: 0.1,
                TechStack.JAVASCRIPT: 0.3,
                TechStack.GSAP: 0.4,
                TechStack.THREE_JS: 0.7,
                TechStack.SVG_ANIMATION: 0.2
            }
            
            base_impact = complexity_impact.get(rule.complexity, 0.3)
            
            # 考虑技术栈影响
            if rule.tech_stacks:
                avg_tech_impact = sum(tech_impact.get(tech, 0.3) for tech in rule.tech_stacks) / len(rule.tech_stacks)
                return (base_impact + avg_tech_impact) / 2
            
            return base_impact
            
        except Exception as e:
            logger.error(f"估算性能影响失败: {e}")
            return 0.3
    
    def estimate_quality(self, rule: AnimationRule, confidence: float) -> float:
        """估算质量分数"""
        try:
            # 基于多个因素估算质量
            base_quality = confidence * 0.4
            
            # 用户评分影响
            rating_quality = (rule.user_rating / 5.0) * 0.3 if rule.user_rating > 0 else 0.15
            
            # 成功率影响
            success_quality = rule.success_rate * 0.2
            
            # 使用频率影响（归一化）
            usage_quality = min(rule.usage_count / 100.0, 1.0) * 0.1
            
            return min(1.0, base_quality + rating_quality + success_quality + usage_quality)
            
        except Exception as e:
            logger.error(f"估算质量分数失败: {e}")
            return confidence * 0.5


class RuleWeightCalculator:
    """规则权重计算器"""
    
    def __init__(self):
        self.weight_factors = {
            "confidence": 0.25,
            "user_preference": 0.20,
            "context_relevance": 0.20,
            "tech_compatibility": 0.15,
            "performance": 0.10,
            "quality": 0.10
        }
        
        logger.info("规则权重计算器初始化完成")
    
    def calculate_weight(self, rule_match: RuleMatch, context: MatchingContext,
                        user_preferences: Dict[str, Any] = None) -> float:
        """计算规则权重"""
        try:
            # 更新用户偏好分数
            if user_preferences:
                rule_match.user_preference_score = self.calculate_user_preference_score(
                    rule_match.rule, user_preferences
                )
            
            # 计算加权分数
            weighted_score = (
                rule_match.confidence * self.weight_factors["confidence"] +
                rule_match.user_preference_score * self.weight_factors["user_preference"] +
                rule_match.context_relevance * self.weight_factors["context_relevance"] +
                rule_match.tech_stack_compatibility * self.weight_factors["tech_compatibility"] +
                (1.0 - rule_match.performance_impact) * self.weight_factors["performance"] +
                rule_match.estimated_quality * self.weight_factors["quality"]
            )
            
            # 应用动态调整
            adjusted_score = self.apply_dynamic_adjustments(weighted_score, rule_match, context)
            
            return min(1.0, max(0.0, adjusted_score))
            
        except Exception as e:
            logger.error(f"计算规则权重失败: {e}")
            return rule_match.confidence * 0.5
    
    def calculate_user_preference_score(self, rule: AnimationRule, 
                                      user_preferences: Dict[str, Any]) -> float:
        """计算用户偏好分数"""
        try:
            score = 0.5  # 默认分数
            
            # 类别偏好
            preferred_categories = user_preferences.get("preferred_categories", [])
            if rule.category.value in preferred_categories:
                score += 0.2
            
            # 复杂度偏好
            preferred_complexity = user_preferences.get("preferred_complexity", "medium")
            complexity_mapping = {
                "simple": RuleComplexity.SIMPLE,
                "medium": RuleComplexity.MEDIUM,
                "complex": RuleComplexity.COMPLEX,
                "advanced": RuleComplexity.ADVANCED
            }
            
            if rule.complexity == complexity_mapping.get(preferred_complexity):
                score += 0.2
            
            # 技术栈偏好
            preferred_tech_stacks = user_preferences.get("preferred_tech_stacks", [])
            if any(tech.value in preferred_tech_stacks for tech in rule.tech_stacks):
                score += 0.2
            
            # 历史使用偏好
            frequently_used = user_preferences.get("frequently_used_rules", [])
            if rule.rule_id in frequently_used:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"计算用户偏好分数失败: {e}")
            return 0.5
    
    def apply_dynamic_adjustments(self, base_score: float, rule_match: RuleMatch,
                                context: MatchingContext) -> float:
        """应用动态调整"""
        try:
            adjusted_score = base_score
            
            # 时间约束调整
            if context.timeline_constraints.get("tight_deadline"):
                if rule_match.rule.complexity == RuleComplexity.SIMPLE:
                    adjusted_score += 0.1
                elif rule_match.rule.complexity == RuleComplexity.ADVANCED:
                    adjusted_score -= 0.1
            
            # 性能要求调整
            if context.performance_requirements == "high_performance":
                adjusted_score -= rule_match.performance_impact * 0.2
            elif context.performance_requirements == "high_quality":
                adjusted_score += rule_match.estimated_quality * 0.1
            
            # 新规则探索调整
            exploration_factor = context.user_preferences.get("exploration_factor", 0.1)
            if rule_match.rule.usage_count < 10:  # 新规则
                adjusted_score += exploration_factor
            
            return adjusted_score
            
        except Exception as e:
            logger.error(f"应用动态调整失败: {e}")
            return base_score


class RuleCombinationEngine:
    """规则组合引擎"""

    def __init__(self):
        self.combination_strategies = {
            "sequential": self.sequential_combination,
            "parallel": self.parallel_combination,
            "layered": self.layered_combination,
            "conditional": self.conditional_combination
        }

        self.compatibility_matrix = self.build_compatibility_matrix()

        logger.info("规则组合引擎初始化完成")

    def build_compatibility_matrix(self) -> Dict[Tuple[RuleCategory, RuleCategory], float]:
        """构建兼容性矩阵"""
        matrix = {}

        # 定义类别间的兼容性分数
        compatibility_scores = {
            (RuleCategory.MOTION, RuleCategory.PHYSICS): 0.9,
            (RuleCategory.MOTION, RuleCategory.TIMING): 0.8,
            (RuleCategory.VISUAL, RuleCategory.EMOTION): 0.8,
            (RuleCategory.PHYSICS, RuleCategory.PERFORMANCE): 0.7,
            (RuleCategory.INTERACTION, RuleCategory.TIMING): 0.8,
            (RuleCategory.STYLE, RuleCategory.VISUAL): 0.9,
            (RuleCategory.EMOTION, RuleCategory.STYLE): 0.7,
            (RuleCategory.PERFORMANCE, RuleCategory.TIMING): 0.6
        }

        # 填充矩阵（双向）
        for (cat1, cat2), score in compatibility_scores.items():
            matrix[(cat1, cat2)] = score
            matrix[(cat2, cat1)] = score

        # 同类别兼容性
        for category in RuleCategory:
            matrix[(category, category)] = 0.5

        return matrix

    def combine_rules(self, rule_matches: List[RuleMatch],
                     max_combinations: int = 3) -> List[Dict[str, Any]]:
        """组合规则"""
        try:
            if len(rule_matches) < 2:
                return [{"rules": rule_matches, "strategy": "single", "compatibility": 1.0}]

            combinations = []

            # 生成不同策略的组合
            for strategy_name, strategy_func in self.combination_strategies.items():
                strategy_combinations = strategy_func(rule_matches, max_combinations)
                for combo in strategy_combinations:
                    combo["strategy"] = strategy_name
                    combinations.append(combo)

            # 按兼容性排序
            combinations.sort(key=lambda c: c["compatibility"], reverse=True)

            return combinations[:max_combinations]

        except Exception as e:
            logger.error(f"组合规则失败: {e}")
            return [{"rules": rule_matches[:1], "strategy": "fallback", "compatibility": 0.5}]

    def sequential_combination(self, rule_matches: List[RuleMatch],
                             max_combinations: int) -> List[Dict[str, Any]]:
        """顺序组合策略"""
        combinations = []

        try:
            # 按时间顺序组合规则
            for i in range(min(len(rule_matches), max_combinations)):
                for j in range(i + 1, min(len(rule_matches), max_combinations + 1)):
                    rules = rule_matches[i:j+1]
                    compatibility = self.calculate_combination_compatibility(rules)

                    if compatibility > 0.4:
                        combinations.append({
                            "rules": rules,
                            "compatibility": compatibility,
                            "execution_order": list(range(len(rules))),
                            "timing_offsets": [i * 0.2 for i in range(len(rules))]
                        })

            return combinations

        except Exception as e:
            logger.error(f"顺序组合失败: {e}")
            return []

    def parallel_combination(self, rule_matches: List[RuleMatch],
                           max_combinations: int) -> List[Dict[str, Any]]:
        """并行组合策略"""
        combinations = []

        try:
            # 选择兼容的规则进行并行组合
            for i in range(len(rule_matches)):
                for j in range(i + 1, len(rule_matches)):
                    rule1, rule2 = rule_matches[i], rule_matches[j]

                    # 检查并行兼容性
                    if self.check_parallel_compatibility(rule1, rule2):
                        compatibility = self.calculate_combination_compatibility([rule1, rule2])

                        combinations.append({
                            "rules": [rule1, rule2],
                            "compatibility": compatibility,
                            "execution_order": [0, 0],  # 同时执行
                            "timing_offsets": [0.0, 0.0]
                        })

            return combinations

        except Exception as e:
            logger.error(f"并行组合失败: {e}")
            return []

    def layered_combination(self, rule_matches: List[RuleMatch],
                          max_combinations: int) -> List[Dict[str, Any]]:
        """分层组合策略"""
        combinations = []

        try:
            # 按类别分层组合
            category_groups = defaultdict(list)
            for match in rule_matches:
                category_groups[match.rule.category].append(match)

            # 创建分层组合
            if len(category_groups) >= 2:
                categories = list(category_groups.keys())

                for i in range(len(categories)):
                    for j in range(i + 1, len(categories)):
                        cat1, cat2 = categories[i], categories[j]

                        # 选择每层的最佳规则
                        rule1 = max(category_groups[cat1], key=lambda r: r.confidence)
                        rule2 = max(category_groups[cat2], key=lambda r: r.confidence)

                        compatibility = self.get_category_compatibility(cat1, cat2)

                        if compatibility > 0.5:
                            combinations.append({
                                "rules": [rule1, rule2],
                                "compatibility": compatibility,
                                "execution_order": [0, 1],  # 分层执行
                                "timing_offsets": [0.0, 0.1],
                                "layers": [cat1.value, cat2.value]
                            })

            return combinations

        except Exception as e:
            logger.error(f"分层组合失败: {e}")
            return []

    def conditional_combination(self, rule_matches: List[RuleMatch],
                              max_combinations: int) -> List[Dict[str, Any]]:
        """条件组合策略"""
        combinations = []

        try:
            # 基于条件的规则组合
            for i, primary_rule in enumerate(rule_matches[:max_combinations]):
                conditional_rules = []

                for j, secondary_rule in enumerate(rule_matches):
                    if i != j and self.check_conditional_compatibility(primary_rule, secondary_rule):
                        conditional_rules.append(secondary_rule)

                if conditional_rules:
                    # 选择最佳的条件规则
                    best_conditional = max(conditional_rules, key=lambda r: r.confidence)

                    compatibility = self.calculate_combination_compatibility([primary_rule, best_conditional])

                    combinations.append({
                        "rules": [primary_rule, best_conditional],
                        "compatibility": compatibility,
                        "execution_order": [0, 1],
                        "timing_offsets": [0.0, 0.3],
                        "conditions": ["always", "on_complete"]
                    })

            return combinations

        except Exception as e:
            logger.error(f"条件组合失败: {e}")
            return []

    def calculate_combination_compatibility(self, rule_matches: List[RuleMatch]) -> float:
        """计算组合兼容性"""
        try:
            if len(rule_matches) < 2:
                return 1.0

            total_compatibility = 0.0
            pair_count = 0

            # 计算所有规则对的兼容性
            for i in range(len(rule_matches)):
                for j in range(i + 1, len(rule_matches)):
                    rule1, rule2 = rule_matches[i], rule_matches[j]

                    # 类别兼容性
                    category_compat = self.get_category_compatibility(rule1.rule.category, rule2.rule.category)

                    # 技术栈兼容性
                    tech_compat = self.calculate_tech_stack_compatibility(rule1.rule, rule2.rule)

                    # 复杂度兼容性
                    complexity_compat = self.calculate_complexity_compatibility(rule1.rule, rule2.rule)

                    # 综合兼容性
                    pair_compatibility = (category_compat * 0.4 + tech_compat * 0.3 + complexity_compat * 0.3)

                    total_compatibility += pair_compatibility
                    pair_count += 1

            return total_compatibility / pair_count if pair_count > 0 else 0.0

        except Exception as e:
            logger.error(f"计算组合兼容性失败: {e}")
            return 0.0

    def get_category_compatibility(self, cat1: RuleCategory, cat2: RuleCategory) -> float:
        """获取类别兼容性"""
        return self.compatibility_matrix.get((cat1, cat2), 0.3)

    def calculate_tech_stack_compatibility(self, rule1: AnimationRule, rule2: AnimationRule) -> float:
        """计算技术栈兼容性"""
        try:
            # 检查技术栈重叠
            common_stacks = set(rule1.tech_stacks).intersection(set(rule2.tech_stacks))
            total_stacks = set(rule1.tech_stacks).union(set(rule2.tech_stacks))

            if not total_stacks:
                return 0.5

            overlap_ratio = len(common_stacks) / len(total_stacks)

            # 特殊兼容性规则
            if TechStack.CSS_ANIMATION in rule1.tech_stacks and TechStack.JAVASCRIPT in rule2.tech_stacks:
                return max(overlap_ratio, 0.8)  # CSS和JS高度兼容

            if TechStack.GSAP in rule1.tech_stacks and TechStack.THREE_JS in rule2.tech_stacks:
                return max(overlap_ratio, 0.7)  # GSAP和Three.js较好兼容

            return overlap_ratio

        except Exception as e:
            logger.error(f"计算技术栈兼容性失败: {e}")
            return 0.5

    def calculate_complexity_compatibility(self, rule1: AnimationRule, rule2: AnimationRule) -> float:
        """计算复杂度兼容性"""
        try:
            complexity_diff = abs(rule1.complexity.value - rule2.complexity.value)

            # 复杂度差异越小，兼容性越高
            if complexity_diff == 0:
                return 1.0
            elif complexity_diff == 1:
                return 0.8
            elif complexity_diff == 2:
                return 0.6
            else:
                return 0.4

        except Exception as e:
            logger.error(f"计算复杂度兼容性失败: {e}")
            return 0.5

    def check_parallel_compatibility(self, rule1: RuleMatch, rule2: RuleMatch) -> bool:
        """检查并行兼容性"""
        try:
            # 检查是否可以并行执行

            # 不同类别的规则通常可以并行
            if rule1.rule.category != rule2.rule.category:
                return True

            # 相同类别但不冲突的规则
            if rule1.rule.category == RuleCategory.VISUAL:
                return True  # 视觉效果通常可以叠加

            if rule1.rule.category == RuleCategory.TIMING:
                return False  # 时间规则通常不能并行

            return False

        except Exception as e:
            logger.error(f"检查并行兼容性失败: {e}")
            return False

    def check_conditional_compatibility(self, primary: RuleMatch, secondary: RuleMatch) -> bool:
        """检查条件兼容性"""
        try:
            # 检查是否可以作为条件组合

            # 运动规则可以触发视觉效果
            if (primary.rule.category == RuleCategory.MOTION and
                secondary.rule.category == RuleCategory.VISUAL):
                return True

            # 交互规则可以触发其他规则
            if primary.rule.category == RuleCategory.INTERACTION:
                return True

            # 时间规则可以控制其他规则
            if (primary.rule.category == RuleCategory.TIMING and
                secondary.rule.category != RuleCategory.TIMING):
                return True

            return False

        except Exception as e:
            logger.error(f"检查条件兼容性失败: {e}")
            return False


class LearningOptimizationEngine:
    """学习优化引擎"""

    def __init__(self):
        self.feedback_history = []
        self.rule_performance_stats = defaultdict(lambda: {
            "usage_count": 0,
            "success_count": 0,
            "user_ratings": [],
            "performance_scores": [],
            "context_success": defaultdict(int)
        })

        self.optimization_strategies = {
            "rule_ranking": self.optimize_rule_ranking,
            "weight_adjustment": self.optimize_weight_factors,
            "context_learning": self.learn_context_patterns,
            "user_preference": self.learn_user_preferences
        }

        logger.info("学习优化引擎初始化完成")

    def record_feedback(self, rule_matches: List[RuleMatch], user_feedback: Dict[str, Any],
                       context: MatchingContext, final_choice: str = None):
        """记录用户反馈"""
        try:
            feedback_entry = {
                "timestamp": datetime.now(),
                "rule_matches": rule_matches,
                "user_feedback": user_feedback,
                "context": context,
                "final_choice": final_choice
            }

            self.feedback_history.append(feedback_entry)

            # 更新规则性能统计
            for match in rule_matches:
                rule_id = match.rule.rule_id
                stats = self.rule_performance_stats[rule_id]

                stats["usage_count"] += 1

                # 记录成功/失败
                if user_feedback.get("satisfaction", 0) >= 3:  # 满意度>=3认为成功
                    stats["success_count"] += 1

                # 记录用户评分
                if "rating" in user_feedback:
                    stats["user_ratings"].append(user_feedback["rating"])

                # 记录性能分数
                if "performance_score" in user_feedback:
                    stats["performance_scores"].append(user_feedback["performance_score"])

                # 记录上下文成功
                context_key = f"{context.project_type}_{context.performance_requirements}"
                if user_feedback.get("satisfaction", 0) >= 3:
                    stats["context_success"][context_key] += 1

            # 定期优化
            if len(self.feedback_history) % 10 == 0:
                self.optimize_system()

            logger.info(f"记录用户反馈: {len(rule_matches)}个规则匹配")

        except Exception as e:
            logger.error(f"记录用户反馈失败: {e}")

    def optimize_system(self):
        """优化系统"""
        try:
            logger.info("开始系统优化...")

            # 执行各种优化策略
            for strategy_name, strategy_func in self.optimization_strategies.items():
                try:
                    strategy_func()
                    logger.info(f"完成{strategy_name}优化")
                except Exception as e:
                    logger.error(f"{strategy_name}优化失败: {e}")

            logger.info("系统优化完成")

        except Exception as e:
            logger.error(f"系统优化失败: {e}")

    def optimize_rule_ranking(self):
        """优化规则排名"""
        try:
            # 基于历史表现更新规则的成功率和评分
            for rule_id, stats in self.rule_performance_stats.items():
                if stats["usage_count"] > 0:
                    # 更新成功率
                    success_rate = stats["success_count"] / stats["usage_count"]

                    # 更新平均评分
                    if stats["user_ratings"]:
                        avg_rating = sum(stats["user_ratings"]) / len(stats["user_ratings"])
                    else:
                        avg_rating = 0.0

                    # 这里可以更新实际的规则对象
                    # rule.success_rate = success_rate
                    # rule.user_rating = avg_rating

                    logger.debug(f"规则 {rule_id}: 成功率={success_rate:.2f}, 评分={avg_rating:.2f}")

        except Exception as e:
            logger.error(f"优化规则排名失败: {e}")

    def optimize_weight_factors(self):
        """优化权重因子"""
        try:
            # 分析哪些因子对用户满意度影响最大
            if len(self.feedback_history) < 10:
                return

            # 简化的权重优化逻辑
            high_satisfaction_feedback = [
                f for f in self.feedback_history
                if f["user_feedback"].get("satisfaction", 0) >= 4
            ]

            if high_satisfaction_feedback:
                # 分析高满意度反馈的特征
                avg_confidence = np.mean([
                    np.mean([m.confidence for m in f["rule_matches"][:3]])
                    for f in high_satisfaction_feedback
                ])

                avg_context_relevance = np.mean([
                    np.mean([m.context_relevance for m in f["rule_matches"][:3]])
                    for f in high_satisfaction_feedback
                ])

                # 根据分析结果调整权重（这里是简化版本）
                if avg_confidence > 0.8:
                    logger.info("高置信度规则表现良好，增加置信度权重")

                if avg_context_relevance > 0.7:
                    logger.info("上下文相关性重要，增加上下文权重")

        except Exception as e:
            logger.error(f"优化权重因子失败: {e}")

    def learn_context_patterns(self):
        """学习上下文模式"""
        try:
            # 分析不同上下文下的成功模式
            context_patterns = defaultdict(list)

            for feedback in self.feedback_history:
                if feedback["user_feedback"].get("satisfaction", 0) >= 3:
                    context_key = (
                        feedback["context"].project_type,
                        feedback["context"].performance_requirements
                    )

                    successful_rules = [
                        match.rule.category.value
                        for match in feedback["rule_matches"][:3]
                    ]

                    context_patterns[context_key].extend(successful_rules)

            # 分析模式
            for context_key, successful_categories in context_patterns.items():
                if len(successful_categories) >= 5:
                    category_counts = Counter(successful_categories)
                    most_common = category_counts.most_common(3)

                    logger.info(f"上下文 {context_key} 的成功模式: {most_common}")

        except Exception as e:
            logger.error(f"学习上下文模式失败: {e}")

    def learn_user_preferences(self):
        """学习用户偏好"""
        try:
            # 分析用户的选择偏好
            user_choices = defaultdict(int)
            user_ratings = defaultdict(list)

            for feedback in self.feedback_history:
                if feedback["final_choice"]:
                    user_choices[feedback["final_choice"]] += 1

                for match in feedback["rule_matches"]:
                    if "rating" in feedback["user_feedback"]:
                        user_ratings[match.rule.rule_id].append(
                            feedback["user_feedback"]["rating"]
                        )

            # 识别偏好模式
            if user_choices:
                most_chosen = max(user_choices, key=user_choices.get)
                logger.info(f"用户最常选择的规则: {most_chosen}")

            # 识别高评分规则
            high_rated_rules = []
            for rule_id, ratings in user_ratings.items():
                if len(ratings) >= 3 and np.mean(ratings) >= 4.0:
                    high_rated_rules.append(rule_id)

            if high_rated_rules:
                logger.info(f"用户高评分规则: {high_rated_rules}")

        except Exception as e:
            logger.error(f"学习用户偏好失败: {e}")

    def get_optimization_insights(self) -> Dict[str, Any]:
        """获取优化洞察"""
        try:
            insights = {
                "total_feedback": len(self.feedback_history),
                "rules_analyzed": len(self.rule_performance_stats),
                "top_performing_rules": [],
                "improvement_suggestions": []
            }

            # 找出表现最好的规则
            if self.rule_performance_stats:
                sorted_rules = sorted(
                    self.rule_performance_stats.items(),
                    key=lambda x: x[1]["success_count"] / max(x[1]["usage_count"], 1),
                    reverse=True
                )

                insights["top_performing_rules"] = [
                    {
                        "rule_id": rule_id,
                        "success_rate": stats["success_count"] / max(stats["usage_count"], 1),
                        "usage_count": stats["usage_count"]
                    }
                    for rule_id, stats in sorted_rules[:5]
                ]

            # 生成改进建议
            if len(self.feedback_history) >= 10:
                recent_satisfaction = [
                    f["user_feedback"].get("satisfaction", 0)
                    for f in self.feedback_history[-10:]
                ]

                avg_satisfaction = np.mean(recent_satisfaction)

                if avg_satisfaction < 3.0:
                    insights["improvement_suggestions"].append(
                        "用户满意度较低，建议优化规则匹配算法"
                    )
                elif avg_satisfaction > 4.0:
                    insights["improvement_suggestions"].append(
                        "用户满意度良好，可以探索更复杂的规则组合"
                    )

            return insights

        except Exception as e:
            logger.error(f"获取优化洞察失败: {e}")
            return {"error": str(e)}


class IntelligentRuleMatchingSystem(QWidget):
    """智能规则匹配系统主组件"""

    # 信号定义
    rules_matched = pyqtSignal(list)                # 规则匹配完成信号
    combination_generated = pyqtSignal(dict)        # 组合生成信号
    feedback_recorded = pyqtSignal(dict)            # 反馈记录信号
    optimization_completed = pyqtSignal(dict)       # 优化完成信号

    def __init__(self, parent=None):
        super().__init__(parent)

        # 核心组件
        self.semantic_matcher = SemanticMatcher()
        self.weight_calculator = RuleWeightCalculator()
        self.combination_engine = RuleCombinationEngine()
        self.learning_engine = LearningOptimizationEngine()

        # 规则库
        self.available_rules = []
        self.rule_categories = {}

        # 状态管理
        self.current_matches = []
        self.current_combinations = []
        self.current_context = None
        self.user_preferences = {}

        self.setup_ui()
        self.setup_connections()
        self.load_default_rules()

        logger.info("智能规则匹配系统初始化完成")

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 创建标题
        title_label = QLabel("🧠 智能规则匹配系统")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c5aa0; margin: 10px;")
        layout.addWidget(title_label)

        # 创建主要内容区域
        self.create_input_section(layout)
        self.create_matching_section(layout)
        self.create_combination_section(layout)
        self.create_optimization_section(layout)

    def create_input_section(self, layout):
        """创建输入区域"""
        input_group = QGroupBox("📝 匹配输入")
        input_layout = QVBoxLayout(input_group)

        # 描述输入
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("动画描述:"))
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("请输入动画描述，如：小球快速向右移动并发光...")
        desc_layout.addWidget(self.description_edit)
        input_layout.addLayout(desc_layout)

        # 上下文设置
        context_layout = QFormLayout()

        self.project_type_combo = QComboBox()
        self.project_type_combo.addItems(["general", "animation", "ui", "game", "presentation"])
        context_layout.addRow("项目类型:", self.project_type_combo)

        self.performance_combo = QComboBox()
        self.performance_combo.addItems(["balanced", "high_performance", "high_quality"])
        context_layout.addRow("性能要求:", self.performance_combo)

        self.audience_combo = QComboBox()
        self.audience_combo.addItems(["general", "children", "professional", "elderly"])
        context_layout.addRow("目标受众:", self.audience_combo)

        input_layout.addLayout(context_layout)

        # 匹配控制
        control_layout = QHBoxLayout()

        self.match_btn = QPushButton("🔍 智能匹配")
        self.match_btn.clicked.connect(self.perform_intelligent_matching)
        self.match_btn.setStyleSheet("""
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
        control_layout.addWidget(self.match_btn)

        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["hybrid", "semantic_similarity", "keyword_matching", "context_aware", "learning_based"])
        control_layout.addWidget(QLabel("策略:"))
        control_layout.addWidget(self.strategy_combo)

        control_layout.addStretch()

        input_layout.addLayout(control_layout)
        layout.addWidget(input_group)

    def create_matching_section(self, layout):
        """创建匹配结果区域"""
        matching_group = QGroupBox("🎯 匹配结果")
        matching_layout = QVBoxLayout(matching_group)

        # 匹配结果列表
        self.matches_list = QListWidget()
        self.matches_list.setMaximumHeight(200)
        self.matches_list.itemClicked.connect(self.on_match_selected)
        matching_layout.addWidget(self.matches_list)

        # 匹配详情
        details_layout = QHBoxLayout()

        # 左侧：规则详情
        rule_details_group = QGroupBox("规则详情")
        rule_details_layout = QVBoxLayout(rule_details_group)

        self.rule_name_label = QLabel("规则名称: -")
        self.rule_category_label = QLabel("类别: -")
        self.rule_complexity_label = QLabel("复杂度: -")
        self.rule_tech_stacks_label = QLabel("技术栈: -")

        rule_details_layout.addWidget(self.rule_name_label)
        rule_details_layout.addWidget(self.rule_category_label)
        rule_details_layout.addWidget(self.rule_complexity_label)
        rule_details_layout.addWidget(self.rule_tech_stacks_label)

        details_layout.addWidget(rule_details_group)

        # 右侧：匹配分析
        match_analysis_group = QGroupBox("匹配分析")
        match_analysis_layout = QVBoxLayout(match_analysis_group)

        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)
        match_analysis_layout.addWidget(QLabel("置信度:"))
        match_analysis_layout.addWidget(self.confidence_bar)

        self.context_relevance_bar = QProgressBar()
        self.context_relevance_bar.setRange(0, 100)
        match_analysis_layout.addWidget(QLabel("上下文相关性:"))
        match_analysis_layout.addWidget(self.context_relevance_bar)

        self.tech_compatibility_bar = QProgressBar()
        self.tech_compatibility_bar.setRange(0, 100)
        match_analysis_layout.addWidget(QLabel("技术兼容性:"))
        match_analysis_layout.addWidget(self.tech_compatibility_bar)

        details_layout.addWidget(match_analysis_group)

        matching_layout.addLayout(details_layout)

        # 匹配原因
        self.matching_reasons_text = QTextEdit()
        self.matching_reasons_text.setMaximumHeight(80)
        self.matching_reasons_text.setReadOnly(True)
        matching_layout.addWidget(QLabel("匹配原因:"))
        matching_layout.addWidget(self.matching_reasons_text)

        layout.addWidget(matching_group)

    def create_combination_section(self, layout):
        """创建组合区域"""
        combination_group = QGroupBox("🔗 智能组合")
        combination_layout = QVBoxLayout(combination_group)

        # 组合控制
        combo_control_layout = QHBoxLayout()

        self.generate_combinations_btn = QPushButton("⚡ 生成组合")
        self.generate_combinations_btn.clicked.connect(self.generate_rule_combinations)
        combo_control_layout.addWidget(self.generate_combinations_btn)

        self.max_combinations_spin = QSpinBox()
        self.max_combinations_spin.setRange(1, 5)
        self.max_combinations_spin.setValue(3)
        combo_control_layout.addWidget(QLabel("最大组合数:"))
        combo_control_layout.addWidget(self.max_combinations_spin)

        combo_control_layout.addStretch()

        combination_layout.addLayout(combo_control_layout)

        # 组合结果
        self.combinations_list = QListWidget()
        self.combinations_list.setMaximumHeight(150)
        self.combinations_list.itemClicked.connect(self.on_combination_selected)
        combination_layout.addWidget(self.combinations_list)

        # 组合详情
        self.combination_details_text = QTextEdit()
        self.combination_details_text.setMaximumHeight(100)
        self.combination_details_text.setReadOnly(True)
        combination_layout.addWidget(QLabel("组合详情:"))
        combination_layout.addWidget(self.combination_details_text)

        layout.addWidget(combination_group)

    def create_optimization_section(self, layout):
        """创建优化区域"""
        optimization_group = QGroupBox("📈 学习优化")
        optimization_layout = QVBoxLayout(optimization_group)

        # 反馈区域
        feedback_layout = QHBoxLayout()

        feedback_layout.addWidget(QLabel("用户反馈:"))

        self.satisfaction_slider = QSlider(Qt.Orientation.Horizontal)
        self.satisfaction_slider.setRange(1, 5)
        self.satisfaction_slider.setValue(3)
        self.satisfaction_slider.valueChanged.connect(self.update_satisfaction_label)
        feedback_layout.addWidget(self.satisfaction_slider)

        self.satisfaction_label = QLabel("满意度: 3")
        feedback_layout.addWidget(self.satisfaction_label)

        self.record_feedback_btn = QPushButton("📝 记录反馈")
        self.record_feedback_btn.clicked.connect(self.record_user_feedback)
        feedback_layout.addWidget(self.record_feedback_btn)

        optimization_layout.addLayout(feedback_layout)

        # 优化统计
        stats_layout = QHBoxLayout()

        self.total_feedback_label = QLabel("总反馈: 0")
        self.avg_satisfaction_label = QLabel("平均满意度: 0.0")
        self.optimization_status_label = QLabel("优化状态: 就绪")

        stats_layout.addWidget(self.total_feedback_label)
        stats_layout.addWidget(self.avg_satisfaction_label)
        stats_layout.addWidget(self.optimization_status_label)

        optimization_layout.addLayout(stats_layout)

        # 优化控制
        opt_control_layout = QHBoxLayout()

        self.optimize_btn = QPushButton("🚀 执行优化")
        self.optimize_btn.clicked.connect(self.execute_optimization)
        opt_control_layout.addWidget(self.optimize_btn)

        self.view_insights_btn = QPushButton("📊 查看洞察")
        self.view_insights_btn.clicked.connect(self.view_optimization_insights)
        opt_control_layout.addWidget(self.view_insights_btn)

        opt_control_layout.addStretch()

        optimization_layout.addLayout(opt_control_layout)

        layout.addWidget(optimization_group)

    def setup_connections(self):
        """设置信号连接"""
        # 内部信号连接
        self.rules_matched.connect(self.on_rules_matched)
        self.combination_generated.connect(self.on_combination_generated)
        self.feedback_recorded.connect(self.on_feedback_recorded)
        self.optimization_completed.connect(self.on_optimization_completed)

    def load_default_rules(self):
        """加载默认规则"""
        try:
            # 创建一些示例规则
            default_rules = [
                AnimationRule(
                    rule_id="emotion_stable",
                    name="稳定感",
                    category=RuleCategory.EMOTION,
                    description="创建稳定、可靠的视觉感受",
                    keywords=["稳定", "可靠", "平衡", "对称"],
                    tech_stacks=[TechStack.CSS_ANIMATION],
                    complexity=RuleComplexity.SIMPLE,
                    css_template="transform: translateX(0); transition: all 0.3s ease;",
                    success_rate=0.85,
                    user_rating=4.2
                ),
                AnimationRule(
                    rule_id="motion_rocket",
                    name="火箭运动",
                    category=RuleCategory.MOTION,
                    description="快速直线运动，模拟火箭推进效果",
                    keywords=["火箭", "快速", "直线", "推进", "加速"],
                    tech_stacks=[TechStack.GSAP, TechStack.CSS_ANIMATION],
                    complexity=RuleComplexity.MEDIUM,
                    css_template="transform: translateX(100%); transition: transform 0.8s cubic-bezier(0.25,0.46,0.45,0.94);",
                    success_rate=0.92,
                    user_rating=4.6
                ),
                AnimationRule(
                    rule_id="physics_bounce",
                    name="弹跳效果",
                    category=RuleCategory.PHYSICS,
                    description="模拟物理弹跳效果",
                    keywords=["弹跳", "反弹", "物理", "弹性"],
                    tech_stacks=[TechStack.GSAP, TechStack.JAVASCRIPT],
                    complexity=RuleComplexity.COMPLEX,
                    js_template="gsap.to(element, {y: -100, duration: 0.5, ease: 'bounce.out'});",
                    success_rate=0.78,
                    user_rating=4.1
                ),
                AnimationRule(
                    rule_id="visual_glow",
                    name="发光效果",
                    category=RuleCategory.VISUAL,
                    description="添加发光视觉效果",
                    keywords=["发光", "光晕", "亮度", "辉光"],
                    tech_stacks=[TechStack.CSS_ANIMATION, TechStack.SVG_ANIMATION],
                    complexity=RuleComplexity.MEDIUM,
                    css_template="box-shadow: 0 0 20px rgba(0,150,255,0.8); filter: brightness(1.2);",
                    success_rate=0.88,
                    user_rating=4.4
                ),
                AnimationRule(
                    rule_id="timing_fast",
                    name="快速时间",
                    category=RuleCategory.TIMING,
                    description="快速执行的时间控制",
                    keywords=["快速", "瞬间", "急速", "立即"],
                    tech_stacks=[TechStack.CSS_ANIMATION, TechStack.JAVASCRIPT],
                    complexity=RuleComplexity.SIMPLE,
                    css_template="animation-duration: 0.3s; animation-timing-function: ease-out;",
                    success_rate=0.90,
                    user_rating=4.0
                )
            ]

            self.available_rules = default_rules

            # 按类别分组
            for rule in default_rules:
                if rule.category not in self.rule_categories:
                    self.rule_categories[rule.category] = []
                self.rule_categories[rule.category].append(rule)

            logger.info(f"加载了 {len(default_rules)} 个默认规则")

        except Exception as e:
            logger.error(f"加载默认规则失败: {e}")

    def perform_intelligent_matching(self):
        """执行智能匹配"""
        try:
            description = self.description_edit.text().strip()
            if not description:
                QMessageBox.warning(self, "警告", "请输入动画描述")
                return

            # 构建匹配上下文
            context = MatchingContext(
                description=description,
                project_type=self.project_type_combo.currentText(),
                target_audience=self.audience_combo.currentText(),
                performance_requirements=self.performance_combo.currentText(),
                user_preferences=self.user_preferences
            )

            self.current_context = context

            # 执行匹配
            matches = self.semantic_matcher.find_matching_rules(
                description, self.available_rules, context
            )

            # 计算权重
            for match in matches:
                match.weight = self.weight_calculator.calculate_weight(
                    match, context, self.user_preferences
                )

            # 按权重排序
            matches.sort(key=lambda m: m.weight, reverse=True)

            self.current_matches = matches[:10]  # 保留前10个匹配

            # 发送信号
            self.rules_matched.emit(self.current_matches)

            logger.info(f"智能匹配完成，找到 {len(self.current_matches)} 个匹配规则")

        except Exception as e:
            logger.error(f"智能匹配失败: {e}")
            QMessageBox.critical(self, "错误", f"智能匹配失败: {str(e)}")

    def generate_rule_combinations(self):
        """生成规则组合"""
        try:
            if not self.current_matches:
                QMessageBox.warning(self, "警告", "请先执行智能匹配")
                return

            max_combinations = self.max_combinations_spin.value()

            # 生成组合
            combinations = self.combination_engine.combine_rules(
                self.current_matches[:5], max_combinations
            )

            self.current_combinations = combinations

            # 发送信号
            self.combination_generated.emit({
                "combinations": combinations,
                "count": len(combinations)
            })

            logger.info(f"生成了 {len(combinations)} 个规则组合")

        except Exception as e:
            logger.error(f"生成规则组合失败: {e}")
            QMessageBox.critical(self, "错误", f"生成规则组合失败: {str(e)}")

    def record_user_feedback(self):
        """记录用户反馈"""
        try:
            if not self.current_matches or not self.current_context:
                QMessageBox.warning(self, "警告", "请先执行匹配")
                return

            satisfaction = self.satisfaction_slider.value()

            feedback = {
                "satisfaction": satisfaction,
                "timestamp": datetime.now().isoformat()
            }

            # 记录反馈
            self.learning_engine.record_feedback(
                self.current_matches, feedback, self.current_context
            )

            # 发送信号
            self.feedback_recorded.emit(feedback)

            logger.info(f"记录用户反馈: 满意度={satisfaction}")

        except Exception as e:
            logger.error(f"记录用户反馈失败: {e}")
            QMessageBox.critical(self, "错误", f"记录用户反馈失败: {str(e)}")

    def execute_optimization(self):
        """执行优化"""
        try:
            self.optimization_status_label.setText("优化状态: 执行中...")

            # 执行系统优化
            self.learning_engine.optimize_system()

            # 获取优化洞察
            insights = self.learning_engine.get_optimization_insights()

            # 发送信号
            self.optimization_completed.emit(insights)

            self.optimization_status_label.setText("优化状态: 完成")

            logger.info("系统优化执行完成")

        except Exception as e:
            logger.error(f"执行优化失败: {e}")
            self.optimization_status_label.setText("优化状态: 失败")
            QMessageBox.critical(self, "错误", f"执行优化失败: {str(e)}")

    def view_optimization_insights(self):
        """查看优化洞察"""
        try:
            insights = self.learning_engine.get_optimization_insights()

            # 创建洞察对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("优化洞察")
            dialog.setModal(True)
            dialog.resize(500, 400)

            layout = QVBoxLayout(dialog)

            # 显示洞察内容
            insights_text = QTextEdit()
            insights_text.setReadOnly(True)

            content = f"""
优化洞察报告
=============

总反馈数量: {insights.get('total_feedback', 0)}
分析规则数量: {insights.get('rules_analyzed', 0)}

表现最佳规则:
"""

            for rule_info in insights.get('top_performing_rules', []):
                content += f"- {rule_info['rule_id']}: 成功率 {rule_info['success_rate']:.2%}, 使用次数 {rule_info['usage_count']}\n"

            content += "\n改进建议:\n"
            for suggestion in insights.get('improvement_suggestions', []):
                content += f"- {suggestion}\n"

            insights_text.setPlainText(content)
            layout.addWidget(insights_text)

            # 关闭按钮
            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)

            dialog.exec()

        except Exception as e:
            logger.error(f"查看优化洞察失败: {e}")
            QMessageBox.critical(self, "错误", f"查看优化洞察失败: {str(e)}")

    def on_rules_matched(self, matches):
        """规则匹配完成处理"""
        try:
            self.matches_list.clear()

            for i, match in enumerate(matches):
                item_text = f"[{match.confidence:.2f}] {match.rule.name} ({match.rule.category.value})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, match)
                self.matches_list.addItem(item)

            # 自动选择第一个匹配
            if matches:
                self.matches_list.setCurrentRow(0)
                self.on_match_selected(self.matches_list.item(0))

        except Exception as e:
            logger.error(f"处理规则匹配结果失败: {e}")

    def on_match_selected(self, item):
        """匹配项选择处理"""
        try:
            if not item:
                return

            match = item.data(Qt.ItemDataRole.UserRole)
            if not match:
                return

            # 更新规则详情
            self.rule_name_label.setText(f"规则名称: {match.rule.name}")
            self.rule_category_label.setText(f"类别: {match.rule.category.value}")
            self.rule_complexity_label.setText(f"复杂度: {match.rule.complexity.name}")

            tech_stacks = ", ".join([tech.value for tech in match.rule.tech_stacks])
            self.rule_tech_stacks_label.setText(f"技术栈: {tech_stacks}")

            # 更新匹配分析
            self.confidence_bar.setValue(int(match.confidence * 100))
            self.context_relevance_bar.setValue(int(match.context_relevance * 100))
            self.tech_compatibility_bar.setValue(int(match.tech_stack_compatibility * 100))

            # 更新匹配原因
            reasons_text = "\n".join([f"• {reason}" for reason in match.matching_reasons])
            self.matching_reasons_text.setPlainText(reasons_text)

        except Exception as e:
            logger.error(f"处理匹配项选择失败: {e}")

    def on_combination_generated(self, result):
        """组合生成处理"""
        try:
            self.combinations_list.clear()

            combinations = result["combinations"]

            for i, combo in enumerate(combinations):
                rules_names = [rule.rule.name for rule in combo["rules"]]
                item_text = f"[{combo['compatibility']:.2f}] {combo['strategy']}: {' + '.join(rules_names)}"

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, combo)
                self.combinations_list.addItem(item)

            # 自动选择第一个组合
            if combinations:
                self.combinations_list.setCurrentRow(0)
                self.on_combination_selected(self.combinations_list.item(0))

        except Exception as e:
            logger.error(f"处理组合生成结果失败: {e}")

    def on_combination_selected(self, item):
        """组合选择处理"""
        try:
            if not item:
                return

            combo = item.data(Qt.ItemDataRole.UserRole)
            if not combo:
                return

            # 显示组合详情
            details = f"组合策略: {combo['strategy']}\n"
            details += f"兼容性: {combo['compatibility']:.2f}\n"
            details += f"规则数量: {len(combo['rules'])}\n\n"

            details += "包含规则:\n"
            for i, rule_match in enumerate(combo["rules"]):
                details += f"{i+1}. {rule_match.rule.name} (置信度: {rule_match.confidence:.2f})\n"

            if "execution_order" in combo:
                details += f"\n执行顺序: {combo['execution_order']}"

            if "timing_offsets" in combo:
                details += f"\n时间偏移: {combo['timing_offsets']}"

            self.combination_details_text.setPlainText(details)

        except Exception as e:
            logger.error(f"处理组合选择失败: {e}")

    def on_feedback_recorded(self, feedback):
        """反馈记录处理"""
        try:
            # 更新统计信息
            total_feedback = len(self.learning_engine.feedback_history)
            self.total_feedback_label.setText(f"总反馈: {total_feedback}")

            # 计算平均满意度
            if total_feedback > 0:
                recent_feedback = self.learning_engine.feedback_history[-10:]
                avg_satisfaction = sum(f["user_feedback"].get("satisfaction", 0) for f in recent_feedback) / len(recent_feedback)
                self.avg_satisfaction_label.setText(f"平均满意度: {avg_satisfaction:.1f}")

        except Exception as e:
            logger.error(f"处理反馈记录失败: {e}")

    def on_optimization_completed(self, insights):
        """优化完成处理"""
        try:
            # 显示优化结果
            QMessageBox.information(
                self, "优化完成",
                f"系统优化完成！\n"
                f"分析了 {insights.get('rules_analyzed', 0)} 个规则\n"
                f"基于 {insights.get('total_feedback', 0)} 个用户反馈"
            )

        except Exception as e:
            logger.error(f"处理优化完成失败: {e}")

    def update_satisfaction_label(self, value):
        """更新满意度标签"""
        self.satisfaction_label.setText(f"满意度: {value}")

    def get_current_matches(self) -> List[RuleMatch]:
        """获取当前匹配结果"""
        return self.current_matches.copy()

    def get_current_combinations(self) -> List[Dict[str, Any]]:
        """获取当前组合结果"""
        return self.current_combinations.copy()

    def set_user_preferences(self, preferences: Dict[str, Any]):
        """设置用户偏好"""
        self.user_preferences.update(preferences)

    def add_custom_rule(self, rule: AnimationRule):
        """添加自定义规则"""
        try:
            self.available_rules.append(rule)

            if rule.category not in self.rule_categories:
                self.rule_categories[rule.category] = []
            self.rule_categories[rule.category].append(rule)

            logger.info(f"添加自定义规则: {rule.name}")

        except Exception as e:
            logger.error(f"添加自定义规则失败: {e}")
