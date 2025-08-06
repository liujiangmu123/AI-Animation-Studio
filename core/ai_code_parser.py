"""
AI Animation Studio - AI代码解析器
解析AI生成的HTML/CSS/JS代码，提取动画元素和属性
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup
import cssutils
import logging

from core.data_structures import Element, AnimationType, TechStack, ElementType, Point, ElementStyle
from core.logger import get_logger

# 禁用cssutils的警告日志
cssutils.log.setLevel(logging.ERROR)

logger = get_logger("ai_code_parser")


@dataclass
class ParsedAnimation:
    """解析的动画数据"""
    element_id: str
    element_type: str
    animation_name: str
    animation_type: AnimationType
    duration: float
    delay: float
    easing: str
    properties: Dict[str, Any]
    keyframes: List[Dict[str, Any]]


@dataclass
class ParsedElement:
    """解析的元素数据"""
    tag: str
    id: str
    classes: List[str]
    content: str
    styles: Dict[str, str]
    attributes: Dict[str, str]
    animations: List[ParsedAnimation]


class AICodeParser:
    """AI代码解析器"""
    
    def __init__(self):
        # CSS动画属性映射
        self.animation_properties = {
            'animation-name': 'name',
            'animation-duration': 'duration',
            'animation-delay': 'delay',
            'animation-timing-function': 'easing',
            'animation-iteration-count': 'iteration_count',
            'animation-direction': 'direction',
            'animation-fill-mode': 'fill_mode'
        }
        
        # 动画类型映射
        self.animation_type_map = {
            'fade': AnimationType.FADE_IN,
            'slide': AnimationType.SLIDE_IN,
            'scale': AnimationType.SCALE,
            'rotate': AnimationType.ROTATE,
            'bounce': AnimationType.BOUNCE,
            'flip': AnimationType.FLIP
        }
        
        logger.info("AI代码解析器初始化完成")
    
    def parse_ai_generated_code(self, html_code: str) -> Dict[str, Any]:
        """解析AI生成的代码"""
        try:
            result = {
                "elements": [],
                "animations": [],
                "styles": {},
                "scripts": "",
                "metadata": {}
            }
            
            # 解析HTML结构
            soup = BeautifulSoup(html_code, 'html.parser')
            
            # 提取CSS样式
            css_content = self.extract_css_content(soup)
            if css_content:
                result["styles"] = self.parse_css_styles(css_content)
                result["animations"] = self.parse_css_animations(css_content)
            
            # 提取JavaScript
            js_content = self.extract_js_content(soup)
            if js_content:
                result["scripts"] = js_content
                result["animations"].extend(self.parse_js_animations(js_content))
            
            # 解析HTML元素
            body = soup.find('body') or soup
            result["elements"] = self.parse_html_elements(body)
            
            # 生成元数据
            result["metadata"] = self.generate_metadata(result)
            
            logger.info(f"AI代码解析完成: {len(result['elements'])} 个元素, {len(result['animations'])} 个动画")
            
            return result
            
        except Exception as e:
            logger.error(f"解析AI代码失败: {e}")
            return {"error": str(e)}
    
    def extract_css_content(self, soup: BeautifulSoup) -> str:
        """提取CSS内容"""
        css_content = ""
        
        # 从<style>标签提取
        for style_tag in soup.find_all('style'):
            css_content += style_tag.get_text() + "\n"
        
        # 从内联样式提取（转换为CSS规则）
        inline_styles = {}
        for element in soup.find_all(attrs={"style": True}):
            element_id = element.get('id') or f"element_{id(element)}"
            inline_styles[element_id] = element.get('style')
        
        # 转换内联样式为CSS规则
        for element_id, style in inline_styles.items():
            css_content += f"#{element_id} {{ {style} }}\n"
        
        return css_content
    
    def extract_js_content(self, soup: BeautifulSoup) -> str:
        """提取JavaScript内容"""
        js_content = ""
        
        for script_tag in soup.find_all('script'):
            if script_tag.get('src'):
                # 外部脚本，记录引用
                js_content += f"// 外部脚本: {script_tag.get('src')}\n"
            else:
                # 内联脚本
                js_content += script_tag.get_text() + "\n"
        
        return js_content
    
    def parse_css_styles(self, css_content: str) -> Dict[str, Dict[str, str]]:
        """解析CSS样式"""
        styles = {}
        
        try:
            sheet = cssutils.parseString(css_content)
            
            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    selector = rule.selectorText
                    properties = {}
                    
                    for prop in rule.style:
                        properties[prop.name] = prop.value
                    
                    styles[selector] = properties
                    
        except Exception as e:
            logger.error(f"解析CSS样式失败: {e}")
        
        return styles
    
    def parse_css_animations(self, css_content: str) -> List[ParsedAnimation]:
        """解析CSS动画"""
        animations = []
        
        try:
            # 解析@keyframes规则
            keyframes_pattern = r'@keyframes\s+(\w+)\s*\{([^}]+)\}'
            keyframes_matches = re.findall(keyframes_pattern, css_content, re.DOTALL)
            
            keyframes_data = {}
            for name, content in keyframes_matches:
                keyframes_data[name] = self.parse_keyframes_content(content)
            
            # 解析animation属性
            animation_pattern = r'animation\s*:\s*([^;]+);'
            animation_matches = re.findall(animation_pattern, css_content)
            
            for i, animation_value in enumerate(animation_matches):
                animation = self.parse_animation_value(animation_value, keyframes_data)
                if animation:
                    animation.element_id = f"element_{i}"
                    animations.append(animation)
                    
        except Exception as e:
            logger.error(f"解析CSS动画失败: {e}")
        
        return animations
    
    def parse_keyframes_content(self, content: str) -> List[Dict[str, Any]]:
        """解析关键帧内容"""
        keyframes = []
        
        try:
            # 解析关键帧规则
            frame_pattern = r'(\d+%|from|to)\s*\{([^}]+)\}'
            frame_matches = re.findall(frame_pattern, content)
            
            for percentage, properties in frame_matches:
                # 转换百分比
                if percentage == 'from':
                    percent = 0
                elif percentage == 'to':
                    percent = 100
                else:
                    percent = int(percentage.replace('%', ''))
                
                # 解析属性
                props = {}
                prop_pattern = r'(\w+(?:-\w+)*)\s*:\s*([^;]+);?'
                prop_matches = re.findall(prop_pattern, properties)
                
                for prop_name, prop_value in prop_matches:
                    props[prop_name] = prop_value.strip()
                
                keyframes.append({
                    "percentage": percent,
                    "properties": props
                })
                
        except Exception as e:
            logger.error(f"解析关键帧内容失败: {e}")
        
        return keyframes
    
    def parse_animation_value(self, animation_value: str, keyframes_data: Dict[str, List]) -> Optional[ParsedAnimation]:
        """解析animation属性值"""
        try:
            # 简化解析，实际应该更复杂
            parts = animation_value.strip().split()
            
            if not parts:
                return None
            
            animation_name = parts[0]
            duration = self.parse_duration(parts[1] if len(parts) > 1 else "1s")
            easing = parts[2] if len(parts) > 2 else "ease"
            delay = self.parse_duration(parts[3] if len(parts) > 3 else "0s")
            
            # 确定动画类型
            animation_type = self.determine_animation_type(animation_name, keyframes_data.get(animation_name, []))
            
            return ParsedAnimation(
                element_id="",
                element_type="div",
                animation_name=animation_name,
                animation_type=animation_type,
                duration=duration,
                delay=delay,
                easing=easing,
                properties={},
                keyframes=keyframes_data.get(animation_name, [])
            )
            
        except Exception as e:
            logger.error(f"解析动画值失败: {e}")
            return None
    
    def parse_duration(self, duration_str: str) -> float:
        """解析持续时间"""
        try:
            if duration_str.endswith('s'):
                return float(duration_str[:-1])
            elif duration_str.endswith('ms'):
                return float(duration_str[:-2]) / 1000
            else:
                return float(duration_str)
        except:
            return 1.0
    
    def determine_animation_type(self, animation_name: str, keyframes: List[Dict[str, Any]]) -> AnimationType:
        """确定动画类型"""
        name_lower = animation_name.lower()
        
        # 基于名称判断
        for keyword, anim_type in self.animation_type_map.items():
            if keyword in name_lower:
                return anim_type
        
        # 基于关键帧属性判断
        if keyframes:
            properties = set()
            for frame in keyframes:
                properties.update(frame.get("properties", {}).keys())
            
            if "opacity" in properties:
                return AnimationType.FADE_IN
            elif "transform" in properties:
                # 进一步分析transform属性
                for frame in keyframes:
                    transform = frame.get("properties", {}).get("transform", "")
                    if "translate" in transform:
                        return AnimationType.SLIDE_IN
                    elif "scale" in transform:
                        return AnimationType.SCALE
                    elif "rotate" in transform:
                        return AnimationType.ROTATE
        
        return AnimationType.FADE_IN  # 默认
    
    def parse_js_animations(self, js_content: str) -> List[ParsedAnimation]:
        """解析JavaScript动画"""
        animations = []
        
        try:
            # 查找Web Animation API调用
            animate_pattern = r'\.animate\s*\(\s*(\[.*?\])\s*,\s*(\{.*?\})\s*\)'
            animate_matches = re.findall(animate_pattern, js_content, re.DOTALL)
            
            for i, (keyframes_str, options_str) in enumerate(animate_matches):
                try:
                    # 解析关键帧和选项
                    keyframes = eval(keyframes_str)  # 简化解析，实际应该更安全
                    options = eval(options_str)
                    
                    animation = ParsedAnimation(
                        element_id=f"js_element_{i}",
                        element_type="div",
                        animation_name=f"js_animation_{i}",
                        animation_type=self.determine_js_animation_type(keyframes),
                        duration=options.get("duration", 1000) / 1000,
                        delay=options.get("delay", 0) / 1000,
                        easing=options.get("easing", "ease"),
                        properties=options,
                        keyframes=self.convert_js_keyframes(keyframes)
                    )
                    
                    animations.append(animation)
                    
                except Exception as e:
                    logger.warning(f"解析JS动画 {i} 失败: {e}")
                    
        except Exception as e:
            logger.error(f"解析JavaScript动画失败: {e}")
        
        return animations
    
    def determine_js_animation_type(self, keyframes: List[Dict[str, Any]]) -> AnimationType:
        """确定JavaScript动画类型"""
        if not keyframes:
            return AnimationType.FADE_IN
        
        # 分析关键帧属性
        properties = set()
        for frame in keyframes:
            properties.update(frame.keys())
        
        if "opacity" in properties:
            return AnimationType.FADE_IN
        elif "transform" in properties:
            # 分析transform内容
            for frame in keyframes:
                transform = frame.get("transform", "")
                if "translate" in transform:
                    return AnimationType.SLIDE_IN
                elif "scale" in transform:
                    return AnimationType.SCALE
                elif "rotate" in transform:
                    return AnimationType.ROTATE
        
        return AnimationType.FADE_IN
    
    def convert_js_keyframes(self, js_keyframes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """转换JavaScript关键帧为标准格式"""
        converted = []
        
        for i, frame in enumerate(js_keyframes):
            percentage = (i / (len(js_keyframes) - 1)) * 100 if len(js_keyframes) > 1 else 0
            
            converted.append({
                "percentage": percentage,
                "properties": frame
            })
        
        return converted
    
    def parse_html_elements(self, soup) -> List[ParsedElement]:
        """解析HTML元素"""
        elements = []
        
        try:
            # 查找所有有意义的元素
            for element in soup.find_all(['div', 'span', 'p', 'h1', 'h2', 'h3', 'img', 'svg']):
                parsed_element = ParsedElement(
                    tag=element.name,
                    id=element.get('id', ''),
                    classes=element.get('class', []),
                    content=element.get_text().strip(),
                    styles=self.parse_inline_styles(element.get('style', '')),
                    attributes=dict(element.attrs),
                    animations=[]
                )
                
                elements.append(parsed_element)
                
        except Exception as e:
            logger.error(f"解析HTML元素失败: {e}")
        
        return elements
    
    def parse_inline_styles(self, style_str: str) -> Dict[str, str]:
        """解析内联样式"""
        styles = {}
        
        if not style_str:
            return styles
        
        try:
            # 分割样式属性
            properties = style_str.split(';')
            
            for prop in properties:
                if ':' in prop:
                    key, value = prop.split(':', 1)
                    styles[key.strip()] = value.strip()
                    
        except Exception as e:
            logger.error(f"解析内联样式失败: {e}")
        
        return styles
    
    def generate_metadata(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成元数据"""
        metadata = {
            "parse_time": str(datetime.now()),
            "element_count": len(parsed_data.get("elements", [])),
            "animation_count": len(parsed_data.get("animations", [])),
            "tech_stack": self.determine_tech_stack(parsed_data),
            "complexity": self.calculate_complexity(parsed_data),
            "estimated_duration": self.estimate_total_duration(parsed_data)
        }
        
        return metadata
    
    def determine_tech_stack(self, parsed_data: Dict[str, Any]) -> str:
        """确定技术栈"""
        has_css_animations = any("@keyframes" in str(parsed_data.get("styles", {})))
        has_js_animations = bool(parsed_data.get("scripts", "").strip())
        
        if has_css_animations and has_js_animations:
            return "混合动画"
        elif has_css_animations:
            return "CSS动画"
        elif has_js_animations:
            return "JavaScript动画"
        else:
            return "静态内容"
    
    def calculate_complexity(self, parsed_data: Dict[str, Any]) -> str:
        """计算复杂度"""
        element_count = len(parsed_data.get("elements", []))
        animation_count = len(parsed_data.get("animations", []))
        
        total_score = element_count + animation_count * 2
        
        if total_score <= 5:
            return "简单"
        elif total_score <= 15:
            return "中等"
        elif total_score <= 30:
            return "复杂"
        else:
            return "非常复杂"
    
    def estimate_total_duration(self, parsed_data: Dict[str, Any]) -> float:
        """估算总持续时间"""
        max_duration = 0
        
        for animation in parsed_data.get("animations", []):
            if isinstance(animation, ParsedAnimation):
                total_time = animation.duration + animation.delay
                max_duration = max(max_duration, total_time)
        
        return max_duration if max_duration > 0 else 2.0  # 默认2秒
    
    def convert_to_project_elements(self, parsed_data: Dict[str, Any]) -> List[Element]:
        """转换为项目元素"""
        project_elements = []
        
        try:
            for parsed_element in parsed_data.get("elements", []):
                # 创建项目元素
                element = Element(
                    element_id=parsed_element.id or f"ai_element_{len(project_elements)}",
                    name=f"AI元素_{len(project_elements)}",
                    element_type=self._map_tag_to_element_type(parsed_element.tag),
                    content=parsed_element.content,
                    position=Point(0, 0),  # 默认位置
                    style=self._convert_styles_to_element_style(parsed_element.styles)
                )
                
                # 添加动画信息
                element_animations = [
                    anim for anim in parsed_data.get("animations", [])
                    if isinstance(anim, ParsedAnimation) and 
                    (anim.element_id == parsed_element.id or not anim.element_id)
                ]
                
                if element_animations:
                    # 使用第一个动画作为主要动画
                    main_animation = element_animations[0]
                    element.animation_type = main_animation.animation_type
                    element.animation_duration = main_animation.duration
                    element.animation_delay = main_animation.delay
                
                project_elements.append(element)
                
        except Exception as e:
            logger.error(f"转换为项目元素失败: {e}")
        
        return project_elements
    
    def generate_animation_summary(self, parsed_data: Dict[str, Any]) -> str:
        """生成动画摘要"""
        try:
            metadata = parsed_data.get("metadata", {})
            
            summary_lines = [
                "=== AI动画解析摘要 ===",
                f"元素数量: {metadata.get('element_count', 0)}",
                f"动画数量: {metadata.get('animation_count', 0)}",
                f"技术栈: {metadata.get('tech_stack', '未知')}",
                f"复杂度: {metadata.get('complexity', '未知')}",
                f"预估时长: {metadata.get('estimated_duration', 0):.1f}秒",
                "",
                "动画详情:"
            ]
            
            for i, animation in enumerate(parsed_data.get("animations", [])):
                if isinstance(animation, ParsedAnimation):
                    summary_lines.append(
                        f"  {i+1}. {animation.animation_name} "
                        f"({animation.animation_type.value}, {animation.duration}s)"
                    )
            
            return "\n".join(summary_lines)
            
        except Exception as e:
            logger.error(f"生成动画摘要失败: {e}")
            return "生成摘要失败"
    
    def validate_parsed_code(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证解析的代码"""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        try:
            # 检查基本结构
            if not parsed_data.get("elements"):
                validation_result["warnings"].append("未找到HTML元素")
            
            if not parsed_data.get("animations"):
                validation_result["warnings"].append("未找到动画定义")
            
            # 检查动画完整性
            for animation in parsed_data.get("animations", []):
                if isinstance(animation, ParsedAnimation):
                    if animation.duration <= 0:
                        validation_result["errors"].append(f"动画 {animation.animation_name} 持续时间无效")
                    
                    if not animation.keyframes:
                        validation_result["warnings"].append(f"动画 {animation.animation_name} 缺少关键帧")
            
            # 检查元素ID唯一性
            element_ids = [elem.id for elem in parsed_data.get("elements", []) if elem.id]
            if len(element_ids) != len(set(element_ids)):
                validation_result["errors"].append("存在重复的元素ID")
            
            # 性能建议
            animation_count = len(parsed_data.get("animations", []))
            if animation_count > 10:
                validation_result["suggestions"].append("动画数量较多，建议优化性能")
            
            # 设置验证状态
            validation_result["is_valid"] = len(validation_result["errors"]) == 0
            
        except Exception as e:
            logger.error(f"验证解析代码失败: {e}")
            validation_result["errors"].append(f"验证过程出错: {str(e)}")
            validation_result["is_valid"] = False
        
        return validation_result

    def _map_tag_to_element_type(self, tag: str) -> ElementType:
        """将HTML标签映射到元素类型"""
        tag_mapping = {
            'div': ElementType.RECTANGLE,
            'span': ElementType.TEXT,
            'p': ElementType.TEXT,
            'h1': ElementType.TEXT,
            'h2': ElementType.TEXT,
            'h3': ElementType.TEXT,
            'img': ElementType.IMAGE,
            'svg': ElementType.SVG,
            'circle': ElementType.CIRCLE,
            'rect': ElementType.RECTANGLE
        }
        return tag_mapping.get(tag.lower(), ElementType.RECTANGLE)

    def _convert_styles_to_element_style(self, styles: Dict[str, str]) -> ElementStyle:
        """将CSS样式转换为ElementStyle对象"""
        try:
            element_style = ElementStyle()

            # 映射常见的CSS属性
            if 'width' in styles:
                element_style.width = styles['width']
            if 'height' in styles:
                element_style.height = styles['height']
            if 'background-color' in styles:
                element_style.background_color = styles['background-color']
            if 'color' in styles:
                element_style.color = styles['color']
            if 'font-size' in styles:
                element_style.font_size = styles['font-size']
            if 'font-family' in styles:
                element_style.font_family = styles['font-family']
            if 'font-weight' in styles:
                element_style.font_weight = styles['font-weight']
            if 'text-align' in styles:
                element_style.text_align = styles['text-align']
            if 'opacity' in styles:
                try:
                    element_style.opacity = float(styles['opacity'])
                except ValueError:
                    pass
            if 'z-index' in styles:
                try:
                    element_style.z_index = int(styles['z-index'])
                except ValueError:
                    pass

            return element_style

        except Exception as e:
            logger.warning(f"转换样式失败: {e}")
            return ElementStyle()
