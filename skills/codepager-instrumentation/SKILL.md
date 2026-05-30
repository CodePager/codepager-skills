---
name: codepager-instrumentation
description: Register a real project check with CodePager, run its proof command, submit heartbeat evidence, and record a narrow incident/page trail on failure.
---

# CodePager Instrumentation

Use this skill when a project already has CodePager setup and needs one real
check wired into CodePager evidence.

## Fast Path

When the user gives a project root and check details, run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/instrument.py --project-root <project-root> --source-key <source-key> --name "<check name>" --proof-command "<command>" --run-once
```

For a failure drill, add:

```bash
--simulate-failure --page-on-failure
```

Then report the source, heartbeat, and incident/page result.

## Rules

- Read `<project-root>/CODEPAGER.md` for project id/slug.
- Use runtime-provided `CODEPAGER_TOKEN`; never write tokens or private target refs to git.
- Keep the check in the real project. CodePager receives evidence; it is not the runtime.
- Do not invent broad policy, marketplace, or repair workflows.
