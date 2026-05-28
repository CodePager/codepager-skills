---
name: codepager-project-setup
description: Use when an agent host needs to create or find a CodePager project using CODEPAGER_TOKEN from its environment or credentials file. Applies to Codex, personal agents, server agents, and other agent runtimes bootstrapping any real project.
---

# CodePager Project Setup

Use this skill on an agent host when the agent needs to attach a real system to
CodePager for the first time.

## Goal

Create or find one CodePager project from the agent's environment without
inventing repo-local project state or changing the agent runtime's own map.

## Fast Path

If the user's message names the project, do not read broad workspace memory,
project docs, or the script source first. From this skill directory, run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/setup_project.py --name "<project-name>" --project-root <path-to-project-root>
```

Only add `--env <path>` if the token is not in the process environment and the
env file path is already known from the user's message, `CODEPAGER_ENV_FILE`,
local `.env`, or local runtime instructions.

Use `--project-root` to write a public-safe `CODEPAGER.md` cheat sheet at the
target project root and add a tiny pointer in the target project's own
`AGENTS.md`. If the project uses a different project-specific agent map, pass
`--project-map <path>`. If the command succeeds, reply and stop.

## Required Environment

Read the target agent env safely. Do not print token values.

```text
CODEPAGER_BASE_URL=https://app.codepager.com
CODEPAGER_TOKEN=cp_live_...
```

Instead of storing the token in the current `.env`, an agent may store:

```text
CODEPAGER_ENV_FILE=/path/to/runtime/credentials.env
```

If `CODEPAGER_TOKEN` is missing or invalid, ask the user to generate a scoped
setup token in `app.codepager.com/settings` and store it in the agent `.env`.

The project name should come from the user's message or the environment. A
natural request such as "set this project up in CodePager as Cal" is enough. If
the project name is missing or genuinely ambiguous, ask one short question and
stop. Derive the slug from the name unless the user gives one.

## Workflow

1. Prefer the fast path when the project name is clear.
2. Identify the real project root. Prefer the user's path, the current working
   directory when it is the project, or a small project-specific map that names
   the repo. Do not use the agent runtime's root workspace or host-level
   `AGENTS.md`.
3. Find the credentials env file from local instructions, shell environment, or
   the user's message. Common examples are `.env`, a runtime credentials file,
   or a path provided through `CODEPAGER_ENV_FILE`.
4. Confirm the project name from the user's message, `CODEPAGER_PROJECT_NAME`,
   or an explicit CLI `--name`.
5. Run the bundled setup script with `python3`, not `python`. Use the actual
   directory where this skill is installed:

   ```bash
   cd <installed-codepager-project-setup-skill-dir>
   PYTHONDONTWRITEBYTECODE=1 python3 scripts/setup_project.py --name <project-name> --project-root <path-to-project-root>
   ```

   Pass `--env <path-to-env>` when the token lives in a credentials file that
   is not already named by `CODEPAGER_ENV_FILE` or the current working
   directory's `.env`. Pass `--project-map <path>` only when the project's
   durable agent map is not `<project-root>/AGENTS.md`. The cheat sheet still
   goes at `<project-root>/CODEPAGER.md`.
6. Use `--json` only if you need the project id for an API call.
7. Stop after project setup. Do not add watchers, paging rules, repair dispatch,
   human escalation, or local documentation edits in this skill.

## Inspection Budget

- Do not read the bundled script source before the first run.
- Do not read broad memory files, project docs, or user profile files for a
  simple named project setup.
- If the first run fails because `CODEPAGER_TOKEN` is missing, inspect only
  likely env locations or the local runtime docs needed to find the env file.
- If the first run succeeds, do not run extra discovery commands.

## Project Files

The setup script writes two public-safe project files:

- `<project-root>/CODEPAGER.md`: the brutally short CodePager cheat sheet.
- `<project-root>/AGENTS.md` or `--project-map`: a tiny pointer to
  `CODEPAGER.md`.

`CODEPAGER.md` should only describe CodePager capabilities that actually exist.
Right now that is `codepager-project-setup`: create/find the project and
refresh the cheat sheet. Do not describe watcher, repair, incident, or paging
flows until those CodePager capabilities are built.

## Reply Shape

Reply in one or two plain sentences. Say whether CodePager created or found the
project, and include the project name, slug, and environment. Do not include raw
`project_id=...`, `project_slug=...`, or `project_environment=...` lines unless
the user explicitly asks for machine-readable output.

## Guardrails

- Keep the full CodePager token in `.env` only.
- Do not commit `.env` or token values.
- Do not create local JSON/YAML as the source of CodePager project truth.
- Only edit the target project's `CODEPAGER.md` and `AGENTS.md` or equivalent
  project-specific map with public-safe CodePager setup information.
- Never write CodePager project state into the agent runtime's root
  `AGENTS.md`, host-level workspace map, or generic assistant identity files.
- Do not edit memory files or broader project docs unless the user explicitly
  asks for documentation updates.
- This skill only bootstraps the project. Understanding, watching, and paging
  are separate steps.
