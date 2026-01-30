#!/bin/sh
# Clawdbot Project Initializer
# 快速初始化一个标准化的 Claude Code 项目（支持多技术栈）
#
# MIT License
# Copyright (c) 2025 Edwin <edwin19861218@hotmail.com>

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取技术栈名称
get_tech_name() {
    case $1 in
        node) echo "Node.js/JavaScript" ;;
        python) echo "Python" ;;
        go) echo "Go" ;;
        rust) echo "Rust" ;;
        java) echo "Java" ;;
        general) echo "General/Other" ;;
        *) echo "Unknown" ;;
    esac
}

# 获取项目文件
get_tech_file() {
    case $1 in
        node) echo "package.json" ;;
        python) echo "requirements.txt" ;;
        go) echo "go.mod" ;;
        rust) echo "Cargo.toml" ;;
        java) echo "pom.xml" ;;
        general) echo "" ;;
        *) echo "" ;;
    esac
}

# 检查技术栈是否有效
is_valid_tech() {
    local tech=$1
    local name=$(get_tech_name $tech)
    [ "$name" != "Unknown" ]
}

# 显示帮助信息
show_help() {
    echo "用法: $0 <project-name> [技术栈]"
    echo ""
    echo "描述: 初始化一个标准化的 Claude Code 项目"
    echo ""
    echo "参数:"
    echo "  <project-name>  项目名称（必需）"
    echo "  [技术栈]        项目技术栈（可选）"
    echo ""
    echo "技术栈选项:"
    echo "  node      - Node.js/JavaScript 项目（默认）"
    echo "  python    - Python 项目"
    echo "  go        - Go 项目"
    echo "  rust      - Rust 项目"
    echo "  java      - Java 项目"
    echo "  general   - 通用项目（其他语言或框架）"
    echo ""
    echo "示例:"
    echo "  $0 my-node-app node"
    echo "  $0 my-python-app python"
    echo "  $0 my-go-app go"
    echo "  $0 my-rust-app rust"
    echo "  $0 my-java-app java"
    echo "  $0 my-general-project general"
    echo ""
    echo "提示: 如果不指定技术栈，将使用 Node.js 作为默认值"
    echo ""
}

# 交互式选择技术栈
select_tech_stack() {
    echo ""
    echo -e "${YELLOW}请选择项目的技术栈：${NC}"
    echo ""
    echo "  1) Node.js/JavaScript"
    echo "  2) Python"
    echo "  3) Go"
    echo "  4) Rust"
    echo "  5) Java"
    echo "  6) General/Other"
    echo ""
    read -p "请输入选项 [1-6]: " choice

    case $choice in
        1) TECH_STACK="node" ;;
        2) TECH_STACK="python" ;;
        3) TECH_STACK="go" ;;
        4) TECH_STACK="rust" ;;
        5) TECH_STACK="java" ;;
        6) TECH_STACK="general" ;;
        *)
            echo -e "${RED}无效的选项，将使用默认技术栈（Node.js）${NC}"
            TECH_STACK="node"
            ;;
    esac

    local name=$(get_tech_name $TECH_STACK)
    echo -e "${GREEN}✓ 已选择技术栈: $name${NC}"
}

# 创建 .gitignore 文件
create_gitignore() {
    cat > .gitignore <<'EOF'
# Common

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local
.env.*.local

# Build outputs
dist/
build/
out/
*.log

# Dependencies
node_modules/
venv/
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
*.so

# Lock files（根据团队策略决定是否提交）
# package-lock.json  # Node.js（推荐提交）
# yarn.lock
# poetry.lock
# Pipfile.lock
# go.sum             # Go（推荐提交）
# Cargo.lock         # Rust（推荐提交）
# pom.xml            # Java/Maven（推荐提交）
# build.gradle      # Java/Gradle（推荐提交）

# Coverage
coverage/
.nyc_output/
*.cover
*.out

# Temporary files
tmp/
temp/
*.tmp
*.temp
.cache/

# Package files
*.tgz
*.zip
*.tar

# Test files
.npm
.pytest_cache/
.tox/
.hypothesis/
.mypy_cache/

# Version control
.git/
.svn/
.hg/

# Backup files
*.bak
*.backup
*~

# Database
*.db
*.sqlite
*.sqlite3

# Secrets
*.pem
*.key
*.crt
secrets/
secrets.yaml
secrets.yml

# Go
*.exe
*.test
*.out

# Rust
target/
Cargo.lock

# Java
*.class
*.jar
*.war
*.ear
hs_err_pid*
EOF
}

