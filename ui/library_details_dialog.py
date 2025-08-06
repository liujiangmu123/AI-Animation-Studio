"""
AI Animation Studio - 库详情对话框
提供JavaScript库的详细信息查看和管理功能
"""

from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QPushButton, QTextEdit, QGroupBox, QFormLayout, QProgressBar,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QScrollArea, QFrame, QSplitter, QCheckBox, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor

from core.js_library_manager import JSLibrary
from core.logger import get_logger

logger = get_logger("library_details_dialog")


class LibraryDetailsDialog(QDialog):
    """库详情对话框"""
    
    library_installed = pyqtSignal(str)  # 库安装信号
    library_uninstalled = pyqtSignal(str)  # 库卸载信号
    library_favorited = pyqtSignal(str, bool)  # 库收藏信号
    
    def __init__(self, library: JSLibrary, lib_id: str, parent=None):
        super().__init__(parent)
        
        self.library = library
        self.lib_id = lib_id
        self.is_favorite = getattr(library, 'is_favorite', False)
        
        self.setup_ui()
        self.load_library_info()
        
        logger.info(f"打开库详情: {library.name}")
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle(f"库详情 - {self.library.name}")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 顶部信息栏
        header = self.create_header()
        layout.addWidget(header)
        
        # 主要内容区域
        content_tabs = QTabWidget()
        
        # 基本信息标签页
        info_tab = self.create_info_tab()
        content_tabs.addTab(info_tab, "📋 基本信息")
        
        # 版本历史标签页
        versions_tab = self.create_versions_tab()
        content_tabs.addTab(versions_tab, "🔄 版本历史")
        
        # 依赖关系标签页
        dependencies_tab = self.create_dependencies_tab()
        content_tabs.addTab(dependencies_tab, "🔗 依赖关系")
        
        # 使用示例标签页
        examples_tab = self.create_examples_tab()
        content_tabs.addTab(examples_tab, "💡 使用示例")
        
        # 统计信息标签页
        stats_tab = self.create_stats_tab()
        content_tabs.addTab(stats_tab, "📊 统计信息")
        
        layout.addWidget(content_tabs)
        
        # 底部操作栏
        actions = self.create_actions()
        layout.addWidget(actions)
    
    def create_header(self):
        """创建顶部信息栏"""
        header = QFrame()
        header.setFrameStyle(QFrame.Shape.StyledPanel)
        header.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        # 左侧库信息
        info_layout = QVBoxLayout()
        
        # 库名和版本
        title_layout = QHBoxLayout()
        
        self.name_label = QLabel(self.library.name)
        self.name_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_layout.addWidget(self.name_label)
        
        self.version_label = QLabel(f"v{self.library.version}")
        self.version_label.setStyleSheet("color: #6c757d; font-size: 14px;")
        title_layout.addWidget(self.version_label)
        
        title_layout.addStretch()
        info_layout.addLayout(title_layout)
        
        # 描述
        self.description_label = QLabel(self.library.description)
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #495057; margin-top: 5px;")
        info_layout.addWidget(self.description_label)
        
        # 标签
        tags_layout = QHBoxLayout()
        tags = getattr(self.library, 'tags', ['JavaScript', '动画'])
        for tag in tags[:5]:  # 最多显示5个标签
            tag_label = QLabel(tag)
            tag_label.setStyleSheet("""
                background-color: #007bff;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 12px;
            """)
            tags_layout.addWidget(tag_label)
        
        tags_layout.addStretch()
        info_layout.addLayout(tags_layout)
        
        layout.addLayout(info_layout)
        
        # 右侧状态信息
        status_layout = QVBoxLayout()
        
        # 安装状态
        status_text = "已安装" if self.library.is_downloaded else "未安装"
        status_color = "#28a745" if self.library.is_downloaded else "#dc3545"
        
        self.status_label = QLabel(status_text)
        self.status_label.setStyleSheet(f"""
            background-color: {status_color};
            color: white;
            padding: 5px 15px;
            border-radius: 15px;
            font-weight: bold;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        # 评分
        rating = getattr(self.library, 'rating', 0.0)
        rating_text = f"⭐ {rating:.1f}/5.0" if rating > 0 else "未评分"
        self.rating_label = QLabel(rating_text)
        self.rating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.rating_label)
        
        # 大小
        size = getattr(self.library, 'size', "未知")
        self.size_label = QLabel(f"大小: {size}")
        self.size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.size_label)
        
        layout.addLayout(status_layout)
        
        return header
    
    def create_info_tab(self):
        """创建基本信息标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 基本信息
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("库名称:", QLabel(self.library.name))
        info_layout.addRow("版本:", QLabel(self.library.version))
        info_layout.addRow("描述:", QLabel(self.library.description))
        
        # 扩展信息
        author = getattr(self.library, 'author', '未知')
        info_layout.addRow("作者:", QLabel(author))
        
        license_info = getattr(self.library, 'license', '未知')
        info_layout.addRow("许可证:", QLabel(license_info))
        
        homepage = getattr(self.library, 'homepage', '未知')
        homepage_label = QLabel(f'<a href="{homepage}">{homepage}</a>')
        homepage_label.setOpenExternalLinks(True)
        info_layout.addRow("主页:", homepage_label)
        
        layout.addWidget(info_group)
        
        # CDN信息
        cdn_group = QGroupBox("CDN信息")
        cdn_layout = QFormLayout(cdn_group)
        
        cdn_layout.addRow("CDN URL:", QLabel(self.library.url))
        
        # 本地路径
        local_path = getattr(self.library, 'local_path', '未设置')
        cdn_layout.addRow("本地路径:", QLabel(local_path))
        
        layout.addWidget(cdn_group)
        
        # 功能特性
        features_group = QGroupBox("功能特性")
        features_layout = QVBoxLayout(features_group)
        
        features = getattr(self.library, 'features', [
            "高性能动画", "易于使用", "跨浏览器兼容", "丰富的API"
        ])
        
        for feature in features:
            feature_item = QLabel(f"• {feature}")
            features_layout.addWidget(feature_item)
        
        layout.addWidget(features_group)
        
        layout.addStretch()
        
        return tab
    
    def create_versions_tab(self):
        """创建版本历史标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 版本列表
        self.versions_table = QTableWidget()
        self.versions_table.setColumnCount(4)
        self.versions_table.setHorizontalHeaderLabels([
            "版本", "发布日期", "大小", "状态"
        ])
        
        # 模拟版本数据
        versions = [
            (self.library.version, "2024-01-15", "120KB", "当前版本"),
            ("3.12.4", "2023-12-10", "118KB", "历史版本"),
            ("3.12.3", "2023-11-05", "115KB", "历史版本"),
            ("3.12.2", "2023-10-20", "112KB", "历史版本"),
        ]
        
        for i, (version, date, size, status) in enumerate(versions):
            self.versions_table.insertRow(i)
            self.versions_table.setItem(i, 0, QTableWidgetItem(version))
            self.versions_table.setItem(i, 1, QTableWidgetItem(date))
            self.versions_table.setItem(i, 2, QTableWidgetItem(size))
            
            status_item = QTableWidgetItem(status)
            if status == "当前版本":
                status_item.setBackground(QColor(40, 167, 69))
            self.versions_table.setItem(i, 3, status_item)
        
        layout.addWidget(self.versions_table)
        
        # 版本操作
        version_actions = QHBoxLayout()
        
        self.install_version_btn = QPushButton("安装选中版本")
        self.install_version_btn.clicked.connect(self.install_selected_version)
        version_actions.addWidget(self.install_version_btn)
        
        self.compare_versions_btn = QPushButton("版本对比")
        self.compare_versions_btn.clicked.connect(self.compare_versions)
        version_actions.addWidget(self.compare_versions_btn)
        
        version_actions.addStretch()
        
        layout.addLayout(version_actions)
        
        return tab
    
    def create_dependencies_tab(self):
        """创建依赖关系标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 依赖库
        deps_group = QGroupBox("依赖库")
        deps_layout = QVBoxLayout(deps_group)
        
        dependencies = getattr(self.library, 'dependencies', [])
        if dependencies:
            for dep in dependencies:
                dep_item = QLabel(f"• {dep}")
                deps_layout.addWidget(dep_item)
        else:
            deps_layout.addWidget(QLabel("无依赖"))
        
        layout.addWidget(deps_group)
        
        # 被依赖
        dependents_group = QGroupBox("被以下库依赖")
        dependents_layout = QVBoxLayout(dependents_group)
        
        dependents = getattr(self.library, 'dependents', [])
        if dependents:
            for dep in dependents:
                dep_item = QLabel(f"• {dep}")
                dependents_layout.addWidget(dep_item)
        else:
            dependents_layout.addWidget(QLabel("暂无"))
        
        layout.addWidget(dependents_group)
        
        layout.addStretch()
        
        return tab
    
    def create_examples_tab(self):
        """创建使用示例标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 示例代码
        examples_group = QGroupBox("使用示例")
        examples_layout = QVBoxLayout(examples_group)
        
        # 基本用法
        basic_example = QTextEdit()
        basic_example.setReadOnly(True)
        basic_example.setFont(QFont("Consolas", 10))
        basic_example.setMaximumHeight(150)
        
        # 根据库类型生成示例代码
        if "gsap" in self.library.name.lower():
            example_code = '''// GSAP 基本动画示例
gsap.to(".my-element", {
    duration: 2,
    x: 100,
    rotation: 360,
    ease: "bounce.out"
});'''
        elif "three" in self.library.name.lower():
            example_code = '''// Three.js 基本场景示例
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);'''
        else:
            example_code = f'''// {self.library.name} 基本用法示例
// 请参考官方文档获取详细使用方法
console.log("Hello {self.library.name}!");'''
        
        basic_example.setPlainText(example_code)
        examples_layout.addWidget(QLabel("基本用法:"))
        examples_layout.addWidget(basic_example)
        
        layout.addWidget(examples_group)
        
        # 在线资源
        resources_group = QGroupBox("学习资源")
        resources_layout = QVBoxLayout(resources_group)
        
        resources = [
            ("官方文档", "https://example.com/docs"),
            ("GitHub仓库", "https://github.com/example/repo"),
            ("教程视频", "https://youtube.com/example"),
            ("社区论坛", "https://forum.example.com")
        ]
        
        for name, url in resources:
            resource_label = QLabel(f'<a href="{url}">{name}</a>')
            resource_label.setOpenExternalLinks(True)
            resources_layout.addWidget(resource_label)
        
        layout.addWidget(resources_group)
        
        layout.addStretch()
        
        return tab
    
    def create_stats_tab(self):
        """创建统计信息标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 下载统计
        download_group = QGroupBox("下载统计")
        download_layout = QFormLayout(download_group)
        
        total_downloads = getattr(self.library, 'total_downloads', 1000000)
        download_layout.addRow("总下载量:", QLabel(f"{total_downloads:,}"))
        
        weekly_downloads = getattr(self.library, 'weekly_downloads', 50000)
        download_layout.addRow("周下载量:", QLabel(f"{weekly_downloads:,}"))
        
        monthly_downloads = getattr(self.library, 'monthly_downloads', 200000)
        download_layout.addRow("月下载量:", QLabel(f"{monthly_downloads:,}"))
        
        layout.addWidget(download_group)
        
        # 评分统计
        rating_group = QGroupBox("评分统计")
        rating_layout = QFormLayout(rating_group)
        
        avg_rating = getattr(self.library, 'rating', 4.5)
        rating_layout.addRow("平均评分:", QLabel(f"{avg_rating:.1f}/5.0"))
        
        total_ratings = getattr(self.library, 'total_ratings', 1500)
        rating_layout.addRow("评分人数:", QLabel(f"{total_ratings:,}"))
        
        layout.addWidget(rating_group)
        
        # 使用趋势
        trend_group = QGroupBox("使用趋势")
        trend_layout = QVBoxLayout(trend_group)
        
        trend_label = QLabel("📈 使用量持续增长")
        trend_layout.addWidget(trend_label)
        
        # 这里可以添加图表组件
        
        layout.addWidget(trend_group)
        
        layout.addStretch()
        
        return tab
    
    def create_actions(self):
        """创建操作栏"""
        actions = QFrame()
        actions.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(actions)
        
        # 收藏按钮
        self.favorite_btn = QPushButton("⭐ 收藏" if not self.is_favorite else "💔 取消收藏")
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        layout.addWidget(self.favorite_btn)
        
        # 评分按钮
        self.rate_btn = QPushButton("📊 评分")
        self.rate_btn.clicked.connect(self.rate_library)
        layout.addWidget(self.rate_btn)
        
        layout.addStretch()
        
        # 主要操作按钮
        if self.library.is_downloaded:
            self.main_btn = QPushButton("🗑️ 卸载")
            self.main_btn.clicked.connect(self.uninstall_library)
            self.main_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
        else:
            self.main_btn = QPushButton("📥 安装")
            self.main_btn.clicked.connect(self.install_library)
            self.main_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
        
        layout.addWidget(self.main_btn)
        
        # 关闭按钮
        close_btn = QPushButton("❌ 关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return actions
    
    def load_library_info(self):
        """加载库信息"""
        try:
            # 这里可以从网络获取更详细的库信息
            # 如GitHub API、npm API等
            pass
            
        except Exception as e:
            logger.error(f"加载库信息失败: {e}")
    
    def toggle_favorite(self):
        """切换收藏状态"""
        try:
            self.is_favorite = not self.is_favorite
            self.favorite_btn.setText("💔 取消收藏" if self.is_favorite else "⭐ 收藏")
            self.library_favorited.emit(self.lib_id, self.is_favorite)
            
        except Exception as e:
            logger.error(f"切换收藏状态失败: {e}")
    
    def rate_library(self):
        """评分库"""
        try:
            from PyQt6.QtWidgets import QInputDialog
            
            rating, ok = QInputDialog.getDouble(
                self, "库评分", 
                f"请为 {self.library.name} 评分 (1-5分):",
                value=3.0, min=1.0, max=5.0, decimals=1
            )
            
            if ok:
                # 这里应该保存评分到数据库或配置文件
                logger.info(f"用户评分: {self.library.name} = {rating}分")
            
        except Exception as e:
            logger.error(f"评分失败: {e}")
    
    def install_library(self):
        """安装库"""
        try:
            self.library_installed.emit(self.lib_id)
            self.close()
            
        except Exception as e:
            logger.error(f"安装库失败: {e}")
    
    def uninstall_library(self):
        """卸载库"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(
                self, "确认卸载",
                f"确定要卸载 {self.library.name} 吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.library_uninstalled.emit(self.lib_id)
                self.close()
            
        except Exception as e:
            logger.error(f"卸载库失败: {e}")
    
    def install_selected_version(self):
        """安装选中的版本"""
        try:
            current_row = self.versions_table.currentRow()
            if current_row >= 0:
                version = self.versions_table.item(current_row, 0).text()
                logger.info(f"安装版本: {version}")
                # 这里应该实现版本安装逻辑
            
        except Exception as e:
            logger.error(f"安装版本失败: {e}")
    
    def compare_versions(self):
        """版本对比"""
        try:
            # 这里应该实现版本对比功能
            logger.info("版本对比功能")
            
        except Exception as e:
            logger.error(f"版本对比失败: {e}")
