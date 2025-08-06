"""
AI Animation Studio - 专业工具栏管理器
实现符合专业软件标准的工具栏系统，支持自定义、分组、上下文敏感
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QToolBar,
                             QPushButton, QLabel, QFrame, QButtonGroup,
                             QMenu, QComboBox, QSpinBox,
                             QCheckBox, QSlider, QToolButton)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QIcon, QFont, QKeySequence, QPixmap, QPainter, QColor, QAction, QActionGroup

from core.value_hierarchy_config import get_value_hierarchy, UserExpertiseLevel, WorkflowStage
from core.logger import get_logger

logger = get_logger("professional_toolbar_manager")


class ToolbarAction:
    """工具栏动作定义"""
    
    def __init__(self, action_id: str, text: str, icon: str, tooltip: str,
                 shortcut: str = None, category: str = "general", 
                 priority: int = 5, expertise_level: UserExpertiseLevel = UserExpertiseLevel.BEGINNER):
        self.action_id = action_id
        self.text = text
        self.icon = icon
        self.tooltip = tooltip
        self.shortcut = shortcut
        self.category = category
        self.priority = priority
        self.expertise_level = expertise_level
        self.enabled = True
        self.visible = True


class ProfessionalToolbar(QToolBar):
    """专业工具栏组件"""
    
    action_triggered = pyqtSignal(str)  # 动作触发信号
    
    def __init__(self, name: str, category: str, parent=None):
        super().__init__(name, parent)
        self.category = category
        self.actions_map = {}
        self.setup_toolbar()
    
    def setup_toolbar(self):
        """设置工具栏"""
        self.setMovable(True)
        self.setFloatable(True)
        self.setIconSize(QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # 设置样式
        self.setStyleSheet("""
            QToolBar {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                spacing: 2px;
                padding: 4px;
            }
            QToolBar::separator {
                background-color: #dee2e6;
                width: 1px;
                margin: 2px 4px;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 4px;
                margin: 1px;
                font-size: 10px;
            }
            QToolButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            QToolButton:pressed {
                background-color: #dee2e6;
                border-color: #6c757d;
            }
            QToolButton:checked {
                background-color: #2C5AA0;
                color: white;
                border-color: #2C5AA0;
            }
        """)
    
    def add_toolbar_action(self, toolbar_action: ToolbarAction, callback=None):
        """添加工具栏动作"""
        action = QAction(toolbar_action.icon + " " + toolbar_action.text, self)
        action.setToolTip(toolbar_action.tooltip)
        
        if toolbar_action.shortcut:
            action.setShortcut(QKeySequence(toolbar_action.shortcut))
        
        if callback:
            action.triggered.connect(lambda: callback(toolbar_action.action_id))
        else:
            action.triggered.connect(lambda: self.action_triggered.emit(toolbar_action.action_id))
        
        action.setEnabled(toolbar_action.enabled)
        action.setVisible(toolbar_action.visible)
        
        self.addAction(action)
        self.actions_map[toolbar_action.action_id] = action
        
        return action
    
    def update_action_state(self, action_id: str, enabled: bool = None, visible: bool = None):
        """更新动作状态"""
        if action_id in self.actions_map:
            action = self.actions_map[action_id]
            if enabled is not None:
                action.setEnabled(enabled)
            if visible is not None:
                action.setVisible(visible)


class ProfessionalToolbarManager(QWidget):
    """专业工具栏管理器"""
    
    toolbar_action_triggered = pyqtSignal(str, str)  # 工具栏名称, 动作ID
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.toolbars = {}
        self.toolbar_actions = {}
        self.current_expertise_level = UserExpertiseLevel.INTERMEDIATE
        self.current_workflow_stage = WorkflowStage.AUDIO_IMPORT
        
        self.initialize_toolbar_actions()
        self.create_toolbars()
        logger.info("专业工具栏管理器初始化完成")
    
    def initialize_toolbar_actions(self):
        """初始化工具栏动作"""
        # 主工具栏动作
        main_actions = [
            ToolbarAction("new_project", "新建", "🆕", "新建项目 (Ctrl+N)", "Ctrl+N", "file", 10),
            ToolbarAction("open_project", "打开", "📂", "打开项目 (Ctrl+O)", "Ctrl+O", "file", 10),
            ToolbarAction("save_project", "保存", "💾", "保存项目 (Ctrl+S)", "Ctrl+S", "file", 10),
            ToolbarAction("import_audio", "导入音频", "🎵", "导入旁白音频文件", "Ctrl+I", "media", 9),
            ToolbarAction("ai_generate", "AI生成", "🤖", "使用AI生成动画", "Ctrl+G", "ai", 9),
            ToolbarAction("preview", "预览", "👁️", "预览动画效果", "Space", "preview", 9),
            ToolbarAction("export", "导出", "📤", "导出动画作品", "Ctrl+E", "export", 8)
        ]
        
        # 编辑工具栏动作
        edit_actions = [
            ToolbarAction("undo", "撤销", "↶", "撤销操作 (Ctrl+Z)", "Ctrl+Z", "edit", 10),
            ToolbarAction("redo", "重做", "↷", "重做操作 (Ctrl+Y)", "Ctrl+Y", "edit", 10),
            ToolbarAction("cut", "剪切", "✂️", "剪切选中内容 (Ctrl+X)", "Ctrl+X", "edit", 8),
            ToolbarAction("copy", "复制", "📋", "复制选中内容 (Ctrl+C)", "Ctrl+C", "edit", 8),
            ToolbarAction("paste", "粘贴", "📄", "粘贴内容 (Ctrl+V)", "Ctrl+V", "edit", 8),
            ToolbarAction("delete", "删除", "🗑️", "删除选中内容 (Delete)", "Delete", "edit", 7)
        ]
        
        # 舞台工具栏动作
        stage_actions = [
            ToolbarAction("select_tool", "选择", "👆", "选择工具 (V)", "V", "stage", 10),
            ToolbarAction("move_tool", "移动", "✋", "移动工具 (M)", "M", "stage", 9),
            ToolbarAction("path_tool", "路径", "📏", "路径工具 (P)", "P", "stage", 8, UserExpertiseLevel.INTERMEDIATE),
            ToolbarAction("text_tool", "文字", "📝", "文字工具 (T)", "T", "stage", 8),
            ToolbarAction("shape_tool", "形状", "🔷", "形状工具 (S)", "S", "stage", 7),
            ToolbarAction("add_element", "添加元素", "➕", "添加新元素", "Ctrl+Shift+A", "stage", 8)
        ]
        
        # 播放控制工具栏动作
        playback_actions = [
            ToolbarAction("play_pause", "播放/暂停", "⏯️", "播放或暂停动画", "Space", "playback", 10),
            ToolbarAction("stop", "停止", "⏹️", "停止播放", "Ctrl+.", "playback", 9),
            ToolbarAction("prev_frame", "上一帧", "⏮️", "跳到上一帧", "Left", "playback", 7),
            ToolbarAction("next_frame", "下一帧", "⏭️", "跳到下一帧", "Right", "playback", 7),
            ToolbarAction("goto_start", "跳到开始", "⏪", "跳到动画开始", "Home", "playback", 6),
            ToolbarAction("goto_end", "跳到结束", "⏩", "跳到动画结束", "End", "playback", 6)
        ]
        
        # AI工具栏动作
        ai_actions = [
            ToolbarAction("ai_describe", "描述动画", "📝", "输入动画描述", "Ctrl+D", "ai", 9),
            ToolbarAction("ai_optimize", "优化描述", "✨", "AI优化描述内容", "Ctrl+Shift+O", "ai", 8, UserExpertiseLevel.INTERMEDIATE),
            ToolbarAction("ai_generate_batch", "批量生成", "🔄", "批量生成多个方案", "Ctrl+Shift+G", "ai", 7, UserExpertiseLevel.ADVANCED),
            ToolbarAction("ai_settings", "AI设置", "⚙️", "AI生成参数设置", None, "ai", 6, UserExpertiseLevel.ADVANCED)
        ]
        
        # 视图工具栏动作
        view_actions = [
            ToolbarAction("zoom_in", "放大", "🔍+", "放大视图", "Ctrl+=", "view", 8),
            ToolbarAction("zoom_out", "缩小", "🔍-", "缩小视图", "Ctrl+-", "view", 8),
            ToolbarAction("zoom_fit", "适合窗口", "🎯", "适合窗口大小", "Ctrl+0", "view", 7),
            ToolbarAction("zoom_100", "实际大小", "💯", "100%显示", "Ctrl+1", "view", 6),
            ToolbarAction("toggle_grid", "网格", "📐", "显示/隐藏网格", "Ctrl+;", "view", 7),
            ToolbarAction("toggle_rulers", "标尺", "📏", "显示/隐藏标尺", "Ctrl+R", "view", 6, UserExpertiseLevel.INTERMEDIATE)
        ]
        
        # 存储所有动作
        self.toolbar_actions = {
            "main": main_actions,
            "edit": edit_actions,
            "stage": stage_actions,
            "playback": playback_actions,
            "ai": ai_actions,
            "view": view_actions
        }
    
    def create_toolbars(self):
        """创建工具栏"""
        toolbar_configs = [
            ("main", "主工具栏", True),
            ("edit", "编辑工具栏", True),
            ("stage", "舞台工具栏", True),
            ("playback", "播放控制", True),
            ("ai", "AI工具栏", True),
            ("view", "视图工具栏", False)  # 默认隐藏
        ]
        
        for toolbar_id, toolbar_name, visible in toolbar_configs:
            toolbar = ProfessionalToolbar(toolbar_name, toolbar_id, self.main_window)
            toolbar.action_triggered.connect(
                lambda action_id, tid=toolbar_id: self.toolbar_action_triggered.emit(tid, action_id)
            )
            
            # 添加动作到工具栏
            if toolbar_id in self.toolbar_actions:
                actions = self.toolbar_actions[toolbar_id]
                for i, action in enumerate(actions):
                    # 根据用户专业水平过滤动作
                    if self.should_show_action(action):
                        toolbar.add_toolbar_action(action, self.handle_toolbar_action)
                        
                        # 在某些位置添加分隔符
                        if self.should_add_separator(toolbar_id, i, actions):
                            toolbar.addSeparator()
            
            # 添加到主窗口
            self.main_window.addToolBar(toolbar)
            toolbar.setVisible(visible)
            self.toolbars[toolbar_id] = toolbar
    
    def should_show_action(self, action: ToolbarAction) -> bool:
        """判断是否应该显示动作"""
        # 根据用户专业水平判断
        expertise_levels = {
            UserExpertiseLevel.BEGINNER: 1,
            UserExpertiseLevel.INTERMEDIATE: 2,
            UserExpertiseLevel.ADVANCED: 3,
            UserExpertiseLevel.EXPERT: 4
        }
        
        current_level = expertise_levels.get(self.current_expertise_level, 2)
        required_level = expertise_levels.get(action.expertise_level, 1)
        
        return current_level >= required_level
    
    def should_add_separator(self, toolbar_id: str, index: int, actions: list) -> bool:
        """判断是否应该添加分隔符"""
        separator_positions = {
            "main": [2, 4],  # 在保存后和预览后添加分隔符
            "edit": [1, 3],  # 在重做后和复制后添加分隔符
            "stage": [1, 3], # 在移动后和文字后添加分隔符
            "playback": [1, 3], # 在停止后和下一帧后添加分隔符
            "ai": [1, 2],    # 在优化后和批量生成后添加分隔符
            "view": [3]      # 在实际大小后添加分隔符
        }
        
        return index in separator_positions.get(toolbar_id, [])
    
    def handle_toolbar_action(self, action_id: str):
        """处理工具栏动作"""
        try:
            # 根据动作ID执行相应的操作
            action_handlers = {
                # 文件操作
                "new_project": lambda: self.main_window.new_project(),
                "open_project": lambda: self.main_window.open_project(),
                "save_project": lambda: self.main_window.save_project(),
                
                # 编辑操作
                "undo": lambda: self.main_window.undo_command(),
                "redo": lambda: self.main_window.redo_command(),
                
                # 媒体操作
                "import_audio": lambda: self.main_window.import_audio(),
                
                # AI操作
                "ai_generate": lambda: self.main_window.generate_animation(),
                
                # 预览操作
                "preview": lambda: self.main_window.toggle_preview(),
                
                # 导出操作
                "export": lambda: self.main_window.export_html(),
                
                # 播放控制
                "play_pause": lambda: self.main_window.toggle_play(),
                "stop": lambda: self.main_window.stop_preview(),
            }
            
            if action_id in action_handlers:
                action_handlers[action_id]()
            else:
                logger.warning(f"未处理的工具栏动作: {action_id}")
                
        except Exception as e:
            logger.error(f"处理工具栏动作失败 {action_id}: {e}")
    
    def update_expertise_level(self, level: UserExpertiseLevel):
        """更新用户专业水平"""
        self.current_expertise_level = level
        self.refresh_toolbars()
    
    def update_workflow_stage(self, stage: WorkflowStage):
        """更新工作流程阶段"""
        self.current_workflow_stage = stage
        self.highlight_relevant_tools(stage)
    
    def refresh_toolbars(self):
        """刷新工具栏显示"""
        for toolbar_id, toolbar in self.toolbars.items():
            # 清空现有动作
            toolbar.clear()
            toolbar.actions_map.clear()
            
            # 重新添加动作
            if toolbar_id in self.toolbar_actions:
                actions = self.toolbar_actions[toolbar_id]
                for i, action in enumerate(actions):
                    if self.should_show_action(action):
                        toolbar.add_toolbar_action(action, self.handle_toolbar_action)
                        
                        if self.should_add_separator(toolbar_id, i, actions):
                            toolbar.addSeparator()
    
    def highlight_relevant_tools(self, stage: WorkflowStage):
        """高亮相关工具"""
        # 根据工作流程阶段高亮相关工具
        stage_tool_mapping = {
            WorkflowStage.AUDIO_IMPORT: ["import_audio", "open_project"],
            WorkflowStage.TIME_MARKING: ["play_pause", "stop", "prev_frame", "next_frame"],
            WorkflowStage.DESCRIPTION: ["ai_describe", "ai_optimize"],
            WorkflowStage.AI_GENERATION: ["ai_generate", "ai_generate_batch"],
            WorkflowStage.PREVIEW_ADJUST: ["preview", "play_pause", "zoom_fit"],
            WorkflowStage.EXPORT: ["export", "save_project"]
        }
        
        relevant_tools = stage_tool_mapping.get(stage, [])
        
        # 重置所有工具的高亮状态
        for toolbar in self.toolbars.values():
            for action in toolbar.actions():
                if hasattr(action, 'setChecked'):
                    action.setChecked(False)
        
        # 高亮相关工具
        for toolbar in self.toolbars.values():
            for action_id, action in toolbar.actions_map.items():
                if action_id in relevant_tools:
                    if hasattr(action, 'setChecked'):
                        action.setChecked(True)
    
    def toggle_toolbar_visibility(self, toolbar_id: str, visible: bool = None):
        """切换工具栏可见性"""
        if toolbar_id in self.toolbars:
            toolbar = self.toolbars[toolbar_id]
            if visible is None:
                visible = not toolbar.isVisible()
            toolbar.setVisible(visible)
    
    def get_toolbar_summary(self) -> dict:
        """获取工具栏摘要"""
        return {
            'total_toolbars': len(self.toolbars),
            'visible_toolbars': len([t for t in self.toolbars.values() if t.isVisible()]),
            'total_actions': sum(len(actions) for actions in self.toolbar_actions.values()),
            'visible_actions': sum(
                len([a for a in actions if self.should_show_action(a)]) 
                for actions in self.toolbar_actions.values()
            ),
            'current_expertise_level': self.current_expertise_level.value,
            'current_workflow_stage': self.current_workflow_stage.name
        }


class MenuAction:
    """菜单动作定义"""

    def __init__(self, action_id: str, text: str, tooltip: str = "",
                 shortcut: str = None, icon: str = None, checkable: bool = False,
                 separator_after: bool = False, submenu: list = None,
                 expertise_level: UserExpertiseLevel = UserExpertiseLevel.BEGINNER):
        self.action_id = action_id
        self.text = text
        self.tooltip = tooltip
        self.shortcut = shortcut
        self.icon = icon
        self.checkable = checkable
        self.separator_after = separator_after
        self.submenu = submenu or []
        self.expertise_level = expertise_level
        self.enabled = True
        self.visible = True


class ContextMenuManager:
    """上下文菜单管理器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.context_menus = {}
        self.initialize_context_menus()
        logger.info("上下文菜单管理器初始化完成")

    def initialize_context_menus(self):
        """初始化上下文菜单"""
        # 音频片段上下文菜单
        self.context_menus['audio_segment'] = [
            MenuAction("edit_segment", "编辑时间段", "编辑选中的时间段"),
            MenuAction("split_segment", "分割时间段", "在当前位置分割时间段"),
            MenuAction("delete_segment", "删除时间段", "删除选中的时间段"),
            MenuAction("separator1", "", separator_after=True),
            MenuAction("segment_properties", "时间段属性", "查看和编辑时间段属性")
        ]

        # 舞台元素上下文菜单
        self.context_menus['stage_element'] = [
            MenuAction("edit_element", "编辑元素", "编辑选中的元素"),
            MenuAction("duplicate_element", "复制元素", "复制选中的元素", "Ctrl+D"),
            MenuAction("delete_element", "删除元素", "删除选中的元素", "Delete"),
            MenuAction("separator1", "", separator_after=True),
            MenuAction("bring_to_front", "置于顶层", "将元素移到最前面"),
            MenuAction("send_to_back", "置于底层", "将元素移到最后面"),
            MenuAction("separator2", "", separator_after=True),
            MenuAction("element_properties", "元素属性", "查看和编辑元素属性")
        ]

        # 时间轴上下文菜单
        self.context_menus['timeline'] = [
            MenuAction("add_keyframe", "添加关键帧", "在当前位置添加关键帧"),
            MenuAction("delete_keyframe", "删除关键帧", "删除选中的关键帧"),
            MenuAction("separator1", "", separator_after=True),
            MenuAction("zoom_to_fit", "缩放适合", "缩放时间轴以适合内容"),
            MenuAction("zoom_selection", "缩放选区", "缩放到选中的时间范围"),
            MenuAction("separator2", "", separator_after=True),
            MenuAction("timeline_properties", "时间轴属性", "时间轴设置和属性")
        ]

    def show_context_menu(self, menu_type: str, position: QPoint, context: dict = None):
        """显示上下文菜单"""
        if menu_type not in self.context_menus:
            logger.warning(f"未知的上下文菜单类型: {menu_type}")
            return

        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self.main_window)

        for menu_action in self.context_menus[menu_type]:
            if menu_action.action_id.startswith("separator"):
                menu.addSeparator()
                continue

            action = menu.addAction(menu_action.text)
            action.setToolTip(menu_action.tooltip)

            if menu_action.shortcut:
                action.setShortcut(QKeySequence(menu_action.shortcut))

            if menu_action.checkable:
                action.setCheckable(True)

            # 连接信号
            action.triggered.connect(
                lambda checked, aid=menu_action.action_id: self.handle_context_action(aid, context)
            )

        menu.exec(position)

    def handle_context_action(self, action_id: str, context: dict = None):
        """处理上下文菜单动作"""
        try:
            logger.info(f"执行上下文菜单动作: {action_id}")

            # 根据动作ID执行相应操作
            context_handlers = {
                # 音频片段操作
                "edit_segment": lambda: self.edit_audio_segment(context),
                "split_segment": lambda: self.split_audio_segment(context),
                "delete_segment": lambda: self.delete_audio_segment(context),

                # 舞台元素操作
                "edit_element": lambda: self.edit_stage_element(context),
                "duplicate_element": lambda: self.duplicate_stage_element(context),
                "delete_element": lambda: self.delete_stage_element(context),
                "bring_to_front": lambda: self.bring_element_to_front(context),
                "send_to_back": lambda: self.send_element_to_back(context),

                # 时间轴操作
                "add_keyframe": lambda: self.add_keyframe(context),
                "delete_keyframe": lambda: self.delete_keyframe(context),
                "zoom_to_fit": lambda: self.zoom_timeline_to_fit(),
                "zoom_selection": lambda: self.zoom_timeline_selection(context),
            }

            if action_id in context_handlers:
                context_handlers[action_id]()
            else:
                logger.warning(f"未处理的上下文菜单动作: {action_id}")

        except Exception as e:
            logger.error(f"处理上下文菜单动作失败 {action_id}: {e}")

    def edit_audio_segment(self, context):
        """编辑音频片段"""
        logger.info("编辑音频片段")

    def split_audio_segment(self, context):
        """分割音频片段"""
        logger.info("分割音频片段")

    def delete_audio_segment(self, context):
        """删除音频片段"""
        logger.info("删除音频片段")

    def edit_stage_element(self, context):
        """编辑舞台元素"""
        logger.info("编辑舞台元素")

    def duplicate_stage_element(self, context):
        """复制舞台元素"""
        logger.info("复制舞台元素")

    def delete_stage_element(self, context):
        """删除舞台元素"""
        logger.info("删除舞台元素")

    def bring_element_to_front(self, context):
        """将元素置于顶层"""
        logger.info("将元素置于顶层")

    def send_element_to_back(self, context):
        """将元素置于底层"""
        logger.info("将元素置于底层")

    def add_keyframe(self, context):
        """添加关键帧"""
        logger.info("添加关键帧")

    def delete_keyframe(self, context):
        """删除关键帧"""
        logger.info("删除关键帧")

    def zoom_timeline_to_fit(self):
        """缩放时间轴适合内容"""
        logger.info("缩放时间轴适合内容")

    def zoom_timeline_selection(self, context):
        """缩放时间轴选区"""
        logger.info("缩放时间轴选区")


