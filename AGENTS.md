# CodePager Skills Repository

This repo is for public-facing CodePager skills, not the private control-plane app.

Current skills:

- [codepager-project-setup](/srv/pager/repos/codepager-skills/skills/codepager-project-setup/SKILL.md)

Archived placeholders:

- [codepager-account-onboarding](/srv/pager/repos/codepager-skills/archive/placeholders/codepager-account-onboarding/SKILL.md)
- [codepager-pager-instrumentation](/srv/pager/repos/codepager-skills/archive/placeholders/codepager-pager-instrumentation/SKILL.md)

Rules:

- keep skill instructions concise
- keep only built and tested skills under `skills/`
- keep future-skill doctrine in `archive/placeholders/` until it earns an active implementation
- keep account and project state in the control plane, not in repo files
- when the product API exists, skills should write through it using tokens instead of inventing local state files
