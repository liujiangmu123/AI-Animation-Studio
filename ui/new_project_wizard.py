"""
AI Animation Studio - 新建项目向导
提供项目创建的向导界面，包括配置选项、模板选择等
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox,
    QTabWidget, QWidget, QScrollArea, QTextEdit, QSlider, QProgressBar,
    QListWidget, QListWidgetItem, QFrame, QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QIcon

from core.logger import get_logger
from core.template_manager import TemplateManager
from core.data_structures import Project

logger = get_logger("new_project_wizard")


class ProjectConfigWidget(QWidget):
    """项目配置组件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QGridLayout(basic_group)
        
        # 项目名称
        basic_layout.addWidget(QLabel("项目名称:"), 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入项目名称")
        basic_layout.addWidget(self.name_edit, 0, 1)
        
        # 项目描述
        basic_layout.addWidget(QLabel("项目描述:"), 1, 0)
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("输入项目描述（可选）")
        basic_layout.addWidget(self.description_edit, 1, 1)
        
        layout.addWidget(basic_group)
        
        # 动画配置组
        animation_group = QGroupBox("动画配置")
        animation_layout = QGridLayout(animation_group)
        
        # 持续时间
        animation_layout.addWidget(QLabel("持续时间(秒):"), 0, 0)
        self.duration_spinbox = QDoubleSpinBox()
        self.duration_spinbox.setRange(1.0, 300.0)
        self.duration_spinbox.setValue(30.0)
        self.duration_spinbox.setSuffix(" 秒")
        animation_layout.addWidget(self.duration_spinbox, 0, 1)
        
        # 帧率
        animation_layout.addWidget(QLabel("帧率(FPS):"), 1, 0)
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(15, 120)
        self.fps_spinbox.setValue(30)
        self.fps_spinbox.setSuffix(" FPS")
        animation_layout.addWidget(self.fps_spinbox, 1, 1)
        
        # 分辨率
        animation_layout.addWidget(QLabel("分辨率:"), 2, 0)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "1920x1080 (Full HD)",
            "1280x720 (HD)",
            "3840x2160 (4K)",
            "1366x768",
            "自定义"
        ])
        animation_layout.addWidget(self.resolution_combo, 2, 1)
        
        layout.addWidget(animation_group)
        
        # 高级选项组
        advanced_group = QGroupBox("高级选项")
        advanced_layout = QGridLayout(advanced_group)
        
        # 自动保存
        self.auto_save_checkbox = QCheckBox("启用自动保存")
        self.auto_save_checkbox.setChecked(True)
        advanced_layout.addWidget(self.auto_save_checkbox, 0, 0)
        
        # 网格显示
        self.show_grid_checkbox = QCheckBox("显示网格")
        self.show_grid_checkbox.setChecked(True)
        advanced_layout.addWidget(self.show_grid_checkbox, 0, 1)
        
        # 性能模式
        advanced_layout.addWidget(QLabel("性能模式:"), 1, 0)
        self.performance_combo = QComboBox()
        self.performance_combo.addItems(["平衡", "高质量", "高性能"])
        advanced_layout.addWidget(self.performance_combo, 1, 1)
        
        layout.addWidget(advanced_group)
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置信息"""
        resolution_text = self.resolution_combo.currentText()
        if "1920x1080" in resolution_text:
            resolution = {"width": 1920, "height": 1080}
        elif "1280x720" in resolution_text:
            resolution = {"width": 1280, "height": 720}
        elif "3840x2160" in resolution_text:
            resolution = {"width": 3840, "height": 2160}
        elif "1366x768" in resolution_text:
            resolution = {"width": 1366, "height": 768}
        else:
            resolution = {"width": 1920, "height": 1080}  # 默认
        
        return {
            "name": self.name_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "duration": self.duration_spinbox.value(),
            "fps": self.fps_spinbox.value(),
            "resolution": resolution,
            "auto_save": self.auto_save_checkbox.isChecked(),
            "show_grid": self.show_grid_checkbox.isChecked(),
            "performance_mode": self.performance_combo.currentText()
        }
    
    def set_config(self, config: Dict[str, Any]):
        """设置配置信息"""
        if "name" in config:
            self.name_edit.setText(config["name"])
        if "description" in config:
            self.description_edit.setPlainText(config["description"])
        if "duration" in config:
            self.duration_spinbox.setValue(config["duration"])
        if "fps" in config:
            self.fps_spinbox.setValue(config["fps"])
        if "auto_save" in config:
            self.auto_save_checkbox.setChecked(config["auto_save"])
        if "show_grid" in config:
            self.show_grid_checkbox.setChecked(config["show_grid"])


class TemplateSelectionWidget(QWidget):
    """模板选择组件"""
    
    template_selected = pyqtSignal(str)  # template_id
    
    def __init__(self):
        super().__init__()
        self.template_manager = TemplateManager()
        self.selected_template_id = None
        self.setup_ui()
        self.load_templates()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 模板列表
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self.on_template_selected)
        layout.addWidget(self.template_list)
        
        # 模板信息
        info_group = QGroupBox("模板信息")
        info_layout = QVBoxLayout(info_group)
        
        self.template_name_label = QLabel("选择一个模板")
        self.template_name_label.setFont(QFont("", 12, QFont.Weight.Bold))
        info_layout.addWidget(self.template_name_label)
        
        self.template_description_label = QLabel("")
        self.template_description_label.setWordWrap(True)
        info_layout.addWidget(self.template_description_label)
        
        layout.addWidget(info_group)
    
    def load_templates(self):
        """加载模板列表"""
        try:
            templates = self.template_manager.get_all_templates()
            
            # 添加"无模板"选项
            no_template_item = QListWidgetItem("无模板（空白项目）")
            no_template_item.setData(Qt.ItemDataRole.UserRole, None)
            self.template_list.addItem(no_template_item)
            
            # 添加模板
            for template in templates:
                item = QListWidgetItem(template.name)
                item.setData(Qt.ItemDataRole.UserRole, template.id)
                item.setToolTip(template.description)
                self.template_list.addItem(item)
                
        except Exception as e:
            logger.error(f"加载模板失败: {e}")
    
    def on_template_selected(self, item: QListWidgetItem):
        """模板选择事件"""
        template_id = item.data(Qt.ItemDataRole.UserRole)
        self.selected_template_id = template_id
        
        if template_id is None:
            self.template_name_label.setText("空白项目")
            self.template_description_label.setText("创建一个空白的动画项目")
        else:
            template = self.template_manager.get_template(template_id)
            if template:
                self.template_name_label.setText(template.name)
                self.template_description_label.setText(template.description)
        
        self.template_selected.emit(template_id or "")
    
    def get_selected_template_id(self) -> Optional[str]:
        """获取选择的模板ID"""
        return self.selected_template_id


class NewProjectWizard(QDialog):
    """新建项目向导"""
    
    project_created = pyqtSignal(dict)  # 项目配置信息
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建项目向导")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        
        self.setup_ui()
        self.setup_connections()
        
        logger.info("新建项目向导初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("创建新的动画项目")
        title_label.setFont(QFont("", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 项目配置选项卡
        self.config_widget = ProjectConfigWidget()
        self.tab_widget.addTab(self.config_widget, "项目配置")
        
        # 模板选择选项卡
        self.template_widget = TemplateSelectionWidget()
        self.tab_widget.addTab(self.template_widget, "模板选择")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        self.create_button = QPushButton("创建项目")
        self.create_button.setDefault(True)
        self.create_button.clicked.connect(self.create_project)
        button_layout.addWidget(self.create_button)
        
        layout.addLayout(button_layout)
    
    def setup_connections(self):
        """设置信号连接"""
        self.template_widget.template_selected.connect(self.on_template_selected)
    
    def on_template_selected(self, template_id: str):
        """模板选择事件"""
        if template_id:
            # 根据模板设置默认配置
            template = self.template_widget.template_manager.get_template(template_id)
            if template and hasattr(template, 'default_config'):
                self.config_widget.set_config(template.default_config)
    
    def create_project(self):
        """创建项目"""
        try:
            # 获取配置
            config = self.config_widget.get_config()
            
            # 验证配置
            if not config["name"]:
                QMessageBox.warning(self, "警告", "请输入项目名称")
                return
            
            # 添加模板信息
            config["template_id"] = self.template_widget.get_selected_template_id()
            
            # 发射信号
            self.project_created.emit(config)
            self.accept()
            
        except Exception as e:
            logger.error(f"创建项目失败: {e}")
            QMessageBox.critical(self, "错误", f"创建项目失败:\n{str(e)}")
