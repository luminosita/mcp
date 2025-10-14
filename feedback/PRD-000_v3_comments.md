## FR-12
### Issue
FR-12 lists a finite list of CLAUDE-*.md files. It should be more flexible. `Hybrid CLAUDE.md approach` is flexible and new specialized `CLAUDE.md` files can be added during development cycle to support additional concerns (security, message queues, authentication/authorization, etc)

```markdown
| **FR-12** | Coding standards documentation referencing specialized CLAUDE.md files | Must-have | Given a developer writing code, when they need style guidance, then coding standards document references CLAUDE-core.md, CLAUDE-tooling.md (including Taskfile commands), CLAUDE-testing.md, CLAUDE-typing.md, CLAUDE-validation.md, CLAUDE-architecture.md |
```

### Proposed Solution
- Update FR-12 with the flexibility in mind
- Evaluate if this update affects HLS and US stories
- Keep PRD at v3
