"""
AI Animation Studio - 方案预览对话框
提供方案的可视化预览和详细分析功能
"""

from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QPushButton, QTextEdit, QGroupBox, QFormLayout, QProgressBar,
    QSlider, QCheckBox, QComboBox, QSpinBox, QSplitter, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter
from PyQt6.QtWebEngineWidgets import QWebEngineView

from core.data_structures import AnimationSolution
from core.logger import get_logger

logger = get_logger("solution_preview_dialog")


class SolutionPreviewDialog(QDialog):
    """方案预览对话框"""
    
    solution_applied = pyqtSignal(str)  # 方案应用信号
    solution_rated = pyqtSignal(str, float)  # 方案评分信号
    
    def __init__(self, solution: AnimationSolution, parent=None):
        super().__init__(parent)
        
        self.solution = solution
        self.is_playing = False
        self.current_time = 0
        self.total_duration = 10  # 默认10秒
        
        self.setup_ui()
        self.load_solution()
        
        logger.info(f"打开方案预览: {solution.name}")
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle(f"方案预览 - {self.solution.name}")
        self.setMinimumSize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧预览区域
        preview_panel = self.create_preview_panel()
        splitter.addWidget(preview_panel)
        
        # 右侧信息区域
        info_panel = self.create_info_panel()
        splitter.addWidget(info_panel)
        
        # 设置分割比例
        splitter.setSizes([700, 300])
        layout.addWidget(splitter)
        
        # 底部控制栏
        control_bar = self.create_control_bar()
        layout.addWidget(control_bar)
    
    def create_preview_panel(self):
        """创建预览面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 预览标签页
        self.preview_tabs = QTabWidget()
        
        # 可视化预览标签页
        try:
            self.web_preview = QWebEngineView()
            self.preview_tabs.addTab(self.web_preview, "🎬 可视化")
        except ImportError:
            # 如果没有WebEngine，使用文本预览
            self.text_preview = QTextEdit()
            self.text_preview.setReadOnly(True)
            self.preview_tabs.addTab(self.text_preview, "📝 代码预览")
        
        # 代码预览标签页
        self.code_preview = QTextEdit()
        self.code_preview.setReadOnly(True)
        self.code_preview.setFont(QFont("Consolas", 10))
        self.preview_tabs.addTab(self.code_preview, "💻 源代码")
        
        # 分析结果标签页
        self.analysis_tab = self.create_analysis_tab()
        self.preview_tabs.addTab(self.analysis_tab, "📊 分析")
        
        layout.addWidget(self.preview_tabs)
        
        # 播放控制
        control_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("▶️ 播放")
        self.play_btn.clicked.connect(self.toggle_play)
        control_layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_animation)
        control_layout.addWidget(self.stop_btn)
        
        # 时间滑块
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 100)
        self.time_slider.valueChanged.connect(self.seek_animation)
        control_layout.addWidget(self.time_slider)
        
        # 时间标签
        self.time_label = QLabel("00:00 / 00:10")
        control_layout.addWidget(self.time_label)
        
        layout.addLayout(control_layout)
        
        return panel
    
    def create_info_panel(self):
        """创建信息面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 基本信息
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout(info_group)
        
        self.name_label = QLabel(self.solution.name)
        info_layout.addRow("名称:", self.name_label)
        
        self.tech_stack_label = QLabel(self.solution.tech_stack.value)
        info_layout.addRow("技术栈:", self.tech_stack_label)
        
        self.complexity_label = QLabel(self.solution.complexity_level)
        info_layout.addRow("复杂度:", self.complexity_label)
        
        self.recommended_label = QLabel("是" if self.solution.recommended else "否")
        info_layout.addRow("推荐:", self.recommended_label)
        
        layout.addWidget(info_group)
        
        # 评分和收藏
        rating_group = QGroupBox("评分收藏")
        rating_layout = QVBoxLayout(rating_group)
        
        # 评分滑块
        rating_layout.addWidget(QLabel("评分 (1-5分):"))
        self.rating_slider = QSlider(Qt.Orientation.Horizontal)
        self.rating_slider.setRange(10, 50)  # 1.0 到 5.0，精度0.1
        self.rating_slider.setValue(30)  # 默认3.0分
        self.rating_slider.valueChanged.connect(self.update_rating_display)
        rating_layout.addWidget(self.rating_slider)
        
        self.rating_display = QLabel("3.0分")
        rating_layout.addWidget(self.rating_display)
        
        # 收藏按钮
        self.favorite_btn = QPushButton("⭐ 添加收藏")
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        rating_layout.addWidget(self.favorite_btn)
        
        layout.addWidget(rating_group)
        
        # 预览设置
        settings_group = QGroupBox("预览设置")
        settings_layout = QFormLayout(settings_group)
        
        # 播放速度
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.5x", "1.0x", "1.5x", "2.0x"])
        self.speed_combo.setCurrentText("1.0x")
        settings_layout.addRow("播放速度:", self.speed_combo)
        
        # 循环播放
        self.loop_cb = QCheckBox("循环播放")
        self.loop_cb.setChecked(True)
        settings_layout.addRow("", self.loop_cb)
        
        # 显示网格
        self.grid_cb = QCheckBox("显示网格")
        settings_layout.addRow("", self.grid_cb)
        
        layout.addWidget(settings_group)
        
        layout.addStretch()
        
        return panel
    
    def create_analysis_tab(self):
        """创建分析标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 性能分析
        perf_group = QGroupBox("性能分析")
        perf_layout = QVBoxLayout(perf_group)
        
        # 性能指标
        metrics_layout = QFormLayout()
        
        self.fps_label = QLabel("计算中...")
        metrics_layout.addRow("预估FPS:", self.fps_label)
        
        self.memory_label = QLabel("计算中...")
        metrics_layout.addRow("内存使用:", self.memory_label)
        
        self.load_time_label = QLabel("计算中...")
        metrics_layout.addRow("加载时间:", self.load_time_label)
        
        perf_layout.addLayout(metrics_layout)
        
        # 性能建议
        self.perf_suggestions = QTextEdit()
        self.perf_suggestions.setReadOnly(True)
        self.perf_suggestions.setMaximumHeight(100)
        perf_layout.addWidget(QLabel("优化建议:"))
        perf_layout.addWidget(self.perf_suggestions)
        
        layout.addWidget(perf_group)
        
        # 兼容性分析
        compat_group = QGroupBox("兼容性分析")
        compat_layout = QVBoxLayout(compat_group)
        
        # 浏览器支持
        browser_layout = QFormLayout()
        
        self.chrome_label = QLabel("✅ 支持")
        browser_layout.addRow("Chrome:", self.chrome_label)
        
        self.firefox_label = QLabel("✅ 支持")
        browser_layout.addRow("Firefox:", self.firefox_label)
        
        self.safari_label = QLabel("⚠️ 部分支持")
        browser_layout.addRow("Safari:", self.safari_label)
        
        self.edge_label = QLabel("✅ 支持")
        browser_layout.addRow("Edge:", self.edge_label)
        
        compat_layout.addLayout(browser_layout)
        
        # 兼容性建议
        self.compat_suggestions = QTextEdit()
        self.compat_suggestions.setReadOnly(True)
        self.compat_suggestions.setMaximumHeight(100)
        compat_layout.addWidget(QLabel("兼容性建议:"))
        compat_layout.addWidget(self.compat_suggestions)
        
        layout.addWidget(compat_group)
        
        layout.addStretch()
        
        return tab
    
    def create_control_bar(self):
        """创建控制栏"""
        control_bar = QWidget()
        layout = QHBoxLayout(control_bar)
        
        # 应用按钮
        self.apply_btn = QPushButton("✅ 应用方案")
        self.apply_btn.clicked.connect(self.apply_solution)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.apply_btn)
        
        # 保存评分按钮
        self.save_rating_btn = QPushButton("💾 保存评分")
        self.save_rating_btn.clicked.connect(self.save_rating)
        layout.addWidget(self.save_rating_btn)
        
        # 导出按钮
        self.export_btn = QPushButton("📤 导出")
        self.export_btn.clicked.connect(self.export_solution)
        layout.addWidget(self.export_btn)
        
        layout.addStretch()
        
        # 关闭按钮
        self.close_btn = QPushButton("❌ 关闭")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)
        
        return control_bar
    
    def load_solution(self):
        """加载方案"""
        try:
            # 加载代码预览
            self.code_preview.setPlainText(self.solution.html_code)
            
            # 加载可视化预览
            if hasattr(self, 'web_preview'):
                self.web_preview.setHtml(self.solution.html_code)
            elif hasattr(self, 'text_preview'):
                self.text_preview.setPlainText(self.solution.html_code)
            
            # 开始性能分析
            self.analyze_performance()
            
            # 设置定时器更新播放时间
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_time)
            
        except Exception as e:
            logger.error(f"加载方案失败: {e}")
    
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
            self.timer.start(100)  # 每100ms更新一次
            
            # 在WebView中执行播放脚本
            if hasattr(self, 'web_preview'):
                self.web_preview.page().runJavaScript("location.reload();")
            
        except Exception as e:
            logger.error(f"播放动画失败: {e}")
    
    def pause_animation(self):
        """暂停动画"""
        try:
            self.is_playing = False
            self.play_btn.setText("▶️ 播放")
            self.timer.stop()
            
        except Exception as e:
            logger.error(f"暂停动画失败: {e}")
    
    def stop_animation(self):
        """停止动画"""
        try:
            self.is_playing = False
            self.play_btn.setText("▶️ 播放")
            self.timer.stop()
            self.current_time = 0
            self.time_slider.setValue(0)
            self.update_time_display()
            
        except Exception as e:
            logger.error(f"停止动画失败: {e}")
    
    def seek_animation(self, value):
        """跳转动画时间"""
        try:
            self.current_time = (value / 100.0) * self.total_duration
            self.update_time_display()
            
        except Exception as e:
            logger.error(f"跳转动画时间失败: {e}")
    
    def update_time(self):
        """更新播放时间"""
        try:
            if self.is_playing:
                self.current_time += 0.1
                
                if self.current_time >= self.total_duration:
                    if self.loop_cb.isChecked():
                        self.current_time = 0
                    else:
                        self.stop_animation()
                        return
                
                progress = int((self.current_time / self.total_duration) * 100)
                self.time_slider.setValue(progress)
                self.update_time_display()
            
        except Exception as e:
            logger.error(f"更新播放时间失败: {e}")
    
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
    
    def update_rating_display(self, value):
        """更新评分显示"""
        try:
            rating = value / 10.0
            self.rating_display.setText(f"{rating:.1f}分")
            
        except Exception as e:
            logger.error(f"更新评分显示失败: {e}")
    
    def toggle_favorite(self):
        """切换收藏状态"""
        try:
            if self.favorite_btn.text() == "⭐ 添加收藏":
                self.favorite_btn.setText("💔 取消收藏")
            else:
                self.favorite_btn.setText("⭐ 添加收藏")
            
        except Exception as e:
            logger.error(f"切换收藏状态失败: {e}")
    
    def analyze_performance(self):
        """分析性能"""
        try:
            # 简单的性能分析
            code_length = len(self.solution.html_code)
            
            # 估算FPS
            if "transform" in self.solution.html_code:
                fps = "60 FPS (GPU加速)"
            elif "animation" in self.solution.html_code:
                fps = "30-60 FPS"
            else:
                fps = "30 FPS"
            
            self.fps_label.setText(fps)
            
            # 估算内存使用
            memory = f"~{code_length // 100}KB"
            self.memory_label.setText(memory)
            
            # 估算加载时间
            load_time = f"~{code_length // 1000 + 1}ms"
            self.load_time_label.setText(load_time)
            
            # 生成优化建议
            suggestions = []
            if "position" in self.solution.html_code and "transform" not in self.solution.html_code:
                suggestions.append("建议使用transform代替position属性以获得更好的性能")
            
            if "setInterval" in self.solution.html_code:
                suggestions.append("建议使用requestAnimationFrame代替setInterval")
            
            if not suggestions:
                suggestions.append("代码已经过优化，性能良好")
            
            self.perf_suggestions.setPlainText("\n".join(suggestions))
            
            # 生成兼容性建议
            compat_suggestions = []
            if "grid" in self.solution.html_code:
                compat_suggestions.append("CSS Grid在旧版浏览器中支持有限")
            
            if "flex" in self.solution.html_code:
                compat_suggestions.append("Flexbox在IE10及以下版本中需要前缀")
            
            if not compat_suggestions:
                compat_suggestions.append("兼容性良好，支持主流浏览器")
            
            self.compat_suggestions.setPlainText("\n".join(compat_suggestions))
            
        except Exception as e:
            logger.error(f"性能分析失败: {e}")
    
    def apply_solution(self):
        """应用方案"""
        try:
            self.solution_applied.emit(self.solution.html_code)
            self.accept()
            
        except Exception as e:
            logger.error(f"应用方案失败: {e}")
    
    def save_rating(self):
        """保存评分"""
        try:
            rating = self.rating_slider.value() / 10.0
            self.solution_rated.emit(self.solution.solution_id, rating)
            
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "成功", f"评分已保存: {rating:.1f}分")
            
        except Exception as e:
            logger.error(f"保存评分失败: {e}")
    
    def export_solution(self):
        """导出方案"""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出方案", f"{self.solution.name}.html",
                "HTML文件 (*.html);;JSON文件 (*.json)"
            )
            
            if file_path:
                if file_path.endswith('.html'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(self.solution.html_code)
                else:
                    # 导出为JSON格式
                    import json
                    solution_data = {
                        'name': self.solution.name,
                        'description': self.solution.description,
                        'html_code': self.solution.html_code,
                        'tech_stack': self.solution.tech_stack.value,
                        'complexity_level': self.solution.complexity_level,
                        'recommended': self.solution.recommended
                    }
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(solution_data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "成功", f"方案已导出到: {file_path}")
            
        except Exception as e:
            logger.error(f"导出方案失败: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "错误", "导出方案失败")
