"""
AI Animation Studio - 视线流动优化管理器
实现F型扫描模式适配的界面布局，优化用户视线流动和信息层次
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGroupBox, QPushButton, QProgressBar,
                             QScrollArea, QSplitter, QStackedWidget, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QPainter

from enum import Enum
from typing import Dict, List, Optional, Tuple
import json

from core.logger import get_logger

logger = get_logger("visual_flow_manager")


class ScanZone(Enum):
    """F型扫描区域枚举"""
    TOP_LEFT_START = "top_left_start"           # 左上角起始点
    TOP_HORIZONTAL = "top_horizontal"           # 顶部水平扫描
    LEFT_VERTICAL = "left_vertical"             # 左侧垂直扫描
    CENTER_FOCUS = "center_focus"               # 中央聚焦区域
    BOTTOM_STATUS = "bottom_status"             # 底部状态信息


class InformationLevel(Enum):
    """信息重要性层级枚举"""
    CORE = "core"           # 核心层（最高权重）
    IMPORTANT = "important" # 重要层（高权重）
    AUXILIARY = "auxiliary" # 辅助层（中权重）
    SECONDARY = "secondary" # 次要层（低权重）


class VisualWeight:
    """视觉权重配置"""
    
    CORE_WEIGHT = {
        'font_size': 14,
        'font_weight': 'bold',
        'color': '#2C5AA0',
        'background': '#E3F2FD',
        'border': '2px solid #2C5AA0',
        'padding': '12px',
        'margin': '8px'
    }
    
    IMPORTANT_WEIGHT = {
        'font_size': 12,
        'font_weight': 'bold',
        'color': '#1976D2',
        'background': '#F3F4F6',
        'border': '1px solid #1976D2',
        'padding': '10px',
        'margin': '6px'
    }
    
    AUXILIARY_WEIGHT = {
        'font_size': 11,
        'font_weight': 'normal',
        'color': '#424242',
        'background': '#FAFAFA',
        'border': '1px solid #E0E0E0',
        'padding': '8px',
        'margin': '4px'
    }
    
    SECONDARY_WEIGHT = {
        'font_size': 10,
        'font_weight': 'normal',
        'color': '#757575',
        'background': '#FFFFFF',
        'border': '1px solid #F0F0F0',
        'padding': '6px',
        'margin': '2px'
    }


class FTypeLayoutZone(QWidget):
    """F型布局区域组件"""
    
    zone_activated = pyqtSignal(str)  # 区域激活信号
    
    def __init__(self, zone_type: ScanZone, title: str, info_level: InformationLevel):
        super().__init__()
        self.zone_type = zone_type
        self.title = title
        self.info_level = info_level
        self.is_active = False
        self.child_widgets = []
        
        self.setup_ui()
        self.apply_visual_weight()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 区域标题（调试用，生产环境可隐藏）
        if logger.level <= 10:  # DEBUG级别时显示
            title_label = QLabel(f"[{self.zone_type.value}] {self.title}")
            title_label.setFont(QFont("Microsoft YaHei", 8))
            title_label.setStyleSheet("color: #999; background: transparent;")
            layout.addWidget(title_label)
        
        # 内容容器
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        layout.addWidget(self.content_widget)
    
    def apply_visual_weight(self):
        """应用视觉权重"""
        # 避免使用枚举作为字典键，防止递归哈希问题
        if self.info_level == InformationLevel.CORE:
            weight = VisualWeight.CORE_WEIGHT
        elif self.info_level == InformationLevel.IMPORTANT:
            weight = VisualWeight.IMPORTANT_WEIGHT
        elif self.info_level == InformationLevel.SECONDARY:
            weight = VisualWeight.SECONDARY_WEIGHT
        else:
            weight = VisualWeight.AUXILIARY_WEIGHT
        
        style = f"""
        FTypeLayoutZone {{
            background-color: {weight['background']};
            border: {weight['border']};
            border-radius: 4px;
            margin: {weight['margin']};
        }}
        """
        
        self.setStyleSheet(style)
        self.content_layout.setContentsMargins(
            int(weight['padding'].replace('px', '')),
            int(weight['padding'].replace('px', '')),
            int(weight['padding'].replace('px', '')),
            int(weight['padding'].replace('px', ''))
        )
    
    def add_widget(self, widget: QWidget):
        """添加子组件"""
        self.child_widgets.append(widget)
        self.content_layout.addWidget(widget)
    
    def activate_zone(self):
        """激活区域"""
        self.is_active = True
        self.zone_activated.emit(self.zone_type.value)
        
        # 添加激活状态样式
        current_style = self.styleSheet()
        active_style = current_style + """
        FTypeLayoutZone {
            box-shadow: 0 0 8px rgba(44, 90, 160, 0.3);
            border-color: #2C5AA0;
        }
        """
        self.setStyleSheet(active_style)
    
    def deactivate_zone(self):
        """取消激活区域"""
        self.is_active = False
        self.apply_visual_weight()  # 恢复原始样式


class WorkflowStepIndicator(QWidget):
    """工作流程步骤指示器"""
    
    step_clicked = pyqtSignal(int)  # 步骤点击信号
    
    def __init__(self):
        super().__init__()
        self.current_step = 1
        self.steps = [
            {"id": 1, "title": "音频导入", "icon": "🎵", "description": "导入旁白音频文件"},
            {"id": 2, "title": "时间段划分", "icon": "⏱️", "description": "划分动画时间段"},
            {"id": 3, "title": "描述输入", "icon": "📝", "description": "输入动画描述"},
            {"id": 4, "title": "AI生成", "icon": "🤖", "description": "生成动画方案"},
            {"id": 5, "title": "预览调整", "icon": "👁️", "description": "预览和调整"},
            {"id": 6, "title": "导出完成", "icon": "📤", "description": "导出最终作品"}
        ]
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # 标题
        title_label = QLabel("工作流程")
        title_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2C5AA0; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # 步骤列表
        self.step_widgets = []
        for step in self.steps:
            step_widget = self.create_step_widget(step)
            self.step_widgets.append(step_widget)
            layout.addWidget(step_widget)
        
        layout.addStretch()
        
        # 更新当前步骤显示
        self.update_current_step(self.current_step)
    
    def create_step_widget(self, step: dict) -> QWidget:
        """创建步骤组件"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.Box)
        widget.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)
        
        # 步骤图标
        icon_label = QLabel(step["icon"])
        icon_label.setFont(QFont("Segoe UI Emoji", 14))
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # 步骤信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        title_label = QLabel(step["title"])
        title_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        info_layout.addWidget(title_label)
        
        desc_label = QLabel(step["description"])
        desc_label.setFont(QFont("Microsoft YaHei", 8))
        desc_label.setStyleSheet("color: #666;")
        info_layout.addWidget(desc_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # 步骤状态指示
        status_label = QLabel()
        status_label.setFixedSize(16, 16)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status_label)
        
        # 存储步骤信息
        widget.step_id = step["id"]
        widget.status_label = status_label
        
        # 点击事件
        widget.mousePressEvent = lambda event, step_id=step["id"]: self.on_step_clicked(step_id)
        
        return widget
    
    def on_step_clicked(self, step_id: int):
        """步骤点击处理"""
        self.step_clicked.emit(step_id)
    
    def update_current_step(self, step_id: int):
        """更新当前步骤"""
        self.current_step = step_id
        
        for i, widget in enumerate(self.step_widgets):
            step_num = i + 1
            status_label = widget.status_label
            
            if step_num < step_id:
                # 已完成步骤
                status_label.setText("✓")
                status_label.setStyleSheet("""
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 8px;
                    font-weight: bold;
                """)
                widget.setStyleSheet("""
                    QFrame {
                        background-color: #E8F5E8;
                        border: 1px solid #4CAF50;
                        border-radius: 4px;
                    }
                """)
            elif step_num == step_id:
                # 当前步骤
                status_label.setText("●")
                status_label.setStyleSheet("""
                    background-color: #2C5AA0;
                    color: white;
                    border-radius: 8px;
                    font-weight: bold;
                """)
                widget.setStyleSheet("""
                    QFrame {
                        background-color: #E3F2FD;
                        border: 2px solid #2C5AA0;
                        border-radius: 4px;
                    }
                """)
            else:
                # 未开始步骤
                status_label.setText("○")
                status_label.setStyleSheet("""
                    background-color: #E0E0E0;
                    color: #999;
                    border-radius: 8px;
                """)
                widget.setStyleSheet("""
                    QFrame {
                        background-color: #FAFAFA;
                        border: 1px solid #E0E0E0;
                        border-radius: 4px;
                    }
                """)


