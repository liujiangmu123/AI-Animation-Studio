"""
AI Animation Studio - 增强AI配置对话框
提供专业的AI服务配置、使用量监控、模型管理等功能
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QGroupBox,
    QFormLayout, QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QPushButton, QTextEdit, QProgressBar, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog, QSlider,
    QFrame, QScrollArea, QListWidget, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QFont, QColor, QPixmap, QIcon

from core.logger import get_logger

logger = get_logger("enhanced_ai_config")


class APIUsageMonitor:
    """API使用量监控器"""
    
    def __init__(self):
        self.usage_file = "ai_usage_stats.json"
        self.usage_data = self.load_usage_data()
    
    def load_usage_data(self) -> Dict[str, Any]:
        """加载使用量数据"""
        try:
            if os.path.exists(self.usage_file):
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {
                "daily_usage": {},
                "monthly_usage": {},
                "total_requests": 0,
                "total_tokens": 0,
                "cost_tracking": {}
            }
        except Exception as e:
            logger.error(f"加载使用量数据失败: {e}")
            return {}
    
    def save_usage_data(self):
        """保存使用量数据"""
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存使用量数据失败: {e}")
    
    def record_usage(self, service: str, tokens: int, cost: float = 0.0):
        """记录使用量"""
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        
        # 日使用量
        if today not in self.usage_data["daily_usage"]:
            self.usage_data["daily_usage"][today] = {}
        if service not in self.usage_data["daily_usage"][today]:
            self.usage_data["daily_usage"][today][service] = {"requests": 0, "tokens": 0, "cost": 0.0}
        
        self.usage_data["daily_usage"][today][service]["requests"] += 1
        self.usage_data["daily_usage"][today][service]["tokens"] += tokens
        self.usage_data["daily_usage"][today][service]["cost"] += cost
        
        # 月使用量
        if month not in self.usage_data["monthly_usage"]:
            self.usage_data["monthly_usage"][month] = {}
        if service not in self.usage_data["monthly_usage"][month]:
            self.usage_data["monthly_usage"][month][service] = {"requests": 0, "tokens": 0, "cost": 0.0}
        
        self.usage_data["monthly_usage"][month][service]["requests"] += 1
        self.usage_data["monthly_usage"][month][service]["tokens"] += tokens
        self.usage_data["monthly_usage"][month][service]["cost"] += cost
        
        # 总计
        self.usage_data["total_requests"] += 1
        self.usage_data["total_tokens"] += tokens
        
        self.save_usage_data()
    
    def get_daily_usage(self, date: str = None) -> Dict[str, Any]:
        """获取日使用量"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return self.usage_data["daily_usage"].get(date, {})
    
    def get_monthly_usage(self, month: str = None) -> Dict[str, Any]:
        """获取月使用量"""
        if month is None:
            month = datetime.now().strftime("%Y-%m")
        return self.usage_data["monthly_usage"].get(month, {})


class ModelTester(QThread):
    """模型测试器"""
    
    test_completed = pyqtSignal(str, bool, str)  # service, success, message
    
    def __init__(self, service_name: str, api_key: str, model: str):
        super().__init__()
        self.service_name = service_name
        self.api_key = api_key
        self.model = model
    
    def run(self):
        """执行测试"""
        try:
            # 简单的测试请求
            test_prompt = "生成一个简单的CSS动画：一个红色方块从左到右移动"
            
            # 这里应该调用实际的AI服务进行测试
            # 简化实现，模拟测试结果
            import time
            time.sleep(2)  # 模拟网络延迟
            
            # 模拟测试成功
            self.test_completed.emit(self.service_name, True, "连接成功")
            
        except Exception as e:
            self.test_completed.emit(self.service_name, False, str(e))


