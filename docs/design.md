# Product design

## Outcome

The user gives an Agent a task and priorities. The Agent selects and applies an available model/effort configuration based on the user's task outcomes and preferences, preserves evidence, and improves future decisions. The user reviews meaningful tradeoffs rather than labels tasks or runs routing commands.

Official recommendations are useful priors. The product gap is connecting them to personal outcomes, preferences and actual runtime application, not the absence of recommendations.

## Entry and scope

Primary entry: route-model-effort Agent Skill. Optional implementation helper: deterministic Python comparison and executor bridge. No new hosted gateway, background service, account, trained classifier or mandatory benchmark campaign.

Model release, new task/project, changed preferences, poorer outcomes, tool/prompt/context changes can all trigger reconsideration. On a cold start, retain the user's existing baseline and make uncertainty visible. Normal authorized work can produce useful records without an up-front benchmarking bill. Explicit calibration remains separately scoped work with representative frozen tasks, acceptance criteria, held-out cases and spending/retry limits.

## Boundaries that affect the product

An Agent can only use controls actually exposed by its host. The product must say whether it applied a current-session change, a worker/new-run configuration, or merely made a recommendation. A Skill cannot provide missing privileges. A model-and-effort pair accepted by an interface is a requested setting until the runtime confirms the effective values.

Quality, latency and cost are user-selected objectives, not fixed cheapness. Existing constraints remain gates. Unknown money, quota, human effort or effective model identity stays unknown. Broad tasks should not be classified by a single technology keyword. Risk and task acceptance change the route even within one project.

Feedback can change evidence used for subsequent decisions. It does not silently modify long-term preferences, permissions or global defaults. Permanent configuration changes are distinct from selecting an authorized per-task model.

## Validation still needed

Real user adoption; held-out task classification; exact provider/host settings; paired real model trials; fixed-default versus routed completion quality and total parent/child/coordination/retry/rework cost. No savings target or delivery timeline is promised. Public evidence may seed hypotheses; it cannot establish performance in another user's environment.