# 创建 CLAUDE.md 文件
create_claude_md() {
    cat > CLAUDE.md <<EOF
# $PROJECT_NAME

[项目简短描述，1-2句话]

---

## 项目概述

- **名称**: $PROJECT_NAME
- **描述**: [详细描述]
- **技术栈**: $(get_tech_name $TECH_STACK)
- **版本**: 1.0.0
- **语言**: [语言]

---

## 开发指南

### 环境要求

- [环境要求]

### 安装依赖

[技术栈特定的依赖安装命令]

### 运行项目

[技术栈特定的运行命令]

### 测试

[技术栈特定的测试命令]

---

## 技术细节

### 当前实现

[描述当前项目的主要功能和实现方式]

### 关键文件说明

- **主要文件**: [文件说明]

---

## 开发规范

### 编码标准

[编码标准和规范]

### 提交规范

使用 Conventional Commits 规范：
- feat: 添加新功能
- fix: 修复 bug
- docs: 更新文档
- style: 代码格式调整
- refactor: 重构代码
- perf: 性能优化
- test: 添加测试
- chore: 构建/工具链变动

---

## 当前任务与待办事项

### 已完成

- [x] 项目初始化

### 进行中

- [ ] [进行中的任务]

### 待办

- [ ] [待办任务]

---

## 开发历史与决策

### [日期] - [决策标题]
- **决策**: [决策内容]
- **原因**: [决策的原因]
- **影响**: [对项目的影响]

---

## 部署

### 开发环境

[开发环境配置]

### 生产环境

[生产环境配置]

---

## 常见问题

### Q: [问题]？

A: [解决方案]

---

*此文件由 Clawdbot 和 Claude Code 协同维护，记录项目的完整上下文。*
EOF
}

# 创建 .clawdbot 标记文件
create_clawdbot_marker() {
    cat > .clawdbot <<EOF
# Clawdbot Project Marker
# 此文件标识这是一个由 Clawdbot 创建的项目
# 请勿手动删除此文件

project_name=$PROJECT_NAME
tech_stack=$TECH_STACK
created_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
clawdbot_version=1.0.0
# session_id will be added by Clawdbot after first interaction
# session_id=
EOF
}

# 根据技术栈初始化项目
init_node_project() {
    if [ ! -f "package.json" ]; then
        cat > package.json <<EOF
{
  "name": "$PROJECT_NAME",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "node index.js",
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": [],
  "author": "",
  "license": "ISC"
}
EOF
    fi
    if [ ! -f "package-lock.json" ]; then
        npm install 2>/dev/null || true
    fi
}

init_python_project() {
    if [ ! -f "requirements.txt" ]; then
        echo "# Python Dependencies" > requirements.txt
        echo "" >> requirements.txt
        echo "# Add your dependencies below" >> requirements.txt
        echo "# example:" >> requirements.txt
        echo "# fastapi==0.100.0" >> requirements.txt
        echo "# uvicorn==0.22.0" >> requirements.txt
    fi
}

init_go_project() {
    if [ ! -f "go.mod" ]; then
        go mod init "$PROJECT_NAME" 2>/dev/null || cat > go.mod <<EOF
module $PROJECT_NAME

go 1.21
EOF
    fi
}

init_rust_project() {
    if [ ! -f "Cargo.toml" ]; then
        cat > Cargo.toml <<EOF
[package]
name = "$PROJECT_NAME"
version = "1.0.0"
edition = "2021"

[dependencies]
EOF
    fi
    
    # 创建 src 目录和 main.rs
    mkdir -p src
    if [ ! -f "src/main.rs" ]; then
        cat > src/main.rs <<EOF
fn main() {
    println!("Hello, world!");
}
EOF
    fi
}

init_java_project() {
    # 选择构建工具
    echo ""
    read -p "选择 Java 构建工具 [1=Gradle, 2=Maven, 3=Skip]: " java_tool
    case $java_tool in
        1)
            gradle init --type java-application --dsl kotlin --test-framework junit-jupiter 2>/dev/null || echo "Gradle 初始化失败，请手动配置"
            ;;
        2)
            echo "请手动创建 pom.xml 文件"
            ;;
        3)
            echo "跳过 Java 构建工具初始化"
            ;;
        *)
            echo "无效的选项，跳过构建工具初始化"
            ;;
    esac
}

init_general_project() {
    echo "初始化通用项目..."
    # 不需要特定的项目文件
}

