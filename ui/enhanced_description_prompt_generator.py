"""
AI Animation Studio - 增强动画描述和Prompt生成器
提供智能描述补全、语音输入、可视化预览、多语言支持等功能
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QTextEdit, QComboBox, QListWidget, QListWidgetItem, QMessageBox,
    QTabWidget, QLineEdit, QCheckBox, QSlider, QProgressBar, QFrame,
    QScrollArea, QSplitter, QTreeWidget, QTreeWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView, QMenu, QDialog, QFormLayout,
    QSpinBox, QDoubleSpinBox, QButtonGroup, QRadioButton, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, QPropertyAnimation
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QTextCursor, QSyntaxHighlighter, QTextCharFormat, QAction

from core.logger import get_logger
from core.description_history_manager import DescriptionHistoryManager, HistoryEntryType

logger = get_logger("enhanced_description_prompt")


class SemanticAnalyzer:
    """语义分析器"""
    
    def __init__(self):
        # 动画关键词库
        self.animation_keywords = {
            "movement": ["移动", "滑动", "飞行", "跳跃", "弹跳", "滚动", "漂浮"],
            "appearance": ["淡入", "淡出", "出现", "消失", "显示", "隐藏", "闪烁"],
            "transformation": ["旋转", "缩放", "变形", "翻转", "扭曲", "拉伸", "压缩"],
            "color": ["变色", "渐变", "闪光", "发光", "阴影", "高亮", "透明"],
            "physics": ["弹性", "重力", "摩擦", "碰撞", "反弹", "摆动", "震动"],
            "timing": ["快速", "缓慢", "瞬间", "延迟", "同步", "交错", "循环"],
            "style": ["科技感", "卡通", "现代", "复古", "简约", "华丽", "立体"]
        }
        
        # 情感关键词
        self.emotion_keywords = {
            "energetic": ["活力", "动感", "激烈", "爆发", "冲击"],
            "gentle": ["温和", "柔和", "优雅", "轻柔", "平静"],
            "playful": ["俏皮", "可爱", "有趣", "活泼", "调皮"],
            "professional": ["专业", "商务", "正式", "严肃", "稳重"],
            "creative": ["创意", "艺术", "独特", "新颖", "前卫"]
        }
        
        # 技术栈关键词
        self.tech_keywords = {
            "css": ["CSS", "过渡", "关键帧", "transform", "animation"],
            "javascript": ["JavaScript", "JS", "动态", "交互", "事件"],
            "svg": ["SVG", "矢量", "路径", "图形", "绘制"],
            "canvas": ["Canvas", "画布", "像素", "绘图", "渲染"],
            "webgl": ["WebGL", "3D", "立体", "光影", "材质", "纹理"]
        }
    
    def analyze_description(self, description: str) -> Dict[str, Any]:
        """分析动画描述"""
        analysis = {
            "animation_types": [],
            "emotions": [],
            "tech_stack": [],
            "complexity_score": 0,
            "duration_hints": [],
            "visual_elements": [],
            "interaction_hints": [],
            "confidence": 0.0
        }
        
        try:
            desc_lower = description.lower()
            
            # 分析动画类型
            for category, keywords in self.animation_keywords.items():
                found_keywords = [kw for kw in keywords if kw in desc_lower]
                if found_keywords:
                    analysis["animation_types"].append({
                        "category": category,
                        "keywords": found_keywords,
                        "confidence": len(found_keywords) / len(keywords)
                    })
            
            # 分析情感倾向
            for emotion, keywords in self.emotion_keywords.items():
                found_keywords = [kw for kw in keywords if kw in desc_lower]
                if found_keywords:
                    analysis["emotions"].append({
                        "emotion": emotion,
                        "keywords": found_keywords,
                        "strength": len(found_keywords)
                    })
            
            # 分析技术栈
            for tech, keywords in self.tech_keywords.items():
                found_keywords = [kw for kw in keywords if kw in desc_lower]
                if found_keywords:
                    analysis["tech_stack"].append({
                        "technology": tech,
                        "keywords": found_keywords
                    })
            
            # 提取时间信息
            time_patterns = [
                r"(\d+(?:\.\d+)?)\s*秒",
                r"(\d+(?:\.\d+)?)\s*s",
                r"(\d+)\s*毫秒",
                r"(\d+)\s*ms"
            ]
            
            for pattern in time_patterns:
                matches = re.findall(pattern, description)
                for match in matches:
                    analysis["duration_hints"].append(float(match))
            
            # 计算复杂度分数
            complexity = 0
            complexity += len(analysis["animation_types"]) * 10
            complexity += len(analysis["emotions"]) * 5
            complexity += len(analysis["tech_stack"]) * 15
            complexity += len(analysis["duration_hints"]) * 5
            
            analysis["complexity_score"] = min(100, complexity)
            
            # 计算置信度
            total_keywords = sum(len(cat["keywords"]) for cat in analysis["animation_types"])
            analysis["confidence"] = min(1.0, total_keywords / 10)
            
        except Exception as e:
            logger.error(f"语义分析失败: {e}")
        
        return analysis


class DescriptionTemplateManager:
    """描述模板管理器"""
    
    def __init__(self):
        self.templates = self.load_default_templates()
        self.user_templates = self.load_user_templates()
    
    def load_default_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """加载默认模板"""
        return {
            "入场动画": [
                {
                    "name": "优雅淡入",
                    "description": "元素从透明状态优雅地淡入显示，带有轻微的向上移动",
                    "keywords": ["淡入", "优雅", "向上"],
                    "complexity": "简单",
                    "duration": "1-2秒"
                },
                {
                    "name": "弹跳入场",
                    "description": "元素从下方弹跳进入，带有弹性效果和轻微的缩放",
                    "keywords": ["弹跳", "弹性", "缩放"],
                    "complexity": "中等",
                    "duration": "1.5-2.5秒"
                },
                {
                    "name": "旋转飞入",
                    "description": "元素从远处旋转飞入，带有3D透视效果和速度变化",
                    "keywords": ["旋转", "飞入", "3D", "透视"],
                    "complexity": "复杂",
                    "duration": "2-3秒"
                }
            ],
            "移动动画": [
                {
                    "name": "平滑滑动",
                    "description": "元素沿指定路径平滑滑动，保持匀速运动",
                    "keywords": ["滑动", "平滑", "匀速"],
                    "complexity": "简单",
                    "duration": "1-3秒"
                },
                {
                    "name": "弧线运动",
                    "description": "元素沿弧线路径运动，模拟抛物线轨迹",
                    "keywords": ["弧线", "抛物线", "轨迹"],
                    "complexity": "中等",
                    "duration": "2-4秒"
                },
                {
                    "name": "螺旋上升",
                    "description": "元素沿螺旋路径向上运动，带有旋转和缩放效果",
                    "keywords": ["螺旋", "上升", "旋转", "缩放"],
                    "complexity": "复杂",
                    "duration": "3-5秒"
                }
            ],
            "变换动画": [
                {
                    "name": "呼吸缩放",
                    "description": "元素周期性地放大和缩小，模拟呼吸效果",
                    "keywords": ["呼吸", "缩放", "周期"],
                    "complexity": "简单",
                    "duration": "2-4秒循环"
                },
                {
                    "name": "翻转展示",
                    "description": "元素进行3D翻转，展示正反两面的内容",
                    "keywords": ["翻转", "3D", "正反面"],
                    "complexity": "中等",
                    "duration": "1.5-2.5秒"
                }
            ],
            "特效动画": [
                {
                    "name": "粒子爆炸",
                    "description": "元素分解为多个粒子并向四周扩散，带有渐变消失效果",
                    "keywords": ["粒子", "爆炸", "扩散", "渐变"],
                    "complexity": "复杂",
                    "duration": "2-4秒"
                },
                {
                    "name": "光影扫描",
                    "description": "光线从一侧扫过元素，产生高光和阴影效果",
                    "keywords": ["光影", "扫描", "高光", "阴影"],
                    "complexity": "中等",
                    "duration": "1-2秒"
                }
            ]
        }
    
    def load_user_templates(self) -> List[Dict[str, Any]]:
        """加载用户自定义模板"""
        try:
            if os.path.exists("user_animation_templates.json"):
                with open("user_animation_templates.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"加载用户模板失败: {e}")
            return []
    
    def save_user_templates(self):
        """保存用户模板"""
        try:
            with open("user_animation_templates.json", 'w', encoding='utf-8') as f:
                json.dump(self.user_templates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存用户模板失败: {e}")
    
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """搜索模板"""
        results = []
        query_lower = query.lower()
        
        # 搜索默认模板
        for category, templates in self.templates.items():
            for template in templates:
                if (query_lower in template["name"].lower() or
                    query_lower in template["description"].lower() or
                    any(query_lower in kw.lower() for kw in template["keywords"])):
                    
                    template_copy = template.copy()
                    template_copy["category"] = category
                    template_copy["source"] = "默认"
                    results.append(template_copy)
        
        # 搜索用户模板
        for template in self.user_templates:
            if (query_lower in template.get("name", "").lower() or
                query_lower in template.get("description", "").lower()):
                
                template_copy = template.copy()
                template_copy["source"] = "用户"
                results.append(template_copy)
        
        return results
    
    def get_smart_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于语义分析获取智能建议"""
        suggestions = []
        
        try:
            # 基于动画类型推荐
            for anim_type in analysis.get("animation_types", []):
                category = anim_type["category"]
                
                if category == "movement":
                    suggestions.extend(self.templates.get("移动动画", []))
                elif category == "appearance":
                    suggestions.extend(self.templates.get("入场动画", []))
                elif category == "transformation":
                    suggestions.extend(self.templates.get("变换动画", []))
            
            # 基于复杂度筛选
            complexity_score = analysis.get("complexity_score", 0)
            if complexity_score < 30:
                suggestions = [s for s in suggestions if s.get("complexity") == "简单"]
            elif complexity_score > 70:
                suggestions = [s for s in suggestions if s.get("complexity") in ["复杂", "中等"]]
            
            # 去重并排序
            unique_suggestions = []
            seen_names = set()
            
            for suggestion in suggestions:
                if suggestion["name"] not in seen_names:
                    unique_suggestions.append(suggestion)
                    seen_names.add(suggestion["name"])
            
            return unique_suggestions[:10]  # 返回前10个建议
            
        except Exception as e:
            logger.error(f"获取智能建议失败: {e}")
            return []


