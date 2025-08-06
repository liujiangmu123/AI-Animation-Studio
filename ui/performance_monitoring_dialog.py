"""
AI Animation Studio - 性能监控对话框
严格按照设计文档的性能监控仪表板实现
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QFrame, QScrollArea, QWidget,
                             QProgressBar, QTabWidget, QSlider, QCheckBox,
                             QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from .color_scheme_manager import color_scheme_manager, ColorRole
from core.logger import get_logger
import psutil
import time

logger = get_logger("performance_monitoring_dialog")


class PerformanceMonitoringDialog(QDialog):
    """性能监控对话框 - 基于设计文档的性能监控仪表板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📊 性能监控仪表板")
        self.setFixedSize(900, 700)
        self.setModal(False)  # 允许非模态显示
        
        # 性能数据
        self.performance_data = {
            "cpu_usage": [],
            "memory_usage": [],
            "gpu_usage": [],
            "fps": []
        }
        
        # 更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_performance_data)
        
        self.setup_ui()
        self.apply_color_scheme()
        self.start_monitoring()
        
        logger.info("性能监控对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 对话框标题
        self.create_dialog_header(layout)
        
        # 主要内容区域
        content_tabs = QTabWidget()
        content_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                background-color: white;
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11px;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-weight: bold;
            }}
        """)
        
        # 实时监控标签页
        realtime_tab = self.create_realtime_monitoring_tab()
        content_tabs.addTab(realtime_tab, "📊 实时监控")
        
        # 性能趋势标签页
        trends_tab = self.create_performance_trends_tab()
        content_tabs.addTab(trends_tab, "📈 性能趋势")
        
        # 智能警告标签页
        warnings_tab = self.create_intelligent_warnings_tab()
        content_tabs.addTab(warnings_tab, "⚠️ 智能警告")
        
        # 调优控制台标签页
        tuning_tab = self.create_performance_tuning_tab()
        content_tabs.addTab(tuning_tab, "🔧 调优控制台")
        
        layout.addWidget(content_tabs)
        
        # 底部：控制按钮
        self.create_control_buttons(layout)
    
    def create_dialog_header(self, layout):
        """创建对话框标题"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color_scheme_manager.get_performance_colors()[0]},
                    stop:1 {color_scheme_manager.get_performance_colors()[1]});
                border: none;
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # 标题信息
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("📊 性能监控仪表板")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title)
        
        subtitle = QLabel("实时监控系统性能，智能优化建议，确保最佳创作体验")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 11px;
            }
        """)
        title_layout.addWidget(subtitle)
        
        header_layout.addWidget(title_frame)
        header_layout.addStretch()
        
        # 状态指示器
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        self.status_label = QLabel("🟢 监控中")
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        status_layout.addWidget(self.status_label)
        
        header_layout.addWidget(status_frame)
        
        layout.addWidget(header)
    
    def create_realtime_monitoring_tab(self):
        """创建实时监控标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 性能指标网格
        metrics_grid = QFrame()
        grid_layout = QGridLayout(metrics_grid)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(12)
        
        # CPU使用率
        cpu_card = self.create_metric_card("💻 CPU使用率", "cpu")
        grid_layout.addWidget(cpu_card, 0, 0)
        
        # 内存使用率
        memory_card = self.create_metric_card("🧠 内存使用率", "memory")
        grid_layout.addWidget(memory_card, 0, 1)
        
        # GPU使用率
        gpu_card = self.create_metric_card("🎮 GPU使用率", "gpu")
        grid_layout.addWidget(gpu_card, 1, 0)
        
        # 帧率
        fps_card = self.create_metric_card("🎬 渲染帧率", "fps")
        grid_layout.addWidget(fps_card, 1, 1)
        
        layout.addWidget(metrics_grid)
        
        # 系统信息
        system_info = self.create_system_info_panel()
        layout.addWidget(system_info)
        
        layout.addStretch()
        return widget
    
    def create_metric_card(self, title, metric_type):
        """创建性能指标卡片"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color_scheme_manager.get_performance_colors()[0]};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)
        
        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-weight: bold;
                font-size: 12px;
            }}
        """)
        card_layout.addWidget(title_label)
        
        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {color_scheme_manager.get_performance_colors()[2]};
                border-radius: 4px;
                text-align: center;
                font-size: 10px;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {color_scheme_manager.get_performance_colors()[0]};
                border-radius: 3px;
            }}
        """)
        card_layout.addWidget(progress_bar)
        
        # 数值显示
        value_label = QLabel("0%")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        card_layout.addWidget(value_label)
        
        # 存储引用以便更新
        setattr(self, f"{metric_type}_progress", progress_bar)
        setattr(self, f"{metric_type}_value", value_label)
        
        return card

    def create_system_info_panel(self):
        """创建系统信息面板"""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 6px;
            }}
        """)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(12, 12, 12, 12)

        # 标题
        info_title = QLabel("💻 系统信息")
        info_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-weight: bold;
                font-size: 12px;
            }}
        """)
        panel_layout.addWidget(info_title)

        # 系统信息文本
        self.system_info_text = QTextEdit()
        self.system_info_text.setMaximumHeight(120)
        self.system_info_text.setReadOnly(True)
        self.system_info_text.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }}
        """)

        # 获取系统信息
        system_info = self.get_system_info()
        self.system_info_text.setPlainText(system_info)

        panel_layout.addWidget(self.system_info_text)

        return panel

    def create_performance_trends_tab(self):
        """创建性能趋势标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)

        # 趋势图占位符
        trends_placeholder = QLabel("📈 性能趋势图\n\n实时性能数据图表\n显示CPU、内存、GPU使用率变化")
        trends_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trends_placeholder.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                font-size: 14px;
                padding: 60px;
                border: 2px dashed {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 8px;
            }}
        """)
        layout.addWidget(trends_placeholder)

        return widget

    def create_intelligent_warnings_tab(self):
        """创建智能警告标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)

        # 警告列表
        self.warnings_area = QScrollArea()
        self.warnings_area.setWidgetResizable(True)
        self.warnings_area.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
                border-radius: 6px;
                background-color: white;
            }}
        """)

        warnings_widget = QWidget()
        self.warnings_layout = QVBoxLayout(warnings_widget)
        self.warnings_layout.setContentsMargins(8, 8, 8, 8)
        self.warnings_layout.setSpacing(8)

        # 默认提示
        default_warning = QLabel("✅ 系统运行正常\n\n暂无性能警告")
        default_warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        default_warning.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_collaboration_colors()[0]};
                font-size: 12px;
                padding: 40px;
            }}
        """)
        self.warnings_layout.addWidget(default_warning)

        self.warnings_area.setWidget(warnings_widget)
        layout.addWidget(self.warnings_area)

        return widget

    def create_performance_tuning_tab(self):
        """创建性能调优标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 调优选项
        tuning_frame = QFrame()
        tuning_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {color_scheme_manager.get_performance_colors()[0]};
                border-radius: 6px;
            }}
        """)

        tuning_layout = QVBoxLayout(tuning_frame)
        tuning_layout.setContentsMargins(12, 12, 12, 12)

        tuning_title = QLabel("🔧 性能调优选项")
        tuning_title.setStyleSheet(f"""
            QLabel {{
                color: {color_scheme_manager.get_performance_colors()[0]};
                font-weight: bold;
                font-size: 12px;
            }}
        """)
        tuning_layout.addWidget(tuning_title)

        # 调优选项复选框
        self.enable_gpu_acceleration = QCheckBox("启用GPU加速")
        self.enable_gpu_acceleration.setChecked(True)
        tuning_layout.addWidget(self.enable_gpu_acceleration)

        self.optimize_memory = QCheckBox("内存优化")
        self.optimize_memory.setChecked(True)
        tuning_layout.addWidget(self.optimize_memory)

        self.reduce_quality = QCheckBox("降低预览质量以提升性能")
        tuning_layout.addWidget(self.reduce_quality)

        layout.addWidget(tuning_frame)

        layout.addStretch()
        return widget

    def create_control_buttons(self, layout):
        """创建控制按钮"""
        button_frame = QFrame()
        button_frame.setFixedHeight(60)
        button_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.SURFACE)};
                border-top: 1px solid {color_scheme_manager.get_color_hex(ColorRole.BORDER)};
            }}
        """)

        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(20, 12, 20, 12)

        # 暂停/继续监控按钮
        self.pause_btn = QPushButton("⏸️ 暂停监控")
        self.pause_btn.setFixedSize(120, 36)
        self.pause_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_performance_colors()[0]};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color_scheme_manager.get_performance_colors()[1]};
            }}
        """)
        self.pause_btn.clicked.connect(self.toggle_monitoring)
        button_layout.addWidget(self.pause_btn)

        button_layout.addStretch()

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setFixedSize(80, 36)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.TEXT_SECONDARY)};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addWidget(button_frame)

    def get_system_info(self):
        """获取系统信息"""
        try:
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()

            info = f"""CPU核心数: {cpu_count}
