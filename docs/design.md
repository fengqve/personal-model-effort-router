# Product design / 产品设想

## User and value hypothesis

Start with individual developers and small teams already using an agent and capable of judging whether a task is complete. They currently select models manually or keep a fixed default. FitMyTask should make that choice inspectable and repeatable using their own work. This is a demand hypothesis, not validated product-market fit.

中文定位：把“凭印象选模型和档位”变成“用自己的任务验收记录作选择”，逐步减少重复试错。

## More than model launches

| Trigger | Necessary observation | Response |
| --- | --- | --- |
| New model or effort option | Exact supported deployment configuration | Add a candidate; do not promote it without comparable runs |
| New project/task family | Representative cases and acceptance checks | Keep known default or review until evidence exists |
| Quality decline | Actual failed outcomes, not model self-confidence | Review classification/rubric/harness; collect matched reruns |
| Cost or deadline changes | Complete task costs/durations | Apply reviewed empirical limits; enforce hard caps in the executor |
| Prompt/tool/context changes | New harness revision | Separate old evidence; recalibrate |
| New team or provider | Different permissions, tool stack, task distribution | Treat prior public evidence as a hypothesis to validate locally |

v0.1 reacts when invoked with updated input files. It has no background monitoring or automatic event subscription.

## Core interaction

User/host describes a task → host classifies against known families → router checks evidence → shows selected/review/fallback plus reasons → authorized adapter executes → evaluator returns acceptance and complete cost → an immutable result is available for the next routing run.

The user may inspect every decision, but an integration can automate accepted low/medium-risk decisions. High risk and uncertainty remain explicit. A result that fails acceptance is retained and returns a nonzero exit; v0.1 does not silently retry or select a stronger model.

## Smallest useful first release

A standard-library Python library and CLI with JSON/JSONL records, source install, one offline demo, unit/integration tests, and a documented adapter contract. No service, accounts, hosted leaderboard, telemetry, global configuration edits, or new Agent Skill. Reasoning effort remains an explicit string attached to each candidate; names do not imply rankings.

Automatic classification belongs to the host model in v0.1. This avoids paying for a new classifier before we know it helps. It also means classification is not yet a validated feature of this repository. The next experiment must test the full host→router→executor loop, not only selection on correct labels.

## Evidence needed before larger claims

1. Real paired runs on versioned tasks, with hard acceptance checks and independent review where needed.
2. Held-out cases for the routing policy. Do not select and report final performance on the same cases.
3. Classification confusion/errors on unseen tasks, including ambiguity and high-risk cases.
4. Routed vs fixed-default complete outcomes, including classification, evaluation, coordination, fallback, retries, cache conditions, human rework and total cost.
5. A user other than the author can import their own results and understand an abstention without help.

No numeric savings target is promised. Keep the first real trial small and explicitly budgeted before paid execution.

## Publication and follow-through

Release as an experimental evidence-to-routing tool. Show the offline simulation labelled as such. Invite reproducible task packs and integration feedback rather than likes as proof of demand. Record whether outside users can complete the import→decision→execution loop. Broaden only when that works.

Planned next steps, not implemented promises: native evaluator imports; validated host classification; paid/local real model trial with cost ceiling; comparative policy evaluation; executor-specific bounded escalation; portable evidence contributions. No release dates are promised.
