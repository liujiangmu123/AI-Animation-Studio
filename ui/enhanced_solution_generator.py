"""
AI Animation Studio - 增强方案生成器界面
提供可视化方案预览、评分系统、收藏功能、版本控制等
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit, QComboBox,
    QProgressBar, QCheckBox, QSpinBox, QSlider, QTabWidget, QFrame,
    QScrollArea, QGridLayout, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QTextBrowser, QTableWidget, QTableWidgetItem, QHeaderView,
    QMenu, QButtonGroup, QRadioButton, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QIcon, QAction

from core.enhanced_solution_manager import (
    EnhancedSolutionManager, EnhancedAnimationSolution, SolutionQuality,
    SolutionCategory, SolutionMetrics
)
from core.solution_recommendation_engine import SolutionRecommendationEngine
from core.solution_performance_optimizer import PerformanceOptimizer
from utils.solution_import_export import SolutionImportExportManager
from core.data_structures import TechStack
from core.logger import get_logger

logger = get_logger("enhanced_solution_generator")


class SolutionCard(QFrame):
    """方案卡片组件"""
    
    solution_selected = pyqtSignal(str)      # 方案选中
    solution_favorited = pyqtSignal(str)     # 方案收藏
    solution_rated = pyqtSignal(str, float)  # 方案评分
    solution_previewed = pyqtSignal(str)     # 方案预览
    
    def __init__(self, solution: EnhancedAnimationSolution, parent=None):
        super().__init__(parent)
        
        self.solution = solution
        self.is_favorite = False
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setMaximumWidth(300)
        self.setMinimumHeight(200)
        
        layout = QVBoxLayout(self)
        
        # 标题栏
        title_layout = QHBoxLayout()
        
        # 方案名称
        self.name_label = QLabel(self.solution.name)
        self.name_label.setFont(QFont("", 12, QFont.Weight.Bold))
        title_layout.addWidget(self.name_label)
        
        title_layout.addStretch()
        
        # 收藏按钮
        self.favorite_btn = QPushButton("⭐")
        self.favorite_btn.setMaximumWidth(30)
        self.favorite_btn.setCheckable(True)
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        title_layout.addWidget(self.favorite_btn)
        
        layout.addLayout(title_layout)
        
        # 预览区域
        self.preview_area = QLabel()
        self.preview_area.setMinimumHeight(120)
        self.preview_area.setStyleSheet("border: 1px solid #ddd; background: #f9f9f9;")
        self.preview_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_area.setText("点击预览")
        self.preview_area.mousePressEvent = self.on_preview_clicked
        layout.addWidget(self.preview_area)
        
        # 信息区域
        info_layout = QVBoxLayout()
        
        # 技术栈和分类
        tech_category_layout = QHBoxLayout()
        
        self.tech_label = QLabel(self.solution.tech_stack.value)
        self.tech_label.setStyleSheet("background: #e3f2fd; padding: 2px 6px; border-radius: 3px; font-size: 10px;")
        tech_category_layout.addWidget(self.tech_label)
        
        self.category_label = QLabel(self.solution.category.value)
        self.category_label.setStyleSheet("background: #f3e5f5; padding: 2px 6px; border-radius: 3px; font-size: 10px;")
        tech_category_layout.addWidget(self.category_label)
        
        tech_category_layout.addStretch()
        
        info_layout.addLayout(tech_category_layout)
        
        # 质量指示器
        quality_layout = QHBoxLayout()
        
        self.quality_progress = QProgressBar()
        self.quality_progress.setRange(0, 100)
        self.quality_progress.setValue(int(self.solution.metrics.overall_score))
        self.quality_progress.setMaximumHeight(15)
        self.quality_progress.setFormat(f"质量: %v%")
        quality_layout.addWidget(self.quality_progress)
        
        info_layout.addLayout(quality_layout)
        
        # 评分和使用统计
        stats_layout = QHBoxLayout()
        
        # 用户评分
        rating_text = f"⭐ {self.solution.user_rating:.1f}"
        if self.solution.rating_count > 0:
            rating_text += f" ({self.solution.rating_count})"
        self.rating_label = QLabel(rating_text)
        stats_layout.addWidget(self.rating_label)
        
        stats_layout.addStretch()
        
        # 使用次数
        self.usage_label = QLabel(f"使用: {self.solution.usage_count}")
        stats_layout.addWidget(self.usage_label)
        
        info_layout.addLayout(stats_layout)
        
        layout.addLayout(info_layout)
        
        # 操作按钮
        actions_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("👁️ 预览")
        self.preview_btn.clicked.connect(self.preview_solution)
        actions_layout.addWidget(self.preview_btn)
        
        self.apply_btn = QPushButton("✅ 应用")
        self.apply_btn.clicked.connect(self.apply_solution)
        actions_layout.addWidget(self.apply_btn)
        
        layout.addLayout(actions_layout)
        
        # 设置质量等级颜色
        self.update_quality_appearance()
    
    def setup_connections(self):
        """设置信号连接"""
        pass
    
    def update_quality_appearance(self):
        """更新质量外观"""
        quality_colors = {
            SolutionQuality.EXCELLENT: "#4CAF50",
            SolutionQuality.GOOD: "#8BC34A",
            SolutionQuality.AVERAGE: "#FFC107",
            SolutionQuality.POOR: "#F44336"
        }
        
        color = quality_colors.get(self.solution.quality_level, "#9E9E9E")
        self.setStyleSheet(f"SolutionCard {{ border-left: 4px solid {color}; }}")
    
    def toggle_favorite(self, checked: bool):
        """切换收藏状态"""
        self.is_favorite = checked
        self.favorite_btn.setText("⭐" if checked else "☆")
        self.solution_favorited.emit(self.solution.solution_id)
    
    def on_preview_clicked(self, event):
        """预览点击事件"""
        self.preview_solution()
    
    def preview_solution(self):
        """预览方案"""
        self.solution_previewed.emit(self.solution.solution_id)
    
    def apply_solution(self):
        """应用方案"""
        self.solution_selected.emit(self.solution.solution_id)
    
    def update_solution_data(self, solution: EnhancedAnimationSolution):
        """更新方案数据"""
        self.solution = solution
        
        # 更新显示
        self.name_label.setText(solution.name)
        self.quality_progress.setValue(int(solution.metrics.overall_score))
        
        rating_text = f"⭐ {solution.user_rating:.1f}"
        if solution.rating_count > 0:
            rating_text += f" ({solution.rating_count})"
        self.rating_label.setText(rating_text)
        
        self.usage_label.setText(f"使用: {solution.usage_count}")
        
        self.update_quality_appearance()


class SolutionFilterPanel(QWidget):
    """方案过滤面板"""
    
    filter_changed = pyqtSignal(dict)  # 过滤条件改变
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 过滤器组
        filter_group = QGroupBox("筛选条件")
        filter_layout = QVBoxLayout(filter_group)
        
        # 分类过滤
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("分类:"))
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("全部", None)
        for category in SolutionCategory:
            self.category_combo.addItem(category.value, category)
        filter_layout.addLayout(category_layout)
        
        # 技术栈过滤
        tech_layout = QHBoxLayout()
        tech_layout.addWidget(QLabel("技术栈:"))
        
        self.tech_combo = QComboBox()
        self.tech_combo.addItem("全部", None)
        for tech in TechStack:
            self.tech_combo.addItem(tech.value, tech)
        tech_layout.addLayout(tech_layout)
        
        # 质量过滤
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("最低质量:"))
        
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(0, 100)
        self.quality_slider.setValue(0)
        quality_layout.addWidget(self.quality_slider)
        
        self.quality_label = QLabel("0%")
        quality_layout.addWidget(self.quality_label)
        
        filter_layout.addLayout(quality_layout)
        
        # 评分过滤
        rating_layout = QHBoxLayout()
        rating_layout.addWidget(QLabel("最低评分:"))
        
        self.rating_slider = QSlider(Qt.Orientation.Horizontal)
        self.rating_slider.setRange(0, 50)  # 0-5.0 * 10
        self.rating_slider.setValue(0)
        rating_layout.addWidget(self.rating_slider)
        
        self.rating_label = QLabel("0.0⭐")
        rating_layout.addWidget(self.rating_label)
        
        filter_layout.addLayout(rating_layout)
        
        # 其他选项
        options_layout = QVBoxLayout()
        
        self.favorites_only_cb = QCheckBox("仅显示收藏")
        options_layout.addWidget(self.favorites_only_cb)
        
        self.recent_only_cb = QCheckBox("仅显示最近")
        options_layout.addWidget(self.recent_only_cb)
        
        filter_layout.addLayout(options_layout)
        
        # 重置按钮
        reset_btn = QPushButton("🔄 重置筛选")
        reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(reset_btn)
        
        layout.addWidget(filter_group)
        
        # 排序选项
        sort_group = QGroupBox("排序方式")
        sort_layout = QVBoxLayout(sort_group)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "综合评分", "用户评分", "使用次数", "创建时间", "更新时间", "质量分数"
        ])
        sort_layout.addWidget(self.sort_combo)
        
        self.sort_order_cb = QCheckBox("降序排列")
        self.sort_order_cb.setChecked(True)
        sort_layout.addWidget(self.sort_order_cb)
        
        layout.addWidget(sort_group)
    
    def setup_connections(self):
        """设置信号连接"""
        self.category_combo.currentTextChanged.connect(self.emit_filter_changed)
        self.tech_combo.currentTextChanged.connect(self.emit_filter_changed)
        self.quality_slider.valueChanged.connect(self.on_quality_changed)
        self.rating_slider.valueChanged.connect(self.on_rating_changed)
        self.favorites_only_cb.toggled.connect(self.emit_filter_changed)
        self.recent_only_cb.toggled.connect(self.emit_filter_changed)
        self.sort_combo.currentTextChanged.connect(self.emit_filter_changed)
        self.sort_order_cb.toggled.connect(self.emit_filter_changed)
    
    def on_quality_changed(self, value: int):
        """质量滑块改变"""
        self.quality_label.setText(f"{value}%")
        self.emit_filter_changed()
    
    def on_rating_changed(self, value: int):
        """评分滑块改变"""
        rating = value / 10.0
        self.rating_label.setText(f"{rating:.1f}⭐")
        self.emit_filter_changed()
    
    def emit_filter_changed(self):
        """发送过滤条件改变信号"""
        filters = self.get_current_filters()
        self.filter_changed.emit(filters)
    
    def get_current_filters(self) -> Dict[str, Any]:
        """获取当前过滤条件"""
        return {
            "category": self.category_combo.currentData(),
            "tech_stack": self.tech_combo.currentData(),
            "min_quality": self.quality_slider.value(),
            "min_rating": self.rating_slider.value() / 10.0,
            "favorites_only": self.favorites_only_cb.isChecked(),
            "recent_only": self.recent_only_cb.isChecked(),
            "sort_by": self.sort_combo.currentText(),
            "sort_descending": self.sort_order_cb.isChecked()
        }
    
    def reset_filters(self):
        """重置过滤器"""
        self.category_combo.setCurrentIndex(0)
        self.tech_combo.setCurrentIndex(0)
        self.quality_slider.setValue(0)
        self.rating_slider.setValue(0)
        self.favorites_only_cb.setChecked(False)
        self.recent_only_cb.setChecked(False)
        self.sort_combo.setCurrentIndex(0)
        self.sort_order_cb.setChecked(True)


class SolutionPreviewDialog(QDialog):
    """方案预览对话框"""
    
    def __init__(self, solution: EnhancedAnimationSolution, parent=None):
        super().__init__(parent)
        
        self.solution = solution
        
        self.setup_ui()
        self.load_preview_content()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle(f"方案预览 - {self.solution.name}")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 标题栏
        title_layout = QHBoxLayout()
        
        title_label = QLabel(self.solution.name)
        title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 质量标签
        quality_label = QLabel(f"质量: {self.solution.quality_level.value}")
        quality_colors = {
            SolutionQuality.EXCELLENT: "green",
            SolutionQuality.GOOD: "blue",
            SolutionQuality.AVERAGE: "orange",
            SolutionQuality.POOR: "red"
        }
        color = quality_colors.get(self.solution.quality_level, "gray")
        quality_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        title_layout.addWidget(quality_label)
        
        layout.addLayout(title_layout)
        
        # 主内容区
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：代码预览
        code_panel = self.create_code_panel()
        content_splitter.addWidget(code_panel)
        
        # 右侧：信息和控制
        info_panel = self.create_info_panel()
        content_splitter.addWidget(info_panel)
        
        content_splitter.setSizes([500, 300])
        layout.addWidget(content_splitter)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        apply_btn = QPushButton("✅ 应用方案")
        apply_btn.clicked.connect(self.apply_solution)
        button_layout.addWidget(apply_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def create_code_panel(self):
        """创建代码面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 代码标签页
        code_tabs = QTabWidget()
        
        # HTML标签页
        if self.solution.html_code:
            html_edit = QTextEdit()
            html_edit.setPlainText(self.solution.html_code)
            html_edit.setReadOnly(True)
            html_edit.setFont(QFont("Consolas", 10))
            code_tabs.addTab(html_edit, "HTML")
        
        # CSS标签页
        if self.solution.css_code:
            css_edit = QTextEdit()
            css_edit.setPlainText(self.solution.css_code)
            css_edit.setReadOnly(True)
            css_edit.setFont(QFont("Consolas", 10))
            code_tabs.addTab(css_edit, "CSS")
        
        # JavaScript标签页
        if self.solution.js_code:
            js_edit = QTextEdit()
            js_edit.setPlainText(self.solution.js_code)
            js_edit.setReadOnly(True)
            js_edit.setFont(QFont("Consolas", 10))
            code_tabs.addTab(js_edit, "JavaScript")
        
        # 完整代码标签页
        full_code_edit = QTextEdit()
        full_code = self.solution.html_code
        if self.solution.css_code:
            full_code += f"\n\n<style>\n{self.solution.css_code}\n</style>"
        if self.solution.js_code:
            full_code += f"\n\n<script>\n{self.solution.js_code}\n</script>"
        
        full_code_edit.setPlainText(full_code)
        full_code_edit.setReadOnly(True)
        full_code_edit.setFont(QFont("Consolas", 10))
        code_tabs.addTab(full_code_edit, "完整代码")
        
        layout.addWidget(code_tabs)
        
        return panel
    
    def create_info_panel(self):
        """创建信息面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 基本信息
        basic_info_group = QGroupBox("基本信息")
        basic_info_layout = QFormLayout(basic_info_group)
        
        basic_info_layout.addRow("名称:", QLabel(self.solution.name))
        basic_info_layout.addRow("分类:", QLabel(self.solution.category.value))
        basic_info_layout.addRow("技术栈:", QLabel(self.solution.tech_stack.value))
        basic_info_layout.addRow("作者:", QLabel(self.solution.author))
        basic_info_layout.addRow("版本:", QLabel(self.solution.version))
        
        created_time = self.solution.created_at.strftime("%Y-%m-%d %H:%M")
        basic_info_layout.addRow("创建时间:", QLabel(created_time))
        
        layout.addWidget(basic_info_group)
        
        # 评估指标
        metrics_group = QGroupBox("评估指标")
        metrics_layout = QVBoxLayout(metrics_group)
        
        metrics_data = [
            ("综合评分", self.solution.metrics.overall_score),
            ("质量分数", self.solution.metrics.quality_score),
            ("性能分数", self.solution.metrics.performance_score),
            ("创意分数", self.solution.metrics.creativity_score),
            ("易用性", self.solution.metrics.usability_score),
            ("兼容性", self.solution.metrics.compatibility_score)
        ]
        
        for name, score in metrics_data:
            metric_layout = QHBoxLayout()
            metric_layout.addWidget(QLabel(f"{name}:"))
            
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setValue(int(score))
            progress.setFormat(f"%v%")
            progress.setMaximumHeight(20)
            metric_layout.addWidget(progress)
            
            metrics_layout.addLayout(metric_layout)
        
        layout.addWidget(metrics_group)
        
        # 用户反馈
        feedback_group = QGroupBox("用户反馈")
        feedback_layout = QVBoxLayout(feedback_group)
        
        # 评分显示
        rating_layout = QHBoxLayout()
        rating_layout.addWidget(QLabel("用户评分:"))
        
        rating_display = QLabel(f"{self.solution.user_rating:.1f} ⭐")
        rating_display.setFont(QFont("", 12, QFont.Weight.Bold))
        rating_layout.addWidget(rating_display)
        
        rating_layout.addWidget(QLabel(f"({self.solution.rating_count} 人评分)"))
        rating_layout.addStretch()
        
        feedback_layout.addLayout(rating_layout)
        
        # 统计信息
        stats_layout = QVBoxLayout()
        stats_layout.addWidget(QLabel(f"使用次数: {self.solution.usage_count}"))
        stats_layout.addWidget(QLabel(f"收藏次数: {self.solution.favorite_count}"))
        
        feedback_layout.addLayout(stats_layout)
        
        # 评分操作
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(QLabel("给方案评分:"))
        
        self.rating_combo = QComboBox()
        self.rating_combo.addItems(["5⭐ 优秀", "4⭐ 良好", "3⭐ 一般", "2⭐ 较差", "1⭐ 很差"])
        rate_layout.addWidget(self.rating_combo)
        
        rate_btn = QPushButton("提交评分")
        rate_btn.clicked.connect(self.submit_rating)
        rate_layout.addWidget(rate_btn)
        
        feedback_layout.addLayout(rate_layout)
        
        layout.addWidget(feedback_group)
        
        layout.addStretch()
        
        return panel
    
    def load_preview_content(self):
        """加载预览内容"""
        # TODO: 实现实际的HTML预览
        pass
    
    def apply_solution(self):
        """应用方案"""
        # TODO: 实现方案应用逻辑
        QMessageBox.information(self, "成功", f"方案 '{self.solution.name}' 已应用")
        self.accept()
    
    def submit_rating(self):
        """提交评分"""
        try:
            rating_text = self.rating_combo.currentText()
            rating_value = float(rating_text[0])  # 提取数字
            
            # 更新方案评分
            self.solution.add_user_rating(rating_value)
            
            QMessageBox.information(self, "成功", f"评分 {rating_value}⭐ 已提交")
            
        except Exception as e:
            logger.error(f"提交评分失败: {e}")
            QMessageBox.warning(self, "错误", "提交评分失败")


class EnhancedSolutionGenerator(QWidget):
    """增强方案生成器"""
    
    # 信号定义
    solution_generated = pyqtSignal(list)        # 方案生成完成
    solution_selected = pyqtSignal(str)          # 方案选中
    solution_applied = pyqtSignal(str)           # 方案应用
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.solution_manager = EnhancedSolutionManager()
        self.recommendation_engine = SolutionRecommendationEngine()
        self.performance_optimizer = PerformanceOptimizer()
        self.import_export_manager = SolutionImportExportManager()
        self.current_solutions = []
        self.solution_cards = []
        
        self.setup_ui()
        self.setup_connections()
        
        # 加载初始方案
        self.load_solutions()
        
        logger.info("增强方案生成器初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QHBoxLayout(self)
        
        # 左侧：过滤和控制面板
        left_panel = QWidget()
        left_panel.setMaximumWidth(250)
        left_layout = QVBoxLayout(left_panel)
        
        # 过滤面板
        self.filter_panel = SolutionFilterPanel()
        left_layout.addWidget(self.filter_panel)
        
        # 操作按钮
        actions_group = QGroupBox("操作")
        actions_layout = QVBoxLayout(actions_group)
        
        generate_btn = QPushButton("🚀 生成新方案")
        generate_btn.clicked.connect(self.generate_new_solutions)
        actions_layout.addWidget(generate_btn)

        template_btn = QPushButton("🎨 从模板创建")
        template_btn.clicked.connect(self.create_from_template)
        actions_layout.addWidget(template_btn)
        
        refresh_btn = QPushButton("🔄 刷新列表")
        refresh_btn.clicked.connect(self.refresh_solutions)
        actions_layout.addWidget(refresh_btn)
        
        smart_recommend_btn = QPushButton("🧠 智能推荐")
        smart_recommend_btn.clicked.connect(self.show_smart_recommendations)
        actions_layout.addWidget(smart_recommend_btn)

        optimize_btn = QPushButton("⚡ 性能优化")
        optimize_btn.clicked.connect(self.optimize_selected_solution)
        actions_layout.addWidget(optimize_btn)

        import_btn = QPushButton("📥 导入方案")
        import_btn.clicked.connect(self.import_solutions)
        actions_layout.addWidget(import_btn)

        export_btn = QPushButton("📤 导出方案")
        export_btn.clicked.connect(self.export_solutions)
        actions_layout.addWidget(export_btn)
        
        left_layout.addWidget(actions_group)
        
        # 统计信息
        stats_group = QGroupBox("统计信息")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("加载中...")
        stats_layout.addWidget(self.stats_label)
        
        left_layout.addWidget(stats_group)
        
        layout.addWidget(left_panel)
        
        # 右侧：方案展示区
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 搜索栏
        search_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 搜索方案...")
        self.search_edit.textChanged.connect(self.search_solutions)
        search_layout.addWidget(self.search_edit)
        
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)
        
        right_layout.addLayout(search_layout)
        
        # 方案展示区
        self.solutions_scroll = QScrollArea()
        self.solutions_scroll.setWidgetResizable(True)
        self.solutions_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.solutions_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 方案容器
        self.solutions_container = QWidget()
        self.solutions_layout = QGridLayout(self.solutions_container)
        self.solutions_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.solutions_scroll.setWidget(self.solutions_container)
        right_layout.addWidget(self.solutions_scroll)
        
        layout.addWidget(right_panel)
    
    def setup_connections(self):
        """设置信号连接"""
        self.filter_panel.filter_changed.connect(self.apply_filters)
    
    def load_solutions(self):
        """加载方案"""
        try:
            # 获取所有方案
            all_solutions = list(self.solution_manager.solutions.values())
            
            # 按综合评分排序
            all_solutions.sort(key=lambda x: x.metrics.overall_score, reverse=True)
            
            self.current_solutions = all_solutions
            self.update_solutions_display()
            self.update_statistics()
            
        except Exception as e:
            logger.error(f"加载方案失败: {e}")
    
    def update_solutions_display(self):
        """更新方案显示"""
        try:
            # 清空现有卡片
            for card in self.solution_cards:
                card.setParent(None)
            self.solution_cards.clear()
            
            # 创建新卡片
            row, col = 0, 0
            max_cols = 3  # 每行最多3个卡片
            
            for solution in self.current_solutions:
                card = SolutionCard(solution)
                card.solution_selected.connect(self.on_solution_selected)
                card.solution_favorited.connect(self.on_solution_favorited)
                card.solution_previewed.connect(self.on_solution_previewed)
                
                self.solutions_layout.addWidget(card, row, col)
                self.solution_cards.append(card)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            logger.info(f"显示 {len(self.current_solutions)} 个方案")
            
        except Exception as e:
            logger.error(f"更新方案显示失败: {e}")
    
    def update_statistics(self):
        """更新统计信息"""
        try:
            stats = self.solution_manager.get_statistics()
            
            if stats:
                stats_text = f"总方案数: {stats.get('total_solutions', 0)}\n"
                stats_text += f"收藏数: {stats.get('total_favorites', 0)}\n"
                stats_text += f"平均质量: {stats.get('average_quality', 0):.1f}\n"
                stats_text += f"平均评分: {stats.get('average_rating', 0):.1f}⭐"
                
                self.stats_label.setText(stats_text)
            
        except Exception as e:
            logger.error(f"更新统计信息失败: {e}")
    
    def apply_filters(self, filters: Dict[str, Any]):
        """应用过滤器"""
        try:
            # 从所有方案开始过滤
            filtered_solutions = list(self.solution_manager.solutions.values())
            
            # 应用各种过滤条件
            if filters.get("category"):
                filtered_solutions = [s for s in filtered_solutions if s.category == filters["category"]]
            
            if filters.get("tech_stack"):
                filtered_solutions = [s for s in filtered_solutions if s.tech_stack == filters["tech_stack"]]
            
            if filters.get("min_quality", 0) > 0:
                min_quality = filters["min_quality"]
                filtered_solutions = [s for s in filtered_solutions if s.metrics.overall_score >= min_quality]
            
            if filters.get("min_rating", 0) > 0:
                min_rating = filters["min_rating"]
                filtered_solutions = [s for s in filtered_solutions if s.user_rating >= min_rating]
            
            if filters.get("favorites_only", False):
                favorite_ids = set(self.solution_manager.favorites)
                filtered_solutions = [s for s in filtered_solutions if s.solution_id in favorite_ids]
            
            if filters.get("recent_only", False):
                week_ago = datetime.now() - timedelta(days=7)
                filtered_solutions = [s for s in filtered_solutions if s.created_at >= week_ago]
            
            # 排序
            sort_by = filters.get("sort_by", "综合评分")
            sort_descending = filters.get("sort_descending", True)
            
            if sort_by == "综合评分":
                filtered_solutions.sort(key=lambda x: x.metrics.overall_score, reverse=sort_descending)
            elif sort_by == "用户评分":
                filtered_solutions.sort(key=lambda x: x.user_rating, reverse=sort_descending)
            elif sort_by == "使用次数":
                filtered_solutions.sort(key=lambda x: x.usage_count, reverse=sort_descending)
            elif sort_by == "创建时间":
                filtered_solutions.sort(key=lambda x: x.created_at, reverse=sort_descending)
            elif sort_by == "更新时间":
                filtered_solutions.sort(key=lambda x: x.updated_at, reverse=sort_descending)
            
            self.current_solutions = filtered_solutions
            self.update_solutions_display()
            
        except Exception as e:
            logger.error(f"应用过滤器失败: {e}")
    
    def search_solutions(self, query: str):
        """搜索方案"""
        if not query.strip():
            self.load_solutions()
            return
        
        # 延迟搜索
        if hasattr(self, 'search_timer'):
            self.search_timer.stop()
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(lambda: self.perform_search(query))
        self.search_timer.start(500)
    
    def perform_search(self, query: str = None):
        """执行搜索"""
        try:
            if query is None:
                query = self.search_edit.text()
            
            if not query.strip():
                self.load_solutions()
                return
            
            # 搜索方案
            search_results = self.solution_manager.search_solutions(query)
            
            self.current_solutions = search_results
            self.update_solutions_display()
            
            logger.info(f"搜索 '{query}' 找到 {len(search_results)} 个结果")
            
        except Exception as e:
            logger.error(f"搜索方案失败: {e}")
    
    def on_solution_selected(self, solution_id: str):
        """方案选中事件"""
        try:
            solution = self.solution_manager.solutions.get(solution_id)
            if solution:
                solution.increment_usage()
                self.solution_manager.save_solution(solution)

                # 更新推荐引擎的用户行为
                self.recommendation_engine.update_user_behavior("apply", solution)

                self.solution_selected.emit(solution_id)
                self.solution_applied.emit(solution_id)

                logger.info(f"方案已选中: {solution.name}")
            
        except Exception as e:
            logger.error(f"处理方案选中失败: {e}")
    
    def on_solution_favorited(self, solution_id: str):
        """方案收藏事件"""
        try:
            solution = self.solution_manager.solutions.get(solution_id)
            if solution:
                if solution_id in self.solution_manager.favorites:
                    self.solution_manager.remove_from_favorites(solution_id)
                else:
                    self.solution_manager.add_to_favorites(solution_id)
                    # 跟踪收藏行为
                    self.recommendation_engine.update_user_behavior("favorite", solution)

                # 更新显示
                self.update_statistics()
            
        except Exception as e:
            logger.error(f"处理方案收藏失败: {e}")
    
    def on_solution_previewed(self, solution_id: str):
        """方案预览事件"""
        try:
            solution = self.solution_manager.solutions.get(solution_id)
            if solution:
                # 跟踪预览行为
                self.recommendation_engine.update_user_behavior("view", solution)

                dialog = SolutionPreviewDialog(solution, self)
                dialog.exec()
            
        except Exception as e:
            logger.error(f"预览方案失败: {e}")
    
    def generate_new_solutions(self):
        """生成新方案"""
        QMessageBox.information(self, "提示", "新方案生成功能将在后续版本中实现")

    def create_from_template(self):
        """从模板创建方案"""
        try:
            from ui.template_selector_dialog import show_template_selector

            # 显示模板选择器
            template_data = show_template_selector(self)

            if template_data:
                # 创建新方案
                solution = EnhancedAnimationSolution()
                solution.name = template_data["name"]
                solution.description = template_data["description"]
                solution.category = template_data["category"]
                solution.tech_stack = template_data["tech_stack"]
                solution.html_code = template_data["html_code"]
                solution.css_code = template_data["css_code"]
                solution.js_code = template_data["js_code"]
                solution.author = "模板生成"

                # 添加到方案管理器
                solution_id = self.solution_manager.add_solution(solution)

                if solution_id:
                    # 刷新显示
                    self.refresh_solutions()

                    QMessageBox.information(
                        self, "成功",
                        f"已从模板创建方案: {solution.name}"
                    )

                    logger.info(f"从模板创建方案: {solution.name}")
                else:
                    QMessageBox.warning(self, "错误", "创建方案失败")

        except Exception as e:
            logger.error(f"从模板创建方案失败: {e}")
            QMessageBox.warning(self, "错误", "从模板创建方案失败")
    
    def refresh_solutions(self):
        """刷新方案列表"""
        self.solution_manager.load_solutions()
        self.load_solutions()
    
    def import_solutions(self):
        """导入方案"""
        try:
            imported_solutions = self.import_export_manager.import_solutions_with_dialog(self)

            if imported_solutions:
                # 添加导入的方案到管理器
                for solution in imported_solutions:
                    self.solution_manager.add_solution(solution)

                # 刷新显示
                self.refresh_solutions()

                logger.info(f"成功导入 {len(imported_solutions)} 个方案")

        except Exception as e:
            logger.error(f"导入方案失败: {e}")
            QMessageBox.warning(self, "错误", "导入方案失败")

    def export_solutions(self):
        """导出方案"""
        try:
            if not self.current_solutions:
                QMessageBox.information(self, "提示", "没有可导出的方案")
                return

            # 导出当前显示的方案
            success = self.import_export_manager.export_solutions_with_dialog(
                self.current_solutions, self
            )

            if success:
                logger.info(f"成功导出 {len(self.current_solutions)} 个方案")

        except Exception as e:
            logger.error(f"导出方案失败: {e}")
            QMessageBox.warning(self, "错误", "导出方案失败")

    def show_smart_recommendations(self):
        """显示智能推荐"""
        try:
            # 获取所有方案
            all_solutions = list(self.solution_manager.solutions.values())

            if not all_solutions:
                QMessageBox.information(self, "提示", "暂无方案可推荐")
                return

            # 获取个性化推荐
            recommendations = self.recommendation_engine.get_personalized_recommendations(
                all_solutions, limit=10
            )

            if not recommendations:
                QMessageBox.information(self, "提示", "暂无推荐方案")
                return

            # 显示推荐对话框
            self.show_recommendations_dialog(recommendations)

        except Exception as e:
            logger.error(f"显示智能推荐失败: {e}")
            QMessageBox.warning(self, "错误", "获取推荐失败")

    def show_recommendations_dialog(self, recommendations):
        """显示推荐对话框"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle("🧠 智能推荐")
        dialog.setMinimumSize(600, 400)

        layout = QVBoxLayout(dialog)

        # 推荐列表
        recommendations_list = QListWidget()

        for rec in recommendations:
            solution = self.solution_manager.solutions.get(rec.solution_id)
            if solution:
                item_text = f"{solution.name}\n"
                item_text += f"推荐分数: {rec.total_score:.2f}\n"
                item_text += f"推荐理由: {rec.explanation}"

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, solution.solution_id)
                recommendations_list.addItem(item)

        layout.addWidget(recommendations_list)

        # 按钮
        button_layout = QHBoxLayout()

        apply_btn = QPushButton("应用选中方案")
        apply_btn.clicked.connect(lambda: self.apply_recommended_solution(recommendations_list, dialog))
        button_layout.addWidget(apply_btn)

        preview_btn = QPushButton("预览选中方案")
        preview_btn.clicked.connect(lambda: self.preview_recommended_solution(recommendations_list))
        button_layout.addWidget(preview_btn)

        button_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        dialog.exec()

    def apply_recommended_solution(self, recommendations_list, dialog):
        """应用推荐的方案"""
        try:
            current_item = recommendations_list.currentItem()
            if current_item:
                solution_id = current_item.data(Qt.ItemDataRole.UserRole)
                self.on_solution_selected(solution_id)
                dialog.accept()

        except Exception as e:
            logger.error(f"应用推荐方案失败: {e}")

    def preview_recommended_solution(self, recommendations_list):
        """预览推荐的方案"""
        try:
            current_item = recommendations_list.currentItem()
            if current_item:
                solution_id = current_item.data(Qt.ItemDataRole.UserRole)
                self.on_solution_previewed(solution_id)

        except Exception as e:
            logger.error(f"预览推荐方案失败: {e}")

    def optimize_selected_solution(self):
        """优化选中的方案"""
        try:
            # 获取当前选中的方案
            selected_solution = None

            # 简化实现：优化第一个方案
            if self.current_solutions:
                selected_solution = self.current_solutions[0]

            if not selected_solution:
                QMessageBox.information(self, "提示", "请先选择一个方案进行优化")
                return

            # 执行性能优化
            optimized_solution = self.performance_optimizer.auto_optimize_solution(selected_solution)

            # 添加优化后的方案
            self.solution_manager.add_solution(optimized_solution)

            # 刷新显示
            self.refresh_solutions()

            QMessageBox.information(
                self, "成功",
                f"方案 '{selected_solution.name}' 已优化完成\n"
                f"优化版本: '{optimized_solution.name}'"
            )

        except Exception as e:
            logger.error(f"优化方案失败: {e}")
            QMessageBox.warning(self, "错误", "方案优化失败")
