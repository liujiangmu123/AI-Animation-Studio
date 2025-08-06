"""
AI Animation Studio - 自然语言动画生成系统
实现智能化描述分析、意图识别、上下文理解和智能建议
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTextEdit, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
                             QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
                             QProgressBar, QFrame, QScrollArea, QGroupBox, QFormLayout,
                             QCheckBox, QTabWidget, QSplitter, QMessageBox, QDialog,
                             QApplication, QMenu, QToolButton, QStackedWidget)
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
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

try:
    import nltk
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    nltk = None
from collections import defaultdict, Counter

from core.logger import get_logger
from core.data_structures import AnimationSolution, TechStack, AnimationType

logger = get_logger("natural_language_animation_system")


class IntentType(Enum):
    """意图类型枚举"""
    CREATE_ANIMATION = "create_animation"       # 创建动画
    MODIFY_ANIMATION = "modify_animation"       # 修改动画
    ENHANCE_EFFECT = "enhance_effect"           # 增强效果
    ADJUST_TIMING = "adjust_timing"             # 调整时间
    CHANGE_STYLE = "change_style"               # 改变样式
    ADD_INTERACTION = "add_interaction"         # 添加交互
    OPTIMIZE_PERFORMANCE = "optimize_performance"  # 优化性能
    COMBINE_ANIMATIONS = "combine_animations"   # 组合动画


class SemanticCategory(Enum):
    """语义类别枚举"""
    MOTION = "motion"                   # 运动
    VISUAL_EFFECT = "visual_effect"     # 视觉效果
    TIMING = "timing"                   # 时间
    EMOTION = "emotion"                 # 情感
    PHYSICS = "physics"                 # 物理
    INTERACTION = "interaction"         # 交互
    STYLE = "style"                     # 样式
    CONTEXT = "context"                 # 上下文


class ConfidenceLevel(Enum):
    """置信度级别枚举"""
    VERY_LOW = 0.2      # 很低
    LOW = 0.4           # 低
    MEDIUM = 0.6        # 中等
    HIGH = 0.8          # 高
    VERY_HIGH = 0.95    # 很高


@dataclass
class SemanticEntity:
    """语义实体"""
    text: str
    category: SemanticCategory
    confidence: float
    start_pos: int
    end_pos: int
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntentAnalysis:
    """意图分析结果"""
    primary_intent: IntentType
    secondary_intents: List[IntentType]
    confidence: float
    reasoning: str
    context_clues: List[str] = field(default_factory=list)


@dataclass
class SemanticAnalysisResult:
    """语义分析结果"""
    entities: List[SemanticEntity]
    intent_analysis: IntentAnalysis
    complexity_score: float
    clarity_score: float
    completeness_score: float
    overall_quality: float
    suggestions: List[str] = field(default_factory=list)
    missing_elements: List[str] = field(default_factory=list)


class AdvancedSemanticAnalyzer:
    """高级语义分析器"""
    
    def __init__(self):
        # 初始化NLP模型
        try:
            self.nlp = spacy.load("zh_core_web_sm")
        except OSError:
            logger.warning("中文模型未找到，使用英文模型")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.error("NLP模型未找到，使用基础分析")
                self.nlp = None
        
        # 语义词典
        self.semantic_patterns = self.initialize_semantic_patterns()
        self.intent_patterns = self.initialize_intent_patterns()
        self.context_keywords = self.initialize_context_keywords()
        
        logger.info("高级语义分析器初始化完成")
    
    def initialize_semantic_patterns(self) -> Dict[SemanticCategory, Dict[str, List[str]]]:
        """初始化语义模式"""
        return {
            SemanticCategory.MOTION: {
                "verbs": ["移动", "飞行", "旋转", "缩放", "跳跃", "滑动", "弹跳", "摇摆", "振动", "漂浮"],
                "directions": ["向上", "向下", "向左", "向右", "顺时针", "逆时针", "对角", "螺旋"],
                "speeds": ["快速", "缓慢", "急速", "平稳", "突然", "渐进", "瞬间", "持续"],
                "patterns": ["直线", "曲线", "圆形", "椭圆", "波浪", "锯齿", "随机", "路径"]
            },
            SemanticCategory.VISUAL_EFFECT: {
                "effects": ["发光", "阴影", "模糊", "透明", "渐变", "闪烁", "粒子", "拖尾", "光晕", "反射"],
                "colors": ["红色", "蓝色", "绿色", "黄色", "紫色", "橙色", "黑色", "白色", "彩色", "单色"],
                "textures": ["金属", "玻璃", "木质", "石质", "液体", "气体", "火焰", "冰霜", "电光", "霓虹"],
                "transformations": ["变形", "扭曲", "拉伸", "压缩", "翻转", "镜像", "分裂", "合并"]
            },
            SemanticCategory.TIMING: {
                "durations": ["瞬间", "短暂", "持续", "长时间", "永久", "循环", "重复", "一次性"],
                "rhythms": ["节拍", "韵律", "同步", "异步", "交替", "连续", "间歇", "脉冲"],
                "sequences": ["先后", "同时", "依次", "并行", "串行", "交叉", "重叠", "间隔"],
                "triggers": ["点击", "悬停", "滚动", "加载", "完成", "开始", "结束", "暂停"]
            },
            SemanticCategory.EMOTION: {
                "moods": ["欢快", "沉稳", "激动", "平静", "紧张", "轻松", "神秘", "明亮", "温暖", "冷酷"],
                "energy": ["活力", "动感", "静谧", "爆发", "收敛", "张扬", "内敛", "狂野", "优雅", "粗犷"],
                "atmosphere": ["科技感", "未来感", "复古", "现代", "古典", "工业", "自然", "梦幻", "现实", "抽象"]
            },
            SemanticCategory.PHYSICS: {
                "forces": ["重力", "弹性", "摩擦", "惯性", "磁力", "风力", "浮力", "压力", "张力", "扭力"],
                "behaviors": ["碰撞", "反弹", "穿透", "吸附", "排斥", "跟随", "避让", "聚集", "分散", "流动"],
                "properties": ["质量", "密度", "硬度", "柔软", "粘性", "弹性", "脆性", "韧性", "光滑", "粗糙"]
            }
        }
    
    def initialize_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """初始化意图模式"""
        return {
            IntentType.CREATE_ANIMATION: [
                "创建", "制作", "生成", "做一个", "来一个", "设计", "构建", "实现"
            ],
            IntentType.MODIFY_ANIMATION: [
                "修改", "调整", "改变", "更新", "优化", "完善", "改进", "微调"
            ],
            IntentType.ENHANCE_EFFECT: [
                "增强", "加强", "提升", "丰富", "美化", "炫酷", "华丽", "特效"
            ],
            IntentType.ADJUST_TIMING: [
                "加快", "减慢", "延迟", "提前", "同步", "时间", "节奏", "速度"
            ],
            IntentType.CHANGE_STYLE: [
                "风格", "样式", "主题", "色彩", "外观", "视觉", "设计", "美学"
            ],
            IntentType.ADD_INTERACTION: [
                "交互", "点击", "悬停", "拖拽", "滚动", "响应", "控制", "操作"
            ]
        }
    
    def initialize_context_keywords(self) -> Dict[str, List[str]]:
        """初始化上下文关键词"""
        return {
            "project_type": ["网站", "应用", "游戏", "演示", "教育", "商业", "艺术", "科技"],
            "target_audience": ["儿童", "青少年", "成人", "专业", "大众", "高端", "入门", "专家"],
            "device_context": ["手机", "平板", "电脑", "大屏", "VR", "AR", "智能手表", "电视"],
            "performance_context": ["高性能", "低功耗", "流畅", "兼容", "轻量", "复杂", "简单", "高效"]
        }
    
    def analyze_description(self, description: str, context: Dict[str, Any] = None) -> SemanticAnalysisResult:
        """分析描述文本"""
        try:
            # 预处理文本
            cleaned_text = self.preprocess_text(description)
            
            # 提取语义实体
            entities = self.extract_semantic_entities(cleaned_text)
            
            # 分析意图
            intent_analysis = self.analyze_intent(cleaned_text, entities, context)
            
            # 计算质量分数
            complexity_score = self.calculate_complexity_score(entities)
            clarity_score = self.calculate_clarity_score(cleaned_text, entities)
            completeness_score = self.calculate_completeness_score(entities)
            overall_quality = (complexity_score + clarity_score + completeness_score) / 3
            
            # 生成建议
            suggestions = self.generate_suggestions(entities, intent_analysis, overall_quality)
            missing_elements = self.identify_missing_elements(entities)
            
            result = SemanticAnalysisResult(
                entities=entities,
                intent_analysis=intent_analysis,
                complexity_score=complexity_score,
                clarity_score=clarity_score,
                completeness_score=completeness_score,
                overall_quality=overall_quality,
                suggestions=suggestions,
                missing_elements=missing_elements
            )
            
            logger.info(f"语义分析完成，质量分数: {overall_quality:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"语义分析失败: {e}")
            # 返回基础分析结果
            return self.create_fallback_analysis(description)
    
    def preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 去除多余空格和标点
        text = re.sub(r'\s+', ' ', text.strip())
        # 统一标点符号
        text = re.sub(r'[，。！？；：]', ',', text)
        return text
    
    def extract_semantic_entities(self, text: str) -> List[SemanticEntity]:
        """提取语义实体"""
        entities = []
        
        try:
            # 使用spaCy进行NLP分析
            if self.nlp:
                doc = self.nlp(text)
                
                # 提取命名实体
                for ent in doc.ents:
                    category = self.map_spacy_label_to_category(ent.label_)
                    if category:
                        entity = SemanticEntity(
                            text=ent.text,
                            category=category,
                            confidence=0.8,
                            start_pos=ent.start_char,
                            end_pos=ent.end_char,
                            attributes={"spacy_label": ent.label_}
                        )
                        entities.append(entity)
            
            # 使用模式匹配提取语义实体
            for category, patterns in self.semantic_patterns.items():
                for pattern_type, keywords in patterns.items():
                    for keyword in keywords:
                        matches = list(re.finditer(re.escape(keyword), text, re.IGNORECASE))
                        for match in matches:
                            entity = SemanticEntity(
                                text=match.group(),
                                category=category,
                                confidence=0.7,
                                start_pos=match.start(),
                                end_pos=match.end(),
                                attributes={"pattern_type": pattern_type}
                            )
                            entities.append(entity)
            
            # 去重和排序
            entities = self.deduplicate_entities(entities)
            entities.sort(key=lambda e: e.start_pos)
            
            return entities
            
        except Exception as e:
            logger.error(f"提取语义实体失败: {e}")
            return []
    
    def map_spacy_label_to_category(self, label: str) -> Optional[SemanticCategory]:
        """映射spaCy标签到语义类别"""
        mapping = {
            "PERSON": SemanticCategory.CONTEXT,
            "ORG": SemanticCategory.CONTEXT,
            "GPE": SemanticCategory.CONTEXT,
            "TIME": SemanticCategory.TIMING,
            "CARDINAL": SemanticCategory.TIMING,
            "ORDINAL": SemanticCategory.TIMING
        }
        return mapping.get(label)
    
    def deduplicate_entities(self, entities: List[SemanticEntity]) -> List[SemanticEntity]:
        """去重语义实体"""
        unique_entities = []
        seen_spans = set()
        
        for entity in entities:
            span = (entity.start_pos, entity.end_pos, entity.text.lower())
            if span not in seen_spans:
                seen_spans.add(span)
                unique_entities.append(entity)
        
        return unique_entities
    
    def analyze_intent(self, text: str, entities: List[SemanticEntity], 
                      context: Dict[str, Any] = None) -> IntentAnalysis:
        """分析用户意图"""
        try:
            intent_scores = defaultdict(float)
            context_clues = []
            
            # 基于关键词匹配计算意图分数
            for intent_type, keywords in self.intent_patterns.items():
                for keyword in keywords:
                    if keyword in text:
                        intent_scores[intent_type] += 1.0
                        context_clues.append(f"关键词'{keyword}'指向{intent_type.value}")
            
            # 基于语义实体调整分数
            for entity in entities:
                if entity.category == SemanticCategory.MOTION:
                    intent_scores[IntentType.CREATE_ANIMATION] += 0.5
                elif entity.category == SemanticCategory.VISUAL_EFFECT:
                    intent_scores[IntentType.ENHANCE_EFFECT] += 0.5
                elif entity.category == SemanticCategory.TIMING:
                    intent_scores[IntentType.ADJUST_TIMING] += 0.5
            
            # 基于上下文调整分数
            if context:
                if context.get("has_existing_animation"):
                    intent_scores[IntentType.MODIFY_ANIMATION] += 0.3
                if context.get("performance_focused"):
                    intent_scores[IntentType.OPTIMIZE_PERFORMANCE] += 0.2
            
            # 确定主要意图和次要意图
            if intent_scores:
                sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
                primary_intent = sorted_intents[0][0]
                primary_score = sorted_intents[0][1]
                
                secondary_intents = [intent for intent, score in sorted_intents[1:3] if score > 0.3]
                
                # 计算置信度
                total_score = sum(intent_scores.values())
                confidence = min(0.95, primary_score / max(total_score, 1.0))
                
                reasoning = f"基于{len(context_clues)}个上下文线索，主要意图为{primary_intent.value}"
            else:
                # 默认意图
                primary_intent = IntentType.CREATE_ANIMATION
                secondary_intents = []
                confidence = 0.3
                reasoning = "未检测到明确意图，默认为创建动画"
            
            return IntentAnalysis(
                primary_intent=primary_intent,
                secondary_intents=secondary_intents,
                confidence=confidence,
                reasoning=reasoning,
                context_clues=context_clues
            )
            
        except Exception as e:
            logger.error(f"意图分析失败: {e}")
            return IntentAnalysis(
                primary_intent=IntentType.CREATE_ANIMATION,
                secondary_intents=[],
                confidence=0.3,
                reasoning=f"分析失败: {str(e)}",
                context_clues=[]
            )
    
    def calculate_complexity_score(self, entities: List[SemanticEntity]) -> float:
        """计算复杂度分数"""
        try:
            if not entities:
                return 0.1
            
            # 基于实体数量和类别多样性
            entity_count = len(entities)
            unique_categories = len(set(entity.category for entity in entities))
            
            # 复杂度指标
            complexity_indicators = {
                SemanticCategory.PHYSICS: 0.3,
                SemanticCategory.INTERACTION: 0.25,
                SemanticCategory.VISUAL_EFFECT: 0.2,
                SemanticCategory.MOTION: 0.15,
                SemanticCategory.TIMING: 0.1
            }
            
            complexity_score = 0.0
            for entity in entities:
                complexity_score += complexity_indicators.get(entity.category, 0.05)
            
            # 归一化到0-1范围
            normalized_score = min(1.0, complexity_score / 2.0)
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"计算复杂度分数失败: {e}")
            return 0.5
    
    def calculate_clarity_score(self, text: str, entities: List[SemanticEntity]) -> float:
        """计算清晰度分数"""
        try:
            # 文本长度适中性
            text_length = len(text)
            length_score = 1.0 if 20 <= text_length <= 200 else max(0.3, 1.0 - abs(text_length - 100) / 200)
            
            # 实体密度
            entity_density = len(entities) / max(text_length, 1) * 100
            density_score = 1.0 if 5 <= entity_density <= 20 else max(0.3, 1.0 - abs(entity_density - 12.5) / 25)
            
            # 语言清晰度（基于常见词汇）
            common_words = ["的", "了", "在", "是", "我", "有", "和", "就", "不", "人"]
            common_word_count = sum(1 for word in common_words if word in text)
            clarity_score = min(1.0, common_word_count / 5)
            
            # 综合分数
            overall_clarity = (length_score + density_score + clarity_score) / 3
            
            return overall_clarity
            
        except Exception as e:
            logger.error(f"计算清晰度分数失败: {e}")
            return 0.5
    
    def calculate_completeness_score(self, entities: List[SemanticEntity]) -> float:
        """计算完整性分数"""
        try:
            # 检查关键类别的覆盖度
            essential_categories = [
                SemanticCategory.MOTION,
                SemanticCategory.VISUAL_EFFECT,
                SemanticCategory.TIMING
            ]
            
            covered_categories = set(entity.category for entity in entities)
            coverage_ratio = len(covered_categories.intersection(essential_categories)) / len(essential_categories)
            
            # 检查描述的具体性
            specific_entities = [e for e in entities if e.confidence > 0.7]
            specificity_score = len(specific_entities) / max(len(entities), 1)
            
            # 综合完整性分数
            completeness_score = (coverage_ratio + specificity_score) / 2
            
            return completeness_score
            
        except Exception as e:
            logger.error(f"计算完整性分数失败: {e}")
            return 0.5
    
    def generate_suggestions(self, entities: List[SemanticEntity], 
                           intent_analysis: IntentAnalysis, quality_score: float) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        try:
            # 基于质量分数的建议
            if quality_score < 0.4:
                suggestions.append("描述过于简单，建议添加更多细节")
            elif quality_score > 0.9:
                suggestions.append("描述很详细，可以考虑简化以提高可读性")
            
            # 基于实体类别的建议
            categories = set(entity.category for entity in entities)
            
            if SemanticCategory.MOTION not in categories:
                suggestions.append("建议添加运动描述，如'移动'、'旋转'、'缩放'等")
            
            if SemanticCategory.TIMING not in categories:
                suggestions.append("建议指定时间信息，如'2秒内'、'快速'、'缓慢'等")
            
            if SemanticCategory.VISUAL_EFFECT not in categories:
                suggestions.append("建议添加视觉效果，如'发光'、'阴影'、'渐变'等")
            
            # 基于意图的建议
            if intent_analysis.confidence < 0.6:
                suggestions.append("意图不够明确，建议使用更直接的动词")
            
            if intent_analysis.primary_intent == IntentType.CREATE_ANIMATION:
                suggestions.append("可以添加情感色彩，如'欢快的'、'优雅的'等")
            
            return suggestions[:5]  # 最多返回5个建议
            
        except Exception as e:
            logger.error(f"生成建议失败: {e}")
            return ["建议添加更多描述细节"]
    
    def identify_missing_elements(self, entities: List[SemanticEntity]) -> List[str]:
        """识别缺失的元素"""
        missing = []
        
        try:
            categories = set(entity.category for entity in entities)
            
            if SemanticCategory.MOTION not in categories:
                missing.append("运动方式")
            
            if SemanticCategory.TIMING not in categories:
                missing.append("时间信息")
            
            if SemanticCategory.VISUAL_EFFECT not in categories:
                missing.append("视觉效果")
            
            if SemanticCategory.EMOTION not in categories:
                missing.append("情感表达")
            
            return missing
            
        except Exception as e:
            logger.error(f"识别缺失元素失败: {e}")
            return []
    
    def create_fallback_analysis(self, description: str) -> SemanticAnalysisResult:
        """创建备用分析结果"""
        return SemanticAnalysisResult(
            entities=[],
            intent_analysis=IntentAnalysis(
                primary_intent=IntentType.CREATE_ANIMATION,
                secondary_intents=[],
                confidence=0.3,
                reasoning="使用备用分析"
            ),
            complexity_score=0.5,
            clarity_score=0.5,
            completeness_score=0.3,
            overall_quality=0.4,
            suggestions=["建议提供更详细的描述"],
            missing_elements=["运动方式", "时间信息", "视觉效果"]
        )


class ContextManager:
    """上下文管理器"""

    def __init__(self):
        self.project_context = {}
        self.animation_history = []
        self.user_preferences = {}
        self.current_elements = []
        self.timeline_context = {}

        logger.info("上下文管理器初始化完成")

    def build_context(self, project_info: Dict[str, Any],
                     semantic_info: SemanticAnalysisResult,
                     intent_analysis: IntentAnalysis) -> Dict[str, Any]:
        """构建完整上下文"""
        try:
            context = {
                # 项目上下文
                "project": {
                    "type": project_info.get("type", "general"),
                    "target_audience": project_info.get("target_audience", "general"),
                    "style_theme": project_info.get("style_theme", "modern"),
                    "performance_requirements": project_info.get("performance_requirements", "standard")
                },

                # 动画历史上下文
                "history": {
                    "previous_animations": self.animation_history[-5:],  # 最近5个动画
                    "common_patterns": self.extract_common_patterns(),
                    "user_style": self.analyze_user_style()
                },

                # 当前状态上下文
                "current": {
                    "elements": self.current_elements,
                    "timeline_position": self.timeline_context.get("current_time", 0),
                    "selected_element": self.timeline_context.get("selected_element"),
                    "canvas_size": project_info.get("canvas_size", {"width": 1920, "height": 1080})
                },

                # 语义上下文
                "semantic": {
                    "complexity": semantic_info.complexity_score,
                    "clarity": semantic_info.clarity_score,
                    "completeness": semantic_info.completeness_score,
                    "primary_intent": intent_analysis.primary_intent.value,
                    "confidence": intent_analysis.confidence
                },

                # 技术上下文
                "technical": {
                    "preferred_tech_stack": self.user_preferences.get("tech_stack", "css"),
                    "performance_mode": self.user_preferences.get("performance_mode", "balanced"),
                    "browser_support": self.user_preferences.get("browser_support", "modern"),
                    "mobile_friendly": self.user_preferences.get("mobile_friendly", True)
                }
            }

            return context

        except Exception as e:
            logger.error(f"构建上下文失败: {e}")
            return {"error": str(e)}

    def extract_common_patterns(self) -> List[str]:
        """提取常见模式"""
        try:
            if not self.animation_history:
                return []

            # 分析历史动画的共同特征
            patterns = []

            # 运动模式
            motion_types = [anim.get("motion_type") for anim in self.animation_history if anim.get("motion_type")]
            if motion_types:
                most_common_motion = Counter(motion_types).most_common(1)[0][0]
                patterns.append(f"常用运动: {most_common_motion}")

            # 时长模式
            durations = [anim.get("duration") for anim in self.animation_history if anim.get("duration")]
            if durations:
                avg_duration = sum(durations) / len(durations)
                patterns.append(f"平均时长: {avg_duration:.1f}秒")

            # 效果模式
            effects = []
            for anim in self.animation_history:
                effects.extend(anim.get("effects", []))
            if effects:
                common_effects = Counter(effects).most_common(3)
                patterns.append(f"常用效果: {', '.join([effect for effect, _ in common_effects])}")

            return patterns

        except Exception as e:
            logger.error(f"提取常见模式失败: {e}")
            return []

    def analyze_user_style(self) -> Dict[str, Any]:
        """分析用户风格"""
        try:
            if not self.animation_history:
                return {"style": "unknown", "confidence": 0.0}

            # 分析风格倾向
            style_indicators = {
                "minimalist": 0,
                "complex": 0,
                "playful": 0,
                "professional": 0,
                "artistic": 0
            }

            for anim in self.animation_history:
                complexity = anim.get("complexity_score", 0.5)
                effects_count = len(anim.get("effects", []))

                if complexity < 0.3 and effects_count <= 2:
                    style_indicators["minimalist"] += 1
                elif complexity > 0.7 or effects_count > 5:
                    style_indicators["complex"] += 1

                if "bounce" in anim.get("easing", "") or "elastic" in anim.get("easing", ""):
                    style_indicators["playful"] += 1
                elif "ease" in anim.get("easing", "") or "linear" in anim.get("easing", ""):
                    style_indicators["professional"] += 1

            # 确定主要风格
            if style_indicators:
                dominant_style = max(style_indicators, key=style_indicators.get)
                confidence = style_indicators[dominant_style] / len(self.animation_history)

                return {
                    "style": dominant_style,
                    "confidence": confidence,
                    "indicators": style_indicators
                }

            return {"style": "balanced", "confidence": 0.5}

        except Exception as e:
            logger.error(f"分析用户风格失败: {e}")
            return {"style": "unknown", "confidence": 0.0}

    def update_project_context(self, project_info: Dict[str, Any]):
        """更新项目上下文"""
        self.project_context.update(project_info)

    def add_animation_to_history(self, animation_info: Dict[str, Any]):
        """添加动画到历史记录"""
        animation_info["timestamp"] = datetime.now().isoformat()
        self.animation_history.append(animation_info)

        # 保持历史记录在合理范围内
        if len(self.animation_history) > 50:
            self.animation_history = self.animation_history[-50:]

    def update_user_preferences(self, preferences: Dict[str, Any]):
        """更新用户偏好"""
        self.user_preferences.update(preferences)

    def set_current_elements(self, elements: List[Dict[str, Any]]):
        """设置当前元素"""
        self.current_elements = elements

    def update_timeline_context(self, timeline_info: Dict[str, Any]):
        """更新时间轴上下文"""
        self.timeline_context.update(timeline_info)


class IntelligentSuggestionEngine:
    """智能建议引擎"""

    def __init__(self):
        self.suggestion_templates = self.initialize_suggestion_templates()
        self.optimization_rules = self.initialize_optimization_rules()

        logger.info("智能建议引擎初始化完成")

    def initialize_suggestion_templates(self) -> Dict[str, List[str]]:
        """初始化建议模板"""
        return {
            "motion_enhancement": [
                "建议添加缓动效果，使运动更自然",
                "可以考虑添加路径动画，增加视觉趣味",
                "建议使用弹性缓动，增加动感",
                "可以添加延迟，创造层次感"
            ],
            "visual_improvement": [
                "建议添加阴影效果，增加立体感",
                "可以考虑添加发光效果，突出重点",
                "建议使用渐变色彩，丰富视觉层次",
                "可以添加粒子效果，增加动态感"
            ],
            "performance_optimization": [
                "建议使用CSS transform代替position变化",
                "可以考虑使用will-change属性优化性能",
                "建议减少同时进行的动画数量",
                "可以使用requestAnimationFrame优化帧率"
            ],
            "timing_adjustment": [
                "建议调整动画时长，当前可能过快/过慢",
                "可以考虑添加动画间的间隔",
                "建议使用交错动画，避免单调",
                "可以添加循环播放，增加持续性"
            ],
            "interaction_enhancement": [
                "建议添加鼠标悬停效果",
                "可以考虑添加点击反馈动画",
                "建议添加滚动触发动画",
                "可以添加拖拽交互功能"
            ]
        }

    def initialize_optimization_rules(self) -> List[Dict[str, Any]]:
        """初始化优化规则"""
        return [
            {
                "condition": lambda ctx: ctx.get("semantic", {}).get("complexity", 0) > 0.8,
                "suggestion": "动画复杂度较高，建议简化以提升性能",
                "priority": "high",
                "category": "performance"
            },
            {
                "condition": lambda ctx: len(ctx.get("current", {}).get("elements", [])) > 10,
                "suggestion": "元素数量较多，建议分批动画以避免卡顿",
                "priority": "medium",
                "category": "performance"
            },
            {
                "condition": lambda ctx: ctx.get("technical", {}).get("mobile_friendly", False),
                "suggestion": "考虑到移动端兼容性，建议使用轻量级动画",
                "priority": "medium",
                "category": "compatibility"
            },
            {
                "condition": lambda ctx: ctx.get("semantic", {}).get("clarity", 0) < 0.5,
                "suggestion": "描述不够清晰，建议添加更具体的细节",
                "priority": "high",
                "category": "clarity"
            }
        ]

    def generate_suggestions(self, semantic_result: SemanticAnalysisResult,
                           context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成智能建议"""
        try:
            suggestions = []

            # 基于语义分析的建议
            semantic_suggestions = self.generate_semantic_suggestions(semantic_result)
            suggestions.extend(semantic_suggestions)

            # 基于上下文的建议
            context_suggestions = self.generate_context_suggestions(context)
            suggestions.extend(context_suggestions)

            # 基于优化规则的建议
            optimization_suggestions = self.generate_optimization_suggestions(context)
            suggestions.extend(optimization_suggestions)

            # 基于用户历史的建议
            history_suggestions = self.generate_history_suggestions(context)
            suggestions.extend(history_suggestions)

            # 排序和去重
            suggestions = self.prioritize_and_deduplicate_suggestions(suggestions)

            return suggestions[:10]  # 返回前10个建议

        except Exception as e:
            logger.error(f"生成智能建议失败: {e}")
            return []

    def generate_semantic_suggestions(self, semantic_result: SemanticAnalysisResult) -> List[Dict[str, Any]]:
        """基于语义分析生成建议"""
        suggestions = []

        try:
            # 基于缺失元素的建议
            for missing in semantic_result.missing_elements:
                if missing == "运动方式":
                    suggestions.append({
                        "type": "enhancement",
                        "category": "motion",
                        "title": "添加运动描述",
                        "description": "建议指定具体的运动方式，如'向右移动'、'旋转'、'缩放'等",
                        "priority": "high",
                        "confidence": 0.9
                    })
                elif missing == "时间信息":
                    suggestions.append({
                        "type": "enhancement",
                        "category": "timing",
                        "title": "添加时间信息",
                        "description": "建议指定动画时长，如'2秒内'、'快速'、'缓慢进行'等",
                        "priority": "medium",
                        "confidence": 0.8
                    })

            # 基于质量分数的建议
            if semantic_result.overall_quality < 0.5:
                suggestions.append({
                    "type": "improvement",
                    "category": "quality",
                    "title": "提升描述质量",
                    "description": "当前描述质量较低，建议添加更多具体细节",
                    "priority": "high",
                    "confidence": 0.85
                })

            # 基于意图置信度的建议
            if semantic_result.intent_analysis.confidence < 0.6:
                suggestions.append({
                    "type": "clarification",
                    "category": "intent",
                    "title": "明确动画意图",
                    "description": "意图不够明确，建议使用更直接的动词描述想要的效果",
                    "priority": "medium",
                    "confidence": 0.7
                })

            return suggestions

        except Exception as e:
            logger.error(f"生成语义建议失败: {e}")
            return []

    def generate_context_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于上下文生成建议"""
        suggestions = []

        try:
            project_type = context.get("project", {}).get("type", "general")

            # 基于项目类型的建议
            if project_type == "educational":
                suggestions.append({
                    "type": "enhancement",
                    "category": "educational",
                    "title": "教育友好设计",
                    "description": "建议使用清晰的动画节奏，便于学习者理解",
                    "priority": "medium",
                    "confidence": 0.8
                })
            elif project_type == "commercial":
                suggestions.append({
                    "type": "enhancement",
                    "category": "commercial",
                    "title": "商业化优化",
                    "description": "建议添加品牌色彩和专业的缓动效果",
                    "priority": "medium",
                    "confidence": 0.75
                })

            # 基于技术偏好的建议
            tech_stack = context.get("technical", {}).get("preferred_tech_stack", "css")
            if tech_stack == "css":
                suggestions.append({
                    "type": "technical",
                    "category": "implementation",
                    "title": "CSS动画优化",
                    "description": "建议使用CSS transform和opacity属性以获得最佳性能",
                    "priority": "low",
                    "confidence": 0.9
                })

            return suggestions

        except Exception as e:
            logger.error(f"生成上下文建议失败: {e}")
            return []

    def generate_optimization_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于优化规则生成建议"""
        suggestions = []

        try:
            for rule in self.optimization_rules:
                if rule["condition"](context):
                    suggestions.append({
                        "type": "optimization",
                        "category": rule["category"],
                        "title": "性能优化建议",
                        "description": rule["suggestion"],
                        "priority": rule["priority"],
                        "confidence": 0.8
                    })

            return suggestions

        except Exception as e:
            logger.error(f"生成优化建议失败: {e}")
            return []

    def generate_history_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于历史记录生成建议"""
        suggestions = []

        try:
            user_style = context.get("history", {}).get("user_style", {})
            style_type = user_style.get("style", "unknown")

            if style_type == "minimalist":
                suggestions.append({
                    "type": "style",
                    "category": "consistency",
                    "title": "保持简约风格",
                    "description": "基于您的使用习惯，建议保持简洁的动画设计",
                    "priority": "low",
                    "confidence": user_style.get("confidence", 0.5)
                })
            elif style_type == "complex":
                suggestions.append({
                    "type": "style",
                    "category": "consistency",
                    "title": "丰富动画效果",
                    "description": "基于您的偏好，可以添加更多视觉效果和复杂动画",
                    "priority": "low",
                    "confidence": user_style.get("confidence", 0.5)
                })

            return suggestions

        except Exception as e:
            logger.error(f"生成历史建议失败: {e}")
            return []

    def prioritize_and_deduplicate_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """优先级排序和去重"""
        try:
            # 去重（基于描述）
            seen_descriptions = set()
            unique_suggestions = []

            for suggestion in suggestions:
                desc = suggestion.get("description", "")
                if desc not in seen_descriptions:
                    seen_descriptions.add(desc)
                    unique_suggestions.append(suggestion)

            # 优先级排序
            priority_order = {"high": 3, "medium": 2, "low": 1}

            unique_suggestions.sort(
                key=lambda s: (
                    priority_order.get(s.get("priority", "low"), 1),
                    s.get("confidence", 0.5)
                ),
                reverse=True
            )

            return unique_suggestions

        except Exception as e:
            logger.error(f"建议排序去重失败: {e}")
            return suggestions


class IntelligentPromptBuilder:
    """智能提示词构建器"""

    def __init__(self):
        self.prompt_templates = self.initialize_prompt_templates()
        self.context_enhancers = self.initialize_context_enhancers()

        logger.info("智能提示词构建器初始化完成")

    def initialize_prompt_templates(self) -> Dict[str, str]:
        """初始化提示词模板"""
        return {
            "basic": """
