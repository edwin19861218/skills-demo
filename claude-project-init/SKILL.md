---
name: claude-project-init
description: Initialize standardized Claude Code projects with multi-stack support. ALL development MUST be done via Claude Code. Use when creating new Claude Code projects that need Git repository initialization, CLAUDE.md context files for memory retention, and technology-specific scaffolding for Node.js/Python/Go/Rust/Java/General stacks.
---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

# Claude Code Project Initializer

Initialize standardized Claude Code projects with proper structure, context retention, and multi-technology support.

## ⚠️ IMPORTANT: Claude Code REQUIRED

**ALL code development MUST be done via Claude Code.** Do not use direct file editing (`write`/`edit`) for code changes.

**When working on projects initialized with this skill:**

1. **Use `sessions_spawn` to invoke Claude Code** for all coding tasks
2. **Session Management**: Capture and reuse session IDs for continuous context
3. **Never use `write`/`edit` tools** directly for source code
4. **Claude Code manages the codebase** through its own mechanisms
5. **Clawdbot acts as coordinator** - sends tasks to Claude Code, receives results

### Session Reuse Pattern

**For optimal context retention, reuse sessions across interactions:**

```typescript
// First interaction - create session and capture ID
let sessionId: string | undefined
const response = query({
  prompt: "Initialize project and setup structure",
  options: { label: "my-project" }
})

for await (const message of response) {
  if (message.type === 'system' && message.subtype === 'init') {
    sessionId = message.session_id  // Save this ID
  }
}

// Subsequent interactions - reuse session
query({
  prompt: "Add user authentication feature",
  options: {
    resume: sessionId,  // Reuse for continuous context
    label: "my-project"
  }
})
```

**Benefits of session reuse:**
- ✅ Maintains conversation context across interactions
- ✅ Reduces token overhead (no need to repeat CLAUDE.md each time)
- ✅ Natural dialogue flow with Claude Code

---

## Quick Start

Initialize a new project:

```bash
# Interactive mode (prompts for tech stack)
./scripts/init-project.sh <project-name>

# Specify tech stack directly
./scripts/init-project.sh <project-name> <tech-stack>
```

**Tech stacks:** `node`, `python`, `go`, `rust`, `java`, `general`

**Examples:**
```bash
# Create project in current directory
./scripts/init-project.sh my-express-app node

# Create Python project
./scripts/init-project.sh my-fastapi-app python

# Create Go project
./scripts/init-project.sh my-go-api go
```

## Modifying Existing Projects

When working on an existing Clawdbot project, use the modify script:

```bash
# Navigate to project directory
cd <project-name>

# Verify project status
./scripts/modify-project.sh -v

# Show project information
./scripts/modify-project.sh -i

# Generate Claude Code invocation command
./scripts/modify-project.sh "your task description"
```

**The modify script:**
- Automatically detects Clawdbot projects (via `.clawdbot` marker)
- Validates project state (Git, CLAUDE.md, tech-specific files)
- Generates proper `sessions_spawn` commands for Claude Code
- Enforces the "use Claude Code only" rule

---

## Project Structure

Projects are created in the current directory with the following structure:

```
[project-name]/              # New project subdirectory
├── .gitignore               # Standardized gitignore
├── .clawdbot               # Project marker (identifies Clawdbot projects)
├── CLAUDE.md               # Project context (editable)
├── [tech-specific]          # package.json, requirements.txt, etc.
└── src/                    # Source code (Rust creates src/)
```

All files are generated automatically by the initialization script.

---

## Key Features

### Context Retention

Each project includes a `CLAUDE.md` file that serves as:
- **Project memory** - Stores decisions, patterns, and preferences across sessions
- **Development guide** - Contains tech stack-specific commands and workflows
- **Collaboration bridge** - Ensures consistency between Clawdbot and Claude Code

### Technology Support

| Stack | Config File | Init Command | Run Command | Test Command |
|-------|-------------|--------------|-------------|--------------|
| **node** | package.json | `npm install` | `npm run dev` / `npm start` | `npm test` |
| **python** | requirements.txt | `pip install -r requirements.txt` | `python main.py` | `pytest` |
| **go** | go.mod | `go mod tidy` | `go run main.go` | `go test ./...` |
| **rust** | Cargo.toml | (auto) | `cargo run` | `cargo test` |
| **java** | pom.xml / build.gradle | (varies) | (varies) | `mvn test` / `gradle test` |
| **general** | (none) | (none) | (varies) | (varies) |