class ProfessionalMenuManager:
    """专业菜单管理器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.menu_actions = {}
        self.context_menu_manager = ContextMenuManager(main_window)
        self.current_expertise_level = UserExpertiseLevel.INTERMEDIATE

        self.initialize_menu_structure()
        logger.info("专业菜单管理器初始化完成")

    def initialize_menu_structure(self):
        """初始化菜单结构"""
        # 重新设计的菜单结构，符合用户心理模型
        self.menu_actions = {
            "project": [
                MenuAction("new_project", "新建项目(&N)", "创建新的动画项目", "Ctrl+N"),
                MenuAction("open_project", "打开项目(&O)", "打开现有项目", "Ctrl+O"),
                MenuAction("open_recent", "最近项目(&R)", "打开最近使用的项目", submenu=[
                    MenuAction("recent_1", "项目1.aiae", ""),
                    MenuAction("recent_2", "项目2.aiae", ""),
                    MenuAction("recent_3", "项目3.aiae", "")
                ]),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("save_project", "保存项目(&S)", "保存当前项目", "Ctrl+S"),
                MenuAction("save_as", "另存为(&A)", "将项目保存到新位置", "Ctrl+Shift+S"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("import_audio", "导入音频(&I)", "导入旁白音频文件", "Ctrl+I"),
                MenuAction("import_assets", "导入素材(&M)", "导入图片、视频等素材"),
                MenuAction("separator3", "", separator_after=True),
                MenuAction("export_video", "导出视频(&V)", "导出为视频文件", "Ctrl+E"),
                MenuAction("export_html", "导出HTML(&H)", "导出为HTML5动画"),
                MenuAction("export_gif", "导出GIF(&G)", "导出为GIF动画"),
                MenuAction("separator4", "", separator_after=True),
                MenuAction("project_settings", "项目设置(&P)", "项目配置和设置"),
                MenuAction("separator5", "", separator_after=True),
                MenuAction("exit", "退出(&X)", "退出应用程序", "Ctrl+Q")
            ],

            "edit": [
                MenuAction("undo", "撤销(&U)", "撤销上一个操作", "Ctrl+Z"),
                MenuAction("redo", "重做(&R)", "重做上一个操作", "Ctrl+Y"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("cut", "剪切(&T)", "剪切选中内容", "Ctrl+X"),
                MenuAction("copy", "复制(&C)", "复制选中内容", "Ctrl+C"),
                MenuAction("paste", "粘贴(&P)", "粘贴内容", "Ctrl+V"),
                MenuAction("delete", "删除(&D)", "删除选中内容", "Delete"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("select_all", "全选(&A)", "选择所有内容", "Ctrl+A"),
                MenuAction("deselect_all", "取消选择(&N)", "取消所有选择", "Ctrl+Shift+A"),
                MenuAction("separator3", "", separator_after=True),
                MenuAction("find", "查找(&F)", "查找内容", "Ctrl+F", expertise_level=UserExpertiseLevel.INTERMEDIATE),
                MenuAction("replace", "替换(&H)", "查找并替换", "Ctrl+H", expertise_level=UserExpertiseLevel.INTERMEDIATE)
            ],

            "create": [
                MenuAction("ai_describe", "描述动画(&D)", "输入动画描述", "Ctrl+D"),
                MenuAction("ai_generate", "生成动画(&G)", "使用AI生成动画", "Ctrl+G"),
                MenuAction("ai_optimize", "优化描述(&O)", "AI优化描述内容", "Ctrl+Shift+O", expertise_level=UserExpertiseLevel.INTERMEDIATE),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("add_element", "添加元素(&E)", "添加新的动画元素", "Ctrl+Shift+A"),
                MenuAction("add_text", "添加文字(&T)", "添加文字元素", "T"),
                MenuAction("add_shape", "添加形状(&S)", "添加几何形状", "S"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("batch_generate", "批量生成(&B)", "批量生成多个方案", "Ctrl+Shift+G", expertise_level=UserExpertiseLevel.ADVANCED),
                MenuAction("ai_settings", "AI设置(&A)", "AI生成参数设置", expertise_level=UserExpertiseLevel.ADVANCED)
            ],

            "view": [
                MenuAction("zoom_in", "放大(&I)", "放大视图", "Ctrl+="),
                MenuAction("zoom_out", "缩小(&O)", "缩小视图", "Ctrl+-"),
                MenuAction("zoom_fit", "适合窗口(&F)", "适合窗口大小", "Ctrl+0"),
                MenuAction("zoom_100", "实际大小(&1)", "100%显示", "Ctrl+1"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("show_grid", "显示网格(&G)", "显示/隐藏网格", "Ctrl+;", checkable=True),
                MenuAction("show_rulers", "显示标尺(&R)", "显示/隐藏标尺", "Ctrl+R", checkable=True, expertise_level=UserExpertiseLevel.INTERMEDIATE),
                MenuAction("show_guides", "显示参考线(&U)", "显示/隐藏参考线", checkable=True, expertise_level=UserExpertiseLevel.INTERMEDIATE),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("fullscreen", "全屏模式(&F)", "切换全屏模式", "F11"),
                MenuAction("separator3", "", separator_after=True),
                MenuAction("layout_standard", "标准布局", "切换到标准布局", checkable=True),
                MenuAction("layout_quadrant", "四象限布局", "切换到四象限布局", checkable=True),
                MenuAction("layout_hierarchy", "价值层次布局", "切换到价值层次布局", checkable=True),
                MenuAction("separator4", "", separator_after=True),
                MenuAction("theme_light", "浅色主题", "切换到浅色主题", checkable=True),
                MenuAction("theme_dark", "深色主题", "切换到深色主题", checkable=True)
            ],

            "tools": [
                MenuAction("preferences", "首选项(&P)", "应用程序设置", "Ctrl+,"),
                MenuAction("customize_toolbar", "自定义工具栏(&T)", "自定义工具栏布局", expertise_level=UserExpertiseLevel.INTERMEDIATE),
                MenuAction("customize_shortcuts", "自定义快捷键(&K)", "自定义键盘快捷键", expertise_level=UserExpertiseLevel.INTERMEDIATE),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("performance_monitor", "性能监控(&M)", "查看性能监控信息", expertise_level=UserExpertiseLevel.EXPERT),
                MenuAction("debug_console", "调试控制台(&D)", "打开调试控制台", "F12", expertise_level=UserExpertiseLevel.EXPERT),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("reset_workspace", "重置工作区(&R)", "重置到默认工作区布局"),
                MenuAction("backup_settings", "备份设置(&B)", "备份当前设置", expertise_level=UserExpertiseLevel.ADVANCED)
            ],

            "help": [
                MenuAction("user_guide", "用户指南(&G)", "打开用户指南", "F1"),
                MenuAction("video_tutorials", "视频教程(&V)", "观看视频教程"),
                MenuAction("keyboard_shortcuts", "快捷键参考(&K)", "查看所有快捷键"),
                MenuAction("separator1", "", separator_after=True),
                MenuAction("check_updates", "检查更新(&U)", "检查软件更新"),
                MenuAction("report_bug", "报告问题(&R)", "报告软件问题"),
                MenuAction("separator2", "", separator_after=True),
                MenuAction("about", "关于(&A)", "关于AI Animation Studio")
            ]
        }

    def create_menus(self, menubar):
        """创建菜单"""
        menu_configs = [
            ("project", "项目(&P)"),
            ("edit", "编辑(&E)"),
            ("create", "创作(&C)"),
            ("view", "视图(&V)"),
            ("tools", "工具(&T)"),
            ("help", "帮助(&H)")
        ]

        for menu_id, menu_title in menu_configs:
            menu = menubar.addMenu(menu_title)

            if menu_id in self.menu_actions:
                self.populate_menu(menu, self.menu_actions[menu_id])

    def populate_menu(self, menu, menu_actions):
        """填充菜单"""
        for menu_action in menu_actions:
            if menu_action.action_id.startswith("separator"):
                menu.addSeparator()
                continue

            # 根据用户专业水平过滤菜单项
            if not self.should_show_menu_action(menu_action):
                continue

            if menu_action.submenu:
                # 创建子菜单
                submenu = menu.addMenu(menu_action.text)
                self.populate_menu(submenu, menu_action.submenu)
            else:
                # 创建普通菜单项
                action = menu.addAction(menu_action.text)
                action.setToolTip(menu_action.tooltip)

                if menu_action.shortcut:
                    action.setShortcut(QKeySequence(menu_action.shortcut))

                if menu_action.checkable:
                    action.setCheckable(True)

                # 连接信号
                action.triggered.connect(
                    lambda checked, aid=menu_action.action_id: self.handle_menu_action(aid)
                )

    def should_show_menu_action(self, menu_action: MenuAction) -> bool:
        """判断是否应该显示菜单项"""
        expertise_levels = {
            UserExpertiseLevel.BEGINNER: 1,
            UserExpertiseLevel.INTERMEDIATE: 2,
            UserExpertiseLevel.ADVANCED: 3,
            UserExpertiseLevel.EXPERT: 4
        }

        current_level = expertise_levels.get(self.current_expertise_level, 2)
        required_level = expertise_levels.get(menu_action.expertise_level, 1)

        return current_level >= required_level

    def handle_menu_action(self, action_id: str):
        """处理菜单动作"""
        try:
            logger.info(f"执行菜单动作: {action_id}")

            # 菜单动作处理器映射
            menu_handlers = {
                # 项目菜单
                "new_project": lambda: self.main_window.new_project(),
                "open_project": lambda: self.main_window.open_project(),
                "save_project": lambda: self.main_window.save_project(),
                "save_as": lambda: self.main_window.save_project_as(),
                "import_audio": lambda: self.main_window.import_audio(),
                "export_video": lambda: self.main_window.export_video(),
                "export_html": lambda: self.main_window.export_html(),
                "exit": lambda: self.main_window.close(),

                # 编辑菜单
                "undo": lambda: self.main_window.undo_command(),
                "redo": lambda: self.main_window.redo_command(),

                # 创作菜单
                "ai_generate": lambda: self.main_window.generate_animation(),

                # 视图菜单
                "layout_standard": lambda: self.main_window.switch_to_standard_layout(),
                "layout_quadrant": lambda: self.main_window.switch_to_quadrant_layout(),
                "layout_hierarchy": lambda: self.main_window.switch_to_hierarchy_layout(),

                # 帮助菜单
                "about": lambda: self.main_window.show_about(),
            }

            if action_id in menu_handlers:
                menu_handlers[action_id]()
            else:
                logger.warning(f"未处理的菜单动作: {action_id}")

        except Exception as e:
            logger.error(f"处理菜单动作失败 {action_id}: {e}")

    def update_expertise_level(self, level: UserExpertiseLevel):
        """更新用户专业水平"""
        self.current_expertise_level = level
        # 需要重新创建菜单以反映新的专业水平
        logger.info(f"菜单系统专业水平更新为: {level.value}")

    def get_context_menu_manager(self) -> ContextMenuManager:
        """获取上下文菜单管理器"""
        return self.context_menu_manager
