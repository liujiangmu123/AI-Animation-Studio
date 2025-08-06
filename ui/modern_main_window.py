"""
AI Animation Studio - 现代化主窗口
按照五区域专业布局重新设计主窗口
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QToolBar, QStatusBar, QMenuBar, QLabel, QPushButton,
    QFrame, QTabWidget, QDockWidget, QTextEdit, QProgressBar, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QAction

from ui.theme_system import get_theme_manager, ColorRole
from ui.stage_widget import StageWidget
from ui.elements_widget import ElementsWidget
from ui.preview_widget import PreviewWidget
from ui.library_manager_widget import LibraryManagerWidget
from core.project_manager import ProjectManager
from core.command_manager import CommandManager
from core.logger import get_logger

logger = get_logger("modern_main_window")


class ModernToolBar(QToolBar):
    """现代化工具栏"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.theme_manager = get_theme_manager()
        self.setup_toolbar()
    
    def setup_toolbar(self):
        """设置工具栏"""
        self.setMovable(False)
        self.setFloatable(False)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setIconSize(QSize(24, 24))
        
        # 应用主题样式
        self.apply_theme()
    
    def apply_theme(self):
        """应用主题样式"""
        theme = self.theme_manager.get_current_theme()
        
        self.setStyleSheet(f"""
            QToolBar {{
                background-color: {self.theme_manager.get_color(ColorRole.SURFACE)};
                border: 1px solid {self.theme_manager.get_color(ColorRole.BORDER)};
                border-radius: {theme.border_radius.sm}px;
                padding: {theme.spacing.sm}px;
                spacing: {theme.spacing.sm}px;
            }}
            
            QToolButton {{
                background-color: transparent;
                color: {self.theme_manager.get_color(ColorRole.TEXT_PRIMARY)};
                border: 1px solid transparent;
                border-radius: {theme.border_radius.sm}px;
                padding: {theme.spacing.sm}px {theme.spacing.md}px;
                font-weight: {theme.typography.medium_weight};
                min-height: 32px;
            }}
            
            QToolButton:hover {{
                background-color: {self.theme_manager.get_color(ColorRole.PRIMARY)};
                color: white;
                border-color: {self.theme_manager.get_color(ColorRole.PRIMARY)};
            }}
            
            QToolButton:pressed {{
                background-color: {self.theme_manager.get_color(ColorRole.SECONDARY)};
            }}
            
            QToolButton[class="ai-button"] {{
                background-color: {self.theme_manager.get_color(ColorRole.AI_FUNCTION)};
                color: white;
                border: none;
                font-weight: {theme.typography.bold_weight};
            }}
            
            QToolButton[class="ai-button"]:hover {{
                background-color: #FB923C;
            }}
        """)


