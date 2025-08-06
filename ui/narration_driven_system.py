"""
AI Animation Studio - 旁白驱动制作系统
实现精确到0.1秒的时间同步系统，支持自动时间段计算和完美同步机制
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QSlider, QSpinBox, QDoubleSpinBox, QLineEdit, QTextEdit,
                             QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
                             QProgressBar, QFrame, QScrollArea, QGroupBox, QFormLayout,
                             QCheckBox, QComboBox, QMessageBox, QDialog, QTabWidget,
                             QSplitter, QApplication, QMenu, QToolButton)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QThread, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QBrush, QPen, QPalette
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
import json
import time
import math
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import librosa
import soundfile as sf
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

from core.logger import get_logger
from core.data_structures import TimeSegment, AnimationType

logger = get_logger("narration_driven_system")


class NarrationDrivenSystem(QWidget):
    """旁白驱动系统 - 主要集成类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_analyzer = AudioAnalyzer()
        self.overlap_detector = TimeSegmentOverlapDetector()
        self.sync_validator = AudioAnimationSyncValidator()
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 创建精确时间轴组件
        self.timeline_widget = PreciseTimelineWidget()
        layout.addWidget(self.timeline_widget)

        # 创建波形显示组件
        self.waveform_widget = PreciseWaveformWidget()
        layout.addWidget(self.waveform_widget)

        # 创建时间段组件
        self.segments_widget = TimeSegmentsWidget()
        layout.addWidget(self.segments_widget)

        # 连接信号
        self.timeline_widget.time_changed.connect(self.waveform_widget.set_current_time)
        self.waveform_widget.time_clicked.connect(self.timeline_widget.set_current_time)

    def load_audio_file(self, file_path: str):
        """加载音频文件"""
        try:
            # 使用音频分析器分析文件
            features = self.audio_analyzer.analyze_audio_file(file_path)

            # 更新波形显示
            self.waveform_widget.load_audio_file(file_path)

            # 更新时间轴
            self.timeline_widget.set_audio_features(features)

            logger.info(f"音频文件加载成功: {file_path}")

        except Exception as e:
            logger.error(f"加载音频文件失败: {e}")

    def get_current_segments(self):
        """获取当前时间段"""
        return self.segments_widget.get_segments()

    def validate_sync(self):
        """验证同步"""
        segments = self.get_current_segments()
        return self.sync_validator.validate_sync(segments)


class TimePrecision(Enum):
    """时间精度枚举"""
    COARSE = 1.0        # 粗糙精度 - 1秒
    NORMAL = 0.5        # 普通精度 - 0.5秒
    FINE = 0.1          # 精细精度 - 0.1秒
    ULTRA_FINE = 0.01   # 超精细精度 - 0.01秒


class SyncQuality(Enum):
    """同步质量枚举"""
    BASIC = "basic"         # 基础同步
    ENHANCED = "enhanced"   # 增强同步
    PERFECT = "perfect"     # 完美同步


class AudioFeatureType(Enum):
    """音频特征类型枚举"""
    SILENCE = "silence"         # 静音段
    SPEECH = "speech"           # 语音段
    MUSIC = "music"             # 音乐段
    NOISE = "noise"             # 噪音段
    TRANSITION = "transition"   # 过渡段


@dataclass
class AudioFeature:
    """音频特征"""
    feature_type: AudioFeatureType
    start_time: float
    end_time: float
    confidence: float
    properties: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


@dataclass
class PreciseTimeSegment:
    """精确时间段"""
    segment_id: str
    start_time: float
    end_time: float
    description: str = ""
    narration_text: str = ""
    animation_type: AnimationType = AnimationType.MOVE
    elements: List[str] = field(default_factory=list)
    audio_features: List[AudioFeature] = field(default_factory=list)
    sync_quality: SyncQuality = SyncQuality.BASIC
    auto_generated: bool = False
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def precise_duration(self) -> float:
        """精确到0.1秒的时长"""
        return round(self.duration, 1)


