---
name: codepager-pager-instrumentation
description: Use when wiring a real app, watcher, or workflow into CodePager. Keeps checks and policy evaluation near the real source, emits typed evidence into CodePager with auth tokens, and documents proof commands without moving runtime responsibility into the dashboard.
---

# CodePager Pager Instrumentation

Use this skill when a project needs to emit evidence or incidents into CodePager.

## Goal

Instrument a real source without turning the dashboard into the runtime.

## Workflow

1. Read the target project's local harness and runbook first.
2. Identify the evidence source:
   - watchdog output
   - contact-form triage
   - queue freshness
   - workflow completion
   - semantic integrity check
3. Keep the check, policy evaluation, and immediate delivery path in the source project when possible.
4. Emit typed evidence or incident updates into CodePager using the project's auth token and the control-plane ingestion contract.
5. Add or update proof commands so a later agent can validate the source quickly.

## Guardrails

- Do not move outage-critical logic into the site.
- Do not store live per-project policy state in repo markdown.
- Use repo changes for code, tests, schemas, and proofs; use control-plane writes for live project configuration.
