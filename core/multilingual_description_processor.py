"""
AI Animation Studio - 多语言描述处理器
支持多语言动画描述的处理、翻译、本地化等功能
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from core.logger import get_logger

logger = get_logger("multilingual_description")


class SupportedLanguage(Enum):
    """支持的语言"""
    CHINESE = "zh"
    ENGLISH = "en"
    JAPANESE = "ja"
    KOREAN = "ko"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"


@dataclass
class TranslationResult:
    """翻译结果"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    detected_elements: List[str]


class LanguageDetector:
    """语言检测器"""
    
    def __init__(self):
        # 语言特征模式
        self.language_patterns = {
            "zh": {
                "characters": r"[\u4e00-\u9fff]",
                "keywords": ["动画", "效果", "移动", "旋转", "缩放", "淡入", "淡出"],
                "punctuation": ["，", "。", "！", "？"]
            },
            "en": {
                "characters": r"[a-zA-Z]",
                "keywords": ["animation", "effect", "move", "rotate", "scale", "fade", "slide"],
                "punctuation": [",", ".", "!", "?"]
            },
            "ja": {
                "characters": r"[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]",
                "keywords": ["アニメーション", "効果", "移動", "回転", "拡大", "フェード"],
                "punctuation": ["、", "。", "！", "？"]
            },
            "ko": {
                "characters": r"[\uac00-\ud7af]",
                "keywords": ["애니메이션", "효과", "이동", "회전", "크기", "페이드"],
                "punctuation": [",", ".", "!", "?"]
            }
        }
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """检测文本语言"""
        try:
            if not text.strip():
                return "zh", 0.0
            
            scores = {}
            
            for lang_code, patterns in self.language_patterns.items():
                score = 0
                
                # 字符匹配
                char_matches = len(re.findall(patterns["characters"], text))
                score += char_matches * 2
                
                # 关键词匹配
                for keyword in patterns["keywords"]:
                    if keyword in text.lower():
                        score += 10
                
                # 标点符号匹配
                for punct in patterns["punctuation"]:
                    score += text.count(punct) * 1
                
                scores[lang_code] = score
            
            # 找到最高分的语言
            if scores:
                best_lang = max(scores, key=scores.get)
                max_score = scores[best_lang]
                confidence = min(1.0, max_score / (len(text) + 10))
                
                return best_lang, confidence
            
            return "zh", 0.0  # 默认中文
            
        except Exception as e:
            logger.error(f"语言检测失败: {e}")
            return "zh", 0.0


class AnimationTermTranslator:
    """动画术语翻译器"""
    
    def __init__(self):
        # 动画术语词典
        self.animation_terms = {
            "zh": {
                "actions": {
                    "移动": ["move", "移動", "이동", "mover"],
                    "旋转": ["rotate", "回転", "회전", "rotar"],
                    "缩放": ["scale", "拡大縮小", "크기조절", "escalar"],
                    "淡入": ["fade in", "フェードイン", "페이드인", "aparecer"],
                    "淡出": ["fade out", "フェードアウト", "페이드아웃", "desvanecer"],
                    "滑动": ["slide", "スライド", "슬라이드", "deslizar"],
                    "弹跳": ["bounce", "バウンス", "바운스", "rebotar"]
                },
                "properties": {
                    "透明度": ["opacity", "不透明度", "투명도", "opacidad"],
                    "位置": ["position", "位置", "위치", "posición"],
                    "大小": ["size", "サイズ", "크기", "tamaño"],
                    "颜色": ["color", "色", "색상", "color"],
                    "持续时间": ["duration", "継続時間", "지속시간", "duración"]
                },
                "directions": {
                    "左": ["left", "左", "왼쪽", "izquierda"],
                    "右": ["right", "右", "오른쪽", "derecha"],
                    "上": ["up", "上", "위", "arriba"],
                    "下": ["down", "下", "아래", "abajo"],
                    "中央": ["center", "中央", "중앙", "centro"]
                }
            }
        }
        
        # 构建反向词典
        self.reverse_terms = {}
        for source_lang, categories in self.animation_terms.items():
            for category, terms in categories.items():
                for source_term, translations in terms.items():
                    for i, translation in enumerate(translations):
                        target_langs = ["en", "ja", "ko", "es"]
                        if i < len(target_langs):
                            target_lang = target_langs[i]
                            if target_lang not in self.reverse_terms:
                                self.reverse_terms[target_lang] = {}
                            if category not in self.reverse_terms[target_lang]:
                                self.reverse_terms[target_lang][category] = {}
                            self.reverse_terms[target_lang][category][translation] = source_term
    
    def translate_animation_terms(self, text: str, source_lang: str, target_lang: str) -> str:
        """翻译动画术语"""
        try:
            if source_lang == target_lang:
                return text
            
            translated_text = text
            
            # 获取源语言术语
            source_terms = self.animation_terms.get(source_lang, {})
            
            # 翻译各类术语
            for category, terms in source_terms.items():
                for source_term, translations in terms.items():
                    if source_term in translated_text:
                        # 根据目标语言选择翻译
                        target_langs = ["en", "ja", "ko", "es", "fr", "de"]
                        lang_index = {"en": 0, "ja": 1, "ko": 2, "es": 3, "fr": 4, "de": 5}.get(target_lang, 0)
                        
                        if lang_index < len(translations):
                            target_term = translations[lang_index]
                            translated_text = translated_text.replace(source_term, target_term)
            
            return translated_text
            
        except Exception as e:
            logger.error(f"翻译动画术语失败: {e}")
            return text
    
    def get_term_suggestions(self, partial_term: str, language: str) -> List[str]:
        """获取术语建议"""
        suggestions = []
        
        try:
            partial_lower = partial_term.lower()
            
            # 从对应语言的术语中查找
            if language in self.animation_terms:
                for category, terms in self.animation_terms[language].items():
                    for term in terms.keys():
                        if partial_lower in term.lower():
                            suggestions.append(term)
            
            # 从反向词典中查找
            if language in self.reverse_terms:
                for category, terms in self.reverse_terms[language].items():
                    for term in terms.keys():
                        if partial_lower in term.lower():
                            suggestions.append(term)
            
            return list(set(suggestions))  # 去重
            
        except Exception as e:
            logger.error(f"获取术语建议失败: {e}")
            return []


