"""
AI Animation Studio - 元素管理器组件
提供元素列表管理和图层控制功能
"""

from typing import List, Optional, Dict, Any, Set
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QComboBox, QCheckBox, QSlider,
    QLineEdit, QMenu, QMessageBox, QInputDialog, QProgressBar,
    QSplitter, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QMimeData, QPoint
from PyQt6.QtGui import QIcon, QDrag, QPixmap, QPainter, QAction

from core.data_structures import Element, ElementType
from core.logger import get_logger

logger = get_logger("elements_widget")

class ElementListItem(QListWidgetItem):
    """元素列表项"""

    def __init__(self, element: Element):
        super().__init__()
        self.element = element
        self.is_selected = False
        self.update_display()

        # 设置拖拽属性
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled)

    def update_display(self):
        """更新显示 - 增强版"""
        # 使用更专业的图标
        type_icons = {
            ElementType.TEXT: "🔤",
            ElementType.IMAGE: "🖼️",
            ElementType.SHAPE: "⬛",
            ElementType.SVG: "🎨",
            ElementType.VIDEO: "🎬",
            ElementType.AUDIO: "🎵",
            ElementType.GROUP: "📁"
        }

        icon = type_icons.get(self.element.element_type, "❓")
        visibility = "👁️" if self.element.visible else "👁️‍🗨️"
        lock = "🔒" if self.element.locked else "🔓"

        # 添加选择状态指示
        selection = "✅" if self.is_selected else ""

        # 添加图层深度指示
        z_index_indicator = f"[{getattr(self.element, 'z_index', 0)}]"

        # 构建显示文本 - 更清晰的格式
        text = f"{icon} {self.element.name} {z_index_indicator} {visibility}{lock} {selection}"
        self.setText(text)

        # 设置工具提示 - 更详细的信息
        tooltip_parts = [
            f"📋 名称: {self.element.name}",
            f"🏷️ 类型: {self.element.element_type.value}",
            f"🆔 ID: {self.element.element_id}",
            f"📍 位置: ({self.element.position.x:.1f}, {self.element.position.y:.1f})",
            f"🎭 图层: {getattr(self.element, 'z_index', 0)}",
            f"👁️ 可见: {'是' if self.element.visible else '否'}",
            f"🔒 锁定: {'是' if self.element.locked else '否'}"
        ]

        # 添加大小信息
        if hasattr(self.element, 'size') and self.element.size:
            tooltip_parts.append(f"📐 大小: {self.element.size.width} × {self.element.size.height}")

        # 添加内容预览
        if hasattr(self.element, 'content') and self.element.content:
            content_preview = self.element.content[:50] + "..." if len(self.element.content) > 50 else self.element.content
            tooltip_parts.append(f"📄 内容: {content_preview}")

        self.setToolTip("\n".join(tooltip_parts))

        # 设置样式 - 增强版
        self._update_item_style()

    def _update_item_style(self):
        """更新项目样式"""
        from PyQt6.QtGui import QColor, QBrush

        # 根据元素状态设置前景色和背景色
        if self.is_selected:
            # 选中状态 - 蓝色背景
            self.setBackground(QBrush(QColor(173, 216, 230, 100)))
            self.setForeground(Qt.GlobalColor.black)
        elif not self.element.visible:
            # 隐藏状态 - 灰色背景和前景
            self.setBackground(QBrush(QColor(128, 128, 128, 50)))
            self.setForeground(Qt.GlobalColor.gray)
        elif self.element.locked:
            # 锁定状态 - 黄色背景
            self.setBackground(QBrush(QColor(255, 255, 0, 30)))
            self.setForeground(Qt.GlobalColor.darkGray)
        else:
            # 正常状态 - 透明背景
            self.setBackground(QBrush(QColor(0, 0, 0, 0)))
            self.setForeground(Qt.GlobalColor.black)

    def set_selected(self, selected: bool):
        """设置选择状态"""
        self.is_selected = selected
        self.update_display()

