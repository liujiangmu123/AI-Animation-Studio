"""
AI Animation Studio - JavaScript库管理器
管理和下载常用的JavaScript动画库
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

from core.logger import get_logger

logger = get_logger("js_library_manager")

class JSLibrary:
    """JavaScript库信息"""
    def __init__(self, name: str, url: str, version: str, description: str, 
                 local_path: str = None, dependencies: List[str] = None):
        self.name = name
        self.url = url
        self.version = version
        self.description = description
        self.local_path = local_path
        self.dependencies = dependencies or []
        self.is_downloaded = False

class JSLibraryManager:
    """JavaScript库管理器"""
    
    def __init__(self, libraries_dir: Path = None):
        if libraries_dir is None:
            libraries_dir = Path(__file__).parent.parent / "assets" / "js_libraries"
        
        self.libraries_dir = libraries_dir
        self.libraries_dir.mkdir(parents=True, exist_ok=True)
        
        # 预定义的常用库
        self.predefined_libraries = {
            "three.js": JSLibrary(
                name="Three.js",
                url="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js",
                version="r128",
                description="3D图形库",
                local_path="three.min.js"
            ),
            "gsap": JSLibrary(
                name="GSAP",
                url="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js",
                version="3.12.2",
                description="高性能动画库",
                local_path="gsap.min.js"
            ),
            "anime.js": JSLibrary(
                name="Anime.js",
                url="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.1/anime.min.js",
                version="3.2.1",
                description="轻量级动画库",
                local_path="anime.min.js"
            ),
            "p5.js": JSLibrary(
                name="p5.js",
                url="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.min.js",
                version="1.4.0",
                description="创意编程库",
                local_path="p5.min.js"
            ),
            "d3.js": JSLibrary(
                name="D3.js",
                url="https://cdnjs.cloudflare.com/ajax/libs/d3/7.6.1/d3.min.js",
                version="7.6.1",
                description="数据可视化库",
                local_path="d3.min.js"
            ),
            "lottie": JSLibrary(
                name="Lottie",
                url="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.9.6/lottie.min.js",
                version="5.9.6",
                description="After Effects动画播放器",
                local_path="lottie.min.js"
            )
        }
        
        self._check_downloaded_libraries()
    
    def _check_downloaded_libraries(self):
        """检查已下载的库"""
        for lib_id, library in self.predefined_libraries.items():
            if library.local_path:
                local_file = self.libraries_dir / library.local_path
                library.is_downloaded = local_file.exists()
    
    def get_available_libraries(self) -> Dict[str, JSLibrary]:
        """获取可用的库列表"""
        return self.predefined_libraries.copy()
    
    def download_library(self, lib_id: str) -> Dict[str, Any]:
        """下载指定的库

        Returns:
            Dict包含: success (bool), message (str), error_type (str, optional)
        """
        if lib_id not in self.predefined_libraries:
            error_msg = f"未知的库: {lib_id}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "error_type": "LIBRARY_NOT_FOUND"
            }

        library = self.predefined_libraries[lib_id]

        if library.is_downloaded:
            msg = f"{library.name} 已经下载"
            logger.info(msg)
            return {
                "success": True,
                "message": msg,
                "already_downloaded": True
            }

        try:
            logger.info(f"开始下载 {library.name} from {library.url}")

            # 检查网络连接
            try:
                response = requests.get(library.url, timeout=30)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                error_msg = f"下载 {library.name} 超时，请检查网络连接"
                logger.error(error_msg)
                return {
                    "success": False,
                    "message": error_msg,
                    "error_type": "NETWORK_TIMEOUT"
                }
            except requests.exceptions.ConnectionError:
                error_msg = f"无法连接到 {library.url}，请检查网络连接"
                logger.error(error_msg)
                return {
                    "success": False,
                    "message": error_msg,
                    "error_type": "NETWORK_ERROR"
                }
            except requests.exceptions.HTTPError as e:
                error_msg = f"下载 {library.name} 失败: HTTP {e.response.status_code}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "message": error_msg,
                    "error_type": "HTTP_ERROR",
                    "status_code": e.response.status_code
                }

            # 确保目录存在
            local_file = self.libraries_dir / library.local_path
            local_file.parent.mkdir(parents=True, exist_ok=True)

            # 保存到本地
            try:
                with open(local_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
            except IOError as e:
                error_msg = f"保存 {library.name} 到本地失败: {e}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "message": error_msg,
                    "error_type": "FILE_WRITE_ERROR"
                }

            # 验证文件
            if not local_file.exists() or local_file.stat().st_size == 0:
                error_msg = f"下载的 {library.name} 文件无效"
                logger.error(error_msg)
                return {
                    "success": False,
                    "message": error_msg,
                    "error_type": "FILE_INVALID"
                }

            library.is_downloaded = True
            success_msg = f"{library.name} 下载成功: {local_file}"
            logger.info(success_msg)
            return {
                "success": True,
                "message": success_msg,
                "local_path": str(local_file),
                "file_size": local_file.stat().st_size
            }

        except Exception as e:
            error_msg = f"下载 {library.name} 时发生未知错误: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "error_type": "UNKNOWN_ERROR",
                "exception": str(e)
            }
    
    def download_all_libraries(self) -> Dict[str, Dict[str, Any]]:
        """下载所有库

        Returns:
            Dict[lib_id, download_result] 每个库的下载结果
        """
        results = {}
        total_libs = len(self.predefined_libraries)
        logger.info(f"开始下载 {total_libs} 个库")

        for i, lib_id in enumerate(self.predefined_libraries, 1):
            logger.info(f"正在下载第 {i}/{total_libs} 个库: {lib_id}")
            results[lib_id] = self.download_library(lib_id)

        # 统计结果
        successful = sum(1 for result in results.values() if result["success"])
        failed = total_libs - successful

        logger.info(f"库下载完成: 成功 {successful}/{total_libs}, 失败 {failed}")

        return results
    
    def get_local_url(self, lib_id: str) -> Optional[str]:
        """获取本地库的URL"""
        try:
            if lib_id not in self.predefined_libraries:
                logger.warning(f"请求未知库的本地URL: {lib_id}")
                return None

            library = self.predefined_libraries[lib_id]
            if not library.is_downloaded:
                logger.debug(f"库 {lib_id} 尚未下载")
                return None

            local_file = self.libraries_dir / library.local_path

            # 验证文件是否存在
            if not local_file.exists():
                logger.error(f"库文件不存在: {local_file}")
                library.is_downloaded = False  # 更新状态
                return None

            return f"file:///{local_file.absolute()}"

        except Exception as e:
            logger.error(f"获取库 {lib_id} 本地URL时发生错误: {e}")
            return None
    
    def get_cdn_url(self, lib_id: str) -> Optional[str]:
        """获取CDN库的URL"""
        if lib_id not in self.predefined_libraries:
            return None
        
        return self.predefined_libraries[lib_id].url
    
    def get_library_script_tag(self, lib_id: str, prefer_local: bool = True) -> Optional[str]:
        """获取库的script标签"""
        if lib_id not in self.predefined_libraries:
            return None
        
        library = self.predefined_libraries[lib_id]
        
        if prefer_local and library.is_downloaded:
            local_file = self.libraries_dir / library.local_path
            return f'<script src="file:///{local_file.absolute()}"></script>'
        else:
            return f'<script src="{library.url}"></script>'
    
    def inject_libraries_to_html(self, html_content: str, required_libs: List[str],
                                prefer_local: bool = True) -> Dict[str, Any]:
        """向HTML中注入所需的库

        Returns:
            Dict包含: success (bool), html (str), message (str), injected_libs (List[str])
        """
        try:
            if not html_content:
                return {
                    "success": False,
                    "html": "",
                    "message": "HTML内容为空",
                    "injected_libs": []
                }

            if not required_libs:
                return {
                    "success": True,
                    "html": html_content,
                    "message": "无需注入库",
                    "injected_libs": []
                }

            # 生成script标签
            script_tags = []
            injected_libs = []
            failed_libs = []

            for lib_id in required_libs:
                try:
                    tag = self.get_library_script_tag(lib_id, prefer_local)
                    if tag:
                        script_tags.append(tag)
                        injected_libs.append(lib_id)
                    else:
                        failed_libs.append(lib_id)
                        logger.warning(f"无法为库 {lib_id} 生成script标签")
                except Exception as e:
                    failed_libs.append(lib_id)
                    logger.error(f"处理库 {lib_id} 时发生错误: {e}")

            if not script_tags:
                return {
                    "success": False,
                    "html": html_content,
                    "message": f"所有库都无法注入: {failed_libs}",
                    "injected_libs": [],
                    "failed_libs": failed_libs
                }

            # 查找插入位置
            head_end = html_content.find('</head>')
            if head_end != -1:
                # 插入到</head>之前
                scripts_html = '\n    ' + '\n    '.join(script_tags) + '\n'
                modified_html = html_content[:head_end] + scripts_html + html_content[head_end:]
            else:
                # 如果没有head标签，插入到开头
                scripts_html = '\n'.join(script_tags) + '\n'
                modified_html = scripts_html + html_content
                logger.warning("HTML中未找到</head>标签，将script标签插入到开头")

            message = f"成功注入 {len(injected_libs)} 个库"
            if failed_libs:
                message += f"，{len(failed_libs)} 个库注入失败"

            logger.info(message + f": {injected_libs}")

            return {
                "success": True,
                "html": modified_html,
                "message": message,
                "injected_libs": injected_libs,
                "failed_libs": failed_libs
            }

        except Exception as e:
            error_msg = f"注入库到HTML时发生错误: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "html": html_content,
                "message": error_msg,
                "injected_libs": [],
                "exception": str(e)
            }
    
    def detect_required_libraries(self, html_content: str) -> Dict[str, Any]:
        """检测HTML内容中需要的库

        Returns:
            Dict包含: success (bool), libraries (List[str]), message (str), details (Dict)
        """
        try:
            if not html_content:
                return {
                    "success": False,
                    "libraries": [],
                    "message": "HTML内容为空",
                    "details": {}
                }

            required_libs = []
            detection_details = {}
            content_lower = html_content.lower()

            # 检测模式
            patterns = {
                "three.js": ["three.", "new three", "three.scene", "three.webglrenderer"],
                "gsap": ["gsap.", "tweenmax", "timelinemax", "gsap.to", "gsap.from"],
                "anime.js": ["anime(", "anime.js", "anime({"],
                "p5.js": ["createcanvas", "setup()", "draw()", "p5."],
                "d3.js": ["d3.", "d3.select", "d3.data"],
                "lottie": ["lottie.", "bodymovin", "lottie.loadanimation"]
            }

            for lib_id, keywords in patterns.items():
                try:
                    found_keywords = []
                    for keyword in keywords:
                        if keyword in content_lower:
                            found_keywords.append(keyword)

                    if found_keywords:
                        required_libs.append(lib_id)
                        detection_details[lib_id] = {
                            "found_keywords": found_keywords,
                            "confidence": len(found_keywords) / len(keywords)
                        }
                        logger.debug(f"检测到库 {lib_id}: {found_keywords}")

                except Exception as e:
                    logger.error(f"检测库 {lib_id} 时发生错误: {e}")
                    continue

            message = f"检测到 {len(required_libs)} 个所需库" if required_libs else "未检测到所需库"
            logger.info(f"{message}: {required_libs}")

            return {
                "success": True,
                "libraries": required_libs,
                "message": message,
                "details": detection_details,
                "content_length": len(html_content)
            }

        except Exception as e:
            error_msg = f"检测所需库时发生错误: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "libraries": [],
                "message": error_msg,
                "details": {},
                "exception": str(e)
            }
    
    def validate_library_integrity(self, lib_id: str) -> Dict[str, Any]:
        """验证库的完整性

        Returns:
            Dict包含: valid (bool), message (str), details (Dict)
        """
        try:
            if lib_id not in self.predefined_libraries:
                return {
                    "valid": False,
                    "message": f"未知的库: {lib_id}",
                    "details": {}
                }

            library = self.predefined_libraries[lib_id]

            if not library.is_downloaded:
                return {
                    "valid": False,
                    "message": f"库 {library.name} 尚未下载",
                    "details": {"downloaded": False}
                }

            local_file = self.libraries_dir / library.local_path

            # 检查文件是否存在
            if not local_file.exists():
                library.is_downloaded = False  # 更新状态
                return {
                    "valid": False,
                    "message": f"库文件不存在: {local_file}",
                    "details": {"file_exists": False}
                }

            # 检查文件大小
            file_size = local_file.stat().st_size
            if file_size == 0:
                return {
                    "valid": False,
                    "message": f"库文件为空: {local_file}",
                    "details": {"file_size": 0}
                }

            # 检查文件内容（基本验证）
            try:
                with open(local_file, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # 读取前1000字符

                # 基本的JavaScript库验证
                if not any(keyword in content.lower() for keyword in ['function', 'var ', 'const ', 'let ', '{']):
                    return {
                        "valid": False,
                        "message": f"库文件内容可能无效: {local_file}",
                        "details": {"content_valid": False, "file_size": file_size}
                    }

            except UnicodeDecodeError:
                return {
                    "valid": False,
                    "message": f"库文件编码错误: {local_file}",
                    "details": {"encoding_error": True, "file_size": file_size}
                }

            return {
                "valid": True,
                "message": f"库 {library.name} 验证通过",
                "details": {
                    "file_size": file_size,
                    "file_path": str(local_file),
                    "content_preview": content[:100] + "..." if len(content) > 100 else content
                }
            }

        except Exception as e:
            error_msg = f"验证库 {lib_id} 时发生错误: {e}"
            logger.error(error_msg)
            return {
                "valid": False,
                "message": error_msg,
                "details": {"exception": str(e)}
            }

    def get_library_status(self) -> Dict[str, Dict]:
        """获取所有库的状态"""
        try:
            status = {}
            for lib_id, library in self.predefined_libraries.items():
                try:
                    # 验证库的完整性
                    validation = self.validate_library_integrity(lib_id)

                    status[lib_id] = {
                        "name": library.name,
                        "version": library.version,
                        "description": library.description,
                        "is_downloaded": library.is_downloaded,
                        "url": library.url,
                        "local_path": str(self.libraries_dir / library.local_path) if library.local_path else None,
                        "is_valid": validation["valid"],
                        "validation_message": validation["message"],
                        "validation_details": validation["details"]
                    }
                except Exception as e:
                    logger.error(f"获取库 {lib_id} 状态时发生错误: {e}")
                    status[lib_id] = {
                        "name": library.name,
                        "version": library.version,
                        "description": library.description,
                        "is_downloaded": False,
                        "url": library.url,
                        "local_path": None,
                        "is_valid": False,
                        "validation_message": f"状态检查失败: {e}",
                        "validation_details": {"exception": str(e)}
                    }

            return status

        except Exception as e:
            logger.error(f"获取库状态时发生错误: {e}")
            return {}