class PrimaryToolbar(QWidget):
    """主要工具栏（顶部水平扫描区域）"""
    
    action_triggered = pyqtSignal(str)  # 动作触发信号
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(12)
        
        # 主要操作按钮（按F型扫描顺序排列）
        primary_actions = [
            {"id": "import_audio", "text": "🎵 导入音频", "shortcut": "Ctrl+I", "primary": True},
            {"id": "ai_generate", "text": "🤖 AI生成", "shortcut": "Ctrl+G", "primary": True},
            {"id": "preview", "text": "👁️ 预览", "shortcut": "Space", "primary": True},
            {"id": "export", "text": "📤 导出", "shortcut": "Ctrl+E", "primary": True}
        ]
        
        # 添加主要按钮
        for action in primary_actions:
            btn = self.create_action_button(action)
            layout.addWidget(btn)
        
        # 分隔符
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("color: #E0E0E0;")
        layout.addWidget(separator)
        
        # 次要操作按钮
        secondary_actions = [
            {"id": "save", "text": "💾 保存", "shortcut": "Ctrl+S", "primary": False},
            {"id": "undo", "text": "↶ 撤销", "shortcut": "Ctrl+Z", "primary": False},
            {"id": "redo", "text": "↷ 重做", "shortcut": "Ctrl+Y", "primary": False}
        ]
        
        for action in secondary_actions:
            btn = self.create_action_button(action)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # 项目信息（右侧）
        self.project_info = QLabel("新项目")
        self.project_info.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        self.project_info.setStyleSheet("color: #2C5AA0; padding: 4px 8px;")
        layout.addWidget(self.project_info)
    
    def create_action_button(self, action: dict) -> QPushButton:
        """创建动作按钮"""
        btn = QPushButton(action["text"])
        btn.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold if action["primary"] else QFont.Weight.Normal))
        
        if action["primary"]:
            # 主要按钮样式
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2C5AA0;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
            """)
        else:
            # 次要按钮样式
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F5F5F5;
                    color: #424242;
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #EEEEEE;
                    border-color: #BDBDBD;
                }
                QPushButton:pressed {
                    background-color: #E0E0E0;
                }
            """)
        
        # 设置工具提示
        if action.get("shortcut"):
            btn.setToolTip(f"{action['text']} ({action['shortcut']})")
        
        # 连接信号
        btn.clicked.connect(lambda checked, action_id=action["id"]: self.action_triggered.emit(action_id))
        
        return btn
    
    def update_project_info(self, project_name: str, status: str = ""):
        """更新项目信息"""
        if status:
            self.project_info.setText(f"{project_name} - {status}")
        else:
            self.project_info.setText(project_name)