class EnhancedAIConfigDialog(QDialog):
    """增强AI配置对话框"""
    
    config_changed = pyqtSignal(dict)  # 配置改变信号
    
    def __init__(self, current_config: dict, parent=None):
        super().__init__(parent)
        self.current_config = current_config.copy()
        self.usage_monitor = APIUsageMonitor()
        self.model_testers = {}
        
        self.setWindowTitle("AI服务配置")
        self.setMinimumSize(800, 700)
        self.resize(900, 800)
        
        self.setup_ui()
        self.load_current_config()
        
        logger.info("增强AI配置对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("AI服务配置")
        title_label.setFont(QFont("", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 标签页
        self.tab_widget = QTabWidget()
        
        # API配置标签页
        self.setup_api_config_tab()
        
        # 模型设置标签页
        self.setup_model_settings_tab()
        
        # 使用量监控标签页
        self.setup_usage_monitoring_tab()
        
        # 高级设置标签页
        self.setup_advanced_settings_tab()
        
        layout.addWidget(self.tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 测试连接按钮
        test_all_btn = QPushButton("测试所有连接")
        test_all_btn.clicked.connect(self.test_all_connections)
        button_layout.addWidget(test_all_btn)
        
        # 导入导出配置
        import_btn = QPushButton("导入配置")
        import_btn.clicked.connect(self.import_config)
        button_layout.addWidget(import_btn)
        
        export_btn = QPushButton("导出配置")
        export_btn.clicked.connect(self.export_config)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        # 标准按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("应用")
        apply_btn.clicked.connect(self.apply_config)
        button_layout.addWidget(apply_btn)
        
        ok_btn = QPushButton("确定")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def setup_api_config_tab(self):
        """设置API配置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # OpenAI配置
        openai_group = QGroupBox("OpenAI GPT")
        openai_layout = QFormLayout(openai_group)
        
        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_edit.setPlaceholderText("sk-...")
        openai_layout.addRow("API Key:", self.openai_key_edit)
        
        # 显示/隐藏密钥按钮
        openai_key_layout = QHBoxLayout()
        openai_key_layout.addWidget(self.openai_key_edit)
        
        self.openai_show_btn = QPushButton("👁")
        self.openai_show_btn.setMaximumWidth(30)
        self.openai_show_btn.setCheckable(True)
        self.openai_show_btn.toggled.connect(lambda checked: self.toggle_password_visibility(self.openai_key_edit, checked))
        openai_key_layout.addWidget(self.openai_show_btn)
        
        self.openai_test_btn = QPushButton("测试")
        self.openai_test_btn.setMaximumWidth(50)
        self.openai_test_btn.clicked.connect(lambda: self.test_connection("openai"))
        openai_key_layout.addWidget(self.openai_test_btn)
        
        openai_layout.addRow("API Key:", openai_key_layout)
        
        # OpenAI模型选择
        self.openai_model_combo = QComboBox()
        self.openai_model_combo.addItems([
            "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"
        ])
        openai_layout.addRow("模型:", self.openai_model_combo)
        
        # OpenAI组织ID（可选）
        self.openai_org_edit = QLineEdit()
        self.openai_org_edit.setPlaceholderText("org-...")
        openai_layout.addRow("组织ID (可选):", self.openai_org_edit)
        
        layout.addWidget(openai_group)
        
        # Claude配置
        claude_group = QGroupBox("Anthropic Claude")
        claude_layout = QFormLayout(claude_group)
        
        claude_key_layout = QHBoxLayout()
        self.claude_key_edit = QLineEdit()
        self.claude_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.claude_key_edit.setPlaceholderText("sk-ant-...")
        claude_key_layout.addWidget(self.claude_key_edit)
        
        self.claude_show_btn = QPushButton("👁")
        self.claude_show_btn.setMaximumWidth(30)
        self.claude_show_btn.setCheckable(True)
        self.claude_show_btn.toggled.connect(lambda checked: self.toggle_password_visibility(self.claude_key_edit, checked))
        claude_key_layout.addWidget(self.claude_show_btn)
        
        self.claude_test_btn = QPushButton("测试")
        self.claude_test_btn.setMaximumWidth(50)
        self.claude_test_btn.clicked.connect(lambda: self.test_connection("claude"))
        claude_key_layout.addWidget(self.claude_test_btn)
        
        claude_layout.addRow("API Key:", claude_key_layout)
        
        # Claude模型选择
        self.claude_model_combo = QComboBox()
        self.claude_model_combo.addItems([
            "claude-3-5-sonnet-20241022", "claude-3-opus-20240229", 
            "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
        ])
        claude_layout.addRow("模型:", self.claude_model_combo)
        
        layout.addWidget(claude_group)
        
        # Gemini配置
        gemini_group = QGroupBox("Google Gemini")
        gemini_layout = QFormLayout(gemini_group)
        
        gemini_key_layout = QHBoxLayout()
        self.gemini_key_edit = QLineEdit()
        self.gemini_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_key_edit.setPlaceholderText("AIza...")
        gemini_key_layout.addWidget(self.gemini_key_edit)
        
        self.gemini_show_btn = QPushButton("👁")
        self.gemini_show_btn.setMaximumWidth(30)
        self.gemini_show_btn.setCheckable(True)
        self.gemini_show_btn.toggled.connect(lambda checked: self.toggle_password_visibility(self.gemini_key_edit, checked))
        gemini_key_layout.addWidget(self.gemini_show_btn)
        
        self.gemini_test_btn = QPushButton("测试")
        self.gemini_test_btn.setMaximumWidth(50)
        self.gemini_test_btn.clicked.connect(lambda: self.test_connection("gemini"))
        gemini_key_layout.addWidget(self.gemini_test_btn)
        
        gemini_layout.addRow("API Key:", gemini_key_layout)
        
        # Gemini模型选择
        self.gemini_model_combo = QComboBox()
        self.gemini_model_combo.addItems([
            "gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"
        ])
        gemini_layout.addRow("模型:", self.gemini_model_combo)
        
        layout.addWidget(gemini_group)
        
        # 首选服务设置
        preference_group = QGroupBox("服务偏好")
        preference_layout = QFormLayout(preference_group)
        
        self.preferred_service_combo = QComboBox()
        self.preferred_service_combo.addItems(["openai", "claude", "gemini"])
        preference_layout.addRow("首选服务:", self.preferred_service_combo)
        
        # 自动切换
        self.auto_fallback_cb = QCheckBox("服务失败时自动切换到备用服务")
        self.auto_fallback_cb.setChecked(True)
        preference_layout.addRow("", self.auto_fallback_cb)
        
        # 备用服务顺序
        self.fallback_order_edit = QLineEdit()
        self.fallback_order_edit.setPlaceholderText("例如: claude,gemini,openai")
        self.fallback_order_edit.setToolTip("用逗号分隔的备用服务顺序")
        preference_layout.addRow("备用服务顺序:", self.fallback_order_edit)
        
        layout.addWidget(preference_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🔑 API配置")
    
    def setup_model_settings_tab(self):
        """设置模型设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 生成参数设置
        params_group = QGroupBox("生成参数")
        params_layout = QFormLayout(params_group)
        
        # 温度设置
        temp_layout = QHBoxLayout()
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 200)  # 0.0 - 2.0
        self.temperature_slider.setValue(70)  # 0.7
        self.temperature_slider.valueChanged.connect(self.on_temperature_changed)
        temp_layout.addWidget(self.temperature_slider)
        
        self.temperature_label = QLabel("0.7")
        self.temperature_label.setMinimumWidth(30)
        temp_layout.addWidget(self.temperature_label)
        
        params_layout.addRow("创造性 (Temperature):", temp_layout)
        
        # 最大令牌数
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 8000)
        self.max_tokens_spin.setValue(2000)
        self.max_tokens_spin.setSuffix(" tokens")
        params_layout.addRow("最大令牌数:", self.max_tokens_spin)
        
        # 超时设置
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" 秒")
        params_layout.addRow("请求超时:", self.timeout_spin)
        
        # 重试次数
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(0, 10)
        self.retry_spin.setValue(3)
        params_layout.addRow("重试次数:", self.retry_spin)
        
        layout.addWidget(params_group)
        
        # 提示词模板设置
        template_group = QGroupBox("提示词模板")
        template_layout = QVBoxLayout(template_group)
        
        # 系统提示词
        template_layout.addWidget(QLabel("系统提示词:"))
        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setMaximumHeight(120)
        self.system_prompt_edit.setPlaceholderText("输入系统提示词模板...")
        template_layout.addWidget(self.system_prompt_edit)
        
        # 用户提示词前缀
        template_layout.addWidget(QLabel("用户提示词前缀:"))
        self.user_prompt_prefix_edit = QLineEdit()
        self.user_prompt_prefix_edit.setPlaceholderText("例如: 请生成一个动画效果：")
        template_layout.addWidget(self.user_prompt_prefix_edit)
        
        # 模板预设
        template_presets_layout = QHBoxLayout()
        
        self.template_preset_combo = QComboBox()
        self.template_preset_combo.addItems([
            "默认模板", "专业动画师", "创意设计师", "技术开发者", "简洁模式"
        ])
        self.template_preset_combo.currentTextChanged.connect(self.load_template_preset)
        template_presets_layout.addWidget(self.template_preset_combo)
        
        load_template_btn = QPushButton("加载模板")
        load_template_btn.clicked.connect(self.load_selected_template)
        template_presets_layout.addWidget(load_template_btn)
        
        save_template_btn = QPushButton("保存模板")
        save_template_btn.clicked.connect(self.save_current_template)
        template_presets_layout.addWidget(save_template_btn)
        
        template_layout.addLayout(template_presets_layout)
        
        layout.addWidget(template_group)
        
        # 质量控制设置
        quality_group = QGroupBox("质量控制")
        quality_layout = QFormLayout(quality_group)
        
        # 启用内容过滤
        self.content_filter_cb = QCheckBox("启用内容安全过滤")
        self.content_filter_cb.setChecked(True)
        quality_layout.addRow("", self.content_filter_cb)
        
        # 代码验证
        self.code_validation_cb = QCheckBox("启用生成代码验证")
        self.code_validation_cb.setChecked(True)
        quality_layout.addRow("", self.code_validation_cb)
        
        # 自动优化
        self.auto_optimize_cb = QCheckBox("自动优化生成的代码")
        self.auto_optimize_cb.setChecked(True)
        quality_layout.addRow("", self.auto_optimize_cb)
        
        layout.addWidget(quality_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "⚙️ 模型设置")
    
    def setup_usage_monitoring_tab(self):
        """设置使用量监控标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 今日使用量
        today_group = QGroupBox("今日使用量")
        today_layout = QVBoxLayout(today_group)
        
        self.today_usage_table = QTableWidget()
        self.today_usage_table.setColumnCount(4)
        self.today_usage_table.setHorizontalHeaderLabels(["服务", "请求次数", "令牌数", "预估费用"])
        self.today_usage_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        today_layout.addWidget(self.today_usage_table)
        
        layout.addWidget(today_group)
        
        # 本月使用量
        month_group = QGroupBox("本月使用量")
        month_layout = QVBoxLayout(month_group)
        
        self.month_usage_table = QTableWidget()
        self.month_usage_table.setColumnCount(4)
        self.month_usage_table.setHorizontalHeaderLabels(["服务", "请求次数", "令牌数", "预估费用"])
        self.month_usage_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        month_layout.addWidget(self.month_usage_table)
        
        layout.addWidget(month_group)
        
        # 使用量限制设置
        limits_group = QGroupBox("使用量限制")
        limits_layout = QFormLayout(limits_group)
        
        # 日限制
        self.daily_limit_spin = QSpinBox()
        self.daily_limit_spin.setRange(0, 10000)
        self.daily_limit_spin.setValue(100)
        self.daily_limit_spin.setSuffix(" 请求")
        limits_layout.addRow("日请求限制:", self.daily_limit_spin)
        
        # 月限制
        self.monthly_limit_spin = QSpinBox()
        self.monthly_limit_spin.setRange(0, 100000)
        self.monthly_limit_spin.setValue(1000)
        self.monthly_limit_spin.setSuffix(" 请求")
        limits_layout.addRow("月请求限制:", self.monthly_limit_spin)
        
        # 费用限制
        self.cost_limit_spin = QDoubleSpinBox()
        self.cost_limit_spin.setRange(0, 1000)
        self.cost_limit_spin.setValue(50.0)
        self.cost_limit_spin.setSuffix(" USD")
        limits_layout.addRow("月费用限制:", self.cost_limit_spin)
        
        # 启用限制警告
        self.limit_warning_cb = QCheckBox("达到限制时显示警告")
        self.limit_warning_cb.setChecked(True)
        limits_layout.addRow("", self.limit_warning_cb)
        
        layout.addWidget(limits_group)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新使用量数据")
        refresh_btn.clicked.connect(self.refresh_usage_data)
        layout.addWidget(refresh_btn)
        
        self.tab_widget.addTab(tab, "📊 使用监控")
    
    def setup_advanced_settings_tab(self):
        """设置高级设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 缓存设置
        cache_group = QGroupBox("缓存设置")
        cache_layout = QFormLayout(cache_group)
        
        # 启用响应缓存
        self.enable_cache_cb = QCheckBox("启用AI响应缓存")
        self.enable_cache_cb.setChecked(True)
        self.enable_cache_cb.setToolTip("缓存相似的请求以提高响应速度")
        cache_layout.addRow("", self.enable_cache_cb)
        
        # 缓存过期时间
        self.cache_expire_spin = QSpinBox()
        self.cache_expire_spin.setRange(1, 168)  # 1小时到1周
        self.cache_expire_spin.setValue(24)
        self.cache_expire_spin.setSuffix(" 小时")
        cache_layout.addRow("缓存过期时间:", self.cache_expire_spin)
        
        # 缓存大小限制
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setValue(100)
        self.cache_size_spin.setSuffix(" MB")
        cache_layout.addRow("缓存大小限制:", self.cache_size_spin)
        
        layout.addWidget(cache_group)
        
        # 代理设置
        proxy_group = QGroupBox("代理设置")
        proxy_layout = QFormLayout(proxy_group)
        
        # 启用代理
        self.enable_proxy_cb = QCheckBox("使用代理服务器")
        proxy_layout.addRow("", self.enable_proxy_cb)
        
        # 代理地址
        self.proxy_host_edit = QLineEdit()
        self.proxy_host_edit.setPlaceholderText("127.0.0.1")
        proxy_layout.addRow("代理地址:", self.proxy_host_edit)
        
        # 代理端口
        self.proxy_port_spin = QSpinBox()
        self.proxy_port_spin.setRange(1, 65535)
        self.proxy_port_spin.setValue(7890)
        proxy_layout.addRow("代理端口:", self.proxy_port_spin)
        
        # 代理认证
        self.proxy_auth_cb = QCheckBox("需要认证")
        proxy_layout.addRow("", self.proxy_auth_cb)
        
        self.proxy_username_edit = QLineEdit()
        self.proxy_username_edit.setPlaceholderText("用户名")
        self.proxy_username_edit.setEnabled(False)
        proxy_layout.addRow("用户名:", self.proxy_username_edit)
        
        self.proxy_password_edit = QLineEdit()
        self.proxy_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.proxy_password_edit.setPlaceholderText("密码")
        self.proxy_password_edit.setEnabled(False)
        proxy_layout.addRow("密码:", self.proxy_password_edit)
        
        # 连接代理认证控件
        self.proxy_auth_cb.toggled.connect(self.proxy_username_edit.setEnabled)
        self.proxy_auth_cb.toggled.connect(self.proxy_password_edit.setEnabled)
        
        layout.addWidget(proxy_group)
        
        # 日志设置
        logging_group = QGroupBox("日志设置")
        logging_layout = QFormLayout(logging_group)
        
        # 启用详细日志
        self.verbose_logging_cb = QCheckBox("启用详细日志记录")
        logging_layout.addRow("", self.verbose_logging_cb)
        
        # 保存API请求日志
        self.save_requests_cb = QCheckBox("保存API请求和响应日志")
        logging_layout.addRow("", self.save_requests_cb)
        
        # 日志保留天数
        self.log_retention_spin = QSpinBox()
        self.log_retention_spin.setRange(1, 365)
        self.log_retention_spin.setValue(30)
        self.log_retention_spin.setSuffix(" 天")
        logging_layout.addRow("日志保留天数:", self.log_retention_spin)
        
        layout.addWidget(logging_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🔧 高级设置")

        # 配置验证标签页
        self.setup_validation_tab()

    def setup_validation_tab(self):
        """设置配置验证标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 验证控制
        control_layout = QHBoxLayout()

        validate_btn = QPushButton("🔍 验证配置")
        validate_btn.clicked.connect(self.validate_current_config)
        control_layout.addWidget(validate_btn)

        auto_validate_cb = QCheckBox("自动验证")
        auto_validate_cb.setChecked(True)
        auto_validate_cb.setToolTip("配置更改时自动验证")
        control_layout.addWidget(auto_validate_cb)

        control_layout.addStretch()

        # 验证状态指示器
        self.validation_status_label = QLabel("🟡 未验证")
        self.validation_status_label.setFont(QFont("", 10, QFont.Weight.Bold))
        control_layout.addWidget(self.validation_status_label)

        layout.addLayout(control_layout)

        # 验证结果显示
        results_group = QGroupBox("验证结果")
        results_layout = QVBoxLayout(results_group)

        # 验证摘要
        summary_layout = QHBoxLayout()

        summary_layout.addWidget(QLabel("错误:"))
        self.error_count_label = QLabel("0")
        self.error_count_label.setStyleSheet("color: red; font-weight: bold;")
        summary_layout.addWidget(self.error_count_label)

        summary_layout.addWidget(QLabel("警告:"))
        self.warning_count_label = QLabel("0")
        self.warning_count_label.setStyleSheet("color: orange; font-weight: bold;")
        summary_layout.addWidget(self.warning_count_label)

        summary_layout.addWidget(QLabel("信息:"))
        self.info_count_label = QLabel("0")
        self.info_count_label.setStyleSheet("color: blue; font-weight: bold;")
        summary_layout.addWidget(self.info_count_label)

        summary_layout.addStretch()

        results_layout.addLayout(summary_layout)

        # 验证结果列表
        self.validation_results_list = QListWidget()
        self.validation_results_list.setMaximumHeight(200)
        results_layout.addWidget(self.validation_results_list)

        layout.addWidget(results_group)

        # 建议和帮助
        recommendations_group = QGroupBox("配置建议")
        recommendations_layout = QVBoxLayout(recommendations_group)

        self.recommendations_text = QTextEdit()
        self.recommendations_text.setMaximumHeight(150)
        self.recommendations_text.setReadOnly(True)
        recommendations_layout.addWidget(self.recommendations_text)

        layout.addWidget(recommendations_group)

        # 配置模板
        templates_group = QGroupBox("配置模板")
        templates_layout = QHBoxLayout(templates_group)

        templates_layout.addWidget(QLabel("快速配置:"))

        self.config_template_combo = QComboBox()
        self.config_template_combo.addItems([
            "选择模板...", "开发环境", "生产环境", "低成本模式", "高性能模式"
        ])
        self.config_template_combo.currentTextChanged.connect(self.apply_config_template)
        templates_layout.addWidget(self.config_template_combo)

        apply_template_btn = QPushButton("应用模板")
        apply_template_btn.clicked.connect(self.apply_selected_template)
        templates_layout.addWidget(apply_template_btn)

        templates_layout.addStretch()

        layout.addWidget(templates_group)

        layout.addStretch()

        self.tab_widget.addTab(tab, "✅ 配置验证")

    def validate_current_config(self):
        """验证当前配置"""
        try:
            from core.ai_config_validator import AIConfigValidator

            validator = AIConfigValidator()
            current_config = self.get_config()

            validation_summary = validator.validate_and_get_summary(current_config)

            # 更新验证状态
            summary = validation_summary["summary"]
            if summary["is_valid"]:
                self.validation_status_label.setText("🟢 配置有效")
                self.validation_status_label.setStyleSheet("color: green;")
            else:
                self.validation_status_label.setText("🔴 配置有误")
                self.validation_status_label.setStyleSheet("color: red;")

            # 更新计数
            self.error_count_label.setText(str(summary["errors"]))
            self.warning_count_label.setText(str(summary["warnings"]))
            self.info_count_label.setText(str(summary["info"]))

            # 更新结果列表
            self.validation_results_list.clear()
            for result in validation_summary["results"]:
                icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[result.level.value]
                item_text = f"{icon} {result.message}"

                item = QListWidgetItem(item_text)
                if result.level.value == "error":
                    item.setBackground(QColor("#ffebee"))
                elif result.level.value == "warning":
                    item.setBackground(QColor("#fff3e0"))
                else:
                    item.setBackground(QColor("#e3f2fd"))

                self.validation_results_list.addItem(item)

            # 生成建议
            self.generate_configuration_recommendations(validation_summary)

        except Exception as e:
            logger.error(f"验证配置失败: {e}")
            self.validation_status_label.setText("🔴 验证失败")
            self.validation_status_label.setStyleSheet("color: red;")

    def generate_configuration_recommendations(self, validation_summary: Dict[str, any]):
        """生成配置建议"""
        recommendations = []

        try:
            results = validation_summary["results"]
            summary = validation_summary["summary"]

            if summary["errors"] > 0:
                recommendations.append("🔴 发现配置错误，请先修复错误项目")

            if summary["warnings"] > 0:
                recommendations.append("⚠️ 发现配置警告，建议优化相关设置")

            # 基于验证结果生成具体建议
            error_fields = [r.field for r in results if r.level.value == "error"]

            if any("api_key" in field for field in error_fields):
                recommendations.append("• 请检查并修正API密钥配置")

            if "temperature" in error_fields:
                recommendations.append("• 请调整温度参数到合理范围(0-2)")

            if "max_tokens" in error_fields:
                recommendations.append("• 请设置合适的最大令牌数(建议1000-4000)")

            # 性能优化建议
            recommendations.extend([
                "",
                "💡 性能优化建议:",
                "• 启用缓存可以显著提高响应速度",
                "• 配置多个AI服务可以提高可用性",
                "• 合理设置使用量限制可以控制成本"
            ])

            if not recommendations:
                recommendations = ["✅ 配置良好，无需特别调整"]

            self.recommendations_text.setPlainText("\n".join(recommendations))

        except Exception as e:
            logger.error(f"生成配置建议失败: {e}")

    def apply_config_template(self, template_name: str):
        """应用配置模板"""
        if template_name == "选择模板...":
            return

        templates = {
            "开发环境": {
                "temperature": 0.7,
                "max_tokens": 2000,
                "timeout": 60,
                "max_retries": 3,
                "enable_cache": True,
                "cache_expire_hours": 1,
                "daily_limit": 200,
                "monthly_limit": 2000,
                "cost_limit": 20.0
            },
            "生产环境": {
                "temperature": 0.5,
                "max_tokens": 3000,
                "timeout": 30,
                "max_retries": 5,
                "enable_cache": True,
                "cache_expire_hours": 24,
                "daily_limit": 500,
                "monthly_limit": 5000,
                "cost_limit": 100.0
            },
            "低成本模式": {
                "temperature": 0.3,
                "max_tokens": 1500,
                "timeout": 45,
                "max_retries": 2,
                "enable_cache": True,
                "cache_expire_hours": 48,
                "daily_limit": 50,
                "monthly_limit": 500,
                "cost_limit": 10.0,
                "preferred_service": "gemini"
            },
            "高性能模式": {
                "temperature": 0.8,
                "max_tokens": 4000,
                "timeout": 20,
                "max_retries": 1,
                "enable_cache": True,
                "cache_expire_hours": 12,
                "daily_limit": 1000,
                "monthly_limit": 10000,
                "cost_limit": 200.0
            }
        }

        if template_name in templates:
            self.apply_template_config(templates[template_name])

    def apply_selected_template(self):
        """应用选中的模板"""
        template_name = self.config_template_combo.currentText()
        self.apply_config_template(template_name)

    def apply_template_config(self, template_config: Dict[str, any]):
        """应用模板配置"""
        try:
            # 应用生成参数
            if "temperature" in template_config:
                self.temperature_slider.setValue(int(template_config["temperature"] * 100))

            if "max_tokens" in template_config:
                self.max_tokens_spin.setValue(template_config["max_tokens"])

            if "timeout" in template_config:
                self.timeout_spin.setValue(template_config["timeout"])

            if "max_retries" in template_config:
                self.retry_spin.setValue(template_config["max_retries"])

            # 应用缓存设置
            if "enable_cache" in template_config:
                self.enable_cache_cb.setChecked(template_config["enable_cache"])

            if "cache_expire_hours" in template_config:
                self.cache_expire_spin.setValue(template_config["cache_expire_hours"])

            # 应用使用量限制
            if "daily_limit" in template_config:
                self.daily_limit_spin.setValue(template_config["daily_limit"])

            if "monthly_limit" in template_config:
                self.monthly_limit_spin.setValue(template_config["monthly_limit"])

            if "cost_limit" in template_config:
                self.cost_limit_spin.setValue(template_config["cost_limit"])

            # 应用首选服务
            if "preferred_service" in template_config:
                index = self.preferred_service_combo.findText(template_config["preferred_service"])
                if index >= 0:
                    self.preferred_service_combo.setCurrentIndex(index)

            # 自动验证
            self.validate_current_config()

            logger.info(f"已应用配置模板: {self.config_template_combo.currentText()}")

        except Exception as e:
            logger.error(f"应用模板配置失败: {e}")

    def toggle_password_visibility(self, line_edit: QLineEdit, show: bool):
        """切换密码可见性"""
        if show:
            line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def on_temperature_changed(self, value: int):
        """温度滑块改变事件"""
        temp = value / 100.0
        self.temperature_label.setText(f"{temp:.1f}")

    def test_connection(self, service: str):
        """测试服务连接"""
        try:
            # 获取API密钥
            api_key = ""
            model = ""

            if service == "openai":
                api_key = self.openai_key_edit.text().strip()
                model = self.openai_model_combo.currentText()
                test_btn = self.openai_test_btn
            elif service == "claude":
                api_key = self.claude_key_edit.text().strip()
                model = self.claude_model_combo.currentText()
                test_btn = self.claude_test_btn
            elif service == "gemini":
                api_key = self.gemini_key_edit.text().strip()
                model = self.gemini_model_combo.currentText()
                test_btn = self.gemini_test_btn

            if not api_key:
                QMessageBox.warning(self, "警告", f"请先输入{service.upper()} API Key")
                return

            # 禁用测试按钮
            test_btn.setText("测试中...")
            test_btn.setEnabled(False)

            # 启动测试线程
            tester = ModelTester(service, api_key, model)
            tester.test_completed.connect(self.on_test_completed)
            self.model_testers[service] = tester
            tester.start()

        except Exception as e:
            logger.error(f"测试{service}连接失败: {e}")
            QMessageBox.critical(self, "错误", f"测试连接失败:\n{str(e)}")

    def test_all_connections(self):
        """测试所有连接"""
        services = []

        if self.openai_key_edit.text().strip():
            services.append("openai")
        if self.claude_key_edit.text().strip():
            services.append("claude")
        if self.gemini_key_edit.text().strip():
            services.append("gemini")

        if not services:
            QMessageBox.warning(self, "警告", "请先配置至少一个API Key")
            return

        for service in services:
            self.test_connection(service)

    def on_test_completed(self, service: str, success: bool, message: str):
        """测试完成事件"""
        try:
            # 恢复测试按钮
            if service == "openai":
                test_btn = self.openai_test_btn
            elif service == "claude":
                test_btn = self.claude_test_btn
            elif service == "gemini":
                test_btn = self.gemini_test_btn

            test_btn.setText("测试")
            test_btn.setEnabled(True)

            # 显示结果
            if success:
                QMessageBox.information(self, "测试成功", f"{service.upper()} 连接测试成功！\n{message}")
            else:
                QMessageBox.critical(self, "测试失败", f"{service.upper()} 连接测试失败:\n{message}")

            # 清理测试器
            if service in self.model_testers:
                del self.model_testers[service]

        except Exception as e:
            logger.error(f"处理测试结果失败: {e}")

    def load_template_preset(self, preset_name: str):
        """加载模板预设"""
        templates = {
            "默认模板": {
                "system": "你是一个专业的网页动画开发者。请根据用户描述生成HTML+CSS+JS动画代码。",
                "prefix": "请生成动画效果："
            },
            "专业动画师": {
                "system": "你是一位经验丰富的动画师，精通各种动画技术和设计原理。请创建流畅、自然、符合物理规律的动画效果。",
                "prefix": "作为专业动画师，请设计："
            },
            "创意设计师": {
                "system": "你是一位富有创意的UI/UX设计师，擅长创造独特、吸引人的视觉效果。请注重美感和用户体验。",
                "prefix": "请设计一个创意动画："
            },
            "技术开发者": {
                "system": "你是一位技术专家，精通前端开发和动画技术。请生成高性能、兼容性好的代码。",
                "prefix": "请实现技术方案："
            },
            "简洁模式": {
                "system": "生成简洁、高效的动画代码。",
                "prefix": ""
            }
        }

        if preset_name in templates:
            template = templates[preset_name]
            self.system_prompt_edit.setPlainText(template["system"])
            self.user_prompt_prefix_edit.setText(template["prefix"])

    def load_selected_template(self):
        """加载选中的模板"""
        preset_name = self.template_preset_combo.currentText()
        self.load_template_preset(preset_name)

    def save_current_template(self):
        """保存当前模板"""
        # 简化实现
        QMessageBox.information(self, "提示", "模板保存功能将在后续版本中实现")

    def refresh_usage_data(self):
        """刷新使用量数据"""
        try:
            # 刷新今日使用量
            today_usage = self.usage_monitor.get_daily_usage()
            self.update_usage_table(self.today_usage_table, today_usage)

            # 刷新本月使用量
            month_usage = self.usage_monitor.get_monthly_usage()
            self.update_usage_table(self.month_usage_table, month_usage)

        except Exception as e:
            logger.error(f"刷新使用量数据失败: {e}")

    def update_usage_table(self, table: QTableWidget, usage_data: Dict[str, Any]):
        """更新使用量表格"""
        table.setRowCount(len(usage_data))

        for row, (service, data) in enumerate(usage_data.items()):
            table.setItem(row, 0, QTableWidgetItem(service.upper()))
            table.setItem(row, 1, QTableWidgetItem(str(data.get("requests", 0))))
            table.setItem(row, 2, QTableWidgetItem(str(data.get("tokens", 0))))
            table.setItem(row, 3, QTableWidgetItem(f"${data.get('cost', 0.0):.2f}"))

    def import_config(self):
        """导入配置"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "导入AI配置", "", "JSON文件 (*.json);;所有文件 (*)"
            )

            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # 应用配置
                self.apply_imported_config(config)
                QMessageBox.information(self, "成功", "配置导入成功")

        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            QMessageBox.critical(self, "错误", f"导入配置失败:\n{str(e)}")

    def export_config(self):
        """导出配置"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出AI配置", "ai_config.json", "JSON文件 (*.json);;所有文件 (*)"
            )

            if file_path:
                config = self.get_config()

                # 移除敏感信息（API密钥）
                export_config = config.copy()
                for key in list(export_config.keys()):
                    if "api_key" in key:
                        export_config[key] = ""

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_config, f, ensure_ascii=False, indent=2)

                QMessageBox.information(self, "成功", "配置导出成功\n注意：API密钥已被移除")

        except Exception as e:
            logger.error(f"导出配置失败: {e}")
            QMessageBox.critical(self, "错误", f"导出配置失败:\n{str(e)}")

    def apply_imported_config(self, config: Dict[str, Any]):
        """应用导入的配置"""
        # API配置
        if "openai_api_key" in config:
            self.openai_key_edit.setText(config["openai_api_key"])
        if "claude_api_key" in config:
            self.claude_key_edit.setText(config["claude_api_key"])
        if "gemini_api_key" in config:
            self.gemini_key_edit.setText(config["gemini_api_key"])

        # 模型设置
        if "openai_model" in config:
            index = self.openai_model_combo.findText(config["openai_model"])
            if index >= 0:
                self.openai_model_combo.setCurrentIndex(index)

        # 其他设置...

    def load_current_config(self):
        """加载当前配置"""
        try:
            # 加载API密钥
            self.openai_key_edit.setText(self.current_config.get("openai_api_key", ""))
            self.claude_key_edit.setText(self.current_config.get("claude_api_key", ""))
            self.gemini_key_edit.setText(self.current_config.get("gemini_api_key", ""))

            # 加载首选服务
            preferred = self.current_config.get("preferred_service", "gemini")
            index = self.preferred_service_combo.findText(preferred)
            if index >= 0:
                self.preferred_service_combo.setCurrentIndex(index)

            # 刷新使用量数据
            self.refresh_usage_data()

        except Exception as e:
            logger.error(f"加载当前配置失败: {e}")

    def apply_config(self):
        """应用配置"""
        try:
            config = self.get_config()
            self.config_changed.emit(config)
            logger.info("AI配置已应用")

        except Exception as e:
            logger.error(f"应用配置失败: {e}")
            QMessageBox.critical(self, "错误", f"应用配置失败:\n{str(e)}")

    def get_config(self) -> Dict[str, Any]:
        """获取配置数据"""
        return {
            # API配置
            "openai_api_key": self.openai_key_edit.text().strip(),
            "claude_api_key": self.claude_key_edit.text().strip(),
            "gemini_api_key": self.gemini_key_edit.text().strip(),
            "preferred_service": self.preferred_service_combo.currentText(),

            # 模型设置
            "openai_model": self.openai_model_combo.currentText(),
            "claude_model": self.claude_model_combo.currentText(),
            "gemini_model": self.gemini_model_combo.currentText(),

            # 生成参数
            "temperature": self.temperature_slider.value() / 100.0,
            "max_tokens": self.max_tokens_spin.value(),
            "timeout": self.timeout_spin.value(),
            "max_retries": self.retry_spin.value(),

            # 提示词模板
            "system_prompt": self.system_prompt_edit.toPlainText(),
            "user_prompt_prefix": self.user_prompt_prefix_edit.text(),

            # 质量控制
            "content_filter": self.content_filter_cb.isChecked(),
            "code_validation": self.code_validation_cb.isChecked(),
            "auto_optimize": self.auto_optimize_cb.isChecked(),

            # 使用量限制
            "daily_limit": self.daily_limit_spin.value(),
            "monthly_limit": self.monthly_limit_spin.value(),
            "cost_limit": self.cost_limit_spin.value(),
            "limit_warning": self.limit_warning_cb.isChecked(),

            # 高级设置
            "enable_cache": self.enable_cache_cb.isChecked(),
            "cache_expire_hours": self.cache_expire_spin.value(),
            "cache_size_mb": self.cache_size_spin.value(),
            "enable_proxy": self.enable_proxy_cb.isChecked(),
            "proxy_host": self.proxy_host_edit.text(),
            "proxy_port": self.proxy_port_spin.value(),
            "proxy_auth": self.proxy_auth_cb.isChecked(),
            "proxy_username": self.proxy_username_edit.text(),
            "proxy_password": self.proxy_password_edit.text(),
            "verbose_logging": self.verbose_logging_cb.isChecked(),
            "save_requests": self.save_requests_cb.isChecked(),
            "log_retention_days": self.log_retention_spin.value(),

            # 自动切换设置
            "auto_fallback": self.auto_fallback_cb.isChecked(),
            "fallback_order": self.fallback_order_edit.text().split(",") if self.fallback_order_edit.text() else []
        }
