"""
AI Animation Studio - 核心数据结构
定义项目中使用的所有数据结构和类型
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime

class ElementType(Enum):
    """元素类型"""
    TEXT = "text"
    IMAGE = "image"
    SVG = "svg"
    SHAPE = "shape"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    VIDEO = "video"
    AUDIO = "audio"
    GROUP = "group"

class AnimationType(Enum):
    """动画类型"""
    APPEAR = "appear"      # 出现动画
    DISAPPEAR = "disappear"  # 消失动画
    MOVE = "move"          # 移动动画
    TRANSFORM = "transform"  # 变换动画
    EMPHASIS = "emphasis"   # 强调动画
    TRANSITION = "transition"  # 转场动画

class PathType(Enum):
    """路径类型"""
    LINEAR = "linear"      # 直线
    CURVED = "curved"      # 曲线
    BEZIER = "bezier"      # 贝塞尔曲线
    PRESET = "preset"      # 预设路径

class TechStack(Enum):
    """技术栈类型"""
    CSS_ANIMATION = "css_animation"
    GSAP = "gsap"
    THREE_JS = "three_js"
    JAVASCRIPT = "javascript"
    MIXED = "mixed"

@dataclass
class Asset:
    """素材资源"""
    asset_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    file_path: str = ""
    asset_type: str = "image"  # image, video, audio, etc.
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None  # 对于视频/音频
    file_size: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'asset_id': self.asset_id,
            'name': self.name,
            'file_path': self.file_path,
            'asset_type': self.asset_type,
            'width': self.width,
            'height': self.height,
            'duration': self.duration,
            'file_size': self.file_size,
            'created_at': self.created_at,
            'tags': self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Asset':
        """从字典创建"""
        return cls(**data)

@dataclass
class ProjectTemplate:
    """项目模板"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: str = ""
    tags: List[str] = field(default_factory=list)
    thumbnail: Optional[str] = None
    preview_url: Optional[str] = None
    duration: float = 0.0
    elements: List[Dict[str, Any]] = field(default_factory=list)
    animations: List[Dict[str, Any]] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: str = ""
    version: str = "1.0.0"
    rating: float = 0.0
    usage_count: int = 0

@dataclass
class Point:
    """二维点"""
    x: float
    y: float
    
    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y}
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Point':
        return cls(data["x"], data["y"])

@dataclass
class Transform:
    """变换属性"""
    translate_x: float = 0.0
    translate_y: float = 0.0
    translate_z: float = 0.0
    rotate_x: float = 0.0
    rotate_y: float = 0.0
    rotate_z: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    scale_z: float = 1.0
    
    def to_css_string(self) -> str:
        """转换为CSS transform字符串"""
        transforms = []
        
        if self.translate_x != 0 or self.translate_y != 0:
            transforms.append(f"translate({self.translate_x}px, {self.translate_y}px)")
        
        if self.translate_z != 0:
            transforms.append(f"translateZ({self.translate_z}px)")
        
        if self.rotate_z != 0:
            transforms.append(f"rotate({self.rotate_z}deg)")
        
        if self.rotate_x != 0:
            transforms.append(f"rotateX({self.rotate_x}deg)")
        
        if self.rotate_y != 0:
            transforms.append(f"rotateY({self.rotate_y}deg)")
        
        if self.scale_x != 1 or self.scale_y != 1:
            transforms.append(f"scale({self.scale_x}, {self.scale_y})")
        
        return " ".join(transforms) if transforms else "none"

@dataclass
class ElementStyle:
    """元素样式"""
    width: str = "auto"
    height: str = "auto"
    background_color: str = "transparent"
    color: str = "inherit"
    opacity: float = 1.0
    border_radius: str = "0"
    border: str = "none"
    font_family: str = "inherit"
    font_size: str = "inherit"
    font_weight: str = "normal"
    text_align: str = "left"
    z_index: int = 1
    
    def to_css_dict(self) -> Dict[str, str]:
        """转换为CSS字典"""
        return {
            "width": self.width,
            "height": self.height,
            "background-color": self.background_color,
            "color": self.color,
            "opacity": str(self.opacity),
            "border-radius": self.border_radius,
            "border": self.border,
            "font-family": self.font_family,
            "font-size": self.font_size,
            "font-weight": self.font_weight,
            "text-align": self.text_align,
            "z-index": str(self.z_index)
        }

@dataclass
class ElementState:
    """元素状态"""
    element_id: str
    timestamp: float
    transform: Transform = field(default_factory=Transform)
    style: ElementStyle = field(default_factory=ElementStyle)
    custom_properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "element_id": self.element_id,
            "timestamp": self.timestamp,
            "transform": self.transform.__dict__,
            "style": self.style.__dict__,
            "custom_properties": self.custom_properties
        }

