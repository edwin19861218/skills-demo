# Claude Code Project Template System

This reference document provides deep dive into the template system for advanced usage patterns.

## Template Structure

### Core Components

```
.template/
├── .gitignore              # Universal gitignore for all tech stacks
├── CLAUDE.md.template      # Comprehensive project context template
└── README.md              # This documentation
```

### Technology-Specific Initialization

The `init-project.sh` script performs tech-specific setup:

#### Node.js
- Creates `package.json` with standard scripts
- Runs `npm install` to generate `package-lock.json`
- Default scripts: `start`, `dev`, `test`

#### Python
- Creates `requirements.txt` with dependency template
- Supports virtual environments (documented in CLAUDE.md)
- Compatible with pip, poetry, and pipenv

#### Go
- Creates `go.mod` with module initialization
- Uses Go 1.21+ as default
- Supports both `go run` and compiled builds

#### Rust
- Creates `Cargo.toml` with standard metadata
- Generates `src/` directory with `main.rs`
- Includes basic "Hello, world!" starter

#### Java
- Prompts for build tool (Gradle, Maven, or skip)
- Supports both `pom.xml` (Maven) and `build.gradle` (Gradle)
- Leaves manual configuration for flexibility

#### General
- Minimal scaffolding
- Suitable for: static sites, documentation, mixed-language projects
- Leaves full control to developer

## CLAUDE.md Structure

The `CLAUDE.md.template` follows a comprehensive structure designed for maximum context retention:

### Required Sections

1. **Project Overview** - Name, description, tech stack, version, language
2. **Development Guide** - Environment, installation, running, testing, structure
3. **Technical Details** - Current implementation, key files, APIs, data models
4. **Development Standards** - Coding standards, commit conventions, branching
5. **Current Tasks** - Completed, in progress, todo
6. **Development History** - Important decisions with dates and rationale
7. **Deployment** - Dev/staging/prod environments, containerization, env vars
8. **FAQ** - Common issues and solutions
9. **Extension Suggestions** - Future features, optimizations, improvements

### Context Retention Patterns

#### Decision Documentation

Document decisions with this pattern:

```markdown
### [Date] - [Decision Title]
- **Decision**: [What was decided]
- **Reason**: [Why this choice was made]
- **Impact**: [Consequences and trade-offs]
- **Alternatives Considered**: [Other options and why they were rejected]
```

**Example:**
```markdown
### 2025-01-30 - Database Choice
- **Decision**: Use PostgreSQL instead of MongoDB
- **Reason**: ACID compliance needed for financial transactions, better joins for reporting
- **Impact**: Requires SQL schema migrations, slower prototyping but better data integrity
- **Alternatives Considered**: MongoDB (rejected due to transaction limitations), MySQL (rejected due to licensing concerns)
```

#### Pattern Documentation

Capture reusable patterns that work well:

```markdown
### Pattern: Async Error Handling

When working with async operations, use this pattern:

```javascript
async function withErrorHandling(fn) {
  try {
    return await fn();
  } catch (error) {
    logger.error({ error, context: 'operation-name' });
    throw new UserFriendlyError('Something went wrong');
  }
}
```

**Why**: Centralizes error logging and transforms technical errors into user-friendly messages.
**Used in**: API routes, background jobs, event handlers.
```

#### Anti-Pattern Documentation

Document what NOT to do based on hard-won lessons:

```markdown
### Anti-Pattern: Direct Database Queries in Handlers

❌ **Don't**: Query database directly in HTTP handlers
```javascript
app.get('/users/:id', async (req, res) => {
  const user = await db.query('SELECT * FROM users WHERE id = ?', [req.params.id]);
  res.json(user);
});
```

✅ **Do**: Use repository layer for abstraction
```javascript
app.get('/users/:id', async (req, res) => {
  const user = await userRepository.findById(req.params.id);
  res.json(user);
});
```

**Why**: Violates single responsibility, makes testing difficult, couples business logic to HTTP layer.
**Lesson learned**: Had to refactor 15 handlers after introducing caching layer.
```

## Git Strategy

### Repository Isolation

Each project is an independent Git repository with these benefits:

- **Simplified history**: Clean, linear commit sequences per project
- **Independent versioning**: Projects can evolve independently
- **Easy deletion**: Remove a project without affecting others
- **Focused CI/CD**: Pipelines can be project-specific

### Commit Standards

Projects use Conventional Commits by default:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`

**Example:**
```
feat(api): add user authentication endpoint

Implement JWT-based authentication with refresh tokens.

