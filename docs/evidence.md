# Evidence format v1

The complete runnable fixture is in `examples/`. It is synthetic and must not be relabeled as observed. The command `python3 -m fitmytask demo` generates fresh synthetic timestamps; static fixtures can eventually expire.

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
  "total_cost_usd": null,
  "total_duration_seconds": null,
  "completed_at": "2026-10-27T00:00:00Z",
  "source": "observed",
  "evidence": "private/evidence/frozen-case-001/acceptance.md"
}
```

This is a schema illustration, not an actual run. `passed` must come from acceptance checks, not the model's claim of success. Include all subcalls, retries, failed attempts, classification/evaluation and coordination costs in the task total where incurred. Record the whole task's elapsed duration, not the sum of parallel child durations. If accounting is incomplete, use null and document the gap in the referenced artifact. Human review/rework should be described there, including whether its elapsed time and monetary valuation are included.

`source` is `observed` or `synthetic`; IDs must be unique. Evidence must be nonempty but is not authenticated or opened by FitMyTask. UTC timestamps are required, future dates rejected. Records must exactly match a catalog candidate's model/effort/harness. Use new case IDs when task inputs change. Results files may be JSONL, a single JSON object (including dispatch output records), or a JSON array. All are validated. Do not feed pending/unverified execution status files into evidence.

`route --runs old.jsonl new-result.json --task ...` combines records. Keep the old files intact; duplicate run IDs cause an error rather than duplicate counting. `dispatch` creates a new result file exclusively and refuses to overwrite it.