class ResourcePanel(QDockWidget):
    """资源管理面板"""
    
    def __init__(self, parent=None):
        super().__init__("资源管理", parent)
        self.theme_manager = get_theme_manager()
        self.setup_panel()
    
    def setup_panel(self):
        """设置面板"""
        # 创建主容器
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 项目文件选项卡
        self.project_tab = self.create_project_tab()
        self.tab_widget.addTab(self.project_tab, "📁 项目")
        
        # 素材库选项卡
        self.assets_tab = self.create_assets_tab()
        self.tab_widget.addTab(self.assets_tab, "🎨 素材")
        
        # 元素管理选项卡
        self.elements_tab = ElementsWidget()
        self.tab_widget.addTab(self.elements_tab, "🧩 元素")
        
        # 模板库选项卡
        self.templates_tab = self.create_templates_tab()
        self.tab_widget.addTab(self.templates_tab, "📋 模板")
        
        # 操作历史选项卡
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "🔄 历史")
        
        layout.addWidget(self.tab_widget)
        self.setWidget(container)
        
        # 设置面板属性
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        
        # 应用主题
        self.apply_theme()
    
    def create_project_tab(self) -> QWidget:
        """创建项目文件选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 项目信息
        info_label = QLabel("当前项目: 新项目")
        info_label.setProperty("class", "subtitle")
        layout.addWidget(info_label)
        
        # 项目操作按钮
        buttons_layout = QHBoxLayout()
        
        new_btn = QPushButton("新建")
        open_btn = QPushButton("打开")
        save_btn = QPushButton("保存")
        
        buttons_layout.addWidget(new_btn)
        buttons_layout.addWidget(open_btn)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        return widget
    
    def create_assets_tab(self) -> QWidget:
        """创建素材库选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 素材分类
        categories = ["图片", "音频", "视频", "字体", "图标"]
        for category in categories:
            btn = QPushButton(f"📂 {category}")
            btn.setStyleSheet("text-align: left; padding: 8px;")
            layout.addWidget(btn)
        
        layout.addStretch()
        return widget
    
    def create_templates_tab(self) -> QWidget:
        """创建模板库选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 模板分类
        templates = ["基础动画", "文字效果", "图形动画", "转场效果", "特殊效果"]
        for template in templates:
            btn = QPushButton(f"📋 {template}")
            btn.setStyleSheet("text-align: left; padding: 8px;")
            layout.addWidget(btn)
        
        layout.addStretch()
        return widget
    
    def create_history_tab(self) -> QWidget:
        """创建操作历史选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 历史记录列表
        history_text = QTextEdit()
        history_text.setReadOnly(True)
        history_text.setMaximumHeight(200)
        history_text.setPlainText("操作历史将在这里显示...")
        
        layout.addWidget(QLabel("操作历史:"))
        layout.addWidget(history_text)
        
        # 历史操作按钮
        buttons_layout = QHBoxLayout()
        clear_btn = QPushButton("清空历史")
        export_btn = QPushButton("导出历史")
        
        buttons_layout.addWidget(clear_btn)
        buttons_layout.addWidget(export_btn)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        return widget
    
    def apply_theme(self):
        """应用主题"""
        theme = self.theme_manager.get_current_theme()
        
        self.setStyleSheet(f"""
            QDockWidget {{
                background-color: {self.theme_manager.get_color(ColorRole.SURFACE)};
                border: 1px solid {self.theme_manager.get_color(ColorRole.BORDER)};
                border-radius: {theme.border_radius.md}px;
            }}
            
            QDockWidget::title {{
                background-color: {self.theme_manager.get_color(ColorRole.PRIMARY)};
                color: white;
                padding: {theme.spacing.sm}px;
                font-weight: {theme.typography.bold_weight};
            }}
        """)


class AIControlPanel(QDockWidget):
    """AI控制面板"""
    
    def __init__(self, parent=None):
        super().__init__("AI控制中心", parent)
        self.theme_manager = get_theme_manager()
        self.setup_panel()
    
    def setup_panel(self):
        """设置面板"""
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # AI生成面板
        ai_frame = QFrame()
        ai_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        ai_layout = QVBoxLayout(ai_frame)
        
        # AI标题
        ai_title = QLabel("🤖 AI动画生成器")
        ai_title.setProperty("class", "title")
        ai_layout.addWidget(ai_title)
        
        # Prompt输入
        prompt_label = QLabel("描述您想要的动画:")
        ai_layout.addWidget(prompt_label)
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setMaximumHeight(100)
        self.prompt_input.setPlaceholderText("例如: 小球像火箭一样快速飞过去，要有科技感和拖尾效果...")
        ai_layout.addWidget(self.prompt_input)
        
        # AI生成按钮
        generate_btn = QPushButton("🚀 生成动画方案")
        generate_btn.setProperty("class", "ai-button")
        ai_layout.addWidget(generate_btn)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        ai_layout.addWidget(self.progress_bar)
        
        layout.addWidget(ai_frame)
        
        # 方案对比面板
        comparison_frame = QFrame()
        comparison_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        comparison_layout = QVBoxLayout(comparison_frame)
        
        comparison_title = QLabel("📊 方案对比")
        comparison_title.setProperty("class", "title")
        comparison_layout.addWidget(comparison_title)
        
        # 方案列表
        solutions_text = QTextEdit()
        solutions_text.setReadOnly(True)
        solutions_text.setMaximumHeight(150)
        solutions_text.setPlainText("AI生成的方案将在这里显示...")
        comparison_layout.addWidget(solutions_text)
        
        layout.addWidget(comparison_frame)
        
        # 协作面板
        collab_frame = QFrame()
        collab_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        collab_layout = QVBoxLayout(collab_frame)
        
        collab_title = QLabel("💬 协作评论")
        collab_title.setProperty("class", "title")
        collab_layout.addWidget(collab_title)
        
        # 评论区
        comments_text = QTextEdit()
        comments_text.setReadOnly(True)
        comments_text.setMaximumHeight(100)
        comments_text.setPlainText("团队评论将在这里显示...")
        collab_layout.addWidget(comments_text)
        
        layout.addWidget(collab_frame)
        
        layout.addStretch()
        self.setWidget(container)
        
        # 设置面板属性
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        
        # 应用主题
        self.apply_theme()
    
    def apply_theme(self):
        """应用主题"""
        theme = self.theme_manager.get_current_theme()
        
        self.setStyleSheet(f"""
            QDockWidget {{
                background-color: {self.theme_manager.get_color(ColorRole.SURFACE)};
                border: 1px solid {self.theme_manager.get_color(ColorRole.BORDER)};
                border-radius: {theme.border_radius.md}px;
            }}
            
            QDockWidget::title {{
                background-color: {self.theme_manager.get_color(ColorRole.AI_FUNCTION)};
                color: white;
                padding: {theme.spacing.sm}px;
                font-weight: {theme.typography.bold_weight};
            }}
            
            QFrame {{
                background-color: {self.theme_manager.get_color(ColorRole.BACKGROUND)};
                border: 1px solid {self.theme_manager.get_color(ColorRole.BORDER)};
                border-radius: {theme.border_radius.md}px;
                margin: {theme.spacing.sm}px;
                padding: {theme.spacing.md}px;
            }}
        """)


