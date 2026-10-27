# Evidence format v1

The bundled helper has a synthetic `demo`; it never calls a model. Published example records are not real task evidence.

## Catalog

```json
{
  "schema_version": 1,
  "synthetic": false,
  "candidates": [
    {"id": "baseline", "model": "YOUR_EXACT_MODEL", "effort": "YOUR_SUPPORTED_EFFORT", "harness": "your-harness-v1"}
  ],
  "fallback": "baseline",
  "policy": {"min_cases": 5, "min_pass_rate": 1.0, "max_age_days": 30}
}
```

Replace placeholders with your actual deployment. No model names or supported effort values are inferred. The fallback must reference a candidate. New providers, model snapshots, service tiers, price accounting, prompts, tool versions and context strategies need a new harness/configuration where relevant. Keep catalogs and evidence versioned together. Do not change a configuration in place and reuse its old evidence.

## Task

```json
{
  "id": "new-case-001",
  "family": "bounded-edit",
  "risk": "low",
  "harness": "your-harness-v1",
  "rubric": "tests-and-review-v1",
  "classification_confirmed": true,
  "prompt": "The task content supplied to your execution adapter",
  "max_mean_cost_usd": 1.0,
  "max_mean_duration_seconds": 180
}
```

Risk is `low`, `medium` or `high`. Families and rubrics are defined by you, not by keyword heuristics in this library. Set classification confirmation false if the task is unknown, mixed or ambiguous. Use a stable case ID for the same frozen task; a materially changed input is a new case. Optional limits refer to historical means, not enforced per-call caps. Additional task fields (such as frozen input paths) are forwarded to your adapter.

## Complete task record

```json
{
  "id": "unique-attempt-id",
  "case_id": "frozen-case-001",
  "family": "bounded-edit",
  "risk": "low",
  "harness": "your-harness-v1",
  "rubric": "tests-and-review-v1",
  "candidate_id": "baseline",
  "model": "YOUR_EXACT_MODEL",
  "effort": "YOUR_SUPPORTED_EFFORT",
  "passed": true,
  "configuration_confirmed": true,
  "total_cost_usd": null,
  "total_duration_seconds": null,
  "completed_at": "2026-10-27T00:00:00Z",
  "source": "observed",
  "evidence": "private/evidence/frozen-case-001/acceptance.md"
}
```

This is a schema illustration, not an actual run. `passed` must come from acceptance checks, not the model's claim of success. Include all subcalls, retries, failed attempts, classification/evaluation and coordination costs in the task total where incurred. Record the whole task's elapsed duration, not the sum of parallel child durations. If accounting is incomplete, use null and document the gap in the referenced artifact. Human review/rework should be described there, including whether its elapsed time and monetary valuation are included.

`source` is `observed` or `synthetic`; IDs must be unique. Evidence must be nonempty but is not authenticated or opened by Personal Model & Effort Router. UTC timestamps are required, future dates rejected. Records must exactly match a catalog candidate's model/effort/harness. Use new case IDs when task inputs change. Results files may be JSONL, a single JSON object (including dispatch output records), or a JSON array. All are validated. Do not feed pending/unverified execution status files into evidence.

`route --runs old.jsonl new-result.json --task ...` combines records. Keep the old files intact; duplicate run IDs cause an error rather than duplicate counting. `dispatch` creates a new result file exclusively and refuses to overwrite it.

# Agent and executor integration

Personal Model & Effort Router's automatic selection is deterministic. Classification is supplied by your existing host agent; execution is supplied by your adapter. v0.2 does not contain or validate either model-backed component. It cannot switch the current chat's own model by writing a prompt.

## Adapter protocol

Only use this adapter when the user has authorized its execution. The executable receives one JSON object on stdin:

```json
{"schema_version": 1, "task": {"...": "complete task object"}, "selected": {"id": "...", "model": "...", "effort": "...", "harness": "..."}}
```

It must actually apply the selected model AND supported effort value through its executor/API. It must independently evaluate acceptance and print a JSON object to stdout:

```json
{
  "output": "A result or local result reference",
  "passed": true,
  "total_cost_usd": null,
  "total_duration_seconds": 120,
  "evidence": "private/evidence/case-001/acceptance.md"
}
```

