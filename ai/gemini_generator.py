"""
AI Animation Studio - Gemini动画生成器
基于Google Gemini API的动画代码生成器
"""

from typing import List

from core.logger import get_logger
from core.data_structures import AnimationSolution, TechStack

logger = get_logger("gemini_generator")

# Gemini API - 使用新的google.genai客户端
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
    logger.info("Google Genai 包已成功导入")
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Genai 包未安装，AI功能将不可用")
    # 创建模拟类以避免运行时错误
    class MockGenai:
        class Client:
            def __init__(self, api_key=None):
                pass
            @property
            def models(self):
                return MockGenai.MockModels()

        class MockModels:
            def generate_content(self, model=None, contents=None, config=None):
                return MockResponse()

    class MockTypes:
        class GenerateContentConfig:
            def __init__(self, **kwargs):
                pass

        class ThinkingConfig:
            def __init__(self, **kwargs):
                pass

    class MockResponse:
        def __init__(self):
            self.text = "模拟响应：Gemini API未安装"

    genai = MockGenai()
    types = MockTypes()

# 尝试导入PyQt6，如果失败则使用模拟类
try:
    from PyQt6.QtCore import QThread, pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

    # 模拟PyQt6类
    class QThread:
        def __init__(self):
            pass
        def start(self):
            pass
        def run(self):
            pass

    class pyqtSignal:
        def __init__(self, *args):
            pass
        def emit(self, *args):
            pass