class AudioAnalyzer:
    """音频分析器"""
    
    def __init__(self):
        self.sample_rate = 22050
        self.hop_length = 512
        self.frame_length = 2048
        
        logger.info("音频分析器初始化完成")
    
    def analyze_audio_file(self, file_path: str) -> Tuple[np.ndarray, List[AudioFeature]]:
        """分析音频文件"""
        try:
            # 加载音频文件
            y, sr = librosa.load(file_path, sr=self.sample_rate)
            
            # 提取音频特征
            features = self.extract_audio_features(y, sr)
            
            logger.info(f"音频分析完成: {file_path}, 特征数量: {len(features)}")
            return y, features
            
        except Exception as e:
            logger.error(f"音频分析失败: {e}")
            return np.array([]), []
    
    def extract_audio_features(self, y: np.ndarray, sr: int) -> List[AudioFeature]:
        """提取音频特征"""
        features = []
        
        try:
            # 检测静音段
            silence_features = self.detect_silence(y, sr)
            features.extend(silence_features)
            
            # 检测语音段
            speech_features = self.detect_speech(y, sr)
            features.extend(speech_features)
            
            # 检测过渡段
            transition_features = self.detect_transitions(y, sr)
            features.extend(transition_features)
            
            # 按时间排序
            features.sort(key=lambda f: f.start_time)
            
            return features
            
        except Exception as e:
            logger.error(f"提取音频特征失败: {e}")
            return []
    
    def detect_silence(self, y: np.ndarray, sr: int, threshold: float = 0.01) -> List[AudioFeature]:
        """检测静音段"""
        try:
            # 计算RMS能量
            rms = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
            
            # 检测静音
            silence_frames = rms < threshold
            
            # 转换为时间段
            silence_features = []
            in_silence = False
            start_time = 0.0
            
            for i, is_silent in enumerate(silence_frames):
                current_time = librosa.frames_to_time(i, sr=sr, hop_length=self.hop_length)
                
                if is_silent and not in_silence:
                    # 静音开始
                    start_time = current_time
                    in_silence = True
                elif not is_silent and in_silence:
                    # 静音结束
                    if current_time - start_time > 0.2:  # 至少0.2秒的静音
                        feature = AudioFeature(
                            feature_type=AudioFeatureType.SILENCE,
                            start_time=round(start_time, 1),
                            end_time=round(current_time, 1),
                            confidence=0.9,
                            properties={"threshold": threshold}
                        )
                        silence_features.append(feature)
                    in_silence = False
            
            return silence_features
            
        except Exception as e:
            logger.error(f"检测静音段失败: {e}")
            return []
    
    def detect_speech(self, y: np.ndarray, sr: int) -> List[AudioFeature]:
        """检测语音段"""
        try:
            # 使用谱质心和过零率检测语音
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)[0]
            zero_crossings = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)[0]
            
            # 语音特征阈值
            speech_frames = (spectral_centroids > 1000) & (zero_crossings > 0.1)
            
            # 转换为时间段
            speech_features = []
            in_speech = False
            start_time = 0.0
            
            for i, is_speech in enumerate(speech_frames):
                current_time = librosa.frames_to_time(i, sr=sr, hop_length=self.hop_length)
                
                if is_speech and not in_speech:
                    start_time = current_time
                    in_speech = True
                elif not is_speech and in_speech:
                    if current_time - start_time > 0.5:  # 至少0.5秒的语音
                        feature = AudioFeature(
                            feature_type=AudioFeatureType.SPEECH,
                            start_time=round(start_time, 1),
                            end_time=round(current_time, 1),
                            confidence=0.8,
                            properties={
                                "avg_centroid": float(np.mean(spectral_centroids[max(0, i-10):i])),
                                "avg_zcr": float(np.mean(zero_crossings[max(0, i-10):i]))
                            }
                        )
                        speech_features.append(feature)
                    in_speech = False
            
            return speech_features
            
        except Exception as e:
            logger.error(f"检测语音段失败: {e}")
            return []
    
    def detect_transitions(self, y: np.ndarray, sr: int) -> List[AudioFeature]:
        """检测过渡段"""
        try:
            # 计算谱对比度变化
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=self.hop_length)
            contrast_diff = np.diff(spectral_contrast, axis=1)
            
            # 检测显著变化点
            transition_threshold = np.std(contrast_diff) * 2
            transition_points = np.where(np.abs(contrast_diff).max(axis=0) > transition_threshold)[0]
            
            # 转换为过渡段
            transition_features = []
            for point in transition_points:
                time = librosa.frames_to_time(point, sr=sr, hop_length=self.hop_length)
                
                feature = AudioFeature(
                    feature_type=AudioFeatureType.TRANSITION,
                    start_time=round(max(0, time - 0.2), 1),
                    end_time=round(time + 0.2, 1),
                    confidence=0.7,
                    properties={"transition_strength": float(np.abs(contrast_diff).max(axis=0)[point])}
                )
                transition_features.append(feature)
            
            return transition_features
            
        except Exception as e:
            logger.error(f"检测过渡段失败: {e}")
            return []


class TimeSegmentOverlapDetector:
    """时间段重叠检测器"""
    
    def __init__(self):
        self.tolerance = 0.1  # 0.1秒容差
        
        logger.info("时间段重叠检测器初始化完成")
    
    def detect_overlaps(self, segments: List[PreciseTimeSegment]) -> List[Tuple[str, str, float]]:
        """检测时间段重叠"""
        overlaps = []
        
        try:
            # 按开始时间排序
            sorted_segments = sorted(segments, key=lambda s: s.start_time)
            
            for i in range(len(sorted_segments)):
                for j in range(i + 1, len(sorted_segments)):
                    segment1 = sorted_segments[i]
                    segment2 = sorted_segments[j]
                    
                    # 检查重叠
                    overlap_duration = self.calculate_overlap(segment1, segment2)
                    if overlap_duration > self.tolerance:
                        overlaps.append((segment1.segment_id, segment2.segment_id, overlap_duration))
            
            return overlaps
            
        except Exception as e:
            logger.error(f"检测时间段重叠失败: {e}")
            return []
    
    def calculate_overlap(self, segment1: PreciseTimeSegment, segment2: PreciseTimeSegment) -> float:
        """计算两个时间段的重叠时长"""
        try:
            # 计算重叠区间
            overlap_start = max(segment1.start_time, segment2.start_time)
            overlap_end = min(segment1.end_time, segment2.end_time)
            
            # 如果有重叠，返回重叠时长
            if overlap_start < overlap_end:
                return round(overlap_end - overlap_start, 1)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"计算重叠时长失败: {e}")
            return 0.0
    
    def resolve_overlaps(self, segments: List[PreciseTimeSegment]) -> List[PreciseTimeSegment]:
        """解决时间段重叠"""
        try:
            overlaps = self.detect_overlaps(segments)
            if not overlaps:
                return segments
            
            # 创建副本进行修改
            resolved_segments = [s for s in segments]
            
            for segment1_id, segment2_id, overlap_duration in overlaps:
                # 找到重叠的时间段
                segment1 = next((s for s in resolved_segments if s.segment_id == segment1_id), None)
                segment2 = next((s for s in resolved_segments if s.segment_id == segment2_id), None)
                
                if segment1 and segment2:
                    # 调整第二个时间段的开始时间
                    segment2.start_time = segment1.end_time + 0.1
                    
                    logger.info(f"解决重叠: {segment1_id} 和 {segment2_id}, 调整时长: {overlap_duration}s")
            
            return resolved_segments
            
        except Exception as e:
            logger.error(f"解决时间段重叠失败: {e}")
            return segments


