"""
AI Animation Studio - 高级预设模板系统
实现高级预设模板管理，提升内容丰富度和创作效率
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QGroupBox, QTabWidget, QSplitter, QFrame, QProgressBar,
                             QTextEdit, QListWidget, QListWidgetItem, QCheckBox,
                             QApplication, QMessageBox, QDialog, QFormLayout,
                             QSpinBox, QDoubleSpinBox, QComboBox, QSlider, QGridLayout,
                             QScrollArea, QTreeWidget, QTreeWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QThread, QPropertyAnimation
from PyQt6.QtGui import QFont, QColor, QIcon, QPainter, QBrush, QPen, QPixmap

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
import os
from pathlib import Path

from core.logger import get_logger

logger = get_logger("advanced_template_system")


class TemplateCategory(Enum):
    """模板分类枚举"""
    BASIC_ANIMATIONS = "basic_animations"           # 基础动画
    ADVANCED_EFFECTS = "advanced_effects"          # 高级效果
    UI_INTERACTIONS = "ui_interactions"            # UI交互
    DATA_VISUALIZATIONS = "data_visualizations"   # 数据可视化
    GAME_ANIMATIONS = "game_animations"            # 游戏动画
    PRESENTATION_EFFECTS = "presentation_effects"  # 演示效果
    ARTISTIC_CREATIONS = "artistic_creations"      # 艺术创作
    COMMERCIAL_TEMPLATES = "commercial_templates"   # 商业模板


class TemplateComplexity(Enum):
    """模板复杂度枚举"""
    BEGINNER = "beginner"       # 初学者
    INTERMEDIATE = "intermediate" # 中级
    ADVANCED = "advanced"       # 高级
    EXPERT = "expert"          # 专家级


class TemplateQuality(Enum):
    """模板质量枚举"""
    BASIC = "basic"            # 基础
    GOOD = "good"              # 良好
    EXCELLENT = "excellent"    # 优秀
    PREMIUM = "premium"        # 高级


@dataclass
class AdvancedTemplate:
    """高级模板数据类"""
    template_id: str
    name: str
    description: str
    category: TemplateCategory
    complexity: TemplateComplexity
    quality: TemplateQuality
    tags: List[str] = field(default_factory=list)
    author: str = "System"
    version: str = "1.0.0"
    created_date: datetime = field(default_factory=datetime.now)
    updated_date: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    rating: float = 0.0
    rating_count: int = 0
    preview_image: Optional[str] = None
    html_code: str = ""
    css_code: str = ""
    js_code: str = ""
    dependencies: List[str] = field(default_factory=list)
    customizable_properties: Dict[str, Any] = field(default_factory=dict)
    is_premium: bool = False
    is_featured: bool = False


@dataclass
class TemplateQualityMetrics:
    """模板质量指标"""
    code_quality_score: float = 0.0
    visual_appeal_score: float = 0.0
    performance_score: float = 0.0
    usability_score: float = 0.0
    creativity_score: float = 0.0
    overall_score: float = 0.0
    quality_level: TemplateQuality = TemplateQuality.BASIC


class AdvancedTemplateManager:
    """高级模板管理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.templates: Dict[str, AdvancedTemplate] = {}
        self.categories: Dict[TemplateCategory, List[str]] = {}
        self.featured_templates: List[str] = []
        self.user_favorites: List[str] = []
        
        self.templates_directory = Path("templates/advanced")
        self.templates_directory.mkdir(parents=True, exist_ok=True)
        
        self.initialize_default_templates()
        
        logger.info("高级模板管理器初始化完成")
    
    def initialize_default_templates(self):
        """初始化默认模板"""
        try:
            default_templates = [
                {
                    "template_id": "fade_in_animation",
                    "name": "淡入动画",
                    "description": "优雅的淡入效果，适用于元素出现动画",
                    "category": TemplateCategory.BASIC_ANIMATIONS,
                    "complexity": TemplateComplexity.BEGINNER,
                    "quality": TemplateQuality.GOOD,
                    "tags": ["fade", "opacity", "entrance"],
                    "html_code": '<div class="fade-in-element">Hello World</div>',
                    "css_code": """
.fade-in-element {
    opacity: 0;
    animation: fadeIn 1s ease-in-out forwards;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
                    """,
                    "customizable_properties": {
                        "duration": {"type": "number", "default": 1, "min": 0.1, "max": 5},
                        "delay": {"type": "number", "default": 0, "min": 0, "max": 3}
                    }
                },
                {
                    "template_id": "bounce_effect",
                    "name": "弹跳效果",
                    "description": "生动的弹跳动画，增加页面活力",
                    "category": TemplateCategory.ADVANCED_EFFECTS,
                    "complexity": TemplateComplexity.INTERMEDIATE,
                    "quality": TemplateQuality.EXCELLENT,
                    "tags": ["bounce", "transform", "playful"],
                    "html_code": '<div class="bounce-element">Bounce Me!</div>',
                    "css_code": """
.bounce-element {
    animation: bounce 2s infinite;
    cursor: pointer;
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% {
        transform: translateY(0);
    }
    40% {
        transform: translateY(-30px);
    }
    60% {
        transform: translateY(-15px);
    }
}
                    """,
                    "customizable_properties": {
                        "height": {"type": "number", "default": 30, "min": 10, "max": 100},
                        "duration": {"type": "number", "default": 2, "min": 0.5, "max": 5}
                    }
                },
                {
                    "template_id": "card_hover_effect",
                    "name": "卡片悬停效果",
                    "description": "现代化的卡片悬停交互效果",
                    "category": TemplateCategory.UI_INTERACTIONS,
                    "complexity": TemplateComplexity.INTERMEDIATE,
                    "quality": TemplateQuality.EXCELLENT,
                    "tags": ["hover", "card", "shadow", "transform"],
                    "html_code": """
<div class="card-hover">
    <h3>Card Title</h3>
    <p>Card content goes here...</p>
</div>
                    """,
                    "css_code": """
.card-hover {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    cursor: pointer;
}

.card-hover:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}
                    """,
                    "customizable_properties": {
                        "lift_height": {"type": "number", "default": 5, "min": 2, "max": 20},
                        "shadow_intensity": {"type": "number", "default": 0.15, "min": 0.05, "max": 0.3}
                    }
                },
                {
                    "template_id": "loading_spinner",
                    "name": "加载旋转器",
                    "description": "流畅的加载动画指示器",
                    "category": TemplateCategory.UI_INTERACTIONS,
                    "complexity": TemplateComplexity.BEGINNER,
                    "quality": TemplateQuality.GOOD,
                    "tags": ["loading", "spinner", "rotation"],
                    "html_code": '<div class="loading-spinner"></div>',
                    "css_code": """
.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
                    """,
                    "customizable_properties": {
                        "size": {"type": "number", "default": 40, "min": 20, "max": 100},
                        "color": {"type": "color", "default": "#3498db"}
                    }
                },
                {
                    "template_id": "text_typewriter",
                    "name": "打字机效果",
                    "description": "逐字显示的打字机文本动画",
                    "category": TemplateCategory.PRESENTATION_EFFECTS,
                    "complexity": TemplateComplexity.ADVANCED,
                    "quality": TemplateQuality.PREMIUM,
                    "tags": ["typewriter", "text", "animation"],
                    "html_code": '<div class="typewriter">Hello, World!</div>',
                    "css_code": """
.typewriter {
    overflow: hidden;
    border-right: .15em solid orange;
    white-space: nowrap;
    margin: 0 auto;
    letter-spacing: .15em;
    animation: 
        typing 3.5s steps(40, end),
        blink-caret .75s step-end infinite;
}

@keyframes typing {
    from { width: 0 }
    to { width: 100% }
}

@keyframes blink-caret {
    from, to { border-color: transparent }
    50% { border-color: orange; }
}
                    """,
                    "customizable_properties": {
                        "typing_speed": {"type": "number", "default": 3.5, "min": 1, "max": 10},
                        "cursor_color": {"type": "color", "default": "orange"}
                    },
                    "is_premium": True,
                    "is_featured": True
                }
            ]
            
            for template_data in default_templates:
                template = AdvancedTemplate(**template_data)
                self.add_template(template)
            
            logger.info(f"初始化了 {len(default_templates)} 个默认模板")
            
        except Exception as e:
            logger.error(f"初始化默认模板失败: {e}")
    
    def add_template(self, template: AdvancedTemplate):
        """添加模板"""
        try:
            self.templates[template.template_id] = template
            
            # 更新分类索引
            if template.category not in self.categories:
                self.categories[template.category] = []
            self.categories[template.category].append(template.template_id)
            
            # 更新特色模板
            if template.is_featured:
                self.featured_templates.append(template.template_id)
            
            logger.debug(f"添加模板: {template.name}")
            
        except Exception as e:
            logger.error(f"添加模板失败: {e}")
    
    def get_template(self, template_id: str) -> Optional[AdvancedTemplate]:
        """获取模板"""
        return self.templates.get(template_id)
    
    def get_templates_by_category(self, category: TemplateCategory) -> List[AdvancedTemplate]:
        """按分类获取模板"""
        template_ids = self.categories.get(category, [])
        return [self.templates[tid] for tid in template_ids if tid in self.templates]
    
    def get_featured_templates(self) -> List[AdvancedTemplate]:
        """获取特色模板"""
        return [self.templates[tid] for tid in self.featured_templates if tid in self.templates]
    
    def search_templates(self, query: str, category: Optional[TemplateCategory] = None) -> List[AdvancedTemplate]:
        """搜索模板"""
        try:
            results = []
            query_lower = query.lower()
            
            for template in self.templates.values():
                # 分类过滤
                if category and template.category != category:
                    continue
                
                # 文本匹配
                if (query_lower in template.name.lower() or
                    query_lower in template.description.lower() or
                    any(query_lower in tag.lower() for tag in template.tags)):
                    results.append(template)
            
            # 按相关性排序
            results.sort(key=lambda t: t.rating, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"搜索模板失败: {e}")
            return []
    
    def rate_template(self, template_id: str, rating: float):
        """评价模板"""
        try:
            template = self.templates.get(template_id)
            if template:
                # 更新评分
                total_rating = template.rating * template.rating_count + rating
                template.rating_count += 1
                template.rating = total_rating / template.rating_count
                
                logger.debug(f"模板 {template.name} 评分更新: {template.rating:.2f}")
            
        except Exception as e:
            logger.error(f"评价模板失败: {e}")
    
    def use_template(self, template_id: str):
        """使用模板"""
        try:
            template = self.templates.get(template_id)
            if template:
                template.usage_count += 1
                logger.debug(f"模板 {template.name} 使用次数: {template.usage_count}")
            
        except Exception as e:
            logger.error(f"使用模板失败: {e}")


