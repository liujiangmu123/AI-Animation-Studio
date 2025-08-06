"""
AI Animation Studio - 增强代码查看器
提供语法高亮、代码折叠、搜索等功能的代码查看器
"""

import re
from typing import Dict, List, Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPlainTextEdit,
    QLineEdit, QPushButton, QLabel, QComboBox, QCheckBox, QFrame,
    QSplitter, QTabWidget, QTreeWidget, QTreeWidgetItem, QScrollArea,
    QSpinBox, QSlider, QGroupBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRegularExpression
from PyQt6.QtGui import (
    QFont, QColor, QTextCursor, QTextDocument, QSyntaxHighlighter,
    QTextCharFormat, QTextBlockFormat, QPalette, QFontMetrics,
    QKeySequence, QShortcut, QAction
)

from core.logger import get_logger

logger = get_logger("enhanced_code_viewer")


class HTMLSyntaxHighlighter(QSyntaxHighlighter):
    """HTML语法高亮器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_highlighting_rules()
    
    def setup_highlighting_rules(self):
        """设置高亮规则"""
        self.highlighting_rules = []
        
        # HTML标签
        tag_format = QTextCharFormat()
        tag_format.setColor(QColor("#3498db"))
        tag_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((
            QRegularExpression(r"<[!?/]?\b[A-Za-z0-9-]+(?:\s[^>]*)?>"),
            tag_format
        ))
        
        # 属性名
        attr_name_format = QTextCharFormat()
        attr_name_format.setColor(QColor("#e74c3c"))
        self.highlighting_rules.append((
            QRegularExpression(r"\b[A-Za-z0-9-]+(?=\s*=)"),
            attr_name_format
        ))
        
        # 属性值
        attr_value_format = QTextCharFormat()
        attr_value_format.setColor(QColor("#27ae60"))
        self.highlighting_rules.append((
            QRegularExpression(r'"[^"]*"'),
            attr_value_format
        ))
        self.highlighting_rules.append((
            QRegularExpression(r"'[^']*'"),
            attr_value_format
        ))
        
        # CSS样式块
        css_format = QTextCharFormat()
        css_format.setColor(QColor("#9b59b6"))
        self.highlighting_rules.append((
            QRegularExpression(r"<style[^>]*>.*?</style>", QRegularExpression.PatternOption.DotMatchesEverythingOption),
            css_format
        ))
        
        # JavaScript块
        js_format = QTextCharFormat()
        js_format.setColor(QColor("#f39c12"))
        self.highlighting_rules.append((
            QRegularExpression(r"<script[^>]*>.*?</script>", QRegularExpression.PatternOption.DotMatchesEverythingOption),
            js_format
        ))
        
        # 注释
        comment_format = QTextCharFormat()
        comment_format.setColor(QColor("#95a5a6"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((
            QRegularExpression(r"<!--.*?-->"),
            comment_format
        ))
    
    def highlightBlock(self, text):
        """高亮文本块"""
        for pattern, format in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class CSSJSSyntaxHighlighter(QSyntaxHighlighter):
    """CSS/JavaScript语法高亮器"""
    
    def __init__(self, language="css", parent=None):
        super().__init__(parent)
        self.language = language
        self.setup_highlighting_rules()
    
    def setup_highlighting_rules(self):
        """设置高亮规则"""
        self.highlighting_rules = []
        
        if self.language == "css":
            self.setup_css_rules()
        elif self.language == "javascript":
            self.setup_js_rules()
    
    def setup_css_rules(self):
        """设置CSS高亮规则"""
        # CSS选择器
        selector_format = QTextCharFormat()
        selector_format.setColor(QColor("#3498db"))
        selector_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((
            QRegularExpression(r"[.#]?[a-zA-Z][a-zA-Z0-9_-]*(?=\s*\{)"),
            selector_format
        ))
        
        # CSS属性
        property_format = QTextCharFormat()
        property_format.setColor(QColor("#e74c3c"))
        self.highlighting_rules.append((
            QRegularExpression(r"\b[a-zA-Z-]+(?=\s*:)"),
            property_format
        ))
        
        # CSS值
        value_format = QTextCharFormat()
        value_format.setColor(QColor("#27ae60"))
        self.highlighting_rules.append((
            QRegularExpression(r":\s*[^;]+"),
            value_format
        ))
        
        # 注释
        comment_format = QTextCharFormat()
        comment_format.setColor(QColor("#95a5a6"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((
            QRegularExpression(r"/\*.*?\*/"),
            comment_format
        ))
    
    def setup_js_rules(self):
        """设置JavaScript高亮规则"""
        # 关键字
        keyword_format = QTextCharFormat()
        keyword_format.setColor(QColor("#9b59b6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = [
            "var", "let", "const", "function", "return", "if", "else",
            "for", "while", "do", "break", "continue", "switch", "case",
            "default", "try", "catch", "finally", "throw", "new", "this"
        ]
        
        for keyword in keywords:
            self.highlighting_rules.append((
                QRegularExpression(f"\\b{keyword}\\b"),
                keyword_format
            ))
        
        # 字符串
        string_format = QTextCharFormat()
        string_format.setColor(QColor("#27ae60"))
        self.highlighting_rules.append((
            QRegularExpression(r'"[^"]*"'),
            string_format
        ))
        self.highlighting_rules.append((
            QRegularExpression(r"'[^']*'"),
            string_format
        ))
        
        # 数字
        number_format = QTextCharFormat()
        number_format.setColor(QColor("#f39c12"))
        self.highlighting_rules.append((
            QRegularExpression(r"\b\d+\.?\d*\b"),
            number_format
        ))
        
        # 注释
        comment_format = QTextCharFormat()
        comment_format.setColor(QColor("#95a5a6"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((
            QRegularExpression(r"//.*"),
            comment_format
        ))
        self.highlighting_rules.append((
            QRegularExpression(r"/\*.*?\*/"),
            comment_format
        ))
    
    def highlightBlock(self, text):
        """高亮文本块"""
        for pattern, format in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class LineNumberArea(QWidget):
    """行号区域"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
    
    def sizeHint(self):
        return self.code_editor.line_number_area_width()
    
    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class EnhancedCodeEditor(QPlainTextEdit):
    """增强代码编辑器"""
    
    def __init__(self, language="html", parent=None):
        super().__init__(parent)
        
        self.language = language
        self.line_number_area = LineNumberArea(self)
        
        self.setup_editor()
        self.setup_syntax_highlighter()
        self.setup_signals()
        
    def setup_editor(self):
        """设置编辑器"""
        # 设置字体
        font = QFont("Consolas", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # 设置样式
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #3399ff;
                line-height: 1.4;
            }
        """)
        
        # 设置制表符宽度
        metrics = QFontMetrics(self.font())
        self.setTabStopDistance(4 * metrics.horizontalAdvance(' '))
        
        # 启用行号
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        
    def setup_syntax_highlighter(self):
        """设置语法高亮"""
        if self.language == "html":
            self.highlighter = HTMLSyntaxHighlighter(self.document())
        elif self.language in ["css", "javascript"]:
            self.highlighter = CSSJSSyntaxHighlighter(self.language, self.document())
        else:
            self.highlighter = None
    
    def setup_signals(self):
        """设置信号连接"""
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.highlight_current_line()
    
    def line_number_area_width(self):
        """计算行号区域宽度"""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self, new_block_count):
        """更新行号区域宽度"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        """更新行号区域"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """调整大小事件"""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            cr.left(), cr.top(), self.line_number_area_width(), cr.height()
        )
    
    def line_number_area_paint_event(self, event):
        """绘制行号区域"""
        from PyQt6.QtGui import QPainter
        
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#3c3c3c"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#888888"))
                painter.drawText(
                    0, int(top), self.line_number_area.width(), 
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number
                )
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
    
    def highlight_current_line(self):
        """高亮当前行"""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            
            line_color = QColor("#404040")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)


class CodeStructureTree(QTreeWidget):
    """代码结构树"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setHeaderLabel("代码结构")
        self.setMaximumWidth(250)
        
        self.setup_style()
    
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #3399ff;
            }
            QTreeWidget::item {
                padding: 2px;
            }
            QTreeWidget::item:hover {
                background-color: #404040;
            }
        """)
    
    def parse_html_structure(self, html_content: str):
        """解析HTML结构"""
        try:
            self.clear()
            
            # 简单的HTML解析
            lines = html_content.split('\n')
            stack = []
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # 查找HTML标签
                tag_match = re.search(r'<(\w+)[^>]*>', line)
                if tag_match:
                    tag_name = tag_match.group(1)
                    
                    # 创建树项
                    if stack:
                        parent_item = stack[-1]
                        item = QTreeWidgetItem(parent_item)
                    else:
                        item = QTreeWidgetItem(self)
                    
                    item.setText(0, f"{tag_name} (行 {line_num})")
                    item.setData(0, Qt.ItemDataRole.UserRole, line_num)
                    
                    # 如果不是自闭合标签，加入栈
                    if not line.endswith('/>') and not tag_name.lower() in ['br', 'hr', 'img', 'input']:
                        stack.append(item)
                
                # 查找结束标签
                end_tag_match = re.search(r'</(\w+)>', line)
                if end_tag_match and stack:
                    stack.pop()
            
            self.expandAll()
            
        except Exception as e:
            logger.error(f"解析HTML结构失败: {e}")


class EnhancedCodeViewer(QWidget):
    """增强代码查看器"""
    
    # 信号定义
    content_changed = pyqtSignal(str)  # 内容改变
    search_performed = pyqtSignal(str, int)  # 搜索执行
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_language = "html"
        self.search_results = []
        self.current_search_index = -1
        
        self.setup_ui()
        self.setup_shortcuts()
        
        logger.info("增强代码查看器初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # 主要内容区域
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧代码编辑器
        editor_panel = self.create_editor_panel()
        content_splitter.addWidget(editor_panel)
        
        # 右侧结构树
        self.structure_tree = CodeStructureTree()
        self.structure_tree.itemClicked.connect(self.on_structure_item_clicked)
        content_splitter.addWidget(self.structure_tree)
        
        # 设置分割比例
        content_splitter.setSizes([800, 200])
        layout.addWidget(content_splitter)
        
        # 状态栏
        status_bar = self.create_status_bar()
        layout.addWidget(status_bar)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(toolbar)
        
        # 语言选择
        layout.addWidget(QLabel("语言:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["HTML", "CSS", "JavaScript"])
        self.language_combo.currentTextChanged.connect(self.change_language)
        layout.addWidget(self.language_combo)
        
        layout.addWidget(QLabel("|"))
        
        # 搜索功能
        layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入搜索内容...")
        self.search_input.returnPressed.connect(self.search_text)
        layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("🔍 搜索")
        self.search_btn.clicked.connect(self.search_text)
        layout.addWidget(self.search_btn)
        
        self.prev_btn = QPushButton("⬆️ 上一个")
        self.prev_btn.clicked.connect(self.find_previous)
        self.prev_btn.setEnabled(False)
        layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("⬇️ 下一个")
        self.next_btn.clicked.connect(self.find_next)
        self.next_btn.setEnabled(False)
        layout.addWidget(self.next_btn)
        
        layout.addWidget(QLabel("|"))
        
        # 显示选项
        self.show_line_numbers_cb = QCheckBox("显示行号")
        self.show_line_numbers_cb.setChecked(True)
        self.show_line_numbers_cb.toggled.connect(self.toggle_line_numbers)
        layout.addWidget(self.show_line_numbers_cb)
        
        self.word_wrap_cb = QCheckBox("自动换行")
        self.word_wrap_cb.toggled.connect(self.toggle_word_wrap)
        layout.addWidget(self.word_wrap_cb)
        
        layout.addStretch()
        
        # 功能按钮
        self.format_btn = QPushButton("🎨 格式化")
        self.format_btn.clicked.connect(self.format_code)
        layout.addWidget(self.format_btn)
        
        self.copy_btn = QPushButton("📋 复制")
        self.copy_btn.clicked.connect(self.copy_code)
        layout.addWidget(self.copy_btn)
        
        return toolbar

    def create_editor_panel(self):
        """创建编辑器面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 代码标签页
        self.code_tabs = QTabWidget()

        # HTML标签页
        self.html_editor = EnhancedCodeEditor("html")
        self.html_editor.setReadOnly(True)
        self.code_tabs.addTab(self.html_editor, "HTML")

        # CSS标签页
        self.css_editor = EnhancedCodeEditor("css")
        self.css_editor.setReadOnly(True)
        self.code_tabs.addTab(self.css_editor, "CSS")

        # JavaScript标签页
        self.js_editor = EnhancedCodeEditor("javascript")
        self.js_editor.setReadOnly(True)
        self.code_tabs.addTab(self.js_editor, "JavaScript")

        # 完整代码标签页
        self.full_editor = EnhancedCodeEditor("html")
        self.full_editor.setReadOnly(True)
        self.code_tabs.addTab(self.full_editor, "完整代码")

        # 连接标签页切换事件
        self.code_tabs.currentChanged.connect(self.on_tab_changed)

        layout.addWidget(self.code_tabs)

        return panel

    def create_status_bar(self):
        """创建状态栏"""
        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(status_bar)

        # 行列信息
        self.cursor_info_label = QLabel("行: 1, 列: 1")
        layout.addWidget(self.cursor_info_label)

        layout.addStretch()

        # 搜索结果信息
        self.search_info_label = QLabel("")
        layout.addWidget(self.search_info_label)

        layout.addStretch()

        # 字符统计
        self.stats_label = QLabel("字符: 0, 行: 0")
        layout.addWidget(self.stats_label)

        return status_bar

    def setup_shortcuts(self):
        """设置快捷键"""
        # 搜索快捷键
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.focus_search)

        # 查找下一个
        find_next_shortcut = QShortcut(QKeySequence("F3"), self)
        find_next_shortcut.activated.connect(self.find_next)

        # 查找上一个
        find_prev_shortcut = QShortcut(QKeySequence("Shift+F3"), self)
        find_prev_shortcut.activated.connect(self.find_previous)

        # 复制快捷键
        copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        copy_shortcut.activated.connect(self.copy_code)

        # 全选快捷键
        select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        select_all_shortcut.activated.connect(self.select_all_code)

    def load_content(self, html_content: str):
        """加载内容"""
        try:
            # 解析HTML内容
            html_part, css_part, js_part = self.parse_html_content(html_content)

            # 加载到各个编辑器
            self.html_editor.setPlainText(html_part)
            self.css_editor.setPlainText(css_part)
            self.js_editor.setPlainText(js_part)
            self.full_editor.setPlainText(html_content)

            # 更新结构树
            self.structure_tree.parse_html_structure(html_content)

            # 更新统计信息
            self.update_statistics()

            # 发送内容改变信号
            self.content_changed.emit(html_content)

            logger.info("代码内容已加载")

        except Exception as e:
            logger.error(f"加载代码内容失败: {e}")

    def parse_html_content(self, html_content: str) -> Tuple[str, str, str]:
        """解析HTML内容，分离HTML、CSS、JavaScript"""
        try:
            html_part = html_content
            css_part = ""
            js_part = ""

            # 提取CSS
            css_matches = re.findall(r'<style[^>]*>(.*?)</style>', html_content, re.DOTALL | re.IGNORECASE)
            if css_matches:
                css_part = '\n'.join(css_matches)
                # 从HTML中移除CSS块
                html_part = re.sub(r'<style[^>]*>.*?</style>', '', html_part, flags=re.DOTALL | re.IGNORECASE)

            # 提取JavaScript
            js_matches = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL | re.IGNORECASE)
            if js_matches:
                js_part = '\n'.join(js_matches)
                # 从HTML中移除JavaScript块
                html_part = re.sub(r'<script[^>]*>.*?</script>', '', html_part, flags=re.DOTALL | re.IGNORECASE)

            # 清理HTML部分
            html_part = html_part.strip()
            css_part = css_part.strip()
            js_part = js_part.strip()

            return html_part, css_part, js_part

        except Exception as e:
            logger.error(f"解析HTML内容失败: {e}")
            return html_content, "", ""

    def get_current_editor(self) -> EnhancedCodeEditor:
        """获取当前编辑器"""
        current_index = self.code_tabs.currentIndex()
        return self.code_tabs.widget(current_index)

    def change_language(self, language: str):
        """改变语言"""
        try:
            self.current_language = language.lower()

            # 切换到对应的标签页
            language_map = {
                "html": 0,
                "css": 1,
                "javascript": 2
            }

            if self.current_language in language_map:
                self.code_tabs.setCurrentIndex(language_map[self.current_language])

        except Exception as e:
            logger.error(f"改变语言失败: {e}")

    def on_tab_changed(self, index: int):
        """标签页改变事件"""
        try:
            # 更新语言选择
            language_map = {0: "HTML", 1: "CSS", 2: "JavaScript", 3: "HTML"}
            if index in language_map:
                self.language_combo.setCurrentText(language_map[index])

            # 更新光标信息
            self.update_cursor_info()

        except Exception as e:
            logger.error(f"处理标签页改变失败: {e}")

    def search_text(self):
        """搜索文本"""
        try:
            search_term = self.search_input.text().strip()
            if not search_term:
                return

            current_editor = self.get_current_editor()
            content = current_editor.toPlainText()

            # 查找所有匹配项
            self.search_results = []
            start = 0

            while True:
                index = content.find(search_term, start)
                if index == -1:
                    break

                self.search_results.append(index)
                start = index + 1

            # 更新搜索状态
            if self.search_results:
                self.current_search_index = 0
                self.highlight_search_result()
                self.prev_btn.setEnabled(len(self.search_results) > 1)
                self.next_btn.setEnabled(len(self.search_results) > 1)

                self.search_info_label.setText(f"找到 {len(self.search_results)} 个匹配项")
            else:
                self.search_info_label.setText("未找到匹配项")
                self.prev_btn.setEnabled(False)
                self.next_btn.setEnabled(False)

            # 发送搜索信号
            self.search_performed.emit(search_term, len(self.search_results))

        except Exception as e:
            logger.error(f"搜索文本失败: {e}")

    def highlight_search_result(self):
        """高亮搜索结果"""
        try:
            if not self.search_results or self.current_search_index < 0:
                return

            current_editor = self.get_current_editor()
            search_term = self.search_input.text()

            # 移动光标到搜索结果位置
            cursor = current_editor.textCursor()
            cursor.setPosition(self.search_results[self.current_search_index])
            cursor.setPosition(
                self.search_results[self.current_search_index] + len(search_term),
                QTextCursor.MoveMode.KeepAnchor
            )

            current_editor.setTextCursor(cursor)
            current_editor.ensureCursorVisible()

            # 更新搜索信息
            self.search_info_label.setText(
                f"第 {self.current_search_index + 1} 个，共 {len(self.search_results)} 个"
            )

        except Exception as e:
            logger.error(f"高亮搜索结果失败: {e}")

    def find_next(self):
        """查找下一个"""
        try:
            if not self.search_results:
                return

            self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
            self.highlight_search_result()

        except Exception as e:
            logger.error(f"查找下一个失败: {e}")

    def find_previous(self):
        """查找上一个"""
        try:
            if not self.search_results:
                return

            self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
            self.highlight_search_result()

        except Exception as e:
            logger.error(f"查找上一个失败: {e}")

    def focus_search(self):
        """聚焦搜索框"""
        self.search_input.setFocus()
        self.search_input.selectAll()

    def toggle_line_numbers(self, enabled: bool):
        """切换行号显示"""
        try:
            # 这里可以实现行号显示切换
            # 由于我们的编辑器已经内置行号，这里主要是控制显示/隐藏
            pass

        except Exception as e:
            logger.error(f"切换行号显示失败: {e}")

    def toggle_word_wrap(self, enabled: bool):
        """切换自动换行"""
        try:
            wrap_mode = QPlainTextEdit.LineWrapMode.WidgetWidth if enabled else QPlainTextEdit.LineWrapMode.NoWrap

            self.html_editor.setLineWrapMode(wrap_mode)
            self.css_editor.setLineWrapMode(wrap_mode)
            self.js_editor.setLineWrapMode(wrap_mode)
            self.full_editor.setLineWrapMode(wrap_mode)

        except Exception as e:
            logger.error(f"切换自动换行失败: {e}")

    def format_code(self):
        """格式化代码"""
        try:
            current_editor = self.get_current_editor()
            content = current_editor.toPlainText()

            # 简单的代码格式化
            if self.current_language == "html":
                formatted_content = self.format_html(content)
            elif self.current_language == "css":
                formatted_content = self.format_css(content)
            elif self.current_language == "javascript":
                formatted_content = self.format_js(content)
            else:
                formatted_content = content

            current_editor.setPlainText(formatted_content)

        except Exception as e:
            logger.error(f"格式化代码失败: {e}")

    def format_html(self, html: str) -> str:
        """格式化HTML"""
        try:
            # 简单的HTML格式化
            lines = html.split('\n')
            formatted_lines = []
            indent_level = 0

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 减少缩进（结束标签）
                if line.startswith('</'):
                    indent_level = max(0, indent_level - 1)

                # 添加缩进
                formatted_lines.append('  ' * indent_level + line)

                # 增加缩进（开始标签，非自闭合）
                if line.startswith('<') and not line.startswith('</') and not line.endswith('/>'):
                    tag_name = re.search(r'<(\w+)', line)
                    if tag_name and tag_name.group(1).lower() not in ['br', 'hr', 'img', 'input']:
                        indent_level += 1

            return '\n'.join(formatted_lines)

        except Exception as e:
            logger.error(f"格式化HTML失败: {e}")
            return html

    def format_css(self, css: str) -> str:
        """格式化CSS"""
        try:
            # 简单的CSS格式化
            css = re.sub(r'\s*{\s*', ' {\n  ', css)
            css = re.sub(r';\s*', ';\n  ', css)
            css = re.sub(r'\s*}\s*', '\n}\n\n', css)
            css = re.sub(r'\n\s*\n', '\n', css)

            return css.strip()

        except Exception as e:
            logger.error(f"格式化CSS失败: {e}")
            return css

    def format_js(self, js: str) -> str:
        """格式化JavaScript"""
        try:
            # 简单的JavaScript格式化
            js = re.sub(r'\s*{\s*', ' {\n  ', js)
            js = re.sub(r';\s*', ';\n  ', js)
            js = re.sub(r'\s*}\s*', '\n}\n\n', js)
            js = re.sub(r'\n\s*\n', '\n', js)

            return js.strip()

        except Exception as e:
            logger.error(f"格式化JavaScript失败: {e}")
            return js

    def copy_code(self):
        """复制代码"""
        try:
            current_editor = self.get_current_editor()

            # 如果有选中文本，复制选中文本；否则复制全部
            cursor = current_editor.textCursor()
            if cursor.hasSelection():
                text = cursor.selectedText()
            else:
                text = current_editor.toPlainText()

            # 复制到剪贴板
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

            self.search_info_label.setText("已复制到剪贴板")

            # 3秒后清除状态信息
            QTimer.singleShot(3000, lambda: self.search_info_label.setText(""))

        except Exception as e:
            logger.error(f"复制代码失败: {e}")

    def select_all_code(self):
        """全选代码"""
        try:
            current_editor = self.get_current_editor()
            current_editor.selectAll()

        except Exception as e:
            logger.error(f"全选代码失败: {e}")

    def on_structure_item_clicked(self, item: QTreeWidgetItem, column: int):
        """结构树项点击事件"""
        try:
            line_number = item.data(0, Qt.ItemDataRole.UserRole)
            if line_number:
                # 跳转到对应行
                current_editor = self.get_current_editor()
                cursor = current_editor.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.MoveAnchor, line_number - 1)
                current_editor.setTextCursor(cursor)
                current_editor.ensureCursorVisible()
                current_editor.setFocus()

        except Exception as e:
            logger.error(f"处理结构树点击失败: {e}")

    def update_cursor_info(self):
        """更新光标信息"""
        try:
            current_editor = self.get_current_editor()
            cursor = current_editor.textCursor()

            # 计算行列号
            line = cursor.blockNumber() + 1
            column = cursor.columnNumber() + 1

            self.cursor_info_label.setText(f"行: {line}, 列: {column}")

        except Exception as e:
            logger.error(f"更新光标信息失败: {e}")

    def update_statistics(self):
        """更新统计信息"""
        try:
            current_editor = self.get_current_editor()
            content = current_editor.toPlainText()

            char_count = len(content)
            line_count = content.count('\n') + 1 if content else 0

            self.stats_label.setText(f"字符: {char_count}, 行: {line_count}")

        except Exception as e:
            logger.error(f"更新统计信息失败: {e}")

    def get_content(self) -> str:
        """获取完整内容"""
        return self.full_editor.toPlainText()

    def clear_content(self):
        """清空内容"""
        try:
            self.html_editor.clear()
            self.css_editor.clear()
            self.js_editor.clear()
            self.full_editor.clear()
            self.structure_tree.clear()

            self.update_statistics()

        except Exception as e:
            logger.error(f"清空内容失败: {e}")
