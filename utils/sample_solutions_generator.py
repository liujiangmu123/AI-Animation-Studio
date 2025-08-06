"""
AI Animation Studio - 示例方案生成器
生成各种类型的示例动画方案，用于演示和测试系统功能
"""

import random
from datetime import datetime, timedelta
from typing import List

from core.enhanced_solution_manager import (
    EnhancedAnimationSolution, SolutionCategory, SolutionQuality, SolutionMetrics
)
from core.data_structures import TechStack
from core.logger import get_logger

logger = get_logger("sample_solutions_generator")


class SampleSolutionsGenerator:
    """示例方案生成器"""
    
    def __init__(self):
        # 示例方案模板
        self.solution_templates = {
            "fade_in": {
                "name": "淡入动画",
                "description": "简单优雅的淡入效果，适用于元素出现场景",
                "category": SolutionCategory.ENTRANCE,
                "tech_stack": TechStack.CSS_ANIMATION,
                "html_code": '<div class="fade-in-element">Hello World</div>',
                "css_code": """
.fade-in-element {
    opacity: 0;
    animation: fadeIn 1s ease-in-out forwards;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}""",
                "js_code": ""
            },
            
            "slide_up": {
                "name": "上滑动画",
                "description": "从底部滑入的动画效果，常用于卡片和面板",
                "category": SolutionCategory.ENTRANCE,
                "tech_stack": TechStack.CSS_ANIMATION,
                "html_code": '<div class="slide-up-element">滑入内容</div>',
                "css_code": """
.slide-up-element {
    transform: translateY(100%);
    animation: slideUp 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}

@keyframes slideUp {
    from {
        transform: translateY(100%);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}""",
                "js_code": ""
            },
            
            "bounce_in": {
                "name": "弹跳进入",
                "description": "活泼的弹跳进入动画，增加趣味性",
                "category": SolutionCategory.ENTRANCE,
                "tech_stack": TechStack.CSS_ANIMATION,
                "html_code": '<div class="bounce-in-element">🎉 弹跳元素</div>',
                "css_code": """
.bounce-in-element {
    animation: bounceIn 1.2s ease-out forwards;
}

@keyframes bounceIn {
    0% {
        transform: scale(0.3);
        opacity: 0;
    }
    50% {
        transform: scale(1.05);
        opacity: 0.8;
    }
    70% {
        transform: scale(0.9);
        opacity: 1;
    }
    100% {
        transform: scale(1);
        opacity: 1;
    }
}""",
                "js_code": ""
            },
            
            "rotate_scale": {
                "name": "旋转缩放",
                "description": "结合旋转和缩放的复合动画效果",
                "category": SolutionCategory.EFFECT,
                "tech_stack": TechStack.CSS_ANIMATION,
                "html_code": '<div class="rotate-scale-element">🔄 旋转缩放</div>',
                "css_code": """
.rotate-scale-element {
    animation: rotateScale 2s infinite alternate;
    transform-origin: center;
}

@keyframes rotateScale {
    0% {
        transform: rotate(0deg) scale(1);
    }
    50% {
        transform: rotate(180deg) scale(1.2);
    }
    100% {
        transform: rotate(360deg) scale(1);
    }
}""",
                "js_code": ""
            },
            
            "pulse_glow": {
                "name": "脉冲发光",
                "description": "脉冲发光效果，适用于按钮和重要元素",
                "category": SolutionCategory.INTERACTION,
                "tech_stack": TechStack.CSS_ANIMATION,
                "html_code": '<button class="pulse-glow-button">点击我</button>',
                "css_code": """
.pulse-glow-button {
    background: #007bff;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    cursor: pointer;
    animation: pulseGlow 2s infinite;
}

@keyframes pulseGlow {
    0%, 100% {
        box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
        transform: scale(1);
    }
    50% {
        box-shadow: 0 0 20px rgba(0, 123, 255, 0.8);
        transform: scale(1.05);
    }
}

.pulse-glow-button:hover {
    animation-play-state: paused;
    transform: scale(1.1);
}""",
                "js_code": ""
            },
            
            "typing_effect": {
                "name": "打字机效果",
                "description": "模拟打字机的文字逐字显示效果",
                "category": SolutionCategory.EFFECT,
                "tech_stack": TechStack.JAVASCRIPT,
                "html_code": '<div class="typing-container"><span id="typing-text"></span><span class="cursor">|</span></div>',
                "css_code": """
.typing-container {
    font-family: 'Courier New', monospace;
    font-size: 18px;
    color: #333;
}

.cursor {
    animation: blink 1s infinite;
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}""",
                "js_code": """
const text = "欢迎使用 AI Animation Studio！";
const typingElement = document.getElementById('typing-text');
let index = 0;

function typeWriter() {
    if (index < text.length) {
        typingElement.textContent += text.charAt(index);
        index++;
        setTimeout(typeWriter, 100);
    }
}

typeWriter();"""
            },
            
            "particle_explosion": {
                "name": "粒子爆炸",
                "description": "粒子爆炸特效，适用于庆祝和强调场景",
                "category": SolutionCategory.EFFECT,
                "tech_stack": TechStack.JAVASCRIPT,
                "html_code": '<div class="particle-container" id="particleContainer"></div>',
                "css_code": """
.particle-container {
    position: relative;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, #1a1a2e, #16213e);
    border-radius: 50%;
    overflow: hidden;
    cursor: pointer;
}

.particle {
    position: absolute;
    width: 4px;
    height: 4px;
    background: #ffd700;
    border-radius: 50%;
    pointer-events: none;
}""",
                "js_code": """
const container = document.getElementById('particleContainer');

container.addEventListener('click', function(e) {
    const rect = container.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    createParticleExplosion(x, y);
});

function createParticleExplosion(x, y) {
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        const angle = (Math.PI * 2 * i) / 20;
        const velocity = 50 + Math.random() * 50;
        
        particle.style.left = x + 'px';
        particle.style.top = y + 'px';
        
        container.appendChild(particle);
        
        animateParticle(particle, angle, velocity);
    }
}

function animateParticle(particle, angle, velocity) {
    const startX = parseFloat(particle.style.left);
    const startY = parseFloat(particle.style.top);
    const startTime = Date.now();
    
    function animate() {
        const elapsed = Date.now() - startTime;
        const progress = elapsed / 1000;
        
        if (progress < 1) {
            const x = startX + Math.cos(angle) * velocity * progress;
            const y = startY + Math.sin(angle) * velocity * progress + 0.5 * 100 * progress * progress;
            
            particle.style.left = x + 'px';
            particle.style.top = y + 'px';
            particle.style.opacity = 1 - progress;
            
            requestAnimationFrame(animate);
        } else {
            particle.remove();
        }
    }
    
    animate();
}"""
            },
            
            "morphing_shapes": {
                "name": "形状变形",
                "description": "SVG形状变形动画，展示流畅的形状过渡",
                "category": SolutionCategory.TRANSITION,
                "tech_stack": TechStack.SVG_ANIMATION,
                "html_code": """
<svg width="200" height="200" viewBox="0 0 200 200">
    <path id="morphing-path" d="M100,50 L150,150 L50,150 Z" fill="#ff6b6b">
        <animate attributeName="d" 
                 values="M100,50 L150,150 L50,150 Z;
                         M100,20 L180,100 L100,180 L20,100 Z;
                         M100,50 L150,150 L50,150 Z"
                 dur="3s" 
                 repeatCount="indefinite"/>
    </path>
</svg>""",
                "css_code": """
svg {
    display: block;
    margin: 20px auto;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
}

#morphing-path {
    transition: fill 0.3s ease;
}

svg:hover #morphing-path {
    fill: #4ecdc4;
}""",
                "js_code": ""
            },
            
            "gsap_timeline": {
                "name": "GSAP时间轴动画",
                "description": "使用GSAP创建复杂的时间轴动画序列",
                "category": SolutionCategory.COMPOSITE,
                "tech_stack": TechStack.GSAP,
                "html_code": """
<div class="gsap-container">
    <div class="box box1"></div>
    <div class="box box2"></div>
    <div class="box box3"></div>
    <button id="playButton">播放动画</button>
</div>""",
                "css_code": """
.gsap-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    padding: 20px;
}

.box {
    width: 50px;
    height: 50px;
    border-radius: 8px;
    margin: 10px;
}

.box1 { background: #ff6b6b; }
.box2 { background: #4ecdc4; }
.box3 { background: #45b7d1; }

#playButton {
    padding: 10px 20px;
    background: #333;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}""",
                "js_code": """
// 需要引入GSAP库
// <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>

const tl = gsap.timeline({ paused: true });

tl.from('.box1', { duration: 0.5, x: -100, opacity: 0, ease: 'back.out(1.7)' })
  .from('.box2', { duration: 0.5, x: 100, opacity: 0, ease: 'back.out(1.7)' }, '-=0.3')
  .from('.box3', { duration: 0.5, y: -100, opacity: 0, ease: 'bounce.out' }, '-=0.3')
  .to('.box', { duration: 0.3, scale: 1.2, stagger: 0.1 })
  .to('.box', { duration: 0.3, scale: 1, stagger: 0.1 });

document.getElementById('playButton').addEventListener('click', () => {
    tl.restart();
});"""
            }
        }
    
    def generate_sample_solutions(self, count: int = None) -> List[EnhancedAnimationSolution]:
        """生成示例方案"""
        try:
            if count is None:
                count = len(self.solution_templates)
            
            solutions = []
            template_names = list(self.solution_templates.keys())
            
            for i in range(count):
                # 循环使用模板
                template_name = template_names[i % len(template_names)]
                template = self.solution_templates[template_name]
                
                # 创建方案
                solution = EnhancedAnimationSolution()
                
                # 基础信息
                solution.name = template["name"]
                if i > 0:
                    solution.name += f" {i+1}"
                
                solution.description = template["description"]
                solution.category = template["category"]
                solution.tech_stack = template["tech_stack"]
                
                # 代码
                solution.html_code = template["html_code"]
                solution.css_code = template["css_code"]
                solution.js_code = template["js_code"]
                
                # 生成随机评估指标
                solution.metrics = self.generate_random_metrics()
                solution.quality_level = self.determine_quality_level(solution.metrics.overall_score)
                
                # 生成随机用户数据
                solution.user_rating = round(random.uniform(3.0, 5.0), 1)
                solution.rating_count = random.randint(5, 50)
                solution.favorite_count = random.randint(0, 20)
                solution.usage_count = random.randint(0, 100)
                
                # 随机时间
                days_ago = random.randint(1, 90)
                solution.created_at = datetime.now() - timedelta(days=days_ago)
                solution.updated_at = solution.created_at + timedelta(days=random.randint(0, days_ago))
                
                # 随机标签
                solution.tags = self.generate_random_tags(template["category"], template["tech_stack"])
                
                solutions.append(solution)
            
            logger.info(f"生成了 {len(solutions)} 个示例方案")
            return solutions
            
        except Exception as e:
            logger.error(f"生成示例方案失败: {e}")
            return []
    
    def generate_random_metrics(self) -> SolutionMetrics:
        """生成随机评估指标"""
        metrics = SolutionMetrics()
        
        # 生成相关联的分数
        base_score = random.uniform(60, 95)
        
        metrics.quality_score = base_score + random.uniform(-10, 10)
        metrics.performance_score = base_score + random.uniform(-15, 15)
        metrics.creativity_score = base_score + random.uniform(-20, 20)
        metrics.usability_score = base_score + random.uniform(-10, 10)
        metrics.compatibility_score = base_score + random.uniform(-5, 5)
        
        # 确保分数在合理范围内
        metrics.quality_score = max(0, min(100, metrics.quality_score))
        metrics.performance_score = max(0, min(100, metrics.performance_score))
        metrics.creativity_score = max(0, min(100, metrics.creativity_score))
        metrics.usability_score = max(0, min(100, metrics.usability_score))
        metrics.compatibility_score = max(0, min(100, metrics.compatibility_score))
        
        # 计算综合分数
        metrics.calculate_overall_score()
        
        return metrics
    
    def determine_quality_level(self, overall_score: float) -> SolutionQuality:
        """确定质量等级"""
        if overall_score >= 85:
            return SolutionQuality.EXCELLENT
        elif overall_score >= 70:
            return SolutionQuality.GOOD
        elif overall_score >= 50:
            return SolutionQuality.AVERAGE
        else:
            return SolutionQuality.POOR
    
    def generate_random_tags(self, category: SolutionCategory, tech_stack: TechStack) -> List[str]:
        """生成随机标签"""
        tag_pools = {
            SolutionCategory.ENTRANCE: ["淡入", "滑入", "弹跳", "旋转", "缩放", "优雅", "流畅"],
            SolutionCategory.EXIT: ["淡出", "滑出", "消失", "收缩", "快速", "平滑"],
            SolutionCategory.TRANSITION: ["过渡", "切换", "变换", "流畅", "自然"],
            SolutionCategory.INTERACTION: ["悬停", "点击", "交互", "响应", "动态"],
            SolutionCategory.EFFECT: ["特效", "炫酷", "视觉", "艺术", "创意"],
            SolutionCategory.COMPOSITE: ["复合", "复杂", "多层", "序列", "组合"]
        }
        
        tech_tags = {
            TechStack.CSS_ANIMATION: ["CSS", "纯CSS", "轻量", "兼容"],
            TechStack.JAVASCRIPT: ["JavaScript", "动态", "交互", "可控"],
            TechStack.GSAP: ["GSAP", "专业", "高性能", "复杂"],
            TechStack.THREE_JS: ["3D", "WebGL", "立体", "沉浸"],
            TechStack.SVG_ANIMATION: ["SVG", "矢量", "缩放", "清晰"]
        }
        
        # 选择标签
        category_tags = tag_pools.get(category, [])
        tech_stack_tags = tech_tags.get(tech_stack, [])
        
        # 随机选择2-4个标签
        all_tags = category_tags + tech_stack_tags + ["动画", "效果", "UI"]
        selected_tags = random.sample(all_tags, min(random.randint(2, 4), len(all_tags)))
        
        return selected_tags
    
    def create_advanced_samples(self) -> List[EnhancedAnimationSolution]:
        """创建高级示例方案"""
        advanced_templates = [
            {
                "name": "3D卡片翻转",
                "description": "3D透视卡片翻转效果，展示正反两面内容",
                "category": SolutionCategory.INTERACTION,
                "tech_stack": TechStack.CSS_ANIMATION,
                "html_code": """
<div class="card-container">
    <div class="card">
        <div class="card-front">
            <h3>正面</h3>
            <p>悬停查看背面</p>
        </div>
        <div class="card-back">
            <h3>背面</h3>
            <p>这是卡片的背面内容</p>
        </div>
    </div>
</div>""",
                "css_code": """
.card-container {
    perspective: 1000px;
    width: 300px;
    height: 200px;
    margin: 50px auto;
}

.card {
    position: relative;
    width: 100%;
    height: 100%;
    transform-style: preserve-3d;
    transition: transform 0.6s;
    cursor: pointer;
}

.card:hover {
    transform: rotateY(180deg);
}

.card-front, .card-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.card-front {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.card-back {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    transform: rotateY(180deg);
}""",
                "js_code": ""
            },
            
            {
                "name": "液体加载动画",
                "description": "模拟液体流动的加载动画效果",
                "category": SolutionCategory.EFFECT,
                "tech_stack": TechStack.CSS_ANIMATION,
                "html_code": """
<div class="liquid-loader">
    <div class="liquid"></div>
    <div class="percentage">75%</div>
</div>""",
                "css_code": """
.liquid-loader {
    position: relative;
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background: #f0f0f0;
    overflow: hidden;
    border: 8px solid #ddd;
}

.liquid {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 75%;
    background: linear-gradient(0deg, #00c9ff 0%, #92fe9d 100%);
    border-radius: 0 0 50% 50%;
    animation: wave 2s ease-in-out infinite;
}

.liquid::before {
    content: '';
    position: absolute;
    top: -10px;
    left: 0;
    width: 100%;
    height: 20px;
    background: inherit;
    border-radius: 50%;
    animation: wave 2s ease-in-out infinite reverse;
}

.percentage {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 24px;
    font-weight: bold;
    color: #333;
    z-index: 10;
}

@keyframes wave {
    0%, 100% {
        transform: translateX(0) rotate(0deg);
    }
    50% {
        transform: translateX(-10px) rotate(5deg);
    }
}""",
                "js_code": ""
            }
        ]
        
        solutions = []
        
        for template in advanced_templates:
            solution = EnhancedAnimationSolution()
            
            solution.name = template["name"]
            solution.description = template["description"]
            solution.category = template["category"]
            solution.tech_stack = template["tech_stack"]
            solution.html_code = template["html_code"]
            solution.css_code = template["css_code"]
            solution.js_code = template["js_code"]
            
            # 高级方案通常质量更高
            solution.metrics = self.generate_high_quality_metrics()
            solution.quality_level = SolutionQuality.EXCELLENT
            
            # 更好的用户反馈
            solution.user_rating = round(random.uniform(4.0, 5.0), 1)
            solution.rating_count = random.randint(10, 30)
            solution.favorite_count = random.randint(5, 25)
            solution.usage_count = random.randint(20, 80)
            
            # 较新的创建时间
            days_ago = random.randint(1, 30)
            solution.created_at = datetime.now() - timedelta(days=days_ago)
            solution.updated_at = solution.created_at + timedelta(days=random.randint(0, days_ago))
            
            solution.tags = ["高级", "专业", "精品"] + self.generate_random_tags(template["category"], template["tech_stack"])[:2]
            
            solutions.append(solution)
        
        return solutions
    
    def generate_high_quality_metrics(self) -> SolutionMetrics:
        """生成高质量评估指标"""
        metrics = SolutionMetrics()
        
        # 高质量方案的分数范围
        base_score = random.uniform(80, 95)
        
        metrics.quality_score = base_score + random.uniform(-5, 5)
        metrics.performance_score = base_score + random.uniform(-8, 8)
        metrics.creativity_score = base_score + random.uniform(-10, 10)
        metrics.usability_score = base_score + random.uniform(-5, 5)
        metrics.compatibility_score = base_score + random.uniform(-3, 3)
        
        # 确保分数在合理范围内
        metrics.quality_score = max(75, min(100, metrics.quality_score))
        metrics.performance_score = max(70, min(100, metrics.performance_score))
        metrics.creativity_score = max(70, min(100, metrics.creativity_score))
        metrics.usability_score = max(75, min(100, metrics.usability_score))
        metrics.compatibility_score = max(80, min(100, metrics.compatibility_score))
        
        # 计算综合分数
        metrics.calculate_overall_score()
        
        return metrics
    
    def populate_solution_manager(self, solution_manager, include_advanced: bool = True):
        """填充方案管理器"""
        try:
            # 生成基础示例
            basic_solutions = self.generate_sample_solutions()
            
            for solution in basic_solutions:
                solution_manager.add_solution(solution, auto_evaluate=False)
            
            # 生成高级示例
            if include_advanced:
                advanced_solutions = self.create_advanced_samples()
                
                for solution in advanced_solutions:
                    solution_manager.add_solution(solution, auto_evaluate=False)
            
            total_count = len(basic_solutions) + (len(self.create_advanced_samples()) if include_advanced else 0)
            logger.info(f"已向方案管理器添加 {total_count} 个示例方案")
            
        except Exception as e:
            logger.error(f"填充方案管理器失败: {e}")
