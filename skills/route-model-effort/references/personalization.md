# Preferences and first use

Reuse the user's explicit instructions, project settings and previously accepted choices before asking anything. This Skill is a per-task decision procedure, not a background service that intercepts every message. Automatic discovery depends on the host; invocation does not grant configuration-write, spending, delegation or publication authority.

For a first use, establish only what changes a decision:

- Acceptance: what must work, how it will be checked, and failure consequences.
- Primary preference: quality, latency or cost, with any explicit secondary constraints.
- Available configurations and the execution boundary: current session, worker/run, or advice only.
- Existing baseline and permitted local feedback storage. No usable baseline means make a provisional recommendation or ask the one necessary tradeoff; do not invent benchmark evidence.

A user can say “keep quality, but cheaper”, “speed matters for this draft”, or “accuracy first; extra time is fine”. Translate this into the applicable objective and preserve explicit constraints. For “balanced” without weights, retain the current policy and state that assumption; do not silently assign arbitrary weights or always favor the cheapest.

## Optional local profile

If useful and authorized, maintain one small `.model-routing/profile.md`, not a new preference system. Example fields (illustrative, not universal defaults):

- Baseline: the user's existing model/effort configuration.
- Priority: quality first for final work; latency first for reversible drafts.
- Boundaries: no additional paid calibration; no global configuration changes.
- Evaluation: task-specific acceptance; preserved failure/rework records.
- Runtime scope: verified worker-level overrides only.

Keep canonical statements and their scope. The user can override the profile for one task without changing the lasting default. Explicit model/effort requests take priority over inferred optimization; unsupported combinations must be reported, not silently substituted.

## Cold start and recalibration

Official guidance is a reasonable prior when current and applicable. Save its source/date separately from observed local outcomes. Use the existing working default until there is a defensible comparison; this avoids front-loading a costly benchmark and lets ordinary authorized work produce evidence.

A calibration campaign is separate work: freeze representative inputs and acceptance checks, choose supported candidate configurations, define the held-out cases, and establish spending/retry scope before execution. Historical tasks may contain private code or side effects; recreate permitted fixtures rather than replaying production actions. Measure total parent/worker calls, cached context, retries, evaluation and coordination, and human rework where known. Do not use tuning cases as held-out proof.

No durable profile is required for a one-off choice. If recording outcomes is not authorized, use current-session evidence and report that personalization will not persist automatically.