class AudioAnimationSyncValidator:
    """音频动画同步验证器"""
    
    def __init__(self):
        self.sync_tolerance = 0.05  # 0.05秒同步容差
        
        logger.info("音频动画同步验证器初始化完成")
    
    def validate_sync(self, segment: PreciseTimeSegment, audio_features: List[AudioFeature]) -> bool:
        """验证时间段与音频的同步性"""
        try:
            # 检查时间段是否与音频特征对齐
            for feature in audio_features:
                if self.is_time_aligned(segment.start_time, feature.start_time):
                    return True
                if self.is_time_aligned(segment.end_time, feature.end_time):
                    return True
            
            # 检查是否在语音段内
            for feature in audio_features:
                if (feature.feature_type == AudioFeatureType.SPEECH and
                    feature.start_time <= segment.start_time <= feature.end_time):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"验证同步性失败: {e}")
            return False
    
    def is_time_aligned(self, time1: float, time2: float) -> bool:
        """检查两个时间点是否对齐"""
        return abs(time1 - time2) <= self.sync_tolerance
    
    def calculate_sync_score(self, segments: List[PreciseTimeSegment], 
                           audio_features: List[AudioFeature]) -> float:
        """计算整体同步分数"""
        try:
            if not segments:
                return 0.0
            
            sync_count = 0
            for segment in segments:
                if self.validate_sync(segment, audio_features):
                    sync_count += 1
            
            return sync_count / len(segments)
            
        except Exception as e:
            logger.error(f"计算同步分数失败: {e}")
            return 0.0
    
    def suggest_sync_improvements(self, segments: List[PreciseTimeSegment], 
                                audio_features: List[AudioFeature]) -> List[Dict[str, Any]]:
        """建议同步改进"""
        suggestions = []
        
        try:
            for segment in segments:
                if not self.validate_sync(segment, audio_features):
                    # 找到最近的音频特征
                    nearest_feature = self.find_nearest_feature(segment, audio_features)
                    if nearest_feature:
                        suggestion = {
                            "segment_id": segment.segment_id,
                            "current_start": segment.start_time,
                            "suggested_start": nearest_feature.start_time,
                            "reason": f"与{nearest_feature.feature_type.value}特征对齐",
                            "confidence": nearest_feature.confidence
                        }
                        suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"生成同步建议失败: {e}")
            return []
    
    def find_nearest_feature(self, segment: PreciseTimeSegment, 
                           audio_features: List[AudioFeature]) -> Optional[AudioFeature]:
        """找到最近的音频特征"""
        try:
            min_distance = float('inf')
            nearest_feature = None
            
            for feature in audio_features:
                # 计算到特征开始时间的距离
                distance = abs(segment.start_time - feature.start_time)
                if distance < min_distance:
                    min_distance = distance
                    nearest_feature = feature
            
            return nearest_feature if min_distance <= 1.0 else None
            
        except Exception as e:
            logger.error(f"查找最近特征失败: {e}")
            return None


