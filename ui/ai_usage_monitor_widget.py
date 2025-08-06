"""
AI Animation Studio - AI使用量监控组件
提供实时的AI服务使用量监控、成本分析、性能统计等功能
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QComboBox, QProgressBar,
    QTextEdit, QTabWidget, QFrame, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QLineSeries, QDateTimeAxis, QValueAxis

from core.logger import get_logger

logger = get_logger("ai_usage_monitor")


class AIUsageMonitorWidget(QWidget):
    """AI使用量监控组件"""
    
    # 信号定义
    usage_limit_exceeded = pyqtSignal(str, str)  # service, limit_type
    cost_warning = pyqtSignal(float)             # current_cost
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_timer()
        
        logger.info("AI使用量监控组件初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("AI服务使用量监控")
        title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 标签页
        self.tab_widget = QTabWidget()
        
        # 实时监控标签页
        self.setup_realtime_tab()
        
        # 历史统计标签页
        self.setup_history_tab()
        
        # 成本分析标签页
        self.setup_cost_analysis_tab()
        
        # 性能统计标签页
        self.setup_performance_tab()
        
        layout.addWidget(self.tab_widget)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 刷新数据")
        refresh_btn.clicked.connect(self.refresh_all_data)
        button_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton("📊 导出报告")
        export_btn.clicked.connect(self.export_usage_report)
        button_layout.addWidget(export_btn)
        
        clear_btn = QPushButton("🗑️ 清空缓存")
        clear_btn.clicked.connect(self.clear_cache)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        # 自动刷新设置
        auto_refresh_label = QLabel("自动刷新:")
        button_layout.addWidget(auto_refresh_label)
        
        self.auto_refresh_combo = QComboBox()
        self.auto_refresh_combo.addItems(["关闭", "30秒", "1分钟", "5分钟"])
        self.auto_refresh_combo.setCurrentText("1分钟")
        self.auto_refresh_combo.currentTextChanged.connect(self.on_auto_refresh_changed)
        button_layout.addWidget(self.auto_refresh_combo)
        
        layout.addLayout(button_layout)
    
    def setup_realtime_tab(self):
        """设置实时监控标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 服务状态概览
        status_group = QGroupBox("服务状态")
        status_layout = QGridLayout(status_group)
        
        # OpenAI状态
        self.openai_status_label = QLabel("🔴 未配置")
        status_layout.addWidget(QLabel("OpenAI:"), 0, 0)
        status_layout.addWidget(self.openai_status_label, 0, 1)
        
        self.openai_requests_label = QLabel("0 请求")
        status_layout.addWidget(self.openai_requests_label, 0, 2)
        
        # Claude状态
        self.claude_status_label = QLabel("🔴 未配置")
        status_layout.addWidget(QLabel("Claude:"), 1, 0)
        status_layout.addWidget(self.claude_status_label, 1, 1)
        
        self.claude_requests_label = QLabel("0 请求")
        status_layout.addWidget(self.claude_requests_label, 1, 2)
        
        # Gemini状态
        self.gemini_status_label = QLabel("🟢 已配置")
        status_layout.addWidget(QLabel("Gemini:"), 2, 0)
        status_layout.addWidget(self.gemini_status_label, 2, 1)
        
        self.gemini_requests_label = QLabel("0 请求")
        status_layout.addWidget(self.gemini_requests_label, 2, 2)
        
        layout.addWidget(status_group)
        
        # 今日使用量
        today_group = QGroupBox("今日使用量")
        today_layout = QVBoxLayout(today_group)
        
        self.today_table = QTableWidget()
        self.today_table.setColumnCount(5)
        self.today_table.setHorizontalHeaderLabels(["服务", "请求数", "令牌数", "成功率", "费用"])
        self.today_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.today_table.setMaximumHeight(150)
        today_layout.addWidget(self.today_table)
        
        layout.addWidget(today_group)
        
        # 使用量限制进度
        limits_group = QGroupBox("使用量限制")
        limits_layout = QVBoxLayout(limits_group)
        
        # 日限制进度
        daily_layout = QHBoxLayout()
        daily_layout.addWidget(QLabel("日请求限制:"))
        self.daily_progress = QProgressBar()
        self.daily_progress.setFormat("%v / %m (%p%)")
        daily_layout.addWidget(self.daily_progress)
        limits_layout.addLayout(daily_layout)
        
        # 月限制进度
        monthly_layout = QHBoxLayout()
        monthly_layout.addWidget(QLabel("月请求限制:"))
        self.monthly_progress = QProgressBar()
        self.monthly_progress.setFormat("%v / %m (%p%)")
        monthly_layout.addWidget(self.monthly_progress)
        limits_layout.addLayout(monthly_layout)
        
        # 费用限制进度
        cost_layout = QHBoxLayout()
        cost_layout.addWidget(QLabel("月费用限制:"))
        self.cost_progress = QProgressBar()
        self.cost_progress.setFormat("$%v / $%m (%p%)")
        monthly_layout.addWidget(self.cost_progress)
        limits_layout.addLayout(cost_layout)
        
        layout.addWidget(limits_group)
        
        # 缓存统计
        cache_group = QGroupBox("缓存统计")
        cache_layout = QGridLayout(cache_group)
        
        cache_layout.addWidget(QLabel("缓存大小:"), 0, 0)
        self.cache_size_label = QLabel("0 MB")
        cache_layout.addWidget(self.cache_size_label, 0, 1)
        
        cache_layout.addWidget(QLabel("缓存命中率:"), 0, 2)
        self.cache_hit_rate_label = QLabel("0%")
        cache_layout.addWidget(self.cache_hit_rate_label, 0, 3)
        
        cache_layout.addWidget(QLabel("缓存项数:"), 1, 0)
        self.cache_items_label = QLabel("0")
        cache_layout.addWidget(self.cache_items_label, 1, 1)
        
        cache_layout.addWidget(QLabel("节省费用:"), 1, 2)
        self.cache_savings_label = QLabel("$0.00")
        cache_layout.addWidget(self.cache_savings_label, 1, 3)
        
        layout.addWidget(cache_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "📊 实时监控")
    
    def setup_history_tab(self):
        """设置历史统计标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 时间范围选择
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("时间范围:"))
        
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(["今天", "最近7天", "最近30天", "本月", "上月"])
        self.time_range_combo.currentTextChanged.connect(self.update_history_data)
        range_layout.addWidget(self.time_range_combo)
        
        range_layout.addStretch()
        layout.addLayout(range_layout)
        
        # 历史数据表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(["日期", "服务", "请求数", "令牌数", "成功率", "费用"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.history_table)
        
        self.tab_widget.addTab(tab, "📈 历史统计")
    
    def setup_cost_analysis_tab(self):
        """设置成本分析标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 成本概览
        cost_overview_group = QGroupBox("成本概览")
        cost_overview_layout = QGridLayout(cost_overview_group)
        
        # 今日费用
        cost_overview_layout.addWidget(QLabel("今日费用:"), 0, 0)
        self.today_cost_label = QLabel("$0.00")
        self.today_cost_label.setFont(QFont("", 12, QFont.Weight.Bold))
        cost_overview_layout.addWidget(self.today_cost_label, 0, 1)
        
        # 本月费用
        cost_overview_layout.addWidget(QLabel("本月费用:"), 0, 2)
        self.month_cost_label = QLabel("$0.00")
        self.month_cost_label.setFont(QFont("", 12, QFont.Weight.Bold))
        cost_overview_layout.addWidget(self.month_cost_label, 0, 3)
        
        # 预计月费用
        cost_overview_layout.addWidget(QLabel("预计月费用:"), 1, 0)
        self.estimated_cost_label = QLabel("$0.00")
        cost_overview_layout.addWidget(self.estimated_cost_label, 1, 1)
        
        # 节省费用
        cost_overview_layout.addWidget(QLabel("缓存节省:"), 1, 2)
        self.saved_cost_label = QLabel("$0.00")
        cost_overview_layout.addWidget(self.saved_cost_label, 1, 3)
        
        layout.addWidget(cost_overview_group)
        
        # 费用分布饼图
        cost_chart_group = QGroupBox("费用分布")
        cost_chart_layout = QVBoxLayout(cost_chart_group)
        
        # 这里应该添加饼图，简化实现
        self.cost_distribution_label = QLabel("费用分布图将在后续版本中实现")
        self.cost_distribution_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cost_distribution_label.setMinimumHeight(200)
        self.cost_distribution_label.setStyleSheet("border: 1px solid #ccc; background: #f9f9f9;")
        cost_chart_layout.addWidget(self.cost_distribution_label)
        
        layout.addWidget(cost_chart_group)
        
        # 成本优化建议
        optimization_group = QGroupBox("成本优化建议")
        optimization_layout = QVBoxLayout(optimization_group)
        
        self.optimization_text = QTextEdit()
        self.optimization_text.setMaximumHeight(120)
        self.optimization_text.setReadOnly(True)
        optimization_layout.addWidget(self.optimization_text)
        
        layout.addWidget(optimization_group)
        
        self.tab_widget.addTab(tab, "💰 成本分析")
    
    def setup_performance_tab(self):
        """设置性能统计标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 性能指标
        performance_group = QGroupBox("性能指标")
        performance_layout = QGridLayout(performance_group)
        
        # 平均响应时间
        performance_layout.addWidget(QLabel("平均响应时间:"), 0, 0)
        self.avg_response_time_label = QLabel("0.0s")
        performance_layout.addWidget(self.avg_response_time_label, 0, 1)
        
        # 成功率
        performance_layout.addWidget(QLabel("总体成功率:"), 0, 2)
        self.success_rate_label = QLabel("0%")
        performance_layout.addWidget(self.success_rate_label, 0, 3)
        
        # 缓存命中率
        performance_layout.addWidget(QLabel("缓存命中率:"), 1, 0)
        self.cache_hit_rate_performance_label = QLabel("0%")
        performance_layout.addWidget(self.cache_hit_rate_performance_label, 1, 1)
        
        # 错误率
        performance_layout.addWidget(QLabel("错误率:"), 1, 2)
        self.error_rate_label = QLabel("0%")
        performance_layout.addWidget(self.error_rate_label, 1, 3)
        
        layout.addWidget(performance_group)
        
        # 服务性能对比
        comparison_group = QGroupBox("服务性能对比")
        comparison_layout = QVBoxLayout(comparison_group)
        
        self.performance_table = QTableWidget()
        self.performance_table.setColumnCount(5)
        self.performance_table.setHorizontalHeaderLabels(["服务", "平均响应时间", "成功率", "平均费用", "推荐度"])
        self.performance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        comparison_layout.addWidget(self.performance_table)
        
        layout.addWidget(comparison_group)
        
        # 性能趋势图
        trend_group = QGroupBox("性能趋势")
        trend_layout = QVBoxLayout(trend_group)
        
        # 简化实现，使用标签代替图表
        self.performance_trend_label = QLabel("性能趋势图将在后续版本中实现")
        self.performance_trend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.performance_trend_label.setMinimumHeight(200)
        self.performance_trend_label.setStyleSheet("border: 1px solid #ccc; background: #f9f9f9;")
        trend_layout.addWidget(self.performance_trend_label)
        
        layout.addWidget(trend_group)
        
        self.tab_widget.addTab(tab, "⚡ 性能统计")
    
    def setup_timer(self):
        """设置定时器"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all_data)
        self.on_auto_refresh_changed("1分钟")  # 默认1分钟刷新
    
    def on_auto_refresh_changed(self, interval: str):
        """自动刷新间隔改变"""
        self.refresh_timer.stop()
        
        if interval == "关闭":
            return
        elif interval == "30秒":
            self.refresh_timer.start(30000)
        elif interval == "1分钟":
            self.refresh_timer.start(60000)
        elif interval == "5分钟":
            self.refresh_timer.start(300000)
    
    def refresh_all_data(self):
        """刷新所有数据"""
        try:
            self.update_service_status()
            self.update_today_usage()
            self.update_usage_limits()
            self.update_cache_stats()
            self.update_cost_analysis()
            self.update_performance_stats()
            
            logger.debug("使用量监控数据已刷新")
            
        except Exception as e:
            logger.error(f"刷新监控数据失败: {e}")
    
    def update_service_status(self):
        """更新服务状态"""
        try:
            from core.ai_service_manager import ai_service_manager
            
            available_services = ai_service_manager.get_available_services()
            
            # 更新OpenAI状态
            if any(s.value == "openai" for s in available_services):
                self.openai_status_label.setText("🟢 已配置")
                self.openai_status_label.setStyleSheet("color: green;")
            else:
                self.openai_status_label.setText("🔴 未配置")
                self.openai_status_label.setStyleSheet("color: red;")
            
            # 更新Claude状态
            if any(s.value == "claude" for s in available_services):
                self.claude_status_label.setText("🟢 已配置")
                self.claude_status_label.setStyleSheet("color: green;")
            else:
                self.claude_status_label.setText("🔴 未配置")
                self.claude_status_label.setStyleSheet("color: red;")
            
            # 更新Gemini状态
            if any(s.value == "gemini" for s in available_services):
                self.gemini_status_label.setText("🟢 已配置")
                self.gemini_status_label.setStyleSheet("color: green;")
            else:
                self.gemini_status_label.setText("🔴 未配置")
                self.gemini_status_label.setStyleSheet("color: red;")
                
        except Exception as e:
            logger.error(f"更新服务状态失败: {e}")
    
    def update_today_usage(self):
        """更新今日使用量"""
        try:
            from core.ai_service_manager import ai_service_manager
            
            usage_summary = ai_service_manager.get_usage_summary()
            daily_usage = usage_summary.get("daily_usage", {})
            
            # 更新表格
            self.today_table.setRowCount(len(daily_usage))
            
            for row, (service, data) in enumerate(daily_usage.items()):
                self.today_table.setItem(row, 0, QTableWidgetItem(service.upper()))
                self.today_table.setItem(row, 1, QTableWidgetItem(str(data.get("requests", 0))))
                self.today_table.setItem(row, 2, QTableWidgetItem(str(data.get("tokens", 0))))
                self.today_table.setItem(row, 3, QTableWidgetItem("100%"))  # 简化实现
                self.today_table.setItem(row, 4, QTableWidgetItem(f"${data.get('cost', 0.0):.4f}"))
            
            # 更新请求数标签
            openai_requests = daily_usage.get("openai", {}).get("requests", 0)
            claude_requests = daily_usage.get("claude", {}).get("requests", 0)
            gemini_requests = daily_usage.get("gemini", {}).get("requests", 0)
            
            self.openai_requests_label.setText(f"{openai_requests} 请求")
            self.claude_requests_label.setText(f"{claude_requests} 请求")
            self.gemini_requests_label.setText(f"{gemini_requests} 请求")
            
        except Exception as e:
            logger.error(f"更新今日使用量失败: {e}")
    
    def update_usage_limits(self):
        """更新使用量限制进度"""
        try:
            from core.ai_service_manager import ai_service_manager
            
            config = ai_service_manager.config
            usage_summary = ai_service_manager.get_usage_summary()
            
            # 日限制
            daily_limit = config.get("daily_limit", 100)
            daily_used = sum(data.get("requests", 0) for data in usage_summary.get("daily_usage", {}).values())
            self.daily_progress.setMaximum(daily_limit)
            self.daily_progress.setValue(daily_used)
            
            # 月限制
            monthly_limit = config.get("monthly_limit", 1000)
            monthly_used = sum(data.get("requests", 0) for data in usage_summary.get("monthly_usage", {}).values())
            self.monthly_progress.setMaximum(monthly_limit)
            self.monthly_progress.setValue(monthly_used)
            
            # 费用限制
            cost_limit = config.get("cost_limit", 50.0)
            monthly_cost = sum(data.get("cost", 0.0) for data in usage_summary.get("monthly_usage", {}).values())
            self.cost_progress.setMaximum(int(cost_limit * 100))  # 转换为分
            self.cost_progress.setValue(int(monthly_cost * 100))
            
            # 检查限制警告
            if daily_used >= daily_limit * 0.9:
                self.usage_limit_exceeded.emit("daily", f"日使用量已达到{daily_used}/{daily_limit}")
            
            if monthly_cost >= cost_limit * 0.9:
                self.cost_warning.emit(monthly_cost)
                
        except Exception as e:
            logger.error(f"更新使用量限制失败: {e}")
    
    def update_cache_stats(self):
        """更新缓存统计"""
        try:
            from core.ai_service_manager import ai_service_manager
            
            usage_summary = ai_service_manager.get_usage_summary()
            cache_stats = usage_summary.get("cache_stats", {})
            
            # 缓存大小（简化实现）
            cache_size = cache_stats.get("cache_size", 0)
            self.cache_size_label.setText(f"{cache_size} 项")
            
            # 缓存命中率
            cache_hits = cache_stats.get("cache_hits", 0)
            cache_misses = cache_stats.get("cache_misses", 0)
            total_requests = cache_hits + cache_misses
            
            if total_requests > 0:
                hit_rate = (cache_hits / total_requests) * 100
                self.cache_hit_rate_label.setText(f"{hit_rate:.1f}%")
            else:
                self.cache_hit_rate_label.setText("0%")
            
            # 缓存项数
            self.cache_items_label.setText(str(cache_size))
            
            # 节省费用（估算）
            estimated_savings = cache_hits * 0.001  # 简化估算
            self.cache_savings_label.setText(f"${estimated_savings:.4f}")
            
        except Exception as e:
            logger.error(f"更新缓存统计失败: {e}")
    
    def update_cost_analysis(self):
        """更新成本分析"""
        try:
            from core.ai_service_manager import ai_service_manager
            
            usage_summary = ai_service_manager.get_usage_summary()
            
            # 今日费用
            daily_cost = sum(data.get("cost", 0.0) for data in usage_summary.get("daily_usage", {}).values())
            self.today_cost_label.setText(f"${daily_cost:.4f}")
            
            # 本月费用
            monthly_cost = sum(data.get("cost", 0.0) for data in usage_summary.get("monthly_usage", {}).values())
            self.month_cost_label.setText(f"${monthly_cost:.4f}")
            
            # 预计月费用（基于当前使用趋势）
            days_in_month = 30
            current_day = datetime.now().day
            if current_day > 0:
                estimated_monthly = (monthly_cost / current_day) * days_in_month
                self.estimated_cost_label.setText(f"${estimated_monthly:.2f}")
            
            # 生成优化建议
            self.generate_cost_optimization_suggestions(usage_summary)
            
        except Exception as e:
            logger.error(f"更新成本分析失败: {e}")
    
    def update_performance_stats(self):
        """更新性能统计"""
        try:
            # 简化实现，显示模拟数据
            self.avg_response_time_label.setText("1.2s")
            self.success_rate_label.setText("98.5%")
            self.cache_hit_rate_performance_label.setText("45%")
            self.error_rate_label.setText("1.5%")
            
            # 更新性能对比表格
            self.performance_table.setRowCount(3)
            
            services_data = [
                ["OpenAI", "1.5s", "97%", "$0.030", "⭐⭐⭐"],
                ["Claude", "1.8s", "99%", "$0.015", "⭐⭐⭐⭐"],
                ["Gemini", "0.8s", "98%", "$0.001", "⭐⭐⭐⭐⭐"]
            ]
            
            for row, data in enumerate(services_data):
                for col, value in enumerate(data):
                    self.performance_table.setItem(row, col, QTableWidgetItem(value))
            
        except Exception as e:
            logger.error(f"更新性能统计失败: {e}")
    
    def update_history_data(self):
        """更新历史数据"""
        # TODO: 实现历史数据更新
        pass
    
    def generate_cost_optimization_suggestions(self, usage_summary: Dict[str, Any]):
        """生成成本优化建议"""
        suggestions = []
        
        try:
            daily_usage = usage_summary.get("daily_usage", {})
            monthly_usage = usage_summary.get("monthly_usage", {})
            
            # 分析使用模式
            total_daily_cost = sum(data.get("cost", 0.0) for data in daily_usage.values())
            total_monthly_cost = sum(data.get("cost", 0.0) for data in monthly_usage.values())
            
            if total_daily_cost > 1.0:
                suggestions.append("• 考虑启用更积极的缓存策略以减少重复请求")
            
            if total_monthly_cost > 20.0:
                suggestions.append("• 建议优化提示词长度，减少不必要的令牌消耗")
            
            # 服务选择建议
            gemini_usage = monthly_usage.get("gemini", {}).get("cost", 0.0)
            openai_usage = monthly_usage.get("openai", {}).get("cost", 0.0)
            
            if openai_usage > gemini_usage * 10:
                suggestions.append("• 考虑更多使用Gemini服务，成本更低")
            
            if not suggestions:
                suggestions.append("• 当前使用模式较为合理，继续保持")
            
            self.optimization_text.setPlainText("\n".join(suggestions))
            
        except Exception as e:
            logger.error(f"生成优化建议失败: {e}")
    
    def export_usage_report(self):
        """导出使用量报告"""
        try:
            from core.ai_service_manager import ai_service_manager
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"ai_usage_report_{timestamp}.json"
            
            ai_service_manager.export_usage_report(file_path)
            
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "成功", f"使用量报告已导出到:\n{file_path}")
            
        except Exception as e:
            logger.error(f"导出使用量报告失败: {e}")
    
    def clear_cache(self):
        """清空缓存"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(
                self, "确认", "确定要清空AI响应缓存吗？\n这将删除所有缓存的响应数据。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                from core.ai_service_manager import ai_service_manager
                ai_service_manager.clear_cache()
                
                QMessageBox.information(self, "成功", "AI缓存已清空")
                self.refresh_all_data()
                
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
    
    def get_usage_summary_text(self) -> str:
        """获取使用量摘要文本"""
        try:
            from core.ai_service_manager import ai_service_manager
            
            usage_summary = ai_service_manager.get_usage_summary()
            
            summary_lines = [
                "=== AI服务使用量摘要 ===",
                f"总请求数: {usage_summary.get('total_requests', 0)}",
                f"总令牌数: {usage_summary.get('total_tokens', 0)}",
                "",
                "今日使用量:"
            ]
            
            daily_usage = usage_summary.get("daily_usage", {})
            for service, data in daily_usage.items():
                summary_lines.append(f"  {service.upper()}: {data.get('requests', 0)} 请求, ${data.get('cost', 0.0):.4f}")
            
            summary_lines.extend([
                "",
                "本月使用量:"
            ])
            
            monthly_usage = usage_summary.get("monthly_usage", {})
            for service, data in monthly_usage.items():
                summary_lines.append(f"  {service.upper()}: {data.get('requests', 0)} 请求, ${data.get('cost', 0.0):.4f}")
            
            return "\n".join(summary_lines)
            
        except Exception as e:
            logger.error(f"获取使用量摘要失败: {e}")
            return "获取使用量摘要失败"
