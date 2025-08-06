"""
AI Animation Studio - 增强音频控制组件
提供专业的音频波形显示、频谱分析、音频标记注释等功能
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QSlider, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QTabWidget,
    QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QFormLayout,
    QScrollArea, QFrame, QSplitter, QProgressBar, QToolButton, QMenu,
    QColorDialog, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, QPropertyAnimation
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QLinearGradient, QPolygon,
    QPixmap, QFontMetrics, QAction, QCursor
)

from core.logger import get_logger

logger = get_logger("enhanced_audio_widget")


class AudioAnalyzer(QThread):
    """音频分析线程"""
    
    analysis_complete = pyqtSignal(dict)  # 分析完成信号
    progress_updated = pyqtSignal(int)    # 进度更新信号
    
    def __init__(self, audio_data: np.ndarray, sample_rate: int):
        super().__init__()
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.should_stop = False
    
    def run(self):
        """执行音频分析"""
        try:
            result = {}
            
            # 基本信息
            result['duration'] = len(self.audio_data) / self.sample_rate
            result['sample_rate'] = self.sample_rate
            result['channels'] = 1 if len(self.audio_data.shape) == 1 else self.audio_data.shape[1]
            
            self.progress_updated.emit(10)
            
            # 波形数据（降采样用于显示）
            downsample_factor = max(1, len(self.audio_data) // 2000)
            result['waveform'] = self.audio_data[::downsample_factor]
            
            self.progress_updated.emit(30)
            
            # 频谱分析
            result['spectrum'] = self.analyze_spectrum()
            
            self.progress_updated.emit(60)
            
            # 音量包络
            result['envelope'] = self.calculate_envelope()
            
            self.progress_updated.emit(80)
            
            # 节拍检测
            result['beats'] = self.detect_beats()
            
            self.progress_updated.emit(100)
            
            self.analysis_complete.emit(result)
            
        except Exception as e:
            logger.error(f"音频分析失败: {e}")
    
    def analyze_spectrum(self) -> np.ndarray:
        """分析频谱"""
        try:
            # 使用FFT进行频谱分析
            window_size = 2048
            hop_size = window_size // 4
            
            spectrogram = []
            for i in range(0, len(self.audio_data) - window_size, hop_size):
                if self.should_stop:
                    break
                
                window = self.audio_data[i:i + window_size]
                fft = np.fft.fft(window)
                magnitude = np.abs(fft[:window_size // 2])
                spectrogram.append(magnitude)
            
            return np.array(spectrogram).T
            
        except Exception as e:
            logger.error(f"频谱分析失败: {e}")
            return np.array([])
    
    def calculate_envelope(self) -> np.ndarray:
        """计算音量包络"""
        try:
            window_size = self.sample_rate // 10  # 100ms窗口
            envelope = []
            
            for i in range(0, len(self.audio_data), window_size):
                if self.should_stop:
                    break
                
                window = self.audio_data[i:i + window_size]
                rms = np.sqrt(np.mean(window ** 2))
                envelope.append(rms)
            
            return np.array(envelope)
            
        except Exception as e:
            logger.error(f"包络计算失败: {e}")
            return np.array([])
    
    def detect_beats(self) -> List[float]:
        """检测节拍"""
        try:
            # 简化的节拍检测算法
            envelope = self.calculate_envelope()
            if len(envelope) == 0:
                return []
            
            # 寻找峰值
            beats = []
            threshold = np.mean(envelope) + np.std(envelope)
            
            for i in range(1, len(envelope) - 1):
                if (envelope[i] > envelope[i-1] and 
                    envelope[i] > envelope[i+1] and 
                    envelope[i] > threshold):
                    time = i * (len(self.audio_data) / len(envelope)) / self.sample_rate
                    beats.append(time)
            
            return beats
            
        except Exception as e:
            logger.error(f"节拍检测失败: {e}")
            return []
    
    def stop(self):
        """停止分析"""
        self.should_stop = True


class AudioMarker:
    """音频标记"""
    
    def __init__(self, time: float, text: str, color: QColor = None, marker_type: str = "note"):
        self.time = time
        self.text = text
        self.color = color or QColor("#ff9800")
        self.marker_type = marker_type  # note, beat, section, cue
        self.id = id(self)


class EnhancedWaveformWidget(QWidget):
    """增强波形显示组件"""
    
    time_clicked = pyqtSignal(float)
    marker_added = pyqtSignal(float, str)
    marker_edited = pyqtSignal(int, str)
    marker_deleted = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        
        # 音频数据
        self.audio_data = np.array([])
        self.spectrum_data = np.array([])
        self.envelope_data = np.array([])
        self.beats = []
        self.duration = 0.0
        self.sample_rate = 44100
        
        # 显示设置
        self.show_waveform = True
        self.show_spectrum = False
        self.show_envelope = True
        self.show_beats = True
        self.show_grid = True
        
        # 缩放和滚动
        self.zoom_level = 1.0
        self.scroll_offset = 0.0
        self.pixels_per_second = 100
        
        # 播放状态
        self.current_time = 0.0
        self.is_playing = False
        
        # 标记系统
        self.markers = []
        self.selected_marker = None
        
        # 颜色设置
        self.waveform_color = QColor("#2196F3")
        self.spectrum_color = QColor("#4CAF50")
        self.envelope_color = QColor("#FF9800")
        self.beat_color = QColor("#F44336")
        self.grid_color = QColor("#E0E0E0")
        self.background_color = QColor("#FAFAFA")
        
        self.setMouseTracking(True)
        
        logger.info("增强波形组件初始化完成")
    
    def set_audio_analysis(self, analysis_data: dict):
        """设置音频分析数据"""
        try:
            self.audio_data = analysis_data.get('waveform', np.array([]))
            self.spectrum_data = analysis_data.get('spectrum', np.array([]))
            self.envelope_data = analysis_data.get('envelope', np.array([]))
            self.beats = analysis_data.get('beats', [])
            self.duration = analysis_data.get('duration', 0.0)
            self.sample_rate = analysis_data.get('sample_rate', 44100)
            
            self.update()
            logger.info(f"音频分析数据已设置，时长: {self.duration:.2f}s")
            
        except Exception as e:
            logger.error(f"设置音频分析数据失败: {e}")
    
    def paintEvent(self, event):
        """绘制波形和频谱"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        
        # 绘制背景
        painter.fillRect(rect, self.background_color)
        
        if self.duration <= 0:
            painter.setPen(QPen(Qt.GlobalColor.gray))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "无音频数据")
            return
        
        # 计算时间范围
        visible_duration = width / (self.pixels_per_second * self.zoom_level)
        start_time = self.scroll_offset
        end_time = start_time + visible_duration
        
        # 绘制网格
        if self.show_grid:
            self.draw_grid(painter, rect, start_time, end_time)
        
        # 绘制频谱（背景）
        if self.show_spectrum and self.spectrum_data.size > 0:
            self.draw_spectrum(painter, rect, start_time, end_time)
        
        # 绘制波形
        if self.show_waveform and self.audio_data.size > 0:
            self.draw_waveform(painter, rect, start_time, end_time)
        
        # 绘制包络
        if self.show_envelope and self.envelope_data.size > 0:
            self.draw_envelope(painter, rect, start_time, end_time)
        
        # 绘制节拍标记
        if self.show_beats:
            self.draw_beats(painter, rect, start_time, end_time)
        
        # 绘制用户标记
        self.draw_markers(painter, rect, start_time, end_time)
        
        # 绘制播放位置
        self.draw_playhead(painter, rect, start_time, end_time)
    
    def draw_grid(self, painter: QPainter, rect, start_time: float, end_time: float):
        """绘制时间网格"""
        painter.setPen(QPen(self.grid_color, 1))
        
        # 计算网格间隔
        duration_range = end_time - start_time
        if duration_range <= 10:
            interval = 1.0  # 1秒
        elif duration_range <= 60:
            interval = 5.0  # 5秒
        else:
            interval = 10.0  # 10秒
        
        # 绘制垂直网格线
        first_line = int(start_time / interval) * interval
        for time in np.arange(first_line, end_time + interval, interval):
            if time >= start_time:
                x = self.time_to_pixel(time, start_time, end_time, rect.width())
                painter.drawLine(x, 0, x, rect.height())
                
                # 绘制时间标签
                painter.setPen(QPen(Qt.GlobalColor.gray))
                painter.drawText(x + 2, 15, f"{time:.1f}s")
                painter.setPen(QPen(self.grid_color, 1))
        
        # 绘制水平网格线
        for y in range(0, rect.height(), 40):
            painter.drawLine(0, y, rect.width(), y)
    
    def draw_waveform(self, painter: QPainter, rect, start_time: float, end_time: float):
        """绘制波形"""
        if len(self.audio_data) == 0:
            return
        
        painter.setPen(QPen(self.waveform_color, 1))
        
        center_y = rect.height() // 2
        max_amplitude = rect.height() // 4
        
        # 计算数据范围
        total_samples = len(self.audio_data)
        start_sample = int((start_time / self.duration) * total_samples)
        end_sample = int((end_time / self.duration) * total_samples)
        
        if start_sample >= total_samples or end_sample <= 0:
            return
        
        start_sample = max(0, start_sample)
        end_sample = min(total_samples, end_sample)
        
        # 绘制波形
        samples_per_pixel = max(1, (end_sample - start_sample) / rect.width())
        
        for x in range(rect.width()):
            sample_start = int(start_sample + x * samples_per_pixel)
            sample_end = int(start_sample + (x + 1) * samples_per_pixel)
            
            if sample_start < total_samples and sample_end <= total_samples:
                segment = self.audio_data[sample_start:sample_end]
                if len(segment) > 0:
                    max_val = np.max(segment)
                    min_val = np.min(segment)
                    
                    y1 = center_y - int(max_val * max_amplitude)
                    y2 = center_y - int(min_val * max_amplitude)
                    
                    painter.drawLine(x, y1, x, y2)
    
    def draw_spectrum(self, painter: QPainter, rect, start_time: float, end_time: float):
        """绘制频谱"""
        if self.spectrum_data.size == 0:
            return
        
        # 创建频谱渐变背景
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(76, 175, 80, 50))  # 绿色，透明
        gradient.setColorAt(1, QColor(76, 175, 80, 10))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # 简化的频谱显示
        spectrum_height = rect.height() // 3
        for x in range(0, rect.width(), 4):
            time = start_time + (x / rect.width()) * (end_time - start_time)
            spectrum_index = int((time / self.duration) * self.spectrum_data.shape[1])
            
            if 0 <= spectrum_index < self.spectrum_data.shape[1]:
                # 取低频部分的平均值
                low_freq_avg = np.mean(self.spectrum_data[:50, spectrum_index])
                height = int(low_freq_avg * spectrum_height)
                painter.drawRect(x, rect.height() - height, 3, height)
    
    def draw_envelope(self, painter: QPainter, rect, start_time: float, end_time: float):
        """绘制音量包络"""
        if len(self.envelope_data) == 0:
            return
        
        painter.setPen(QPen(self.envelope_color, 2))
        
        points = []
        envelope_height = rect.height() // 6
        base_y = rect.height() - envelope_height
        
        for x in range(rect.width()):
            time = start_time + (x / rect.width()) * (end_time - start_time)
            envelope_index = int((time / self.duration) * len(self.envelope_data))
            
            if 0 <= envelope_index < len(self.envelope_data):
                envelope_val = self.envelope_data[envelope_index]
                y = base_y - int(envelope_val * envelope_height)
                points.append((x, y))
        
        # 绘制包络线
        for i in range(len(points) - 1):
            painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
    
    def draw_beats(self, painter: QPainter, rect, start_time: float, end_time: float):
        """绘制节拍标记"""
        painter.setPen(QPen(self.beat_color, 2))
        
        for beat_time in self.beats:
            if start_time <= beat_time <= end_time:
                x = self.time_to_pixel(beat_time, start_time, end_time, rect.width())
                painter.drawLine(x, 0, x, rect.height())
                
                # 绘制节拍标记
                painter.setBrush(QBrush(self.beat_color))
                painter.drawEllipse(x - 3, 5, 6, 6)
    
    def draw_markers(self, painter: QPainter, rect, start_time: float, end_time: float):
        """绘制用户标记"""
        for i, marker in enumerate(self.markers):
            if start_time <= marker.time <= end_time:
                x = self.time_to_pixel(marker.time, start_time, end_time, rect.width())
                
                # 绘制标记线
                pen_width = 3 if i == self.selected_marker else 2
                painter.setPen(QPen(marker.color, pen_width))
                painter.drawLine(x, 0, x, rect.height())
                
                # 绘制标记图标
                painter.setBrush(QBrush(marker.color))
                if marker.marker_type == "note":
                    painter.drawRect(x - 4, 2, 8, 8)
                elif marker.marker_type == "cue":
                    points = [x, 2, x - 4, 10, x + 4, 10]
                    painter.drawPolygon(QPolygon([points[i:i+2] for i in range(0, len(points), 2)]))
                
                # 绘制标记文本
                if marker.text:
                    painter.setPen(QPen(Qt.GlobalColor.black))
                    painter.drawText(x + 6, 15, marker.text[:20])
    
    def draw_playhead(self, painter: QPainter, rect, start_time: float, end_time: float):
        """绘制播放位置"""
        if start_time <= self.current_time <= end_time:
            x = self.time_to_pixel(self.current_time, start_time, end_time, rect.width())
            
            # 绘制播放线
            painter.setPen(QPen(QColor("#FF5722"), 3))
            painter.drawLine(x, 0, x, rect.height())
            
            # 绘制播放头
            painter.setBrush(QBrush(QColor("#FF5722")))
            points = [x, 0, x - 6, 12, x + 6, 12]
            painter.drawPolygon(QPolygon([points[i:i+2] for i in range(0, len(points), 2)]))
    
    def time_to_pixel(self, time: float, start_time: float, end_time: float, width: int) -> int:
        """时间转换为像素位置"""
        if end_time <= start_time:
            return 0
        return int(((time - start_time) / (end_time - start_time)) * width)
    
    def pixel_to_time(self, x: int, start_time: float, end_time: float, width: int) -> float:
        """像素位置转换为时间"""
        if width <= 0:
            return start_time
        return start_time + (x / width) * (end_time - start_time)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 计算点击时间
            visible_duration = self.width() / (self.pixels_per_second * self.zoom_level)
            start_time = self.scroll_offset
            end_time = start_time + visible_duration
            
            click_time = self.pixel_to_time(event.position().x(), start_time, end_time, self.width())
            
            # 检查是否点击了标记
            clicked_marker = None
            for i, marker in enumerate(self.markers):
                marker_x = self.time_to_pixel(marker.time, start_time, end_time, self.width())
                if abs(event.position().x() - marker_x) < 10:
                    clicked_marker = i
                    break
            
            if clicked_marker is not None:
                self.selected_marker = clicked_marker
                self.update()
            else:
                self.selected_marker = None
                self.time_clicked.emit(click_time)
        
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键菜单
            self.show_context_menu(event.position().toPoint())
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)
        
        # 添加标记
        add_marker_action = QAction("添加标记", self)
        add_marker_action.triggered.connect(lambda: self.add_marker_at_position(position))
        menu.addAction(add_marker_action)
        
        # 如果有选中的标记
        if self.selected_marker is not None:
            menu.addSeparator()
            
            edit_marker_action = QAction("编辑标记", self)
            edit_marker_action.triggered.connect(self.edit_selected_marker)
            menu.addAction(edit_marker_action)
            
            delete_marker_action = QAction("删除标记", self)
            delete_marker_action.triggered.connect(self.delete_selected_marker)
            menu.addAction(delete_marker_action)
        
        menu.exec(self.mapToGlobal(position))
    
    def add_marker_at_position(self, position):
        """在指定位置添加标记"""
        visible_duration = self.width() / (self.pixels_per_second * self.zoom_level)
        start_time = self.scroll_offset
        end_time = start_time + visible_duration
        
        click_time = self.pixel_to_time(position.x(), start_time, end_time, self.width())
        
        text, ok = QInputDialog.getText(self, "添加标记", "标记文本:")
        if ok and text:
            marker = AudioMarker(click_time, text)
            self.markers.append(marker)
            self.update()
            self.marker_added.emit(click_time, text)
    
    def edit_selected_marker(self):
        """编辑选中的标记"""
        if self.selected_marker is not None and self.selected_marker < len(self.markers):
            marker = self.markers[self.selected_marker]
            text, ok = QInputDialog.getText(self, "编辑标记", "标记文本:", text=marker.text)
            if ok:
                marker.text = text
                self.update()
                self.marker_edited.emit(self.selected_marker, text)
    
    def delete_selected_marker(self):
        """删除选中的标记"""
        if self.selected_marker is not None and self.selected_marker < len(self.markers):
            del self.markers[self.selected_marker]
            self.marker_deleted.emit(self.selected_marker)
            self.selected_marker = None
            self.update()
    
    def set_current_time(self, time: float):
        """设置当前播放时间"""
        self.current_time = time
        self.update()
    
    def set_zoom_level(self, zoom: float):
        """设置缩放级别"""
        self.zoom_level = max(0.1, min(10.0, zoom))
        self.update()
    
    def set_scroll_offset(self, offset: float):
        """设置滚动偏移"""
        self.scroll_offset = max(0, min(self.duration, offset))
        self.update()


