"""
AI Animation Studio - 模板选择对话框
提供项目模板的浏览、预览和选择功能
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QTextEdit, QComboBox, QLineEdit,
    QDialogButtonBox, QGroupBox, QSplitter, QMessageBox, QTabWidget,
    QListWidget, QListWidgetItem, QProgressBar, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer, QThread
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QMovie
from PyQt6.QtWebEngineWidgets import QWebEngineView

from core.template_manager import TemplateManager, ProjectTemplate
from core.logger import get_logger
from ui.template_preview_dialog import TemplatePreviewDialog

logger = get_logger("template_dialog")


class TemplatePreviewWorker(QThread):
    """模板预览加载工作线程"""

    preview_ready = pyqtSignal(str, str)  # template_id, preview_html
    error_occurred = pyqtSignal(str, str)  # template_id, error_message

    def __init__(self, template: 'ProjectTemplate'):
        super().__init__()
        self.template = template

    def run(self):
        """加载模板预览"""
        try:
            # 读取模板HTML文件
            if self.template.html_file and self.template.html_file.exists():
                with open(self.template.html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                # 添加预览控制脚本
                enhanced_html = self.add_preview_controls(html_content)
                self.preview_ready.emit(self.template.id, enhanced_html)
            else:
                self.error_occurred.emit(self.template.id, "模板文件不存在")

        except Exception as e:
            logger.error(f"加载模板预览失败: {e}")
            self.error_occurred.emit(self.template.id, str(e))

    def add_preview_controls(self, html_content: str) -> str:
        """为HTML添加预览控制功能"""
        control_script = """
        <script>
        // 预览控制功能
        let isPlaying = false;
        let currentTime = 0;
        let totalDuration = 5.0; // 默认5秒

        function playPreview() {
            isPlaying = true;
            if (typeof renderAtTime === 'function') {
                const interval = setInterval(() => {
                    if (!isPlaying || currentTime >= totalDuration) {
                        clearInterval(interval);
                        isPlaying = false;
                        return;
                    }
                    renderAtTime(currentTime);
                    currentTime += 0.1;
                }, 100);
            }
        }

        function pausePreview() {
            isPlaying = false;
        }

        function resetPreview() {
            isPlaying = false;
            currentTime = 0;
            if (typeof renderAtTime === 'function') {
                renderAtTime(0);
            }
        }

        function seekTo(time) {
            currentTime = time;
            if (typeof renderAtTime === 'function') {
                renderAtTime(currentTime);
            }
        }

        // 暴露给外部调用
        window.previewControls = {
            play: playPreview,
            pause: pausePreview,
            reset: resetPreview,
            seek: seekTo,
            isPlaying: () => isPlaying,
            getCurrentTime: () => currentTime,
            getDuration: () => totalDuration
        };
        </script>
        """

        # 在</body>前插入控制脚本
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', control_script + '</body>')
        else:
            html_content += control_script

        return html_content


class EnhancedTemplatePreview(QWidget):
    """增强的模板预览组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_template = None
        self.preview_worker = None
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)

        # 创建选项卡
        self.tab_widget = QTabWidget()

        # 实时预览选项卡
        self.live_preview_tab = self.create_live_preview_tab()
        self.tab_widget.addTab(self.live_preview_tab, "实时预览")

        # 静态预览选项卡
        self.static_preview_tab = self.create_static_preview_tab()
        self.tab_widget.addTab(self.static_preview_tab, "静态预览")

        # 详细信息选项卡
        self.details_tab = self.create_details_tab()
        self.tab_widget.addTab(self.details_tab, "详细信息")

        layout.addWidget(self.tab_widget)

        # 控制面板
        self.control_panel = self.create_control_panel()
        layout.addWidget(self.control_panel)

    def create_live_preview_tab(self) -> QWidget:
        """创建实时预览选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Web视图用于显示HTML预览
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(300)
        layout.addWidget(self.web_view)

        # 加载状态
        self.loading_label = QLabel("选择模板以查看预览")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(self.loading_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        return widget

    def create_static_preview_tab(self) -> QWidget:
        """创建静态预览选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 缩略图显示
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setMinimumSize(400, 300)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                background-color: #f9f9f9;
            }
        """)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setText("无预览图")
        layout.addWidget(self.thumbnail_label)

        return widget

    def create_details_tab(self) -> QWidget:
        """创建详细信息选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # 基本信息
        self.info_group = QGroupBox("基本信息")
        info_layout = QVBoxLayout(self.info_group)

        self.name_label = QLabel("名称: -")
        self.description_label = QLabel("描述: -")
        self.description_label.setWordWrap(True)
        self.category_label = QLabel("分类: -")
        self.difficulty_label = QLabel("难度: -")
        self.duration_label = QLabel("时长: -")

        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.description_label)
        info_layout.addWidget(self.category_label)
        info_layout.addWidget(self.difficulty_label)
        info_layout.addWidget(self.duration_label)

        scroll_layout.addWidget(self.info_group)

        # 技术信息
        self.tech_group = QGroupBox("技术信息")
        tech_layout = QVBoxLayout(self.tech_group)

        self.tech_stack_label = QLabel("技术栈: -")
        self.libraries_label = QLabel("依赖库: -")
        self.libraries_label.setWordWrap(True)
        self.features_label = QLabel("特性: -")
        self.features_label.setWordWrap(True)

        tech_layout.addWidget(self.tech_stack_label)
        tech_layout.addWidget(self.libraries_label)
        tech_layout.addWidget(self.features_label)

        scroll_layout.addWidget(self.tech_group)

        # 标签
        self.tags_group = QGroupBox("标签")
        tags_layout = QVBoxLayout(self.tags_group)

        self.tags_label = QLabel("无标签")
        self.tags_label.setWordWrap(True)
        tags_layout.addWidget(self.tags_label)

        scroll_layout.addWidget(self.tags_group)

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        return widget

    def create_control_panel(self) -> QWidget:
        """创建控制面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMaximumHeight(80)

        layout = QHBoxLayout(panel)

        # 播放控制
        self.play_button = QPushButton("▶ 播放")
        self.play_button.clicked.connect(self.play_preview)
        self.play_button.setEnabled(False)

        self.pause_button = QPushButton("⏸ 暂停")
        self.pause_button.clicked.connect(self.pause_preview)
        self.pause_button.setEnabled(False)

        self.reset_button = QPushButton("⏹ 重置")
        self.reset_button.clicked.connect(self.reset_preview)
        self.reset_button.setEnabled(False)

        layout.addWidget(self.play_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.reset_button)

        # 时间滑块
        layout.addWidget(QLabel("时间:"))
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 100)
        self.time_slider.setValue(0)
        self.time_slider.valueChanged.connect(self.seek_preview)
        self.time_slider.setEnabled(False)
        layout.addWidget(self.time_slider)

        # 时间显示
        self.time_label = QLabel("0.0s / 0.0s")
        layout.addWidget(self.time_label)

        layout.addStretch()

        return panel

    def load_template_preview(self, template: 'ProjectTemplate'):
        """加载模板预览"""
        self.current_template = template

        if not template:
            self.clear_preview()
            return

        # 更新详细信息
        self.update_template_details(template)

        # 加载静态预览
        self.load_static_preview(template)

        # 加载实时预览
        self.load_live_preview(template)

    def update_template_details(self, template: 'ProjectTemplate'):
        """更新模板详细信息"""
        self.name_label.setText(f"名称: {template.name}")
        self.description_label.setText(f"描述: {template.description}")
        self.category_label.setText(f"分类: {template.category}")
        self.difficulty_label.setText(f"难度: {template.difficulty}")
        self.duration_label.setText(f"时长: {template.duration}秒")

        self.tech_stack_label.setText(f"技术栈: {template.tech_stack.value}")

        libraries = ", ".join(template.required_libraries) if template.required_libraries else "无"
        self.libraries_label.setText(f"依赖库: {libraries}")

        features = ", ".join(template.features) if template.features else "无"
        self.features_label.setText(f"特性: {features}")

        tags = " ".join([f"#{tag}" for tag in template.tags]) if template.tags else "无标签"
        self.tags_label.setText(tags)

    def load_static_preview(self, template: 'ProjectTemplate'):
        """加载静态预览"""
        if template.thumbnail and template.thumbnail.exists():
            try:
                pixmap = QPixmap(str(template.thumbnail))
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.thumbnail_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.thumbnail_label.setPixmap(scaled_pixmap)
                else:
                    self.thumbnail_label.setText("无法加载预览图")
            except Exception as e:
                logger.error(f"加载缩略图失败: {e}")
                self.thumbnail_label.setText("加载预览图失败")
        else:
            self.thumbnail_label.setText("无预览图")

    def load_live_preview(self, template: 'ProjectTemplate'):
        """加载实时预览"""
        self.loading_label.setText("正在加载预览...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 无限进度条

        # 启动预览加载线程
        self.preview_worker = TemplatePreviewWorker(template)
        self.preview_worker.preview_ready.connect(self.on_preview_ready)
        self.preview_worker.error_occurred.connect(self.on_preview_error)
        self.preview_worker.start()

    def on_preview_ready(self, template_id: str, html_content: str):
        """预览加载完成"""
        if self.current_template and self.current_template.id == template_id:
            self.progress_bar.setVisible(False)
            self.loading_label.setText("")

            # 加载HTML到WebView
            self.web_view.setHtml(html_content)

            # 启用控制按钮
            self.play_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            self.time_slider.setEnabled(True)

            logger.info(f"模板预览加载完成: {template_id}")

    def on_preview_error(self, template_id: str, error_msg: str):
        """预览加载错误"""
        if self.current_template and self.current_template.id == template_id:
            self.progress_bar.setVisible(False)
            self.loading_label.setText(f"预览加载失败: {error_msg}")
            logger.error(f"模板预览加载失败: {template_id} - {error_msg}")

    def play_preview(self):
        """播放预览"""
        if self.web_view:
            self.web_view.page().runJavaScript("window.previewControls.play();")
            self.play_button.setEnabled(False)
            self.pause_button.setEnabled(True)

            # 启动时间更新定时器
            self.start_time_update()

    def pause_preview(self):
        """暂停预览"""
        if self.web_view:
            self.web_view.page().runJavaScript("window.previewControls.pause();")
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)

    def reset_preview(self):
        """重置预览"""
        if self.web_view:
            self.web_view.page().runJavaScript("window.previewControls.reset();")
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.time_slider.setValue(0)
            self.time_label.setText("0.0s / 0.0s")

    def seek_preview(self, value):
        """跳转预览时间"""
        if self.web_view and self.current_template:
            time_ratio = value / 100.0
            seek_time = time_ratio * self.current_template.duration
            self.web_view.page().runJavaScript(f"window.previewControls.seek({seek_time});")

    def start_time_update(self):
        """启动时间更新"""
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time_display)
        self.time_timer.start(100)  # 每100ms更新一次

    def update_time_display(self):
        """更新时间显示"""
        if self.web_view:
            # 获取当前播放时间
            self.web_view.page().runJavaScript(
                "window.previewControls.getCurrentTime();",
                self.on_time_updated
            )

    def on_time_updated(self, current_time):
        """时间更新回调"""
        if self.current_template and isinstance(current_time, (int, float)):
            total_time = self.current_template.duration
            progress = int((current_time / total_time) * 100) if total_time > 0 else 0

            self.time_slider.setValue(progress)
            self.time_label.setText(f"{current_time:.1f}s / {total_time:.1f}s")

            # 检查是否播放完成
            if current_time >= total_time:
                self.play_button.setEnabled(True)
                self.pause_button.setEnabled(False)
                if hasattr(self, 'time_timer'):
                    self.time_timer.stop()

    def clear_preview(self):
        """清空预览"""
        self.web_view.setHtml("")
        self.thumbnail_label.clear()
        self.thumbnail_label.setText("选择模板以查看预览")
        self.loading_label.setText("选择模板以查看预览")

        # 禁用控制按钮
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.time_slider.setEnabled(False)

        # 清空详细信息
        self.name_label.setText("名称: -")
        self.description_label.setText("描述: -")
        self.category_label.setText("分类: -")
        self.difficulty_label.setText("难度: -")
        self.duration_label.setText("时长: -")
        self.tech_stack_label.setText("技术栈: -")
        self.libraries_label.setText("依赖库: -")
        self.features_label.setText("特性: -")
        self.tags_label.setText("无标签")

class TemplateCard(QFrame):
    """模板卡片组件"""
    
    template_selected = pyqtSignal(str)  # 模板选择信号
    
    def __init__(self, template: ProjectTemplate, parent=None):
        super().__init__(parent)
        self.template = template
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            TemplateCard {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #f9f9f9;
            }
            TemplateCard:hover {
                border-color: #007acc;
                background-color: #f0f8ff;
            }
        """)
        self.setFixedSize(280, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 缩略图区域
        thumbnail_label = QLabel()
        thumbnail_label.setFixedSize(260, 120)
        thumbnail_label.setStyleSheet("border: 1px solid #ccc; background-color: #fff;")
        thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 加载缩略图或显示默认图像
        if self.template.thumbnail:
            try:
                pixmap = QPixmap(self.template.thumbnail)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(260, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    thumbnail_label.setPixmap(scaled_pixmap)
                else:
                    thumbnail_label.setText("无预览图")
            except:
                thumbnail_label.setText("无预览图")
        else:
            # 生成默认缩略图
            self.generate_default_thumbnail(thumbnail_label)
        
        layout.addWidget(thumbnail_label)
        
        # 模板信息
        info_layout = QVBoxLayout()

        # 标题行（包含标题和评分）
        title_row = QHBoxLayout()

        title_label = QLabel(self.template.name)
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        title_row.addWidget(title_label)

        title_row.addStretch()

        # 评分显示
        rating_widget = self.create_rating_widget()
        title_row.addWidget(rating_widget)

        info_layout.addLayout(title_row)

        # 描述
        desc_label = QLabel(self.template.description[:50] + "..." if len(self.template.description) > 50 else self.template.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; font-size: 9px;")
        info_layout.addWidget(desc_label)

        # 底部信息行
        bottom_row = QHBoxLayout()

        # 标签
        tags_text = " ".join([f"#{tag}" for tag in self.template.tags[:2]])  # 最多显示2个标签
        tags_label = QLabel(tags_text)
        tags_label.setStyleSheet("color: #007acc; font-size: 8px;")
        bottom_row.addWidget(tags_label)

        bottom_row.addStretch()

        # 难度和技术栈
        meta_info = f"{self.template.difficulty} | {self.template.tech_stack}"
        meta_label = QLabel(meta_info)
        meta_label.setStyleSheet("color: #999; font-size: 8px;")
        bottom_row.addWidget(meta_label)

        info_layout.addLayout(bottom_row)
        
        layout.addLayout(info_layout)

    def create_rating_widget(self) -> QWidget:
        """创建评分显示组件"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        if self.template.rating_count > 0:
            # 显示星级评分
            stars = self.get_star_display(self.template.rating)
            star_label = QLabel(stars)
            star_label.setStyleSheet("color: #ffa500; font-size: 10px;")
            layout.addWidget(star_label)

            # 显示评分数值
            rating_text = f"{self.template.rating:.1f}"
            rating_label = QLabel(rating_text)
            rating_label.setStyleSheet("color: #333; font-size: 9px; font-weight: bold;")
            layout.addWidget(rating_label)

            # 显示评分人数
            count_text = f"({self.template.rating_count})"
            count_label = QLabel(count_text)
            count_label.setStyleSheet("color: #999; font-size: 8px;")
            layout.addWidget(count_label)
        else:
            # 无评分
            no_rating_label = QLabel("暂无评分")
            no_rating_label.setStyleSheet("color: #999; font-size: 8px;")
            layout.addWidget(no_rating_label)

        return widget

    def get_star_display(self, rating: float) -> str:
        """获取星级显示"""
        full_stars = int(rating)
        half_star = 1 if rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star

        return "★" * full_stars + "☆" * half_star + "☆" * empty_stars

    def generate_default_thumbnail(self, label: QLabel):
        """生成默认缩略图"""
        pixmap = QPixmap(260, 120)
        pixmap.fill(QColor("#f0f0f0"))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor("#ccc"))
        painter.setFont(QFont("Microsoft YaHei", 12))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, self.template.category)
        painter.end()
        
        label.setPixmap(pixmap)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.template_selected.emit(self.template.id)
        super().mousePressEvent(event)

class TemplateDialog(QDialog):
    """模板选择对话框"""
    
    template_selected = pyqtSignal(str)  # 选择的模板ID
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.template_manager = TemplateManager()
        self.selected_template_id = None
        
        self.setWindowTitle("选择项目模板")
        self.setMinimumSize(900, 600)
        self.setModal(True)
        
        self.setup_ui()
        self.load_templates()
        
        logger.info("模板选择对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 顶部：搜索和过滤
        self.setup_filter_section(layout)
        
        # 中间：分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧：模板列表
        self.setup_template_list(splitter)
        
        # 右侧：模板详情
        self.setup_template_details(splitter)
        
        # 设置分割器比例
        splitter.setSizes([600, 300])
        
        # 底部：按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("使用模板")
        self.ok_button.setEnabled(False)
        
        layout.addWidget(button_box)
    
    def setup_filter_section(self, parent_layout):
        """设置过滤区域"""
        filter_group = QGroupBox("筛选和搜索")
        filter_layout = QVBoxLayout(filter_group)

        # 第一行：搜索和分类
        first_row = QHBoxLayout()

        # 搜索框
        first_row.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索模板...")
        self.search_input.textChanged.connect(self.filter_templates)
        first_row.addWidget(self.search_input)

        # 分类过滤
        first_row.addWidget(QLabel("分类:"))
        self.category_combo = QComboBox()
        self.category_combo.addItem("全部分类")
        self.category_combo.currentTextChanged.connect(self.filter_templates)
        first_row.addWidget(self.category_combo)

        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.load_templates)
        first_row.addWidget(refresh_btn)

        filter_layout.addLayout(first_row)

        # 第二行：排序和推荐
        second_row = QHBoxLayout()

        # 排序方式
        second_row.addWidget(QLabel("排序:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "推荐度", "评分", "下载量", "最新", "名称"
        ])
        self.sort_combo.currentTextChanged.connect(self.filter_templates)
        second_row.addWidget(self.sort_combo)

        # 难度筛选
        second_row.addWidget(QLabel("难度:"))
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["全部难度", "初级", "中级", "高级"])
        self.difficulty_combo.currentTextChanged.connect(self.filter_templates)
        second_row.addWidget(self.difficulty_combo)

        # 技术栈筛选
        second_row.addWidget(QLabel("技术栈:"))
        self.tech_stack_combo = QComboBox()
        self.tech_stack_combo.addItems(["全部技术栈", "CSS", "GSAP", "Three.js", "Canvas"])
        self.tech_stack_combo.currentTextChanged.connect(self.filter_templates)
        second_row.addWidget(self.tech_stack_combo)

        # 只显示高评分
        self.high_rating_checkbox = QCheckBox("仅显示高评分(4.0+)")
        self.high_rating_checkbox.toggled.connect(self.filter_templates)
        second_row.addWidget(self.high_rating_checkbox)

        second_row.addStretch()

        filter_layout.addLayout(second_row)

        parent_layout.addWidget(filter_group)
    
    def setup_template_list(self, parent):
        """设置模板列表"""
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        # 标题
        list_layout.addWidget(QLabel("可用模板"))
        
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 模板容器
        self.template_container = QWidget()
        self.template_layout = QGridLayout(self.template_container)
        self.template_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.template_container)
        list_layout.addWidget(self.scroll_area)
        
        parent.addWidget(list_widget)
    
    def setup_template_details(self, parent):
        """设置模板详情 - 使用增强预览组件"""
        # 使用新的增强预览组件
        self.enhanced_preview = EnhancedTemplatePreview()
        parent.addWidget(self.enhanced_preview)
    
    def load_templates(self):
        """加载模板"""
        try:
            # 重新加载模板
            self.template_manager.load_templates()
            
            # 更新分类下拉框
            categories = self.template_manager.get_all_categories()
            self.category_combo.clear()
            self.category_combo.addItem("全部分类")
            self.category_combo.addItems(categories)
            
            # 显示模板
            self.display_templates(list(self.template_manager.templates.values()))
            
        except Exception as e:
            logger.error(f"加载模板失败: {e}")
            QMessageBox.warning(self, "错误", f"加载模板失败: {e}")
    
    def display_templates(self, templates):
        """显示模板列表"""
        # 清空现有模板卡片
        for i in reversed(range(self.template_layout.count())):
            child = self.template_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加模板卡片
        row, col = 0, 0
        max_cols = 2  # 每行最多2个模板
        
        for template in templates:
            card = TemplateCard(template)
            card.template_selected.connect(self.on_template_selected)
            
            self.template_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 更新滚动区域
        self.template_container.adjustSize()
    
    def filter_templates(self):
        """过滤模板 - 增强版"""
        search_text = self.search_input.text().strip()
        selected_category = self.category_combo.currentText()
        selected_difficulty = self.difficulty_combo.currentText()
        selected_tech_stack = self.tech_stack_combo.currentText()
        sort_method = self.sort_combo.currentText()
        high_rating_only = self.high_rating_checkbox.isChecked()

        # 获取模板
        if sort_method == "推荐度":
            # 使用推荐系统
            all_templates = self.template_manager.get_recommended_templates(limit=50)
        else:
            all_templates = list(self.template_manager.templates.values())

        # 应用过滤条件
        filtered_templates = []

        for template in all_templates:
            # 分类过滤
            if selected_category != "全部分类" and template.category != selected_category:
                continue

            # 难度过滤
            if selected_difficulty != "全部难度" and template.difficulty != selected_difficulty:
                continue

            # 技术栈过滤
            if selected_tech_stack != "全部技术栈" and template.tech_stack != selected_tech_stack:
                continue

            # 高评分过滤
            if high_rating_only and (template.rating < 4.0 or template.rating_count == 0):
                continue

            # 搜索过滤
            if search_text:
                if not (search_text.lower() in template.name.lower() or
                       search_text.lower() in template.description.lower() or
                       any(search_text.lower() in tag.lower() for tag in template.tags)):
                    continue

            filtered_templates.append(template)

        # 应用排序
        if sort_method != "推荐度":  # 推荐度已经排序了
            filtered_templates = self._sort_templates(filtered_templates, sort_method)

        # 显示过滤后的模板
        self.display_templates(filtered_templates)

    def _sort_templates(self, templates: list, sort_method: str) -> list:
        """排序模板"""
        if sort_method == "评分":
            return sorted(templates, key=lambda t: (t.rating, t.rating_count), reverse=True)
        elif sort_method == "下载量":
            return sorted(templates, key=lambda t: t.download_count, reverse=True)
        elif sort_method == "最新":
            return sorted(templates, key=lambda t: t.created_time, reverse=True)
        elif sort_method == "名称":
            return sorted(templates, key=lambda t: t.name.lower())
        else:
            return templates
    
    def on_template_selected(self, template_id: str):
        """模板选择事件 - 使用增强预览"""
        self.selected_template_id = template_id
        template = self.template_manager.templates[template_id]

        # 使用增强预览组件加载模板
        self.enhanced_preview.load_template_preview(template)

        # 启用确定按钮
        self.ok_button.setEnabled(True)

        logger.info(f"已选择模板: {template.name}")
    
    def preview_template(self):
        """预览模板 - 打开增强预览对话框"""
        if not self.selected_template_id:
            QMessageBox.information(self, "提示", "请先选择一个模板")
            return

        try:
            # 获取选中的模板
            template = None
            for tmpl in self.template_manager.get_templates():
                if tmpl.template_id == self.selected_template_id:
                    template = tmpl
                    break

            if not template:
                QMessageBox.warning(self, "错误", "无法找到选中的模板")
                return

            # 打开增强预览对话框
            preview_dialog = TemplatePreviewDialog(template, self)
            preview_dialog.template_selected.connect(self.template_selected.emit)

            # 显示对话框
            if preview_dialog.exec() == QDialog.DialogCode.Accepted:
                logger.info(f"用户从预览对话框选择了模板: {template.name}")
                # 如果用户在预览对话框中选择了模板，关闭当前对话框
                self.accept()

        except Exception as e:
            logger.error(f"打开模板预览对话框失败: {e}")
            QMessageBox.critical(self, "错误", f"无法打开模板预览: {str(e)}")

            # 回退到原有的预览方式
            self.enhanced_preview.tab_widget.setCurrentIndex(0)
            if self.enhanced_preview.play_button.isEnabled():
                self.enhanced_preview.play_preview()
    
    def accept(self):
        """确定按钮"""
        if self.selected_template_id:
            self.template_selected.emit(self.selected_template_id)
            super().accept()
        else:
            QMessageBox.information(self, "提示", "请先选择一个模板")
    
    def get_selected_template_id(self) -> Optional[str]:
        """获取选择的模板ID"""
        return self.selected_template_id
