# Personal Model & Effort Router

**Let your agent choose the model and reasoning effort for your task, your priorities, and your observed results.**

[简体中文](README.zh-CN.md) · [Read the Skill](skills/route-model-effort/SKILL.md) · [Validation](docs/verification.md)

Model recommendations are useful starting points. The missing connection is applying them to your actual work: what quality you need, how long you can wait, what you can spend, and how each model/effort configuration has performed in your environment.

This project makes that decision an Agent workflow. A new model is only one trigger; changed tasks, priorities, tools or results matter too.

## Start with your agent

After opening this repository in your agent, say:

> Read `skills/route-model-effort/SKILL.md`. For this task, use my existing model preferences and local outcomes to choose a model and reasoning effort. Quality comes first; preserve my current default when evidence is insufficient. Apply the choice only through controls this host actually supports, and tell me what was really applied.

Your agent reads the Skill, interprets the task, prepares any needed evidence inputs, selects a configuration and uses the host's actual execution controls. You do not need to classify tasks or operate a Python CLI.

For a host with Agent Skills support, the **complete** `skills/route-model-effort/` folder is the installable unit. Use the host's supported skill installation mechanism. Once installed, it can be explicitly invoked as `$route-model-effort` where that syntax is supported. Implicit invocation is enabled in the package metadata, but discovery and routing frequency depend on the host. Installing a Skill does not create a model-switching API or intercept every message. Installed discovery and other-host compatibility have not been verified here.

## What the agent does

1. Reuse the user's current preferences, baseline and permitted model/effort configurations.
2. Judge task ambiguity, context, acceptance checks, reversibility and failure cost.
3. Use comparable local outcomes; treat official guidance as a prior when evidence is missing.
4. Optimize the user's quality, latency or cost preference without silently relaxing requirements.
5. Apply both settings through a supported session/worker/executor control, or say why it cannot.
6. Verify the task and, where authorized, retain outcome evidence for the next decision.

If the host exposes worker overrides but no main-session switch, the Skill does not claim to switch the main agent. It does not spawn redundant workers to simulate a switch. No local history is uploaded, no global configuration is changed, and no paid benchmark campaign starts merely because a new model appears.

## Two parts, one workflow

- **Primary interface:** [the Agent Skill](skills/route-model-effort/SKILL.md), including personalization, runtime application and evidence handling.
- **Optional helper:** deterministic Python selection for structured task records. It supports cost/latency/quality objectives, availability filtering, shared-case comparisons, risk/quality gates, evidence references and an explicit executor bridge. The agent prepares and invokes it when useful.

The helper requires Python 3.9+ with no runtime dependencies. An offline inspection command:

```sh
python3 skills/route-model-effort/scripts/route.py demo --objective quality
```

The same invented records choose `economy-low` for cost, `fast-medium` for latency and `careful-high` for quality. **All three are fictional.** The thresholds illustrate the mechanism, not recommended production policy. Synthetic decisions cannot be dispatched.

## Evidence and honest boundaries

**Experimental v0.2.0.** 29 offline tests passed. An independent agent read the Skill and exercised one real host worker request plus unsupported-switch and synthetic-preference scenarios. The worker returned the correct small task result. The requested model/effort pair was accepted, but the host supplied no independent effective-configuration readback. This is not a comparative model benchmark or savings claim.

The helper excludes runs whose configuration is unconfirmed, counts independent cases rather than repeated attempts, retains failure costs, and never treats missing costs as zero. User-supplied evidence declarations are not independently authenticated. Historical mean limits are not hard spend limits; enforce those in your executor.

The Skill is an instruction-based agent decision workflow, not a trained classifier or universal automatic gateway. Classification accuracy, real economic benefit, global installation/discovery, provider adapters and broad cross-host compatibility remain unverified. See [method](docs/method.md) and [integration](docs/integration.md).

## Related work

[OpenAI's model-selection guidance](https://developers.openai.com/api/docs/guides/model-selection), [RouteLLM](https://github.com/lm-sys/RouteLLM), [LiteLLM](https://docs.litellm.ai/docs/proxy/auto_routing), and existing model/effort skills from [enzoo808](https://github.com/enzoo808/model-effort-router) and [nyattoh](https://github.com/nyattoh/model-effort-router) already address related problems. We do not claim to invent recommendations, skills, feedback or routing.

Our focus is a small, inspectable personal loop: user priorities → local task outcomes → model + effort choice → actual supported application → verified outcome. Whether that improves real work remains something to measure.

MIT licensed. Contributions and negative results welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and [source provenance](PROVENANCE.md).
