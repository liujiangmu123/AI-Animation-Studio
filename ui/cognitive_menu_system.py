"""
AI Animation Studio - 认知菜单系统设计
基于用户心理模型的菜单分类和组织系统
"""

from PyQt6.QtWidgets import QMenuBar, QMenu, QAction, QWidget, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QPoint
from PyQt6.QtGui import QKeySequence, QIcon

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Callable
import json
from dataclasses import dataclass

from core.logger import get_logger

logger = get_logger("cognitive_menu_system")


class UserMentalModel(Enum):
    """用户心理模型枚举"""
    PROJECT_LIFECYCLE = "project_lifecycle"     # 项目生命周期模型
    CREATIVE_WORKFLOW = "creative_workflow"     # 创作工作流程模型
    CONTENT_MANAGEMENT = "content_management"   # 内容管理模型
    TOOL_OPERATION = "tool_operation"          # 工具操作模型
    HELP_SUPPORT = "help_support"              # 帮助支持模型


class MenuCategory(Enum):
    """菜单分类枚举"""
    PROJECT = "project"         # 项目管理
    CREATE = "create"          # 创作制作
    EDIT = "edit"              # 编辑修改
    VIEW = "view"              # 视图显示
    TOOLS = "tools"            # 工具设置
    HELP = "help"              # 帮助支持


class UserExpertiseLevel(Enum):
    """用户专业水平枚举"""
    BEGINNER = "beginner"       # 初学者
    INTERMEDIATE = "intermediate" # 中级用户
    ADVANCED = "advanced"       # 高级用户
    EXPERT = "expert"          # 专家用户


@dataclass
class CognitiveMenuItem:
    """认知菜单项定义"""
    action_id: str
    text: str
    description: str
    shortcut: str = None
    icon: str = None
    mental_model: UserMentalModel = UserMentalModel.TOOL_OPERATION
    expertise_level: UserExpertiseLevel = UserExpertiseLevel.BEGINNER
    frequency: int = 1  # 使用频率 1-5
    importance: int = 1  # 重要程度 1-5
    submenu: List['CognitiveMenuItem'] = None
    separator_after: bool = False
    enabled: bool = True
    visible: bool = True
    
    def __post_init__(self):
        if self.submenu is None:
            self.submenu = []


