#!/usr/bin/env python3
import argparse
import json
import re
import sys


FORBIDDEN_COMMAND_PATTERNS = [
    r"\b(cat|sed|grep|rg|find|ls|nl|head|tail)\b.*\b(MEMORY|USER|SOUL|HEARTBEAT|CODEPAGER|AGENTS)\.md\b",
    r"\b(cat|sed|grep|rg|find|ls|nl|head|tail)\b.*\bmemory/",
    r"\b(cat|sed|grep|rg|find|ls|nl|head|tail)\b.*\b/srv/",
]


def read_jsonl(path):
    events = []
    with open(path, "r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            event["_line_no"] = line_no
            events.append(event)
    return events


def event_data(event):
    data = event.get("data")
    return data if isinstance(data, dict) else {}


def tool_name(event):
    return event_data(event).get("name", "")


def tool_command(event):
    arguments = event_data(event).get("arguments")
    if isinstance(arguments, dict):
        command = arguments.get("command", "")
        cwd = arguments.get("cwd", "")
        return f"cwd={cwd} command={command}"
    return ""


def tool_output(event):
    output = event_data(event).get("output", "")
    return output if isinstance(output, str) else ""


def is_tool_call(event):
    return event.get("type") == "tool.call"


def is_tool_result(event):
    return event.get("type") == "tool.result"


def is_failure(event):
    data = event_data(event)
    if data.get("isError") is True:
        return True
    result = data.get("result")
    if isinstance(result, dict):
        status = result.get("status")
        exit_code = result.get("exitCode")
        return status == "failed" or (exit_code not in (None, 0))
    return False


def find_skill_read(events, skill_name):
    for index, event in enumerate(events):
        if not is_tool_result(event):
            continue
        output = tool_output(event)
        if f"name: {skill_name}" in output or f"# {skill_name}" in output:
            return index
    return -1


def is_setup_command(command, setup_script, project_root):
    return setup_script in command and "--project-root" in command and project_root in command


def forbidden_reason(command):
    for pattern in FORBIDDEN_COMMAND_PATTERNS:
        if re.search(pattern, command):
            return pattern
    return ""


def score_trace(events, skill_name, setup_script, project_root, max_tool_calls):
    failures = []
    tool_calls = [event for event in events if is_tool_call(event)]
    failed_results = [event for event in events if is_tool_result(event) and is_failure(event)]
    if failed_results:
        failures.append(f"{len(failed_results)} failed tool result(s)")

    skill_index = find_skill_read(events, skill_name)
    if skill_index == -1:
        failures.append("skill file was not read")

    setup_call_indexes = []
    unnecessary_env_indexes = []
    for index, event in enumerate(events):
        if not is_tool_call(event):
            continue
        command = tool_command(event)
        if is_setup_command(command, setup_script, project_root):
            setup_call_indexes.append(index)
            if "--env" in command:
                unnecessary_env_indexes.append(index)

    if not setup_call_indexes:
        failures.append("setup command was not run")

    forbidden_between = []
    first_setup_index = setup_call_indexes[0] if setup_call_indexes else None
    if skill_index != -1 and first_setup_index is not None:
        for index in range(skill_index + 1, first_setup_index):
            event = events[index]
            if not is_tool_call(event):
                continue
            command = tool_command(event)
            reason = forbidden_reason(command)
            if reason:
                forbidden_between.append(
                    {
                        "line": event.get("_line_no"),
                        "command": command,
                        "reason": reason,
                    }
                )
        if forbidden_between:
            failures.append("forbidden pre-setup inspection after skill read")

    if unnecessary_env_indexes:
        failures.append("setup command passed --env even though project name/root fast path should not")
    if len(tool_calls) > max_tool_calls:
        failures.append(f"tool call count exceeded {max_tool_calls}")

    score = 10
    score -= min(3, len(failed_results))
    if skill_index == -1:
        score -= 2
    if not setup_call_indexes:
        score -= 4
    if forbidden_between:
        score -= min(3, len(forbidden_between))
    if unnecessary_env_indexes:
        score -= 1
    if len(tool_calls) > max_tool_calls:
        score -= min(2, len(tool_calls) - max_tool_calls)
    score = max(0, score)

    return {
        "ok": not failures,
        "score": score,
        "failures": failures,
        "tool_calls": len(tool_calls),
        "failed_tool_results": len(failed_results),
        "skill_read_line": events[skill_index].get("_line_no") if skill_index != -1 else None,
        "setup_call_lines": [events[index].get("_line_no") for index in setup_call_indexes],
        "forbidden_between_skill_and_setup": forbidden_between,
        "unnecessary_env_lines": [events[index].get("_line_no") for index in unnecessary_env_indexes],
    }


def main():
    parser = argparse.ArgumentParser(description="Score a project setup agent trace.")
    parser.add_argument("trace", help="JSONL trajectory or tool trace.")
    parser.add_argument("--skill-name", default="codepager-project-setup")
    parser.add_argument("--setup-script", default="scripts/setup_project.py")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--max-tool-calls", type=int, default=4)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = score_trace(
        read_jsonl(args.trace),
        args.skill_name,
        args.setup_script,
        args.project_root,
        args.max_tool_calls,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"score={report['score']}")
        print(f"ok={str(report['ok']).lower()}")
        print(f"tool_calls={report['tool_calls']}")
        print(f"failed_tool_results={report['failed_tool_results']}")
        print(f"skill_read_line={report['skill_read_line']}")
        print("setup_call_lines=" + ",".join(str(line) for line in report["setup_call_lines"]))
        for failure in report["failures"]:
            print(f"failure={failure}")
        for item in report["forbidden_between_skill_and_setup"]:
            print(f"forbidden_line={item['line']} reason={item['reason']} command={item['command']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