These are protocol illustrations. `passed` is a real boolean; numeric totals must be finite and nonnegative, or null when unknown. Complete-task accounting is the adapter's responsibility. Output is returned to the caller but not placed into the evidence record. Keep diagnostics on stderr and credentials out of both streams. Personal Model & Effort Router does not print captured adapter error streams, to reduce accidental disclosure.

```sh
python3 <skill-root>/scripts/route.py dispatch \
  --catalog private/catalog.json \
  --runs private/runs.jsonl \
  --task private/task.json \
  --record-to local-runs/new-result.json \
  --timeout 300 \
  --adapter python3 your_adapter.py
```

Create `local-runs/` first. The named adapter is your trusted program, not a bundled provider integration. Put `--adapter` last. Arguments are passed as an argv list, without a shell; task text is passed via stdin. The process inherits the caller's environment and permissions. An adapter is not sandboxed. Configure spend limits, tool scopes, idempotency and isolation in the executor before using it. A historical mean limit is not a hard cap.

Synthetic decisions cannot be dispatched. A fallback requires `--allow-fallback` in addition to the explicit dispatch command. High-risk/unconfirmed tasks have no dispatch override in v0.2. Review those through your normal workflow.

The output path is reserved before invoking the adapter. Success saves a new observed record; failed acceptance saves the failure too. Nonzero process exit, malformed output, timeouts, or result-validation failure leave `execution_unverified`; interruption may leave `pending`. These are recovery markers, not accepted evidence. Do not retry blindly: the provider or a child process may still have performed work or incurred charges. There is no automatic retry, rollback or escalation.

Use a subsequent routing command to include the new record:

```sh
python3 <skill-root>/scripts/route.py route \
  --catalog private/catalog.json \
  --runs private/runs.jsonl local-runs/new-result.json \
  --task private/next-task.json
```

Exit statuses: `0` successful route/accepted dispatch; `1` malformed input or execution/result error; `2` review or blocked dispatch; `3` completed adapter with failed acceptance. The route command can return `0` with `status=fallback`, so always inspect the JSON status before custom execution.

## Existing evaluators and gateways

Promptfoo can produce evaluation outcomes, and LiteLLM can apply supported provider settings. v0.2 has no native exporter/importer for either. Convert their results into the documented schema only after checking that full-task cost, final acceptance, exact model/effort and harness revision are available. Partial records must preserve unknowns. Provider-specific setup and any paid calibration need separate, explicit configuration and spending limits.

## Preference and availability fields

Optional `task.objective` is `cost`, `latency`, or `quality`; it overrides `catalog.policy.objective`. The legacy default is cost, so explicitly set the objective when translating user preferences. Cost minimizes known mean complete-task cost. Latency minimizes known mean complete-task duration. Quality prefers the highest observed case pass rate after gates. All objectives obey the same acceptance/sample/harness/risk gates and explicit mean limits. Unknown costs can participate in latency/quality routing only when no money constraint needs them. None of these objective values relax acceptance.

Optional `task.allowed_candidates` contains currently available/permitted candidate IDs. Keep historical configurations in the catalog for run validation, but exclude unavailable ones from current comparison. An empty list means no allowed configurations and requires review. `evidence_run_ids` in each candidate result identifies the exact records used.

The agent prepares these files when using the deterministic helper. Users need not label tasks or write JSON. A profile or runtime constraint must not be overwritten to make a cheap candidate win.

## Configuration confirmation

A run is used for selection only when `configuration_confirmed` is true. Missing/false preserves the record but excludes it from calibration; requested settings alone do not establish the effective model/effort. Do not manually set true unless the evaluator/executor has the relevant runtime evidence. This field is a declaration, not independent remote authentication.

An executor adapter may return `applied_config: {"model": "...", "effort": "...", "harness": "..."}` matching the requested values exactly, based on actual executor acknowledgement/readback. A mismatch leaves `execution_unverified`. Missing/null records configuration_confirmed=false, so the accepted task is not attributed as performance evidence to an unconfirmed configuration. The CLI returns this confirmation flag separately from acceptance. Merely echoing the request does not provide legitimate confirmation; the offline mock tests check protocol handling only.
