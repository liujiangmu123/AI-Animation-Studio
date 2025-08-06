"""
AI Animation Studio - 双模式布局管理器
实现编辑模式和预览模式的一键切换功能
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QSplitter, QFrame, QStackedWidget, QToolButton, QButtonGroup,
                             QApplication, QSizePolicy, QSpacerItem, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QPropertyAnimation, QEasingCurve, QRect, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPainter, QBrush, QPen, QPixmap

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union
import json
import time
from dataclasses import dataclass, field
from datetime import datetime

from core.logger import get_logger

logger = get_logger("dual_mode_layout_manager")


class LayoutMode(Enum):
    """布局模式枚举"""
    EDIT = "edit"           # 编辑模式
    PREVIEW = "preview"     # 预览模式


class TransitionType(Enum):
    """过渡类型枚举"""
    INSTANT = "instant"     # 即时切换
    SMOOTH = "smooth"       # 平滑过渡
    SLIDE = "slide"         # 滑动过渡
    FADE = "fade"           # 淡入淡出


@dataclass
class LayoutConfig:
    """布局配置"""
    mode: LayoutMode
    main_area_ratio: float      # 主区域占比
    secondary_area_ratio: float # 次要区域占比
    visible_panels: List[str]   # 可见面板列表
    hidden_panels: List[str]    # 隐藏面板列表
    toolbar_style: str = "full" # 工具栏样式
    status_bar_visible: bool = True  # 状态栏可见性
    transition_duration: int = 300   # 过渡时长(毫秒)


class LayoutTransitionAnimator(QObject):
    """布局过渡动画器"""
    
    transition_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animations: List[QPropertyAnimation] = []
        self.is_animating = False
        
        logger.info("布局过渡动画器初始化完成")
    
    def animate_layout_change(self, from_config: LayoutConfig, to_config: LayoutConfig, 
                            widgets: Dict[str, QWidget]):
        """执行布局变化动画"""
        try:
            if self.is_animating:
                self.stop_all_animations()
            
            self.is_animating = True
            self.animations.clear()
            
            # 创建动画
            duration = to_config.transition_duration
            
            # 主区域动画
            if "main_area" in widgets:
                main_widget = widgets["main_area"]
                self.create_resize_animation(main_widget, to_config.main_area_ratio, duration)
            
            # 次要区域动画
            if "secondary_area" in widgets:
                secondary_widget = widgets["secondary_area"]
                self.create_resize_animation(secondary_widget, to_config.secondary_area_ratio, duration)
            
            # 面板显示/隐藏动画
            self.animate_panel_visibility(from_config, to_config, widgets, duration)
            
            # 启动所有动画
            self.start_all_animations()
            
        except Exception as e:
            logger.error(f"执行布局变化动画失败: {e}")
            self.is_animating = False
    
    def create_resize_animation(self, widget: QWidget, target_ratio: float, duration: int):
        """创建调整大小动画"""
        try:
            animation = QPropertyAnimation(widget, b"geometry")
            animation.setDuration(duration)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # 计算目标几何形状
            parent = widget.parent()
            if parent:
                parent_rect = parent.rect()
                target_width = int(parent_rect.width() * target_ratio)
                target_rect = QRect(widget.x(), widget.y(), target_width, widget.height())
                animation.setEndValue(target_rect)
            
            self.animations.append(animation)
            
        except Exception as e:
            logger.error(f"创建调整大小动画失败: {e}")
    
    def animate_panel_visibility(self, from_config: LayoutConfig, to_config: LayoutConfig, 
                               widgets: Dict[str, QWidget], duration: int):
        """动画面板可见性变化"""
        try:
            # 需要隐藏的面板
            panels_to_hide = set(from_config.visible_panels) - set(to_config.visible_panels)
            for panel_name in panels_to_hide:
                if panel_name in widgets:
                    self.create_fade_out_animation(widgets[panel_name], duration)
            
            # 需要显示的面板
            panels_to_show = set(to_config.visible_panels) - set(from_config.visible_panels)
            for panel_name in panels_to_show:
                if panel_name in widgets:
                    self.create_fade_in_animation(widgets[panel_name], duration)
            
        except Exception as e:
            logger.error(f"动画面板可见性变化失败: {e}")
    
    def create_fade_out_animation(self, widget: QWidget, duration: int):
        """创建淡出动画"""
        try:
            animation = QPropertyAnimation(widget, b"windowOpacity")
            animation.setDuration(duration)
            animation.setStartValue(1.0)
            animation.setEndValue(0.0)
            animation.setEasingCurve(QEasingCurve.Type.OutQuad)
            
            # 动画结束后隐藏组件
            animation.finished.connect(lambda: widget.setVisible(False))
            
            self.animations.append(animation)
            
        except Exception as e:
            logger.error(f"创建淡出动画失败: {e}")
    
    def create_fade_in_animation(self, widget: QWidget, duration: int):
        """创建淡入动画"""
        try:
            # 先显示组件
            widget.setVisible(True)
            widget.setWindowOpacity(0.0)
            
            animation = QPropertyAnimation(widget, b"windowOpacity")
            animation.setDuration(duration)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.InQuad)
            
            self.animations.append(animation)
            
        except Exception as e:
            logger.error(f"创建淡入动画失败: {e}")
    
    def start_all_animations(self):
        """启动所有动画"""
        try:
            if not self.animations:
                self.is_animating = False
                self.transition_finished.emit()
                return
            
            # 连接最后一个动画的完成信号
            if self.animations:
                self.animations[-1].finished.connect(self.on_animation_finished)
            
            # 启动所有动画
            for animation in self.animations:
                animation.start()
            
        except Exception as e:
            logger.error(f"启动所有动画失败: {e}")
            self.is_animating = False
    
    def stop_all_animations(self):
        """停止所有动画"""
        try:
            for animation in self.animations:
                if animation.state() == QPropertyAnimation.State.Running:
                    animation.stop()
            
            self.animations.clear()
            self.is_animating = False
            
        except Exception as e:
            logger.error(f"停止所有动画失败: {e}")
    
    def on_animation_finished(self):
        """动画完成处理"""
        try:
            self.is_animating = False
            self.transition_finished.emit()
            
        except Exception as e:
            logger.error(f"动画完成处理失败: {e}")


class DualModeLayoutManager(QObject):
    """双模式布局管理器"""
    
    # 信号定义
    mode_changed = pyqtSignal(str)              # 模式改变信号
    layout_applied = pyqtSignal(str)            # 布局应用信号
    transition_started = pyqtSignal(str, str)   # 过渡开始信号 (from_mode, to_mode)
    transition_finished = pyqtSignal(str)       # 过渡完成信号
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_mode = LayoutMode.EDIT
        self.layout_configs = self.setup_layout_configs()
        self.transition_animator = LayoutTransitionAnimator()
        self.widgets_registry: Dict[str, QWidget] = {}
        
        # 连接动画器信号
        self.transition_animator.transition_finished.connect(self.on_transition_finished)
        
        logger.info("双模式布局管理器初始化完成")
    
    def setup_layout_configs(self) -> Dict[LayoutMode, LayoutConfig]:
        """设置布局配置"""
        return {
            LayoutMode.EDIT: LayoutConfig(
                mode=LayoutMode.EDIT,
                main_area_ratio=0.8,        # 编辑区域占80%
                secondary_area_ratio=0.2,   # 预览区域占20%
                visible_panels=[
                    "elements_widget", "properties_widget", "stage_widget", 
                    "timeline_widget", "ai_generator_widget", "preview_widget"
                ],
                hidden_panels=[],
                toolbar_style="full",
                status_bar_visible=True,
                transition_duration=300
            ),
            LayoutMode.PREVIEW: LayoutConfig(
                mode=LayoutMode.PREVIEW,
                main_area_ratio=0.8,        # 预览区域占80%
                secondary_area_ratio=0.2,   # 控制面板占20%
                visible_panels=[
                    "preview_widget", "timeline_widget", "playback_control"
                ],
                hidden_panels=[
                    "elements_widget", "properties_widget", "ai_generator_widget"
                ],
                toolbar_style="minimal",
                status_bar_visible=False,
                transition_duration=300
            )
        }
    
    def register_widget(self, name: str, widget: QWidget):
        """注册组件"""
        self.widgets_registry[name] = widget
        logger.debug(f"注册组件: {name}")
    
    def unregister_widget(self, name: str):
        """取消注册组件"""
        if name in self.widgets_registry:
            del self.widgets_registry[name]
            logger.debug(f"取消注册组件: {name}")
    
    def get_current_mode(self) -> LayoutMode:
        """获取当前模式"""
        return self.current_mode
    
    def switch_to_mode(self, mode: LayoutMode, animated: bool = True):
        """切换到指定模式"""
        try:
            if mode == self.current_mode:
                return
            
            old_mode = self.current_mode
            old_config = self.layout_configs[old_mode]
            new_config = self.layout_configs[mode]
            
            # 发送过渡开始信号
            self.transition_started.emit(old_mode.value, mode.value)
            
            if animated:
                # 执行动画过渡
                self.transition_animator.animate_layout_change(
                    old_config, new_config, self.widgets_registry
                )
            else:
                # 立即应用布局
                self.apply_layout_immediately(new_config)
                self.on_transition_finished()
            
            self.current_mode = mode
            
            logger.info(f"切换布局模式: {old_mode.value} -> {mode.value}")
            
        except Exception as e:
            logger.error(f"切换到指定模式失败: {e}")
    
    def toggle_mode(self, animated: bool = True):
        """切换模式"""
        try:
            new_mode = LayoutMode.PREVIEW if self.current_mode == LayoutMode.EDIT else LayoutMode.EDIT
            self.switch_to_mode(new_mode, animated)
            
        except Exception as e:
            logger.error(f"切换模式失败: {e}")
    
    def apply_layout_immediately(self, config: LayoutConfig):
        """立即应用布局"""
        try:
            # 应用面板可见性
            self.apply_panel_visibility(config)
            
            # 应用布局比例
            self.apply_layout_ratios(config)
            
            # 应用工具栏样式
            self.apply_toolbar_style(config)
            
            # 应用状态栏可见性
            self.apply_status_bar_visibility(config)
            
            # 发送布局应用信号
            self.layout_applied.emit(config.mode.value)
            
        except Exception as e:
            logger.error(f"立即应用布局失败: {e}")
    
    def apply_panel_visibility(self, config: LayoutConfig):
        """应用面板可见性"""
        try:
            # 显示可见面板
            for panel_name in config.visible_panels:
                if panel_name in self.widgets_registry:
                    widget = self.widgets_registry[panel_name]
                    widget.setVisible(True)
                    widget.setWindowOpacity(1.0)
            
            # 隐藏不可见面板
            for panel_name in config.hidden_panels:
                if panel_name in self.widgets_registry:
                    widget = self.widgets_registry[panel_name]
                    widget.setVisible(False)
            
        except Exception as e:
            logger.error(f"应用面板可见性失败: {e}")
    
    def apply_layout_ratios(self, config: LayoutConfig):
        """应用布局比例"""
        try:
            # 获取主分割器
            if hasattr(self.main_window, 'main_splitter'):
                splitter = self.main_window.main_splitter
                total_width = splitter.width()
                
                if config.mode == LayoutMode.EDIT:
                    # 编辑模式：左侧面板 + 主编辑区域(80%) + 预览区域(20%)
                    left_size = int(total_width * 0.2)
                    center_size = int(total_width * 0.6)  # 主编辑区域
                    right_size = int(total_width * 0.2)   # 预览区域
                    
                elif config.mode == LayoutMode.PREVIEW:
                    # 预览模式：控制面板(20%) + 主预览区域(80%)
                    left_size = int(total_width * 0.1)
                    center_size = int(total_width * 0.8)  # 主预览区域
                    right_size = int(total_width * 0.1)
                
                splitter.setSizes([left_size, center_size, right_size])
            
        except Exception as e:
            logger.error(f"应用布局比例失败: {e}")
    
    def apply_toolbar_style(self, config: LayoutConfig):
        """应用工具栏样式"""
        try:
            if hasattr(self.main_window, 'toolbar'):
                toolbar = self.main_window.toolbar
                
                if config.toolbar_style == "minimal":
                    # 最小化工具栏：只显示核心功能
                    self.set_minimal_toolbar(toolbar)
                elif config.toolbar_style == "full":
                    # 完整工具栏：显示所有功能
                    self.set_full_toolbar(toolbar)
            
        except Exception as e:
            logger.error(f"应用工具栏样式失败: {e}")
    
    def set_minimal_toolbar(self, toolbar):
        """设置最小化工具栏"""
        try:
            # 隐藏非核心工具栏项
            actions = toolbar.actions()
            essential_actions = ["play", "pause", "stop", "fullscreen", "settings"]
            
            for action in actions:
                action_name = action.objectName()
                if action_name and action_name not in essential_actions:
                    action.setVisible(False)
                else:
                    action.setVisible(True)
            
        except Exception as e:
            logger.error(f"设置最小化工具栏失败: {e}")
    
    def set_full_toolbar(self, toolbar):
        """设置完整工具栏"""
        try:
            # 显示所有工具栏项
            actions = toolbar.actions()
            for action in actions:
                action.setVisible(True)
            
        except Exception as e:
            logger.error(f"设置完整工具栏失败: {e}")
    
    def apply_status_bar_visibility(self, config: LayoutConfig):
        """应用状态栏可见性"""
        try:
            if hasattr(self.main_window, 'statusBar'):
                status_bar = self.main_window.statusBar()
                status_bar.setVisible(config.status_bar_visible)
            
        except Exception as e:
            logger.error(f"应用状态栏可见性失败: {e}")
    
    def on_transition_finished(self):
        """过渡完成处理"""
        try:
            # 发送过渡完成信号
            self.transition_finished.emit(self.current_mode.value)
            
            # 发送模式改变信号
            self.mode_changed.emit(self.current_mode.value)
            
            logger.info(f"布局过渡完成: {self.current_mode.value}")
            
        except Exception as e:
            logger.error(f"过渡完成处理失败: {e}")
    
    def get_layout_config(self, mode: LayoutMode) -> LayoutConfig:
        """获取布局配置"""
        return self.layout_configs.get(mode, self.layout_configs[LayoutMode.EDIT])
    
    def update_layout_config(self, mode: LayoutMode, config: LayoutConfig):
        """更新布局配置"""
        self.layout_configs[mode] = config
        logger.debug(f"更新布局配置: {mode.value}")
    
    def save_current_layout(self) -> Dict[str, Any]:
        """保存当前布局状态"""
        try:
            layout_state = {
                "current_mode": self.current_mode.value,
                "splitter_sizes": [],
                "panel_visibility": {}
            }
            
            # 保存分割器尺寸
            if hasattr(self.main_window, 'main_splitter'):
                layout_state["splitter_sizes"] = self.main_window.main_splitter.sizes()
            
            # 保存面板可见性
            for name, widget in self.widgets_registry.items():
                layout_state["panel_visibility"][name] = widget.isVisible()
            
            return layout_state
            
        except Exception as e:
            logger.error(f"保存当前布局状态失败: {e}")
            return {}
    
    def restore_layout(self, layout_state: Dict[str, Any]):
        """恢复布局状态"""
        try:
            # 恢复模式
            if "current_mode" in layout_state:
                mode_value = layout_state["current_mode"]
                mode = LayoutMode.EDIT if mode_value == "edit" else LayoutMode.PREVIEW
                self.switch_to_mode(mode, animated=False)
            
            # 恢复分割器尺寸
            if "splitter_sizes" in layout_state and hasattr(self.main_window, 'main_splitter'):
                self.main_window.main_splitter.setSizes(layout_state["splitter_sizes"])
            
            # 恢复面板可见性
            if "panel_visibility" in layout_state:
                for name, visible in layout_state["panel_visibility"].items():
                    if name in self.widgets_registry:
                        self.widgets_registry[name].setVisible(visible)
            
            logger.info("布局状态恢复完成")
            
        except Exception as e:
            logger.error(f"恢复布局状态失败: {e}")


class ModeToggleButton(QToolButton):
    """模式切换按钮"""
    
    mode_toggle_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = LayoutMode.EDIT
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setCheckable(True)
        self.update_appearance()
        
        # 设置样式
        self.setStyleSheet("""
            QToolButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QToolButton:hover {
                background-color: #357abd;
            }
            QToolButton:checked {
                background-color: #2c5aa0;
            }
        """)
    
    def setup_connections(self):
        """设置信号连接"""
        self.clicked.connect(self.on_clicked)
    
    def update_appearance(self):
        """更新外观"""
        if self.current_mode == LayoutMode.EDIT:
            self.setText("🔄 编辑模式")
            self.setToolTip("点击切换到预览模式")
            self.setChecked(False)
        else:
            self.setText("👁️ 预览模式")
            self.setToolTip("点击切换到编辑模式")
            self.setChecked(True)
    
    def set_mode(self, mode: LayoutMode):
        """设置模式"""
        if mode != self.current_mode:
            self.current_mode = mode
            self.update_appearance()
    
    def on_clicked(self):
        """点击处理"""
        self.mode_toggle_requested.emit()


class ModeControlToolbar(QWidget):
    """模式控制工具栏"""

    mode_changed = pyqtSignal(str)
    layout_saved = pyqtSignal()
    layout_restored = pyqtSignal()

    def __init__(self, layout_manager: DualModeLayoutManager, parent=None):
        super().__init__(parent)
        self.layout_manager = layout_manager
        self.setup_ui()
        self.setup_connections()

        logger.info("模式控制工具栏初始化完成")

    def setup_ui(self):
        """设置用户界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # 模式切换按钮
        self.toggle_button = ModeToggleButton()
        layout.addWidget(self.toggle_button)

        # 分隔符
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator1)

        # 模式选择按钮组
        self.mode_group = QButtonGroup(self)

        self.edit_mode_btn = QPushButton("📝 编辑模式")
        self.edit_mode_btn.setCheckable(True)
        self.edit_mode_btn.setChecked(True)
        self.edit_mode_btn.setStyleSheet(self.get_mode_button_style())
        self.mode_group.addButton(self.edit_mode_btn, 0)
        layout.addWidget(self.edit_mode_btn)

        self.preview_mode_btn = QPushButton("👁️ 预览模式")
        self.preview_mode_btn.setCheckable(True)
        self.preview_mode_btn.setStyleSheet(self.get_mode_button_style())
        self.mode_group.addButton(self.preview_mode_btn, 1)
        layout.addWidget(self.preview_mode_btn)

        # 分隔符
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator2)

        # 布局控制按钮
        self.save_layout_btn = QPushButton("💾 保存布局")
        self.save_layout_btn.setToolTip("保存当前布局配置")
        self.save_layout_btn.setStyleSheet(self.get_control_button_style())
        layout.addWidget(self.save_layout_btn)

        self.restore_layout_btn = QPushButton("🔄 恢复布局")
        self.restore_layout_btn.setToolTip("恢复默认布局配置")
        self.restore_layout_btn.setStyleSheet(self.get_control_button_style())
        layout.addWidget(self.restore_layout_btn)

        # 弹簧
        layout.addStretch()

        # 状态指示器
        self.status_label = QLabel("当前模式: 编辑模式")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                padding: 4px 8px;
                background-color: #f0f0f0;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.status_label)

        # 设置整体样式
        self.setStyleSheet("""
            ModeControlToolbar {
                background-color: #fafafa;
                border-bottom: 1px solid #ddd;
            }
        """)

    def get_mode_button_style(self) -> str:
        """获取模式按钮样式"""
        return """
            QPushButton {
                background-color: #e8e8e8;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #d4edda;
                border-color: #c3e6cb;
            }
            QPushButton:checked {
                background-color: #28a745;
                color: white;
                border-color: #1e7e34;
            }
        """

    def get_control_button_style(self) -> str:
        """获取控制按钮样式"""
        return """
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #495057;
            }
        """

    def setup_connections(self):
        """设置信号连接"""
        # 模式切换按钮
        self.toggle_button.mode_toggle_requested.connect(self.on_toggle_mode)

        # 模式选择按钮
        self.mode_group.buttonClicked.connect(self.on_mode_button_clicked)

        # 布局控制按钮
        self.save_layout_btn.clicked.connect(self.on_save_layout)
        self.restore_layout_btn.clicked.connect(self.on_restore_layout)

        # 布局管理器信号
        self.layout_manager.mode_changed.connect(self.on_layout_mode_changed)
        self.layout_manager.transition_started.connect(self.on_transition_started)
        self.layout_manager.transition_finished.connect(self.on_transition_finished)

    def on_toggle_mode(self):
        """切换模式处理"""
        try:
            self.layout_manager.toggle_mode(animated=True)

        except Exception as e:
            logger.error(f"切换模式处理失败: {e}")

    def on_mode_button_clicked(self, button):
        """模式按钮点击处理"""
        try:
            button_id = self.mode_group.id(button)

            if button_id == 0:  # 编辑模式
                self.layout_manager.switch_to_mode(LayoutMode.EDIT, animated=True)
            elif button_id == 1:  # 预览模式
                self.layout_manager.switch_to_mode(LayoutMode.PREVIEW, animated=True)

        except Exception as e:
            logger.error(f"模式按钮点击处理失败: {e}")

    def on_save_layout(self):
        """保存布局处理"""
        try:
            layout_state = self.layout_manager.save_current_layout()

            # 这里可以保存到文件或用户设置
            # 暂时只发送信号
            self.layout_saved.emit()

            # 显示保存成功消息
            self.show_status_message("布局已保存", 2000)

        except Exception as e:
            logger.error(f"保存布局处理失败: {e}")

    def on_restore_layout(self):
        """恢复布局处理"""
        try:
            # 恢复到默认编辑模式
            self.layout_manager.switch_to_mode(LayoutMode.EDIT, animated=True)

            self.layout_restored.emit()

            # 显示恢复成功消息
            self.show_status_message("布局已恢复", 2000)

        except Exception as e:
            logger.error(f"恢复布局处理失败: {e}")

    def on_layout_mode_changed(self, mode: str):
        """布局模式改变处理"""
        try:
            # 更新切换按钮
            layout_mode = LayoutMode.EDIT if mode == "edit" else LayoutMode.PREVIEW
            self.toggle_button.set_mode(layout_mode)

            # 更新模式按钮状态
            if mode == "edit":
                self.edit_mode_btn.setChecked(True)
                self.status_label.setText("当前模式: 编辑模式")
            else:
                self.preview_mode_btn.setChecked(True)
                self.status_label.setText("当前模式: 预览模式")

            # 发送模式改变信号
            self.mode_changed.emit(mode)

        except Exception as e:
            logger.error(f"布局模式改变处理失败: {e}")

    def on_transition_started(self, from_mode: str, to_mode: str):
        """过渡开始处理"""
        try:
            self.status_label.setText(f"切换中: {from_mode} → {to_mode}")

            # 禁用按钮防止重复点击
            self.set_buttons_enabled(False)

        except Exception as e:
            logger.error(f"过渡开始处理失败: {e}")

    def on_transition_finished(self, mode: str):
        """过渡完成处理"""
        try:
            mode_text = "编辑模式" if mode == "edit" else "预览模式"
            self.status_label.setText(f"当前模式: {mode_text}")

            # 重新启用按钮
            self.set_buttons_enabled(True)

        except Exception as e:
            logger.error(f"过渡完成处理失败: {e}")

    def set_buttons_enabled(self, enabled: bool):
        """设置按钮启用状态"""
        try:
            self.toggle_button.setEnabled(enabled)
            self.edit_mode_btn.setEnabled(enabled)
            self.preview_mode_btn.setEnabled(enabled)
            self.save_layout_btn.setEnabled(enabled)
            self.restore_layout_btn.setEnabled(enabled)

        except Exception as e:
            logger.error(f"设置按钮启用状态失败: {e}")

    def show_status_message(self, message: str, duration: int = 3000):
        """显示状态消息"""
        try:
            original_text = self.status_label.text()
            self.status_label.setText(message)

            # 定时器恢复原始文本
            QTimer.singleShot(duration, lambda: self.status_label.setText(original_text))

        except Exception as e:
            logger.error(f"显示状态消息失败: {e}")

    def get_current_mode(self) -> str:
        """获取当前模式"""
        return self.layout_manager.get_current_mode().value

    def set_mode(self, mode: str, animated: bool = True):
        """设置模式"""
        try:
            layout_mode = LayoutMode.EDIT if mode == "edit" else LayoutMode.PREVIEW
            self.layout_manager.switch_to_mode(layout_mode, animated)

        except Exception as e:
            logger.error(f"设置模式失败: {e}")