class CognitiveMenuStructure:
    """认知菜单结构"""
    
    def __init__(self):
        self.menu_structure = self.build_cognitive_menu_structure()
        logger.info("认知菜单结构初始化完成")
    
    def build_cognitive_menu_structure(self) -> Dict[MenuCategory, List[CognitiveMenuItem]]:
        """构建基于认知模型的菜单结构"""
        return {
            # 项目管理 - 基于项目生命周期心理模型
            MenuCategory.PROJECT: [
                CognitiveMenuItem(
                    "new_project", "新建项目(&N)", "创建新的动画项目",
                    "Ctrl+N", "new_project",
                    UserMentalModel.PROJECT_LIFECYCLE, UserExpertiseLevel.BEGINNER,
                    frequency=5, importance=5
                ),
                CognitiveMenuItem(
                    "new_from_template", "从模板新建(&T)", "使用模板快速创建项目",
                    "Ctrl+Shift+N", "template",
                    UserMentalModel.PROJECT_LIFECYCLE, UserExpertiseLevel.BEGINNER,
                    frequency=4, importance=4
                ),
                CognitiveMenuItem(
                    "open_project", "打开项目(&O)", "打开现有项目",
                    "Ctrl+O", "open",
                    UserMentalModel.PROJECT_LIFECYCLE, UserExpertiseLevel.BEGINNER,
                    frequency=5, importance=5
                ),
                CognitiveMenuItem(
                    "recent_projects", "最近项目(&R)", "快速访问最近使用的项目",
                    submenu=[
                        CognitiveMenuItem("recent_1", "项目1.aiae", ""),
                        CognitiveMenuItem("recent_2", "项目2.aiae", ""),
                        CognitiveMenuItem("recent_3", "项目3.aiae", ""),
                        CognitiveMenuItem("separator1", "", "", separator_after=True),
                        CognitiveMenuItem("clear_recent", "清除历史记录", "清除最近项目列表")
                    ],
                    mental_model=UserMentalModel.PROJECT_LIFECYCLE,
                    frequency=3, importance=3, separator_after=True
                ),
                CognitiveMenuItem(
                    "save_project", "保存项目(&S)", "保存当前项目",
                    "Ctrl+S", "save",
                    UserMentalModel.PROJECT_LIFECYCLE, UserExpertiseLevel.BEGINNER,
                    frequency=5, importance=5
                ),
                CognitiveMenuItem(
                    "save_as", "另存为(&A)", "将项目保存到新位置",
                    "Ctrl+Shift+S", "save_as",
                    UserMentalModel.PROJECT_LIFECYCLE, UserExpertiseLevel.BEGINNER,
                    frequency=3, importance=3
                ),
                CognitiveMenuItem(
                    "export", "导出作品(&E)", "导出动画作品",
                    submenu=[
                        CognitiveMenuItem("export_html", "导出HTML", "导出为HTML格式", "Ctrl+E"),
                        CognitiveMenuItem("export_video", "导出视频", "导出为视频格式", "Ctrl+Shift+E"),
                        CognitiveMenuItem("export_gif", "导出GIF", "导出为GIF动画"),
                        CognitiveMenuItem("separator2", "", "", separator_after=True),
                        CognitiveMenuItem("export_settings", "导出设置", "配置导出参数")
                    ],
                    mental_model=UserMentalModel.PROJECT_LIFECYCLE,
                    frequency=4, importance=4, separator_after=True
                ),
                CognitiveMenuItem(
                    "project_settings", "项目设置(&P)", "配置项目参数",
                    mental_model=UserMentalModel.PROJECT_LIFECYCLE,
                    expertise_level=UserExpertiseLevel.INTERMEDIATE,
                    frequency=2, importance=3
                )
            ],
            
            # 创作制作 - 基于创作工作流程心理模型
            MenuCategory.CREATE: [
                CognitiveMenuItem(
                    "import_audio", "导入音频(&A)", "导入音频文件作为动画基础",
                    "Ctrl+I", "audio_import",
                    UserMentalModel.CREATIVE_WORKFLOW, UserExpertiseLevel.BEGINNER,
                    frequency=5, importance=5
                ),
                CognitiveMenuItem(
                    "record_audio", "录制音频(&R)", "直接录制音频",
                    "Ctrl+R", "record",
                    UserMentalModel.CREATIVE_WORKFLOW, UserExpertiseLevel.INTERMEDIATE,
                    frequency=2, importance=3, separator_after=True
                ),
                CognitiveMenuItem(
                    "add_time_segment", "添加时间段(&T)", "在时间轴上添加新的时间段",
                    "Ctrl+T", "time_segment",
                    UserMentalModel.CREATIVE_WORKFLOW, UserExpertiseLevel.BEGINNER,
                    frequency=5, importance=5
                ),
                CognitiveMenuItem(
                    "describe_animation", "描述动画(&D)", "为时间段添加动画描述",
                    "Ctrl+D", "animation_desc",
                    UserMentalModel.CREATIVE_WORKFLOW, UserExpertiseLevel.BEGINNER,
                    frequency=5, importance=5
                ),
                CognitiveMenuItem(
                    "generate_animation", "生成动画(&G)", "使用AI生成动画代码",
                    "Ctrl+G", "ai_generation",
                    UserMentalModel.CREATIVE_WORKFLOW, UserExpertiseLevel.BEGINNER,
                    frequency=5, importance=5, separator_after=True
                ),
                CognitiveMenuItem(
                    "add_element", "添加元素(&E)", "手动添加动画元素",
                    submenu=[
                        CognitiveMenuItem("add_text", "添加文本", "添加文本元素"),
                        CognitiveMenuItem("add_shape", "添加图形", "添加几何图形"),
                        CognitiveMenuItem("add_image", "添加图片", "添加图片元素"),
                        CognitiveMenuItem("add_path", "添加路径", "添加运动路径")
                    ],
                    mental_model=UserMentalModel.CREATIVE_WORKFLOW,
                    expertise_level=UserExpertiseLevel.INTERMEDIATE,
                    frequency=3, importance=3
                ),
                CognitiveMenuItem(
                    "animation_templates", "动画模板(&M)", "使用预设动画模板",
                    mental_model=UserMentalModel.CREATIVE_WORKFLOW,
                    expertise_level=UserExpertiseLevel.BEGINNER,
                    frequency=3, importance=4
                )
            ],
            
            # 编辑修改 - 基于内容管理心理模型
            MenuCategory.EDIT: [
                CognitiveMenuItem(
                    "undo", "撤销(&U)", "撤销上一步操作",
                    "Ctrl+Z", "undo",
                    UserMentalModel.CONTENT_MANAGEMENT, UserExpertiseLevel.BEGINNER,
                    frequency=5, importance=5
                ),
                CognitiveMenuItem(
                    "redo", "重做(&R)", "重做已撤销的操作",
                    "Ctrl+Y", "redo",
                    UserMentalModel.CONTENT_MANAGEMENT, UserExpertiseLevel.BEGINNER,
                    frequency=4, importance=4, separator_after=True
                ),
                CognitiveMenuItem(
                    "cut", "剪切(&T)", "剪切选中内容",
                    "Ctrl+X", "cut",
                    UserMentalModel.CONTENT_MANAGEMENT, UserExpertiseLevel.BEGINNER,
                    frequency=3, importance=3
                ),
                CognitiveMenuItem(
                    "copy", "复制(&C)", "复制选中内容",
                    "Ctrl+C", "copy",
                    UserMentalModel.CONTENT_MANAGEMENT, UserExpertiseLevel.BEGINNER,
                    frequency=4, importance=4
                ),
                CognitiveMenuItem(
                    "paste", "粘贴(&P)", "粘贴剪贴板内容",
                    "Ctrl+V", "paste",
                    UserMentalModel.CONTENT_MANAGEMENT, UserExpertiseLevel.BEGINNER,
                    frequency=4, importance=4, separator_after=True
                ),
                CognitiveMenuItem(
                    "select_all", "全选(&A)", "选择所有内容",
                    "Ctrl+A", "select_all",
                    UserMentalModel.CONTENT_MANAGEMENT, UserExpertiseLevel.BEGINNER,
                    frequency=3, importance=3
                ),
                CognitiveMenuItem(
                    "find", "查找(&F)", "查找内容",
                    "Ctrl+F", "find",
                    UserMentalModel.CONTENT_MANAGEMENT, UserExpertiseLevel.INTERMEDIATE,
                    frequency=2, importance=3, separator_after=True
                ),
                CognitiveMenuItem(
                    "preferences", "首选项(&E)", "配置应用程序设置",
                    "Ctrl+,", "preferences",
                    UserMentalModel.CONTENT_MANAGEMENT, UserExpertiseLevel.INTERMEDIATE,
                    frequency=2, importance=3
                )
            ],
            
            # 视图显示 - 基于工具操作心理模型
            MenuCategory.VIEW: [
                CognitiveMenuItem(
                    "layout", "布局(&L)", "切换界面布局",
                    submenu=[
                        CognitiveMenuItem("layout_standard", "标准布局", "使用标准四象限布局"),
                        CognitiveMenuItem("layout_focus", "专注布局", "隐藏辅助面板"),
                        CognitiveMenuItem("layout_preview", "预览布局", "最大化预览区域"),
                        CognitiveMenuItem("separator3", "", "", separator_after=True),
                        CognitiveMenuItem("layout_custom", "自定义布局", "自定义面板布局")
                    ],
                    mental_model=UserMentalModel.TOOL_OPERATION,
                    frequency=3, importance=3
                ),
                CognitiveMenuItem(
                    "panels", "面板(&P)", "显示或隐藏面板",
                    submenu=[
                        CognitiveMenuItem("show_elements", "元素面板", "显示/隐藏元素面板"),
                        CognitiveMenuItem("show_properties", "属性面板", "显示/隐藏属性面板"),
                        CognitiveMenuItem("show_timeline", "时间轴面板", "显示/隐藏时间轴面板"),
                        CognitiveMenuItem("show_preview", "预览面板", "显示/隐藏预览面板")
                    ],
                    mental_model=UserMentalModel.TOOL_OPERATION,
                    frequency=3, importance=3, separator_after=True
                ),
                CognitiveMenuItem(
                    "zoom", "缩放(&Z)", "调整舞台缩放",
                    submenu=[
                        CognitiveMenuItem("zoom_in", "放大", "放大舞台视图", "Ctrl+="),
                        CognitiveMenuItem("zoom_out", "缩小", "缩小舞台视图", "Ctrl+-"),
                        CognitiveMenuItem("zoom_fit", "适合窗口", "适合窗口大小", "Ctrl+0"),
                        CognitiveMenuItem("zoom_100", "实际大小", "100%显示", "Ctrl+1")
                    ],
                    mental_model=UserMentalModel.TOOL_OPERATION,
                    frequency=3, importance=3
                ),
                CognitiveMenuItem(
                    "grid", "网格(&G)", "显示/隐藏网格",
                    "Ctrl+;", "grid",
                    UserMentalModel.TOOL_OPERATION, UserExpertiseLevel.INTERMEDIATE,
                    frequency=2, importance=2
                ),
                CognitiveMenuItem(
                    "rulers", "标尺(&R)", "显示/隐藏标尺",
                    "Ctrl+Shift+R", "rulers",
                    UserMentalModel.TOOL_OPERATION, UserExpertiseLevel.INTERMEDIATE,
                    frequency=2, importance=2, separator_after=True
                ),
                CognitiveMenuItem(
                    "fullscreen", "全屏(&F)", "切换全屏模式",
                    "F11", "fullscreen",
                    UserMentalModel.TOOL_OPERATION, UserExpertiseLevel.BEGINNER,
                    frequency=2, importance=3
                )
            ],
            
            # 工具设置 - 基于工具操作心理模型
            MenuCategory.TOOLS: [
                CognitiveMenuItem(
                    "ai_config", "AI配置(&A)", "配置AI生成参数",
                    mental_model=UserMentalModel.TOOL_OPERATION,
                    expertise_level=UserExpertiseLevel.INTERMEDIATE,
                    frequency=3, importance=4
                ),
                CognitiveMenuItem(
                    "library_manager", "库管理器(&L)", "管理JavaScript库",
                    mental_model=UserMentalModel.TOOL_OPERATION,
                    expertise_level=UserExpertiseLevel.ADVANCED,
                    frequency=2, importance=3
                ),
                CognitiveMenuItem(
                    "rule_editor", "规则编辑器(&R)", "编辑动画生成规则",
                    mental_model=UserMentalModel.TOOL_OPERATION,
                    expertise_level=UserExpertiseLevel.EXPERT,
                    frequency=1, importance=2, separator_after=True
                ),
                CognitiveMenuItem(
                    "export_settings", "导出设置(&E)", "配置导出参数",
                    mental_model=UserMentalModel.TOOL_OPERATION,
                    expertise_level=UserExpertiseLevel.INTERMEDIATE,
                    frequency=3, importance=3
                ),
                CognitiveMenuItem(
                    "performance", "性能设置(&P)", "优化性能参数",
                    mental_model=UserMentalModel.TOOL_OPERATION,
                    expertise_level=UserExpertiseLevel.ADVANCED,
                    frequency=1, importance=2, separator_after=True
                ),
                CognitiveMenuItem(
                    "customize", "自定义(&C)", "自定义界面和快捷键",
                    submenu=[
                        CognitiveMenuItem("customize_toolbar", "自定义工具栏", "配置工具栏"),
                        CognitiveMenuItem("customize_shortcuts", "自定义快捷键", "配置键盘快捷键"),
                        CognitiveMenuItem("customize_theme", "自定义主题", "配置界面主题")
                    ],
                    mental_model=UserMentalModel.TOOL_OPERATION,
                    expertise_level=UserExpertiseLevel.ADVANCED,
                    frequency=1, importance=2
                )
            ],
            
            # 帮助支持 - 基于帮助支持心理模型
            MenuCategory.HELP: [
                CognitiveMenuItem(
                    "quick_start", "快速入门(&Q)", "查看快速入门指南",
                    "F1", "help",
                    UserMentalModel.HELP_SUPPORT, UserExpertiseLevel.BEGINNER,
                    frequency=3, importance=4
                ),
                CognitiveMenuItem(
                    "user_guide", "用户手册(&U)", "查看完整用户手册",
                    mental_model=UserMentalModel.HELP_SUPPORT,
                    expertise_level=UserExpertiseLevel.BEGINNER,
                    frequency=2, importance=3
                ),
                CognitiveMenuItem(
                    "video_tutorials", "视频教程(&V)", "观看视频教程",
                    mental_model=UserMentalModel.HELP_SUPPORT,
                    expertise_level=UserExpertiseLevel.BEGINNER,
                    frequency=2, importance=3, separator_after=True
                ),
                CognitiveMenuItem(
                    "keyboard_shortcuts", "快捷键(&K)", "查看键盘快捷键",
                    mental_model=UserMentalModel.HELP_SUPPORT,
                    expertise_level=UserExpertiseLevel.INTERMEDIATE,
                    frequency=2, importance=3
                ),
                CognitiveMenuItem(
                    "tips_tricks", "技巧提示(&T)", "查看使用技巧",
                    mental_model=UserMentalModel.HELP_SUPPORT,
                    expertise_level=UserExpertiseLevel.INTERMEDIATE,
                    frequency=1, importance=2, separator_after=True
                ),
                CognitiveMenuItem(
                    "feedback", "问题反馈(&F)", "报告问题或建议",
                    mental_model=UserMentalModel.HELP_SUPPORT,
                    frequency=1, importance=3
                ),
                CognitiveMenuItem(
                    "check_updates", "检查更新(&C)", "检查软件更新",
                    mental_model=UserMentalModel.HELP_SUPPORT,
                    frequency=1, importance=2, separator_after=True
                ),
                CognitiveMenuItem(
                    "about", "关于(&A)", "查看软件信息",
                    mental_model=UserMentalModel.HELP_SUPPORT,
                    frequency=1, importance=1
                )
            ]
        }
    
    def get_menu_structure(self) -> Dict[MenuCategory, List[CognitiveMenuItem]]:
        """获取菜单结构"""
        return self.menu_structure
    
    def get_category_items(self, category: MenuCategory) -> List[CognitiveMenuItem]:
        """获取指定分类的菜单项"""
        return self.menu_structure.get(category, [])
    
    def filter_by_expertise_level(self, items: List[CognitiveMenuItem], 
                                 level: UserExpertiseLevel) -> List[CognitiveMenuItem]:
        """根据用户专业水平过滤菜单项"""
        level_values = {
            UserExpertiseLevel.BEGINNER: 1,
            UserExpertiseLevel.INTERMEDIATE: 2,
            UserExpertiseLevel.ADVANCED: 3,
            UserExpertiseLevel.EXPERT: 4
        }
        
        current_level = level_values.get(level, 1)
        filtered_items = []
        
        for item in items:
            item_level = level_values.get(item.expertise_level, 1)
            if current_level >= item_level and item.visible:
                # 递归过滤子菜单
                if item.submenu:
                    item.submenu = self.filter_by_expertise_level(item.submenu, level)
                filtered_items.append(item)
        
        return filtered_items
    
    def sort_by_importance_and_frequency(self, items: List[CognitiveMenuItem]) -> List[CognitiveMenuItem]:
        """根据重要性和使用频率排序菜单项"""
        return sorted(items, key=lambda x: (x.importance * 2 + x.frequency), reverse=True)


