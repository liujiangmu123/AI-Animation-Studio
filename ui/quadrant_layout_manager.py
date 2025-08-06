"""
AI Animation Studio - 四象限布局管理器
实现专业软件四象限布局：输入区域、处理区域、控制区域、时间区域
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QFrame, QLabel, QGroupBox, QTabWidget,
                             QScrollArea, QPushButton, QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPalette, QColor

from core.logger import get_logger

logger = get_logger("quadrant_layout_manager")


class QuadrantArea(QWidget):
    """象限区域基类"""
    
    area_activated = pyqtSignal(str)  # 区域激活信号
    
    def __init__(self, area_name: str, area_title: str, area_color: str):
        super().__init__()
        self.area_name = area_name
        self.area_title = area_title
        self.area_color = area_color
        self.is_active = False
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 区域标题栏
        self.title_bar = self.create_title_bar()
        layout.addWidget(self.title_bar)
        
        # 内容区域
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.setup_content()
        
        layout.addWidget(self.content_area)
        
        # 设置样式
        self.setStyleSheet(f"""
            QuadrantArea {{
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
            }}
            QuadrantArea:hover {{
                border-color: {self.area_color};
            }}
        """)
    
    def create_title_bar(self) -> QWidget:
        """创建标题栏"""
        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {self.area_color};
                border: none;
                border-radius: 6px;
                color: white;
            }}
        """)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 标题
        title_label = QLabel(self.area_title)
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # 激活指示器
        self.active_indicator = QLabel("●")
        self.active_indicator.setStyleSheet("color: #FFD700; font-size: 16px;")
        self.active_indicator.setVisible(False)
        layout.addWidget(self.active_indicator)
        
        return title_bar
    
    def setup_content(self):
        """设置内容 - 子类重写"""
        pass
    
    def set_active(self, active: bool):
        """设置激活状态"""
        self.is_active = active
        self.active_indicator.setVisible(active)
        
        if active:
            self.setStyleSheet(f"""
                QuadrantArea {{
                    background-color: #ffffff;
                    border: 3px solid {self.area_color};
                    border-radius: 8px;
                }}
            """)
            self.area_activated.emit(self.area_name)
        else:
            self.setStyleSheet(f"""
                QuadrantArea {{
                    background-color: #f8f9fa;
                    border: 2px solid #dee2e6;
                    border-radius: 8px;
                }}
                QuadrantArea:hover {{
                    border-color: {self.area_color};
                }}
            """)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        super().mousePressEvent(event)
        if not self.is_active:
            self.set_active(True)


class InputArea(QuadrantArea):
    """输入区域 - 左侧25%"""
    
    def __init__(self):
        super().__init__("input", "🎵 输入区域", "#9C27B0")  # 紫色
    
    def setup_content(self):
        """设置输入区域内容"""
        # 创建选项卡
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.West)
        
        # 音频控制
        audio_widget = QWidget()
        audio_layout = QVBoxLayout(audio_widget)
        audio_layout.addWidget(QLabel("🎵 音频文件导入"))
        audio_layout.addWidget(QLabel("🎚️ 音频控制面板"))
        audio_layout.addWidget(QLabel("📊 音频波形显示"))
        audio_layout.addStretch()
        tabs.addTab(audio_widget, "🎵\n音频")
        
        # 时间段管理
        time_widget = QWidget()
        time_layout = QVBoxLayout(time_widget)
        time_layout.addWidget(QLabel("⏱️ 时间段标记"))
        time_layout.addWidget(QLabel("📍 关键帧设置"))
        time_layout.addWidget(QLabel("🎯 时间点管理"))
        time_layout.addStretch()
        tabs.addTab(time_widget, "⏱️\n时间")
        
        # 素材库
        asset_widget = QWidget()
        asset_layout = QVBoxLayout(asset_widget)
        asset_layout.addWidget(QLabel("📚 素材库管理"))
        asset_layout.addWidget(QLabel("🎨 图片素材"))
        asset_layout.addWidget(QLabel("🎵 音效素材"))
        asset_layout.addStretch()
        tabs.addTab(asset_widget, "📚\n素材")
        
        self.content_layout.addWidget(tabs)