### Git Integration

Every project is automatically initialized as an independent Git repository:
- Pre-configured with `clawdbot@local` identity
- Standardized `.gitignore` included
- Initial commit captures project scaffolding

---

## Workflow

### Creating New Projects

1. **Navigate to desired location** - `cd ~/dev/projects` or any directory
2. **Initialize project** - Run `./scripts/init-project.sh <project-name> <tech-stack>`
3. **Edit CLAUDE.md** - Customize project context, fill in project details
4. **Develop** - **USE CLAUDE CODE ONLY** - send tasks to Claude Code via `sessions_spawn`
5. **Iterate** - Update `CLAUDE.md` with decisions and patterns as you go

### Modifying Existing Projects

1. **Navigate to project directory** - `cd <project-name>`
2. **Verify project** - Run `./scripts/modify-project.sh -v` to check status
3. **Get task command** - Run `./scripts/modify-project.sh "your task"` for the proper invocation
4. **Execute via Claude Code** - Use the generated `sessions_spawn` command with session reuse
5. **Update CLAUDE.md** - Document any important decisions or changes

### Session Lifecycle Management

**Best practices for managing sessions across Clawdbot interactions:**

| Scenario | Approach | Reason |
|----------|----------|--------|
| **First interaction** | Create new session, save ID | Initialize context |
| **Same project, same session** | Reuse with `resume: sessionId` | Maintain context continuity |
| **Same project, fresh start** | Create new session (no `resume`) | Clean slate for new direction |
| **Experimenting** | Use `forkSession: true` | Branch without affecting original |

### How to Use Claude Code

**When Clawdbot receives a development task:**

```typescript
// First interaction - create new session
sessions_spawn(
  agentId="claude-code",
  task="Your task description here",
  label="project-name"
)
// Capture session_id from response for reuse

// Subsequent interactions - reuse session
sessions_spawn(
  agentId="claude-code",
  task="Your next task",
  label="project-name",
  resume: "<captured-session-id>"  // ← Reuse for continuity
)
```

**Claude Code will:**
- Read CLAUDE.md for context
- Access the project files
- Make code changes
- Report back to Clawdbot with results
- Return session ID for potential reuse

**Clawdbot will:**
- Coordinate with Claude Code
- Forward results to the user
- Update CLAUDE.md if needed
- **Store session ID for project** (enables context reuse)
- **Reuse session on subsequent interactions** (maintains conversation continuity)

---

## Reference Material

For detailed project specifications and advanced usage patterns, see [TEMPLATE_SYSTEM.md](references/TEMPLATE_SYSTEM.md).

---

## Session Storage Strategy

**Where to store session IDs:**

### Option 1: Project-Level Storage (Recommended)

Store session ID in `.clawdbot` marker file:

```bash
# .clawdbot file format
project_name=my-project
tech_stack=node
created_at=2025-01-30T12:00:00Z
clawdbot_version=1.0.0
session_id=<captured-session-id>  # ← Add this line
```

**Benefits:**
- Session ID travels with the project
- Automatic when navigating to project directory
- Survives Clawdbot restarts

### Option 2: Clawdbot Memory

Store session ID in Clawdbot's internal state:

```typescript
// In Clawdbot implementation
const projectSessions = new Map<string, string>()

function saveSessionId(projectName: string, sessionId: string) {
  projectSessions.set(projectName, sessionId)
}

function getSessionId(projectName: string): string | undefined {
  return projectSessions.get(projectName)
}
```

**Benefits:**
- Centralized management
- Easy to implement
- Works across multiple projects

### Option 3: External State File

Store in a separate JSON file:

```json
{
  "sessions": {
    "my-project": "session-abc-123",
    "another-project": "session-xyz-789"
  }
}
```

**Benefits:**
- Human-readable
- Easy to backup and version control
- Can store additional metadata

---

## Implementation Example

**Clawdbot pseudo-code for session management:**

