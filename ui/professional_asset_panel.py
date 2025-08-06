"""
专业素材面板UI
参考Adobe After Effects、DaVinci Resolve等专业软件的素材管理界面
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QLineEdit, QComboBox, QPushButton, QLabel, QFrame, QSplitter,
    QListWidget, QListWidgetItem, QButtonGroup, QToolButton,
    QMenu, QSlider, QCheckBox, QSpinBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot, QSize
from PyQt6.QtGui import QPixmap, QIcon, QFont, QPainter, QColor, QAction
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from core.asset_management import AssetManager, EnhancedAsset, AssetSearchFilter, AssetType, AssetStatus
from ui.asset_drag_system import DraggableAssetWidget, AssetDragHandler

logger = logging.getLogger(__name__)

class AssetThumbnailWidget(QFrame):
    """素材缩略图组件"""
    
    clicked = pyqtSignal(str)  # asset_id
    double_clicked = pyqtSignal(str)  # asset_id
    context_menu_requested = pyqtSignal(str, object)  # asset_id, position
    
    def __init__(self, asset: EnhancedAsset, size: int = 128):
        super().__init__()
        self.asset = asset
        self.thumbnail_size = size
        self.selected = False
        
        self.setup_ui()
        self.load_thumbnail()
    
    def setup_ui(self):
        """设置UI"""
        self.setFixedSize(self.thumbnail_size + 20, self.thumbnail_size + 60)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            AssetThumbnailWidget {
                background-color: #F8F9FA;
                border: 2px solid #E9ECEF;
                border-radius: 8px;
            }
            AssetThumbnailWidget:hover {
                border-color: #007BFF;
                background-color: #E3F2FD;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # 缩略图标签
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(self.thumbnail_size, self.thumbnail_size)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #DEE2E6;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.thumbnail_label)
        
        # 素材名称
        self.name_label = QLabel(self.asset.name)
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #495057;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.name_label)
        
        # 状态指示器
        self.status_label = QLabel()
        self.status_label.setFixedHeight(12)
        self.update_status_indicator()
        layout.addWidget(self.status_label)
    
    def load_thumbnail(self):
        """加载缩略图"""
        try:
            thumbnail_path = self.asset.thumbnail.medium_path
            if thumbnail_path and Path(thumbnail_path).exists():
                pixmap = QPixmap(thumbnail_path)
                if not pixmap.isNull():
                    # 缩放到合适大小
                    scaled_pixmap = pixmap.scaled(
                        self.thumbnail_size, self.thumbnail_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.thumbnail_label.setPixmap(scaled_pixmap)
                    return
            
            # 使用默认图标
            self.set_default_icon()
            
        except Exception as e:
            logger.error(f"加载缩略图失败: {e}")
            self.set_default_icon()
    
    def set_default_icon(self):
        """设置默认图标"""
        # 创建简单的默认图标
        pixmap = QPixmap(self.thumbnail_size, self.thumbnail_size)
        pixmap.fill(QColor("#F8F9FA"))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor("#6C757D"))
        painter.drawRect(0, 0, self.thumbnail_size-1, self.thumbnail_size-1)
        
        # 绘制文件类型图标
        type_text = self.asset.asset_type.value.upper()
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, type_text)
        painter.end()
        
        self.thumbnail_label.setPixmap(pixmap)
    
    def update_status_indicator(self):
        """更新状态指示器"""
        if self.asset.status == AssetStatus.MISSING:
            self.status_label.setStyleSheet("background-color: #DC3545; border-radius: 6px;")
            self.status_label.setToolTip("文件丢失")
        elif self.asset.status == AssetStatus.ERROR:
            self.status_label.setStyleSheet("background-color: #FD7E14; border-radius: 6px;")
            self.status_label.setToolTip("文件错误")
        elif self.asset.favorite:
            self.status_label.setStyleSheet("background-color: #FFC107; border-radius: 6px;")
            self.status_label.setToolTip("收藏")
        else:
            self.status_label.setStyleSheet("background-color: #28A745; border-radius: 6px;")
            self.status_label.setToolTip("正常")
    
    def set_selected(self, selected: bool):
        """设置选中状态"""
        self.selected = selected
        if selected:
            self.setStyleSheet("""
                AssetThumbnailWidget {
                    background-color: #007BFF;
                    border: 2px solid #0056B3;
                    border-radius: 8px;
                }
            """)
            self.name_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: white;
                    background: transparent;
                    border: none;
                    font-weight: bold;
                }
            """)
        else:
            self.setStyleSheet("""
                AssetThumbnailWidget {
                    background-color: #F8F9FA;
                    border: 2px solid #E9ECEF;
                    border-radius: 8px;
                }
                AssetThumbnailWidget:hover {
                    border-color: #007BFF;
                    background-color: #E3F2FD;
                }
            """)
            self.name_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #495057;
                    background: transparent;
                    border: none;
                }
            """)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.asset.asset_id)
        elif event.button() == Qt.MouseButton.RightButton:
            self.context_menu_requested.emit(self.asset.asset_id, event.globalPosition())
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.asset.asset_id)
        super().mouseDoubleClickEvent(event)


class AssetGridView(QScrollArea, DraggableAssetWidget):
    """素材网格视图"""
    
    asset_selected = pyqtSignal(str)  # asset_id
    asset_double_clicked = pyqtSignal(str)  # asset_id
    assets_selection_changed = pyqtSignal(list)  # selected asset_ids
    
    def __init__(self):
        QScrollArea.__init__(self)
        DraggableAssetWidget.__init__(self)
        self.asset_widgets: Dict[str, AssetThumbnailWidget] = {}
        self.selected_asset_ids: List[str] = []
        self.thumbnail_size = 128

        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建容器
        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        
        self.setWidget(self.container)
    
    def set_assets(self, assets: List[EnhancedAsset]):
        """设置素材列表"""
        # 清除现有组件
        self.clear_assets()
        
        # 添加新组件
        columns = max(1, (self.width() - 40) // (self.thumbnail_size + 30))
        
        for i, asset in enumerate(assets):
            widget = AssetThumbnailWidget(asset, self.thumbnail_size)
            widget.clicked.connect(self.on_asset_clicked)
            widget.double_clicked.connect(self.on_asset_double_clicked)
            widget.context_menu_requested.connect(self.on_context_menu_requested)
            
            row = i // columns
            col = i % columns
            self.grid_layout.addWidget(widget, row, col)
            
            self.asset_widgets[asset.asset_id] = widget
    
    def clear_assets(self):
        """清除所有素材"""
        for widget in self.asset_widgets.values():
            widget.deleteLater()
        self.asset_widgets.clear()
        self.selected_asset_ids.clear()
        
        # 清除布局
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def set_thumbnail_size(self, size: int):
        """设置缩略图大小"""
        self.thumbnail_size = size
        for widget in self.asset_widgets.values():
            widget.thumbnail_size = size
            widget.setFixedSize(size + 20, size + 60)
            widget.thumbnail_label.setFixedSize(size, size)
            widget.load_thumbnail()
    
    def on_asset_clicked(self, asset_id: str):
        """素材点击事件"""
        # 更新选择状态
        if asset_id in self.selected_asset_ids:
            self.selected_asset_ids.remove(asset_id)
        else:
            self.selected_asset_ids.clear()  # 单选模式
            self.selected_asset_ids.append(asset_id)

        # 更新UI
        for aid, widget in self.asset_widgets.items():
            widget.set_selected(aid in self.selected_asset_ids)

        # 更新拖拽组件的选中素材
        selected_assets = []
        for aid in self.selected_asset_ids:
            widget = self.asset_widgets.get(aid)
            if widget:
                selected_assets.append(widget.asset)
        self.set_selected_assets(selected_assets)

        self.asset_selected.emit(asset_id)
        self.assets_selection_changed.emit(self.selected_asset_ids)
    
    def on_asset_double_clicked(self, asset_id: str):
        """素材双击事件"""
        self.asset_double_clicked.emit(asset_id)
    
    def on_context_menu_requested(self, asset_id: str, position):
        """右键菜单请求"""
        # 这里可以显示上下文菜单
        pass
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 重新计算网格布局
        if self.asset_widgets:
            # 这里可以重新排列网格
            pass


class ProfessionalAssetPanel(QWidget):
    """专业素材面板"""

    asset_selected = pyqtSignal(str)  # asset_id
    asset_double_clicked = pyqtSignal(str)  # asset_id
    asset_import_requested = pyqtSignal()
    asset_deleted = pyqtSignal(str)  # asset_id

    def __init__(self, asset_manager: AssetManager):
        super().__init__()
        self.asset_manager = asset_manager
        self.current_filter = AssetSearchFilter()
        self.current_assets: List[EnhancedAsset] = []

        self.setup_ui()
        self.connect_signals()
        self.refresh_assets()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 工具栏
        self.create_toolbar()
        layout.addWidget(self.toolbar)

        # 搜索和过滤区域
        self.create_search_area()
        layout.addWidget(self.search_area)

        # 主内容区域
        self.create_main_area()
        layout.addWidget(self.main_area, 1)

        # 状态栏
        self.create_status_bar()
        layout.addWidget(self.status_bar)

    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = QFrame()
        self.toolbar.setFixedHeight(40)
        self.toolbar.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-bottom: 1px solid #DEE2E6;
            }
        """)

        layout = QHBoxLayout(self.toolbar)
        layout.setContentsMargins(10, 5, 10, 5)

        # 导入按钮
        self.import_btn = QPushButton("导入素材")
        self.import_btn.setIcon(QIcon("icons/import.png"))
        layout.addWidget(self.import_btn)

        # 视图切换按钮
        self.view_group = QButtonGroup()

        self.grid_view_btn = QToolButton()
        self.grid_view_btn.setText("网格")
        self.grid_view_btn.setCheckable(True)
        self.grid_view_btn.setChecked(True)
        self.view_group.addButton(self.grid_view_btn, 0)
        layout.addWidget(self.grid_view_btn)

        self.list_view_btn = QToolButton()
        self.list_view_btn.setText("列表")
        self.list_view_btn.setCheckable(True)
        self.view_group.addButton(self.list_view_btn, 1)
        layout.addWidget(self.list_view_btn)

        layout.addStretch()

        # 缩略图大小滑块
        layout.addWidget(QLabel("大小:"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(64, 256)
        self.size_slider.setValue(128)
        self.size_slider.setFixedWidth(100)
        layout.addWidget(self.size_slider)

        # 刷新按钮
        self.refresh_btn = QPushButton("刷新")
        layout.addWidget(self.refresh_btn)

    def create_search_area(self):
        """创建搜索区域"""
        self.search_area = QFrame()
        self.search_area.setFixedHeight(60)
        self.search_area.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-bottom: 1px solid #DEE2E6;
            }
        """)

        layout = QHBoxLayout(self.search_area)
        layout.setContentsMargins(10, 10, 10, 10)

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索素材...")
        self.search_input.setFixedHeight(30)
        layout.addWidget(self.search_input, 2)

        # 类型过滤
        self.type_combo = QComboBox()
        self.type_combo.addItem("所有类型", "")
        for asset_type in AssetType:
            self.type_combo.addItem(asset_type.value.title(), asset_type.value)
        layout.addWidget(self.type_combo)

        # 分类过滤
        self.category_combo = QComboBox()
        self.category_combo.addItem("所有分类", "")
        layout.addWidget(self.category_combo)

        # 状态过滤
        self.status_combo = QComboBox()
        self.status_combo.addItem("所有状态", "")
        for status in AssetStatus:
            self.status_combo.addItem(status.value.title(), status.value)
        layout.addWidget(self.status_combo)

        # 收藏过滤
        self.favorites_check = QCheckBox("仅收藏")
        layout.addWidget(self.favorites_check)

    def create_main_area(self):
        """创建主内容区域"""
        self.main_area = QFrame()

        layout = QVBoxLayout(self.main_area)
        layout.setContentsMargins(0, 0, 0, 0)

        # 网格视图
        self.grid_view = AssetGridView()
        layout.addWidget(self.grid_view)

        # 列表视图（暂时隐藏）
        # self.list_view = AssetListView()
        # layout.addWidget(self.list_view)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QFrame()
        self.status_bar.setFixedHeight(25)
        self.status_bar.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-top: 1px solid #DEE2E6;
            }
        """)

        layout = QHBoxLayout(self.status_bar)
        layout.setContentsMargins(10, 2, 10, 2)

        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.count_label = QLabel("0 个素材")
        layout.addWidget(self.count_label)

    def connect_signals(self):
        """连接信号"""
        # 工具栏信号
        self.import_btn.clicked.connect(self.asset_import_requested.emit)
        self.refresh_btn.clicked.connect(self.refresh_assets)
        self.size_slider.valueChanged.connect(self.on_thumbnail_size_changed)

        # 搜索信号
        self.search_input.textChanged.connect(self.on_search_changed)
        self.type_combo.currentTextChanged.connect(self.on_filter_changed)
        self.category_combo.currentTextChanged.connect(self.on_filter_changed)
        self.status_combo.currentTextChanged.connect(self.on_filter_changed)
        self.favorites_check.toggled.connect(self.on_filter_changed)

        # 视图信号
        self.grid_view.asset_selected.connect(self.asset_selected.emit)
        self.grid_view.asset_double_clicked.connect(self.asset_double_clicked.emit)

    def refresh_assets(self):
        """刷新素材列表"""
        try:
            # 更新分类下拉框
            self.update_category_combo()

            # 应用过滤器
            self.apply_current_filter()

            # 更新状态
            self.update_status()

        except Exception as e:
            logger.error(f"刷新素材列表失败: {e}")

    def update_category_combo(self):
        """更新分类下拉框"""
        current_category = self.category_combo.currentData()
        self.category_combo.clear()
        self.category_combo.addItem("所有分类", "")

        categories = self.asset_manager.get_all_categories()
        for category in categories:
            self.category_combo.addItem(category, category)

        # 恢复选择
        if current_category:
            index = self.category_combo.findData(current_category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

    def apply_current_filter(self):
        """应用当前过滤器"""
        # 搜索结果
        filtered_assets = self.asset_manager.search(self.current_filter)

        # 更新视图
        self.grid_view.set_assets(filtered_assets)
        self.current_assets = filtered_assets

    def on_search_changed(self):
        """搜索文本改变"""
        self.current_filter.text_query = self.search_input.text()
        self.apply_current_filter()

    def on_filter_changed(self):
        """过滤条件改变"""
        # 类型过滤
        type_value = self.type_combo.currentData()
        if type_value:
            self.current_filter.asset_types = {AssetType(type_value)}
        else:
            self.current_filter.asset_types = set()

        # 分类过滤
        category_value = self.category_combo.currentData()
        if category_value:
            self.current_filter.categories = {category_value}
        else:
            self.current_filter.categories = set()

        # 状态过滤
        status_value = self.status_combo.currentData()
        if status_value:
            self.current_filter.status_filter = {AssetStatus(status_value)}
        else:
            self.current_filter.status_filter = set()

        # 收藏过滤
        self.current_filter.favorites_only = self.favorites_check.isChecked()

        self.apply_current_filter()

    def on_thumbnail_size_changed(self, size: int):
        """缩略图大小改变"""
        self.grid_view.set_thumbnail_size(size)

    def update_status(self):
        """更新状态栏"""
        total_count = len(self.current_assets)
        self.count_label.setText(f"{total_count} 个素材")

        if total_count == 0:
            self.status_label.setText("没有找到匹配的素材")
        else:
            self.status_label.setText("就绪")

    def add_asset(self, asset: EnhancedAsset):
        """添加素材"""
        self.refresh_assets()

    def remove_asset(self, asset_id: str):
        """移除素材"""
        self.refresh_assets()
