#!/bin/sh
# Clawdbot Project Modifier
# 检测并验证 Clawdbot 项目，强制使用 Claude Code 进行修改
#
# MIT License
# Copyright (c) 2025 Edwin <edwin19861218@hotmail.com>

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "描述: 检测当前目录是否为 Clawdbot 项目，并强制使用 Claude Code 进行修改"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -v, --verify   仅验证项目状态，不执行其他操作"
    echo "  -i, --info     显示项目信息"
    echo ""
    echo "工作流程:"
    echo "  1. 检测 .clawdbot 标记文件"
    echo "  2. 读取项目元数据"
    echo "  3. 验证项目状态"
    echo "  4. 输出 Claude Code 调用指令"
    echo ""
}

# 解析 .clawdbot 文件
parse_clawdbot_marker() {
    if [ ! -f ".clawdbot" ]; then
        return 1
    fi

    # 解析标记文件（跳过注释行）
    PROJECT_NAME=$(grep "^project_name=" .clawdbot | cut -d'=' -f2)
    TECH_STACK=$(grep "^tech_stack=" .clawdbot | cut -d'=' -f2)
    CREATED_AT=$(grep "^created_at=" .clawdbot | cut -d'=' -f2)
    CLAWDBOT_VERSION=$(grep "^clawdbot_version=" .clawdbot | cut -d'=' -f2)
    SESSION_ID=$(grep "^session_id=" .clawdbot | cut -d'=' -f2)

    export PROJECT_NAME TECH_STACK CREATED_AT CLAWDBOT_VERSION SESSION_ID
    return 0
}

# 获取技术栈显示名称
get_tech_name() {
    case $1 in
        node) echo "Node.js/JavaScript" ;;
        python) echo "Python" ;;
        go) echo "Go" ;;
        rust) echo "Rust" ;;
        java) echo "Java" ;;
        general) echo "General/Other" ;;
        *) echo "Unknown ($1)" ;;
    esac
}

# 显示项目信息
show_project_info() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}📋 Clawdbot 项目信息${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}项目名称:${NC}   $PROJECT_NAME"
    echo -e "${BLUE}技术栈:${NC}     $(get_tech_name $TECH_STACK)"
    echo -e "${BLUE}创建时间:${NC}   $CREATED_AT"
    echo -e "${BLUE}版本:${NC}       $CLAWDBOT_VERSION"
    if [ -n "$SESSION_ID" ]; then
        echo -e "${GREEN}Session ID:${NC} $SESSION_ID"
    else
        echo -e "${YELLOW}Session ID:${NC} 未设置 (首次交互后将自动添加)"
    fi
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# 验证项目状态
verify_project() {
    local has_error=0

    echo -e "${YELLOW}🔍 验证项目状态...${NC}"
    echo ""

    # 检查 Git 仓库
    if [ ! -d ".git" ]; then
        echo -e "${RED}  ✗ Git 仓库未初始化${NC}"
        has_error=1
    else
        echo -e "${GREEN}  ✓ Git 仓库已初始化${NC}"
    fi

    # 检查 CLAUDE.md
    if [ ! -f "CLAUDE.md" ]; then
        echo -e "${RED}  ✗ CLAUDE.md 文件缺失${NC}"
        has_error=1
    else
        echo -e "${GREEN}  ✓ CLAUDE.md 文件存在${NC}"
    fi

    # 检查 .gitignore
    if [ ! -f ".gitignore" ]; then
        echo -e "${YELLOW}  ⚠ .gitignore 文件缺失${NC}"
    else
        echo -e "${GREEN}  ✓ .gitignore 文件存在${NC}"
    fi

    # 检查技术栈特定文件
    case $TECH_STACK in
        node)
            if [ ! -f "package.json" ]; then
                echo -e "${YELLOW}  ⚠ package.json 文件缺失${NC}"
            else
                echo -e "${GREEN}  ✓ package.json 文件存在${NC}"
            fi
            ;;
        python)
            if [ ! -f "requirements.txt" ]; then
                echo -e "${YELLOW}  ⚠ requirements.txt 文件缺失${NC}"
            else
                echo -e "${GREEN}  ✓ requirements.txt 文件存在${NC}"
            fi
            ;;
        go)
            if [ ! -f "go.mod" ]; then
                echo -e "${YELLOW}  ⚠ go.mod 文件缺失${NC}"
            else
                echo -e "${GREEN}  ✓ go.mod 文件存在${NC}"
            fi
            ;;
        rust)
            if [ ! -f "Cargo.toml" ]; then
                echo -e "${YELLOW}  ⚠ Cargo.toml 文件缺失${NC}"
            else
                echo -e "${GREEN}  ✓ Cargo.toml 文件存在${NC}"
            fi
            ;;
        java)
            if [ ! -f "pom.xml" ] && [ ! -f "build.gradle" ] && [ ! -f "build.gradle.kts" ]; then
                echo -e "${YELLOW}  ⚠ Java 构建文件 (pom.xml/build.gradle) 缺失${NC}"
            else
                echo -e "${GREEN}  ✓ Java 构建文件存在${NC}"
            fi
            ;;
    esac

    echo ""

    # 检查 Git 状态
    if git rev-parse --git-dir > /dev/null 2>&1; then
        if [ -n "$(git status --porcelain)" ]; then
            echo -e "${YELLOW}  ⚠ 工作目录有未提交的更改${NC}"
            echo -e "${CYAN}    更改内容:${NC}"
            git status --short | sed 's/^/    /'
        else
            echo -e "${GREEN}  ✓ 工作目录干净${NC}"
        fi
    fi

    echo ""

    if [ $has_error -eq 1 ]; then
        return 1
    fi
    return 0
}