class DualModeLayoutWidget(QWidget):
    """双模式布局主组件"""

    mode_changed = pyqtSignal(str)

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window

        # 创建布局管理器
        self.layout_manager = DualModeLayoutManager(main_window)

        # 创建控制工具栏
        self.control_toolbar = ModeControlToolbar(self.layout_manager)

        self.setup_ui()
        self.setup_connections()

        logger.info("双模式布局主组件初始化完成")

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 添加控制工具栏
        layout.addWidget(self.control_toolbar)

        # 添加主内容区域（由主窗口管理）
        # 这里不添加具体内容，只是提供布局管理功能

    def setup_connections(self):
        """设置信号连接"""
        # 连接控制工具栏信号
        self.control_toolbar.mode_changed.connect(self.mode_changed.emit)

        # 连接布局管理器信号
        self.layout_manager.mode_changed.connect(self.mode_changed.emit)

    def register_widget(self, name: str, widget: QWidget):
        """注册组件"""
        self.layout_manager.register_widget(name, widget)

    def unregister_widget(self, name: str):
        """取消注册组件"""
        self.layout_manager.unregister_widget(name)

    def get_current_mode(self) -> str:
        """获取当前模式"""
        return self.layout_manager.get_current_mode().value

    def set_mode(self, mode: str, animated: bool = True):
        """设置模式"""
        self.control_toolbar.set_mode(mode, animated)

    def toggle_mode(self, animated: bool = True):
        """切换模式"""
        self.layout_manager.toggle_mode(animated)

    def get_layout_manager(self) -> DualModeLayoutManager:
        """获取布局管理器"""
        return self.layout_manager

    def get_control_toolbar(self) -> ModeControlToolbar:
        """获取控制工具栏"""
        return self.control_toolbar
