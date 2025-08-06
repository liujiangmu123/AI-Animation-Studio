"""
AI Animation Studio - 库管理器界面组件
管理JavaScript库的下载和使用
"""

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
        QPushButton, QProgressBar, QCheckBox, QGroupBox, QTextEdit, QMessageBox,
        QHeaderView, QSplitter, QTabWidget, QComboBox, QLineEdit, QSpinBox,
        QTreeWidget, QTreeWidgetItem, QFormLayout, QScrollArea, QFrame,
        QToolButton, QMenu, QDialog, QDialogButtonBox, QListWidget,
        QListWidgetItem, QSlider, QDoubleSpinBox, QRadioButton, QButtonGroup
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
    from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QLinearGradient, QIcon, QAction
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    # 模拟类
    QWidget = QVBoxLayout = QHBoxLayout = QLabel = object
    QTableWidget = QTableWidgetItem = QPushButton = object
    QProgressBar = QCheckBox = QGroupBox = QTextEdit = object
    QMessageBox = QHeaderView = QSplitter = object
    QThread = pyqtSignal = Qt = QFont = object

import os
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional

from core.js_library_manager import JSLibraryManager
from core.logger import get_logger

logger = get_logger("library_manager_widget")


class NetworkException(Exception):
    """网络异常"""
    pass


class FilePermissionException(Exception):
    """文件权限异常"""
    pass


class DiskSpaceException(Exception):
    """磁盘空间不足异常"""
    pass


class LibraryNotFoundException(Exception):
    """库未找到异常"""
    pass

class LibraryDownloadThread(QThread):
    """增强的库下载线程 - 包含完善的异常处理"""
    progress_update = pyqtSignal(str, str)  # lib_id, status
    download_complete = pyqtSignal(str, bool, str)  # lib_id, success, error_msg
    all_complete = pyqtSignal(dict)  # results
    error_occurred = pyqtSignal(str, str)  # lib_id, error_message

    def __init__(self, library_manager: JSLibraryManager, lib_ids: list):
        super().__init__()
        self.library_manager = library_manager
        self.lib_ids = lib_ids
        self.retry_count = 3
        self.retry_delay = 2  # 秒

    def run(self):
        """运行下载任务"""
        results = {}

        # 预检查
        pre_check_result = self.pre_download_check()
        if not pre_check_result['success']:
            for lib_id in self.lib_ids:
                self.error_occurred.emit(lib_id, pre_check_result['error'])
                results[lib_id] = False
            self.all_complete.emit(results)
            return

        # 下载每个库
        for lib_id in self.lib_ids:
            try:
                self.progress_update.emit(lib_id, "准备下载...")
                success, error_msg = self.download_library_with_retry(lib_id)
                results[lib_id] = success

                if success:
                    self.progress_update.emit(lib_id, "下载完成")
                    self.download_complete.emit(lib_id, True, "")
                else:
                    self.progress_update.emit(lib_id, f"下载失败: {error_msg}")
                    self.download_complete.emit(lib_id, False, error_msg)
                    self.error_occurred.emit(lib_id, error_msg)

            except Exception as e:
                logger.error(f"下载库 {lib_id} 时发生未预期错误: {e}")
                error_msg = f"未预期错误: {str(e)}"
                results[lib_id] = False
                self.progress_update.emit(lib_id, f"错误: {error_msg}")
                self.download_complete.emit(lib_id, False, error_msg)
                self.error_occurred.emit(lib_id, error_msg)

        self.all_complete.emit(results)

    def pre_download_check(self) -> Dict[str, any]:
        """下载前预检查"""
        try:
            # 检查网络连接
            if not self.check_network_connection():
                return {'success': False, 'error': '网络连接不可用，请检查网络设置'}

            # 检查磁盘空间
            if not self.check_disk_space():
                return {'success': False, 'error': '磁盘空间不足，请清理磁盘空间'}

            # 检查文件权限
            if not self.check_file_permissions():
                return {'success': False, 'error': '没有写入权限，请检查文件夹权限'}

            return {'success': True, 'error': None}

        except Exception as e:
            logger.error(f"预检查失败: {e}")
            return {'success': False, 'error': f'预检查失败: {str(e)}'}

    def check_network_connection(self) -> bool:
        """检查网络连接"""
        try:
            # 尝试连接到常用的CDN
            test_urls = [
                'https://cdnjs.cloudflare.com',
                'https://unpkg.com',
                'https://cdn.jsdelivr.net'
            ]

            for url in test_urls:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        return True
                except:
                    continue

            return False

        except Exception as e:
            logger.error(f"网络连接检查失败: {e}")
            return False

    def check_disk_space(self, min_space_mb: int = 100) -> bool:
        """检查磁盘空间"""
        try:
            # 获取库存储目录
            lib_dir = self.library_manager.get_library_directory()

            # 检查可用空间
            if hasattr(os, 'statvfs'):  # Unix/Linux
                statvfs = os.statvfs(lib_dir)
                available_bytes = statvfs.f_frsize * statvfs.f_bavail
            else:  # Windows
                import shutil
                _, _, available_bytes = shutil.disk_usage(lib_dir)

            available_mb = available_bytes / (1024 * 1024)
            return available_mb >= min_space_mb

        except Exception as e:
            logger.error(f"磁盘空间检查失败: {e}")
            return True  # 如果检查失败，假设空间足够

    def check_file_permissions(self) -> bool:
        """检查文件权限"""
        try:
            lib_dir = Path(self.library_manager.get_library_directory())

            # 确保目录存在
            lib_dir.mkdir(parents=True, exist_ok=True)

            # 尝试创建测试文件
            test_file = lib_dir / 'permission_test.tmp'
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                test_file.unlink()  # 删除测试文件
                return True
            except PermissionError:
                return False

        except Exception as e:
            logger.error(f"文件权限检查失败: {e}")
            return False

    def download_library_with_retry(self, lib_id: str) -> tuple[bool, str]:
        """带重试机制的库下载"""
        last_error = ""

        for attempt in range(self.retry_count):
            try:
                if attempt > 0:
                    self.progress_update.emit(lib_id, f"重试 {attempt}/{self.retry_count-1}...")
                    time.sleep(self.retry_delay)

                # 尝试下载
                success = self.library_manager.download_library(lib_id)

                if success:
                    return True, ""
                else:
                    last_error = "下载失败，原因未知"

            except requests.exceptions.ConnectionError as e:
                last_error = f"网络连接错误: {str(e)}"
                logger.warning(f"库 {lib_id} 下载连接错误 (尝试 {attempt+1}): {e}")

            except requests.exceptions.Timeout as e:
                last_error = f"下载超时: {str(e)}"
                logger.warning(f"库 {lib_id} 下载超时 (尝试 {attempt+1}): {e}")

            except requests.exceptions.HTTPError as e:
                last_error = f"HTTP错误: {str(e)}"
                logger.warning(f"库 {lib_id} HTTP错误 (尝试 {attempt+1}): {e}")

            except PermissionError as e:
                last_error = f"文件权限错误: {str(e)}"
                logger.error(f"库 {lib_id} 权限错误: {e}")
                break  # 权限错误不需要重试

            except OSError as e:
                if "No space left on device" in str(e) or "磁盘空间不足" in str(e):
                    last_error = f"磁盘空间不足: {str(e)}"
                    logger.error(f"库 {lib_id} 磁盘空间不足: {e}")
                    break  # 磁盘空间不足不需要重试
                else:
                    last_error = f"系统错误: {str(e)}"
                    logger.warning(f"库 {lib_id} 系统错误 (尝试 {attempt+1}): {e}")

            except Exception as e:
                last_error = f"未知错误: {str(e)}"
                logger.error(f"库 {lib_id} 未知错误 (尝试 {attempt+1}): {e}")

        return False, last_error

