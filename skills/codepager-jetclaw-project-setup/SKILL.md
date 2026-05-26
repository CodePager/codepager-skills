---
name: codepager-jetclaw-project-setup
description: Use when installing CodePager onto a Jetclaw/OpenClaw personal agent so it can create or find its CodePager project using CODEPAGER_TOKEN, especially for bootstrapping projects like Cal from an agent .env.
---

# CodePager Jetclaw Project Setup

Use this skill on a Jetclaw/OpenClaw host when the agent needs to attach a real
system to CodePager for the first time.

## Goal

Create or find one CodePager project from the agent's environment without
inventing repo-local project state.

## Required Environment

Read the target agent `.env` safely. Do not print token values.

```text
CODEPAGER_BASE_URL=https://app.codepager.com
CODEPAGER_TOKEN=cp_live_...
CODEPAGER_PROJECT_NAME=Cal
CODEPAGER_PROJECT_SLUG=cal
```

If `CODEPAGER_TOKEN` is missing or invalid, ask the user to generate a scoped
setup token in `app.codepager.com/settings` and store it in the agent `.env`.

If project name or slug is missing, ask the user what project to set up. For
Cal, use `Cal` and `cal` unless the user says otherwise.

## Workflow

1. Read local instructions for the target agent/project first.
2. Confirm or ask for `CODEPAGER_PROJECT_NAME` and `CODEPAGER_PROJECT_SLUG`.
3. Run `scripts/setup_project.py --env <path-to-env>`.
4. Record the returned project id/slug in the agent's durable local notes if the
   target repo has such notes.
5. Stop after project setup. Do not add watchers, paging rules, repair dispatch,
   or human escalation in this skill.

## Guardrails

- Keep the full CodePager token in `.env` only.
- Do not commit `.env` or token values.
- Do not create local JSON/YAML as the source of CodePager project truth.
- This skill only bootstraps the project. Understanding, watching, and paging
  are separate steps.
