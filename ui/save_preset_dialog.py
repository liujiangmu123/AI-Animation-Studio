"""
AI Animation Studio - 保存预设对话框
提供保存当前属性为预设的功能
"""

from typing import Dict, List, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QCheckBox, QGroupBox, QListWidget,
    QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.data_structures import Element, ElementType
from core.property_presets import PropertyPresetManager
from core.logger import get_logger

logger = get_logger("save_preset_dialog")


class SavePresetDialog(QDialog):
    """保存预设对话框"""
    
    def __init__(self, parent=None, element: Element = None, preset_manager: PropertyPresetManager = None):
        super().__init__(parent)
        self.element = element
        self.preset_manager = preset_manager
        
        self.setWindowTitle("保存预设")
        self.setMinimumSize(500, 600)
        self.resize(600, 700)
        
        self.setup_ui()
        self.load_current_properties()
        
        logger.info("保存预设对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("保存属性预设")
        title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 基本信息组
        info_group = QGroupBox("预设信息")
        info_layout = QGridLayout(info_group)
        
        # 预设名称
        info_layout.addWidget(QLabel("预设名称:"), 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入预设名称...")
        info_layout.addWidget(self.name_edit, 0, 1)
        
        # 预设描述
        info_layout.addWidget(QLabel("预设描述:"), 1, 0)
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("输入预设描述...")
        info_layout.addWidget(self.description_edit, 1, 1)
        
        # 预设分类
        info_layout.addWidget(QLabel("预设分类:"), 2, 0)
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "基本属性", "样式属性", "变换属性", "动画属性", "自定义"
        ])
        info_layout.addWidget(self.category_combo, 2, 1)
        
        layout.addWidget(info_group)
        
        # 适用元素类型组
        element_types_group = QGroupBox("适用元素类型")
        element_types_layout = QVBoxLayout(element_types_group)
        
        self.element_type_checkboxes = {}
        element_types = [
            (ElementType.TEXT, "文本"),
            (ElementType.IMAGE, "图片"),
            (ElementType.SHAPE, "形状"),
            (ElementType.SVG, "SVG"),
            (ElementType.VIDEO, "视频"),
            (ElementType.AUDIO, "音频"),
            (ElementType.GROUP, "组")
        ]
        
        for element_type, display_name in element_types:
            checkbox = QCheckBox(display_name)
            # 默认选中当前元素类型
            if self.element and element_type == self.element.element_type:
                checkbox.setChecked(True)
            self.element_type_checkboxes[element_type] = checkbox
            element_types_layout.addWidget(checkbox)
        
        layout.addWidget(element_types_group)
        
        # 属性选择组
        properties_group = QGroupBox("包含属性")
        properties_layout = QVBoxLayout(properties_group)
        
        # 属性列表
        self.properties_list = QListWidget()
        self.properties_list.setMaximumHeight(200)
        properties_layout.addWidget(self.properties_list)
        
        # 全选/全不选按钮
        select_buttons_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("全选")
        select_all_btn.clicked.connect(self.select_all_properties)
        select_buttons_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("全不选")
        select_none_btn.clicked.connect(self.select_no_properties)
        select_buttons_layout.addWidget(select_none_btn)
        
        select_buttons_layout.addStretch()
        
        properties_layout.addLayout(select_buttons_layout)
        
        layout.addWidget(properties_group)
        
        # 预览组
        preview_group = QGroupBox("预设预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        # 更新预览按钮
        update_preview_btn = QPushButton("更新预览")
        update_preview_btn.clicked.connect(self.update_preview)
        preview_layout.addWidget(update_preview_btn)
        
        layout.addWidget(preview_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        button_layout.addStretch()
        
        self.save_button = QPushButton("保存预设")
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.save_preset)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
    
    def load_current_properties(self):
        """加载当前元素的属性"""
        if not self.element:
            return
        
        try:
            # 基本属性
            properties = [
                ("name", "名称", getattr(self.element, 'name', '')),
                ("content", "内容", getattr(self.element, 'content', '')),
                ("visible", "可见性", self.element.visible),
                ("locked", "锁定状态", self.element.locked),
            ]
            
            # 样式属性
            if hasattr(self.element, 'style') and self.element.style:
                style = self.element.style
                style_props = [
                    ("color", "颜色", getattr(style, 'color', '')),
                    ("background", "背景", getattr(style, 'background', '')),
                    ("font_size", "字体大小", getattr(style, 'font_size', '')),
                    ("font_weight", "字体粗细", getattr(style, 'font_weight', '')),
                    ("text_align", "文本对齐", getattr(style, 'text_align', '')),
                    ("border_radius", "圆角", getattr(style, 'border_radius', '')),
                    ("padding", "内边距", getattr(style, 'padding', '')),
                    ("margin", "外边距", getattr(style, 'margin', '')),
                    ("box_shadow", "盒阴影", getattr(style, 'box_shadow', '')),
                    ("text_shadow", "文字阴影", getattr(style, 'text_shadow', '')),
                ]
                properties.extend(style_props)
            
            # 变换属性
            if hasattr(self.element, 'transform') and self.element.transform:
                transform = self.element.transform
                transform_props = [
                    ("rotation", "旋转", getattr(transform, 'rotation', 0)),
                    ("scale_x", "X缩放", getattr(transform, 'scale_x', 1)),
                    ("scale_y", "Y缩放", getattr(transform, 'scale_y', 1)),
                ]
                properties.extend(transform_props)
            
            # 位置属性
            properties.extend([
                ("position_x", "X位置", self.element.position.x),
                ("position_y", "Y位置", self.element.position.y),
            ])
            
            # 添加到列表
            for prop_key, prop_name, prop_value in properties:
                if prop_value is not None and prop_value != '':
                    item = QListWidgetItem(f"{prop_name}: {prop_value}")
                    item.setCheckState(Qt.CheckState.Checked)
                    item.setData(Qt.ItemDataRole.UserRole, (prop_key, prop_value))
                    self.properties_list.addItem(item)
            
            # 生成默认预设名称
            element_type_name = {
                ElementType.TEXT: "文本",
                ElementType.IMAGE: "图片", 
                ElementType.SHAPE: "形状",
                ElementType.SVG: "SVG",
                ElementType.VIDEO: "视频",
                ElementType.AUDIO: "音频",
                ElementType.GROUP: "组"
            }.get(self.element.element_type, "元素")
            
            default_name = f"{element_type_name}预设_{len(self.preset_manager.get_all_presets()) + 1}"
            self.name_edit.setText(default_name)
            
        except Exception as e:
            logger.error(f"加载当前属性失败: {e}")
    
    def select_all_properties(self):
        """全选属性"""
        for i in range(self.properties_list.count()):
            item = self.properties_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)
    
    def select_no_properties(self):
        """全不选属性"""
        for i in range(self.properties_list.count()):
            item = self.properties_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
    
    def update_preview(self):
        """更新预览"""
        try:
            properties = self.get_selected_properties()
            
            preview_text = f"预设名称: {self.name_edit.text()}\n"
            preview_text += f"预设描述: {self.description_edit.toPlainText()}\n"
            preview_text += f"预设分类: {self.category_combo.currentText()}\n"
            
            # 适用元素类型
            selected_types = []
            for element_type, checkbox in self.element_type_checkboxes.items():
                if checkbox.isChecked():
                    type_name = {
                        ElementType.TEXT: "文本",
                        ElementType.IMAGE: "图片",
                        ElementType.SHAPE: "形状", 
                        ElementType.SVG: "SVG",
                        ElementType.VIDEO: "视频",
                        ElementType.AUDIO: "音频",
                        ElementType.GROUP: "组"
                    }.get(element_type, str(element_type))
                    selected_types.append(type_name)
            
            preview_text += f"适用类型: {', '.join(selected_types)}\n"
            preview_text += f"包含属性: {len(properties)} 个\n\n"
            
            # 属性详情
            preview_text += "属性详情:\n"
            for prop_key, prop_value in properties.items():
                preview_text += f"  {prop_key}: {prop_value}\n"
            
            self.preview_text.setPlainText(preview_text)
            
        except Exception as e:
            logger.error(f"更新预览失败: {e}")
    
    def get_selected_properties(self) -> Dict[str, Any]:
        """获取选中的属性"""
        properties = {}
        
        for i in range(self.properties_list.count()):
            item = self.properties_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                prop_key, prop_value = item.data(Qt.ItemDataRole.UserRole)
                properties[prop_key] = prop_value
        
        return properties
    
    def get_selected_element_types(self) -> List[ElementType]:
        """获取选中的元素类型"""
        selected_types = []
        
        for element_type, checkbox in self.element_type_checkboxes.items():
            if checkbox.isChecked():
                selected_types.append(element_type)
        
        return selected_types
    
    def save_preset(self):
        """保存预设"""
        try:
            # 验证输入
            name = self.name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "错误", "请输入预设名称")
                return
            
            description = self.description_edit.toPlainText().strip()
            category_map = {
                "基本属性": "basic",
                "样式属性": "style", 
                "变换属性": "transform",
                "动画属性": "animation",
                "自定义": "custom"
            }
            category = category_map.get(self.category_combo.currentText(), "custom")
            
            element_types = self.get_selected_element_types()
            if not element_types:
                QMessageBox.warning(self, "错误", "请至少选择一种适用的元素类型")
                return
            
            properties = self.get_selected_properties()
            if not properties:
                QMessageBox.warning(self, "错误", "请至少选择一个属性")
                return
            
            # 检查预设名称是否已存在
            if self.preset_manager.get_preset(name):
                reply = QMessageBox.question(
                    self, "预设已存在",
                    f"预设 '{name}' 已存在，是否覆盖？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # 创建预设
            success = self.preset_manager.create_preset(
                name, description, category, element_types, properties
            )
            
            if success:
                logger.info(f"预设保存成功: {name}")
                self.accept()
            else:
                QMessageBox.critical(self, "错误", "保存预设失败")
                
        except Exception as e:
            logger.error(f"保存预设失败: {e}")
            QMessageBox.critical(self, "错误", f"保存预设失败:\n{str(e)}")
