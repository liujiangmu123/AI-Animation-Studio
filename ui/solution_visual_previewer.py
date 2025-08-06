"""
AI Animation Studio - 方案可视化预览器
提供方案的实时可视化预览、对比功能、性能分析等
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QTextEdit, QComboBox, QListWidget, QListWidgetItem, QTabWidget,
    QFrame, QScrollArea, QSplitter, QProgressBar, QCheckBox, QSlider,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath
from PyQt6.QtWebEngineWidgets import QWebEngineView

from core.enhanced_solution_manager import EnhancedAnimationSolution, SolutionMetrics
from core.logger import get_logger

logger = get_logger("solution_visual_previewer")


class AnimationCodeAnalyzer:
    """动画代码分析器"""
    
    def __init__(self):
        # CSS动画属性模式
        self.css_patterns = {
            "animations": r"@keyframes\s+(\w+)",
            "transitions": r"transition\s*:\s*([^;]+)",
            "transforms": r"transform\s*:\s*([^;]+)",
            "durations": r"(\d+(?:\.\d+)?)\s*(s|ms)",
            "easings": r"(ease|ease-in|ease-out|ease-in-out|linear|cubic-bezier\([^)]+\))"
        }
        
        # JavaScript动画模式
        self.js_patterns = {
            "gsap_animations": r"gsap\.(to|from|fromTo|timeline)",
            "three_js": r"THREE\.(Scene|Camera|Renderer|Mesh)",
            "requestAnimationFrame": r"requestAnimationFrame",
            "setInterval": r"setInterval",
            "setTimeout": r"setTimeout"
        }
    
    def analyze_solution(self, solution: EnhancedAnimationSolution) -> Dict[str, Any]:
        """分析方案代码"""
        analysis = {
            "css_analysis": self.analyze_css(solution.css_code),
            "js_analysis": self.analyze_js(solution.js_code),
            "html_analysis": self.analyze_html(solution.html_code),
            "performance_hints": [],
            "compatibility_issues": [],
            "optimization_suggestions": []
        }
        
        # 生成性能提示
        analysis["performance_hints"] = self.generate_performance_hints(analysis)
        
        # 检查兼容性问题
        analysis["compatibility_issues"] = self.check_compatibility_issues(analysis)
        
        # 生成优化建议
        analysis["optimization_suggestions"] = self.generate_optimization_suggestions(analysis)
        
        return analysis
    
    def analyze_css(self, css_code: str) -> Dict[str, Any]:
        """分析CSS代码"""
        if not css_code:
            return {}
        
        analysis = {
            "keyframes": [],
            "transitions": [],
            "transforms": [],
            "durations": [],
            "easings": [],
            "properties_used": [],
            "performance_score": 0
        }
        
        try:
            # 提取关键帧动画
            keyframes = re.findall(self.css_patterns["animations"], css_code)
            analysis["keyframes"] = keyframes
            
            # 提取过渡效果
            transitions = re.findall(self.css_patterns["transitions"], css_code)
            analysis["transitions"] = transitions
            
            # 提取变换
            transforms = re.findall(self.css_patterns["transforms"], css_code)
            analysis["transforms"] = transforms
            
            # 提取时长
            durations = re.findall(self.css_patterns["durations"], css_code)
            analysis["durations"] = [(float(d[0]), d[1]) for d in durations]
            
            # 提取缓动函数
            easings = re.findall(self.css_patterns["easings"], css_code)
            analysis["easings"] = easings
            
            # 分析使用的CSS属性
            css_properties = [
                "opacity", "transform", "left", "top", "width", "height",
                "background", "color", "border", "box-shadow", "filter"
            ]
            
            for prop in css_properties:
                if prop in css_code.lower():
                    analysis["properties_used"].append(prop)
            
            # 计算性能分数
            analysis["performance_score"] = self.calculate_css_performance_score(analysis)
            
        except Exception as e:
            logger.error(f"CSS分析失败: {e}")
        
        return analysis
    
    def analyze_js(self, js_code: str) -> Dict[str, Any]:
        """分析JavaScript代码"""
        if not js_code:
            return {}
        
        analysis = {
            "animation_libraries": [],
            "animation_methods": [],
            "performance_optimizations": [],
            "complexity_score": 0
        }
        
        try:
            # 检测动画库
            if "gsap" in js_code.lower():
                analysis["animation_libraries"].append("GSAP")
            
            if "three" in js_code.lower():
                analysis["animation_libraries"].append("Three.js")
            
            if "anime" in js_code.lower():
                analysis["animation_libraries"].append("Anime.js")
            
            # 检测动画方法
            js_methods = ["requestAnimationFrame", "setInterval", "setTimeout"]
            for method in js_methods:
                if method in js_code:
                    analysis["animation_methods"].append(method)
            
            # 检测性能优化
            optimizations = ["will-change", "transform3d", "translateZ"]
            for opt in optimizations:
                if opt in js_code:
                    analysis["performance_optimizations"].append(opt)
            
            # 计算复杂度分数
            analysis["complexity_score"] = self.calculate_js_complexity_score(js_code)
            
        except Exception as e:
            logger.error(f"JavaScript分析失败: {e}")
        
        return analysis
    
    def analyze_html(self, html_code: str) -> Dict[str, Any]:
        """分析HTML代码"""
        if not html_code:
            return {}
        
        analysis = {
            "elements_count": 0,
            "classes_used": [],
            "ids_used": [],
            "semantic_elements": [],
            "accessibility_score": 0
        }
        
        try:
            # 统计元素数量
            elements = re.findall(r'<(\w+)', html_code)
            analysis["elements_count"] = len(elements)
            
            # 提取类名
            classes = re.findall(r'class=["\']([^"\']+)["\']', html_code)
            analysis["classes_used"] = classes
            
            # 提取ID
            ids = re.findall(r'id=["\']([^"\']+)["\']', html_code)
            analysis["ids_used"] = ids
            
            # 检测语义化元素
            semantic_tags = ["header", "nav", "main", "section", "article", "aside", "footer"]
            for tag in semantic_tags:
                if f"<{tag}" in html_code.lower():
                    analysis["semantic_elements"].append(tag)
            
            # 计算可访问性分数
            analysis["accessibility_score"] = self.calculate_accessibility_score(html_code)
            
        except Exception as e:
            logger.error(f"HTML分析失败: {e}")
        
        return analysis
    
    def calculate_css_performance_score(self, css_analysis: Dict[str, Any]) -> int:
        """计算CSS性能分数"""
        score = 50  # 基础分数
        
        # 使用高性能属性加分
        high_perf_props = ["transform", "opacity", "filter"]
        for prop in high_perf_props:
            if prop in css_analysis.get("properties_used", []):
                score += 10
        
        # 使用低性能属性扣分
        low_perf_props = ["left", "top", "width", "height"]
        for prop in low_perf_props:
            if prop in css_analysis.get("properties_used", []):
                score -= 5
        
        # 有缓动函数加分
        if css_analysis.get("easings"):
            score += 10
        
        return max(0, min(100, score))
    
    def calculate_js_complexity_score(self, js_code: str) -> int:
        """计算JavaScript复杂度分数"""
        score = 0
        
        # 代码长度
        score += min(50, len(js_code) // 100)
        
        # 函数数量
        functions = re.findall(r'function\s+\w+', js_code)
        score += len(functions) * 5
        
        # 循环结构
        loops = re.findall(r'(for|while)\s*\(', js_code)
        score += len(loops) * 10
        
        return min(100, score)
    
    def calculate_accessibility_score(self, html_code: str) -> int:
        """计算可访问性分数"""
        score = 50  # 基础分数
        
        # 检查alt属性
        if 'alt=' in html_code:
            score += 15
        
        # 检查aria属性
        if 'aria-' in html_code:
            score += 15
        
        # 检查语义化标签
        semantic_tags = ["header", "nav", "main", "section"]
        for tag in semantic_tags:
            if f"<{tag}" in html_code.lower():
                score += 5
        
        return max(0, min(100, score))
    
    def generate_performance_hints(self, analysis: Dict[str, Any]) -> List[str]:
        """生成性能提示"""
        hints = []
        
        css_analysis = analysis.get("css_analysis", {})
        
        # CSS性能提示
        if "left" in css_analysis.get("properties_used", []) or "top" in css_analysis.get("properties_used", []):
            hints.append("建议使用transform代替left/top属性以获得更好的性能")
        
        if not css_analysis.get("easings"):
            hints.append("建议添加缓动函数以提升动画质量")
        
        # JavaScript性能提示
        js_analysis = analysis.get("js_analysis", {})
        
        if "setInterval" in js_analysis.get("animation_methods", []):
            hints.append("建议使用requestAnimationFrame代替setInterval")
        
        if not js_analysis.get("performance_optimizations"):
            hints.append("建议添加will-change属性优化渲染性能")
        
        return hints
    
    def check_compatibility_issues(self, analysis: Dict[str, Any]) -> List[str]:
        """检查兼容性问题"""
        issues = []
        
        css_analysis = analysis.get("css_analysis", {})
        
        # 检查现代CSS特性
        modern_features = ["grid", "flexbox", "clip-path", "backdrop-filter"]
        for feature in modern_features:
            if feature in css_analysis.get("properties_used", []):
                issues.append(f"{feature}在旧版浏览器中可能不支持")
        
        return issues
    
    def generate_optimization_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        css_analysis = analysis.get("css_analysis", {})
        
        # CSS优化建议
        if css_analysis.get("performance_score", 0) < 70:
            suggestions.append("优化CSS动画性能，使用GPU加速属性")
        
        if len(css_analysis.get("keyframes", [])) > 5:
            suggestions.append("考虑合并相似的关键帧动画以减少代码复杂度")
        
        # 时长优化
        durations = css_analysis.get("durations", [])
        if durations:
            avg_duration = sum(d[0] for d in durations) / len(durations)
            if avg_duration > 3:
                suggestions.append("动画时长较长，考虑缩短以提升用户体验")
        
        return suggestions


class SolutionComparisonWidget(QWidget):
    """方案对比组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.compared_solutions = []
        self.analyzer = AnimationCodeAnalyzer()
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("方案对比分析")
        title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 对比表格
        self.comparison_table = QTableWidget()
        self.comparison_table.setAlternatingRowColors(True)
        layout.addWidget(self.comparison_table)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        add_solution_btn = QPushButton("➕ 添加方案")
        add_solution_btn.clicked.connect(self.add_solution_to_comparison)
        control_layout.addWidget(add_solution_btn)
        
        remove_solution_btn = QPushButton("➖ 移除方案")
        remove_solution_btn.clicked.connect(self.remove_solution_from_comparison)
        control_layout.addWidget(remove_solution_btn)
        
        clear_comparison_btn = QPushButton("🗑️ 清空对比")
        clear_comparison_btn.clicked.connect(self.clear_comparison)
        control_layout.addWidget(clear_comparison_btn)
        
        control_layout.addStretch()
        
        export_comparison_btn = QPushButton("📊 导出对比")
        export_comparison_btn.clicked.connect(self.export_comparison)
        control_layout.addWidget(export_comparison_btn)
        
        layout.addLayout(control_layout)
    
    def add_solution_to_comparison(self, solution: EnhancedAnimationSolution = None):
        """添加方案到对比"""
        try:
            if solution and solution not in self.compared_solutions:
                self.compared_solutions.append(solution)
                self.update_comparison_table()
                
                logger.info(f"方案已添加到对比: {solution.name}")
            
        except Exception as e:
            logger.error(f"添加方案到对比失败: {e}")
    
    def remove_solution_from_comparison(self):
        """从对比中移除方案"""
        try:
            current_row = self.comparison_table.currentRow()
            if 0 <= current_row < len(self.compared_solutions):
                removed_solution = self.compared_solutions.pop(current_row)
                self.update_comparison_table()
                
                logger.info(f"方案已从对比中移除: {removed_solution.name}")
            
        except Exception as e:
            logger.error(f"移除方案失败: {e}")
    
    def clear_comparison(self):
        """清空对比"""
        self.compared_solutions.clear()
        self.update_comparison_table()
    
    def update_comparison_table(self):
        """更新对比表格"""
        try:
            if not self.compared_solutions:
                self.comparison_table.clear()
                return
            
            # 设置表格结构
            comparison_items = [
                "方案名称", "技术栈", "分类", "综合评分", "质量分数", "性能分数",
                "创意分数", "用户评分", "使用次数", "代码长度", "动画数量", "兼容性"
            ]
            
            self.comparison_table.setRowCount(len(comparison_items))
            self.comparison_table.setColumnCount(len(self.compared_solutions))
            
            # 设置表头
            headers = [solution.name for solution in self.compared_solutions]
            self.comparison_table.setHorizontalHeaderLabels(headers)
            self.comparison_table.setVerticalHeaderLabels(comparison_items)
            
            # 填充数据
            for col, solution in enumerate(self.compared_solutions):
                analysis = self.analyzer.analyze_solution(solution)
                
                data = [
                    solution.name,
                    solution.tech_stack.value,
                    solution.category.value,
                    f"{solution.metrics.overall_score:.1f}",
                    f"{solution.metrics.quality_score:.1f}",
                    f"{solution.metrics.performance_score:.1f}",
                    f"{solution.metrics.creativity_score:.1f}",
                    f"{solution.user_rating:.1f}⭐",
                    str(solution.usage_count),
                    str(len(solution.html_code) + len(solution.css_code) + len(solution.js_code)),
                    str(len(analysis.get("css_analysis", {}).get("keyframes", []))),
                    f"{solution.metrics.compatibility_score:.1f}"
                ]
                
                for row, value in enumerate(data):
                    item = QTableWidgetItem(value)
                    
                    # 根据数值设置颜色
                    if row in [3, 4, 5, 6, 11]:  # 分数类项目
                        try:
                            score = float(value.replace("⭐", ""))
                            if score >= 80:
                                item.setBackground(QColor("#C8E6C9"))  # 绿色
                            elif score >= 60:
                                item.setBackground(QColor("#FFF9C4"))  # 黄色
                            else:
                                item.setBackground(QColor("#FFCDD2"))  # 红色
                        except:
                            pass
                    
                    self.comparison_table.setItem(row, col, item)
            
            # 调整列宽
            self.comparison_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            
        except Exception as e:
            logger.error(f"更新对比表格失败: {e}")
    
    def export_comparison(self):
        """导出对比结果"""
        try:
            if not self.compared_solutions:
                QMessageBox.warning(self, "警告", "没有可对比的方案")
                return
            
            # 生成对比报告
            report = self.generate_comparison_report()
            
            # 保存到文件
            from PyQt6.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出对比报告", "solution_comparison.txt",
                "文本文件 (*.txt);;JSON文件 (*.json);;所有文件 (*)"
            )
            
            if file_path:
                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(report, f, ensure_ascii=False, indent=2)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(self.format_comparison_report(report))
                
                QMessageBox.information(self, "成功", f"对比报告已导出到:\n{file_path}")
            
        except Exception as e:
            logger.error(f"导出对比失败: {e}")
    
    def generate_comparison_report(self) -> Dict[str, Any]:
        """生成对比报告"""
        report = {
            "comparison_time": datetime.now().isoformat(),
            "solutions_count": len(self.compared_solutions),
            "solutions": []
        }
        
        for solution in self.compared_solutions:
            analysis = self.analyzer.analyze_solution(solution)
            
            solution_data = {
                "name": solution.name,
                "id": solution.solution_id,
                "tech_stack": solution.tech_stack.value,
                "category": solution.category.value,
                "metrics": {
                    "overall_score": solution.metrics.overall_score,
                    "quality_score": solution.metrics.quality_score,
                    "performance_score": solution.metrics.performance_score,
                    "creativity_score": solution.metrics.creativity_score,
                    "usability_score": solution.metrics.usability_score,
                    "compatibility_score": solution.metrics.compatibility_score
                },
                "user_feedback": {
                    "rating": solution.user_rating,
                    "rating_count": solution.rating_count,
                    "usage_count": solution.usage_count,
                    "favorite_count": solution.favorite_count
                },
                "analysis": analysis
            }
            
            report["solutions"].append(solution_data)
        
        return report
    
    def format_comparison_report(self, report: Dict[str, Any]) -> str:
        """格式化对比报告"""
        lines = []
        
        lines.append("=" * 60)
        lines.append("方案对比分析报告")
        lines.append("=" * 60)
        lines.append(f"生成时间: {report['comparison_time']}")
        lines.append(f"对比方案数: {report['solutions_count']}")
        lines.append("")
        
        for i, solution_data in enumerate(report["solutions"], 1):
            lines.append(f"{i}. {solution_data['name']}")
            lines.append("-" * 40)
            lines.append(f"技术栈: {solution_data['tech_stack']}")
            lines.append(f"分类: {solution_data['category']}")
            lines.append("")
            
            lines.append("评估指标:")
            metrics = solution_data["metrics"]
            for metric_name, score in metrics.items():
                lines.append(f"  {metric_name}: {score:.1f}")
            lines.append("")
            
            lines.append("用户反馈:")
            feedback = solution_data["user_feedback"]
            lines.append(f"  评分: {feedback['rating']:.1f}⭐ ({feedback['rating_count']} 人)")
            lines.append(f"  使用次数: {feedback['usage_count']}")
            lines.append(f"  收藏次数: {feedback['favorite_count']}")
            lines.append("")
        
        return "\n".join(lines)


