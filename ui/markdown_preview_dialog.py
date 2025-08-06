"""
AI Animation Studio - Markdown预览对话框
提供Markdown内容的可视化预览功能
"""

import re
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QPushButton, QTextEdit, QGroupBox, QFormLayout, QScrollArea,
    QSplitter, QFrame, QCheckBox, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QFont, QTextDocument, QTextCursor, QTextCharFormat, QColor

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False

from core.logger import get_logger

logger = get_logger("markdown_preview_dialog")


class MarkdownPreviewDialog(QDialog):
    """Markdown预览对话框"""
    
    def __init__(self, markdown_content: str, title: str = "Markdown预览", parent=None):
        super().__init__(parent)
        
        self.markdown_content = markdown_content
        self.title = title
        
        self.setup_ui()
        self.render_markdown()
        
        logger.info(f"打开Markdown预览: {title}")
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle(f"📖 {self.title}")
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # 主要内容区域
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧原始内容
        source_panel = self.create_source_panel()
        content_splitter.addWidget(source_panel)
        
        # 右侧预览内容
        preview_panel = self.create_preview_panel()
        content_splitter.addWidget(preview_panel)
        
        # 设置分割比例
        content_splitter.setSizes([400, 500])
        layout.addWidget(content_splitter)
        
        # 底部状态栏
        status_bar = self.create_status_bar()
        layout.addWidget(status_bar)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(toolbar)
        
        # 预览模式选择
        layout.addWidget(QLabel("预览模式:"))
        self.preview_mode_combo = QComboBox()
        self.preview_mode_combo.addItems(["富文本", "HTML", "原始文本"])
        self.preview_mode_combo.currentTextChanged.connect(self.change_preview_mode)
        layout.addWidget(self.preview_mode_combo)
        
        layout.addWidget(QLabel("|"))
        
        # 字体大小控制
        layout.addWidget(QLabel("字体大小:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        self.font_size_spin.valueChanged.connect(self.change_font_size)
        layout.addWidget(self.font_size_spin)
        
        layout.addWidget(QLabel("|"))
        
        # 显示选项
        self.show_line_numbers_cb = QCheckBox("显示行号")
        self.show_line_numbers_cb.toggled.connect(self.toggle_line_numbers)
        layout.addWidget(self.show_line_numbers_cb)
        
        self.word_wrap_cb = QCheckBox("自动换行")
        self.word_wrap_cb.setChecked(True)
        self.word_wrap_cb.toggled.connect(self.toggle_word_wrap)
        layout.addWidget(self.word_wrap_cb)
        
        layout.addStretch()
        
        # 导出按钮
        self.export_html_btn = QPushButton("📤 导出HTML")
        self.export_html_btn.clicked.connect(self.export_html)
        layout.addWidget(self.export_html_btn)
        
        # 打印按钮
        self.print_btn = QPushButton("🖨️ 打印")
        self.print_btn.clicked.connect(self.print_preview)
        layout.addWidget(self.print_btn)
        
        return toolbar
    
    def create_source_panel(self):
        """创建源码面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 标题
        title_label = QLabel("📝 Markdown源码")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 源码编辑器
        self.source_editor = QTextEdit()
        self.source_editor.setPlainText(self.markdown_content)
        self.source_editor.setFont(QFont("Consolas", 10))
        self.source_editor.setReadOnly(True)
        layout.addWidget(self.source_editor)
        
        # 源码统计
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        stats_layout = QHBoxLayout(stats_frame)
        
        # 计算统计信息
        lines = len(self.markdown_content.split('\n'))
        words = len(self.markdown_content.split())
        chars = len(self.markdown_content)
        
        self.stats_label = QLabel(f"行数: {lines} | 单词: {words} | 字符: {chars}")
        self.stats_label.setStyleSheet("color: #666; font-size: 11px;")
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(stats_frame)
        
        return panel
    
    def create_preview_panel(self):
        """创建预览面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 标题
        title_label = QLabel("👁️ 预览效果")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 预览标签页
        self.preview_tabs = QTabWidget()
        
        # 富文本预览
        self.rich_text_preview = QTextEdit()
        self.rich_text_preview.setReadOnly(True)
        self.preview_tabs.addTab(self.rich_text_preview, "富文本")
        
        # HTML预览
        if WEB_ENGINE_AVAILABLE:
            self.html_preview = QWebEngineView()
            self.preview_tabs.addTab(self.html_preview, "HTML")
        else:
            self.html_text_preview = QTextEdit()
            self.html_text_preview.setReadOnly(True)
            self.html_text_preview.setFont(QFont("Consolas", 10))
            self.preview_tabs.addTab(self.html_text_preview, "HTML代码")
        
        # 原始文本预览
        self.plain_text_preview = QTextEdit()
        self.plain_text_preview.setReadOnly(True)
        self.plain_text_preview.setFont(QFont("Consolas", 10))
        self.preview_tabs.addTab(self.plain_text_preview, "原始文本")
        
        layout.addWidget(self.preview_tabs)
        
        return panel
    
    def create_status_bar(self):
        """创建状态栏"""
        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(status_bar)
        
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton("❌ 关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return status_bar
    
    def render_markdown(self):
        """渲染Markdown内容"""
        try:
            # 渲染富文本预览
            html_content = self.markdown_to_html(self.markdown_content)
            self.rich_text_preview.setHtml(html_content)
            
            # 渲染HTML预览
            if WEB_ENGINE_AVAILABLE:
                full_html = self.create_full_html(html_content)
                self.html_preview.setHtml(full_html)
            else:
                self.html_text_preview.setPlainText(html_content)
            
            # 渲染原始文本预览
            self.plain_text_preview.setPlainText(self.markdown_content)
            
            self.status_label.setText("预览已更新")
            
        except Exception as e:
            logger.error(f"渲染Markdown失败: {e}")
            self.status_label.setText("渲染失败")
    
    def markdown_to_html(self, markdown_text: str) -> str:
        """将Markdown转换为HTML"""
        try:
            # 简单的Markdown到HTML转换
            html = markdown_text
            
            # 标题转换
            html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
            html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
            html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
            html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
            
            # 粗体和斜体
            html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
            html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
            
            # 代码块
            html = re.sub(r'```(.+?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
            html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
            
            # 链接
            html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
            
            # 列表
            html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
            html = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', html, flags=re.MULTILINE)
            
            # 段落
            paragraphs = html.split('\n\n')
            html_paragraphs = []
            
            for para in paragraphs:
                para = para.strip()
                if para:
                    if not any(tag in para for tag in ['<h', '<pre>', '<li>', '<ul>', '<ol>']):
                        para = f'<p>{para}</p>'
                    html_paragraphs.append(para)
            
            html = '\n'.join(html_paragraphs)
            
            # 包装列表项
            html = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
            
            return html
            
        except Exception as e:
            logger.error(f"Markdown转HTML失败: {e}")
            return f"<p>转换失败: {e}</p>"
    
    def create_full_html(self, content: str) -> str:
        """创建完整的HTML文档"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{self.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        h1 {{ border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }}
        code {{
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        pre {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 0;
            padding-left: 20px;
            color: #7f8c8d;
        }}
        ul, ol {{ padding-left: 20px; }}
        li {{ margin-bottom: 5px; }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
{content}
</body>
</html>
"""
    
    def change_preview_mode(self, mode: str):
        """切换预览模式"""
        try:
            if mode == "富文本":
                self.preview_tabs.setCurrentIndex(0)
            elif mode == "HTML":
                self.preview_tabs.setCurrentIndex(1)
            elif mode == "原始文本":
                self.preview_tabs.setCurrentIndex(2)
            
        except Exception as e:
            logger.error(f"切换预览模式失败: {e}")
    
    def change_font_size(self, size: int):
        """改变字体大小"""
        try:
            font = QFont("Consolas", size)
            self.source_editor.setFont(font)
            self.plain_text_preview.setFont(font)
            
            if hasattr(self, 'html_text_preview'):
                self.html_text_preview.setFont(font)
            
        except Exception as e:
            logger.error(f"改变字体大小失败: {e}")
    
    def toggle_line_numbers(self, enabled: bool):
        """切换行号显示"""
        try:
            # 这里可以实现行号显示功能
            # 由于QTextEdit没有内置行号，这里简化处理
            self.status_label.setText(f"行号显示: {'开启' if enabled else '关闭'}")
            
        except Exception as e:
            logger.error(f"切换行号显示失败: {e}")
    
    def toggle_word_wrap(self, enabled: bool):
        """切换自动换行"""
        try:
            wrap_mode = QTextEdit.LineWrapMode.WidgetWidth if enabled else QTextEdit.LineWrapMode.NoWrap
            
            self.source_editor.setLineWrapMode(wrap_mode)
            self.rich_text_preview.setLineWrapMode(wrap_mode)
            self.plain_text_preview.setLineWrapMode(wrap_mode)
            
            if hasattr(self, 'html_text_preview'):
                self.html_text_preview.setLineWrapMode(wrap_mode)
            
        except Exception as e:
            logger.error(f"切换自动换行失败: {e}")
    
    def export_html(self):
        """导出HTML文件"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出HTML", f"{self.title}.html", "HTML文件 (*.html)"
            )
            
            if file_path:
                html_content = self.markdown_to_html(self.markdown_content)
                full_html = self.create_full_html(html_content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(full_html)
                
                self.status_label.setText(f"已导出到: {file_path}")
            
        except Exception as e:
            logger.error(f"导出HTML失败: {e}")
            self.status_label.setText("导出失败")
    
    def print_preview(self):
        """打印预览"""
        try:
            from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
            
            printer = QPrinter()
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                self.rich_text_preview.print(printer)
                self.status_label.setText("打印完成")
            
        except Exception as e:
            logger.error(f"打印失败: {e}")
            self.status_label.setText("打印失败")
