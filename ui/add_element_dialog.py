"""
AI Animation Studio - 添加元素对话框
提供完整的元素添加功能，包括AI智能推荐
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QComboBox, QTextEdit, QSpinBox,
                             QDoubleSpinBox, QCheckBox, QPushButton, QGroupBox,
                             QListWidget, QListWidgetItem, QSplitter, QTabWidget,
                             QWidget, QColorDialog, QFileDialog, QMessageBox,
                             QProgressBar, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QColor, QFont

from core.data_structures import Element, ElementType, Point, ElementStyle, Transform
from core.logger import get_logger
from ai.gemini_generator import GeminiGenerator

logger = get_logger("add_element_dialog")


class AIRecommendationWorker(QThread):
    """AI推荐工作线程"""
    
    recommendations_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, description: str, element_type: str):
        super().__init__()
        self.description = description
        self.element_type = element_type
        self.gemini_generator = GeminiGenerator()
    
    def run(self):
        """运行AI推荐"""
        try:
            if not self.gemini_generator.is_available():
                self.error_occurred.emit("AI服务不可用")
                return
            
            # 构建推荐请求
            prompt = f"""
            用户想要添加一个{self.element_type}元素，描述：{self.description}
            
            请为这个元素推荐合适的属性，包括：
            1. 元素名称
            2. 内容建议
            3. 位置建议（x, y坐标）
            4. 样式建议（颜色、字体、大小等）
            5. 动画建议
            
            请以JSON格式返回推荐结果。
            """
            
            response = self.gemini_generator.generate_animation_solution(
                prompt, {"element_type": self.element_type}
            )
            
            if response and response.solutions:
                recommendations = []
                for solution in response.solutions:
                    recommendations.append({
                        "name": solution.name,
                        "description": solution.description,
                        "properties": solution.custom_data
                    })
                
                self.recommendations_ready.emit(recommendations)
            else:
                self.error_occurred.emit("未能生成推荐")
                
        except Exception as e:
            logger.error(f"AI推荐失败: {e}")
            self.error_occurred.emit(f"AI推荐失败: {str(e)}")


class ElementPreviewWidget(QWidget):
    """元素预览组件"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(300, 200)
        self.setStyleSheet("""
            ElementPreviewWidget {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout()
        self.preview_label = QLabel("元素预览")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(self.preview_label)
        self.setLayout(layout)
    
    def update_preview(self, element: Element):
        """更新预览"""
        try:
            preview_text = f"""
            名称: {element.name}
            类型: {element.element_type.value}
            内容: {element.content[:50]}...
            位置: ({element.position.x}, {element.position.y})
            """
            self.preview_label.setText(preview_text)
        except Exception as e:
            logger.error(f"更新预览失败: {e}")
            self.preview_label.setText("预览更新失败")


class AddElementDialog(QDialog):
    """添加元素对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加元素")
        self.setModal(True)
        self.resize(800, 600)
        
        self.element = None
        self.ai_worker = None
        
        self.setup_ui()
        self.connect_signals()
        
        # 默认值
        self.update_preview()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 基本属性选项卡
        self.basic_tab = self.create_basic_tab()
        self.tab_widget.addTab(self.basic_tab, "基本属性")
        
        # 样式选项卡
        self.style_tab = self.create_style_tab()
        self.tab_widget.addTab(self.style_tab, "样式设置")
        
        # AI推荐选项卡
        self.ai_tab = self.create_ai_tab()
        self.tab_widget.addTab(self.ai_tab, "AI推荐")
        
        layout.addWidget(self.tab_widget)
        
        # 预览区域
        self.preview_widget = ElementPreviewWidget()
        layout.addWidget(self.preview_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self.apply_changes)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_basic_tab(self) -> QWidget:
        """创建基本属性选项卡"""
        widget = QWidget()
        layout = QFormLayout()
        
        # 元素名称
        self.name_edit = QLineEdit("新元素")
        layout.addRow("名称:", self.name_edit)
        
        # 元素类型
        self.type_combo = QComboBox()
        for element_type in ElementType:
            self.type_combo.addItem(element_type.value.title(), element_type)
        layout.addRow("类型:", self.type_combo)
        
        # 内容
        self.content_edit = QTextEdit()
        self.content_edit.setMaximumHeight(100)
        self.content_edit.setPlainText("元素内容")
        layout.addRow("内容:", self.content_edit)
        
        # 位置
        position_layout = QHBoxLayout()
        self.x_spin = QDoubleSpinBox()
        self.x_spin.setRange(-9999, 9999)
        self.x_spin.setValue(100)
        self.y_spin = QDoubleSpinBox()
        self.y_spin.setRange(-9999, 9999)
        self.y_spin.setValue(100)
        position_layout.addWidget(QLabel("X:"))
        position_layout.addWidget(self.x_spin)
        position_layout.addWidget(QLabel("Y:"))
        position_layout.addWidget(self.y_spin)
        layout.addRow("位置:", position_layout)
        
        # 可见性和锁定
        options_layout = QHBoxLayout()
        self.visible_check = QCheckBox("可见")
        self.visible_check.setChecked(True)
        self.locked_check = QCheckBox("锁定")
        options_layout.addWidget(self.visible_check)
        options_layout.addWidget(self.locked_check)
        layout.addRow("选项:", options_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_style_tab(self) -> QWidget:
        """创建样式选项卡"""
        widget = QWidget()
        layout = QFormLayout()
        
        # 尺寸
        size_layout = QHBoxLayout()
        self.width_edit = QLineEdit("auto")
        self.height_edit = QLineEdit("auto")
        size_layout.addWidget(QLabel("宽:"))
        size_layout.addWidget(self.width_edit)
        size_layout.addWidget(QLabel("高:"))
        size_layout.addWidget(self.height_edit)
        layout.addRow("尺寸:", size_layout)
        
        # 颜色
        color_layout = QHBoxLayout()
        self.bg_color_button = QPushButton("背景色")
        self.bg_color_button.clicked.connect(self.choose_bg_color)
        self.text_color_button = QPushButton("文字色")
        self.text_color_button.clicked.connect(self.choose_text_color)
        color_layout.addWidget(self.bg_color_button)
        color_layout.addWidget(self.text_color_button)
        layout.addRow("颜色:", color_layout)
        
        # 透明度
        self.opacity_spin = QDoubleSpinBox()
        self.opacity_spin.setRange(0.0, 1.0)
        self.opacity_spin.setSingleStep(0.1)
        self.opacity_spin.setValue(1.0)
        layout.addRow("透明度:", self.opacity_spin)
        
        # 字体
        font_layout = QHBoxLayout()
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["Arial", "微软雅黑", "宋体", "黑体", "楷体"])
        self.font_size_edit = QLineEdit("16px")
        font_layout.addWidget(self.font_family_combo)
        font_layout.addWidget(self.font_size_edit)
        layout.addRow("字体:", font_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_ai_tab(self) -> QWidget:
        """创建AI推荐选项卡"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 描述输入
        desc_group = QGroupBox("描述您想要的元素")
        desc_layout = QVBoxLayout()
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("例如：一个红色的标题文字，位于屏幕中央，字体较大...")
        self.description_edit.setMaximumHeight(80)
        desc_layout.addWidget(self.description_edit)
        
        self.get_recommendations_button = QPushButton("获取AI推荐")
        self.get_recommendations_button.clicked.connect(self.get_ai_recommendations)
        desc_layout.addWidget(self.get_recommendations_button)
        
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # 推荐结果
        rec_group = QGroupBox("AI推荐结果")
        rec_layout = QVBoxLayout()
        
        self.recommendations_list = QListWidget()
        self.recommendations_list.itemClicked.connect(self.apply_recommendation)
        rec_layout.addWidget(self.recommendations_list)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        rec_layout.addWidget(self.progress_bar)
        
        rec_group.setLayout(rec_layout)
        layout.addWidget(rec_group)
        
        widget.setLayout(layout)
        return widget

    def connect_signals(self):
        """连接信号"""
        # 基本属性变化时更新预览
        self.name_edit.textChanged.connect(self.update_preview)
        self.type_combo.currentTextChanged.connect(self.update_preview)
        self.content_edit.textChanged.connect(self.update_preview)
        self.x_spin.valueChanged.connect(self.update_preview)
        self.y_spin.valueChanged.connect(self.update_preview)

        # 样式变化时更新预览
        self.opacity_spin.valueChanged.connect(self.update_preview)

    def choose_bg_color(self):
        """选择背景色"""
        color = QColorDialog.getColor(QColor("white"), self)
        if color.isValid():
            self.bg_color_button.setStyleSheet(f"background-color: {color.name()};")
            self.update_preview()

    def choose_text_color(self):
        """选择文字色"""
        color = QColorDialog.getColor(QColor("black"), self)
        if color.isValid():
            self.text_color_button.setStyleSheet(f"background-color: {color.name()};")
            self.update_preview()

    def get_ai_recommendations(self):
        """获取AI推荐"""
        description = self.description_edit.toPlainText().strip()
        if not description:
            QMessageBox.warning(self, "警告", "请输入元素描述")
            return

        element_type = self.type_combo.currentData().value

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 无限进度条
        self.get_recommendations_button.setEnabled(False)

        # 启动AI工作线程
        self.ai_worker = AIRecommendationWorker(description, element_type)
        self.ai_worker.recommendations_ready.connect(self.on_recommendations_ready)
        self.ai_worker.error_occurred.connect(self.on_ai_error)
        self.ai_worker.start()

    def on_recommendations_ready(self, recommendations):
        """AI推荐就绪"""
        self.progress_bar.setVisible(False)
        self.get_recommendations_button.setEnabled(True)

        self.recommendations_list.clear()

        for i, rec in enumerate(recommendations):
            item = QListWidgetItem(f"{i+1}. {rec['name']}")
            item.setData(Qt.ItemDataRole.UserRole, rec)
            item.setToolTip(rec['description'])
            self.recommendations_list.addItem(item)

        if recommendations:
            QMessageBox.information(self, "成功", f"获得 {len(recommendations)} 个推荐")
        else:
            QMessageBox.information(self, "提示", "未获得推荐结果")

    def on_ai_error(self, error_msg):
        """AI推荐错误"""
        self.progress_bar.setVisible(False)
        self.get_recommendations_button.setEnabled(True)
        QMessageBox.warning(self, "错误", f"AI推荐失败: {error_msg}")

    def apply_recommendation(self, item):
        """应用推荐"""
        rec_data = item.data(Qt.ItemDataRole.UserRole)
        if not rec_data:
            return

        try:
            properties = rec_data.get('properties', {})

            # 应用基本属性
            if 'name' in properties:
                self.name_edit.setText(properties['name'])

            if 'content' in properties:
                self.content_edit.setPlainText(properties['content'])

            if 'position' in properties:
                pos = properties['position']
                if isinstance(pos, dict):
                    self.x_spin.setValue(pos.get('x', 100))
                    self.y_spin.setValue(pos.get('y', 100))

            # 应用样式属性
            if 'style' in properties:
                style = properties['style']
                if 'width' in style:
                    self.width_edit.setText(str(style['width']))
                if 'height' in style:
                    self.height_edit.setText(str(style['height']))
                if 'opacity' in style:
                    self.opacity_spin.setValue(float(style['opacity']))

            self.update_preview()
            QMessageBox.information(self, "成功", "已应用推荐设置")

        except Exception as e:
            logger.error(f"应用推荐失败: {e}")
            QMessageBox.warning(self, "错误", f"应用推荐失败: {str(e)}")

    def update_preview(self):
        """更新预览"""
        try:
            element = self.create_element()
            self.preview_widget.update_preview(element)
        except Exception as e:
            logger.error(f"更新预览失败: {e}")

    def create_element(self) -> Element:
        """根据当前设置创建元素"""
        # 基本属性
        name = self.name_edit.text() or "新元素"
        element_type = self.type_combo.currentData()
        content = self.content_edit.toPlainText()
        position = Point(self.x_spin.value(), self.y_spin.value())

        # 样式
        style = ElementStyle(
            width=self.width_edit.text() or "auto",
            height=self.height_edit.text() or "auto",
            opacity=self.opacity_spin.value(),
            font_family=self.font_family_combo.currentText(),
            font_size=self.font_size_edit.text() or "16px"
        )

        # 创建元素
        element = Element(
            name=name,
            element_type=element_type,
            content=content,
            position=position,
            style=style,
            visible=self.visible_check.isChecked(),
            locked=self.locked_check.isChecked()
        )

        return element

    def apply_changes(self):
        """应用更改"""
        try:
            self.element = self.create_element()
            QMessageBox.information(self, "成功", "设置已应用")
        except Exception as e:
            logger.error(f"应用更改失败: {e}")
            QMessageBox.warning(self, "错误", f"应用更改失败: {str(e)}")

    def accept(self):
        """确定"""
        try:
            self.element = self.create_element()
            super().accept()
        except Exception as e:
            logger.error(f"创建元素失败: {e}")
            QMessageBox.warning(self, "错误", f"创建元素失败: {str(e)}")

    def get_element(self) -> Element:
        """获取创建的元素"""
        return self.element

    def closeEvent(self, event):
        """关闭事件"""
        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.terminate()
            self.ai_worker.wait()
        event.accept()