class TimelinePanel(QDockWidget):
    """时间轴面板"""
    
    def __init__(self, parent=None):
        super().__init__("时间轴", parent)
        self.theme_manager = get_theme_manager()
        self.setup_panel()
    
    def setup_panel(self):
        """设置面板"""
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # 时间轴控制
        controls_layout = QHBoxLayout()
        
        play_btn = QPushButton("▶ 播放")
        pause_btn = QPushButton("⏸ 暂停")
        stop_btn = QPushButton("⏹ 停止")
        
        controls_layout.addWidget(play_btn)
        controls_layout.addWidget(pause_btn)
        controls_layout.addWidget(stop_btn)
        controls_layout.addStretch()
        
        # 时间显示
        time_label = QLabel("时间: 00:00 / 05:00")
        controls_layout.addWidget(time_label)
        
        layout.addLayout(controls_layout)
        
        # 时间轴视图
        timeline_frame = QFrame()
        timeline_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        timeline_frame.setMinimumHeight(150)
        
        timeline_layout = QVBoxLayout(timeline_frame)
        
        # 音频波形
        audio_label = QLabel("🎵 音频波形区域")
        audio_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        audio_label.setStyleSheet("background-color: #f0f0f0; border: 1px dashed #ccc; padding: 20px;")
        timeline_layout.addWidget(audio_label)
        
        # 动画片段
        segments_label = QLabel("🎬 动画片段区域")
        segments_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        segments_label.setStyleSheet("background-color: #f0f8ff; border: 1px dashed #ccc; padding: 20px;")
        timeline_layout.addWidget(segments_label)
        
        layout.addWidget(timeline_frame)
        
        self.setWidget(container)
        
        # 设置面板属性
        self.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        
        # 应用主题
        self.apply_theme()
    
    def apply_theme(self):
        """应用主题"""
        theme = self.theme_manager.get_current_theme()
        
        self.setStyleSheet(f"""
            QDockWidget {{
                background-color: {self.theme_manager.get_color(ColorRole.SURFACE)};
                border: 1px solid {self.theme_manager.get_color(ColorRole.BORDER)};
                border-radius: {theme.border_radius.md}px;
            }}
            
            QDockWidget::title {{
                background-color: {self.theme_manager.get_color(ColorRole.PERFORMANCE)};
                color: white;
                padding: {theme.spacing.sm}px;
                font-weight: {theme.typography.bold_weight};
            }}
        """)


