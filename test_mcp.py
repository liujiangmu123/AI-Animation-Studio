#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP功能测试脚本
用于验证MCP服务器配置是否正确
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def check_mcp_config():
    """检查MCP配置文件"""
    config_path = Path(".vscode/mcp.json")
    
    if not config_path.exists():
        print("❌ MCP配置文件不存在")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ MCP配置文件格式正确")
        print(f"📋 配置的服务器数量: {len(config.get('servers', {}))}")
        
        for server_name in config.get('servers', {}):
            print(f"  - {server_name}")
        
        return True
    except json.JSONDecodeError as e:
        print(f"❌ MCP配置文件JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 读取MCP配置文件失败: {e}")
        return False

def check_node_npm():
    """检查Node.js和npm是否安装"""
    try:
        # 检查Node.js
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js版本: {result.stdout.strip()}")
        else:
            print("❌ Node.js未安装或不在PATH中")
            return False
        
        # 检查npm
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm版本: {result.stdout.strip()}")
        else:
            print("❌ npm未安装或不在PATH中")
            return False
        
        return True
    except FileNotFoundError:
        print("❌ Node.js/npm未安装")
        return False

def check_python_env():
    """检查Python环境"""
    print(f"✅ Python版本: {sys.version}")
    print(f"✅ Python路径: {sys.executable}")
    
    # 检查项目依赖
    requirements_path = Path("requirements.txt")
    if requirements_path.exists():
        print("✅ 找到requirements.txt文件")
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                deps = f.read().strip().split('\n')
            print(f"📋 项目依赖数量: {len([d for d in deps if d.strip()])}")
        except Exception as e:
            print(f"⚠️ 读取requirements.txt失败: {e}")
    else:
        print("⚠️ 未找到requirements.txt文件")

def check_github_token():
    """检查GitHub token"""
    token = os.getenv('GITHUB_TOKEN')
    if token:
        print("✅ 找到GITHUB_TOKEN环境变量")
        print(f"📋 Token长度: {len(token)} 字符")
        # 不显示完整token，只显示前4位和后4位
        if len(token) > 8:
            masked_token = token[:4] + '*' * (len(token) - 8) + token[-4:]
            print(f"📋 Token预览: {masked_token}")
    else:
        print("⚠️ 未找到GITHUB_TOKEN环境变量")
        print("💡 请设置GitHub Personal Access Token:")
        print("   Windows: set GITHUB_TOKEN=your_token_here")
        print("   Linux/Mac: export GITHUB_TOKEN=your_token_here")

def test_mcp_server_availability():
    """测试MCP服务器可用性"""
    print("\n🔍 测试MCP服务器可用性...")
    
    servers_to_test = [
        ("@modelcontextprotocol/server-github", "GitHub服务器"),
        ("@modelcontextprotocol/server-filesystem", "文件系统服务器"),
        ("@modelcontextprotocol/server-memory", "内存服务器"),
        ("mcp-server-fetch", "Fetch服务器")
    ]
    
    for package, name in servers_to_test:
        try:
            # 尝试获取包信息
            result = subprocess.run(['npm', 'view', package, 'version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ {name} - 最新版本: {version}")
            else:
                print(f"⚠️ {name} - 无法获取版本信息")
        except subprocess.TimeoutExpired:
            print(f"⚠️ {name} - 请求超时")
        except Exception as e:
            print(f"❌ {name} - 检查失败: {e}")

def main():
    """主函数"""
    print("🚀 AI Animation Studio - MCP配置测试")
    print("=" * 50)
    
    # 检查MCP配置
    print("\n📁 检查MCP配置...")
    mcp_ok = check_mcp_config()
    
    # 检查Node.js环境
    print("\n🟢 检查Node.js环境...")
    node_ok = check_node_npm()
    
    # 检查Python环境
    print("\n🐍 检查Python环境...")
    check_python_env()
    
    # 检查GitHub token
    print("\n🔑 检查GitHub认证...")
    check_github_token()
    
    # 测试服务器可用性
    if node_ok:
        test_mcp_server_availability()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试总结:")
    
    if mcp_ok and node_ok:
        print("✅ MCP配置基本正常，可以在VS Code中启动MCP服务器")
        print("\n💡 下一步:")
        print("1. 在VS Code中打开项目")
        print("2. 打开 .vscode/mcp.json 文件")
        print("3. 点击文件顶部的 'Start' 按钮")
        print("4. 在Copilot Chat中选择 'Agent' 模式")
    else:
        print("❌ 存在配置问题，请根据上述提示进行修复")
        
        if not node_ok:
            print("\n🔧 修复建议:")
            print("1. 安装Node.js: https://nodejs.org/")
            print("2. 重启终端/命令提示符")
            print("3. 重新运行此测试脚本")

if __name__ == "__main__":
    main()