class AudioControlPanel(QWidget):
    """音频控制面板"""

    # 信号定义
    audio_loaded = pyqtSignal(str)           # 音频加载信号
    play_requested = pyqtSignal()            # 播放请求信号
    pause_requested = pyqtSignal()           # 暂停请求信号
    stop_requested = pyqtSignal()            # 停止请求信号
    seek_requested = pyqtSignal(float)       # 跳转请求信号
    volume_changed = pyqtSignal(float)       # 音量改变信号
    speed_changed = pyqtSignal(float)        # 播放速度改变信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_file_path = ""
        self.is_playing = False
        self.current_time = 0.0
        self.duration = 0.0

        self.setup_ui()
        self.setup_connections()

        logger.info("音频控制面板初始化完成")

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 音频文件控制
        file_group = QGroupBox("音频文件")
        file_layout = QVBoxLayout(file_group)

        # 文件选择
        file_select_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("选择音频文件...")
        self.file_path_edit.setReadOnly(True)
        file_select_layout.addWidget(self.file_path_edit)

        self.browse_btn = QPushButton("浏览")
        self.browse_btn.clicked.connect(self.browse_audio_file)
        file_select_layout.addWidget(self.browse_btn)

        self.load_btn = QPushButton("加载")
        self.load_btn.clicked.connect(self.load_audio_file)
        file_select_layout.addWidget(self.load_btn)

        file_layout.addLayout(file_select_layout)

        # 音频信息
        self.audio_info_label = QLabel("未加载音频文件")
        file_layout.addWidget(self.audio_info_label)

        layout.addWidget(file_group)

        # 播放控制
        playback_group = QGroupBox("播放控制")
        playback_layout = QVBoxLayout(playback_group)

        # 播放按钮
        playback_buttons_layout = QHBoxLayout()

        self.play_btn = QPushButton("▶️ 播放")
        self.play_btn.clicked.connect(self.toggle_playback)
        self.play_btn.setEnabled(False)
        playback_buttons_layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_playback)
        self.stop_btn.setEnabled(False)
        playback_buttons_layout.addWidget(self.stop_btn)

        playback_buttons_layout.addStretch()

        # 循环播放
        self.loop_cb = QCheckBox("循环播放")
        playback_buttons_layout.addWidget(self.loop_cb)

        playback_layout.addLayout(playback_buttons_layout)

        # 时间显示和跳转
        time_layout = QHBoxLayout()

        self.current_time_label = QLabel("00:00")
        time_layout.addWidget(self.current_time_label)

        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setEnabled(False)
        self.time_slider.valueChanged.connect(self.on_time_slider_changed)
        time_layout.addWidget(self.time_slider)

        self.duration_label = QLabel("00:00")
        time_layout.addWidget(self.duration_label)

        playback_layout.addLayout(time_layout)

        layout.addWidget(playback_group)

        # 音频设置
        settings_group = QGroupBox("音频设置")
        settings_layout = QFormLayout(settings_group)

        # 音量控制
        volume_layout = QHBoxLayout()
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        volume_layout.addWidget(self.volume_slider)

        self.volume_label = QLabel("70%")
        volume_layout.addWidget(self.volume_label)

        settings_layout.addRow("音量:", volume_layout)

        # 播放速度
        speed_layout = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(25, 200)  # 0.25x to 2.0x
        self.speed_slider.setValue(100)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        speed_layout.addWidget(self.speed_slider)

        self.speed_label = QLabel("1.0x")
        speed_layout.addWidget(self.speed_label)

        settings_layout.addRow("播放速度:", speed_layout)

        layout.addWidget(settings_group)

        # 分析控制
        analysis_group = QGroupBox("音频分析")
        analysis_layout = QVBoxLayout(analysis_group)

        # 分析选项
        analysis_options_layout = QHBoxLayout()

        self.analyze_btn = QPushButton("开始分析")
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setEnabled(False)
        analysis_options_layout.addWidget(self.analyze_btn)

        self.auto_analyze_cb = QCheckBox("自动分析")
        self.auto_analyze_cb.setChecked(True)
        analysis_options_layout.addWidget(self.auto_analyze_cb)

        analysis_options_layout.addStretch()

        analysis_layout.addLayout(analysis_options_layout)

        # 分析进度
        self.analysis_progress = QProgressBar()
        self.analysis_progress.setVisible(False)
        analysis_layout.addWidget(self.analysis_progress)

        # 分析结果显示选项
        display_options_layout = QHBoxLayout()

        self.show_waveform_cb = QCheckBox("波形")
        self.show_waveform_cb.setChecked(True)
        display_options_layout.addWidget(self.show_waveform_cb)

        self.show_spectrum_cb = QCheckBox("频谱")
        display_options_layout.addWidget(self.show_spectrum_cb)

        self.show_envelope_cb = QCheckBox("包络")
        self.show_envelope_cb.setChecked(True)
        display_options_layout.addWidget(self.show_envelope_cb)

        self.show_beats_cb = QCheckBox("节拍")
        self.show_beats_cb.setChecked(True)
        display_options_layout.addWidget(self.show_beats_cb)

        analysis_layout.addLayout(display_options_layout)

        layout.addWidget(analysis_group)

        layout.addStretch()

    def setup_connections(self):
        """设置信号连接"""
        # 显示选项连接
        self.show_waveform_cb.toggled.connect(self.update_display_options)
        self.show_spectrum_cb.toggled.connect(self.update_display_options)
        self.show_envelope_cb.toggled.connect(self.update_display_options)
        self.show_beats_cb.toggled.connect(self.update_display_options)

    def browse_audio_file(self):
        """浏览音频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择音频文件",
            "", "音频文件 (*.wav *.mp3 *.m4a *.flac *.ogg);;所有文件 (*)"
        )

        if file_path:
            self.file_path_edit.setText(file_path)
            self.audio_file_path = file_path

    def load_audio_file(self):
        """加载音频文件"""
        if not self.audio_file_path:
            QMessageBox.warning(self, "警告", "请先选择音频文件")
            return

        try:
            # 发送加载信号
            self.audio_loaded.emit(self.audio_file_path)

            # 启用控件
            self.play_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.time_slider.setEnabled(True)
            self.analyze_btn.setEnabled(True)

            # 如果启用了自动分析，开始分析
            if self.auto_analyze_cb.isChecked():
                self.start_analysis()

            logger.info(f"音频文件加载: {self.audio_file_path}")

        except Exception as e:
            logger.error(f"加载音频文件失败: {e}")
            QMessageBox.critical(self, "错误", f"加载音频文件失败:\n{str(e)}")

    def toggle_playback(self):
        """切换播放状态"""
        if self.is_playing:
            self.pause_requested.emit()
            self.play_btn.setText("▶️ 播放")
            self.is_playing = False
        else:
            self.play_requested.emit()
            self.play_btn.setText("⏸️ 暂停")
            self.is_playing = True

    def stop_playback(self):
        """停止播放"""
        self.stop_requested.emit()
        self.play_btn.setText("▶️ 播放")
        self.is_playing = False
        self.current_time = 0.0
        self.update_time_display()

    def on_time_slider_changed(self, value):
        """时间滑块改变事件"""
        if self.duration > 0:
            seek_time = (value / 100.0) * self.duration
            self.seek_requested.emit(seek_time)

    def on_volume_changed(self, value):
        """音量改变事件"""
        volume = value / 100.0
        self.volume_label.setText(f"{value}%")
        self.volume_changed.emit(volume)

    def on_speed_changed(self, value):
        """播放速度改变事件"""
        speed = value / 100.0
        self.speed_label.setText(f"{speed:.1f}x")
        self.speed_changed.emit(speed)

    def start_analysis(self):
        """开始音频分析"""
        if not self.audio_file_path:
            return

        try:
            self.analysis_progress.setVisible(True)
            self.analysis_progress.setValue(0)
            self.analyze_btn.setEnabled(False)

            # 这里应该启动音频分析线程
            # 简化实现，直接发送信号
            logger.info("开始音频分析")

        except Exception as e:
            logger.error(f"开始音频分析失败: {e}")

    def update_display_options(self):
        """更新显示选项"""
        # 这里应该通知波形组件更新显示选项
        pass

    def set_audio_info(self, duration: float, sample_rate: int, channels: int):
        """设置音频信息"""
        self.duration = duration
        self.time_slider.setRange(0, 100)

        # 更新信息显示
        duration_str = self.format_time(duration)
        info_text = f"时长: {duration_str} | 采样率: {sample_rate}Hz | 声道: {channels}"
        self.audio_info_label.setText(info_text)
        self.duration_label.setText(duration_str)

    def set_current_time(self, time: float):
        """设置当前播放时间"""
        self.current_time = time
        self.update_time_display()

        # 更新时间滑块
        if self.duration > 0:
            progress = int((time / self.duration) * 100)
            self.time_slider.setValue(progress)

    def update_time_display(self):
        """更新时间显示"""
        current_str = self.format_time(self.current_time)
        self.current_time_label.setText(current_str)

    def format_time(self, seconds: float) -> str:
        """格式化时间显示"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def on_analysis_progress(self, progress: int):
        """分析进度更新"""
        self.analysis_progress.setValue(progress)

        if progress >= 100:
            self.analysis_progress.setVisible(False)
            self.analyze_btn.setEnabled(True)
            logger.info("音频分析完成")

    def on_analysis_complete(self, analysis_data: dict):
        """分析完成事件"""
        self.on_analysis_progress(100)

        # 更新音频信息
        duration = analysis_data.get('duration', 0.0)
        sample_rate = analysis_data.get('sample_rate', 44100)
        channels = analysis_data.get('channels', 1)

        self.set_audio_info(duration, sample_rate, channels)