class DescriptionLocalizer:
    """描述本地化器"""
    
    def __init__(self):
        # 本地化模板
        self.localization_templates = {
            "zh": {
                "greeting": "请描述您想要的动画效果",
                "examples": [
                    "一个红色的方块从左边滑入",
                    "文字逐个淡入显示",
                    "按钮带有弹跳效果"
                ],
                "tips": [
                    "描述元素的起始和结束状态",
                    "说明运动的方向和路径",
                    "指定动画的时长和节奏"
                ]
            },
            "en": {
                "greeting": "Please describe the animation effect you want",
                "examples": [
                    "A red square slides in from the left",
                    "Text fades in one by one",
                    "Button has a bounce effect"
                ],
                "tips": [
                    "Describe the start and end states of elements",
                    "Specify the direction and path of movement",
                    "Define the duration and rhythm of animation"
                ]
            },
            "ja": {
                "greeting": "希望するアニメーション効果を説明してください",
                "examples": [
                    "赤い四角が左からスライドイン",
                    "テキストが一つずつフェードイン",
                    "ボタンにバウンス効果"
                ],
                "tips": [
                    "要素の開始状態と終了状態を説明",
                    "動きの方向とパスを指定",
                    "アニメーションの時間とリズムを定義"
                ]
            }
        }
    
    def get_localized_content(self, language: str, content_type: str) -> Any:
        """获取本地化内容"""
        try:
            lang_content = self.localization_templates.get(language, self.localization_templates["zh"])
            return lang_content.get(content_type, "")
            
        except Exception as e:
            logger.error(f"获取本地化内容失败: {e}")
            return ""
    
    def localize_ui_text(self, language: str) -> Dict[str, str]:
        """本地化UI文本"""
        ui_texts = {
            "zh": {
                "description_input": "动画描述输入",
                "template_library": "模板库",
                "visual_preview": "可视预览",
                "smart_suggestions": "智能建议",
                "voice_input": "语音输入",
                "text_input": "文字输入",
                "template_input": "模板输入",
                "analyze_description": "分析描述",
                "generate_prompt": "生成Prompt",
                "optimize_prompt": "优化Prompt",
                "quality_assessment": "质量评估"
            },
            "en": {
                "description_input": "Animation Description Input",
                "template_library": "Template Library",
                "visual_preview": "Visual Preview",
                "smart_suggestions": "Smart Suggestions",
                "voice_input": "Voice Input",
                "text_input": "Text Input",
                "template_input": "Template Input",
                "analyze_description": "Analyze Description",
                "generate_prompt": "Generate Prompt",
                "optimize_prompt": "Optimize Prompt",
                "quality_assessment": "Quality Assessment"
            },
            "ja": {
                "description_input": "アニメーション説明入力",
                "template_library": "テンプレートライブラリ",
                "visual_preview": "ビジュアルプレビュー",
                "smart_suggestions": "スマート提案",
                "voice_input": "音声入力",
                "text_input": "テキスト入力",
                "template_input": "テンプレート入力",
                "analyze_description": "説明を分析",
                "generate_prompt": "プロンプト生成",
                "optimize_prompt": "プロンプト最適化",
                "quality_assessment": "品質評価"
            }
        }
        
        return ui_texts.get(language, ui_texts["zh"])


