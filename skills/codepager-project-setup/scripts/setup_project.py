#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request


def parse_env(path):
    values = {}
    if not path or not os.path.exists(path):
        return values
    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if key:
                values[key] = value
    return values


def candidate_env_paths(explicit):
    paths = []
    if explicit:
        paths.append(explicit)
    for key in ("CODEPAGER_ENV_FILE", "CODEPAGER_ENV"):
        value = os.environ.get(key, "").strip()
        if value:
            paths.append(value)
    paths.extend(
        [
            ".env",
            str(Path.home() / ".openclaw" / "credentials" / "assistant.env"),
            "/root/.openclaw/credentials/assistant.env",
        ]
    )

    seen = set()
    for path in paths:
        expanded = os.path.expanduser(path)
        if expanded not in seen:
            seen.add(expanded)
            yield expanded


def load_env(explicit):
    chosen = None
    values = {}
    for path in candidate_env_paths(explicit):
        if os.path.exists(path):
            chosen = path
            values.update(parse_env(path))
            break

    for key, value in os.environ.items():
        if key.startswith("CODEPAGER_"):
            values[key] = value
    return chosen, values


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "project"


def ask(label, default=""):
    prompt = f"{label}"
    if default:
        prompt += f" [{default}]"
    prompt += ": "
    if not sys.stdin.isatty():
        raise SystemExit(f"{label} is required. Add it to .env or rerun interactively.")
    answer = input(prompt).strip()
    return answer or default


def post_json(url, token, payload):
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "CodePagerProjectSetupSkill/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        try:
            payload = json.loads(error.read().decode("utf-8"))
        except Exception:
            payload = {"ok": False, "error": error.reason}
        return error.code, payload


def main():
    parser = argparse.ArgumentParser(description="Create or find a CodePager project for an agent host.")
    parser.add_argument("--env", default="", help="Path to the agent env file. Defaults to .env or ~/.openclaw/credentials/assistant.env.")
    parser.add_argument("--base-url", default="", help="CodePager base URL. Defaults to CODEPAGER_BASE_URL or https://app.codepager.com.")
    parser.add_argument("--name", default="", help="Project name, for example Cal.")
    parser.add_argument("--slug", default="", help="Project slug. Defaults to a slugified project name.")
    parser.add_argument("--environment", default="", help="Project environment. Defaults to CODEPAGER_PROJECT_ENVIRONMENT or production.")
    args = parser.parse_args()

    env_path, env = load_env(args.env)
    base_url = (args.base_url or env.get("CODEPAGER_BASE_URL") or "https://app.codepager.com").rstrip("/")
    token = env.get("CODEPAGER_TOKEN", "").strip()
    if not token:
        env_hint = args.env or env_path or ".env or ~/.openclaw/credentials/assistant.env"
        raise SystemExit(f"CODEPAGER_TOKEN is missing. Generate a setup token in app.codepager.com/settings and add it to {env_hint}.")

    name = args.name or env.get("CODEPAGER_PROJECT_NAME", "").strip()
    if not name:
        name = ask("CodePager project name")

    slug = args.slug or env.get("CODEPAGER_PROJECT_SLUG", "").strip() or slugify(name)
    environment = args.environment or env.get("CODEPAGER_PROJECT_ENVIRONMENT", "production").strip() or "production"
    status, payload = post_json(
        f"{base_url}/api/projects/setup",
        token,
        {"name": name, "slug": slug, "environment": environment},
    )

    if status in (401, 403):
        raise SystemExit("CodePager token was rejected. Generate a fresh project setup token and update the agent .env.")
    if not payload.get("ok"):
        raise SystemExit(f"CodePager project setup failed: {payload.get('error', 'unknown_error')}")

    project = payload["project"]
    action = "created" if payload.get("created") else "found"
    print(f"CodePager project {action}: {project['name']} ({project['slug']})")
    print(f"project_id={project['id']}")
    print(f"project_slug={project['slug']}")
    print(f"project_environment={project['environment']}")
    if env_path:
        print(f"env_file={env_path}")


if __name__ == "__main__":
    main()
