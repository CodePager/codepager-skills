# Install CodePager Project Setup

Use this when you want any coding agent to register a project in CodePager and
write the project-local `CODEPAGER.md` cheat sheet.

## What You Need

- A project root on disk.
- A CodePager setup token from `app.codepager.com/settings`.
- Python 3.

Do not commit the token.

## Option A: Agent Skill

Install or copy `skills/codepager-project-setup` into your agent's skill folder.
How you do that depends on the agent runtime.

Then give the agent:

```text
Set this project up in CodePager as <project name>. Use the
codepager-project-setup skill and use <absolute project root> as the project
root. Stop after setup.
```

The agent should run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/setup_project.py --name "<project name>" --project-root <absolute project root>
```

from the installed skill directory.

## Option B: Plain Script

If the agent does not support skills, copy
`skills/codepager-project-setup/scripts/setup_project.py` somewhere temporary.

From the project root:

```bash
CODEPAGER_TOKEN=cp_live_... PYTHONDONTWRITEBYTECODE=1 python3 /path/to/setup_project.py --name "<project name>"
```

Or point to an env file:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 /path/to/setup_project.py --name "<project name>" --env /path/to/agent.env
```

## Expected Files

The setup writes public-safe files only:

- `CODEPAGER.md`
- `AGENTS.md`, or a project map passed with `--project-map`

It must not edit an agent runtime's global `AGENTS.md`, identity files, memory
files, or credential files.

## Token Env

The setup script reads:

```text
CODEPAGER_BASE_URL=https://app.codepager.com
CODEPAGER_TOKEN=cp_live_...
```

It also supports an env pointer:

```text
CODEPAGER_ENV_FILE=/path/to/credentials.env
```

## Troubleshooting

- Missing token: generate a setup token in `app.codepager.com/settings`.
- Wrong project root: rerun with `--project-root <absolute path>`.
- No `AGENTS.md`: the script creates a minimal one.
- Existing `CODEPAGER.md`: the script refreshes it unless it appears to contain
  a token, in which case it refuses so secrets can be removed manually.
