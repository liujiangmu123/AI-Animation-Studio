"""
AI Animation Studio - 响应式布局管理器
实现自适应窗口大小、分辨率和屏幕适配的响应式布局系统
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QFrame, QLabel, QScrollArea, QTabWidget,
                             QStackedWidget, QGroupBox, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QRect, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QScreen, QResizeEvent

from core.logger import get_logger
from core.value_hierarchy_config import UserExpertiseLevel

logger = get_logger("responsive_layout_manager")


class ScreenSize:
    """屏幕尺寸定义"""
    
    # 断点定义（宽度）
    MOBILE = 768
    TABLET = 1024
    DESKTOP = 1440
    LARGE_DESKTOP = 1920
    ULTRA_WIDE = 2560
    
    # 高度断点
    COMPACT_HEIGHT = 600
    STANDARD_HEIGHT = 800
    TALL_HEIGHT = 1080


class LayoutMode:
    """布局模式定义"""
    
    MOBILE = "mobile"           # 移动端布局
    TABLET = "tablet"           # 平板布局
    DESKTOP = "desktop"         # 桌面布局
    LARGE_DESKTOP = "large"     # 大屏桌面布局
    ULTRA_WIDE = "ultra_wide"   # 超宽屏布局


class ResponsivePanel(QWidget):
    """响应式面板基类"""
    
    def __init__(self, panel_id: str, title: str, min_width: int = 200, min_height: int = 100):
        super().__init__()
        self.panel_id = panel_id
        self.title = title
        self.min_width = min_width
        self.min_height = min_height
        self.is_collapsible = True
        self.is_collapsed = False
        self.preferred_width = min_width
        self.preferred_height = min_height
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setMinimumSize(self.min_width, self.min_height)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题栏
        self.title_bar = self.create_title_bar()
        layout.addWidget(self.title_bar)
        
        # 内容区域
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.setup_content()
        
        layout.addWidget(self.content_area)
    
    def create_title_bar(self) -> QWidget:
        """创建标题栏"""
        title_bar = QFrame()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                border-radius: 4px 4px 0 0;
            }
        """)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # 标题
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        return title_bar
    
    def setup_content(self):
        """设置内容 - 子类重写"""
        pass
    
    def collapse(self):
        """折叠面板"""
        if self.is_collapsible:
            self.is_collapsed = True
            self.content_area.setVisible(False)
            self.setMaximumHeight(self.title_bar.height())
    
    def expand(self):
        """展开面板"""
        self.is_collapsed = False
        self.content_area.setVisible(True)
        self.setMaximumHeight(16777215)  # 恢复最大高度
    
    def set_responsive_size(self, width: int, height: int):
        """设置响应式尺寸"""
        self.preferred_width = max(width, self.min_width)
        self.preferred_height = max(height, self.min_height)
        self.resize(self.preferred_width, self.preferred_height)


