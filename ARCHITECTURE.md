# Architecture

## Purpose

This repo publishes CodePager skills that can be installed into coding agents,
watchdog agents, and personal agents without exposing private CodePager app
code.

CodePager gives agents and production automation a clear way to detect failures,
prove they are alive, and escalate real incidents.

## Shape

```text
AGENTS.md
ARCHITECTURE.md
DESIRES.md
LEARNINGS.md
MISTAKES.md
README.md
docs/exec-plans/active/codepager-skills-roadmap.md
docs/harness-engineering.md
scripts/validate.sh
skills/
  codepager-project-setup/
    SKILL.md
    scripts/setup_project.py
archive/placeholders/
```

## Flow

1. A human generates a setup token in CodePager.
2. An agent gets `CODEPAGER_TOKEN` through its runtime environment.
3. The active setup skill calls the CodePager project setup API.
4. The skill writes only project-local public-safe files:
   - `CODEPAGER.md`
   - `AGENTS.md`, or a project map passed with `--project-map`

## Boundaries

- `skills/` contains only built and tested installable skills.
- `archive/placeholders/` contains future-skill notes, not installable skills.
- Skill instructions stay short; deterministic behavior belongs in scripts.
- Skills must not write private tokens, paging credentials, webhook URLs, or
  incident payloads into repositories.
- Skills must not write project state into runtime-global agent maps or memory.
- Private CodePager control-plane code does not belong in this public repo.

## Canonical Patterns

- Every active skill has a `SKILL.md`.
- Repeated or fragile behavior goes in `scripts/`.
- Repo-level doctrine goes in `docs/`, not inside individual skills.
- One command, `./scripts/validate.sh`, proves the repo is shaped correctly.

## Hazards

- Placeholder skills in `skills/` look installable and mislead agents.
- Long `SKILL.md` files spend the agent context window before work starts.
- Agent-specific paths make public skills brittle.
- Missing network/error handling turns product setup failures into Python
  tracebacks.
- Generated docs that contain tokens or private incident data are security
  failures.