作为专业的动画开发专家，请根据以下描述生成高质量的动画代码：

用户描述：{description}

项目信息：
- 项目类型：{project_type}
- 目标受众：{target_audience}
- 技术栈：{tech_stack}
- 性能要求：{performance_mode}

请生成包含以下内容的完整动画方案：
1. HTML结构
2. CSS样式和动画
3. JavaScript交互（如需要）
4. 详细的实现说明

要求：
- 代码简洁高效
- 注释清晰详细
- 兼容现代浏览器
- 性能优化良好
""",
            "enhanced": """
作为顶级动画设计师和开发专家，请基于深度语义分析生成专业动画方案：

## 用户需求分析
原始描述：{description}

语义分析结果：
- 主要意图：{primary_intent}
- 复杂度：{complexity_score:.2f}
- 清晰度：{clarity_score:.2f}
- 完整性：{completeness_score:.2f}

## 上下文信息
项目背景：
- 类型：{project_type}
- 风格：{style_theme}
- 受众：{target_audience}
- 设备：{device_context}

技术要求：
- 首选技术：{preferred_tech_stack}
- 性能模式：{performance_mode}
- 浏览器支持：{browser_support}
- 移动友好：{mobile_friendly}

用户偏好：
- 历史风格：{user_style}
- 常用模式：{common_patterns}