class SolutionVisualPreviewer(QWidget):
    """方案可视化预览器"""
    
    # 信号定义
    solution_analyzed = pyqtSignal(dict)         # 方案分析完成
    comparison_updated = pyqtSignal(list)        # 对比更新
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.analyzer = AnimationCodeAnalyzer()
        self.current_solution = None
        self.preview_mode = "visual"  # visual, code, analysis
        
        self.setup_ui()
        
        logger.info("方案可视化预览器初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 控制栏
        control_bar = self.create_control_bar()
        layout.addWidget(control_bar)
        
        # 主预览区
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：预览显示
        preview_panel = self.create_preview_panel()
        main_splitter.addWidget(preview_panel)
        
        # 右侧：分析信息
        analysis_panel = self.create_analysis_panel()
        main_splitter.addWidget(analysis_panel)
        
        main_splitter.setSizes([600, 400])
        layout.addWidget(main_splitter)
        
        # 底部：对比功能
        comparison_panel = SolutionComparisonWidget()
        layout.addWidget(comparison_panel)
    
    def create_control_bar(self):
        """创建控制栏"""
        control_bar = QFrame()
        control_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        control_bar.setMaximumHeight(50)
        
        layout = QHBoxLayout(control_bar)
        
        # 预览模式选择
        layout.addWidget(QLabel("预览模式:"))
        
        self.preview_mode_combo = QComboBox()
        self.preview_mode_combo.addItems(["可视化预览", "代码预览", "分析报告"])
        self.preview_mode_combo.currentTextChanged.connect(self.on_preview_mode_changed)
        layout.addWidget(self.preview_mode_combo)
        
        layout.addWidget(QLabel("|"))
        
        # 预览控制
        self.play_btn = QPushButton("▶️ 播放")
        self.play_btn.clicked.connect(self.toggle_preview_playback)
        layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_preview)
        layout.addWidget(self.stop_btn)
        
        layout.addWidget(QLabel("|"))
        
        # 缩放控制
        layout.addWidget(QLabel("缩放:"))
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(25, 200)  # 25% - 200%
        self.zoom_slider.setValue(100)
        self.zoom_slider.setMaximumWidth(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        layout.addWidget(self.zoom_slider)
        
        self.zoom_label = QLabel("100%")
        layout.addWidget(self.zoom_label)
        
        layout.addStretch()
        
        # 分析按钮
        analyze_btn = QPushButton("🔍 深度分析")
        analyze_btn.clicked.connect(self.perform_deep_analysis)
        layout.addWidget(analyze_btn)
        
        return control_bar
    
    def create_preview_panel(self):
        """创建预览面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 预览标签页
        self.preview_tabs = QTabWidget()
        
        # 可视化预览标签页
        try:
            self.web_preview = QWebEngineView()
            self.preview_tabs.addTab(self.web_preview, "🎬 可视化")
        except ImportError:
            # 如果没有WebEngine，使用文本预览
            self.text_preview = QTextEdit()
            self.text_preview.setReadOnly(True)
            self.preview_tabs.addTab(self.text_preview, "📝 代码预览")
        
        # 代码预览标签页
        self.code_preview = QTextEdit()
        self.code_preview.setReadOnly(True)
        self.code_preview.setFont(QFont("Consolas", 10))
        self.preview_tabs.addTab(self.code_preview, "💻 源代码")
        
        layout.addWidget(self.preview_tabs)
        
        return panel
    
    def create_analysis_panel(self):
        """创建分析面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 分析标签页
        analysis_tabs = QTabWidget()
        
        # 性能分析
        performance_tab = self.create_performance_analysis_tab()
        analysis_tabs.addTab(performance_tab, "⚡ 性能")
        
        # 质量分析
        quality_tab = self.create_quality_analysis_tab()
        analysis_tabs.addTab(quality_tab, "✨ 质量")
        
        # 兼容性分析
        compatibility_tab = self.create_compatibility_analysis_tab()
        analysis_tabs.addTab(compatibility_tab, "🌐 兼容性")
        
        layout.addWidget(analysis_tabs)
        
        return panel
    
    def create_performance_analysis_tab(self):
        """创建性能分析标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 性能指标
        metrics_group = QGroupBox("性能指标")
        metrics_layout = QVBoxLayout(metrics_group)
        
        self.performance_progress = QProgressBar()
        self.performance_progress.setRange(0, 100)
        self.performance_progress.setFormat("性能分数: %v%")
        metrics_layout.addWidget(self.performance_progress)
        
        # 性能详情
        self.performance_details = QTextEdit()
        self.performance_details.setMaximumHeight(150)
        self.performance_details.setReadOnly(True)
        metrics_layout.addWidget(self.performance_details)
        
        layout.addWidget(metrics_group)
        
        # 优化建议
        optimization_group = QGroupBox("优化建议")
        optimization_layout = QVBoxLayout(optimization_group)
        
        self.optimization_list = QListWidget()
        optimization_layout.addWidget(self.optimization_list)
        
        layout.addWidget(optimization_group)
        
        return tab
    
    def create_quality_analysis_tab(self):
        """创建质量分析标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 质量指标
        quality_group = QGroupBox("质量评估")
        quality_layout = QVBoxLayout(quality_group)
        
        quality_metrics = [
            ("代码结构", "code_structure"),
            ("动画流畅度", "animation_smoothness"),
            ("视觉吸引力", "visual_appeal")
        ]
        
        self.quality_progress_bars = {}
        
        for name, key in quality_metrics:
            metric_layout = QHBoxLayout()
            metric_layout.addWidget(QLabel(f"{name}:"))
            
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setFormat("%v%")
            progress.setMaximumHeight(20)
            metric_layout.addWidget(progress)
            
            self.quality_progress_bars[key] = progress
            quality_layout.addLayout(metric_layout)
        
        layout.addWidget(quality_group)
        
        # 质量详情
        details_group = QGroupBox("详细分析")
        details_layout = QVBoxLayout(details_group)
        
        self.quality_details = QTextEdit()
        self.quality_details.setReadOnly(True)
        details_layout.addWidget(self.quality_details)
        
        layout.addWidget(details_group)
        
        return tab
    
    def create_compatibility_analysis_tab(self):
        """创建兼容性分析标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 兼容性概览
        overview_group = QGroupBox("兼容性概览")
        overview_layout = QVBoxLayout(overview_group)
        
        self.compatibility_progress = QProgressBar()
        self.compatibility_progress.setRange(0, 100)
        self.compatibility_progress.setFormat("兼容性: %v%")
        overview_layout.addWidget(self.compatibility_progress)
        
        layout.addWidget(overview_group)
        
        # 兼容性问题
        issues_group = QGroupBox("兼容性问题")
        issues_layout = QVBoxLayout(issues_group)
        
        self.compatibility_issues = QListWidget()
        issues_layout.addWidget(self.compatibility_issues)
        
        layout.addWidget(issues_group)
        
        return tab
    
    def preview_solution(self, solution: EnhancedAnimationSolution):
        """预览方案"""
        try:
            self.current_solution = solution
            
            # 更新代码预览
            full_code = solution.html_code
            if solution.css_code:
                full_code += f"\n\n<style>\n{solution.css_code}\n</style>"
            if solution.js_code:
                full_code += f"\n\n<script>\n{solution.js_code}\n</script>"
            
            self.code_preview.setPlainText(full_code)
            
            # 更新可视化预览
            if hasattr(self, 'web_preview'):
                self.web_preview.setHtml(full_code)
            elif hasattr(self, 'text_preview'):
                self.text_preview.setPlainText(full_code)
            
            # 执行分析
            self.analyze_current_solution()
            
            logger.info(f"开始预览方案: {solution.name}")
            
        except Exception as e:
            logger.error(f"预览方案失败: {e}")
    
    def analyze_current_solution(self):
        """分析当前方案"""
        try:
            if not self.current_solution:
                return
            
            analysis = self.analyzer.analyze_solution(self.current_solution)
            
            # 更新性能分析
            self.update_performance_analysis(analysis)
            
            # 更新质量分析
            self.update_quality_analysis(analysis)
            
            # 更新兼容性分析
            self.update_compatibility_analysis(analysis)
            
            # 发送分析完成信号
            self.solution_analyzed.emit(analysis)
            
        except Exception as e:
            logger.error(f"分析方案失败: {e}")
    
    def update_performance_analysis(self, analysis: Dict[str, Any]):
        """更新性能分析"""
        try:
            performance_score = self.current_solution.metrics.performance_score
            self.performance_progress.setValue(int(performance_score))
            
            # 更新性能详情
            details = []
            
            css_analysis = analysis.get("css_analysis", {})
            if css_analysis:
                details.append(f"CSS性能分数: {css_analysis.get('performance_score', 0)}")
                details.append(f"使用的属性: {', '.join(css_analysis.get('properties_used', []))}")
                details.append(f"动画数量: {len(css_analysis.get('keyframes', []))}")
            
            js_analysis = analysis.get("js_analysis", {})
            if js_analysis:
                details.append(f"JavaScript复杂度: {js_analysis.get('complexity_score', 0)}")
                details.append(f"动画库: {', '.join(js_analysis.get('animation_libraries', []))}")
            
            self.performance_details.setPlainText("\n".join(details))
            
            # 更新优化建议
            self.optimization_list.clear()
            for suggestion in analysis.get("optimization_suggestions", []):
                item = QListWidgetItem(suggestion)
                self.optimization_list.addItem(item)
            
        except Exception as e:
            logger.error(f"更新性能分析失败: {e}")
    
    def update_quality_analysis(self, analysis: Dict[str, Any]):
        """更新质量分析"""
        try:
            # 更新质量进度条（简化实现）
            metrics = self.current_solution.metrics
            
            quality_scores = {
                "code_structure": metrics.quality_score * 0.8,  # 简化计算
                "animation_smoothness": metrics.performance_score * 0.9,
                "visual_appeal": metrics.creativity_score
            }
            
            for key, progress_bar in self.quality_progress_bars.items():
                score = quality_scores.get(key, 0)
                progress_bar.setValue(int(score))
            
            # 更新质量详情
            details = []
            details.append(f"综合质量分数: {metrics.quality_score:.1f}")
            details.append(f"代码结构评分: {quality_scores['code_structure']:.1f}")
            details.append(f"动画流畅度: {quality_scores['animation_smoothness']:.1f}")
            details.append(f"视觉吸引力: {quality_scores['visual_appeal']:.1f}")
            
            self.quality_details.setPlainText("\n".join(details))
            
        except Exception as e:
            logger.error(f"更新质量分析失败: {e}")
    
    def update_compatibility_analysis(self, analysis: Dict[str, Any]):
        """更新兼容性分析"""
        try:
            compatibility_score = self.current_solution.metrics.compatibility_score
            self.compatibility_progress.setValue(int(compatibility_score))
            
            # 更新兼容性问题
            self.compatibility_issues.clear()
            for issue in analysis.get("compatibility_issues", []):
                item = QListWidgetItem(issue)
                item.setIcon(QIcon("⚠️"))
                self.compatibility_issues.addItem(item)
            
        except Exception as e:
            logger.error(f"更新兼容性分析失败: {e}")
    
    def on_preview_mode_changed(self, mode: str):
        """预览模式改变"""
        mode_map = {
            "可视化预览": "visual",
            "代码预览": "code", 
            "分析报告": "analysis"
        }
        
        self.preview_mode = mode_map.get(mode, "visual")
        
        # 切换预览标签页
        if self.preview_mode == "visual" and hasattr(self, 'web_preview'):
            self.preview_tabs.setCurrentWidget(self.web_preview)
        elif self.preview_mode == "code":
            self.preview_tabs.setCurrentWidget(self.code_preview)
    
    def toggle_preview_playback(self):
        """切换预览播放状态"""
        if self.play_btn.text() == "▶️ 播放":
            self.play_btn.setText("⏸️ 暂停")
            # TODO: 开始播放动画
        else:
            self.play_btn.setText("▶️ 播放")
            # TODO: 暂停动画
    
    def stop_preview(self):
        """停止预览"""
        self.play_btn.setText("▶️ 播放")
        # TODO: 停止并重置动画
    
    def on_zoom_changed(self, value: int):
        """缩放改变"""
        self.zoom_label.setText(f"{value}%")
        # TODO: 应用缩放到预览
    
    def perform_deep_analysis(self):
        """执行深度分析"""
        try:
            if not self.current_solution:
                QMessageBox.warning(self, "警告", "请先选择一个方案进行预览")
                return
            
            # 执行深度分析
            analysis = self.analyzer.analyze_solution(self.current_solution)
            
            # 显示分析结果对话框
            self.show_analysis_dialog(analysis)
            
        except Exception as e:
            logger.error(f"深度分析失败: {e}")
    
    def show_analysis_dialog(self, analysis: Dict[str, Any]):
        """显示分析结果对话框"""
        dialog = QMessageBox(self)
        dialog.setWindowTitle("深度分析结果")
        dialog.setIcon(QMessageBox.Icon.Information)
        
        # 构建分析报告
        report_lines = []
        report_lines.append(f"方案: {self.current_solution.name}")
        report_lines.append("=" * 40)
        
        # CSS分析
        css_analysis = analysis.get("css_analysis", {})
        if css_analysis:
            report_lines.append("CSS分析:")
            report_lines.append(f"  关键帧动画: {len(css_analysis.get('keyframes', []))}")
            report_lines.append(f"  过渡效果: {len(css_analysis.get('transitions', []))}")
            report_lines.append(f"  性能分数: {css_analysis.get('performance_score', 0)}")
        
        # 性能提示
        if analysis.get("performance_hints"):
            report_lines.append("\n性能提示:")
            for hint in analysis["performance_hints"]:
                report_lines.append(f"  • {hint}")
        
        # 优化建议
        if analysis.get("optimization_suggestions"):
            report_lines.append("\n优化建议:")
            for suggestion in analysis["optimization_suggestions"]:
                report_lines.append(f"  • {suggestion}")
        
        dialog.setText("\n".join(report_lines))
        dialog.exec()
