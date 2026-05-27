---
name: codepager-project-setup
description: Use when an agent host needs to create or find a CodePager project using CODEPAGER_TOKEN from its environment or credentials file. Applies to OpenClaw, Codex, Jetclaw, personal agents, and server agents bootstrapping any real project.
---

# CodePager Project Setup

Use this skill on an agent host when the agent needs to attach a real system to
CodePager for the first time.

## Goal

Create or find one CodePager project from the agent's environment without
inventing repo-local project state.

## Required Environment

Read the target agent env safely. Do not print token values.

```text
CODEPAGER_BASE_URL=https://app.codepager.com
CODEPAGER_TOKEN=cp_live_...
```

If `CODEPAGER_TOKEN` is missing or invalid, ask the user to generate a scoped
setup token in `app.codepager.com/settings` and store it in the agent `.env`.

The project name should come from the user's message or the environment. A
natural request such as "set this project up in CodePager as Cal" is enough. If
the project name is missing or genuinely ambiguous, ask one short question and
stop. Derive the slug from the name unless the user gives one.

## Workflow

1. Read local instructions for the target agent/project first.
2. Find the credentials env file, usually `.env` or
   `~/.openclaw/credentials/assistant.env`.
3. Confirm the project name from the user's message, `CODEPAGER_PROJECT_NAME`,
   or an explicit CLI `--name`.
4. Run `PYTHONDONTWRITEBYTECODE=1 scripts/setup_project.py --name <project-name>`.
   Pass `--env <path-to-env>` only when auto-discovery will not find it.
5. Record the returned project slug in durable local notes if the target repo
   has such notes. Use `--json` only if you need the project id for an API call.
6. Stop after project setup. Do not add watchers, paging rules, repair dispatch,
   or human escalation in this skill.

## Reply Shape

Reply in one or two plain sentences. Say whether CodePager created or found the
project, and include the project name, slug, and environment. Do not include raw
`project_id=...`, `project_slug=...`, or `project_environment=...` lines unless
the user explicitly asks for machine-readable output.

## Guardrails

- Keep the full CodePager token in `.env` only.
- Do not commit `.env` or token values.
- Do not create local JSON/YAML as the source of CodePager project truth.
- This skill only bootstraps the project. Understanding, watching, and paging
  are separate steps.