class ProcessingArea(QuadrantArea):
    """处理区域 - 中央50%"""
    
    def __init__(self):
        super().__init__("processing", "🎭 处理区域", "#2C5AA0")  # 蓝色
    
    def setup_content(self):
        """设置处理区域内容"""
        # 创建堆叠组件
        stack = QStackedWidget()
        
        # 舞台画布
        stage_widget = QWidget()
        stage_layout = QVBoxLayout(stage_widget)
        stage_layout.addWidget(QLabel("🎭 舞台画布"))
        stage_layout.addWidget(QLabel("📐 元素编辑器"))
        stage_layout.addWidget(QLabel("🎨 视觉编辑工具"))
        stage_layout.addStretch()
        stack.addWidget(stage_widget)
        
        # 动画描述输入
        desc_widget = QWidget()
        desc_layout = QVBoxLayout(desc_widget)
        desc_layout.addWidget(QLabel("📝 动画描述输入"))
        desc_layout.addWidget(QLabel("💭 自然语言处理"))
        desc_layout.addWidget(QLabel("🎯 描述优化建议"))
        desc_layout.addStretch()
        stack.addWidget(desc_widget)
        
        # AI生成控制
        ai_widget = QWidget()
        ai_layout = QVBoxLayout(ai_widget)
        ai_layout.addWidget(QLabel("🤖 AI生成控制"))
        ai_layout.addWidget(QLabel("⚙️ 生成参数调整"))
        ai_layout.addWidget(QLabel("📊 生成进度监控"))
        ai_layout.addStretch()
        stack.addWidget(ai_widget)
        
        # 切换按钮
        switch_layout = QHBoxLayout()
        
        stage_btn = QPushButton("🎭 舞台")
        stage_btn.clicked.connect(lambda: stack.setCurrentIndex(0))
        switch_layout.addWidget(stage_btn)
        
        desc_btn = QPushButton("📝 描述")
        desc_btn.clicked.connect(lambda: stack.setCurrentIndex(1))
        switch_layout.addWidget(desc_btn)
        
        ai_btn = QPushButton("🤖 AI")
        ai_btn.clicked.connect(lambda: stack.setCurrentIndex(2))
        switch_layout.addWidget(ai_btn)
        
        self.content_layout.addLayout(switch_layout)
        self.content_layout.addWidget(stack)


class ControlArea(QuadrantArea):
    """控制区域 - 右侧25%"""
    
    def __init__(self):
        super().__init__("control", "⚙️ 控制区域", "#FF6B35")  # 橙色
    
    def setup_content(self):
        """设置控制区域内容"""
        # 创建选项卡
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.East)
        
        # 元素列表
        elements_widget = QWidget()
        elements_layout = QVBoxLayout(elements_widget)
        elements_layout.addWidget(QLabel("📋 元素列表"))
        elements_layout.addWidget(QLabel("🎯 元素选择"))
        elements_layout.addWidget(QLabel("📊 图层管理"))
        elements_layout.addStretch()
        tabs.addTab(elements_widget, "📋\n元素")
        
        # 属性面板
        props_widget = QWidget()
        props_layout = QVBoxLayout(props_widget)
        props_layout.addWidget(QLabel("⚙️ 属性面板"))
        props_layout.addWidget(QLabel("🎨 样式设置"))
        props_layout.addWidget(QLabel("📐 变换控制"))
        props_layout.addStretch()
        tabs.addTab(props_widget, "⚙️\n属性")
        
        # 预览控制
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.addWidget(QLabel("👁️ 预览控制"))
        preview_layout.addWidget(QLabel("📱 多设备预览"))
        preview_layout.addWidget(QLabel("🎬 播放控制"))
        preview_layout.addStretch()
        tabs.addTab(preview_widget, "👁️\n预览")
        
        self.content_layout.addWidget(tabs)