class ElementsWidget(QWidget):
    """元素管理器组件"""

    element_selected = pyqtSignal(str)  # 元素选择信号
    element_visibility_changed = pyqtSignal(str, bool)  # 可见性改变信号
    element_lock_changed = pyqtSignal(str, bool)  # 锁定状态改变信号
    element_order_changed = pyqtSignal(list)  # 元素顺序改变信号
    elements_deleted = pyqtSignal(list)  # 元素删除信号
    element_duplicated = pyqtSignal(str)  # 元素复制信号

    def __init__(self):
        super().__init__()
        self.elements = {}
        self.selected_elements = set()  # 多选元素
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

        self.setup_ui()
        self.setup_connections()

        logger.info("元素管理器组件初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)

        # 搜索和筛选组
        search_group = QGroupBox("🔍 搜索与筛选")
        search_layout = QVBoxLayout(search_group)

        # 搜索框
        search_layout_h = QHBoxLayout()
        search_layout_h.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入元素名称或ID...")
        search_layout_h.addWidget(self.search_input)

        self.clear_search_btn = QPushButton("✖")
        self.clear_search_btn.setToolTip("清除搜索")
        self.clear_search_btn.setMaximumWidth(30)
        search_layout_h.addWidget(self.clear_search_btn)
        search_layout.addLayout(search_layout_h)

        # 类型筛选
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("类型:"))
        self.type_filter = QComboBox()
        self.type_filter.addItem("全部", None)
        for element_type in ElementType:
            self.type_filter.addItem(element_type.value, element_type)
        type_layout.addWidget(self.type_filter)

        # 状态筛选
        self.show_hidden_cb = QCheckBox("显示隐藏")
        self.show_locked_cb = QCheckBox("显示锁定")
        type_layout.addWidget(self.show_hidden_cb)
        type_layout.addWidget(self.show_locked_cb)
        search_layout.addLayout(type_layout)

        # 排序控制
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("排序:"))

        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "名称", "类型", "图层", "创建时间", "大小"
        ])
        self.sort_combo.setCurrentText("名称")
        sort_layout.addWidget(self.sort_combo)

        self.reverse_sort_cb = QCheckBox("倒序")
        sort_layout.addWidget(self.reverse_sort_cb)

        # 视图模式切换
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["列表视图", "缩略图视图", "详细视图"])
        sort_layout.addWidget(self.view_mode_combo)

        sort_layout.addStretch()
        search_layout.addLayout(sort_layout)

        layout.addWidget(search_group)

        # 元素列表组
        list_group = QGroupBox("📋 元素列表")
        list_layout = QVBoxLayout(list_group)

        # 工具栏
        toolbar_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕")
        self.add_btn.setToolTip("添加元素")
        self.add_btn.setMaximumWidth(30)
        toolbar_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setToolTip("删除选中元素")
        self.delete_btn.setMaximumWidth(30)
        toolbar_layout.addWidget(self.delete_btn)

        self.duplicate_btn = QPushButton("📋")
        self.duplicate_btn.setToolTip("复制选中元素")
        self.duplicate_btn.setMaximumWidth(30)
        toolbar_layout.addWidget(self.duplicate_btn)

        # 快速操作下拉菜单
        from PyQt6.QtWidgets import QToolButton, QMenu
        self.quick_actions_btn = QToolButton()
        self.quick_actions_btn.setText("⚡")
        self.quick_actions_btn.setToolTip("快速操作")
        self.quick_actions_btn.setMaximumWidth(30)
        self.quick_actions_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        # 创建快速操作菜单
        quick_menu = QMenu(self)

        # 对齐操作
        align_menu = quick_menu.addMenu("对齐")
        align_menu.addAction("左对齐", lambda: self.align_elements("left"))
        align_menu.addAction("右对齐", lambda: self.align_elements("right"))
        align_menu.addAction("顶部对齐", lambda: self.align_elements("top"))
        align_menu.addAction("底部对齐", lambda: self.align_elements("bottom"))
        align_menu.addAction("水平居中", lambda: self.align_elements("center_h"))
        align_menu.addAction("垂直居中", lambda: self.align_elements("center_v"))

        # 分布操作
        distribute_menu = quick_menu.addMenu("分布")
        distribute_menu.addAction("水平分布", lambda: self.distribute_elements("horizontal"))
        distribute_menu.addAction("垂直分布", lambda: self.distribute_elements("vertical"))

        # 变换操作
        transform_menu = quick_menu.addMenu("变换")
        transform_menu.addAction("水平翻转", lambda: self.flip_elements("horizontal"))
        transform_menu.addAction("垂直翻转", lambda: self.flip_elements("vertical"))
        transform_menu.addAction("顺时针旋转90°", lambda: self.rotate_elements(90))
        transform_menu.addAction("逆时针旋转90°", lambda: self.rotate_elements(-90))

        # 批量样式操作
        style_menu = quick_menu.addMenu("样式")
        style_menu.addAction("复制样式", self.copy_style)
        style_menu.addAction("粘贴样式", self.paste_style)
        style_menu.addAction("清除样式", self.clear_style)

        self.quick_actions_btn.setMenu(quick_menu)
        toolbar_layout.addWidget(self.quick_actions_btn)

        toolbar_layout.addStretch()

        # 批量操作按钮
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setMaximumWidth(50)
        toolbar_layout.addWidget(self.select_all_btn)

        self.select_none_btn = QPushButton("取消")
        self.select_none_btn.setMaximumWidth(50)
        toolbar_layout.addWidget(self.select_none_btn)

        self.visibility_btn = QPushButton("👁️")
        self.visibility_btn.setToolTip("切换选中元素可见性")
        self.visibility_btn.setMaximumWidth(30)
        toolbar_layout.addWidget(self.visibility_btn)

        self.lock_btn = QPushButton("🔒")
        self.lock_btn.setToolTip("切换选中元素锁定")
        self.lock_btn.setMaximumWidth(30)
        toolbar_layout.addWidget(self.lock_btn)

        list_layout.addLayout(toolbar_layout)

        # 元素计数标签
        self.count_label = QLabel("元素: 0")
        list_layout.addWidget(self.count_label)

        # 元素列表
        self.elements_list = QListWidget()
        self.elements_list.setMaximumHeight(250)
        self.elements_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.elements_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)

        # 启用右键菜单
        self.elements_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.elements_list.customContextMenuRequested.connect(self.show_context_menu)

        list_layout.addWidget(self.elements_list)

        layout.addWidget(list_group)
        
        # 图层控制组 - 增强版
        layer_group = QGroupBox("🎭 图层控制")
        layer_layout = QVBoxLayout(layer_group)

        # 图层信息显示
        layer_info_layout = QHBoxLayout()
        layer_info_layout.addWidget(QLabel("当前图层:"))
        self.current_layer_label = QLabel("无选择")
        self.current_layer_label.setStyleSheet("font-weight: bold; color: #007acc;")
        layer_info_layout.addWidget(self.current_layer_label)
        layer_info_layout.addStretch()
        layer_layout.addLayout(layer_info_layout)

        # 图层操作按钮 - 第一行
        layer_btn_layout = QHBoxLayout()

        self.move_up_btn = QPushButton("⬆️ 上移")
        self.move_up_btn.setToolTip("将选中元素向上移动一层")
        self.move_down_btn = QPushButton("⬇️ 下移")
        self.move_down_btn.setToolTip("将选中元素向下移动一层")

        layer_btn_layout.addWidget(self.move_up_btn)
        layer_btn_layout.addWidget(self.move_down_btn)
        layer_layout.addLayout(layer_btn_layout)

        # 图层操作按钮 - 第二行
        layer_btn_layout2 = QHBoxLayout()

        self.to_top_btn = QPushButton("⏫ 置顶")
        self.to_top_btn.setToolTip("将选中元素移动到最顶层")
        self.to_bottom_btn = QPushButton("⏬ 置底")
        self.to_bottom_btn.setToolTip("将选中元素移动到最底层")

        layer_btn_layout2.addWidget(self.to_top_btn)
        layer_btn_layout2.addWidget(self.to_bottom_btn)
        layer_layout.addLayout(layer_btn_layout2)

        # 图层分组功能 - 第三行
        group_layout = QHBoxLayout()

        self.group_btn = QPushButton("📁 分组")
        self.group_btn.setToolTip("将选中元素创建为组")
        self.ungroup_btn = QPushButton("📂 解组")
        self.ungroup_btn.setToolTip("解散选中的组")

        group_layout.addWidget(self.group_btn)
        group_layout.addWidget(self.ungroup_btn)
        layer_layout.addLayout(group_layout)

        # 图层预览功能
        preview_layout = QHBoxLayout()

        self.layer_preview_btn = QPushButton("👁️ 预览")
        self.layer_preview_btn.setToolTip("预览图层结构")
        self.layer_preview_btn.setCheckable(True)

        self.isolate_layer_btn = QPushButton("🔍 隔离")
        self.isolate_layer_btn.setToolTip("隔离显示选中图层")
        self.isolate_layer_btn.setCheckable(True)

        preview_layout.addWidget(self.layer_preview_btn)
        preview_layout.addWidget(self.isolate_layer_btn)
        layer_layout.addLayout(preview_layout)

        # 图层混合模式
        blend_layout = QHBoxLayout()
        blend_layout.addWidget(QLabel("混合:"))

        self.blend_mode_combo = QComboBox()
        self.blend_mode_combo.addItems([
            "正常", "叠加", "柔光", "强光", "颜色减淡",
            "颜色加深", "正片叠底", "滤色", "差值", "排除"
        ])
        self.blend_mode_combo.setToolTip("设置图层混合模式")
        blend_layout.addWidget(self.blend_mode_combo)

        layer_layout.addLayout(blend_layout)

        # 图层不透明度
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("不透明度:"))

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setToolTip("调整图层不透明度")
        opacity_layout.addWidget(self.opacity_slider)

        self.opacity_label = QLabel("100%")
        self.opacity_label.setMinimumWidth(40)
        opacity_layout.addWidget(self.opacity_label)

        layer_layout.addLayout(opacity_layout)

        layout.addWidget(layer_group)

        # 统计信息组
        stats_group = QGroupBox("📊 统计信息")
        stats_layout = QVBoxLayout(stats_group)

        self.stats_label = QLabel("总元素: 0 | 可见: 0 | 锁定: 0")
        stats_layout.addWidget(self.stats_label)

        # 进度条（用于批量操作）
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        stats_layout.addWidget(self.progress_bar)

        layout.addWidget(stats_group)

        # 添加弹性空间
        layout.addStretch()
    
    def setup_connections(self):
        """设置信号连接"""
        # 列表操作
        self.elements_list.currentRowChanged.connect(self.on_element_selected)
        self.elements_list.itemSelectionChanged.connect(self.on_selection_changed)

        # 搜索功能
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.clear_search_btn.clicked.connect(self.clear_search)

        # 工具栏按钮
        self.add_btn.clicked.connect(self.add_element)
        self.delete_btn.clicked.connect(self.delete_selected_elements)
        self.duplicate_btn.clicked.connect(self.duplicate_selected_elements)
        self.visibility_btn.clicked.connect(self.toggle_selected_visibility)
        self.lock_btn.clicked.connect(self.toggle_selected_lock)

        # 批量选择
        self.select_all_btn.clicked.connect(self.select_all_elements)
        self.select_none_btn.clicked.connect(self.select_no_elements)

        # 图层操作
        self.move_up_btn.clicked.connect(self.move_selected_up)
        self.move_down_btn.clicked.connect(self.move_selected_down)
        self.to_top_btn.clicked.connect(self.move_selected_to_top)
        self.to_bottom_btn.clicked.connect(self.move_selected_to_bottom)

        # 图层分组
        self.group_btn.clicked.connect(self.group_selected_elements)
        self.ungroup_btn.clicked.connect(self.ungroup_selected_elements)

        # 图层预览
        self.layer_preview_btn.toggled.connect(self.toggle_layer_preview)
        self.isolate_layer_btn.toggled.connect(self.toggle_layer_isolation)

        # 图层属性
        self.blend_mode_combo.currentTextChanged.connect(self.on_blend_mode_changed)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)

        # 筛选
        self.type_filter.currentTextChanged.connect(self.apply_filter)
        self.show_hidden_cb.toggled.connect(self.apply_filter)
        self.show_locked_cb.toggled.connect(self.apply_filter)

        # 排序和视图
        self.sort_combo.currentTextChanged.connect(self.on_sort_changed)
        self.reverse_sort_cb.toggled.connect(self.on_sort_changed)
        self.view_mode_combo.currentTextChanged.connect(self.on_view_mode_changed)

    # 搜索功能
    def on_search_text_changed(self, text: str):
        """搜索文本改变时的处理"""
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms延迟搜索

    def perform_search(self):
        """执行搜索"""
        search_text = self.search_input.text().strip().lower()

        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            if isinstance(item, ElementListItem):
                element = item.element

                # 搜索元素名称、ID和类型
                matches = (
                    search_text in element.name.lower() or
                    search_text in element.element_id.lower() or
                    search_text in element.element_type.value.lower()
                )

                item.setHidden(not matches if search_text else False)

        self.update_statistics()
        logger.debug(f"搜索完成: '{search_text}'")

    def clear_search(self):
        """清除搜索"""
        self.search_input.clear()

        # 显示所有项目
        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            item.setHidden(False)

        self.apply_filter()
        logger.debug("搜索已清除")

    # 选择功能
    def on_selection_changed(self):
        """选择改变时的处理"""
        selected_items = self.elements_list.selectedItems()
        self.selected_elements.clear()

        for item in selected_items:
            if isinstance(item, ElementListItem):
                self.selected_elements.add(item.element.element_id)
                item.set_selected(True)

        # 更新所有项目的选择状态显示
        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            if isinstance(item, ElementListItem):
                is_selected = item.element.element_id in self.selected_elements
                item.set_selected(is_selected)

        self.update_button_states()
        logger.debug(f"选择了 {len(self.selected_elements)} 个元素")

    def select_all_elements(self):
        """选择所有可见元素"""
        self.elements_list.selectAll()
        logger.debug("已选择所有元素")

    def select_no_elements(self):
        """取消选择所有元素"""
        self.elements_list.clearSelection()
        logger.debug("已取消选择所有元素")

    def update_button_states(self):
        """更新按钮状态"""
        has_selection = len(self.selected_elements) > 0

        # 更新按钮启用状态
        self.delete_btn.setEnabled(has_selection)
        self.duplicate_btn.setEnabled(has_selection)
        self.visibility_btn.setEnabled(has_selection)
        self.lock_btn.setEnabled(has_selection)

        # 更新图层操作按钮
        self.move_up_btn.setEnabled(has_selection)
        self.move_down_btn.setEnabled(has_selection)
        self.to_top_btn.setEnabled(has_selection)
        self.to_bottom_btn.setEnabled(has_selection)

        # 更新按钮文本
        count = len(self.selected_elements)
        if count > 1:
            self.delete_btn.setToolTip(f"删除 {count} 个元素")
            self.duplicate_btn.setToolTip(f"复制 {count} 个元素")
            self.visibility_btn.setToolTip(f"切换 {count} 个元素可见性")
            self.lock_btn.setToolTip(f"切换 {count} 个元素锁定")
        else:
            self.delete_btn.setToolTip("删除选中元素")
            self.duplicate_btn.setToolTip("复制选中元素")
            self.visibility_btn.setToolTip("切换选中元素可见性")
            self.lock_btn.setToolTip("切换选中元素锁定")

    def update_statistics(self):
        """更新统计信息"""
        total_count = len(self.elements)
        visible_count = sum(1 for elem in self.elements.values() if elem.visible)
        locked_count = sum(1 for elem in self.elements.values() if elem.locked)

        # 更新计数标签
        self.count_label.setText(f"元素: {total_count}")

        # 更新统计标签
        self.stats_label.setText(f"总元素: {total_count} | 可见: {visible_count} | 锁定: {locked_count}")

        logger.debug(f"统计信息更新: 总计{total_count}, 可见{visible_count}, 锁定{locked_count}")

    def apply_filter(self):
        """应用筛选条件"""
        selected_type = self.type_filter.currentData()
        show_hidden = self.show_hidden_cb.isChecked()
        show_locked = self.show_locked_cb.isChecked()

        visible_count = 0

        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            if isinstance(item, ElementListItem):
                element = item.element

                # 类型筛选
                type_match = selected_type is None or element.element_type == selected_type

                # 状态筛选
                visibility_match = show_hidden or element.visible
                lock_match = show_locked or not element.locked

                should_show = type_match and visibility_match and lock_match
                item.setHidden(not should_show)

                if should_show:
                    visible_count += 1

        logger.debug(f"筛选完成: 显示 {visible_count} 个元素")

        # 如果有搜索文本，重新应用搜索
        if self.search_input.text().strip():
            self.perform_search()
    
    def add_element(self, element: Element = None):
        """添加元素 - 使用完整对话框"""
        if element is None:
            # 打开添加元素对话框
            from .add_element_dialog import AddElementDialog

            dialog = AddElementDialog(self)
            if dialog.exec() == dialog.DialogCode.Accepted:
                element = dialog.get_element()
                if element is None:
                    logger.warning("对话框返回空元素")
                    return
            else:
                logger.info("用户取消添加元素")
                return

        # 添加到项目管理器（如果可用）
        try:
            if hasattr(self.parent(), 'project_manager'):
                self.parent().project_manager.add_element(element)

            # 使用命令系统（如果可用）
            if hasattr(self.parent(), 'command_manager'):
                from core.commands import AddElementCommand
                command = AddElementCommand(self.parent().project_manager, element)
                self.parent().execute_command(command)
            else:
                # 直接添加到本地列表
                self.elements[element.element_id] = element

        except Exception as e:
            logger.error(f"添加元素到项目失败: {e}")
            # 回退到本地添加
            self.elements[element.element_id] = element

        self.refresh_list()

        # 选择新添加的元素
        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            if isinstance(item, ElementListItem) and item.element.element_id == element.element_id:
                self.elements_list.setCurrentRow(i)
                break

        logger.info(f"添加元素: {element.name} ({element.element_id})")
    
    def delete_element(self):
        """删除选中的元素"""
        current_item = self.elements_list.currentItem()
        if isinstance(current_item, ElementListItem):
            element_id = current_item.element.element_id
            if element_id in self.elements:
                del self.elements[element_id]
                self.refresh_list()
                logger.info(f"删除元素: {element_id}")
    
    def duplicate_element(self):
        """复制选中的元素"""
        current_item = self.elements_list.currentItem()
        if isinstance(current_item, ElementListItem):
            original = current_item.element
            
            # 创建副本
            from core.data_structures import Point
            duplicate = Element(
                name=f"{original.name}_副本",
                element_type=original.element_type,
                content=original.content,
                position=Point(original.position.x + 20, original.position.y + 20)
            )
            
            self.add_element(duplicate)
            logger.info(f"复制元素: {original.name}")
    
    def toggle_visibility(self):
        """切换可见性"""
        current_item = self.elements_list.currentItem()
        if isinstance(current_item, ElementListItem):
            element = current_item.element
            element.visible = not element.visible
            current_item.update_display()
            self.element_visibility_changed.emit(element.element_id, element.visible)
            logger.info(f"切换元素可见性: {element.name} -> {element.visible}")
    
    def toggle_lock(self):
        """切换锁定状态"""
        current_item = self.elements_list.currentItem()
        if isinstance(current_item, ElementListItem):
            element = current_item.element
            element.locked = not element.locked
            current_item.update_display()
            self.element_lock_changed.emit(element.element_id, element.locked)
            logger.info(f"切换元素锁定: {element.name} -> {element.locked}")
    
    def move_element_up(self):
        """上移元素"""
        current_item = self.elements_list.currentItem()
        if not isinstance(current_item, ElementListItem):
            return

        element = current_item.element
        self.selected_elements = {element.element_id}
        self.move_selected_up()

    def move_element_down(self):
        """下移元素"""
        current_item = self.elements_list.currentItem()
        if not isinstance(current_item, ElementListItem):
            return

        element = current_item.element
        self.selected_elements = {element.element_id}
        self.move_selected_down()

    def move_element_to_top(self):
        """置顶元素"""
        current_item = self.elements_list.currentItem()
        if not isinstance(current_item, ElementListItem):
            return

        element = current_item.element
        self.selected_elements = {element.element_id}
        self.move_selected_to_top()

    def move_element_to_bottom(self):
        """置底元素"""
        current_item = self.elements_list.currentItem()
        if not isinstance(current_item, ElementListItem):
            return

        element = current_item.element
        self.selected_elements = {element.element_id}
        self.move_selected_to_bottom()
    
    def apply_filter(self):
        """应用筛选"""
        self.refresh_list()

    def on_sort_changed(self):
        """排序方式改变处理"""
        sort_text = self.sort_combo.currentText()
        sort_map = {
            "名称": "name",
            "类型": "type",
            "图层": "z_index",
            "创建时间": "creation_time",
            "大小": "size"
        }

        self.current_sort_method = sort_map.get(sort_text, "name")
        self.reverse_sort = self.reverse_sort_cb.isChecked()

        self.refresh_list()
        logger.debug(f"排序方式改变: {self.current_sort_method}, 倒序: {self.reverse_sort}")

    def on_view_mode_changed(self):
        """视图模式改变处理"""
        view_mode = self.view_mode_combo.currentText()

        if view_mode == "列表视图":
            self._set_list_view_mode()
        elif view_mode == "缩略图视图":
            self._set_thumbnail_view_mode()
        elif view_mode == "详细视图":
            self._set_detailed_view_mode()

        logger.debug(f"视图模式改变: {view_mode}")

    def _set_list_view_mode(self):
        """设置列表视图模式"""
        self.elements_list.setViewMode(self.elements_list.ViewMode.ListMode)
        self.elements_list.setIconSize(QSize(16, 16))
        self.elements_list.setGridSize(QSize())

    def _set_thumbnail_view_mode(self):
        """设置缩略图视图模式"""
        from PyQt6.QtCore import QSize
        self.elements_list.setViewMode(self.elements_list.ViewMode.IconMode)
        self.elements_list.setIconSize(QSize(64, 64))
        self.elements_list.setGridSize(QSize(80, 80))
        self.elements_list.setResizeMode(self.elements_list.ResizeMode.Adjust)

    def _set_detailed_view_mode(self):
        """设置详细视图模式"""
        self.elements_list.setViewMode(self.elements_list.ViewMode.ListMode)
        self.elements_list.setIconSize(QSize(32, 32))
        self.elements_list.setGridSize(QSize())

        # 在详细视图模式下显示更多信息
        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            if isinstance(item, ElementListItem):
                item.update_display()  # 重新更新显示以包含更多详细信息

    def show_context_menu(self, position):
        """显示右键菜单"""
        try:
            from PyQt6.QtWidgets import QMenu
            from PyQt6.QtGui import QAction

            item = self.elements_list.itemAt(position)
            if not item:
                return

            menu = QMenu(self)

            # 基本操作
            edit_action = QAction("编辑元素", self)
            edit_action.triggered.connect(lambda: self.edit_element(item))
            menu.addAction(edit_action)

            duplicate_action = QAction("复制元素", self)
            duplicate_action.triggered.connect(lambda: self.duplicate_element_item(item))
            menu.addAction(duplicate_action)

            delete_action = QAction("删除元素", self)
            delete_action.triggered.connect(lambda: self.delete_element_item(item))
            menu.addAction(delete_action)

            menu.addSeparator()

            # 可见性和锁定
            if isinstance(item, ElementListItem):
                element = item.element

                visibility_text = "隐藏" if element.visible else "显示"
                visibility_action = QAction(f"{visibility_text}元素", self)
                visibility_action.triggered.connect(lambda: self.toggle_element_visibility(item))
                menu.addAction(visibility_action)

                lock_text = "解锁" if element.locked else "锁定"
                lock_action = QAction(f"{lock_text}元素", self)
                lock_action.triggered.connect(lambda: self.toggle_element_lock(item))
                menu.addAction(lock_action)

                menu.addSeparator()

                # 图层操作
                layer_menu = menu.addMenu("图层操作")

                move_up_action = QAction("上移一层", self)
                move_up_action.triggered.connect(lambda: self.move_element_up(item))
                layer_menu.addAction(move_up_action)

                move_down_action = QAction("下移一层", self)
                move_down_action.triggered.connect(lambda: self.move_element_down(item))
                layer_menu.addAction(move_down_action)

                to_top_action = QAction("置于顶层", self)
                to_top_action.triggered.connect(lambda: self.move_element_to_top(item))
                layer_menu.addAction(to_top_action)

                to_bottom_action = QAction("置于底层", self)
                to_bottom_action.triggered.connect(lambda: self.move_element_to_bottom(item))
                layer_menu.addAction(to_bottom_action)

                menu.addSeparator()

                # 高级操作
                advanced_menu = menu.addMenu("高级操作")

                properties_action = QAction("属性面板", self)
                properties_action.triggered.connect(lambda: self.show_element_properties(item))
                advanced_menu.addAction(properties_action)

                export_action = QAction("导出元素", self)
                export_action.triggered.connect(lambda: self.export_element(item))
                advanced_menu.addAction(export_action)

            # 显示菜单
            menu.exec(self.elements_list.mapToGlobal(position))

        except Exception as e:
            logger.error(f"显示右键菜单失败: {e}")

    def edit_element(self, item):
        """编辑元素"""
        if isinstance(item, ElementListItem):
            # 这里可以打开元素编辑对话框
            logger.info(f"编辑元素: {item.element.name}")

    def duplicate_element_item(self, item):
        """复制指定元素项"""
        if isinstance(item, ElementListItem):
            self.duplicate_element_by_id(item.element.element_id)

    def delete_element_item(self, item):
        """删除指定元素项"""
        if isinstance(item, ElementListItem):
            self.delete_element_by_id(item.element.element_id)

    def toggle_element_visibility(self, item):
        """切换元素可见性"""
        if isinstance(item, ElementListItem):
            element = item.element
            element.visible = not element.visible
            item.update_display()
            logger.info(f"切换元素可见性: {element.name} -> {'可见' if element.visible else '隐藏'}")

    def toggle_element_lock(self, item):
        """切换元素锁定状态"""
        if isinstance(item, ElementListItem):
            element = item.element
            element.locked = not element.locked
            item.update_display()
            logger.info(f"切换元素锁定: {element.name} -> {'锁定' if element.locked else '解锁'}")

    def move_element_up(self, item):
        """上移元素"""
        if isinstance(item, ElementListItem):
            current_row = self.elements_list.row(item)
            if current_row > 0:
                self.elements_list.insertItem(current_row - 1, self.elements_list.takeItem(current_row))
                self.elements_list.setCurrentRow(current_row - 1)

    def move_element_down(self, item):
        """下移元素"""
        if isinstance(item, ElementListItem):
            current_row = self.elements_list.row(item)
            if current_row < self.elements_list.count() - 1:
                self.elements_list.insertItem(current_row + 1, self.elements_list.takeItem(current_row))
                self.elements_list.setCurrentRow(current_row + 1)

    def move_element_to_top(self, item):
        """置顶元素"""
        if isinstance(item, ElementListItem):
            current_row = self.elements_list.row(item)
            self.elements_list.insertItem(0, self.elements_list.takeItem(current_row))
            self.elements_list.setCurrentRow(0)

    def move_element_to_bottom(self, item):
        """置底元素"""
        if isinstance(item, ElementListItem):
            current_row = self.elements_list.row(item)
            self.elements_list.addItem(self.elements_list.takeItem(current_row))
            self.elements_list.setCurrentRow(self.elements_list.count() - 1)

    def show_element_properties(self, item):
        """显示元素属性"""
        if isinstance(item, ElementListItem):
            # 这里可以打开属性面板或发送信号
            self.element_selected.emit(item.element.element_id)
            logger.info(f"显示元素属性: {item.element.name}")

    def export_element(self, item):
        """导出元素"""
        if isinstance(item, ElementListItem):
            # 这里可以实现元素导出功能
            logger.info(f"导出元素: {item.element.name}")

    # ==================== 快速操作方法 ====================

    def align_elements(self, alignment: str):
        """对齐元素"""
        try:
            selected_items = self.elements_list.selectedItems()
            if len(selected_items) < 2:
                logger.warning("对齐操作需要选择至少2个元素")
                return

            elements = [item.element for item in selected_items if isinstance(item, ElementListItem)]
            if not elements:
                return

            # 计算对齐基准
            if alignment == "left":
                min_x = min(e.position.x for e in elements)
                for element in elements:
                    element.position.x = min_x
            elif alignment == "right":
                max_x = max(e.position.x + getattr(e, 'width', 0) for e in elements)
                for element in elements:
                    element.position.x = max_x - getattr(element, 'width', 0)
            elif alignment == "top":
                min_y = min(e.position.y for e in elements)
                for element in elements:
                    element.position.y = min_y
            elif alignment == "bottom":
                max_y = max(e.position.y + getattr(e, 'height', 0) for e in elements)
                for element in elements:
                    element.position.y = max_y - getattr(element, 'height', 0)
            elif alignment == "center_h":
                center_x = sum(e.position.x + getattr(e, 'width', 0) / 2 for e in elements) / len(elements)
                for element in elements:
                    element.position.x = center_x - getattr(element, 'width', 0) / 2
            elif alignment == "center_v":
                center_y = sum(e.position.y + getattr(e, 'height', 0) / 2 for e in elements) / len(elements)
                for element in elements:
                    element.position.y = center_y - getattr(element, 'height', 0) / 2

            # 更新显示
            self.refresh_list()
            logger.info(f"对齐操作完成: {alignment}, 影响 {len(elements)} 个元素")

        except Exception as e:
            logger.error(f"对齐操作失败: {e}")

    def distribute_elements(self, direction: str):
        """分布元素"""
        try:
            selected_items = self.elements_list.selectedItems()
            if len(selected_items) < 3:
                logger.warning("分布操作需要选择至少3个元素")
                return

            elements = [item.element for item in selected_items if isinstance(item, ElementListItem)]
            if not elements:
                return

            if direction == "horizontal":
                # 按X坐标排序
                elements.sort(key=lambda e: e.position.x)

                # 计算总宽度和间距
                total_width = elements[-1].position.x - elements[0].position.x
                if len(elements) > 2:
                    spacing = total_width / (len(elements) - 1)

                    for i, element in enumerate(elements[1:-1], 1):
                        element.position.x = elements[0].position.x + spacing * i

            elif direction == "vertical":
                # 按Y坐标排序
                elements.sort(key=lambda e: e.position.y)

                # 计算总高度和间距
                total_height = elements[-1].position.y - elements[0].position.y
                if len(elements) > 2:
                    spacing = total_height / (len(elements) - 1)

                    for i, element in enumerate(elements[1:-1], 1):
                        element.position.y = elements[0].position.y + spacing * i

            # 更新显示
            self.refresh_list()
            logger.info(f"分布操作完成: {direction}, 影响 {len(elements)} 个元素")

        except Exception as e:
            logger.error(f"分布操作失败: {e}")

    def flip_elements(self, direction: str):
        """翻转元素"""
        try:
            selected_items = self.elements_list.selectedItems()
            elements = [item.element for item in selected_items if isinstance(item, ElementListItem)]

            for element in elements:
                if hasattr(element, 'transform'):
                    if direction == "horizontal":
                        element.transform.scale_x *= -1
                    elif direction == "vertical":
                        element.transform.scale_y *= -1

            # 更新显示
            self.refresh_list()
            logger.info(f"翻转操作完成: {direction}, 影响 {len(elements)} 个元素")

        except Exception as e:
            logger.error(f"翻转操作失败: {e}")

    def rotate_elements(self, angle: float):
        """旋转元素"""
        try:
            selected_items = self.elements_list.selectedItems()
            elements = [item.element for item in selected_items if isinstance(item, ElementListItem)]

            for element in elements:
                if hasattr(element, 'transform'):
                    element.transform.rotation = (element.transform.rotation + angle) % 360

            # 更新显示
            self.refresh_list()
            logger.info(f"旋转操作完成: {angle}°, 影响 {len(elements)} 个元素")

        except Exception as e:
            logger.error(f"旋转操作失败: {e}")

    def copy_style(self):
        """复制样式"""
        try:
            selected_items = self.elements_list.selectedItems()
            if len(selected_items) != 1:
                logger.warning("复制样式需要选择一个元素")
                return

            element = selected_items[0].element
            if hasattr(element, 'style'):
                self.copied_style = element.style
                logger.info(f"已复制样式: {element.name}")
            else:
                logger.warning("选中元素没有样式信息")

        except Exception as e:
            logger.error(f"复制样式失败: {e}")

    def paste_style(self):
        """粘贴样式"""
        try:
            if not hasattr(self, 'copied_style') or not self.copied_style:
                logger.warning("没有复制的样式")
                return

            selected_items = self.elements_list.selectedItems()
            elements = [item.element for item in selected_items if isinstance(item, ElementListItem)]

            for element in elements:
                if hasattr(element, 'style'):
                    element.style = self.copied_style.copy() if hasattr(self.copied_style, 'copy') else self.copied_style

            # 更新显示
            self.refresh_list()
            logger.info(f"粘贴样式完成, 影响 {len(elements)} 个元素")

        except Exception as e:
            logger.error(f"粘贴样式失败: {e}")

    def clear_style(self):
        """清除样式"""
        try:
            selected_items = self.elements_list.selectedItems()
            elements = [item.element for item in selected_items if isinstance(item, ElementListItem)]

            for element in elements:
                if hasattr(element, 'style'):
                    element.style = None

            # 更新显示
            self.refresh_list()
            logger.info(f"清除样式完成, 影响 {len(elements)} 个元素")

        except Exception as e:
            logger.error(f"清除样式失败: {e}")

    # ==================== 图层控制增强功能 ====================

    def group_selected_elements(self):
        """将选中元素创建为组"""
        try:
            selected_items = self.elements_list.selectedItems()
            if len(selected_items) < 2:
                logger.warning("分组需要选择至少2个元素")
                return

            elements = [item.element for item in selected_items if isinstance(item, ElementListItem)]
            if not elements:
                return

            # 创建组元素
            from core.data_structures import Element, ElementType, Point
            import uuid

            group_id = str(uuid.uuid4())
            group_name = f"组_{len([e for e in self.elements.values() if e.element_type == ElementType.GROUP]) + 1}"

            # 计算组的边界
            min_x = min(e.position.x for e in elements)
            min_y = min(e.position.y for e in elements)
            max_x = max(e.position.x + getattr(e, 'width', 0) for e in elements)
            max_y = max(e.position.y + getattr(e, 'height', 0) for e in elements)

            group_element = Element(
                element_id=group_id,
                name=group_name,
                element_type=ElementType.GROUP,
                position=Point(min_x, min_y)
            )

            # 设置组的大小
            group_element.width = max_x - min_x
            group_element.height = max_y - min_y

            # 将元素添加到组中
            group_element.children = [e.element_id for e in elements]

            # 调整子元素的相对位置
            for element in elements:
                element.position.x -= min_x
                element.position.y -= min_y
                element.parent_id = group_id

            # 添加组到元素列表
            self.elements[group_id] = group_element

            # 从列表中移除原始元素（它们现在是组的子元素）
            for element in elements:
                if element.element_id in self.elements:
                    del self.elements[element.element_id]

            self.refresh_list()
            logger.info(f"创建组成功: {group_name}, 包含 {len(elements)} 个元素")

        except Exception as e:
            logger.error(f"创建组失败: {e}")

    def ungroup_selected_elements(self):
        """解散选中的组"""
        try:
            selected_items = self.elements_list.selectedItems()
            groups = [item.element for item in selected_items
                     if isinstance(item, ElementListItem) and item.element.element_type == ElementType.GROUP]

            if not groups:
                logger.warning("没有选中的组可以解散")
                return

            for group in groups:
                # 获取组中的子元素
                if hasattr(group, 'children') and group.children:
                    # 恢复子元素的绝对位置
                    for child_id in group.children:
                        # 这里需要从某个地方获取子元素，简化实现
                        logger.info(f"解散组中的子元素: {child_id}")

                # 从元素列表中移除组
                if group.element_id in self.elements:
                    del self.elements[group.element_id]

            self.refresh_list()
            logger.info(f"解散组完成, 影响 {len(groups)} 个组")

        except Exception as e:
            logger.error(f"解散组失败: {e}")

    def toggle_layer_preview(self, enabled: bool):
        """切换图层预览"""
        try:
            if enabled:
                # 启用图层预览模式
                self._show_layer_preview()
                logger.info("图层预览模式已启用")
            else:
                # 禁用图层预览模式
                self._hide_layer_preview()
                logger.info("图层预览模式已禁用")

        except Exception as e:
            logger.error(f"切换图层预览失败: {e}")

    def _show_layer_preview(self):
        """显示图层预览"""
        # 为每个元素添加图层边框显示
        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            if isinstance(item, ElementListItem):
                # 添加图层边框样式
                item.setBackground(QBrush(QColor(0, 123, 255, 30)))

    def _hide_layer_preview(self):
        """隐藏图层预览"""
        # 移除图层边框显示
        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            if isinstance(item, ElementListItem):
                item._update_item_style()  # 恢复正常样式

    def toggle_layer_isolation(self, enabled: bool):
        """切换图层隔离"""
        try:
            selected_items = self.elements_list.selectedItems()

            if enabled:
                # 隔离选中的图层
                selected_ids = {item.element.element_id for item in selected_items if isinstance(item, ElementListItem)}

                for i in range(self.elements_list.count()):
                    item = self.elements_list.item(i)
                    if isinstance(item, ElementListItem):
                        # 隐藏非选中的元素
                        is_selected = item.element.element_id in selected_ids
                        item.setHidden(not is_selected)

                logger.info(f"图层隔离已启用, 显示 {len(selected_ids)} 个图层")
            else:
                # 取消隔离，显示所有元素
                for i in range(self.elements_list.count()):
                    item = self.elements_list.item(i)
                    if isinstance(item, ElementListItem):
                        item.setHidden(False)

                logger.info("图层隔离已禁用")

        except Exception as e:
            logger.error(f"切换图层隔离失败: {e}")

    def on_blend_mode_changed(self, blend_mode: str):
        """混合模式改变处理"""
        try:
            selected_items = self.elements_list.selectedItems()
            elements = [item.element for item in selected_items if isinstance(item, ElementListItem)]

            for element in elements:
                # 设置混合模式（需要在元素数据结构中添加支持）
                if not hasattr(element, 'blend_mode'):
                    element.blend_mode = blend_mode
                else:
                    element.blend_mode = blend_mode

            logger.info(f"混合模式已更改: {blend_mode}, 影响 {len(elements)} 个元素")

        except Exception as e:
            logger.error(f"更改混合模式失败: {e}")

    def on_opacity_changed(self, value: int):
        """不透明度改变处理"""
        try:
            # 更新标签显示
            self.opacity_label.setText(f"{value}%")

            selected_items = self.elements_list.selectedItems()
            elements = [item.element for item in selected_items if isinstance(item, ElementListItem)]

            opacity = value / 100.0
            for element in elements:
                # 设置不透明度（需要在元素数据结构中添加支持）
                if not hasattr(element, 'opacity'):
                    element.opacity = opacity
                else:
                    element.opacity = opacity

            if elements:
                logger.debug(f"不透明度已更改: {value}%, 影响 {len(elements)} 个元素")

        except Exception as e:
            logger.error(f"更改不透明度失败: {e}")

    def update_layer_info(self):
        """更新图层信息显示"""
        try:
            selected_items = self.elements_list.selectedItems()

            if not selected_items:
                self.current_layer_label.setText("无选择")
                return

            if len(selected_items) == 1:
                item = selected_items[0]
                if isinstance(item, ElementListItem):
                    element = item.element
                    layer_info = f"{element.name} (图层 {getattr(element, 'z_index', 0)})"
                    self.current_layer_label.setText(layer_info)
            else:
                self.current_layer_label.setText(f"多选 ({len(selected_items)} 个)")

        except Exception as e:
            logger.error(f"更新图层信息失败: {e}")
    
    def refresh_list(self):
        """刷新元素列表"""
        self.elements_list.clear()
        
        # 获取筛选条件
        type_filter = self.type_filter.currentData()
        show_visible_only = self.show_visible_only.isChecked()
        show_unlocked_only = self.show_unlocked_only.isChecked()
        
        # 筛选元素
        filtered_elements = []
        for element in self.elements.values():
            # 类型筛选
            if type_filter is not None and element.element_type != type_filter:
                continue
            
            # 可见性筛选
            if show_visible_only and not element.visible:
                continue
            
            # 锁定状态筛选
            if show_unlocked_only and element.locked:
                continue
            
            filtered_elements.append(element)
        
        # 智能排序 - 支持多种排序方式
        sort_method = getattr(self, 'current_sort_method', 'name')
        reverse_order = getattr(self, 'reverse_sort', False)

        if sort_method == 'name':
            filtered_elements.sort(key=lambda e: e.name.lower(), reverse=reverse_order)
        elif sort_method == 'type':
            filtered_elements.sort(key=lambda e: e.element_type.value, reverse=reverse_order)
        elif sort_method == 'z_index':
            filtered_elements.sort(key=lambda e: getattr(e, 'z_index', 0), reverse=reverse_order)
        elif sort_method == 'creation_time':
            filtered_elements.sort(key=lambda e: getattr(e, 'created_at', ''), reverse=reverse_order)
        elif sort_method == 'size':
            def get_element_size(e):
                if hasattr(e, 'size') and e.size:
                    return e.size.width * e.size.height
                return 0
            filtered_elements.sort(key=get_element_size, reverse=reverse_order)

        # 添加到列表 - 增强版
        for element in filtered_elements:
            item = ElementListItem(element)

            # 设置拖拽数据
            item.setData(Qt.ItemDataRole.UserRole, element.element_id)

            # 添加右键菜单支持
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable |
                         Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled)

            self.elements_list.addItem(item)

        # 更新统计信息
        self.update_statistics()
    
    def on_element_selected(self, row: int):
        """元素选择处理"""
        if row >= 0:
            item = self.elements_list.item(row)
            if isinstance(item, ElementListItem):
                self.element_selected.emit(item.element.element_id)

        # 更新图层信息显示
        self.update_layer_info()
    
    def select_element(self, element_id: str):
        """选择指定元素"""
        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            if isinstance(item, ElementListItem) and item.element.element_id == element_id:
                self.elements_list.setCurrentRow(i)
                break
    
    def update_element(self, element: Element):
        """更新元素"""
        self.elements[element.element_id] = element
        
        # 更新列表项显示
        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            if isinstance(item, ElementListItem) and item.element.element_id == element.element_id:
                item.element = element
                item.update_display()
                break

    # 批量操作方法
    def delete_selected_elements(self):
        """删除选中的元素"""
        if not self.selected_elements:
            logger.warning("没有选中的元素可删除")
            return

        # 确认删除
        count = len(self.selected_elements)
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 {count} 个选中的元素吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 删除元素
        deleted_ids = list(self.selected_elements)

        try:
            # 显示进度
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(count)

            for i, element_id in enumerate(deleted_ids):
                if element_id in self.elements:
                    del self.elements[element_id]

                # 从列表中移除
                for j in range(self.elements_list.count()):
                    item = self.elements_list.item(j)
                    if isinstance(item, ElementListItem) and item.element.element_id == element_id:
                        self.elements_list.takeItem(j)
                        break

                self.progress_bar.setValue(i + 1)

            # 清除选择
            self.selected_elements.clear()

            # 发送删除信号
            self.elements_deleted.emit(deleted_ids)

            # 更新统计和按钮状态
            self.update_statistics()
            self.update_button_states()

            logger.info(f"已删除 {count} 个元素")

        except Exception as e:
            logger.error(f"删除元素失败: {e}")
            QMessageBox.warning(self, "错误", f"删除元素失败: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)

    def duplicate_selected_elements(self):
        """复制选中的元素"""
        if not self.selected_elements:
            logger.warning("没有选中的元素可复制")
            return

        count = len(self.selected_elements)

        try:
            # 显示进度
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(count)

            duplicated_ids = []

            for i, element_id in enumerate(self.selected_elements):
                if element_id in self.elements:
                    original = self.elements[element_id]

                    # 创建副本
                    duplicate = Element(
                        name=f"{original.name}_副本",
                        element_type=original.element_type,
                        content=original.content,
                        position=Point(original.position.x + 20, original.position.y + 20),
                        style=original.style,
                        visible=original.visible,
                        locked=False  # 副本默认不锁定
                    )

                    # 添加到列表
                    self.elements[duplicate.element_id] = duplicate

                    # 添加到UI列表
                    item = ElementListItem(duplicate)
                    self.elements_list.addItem(item)

                    duplicated_ids.append(duplicate.element_id)

                    # 发送复制信号
                    self.element_duplicated.emit(duplicate.element_id)

                self.progress_bar.setValue(i + 1)

            # 更新统计
            self.update_statistics()

            logger.info(f"已复制 {count} 个元素")

        except Exception as e:
            logger.error(f"复制元素失败: {e}")
            QMessageBox.warning(self, "错误", f"复制元素失败: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)

    def toggle_selected_visibility(self):
        """切换选中元素的可见性"""
        if not self.selected_elements:
            logger.warning("没有选中的元素可切换可见性")
            return

        # 确定新的可见性状态（如果所有选中元素都可见，则隐藏；否则显示）
        all_visible = all(self.elements[eid].visible for eid in self.selected_elements if eid in self.elements)
        new_visibility = not all_visible

        count = 0
        for element_id in self.selected_elements:
            if element_id in self.elements:
                element = self.elements[element_id]
                element.visible = new_visibility

                # 发送可见性改变信号
                self.element_visibility_changed.emit(element_id, new_visibility)
                count += 1

        # 更新显示
        self.refresh_list()
        self.update_statistics()

        action = "显示" if new_visibility else "隐藏"
        logger.info(f"已{action} {count} 个元素")

    def toggle_selected_lock(self):
        """切换选中元素的锁定状态"""
        if not self.selected_elements:
            logger.warning("没有选中的元素可切换锁定状态")
            return

        # 确定新的锁定状态（如果所有选中元素都锁定，则解锁；否则锁定）
        all_locked = all(self.elements[eid].locked for eid in self.selected_elements if eid in self.elements)
        new_lock_state = not all_locked

        count = 0
        for element_id in self.selected_elements:
            if element_id in self.elements:
                element = self.elements[element_id]
                element.locked = new_lock_state

                # 发送锁定状态改变信号
                self.element_lock_changed.emit(element_id, new_lock_state)
                count += 1

        # 更新显示
        self.refresh_list()
        self.update_statistics()

        action = "锁定" if new_lock_state else "解锁"
        logger.info(f"已{action} {count} 个元素")

    def refresh_list(self):
        """刷新列表显示"""
        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            if isinstance(item, ElementListItem):
                item.update_display()

    # 图层操作的批量版本
    def move_selected_up(self):
        """上移选中元素"""
        if not self.selected_elements:
            logger.warning("没有选中的元素可上移")
            return

        try:
            # 获取所有元素的Z-index
            all_z_indices = []
            for element in self.elements.values():
                z_index = getattr(element, 'z_index', 0)
                all_z_indices.append(z_index)

            if not all_z_indices:
                return

            # 对选中的元素进行上移
            moved_count = 0
            for element_id in self.selected_elements:
                if element_id in self.elements:
                    element = self.elements[element_id]
                    current_z = getattr(element, 'z_index', 0)

                    # 找到比当前Z-index大的最小值
                    higher_indices = [z for z in all_z_indices if z > current_z]
                    if higher_indices:
                        new_z = min(higher_indices)

                        # 使用命令系统（如果可用）
                        if hasattr(self.parent(), 'command_manager'):
                            from core.commands import ChangeLayerOrderCommand
                            command = ChangeLayerOrderCommand(
                                self.parent().project_manager, element_id, current_z, new_z
                            )
                            if self.parent().execute_command(command):
                                moved_count += 1
                        else:
                            # 直接修改
                            element.z_index = new_z
                            moved_count += 1

            # 更新显示
            self.refresh_list()
            self.element_order_changed.emit(list(self.selected_elements))

            logger.info(f"上移了 {moved_count} 个元素")

        except Exception as e:
            logger.error(f"上移元素失败: {e}")
            QMessageBox.warning(self, "错误", f"上移元素失败: {str(e)}")

    def move_selected_down(self):
        """下移选中元素"""
        if not self.selected_elements:
            logger.warning("没有选中的元素可下移")
            return

        try:
            # 获取所有元素的Z-index
            all_z_indices = []
            for element in self.elements.values():
                z_index = getattr(element, 'z_index', 0)
                all_z_indices.append(z_index)

            if not all_z_indices:
                return

            # 对选中的元素进行下移
            moved_count = 0
            for element_id in self.selected_elements:
                if element_id in self.elements:
                    element = self.elements[element_id]
                    current_z = getattr(element, 'z_index', 0)

                    # 找到比当前Z-index小的最大值
                    lower_indices = [z for z in all_z_indices if z < current_z]
                    if lower_indices:
                        new_z = max(lower_indices)

                        # 使用命令系统（如果可用）
                        if hasattr(self.parent(), 'command_manager'):
                            from core.commands import ChangeLayerOrderCommand
                            command = ChangeLayerOrderCommand(
                                self.parent().project_manager, element_id, current_z, new_z
                            )
                            if self.parent().execute_command(command):
                                moved_count += 1
                        else:
                            # 直接修改
                            element.z_index = new_z
                            moved_count += 1

            # 更新显示
            self.refresh_list()
            self.element_order_changed.emit(list(self.selected_elements))

            logger.info(f"下移了 {moved_count} 个元素")

        except Exception as e:
            logger.error(f"下移元素失败: {e}")
            QMessageBox.warning(self, "错误", f"下移元素失败: {str(e)}")

    def move_selected_to_top(self):
        """置顶选中元素"""
        if not self.selected_elements:
            logger.warning("没有选中的元素可置顶")
            return

        try:
            # 获取当前最大的Z-index
            max_z_index = 0
            for element in self.elements.values():
                z_index = getattr(element, 'z_index', 0)
                max_z_index = max(max_z_index, z_index)

            # 对选中的元素进行置顶
            moved_count = 0
            for element_id in self.selected_elements:
                if element_id in self.elements:
                    element = self.elements[element_id]
                    current_z = getattr(element, 'z_index', 0)
                    new_z = max_z_index + 1

                    # 使用命令系统（如果可用）
                    if hasattr(self.parent(), 'command_manager'):
                        from core.commands import ChangeLayerOrderCommand
                        command = ChangeLayerOrderCommand(
                            self.parent().project_manager, element_id, current_z, new_z
                        )
                        if self.parent().execute_command(command):
                            moved_count += 1
                            max_z_index = new_z  # 更新最大值，避免重叠
                    else:
                        # 直接修改
                        element.z_index = new_z
                        moved_count += 1
                        max_z_index = new_z

            # 更新显示
            self.refresh_list()
            self.element_order_changed.emit(list(self.selected_elements))

            logger.info(f"置顶了 {moved_count} 个元素")

        except Exception as e:
            logger.error(f"置顶元素失败: {e}")
            QMessageBox.warning(self, "错误", f"置顶元素失败: {str(e)}")

    def move_selected_to_bottom(self):
        """置底选中元素"""
        if not self.selected_elements:
            logger.warning("没有选中的元素可置底")
            return

        try:
            # 获取当前最小的Z-index
            min_z_index = 0
            for element in self.elements.values():
                z_index = getattr(element, 'z_index', 0)
                min_z_index = min(min_z_index, z_index)

            # 对选中的元素进行置底
            moved_count = 0
            for element_id in self.selected_elements:
                if element_id in self.elements:
                    element = self.elements[element_id]
                    current_z = getattr(element, 'z_index', 0)
                    new_z = min_z_index - 1

                    # 使用命令系统（如果可用）
                    if hasattr(self.parent(), 'command_manager'):
                        from core.commands import ChangeLayerOrderCommand
                        command = ChangeLayerOrderCommand(
                            self.parent().project_manager, element_id, current_z, new_z
                        )
                        if self.parent().execute_command(command):
                            moved_count += 1
                            min_z_index = new_z  # 更新最小值，避免重叠
                    else:
                        # 直接修改
                        element.z_index = new_z
                        moved_count += 1
                        min_z_index = new_z

            # 更新显示
            self.refresh_list()
            self.element_order_changed.emit(list(self.selected_elements))

            logger.info(f"置底了 {moved_count} 个元素")

        except Exception as e:
            logger.error(f"置底元素失败: {e}")
            QMessageBox.warning(self, "错误", f"置底元素失败: {str(e)}")

    # ========== 鼠标事件处理 ==========

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self.handle_left_press(event)
            elif event.button() == Qt.MouseButton.RightButton:
                self.handle_right_press(event)

            super().mousePressEvent(event)

        except Exception as e:
            logger.error(f"鼠标按下事件处理失败: {e}")

    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                # 双击编辑元素名称
                self.handle_double_click(event)

            super().mouseDoubleClickEvent(event)

        except Exception as e:
            logger.error(f"鼠标双击事件处理失败: {e}")

    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        try:
            if event.mimeData().hasText():
                event.acceptProposedAction()
            else:
                event.ignore()

        except Exception as e:
            logger.error(f"拖拽进入事件处理失败: {e}")

    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        try:
            if event.mimeData().hasText():
                event.acceptProposedAction()
            else:
                event.ignore()

        except Exception as e:
            logger.error(f"拖拽移动事件处理失败: {e}")

    def dropEvent(self, event):
        """拖拽放下事件"""
        try:
            if event.mimeData().hasText():
                # 处理拖拽放下的元素
                self.handle_drop(event)
                event.acceptProposedAction()
            else:
                event.ignore()

        except Exception as e:
            logger.error(f"拖拽放下事件处理失败: {e}")

    def handle_left_press(self, event):
        """处理左键按下"""
        try:
            # 查找点击的元素项
            item = self.get_item_at_position(event.position())

            if item:
                element_id = item.data(Qt.ItemDataRole.UserRole)

                # 检查修饰键
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    # Ctrl+点击：切换选择状态
                    self.toggle_element_selection(element_id)
                elif event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    # Shift+点击：范围选择
                    self.range_select_to_element(element_id)
                else:
                    # 普通点击：单选
                    self.select_single_element(element_id)
            else:
                # 点击空白区域，清除选择
                self.clear_selection()

        except Exception as e:
            logger.error(f"左键按下处理失败: {e}")

    def handle_right_press(self, event):
        """处理右键按下"""
        try:
            # 查找点击的元素项
            item = self.get_item_at_position(event.position())

            if item:
                element_id = item.data(Qt.ItemDataRole.UserRole)
                # 如果右键的元素没有被选中，先选中它
                if element_id not in self.selected_elements:
                    self.select_single_element(element_id)

            # 显示上下文菜单
            self.show_context_menu(event.globalPosition().toPoint())

        except Exception as e:
            logger.error(f"右键按下处理失败: {e}")

    def handle_double_click(self, event):
        """处理双击"""
        try:
            # 查找双击的元素项
            item = self.get_item_at_position(event.position())

            if item:
                element_id = item.data(Qt.ItemDataRole.UserRole)
                # 进入元素名称编辑模式
                self.edit_element_name(element_id)

        except Exception as e:
            logger.error(f"双击处理失败: {e}")

    def handle_drop(self, event):
        """处理拖拽放下"""
        try:
            # 获取拖拽的数据
            mime_data = event.mimeData()

            if mime_data.hasText():
                # 解析拖拽的元素数据
                data = mime_data.text()

                # 获取放下位置
                drop_position = event.position()
                target_item = self.get_item_at_position(drop_position)

                if target_item:
                    target_element_id = target_item.data(Qt.ItemDataRole.UserRole)
                    # 重新排序元素
                    self.reorder_elements_by_drop(data, target_element_id)

        except Exception as e:
            logger.error(f"拖拽放下处理失败: {e}")

    def get_item_at_position(self, position):
        """获取指定位置的列表项"""
        try:
            # 转换为整数坐标
            point = position.toPoint()

            # 查找列表项
            if hasattr(self, 'element_list'):
                return self.element_list.itemAt(point)
            return None

        except Exception as e:
            logger.error(f"获取位置项失败: {e}")
            return None

    def toggle_element_selection(self, element_id: str):
        """切换元素选择状态"""
        try:
            if element_id in self.selected_elements:
                self.selected_elements.remove(element_id)
            else:
                self.selected_elements.add(element_id)

            self.update_selection_display()
            self.element_selected.emit(element_id)

        except Exception as e:
            logger.error(f"切换元素选择状态失败: {e}")

    def range_select_to_element(self, element_id: str):
        """范围选择到指定元素"""
        try:
            # 获取当前选择的最后一个元素
            if self.selected_elements:
                last_selected = list(self.selected_elements)[-1]

                # 获取两个元素在列表中的位置
                start_index = self.get_element_index(last_selected)
                end_index = self.get_element_index(element_id)

                if start_index is not None and end_index is not None:
                    # 选择范围内的所有元素
                    min_index = min(start_index, end_index)
                    max_index = max(start_index, end_index)

                    for i in range(min_index, max_index + 1):
                        element_at_index = self.get_element_at_index(i)
                        if element_at_index:
                            self.selected_elements.add(element_at_index)

                    self.update_selection_display()
            else:
                # 如果没有选择，直接选择当前元素
                self.select_single_element(element_id)

        except Exception as e:
            logger.error(f"范围选择失败: {e}")

    def select_single_element(self, element_id: str):
        """单选元素"""
        try:
            self.selected_elements.clear()
            self.selected_elements.add(element_id)
            self.update_selection_display()
            self.element_selected.emit(element_id)

        except Exception as e:
            logger.error(f"单选元素失败: {e}")

    def clear_selection(self):
        """清除选择"""
        try:
            self.selected_elements.clear()
            self.update_selection_display()

        except Exception as e:
            logger.error(f"清除选择失败: {e}")

    def update_selection_display(self):
        """更新选择显示"""
        try:
            # 更新列表项的选择状态显示
            if hasattr(self, 'element_list'):
                for i in range(self.element_list.count()):
                    item = self.element_list.item(i)
                    if item:
                        element_id = item.data(Qt.ItemDataRole.UserRole)
                        is_selected = element_id in self.selected_elements

                        # 更新项的选择状态
                        item.setSelected(is_selected)

                        # 更新背景颜色
                        if is_selected:
                            item.setBackground(QColor(100, 150, 255, 100))
                        else:
                            item.setBackground(QColor(255, 255, 255, 0))

        except Exception as e:
            logger.error(f"更新选择显示失败: {e}")

    def edit_element_name(self, element_id: str):
        """编辑元素名称"""
        try:
            if element_id in self.elements:
                element = self.elements[element_id]
                current_name = element.name

                # 弹出输入对话框
                from PyQt6.QtWidgets import QInputDialog

                new_name, ok = QInputDialog.getText(
                    self, "编辑元素名称", "请输入新的元素名称:",
                    text=current_name
                )

                if ok and new_name.strip():
                    # 更新元素名称
                    element.name = new_name.strip()
                    self.refresh_list()
                    logger.info(f"元素名称已更新: {element_id} -> {new_name}")

        except Exception as e:
            logger.error(f"编辑元素名称失败: {e}")

    def get_element_index(self, element_id: str) -> Optional[int]:
        """获取元素在列表中的索引"""
        try:
            if hasattr(self, 'element_list'):
                for i in range(self.element_list.count()):
                    item = self.element_list.item(i)
                    if item and item.data(Qt.ItemDataRole.UserRole) == element_id:
                        return i
            return None

        except Exception as e:
            logger.error(f"获取元素索引失败: {e}")
            return None

    def get_element_at_index(self, index: int) -> Optional[str]:
        """获取指定索引的元素ID"""
        try:
            if hasattr(self, 'element_list') and 0 <= index < self.element_list.count():
                item = self.element_list.item(index)
                if item:
                    return item.data(Qt.ItemDataRole.UserRole)
            return None

        except Exception as e:
            logger.error(f"获取索引元素失败: {e}")
            return None

    def reorder_elements_by_drop(self, drag_data: str, target_element_id: str):
        """通过拖拽重新排序元素"""
        try:
            # TODO: 实现拖拽重排序逻辑
            logger.info(f"拖拽重排序: {drag_data} -> {target_element_id}")

        except Exception as e:
            logger.error(f"拖拽重排序失败: {e}")

    def show_context_menu(self, global_pos):
        """显示上下文菜单"""
        try:
            from PyQt6.QtWidgets import QMenu

            menu = QMenu(self)

            if self.selected_elements:
                # 有选择的元素时的菜单
                if len(self.selected_elements) == 1:
                    element_id = list(self.selected_elements)[0]

                    # 单个元素菜单
                    edit_name_action = menu.addAction("重命名")
                    edit_name_action.triggered.connect(lambda: self.edit_element_name(element_id))

                    duplicate_action = menu.addAction("复制")
                    duplicate_action.triggered.connect(lambda: self.duplicate_element(element_id))
                else:
                    # 多个元素菜单
                    group_action = menu.addAction(f"组合 ({len(self.selected_elements)} 个元素)")
                    group_action.triggered.connect(self.group_selected_elements)

                menu.addSeparator()

                # 通用操作
                delete_action = menu.addAction("删除")
                delete_action.triggered.connect(self.delete_selected_elements)

                menu.addSeparator()

                # 层级操作
                bring_front_action = menu.addAction("置于顶层")
                bring_front_action.triggered.connect(self.bring_to_front)

                send_back_action = menu.addAction("置于底层")
                send_back_action.triggered.connect(self.send_to_back)

                menu.addSeparator()

                # 可见性和锁定
                toggle_visibility_action = menu.addAction("切换可见性")
                toggle_visibility_action.triggered.connect(self.toggle_selected_visibility)

                toggle_lock_action = menu.addAction("切换锁定")
                toggle_lock_action.triggered.connect(self.toggle_selected_lock)
            else:
                # 没有选择时的菜单
                select_all_action = menu.addAction("全选")
                select_all_action.triggered.connect(self.select_all_elements)

                menu.addSeparator()

                # 添加元素
                add_text_action = menu.addAction("添加文本")
                add_text_action.triggered.connect(self.add_text_element)

                add_shape_action = menu.addAction("添加形状")
                add_shape_action.triggered.connect(self.add_shape_element)

                add_image_action = menu.addAction("添加图片")
                add_image_action.triggered.connect(self.add_image_element)

            menu.exec(global_pos)

        except Exception as e:
            logger.error(f"显示上下文菜单失败: {e}")

    def duplicate_element(self, element_id: str):
        """复制元素"""
        try:
            logger.info(f"复制元素: {element_id}")
            # TODO: 实现元素复制逻辑

        except Exception as e:
            logger.error(f"复制元素失败: {e}")

    def group_selected_elements(self):
        """组合选中的元素"""
        try:
            logger.info(f"组合 {len(self.selected_elements)} 个元素")
            # TODO: 实现元素组合逻辑

        except Exception as e:
            logger.error(f"组合元素失败: {e}")

    def delete_selected_elements(self):
        """删除选中的元素"""
        try:
            if self.selected_elements:
                # 确认删除
                from PyQt6.QtWidgets import QMessageBox

                reply = QMessageBox.question(
                    self, "确认删除",
                    f"确定要删除 {len(self.selected_elements)} 个元素吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # 删除元素
                    for element_id in list(self.selected_elements):
                        self.remove_element(element_id)

                    self.selected_elements.clear()
                    logger.info("已删除选中的元素")

        except Exception as e:
            logger.error(f"删除选中元素失败: {e}")

    def toggle_selected_visibility(self):
        """切换选中元素的可见性"""
        try:
            for element_id in self.selected_elements:
                if element_id in self.elements:
                    element = self.elements[element_id]
                    element.visible = not element.visible
                    self.element_visibility_changed.emit(element_id, element.visible)

            self.refresh_list()
            logger.info("已切换选中元素的可见性")

        except Exception as e:
            logger.error(f"切换可见性失败: {e}")

    def toggle_selected_lock(self):
        """切换选中元素的锁定状态"""
        try:
            for element_id in self.selected_elements:
                if element_id in self.elements:
                    element = self.elements[element_id]
                    element.locked = not element.locked
                    self.element_lock_changed.emit(element_id, element.locked)

            self.refresh_list()
            logger.info("已切换选中元素的锁定状态")

        except Exception as e:
            logger.error(f"切换锁定状态失败: {e}")

    def select_all_elements(self):
        """全选元素"""
        try:
            self.selected_elements = set(self.elements.keys())
            self.update_selection_display()
            logger.info(f"已全选 {len(self.selected_elements)} 个元素")

        except Exception as e:
            logger.error(f"全选元素失败: {e}")

    def add_text_element(self):
        """添加文本元素"""
        try:
            logger.info("添加文本元素")
            # TODO: 实现文本元素添加逻辑

        except Exception as e:
            logger.error(f"添加文本元素失败: {e}")

    def add_shape_element(self):
        """添加形状元素"""
        try:
            logger.info("添加形状元素")
            # TODO: 实现形状元素添加逻辑

        except Exception as e:
            logger.error(f"添加形状元素失败: {e}")

    def add_image_element(self):
        """添加图片元素"""
        try:
            logger.info("添加图片元素")
            # TODO: 实现图片元素添加逻辑

        except Exception as e:
            logger.error(f"添加图片元素失败: {e}")