- POST /api/auth/login
- POST /api/auth/refresh
- Middleware for protected routes

Closes #123
```

### Branch Naming

Recommended branch patterns:

- `feature/feature-name`
- `fix/bug-description`
- `refactor/component-name`
- `docs/update-topic`

## Collaboration Workflow

### Clawdbot ↔ Claude Code Bridge

```
User Request
    ↓
Clawdbot (analyzes & refines request)
    ↓
Claude Code (executes in project directory)
    ↓
Updates CLAUDE.md (captures decisions & patterns)
    ↓
Clawdbot (summarizes results)
    ↓
User
```

### Session Handoff

When transitioning between sessions:

1. **Review CLAUDE.md**: Current state, decisions, patterns
2. **Check task list**: What was done vs. pending
3. **Note context**: Important files, API endpoints, database schemas
4. **Start work**: Claude Code has full context instantly

### Conflict Resolution

When Clawdbot and Claude Code disagree:

- **Trust Claude Code** for implementation details (it's in the code)
- **Trust Clawdbot** for user intent and context
- **Document disagreements** in CLAUDE.md under "Known Issues"
- **Make decision** and record rationale

## Advanced Usage

### Multi-Project Dependencies

When projects depend on each other:

**Option 1: Git Submodules**
```bash
git submodule add <path-to-shared-lib> lib/shared
```

**Option 2: npm/local packages (Node.js)**
```json
{
  "dependencies": {
    "my-shared-lib": "file:../shared-lib"
  }
}
```

**Option 3: Workspace monorepo (Go)**
```go
module github.com/user/myproject
go 1.21

go 1.21
```

### Environment Switching

Manage multiple environments per project:

**CLAUDE.md documentation:**
```markdown
## Environments

### Development
- `.env.dev` - Local development config
- Database: `dev-db.local`

### Staging
- `.env.staging` - Staging config
- Database: `staging-db.company.com`

### Production
- `.env.prod` - Production config (never commit)
- Database: `prod-db.company.com`

### Loading Environment
```bash
# Node.js
node -r dotenv/config src/index.js dotenv_config_path=.env.dev

# Python
python-dotenv --env-file=.env.dev python main.py

# Go
go run -ldflags="-X main.Env=dev" main.go
```
```

### Testing Strategies

Document testing approach in CLAUDE.md:

```markdown
## Testing Strategy

### Unit Tests
- Framework: Jest (Node.js) / pytest (Python)
- Coverage target: 80%
- Run: `npm test` / `pytest`

### Integration Tests
- Docker Compose for external services
- Run: `npm run test:integration` / `pytest tests/integration/`

### E2E Tests
- Playwright for frontend
- Run: `npm run test:e2e`

### Manual Testing Checklist
- [ ] User registration flow
- [ ] Email verification
- [ ] Password reset
- [ ] API rate limiting
```

## Maintenance

### Template Updates

When improving the template system:

1. **Test thoroughly**: Create test projects with each tech stack
2. **Update docs**: Reflect changes in this README
3. **Version tracking**: Consider adding version numbers to template files
4. **Migration notes**: Document how existing projects should adapt

### Skill Updates

When this skill evolves:

1. **Test skill**: Use skill on real projects before publishing
2. **Update examples**: Ensure examples reflect current behavior
3. **Package skill**: Run `scripts/package_skill.py` to create distributable .skill file
4. **Document changes**: Add changelog entry to SKILL.md if major

## Troubleshooting

### Common Issues

**Issue**: `init-project.sh` fails with permission denied
```bash
chmod +x <path-to-script>/init-project.sh
```

**Issue**: Tech stack not recognized
- Valid stacks: `node`, `python`, `go`, `rust`, `java`, `general`
- Case-sensitive, lowercase only

**Issue**: Git not initialized
```bash
cd <project-root>/<project-name>
git init
git config user.email "clawdbot@local"
git config user.name "Clawdbot"
```

**Issue**: CLAUDE.md not recognized by Claude Code
- Ensure file is named exactly `CLAUDE.md` (uppercase)
- Check file is in project root, not a subdirectory
- Verify file has proper Markdown formatting

## Best Practices

1. **Update CLAUDE.md immediately**: Don't rely on memory
2. **Be specific with decisions**: Record rationale, not just the decision
3. **Delete irrelevant sections**: Remove unused tech stack sections from CLAUDE.md
4. **Commit frequently**: Save progress even if incomplete
5. **Use descriptive commit messages**: Future-you will thank you
6. **Test the init script**: Before relying on it for production projects
7. **Document workarounds**: When you hack something, write it down
