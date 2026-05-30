# CodePager Skills Repository

This repo is for public-facing CodePager skills, not the private control-plane app.

## Read First

- [README.md](/srv/pager/repos/codepager-skills/README.md) for public setup notes.

Current skills:

- [codepager-project-setup](/srv/pager/repos/codepager-skills/skills/codepager-project-setup/SKILL.md)
- [codepager-onboarding](/srv/pager/repos/codepager-skills/skills/codepager-onboarding/SKILL.md)
- [codepager-instrumentation](/srv/pager/repos/codepager-skills/skills/codepager-instrumentation/SKILL.md)
- [codepager-pass](/srv/pager/repos/codepager-skills/skills/codepager-pass/SKILL.md)

Rules:

- `AGENTS.md` is a map, not a manual
- keep skill instructions concise
- keep only built and tested skills under `skills/`
- keep roadmap, evals, and future-skill doctrine in the private `codepager-skills-harness` repo
- keep account and project state in the control plane, not in repo files
- when the product API exists, skills should write through it using tokens instead of inventing local state files
