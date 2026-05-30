#!/usr/bin/env python3
import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path


def parse_env(path):
    values = {}
    if path and Path(path).expanduser().exists():
        for raw in Path(path).expanduser().read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip("'\"")
    return values


def load_env(explicit, project_root=""):
    values = {}
    for path in [
        explicit,
        os.environ.get("CODEPAGER_ENV_FILE", ""),
        os.environ.get("CODEPAGER_ENV", ""),
        str(Path(project_root) / ".env") if project_root else "",
        str(Path(__file__).resolve().parents[1] / ".env"),
        ".env",
    ]:
        if path and Path(os.path.expanduser(path)).exists():
            values.update(parse_env(os.path.expanduser(path)))
            break
    nested = values.get("CODEPAGER_ENV_FILE") or values.get("CODEPAGER_ENV")
    if nested and Path(os.path.expanduser(nested)).exists():
        nested_values = parse_env(os.path.expanduser(nested))
        nested_values.update(values)
        values = nested_values
    for key, value in os.environ.items():
        if key.startswith("CODEPAGER_"):
            values[key] = value
    return values


def project_from_doc(root):
    path = Path(root) / "CODEPAGER.md"
    if not path.exists():
        raise SystemExit("CODEPAGER.md missing. Run codepager-project-setup first.")
    text = path.read_text(encoding="utf-8")
    project = {}
    for key, pattern in {
        "id": r"Project ID:\s*`([^`]+)`",
        "slug": r"Slug:\s*`([^`]+)`",
        "name": r"Name:\s*`([^`]+)`",
    }.items():
        match = re.search(pattern, text)
        if match:
            project[key] = match.group(1)
    if not project.get("id"):
        raise SystemExit("CODEPAGER.md does not include a project id.")
    return project


def post_json(base_url, token, path, payload):
    request = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "CodePagerOnboardingSkill/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        try:
            return error.code, json.loads(error.read().decode("utf-8"))
        except Exception:
            return error.code, {"ok": False, "error": error.reason}


def update_doc(root, route_name, agent_first_seconds, human_after_seconds):
    path = Path(root) / "CODEPAGER.md"
    text = path.read_text(encoding="utf-8")
    block = "\n".join(
        [
            "## Pager",
            "<!-- CODEPAGER:PAGER:BEGIN -->",
            f"- Route: `{route_name}`.",
            f"- Agent-first window: `{agent_first_seconds}` seconds.",
            f"- Human escalation after: `{human_after_seconds}` seconds.",
            "- Route targets and secrets live outside git.",
            "<!-- CODEPAGER:PAGER:END -->",
            "",
        ]
    )
    pattern = re.compile(r"\n?## Pager\n<!-- CODEPAGER:PAGER:BEGIN -->.*?<!-- CODEPAGER:PAGER:END -->\n?", re.S)
    if pattern.search(text):
        text = pattern.sub("\n" + block, text).rstrip() + "\n"
    else:
        text = text.rstrip() + "\n\n" + block
    path.write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--route-name", default="Primary escalation")
    parser.add_argument("--agent-ref", default="")
    parser.add_argument("--human-ref", default="")
    parser.add_argument("--agent-first-seconds", type=int, default=0)
    parser.add_argument("--human-after-seconds", type=int, default=300)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = str(Path(args.project_root).expanduser().resolve())
    env = load_env(args.env, root)
    token = env.get("CODEPAGER_TOKEN", "").strip()
    if not token:
        raise SystemExit("CODEPAGER_TOKEN missing. Store it in the runtime env, not git.")
    base_url = (args.base_url or env.get("CODEPAGER_BASE_URL") or "https://app.codepager.com").rstrip("/")
    project = project_from_doc(root)
    agent_ref = args.agent_ref or env.get("CODEPAGER_AGENT_TARGET_REF", "agent:primary")
    human_ref = args.human_ref or env.get("CODEPAGER_HUMAN_TARGET_REF", "human:primary")
    payload = {
        "project_id": project["id"],
        "name": args.route_name,
        "match": {"project_slug": project.get("slug", "")},
        "escalation": {
            "agent_first_seconds": max(0, args.agent_first_seconds),
            "human_after_seconds": max(0, args.human_after_seconds),
        },
        "targets": [
            {"target_type": "agent_alias", "target_ref": agent_ref, "priority": 10},
            {"target_type": "human_alias", "target_ref": human_ref, "priority": 20},
        ],
    }
    status, result = post_json(base_url, token, "/api/routes/upsert", payload)
    if not result.get("ok"):
        raise SystemExit(f"route upsert failed: {result.get('error', status)}")
    update_doc(root, args.route_name, max(0, args.agent_first_seconds), max(0, args.human_after_seconds))
    output = {"ok": True, "project": project, "route": result["route"]}
    if args.json:
        print(json.dumps(output, sort_keys=True))
    else:
        print(f"CodePager route ready: {args.route_name}")
        print("Private targets are aliases only; no secrets were written.")
        print("Stop now. Do not inspect unrelated memory or project files.")


if __name__ == "__main__":
    main()
