# Plan: CodePager Skills Roadmap

## Goal

Build CodePager skills one at a time so agents can safely set up projects,
instrument real reliability signals, and run CodePager-aware maintenance passes
without depending on private app code or one agent runtime.

CodePager's mission for these skills:

```text
CodePager gives watchdog agents, coding agents, and production automation a
clear way to detect failures, prove they are alive, and escalate real incidents.
```

## Current Truth

- `codepager-project-setup` is the only active installable skill.
- `codepager-account-onboarding` and `codepager-pager-instrumentation` are
  archived placeholders, not installable product.
- The repo has a small harness scaffold and one validation command.
- Project setup has been live-tested in one personal-agent runtime and has a
  plain-script fallback path, but it is not yet proven across random agents.
- No repair dispatch, external paging, watcher marketplace, or incident policy
  system exists in this repo.

## Constraints

- Keep each skill self-contained until consolidation is proven better.
- Keep `SKILL.md` files short and procedural.
- Put fragile or API-calling behavior in bundled scripts.
- Keep only built and tested installable skills under `skills/`.
- Do not add speculative skills to active paths.
- Do not write tokens, webhook URLs, paging credentials, or private incident
  payloads into project repos.
- Do not create CodePager-only abstractions before the product behavior exists.

## Skill Sequence

### 1. `codepager-project-setup`

Purpose: create or find a CodePager project and leave a public-safe project
pointer.

Built today:

- setup API call
- runtime/env token loading
- project-local `CODEPAGER.md`
- tiny `AGENTS.md` or `--project-map` pointer
- installed-skill and plain-script paths

Remaining before calling it product-ready:

- cleaner network, timeout, and invalid-response errors
- shell-safe generated command examples
- remove or implement unused CLI flags
- test against a plain fixture server or fake API
- test against at least one more agent/runtime mode

### 2. `codepager-instrumentation`

Purpose: help an agent wire a real project workflow, watcher, cron, queue,
worker, or background job into CodePager evidence.

This skill should be built only after the product has a stable ingestion
contract. It should answer:

- what signal is being protected
- where the check runs
- how it proves liveness
- what evidence it emits
- what local proof command validates it

It must not invent paging policy or move outage-critical runtime behavior into
the dashboard.

### 3. `codepager-onboarding`

Purpose: help map a larger user/project into CodePager once project setup and
instrumentation are real.

This may stay separate from instrumentation if separate skills use less context
and produce better agent behavior. Consolidate only after tests prove a single
skill is better.

It should help agents identify:

- projects
- protected workflows
- existing watchers or jobs
- proof commands
- missing native coverage
- safe next instrumentation steps

### 4. `codepager-pass`

Purpose: run during ordinary coding-agent work to keep CodePager truth aligned
with the project being changed.

This skill should check whether changes touched:

- background jobs
- cron jobs
- watchers
- queues or workers
- incident handling
- paging behavior
- CodePager docs or pointers

It should then refresh docs, run relevant proof, or tell the agent what
CodePager setup/instrumentation step is missing.

## Acceptance

For each active skill:

- `SKILL.md` stays short enough to read at trigger time.
- bundled scripts own deterministic behavior.
- `./scripts/validate.sh` proves repo shape and basic syntax.
- live eval evidence includes raw transcript or command output.
- plain-script fallback is tested when the skill performs setup or API work.
- `MISTAKES.md`, `LEARNINGS.md`, and `DESIRES.md` are updated when the loop
  teaches something durable.

## Proof Commands

```bash
./scripts/validate.sh
```

Parent proof:

```bash
cd /srv/pager && ./scripts/validate.sh
```

## Change Log

- 2026-05-30: Created plan after project setup work showed the repo needed an
  explicit multi-skill roadmap rather than scattered doctrine.

## Next Recommendation

Before another live project setup eval, harden `codepager-project-setup` around
script errors and command quoting. Then run one installed-skill eval and one
plain-script eval from a boring temporary project.