class PromptSyntaxHighlighter(QSyntaxHighlighter):
    """Prompt语法高亮器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 定义高亮规则
        self.highlighting_rules = []
        
        # 关键词格式
        keyword_format = QTextCharFormat()
        keyword_format.setColor(QColor("#0066CC"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = [
            "动画类型", "用户描述", "技术要求", "性能要求", "代码结构",
            "HTML", "CSS", "JavaScript", "duration", "easing", "transform"
        ]
        
        for keyword in keywords:
            pattern = f"\\b{keyword}\\b"
            self.highlighting_rules.append((re.compile(pattern), keyword_format))
        
        # 参数格式
        param_format = QTextCharFormat()
        param_format.setColor(QColor("#CC6600"))
        
        param_pattern = re.compile(r"\{[^}]+\}")
        self.highlighting_rules.append((param_pattern, param_format))
        
        # 注释格式
        comment_format = QTextCharFormat()
        comment_format.setColor(QColor("#008000"))
        comment_format.setFontItalic(True)
        
        comment_pattern = re.compile(r"#.*")
        self.highlighting_rules.append((comment_pattern, comment_format))
    
    def highlightBlock(self, text):
        """高亮文本块"""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


class VoiceInputSimulator:
    """语音输入模拟器（简化实现）"""
    
    def __init__(self):
        self.is_recording = False
        self.recognition_results = []
    
    def start_recording(self) -> bool:
        """开始录音"""
        try:
            # 简化实现，实际应该集成语音识别API
            self.is_recording = True
            logger.info("语音录音开始（模拟）")
            return True
        except Exception as e:
            logger.error(f"开始录音失败: {e}")
            return False
    
    def stop_recording(self) -> Optional[str]:
        """停止录音并返回识别结果"""
        try:
            self.is_recording = False
            
            # 模拟语音识别结果
            mock_results = [
                "一个红色的小球从左边弹跳到右边",
                "文字从上方淡入然后旋转三百六十度",
                "卡片翻转显示背面内容带有光影效果"
            ]
            
            import random
            result = random.choice(mock_results)
            logger.info(f"语音识别完成（模拟）: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"停止录音失败: {e}")
            return None


class EnhancedDescriptionPromptGenerator(QWidget):
    """增强动画描述和Prompt生成器"""
    
    # 信号定义
    description_analyzed = pyqtSignal(dict)      # 描述分析完成
    prompt_generated = pyqtSignal(str)           # Prompt生成完成
    template_applied = pyqtSignal(dict)          # 模板应用完成
    voice_input_completed = pyqtSignal(str)      # 语音输入完成
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.semantic_analyzer = SemanticAnalyzer()
        self.template_manager = DescriptionTemplateManager()
        self.voice_input = VoiceInputSimulator()
        self.history_manager = DescriptionHistoryManager()
        self.current_analysis = None
        self.current_entry_id = None
        
        self.setup_ui()
        self.setup_connections()
        
        logger.info("增强动画描述和Prompt生成器初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("智能动画描述生成器")
        title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 主要内容区域
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：描述输入和分析
        left_panel = self.create_description_panel()
        content_splitter.addWidget(left_panel)
        
        # 右侧：模板和预览
        right_panel = self.create_template_and_preview_panel()
        content_splitter.addWidget(right_panel)
        
        content_splitter.setSizes([500, 400])
        layout.addWidget(content_splitter)
        
        # 底部：Prompt生成区域
        prompt_panel = self.create_prompt_panel()
        layout.addWidget(prompt_panel)
    
    def create_description_panel(self):
        """创建描述面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 描述输入组
        input_group = QGroupBox("动画描述输入")
        input_layout = QVBoxLayout(input_group)
        
        # 输入方式选择
        input_mode_layout = QHBoxLayout()
        
        self.text_input_rb = QRadioButton("文字输入")
        self.text_input_rb.setChecked(True)
        input_mode_layout.addWidget(self.text_input_rb)
        
        self.voice_input_rb = QRadioButton("语音输入")
        input_mode_layout.addWidget(self.voice_input_rb)
        
        self.template_input_rb = QRadioButton("模板输入")
        input_mode_layout.addWidget(self.template_input_rb)
        
        input_mode_layout.addStretch()
        
        input_layout.addLayout(input_mode_layout)
        
        # 描述文本区域
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText(
            "请用自然语言详细描述您想要的动画效果...\n\n"
            "💡 描述技巧：\n"
            "• 说明元素的起始和结束状态\n"
            "• 描述运动的方向和路径\n"
            "• 指定动画的时长和节奏\n"
            "• 添加视觉风格和情感色彩\n\n"
            "🎯 示例：\n"
            "一个蓝色的圆形按钮从屏幕左侧优雅地滑入，"
            "在中央停留0.5秒后轻微弹跳，"
            "最后带着发光效果淡出消失。整个过程持续3秒，"
            "要有科技感和未来感。"
        )
        self.description_edit.setMinimumHeight(150)
        input_layout.addWidget(self.description_edit)
        
        # 语音输入控制
        voice_layout = QHBoxLayout()
        
        self.voice_record_btn = QPushButton("🎤 开始录音")
        self.voice_record_btn.setCheckable(True)
        self.voice_record_btn.clicked.connect(self.toggle_voice_recording)
        voice_layout.addWidget(self.voice_record_btn)
        
        self.voice_status_label = QLabel("语音输入就绪")
        voice_layout.addWidget(self.voice_status_label)
        
        voice_layout.addStretch()
        
        # 语言选择
        voice_layout.addWidget(QLabel("语言:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["中文", "English", "日本語"])
        voice_layout.addWidget(self.language_combo)
        
        input_layout.addLayout(voice_layout)
        
        # 快速输入按钮
        quick_input_layout = QHBoxLayout()
        
        quick_buttons = [
            ("✨ 淡入", "元素优雅淡入显示"),
            ("🚀 滑入", "元素从侧边快速滑入"),
            ("🔄 旋转", "元素围绕中心旋转"),
            ("📏 缩放", "元素大小变化"),
            ("⚡ 弹跳", "元素带弹性效果"),
            ("🌟 闪烁", "元素闪烁发光")
        ]
        
        for text, desc in quick_buttons:
            btn = QPushButton(text)
            btn.setMaximumWidth(70)
            btn.clicked.connect(lambda checked, d=desc: self.add_quick_description(d))
            quick_input_layout.addWidget(btn)
        
        input_layout.addLayout(quick_input_layout)
        
        layout.addWidget(input_group)
        
        # 智能分析结果
        analysis_group = QGroupBox("智能分析结果")
        analysis_layout = QVBoxLayout(analysis_group)
        
        # 分析控制
        analysis_control_layout = QHBoxLayout()
        
        self.auto_analyze_cb = QCheckBox("自动分析")
        self.auto_analyze_cb.setChecked(True)
        analysis_control_layout.addWidget(self.auto_analyze_cb)
        
        analyze_btn = QPushButton("🧠 立即分析")
        analyze_btn.clicked.connect(self.analyze_current_description)
        analysis_control_layout.addWidget(analyze_btn)
        
        analysis_control_layout.addStretch()
        
        # 分析质量指示器
        self.analysis_quality_label = QLabel("分析质量: 未分析")
        analysis_control_layout.addWidget(self.analysis_quality_label)
        
        analysis_layout.addLayout(analysis_control_layout)
        
        # 分析结果显示
        self.analysis_result_edit = QTextEdit()
        self.analysis_result_edit.setMaximumHeight(120)
        self.analysis_result_edit.setReadOnly(True)
        self.analysis_result_edit.setPlaceholderText("智能分析结果将显示在这里...")
        analysis_layout.addWidget(self.analysis_result_edit)
        
        layout.addWidget(analysis_group)
        
        # 描述优化建议
        optimization_group = QGroupBox("描述优化建议")
        optimization_layout = QVBoxLayout(optimization_group)
        
        self.optimization_list = QListWidget()
        self.optimization_list.setMaximumHeight(100)
        optimization_layout.addWidget(self.optimization_list)
        
        # 应用建议按钮
        apply_suggestions_btn = QPushButton("📝 应用所有建议")
        apply_suggestions_btn.clicked.connect(self.apply_optimization_suggestions)
        optimization_layout.addWidget(apply_suggestions_btn)
        
        layout.addWidget(optimization_group)
        
        return panel

    def create_template_and_preview_panel(self):
        """创建模板和预览面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 标签页
        tab_widget = QTabWidget()

        # 模板标签页
        template_tab = self.create_template_panel()
        tab_widget.addTab(template_tab, "📋 模板库")

        # 可视化预览标签页
        preview_tab = self.create_preview_panel()
        tab_widget.addTab(preview_tab, "👁️ 可视预览")

        # 智能建议标签页
        suggestions_tab = self.create_suggestions_panel()
        tab_widget.addTab(suggestions_tab, "💡 智能建议")

        # 历史记录标签页
        history_tab = self.create_history_panel()
        tab_widget.addTab(history_tab, "📚 历史记录")

        layout.addWidget(tab_widget)

        return panel

    def create_preview_panel(self):
        """创建预览面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        try:
            from ui.visual_description_previewer import VisualDescriptionPreviewer

            # 可视化预览器
            self.visual_previewer = VisualDescriptionPreviewer()
            self.visual_previewer.preview_updated.connect(self.on_preview_updated)
            self.visual_previewer.animation_state_changed.connect(self.on_animation_state_changed)
            layout.addWidget(self.visual_previewer)

            # 预览控制
            preview_control_layout = QHBoxLayout()

            update_preview_btn = QPushButton("🔄 更新预览")
            update_preview_btn.clicked.connect(self.update_visual_preview)
            preview_control_layout.addWidget(update_preview_btn)

            export_preview_btn = QPushButton("📷 导出图片")
            export_preview_btn.clicked.connect(self.export_preview_image)
            preview_control_layout.addWidget(export_preview_btn)

            preview_control_layout.addStretch()

            layout.addLayout(preview_control_layout)

        except ImportError as e:
            logger.warning(f"无法导入可视化预览器: {e}")
            # 创建占位符
            placeholder = QLabel("可视化预览功能暂不可用")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("border: 1px solid #ccc; background: #f9f9f9; min-height: 200px;")
            layout.addWidget(placeholder)

        return panel

    def create_suggestions_panel(self):
        """创建智能建议面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 智能建议控制
        suggestions_control_layout = QHBoxLayout()

        get_suggestions_btn = QPushButton("🧠 获取建议")
        get_suggestions_btn.clicked.connect(self.get_smart_suggestions)
        suggestions_control_layout.addWidget(get_suggestions_btn)

        auto_suggestions_cb = QCheckBox("自动建议")
        auto_suggestions_cb.setChecked(True)
        suggestions_control_layout.addWidget(auto_suggestions_cb)

        suggestions_control_layout.addStretch()

        layout.addLayout(suggestions_control_layout)

        # 建议列表
        suggestions_group = QGroupBox("智能建议")
        suggestions_layout = QVBoxLayout(suggestions_group)

        self.suggestions_list = QListWidget()
        self.suggestions_list.itemDoubleClicked.connect(self.apply_suggestion)
        suggestions_layout.addWidget(self.suggestions_list)

        # 建议操作
        suggestions_actions_layout = QHBoxLayout()

        apply_suggestion_btn = QPushButton("应用选中建议")
        apply_suggestion_btn.clicked.connect(self.apply_selected_suggestion)
        suggestions_actions_layout.addWidget(apply_suggestion_btn)

        refresh_suggestions_btn = QPushButton("刷新建议")
        refresh_suggestions_btn.clicked.connect(self.refresh_suggestions)
        suggestions_actions_layout.addWidget(refresh_suggestions_btn)

        suggestions_actions_layout.addStretch()

        suggestions_layout.addLayout(suggestions_actions_layout)

        layout.addWidget(suggestions_group)

        # 描述质量评估
        quality_group = QGroupBox("描述质量评估")
        quality_layout = QVBoxLayout(quality_group)

        self.quality_progress = QProgressBar()
        self.quality_progress.setRange(0, 100)
        self.quality_progress.setValue(0)
        self.quality_progress.setFormat("质量评分: %v/100")
        quality_layout.addWidget(self.quality_progress)

        self.quality_details = QTextEdit()
        self.quality_details.setMaximumHeight(80)
        self.quality_details.setReadOnly(True)
        self.quality_details.setPlaceholderText("质量评估详情将显示在这里...")
        quality_layout.addWidget(self.quality_details)

        layout.addWidget(quality_group)

        return panel

    def create_history_panel(self):
        """创建历史记录面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 历史记录控制
        history_control_layout = QHBoxLayout()

        refresh_history_btn = QPushButton("🔄 刷新")
        refresh_history_btn.clicked.connect(self.refresh_history)
        history_control_layout.addWidget(refresh_history_btn)

        clear_history_btn = QPushButton("🗑️ 清空")
        clear_history_btn.clicked.connect(self.clear_history)
        history_control_layout.addWidget(clear_history_btn)

        export_history_btn = QPushButton("📤 导出")
        export_history_btn.clicked.connect(self.export_history)
        history_control_layout.addWidget(export_history_btn)

        history_control_layout.addStretch()

        # 搜索框
        self.history_search_edit = QLineEdit()
        self.history_search_edit.setPlaceholderText("搜索历史记录...")
        self.history_search_edit.textChanged.connect(self.search_history)
        history_control_layout.addWidget(self.history_search_edit)

        layout.addLayout(history_control_layout)

        # 历史记录列表
        history_group = QGroupBox("历史记录")
        history_layout = QVBoxLayout(history_group)

        # 过滤选项
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("类型:"))
        self.history_type_filter = QComboBox()
        self.history_type_filter.addItems([
            "全部", "手动输入", "模板应用", "AI生成", "语音输入", "优化结果"
        ])
        self.history_type_filter.currentTextChanged.connect(self.filter_history)
        filter_layout.addWidget(self.history_type_filter)

        filter_layout.addWidget(QLabel("语言:"))
        self.history_lang_filter = QComboBox()
        self.history_lang_filter.addItems(["全部", "中文", "English", "日本語"])
        self.history_lang_filter.currentTextChanged.connect(self.filter_history)
        filter_layout.addWidget(self.history_lang_filter)

        filter_layout.addStretch()

        history_layout.addLayout(filter_layout)

        # 历史列表
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.load_history_entry)
        self.history_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_history_context_menu)
        history_layout.addWidget(self.history_list)

        # 历史操作
        history_actions_layout = QHBoxLayout()

        load_history_btn = QPushButton("📋 加载选中")
        load_history_btn.clicked.connect(self.load_selected_history)
        history_actions_layout.addWidget(load_history_btn)

        delete_history_btn = QPushButton("❌ 删除选中")
        delete_history_btn.clicked.connect(self.delete_selected_history)
        history_actions_layout.addWidget(delete_history_btn)

        history_actions_layout.addStretch()

        history_layout.addLayout(history_actions_layout)

        layout.addWidget(history_group)

        # 历史统计
        stats_group = QGroupBox("使用统计")
        stats_layout = QVBoxLayout(stats_group)

        self.history_stats_label = QLabel("统计信息加载中...")
        stats_layout.addWidget(self.history_stats_label)

        layout.addWidget(stats_group)

        # 初始化历史显示
        self.refresh_history()

        return panel

    def create_template_panel(self):
        """创建模板面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 模板搜索
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索模板:"))
        
        self.template_search_edit = QLineEdit()
        self.template_search_edit.setPlaceholderText("输入关键词搜索...")
        self.template_search_edit.textChanged.connect(self.search_templates)
        search_layout.addWidget(self.template_search_edit)
        
        layout.addLayout(search_layout)
        
        # 模板分类标签页
        self.template_tabs = QTabWidget()
        
        # 为每个模板分类创建标签页
        for category, templates in self.template_manager.templates.items():
            tab = self.create_template_category_tab(category, templates)
            self.template_tabs.addTab(tab, category)
        
        # 用户模板标签页
        user_tab = self.create_user_templates_tab()
        self.template_tabs.addTab(user_tab, "我的模板")
        
        layout.addWidget(self.template_tabs)
        
        # 模板操作按钮
        template_actions_layout = QHBoxLayout()
        
        apply_template_btn = QPushButton("📋 应用模板")
        apply_template_btn.clicked.connect(self.apply_selected_template)
        template_actions_layout.addWidget(apply_template_btn)
        
        save_template_btn = QPushButton("💾 保存为模板")
        save_template_btn.clicked.connect(self.save_as_template)
        template_actions_layout.addWidget(save_template_btn)
        
        template_actions_layout.addStretch()
        
        layout.addLayout(template_actions_layout)
        
        return panel
    
    def create_template_category_tab(self, category: str, templates: List[Dict[str, Any]]):
        """创建模板分类标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        template_list = QListWidget()
        
        for template in templates:
            item_text = f"{template['name']} ({template['complexity']}, {template['duration']})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, template)
            item.setToolTip(template['description'])
            
            # 根据复杂度设置颜色
            if template['complexity'] == "简单":
                item.setBackground(QColor("#E8F5E8"))
            elif template['complexity'] == "中等":
                item.setBackground(QColor("#FFF3E0"))
            else:
                item.setBackground(QColor("#FFEBEE"))
            
            template_list.addItem(item)
        
        template_list.itemDoubleClicked.connect(self.on_template_double_clicked)
        layout.addWidget(template_list)
        
        return tab
    
    def create_user_templates_tab(self):
        """创建用户模板标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.user_template_list = QListWidget()
        self.update_user_templates_display()
        layout.addWidget(self.user_template_list)
        
        # 用户模板操作
        user_actions_layout = QHBoxLayout()
        
        edit_template_btn = QPushButton("编辑")
        edit_template_btn.clicked.connect(self.edit_user_template)
        user_actions_layout.addWidget(edit_template_btn)
        
        delete_template_btn = QPushButton("删除")
        delete_template_btn.clicked.connect(self.delete_user_template)
        user_actions_layout.addWidget(delete_template_btn)
        
        user_actions_layout.addStretch()
        
        layout.addLayout(user_actions_layout)
        
        return tab
    
    def create_prompt_panel(self):
        """创建Prompt面板"""
        panel = QGroupBox("智能Prompt生成器")
        layout = QVBoxLayout(panel)
        
        # Prompt控制
        prompt_control_layout = QHBoxLayout()
        
        generate_prompt_btn = QPushButton("🚀 生成Prompt")
        generate_prompt_btn.clicked.connect(self.generate_smart_prompt)
        prompt_control_layout.addWidget(generate_prompt_btn)
        
        optimize_prompt_btn = QPushButton("⚡ 优化Prompt")
        optimize_prompt_btn.clicked.connect(self.optimize_current_prompt)
        prompt_control_layout.addWidget(optimize_prompt_btn)
        
        validate_prompt_btn = QPushButton("✅ 验证Prompt")
        validate_prompt_btn.clicked.connect(self.validate_current_prompt)
        prompt_control_layout.addWidget(validate_prompt_btn)
        
        prompt_control_layout.addStretch()
        
        # Prompt质量指示器
        self.prompt_quality_label = QLabel("质量: 未评估")
        prompt_control_layout.addWidget(self.prompt_quality_label)
        
        layout.addLayout(prompt_control_layout)
        
        # Prompt编辑器
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setMinimumHeight(150)
        self.prompt_edit.setPlaceholderText("智能生成的Prompt将显示在这里...")
        
        # 添加语法高亮
        self.syntax_highlighter = PromptSyntaxHighlighter(self.prompt_edit.document())
        
        layout.addWidget(self.prompt_edit)
        
        # Prompt模板选择
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Prompt模板:"))
        
        self.prompt_template_combo = QComboBox()
        self.prompt_template_combo.addItems([
            "标准模板", "创意模式", "技术模式", "性能优先", "兼容性优先"
        ])
        self.prompt_template_combo.currentTextChanged.connect(self.on_prompt_template_changed)
        template_layout.addWidget(self.prompt_template_combo)
        
        load_template_btn = QPushButton("加载")
        load_template_btn.clicked.connect(self.load_prompt_template)
        template_layout.addWidget(load_template_btn)
        
        template_layout.addStretch()
        
        layout.addLayout(template_layout)
        
        return panel
    
    def setup_connections(self):
        """设置信号连接"""
        # 描述文本变化时自动分析
        self.description_edit.textChanged.connect(self.on_description_changed)
        
        # 语音输入模式切换
        self.voice_input_rb.toggled.connect(self.on_input_mode_changed)
        self.text_input_rb.toggled.connect(self.on_input_mode_changed)
        self.template_input_rb.toggled.connect(self.on_input_mode_changed)
    
    def on_description_changed(self):
        """描述改变事件"""
        if self.auto_analyze_cb.isChecked():
            # 延迟分析，避免频繁触发
            if hasattr(self, 'analysis_timer'):
                self.analysis_timer.stop()
            
            self.analysis_timer = QTimer()
            self.analysis_timer.setSingleShot(True)
            self.analysis_timer.timeout.connect(self.analyze_current_description)
            self.analysis_timer.start(1500)  # 1.5秒延迟
    
    def analyze_current_description(self):
        """分析当前描述"""
        try:
            description = self.description_edit.toPlainText().strip()
            if not description:
                self.analysis_result_edit.clear()
                self.analysis_quality_label.setText("分析质量: 未分析")
                return
            
            # 进行语义分析
            self.current_analysis = self.semantic_analyzer.analyze_description(description)
            
            # 更新分析结果显示
            self.update_analysis_display()
            
            # 生成优化建议
            self.generate_optimization_suggestions()
            
            # 发送分析完成信号
            self.description_analyzed.emit(self.current_analysis)

            # 保存到历史记录
            self.save_current_description_to_history(HistoryEntryType.MANUAL_INPUT)
            
        except Exception as e:
            logger.error(f"分析描述失败: {e}")
    
    def update_analysis_display(self):
        """更新分析结果显示"""
        if not self.current_analysis:
            return
        
        try:
            result_lines = []
            
            # 动画类型分析
            if self.current_analysis["animation_types"]:
                result_lines.append("🎬 检测到的动画类型:")
                for anim_type in self.current_analysis["animation_types"]:
                    keywords_str = ", ".join(anim_type["keywords"])
                    confidence = anim_type["confidence"] * 100
                    result_lines.append(f"  • {anim_type['category']}: {keywords_str} (置信度: {confidence:.0f}%)")
                result_lines.append("")
            
            # 情感分析
            if self.current_analysis["emotions"]:
                result_lines.append("💭 情感倾向:")
                for emotion in self.current_analysis["emotions"]:
                    keywords_str = ", ".join(emotion["keywords"])
                    result_lines.append(f"  • {emotion['emotion']}: {keywords_str}")
                result_lines.append("")
            
            # 技术栈建议
            if self.current_analysis["tech_stack"]:
                result_lines.append("🔧 建议技术栈:")
                for tech in self.current_analysis["tech_stack"]:
                    result_lines.append(f"  • {tech['technology'].upper()}")
                result_lines.append("")
            
            # 复杂度评估
            complexity = self.current_analysis["complexity_score"]
            result_lines.append(f"📊 复杂度评分: {complexity}/100")
            
            if complexity < 30:
                result_lines.append("  → 简单动画，适合快速实现")
            elif complexity < 70:
                result_lines.append("  → 中等复杂度，需要一定技术实现")
            else:
                result_lines.append("  → 高复杂度，需要专业技术和更多时间")
            
            # 时间建议
            if self.current_analysis["duration_hints"]:
                durations = self.current_analysis["duration_hints"]
                avg_duration = sum(durations) / len(durations)
                result_lines.append(f"⏱️ 建议时长: {avg_duration:.1f}秒")
            
            self.analysis_result_edit.setPlainText("\n".join(result_lines))
            
            # 更新质量指示器
            confidence = self.current_analysis["confidence"] * 100
            if confidence >= 80:
                quality_text = f"分析质量: 优秀 ({confidence:.0f}%)"
                color = "green"
            elif confidence >= 60:
                quality_text = f"分析质量: 良好 ({confidence:.0f}%)"
                color = "orange"
            else:
                quality_text = f"分析质量: 需改进 ({confidence:.0f}%)"
                color = "red"
            
            self.analysis_quality_label.setText(quality_text)
            self.analysis_quality_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            
        except Exception as e:
            logger.error(f"更新分析显示失败: {e}")
    
    def generate_optimization_suggestions(self):
        """生成优化建议"""
        if not self.current_analysis:
            return
        
        try:
            suggestions = []
            
            # 基于分析结果生成建议
            if self.current_analysis["confidence"] < 0.6:
                suggestions.append("💡 建议添加更多具体的动画描述词汇")
            
            if not self.current_analysis["duration_hints"]:
                suggestions.append("⏱️ 建议指定动画的持续时间")
            
            if not self.current_analysis["emotions"]:
                suggestions.append("🎨 建议添加视觉风格或情感描述")
            
            if not self.current_analysis["tech_stack"]:
                suggestions.append("🔧 建议指定使用的技术栈（CSS/JS/SVG等）")
            
            if self.current_analysis["complexity_score"] < 20:
                suggestions.append("📈 描述较为简单，可以添加更多动画细节")
            
            # 更新建议列表
            self.optimization_list.clear()
            for suggestion in suggestions:
                item = QListWidgetItem(suggestion)
                self.optimization_list.addItem(item)
            
        except Exception as e:
            logger.error(f"生成优化建议失败: {e}")

    def add_quick_description(self, description: str):
        """添加快速描述"""
        current_text = self.description_edit.toPlainText()
        if current_text:
            new_text = current_text + "，" + description
        else:
            new_text = description

        self.description_edit.setPlainText(new_text)

        # 移动光标到末尾
        cursor = self.description_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.description_edit.setTextCursor(cursor)

    def toggle_voice_recording(self, checked: bool):
        """切换语音录音状态"""
        try:
            if checked:
                # 开始录音
                if self.voice_input.start_recording():
                    self.voice_record_btn.setText("🔴 停止录音")
                    self.voice_status_label.setText("正在录音...")
                    self.voice_status_label.setStyleSheet("color: red;")
                else:
                    self.voice_record_btn.setChecked(False)
                    QMessageBox.warning(self, "错误", "无法启动语音录音")
            else:
                # 停止录音
                result = self.voice_input.stop_recording()
                self.voice_record_btn.setText("🎤 开始录音")
                self.voice_status_label.setText("语音输入就绪")
                self.voice_status_label.setStyleSheet("")

                if result:
                    # 将语音识别结果添加到描述中
                    self.description_edit.setPlainText(result)
                    self.voice_input_completed.emit(result)

                    # 保存到历史记录
                    self.save_current_description_to_history(HistoryEntryType.VOICE_INPUT)

                    QMessageBox.information(self, "语音输入完成", f"识别结果：\n{result}")

        except Exception as e:
            logger.error(f"语音录音操作失败: {e}")
            self.voice_record_btn.setChecked(False)

    def on_input_mode_changed(self):
        """输入模式改变事件"""
        if self.voice_input_rb.isChecked():
            # 启用语音输入相关控件
            self.voice_record_btn.setEnabled(True)
            self.language_combo.setEnabled(True)
        else:
            # 禁用语音输入相关控件
            self.voice_record_btn.setEnabled(False)
            self.language_combo.setEnabled(False)

            if self.voice_input.is_recording:
                self.voice_record_btn.setChecked(False)
                self.toggle_voice_recording(False)

    def search_templates(self, query: str):
        """搜索模板"""
        if not query.strip():
            return

        try:
            results = self.template_manager.search_templates(query)

            # 显示搜索结果
            if results:
                # 创建搜索结果对话框
                dialog = QDialog(self)
                dialog.setWindowTitle(f"模板搜索结果 - '{query}'")
                dialog.setMinimumSize(600, 400)

                layout = QVBoxLayout(dialog)

                result_list = QListWidget()
                for template in results:
                    item_text = f"{template['name']} ({template.get('category', template.get('source', ''))})"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, template)
                    item.setToolTip(template['description'])
                    result_list.addItem(item)

                result_list.itemDoubleClicked.connect(lambda item: self.apply_template_from_search(item, dialog))
                layout.addWidget(result_list)

                # 按钮
                button_layout = QHBoxLayout()
                button_layout.addStretch()

                apply_btn = QPushButton("应用选中模板")
                apply_btn.clicked.connect(lambda: self.apply_template_from_search(result_list.currentItem(), dialog))
                button_layout.addWidget(apply_btn)

                close_btn = QPushButton("关闭")
                close_btn.clicked.connect(dialog.accept)
                button_layout.addWidget(close_btn)

                layout.addLayout(button_layout)

                dialog.exec()
            else:
                QMessageBox.information(self, "搜索结果", f"未找到包含'{query}'的模板")

        except Exception as e:
            logger.error(f"搜索模板失败: {e}")

    def apply_template_from_search(self, item: QListWidgetItem, dialog: QDialog):
        """从搜索结果应用模板"""
        if item:
            template = item.data(Qt.ItemDataRole.UserRole)
            self.apply_template(template)
            dialog.accept()

    def on_template_double_clicked(self, item: QListWidgetItem):
        """模板双击事件"""
        template = item.data(Qt.ItemDataRole.UserRole)
        self.apply_template(template)

    def apply_selected_template(self):
        """应用选中的模板"""
        # 获取当前标签页的选中项
        current_tab = self.template_tabs.currentWidget()
        if hasattr(current_tab, 'findChild'):
            template_list = current_tab.findChild(QListWidget)
            if template_list and template_list.currentItem():
                template = template_list.currentItem().data(Qt.ItemDataRole.UserRole)
                self.apply_template(template)
            else:
                QMessageBox.warning(self, "警告", "请先选择一个模板")

    def apply_template(self, template: Dict[str, Any]):
        """应用模板"""
        try:
            description = template.get("description", "")

            # 询问用户是否替换还是追加
            reply = QMessageBox.question(
                self, "应用模板",
                f"要应用模板: {template['name']}\n\n"
                f"描述: {description}\n\n"
                f"选择应用方式:",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 替换当前描述
                self.description_edit.setPlainText(description)
            elif reply == QMessageBox.StandardButton.No:
                # 追加到当前描述
                current_text = self.description_edit.toPlainText()
                if current_text:
                    new_text = current_text + "\n\n" + description
                else:
                    new_text = description
                self.description_edit.setPlainText(new_text)

            if reply != QMessageBox.StandardButton.Cancel:
                self.template_applied.emit(template)

                # 保存到历史记录
                self.save_current_description_to_history(HistoryEntryType.TEMPLATE_APPLIED)

                logger.info(f"已应用模板: {template['name']}")

        except Exception as e:
            logger.error(f"应用模板失败: {e}")

    def save_as_template(self):
        """保存为模板"""
        try:
            description = self.description_edit.toPlainText().strip()
            if not description:
                QMessageBox.warning(self, "警告", "请先输入动画描述")
                return

            # 创建保存模板对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("保存为模板")
            dialog.setMinimumSize(400, 300)

            layout = QFormLayout(dialog)

            # 模板名称
            name_edit = QLineEdit()
            name_edit.setPlaceholderText("输入模板名称...")
            layout.addRow("模板名称:", name_edit)

            # 模板分类
            category_combo = QComboBox()
            category_combo.addItems(["入场动画", "移动动画", "变换动画", "特效动画", "自定义"])
            category_combo.setEditable(True)
            layout.addRow("分类:", category_combo)

            # 复杂度
            complexity_combo = QComboBox()
            complexity_combo.addItems(["简单", "中等", "复杂"])
            layout.addRow("复杂度:", complexity_combo)

            # 预估时长
            duration_edit = QLineEdit()
            duration_edit.setPlaceholderText("例如: 2-3秒")
            layout.addRow("预估时长:", duration_edit)

            # 关键词
            keywords_edit = QLineEdit()
            keywords_edit.setPlaceholderText("用逗号分隔关键词...")
            layout.addRow("关键词:", keywords_edit)

            # 按钮
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            save_btn = QPushButton("保存")
            save_btn.clicked.connect(lambda: self.save_template_data(
                name_edit.text(), category_combo.currentText(),
                complexity_combo.currentText(), duration_edit.text(),
                keywords_edit.text(), description, dialog
            ))
            button_layout.addWidget(save_btn)

            cancel_btn = QPushButton("取消")
            cancel_btn.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_btn)

            layout.addRow(button_layout)

            dialog.exec()

        except Exception as e:
            logger.error(f"保存模板失败: {e}")

    def save_template_data(self, name: str, category: str, complexity: str,
                          duration: str, keywords: str, description: str, dialog: QDialog):
        """保存模板数据"""
        try:
            if not name.strip():
                QMessageBox.warning(dialog, "警告", "请输入模板名称")
                return

            template = {
                "name": name.strip(),
                "description": description,
                "category": category,
                "complexity": complexity,
                "duration": duration.strip() or "1-2秒",
                "keywords": [kw.strip() for kw in keywords.split(",") if kw.strip()],
                "created_at": datetime.now().isoformat(),
                "usage_count": 0
            }

            self.template_manager.user_templates.append(template)
            self.template_manager.save_user_templates()

            # 更新用户模板显示
            self.update_user_templates_display()

            dialog.accept()
            QMessageBox.information(self, "成功", f"模板 '{name}' 已保存")

        except Exception as e:
            logger.error(f"保存模板数据失败: {e}")

    def update_user_templates_display(self):
        """更新用户模板显示"""
        try:
            self.user_template_list.clear()

            for template in self.template_manager.user_templates:
                item_text = f"{template['name']} ({template.get('complexity', '未知')})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, template)
                item.setToolTip(template['description'])

                self.user_template_list.addItem(item)

        except Exception as e:
            logger.error(f"更新用户模板显示失败: {e}")

    def edit_user_template(self):
        """编辑用户模板"""
        current_item = self.user_template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个模板")
            return

        # TODO: 实现模板编辑功能
        QMessageBox.information(self, "提示", "模板编辑功能将在后续版本中实现")

    def delete_user_template(self):
        """删除用户模板"""
        try:
            current_item = self.user_template_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个模板")
                return

            template = current_item.data(Qt.ItemDataRole.UserRole)

            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除模板 '{template['name']}' 吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 从列表中移除
                self.template_manager.user_templates.remove(template)
                self.template_manager.save_user_templates()

                # 更新显示
                self.update_user_templates_display()

                QMessageBox.information(self, "成功", "模板已删除")

        except Exception as e:
            logger.error(f"删除用户模板失败: {e}")

    def apply_optimization_suggestions(self):
        """应用优化建议"""
        try:
            if not self.current_analysis:
                QMessageBox.warning(self, "警告", "请先分析当前描述")
                return

            current_description = self.description_edit.toPlainText()
            optimized_description = current_description

            # 基于分析结果优化描述
            if not self.current_analysis["duration_hints"]:
                optimized_description += "，持续时间约2秒"

            if not self.current_analysis["emotions"]:
                optimized_description += "，要有现代感和科技感"

            if self.current_analysis["complexity_score"] < 20:
                optimized_description += "，添加轻微的弹性效果和渐变色彩"

            # 更新描述
            self.description_edit.setPlainText(optimized_description)

            QMessageBox.information(self, "优化完成", "描述已根据建议进行优化")

        except Exception as e:
            logger.error(f"应用优化建议失败: {e}")

    def generate_smart_prompt(self):
        """生成智能Prompt"""
        try:
            description = self.description_edit.toPlainText().strip()
            if not description:
                QMessageBox.warning(self, "警告", "请先输入动画描述")
                return

            # 如果没有分析结果，先进行分析
            if not self.current_analysis:
                self.analyze_current_description()

            # 生成智能Prompt
            prompt = self.build_intelligent_prompt(description, self.current_analysis)

            # 更新Prompt显示
            self.prompt_edit.setPlainText(prompt)

            # 评估Prompt质量
            self.evaluate_prompt_quality(prompt)

            # 发送信号
            self.prompt_generated.emit(prompt)

        except Exception as e:
            logger.error(f"生成智能Prompt失败: {e}")

    def build_intelligent_prompt(self, description: str, analysis: Dict[str, Any]) -> str:
        """构建智能Prompt"""
        try:
            prompt_parts = []

            # 基础Prompt模板
            template = self.get_prompt_template()
            prompt_parts.append(template["header"])

            # 用户描述
            prompt_parts.append(f"用户描述: {description}")
            prompt_parts.append("")

            # 基于分析结果添加技术要求
            if analysis and analysis.get("tech_stack"):
                tech_requirements = []
                for tech in analysis["tech_stack"]:
                    tech_name = tech["technology"].upper()
                    if tech_name == "CSS":
                        tech_requirements.append("使用CSS3动画和过渡效果")
                    elif tech_name == "JAVASCRIPT":
                        tech_requirements.append("使用JavaScript实现动态交互")
                    elif tech_name == "SVG":
                        tech_requirements.append("使用SVG矢量动画")

                if tech_requirements:
                    prompt_parts.append("技术要求:")
                    for req in tech_requirements:
                        prompt_parts.append(f"- {req}")
                    prompt_parts.append("")

            # 基于复杂度添加性能要求
            if analysis:
                complexity = analysis.get("complexity_score", 0)
                if complexity > 70:
                    prompt_parts.append("性能要求:")
                    prompt_parts.append("- 优化动画性能，使用GPU加速")
                    prompt_parts.append("- 避免布局重排，优先使用transform属性")
                    prompt_parts.append("- 考虑降级方案以确保兼容性")
                    prompt_parts.append("")

            # 基于情感添加风格要求
            if analysis and analysis.get("emotions"):
                style_requirements = []
                for emotion in analysis["emotions"]:
                    emotion_type = emotion["emotion"]
                    if emotion_type == "energetic":
                        style_requirements.append("使用动感的缓动函数和快速的节奏")
                    elif emotion_type == "gentle":
                        style_requirements.append("使用柔和的过渡和优雅的缓动")
                    elif emotion_type == "playful":
                        style_requirements.append("添加俏皮的弹跳效果和明亮的色彩")

                if style_requirements:
                    prompt_parts.append("风格要求:")
                    for req in style_requirements:
                        prompt_parts.append(f"- {req}")
                    prompt_parts.append("")

            # 添加代码结构要求
            prompt_parts.extend(template["footer"])

            return "\n".join(prompt_parts)

        except Exception as e:
            logger.error(f"构建智能Prompt失败: {e}")
            return description

    def get_prompt_template(self) -> Dict[str, Any]:
        """获取Prompt模板"""
        templates = {
            "标准模板": {
                "header": [
                    "请生成符合以下要求的HTML动画代码:",
                    ""
                ],
                "footer": [
                    "代码结构要求:",
                    "1. 包含完整的HTML结构",
                    "2. CSS样式清晰分离",
                    "3. 动画可控制和暂停",
                    "4. 代码注释详细",
                    "5. 确保跨浏览器兼容性",
                    "",
                    "请提供完整可运行的代码。"
                ]
            },
            "创意模式": {
                "header": [
                    "作为创意动画设计师，请创造一个独特而吸引人的动画效果:",
                    ""
                ],
                "footer": [
                    "创意要求:",
                    "1. 追求视觉冲击力和美观度",
                    "2. 可以使用实验性CSS特性",
                    "3. 鼓励创新的动画组合",
                    "4. 注重用户体验和情感表达",
                    "5. 代码应该优雅且富有表现力",
                    "",
                    "请发挥创意，创造令人印象深刻的动画效果。"
                ]
            },
            "技术模式": {
                "header": [
                    "作为前端技术专家，请实现高性能的动画解决方案:",
                    ""
                ],
                "footer": [
                    "技术要求:",
                    "1. 优化动画性能，避免重排重绘",
                    "2. 使用现代CSS特性和最佳实践",
                    "3. 提供降级方案确保兼容性",
                    "4. 代码模块化且易于维护",
                    "5. 包含性能监控和调试信息",
                    "",
                    "请提供技术先进且性能优异的实现方案。"
                ]
            }
        }

        template_name = self.prompt_template_combo.currentText()
        return templates.get(template_name, templates["标准模板"])

    def optimize_current_prompt(self):
        """优化当前Prompt"""
        try:
            current_prompt = self.prompt_edit.toPlainText().strip()
            if not current_prompt:
                QMessageBox.warning(self, "警告", "请先生成Prompt")
                return

            # 简化的Prompt优化
            optimized_prompt = current_prompt

            # 添加缺失的技术要求
            if "GPU加速" not in optimized_prompt:
                optimized_prompt += "\n\n性能优化: 使用GPU加速的transform属性。"

            if "响应式" not in optimized_prompt:
                optimized_prompt += "\n响应式设计: 适配不同屏幕尺寸。"

            # 更新显示
            self.prompt_edit.setPlainText(optimized_prompt)

            QMessageBox.information(self, "优化完成", "Prompt已优化")

        except Exception as e:
            logger.error(f"优化Prompt失败: {e}")

    def validate_current_prompt(self):
        """验证当前Prompt"""
        try:
            prompt = self.prompt_edit.toPlainText().strip()
            if not prompt:
                QMessageBox.warning(self, "警告", "请先输入Prompt")
                return

            # 简化的Prompt验证
            validation_results = []

            # 检查基本结构
            if "用户描述" in prompt:
                validation_results.append("✅ 包含用户描述")
            else:
                validation_results.append("❌ 缺少用户描述")

            if "技术要求" in prompt or "代码结构" in prompt:
                validation_results.append("✅ 包含技术要求")
            else:
                validation_results.append("⚠️ 建议添加技术要求")

            if len(prompt) > 200:
                validation_results.append("✅ Prompt长度充足")
            else:
                validation_results.append("⚠️ Prompt可能过短")

            # 显示验证结果
            result_text = "Prompt验证结果:\n\n" + "\n".join(validation_results)
            QMessageBox.information(self, "验证结果", result_text)

        except Exception as e:
            logger.error(f"验证Prompt失败: {e}")

    def evaluate_prompt_quality(self, prompt: str):
        """评估Prompt质量"""
        try:
            score = 0

            # 长度评分
            if 100 <= len(prompt) <= 1000:
                score += 25
            elif len(prompt) > 50:
                score += 15

            # 结构评分
            if "用户描述" in prompt:
                score += 20
            if "技术要求" in prompt or "代码结构" in prompt:
                score += 20
            if "性能" in prompt:
                score += 15

            # 具体性评分
            specific_keywords = ["HTML", "CSS", "JavaScript", "动画", "效果"]
            found_keywords = sum(1 for kw in specific_keywords if kw in prompt)
            score += found_keywords * 4

            # 更新质量显示
            if score >= 80:
                quality_text = f"质量: 优秀 ({score}/100)"
                color = "green"
            elif score >= 60:
                quality_text = f"质量: 良好 ({score}/100)"
                color = "orange"
            else:
                quality_text = f"质量: 需改进 ({score}/100)"
                color = "red"

            self.prompt_quality_label.setText(quality_text)
            self.prompt_quality_label.setStyleSheet(f"color: {color}; font-weight: bold;")

        except Exception as e:
            logger.error(f"评估Prompt质量失败: {e}")

    def on_prompt_template_changed(self, template_name: str):
        """Prompt模板改变事件"""
        # 如果当前有描述，重新生成Prompt
        if self.description_edit.toPlainText().strip():
            self.generate_smart_prompt()

    def load_prompt_template(self):
        """加载Prompt模板"""
        self.generate_smart_prompt()

    def get_current_description_data(self) -> Dict[str, Any]:
        """获取当前描述数据"""
        return {
            "description": self.description_edit.toPlainText(),
            "analysis": self.current_analysis,
            "prompt": self.prompt_edit.toPlainText(),
            "timestamp": datetime.now().isoformat()
        }

    def load_description_data(self, data: Dict[str, Any]):
        """加载描述数据"""
        try:
            self.description_edit.setPlainText(data.get("description", ""))
            self.prompt_edit.setPlainText(data.get("prompt", ""))
            self.current_analysis = data.get("analysis")

            if self.current_analysis:
                self.update_analysis_display()

        except Exception as e:
            logger.error(f"加载描述数据失败: {e}")

    def save_current_description_to_history(self, entry_type: HistoryEntryType = HistoryEntryType.MANUAL_INPUT):
        """保存当前描述到历史记录"""
        try:
            description = self.description_edit.toPlainText().strip()
            if description:
                self.current_entry_id = self.history_manager.add_entry(
                    description=description,
                    entry_type=entry_type,
                    language="zh",  # 默认中文，实际应该检测
                    analysis_result=self.current_analysis,
                    prompt_generated=self.prompt_edit.toPlainText(),
                    quality_score=self.current_analysis.get("confidence", 0) if self.current_analysis else None
                )

                # 刷新历史显示
                self.refresh_history()

        except Exception as e:
            logger.error(f"保存描述到历史失败: {e}")

    def refresh_history(self):
        """刷新历史记录显示"""
        try:
            self.history_list.clear()

            # 获取最近的历史记录
            recent_entries = self.history_manager.get_recent_entries(50)

            for entry in recent_entries:
                # 创建显示文本
                timestamp = datetime.fromisoformat(entry.timestamp)
                time_str = timestamp.strftime("%m-%d %H:%M")

                item_text = f"[{time_str}] {entry.description[:50]}..."
                if len(entry.description) <= 50:
                    item_text = f"[{time_str}] {entry.description}"

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, entry)

                # 根据类型设置图标和颜色
                type_colors = {
                    HistoryEntryType.MANUAL_INPUT: "#2196F3",
                    HistoryEntryType.TEMPLATE_APPLIED: "#4CAF50",
                    HistoryEntryType.AI_GENERATED: "#FF9800",
                    HistoryEntryType.VOICE_INPUT: "#9C27B0",
                    HistoryEntryType.OPTIMIZED: "#F44336"
                }

                color = type_colors.get(entry.entry_type, "#666")
                item.setForeground(QColor(color))

                # 设置工具提示
                tooltip = f"类型: {entry.entry_type.value}\n"
                tooltip += f"语言: {entry.language}\n"
                tooltip += f"使用次数: {entry.usage_count}\n"
                if entry.quality_score:
                    tooltip += f"质量分数: {entry.quality_score:.2f}\n"
                tooltip += f"完整描述: {entry.description}"

                item.setToolTip(tooltip)

                self.history_list.addItem(item)

            # 更新统计信息
            self.update_history_statistics()

        except Exception as e:
            logger.error(f"刷新历史记录失败: {e}")

    def update_history_statistics(self):
        """更新历史统计信息"""
        try:
            stats = self.history_manager.get_statistics()

            if stats:
                stats_text = f"总记录数: {stats.get('total_entries', 0)}\n"
                stats_text += f"总使用次数: {stats.get('total_usage', 0)}\n"
                stats_text += f"平均质量: {stats.get('average_quality', 0):.2f}\n"
                stats_text += f"最近7天: {stats.get('recent_entries_count', 0)} 条"

                self.history_stats_label.setText(stats_text)
            else:
                self.history_stats_label.setText("暂无统计信息")

        except Exception as e:
            logger.error(f"更新历史统计失败: {e}")

    def search_history(self, query: str):
        """搜索历史记录"""
        try:
            if not query.strip():
                self.refresh_history()
                return

            # 搜索匹配的条目
            search_results = self.history_manager.search_entries(query)

            # 更新显示
            self.history_list.clear()

            for entry in search_results:
                timestamp = datetime.fromisoformat(entry.timestamp)
                time_str = timestamp.strftime("%m-%d %H:%M")

                item_text = f"[{time_str}] {entry.description[:50]}..."
                if len(entry.description) <= 50:
                    item_text = f"[{time_str}] {entry.description}"

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, entry)

                # 高亮搜索关键词
                if query.lower() in entry.description.lower():
                    item.setBackground(QColor("#FFEB3B"))

                self.history_list.addItem(item)

        except Exception as e:
            logger.error(f"搜索历史记录失败: {e}")

    def filter_history(self):
        """过滤历史记录"""
        try:
            type_filter = self.history_type_filter.currentText()
            lang_filter = self.history_lang_filter.currentText()

            # 获取所有条目
            all_entries = self.history_manager.get_recent_entries(200)

            # 应用过滤器
            filtered_entries = all_entries

            if type_filter != "全部":
                type_map = {
                    "手动输入": HistoryEntryType.MANUAL_INPUT,
                    "模板应用": HistoryEntryType.TEMPLATE_APPLIED,
                    "AI生成": HistoryEntryType.AI_GENERATED,
                    "语音输入": HistoryEntryType.VOICE_INPUT,
                    "优化结果": HistoryEntryType.OPTIMIZED
                }

                target_type = type_map.get(type_filter)
                if target_type:
                    filtered_entries = [e for e in filtered_entries if e.entry_type == target_type]

            if lang_filter != "全部":
                lang_map = {"中文": "zh", "English": "en", "日本語": "ja"}
                target_lang = lang_map.get(lang_filter, lang_filter)
                filtered_entries = [e for e in filtered_entries if e.language == target_lang]

            # 更新显示
            self.history_list.clear()

            for entry in filtered_entries:
                timestamp = datetime.fromisoformat(entry.timestamp)
                time_str = timestamp.strftime("%m-%d %H:%M")

                item_text = f"[{time_str}] {entry.description[:50]}..."
                if len(entry.description) <= 50:
                    item_text = f"[{time_str}] {entry.description}"

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, entry)

                self.history_list.addItem(item)

        except Exception as e:
            logger.error(f"过滤历史记录失败: {e}")

    def load_history_entry(self, item: QListWidgetItem):
        """加载历史条目"""
        try:
            entry = item.data(Qt.ItemDataRole.UserRole)
            if entry:
                # 加载描述
                self.description_edit.setPlainText(entry.description)

                # 加载分析结果
                if entry.analysis_result:
                    self.current_analysis = entry.analysis_result
                    self.update_analysis_display()

                # 加载Prompt
                if entry.prompt_generated:
                    self.prompt_edit.setPlainText(entry.prompt_generated)

                # 更新使用次数
                self.history_manager.update_entry_quality(entry.id, entry.usage_count + 1)

                logger.info(f"已加载历史条目: {entry.id}")

        except Exception as e:
            logger.error(f"加载历史条目失败: {e}")

    def load_selected_history(self):
        """加载选中的历史记录"""
        current_item = self.history_list.currentItem()
        if current_item:
            self.load_history_entry(current_item)
        else:
            QMessageBox.warning(self, "警告", "请先选择一个历史记录")

    def delete_selected_history(self):
        """删除选中的历史记录"""
        try:
            current_item = self.history_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个历史记录")
                return

            entry = current_item.data(Qt.ItemDataRole.UserRole)

            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除这条历史记录吗？\n\n{entry.description[:100]}...",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                if self.history_manager.delete_entry(entry.id):
                    self.refresh_history()
                    QMessageBox.information(self, "成功", "历史记录已删除")

        except Exception as e:
            logger.error(f"删除历史记录失败: {e}")

    def clear_history(self):
        """清空历史记录"""
        try:
            reply = QMessageBox.question(
                self, "确认清空",
                "确定要清空所有历史记录吗？此操作不可恢复！",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.history_manager.clear_history(confirm=True)
                self.refresh_history()
                QMessageBox.information(self, "成功", "历史记录已清空")

        except Exception as e:
            logger.error(f"清空历史记录失败: {e}")

    def export_history(self):
        """导出历史记录"""
        try:
            from PyQt6.QtWidgets import QFileDialog

            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出历史记录", "description_history.json",
                "JSON文件 (*.json);;CSV文件 (*.csv);;所有文件 (*)"
            )

            if file_path:
                format_type = "csv" if file_path.endswith(".csv") else "json"
                self.history_manager.export_history(file_path, format_type)
                QMessageBox.information(self, "成功", f"历史记录已导出到:\n{file_path}")

        except Exception as e:
            logger.error(f"导出历史记录失败: {e}")

    def show_history_context_menu(self, position):
        """显示历史记录上下文菜单"""
        try:
            item = self.history_list.itemAt(position)
            if not item:
                return

            menu = QMenu(self)

            load_action = QAction("📋 加载", self)
            load_action.triggered.connect(lambda: self.load_history_entry(item))
            menu.addAction(load_action)

            delete_action = QAction("❌ 删除", self)
            delete_action.triggered.connect(self.delete_selected_history)
            menu.addAction(delete_action)

            menu.addSeparator()

            details_action = QAction("ℹ️ 详情", self)
            details_action.triggered.connect(lambda: self.show_history_details(item))
            menu.addAction(details_action)

            menu.exec(self.history_list.mapToGlobal(position))

        except Exception as e:
            logger.error(f"显示上下文菜单失败: {e}")

    def show_history_details(self, item: QListWidgetItem):
        """显示历史记录详情"""
        try:
            entry = item.data(Qt.ItemDataRole.UserRole)
            if not entry:
                return

            details = self.history_manager.get_entry_details(entry.id)
            if details:
                # 创建详情对话框
                dialog = QDialog(self)
                dialog.setWindowTitle("历史记录详情")
                dialog.setMinimumSize(500, 400)

                layout = QVBoxLayout(dialog)

                # 基本信息
                basic_info = details["basic_info"]
                info_text = f"ID: {basic_info['id']}\n"
                info_text += f"类型: {basic_info['type']}\n"
                info_text += f"时间: {basic_info['timestamp']}\n"
                info_text += f"语言: {basic_info['language']}\n\n"
                info_text += f"描述:\n{basic_info['description']}"

                info_label = QLabel(info_text)
                info_label.setWordWrap(True)
                layout.addWidget(info_label)

                # 使用信息
                usage_info = details["usage_info"]
                usage_text = f"使用次数: {usage_info['usage_count']}\n"
                usage_text += f"成功率: {usage_info['success_rate']:.2f}\n"
                if usage_info['quality_score']:
                    usage_text += f"质量分数: {usage_info['quality_score']:.2f}"

                usage_label = QLabel(usage_text)
                layout.addWidget(usage_label)

                # 关闭按钮
                close_btn = QPushButton("关闭")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn)

                dialog.exec()

        except Exception as e:
            logger.error(f"显示历史详情失败: {e}")

    def create_template_panel(self):
        """创建模板面板"""
        pass

    def update_visual_preview(self):
        """更新可视化预览"""
        try:
            if hasattr(self, 'visual_previewer'):
                description = self.description_edit.toPlainText().strip()
                if description:
                    self.visual_previewer.update_preview_from_description(description, self.current_analysis)
                else:
                    QMessageBox.warning(self, "警告", "请先输入动画描述")

        except Exception as e:
            logger.error(f"更新可视化预览失败: {e}")

    def on_preview_updated(self, elements: list):
        """预览更新事件"""
        try:
            logger.info(f"可视化预览已更新，包含 {len(elements)} 个元素")

        except Exception as e:
            logger.error(f"处理预览更新事件失败: {e}")

    def on_animation_state_changed(self, is_playing: bool):
        """动画状态改变事件"""
        try:
            if is_playing:
                logger.debug("预览动画开始播放")
            else:
                logger.debug("预览动画已暂停")

        except Exception as e:
            logger.error(f"处理动画状态改变失败: {e}")

    def export_preview_image(self):
        """导出预览图片"""
        try:
            if hasattr(self, 'visual_previewer'):
                from PyQt6.QtWidgets import QFileDialog

                file_path, _ = QFileDialog.getSaveFileName(
                    self, "导出预览图片", "animation_preview.png",
                    "PNG图片 (*.png);;JPEG图片 (*.jpg);;所有文件 (*)"
                )

                if file_path:
                    self.visual_previewer.export_preview_as_image(file_path)
                    QMessageBox.information(self, "成功", f"预览图片已导出到:\n{file_path}")

        except Exception as e:
            logger.error(f"导出预览图片失败: {e}")

    def get_smart_suggestions(self):
        """获取智能建议"""
        try:
            description = self.description_edit.toPlainText().strip()
            if not description:
                QMessageBox.warning(self, "警告", "请先输入动画描述")
                return

            # 如果没有分析结果，先进行分析
            if not self.current_analysis:
                self.analyze_current_description()

            # 获取模板建议
            template_suggestions = self.template_manager.get_smart_suggestions(self.current_analysis)

            # 更新建议列表
            self.suggestions_list.clear()

            for suggestion in template_suggestions:
                item_text = f"{suggestion['name']} - {suggestion.get('complexity', '未知')}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, suggestion)
                item.setToolTip(suggestion['description'])

                # 根据复杂度设置颜色
                if suggestion.get('complexity') == "简单":
                    item.setBackground(QColor("#E8F5E8"))
                elif suggestion.get('complexity') == "中等":
                    item.setBackground(QColor("#FFF3E0"))
                else:
                    item.setBackground(QColor("#FFEBEE"))

                self.suggestions_list.addItem(item)

            # 更新质量评估
            self.update_quality_assessment()

        except Exception as e:
            logger.error(f"获取智能建议失败: {e}")

    def apply_suggestion(self, item: QListWidgetItem):
        """应用建议"""
        try:
            suggestion = item.data(Qt.ItemDataRole.UserRole)
            if suggestion:
                self.apply_template(suggestion)

        except Exception as e:
            logger.error(f"应用建议失败: {e}")

    def apply_selected_suggestion(self):
        """应用选中的建议"""
        try:
            current_item = self.suggestions_list.currentItem()
            if current_item:
                self.apply_suggestion(current_item)
            else:
                QMessageBox.warning(self, "警告", "请先选择一个建议")

        except Exception as e:
            logger.error(f"应用选中建议失败: {e}")

    def refresh_suggestions(self):
        """刷新建议"""
        self.get_smart_suggestions()

    def update_quality_assessment(self):
        """更新质量评估"""
        try:
            from core.smart_description_completer import DescriptionValidator

            description = self.description_edit.toPlainText().strip()
            if not description:
                self.quality_progress.setValue(0)
                self.quality_details.clear()
                return

            validator = DescriptionValidator()
            validation_result = validator.validate_description(description)

            # 更新质量进度条
            score = validation_result.get("score", 0)
            self.quality_progress.setValue(score)

            # 更新质量详情
            details = []

            if validation_result.get("strengths"):
                details.append("✅ 优点:")
                for strength in validation_result["strengths"]:
                    details.append(f"  • {strength}")
                details.append("")

            if validation_result.get("issues"):
                details.append("❌ 问题:")
                for issue in validation_result["issues"]:
                    details.append(f"  • {issue}")
                details.append("")

            if validation_result.get("suggestions"):
                details.append("💡 建议:")
                for suggestion in validation_result["suggestions"]:
                    details.append(f"  • {suggestion}")

            self.quality_details.setPlainText("\n".join(details))

        except Exception as e:
            logger.error(f"更新质量评估失败: {e}")

    def create_template_panel(self):
        """创建模板面板"""
        pass