class ResponsiveLayoutManager(QWidget):
    """响应式布局管理器"""
    
    layout_changed = pyqtSignal(str)  # 布局模式改变信号
    panel_resized = pyqtSignal(str, QSize)  # 面板大小改变信号
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_mode = LayoutMode.DESKTOP
        self.panels = {}
        self.splitters = {}
        self.layout_configs = {}
        
        # 响应式参数
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.handle_delayed_resize)
        
        self.initialize_layout_configs()
        self.setup_ui()
        
        logger.info("响应式布局管理器初始化完成")
    
    def initialize_layout_configs(self):
        """初始化布局配置"""
        self.layout_configs = {
            LayoutMode.MOBILE: {
                'panel_arrangement': 'stacked',  # 堆叠布局
                'visible_panels': ['main_work', 'timeline'],
                'collapsed_panels': ['left_panel', 'right_panel'],
                'splitter_orientation': Qt.Orientation.Vertical,
                'panel_sizes': {
                    'main_work': {'width': '100%', 'height': '70%'},
                    'timeline': {'width': '100%', 'height': '30%'}
                },
                'toolbar_style': 'compact',
                'menu_style': 'hamburger'
            },
            
            LayoutMode.TABLET: {
                'panel_arrangement': 'two_column',  # 两列布局
                'visible_panels': ['left_panel', 'main_work', 'timeline'],
                'collapsed_panels': ['right_panel'],
                'splitter_orientation': Qt.Orientation.Horizontal,
                'panel_sizes': {
                    'left_panel': {'width': '25%', 'height': '100%'},
                    'main_work': {'width': '75%', 'height': '70%'},
                    'timeline': {'width': '100%', 'height': '30%'}
                },
                'toolbar_style': 'standard',
                'menu_style': 'full'
            },
            
            LayoutMode.DESKTOP: {
                'panel_arrangement': 'three_column',  # 三列布局
                'visible_panels': ['left_panel', 'main_work', 'right_panel', 'timeline'],
                'collapsed_panels': [],
                'splitter_orientation': Qt.Orientation.Horizontal,
                'panel_sizes': {
                    'left_panel': {'width': '20%', 'height': '100%'},
                    'main_work': {'width': '60%', 'height': '70%'},
                    'right_panel': {'width': '20%', 'height': '100%'},
                    'timeline': {'width': '100%', 'height': '30%'}
                },
                'toolbar_style': 'full',
                'menu_style': 'full'
            },
            
            LayoutMode.LARGE_DESKTOP: {
                'panel_arrangement': 'four_column',  # 四列布局
                'visible_panels': ['left_panel', 'main_work', 'right_panel', 'ai_panel', 'timeline'],
                'collapsed_panels': [],
                'splitter_orientation': Qt.Orientation.Horizontal,
                'panel_sizes': {
                    'left_panel': {'width': '18%', 'height': '100%'},
                    'main_work': {'width': '50%', 'height': '70%'},
                    'right_panel': {'width': '16%', 'height': '100%'},
                    'ai_panel': {'width': '16%', 'height': '100%'},
                    'timeline': {'width': '100%', 'height': '30%'}
                },
                'toolbar_style': 'extended',
                'menu_style': 'full'
            },
            
            LayoutMode.ULTRA_WIDE: {
                'panel_arrangement': 'multi_column',  # 多列布局
                'visible_panels': ['left_panel', 'main_work', 'preview_panel', 'right_panel', 'ai_panel', 'timeline'],
                'collapsed_panels': [],
                'splitter_orientation': Qt.Orientation.Horizontal,
                'panel_sizes': {
                    'left_panel': {'width': '15%', 'height': '100%'},
                    'main_work': {'width': '40%', 'height': '70%'},
                    'preview_panel': {'width': '15%', 'height': '100%'},
                    'right_panel': {'width': '15%', 'height': '100%'},
                    'ai_panel': {'width': '15%', 'height': '100%'},
                    'timeline': {'width': '100%', 'height': '30%'}
                },
                'toolbar_style': 'professional',
                'menu_style': 'full'
            }
        }
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建主容器
        self.main_container = QWidget()
        layout.addWidget(self.main_container)
        
        # 初始化为桌面布局
        self.apply_layout_mode(LayoutMode.DESKTOP)
    
    def detect_layout_mode(self, size: QSize) -> str:
        """检测应该使用的布局模式"""
        width = size.width()
        height = size.height()
        
        # 根据宽度确定基本模式
        if width < ScreenSize.MOBILE:
            base_mode = LayoutMode.MOBILE
        elif width < ScreenSize.TABLET:
            base_mode = LayoutMode.TABLET
        elif width < ScreenSize.DESKTOP:
            base_mode = LayoutMode.DESKTOP
        elif width < ScreenSize.LARGE_DESKTOP:
            base_mode = LayoutMode.LARGE_DESKTOP
        else:
            base_mode = LayoutMode.ULTRA_WIDE
        
        # 考虑高度因素
        if height < ScreenSize.COMPACT_HEIGHT:
            # 高度不足时，优先使用紧凑布局
            if base_mode in [LayoutMode.LARGE_DESKTOP, LayoutMode.ULTRA_WIDE]:
                base_mode = LayoutMode.DESKTOP
        
        return base_mode
    
    def apply_layout_mode(self, mode: str):
        """应用布局模式"""
        if mode == self.current_mode:
            return

        try:
            old_mode = self.current_mode
            self.current_mode = mode

            config = self.layout_configs.get(mode, self.layout_configs[LayoutMode.DESKTOP])

            # 对于桌面相关模式，不要重新创建布局，而是适配现有的五区域布局
            desktop_modes = [LayoutMode.DESKTOP, LayoutMode.LARGE_DESKTOP, LayoutMode.ULTRA_WIDE]
            if mode in desktop_modes and hasattr(self.main_window, 'timeline_area_widget'):
                logger.info(f"{mode}模式：保持现有五区域布局，不进行重建")
                # 只更新工具栏和菜单样式，不重建布局
                self.update_toolbar_style(config.get('toolbar_style', 'standard'))
                self.update_menu_style(config.get('menu_style', 'full'))
            else:
                # 其他模式才进行布局重建
                # 清空现有布局
                self.clear_layout()

                # 应用新布局
                self.create_layout_by_config(config)

                # 更新工具栏和菜单样式
                self.update_toolbar_style(config.get('toolbar_style', 'standard'))
                self.update_menu_style(config.get('menu_style', 'full'))

            # 发送布局改变信号
            self.layout_changed.emit(mode)

            logger.info(f"布局模式从 {old_mode} 切换到 {mode}")

        except Exception as e:
            logger.error(f"应用布局模式失败: {e}")
    
    def clear_layout(self):
        """清空现有布局"""
        if self.main_container.layout():
            layout = self.main_container.layout()
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
    
    def create_layout_by_config(self, config: dict):
        """根据配置创建布局"""
        arrangement = config.get('panel_arrangement', 'three_column')
        
        if arrangement == 'stacked':
            self.create_stacked_layout(config)
        elif arrangement == 'two_column':
            self.create_two_column_layout(config)
        elif arrangement == 'three_column':
            self.create_three_column_layout(config)
        elif arrangement == 'four_column':
            self.create_four_column_layout(config)
        elif arrangement == 'multi_column':
            self.create_multi_column_layout(config)
    
    def create_stacked_layout(self, config: dict):
        """创建堆叠布局（移动端）"""
        layout = QVBoxLayout(self.main_container)
        
        # 主工作区
        main_work = self.get_or_create_panel('main_work', '主工作区')
        layout.addWidget(main_work, 7)  # 70%
        
        # 时间轴
        timeline = self.get_or_create_panel('timeline', '时间轴')
        layout.addWidget(timeline, 3)  # 30%
    
    def create_two_column_layout(self, config: dict):
        """创建两列布局（平板）"""
        main_layout = QVBoxLayout(self.main_container)
        
        # 上部分：左侧面板 + 主工作区
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_panel = self.get_or_create_panel('left_panel', '左侧面板')
        main_work = self.get_or_create_panel('main_work', '主工作区')
        
        top_splitter.addWidget(left_panel)
        top_splitter.addWidget(main_work)
        top_splitter.setSizes([250, 750])  # 25% : 75%
        
        main_layout.addWidget(top_splitter, 7)
        
        # 下部分：时间轴
        timeline = self.get_or_create_panel('timeline', '时间轴')
        main_layout.addWidget(timeline, 3)
    
    def create_three_column_layout(self, config: dict):
        """创建三列布局（桌面）"""
        main_layout = QVBoxLayout(self.main_container)
        
        # 上部分：三列布局
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_panel = self.get_or_create_panel('left_panel', '左侧面板')
        main_work = self.get_or_create_panel('main_work', '主工作区')
        right_panel = self.get_or_create_panel('right_panel', '右侧面板')
        
        top_splitter.addWidget(left_panel)
        top_splitter.addWidget(main_work)
        top_splitter.addWidget(right_panel)
        top_splitter.setSizes([300, 800, 300])  # 20% : 60% : 20%
        
        main_layout.addWidget(top_splitter, 7)
        
        # 下部分：时间轴
        timeline = self.get_or_create_panel('timeline', '时间轴')
        main_layout.addWidget(timeline, 3)
        
        self.splitters['main'] = top_splitter
    
    def create_four_column_layout(self, config: dict):
        """创建四列布局（大屏桌面）"""
        main_layout = QVBoxLayout(self.main_container)
        
        # 上部分：四列布局
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_panel = self.get_or_create_panel('left_panel', '左侧面板')
        main_work = self.get_or_create_panel('main_work', '主工作区')
        right_panel = self.get_or_create_panel('right_panel', '右侧面板')
        ai_panel = self.get_or_create_panel('ai_panel', 'AI面板')
        
        top_splitter.addWidget(left_panel)
        top_splitter.addWidget(main_work)
        top_splitter.addWidget(right_panel)
        top_splitter.addWidget(ai_panel)
        top_splitter.setSizes([270, 750, 240, 240])  # 18% : 50% : 16% : 16%
        
        main_layout.addWidget(top_splitter, 7)
        
        # 下部分：时间轴
        timeline = self.get_or_create_panel('timeline', '时间轴')
        main_layout.addWidget(timeline, 3)
        
        self.splitters['main'] = top_splitter
    
    def create_multi_column_layout(self, config: dict):
        """创建多列布局（超宽屏）"""
        main_layout = QVBoxLayout(self.main_container)
        
        # 上部分：多列布局
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_panel = self.get_or_create_panel('left_panel', '左侧面板')
        main_work = self.get_or_create_panel('main_work', '主工作区')
        preview_panel = self.get_or_create_panel('preview_panel', '预览面板')
        right_panel = self.get_or_create_panel('right_panel', '右侧面板')
        ai_panel = self.get_or_create_panel('ai_panel', 'AI面板')
        
        top_splitter.addWidget(left_panel)
        top_splitter.addWidget(main_work)
        top_splitter.addWidget(preview_panel)
        top_splitter.addWidget(right_panel)
        top_splitter.addWidget(ai_panel)
        top_splitter.setSizes([300, 800, 300, 300, 300])  # 15% : 40% : 15% : 15% : 15%
        
        main_layout.addWidget(top_splitter, 7)
        
        # 下部分：时间轴
        timeline = self.get_or_create_panel('timeline', '时间轴')
        main_layout.addWidget(timeline, 3)
        
        self.splitters['main'] = top_splitter
    
    def get_or_create_panel(self, panel_id: str, title: str) -> ResponsivePanel:
        """获取或创建面板"""
        if panel_id not in self.panels:
            self.panels[panel_id] = ResponsivePanel(panel_id, title)
        return self.panels[panel_id]
    
    def update_toolbar_style(self, style: str):
        """更新工具栏样式"""
        try:
            if hasattr(self.main_window, 'professional_toolbar_manager'):
                toolbar_manager = self.main_window.professional_toolbar_manager
                
                if style == 'compact':
                    # 紧凑样式：只显示图标
                    for toolbar in toolbar_manager.toolbars.values():
                        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
                        toolbar.setIconSize(QSize(16, 16))
                elif style == 'standard':
                    # 标准样式：图标+文字
                    for toolbar in toolbar_manager.toolbars.values():
                        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
                        toolbar.setIconSize(QSize(20, 20))
                elif style == 'full':
                    # 完整样式：图标下方文字
                    for toolbar in toolbar_manager.toolbars.values():
                        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
                        toolbar.setIconSize(QSize(24, 24))
                elif style == 'extended':
                    # 扩展样式：大图标+文字
                    for toolbar in toolbar_manager.toolbars.values():
                        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
                        toolbar.setIconSize(QSize(32, 32))
                elif style == 'professional':
                    # 专业样式：超大图标+文字
                    for toolbar in toolbar_manager.toolbars.values():
                        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
                        toolbar.setIconSize(QSize(40, 40))
                        
        except Exception as e:
            logger.error(f"更新工具栏样式失败: {e}")
    
    def update_menu_style(self, style: str):
        """更新菜单样式"""
        try:
            if style == 'hamburger':
                # 汉堡菜单样式（移动端）
                self.main_window.menuBar().setVisible(False)
                # 这里可以添加汉堡菜单按钮
            else:
                # 完整菜单样式
                self.main_window.menuBar().setVisible(True)
                
        except Exception as e:
            logger.error(f"更新菜单样式失败: {e}")
    
    def handle_resize(self, size: QSize):
        """处理窗口大小改变"""
        # 延迟处理，避免频繁调整
        self.pending_size = size
        self.resize_timer.start(100)  # 100ms延迟
    
    def handle_delayed_resize(self):
        """延迟处理窗口大小改变"""
        try:
            new_mode = self.detect_layout_mode(self.pending_size)
            self.apply_layout_mode(new_mode)
            
        except Exception as e:
            logger.error(f"处理窗口大小改变失败: {e}")
    
    def get_current_mode(self) -> str:
        """获取当前布局模式"""
        return self.current_mode
    
    def get_layout_summary(self) -> dict:
        """获取布局摘要"""
        return {
            'current_mode': self.current_mode,
            'window_size': self.size(),
            'panel_count': len(self.panels),
            'visible_panels': len([p for p in self.panels.values() if p.isVisible()]),
            'collapsed_panels': len([p for p in self.panels.values() if p.is_collapsed]),
            'layout_config': self.layout_configs.get(self.current_mode, {})
        }


