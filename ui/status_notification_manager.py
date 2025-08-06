"""
AI Animation Studio - 状态栏和通知系统管理器
实现专业的状态显示、进度跟踪、通知提醒和用户反馈系统
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QProgressBar, QStatusBar,
                             QSystemTrayIcon, QMenu, QApplication, QGraphicsOpacityEffect,
                             QScrollArea, QGroupBox, QTextEdit, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QPainter

from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional
import json

from core.logger import get_logger

logger = get_logger("status_notification_manager")


class NotificationType(Enum):
    """通知类型枚举"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    PROGRESS = "progress"


class StatusType(Enum):
    """状态类型枚举"""
    READY = "ready"
    WORKING = "working"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    SAVING = "saving"
    LOADING = "loading"


class NotificationItem:
    """通知项目"""
    
    def __init__(self, title: str, message: str, notification_type: NotificationType,
                 duration: int = 5000, action_text: str = None, action_callback=None):
        self.id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.title = title
        self.message = message
        self.type = notification_type
        self.duration = duration
        self.action_text = action_text
        self.action_callback = action_callback
        self.timestamp = datetime.now()
        self.is_read = False
        self.is_dismissed = False


class StatusBarWidget(QWidget):
    """专业状态栏组件"""
    
    def __init__(self):
        super().__init__()
        self.current_status = StatusType.READY
        self.progress_value = 0
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)
        
        # 主状态标签
        self.status_label = QLabel("📍 就绪")
        self.status_label.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self.status_label)
        
        # 分隔符
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setStyleSheet("color: #dee2e6;")
        layout.addWidget(separator1)
        
        # 选中元素信息
        self.selection_label = QLabel("🎯 无选择")
        self.selection_label.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self.selection_label)
        
        # 分隔符
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setStyleSheet("color: #dee2e6;")
        layout.addWidget(separator2)
        
        # 位置信息
        self.position_label = QLabel("📐 位置: (0,0)")
        self.position_label.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self.position_label)
        
        # 分隔符
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.VLine)
        separator3.setStyleSheet("color: #dee2e6;")
        layout.addWidget(separator3)
        
        # 保存状态
        self.save_label = QLabel("💾 已保存")
        self.save_label.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self.save_label)
        
        # 弹性空间
        layout.addStretch()
        
        # 进度条（默认隐藏）
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setFixedHeight(16)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: #f8f9fa;
                text-align: center;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #2C5AA0;
                border-radius: 7px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # 分隔符
        separator4 = QFrame()
        separator4.setFrameShape(QFrame.Shape.VLine)
        separator4.setStyleSheet("color: #dee2e6;")
        layout.addWidget(separator4)
        
        # 性能信息
        self.performance_label = QLabel("⚡ GPU: 45%")
        self.performance_label.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self.performance_label)
        
        # 分隔符
        separator5 = QFrame()
        separator5.setFrameShape(QFrame.Shape.VLine)
        separator5.setStyleSheet("color: #dee2e6;")
        layout.addWidget(separator5)
        
        # 协作信息
        self.collaboration_label = QLabel("👥 在线: 1人")
        self.collaboration_label.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self.collaboration_label)
        
        # 设置样式
        self.setStyleSheet("""
            StatusBarWidget {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }
            QLabel {
                color: #495057;
            }
        """)
    
    def update_status(self, status: StatusType, message: str = ""):
        """更新主状态"""
        self.current_status = status
        
        status_icons = {
            StatusType.READY: "📍",
            StatusType.WORKING: "⚙️",
            StatusType.PROCESSING: "🔄",
            StatusType.COMPLETED: "✅",
            StatusType.ERROR: "❌",
            StatusType.SAVING: "💾",
            StatusType.LOADING: "📂"
        }
        
        status_texts = {
            StatusType.READY: "就绪",
            StatusType.WORKING: "工作中",
            StatusType.PROCESSING: "处理中",
            StatusType.COMPLETED: "已完成",
            StatusType.ERROR: "错误",
            StatusType.SAVING: "保存中",
            StatusType.LOADING: "加载中"
        }
        
        icon = status_icons.get(status, "📍")
        text = message or status_texts.get(status, "未知状态")
        
        self.status_label.setText(f"{icon} {text}")
    
    def update_selection(self, element_name: str = None):
        """更新选中元素信息"""
        if element_name:
            self.selection_label.setText(f"🎯 选中: {element_name}")
        else:
            self.selection_label.setText("🎯 无选择")
    
    def update_position(self, x: int, y: int):
        """更新位置信息"""
        self.position_label.setText(f"📐 位置: ({x},{y})")
    
    def update_save_status(self, is_saved: bool, auto_save: bool = False):
        """更新保存状态"""
        if is_saved:
            if auto_save:
                self.save_label.setText("💾 自动保存")
            else:
                self.save_label.setText("💾 已保存")
        else:
            self.save_label.setText("💾 未保存*")
    
    def show_progress(self, value: int, text: str = ""):
        """显示进度条"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(value)
        if text:
            self.progress_bar.setFormat(f"{text} %p%")
        else:
            self.progress_bar.setFormat("%p%")
    
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.setVisible(False)
    
    def update_performance(self, gpu_usage: int, memory_usage: int = None):
        """更新性能信息"""
        if memory_usage is not None:
            self.performance_label.setText(f"⚡ GPU: {gpu_usage}% | 内存: {memory_usage}%")
        else:
            self.performance_label.setText(f"⚡ GPU: {gpu_usage}%")
    
    def update_collaboration(self, online_users: int, total_users: int = None):
        """更新协作信息"""
        if total_users is not None:
            self.collaboration_label.setText(f"👥 在线: {online_users}/{total_users}人")
        else:
            self.collaboration_label.setText(f"👥 在线: {online_users}人")


class NotificationWidget(QWidget):
    """通知弹窗组件"""
    
    dismissed = pyqtSignal(str)  # 通知被关闭信号
    action_clicked = pyqtSignal(str)  # 动作按钮点击信号
    
    def __init__(self, notification: NotificationItem):
        super().__init__()
        self.notification = notification
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setFixedSize(350, 100)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 主容器
        main_frame = QFrame()
        main_frame.setStyleSheet(self.get_notification_style())
        
        layout = QVBoxLayout(main_frame)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # 标题行
        title_layout = QHBoxLayout()
        
        # 图标
        icon_label = QLabel(self.get_notification_icon())
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        title_layout.addWidget(icon_label)
        
        # 标题
        title_label = QLabel(self.notification.title)
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.2);
                border-radius: 10px;
            }
        """)
        close_btn.clicked.connect(self.dismiss)
        title_layout.addWidget(close_btn)
        
        layout.addLayout(title_layout)
        
        # 消息内容
        message_label = QLabel(self.notification.message)
        message_label.setFont(QFont("Microsoft YaHei", 9))
        message_label.setStyleSheet("color: rgba(255,255,255,0.9);")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # 动作按钮（如果有）
        if self.notification.action_text:
            action_btn = QPushButton(self.notification.action_text)
            action_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255,255,255,0.2);
                    color: white;
                    border: 1px solid rgba(255,255,255,0.3);
                    border-radius: 4px;
                    padding: 4px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255,255,255,0.3);
                }
            """)
            action_btn.clicked.connect(self.on_action_clicked)
            layout.addWidget(action_btn)
        
        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_frame)
    
    def get_notification_icon(self) -> str:
        """获取通知图标"""
        icons = {
            NotificationType.INFO: "ℹ️",
            NotificationType.SUCCESS: "✅",
            NotificationType.WARNING: "⚠️",
            NotificationType.ERROR: "❌",
            NotificationType.PROGRESS: "🔄"
        }
        return icons.get(self.notification.type, "ℹ️")
    
    def get_notification_style(self) -> str:
        """获取通知样式"""
        colors = {
            NotificationType.INFO: "background-color: #2C5AA0;",
            NotificationType.SUCCESS: "background-color: #10B981;",
            NotificationType.WARNING: "background-color: #F59E0B;",
            NotificationType.ERROR: "background-color: #EF4444;",
            NotificationType.PROGRESS: "background-color: #6366F1;"
        }
        
        base_style = """
            QFrame {
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.2);
            }
        """
        
        return base_style + colors.get(self.notification.type, colors[NotificationType.INFO])
    
    def setup_animation(self):
        """设置动画"""
        # 透明度效果
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        # 淡入动画
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 淡出动画
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out_animation.finished.connect(self.close)
    
    def show_notification(self):
        """显示通知"""
        # 计算位置（右下角）
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 20
        y = screen.height() - self.height() - 50
        self.move(x, y)
        
        # 显示并播放淡入动画
        self.show()
        self.fade_in_animation.start()
        
        # 设置自动关闭定时器
        if self.notification.duration > 0:
            QTimer.singleShot(self.notification.duration, self.dismiss)
    
    def dismiss(self):
        """关闭通知"""
        self.fade_out_animation.start()
        self.dismissed.emit(self.notification.id)
    
    def on_action_clicked(self):
        """动作按钮点击处理"""
        self.action_clicked.emit(self.notification.id)
        if self.notification.action_callback:
            self.notification.action_callback()
        self.dismiss()


class NotificationCenter(QWidget):
    """通知中心"""
    
    def __init__(self):
        super().__init__()
        self.notifications: List[NotificationItem] = []
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setFixedSize(400, 600)
        self.setWindowTitle("通知中心")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题栏
        title_layout = QHBoxLayout()
        
        title_label = QLabel("🔔 通知中心")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 清空按钮
        clear_btn = QPushButton("清空全部")
        clear_btn.clicked.connect(self.clear_all_notifications)
        title_layout.addWidget(clear_btn)
        
        layout.addLayout(title_layout)
        
        # 通知列表
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        self.notifications_widget = QWidget()
        self.notifications_layout = QVBoxLayout(self.notifications_widget)
        self.notifications_layout.setSpacing(5)
        self.notifications_layout.addStretch()
        
        self.scroll_area.setWidget(self.notifications_widget)
        layout.addWidget(self.scroll_area)
    
    def add_notification_item(self, notification: NotificationItem):
        """添加通知项到中心"""
        self.notifications.append(notification)
        
        # 创建通知项组件
        item_widget = self.create_notification_item_widget(notification)
        
        # 插入到布局顶部
        self.notifications_layout.insertWidget(0, item_widget)
        
        # 限制通知数量
        if len(self.notifications) > 100:
            self.notifications = self.notifications[-100:]
            # 移除多余的UI组件
            for i in range(self.notifications_layout.count() - 101):
                item = self.notifications_layout.takeAt(100)
                if item.widget():
                    item.widget().deleteLater()
    
    def create_notification_item_widget(self, notification: NotificationItem) -> QWidget:
        """创建通知项组件"""
        item = QFrame()
        item.setFrameStyle(QFrame.Shape.Box)
        item.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
            }
        """)
        
        layout = QVBoxLayout(item)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        
        # 标题行
        title_layout = QHBoxLayout()
        
        # 图标和标题
        icon_label = QLabel(self.get_notification_icon(notification.type))
        title_label = QLabel(notification.title)
        title_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 时间戳
        time_label = QLabel(notification.timestamp.strftime("%H:%M"))
        time_label.setStyleSheet("color: #6c757d; font-size: 10px;")
        title_layout.addWidget(time_label)
        
        layout.addLayout(title_layout)
        
        # 消息内容
        message_label = QLabel(notification.message)
        message_label.setFont(QFont("Microsoft YaHei", 8))
        message_label.setStyleSheet("color: #495057;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        return item
    
    def get_notification_icon(self, notification_type: NotificationType) -> str:
        """获取通知图标"""
        icons = {
            NotificationType.INFO: "ℹ️",
            NotificationType.SUCCESS: "✅",
            NotificationType.WARNING: "⚠️",
            NotificationType.ERROR: "❌",
            NotificationType.PROGRESS: "🔄"
        }
        return icons.get(notification_type, "ℹ️")
    
    def clear_all_notifications(self):
        """清空所有通知"""
        self.notifications.clear()
        
        # 清空UI
        for i in reversed(range(self.notifications_layout.count())):
            item = self.notifications_layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        self.notifications_layout.addStretch()
    
    def get_unread_count(self) -> int:
        """获取未读通知数量"""
        return len([n for n in self.notifications if not n.is_read])
    
    def mark_all_as_read(self):
        """标记所有通知为已读"""
        for notification in self.notifications:
            notification.is_read = True


class SystemTrayManager:
    """系统托盘管理器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.tray_icon = None
        self.setup_tray_icon()
        logger.info("系统托盘管理器初始化完成")

    def setup_tray_icon(self):
        """设置系统托盘图标"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("系统托盘不可用")
            return

        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self.main_window)

        # 设置图标
        icon = self.create_tray_icon()
        self.tray_icon.setIcon(icon)

        # 设置工具提示
        self.tray_icon.setToolTip("AI Animation Studio")

        # 创建上下文菜单
        tray_menu = QMenu()

        # 显示/隐藏主窗口
        show_action = tray_menu.addAction("显示主窗口")
        show_action.triggered.connect(self.show_main_window)

        hide_action = tray_menu.addAction("隐藏到托盘")
        hide_action.triggered.connect(self.hide_main_window)

        tray_menu.addSeparator()

        # 通知中心
        notifications_action = tray_menu.addAction("🔔 通知中心")
        notifications_action.triggered.connect(self.show_notification_center)

        tray_menu.addSeparator()

        # 退出
        quit_action = tray_menu.addAction("退出")
        quit_action.triggered.connect(self.main_window.close)

        self.tray_icon.setContextMenu(tray_menu)

        # 连接信号
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # 显示托盘图标
        self.tray_icon.show()

    def create_tray_icon(self) -> QIcon:
        """创建托盘图标"""
        # 创建一个简单的图标
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制圆形背景
        painter.setBrush(QColor("#2C5AA0"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 28, 28)

        # 绘制文字
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "AI")

        painter.end()

        return QIcon(pixmap)

    def on_tray_icon_activated(self, reason):
        """托盘图标激活处理"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window()
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            self.show_notification_center()

    def show_main_window(self):
        """显示主窗口"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def hide_main_window(self):
        """隐藏主窗口到托盘"""
        self.main_window.hide()
        self.show_tray_message("AI Animation Studio", "应用程序已最小化到系统托盘")

    def show_notification_center(self):
        """显示通知中心"""
        if hasattr(self.main_window, 'status_notification_manager'):
            self.main_window.status_notification_manager.show_notification_center()

    def show_tray_message(self, title: str, message: str,
                         icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
                         duration: int = 3000):
        """显示托盘消息"""
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, icon, duration)

    def update_tray_icon_badge(self, count: int):
        """更新托盘图标徽章"""
        icon = self.create_tray_icon_with_badge(count)
        if self.tray_icon:
            self.tray_icon.setIcon(icon)

    def create_tray_icon_with_badge(self, count: int) -> QIcon:
        """创建带徽章的托盘图标"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制主图标
        painter.setBrush(QColor("#2C5AA0"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 28, 28)

        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(QRect(2, 2, 28, 28), Qt.AlignmentFlag.AlignCenter, "AI")

        # 绘制徽章
        if count > 0:
            badge_size = 12
            badge_x = 32 - badge_size
            badge_y = 0

            painter.setBrush(QColor("#EF4444"))
            painter.drawEllipse(badge_x, badge_y, badge_size, badge_size)

            painter.setPen(QColor("white"))
            painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            badge_text = str(count) if count < 100 else "99+"
            painter.drawText(QRect(badge_x, badge_y, badge_size, badge_size),
                           Qt.AlignmentFlag.AlignCenter, badge_text)

        painter.end()

        return QIcon(pixmap)


class StatusNotificationManager:
    """状态栏和通知系统管理器"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.status_bar_widget = None
        self.notification_center = None
        self.system_tray_manager = None
        self.active_notifications: Dict[str, NotificationWidget] = {}
        self.notification_queue: List[NotificationItem] = []
        self.max_concurrent_notifications = 3

        self.setup_status_bar()
        self.setup_notification_center()
        self.setup_system_tray()

        logger.info("状态栏和通知系统管理器初始化完成")

    def setup_status_bar(self):
        """设置状态栏"""
        # 替换原有状态栏
        if self.main_window.statusBar():
            self.main_window.statusBar().hide()

        # 创建新的状态栏组件
        self.status_bar_widget = StatusBarWidget()

        # 添加到主窗口底部
        if hasattr(self.main_window, 'centralWidget'):
            central_widget = self.main_window.centralWidget()
            if central_widget and central_widget.layout():
                central_widget.layout().addWidget(self.status_bar_widget)

    def setup_notification_center(self):
        """设置通知中心"""
        self.notification_center = NotificationCenter()

    def setup_system_tray(self):
        """设置系统托盘"""
        self.system_tray_manager = SystemTrayManager(self.main_window)

    def show_notification(self, title: str, message: str,
                         notification_type: NotificationType = NotificationType.INFO,
                         duration: int = 5000, action_text: str = None,
                         action_callback=None) -> str:
        """显示通知"""
        notification = NotificationItem(
            title=title,
            message=message,
            notification_type=notification_type,
            duration=duration,
            action_text=action_text,
            action_callback=action_callback
        )

        # 添加到通知中心
        self.notification_center.add_notification_item(notification)

        # 更新托盘图标徽章
        unread_count = self.notification_center.get_unread_count()
        self.system_tray_manager.update_tray_icon_badge(unread_count)

        # 显示弹窗通知
        if len(self.active_notifications) < self.max_concurrent_notifications:
            self._show_popup_notification(notification)
        else:
            self.notification_queue.append(notification)

        return notification.id

    def _show_popup_notification(self, notification: NotificationItem):
        """显示弹窗通知"""
        popup = NotificationWidget(notification)
        popup.dismissed.connect(self._on_notification_dismissed)
        popup.action_clicked.connect(self._on_notification_action_clicked)

        self.active_notifications[notification.id] = popup
        popup.show_notification()

    def _on_notification_dismissed(self, notification_id: str):
        """通知被关闭处理"""
        if notification_id in self.active_notifications:
            del self.active_notifications[notification_id]

        # 显示队列中的下一个通知
        if self.notification_queue:
            next_notification = self.notification_queue.pop(0)
            self._show_popup_notification(next_notification)

    def _on_notification_action_clicked(self, notification_id: str):
        """通知动作按钮点击处理"""
        logger.info(f"通知动作被点击: {notification_id}")

    def show_notification_center(self):
        """显示通知中心"""
        self.notification_center.show()
        self.notification_center.raise_()
        self.notification_center.activateWindow()

        # 标记所有通知为已读
        self.notification_center.mark_all_as_read()

        # 更新托盘图标
        self.system_tray_manager.update_tray_icon_badge(0)

    def update_status(self, status: StatusType, message: str = ""):
        """更新状态栏状态"""
        if self.status_bar_widget:
            self.status_bar_widget.update_status(status, message)

    def update_selection(self, element_name: str = None):
        """更新选中元素信息"""
        if self.status_bar_widget:
            self.status_bar_widget.update_selection(element_name)

    def update_position(self, x: int, y: int):
        """更新位置信息"""
        if self.status_bar_widget:
            self.status_bar_widget.update_position(x, y)

    def update_save_status(self, is_saved: bool, auto_save: bool = False):
        """更新保存状态"""
        if self.status_bar_widget:
            self.status_bar_widget.update_save_status(is_saved, auto_save)

    def show_progress(self, value: int, text: str = ""):
        """显示进度条"""
        if self.status_bar_widget:
            self.status_bar_widget.show_progress(value, text)

    def hide_progress(self):
        """隐藏进度条"""
        if self.status_bar_widget:
            self.status_bar_widget.hide_progress()

    def update_performance(self, gpu_usage: int, memory_usage: int = None):
        """更新性能信息"""
        if self.status_bar_widget:
            self.status_bar_widget.update_performance(gpu_usage, memory_usage)

    def update_collaboration(self, online_users: int, total_users: int = None):
        """更新协作信息"""
        if self.status_bar_widget:
            self.status_bar_widget.update_collaboration(online_users, total_users)

    def show_success(self, title: str, message: str, duration: int = 3000):
        """显示成功通知"""
        return self.show_notification(title, message, NotificationType.SUCCESS, duration)

    def show_error(self, title: str, message: str, duration: int = 5000):
        """显示错误通知"""
        return self.show_notification(title, message, NotificationType.ERROR, duration)

    def show_warning(self, title: str, message: str, duration: int = 4000):
        """显示警告通知"""
        return self.show_notification(title, message, NotificationType.WARNING, duration)

    def show_info(self, title: str, message: str, duration: int = 3000):
        """显示信息通知"""
        return self.show_notification(title, message, NotificationType.INFO, duration)

    def show_progress_notification(self, title: str, message: str):
        """显示进度通知"""
        return self.show_notification(title, message, NotificationType.PROGRESS, 0)  # 不自动关闭

    def dismiss_notification(self, notification_id: str):
        """关闭指定通知"""
        if notification_id in self.active_notifications:
            self.active_notifications[notification_id].dismiss()

    def get_status_summary(self) -> dict:
        """获取状态摘要"""
        return {
            'current_status': self.status_bar_widget.current_status.value if self.status_bar_widget else None,
            'active_notifications': len(self.active_notifications),
            'queued_notifications': len(self.notification_queue),
            'unread_notifications': self.notification_center.get_unread_count() if self.notification_center else 0,
            'total_notifications': len(self.notification_center.notifications) if self.notification_center else 0
        }
