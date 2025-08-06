"""
AI Animation Studio - 视频导出器
使用Puppeteer或类似技术将HTML动画导出为视频
"""

import os
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtCore import QThread, pyqtSignal

from core.logger import get_logger

logger = get_logger("video_exporter")

class VideoExportThread(QThread):
    """视频导出线程"""
    
    progress_update = pyqtSignal(str)  # 进度更新信号
    export_complete = pyqtSignal(bool, str)  # 导出完成信号 (成功, 消息)
    
    def __init__(self, html_content: str, output_path: str, 
                 duration: float = 10.0, fps: int = 30, 
                 width: int = 1920, height: int = 1080):
        super().__init__()
        self.html_content = html_content
        self.output_path = output_path
        self.duration = duration
        self.fps = fps
        self.width = width
        self.height = height
    
    def run(self):
        """执行视频导出"""
        try:
            self.progress_update.emit("准备导出环境...")
            
            # 创建临时HTML文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(self.html_content)
                html_file = f.name
            
            try:
                # 尝试使用不同的导出方法
                success = False
                
                # 方法1: 使用Puppeteer (如果可用)
                if self.check_puppeteer():
                    self.progress_update.emit("使用Puppeteer导出...")
                    success = self.export_with_puppeteer(html_file)
                
                # 方法2: 使用FFmpeg + 截图 (备选方案)
                if not success and self.check_ffmpeg():
                    self.progress_update.emit("使用FFmpeg导出...")
                    success = self.export_with_ffmpeg(html_file)
                
                # 方法3: 使用PyQt6 WebEngine截图 (最后备选)
                if not success:
                    self.progress_update.emit("使用WebEngine截图...")
                    success = self.export_with_webengine(html_file)
                
                if success:
                    self.export_complete.emit(True, f"视频已导出到: {self.output_path}")
                else:
                    self.export_complete.emit(False, "所有导出方法都失败了")
                    
            finally:
                # 清理临时文件
                try:
                    os.unlink(html_file)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"视频导出失败: {e}")
            self.export_complete.emit(False, f"导出失败: {str(e)}")
    
    def check_puppeteer(self) -> bool:
        """检查Puppeteer是否可用"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def check_ffmpeg(self) -> bool:
        """检查FFmpeg是否可用"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def export_with_puppeteer(self, html_file: str) -> bool:
        """使用Puppeteer导出视频"""
        try:
            # 创建Puppeteer脚本
            script_content = f"""
const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {{
    const browser = await puppeteer.launch({{
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }});
    
    const page = await browser.newPage();
    await page.setViewport({{ width: {self.width}, height: {self.height} }});
    
    // 加载HTML文件
    await page.goto('file://{html_file}', {{ waitUntil: 'networkidle0' }});
    
    // 等待动画库加载
    await page.waitForTimeout(2000);
    
    const totalFrames = {int(self.duration * self.fps)};
    const frameDuration = 1000 / {self.fps}; // 毫秒
    
    console.log(`开始录制 ${{totalFrames}} 帧...`);
    
    for (let frame = 0; frame < totalFrames; frame++) {{
        const time = frame / {self.fps};
        
        // 调用renderAtTime函数
        await page.evaluate((t) => {{
            if (typeof window.renderAtTime === 'function') {{
                window.renderAtTime(t);
            }}
        }}, time);
        
        // 等待渲染完成
        await page.waitForTimeout(50);
        
        // 截图
        await page.screenshot({{
            path: `frame_${{frame.toString().padStart(6, '0')}}.png`,
            fullPage: false
        }});
        
        if (frame % 30 === 0) {{
            console.log(`已录制 ${{frame}} / ${{totalFrames}} 帧`);
        }}
    }}
    
    await browser.close();
    console.log('截图完成');
}})();
"""
            
            # 保存脚本
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(script_content)
                script_file = f.name
            
            try:
                # 执行Puppeteer脚本
                self.progress_update.emit("正在截取帧...")
                result = subprocess.run(['node', script_file], 
                                      capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    # 使用FFmpeg合成视频
                    self.progress_update.emit("正在合成视频...")
                    ffmpeg_cmd = [
                        'ffmpeg', '-y',
                        '-framerate', str(self.fps),
                        '-i', 'frame_%06d.png',
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        self.output_path
                    ]
                    
                    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=120)
                    return result.returncode == 0
                
            finally:
                # 清理文件
                try:
                    os.unlink(script_file)
                    # 清理截图文件
                    for i in range(int(self.duration * self.fps)):
                        frame_file = f"frame_{i:06d}.png"
                        if os.path.exists(frame_file):
                            os.unlink(frame_file)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Puppeteer导出失败: {e}")
            return False
        
        return False
    
    def export_with_ffmpeg(self, html_file: str) -> bool:
        """使用FFmpeg导出视频"""
        try:
            # 检查FFmpeg是否可用
            if not self.check_ffmpeg():
                self.progress_update.emit("FFmpeg未安装或不可用")
                return False

            self.progress_update.emit("开始FFmpeg导出...")

            # 创建临时目录存储帧
            import tempfile
            import os

            temp_dir = tempfile.mkdtemp()
            frames_dir = os.path.join(temp_dir, "frames")
            os.makedirs(frames_dir, exist_ok=True)

            # 使用Chrome headless模式截取帧
            try:
                import subprocess
                import time

                # 启动Chrome headless
                chrome_cmd = [
                    "chrome", "--headless", "--disable-gpu", "--virtual-time-budget=5000",
                    f"--window-size={self.width},{self.height}",
                    "--run-all-compositor-stages-before-draw",
                    "--disable-background-timer-throttling",
                    "--disable-renderer-backgrounding",
                    "--disable-backgrounding-occluded-windows",
                    f"file://{html_file}"
                ]

                # 计算需要的帧数
                total_frames = int(self.duration * self.fps)
                frame_interval = 1.0 / self.fps

                self.progress_update.emit(f"准备截取 {total_frames} 帧...")

                # 使用Puppeteer脚本截取帧
                puppeteer_script = f"""
const puppeteer = require('puppeteer');
const path = require('path');

(async () => {{
    const browser = await puppeteer.launch({{
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }});

    const page = await browser.newPage();
    await page.setViewport({{ width: {self.width}, height: {self.height} }});

    await page.goto('file://{html_file}', {{ waitUntil: 'networkidle0' }});

    // 等待动画开始
    await page.waitForTimeout(1000);

    const totalFrames = {total_frames};
    const frameInterval = {frame_interval * 1000}; // 转换为毫秒

    for (let i = 0; i < totalFrames; i++) {{
        const framePath = path.join('{frames_dir}', `frame_${{i.toString().padStart(6, '0')}}.png`);
        await page.screenshot({{ path: framePath, fullPage: false }});

        // 等待下一帧
        if (i < totalFrames - 1) {{
            await page.waitForTimeout(frameInterval);
        }}

        // 更新进度
        const progress = Math.round((i + 1) / totalFrames * 50); // 截图占50%进度
        console.log(`截图进度: ${{progress}}%`);
    }}

    await browser.close();
    console.log('截图完成');
}})();
"""

                # 保存Puppeteer脚本
                script_path = os.path.join(temp_dir, "capture.js")
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(puppeteer_script)

                # 执行Puppeteer脚本
                self.progress_update.emit("正在截取动画帧...")
                result = subprocess.run(
                    ["node", script_path],
                    capture_output=True,
                    text=True,
                    timeout=self.duration * 2 + 60  # 给足够的时间
                )

                if result.returncode != 0:
                    logger.error(f"Puppeteer截图失败: {result.stderr}")
                    return False

                # 使用FFmpeg合成视频
                self.progress_update.emit("正在合成视频...")

                ffmpeg_cmd = [
                    "ffmpeg", "-y",  # 覆盖输出文件
                    "-framerate", str(self.fps),
                    "-i", os.path.join(frames_dir, "frame_%06d.png"),
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-crf", "18",  # 高质量
                    "-preset", "medium",
                    self.output_path
                ]

                result = subprocess.run(
                    ffmpeg_cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode == 0:
                    self.progress_update.emit("视频导出完成")
                    return True
                else:
                    logger.error(f"FFmpeg合成失败: {result.stderr}")
                    return False

            finally:
                # 清理临时文件
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass

        except Exception as e:
            logger.error(f"FFmpeg导出失败: {e}")
            self.progress_update.emit(f"导出失败: {str(e)}")
            return False
    
    def export_with_webengine(self, html_file: str) -> bool:
        """使用WebEngine截图导出"""
        try:
            from PyQt6.QtWebEngineWidgets import QWebEngineView
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QUrl, QTimer
            from PyQt6.QtGui import QPixmap
            import tempfile
            import os

            self.progress_update.emit("开始WebEngine导出...")

            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            frames_dir = os.path.join(temp_dir, "frames")
            os.makedirs(frames_dir, exist_ok=True)

            # 创建WebEngine视图
            web_view = QWebEngineView()
            web_view.resize(self.width, self.height)

            # 加载HTML文件
            web_view.load(QUrl.fromLocalFile(html_file))

            # 等待页面加载完成
            page_loaded = False
            def on_load_finished(success):
                nonlocal page_loaded
                page_loaded = success

            web_view.loadFinished.connect(on_load_finished)

            # 等待加载完成
            app = QApplication.instance()
            while not page_loaded:
                app.processEvents()

            if not page_loaded:
                self.progress_update.emit("页面加载失败")
                return False

            self.progress_update.emit("页面加载完成，开始截图...")

            # 计算帧数和间隔
            total_frames = int(self.duration * self.fps)
            frame_interval = 1000 / self.fps  # 毫秒

            current_frame = 0

            def capture_frame():
                nonlocal current_frame

                if current_frame >= total_frames:
                    # 截图完成，开始合成视频
                    self.compose_video_from_frames(frames_dir)
                    return

                # 截取当前帧
                pixmap = web_view.grab()
                frame_path = os.path.join(frames_dir, f"frame_{current_frame:06d}.png")
                pixmap.save(frame_path, "PNG")

                current_frame += 1
                progress = int((current_frame / total_frames) * 80)  # 截图占80%进度
                self.progress_update.emit(f"截图进度: {progress}%")

                # 设置下一帧的定时器
                QTimer.singleShot(int(frame_interval), capture_frame)

            # 开始截图
            capture_frame()

            return True

        except Exception as e:
            logger.error(f"WebEngine导出失败: {e}")
            self.progress_update.emit(f"WebEngine导出失败: {str(e)}")
            return False

    def compose_video_from_frames(self, frames_dir: str) -> bool:
        """从帧图片合成视频"""
        try:
            import subprocess
            import os

            self.progress_update.emit("正在合成视频...")

            # 检查是否有帧文件
            frame_files = [f for f in os.listdir(frames_dir) if f.startswith("frame_") and f.endswith(".png")]
            if not frame_files:
                self.progress_update.emit("没有找到帧文件")
                return False

            # 使用FFmpeg合成视频
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-framerate", str(self.fps),
                "-i", os.path.join(frames_dir, "frame_%06d.png"),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "18",
                "-preset", "medium",
                self.output_path
            ]

            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                self.progress_update.emit("视频合成完成")
                return True
            else:
                logger.error(f"视频合成失败: {result.stderr}")
                self.progress_update.emit(f"视频合成失败: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"视频合成失败: {e}")
            self.progress_update.emit(f"视频合成失败: {str(e)}")
            return False

class VideoExporter:
    """视频导出器主类"""
    
    def __init__(self):
        self.export_thread = None
    
    def export_video(self, html_content: str, output_path: str, 
                    duration: float = 10.0, fps: int = 30,
                    width: int = 1920, height: int = 1080,
                    progress_callback=None, complete_callback=None):
        """导出视频"""
        
        if self.export_thread and self.export_thread.isRunning():
            logger.warning("视频导出正在进行中")
            return False
        
        # 创建导出线程
        self.export_thread = VideoExportThread(
            html_content, output_path, duration, fps, width, height
        )
        
        # 连接信号
        if progress_callback:
            self.export_thread.progress_update.connect(progress_callback)
        if complete_callback:
            self.export_thread.export_complete.connect(complete_callback)
        
        # 启动导出
        self.export_thread.start()
        return True
    
    def is_exporting(self) -> bool:
        """检查是否正在导出"""
        return self.export_thread and self.export_thread.isRunning()
    
    def cancel_export(self):
        """取消导出"""
        if self.export_thread and self.export_thread.isRunning():
            self.export_thread.terminate()
            self.export_thread.wait()
    
    @staticmethod
    def check_dependencies() -> Dict[str, bool]:
        """检查导出依赖"""
        deps = {}
        
        # 检查Node.js
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            deps['nodejs'] = result.returncode == 0
        except:
            deps['nodejs'] = False
        
        # 检查FFmpeg
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            deps['ffmpeg'] = result.returncode == 0
        except:
            deps['ffmpeg'] = False
        
        # 检查Puppeteer (需要npm)
        try:
            result = subprocess.run(['npm', 'list', 'puppeteer'], 
                                  capture_output=True, text=True, timeout=10)
            deps['puppeteer'] = 'puppeteer@' in result.stdout
        except:
            deps['puppeteer'] = False
        
        return deps