class TimeArea(QuadrantArea):
    """时间区域 - 底部"""
    
    def __init__(self):
        super().__init__("time", "🎬 时间区域", "#10B981")  # 绿色
    
    def setup_content(self):
        """设置时间区域内容"""
        # 时间轴控制
        timeline_layout = QHBoxLayout()
        
        # 播放控制
        play_controls = QWidget()
        play_layout = QHBoxLayout(play_controls)
        play_layout.addWidget(QPushButton("⏯️"))
        play_layout.addWidget(QPushButton("⏸️"))
        play_layout.addWidget(QPushButton("⏹️"))
        play_layout.addWidget(QPushButton("⏮️"))
        play_layout.addWidget(QPushButton("⏭️"))
        timeline_layout.addWidget(play_controls)
        
        # 时间显示
        time_display = QLabel("时间: 02:30 / 10:00")
        time_display.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        timeline_layout.addWidget(time_display)
        
        timeline_layout.addStretch()
        
        # 缩放控制
        zoom_controls = QWidget()
        zoom_layout = QHBoxLayout(zoom_controls)
        zoom_layout.addWidget(QPushButton("🔍-"))
        zoom_layout.addWidget(QLabel("100%"))
        zoom_layout.addWidget(QPushButton("🔍+"))
        timeline_layout.addWidget(zoom_controls)
        
        self.content_layout.addLayout(timeline_layout)
        
        # 音频波形和动画片段
        waveform_label = QLabel("🎵 ████▓▓▓░░░▓▓▓████░░░▓▓▓████  音频波形")
        waveform_label.setStyleSheet("""
            background-color: #e8f5e8;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
        """)
        self.content_layout.addWidget(waveform_label)
        
        # 动画片段
        segments_label = QLabel("🎬 [动画1] [动画2] [动画3] [动画4] 动画片段")
        segments_label.setStyleSheet("""
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 4px;
        """)
        self.content_layout.addWidget(segments_label)


