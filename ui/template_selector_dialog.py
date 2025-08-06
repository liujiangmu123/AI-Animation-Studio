"""
AI Animation Studio - 模板选择器对话框
提供可视化的动画模板选择和自定义界面
"""

from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QComboBox, QFormLayout,
    QLineEdit, QScrollArea, QWidget, QGridLayout, QFrame, QSplitter,
    QTabWidget, QMessageBox, QSpinBox, QSlider, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from templates.animation_templates import AnimationTemplateLibrary
from core.enhanced_solution_manager import EnhancedAnimationSolution, SolutionCategory
from core.data_structures import TechStack
from core.logger import get_logger

logger = get_logger("template_selector_dialog")


class TemplateVariableEditor(QWidget):
    """模板变量编辑器"""
    
    variables_changed = pyqtSignal(dict)
    
    def __init__(self, template_variables: Dict[str, List[str]], parent=None):
        super().__init__(parent)
        
        self.template_variables = template_variables
        self.current_values = {}
        self.variable_widgets = {}
        
        self.setup_ui()
        self.setup_default_values()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("模板变量设置")
        title_label.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(300)
        
        # 变量编辑区域
        variables_widget = QWidget()
        variables_layout = QFormLayout(variables_widget)
        
        for var_name, var_options in self.template_variables.items():
            # 创建变量编辑控件
            if len(var_options) <= 5:
                # 使用下拉框
                combo = QComboBox()
                combo.addItems(var_options)
                combo.currentTextChanged.connect(self.on_variable_changed)
                
                self.variable_widgets[var_name] = combo
                variables_layout.addRow(f"{var_name}:", combo)
                
            else:
                # 使用文本输入框
                line_edit = QLineEdit()
                line_edit.setText(var_options[0] if var_options else "")
                line_edit.textChanged.connect(self.on_variable_changed)
                
                self.variable_widgets[var_name] = line_edit
                variables_layout.addRow(f"{var_name}:", line_edit)
        
        scroll_area.setWidget(variables_widget)
        layout.addWidget(scroll_area)
        
        # 预设按钮
        presets_layout = QHBoxLayout()
        
        preset_btn1 = QPushButton("预设1: 快速")
        preset_btn1.clicked.connect(lambda: self.apply_preset("fast"))
        presets_layout.addWidget(preset_btn1)
        
        preset_btn2 = QPushButton("预设2: 平滑")
        preset_btn2.clicked.connect(lambda: self.apply_preset("smooth"))
        presets_layout.addWidget(preset_btn2)
        
        preset_btn3 = QPushButton("预设3: 炫酷")
        preset_btn3.clicked.connect(lambda: self.apply_preset("cool"))
        presets_layout.addWidget(preset_btn3)
        
        layout.addLayout(presets_layout)
        
        # 重置按钮
        reset_btn = QPushButton("🔄 重置为默认")
        reset_btn.clicked.connect(self.reset_to_defaults)
        layout.addWidget(reset_btn)
    
    def setup_default_values(self):
        """设置默认值"""
        for var_name, var_options in self.template_variables.items():
            if var_options:
                self.current_values[var_name] = var_options[0]
    
    def on_variable_changed(self):
        """变量改变事件"""
        # 更新当前值
        for var_name, widget in self.variable_widgets.items():
            if isinstance(widget, QComboBox):
                self.current_values[var_name] = widget.currentText()
            elif isinstance(widget, QLineEdit):
                self.current_values[var_name] = widget.text()
        
        # 发送变量改变信号
        self.variables_changed.emit(self.current_values.copy())
    
    def apply_preset(self, preset_name: str):
        """应用预设"""
        presets = {
            "fast": {
                "duration": "0.3s",
                "easing": "ease-out"
            },
            "smooth": {
                "duration": "0.8s",
                "easing": "ease-in-out"
            },
            "cool": {
                "duration": "1.2s",
                "easing": "cubic-bezier(0.25, 0.46, 0.45, 0.94)"
            }
        }
        
        preset_values = presets.get(preset_name, {})
        
        for var_name, value in preset_values.items():
            if var_name in self.variable_widgets:
                widget = self.variable_widgets[var_name]
                
                if isinstance(widget, QComboBox):
                    index = widget.findText(value)
                    if index >= 0:
                        widget.setCurrentIndex(index)
                elif isinstance(widget, QLineEdit):
                    widget.setText(value)
        
        self.on_variable_changed()
    
    def reset_to_defaults(self):
        """重置为默认值"""
        for var_name, widget in self.variable_widgets.items():
            var_options = self.template_variables.get(var_name, [])
            
            if var_options:
                if isinstance(widget, QComboBox):
                    widget.setCurrentIndex(0)
                elif isinstance(widget, QLineEdit):
                    widget.setText(var_options[0])
        
        self.on_variable_changed()
    
    def get_current_values(self) -> Dict[str, str]:
        """获取当前变量值"""
        return self.current_values.copy()


