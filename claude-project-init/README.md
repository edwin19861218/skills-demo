# claude-project-init

> **Initialize standardized Claude Code projects with Session Resume support**

让 Clawdbot 通过 Claude Code 进行项目开发，并实现 Session 复用以保持上下文连续性。

---

## 背景

### 为什么需要这个 Skill？

**问题**：Clawdbot 擅长对话理解和工具编排，但不擅长复杂的代码编辑。而 Claude Code 是专门的编程助手，但每次调用都是新 Session，不记得之前的对话。

**解决方案**：让 Clawdbot 调用 Claude Code，并通过这个 Skill 管理 Session ID，实现"持久记忆"。

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  钉钉/Telegram │ ─> │   Clawdbot   │ ─> │  Claude Code │
│   (用户)     │     │  (协调者)   │     │  (编程专家)  │
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                            ↓ sessions_spawn(resume=xxx)
                        保持同一 Session，AI 记得一切！
```

---

## 功能特性

| 特性 | 说明 |
|------|------|
| **多技术栈支持** | Node.js, Python, Go, Rust, Java, General |
| **项目初始化** | 自动创建标准化的项目结构 |
| **Git 集成** | 自动初始化 Git 仓库 |
| **Session 管理** | 自动保存和复用 Session ID |
| **上下文持久化** | CLAUDE.md 作为项目记忆载体 |

---

## 安装

### 方式一：在 Clawdbot 中加载（推荐）

```bash
# 在钉钉或 Telegram 中发送指令：
"加载 /YourPath/skills/claude-project-init 目录下的 claude-project-init skill"
```

### 方式二：手动安装

```bash
# 创建符号链接到 Clawdbot 的 skills 目录
ln -s /YourPath/skills/claude-project-init \
  ~/opt/homebrew/lib/node_modules/clawdbot/skills/claude-project-init

# 重启 Clawdbot
clawdbot gateway restart
```

### 验证安装

```bash
# 在钉钉中发送：
"查看已加载的 skills 列表"

# 确认输出中包含 claude-project-init
```

---

## 使用方法

### 初始化新项目

```bash
# 在项目目录运行
/YourPath/skills/claude-project-init/scripts/init-project.sh \
  my-project-name node
```

### 修改现有项目

```bash
# 进入项目目录
cd my-project-name

# 查看项目状态
/YourPath/skills/claude-project-init/scripts/modify-project.sh -v

# 生成调用指令
/YourPath/skills/claude-project-init/scripts/modify-project.sh "添加功能描述"
```

---

## 在 Clawdbot 中的使用

### 通过钉钉指令调用

**指令1：初始化项目**

```
使用 claude-project-init skill 创建一个名为 my-app 的 Node.js 项目
```

**指令2：添加功能（自动复用 Session）**

```
使用 claude-project-init skill 给 my-app 添加用户认证功能
```

**指令3：继续开发（同一 Session）**

```
使用 claude-project-init skill 给 my-app 添加单元测试
```

---

## Session 管理原理

### .clawdbot 文件

Skill 会在项目根目录创建 `.clawdbot` 标记文件：

```bash
project_name=my-app
tech_stack=node
created_at=2025-01-30T12:00:00Z
clawdbot_version=1.0.0
session_id=sess-20250130-abc-123  # Session ID 存储在这里
```

### Session Resume 流程

```
首次调用：
  读取 .clawdbot（无 session_id）
       ↓
  创建新 Session，返回 session_id
       ↓
  写入 .clawdbot 文件

后续调用：
  读取 .clawdbot（有 session_id）
       ↓
  使用 resume 参数复用 Session ⭐
       ↓
  Claude Code 记得完整的对话历史！
```

---

## 技术栈支持

| 技术栈 | 配置文件 | 初始化命令 | 运行命令 | 测试命令 |
|--------|----------|------------|----------|----------|
| **node** | package.json | `npm install` | `npm run dev` | `npm test` |
| **python** | requirements.txt | `pip install -r requirements.txt` | `python main.py` | `pytest` |
| **go** | go.mod | `go mod tidy` | `go run main.go` | `go test ./...` |
| **rust** | Cargo.toml | (自动) | `cargo run` | `cargo test` |
| **java** | pom.xml / build.gradle | (varies) | (varies) | `mvn test` / `gradle test` |
| **general** | (none) | (none) | (varies) | (varies) |

---

## 项目结构

初始化后的项目结构：

```
my-project/
├── .gitignore               # 标准 gitignore
├── .clawdbot               # 项目标记 + Session ID
├── CLAUDE.md               # 项目上下文文档
├── [技术栈特定配置]         # package.json, go.mod, etc.
└── src/                     # 源代码目录
```

---

## 文档

- **SKILL.md** - Skill 定义和完整使用文档
- **TEMPLATE_SYSTEM.md** - 模板系统深度文档
- **scripts/init-project.sh** - 项目初始化脚本
- **scripts/modify-project.sh** - 项目修改验证脚本

---

## 许可证

MIT License - Copyright (c) 2025 Edwin <edwin19861218@hotmail.com>

---

## 相关资源

- [Claude Agent SDK Session 文档](https://platform.claude.com/docs/en/agent-sdk/sessions)
- [Clawdbot 官方文档](https://docs.molt.bot/)
- [上一篇：5分钟打通钉钉与私有Clawdbot](https://mp.weixin.qq.com/s/VimmIR7Ma0WyFHNiA7jNAw)


---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## License

MIT
