"""
AI Animation Studio - 信息重要性金字塔管理器
实现四层信息权重的重新分配，核心层、重要层、辅助层、补充层
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGroupBox, QPushButton, QProgressBar,
                             QScrollArea, QSplitter, QStackedWidget, QTabWidget,
                             QSizePolicy, QSpacerItem)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QPainter

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import json

from core.logger import get_logger

logger = get_logger("information_hierarchy_manager")


class InformationLevel(Enum):
    """信息重要性层级枚举"""
    CORE = "core"           # 核心层（最高权重）
    IMPORTANT = "important" # 重要层（高权重）
    AUXILIARY = "auxiliary" # 辅助层（中权重）
    SUPPLEMENTARY = "supplementary" # 补充层（低权重）


class HierarchyWeight:
    """信息层级权重配置"""
    
    CORE_WEIGHT = {
        'priority': 100,
        'font_size': 16,
        'font_weight': 'bold',
        'color': '#1565C0',
        'background': '#E3F2FD',
        'border': '3px solid #1565C0',
        'border_radius': '8px',
        'padding': '16px',
        'margin': '12px',
        'shadow': '0 4px 12px rgba(21, 101, 192, 0.3)',
        'min_height': '120px',
        'opacity': 1.0
    }
    
    IMPORTANT_WEIGHT = {
        'priority': 80,
        'font_size': 14,
        'font_weight': 'bold',
        'color': '#1976D2',
        'background': '#F3F4F6',
        'border': '2px solid #1976D2',
        'border_radius': '6px',
        'padding': '12px',
        'margin': '8px',
        'shadow': '0 2px 8px rgba(25, 118, 210, 0.2)',
        'min_height': '80px',
        'opacity': 0.95
    }
    
    AUXILIARY_WEIGHT = {
        'priority': 60,
        'font_size': 12,
        'font_weight': 'normal',
        'color': '#424242',
        'background': '#FAFAFA',
        'border': '1px solid #BDBDBD',
        'border_radius': '4px',
        'padding': '8px',
        'margin': '6px',
        'shadow': '0 1px 4px rgba(66, 66, 66, 0.1)',
        'min_height': '60px',
        'opacity': 0.85
    }
    
    SUPPLEMENTARY_WEIGHT = {
        'priority': 40,
        'font_size': 11,
        'font_weight': 'normal',
        'color': '#757575',
        'background': '#FFFFFF',
        'border': '1px solid #E0E0E0',
        'border_radius': '3px',
        'padding': '6px',
        'margin': '4px',
        'shadow': 'none',
        'min_height': '40px',
        'opacity': 0.75
    }


class HierarchicalWidget(QWidget):
    """层级化组件基类"""
    
    hierarchy_changed = pyqtSignal(str, str)  # 层级改变信号
    
    def __init__(self, widget_id: str, title: str, level: InformationLevel, content_widget: QWidget = None):
        super().__init__()
        self.widget_id = widget_id
        self.title = title
        self.level = level
        self.content_widget = content_widget
        self.is_focused = False
        self.is_collapsed = False
        
        self.setup_ui()
        self.apply_hierarchy_weight()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 主容器
        self.main_container = QFrame()
        self.main_container.setObjectName("hierarchical_container")
        
        container_layout = QVBoxLayout(self.main_container)
        
        # 标题栏
        self.title_bar = self.create_title_bar()
        container_layout.addWidget(self.title_bar)
        
        # 内容区域
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        if self.content_widget:
            self.content_layout.addWidget(self.content_widget)
        
        container_layout.addWidget(self.content_area)
        
        layout.addWidget(self.main_container)
    
    def create_title_bar(self) -> QWidget:
        """创建标题栏"""
        title_bar = QFrame()
        title_bar.setFixedHeight(32)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # 层级指示器
        level_indicator = QLabel(self.get_level_indicator())
        level_indicator.setFont(QFont("Segoe UI Emoji", 12))
        layout.addWidget(level_indicator)
        
        # 标题
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # 折叠按钮
        self.collapse_btn = QPushButton("−")
        self.collapse_btn.setFixedSize(20, 20)
        self.collapse_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #BDBDBD;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
            }
        """)
        self.collapse_btn.clicked.connect(self.toggle_collapse)
        layout.addWidget(self.collapse_btn)
        
        return title_bar
    
    def get_level_indicator(self) -> str:
        """获取层级指示器"""
        indicators = {
            InformationLevel.CORE: "🔴",
            InformationLevel.IMPORTANT: "🟡",
            InformationLevel.AUXILIARY: "🟢",
            InformationLevel.SUPPLEMENTARY: "⚪"
        }
        return indicators.get(self.level, "⚪")
    
    def apply_hierarchy_weight(self):
        """应用层级权重"""
        weight_map = {
            InformationLevel.CORE: HierarchyWeight.CORE_WEIGHT,
            InformationLevel.IMPORTANT: HierarchyWeight.IMPORTANT_WEIGHT,
            InformationLevel.AUXILIARY: HierarchyWeight.AUXILIARY_WEIGHT,
            InformationLevel.SUPPLEMENTARY: HierarchyWeight.SUPPLEMENTARY_WEIGHT
        }
        
        weight = weight_map.get(self.level, HierarchyWeight.AUXILIARY_WEIGHT)
        
        # 应用样式
        style = f"""
        QFrame#hierarchical_container {{
            background-color: {weight['background']};
            border: {weight['border']};
            border-radius: {weight['border_radius']};
            margin: {weight['margin']};
            min-height: {weight['min_height']};
        }}
        """
        
        if weight['shadow'] != 'none':
            style += f"""
            QFrame#hierarchical_container {{
                /* box-shadow: {weight['shadow']}; */
            }}
            """
        
        self.main_container.setStyleSheet(style)
        
        # 设置内容边距
        padding = int(weight['padding'].replace('px', ''))
        self.content_layout.setContentsMargins(padding, padding, padding, padding)
        
        # 设置透明度
        self.setWindowOpacity(weight['opacity'])
        
        # 设置最小高度
        min_height = int(weight['min_height'].replace('px', ''))
        self.setMinimumHeight(min_height)
    
    def toggle_collapse(self):
        """切换折叠状态"""
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            self.content_area.setVisible(False)
            self.collapse_btn.setText("+")
        else:
            self.content_area.setVisible(True)
            self.collapse_btn.setText("−")
        
        self.hierarchy_changed.emit(self.widget_id, "collapsed" if self.is_collapsed else "expanded")
    
    def set_focus_state(self, focused: bool):
        """设置焦点状态"""
        self.is_focused = focused
        
        if focused:
            # 添加焦点样式
            current_style = self.main_container.styleSheet()
            focus_style = current_style + """
            QFrame#hierarchical_container {
                border-width: 3px;
                box-shadow: 0 0 12px rgba(21, 101, 192, 0.5);
            }
            """
            self.main_container.setStyleSheet(focus_style)
        else:
            # 恢复原始样式
            self.apply_hierarchy_weight()
    
    def update_level(self, new_level: InformationLevel):
        """更新层级"""
        old_level = self.level
        self.level = new_level
        self.apply_hierarchy_weight()
        
        # 更新层级指示器
        if hasattr(self, 'title_bar'):
            level_indicator = self.title_bar.findChild(QLabel)
            if level_indicator:
                level_indicator.setText(self.get_level_indicator())
        
        self.hierarchy_changed.emit(self.widget_id, f"level_changed:{old_level.value}:{new_level.value}")


