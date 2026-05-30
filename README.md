# CodePager Skills

Public skill collection for CodePager.

CodePager gives watchdog agents, coding agents, and production automation a
clear way to detect failures, prove they are alive, and escalate real incidents.

This repo stays separate from the private CodePager app so skills can be copied
into different agent runtimes without carrying private control-plane code.

## Shape

```text
AGENTS.md
README.md
skills/
  codepager-project-setup/
    SKILL.md
    scripts/setup_project.py
  codepager-instrumentation/
    SKILL.md
    scripts/instrument.py
  codepager-onboarding/
    SKILL.md
    scripts/onboard.py
  codepager-pass/
    SKILL.md
    scripts/codepager_pass.py
```

The private `CodePager/codepager-skills-harness` repo owns roadmap, evals,
future-skill doctrine, and private proof data.

## Active Skills

- [codepager-project-setup](skills/codepager-project-setup/SKILL.md): create or
  find a CodePager project, then write the project-local `CODEPAGER.md` cheat
  sheet and tiny `AGENTS.md` pointer.
- [codepager-onboarding](skills/codepager-onboarding/SKILL.md): register a
  private route alias map and keep only public-safe pager facts in
  `CODEPAGER.md`.
- [codepager-instrumentation](skills/codepager-instrumentation/SKILL.md): wire
  one real project check into CodePager evidence, heartbeat, incident, and page
  trail endpoints.
- [codepager-pass](skills/codepager-pass/SKILL.md): run during project changes
  to refresh CodePager evidence and open one deduped incident on proof failure.

## Setup Token

Generate a setup token in `app.codepager.com/settings`, provide it to the agent
runtime as `CODEPAGER_TOKEN`, and do not commit it.

For agents without skill support, run the bundled setup script from the project
root:

```bash
CODEPAGER_TOKEN=cp_live_... PYTHONDONTWRITEBYTECODE=1 python3 /path/to/setup_project.py --name "<project name>"
```

## Safety

- Skills must not write tokens, webhook URLs, paging credentials, or private
  incident payloads into project repos.
- Skills must not write project state into runtime-global agent maps or memory.
- Keep only built and tested installable skills under `skills/`.
