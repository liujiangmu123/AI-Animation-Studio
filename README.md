# AI Animation Studio

AI驱动的动画工作站 - 通过自然语言创作专业级Web动画

## 项目概述

AI Animation Studio是一个革命性的动画制作工具，通过AI技术将复杂的动画制作转换为简单的自然语言描述。用户只需要描述想要的动画效果，AI就能自动生成专业的HTML动画代码。

## 核心特性

- 🎵 **旁白驱动制作**: 通过旁白时间精确控制动画节奏
- 🤖 **AI智能生成**: 自然语言描述转换为专业动画代码
- 🎨 **可视化编辑**: 直观的舞台布局和时间轴管理
- 🔗 **完美状态衔接**: 自动处理动画间的连续性
- 📱 **多方案预览**: 一次描述生成多种风格选择
- 🎬 **实时预览**: 基于WebEngine的HTML动画预览

### 增强功能 (v1.0+)
- **🎯 方案管理系统**: 完整的方案生成、存储、评分、收藏功能
- **🧠 智能推荐引擎**: 基于用户行为的个性化方案推荐
- **⚡ 性能优化器**: 自动分析和优化动画性能
- **👁️ 可视化预览器**: 方案的实时可视化预览和分析
- **📊 方案对比工具**: 多方案对比分析功能
- **🎨 模板库系统**: 丰富的预定义动画模板
- **📥📤 导入导出**: 支持多种格式的方案导入导出

## 技术架构

- **前端框架**: PyQt6
- **AI服务**: Google Gemini API
- **动画引擎**: HTML5 + CSS3 + JavaScript
- **预览引擎**: QWebEngineView
- **音频处理**: PyQt6 Audio

## 安装要求

### 系统要求
- Python 3.8+
- Windows 10/11, macOS 10.14+, 或 Linux
- 4GB+ RAM
- 支持OpenGL的显卡

### 依赖安装
```bash
# 进入项目目录
cd "AI Animation Studio"

# 安装依赖
pip install -r requirements.txt

# 或手动安装核心依赖
pip install PyQt6 PyQt6-WebEngine google-generativeai
```

## 快速开始

### 1. 设置API Key（首次使用）
```bash
# 设置Gemini API Key
python setup_api_key.py
```

### 2. 启动应用
```bash
# 推荐方式（包含依赖检查）
python start.py

# 或使用原始启动脚本
python run.py

# 或直接启动
python main.py

# 测试核心功能
python test_core.py
```

### 2. 基本使用流程
1. **配置AI服务**: 在AI生成器中输入Gemini API Key
2. **描述动画**: 用自然语言描述想要的动画效果
3. **生成方案**: AI自动生成多个动画方案
4. **预览调整**: 在预览器中查看和调整效果
5. **舞台编辑**: 在舞台上添加和编辑元素
6. **时间轴同步**: 导入音频并创建时间段
7. **导出作品**: 导出为HTML或视频文件

### 3. 增强功能使用

#### 方案管理系统
- **浏览方案**: 在 "🎯 方案管理" 标签页浏览所有动画方案
- **筛选排序**: 按分类、技术栈、质量等条件筛选方案
- **收藏管理**: 收藏喜欢的方案，建立个人方案库
- **智能推荐**: 点击 "🧠 智能推荐" 获取个性化推荐

#### 模板系统
- **快速创建**: 点击 "🎨 从模板创建" 使用预定义模板
- **自定义变量**: 调整模板参数创建个性化动画
- **模板预览**: 实时预览模板效果

#### 性能优化
- **自动优化**: 选择方案后点击 "⚡ 性能优化" 自动优化代码
- **性能分析**: 在 "👁️ 方案预览" 中查看详细性能报告
- **优化建议**: 获取针对性的性能改进建议

#### 导入导出
- **多格式支持**: JSON、ZIP、HTML、CodePen格式
- **批量操作**: 支持批量导入导出方案
- **完整代码**: 导出包含完整HTML代码的可运行文件

### 4. 示例动画
项目包含完整的测试动画示例：
- `test_animation.html` - 复杂动画演示
- `assets/templates/basic_template.html` - 基础模板
- 内置示例方案库 - 首次运行自动生成

## 项目结构

```
AI Animation Studio/
├── main.py                 # 主程序入口
├── run_app.py              # 增强版启动脚本
├── setup_sample_data.py    # 示例数据设置脚本
├── core/                   # 核心模块
│   ├── enhanced_solution_manager.py      # 增强方案管理器
│   ├── solution_recommendation_engine.py # 智能推荐引擎
│   ├── solution_performance_optimizer.py # 性能优化器
│   └── ...
├── ui/                     # 用户界面
│   ├── enhanced_solution_generator.py    # 增强方案生成器
│   ├── solution_visual_previewer.py      # 可视化预览器
│   ├── template_selector_dialog.py       # 模板选择器
│   └── ...
├── templates/              # 模板库
│   └── animation_templates.py            # 动画模板定义
├── utils/                  # 工具模块
│   ├── solution_import_export.py         # 导入导出工具
│   └── sample_solutions_generator.py     # 示例数据生成器
├── ai/                     # AI生成系统
├── preview/                # 预览系统
├── assets/                 # 资源文件
├── rules/                  # 动画规则库
├── solutions/              # 方案存储目录
├── exports/                # 导出文件
├── logs/                   # 日志文件
└── tests/                  # 测试文件
```

## 开发状态

✅ **核心功能已完成**
- ✅ 完整的项目架构和模块化设计
- ✅ AI动画生成系统（基于Gemini API）
- ✅ 可视化舞台编辑器
- ✅ 时间轴和音频系统
- ✅ HTML动画预览系统
- ✅ 元素管理和属性编辑
- ✅ 多主题界面系统
- ✅ 项目保存和加载

✅ **增强功能已完成 (v1.0+)**
- ✅ 增强方案管理系统（评分、收藏、版本控制）
- ✅ 智能推荐引擎（个性化推荐、用户行为分析）
- ✅ 性能优化器（自动优化、性能分析）
- ✅ 可视化预览器（实时预览、深度分析）
- ✅ 方案对比工具（多方案对比分析）
- ✅ 模板库系统（预定义模板、自定义变量）
- ✅ 导入导出功能（多格式支持、批量操作）

🚧 **待完善功能**
- 🔄 视频导出功能
- 🔄 云端同步和协作
- 🔄 移动端预览
- 🔄 AI动画生成优化
- 🔄 更多动画模板

## 许可证

MIT License
