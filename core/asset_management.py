"""
专业素材管理系统
参考Adobe After Effects、DaVinci Resolve等专业软件的素材管理模式
"""

import os
import json
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AssetType(Enum):
    """素材类型枚举"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    FONT = "font"
    VECTOR = "vector"
    ANIMATION = "animation"
    TEMPLATE = "template"
    UNKNOWN = "unknown"

class AssetStatus(Enum):
    """素材状态"""
    AVAILABLE = "available"      # 可用
    MISSING = "missing"          # 文件丢失
    OFFLINE = "offline"          # 离线
    PROCESSING = "processing"    # 处理中
    ERROR = "error"             # 错误

@dataclass
class AssetMetadata:
    """素材元数据"""
    # 基本信息
    file_size: int = 0
    file_hash: str = ""
    mime_type: str = ""
    
    # 媒体信息
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    frame_rate: Optional[float] = None
    bit_rate: Optional[int] = None
    
    # 颜色信息
    color_space: Optional[str] = None
    has_alpha: bool = False
    dominant_colors: List[str] = field(default_factory=list)
    
    # 音频信息
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    
    # 扩展信息
    camera_info: Dict[str, Any] = field(default_factory=dict)
    gps_info: Dict[str, Any] = field(default_factory=dict)
    custom_fields: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AssetThumbnail:
    """素材缩略图"""
    small_path: Optional[str] = None      # 64x64
    medium_path: Optional[str] = None     # 256x256
    large_path: Optional[str] = None      # 512x512
    preview_path: Optional[str] = None    # 预览图（可能是动图）
    generated_at: Optional[datetime] = None

@dataclass
class AssetUsage:
    """素材使用情况"""
    used_in_projects: Set[str] = field(default_factory=set)
    used_in_scenes: Set[str] = field(default_factory=set)
    usage_count: int = 0
    last_used: Optional[datetime] = None
    
    def add_usage(self, project_id: str, scene_id: str = None):
        """添加使用记录"""
        self.used_in_projects.add(project_id)
        if scene_id:
            self.used_in_scenes.add(scene_id)
        self.usage_count += 1
        self.last_used = datetime.now()

@dataclass
class EnhancedAsset:
    """增强的素材类 - 统一所有素材管理"""
    # 基本标识
    asset_id: str
    name: str
    file_path: str
    
    # 分类信息
    asset_type: AssetType
    category: str = "未分类"
    tags: Set[str] = field(default_factory=set)
    
    # 状态信息
    status: AssetStatus = AssetStatus.AVAILABLE
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    imported_at: datetime = field(default_factory=datetime.now)
    
    # 详细信息
    metadata: AssetMetadata = field(default_factory=AssetMetadata)
    thumbnail: AssetThumbnail = field(default_factory=AssetThumbnail)
    usage: AssetUsage = field(default_factory=AssetUsage)
    
    # 用户信息
    description: str = ""
    rating: int = 0  # 0-5星评级
    favorite: bool = False
    
    # 版本控制
    version: int = 1
    parent_id: Optional[str] = None  # 用于版本链
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.asset_id:
            self.asset_id = self.generate_id()
        
        # 自动检测素材类型
        if self.asset_type == AssetType.UNKNOWN:
            self.asset_type = self.detect_type()
    
    def generate_id(self) -> str:
        """生成唯一ID"""
        content = f"{self.file_path}{self.created_at.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def detect_type(self) -> AssetType:
        """自动检测素材类型"""
        if not self.file_path:
            return AssetType.UNKNOWN
            
        mime_type, _ = mimetypes.guess_type(self.file_path)
        if not mime_type:
            return AssetType.UNKNOWN
        
        if mime_type.startswith('image/'):
            if mime_type in ['image/svg+xml']:
                return AssetType.VECTOR
            return AssetType.IMAGE
        elif mime_type.startswith('video/'):
            return AssetType.VIDEO
        elif mime_type.startswith('audio/'):
            return AssetType.AUDIO
        elif mime_type.startswith('font/') or self.file_path.endswith(('.ttf', '.otf', '.woff')):
            return AssetType.FONT
        elif mime_type.startswith('text/') or mime_type == 'application/pdf':
            return AssetType.DOCUMENT
        else:
            return AssetType.UNKNOWN
    
    def update_metadata(self):
        """更新元数据"""
        try:
            if not Path(self.file_path).exists():
                self.status = AssetStatus.MISSING
                return
            
            file_stat = Path(self.file_path).stat()
            self.metadata.file_size = file_stat.st_size
            self.modified_at = datetime.fromtimestamp(file_stat.st_mtime)
            
            # 计算文件哈希
            with open(self.file_path, 'rb') as f:
                content = f.read()
                self.metadata.file_hash = hashlib.md5(content).hexdigest()
            
            # 获取MIME类型
            self.metadata.mime_type, _ = mimetypes.guess_type(self.file_path)
            
            self.status = AssetStatus.AVAILABLE
            
        except Exception as e:
            logger.error(f"更新素材元数据失败: {e}")
            self.status = AssetStatus.ERROR
    
    def add_tag(self, tag: str):
        """添加标签"""
        self.tags.add(tag.strip().lower())
    
    def remove_tag(self, tag: str):
        """移除标签"""
        self.tags.discard(tag.strip().lower())
    
    def has_tag(self, tag: str) -> bool:
        """检查是否有标签"""
        return tag.strip().lower() in self.tags
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'asset_id': self.asset_id,
            'name': self.name,
            'file_path': self.file_path,
            'asset_type': self.asset_type.value,
            'category': self.category,
            'tags': list(self.tags),
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'imported_at': self.imported_at.isoformat(),
            'description': self.description,
            'rating': self.rating,
            'favorite': self.favorite,
            'version': self.version,
            'parent_id': self.parent_id,
            'metadata': {
                'file_size': self.metadata.file_size,
                'file_hash': self.metadata.file_hash,
                'mime_type': self.metadata.mime_type,
                'width': self.metadata.width,
                'height': self.metadata.height,
                'duration': self.metadata.duration,
                'frame_rate': self.metadata.frame_rate,
                'bit_rate': self.metadata.bit_rate,
                'color_space': self.metadata.color_space,
                'has_alpha': self.metadata.has_alpha,
                'dominant_colors': self.metadata.dominant_colors,
                'sample_rate': self.metadata.sample_rate,
                'channels': self.metadata.channels,
                'camera_info': self.metadata.camera_info,
                'gps_info': self.metadata.gps_info,
                'custom_fields': self.metadata.custom_fields
            },
            'thumbnail': {
                'small_path': self.thumbnail.small_path,
                'medium_path': self.thumbnail.medium_path,
                'large_path': self.thumbnail.large_path,
                'preview_path': self.thumbnail.preview_path,
                'generated_at': self.thumbnail.generated_at.isoformat() if self.thumbnail.generated_at else None
            },
            'usage': {
                'used_in_projects': list(self.usage.used_in_projects),
                'used_in_scenes': list(self.usage.used_in_scenes),
                'usage_count': self.usage.usage_count,
                'last_used': self.usage.last_used.isoformat() if self.usage.last_used else None
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedAsset':
        """从字典创建"""
        # 基本信息
        asset = cls(
            asset_id=data['asset_id'],
            name=data['name'],
            file_path=data['file_path'],
            asset_type=AssetType(data['asset_type']),
            category=data.get('category', '未分类'),
            tags=set(data.get('tags', [])),
            status=AssetStatus(data.get('status', 'available')),
            description=data.get('description', ''),
            rating=data.get('rating', 0),
            favorite=data.get('favorite', False),
            version=data.get('version', 1),
            parent_id=data.get('parent_id')
        )
        
        # 时间信息
        if 'created_at' in data:
            asset.created_at = datetime.fromisoformat(data['created_at'])
        if 'modified_at' in data:
            asset.modified_at = datetime.fromisoformat(data['modified_at'])
        if 'imported_at' in data:
            asset.imported_at = datetime.fromisoformat(data['imported_at'])
        
        # 元数据
        if 'metadata' in data:
            meta = data['metadata']
            asset.metadata = AssetMetadata(
                file_size=meta.get('file_size', 0),
                file_hash=meta.get('file_hash', ''),
                mime_type=meta.get('mime_type', ''),
                width=meta.get('width'),
                height=meta.get('height'),
                duration=meta.get('duration'),
                frame_rate=meta.get('frame_rate'),
                bit_rate=meta.get('bit_rate'),
                color_space=meta.get('color_space'),
                has_alpha=meta.get('has_alpha', False),
                dominant_colors=meta.get('dominant_colors', []),
                sample_rate=meta.get('sample_rate'),
                channels=meta.get('channels'),
                camera_info=meta.get('camera_info', {}),
                gps_info=meta.get('gps_info', {}),
                custom_fields=meta.get('custom_fields', {})
            )
        
        # 缩略图
        if 'thumbnail' in data:
            thumb = data['thumbnail']
            asset.thumbnail = AssetThumbnail(
                small_path=thumb.get('small_path'),
                medium_path=thumb.get('medium_path'),
                large_path=thumb.get('large_path'),
                preview_path=thumb.get('preview_path'),
                generated_at=datetime.fromisoformat(thumb['generated_at']) if thumb.get('generated_at') else None
            )
        
        # 使用情况
        if 'usage' in data:
            usage = data['usage']
            asset.usage = AssetUsage(
                used_in_projects=set(usage.get('used_in_projects', [])),
                used_in_scenes=set(usage.get('used_in_scenes', [])),
                usage_count=usage.get('usage_count', 0),
                last_used=datetime.fromisoformat(usage['last_used']) if usage.get('last_used') else None
            )
        
        return asset


class AssetSearchFilter:
    """素材搜索过滤器"""

    def __init__(self):
        self.text_query: str = ""
        self.asset_types: Set[AssetType] = set()
        self.categories: Set[str] = set()
        self.tags: Set[str] = set()
        self.rating_min: int = 0
        self.rating_max: int = 5
        self.favorites_only: bool = False
        self.date_from: Optional[datetime] = None
        self.date_to: Optional[datetime] = None
        self.file_size_min: int = 0
        self.file_size_max: int = 0
        self.status_filter: Set[AssetStatus] = set()

    def matches(self, asset: EnhancedAsset) -> bool:
        """检查素材是否匹配过滤条件"""
        # 文本搜索
        if self.text_query:
            query_lower = self.text_query.lower()
            if not (query_lower in asset.name.lower() or
                   query_lower in asset.description.lower() or
                   any(query_lower in tag for tag in asset.tags)):
                return False

        # 类型过滤
        if self.asset_types and asset.asset_type not in self.asset_types:
            return False

        # 分类过滤
        if self.categories and asset.category not in self.categories:
            return False

        # 标签过滤
        if self.tags and not self.tags.intersection(asset.tags):
            return False

        # 评级过滤
        if not (self.rating_min <= asset.rating <= self.rating_max):
            return False

        # 收藏过滤
        if self.favorites_only and not asset.favorite:
            return False

        # 日期过滤
        if self.date_from and asset.created_at < self.date_from:
            return False
        if self.date_to and asset.created_at > self.date_to:
            return False

        # 文件大小过滤
        if self.file_size_min > 0 and asset.metadata.file_size < self.file_size_min:
            return False
        if self.file_size_max > 0 and asset.metadata.file_size > self.file_size_max:
            return False

        # 状态过滤
        if self.status_filter and asset.status not in self.status_filter:
            return False

        return True


class AssetIndex:
    """素材索引 - 用于快速搜索"""

    def __init__(self):
        self.name_index: Dict[str, Set[str]] = {}      # 名称索引
        self.tag_index: Dict[str, Set[str]] = {}       # 标签索引
        self.type_index: Dict[AssetType, Set[str]] = {} # 类型索引
        self.category_index: Dict[str, Set[str]] = {}   # 分类索引
        self.hash_index: Dict[str, str] = {}           # 哈希索引（去重）

    def add_asset(self, asset: EnhancedAsset):
        """添加素材到索引"""
        asset_id = asset.asset_id

        # 名称索引
        name_words = asset.name.lower().split()
        for word in name_words:
            if word not in self.name_index:
                self.name_index[word] = set()
            self.name_index[word].add(asset_id)

        # 标签索引
        for tag in asset.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(asset_id)

        # 类型索引
        if asset.asset_type not in self.type_index:
            self.type_index[asset.asset_type] = set()
        self.type_index[asset.asset_type].add(asset_id)

        # 分类索引
        if asset.category not in self.category_index:
            self.category_index[asset.category] = set()
        self.category_index[asset.category].add(asset_id)

        # 哈希索引
        if asset.metadata.file_hash:
            self.hash_index[asset.metadata.file_hash] = asset_id

    def remove_asset(self, asset: EnhancedAsset):
        """从索引中移除素材"""
        asset_id = asset.asset_id

        # 从各个索引中移除
        for word_set in self.name_index.values():
            word_set.discard(asset_id)

        for tag_set in self.tag_index.values():
            tag_set.discard(asset_id)

        for type_set in self.type_index.values():
            type_set.discard(asset_id)

        for category_set in self.category_index.values():
            category_set.discard(asset_id)

        # 从哈希索引中移除
        if asset.metadata.file_hash in self.hash_index:
            del self.hash_index[asset.metadata.file_hash]

    def search_by_text(self, query: str) -> Set[str]:
        """按文本搜索"""
        if not query:
            return set()

        words = query.lower().split()
        result_sets = []

        for word in words:
            word_results = set()

            # 在名称索引中搜索
            for indexed_word, asset_ids in self.name_index.items():
                if word in indexed_word:
                    word_results.update(asset_ids)

            # 在标签索引中搜索
            for tag, asset_ids in self.tag_index.items():
                if word in tag:
                    word_results.update(asset_ids)

            result_sets.append(word_results)

        # 取交集（所有词都要匹配）
        if result_sets:
            return set.intersection(*result_sets)
        return set()

    def find_duplicates(self) -> Dict[str, List[str]]:
        """查找重复文件"""
        duplicates = {}
        hash_to_assets = {}

        for file_hash, asset_id in self.hash_index.items():
            if file_hash not in hash_to_assets:
                hash_to_assets[file_hash] = []
            hash_to_assets[file_hash].append(asset_id)

        for file_hash, asset_ids in hash_to_assets.items():
            if len(asset_ids) > 1:
                duplicates[file_hash] = asset_ids

        return duplicates


class AssetManager:
    """专业素材管理器 - 核心管理类"""

    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else None
        self.assets: Dict[str, EnhancedAsset] = {}
        self.index = AssetIndex()
        self.cache_dir = self._setup_cache_dir()
        self.thumbnail_dir = self.cache_dir / "thumbnails"
        self.thumbnail_dir.mkdir(exist_ok=True)

        # 初始化缩略图生成器
        from .thumbnail_generator import ThumbnailGenerator
        self.thumbnail_generator = ThumbnailGenerator(self.thumbnail_dir)

        # 统计信息
        self.stats = {
            'total_assets': 0,
            'by_type': {},
            'by_category': {},
            'total_size': 0,
            'missing_files': 0
        }

        logger.info("专业素材管理器初始化完成")

    def _setup_cache_dir(self) -> Path:
        """设置缓存目录"""
        if self.project_path:
            cache_dir = self.project_path / ".asset_cache"
        else:
            cache_dir = Path.home() / ".ai_animation_studio" / "asset_cache"

        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def add_asset(self, file_path: str, category: str = "未分类", tags: List[str] = None) -> Optional[EnhancedAsset]:
        """添加素材"""
        try:
            file_path = str(Path(file_path).resolve())

            # 检查文件是否存在
            if not Path(file_path).exists():
                logger.error(f"文件不存在: {file_path}")
                return None

            # 检查是否已存在
            existing_asset = self.find_by_path(file_path)
            if existing_asset:
                logger.info(f"素材已存在: {existing_asset.name}")
                return existing_asset

            # 创建新素材
            asset = EnhancedAsset(
                asset_id="",  # 将自动生成
                name=Path(file_path).name,
                file_path=file_path,
                asset_type=AssetType.UNKNOWN,  # 将自动检测
                category=category,
                tags=set(tags) if tags else set()
            )

            # 更新元数据
            asset.update_metadata()

            # 生成缩略图
            self._generate_thumbnails_for_asset(asset)

            # 添加到管理器
            self.assets[asset.asset_id] = asset
            self.index.add_asset(asset)
            self._update_stats()

            logger.info(f"已添加素材: {asset.name} ({asset.asset_type.value})")
            return asset

        except Exception as e:
            logger.error(f"添加素材失败: {e}")
            return None

    def remove_asset(self, asset_id: str) -> bool:
        """移除素材"""
        try:
            if asset_id not in self.assets:
                return False

            asset = self.assets[asset_id]

            # 从索引中移除
            self.index.remove_asset(asset)

            # 删除缩略图
            self._cleanup_thumbnails(asset)

            # 从字典中移除
            del self.assets[asset_id]

            self._update_stats()
            logger.info(f"已移除素材: {asset.name}")
            return True

        except Exception as e:
            logger.error(f"移除素材失败: {e}")
            return False

    def get_asset(self, asset_id: str) -> Optional[EnhancedAsset]:
        """获取素材"""
        return self.assets.get(asset_id)

    def find_by_path(self, file_path: str) -> Optional[EnhancedAsset]:
        """根据文件路径查找素材"""
        file_path = str(Path(file_path).resolve())
        for asset in self.assets.values():
            if asset.file_path == file_path:
                return asset
        return None

    def search(self, filter_obj: AssetSearchFilter) -> List[EnhancedAsset]:
        """搜索素材"""
        try:
            results = []

            # 如果有文本查询，先用索引快速筛选
            candidate_ids = None
            if filter_obj.text_query:
                candidate_ids = self.index.search_by_text(filter_obj.text_query)
                if not candidate_ids:
                    return []

            # 遍历素材进行过滤
            for asset_id, asset in self.assets.items():
                # 如果有候选ID列表，只检查候选素材
                if candidate_ids is not None and asset_id not in candidate_ids:
                    continue

                if filter_obj.matches(asset):
                    results.append(asset)

            return results

        except Exception as e:
            logger.error(f"搜索素材失败: {e}")
            return []

    def get_by_type(self, asset_type: AssetType) -> List[EnhancedAsset]:
        """按类型获取素材"""
        return [asset for asset in self.assets.values() if asset.asset_type == asset_type]

    def get_by_category(self, category: str) -> List[EnhancedAsset]:
        """按分类获取素材"""
        return [asset for asset in self.assets.values() if asset.category == category]

    def get_favorites(self) -> List[EnhancedAsset]:
        """获取收藏的素材"""
        return [asset for asset in self.assets.values() if asset.favorite]

    def get_recent(self, limit: int = 10) -> List[EnhancedAsset]:
        """获取最近使用的素材"""
        sorted_assets = sorted(
            self.assets.values(),
            key=lambda x: x.usage.last_used or datetime.min,
            reverse=True
        )
        return sorted_assets[:limit]

    def get_all_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set()
        for asset in self.assets.values():
            categories.add(asset.category)
        return sorted(list(categories))

    def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        tags = set()
        for asset in self.assets.values():
            tags.update(asset.tags)
        return sorted(list(tags))

    def find_duplicates(self) -> Dict[str, List[EnhancedAsset]]:
        """查找重复文件"""
        hash_duplicates = self.index.find_duplicates()
        result = {}

        for file_hash, asset_ids in hash_duplicates.items():
            assets = [self.assets[aid] for aid in asset_ids if aid in self.assets]
            if len(assets) > 1:
                result[file_hash] = assets

        return result

    def verify_assets(self) -> Dict[str, List[str]]:
        """验证所有素材文件"""
        results = {
            'missing': [],
            'corrupted': [],
            'valid': []
        }

        for asset in self.assets.values():
            try:
                if not Path(asset.file_path).exists():
                    asset.status = AssetStatus.MISSING
                    results['missing'].append(asset.asset_id)
                else:
                    # 验证文件完整性
                    old_hash = asset.metadata.file_hash
                    asset.update_metadata()

                    if old_hash and old_hash != asset.metadata.file_hash:
                        asset.status = AssetStatus.ERROR
                        results['corrupted'].append(asset.asset_id)
                    else:
                        asset.status = AssetStatus.AVAILABLE
                        results['valid'].append(asset.asset_id)

            except Exception as e:
                logger.error(f"验证素材失败 {asset.name}: {e}")
                asset.status = AssetStatus.ERROR
                results['corrupted'].append(asset.asset_id)

        self._update_stats()
        return results

    def batch_import(self, directory: str, recursive: bool = True,
                    category: str = "导入", tags: List[str] = None) -> List[EnhancedAsset]:
        """批量导入素材"""
        imported_assets = []
        directory = Path(directory)

        if not directory.exists():
            logger.error(f"目录不存在: {directory}")
            return imported_assets

        # 支持的文件扩展名
        supported_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp',  # 图片
            '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv',           # 视频
            '.mp3', '.wav', '.ogg', '.flac', '.aac',                  # 音频
            '.ttf', '.otf', '.woff', '.woff2',                        # 字体
            '.pdf', '.txt', '.md'                                     # 文档
        }

        # 遍历文件
        pattern = "**/*" if recursive else "*"
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                asset = self.add_asset(str(file_path), category, tags)
                if asset:
                    imported_assets.append(asset)

        logger.info(f"批量导入完成，共导入 {len(imported_assets)} 个素材")
        return imported_assets

    def export_catalog(self, output_path: str) -> bool:
        """导出素材目录"""
        try:
            catalog_data = {
                'version': '1.0',
                'exported_at': datetime.now().isoformat(),
                'stats': self.stats,
                'assets': [asset.to_dict() for asset in self.assets.values()]
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(catalog_data, f, indent=2, ensure_ascii=False)

            logger.info(f"素材目录已导出: {output_path}")
            return True

        except Exception as e:
            logger.error(f"导出素材目录失败: {e}")
            return False

    def import_catalog(self, catalog_path: str) -> bool:
        """导入素材目录"""
        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                catalog_data = json.load(f)

            for asset_data in catalog_data.get('assets', []):
                asset = EnhancedAsset.from_dict(asset_data)

                # 验证文件是否存在
                if Path(asset.file_path).exists():
                    self.assets[asset.asset_id] = asset
                    self.index.add_asset(asset)
                else:
                    asset.status = AssetStatus.MISSING
                    self.assets[asset.asset_id] = asset
                    self.index.add_asset(asset)

            self._update_stats()
            logger.info(f"素材目录已导入: {len(catalog_data.get('assets', []))} 个素材")
            return True

        except Exception as e:
            logger.error(f"导入素材目录失败: {e}")
            return False

    def _cleanup_thumbnails(self, asset: EnhancedAsset):
        """清理缩略图"""
        try:
            for thumb_path in [asset.thumbnail.small_path, asset.thumbnail.medium_path,
                             asset.thumbnail.large_path, asset.thumbnail.preview_path]:
                if thumb_path and Path(thumb_path).exists():
                    Path(thumb_path).unlink()
        except Exception as e:
            logger.warning(f"清理缩略图失败: {e}")

    def _update_stats(self):
        """更新统计信息"""
        self.stats['total_assets'] = len(self.assets)
        self.stats['by_type'] = {}
        self.stats['by_category'] = {}
        self.stats['total_size'] = 0
        self.stats['missing_files'] = 0

        for asset in self.assets.values():
            # 按类型统计
            type_name = asset.asset_type.value
            self.stats['by_type'][type_name] = self.stats['by_type'].get(type_name, 0) + 1

            # 按分类统计
            category = asset.category
            self.stats['by_category'][category] = self.stats['by_category'].get(category, 0) + 1

            # 总大小
            self.stats['total_size'] += asset.metadata.file_size

            # 丢失文件
            if asset.status == AssetStatus.MISSING:
                self.stats['missing_files'] += 1

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()

    def _generate_thumbnails_for_asset(self, asset: EnhancedAsset):
        """为素材生成缩略图"""
        try:
            thumbnails = self.thumbnail_generator.generate_thumbnails(
                asset.file_path,
                asset.asset_type.value,
                asset.asset_id
            )

            # 更新素材的缩略图信息
            asset.thumbnail.small_path = thumbnails.get('small_path')
            asset.thumbnail.medium_path = thumbnails.get('medium_path')
            asset.thumbnail.large_path = thumbnails.get('large_path')
            asset.thumbnail.generated_at = datetime.now()

            logger.debug(f"已生成缩略图: {asset.name}")

        except Exception as e:
            logger.error(f"生成缩略图失败 {asset.name}: {e}")

    def regenerate_thumbnails(self, asset_id: str = None) -> bool:
        """重新生成缩略图"""
        try:
            if asset_id:
                # 重新生成单个素材的缩略图
                asset = self.get_asset(asset_id)
                if asset:
                    self._generate_thumbnails_for_asset(asset)
                    return True
                return False
            else:
                # 重新生成所有素材的缩略图
                for asset in self.assets.values():
                    self._generate_thumbnails_for_asset(asset)
                return True

        except Exception as e:
            logger.error(f"重新生成缩略图失败: {e}")
            return False

    def get_thumbnail_path(self, asset_id: str, size: str = 'medium') -> Optional[str]:
        """获取缩略图路径"""
        asset = self.get_asset(asset_id)
        if not asset:
            return None

        if size == 'small':
            return asset.thumbnail.small_path
        elif size == 'medium':
            return asset.thumbnail.medium_path
        elif size == 'large':
            return asset.thumbnail.large_path
        else:
            return asset.thumbnail.medium_path