# 检查参数
if [ -z "$1" ]; then
    echo -e "${RED}错误：缺少项目名称${NC}"
    echo ""
    show_help
    exit 1
fi

PROJECT_NAME=$1
PROJECT_DIR="$(pwd)/$PROJECT_NAME"

# 处理技术栈参数
if [ -z "$2" ]; then
    echo -e "${YELLOW}未指定技术栈，启动交互式选择...${NC}"
    select_tech_stack
else
    TECH_STACK=$2
    # 验证技术栈选项
    if ! is_valid_tech $TECH_STACK; then
        echo -e "${RED}错误：未知的技术栈 '$TECH_STACK'${NC}"
        echo ""
        echo "有效的技术栈选项："
        echo "  - node (Node.js/JavaScript)"
        echo "  - python (Python)"
        echo "  - go (Go)"
        echo "  - rust (Rust)"
        echo "  - java (Java)"
        echo "  - general (General/Other)"
        echo ""
        exit 1
    fi
fi

TECH_NAME=$(get_tech_name $TECH_STACK)
echo -e "${YELLOW}🚀 正在初始化项目: $PROJECT_NAME${NC}"
echo -e "${YELLOW}💻 技术栈: $TECH_NAME${NC}"

# 检查目录是否已存在
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${RED}错误：项目目录已存在: $PROJECT_DIR${NC}"
    exit 1
fi

# 创建项目目录
echo -e "${YELLOW}📁 创建项目目录...${NC}"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 创建模板文件
echo -e "${YELLOW}📋 创建模板文件...${NC}"
create_gitignore
create_claude_md
create_clawdbot_marker

# 初始化 Git 仓库
echo -e "${YELLOW}📦 初始化 Git 仓库...${NC}"
git init
git config user.email "clawdbot@local"
git config user.name "Clawdbot"

# 根据技术栈初始化项目文件
echo -e "${YELLOW}🔧 初始化 $TECH_NAME 项目...${NC}"
case $TECH_STACK in
    node)
        init_node_project
        ;;
    python)
        init_python_project
        ;;
    go)
        init_go_project
        ;;
    rust)
        init_rust_project
        ;;
    java)
        init_java_project
        ;;
    general)
        init_general_project
        ;;
esac

# 第一次提交
echo -e "${YELLOW}💾 第一次提交...${NC}"
git add .gitignore CLAUDE.md .clawdbot

# 根据技术栈添加项目文件
TECH_FILE=$(get_tech_file $TECH_STACK)
if [ -n "$TECH_FILE" ] && [ -f "$TECH_FILE" ]; then
    git add "$TECH_FILE"
fi

# 如果是 Rust 项目，还需要添加 src 目录
if [ "$TECH_STACK" = "rust" ] && [ -d "src" ]; then
    git add src/
fi

git commit -m "Initial commit: $TECH_NAME project structure"

# 完成
echo ""
echo -e "${GREEN}✅ 项目 $PROJECT_NAME 初始化完成！${NC}"
echo ""
echo -e "${BLUE}📁 项目位置:${NC} $PROJECT_DIR"
echo -e "${BLUE}💻 技术栈:${NC} $TECH_NAME"
echo ""
echo -e "${YELLOW}📝 下一步操作：${NC}"
echo "  1. 编辑 CLAUDE.md 以配置项目上下文"
echo "  2. $TECH_NAME 特定配置："

case $TECH_STACK in
    node)
        echo "     - 编辑 package.json 添加依赖和脚本"
        ;;
    python)
        echo "     - 编辑 requirements.txt 添加 Python 依赖"
        ;;
    go)
        echo "     - 编辑 go.mod 添加 Go 模块"
        ;;
    rust)
        echo "     - 编辑 Cargo.toml 添加 Rust 依赖"
        ;;
    java)
        echo "     - 编辑 pom.xml 或 build.gradle 添加依赖"
        ;;
    general)
        echo "     - 根据项目需要添加配置文件"
        ;;
esac

echo "  3. 开始开发（通过 Clawdbot 发送指令）"
echo ""
echo -e "${BLUE}💡 提示：${NC}"
echo "  - 项目已初始化 Git 仓库"
echo "  - 标准化的 .gitignore 已配置"
echo "  - CLAUDE.md 文件已创建，请根据项目内容修改"
echo "  - 项目文件已根据 $TECH_NAME 技术栈初始化"
echo ""
echo -e "${GREEN}🚀 准备开始开发！${NC}"