class ScreenAdaptationManager:
    """屏幕适配管理器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.current_screen = None
        self.dpi_scale = 1.0
        self.font_scale = 1.0
        self.icon_scale = 1.0

        self.detect_screen_properties()
        logger.info("屏幕适配管理器初始化完成")

    def detect_screen_properties(self):
        """检测屏幕属性"""
        try:
            app = QApplication.instance()
            if app:
                self.current_screen = app.primaryScreen()

                # 获取DPI信息
                logical_dpi = self.current_screen.logicalDotsPerInch()
                physical_dpi = self.current_screen.physicalDotsPerInch()
                device_pixel_ratio = self.current_screen.devicePixelRatio()

                # 计算缩放比例
                self.dpi_scale = device_pixel_ratio

                # 根据DPI调整字体和图标缩放
                if logical_dpi > 120:  # 高DPI屏幕
                    self.font_scale = min(logical_dpi / 96.0, 1.5)  # 最大1.5倍
                    self.icon_scale = min(device_pixel_ratio, 2.0)  # 最大2倍
                else:
                    self.font_scale = 1.0
                    self.icon_scale = 1.0

                logger.info(f"屏幕适配: DPI={logical_dpi}, 设备像素比={device_pixel_ratio}, "
                           f"字体缩放={self.font_scale:.2f}, 图标缩放={self.icon_scale:.2f}")

        except Exception as e:
            logger.error(f"检测屏幕属性失败: {e}")

    def apply_screen_adaptation(self):
        """应用屏幕适配"""
        try:
            self.adapt_fonts()
            self.adapt_icons()
            self.adapt_spacing()

        except Exception as e:
            logger.error(f"应用屏幕适配失败: {e}")

    def adapt_fonts(self):
        """适配字体大小"""
        try:
            # 获取应用程序字体
            app = QApplication.instance()
            if app:
                font = app.font()

                # 调整字体大小
                new_size = int(font.pointSize() * self.font_scale)
                font.setPointSize(new_size)
                app.setFont(font)

                # 为不同组件设置特定字体
                self.set_component_fonts()

        except Exception as e:
            logger.error(f"适配字体失败: {e}")

    def set_component_fonts(self):
        """设置组件特定字体"""
        try:
            base_size = int(12 * self.font_scale)

            # 定义字体样式
            font_styles = {
                'title': QFont("Microsoft YaHei", int(base_size * 1.2), QFont.Weight.Bold),
                'subtitle': QFont("Microsoft YaHei", int(base_size * 1.1), QFont.Weight.Bold),
                'body': QFont("Microsoft YaHei", base_size),
                'small': QFont("Microsoft YaHei", int(base_size * 0.9)),
                'code': QFont("Consolas", base_size),
                'button': QFont("Microsoft YaHei", base_size, QFont.Weight.Bold)
            }

            # 应用到主窗口
            self.main_window.setFont(font_styles['body'])

        except Exception as e:
            logger.error(f"设置组件字体失败: {e}")

    def adapt_icons(self):
        """适配图标大小"""
        try:
            if hasattr(self.main_window, 'professional_toolbar_manager'):
                toolbar_manager = self.main_window.professional_toolbar_manager

                # 计算图标大小
                base_icon_size = 24
                scaled_size = int(base_icon_size * self.icon_scale)
                icon_size = QSize(scaled_size, scaled_size)

                # 应用到所有工具栏
                for toolbar in toolbar_manager.toolbars.values():
                    toolbar.setIconSize(icon_size)

        except Exception as e:
            logger.error(f"适配图标失败: {e}")

    def adapt_spacing(self):
        """适配间距和边距"""
        try:
            # 计算缩放后的间距
            base_margin = 5
            base_spacing = 5

            scaled_margin = int(base_margin * self.dpi_scale)
            scaled_spacing = int(base_spacing * self.dpi_scale)

            # 应用到主窗口布局
            if self.main_window.centralWidget():
                layout = self.main_window.centralWidget().layout()
                if layout:
                    layout.setContentsMargins(scaled_margin, scaled_margin,
                                            scaled_margin, scaled_margin)
                    layout.setSpacing(scaled_spacing)

        except Exception as e:
            logger.error(f"适配间距失败: {e}")

    def get_scaled_size(self, base_size: int) -> int:
        """获取缩放后的尺寸"""
        return int(base_size * self.dpi_scale)

    def get_scaled_font_size(self, base_size: int) -> int:
        """获取缩放后的字体大小"""
        return int(base_size * self.font_scale)

    def get_scaled_icon_size(self, base_size: int) -> QSize:
        """获取缩放后的图标大小"""
        scaled_size = int(base_size * self.icon_scale)
        return QSize(scaled_size, scaled_size)


class ResponsiveBreakpointManager:
    """响应式断点管理器"""

    def __init__(self):
        self.breakpoints = {
            'xs': 0,      # 超小屏
            'sm': 576,    # 小屏
            'md': 768,    # 中屏
            'lg': 992,    # 大屏
            'xl': 1200,   # 超大屏
            'xxl': 1400   # 超超大屏
        }

        self.current_breakpoint = 'lg'
        logger.info("响应式断点管理器初始化完成")

    def get_breakpoint(self, width: int) -> str:
        """根据宽度获取断点"""
        for name, min_width in reversed(list(self.breakpoints.items())):
            if width >= min_width:
                return name
        return 'xs'

    def update_breakpoint(self, width: int):
        """更新当前断点"""
        new_breakpoint = self.get_breakpoint(width)
        if new_breakpoint != self.current_breakpoint:
            old_breakpoint = self.current_breakpoint
            self.current_breakpoint = new_breakpoint
            logger.info(f"断点从 {old_breakpoint} 切换到 {new_breakpoint}")

    def is_mobile(self) -> bool:
        """是否为移动端尺寸"""
        return self.current_breakpoint in ['xs', 'sm']

    def is_tablet(self) -> bool:
        """是否为平板尺寸"""
        return self.current_breakpoint == 'md'

    def is_desktop(self) -> bool:
        """是否为桌面尺寸"""
        return self.current_breakpoint in ['lg', 'xl', 'xxl']

    def get_column_count(self) -> int:
        """根据断点获取推荐列数"""
        column_map = {
            'xs': 1,
            'sm': 1,
            'md': 2,
            'lg': 3,
            'xl': 4,
            'xxl': 5
        }
        return column_map.get(self.current_breakpoint, 3)


class ResponsiveStyleManager:
    """响应式样式管理器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.style_cache = {}
        self.current_theme = 'light'

        self.initialize_responsive_styles()
        logger.info("响应式样式管理器初始化完成")

    def initialize_responsive_styles(self):
        """初始化响应式样式"""
        self.style_cache = {
            'mobile': {
                'panel_padding': '8px',
                'button_height': '44px',
                'font_size': '14px',
                'icon_size': '20px',
                'border_radius': '6px'
            },
            'tablet': {
                'panel_padding': '12px',
                'button_height': '36px',
                'font_size': '13px',
                'icon_size': '22px',
                'border_radius': '5px'
            },
            'desktop': {
                'panel_padding': '16px',
                'button_height': '32px',
                'font_size': '12px',
                'icon_size': '24px',
                'border_radius': '4px'
            },
            'large_desktop': {
                'panel_padding': '20px',
                'button_height': '36px',
                'font_size': '13px',
                'icon_size': '28px',
                'border_radius': '6px'
            }
        }

    def apply_responsive_styles(self, layout_mode: str):
        """应用响应式样式"""
        try:
            # 映射布局模式到样式模式
            style_mode_map = {
                LayoutMode.MOBILE: 'mobile',
                LayoutMode.TABLET: 'tablet',
                LayoutMode.DESKTOP: 'desktop',
                LayoutMode.LARGE_DESKTOP: 'large_desktop',
                LayoutMode.ULTRA_WIDE: 'large_desktop'
            }

            style_mode = style_mode_map.get(layout_mode, 'desktop')
            styles = self.style_cache.get(style_mode, self.style_cache['desktop'])

            # 生成CSS样式
            css = self.generate_css(styles)

            # 应用到主窗口
            self.main_window.setStyleSheet(css)

        except Exception as e:
            logger.error(f"应用响应式样式失败: {e}")

    def generate_css(self, styles: dict) -> str:
        """生成CSS样式"""
        css = f"""
        /* 响应式样式 */
        QWidget {{
            font-size: {styles['font_size']};
        }}

        QPushButton {{
            min-height: {styles['button_height']};
            padding: 0 {styles['panel_padding']};
            border-radius: {styles['border_radius']};
            font-weight: bold;
        }}

        QGroupBox {{
            padding: {styles['panel_padding']};
            border-radius: {styles['border_radius']};
        }}

        QFrame {{
            border-radius: {styles['border_radius']};
        }}

        QTabWidget::pane {{
            border-radius: {styles['border_radius']};
        }}

        /* 工具栏样式 */
        QToolBar {{
            spacing: 4px;
            padding: 4px;
        }}

        QToolButton {{
            min-width: {styles['button_height']};
            min-height: {styles['button_height']};
            border-radius: {styles['border_radius']};
        }}
        """

        return css

    def update_theme(self, theme: str):
        """更新主题"""
        self.current_theme = theme
        # 这里可以根据主题调整颜色

    def get_current_styles(self) -> dict:
        """获取当前样式"""
        return self.style_cache.get('desktop', {})