class QuadrantLayoutManager(QWidget):
    """四象限布局管理器"""
    
    active_area_changed = pyqtSignal(str)  # 活动区域改变信号
    
    def __init__(self):
        super().__init__()
        self.current_active_area = None
        self.quadrants = {}
        self.setup_ui()
        logger.info("四象限布局管理器初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # 顶部工具栏区域
        self.create_top_toolbar(main_layout)
        
        # 四象限主区域
        self.create_quadrant_areas(main_layout)
        
        # 底部状态栏
        self.create_status_bar(main_layout)
    
    def create_top_toolbar(self, parent_layout):
        """创建顶部工具栏"""
        toolbar = QFrame()
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #2C5AA0;
                border-radius: 6px;
                color: white;
            }
        """)
        
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(15, 10, 15, 10)
        
        # 工具栏标题
        title = QLabel("🎯 专业四象限布局")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        toolbar_layout.addWidget(title)
        
        toolbar_layout.addStretch()
        
        # 布局切换按钮
        layout_buttons = [
            ("📐 标准", self.set_standard_layout),
            ("🎨 创作", self.set_creative_layout),
            ("🔧 调试", self.set_debug_layout)
        ]
        
        for btn_text, btn_callback in layout_buttons:
            btn = QPushButton(btn_text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4A90E2;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #FF6B35;
                }
            """)
            btn.clicked.connect(btn_callback)
            toolbar_layout.addWidget(btn)
        
        parent_layout.addWidget(toolbar)
    
    def create_quadrant_areas(self, parent_layout):
        """创建四象限区域"""
        # 主分割器（水平）
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 创建四个象限
        self.quadrants['input'] = InputArea()
        self.quadrants['processing'] = ProcessingArea()
        self.quadrants['control'] = ControlArea()
        self.quadrants['time'] = TimeArea()
        
        # 连接信号
        for area in self.quadrants.values():
            area.area_activated.connect(self.on_area_activated)
        
        # 上部分割器
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        top_splitter.addWidget(self.quadrants['input'])
        top_splitter.addWidget(self.quadrants['processing'])
        top_splitter.addWidget(self.quadrants['control'])
        
        # 设置比例：输入25% : 处理50% : 控制25%
        top_splitter.setSizes([300, 600, 300])
        top_splitter.setStretchFactor(1, 1)  # 处理区域可拉伸
        
        # 垂直分割器
        vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        vertical_splitter.addWidget(top_splitter)
        vertical_splitter.addWidget(self.quadrants['time'])
        
        # 设置比例：上部75% : 时间区域25%
        vertical_splitter.setSizes([600, 200])
        vertical_splitter.setStretchFactor(0, 1)  # 上部可拉伸
        
        parent_layout.addWidget(vertical_splitter)
    
    def create_status_bar(self, parent_layout):
        """创建状态栏"""
        status_bar = QFrame()
        status_bar.setFixedHeight(30)
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #343a40;
                border-radius: 4px;
                color: white;
            }
        """)
        
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        # 当前活动区域
        self.active_area_label = QLabel("活动区域: 无")
        self.active_area_label.setStyleSheet("color: white; font-weight: bold;")
        status_layout.addWidget(self.active_area_label)
        
        status_layout.addStretch()
        
        # 布局信息
        layout_info = QLabel("四象限专业布局 | 输入-处理-控制-时间")
        layout_info.setStyleSheet("color: #adb5bd; font-size: 11px;")
        status_layout.addWidget(layout_info)
        
        parent_layout.addWidget(status_bar)
    
    def on_area_activated(self, area_name: str):
        """区域激活处理"""
        # 取消其他区域的激活状态
        for name, area in self.quadrants.items():
            if name != area_name:
                area.set_active(False)
        
        self.current_active_area = area_name
        self.active_area_changed.emit(area_name)
        
        # 更新状态栏
        area_names = {
            'input': '🎵 输入区域',
            'processing': '🎭 处理区域',
            'control': '⚙️ 控制区域',
            'time': '🎬 时间区域'
        }
        
        self.active_area_label.setText(f"活动区域: {area_names.get(area_name, area_name)}")
        
        logger.info(f"象限区域激活: {area_name}")
    
    def set_standard_layout(self):
        """设置标准布局"""
        # 标准四象限布局
        self.activate_area('processing')
        logger.info("切换到标准布局")
    
    def set_creative_layout(self):
        """设置创作布局"""
        # 突出处理区域的创作布局
        self.activate_area('processing')
        logger.info("切换到创作布局")
    
    def set_debug_layout(self):
        """设置调试布局"""
        # 突出控制区域的调试布局
        self.activate_area('control')
        logger.info("切换到调试布局")
    
    def activate_area(self, area_name: str):
        """激活指定区域"""
        if area_name in self.quadrants:
            self.quadrants[area_name].set_active(True)
    
    def get_current_active_area(self) -> str:
        """获取当前活动区域"""
        return self.current_active_area
    
    def get_layout_summary(self) -> dict:
        """获取布局摘要"""
        return {
            'layout_type': '四象限专业布局',
            'areas': list(self.quadrants.keys()),
            'current_active': self.current_active_area,
            'area_count': len(self.quadrants)
        }


class WorkflowAreaManager:
    """工作流程区域管理器"""

    def __init__(self, quadrant_manager: QuadrantLayoutManager):
        self.quadrant_manager = quadrant_manager
        self.workflow_mappings = self._initialize_workflow_mappings()
        logger.info("工作流程区域管理器初始化完成")

    def _initialize_workflow_mappings(self) -> dict:
        """初始化工作流程映射"""
        return {
            # 音频导入阶段
            'audio_import': {
                'primary_area': 'input',
                'secondary_areas': ['time'],
                'focus_elements': ['音频控制', '时间轴'],
                'description': '专注于音频文件导入和基础设置'
            },

            # 时间段标记阶段
            'time_marking': {
                'primary_area': 'time',
                'secondary_areas': ['input', 'processing'],
                'focus_elements': ['时间轴', '音频波形', '时间段管理'],
                'description': '在时间轴上标记关键动画节点'
            },

            # 动画描述阶段
            'animation_description': {
                'primary_area': 'processing',
                'secondary_areas': ['input', 'control'],
                'focus_elements': ['描述输入', '元素列表', '素材库'],
                'description': '编写和优化动画描述内容'
            },

            # AI生成阶段
            'ai_generation': {
                'primary_area': 'processing',
                'secondary_areas': ['control'],
                'focus_elements': ['AI生成控制', '参数调整', '预览控制'],
                'description': '使用AI生成动画内容'
            },

            # 预览调整阶段
            'preview_adjust': {
                'primary_area': 'control',
                'secondary_areas': ['processing', 'time'],
                'focus_elements': ['预览控制', '舞台画布', '播放控制'],
                'description': '预览动画效果并进行微调'
            },

            # 导出完成阶段
            'export_complete': {
                'primary_area': 'control',
                'secondary_areas': ['processing'],
                'focus_elements': ['导出设置', '预览控制'],
                'description': '导出最终动画作品'
            }
        }

    def switch_to_workflow_stage(self, stage: str):
        """切换到指定工作流程阶段"""
        if stage not in self.workflow_mappings:
            logger.warning(f"未知的工作流程阶段: {stage}")
            return

        mapping = self.workflow_mappings[stage]

        # 激活主要区域
        primary_area = mapping['primary_area']
        self.quadrant_manager.activate_area(primary_area)

        # 高亮次要区域（可以通过样式变化实现）
        secondary_areas = mapping.get('secondary_areas', [])
        for area_name in secondary_areas:
            if area_name in self.quadrant_manager.quadrants:
                area = self.quadrant_manager.quadrants[area_name]
                # 添加次要高亮效果
                area.setStyleSheet(area.styleSheet() + """
                    QuadrantArea {
                        border: 2px dashed #4A90E2;
                    }
                """)

        logger.info(f"切换到工作流程阶段: {stage} - {mapping['description']}")

    def get_current_workflow_info(self) -> dict:
        """获取当前工作流程信息"""
        active_area = self.quadrant_manager.get_current_active_area()

        # 查找匹配的工作流程阶段
        for stage, mapping in self.workflow_mappings.items():
            if mapping['primary_area'] == active_area:
                return {
                    'stage': stage,
                    'primary_area': mapping['primary_area'],
                    'secondary_areas': mapping['secondary_areas'],
                    'focus_elements': mapping['focus_elements'],
                    'description': mapping['description']
                }

        return {
            'stage': 'unknown',
            'primary_area': active_area,
            'secondary_areas': [],
            'focus_elements': [],
            'description': '未知工作流程阶段'
        }

    def get_workflow_suggestions(self) -> list:
        """获取工作流程建议"""
        current_info = self.get_current_workflow_info()
        current_stage = current_info['stage']

        suggestions = []

        # 基于当前阶段提供下一步建议
        stage_sequence = [
            'audio_import', 'time_marking', 'animation_description',
            'ai_generation', 'preview_adjust', 'export_complete'
        ]

        try:
            current_index = stage_sequence.index(current_stage)
            if current_index < len(stage_sequence) - 1:
                next_stage = stage_sequence[current_index + 1]
                next_mapping = self.workflow_mappings[next_stage]
                suggestions.append({
                    'type': 'next_step',
                    'stage': next_stage,
                    'description': f"下一步: {next_mapping['description']}",
                    'primary_area': next_mapping['primary_area']
                })
        except ValueError:
            # 当前阶段不在序列中，提供通用建议
            suggestions.append({
                'type': 'general',
                'description': '建议从音频导入开始工作流程',
                'stage': 'audio_import',
                'primary_area': 'input'
            })

        return suggestions