# 生成 Claude Code 调用指令
generate_claude_code_command() {
    local task_desc="$1"

    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}🚀 Claude Code 调用指令${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  重要：此项目必须通过 Claude Code 进行修改！${NC}"
    echo ""

    if [ -n "$SESSION_ID" ]; then
        echo -e "${GREEN}✓ 检测到现有 Session ID，将复用 session 以保持上下文连续性${NC}"
        echo ""
        echo -e "${BLUE}调用方式（复用现有 session）：${NC}"
        echo ""
        echo -e "${GREEN}sessions_spawn(${NC}"
        echo -e "${GREEN}  agentId=\"claude-code\",${NC}"
        echo -e "${GREEN}  task=\"$task_desc\",${NC}"
        echo -e "${GREEN}  label=\"$PROJECT_NAME\",${NC}"
        echo -e "${GREEN}  resume: \"$SESSION_ID\"${NC}"
        echo -e "${GREEN})${NC}"
        echo ""
        echo -e "${YELLOW}💡 如需创建全新 session，请删除 .clawdbot 中的 session_id 行${NC}"
    else
        echo -e "${YELLOW}⚠️  未检测到 Session ID，将创建新 session${NC}"
        echo ""
        echo -e "${BLUE}调用方式（创建新 session）：${NC}"
        echo ""
        echo -e "${GREEN}sessions_spawn(${NC}"
        echo -e "${GREEN}  agentId=\"claude-code\",${NC}"
        echo -e "${GREEN}  task=\"$task_desc\",${NC}"
        echo -e "${GREEN}  label=\"$PROJECT_NAME\"${NC}"
        echo -e "${GREEN})${NC}"
        echo ""
        echo -e "${YELLOW}💡 首次调用后，请将返回的 session_id 添加到 .clawdbot 文件${NC}"
    fi

    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# 主逻辑
main() {
    local mode="normal"
    local task_desc=""

    # 解析参数
    while [ $# -gt 0 ]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verify)
                mode="verify"
                shift
                ;;
            -i|--info)
                mode="info"
                shift
                ;;
            -t|--task)
                task_desc="$2"
                shift 2
                ;;
            *)
                task_desc="$1"
                shift
                ;;
        esac
    done

    # 检查是否在项目目录中
    if [ ! -f ".clawdbot" ]; then
        echo -e "${RED}错误：当前目录不是 Clawdbot 项目${NC}"
        echo -e "${YELLOW}提示：.clawdbot 标记文件不存在${NC}"
        echo ""
        echo -e "${BLUE}如果要创建新项目，请使用:${NC}"
        echo -e "  ${GREEN}init-project.sh <project-name> <tech-stack>${NC}"
        echo ""
        exit 1
    fi

    # 解析项目标记
    if ! parse_clawdbot_marker; then
        echo -e "${RED}错误：无法解析 .clawdbot 文件${NC}"
        exit 1
    fi

    # 显示项目信息
    show_project_info

    # 根据模式执行
    case $mode in
        info)
            exit 0
            ;;
        verify)
            verify_project
            exit $?
            ;;
    esac

    # 验证项目状态
    verify_project
    local verify_result=$?

    # 如果有任务描述，生成调用指令
    if [ -n "$task_desc" ]; then
        generate_claude_code_command "$task_desc"
    else
        echo -e "${YELLOW}📝 使用提示：${NC}"
        echo ""
        echo -e "  ${BLUE}查看项目信息:${NC}"
        echo -e "    ${GREEN}$0 -i${NC}"
        echo ""
        echo -e "  ${BLUE}验证项目状态:${NC}"
        echo -e "    ${GREEN}$0 -v${NC}"
        echo ""
        echo -e "  ${BLUE}生成 Claude Code 调用指令:${NC}"
        echo -e "    ${GREEN}$0 \"你的任务描述\"${NC}"
        echo ""
    fi

    # 返回验证结果
    if [ $verify_result -ne 0 ]; then
        echo -e "${RED}⚠️  项目验证失败，请先修复上述问题${NC}"
        exit 1
    fi

    exit 0
}

# 执行主逻辑
main "$@"
