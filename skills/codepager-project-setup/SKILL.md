---
name: codepager-project-setup
description: Create or find a CodePager project. When project name and root are supplied, immediately run scripts/setup_project.py from this skill; do not inspect memory or project files first.
---

# CodePager Project Setup

Use this skill only to attach a real project to CodePager.

## Fast Path

When the user gives both project name and project root, run this from the
installed `codepager-project-setup` skill directory as the next tool call:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/setup_project.py --name "<project-name>" --project-root <project-root>
```

Then reply and stop.

Do not list the project, inspect `CODEPAGER.md`, read memory, read project docs,
or read the bundled script first. The setup script creates or finds the project,
writes `<project-root>/CODEPAGER.md`, and updates the project map pointer.

## Token

Use runtime-provided `CODEPAGER_TOKEN`. If the installed skill directory has a
local `.env` with `CODEPAGER_ENV_FILE`, run the fast path without `--env`; the
helper follows that pointer. Add `--env <path>` only after a missing-token
failure or when the user directly gave the env path.

## Files

- `CODEPAGER.md` is public-safe and brutally short.
- `AGENTS.md` or `--project-map` gets only a tiny pointer to `CODEPAGER.md`.
- Never write CodePager project state into the agent runtime's root
  `AGENTS.md`, host-level workspace map, or identity/memory files.

This skill only bootstraps setup. Do not add watchers, repair dispatch,
incident handling, paging rules, or extra docs.