class TemplatePreviewWidget(QWidget):
    """模板预览组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_template_data = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 预览标签页
        self.preview_tabs = QTabWidget()
        
        # HTML预览
        self.html_preview = QTextEdit()
        self.html_preview.setReadOnly(True)
        self.html_preview.setFont(QFont("Consolas", 10))
        self.preview_tabs.addTab(self.html_preview, "HTML")
        
        # CSS预览
        self.css_preview = QTextEdit()
        self.css_preview.setReadOnly(True)
        self.css_preview.setFont(QFont("Consolas", 10))
        self.preview_tabs.addTab(self.css_preview, "CSS")
        
        # JavaScript预览
        self.js_preview = QTextEdit()
        self.js_preview.setReadOnly(True)
        self.js_preview.setFont(QFont("Consolas", 10))
        self.preview_tabs.addTab(self.js_preview, "JavaScript")
        
        layout.addWidget(self.preview_tabs)
    
    def update_preview(self, template_data: Dict[str, Any]):
        """更新预览"""
        try:
            self.current_template_data = template_data
            
            # 更新各个标签页
            self.html_preview.setPlainText(template_data.get("html_code", ""))
            self.css_preview.setPlainText(template_data.get("css_code", ""))
            self.js_preview.setPlainText(template_data.get("js_code", ""))
            
        except Exception as e:
            logger.error(f"更新模板预览失败: {e}")


class TemplateSelectorDialog(QDialog):
    """模板选择器对话框"""
    
    template_selected = pyqtSignal(dict)  # 模板选中信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.template_library = AnimationTemplateLibrary()
        self.current_template = None
        self.current_variables = {}
        
        self.setup_ui()
        self.load_templates()
        
        logger.info("模板选择器对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("🎨 动画模板选择器")
        self.setMinimumSize(900, 600)
        
        layout = QVBoxLayout(self)
        
        # 主分割器
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：模板列表和过滤
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # 右侧：预览和编辑
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        main_splitter.setSizes([300, 600])
        layout.addWidget(main_splitter)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_btn = QPushButton("✅ 应用模板")
        self.apply_btn.clicked.connect(self.apply_template)
        self.apply_btn.setEnabled(False)
        button_layout.addWidget(self.apply_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_left_panel(self):
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 过滤器
        filter_group = QGroupBox("筛选模板")
        filter_layout = QVBoxLayout(filter_group)
        
        # 分类过滤
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("分类:"))
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("全部", None)
        for category in SolutionCategory:
            self.category_filter.addItem(category.value, category)
        self.category_filter.currentTextChanged.connect(self.filter_templates)
        category_layout.addWidget(self.category_filter)
        
        filter_layout.addLayout(category_layout)
        
        # 技术栈过滤
        tech_layout = QHBoxLayout()
        tech_layout.addWidget(QLabel("技术栈:"))
        
        self.tech_filter = QComboBox()
        self.tech_filter.addItem("全部", None)
        for tech in TechStack:
            self.tech_filter.addItem(tech.value, tech)
        self.tech_filter.currentTextChanged.connect(self.filter_templates)
        tech_layout.addWidget(self.tech_filter)
        
        filter_layout.addLayout(tech_layout)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入关键词...")
        self.search_edit.textChanged.connect(self.filter_templates)
        search_layout.addWidget(self.search_edit)
        
        filter_layout.addLayout(search_layout)
        
        layout.addWidget(filter_group)
        
        # 模板列表
        templates_group = QGroupBox("模板列表")
        templates_layout = QVBoxLayout(templates_group)
        
        self.templates_list = QListWidget()
        self.templates_list.itemClicked.connect(self.on_template_selected)
        templates_layout.addWidget(self.templates_list)
        
        layout.addWidget(templates_group)
        
        return panel
    
    def create_right_panel(self):
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 模板信息
        info_group = QGroupBox("模板信息")
        info_layout = QVBoxLayout(info_group)
        
        self.template_name_label = QLabel("请选择模板")
        self.template_name_label.setFont(QFont("", 12, QFont.Weight.Bold))
        info_layout.addWidget(self.template_name_label)
        
        self.template_desc_label = QLabel("")
        self.template_desc_label.setWordWrap(True)
        info_layout.addWidget(self.template_desc_label)
        
        layout.addWidget(info_group)
        
        # 变量编辑和预览
        content_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 变量编辑器
        self.variable_editor = None  # 将在选择模板时创建
        
        # 代码预览
        self.preview_widget = TemplatePreviewWidget()
        content_splitter.addWidget(self.preview_widget)
        
        content_splitter.setSizes([200, 400])
        layout.addWidget(content_splitter)
        
        return panel
    
    def load_templates(self):
        """加载模板"""
        try:
            self.templates_list.clear()
            
            # 获取所有模板
            all_template_names = self.template_library.get_all_template_names()
            
            for template_name in all_template_names:
                template_data = self.template_library.get_template_by_name(template_name)
                
                if template_data:
                    item = QListWidgetItem(template_data["name"])
                    item.setData(Qt.ItemDataRole.UserRole, template_name)
                    item.setToolTip(template_data["description"])
                    
                    # 根据技术栈设置颜色
                    tech_colors = {
                        TechStack.CSS_ANIMATION: QColor("#e3f2fd"),
                        TechStack.JAVASCRIPT: QColor("#fff3e0"),
                        TechStack.GSAP: QColor("#f3e5f5"),
                        TechStack.THREE_JS: QColor("#e8f5e8"),
                        TechStack.SVG_ANIMATION: QColor("#fce4ec")
                    }
                    
                    color = tech_colors.get(template_data["tech_stack"], QColor("#f5f5f5"))
                    item.setBackground(color)
                    
                    self.templates_list.addItem(item)
            
            logger.info(f"加载了 {len(all_template_names)} 个模板")
            
        except Exception as e:
            logger.error(f"加载模板失败: {e}")
    
    def filter_templates(self):
        """过滤模板"""
        try:
            # 获取过滤条件
            selected_category = self.category_filter.currentData()
            selected_tech = self.tech_filter.currentData()
            search_query = self.search_edit.text().lower()
            
            # 过滤模板
            for i in range(self.templates_list.count()):
                item = self.templates_list.item(i)
                template_name = item.data(Qt.ItemDataRole.UserRole)
                template_data = self.template_library.get_template_by_name(template_name)
                
                # 应用过滤条件
                show_item = True
                
                # 分类过滤
                if selected_category and template_data["category"] != selected_category:
                    show_item = False
                
                # 技术栈过滤
                if selected_tech and template_data["tech_stack"] != selected_tech:
                    show_item = False
                
                # 搜索过滤
                if search_query:
                    if (search_query not in template_data["name"].lower() and
                        search_query not in template_data["description"].lower()):
                        show_item = False
                
                item.setHidden(not show_item)
            
        except Exception as e:
            logger.error(f"过滤模板失败: {e}")
    
    def on_template_selected(self, item: QListWidgetItem):
        """模板选中事件"""
        try:
            template_name = item.data(Qt.ItemDataRole.UserRole)
            template_data = self.template_library.get_template_by_name(template_name)
            
            if not template_data:
                return
            
            self.current_template = template_name
            
            # 更新模板信息
            self.template_name_label.setText(template_data["name"])
            self.template_desc_label.setText(template_data["description"])
            
            # 创建变量编辑器
            template_variables = self.template_library.get_template_variables(template_name)
            
            if template_variables:
                # 移除旧的变量编辑器
                if self.variable_editor:
                    self.variable_editor.setParent(None)
                
                # 创建新的变量编辑器
                self.variable_editor = TemplateVariableEditor(template_variables)
                self.variable_editor.variables_changed.connect(self.on_variables_changed)
                
                # 添加到布局
                content_splitter = self.preview_widget.parent()
                content_splitter.insertWidget(0, self.variable_editor)
                content_splitter.setSizes([200, 400])
            
            # 生成初始预览
            self.update_preview()
            
            # 启用应用按钮
            self.apply_btn.setEnabled(True)
            
            logger.info(f"选中模板: {template_data['name']}")
            
        except Exception as e:
            logger.error(f"处理模板选中失败: {e}")
    
    def on_variables_changed(self, variables: Dict[str, str]):
        """变量改变事件"""
        self.current_variables = variables
        self.update_preview()
    
    def update_preview(self):
        """更新预览"""
        try:
            if not self.current_template:
                return
            
            # 生成模板代码
            template_data = self.template_library.generate_solution_from_template(
                self.current_template, self.current_variables
            )
            
            if template_data:
                self.preview_widget.update_preview(template_data)
            
        except Exception as e:
            logger.error(f"更新预览失败: {e}")
    
    def apply_template(self):
        """应用模板"""
        try:
            if not self.current_template:
                QMessageBox.warning(self, "警告", "请先选择一个模板")
                return
            
            # 生成最终的模板数据
            template_data = self.template_library.generate_solution_from_template(
                self.current_template, self.current_variables
            )
            
            if template_data:
                # 发送模板选中信号
                self.template_selected.emit(template_data)
                
                # 关闭对话框
                self.accept()
                
                logger.info(f"应用模板: {template_data['name']}")
            else:
                QMessageBox.warning(self, "错误", "生成模板失败")
            
        except Exception as e:
            logger.error(f"应用模板失败: {e}")
            QMessageBox.warning(self, "错误", "应用模板失败")


class QuickTemplateSelector(QWidget):
    """快速模板选择器"""
    
    template_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.template_library = AnimationTemplateLibrary()
        
        self.setup_ui()
        self.load_quick_templates()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("🚀 快速模板")
        title_label.setFont(QFont("", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 模板网格
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        templates_widget = QWidget()
        self.templates_grid = QGridLayout(templates_widget)
        
        scroll_area.setWidget(templates_widget)
        layout.addWidget(scroll_area)
        
        # 更多模板按钮
        more_btn = QPushButton("📚 更多模板...")
        more_btn.clicked.connect(self.show_full_selector)
        layout.addWidget(more_btn)
    
    def load_quick_templates(self):
        """加载快速模板"""
        try:
            # 选择一些常用模板
            quick_template_names = [
                "fade_in_up", "slide_in_left", "zoom_in",
                "hover_lift", "button_ripple", "floating_particles"
            ]
            
            row, col = 0, 0
            max_cols = 2
            
            for template_name in quick_template_names:
                template_data = self.template_library.get_template_by_name(template_name)
                
                if template_data:
                    # 创建模板卡片
                    card = self.create_template_card(template_name, template_data)
                    self.templates_grid.addWidget(card, row, col)
                    
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
            
        except Exception as e:
            logger.error(f"加载快速模板失败: {e}")
    
    def create_template_card(self, template_name: str, template_data: Dict[str, Any]):
        """创建模板卡片"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setMaximumWidth(200)
        card.setMinimumHeight(120)
        card.setStyleSheet("QFrame:hover { background-color: #f0f0f0; }")
        
        layout = QVBoxLayout(card)
        
        # 模板名称
        name_label = QLabel(template_data["name"])
        name_label.setFont(QFont("", 10, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # 模板描述
        desc_label = QLabel(template_data["description"])
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("color: #666; font-size: 9px;")
        layout.addWidget(desc_label)
        
        # 技术栈标签
        tech_label = QLabel(template_data["tech_stack"].value)
        tech_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tech_label.setStyleSheet("background: #e3f2fd; padding: 2px 6px; border-radius: 3px; font-size: 8px;")
        layout.addWidget(tech_label)
        
        # 应用按钮
        apply_btn = QPushButton("应用")
        apply_btn.clicked.connect(lambda: self.apply_quick_template(template_name))
        layout.addWidget(apply_btn)
        
        return card
    
    def apply_quick_template(self, template_name: str):
        """应用快速模板"""
        try:
            # 使用默认变量生成模板
            template_data = self.template_library.generate_solution_from_template(template_name)
            
            if template_data:
                self.template_selected.emit(template_data)
                logger.info(f"应用快速模板: {template_data['name']}")
            
        except Exception as e:
            logger.error(f"应用快速模板失败: {e}")
    
    def show_full_selector(self):
        """显示完整的模板选择器"""
        try:
            dialog = TemplateSelectorDialog(self)
            dialog.template_selected.connect(self.template_selected.emit)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"显示完整模板选择器失败: {e}")


def show_template_selector(parent=None) -> Optional[Dict[str, Any]]:
    """显示模板选择器并返回选中的模板"""
    try:
        dialog = TemplateSelectorDialog(parent)
        
        selected_template = None
        
        def on_template_selected(template_data):
            nonlocal selected_template
            selected_template = template_data
        
        dialog.template_selected.connect(on_template_selected)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return selected_template
        
        return None
        
    except Exception as e:
        logger.error(f"显示模板选择器失败: {e}")
        return None
