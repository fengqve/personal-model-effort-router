"""Local CLI. Network/model execution belongs to an explicitly supplied adapter."""

import argparse
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .core import evaluate


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_runs(path):
    source = Path(path).read_text(encoding="utf-8")
    try:
        value = json.loads(source)
    except ValueError:
        value = None
    else:
        if isinstance(value, dict):
            return [value]
        if isinstance(value, list):
            return value
        raise ValueError("Evidence must be a JSON object, array or JSONL records")
    rows = []
    for line_number, line in enumerate(source.splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except ValueError as exc:
                raise ValueError("Invalid run JSON at line %s" % line_number) from exc
    return rows


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


def demo_data():
    """Entirely invented fixtures; never evidence about a real model."""
    candidates = [
        {"id": "small-low", "model": "fictional-small-v1", "effort": "low", "harness": "demo-v1"},
        {"id": "small-high", "model": "fictional-small-v1", "effort": "high", "harness": "demo-v1"},
        {"id": "large-high", "model": "fictional-large-v1", "effort": "high", "harness": "demo-v1"},
    ]
    catalog = {"schema_version": 1, "synthetic": True, "candidates": candidates,
               "fallback": "large-high", "policy": {"min_cases": 5, "min_pass_rate": 1.0, "max_age_days": 30}}
    task = {"id": "new-demo-task", "family": "bounded-edit", "risk": "low", "harness": "demo-v1",
            "rubric": "tests-and-review-v1", "classification_confirmed": True,
            "prompt": "Fictional task used to demonstrate routing only."}
    runs = []
    for index, candidate in enumerate(candidates):
        for case in range(6):
            runs.append({"id": "%s-%s" % (candidate["id"], case), "case_id": "fixture-%s" % case,
                         **{key: task[key] for key in ("family", "risk", "harness", "rubric")},
                         "candidate_id": candidate["id"], "model": candidate["model"], "effort": candidate["effort"],
                         "passed": index > 0 or case < 4, "total_cost_usd": [0.02, 0.08, 0.30][index],
                         "total_duration_seconds": [10, 30, 90][index],
                         "completed_at": datetime.now(timezone.utc).isoformat(),
                         "source": "synthetic", "evidence": "Invented fixture, no model was called."})
    return catalog, runs, task


def dispatch(args, catalog, runs, task, decision):
    if decision["simulation"]:
        raise ValueError("Synthetic decisions cannot be dispatched. Use observed evidence and a real catalog.")
    if decision["status"] == "review_required":
        emit(decision)
        return 2
    if decision["status"] == "fallback" and not args.allow_fallback:
        emit({**decision, "dispatch": "blocked: inspect fallback, then explicitly allow it"})
        return 2
    if not args.adapter:
        raise ValueError("dispatch requires --adapter followed by an executable and its arguments")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        raise ValueError("timeout must be a positive finite number")
    # Reserve output BEFORE execution: a typo or existing record must not trigger a model call.
    # A pending record is intentional: a crash must not suggest nothing happened or invite a retry.
    record_path = Path(args.record_to)
    with record_path.open("x", encoding="utf-8") as output_file:
        pending = {"status": "pending", "task_id": task["id"], "selected": decision["selected"],
                   "note": "Execution may have started. Inspect the adapter before retrying."}
        json.dump(pending, output_file, ensure_ascii=False, allow_nan=False)
        output_file.flush()
        request = {"schema_version": 1, "task": task, "selected": decision["selected"]}
        try:
            completed = subprocess.run(args.adapter, input=json.dumps(request, ensure_ascii=False),
                                       capture_output=True, text=True, timeout=args.timeout, check=False)
            if completed.returncode:
                raise ValueError("Adapter failed (exit %s); inspect it locally. No automatic retry." % completed.returncode)
            response = json.loads(completed.stdout)
            if not isinstance(response, dict):
                raise ValueError("Adapter must return a JSON object")
            candidate = decision["selected"]
            record = {"id": str(uuid4()), "case_id": task["id"],
                      **{key: task[key] for key in ("family", "risk", "harness", "rubric")},
                      "candidate_id": candidate["id"], "model": candidate["model"], "effort": candidate["effort"],
                      "completed_at": datetime.now(timezone.utc).isoformat(), "source": "observed",
                      **{key: response[key] for key in ("passed", "total_cost_usd", "total_duration_seconds", "evidence")}}
            # Validate adapter evidence against the same rules used for routing.
            evaluate(catalog, [record], task)
            output_file.seek(0)
            json.dump(record, output_file, ensure_ascii=False, indent=2, allow_nan=False)
            output_file.truncate()
        except (ValueError, KeyError, OSError, subprocess.TimeoutExpired) as exc:
            failure = {**pending, "status": "execution_unverified",
                       "note": "No accepted evidence recorded. Check the adapter before retrying; work or charges may exist."}
            output_file.seek(0)
            json.dump(failure, output_file, ensure_ascii=False, indent=2)
            output_file.truncate()
            raise ValueError("Adapter execution/result unverified; see reserved record. %s" % type(exc).__name__) from exc
    emit({"decision": decision, "record": str(record_path), "passed": record["passed"],
          "output": response.get("output")})
    return 0 if record["passed"] else 3


def main(argv=None):
    parser = argparse.ArgumentParser(description="Choose a model + reasoning effort from your task evidence.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="Offline simulation; no model calls, no performance claims")
    for name in ("route", "dispatch"):
        command = sub.add_parser(name)
        command.add_argument("--catalog", required=True)
        command.add_argument("--runs", required=True, nargs="+", help="JSON/JSONL files of complete task runs")
        command.add_argument("--task", required=True)
        command.add_argument("--allow-synthetic", action="store_true")
        if name == "dispatch":
            command.add_argument("--allow-fallback", action="store_true")
            command.add_argument("--record-to", required=True, help="New single-record JSON file; never overwritten")
            command.add_argument("--timeout", type=float, default=300)
            command.add_argument("--adapter", nargs=argparse.REMAINDER, help="Explicit local executable; place last")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            catalog, runs, task = demo_data()
            emit(evaluate(catalog, runs, task, allow_synthetic=True))
            return 0
        catalog, task = load(args.catalog), load(args.task)
        runs = [run for path in args.runs for run in read_runs(path)]
        decision = evaluate(catalog, runs, task, allow_synthetic=args.allow_synthetic)
        if args.command == "route":
            emit(decision)
            return 2 if decision["status"] == "review_required" else 0
        return dispatch(args, catalog, runs, task, decision)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print("fitmytask: %s" % exc, file=sys.stderr)
        return 1