class MultilingualDescriptionProcessor:
    """多语言描述处理器"""
    
    def __init__(self):
        self.language_detector = LanguageDetector()
        self.term_translator = AnimationTermTranslator()
        self.localizer = DescriptionLocalizer()
        
        self.current_language = "zh"
        self.supported_languages = [lang.value for lang in SupportedLanguage]
        
        logger.info("多语言描述处理器初始化完成")
    
    def process_description(self, description: str, target_language: str = None) -> Dict[str, Any]:
        """处理多语言描述"""
        try:
            # 检测语言
            detected_lang, confidence = self.language_detector.detect_language(description)
            
            # 确定目标语言
            if target_language is None:
                target_language = self.current_language
            
            result = {
                "original_text": description,
                "detected_language": detected_lang,
                "detection_confidence": confidence,
                "target_language": target_language,
                "processed_text": description,
                "translation_needed": detected_lang != target_language,
                "extracted_terms": [],
                "localized_suggestions": []
            }
            
            # 提取动画术语
            result["extracted_terms"] = self.extract_animation_terms(description, detected_lang)
            
            # 如果需要翻译
            if result["translation_needed"]:
                translated_text = self.term_translator.translate_animation_terms(
                    description, detected_lang, target_language
                )
                result["processed_text"] = translated_text
            
            # 获取本地化建议
            result["localized_suggestions"] = self.get_localized_suggestions(target_language)
            
            return result
            
        except Exception as e:
            logger.error(f"处理多语言描述失败: {e}")
            return {"error": str(e)}
    
    def extract_animation_terms(self, text: str, language: str) -> List[Dict[str, str]]:
        """提取动画术语"""
        terms = []
        
        try:
            # 获取该语言的术语
            lang_terms = self.term_translator.animation_terms.get(language, {})
            
            for category, term_dict in lang_terms.items():
                for term in term_dict.keys():
                    if term in text:
                        terms.append({
                            "term": term,
                            "category": category,
                            "language": language
                        })
            
        except Exception as e:
            logger.error(f"提取动画术语失败: {e}")
        
        return terms
    
    def get_localized_suggestions(self, language: str) -> List[str]:
        """获取本地化建议"""
        try:
            examples = self.localizer.get_localized_content(language, "examples")
            return examples if isinstance(examples, list) else []
            
        except Exception as e:
            logger.error(f"获取本地化建议失败: {e}")
            return []
    
    def normalize_description(self, description: str, language: str) -> str:
        """标准化描述"""
        try:
            normalized = description.strip()
            
            # 语言特定的标准化
            if language == "zh":
                # 中文标准化
                normalized = re.sub(r'\s+', '', normalized)  # 移除多余空格
                normalized = normalized.replace("，，", "，")  # 移除重复逗号
                normalized = normalized.replace("。。", "。")  # 移除重复句号
                
            elif language == "en":
                # 英文标准化
                normalized = re.sub(r'\s+', ' ', normalized)  # 标准化空格
                normalized = normalized.replace(" ,", ",")  # 修复逗号前空格
                normalized = normalized.replace(" .", ".")  # 修复句号前空格
                
            elif language == "ja":
                # 日文标准化
                normalized = re.sub(r'\s+', '', normalized)  # 移除空格
                normalized = normalized.replace("、、", "、")  # 移除重复顿号
                
            return normalized
            
        except Exception as e:
            logger.error(f"标准化描述失败: {e}")
            return description
    
    def validate_multilingual_description(self, description: str, language: str) -> Dict[str, Any]:
        """验证多语言描述"""
        validation = {
            "is_valid": True,
            "issues": [],
            "suggestions": [],
            "language_specific_tips": []
        }
        
        try:
            # 基本验证
            if not description.strip():
                validation["is_valid"] = False
                validation["issues"].append("描述不能为空")
                return validation
            
            # 语言特定验证
            if language == "zh":
                # 中文验证
                if len(description) < 10:
                    validation["suggestions"].append("建议描述更详细一些")
                
                # 检查是否包含动画相关词汇
                animation_keywords = ["动画", "效果", "移动", "旋转", "缩放"]
                if not any(keyword in description for keyword in animation_keywords):
                    validation["suggestions"].append("建议添加具体的动画动作描述")
                
                validation["language_specific_tips"] = [
                    "使用具体的动作词汇，如'滑动'、'旋转'、'淡入'等",
                    "描述元素的起始和结束状态",
                    "可以添加时间和速度的描述"
                ]
                
            elif language == "en":
                # 英文验证
                if len(description.split()) < 5:
                    validation["suggestions"].append("Consider adding more details to the description")
                
                animation_keywords = ["animation", "effect", "move", "rotate", "scale", "fade"]
                if not any(keyword in description.lower() for keyword in animation_keywords):
                    validation["suggestions"].append("Consider adding specific animation action words")
                
                validation["language_specific_tips"] = [
                    "Use specific action verbs like 'slide', 'rotate', 'fade in', etc.",
                    "Describe the initial and final states of elements",
                    "Include timing and speed descriptions"
                ]
            
            # 通用建议
            if "时间" not in description and "second" not in description.lower():
                validation["suggestions"].append("建议添加时间信息")
            
        except Exception as e:
            logger.error(f"验证多语言描述失败: {e}")
            validation["issues"].append(f"验证过程出错: {str(e)}")
        
        return validation
    
    def get_language_specific_templates(self, language: str) -> List[Dict[str, Any]]:
        """获取语言特定的模板"""
        templates = {
            "zh": [
                {
                    "name": "基础淡入",
                    "description": "元素从透明状态逐渐显示",
                    "category": "入场动画"
                },
                {
                    "name": "滑动进入",
                    "description": "元素从一侧滑入视图",
                    "category": "移动动画"
                },
                {
                    "name": "弹跳效果",
                    "description": "元素带有弹性的跳跃动画",
                    "category": "特效动画"
                }
            ],
            "en": [
                {
                    "name": "Basic Fade In",
                    "description": "Element gradually appears from transparent state",
                    "category": "Entrance Animation"
                },
                {
                    "name": "Slide In",
                    "description": "Element slides into view from one side",
                    "category": "Movement Animation"
                },
                {
                    "name": "Bounce Effect",
                    "description": "Element has elastic bouncing animation",
                    "category": "Effect Animation"
                }
            ],
            "ja": [
                {
                    "name": "基本フェードイン",
                    "description": "要素が透明状態から徐々に表示される",
                    "category": "入場アニメーション"
                },
                {
                    "name": "スライドイン",
                    "description": "要素が一方からビューにスライドする",
                    "category": "移動アニメーション"
                },
                {
                    "name": "バウンス効果",
                    "description": "要素が弾性のあるジャンプアニメーション",
                    "category": "エフェクトアニメーション"
                }
            ]
        }
        
        return templates.get(language, templates["zh"])
    
    def convert_to_universal_format(self, description: str, source_language: str) -> Dict[str, Any]:
        """转换为通用格式"""
        try:
            # 提取结构化信息
            universal_format = {
                "elements": [],
                "actions": [],
                "properties": {},
                "timing": {},
                "style": {},
                "source_language": source_language,
                "original_description": description
            }
            
            # 提取动画术语
            extracted_terms = self.extract_animation_terms(description, source_language)
            
            for term_info in extracted_terms:
                category = term_info["category"]
                term = term_info["term"]
                
                if category == "actions":
                    universal_format["actions"].append(term)
                elif category == "properties":
                    universal_format["properties"][term] = True
                elif category == "directions":
                    universal_format["properties"]["direction"] = term
            
            # 提取时间信息
            time_patterns = {
                "zh": r"(\d+(?:\.\d+)?)\s*秒",
                "en": r"(\d+(?:\.\d+)?)\s*seconds?",
                "ja": r"(\d+(?:\.\d+)?)\s*秒"
            }
            
            pattern = time_patterns.get(source_language, time_patterns["zh"])
            time_matches = re.findall(pattern, description)
            
            if time_matches:
                universal_format["timing"]["duration"] = float(time_matches[0])
            
            return universal_format
            
        except Exception as e:
            logger.error(f"转换为通用格式失败: {e}")
            return {}
    
    def set_current_language(self, language: str):
        """设置当前语言"""
        if language in self.supported_languages:
            self.current_language = language
            logger.info(f"当前语言已设置为: {language}")
        else:
            logger.warning(f"不支持的语言: {language}")
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """获取支持的语言列表"""
        languages = [
            {"code": "zh", "name": "中文", "native_name": "中文"},
            {"code": "en", "name": "English", "native_name": "English"},
            {"code": "ja", "name": "Japanese", "native_name": "日本語"},
            {"code": "ko", "name": "Korean", "native_name": "한국어"},
            {"code": "es", "name": "Spanish", "native_name": "Español"},
            {"code": "fr", "name": "French", "native_name": "Français"},
            {"code": "de", "name": "German", "native_name": "Deutsch"}
        ]
        
        return languages
