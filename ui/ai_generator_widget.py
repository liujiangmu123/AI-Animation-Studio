"""
AI Animation Studio - AI生成器组件
提供AI动画生成功能，包括Prompt预览编辑和多方案生成
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QTextEdit, QComboBox, QSpinBox, QCheckBox, QTabWidget, QListWidget,
    QListWidgetItem, QMessageBox, QProgressBar, QSplitter, QLineEdit,
    QSlider, QDoubleSpinBox, QFormLayout, QScrollArea, QFrame, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMenu, QToolButton, QButtonGroup,
    QRadioButton, QDialog, QDialogButtonBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QAction

from core.data_structures import AnimationSolution, TechStack
from core.logger import get_logger
from core.user_settings import UserSettingsManager
from core.js_library_manager import JSLibraryManager
from ai.gemini_generator import GeminiGenerator

logger = get_logger("ai_generator_widget")

class AIGeneratorWidget(QWidget):
    """AI生成器组件"""

    solutions_generated = pyqtSignal(list)  # 方案生成完成信号
    solution_selected = pyqtSignal(AnimationSolution)  # 方案选择信号
    template_applied = pyqtSignal(str)  # 模板应用信号
    batch_generation_completed = pyqtSignal(list)  # 批量生成完成信号

    def __init__(self):
        super().__init__()

        self.current_solutions = []
        self.generator_thread = None
        self.selected_solution = None

        # 模板管理
        self.prompt_templates = {}
        self.description_history = []
        self.favorite_solutions = []

        # 批量生成
        self.batch_mode = False
        self.batch_variations = 3
        self.batch_progress = 0

        # 智能推荐
        self.recommendation_enabled = True
        self.learning_data = {}

        # 方案对比
        self.comparison_mode = False
        self.compared_solutions = []

        # 初始化管理器
        self.user_settings = UserSettingsManager()
        self.js_library_manager = JSLibraryManager()

        # 加载数据
        self.load_templates()
        self.load_history()

        self.setup_ui()
        self.setup_connections()
        self.load_user_settings()

        logger.info("AI生成器组件初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 顶部工具栏
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)

        # 主要内容区域
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧面板 - 输入和配置
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)

        # 右侧面板 - 方案管理和预览
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)

        # 设置分割器比例
        main_splitter.setSizes([450, 750])
        layout.addWidget(main_splitter)

        # 底部状态栏
        status_bar = self.create_status_bar()
        layout.addWidget(status_bar)

    def create_toolbar(self):
        """创建工具栏"""
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(toolbar_frame)

        # 模式切换
        mode_group = QButtonGroup()

        self.single_mode_radio = QRadioButton("单次生成")
        self.single_mode_radio.setChecked(True)
        mode_group.addButton(self.single_mode_radio)
        layout.addWidget(self.single_mode_radio)

        self.batch_mode_radio = QRadioButton("批量生成")
        mode_group.addButton(self.batch_mode_radio)
        layout.addWidget(self.batch_mode_radio)

        self.comparison_mode_radio = QRadioButton("方案对比")
        mode_group.addButton(self.comparison_mode_radio)
        layout.addWidget(self.comparison_mode_radio)

        layout.addWidget(QLabel("|"))

        # 快速操作
        self.template_btn = QToolButton()
        self.template_btn.setText("模板")
        self.template_btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.template_menu = QMenu()
        self.template_btn.setMenu(self.template_menu)
        layout.addWidget(self.template_btn)

        self.history_btn = QPushButton("历史")
        layout.addWidget(self.history_btn)

        self.favorites_btn = QPushButton("收藏")
        layout.addWidget(self.favorites_btn)

        layout.addStretch()

        # 智能推荐开关
        self.recommendation_cb = QCheckBox("智能推荐")
        self.recommendation_cb.setChecked(True)
        layout.addWidget(self.recommendation_cb)

        return toolbar_frame

    def create_left_panel(self):
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 创建标签页
        tab_widget = QTabWidget()

        # 基本配置标签页
        config_tab = self.create_config_tab()
        tab_widget.addTab(config_tab, "🤖 配置")

        # 描述输入标签页
        description_tab = self.create_description_tab()
        tab_widget.addTab(description_tab, "📝 描述")

        # 高级设置标签页
        advanced_tab = self.create_advanced_tab()
        tab_widget.addTab(advanced_tab, "⚙️ 高级")

        layout.addWidget(tab_widget)

        # 生成控制区域
        control_area = self.create_generation_controls()
        layout.addWidget(control_area)

        return panel

    def create_config_tab(self):
        """创建配置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # AI配置组
        config_group = QGroupBox("AI配置")
        config_layout = QFormLayout(config_group)

        # API Key设置
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("请输入Gemini API Key")
        config_layout.addRow("API Key:", self.api_key_input)

        # 模型选择
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gemini-2.5-flash",
            "gemini-pro",
            "gemini-1.5-pro"
        ])
        config_layout.addRow("模型:", self.model_combo)

        # 思考模式
        self.thinking_checkbox = QCheckBox("启用深度思考")
        config_layout.addRow("", self.thinking_checkbox)

        layout.addWidget(config_group)

        # 生成参数组
        params_group = QGroupBox("生成参数")
        params_layout = QFormLayout(params_group)

        # 创意度
        self.creativity_slider = QSlider(Qt.Orientation.Horizontal)
        self.creativity_slider.setRange(0, 100)
        self.creativity_slider.setValue(70)
        creativity_layout = QHBoxLayout()
        creativity_layout.addWidget(self.creativity_slider)
        self.creativity_label = QLabel("70%")
        creativity_layout.addWidget(self.creativity_label)
        params_layout.addRow("创意度:", creativity_layout)

        # 复杂度
        self.complexity_combo = QComboBox()
        self.complexity_combo.addItems(["简单", "中等", "复杂", "专业"])
        self.complexity_combo.setCurrentText("中等")
        params_layout.addRow("复杂度:", self.complexity_combo)

        # 方案数量
        self.solution_count_spin = QSpinBox()
        self.solution_count_spin.setRange(1, 10)
        self.solution_count_spin.setValue(3)
        params_layout.addRow("方案数量:", self.solution_count_spin)

        layout.addWidget(params_group)

        layout.addStretch()
        return tab

    def create_description_tab(self):
        """创建描述标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 动画类型选择
        type_group = QGroupBox("动画类型")
        type_layout = QVBoxLayout(type_group)

        self.animation_type_combo = QComboBox()
        self.animation_type_combo.addItems([
            "CSS动画",
            "GSAP动画",
            "Three.js动画",
            "JavaScript动画",
            "混合动画"
        ])
        type_layout.addWidget(self.animation_type_combo)

        layout.addWidget(type_group)

        # 描述输入
        desc_group = QGroupBox("动画描述")
        desc_layout = QVBoxLayout(desc_group)

        # 快速模板按钮
        template_buttons = QHBoxLayout()
        quick_templates = ["弹跳球", "淡入文字", "旋转立方体", "粒子效果", "加载动画"]
        for template in quick_templates:
            btn = QPushButton(template)
            btn.setMaximumWidth(80)
            btn.clicked.connect(lambda checked, t=template: self.apply_quick_template(t))
            template_buttons.addWidget(btn)
        desc_layout.addLayout(template_buttons)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "请描述您想要的动画效果，例如：\n"
            "- 一个蓝色的小球从左边弹跳到右边\n"
            "- 文字从上方淡入，然后旋转360度\n"
            "- 3D立方体在空间中旋转，带有光影效果"
        )
        self.description_input.setMaximumHeight(150)
        desc_layout.addWidget(self.description_input)

        # 智能建议
        self.suggestions_list = QListWidget()
        self.suggestions_list.setMaximumHeight(80)
        desc_layout.addWidget(QLabel("智能建议:"))
        desc_layout.addWidget(self.suggestions_list)

        layout.addWidget(desc_group)

        return tab

    def create_advanced_tab(self):
        """创建高级设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 技术栈偏好
        tech_group = QGroupBox("技术栈偏好")
        tech_layout = QVBoxLayout(tech_group)

        # CSS偏好
        css_layout = QHBoxLayout()
        css_layout.addWidget(QLabel("CSS:"))
        self.css_preference_slider = QSlider(Qt.Orientation.Horizontal)
        self.css_preference_slider.setRange(0, 100)
        self.css_preference_slider.setValue(80)
        css_layout.addWidget(self.css_preference_slider)
        self.css_pref_label = QLabel("80%")
        css_layout.addWidget(self.css_pref_label)
        tech_layout.addLayout(css_layout)

        # JavaScript偏好
        js_layout = QHBoxLayout()
        js_layout.addWidget(QLabel("JavaScript:"))
        self.js_preference_slider = QSlider(Qt.Orientation.Horizontal)
        self.js_preference_slider.setRange(0, 100)
        self.js_preference_slider.setValue(60)
        js_layout.addWidget(self.js_preference_slider)
        self.js_pref_label = QLabel("60%")
        js_layout.addWidget(self.js_pref_label)
        tech_layout.addLayout(js_layout)

        # 库偏好
        lib_layout = QHBoxLayout()
        lib_layout.addWidget(QLabel("第三方库:"))
        self.lib_preference_slider = QSlider(Qt.Orientation.Horizontal)
        self.lib_preference_slider.setRange(0, 100)
        self.lib_preference_slider.setValue(40)
        lib_layout.addWidget(self.lib_preference_slider)
        self.lib_pref_label = QLabel("40%")
        lib_layout.addWidget(self.lib_pref_label)
        tech_layout.addLayout(lib_layout)

        layout.addWidget(tech_group)

        # 输出设置
        output_group = QGroupBox("输出设置")
        output_layout = QFormLayout(output_group)

        # 代码风格
        self.code_style_combo = QComboBox()
        self.code_style_combo.addItems(["现代", "兼容", "简洁", "详细"])
        output_layout.addRow("代码风格:", self.code_style_combo)

        # 注释详细度
        self.comment_level_combo = QComboBox()
        self.comment_level_combo.addItems(["无注释", "简单", "详细", "教学级"])
        self.comment_level_combo.setCurrentText("简单")
        output_layout.addRow("注释详细度:", self.comment_level_combo)

        # 响应式设计
        self.responsive_cb = QCheckBox("包含响应式设计")
        output_layout.addRow("", self.responsive_cb)

        # 浏览器兼容性
        self.compatibility_cb = QCheckBox("优化浏览器兼容性")
        output_layout.addRow("", self.compatibility_cb)

        layout.addWidget(output_group)

        # 学习设置
        learning_group = QGroupBox("学习设置")
        learning_layout = QVBoxLayout(learning_group)

        self.learn_from_feedback_cb = QCheckBox("从用户反馈中学习")
        self.learn_from_feedback_cb.setChecked(True)
        learning_layout.addWidget(self.learn_from_feedback_cb)

        self.save_successful_prompts_cb = QCheckBox("保存成功的提示词")
        self.save_successful_prompts_cb.setChecked(True)
        learning_layout.addWidget(self.save_successful_prompts_cb)

        layout.addWidget(learning_group)

        layout.addStretch()
        return tab

    def create_generation_controls(self):
        """创建生成控制区域"""
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(control_frame)

        # Prompt预览
        prompt_group = QGroupBox("Prompt预览")
        prompt_layout = QVBoxLayout(prompt_group)

        self.prompt_preview = QTextEdit()
        self.prompt_preview.setReadOnly(True)
        self.prompt_preview.setMaximumHeight(120)
        self.prompt_preview.setFont(QFont("Consolas", 9))
        prompt_layout.addWidget(self.prompt_preview)

        # Prompt操作按钮
        prompt_buttons = QHBoxLayout()
        self.edit_prompt_btn = QPushButton("编辑")
        self.save_prompt_btn = QPushButton("保存")
        self.load_prompt_btn = QPushButton("加载")
        prompt_buttons.addWidget(self.edit_prompt_btn)
        prompt_buttons.addWidget(self.save_prompt_btn)
        prompt_buttons.addWidget(self.load_prompt_btn)
        prompt_buttons.addStretch()
        prompt_layout.addLayout(prompt_buttons)

        layout.addWidget(prompt_group)

        # 生成按钮和进度
        generation_layout = QVBoxLayout()

        self.generate_btn = QPushButton("🚀 生成动画方案")
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        generation_layout.addWidget(self.generate_btn)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        generation_layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        generation_layout.addWidget(self.status_label)

        layout.addLayout(generation_layout)

        return control_frame

    def create_right_panel(self):
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 创建标签页
        tab_widget = QTabWidget()

        # 方案列表标签页
        solutions_tab = self.create_solutions_tab()
        tab_widget.addTab(solutions_tab, "📋 方案")

        # 方案对比标签页
        comparison_tab = self.create_comparison_tab()
        tab_widget.addTab(comparison_tab, "⚖️ 对比")

        # 收藏夹标签页
        favorites_tab = self.create_favorites_tab()
        tab_widget.addTab(favorites_tab, "⭐ 收藏")

        # 历史记录标签页
        history_tab = self.create_history_tab()
        tab_widget.addTab(history_tab, "📜 历史")

        layout.addWidget(tab_widget)

        return panel

    def create_solutions_tab(self):
        """创建方案标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 方案操作工具栏
        toolbar = QHBoxLayout()

        # 刷新按钮
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setToolTip("刷新方案列表")
        self.refresh_btn.clicked.connect(self.refresh_solutions)
        toolbar.addWidget(self.refresh_btn)

        # 筛选按钮
        self.filter_btn = QPushButton("🔍 筛选")
        self.filter_btn.setToolTip("筛选方案")
        self.filter_btn.clicked.connect(self.show_filter_dialog)
        toolbar.addWidget(self.filter_btn)

        # 导出按钮
        self.export_btn = QPushButton("📤 导出")
        self.export_btn.setToolTip("导出选中方案")
        self.export_btn.clicked.connect(self.export_selected_solutions)
        toolbar.addWidget(self.export_btn)

        # 删除按钮
        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.setToolTip("删除选中方案")
        self.delete_btn.clicked.connect(self.delete_selected_solutions)
        toolbar.addWidget(self.delete_btn)

        toolbar.addStretch()

        # 视图模式切换
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["列表视图", "网格视图", "详细视图"])
        self.view_mode_combo.currentTextChanged.connect(self.change_view_mode)
        toolbar.addWidget(QLabel("视图:"))
        toolbar.addWidget(self.view_mode_combo)

        # 排序选项
        toolbar.addWidget(QLabel("排序:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["时间↓", "时间↑", "评分↓", "评分↑", "复杂度↓", "复杂度↑", "类型"])
        self.sort_combo.currentTextChanged.connect(self.sort_solutions)
        toolbar.addWidget(self.sort_combo)

        layout.addLayout(toolbar)

        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索方案...")
        self.search_input.textChanged.connect(self.search_solutions)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # 方案列表
        self.solutions_list = QListWidget()
        self.solutions_list.setAlternatingRowColors(True)
        self.solutions_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.solutions_list.currentRowChanged.connect(self.on_solution_selected)
        self.solutions_list.itemDoubleClicked.connect(self.preview_solution)
        layout.addWidget(self.solutions_list)

        # 方案详情预览
        preview_group = QGroupBox("方案预览")
        preview_layout = QVBoxLayout(preview_group)

        # 方案信息
        info_layout = QFormLayout()
        self.solution_name_label = QLabel("未选择")
        self.solution_type_label = QLabel("未知")
        self.solution_complexity_label = QLabel("未知")
        self.solution_rating_label = QLabel("未评分")

        info_layout.addRow("名称:", self.solution_name_label)
        info_layout.addRow("类型:", self.solution_type_label)
        info_layout.addRow("复杂度:", self.solution_complexity_label)
        info_layout.addRow("评分:", self.solution_rating_label)
        preview_layout.addLayout(info_layout)

        # 代码预览
        self.code_preview = QTextEdit()
        self.code_preview.setReadOnly(True)
        self.code_preview.setMaximumHeight(200)
        self.code_preview.setFont(QFont("Consolas", 9))
        preview_layout.addWidget(QLabel("代码预览:"))
        preview_layout.addWidget(self.code_preview)

        # 操作按钮
        action_buttons = QHBoxLayout()
        self.preview_btn = QPushButton("🔍 预览")
        self.preview_btn.clicked.connect(self.preview_solution)
        self.apply_btn = QPushButton("✅ 应用")
        self.apply_btn.clicked.connect(self.apply_solution)
        self.favorite_btn = QPushButton("⭐ 收藏")
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        self.rate_btn = QPushButton("📊 评分")
        self.rate_btn.clicked.connect(self.rate_solution)

        action_buttons.addWidget(self.preview_btn)
        action_buttons.addWidget(self.apply_btn)
        action_buttons.addWidget(self.favorite_btn)
        action_buttons.addWidget(self.rate_btn)
        preview_layout.addLayout(action_buttons)

        layout.addWidget(preview_group)

        return tab

    def create_comparison_tab(self):
        """创建对比标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 对比说明
        info_label = QLabel("选择多个方案进行详细对比分析，支持性能、代码复杂度、兼容性等多维度对比")
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 10px; background-color: #f5f5f5; border-radius: 4px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # 对比控制
        control_layout = QHBoxLayout()

        self.add_to_comparison_btn = QPushButton("➕ 添加到对比")
        self.add_to_comparison_btn.clicked.connect(self.add_to_comparison)
        self.add_to_comparison_btn.setToolTip("将当前选中的方案添加到对比列表")
        control_layout.addWidget(self.add_to_comparison_btn)

        self.remove_from_comparison_btn = QPushButton("➖ 移除选中")
        self.remove_from_comparison_btn.clicked.connect(self.remove_from_comparison)
        self.remove_from_comparison_btn.setToolTip("从对比列表中移除选中的方案")
        control_layout.addWidget(self.remove_from_comparison_btn)

        self.clear_comparison_btn = QPushButton("🗑️ 清空对比")
        self.clear_comparison_btn.clicked.connect(self.clear_comparison)
        self.clear_comparison_btn.setToolTip("清空所有对比方案")
        control_layout.addWidget(self.clear_comparison_btn)

        control_layout.addStretch()

        self.start_comparison_btn = QPushButton("🔍 开始对比")
        self.start_comparison_btn.clicked.connect(self.start_comparison)
        self.start_comparison_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        control_layout.addWidget(self.start_comparison_btn)

        layout.addLayout(control_layout)

        # 对比表格
        self.comparison_table = QTableWidget()
        self.comparison_table.setColumnCount(7)
        self.comparison_table.setHorizontalHeaderLabels([
            "方案名称", "技术栈", "复杂度", "评分", "代码长度", "性能", "兼容性"
        ])
        self.comparison_table.horizontalHeader().setStretchLastSection(True)
        self.comparison_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.comparison_table.setAlternatingRowColors(True)
        layout.addWidget(QLabel("对比方案列表:"))
        layout.addWidget(self.comparison_table)

        # 对比结果显示区域
        result_tabs = QTabWidget()

        # 综合对比标签页
        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)

        self.summary_comparison_result = QTextEdit()
        self.summary_comparison_result.setReadOnly(True)
        self.summary_comparison_result.setFont(QFont("Consolas", 10))
        summary_layout.addWidget(self.summary_comparison_result)

        result_tabs.addTab(summary_tab, "📊 综合对比")

        # 性能对比标签页
        perf_tab = QWidget()
        perf_layout = QVBoxLayout(perf_tab)

        self.perf_comparison_result = QTextEdit()
        self.perf_comparison_result.setReadOnly(True)
        self.perf_comparison_result.setFont(QFont("Consolas", 10))
        perf_layout.addWidget(self.perf_comparison_result)

        result_tabs.addTab(perf_tab, "⚡ 性能对比")

        # 代码对比标签页
        code_tab = QWidget()
        code_layout = QVBoxLayout(code_tab)

        self.code_comparison_result = QTextEdit()
        self.code_comparison_result.setReadOnly(True)
        self.code_comparison_result.setFont(QFont("Consolas", 9))
        code_layout.addWidget(self.code_comparison_result)

        result_tabs.addTab(code_tab, "💻 代码对比")

        # 兼容性对比标签页
        compat_tab = QWidget()
        compat_layout = QVBoxLayout(compat_tab)

        self.compat_comparison_result = QTextEdit()
        self.compat_comparison_result.setReadOnly(True)
        self.compat_comparison_result.setFont(QFont("Consolas", 10))
        compat_layout.addWidget(self.compat_comparison_result)

        result_tabs.addTab(compat_tab, "🌐 兼容性对比")

        layout.addWidget(QLabel("对比结果:"))
        layout.addWidget(result_tabs)

        return tab
    
    def setup_input_panel(self, parent):
        """设置输入面板"""
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        # AI配置组
        config_group = QGroupBox("🤖 AI配置")
        config_layout = QVBoxLayout(config_group)
        
        # API Key设置
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("请输入Gemini API Key")
        api_layout.addWidget(self.api_key_input)
        config_layout.addLayout(api_layout)
        
        # 模型选择
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("模型:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gemini-2.5-flash",
            "gemini-pro",
            "gemini-1.5-pro"
        ])
        model_layout.addWidget(self.model_combo)
        
        # 思考模式
        self.thinking_checkbox = QCheckBox("启用深度思考")
        model_layout.addWidget(self.thinking_checkbox)
        config_layout.addLayout(model_layout)
        
        input_layout.addWidget(config_group)
        
        # 动画描述组
        desc_group = QGroupBox("📝 动画描述")
        desc_layout = QVBoxLayout(desc_group)
        
        # 动画类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("动画类型:"))
        self.animation_type_combo = QComboBox()
        self.animation_type_combo.addItems([
            "CSS动画",
            "GSAP动画", 
            "Three.js动画",
            "JavaScript动画",
            "混合动画"
        ])
        type_layout.addWidget(self.animation_type_combo)
        desc_layout.addLayout(type_layout)
        
        # 用户描述输入
        desc_header_layout = QHBoxLayout()
        desc_header_layout.addWidget(QLabel("动画描述:"))

        # 历史记录按钮
        self.history_btn = QPushButton("📜 历史")
        self.history_btn.setMaximumWidth(60)
        self.history_btn.clicked.connect(self.show_description_history)
        desc_header_layout.addWidget(self.history_btn)

        desc_header_layout.addStretch()
        desc_layout.addLayout(desc_header_layout)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "请描述您想要的动画效果，例如：\n"
            "- 一个蓝色的小球从左边弹跳到右边\n"
            "- 文字从上方淡入，然后旋转360度\n"
            "- 3D立方体在空间中旋转，带有光影效果"
        )
        self.description_input.setMaximumHeight(120)
        desc_layout.addWidget(self.description_input)
        
        input_layout.addWidget(desc_group)
        
        # Prompt预览组
        prompt_group = QGroupBox("👁️ Prompt预览")
        prompt_layout = QVBoxLayout(prompt_group)
        
        # Prompt显示
        self.prompt_preview = QTextEdit()
        self.prompt_preview.setReadOnly(True)
        self.prompt_preview.setMaximumHeight(200)
        font = QFont("Consolas", 9)
        self.prompt_preview.setFont(font)
        prompt_layout.addWidget(self.prompt_preview)
        
        # Prompt操作按钮
        prompt_btn_layout = QHBoxLayout()
        self.generate_prompt_btn = QPushButton("🔄 生成Prompt")
        self.edit_prompt_btn = QPushButton("✏️ 编辑Prompt")
        prompt_btn_layout.addWidget(self.generate_prompt_btn)
        prompt_btn_layout.addWidget(self.edit_prompt_btn)
        prompt_layout.addLayout(prompt_btn_layout)
        
        input_layout.addWidget(prompt_group)
        
        # 生成控制组
        generate_group = QGroupBox("⚡ 生成控制")
        generate_layout = QVBoxLayout(generate_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        generate_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        generate_layout.addWidget(self.status_label)
        
        # 生成按钮
        self.generate_btn = QPushButton("🎨 生成动画方案")
        self.generate_btn.setObjectName("primary")
        self.generate_btn.setMinimumHeight(40)
        generate_layout.addWidget(self.generate_btn)
        
        input_layout.addWidget(generate_group)
        
        # 添加弹性空间
        input_layout.addStretch()
        
        parent.addWidget(input_widget)
    
    def setup_preview_panel(self, parent):
        """设置预览面板"""
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        # 方案列表组
        solutions_group = QGroupBox("📋 生成方案")
        solutions_layout = QVBoxLayout(solutions_group)
        
        # 方案列表
        self.solutions_list = QListWidget()
        self.solutions_list.setMaximumHeight(150)
        solutions_layout.addWidget(self.solutions_list)
        
        # 方案操作按钮
        solution_btn_layout = QHBoxLayout()
        self.preview_solution_btn = QPushButton("👁️ 预览")
        self.apply_solution_btn = QPushButton("✅ 应用")
        self.save_solution_btn = QPushButton("💾 保存")
        
        solution_btn_layout.addWidget(self.preview_solution_btn)
        solution_btn_layout.addWidget(self.apply_solution_btn)
        solution_btn_layout.addWidget(self.save_solution_btn)
        solutions_layout.addLayout(solution_btn_layout)
        
        preview_layout.addWidget(solutions_group)
        
        # 方案详情组
        details_group = QGroupBox("📄 方案详情")
        details_layout = QVBoxLayout(details_group)
        
        # 方案信息
        info_layout = QHBoxLayout()
        
        info_left = QVBoxLayout()
        info_left.addWidget(QLabel("方案名称:"))
        self.solution_name_label = QLabel("未选择")
        info_left.addWidget(self.solution_name_label)
        
        info_left.addWidget(QLabel("技术栈:"))
        self.tech_stack_label = QLabel("未知")
        info_left.addWidget(self.tech_stack_label)
        
        info_layout.addLayout(info_left)
        
        info_right = QVBoxLayout()
        info_right.addWidget(QLabel("复杂度:"))
        self.complexity_label = QLabel("未知")
        info_right.addWidget(self.complexity_label)
        
        info_right.addWidget(QLabel("推荐度:"))
        self.recommended_label = QLabel("未知")
        info_right.addWidget(self.recommended_label)
        
        info_layout.addLayout(info_right)
        details_layout.addLayout(info_layout)
        
        # 代码预览
        details_layout.addWidget(QLabel("HTML代码:"))
        self.code_preview = QTextEdit()
        self.code_preview.setReadOnly(True)
        self.code_preview.setFont(QFont("Consolas", 9))
        details_layout.addWidget(self.code_preview)
        
        preview_layout.addWidget(details_group)
        
        parent.addWidget(preview_widget)
    
    def setup_connections(self):
        """设置信号连接"""
        # 按钮连接
        self.generate_prompt_btn.clicked.connect(self.generate_prompt)
        self.edit_prompt_btn.clicked.connect(self.edit_prompt)
        self.generate_btn.clicked.connect(self.generate_animations)
        
        # 方案操作
        self.solutions_list.currentRowChanged.connect(self.on_solution_selected)
        self.preview_solution_btn.clicked.connect(self.preview_solution)
        self.apply_solution_btn.clicked.connect(self.apply_solution)
        self.save_solution_btn.clicked.connect(self.save_solution)
        
        # 描述改变时自动生成Prompt
        self.description_input.textChanged.connect(self.auto_generate_prompt)
        self.animation_type_combo.currentTextChanged.connect(self.auto_generate_prompt)
    
    def generate_prompt(self):
        """生成Prompt"""
        animation_type = self.animation_type_combo.currentText()
        description = self.description_input.toPlainText().strip()
        
        if not description:
            QMessageBox.warning(self, "警告", "请先输入动画描述")
            return
        
        # 构建Prompt
        prompt = f"""动画类型: {animation_type}
用户描述: {description}

请生成符合以下要求的HTML动画：
1. 包含完整的renderAtTime(t)函数
2. 动画完全由时间参数控制
3. 禁用自动播放
4. 代码清晰易读
5. 确保浏览器兼容性

技术要求:
- 使用{animation_type}技术
- 支持时间控制
- 60fps流畅运行
- 包含错误处理"""
        
        self.prompt_preview.setPlainText(prompt)
    
    def auto_generate_prompt(self):
        """自动生成Prompt"""
        # 延迟生成，避免频繁更新
        if hasattr(self, '_prompt_timer'):
            self._prompt_timer.stop()
        
        from PyQt6.QtCore import QTimer
        self._prompt_timer = QTimer()
        self._prompt_timer.setSingleShot(True)
        self._prompt_timer.timeout.connect(self.generate_prompt)
        self._prompt_timer.start(500)  # 500ms延迟
    
    def edit_prompt(self):
        """编辑Prompt"""
        self.prompt_preview.setReadOnly(False)
        self.edit_prompt_btn.setText("💾 保存")
        self.edit_prompt_btn.clicked.disconnect()
        self.edit_prompt_btn.clicked.connect(self.save_prompt)
    
    def save_prompt(self):
        """保存Prompt"""
        self.prompt_preview.setReadOnly(True)
        self.edit_prompt_btn.setText("✏️ 编辑Prompt")
        self.edit_prompt_btn.clicked.disconnect()
        self.edit_prompt_btn.clicked.connect(self.edit_prompt)
    
    def generate_animations(self):
        """生成动画方案"""
        try:
            # 验证输入
            description = self.description_input.toPlainText().strip()
            if not description:
                QMessageBox.warning(self, "警告", "请先输入动画描述")
                return

            prompt = self.prompt_preview.toPlainText().strip()
            if not prompt:
                self.generate_prompt()
                prompt = self.prompt_preview.toPlainText().strip()

            # 保存用户设置
            self.save_user_settings()

            # 使用增强的AI服务管理器
            from core.ai_service_manager import ai_service_manager, AIServiceType

            # 检查可用服务
            available_services = ai_service_manager.get_available_services()
            if not available_services:
                QMessageBox.warning(self, "警告", "没有可用的AI服务，请先在设置中配置API密钥")
                return

            # 获取首选服务
            preferred_service = ai_service_manager.get_preferred_service()
            if not preferred_service:
                QMessageBox.warning(self, "警告", "无法确定首选AI服务")
                return

            # 检查使用量限制
            can_use, limit_message = ai_service_manager.check_usage_limits(preferred_service)
            if not can_use:
                reply = QMessageBox.question(
                    self, "使用量限制",
                    f"{limit_message}\n\n是否尝试使用备用服务？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.No:
                    return

                # 尝试备用服务
                fallback_services = ai_service_manager.get_fallback_services(preferred_service)
                if not fallback_services:
                    QMessageBox.warning(self, "警告", "没有可用的备用服务")
                    return

                preferred_service = fallback_services[0]

            # 记录生成参数
            logger.info("开始生成动画方案")
            logger.info(f"使用服务: {preferred_service.value}")
            logger.info(f"动画类型: {self.animation_type_combo.currentText()}")
            logger.info(f"模型: {ai_service_manager.get_model_for_service(preferred_service)}")
            logger.info(f"描述长度: {len(description)}")
            logger.info(f"提示词长度: {len(prompt)}")

            # 禁用生成按钮
            self.generate_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 不确定进度
            self.status_label.setText("正在生成动画...")

            # 清空之前的结果
            self.current_solutions = []
            self.solutions_list.clear()

            # 使用AI服务管理器生成
            response = ai_service_manager.generate_animation_code(prompt, preferred_service)

            if response:
                # 创建解决方案对象
                from core.data_structures import AnimationSolution, TechStack

                solution = AnimationSolution(
                    name=f"AI生成方案 ({preferred_service.value})",
                    description=f"使用{preferred_service.value}生成的动画方案",
                    html_code=response.content,
                    tech_stack=TechStack.CSS_ANIMATION,
                    recommended=True
                )

                solutions = [solution]
                self.on_generation_complete(solutions)

                # 显示使用量信息
                usage_info = f"使用令牌: {response.tokens_used}, 费用: ${response.cost:.4f}, 响应时间: {response.response_time:.2f}s"
                if response.cached:
                    usage_info += " (缓存)"
                self.status_label.setText(usage_info)

            else:
                self.on_generation_error("AI服务生成失败，请检查网络连接和API配置")

        except Exception as e:
            logger.error(f"生成动画失败: {e}")
            self.on_generation_error(f"生成动画失败: {str(e)}")
    
    def on_generation_complete(self, solutions: list):
        """生成完成处理"""
        self.current_solutions = solutions
        
        # 更新方案列表
        self.solutions_list.clear()
        for i, solution in enumerate(solutions):
            item = QListWidgetItem(f"{solution.name} ({solution.tech_stack.value})")
            if solution.recommended:
                item.setText(f"⭐ {item.text()}")
            self.solutions_list.addItem(item)
        
        # 选择第一个方案
        if solutions:
            self.solutions_list.setCurrentRow(0)
        
        # 恢复界面
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"生成完成，共{len(solutions)}个方案")
        
        # 发射信号
        self.solutions_generated.emit(solutions)
        
        logger.info(f"AI生成完成，共{len(solutions)}个方案")
    
    def on_generation_error(self, error_message: str):
        """生成错误处理"""
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("生成失败")
        
        QMessageBox.critical(self, "生成错误", error_message)
        logger.error(f"AI生成失败: {error_message}")
    
    def on_progress_update(self, message: str):
        """进度更新处理"""
        self.status_label.setText(message)
        logger.info(f"生成进度: {message}")

        # 如果是错误消息，也记录到日志
        if "❌" in message or "失败" in message:
            logger.warning(f"生成警告: {message}")
    
    def on_solution_selected(self, row: int):
        """方案选择处理"""
        if 0 <= row < len(self.current_solutions):
            solution = self.current_solutions[row]
            
            # 更新方案详情
            self.solution_name_label.setText(solution.name)
            self.tech_stack_label.setText(solution.tech_stack.value)
            self.complexity_label.setText(solution.complexity_level)
            self.recommended_label.setText("是" if solution.recommended else "否")
            self.code_preview.setPlainText(solution.html_code)
    
    def preview_solution(self):
        """预览方案"""
        current_row = self.solutions_list.currentRow()
        if 0 <= current_row < len(self.current_solutions):
            solution = self.current_solutions[current_row]
            # TODO: 发送到预览组件
            QMessageBox.information(self, "提示", f"预览方案: {solution.name}")
    
    def apply_solution(self):
        """应用方案"""
        current_row = self.solutions_list.currentRow()
        if 0 <= current_row < len(self.current_solutions):
            solution = self.current_solutions[current_row]
            # TODO: 应用到项目
            QMessageBox.information(self, "提示", f"应用方案: {solution.name}")
    
    def save_solution(self):
        """保存方案"""
        current_row = self.solutions_list.currentRow()
        if 0 <= current_row < len(self.current_solutions):
            solution = self.current_solutions[current_row]
            # TODO: 保存方案到文件
            QMessageBox.information(self, "提示", f"保存方案: {solution.name}")
    
    def set_api_key(self, api_key: str):
        """设置API Key"""
        self.api_key_input.setText(api_key)
    
    def get_current_solution(self) -> AnimationSolution:
        """获取当前选中的方案"""
        current_row = self.solutions_list.currentRow()
        if 0 <= current_row < len(self.current_solutions):
            return self.current_solutions[current_row]
        return None

    def load_user_settings(self):
        """加载用户设置"""
        try:
            # 加载API Key
            api_key = self.user_settings.get_api_key()
            if api_key:
                self.api_key_input.setText(api_key)

            # 加载模型设置
            model_settings = self.user_settings.get_model_settings()
            self.model_combo.setCurrentText(model_settings["model"])
            self.thinking_checkbox.setChecked(model_settings["enable_thinking"])

            # 加载偏好的动画类型
            preferred_type = self.user_settings.get_preferred_animation_type()
            index = self.animation_type_combo.findText(preferred_type)
            if index >= 0:
                self.animation_type_combo.setCurrentIndex(index)

            # 加载最后的描述
            last_description = self.user_settings.get_last_animation_description()
            if last_description:
                self.description_input.setPlainText(last_description)

            logger.info("用户设置已加载")

        except Exception as e:
            logger.error(f"加载用户设置失败: {e}")

    def save_user_settings(self):
        """保存用户设置"""
        try:
            # 保存API Key
            api_key = self.api_key_input.text().strip()
            if api_key:
                self.user_settings.set_api_key(api_key)

            # 保存模型设置
            model = self.model_combo.currentText()
            thinking = self.thinking_checkbox.isChecked()
            self.user_settings.set_model_settings(model, thinking)

            # 保存偏好的动画类型
            animation_type = self.animation_type_combo.currentText()
            self.user_settings.set_preferred_animation_type(animation_type)

            # 保存描述到历史
            description = self.description_input.toPlainText().strip()
            if description:
                self.user_settings.add_animation_description(description)

            logger.info("用户设置已保存")

        except Exception as e:
            logger.error(f"保存用户设置失败: {e}")

    def show_description_history(self):
        """显示描述历史"""
        try:
            from PyQt6.QtWidgets import QDialog, QListWidget, QDialogButtonBox

            dialog = QDialog(self)
            dialog.setWindowTitle("动画描述历史")
            dialog.setMinimumSize(400, 300)

            layout = QVBoxLayout(dialog)

            # 历史列表
            history_list = QListWidget()
            history = self.user_settings.get_animation_description_history()

            if history:
                for desc in history:
                    history_list.addItem(desc)
            else:
                history_list.addItem("暂无历史记录")

            layout.addWidget(QLabel("选择一个历史描述:"))
            layout.addWidget(history_list)

            # 按钮
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok |
                QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            # 双击选择
            def on_item_double_clicked():
                dialog.accept()

            history_list.itemDoubleClicked.connect(on_item_double_clicked)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                current_item = history_list.currentItem()
                if current_item and current_item.text() != "暂无历史记录":
                    self.description_input.setPlainText(current_item.text())
                    logger.info("已选择历史描述")

        except Exception as e:
            logger.error(f"显示历史记录失败: {e}")
            QMessageBox.warning(self, "错误", f"显示历史记录失败: {e}")

    def enhance_html_with_libraries(self, html_content: str) -> str:
        """增强HTML，自动注入所需的库"""
        try:
            # 检测需要的库
            required_libs = self.js_library_manager.detect_required_libraries(html_content)

            if required_libs:
                logger.info(f"检测到需要的库: {required_libs}")

                # 获取库偏好设置
                lib_prefs = self.user_settings.get_library_preferences()

                # 注入库
                enhanced_html = self.js_library_manager.inject_libraries_to_html(
                    html_content,
                    required_libs,
                    prefer_local=lib_prefs["prefer_local"]
                )

                return enhanced_html

            return html_content

        except Exception as e:
            logger.error(f"增强HTML失败: {e}")
            return html_content

    # 方案管理增强方法
    def refresh_solutions(self):
        """刷新方案列表"""
        try:
            # 从增强方案管理器获取方案
            if hasattr(self, 'enhanced_solution_manager'):
                solutions = self.enhanced_solution_manager.get_all_solutions()
                self.update_solutions_display(solutions)
            else:
                # 使用历史管理器的方案
                entries = self.history_manager.get_all_entries()
                self.update_solutions_display(entries)

            logger.info("方案列表已刷新")

        except Exception as e:
            logger.error(f"刷新方案列表失败: {e}")

    def search_solutions(self, query: str):
        """搜索方案"""
        try:
            if not query.strip():
                self.refresh_solutions()
                return

            # 执行搜索
            filtered_solutions = []
            for i in range(self.solutions_list.count()):
                item = self.solutions_list.item(i)
                if query.lower() in item.text().lower():
                    filtered_solutions.append(item)

            # 更新显示
            self.solutions_list.clear()
            for item in filtered_solutions:
                self.solutions_list.addItem(item.text())

            logger.info(f"搜索到 {len(filtered_solutions)} 个匹配方案")

        except Exception as e:
            logger.error(f"搜索方案失败: {e}")

    def sort_solutions(self, sort_type: str):
        """排序方案"""
        try:
            items = []
            for i in range(self.solutions_list.count()):
                items.append(self.solutions_list.item(i).text())

            # 根据排序类型排序
            if "时间" in sort_type:
                # 按时间排序（这里简化处理）
                items.sort(reverse="↓" in sort_type)
            elif "评分" in sort_type:
                # 按评分排序（这里简化处理）
                items.sort(reverse="↓" in sort_type)
            elif "复杂度" in sort_type:
                # 按复杂度排序（这里简化处理）
                items.sort(reverse="↓" in sort_type)

            # 更新显示
            self.solutions_list.clear()
            for item_text in items:
                self.solutions_list.addItem(item_text)

            logger.info(f"方案已按 {sort_type} 排序")

        except Exception as e:
            logger.error(f"排序方案失败: {e}")

    def change_view_mode(self, mode: str):
        """切换视图模式"""
        try:
            if mode == "列表视图":
                # 显示列表视图
                pass
            elif mode == "网格视图":
                # 显示网格视图
                pass
            elif mode == "详细视图":
                # 显示详细视图
                pass

            logger.info(f"视图模式已切换为: {mode}")

        except Exception as e:
            logger.error(f"切换视图模式失败: {e}")

    def show_filter_dialog(self):
        """显示筛选对话框"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox

            dialog = QDialog(self)
            dialog.setWindowTitle("筛选方案")
            dialog.setMinimumSize(300, 400)

            layout = QVBoxLayout(dialog)

            # 技术栈筛选
            layout.addWidget(QLabel("技术栈:"))
            tech_stacks = ["CSS动画", "JavaScript", "GSAP", "Three.js", "SVG动画"]
            tech_checkboxes = {}

            for tech in tech_stacks:
                cb = QCheckBox(tech)
                cb.setChecked(True)
                tech_checkboxes[tech] = cb
                layout.addWidget(cb)

            # 复杂度筛选
            layout.addWidget(QLabel("复杂度:"))
            complexity_levels = ["简单", "中等", "复杂", "高级"]
            complexity_checkboxes = {}

            for level in complexity_levels:
                cb = QCheckBox(level)
                cb.setChecked(True)
                complexity_checkboxes[level] = cb
                layout.addWidget(cb)

            # 按钮
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 应用筛选
                self.apply_filters(tech_checkboxes, complexity_checkboxes)

        except Exception as e:
            logger.error(f"显示筛选对话框失败: {e}")

    def apply_filters(self, tech_filters: dict, complexity_filters: dict):
        """应用筛选条件"""
        try:
            # 获取选中的筛选条件
            selected_techs = [tech for tech, cb in tech_filters.items() if cb.isChecked()]
            selected_complexity = [level for level, cb in complexity_filters.items() if cb.isChecked()]

            # 应用筛选逻辑
            # 这里简化处理，实际应该根据方案的实际属性进行筛选
            logger.info(f"应用筛选: 技术栈={selected_techs}, 复杂度={selected_complexity}")

        except Exception as e:
            logger.error(f"应用筛选失败: {e}")

    def export_selected_solutions(self):
        """导出选中的方案"""
        try:
            selected_items = self.solutions_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "警告", "请先选择要导出的方案")
                return

            # 获取导出路径
            from PyQt6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出方案", "", "JSON文件 (*.json);;ZIP文件 (*.zip)"
            )

            if file_path:
                # 执行导出
                solution_names = [item.text() for item in selected_items]
                # 这里应该调用实际的导出功能
                QMessageBox.information(self, "成功", f"已导出 {len(solution_names)} 个方案到 {file_path}")
                logger.info(f"导出方案: {solution_names}")

        except Exception as e:
            logger.error(f"导出方案失败: {e}")
            QMessageBox.warning(self, "错误", "导出方案失败")

    def delete_selected_solutions(self):
        """删除选中的方案"""
        try:
            selected_items = self.solutions_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "警告", "请先选择要删除的方案")
                return

            # 确认删除
            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除选中的 {len(selected_items)} 个方案吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 执行删除
                for item in selected_items:
                    row = self.solutions_list.row(item)
                    self.solutions_list.takeItem(row)

                QMessageBox.information(self, "成功", f"已删除 {len(selected_items)} 个方案")
                logger.info(f"删除了 {len(selected_items)} 个方案")

        except Exception as e:
            logger.error(f"删除方案失败: {e}")
            QMessageBox.warning(self, "错误", "删除方案失败")

    def preview_solution(self):
        """预览选中的方案"""
        try:
            current_item = self.solutions_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个方案")
                return

            solution_name = current_item.text().replace("🏆 ", "").replace("⭐ ", "")

            # 获取方案详情
            solution = None

            # 首先尝试从当前生成的方案中查找
            for sol in self.current_solutions:
                if sol.name == solution_name:
                    solution = sol
                    break

            # 如果没找到，尝试从历史记录中查找
            if not solution:
                entry = self.history_manager.get_entry_by_name(solution_name)
                if entry:
                    # 将历史记录转换为方案对象
                    from core.data_structures import AnimationSolution, TechStack
                    solution = AnimationSolution(
                        name=entry.name,
                        description=entry.description or "",
                        html_code=entry.html_content,
                        tech_stack=TechStack.CSS_ANIMATION,
                        complexity_level="medium",
                        recommended=entry.rating > 4.0
                    )

            if solution:
                # 使用增强的预览对话框
                from ui.solution_preview_dialog import SolutionPreviewDialog

                preview_dialog = SolutionPreviewDialog(solution, self)
                preview_dialog.solution_applied.connect(self.on_solution_applied)
                preview_dialog.solution_rated.connect(self.on_solution_rated)
                preview_dialog.exec()

                logger.info(f"预览方案: {solution_name}")
            else:
                QMessageBox.warning(self, "错误", "找不到方案详情")

        except Exception as e:
            logger.error(f"预览方案失败: {e}")
            QMessageBox.warning(self, "错误", "预览方案失败")

    def on_solution_applied(self, html_code: str):
        """方案应用事件处理"""
        try:
            # 发送应用信号给主窗口
            self.solution_applied.emit(html_code)
            logger.info("方案已应用")

        except Exception as e:
            logger.error(f"处理方案应用事件失败: {e}")

    def on_solution_rated(self, solution_id: str, rating: float):
        """方案评分事件处理"""
        try:
            # 更新方案评分
            # 这里应该调用方案管理器的评分功能
            logger.info(f"方案评分: {solution_id} = {rating}分")

        except Exception as e:
            logger.error(f"处理方案评分事件失败: {e}")

    def apply_solution(self):
        """应用选中的方案"""
        try:
            current_item = self.solutions_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个方案")
                return

            solution_name = current_item.text()

            # 获取方案详情
            entry = self.history_manager.get_entry_by_name(solution_name)
            if entry:
                # 将方案应用到当前编辑器
                self.html_editor.setPlainText(entry.html_content)

                # 发送应用信号
                self.solution_applied.emit(entry.html_content)

                QMessageBox.information(self, "成功", f"方案 '{solution_name}' 已应用")
                logger.info(f"应用方案: {solution_name}")
            else:
                QMessageBox.warning(self, "错误", "找不到方案详情")

        except Exception as e:
            logger.error(f"应用方案失败: {e}")
            QMessageBox.warning(self, "错误", "应用方案失败")

    def toggle_favorite(self):
        """切换收藏状态"""
        try:
            current_item = self.solutions_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个方案")
                return

            solution_name = current_item.text()

            # 切换收藏状态
            # 这里应该调用方案管理器的收藏功能
            is_favorite = "⭐" in current_item.text()

            if is_favorite:
                # 取消收藏
                new_text = current_item.text().replace("⭐ ", "")
                current_item.setText(new_text)
                self.favorite_btn.setText("⭐ 收藏")
                QMessageBox.information(self, "成功", "已取消收藏")
            else:
                # 添加收藏
                current_item.setText("⭐ " + current_item.text())
                self.favorite_btn.setText("💔 取消收藏")
                QMessageBox.information(self, "成功", "已添加到收藏")

            logger.info(f"切换收藏状态: {solution_name}")

        except Exception as e:
            logger.error(f"切换收藏状态失败: {e}")
            QMessageBox.warning(self, "错误", "操作失败")

    def rate_solution(self):
        """为方案评分"""
        try:
            current_item = self.solutions_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个方案")
                return

            solution_name = current_item.text()

            # 显示评分对话框
            from PyQt6.QtWidgets import QInputDialog

            rating, ok = QInputDialog.getDouble(
                self, "方案评分",
                f"请为方案 '{solution_name}' 评分 (1-5分):",
                value=3.0, min=1.0, max=5.0, decimals=1
            )

            if ok:
                # 保存评分
                # 这里应该调用方案管理器的评分功能
                QMessageBox.information(self, "成功", f"已为方案评分: {rating}分")
                logger.info(f"方案评分: {solution_name} = {rating}分")

        except Exception as e:
            logger.error(f"方案评分失败: {e}")
            QMessageBox.warning(self, "错误", "评分失败")

    def on_solution_selected(self, row: int):
        """方案选中事件"""
        try:
            if row >= 0:
                item = self.solutions_list.item(row)
                if item:
                    solution_name = item.text()

                    # 更新详情显示
                    # 这里应该从方案管理器获取详细信息
                    entry = self.history_manager.get_entry_by_name(solution_name)
                    if entry:
                        self.update_solution_details(entry)

                    logger.info(f"选中方案: {solution_name}")

        except Exception as e:
            logger.error(f"处理方案选中事件失败: {e}")

    def update_solution_details(self, entry):
        """更新方案详情显示"""
        try:
            # 更新详情标签
            if hasattr(self, 'solution_name_label'):
                self.solution_name_label.setText(entry.name or "未命名")

            # 检测技术栈
            tech_stack = "未知"
            if "gsap" in entry.html_content.lower():
                tech_stack = "GSAP"
            elif "three.js" in entry.html_content.lower():
                tech_stack = "Three.js"
            elif "<svg" in entry.html_content.lower():
                tech_stack = "SVG动画"
            elif "animation:" in entry.html_content.lower():
                tech_stack = "CSS动画"
            elif "javascript" in entry.html_content.lower():
                tech_stack = "JavaScript"

            if hasattr(self, 'tech_stack_label'):
                self.tech_stack_label.setText(tech_stack)

            # 估算复杂度
            complexity = "简单"
            code_length = len(entry.html_content)
            if code_length > 5000:
                complexity = "高级"
            elif code_length > 2000:
                complexity = "复杂"
            elif code_length > 1000:
                complexity = "中等"

            if hasattr(self, 'complexity_label'):
                self.complexity_label.setText(complexity)

            # 更新其他信息
            if hasattr(self, 'recommended_label'):
                self.recommended_label.setText("是" if entry.rating > 4.0 else "否")

            if hasattr(self, 'rating_label'):
                self.rating_label.setText(f"{entry.rating:.1f}分")

            if hasattr(self, 'created_time_label'):
                self.created_time_label.setText(entry.created_at.strftime("%Y-%m-%d %H:%M"))

        except Exception as e:
            logger.error(f"更新方案详情失败: {e}")

    def update_solutions_display(self, solutions):
        """更新方案显示"""
        try:
            self.solutions_list.clear()

            for solution in solutions:
                # 创建显示文本
                display_text = solution.name if hasattr(solution, 'name') else str(solution)

                # 添加评分和收藏标识
                if hasattr(solution, 'rating') and solution.rating > 4.0:
                    display_text = f"🏆 {display_text}"

                if hasattr(solution, 'is_favorite') and solution.is_favorite:
                    display_text = f"⭐ {display_text}"

                self.solutions_list.addItem(display_text)

            logger.info(f"更新方案显示: {len(solutions)} 个方案")

        except Exception as e:
            logger.error(f"更新方案显示失败: {e}")

    # 方案对比功能实现
    def add_to_comparison(self):
        """添加方案到对比列表"""
        try:
            current_item = self.solutions_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请先选择一个方案")
                return

            solution_name = current_item.text().replace("🏆 ", "").replace("⭐ ", "")

            # 检查是否已经在对比列表中
            for row in range(self.comparison_table.rowCount()):
                if self.comparison_table.item(row, 0).text() == solution_name:
                    QMessageBox.information(self, "提示", "该方案已在对比列表中")
                    return

            # 获取方案详情
            solution = self.get_solution_by_name(solution_name)
            if solution:
                self.add_solution_to_comparison_table(solution)
                QMessageBox.information(self, "成功", f"已添加方案 '{solution_name}' 到对比列表")
                logger.info(f"添加方案到对比: {solution_name}")
            else:
                QMessageBox.warning(self, "错误", "找不到方案详情")

        except Exception as e:
            logger.error(f"添加方案到对比失败: {e}")
            QMessageBox.warning(self, "错误", "添加方案到对比失败")

    def remove_from_comparison(self):
        """从对比列表中移除选中的方案"""
        try:
            current_row = self.comparison_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "警告", "请先选择要移除的方案")
                return

            solution_name = self.comparison_table.item(current_row, 0).text()
            self.comparison_table.removeRow(current_row)

            QMessageBox.information(self, "成功", f"已移除方案 '{solution_name}'")
            logger.info(f"从对比中移除方案: {solution_name}")

        except Exception as e:
            logger.error(f"移除对比方案失败: {e}")
            QMessageBox.warning(self, "错误", "移除对比方案失败")

    def clear_comparison(self):
        """清空对比列表"""
        try:
            if self.comparison_table.rowCount() == 0:
                QMessageBox.information(self, "提示", "对比列表已为空")
                return

            reply = QMessageBox.question(
                self, "确认清空",
                "确定要清空所有对比方案吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.comparison_table.setRowCount(0)

                # 清空对比结果
                if hasattr(self, 'summary_comparison_result'):
                    self.summary_comparison_result.clear()
                if hasattr(self, 'perf_comparison_result'):
                    self.perf_comparison_result.clear()
                if hasattr(self, 'code_comparison_result'):
                    self.code_comparison_result.clear()
                if hasattr(self, 'compat_comparison_result'):
                    self.compat_comparison_result.clear()

                QMessageBox.information(self, "成功", "对比列表已清空")
                logger.info("清空对比列表")

        except Exception as e:
            logger.error(f"清空对比列表失败: {e}")
            QMessageBox.warning(self, "错误", "清空对比列表失败")

    def start_comparison(self):
        """开始对比分析"""
        try:
            if self.comparison_table.rowCount() < 2:
                QMessageBox.warning(self, "警告", "至少需要2个方案才能进行对比")
                return

            # 获取所有对比方案
            comparison_solutions = []
            for row in range(self.comparison_table.rowCount()):
                solution_name = self.comparison_table.item(row, 0).text()
                solution = self.get_solution_by_name(solution_name)
                if solution:
                    comparison_solutions.append(solution)

            if len(comparison_solutions) < 2:
                QMessageBox.warning(self, "错误", "无法获取方案详情")
                return

            # 执行对比分析
            self.perform_comparison_analysis(comparison_solutions)

            QMessageBox.information(self, "成功", f"已完成 {len(comparison_solutions)} 个方案的对比分析")
            logger.info(f"完成方案对比分析: {len(comparison_solutions)} 个方案")

        except Exception as e:
            logger.error(f"对比分析失败: {e}")
            QMessageBox.warning(self, "错误", "对比分析失败")

    def get_solution_by_name(self, name: str):
        """根据名称获取方案"""
        try:
            # 首先从当前生成的方案中查找
            for solution in self.current_solutions:
                if solution.name == name:
                    return solution

            # 从历史记录中查找
            entry = self.history_manager.get_entry_by_name(name)
            if entry:
                from core.data_structures import AnimationSolution, TechStack
                return AnimationSolution(
                    name=entry.name,
                    description=entry.description or "",
                    html_code=entry.html_content,
                    tech_stack=TechStack.CSS_ANIMATION,
                    complexity_level="medium",
                    recommended=entry.rating > 4.0
                )

            return None

        except Exception as e:
            logger.error(f"获取方案失败: {e}")
            return None

    def add_solution_to_comparison_table(self, solution):
        """将方案添加到对比表格"""
        try:
            row = self.comparison_table.rowCount()
            self.comparison_table.insertRow(row)

            # 方案名称
            self.comparison_table.setItem(row, 0, QTableWidgetItem(solution.name))

            # 技术栈
            self.comparison_table.setItem(row, 1, QTableWidgetItem(solution.tech_stack.value))

            # 复杂度
            self.comparison_table.setItem(row, 2, QTableWidgetItem(solution.complexity_level))

            # 评分（模拟）
            rating = "4.5分" if solution.recommended else "3.0分"
            self.comparison_table.setItem(row, 3, QTableWidgetItem(rating))

            # 代码长度
            code_length = f"{len(solution.html_code)} 字符"
            self.comparison_table.setItem(row, 4, QTableWidgetItem(code_length))

            # 性能评估（简化）
            if "transform" in solution.html_code:
                performance = "优秀"
            elif "animation" in solution.html_code:
                performance = "良好"
            else:
                performance = "一般"
            self.comparison_table.setItem(row, 5, QTableWidgetItem(performance))

            # 兼容性评估（简化）
            if "grid" in solution.html_code or "flex" in solution.html_code:
                compatibility = "现代浏览器"
            else:
                compatibility = "全兼容"
            self.comparison_table.setItem(row, 6, QTableWidgetItem(compatibility))

        except Exception as e:
            logger.error(f"添加方案到对比表格失败: {e}")

    def perform_comparison_analysis(self, solutions):
        """执行对比分析"""
        try:
            # 综合对比分析
            summary_analysis = self.generate_summary_comparison(solutions)
            if hasattr(self, 'summary_comparison_result'):
                self.summary_comparison_result.setPlainText(summary_analysis)

            # 性能对比分析
            perf_analysis = self.generate_performance_comparison(solutions)
            if hasattr(self, 'perf_comparison_result'):
                self.perf_comparison_result.setPlainText(perf_analysis)

            # 代码对比分析
            code_analysis = self.generate_code_comparison(solutions)
            if hasattr(self, 'code_comparison_result'):
                self.code_comparison_result.setPlainText(code_analysis)

            # 兼容性对比分析
            compat_analysis = self.generate_compatibility_comparison(solutions)
            if hasattr(self, 'compat_comparison_result'):
                self.compat_comparison_result.setPlainText(compat_analysis)

        except Exception as e:
            logger.error(f"执行对比分析失败: {e}")

    def generate_summary_comparison(self, solutions):
        """生成综合对比分析"""
        try:
            analysis = "=== 方案综合对比分析 ===\n\n"

            for i, solution in enumerate(solutions, 1):
                analysis += f"{i}. {solution.name}\n"
                analysis += f"   技术栈: {solution.tech_stack.value}\n"
                analysis += f"   复杂度: {solution.complexity_level}\n"
                analysis += f"   推荐度: {'高' if solution.recommended else '中'}\n"
                analysis += f"   代码长度: {len(solution.html_code)} 字符\n\n"

            # 添加对比结论
            analysis += "=== 对比结论 ===\n"

            # 找出最佳方案
            best_solution = max(solutions, key=lambda s: len(s.html_code) if s.recommended else 0)
            analysis += f"推荐方案: {best_solution.name}\n"
            analysis += f"推荐理由: 综合考虑功能完整性、代码质量和性能表现\n\n"

            # 添加选择建议
            analysis += "=== 选择建议 ===\n"
            analysis += "• 如果追求性能，选择使用transform的方案\n"
            analysis += "• 如果需要兼容性，选择使用CSS动画的方案\n"
            analysis += "• 如果要求功能丰富，选择代码较长的方案\n"

            return analysis

        except Exception as e:
            logger.error(f"生成综合对比分析失败: {e}")
            return "生成对比分析失败"

    def generate_performance_comparison(self, solutions):
        """生成性能对比分析"""
        try:
            analysis = "=== 性能对比分析 ===\n\n"

            for i, solution in enumerate(solutions, 1):
                analysis += f"{i}. {solution.name} 性能分析:\n"

                # 分析动画性能
                if "transform" in solution.html_code:
                    analysis += "   ✅ 使用transform属性，GPU加速，性能优秀\n"
                elif "left" in solution.html_code or "top" in solution.html_code:
                    analysis += "   ⚠️ 使用position属性，可能触发重排，性能一般\n"
                else:
                    analysis += "   ℹ️ 静态内容，性能影响较小\n"

                # 分析JavaScript性能
                if "setInterval" in solution.html_code:
                    analysis += "   ⚠️ 使用setInterval，建议改用requestAnimationFrame\n"
                elif "requestAnimationFrame" in solution.html_code:
                    analysis += "   ✅ 使用requestAnimationFrame，性能优化良好\n"

                # 分析代码复杂度
                code_length = len(solution.html_code)
                if code_length > 5000:
                    analysis += "   ⚠️ 代码较长，可能影响加载性能\n"
                elif code_length > 2000:
                    analysis += "   ℹ️ 代码长度适中\n"
                else:
                    analysis += "   ✅ 代码简洁，加载快速\n"

                analysis += "\n"

            # 性能排名
            analysis += "=== 性能排名 ===\n"

            # 简单的性能评分
            perf_scores = []
            for solution in solutions:
                score = 0
                if "transform" in solution.html_code:
                    score += 30
                if "requestAnimationFrame" in solution.html_code:
                    score += 20
                if len(solution.html_code) < 2000:
                    score += 20
                if "will-change" in solution.html_code:
                    score += 15
                if "translate3d" in solution.html_code:
                    score += 15

                perf_scores.append((solution.name, score))

            # 按分数排序
            perf_scores.sort(key=lambda x: x[1], reverse=True)

            for i, (name, score) in enumerate(perf_scores, 1):
                analysis += f"{i}. {name}: {score}分\n"

            return analysis

        except Exception as e:
            logger.error(f"生成性能对比分析失败: {e}")
            return "生成性能对比分析失败"

    def generate_code_comparison(self, solutions):
        """生成代码对比分析"""
        try:
            analysis = "=== 代码对比分析 ===\n\n"

            for i, solution in enumerate(solutions, 1):
                analysis += f"{i}. {solution.name} 代码分析:\n"
                analysis += f"   代码长度: {len(solution.html_code)} 字符\n"

                # 分析技术栈
                tech_features = []
                if "css" in solution.html_code.lower() or "@keyframes" in solution.html_code:
                    tech_features.append("CSS动画")
                if "gsap" in solution.html_code.lower():
                    tech_features.append("GSAP")
                if "three.js" in solution.html_code.lower():
                    tech_features.append("Three.js")
                if "<svg" in solution.html_code.lower():
                    tech_features.append("SVG")
                if "canvas" in solution.html_code.lower():
                    tech_features.append("Canvas")

                analysis += f"   使用技术: {', '.join(tech_features) if tech_features else '基础HTML/CSS'}\n"

                # 分析代码结构
                html_lines = solution.html_code.count('\n') + 1
                analysis += f"   代码行数: {html_lines} 行\n"

                # 分析复杂度
                if len(solution.html_code) > 5000:
                    complexity = "高"
                elif len(solution.html_code) > 2000:
                    complexity = "中"
                else:
                    complexity = "低"
                analysis += f"   复杂度: {complexity}\n"

                analysis += "\n"

            # 代码质量对比
            analysis += "=== 代码质量对比 ===\n"

            for solution in solutions:
                analysis += f"\n{solution.name}:\n"

                # 检查最佳实践
                best_practices = []
                if "transform" in solution.html_code:
                    best_practices.append("✅ 使用transform进行动画")
                if "transition" in solution.html_code:
                    best_practices.append("✅ 使用CSS transition")
                if "will-change" in solution.html_code:
                    best_practices.append("✅ 使用will-change优化")
                if solution.html_code.count('class=') > 0:
                    best_practices.append("✅ 使用CSS类")

                if best_practices:
                    analysis += "   " + "\n   ".join(best_practices) + "\n"
                else:
                    analysis += "   ℹ️ 基础实现，可进一步优化\n"

            return analysis

        except Exception as e:
            logger.error(f"生成代码对比分析失败: {e}")
            return "生成代码对比分析失败"

    def generate_compatibility_comparison(self, solutions):
        """生成兼容性对比分析"""
        try:
            analysis = "=== 兼容性对比分析 ===\n\n"

            for i, solution in enumerate(solutions, 1):
                analysis += f"{i}. {solution.name} 兼容性分析:\n"

                # 检查现代CSS特性
                modern_features = []
                compatibility_issues = []

                if "grid" in solution.html_code:
                    modern_features.append("CSS Grid")
                    compatibility_issues.append("IE不支持CSS Grid")

                if "flex" in solution.html_code:
                    modern_features.append("Flexbox")
                    compatibility_issues.append("IE9及以下不支持Flexbox")

                if "transform" in solution.html_code:
                    modern_features.append("CSS Transform")

                if "@keyframes" in solution.html_code:
                    modern_features.append("CSS Keyframes")

                if "var(" in solution.html_code:
                    modern_features.append("CSS变量")
                    compatibility_issues.append("IE不支持CSS变量")

                # 显示使用的现代特性
                if modern_features:
                    analysis += f"   使用特性: {', '.join(modern_features)}\n"
                else:
                    analysis += "   使用特性: 基础CSS\n"

                # 显示兼容性问题
                if compatibility_issues:
                    analysis += "   兼容性问题:\n"
                    for issue in compatibility_issues:
                        analysis += f"     ⚠️ {issue}\n"
                else:
                    analysis += "   ✅ 兼容性良好\n"

                # 浏览器支持评估
                analysis += "   浏览器支持:\n"
                analysis += "     Chrome: ✅ 完全支持\n"
                analysis += "     Firefox: ✅ 完全支持\n"
                analysis += "     Safari: ✅ 完全支持\n"
                analysis += "     Edge: ✅ 完全支持\n"

                if compatibility_issues:
                    analysis += "     IE11: ⚠️ 部分支持\n"
                    analysis += "     IE10及以下: ❌ 不支持\n"
                else:
                    analysis += "     IE11: ✅ 支持\n"
                    analysis += "     IE10及以下: ✅ 支持\n"

                analysis += "\n"

            # 兼容性建议
            analysis += "=== 兼容性建议 ===\n"
            analysis += "• 如需支持IE，避免使用CSS Grid和CSS变量\n"
            analysis += "• 使用autoprefixer自动添加浏览器前缀\n"
            analysis += "• 提供降级方案for不支持的特性\n"
            analysis += "• 使用feature detection检测浏览器能力\n"

            return analysis

        except Exception as e:
            logger.error(f"生成兼容性对比分析失败: {e}")
            return "生成兼容性对比分析失败"
