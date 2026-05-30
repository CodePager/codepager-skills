---
name: codepager-onboarding
description: Map an existing project into CodePager by registering private route aliases and writing a compact project-local CodePager operating note.
---

# CodePager Onboarding

Use this after `codepager-project-setup` and before instrumentation needs paging.

## Fast Path

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/onboard.py --project-root <project-root> --route-name "<route name>"
```

Then report the route alias configuration and the updated `CODEPAGER.md`.

## Rules

- Use private aliases such as `agent:primary` and `human:primary`; never write
  chat IDs, bot tokens, webhooks, or private payloads to the repo.
- Keep project docs short and practical.
- Do not create sources or incidents. Use instrumentation for that.