class PreciseTimelineWidget(QWidget):
    """精确时间轴组件"""

    # 信号定义
    time_changed = pyqtSignal(float)                    # 时间改变信号
    segment_selected = pyqtSignal(str)                  # 时间段选择信号
    segment_created = pyqtSignal(dict)                  # 时间段创建信号
    segment_modified = pyqtSignal(str, dict)            # 时间段修改信号
    sync_quality_changed = pyqtSignal(float)            # 同步质量改变信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_file_path = ""
        self.audio_data = np.array([])
        self.audio_features = []
        self.segments = []
        self.current_time = 0.0
        self.duration = 0.0
        self.time_precision = TimePrecision.FINE
        self.sync_quality = SyncQuality.ENHANCED

        # 分析器和验证器
        self.audio_analyzer = AudioAnalyzer()
        self.overlap_detector = TimeSegmentOverlapDetector()
        self.sync_validator = AudioAnimationSyncValidator()

        # UI状态
        self.selected_segment_id = None
        self.is_playing = False
        self.zoom_level = 1.0

        self.setup_ui()
        self.setup_connections()

        logger.info("精确时间轴组件初始化完成")

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 工具栏
        self.create_toolbar(layout)

        # 时间轴主体
        self.create_timeline_body(layout)

        # 控制面板
        self.create_control_panel(layout)

    def create_toolbar(self, layout):
        """创建工具栏"""
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar_layout = QHBoxLayout(toolbar_frame)

        # 精度控制
        precision_label = QLabel("时间精度:")
        self.precision_combo = QComboBox()
        self.precision_combo.addItems(["粗糙(1s)", "普通(0.5s)", "精细(0.1s)", "超精细(0.01s)"])
        self.precision_combo.setCurrentIndex(2)  # 默认精细精度
        self.precision_combo.currentIndexChanged.connect(self.on_precision_changed)

        toolbar_layout.addWidget(precision_label)
        toolbar_layout.addWidget(self.precision_combo)

        # 同步质量
        sync_label = QLabel("同步质量:")
        self.sync_combo = QComboBox()
        self.sync_combo.addItems(["基础", "增强", "完美"])
        self.sync_combo.setCurrentIndex(1)  # 默认增强同步
        self.sync_combo.currentIndexChanged.connect(self.on_sync_quality_changed)

        toolbar_layout.addWidget(sync_label)
        toolbar_layout.addWidget(self.sync_combo)

        toolbar_layout.addStretch()

        # 自动分析按钮
        self.analyze_btn = QPushButton("🔍 分析音频")
        self.analyze_btn.clicked.connect(self.analyze_audio)
        toolbar_layout.addWidget(self.analyze_btn)

        # 自动生成时间段按钮
        self.auto_generate_btn = QPushButton("⚡ 自动生成时间段")
        self.auto_generate_btn.clicked.connect(self.auto_generate_segments)
        toolbar_layout.addWidget(self.auto_generate_btn)

        # 验证同步按钮
        self.validate_btn = QPushButton("✅ 验证同步")
        self.validate_btn.clicked.connect(self.validate_sync)
        toolbar_layout.addWidget(self.validate_btn)

        layout.addWidget(toolbar_frame)

    def create_timeline_body(self, layout):
        """创建时间轴主体"""
        # 使用分割器分离波形和时间段
        splitter = QSplitter(Qt.Orientation.Vertical)

        # 波形显示区域
        self.waveform_widget = PreciseWaveformWidget()
        self.waveform_widget.setMinimumHeight(120)
        self.waveform_widget.time_clicked.connect(self.on_time_clicked)
        splitter.addWidget(self.waveform_widget)

        # 时间段显示区域
        self.segments_widget = TimeSegmentsWidget()
        self.segments_widget.setMinimumHeight(100)
        self.segments_widget.segment_selected.connect(self.on_segment_selected)
        self.segments_widget.segment_modified.connect(self.on_segment_modified)
        splitter.addWidget(self.segments_widget)

        # 设置分割器比例
        splitter.setSizes([120, 100])

        layout.addWidget(splitter)

    def create_control_panel(self, layout):
        """创建控制面板"""
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        control_layout = QHBoxLayout(control_frame)

        # 播放控制
        self.play_btn = QPushButton("▶️")
        self.play_btn.setFixedSize(40, 30)
        self.play_btn.clicked.connect(self.toggle_playback)
        control_layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("⏹️")
        self.stop_btn.setFixedSize(40, 30)
        self.stop_btn.clicked.connect(self.stop_playback)
        control_layout.addWidget(self.stop_btn)

        # 时间显示
        self.time_label = QLabel("00:00.0 / 00:00.0")
        self.time_label.setFont(QFont("Consolas", 10))
        control_layout.addWidget(self.time_label)

        control_layout.addStretch()

        # 缩放控制
        zoom_label = QLabel("缩放:")
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 500)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setMaximumWidth(150)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)

        control_layout.addWidget(zoom_label)
        control_layout.addWidget(self.zoom_slider)

        # 同步分数显示
        self.sync_score_label = QLabel("同步分数: --")
        control_layout.addWidget(self.sync_score_label)

        layout.addWidget(control_frame)

    def setup_connections(self):
        """设置信号连接"""
        self.waveform_widget.time_changed.connect(self.on_time_changed)
        self.segments_widget.segment_created.connect(self.on_segment_created)

    def load_audio_file(self, file_path: str):
        """加载音频文件"""
        try:
            self.audio_file_path = file_path

            # 分析音频
            self.audio_data, self.audio_features = self.audio_analyzer.analyze_audio_file(file_path)

            if len(self.audio_data) > 0:
                # 计算时长
                self.duration = len(self.audio_data) / self.audio_analyzer.sample_rate

                # 更新波形显示
                self.waveform_widget.set_audio_data(self.audio_data, self.audio_analyzer.sample_rate)
                self.waveform_widget.set_audio_features(self.audio_features)

                # 更新时间段显示
                self.segments_widget.set_duration(self.duration)

                # 启用控件
                self.analyze_btn.setEnabled(True)
                self.auto_generate_btn.setEnabled(True)
                self.validate_btn.setEnabled(True)

                # 更新时间显示
                self.update_time_display()

                logger.info(f"音频文件加载完成: {file_path}, 时长: {self.duration:.1f}s")

        except Exception as e:
            logger.error(f"加载音频文件失败: {e}")
            QMessageBox.critical(self, "错误", f"加载音频文件失败:\n{str(e)}")

    def analyze_audio(self):
        """分析音频"""
        if not self.audio_file_path:
            QMessageBox.warning(self, "警告", "请先加载音频文件")
            return

        try:
            # 重新分析音频
            self.audio_data, self.audio_features = self.audio_analyzer.analyze_audio_file(self.audio_file_path)

            # 更新显示
            self.waveform_widget.set_audio_features(self.audio_features)

            # 显示分析结果
            feature_count = len(self.audio_features)
            speech_count = sum(1 for f in self.audio_features if f.feature_type == AudioFeatureType.SPEECH)
            silence_count = sum(1 for f in self.audio_features if f.feature_type == AudioFeatureType.SILENCE)

            QMessageBox.information(
                self, "分析完成",
                f"音频分析完成！\n\n"
                f"总特征数: {feature_count}\n"
                f"语音段: {speech_count}\n"
                f"静音段: {silence_count}\n"
                f"过渡段: {feature_count - speech_count - silence_count}"
            )

        except Exception as e:
            logger.error(f"分析音频失败: {e}")
            QMessageBox.critical(self, "错误", f"分析音频失败:\n{str(e)}")

    def auto_generate_segments(self):
        """自动生成时间段"""
        if not self.audio_features:
            QMessageBox.warning(self, "警告", "请先分析音频")
            return

        try:
            # 基于语音段生成时间段
            generated_segments = []
            segment_id = 0

            for feature in self.audio_features:
                if feature.feature_type == AudioFeatureType.SPEECH and feature.duration >= 1.0:
                    segment = PreciseTimeSegment(
                        segment_id=f"auto_segment_{segment_id}",
                        start_time=feature.start_time,
                        end_time=feature.end_time,
                        description=f"自动生成段落 {segment_id + 1}",
                        narration_text="",
                        animation_type=AnimationType.MOVE,
                        audio_features=[feature],
                        sync_quality=self.sync_quality,
                        auto_generated=True
                    )
                    generated_segments.append(segment)
                    segment_id += 1

            # 检测和解决重叠
            resolved_segments = self.overlap_detector.resolve_overlaps(generated_segments)

            # 添加到时间段列表
            self.segments.extend(resolved_segments)

            # 更新显示
            self.segments_widget.set_segments(self.segments)

            # 验证同步
            self.validate_sync()

            QMessageBox.information(
                self, "生成完成",
                f"自动生成了 {len(resolved_segments)} 个时间段"
            )

        except Exception as e:
            logger.error(f"自动生成时间段失败: {e}")
            QMessageBox.critical(self, "错误", f"自动生成时间段失败:\n{str(e)}")

    def validate_sync(self):
        """验证同步质量"""
        if not self.segments or not self.audio_features:
            return

        try:
            # 计算同步分数
            sync_score = self.sync_validator.calculate_sync_score(self.segments, self.audio_features)

            # 更新显示
            self.sync_score_label.setText(f"同步分数: {sync_score:.1%}")

            # 发送信号
            self.sync_quality_changed.emit(sync_score)

            # 如果同步质量较低，提供改进建议
            if sync_score < 0.8:
                suggestions = self.sync_validator.suggest_sync_improvements(self.segments, self.audio_features)
                if suggestions:
                    self.show_sync_suggestions(suggestions)

        except Exception as e:
            logger.error(f"验证同步质量失败: {e}")

    def show_sync_suggestions(self, suggestions: List[Dict[str, Any]]):
        """显示同步建议"""
        try:
            dialog = SyncSuggestionDialog(suggestions, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 应用建议的修改
                applied_suggestions = dialog.get_applied_suggestions()
                for suggestion in applied_suggestions:
                    self.apply_sync_suggestion(suggestion)

                # 重新验证
                self.validate_sync()

        except Exception as e:
            logger.error(f"显示同步建议失败: {e}")

    def apply_sync_suggestion(self, suggestion: Dict[str, Any]):
        """应用同步建议"""
        try:
            segment_id = suggestion["segment_id"]
            new_start_time = suggestion["suggested_start"]

            # 找到对应的时间段
            for segment in self.segments:
                if segment.segment_id == segment_id:
                    # 调整时间
                    duration = segment.duration
                    segment.start_time = new_start_time
                    segment.end_time = new_start_time + duration

                    logger.info(f"应用同步建议: {segment_id} -> {new_start_time:.1f}s")
                    break

            # 更新显示
            self.segments_widget.set_segments(self.segments)

        except Exception as e:
            logger.error(f"应用同步建议失败: {e}")

    def on_precision_changed(self, index):
        """精度改变事件"""
        precisions = [TimePrecision.COARSE, TimePrecision.NORMAL, TimePrecision.FINE, TimePrecision.ULTRA_FINE]
        self.time_precision = precisions[index]

        # 更新显示精度
        self.waveform_widget.set_time_precision(self.time_precision)
        self.segments_widget.set_time_precision(self.time_precision)

        logger.info(f"时间精度设置为: {self.time_precision.value}s")

    def on_sync_quality_changed(self, index):
        """同步质量改变事件"""
        qualities = [SyncQuality.BASIC, SyncQuality.ENHANCED, SyncQuality.PERFECT]
        self.sync_quality = qualities[index]

        # 更新验证器设置
        if self.sync_quality == SyncQuality.PERFECT:
            self.sync_validator.sync_tolerance = 0.01
        elif self.sync_quality == SyncQuality.ENHANCED:
            self.sync_validator.sync_tolerance = 0.05
        else:
            self.sync_validator.sync_tolerance = 0.1

        logger.info(f"同步质量设置为: {self.sync_quality.value}")

    def on_time_clicked(self, time: float):
        """时间点击事件"""
        self.set_current_time(time)

    def on_time_changed(self, time: float):
        """时间改变事件"""
        self.set_current_time(time)

    def set_current_time(self, time: float):
        """设置当前时间"""
        # 根据精度调整时间
        precision_value = self.time_precision.value
        self.current_time = round(time / precision_value) * precision_value

        # 更新显示
        self.update_time_display()
        self.waveform_widget.set_current_time(self.current_time)
        self.segments_widget.set_current_time(self.current_time)

        # 发送信号
        self.time_changed.emit(self.current_time)

    def update_time_display(self):
        """更新时间显示"""
        current_min = int(self.current_time // 60)
        current_sec = self.current_time % 60
        total_min = int(self.duration // 60)
        total_sec = self.duration % 60

        # 根据精度显示小数位
        if self.time_precision == TimePrecision.ULTRA_FINE:
            time_format = f"{current_min:02d}:{current_sec:05.2f} / {total_min:02d}:{total_sec:05.2f}"
        elif self.time_precision == TimePrecision.FINE:
            time_format = f"{current_min:02d}:{current_sec:04.1f} / {total_min:02d}:{total_sec:04.1f}"
        else:
            time_format = f"{current_min:02d}:{current_sec:02.0f} / {total_min:02d}:{total_sec:02.0f}"

        self.time_label.setText(time_format)

    def toggle_playback(self):
        """切换播放状态"""
        if self.is_playing:
            self.pause_playback()
        else:
            self.start_playback()

    def start_playback(self):
        """开始播放"""
        self.is_playing = True
        self.play_btn.setText("⏸️")
        # TODO: 实现实际的音频播放

    def pause_playback(self):
        """暂停播放"""
        self.is_playing = False
        self.play_btn.setText("▶️")
        # TODO: 实现实际的音频暂停

    def stop_playback(self):
        """停止播放"""
        self.is_playing = False
        self.play_btn.setText("▶️")
        self.set_current_time(0.0)
        # TODO: 实现实际的音频停止

    def on_zoom_changed(self, value):
        """缩放改变事件"""
        self.zoom_level = value / 100.0
        self.waveform_widget.set_zoom_level(self.zoom_level)
        self.segments_widget.set_zoom_level(self.zoom_level)

    def on_segment_selected(self, segment_id: str):
        """时间段选择事件"""
        self.selected_segment_id = segment_id
        self.segment_selected.emit(segment_id)

    def on_segment_created(self, segment_data: dict):
        """时间段创建事件"""
        self.segment_created.emit(segment_data)

    def on_segment_modified(self, segment_id: str, changes: dict):
        """时间段修改事件"""
        self.segment_modified.emit(segment_id, changes)

    def get_segments(self) -> List[PreciseTimeSegment]:
        """获取时间段列表"""
        return self.segments.copy()

    def add_segment(self, segment: PreciseTimeSegment):
        """添加时间段"""
        self.segments.append(segment)
        self.segments_widget.set_segments(self.segments)
        self.validate_sync()

    def remove_segment(self, segment_id: str):
        """移除时间段"""
        self.segments = [s for s in self.segments if s.segment_id != segment_id]
        self.segments_widget.set_segments(self.segments)
        self.validate_sync()


class PreciseWaveformWidget(QWidget):
    """精确波形显示组件"""

    # 信号定义
    time_clicked = pyqtSignal(float)        # 时间点击信号
    time_changed = pyqtSignal(float)        # 时间改变信号
    region_selected = pyqtSignal(float, float)  # 区域选择信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_data = np.array([])
        self.sample_rate = 22050
        self.audio_features = []
        self.current_time = 0.0
        self.duration = 0.0
        self.zoom_level = 1.0
        self.time_precision = TimePrecision.FINE

        # 选择状态
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False

        self.setMinimumHeight(120)
        self.setMouseTracking(True)

        logger.info("精确波形显示组件初始化完成")

    def set_audio_data(self, audio_data: np.ndarray, sample_rate: int):
        """设置音频数据"""
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.duration = len(audio_data) / sample_rate if len(audio_data) > 0 else 0.0
        self.update()

    def set_audio_features(self, features: List[AudioFeature]):
        """设置音频特征"""
        self.audio_features = features
        self.update()

    def set_current_time(self, time: float):
        """设置当前时间"""
        self.current_time = time
        self.update()

    def set_zoom_level(self, zoom: float):
        """设置缩放级别"""
        self.zoom_level = zoom
        self.update()

    def set_time_precision(self, precision: TimePrecision):
        """设置时间精度"""
        self.time_precision = precision
        self.update()

    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        width = rect.width()
        height = rect.height()

        # 绘制背景
        painter.fillRect(rect, QColor("#1e1e1e"))

        if len(self.audio_data) == 0:
            painter.setPen(QColor("#666666"))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "请加载音频文件")
            return

        # 绘制波形
        self.draw_waveform(painter, width, height)

        # 绘制音频特征
        self.draw_audio_features(painter, width, height)

        # 绘制时间刻度
        self.draw_time_scale(painter, width, height)

        # 绘制当前时间指示器
        self.draw_current_time_indicator(painter, width, height)

        # 绘制选择区域
        if self.selection_start is not None and self.selection_end is not None:
            self.draw_selection(painter, width, height)

    def draw_waveform(self, painter: QPainter, width: int, height: int):
        """绘制波形"""
        try:
            if len(self.audio_data) == 0:
                return

            # 计算显示范围
            visible_duration = self.duration / self.zoom_level
            start_time = max(0, self.current_time - visible_duration / 2)
            end_time = min(self.duration, start_time + visible_duration)

            # 转换为样本索引
            start_sample = int(start_time * self.sample_rate)
            end_sample = int(end_time * self.sample_rate)

            if start_sample >= len(self.audio_data):
                return

            # 获取显示的音频数据
            display_data = self.audio_data[start_sample:end_sample]

            if len(display_data) == 0:
                return

            # 下采样以适应显示宽度
            samples_per_pixel = max(1, len(display_data) // width)
            downsampled_data = []

            for i in range(0, len(display_data), samples_per_pixel):
                chunk = display_data[i:i + samples_per_pixel]
                if len(chunk) > 0:
                    downsampled_data.append(np.max(np.abs(chunk)))

            # 绘制波形
            painter.setPen(QPen(QColor("#4caf50"), 1))

            for i, amplitude in enumerate(downsampled_data):
                if i >= width:
                    break

                x = i
                wave_height = int(amplitude * height * 0.4)  # 波形高度占40%
                center_y = height // 2

                painter.drawLine(x, center_y - wave_height, x, center_y + wave_height)

        except Exception as e:
            logger.error(f"绘制波形失败: {e}")

    def draw_audio_features(self, painter: QPainter, width: int, height: int):
        """绘制音频特征"""
        try:
            if not self.audio_features or self.duration == 0:
                return

            # 计算显示范围
            visible_duration = self.duration / self.zoom_level
            start_time = max(0, self.current_time - visible_duration / 2)
            end_time = min(self.duration, start_time + visible_duration)

            for feature in self.audio_features:
                # 检查特征是否在可见范围内
                if feature.end_time < start_time or feature.start_time > end_time:
                    continue

                # 计算特征在屏幕上的位置
                feature_start_x = int((feature.start_time - start_time) / visible_duration * width)
                feature_end_x = int((feature.end_time - start_time) / visible_duration * width)

                # 根据特征类型选择颜色
                if feature.feature_type == AudioFeatureType.SPEECH:
                    color = QColor("#2196f3")  # 蓝色
                elif feature.feature_type == AudioFeatureType.SILENCE:
                    color = QColor("#757575")  # 灰色
                elif feature.feature_type == AudioFeatureType.TRANSITION:
                    color = QColor("#ff9800")  # 橙色
                else:
                    color = QColor("#9c27b0")  # 紫色

                # 绘制特征区域
                painter.fillRect(feature_start_x, height - 20,
                               feature_end_x - feature_start_x, 20,
                               QColor(color.red(), color.green(), color.blue(), 100))

                # 绘制特征边界
                painter.setPen(QPen(color, 2))
                painter.drawLine(feature_start_x, height - 20, feature_start_x, height)
                painter.drawLine(feature_end_x, height - 20, feature_end_x, height)

        except Exception as e:
            logger.error(f"绘制音频特征失败: {e}")

    def draw_time_scale(self, painter: QPainter, width: int, height: int):
        """绘制时间刻度"""
        try:
            if self.duration == 0:
                return

            # 计算显示范围
            visible_duration = self.duration / self.zoom_level
            start_time = max(0, self.current_time - visible_duration / 2)

            # 根据精度和缩放级别确定刻度间隔
            if self.time_precision == TimePrecision.ULTRA_FINE:
                interval = 0.1 if visible_duration < 10 else 1.0
            elif self.time_precision == TimePrecision.FINE:
                interval = 0.5 if visible_duration < 30 else 5.0
            else:
                interval = 1.0 if visible_duration < 60 else 10.0

            # 绘制刻度
            painter.setPen(QPen(QColor("#666666"), 1))
            painter.setFont(QFont("Consolas", 8))

            current_mark = math.ceil(start_time / interval) * interval
            while current_mark <= start_time + visible_duration:
                x = int((current_mark - start_time) / visible_duration * width)

                if 0 <= x <= width:
                    # 绘制刻度线
                    painter.drawLine(x, height - 30, x, height - 20)

                    # 绘制时间标签
                    if self.time_precision == TimePrecision.ULTRA_FINE:
                        time_text = f"{current_mark:.2f}s"
                    elif self.time_precision == TimePrecision.FINE:
                        time_text = f"{current_mark:.1f}s"
                    else:
                        time_text = f"{current_mark:.0f}s"

                    painter.drawText(x + 2, height - 5, time_text)

                current_mark += interval

        except Exception as e:
            logger.error(f"绘制时间刻度失败: {e}")

    def draw_current_time_indicator(self, painter: QPainter, width: int, height: int):
        """绘制当前时间指示器"""
        try:
            if self.duration == 0:
                return

            # 计算显示范围
            visible_duration = self.duration / self.zoom_level
            start_time = max(0, self.current_time - visible_duration / 2)

            # 计算当前时间在屏幕上的位置
            if start_time <= self.current_time <= start_time + visible_duration:
                x = int((self.current_time - start_time) / visible_duration * width)

                # 绘制时间线
                painter.setPen(QPen(QColor("#f44336"), 3))
                painter.drawLine(x, 0, x, height)

                # 绘制时间标签
                painter.setPen(QPen(QColor("#ffffff"), 1))
                painter.fillRect(x - 30, 5, 60, 20, QColor("#f44336"))
                painter.drawText(x - 25, 20, f"{self.current_time:.1f}s")

        except Exception as e:
            logger.error(f"绘制当前时间指示器失败: {e}")

    def draw_selection(self, painter: QPainter, width: int, height: int):
        """绘制选择区域"""
        try:
            if self.duration == 0:
                return

            # 计算显示范围
            visible_duration = self.duration / self.zoom_level
            start_time = max(0, self.current_time - visible_duration / 2)

            # 计算选择区域在屏幕上的位置
            sel_start_x = int((self.selection_start - start_time) / visible_duration * width)
            sel_end_x = int((self.selection_end - start_time) / visible_duration * width)

            # 绘制选择区域
            painter.fillRect(sel_start_x, 0, sel_end_x - sel_start_x, height,
                           QColor(255, 255, 0, 50))  # 半透明黄色

            # 绘制选择边界
            painter.setPen(QPen(QColor("#ffeb3b"), 2))
            painter.drawLine(sel_start_x, 0, sel_start_x, height)
            painter.drawLine(sel_end_x, 0, sel_end_x, height)

        except Exception as e:
            logger.error(f"绘制选择区域失败: {e}")

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            time = self.pixel_to_time(event.position().x())

            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                # Shift+点击开始选择
                self.selection_start = time
                self.is_selecting = True
            else:
                # 普通点击设置当前时间
                self.time_clicked.emit(time)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_selecting:
            self.selection_end = self.pixel_to_time(event.position().x())
            self.update()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.is_selecting and event.button() == Qt.MouseButton.LeftButton:
            self.is_selecting = False

            if self.selection_start is not None and self.selection_end is not None:
                # 确保开始时间小于结束时间
                start = min(self.selection_start, self.selection_end)
                end = max(self.selection_start, self.selection_end)

                if end - start > 0.1:  # 最小选择长度0.1秒
                    self.region_selected.emit(start, end)

    def pixel_to_time(self, x: float) -> float:
        """像素坐标转换为时间"""
        if self.duration == 0:
            return 0.0

        visible_duration = self.duration / self.zoom_level
        start_time = max(0, self.current_time - visible_duration / 2)

        time = start_time + (x / self.width()) * visible_duration

        # 根据精度调整
        precision_value = self.time_precision.value
        return round(time / precision_value) * precision_value

    def wheelEvent(self, event):
        """鼠标滚轮事件（缩放）"""
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9

        new_zoom = self.zoom_level * zoom_factor
        new_zoom = max(0.1, min(10.0, new_zoom))  # 限制缩放范围

        if new_zoom != self.zoom_level:
            self.zoom_level = new_zoom
            self.update()


class TimeSegmentsWidget(QWidget):
    """时间段显示组件"""

    # 信号定义
    segment_selected = pyqtSignal(str)              # 时间段选择信号
    segment_created = pyqtSignal(dict)              # 时间段创建信号
    segment_modified = pyqtSignal(str, dict)        # 时间段修改信号
    segment_deleted = pyqtSignal(str)               # 时间段删除信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.segments = []
        self.duration = 0.0
        self.current_time = 0.0
        self.zoom_level = 1.0
        self.time_precision = TimePrecision.FINE
        self.selected_segment_id = None

        # 拖拽状态
        self.dragging_segment = None
        self.drag_start_pos = None
        self.drag_mode = None  # 'move', 'resize_start', 'resize_end'

        self.setMinimumHeight(100)
        self.setMouseTracking(True)

        logger.info("时间段显示组件初始化完成")

    def set_segments(self, segments: List[PreciseTimeSegment]):
        """设置时间段列表"""
        self.segments = segments
        self.update()

    def set_duration(self, duration: float):
        """设置总时长"""
        self.duration = duration
        self.update()

    def set_current_time(self, time: float):
        """设置当前时间"""
        self.current_time = time
        self.update()

    def set_zoom_level(self, zoom: float):
        """设置缩放级别"""
        self.zoom_level = zoom
        self.update()

    def set_time_precision(self, precision: TimePrecision):
        """设置时间精度"""
        self.time_precision = precision
        self.update()

    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        width = rect.width()
        height = rect.height()

        # 绘制背景
        painter.fillRect(rect, QColor("#2e2e2e"))

        if self.duration == 0:
            painter.setPen(QColor("#666666"))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "请设置时长")
            return

        # 绘制时间段
        self.draw_segments(painter, width, height)

        # 绘制当前时间指示器
        self.draw_current_time_indicator(painter, width, height)

    def draw_segments(self, painter: QPainter, width: int, height: int):
        """绘制时间段"""
        try:
            # 计算显示范围
            visible_duration = self.duration / self.zoom_level
            start_time = max(0, self.current_time - visible_duration / 2)
            end_time = min(self.duration, start_time + visible_duration)

            for segment in self.segments:
                # 检查时间段是否在可见范围内
                if segment.end_time < start_time or segment.start_time > end_time:
                    continue

                # 计算时间段在屏幕上的位置
                seg_start_x = int((segment.start_time - start_time) / visible_duration * width)
                seg_end_x = int((segment.end_time - start_time) / visible_duration * width)
                seg_width = seg_end_x - seg_start_x

                # 根据时间段类型选择颜色
                if segment.segment_id == self.selected_segment_id:
                    color = QColor("#ff5722")  # 选中颜色
                elif segment.auto_generated:
                    color = QColor("#9c27b0")  # 自动生成颜色
                else:
                    color = QColor("#2196f3")  # 默认颜色

                # 绘制时间段矩形
                painter.fillRect(seg_start_x, 10, seg_width, height - 20, color)

                # 绘制边框
                painter.setPen(QPen(QColor("#ffffff"), 1))
                painter.drawRect(seg_start_x, 10, seg_width, height - 20)

                # 绘制时间段文本
                if seg_width > 50:  # 只有足够宽度时才显示文本
                    painter.setPen(QColor("#ffffff"))
                    painter.setFont(QFont("Microsoft YaHei", 8))

                    # 时间段描述
                    text_rect = QRect(seg_start_x + 5, 15, seg_width - 10, 20)
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft, segment.description)

                    # 时间信息
                    time_text = f"{segment.start_time:.1f}s - {segment.end_time:.1f}s"
                    time_rect = QRect(seg_start_x + 5, height - 25, seg_width - 10, 15)
                    painter.drawText(time_rect, Qt.AlignmentFlag.AlignLeft, time_text)

                # 绘制调整手柄
                if segment.segment_id == self.selected_segment_id:
                    # 左侧调整手柄
                    painter.fillRect(seg_start_x - 3, 10, 6, height - 20, QColor("#ffffff"))
                    # 右侧调整手柄
                    painter.fillRect(seg_end_x - 3, 10, 6, height - 20, QColor("#ffffff"))

        except Exception as e:
            logger.error(f"绘制时间段失败: {e}")

    def draw_current_time_indicator(self, painter: QPainter, width: int, height: int):
        """绘制当前时间指示器"""
        try:
            if self.duration == 0:
                return

            # 计算显示范围
            visible_duration = self.duration / self.zoom_level
            start_time = max(0, self.current_time - visible_duration / 2)

            # 计算当前时间在屏幕上的位置
            if start_time <= self.current_time <= start_time + visible_duration:
                x = int((self.current_time - start_time) / visible_duration * width)

                # 绘制时间线
                painter.setPen(QPen(QColor("#f44336"), 2))
                painter.drawLine(x, 0, x, height)

        except Exception as e:
            logger.error(f"绘制当前时间指示器失败: {e}")

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            time = self.pixel_to_time(event.position().x())
            segment = self.find_segment_at_time(time)

            if segment:
                self.selected_segment_id = segment.segment_id
                self.segment_selected.emit(segment.segment_id)

                # 检查是否点击在调整手柄上
                self.drag_mode = self.get_drag_mode(event.position().x(), segment)
                if self.drag_mode:
                    self.dragging_segment = segment
                    self.drag_start_pos = event.position()

                self.update()
            else:
                # 点击空白区域，取消选择
                self.selected_segment_id = None
                self.update()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.dragging_segment and self.drag_mode:
            # 计算时间偏移
            time_offset = self.pixel_to_time(event.position().x()) - self.pixel_to_time(self.drag_start_pos.x())

            # 根据拖拽模式调整时间段
            if self.drag_mode == 'move':
                # 移动整个时间段
                new_start = max(0, self.dragging_segment.start_time + time_offset)
                new_end = new_start + self.dragging_segment.duration

                if new_end <= self.duration:
                    self.dragging_segment.start_time = new_start
                    self.dragging_segment.end_time = new_end

            elif self.drag_mode == 'resize_start':
                # 调整开始时间
                new_start = max(0, self.dragging_segment.start_time + time_offset)
                if new_start < self.dragging_segment.end_time - 0.1:  # 最小时长0.1秒
                    self.dragging_segment.start_time = new_start

            elif self.drag_mode == 'resize_end':
                # 调整结束时间
                new_end = min(self.duration, self.dragging_segment.end_time + time_offset)
                if new_end > self.dragging_segment.start_time + 0.1:  # 最小时长0.1秒
                    self.dragging_segment.end_time = new_end

            self.update()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.dragging_segment and self.drag_mode:
            # 发送修改信号
            changes = {
                "start_time": self.dragging_segment.start_time,
                "end_time": self.dragging_segment.end_time
            }
            self.segment_modified.emit(self.dragging_segment.segment_id, changes)

            # 重置拖拽状态
            self.dragging_segment = None
            self.drag_mode = None
            self.drag_start_pos = None

    def find_segment_at_time(self, time: float) -> Optional[PreciseTimeSegment]:
        """查找指定时间的时间段"""
        for segment in self.segments:
            if segment.start_time <= time <= segment.end_time:
                return segment
        return None

    def get_drag_mode(self, x: float, segment: PreciseTimeSegment) -> Optional[str]:
        """获取拖拽模式"""
        # 计算时间段在屏幕上的位置
        visible_duration = self.duration / self.zoom_level
        start_time = max(0, self.current_time - visible_duration / 2)

        seg_start_x = int((segment.start_time - start_time) / visible_duration * self.width())
        seg_end_x = int((segment.end_time - start_time) / visible_duration * self.width())

        # 检查是否在调整手柄范围内
        if abs(x - seg_start_x) <= 5:
            return 'resize_start'
        elif abs(x - seg_end_x) <= 5:
            return 'resize_end'
        elif seg_start_x <= x <= seg_end_x:
            return 'move'

        return None

    def pixel_to_time(self, x: float) -> float:
        """像素坐标转换为时间"""
        if self.duration == 0:
            return 0.0

        visible_duration = self.duration / self.zoom_level
        start_time = max(0, self.current_time - visible_duration / 2)

        time = start_time + (x / self.width()) * visible_duration

        # 根据精度调整
        precision_value = self.time_precision.value
        return round(time / precision_value) * precision_value
