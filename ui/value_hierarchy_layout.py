"""
AI Animation Studio - 价值层次驱动的布局管理器
实现清晰的设计价值层次和核心工作流程优先级体系
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QTabWidget, QStackedWidget, QFrame, QLabel,
                             QPushButton, QProgressBar, QGroupBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPalette, QColor

from core.logger import get_logger

logger = get_logger("value_hierarchy_layout")


class WorkflowPriorityIndicator(QWidget):
    """工作流程优先级指示器"""
    
    step_activated = pyqtSignal(int)  # 步骤激活信号
    
    def __init__(self):
        super().__init__()
        self.current_step = 0
        self.steps = [
            ("1. 音频导入", "导入旁白音频文件"),
            ("2. 时间段标记", "标记关键时间点"),
            ("3. 动画描述", "描述动画内容"),
            ("4. AI生成", "生成动画方案"),
            ("5. 预览调整", "预览和微调"),
            ("6. 导出完成", "导出最终作品")
        ]
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        
        # 标题
        title = QLabel("🎯 核心工作流程")
        title.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #2C5AA0; padding: 5px;")
        layout.addWidget(title)
        
        # 步骤指示器
        self.step_widgets = []
        for i, (step_name, step_desc) in enumerate(self.steps):
            step_widget = self.create_step_widget(i, step_name, step_desc)
            self.step_widgets.append(step_widget)
            layout.addWidget(step_widget)
        
        layout.addStretch()
        
        # 设置样式
        self.setStyleSheet("""
            WorkflowPriorityIndicator {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
        """)
    
    def create_step_widget(self, index: int, name: str, description: str) -> QWidget:
        """创建步骤组件"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.Box)
        widget.setLineWidth(1)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 6, 8, 6)
        
        # 步骤名称
        name_label = QLabel(name)
        name_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        layout.addWidget(name_label)
        
        # 步骤描述
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Microsoft YaHei", 8))
        desc_label.setStyleSheet("color: #6c757d;")
        layout.addWidget(desc_label)
        
        # 进度指示
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setValue(0)
        progress.setMaximumHeight(4)
        layout.addWidget(progress)
        
        # 设置初始样式
        self.update_step_style(widget, index, False)
        
        # 点击事件
        widget.mousePressEvent = lambda event: self.step_activated.emit(index)
        
        return widget
    
    def update_step_style(self, widget: QWidget, index: int, is_active: bool):
        """更新步骤样式"""
        if is_active:
            widget.setStyleSheet("""
                QFrame {
                    background-color: #e3f2fd;
                    border: 2px solid #2C5AA0;
                    border-radius: 6px;
                }
                QLabel {
                    color: #2C5AA0;
                }
            """)
        elif index < self.current_step:
            widget.setStyleSheet("""
                QFrame {
                    background-color: #e8f5e8;
                    border: 1px solid #4caf50;
                    border-radius: 6px;
                }
                QLabel {
                    color: #2e7d32;
                }
            """)
        else:
            widget.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                }
                QLabel {
                    color: #757575;
                }
            """)
    
    def set_current_step(self, step: int):
        """设置当前步骤"""
        if 0 <= step < len(self.steps):
            old_step = self.current_step
            self.current_step = step
            
            # 更新所有步骤的样式
            for i, widget in enumerate(self.step_widgets):
                self.update_step_style(widget, i, i == step)
                
                # 更新进度条
                progress = widget.findChild(QProgressBar)
                if progress:
                    if i < step:
                        progress.setValue(100)
                    elif i == step:
                        progress.setValue(50)
                    else:
                        progress.setValue(0)


class ValueHierarchyLayout(QWidget):
    """价值层次驱动的布局管理器"""
    
    def __init__(self):
        super().__init__()
        self.current_priority_level = 1
        self.setup_ui()
        logger.info("价值层次布局管理器初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        # 主布局 - 五区域专业布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. 顶部工具栏区域 (优先级1)
        self.create_top_toolbar(main_layout)
        
        # 2. 主工作区域 (三列布局)
        self.create_main_work_area(main_layout)
        
        # 3. 底部时间轴区域 (优先级1)
        self.create_bottom_timeline(main_layout)
        
        # 4. 状态栏区域
        self.create_status_bar(main_layout)
    
    def create_top_toolbar(self, parent_layout):
        """创建顶部工具栏 - 优先级1功能"""
        toolbar_frame = QFrame()
        toolbar_frame.setFixedHeight(60)
        toolbar_frame.setStyleSheet("""
            QFrame {
                background-color: #2C5AA0;
                border-bottom: 2px solid #1e3a5f;
            }
        """)
        
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        
        # 核心工作流程按钮 (优先级1)
        core_buttons = [
            ("📁 项目", "项目管理"),
            ("🎵 音频", "音频导入"),
            ("🤖 AI生成", "AI动画生成"),
            ("👁️ 预览", "实时预览"),
            ("📤 导出", "导出作品")
        ]
        
        for btn_text, tooltip in core_buttons:
            btn = QPushButton(btn_text)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4A90E2;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #FF6B35;
                }
                QPushButton:pressed {
                    background-color: #e55a2b;
                }
            """)
            toolbar_layout.addWidget(btn)
        
        toolbar_layout.addStretch()
        
        # 模式切换和设置 (优先级3)
        mode_btn = QPushButton("🔄 编辑模式")
        settings_btn = QPushButton("⚙️ 设置")
        user_btn = QPushButton("👤 用户")
        
        for btn in [mode_btn, settings_btn, user_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: 1px solid #4A90E2;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #4A90E2;
                }
            """)
            toolbar_layout.addWidget(btn)
        
        parent_layout.addWidget(toolbar_frame)
    
    def create_main_work_area(self, parent_layout):
        """创建主工作区域 - 三列布局"""
        work_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：资源管理区 (优先级2-3)
        self.create_resource_panel(work_splitter)
        
        # 中央：主工作区 (优先级1)
        self.create_central_work_area(work_splitter)
        
        # 右侧：AI控制区 (优先级1-2)
        self.create_ai_control_panel(work_splitter)
        
        # 设置分割器比例 - 突出主工作区
        work_splitter.setSizes([300, 800, 350])
        work_splitter.setStretchFactor(1, 1)  # 中央区域可拉伸
        
        parent_layout.addWidget(work_splitter)
    
    def create_resource_panel(self, parent_splitter):
        """创建资源管理面板"""
        resource_widget = QWidget()
        resource_layout = QVBoxLayout(resource_widget)
        resource_layout.setContentsMargins(5, 5, 5, 5)
        
        # 工作流程指示器 (优先级1)
        self.workflow_indicator = WorkflowPriorityIndicator()
        resource_layout.addWidget(self.workflow_indicator)
        
        # 资源管理选项卡 (优先级2-3)
        resource_tabs = QTabWidget()
        resource_tabs.setTabPosition(QTabWidget.TabPosition.West)
        
        # 按优先级排序的选项卡
        tabs_config = [
            ("📁", "项目文件", "优先级2"),
            ("🎵", "音频管理", "优先级1"),
            ("🎨", "素材库", "优先级3"),
            ("📐", "工具箱", "优先级2"),
            ("📚", "规则库", "优先级3"),
            ("🔄", "操作历史", "优先级2"),
            ("📋", "模板库", "优先级3")
        ]
        
        for icon, name, priority in tabs_config:
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            
            # 优先级标识
            priority_label = QLabel(f"{priority}")
            priority_label.setStyleSheet("color: #6c757d; font-size: 10px;")
            tab_layout.addWidget(priority_label)
            
            tab_layout.addStretch()
            resource_tabs.addTab(tab_widget, f"{icon}\n{name}")
        
        resource_layout.addWidget(resource_tabs)
        parent_splitter.addWidget(resource_widget)
    
    def create_central_work_area(self, parent_splitter):
        """创建中央工作区域 - 优先级1"""
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        
        # 工作区选项卡
        self.work_tabs = QTabWidget()
        self.work_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #2C5AA0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #2C5AA0;
                color: white;
            }
        """)
        
        # 按优先级排序的工作区
        work_areas = [
            ("🎨 舞台编辑", "核心工作区 - 优先级1"),
            ("📱 设备预览", "预览反馈 - 优先级1"),
            ("🧪 测试控制台", "调试工具 - 优先级2"),
            ("🔍 调试面板", "开发工具 - 优先级3"),
            ("📈 性能监控", "系统监控 - 优先级3")
        ]
        
        for tab_name, description in work_areas:
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            
            # 区域描述
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #6c757d; padding: 10px; font-style: italic;")
            tab_layout.addWidget(desc_label)
            
            tab_layout.addStretch()
            self.work_tabs.addTab(tab_widget, tab_name)
        
        central_layout.addWidget(self.work_tabs)
        parent_splitter.addWidget(central_widget)
    
    def create_ai_control_panel(self, parent_splitter):
        """创建AI控制面板 - 优先级1-2"""
        ai_widget = QWidget()
        ai_layout = QVBoxLayout(ai_widget)
        ai_layout.setContentsMargins(5, 5, 5, 5)
        
        # AI控制标题
        ai_title = QLabel("🤖 AI智能控制中心")
        ai_title.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        ai_title.setStyleSheet("color: #2C5AA0; padding: 5px; background-color: #e3f2fd; border-radius: 4px;")
        ai_layout.addWidget(ai_title)
        
        # AI功能选项卡
        ai_tabs = QTabWidget()
        ai_tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        ai_functions = [
            ("🎯 生成", "AI动画生成 - 优先级1"),
            ("📋 Prompt", "提示词编辑 - 优先级1"),
            ("📊 对比", "方案对比 - 优先级2"),
            ("⚙️ 参数", "参数调整 - 优先级2"),
            ("📈 监控", "状态监控 - 优先级3"),
            ("💬 协作", "协作评论 - 优先级3"),
            ("🔧 修复", "智能修复 - 优先级2")
        ]
        
        for tab_name, description in ai_functions:
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #6c757d; font-size: 10px;")
            tab_layout.addWidget(desc_label)
            
            tab_layout.addStretch()
            ai_tabs.addTab(tab_widget, tab_name)
        
        ai_layout.addWidget(ai_tabs)
        parent_splitter.addWidget(ai_widget)
    
    def create_bottom_timeline(self, parent_layout):
        """创建底部时间轴区域 - 优先级1"""
        timeline_frame = QFrame()
        timeline_frame.setFixedHeight(200)
        timeline_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-top: 2px solid #2C5AA0;
                border-bottom: 1px solid #dee2e6;
            }
        """)
        
        timeline_layout = QVBoxLayout(timeline_frame)
        timeline_layout.setContentsMargins(10, 5, 10, 5)
        
        # 时间轴标题
        timeline_title = QLabel("⏱️ 核心时间轴控制 - 旁白驱动制作")
        timeline_title.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        timeline_title.setStyleSheet("color: #2C5AA0;")
        timeline_layout.addWidget(timeline_title)
        
        # 音频波形区域
        waveform_label = QLabel("🎵 ████▓▓▓░░░▓▓▓████░░░▓▓▓████  音频波形 + 时间标记")
        waveform_label.setStyleSheet("background-color: #e8f5e8; padding: 10px; border-radius: 4px; font-family: monospace;")
        timeline_layout.addWidget(waveform_label)
        
        # 动画片段区域
        segments_label = QLabel("🎬 [动画1] [动画2] [动画3] [动画4] 动画片段 + 状态衔接指示")
        segments_label.setStyleSheet("background-color: #fff3cd; padding: 10px; border-radius: 4px;")
        timeline_layout.addWidget(segments_label)
        
        # 控制按钮区域
        controls_layout = QHBoxLayout()
        control_buttons = ["⏯️ 播放", "⏸️ 暂停", "📍 标记", "↶ 撤销", "↷ 重做"]
        
        for btn_text in control_buttons:
            btn = QPushButton(btn_text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2C5AA0;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4A90E2;
                }
            """)
            controls_layout.addWidget(btn)
        
        controls_layout.addStretch()
        
        # 时间显示
        time_label = QLabel("时间: 02:30 / 10:00")
        time_label.setStyleSheet("color: #2C5AA0; font-weight: bold; font-size: 14px;")
        controls_layout.addWidget(time_label)
        
        timeline_layout.addLayout(controls_layout)
        parent_layout.addWidget(timeline_frame)
    
    def create_status_bar(self, parent_layout):
        """创建状态栏"""
        status_frame = QFrame()
        status_frame.setFixedHeight(24)
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #343a40;
                color: white;
            }
        """)
        
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 2, 10, 2)
        
        # 状态信息
        status_items = [
            "📍选中: 小球元素",
            "🎯位置: (400,300)",
            "💾已保存",
            "⚡GPU:45%",
            "👥在线:3人"
        ]
        
        for item in status_items:
            label = QLabel(item)
            label.setStyleSheet("color: white; font-size: 11px;")
            status_layout.addWidget(label)
            
            if item != status_items[-1]:
                separator = QLabel("|")
                separator.setStyleSheet("color: #6c757d;")
                status_layout.addWidget(separator)
        
        status_layout.addStretch()
        parent_layout.addWidget(status_frame)
    
    def set_priority_level(self, level: int):
        """设置当前优先级级别"""
        if 1 <= level <= 4:
            self.current_priority_level = level
            self.update_visibility_by_priority()
            logger.info(f"切换到优先级级别: {level}")
    
    def update_visibility_by_priority(self):
        """根据优先级更新界面可见性"""
        # 这里可以实现渐进式功能披露
        # 根据当前优先级级别显示/隐藏相应的功能
        pass