class VisualFlowManager:
    """视线流动优化管理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.zones: Dict[str, FTypeLayoutZone] = {}  # 使用字符串作为键避免递归哈希
        self.current_focus_zone = None
        self.workflow_indicator = None
        self.primary_toolbar = None

        # 添加状态锁防止递归调用
        self._is_updating = False

        self.initialize_f_type_layout()
        logger.info("视线流动优化管理器初始化完成")
    
    def initialize_f_type_layout(self):
        """初始化F型布局"""
        try:
            # 创建F型扫描区域
            self.create_scan_zones()
            
            # 应用F型布局到主窗口
            self.apply_f_type_layout()
            
            # 设置视线流动引导
            self.setup_visual_flow_guidance()
            
        except Exception as e:
            logger.error(f"初始化F型布局失败: {e}")
    
    def create_scan_zones(self):
        """创建F型扫描区域"""
        zone_configs = [
            (ScanZone.TOP_LEFT_START, "项目信息区", InformationLevel.CORE),
            (ScanZone.TOP_HORIZONTAL, "主要工具栏", InformationLevel.CORE),
            (ScanZone.LEFT_VERTICAL, "工作流程指示", InformationLevel.IMPORTANT),
            (ScanZone.CENTER_FOCUS, "中央工作区", InformationLevel.CORE),
            (ScanZone.BOTTOM_STATUS, "状态信息区", InformationLevel.AUXILIARY)
        ]
        
        for zone_type, title, info_level in zone_configs:
            zone = FTypeLayoutZone(zone_type, title, info_level)
            zone.zone_activated.connect(self.on_zone_activated)
            self.zones[zone_type.value] = zone  # 使用枚举的值作为字符串键
    
    def apply_f_type_layout(self):
        """应用F型布局到主窗口"""
        try:
            # 获取主窗口的中央组件
            central_widget = self.main_window.centralWidget()
            if not central_widget:
                logger.warning("主窗口没有中央组件")
                return
            
            # 创建新的F型布局结构
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # 1. 顶部区域（左上角起始点 + 顶部水平扫描）
            top_layout = QHBoxLayout()
            top_layout.setContentsMargins(0, 0, 0, 0)
            top_layout.setSpacing(0)
            
            # 左上角起始点（项目信息）
            top_left_zone = self.zones[ScanZone.TOP_LEFT_START]
            top_left_zone.setFixedWidth(200)
            top_layout.addWidget(top_left_zone)
            
            # 顶部水平扫描（主要工具栏）
            top_horizontal_zone = self.zones[ScanZone.TOP_HORIZONTAL]
            self.primary_toolbar = PrimaryToolbar()
            self.primary_toolbar.action_triggered.connect(self.on_primary_action_triggered)
            top_horizontal_zone.add_widget(self.primary_toolbar)
            top_layout.addWidget(top_horizontal_zone)
            
            main_layout.addLayout(top_layout)
            
            # 2. 中间区域（左侧垂直扫描 + 中央聚焦区域）
            middle_layout = QHBoxLayout()
            middle_layout.setContentsMargins(0, 0, 0, 0)
            middle_layout.setSpacing(0)
            
            # 左侧垂直扫描（工作流程指示）
            left_vertical_zone = self.zones[ScanZone.LEFT_VERTICAL]
            left_vertical_zone.setFixedWidth(200)
            self.workflow_indicator = WorkflowStepIndicator()
            self.workflow_indicator.step_clicked.connect(self.on_workflow_step_clicked)
            left_vertical_zone.add_widget(self.workflow_indicator)
            middle_layout.addWidget(left_vertical_zone)
            
            # 中央聚焦区域（主要工作内容）
            center_focus_zone = self.zones[ScanZone.CENTER_FOCUS]
            
            # 将原有的主分割器添加到中央区域
            if hasattr(self.main_window, 'main_splitter'):
                center_focus_zone.add_widget(self.main_window.main_splitter)
            
            middle_layout.addWidget(center_focus_zone)
            
            main_layout.addLayout(middle_layout)
            
            # 3. 底部状态信息区
            bottom_status_zone = self.zones[ScanZone.BOTTOM_STATUS]
            bottom_status_zone.setFixedHeight(30)
            
            # 将状态栏添加到底部区域
            if hasattr(self.main_window, 'status_notification_manager'):
                status_widget = self.main_window.status_notification_manager.status_bar_widget
                if status_widget:
                    bottom_status_zone.add_widget(status_widget)
            
            main_layout.addWidget(bottom_status_zone)
            
            # 应用新布局
            new_central_widget = QWidget()
            new_central_widget.setLayout(main_layout)
            self.main_window.setCentralWidget(new_central_widget)
            
            logger.info("F型布局应用成功")
            
        except Exception as e:
            logger.error(f"应用F型布局失败: {e}")
    
    def setup_visual_flow_guidance(self):
        """设置视线流动引导"""
        # 设置初始焦点区域
        self.set_focus_zone(ScanZone.TOP_LEFT_START)
        
        # 设置区域切换动画
        self.setup_zone_transitions()
    
    def setup_zone_transitions(self):
        """设置区域切换动画"""
        # 这里可以添加区域间的过渡动画
        pass
    
    def on_zone_activated(self, zone_type):
        """区域激活处理"""
        # 如果正在更新中，则直接返回，避免重入
        if self._is_updating:
            return

        try:
            self._is_updating = True  # 上锁

            # 检查zone_type的类型，避免递归
            if isinstance(zone_type, ScanZone):
                zone_enum = zone_type
            elif isinstance(zone_type, str):
                # 通过字符串值查找对应的枚举
                zone_enum = None
                for scan_zone in ScanZone:
                    if scan_zone.value == zone_type:
                        zone_enum = scan_zone
                        break
                if zone_enum is None:
                    print(f"警告: 未知的区域类型: {zone_type}")  # 使用print避免日志递归
                    return
            else:
                print(f"警告: 无效的区域类型参数: {zone_type} (类型: {type(zone_type)})")
                return

            self.set_focus_zone(zone_enum)
            print(f"调试: 区域激活: {zone_type}")  # 使用print避免日志递归

        except Exception as e:
            print(f"错误: 区域激活处理失败: {e}")  # 使用print避免日志递归
        finally:
            # 确保在函数退出前，无论是否异常，都解锁
            self._is_updating = False
    
    def set_focus_zone(self, zone: ScanZone):
        """设置焦点区域"""
        # 如果正在更新中，则直接返回，避免重入
        if self._is_updating:
            return

        try:
            self._is_updating = True  # 上锁

            zone_key = zone.value if hasattr(zone, 'value') else str(zone)

            # 取消之前的焦点
            if self.current_focus_zone and self.current_focus_zone in self.zones:
                self.zones[self.current_focus_zone].deactivate_zone()

            # 设置新焦点
            self.current_focus_zone = zone_key
            if zone_key in self.zones:
                self.zones[zone_key].activate_zone()

        except Exception as e:
            print(f"错误: 设置焦点区域失败: {e}")  # 使用print避免日志递归
        finally:
            # 确保在函数退出前，无论是否异常，都解锁
            self._is_updating = False
    
    def on_primary_action_triggered(self, action_id: str):
        """主要动作触发处理"""
        logger.info(f"主要动作触发: {action_id}")
        
        # 根据动作类型设置相应的焦点区域
        action_zone_map = {
            "import_audio": ScanZone.CENTER_FOCUS,
            "ai_generate": ScanZone.CENTER_FOCUS,
            "preview": ScanZone.CENTER_FOCUS,
            "export": ScanZone.BOTTOM_STATUS
        }
        
        if action_id in action_zone_map:
            self.set_focus_zone(action_zone_map[action_id])
        
        # 转发到主窗口处理
        if hasattr(self.main_window, 'handle_primary_action'):
            self.main_window.handle_primary_action(action_id)
    
    def on_workflow_step_clicked(self, step_id: int):
        """工作流程步骤点击处理"""
        logger.info(f"工作流程步骤点击: {step_id}")
        
        # 更新工作流程指示器
        if self.workflow_indicator:
            self.workflow_indicator.update_current_step(step_id)
        
        # 设置焦点到中央区域
        self.set_focus_zone(ScanZone.CENTER_FOCUS)
        
        # 转发到主窗口处理
        if hasattr(self.main_window, 'handle_workflow_step'):
            self.main_window.handle_workflow_step(step_id)
    
    def update_project_info(self, project_name: str, status: str = ""):
        """更新项目信息"""
        if self.primary_toolbar:
            self.primary_toolbar.update_project_info(project_name, status)
    
    def update_workflow_step(self, step_id: int):
        """更新工作流程步骤"""
        if self.workflow_indicator:
            self.workflow_indicator.update_current_step(step_id)
    
    def get_visual_flow_summary(self) -> dict:
        """获取视线流动摘要"""
        return {
            'current_focus_zone': self.current_focus_zone.value if self.current_focus_zone else None,
            'total_zones': len(self.zones),
            'workflow_step': self.workflow_indicator.current_step if self.workflow_indicator else 1,
            'f_type_layout_active': True
        }