class CognitiveMenuManager(QObject):
    """认知菜单管理器"""

    menu_action_triggered = pyqtSignal(str)  # 菜单动作触发信号

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.menu_structure = CognitiveMenuStructure()
        self.current_expertise_level = UserExpertiseLevel.INTERMEDIATE
        self.menu_usage_stats = {}  # 菜单使用统计

        logger.info("认知菜单管理器初始化完成")

    def create_cognitive_menus(self, menubar: QMenuBar):
        """创建基于认知模型的菜单"""
        try:
            # 清空现有菜单
            menubar.clear()

            # 菜单分类和标题映射
            menu_titles = {
                MenuCategory.PROJECT: "项目(&P)",
                MenuCategory.CREATE: "创作(&C)",
                MenuCategory.EDIT: "编辑(&E)",
                MenuCategory.VIEW: "视图(&V)",
                MenuCategory.TOOLS: "工具(&T)",
                MenuCategory.HELP: "帮助(&H)"
            }

            # 创建各个菜单
            for category, title in menu_titles.items():
                menu = menubar.addMenu(title)
                menu_items = self.menu_structure.get_category_items(category)

                # 根据用户专业水平过滤菜单项
                filtered_items = self.menu_structure.filter_by_expertise_level(
                    menu_items, self.current_expertise_level
                )

                # 根据重要性和频率排序
                sorted_items = self.menu_structure.sort_by_importance_and_frequency(filtered_items)

                # 填充菜单
                self.populate_menu(menu, sorted_items)

            logger.info(f"认知菜单创建完成 - 专业水平: {self.current_expertise_level.value}")

        except Exception as e:
            logger.error(f"创建认知菜单失败: {e}")

    def populate_menu(self, menu: QMenu, items: List[CognitiveMenuItem]):
        """填充菜单项"""
        for item in items:
            if item.separator_after and menu.actions():
                menu.addSeparator()
                continue

            if not item.enabled or not item.visible:
                continue

            if item.submenu:
                # 创建子菜单
                submenu = menu.addMenu(item.text)
                submenu.setToolTip(item.description)
                self.populate_menu(submenu, item.submenu)
            else:
                # 创建普通菜单项
                action = menu.addAction(item.text)
                action.setToolTip(item.description)

                if item.shortcut:
                    action.setShortcut(QKeySequence(item.shortcut))

                # 连接信号
                action.triggered.connect(
                    lambda checked, aid=item.action_id: self.handle_menu_action(aid)
                )

            # 添加分隔符
            if item.separator_after:
                menu.addSeparator()

    def handle_menu_action(self, action_id: str):
        """处理菜单动作"""
        try:
            # 记录使用统计
            self.record_menu_usage(action_id)

            # 发送信号
            self.menu_action_triggered.emit(action_id)

            logger.debug(f"菜单动作触发: {action_id}")

        except Exception as e:
            logger.error(f"处理菜单动作失败 {action_id}: {e}")

    def record_menu_usage(self, action_id: str):
        """记录菜单使用统计"""
        if action_id not in self.menu_usage_stats:
            self.menu_usage_stats[action_id] = {
                'count': 0,
                'last_used': None
            }

        self.menu_usage_stats[action_id]['count'] += 1
        from datetime import datetime
        self.menu_usage_stats[action_id]['last_used'] = datetime.now()

    def update_expertise_level(self, level: UserExpertiseLevel):
        """更新用户专业水平"""
        if level != self.current_expertise_level:
            self.current_expertise_level = level
            # 需要重新创建菜单以反映新的专业水平
            if hasattr(self.main_window, 'menuBar'):
                self.create_cognitive_menus(self.main_window.menuBar())

            logger.info(f"用户专业水平更新为: {level.value}")

    def get_menu_usage_stats(self) -> Dict[str, Any]:
        """获取菜单使用统计"""
        return self.menu_usage_stats.copy()

    def get_recommended_actions(self, limit: int = 5) -> List[str]:
        """获取推荐的菜单动作"""
        # 根据使用频率推荐
        sorted_actions = sorted(
            self.menu_usage_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )

        return [action_id for action_id, _ in sorted_actions[:limit]]

    def adapt_menu_based_on_usage(self):
        """基于使用情况自适应调整菜单"""
        try:
            # 分析使用模式
            high_usage_actions = []
            low_usage_actions = []

            for action_id, stats in self.menu_usage_stats.items():
                if stats['count'] > 10:  # 高频使用
                    high_usage_actions.append(action_id)
                elif stats['count'] < 2:  # 低频使用
                    low_usage_actions.append(action_id)

            # 根据使用模式调整菜单结构
            # 这里可以实现动态菜单调整逻辑

            logger.info(f"菜单自适应调整: 高频{len(high_usage_actions)}项, 低频{len(low_usage_actions)}项")

        except Exception as e:
            logger.error(f"菜单自适应调整失败: {e}")


