"""
AI Animation Studio - 增强AI生成器
基于自然语言的智能动画生成系统，支持多模型对比、实时预览、智能优化等
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QTextEdit, QComboBox, QSpinBox, QCheckBox, QTabWidget, QListWidget,
    QListWidgetItem, QMessageBox, QProgressBar, QSplitter, QLineEdit,
    QSlider, QFrame, QScrollArea, QTreeWidget, QTreeWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QToolButton,
    QButtonGroup, QRadioButton, QDialog, QFormLayout, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QPropertyAnimation
from PyQt6.QtGui import QFont, QColor, QAction, QPixmap, QPainter

from core.data_structures import AnimationSolution, TechStack
from core.logger import get_logger

logger = get_logger("enhanced_ai_generator")


class PromptOptimizer:
    """提示词优化器"""
    
    def __init__(self):
        self.optimization_rules = {
            "clarity": [
                "使用具体的动画描述词汇",
                "明确指定动画的开始和结束状态",
                "描述动画的时长和缓动效果"
            ],
            "technical": [
                "指定使用的技术栈（CSS、JS、SVG等）",
                "说明浏览器兼容性要求",
                "描述性能优化需求"
            ],
            "creative": [
                "添加视觉风格描述",
                "指定色彩方案",
                "描述用户交互方式"
            ]
        }
    
    def optimize_prompt(self, original_prompt: str, optimization_type: str = "balanced") -> str:
        """优化提示词"""
        try:
            optimized = original_prompt
            
            # 添加技术规范
            if "CSS" not in optimized and "JavaScript" not in optimized:
                optimized += "\n\n技术要求：使用现代CSS3动画和JavaScript，确保跨浏览器兼容性。"
            
            # 添加性能要求
            if "性能" not in optimized:
                optimized += "\n性能要求：动画应流畅运行，避免卡顿，优化GPU加速。"
            
            # 添加代码结构要求
            if "结构" not in optimized:
                optimized += "\n代码结构：请提供完整的HTML、CSS和JavaScript代码，代码应清晰注释。"
            
            return optimized.strip()
            
        except Exception as e:
            logger.error(f"优化提示词失败: {e}")
            return original_prompt
    
    def analyze_prompt_quality(self, prompt: str) -> Dict[str, Any]:
        """分析提示词质量"""
        analysis = {
            "score": 0,
            "suggestions": [],
            "strengths": [],
            "weaknesses": []
        }
        
        try:
            # 长度检查
            if len(prompt) < 50:
                analysis["weaknesses"].append("提示词过短，可能缺少关键信息")
                analysis["suggestions"].append("添加更多动画细节描述")
            elif len(prompt) > 1000:
                analysis["weaknesses"].append("提示词过长，可能包含冗余信息")
                analysis["suggestions"].append("精简提示词，突出核心需求")
            else:
                analysis["strengths"].append("提示词长度适中")
                analysis["score"] += 20
            
            # 技术词汇检查
            tech_keywords = ["CSS", "JavaScript", "HTML", "动画", "过渡", "变换"]
            found_tech = sum(1 for keyword in tech_keywords if keyword in prompt)
            
            if found_tech >= 3:
                analysis["strengths"].append("包含丰富的技术描述")
                analysis["score"] += 30
            elif found_tech >= 1:
                analysis["score"] += 15
            else:
                analysis["weaknesses"].append("缺少技术规格描述")
                analysis["suggestions"].append("添加技术实现要求")
            
            # 视觉描述检查
            visual_keywords = ["颜色", "大小", "位置", "形状", "效果", "风格"]
            found_visual = sum(1 for keyword in visual_keywords if keyword in prompt)
            
            if found_visual >= 3:
                analysis["strengths"].append("视觉描述详细")
                analysis["score"] += 25
            elif found_visual >= 1:
                analysis["score"] += 10
            else:
                analysis["weaknesses"].append("缺少视觉效果描述")
                analysis["suggestions"].append("添加视觉风格和效果描述")
            
            # 交互描述检查
            interaction_keywords = ["点击", "悬停", "滚动", "拖拽", "触摸"]
            found_interaction = sum(1 for keyword in interaction_keywords if keyword in prompt)
            
            if found_interaction >= 1:
                analysis["strengths"].append("包含交互描述")
                analysis["score"] += 25
            else:
                analysis["suggestions"].append("考虑添加用户交互方式")
            
            # 确保分数在0-100之间
            analysis["score"] = min(100, max(0, analysis["score"]))
            
        except Exception as e:
            logger.error(f"分析提示词质量失败: {e}")
        
        return analysis


class MultiModelGenerator(QThread):
    """多模型生成器"""
    
    result_ready = pyqtSignal(str, dict)  # model_name, result
    all_completed = pyqtSignal(list)      # all_results
    progress_update = pyqtSignal(str)     # status_message
    error_occurred = pyqtSignal(str, str) # model_name, error_message
    
    def __init__(self, prompt: str, models: List[str]):
        super().__init__()
        self.prompt = prompt
        self.models = models
        self.results = {}
        self.completed_count = 0
    
    def run(self):
        """执行多模型生成"""
        try:
            from core.ai_service_manager import ai_service_manager, AIServiceType
            
            for model_name in self.models:
                try:
                    self.progress_update.emit(f"正在使用 {model_name} 生成...")
                    
                    # 根据模型名称确定服务类型
                    if "gpt" in model_name.lower():
                        service = AIServiceType.OPENAI
                    elif "claude" in model_name.lower():
                        service = AIServiceType.CLAUDE
                    elif "gemini" in model_name.lower():
                        service = AIServiceType.GEMINI
                    else:
                        continue
                    
                    # 生成动画代码
                    response = ai_service_manager.generate_animation_code(self.prompt, service)
                    
                    if response:
                        result = {
                            "content": response.content,
                            "tokens_used": response.tokens_used,
                            "cost": response.cost,
                            "response_time": response.response_time,
                            "cached": response.cached,
                            "service": service.value,
                            "model": response.model
                        }
                        
                        self.results[model_name] = result
                        self.result_ready.emit(model_name, result)
                    else:
                        self.error_occurred.emit(model_name, "生成失败")
                    
                    self.completed_count += 1
                    
                except Exception as e:
                    logger.error(f"模型 {model_name} 生成失败: {e}")
                    self.error_occurred.emit(model_name, str(e))
            
            # 所有模型完成
            self.all_completed.emit(list(self.results.values()))
            
        except Exception as e:
            logger.error(f"多模型生成失败: {e}")
            self.error_occurred.emit("all", str(e))


class EnhancedAIGenerator(QWidget):
    """增强AI生成器"""
    
    # 信号定义
    solution_generated = pyqtSignal(dict)        # 方案生成信号
    generation_started = pyqtSignal()            # 生成开始信号
    generation_completed = pyqtSignal(list)      # 生成完成信号
    prompt_optimized = pyqtSignal(str)           # 提示词优化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.prompt_optimizer = PromptOptimizer()
        self.generation_history = []
        self.current_results = {}
        self.comparison_mode = False
        
        self.setup_ui()
        self.setup_connections()
        
        logger.info("增强AI生成器初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题和模式切换
        header_layout = QHBoxLayout()
        
        title_label = QLabel("AI动画生成器")
        title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 生成模式选择
        mode_group = QButtonGroup(self)
        
        self.single_mode_rb = QRadioButton("单模型生成")
        self.single_mode_rb.setChecked(True)
        mode_group.addButton(self.single_mode_rb)
        header_layout.addWidget(self.single_mode_rb)
        
        self.multi_mode_rb = QRadioButton("多模型对比")
        mode_group.addButton(self.multi_mode_rb)
        header_layout.addWidget(self.multi_mode_rb)
        
        self.batch_mode_rb = QRadioButton("批量生成")
        mode_group.addButton(self.batch_mode_rb)
        header_layout.addWidget(self.batch_mode_rb)
        
        layout.addLayout(header_layout)
        
        # 主要内容区域
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：输入和配置
        left_panel = self.create_input_panel()
        content_splitter.addWidget(left_panel)
        
        # 右侧：结果和对比
        right_panel = self.create_results_panel()
        content_splitter.addWidget(right_panel)
        
        content_splitter.setSizes([400, 600])
        layout.addWidget(content_splitter)
        
        # 底部控制栏
        control_bar = self.create_control_bar()
        layout.addWidget(control_bar)
    
    def create_input_panel(self):
        """创建输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 自然语言输入
        input_group = QGroupBox("动画描述")
        input_layout = QVBoxLayout(input_group)
        
        # 描述输入
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText(
            "请用自然语言描述您想要的动画效果...\n\n"
            "例如：\n"
            "- 一个红色的方块从左边滑入，然后旋转360度\n"
            "- 文字逐个淡入显示，带有弹跳效果\n"
            "- 卡片翻转动画，显示背面内容"
        )
        self.description_edit.setMinimumHeight(120)
        input_layout.addWidget(self.description_edit)
        
        # 快速输入按钮
        quick_input_layout = QHBoxLayout()
        
        quick_buttons = [
            ("淡入效果", "元素从透明逐渐显示"),
            ("滑动效果", "元素从一侧滑入视图"),
            ("缩放效果", "元素从小到大或从大到小变化"),
            ("旋转效果", "元素围绕中心点旋转"),
            ("弹跳效果", "元素带有弹性动画效果")
        ]
        
        for text, description in quick_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, desc=description: self.add_quick_description(desc))
            btn.setMaximumWidth(80)
            quick_input_layout.addWidget(btn)
        
        input_layout.addLayout(quick_input_layout)
        
        layout.addWidget(input_group)
        
        # 智能提示词生成
        prompt_group = QGroupBox("智能提示词")
        prompt_layout = QVBoxLayout(prompt_group)
        
        # 提示词优化控制
        prompt_control_layout = QHBoxLayout()
        
        optimize_btn = QPushButton("🧠 智能优化")
        optimize_btn.clicked.connect(self.optimize_prompt)
        prompt_control_layout.addWidget(optimize_btn)
        
        analyze_btn = QPushButton("📊 质量分析")
        analyze_btn.clicked.connect(self.analyze_prompt)
        prompt_control_layout.addWidget(analyze_btn)
        
        template_btn = QPushButton("📋 使用模板")
        template_btn.clicked.connect(self.show_template_selector)
        prompt_control_layout.addWidget(template_btn)
        
        prompt_layout.addLayout(prompt_control_layout)
        
        # 提示词显示和编辑
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setMinimumHeight(150)
        self.prompt_edit.setPlaceholderText("智能生成的提示词将显示在这里...")
        prompt_layout.addWidget(self.prompt_edit)
        
        # 提示词质量指示器
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("质量评分:"))
        
        self.quality_score_label = QLabel("未评估")
        self.quality_score_label.setStyleSheet("font-weight: bold;")
        quality_layout.addWidget(self.quality_score_label)
        
        quality_layout.addStretch()
        
        self.quality_details_btn = QPushButton("详情")
        self.quality_details_btn.clicked.connect(self.show_quality_details)
        self.quality_details_btn.setEnabled(False)
        quality_layout.addWidget(self.quality_details_btn)
        
        prompt_layout.addLayout(quality_layout)
        
        layout.addWidget(prompt_group)
        
        # 生成设置
        settings_group = QGroupBox("生成设置")
        settings_layout = QFormLayout(settings_group)
        
        # 动画类型
        self.animation_type_combo = QComboBox()
        self.animation_type_combo.addItems([
            "自动检测", "CSS动画", "JavaScript动画", "SVG动画", 
            "Canvas动画", "WebGL动画", "混合动画"
        ])
        settings_layout.addRow("动画类型:", self.animation_type_combo)
        
        # 复杂度级别
        self.complexity_combo = QComboBox()
        self.complexity_combo.addItems(["简单", "中等", "复杂", "专业级"])
        self.complexity_combo.setCurrentText("中等")
        settings_layout.addRow("复杂度:", self.complexity_combo)
        
        # 浏览器兼容性
        self.compatibility_combo = QComboBox()
        self.compatibility_combo.addItems(["现代浏览器", "IE11+", "全兼容"])
        settings_layout.addRow("兼容性:", self.compatibility_combo)
        
        # 性能优先级
        self.performance_combo = QComboBox()
        self.performance_combo.addItems(["平衡", "性能优先", "效果优先"])
        settings_layout.addRow("性能:", self.performance_combo)
        
        # 代码风格
        self.code_style_combo = QComboBox()
        self.code_style_combo.addItems(["标准", "简洁", "详细注释", "模块化"])
        settings_layout.addRow("代码风格:", self.code_style_combo)
        
        layout.addWidget(settings_group)
        
        # 高级选项
        advanced_group = QGroupBox("高级选项")
        advanced_layout = QVBoxLayout(advanced_group)
        
        # 启用实验性功能
        self.experimental_cb = QCheckBox("启用实验性功能")
        self.experimental_cb.setToolTip("使用最新的CSS和JS特性")
        advanced_layout.addWidget(self.experimental_cb)
        
        # 包含响应式设计
        self.responsive_cb = QCheckBox("包含响应式设计")
        self.responsive_cb.setChecked(True)
        advanced_layout.addWidget(self.responsive_cb)
        
        # 添加无障碍支持
        self.accessibility_cb = QCheckBox("添加无障碍支持")
        advanced_layout.addWidget(self.accessibility_cb)
        
        # 生成多个变体
        variation_layout = QHBoxLayout()
        variation_layout.addWidget(QLabel("生成变体数:"))
        
        self.variation_spin = QSpinBox()
        self.variation_spin.setRange(1, 5)
        self.variation_spin.setValue(1)
        variation_layout.addWidget(self.variation_spin)
        
        variation_layout.addStretch()
        advanced_layout.addLayout(variation_layout)
        
        layout.addWidget(advanced_group)
        
        layout.addStretch()
        
        return panel
    
    def create_results_panel(self):
        """创建结果面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 结果标签页
        self.results_tab = QTabWidget()
        
        # 生成结果标签页
        self.setup_generation_results_tab()
        
        # 模型对比标签页
        self.setup_model_comparison_tab()
        
        # 历史记录标签页
        self.setup_history_tab()
        
        layout.addWidget(self.results_tab)
        
        return panel
    
    def setup_generation_results_tab(self):
        """设置生成结果标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 结果列表
        self.results_list = QListWidget()
        self.results_list.itemSelectionChanged.connect(self.on_result_selected)
        self.results_list.itemDoubleClicked.connect(self.on_result_double_clicked)
        layout.addWidget(self.results_list)
        
        # 结果详情
        details_group = QGroupBox("生成详情")
        details_layout = QFormLayout(details_group)
        
        self.model_label = QLabel("-")
        details_layout.addRow("使用模型:", self.model_label)
        
        self.tokens_label = QLabel("-")
        details_layout.addRow("令牌消耗:", self.tokens_label)
        
        self.cost_label = QLabel("-")
        details_layout.addRow("生成费用:", self.cost_label)
        
        self.time_label = QLabel("-")
        details_layout.addRow("响应时间:", self.time_label)
        
        self.cached_label = QLabel("-")
        details_layout.addRow("缓存状态:", self.cached_label)
        
        layout.addWidget(details_group)
        
        # 操作按钮
        action_layout = QHBoxLayout()
        
        preview_btn = QPushButton("🔍 预览")
        preview_btn.clicked.connect(self.preview_selected_result)
        action_layout.addWidget(preview_btn)
        
        apply_btn = QPushButton("✅ 应用")
        apply_btn.clicked.connect(self.apply_selected_result)
        action_layout.addWidget(apply_btn)
        
        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(self.save_selected_result)
        action_layout.addWidget(save_btn)
        
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        self.results_tab.addTab(tab, "📝 生成结果")
    
    def setup_model_comparison_tab(self):
        """设置模型对比标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 对比表格
        self.comparison_table = QTableWidget()
        self.comparison_table.setColumnCount(6)
        self.comparison_table.setHorizontalHeaderLabels([
            "模型", "质量评分", "响应时间", "令牌消耗", "费用", "推荐度"
        ])
        self.comparison_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.comparison_table)
        
        # 对比分析
        analysis_group = QGroupBox("对比分析")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.comparison_analysis = QTextEdit()
        self.comparison_analysis.setMaximumHeight(100)
        self.comparison_analysis.setReadOnly(True)
        analysis_layout.addWidget(self.comparison_analysis)
        
        layout.addWidget(analysis_group)
        
        self.results_tab.addTab(tab, "⚖️ 模型对比")
    
    def setup_history_tab(self):
        """设置历史记录标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 历史记录列表
        self.history_list = QTreeWidget()
        self.history_list.setHeaderLabels(["时间", "描述", "模型", "状态"])
        self.history_list.itemDoubleClicked.connect(self.load_from_history)
        layout.addWidget(self.history_list)
        
        # 历史操作
        history_actions_layout = QHBoxLayout()
        
        reload_btn = QPushButton("🔄 重新生成")
        reload_btn.clicked.connect(self.regenerate_from_history)
        history_actions_layout.addWidget(reload_btn)
        
        clear_btn = QPushButton("🗑️ 清空历史")
        clear_btn.clicked.connect(self.clear_history)
        history_actions_layout.addWidget(clear_btn)
        
        export_btn = QPushButton("📤 导出历史")
        export_btn.clicked.connect(self.export_history)
        history_actions_layout.addWidget(export_btn)
        
        history_actions_layout.addStretch()
        
        layout.addLayout(history_actions_layout)
        
        self.results_tab.addTab(tab, "📚 历史记录")
    
    def create_control_bar(self):
        """创建控制栏"""
        bar = QFrame()
        bar.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(bar)
        
        # 生成按钮
        self.generate_btn = QPushButton("🚀 开始生成")
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5CBF60, stop:1 #55b059);
            }
            QPushButton:disabled {
                background: #cccccc;
            }
        """)
        self.generate_btn.clicked.connect(self.start_generation)
        layout.addWidget(self.generate_btn)
        
        # 停止按钮
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_generation)
        layout.addWidget(self.stop_btn)
        
        layout.addStretch()
        
        # 进度显示
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumWidth(200)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)
        
        return bar
    
    def setup_connections(self):
        """设置信号连接"""
        # 描述输入变化时自动生成提示词
        self.description_edit.textChanged.connect(self.on_description_changed)
        
        # 模式切换
        self.single_mode_rb.toggled.connect(self.on_mode_changed)
        self.multi_mode_rb.toggled.connect(self.on_mode_changed)
        self.batch_mode_rb.toggled.connect(self.on_mode_changed)
    
    def add_quick_description(self, description: str):
        """添加快速描述"""
        current_text = self.description_edit.toPlainText()
        if current_text:
            new_text = current_text + "\n" + description
        else:
            new_text = description
        
        self.description_edit.setPlainText(new_text)
    
    def on_description_changed(self):
        """描述改变事件"""
        # 延迟自动生成提示词
        if hasattr(self, 'auto_prompt_timer'):
            self.auto_prompt_timer.stop()
        
        self.auto_prompt_timer = QTimer()
        self.auto_prompt_timer.setSingleShot(True)
        self.auto_prompt_timer.timeout.connect(self.auto_generate_prompt)
        self.auto_prompt_timer.start(2000)  # 2秒延迟
    
    def auto_generate_prompt(self):
        """自动生成提示词"""
        description = self.description_edit.toPlainText().strip()
        if description:
            optimized_prompt = self.prompt_optimizer.optimize_prompt(description)
            self.prompt_edit.setPlainText(optimized_prompt)
    
    def optimize_prompt(self):
        """优化提示词"""
        try:
            current_prompt = self.prompt_edit.toPlainText()
            if not current_prompt:
                current_prompt = self.description_edit.toPlainText()
            
            if not current_prompt:
                QMessageBox.warning(self, "警告", "请先输入动画描述")
                return
            
            optimized = self.prompt_optimizer.optimize_prompt(current_prompt)
            self.prompt_edit.setPlainText(optimized)
            
            self.prompt_optimized.emit(optimized)
            self.status_label.setText("提示词已优化")
            
        except Exception as e:
            logger.error(f"优化提示词失败: {e}")
    
    def analyze_prompt(self):
        """分析提示词质量"""
        try:
            prompt = self.prompt_edit.toPlainText()
            if not prompt:
                QMessageBox.warning(self, "警告", "请先输入提示词")
                return
            
            analysis = self.prompt_optimizer.analyze_prompt_quality(prompt)
            
            # 更新质量评分显示
            score = analysis["score"]
            if score >= 80:
                color = "green"
                level = "优秀"
            elif score >= 60:
                color = "orange"
                level = "良好"
            else:
                color = "red"
                level = "需改进"
            
            self.quality_score_label.setText(f"{score}/100 ({level})")
            self.quality_score_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            
            # 保存分析结果
            self.current_analysis = analysis
            self.quality_details_btn.setEnabled(True)
            
        except Exception as e:
            logger.error(f"分析提示词失败: {e}")
    
    def show_quality_details(self):
        """显示质量详情"""
        if not hasattr(self, 'current_analysis'):
            return
        
        analysis = self.current_analysis
        
        details = []
        details.append(f"质量评分: {analysis['score']}/100")
        details.append("")
        
        if analysis['strengths']:
            details.append("✅ 优点:")
            for strength in analysis['strengths']:
                details.append(f"  • {strength}")
            details.append("")
        
        if analysis['weaknesses']:
            details.append("❌ 不足:")
            for weakness in analysis['weaknesses']:
                details.append(f"  • {weakness}")
            details.append("")
        
        if analysis['suggestions']:
            details.append("💡 改进建议:")
            for suggestion in analysis['suggestions']:
                details.append(f"  • {suggestion}")
        
        QMessageBox.information(self, "提示词质量分析", "\n".join(details))
    
    def show_template_selector(self):
        """显示模板选择器"""
        # TODO: 实现模板选择对话框
        QMessageBox.information(self, "提示", "模板选择功能将在后续版本中实现")
    
    def on_mode_changed(self):
        """生成模式改变事件"""
        if self.multi_mode_rb.isChecked():
            self.comparison_mode = True
            self.results_tab.setCurrentIndex(1)  # 切换到对比标签页
        else:
            self.comparison_mode = False
            self.results_tab.setCurrentIndex(0)  # 切换到结果标签页
    
    def start_generation(self):
        """开始生成"""
        try:
            prompt = self.prompt_edit.toPlainText().strip()
            if not prompt:
                QMessageBox.warning(self, "警告", "请先输入提示词")
                return
            
            # 检查AI服务配置
            from core.ai_service_manager import ai_service_manager
            
            available_services = ai_service_manager.get_available_services()
            if not available_services:
                QMessageBox.warning(self, "警告", "没有可用的AI服务，请先配置API密钥")
                return
            
            # 更新UI状态
            self.generate_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            self.status_label.setText("正在生成...")
            
            self.generation_started.emit()
            
            # 根据模式选择生成方式
            if self.multi_mode_rb.isChecked():
                self.start_multi_model_generation(prompt)
            else:
                self.start_single_generation(prompt)
                
        except Exception as e:
            logger.error(f"开始生成失败: {e}")
            self.on_generation_error("all", str(e))
    
    def start_single_generation(self, prompt: str):
        """开始单模型生成"""
        try:
            from core.ai_service_manager import ai_service_manager
            
            # 使用首选服务生成
            response = ai_service_manager.generate_animation_code(prompt)
            
            if response:
                result = {
                    "content": response.content,
                    "model": response.model,
                    "service": response.service.value,
                    "tokens_used": response.tokens_used,
                    "cost": response.cost,
                    "response_time": response.response_time,
                    "cached": response.cached,
                    "timestamp": response.timestamp.isoformat()
                }
                
                self.on_single_generation_complete(result)
            else:
                self.on_generation_error("single", "生成失败")
                
        except Exception as e:
            logger.error(f"单模型生成失败: {e}")
            self.on_generation_error("single", str(e))
    
    def start_multi_model_generation(self, prompt: str):
        """开始多模型生成"""
        try:
            # 获取可用的模型列表
            models = ["gpt-4", "claude-3-5-sonnet", "gemini-2.0-flash"]
            
            # 启动多模型生成线程
            self.multi_generator = MultiModelGenerator(prompt, models)
            self.multi_generator.result_ready.connect(self.on_model_result_ready)
            self.multi_generator.all_completed.connect(self.on_multi_generation_complete)
            self.multi_generator.progress_update.connect(self.on_progress_update)
            self.multi_generator.error_occurred.connect(self.on_generation_error)
            
            self.multi_generator.start()
            
        except Exception as e:
            logger.error(f"多模型生成失败: {e}")
            self.on_generation_error("multi", str(e))

    def stop_generation(self):
        """停止生成"""
        try:
            if hasattr(self, 'multi_generator') and self.multi_generator.isRunning():
                self.multi_generator.terminate()
                self.multi_generator.wait()

            self.reset_ui_state()
            self.status_label.setText("生成已停止")

        except Exception as e:
            logger.error(f"停止生成失败: {e}")

    def reset_ui_state(self):
        """重置UI状态"""
        self.generate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

    def on_single_generation_complete(self, result: Dict[str, Any]):
        """单模型生成完成"""
        try:
            # 添加到结果列表
            self.current_results = {"single": result}

            # 更新结果显示
            self.update_results_display([result])

            # 添加到历史记录
            self.add_to_history(result)

            self.reset_ui_state()
            self.status_label.setText("生成完成")

            self.generation_completed.emit([result])

        except Exception as e:
            logger.error(f"处理单模型生成结果失败: {e}")

    def on_model_result_ready(self, model_name: str, result: Dict[str, Any]):
        """模型结果就绪"""
        try:
            self.current_results[model_name] = result

            # 更新对比表格
            self.update_comparison_table()

            self.status_label.setText(f"{model_name} 生成完成")

        except Exception as e:
            logger.error(f"处理模型结果失败: {e}")

    def on_multi_generation_complete(self, results: List[Dict[str, Any]]):
        """多模型生成完成"""
        try:
            # 更新结果显示
            self.update_results_display(results)

            # 生成对比分析
            self.generate_comparison_analysis()

            # 添加到历史记录
            for result in results:
                self.add_to_history(result)

            self.reset_ui_state()
            self.status_label.setText(f"多模型生成完成，共 {len(results)} 个结果")

            self.generation_completed.emit(results)

        except Exception as e:
            logger.error(f"处理多模型生成结果失败: {e}")

    def on_progress_update(self, message: str):
        """进度更新"""
        self.status_label.setText(message)

    def on_generation_error(self, model_name: str, error_message: str):
        """生成错误处理"""
        try:
            self.reset_ui_state()

            if model_name == "all":
                self.status_label.setText("生成失败")
                QMessageBox.critical(self, "生成错误", f"生成失败:\n{error_message}")
            else:
                self.status_label.setText(f"{model_name} 生成失败")
                logger.warning(f"模型 {model_name} 生成失败: {error_message}")

        except Exception as e:
            logger.error(f"处理生成错误失败: {e}")

    def update_results_display(self, results: List[Dict[str, Any]]):
        """更新结果显示"""
        try:
            self.results_list.clear()

            for i, result in enumerate(results):
                model = result.get("model", "未知模型")
                service = result.get("service", "未知服务")
                cached = " (缓存)" if result.get("cached", False) else ""

                item_text = f"{service.upper()} - {model}{cached}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, result)

                # 设置图标和颜色
                if result.get("cached", False):
                    item.setBackground(QColor("#E8F5E8"))  # 浅绿色表示缓存

                self.results_list.addItem(item)

            # 自动选择第一个结果
            if results:
                self.results_list.setCurrentRow(0)

        except Exception as e:
            logger.error(f"更新结果显示失败: {e}")

    def update_comparison_table(self):
        """更新对比表格"""
        try:
            results = list(self.current_results.values())
            self.comparison_table.setRowCount(len(results))

            for row, result in enumerate(results):
                # 模型名称
                model = f"{result.get('service', '').upper()} - {result.get('model', '')}"
                self.comparison_table.setItem(row, 0, QTableWidgetItem(model))

                # 质量评分（简化实现）
                quality_score = 85 + (row * 5)  # 模拟评分
                self.comparison_table.setItem(row, 1, QTableWidgetItem(f"{quality_score}/100"))

                # 响应时间
                response_time = result.get("response_time", 0)
                self.comparison_table.setItem(row, 2, QTableWidgetItem(f"{response_time:.2f}s"))

                # 令牌消耗
                tokens = result.get("tokens_used", 0)
                self.comparison_table.setItem(row, 3, QTableWidgetItem(str(tokens)))

                # 费用
                cost = result.get("cost", 0)
                self.comparison_table.setItem(row, 4, QTableWidgetItem(f"${cost:.4f}"))

                # 推荐度
                if row == 0:  # 第一个结果推荐度最高
                    recommendation = "⭐⭐⭐⭐⭐"
                elif row == 1:
                    recommendation = "⭐⭐⭐⭐"
                else:
                    recommendation = "⭐⭐⭐"

                self.comparison_table.setItem(row, 5, QTableWidgetItem(recommendation))

        except Exception as e:
            logger.error(f"更新对比表格失败: {e}")

    def generate_comparison_analysis(self):
        """生成对比分析"""
        try:
            if not self.current_results:
                return

            results = list(self.current_results.values())
            analysis_lines = []

            # 性能对比
            response_times = [r.get("response_time", 0) for r in results]
            fastest_idx = response_times.index(min(response_times))
            analysis_lines.append(f"🚀 最快响应: {list(self.current_results.keys())[fastest_idx]}")

            # 成本对比
            costs = [r.get("cost", 0) for r in results]
            cheapest_idx = costs.index(min(costs))
            analysis_lines.append(f"💰 最低成本: {list(self.current_results.keys())[cheapest_idx]}")

            # 缓存状态
            cached_count = sum(1 for r in results if r.get("cached", False))
            if cached_count > 0:
                analysis_lines.append(f"📦 缓存命中: {cached_count}/{len(results)} 个结果")

            # 总体建议
            analysis_lines.append("")
            analysis_lines.append("💡 建议:")

            if cached_count > 0:
                analysis_lines.append("• 缓存有效减少了响应时间和费用")

            if len(set(costs)) > 1:
                analysis_lines.append("• 不同模型的成本差异较大，可根据预算选择")

            analysis_lines.append("• 建议综合考虑质量、速度和成本选择最适合的模型")

            self.comparison_analysis.setPlainText("\n".join(analysis_lines))

        except Exception as e:
            logger.error(f"生成对比分析失败: {e}")

    def on_result_selected(self):
        """结果选择事件"""
        try:
            current_item = self.results_list.currentItem()
            if current_item:
                result = current_item.data(Qt.ItemDataRole.UserRole)

                # 更新详情显示
                self.model_label.setText(f"{result.get('service', '').upper()} - {result.get('model', '')}")
                self.tokens_label.setText(str(result.get("tokens_used", 0)))
                self.cost_label.setText(f"${result.get('cost', 0):.4f}")
                self.time_label.setText(f"{result.get('response_time', 0):.2f}s")
                self.cached_label.setText("是" if result.get("cached", False) else "否")

        except Exception as e:
            logger.error(f"处理结果选择失败: {e}")

    def on_result_double_clicked(self, item: QListWidgetItem):
        """结果双击事件"""
        self.preview_selected_result()

    def preview_selected_result(self):
        """预览选中的结果"""
        try:
            current_item = self.results_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个结果")
                return

            result = current_item.data(Qt.ItemDataRole.UserRole)
            content = result.get("content", "")

            # 创建预览对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("动画预览")
            dialog.setMinimumSize(800, 600)

            layout = QVBoxLayout(dialog)

            # 代码显示
            code_edit = QTextEdit()
            code_edit.setPlainText(content)
            code_edit.setReadOnly(True)
            layout.addWidget(code_edit)

            # 按钮
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.accept)
            button_layout.addWidget(close_btn)

            layout.addLayout(button_layout)

            dialog.exec()

        except Exception as e:
            logger.error(f"预览结果失败: {e}")

    def apply_selected_result(self):
        """应用选中的结果"""
        try:
            current_item = self.results_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个结果")
                return

            result = current_item.data(Qt.ItemDataRole.UserRole)

            # 创建动画解决方案对象
            solution = AnimationSolution(
                name=f"AI生成方案 ({result.get('service', '')})",
                description=f"使用{result.get('model', '')}生成",
                html_code=result.get("content", ""),
                tech_stack=TechStack.CSS_ANIMATION,
                recommended=True
            )

            # 发送信号
            self.solution_generated.emit(result)

            QMessageBox.information(self, "成功", "动画方案已应用")

        except Exception as e:
            logger.error(f"应用结果失败: {e}")

    def save_selected_result(self):
        """保存选中的结果"""
        try:
            current_item = self.results_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个结果")
                return

            result = current_item.data(Qt.ItemDataRole.UserRole)

            # 保存到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_animation_{timestamp}.html"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result.get("content", ""))

            QMessageBox.information(self, "成功", f"动画代码已保存到:\n{filename}")

        except Exception as e:
            logger.error(f"保存结果失败: {e}")

    def add_to_history(self, result: Dict[str, Any]):
        """添加到历史记录"""
        try:
            history_item = {
                "timestamp": datetime.now().isoformat(),
                "description": self.description_edit.toPlainText()[:100] + "...",
                "prompt": self.prompt_edit.toPlainText(),
                "result": result
            }

            self.generation_history.append(history_item)

            # 更新历史记录显示
            self.update_history_display()

            # 保存历史记录
            self.save_history()

        except Exception as e:
            logger.error(f"添加历史记录失败: {e}")

    def update_history_display(self):
        """更新历史记录显示"""
        try:
            self.history_list.clear()

            for item in reversed(self.generation_history[-20:]):  # 显示最近20条
                timestamp = datetime.fromisoformat(item["timestamp"])
                time_str = timestamp.strftime("%m-%d %H:%M")

                tree_item = QTreeWidgetItem([
                    time_str,
                    item["description"],
                    item["result"].get("model", ""),
                    "成功"
                ])
                tree_item.setData(0, Qt.ItemDataRole.UserRole, item)

                self.history_list.addTopLevelItem(tree_item)

        except Exception as e:
            logger.error(f"更新历史记录显示失败: {e}")

    def load_from_history(self, item: QTreeWidgetItem):
        """从历史记录加载"""
        try:
            history_data = item.data(0, Qt.ItemDataRole.UserRole)
            if history_data:
                self.description_edit.setPlainText(history_data.get("description", ""))
                self.prompt_edit.setPlainText(history_data.get("prompt", ""))

        except Exception as e:
            logger.error(f"从历史记录加载失败: {e}")

    def regenerate_from_history(self):
        """从历史记录重新生成"""
        try:
            current_item = self.history_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个历史记录")
                return

            history_data = current_item.data(0, Qt.ItemDataRole.UserRole)
            if history_data:
                self.load_from_history(current_item)
                self.start_generation()

        except Exception as e:
            logger.error(f"重新生成失败: {e}")

    def clear_history(self):
        """清空历史记录"""
        try:
            reply = QMessageBox.question(
                self, "确认", "确定要清空所有历史记录吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.generation_history.clear()
                self.history_list.clear()
                self.save_history()

                QMessageBox.information(self, "成功", "历史记录已清空")

        except Exception as e:
            logger.error(f"清空历史记录失败: {e}")

    def export_history(self):
        """导出历史记录"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_generation_history_{timestamp}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.generation_history, f, ensure_ascii=False, indent=2)

            QMessageBox.information(self, "成功", f"历史记录已导出到:\n{filename}")

        except Exception as e:
            logger.error(f"导出历史记录失败: {e}")

    def save_history(self):
        """保存历史记录"""
        try:
            with open("ai_generation_history.json", 'w', encoding='utf-8') as f:
                json.dump(self.generation_history, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")

    def load_history(self):
        """加载历史记录"""
        try:
            if os.path.exists("ai_generation_history.json"):
                with open("ai_generation_history.json", 'r', encoding='utf-8') as f:
                    self.generation_history = json.load(f)

                self.update_history_display()

        except Exception as e:
            logger.error(f"加载历史记录失败: {e}")

    def get_generation_statistics(self) -> Dict[str, Any]:
        """获取生成统计信息"""
        try:
            if not self.generation_history:
                return {}

            # 统计各种指标
            total_generations = len(self.generation_history)

            # 服务使用统计
            service_counts = {}
            total_cost = 0
            total_tokens = 0

            for item in self.generation_history:
                result = item.get("result", {})
                service = result.get("service", "unknown")

                service_counts[service] = service_counts.get(service, 0) + 1
                total_cost += result.get("cost", 0)
                total_tokens += result.get("tokens_used", 0)

            return {
                "total_generations": total_generations,
                "service_usage": service_counts,
                "total_cost": total_cost,
                "total_tokens": total_tokens,
                "average_cost": total_cost / total_generations if total_generations > 0 else 0,
                "average_tokens": total_tokens / total_generations if total_generations > 0 else 0
            }

        except Exception as e:
            logger.error(f"获取生成统计失败: {e}")
            return {}

    def export_generation_report(self) -> str:
        """导出生成报告"""
        try:
            stats = self.get_generation_statistics()

            report_lines = [
                "=== AI动画生成报告 ===",
                f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                f"总生成次数: {stats.get('total_generations', 0)}",
                f"总消耗令牌: {stats.get('total_tokens', 0)}",
                f"总费用: ${stats.get('total_cost', 0):.4f}",
                f"平均费用: ${stats.get('average_cost', 0):.4f}",
                "",
                "服务使用分布:"
            ]

            for service, count in stats.get('service_usage', {}).items():
                percentage = (count / stats.get('total_generations', 1)) * 100
                report_lines.append(f"  {service.upper()}: {count} 次 ({percentage:.1f}%)")

            return "\n".join(report_lines)

        except Exception as e:
            logger.error(f"导出生成报告失败: {e}")
            return "导出报告失败"