class GeminiGenerator(QThread):
    """Gemini HTML动画生成器"""
    
    result_ready = pyqtSignal(list)  # 生成的动画方案列表
    error_occurred = pyqtSignal(str)  # 错误信息
    progress_update = pyqtSignal(str)  # 进度更新
    
    def __init__(self, api_key: str = None, prompt: str = "", animation_type: str = "fade", model: str = "gemini-2.0-flash-exp", enable_thinking: bool = False):
        super().__init__()
        self.api_key = api_key
        self.prompt = prompt
        self.animation_type = animation_type
        self.model = model
        self.enable_thinking = enable_thinking
        
    def run(self):
        """运行生成任务"""
        try:
            logger.info("开始AI生成任务")

            # 检查Gemini库
            if not GEMINI_AVAILABLE:
                error_msg = "Gemini库未安装，请运行: pip install google-generativeai"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return

            if not self.api_key:
                error_msg = "请先设置Gemini API Key"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return

            logger.info(f"使用模型: {self.model}")
            logger.info(f"API Key长度: {len(self.api_key)}")
            logger.info(f"思考模式: {self.enable_thinking}")

            self.progress_update.emit(f"🤖 正在连接Gemini ({self.model})...")

            # 初始化Gemini客户端 - 使用新的google.genai客户端
            try:
                # 创建客户端
                client = genai.Client(api_key=self.api_key)
                logger.info("Gemini客户端初始化成功")
                self.progress_update.emit("✅ 已连接到Gemini API")
            except Exception as e:
                error_msg = f"Gemini模型初始化失败: {str(e)}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return
            
            # 生成多个方案
            solutions = []
            
            for i, (solution_name, solution_type) in enumerate([
                ("标准方案", "standard"),
                ("增强方案", "enhanced"),
                ("写实方案", "realistic")
            ]):
                logger.info(f"开始生成方案 {i+1}/3: {solution_name}")
                self.progress_update.emit(f"🎨 正在生成{solution_name}... ({i+1}/3)")

                try:
                    # 构建专用的系统指令
                    system_instruction = self._get_system_instruction(solution_type)
                    logger.info(f"系统指令长度: {len(system_instruction)}")

                    # 构建完整提示词
                    full_prompt = self._build_prompt(solution_type)
                    logger.info(f"完整提示词长度: {len(full_prompt)}")

                    thinking_status = "启用" if self.enable_thinking else "禁用"
                    self.progress_update.emit(f"🎨 正在生成{solution_name}... (思考模式: {thinking_status})")

                    # 按照官方文档的方式调用API
                    try:
                        logger.info("开始调用Gemini API...")
                        self.progress_update.emit(f"📡 正在调用API生成{solution_name}...")

                        # 配置生成参数 - 使用新的google.genai客户端方式
                        config = types.GenerateContentConfig(
                            temperature=0.7,
                            max_output_tokens=8192,
                        )

                        # 如果启用思考模式，添加思考配置
                        if self.enable_thinking:
                            config.thinking_config = types.ThinkingConfig(thinking_budget=1024)

                        # 调用Gemini API - 使用新的客户端方式
                        response = client.models.generate_content(
                            model=self.model,
                            contents=full_prompt,
                            config=config
                        )

                        logger.info("API调用完成，正在处理响应...")

                    except Exception as api_error:
                        error_msg = f"API调用失败: {str(api_error)}"
                        logger.error(error_msg)
                        self.progress_update.emit(f"❌ {solution_name}生成失败: {str(api_error)}")
                        continue
                    
                    if response and response.text:
                        logger.info(f"方案{i+1}生成成功，响应长度: {len(response.text)}")
                        self.progress_update.emit(f"✅ {solution_name}生成成功")

                        # 创建动画方案
                        solution = AnimationSolution(
                            name=solution_name,
                            description=f"基于{self.animation_type}的{solution_name}",
                            html_code=response.text,
                            tech_stack=self._detect_tech_stack(response.text),
                            complexity_level=self._get_complexity_level(solution_type),
                            recommended=(i == 0)  # 第一个方案为推荐方案
                        )
                        solutions.append(solution)
                        logger.info(f"方案{i+1}已添加到结果列表")

                    elif response:
                        logger.warning(f"方案{i+1}生成失败：响应为空")
                        logger.warning(f"响应对象: {response}")
                        self.progress_update.emit(f"⚠️ {solution_name}响应为空")
                    else:
                        logger.warning(f"方案{i+1}生成失败：无响应")
                        self.progress_update.emit(f"❌ {solution_name}无响应")

                except Exception as e:
                    error_msg = f"生成方案{i+1}失败: {str(e)}"
                    logger.error(error_msg)
                    logger.error(f"错误详情: {type(e).__name__}: {e}")
                    self.progress_update.emit(f"❌ {solution_name}失败: {str(e)}")
                    continue
            
            logger.info(f"生成任务完成，共生成 {len(solutions)} 个方案")

            if solutions:
                self.progress_update.emit(f"✅ 生成完成，共{len(solutions)}个方案")
                self.result_ready.emit(solutions)
                logger.info("结果已发送到UI")
            else:
                error_msg = "所有方案生成失败，请检查API Key和网络连接"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)

        except Exception as e:
            error_msg = f"生成失败: {str(e)}"
            logger.error(error_msg)
            logger.error(f"错误类型: {type(e).__name__}")
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            self.error_occurred.emit(error_msg)
    
    def _get_system_instruction(self, solution_type: str) -> str:
        """获取基于动画规范文档的系统指令"""
        base_instruction = """你是一个专业的网页动画开发专家，专门为动画录制工具生成HTML动画代码。

## 核心规范要求

### 必须实现的控制函数
生成的HTML必须包含以下控制函数之一：
- renderAtTime(t) - 主推荐
- updateAtTime(t)
- seekTo(t) 
- goToTime(t)
- setAnimationTime(t)

其中t是时间参数（秒，浮点数），函数必须挂载到window对象：
```javascript
window.renderAtTime = renderAtTime;
```

### 动画控制原理
1. 禁用自动播放 - 动画不能自动播放，必须通过控制函数驱动
2. 时间映射 - 将时间参数t映射到动画的具体状态  
3. 同步渲染 - 调用控制函数后立即渲染对应状态

### 技术要求
- 时间参数t单位为秒，起始值0.0
- 控制函数要快速执行，避免重复DOM查询
- 支持现代浏览器，确保无头浏览器兼容
- 包含边界处理（t=0到duration）

### 严格禁止
- 自动播放动画：setInterval、requestAnimationFrame循环
- 依赖实时时间：Date.now()、performance.now()
- 异步动画：setTimeout、Promise延迟

## 输出要求
- 生成完整可运行的HTML文件
- 包含完整的renderAtTime(t)函数实现
- 确保动画完全由时间参数控制
- 代码要有清晰注释说明控制逻辑
- 不要包含解释文字，只输出HTML代码"""
        
        # 根据方案类型添加特定约束
        if solution_type == "enhanced":
            base_instruction += "\n\n### 增强方案要求\n- 添加更多视觉效果和动感\n- 使用高级动画技术\n- 增强用户体验"
        elif solution_type == "realistic":
            base_instruction += "\n\n### 写实方案要求\n- 注重物理真实感\n- 符合自然规律\n- 使用真实的物理参数"
        
        # 根据动画类型添加特定约束
        if self.animation_type != "混合动画":
            type_constraint = f"\n\n### 动画类型约束\n请严格按照 {self.animation_type} 规范生成代码，不要混合使用其他动画技术。"
            base_instruction += type_constraint
        
        return base_instruction
    
    def _build_prompt(self, solution_type: str) -> str:
        """构建完整的提示词"""
        
        # 动画类型特定的技术指导
        type_guidance = {
            "CSS动画": """
生成基于CSS的动画，严格遵循以下要求：
- 只使用CSS变换和样式属性，禁用animation属性
- 在renderAtTime(t)函数中手动计算样式值
- 使用progress = Math.min(t / duration, 1)计算进度
- 通过element.style直接设置样式属性
- 不要使用GSAP、Three.js或其他库
            """,
            "GSAP动画": """
生成基于GSAP的动画，严格遵循以下要求：
- 只使用GSAP库，不要混合CSS动画或Three.js
- 引入GSAP库：<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
- 创建paused时间轴：gsap.timeline({paused: true})
- 在renderAtTime(t)中使用timeline.seek(t)控制进度
- 禁用autoplay和循环
            """,
            "Three.js动画": """
生成基于Three.js的3D动画，严格遵循以下要求：
- 只使用Three.js，不要混合CSS动画或GSAP
- 引入Three.js库：<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
- 移除requestAnimationFrame循环
- 在renderAtTime(t)中更新3D对象属性并调用renderer.render()
- 根据时间参数控制相机、光照、材质等
            """,
            "JavaScript动画": """
生成基于纯JavaScript的动画，严格遵循以下要求：
- 只使用原生JavaScript，不要使用任何动画库
- 禁用setInterval、setTimeout、requestAnimationFrame
- 在renderAtTime(t)中直接操作DOM元素
- 使用数学函数计算动画状态
- 缓存DOM查询结果避免重复查找
            """,
            "混合动画": """
生成包含多种技术的混合动画，可以组合使用：
- CSS动画 + GSAP缓动
- Three.js 3D场景 + CSS界面动画
- JavaScript粒子系统 + CSS背景动画
- 在单一renderAtTime(t)函数中统一控制所有动画组件
- 确保不同技术间的时间同步
- 禁用所有自动播放机制
            """
        }
        
        guidance = type_guidance.get(self.animation_type, type_guidance["JavaScript动画"])
        
        # 方案类型特定的要求
        solution_requirements = {
            "standard": "严格按描述生成，保守稳定，确保兼容性",
            "enhanced": "增加更多视觉效果，动感强烈，使用高级技术",
            "realistic": "更符合物理规律，真实感强，注重细节"
        }
        
        requirement = solution_requirements.get(solution_type, solution_requirements["standard"])
        
        return f"""
{guidance}

用户动画需求：{self.prompt}

方案要求：{requirement}

请严格按照动画规范生成完整的HTML文件，确保：

1. 包含完整的renderAtTime(t)函数实现
2. 函数挂载到window对象：window.renderAtTime = renderAtTime
3. 动画完全由时间参数t控制，禁用自动播放
4. 包含适当的边界检查和错误处理
5. 添加必要的注释说明控制逻辑
6. 严格遵循选定的动画类型约束

现在请生成符合规范的HTML代码：
        """
    
    def _detect_tech_stack(self, html_code: str) -> TechStack:
        """检测技术栈"""
        html_lower = html_code.lower()
        
        if "three.js" in html_lower or "three.min.js" in html_lower:
            return TechStack.THREE_JS
        elif "gsap" in html_lower or "tweenmax" in html_lower:
            return TechStack.GSAP
        elif "@keyframes" in html_lower or "animation:" in html_lower:
            return TechStack.CSS_ANIMATION
        elif "three.js" in html_lower and "gsap" in html_lower:
            return TechStack.MIXED
        else:
            return TechStack.JAVASCRIPT
    
    def _get_complexity_level(self, solution_type: str) -> str:
        """获取复杂度级别"""
        complexity_map = {
            "standard": "simple",
            "enhanced": "complex", 
            "realistic": "medium"
        }
        return complexity_map.get(solution_type, "medium")
