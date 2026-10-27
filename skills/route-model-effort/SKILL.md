---
name: route-model-effort
description: Select and apply an available LLM and reasoning effort for a task using the user's quality, speed or cost preferences and local task outcomes. Use when delegating work, revisiting model defaults, or asked to personalize model routing; distinguish a recommendation from an actual runtime change.
---

# Personal Model & Effort Router

Make model and reasoning-effort choices for the user, using their goals and actual task results. Official recommendations can seed a choice; they do not establish the best configuration for this user's workflow. The user should describe the work and priorities, not prepare routing commands or classify tasks manually.

## Establish the available decision

Read existing user/project routing preferences and relevant task outcomes first. Use a user-specified location, or `.model-routing/` in the project when local feedback storage is authorized. Do not crawl unrelated chats or install global defaults. For a first run or changed priorities, read [personalization](references/personalization.md); reuse established choices instead of asking on every task.

Inspect the current host's actual model/effort controls and available configurations. An installed Skill does not create a switching API. Distinguish: current-session switch, new worker/run configuration, or recommendation only. When no supported control exists, preserve the current setting, explain the limitation briefly, and continue authorized work where possible. Do not create a second agent merely to simulate a current-model switch.

Honor an explicit user choice within the runtime's capabilities and permissions. Otherwise select among available, permitted configurations; never infer supported effort values or cross-provider equivalence from names. Treat model, effort, prompt/tool/context setup and service/accounting conditions as a configuration.

## Judge this task and select

Infer the task's demands from its acceptance conditions, ambiguity, context/dependencies, verifiability, reversibility and failure cost. Reuse a matching local task family and rubric. A project name, technology keyword, prompt length or the model's confidence is insufficient. For unfamiliar or mixed tasks, record uncertainty and retain the known default; split only when the work itself benefits from independent subtasks.

Apply the user's explicit quality requirements, budget, time and allowed configurations before optimizing their primary preference. Preserve their existing default when preferences are missing; ask only when a missing tradeoff materially changes the outcome. Do not invent a numeric quality threshold or convert an informal preference into a hard dollar cap.

Use comparable local outcomes first. Consider actual acceptance, complete cost, elapsed time and rework; include failures and classification/coordination/evaluation overhead. Missing money or quota data stays unknown. A small sample, synthetic result or unverified model self-report cannot establish a better configuration.

When structured comparable records exist, use the bundled [selection helper](scripts/route.py) with the format in [evidence and execution](references/evidence-and-execution.md). Prepare the input yourself from available evidence; the user does not need to operate the CLI. The helper supports cost, latency and quality objectives and an allowed-candidate list. Respect its `review_required`, `fallback` and `simulation` states; do not invent evidence to get a selection.

Without sufficient evidence, use an already authorized baseline. Label this as a prior/default, not a calibrated winner. A new model, changed task, failed outcome, changed priorities or changed harness can trigger reconsideration, but does not by itself justify a benchmark campaign or migration.

## Apply, verify and learn

Use the supported runtime fields for both model and effort. A recommendation, config file or prompt saying “use model X” is not execution. When a host supports only worker-level overrides, apply the choice only to a justified, authorized worker task. Keep the main agent's unchanged setting explicit when relevant. Follow [runtime application](references/runtime.md) when applying a choice for the first time on a host.

Capture the requested configuration and the runtime's acknowledgement/readback separately. If it cannot be read back, say “requested, not independently confirmed.” Judge task completion using the actual acceptance checks. Do not turn runtime acceptance of a request into proof of quality or savings.

If acceptance fails, preserve useful work and diagnose task definition, missing evidence, tool/environment failures and reasoning separately. Escalate model/effort only when that addresses the cause and fits the existing retry/spend scope. Without a retry allowance, stop the attempted escalation and report the useful result and missing decision. Never blindly repeat potentially completed side effects.

Within authorized local feedback storage, record the result, evidence reference, actual/unknown configuration, complete/unknown consumption and material human rework. Use [evidence and execution](references/evidence-and-execution.md) for the schema. Do not automatically write global memory or promote one result into a permanent rule. New records inform the next decision; changes to user constraints, defaults or permissions need their own authorization.

Keep ordinary decision explanations short: chosen model/effort; why it fits the user's priority; evidence or fallback basis; what was actually applied; task outcome and remaining uncertainty. A detailed comparison is useful when reviewing policy, not on every routine task.
