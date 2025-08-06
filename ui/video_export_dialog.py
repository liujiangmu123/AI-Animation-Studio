"""
AI Animation Studio - 视频导出选项对话框
提供视频导出的高级选项，包括预设、硬件加速、批量导出等功能
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit,
    QTabWidget, QWidget, QSlider, QFileDialog, QListWidget, QListWidgetItem,
    QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont

from core.logger import get_logger

logger = get_logger("video_export_dialog")


class VideoExportDialog(QDialog):
    """视频导出选项对话框"""
    
    def __init__(self, parent=None, current_project=None):
        super().__init__(parent)
        self.current_project = current_project
        self.export_options = {}
        
        self.setWindowTitle("视频导出选项")
        self.setMinimumSize(600, 700)
        self.resize(700, 800)
        
        self.setup_ui()
        self.load_default_options()
        
        logger.info("视频导出选项对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("视频导出选项")
        title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 基本选项选项卡
        self.setup_basic_options_tab()
        
        # 质量选项选项卡
        self.setup_quality_options_tab()
        
        # 高级选项选项卡
        self.setup_advanced_options_tab()
        
        # 批量导出选项卡
        self.setup_batch_export_tab()
        
        layout.addWidget(self.tab_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        preview_button = QPushButton("预览")
        preview_button.clicked.connect(self.preview_video)
        button_layout.addWidget(preview_button)
        
        button_layout.addStretch()
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        self.export_button = QPushButton("导出")
        self.export_button.setDefault(True)
        self.export_button.clicked.connect(self.accept)
        button_layout.addWidget(self.export_button)
        
        layout.addLayout(button_layout)
    
    def setup_basic_options_tab(self):
        """设置基本选项选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 输出设置组
        output_group = QGroupBox("输出设置")
        output_layout = QGridLayout(output_group)
        
        # 文件名
        output_layout.addWidget(QLabel("文件名:"), 0, 0)
        self.filename_edit = QLineEdit()
        if self.current_project:
            self.filename_edit.setText(f"{self.current_project.name}.mp4")
        else:
            self.filename_edit.setText("animation.mp4")
        output_layout.addWidget(self.filename_edit, 0, 1)
        
        # 输出目录
        output_layout.addWidget(QLabel("输出目录:"), 1, 0)
        output_dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setText(str(Path.cwd()))
        output_dir_layout.addWidget(self.output_dir_edit)
        
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_output_dir)
        output_dir_layout.addWidget(browse_button)
        
        output_layout.addLayout(output_dir_layout, 1, 1)
        
        # 视频格式
        output_layout.addWidget(QLabel("视频格式:"), 2, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4 (H.264)", "WebM (VP9)", "AVI", "MOV"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        output_layout.addWidget(self.format_combo, 2, 1)
        
        layout.addWidget(output_group)
        
        # 分辨率设置组
        resolution_group = QGroupBox("分辨率设置")
        resolution_layout = QGridLayout(resolution_group)
        
        # 预设分辨率
        resolution_layout.addWidget(QLabel("预设分辨率:"), 0, 0)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "自定义",
            "4K (3840x2160)",
            "2K (2560x1440)",
            "Full HD (1920x1080)",
            "HD (1280x720)",
            "SD (854x480)",
            "移动端 (720x1280)",
            "正方形 (1080x1080)"
        ])
        self.resolution_combo.setCurrentText("Full HD (1920x1080)")
        self.resolution_combo.currentTextChanged.connect(self.on_resolution_changed)
        resolution_layout.addWidget(self.resolution_combo, 0, 1)
        
        # 自定义宽度
        resolution_layout.addWidget(QLabel("宽度:"), 1, 0)
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(320, 7680)
        self.width_spinbox.setValue(1920)
        resolution_layout.addWidget(self.width_spinbox, 1, 1)
        
        # 自定义高度
        resolution_layout.addWidget(QLabel("高度:"), 2, 0)
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(240, 4320)
        self.height_spinbox.setValue(1080)
        resolution_layout.addWidget(self.height_spinbox, 2, 1)
        
        layout.addWidget(resolution_group)
        
        # 时间设置组
        time_group = QGroupBox("时间设置")
        time_layout = QGridLayout(time_group)
        
        # 帧率
        time_layout.addWidget(QLabel("帧率 (FPS):"), 0, 0)
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["24", "25", "30", "50", "60"])
        self.fps_combo.setCurrentText("30")
        time_layout.addWidget(self.fps_combo, 0, 1)
        
        # 时长
        time_layout.addWidget(QLabel("时长 (秒):"), 1, 0)
        self.duration_spinbox = QDoubleSpinBox()
        self.duration_spinbox.setRange(0.1, 3600.0)
        self.duration_spinbox.setValue(10.0)
        self.duration_spinbox.setSingleStep(0.1)
        if self.current_project:
            self.duration_spinbox.setValue(self.current_project.total_duration)
        time_layout.addWidget(self.duration_spinbox, 1, 1)
        
        layout.addWidget(time_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "基本选项")
    
    def setup_quality_options_tab(self):
        """设置质量选项选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 质量预设组
        preset_group = QGroupBox("质量预设")
        preset_layout = QVBoxLayout(preset_group)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "最高质量 (慢速)",
            "高质量 (中速)",
            "标准质量 (快速)",
            "低质量 (最快)",
            "自定义"
        ])
        self.quality_combo.setCurrentText("高质量 (中速)")
        self.quality_combo.currentTextChanged.connect(self.on_quality_changed)
        preset_layout.addWidget(self.quality_combo)
        
        layout.addWidget(preset_group)
        
        # 编码设置组
        encoding_group = QGroupBox("编码设置")
        encoding_layout = QGridLayout(encoding_group)
        
        # 比特率
        encoding_layout.addWidget(QLabel("视频比特率 (Mbps):"), 0, 0)
        self.bitrate_spinbox = QDoubleSpinBox()
        self.bitrate_spinbox.setRange(0.5, 100.0)
        self.bitrate_spinbox.setValue(8.0)
        self.bitrate_spinbox.setSingleStep(0.5)
        encoding_layout.addWidget(self.bitrate_spinbox, 0, 1)
        
        # 编码器
        encoding_layout.addWidget(QLabel("视频编码器:"), 1, 0)
        self.encoder_combo = QComboBox()
        self.encoder_combo.addItems([
            "H.264 (x264)",
            "H.265 (x265)",
            "VP9",
            "AV1"
        ])
        encoding_layout.addWidget(self.encoder_combo, 1, 1)
        
        # 编码速度
        encoding_layout.addWidget(QLabel("编码速度:"), 2, 0)
        speed_layout = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 5)
        self.speed_slider.setValue(3)
        self.speed_slider.valueChanged.connect(self.update_speed_label)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("中等")
        speed_layout.addWidget(self.speed_label)
        encoding_layout.addLayout(speed_layout, 2, 1)
        
        layout.addWidget(encoding_group)
        
        # 音频设置组
        audio_group = QGroupBox("音频设置")
        audio_layout = QGridLayout(audio_group)
        
        self.include_audio_checkbox = QCheckBox("包含音频")
        self.include_audio_checkbox.setChecked(True)
        audio_layout.addWidget(self.include_audio_checkbox, 0, 0, 1, 2)
        
        # 音频比特率
        audio_layout.addWidget(QLabel("音频比特率 (kbps):"), 1, 0)
        self.audio_bitrate_combo = QComboBox()
        self.audio_bitrate_combo.addItems(["128", "192", "256", "320"])
        self.audio_bitrate_combo.setCurrentText("192")
        audio_layout.addWidget(self.audio_bitrate_combo, 1, 1)
        
        # 音频采样率
        audio_layout.addWidget(QLabel("采样率 (Hz):"), 2, 0)
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["44100", "48000", "96000"])
        self.sample_rate_combo.setCurrentText("48000")
        audio_layout.addWidget(self.sample_rate_combo, 2, 1)
        
        layout.addWidget(audio_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "质量选项")
    
    def setup_advanced_options_tab(self):
        """设置高级选项选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 硬件加速组
        hardware_group = QGroupBox("硬件加速")
        hardware_layout = QVBoxLayout(hardware_group)
        
        self.enable_hardware_checkbox = QCheckBox("启用硬件加速")
        self.enable_hardware_checkbox.setChecked(True)
        self.enable_hardware_checkbox.setToolTip("使用GPU加速视频编码")
        hardware_layout.addWidget(self.enable_hardware_checkbox)
        
        hw_layout = QGridLayout()
        hw_layout.addWidget(QLabel("加速类型:"), 0, 0)
        self.hardware_type_combo = QComboBox()
        self.hardware_type_combo.addItems([
            "自动检测",
            "NVIDIA NVENC",
            "Intel Quick Sync",
            "AMD VCE",
            "仅CPU"
        ])
        hw_layout.addWidget(self.hardware_type_combo, 0, 1)
        
        hardware_layout.addLayout(hw_layout)
        
        layout.addWidget(hardware_group)
        
        # 性能选项组
        performance_group = QGroupBox("性能选项")
        performance_layout = QGridLayout(performance_group)
        
        # 线程数
        performance_layout.addWidget(QLabel("编码线程数:"), 0, 0)
        self.threads_spinbox = QSpinBox()
        self.threads_spinbox.setRange(1, 32)
        self.threads_spinbox.setValue(4)
        performance_layout.addWidget(self.threads_spinbox, 0, 1)
        
        # 内存限制
        performance_layout.addWidget(QLabel("内存限制 (MB):"), 1, 0)
        self.memory_limit_spinbox = QSpinBox()
        self.memory_limit_spinbox.setRange(512, 8192)
        self.memory_limit_spinbox.setValue(2048)
        performance_layout.addWidget(self.memory_limit_spinbox, 1, 1)
        
        layout.addWidget(performance_group)
        
        # 后处理选项组
        postprocess_group = QGroupBox("后处理选项")
        postprocess_layout = QVBoxLayout(postprocess_group)
        
        self.auto_crop_checkbox = QCheckBox("自动裁剪黑边")
        self.auto_crop_checkbox.setChecked(False)
        postprocess_layout.addWidget(self.auto_crop_checkbox)
        
        self.stabilization_checkbox = QCheckBox("视频稳定化")
        self.stabilization_checkbox.setChecked(False)
        postprocess_layout.addWidget(self.stabilization_checkbox)
        
        self.noise_reduction_checkbox = QCheckBox("降噪处理")
        self.noise_reduction_checkbox.setChecked(False)
        postprocess_layout.addWidget(self.noise_reduction_checkbox)
        
        layout.addWidget(postprocess_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "高级选项")
    
    def setup_batch_export_tab(self):
        """设置批量导出选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 批量导出组
        batch_group = QGroupBox("批量导出")
        batch_layout = QVBoxLayout(batch_group)
        
        self.enable_batch_checkbox = QCheckBox("启用批量导出")
        self.enable_batch_checkbox.toggled.connect(self.toggle_batch_options)
        batch_layout.addWidget(self.enable_batch_checkbox)
        
        # 批量选项
        self.batch_options_widget = QWidget()
        batch_options_layout = QGridLayout(self.batch_options_widget)
        
        # 导出多种格式
        batch_options_layout.addWidget(QLabel("导出格式:"), 0, 0)
        self.batch_formats_list = QListWidget()
        self.batch_formats_list.setMaximumHeight(100)
        
        formats = [("MP4", True), ("WebM", False), ("AVI", False), ("MOV", False)]
        for format_name, checked in formats:
            item = QListWidgetItem(format_name)
            item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
            self.batch_formats_list.addItem(item)
        
        batch_options_layout.addWidget(self.batch_formats_list, 0, 1)
        
        # 导出多种分辨率
        batch_options_layout.addWidget(QLabel("导出分辨率:"), 1, 0)
        self.batch_resolutions_list = QListWidget()
        self.batch_resolutions_list.setMaximumHeight(100)
        
        resolutions = [
            ("1920x1080", True),
            ("1280x720", False),
            ("854x480", False)
        ]
        for res_name, checked in resolutions:
            item = QListWidgetItem(res_name)
            item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
            self.batch_resolutions_list.addItem(item)
        
        batch_options_layout.addWidget(self.batch_resolutions_list, 1, 1)
        
        batch_layout.addWidget(self.batch_options_widget)
        self.batch_options_widget.setEnabled(False)
        
        layout.addWidget(batch_group)
        
        # 进度显示组
        progress_group = QGroupBox("导出进度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_text = QTextEdit()
        self.progress_text.setMaximumHeight(100)
        self.progress_text.setReadOnly(True)
        progress_layout.addWidget(self.progress_text)
        
        layout.addWidget(progress_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "批量导出")
    
    def browse_output_dir(self):
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir_edit.setText(dir_path)
    
    def on_format_changed(self, format_text):
        """格式改变事件"""
        # 根据格式调整编码器选项
        if "MP4" in format_text:
            self.encoder_combo.setCurrentText("H.264 (x264)")
        elif "WebM" in format_text:
            self.encoder_combo.setCurrentText("VP9")
    
    def on_resolution_changed(self, resolution_text):
        """分辨率改变事件"""
        resolution_map = {
            "4K (3840x2160)": (3840, 2160),
            "2K (2560x1440)": (2560, 1440),
            "Full HD (1920x1080)": (1920, 1080),
            "HD (1280x720)": (1280, 720),
            "SD (854x480)": (854, 480),
            "移动端 (720x1280)": (720, 1280),
            "正方形 (1080x1080)": (1080, 1080)
        }
        
        if resolution_text in resolution_map:
            width, height = resolution_map[resolution_text]
            self.width_spinbox.setValue(width)
            self.height_spinbox.setValue(height)
    
    def on_quality_changed(self, quality_text):
        """质量改变事件"""
        quality_map = {
            "最高质量 (慢速)": {"bitrate": 15.0, "speed": 1},
            "高质量 (中速)": {"bitrate": 8.0, "speed": 3},
            "标准质量 (快速)": {"bitrate": 4.0, "speed": 4},
            "低质量 (最快)": {"bitrate": 2.0, "speed": 5}
        }
        
        if quality_text in quality_map:
            settings = quality_map[quality_text]
            self.bitrate_spinbox.setValue(settings["bitrate"])
            self.speed_slider.setValue(settings["speed"])
    
    def update_speed_label(self, value):
        """更新速度标签"""
        labels = ["", "最慢", "慢", "中等", "快", "最快"]
        self.speed_label.setText(labels[value])
    
    def toggle_batch_options(self, enabled):
        """切换批量选项"""
        self.batch_options_widget.setEnabled(enabled)
    
    def preview_video(self):
        """预览视频"""
        # 实现视频预览功能
        pass
    
    def load_default_options(self):
        """加载默认选项"""
        # 从配置文件加载默认选项
        pass
    
    def get_export_options(self) -> Dict[str, Any]:
        """获取导出选项"""
        # 获取批量格式
        batch_formats = []
        if self.enable_batch_checkbox.isChecked():
            for i in range(self.batch_formats_list.count()):
                item = self.batch_formats_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    batch_formats.append(item.text())
        
        # 获取批量分辨率
        batch_resolutions = []
        if self.enable_batch_checkbox.isChecked():
            for i in range(self.batch_resolutions_list.count()):
                item = self.batch_resolutions_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    batch_resolutions.append(item.text())
        
        options = {
            # 基本选项
            "filename": self.filename_edit.text(),
            "output_dir": self.output_dir_edit.text(),
            "format": self.format_combo.currentText(),
            "width": self.width_spinbox.value(),
            "height": self.height_spinbox.value(),
            "fps": int(self.fps_combo.currentText()),
            "duration": self.duration_spinbox.value(),
            
            # 质量选项
            "quality_preset": self.quality_combo.currentText(),
            "bitrate": self.bitrate_spinbox.value(),
            "encoder": self.encoder_combo.currentText(),
            "encoding_speed": self.speed_slider.value(),
            "include_audio": self.include_audio_checkbox.isChecked(),
            "audio_bitrate": int(self.audio_bitrate_combo.currentText()),
            "sample_rate": int(self.sample_rate_combo.currentText()),
            
            # 高级选项
            "enable_hardware": self.enable_hardware_checkbox.isChecked(),
            "hardware_type": self.hardware_type_combo.currentText(),
            "threads": self.threads_spinbox.value(),
            "memory_limit": self.memory_limit_spinbox.value(),
            "auto_crop": self.auto_crop_checkbox.isChecked(),
            "stabilization": self.stabilization_checkbox.isChecked(),
            "noise_reduction": self.noise_reduction_checkbox.isChecked(),
            
            # 批量导出选项
            "enable_batch": self.enable_batch_checkbox.isChecked(),
            "batch_formats": batch_formats,
            "batch_resolutions": batch_resolutions,
        }
        
        return options
