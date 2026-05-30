---
name: codepager-pass
description: Run a CodePager-aware maintenance pass after project changes, proving the project still works and refreshing heartbeat evidence.
---

# CodePager Pass

Use this during ordinary coding work when changes touch background jobs,
watchers, cron, queues, workers, incident handling, paging, or `CODEPAGER.md`.

## Fast Path

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/codepager_pass.py --project-root <project-root>
```

Then report whether proof passed and whether CodePager evidence was refreshed.

## Rules

- Read `CODEPAGER.md`; do not write secrets.
- Run the project proof command.
- Submit a heartbeat to CodePager.
- If proof fails, open/update one deduped incident.
