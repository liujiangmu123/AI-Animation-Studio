"""
AI Animation Studio - 自适应界面管理器
根据用户专业水平动态调整界面复杂度和功能可见性
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QTabWidget, QMenuBar,
                             QToolBar, QStatusBar, QSplitter, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QAction

from core.value_hierarchy_config import get_value_hierarchy, UserExpertiseLevel, PriorityLevel
from core.logger import get_logger

logger = get_logger("adaptive_interface_manager")


class InterfaceComplexityLevel:
    """界面复杂度级别定义"""
    
    MINIMAL = "minimal"      # 最简界面
    BASIC = "basic"          # 基础界面
    STANDARD = "standard"    # 标准界面
    ADVANCED = "advanced"    # 高级界面
    EXPERT = "expert"        # 专家界面


class AdaptiveInterfaceManager:
    """自适应界面管理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_level = UserExpertiseLevel.INTERMEDIATE
        self.complexity_level = InterfaceComplexityLevel.STANDARD
        self.adaptive_elements = {}
        self.animation_duration = 300
        
        # 界面适配规则
        self.adaptation_rules = self._initialize_adaptation_rules()
        
        logger.info("自适应界面管理器初始化完成")
    
    def _initialize_adaptation_rules(self) -> dict:
        """初始化界面适配规则"""
        return {
            UserExpertiseLevel.BEGINNER: {
                'complexity': InterfaceComplexityLevel.BASIC,
                'visible_tabs': ['🎨 舞台', '🤖 AI生成器', '👁️ 预览'],
                'hidden_menus': ['开发者', '调试', '高级'],
                'simplified_toolbars': True,
                'show_tooltips': True,
                'show_shortcuts': False,
                'panel_layout': 'simplified',
                'max_tabs': 3
            },
            UserExpertiseLevel.INTERMEDIATE: {
                'complexity': InterfaceComplexityLevel.STANDARD,
                'visible_tabs': ['🎨 舞台', '⏱️ 时间轴', '🤖 AI生成器', '👁️ 预览'],
                'hidden_menus': ['调试'],
                'simplified_toolbars': False,
                'show_tooltips': True,
                'show_shortcuts': True,
                'panel_layout': 'standard',
                'max_tabs': 6
            },
            UserExpertiseLevel.ADVANCED: {
                'complexity': InterfaceComplexityLevel.ADVANCED,
                'visible_tabs': 'all',
                'hidden_menus': [],
                'simplified_toolbars': False,
                'show_tooltips': True,
                'show_shortcuts': True,
                'panel_layout': 'advanced',
                'max_tabs': 10
            },
            UserExpertiseLevel.EXPERT: {
                'complexity': InterfaceComplexityLevel.EXPERT,
                'visible_tabs': 'all',
                'hidden_menus': [],
                'simplified_toolbars': False,
                'show_tooltips': False,  # 专家不需要提示
                'show_shortcuts': True,
                'panel_layout': 'expert',
                'max_tabs': -1  # 无限制
            }
        }
    
    def adapt_interface(self, level: UserExpertiseLevel):
        """适配界面到指定用户级别"""
        try:
            self.current_level = level
            rules = self.adaptation_rules.get(level, {})
            self.complexity_level = rules.get('complexity', InterfaceComplexityLevel.STANDARD)
            
            # 执行各种适配操作
            self._adapt_tabs(rules)
            self._adapt_menus(rules)
            self._adapt_toolbars(rules)
            self._adapt_panels(rules)
            self._adapt_tooltips(rules)
            self._adapt_shortcuts(rules)
            
            logger.info(f"界面已适配到用户级别: {level.value}")
            
        except Exception as e:
            logger.error(f"界面适配失败: {e}")
    
    def _adapt_tabs(self, rules: dict):
        """适配选项卡显示"""
        try:
            visible_tabs = rules.get('visible_tabs', 'all')
            max_tabs = rules.get('max_tabs', -1)
            
            # 获取中央选项卡组件
            center_tabs = getattr(self.main_window, 'center_tabs', None)
            if not center_tabs:
                return
            
            # 如果是特定列表，只显示指定的选项卡
            if isinstance(visible_tabs, list):
                for i in range(center_tabs.count()):
                    tab_text = center_tabs.tabText(i)
                    should_show = any(visible_tab in tab_text for visible_tab in visible_tabs)
                    center_tabs.setTabVisible(i, should_show)
            
            # 限制最大选项卡数量
            if max_tabs > 0:
                for i in range(max_tabs, center_tabs.count()):
                    center_tabs.setTabVisible(i, False)
            
        except Exception as e:
            logger.error(f"适配选项卡失败: {e}")
    
    def _adapt_menus(self, rules: dict):
        """适配菜单显示"""
        try:
            hidden_menus = rules.get('hidden_menus', [])
            
            menubar = self.main_window.menuBar()
            if not menubar:
                return
            
            # 隐藏指定的菜单
            for action in menubar.actions():
                menu_text = action.text().replace('&', '')
                should_hide = any(hidden_menu in menu_text for hidden_menu in hidden_menus)
                action.setVisible(not should_hide)
            
        except Exception as e:
            logger.error(f"适配菜单失败: {e}")
    
    def _adapt_toolbars(self, rules: dict):
        """适配工具栏显示"""
        try:
            simplified = rules.get('simplified_toolbars', False)
            
            # 获取所有工具栏
            toolbars = self.main_window.findChildren(QToolBar)
            
            for toolbar in toolbars:
                if simplified:
                    # 简化模式：只显示核心工具
                    self._simplify_toolbar(toolbar)
                else:
                    # 标准模式：显示所有工具
                    self._restore_toolbar(toolbar)
            
        except Exception as e:
            logger.error(f"适配工具栏失败: {e}")
    
    def _simplify_toolbar(self, toolbar: QToolBar):
        """简化工具栏"""
        try:
            # 定义核心工具关键词
            core_tools = ['新建', '打开', '保存', '播放', '暂停', '预览']
            
            for action in toolbar.actions():
                if action.isSeparator():
                    continue
                
                action_text = action.text().replace('&', '')
                is_core = any(core_tool in action_text for core_tool in core_tools)
                action.setVisible(is_core)
            
        except Exception as e:
            logger.error(f"简化工具栏失败: {e}")
    
    def _restore_toolbar(self, toolbar: QToolBar):
        """恢复工具栏"""
        try:
            for action in toolbar.actions():
                action.setVisible(True)
        except Exception as e:
            logger.error(f"恢复工具栏失败: {e}")
    
    def _adapt_panels(self, rules: dict):
        """适配面板布局"""
        try:
            layout = rules.get('panel_layout', 'standard')
            
            # 获取主分割器
            main_splitter = getattr(self.main_window, 'main_splitter', None)
            if not main_splitter:
                return
            
            # 根据布局类型调整分割器比例
            if layout == 'simplified':
                # 简化布局：突出中央区域
                main_splitter.setSizes([200, 1000, 200])
            elif layout == 'standard':
                # 标准布局：平衡分配
                main_splitter.setSizes([300, 800, 300])
            elif layout == 'advanced':
                # 高级布局：更多侧边栏空间
                main_splitter.setSizes([350, 700, 350])
            elif layout == 'expert':
                # 专家布局：最大化工作区域
                main_splitter.setSizes([400, 600, 400])
            
        except Exception as e:
            logger.error(f"适配面板布局失败: {e}")
    
    def _adapt_tooltips(self, rules: dict):
        """适配工具提示显示"""
        try:
            show_tooltips = rules.get('show_tooltips', True)
            
            # 递归设置所有子组件的工具提示
            self._set_tooltips_recursive(self.main_window, show_tooltips)
            
        except Exception as e:
            logger.error(f"适配工具提示失败: {e}")
    
    def _set_tooltips_recursive(self, widget: QWidget, enabled: bool):
        """递归设置工具提示"""
        try:
            # 如果禁用工具提示，清空现有提示
            if not enabled and widget.toolTip():
                widget.setToolTip("")
            
            # 递归处理子组件
            for child in widget.findChildren(QWidget):
                if not enabled and child.toolTip():
                    child.setToolTip("")
            
        except Exception as e:
            logger.error(f"递归设置工具提示失败: {e}")
    
    def _adapt_shortcuts(self, rules: dict):
        """适配快捷键显示"""
        try:
            show_shortcuts = rules.get('show_shortcuts', True)
            
            # 获取所有动作
            actions = self.main_window.findChildren(QAction)
            
            for action in actions:
                if not show_shortcuts:
                    # 隐藏快捷键（但保持功能）
                    original_text = action.text()
                    if '\t' in original_text:
                        action.setText(original_text.split('\t')[0])
                
        except Exception as e:
            logger.error(f"适配快捷键显示失败: {e}")
    
    def get_current_complexity(self) -> str:
        """获取当前复杂度级别"""
        return self.complexity_level
    
    def get_adaptation_summary(self) -> dict:
        """获取适配摘要"""
        try:
            rules = self.adaptation_rules.get(self.current_level, {})
            
            return {
                'user_level': self.current_level.value,
                'complexity_level': self.complexity_level,
                'visible_tabs': rules.get('visible_tabs', 'all'),
                'hidden_menus': rules.get('hidden_menus', []),
                'simplified_toolbars': rules.get('simplified_toolbars', False),
                'show_tooltips': rules.get('show_tooltips', True),
                'show_shortcuts': rules.get('show_shortcuts', True),
                'panel_layout': rules.get('panel_layout', 'standard'),
                'max_tabs': rules.get('max_tabs', -1)
            }
            
        except Exception as e:
            logger.error(f"获取适配摘要失败: {e}")
            return {}
    
    def animate_adaptation(self, target_widget: QWidget, property_name: str, 
                          start_value, end_value):
        """界面适配动画"""
        try:
            animation = QPropertyAnimation(target_widget, property_name.encode())
            animation.setDuration(self.animation_duration)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            animation.setStartValue(start_value)
            animation.setEndValue(end_value)
            animation.start()
            
            # 保存动画引用防止被垃圾回收
            if not hasattr(self, 'animations'):
                self.animations = []
            self.animations.append(animation)
            
        except Exception as e:
            logger.error(f"界面适配动画失败: {e}")
    
    def reset_to_default(self):
        """重置到默认界面"""
        try:
            self.adapt_interface(UserExpertiseLevel.INTERMEDIATE)
            logger.info("界面已重置到默认状态")
        except Exception as e:
            logger.error(f"重置界面失败: {e}")
    
    def export_current_state(self) -> dict:
        """导出当前界面状态"""
        try:
            return {
                'timestamp': QTimer().remainingTime(),
                'user_level': self.current_level.value,
                'complexity_level': self.complexity_level,
                'adaptation_summary': self.get_adaptation_summary()
            }
        except Exception as e:
            logger.error(f"导出界面状态失败: {e}")
            return {}
