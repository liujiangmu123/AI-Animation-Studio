"""
AI Animation Studio - 智能描述补全系统
提供实时的动画描述智能补全、语法检查、上下文感知等功能
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from PyQt6.QtWidgets import QCompleter
from PyQt6.QtCore import Qt, QAbstractListModel, QModelIndex, pyqtSignal, QStringListModel

from core.logger import get_logger

logger = get_logger("smart_description_completer")


@dataclass
class CompletionSuggestion:
    """补全建议"""
    text: str
    description: str
    category: str
    confidence: float
    context_match: bool = False


class AnimationVocabulary:
    """动画词汇库"""
    
    def __init__(self):
        self.vocabulary = {
            "动作词汇": {
                "基础动作": ["移动", "滑动", "飞行", "跳跃", "弹跳", "滚动", "漂浮", "下降", "上升"],
                "旋转动作": ["旋转", "转动", "自转", "公转", "翻转", "翻滚", "摇摆", "摆动"],
                "变形动作": ["缩放", "放大", "缩小", "拉伸", "压缩", "扭曲", "变形", "弯曲"],
                "显隐动作": ["淡入", "淡出", "出现", "消失", "显示", "隐藏", "闪烁", "闪现"]
            },
            "方向词汇": {
                "基本方向": ["左", "右", "上", "下", "前", "后", "中央", "中心"],
                "复合方向": ["左上", "右上", "左下", "右下", "斜向", "对角"],
                "相对方向": ["向内", "向外", "顺时针", "逆时针", "垂直", "水平"]
            },
            "时间词汇": {
                "速度描述": ["快速", "缓慢", "瞬间", "逐渐", "突然", "平稳", "急速", "温和"],
                "时间关系": ["同时", "依次", "交错", "延迟", "提前", "同步", "异步"],
                "持续性": ["持续", "间歇", "循环", "重复", "一次性", "连续", "断续"]
            },
            "视觉词汇": {
                "颜色变化": ["变色", "渐变", "闪光", "发光", "变亮", "变暗", "彩虹", "单色"],
                "透明度": ["透明", "半透明", "不透明", "模糊", "清晰", "朦胧"],
                "阴影光效": ["阴影", "光晕", "高光", "反光", "投影", "光束", "光斑"]
            },
            "物理词汇": {
                "力学效果": ["弹性", "重力", "摩擦", "惯性", "反弹", "碰撞", "震动"],
                "材质感觉": ["柔软", "坚硬", "液体", "气体", "金属", "玻璃", "橡胶"]
            },
            "情感词汇": {
                "情绪表达": ["欢快", "忧郁", "激动", "平静", "紧张", "放松", "神秘"],
                "风格特征": ["现代", "复古", "科技", "自然", "简约", "华丽", "可爱", "酷炫"]
            }
        }
        
        # 构建扁平化词汇列表
        self.flat_vocabulary = []
        for category, subcategories in self.vocabulary.items():
            for subcategory, words in subcategories.items():
                for word in words:
                    self.flat_vocabulary.append({
                        "word": word,
                        "category": category,
                        "subcategory": subcategory
                    })
    
    def get_words_by_category(self, category: str) -> List[str]:
        """按分类获取词汇"""
        words = []
        for item in self.flat_vocabulary:
            if item["category"] == category:
                words.append(item["word"])
        return words
    
    def search_words(self, query: str) -> List[Dict[str, str]]:
        """搜索词汇"""
        results = []
        query_lower = query.lower()
        
        for item in self.flat_vocabulary:
            if query_lower in item["word"].lower():
                results.append(item)
        
        return results


class ContextAnalyzer:
    """上下文分析器"""
    
    def __init__(self):
        # 上下文模式
        self.context_patterns = {
            "动作序列": r"(然后|接着|随后|之后|同时)",
            "时间描述": r"(\d+秒|\d+毫秒|快速|缓慢|瞬间)",
            "位置描述": r"(从.*到|在.*位置|向.*方向)",
            "效果描述": r"(带有.*效果|具有.*特征|呈现.*状态)"
        }
        
        # 补全规则
        self.completion_rules = {
            "动作后缀": {
                "移动": ["到中央", "到右侧", "到左侧", "向上", "向下"],
                "旋转": ["360度", "180度", "90度", "一圈", "半圈"],
                "缩放": ["到原来的2倍", "到50%", "放大", "缩小"],
                "淡入": ["显示", "出现", "展现"],
                "淡出": ["消失", "隐藏", "退场"]
            },
            "时间补全": {
                "持续": ["1秒", "2秒", "3秒", "0.5秒"],
                "延迟": ["0.5秒后", "1秒后", "同时"],
                "速度": ["快速地", "缓慢地", "平稳地", "突然"]
            },
            "效果补全": {
                "带有": ["弹性效果", "阴影效果", "发光效果", "渐变效果"],
                "具有": ["科技感", "现代感", "立体感", "动感"],
                "呈现": ["流畅的", "自然的", "优雅的", "动感的"]
            }
        }
    
    def analyze_context(self, text: str, cursor_position: int) -> Dict[str, Any]:
        """分析上下文"""
        context = {
            "preceding_text": text[:cursor_position],
            "following_text": text[cursor_position:],
            "current_sentence": self.extract_current_sentence(text, cursor_position),
            "detected_patterns": [],
            "suggested_completions": []
        }
        
        # 检测上下文模式
        for pattern_name, pattern in self.context_patterns.items():
            matches = re.findall(pattern, context["preceding_text"])
            if matches:
                context["detected_patterns"].append({
                    "pattern": pattern_name,
                    "matches": matches
                })
        
        return context
    
    def extract_current_sentence(self, text: str, cursor_position: int) -> str:
        """提取当前句子"""
        # 向前查找句子开始
        start = cursor_position
        while start > 0 and text[start-1] not in "。！？\n":
            start -= 1
        
        # 向后查找句子结束
        end = cursor_position
        while end < len(text) and text[end] not in "。！？\n":
            end += 1
        
        return text[start:end].strip()
    
    def get_contextual_suggestions(self, context: Dict[str, Any]) -> List[CompletionSuggestion]:
        """获取上下文相关的建议"""
        suggestions = []
        
        try:
            preceding_text = context["preceding_text"].lower()
            
            # 基于前置文本生成建议
            for rule_category, rules in self.completion_rules.items():
                for trigger, completions in rules.items():
                    if trigger in preceding_text:
                        for completion in completions:
                            suggestion = CompletionSuggestion(
                                text=completion,
                                description=f"{rule_category}建议",
                                category=rule_category,
                                confidence=0.8,
                                context_match=True
                            )
                            suggestions.append(suggestion)
            
            # 根据检测到的模式生成建议
            for pattern_info in context["detected_patterns"]:
                pattern_name = pattern_info["pattern"]
                
                if pattern_name == "动作序列":
                    # 建议后续动作
                    action_suggestions = ["然后停留", "接着旋转", "随后淡出", "最后消失"]
                    for action in action_suggestions:
                        suggestion = CompletionSuggestion(
                            text=action,
                            description="动作序列建议",
                            category="动作序列",
                            confidence=0.7
                        )
                        suggestions.append(suggestion)
                
                elif pattern_name == "位置描述":
                    # 建议位置补全
                    position_suggestions = ["中央位置", "屏幕边缘", "视图中心", "角落位置"]
                    for position in position_suggestions:
                        suggestion = CompletionSuggestion(
                            text=position,
                            description="位置描述建议",
                            category="位置描述",
                            confidence=0.6
                        )
                        suggestions.append(suggestion)
            
            # 按置信度排序
            suggestions.sort(key=lambda x: x.confidence, reverse=True)
            
        except Exception as e:
            logger.error(f"获取上下文建议失败: {e}")
        
        return suggestions[:10]  # 返回前10个建议


class SmartDescriptionCompleter(QCompleter):
    """智能描述补全器"""
    
    suggestion_selected = pyqtSignal(str, str)  # text, description
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.vocabulary = AnimationVocabulary()
        self.context_analyzer = ContextAnalyzer()
        self.completion_history = []
        
        # 设置补全模式
        self.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setMaxVisibleItems(10)
        
        # 初始化词汇模型
        self.update_vocabulary_model()
        
        logger.info("智能描述补全器初始化完成")
    
    def update_vocabulary_model(self):
        """更新词汇模型"""
        try:
            # 获取所有词汇
            all_words = [item["word"] for item in self.vocabulary.flat_vocabulary]
            
            # 添加常用短语
            common_phrases = [
                "从左侧滑入", "向右移动", "旋转360度", "缓慢淡入",
                "快速弹跳", "优雅地出现", "带有阴影效果", "具有科技感",
                "持续2秒", "延迟0.5秒", "同时进行", "依次执行"
            ]
            
            all_words.extend(common_phrases)
            
            # 设置模型
            model = QStringListModel(all_words)
            self.setModel(model)
            
        except Exception as e:
            logger.error(f"更新词汇模型失败: {e}")
    
    def get_smart_completions(self, text: str, cursor_position: int) -> List[CompletionSuggestion]:
        """获取智能补全建议"""
        try:
            # 分析上下文
            context = self.context_analyzer.analyze_context(text, cursor_position)
            
            # 获取上下文相关建议
            contextual_suggestions = self.context_analyzer.get_contextual_suggestions(context)
            
            # 获取词汇建议
            current_word = self.extract_current_word(text, cursor_position)
            vocabulary_suggestions = self.get_vocabulary_suggestions(current_word)
            
            # 合并建议
            all_suggestions = contextual_suggestions + vocabulary_suggestions
            
            # 去重并排序
            unique_suggestions = self.deduplicate_suggestions(all_suggestions)
            
            return unique_suggestions[:10]
            
        except Exception as e:
            logger.error(f"获取智能补全失败: {e}")
            return []
    
    def extract_current_word(self, text: str, cursor_position: int) -> str:
        """提取当前单词"""
        # 向前查找单词开始
        start = cursor_position
        while start > 0 and text[start-1] not in " \t\n，。！？":
            start -= 1
        
        # 向后查找单词结束
        end = cursor_position
        while end < len(text) and text[end] not in " \t\n，。！？":
            end += 1
        
        return text[start:end].strip()
    
    def get_vocabulary_suggestions(self, partial_word: str) -> List[CompletionSuggestion]:
        """获取词汇建议"""
        suggestions = []
        
        if not partial_word:
            return suggestions
        
        try:
            # 搜索匹配的词汇
            matching_words = self.vocabulary.search_words(partial_word)
            
            for word_info in matching_words:
                suggestion = CompletionSuggestion(
                    text=word_info["word"],
                    description=f"{word_info['category']} - {word_info['subcategory']}",
                    category=word_info["category"],
                    confidence=0.5
                )
                suggestions.append(suggestion)
            
        except Exception as e:
            logger.error(f"获取词汇建议失败: {e}")
        
        return suggestions
    
    def deduplicate_suggestions(self, suggestions: List[CompletionSuggestion]) -> List[CompletionSuggestion]:
        """去重建议"""
        seen_texts = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            if suggestion.text not in seen_texts:
                seen_texts.add(suggestion.text)
                unique_suggestions.append(suggestion)
        
        # 按置信度和上下文匹配排序
        unique_suggestions.sort(key=lambda x: (x.context_match, x.confidence), reverse=True)
        
        return unique_suggestions
    
    def learn_from_completion(self, completed_text: str, selected_suggestion: str):
        """从补全中学习"""
        try:
            # 记录补全历史
            completion_record = {
                "original_text": completed_text,
                "selected_suggestion": selected_suggestion,
                "timestamp": str(datetime.now())
            }
            
            self.completion_history.append(completion_record)
            
            # 保持历史记录在合理范围内
            if len(self.completion_history) > 1000:
                self.completion_history = self.completion_history[-500:]
            
            logger.debug(f"学习补全记录: {selected_suggestion}")
            
        except Exception as e:
            logger.error(f"学习补全失败: {e}")
    
    def get_completion_statistics(self) -> Dict[str, Any]:
        """获取补全统计"""
        try:
            if not self.completion_history:
                return {}
            
            # 统计最常用的建议
            suggestion_counts = {}
            for record in self.completion_history:
                suggestion = record["selected_suggestion"]
                suggestion_counts[suggestion] = suggestion_counts.get(suggestion, 0) + 1
            
            # 排序
            sorted_suggestions = sorted(suggestion_counts.items(), key=lambda x: x[1], reverse=True)
            
            return {
                "total_completions": len(self.completion_history),
                "most_used_suggestions": sorted_suggestions[:10],
                "completion_rate": len(self.completion_history) / max(1, len(self.completion_history))
            }
            
        except Exception as e:
            logger.error(f"获取补全统计失败: {e}")
            return {}


class DescriptionValidator:
    """描述验证器"""
    
    def __init__(self):
        # 验证规则
        self.validation_rules = {
            "completeness": {
                "required_elements": ["动作", "对象", "效果"],
                "optional_elements": ["时间", "方向", "风格"]
            },
            "clarity": {
                "ambiguous_words": ["那个", "这个", "某种", "一些"],
                "vague_descriptions": ["好看的", "不错的", "合适的"]
            },
            "technical": {
                "performance_keywords": ["流畅", "性能", "优化", "兼容"],
                "implementation_hints": ["CSS", "JavaScript", "SVG", "Canvas"]
            }
        }
    
    def validate_description(self, description: str) -> Dict[str, Any]:
        """验证描述质量"""
        validation_result = {
            "score": 0,
            "issues": [],
            "suggestions": [],
            "strengths": []
        }
        
        try:
            desc_lower = description.lower()
            
            # 完整性检查
            completeness_score = self.check_completeness(description)
            validation_result["score"] += completeness_score
            
            if completeness_score >= 30:
                validation_result["strengths"].append("描述要素完整")
            else:
                validation_result["issues"].append("描述要素不够完整")
                validation_result["suggestions"].append("建议添加更多动画细节")
            
            # 清晰度检查
            clarity_score = self.check_clarity(description)
            validation_result["score"] += clarity_score
            
            if clarity_score >= 25:
                validation_result["strengths"].append("描述清晰明确")
            else:
                validation_result["issues"].append("描述存在模糊表达")
                validation_result["suggestions"].append("建议使用更具体的描述词汇")
            
            # 技术性检查
            technical_score = self.check_technical_aspects(description)
            validation_result["score"] += technical_score
            
            if technical_score >= 20:
                validation_result["strengths"].append("包含技术实现提示")
            else:
                validation_result["suggestions"].append("建议添加技术实现要求")
            
            # 长度检查
            length_score = self.check_length(description)
            validation_result["score"] += length_score
            
            # 确保分数在0-100之间
            validation_result["score"] = min(100, max(0, validation_result["score"]))
            
        except Exception as e:
            logger.error(f"验证描述失败: {e}")
            validation_result["issues"].append(f"验证过程出错: {str(e)}")
        
        return validation_result
    
    def check_completeness(self, description: str) -> int:
        """检查完整性"""
        score = 0
        desc_lower = description.lower()
        
        # 检查必需元素
        required_elements = self.validation_rules["completeness"]["required_elements"]
        
        # 动作检查
        action_keywords = ["移动", "旋转", "缩放", "淡入", "淡出", "弹跳", "滑动"]
        if any(keyword in desc_lower for keyword in action_keywords):
            score += 15
        
        # 对象检查
        object_keywords = ["元素", "按钮", "文字", "图片", "方块", "圆形", "卡片"]
        if any(keyword in desc_lower for keyword in object_keywords):
            score += 10
        
        # 效果检查
        effect_keywords = ["效果", "动画", "过渡", "变化", "转换"]
        if any(keyword in desc_lower for keyword in effect_keywords):
            score += 5
        
        return score
    
    def check_clarity(self, description: str) -> int:
        """检查清晰度"""
        score = 25  # 基础分数
        desc_lower = description.lower()
        
        # 检查模糊词汇
        ambiguous_words = self.validation_rules["clarity"]["ambiguous_words"]
        ambiguous_count = sum(1 for word in ambiguous_words if word in desc_lower)
        score -= ambiguous_count * 5
        
        # 检查具体性
        specific_keywords = ["像素", "度", "秒", "毫秒", "倍", "%"]
        specific_count = sum(1 for keyword in specific_keywords if keyword in desc_lower)
        score += specific_count * 3
        
        return max(0, score)
    
    def check_technical_aspects(self, description: str) -> int:
        """检查技术方面"""
        score = 0
        desc_lower = description.lower()
        
        # 性能关键词
        performance_keywords = self.validation_rules["technical"]["performance_keywords"]
        performance_count = sum(1 for keyword in performance_keywords if keyword in desc_lower)
        score += performance_count * 5
        
        # 实现提示
        implementation_keywords = self.validation_rules["technical"]["implementation_hints"]
        implementation_count = sum(1 for keyword in implementation_keywords if keyword in desc_lower)
        score += implementation_count * 8
        
        return score
    
    def check_length(self, description: str) -> int:
        """检查长度"""
        length = len(description)
        
        if 50 <= length <= 300:
            return 15
        elif 30 <= length <= 500:
            return 10
        elif length >= 20:
            return 5
        else:
            return 0
    
    def get_improvement_suggestions(self, validation_result: Dict[str, Any]) -> List[str]:
        """获取改进建议"""
        suggestions = []
        
        score = validation_result["score"]
        
        if score < 50:
            suggestions.append("🔴 描述质量较低，建议重新组织语言")
        elif score < 75:
            suggestions.append("🟡 描述质量中等，可以进一步优化")
        else:
            suggestions.append("🟢 描述质量良好")
        
        # 添加具体建议
        suggestions.extend(validation_result.get("suggestions", []))
        
        return suggestions


class DescriptionEnhancer:
    """描述增强器"""
    
    def __init__(self):
        # 增强规则
        self.enhancement_rules = {
            "time_enhancement": {
                "patterns": [r"快速", r"缓慢", r"瞬间"],
                "replacements": {
                    "快速": "在0.5秒内快速",
                    "缓慢": "在3秒内缓慢",
                    "瞬间": "在0.1秒内瞬间"
                }
            },
            "effect_enhancement": {
                "patterns": [r"移动", r"旋转", r"缩放"],
                "additions": {
                    "移动": "，带有平滑的缓动效果",
                    "旋转": "，保持中心点稳定",
                    "缩放": "，保持宽高比例"
                }
            },
            "style_enhancement": {
                "generic_styles": ["好看", "漂亮", "美观"],
                "specific_styles": ["现代简约风格", "科技感设计", "优雅的视觉效果"]
            }
        }
    
    def enhance_description(self, description: str, enhancement_level: str = "moderate") -> str:
        """增强描述"""
        try:
            enhanced = description
            
            if enhancement_level == "minimal":
                # 最小增强，只修复明显问题
                enhanced = self.fix_basic_issues(enhanced)
            
            elif enhancement_level == "moderate":
                # 中等增强，添加必要细节
                enhanced = self.fix_basic_issues(enhanced)
                enhanced = self.add_technical_details(enhanced)
                enhanced = self.improve_clarity(enhanced)
            
            elif enhancement_level == "comprehensive":
                # 全面增强，最大化描述质量
                enhanced = self.fix_basic_issues(enhanced)
                enhanced = self.add_technical_details(enhanced)
                enhanced = self.improve_clarity(enhanced)
                enhanced = self.add_creative_elements(enhanced)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"增强描述失败: {e}")
            return description
    
    def fix_basic_issues(self, description: str) -> str:
        """修复基本问题"""
        # 移除多余空格
        fixed = re.sub(r'\s+', ' ', description).strip()
        
        # 确保句子以标点结尾
        if fixed and fixed[-1] not in "。！？":
            fixed += "。"
        
        return fixed
    
    def add_technical_details(self, description: str) -> str:
        """添加技术细节"""
        enhanced = description
        
        # 如果没有时间信息，添加默认时间
        if not re.search(r'\d+秒|\d+毫秒', enhanced):
            enhanced += "，动画持续2秒"
        
        # 如果没有缓动信息，添加缓动描述
        if "缓动" not in enhanced and "ease" not in enhanced.lower():
            enhanced += "，使用平滑的缓动效果"
        
        return enhanced
    
    def improve_clarity(self, description: str) -> str:
        """提高清晰度"""
        enhanced = description
        
        # 替换模糊词汇
        replacements = {
            "那个": "目标",
            "这个": "当前",
            "好看的": "视觉吸引人的",
            "不错的": "高质量的"
        }
        
        for vague, specific in replacements.items():
            enhanced = enhanced.replace(vague, specific)
        
        return enhanced
    
    def add_creative_elements(self, description: str) -> str:
        """添加创意元素"""
        enhanced = description
        
        # 如果描述较短，添加创意细节
        if len(enhanced) < 100:
            creative_additions = [
                "，配合微妙的阴影变化",
                "，呈现出立体的视觉层次",
                "，营造出现代科技的氛围"
            ]
            
            import random
            enhanced += random.choice(creative_additions)
        
        return enhanced
