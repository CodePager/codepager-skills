#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

BLOCK_BEGIN_PREFIX = "<!-- CODEPAGER:PROJECT "
BLOCK_END_PREFIX = "<!-- /CODEPAGER:PROJECT "
CODEPAGER_DOC_NAME = "CODEPAGER.md"


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

    nested_env = values.get("CODEPAGER_ENV_FILE") or values.get("CODEPAGER_ENV")
    if nested_env:
        nested_path = os.path.expanduser(nested_env.strip())
        if os.path.exists(nested_path) and nested_path != chosen:
            nested_values = parse_env(nested_path)
            nested_values.update(values)
            values = nested_values

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


def agent_pointer_block(project):
    slug = project["slug"]
    return "\n".join(
        [
            "## CodePager",
            f"{BLOCK_BEGIN_PREFIX}{slug} -->",
            "",
            f"- CodePager cheat sheet: `{CODEPAGER_DOC_NAME}`.",
            f"- Project: `{project['name']}` (`{project['slug']}`, {project['environment']}), project id `{project['id']}`.",
            f"- Read `{CODEPAGER_DOC_NAME}` before doing CodePager-related work for this project.",
            "",
            f"{BLOCK_END_PREFIX}{slug} -->",
            "",
            "",
        ]
    )


def codepager_doc(project):
    command = f'PYTHONDONTWRITEBYTECODE=1 python3 scripts/setup_project.py --name "{project["name"]}" --project-root <project-root>'
    return "\n".join(
        [
            "# CODEPAGER.md",
            "",
            "Public-safe CodePager cheat sheet for this project.",
            "",
            "## Project",
            f"- Name: `{project['name']}`",
            f"- Slug: `{project['slug']}`",
            f"- Project ID: `{project['id']}`",
            f"- Environment: `{project['environment']}`",
            "",
            "## What Exists Today",
            "- `codepager-project-setup` creates or finds the CodePager project and refreshes this file.",
            "- Run it from the installed `codepager-project-setup` skill directory:",
            f"  `{command}`",
            "",
            "## Rules",
            "- Use runtime-provided `CODEPAGER_TOKEN`; never commit tokens, paging credentials, webhook URLs, or private incident payloads.",
            "- Do not invent watcher, repair, incident, or paging workflows from this file. Add them here only after the CodePager capability exists.",
            "- If this file and CodePager disagree, verify against the live CodePager project and refresh this file.",
            "",
        ]
    )


def is_runtime_global_map(path):
    resolved = Path(os.path.abspath(os.path.expanduser(path)))
    if resolved.name != "AGENTS.md":
        return False
    parent = resolved.parent
    grandparent = parent.parent
    return parent.name == "workspace" and grandparent.name.startswith(".")


def resolve_project_paths(project_root, project_map, agents_file, env):
    root = project_root or env.get("CODEPAGER_PROJECT_ROOT", "").strip()
    explicit_map = (
        project_map
        or env.get("CODEPAGER_PROJECT_MAP", "").strip()
        or agents_file
        or env.get("CODEPAGER_AGENTS_FILE", "").strip()
    )

    if not root and explicit_map:
        root = os.path.dirname(os.path.abspath(os.path.expanduser(explicit_map)))
    if not root:
        return "", "", ""

    root_abs = os.path.abspath(os.path.expanduser(root))
    agents_path = os.path.abspath(os.path.expanduser(explicit_map or os.path.join(root_abs, "AGENTS.md")))
    codepager_path = os.path.abspath(os.path.join(root_abs, CODEPAGER_DOC_NAME))

    if is_runtime_global_map(agents_path) or is_runtime_global_map(root_abs):
        raise SystemExit(
            "Refusing to write CodePager project state into a runtime-global workspace map. "
            "Pass --project-root for the real project repo."
        )

    for label, path in (("project map", agents_path), ("CODEPAGER.md", codepager_path)):
        try:
            inside_root = os.path.commonpath([root_abs, path]) == root_abs
        except ValueError:
            inside_root = False
        if not inside_root:
            raise SystemExit(f"{label} must live inside --project-root.")
    return root_abs, agents_path, codepager_path


def codepager_section_bounds(content):
    match = re.search(r"(?m)^## CodePager\s*$", content)
    if not match:
        return -1, -1
    next_heading = re.search(r"(?m)^## (?!CodePager\b).*$", content[match.end():])
    if not next_heading:
        return match.start(), len(content)
    return match.start(), match.end() + next_heading.start()


