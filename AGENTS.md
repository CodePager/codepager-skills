# CodePager Skills Repository

This repo is for public-facing CodePager skills, not the private control-plane app.

## Read First

- [ARCHITECTURE.md](/srv/pager/repos/codepager-skills/ARCHITECTURE.md) for repo shape and boundaries.
- [docs/harness-engineering.md](/srv/pager/repos/codepager-skills/docs/harness-engineering.md) for skill repo doctrine.
- [README.md](/srv/pager/repos/codepager-skills/README.md) for public setup notes.
- [MISTAKES.md](/srv/pager/repos/codepager-skills/MISTAKES.md), [LEARNINGS.md](/srv/pager/repos/codepager-skills/LEARNINGS.md), and [DESIRES.md](/srv/pager/repos/codepager-skills/DESIRES.md) before changing skill doctrine or evals.

Current skills:

- [codepager-project-setup](/srv/pager/repos/codepager-skills/skills/codepager-project-setup/SKILL.md)

Archived placeholders:

- [codepager-account-onboarding](/srv/pager/repos/codepager-skills/archive/placeholders/codepager-account-onboarding/ARCHIVED_SKILL.md)
- [codepager-pager-instrumentation](/srv/pager/repos/codepager-skills/archive/placeholders/codepager-pager-instrumentation/ARCHIVED_SKILL.md)

Validate:

- `./scripts/validate.sh`

Rules:

- `AGENTS.md` is a map, not a manual
- keep skill instructions concise
- keep only built and tested skills under `skills/`
- keep future-skill doctrine in `archive/placeholders/` until it earns an active implementation
- keep account and project state in the control plane, not in repo files
- when the product API exists, skills should write through it using tokens instead of inventing local state files
