"""
AI Animation Studio - 方案导入导出工具
支持多种格式的方案导入导出，包括JSON、ZIP包、代码片段等
"""

import os
import json
import zipfile
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from core.enhanced_solution_manager import EnhancedAnimationSolution, SolutionCategory, SolutionQuality
from core.data_structures import TechStack
from core.logger import get_logger

logger = get_logger("solution_import_export")


class SolutionExporter:
    """方案导出器"""
    
    def __init__(self):
        self.supported_formats = ["json", "zip", "html", "codepen"]
    
    def export_solution(self, solution: EnhancedAnimationSolution, 
                       export_path: str, format_type: str = "json") -> bool:
        """导出单个方案"""
        try:
            if format_type not in self.supported_formats:
                logger.error(f"不支持的导出格式: {format_type}")
                return False
            
            if format_type == "json":
                return self.export_to_json(solution, export_path)
            elif format_type == "zip":
                return self.export_to_zip([solution], export_path)
            elif format_type == "html":
                return self.export_to_html(solution, export_path)
            elif format_type == "codepen":
                return self.export_to_codepen_format(solution, export_path)
            
            return False
            
        except Exception as e:
            logger.error(f"导出方案失败: {e}")
            return False
    
    def export_solutions_batch(self, solutions: List[EnhancedAnimationSolution],
                              export_path: str, format_type: str = "zip") -> bool:
        """批量导出方案"""
        try:
            if format_type == "zip":
                return self.export_to_zip(solutions, export_path)
            elif format_type == "json":
                return self.export_batch_to_json(solutions, export_path)
            else:
                logger.error(f"批量导出不支持格式: {format_type}")
                return False
            
        except Exception as e:
            logger.error(f"批量导出方案失败: {e}")
            return False
    
    def export_to_json(self, solution: EnhancedAnimationSolution, file_path: str) -> bool:
        """导出为JSON格式"""
        try:
            # 转换为字典
            solution_dict = self.solution_to_dict(solution)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(solution_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"方案已导出为JSON: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出JSON失败: {e}")
            return False
    
    def export_batch_to_json(self, solutions: List[EnhancedAnimationSolution], file_path: str) -> bool:
        """批量导出为JSON格式"""
        try:
            solutions_data = {
                "export_info": {
                    "export_time": datetime.now().isoformat(),
                    "solutions_count": len(solutions),
                    "exporter_version": "1.0.0"
                },
                "solutions": [self.solution_to_dict(solution) for solution in solutions]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(solutions_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"批量导出 {len(solutions)} 个方案为JSON: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"批量导出JSON失败: {e}")
            return False
    
    def export_to_zip(self, solutions: List[EnhancedAnimationSolution], zip_path: str) -> bool:
        """导出为ZIP包"""
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 添加方案信息文件
                solutions_info = {
                    "export_info": {
                        "export_time": datetime.now().isoformat(),
                        "solutions_count": len(solutions)
                    },
                    "solutions": []
                }
                
                for i, solution in enumerate(solutions):
                    solution_folder = f"solution_{i+1}_{solution.solution_id[:8]}"
                    
                    # 添加HTML文件
                    if solution.html_code:
                        html_path = f"{solution_folder}/index.html"
                        zipf.writestr(html_path, solution.html_code)
                    
                    # 添加CSS文件
                    if solution.css_code:
                        css_path = f"{solution_folder}/style.css"
                        zipf.writestr(css_path, solution.css_code)
                    
                    # 添加JavaScript文件
                    if solution.js_code:
                        js_path = f"{solution_folder}/script.js"
                        zipf.writestr(js_path, solution.js_code)
                    
                    # 添加完整HTML文件
                    full_html = self.generate_complete_html(solution)
                    complete_path = f"{solution_folder}/complete.html"
                    zipf.writestr(complete_path, full_html)
                    
                    # 添加方案信息
                    solution_info = self.solution_to_dict(solution)
                    info_path = f"{solution_folder}/info.json"
                    zipf.writestr(info_path, json.dumps(solution_info, ensure_ascii=False, indent=2))
                    
                    # 记录到总信息中
                    solutions_info["solutions"].append({
                        "name": solution.name,
                        "id": solution.solution_id,
                        "folder": solution_folder
                    })
                
                # 添加总信息文件
                zipf.writestr("solutions_info.json", json.dumps(solutions_info, ensure_ascii=False, indent=2))
                
                # 添加README文件
                readme_content = self.generate_readme(solutions)
                zipf.writestr("README.md", readme_content)
            
            logger.info(f"方案已导出为ZIP包: {zip_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出ZIP包失败: {e}")
            return False
    
    def export_to_html(self, solution: EnhancedAnimationSolution, file_path: str) -> bool:
        """导出为完整HTML文件"""
        try:
            html_content = self.generate_complete_html(solution)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"方案已导出为HTML: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出HTML失败: {e}")
            return False
    
    def export_to_codepen_format(self, solution: EnhancedAnimationSolution, file_path: str) -> bool:
        """导出为CodePen格式"""
        try:
            codepen_data = {
                "title": solution.name,
                "description": solution.description,
                "html": solution.html_code,
                "css": solution.css_code,
                "js": solution.js_code,
                "css_external": "",
                "js_external": "",
                "css_pre_processor": "none",
                "js_pre_processor": "none"
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(codepen_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"方案已导出为CodePen格式: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出CodePen格式失败: {e}")
            return False
    
    def solution_to_dict(self, solution: EnhancedAnimationSolution) -> Dict[str, Any]:
        """将方案转换为字典"""
        from dataclasses import asdict
        
        solution_dict = asdict(solution)
        
        # 处理特殊类型
        solution_dict["created_at"] = solution.created_at.isoformat()
        solution_dict["updated_at"] = solution.updated_at.isoformat()
        solution_dict["category"] = solution.category.value
        solution_dict["quality_level"] = solution.quality_level.value
        solution_dict["tech_stack"] = solution.tech_stack.value
        
        return solution_dict
    
    def generate_complete_html(self, solution: EnhancedAnimationSolution) -> str:
        """生成完整的HTML文件"""
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{solution.name}</title>
    <style>
{solution.css_code}
    </style>
</head>
<body>
    <!-- {solution.description} -->
    {solution.html_code}
    
    <script>
{solution.js_code}
    </script>
</body>
</html>"""
        
        return html_template
    
    def generate_readme(self, solutions: List[EnhancedAnimationSolution]) -> str:
        """生成README文件"""
        readme_lines = [
            "# AI Animation Studio - 导出方案",
            "",
            f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"方案数量: {len(solutions)}",
            "",
            "## 方案列表",
            ""
        ]
        
        for i, solution in enumerate(solutions, 1):
            readme_lines.extend([
                f"### {i}. {solution.name}",
                f"- **技术栈**: {solution.tech_stack.value}",
                f"- **分类**: {solution.category.value}",
                f"- **质量评分**: {solution.metrics.overall_score:.1f}",
                f"- **用户评分**: {solution.user_rating:.1f}⭐",
                f"- **描述**: {solution.description}",
                ""
            ])
        
        readme_lines.extend([
            "## 使用说明",
            "",
            "1. 每个方案都包含在独立的文件夹中",
            "2. `complete.html` 是可直接运行的完整文件",
            "3. `index.html`, `style.css`, `script.js` 是分离的代码文件",
            "4. `info.json` 包含方案的详细信息",
            "",
            "## 技术支持",
            "",
            "如有问题，请联系 AI Animation Studio 技术支持。"
        ])
        
        return "\n".join(readme_lines)


class SolutionImporter:
    """方案导入器"""
    
    def __init__(self):
        self.supported_formats = ["json", "zip", "html", "codepen"]
    
    def import_solution(self, import_path: str, format_type: str = None) -> List[EnhancedAnimationSolution]:
        """导入方案"""
        try:
            # 自动检测格式
            if format_type is None:
                format_type = self.detect_format(import_path)
            
            if format_type not in self.supported_formats:
                logger.error(f"不支持的导入格式: {format_type}")
                return []
            
            if format_type == "json":
                return self.import_from_json(import_path)
            elif format_type == "zip":
                return self.import_from_zip(import_path)
            elif format_type == "html":
                return self.import_from_html(import_path)
            elif format_type == "codepen":
                return self.import_from_codepen(import_path)
            
            return []
            
        except Exception as e:
            logger.error(f"导入方案失败: {e}")
            return []
    
    def detect_format(self, file_path: str) -> str:
        """检测文件格式"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == ".json":
            return "json"
        elif file_ext == ".zip":
            return "zip"
        elif file_ext in [".html", ".htm"]:
            return "html"
        else:
            return "json"  # 默认格式
    
    def import_from_json(self, file_path: str) -> List[EnhancedAnimationSolution]:
        """从JSON文件导入"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            solutions = []
            
            # 检查是否是批量导出格式
            if "solutions" in data and isinstance(data["solutions"], list):
                # 批量格式
                for solution_data in data["solutions"]:
                    solution = self.dict_to_solution(solution_data)
                    if solution:
                        solutions.append(solution)
            else:
                # 单个方案格式
                solution = self.dict_to_solution(data)
                if solution:
                    solutions.append(solution)
            
            logger.info(f"从JSON导入 {len(solutions)} 个方案")
            return solutions
            
        except Exception as e:
            logger.error(f"从JSON导入失败: {e}")
            return []
    
    def import_from_zip(self, zip_path: str) -> List[EnhancedAnimationSolution]:
        """从ZIP包导入"""
        try:
            solutions = []
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # 查找方案信息文件
                info_files = [name for name in zipf.namelist() if name.endswith('info.json')]
                
                for info_file in info_files:
                    try:
                        # 读取方案信息
                        with zipf.open(info_file) as f:
                            solution_data = json.load(f)
                        
                        solution = self.dict_to_solution(solution_data)
                        if solution:
                            solutions.append(solution)
                            
                    except Exception as e:
                        logger.warning(f"导入方案信息失败 {info_file}: {e}")
                
                # 如果没有找到info.json，尝试解析HTML文件
                if not solutions:
                    html_files = [name for name in zipf.namelist() if name.endswith('.html')]
                    
                    for html_file in html_files:
                        try:
                            with zipf.open(html_file) as f:
                                html_content = f.read().decode('utf-8')
                            
                            solution = self.parse_html_content(html_content, html_file)
                            if solution:
                                solutions.append(solution)
                                
                        except Exception as e:
                            logger.warning(f"解析HTML文件失败 {html_file}: {e}")
            
            logger.info(f"从ZIP包导入 {len(solutions)} 个方案")
            return solutions
            
        except Exception as e:
            logger.error(f"从ZIP包导入失败: {e}")
            return []
    
    def import_from_html(self, file_path: str) -> List[EnhancedAnimationSolution]:
        """从HTML文件导入"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            solution = self.parse_html_content(html_content, file_path)
            
            if solution:
                logger.info(f"从HTML导入方案: {solution.name}")
                return [solution]
            else:
                return []
            
        except Exception as e:
            logger.error(f"从HTML导入失败: {e}")
            return []
    
    def import_from_codepen(self, file_path: str) -> List[EnhancedAnimationSolution]:
        """从CodePen格式导入"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                codepen_data = json.load(f)
            
            solution = EnhancedAnimationSolution()
            solution.name = codepen_data.get("title", "导入的方案")
            solution.description = codepen_data.get("description", "")
            solution.html_code = codepen_data.get("html", "")
            solution.css_code = codepen_data.get("css", "")
            solution.js_code = codepen_data.get("js", "")
            
            # 自动检测技术栈
            solution.tech_stack = self.detect_tech_stack(solution.css_code, solution.js_code)
            
            # 自动检测分类
            solution.category = self.detect_category(solution.html_code, solution.css_code)
            
            logger.info(f"从CodePen格式导入方案: {solution.name}")
            return [solution]
            
        except Exception as e:
            logger.error(f"从CodePen格式导入失败: {e}")
            return []
    
    def dict_to_solution(self, solution_dict: Dict[str, Any]) -> Optional[EnhancedAnimationSolution]:
        """将字典转换为方案对象"""
        try:
            # 处理枚举类型
            if "category" in solution_dict:
                solution_dict["category"] = SolutionCategory(solution_dict["category"])
            
            if "quality_level" in solution_dict:
                solution_dict["quality_level"] = SolutionQuality(solution_dict["quality_level"])
            
            if "tech_stack" in solution_dict:
                solution_dict["tech_stack"] = TechStack(solution_dict["tech_stack"])
            
            # 处理时间类型
            if "created_at" in solution_dict:
                solution_dict["created_at"] = datetime.fromisoformat(solution_dict["created_at"])
            
            if "updated_at" in solution_dict:
                solution_dict["updated_at"] = datetime.fromisoformat(solution_dict["updated_at"])
            
            # 创建方案对象
            solution = EnhancedAnimationSolution(**solution_dict)
            
            return solution
            
        except Exception as e:
            logger.error(f"转换字典为方案对象失败: {e}")
            return None
    
    def parse_html_content(self, html_content: str, file_name: str) -> Optional[EnhancedAnimationSolution]:
        """解析HTML内容"""
        try:
            import re
            
            solution = EnhancedAnimationSolution()
            
            # 提取标题
            title_match = re.search(r"<title>([^<]+)</title>", html_content, re.IGNORECASE)
            if title_match:
                solution.name = title_match.group(1).strip()
            else:
                solution.name = Path(file_name).stem
            
            # 提取CSS
            css_matches = re.findall(r"<style[^>]*>(.*?)</style>", html_content, re.DOTALL | re.IGNORECASE)
            if css_matches:
                solution.css_code = "\n".join(css_matches).strip()
            
            # 提取JavaScript
            js_matches = re.findall(r"<script[^>]*>(.*?)</script>", html_content, re.DOTALL | re.IGNORECASE)
            if js_matches:
                solution.js_code = "\n".join(js_matches).strip()
            
            # 提取HTML主体
            body_match = re.search(r"<body[^>]*>(.*?)</body>", html_content, re.DOTALL | re.IGNORECASE)
            if body_match:
                solution.html_code = body_match.group(1).strip()
            else:
                # 如果没有body标签，使用整个内容
                solution.html_code = html_content
            
            # 自动检测技术栈和分类
            solution.tech_stack = self.detect_tech_stack(solution.css_code, solution.js_code)
            solution.category = self.detect_category(solution.html_code, solution.css_code)
            
            return solution
            
        except Exception as e:
            logger.error(f"解析HTML内容失败: {e}")
            return None
    
    def detect_tech_stack(self, css_code: str, js_code: str) -> TechStack:
        """检测技术栈"""
        try:
            # 检查JavaScript库
            if js_code:
                if "gsap" in js_code.lower() or "TweenMax" in js_code:
                    return TechStack.GSAP
                elif "THREE" in js_code or "three.js" in js_code.lower():
                    return TechStack.THREE_JS
                else:
                    return TechStack.JAVASCRIPT
            
            # 检查SVG动画
            if "svg" in css_code.lower() or "<svg" in css_code.lower():
                return TechStack.SVG_ANIMATION
            
            # 默认CSS动画
            return TechStack.CSS_ANIMATION
            
        except Exception as e:
            logger.error(f"检测技术栈失败: {e}")
            return TechStack.CSS_ANIMATION
    
    def detect_category(self, html_code: str, css_code: str) -> SolutionCategory:
        """检测方案分类"""
        try:
            content = (html_code + css_code).lower()
            
            # 关键词匹配
            if any(keyword in content for keyword in ["fade", "slide", "enter", "appear"]):
                return SolutionCategory.ENTRANCE
            elif any(keyword in content for keyword in ["exit", "leave", "disappear", "hide"]):
                return SolutionCategory.EXIT
            elif any(keyword in content for keyword in ["transition", "change", "switch"]):
                return SolutionCategory.TRANSITION
            elif any(keyword in content for keyword in ["hover", "click", "interact", "button"]):
                return SolutionCategory.INTERACTION
            elif any(keyword in content for keyword in ["particle", "effect", "glow", "shadow"]):
                return SolutionCategory.EFFECT
            else:
                return SolutionCategory.COMPOSITE
            
        except Exception as e:
            logger.error(f"检测方案分类失败: {e}")
            return SolutionCategory.EFFECT


class SolutionImportExportManager:
    """方案导入导出管理器"""
    
    def __init__(self):
        self.exporter = SolutionExporter()
        self.importer = SolutionImporter()
    
    def export_solutions_with_dialog(self, solutions: List[EnhancedAnimationSolution], 
                                   parent_widget=None) -> bool:
        """通过对话框导出方案"""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            
            if not solutions:
                QMessageBox.warning(parent_widget, "警告", "没有可导出的方案")
                return False
            
            # 选择导出格式
            format_options = {
                "JSON文件 (*.json)": "json",
                "ZIP压缩包 (*.zip)": "zip",
                "HTML文件 (*.html)": "html",
                "CodePen格式 (*.json)": "codepen"
            }
            
            file_filter = ";;".join(format_options.keys())
            
            file_path, selected_filter = QFileDialog.getSaveFileName(
                parent_widget, "导出方案", "", file_filter
            )
            
            if file_path:
                format_type = format_options.get(selected_filter, "json")
                
                if len(solutions) == 1:
                    success = self.exporter.export_solution(solutions[0], file_path, format_type)
                else:
                    success = self.exporter.export_solutions_batch(solutions, file_path, format_type)
                
                if success:
                    QMessageBox.information(parent_widget, "成功", f"方案已导出到:\n{file_path}")
                    return True
                else:
                    QMessageBox.warning(parent_widget, "错误", "导出失败")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"导出方案对话框失败: {e}")
            return False
    
    def import_solutions_with_dialog(self, parent_widget=None) -> List[EnhancedAnimationSolution]:
        """通过对话框导入方案"""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            
            file_filter = "所有支持格式 (*.json *.zip *.html *.htm);;JSON文件 (*.json);;ZIP压缩包 (*.zip);;HTML文件 (*.html *.htm)"
            
            file_path, _ = QFileDialog.getOpenFileName(
                parent_widget, "导入方案", "", file_filter
            )
            
            if file_path:
                solutions = self.importer.import_solution(file_path)
                
                if solutions:
                    QMessageBox.information(
                        parent_widget, "成功", 
                        f"成功导入 {len(solutions)} 个方案"
                    )
                    return solutions
                else:
                    QMessageBox.warning(parent_widget, "错误", "导入失败或文件中没有有效方案")
                    return []
            
            return []
            
        except Exception as e:
            logger.error(f"导入方案对话框失败: {e}")
            return []
