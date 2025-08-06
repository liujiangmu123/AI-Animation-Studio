# AI Animation Studio - MCP 配置指南

## 概述

本项目已配置了模型上下文协议（MCP），可以与GitHub Copilot和其他AI工具深度集成。

## 已配置的MCP服务器

### 1. GitHub服务器
- **功能**: 访问GitHub仓库、issues、PR等
- **用途**: 代码管理、版本控制、协作
- **需要**: GitHub Personal Access Token

### 2. 文件系统服务器  
- **功能**: 访问项目文件和目录
- **用途**: 文件操作、代码分析
- **限制**: 仅限AI Animation Studio目录

### 3. Fetch服务器
- **功能**: 获取网页内容和API数据
- **用途**: 获取外部资源、API调用

### 4. 内存服务器
- **功能**: 在会话间保持上下文记忆
- **用途**: 记住项目状态、用户偏好

### 5. Python服务器
- **功能**: 执行Python代码和分析
- **用途**: 代码测试、调试、分析

## 使用方法

### 在VS Code中使用

1. **启动MCP服务器**
   - 打开 `.vscode/mcp.json` 文件
   - 点击文件顶部的 "Start" 按钮

2. **在Copilot Chat中使用**
   - 打开Copilot Chat面板
   - 选择 "Agent" 模式
   - 点击工具图标查看可用的MCP服务器

3. **示例命令**
   ```
   # 分析项目结构
   分析AI Animation Studio项目的架构

   # 获取GitHub信息
   查看这个项目的最新提交

   # 文件操作
   帮我优化main.py文件

   # 获取外部资源
   Fetch https://api.github.com/repos/owner/repo
   ```

## 环境变量设置

### GitHub Token设置
```bash
# Windows
set GITHUB_TOKEN=your_github_token_here

# Linux/Mac
export GITHUB_TOKEN=your_github_token_here
```

### Python路径
项目已自动配置Python路径指向AI Animation Studio目录。

## 故障排除

### 常见问题

1. **MCP服务器启动失败**
   - 检查Node.js和npm是否已安装
   - 确保网络连接正常
   - 检查环境变量是否正确设置

2. **GitHub服务器无法访问**
   - 验证GITHUB_TOKEN是否有效
   - 检查token权限是否足够

3. **Python服务器错误**
   - 确保Python环境正确
   - 检查项目依赖是否已安装

### 日志查看
在VS Code中查看MCP服务器日志：
1. 打开命令面板 (Ctrl+Shift+P)
2. 搜索 "MCP: Show Logs"

## 高级配置

### 自定义工具集
可以在VS Code中定义工具集来组织相关的MCP工具：

```json
{
  "toolsets": {
    "development": ["filesystem", "python", "memory"],
    "collaboration": ["github", "fetch"]
  }
}
```

### 安全设置
- 文件系统访问限制在项目目录内
- GitHub token使用环境变量存储
- 所有外部请求都需要确认

## 最佳实践

1. **定期更新MCP服务器**
   ```bash
   npx -y @modelcontextprotocol/server-github@latest
   ```

2. **使用工具集管理**
   - 根据任务类型启用相关工具
   - 避免同时启用过多服务器

3. **安全考虑**
   - 不要在代码中硬编码token
   - 定期轮换访问令牌
   - 监控MCP服务器的网络活动

## 支持的IDE

- ✅ Visual Studio Code (正式版)
- ⚠️ JetBrains IDEs (预览版)
- ⚠️ Visual Studio (预览版)
- ⚠️ Eclipse (预览版)
- ⚠️ Xcode (预览版)

## 更多资源

- [MCP官方文档](https://modelcontextprotocol.io/)
- [MCP服务器仓库](https://github.com/modelcontextprotocol/servers)
- [VS Code MCP指南](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)
