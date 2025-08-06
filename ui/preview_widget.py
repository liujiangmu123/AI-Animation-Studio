"""
AI Animation Studio - 动画预览组件
基于参考代码的HTML预览功能，支持实时预览和播放控制
"""

import os
import tempfile
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QSlider, QDoubleSpinBox, QPlainTextEdit, QTabWidget, QMessageBox,
    QSplitter, QComboBox, QCheckBox, QSpinBox, QProgressBar, QListWidget,
    QListWidgetItem, QTreeWidget, QTreeWidgetItem, QHeaderView, QFormLayout,
    QScrollArea, QFrame, QToolButton, QMenu, QDialog, QDialogButtonBox,
    QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, QUrl, pyqtSignal, QThread, QPropertyAnimation, QEasingCurve
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QAction

from core.logger import get_logger

logger = get_logger("preview_widget")

class AnimationPreviewController(QWidget):
    """动画预览控制器 - 基于参考代码"""
    
    time_changed = pyqtSignal(float)  # 时间改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.html_file = None
        self.duration = 10.0  # 默认动画时长
        self.current_time = 0.0
        self.page_ready = False  # 页面就绪状态
        self.is_playing = False
        
        self.setup_ui()
        self.setup_web_engine()
        
        # 播放定时器
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.advance_time)
        self.play_timer.setInterval(50)  # 20fps预览

        # 性能监控
        self.fps_counter = 0
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self.update_fps_display)
        self.fps_timer.start(1000)  # 每秒更新FPS

        self.last_frame_time = 0
        self.frame_times = []
        
        logger.info("动画预览控制器初始化完成")

    def setup_web_engine(self):
        """配置WebEngine支持Three.js等库"""
        # 获取默认配置文件
        profile = QWebEngineProfile.defaultProfile()
        settings = profile.settings()

        # 启用WebGL和其他必要功能
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

        # 启用本地存储
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)

        logger.info("✅ WebEngine配置完成：启用WebGL、Canvas2D、JavaScript")

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 预览窗口
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(400)
        layout.addWidget(self.web_view)

        # 调试信息区域
        debug_group = QGroupBox("调试信息")
        debug_layout = QVBoxLayout(debug_group)
        self.debug_text = QPlainTextEdit()
        self.debug_text.setMaximumHeight(100)
        self.debug_text.setReadOnly(True)
        debug_layout.addWidget(self.debug_text)
        layout.addWidget(debug_group)

        # 控制面板
        control_panel = QGroupBox("预览控制")
        control_layout = QVBoxLayout(control_panel)

        # 页面状态指示
        status_layout = QHBoxLayout()
        self.status_label = QLabel("📄 等待加载...")
        self.status_label.setStyleSheet("color: #666; font-weight: bold;")
        status_layout.addWidget(self.status_label)

        self.reload_btn = QPushButton("🔄 重新加载")
        self.reload_btn.clicked.connect(self.reload_page)
        status_layout.addWidget(self.reload_btn)
        status_layout.addStretch()
        control_layout.addLayout(status_layout)
        
        # 播放控制按钮
        play_layout = QHBoxLayout()

        self.play_btn = QPushButton("▶️ 播放")
        self.play_btn.clicked.connect(self.play_animation)
        play_layout.addWidget(self.play_btn)

        self.pause_btn = QPushButton("⏸️ 暂停")
        self.pause_btn.clicked.connect(self.pause_animation)
        self.pause_btn.setEnabled(False)
        play_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_animation)
        play_layout.addWidget(self.stop_btn)

        play_layout.addStretch()
        control_layout.addLayout(play_layout)

        # 时间滑块
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("时间:"))
        
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 1000)
        self.time_slider.setValue(0)
        self.time_slider.valueChanged.connect(self.on_time_changed)
        slider_layout.addWidget(self.time_slider)
        
        self.time_label = QLabel("0.0s / 10.0s")
        slider_layout.addWidget(self.time_label)
        
        control_layout.addLayout(slider_layout)
        
        # 播放控制按钮
        btn_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("▶ 播放")
        self.play_btn.clicked.connect(self.toggle_play)
        btn_layout.addWidget(self.play_btn)
        
        self.reset_btn = QPushButton("⏮ 重置")
        self.reset_btn.clicked.connect(self.reset_animation)
        btn_layout.addWidget(self.reset_btn)

        # 增强功能按钮
        btn_layout.addWidget(QLabel("|"))

        # 全屏按钮
        self.fullscreen_btn = QPushButton("🔍 全屏")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        self.fullscreen_btn.setToolTip("切换全屏预览模式")
        btn_layout.addWidget(self.fullscreen_btn)

        # 录制按钮
        self.record_btn = QPushButton("🎥 录制")
        self.record_btn.clicked.connect(self.toggle_recording)
        self.record_btn.setToolTip("录制动画为视频")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        btn_layout.addWidget(self.record_btn)

        # 截图按钮
        self.screenshot_btn = QPushButton("📷 截图")
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        self.screenshot_btn.setToolTip("截取当前帧")
        btn_layout.addWidget(self.screenshot_btn)

        btn_layout.addWidget(QLabel("|"))

        # 播放速度控制
        btn_layout.addWidget(QLabel("速度:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "1.0x", "1.5x", "2.0x"])
        self.speed_combo.setCurrentText("1.0x")
        self.speed_combo.currentTextChanged.connect(self.change_playback_speed)
        self.speed_combo.setMaximumWidth(80)
        btn_layout.addWidget(self.speed_combo)

        # 时长设置
        btn_layout.addWidget(QLabel("时长:"))
        self.duration_spinbox = QDoubleSpinBox()
        self.duration_spinbox.setRange(1.0, 60.0)
        self.duration_spinbox.setValue(self.duration)
        self.duration_spinbox.setSuffix("s")
        self.duration_spinbox.valueChanged.connect(self.update_duration)
        self.duration_spinbox.setMaximumWidth(80)
        btn_layout.addWidget(self.duration_spinbox)

        btn_layout.addStretch()

        # 性能监控
        self.fps_label = QLabel("FPS: --")
        self.fps_label.setStyleSheet("color: #666; font-size: 11px;")
        btn_layout.addWidget(self.fps_label)
        
        control_layout.addLayout(btn_layout)
        layout.addWidget(control_panel)

    def debug_log(self, message):
        """添加调试日志"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        self.debug_text.appendPlainText(f"[{timestamp}] {message}")
        logger.info(f"[预览调试] {message}")

    def load_html(self, html_file):
        """加载HTML文件"""
        self.html_file = html_file
        self.page_ready = False

        if html_file and os.path.exists(html_file):
            # 断开之前的连接
            try:
                self.web_view.loadFinished.disconnect()
            except:
                pass

            # 连接加载完成信号
            self.web_view.loadFinished.connect(self.on_page_loaded)

            url = QUrl.fromLocalFile(os.path.abspath(html_file))
            self.debug_log(f"开始加载: {url.toString()}")
            self.status_label.setText("📄 正在加载...")
            self.web_view.load(url)
        else:
            self.debug_log(f"文件不存在: {html_file}")
            self.status_label.setText("❌ 文件不存在")

    def load_html_content(self, html_content: str):
        """加载HTML内容"""
        try:
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
            temp_file.write(html_content)
            temp_file.close()
            
            self.load_html(temp_file.name)
            self.debug_log(f"HTML内容已加载到临时文件: {temp_file.name}")
            
        except Exception as e:
            self.debug_log(f"加载HTML内容失败: {e}")
            QMessageBox.warning(self, "错误", f"加载HTML内容失败: {e}")

    def reload_page(self):
        """重新加载页面"""
        if self.html_file:
            self.debug_log("手动重新加载页面")
            self.load_html(self.html_file)

    def on_page_loaded(self, success):
        """页面加载完成"""
        if success:
            self.debug_log("页面基础加载完成，等待库加载...")
            self.status_label.setText("⏳ 等待库加载...")

            # 等待外部库加载完成
            self.wait_for_libraries()
        else:
            self.debug_log("❌ 页面加载失败")
            self.status_label.setText("❌ 页面加载失败")

    def wait_for_libraries(self):
        """等待外部库加载完成"""
        check_script = """
        (function() {
            // 检查常见的动画库是否加载完成
            const checks = {
                'THREE.js': typeof THREE !== 'undefined',
                'GSAP': typeof gsap !== 'undefined' || typeof TweenMax !== 'undefined',
                'renderAtTime': typeof window.renderAtTime === 'function'
            };

            const loadedLibs = Object.keys(checks).filter(lib => checks[lib]);
            const missingLibs = Object.keys(checks).filter(lib => !checks[lib]);

            return {
                loaded: loadedLibs,
                missing: missingLibs,
                allReady: missingLibs.length <= 1, // 允许某些库不存在
                hasRenderFunction: checks['renderAtTime']
            };
        })();
        """

        def check_result(result):
            if result:
                loaded = result.get('loaded', [])
                missing = result.get('missing', [])
                all_ready = result.get('allReady', False)
                has_render = result.get('hasRenderFunction', False)

                self.debug_log(f"已加载库: {', '.join(loaded) if loaded else '无'}")
                self.debug_log(f"缺失库: {', '.join(missing) if missing else '无'}")

                if has_render:
                    self.page_ready = True
                    self.status_label.setText("✅ 页面就绪")
                    self.debug_log("✅ renderAtTime函数已就绪")

                    # 初始渲染
                    QTimer.singleShot(100, lambda: self.reset_animation())
                else:
                    self.status_label.setText("⚠️ 无renderAtTime函数")
                    self.debug_log("⚠️ 未找到renderAtTime函数")
            else:
                self.debug_log("❌ 库检查失败")
                self.status_label.setText("❌ 检查失败")

        # 延迟检查，给库一些加载时间
        QTimer.singleShot(1000, lambda: self.web_view.page().runJavaScript(check_script, check_result))

    def test_render_function(self):
        """测试渲染函数"""
        if not self.page_ready:
            self.debug_log("⚠️ 页面还未就绪")
            return

        test_script = """
        (function() {
            try {
                if (typeof window.renderAtTime === 'function') {
                    window.renderAtTime(0.5);
                    return {success: true, message: 'renderAtTime(0.5) 调用成功'};
                } else {
                    return {success: false, message: 'renderAtTime 函数不存在'};
                }
            } catch (error) {
                return {success: false, message: 'Error: ' + error.message};
            }
        })();
        """

        def test_result(result):
            if result:
                success = result.get('success', False)
                message = result.get('message', '未知结果')

                if success:
                    self.debug_log(f"✅ 测试成功: {message}")
                else:
                    self.debug_log(f"❌ 测试失败: {message}")
            else:
                self.debug_log("❌ 测试脚本执行失败")

        self.web_view.page().runJavaScript(test_script, test_result)

    def on_time_changed(self, value):
        """时间滑块变化"""
        if not self.page_ready:
            return

        self.current_time = (value / 1000.0) * self.duration
        self.update_time_display()
        self.render_at_time(self.current_time)
    
    def render_at_time(self, t):
        """渲染指定时间的动画状态"""
        if not self.page_ready or not self.html_file:
            return

        js_code = f"""
        (function() {{
            try {{
                if (typeof window.renderAtTime === 'function') {{
                    window.renderAtTime({t});
                    return {{success: true, time: {t}}};
                }} else {{
                    return {{success: false, error: 'renderAtTime function not found'}};
                }}
            }} catch (error) {{
                return {{success: false, error: error.message}};
            }}
        }})();
        """

        def render_result(result):
            if result and not result.get('success', True):
                error = result.get('error', '未知错误')
                self.debug_log(f"❌ 渲染错误 t={t}: {error}")

        self.web_view.page().runJavaScript(js_code, render_result)
        
        # 发射时间改变信号
        self.time_changed.emit(t)
    
    def toggle_play(self):
        """切换播放/暂停"""
        if not self.page_ready:
            self.debug_log("⚠️ 页面未就绪，无法播放")
            return

        if self.is_playing:
            self.pause_animation()
        else:
            self.play_animation()
    
    def play_animation(self):
        """播放动画 - 统一实现"""
        if not self.page_ready:
            QMessageBox.warning(self, "警告", "页面还未就绪，无法播放")
            return

        self.is_playing = True
        self.play_timer.start()

        # 更新按钮状态
        if hasattr(self, 'play_btn'):
            self.play_btn.setText("⏸ 暂停")
            self.play_btn.setEnabled(False)

        if hasattr(self, 'pause_btn'):
            self.pause_btn.setEnabled(True)

        self.debug_log("▶️ 开始播放动画")

    def pause_animation(self):
        """暂停动画 - 统一实现"""
        self.is_playing = False
        self.play_timer.stop()

        # 更新按钮状态
        if hasattr(self, 'play_btn'):
            self.play_btn.setText("▶ 播放")
            self.play_btn.setEnabled(True)

        if hasattr(self, 'pause_btn'):
            self.pause_btn.setEnabled(False)

        self.debug_log("⏸️ 暂停动画播放")
    
    def reset_animation(self):
        """重置动画"""
        self.pause_animation()
        self.current_time = 0.0
        self.time_slider.setValue(0)
        self.update_time_display()
        self.render_at_time(0.0)
        self.debug_log("⏮ 重置动画")
    

    
    def update_duration(self, duration):
        """更新动画时长"""
        self.duration = duration
        self.update_time_display()
        # 重新计算滑块位置
        if self.duration > 0:
            progress = int((self.current_time / self.duration) * 1000)
            self.time_slider.setValue(progress)
    
    def update_time_display(self):
        """更新时间显示"""
        self.time_label.setText(f"{self.current_time:.1f}s / {self.duration:.1f}s")





    def stop_animation(self):
        """停止动画"""
        self.is_playing = False
        self.play_timer.stop()
        self.current_time = 0.0

        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)

        self.time_slider.setValue(0)
        self.time_spinbox.setValue(0.0)

        # 重置到起始状态
        self.reset_animation()

        self.debug_log("⏹️ 停止动画播放")

    def advance_time(self):
        """推进时间（包含性能监控）"""
        try:
            if not self.is_playing:
                return

            # 计算帧数（性能监控）
            if hasattr(self, 'count_frame'):
                self.count_frame()

            # 每次推进0.05秒（20fps）
            self.current_time += 0.05

            # 检查是否到达结尾
            if self.current_time >= self.duration:
                if hasattr(self, 'loop_enabled') and self.loop_enabled:
                    self.current_time = 0  # 循环播放
                else:
                    self.current_time = self.duration
                    self.stop_animation()
                    return

            # 更新界面
            self.time_slider.setValue(int((self.current_time / self.duration) * 1000))
            self.time_spinbox.setValue(self.current_time)

            # 渲染当前帧
            self.render_at_time(self.current_time)

            # 发射时间改变信号
            self.time_changed.emit(self.current_time)

        except Exception as e:
            logger.error(f"推进时间失败: {e}")

    def debug_log(self, message: str):
        """添加调试日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.debug_text.appendPlainText(log_message)
        logger.info(f"Preview: {message}")

class PreviewWidget(QWidget):
    """预览组件主界面"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        logger.info("预览组件初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # 动画预览标签页
        self.preview_controller = AnimationPreviewController()
        self.tabs.addTab(self.preview_controller, "🎬 动画预览")
        
        # 增强代码查看标签页
        from ui.enhanced_code_viewer import EnhancedCodeViewer
        self.code_viewer = EnhancedCodeViewer()
        self.code_viewer.load_content("<!-- HTML代码将在这里显示 -->")
        self.tabs.addTab(self.code_viewer, "📄 代码查看")
    
    def load_html_content(self, html_content: str):
        """加载HTML内容"""
        self.preview_controller.load_html_content(html_content)
        self.code_viewer.load_content(html_content)
    
    def load_html_file(self, file_path: str):
        """加载HTML文件"""
        self.preview_controller.load_html(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.code_viewer.load_content(content)
        except Exception as e:
            self.code_viewer.load_content(f"<!-- 无法读取文件: {e} -->")
    
    def set_duration(self, duration: float):
        """设置动画时长"""
        self.preview_controller.update_duration(duration)

    # 增强功能实现
    def toggle_fullscreen(self):
        """切换全屏模式"""
        try:
            if hasattr(self, 'fullscreen_window') and self.fullscreen_window.isVisible():
                # 退出全屏
                self.exit_fullscreen()
            else:
                # 进入全屏
                self.enter_fullscreen()

        except Exception as e:
            logger.error(f"切换全屏模式失败: {e}")

    def enter_fullscreen(self):
        """进入全屏模式"""
        try:
            from ui.fullscreen_preview_dialog import FullscreenPreviewDialog

            # 获取当前HTML内容
            html_content = self.code_viewer.get_content()

            # 创建全屏预览窗口
            self.fullscreen_window = FullscreenPreviewDialog(html_content, self)
            self.fullscreen_window.show()

            # 更新按钮文本
            self.preview_controller.fullscreen_btn.setText("🔙 退出全屏")

            logger.info("进入全屏预览模式")

        except Exception as e:
            logger.error(f"进入全屏模式失败: {e}")

    def exit_fullscreen(self):
        """退出全屏模式"""
        try:
            if hasattr(self, 'fullscreen_window'):
                self.fullscreen_window.close()
                delattr(self, 'fullscreen_window')

            # 更新按钮文本
            self.preview_controller.fullscreen_btn.setText("🔍 全屏")

            logger.info("退出全屏预览模式")

        except Exception as e:
            logger.error(f"退出全屏模式失败: {e}")

    def toggle_recording(self):
        """切换录制状态"""
        try:
            if hasattr(self, 'is_recording') and self.is_recording:
                self.stop_recording()
            else:
                self.start_recording()

        except Exception as e:
            logger.error(f"切换录制状态失败: {e}")

    def start_recording(self):
        """开始录制"""
        try:
            from PyQt6.QtWidgets import QFileDialog

            # 选择保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存录制视频", "", "MP4文件 (*.mp4);;WebM文件 (*.webm)"
            )

            if not file_path:
                return

            # 获取当前HTML内容
            html_content = self.code_viewer.get_content()

            # 开始录制
            from core.video_exporter import VideoExporter

            self.video_exporter = VideoExporter()

            def on_progress(message):
                self.preview_controller.fps_label.setText(f"录制: {message}")

            def on_complete(success, message):
                self.is_recording = False
                self.preview_controller.record_btn.setText("🎥 录制")
                self.preview_controller.record_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)

                if success:
                    QMessageBox.information(self, "录制完成", f"视频已保存到:\n{file_path}")
                else:
                    QMessageBox.warning(self, "录制失败", message)

            # 启动录制
            duration = self.preview_controller.duration
            success = self.video_exporter.export_video(
                html_content, file_path, duration, 30, 1920, 1080,
                progress_callback=on_progress,
                complete_callback=on_complete
            )

            if success:
                self.is_recording = True
                self.preview_controller.record_btn.setText("⏹️ 停止录制")
                self.preview_controller.record_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #28a745;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                    }
                """)
                logger.info("开始录制动画")
            else:
                QMessageBox.warning(self, "错误", "无法启动录制")

        except Exception as e:
            logger.error(f"开始录制失败: {e}")
            QMessageBox.warning(self, "错误", "开始录制失败")

    def stop_recording(self):
        """停止录制"""
        try:
            if hasattr(self, 'video_exporter'):
                # 停止录制（这里需要实现停止逻辑）
                pass

            self.is_recording = False
            self.preview_controller.record_btn.setText("🎥 录制")
            self.preview_controller.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)

            logger.info("停止录制动画")

        except Exception as e:
            logger.error(f"停止录制失败: {e}")

    def take_screenshot(self):
        """截取当前帧"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            from PyQt6.QtGui import QPixmap

            # 选择保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存截图", "", "PNG文件 (*.png);;JPEG文件 (*.jpg)"
            )

            if not file_path:
                return

            # 截取WebView内容
            if hasattr(self.preview_controller, 'web_view'):
                # 获取WebView的截图
                pixmap = self.preview_controller.web_view.grab()

                if pixmap.save(file_path):
                    QMessageBox.information(self, "截图成功", f"截图已保存到:\n{file_path}")
                    logger.info(f"截图保存到: {file_path}")
                else:
                    QMessageBox.warning(self, "错误", "保存截图失败")
            else:
                QMessageBox.warning(self, "错误", "无法截取预览内容")

        except Exception as e:
            logger.error(f"截图失败: {e}")
            QMessageBox.warning(self, "错误", "截图失败")

    def change_playback_speed(self, speed_text: str):
        """改变播放速度"""
        try:
            # 解析速度值
            speed_value = float(speed_text.replace('x', ''))

            # 更新播放速度
            if hasattr(self.preview_controller, 'play_timer'):
                # 调整定时器间隔
                base_interval = 50  # 基础间隔50ms (20fps)
                new_interval = int(base_interval / speed_value)
                self.preview_controller.play_timer.setInterval(new_interval)

            logger.info(f"播放速度已设置为: {speed_text}")

        except Exception as e:
            logger.error(f"改变播放速度失败: {e}")

    # 性能监控功能
    def update_fps_display(self):
        """更新FPS显示"""
        try:
            if hasattr(self, 'fps_counter'):
                fps = self.fps_counter
                self.fps_counter = 0

                # 更新FPS标签
                if hasattr(self, 'fps_label'):
                    color = "#28a745" if fps >= 30 else "#ffc107" if fps >= 20 else "#dc3545"
                    self.fps_label.setText(f"FPS: {fps}")
                    self.fps_label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold;")

                # 记录帧时间
                if hasattr(self, 'frame_times'):
                    self.frame_times.append(fps)
                    if len(self.frame_times) > 60:  # 保留最近60秒的数据
                        self.frame_times.pop(0)

        except Exception as e:
            logger.error(f"更新FPS显示失败: {e}")

    def count_frame(self):
        """计算帧数"""
        try:
            if hasattr(self, 'fps_counter'):
                self.fps_counter += 1

        except Exception as e:
            logger.error(f"计算帧数失败: {e}")

    def get_performance_stats(self):
        """获取性能统计"""
        try:
            if not hasattr(self, 'frame_times') or not self.frame_times:
                return {
                    'current_fps': 0,
                    'average_fps': 0,
                    'min_fps': 0,
                    'max_fps': 0,
                    'frame_drops': 0
                }

            current_fps = self.frame_times[-1] if self.frame_times else 0
            average_fps = sum(self.frame_times) / len(self.frame_times)
            min_fps = min(self.frame_times)
            max_fps = max(self.frame_times)

            # 计算掉帧数（FPS低于20的次数）
            frame_drops = sum(1 for fps in self.frame_times if fps < 20)

            return {
                'current_fps': current_fps,
                'average_fps': round(average_fps, 1),
                'min_fps': min_fps,
                'max_fps': max_fps,
                'frame_drops': frame_drops
            }

        except Exception as e:
            logger.error(f"获取性能统计失败: {e}")
            return {}

    def show_performance_dialog(self):
        """显示性能统计对话框"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox

            stats = self.get_performance_stats()

            dialog = QDialog(self)
            dialog.setWindowTitle("性能统计")
            dialog.setMinimumSize(300, 200)

            layout = QVBoxLayout(dialog)

            # 性能数据
            stats_layout = QFormLayout()

            stats_layout.addRow("当前FPS:", QLabel(str(stats.get('current_fps', 0))))
            stats_layout.addRow("平均FPS:", QLabel(str(stats.get('average_fps', 0))))
            stats_layout.addRow("最低FPS:", QLabel(str(stats.get('min_fps', 0))))
            stats_layout.addRow("最高FPS:", QLabel(str(stats.get('max_fps', 0))))
            stats_layout.addRow("掉帧次数:", QLabel(str(stats.get('frame_drops', 0))))

            layout.addLayout(stats_layout)

            # 性能建议
            suggestions = self.generate_performance_suggestions(stats)
            if suggestions:
                layout.addWidget(QLabel("性能建议:"))
                for suggestion in suggestions:
                    layout.addWidget(QLabel(f"• {suggestion}"))

            # 按钮
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            buttons.accepted.connect(dialog.accept)
            layout.addWidget(buttons)

            dialog.exec()

        except Exception as e:
            logger.error(f"显示性能统计对话框失败: {e}")

    def generate_performance_suggestions(self, stats: dict):
        """生成性能建议"""
        try:
            suggestions = []

            avg_fps = stats.get('average_fps', 0)
            frame_drops = stats.get('frame_drops', 0)

            if avg_fps < 20:
                suggestions.append("平均FPS较低，建议简化动画效果")
                suggestions.append("考虑使用CSS transform代替position属性")
                suggestions.append("减少同时进行的动画数量")

            if frame_drops > 10:
                suggestions.append("掉帧较多，建议优化动画性能")
                suggestions.append("使用will-change属性预告浏览器优化")
                suggestions.append("避免在动画中修改布局属性")

            if avg_fps >= 50:
                suggestions.append("性能表现优秀！")

            return suggestions

        except Exception as e:
            logger.error(f"生成性能建议失败: {e}")
            return []

    # 增强的时间控制已合并到上面的advance_time方法中

    # 导出功能增强
    def export_animation_data(self):
        """导出动画数据"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            import json
            from datetime import datetime

            # 选择保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出动画数据", "", "JSON文件 (*.json)"
            )

            if not file_path:
                return

            # 收集动画数据
            animation_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0'
                },
                'animation': {
                    'html_content': self.code_viewer.get_content() if hasattr(self, 'code_viewer') else '',
                    'duration': getattr(self, 'duration', 10.0),
                    'loop_enabled': getattr(self, 'loop_enabled', True)
                },
                'performance': self.get_performance_stats(),
                'settings': {
                    'playback_speed': getattr(self, 'playback_speed', 1.0),
                    'auto_play': getattr(self, 'auto_play', False)
                }
            }

            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(animation_data, f, ensure_ascii=False, indent=2)

            QMessageBox.information(self, "导出成功", f"动画数据已导出到:\n{file_path}")
            logger.info(f"动画数据已导出到: {file_path}")

        except Exception as e:
            logger.error(f"导出动画数据失败: {e}")
            QMessageBox.warning(self, "错误", "导出动画数据失败")

    # ========== 鼠标事件处理 ==========

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self.handle_left_click(event)
            elif event.button() == Qt.MouseButton.RightButton:
                self.handle_right_click(event)
            elif event.button() == Qt.MouseButton.MiddleButton:
                self.handle_middle_click(event)

            super().mousePressEvent(event)

        except Exception as e:
            logger.error(f"鼠标按下事件处理失败: {e}")

    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                # 双击切换全屏
                self.toggle_fullscreen()

            super().mouseDoubleClickEvent(event)

        except Exception as e:
            logger.error(f"鼠标双击事件处理失败: {e}")

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        try:
            # 更新鼠标位置信息
            pos = event.position()
            self.update_mouse_position(int(pos.x()), int(pos.y()))

            super().mouseMoveEvent(event)

        except Exception as e:
            logger.error(f"鼠标移动事件处理失败: {e}")

    def wheelEvent(self, event):
        """鼠标滚轮事件"""
        try:
            # 获取滚轮增量
            delta = event.angleDelta().y()

            # Ctrl + 滚轮：缩放
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                if delta > 0:
                    self.zoom_in()
                else:
                    self.zoom_out()
            # 普通滚轮：滚动时间轴
            else:
                if hasattr(self.preview_controller, 'seek_relative'):
                    step = 0.1 if delta > 0 else -0.1
                    self.preview_controller.seek_relative(step)

            super().wheelEvent(event)

        except Exception as e:
            logger.error(f"滚轮事件处理失败: {e}")

    def handle_left_click(self, event):
        """处理左键点击"""
        try:
            # 如果点击在预览区域，暂停/播放动画
            if hasattr(self.preview_controller, 'toggle_play'):
                self.preview_controller.toggle_play()

        except Exception as e:
            logger.error(f"左键点击处理失败: {e}")

    def handle_right_click(self, event):
        """处理右键点击"""
        try:
            # 显示上下文菜单
            self.show_context_menu(event.globalPosition().toPoint())

        except Exception as e:
            logger.error(f"右键点击处理失败: {e}")

    def handle_middle_click(self, event):
        """处理中键点击"""
        try:
            # 中键点击重置视图
            if hasattr(self.preview_controller, 'reset_view'):
                self.preview_controller.reset_view()

        except Exception as e:
            logger.error(f"中键点击处理失败: {e}")

    def show_context_menu(self, global_pos):
        """显示上下文菜单"""
        try:
            from PyQt6.QtWidgets import QMenu

            menu = QMenu(self)

            # 播放控制
            play_action = menu.addAction("播放/暂停")
            play_action.triggered.connect(lambda: self.preview_controller.toggle_play())

            stop_action = menu.addAction("停止")
            stop_action.triggered.connect(lambda: self.preview_controller.stop())

            menu.addSeparator()

            # 视图控制
            fullscreen_action = menu.addAction("全屏")
            fullscreen_action.triggered.connect(self.toggle_fullscreen)

            zoom_in_action = menu.addAction("放大")
            zoom_in_action.triggered.connect(self.zoom_in)

            zoom_out_action = menu.addAction("缩小")
            zoom_out_action.triggered.connect(self.zoom_out)

            menu.addSeparator()

            # 导出功能
            export_action = menu.addAction("导出动画")
            export_action.triggered.connect(self.export_animation_data)

            menu.exec(global_pos)

        except Exception as e:
            logger.error(f"显示上下文菜单失败: {e}")

    def update_mouse_position(self, x: int, y: int):
        """更新鼠标位置信息"""
        try:
            # 可以在状态栏显示鼠标位置
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"位置: ({x}, {y})")

        except Exception as e:
            logger.error(f"更新鼠标位置失败: {e}")

    def zoom_in(self):
        """放大视图"""
        try:
            if hasattr(self.preview_controller, 'zoom_in'):
                self.preview_controller.zoom_in()
            else:
                logger.info("放大功能")

        except Exception as e:
            logger.error(f"放大视图失败: {e}")

    def zoom_out(self):
        """缩小视图"""
        try:
            if hasattr(self.preview_controller, 'zoom_out'):
                self.preview_controller.zoom_out()
            else:
                logger.info("缩小功能")

        except Exception as e:
            logger.error(f"缩小视图失败: {e}")
