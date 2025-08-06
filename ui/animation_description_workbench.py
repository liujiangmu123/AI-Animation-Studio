"""
AI Animation Studio - 动画描述工作台
集成所有描述相关功能的综合工作台
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget,
    QGroupBox, QLabel, QPushButton, QTextEdit, QListWidget,
    QComboBox, QCheckBox, QProgressBar, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor

from ui.enhanced_description_prompt_generator import EnhancedDescriptionPromptGenerator
from core.description_history_manager import DescriptionHistoryManager, HistoryEntryType
from core.multilingual_description_processor import MultilingualDescriptionProcessor
from core.smart_description_completer import SmartDescriptionCompleter, DescriptionValidator, DescriptionEnhancer
from core.logger import get_logger

logger = get_logger("animation_description_workbench")


class AnimationDescriptionWorkbench(QWidget):
    """动画描述工作台"""
    
    # 信号定义
    description_ready = pyqtSignal(str, dict)    # 描述准备就绪
    prompt_ready = pyqtSignal(str)               # Prompt准备就绪
    animation_requested = pyqtSignal(dict)       # 请求生成动画
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 核心组件
        self.description_generator = EnhancedDescriptionPromptGenerator()
        self.history_manager = DescriptionHistoryManager()
        self.multilingual_processor = MultilingualDescriptionProcessor()
        self.description_completer = SmartDescriptionCompleter()
        self.description_validator = DescriptionValidator()
        self.description_enhancer = DescriptionEnhancer()
        
        # 工作台状态
        self.current_language = "zh"
        self.auto_save_enabled = True
        self.real_time_validation = True
        
        self.setup_ui()
        self.setup_connections()
        
        logger.info("动画描述工作台初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题栏
        title_bar = self.create_title_bar()
        layout.addWidget(title_bar)
        
        # 主工作区
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：描述编辑区
        left_panel = self.create_description_editor()
        main_splitter.addWidget(left_panel)
        
        # 右侧：增强功能区
        right_panel = self.description_generator
        main_splitter.addWidget(right_panel)
        
        main_splitter.setSizes([600, 800])
        layout.addWidget(main_splitter)
        
        # 底部状态栏
        status_bar = self.create_status_bar()
        layout.addWidget(status_bar)
    
    def create_title_bar(self):
        """创建标题栏"""
        title_bar = QFrame()
        title_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        title_bar.setMaximumHeight(60)
        
        layout = QHBoxLayout(title_bar)
        
        # 标题
        title_label = QLabel("🎬 动画描述工作台")
        title_label.setFont(QFont("", 16, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # 语言选择
        layout.addWidget(QLabel("语言:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["中文", "English", "日本語", "한국어"])
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        layout.addWidget(self.language_combo)
        
        # 工作模式
        layout.addWidget(QLabel("模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["标准模式", "专家模式", "创意模式"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        layout.addWidget(self.mode_combo)
        
        # 设置按钮
        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(settings_btn)
        
        return title_bar
    
    def create_description_editor(self):
        """创建描述编辑器"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 编辑器标题
        editor_title = QGroupBox("智能描述编辑器")
        editor_layout = QVBoxLayout(editor_title)
        
        # 快速操作栏
        quick_actions = QHBoxLayout()
        
        new_desc_btn = QPushButton("📝 新建")
        new_desc_btn.clicked.connect(self.new_description)
        quick_actions.addWidget(new_desc_btn)
        
        load_template_btn = QPushButton("📋 加载模板")
        load_template_btn.clicked.connect(self.load_template)
        quick_actions.addWidget(load_template_btn)
        
        voice_input_btn = QPushButton("🎤 语音输入")
        voice_input_btn.clicked.connect(self.start_voice_input)
        quick_actions.addWidget(voice_input_btn)
        
        quick_actions.addStretch()
        
        # 实时状态指示器
        self.status_indicator = QLabel("✅ 就绪")
        self.status_indicator.setStyleSheet("color: green; font-weight: bold;")
        quick_actions.addWidget(self.status_indicator)
        
        editor_layout.addLayout(quick_actions)
        
        # 主编辑区
        self.main_description_edit = QTextEdit()
        self.main_description_edit.setPlaceholderText(
            "🎯 在这里输入您的动画描述...\n\n"
            "💡 智能提示：\n"
            "• 描述具体的动画动作和效果\n"
            "• 指定元素的起始和结束状态\n"
            "• 添加时间、速度、风格等细节\n"
            "• 使用自然语言，系统会智能理解\n\n"
            "🌟 示例：\n"
            "一个蓝色的圆形按钮从屏幕左侧优雅地滑入，"
            "在中央停留0.5秒后轻微弹跳，"
            "最后带着发光效果淡出消失。"
        )
        self.main_description_edit.setMinimumHeight(200)
        
        # 设置智能补全
        self.main_description_edit.setCompleter(self.description_completer)
        
        editor_layout.addWidget(self.main_description_edit)
        
        # 实时反馈区
        feedback_layout = QHBoxLayout()
        
        # 字数统计
        self.word_count_label = QLabel("字数: 0")
        feedback_layout.addWidget(self.word_count_label)
        
        # 质量指示器
        self.quality_indicator = QProgressBar()
        self.quality_indicator.setRange(0, 100)
        self.quality_indicator.setValue(0)
        self.quality_indicator.setFormat("质量: %v%")
        self.quality_indicator.setMaximumWidth(150)
        feedback_layout.addWidget(self.quality_indicator)
        
        # 语言检测
        self.language_indicator = QLabel("语言: 中文")
        feedback_layout.addWidget(self.language_indicator)
        
        feedback_layout.addStretch()
        
        editor_layout.addLayout(feedback_layout)
        
        layout.addWidget(editor_title)
        
        # 快速增强工具
        enhancement_group = QGroupBox("快速增强工具")
        enhancement_layout = QVBoxLayout(enhancement_group)
        
        # 增强按钮
        enhancement_buttons = QHBoxLayout()
        
        auto_enhance_btn = QPushButton("✨ 自动增强")
        auto_enhance_btn.clicked.connect(self.auto_enhance_description)
        enhancement_buttons.addWidget(auto_enhance_btn)
        
        add_details_btn = QPushButton("📝 添加细节")
        add_details_btn.clicked.connect(self.add_description_details)
        enhancement_buttons.addWidget(add_details_btn)
        
        fix_issues_btn = QPushButton("🔧 修复问题")
        fix_issues_btn.clicked.connect(self.fix_description_issues)
        enhancement_buttons.addWidget(fix_issues_btn)
        
        enhancement_layout.addLayout(enhancement_buttons)
        
        # 增强选项
        enhancement_options = QHBoxLayout()
        
        self.auto_enhance_cb = QCheckBox("自动增强")
        self.auto_enhance_cb.setChecked(True)
        enhancement_options.addWidget(self.auto_enhance_cb)
        
        self.real_time_validation_cb = QCheckBox("实时验证")
        self.real_time_validation_cb.setChecked(True)
        enhancement_options.addWidget(self.real_time_validation_cb)
        
        self.smart_suggestions_cb = QCheckBox("智能建议")
        self.smart_suggestions_cb.setChecked(True)
        enhancement_options.addWidget(self.smart_suggestions_cb)
        
        enhancement_options.addStretch()
        
        enhancement_layout.addLayout(enhancement_options)
        
        layout.addWidget(enhancement_group)
        
        # 快速历史访问
        quick_history_group = QGroupBox("快速历史")
        quick_history_layout = QVBoxLayout(quick_history_group)
        
        self.quick_history_list = QListWidget()
        self.quick_history_list.setMaximumHeight(120)
        self.quick_history_list.itemDoubleClicked.connect(self.load_quick_history)
        quick_history_layout.addWidget(self.quick_history_list)
        
        layout.addWidget(quick_history_group)
        
        return panel
    
    def create_status_bar(self):
        """创建状态栏"""
        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        status_bar.setMaximumHeight(40)
        
        layout = QHBoxLayout(status_bar)
        
        # 状态信息
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # 统计信息
        self.stats_label = QLabel("历史记录: 0 | 今日使用: 0")
        layout.addWidget(self.stats_label)
        
        # 自动保存状态
        self.auto_save_label = QLabel("✅ 自动保存")
        layout.addWidget(self.auto_save_label)
        
        return status_bar
    
    def setup_connections(self):
        """设置信号连接"""
        # 主编辑器事件
        self.main_description_edit.textChanged.connect(self.on_main_description_changed)
        
        # 描述生成器信号
        self.description_generator.description_analyzed.connect(self.on_description_analyzed)
        self.description_generator.prompt_generated.connect(self.on_prompt_generated)
        self.description_generator.template_applied.connect(self.on_template_applied)
        self.description_generator.voice_input_completed.connect(self.on_voice_input_completed)
        
        # 定时器
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self.validate_current_description)
        
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.start(30000)  # 每30秒更新统计
    
    def on_main_description_changed(self):
        """主描述改变事件"""
        try:
            description = self.main_description_edit.toPlainText()
            
            # 更新字数统计
            word_count = len(description)
            self.word_count_label.setText(f"字数: {word_count}")
            
            # 同步到描述生成器
            self.description_generator.description_edit.setPlainText(description)
            
            # 检测语言
            detected_lang, confidence = self.multilingual_processor.language_detector.detect_language(description)
            lang_names = {"zh": "中文", "en": "English", "ja": "日本語", "ko": "한국어"}
            lang_name = lang_names.get(detected_lang, "未知")
            self.language_indicator.setText(f"语言: {lang_name} ({confidence:.0%})")
            
            # 实时验证
            if self.real_time_validation_cb.isChecked() and description.strip():
                self.validation_timer.stop()
                self.validation_timer.start(2000)  # 2秒延迟验证
            
            # 更新状态
            if description.strip():
                self.status_indicator.setText("✏️ 编辑中")
                self.status_indicator.setStyleSheet("color: orange; font-weight: bold;")
            else:
                self.status_indicator.setText("✅ 就绪")
                self.status_indicator.setStyleSheet("color: green; font-weight: bold;")
                
        except Exception as e:
            logger.error(f"处理主描述改变失败: {e}")
    
    def validate_current_description(self):
        """验证当前描述"""
        try:
            description = self.main_description_edit.toPlainText().strip()
            if not description:
                self.quality_indicator.setValue(0)
                return
            
            # 验证描述质量
            validation_result = self.description_validator.validate_description(description)
            quality_score = validation_result.get("score", 0)
            
            # 更新质量指示器
            self.quality_indicator.setValue(quality_score)
            
            # 更新状态
            if quality_score >= 80:
                self.status_indicator.setText("✅ 优秀")
                self.status_indicator.setStyleSheet("color: green; font-weight: bold;")
            elif quality_score >= 60:
                self.status_indicator.setText("⚠️ 良好")
                self.status_indicator.setStyleSheet("color: orange; font-weight: bold;")
            else:
                self.status_indicator.setText("❌ 需改进")
                self.status_indicator.setStyleSheet("color: red; font-weight: bold;")
                
        except Exception as e:
            logger.error(f"验证描述失败: {e}")
    
    def on_description_analyzed(self, analysis: dict):
        """描述分析完成事件"""
        try:
            # 发送描述准备就绪信号
            description = self.main_description_edit.toPlainText()
            self.description_ready.emit(description, analysis)
            
            logger.info("描述分析完成，已发送准备就绪信号")
            
        except Exception as e:
            logger.error(f"处理描述分析完成事件失败: {e}")
    
    def on_prompt_generated(self, prompt: str):
        """Prompt生成完成事件"""
        try:
            # 发送Prompt准备就绪信号
            self.prompt_ready.emit(prompt)
            
            # 保存到历史记录
            description = self.main_description_edit.toPlainText()
            if description:
                self.history_manager.add_entry(
                    description=description,
                    entry_type=HistoryEntryType.AI_GENERATED,
                    language=self.current_language,
                    prompt_generated=prompt
                )
            
            logger.info("Prompt生成完成，已发送准备就绪信号")
            
        except Exception as e:
            logger.error(f"处理Prompt生成完成事件失败: {e}")
    
    def on_template_applied(self, template: dict):
        """模板应用完成事件"""
        try:
            # 同步描述到主编辑器
            description = self.description_generator.description_edit.toPlainText()
            self.main_description_edit.setPlainText(description)
            
            logger.info(f"模板应用完成: {template.get('name', '未知模板')}")
            
        except Exception as e:
            logger.error(f"处理模板应用事件失败: {e}")
    
    def on_voice_input_completed(self, text: str):
        """语音输入完成事件"""
        try:
            # 同步到主编辑器
            self.main_description_edit.setPlainText(text)
            
            logger.info("语音输入完成")
            
        except Exception as e:
            logger.error(f"处理语音输入完成事件失败: {e}")
    
    def on_language_changed(self, language: str):
        """语言改变事件"""
        try:
            lang_map = {"中文": "zh", "English": "en", "日本語": "ja", "한국어": "ko"}
            self.current_language = lang_map.get(language, "zh")
            
            # 更新多语言处理器
            self.multilingual_processor.set_current_language(self.current_language)
            
            logger.info(f"语言已切换到: {language}")
            
        except Exception as e:
            logger.error(f"处理语言改变失败: {e}")
    
    def on_mode_changed(self, mode: str):
        """模式改变事件"""
        try:
            # 根据模式调整界面和功能
            if mode == "专家模式":
                # 显示更多高级功能
                self.description_generator.setVisible(True)
            elif mode == "创意模式":
                # 启用创意增强功能
                self.auto_enhance_cb.setChecked(True)
            else:  # 标准模式
                # 使用默认设置
                pass
            
            logger.info(f"工作模式已切换到: {mode}")
            
        except Exception as e:
            logger.error(f"处理模式改变失败: {e}")
    
    def new_description(self):
        """新建描述"""
        try:
            if self.main_description_edit.toPlainText().strip():
                reply = QMessageBox.question(
                    self, "新建描述",
                    "当前有未保存的描述，确定要新建吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # 清空编辑器
            self.main_description_edit.clear()
            self.description_generator.description_edit.clear()
            self.description_generator.prompt_edit.clear()
            
            # 重置状态
            self.quality_indicator.setValue(0)
            self.status_indicator.setText("✅ 就绪")
            self.status_indicator.setStyleSheet("color: green; font-weight: bold;")
            
            logger.info("已新建描述")
            
        except Exception as e:
            logger.error(f"新建描述失败: {e}")
    
    def load_template(self):
        """加载模板"""
        try:
            # 切换到模板标签页
            if hasattr(self.description_generator, 'template_tabs'):
                # 显示模板选择对话框或切换标签页
                pass
            
        except Exception as e:
            logger.error(f"加载模板失败: {e}")
    
    def start_voice_input(self):
        """开始语音输入"""
        try:
            # 切换到语音输入模式
            self.description_generator.voice_input_rb.setChecked(True)
            self.description_generator.voice_record_btn.click()
            
        except Exception as e:
            logger.error(f"开始语音输入失败: {e}")
    
    def auto_enhance_description(self):
        """自动增强描述"""
        try:
            description = self.main_description_edit.toPlainText().strip()
            if not description:
                QMessageBox.warning(self, "警告", "请先输入描述")
                return
            
            # 增强描述
            enhanced_description = self.description_enhancer.enhance_description(
                description, "moderate"
            )
            
            if enhanced_description != description:
                # 询问是否应用增强
                reply = QMessageBox.question(
                    self, "自动增强",
                    f"原描述:\n{description}\n\n"
                    f"增强后:\n{enhanced_description}\n\n"
                    f"是否应用增强结果？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.main_description_edit.setPlainText(enhanced_description)
                    
                    # 保存到历史
                    self.history_manager.add_entry(
                        description=enhanced_description,
                        entry_type=HistoryEntryType.OPTIMIZED,
                        language=self.current_language
                    )
            else:
                QMessageBox.information(self, "提示", "当前描述已经很好，无需增强")
                
        except Exception as e:
            logger.error(f"自动增强描述失败: {e}")
    
    def add_description_details(self):
        """添加描述细节"""
        try:
            description = self.main_description_edit.toPlainText().strip()
            if not description:
                QMessageBox.warning(self, "警告", "请先输入基础描述")
                return
            
            # 分析当前描述
            analysis = self.description_generator.semantic_analyzer.analyze_description(description)
            
            # 根据分析结果添加细节
            details_to_add = []
            
            if not analysis.get("duration_hints"):
                details_to_add.append("，持续时间约2秒")
            
            if not analysis.get("emotions"):
                details_to_add.append("，具有现代科技感")
            
            if analysis.get("complexity_score", 0) < 30:
                details_to_add.append("，带有平滑的缓动效果")
            
            if details_to_add:
                enhanced_description = description + "".join(details_to_add)
                self.main_description_edit.setPlainText(enhanced_description)
                
                QMessageBox.information(self, "成功", "已添加描述细节")
            else:
                QMessageBox.information(self, "提示", "当前描述已经很详细")
                
        except Exception as e:
            logger.error(f"添加描述细节失败: {e}")
    
    def fix_description_issues(self):
        """修复描述问题"""
        try:
            description = self.main_description_edit.toPlainText().strip()
            if not description:
                QMessageBox.warning(self, "警告", "请先输入描述")
                return
            
            # 验证描述
            validation_result = self.description_validator.validate_description(description)
            
            if validation_result.get("issues"):
                # 显示问题和修复建议
                issues_text = "发现的问题:\n"
                for issue in validation_result["issues"]:
                    issues_text += f"• {issue}\n"
                
                suggestions_text = "\n修复建议:\n"
                for suggestion in validation_result.get("suggestions", []):
                    suggestions_text += f"• {suggestion}\n"
                
                QMessageBox.information(self, "描述问题分析", issues_text + suggestions_text)
            else:
                QMessageBox.information(self, "检查结果", "未发现明显问题，描述质量良好！")
                
        except Exception as e:
            logger.error(f"修复描述问题失败: {e}")
    
    def load_quick_history(self, item):
        """加载快速历史"""
        try:
            entry = item.data(Qt.ItemDataRole.UserRole)
            if entry:
                self.main_description_edit.setPlainText(entry.description)
                
        except Exception as e:
            logger.error(f"加载快速历史失败: {e}")
    
    def update_quick_history(self):
        """更新快速历史显示"""
        try:
            self.quick_history_list.clear()
            
            # 获取最近的5条记录
            recent_entries = self.history_manager.get_recent_entries(5)
            
            for entry in recent_entries:
                item_text = entry.description[:30] + "..." if len(entry.description) > 30 else entry.description
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, entry)
                item.setToolTip(entry.description)
                
                self.quick_history_list.addItem(item)
                
        except Exception as e:
            logger.error(f"更新快速历史失败: {e}")
    
    def update_statistics(self):
        """更新统计信息"""
        try:
            stats = self.history_manager.get_statistics()
            
            total_entries = stats.get("total_entries", 0)
            recent_count = stats.get("recent_entries_count", 0)
            
            self.stats_label.setText(f"历史记录: {total_entries} | 今日使用: {recent_count}")
            
            # 更新快速历史
            self.update_quick_history()
            
        except Exception as e:
            logger.error(f"更新统计信息失败: {e}")
    
    def show_settings(self):
        """显示设置对话框"""
        QMessageBox.information(self, "设置", "设置功能将在后续版本中实现")
    
    def get_current_description_data(self) -> dict:
        """获取当前描述数据"""
        return {
            "description": self.main_description_edit.toPlainText(),
            "language": self.current_language,
            "mode": self.mode_combo.currentText(),
            "analysis": getattr(self.description_generator, 'current_analysis', None),
            "prompt": self.description_generator.prompt_edit.toPlainText()
        }
    
    def load_description_data(self, data: dict):
        """加载描述数据"""
        try:
            if "description" in data:
                self.main_description_edit.setPlainText(data["description"])
            
            if "language" in data:
                lang_names = {"zh": "中文", "en": "English", "ja": "日本語", "ko": "한국어"}
                lang_name = lang_names.get(data["language"], "中文")
                self.language_combo.setCurrentText(lang_name)
            
            if "mode" in data:
                self.mode_combo.setCurrentText(data["mode"])
            
            if "prompt" in data:
                self.description_generator.prompt_edit.setPlainText(data["prompt"])
                
        except Exception as e:
            logger.error(f"加载描述数据失败: {e}")