class MenuActionHandler:
    """菜单动作处理器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.action_handlers = self.setup_action_handlers()

        logger.info("菜单动作处理器初始化完成")

    def setup_action_handlers(self) -> Dict[str, Callable]:
        """设置动作处理器映射"""
        return {
            # 项目管理动作
            "new_project": lambda: self.main_window.new_project(),
            "new_from_template": lambda: self.main_window.new_project_from_template(),
            "open_project": lambda: self.main_window.open_project(),
            "save_project": lambda: self.main_window.save_project(),
            "save_as": lambda: self.main_window.save_project_as(),
            "export_html": lambda: self.main_window.export_html(),
            "export_video": lambda: self.main_window.export_video(),
            "export_gif": lambda: self.main_window.export_gif(),
            "project_settings": lambda: self.main_window.show_project_settings(),

            # 创作制作动作
            "import_audio": lambda: self.main_window.import_audio(),
            "record_audio": lambda: self.main_window.record_audio(),
            "add_time_segment": lambda: self.main_window.add_time_segment(),
            "describe_animation": lambda: self.main_window.describe_animation(),
            "generate_animation": lambda: self.main_window.generate_animation(),
            "add_text": lambda: self.main_window.add_text_element(),
            "add_shape": lambda: self.main_window.add_shape_element(),
            "add_image": lambda: self.main_window.add_image_element(),
            "add_path": lambda: self.main_window.add_path_element(),

            # 编辑修改动作
            "undo": lambda: self.main_window.undo(),
            "redo": lambda: self.main_window.redo(),
            "cut": lambda: self.main_window.cut(),
            "copy": lambda: self.main_window.copy(),
            "paste": lambda: self.main_window.paste(),
            "select_all": lambda: self.main_window.select_all(),
            "find": lambda: self.main_window.show_find_dialog(),
            "preferences": lambda: self.main_window.show_preferences(),

            # 视图显示动作
            "layout_standard": lambda: self.main_window.switch_to_standard_layout(),
            "layout_focus": lambda: self.main_window.switch_to_focus_layout(),
            "layout_preview": lambda: self.main_window.switch_to_preview_layout(),
            "zoom_in": lambda: self.main_window.zoom_in(),
            "zoom_out": lambda: self.main_window.zoom_out(),
            "zoom_fit": lambda: self.main_window.zoom_fit(),
            "zoom_100": lambda: self.main_window.zoom_100(),
            "fullscreen": lambda: self.main_window.toggle_fullscreen(),

            # 工具设置动作
            "ai_config": lambda: self.main_window.show_ai_config(),
            "library_manager": lambda: self.main_window.show_library_manager(),
            "rule_editor": lambda: self.main_window.show_rule_editor(),

            # 帮助支持动作
            "quick_start": lambda: self.main_window.show_quick_start(),
            "user_guide": lambda: self.main_window.show_user_guide(),
            "about": lambda: self.main_window.show_about()
        }

    def handle_action(self, action_id: str):
        """处理菜单动作"""
        try:
            if action_id in self.action_handlers:
                self.action_handlers[action_id]()
            else:
                logger.warning(f"未处理的菜单动作: {action_id}")

        except Exception as e:
            logger.error(f"处理菜单动作失败 {action_id}: {e}")


class CognitiveMenuIntegrator:
    """认知菜单集成器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.menu_manager = CognitiveMenuManager(main_window)
        self.action_handler = MenuActionHandler(main_window)

        # 连接信号
        self.menu_manager.menu_action_triggered.connect(
            self.action_handler.handle_action
        )

        logger.info("认知菜单集成器初始化完成")

    def integrate_cognitive_menu_system(self):
        """集成认知菜单系统"""
        try:
            # 创建认知菜单
            self.menu_manager.create_cognitive_menus(self.main_window.menuBar())

            # 设置用户专业水平（可以从配置文件读取）
            self.menu_manager.update_expertise_level(UserExpertiseLevel.INTERMEDIATE)

            logger.info("认知菜单系统集成完成")
            return True

        except Exception as e:
            logger.error(f"认知菜单系统集成失败: {e}")
            return False

    def get_menu_manager(self) -> CognitiveMenuManager:
        """获取菜单管理器"""
        return self.menu_manager

    def get_action_handler(self) -> MenuActionHandler:
        """获取动作处理器"""
        return self.action_handler

    def export_menu_configuration(self, file_path: str):
        """导出菜单配置"""
        try:
            config = {
                "expertise_level": self.menu_manager.current_expertise_level.value,
                "usage_stats": self.menu_manager.get_menu_usage_stats(),
                "menu_structure": "cognitive_menu_structure"
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"菜单配置已导出到: {file_path}")

        except Exception as e:
            logger.error(f"导出菜单配置失败: {e}")

    def get_integration_summary(self) -> Dict[str, Any]:
        """获取集成摘要"""
        return {
            "menu_categories": len(MenuCategory),
            "expertise_level": self.menu_manager.current_expertise_level.value,
            "total_actions": len(self.action_handler.action_handlers),
            "usage_stats": len(self.menu_manager.menu_usage_stats),
            "integration_status": "completed"
        }
