"""
AI Animation Studio - 撤销重做历史对话框
提供撤销重做历史的可视化管理界面
"""

from typing import List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QGroupBox, QTextEdit, QSplitter,
    QProgressBar, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon

from core.logger import get_logger
from core.command_manager import CommandManager

logger = get_logger("undo_history_dialog")


class UndoHistoryDialog(QDialog):
    """撤销重做历史对话框"""
    
    # 信号定义
    command_selected = pyqtSignal(str)  # 选择命令
    history_cleared = pyqtSignal()      # 清空历史
    
    def __init__(self, parent=None, command_manager: CommandManager = None):
        super().__init__(parent)
        self.command_manager = command_manager
        
        self.setWindowTitle("撤销重做历史")
        self.setMinimumSize(600, 500)
        self.resize(800, 600)
        
        self.setup_ui()
        self.load_history()
        
        # 定时刷新历史
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_history)
        self.refresh_timer.start(1000)  # 每秒刷新一次
        
        logger.info("撤销重做历史对话框初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("撤销重做历史")
        title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 主要内容区域
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：历史列表
        left_widget = self.setup_history_list()
        splitter.addWidget(left_widget)
        
        # 右侧：详细信息和控制
        right_widget = self.setup_details_panel()
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setSizes([400, 300])
        layout.addWidget(splitter)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        # 统计信息
        self.stats_label = QLabel()
        button_layout.addWidget(self.stats_label)
        
        button_layout.addStretch()
        
        # 刷新按钮
        refresh_button = QPushButton("刷新")
        refresh_button.clicked.connect(self.refresh_history)
        button_layout.addWidget(refresh_button)
        
        # 清空历史按钮
        clear_button = QPushButton("清空历史")
        clear_button.clicked.connect(self.clear_history)
        button_layout.addWidget(clear_button)
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def setup_history_list(self) -> QGroupBox:
        """设置历史列表"""
        group = QGroupBox("命令历史")
        layout = QVBoxLayout(group)
        
        # 历史列表
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_item_clicked)
        self.history_list.itemDoubleClicked.connect(self.on_history_item_double_clicked)
        layout.addWidget(self.history_list)
        
        # 列表控制
        list_controls = QHBoxLayout()
        
        # 自动刷新选项
        self.auto_refresh_checkbox = QCheckBox("自动刷新")
        self.auto_refresh_checkbox.setChecked(True)
        self.auto_refresh_checkbox.toggled.connect(self.toggle_auto_refresh)
        list_controls.addWidget(self.auto_refresh_checkbox)
        
        list_controls.addStretch()
        
        # 最大显示数量
        list_controls.addWidget(QLabel("显示数量:"))
        self.max_display_spinbox = QSpinBox()
        self.max_display_spinbox.setRange(10, 1000)
        self.max_display_spinbox.setValue(100)
        self.max_display_spinbox.valueChanged.connect(self.refresh_history)
        list_controls.addWidget(self.max_display_spinbox)
        
        layout.addLayout(list_controls)
        
        return group
    
    def setup_details_panel(self) -> QGroupBox:
        """设置详细信息面板"""
        group = QGroupBox("命令详情")
        layout = QVBoxLayout(group)
        
        # 命令信息
        info_group = QGroupBox("基本信息")
        info_layout = QVBoxLayout(info_group)
        
        self.command_id_label = QLabel("ID: -")
        info_layout.addWidget(self.command_id_label)
        
        self.command_desc_label = QLabel("描述: -")
        info_layout.addWidget(self.command_desc_label)
        
        self.command_time_label = QLabel("时间: -")
        info_layout.addWidget(self.command_time_label)
        
        self.command_status_label = QLabel("状态: -")
        info_layout.addWidget(self.command_status_label)
        
        layout.addWidget(info_group)
        
        # 命令详细信息
        details_group = QGroupBox("详细信息")
        details_layout = QVBoxLayout(details_group)
        
        self.command_details_text = QTextEdit()
        self.command_details_text.setReadOnly(True)
        self.command_details_text.setMaximumHeight(150)
        details_layout.addWidget(self.command_details_text)
        
        layout.addWidget(details_group)
        
        # 操作按钮
        action_group = QGroupBox("操作")
        action_layout = QVBoxLayout(action_group)
        
        self.undo_to_button = QPushButton("撤销到此处")
        self.undo_to_button.setEnabled(False)
        self.undo_to_button.clicked.connect(self.undo_to_selected)
        action_layout.addWidget(self.undo_to_button)
        
        self.redo_to_button = QPushButton("重做到此处")
        self.redo_to_button.setEnabled(False)
        self.redo_to_button.clicked.connect(self.redo_to_selected)
        action_layout.addWidget(self.redo_to_button)
        
        layout.addWidget(action_group)
        
        # 统计信息
        stats_group = QGroupBox("统计信息")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(100)
        stats_layout.addWidget(self.stats_text)
        
        layout.addWidget(stats_group)
        
        return group
    
    def load_history(self):
        """加载历史记录"""
        if not self.command_manager:
            return
        
        try:
            self.history_list.clear()
            
            # 获取历史记录
            history = self.command_manager.get_history()
            max_display = self.max_display_spinbox.value()
            
            # 限制显示数量
            if len(history) > max_display:
                history = history[-max_display:]
            
            # 添加到列表
            for i, cmd_str in enumerate(history):
                item = QListWidgetItem(cmd_str)
                
                # 设置图标和样式
                if "✅" in cmd_str:  # 已执行的命令
                    item.setForeground(Qt.GlobalColor.black)
                elif "⏳" in cmd_str:  # 可重做的命令
                    item.setForeground(Qt.GlobalColor.gray)
                
                self.history_list.addItem(item)
            
            # 更新统计信息
            self.update_statistics()
            
        except Exception as e:
            logger.error(f"加载历史记录失败: {e}")
    
    def refresh_history(self):
        """刷新历史记录"""
        if self.auto_refresh_checkbox.isChecked():
            self.load_history()
    
    def toggle_auto_refresh(self, enabled: bool):
        """切换自动刷新"""
        if enabled:
            self.refresh_timer.start(1000)
        else:
            self.refresh_timer.stop()
    
    def on_history_item_clicked(self, item: QListWidgetItem):
        """历史项点击事件"""
        try:
            # 解析命令信息
            cmd_text = item.text()
            
            # 更新详细信息显示
            self.update_command_details(cmd_text)
            
            # 更新操作按钮状态
            self.update_action_buttons(item)
            
        except Exception as e:
            logger.error(f"处理历史项点击失败: {e}")
    
    def on_history_item_double_clicked(self, item: QListWidgetItem):
        """历史项双击事件"""
        # 双击可以执行撤销或重做到该位置
        self.undo_to_selected()
    
    def update_command_details(self, cmd_text: str):
        """更新命令详细信息"""
        try:
            # 解析命令文本
            parts = cmd_text.split(" (")
            if len(parts) >= 2:
                description = parts[0].replace("✅ ", "").replace("⏳ ", "")
                time_part = parts[1].rstrip(")")
                
                self.command_desc_label.setText(f"描述: {description}")
                self.command_time_label.setText(f"时间: {time_part}")
                
                if "✅" in cmd_text:
                    self.command_status_label.setText("状态: 已执行")
                elif "⏳" in cmd_text:
                    self.command_status_label.setText("状态: 可重做")
                else:
                    self.command_status_label.setText("状态: 未知")
            
            # 显示详细信息
            details = f"命令文本: {cmd_text}\n"
            details += f"类型: {'已执行' if '✅' in cmd_text else '可重做'}\n"
            
            self.command_details_text.setPlainText(details)
            
        except Exception as e:
            logger.error(f"更新命令详细信息失败: {e}")
    
    def update_action_buttons(self, item: QListWidgetItem):
        """更新操作按钮状态"""
        try:
            cmd_text = item.text()
            
            # 根据命令状态启用/禁用按钮
            if "✅" in cmd_text:  # 已执行的命令
                self.undo_to_button.setEnabled(True)
                self.redo_to_button.setEnabled(False)
            elif "⏳" in cmd_text:  # 可重做的命令
                self.undo_to_button.setEnabled(False)
                self.redo_to_button.setEnabled(True)
            else:
                self.undo_to_button.setEnabled(False)
                self.redo_to_button.setEnabled(False)
                
        except Exception as e:
            logger.error(f"更新操作按钮状态失败: {e}")
    
    def update_statistics(self):
        """更新统计信息"""
        if not self.command_manager:
            return
        
        try:
            stats = self.command_manager.get_stats()
            
            # 更新底部统计标签
            stats_text = f"撤销: {stats['undo_count']} | 重做: {stats['redo_count']} | 总计: {stats['total_operations']}"
            self.stats_label.setText(stats_text)
            
            # 更新详细统计信息
            details = []
            details.append(f"可撤销操作数: {stats['undo_count']}")
            details.append(f"可重做操作数: {stats['redo_count']}")
            details.append(f"总操作数: {stats['total_operations']}")
            details.append(f"最大历史记录: {stats['max_history']}")
            details.append(f"自动合并: {'启用' if stats['auto_merge'] else '禁用'}")
            
            self.stats_text.setPlainText("\n".join(details))
            
        except Exception as e:
            logger.error(f"更新统计信息失败: {e}")
    
    def undo_to_selected(self):
        """撤销到选中的命令"""
        try:
            current_item = self.history_list.currentItem()
            if not current_item:
                return
            
            # 计算需要撤销的步数
            current_row = self.history_list.currentRow()
            total_rows = self.history_list.count()
            
            # 从当前位置撤销到选中位置
            undo_steps = total_rows - current_row - 1
            
            for _ in range(undo_steps):
                if not self.command_manager.undo():
                    break
            
            self.refresh_history()
            logger.info(f"撤销到选中位置，执行了 {undo_steps} 步撤销")
            
        except Exception as e:
            logger.error(f"撤销到选中位置失败: {e}")
    
    def redo_to_selected(self):
        """重做到选中的命令"""
        try:
            current_item = self.history_list.currentItem()
            if not current_item:
                return
            
            # 计算需要重做的步数
            current_row = self.history_list.currentRow()
            
            # 重做到选中位置
            redo_steps = current_row + 1
            
            for _ in range(redo_steps):
                if not self.command_manager.redo():
                    break
            
            self.refresh_history()
            logger.info(f"重做到选中位置，执行了 {redo_steps} 步重做")
            
        except Exception as e:
            logger.error(f"重做到选中位置失败: {e}")
    
    def clear_history(self):
        """清空历史记录"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(
                self, "确认清空",
                "确定要清空所有撤销重做历史吗？\n此操作不可撤销。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.command_manager.clear_history()
                self.refresh_history()
                self.history_cleared.emit()
                logger.info("撤销重做历史已清空")
                
        except Exception as e:
            logger.error(f"清空历史记录失败: {e}")
    
    def closeEvent(self, event):
        """关闭事件"""
        self.refresh_timer.stop()
        super().closeEvent(event)
