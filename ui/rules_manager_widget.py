"""
AI Animation Studio - 动画规则库管理器
管理和编辑动画规则文档
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QPushButton, QLabel, QGroupBox, QLineEdit, QComboBox,
    QMessageBox, QFileDialog, QInputDialog, QMenu, QTabWidget, QCheckBox,
    QSpinBox, QDoubleSpinBox, QSlider, QProgressBar, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout, QScrollArea,
    QFrame, QToolButton, QButtonGroup, QRadioButton, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QAction, QColor, QPixmap, QPainter, QLinearGradient, QSyntaxHighlighter, QTextCharFormat

from core.logger import get_logger

logger = get_logger("rules_manager_widget")

class RulesManagerWidget(QWidget):
    """动画规则库管理器 - 增强版"""

    # 信号定义
    rules_updated = pyqtSignal()  # 规则更新信号
    rule_validated = pyqtSignal(str, bool, str)  # 规则验证信号 (rule_id, valid, message)
    rule_recommended = pyqtSignal(str, float)  # 规则推荐信号 (rule_id, score)
    version_created = pyqtSignal(str, str)  # 版本创建信号 (rule_id, version)

    def __init__(self, parent=None):
        super().__init__(parent)

        # 规则库根目录
        self.rules_dir = Path(__file__).parent.parent / "assets" / "animation_rules"
        self.rules_dir.mkdir(parents=True, exist_ok=True)

        # 版本控制目录
        self.versions_dir = self.rules_dir / "versions"
        self.versions_dir.mkdir(exist_ok=True)

        # 当前状态
        self.current_file = None
        self.current_rule_id = None
        self.is_modified = False

        # 版本管理
        self.version_history = {}
        self.current_version = "1.0.0"

        # 智能推荐
        self.recommendation_engine = None
        self.usage_statistics = {}
        self.rule_relationships = {}

        # 验证系统
        self.validation_rules = []
        self.validation_enabled = True

        # 搜索和筛选
        self.search_filters = {
            'category': 'all',
            'complexity': 'all',
            'rating': 0,
            'recent': False
        }

        self.setup_ui()
        self.load_rules_tree()
        self.create_default_rules()
        self.setup_connections()
        self.initialize_recommendation_engine()

        logger.info("动画规则库管理器初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 顶部工具栏
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)

        # 主要内容区域
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧面板 - 规则浏览和管理
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)

        # 右侧面板 - 编辑和详情
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)

        # 设置分割器比例
        main_splitter.setSizes([400, 700])
        layout.addWidget(main_splitter)

        # 底部状态栏
        status_bar = self.create_status_bar()
        layout.addWidget(status_bar)

    def create_toolbar(self):
        """创建工具栏"""
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(toolbar_frame)

        # 文件操作
        self.new_rule_btn = QPushButton("📄 新建")
        self.new_rule_btn.setToolTip("新建规则")
        layout.addWidget(self.new_rule_btn)

        self.save_btn = QPushButton("💾 保存")
        self.save_btn.setToolTip("保存当前规则")
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)

        self.save_as_btn = QPushButton("📄 另存为")
        self.save_as_btn.setToolTip("另存为新规则")
        layout.addWidget(self.save_as_btn)

        layout.addWidget(QLabel("|"))

        # 版本控制
        self.create_version_btn = QPushButton("🏷️ 版本")
        self.create_version_btn.setToolTip("创建新版本")
        layout.addWidget(self.create_version_btn)

        self.version_combo = QComboBox()
        self.version_combo.setMinimumWidth(100)
        self.version_combo.setToolTip("选择版本")
        layout.addWidget(self.version_combo)

        layout.addWidget(QLabel("|"))

        # 验证和推荐
        self.validate_btn = QPushButton("✅ 验证")
        self.validate_btn.setToolTip("验证规则语法")
        self.validate_btn.clicked.connect(self.validate_current_rule)
        layout.addWidget(self.validate_btn)

        self.recommend_btn = QPushButton("💡 推荐")
        self.recommend_btn.setToolTip("获取智能推荐")
        self.recommend_btn.clicked.connect(self.show_rule_recommendations)
        layout.addWidget(self.recommend_btn)

        layout.addStretch()

        # 搜索框
        layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索规则...")
        self.search_input.setMaximumWidth(200)
        layout.addWidget(self.search_input)

        # 设置按钮
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setToolTip("设置")
        self.settings_btn.setMaximumWidth(30)
        layout.addWidget(self.settings_btn)

        return toolbar_frame

    def create_left_panel(self):
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 创建标签页
        tab_widget = QTabWidget()

        # 规则浏览标签页
        browse_tab = self.create_browse_tab()
        tab_widget.addTab(browse_tab, "📚 浏览")

        # 分类管理标签页
        categories_tab = self.create_categories_tab()
        tab_widget.addTab(categories_tab, "📁 分类")

        # 推荐标签页
        recommendations_tab = self.create_recommendations_tab()
        tab_widget.addTab(recommendations_tab, "💡 推荐")

        # 统计标签页
        statistics_tab = self.create_statistics_tab()
        tab_widget.addTab(statistics_tab, "📊 统计")

        layout.addWidget(tab_widget)

        return panel

    def create_browse_tab(self):
        """创建浏览标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 筛选控制
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        filter_layout = QFormLayout(filter_frame)

        # 分类筛选
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItems([
            "全部", "情感类规则", "物理类规则", "运动类规则", "场景类规则", "交互类规则"
        ])
        filter_layout.addRow("分类:", self.category_filter_combo)

        # 复杂度筛选
        self.complexity_filter_combo = QComboBox()
        self.complexity_filter_combo.addItems(["全部", "简单", "中等", "复杂", "专家"])
        filter_layout.addRow("复杂度:", self.complexity_filter_combo)

        # 评分筛选
        self.rating_filter_slider = QSlider(Qt.Orientation.Horizontal)
        self.rating_filter_slider.setRange(0, 5)
        self.rating_filter_slider.setValue(0)
        filter_layout.addRow("最低评分:", self.rating_filter_slider)

        # 最近使用
        self.recent_filter_cb = QCheckBox("仅显示最近使用")
        filter_layout.addRow("", self.recent_filter_cb)

        layout.addWidget(filter_frame)

        # 规则树
        self.rules_tree = QTreeWidget()
        self.rules_tree.setHeaderLabels(["规则名称", "类型", "评分", "使用次数"])
        self.rules_tree.header().setStretchLastSection(False)
        self.rules_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.rules_tree.setAlternatingRowColors(True)
        self.rules_tree.setSortingEnabled(True)
        self.rules_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        layout.addWidget(self.rules_tree)

        # 快速操作
        quick_actions = QHBoxLayout()

        self.expand_all_btn = QPushButton("展开全部")
        self.expand_all_btn.setMaximumWidth(80)
        quick_actions.addWidget(self.expand_all_btn)

        self.collapse_all_btn = QPushButton("折叠全部")
        self.collapse_all_btn.setMaximumWidth(80)
        quick_actions.addWidget(self.collapse_all_btn)

        quick_actions.addStretch()

        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setMaximumWidth(30)
        self.refresh_btn.setToolTip("刷新规则列表")
        quick_actions.addWidget(self.refresh_btn)

        layout.addLayout(quick_actions)

        return tab

    def create_categories_tab(self):
        """创建分类管理标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 分类列表
        self.categories_list = QListWidget()
        layout.addWidget(self.categories_list)

        # 分类操作
        category_actions = QHBoxLayout()

        self.add_category_btn = QPushButton("➕ 添加")
        category_actions.addWidget(self.add_category_btn)

        self.edit_category_btn = QPushButton("✏️ 编辑")
        category_actions.addWidget(self.edit_category_btn)

        self.delete_category_btn = QPushButton("🗑️ 删除")
        category_actions.addWidget(self.delete_category_btn)

        category_actions.addStretch()
        layout.addLayout(category_actions)

        # 分类属性
        category_props = QGroupBox("分类属性")
        props_layout = QFormLayout(category_props)

        self.category_name_input = QLineEdit()
        props_layout.addRow("名称:", self.category_name_input)

        self.category_description_input = QTextEdit()
        self.category_description_input.setMaximumHeight(80)
        props_layout.addRow("描述:", self.category_description_input)

        self.category_color_btn = QPushButton("选择颜色")
        props_layout.addRow("颜色:", self.category_color_btn)

        layout.addWidget(category_props)

        return tab

    def create_recommendations_tab(self):
        """创建推荐标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 推荐设置
        settings_group = QGroupBox("推荐设置")
        settings_layout = QFormLayout(settings_group)

        self.auto_recommend_cb = QCheckBox("自动推荐")
        self.auto_recommend_cb.setChecked(True)
        settings_layout.addRow("", self.auto_recommend_cb)

        self.recommendation_strength_slider = QSlider(Qt.Orientation.Horizontal)
        self.recommendation_strength_slider.setRange(1, 5)
        self.recommendation_strength_slider.setValue(3)
        settings_layout.addRow("推荐强度:", self.recommendation_strength_slider)

        layout.addWidget(settings_group)

        # 推荐列表
        self.recommendations_list = QListWidget()
        layout.addWidget(self.recommendations_list)

        # 推荐操作
        recommend_actions = QHBoxLayout()

        self.get_recommendations_btn = QPushButton("获取推荐")
        recommend_actions.addWidget(self.get_recommendations_btn)

        self.apply_recommendation_btn = QPushButton("应用推荐")
        recommend_actions.addWidget(self.apply_recommendation_btn)

        recommend_actions.addStretch()
        layout.addLayout(recommend_actions)

        return tab

    def create_statistics_tab(self):
        """创建统计标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 统计信息
        stats_group = QGroupBox("使用统计")
        stats_layout = QFormLayout(stats_group)

        self.total_rules_label = QLabel("0")
        stats_layout.addRow("总规则数:", self.total_rules_label)

        self.most_used_label = QLabel("无")
        stats_layout.addRow("最常用:", self.most_used_label)

        self.recent_created_label = QLabel("无")
        stats_layout.addRow("最近创建:", self.recent_created_label)

        self.avg_rating_label = QLabel("0.0")
        stats_layout.addRow("平均评分:", self.avg_rating_label)

        layout.addWidget(stats_group)

        # 使用历史
        history_group = QGroupBox("使用历史")
        history_layout = QVBoxLayout(history_group)

        self.usage_history_list = QListWidget()
        self.usage_history_list.setMaximumHeight(150)
        history_layout.addWidget(self.usage_history_list)

        layout.addWidget(history_group)

        layout.addStretch()
        return tab

    def create_right_panel(self):
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 创建标签页
        tab_widget = QTabWidget()

        # 编辑器标签页
        editor_tab = self.create_editor_tab()
        tab_widget.addTab(editor_tab, "✏️ 编辑器")

        # 预览标签页
        preview_tab = self.create_preview_tab()
        tab_widget.addTab(preview_tab, "👁️ 预览")

        # 版本历史标签页
        versions_tab = self.create_versions_tab()
        tab_widget.addTab(versions_tab, "🏷️ 版本")

        # 验证标签页
        validation_tab = self.create_validation_tab()
        tab_widget.addTab(validation_tab, "✅ 验证")

        layout.addWidget(tab_widget)

        return panel

    def create_editor_tab(self):
        """创建编辑器标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 文件信息
        info_group = QGroupBox("规则信息")
        info_layout = QFormLayout(info_group)

        self.rule_name_input = QLineEdit()
        info_layout.addRow("规则名称:", self.rule_name_input)

        self.rule_category_combo = QComboBox()
        self.rule_category_combo.addItems([
            "情感类规则", "物理类规则", "运动类规则", "场景类规则", "交互类规则"
        ])
        self.rule_category_combo.setEditable(True)
        info_layout.addRow("分类:", self.rule_category_combo)

        self.rule_complexity_combo = QComboBox()
        self.rule_complexity_combo.addItems(["简单", "中等", "复杂", "专家"])
        info_layout.addRow("复杂度:", self.rule_complexity_combo)

        self.rule_tags_input = QLineEdit()
        self.rule_tags_input.setPlaceholderText("用逗号分隔多个标签")
        info_layout.addRow("标签:", self.rule_tags_input)

        layout.addWidget(info_group)

        # 编辑器工具栏
        editor_toolbar = QHBoxLayout()

        self.bold_btn = QPushButton("B")
        self.bold_btn.setMaximumWidth(30)
        self.bold_btn.setToolTip("粗体")
        editor_toolbar.addWidget(self.bold_btn)

        self.italic_btn = QPushButton("I")
        self.italic_btn.setMaximumWidth(30)
        self.italic_btn.setToolTip("斜体")
        editor_toolbar.addWidget(self.italic_btn)

        self.code_btn = QPushButton("< >")
        self.code_btn.setMaximumWidth(40)
        self.code_btn.setToolTip("代码块")
        editor_toolbar.addWidget(self.code_btn)

        editor_toolbar.addStretch()

        self.word_count_label = QLabel("字数: 0")
        editor_toolbar.addWidget(self.word_count_label)

        layout.addLayout(editor_toolbar)

        # 文本编辑器
        self.rule_editor = QTextEdit()
        self.rule_editor.setPlaceholderText("在此输入规则内容...")
        layout.addWidget(self.rule_editor)

        return tab
    
    def setup_rules_tree(self, parent):
        """设置规则树"""
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索规则...")
        self.search_input.textChanged.connect(self.filter_rules)
        search_layout.addWidget(self.search_input)
        tree_layout.addLayout(search_layout)
        
        # 规则树
        self.rules_tree = QTreeWidget()
        self.rules_tree.setHeaderLabel("动画规则")
        self.rules_tree.itemClicked.connect(self.on_rule_selected)
        self.rules_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.rules_tree.customContextMenuRequested.connect(self.show_context_menu)
        tree_layout.addWidget(self.rules_tree)
        
        parent.addWidget(tree_widget)
    
    def setup_editor(self, parent):
        """设置编辑器"""
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # 文件信息
        info_group = QGroupBox("文件信息")
        info_layout = QVBoxLayout(info_group)
        
        # 文件名
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("文件名:"))
        self.file_name_label = QLabel("未选择文件")
        name_layout.addWidget(self.file_name_label)
        name_layout.addStretch()
        info_layout.addLayout(name_layout)
        
        # 分类
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("分类:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["情感类规则", "物理类规则", "运动类规则", "场景类规则"])
        self.category_combo.setEditable(True)
        category_layout.addWidget(self.category_combo)
        info_layout.addLayout(category_layout)
        
        editor_layout.addWidget(info_group)
        
        # 编辑器
        editor_group = QGroupBox("规则内容")
        editor_group_layout = QVBoxLayout(editor_group)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.bold_btn = QPushButton("B")
        self.bold_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.bold_btn.setMaximumWidth(30)
        self.bold_btn.clicked.connect(lambda: self.insert_markdown("**", "**"))
        toolbar_layout.addWidget(self.bold_btn)
        
        self.italic_btn = QPushButton("I")
        self.italic_btn.setFont(QFont("Arial", 10, QFont.Weight.Normal))
        self.italic_btn.setStyleSheet("font-style: italic;")
        self.italic_btn.setMaximumWidth(30)
        self.italic_btn.clicked.connect(lambda: self.insert_markdown("*", "*"))
        toolbar_layout.addWidget(self.italic_btn)
        
        self.code_btn = QPushButton("Code")
        self.code_btn.setMaximumWidth(50)
        self.code_btn.clicked.connect(lambda: self.insert_markdown("```\n", "\n```"))
        toolbar_layout.addWidget(self.code_btn)
        
        toolbar_layout.addStretch()
        
        self.preview_btn = QPushButton("👁️ 预览")
        self.preview_btn.clicked.connect(self.preview_markdown)
        toolbar_layout.addWidget(self.preview_btn)
        
        editor_group_layout.addLayout(toolbar_layout)
        
        # 文本编辑器
        self.text_editor = QTextEdit()
        self.text_editor.setFont(QFont("Consolas", 10))
        self.text_editor.textChanged.connect(self.on_text_changed)
        editor_group_layout.addWidget(self.text_editor)
        
        editor_layout.addWidget(editor_group)
        
        parent.addWidget(editor_widget)
    
    def load_rules_tree(self):
        """加载规则树"""
        self.rules_tree.clear()
        
        # 遍历规则目录
        for category_dir in self.rules_dir.iterdir():
            if category_dir.is_dir():
                category_item = QTreeWidgetItem(self.rules_tree)
                category_item.setText(0, category_dir.name)
                category_item.setData(0, Qt.ItemDataRole.UserRole, str(category_dir))
                
                # 加载分类下的规则文件
                for rule_file in category_dir.glob("*.md"):
                    rule_item = QTreeWidgetItem(category_item)
                    rule_item.setText(0, rule_file.stem)
                    rule_item.setData(0, Qt.ItemDataRole.UserRole, str(rule_file))
        
        # 展开所有项
        self.rules_tree.expandAll()
    
    def create_default_rules(self):
        """创建默认规则"""
        default_rules = {
            "情感类规则": {
                "稳定感.md": """# 稳定感动画规则

## 视觉特征
- 水平垂直线条为主
- 缓慢渐变效果
- 对称布局设计
- 平稳的运动轨迹

## 动画参数
- 缓动函数: ease-in-out
- 运动速度: 慢速 (1-2秒)
- 颜色变化: 渐进式
- 形状变化: 平滑过渡

## CSS实现
```css
.stable-animation {
    transition: all 2s ease-in-out;
    transform-origin: center;
}
```

## 应用场景
- 企业宣传
- 产品展示
- 数据报告
- 专业演示
""",
                "科技感.md": """# 科技感动画规则

## 视觉特征
- 60度网格背景
- 2.5D透视效果
- 发光边框和阴影
- 金属质感材质

## 动画参数
- 缓动函数: cubic-bezier(0.25, 0.46, 0.45, 0.94)
- 运动轨迹: 几何精确
- 光效动画: 脉冲闪烁
- 颜色方案: 蓝色系(#0066ff)、绿色系(#00ff00)

## CSS实现
```css
.tech-animation {
    filter: drop-shadow(0 0 10px #00ff00);
    transform: rotateX(60deg);
    background: linear-gradient(45deg, #001122, #003366);
}
```

## 应用场景
- 科技产品
- 数据可视化
- 未来概念
- 技术演示
"""
            },
            "物理类规则": {
                "重力效果.md": """# 重力效果动画规则

## 物理特征
- 下落加速运动
- 弹跳衰减效果
- 重力常数: 9.8m/s²
- 空气阻力影响

## 动画参数
- 初始速度: 0
- 加速度: 递增
- 弹跳系数: 0.7
- 摩擦系数: 0.1

## 实现方式
```javascript
function gravityAnimation(element, height) {
    const gravity = 9.8;
    const bounce = 0.7;
    // 实现重力动画逻辑
}
```

## 应用场景
- 物体掉落
- 弹球游戏
- 物理模拟
- 教育演示
"""
            }
        }
        
        # 创建默认规则文件
        for category, rules in default_rules.items():
            category_dir = self.rules_dir / category
            category_dir.mkdir(exist_ok=True)
            
            for filename, content in rules.items():
                rule_file = category_dir / filename
                if not rule_file.exists():
                    rule_file.write_text(content, encoding='utf-8')
    
    def on_rule_selected(self, item, column):
        """规则选择事件"""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        
        if file_path and Path(file_path).is_file():
            self.load_rule_file(file_path)
    
    def load_rule_file(self, file_path: str):
        """加载规则文件"""
        try:
            self.current_file = Path(file_path)
            
            # 读取文件内容
            content = self.current_file.read_text(encoding='utf-8')
            self.text_editor.setPlainText(content)
            
            # 更新界面
            self.file_name_label.setText(self.current_file.name)
            self.category_combo.setCurrentText(self.current_file.parent.name)
            
            self.save_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            
            logger.info(f"已加载规则文件: {file_path}")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载规则文件失败: {e}")
            logger.error(f"加载规则文件失败: {e}")
    
    def on_text_changed(self):
        """文本改变事件"""
        if self.current_file:
            self.save_btn.setEnabled(True)
    
    def save_current_rule(self):
        """保存当前规则"""
        if not self.current_file:
            return
        
        try:
            content = self.text_editor.toPlainText()
            self.current_file.write_text(content, encoding='utf-8')
            
            self.save_btn.setEnabled(False)
            self.rules_updated.emit()
            
            logger.info(f"规则文件已保存: {self.current_file}")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存规则文件失败: {e}")
            logger.error(f"保存规则文件失败: {e}")
    
    def new_rule(self):
        """新建规则"""
        name, ok = QInputDialog.getText(self, "新建规则", "请输入规则名称:")
        if ok and name:
            category = self.category_combo.currentText()
            category_dir = self.rules_dir / category
            category_dir.mkdir(exist_ok=True)
            
            rule_file = category_dir / f"{name}.md"
            if rule_file.exists():
                QMessageBox.warning(self, "错误", "规则文件已存在")
                return
            
            # 创建新规则文件
            template = f"""# {name}

## 描述
请在这里描述动画规则的特征和用途。

## 参数设置
- 参数1: 值1
- 参数2: 值2

## 实现方式
```css
/* CSS代码示例 */
.{name.lower().replace(' ', '-')} {{
    /* 样式定义 */
}}
```

## 应用场景
- 场景1
- 场景2
"""
            
            rule_file.write_text(template, encoding='utf-8')
            self.load_rules_tree()
            self.load_rule_file(str(rule_file))
    
    def new_category(self):
        """新建分类"""
        name, ok = QInputDialog.getText(self, "新建分类", "请输入分类名称:")
        if ok and name:
            category_dir = self.rules_dir / name
            if category_dir.exists():
                QMessageBox.warning(self, "错误", "分类已存在")
                return
            
            category_dir.mkdir()
            self.load_rules_tree()
    
    def delete_rule(self):
        """删除规则"""
        if not self.current_file:
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除规则文件 '{self.current_file.name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.current_file.unlink()
                self.current_file = None
                self.text_editor.clear()
                self.file_name_label.setText("未选择文件")
                self.save_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
                self.load_rules_tree()
                
                logger.info("规则文件已删除")
                
            except Exception as e:
                QMessageBox.warning(self, "错误", f"删除规则文件失败: {e}")
    
    def filter_rules(self, text):
        """过滤规则"""
        # TODO: 实现搜索过滤功能
        pass
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        # TODO: 实现右键菜单
        pass
    
    def insert_markdown(self, prefix, suffix):
        """插入Markdown格式"""
        cursor = self.text_editor.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            new_text = f"{prefix}{selected_text}{suffix}"
            cursor.insertText(new_text)
        else:
            cursor.insertText(f"{prefix}{suffix}")
            # 移动光标到中间
            for _ in range(len(suffix)):
                cursor.movePosition(cursor.MoveOperation.Left)
            self.text_editor.setTextCursor(cursor)
    
    def preview_markdown(self):
        """预览Markdown"""
        try:
            content = self.text_editor.toPlainText()
            if not content.strip():
                QMessageBox.warning(self, "警告", "没有内容可预览")
                return

            # 创建预览对话框
            from ui.markdown_preview_dialog import MarkdownPreviewDialog

            preview_dialog = MarkdownPreviewDialog(content, self.current_file.name if self.current_file else "预览", self)
            preview_dialog.exec()

        except Exception as e:
            logger.error(f"预览Markdown失败: {e}")
            QMessageBox.warning(self, "错误", "预览失败")
    
    def import_rules(self):
        """导入规则"""
        try:
            from PyQt6.QtWidgets import QFileDialog

            # 选择导入文件
            file_path, _ = QFileDialog.getOpenFileName(
                self, "导入规则", "",
                "规则文件 (*.md *.json *.zip);;Markdown文件 (*.md);;JSON文件 (*.json);;ZIP文件 (*.zip)"
            )

            if not file_path:
                return

            file_path = Path(file_path)

            if file_path.suffix == '.md':
                self.import_markdown_rule(file_path)
            elif file_path.suffix == '.json':
                self.import_json_rules(file_path)
            elif file_path.suffix == '.zip':
                self.import_zip_rules(file_path)
            else:
                QMessageBox.warning(self, "错误", "不支持的文件格式")

        except Exception as e:
            logger.error(f"导入规则失败: {e}")
            QMessageBox.warning(self, "错误", f"导入规则失败: {e}")

    def export_rules(self):
        """导出规则"""
        try:
            from PyQt6.QtWidgets import QFileDialog, QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox

            # 选择导出格式和选项
            export_dialog = QDialog(self)
            export_dialog.setWindowTitle("导出规则")
            export_dialog.setMinimumSize(400, 300)

            layout = QVBoxLayout(export_dialog)

            # 导出格式选择
            layout.addWidget(QLabel("导出格式:"))

            self.export_md_cb = QCheckBox("Markdown文件 (.md)")
            self.export_md_cb.setChecked(True)
            layout.addWidget(self.export_md_cb)

            self.export_json_cb = QCheckBox("JSON文件 (.json)")
            layout.addWidget(self.export_json_cb)

            self.export_zip_cb = QCheckBox("ZIP压缩包 (.zip)")
            layout.addWidget(self.export_zip_cb)

            # 导出选项
            layout.addWidget(QLabel("导出选项:"))

            self.export_all_cb = QCheckBox("导出所有规则")
            self.export_all_cb.setChecked(True)
            layout.addWidget(self.export_all_cb)

            self.export_current_cb = QCheckBox("仅导出当前规则")
            layout.addWidget(self.export_current_cb)

            self.include_metadata_cb = QCheckBox("包含元数据")
            self.include_metadata_cb.setChecked(True)
            layout.addWidget(self.include_metadata_cb)

            # 按钮
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(export_dialog.accept)
            buttons.rejected.connect(export_dialog.reject)
            layout.addWidget(buttons)

            if export_dialog.exec() == QDialog.DialogCode.Accepted:
                self.perform_export()

        except Exception as e:
            logger.error(f"导出规则失败: {e}")
            QMessageBox.warning(self, "错误", f"导出规则失败: {e}")

    def import_markdown_rule(self, file_path: Path):
        """导入Markdown规则文件"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # 询问导入到哪个分类
            category, ok = QInputDialog.getItem(
                self, "选择分类", "请选择导入到哪个分类:",
                [item.text() for item in self.category_combo.model().stringList()],
                0, False
            )

            if ok and category:
                category_dir = self.rules_dir / category
                category_dir.mkdir(exist_ok=True)

                # 生成新文件名
                new_file = category_dir / file_path.name
                counter = 1
                while new_file.exists():
                    stem = file_path.stem
                    new_file = category_dir / f"{stem}_{counter}.md"
                    counter += 1

                # 复制文件
                new_file.write_text(content, encoding='utf-8')

                # 刷新界面
                self.load_rules_tree()

                QMessageBox.information(self, "成功", f"规则已导入到 {category}/{new_file.name}")

        except Exception as e:
            logger.error(f"导入Markdown规则失败: {e}")
            raise

    def import_json_rules(self, file_path: Path):
        """导入JSON规则文件"""
        try:
            import json

            with open(file_path, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)

            imported_count = 0

            for rule_data in rules_data.get('rules', []):
                category = rule_data.get('category', '其他规则')
                name = rule_data.get('name', 'unnamed')
                content = rule_data.get('content', '')

                # 创建分类目录
                category_dir = self.rules_dir / category
                category_dir.mkdir(exist_ok=True)

                # 创建规则文件
                rule_file = category_dir / f"{name}.md"
                counter = 1
                while rule_file.exists():
                    rule_file = category_dir / f"{name}_{counter}.md"
                    counter += 1

                rule_file.write_text(content, encoding='utf-8')
                imported_count += 1

            # 刷新界面
            self.load_rules_tree()

            QMessageBox.information(self, "成功", f"成功导入 {imported_count} 个规则")

        except Exception as e:
            logger.error(f"导入JSON规则失败: {e}")
            raise

    def import_zip_rules(self, file_path: Path):
        """导入ZIP规则文件"""
        try:
            import zipfile

            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # 解压到临时目录
                import tempfile
                with tempfile.TemporaryDirectory() as temp_dir:
                    zip_file.extractall(temp_dir)

                    # 递归导入所有.md文件
                    temp_path = Path(temp_dir)
                    imported_count = 0

                    for md_file in temp_path.rglob("*.md"):
                        try:
                            # 根据目录结构确定分类
                            relative_path = md_file.relative_to(temp_path)
                            category = relative_path.parent.name if relative_path.parent.name != '.' else '导入规则'

                            # 导入文件
                            content = md_file.read_text(encoding='utf-8')

                            category_dir = self.rules_dir / category
                            category_dir.mkdir(exist_ok=True)

                            new_file = category_dir / md_file.name
                            counter = 1
                            while new_file.exists():
                                stem = md_file.stem
                                new_file = category_dir / f"{stem}_{counter}.md"
                                counter += 1

                            new_file.write_text(content, encoding='utf-8')
                            imported_count += 1

                        except Exception as e:
                            logger.warning(f"导入文件 {md_file} 失败: {e}")

            # 刷新界面
            self.load_rules_tree()

            QMessageBox.information(self, "成功", f"成功导入 {imported_count} 个规则")

        except Exception as e:
            logger.error(f"导入ZIP规则失败: {e}")
            raise

    def perform_export(self):
        """执行导出操作"""
        try:
            from PyQt6.QtWidgets import QFileDialog

            # 选择导出目录
            export_dir = QFileDialog.getExistingDirectory(self, "选择导出目录")
            if not export_dir:
                return

            export_path = Path(export_dir)
            exported_files = []

            # 获取要导出的规则
            if self.export_all_cb.isChecked():
                rules_to_export = self.get_all_rules_data()
            else:
                rules_to_export = self.get_current_rule_data()

            # 导出为Markdown
            if self.export_md_cb.isChecked():
                md_files = self.export_as_markdown(rules_to_export, export_path)
                exported_files.extend(md_files)

            # 导出为JSON
            if self.export_json_cb.isChecked():
                json_file = self.export_as_json(rules_to_export, export_path)
                exported_files.append(json_file)

            # 导出为ZIP
            if self.export_zip_cb.isChecked():
                zip_file = self.export_as_zip(rules_to_export, export_path)
                exported_files.append(zip_file)

            if exported_files:
                files_list = '\n'.join([f"• {f.name}" for f in exported_files])
                QMessageBox.information(self, "导出成功", f"已导出以下文件:\n{files_list}")
            else:
                QMessageBox.warning(self, "警告", "没有选择导出格式")

        except Exception as e:
            logger.error(f"执行导出失败: {e}")
            QMessageBox.warning(self, "错误", f"导出失败: {e}")
    
    def get_all_rules_content(self) -> str:
        """获取所有规则内容"""
        all_content = []
        
        for category_dir in self.rules_dir.iterdir():
            if category_dir.is_dir():
                all_content.append(f"\n# {category_dir.name}\n")
                
                for rule_file in category_dir.glob("*.md"):
                    try:
                        content = rule_file.read_text(encoding='utf-8')
                        all_content.append(content)
                        all_content.append("\n---\n")
                    except Exception as e:
                        logger.error(f"读取规则文件失败: {e}")
        
        return "\n".join(all_content)

    # 导出功能实现
    def get_all_rules_data(self):
        """获取所有规则数据"""
        try:
            rules_data = []

            for category_dir in self.rules_dir.iterdir():
                if category_dir.is_dir():
                    for rule_file in category_dir.glob("*.md"):
                        try:
                            content = rule_file.read_text(encoding='utf-8')
                            rules_data.append({
                                'name': rule_file.stem,
                                'category': category_dir.name,
                                'content': content,
                                'file_path': str(rule_file)
                            })
                        except Exception as e:
                            logger.warning(f"读取规则文件失败: {e}")

            return rules_data

        except Exception as e:
            logger.error(f"获取规则数据失败: {e}")
            return []

    def get_current_rule_data(self):
        """获取当前规则数据"""
        try:
            if not self.current_file:
                return []

            content = self.text_editor.toPlainText()
            return [{
                'name': self.current_file.stem,
                'category': self.current_file.parent.name,
                'content': content,
                'file_path': str(self.current_file)
            }]

        except Exception as e:
            logger.error(f"获取当前规则数据失败: {e}")
            return []

    def export_as_markdown(self, rules_data: list, export_path: Path):
        """导出为Markdown文件"""
        try:
            exported_files = []

            for rule in rules_data:
                # 创建分类目录
                category_dir = export_path / rule['category']
                category_dir.mkdir(exist_ok=True)

                # 写入文件
                file_path = category_dir / f"{rule['name']}.md"
                file_path.write_text(rule['content'], encoding='utf-8')
                exported_files.append(file_path)

            return exported_files

        except Exception as e:
            logger.error(f"导出Markdown失败: {e}")
            return []

    def export_as_json(self, rules_data: list, export_path: Path):
        """导出为JSON文件"""
        try:
            import json
            from datetime import datetime

            export_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0',
                    'total_rules': len(rules_data)
                },
                'rules': rules_data
            }

            file_path = export_path / "animation_rules.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            return file_path

        except Exception as e:
            logger.error(f"导出JSON失败: {e}")
            return None

    def export_as_zip(self, rules_data: list, export_path: Path):
        """导出为ZIP文件"""
        try:
            import zipfile
            from datetime import datetime

            zip_path = export_path / f"animation_rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # 添加规则文件
                for rule in rules_data:
                    file_path = f"{rule['category']}/{rule['name']}.md"
                    zip_file.writestr(file_path, rule['content'])

                # 添加README文件
                readme_content = f"""# 动画规则库导出

导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
规则总数: {len(rules_data)}

## 目录结构

"""

                categories = {}
                for rule in rules_data:
                    category = rule['category']
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(rule['name'])

                for category, rules in categories.items():
                    readme_content += f"### {category}\n"
                    for rule_name in rules:
                        readme_content += f"- {rule_name}.md\n"
                    readme_content += "\n"

                zip_file.writestr("README.md", readme_content)

            return zip_path

        except Exception as e:
            logger.error(f"导出ZIP失败: {e}")
            return None

    # 智能推荐功能
    def generate_rule_recommendations(self, context: dict = None):
        """生成规则推荐"""
        try:
            recommendations = []

            # 基于当前项目类型推荐
            project_type = context.get('project_type', 'general') if context else 'general'

            # 推荐规则映射
            recommendation_map = {
                'animation': [
                    ('情感类规则/动态感.md', '适合动画项目的动态效果'),
                    ('物理类规则/弹性效果.md', '增加动画的物理真实感'),
                    ('运动类规则/弹跳运动.md', '创建生动的运动效果')
                ],
                'ui': [
                    ('情感类规则/稳定感.md', '提供稳定的用户界面感受'),
                    ('情感类规则/亲和力.md', '增强界面亲和力'),
                    ('物理类规则/惯性效果.md', '自然的交互反馈')
                ],
                'game': [
                    ('运动类规则/火箭运动.md', '游戏中的推进效果'),
                    ('物理类规则/重力效果.md', '重力物理模拟'),
                    ('情感类规则/科技感.md', '科技风格设计')
                ],
                'general': [
                    ('情感类规则/稳定感.md', '通用的稳定感设计'),
                    ('物理类规则/弹性效果.md', '常用的弹性效果'),
                    ('情感类规则/动态感.md', '增加视觉动态性')
                ]
            }

            # 获取推荐规则
            project_recommendations = recommendation_map.get(project_type, recommendation_map['general'])

            for rule_path, reason in project_recommendations:
                full_path = self.rules_dir / rule_path
                if full_path.exists():
                    recommendations.append({
                        'path': rule_path,
                        'name': full_path.stem,
                        'category': full_path.parent.name,
                        'reason': reason,
                        'score': 0.8  # 基础推荐分数
                    })

            # 基于使用历史推荐（简化实现）
            if hasattr(self, 'usage_statistics'):
                for rule_path, usage_count in self.usage_statistics.items():
                    if usage_count > 3:  # 使用次数超过3次
                        rule_file = Path(rule_path)
                        if rule_file.exists():
                            recommendations.append({
                                'path': str(rule_file.relative_to(self.rules_dir)),
                                'name': rule_file.stem,
                                'category': rule_file.parent.name,
                                'reason': f'您经常使用此规则 ({usage_count}次)',
                                'score': min(0.9, 0.5 + usage_count * 0.1)
                            })

            # 去重和排序
            unique_recommendations = {}
            for rec in recommendations:
                key = rec['path']
                if key not in unique_recommendations or rec['score'] > unique_recommendations[key]['score']:
                    unique_recommendations[key] = rec

            # 按分数排序
            sorted_recommendations = sorted(
                unique_recommendations.values(),
                key=lambda x: x['score'],
                reverse=True
            )

            return sorted_recommendations[:5]  # 返回前5个推荐

        except Exception as e:
            logger.error(f"生成规则推荐失败: {e}")
            return []

    def show_rule_recommendations(self):
        """显示规则推荐对话框"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QDialogButtonBox

            recommendations = self.generate_rule_recommendations()

            if not recommendations:
                QMessageBox.information(self, "提示", "暂无推荐规则")
                return

            # 创建推荐对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("智能规则推荐")
            dialog.setMinimumSize(500, 400)

            layout = QVBoxLayout(dialog)

            # 推荐说明
            info_label = QLabel("基于您的项目类型和使用习惯，为您推荐以下规则:")
            info_label.setWordWrap(True)
            layout.addWidget(info_label)

            # 推荐列表
            recommendations_list = QListWidget()

            for rec in recommendations:
                item_text = f"📋 {rec['name']} ({rec['category']})\n💡 {rec['reason']}\n⭐ 推荐度: {rec['score']:.1f}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, rec['path'])
                recommendations_list.addItem(item)

            recommendations_list.itemDoubleClicked.connect(
                lambda item: self.apply_recommended_rule(item.data(Qt.ItemDataRole.UserRole))
            )

            layout.addWidget(recommendations_list)

            # 按钮
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )

            def apply_selected():
                current_item = recommendations_list.currentItem()
                if current_item:
                    rule_path = current_item.data(Qt.ItemDataRole.UserRole)
                    self.apply_recommended_rule(rule_path)
                dialog.accept()

            buttons.accepted.connect(apply_selected)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            dialog.exec()

        except Exception as e:
            logger.error(f"显示规则推荐失败: {e}")
            QMessageBox.warning(self, "错误", "显示推荐失败")

    def apply_recommended_rule(self, rule_path: str):
        """应用推荐的规则"""
        try:
            full_path = self.rules_dir / rule_path
            if full_path.exists():
                self.load_rule_file(str(full_path))

                # 更新使用统计
                if not hasattr(self, 'usage_statistics'):
                    self.usage_statistics = {}

                self.usage_statistics[str(full_path)] = self.usage_statistics.get(str(full_path), 0) + 1

                logger.info(f"应用推荐规则: {rule_path}")
            else:
                QMessageBox.warning(self, "错误", "推荐的规则文件不存在")

        except Exception as e:
            logger.error(f"应用推荐规则失败: {e}")
            QMessageBox.warning(self, "错误", "应用推荐规则失败")

    # 规则验证功能
    def validate_current_rule(self):
        """验证当前规则"""
        try:
            content = self.text_editor.toPlainText()
            if not content.strip():
                QMessageBox.warning(self, "警告", "没有内容可验证")
                return

            # 执行验证
            validation_results = self.validate_rule_content(content)

            # 显示验证结果
            self.show_validation_results(validation_results)

        except Exception as e:
            logger.error(f"验证规则失败: {e}")
            QMessageBox.warning(self, "错误", "验证规则失败")

    def validate_rule_content(self, content: str):
        """验证规则内容"""
        try:
            results = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'suggestions': [],
                'score': 100
            }

            # 基本结构验证
            if not content.startswith('#'):
                results['warnings'].append("建议以标题开始（使用 # 标记）")
                results['score'] -= 10

            # 检查必要章节
            required_sections = ['描述', '参数', '示例', '注意事项']
            missing_sections = []

            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)

            if missing_sections:
                results['warnings'].append(f"缺少推荐章节: {', '.join(missing_sections)}")
                results['score'] -= len(missing_sections) * 5

            # 检查代码块
            code_blocks = content.count('```')
            if code_blocks % 2 != 0:
                results['errors'].append("代码块标记不匹配（``` 数量应为偶数）")
                results['is_valid'] = False
                results['score'] -= 20

            # 检查链接格式
            import re
            invalid_links = re.findall(r'\[([^\]]*)\]\(([^)]*)\)', content)
            for link_text, link_url in invalid_links:
                if not link_url.strip():
                    results['warnings'].append(f"链接 '{link_text}' 缺少URL")
                    results['score'] -= 5

            # 内容质量检查
            if len(content) < 100:
                results['warnings'].append("内容较短，建议添加更多详细信息")
                results['score'] -= 15

            if content.count('\n') < 5:
                results['warnings'].append("建议增加段落分隔，提高可读性")
                results['score'] -= 10

            # 生成改进建议
            if results['score'] < 80:
                results['suggestions'].append("考虑添加更多示例代码")
                results['suggestions'].append("增加详细的参数说明")
                results['suggestions'].append("添加使用场景描述")

            # 确保分数不低于0
            results['score'] = max(0, results['score'])

            return results

        except Exception as e:
            logger.error(f"验证规则内容失败: {e}")
            return {
                'is_valid': False,
                'errors': [f"验证过程出错: {e}"],
                'warnings': [],
                'suggestions': [],
                'score': 0
            }

    def show_validation_results(self, results: dict):
        """显示验证结果"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QTextEdit, QDialogButtonBox

            dialog = QDialog(self)
            dialog.setWindowTitle("规则验证结果")
            dialog.setMinimumSize(600, 500)

            layout = QVBoxLayout(dialog)

            # 总体评分
            score = results['score']
            score_color = "#28a745" if score >= 80 else "#ffc107" if score >= 60 else "#dc3545"

            score_label = QLabel(f"📊 总体评分: {score}/100")
            score_label.setStyleSheet(f"""
                font-size: 16px;
                font-weight: bold;
                color: {score_color};
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
                border-left: 4px solid {score_color};
            """)
            layout.addWidget(score_label)

            # 详细结果标签页
            tabs = QTabWidget()

            # 错误标签页
            if results['errors']:
                errors_text = QTextEdit()
                errors_text.setReadOnly(True)
                error_content = "发现以下错误，需要修复:\n\n"
                for i, error in enumerate(results['errors'], 1):
                    error_content += f"{i}. ❌ {error}\n"
                errors_text.setPlainText(error_content)
                tabs.addTab(errors_text, f"❌ 错误 ({len(results['errors'])})")

            # 警告标签页
            if results['warnings']:
                warnings_text = QTextEdit()
                warnings_text.setReadOnly(True)
                warning_content = "发现以下警告，建议修复:\n\n"
                for i, warning in enumerate(results['warnings'], 1):
                    warning_content += f"{i}. ⚠️ {warning}\n"
                warnings_text.setPlainText(warning_content)
                tabs.addTab(warnings_text, f"⚠️ 警告 ({len(results['warnings'])})")

            # 建议标签页
            if results['suggestions']:
                suggestions_text = QTextEdit()
                suggestions_text.setReadOnly(True)
                suggestion_content = "改进建议:\n\n"
                for i, suggestion in enumerate(results['suggestions'], 1):
                    suggestion_content += f"{i}. 💡 {suggestion}\n"
                suggestions_text.setPlainText(suggestion_content)
                tabs.addTab(suggestions_text, f"💡 建议 ({len(results['suggestions'])})")

            # 如果没有问题，显示成功信息
            if not results['errors'] and not results['warnings'] and not results['suggestions']:
                success_text = QTextEdit()
                success_text.setReadOnly(True)
                success_text.setPlainText("🎉 恭喜！规则验证通过，没有发现问题。")
                tabs.addTab(success_text, "✅ 验证通过")

            layout.addWidget(tabs)

            # 按钮
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            buttons.accepted.connect(dialog.accept)
            layout.addWidget(buttons)

            dialog.exec()

        except Exception as e:
            logger.error(f"显示验证结果失败: {e}")
            QMessageBox.warning(self, "错误", "显示验证结果失败")

    # 增强搜索功能
    def enhanced_search_rules(self, query: str):
        """增强搜索功能"""
        try:
            if not query.strip():
                self.load_rules_tree()
                return

            # 清空当前树
            self.rules_tree.clear()

            # 搜索匹配的规则
            matches = []
            query_lower = query.lower()

            for category_dir in self.rules_dir.iterdir():
                if category_dir.is_dir():
                    category_matches = []

                    for rule_file in category_dir.glob("*.md"):
                        try:
                            # 检查文件名匹配
                            if query_lower in rule_file.stem.lower():
                                category_matches.append((rule_file, "文件名匹配"))
                                continue

                            # 检查内容匹配
                            content = rule_file.read_text(encoding='utf-8')
                            if query_lower in content.lower():
                                # 找到匹配的行
                                lines = content.split('\n')
                                match_lines = [i for i, line in enumerate(lines) if query_lower in line.lower()]
                                match_info = f"内容匹配 (第{match_lines[0]+1}行)" if match_lines else "内容匹配"
                                category_matches.append((rule_file, match_info))

                        except Exception as e:
                            logger.warning(f"搜索文件 {rule_file} 失败: {e}")

                    if category_matches:
                        matches.append((category_dir, category_matches))

            # 构建搜索结果树
            for category_dir, category_matches in matches:
                category_item = QTreeWidgetItem(self.rules_tree)
                category_item.setText(0, f"{category_dir.name} ({len(category_matches)})")
                category_item.setData(0, Qt.ItemDataRole.UserRole, str(category_dir))

                for rule_file, match_info in category_matches:
                    rule_item = QTreeWidgetItem(category_item)
                    rule_item.setText(0, f"{rule_file.stem} - {match_info}")
                    rule_item.setData(0, Qt.ItemDataRole.UserRole, str(rule_file))

            # 展开所有项
            self.rules_tree.expandAll()

            # 更新状态
            total_matches = sum(len(matches) for _, matches in matches)
            logger.info(f"搜索 '{query}' 找到 {total_matches} 个匹配项")

        except Exception as e:
            logger.error(f"增强搜索失败: {e}")
            QMessageBox.warning(self, "错误", "搜索失败")