```typescript
interface ProjectState {
  sessionId?: string
  projectName: string
  lastActivity: Date
}

const projectStates = new Map<string, ProjectState>()

async function executeProjectTask(projectName: string, task: string) {
  const state = projectStates.get(projectName) || { projectName, lastActivity: new Date() }

  const options: any = {
    agentId: "claude-code",
    task: task,
    label: projectName
  }

  // Reuse session if available
  if (state.sessionId) {
    options.resume = state.sessionId
  }

  // Execute task
  const response = await sessions_spawn(options)

  // Capture new session ID
  for await (const message of response) {
    if (message.type === 'system' && message.subtype === 'init') {
      state.sessionId = message.session_id
      state.lastActivity = new Date()
      projectStates.set(projectName, state)
      break
    }
  }

  return response
}
```

---

## Common Patterns

### Adding Dependencies

**Node.js (via Claude Code):**
```
Ask Claude Code to: "Install <package> package"
```

**Python (via Claude Code):**
```
Ask Claude Code to: "Install <package> package and update requirements.txt"
```

**Go (via Claude Code):**
```
Ask Claude Code to: "Add <package> dependency using go get"
```

**Rust (via Claude Code):**
```
Ask Claude Code to: "Add <package> crate using cargo"
```

### Project Context Updates

When making important decisions or discovering patterns, update `CLAUDE.md`:

```markdown
## Development History & Decisions

### 2025-01-30 - Architecture Decision
- **Decision**: Use FastAPI for backend API
- **Reason**: Async support, automatic docs, type hints
- **Impact**: All routes now defined in `src/api/`, requires Python 3.8+
```

This ensures future sessions maintain continuity and knowledge transfer.

### Multi-Session Development

**Approach 1: Session Reuse (Recommended for Continuity)**

When working on the same project with continuous context:

1. **First interaction**: Create session, capture and store session ID
2. **Update CLAUDE.md**: Document key decisions and patterns
3. **Next interactions**: Reuse session with `resume: sessionId`
4. **Continuous**: Claude Code maintains conversation context naturally

**Approach 2: Fresh Sessions (For New Directions)**

When starting a new direction or after a significant break:

1. **First session**: Initialize project and establish patterns
2. **Update CLAUDE.md**: Document key decisions and patterns
3. **Next session**: CLAUDE.md provides instant context
4. **Continuous**: Keep CLAUDE.md updated with each session's insights

**When to use each approach:**

| Scenario | Recommended Approach |
|----------|---------------------|
| Continuous development on same feature | Session Reuse |
| Bug fixes, small iterations | Session Reuse |
| New feature, different context | Fresh Session |
| After long break (context stale) | Fresh Session |
| Experimenting with alternatives | Fork Session |

---

## ⚠️ Enforcement Rules

**MANDATORY:**
- ✅ ALL code changes via `sessions_spawn(agentId="claude-code", ...)`
- ✅ Claude Code manages the project directory
- ✅ Clawdbot coordinates and communicates results
- ✅ Use `modify-project.sh` when working on existing Clawdbot projects
- ✅ **Store and reuse session IDs** for continuous project development

**FORBIDDEN:**
- ❌ Do NOT use `write` tool for source code files
- ❌ Do NOT use `edit` tool for source code files
- ❌ Do NOT manually edit files in IDE for this project type
- ❌ Do NOT use `exec` for file operations that should be done by Claude Code

**ALLOWED (Non-code operations):**
- ✅ `write`/`edit` for documentation files (README.md, docs/*, CLAUDE.md)
- ✅ `exec` for build/test commands (npm run, go test, etc.)
- ✅ `read` for inspection and debugging
- ✅ `sessions_send` for coordination
- ✅ `modify-project.sh` for project verification and task generation

---

## Notes

- **Directory isolation**: Each project lives in its own subdirectory to prevent conflicts
- **Claude Code integration**: ALL development is done through Claude Code sessions
- **Git independence**: Each project has its own Git repository
- **Context-first**: CLAUDE.md is the single source of truth for project memory
- **Workflow enforcement**: This skill enforces Claude Code usage for code changes

---

## Why Claude Code?

**Benefits of this enforced workflow:**

1. **Consistency**: Claude Code follows its own development patterns and best practices
2. **Context awareness**: Claude Code has full access to project state and history
3. **Tool integration**: Claude Code can use advanced tools (refactoring, testing, etc.)
4. **Session isolation**: Code changes happen in isolated sessions, reducing conflicts
5. **Memory retention**: CLAUDE.md provides persistent context across sessions

**This is not just a recommendation—it's a requirement for this project type.**
