# CodePager Skills

Public skill collection for CodePager.

CodePager gives watchdog agents, coding agents, and production automation a
clear way to detect failures, prove they are alive, and escalate real incidents.

This repo stays separate from the private CodePager app so skills can be copied
into different agent runtimes without carrying private control-plane code.

## Doctrine

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [docs/exec-plans/active/codepager-skills-roadmap.md](docs/exec-plans/active/codepager-skills-roadmap.md)
- [docs/harness-engineering.md](docs/harness-engineering.md)
- [MISTAKES.md](MISTAKES.md)
- [LEARNINGS.md](LEARNINGS.md)
- [DESIRES.md](DESIRES.md)

## Active Skills

- [codepager-project-setup](skills/codepager-project-setup/SKILL.md): create or
  find a CodePager project, then write the project-local `CODEPAGER.md` cheat
  sheet and tiny `AGENTS.md` pointer.

## Setup Token

Generate a setup token in `app.codepager.com/settings`, provide it to the agent
runtime as `CODEPAGER_TOKEN`, and do not commit it.

For agents without skill support, run the bundled setup script from the project
root:

```bash
CODEPAGER_TOKEN=cp_live_... PYTHONDONTWRITEBYTECODE=1 python3 /path/to/setup_project.py --name "<project name>"
```

## Archived Placeholders

The old `codepager-account-onboarding` and `codepager-pager-instrumentation`
placeholders are archived under `archive/placeholders/`. They should not be
installed until real product/API behavior exists and has been tested.

## Validate

```bash
./scripts/validate.sh
```
