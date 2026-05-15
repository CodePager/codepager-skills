---
name: codepager-account-onboarding
description: Use when onboarding a new user, account, or project into CodePager. Maps the user's real systems into projects, lanes, sources, policies, routes, and proofs, then writes that state into the CodePager control plane instead of inventing repo-local contract files.
---

# CodePager Account Onboarding

Use this skill when the task is to onboard a user or project into CodePager.

## Goal

Produce a clean control-plane record for the user's real systems.

## Workflow

1. Inventory the user's projects and public surfaces.
2. Split each project into mission_critical, maintenance, and urgent_inbox lanes only when those lanes are real.
3. For each source, capture:
   - evidence location
   - freshness expectation
   - owner context
   - proof commands
   - delivery routes
4. Write the state into the CodePager control plane using the available auth token or API credentials reference.
5. Do not create ad hoc repo files for thresholds, owners, or routes unless the task is explicitly about schemas or migrations.

## Guardrails

- Account and project definitions are control-plane data.
- Repo-local docs are for durable implementation truth and proof commands, not for pretending to be the source of live policy state.
- Keep the execution plane in the user's real apps and agents.
