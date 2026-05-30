# Desires

Context, tools, or product surfaces that would make future skill work more
reliable.

## Cross-Agent Eval Harness

We need a small eval harness that can run the same skill task through multiple
agent modes:

- installed skill runtime
- plain script from project root
- shell-only or minimal agent environment
- at least one non-OpenClaw runtime

The harness should preserve raw transcripts and artifacts without turning them
into a fake universal score.

## Public Setup API Contract

The setup script currently relies on the live project setup API behavior. A
short public contract for `/api/projects/setup` would make skill changes easier
to review:

- request fields
- response shape
- token expectations
- idempotency behavior
- error cases

## Token UX Contract

The repo would benefit from a stable product contract for setup tokens:

- where users generate them
- what scopes they carry
- whether they expire
- how agents should store them
- how revocation should be handled

## Plain Fixture Server

A tiny local fake CodePager setup API would let `scripts/validate.sh` test
network success, token rejection, malformed responses, and idempotent project
setup without touching production.

## Skill Packaging Matrix

As CodePager supports more agents, keep a compact matrix of how each runtime
installs and invokes skills. Do not put runtime-specific paths in `SKILL.md`;
use the matrix to design tests and examples.