class LibraryManagerWidget(QWidget):
    """库管理器界面组件 - 增强版"""

    # 信号定义
    library_installed = pyqtSignal(str, str)  # lib_id, version
    library_uninstalled = pyqtSignal(str)  # lib_id
    dependency_resolved = pyqtSignal(str, list)  # lib_id, dependencies
    version_updated = pyqtSignal(str, str, str)  # lib_id, old_version, new_version

    def __init__(self, parent=None):
        super().__init__(parent)
        self.library_manager = JSLibraryManager()
        self.download_thread = None

        # 版本管理
        self.version_history = {}
        self.available_versions = {}
        self.dependency_graph = {}

        # 搜索和筛选
        self.search_query = ""
        self.category_filter = "all"
        self.status_filter = "all"

        # 智能推荐
        self.recommendation_engine = None
        self.usage_stats = {}

        # 批量操作
        self.batch_operations = []
        self.operation_queue = []

        self.init_ui()
        self.load_library_status()
        self.setup_connections()

        logger.info("库管理器组件初始化完成")
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 顶部工具栏
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)

        # 主要内容区域
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧面板 - 库浏览和搜索
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)

        # 右侧面板 - 详情和管理
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)

        # 设置分割器比例
        main_splitter.setSizes([500, 600])
        layout.addWidget(main_splitter)

        # 底部状态栏
        status_bar = self.create_status_bar()
        layout.addWidget(status_bar)

    def create_toolbar(self):
        """创建工具栏"""
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(toolbar_frame)

        # 增强搜索框
        search_group = QFrame()
        search_group.setFrameStyle(QFrame.Shape.StyledPanel)
        search_layout = QHBoxLayout(search_group)

        search_layout.addWidget(QLabel("🔍"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索库名称、描述、标签或作者...")
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.setMaximumWidth(250)
        search_layout.addWidget(self.search_input)

        # 搜索选项
        self.search_options_btn = QPushButton("⚙️")
        self.search_options_btn.setToolTip("搜索选项")
        self.search_options_btn.setMaximumWidth(30)
        self.search_options_btn.clicked.connect(self.show_search_options)
        search_layout.addWidget(self.search_options_btn)

        layout.addWidget(search_group)

        # 高级筛选
        filter_group = QFrame()
        filter_group.setFrameStyle(QFrame.Shape.StyledPanel)
        filter_layout = QHBoxLayout(filter_group)

        # 分类筛选
        filter_layout.addWidget(QLabel("分类:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "全部", "动画库", "3D图形", "UI框架", "工具库", "图表库",
            "音频库", "视频库", "游戏引擎", "数据处理", "其他"
        ])
        self.category_combo.currentTextChanged.connect(self.on_filter_changed)
        self.category_combo.setMaximumWidth(120)
        filter_layout.addWidget(self.category_combo)

        # 状态筛选
        filter_layout.addWidget(QLabel("状态:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["全部", "已安装", "未安装", "有更新", "已过期", "收藏"])
        self.status_combo.currentTextChanged.connect(self.on_filter_changed)
        self.status_combo.setMaximumWidth(100)
        filter_layout.addWidget(self.status_combo)

        # 版本筛选
        filter_layout.addWidget(QLabel("版本:"))
        self.version_combo = QComboBox()
        self.version_combo.addItems(["全部", "最新版", "稳定版", "测试版", "旧版本"])
        self.version_combo.currentTextChanged.connect(self.on_filter_changed)
        self.version_combo.setMaximumWidth(100)
        filter_layout.addWidget(self.version_combo)

        # 大小筛选
        filter_layout.addWidget(QLabel("大小:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(["全部", "<50KB", "50-200KB", "200KB-1MB", ">1MB"])
        self.size_combo.currentTextChanged.connect(self.on_filter_changed)
        self.size_combo.setMaximumWidth(100)
        filter_layout.addWidget(self.size_combo)

        layout.addWidget(filter_group)

        layout.addWidget(QLabel("|"))

        # 视图切换
        self.view_group = QButtonGroup()

        self.list_view_radio = QRadioButton("列表")
        self.list_view_radio.setChecked(True)
        self.view_group.addButton(self.list_view_radio)
        layout.addWidget(self.list_view_radio)

        self.card_view_radio = QRadioButton("卡片")
        self.view_group.addButton(self.card_view_radio)
        layout.addWidget(self.card_view_radio)

        layout.addStretch()

        # 快速操作
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setToolTip("刷新库列表")
        self.refresh_btn.setMaximumWidth(30)
        layout.addWidget(self.refresh_btn)

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

        # 库浏览标签页
        browse_tab = self.create_browse_tab()
        tab_widget.addTab(browse_tab, "📚 浏览")

        # 已安装标签页
        installed_tab = self.create_installed_tab()
        tab_widget.addTab(installed_tab, "✅ 已安装")

        # 推荐标签页
        recommendations_tab = self.create_recommendations_tab()
        tab_widget.addTab(recommendations_tab, "💡 推荐")

        # 收藏标签页
        favorites_tab = self.create_favorites_tab()
        tab_widget.addTab(favorites_tab, "⭐ 收藏")

        layout.addWidget(tab_widget)

        return panel

    def create_browse_tab(self):
        """创建浏览标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 增强库列表
        self.library_table = QTableWidget()
        self.library_table.setColumnCount(9)
        self.library_table.setHorizontalHeaderLabels([
            "选择", "库名", "当前版本", "最新版本", "状态", "大小", "评分", "下载量", "更新日期"
        ])

        # 设置列宽
        header = self.library_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 选择
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 库名
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # 当前版本
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # 最新版本
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # 状态
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # 大小
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # 评分
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)  # 下载量
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)  # 更新日期

        self.library_table.setColumnWidth(0, 50)   # 选择
        self.library_table.setColumnWidth(2, 100)  # 当前版本
        self.library_table.setColumnWidth(3, 100)  # 最新版本
        self.library_table.setColumnWidth(4, 80)   # 状态
        self.library_table.setColumnWidth(5, 80)   # 大小
        self.library_table.setColumnWidth(6, 80)   # 评分
        self.library_table.setColumnWidth(7, 100)  # 下载量
        self.library_table.setColumnWidth(8, 120)  # 更新日期

        # 设置表格属性
        self.library_table.setAlternatingRowColors(True)
        self.library_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.library_table.setSortingEnabled(True)
        self.library_table.itemDoubleClicked.connect(self.show_library_details)

        layout.addWidget(self.library_table)

        # 批量操作工具栏
        batch_toolbar = QHBoxLayout()

        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setMaximumWidth(60)
        batch_toolbar.addWidget(self.select_all_btn)

        self.select_none_btn = QPushButton("取消")
        self.select_none_btn.setMaximumWidth(60)
        batch_toolbar.addWidget(self.select_none_btn)

        batch_toolbar.addStretch()

        self.batch_install_btn = QPushButton("批量安装")
        batch_toolbar.addWidget(self.batch_install_btn)

        self.batch_update_btn = QPushButton("批量更新")
        batch_toolbar.addWidget(self.batch_update_btn)

        layout.addLayout(batch_toolbar)

        return tab

    def create_installed_tab(self):
        """创建已安装标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 已安装库树形视图
        self.installed_tree = QTreeWidget()
        self.installed_tree.setHeaderLabels([
            "库名", "版本", "安装日期", "大小", "状态"
        ])
        self.installed_tree.header().setStretchLastSection(False)
        self.installed_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.installed_tree)

        # 已安装库操作
        installed_toolbar = QHBoxLayout()

        self.update_all_btn = QPushButton("全部更新")
        installed_toolbar.addWidget(self.update_all_btn)

        self.clean_cache_btn = QPushButton("清理缓存")
        installed_toolbar.addWidget(self.clean_cache_btn)

        self.export_list_btn = QPushButton("导出列表")
        installed_toolbar.addWidget(self.export_list_btn)

        installed_toolbar.addStretch()

        layout.addLayout(installed_toolbar)

        return tab

    def create_recommendations_tab(self):
        """创建推荐标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 推荐类别
        categories_layout = QHBoxLayout()

        self.trending_btn = QPushButton("🔥 热门")
        self.trending_btn.setCheckable(True)
        self.trending_btn.setChecked(True)
        categories_layout.addWidget(self.trending_btn)

        self.new_releases_btn = QPushButton("🆕 新发布")
        self.new_releases_btn.setCheckable(True)
        categories_layout.addWidget(self.new_releases_btn)

        self.compatible_btn = QPushButton("🔗 兼容")
        self.compatible_btn.setCheckable(True)
        categories_layout.addWidget(self.compatible_btn)

        categories_layout.addStretch()
        layout.addLayout(categories_layout)

        # 推荐列表
        self.recommendations_list = QListWidget()
        layout.addWidget(self.recommendations_list)

        # 推荐设置
        settings_group = QGroupBox("推荐设置")
        settings_layout = QFormLayout(settings_group)

        self.auto_recommend_cb = QCheckBox("自动推荐")
        self.auto_recommend_cb.setChecked(True)
        settings_layout.addRow("", self.auto_recommend_cb)

        self.recommendation_level_slider = QSlider(Qt.Orientation.Horizontal)
        self.recommendation_level_slider.setRange(1, 5)
        self.recommendation_level_slider.setValue(3)
        settings_layout.addRow("推荐强度:", self.recommendation_level_slider)

        layout.addWidget(settings_group)

        return tab

    def create_favorites_tab(self):
        """创建收藏标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 收藏库列表
        self.favorites_list = QListWidget()
        layout.addWidget(self.favorites_list)

        # 收藏操作
        favorites_toolbar = QHBoxLayout()

        self.add_to_favorites_btn = QPushButton("添加收藏")
        favorites_toolbar.addWidget(self.add_to_favorites_btn)

        self.remove_from_favorites_btn = QPushButton("移除收藏")
        favorites_toolbar.addWidget(self.remove_from_favorites_btn)

        favorites_toolbar.addStretch()

        layout.addLayout(favorites_toolbar)

        return tab

    def create_right_panel(self):
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 创建标签页
        tab_widget = QTabWidget()

        # 库详情标签页
        details_tab = self.create_details_tab()
        tab_widget.addTab(details_tab, "📋 详情")

        # 版本管理标签页
        versions_tab = self.create_versions_tab()
        tab_widget.addTab(versions_tab, "🔄 版本")

        # 依赖关系标签页
        dependencies_tab = self.create_dependencies_tab()
        tab_widget.addTab(dependencies_tab, "🔗 依赖")

        # 使用统计标签页
        stats_tab = self.create_stats_tab()
        tab_widget.addTab(stats_tab, "📊 统计")

        layout.addWidget(tab_widget)

        return panel

    def create_details_tab(self):
        """创建详情标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 库基本信息
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout(info_group)

        self.lib_name_label = QLabel("未选择")
        info_layout.addRow("名称:", self.lib_name_label)

        self.lib_version_label = QLabel("未知")
        info_layout.addRow("版本:", self.lib_version_label)

        self.lib_author_label = QLabel("未知")
        info_layout.addRow("作者:", self.lib_author_label)

        self.lib_license_label = QLabel("未知")
        info_layout.addRow("许可证:", self.lib_license_label)

        self.lib_size_label = QLabel("未知")
        info_layout.addRow("大小:", self.lib_size_label)

        self.lib_downloads_label = QLabel("未知")
        info_layout.addRow("下载量:", self.lib_downloads_label)

        layout.addWidget(info_group)

        # 库描述
        desc_group = QGroupBox("描述")
        desc_layout = QVBoxLayout(desc_group)

        self.lib_description = QTextEdit()
        self.lib_description.setReadOnly(True)
        self.lib_description.setMaximumHeight(120)
        desc_layout.addWidget(self.lib_description)

        layout.addWidget(desc_group)

        # 操作按钮
        actions_group = QGroupBox("操作")
        actions_layout = QVBoxLayout(actions_group)

        # 主要操作
        main_actions = QHBoxLayout()

        self.install_btn = QPushButton("安装")
        self.install_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
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
        main_actions.addWidget(self.install_btn)

        self.uninstall_btn = QPushButton("卸载")
        self.uninstall_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        main_actions.addWidget(self.uninstall_btn)

        self.update_btn = QPushButton("更新")
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        main_actions.addWidget(self.update_btn)

        actions_layout.addLayout(main_actions)

        # 次要操作
        secondary_actions = QHBoxLayout()

        self.favorite_btn = QPushButton("收藏")
        secondary_actions.addWidget(self.favorite_btn)

        self.share_btn = QPushButton("分享")
        secondary_actions.addWidget(self.share_btn)

        self.report_btn = QPushButton("报告问题")
        secondary_actions.addWidget(self.report_btn)

        actions_layout.addLayout(secondary_actions)

        layout.addWidget(actions_group)

        layout.addStretch()
        return tab
    
    def create_library_list(self):
        """创建库列表"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题
        layout.addWidget(QLabel("可用库列表"))
        
        # 表格
        self.library_table = QTableWidget()
        self.library_table.setColumnCount(4)
        self.library_table.setHorizontalHeaderLabels(["选择", "库名", "版本", "状态"])
        
        # 设置列宽
        header = self.library_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        
        self.library_table.setColumnWidth(0, 50)
        self.library_table.setColumnWidth(2, 80)
        self.library_table.setColumnWidth(3, 80)
        
        # 选择变化事件
        self.library_table.itemSelectionChanged.connect(self.on_library_selected)
        
        layout.addWidget(self.library_table)
        
        return widget
    
    def create_library_details(self):
        """创建库详情面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 库详情
        details_group = QGroupBox("库详情")
        details_layout = QVBoxLayout(details_group)
        
        self.library_name_label = QLabel("选择一个库查看详情")
        self.library_description = QTextEdit()
        self.library_description.setMaximumHeight(100)
        self.library_description.setReadOnly(True)
        
        details_layout.addWidget(self.library_name_label)
        details_layout.addWidget(QLabel("描述:"))
        details_layout.addWidget(self.library_description)
        
        layout.addWidget(details_group)
        
        # 设置
        settings_group = QGroupBox("设置")
        settings_layout = QVBoxLayout(settings_group)
        
        self.auto_inject_checkbox = QCheckBox("自动注入所需库到HTML")
        self.auto_inject_checkbox.setChecked(True)
        settings_layout.addWidget(self.auto_inject_checkbox)
        
        self.prefer_local_checkbox = QCheckBox("优先使用本地库")
        self.prefer_local_checkbox.setChecked(True)
        settings_layout.addWidget(self.prefer_local_checkbox)
        
        layout.addWidget(settings_group)
        
        # 库路径信息
        path_group = QGroupBox("路径信息")
        path_layout = QVBoxLayout(path_group)
        
        self.library_path_label = QLabel(f"库存储路径: {self.library_manager.libraries_dir}")
        self.library_path_label.setWordWrap(True)
        path_layout.addWidget(self.library_path_label)
        
        layout.addWidget(path_group)
        
        layout.addStretch()
        
        return widget
    
    def load_library_status(self):
        """加载库状态"""
        libraries = self.library_manager.get_available_libraries()
        
        self.library_table.setRowCount(len(libraries))
        
        for row, (lib_id, library) in enumerate(libraries.items()):
            # 选择框
            checkbox = QCheckBox()
            self.library_table.setCellWidget(row, 0, checkbox)
            
            # 库名
            name_item = QTableWidgetItem(library.name)
            name_item.setData(Qt.ItemDataRole.UserRole, lib_id)
            self.library_table.setItem(row, 1, name_item)
            
            # 版本
            version_item = QTableWidgetItem(library.version)
            self.library_table.setItem(row, 2, version_item)
            
            # 状态
            status = "已下载" if library.is_downloaded else "未下载"
            status_item = QTableWidgetItem(status)
            if library.is_downloaded:
                status_item.setBackground(QColor(144, 238, 144))  # lightgreen
            else:
                status_item.setBackground(QColor(211, 211, 211))  # lightgray
            self.library_table.setItem(row, 3, status_item)
    
    def on_library_selected(self):
        """库选择变化"""
        current_row = self.library_table.currentRow()
        if current_row >= 0:
            name_item = self.library_table.item(current_row, 1)
            if name_item:
                lib_id = name_item.data(Qt.ItemDataRole.UserRole)
                library = self.library_manager.get_available_libraries().get(lib_id)
                
                if library:
                    self.library_name_label.setText(f"{library.name} v{library.version}")
                    self.library_description.setText(library.description)
    
    def get_selected_libraries(self):
        """获取选中的库"""
        selected = []
        for row in range(self.library_table.rowCount()):
            checkbox = self.library_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                name_item = self.library_table.item(row, 1)
                if name_item:
                    lib_id = name_item.data(Qt.ItemDataRole.UserRole)
                    selected.append(lib_id)
        return selected
    
    def download_selected_libraries(self):
        """下载选中的库 - 增强异常处理"""
        try:
            selected = self.get_selected_libraries()
            if not selected:
                QMessageBox.warning(self, "警告", "请先选择要下载的库")
                return

            # 显示确认对话框
            reply = QMessageBox.question(
                self, "确认下载",
                f"确定要下载 {len(selected)} 个库吗？\n\n这可能需要一些时间，请确保网络连接稳定。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.start_download(selected)

        except Exception as e:
            logger.error(f"启动选中库下载失败: {e}")
            QMessageBox.critical(self, "错误", f"启动下载失败: {str(e)}")

    def download_all_libraries(self):
        """下载所有库 - 增强异常处理"""
        try:
            all_libs = list(self.library_manager.get_available_libraries().keys())

            if not all_libs:
                QMessageBox.information(self, "提示", "没有可用的库")
                return

            # 显示确认对话框
            reply = QMessageBox.question(
                self, "确认下载",
                f"确定要下载所有 {len(all_libs)} 个库吗？\n\n这可能需要较长时间，请确保：\n"
                "• 网络连接稳定\n• 磁盘空间充足\n• 有足够的时间等待",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.start_download(all_libs)

        except Exception as e:
            logger.error(f"启动全部库下载失败: {e}")
            QMessageBox.critical(self, "错误", f"启动下载失败: {str(e)}")

    def start_download(self, lib_ids):
        """开始下载 - 增强异常处理"""
        try:
            if self.download_thread and self.download_thread.isRunning():
                QMessageBox.warning(self, "警告", "下载正在进行中，请等待完成")
                return

            if not lib_ids:
                QMessageBox.warning(self, "警告", "没有要下载的库")
                return

            # 禁用按钮
            self.download_selected_btn.setEnabled(False)
            self.download_all_btn.setEnabled(False)
            self.refresh_btn.setEnabled(False)

            # 显示进度条
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, len(lib_ids))
            self.progress_bar.setValue(0)

            # 更新状态显示
            self.update_status_display("准备下载...")

            # 创建下载线程
            self.download_thread = LibraryDownloadThread(self.library_manager, lib_ids)
            self.download_thread.progress_update.connect(self.on_download_progress)
            self.download_thread.download_complete.connect(self.on_download_complete)
            self.download_thread.all_complete.connect(self.on_all_downloads_complete)
            self.download_thread.error_occurred.connect(self.on_download_error)

            self.download_thread.start()
            logger.info(f"开始下载 {len(lib_ids)} 个库")

        except Exception as e:
            logger.error(f"启动下载失败: {e}")
            self.reset_download_ui()
            QMessageBox.critical(self, "错误", f"启动下载失败: {str(e)}")

    def on_download_progress(self, lib_id, status):
        """下载进度更新 - 增强显示"""
        try:
            logger.info(f"库 {lib_id}: {status}")
            self.update_library_status_in_table(lib_id, status)
            self.update_status_display(f"正在处理: {lib_id} - {status}")

        except Exception as e:
            logger.error(f"更新下载进度失败: {e}")

    def on_download_complete(self, lib_id, success, error_msg=""):
        """单个库下载完成 - 增强处理"""
        try:
            current_value = self.progress_bar.value()
            self.progress_bar.setValue(current_value + 1)

            # 更新表格状态
            status = "已安装" if success else f"失败: {error_msg}"
            self.update_library_status_in_table(lib_id, status)

            if success:
                logger.info(f"库 {lib_id} 下载成功")
            else:
                logger.warning(f"库 {lib_id} 下载失败: {error_msg}")

        except Exception as e:
            logger.error(f"处理下载完成事件失败: {e}")

    def on_download_error(self, lib_id, error_msg):
        """下载错误处理"""
        try:
            logger.error(f"库 {lib_id} 下载错误: {error_msg}")
            self.update_library_status_in_table(lib_id, f"错误: {error_msg}")

            # 显示错误通知（但不阻塞其他下载）
            self.show_error_notification(lib_id, error_msg)

        except Exception as e:
            logger.error(f"处理下载错误失败: {e}")

    def update_library_status_in_table(self, lib_id, status):
        """更新表格中的库状态"""
        try:
            for row in range(self.library_table.rowCount()):
                name_item = self.library_table.item(row, 1)  # 名称列
                if name_item and name_item.data(Qt.ItemDataRole.UserRole) == lib_id:
                    status_item = self.library_table.item(row, 2)  # 状态列
                    if status_item:
                        status_item.setText(status)

                        # 根据状态设置颜色
                        if "成功" in status or "已安装" in status:
                            status_item.setBackground(QColor(200, 255, 200))
                        elif "失败" in status or "错误" in status:
                            status_item.setBackground(QColor(255, 200, 200))
                        elif "下载中" in status:
                            status_item.setBackground(QColor(255, 255, 200))
                    break

        except Exception as e:
            logger.error(f"更新表格状态失败: {e}")

    def update_status_display(self, message):
        """更新状态显示"""
        try:
            # 如果有状态标签，更新它
            if hasattr(self, 'status_label'):
                self.status_label.setText(message)

            # 更新窗口标题
            if hasattr(self, 'parent') and self.parent():
                original_title = "库管理器"
                self.parent().setWindowTitle(f"{original_title} - {message}")

        except Exception as e:
            logger.error(f"更新状态显示失败: {e}")

    def show_error_notification(self, lib_id, error_msg):
        """显示错误通知"""
        try:
            # 这里可以实现非阻塞的错误通知
            # 比如状态栏消息、系统通知等
            logger.warning(f"库 {lib_id} 错误通知: {error_msg}")

        except Exception as e:
            logger.error(f"显示错误通知失败: {e}")

    def reset_download_ui(self):
        """重置下载UI状态"""
        try:
            # 启用按钮
            self.download_selected_btn.setEnabled(True)
            self.download_all_btn.setEnabled(True)
            self.refresh_btn.setEnabled(True)

            # 隐藏进度条
            self.progress_bar.setVisible(False)
            self.progress_bar.setValue(0)

            # 重置状态显示
            self.update_status_display("就绪")

        except Exception as e:
            logger.error(f"重置下载UI失败: {e}")

    def on_all_downloads_complete(self, results):
        """所有下载完成 - 增强结果处理"""
        try:
            # 重置UI状态
            self.reset_download_ui()

            # 刷新库状态
            self.load_library_status()

            # 分析结果
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            failed_count = total_count - success_count

            # 生成详细报告
            success_libs = [lib_id for lib_id, success in results.items() if success]
            failed_libs = [lib_id for lib_id, success in results.items() if not success]

            # 显示结果对话框
            if success_count == total_count:
                QMessageBox.information(
                    self, "下载完成",
                    f"🎉 所有 {total_count} 个库下载成功！\n\n"
                    f"成功下载的库：\n" + "\n".join([f"• {lib}" for lib in success_libs])
                )
                logger.info(f"所有库下载成功: {success_libs}")
            else:
                # 构建详细的失败报告
                message = f"下载完成：{success_count} 成功，{failed_count} 失败\n\n"

                if success_libs:
                    message += f"✅ 成功下载 ({success_count})：\n"
                    message += "\n".join([f"• {lib}" for lib in success_libs[:5]])  # 最多显示5个
                    if len(success_libs) > 5:
                        message += f"\n• ... 还有 {len(success_libs) - 5} 个"
                    message += "\n\n"

                if failed_libs:
                    message += f"❌ 下载失败 ({failed_count})：\n"
                    message += "\n".join([f"• {lib}" for lib in failed_libs[:5]])  # 最多显示5个
                    if len(failed_libs) > 5:
                        message += f"\n• ... 还有 {len(failed_libs) - 5} 个"
                    message += "\n\n建议检查网络连接后重试失败的库。"

                QMessageBox.warning(self, "下载完成", message)
                logger.warning(f"部分库下载失败 - 成功: {success_libs}, 失败: {failed_libs}")

            # 更新统计信息
            self.update_download_statistics(success_count, failed_count)

        except Exception as e:
            logger.error(f"处理下载完成事件失败: {e}")
            # 至少要重置UI状态
            self.reset_download_ui()
            QMessageBox.critical(self, "错误", f"处理下载结果时发生错误: {str(e)}")

    def update_download_statistics(self, success_count, failed_count):
        """更新下载统计信息"""
        try:
            # 这里可以更新统计显示，比如状态栏信息
            total = success_count + failed_count
            if hasattr(self, 'stats_label'):
                self.stats_label.setText(
                    f"本次下载: {success_count}/{total} 成功"
                )

            logger.info(f"下载统计 - 成功: {success_count}, 失败: {failed_count}")

        except Exception as e:
            logger.error(f"更新下载统计失败: {e}")
        
        logger.info(f"下载完成：{success_count}/{total_count} 成功")
    
    def get_library_preferences(self):
        """获取库偏好设置"""
        return {
            "auto_inject": self.auto_inject_checkbox.isChecked(),
            "prefer_local": self.prefer_local_checkbox.isChecked()
        }
    
    def set_library_preferences(self, auto_inject: bool, prefer_local: bool):
        """设置库偏好"""
        self.auto_inject_checkbox.setChecked(auto_inject)
        self.prefer_local_checkbox.setChecked(prefer_local)

    # 增强搜索和筛选功能
    def on_search_changed(self, text: str):
        """搜索文本改变事件"""
        try:
            self.search_query = text.strip().lower()
            self.apply_filters()

        except Exception as e:
            logger.error(f"搜索失败: {e}")

    def on_filter_changed(self):
        """筛选条件改变事件"""
        try:
            self.category_filter = self.category_combo.currentText()
            self.status_filter = self.status_combo.currentText()
            self.apply_filters()

        except Exception as e:
            logger.error(f"筛选失败: {e}")

    def show_search_options(self):
        """显示搜索选项对话框"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox

            dialog = QDialog(self)
            dialog.setWindowTitle("搜索选项")
            dialog.setMinimumSize(300, 200)

            layout = QVBoxLayout(dialog)

            # 搜索范围选项
            layout.addWidget(QLabel("搜索范围:"))

            self.search_name_cb = QCheckBox("库名称")
            self.search_name_cb.setChecked(True)
            layout.addWidget(self.search_name_cb)

            self.search_desc_cb = QCheckBox("描述")
            self.search_desc_cb.setChecked(True)
            layout.addWidget(self.search_desc_cb)

            self.search_tags_cb = QCheckBox("标签")
            self.search_tags_cb.setChecked(True)
            layout.addWidget(self.search_tags_cb)

            self.search_author_cb = QCheckBox("作者")
            self.search_author_cb.setChecked(False)
            layout.addWidget(self.search_author_cb)

            # 搜索模式
            layout.addWidget(QLabel("搜索模式:"))

            self.fuzzy_search_cb = QCheckBox("模糊搜索")
            self.fuzzy_search_cb.setChecked(True)
            layout.addWidget(self.fuzzy_search_cb)

            self.case_sensitive_cb = QCheckBox("区分大小写")
            self.case_sensitive_cb.setChecked(False)
            layout.addWidget(self.case_sensitive_cb)

            # 按钮
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.apply_filters()

        except Exception as e:
            logger.error(f"显示搜索选项失败: {e}")

    def apply_filters(self):
        """应用搜索和筛选条件"""
        try:
            # 获取所有库
            all_libraries = self.library_manager.get_available_libraries()

            # 应用筛选
            filtered_libraries = {}

            for lib_id, library in all_libraries.items():
                # 搜索筛选
                if self.search_query and not self.matches_search(library):
                    continue

                # 分类筛选
                if self.category_filter != "全部" and not self.matches_category(library):
                    continue

                # 状态筛选
                if self.status_filter != "全部" and not self.matches_status(library):
                    continue

                filtered_libraries[lib_id] = library

            # 更新显示
            self.update_library_display(filtered_libraries)

            # 更新状态栏
            total_count = len(all_libraries)
            filtered_count = len(filtered_libraries)
            self.update_status_message(f"显示 {filtered_count}/{total_count} 个库")

        except Exception as e:
            logger.error(f"应用筛选失败: {e}")

    def matches_search(self, library) -> bool:
        """检查库是否匹配搜索条件"""
        try:
            if not self.search_query:
                return True

            search_text = self.search_query

            # 检查库名称
            if hasattr(self, 'search_name_cb') and self.search_name_cb.isChecked():
                if search_text in library.name.lower():
                    return True

            # 检查描述
            if hasattr(self, 'search_desc_cb') and self.search_desc_cb.isChecked():
                if hasattr(library, 'description') and search_text in library.description.lower():
                    return True

            # 检查标签
            if hasattr(self, 'search_tags_cb') and self.search_tags_cb.isChecked():
                if hasattr(library, 'tags'):
                    for tag in library.tags:
                        if search_text in tag.lower():
                            return True

            # 简单的名称和描述搜索（默认行为）
            if not hasattr(self, 'search_name_cb'):
                if (search_text in library.name.lower() or
                    (hasattr(library, 'description') and search_text in library.description.lower())):
                    return True

            return False

        except Exception as e:
            logger.error(f"搜索匹配失败: {e}")
            return True

    def matches_category(self, library) -> bool:
        """检查库是否匹配分类条件"""
        try:
            if self.category_filter == "全部":
                return True

            # 根据库名称和描述判断分类
            lib_name = library.name.lower()
            lib_desc = getattr(library, 'description', '').lower()

            category_keywords = {
                "动画库": ["gsap", "anime", "velocity", "tween", "motion", "animation"],
                "3D图形": ["three", "babylon", "webgl", "3d", "graphics"],
                "UI框架": ["react", "vue", "angular", "bootstrap", "material"],
                "工具库": ["lodash", "underscore", "moment", "axios", "jquery"],
                "图表库": ["chart", "d3", "echarts", "highcharts", "plot"],
                "音频库": ["howler", "tone", "audio", "sound", "music"],
                "视频库": ["video", "player", "media", "stream"],
                "游戏引擎": ["phaser", "pixi", "game", "engine"],
                "数据处理": ["data", "json", "xml", "csv", "parse"]
            }

            if self.category_filter in category_keywords:
                keywords = category_keywords[self.category_filter]
                for keyword in keywords:
                    if keyword in lib_name or keyword in lib_desc:
                        return True

            return False

        except Exception as e:
            logger.error(f"分类匹配失败: {e}")
            return True

    def matches_status(self, library) -> bool:
        """检查库是否匹配状态条件"""
        try:
            if self.status_filter == "全部":
                return True

            if self.status_filter == "已安装":
                return library.is_downloaded
            elif self.status_filter == "未安装":
                return not library.is_downloaded
            elif self.status_filter == "有更新":
                # 这里需要实现版本比较逻辑
                return False  # 简化处理
            elif self.status_filter == "已过期":
                # 这里需要实现过期检查逻辑
                return False  # 简化处理
            elif self.status_filter == "收藏":
                return getattr(library, 'is_favorite', False)

            return True

        except Exception as e:
            logger.error(f"状态匹配失败: {e}")
            return True

    def update_library_display(self, libraries: dict):
        """更新库显示"""
        try:
            self.library_table.setRowCount(0)

            for lib_id, library in libraries.items():
                row = self.library_table.rowCount()
                self.library_table.insertRow(row)

                # 选择框
                checkbox = QCheckBox()
                self.library_table.setCellWidget(row, 0, checkbox)

                # 库名
                name_item = QTableWidgetItem(library.name)
                name_item.setData(Qt.ItemDataRole.UserRole, lib_id)
                self.library_table.setItem(row, 1, name_item)

                # 当前版本
                current_version = library.version if library.is_downloaded else "未安装"
                self.library_table.setItem(row, 2, QTableWidgetItem(current_version))

                # 最新版本
                latest_version = getattr(library, 'latest_version', library.version)
                self.library_table.setItem(row, 3, QTableWidgetItem(latest_version))

                # 状态
                if library.is_downloaded:
                    if current_version != latest_version:
                        status = "有更新"
                        status_item = QTableWidgetItem(status)
                        status_item.setBackground(QColor(255, 193, 7))  # 黄色
                    else:
                        status = "已安装"
                        status_item = QTableWidgetItem(status)
                        status_item.setBackground(QColor(40, 167, 69))  # 绿色
                else:
                    status = "未安装"
                    status_item = QTableWidgetItem(status)
                    status_item.setBackground(QColor(220, 53, 69))  # 红色

                self.library_table.setItem(row, 4, status_item)

                # 大小
                size = getattr(library, 'size', "未知")
                self.library_table.setItem(row, 5, QTableWidgetItem(size))

                # 评分
                rating = getattr(library, 'rating', 0.0)
                rating_text = f"⭐ {rating:.1f}" if rating > 0 else "未评分"
                self.library_table.setItem(row, 6, QTableWidgetItem(rating_text))

                # 下载量
                downloads = getattr(library, 'downloads', 0)
                if downloads > 1000000:
                    downloads_text = f"{downloads/1000000:.1f}M"
                elif downloads > 1000:
                    downloads_text = f"{downloads/1000:.1f}K"
                else:
                    downloads_text = str(downloads)
                self.library_table.setItem(row, 7, QTableWidgetItem(downloads_text))

                # 更新日期
                update_date = getattr(library, 'update_date', "未知")
                self.library_table.setItem(row, 8, QTableWidgetItem(update_date))

            logger.info(f"更新库显示: {len(libraries)} 个库")

        except Exception as e:
            logger.error(f"更新库显示失败: {e}")

    def update_status_message(self, message: str):
        """更新状态栏消息"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.setText(message)

        except Exception as e:
            logger.error(f"更新状态消息失败: {e}")

    # 版本管理功能
    def check_for_updates(self):
        """检查库更新"""
        try:
            # 这里应该实现实际的版本检查逻辑
            # 可以从CDN或GitHub API获取最新版本信息

            libraries = self.library_manager.get_available_libraries()
            updates_available = []

            for lib_id, library in libraries.items():
                if library.is_downloaded:
                    # 模拟版本检查
                    current_version = library.version
                    latest_version = self.get_latest_version(lib_id)

                    if latest_version and current_version != latest_version:
                        updates_available.append({
                            'lib_id': lib_id,
                            'name': library.name,
                            'current': current_version,
                            'latest': latest_version
                        })

            if updates_available:
                self.show_update_dialog(updates_available)
            else:
                QMessageBox.information(self, "检查更新", "所有库都是最新版本")

        except Exception as e:
            logger.error(f"检查更新失败: {e}")
            QMessageBox.warning(self, "错误", "检查更新失败")

    def get_latest_version(self, lib_id: str) -> str:
        """获取库的最新版本"""
        try:
            # 这里应该实现实际的版本获取逻辑
            # 可以从CDN API或GitHub API获取

            # 模拟返回最新版本
            version_map = {
                "three.js": "r150",
                "gsap": "3.12.5",
                "anime.js": "3.2.2",
                "p5.js": "1.5.0",
                "d3.js": "7.8.0",
                "lottie": "5.10.0"
            }

            return version_map.get(lib_id, None)

        except Exception as e:
            logger.error(f"获取最新版本失败: {e}")
            return None

    def show_update_dialog(self, updates: list):
        """显示更新对话框"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QDialogButtonBox

            dialog = QDialog(self)
            dialog.setWindowTitle("可用更新")
            dialog.setMinimumSize(500, 300)

            layout = QVBoxLayout(dialog)

            # 更新列表
            update_table = QTableWidget()
            update_table.setColumnCount(4)
            update_table.setHorizontalHeaderLabels(["选择", "库名", "当前版本", "最新版本"])

            for i, update in enumerate(updates):
                update_table.insertRow(i)

                # 选择框
                checkbox = QCheckBox()
                checkbox.setChecked(True)
                update_table.setCellWidget(i, 0, checkbox)

                # 库名
                update_table.setItem(i, 1, QTableWidgetItem(update['name']))

                # 当前版本
                update_table.setItem(i, 2, QTableWidgetItem(update['current']))

                # 最新版本
                update_table.setItem(i, 3, QTableWidgetItem(update['latest']))

            layout.addWidget(update_table)

            # 按钮
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 执行更新
                selected_updates = []
                for i in range(update_table.rowCount()):
                    checkbox = update_table.cellWidget(i, 0)
                    if checkbox.isChecked():
                        selected_updates.append(updates[i])

                if selected_updates:
                    self.perform_updates(selected_updates)

        except Exception as e:
            logger.error(f"显示更新对话框失败: {e}")

    def perform_updates(self, updates: list):
        """执行库更新"""
        try:
            # 这里应该实现实际的更新逻辑
            for update in updates:
                lib_id = update['lib_id']
                # 重新下载库文件
                result = self.library_manager.download_library(lib_id)
                if result['success']:
                    logger.info(f"更新库 {update['name']} 成功")
                else:
                    logger.error(f"更新库 {update['name']} 失败: {result['message']}")

            # 刷新显示
            self.apply_filters()

            QMessageBox.information(self, "更新完成", f"已更新 {len(updates)} 个库")

        except Exception as e:
            logger.error(f"执行更新失败: {e}")
            QMessageBox.warning(self, "错误", "更新失败")

    def show_library_details(self, item):
        """显示库详情对话框"""
        try:
            # 获取库ID
            row = item.row()
            name_item = self.library_table.item(row, 1)
            lib_id = name_item.data(Qt.ItemDataRole.UserRole)

            if lib_id:
                # 获取库信息
                libraries = self.library_manager.get_available_libraries()
                if lib_id in libraries:
                    library = libraries[lib_id]

                    # 显示详情对话框
                    from ui.library_details_dialog import LibraryDetailsDialog

                    details_dialog = LibraryDetailsDialog(library, lib_id, self)
                    details_dialog.library_installed.connect(self.on_library_installed)
                    details_dialog.library_uninstalled.connect(self.on_library_uninstalled)
                    details_dialog.library_favorited.connect(self.on_library_favorited)
                    details_dialog.exec()

        except Exception as e:
            logger.error(f"显示库详情失败: {e}")

    def on_library_installed(self, lib_id: str):
        """库安装事件处理"""
        try:
            # 执行安装
            result = self.library_manager.download_library(lib_id)
            if result['success']:
                QMessageBox.information(self, "成功", f"库 {lib_id} 安装成功")
                self.apply_filters()  # 刷新显示
            else:
                QMessageBox.warning(self, "失败", f"库 {lib_id} 安装失败: {result['message']}")

        except Exception as e:
            logger.error(f"处理库安装事件失败: {e}")

    def on_library_uninstalled(self, lib_id: str):
        """库卸载事件处理"""
        try:
            # 执行卸载（删除本地文件）
            libraries = self.library_manager.get_available_libraries()
            if lib_id in libraries:
                library = libraries[lib_id]
                if library.local_path:
                    local_file = self.library_manager.libraries_dir / library.local_path
                    if local_file.exists():
                        local_file.unlink()
                        library.is_downloaded = False
                        QMessageBox.information(self, "成功", f"库 {lib_id} 卸载成功")
                        self.apply_filters()  # 刷新显示
                    else:
                        QMessageBox.warning(self, "警告", "库文件不存在")

        except Exception as e:
            logger.error(f"处理库卸载事件失败: {e}")
            QMessageBox.warning(self, "错误", "卸载失败")

    def on_library_favorited(self, lib_id: str, is_favorite: bool):
        """库收藏事件处理"""
        try:
            # 保存收藏状态
            libraries = self.library_manager.get_available_libraries()
            if lib_id in libraries:
                library = libraries[lib_id]
                library.is_favorite = is_favorite

                # 这里应该保存到配置文件
                action = "添加到收藏" if is_favorite else "取消收藏"
                logger.info(f"{action}: {lib_id}")

        except Exception as e:
            logger.error(f"处理库收藏事件失败: {e}")

    # 智能推荐功能
    def generate_recommendations(self):
        """生成库推荐"""
        try:
            # 基于使用历史和项目类型推荐库
            recommendations = []

            # 获取当前项目信息（这里简化处理）
            project_type = "animation"  # 可以从项目配置获取

            # 推荐规则
            if project_type == "animation":
                recommendations.extend([
                    ("gsap", "高性能动画库，适合复杂动画"),
                    ("anime.js", "轻量级动画库，易于学习"),
                    ("lottie", "After Effects动画播放器")
                ])

            if project_type == "3d":
                recommendations.extend([
                    ("three.js", "强大的3D图形库"),
                    ("babylon.js", "专业的3D引擎")
                ])

            # 基于流行度推荐
            popular_libs = [
                ("d3.js", "数据可视化首选"),
                ("p5.js", "创意编程库")
            ]
            recommendations.extend(popular_libs)

            return recommendations[:5]  # 返回前5个推荐

        except Exception as e:
            logger.error(f"生成推荐失败: {e}")
            return []

    def update_recommendations_display(self):
        """更新推荐显示"""
        try:
            recommendations = self.generate_recommendations()

            # 更新推荐标签页的显示
            if hasattr(self, 'recommendations_list'):
                self.recommendations_list.clear()

                for lib_id, reason in recommendations:
                    item_text = f"{lib_id} - {reason}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, lib_id)
                    self.recommendations_list.addItem(item)

        except Exception as e:
            logger.error(f"更新推荐显示失败: {e}")

    # 批量操作功能
    def select_all_libraries(self):
        """全选库"""
        try:
            for row in range(self.library_table.rowCount()):
                checkbox = self.library_table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(True)

        except Exception as e:
            logger.error(f"全选失败: {e}")

    def select_none_libraries(self):
        """取消全选"""
        try:
            for row in range(self.library_table.rowCount()):
                checkbox = self.library_table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(False)

        except Exception as e:
            logger.error(f"取消全选失败: {e}")

    def get_selected_libraries(self):
        """获取选中的库"""
        try:
            selected_libs = []

            for row in range(self.library_table.rowCount()):
                checkbox = self.library_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked():
                    name_item = self.library_table.item(row, 1)
                    lib_id = name_item.data(Qt.ItemDataRole.UserRole)
                    if lib_id:
                        selected_libs.append(lib_id)

            return selected_libs

        except Exception as e:
            logger.error(f"获取选中库失败: {e}")
            return []

    def batch_install_libraries(self):
        """批量安装库"""
        try:
            selected_libs = self.get_selected_libraries()
            if not selected_libs:
                QMessageBox.warning(self, "警告", "请先选择要安装的库")
                return

            # 确认安装
            reply = QMessageBox.question(
                self, "确认安装",
                f"确定要安装选中的 {len(selected_libs)} 个库吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 执行批量安装
                self.start_batch_download(selected_libs)

        except Exception as e:
            logger.error(f"批量安装失败: {e}")
            QMessageBox.warning(self, "错误", "批量安装失败")

    def batch_update_libraries(self):
        """批量更新库"""
        try:
            # 检查哪些库有更新
            libraries = self.library_manager.get_available_libraries()
            update_libs = []

            for lib_id, library in libraries.items():
                if library.is_downloaded:
                    # 检查是否有更新（这里简化处理）
                    latest_version = self.get_latest_version(lib_id)
                    if latest_version and library.version != latest_version:
                        update_libs.append(lib_id)

            if not update_libs:
                QMessageBox.information(self, "提示", "所有库都是最新版本")
                return

            # 确认更新
            reply = QMessageBox.question(
                self, "确认更新",
                f"发现 {len(update_libs)} 个库有更新，是否立即更新？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 执行批量更新
                self.start_batch_download(update_libs)

        except Exception as e:
            logger.error(f"批量更新失败: {e}")
            QMessageBox.warning(self, "错误", "批量更新失败")
