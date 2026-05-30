#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys
import time
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


def redact(text):
    return re.sub(r"cp_(?:live|test)_[A-Za-z0-9_\\-]+", "cp_[REDACTED]", text)


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
            "User-Agent": "CodePagerPassSkill/1.0",
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


def infer_command(root, explicit):
    if explicit:
        return explicit
    if (Path(root) / "scripts" / "validate.sh").exists():
        return "./scripts/validate.sh"
    raise SystemExit("No proof command found. Pass --proof-command.")


def scan_touched(root):
    proc = subprocess.run("git diff --name-only HEAD --", cwd=root, shell=True, text=True, capture_output=True)
    if proc.returncode != 0:
        return []
    interesting = []
    needles = ("cron", "watch", "worker", "queue", "incident", "pager", "codepager", "heartbeat", "background")
    for path in proc.stdout.splitlines():
        if any(needle in path.lower() for needle in needles):
            interesting.append(path)
    return interesting[:20]


def run_command(root, command):
    started = time.time()
    proc = subprocess.run(command, cwd=root, shell=True, text=True, capture_output=True, timeout=300)
    return {
        "status": "ok" if proc.returncode == 0 else "failed",
        "exit_code": proc.returncode,
        "latency_ms": int((time.time() - started) * 1000),
        "stdout": redact(proc.stdout[-4000:]),
        "stderr": redact(proc.stderr[-4000:]),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--source-key", default="codepager.pass")
    parser.add_argument("--name", default="CodePager pass")
    parser.add_argument("--proof-command", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = str(Path(args.project_root).expanduser().resolve())
    env = load_env(args.env, root)
    token = env.get("CODEPAGER_TOKEN", "").strip()
    if not token:
        raise SystemExit("CODEPAGER_TOKEN missing. Store it in the runtime env, not git.")
    base_url = (args.base_url or env.get("CODEPAGER_BASE_URL") or "https://app.codepager.com").rstrip("/")
    project = project_from_doc(root)
    command = infer_command(root, args.proof_command)
    touched = scan_touched(root)

    source_payload = {
        "project_id": project["id"],
        "source_key": args.source_key,
        "name": args.name,
        "lane": "maintenance",
        "source_type": "agent_pass",
        "freshness_seconds": 604800,
        "proof_command": command,
        "metadata": {"origin": "codepager-pass", "watches_changes": touched},
    }
    status, source = post_json(base_url, token, "/api/sources/upsert", source_payload)
    if not source.get("ok"):
        raise SystemExit(f"source upsert failed: {source.get('error', status)}")

    result = run_command(root, command)
    heartbeat = {
        "project_id": project["id"],
        "source_key": args.source_key,
        "status": "ok" if result["status"] == "ok" else "failed",
        "latency_ms": result["latency_ms"],
        "message": f"CodePager pass {result['status']}",
        "payload": {"result": {"evidence": {"kind": "command", "path": command, "status": result["status"]}, "check": result, "touched": touched}},
    }
    status, heartbeat_result = post_json(base_url, token, "/api/heartbeats", heartbeat)
    if not heartbeat_result.get("ok"):
        raise SystemExit(f"heartbeat failed: {heartbeat_result.get('error', status)}")

    incident = None
    if result["status"] != "ok":
        status, incident = post_json(base_url, token, "/api/incidents/upsert", {
            "project_id": project["id"],
            "source_key": args.source_key,
            "dedupe_key": "codepager.pass.failure",
            "severity": "warning",
            "status": "open",
            "title": "CodePager pass failed",
            "summary": result["stderr"] or result["stdout"] or "Project proof command failed.",
            "metadata": {"origin": "codepager-pass", "touched": touched},
        })
        if not incident.get("ok"):
            raise SystemExit(f"incident upsert failed: {incident.get('error', status)}")

    output = {"ok": result["status"] == "ok", "project": project, "source": source.get("source"), "heartbeat": heartbeat_result.get("heartbeat"), "incident": incident.get("incident") if isinstance(incident, dict) else None, "touched": touched}
    if args.json:
        print(json.dumps(output, sort_keys=True))
    else:
        print(f"CodePager pass: {result['status']}")
        print(f"Heartbeat: {heartbeat_result['heartbeat']['id']}")
        if touched:
            print("Touched reliability paths: " + ", ".join(touched))
        if incident:
            print(f"Incident: {base_url}{incident['incident']['url']}")
        print("Stop now. Do not inspect unrelated memory or project files.")
    sys.exit(0 if result["status"] == "ok" else 1)


if __name__ == "__main__":
    main()