class TemplateQualityAnalyzer:
    """模板质量分析器"""
    
    def __init__(self):
        self.quality_weights = {
            "code_quality": 0.25,
            "visual_appeal": 0.20,
            "performance": 0.20,
            "usability": 0.15,
            "creativity": 0.20
        }
        
        logger.info("模板质量分析器初始化完成")
    
    def analyze_template_quality(self, template: AdvancedTemplate) -> TemplateQualityMetrics:
        """分析模板质量"""
        try:
            metrics = TemplateQualityMetrics()
            
            # 代码质量分析
            metrics.code_quality_score = self.analyze_code_quality(template)
            
            # 视觉吸引力分析
            metrics.visual_appeal_score = self.analyze_visual_appeal(template)
            
            # 性能分析
            metrics.performance_score = self.analyze_performance(template)
            
            # 可用性分析
            metrics.usability_score = self.analyze_usability(template)
            
            # 创意性分析
            metrics.creativity_score = self.analyze_creativity(template)
            
            # 计算总分
            metrics.overall_score = (
                metrics.code_quality_score * self.quality_weights["code_quality"] +
                metrics.visual_appeal_score * self.quality_weights["visual_appeal"] +
                metrics.performance_score * self.quality_weights["performance"] +
                metrics.usability_score * self.quality_weights["usability"] +
                metrics.creativity_score * self.quality_weights["creativity"]
            )
            
            # 确定质量等级
            if metrics.overall_score >= 90:
                metrics.quality_level = TemplateQuality.PREMIUM
            elif metrics.overall_score >= 75:
                metrics.quality_level = TemplateQuality.EXCELLENT
            elif metrics.overall_score >= 60:
                metrics.quality_level = TemplateQuality.GOOD
            else:
                metrics.quality_level = TemplateQuality.BASIC
            
            return metrics
            
        except Exception as e:
            logger.error(f"分析模板质量失败: {e}")
            return TemplateQualityMetrics()
    
    def analyze_code_quality(self, template: AdvancedTemplate) -> float:
        """分析代码质量"""
        try:
            score = 70.0  # 基础分数
            
            # CSS代码质量检查
            css_code = template.css_code
            if css_code:
                # 检查是否使用了现代CSS特性
                if "flexbox" in css_code or "grid" in css_code:
                    score += 10
                if "transition" in css_code or "animation" in css_code:
                    score += 10
                if "@keyframes" in css_code:
                    score += 5
                # 检查代码结构
                if css_code.count("{") == css_code.count("}"):
                    score += 5
            
            # HTML代码质量检查
            html_code = template.html_code
            if html_code:
                # 检查语义化标签
                semantic_tags = ["header", "nav", "main", "section", "article", "aside", "footer"]
                if any(tag in html_code for tag in semantic_tags):
                    score += 5
            
            return min(100, score)
            
        except Exception as e:
            logger.error(f"分析代码质量失败: {e}")
            return 50.0
    
    def analyze_visual_appeal(self, template: AdvancedTemplate) -> float:
        """分析视觉吸引力"""
        try:
            score = 60.0  # 基础分数
            
            # 基于模板复杂度调整
            if template.complexity == TemplateComplexity.EXPERT:
                score += 20
            elif template.complexity == TemplateComplexity.ADVANCED:
                score += 15
            elif template.complexity == TemplateComplexity.INTERMEDIATE:
                score += 10
            
            # 基于分类调整
            if template.category in [TemplateCategory.ARTISTIC_CREATIONS, TemplateCategory.ADVANCED_EFFECTS]:
                score += 15
            
            # 基于标签调整
            visual_tags = ["gradient", "shadow", "glow", "3d", "artistic"]
            tag_bonus = sum(5 for tag in template.tags if any(vt in tag.lower() for vt in visual_tags))
            score += min(15, tag_bonus)
            
            return min(100, score)
            
        except Exception as e:
            logger.error(f"分析视觉吸引力失败: {e}")
            return 50.0
    
    def analyze_performance(self, template: AdvancedTemplate) -> float:
        """分析性能"""
        try:
            score = 80.0  # 基础分数
            
            # CSS性能检查
            css_code = template.css_code
            if css_code:
                # 检查是否使用了高性能的CSS属性
                if "transform" in css_code:
                    score += 10
                if "opacity" in css_code:
                    score += 5
                # 检查是否避免了低性能属性
                if "width" in css_code or "height" in css_code:
                    score -= 5
                if "left" in css_code or "top" in css_code:
                    score -= 5
            
            # JavaScript性能检查
            if template.js_code:
                score -= 10  # JavaScript通常比CSS动画性能低
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"分析性能失败: {e}")
            return 50.0
    
    def analyze_usability(self, template: AdvancedTemplate) -> float:
        """分析可用性"""
        try:
            score = 70.0  # 基础分数
            
            # 基于复杂度调整（简单的模板更易用）
            if template.complexity == TemplateComplexity.BEGINNER:
                score += 15
            elif template.complexity == TemplateComplexity.INTERMEDIATE:
                score += 10
            elif template.complexity == TemplateComplexity.ADVANCED:
                score += 5
            
            # 基于可自定义属性数量
            customizable_count = len(template.customizable_properties)
            if customizable_count > 0:
                score += min(15, customizable_count * 3)
            
            # 基于使用次数（受欢迎程度）
            if template.usage_count > 100:
                score += 10
            elif template.usage_count > 50:
                score += 5
            
            return min(100, score)
            
        except Exception as e:
            logger.error(f"分析可用性失败: {e}")
            return 50.0
    
    def analyze_creativity(self, template: AdvancedTemplate) -> float:
        """分析创意性"""
        try:
            score = 60.0  # 基础分数
            
            # 基于分类调整
            if template.category == TemplateCategory.ARTISTIC_CREATIONS:
                score += 20
            elif template.category == TemplateCategory.ADVANCED_EFFECTS:
                score += 15
            elif template.category == TemplateCategory.GAME_ANIMATIONS:
                score += 10
            
            # 基于标签调整
            creative_tags = ["unique", "innovative", "artistic", "creative", "experimental"]
            tag_bonus = sum(5 for tag in template.tags if any(ct in tag.lower() for ct in creative_tags))
            score += min(20, tag_bonus)
            
            # 基于复杂度调整
            if template.complexity == TemplateComplexity.EXPERT:
                score += 15
            elif template.complexity == TemplateComplexity.ADVANCED:
                score += 10
            
            return min(100, score)
            
        except Exception as e:
            logger.error(f"分析创意性失败: {e}")
            return 50.0


