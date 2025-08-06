"""
AI Animation Studio - 全屏预览对话框
提供沉浸式的全屏动画预览体验
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QPushButton, QFrame, QSlider, QComboBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QColor, QPalette

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    from PyQt6.QtWidgets import QTextEdit
    WEB_ENGINE_AVAILABLE = False

from core.logger import get_logger

logger = get_logger("fullscreen_preview_dialog")


class FullscreenPreviewDialog(QDialog):
    """全屏预览对话框"""
    
    # 信号定义
    playback_state_changed = pyqtSignal(bool)  # 播放状态改变
    time_changed = pyqtSignal(float)  # 时间改变
    
    def __init__(self, html_content: str, parent=None):
        super().__init__(parent)
        
        self.html_content = html_content
        self.is_playing = False
        self.current_time = 0.0
        self.total_duration = 10.0
        self.playback_speed = 1.0
        self.controls_visible = True
        self.auto_hide_timer = QTimer()
        
        self.setup_ui()
        self.setup_shortcuts()
        self.setup_auto_hide()
        self.load_content()
        
        logger.info("全屏预览对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        # 设置为全屏无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        # 设置黑色背景
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 预览区域
        self.preview_area = self.create_preview_area()
        layout.addWidget(self.preview_area)
        
        # 控制栏（可隐藏）
        self.control_bar = self.create_control_bar()
        layout.addWidget(self.control_bar)
        
        # 播放定时器
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.update_time)
        self.play_timer.setInterval(50)  # 20fps
    
    def create_preview_area(self):
        """创建预览区域"""
        area = QWidget()
        area.setStyleSheet("background-color: #000000;")
        
        layout = QVBoxLayout(area)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建WebView或文本预览
        if WEB_ENGINE_AVAILABLE:
            self.web_view = QWebEngineView()
            self.web_view.setStyleSheet("background-color: #000000;")
            layout.addWidget(self.web_view)
        else:
            self.text_view = QTextEdit()
            self.text_view.setReadOnly(True)
            self.text_view.setStyleSheet("""
                QTextEdit {
                    background-color: #000000;
                    color: #ffffff;
                    border: none;
                    font-family: 'Consolas', monospace;
                    font-size: 14px;
                }
            """)
            layout.addWidget(self.text_view)
        
        return area
    
    def create_control_bar(self):
        """创建控制栏"""
        control_bar = QFrame()
        control_bar.setFixedHeight(80)
        control_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 180);
                border-top: 1px solid rgba(255, 255, 255, 50);
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 20);
                color: white;
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 40);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 60);
            }
            QSlider::groove:horizontal {
                border: 1px solid rgba(255, 255, 255, 50);
                height: 6px;
                background: rgba(255, 255, 255, 20);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 1px solid rgba(255, 255, 255, 100);
                width: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }
            QSlider::sub-page:horizontal {
                background: #007bff;
                border-radius: 3px;
            }
            QComboBox {
                background-color: rgba(255, 255, 255, 20);
                color: white;
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 3px;
                padding: 5px;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
        """)
        
        layout = QHBoxLayout(control_bar)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # 播放控制
        self.play_btn = QPushButton("▶️ 播放")
        self.play_btn.clicked.connect(self.toggle_play)
        layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_animation)
        layout.addWidget(self.stop_btn)
        
        # 时间滑块
        layout.addWidget(QLabel("时间:"))
        
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 1000)
        self.time_slider.setValue(0)
        self.time_slider.valueChanged.connect(self.seek_time)
        layout.addWidget(self.time_slider)
        
        self.time_label = QLabel("00:00 / 10:00")
        self.time_label.setFont(QFont("Consolas", 10))
        layout.addWidget(self.time_label)
        
        layout.addWidget(QLabel("|"))
        
        # 播放速度
        layout.addWidget(QLabel("速度:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "1.0x", "1.5x", "2.0x"])
        self.speed_combo.setCurrentText("1.0x")
        self.speed_combo.currentTextChanged.connect(self.change_speed)
        layout.addWidget(self.speed_combo)
        
        layout.addStretch()
        
        # 控制按钮
        self.hide_controls_btn = QPushButton("👁️ 隐藏控制")
        self.hide_controls_btn.clicked.connect(self.toggle_controls)
        layout.addWidget(self.hide_controls_btn)
        
        self.exit_btn = QPushButton("❌ 退出全屏")
        self.exit_btn.clicked.connect(self.close)
        layout.addWidget(self.exit_btn)
        
        return control_bar
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # 退出全屏
        exit_shortcut = QShortcut(QKeySequence("Escape"), self)
        exit_shortcut.activated.connect(self.close)
        
        # 播放/暂停
        play_shortcut = QShortcut(QKeySequence("Space"), self)
        play_shortcut.activated.connect(self.toggle_play)
        
        # 全屏切换
        fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        fullscreen_shortcut.activated.connect(self.close)
        
        # 隐藏/显示控制
        hide_shortcut = QShortcut(QKeySequence("H"), self)
        hide_shortcut.activated.connect(self.toggle_controls)
        
        # 重置动画
        reset_shortcut = QShortcut(QKeySequence("R"), self)
        reset_shortcut.activated.connect(self.reset_animation)
    
    def setup_auto_hide(self):
        """设置自动隐藏控制栏"""
        self.auto_hide_timer.timeout.connect(self.auto_hide_controls)
        self.auto_hide_timer.setSingleShot(True)
        
        # 鼠标移动时重置定时器
        self.setMouseTracking(True)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        super().mouseMoveEvent(event)
        
        # 显示控制栏
        if not self.controls_visible:
            self.show_controls()
        
        # 重置自动隐藏定时器
        self.auto_hide_timer.start(3000)  # 3秒后自动隐藏
    
    def load_content(self):
        """加载内容"""
        try:
            if WEB_ENGINE_AVAILABLE and hasattr(self, 'web_view'):
                self.web_view.setHtml(self.html_content)
            elif hasattr(self, 'text_view'):
                self.text_view.setPlainText(self.html_content)
            
            logger.info("全屏预览内容已加载")
            
        except Exception as e:
            logger.error(f"加载全屏预览内容失败: {e}")
    
    def toggle_play(self):
        """切换播放状态"""
        try:
            if self.is_playing:
                self.pause_animation()
            else:
                self.play_animation()
                
        except Exception as e:
            logger.error(f"切换播放状态失败: {e}")
    
    def play_animation(self):
        """播放动画"""
        try:
            self.is_playing = True
            self.play_btn.setText("⏸️ 暂停")
            self.play_timer.start()
            
            # 在WebView中重新加载以重新开始动画
            if WEB_ENGINE_AVAILABLE and hasattr(self, 'web_view'):
                self.web_view.reload()
            
            self.playback_state_changed.emit(True)
            logger.info("全屏预览开始播放")
            
        except Exception as e:
            logger.error(f"播放动画失败: {e}")
    
    def pause_animation(self):
        """暂停动画"""
        try:
            self.is_playing = False
            self.play_btn.setText("▶️ 播放")
            self.play_timer.stop()
            
            self.playback_state_changed.emit(False)
            logger.info("全屏预览已暂停")
            
        except Exception as e:
            logger.error(f"暂停动画失败: {e}")
    
    def stop_animation(self):
        """停止动画"""
        try:
            self.is_playing = False
            self.current_time = 0.0
            self.play_btn.setText("▶️ 播放")
            self.play_timer.stop()
            
            # 重置时间滑块
            self.time_slider.setValue(0)
            self.update_time_display()
            
            # 重新加载内容
            self.load_content()
            
            logger.info("全屏预览已停止")
            
        except Exception as e:
            logger.error(f"停止动画失败: {e}")
    
    def reset_animation(self):
        """重置动画"""
        try:
            self.stop_animation()
            logger.info("全屏预览已重置")
            
        except Exception as e:
            logger.error(f"重置动画失败: {e}")
    
    def seek_time(self, value):
        """跳转时间"""
        try:
            self.current_time = (value / 1000.0) * self.total_duration
            self.update_time_display()
            self.time_changed.emit(self.current_time)
            
        except Exception as e:
            logger.error(f"跳转时间失败: {e}")
    
    def update_time(self):
        """更新时间"""
        try:
            if self.is_playing:
                self.current_time += 0.05 * self.playback_speed
                
                if self.current_time >= self.total_duration:
                    # 循环播放
                    self.current_time = 0.0
                
                # 更新滑块
                progress = int((self.current_time / self.total_duration) * 1000)
                self.time_slider.setValue(progress)
                
                self.update_time_display()
                self.time_changed.emit(self.current_time)
            
        except Exception as e:
            logger.error(f"更新时间失败: {e}")
    
    def update_time_display(self):
        """更新时间显示"""
        try:
            current_min = int(self.current_time // 60)
            current_sec = int(self.current_time % 60)
            total_min = int(self.total_duration // 60)
            total_sec = int(self.total_duration % 60)
            
            time_text = f"{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}"
            self.time_label.setText(time_text)
            
        except Exception as e:
            logger.error(f"更新时间显示失败: {e}")
    
    def change_speed(self, speed_text: str):
        """改变播放速度"""
        try:
            self.playback_speed = float(speed_text.replace('x', ''))
            
            # 调整定时器间隔
            base_interval = 50
            new_interval = int(base_interval / self.playback_speed)
            self.play_timer.setInterval(new_interval)
            
            logger.info(f"播放速度已设置为: {speed_text}")
            
        except Exception as e:
            logger.error(f"改变播放速度失败: {e}")
    
    def toggle_controls(self):
        """切换控制栏显示"""
        try:
            if self.controls_visible:
                self.hide_controls()
            else:
                self.show_controls()
                
        except Exception as e:
            logger.error(f"切换控制栏显示失败: {e}")
    
    def hide_controls(self):
        """隐藏控制栏"""
        try:
            self.controls_visible = False
            self.control_bar.hide()
            self.hide_controls_btn.setText("👁️ 显示控制")
            
            # 停止自动隐藏定时器
            self.auto_hide_timer.stop()
            
        except Exception as e:
            logger.error(f"隐藏控制栏失败: {e}")
    
    def show_controls(self):
        """显示控制栏"""
        try:
            self.controls_visible = True
            self.control_bar.show()
            self.hide_controls_btn.setText("👁️ 隐藏控制")
            
        except Exception as e:
            logger.error(f"显示控制栏失败: {e}")
    
    def auto_hide_controls(self):
        """自动隐藏控制栏"""
        try:
            if self.controls_visible:
                self.hide_controls()
                
        except Exception as e:
            logger.error(f"自动隐藏控制栏失败: {e}")
    
    def keyPressEvent(self, event):
        """键盘事件"""
        try:
            if event.key() == Qt.Key.Key_Escape:
                self.close()
            elif event.key() == Qt.Key.Key_Space:
                self.toggle_play()
            elif event.key() == Qt.Key.Key_H:
                self.toggle_controls()
            elif event.key() == Qt.Key.Key_R:
                self.reset_animation()
            else:
                super().keyPressEvent(event)
                
        except Exception as e:
            logger.error(f"处理键盘事件失败: {e}")
    
    def closeEvent(self, event):
        """关闭事件"""
        try:
            # 停止播放
            if self.is_playing:
                self.stop_animation()
            
            # 停止定时器
            self.play_timer.stop()
            self.auto_hide_timer.stop()
            
            logger.info("全屏预览对话框已关闭")
            super().closeEvent(event)
            
        except Exception as e:
            logger.error(f"关闭全屏预览对话框失败: {e}")
            super().closeEvent(event)
