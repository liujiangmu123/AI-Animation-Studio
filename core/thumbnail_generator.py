"""
专业缩略图生成系统
支持图片、视频、音频、文档等多种格式的缩略图生成
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)

class ThumbnailGenerator:
    """专业缩略图生成器"""
    
    # 缩略图尺寸定义
    SIZES = {
        'small': (64, 64),
        'medium': (256, 256),
        'large': (512, 512)
    }
    
    # 默认颜色方案
    COLORS = {
        'image': '#4F46E5',      # 蓝色
        'video': '#DC2626',      # 红色
        'audio': '#059669',      # 绿色
        'document': '#7C2D12',   # 棕色
        'font': '#7C3AED',       # 紫色
        'vector': '#EA580C',     # 橙色
        'unknown': '#6B7280'     # 灰色
    }
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查外部工具
        self.ffmpeg_available = self._check_ffmpeg()
        self.imagemagick_available = self._check_imagemagick()
        
        logger.info(f"缩略图生成器初始化完成 (FFmpeg: {self.ffmpeg_available}, ImageMagick: {self.imagemagick_available})")
    
    def _check_ffmpeg(self) -> bool:
        """检查FFmpeg是否可用"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_imagemagick(self) -> bool:
        """检查ImageMagick是否可用"""
        try:
            subprocess.run(['magick', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(['convert', '-version'], capture_output=True, check=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False
    
    def generate_thumbnails(self, file_path: str, asset_type: str, asset_id: str) -> Dict[str, Optional[str]]:
        """生成所有尺寸的缩略图"""
        thumbnails = {}
        
        for size_name, size in self.SIZES.items():
            thumbnail_path = self._get_thumbnail_path(asset_id, size_name)
            
            if self._generate_single_thumbnail(file_path, asset_type, thumbnail_path, size):
                thumbnails[f'{size_name}_path'] = str(thumbnail_path)
            else:
                thumbnails[f'{size_name}_path'] = None
        
        return thumbnails
    
    def _get_thumbnail_path(self, asset_id: str, size_name: str) -> Path:
        """获取缩略图路径"""
        return self.cache_dir / f"{asset_id}_{size_name}.png"
    
    def _generate_single_thumbnail(self, file_path: str, asset_type: str, output_path: Path, size: Tuple[int, int]) -> bool:
        """生成单个缩略图"""
        try:
            if asset_type == 'image':
                return self._generate_image_thumbnail(file_path, output_path, size)
            elif asset_type == 'video':
                return self._generate_video_thumbnail(file_path, output_path, size)
            elif asset_type == 'audio':
                return self._generate_audio_thumbnail(file_path, output_path, size)
            elif asset_type == 'vector':
                return self._generate_vector_thumbnail(file_path, output_path, size)
            elif asset_type == 'font':
                return self._generate_font_thumbnail(file_path, output_path, size)
            elif asset_type == 'document':
                return self._generate_document_thumbnail(file_path, output_path, size)
            else:
                return self._generate_default_thumbnail(file_path, asset_type, output_path, size)
                
        except Exception as e:
            logger.error(f"生成缩略图失败 {file_path}: {e}")
            return False
    
    def _generate_image_thumbnail(self, file_path: str, output_path: Path, size: Tuple[int, int]) -> bool:
        """生成图片缩略图"""
        try:
            with Image.open(file_path) as img:
                # 转换为RGB（处理RGBA、P等模式）
                if img.mode in ('RGBA', 'LA'):
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 生成缩略图
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # 创建正方形画布
                thumbnail = Image.new('RGB', size, (255, 255, 255))
                
                # 居中放置
                x = (size[0] - img.width) // 2
                y = (size[1] - img.height) // 2
                thumbnail.paste(img, (x, y))
                
                thumbnail.save(output_path, 'PNG', optimize=True)
                return True
                
        except Exception as e:
            logger.error(f"生成图片缩略图失败: {e}")
            return False
    
    def _generate_video_thumbnail(self, file_path: str, output_path: Path, size: Tuple[int, int]) -> bool:
        """生成视频缩略图"""
        if not self.ffmpeg_available:
            return self._generate_default_thumbnail(file_path, 'video', output_path, size)
        
        try:
            # 使用FFmpeg提取第一帧
            cmd = [
                'ffmpeg',
                '-i', file_path,
                '-vf', f'scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease,pad={size[0]}:{size[1]}:(ow-iw)/2:(oh-ih)/2:white',
                '-vframes', '1',
                '-y',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and output_path.exists():
                return True
            else:
                logger.warning(f"FFmpeg提取视频帧失败: {result.stderr}")
                return self._generate_default_thumbnail(file_path, 'video', output_path, size)
                
        except Exception as e:
            logger.error(f"生成视频缩略图失败: {e}")
            return self._generate_default_thumbnail(file_path, 'video', output_path, size)
    
    def _generate_audio_thumbnail(self, file_path: str, output_path: Path, size: Tuple[int, int]) -> bool:
        """生成音频缩略图（波形图）"""
        try:
            # 创建音频图标缩略图
            img = Image.new('RGB', size, (255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # 背景色
            color = self.COLORS['audio']
            
            # 绘制音频波形样式
            center_y = size[1] // 2
            wave_width = size[0] - 20
            wave_start_x = 10
            
            # 绘制多条波形线
            for i in range(0, wave_width, 4):
                x = wave_start_x + i
                # 生成随机高度的波形
                import random
                height = random.randint(5, size[1] // 3)
                
                draw.line([
                    (x, center_y - height // 2),
                    (x, center_y + height // 2)
                ], fill=color, width=2)
            
            # 添加音频图标
            icon_size = min(size) // 4
            icon_x = size[0] - icon_size - 10
            icon_y = 10
            
            # 绘制简单的音符图标
            draw.ellipse([
                icon_x, icon_y + icon_size - 8,
                icon_x + 8, icon_y + icon_size
            ], fill=color)
            
            draw.line([
                icon_x + 8, icon_y + icon_size - 4,
                icon_x + 8, icon_y + 4
            ], fill=color, width=2)
            
            img.save(output_path, 'PNG')
            return True
            
        except Exception as e:
            logger.error(f"生成音频缩略图失败: {e}")
            return self._generate_default_thumbnail(file_path, 'audio', output_path, size)
    
    def _generate_vector_thumbnail(self, file_path: str, output_path: Path, size: Tuple[int, int]) -> bool:
        """生成矢量图缩略图"""
        try:
            # 对于SVG文件，尝试直接渲染
            if file_path.lower().endswith('.svg'):
                # 尝试使用PIL渲染SVG（需要额外库支持）
                try:
                    from cairosvg import svg2png
                    svg2png(url=file_path, write_to=str(output_path), 
                           output_width=size[0], output_height=size[1])
                    return True
                except ImportError:
                    # 如果没有cairosvg，使用默认方法
                    pass
            
            # 回退到默认缩略图
            return self._generate_default_thumbnail(file_path, 'vector', output_path, size)
            
        except Exception as e:
            logger.error(f"生成矢量图缩略图失败: {e}")
            return self._generate_default_thumbnail(file_path, 'vector', output_path, size)
    
    def _generate_font_thumbnail(self, file_path: str, output_path: Path, size: Tuple[int, int]) -> bool:
        """生成字体缩略图"""
        try:
            img = Image.new('RGB', size, (255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # 尝试使用字体文件
            try:
                font_size = min(size) // 3
                font = ImageFont.truetype(file_path, font_size)
                text = "Aa"
            except:
                # 使用默认字体
                font = ImageFont.load_default()
                text = "Font"
            
            # 获取文本尺寸
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 居中绘制
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            
            draw.text((x, y), text, fill=self.COLORS['font'], font=font)
            
            # 添加字体名称
            font_name = Path(file_path).stem
            small_font = ImageFont.load_default()
            draw.text((5, size[1] - 15), font_name[:10], fill='#666666', font=small_font)
            
            img.save(output_path, 'PNG')
            return True
            
        except Exception as e:
            logger.error(f"生成字体缩略图失败: {e}")
            return self._generate_default_thumbnail(file_path, 'font', output_path, size)
    
    def _generate_document_thumbnail(self, file_path: str, output_path: Path, size: Tuple[int, int]) -> bool:
        """生成文档缩略图"""
        try:
            img = Image.new('RGB', size, (255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # 绘制文档图标
            margin = size[0] // 8
            doc_width = size[0] - 2 * margin
            doc_height = size[1] - 2 * margin
            
            # 文档背景
            draw.rectangle([
                margin, margin,
                margin + doc_width, margin + doc_height
            ], fill='white', outline=self.COLORS['document'], width=2)
            
            # 绘制文本行
            line_height = doc_height // 8
            for i in range(3, 7):
                y = margin + i * line_height
                line_width = doc_width - 20
                if i == 6:  # 最后一行短一些
                    line_width = line_width // 2
                
                draw.rectangle([
                    margin + 10, y,
                    margin + 10 + line_width, y + 2
                ], fill=self.COLORS['document'])
            
            # 添加文件扩展名
            ext = Path(file_path).suffix.upper()
            if ext:
                font = ImageFont.load_default()
                draw.text((margin + 5, margin + doc_height - 20), ext, 
                         fill=self.COLORS['document'], font=font)
            
            img.save(output_path, 'PNG')
            return True
            
        except Exception as e:
            logger.error(f"生成文档缩略图失败: {e}")
            return self._generate_default_thumbnail(file_path, 'document', output_path, size)
    
    def _generate_default_thumbnail(self, file_path: str, asset_type: str, output_path: Path, size: Tuple[int, int]) -> bool:
        """生成默认缩略图"""
        try:
            img = Image.new('RGB', size, (255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # 背景色
            color = self.COLORS.get(asset_type, self.COLORS['unknown'])
            
            # 绘制圆角矩形背景
            margin = size[0] // 8
            draw.rounded_rectangle([
                margin, margin,
                size[0] - margin, size[1] - margin
            ], radius=10, fill=color)
            
            # 添加文件扩展名
            ext = Path(file_path).suffix.upper()
            if ext:
                font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), ext, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (size[0] - text_width) // 2
                y = (size[1] - text_height) // 2
                
                draw.text((x, y), ext, fill='white', font=font)
            
            # 添加类型标识
            type_text = asset_type.upper()
            small_font = ImageFont.load_default()
            draw.text((5, 5), type_text, fill='white', font=small_font)
            
            img.save(output_path, 'PNG')
            return True
            
        except Exception as e:
            logger.error(f"生成默认缩略图失败: {e}")
            return False
