"""
AI Animation Studio - 动画模板库
包含各种预定义的动画模板，用于快速生成方案
"""

from typing import Dict, List, Any
from core.enhanced_solution_manager import SolutionCategory
from core.data_structures import TechStack


class AnimationTemplateLibrary:
    """动画模板库"""
    
    def __init__(self):
        self.templates = {
            # 入场动画模板
            "entrance_templates": {
                "fade_in_up": {
                    "name": "淡入上移",
                    "description": "元素从下方淡入并上移的优雅动画",
                    "category": SolutionCategory.ENTRANCE,
                    "tech_stack": TechStack.CSS_ANIMATION,
                    "html_template": '<div class="fade-in-up">{content}</div>',
                    "css_template": """
.fade-in-up {
    opacity: 0;
    transform: translateY(30px);
    animation: fadeInUp {duration} {easing} forwards;
}

@keyframes fadeInUp {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}""",
                    "js_template": "",
                    "variables": {
                        "duration": ["0.5s", "0.8s", "1s", "1.2s"],
                        "easing": ["ease", "ease-out", "ease-in-out", "cubic-bezier(0.25, 0.46, 0.45, 0.94)"],
                        "content": ["内容文本", "标题", "卡片内容"]
                    }
                },
                
                "slide_in_left": {
                    "name": "左侧滑入",
                    "description": "元素从左侧滑入的动画效果",
                    "category": SolutionCategory.ENTRANCE,
                    "tech_stack": TechStack.CSS_ANIMATION,
                    "html_template": '<div class="slide-in-left">{content}</div>',
                    "css_template": """
.slide-in-left {
    transform: translateX(-100%);
    animation: slideInLeft {duration} {easing} forwards;
}

@keyframes slideInLeft {
    to {
        transform: translateX(0);
    }
}""",
                    "js_template": "",
                    "variables": {
                        "duration": ["0.6s", "0.8s", "1s"],
                        "easing": ["ease-out", "cubic-bezier(0.25, 0.46, 0.45, 0.94)"],
                        "content": ["菜单项", "侧边栏", "导航"]
                    }
                },
                
                "zoom_in": {
                    "name": "缩放进入",
                    "description": "元素从小到大缩放进入的动画",
                    "category": SolutionCategory.ENTRANCE,
                    "tech_stack": TechStack.CSS_ANIMATION,
                    "html_template": '<div class="zoom-in">{content}</div>',
                    "css_template": """
.zoom-in {
    transform: scale(0);
    animation: zoomIn {duration} {easing} forwards;
}

@keyframes zoomIn {
    to {
        transform: scale(1);
    }
}""",
                    "js_template": "",
                    "variables": {
                        "duration": ["0.4s", "0.6s", "0.8s"],
                        "easing": ["ease-out", "back.out(1.7)", "elastic.out(1, 0.3)"],
                        "content": ["按钮", "图标", "弹窗"]
                    }
                }
            },
            
            # 退场动画模板
            "exit_templates": {
                "fade_out_down": {
                    "name": "淡出下移",
                    "description": "元素淡出并向下移动消失",
                    "category": SolutionCategory.EXIT,
                    "tech_stack": TechStack.CSS_ANIMATION,
                    "html_template": '<div class="fade-out-down">{content}</div>',
                    "css_template": """
.fade-out-down {
    animation: fadeOutDown {duration} {easing} forwards;
}

@keyframes fadeOutDown {
    to {
        opacity: 0;
        transform: translateY(30px);
    }
}""",
                    "js_template": "",
                    "variables": {
                        "duration": ["0.5s", "0.8s", "1s"],
                        "easing": ["ease-in", "ease-in-out"],
                        "content": ["提示信息", "通知", "临时元素"]
                    }
                },
                
                "slide_out_right": {
                    "name": "右侧滑出",
                    "description": "元素向右侧滑出消失",
                    "category": SolutionCategory.EXIT,
                    "tech_stack": TechStack.CSS_ANIMATION,
                    "html_template": '<div class="slide-out-right">{content}</div>',
                    "css_template": """
.slide-out-right {
    animation: slideOutRight {duration} {easing} forwards;
}

@keyframes slideOutRight {
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}""",
                    "js_template": "",
                    "variables": {
                        "duration": ["0.4s", "0.6s", "0.8s"],
                        "easing": ["ease-in", "cubic-bezier(0.55, 0.055, 0.675, 0.19)"],
                        "content": ["侧边栏", "抽屉", "面板"]
                    }
                }
            },
            
            # 交互动画模板
            "interaction_templates": {
                "hover_lift": {
                    "name": "悬停上浮",
                    "description": "鼠标悬停时元素上浮的交互效果",
                    "category": SolutionCategory.INTERACTION,
                    "tech_stack": TechStack.CSS_ANIMATION,
                    "html_template": '<div class="hover-lift">{content}</div>',
                    "css_template": """
.hover-lift {
    transition: transform {duration} {easing}, box-shadow {duration} {easing};
    cursor: pointer;
}

.hover-lift:hover {
    transform: translateY(-{lift_distance});
    box-shadow: 0 {shadow_blur} {shadow_spread} rgba(0, 0, 0, 0.15);
}""",
                    "js_template": "",
                    "variables": {
                        "duration": ["0.2s", "0.3s", "0.4s"],
                        "easing": ["ease", "ease-out", "cubic-bezier(0.25, 0.46, 0.45, 0.94)"],
                        "lift_distance": ["5px", "8px", "10px", "15px"],
                        "shadow_blur": ["10px", "15px", "20px"],
                        "shadow_spread": ["5px", "8px", "10px"],
                        "content": ["卡片", "按钮", "图片"]
                    }
                },
                
                "button_ripple": {
                    "name": "按钮波纹",
                    "description": "点击按钮时的波纹扩散效果",
                    "category": SolutionCategory.INTERACTION,
                    "tech_stack": TechStack.JAVASCRIPT,
                    "html_template": '<button class="ripple-button" onclick="createRipple(event)">{content}</button>',
                    "css_template": """
.ripple-button {
    position: relative;
    overflow: hidden;
    background: {button_color};
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.3s ease;
}

.ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.6);
    transform: scale(0);
    animation: rippleEffect {duration} ease-out;
    pointer-events: none;
}

@keyframes rippleEffect {
    to {
        transform: scale(4);
        opacity: 0;
    }
}""",
                    "js_template": """
function createRipple(event) {
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    const ripple = document.createElement('span');
    ripple.className = 'ripple';
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    
    button.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, {duration_ms});
}""",
                    "variables": {
                        "duration": ["0.6s", "0.8s", "1s"],
                        "duration_ms": ["600", "800", "1000"],
                        "button_color": ["#007bff", "#28a745", "#dc3545", "#ffc107"],
                        "content": ["点击我", "提交", "确认", "开始"]
                    }
                }
            },
            
            # 特效动画模板
            "effect_templates": {
                "floating_particles": {
                    "name": "浮动粒子",
                    "description": "背景浮动粒子特效",
                    "category": SolutionCategory.EFFECT,
                    "tech_stack": TechStack.JAVASCRIPT,
                    "html_template": '<div class="particles-container" id="particlesContainer"></div>',
                    "css_template": """
.particles-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: -1;
}

.particle {
    position: absolute;
    width: {particle_size};
    height: {particle_size};
    background: {particle_color};
    border-radius: 50%;
    opacity: {particle_opacity};
}""",
                    "js_template": """
class ParticleSystem {
    constructor(container) {
        this.container = container;
        this.particles = [];
        this.particleCount = {particle_count};
        
        this.init();
    }
    
    init() {
        for (let i = 0; i < this.particleCount; i++) {
            this.createParticle();
        }
        this.animate();
    }
    
    createParticle() {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        particle.style.left = Math.random() * window.innerWidth + 'px';
        particle.style.top = Math.random() * window.innerHeight + 'px';
        
        const particle_data = {
            element: particle,
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            vx: (Math.random() - 0.5) * {velocity},
            vy: (Math.random() - 0.5) * {velocity}
        };
        
        this.container.appendChild(particle);
        this.particles.push(particle_data);
    }
    
    animate() {
        this.particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            if (particle.x < 0 || particle.x > window.innerWidth) particle.vx *= -1;
            if (particle.y < 0 || particle.y > window.innerHeight) particle.vy *= -1;
            
            particle.element.style.left = particle.x + 'px';
            particle.element.style.top = particle.y + 'px';
        });
        
        requestAnimationFrame(() => this.animate());
    }
}

const particleSystem = new ParticleSystem(document.getElementById('particlesContainer'));""",
                    "variables": {
                        "particle_count": ["20", "30", "50"],
                        "particle_size": ["2px", "3px", "4px"],
                        "particle_color": ["#ffffff", "#ffd700", "#ff6b6b", "#4ecdc4"],
                        "particle_opacity": ["0.3", "0.5", "0.7"],
                        "velocity": ["0.5", "1", "1.5"]
                    }
                },
                
                "gradient_wave": {
                    "name": "渐变波浪",
                    "description": "流动的渐变波浪背景效果",
                    "category": SolutionCategory.EFFECT,
                    "tech_stack": TechStack.CSS_ANIMATION,
                    "html_template": '<div class="gradient-wave"></div>',
                    "css_template": """
.gradient-wave {
    width: 100%;
    height: {wave_height};
    background: linear-gradient({angle}, {color1}, {color2}, {color3});
    background-size: {wave_size} {wave_size};
    animation: waveMove {duration} ease-in-out infinite;
}

@keyframes waveMove {
    0%, 100% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
}""",
                    "js_template": "",
                    "variables": {
                        "wave_height": ["200px", "300px", "100vh"],
                        "angle": ["45deg", "90deg", "135deg", "180deg"],
                        "color1": ["#667eea", "#764ba2", "#f093fb", "#4facfe"],
                        "color2": ["#764ba2", "#667eea", "#f5576c", "#00f2fe"],
                        "color3": ["#667eea", "#f093fb", "#667eea", "#4facfe"],
                        "wave_size": ["200%", "300%", "400%"],
                        "duration": ["3s", "4s", "5s", "6s"]
                    }
                }
            },
            
            # 过渡动画模板
            "transition_templates": {
                "page_slide": {
                    "name": "页面滑动",
                    "description": "页面间的滑动过渡效果",
                    "category": SolutionCategory.TRANSITION,
                    "tech_stack": TechStack.JAVASCRIPT,
                    "html_template": """
<div class="page-container">
    <div class="page active" id="page1">{page1_content}</div>
    <div class="page" id="page2">{page2_content}</div>
    <button onclick="switchPage()">切换页面</button>
</div>""",
                    "css_template": """
.page-container {
    position: relative;
    width: 100%;
    height: {container_height};
    overflow: hidden;
}

.page {
    position: absolute;
    width: 100%;
    height: 100%;
    transition: transform {duration} {easing};
    background: {page_background};
    display: flex;
    align-items: center;
    justify-content: center;
}

.page:not(.active) {
    transform: translateX(100%);
}""",
                    "js_template": """
let currentPage = 1;

function switchPage() {
    const page1 = document.getElementById('page1');
    const page2 = document.getElementById('page2');
    
    if (currentPage === 1) {
        page1.style.transform = 'translateX(-100%)';
        page2.style.transform = 'translateX(0)';
        page2.classList.add('active');
        page1.classList.remove('active');
        currentPage = 2;
    } else {
        page1.style.transform = 'translateX(0)';
        page2.style.transform = 'translateX(100%)';
        page1.classList.add('active');
        page2.classList.remove('active');
        currentPage = 1;
    }
}""",
                    "variables": {
                        "container_height": ["400px", "500px", "100vh"],
                        "duration": ["0.5s", "0.8s", "1s"],
                        "easing": ["ease", "ease-in-out", "cubic-bezier(0.25, 0.46, 0.45, 0.94)"],
                        "page_background": ["#f8f9fa", "#e9ecef", "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"],
                        "page1_content": ["页面 1", "首页内容", "欢迎页面"],
                        "page2_content": ["页面 2", "详情内容", "关于页面"]
                    }
                }
            },
            
            # 复合动画模板
            "composite_templates": {
                "loading_sequence": {
                    "name": "加载序列",
                    "description": "多步骤的加载动画序列",
                    "category": SolutionCategory.COMPOSITE,
                    "tech_stack": TechStack.CSS_ANIMATION,
                    "html_template": """
<div class="loading-sequence">
    <div class="loading-step step1"></div>
    <div class="loading-step step2"></div>
    <div class="loading-step step3"></div>
    <div class="loading-text">加载中...</div>
</div>""",
                    "css_template": """
.loading-sequence {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
}

.loading-step {
    width: {step_size};
    height: {step_size};
    border-radius: 50%;
    background: {step_color};
    opacity: 0.3;
}

.step1 {
    animation: loadingPulse {duration} ease-in-out infinite;
}

.step2 {
    animation: loadingPulse {duration} ease-in-out infinite {delay1};
}

.step3 {
    animation: loadingPulse {duration} ease-in-out infinite {delay2};
}

@keyframes loadingPulse {
    0%, 100% {
        opacity: 0.3;
        transform: scale(1);
    }
    50% {
        opacity: 1;
        transform: scale(1.2);
    }
}

.loading-text {
    font-size: 16px;
    color: #666;
    animation: textFade 2s ease-in-out infinite;
}

@keyframes textFade {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
}""",
                    "js_template": "",
                    "variables": {
                        "step_size": ["20px", "25px", "30px"],
                        "step_color": ["#007bff", "#28a745", "#ffc107"],
                        "duration": ["1.5s", "2s", "2.5s"],
                        "delay1": ["0.3s", "0.4s", "0.5s"],
                        "delay2": ["0.6s", "0.8s", "1s"]
                    }
                }
            }
        }
    
    def get_template_by_category(self, category: SolutionCategory) -> Dict[str, Any]:
        """根据分类获取模板"""
        category_mapping = {
            SolutionCategory.ENTRANCE: "entrance_templates",
            SolutionCategory.EXIT: "exit_templates",
            SolutionCategory.INTERACTION: "interaction_templates",
            SolutionCategory.EFFECT: "effect_templates",
            SolutionCategory.COMPOSITE: "composite_templates",
            SolutionCategory.TRANSITION: "transition_templates"
        }
        
        template_category = category_mapping.get(category, "effect_templates")
        return self.templates.get(template_category, {})
    
    def get_template_by_name(self, template_name: str) -> Dict[str, Any]:
        """根据名称获取模板"""
        for category_templates in self.templates.values():
            if template_name in category_templates:
                return category_templates[template_name]
        return {}
    
    def get_all_template_names(self) -> List[str]:
        """获取所有模板名称"""
        names = []
        for category_templates in self.templates.values():
            names.extend(category_templates.keys())
        return names
    
    def generate_solution_from_template(self, template_name: str, 
                                      variables: Dict[str, str] = None) -> Dict[str, Any]:
        """从模板生成方案"""
        template = self.get_template_by_name(template_name)
        
        if not template:
            return {}
        
        # 使用默认变量或提供的变量
        if variables is None:
            variables = {}
            
            # 为每个变量选择默认值（第一个选项）
            for var_name, var_options in template.get("variables", {}).items():
                if var_name not in variables and var_options:
                    variables[var_name] = var_options[0]
        
        # 替换模板中的变量
        html_code = template["html_template"]
        css_code = template["css_template"]
        js_code = template["js_template"]
        
        for var_name, var_value in variables.items():
            placeholder = "{" + var_name + "}"
            html_code = html_code.replace(placeholder, var_value)
            css_code = css_code.replace(placeholder, var_value)
            js_code = js_code.replace(placeholder, var_value)
        
        return {
            "name": template["name"],
            "description": template["description"],
            "category": template["category"],
            "tech_stack": template["tech_stack"],
            "html_code": html_code,
            "css_code": css_code,
            "js_code": js_code,
            "variables_used": variables
        }
    
    def get_template_variables(self, template_name: str) -> Dict[str, List[str]]:
        """获取模板变量选项"""
        template = self.get_template_by_name(template_name)
        return template.get("variables", {})
    
    def search_templates(self, query: str) -> List[str]:
        """搜索模板"""
        query_lower = query.lower()
        matching_templates = []
        
        for category_templates in self.templates.values():
            for template_name, template_data in category_templates.items():
                # 搜索名称和描述
                if (query_lower in template_data["name"].lower() or
                    query_lower in template_data["description"].lower()):
                    matching_templates.append(template_name)
        
        return matching_templates
    
    def get_templates_by_tech_stack(self, tech_stack: TechStack) -> List[str]:
        """根据技术栈获取模板"""
        matching_templates = []
        
        for category_templates in self.templates.values():
            for template_name, template_data in category_templates.items():
                if template_data["tech_stack"] == tech_stack:
                    matching_templates.append(template_name)
        
        return matching_templates
