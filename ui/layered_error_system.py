"""
AI Animation Studio - 分层错误信息系统
实现专业级错误处理，提供分层错误信息和智能修复建议
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QDialog, QTextEdit, QTabWidget, QGroupBox, QFormLayout,
                             QScrollArea, QFrame, QProgressBar, QCheckBox, QComboBox,
                             QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
                             QSplitter, QMessageBox, QApplication, QMenu, QToolButton,
                             QButtonGroup, QRadioButton, QSpinBox, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QThread, QMutex, QPropertyAnimation
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QBrush, QPen, QTextCharFormat

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
import json
import traceback
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from core.logger import get_logger

logger = get_logger("layered_error_system")


class ErrorSeverity(Enum):
    """错误严重程度枚举"""
    INFO = "info"           # 信息
    WARNING = "warning"     # 警告
    ERROR = "error"         # 错误
    CRITICAL = "critical"   # 严重错误
    FATAL = "fatal"         # 致命错误


class ErrorCategory(Enum):
    """错误分类枚举"""
    SYSTEM = "system"               # 系统错误
    NETWORK = "network"             # 网络错误
    AI_SERVICE = "ai_service"       # AI服务错误
    FILE_IO = "file_io"            # 文件IO错误
    AUDIO_PROCESSING = "audio"      # 音频处理错误
    ANIMATION = "animation"         # 动画错误
    UI_COMPONENT = "ui_component"   # UI组件错误
    USER_INPUT = "user_input"       # 用户输入错误
    CONFIGURATION = "configuration" # 配置错误
    DEPENDENCY = "dependency"       # 依赖错误


class ErrorContext(Enum):
    """错误上下文枚举"""
    STARTUP = "startup"             # 启动时
    AUDIO_IMPORT = "audio_import"   # 音频导入
    AI_GENERATION = "ai_generation" # AI生成
    PREVIEW = "preview"             # 预览
    EXPORT = "export"               # 导出
    SAVE_LOAD = "save_load"        # 保存加载
    UI_INTERACTION = "ui_interaction" # UI交互


@dataclass
class ErrorInfo:
    """错误信息数据类"""
    error_id: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    timestamp: datetime
    
    # 分层信息
    simple_message: str         # 简单用户友好信息
    detailed_message: str       # 详细描述
    technical_details: str      # 技术细节
    
    # 解决方案
    solutions: List[str] = field(default_factory=list)
    auto_fix_available: bool = False
    auto_fix_function: Optional[Callable] = None
    
    # 上下文信息
    component: str = ""
    file_path: str = ""
    line_number: int = 0
    stack_trace: str = ""
    
    # 用户操作
    user_action: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    
    # 影响评估
    impact_description: str = ""
    affected_features: List[str] = field(default_factory=list)
    
    # 统计信息
    occurrence_count: int = 1
    first_occurrence: Optional[datetime] = None
    last_occurrence: Optional[datetime] = None


class ErrorTemplateManager:
    """错误模板管理器"""
    
    def __init__(self):
        self.templates = self.initialize_error_templates()
        
        logger.info("错误模板管理器初始化完成")
    
    def initialize_error_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化错误模板"""
        return {
            # AI服务错误
            "ai_generation_failed": {
                "severity": ErrorSeverity.ERROR,
                "category": ErrorCategory.AI_SERVICE,
                "simple": "AI动画生成失败，请检查网络连接和API设置",
                "detailed": "Gemini API调用失败，可能原因：网络连接问题、API密钥无效或配额不足",
                "solutions": [
                    "检查网络连接是否正常",
                    "验证API密钥是否正确",
                    "确认API配额是否充足",
                    "尝试切换到其他AI模型",
                    "检查防火墙设置"
                ],
                "impact": "AI动画生成功能无法使用",
                "affected_features": ["AI生成", "智能推荐", "自动优化"]
            },
            
            "api_key_invalid": {
                "severity": ErrorSeverity.CRITICAL,
                "category": ErrorCategory.CONFIGURATION,
                "simple": "API密钥无效，请检查配置",
                "detailed": "提供的API密钥格式不正确或已过期，无法访问AI服务",
                "solutions": [
                    "检查API密钥格式是否正确",
                    "确认API密钥是否已过期",
                    "重新生成API密钥",
                    "检查API密钥权限设置"
                ],
                "impact": "所有AI功能无法使用",
                "affected_features": ["AI生成", "智能分析", "自动建议"],
                "auto_fix": True
            },
            
            # 音频处理错误
            "audio_load_failed": {
                "severity": ErrorSeverity.ERROR,
                "category": ErrorCategory.AUDIO_PROCESSING,
                "simple": "音频文件加载失败，请检查文件格式",
                "detailed": "不支持的音频格式或文件已损坏，支持的格式：MP3、WAV、M4A、OGG",
                "solutions": [
                    "确认文件格式是否支持",
                    "尝试使用其他音频文件",
                    "使用音频转换工具转换格式",
                    "检查文件是否完整",
                    "确认文件路径是否正确"
                ],
                "impact": "无法导入音频文件，影响动画创建",
                "affected_features": ["音频导入", "时间轴同步", "音频分析"]
            },
            
            "audio_decode_error": {
                "severity": ErrorSeverity.WARNING,
                "category": ErrorCategory.AUDIO_PROCESSING,
                "simple": "音频解码出现问题，可能影响播放质量",
                "detailed": "音频文件解码过程中遇到问题，可能是编码格式特殊或文件部分损坏",
                "solutions": [
                    "尝试重新导入音频文件",
                    "使用标准格式的音频文件",
                    "检查音频文件完整性",
                    "降低音频质量设置"
                ],
                "impact": "音频播放可能不稳定",
                "affected_features": ["音频播放", "波形显示"]
            },
            
            # 文件IO错误
            "file_not_found": {
                "severity": ErrorSeverity.ERROR,
                "category": ErrorCategory.FILE_IO,
                "simple": "找不到指定的文件",
                "detailed": "系统无法找到指定路径的文件，可能文件已被移动、删除或路径不正确",
                "solutions": [
                    "检查文件路径是否正确",
                    "确认文件是否存在",
                    "检查文件权限设置",
                    "尝试重新选择文件"
                ],
                "impact": "无法访问所需文件",
                "affected_features": ["文件操作", "项目加载"]
            },
            
            "permission_denied": {
                "severity": ErrorSeverity.ERROR,
                "category": ErrorCategory.FILE_IO,
                "simple": "没有访问文件的权限",
                "detailed": "当前用户没有足够的权限访问指定文件或目录",
                "solutions": [
                    "以管理员身份运行程序",
                    "检查文件权限设置",
                    "选择其他可访问的位置",
                    "联系系统管理员"
                ],
                "impact": "无法读写文件",
                "affected_features": ["文件保存", "项目导出"]
            },
            
            # 系统错误
            "memory_insufficient": {
                "severity": ErrorSeverity.CRITICAL,
                "category": ErrorCategory.SYSTEM,
                "simple": "系统内存不足",
                "detailed": "可用内存不足以完成当前操作，可能导致程序不稳定",
                "solutions": [
                    "关闭其他不必要的程序",
                    "减少项目复杂度",
                    "降低预览质量",
                    "重启应用程序",
                    "增加系统内存"
                ],
                "impact": "程序可能变慢或崩溃",
                "affected_features": ["预览", "导出", "复杂动画"]
            },
            
            "dependency_missing": {
                "severity": ErrorSeverity.FATAL,
                "category": ErrorCategory.DEPENDENCY,
                "simple": "缺少必要的依赖组件",
                "detailed": "程序运行所需的依赖库或组件未正确安装",
                "solutions": [
                    "重新安装程序",
                    "手动安装缺失的依赖",
                    "检查Python环境",
                    "更新系统组件"
                ],
                "impact": "程序无法正常启动或运行",
                "affected_features": ["程序启动", "核心功能"],
                "auto_fix": True
            },
            
            # UI组件错误
            "ui_component_error": {
                "severity": ErrorSeverity.WARNING,
                "category": ErrorCategory.UI_COMPONENT,
                "simple": "界面组件出现异常",
                "detailed": "某个界面组件在运行过程中遇到问题，可能影响用户交互",
                "solutions": [
                    "刷新界面",
                    "重启程序",
                    "重置界面布局",
                    "检查界面配置"
                ],
                "impact": "部分界面功能可能不可用",
                "affected_features": ["用户界面", "交互操作"]
            },
            
            # 网络错误
            "network_timeout": {
                "severity": ErrorSeverity.WARNING,
                "category": ErrorCategory.NETWORK,
                "simple": "网络连接超时",
                "detailed": "网络请求超时，可能是网络连接不稳定或服务器响应慢",
                "solutions": [
                    "检查网络连接",
                    "稍后重试",
                    "检查防火墙设置",
                    "尝试使用其他网络"
                ],
                "impact": "在线功能暂时不可用",
                "affected_features": ["AI服务", "在线更新", "云同步"]
            },
            
            # 用户输入错误
            "invalid_input": {
                "severity": ErrorSeverity.INFO,
                "category": ErrorCategory.USER_INPUT,
                "simple": "输入的数据格式不正确",
                "detailed": "用户输入的数据不符合预期格式或范围要求",
                "solutions": [
                    "检查输入格式",
                    "参考输入示例",
                    "使用推荐的数值范围",
                    "查看帮助文档"
                ],
                "impact": "当前操作无法完成",
                "affected_features": ["数据输入", "参数设置"]
            }
        }
    
    def get_template(self, error_type: str) -> Optional[Dict[str, Any]]:
        """获取错误模板"""
        return self.templates.get(error_type)
    
    def create_error_info(self, error_type: str, context: ErrorContext, 
                         technical_details: str = "", **kwargs) -> Optional[ErrorInfo]:
        """根据模板创建错误信息"""
        template = self.get_template(error_type)
        if not template:
            return None
        
        error_info = ErrorInfo(
            error_id=f"{error_type}_{int(time.time())}",
            severity=template["severity"],
            category=template["category"],
            context=context,
            timestamp=datetime.now(),
            simple_message=template["simple"],
            detailed_message=template["detailed"],
            technical_details=technical_details,
            solutions=template["solutions"].copy(),
            auto_fix_available=template.get("auto_fix", False),
            impact_description=template["impact"],
            affected_features=template["affected_features"].copy()
        )
        
        # 添加额外信息
        for key, value in kwargs.items():
            if hasattr(error_info, key):
                setattr(error_info, key, value)
        
        return error_info
    
    def add_custom_template(self, error_type: str, template: Dict[str, Any]):
        """添加自定义错误模板"""
        self.templates[error_type] = template
        logger.info(f"添加自定义错误模板: {error_type}")