class TemplatePersonalizationEngine:
    """模板个性化引擎"""
    
    def __init__(self):
        self.user_preferences = {
            "preferred_categories": {},
            "preferred_complexity": TemplateComplexity.INTERMEDIATE,
            "preferred_quality": TemplateQuality.GOOD,
            "usage_history": [],
            "favorite_tags": []
        }
        
        logger.info("模板个性化引擎初始化完成")
    
    def learn_from_usage(self, template: AdvancedTemplate, usage_duration: float, rating: Optional[float] = None):
        """从使用行为中学习"""
        try:
            # 记录使用历史
            usage_record = {
                "template_id": template.template_id,
                "category": template.category.value,
                "complexity": template.complexity.value,
                "quality": template.quality.value,
                "tags": template.tags,
                "usage_duration": usage_duration,
                "rating": rating,
                "timestamp": datetime.now().isoformat()
            }
            
            self.user_preferences["usage_history"].append(usage_record)
            
            # 更新分类偏好
            category = template.category.value
            if category not in self.user_preferences["preferred_categories"]:
                self.user_preferences["preferred_categories"][category] = 0
            
            # 基于使用时长和评分调整偏好权重
            weight_increase = usage_duration / 60.0  # 转换为分钟
            if rating:
                weight_increase *= (rating / 5.0)  # 评分权重
            
            self.user_preferences["preferred_categories"][category] += weight_increase
            
            # 更新标签偏好
            for tag in template.tags:
                if tag not in self.user_preferences["favorite_tags"]:
                    self.user_preferences["favorite_tags"].append(tag)
            
            logger.debug(f"学习用户偏好: {template.name}")
            
        except Exception as e:
            logger.error(f"学习用户偏好失败: {e}")
    
    def get_personalized_recommendations(self, templates: List[AdvancedTemplate], count: int = 10) -> List[AdvancedTemplate]:
        """获取个性化推荐"""
        try:
            if not templates:
                return []
            
            # 计算每个模板的个性化分数
            scored_templates = []
            for template in templates:
                score = self.calculate_personalization_score(template)
                scored_templates.append((template, score))
            
            # 按分数排序
            scored_templates.sort(key=lambda x: x[1], reverse=True)
            
            # 返回前N个推荐
            return [template for template, _ in scored_templates[:count]]
            
        except Exception as e:
            logger.error(f"获取个性化推荐失败: {e}")
            return templates[:count]
    
    def calculate_personalization_score(self, template: AdvancedTemplate) -> float:
        """计算个性化分数"""
        try:
            score = 0.0
            
            # 分类偏好分数
            category_preference = self.user_preferences["preferred_categories"].get(
                template.category.value, 0
            )
            score += category_preference * 0.4
            
            # 标签匹配分数
            tag_matches = sum(1 for tag in template.tags 
                            if tag in self.user_preferences["favorite_tags"])
            score += tag_matches * 0.3
            
            # 质量分数
            quality_scores = {
                TemplateQuality.BASIC: 1,
                TemplateQuality.GOOD: 2,
                TemplateQuality.EXCELLENT: 3,
                TemplateQuality.PREMIUM: 4
            }
            score += quality_scores.get(template.quality, 1) * 0.2
            
            # 流行度分数
            score += min(template.usage_count / 100.0, 1.0) * 0.1
            
            return score
            
        except Exception as e:
            logger.error(f"计算个性化分数失败: {e}")
            return 0.0
