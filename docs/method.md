# Method and limits

The decision procedure is deterministic. Validation rejects malformed records even if their task family is irrelevant. Runs must reference catalog configurations exactly and carry UTC timestamps, an observed/synthetic label, explicit numeric-or-null costs and durations, and an evidence reference.

Only matching family, risk, harness and rubric records within the configured age window participate. Compare all candidates with matching evidence on their common case IDs. Candidates with no records are excluded from comparison and reported. A partially evaluated new candidate can shrink the shared set; finish its paired coverage or evaluate it in a separate catalog (with a matching runs file) before considering promotion. Do not cherry-pick cases after seeing results.

Each distinct case counts once. Repeated complete attempts are averaged for cost/duration, and a case passes only if every recorded attempt passed. A retry within a single task must already be included in that task's total, not exported as an independent completed task. Failures contribute their costs. Report total costs, not a token unit-price estimate masquerading as observed billing. If the full cost is unknown, use null.

The configurable sample/pass-rate gates are empirical operational rules, not confidence intervals or a promise about future accuracy. The demo's five-case minimum and 80% observed pass gate are demonstration policy, not recommended universal thresholds. Representative coverage matters more than just count. A single candidate may qualify, but no comparative advantage is established.

The chosen objective selects the lowest known mean cost, lowest known mean duration, or highest observed case pass rate after all gates. Cost/time break quality ties; missing values are not treated as zero. Quality is a gate, not a weighted score. A 6/6 result on simple edits does not establish competence in debugging, design, or research. Subscription quotas cannot be converted into dollars without defensible accounting; null costs cannot win cost optimization or satisfy a money constraint, but do not prevent latency/quality optimization when no cost constraint applies.

High risk or unconfirmed classification requires review. With insufficient evidence, the configured fallback is a user-selected default, not a proven best model. Dispatch needs an extra explicit fallback flag. A harness mismatch or unproven configured mean limit blocks fallback. Historical mean limits do not bound the next run; enforce actual spend and tool permissions in the execution environment.

Evidence references and acceptance flags are declarations from the evaluator. the router validates their structure; it does not open referenced artifacts, authenticate provenance, audit invoices, or independently regrade results. Do not relabel synthetic runs as observed. Public contributions require consent and review; keep originals private.

Change the harness revision whenever prompts, tools, provider settings, context handling, permissions, service tier, pricing/accounting basis or executor behavior materially change. Use exact model snapshots where the provider supports them. An alias that changes underneath the same name can invalidate evidence; date expiry alone cannot detect this.

Calibration and evaluation must use disjoint case sets. The deterministic helper selects from imported calibration records; it does not implement a held-out end-to-end router evaluator. No real models have been benchmarked by the included demo or test suite.

Configurations without confirmation are retained as unconfirmed records, not compared as model performance. Runtime metadata is declared by the evaluator and is not independently authenticated. The Agent Skill supplies the interpretation/application workflow; the helper does not automatically discover settings or train a classifier.