class LayeredErrorDialog(QDialog):
    """分层错误对话框"""
    
    auto_fix_requested = pyqtSignal(str)  # 自动修复请求
    help_requested = pyqtSignal(str)      # 帮助请求
    
    def __init__(self, error_info: ErrorInfo, parent=None):
        super().__init__(parent)
        self.error_info = error_info
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("错误信息")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 错误概要
        self.create_error_summary(layout)
        
        # 分层信息标签页
        self.create_tabbed_content(layout)
        
        # 操作按钮
        self.create_action_buttons(layout)
    
    def create_error_summary(self, layout: QVBoxLayout):
        """创建错误概要"""
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        summary_frame.setStyleSheet(self.get_severity_style())
        
        summary_layout = QHBoxLayout(summary_frame)
        
        # 错误图标
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setText(self.get_severity_icon())
        icon_label.setStyleSheet("font-size: 32px;")
        summary_layout.addWidget(icon_label)
        
        # 错误信息
        info_layout = QVBoxLayout()
        
        # 简单消息
        simple_label = QLabel(self.error_info.simple_message)
        simple_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        simple_label.setWordWrap(True)
        info_layout.addWidget(simple_label)
        
        # 错误分类和严重程度
        meta_label = QLabel(
            f"分类: {self.error_info.category.value} | "
            f"严重程度: {self.error_info.severity.value} | "
            f"时间: {self.error_info.timestamp.strftime('%H:%M:%S')}"
        )
        meta_label.setStyleSheet("color: #666; font-size: 10px;")
        info_layout.addWidget(meta_label)
        
        summary_layout.addLayout(info_layout)
        summary_layout.addStretch()
        
        layout.addWidget(summary_frame)
    
    def create_tabbed_content(self, layout: QVBoxLayout):
        """创建分层内容标签页"""
        self.tab_widget = QTabWidget()
        
        # 详细信息标签页
        self.create_details_tab()
        
        # 解决方案标签页
        self.create_solutions_tab()
        
        # 技术细节标签页
        self.create_technical_tab()
        
        # 影响分析标签页
        self.create_impact_tab()
        
        layout.addWidget(self.tab_widget)
    
    def create_details_tab(self):
        """创建详细信息标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 详细描述
        desc_group = QGroupBox("详细描述")
        desc_layout = QVBoxLayout(desc_group)
        
        desc_text = QTextEdit()
        desc_text.setPlainText(self.error_info.detailed_message)
        desc_text.setReadOnly(True)
        desc_text.setMaximumHeight(100)
        desc_layout.addWidget(desc_text)
        
        layout.addWidget(desc_group)
        
        # 上下文信息
        context_group = QGroupBox("上下文信息")
        context_layout = QFormLayout(context_group)
        
        context_layout.addRow("发生位置:", QLabel(self.error_info.context.value))
        if self.error_info.component:
            context_layout.addRow("组件:", QLabel(self.error_info.component))
        if self.error_info.user_action:
            context_layout.addRow("用户操作:", QLabel(self.error_info.user_action))
        if self.error_info.file_path:
            context_layout.addRow("文件路径:", QLabel(self.error_info.file_path))
        
        layout.addWidget(context_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "📋 详细信息")
    
    def create_solutions_tab(self):
        """创建解决方案标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 自动修复
        if self.error_info.auto_fix_available:
            auto_fix_group = QGroupBox("🔧 自动修复")
            auto_fix_layout = QVBoxLayout(auto_fix_group)
            
            auto_fix_desc = QLabel("系统可以尝试自动修复此问题")
            auto_fix_desc.setStyleSheet("color: #2e7d32; font-weight: bold;")
            auto_fix_layout.addWidget(auto_fix_desc)
            
            self.auto_fix_btn = QPushButton("立即自动修复")
            self.auto_fix_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
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
            self.auto_fix_btn.clicked.connect(self.request_auto_fix)
            auto_fix_layout.addWidget(self.auto_fix_btn)
            
            layout.addWidget(auto_fix_group)
        
        # 手动解决方案
        solutions_group = QGroupBox("💡 解决方案")
        solutions_layout = QVBoxLayout(solutions_group)
        
        for i, solution in enumerate(self.error_info.solutions, 1):
            solution_label = QLabel(f"{i}. {solution}")
            solution_label.setWordWrap(True)
            solution_label.setStyleSheet("margin: 4px 0; padding: 4px;")
            solutions_layout.addWidget(solution_label)
        
        layout.addWidget(solutions_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "💡 解决方案")
    
    def create_technical_tab(self):
        """创建技术细节标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 技术详情
        tech_group = QGroupBox("技术详情")
        tech_layout = QVBoxLayout(tech_group)
        
        tech_text = QTextEdit()
        tech_text.setPlainText(self.error_info.technical_details)
        tech_text.setReadOnly(True)
        tech_text.setFont(QFont("Consolas", 9))
        tech_layout.addWidget(tech_text)
        
        layout.addWidget(tech_group)
        
        # 堆栈跟踪
        if self.error_info.stack_trace:
            stack_group = QGroupBox("堆栈跟踪")
            stack_layout = QVBoxLayout(stack_group)
            
            stack_text = QTextEdit()
            stack_text.setPlainText(self.error_info.stack_trace)
            stack_text.setReadOnly(True)
            stack_text.setFont(QFont("Consolas", 8))
            stack_layout.addWidget(stack_text)
            
            layout.addWidget(stack_group)
        
        self.tab_widget.addTab(tab, "🔧 技术细节")
    
    def create_impact_tab(self):
        """创建影响分析标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 影响描述
        impact_group = QGroupBox("影响分析")
        impact_layout = QVBoxLayout(impact_group)
        
        impact_label = QLabel(self.error_info.impact_description)
        impact_label.setWordWrap(True)
        impact_label.setStyleSheet("font-size: 11px; margin: 8px;")
        impact_layout.addWidget(impact_label)
        
        layout.addWidget(impact_group)
        
        # 受影响的功能
        if self.error_info.affected_features:
            features_group = QGroupBox("受影响的功能")
            features_layout = QVBoxLayout(features_group)
            
            for feature in self.error_info.affected_features:
                feature_label = QLabel(f"• {feature}")
                feature_label.setStyleSheet("color: #d32f2f; margin: 2px 8px;")
                features_layout.addWidget(feature_label)
            
            layout.addWidget(features_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "⚠️ 影响分析")
    
    def create_action_buttons(self, layout: QVBoxLayout):
        """创建操作按钮"""
        button_layout = QHBoxLayout()
        
        # 帮助按钮
        help_btn = QPushButton("获取帮助")
        help_btn.clicked.connect(self.request_help)
        button_layout.addWidget(help_btn)
        
        # 复制错误信息按钮
        copy_btn = QPushButton("复制错误信息")
        copy_btn.clicked.connect(self.copy_error_info)
        button_layout.addWidget(copy_btn)
        
        button_layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def setup_connections(self):
        """设置信号连接"""
        pass
    
    def get_severity_style(self) -> str:
        """获取严重程度样式"""
        styles = {
            ErrorSeverity.INFO: "background-color: #e3f2fd; border-left: 4px solid #2196f3;",
            ErrorSeverity.WARNING: "background-color: #fff3e0; border-left: 4px solid #ff9800;",
            ErrorSeverity.ERROR: "background-color: #ffebee; border-left: 4px solid #f44336;",
            ErrorSeverity.CRITICAL: "background-color: #fce4ec; border-left: 4px solid #e91e63;",
            ErrorSeverity.FATAL: "background-color: #f3e5f5; border-left: 4px solid #9c27b0;"
        }
        return styles.get(self.error_info.severity, styles[ErrorSeverity.ERROR])
    
    def get_severity_icon(self) -> str:
        """获取严重程度图标"""
        icons = {
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.CRITICAL: "🚨",
            ErrorSeverity.FATAL: "💀"
        }
        return icons.get(self.error_info.severity, "❌")
    
    def request_auto_fix(self):
        """请求自动修复"""
        self.auto_fix_requested.emit(self.error_info.error_id)
    
    def request_help(self):
        """请求帮助"""
        self.help_requested.emit(self.error_info.error_id)
    
    def copy_error_info(self):
        """复制错误信息"""
        try:
            error_text = f"""
错误ID: {self.error_info.error_id}
时间: {self.error_info.timestamp}
严重程度: {self.error_info.severity.value}
分类: {self.error_info.category.value}
上下文: {self.error_info.context.value}

简单描述: {self.error_info.simple_message}

详细描述: {self.error_info.detailed_message}

技术细节: {self.error_info.technical_details}

解决方案:
{chr(10).join(f'{i+1}. {sol}' for i, sol in enumerate(self.error_info.solutions))}

影响: {self.error_info.impact_description}
受影响功能: {', '.join(self.error_info.affected_features)}
            """.strip()
            
            clipboard = QApplication.clipboard()
            clipboard.setText(error_text)
            
            # 显示复制成功提示
            self.show_copy_success()
            
        except Exception as e:
            logger.error(f"复制错误信息失败: {e}")
    
    def show_copy_success(self):
        """显示复制成功提示"""
        # 这里可以实现一个临时的成功提示
        pass