@dataclass
class AnimationPath:
    """动画路径"""
    path_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    path_type: PathType = PathType.LINEAR
    points: List[Point] = field(default_factory=list)
    control_points: List[Point] = field(default_factory=list)
    total_length: float = 0.0
    creation_method: str = "manual"  # manual, drag, click, preset
    
    def add_point(self, point: Point):
        """添加路径点"""
        self.points.append(point)
        self._calculate_length()
    
    def _calculate_length(self):
        """计算路径总长度"""
        if len(self.points) < 2:
            self.total_length = 0.0
            return
        
        total = 0.0
        for i in range(1, len(self.points)):
            p1, p2 = self.points[i-1], self.points[i]
            distance = ((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2) ** 0.5
            total += distance
        
        self.total_length = total

@dataclass
class Element:
    """舞台元素"""
    element_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "未命名元素"
    element_type: ElementType = ElementType.TEXT
    content: str = ""
    position: Point = field(default_factory=lambda: Point(0, 0))
    transform: Transform = field(default_factory=Transform)
    style: ElementStyle = field(default_factory=ElementStyle)
    visible: bool = True
    locked: bool = False
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    custom_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_absolute_position(self, elements: Dict[str, 'Element']) -> Point:
        """获取绝对位置（考虑父元素）"""
        if self.parent_id and self.parent_id in elements:
            parent_pos = elements[self.parent_id].get_absolute_position(elements)
            return Point(
                parent_pos.x + self.position.x,
                parent_pos.y + self.position.y
            )
        return self.position

@dataclass
class TimeSegment:
    """时间段"""
    segment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: float = 0.0
    end_time: float = 1.0
    description: str = ""
    narration_text: str = ""
    animation_type: AnimationType = AnimationType.MOVE
    elements: List[str] = field(default_factory=list)  # 元素ID列表
    
    @property
    def duration(self) -> float:
        """时间段长度"""
        return self.end_time - self.start_time

@dataclass
class AnimationSolution:
    """动画方案"""
    solution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "方案1"
    description: str = ""
    html_code: str = ""
    tech_stack: TechStack = TechStack.CSS_ANIMATION
    element_states: List[ElementState] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)
    complexity_level: str = "medium"  # simple, medium, complex
    recommended: bool = False
    generated_at: datetime = field(default_factory=datetime.now)
    
    def get_end_states(self) -> Dict[str, ElementState]:
        """获取结束状态"""
        end_states = {}
        for state in self.element_states:
            if state.element_id not in end_states or state.timestamp > end_states[state.element_id].timestamp:
                end_states[state.element_id] = state
        return end_states

@dataclass
class Project:
    """项目数据"""
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "新项目"
    description: str = ""
    canvas_width: int = 1920
    canvas_height: int = 1080
    audio_file: Optional[str] = None
    elements: Dict[str, Element] = field(default_factory=dict)
    time_segments: List[TimeSegment] = field(default_factory=list)
    animation_solutions: Dict[str, List[AnimationSolution]] = field(default_factory=dict)
    animation_rules: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)

    # 新增字段以支持增强功能
    duration: float = 30.0  # 项目持续时间
    fps: int = 30  # 帧率
    resolution: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    settings: Optional[Dict[str, Any]] = field(default_factory=dict)  # 项目设置
    saved_at: Optional[datetime] = None  # 最后保存时间
    assets: List['Asset'] = field(default_factory=list)  # 项目素材列表
    
    def add_element(self, element: Element):
        """添加元素"""
        self.elements[element.element_id] = element
        self.modified_at = datetime.now()

    def remove_element(self, element_id: str):
        """移除元素"""
        if element_id in self.elements:
            del self.elements[element_id]
            self.modified_at = datetime.now()

    def add_asset(self, asset: 'Asset'):
        """添加素材"""
        self.assets.append(asset)
        self.modified_at = datetime.now()

    def remove_asset(self, asset_id: str):
        """移除素材"""
        self.assets = [asset for asset in self.assets if asset.asset_id != asset_id]
        self.modified_at = datetime.now()
    
    def add_time_segment(self, segment: TimeSegment):
        """添加时间段"""
        self.time_segments.append(segment)
        self.time_segments.sort(key=lambda s: s.start_time)
        self.modified_at = datetime.now()
    
    def get_segment_at_time(self, time: float) -> Optional[TimeSegment]:
        """获取指定时间的时间段"""
        for segment in self.time_segments:
            if segment.start_time <= time <= segment.end_time:
                return segment
        return None

    # 增强的元素管理方法
    def get_element(self, element_id: str) -> Optional[Element]:
        """获取指定元素"""
        return self.elements.get(element_id)

    def get_elements_by_type(self, element_type: ElementType) -> List[Element]:
        """获取指定类型的所有元素"""
        return [element for element in self.elements.values()
                if element.element_type == element_type]

    def get_visible_elements(self) -> List[Element]:
        """获取所有可见元素"""
        return [element for element in self.elements.values() if element.visible]

    def get_elements_count(self) -> int:
        """获取元素总数"""
        return len(self.elements)

    def get_elements_by_parent(self, parent_id: Optional[str] = None) -> List[Element]:
        """获取指定父元素的子元素，parent_id为None时返回根元素"""
        return [element for element in self.elements.values()
                if element.parent_id == parent_id]

    def update_element(self, element: Element):
        """更新元素"""
        if element.element_id in self.elements:
            self.elements[element.element_id] = element
            self.modified_at = datetime.now()
        else:
            raise ValueError(f"元素不存在: {element.element_id}")

    def move_element(self, element_id: str, new_position: Point):
        """移动元素到新位置"""
        if element_id in self.elements:
            self.elements[element_id].position = new_position
            self.modified_at = datetime.now()
        else:
            raise ValueError(f"元素不存在: {element_id}")

    def set_element_visibility(self, element_id: str, visible: bool):
        """设置元素可见性"""
        if element_id in self.elements:
            self.elements[element_id].visible = visible
            self.modified_at = datetime.now()
        else:
            raise ValueError(f"元素不存在: {element_id}")

    def clear_elements(self):
        """清空所有元素"""
        self.elements.clear()
        self.modified_at = datetime.now()

    def duplicate_element(self, element_id: str) -> Optional[Element]:
        """复制元素"""
        if element_id not in self.elements:
            return None

        original = self.elements[element_id]

        # 创建副本
        import copy
        duplicated = copy.deepcopy(original)
        duplicated.element_id = str(uuid.uuid4())  # 生成新ID
        duplicated.name = f"{original.name}_副本"

        # 稍微偏移位置
        duplicated.position = Point(
            original.position.x + 20,
            original.position.y + 20
        )

        # 添加到项目
        self.add_element(duplicated)

        return duplicated