class InformationHierarchyManager:
    """信息重要性金字塔管理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.hierarchical_widgets: Dict[str, HierarchicalWidget] = {}
        self.level_assignments: Dict[str, InformationLevel] = {}
        self.current_focus_widget = None
        
        self.initialize_hierarchy_assignments()
        self.apply_information_hierarchy()
        
        logger.info("信息重要性金字塔管理器初始化完成")
    
    def initialize_hierarchy_assignments(self):
        """初始化层级分配"""
        # 根据分析报告定义的四层信息权重
        self.level_assignments = {
            # 核心层（最高权重）- 当前时间段、动画描述输入、AI生成状态
            'current_time_segment': InformationLevel.CORE,
            'animation_description_input': InformationLevel.CORE,
            'ai_generation_status': InformationLevel.CORE,
            'primary_toolbar': InformationLevel.CORE,
            
            # 重要层（高权重）- 音频控制、舞台画布、时间轴
            'audio_control': InformationLevel.IMPORTANT,
            'stage_canvas': InformationLevel.IMPORTANT,
            'timeline': InformationLevel.IMPORTANT,
            'workflow_indicator': InformationLevel.IMPORTANT,
            
            # 辅助层（中权重）- 元素列表、属性面板、预览窗口
            'elements_list': InformationLevel.AUXILIARY,
            'properties_panel': InformationLevel.AUXILIARY,
            'preview_window': InformationLevel.AUXILIARY,
            'ai_generator': InformationLevel.AUXILIARY,
            
            # 补充层（低权重）- 库管理、规则库、系统设置
            'library_manager': InformationLevel.SUPPLEMENTARY,
            'rules_library': InformationLevel.SUPPLEMENTARY,
            'system_settings': InformationLevel.SUPPLEMENTARY,
            'status_bar': InformationLevel.SUPPLEMENTARY
        }
    
    def apply_information_hierarchy(self):
        """应用信息层级"""
        try:
            # 获取主窗口的各个组件
            self.wrap_existing_widgets()
            
            # 重新排列布局优先级
            self.rearrange_layout_priority()
            
            # 设置焦点管理
            self.setup_focus_management()
            
        except Exception as e:
            logger.error(f"应用信息层级失败: {e}")
    
    def wrap_existing_widgets(self):
        """包装现有组件"""
        try:
            # 包装主要组件
            widget_mappings = {
                'primary_toolbar': self.get_primary_toolbar(),
                'audio_control': self.get_audio_control_widget(),
                'stage_canvas': self.get_stage_canvas_widget(),
                'timeline': self.get_timeline_widget(),
                'elements_list': self.get_elements_list_widget(),
                'properties_panel': self.get_properties_panel_widget(),
                'preview_window': self.get_preview_window_widget(),
                'ai_generator': self.get_ai_generator_widget(),
                'library_manager': self.get_library_manager_widget(),
                'rules_library': self.get_rules_library_widget()
            }
            
            for widget_id, widget in widget_mappings.items():
                if widget and widget_id in self.level_assignments:
                    level = self.level_assignments[widget_id]
                    title = self.get_widget_title(widget_id)
                    
                    hierarchical_widget = HierarchicalWidget(widget_id, title, level, widget)
                    hierarchical_widget.hierarchy_changed.connect(self.on_hierarchy_changed)
                    
                    self.hierarchical_widgets[widget_id] = hierarchical_widget
                    
                    # 替换原有组件
                    self.replace_widget_in_layout(widget, hierarchical_widget)
            
        except Exception as e:
            logger.error(f"包装现有组件失败: {e}")
    
    def get_primary_toolbar(self) -> QWidget:
        """获取主要工具栏"""
        try:
            if (hasattr(self.main_window, 'visual_flow_manager') and
                self.main_window.visual_flow_manager is not None and
                hasattr(self.main_window.visual_flow_manager, 'primary_toolbar')):
                return self.main_window.visual_flow_manager.primary_toolbar

            # 备选方案：尝试从主窗口获取工具栏
            if hasattr(self.main_window, 'toolbar'):
                return self.main_window.toolbar
            elif hasattr(self.main_window, 'main_toolbar'):
                return self.main_window.main_toolbar

        except Exception as e:
            print(f"获取主要工具栏失败: {e}")

        return None
    
    def get_audio_control_widget(self) -> QWidget:
        """获取音频控制组件"""
        if hasattr(self.main_window, 'audio_widget'):
            return self.main_window.audio_widget
        return None
    
    def get_stage_canvas_widget(self) -> QWidget:
        """获取舞台画布组件"""
        if hasattr(self.main_window, 'stage_widget'):
            return self.main_window.stage_widget
        return None
    
    def get_timeline_widget(self) -> QWidget:
        """获取时间轴组件"""
        if hasattr(self.main_window, 'timeline_widget'):
            return self.main_window.timeline_widget
        return None
    
    def get_elements_list_widget(self) -> QWidget:
        """获取元素列表组件"""
        if hasattr(self.main_window, 'elements_widget'):
            return self.main_window.elements_widget
        return None
    
    def get_properties_panel_widget(self) -> QWidget:
        """获取属性面板组件"""
        if hasattr(self.main_window, 'properties_widget'):
            return self.main_window.properties_widget
        return None
    
    def get_preview_window_widget(self) -> QWidget:
        """获取预览窗口组件"""
        if hasattr(self.main_window, 'preview_widget'):
            return self.main_window.preview_widget
        return None
    
    def get_ai_generator_widget(self) -> QWidget:
        """获取AI生成器组件"""
        if hasattr(self.main_window, 'ai_generator_widget'):
            return self.main_window.ai_generator_widget
        return None
    
    def get_library_manager_widget(self) -> QWidget:
        """获取库管理器组件"""
        if hasattr(self.main_window, 'library_manager_widget'):
            return self.main_window.library_manager_widget
        return None
    
    def get_rules_library_widget(self) -> QWidget:
        """获取规则库组件"""
        if hasattr(self.main_window, 'rules_widget'):
            return self.main_window.rules_widget
        return None
    
    def get_widget_title(self, widget_id: str) -> str:
        """获取组件标题"""
        titles = {
            'primary_toolbar': '主要工具栏',
            'audio_control': '音频控制',
            'stage_canvas': '舞台画布',
            'timeline': '时间轴',
            'elements_list': '元素列表',
            'properties_panel': '属性面板',
            'preview_window': '预览窗口',
            'ai_generator': 'AI生成器',
            'library_manager': '库管理器',
            'rules_library': '规则库'
        }
        return titles.get(widget_id, widget_id)
    
    def replace_widget_in_layout(self, old_widget: QWidget, new_widget: QWidget):
        """在布局中替换组件"""
        try:
            parent = old_widget.parent()
            if parent and hasattr(parent, 'layout') and parent.layout():
                layout = parent.layout()
                
                # 找到旧组件的位置
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if item and item.widget() == old_widget:
                        # 移除旧组件
                        layout.removeWidget(old_widget)
                        old_widget.setParent(None)
                        
                        # 插入新组件
                        layout.insertWidget(i, new_widget)
                        break
                        
        except Exception as e:
            logger.error(f"替换组件失败: {e}")
    
    def rearrange_layout_priority(self):
        """重新排列布局优先级"""
        try:
            # 根据层级权重重新排列组件顺序
            core_widgets = []
            important_widgets = []
            auxiliary_widgets = []
            supplementary_widgets = []
            
            for widget_id, widget in self.hierarchical_widgets.items():
                level = self.level_assignments.get(widget_id, InformationLevel.AUXILIARY)
                
                if level == InformationLevel.CORE:
                    core_widgets.append(widget)
                elif level == InformationLevel.IMPORTANT:
                    important_widgets.append(widget)
                elif level == InformationLevel.AUXILIARY:
                    auxiliary_widgets.append(widget)
                else:
                    supplementary_widgets.append(widget)
            
            # 设置Z-order（显示层次）
            z_order = 1000
            for widget_list in [core_widgets, important_widgets, auxiliary_widgets, supplementary_widgets]:
                for widget in widget_list:
                    widget.raise_()
                    z_order -= 10
                    
        except Exception as e:
            logger.error(f"重新排列布局优先级失败: {e}")
    
    def setup_focus_management(self):
        """设置焦点管理"""
        # 默认焦点设置到核心层组件
        core_widgets = [w for w_id, w in self.hierarchical_widgets.items() 
                       if self.level_assignments.get(w_id) == InformationLevel.CORE]
        
        if core_widgets:
            self.set_focus_widget(core_widgets[0])
    
    def set_focus_widget(self, widget: HierarchicalWidget):
        """设置焦点组件"""
        # 清除之前的焦点
        if self.current_focus_widget:
            self.current_focus_widget.set_focus_state(False)
        
        # 设置新焦点
        self.current_focus_widget = widget
        if widget:
            widget.set_focus_state(True)
    
    def on_hierarchy_changed(self, widget_id: str, change_type: str):
        """层级改变处理"""
        logger.info(f"层级改变: {widget_id} - {change_type}")
        
        if change_type.startswith("level_changed"):
            # 处理层级变更
            parts = change_type.split(":")
            if len(parts) == 3:
                old_level, new_level = parts[1], parts[2]
                logger.info(f"组件 {widget_id} 层级从 {old_level} 变更为 {new_level}")
    
    def update_widget_level(self, widget_id: str, new_level: InformationLevel):
        """更新组件层级"""
        if widget_id in self.hierarchical_widgets:
            self.level_assignments[widget_id] = new_level
            self.hierarchical_widgets[widget_id].update_level(new_level)
            
            # 重新排列布局优先级
            self.rearrange_layout_priority()
    
    def get_hierarchy_summary(self) -> dict:
        """获取层级摘要"""
        summary = {
            'total_widgets': len(self.hierarchical_widgets),
            'level_distribution': {
                'core': 0,
                'important': 0,
                'auxiliary': 0,
                'supplementary': 0
            },
            'current_focus': self.current_focus_widget.widget_id if self.current_focus_widget else None,
            'collapsed_widgets': []
        }
        
        for widget_id, level in self.level_assignments.items():
            if level == InformationLevel.CORE:
                summary['level_distribution']['core'] += 1
            elif level == InformationLevel.IMPORTANT:
                summary['level_distribution']['important'] += 1
            elif level == InformationLevel.AUXILIARY:
                summary['level_distribution']['auxiliary'] += 1
            else:
                summary['level_distribution']['supplementary'] += 1
        
        # 统计折叠的组件
        for widget_id, widget in self.hierarchical_widgets.items():
            if widget.is_collapsed:
                summary['collapsed_widgets'].append(widget_id)
        
        return summary