## 智能建议
{suggestions}

## 生成要求
请生成一个完整的动画解决方案，包括：

1. **HTML结构**：语义化、可访问性良好
2. **CSS动画**：
   - 使用现代CSS特性
   - 优化性能（transform、opacity优先）
   - 响应式设计
   - 流畅的缓动函数
3. **JavaScript增强**（如需要）：
   - 交互控制
   - 动态参数调整
   - 事件处理
4. **实现说明**：
   - 设计思路
   - 技术选择理由
   - 性能优化点
   - 可能的扩展方向

请确保代码专业、高效、易维护，并充分体现用户的创意意图。
""",
            "context_aware": """
基于完整上下文的智能动画生成：

## 核心需求
{description}

## 深度分析
语义实体：{semantic_entities}
意图分析：{intent_analysis}
质量评估：{quality_assessment}

## 项目上下文
{project_context}

## 历史模式
{animation_history}

## 当前状态
画布尺寸：{canvas_size}
现有元素：{current_elements}
时间轴位置：{timeline_position}

## 智能优化建议
{optimization_suggestions}

请生成最适合当前上下文的动画方案，确保：
1. 与项目整体风格一致
2. 符合用户历史偏好
3. 考虑性能和兼容性
4. 提供多个实现选项
5. 包含详细的技术说明
"""
        }

    def initialize_context_enhancers(self) -> Dict[str, Callable]:
        """初始化上下文增强器"""
        return {
            "semantic_entities": lambda entities: ", ".join([f"{e.text}({e.category.value})" for e in entities[:5]]),
            "intent_analysis": lambda intent: f"{intent.primary_intent.value} (置信度: {intent.confidence:.2f})",
            "quality_assessment": lambda result: f"复杂度{result.complexity_score:.2f}, 清晰度{result.clarity_score:.2f}, 完整性{result.completeness_score:.2f}",
            "suggestions": lambda suggestions: "\n".join([f"- {s.get('description', '')}" for s in suggestions[:3]]),
            "common_patterns": lambda patterns: ", ".join(patterns) if patterns else "暂无历史模式"
        }

    def build_intelligent_prompt(self, description: str, semantic_result: SemanticAnalysisResult,
                                context: Dict[str, Any], suggestions: List[Dict[str, Any]]) -> str:
        """构建智能提示词"""
        try:
            # 选择合适的模板
            template_name = self.select_template(semantic_result, context)
            template = self.prompt_templates[template_name]

            # 准备模板参数
            template_params = self.prepare_template_params(
                description, semantic_result, context, suggestions
            )

            # 填充模板
            enhanced_prompt = template.format(**template_params)

            # 后处理优化
            enhanced_prompt = self.post_process_prompt(enhanced_prompt, context)

            logger.info(f"智能提示词构建完成，使用模板: {template_name}")
            return enhanced_prompt

        except Exception as e:
            logger.error(f"构建智能提示词失败: {e}")
            # 返回基础提示词
            return f"请为以下描述生成动画代码：{description}"

    def select_template(self, semantic_result: SemanticAnalysisResult,
                       context: Dict[str, Any]) -> str:
        """选择合适的模板"""
        try:
            # 基于语义质量选择模板
            quality = semantic_result.overall_quality

            if quality >= 0.8:
                return "context_aware"  # 高质量描述使用上下文感知模板
            elif quality >= 0.5:
                return "enhanced"       # 中等质量使用增强模板
            else:
                return "basic"          # 低质量使用基础模板

        except Exception as e:
            logger.error(f"选择模板失败: {e}")
            return "basic"

    def prepare_template_params(self, description: str, semantic_result: SemanticAnalysisResult,
                               context: Dict[str, Any], suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """准备模板参数"""
        try:
            params = {
                # 基础参数
                "description": description,

                # 语义分析参数
                "primary_intent": semantic_result.intent_analysis.primary_intent.value,
                "complexity_score": semantic_result.complexity_score,
                "clarity_score": semantic_result.clarity_score,
                "completeness_score": semantic_result.completeness_score,

                # 项目上下文参数
                "project_type": context.get("project", {}).get("type", "general"),
                "target_audience": context.get("project", {}).get("target_audience", "general"),
                "style_theme": context.get("project", {}).get("style_theme", "modern"),
                "device_context": "多设备兼容",

                # 技术参数
                "tech_stack": context.get("technical", {}).get("preferred_tech_stack", "css"),
                "preferred_tech_stack": context.get("technical", {}).get("preferred_tech_stack", "css"),
                "performance_mode": context.get("technical", {}).get("performance_mode", "balanced"),
                "browser_support": context.get("technical", {}).get("browser_support", "modern"),
                "mobile_friendly": "是" if context.get("technical", {}).get("mobile_friendly", True) else "否",

                # 用户偏好参数
                "user_style": context.get("history", {}).get("user_style", {}).get("style", "balanced"),
                "common_patterns": context.get("history", {}).get("common_patterns", []),

                # 当前状态参数
                "canvas_size": context.get("current", {}).get("canvas_size", {"width": 1920, "height": 1080}),
                "current_elements": len(context.get("current", {}).get("elements", [])),
                "timeline_position": context.get("current", {}).get("timeline_position", 0),

                # 高级参数（使用增强器处理）
                "semantic_entities": self.context_enhancers["semantic_entities"](semantic_result.entities),
                "intent_analysis": self.context_enhancers["intent_analysis"](semantic_result.intent_analysis),
                "quality_assessment": self.context_enhancers["quality_assessment"](semantic_result),
                "suggestions": self.context_enhancers["suggestions"](suggestions),

                # 复杂参数的字符串化
                "project_context": json.dumps(context.get("project", {}), ensure_ascii=False, indent=2),
                "animation_history": str(context.get("history", {}).get("previous_animations", [])),
                "optimization_suggestions": "\n".join([s.get("description", "") for s in suggestions[:5]])
            }

            return params

        except Exception as e:
            logger.error(f"准备模板参数失败: {e}")
            return {"description": description}

    def post_process_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """后处理提示词"""
        try:
            # 移除多余的空行
            prompt = re.sub(r'\n\s*\n\s*\n', '\n\n', prompt)

            # 确保格式整洁
            prompt = prompt.strip()

            # 根据上下文添加特殊指令
            performance_mode = context.get("technical", {}).get("performance_mode", "balanced")
            if performance_mode == "high_performance":
                prompt += "\n\n特别注意：请优先考虑性能，使用最高效的实现方式。"
            elif performance_mode == "high_quality":
                prompt += "\n\n特别注意：请优先考虑视觉效果，可以使用更复杂的实现。"

            return prompt

        except Exception as e:
            logger.error(f"后处理提示词失败: {e}")
            return prompt


class NaturalLanguageAnimationGenerator(QWidget):
    """自然语言动画生成器主组件"""

    # 信号定义
    analysis_completed = pyqtSignal(dict)           # 分析完成信号
    suggestions_generated = pyqtSignal(list)       # 建议生成信号
    animation_generated = pyqtSignal(dict)         # 动画生成信号
    context_updated = pyqtSignal(dict)             # 上下文更新信号

    def __init__(self, parent=None):
        super().__init__(parent)

        # 核心组件
        self.semantic_analyzer = AdvancedSemanticAnalyzer()
        self.context_manager = ContextManager()
        self.suggestion_engine = IntelligentSuggestionEngine()
        self.prompt_builder = IntelligentPromptBuilder()

        # 状态管理
        self.current_description = ""
        self.current_analysis = None
        self.current_context = {}
        self.current_suggestions = []
        self.generation_history = []

        self.setup_ui()
        self.setup_connections()

        logger.info("自然语言动画生成器初始化完成")

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 创建标题
        title_label = QLabel("🧠 智能自然语言动画生成器")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c5aa0; margin: 10px;")
        layout.addWidget(title_label)

        # 创建主要内容区域
        self.create_input_section(layout)
        self.create_analysis_section(layout)
        self.create_suggestions_section(layout)
        self.create_generation_section(layout)

    def create_input_section(self, layout):
        """创建输入区域"""
        input_group = QGroupBox("📝 动画描述输入")
        input_layout = QVBoxLayout(input_group)

        # 描述输入框
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText(
            "请用自然语言描述您想要的动画效果...\n\n"
            "例如：\n"
            "• 小球像火箭一样快速向右飞行，带有蓝色发光拖尾\n"
            "• 文字从左侧优雅地滑入，然后轻微弹跳\n"
            "• 图片缓慢放大并旋转360度，同时透明度从0变为1"
        )
        self.description_edit.setMinimumHeight(120)
        self.description_edit.textChanged.connect(self.on_description_changed)
        input_layout.addWidget(self.description_edit)

        # 输入工具栏
        toolbar_layout = QHBoxLayout()

        self.analyze_btn = QPushButton("🔍 智能分析")
        self.analyze_btn.clicked.connect(self.analyze_description)
        toolbar_layout.addWidget(self.analyze_btn)

        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.clicked.connect(self.clear_input)
        toolbar_layout.addWidget(self.clear_btn)

        toolbar_layout.addStretch()

        self.word_count_label = QLabel("字数: 0")
        toolbar_layout.addWidget(self.word_count_label)

        input_layout.addLayout(toolbar_layout)
        layout.addWidget(input_group)

    def create_analysis_section(self, layout):
        """创建分析区域"""
        analysis_group = QGroupBox("🧠 智能语义分析")
        analysis_layout = QVBoxLayout(analysis_group)

        # 分析结果显示
        self.analysis_display = QTextEdit()
        self.analysis_display.setReadOnly(True)
        self.analysis_display.setMaximumHeight(150)
        analysis_layout.addWidget(self.analysis_display)

        # 质量指标
        metrics_layout = QHBoxLayout()

        self.complexity_bar = QProgressBar()
        self.complexity_bar.setRange(0, 100)
        metrics_layout.addWidget(QLabel("复杂度:"))
        metrics_layout.addWidget(self.complexity_bar)

        self.clarity_bar = QProgressBar()
        self.clarity_bar.setRange(0, 100)
        metrics_layout.addWidget(QLabel("清晰度:"))
        metrics_layout.addWidget(self.clarity_bar)

        self.completeness_bar = QProgressBar()
        self.completeness_bar.setRange(0, 100)
        metrics_layout.addWidget(QLabel("完整性:"))
        metrics_layout.addWidget(self.completeness_bar)

        analysis_layout.addLayout(metrics_layout)
        layout.addWidget(analysis_group)

    def create_suggestions_section(self, layout):
        """创建建议区域"""
        suggestions_group = QGroupBox("💡 智能优化建议")
        suggestions_layout = QVBoxLayout(suggestions_group)

        self.suggestions_list = QListWidget()
        self.suggestions_list.setMaximumHeight(120)
        suggestions_layout.addWidget(self.suggestions_list)

        # 建议操作按钮
        suggestions_toolbar = QHBoxLayout()

        self.apply_suggestions_btn = QPushButton("✅ 应用建议")
        self.apply_suggestions_btn.clicked.connect(self.apply_suggestions)
        suggestions_toolbar.addWidget(self.apply_suggestions_btn)

        self.refresh_suggestions_btn = QPushButton("🔄 刷新建议")
        self.refresh_suggestions_btn.clicked.connect(self.refresh_suggestions)
        suggestions_toolbar.addWidget(self.refresh_suggestions_btn)

        suggestions_toolbar.addStretch()

        suggestions_layout.addLayout(suggestions_toolbar)
        layout.addWidget(suggestions_group)

    def create_generation_section(self, layout):
        """创建生成区域"""
        generation_group = QGroupBox("⚡ 智能动画生成")
        generation_layout = QVBoxLayout(generation_group)

        # 生成控制
        control_layout = QHBoxLayout()

        self.generate_btn = QPushButton("🚀 生成动画")
        self.generate_btn.clicked.connect(self.generate_animation)
        self.generate_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        control_layout.addWidget(self.generate_btn)

        control_layout.addStretch()

        self.generation_status = QLabel("就绪")
        control_layout.addWidget(self.generation_status)

        generation_layout.addLayout(control_layout)

        # 生成进度
        self.generation_progress = QProgressBar()
        self.generation_progress.setVisible(False)
        generation_layout.addWidget(self.generation_progress)

        layout.addWidget(generation_group)

    def setup_connections(self):
        """设置信号连接"""
        # 内部信号连接
        self.analysis_completed.connect(self.on_analysis_completed)
        self.suggestions_generated.connect(self.on_suggestions_generated)

    def on_description_changed(self):
        """描述文本改变事件"""
        text = self.description_edit.toPlainText()
        self.current_description = text

        # 更新字数统计
        word_count = len(text.replace(' ', ''))
        self.word_count_label.setText(f"字数: {word_count}")

        # 启用/禁用分析按钮
        self.analyze_btn.setEnabled(len(text.strip()) > 0)

    def analyze_description(self):
        """分析描述"""
        try:
            if not self.current_description.strip():
                QMessageBox.warning(self, "警告", "请先输入动画描述")
                return

            self.generation_status.setText("正在分析...")

            # 执行语义分析
            self.current_analysis = self.semantic_analyzer.analyze_description(
                self.current_description, self.current_context
            )

            # 生成智能建议
            self.current_suggestions = self.suggestion_engine.generate_suggestions(
                self.current_analysis, self.current_context
            )

            # 发送信号
            self.analysis_completed.emit({
                "analysis": self.current_analysis,
                "description": self.current_description
            })

            self.suggestions_generated.emit(self.current_suggestions)

            self.generation_status.setText("分析完成")

        except Exception as e:
            logger.error(f"分析描述失败: {e}")
            self.generation_status.setText("分析失败")
            QMessageBox.critical(self, "错误", f"分析失败: {str(e)}")

    def on_analysis_completed(self, result):
        """分析完成处理"""
        try:
            analysis = result["analysis"]

            # 更新分析显示
            analysis_text = f"主要意图: {analysis.intent_analysis.primary_intent.value}\n"
            analysis_text += f"置信度: {analysis.intent_analysis.confidence:.2f}\n"
            analysis_text += f"识别实体: {len(analysis.entities)}个\n"
            analysis_text += f"推理: {analysis.intent_analysis.reasoning}"

            self.analysis_display.setText(analysis_text)

            # 更新质量指标
            self.complexity_bar.setValue(int(analysis.complexity_score * 100))
            self.clarity_bar.setValue(int(analysis.clarity_score * 100))
            self.completeness_bar.setValue(int(analysis.completeness_score * 100))

            # 启用生成按钮
            self.generate_btn.setEnabled(True)

        except Exception as e:
            logger.error(f"处理分析结果失败: {e}")

    def on_suggestions_generated(self, suggestions):
        """建议生成处理"""
        try:
            self.suggestions_list.clear()

            for suggestion in suggestions:
                item = QListWidgetItem()
                item.setText(f"[{suggestion.get('priority', 'low').upper()}] {suggestion.get('description', '')}")
                item.setData(Qt.ItemDataRole.UserRole, suggestion)

                # 根据优先级设置颜色
                priority = suggestion.get('priority', 'low')
                if priority == 'high':
                    item.setBackground(QColor("#ffebee"))
                elif priority == 'medium':
                    item.setBackground(QColor("#fff3e0"))

                self.suggestions_list.addItem(item)

            # 启用建议按钮
            self.apply_suggestions_btn.setEnabled(len(suggestions) > 0)

        except Exception as e:
            logger.error(f"处理建议失败: {e}")

    def apply_suggestions(self):
        """应用建议"""
        try:
            # 这里可以实现建议的自动应用逻辑
            QMessageBox.information(self, "提示", "建议应用功能正在开发中")

        except Exception as e:
            logger.error(f"应用建议失败: {e}")

    def refresh_suggestions(self):
        """刷新建议"""
        if self.current_analysis:
            self.current_suggestions = self.suggestion_engine.generate_suggestions(
                self.current_analysis, self.current_context
            )
            self.suggestions_generated.emit(self.current_suggestions)

    def generate_animation(self):
        """生成动画"""
        try:
            if not self.current_analysis:
                QMessageBox.warning(self, "警告", "请先分析描述")
                return

            self.generation_status.setText("正在生成...")
            self.generation_progress.setVisible(True)
            self.generation_progress.setRange(0, 0)  # 不确定进度

            # 构建智能提示词
            enhanced_prompt = self.prompt_builder.build_intelligent_prompt(
                self.current_description,
                self.current_analysis,
                self.current_context,
                self.current_suggestions
            )

            # 发送生成信号（由外部AI服务处理）
            self.animation_generated.emit({
                "prompt": enhanced_prompt,
                "description": self.current_description,
                "analysis": self.current_analysis,
                "suggestions": self.current_suggestions
            })

            self.generation_status.setText("生成完成")
            self.generation_progress.setVisible(False)

        except Exception as e:
            logger.error(f"生成动画失败: {e}")
            self.generation_status.setText("生成失败")
            self.generation_progress.setVisible(False)
            QMessageBox.critical(self, "错误", f"生成失败: {str(e)}")

    def clear_input(self):
        """清空输入"""
        self.description_edit.clear()
        self.analysis_display.clear()
        self.suggestions_list.clear()

        # 重置状态
        self.current_description = ""
        self.current_analysis = None
        self.current_suggestions = []

        # 重置UI状态
        self.complexity_bar.setValue(0)
        self.clarity_bar.setValue(0)
        self.completeness_bar.setValue(0)
        self.generate_btn.setEnabled(False)
        self.apply_suggestions_btn.setEnabled(False)
        self.generation_status.setText("就绪")

    def update_context(self, context: Dict[str, Any]):
        """更新上下文"""
        self.current_context.update(context)
        self.context_manager.update_project_context(context.get("project", {}))
        self.context_manager.update_user_preferences(context.get("user_preferences", {}))
        self.context_updated.emit(self.current_context)

    def get_current_analysis(self) -> Optional[SemanticAnalysisResult]:
        """获取当前分析结果"""
        return self.current_analysis

    def get_current_suggestions(self) -> List[Dict[str, Any]]:
        """获取当前建议"""
        return self.current_suggestions.copy()

    def set_description(self, description: str):
        """设置描述文本"""
        self.description_edit.setPlainText(description)
        self.current_description = description


class NaturalLanguageAnimationSystem(QWidget):
    """自然语言动画系统 - 主要集成类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.semantic_analyzer = AdvancedSemanticAnalyzer()
        self.context_manager = ContextManager()
        self.suggestion_engine = IntelligentSuggestionEngine()
        self.prompt_builder = IntelligentPromptBuilder()
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 创建自然语言动画生成器组件
        self.animation_generator = NaturalLanguageAnimationGenerator()
        layout.addWidget(self.animation_generator)

        # 连接信号
        self.animation_generator.analysis_completed.connect(self.on_analysis_completed)
        self.animation_generator.suggestions_generated.connect(self.on_suggestions_generated)

    def on_analysis_completed(self, analysis_result):
        """分析完成处理"""
        logger.info("自然语言分析完成")

    def on_suggestions_generated(self, suggestions):
        """建议生成处理"""
        logger.info(f"生成了 {len(suggestions)} 个建议")

    def analyze_description(self, description: str):
        """分析描述"""
        return self.semantic_analyzer.analyze_description(description)

    def generate_suggestions(self, description: str):
        """生成建议"""
        analysis = self.analyze_description(description)
        return self.suggestion_engine.generate_suggestions(analysis)

    def build_prompt(self, description: str, context: Dict[str, Any] = None):
        """构建提示词"""
        return self.prompt_builder.build_enhanced_prompt(description, context or {})
