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
    if not path or not Path(path).exists():
        return values
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def load_env(explicit, project_root=""):
    values = {}
    paths = [
        explicit,
        os.environ.get("CODEPAGER_ENV_FILE", ""),
        os.environ.get("CODEPAGER_ENV", ""),
        str(Path(project_root) / ".env") if project_root else "",
        str(Path(__file__).resolve().parents[1] / ".env"),
        ".env",
    ]
    for path in paths:
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
    doc = Path(root) / "CODEPAGER.md"
    if not doc.exists():
        raise SystemExit("CODEPAGER.md missing. Run codepager-project-setup first.")
    text = doc.read_text(encoding="utf-8")
    data = {}
    patterns = {
        "id": r"Project ID:\s*`([^`]+)`",
        "slug": r"Slug:\s*`([^`]+)`",
        "name": r"Name:\s*`([^`]+)`",
        "environment": r"Environment:\s*`([^`]+)`",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            data[key] = match.group(1)
    if not data.get("id"):
        raise SystemExit("CODEPAGER.md does not include a project id.")
    return data


def post_json(base_url, token, path, payload):
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "CodePagerInstrumentationSkill/1.0",
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
    except Exception as exc:
        return 0, {"ok": False, "error": str(exc)}


def spool(root, payload):
    spool_dir = Path(root) / ".codepager"
    spool_dir.mkdir(exist_ok=True)
    with (spool_dir / "spool.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def run_check(root, command, simulate_failure):
    started = time.time()
    if simulate_failure:
        return {
            "status": "failed",
            "exit_code": 42,
            "latency_ms": 0,
            "stdout": "",
            "stderr": "Simulated CodePager failure drill.",
        }
    proc = subprocess.run(command, cwd=root, shell=True, text=True, capture_output=True, timeout=300)
    return {
        "status": "ok" if proc.returncode == 0 else "failed",
        "exit_code": proc.returncode,
        "latency_ms": int((time.time() - started) * 1000),
        "stdout": redact(proc.stdout[-4000:]),
        "stderr": redact(proc.stderr[-4000:]),
    }


def run_private_command(command, incident_url, label):
    if not command:
        return {"status": "not_configured", "label": label}
    rendered = command.replace("{incident_url}", incident_url)
    proc = subprocess.run(rendered, shell=True, text=True, capture_output=True, timeout=120)
    return {
        "status": "sent" if proc.returncode == 0 else "failed",
        "label": label,
        "exit_code": proc.returncode,
        "stdout": redact(proc.stdout[-1000:]),
        "stderr": redact(proc.stderr[-1000:]),
    }


def update_codepager_doc(root, source_key, name, proof_command, route_name):
    path = Path(root) / "CODEPAGER.md"
    text = path.read_text(encoding="utf-8")
    block = "\n".join(
        [
            "## Checks",
            "<!-- CODEPAGER:CHECKS:BEGIN -->",
            f"- `{source_key}`: {name}. Proof: `{proof_command}`.",
            f"- Route: `{route_name}`. Private agent/human targets live outside git.",
            "<!-- CODEPAGER:CHECKS:END -->",
            "",
        ]
    )
    pattern = re.compile(r"\n?## Checks\n<!-- CODEPAGER:CHECKS:BEGIN -->.*?<!-- CODEPAGER:CHECKS:END -->\n?", re.S)
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
    parser.add_argument("--source-key", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--proof-command", required=True)
    parser.add_argument("--freshness-seconds", type=int, default=86400)
    parser.add_argument("--route-name", default="Primary escalation")
    parser.add_argument("--run-once", action="store_true")
    parser.add_argument("--simulate-failure", action="store_true")
    parser.add_argument("--page-on-failure", action="store_true")
    parser.add_argument("--human-escalation-seconds", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = str(Path(args.project_root).expanduser().resolve())
    env = load_env(args.env, root)
    token = env.get("CODEPAGER_TOKEN", "").strip()
    if not token:
        raise SystemExit("CODEPAGER_TOKEN missing. Store it in the agent runtime env, not in git.")
    base_url = (args.base_url or env.get("CODEPAGER_BASE_URL") or "https://app.codepager.com").rstrip("/")
    project = project_from_doc(root)

    source_payload = {
        "project_id": project["id"],
        "source_key": args.source_key,
        "name": args.name,
        "lane": "mission_critical",
        "source_type": "agent_check",
        "freshness_seconds": args.freshness_seconds,
        "proof_command": args.proof_command,
        "metadata": {"origin": "codepager-instrumentation", "protects": args.name},
    }
    status, source_result = post_json(base_url, token, "/api/sources/upsert", source_payload)
    if not source_result.get("ok"):
        spool(root, {"kind": "source_upsert", "payload": source_payload, "result": source_result})
        raise SystemExit(f"source upsert failed: {source_result.get('error', status)}")

    update_codepager_doc(root, args.source_key, args.name, args.proof_command, args.route_name)

    check = None
    heartbeat_result = None
    incident_result = None
    page_events = []
    if args.run_once or args.simulate_failure:
        check = run_check(root, args.proof_command, args.simulate_failure)
        heartbeat_payload = {
            "project_id": project["id"],
            "source_key": args.source_key,
            "status": "ok" if check["status"] == "ok" else "failed",
            "latency_ms": check["latency_ms"],
            "message": f"{args.name}: {check['status']}",
            "payload": {"result": {"evidence": {"kind": "command", "path": args.proof_command, "status": check["status"]}, "check": check}},
        }
        status, heartbeat_result = post_json(base_url, token, "/api/heartbeats", heartbeat_payload)
        if not heartbeat_result.get("ok"):
            spool(root, {"kind": "heartbeat", "payload": heartbeat_payload, "result": heartbeat_result})
            raise SystemExit(f"heartbeat failed: {heartbeat_result.get('error', status)}")

        if check["status"] != "ok":
            incident_payload = {
                "project_id": project["id"],
                "source_key": args.source_key,
                "dedupe_key": f"{args.source_key}.failure",
                "severity": "critical",
                "status": "open",
                "title": f"{args.name} failed",
                "summary": check["stderr"] or check["stdout"] or "Proof command failed.",
                "metadata": {"origin": "codepager-instrumentation", "route": args.route_name},
            }
            status, incident_result = post_json(base_url, token, "/api/incidents/upsert", incident_payload)
            if not incident_result.get("ok"):
                spool(root, {"kind": "incident", "payload": incident_payload, "result": incident_result})
                raise SystemExit(f"incident upsert failed: {incident_result.get('error', status)}")

            if args.page_on_failure:
                incident_url = base_url + incident_result["incident"]["url"]
                page_events.append(run_private_command(env.get("CODEPAGER_AGENT_PAGE_COMMAND", ""), incident_url, "agent"))
                if args.human_escalation_seconds > 0:
                    time.sleep(args.human_escalation_seconds)
                page_events.append(run_private_command(env.get("CODEPAGER_HUMAN_PAGE_COMMAND", ""), incident_url, "human"))
                for event in page_events:
                    event_type = event["label"] + "_page_" + event["status"]
                    post_json(base_url, token, "/api/incidents/events", {
                        "project_id": project["id"],
                        "incident_id": incident_result["incident"]["id"],
                        "event_type": event_type,
                        "actor_type": "agent",
                        "message": f"{event['label']} page {event['status']}",
                        "evidence": {"label": event["label"], "status": event["status"]},
                    })

    result = {
        "ok": True,
        "project": project,
        "source": source_result.get("source"),
        "heartbeat": heartbeat_result.get("heartbeat") if isinstance(heartbeat_result, dict) else None,
        "incident": incident_result.get("incident") if isinstance(incident_result, dict) else None,
        "pages": page_events,
    }
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"CodePager source ready: {args.source_key}")
        if result["heartbeat"]:
            print(f"Heartbeat: {result['heartbeat']['status']}")
        if result["incident"]:
            print(f"Incident: {base_url}{result['incident']['url']}")
        print("Stop now. Do not inspect unrelated memory or project files.")


if __name__ == "__main__":
    main()
