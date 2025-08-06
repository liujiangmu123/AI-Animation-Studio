"""
AI Animation Studio - 项目打包器
提供项目打包、导出、格式转换等功能
"""

import json
import zipfile
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import xml.etree.ElementTree as ET

from core.logger import get_logger
from core.data_structures import Project

logger = get_logger("project_packager")


class ProjectPackager:
    """项目打包器"""
    
    def __init__(self):
        self.supported_formats = {
            'aas': 'AI Animation Studio项目',
            'json': 'JSON格式',
            'zip': '压缩包',
            'xml': 'XML格式',
            'html': 'HTML包',
            'exe': '可执行文件'
        }
    
    def package_project(self, project: Project, output_path: Path, 
                       format_type: str = 'zip', options: Dict = None) -> bool:
        """打包项目"""
        try:
            options = options or {}
            
            if format_type == 'aas':
                return self._package_as_aas(project, output_path, options)
            elif format_type == 'json':
                return self._package_as_json(project, output_path, options)
            elif format_type == 'zip':
                return self._package_as_zip(project, output_path, options)
            elif format_type == 'xml':
                return self._package_as_xml(project, output_path, options)
            elif format_type == 'html':
                return self._package_as_html(project, output_path, options)
            elif format_type == 'exe':
                return self._package_as_executable(project, output_path, options)
            else:
                logger.error(f"不支持的格式: {format_type}")
                return False
                
        except Exception as e:
            logger.error(f"打包项目失败: {e}")
            return False
    
    def _package_as_aas(self, project: Project, output_path: Path, options: Dict) -> bool:
        """打包为AAS格式"""
        try:
            # 使用项目管理器的标准保存方法
            from core.project_manager import ProjectManager
            pm = ProjectManager()
            pm.current_project = project
            
            return pm.save_project(
                output_path,
                create_backup=options.get('create_backup', False),
                incremental=options.get('incremental', False)
            )
            
        except Exception as e:
            logger.error(f"打包AAS格式失败: {e}")
            return False
    
    def _package_as_json(self, project: Project, output_path: Path, options: Dict) -> bool:
        """打包为JSON格式"""
        try:
            # 转换项目为字典
            project_data = self._project_to_dict(project, options)
            
            # 保存为JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"项目已保存为JSON: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"打包JSON格式失败: {e}")
            return False
    
    def _package_as_zip(self, project: Project, output_path: Path, options: Dict) -> bool:
        """打包为ZIP压缩包"""
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 添加项目文件
                project_data = self._project_to_dict(project, options)
                
                # 保存项目数据
                zipf.writestr('project.json', json.dumps(project_data, indent=2, ensure_ascii=False, default=str))
                
                # 添加资源文件
                if options.get('include_assets', True):
                    self._add_assets_to_zip(project, zipf, options)
                
                # 添加元数据
                metadata = self._generate_metadata(project, options)
                zipf.writestr('metadata.json', json.dumps(metadata, indent=2, ensure_ascii=False, default=str))
                
                # 添加README
                if options.get('include_readme', True):
                    readme_content = self._generate_readme(project, options)
                    zipf.writestr('README.md', readme_content)
                
                # 添加许可证
                if options.get('include_license', False):
                    license_content = options.get('license_text', self._get_default_license())
                    zipf.writestr('LICENSE.txt', license_content)
            
            logger.info(f"项目已打包为ZIP: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"打包ZIP格式失败: {e}")
            return False
    
    def _package_as_xml(self, project: Project, output_path: Path, options: Dict) -> bool:
        """打包为XML格式"""
        try:
            # 创建XML根元素
            root = ET.Element('AnimationProject')
            root.set('version', '1.0')
            root.set('created', datetime.now().isoformat())
            
            # 项目信息
            info = ET.SubElement(root, 'ProjectInfo')
            ET.SubElement(info, 'Name').text = project.name
            ET.SubElement(info, 'Description').text = getattr(project, 'description', '')
            ET.SubElement(info, 'Author').text = getattr(project, 'author', '')
            ET.SubElement(info, 'Version').text = getattr(project, 'version', '1.0')
            ET.SubElement(info, 'CreatedAt').text = project.created_at.isoformat() if hasattr(project, 'created_at') else ''
            
            # 元素列表
            elements = ET.SubElement(root, 'Elements')
            if hasattr(project, 'elements'):
                for element in project.elements.values():
                    elem_xml = ET.SubElement(elements, 'Element')
                    elem_xml.set('id', element.element_id)
                    elem_xml.set('type', element.element_type.value)
                    
                    ET.SubElement(elem_xml, 'Name').text = element.name
                    ET.SubElement(elem_xml, 'Content').text = getattr(element, 'content', '')
                    
                    # 位置信息
                    pos = ET.SubElement(elem_xml, 'Position')
                    pos.set('x', str(element.position.x))
                    pos.set('y', str(element.position.y))
                    
                    # 样式信息
                    if hasattr(element, 'style') and element.style:
                        style = ET.SubElement(elem_xml, 'Style')
                        # 添加样式属性
                        for attr, value in vars(element.style).items():
                            style.set(attr, str(value))
            
            # 时间轴信息
            timeline = ET.SubElement(root, 'Timeline')
            if hasattr(project, 'time_segments'):
                for segment in project.time_segments:
                    seg_xml = ET.SubElement(timeline, 'Segment')
                    seg_xml.set('id', segment.segment_id)
                    seg_xml.set('start', str(segment.start_time))
                    seg_xml.set('end', str(segment.end_time))
                    
                    if hasattr(segment, 'animation_solution') and segment.animation_solution:
                        solution = ET.SubElement(seg_xml, 'AnimationSolution')
                        solution.text = segment.animation_solution.html_code
            
            # 保存XML
            tree = ET.ElementTree(root)
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            
            logger.info(f"项目已保存为XML: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"打包XML格式失败: {e}")
            return False
    
    def _package_as_html(self, project: Project, output_path: Path, options: Dict) -> bool:
        """打包为HTML包"""
        try:
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 生成HTML文件
                html_content = self._generate_html_package(project, options)
                html_file = temp_path / 'index.html'
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # 复制资源文件
                assets_dir = temp_path / 'assets'
                assets_dir.mkdir(exist_ok=True)
                
                if options.get('include_assets', True):
                    self._copy_assets_for_html(project, assets_dir, options)
                
                # 添加CSS和JS文件
                self._add_web_resources(temp_path, options)
                
                # 创建ZIP包
                shutil.make_archive(str(output_path.with_suffix('')), 'zip', temp_dir)
                
                # 重命名为正确的扩展名
                if output_path.suffix != '.zip':
                    zip_file = output_path.with_suffix('.zip')
                    if zip_file.exists():
                        zip_file.rename(output_path)
            
            logger.info(f"项目已打包为HTML: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"打包HTML格式失败: {e}")
            return False
    
    def _package_as_executable(self, project: Project, output_path: Path, options: Dict) -> bool:
        """打包为可执行文件"""
        try:
            # 这是一个复杂的功能，需要使用PyInstaller或类似工具
            # 这里提供基础框架
            
            logger.warning("可执行文件打包功能尚未完全实现")
            
            # 创建一个简单的启动脚本
            launcher_script = self._generate_launcher_script(project, options)
            
            script_file = output_path.with_suffix('.py')
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(launcher_script)
            
            logger.info(f"启动脚本已生成: {script_file}")
            return True
            
        except Exception as e:
            logger.error(f"打包可执行文件失败: {e}")
            return False
    
    def _project_to_dict(self, project: Project, options: Dict) -> Dict:
        """将项目转换为字典"""
        try:
            data = {
                'project_info': {
                    'name': project.name,
                    'description': getattr(project, 'description', ''),
                    'author': getattr(project, 'author', ''),
                    'version': getattr(project, 'version', '1.0'),
                    'created_at': project.created_at.isoformat() if hasattr(project, 'created_at') else '',
                    'modified_at': project.modified_at.isoformat() if hasattr(project, 'modified_at') else '',
                    'duration': getattr(project, 'duration', getattr(project, 'total_duration', 0))
                },
                'elements': {},
                'time_segments': [],
                'settings': getattr(project, 'settings', {}),
                'metadata': {
                    'export_time': datetime.now().isoformat(),
                    'export_options': options,
                    'format_version': '1.0'
                }
            }
            
            # 添加元素
            if hasattr(project, 'elements'):
                for element_id, element in project.elements.items():
                    data['elements'][element_id] = {
                        'element_id': element.element_id,
                        'name': element.name,
                        'element_type': element.element_type.value,
                        'content': getattr(element, 'content', ''),
                        'position': {
                            'x': element.position.x,
                            'y': element.position.y
                        },
                        'visible': element.visible,
                        'locked': element.locked,
                        'z_index': getattr(element, 'z_index', 0),
                        'style': vars(element.style) if hasattr(element, 'style') and element.style else {},
                        'transform': vars(element.transform) if hasattr(element, 'transform') and element.transform else {}
                    }
            
            # 添加时间段
            if hasattr(project, 'time_segments'):
                for segment in project.time_segments:
                    segment_data = {
                        'segment_id': segment.segment_id,
                        'start_time': segment.start_time,
                        'end_time': segment.end_time,
                        'description': getattr(segment, 'description', ''),
                        'animation_solution': None
                    }
                    
                    if hasattr(segment, 'animation_solution') and segment.animation_solution:
                        segment_data['animation_solution'] = {
                            'name': segment.animation_solution.name,
                            'html_code': segment.animation_solution.html_code,
                            'css_code': getattr(segment.animation_solution, 'css_code', ''),
                            'js_code': getattr(segment.animation_solution, 'js_code', ''),
                            'description': getattr(segment.animation_solution, 'description', '')
                        }
                    
                    data['time_segments'].append(segment_data)
            
            return data
            
        except Exception as e:
            logger.error(f"项目转换为字典失败: {e}")
            return {}
    
    def _add_assets_to_zip(self, project: Project, zipf: zipfile.ZipFile, options: Dict):
        """添加资源文件到ZIP"""
        try:
            # 这里需要根据项目中的资源文件路径来添加
            # 简化实现，实际需要扫描项目中引用的所有资源
            assets_dir = Path("assets")  # 假设的资源目录
            
            if assets_dir.exists():
                for asset_file in assets_dir.rglob("*"):
                    if asset_file.is_file():
                        arcname = f"assets/{asset_file.relative_to(assets_dir)}"
                        zipf.write(asset_file, arcname)
                        
        except Exception as e:
            logger.warning(f"添加资源文件失败: {e}")
    
    def _generate_metadata(self, project: Project, options: Dict) -> Dict:
        """生成元数据"""
        return {
            'project_name': project.name,
            'export_time': datetime.now().isoformat(),
            'export_options': options,
            'file_format': 'AI Animation Studio Package',
            'version': '1.0',
            'elements_count': len(getattr(project, 'elements', {})),
            'segments_count': len(getattr(project, 'time_segments', [])),
            'duration': getattr(project, 'duration', getattr(project, 'total_duration', 0))
        }
    
    def _generate_readme(self, project: Project, options: Dict) -> str:
        """生成README文件"""
        return f"""# {project.name}

## 项目信息
- 名称: {project.name}
- 描述: {getattr(project, 'description', '无描述')}
- 作者: {getattr(project, 'author', '未知')}
- 版本: {getattr(project, 'version', '1.0')}
- 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 项目统计
- 元素数量: {len(getattr(project, 'elements', {}))}
- 时间段数量: {len(getattr(project, 'time_segments', []))}
- 总时长: {getattr(project, 'total_duration', 0)} 秒

## 文件说明
- project.json: 项目数据文件
- metadata.json: 项目元数据
- assets/: 资源文件目录
- README.md: 本说明文件

## 使用方法
使用 AI Animation Studio 打开 project.json 文件即可导入此项目。

---
由 AI Animation Studio 生成
"""
    
    def _get_default_license(self) -> str:
        """获取默认许可证"""
        return """MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    def _generate_html_package(self, project: Project, options: Dict) -> str:
        """生成HTML包"""
        # 简化的HTML生成，实际需要更复杂的逻辑
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project.name}</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <div id="animation-container">
        <h1>{project.name}</h1>
        <p>{getattr(project, 'description', '')}</p>
        <!-- 动画内容将在这里生成 -->
    </div>
    <script src="assets/animation.js"></script>
</body>
</html>"""
    
    def _copy_assets_for_html(self, project: Project, assets_dir: Path, options: Dict):
        """为HTML包复制资源"""
        # 实现资源文件复制逻辑
        pass
    
    def _add_web_resources(self, temp_path: Path, options: Dict):
        """添加Web资源"""
        # 添加CSS和JS文件
        assets_dir = temp_path / 'assets'
        
        # 创建基础CSS
        css_content = """
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background: #f0f0f0;
}

#animation-container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
"""
        
        with open(assets_dir / 'style.css', 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        # 创建基础JS
        js_content = """
// AI Animation Studio 生成的动画脚本
console.log('Animation loaded');

// 动画初始化代码将在这里添加
"""
        
        with open(assets_dir / 'animation.js', 'w', encoding='utf-8') as f:
            f.write(js_content)
    
    def _generate_launcher_script(self, project: Project, options: Dict) -> str:
        """生成启动脚本"""
        return f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
{project.name} - 启动脚本
由 AI Animation Studio 生成
\"\"\"

import sys
import json
from pathlib import Path

def main():
    print("启动 {project.name}")
    print("项目描述: {getattr(project, 'description', '无描述')}")
    
    # 这里可以添加项目运行逻辑
    
if __name__ == "__main__":
    main()
"""