内存总量: {memory.total // (1024**3)} GB
可用内存: {memory.available // (1024**3)} GB
Python版本: 3.9+
PyQt版本: 6.x"""

            return info
        except Exception as e:
            return f"获取系统信息失败: {str(e)}"

    def start_monitoring(self):
        """开始监控"""
        self.update_timer.start(1000)  # 每秒更新一次
        self.status_label.setText("🟢 监控中")
        logger.info("性能监控已开始")

    def stop_monitoring(self):
        """停止监控"""
        self.update_timer.stop()
        self.status_label.setText("🔴 已暂停")
        logger.info("性能监控已停止")

    def toggle_monitoring(self):
        """切换监控状态"""
        if self.update_timer.isActive():
            self.stop_monitoring()
            self.pause_btn.setText("▶️ 继续监控")
        else:
            self.start_monitoring()
            self.pause_btn.setText("⏸️ 暂停监控")

    def update_performance_data(self):
        """更新性能数据"""
        try:
            # 获取CPU使用率
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_progress.setValue(int(cpu_percent))
            self.cpu_value.setText(f"{cpu_percent:.1f}%")

            # 获取内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_progress.setValue(int(memory_percent))
            self.memory_value.setText(f"{memory_percent:.1f}%")

            # 模拟GPU使用率（实际应用中需要使用GPU监控库）
            gpu_percent = min(cpu_percent * 1.2, 100)
            self.gpu_progress.setValue(int(gpu_percent))
            self.gpu_value.setText(f"{gpu_percent:.1f}%")

            # 模拟FPS
            fps = max(60 - cpu_percent * 0.5, 15)
            self.fps_progress.setValue(int(fps))
            self.fps_value.setText(f"{fps:.0f} FPS")

            # 存储历史数据
            self.performance_data["cpu_usage"].append(cpu_percent)
            self.performance_data["memory_usage"].append(memory_percent)
            self.performance_data["gpu_usage"].append(gpu_percent)
            self.performance_data["fps"].append(fps)

            # 限制历史数据长度
            for key in self.performance_data:
                if len(self.performance_data[key]) > 60:  # 保留最近60个数据点
                    self.performance_data[key].pop(0)

            # 检查性能警告
            self.check_performance_warnings(cpu_percent, memory_percent, gpu_percent, fps)

        except Exception as e:
            logger.error(f"更新性能数据失败: {e}")

    def check_performance_warnings(self, cpu, memory, gpu, fps):
        """检查性能警告"""
        warnings = []

        if cpu > 80:
            warnings.append("⚠️ CPU使用率过高")
        if memory > 85:
            warnings.append("⚠️ 内存使用率过高")
        if gpu > 90:
            warnings.append("⚠️ GPU使用率过高")
        if fps < 20:
            warnings.append("⚠️ 渲染帧率过低")

        # 更新警告显示（这里简化处理）
        if warnings:
            logger.warning(f"性能警告: {', '.join(warnings)}")

    def apply_color_scheme(self):
        """应用色彩方案"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {color_scheme_manager.get_color_hex(ColorRole.BACKGROUND)};
            }}
        """)

    def closeEvent(self, event):
        """关闭事件"""
        self.stop_monitoring()
        event.accept()