class ModernMainWindow(QMainWindow):
    """现代化主窗口"""
    
    project_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.theme_manager = get_theme_manager()
        self.project_manager = ProjectManager()
        self.command_manager = CommandManager()
        
        self.setup_window()
        self.setup_ui()
        self.setup_connections()
        
        logger.info("现代化主窗口初始化完成")
    
    def setup_window(self):
        """设置窗口"""
        self.setWindowTitle("AI Animation Studio - 现代化界面")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # 应用主题
        self.theme_manager.apply_theme_to_application()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建中央工作区
        self.create_central_widget()
        
        # 创建停靠面板
        self.create_dock_panels()
        
        # 创建状态栏
        self.create_status_bar()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        new_action = QAction("新建项目(&N)", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        open_action = QAction("打开项目(&O)", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        
        save_action = QAction("保存项目(&S)", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        
        self.undo_action = QAction("撤销(&U)", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.setEnabled(False)
        edit_menu.addAction(self.undo_action)
        
        self.redo_action = QAction("重做(&R)", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.setEnabled(False)
        edit_menu.addAction(self.redo_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        theme_action = QAction("切换主题(&T)", self)
        theme_action.triggered.connect(self.theme_manager.toggle_theme)
        view_menu.addAction(theme_action)
    
    def create_toolbar(self):
        """创建工具栏 - 按照设计方案优化为60px高度的专业工具栏"""
        self.main_toolbar = ModernToolBar("主工具栏", self)
        self.main_toolbar.setFixedHeight(60)  # 设置固定高度60px
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)

        # 左侧主要功能区
        project_menu = self.create_toolbar_menu("项目", [
            ("新建项目", "Ctrl+N", "📄"),
            ("打开项目", "Ctrl+O", "📂"),
            ("保存项目", "Ctrl+S", "💾")
        ])
        self.main_toolbar.addWidget(project_menu)

        edit_menu = self.create_toolbar_menu("编辑", [
            ("撤销", "Ctrl+Z", "↶"),
            ("重做", "Ctrl+Y", "↷"),
            ("复制", "Ctrl+C", "📋")
        ])
        self.main_toolbar.addWidget(edit_menu)

        # AI生成按钮 - 突出显示
        ai_action = self.main_toolbar.addAction("🤖 AI生成")
        ai_action.setProperty("class", "ai-button")
        ai_action.setToolTip("使用AI生成动画")

        # 预览和协作功能
        preview_action = self.main_toolbar.addAction("👁️ 预览")
        preview_action.setToolTip("预览动画效果")

        collab_action = self.main_toolbar.addAction("👥 协作")
        collab_action.setToolTip("团队协作功能")

        export_menu = self.create_toolbar_menu("导出", [
            ("导出HTML", "", "🌐"),
            ("导出视频", "", "🎥"),
            ("导出图片", "", "🖼️")
        ])
        self.main_toolbar.addWidget(export_menu)

        # 右侧状态和设置区
        self.main_toolbar.addSeparator()

        # 编辑模式切换
        mode_toggle = QPushButton("🔄 编辑模式")
        mode_toggle.setCheckable(True)
        mode_toggle.setChecked(True)
        mode_toggle.setToolTip("切换编辑/预览模式")
        self.main_toolbar.addWidget(mode_toggle)

        settings_action = self.main_toolbar.addAction("⚙️ 设置")
        settings_action.setToolTip("系统设置")

        user_action = self.main_toolbar.addAction("👤 用户")
        user_action.setToolTip("用户账户")

    def create_toolbar_menu(self, title, items):
        """创建工具栏下拉菜单"""
        menu_button = QPushButton(f"{title} ▼")
        menu_button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 8px 12px;
                background: transparent;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(74, 144, 226, 0.1);
                border-radius: 4px;
            }
        """)

        menu = QMenu(menu_button)
        for item_name, shortcut, icon in items:
            action = QAction(f"{icon} {item_name}", menu)
            if shortcut:
                action.setShortcut(shortcut)
            menu.addAction(action)

        menu_button.setMenu(menu)
        return menu_button
    
    def create_central_widget(self):
        """创建中央工作区"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主工作区选项卡
        self.main_tabs = QTabWidget()
        
        # 舞台编辑选项卡
        self.stage_widget = StageWidget()
        self.main_tabs.addTab(self.stage_widget, "🎨 舞台编辑")
        
        # 设备预览选项卡
        self.preview_widget = PreviewWidget()
        self.main_tabs.addTab(self.preview_widget, "📱 设备预览")
        
        # 测试面板选项卡
        test_widget = QWidget()
        self.main_tabs.addTab(test_widget, "🧪 测试面板")
        
        # 性能监控选项卡
        performance_widget = QWidget()
        self.main_tabs.addTab(performance_widget, "📊 性能监控")
        
        # 调试面板选项卡
        debug_widget = QWidget()
        self.main_tabs.addTab(debug_widget, "🔍 调试面板")
        
        # 设置布局
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.main_tabs)
    
    def create_dock_panels(self):
        """创建停靠面板 - 按照设计方案的五区域布局"""
        # 资源管理面板（左侧，300px宽度）
        self.resource_panel = ResourcePanel(self)
        self.resource_panel.setMinimumWidth(280)
        self.resource_panel.setMaximumWidth(320)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.resource_panel)

        # AI控制面板（右侧，350px宽度）
        self.ai_panel = AIControlPanel(self)
        self.ai_panel.setMinimumWidth(330)
        self.ai_panel.setMaximumWidth(370)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ai_panel)

        # 时间轴面板（底部，200px高度）
        self.timeline_panel = TimelinePanel(self)
        self.timeline_panel.setMinimumHeight(180)
        self.timeline_panel.setMaximumHeight(220)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.timeline_panel)

        # 设置停靠面板初始大小 - 严格按照设计方案
        self.resizeDocks([self.resource_panel], [300], Qt.Orientation.Horizontal)
        self.resizeDocks([self.ai_panel], [350], Qt.Orientation.Horizontal)
        self.resizeDocks([self.timeline_panel], [200], Qt.Orientation.Vertical)

        # 设置停靠面板样式
        self.apply_dock_panel_styles()
    
    def create_status_bar(self):
        """创建状态栏 - 按照设计方案24px高度"""
        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(24)  # 严格按照设计方案24px高度
        self.setStatusBar(self.status_bar)

        # 左侧状态信息 - 按照设计方案的内容布局
        status_info = QLabel("📍选中: 小球元素 | 🎯位置: (400,300)")
        status_info.setStyleSheet("color: #64748B; font-size: 11px;")
        self.status_bar.addWidget(status_info)

        # 中间状态信息
        save_status = QLabel("💾已保存")
        save_status.setStyleSheet("color: #10B981; font-size: 11px;")
        self.status_bar.addWidget(save_status)

        # 右侧性能和协作信息
        performance_info = QLabel("⚡GPU:45%")
        performance_info.setStyleSheet("color: #F59E0B; font-size: 11px;")
        self.status_bar.addPermanentWidget(performance_info)

        online_users = QLabel("👥在线:3人")
        online_users.setStyleSheet("color: #10B981; font-size: 11px;")
        self.status_bar.addPermanentWidget(online_users)

        # 应用状态栏样式
        self.apply_status_bar_styles()
    
    def setup_connections(self):
        """设置信号连接"""
        # 主题变更连接
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # 撤销重做连接
        self.undo_action.triggered.connect(self.command_manager.undo)
        self.redo_action.triggered.connect(self.command_manager.redo)
    
    def on_theme_changed(self, theme_name: str):
        """主题变更处理"""
        logger.info(f"主题已变更为: {theme_name}")
        # 重新应用样式
        self.resource_panel.apply_theme()
        self.ai_panel.apply_theme()
        self.timeline_panel.apply_theme()
        self.apply_dock_panel_styles()
        self.apply_status_bar_styles()

    def apply_dock_panel_styles(self):
        """应用停靠面板样式"""
        theme = self.theme_manager.get_current_theme()

        # 统一的停靠面板样式
        dock_style = f"""
            QDockWidget {{
                background-color: {self.theme_manager.get_color(ColorRole.SURFACE)};
                border: 1px solid {self.theme_manager.get_color(ColorRole.BORDER)};
                border-radius: {theme.border_radius.md}px;
                font-family: {theme.typography.primary_font};
            }}

            QDockWidget::title {{
                background-color: {self.theme_manager.get_color(ColorRole.PRIMARY)};
                color: white;
                padding: {theme.spacing.sm}px;
                font-weight: {theme.typography.medium_weight};
                font-size: {theme.typography.h4_size}px;
                text-align: center;
            }}

            QDockWidget::close-button, QDockWidget::float-button {{
                background-color: transparent;
                border: none;
                padding: 2px;
            }}

            QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
            }}
        """

        self.resource_panel.setStyleSheet(dock_style)
        self.ai_panel.setStyleSheet(dock_style)
        self.timeline_panel.setStyleSheet(dock_style)

    def apply_status_bar_styles(self):
        """应用状态栏样式"""
        theme = self.theme_manager.get_current_theme()

        status_style = f"""
            QStatusBar {{
                background-color: {self.theme_manager.get_color(ColorRole.SURFACE)};
                border-top: 1px solid {self.theme_manager.get_color(ColorRole.BORDER)};
                color: {self.theme_manager.get_color(ColorRole.TEXT_SECONDARY)};
                font-family: {theme.typography.primary_font};
                font-size: {theme.typography.caption_size}px;
                padding: 2px {theme.spacing.sm}px;
            }}

            QStatusBar QLabel {{
                background: transparent;
                border: none;
                padding: 0px {theme.spacing.xs}px;
            }}
        """

        self.status_bar.setStyleSheet(status_style)
        self.main_toolbar.apply_theme()
