"""
AI Animation Studio - 时间轴组件
提供音频波形显示、时间段管理和播放控制功能
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QSlider, QSpinBox, QDoubleSpinBox, QFileDialog, QMessageBox,
    QListWidget, QListWidgetItem, QSplitter, QTextEdit, QComboBox,
    QCheckBox, QProgressBar, QTabWidget, QScrollArea, QFrame,
    QToolButton, QMenu, QLineEdit, QFormLayout, QButtonGroup,
    QRadioButton, QTreeWidget, QTreeWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl, QThread, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPixmap, QLinearGradient, QPolygon, QAction
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QAudioFormat

from core.data_structures import TimeSegment, AnimationType
from core.logger import get_logger

logger = get_logger("timeline_widget")

class WaveformWidget(QWidget):
    """音频波形显示组件"""

    time_clicked = pyqtSignal(float)  # 点击时间位置信号
    segment_created = pyqtSignal(float, float)  # 时间段创建信号
    segment_modified = pyqtSignal(str, float, float)  # 时间段修改信号
    keyframe_added = pyqtSignal(float)  # 关键帧添加信号

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(120)
        self.setMaximumHeight(200)

        # 音频数据
        self.audio_data = []
        self.duration = 0.0
        self.current_time = 0.0
        self.time_segments = []
        self.keyframes = []  # 关键帧列表

        # 显示设置
        self.show_waveform = True
        self.show_spectrum = False
        self.zoom_level = 1.0
        self.scroll_offset = 0.0

        # 交互状态
        self.dragging_segment = None
        self.dragging_edge = None  # 'start' 或 'end'
        self.creating_segment = False
        self.segment_start = 0.0

        # 视觉设置
        self.waveform_color = QColor("#2196F3")
        self.segment_color = QColor("#e3f2fd")
        self.current_time_color = QColor("#f44336")
        self.keyframe_color = QColor("#ff9800")
        self.grid_color = QColor("#e0e0e0")

        self.setMouseTracking(True)
        
    def set_audio_data(self, audio_data: list, duration: float):
        """设置音频数据"""
        self.audio_data = audio_data
        self.duration = duration
        self.update()
    
    def set_current_time(self, time: float):
        """设置当前时间"""
        self.current_time = time
        self.update()
    
    def set_time_segments(self, segments: list):
        """设置时间段"""
        self.time_segments = segments
        self.update()
    
    def paintEvent(self, event):
        """绘制波形"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        
        # 绘制背景
        painter.fillRect(rect, QColor("#f5f5f5"))
        
        # 绘制时间段背景
        for segment in self.time_segments:
            if self.duration > 0:
                start_x = int((segment.start_time / self.duration) * width)
                end_x = int((segment.end_time / self.duration) * width)
                segment_rect = rect.adjusted(start_x, 0, -(width - end_x), 0)
                painter.fillRect(segment_rect, QColor("#e3f2fd"))
        
        # 绘制波形
        if self.audio_data and len(self.audio_data) > 1:
            painter.setPen(QPen(QColor("#2196F3"), 1))
            
            points_per_pixel = len(self.audio_data) / width
            center_y = height // 2
            
            for x in range(width):
                start_idx = int(x * points_per_pixel)
                end_idx = int((x + 1) * points_per_pixel)
                
                if start_idx < len(self.audio_data) and end_idx <= len(self.audio_data):
                    # 计算该像素范围内的最大和最小值
                    segment_data = self.audio_data[start_idx:end_idx]
                    if segment_data:
                        max_val = max(segment_data)
                        min_val = min(segment_data)
                        
                        # 绘制波形线
                        y1 = center_y - int(max_val * center_y * 0.8)
                        y2 = center_y - int(min_val * center_y * 0.8)
                        painter.drawLine(x, y1, x, y2)
        
        # 绘制时间刻度
        painter.setPen(QPen(QColor("#666666"), 1))
        if self.duration > 0:
            # 每5秒一个刻度
            interval = 5.0
            for i in range(int(self.duration / interval) + 1):
                time = i * interval
                x = int((time / self.duration) * width)
                painter.drawLine(x, height - 20, x, height)
                painter.drawText(x + 2, height - 5, f"{time:.0f}s")
        
        # 绘制当前时间指示器
        if self.duration > 0:
            current_x = int((self.current_time / self.duration) * width)
            painter.setPen(QPen(QColor("#f44336"), 2))
            painter.drawLine(current_x, 0, current_x, height)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton and self.duration > 0:
            x = event.position().x()
            time = (x / self.width()) * self.duration
            self.time_clicked.emit(time)

