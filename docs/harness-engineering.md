# Harness Engineering

CodePager skills are agent-first engineering infrastructure. Treat them like
production-facing systems even when the repo is small.

This doctrine is adapted from CodePager's harness-engineering notes.

## Thesis

Humans steer. Agents execute.

A skill repo should make the right agent behavior easy to discover, easy to run,
and easy to validate. Add harness only when it removes repeated confusion or
risk.

## Non-Negotiables

- `AGENTS.md` is a map, not a manual.
- Durable truth lives in the repo, close to the code that uses it.
- Every repo has one validation command.
- Every change leaves proof.
- Repeated mistakes become guardrails.
- Delete stale harness. Ceremony is slop too.

## Current Maturity

This repo is a small public product repo, not an agent factory.

Required scaffold:

```text
AGENTS.md
ARCHITECTURE.md
README.md
scripts/validate.sh
```

Optional only after repeated pain:

```text
docs/quality.md
docs/runbook.md
docs/exec-plans/active/
review personas
CI proof gates
```

Do not add extra docs, personas, skills, or CI because a larger repo needed
them.

## Skill Rules

- Prefer 5-10 strong skills over brittle micro-skills.
- Do not create a skill for something a short command explains.
- Keep `SKILL.md` short and procedural.
- Put fragile, repeated, or API-calling behavior in scripts.
- Keep future-skill doctrine out of `skills/` until it is built and tested.
- Test skills against real agent behavior and plain-script fallback behavior.

## Escalation Triggers

| Pain | Smallest useful addition |
| --- | --- |
| Agent misses setup | Fix `README.md` or `SKILL.md`; improve `scripts/validate.sh` |
| Agent edits wrong files | Clarify `ARCHITECTURE.md` boundaries |
| Same mistake repeats | Add a source check or script guardrail |
| Setup failure is hard to diagnose | Improve script error messages |
| Runtime behavior is opaque | Add command output first, logs next |
| Docs rot | Add a freshness check or delete the docs |

## Adoption Test

Before adding harness, answer:

```text
What repeated pain does this remove?
Who or what will read/run it?
How will we know it worked?
What existing thing can be deleted or simplified?
What is the smallest version that helps today?
```

Weak answers mean the harness should not be added yet.

## Proof Standard

For repo changes, record:

- files changed
- commands run
- validation output
- live agent or plain-script evidence when behavior changes
- known limitations

The goal is fewer decisions for the next agent, not more paperwork.