class ErrorStatistics:
    """错误统计"""

    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.severity_counts: Dict[ErrorSeverity, int] = {
            severity: 0 for severity in ErrorSeverity
        }
        self.category_counts: Dict[ErrorCategory, int] = {
            category: 0 for category in ErrorCategory
        }
        self.hourly_counts: Dict[int, int] = {}
        self.total_errors = 0
        self.session_start = datetime.now()

    def record_error(self, error_info: ErrorInfo):
        """记录错误"""
        self.total_errors += 1

        # 按错误类型统计
        error_type = f"{error_info.category.value}_{error_info.severity.value}"
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        # 按严重程度统计
        self.severity_counts[error_info.severity] += 1

        # 按分类统计
        self.category_counts[error_info.category] += 1

        # 按小时统计
        hour = error_info.timestamp.hour
        self.hourly_counts[hour] = self.hourly_counts.get(hour, 0) + 1

    def get_summary(self) -> Dict[str, Any]:
        """获取统计摘要"""
        session_duration = datetime.now() - self.session_start

        return {
            "total_errors": self.total_errors,
            "session_duration": str(session_duration),
            "errors_per_hour": self.total_errors / max(session_duration.total_seconds() / 3600, 0.1),
            "severity_distribution": {
                severity.value: count for severity, count in self.severity_counts.items()
            },
            "category_distribution": {
                category.value: count for category, count in self.category_counts.items()
            },
            "most_common_errors": sorted(
                self.error_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]
        }


