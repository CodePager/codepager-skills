#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() {
  printf '%s\n' "$1" >&2
  exit 1
}

require_file() {
  [ -f "$1" ] || fail "missing required file: $1"
}

require_file AGENTS.md
require_file ARCHITECTURE.md
require_file DESIRES.md
require_file LEARNINGS.md
require_file MISTAKES.md
require_file README.md
require_file docs/exec-plans/active/codepager-skills-roadmap.md
require_file docs/harness-engineering.md
require_file skills/codepager-project-setup/SKILL.md
require_file skills/codepager-project-setup/scripts/setup_project.py

[ -x skills/codepager-project-setup/scripts/setup_project.py ] || fail "setup_project.py must be executable"

active_skills="$(find skills -mindepth 2 -maxdepth 2 -name SKILL.md | sort)"
[ "$active_skills" = "skills/codepager-project-setup/SKILL.md" ] || {
  printf 'unexpected active skills:\n%s\n' "$active_skills" >&2
  exit 1
}

if find . -path './.git' -prune -o -path './skills/*/SKILL.md' -prune -o -name SKILL.md -print | grep -q .; then
  echo "SKILL.md files outside active skills are discoverable as installable skills" >&2
  find . -path './.git' -prune -o -path './skills/*/SKILL.md' -prune -o -name SKILL.md -print >&2
  exit 1
fi

if find . \( -path '*/__pycache__' -o -name '*.pyc' \) -print | grep -q .; then
  echo "generated Python cache files must not be committed or left in the repo" >&2
  find . \( -path '*/__pycache__' -o -name '*.pyc' \) -print >&2
  exit 1
fi

if grep -RInE 'Jetclaw|OpenClaw|assistant\.env|/root/|\.openclaw|DroidFi|score_project_setup_trace' \
  AGENTS.md ARCHITECTURE.md README.md docs skills archive >/tmp/codepager-skills-runtime-specific.txt; then
  echo "runtime-specific or overfit strings found:" >&2
  cat /tmp/codepager-skills-runtime-specific.txt >&2
  exit 1
fi

skill_lines="$(wc -l < skills/codepager-project-setup/SKILL.md)"
[ "$skill_lines" -le 80 ] || fail "SKILL.md is too long for this small setup skill: $skill_lines lines"

python3 - <<'PY'
from pathlib import Path

script = Path("skills/codepager-project-setup/scripts/setup_project.py")
compile(script.read_text(encoding="utf-8"), str(script), "exec")
print("setup_project.py syntax ok")
PY

echo "codepager-skills validation ok"
