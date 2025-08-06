"""
AI Animation Studio - 设置对话框
提供完整的应用程序设置界面
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QLineEdit, QComboBox, QCheckBox, QSpinBox, QPushButton, QGroupBox,
    QFormLayout, QDialogButtonBox, QFileDialog, QMessageBox, QSlider,
    QTextEdit, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from core.config import AppConfig
from core.user_settings import UserSettingsManager
from config.app_config import get_config
from core.logger import get_logger

logger = get_logger("settings_dialog")

class SettingsDialog(QDialog):
    """设置对话框"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.user_settings = UserSettingsManager()
        
        self.setWindowTitle("设置")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # AI设置标签页
        self.setup_ai_tab()
        
        # 界面设置标签页
        self.setup_ui_tab()
        
        # 导出设置标签页
        self.setup_export_tab()
        
        # 高级设置标签页
        self.setup_advanced_tab()
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        layout.addWidget(button_box)
    
    def setup_ai_tab(self):
        """设置AI标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # API配置组
        api_group = QGroupBox("API配置")
        api_layout = QFormLayout(api_group)
        
        # Gemini API Key
        self.gemini_api_key_edit = QLineEdit()
        self.gemini_api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_api_key_edit.setPlaceholderText("请输入Gemini API Key")
        api_layout.addRow("Gemini API Key:", self.gemini_api_key_edit)
        
        # 模型选择
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gemini-2.5-flash",
            "gemini-pro", 
            "gemini-1.5-pro"
        ])
        api_layout.addRow("默认模型:", self.model_combo)
        
        # 思考模式
        self.thinking_checkbox = QCheckBox("启用深度思考模式")
        api_layout.addRow("", self.thinking_checkbox)
        
        layout.addWidget(api_group)
        
        # 生成设置组
        gen_group = QGroupBox("生成设置")
        gen_layout = QFormLayout(gen_group)
        
        # 默认动画类型
        self.animation_type_combo = QComboBox()
        self.animation_type_combo.addItems([
            "CSS动画", "GSAP动画", "Three.js动画", 
            "JavaScript动画", "混合动画"
        ])
        gen_layout.addRow("默认动画类型:", self.animation_type_combo)
        
        # 生成超时时间
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setSuffix(" 秒")
        self.timeout_spin.setValue(30)
        gen_layout.addRow("生成超时:", self.timeout_spin)
        
        layout.addWidget(gen_group)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "🤖 AI设置")
    
    def setup_ui_tab(self):
        """设置界面标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 主题设置组
        theme_group = QGroupBox("主题设置")
        theme_layout = QFormLayout(theme_group)
        
        # 主题选择
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色主题", "深色主题", "蓝色主题"])
        theme_layout.addRow("界面主题:", self.theme_combo)
        
        # 字体大小
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 20)
        self.font_size_spin.setValue(9)
        theme_layout.addRow("字体大小:", self.font_size_spin)
        
        layout.addWidget(theme_group)
        
        # 窗口设置组
        window_group = QGroupBox("窗口设置")
        window_layout = QFormLayout(window_group)
        
        # 启动时恢复窗口大小
        self.restore_window_checkbox = QCheckBox("启动时恢复窗口大小和位置")
        self.restore_window_checkbox.setChecked(True)
        window_layout.addRow("", self.restore_window_checkbox)
        
        # 自动保存间隔
        self.autosave_spin = QSpinBox()
        self.autosave_spin.setRange(0, 60)
        self.autosave_spin.setSuffix(" 分钟")
        self.autosave_spin.setValue(5)
        self.autosave_spin.setSpecialValueText("禁用")
        window_layout.addRow("自动保存间隔:", self.autosave_spin)
        
        layout.addWidget(window_group)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "🎨 界面设置")
    
    def setup_export_tab(self):
        """设置导出标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # HTML导出设置组
        html_group = QGroupBox("HTML导出设置")
        html_layout = QFormLayout(html_group)
        
        # 自动注入库
        self.auto_inject_checkbox = QCheckBox("自动注入所需的JavaScript库")
        self.auto_inject_checkbox.setChecked(True)
        html_layout.addRow("", self.auto_inject_checkbox)
        
        # 优先本地库
        self.prefer_local_checkbox = QCheckBox("优先使用本地库而非CDN")
        self.prefer_local_checkbox.setChecked(True)
        html_layout.addRow("", self.prefer_local_checkbox)
        
        # 代码压缩
        self.minify_checkbox = QCheckBox("压缩导出的代码")
        html_layout.addRow("", self.minify_checkbox)
        
        layout.addWidget(html_group)
        
        # 视频导出设置组
        video_group = QGroupBox("视频导出设置")
        video_layout = QFormLayout(video_group)
        
        # 默认格式
        self.video_format_combo = QComboBox()
        self.video_format_combo.addItems(["MP4", "WebM", "AVI"])
        video_layout.addRow("默认格式:", self.video_format_combo)
        
        # 质量设置
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["高质量", "中等质量", "低质量"])
        video_layout.addRow("视频质量:", self.quality_combo)
        
        # 帧率
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(15, 60)
        self.fps_spin.setValue(30)
        video_layout.addRow("帧率:", self.fps_spin)
        
        layout.addWidget(video_group)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "📤 导出设置")
    
    def setup_advanced_tab(self):
        """设置高级标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 性能设置组
        perf_group = QGroupBox("性能设置")
        perf_layout = QFormLayout(perf_group)
        
        # 渲染线程数
        self.render_threads_spin = QSpinBox()
        self.render_threads_spin.setRange(1, 8)
        self.render_threads_spin.setValue(2)
        perf_layout.addRow("渲染线程数:", self.render_threads_spin)
        
        # 内存限制
        self.memory_limit_spin = QSpinBox()
        self.memory_limit_spin.setRange(512, 8192)
        self.memory_limit_spin.setSuffix(" MB")
        self.memory_limit_spin.setValue(2048)
        perf_layout.addRow("内存限制:", self.memory_limit_spin)
        
        layout.addWidget(perf_group)
        
        # 调试设置组
        debug_group = QGroupBox("调试设置")
        debug_layout = QFormLayout(debug_group)
        
        # 启用调试日志
        self.debug_log_checkbox = QCheckBox("启用详细调试日志")
        debug_layout.addRow("", self.debug_log_checkbox)
        
        # 保存生成历史
        self.save_history_checkbox = QCheckBox("保存AI生成历史")
        self.save_history_checkbox.setChecked(True)
        debug_layout.addRow("", self.save_history_checkbox)

        layout.addWidget(debug_group)

        # 增强功能设置组
        enhanced_group = QGroupBox("增强功能")
        enhanced_layout = QFormLayout(enhanced_group)

        # 启用智能推荐
        self.enable_recommendations_cb = QCheckBox("启用智能推荐")
        self.enable_recommendations_cb.setChecked(True)
        enhanced_layout.addRow("", self.enable_recommendations_cb)

        # 启用性能优化
        self.enable_optimization_cb = QCheckBox("启用自动性能优化")
        self.enable_optimization_cb.setChecked(True)
        enhanced_layout.addRow("", self.enable_optimization_cb)

        # 跟踪用户行为
        self.track_behavior_cb = QCheckBox("跟踪用户行为（用于推荐）")
        self.track_behavior_cb.setChecked(True)
        enhanced_layout.addRow("", self.track_behavior_cb)

        # 推荐数量限制
        self.recommendation_limit_spin = QSpinBox()
        self.recommendation_limit_spin.setRange(5, 50)
        self.recommendation_limit_spin.setValue(10)
        enhanced_layout.addRow("推荐数量限制:", self.recommendation_limit_spin)

        layout.addWidget(enhanced_group)

        layout.addStretch()
        
        self.tab_widget.addTab(widget, "⚙️ 高级设置")
    
    def load_settings(self):
        """加载设置"""
        try:
            # 加载AI设置
            api_key = self.user_settings.get_api_key()
            if api_key:
                self.gemini_api_key_edit.setText(api_key)
            
            model_settings = self.user_settings.get_model_settings()
            self.model_combo.setCurrentText(model_settings["model"])
            self.thinking_checkbox.setChecked(model_settings["enable_thinking"])
            
            # 加载界面设置
            self.theme_combo.setCurrentText(self.config.ui.theme)
            self.autosave_spin.setValue(self.config.timeline.auto_save_interval // 60)
            
            # 加载库设置
            lib_prefs = self.user_settings.get_library_preferences()
            self.auto_inject_checkbox.setChecked(lib_prefs["auto_inject"])
            self.prefer_local_checkbox.setChecked(lib_prefs["prefer_local"])

            # 加载增强功能设置
            enhanced_config = get_config()
            if hasattr(self, 'enable_recommendations_cb'):
                self.enable_recommendations_cb.setChecked(enhanced_config.recommendation.enable_recommendations)
                self.enable_optimization_cb.setChecked(enhanced_config.performance.enable_auto_optimization)
                self.track_behavior_cb.setChecked(enhanced_config.recommendation.track_user_behavior)
                self.recommendation_limit_spin.setValue(enhanced_config.recommendation.recommendation_limit)
            
            logger.info("设置已加载")
            
        except Exception as e:
            logger.error(f"加载设置失败: {e}")
    
    def apply_settings(self):
        """应用设置"""
        try:
            # 保存AI设置
            api_key = self.gemini_api_key_edit.text().strip()
            if api_key:
                self.user_settings.set_api_key(api_key)
            
            model = self.model_combo.currentText()
            thinking = self.thinking_checkbox.isChecked()
            self.user_settings.set_model_settings(model, thinking)
            
            # 保存界面设置
            self.config.ui.theme = self.theme_combo.currentText()
            self.config.timeline.auto_save_interval = self.autosave_spin.value() * 60
            
            # 保存库设置
            auto_inject = self.auto_inject_checkbox.isChecked()
            prefer_local = self.prefer_local_checkbox.isChecked()
            self.user_settings.set_library_preferences(auto_inject, prefer_local)

            # 保存增强功能设置
            enhanced_config = get_config()
            if hasattr(self, 'enable_recommendations_cb'):
                enhanced_config.recommendation.enable_recommendations = self.enable_recommendations_cb.isChecked()
                enhanced_config.performance.enable_auto_optimization = self.enable_optimization_cb.isChecked()
                enhanced_config.recommendation.track_user_behavior = self.track_behavior_cb.isChecked()
                enhanced_config.recommendation.recommendation_limit = self.recommendation_limit_spin.value()
                enhanced_config.save_config()

            # 保存配置
            self.config.save()
            
            # 发射信号
            self.settings_changed.emit()
            
            logger.info("设置已保存")
            
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            QMessageBox.warning(self, "错误", f"保存设置失败: {e}")
    
    def accept(self):
        """确定按钮"""
        self.apply_settings()
        super().accept()