class TimelineWidget(QWidget):
    """时间轴组件 - 增强版"""

    time_changed = pyqtSignal(float)  # 时间改变信号
    segment_selected = pyqtSignal(str)  # 时间段选择信号
    segment_added = pyqtSignal(TimeSegment)  # 时间段添加信号
    segment_deleted = pyqtSignal(str)  # 时间段删除信号
    keyframe_added = pyqtSignal(float, str)  # 关键帧添加信号
    playback_state_changed = pyqtSignal(bool)  # 播放状态改变信号
    marker_added = pyqtSignal(float, str)  # 标记添加信号
    analysis_requested = pyqtSignal(str)  # 分析请求信号

    def __init__(self):
        super().__init__()

        # 音频播放器
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        # 音频分析器
        self.audio_analyzer = None

        # 播放状态
        self.is_playing = False
        self.is_looping = False
        self.loop_start = 0.0
        self.loop_end = 0.0
        self.playback_speed = 1.0
        self.duration = 30.0  # 默认30秒
        self.current_time = 0.0

        # 播放定时器
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.update_time)
        self.play_timer.setInterval(50)  # 20fps更新

        # 时间段管理
        self.time_segments = {}
        self.selected_segment = None
        self.segment_counter = 0

        # 关键帧管理
        self.keyframes = {}  # {time: {property: value}}
        self.keyframe_properties = ["opacity", "scale", "rotation", "position"]

        # 音频分析
        self.audio_file_path = None
        self.audio_analyzer = None

        # 精确时间控制
        self.snap_to_grid = True
        self.grid_interval = 1.0  # 秒
        self.time_precision = 0.1  # 时间精度

        self.setup_ui()
        self.setup_connections()

        logger.info("时间轴组件初始化完成")
    
    def setup_ui(self):
        """设置用户界面 - 增强版"""
        layout = QVBoxLayout(self)

        # 顶部控制栏
        control_bar = self.create_control_bar()
        layout.addWidget(control_bar)

        # 主要内容区域
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧面板 - 增强音频控制
        left_panel = self.create_enhanced_left_panel()
        main_splitter.addWidget(left_panel)

        # 中间面板 - 时间段和关键帧管理
        middle_panel = self.create_middle_panel()
        main_splitter.addWidget(middle_panel)

        # 右侧面板 - 增强波形和时间轴
        right_panel = self.create_enhanced_right_panel()
        main_splitter.addWidget(right_panel)

        # 设置分割比例
        main_splitter.setSizes([250, 200, 550])
        layout.addWidget(main_splitter)

        # 底部状态栏
        status_bar = self.create_status_bar()
        layout.addWidget(status_bar)

    def create_control_bar(self):
        """创建控制栏"""
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(control_frame)

        # 播放控制
        self.play_btn = QPushButton("▶")
        self.play_btn.setMaximumWidth(40)
        self.play_btn.setToolTip("播放/暂停")
        layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setMaximumWidth(40)
        self.stop_btn.setToolTip("停止")
        layout.addWidget(self.stop_btn)

        self.prev_btn = QPushButton("⏮")
        self.prev_btn.setMaximumWidth(40)
        self.prev_btn.setToolTip("上一个关键帧")
        layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("⏭")
        self.next_btn.setMaximumWidth(40)
        self.next_btn.setToolTip("下一个关键帧")
        layout.addWidget(self.next_btn)

        layout.addWidget(QLabel("|"))

        # 时间显示和控制
        self.time_display = QLabel("00:00.0")
        self.time_display.setMinimumWidth(80)
        self.time_display.setStyleSheet("font-family: monospace; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.time_display)

        layout.addWidget(QLabel("/"))

        self.duration_display = QLabel("00:30.0")
        self.duration_display.setMinimumWidth(80)
        self.duration_display.setStyleSheet("font-family: monospace; font-size: 14px;")
        layout.addWidget(self.duration_display)

        layout.addWidget(QLabel("|"))

        # 播放速度控制
        layout.addWidget(QLabel("速度:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"])
        self.speed_combo.setCurrentText("1.0x")
        self.speed_combo.setMaximumWidth(80)
        layout.addWidget(self.speed_combo)

        layout.addWidget(QLabel("|"))

        # 循环播放
        self.loop_checkbox = QCheckBox("循环")
        layout.addWidget(self.loop_checkbox)

        # 网格对齐
        self.snap_checkbox = QCheckBox("网格对齐")
        self.snap_checkbox.setChecked(True)
        layout.addWidget(self.snap_checkbox)

        layout.addStretch()

        # 音频控制
        layout.addWidget(QLabel("音量:"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(100)
        layout.addWidget(self.volume_slider)

        # 加载音频按钮
        self.load_audio_btn = QPushButton("加载音频")
        layout.addWidget(self.load_audio_btn)

        return control_frame

    def create_left_panel(self):
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 创建标签页
        tab_widget = QTabWidget()

        # 时间段标签页
        segments_tab = self.create_segments_tab()
        tab_widget.addTab(segments_tab, "时间段")

        # 关键帧标签页
        keyframes_tab = self.create_keyframes_tab()
        tab_widget.addTab(keyframes_tab, "关键帧")

        # 音频分析标签页
        audio_tab = self.create_audio_analysis_tab()
        tab_widget.addTab(audio_tab, "音频分析")

        layout.addWidget(tab_widget)
        return panel

    def create_segments_tab(self):
        """创建时间段标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 工具栏
        toolbar = QHBoxLayout()

        self.add_segment_btn = QPushButton("➕")
        self.add_segment_btn.setToolTip("添加时间段")
        self.add_segment_btn.setMaximumWidth(30)
        toolbar.addWidget(self.add_segment_btn)

        self.delete_segment_btn = QPushButton("🗑️")
        self.delete_segment_btn.setToolTip("删除时间段")
        self.delete_segment_btn.setMaximumWidth(30)
        toolbar.addWidget(self.delete_segment_btn)

        self.duplicate_segment_btn = QPushButton("📋")
        self.duplicate_segment_btn.setToolTip("复制时间段")
        self.duplicate_segment_btn.setMaximumWidth(30)
        toolbar.addWidget(self.duplicate_segment_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 时间段列表
        self.segments_tree = QTreeWidget()
        self.segments_tree.setHeaderLabels(["名称", "开始", "结束", "时长"])
        self.segments_tree.header().setStretchLastSection(False)
        self.segments_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.segments_tree)

        # 时间段属性编辑
        props_group = QGroupBox("属性")
        props_layout = QFormLayout(props_group)

        self.segment_name_input = QLineEdit()
        props_layout.addRow("名称:", self.segment_name_input)

        self.segment_start_spin = QDoubleSpinBox()
        self.segment_start_spin.setRange(0, 3600)
        self.segment_start_spin.setDecimals(1)
        self.segment_start_spin.setSuffix("s")
        props_layout.addRow("开始时间:", self.segment_start_spin)

        self.segment_duration_spin = QDoubleSpinBox()
        self.segment_duration_spin.setRange(0.1, 3600)
        self.segment_duration_spin.setDecimals(1)
        self.segment_duration_spin.setSuffix("s")
        props_layout.addRow("持续时间:", self.segment_duration_spin)

        self.segment_description_input = QTextEdit()
        self.segment_description_input.setMaximumHeight(60)
        props_layout.addRow("描述:", self.segment_description_input)

        layout.addWidget(props_group)

        return tab

    def create_keyframes_tab(self):
        """创建关键帧标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 工具栏
        toolbar = QHBoxLayout()

        self.add_keyframe_btn = QPushButton("➕")
        self.add_keyframe_btn.setToolTip("添加关键帧")
        self.add_keyframe_btn.setMaximumWidth(30)
        toolbar.addWidget(self.add_keyframe_btn)

        self.delete_keyframe_btn = QPushButton("🗑️")
        self.delete_keyframe_btn.setToolTip("删除关键帧")
        self.delete_keyframe_btn.setMaximumWidth(30)
        toolbar.addWidget(self.delete_keyframe_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 关键帧列表
        self.keyframes_tree = QTreeWidget()
        self.keyframes_tree.setHeaderLabels(["时间", "属性", "值"])
        layout.addWidget(self.keyframes_tree)

        # 关键帧属性编辑
        props_group = QGroupBox("关键帧属性")
        props_layout = QFormLayout(props_group)

        self.keyframe_time_spin = QDoubleSpinBox()
        self.keyframe_time_spin.setRange(0, 3600)
        self.keyframe_time_spin.setDecimals(1)
        self.keyframe_time_spin.setSuffix("s")
        props_layout.addRow("时间:", self.keyframe_time_spin)

        self.keyframe_property_combo = QComboBox()
        self.keyframe_property_combo.addItems(self.keyframe_properties)
        props_layout.addRow("属性:", self.keyframe_property_combo)

        self.keyframe_value_input = QLineEdit()
        props_layout.addRow("值:", self.keyframe_value_input)

        # 缓动类型
        self.easing_combo = QComboBox()
        easing_types = ["Linear", "InQuad", "OutQuad", "InOutQuad", "InCubic", "OutCubic", "InOutCubic"]
        self.easing_combo.addItems(easing_types)
        props_layout.addRow("缓动:", self.easing_combo)

        layout.addWidget(props_group)

        return tab

    def create_audio_analysis_tab(self):
        """创建音频分析标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 音频文件信息
        info_group = QGroupBox("音频信息")
        info_layout = QFormLayout(info_group)

        self.audio_file_label = QLabel("未加载")
        info_layout.addRow("文件:", self.audio_file_label)

        self.audio_duration_label = QLabel("00:00")
        info_layout.addRow("时长:", self.audio_duration_label)

        self.audio_format_label = QLabel("未知")
        info_layout.addRow("格式:", self.audio_format_label)

        self.audio_sample_rate_label = QLabel("未知")
        info_layout.addRow("采样率:", self.audio_sample_rate_label)

        layout.addWidget(info_group)

        # 分析控制
        analysis_group = QGroupBox("分析控制")
        analysis_layout = QVBoxLayout(analysis_group)

        # 分析选项
        self.analyze_beats_cb = QCheckBox("节拍检测")
        self.analyze_beats_cb.setChecked(True)
        analysis_layout.addWidget(self.analyze_beats_cb)

        self.analyze_tempo_cb = QCheckBox("节奏分析")
        self.analyze_tempo_cb.setChecked(True)
        analysis_layout.addWidget(self.analyze_tempo_cb)

        self.analyze_energy_cb = QCheckBox("能量分析")
        analysis_layout.addWidget(self.analyze_energy_cb)

        # 分析按钮
        self.analyze_btn = QPushButton("开始分析")
        analysis_layout.addWidget(self.analyze_btn)

        # 分析进度
        self.analysis_progress = QProgressBar()
        self.analysis_progress.setVisible(False)
        analysis_layout.addWidget(self.analysis_progress)

        layout.addWidget(analysis_group)

        # 分析结果
        results_group = QGroupBox("分析结果")
        results_layout = QVBoxLayout(results_group)

        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(100)
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)

        layout.addWidget(results_group)

        layout.addStretch()
        return tab

    def create_right_panel(self):
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 时间轴控制
        timeline_controls = QHBoxLayout()

        # 缩放控制
        timeline_controls.addWidget(QLabel("缩放:"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 500)  # 0.1x 到 5x
        self.zoom_slider.setValue(100)  # 1x
        self.zoom_slider.setMaximumWidth(150)
        timeline_controls.addWidget(self.zoom_slider)

        self.zoom_label = QLabel("1.0x")
        self.zoom_label.setMinimumWidth(40)
        timeline_controls.addWidget(self.zoom_label)

        timeline_controls.addWidget(QLabel("|"))

        # 网格设置
        timeline_controls.addWidget(QLabel("网格:"))
        self.grid_interval_spin = QDoubleSpinBox()
        self.grid_interval_spin.setRange(0.1, 10.0)
        self.grid_interval_spin.setValue(1.0)
        self.grid_interval_spin.setDecimals(1)
        self.grid_interval_spin.setSuffix("s")
        self.grid_interval_spin.setMaximumWidth(80)
        timeline_controls.addWidget(self.grid_interval_spin)

        timeline_controls.addStretch()

        # 显示选项
        self.show_waveform_cb = QCheckBox("波形")
        self.show_waveform_cb.setChecked(True)
        timeline_controls.addWidget(self.show_waveform_cb)

        self.show_spectrum_cb = QCheckBox("频谱")
        timeline_controls.addWidget(self.show_spectrum_cb)

        layout.addLayout(timeline_controls)

        # 波形显示区域
        self.waveform_widget = WaveformWidget()
        layout.addWidget(self.waveform_widget)

        # 时间轴滑块
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, int(self.duration * 10))  # 0.1秒精度
        layout.addWidget(self.time_slider)

        return panel

    def create_status_bar(self):
        """创建状态栏"""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(status_frame)

        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # 精确时间输入
        layout.addWidget(QLabel("跳转到:"))
        self.goto_time_input = QLineEdit()
        self.goto_time_input.setPlaceholderText("mm:ss.s")
        self.goto_time_input.setMaximumWidth(80)
        layout.addWidget(self.goto_time_input)

        self.goto_btn = QPushButton("跳转")
        self.goto_btn.setMaximumWidth(50)
        layout.addWidget(self.goto_btn)

        return status_frame
        
        # 音频控制面板
        audio_group = QGroupBox("🎵 音频控制")
        audio_layout = QVBoxLayout(audio_group)
        
        # 音频文件选择
        file_layout = QHBoxLayout()
        self.audio_file_label = QLabel("未选择音频文件")
        self.select_audio_btn = QPushButton("📂 选择音频")
        self.format_info_btn = QPushButton("ℹ️ 格式支持")
        self.format_info_btn.setToolTip("查看支持的音频格式信息")

        file_layout.addWidget(self.audio_file_label)
        file_layout.addWidget(self.select_audio_btn)
        file_layout.addWidget(self.format_info_btn)
        audio_layout.addLayout(file_layout)
        
        # 波形显示
        self.waveform_widget = WaveformWidget()
        audio_layout.addWidget(self.waveform_widget)
        
        # 播放控制
        control_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("▶️ 播放")
        self.pause_btn = QPushButton("⏸️ 暂停")
        self.stop_btn = QPushButton("⏹️ 停止")
        
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.stop_btn)
        
        # 时间滑块
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 1000)
        self.time_slider.setValue(0)
        control_layout.addWidget(self.time_slider)
        
        # 时间显示
        self.time_label = QLabel("00:00 / 00:30")
        control_layout.addWidget(self.time_label)
        
        # 音量控制
        control_layout.addWidget(QLabel("音量:"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.setMaximumWidth(100)
        control_layout.addWidget(self.volume_slider)
        
        audio_layout.addLayout(control_layout)
        layout.addWidget(audio_group)
        
        # 时间段管理
        segments_group = QGroupBox("⏱️ 时间段管理")
        segments_layout = QHBoxLayout(segments_group)
        
        # 时间段列表
        segments_left = QVBoxLayout()
        segments_left.addWidget(QLabel("时间段列表:"))
        
        self.segments_list = QListWidget()
        self.segments_list.setMaximumHeight(150)
        segments_left.addWidget(self.segments_list)
        
        # 时间段操作按钮
        segment_btn_layout = QHBoxLayout()
        self.add_segment_btn = QPushButton("➕ 添加")
        self.edit_segment_btn = QPushButton("✏️ 编辑")
        self.delete_segment_btn = QPushButton("🗑️ 删除")
        
        segment_btn_layout.addWidget(self.add_segment_btn)
        segment_btn_layout.addWidget(self.edit_segment_btn)
        segment_btn_layout.addWidget(self.delete_segment_btn)
        segments_left.addLayout(segment_btn_layout)
        
        segments_layout.addLayout(segments_left)
        
        # 时间段详情
        segments_right = QVBoxLayout()
        segments_right.addWidget(QLabel("时间段详情:"))
        
        # 时间设置
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("开始:"))
        self.start_time_spin = QDoubleSpinBox()
        self.start_time_spin.setRange(0.0, 300.0)
        self.start_time_spin.setSuffix("s")
        time_layout.addWidget(self.start_time_spin)
        
        time_layout.addWidget(QLabel("结束:"))
        self.end_time_spin = QDoubleSpinBox()
        self.end_time_spin.setRange(0.0, 300.0)
        self.end_time_spin.setSuffix("s")
        time_layout.addWidget(self.end_time_spin)
        
        segments_right.addLayout(time_layout)
        
        # 动画类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("类型:"))
        self.animation_type_combo = QComboBox()
        for anim_type in AnimationType:
            self.animation_type_combo.addItem(anim_type.value, anim_type)
        type_layout.addWidget(self.animation_type_combo)
        segments_right.addLayout(type_layout)
        
        # 描述
        segments_right.addWidget(QLabel("描述:"))
        self.segment_description = QTextEdit()
        self.segment_description.setMaximumHeight(80)
        segments_right.addWidget(self.segment_description)
        
        # 旁白文本
        segments_right.addWidget(QLabel("旁白文本:"))
        self.narration_text = QTextEdit()
        self.narration_text.setMaximumHeight(60)
        segments_right.addWidget(self.narration_text)
        
        segments_layout.addLayout(segments_right)
        layout.addWidget(segments_group)
    
    def setup_connections(self):
        """设置信号连接"""
        # 音频控制 - 检查组件是否存在
        if hasattr(self, 'select_audio_btn'):
            self.select_audio_btn.clicked.connect(self.select_audio_file)
        if hasattr(self, 'format_info_btn'):
            self.format_info_btn.clicked.connect(self.show_audio_format_info)
        if hasattr(self, 'play_btn'):
            self.play_btn.clicked.connect(self.play_audio)
        if hasattr(self, 'pause_btn'):
            self.pause_btn.clicked.connect(self.pause_audio)
        if hasattr(self, 'stop_btn'):
            self.stop_btn.clicked.connect(self.stop_audio)

        # 时间控制
        if hasattr(self, 'time_slider'):
            self.time_slider.valueChanged.connect(self.on_time_slider_changed)
        if hasattr(self, 'waveform_widget'):
            self.waveform_widget.time_clicked.connect(self.seek_to_time)

        # 音量控制
        if hasattr(self, 'volume_slider'):
            self.volume_slider.valueChanged.connect(self.on_volume_changed)

        # 时间段管理
        if hasattr(self, 'add_segment_btn'):
            self.add_segment_btn.clicked.connect(self.add_time_segment)
        if hasattr(self, 'edit_segment_btn'):
            self.edit_segment_btn.clicked.connect(self.edit_time_segment)
        if hasattr(self, 'delete_segment_btn'):
            self.delete_segment_btn.clicked.connect(self.delete_time_segment)
        if hasattr(self, 'segments_list'):
            self.segments_list.currentRowChanged.connect(self.on_segment_selected)

        # 媒体播放器
        self.media_player.durationChanged.connect(self.on_duration_changed)
        self.media_player.positionChanged.connect(self.on_position_changed)
    
    def select_audio_file(self):
        """选择音频文件 - 增强版"""
        supported_formats = self.get_supported_audio_formats()
        filter_str = "音频文件 (" + " ".join(f"*.{fmt}" for fmt in supported_formats) + ")"

        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择音频文件", "", filter_str
        )

        if file_path:
            if self.validate_audio_file(file_path):
                self.load_audio_file(file_path)
            else:
                QMessageBox.warning(self, "警告", "不支持的音频格式或文件已损坏")
    
    def get_supported_audio_formats(self) -> list:
        """获取支持的音频格式 - 增强版"""
        try:
            from PyQt6.QtMultimedia import QMediaFormat

            # 定义完整的音频格式支持列表
            format_definitions = {
                # 无损格式
                'wav': {'name': 'WAV (无损)', 'quality': 'lossless', 'size': 'large'},
                'flac': {'name': 'FLAC (无损压缩)', 'quality': 'lossless', 'size': 'medium'},
                'aiff': {'name': 'AIFF (无损)', 'quality': 'lossless', 'size': 'large'},

                # 有损格式
                'mp3': {'name': 'MP3 (通用)', 'quality': 'lossy', 'size': 'small'},
                'm4a': {'name': 'M4A/AAC (高质量)', 'quality': 'lossy', 'size': 'small'},
                'aac': {'name': 'AAC (高效)', 'quality': 'lossy', 'size': 'small'},
                'ogg': {'name': 'OGG Vorbis (开源)', 'quality': 'lossy', 'size': 'small'},
                'wma': {'name': 'WMA (Windows)', 'quality': 'lossy', 'size': 'small'},

                # 专业格式
                'opus': {'name': 'Opus (现代)', 'quality': 'lossy', 'size': 'small'},
                'webm': {'name': 'WebM Audio', 'quality': 'lossy', 'size': 'small'},
                'amr': {'name': 'AMR (语音)', 'quality': 'lossy', 'size': 'tiny'},

                # 原始格式
                'pcm': {'name': 'PCM (原始)', 'quality': 'lossless', 'size': 'huge'},
                'raw': {'name': 'RAW Audio', 'quality': 'lossless', 'size': 'huge'}
            }

            supported = []
            format_obj = QMediaFormat()

            # 尝试检测系统支持的格式
            for fmt, info in format_definitions.items():
                try:
                    # 这里可以添加更精确的格式检测逻辑
                    # 目前简化为添加所有常见格式
                    if fmt in ['wav', 'mp3', 'm4a', 'ogg', 'flac', 'aac']:
                        supported.append(fmt)
                except:
                    continue

            # 如果检测失败，使用默认的广泛支持格式
            if not supported:
                supported = ['wav', 'mp3', 'm4a', 'ogg', 'flac', 'aac']

            # 存储格式信息供其他方法使用
            self.format_definitions = format_definitions

            logger.info(f"支持的音频格式: {supported}")
            return supported

        except ImportError:
            # 如果无法导入QMediaFormat，返回常见格式
            default_formats = ['wav', 'mp3', 'm4a', 'ogg', 'flac', 'aac']
            logger.warning("无法检测音频格式支持，使用默认格式列表")
            return default_formats
        except Exception as e:
            logger.error(f"检测音频格式支持时发生错误: {e}")
            return ['wav', 'mp3', 'm4a']  # 最基本的支持

    def validate_audio_file(self, file_path: str) -> bool:
        """验证音频文件"""
        try:
            import os
            from pathlib import Path

            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"音频文件不存在: {file_path}")
                return False

            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                logger.error(f"音频文件为空: {file_path}")
                return False

            # 检查文件大小限制（100MB）
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                logger.error(f"音频文件过大 ({file_size / 1024 / 1024:.1f}MB > 100MB): {file_path}")
                QMessageBox.warning(self, "警告", f"音频文件过大 ({file_size / 1024 / 1024:.1f}MB)，建议使用小于100MB的文件")
                return False

            # 检查文件扩展名
            file_ext = Path(file_path).suffix.lower().lstrip('.')
            supported_formats = self.get_supported_audio_formats()

            if file_ext not in supported_formats:
                logger.error(f"不支持的音频格式: {file_ext}")
                return False

            # 增强的文件头检查
            if not self.validate_audio_file_header(file_path, file_ext):
                logger.warning(f"音频文件头验证失败，但继续尝试加载: {file_path}")

            # 尝试获取音频文件详细信息
            audio_info = self.get_audio_file_info(file_path)
            if audio_info:
                logger.info(f"音频文件信息: {audio_info}")

        except Exception as e:
            logger.warning(f"无法完全验证音频文件: {e}")

            logger.info(f"音频文件验证通过: {file_path} ({file_size / 1024:.1f}KB)")
            return True

        except Exception as e:
            logger.error(f"验证音频文件时发生错误: {e}")
            return False

    def load_audio_file(self, file_path: str):
        """加载音频文件 - 增强版"""
        try:
            # 再次验证文件（防御性编程）
            if not self.validate_audio_file(file_path):
                QMessageBox.warning(self, "错误", "音频文件验证失败")
                return

            # 设置媒体源
            self.media_player.setSource(QUrl.fromLocalFile(file_path))

            # 获取详细的音频文件信息
            audio_info = self.get_audio_file_info(file_path)

            # 更新UI显示
            file_name = Path(file_path).name
            file_size = os.path.getsize(file_path)

            if audio_info:
                # 显示详细信息
                size_text = f"{file_size / 1024:.1f}KB" if file_size < 1024*1024 else f"{file_size / 1024 / 1024:.1f}MB"
                format_text = audio_info.get('format_name', audio_info['extension'].upper())

                self.audio_file_label.setText(f"🎵 {file_name}")

                # 更新音频信息标签（如果存在）
                if hasattr(self, 'audio_format_label'):
                    self.audio_format_label.setText(format_text)
                if hasattr(self, 'audio_duration_label') and audio_info['estimated_duration'] > 0:
                    duration_min = int(audio_info['estimated_duration'] // 60)
                    duration_sec = int(audio_info['estimated_duration'] % 60)
                    self.audio_duration_label.setText(f"{duration_min:02d}:{duration_sec:02d} (估算)")
                if hasattr(self, 'audio_sample_rate_label') and audio_info['estimated_bitrate'] > 0:
                    self.audio_sample_rate_label.setText(f"{audio_info['estimated_bitrate']} kbps (估算)")

                # 在状态栏显示详细信息
                status_msg = f"音频已加载: {format_text} | {size_text}"
                if audio_info['estimated_duration'] > 0:
                    duration_min = int(audio_info['estimated_duration'] // 60)
                    duration_sec = int(audio_info['estimated_duration'] % 60)
                    status_msg += f" | ~{duration_min:02d}:{duration_sec:02d}"
            else:
                # 基本信息显示
                self.audio_file_label.setText(f"🎵 {file_name} ({file_size / 1024:.1f}KB)")
                status_msg = f"音频文件已加载: {file_name}"

            # 生成模拟波形数据
            self.generate_mock_waveform()

            # 记录成功信息
            logger.info(f"音频文件已加载: {file_path}")
            if audio_info:
                logger.info(f"音频信息: {audio_info}")

            # 显示成功消息
            if hasattr(self.parent(), 'statusBar'):
                self.parent().statusBar().showMessage(status_msg, 5000)

        except Exception as e:
            error_msg = f"无法加载音频文件: {e}"
            QMessageBox.warning(self, "错误", error_msg)
            logger.error(f"加载音频文件失败: {file_path} - {e}")

            # 清理UI状态
            self.audio_file_label.setText("未选择音频文件")

            # 显示错误消息
            if hasattr(self.parent(), 'statusBar'):
                self.parent().statusBar().showMessage(f"音频加载失败: {Path(file_path).name}", 5000)

    def generate_mock_waveform(self):
        """生成模拟波形数据"""
        import random
        import math

        # 生成30秒的模拟波形数据
        sample_rate = 1000  # 降低采样率以提高性能
        duration = 30.0
        samples = int(sample_rate * duration)

        waveform_data = []
        for i in range(samples):
            # 生成模拟的音频波形
            t = i / sample_rate
            amplitude = 0.5 * math.sin(2 * math.pi * 2 * t) + 0.3 * random.uniform(-0.5, 0.5)
            waveform_data.append(amplitude)

        self.waveform_widget.set_audio_data(waveform_data, duration)
        self.duration = duration
        self.update_time_display()
    
    def play_audio(self):
        """播放音频"""
        if self.media_player.source().isEmpty():
            QMessageBox.warning(self, "警告", "请先选择音频文件")
            return

        self.media_player.play()
        self.is_playing = True
        self.play_timer.start()

        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)

        logger.info("开始播放音频")
    
    def pause_audio(self):
        """暂停音频"""
        self.media_player.pause()
        self.is_playing = False
        self.play_timer.stop()

        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)

        logger.info("暂停音频播放")
    
    def stop_audio(self):
        """停止音频"""
        self.media_player.stop()
        self.is_playing = False
        self.play_timer.stop()
        self.current_time = 0.0

        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)

        self.update_time_display()
        self.waveform_widget.set_current_time(0.0)

        logger.info("停止音频播放")
    
    def seek_to_time(self, time: float):
        """跳转到指定时间"""
        self.current_time = time
        position = int(time * 1000)  # 转换为毫秒
        self.media_player.setPosition(position)
        self.update_time_display()
        self.time_changed.emit(time)
    
    def on_time_slider_changed(self, value):
        """时间滑块改变"""
        if self.duration > 0:
            time = (value / 1000.0) * self.duration
            self.seek_to_time(time)
    
    def on_volume_changed(self, value):
        """音量改变"""
        volume = value / 100.0
        self.audio_output.setVolume(volume)
    
    def on_duration_changed(self, duration):
        """音频时长改变"""
        self.duration = duration / 1000.0  # 转换为秒
        self.waveform_widget.duration = self.duration
        self.update_time_display()
    
    def on_position_changed(self, position):
        """播放位置改变"""
        self.current_time = position / 1000.0  # 转换为秒
        self.update_time_display()
        self.time_changed.emit(self.current_time)
    
    def update_time(self):
        """更新时间显示"""
        if self.is_playing:
            self.waveform_widget.set_current_time(self.current_time)
    
    def update_time_display(self):
        """更新时间显示"""
        current_min = int(self.current_time // 60)
        current_sec = int(self.current_time % 60)
        total_min = int(self.duration // 60)
        total_sec = int(self.duration % 60)
        
        self.time_label.setText(f"{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}")
        
        # 更新滑块位置
        if self.duration > 0:
            progress = int((self.current_time / self.duration) * 1000)
            self.time_slider.setValue(progress)
        
        # 更新波形显示
        self.waveform_widget.set_current_time(self.current_time)
    
    def add_time_segment(self):
        """添加时间段"""
        # TODO: 实现添加时间段功能
        QMessageBox.information(self, "提示", "添加时间段功能正在开发中...")
    
    def edit_time_segment(self):
        """编辑时间段"""
        # TODO: 实现编辑时间段功能
        QMessageBox.information(self, "提示", "编辑时间段功能正在开发中...")
    
    def delete_time_segment(self):
        """删除时间段"""
        # TODO: 实现删除时间段功能
        QMessageBox.information(self, "提示", "删除时间段功能正在开发中...")
    
    def on_segment_selected(self, row):
        """时间段选择"""
        # TODO: 实现时间段选择功能
        pass

    # ==================== 增强面板创建方法 ====================

    def create_enhanced_left_panel(self):
        """创建增强的左侧音频控制面板"""
        try:
            from .enhanced_audio_widget import AudioControlPanel

            panel = QWidget()
            layout = QVBoxLayout(panel)

            # 音频控制面板
            self.audio_control_panel = AudioControlPanel()
            self.audio_control_panel.audio_loaded.connect(self.on_audio_loaded)
            self.audio_control_panel.play_requested.connect(self.play_audio)
            self.audio_control_panel.pause_requested.connect(self.pause_audio)
            self.audio_control_panel.stop_requested.connect(self.stop_audio)
            self.audio_control_panel.seek_requested.connect(self.seek_audio)
            self.audio_control_panel.volume_changed.connect(self.set_volume)
            self.audio_control_panel.speed_changed.connect(self.set_playback_speed)

            layout.addWidget(self.audio_control_panel)

            return panel

        except ImportError as e:
            logger.warning(f"无法导入增强音频控制面板: {e}")
            # 回退到原始左侧面板
            return self.create_left_panel()

    def create_middle_panel(self):
        """创建中间面板（时间段和关键帧管理）"""
        try:
            from .enhanced_timeline_manager import TimeSegmentManager

            panel = QWidget()
            layout = QVBoxLayout(panel)

            # 增强时间段管理器
            self.segment_manager = TimeSegmentManager()
            self.segment_manager.segment_created.connect(self.on_segment_created)
            self.segment_manager.segment_updated.connect(self.on_segment_updated)
            self.segment_manager.segment_deleted.connect(self.on_segment_deleted)
            self.segment_manager.playback_requested.connect(self.on_playback_requested)

            layout.addWidget(self.segment_manager)

            return panel

        except ImportError as e:
            logger.warning(f"无法导入增强时间段管理器: {e}")
            # 回退到原始左侧面板
            return self.create_left_panel()

    def create_enhanced_right_panel(self):
        """创建增强的右侧波形面板"""
        try:
            from .enhanced_audio_widget import EnhancedWaveformWidget

            panel = QWidget()
            layout = QVBoxLayout(panel)

            # 波形显示控制
            waveform_controls = QHBoxLayout()

            # 显示选项
            self.show_waveform_cb = QCheckBox("波形")
            self.show_waveform_cb.setChecked(True)
            waveform_controls.addWidget(self.show_waveform_cb)

            self.show_spectrum_cb = QCheckBox("频谱")
            waveform_controls.addWidget(self.show_spectrum_cb)

            self.show_envelope_cb = QCheckBox("包络")
            self.show_envelope_cb.setChecked(True)
            waveform_controls.addWidget(self.show_envelope_cb)

            self.show_beats_cb = QCheckBox("节拍")
            self.show_beats_cb.setChecked(True)
            waveform_controls.addWidget(self.show_beats_cb)

            waveform_controls.addStretch()

            # 缩放控制
            waveform_controls.addWidget(QLabel("缩放:"))
            self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
            self.zoom_slider.setRange(10, 1000)  # 0.1x to 10x
            self.zoom_slider.setValue(100)
            self.zoom_slider.setMaximumWidth(100)
            self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
            waveform_controls.addWidget(self.zoom_slider)

            layout.addLayout(waveform_controls)

            # 增强波形组件
            self.enhanced_waveform = EnhancedWaveformWidget()
            self.enhanced_waveform.time_clicked.connect(self.time_changed.emit)
            self.enhanced_waveform.marker_added.connect(self.marker_added.emit)
            layout.addWidget(self.enhanced_waveform)

            # 连接显示选项
            self.show_waveform_cb.toggled.connect(self.update_waveform_display)
            self.show_spectrum_cb.toggled.connect(self.update_waveform_display)
            self.show_envelope_cb.toggled.connect(self.update_waveform_display)
            self.show_beats_cb.toggled.connect(self.update_waveform_display)

            return panel

        except ImportError as e:
            logger.warning(f"无法导入增强波形组件: {e}")
            # 回退到原始右侧面板
            return self.create_right_panel()

    # ==================== 增强音频控制方法 ====================

    def on_audio_loaded(self, file_path: str):
        """音频加载事件"""
        try:
            # 加载音频到媒体播放器
            self.media_player.setSource(QUrl.fromLocalFile(file_path))

            # 开始音频分析
            self.start_audio_analysis(file_path)

            logger.info(f"音频文件已加载: {file_path}")

        except Exception as e:
            logger.error(f"加载音频文件失败: {e}")

    def start_audio_analysis(self, file_path: str):
        """开始音频分析"""
        try:
            from .enhanced_audio_widget import AudioAnalyzer
            import numpy as np

            # 这里应该加载音频数据
            # 简化实现，使用模拟数据
            sample_rate = 44100
            duration = 30.0  # 30秒
            samples = int(sample_rate * duration)
            audio_data = np.random.randn(samples) * 0.1  # 模拟音频数据

            # 创建分析器
            self.audio_analyzer = AudioAnalyzer(audio_data, sample_rate)
            self.audio_analyzer.analysis_complete.connect(self.on_analysis_complete)
            self.audio_analyzer.progress_updated.connect(self.on_analysis_progress)

            # 开始分析
            self.audio_analyzer.start()

        except Exception as e:
            logger.error(f"开始音频分析失败: {e}")

    def on_analysis_complete(self, analysis_data: dict):
        """音频分析完成"""
        try:
            # 更新音频控制面板
            if hasattr(self, 'audio_control_panel'):
                self.audio_control_panel.on_analysis_complete(analysis_data)

            # 更新增强波形组件
            if hasattr(self, 'enhanced_waveform'):
                self.enhanced_waveform.set_audio_analysis(analysis_data)

            logger.info("音频分析数据已应用")

        except Exception as e:
            logger.error(f"应用音频分析数据失败: {e}")

    def on_analysis_progress(self, progress: int):
        """音频分析进度更新"""
        if hasattr(self, 'audio_control_panel'):
            self.audio_control_panel.on_analysis_progress(progress)

    def on_zoom_changed(self, value: int):
        """缩放改变事件"""
        try:
            zoom_level = value / 100.0
            if hasattr(self, 'enhanced_waveform'):
                self.enhanced_waveform.set_zoom_level(zoom_level)
        except Exception as e:
            logger.error(f"设置缩放级别失败: {e}")

    def update_waveform_display(self):
        """更新波形显示选项"""
        try:
            if hasattr(self, 'enhanced_waveform'):
                self.enhanced_waveform.show_waveform = self.show_waveform_cb.isChecked()
                self.enhanced_waveform.show_spectrum = self.show_spectrum_cb.isChecked()
                self.enhanced_waveform.show_envelope = self.show_envelope_cb.isChecked()
                self.enhanced_waveform.show_beats = self.show_beats_cb.isChecked()
                self.enhanced_waveform.update()
        except Exception as e:
            logger.error(f"更新波形显示选项失败: {e}")

    def set_volume(self, volume: float):
        """设置音量"""
        try:
            self.audio_output.setVolume(volume)
        except Exception as e:
            logger.error(f"设置音量失败: {e}")

    def set_playback_speed(self, speed: float):
        """设置播放速度"""
        try:
            self.media_player.setPlaybackRate(speed)
        except Exception as e:
            logger.error(f"设置播放速度失败: {e}")

    def seek_audio(self, time: float):
        """跳转到指定时间"""
        try:
            position_ms = int(time * 1000)
            self.media_player.setPosition(position_ms)

            # 更新波形显示
            if hasattr(self, 'enhanced_waveform'):
                self.enhanced_waveform.set_current_time(time)

        except Exception as e:
            logger.error(f"音频跳转失败: {e}")

    # ==================== 时间段管理事件处理 ====================

    def on_segment_created(self, segment_data: dict):
        """时间段创建事件"""
        try:
            # 创建时间段对象
            segment = TimeSegment(
                start_time=segment_data.get('start_time', 0.0),
                end_time=segment_data.get('end_time', 2.0),
                animation_type=AnimationType.FADE_IN,
                element_id=segment_data.get('element_id', ''),
                properties=segment_data.get('properties', {})
            )

            # 添加到时间段列表
            self.time_segments.append(segment)

            # 发送信号
            self.segment_added.emit(segment)

            logger.info(f"时间段已创建: {segment.start_time}-{segment.end_time}")

        except Exception as e:
            logger.error(f"创建时间段失败: {e}")

    def on_segment_updated(self, segment_id: int, updates: dict):
        """时间段更新事件"""
        try:
            # 查找并更新时间段
            for segment in self.time_segments:
                if id(segment) == segment_id:
                    if 'start_time' in updates:
                        segment.start_time = updates['start_time']
                    if 'end_time' in updates:
                        segment.end_time = updates['end_time']
                    if 'properties' in updates:
                        segment.properties.update(updates['properties'])

                    logger.info(f"时间段已更新: {segment_id}")
                    break

        except Exception as e:
            logger.error(f"更新时间段失败: {e}")

    def on_segment_deleted(self, segment_id: int):
        """时间段删除事件"""
        try:
            # 查找并删除时间段
            self.time_segments = [s for s in self.time_segments if id(s) != segment_id]

            # 发送信号
            self.segment_deleted.emit(str(segment_id))

            logger.info(f"时间段已删除: {segment_id}")

        except Exception as e:
            logger.error(f"删除时间段失败: {e}")

    def on_playback_requested(self, start_time: float):
        """播放请求事件"""
        try:
            # 设置播放位置
            self.current_time = start_time

            # 更新UI显示
            if hasattr(self, 'enhanced_waveform'):
                self.enhanced_waveform.set_current_time(start_time)

            if hasattr(self, 'segment_manager'):
                self.segment_manager.visual_timeline.set_current_time(start_time)

            # 开始播放
            self.play_audio()

            logger.info(f"从时间 {start_time}s 开始播放")

        except Exception as e:
            logger.error(f"播放请求处理失败: {e}")

    def sync_timeline_with_playback(self):
        """同步时间轴与播放状态"""
        try:
            if hasattr(self, 'segment_manager'):
                current_time = self.media_player.position() / 1000.0
                self.segment_manager.visual_timeline.set_current_time(current_time)
                self.segment_manager.time_display.setText(f"{current_time:.1f}s")

        except Exception as e:
            logger.error(f"同步时间轴失败: {e}")

    def update_timeline_duration(self, duration: float):
        """更新时间轴总时长"""
        try:
            if hasattr(self, 'segment_manager'):
                self.segment_manager.visual_timeline.set_total_duration(duration)

        except Exception as e:
            logger.error(f"更新时间轴时长失败: {e}")

    def add_timeline_segment(self, start_time: float, end_time: float,
                           segment_type: str = "animation", name: str = ""):
        """添加时间轴段"""
        try:
            if hasattr(self, 'segment_manager'):
                from .enhanced_timeline_manager import TimelineSegment

                segment = TimelineSegment(start_time, end_time, name, segment_type)
                self.segment_manager.visual_timeline.add_segment(segment)
                self.segment_manager.update_segments_tree()

                logger.info(f"时间轴段已添加: {name} ({start_time}-{end_time})")

        except Exception as e:
            logger.error(f"添加时间轴段失败: {e}")

    def get_segments_at_time(self, time: float) -> list:
        """获取指定时间的所有段"""
        try:
            segments = []
            if hasattr(self, 'segment_manager'):
                for segment in self.segment_manager.visual_timeline.segments:
                    if segment.contains_time(time):
                        segments.append(segment)
            return segments

        except Exception as e:
            logger.error(f"获取时间段失败: {e}")
            return []

    def export_timeline_data(self) -> dict:
        """导出时间轴数据"""
        try:
            timeline_data = {
                'duration': 0.0,
                'segments': [],
                'markers': [],
                'audio_file': self.audio_file_path if hasattr(self, 'audio_file_path') else ""
            }

            if hasattr(self, 'segment_manager'):
                timeline_data['duration'] = self.segment_manager.visual_timeline.total_duration

                for segment in self.segment_manager.visual_timeline.segments:
                    segment_data = {
                        'id': segment.id,
                        'name': segment.name,
                        'type': segment.segment_type,
                        'start_time': segment.start_time,
                        'end_time': segment.end_time,
                        'color': segment.color.name(),
                        'description': segment.description,
                        'locked': segment.locked,
                        'visible': segment.visible,
                        'track_index': getattr(segment, 'track_index', 0)
                    }
                    timeline_data['segments'].append(segment_data)

            return timeline_data

        except Exception as e:
            logger.error(f"导出时间轴数据失败: {e}")
            return {}

    def import_timeline_data(self, timeline_data: dict):
        """导入时间轴数据"""
        try:
            if not hasattr(self, 'segment_manager'):
                return

            # 清除现有段
            self.segment_manager.visual_timeline.segments.clear()

            # 设置时长
            duration = timeline_data.get('duration', 30.0)
            self.segment_manager.visual_timeline.set_total_duration(duration)

            # 导入段
            from .enhanced_timeline_manager import TimelineSegment

            for segment_data in timeline_data.get('segments', []):
                segment = TimelineSegment(
                    segment_data['start_time'],
                    segment_data['end_time'],
                    segment_data['name'],
                    segment_data['type'],
                    QColor(segment_data.get('color', '#2196F3'))
                )

                segment.description = segment_data.get('description', '')
                segment.locked = segment_data.get('locked', False)
                segment.visible = segment_data.get('visible', True)
                segment.track_index = segment_data.get('track_index', 0)

                self.segment_manager.visual_timeline.add_segment(segment)

            # 更新显示
            self.segment_manager.update_segments_tree()

            logger.info(f"时间轴数据导入完成，共 {len(timeline_data.get('segments', []))} 个段")

        except Exception as e:
            logger.error(f"导入时间轴数据失败: {e}")

    def validate_audio_file_header(self, file_path: str, file_ext: str) -> bool:
        """验证音频文件头 - 增强版"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)  # 读取更多字节以进行详细检查

            # 定义音频格式的文件头特征
            format_signatures = {
                'mp3': [
                    b'ID3',  # ID3 标签
                    b'\xff\xfb',  # MPEG Layer 3
                    b'\xff\xfa',  # MPEG Layer 3
                    b'\xff\xf3',  # MPEG Layer 3
                    b'\xff\xf2'   # MPEG Layer 3
                ],
                'wav': [b'RIFF'],
                'ogg': [b'OggS'],
                'flac': [b'fLaC'],
                'm4a': [b'ftypM4A ', b'ftypisom', b'ftypmp42'],
                'aac': [b'\xff\xf0', b'\xff\xf1', b'\xff\xf9'],
                'wma': [b'\x30\x26\xb2\x75'],
                'aiff': [b'FORM'],
                'opus': [b'OpusHead'],
                'webm': [b'\x1a\x45\xdf\xa3']
            }

            if file_ext in format_signatures:
                signatures = format_signatures[file_ext]
                for signature in signatures:
                    if header.startswith(signature):
                        logger.info(f"音频文件头验证成功: {file_ext} - {signature}")
                        return True

                logger.warning(f"音频文件头不匹配预期格式: {file_ext}")
                return False
            else:
                logger.info(f"未知格式，跳过文件头验证: {file_ext}")
                return True

        except Exception as e:
            logger.error(f"验证音频文件头时发生错误: {e}")
            return False

    def get_audio_file_info(self, file_path: str) -> dict:
        """获取音频文件详细信息"""
        try:
            import os
            from pathlib import Path

            file_info = {
                'path': file_path,
                'name': Path(file_path).name,
                'size': os.path.getsize(file_path),
                'extension': Path(file_path).suffix.lower().lstrip('.'),
                'format_name': 'Unknown',
                'estimated_duration': 0,
                'estimated_bitrate': 0
            }

            # 获取格式友好名称
            if hasattr(self, 'format_definitions') and file_info['extension'] in self.format_definitions:
                format_def = self.format_definitions[file_info['extension']]
                file_info['format_name'] = format_def['name']
                file_info['quality'] = format_def['quality']
                file_info['size_category'] = format_def['size']

            # 估算音频时长（基于文件大小和格式的粗略估算）
            file_size_mb = file_info['size'] / (1024 * 1024)
            if file_info['extension'] == 'wav':
                # WAV: 约10MB/分钟 (44.1kHz, 16bit, 立体声)
                file_info['estimated_duration'] = file_size_mb / 10 * 60
                file_info['estimated_bitrate'] = 1411  # kbps
            elif file_info['extension'] == 'mp3':
                # MP3: 约1MB/分钟 (128kbps)
                file_info['estimated_duration'] = file_size_mb * 60
                file_info['estimated_bitrate'] = 128  # kbps
            elif file_info['extension'] in ['m4a', 'aac']:
                # AAC: 约0.8MB/分钟 (128kbps)
                file_info['estimated_duration'] = file_size_mb / 0.8 * 60
                file_info['estimated_bitrate'] = 128  # kbps
            elif file_info['extension'] == 'flac':
                # FLAC: 约5MB/分钟 (压缩的无损)
                file_info['estimated_duration'] = file_size_mb / 5 * 60
                file_info['estimated_bitrate'] = 700  # kbps (平均)
            elif file_info['extension'] == 'ogg':
                # OGG: 约1.2MB/分钟 (160kbps)
                file_info['estimated_duration'] = file_size_mb / 1.2 * 60
                file_info['estimated_bitrate'] = 160  # kbps

            return file_info

        except Exception as e:
            logger.error(f"获取音频文件信息时发生错误: {e}")
            return None

    def show_audio_format_info(self):
        """显示音频格式支持信息"""
        try:
            supported_formats = self.get_supported_audio_formats()

            info_text = "🎵 支持的音频格式:\n\n"

            if hasattr(self, 'format_definitions'):
                # 按质量分类显示
                lossless_formats = []
                lossy_formats = []

                for fmt in supported_formats:
                    if fmt in self.format_definitions:
                        format_def = self.format_definitions[fmt]
                        format_info = f"• {fmt.upper()}: {format_def['name']}"

                        if format_def['quality'] == 'lossless':
                            lossless_formats.append(format_info)
                        else:
                            lossy_formats.append(format_info)
                    else:
                        lossy_formats.append(f"• {fmt.upper()}: 通用格式")

                if lossless_formats:
                    info_text += "📀 无损格式:\n"
                    info_text += "\n".join(lossless_formats) + "\n\n"

                if lossy_formats:
                    info_text += "🎧 有损格式:\n"
                    info_text += "\n".join(lossy_formats) + "\n\n"
            else:
                info_text += "、".join(fmt.upper() for fmt in supported_formats) + "\n\n"

            info_text += "💡 建议:\n"
            info_text += "• 高质量音乐: 使用 FLAC 或 WAV\n"
            info_text += "• 一般用途: 使用 MP3 或 M4A\n"
            info_text += "• 文件大小优先: 使用 OGG 或 AAC\n"
            info_text += "• 最大兼容性: 使用 MP3"

            QMessageBox.information(self, "音频格式支持", info_text)

        except Exception as e:
            logger.error(f"显示音频格式信息时发生错误: {e}")
            QMessageBox.warning(self, "错误", "无法获取音频格式信息")

    # ========== 鼠标事件处理 ==========

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self.handle_left_press(event)
            elif event.button() == Qt.MouseButton.RightButton:
                self.handle_right_press(event)
            elif event.button() == Qt.MouseButton.MiddleButton:
                self.handle_middle_press(event)

            super().mousePressEvent(event)

        except Exception as e:
            logger.error(f"鼠标按下事件处理失败: {e}")

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        try:
            # 如果正在拖拽，更新时间位置
            if hasattr(self, '_dragging') and self._dragging:
                self.handle_drag_move(event)

            # 更新鼠标悬停信息
            self.update_hover_info(event)

            super().mouseMoveEvent(event)

        except Exception as e:
            logger.error(f"鼠标移动事件处理失败: {e}")

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        try:
            if hasattr(self, '_dragging'):
                self._dragging = False

            if event.button() == Qt.MouseButton.LeftButton:
                self.handle_left_release(event)

            super().mouseReleaseEvent(event)

        except Exception as e:
            logger.error(f"鼠标释放事件处理失败: {e}")

    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                # 双击添加关键帧或标记
                self.handle_double_click(event)

            super().mouseDoubleClickEvent(event)

        except Exception as e:
            logger.error(f"鼠标双击事件处理失败: {e}")

    def wheelEvent(self, event):
        """鼠标滚轮事件"""
        try:
            delta = event.angleDelta().y()

            # Ctrl + 滚轮：缩放时间轴
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                if delta > 0:
                    self.zoom_in()
                else:
                    self.zoom_out()
            # Shift + 滚轮：水平滚动
            elif event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                if hasattr(self, 'scroll_area'):
                    scroll_bar = self.scroll_area.horizontalScrollBar()
                    scroll_bar.setValue(scroll_bar.value() - delta // 8)
            # 普通滚轮：垂直滚动
            else:
                if hasattr(self, 'scroll_area'):
                    scroll_bar = self.scroll_area.verticalScrollBar()
                    scroll_bar.setValue(scroll_bar.value() - delta // 8)

            super().wheelEvent(event)

        except Exception as e:
            logger.error(f"滚轮事件处理失败: {e}")

    def handle_left_press(self, event):
        """处理左键按下"""
        try:
            pos = event.position()
            x = pos.x()

            # 计算时间位置
            if hasattr(self, 'duration') and self.duration > 0:
                time_pos = (x / self.width()) * self.duration

                # 检查是否点击在时间段上
                clicked_segment = self.get_segment_at_position(x)
                if clicked_segment:
                    self.segment_selected.emit(clicked_segment.id)
                    self._dragging = True
                    self._drag_start_x = x
                else:
                    # 点击空白区域，移动时间指针
                    self.time_changed.emit(time_pos)

        except Exception as e:
            logger.error(f"左键按下处理失败: {e}")

    def handle_right_press(self, event):
        """处理右键按下"""
        try:
            # 显示上下文菜单
            self.show_context_menu(event.globalPosition().toPoint())

        except Exception as e:
            logger.error(f"右键按下处理失败: {e}")

    def handle_middle_press(self, event):
        """处理中键按下"""
        try:
            # 中键点击重置视图
            self.reset_view()

        except Exception as e:
            logger.error(f"中键按下处理失败: {e}")

    def handle_drag_move(self, event):
        """处理拖拽移动"""
        try:
            if hasattr(self, '_drag_start_x'):
                pos = event.position()
                delta_x = pos.x() - self._drag_start_x

                # 更新拖拽的时间段位置
                # TODO: 实现时间段拖拽逻辑

        except Exception as e:
            logger.error(f"拖拽移动处理失败: {e}")

    def handle_left_release(self, event):
        """处理左键释放"""
        try:
            # 完成拖拽操作
            if hasattr(self, '_dragging') and self._dragging:
                # TODO: 完成时间段拖拽
                pass

        except Exception as e:
            logger.error(f"左键释放处理失败: {e}")

    def handle_double_click(self, event):
        """处理双击"""
        try:
            pos = event.position()
            x = pos.x()

            # 计算时间位置
            if hasattr(self, 'duration') and self.duration > 0:
                time_pos = (x / self.width()) * self.duration

                # 添加关键帧或标记
                self.keyframe_added.emit(time_pos, "用户添加")

        except Exception as e:
            logger.error(f"双击处理失败: {e}")

    def update_hover_info(self, event):
        """更新悬停信息"""
        try:
            pos = event.position()
            x = pos.x()

            # 计算时间位置
            if hasattr(self, 'duration') and self.duration > 0:
                time_pos = (x / self.width()) * self.duration

                # 更新工具提示
                self.setToolTip(f"时间: {time_pos:.2f}s")

        except Exception as e:
            logger.error(f"更新悬停信息失败: {e}")

    def get_segment_at_position(self, x: float):
        """获取指定位置的时间段"""
        try:
            # TODO: 实现时间段检测逻辑
            return None

        except Exception as e:
            logger.error(f"获取时间段失败: {e}")
            return None

    def show_context_menu(self, global_pos):
        """显示上下文菜单"""
        try:
            from PyQt6.QtWidgets import QMenu

            menu = QMenu(self)

            # 添加关键帧
            add_keyframe_action = menu.addAction("添加关键帧")
            add_keyframe_action.triggered.connect(self.add_keyframe_at_cursor)

            # 添加标记
            add_marker_action = menu.addAction("添加标记")
            add_marker_action.triggered.connect(self.add_marker_at_cursor)

            menu.addSeparator()

            # 播放控制
            play_action = menu.addAction("播放/暂停")
            play_action.triggered.connect(self.toggle_playback)

            stop_action = menu.addAction("停止")
            stop_action.triggered.connect(self.stop_playback)

            menu.addSeparator()

            # 视图控制
            zoom_in_action = menu.addAction("放大")
            zoom_in_action.triggered.connect(self.zoom_in)

            zoom_out_action = menu.addAction("缩小")
            zoom_out_action.triggered.connect(self.zoom_out)

            reset_view_action = menu.addAction("重置视图")
            reset_view_action.triggered.connect(self.reset_view)

            menu.exec(global_pos)

        except Exception as e:
            logger.error(f"显示上下文菜单失败: {e}")

    def add_keyframe_at_cursor(self):
        """在光标位置添加关键帧"""
        try:
            # TODO: 实现关键帧添加逻辑
            logger.info("添加关键帧")

        except Exception as e:
            logger.error(f"添加关键帧失败: {e}")

    def add_marker_at_cursor(self):
        """在光标位置添加标记"""
        try:
            # TODO: 实现标记添加逻辑
            logger.info("添加标记")

        except Exception as e:
            logger.error(f"添加标记失败: {e}")

    def toggle_playback(self):
        """切换播放状态"""
        try:
            # TODO: 实现播放切换逻辑
            logger.info("切换播放状态")

        except Exception as e:
            logger.error(f"切换播放状态失败: {e}")

    def stop_playback(self):
        """停止播放"""
        try:
            # TODO: 实现停止播放逻辑
            logger.info("停止播放")

        except Exception as e:
            logger.error(f"停止播放失败: {e}")

    def zoom_in(self):
        """放大时间轴"""
        try:
            # TODO: 实现缩放逻辑
            logger.info("放大时间轴")

        except Exception as e:
            logger.error(f"放大时间轴失败: {e}")

    def zoom_out(self):
        """缩小时间轴"""
        try:
            # TODO: 实现缩放逻辑
            logger.info("缩小时间轴")

        except Exception as e:
            logger.error(f"缩小时间轴失败: {e}")

    def reset_view(self):
        """重置视图"""
        try:
            # TODO: 实现视图重置逻辑
            logger.info("重置视图")

        except Exception as e:
            logger.error(f"重置视图失败: {e}")
