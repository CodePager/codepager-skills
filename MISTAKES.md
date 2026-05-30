# Mistakes

Mistakes are recorded so future skill work can add the smallest useful
guardrail instead of repeating the same failure.

## 2026-05-30 Overfit Project Setup To One Agent Runtime

The `codepager-project-setup` loop initially optimized for one live agent eval
instead of product readiness across random agent runtimes. The skill became
better at making that runtime do the expected action, but that did not prove it
would work for agents without the same memory, skill loader, env layout, or
session behavior.

Fix: keep the skill short, put deterministic behavior in the script, support a
plain-script path, and test both installed-skill and non-skill usage.

## 2026-05-30 Built A Trace Scorer Before The Product Bar Was Clear

A `score_project_setup_trace.py` script made the eval look objective while
quietly encouraging optimization for a narrow tool-call pattern. That was the
wrong center of gravity. The real bar is whether a random agent can safely
create/find a CodePager project and leave clear project-local instructions.

Fix: remove the scorer. Use raw artifacts, command output, file diffs, and live
agent behavior as evidence.

## 2026-05-30 Let Placeholder Skills Look Installable

Early placeholder skills for onboarding and pager instrumentation lived under
`skills/`, which made speculative doctrine look like product. Agents and humans
copy what exists; placeholders in active paths invite premature use.

Fix: only built and tested skills live under `skills/`. Future-skill notes live
under `archive/placeholders/` and must not be named `SKILL.md`.

## 2026-05-30 Wrote Project State Into The Wrong Level First

The early project pointer experiment wrote CodePager project state into an
agent-runtime-level map. That changed the agent environment instead of the
project being set up.

Fix: write public-safe state into the watched project only: `CODEPAGER.md` plus
a tiny project-local `AGENTS.md` or `--project-map` pointer.

## 2026-05-30 Added Harness Without The Active Roadmap

I added `ARCHITECTURE.md`, harness doctrine, validation, and repo-local
mistake/learning/desire files before adding an active exec plan for the actual
multi-skill roadmap. That left future agents to infer the product sequence from
scattered notes instead of one execution truth.

Fix: keep `docs/exec-plans/active/codepager-skills-roadmap.md` as the active
roadmap for project setup, instrumentation, onboarding, and CodePager pass work.