def upsert_agent_pointer(path, project):
    slug = project["slug"]
    expanded = os.path.expanduser(path)
    begin = f"{BLOCK_BEGIN_PREFIX}{slug} -->"
    end = f"{BLOCK_END_PREFIX}{slug} -->"
    block = agent_pointer_block(project)

    if os.path.exists(expanded):
        with open(expanded, "r", encoding="utf-8") as handle:
            content = handle.read()
    else:
        content = "# AGENTS.md\n\n"

    start = content.find(begin)
    if start != -1:
        stop = content.find(end, start)
        if stop == -1:
            raise SystemExit(f"Existing CodePager block in {expanded} is missing its end marker.")
        stop += len(end)
        while stop < len(content) and content[stop] in "\r\n":
            stop += 1
        replace_start = start
        heading_start = content[:start].rfind("\n## CodePager")
        if heading_start != -1:
            heading_start += 1
        elif content.startswith("## CodePager"):
            heading_start = 0
        if heading_start != -1 and content[heading_start:start].strip() == "## CodePager":
            replace_start = heading_start
        content = content[:replace_start].rstrip() + "\n\n" + block + content[stop:].lstrip()
    else:
        section_start, section_stop = codepager_section_bounds(content)
        if section_start != -1:
            existing = content[section_start:section_stop]
            if project["id"] in existing and project["slug"] in existing:
                content = content[:section_start].rstrip() + "\n\n" + block + content[section_stop:].lstrip()
            else:
                raise SystemExit(
                    f"{expanded} already has an unmarked CodePager section. "
                    "Review it manually instead of overwriting project instructions."
                )
        else:
            content = content.rstrip() + "\n\n" + block

    with open(expanded, "w", encoding="utf-8") as handle:
        handle.write(content)
    return expanded, True


def write_codepager_doc(path, project):
    expanded = os.path.expanduser(path)
    next_content = codepager_doc(project)
    if os.path.exists(expanded):
        with open(expanded, "r", encoding="utf-8") as handle:
            current = handle.read()
        if current == next_content:
            return expanded, False
        if "CODEPAGER_TOKEN=" in current or "cp_live_" in current:
            raise SystemExit(
                f"{expanded} appears to contain a token. Refusing to overwrite; remove secrets manually first."
            )

    with open(expanded, "w", encoding="utf-8") as handle:
        handle.write(next_content)
    return expanded, True


def main():
    parser = argparse.ArgumentParser(description="Create or find a CodePager project for an agent host.")
    parser.add_argument("--env", default="", help="Path to an agent env file. Defaults to CODEPAGER_ENV_FILE, CODEPAGER_ENV, or .env.")
    parser.add_argument("--base-url", default="", help="CodePager base URL. Defaults to CODEPAGER_BASE_URL or https://app.codepager.com.")
    parser.add_argument("--name", default="", help="Project name, for example Cal.")
    parser.add_argument("--slug", default="", help="Project slug. Defaults to a slugified project name.")
    parser.add_argument("--environment", default="", help="Project environment. Defaults to CODEPAGER_PROJECT_ENVIRONMENT or production.")
    parser.add_argument("--project-root", default="", help="Path to the real project repository/root. When set, writes <project-root>/CODEPAGER.md and updates <project-root>/AGENTS.md.")
    parser.add_argument("--project-map", default="", help="Path to a project-specific AGENTS.md/map file to point at CODEPAGER.md.")
    parser.add_argument("--agents-file", default="", help="Deprecated alias for --project-map. Must be project-specific, not a runtime-global AGENTS.md.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON including the project id.")
    parser.add_argument("--show-id", action="store_true", help="Include the project id in text output.")
    args = parser.parse_args()

    env_path, env = load_env(args.env)
    base_url = (args.base_url or env.get("CODEPAGER_BASE_URL") or "https://app.codepager.com").rstrip("/")
    token = env.get("CODEPAGER_TOKEN", "").strip()
    if not token:
        env_hint = args.env or env_path or "CODEPAGER_ENV_FILE, CODEPAGER_ENV, or .env"
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
    project_root, agents_file, codepager_file = resolve_project_paths(args.project_root, args.project_map, args.agents_file, env)
    agents_file_written = ""
    agents_file_changed = False
    codepager_file_written = ""
    codepager_file_changed = False
    if project_root:
        agents_file_written, agents_file_changed = upsert_agent_pointer(agents_file, project)
        codepager_file_written, codepager_file_changed = write_codepager_doc(codepager_file, project)

    result = {
        "ok": True,
        "action": action,
        "project": project,
        "env_file": env_path,
        "project_root": project_root,
        "agents_file": agents_file_written,
        "agents_file_changed": agents_file_changed,
        "codepager_file": codepager_file_written,
        "codepager_file_changed": codepager_file_changed,
    }
    if args.json:
        print(json.dumps(result, sort_keys=True))
        return

    print(f"CodePager project {action}: {project['name']} ({project['slug']}, {project['environment']}).")
    if agents_file_written:
        verb = "Updated" if agents_file_changed else "Verified"
        print(f"{verb} project map: {agents_file_written}")
    if codepager_file_written:
        verb = "Updated" if codepager_file_changed else "Verified"
        print(f"{verb} CodePager cheat sheet: {codepager_file_written}")
    if args.show_id:
        print(f"Project id: {project['id']}")


if __name__ == "__main__":
    main()