class LayeredErrorManager(QObject):
    """分层错误管理器"""

    error_occurred = pyqtSignal(ErrorInfo)  # 错误发生信号
    error_resolved = pyqtSignal(str)        # 错误解决信号

    def __init__(self):
        super().__init__()
        self.template_manager = ErrorTemplateManager()
        self.statistics = ErrorStatistics()
        self.error_history: List[ErrorInfo] = []
        self.active_errors: Dict[str, ErrorInfo] = {}
        self.auto_fix_handlers: Dict[str, Callable] = {}
        self.max_history_size = 1000

        logger.info("分层错误管理器初始化完成")

    def handle_exception(self, exc_type, exc_value, exc_traceback,
                        context: ErrorContext = ErrorContext.UI_INTERACTION,
                        component: str = "", user_action: str = "") -> str:
        """处理异常"""
        try:
            # 确定错误类型
            error_type = self.classify_exception(exc_type, exc_value)

            # 获取技术细节
            technical_details = f"{exc_type.__name__}: {str(exc_value)}"
            stack_trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

            # 创建错误信息
            error_info = self.template_manager.create_error_info(
                error_type, context, technical_details,
                component=component,
                user_action=user_action,
                stack_trace=stack_trace
            )

            if error_info:
                return self.report_error(error_info)
            else:
                # 创建通用错误信息
                return self.report_generic_error(exc_type, exc_value, context, technical_details, stack_trace)

        except Exception as e:
            logger.error(f"处理异常时发生错误: {e}")
            return "error_handling_failed"

    def classify_exception(self, exc_type, exc_value) -> str:
        """分类异常"""
        exception_mapping = {
            FileNotFoundError: "file_not_found",
            PermissionError: "permission_denied",
            MemoryError: "memory_insufficient",
            ImportError: "dependency_missing",
            ModuleNotFoundError: "dependency_missing",
            ConnectionError: "network_timeout",
            TimeoutError: "network_timeout",
            ValueError: "invalid_input",
            TypeError: "invalid_input",
            KeyError: "configuration",
            AttributeError: "ui_component_error"
        }

        return exception_mapping.get(exc_type, "system_error")

    def report_error(self, error_info: ErrorInfo) -> str:
        """报告错误"""
        try:
            # 检查是否是重复错误
            existing_error = self.find_similar_error(error_info)
            if existing_error:
                existing_error.occurrence_count += 1
                existing_error.last_occurrence = error_info.timestamp
                error_id = existing_error.error_id
            else:
                # 新错误
                error_info.first_occurrence = error_info.timestamp
                error_info.last_occurrence = error_info.timestamp
                self.active_errors[error_info.error_id] = error_info
                error_id = error_info.error_id

            # 添加到历史记录
            self.error_history.append(error_info)
            if len(self.error_history) > self.max_history_size:
                self.error_history.pop(0)

            # 更新统计
            self.statistics.record_error(error_info)

            # 发送信号
            self.error_occurred.emit(error_info)

            # 记录日志
            self.log_error(error_info)

            return error_id

        except Exception as e:
            logger.error(f"报告错误失败: {e}")
            return "error_reporting_failed"

    def report_generic_error(self, exc_type, exc_value, context: ErrorContext,
                           technical_details: str, stack_trace: str) -> str:
        """报告通用错误"""
        error_info = ErrorInfo(
            error_id=f"generic_{int(time.time())}",
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.SYSTEM,
            context=context,
            timestamp=datetime.now(),
            simple_message="程序遇到了一个未知错误",
            detailed_message=f"程序执行过程中遇到了未预期的错误: {exc_type.__name__}",
            technical_details=technical_details,
            stack_trace=stack_trace,
            solutions=[
                "尝试重新执行操作",
                "重启程序",
                "检查系统资源",
                "联系技术支持"
            ],
            impact_description="可能影响程序的正常运行",
            affected_features=["当前操作"]
        )

        return self.report_error(error_info)

    def find_similar_error(self, error_info: ErrorInfo) -> Optional[ErrorInfo]:
        """查找相似错误"""
        for existing_error in self.active_errors.values():
            if (existing_error.category == error_info.category and
                existing_error.severity == error_info.severity and
                existing_error.simple_message == error_info.simple_message):
                return existing_error
        return None

    def log_error(self, error_info: ErrorInfo):
        """记录错误日志"""
        log_level_map = {
            ErrorSeverity.INFO: logger.info,
            ErrorSeverity.WARNING: logger.warning,
            ErrorSeverity.ERROR: logger.error,
            ErrorSeverity.CRITICAL: logger.critical,
            ErrorSeverity.FATAL: logger.critical
        }

        log_func = log_level_map.get(error_info.severity, logger.error)
        log_func(f"[{error_info.error_id}] {error_info.simple_message} - {error_info.technical_details}")

    def show_error_dialog(self, error_id: str, parent=None) -> Optional[LayeredErrorDialog]:
        """显示错误对话框"""
        try:
            error_info = self.active_errors.get(error_id)
            if not error_info:
                return None

            dialog = LayeredErrorDialog(error_info, parent)
            dialog.auto_fix_requested.connect(self.handle_auto_fix_request)
            dialog.help_requested.connect(self.handle_help_request)

            return dialog

        except Exception as e:
            logger.error(f"显示错误对话框失败: {e}")
            return None

    def handle_auto_fix_request(self, error_id: str):
        """处理自动修复请求"""
        try:
            error_info = self.active_errors.get(error_id)
            if not error_info or not error_info.auto_fix_available:
                return

            # 查找自动修复处理器
            handler = self.auto_fix_handlers.get(error_info.category.value)
            if handler:
                success = handler(error_info)
                if success:
                    self.resolve_error(error_id)
                    logger.info(f"自动修复成功: {error_id}")
                else:
                    logger.warning(f"自动修复失败: {error_id}")
            else:
                logger.warning(f"未找到自动修复处理器: {error_info.category.value}")

        except Exception as e:
            logger.error(f"处理自动修复请求失败: {e}")

    def handle_help_request(self, error_id: str):
        """处理帮助请求"""
        try:
            error_info = self.active_errors.get(error_id)
            if not error_info:
                return

            # 这里可以打开帮助文档、在线支持等
            logger.info(f"用户请求帮助: {error_id}")

        except Exception as e:
            logger.error(f"处理帮助请求失败: {e}")

    def resolve_error(self, error_id: str):
        """解决错误"""
        if error_id in self.active_errors:
            del self.active_errors[error_id]
            self.error_resolved.emit(error_id)
            logger.info(f"错误已解决: {error_id}")

    def register_auto_fix_handler(self, category: str, handler: Callable):
        """注册自动修复处理器"""
        self.auto_fix_handlers[category] = handler
        logger.info(f"注册自动修复处理器: {category}")

    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计"""
        return self.statistics.get_summary()

    def get_active_errors(self) -> List[ErrorInfo]:
        """获取活跃错误"""
        return list(self.active_errors.values())

    def get_error_history(self, limit: int = 100) -> List[ErrorInfo]:
        """获取错误历史"""
        return self.error_history[-limit:]

    def clear_resolved_errors(self):
        """清除已解决的错误"""
        self.active_errors.clear()
        logger.info("已清除所有已解决的错误")

    def export_error_report(self, file_path: str):
        """导出错误报告"""
        try:
            report = {
                "generated_at": datetime.now().isoformat(),
                "statistics": self.get_error_statistics(),
                "active_errors": [
                    {
                        "error_id": error.error_id,
                        "severity": error.severity.value,
                        "category": error.category.value,
                        "context": error.context.value,
                        "timestamp": error.timestamp.isoformat(),
                        "simple_message": error.simple_message,
                        "detailed_message": error.detailed_message,
                        "technical_details": error.technical_details,
                        "solutions": error.solutions,
                        "occurrence_count": error.occurrence_count,
                        "impact_description": error.impact_description,
                        "affected_features": error.affected_features
                    }
                    for error in self.active_errors.values()
                ],
                "recent_history": [
                    {
                        "error_id": error.error_id,
                        "severity": error.severity.value,
                        "category": error.category.value,
                        "timestamp": error.timestamp.isoformat(),
                        "simple_message": error.simple_message
                    }
                    for error in self.error_history[-50:]
                ]
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            logger.info(f"错误报告已导出到: {file_path}")

        except Exception as e:
            logger.error(f"导出错误报告失败: {e}")


class ErrorNotificationWidget(QWidget):
    """错误通知组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_notifications: List[QWidget] = []
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        self.setFixedWidth(300)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        self.layout.addStretch()

    def show_notification(self, error_info: ErrorInfo, duration: int = 5000):
        """显示通知"""
        try:
            notification = self.create_notification_item(error_info)

            # 添加到布局
            self.layout.insertWidget(self.layout.count() - 1, notification)
            self.active_notifications.append(notification)

            # 动画显示
            self.animate_notification_in(notification)

            # 自动隐藏
            if duration > 0:
                QTimer.singleShot(duration, lambda: self.hide_notification(notification))

        except Exception as e:
            logger.error(f"显示错误通知失败: {e}")

    def create_notification_item(self, error_info: ErrorInfo) -> QWidget:
        """创建通知项"""
        item = QFrame()
        item.setFrameStyle(QFrame.Shape.StyledPanel)
        item.setStyleSheet(f"""
            QFrame {{
                background-color: {self.get_notification_color(error_info.severity)};
                border-radius: 6px;
                padding: 8px;
                margin: 2px;
            }}
        """)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(8, 6, 8, 6)

        # 图标
        icon_label = QLabel(self.get_severity_icon(error_info.severity))
        icon_label.setFixedSize(20, 20)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # 消息
        message_label = QLabel(error_info.simple_message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(message_label)

        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
            }
        """)
        close_btn.clicked.connect(lambda: self.hide_notification(item))
        layout.addWidget(close_btn)

        return item

    def get_notification_color(self, severity: ErrorSeverity) -> str:
        """获取通知颜色"""
        colors = {
            ErrorSeverity.INFO: "#2196f3",
            ErrorSeverity.WARNING: "#ff9800",
            ErrorSeverity.ERROR: "#f44336",
            ErrorSeverity.CRITICAL: "#e91e63",
            ErrorSeverity.FATAL: "#9c27b0"
        }
        return colors.get(severity, "#f44336")

    def get_severity_icon(self, severity: ErrorSeverity) -> str:
        """获取严重程度图标"""
        icons = {
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.CRITICAL: "🚨",
            ErrorSeverity.FATAL: "💀"
        }
        return icons.get(severity, "❌")

    def animate_notification_in(self, notification: QWidget):
        """动画显示通知"""
        try:
            # 初始状态
            notification.setMaximumHeight(0)

            # 创建动画
            animation = QPropertyAnimation(notification, b"maximumHeight")
            animation.setDuration(300)
            animation.setStartValue(0)
            animation.setEndValue(notification.sizeHint().height())
            animation.finished.connect(lambda: notification.setMaximumHeight(16777215))

            animation.start()

        except Exception as e:
            logger.error(f"通知动画失败: {e}")

    def hide_notification(self, notification: QWidget):
        """隐藏通知"""
        try:
            if notification in self.active_notifications:
                self.active_notifications.remove(notification)

            # 动画隐藏
            animation = QPropertyAnimation(notification, b"maximumHeight")
            animation.setDuration(200)
            animation.setStartValue(notification.height())
            animation.setEndValue(0)
            animation.finished.connect(notification.deleteLater)

            animation.start()

        except Exception as e:
            logger.error(f"隐藏通知失败: {e}")
            notification.deleteLater()


class ErrorSystemIntegrator:
    """错误系统集成器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.error_manager = LayeredErrorManager()
        self.notification_widget = None
        self.original_excepthook = None

        # 设置自动修复处理器
        self.setup_auto_fix_handlers()

        logger.info("错误系统集成器初始化完成")

    def integrate_error_system(self):
        """集成错误系统"""
        try:
            # 集成全局异常处理
            self.integrate_global_exception_handling()

            # 集成错误通知
            self.integrate_error_notifications()

            # 集成错误对话框
            self.integrate_error_dialogs()

            # 集成错误统计
            self.integrate_error_statistics()

            logger.info("错误系统集成完成")
            return True

        except Exception as e:
            logger.error(f"错误系统集成失败: {e}")
            return False

    def integrate_global_exception_handling(self):
        """集成全局异常处理"""
        try:
            # 保存原始异常钩子
            self.original_excepthook = sys.excepthook

            # 设置自定义异常钩子
            def custom_excepthook(exc_type, exc_value, exc_traceback):
                # 处理异常
                error_id = self.error_manager.handle_exception(
                    exc_type, exc_value, exc_traceback,
                    context=ErrorContext.UI_INTERACTION,
                    component="global"
                )

                # 显示错误对话框
                if error_id and error_id != "error_handling_failed":
                    dialog = self.error_manager.show_error_dialog(error_id, self.main_window)
                    if dialog:
                        dialog.exec()

                # 调用原始异常钩子
                if self.original_excepthook:
                    self.original_excepthook(exc_type, exc_value, exc_traceback)

            sys.excepthook = custom_excepthook
            logger.info("全局异常处理已集成")

        except Exception as e:
            logger.error(f"集成全局异常处理失败: {e}")

    def integrate_error_notifications(self):
        """集成错误通知"""
        try:
            # 创建通知组件
            self.notification_widget = ErrorNotificationWidget()

            # 添加到主窗口
            if hasattr(self.main_window, 'add_notification_widget'):
                self.main_window.add_notification_widget(self.notification_widget)
            else:
                # 添加到状态栏或其他位置
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().addPermanentWidget(self.notification_widget)

            # 连接错误发生信号
            self.error_manager.error_occurred.connect(self.show_error_notification)

            logger.info("错误通知已集成")

        except Exception as e:
            logger.error(f"集成错误通知失败: {e}")

    def integrate_error_dialogs(self):
        """集成错误对话框"""
        try:
            # 连接错误发生信号到对话框显示
            self.error_manager.error_occurred.connect(self.handle_error_occurred)

            logger.info("错误对话框已集成")

        except Exception as e:
            logger.error(f"集成错误对话框失败: {e}")

    def integrate_error_statistics(self):
        """集成错误统计"""
        try:
            # 这里可以添加错误统计面板到主窗口
            # 或者定期生成错误报告

            logger.info("错误统计已集成")

        except Exception as e:
            logger.error(f"集成错误统计失败: {e}")

    def setup_auto_fix_handlers(self):
        """设置自动修复处理器"""
        try:
            # 依赖错误自动修复
            self.error_manager.register_auto_fix_handler(
                ErrorCategory.DEPENDENCY.value,
                self.auto_fix_dependency_error
            )

            # 配置错误自动修复
            self.error_manager.register_auto_fix_handler(
                ErrorCategory.CONFIGURATION.value,
                self.auto_fix_configuration_error
            )

            logger.info("自动修复处理器设置完成")

        except Exception as e:
            logger.error(f"设置自动修复处理器失败: {e}")

    def auto_fix_dependency_error(self, error_info: ErrorInfo) -> bool:
        """自动修复依赖错误"""
        try:
            # 这里可以实现自动安装缺失的依赖
            logger.info(f"尝试自动修复依赖错误: {error_info.error_id}")

            # 示例：自动安装google-generativeai
            if "google.generativeai" in error_info.technical_details:
                import subprocess
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "google-generativeai"
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    logger.info("依赖安装成功")
                    return True
                else:
                    logger.error(f"依赖安装失败: {result.stderr}")
                    return False

            return False

        except Exception as e:
            logger.error(f"自动修复依赖错误失败: {e}")
            return False

    def auto_fix_configuration_error(self, error_info: ErrorInfo) -> bool:
        """自动修复配置错误"""
        try:
            logger.info(f"尝试自动修复配置错误: {error_info.error_id}")

            # 这里可以实现配置自动修复逻辑
            # 例如重置配置文件、修复API密钥格式等

            return False

        except Exception as e:
            logger.error(f"自动修复配置错误失败: {e}")
            return False

    def show_error_notification(self, error_info: ErrorInfo):
        """显示错误通知"""
        try:
            if self.notification_widget:
                # 只对严重错误显示通知
                if error_info.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL, ErrorSeverity.FATAL]:
                    self.notification_widget.show_notification(error_info)

        except Exception as e:
            logger.error(f"显示错误通知失败: {e}")

    def handle_error_occurred(self, error_info: ErrorInfo):
        """处理错误发生事件"""
        try:
            # 对于严重错误，自动显示对话框
            if error_info.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.FATAL]:
                dialog = self.error_manager.show_error_dialog(error_info.error_id, self.main_window)
                if dialog:
                    dialog.exec()

        except Exception as e:
            logger.error(f"处理错误发生事件失败: {e}")

    def report_error(self, error_type: str, context: ErrorContext,
                    technical_details: str = "", **kwargs) -> str:
        """报告错误的便捷方法"""
        try:
            error_info = self.error_manager.template_manager.create_error_info(
                error_type, context, technical_details, **kwargs
            )

            if error_info:
                return self.error_manager.report_error(error_info)
            else:
                logger.warning(f"未找到错误模板: {error_type}")
                return ""

        except Exception as e:
            logger.error(f"报告错误失败: {e}")
            return ""

    def get_error_manager(self) -> LayeredErrorManager:
        """获取错误管理器"""
        return self.error_manager

    def cleanup(self):
        """清理资源"""
        try:
            # 恢复原始异常钩子
            if self.original_excepthook:
                sys.excepthook = self.original_excepthook

            logger.info("错误系统资源已清理")

        except Exception as e:
            logger.error(f"清理错误系统资源失败: {e}")

    def export_error_report(self, file_path: str):
        """导出错误报告"""
        self.error_manager.export_error_report(file_path)

    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计"""
        return self.error_manager.get_error_statistics()
