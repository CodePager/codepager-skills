# Learnings

Keep these notes practical. If a learning does not change future skill work, it
does not belong here.

## 2026-05-30 Skill Shape

`SKILL.md` should be short and procedural. It is loaded into the agent context
when the skill triggers, so it should say what to do next, not explain the whole
product.

Fragile, repeated, or API-calling behavior belongs in bundled scripts. For
`codepager-project-setup`, the script owns token loading, API calls,
project-root resolution, project-local file updates, and safety checks.

## 2026-05-30 Portable Setup Path

Not every agent runtime has skills. Project setup needs two supported paths:

- installed skill: run `scripts/setup_project.py` from the skill directory with
  `--project-root`
- plain script: run `setup_project.py` from the target project root

Both paths use `CODEPAGER_TOKEN` from runtime env or an env file. Neither path
should require agent-specific folders.

## 2026-05-30 Project-Local CodePager Truth

The durable project pointer belongs in the project being protected, not in the
agent runtime. The current pattern is:

- `CODEPAGER.md` for the public-safe CodePager cheat sheet
- `AGENTS.md` or `--project-map` for a tiny pointer to that cheat sheet

Project IDs and slugs are okay to commit. Tokens, webhook URLs, paging
credentials, and private incident payloads are not.

## 2026-05-30 Harness Size

This repo earned a small harness scaffold:

- `AGENTS.md`
- `ARCHITECTURE.md`
- `README.md`
- `docs/harness-engineering.md`
- `scripts/validate.sh`

It has not earned a larger docs tree, review personas, CI control plane, or
multi-skill framework yet.

## 2026-05-30 Active Skill Hygiene

Only built and tested installable skills belong under `skills/`. Archived
future-skill notes should not use the filename `SKILL.md`, because discovery
tools may treat any `SKILL.md` as installable.

## 2026-05-30 Multi-Skill Work Needs An Active Plan

Once the repo is about a sequence of skills, not just one skill, the roadmap
belongs in `docs/exec-plans/active/`. Keep the active plan focused on product
order, acceptance, proof, and what is deliberately not built yet.
