# FitMyTask

**Choose a model and reasoning effort from your own task evidence.**

[简体中文](README.zh-CN.md) · [Evidence format](docs/evidence.md) · [Agent integration](docs/integration.md) · [Method and limits](docs/method.md)

A new model is one reason to reconsider your defaults. A new task, a changed workflow, rising costs, or disappointing results are others.

FitMyTask is a small, local Python tool that turns complete-task evaluation records into an explainable model + effort decision. Keep your existing evaluator and execution stack. Bring their results; inspect the decision; let your agent call an explicitly supplied adapter.

**Status: experimental v0.1.0.** The included demo uses fictional models and invented results. No real-model advantage, cost saving, or classification accuracy has been demonstrated. This is a routing mechanism, not a published model recommendation.

## Try it in 30 seconds

Python 3.9+, no runtime dependencies, API key, network, or installation needed:

```sh
python3 -m fitmytask demo
python3 -m unittest discover -s tests -v
```

Run these commands from the repository root. Optional installation from source: `python3 -m pip install .` then `fitmytask demo`. No PyPI release is claimed.

The simulation compares six shared fixtures:

| Fictional configuration | Cases passed | Mean complete-task cost | Decision |
| --- | --- | --- | --- |
| small / low | 4/6 | $0.02 | Fails the quality gate |
| small / high | 6/6 | $0.08 | Selected in the simulation |
| large / high | 6/6 | $0.30 | Eligible, more expensive in these fixtures |

These numbers illustrate the code. They say nothing about any real model. A dispatch cannot use synthetic decisions.

## Use your own evidence

1. Freeze representative cases and acceptance criteria. Run the same cases through candidate model/effort configurations using your existing evaluator.
2. Export one complete task attempt per JSONL record, including failures, retries, handoffs, and rework. Unknown costs are `null`, not zero. See [the format](docs/evidence.md).
3. Have your host agent assign a known task family, risk, harness revision, and rubric. Unknown or uncertain classifications must set `classification_confirmed: false`.
4. Ask for a decision:

```sh
python3 -m fitmytask route   --catalog private/catalog.json   --runs private/runs.jsonl   --task private/task.json
```

The JSON includes the selected model and effort, sample counts, observed pass rates, cost and duration, exclusions, and limitations. A high-risk or unconfirmed task returns `review_required` with no selection.

When you are ready to execute, `dispatch` sends the choice and task to **your explicitly named executable**. It is not a sandbox. See [the adapter contract](docs/integration.md); dispatch may incur costs or change files according to your adapter. The core itself makes no provider requests and changes no global agent configuration.

## What v0.1 does

- Treat model + effort + harness as a configuration, without guessing capability from names.
- Compare matching family/risk/rubric/harness records on shared case IDs.
- Retain failed task costs and avoid counting reruns as independent cases.
- Reject malformed, mismatched, future-dated or unsupported records; exclude stale and synthetic evidence by default.
- Apply explicit empirical quality/sample gates before choosing the lowest known mean task cost.
- Explain abstentions and fallback; explicitly gate fallback execution.
- Pass the selected configuration to an adapter and save its accepted result as a new evidence record.

## What v0.1 does not do

It does not include a trained task classifier, provider integrations, native Promptfoo/LiteLLM importers, a benchmark runner, a live price catalog, or automatic escalation. Your host agent supplies classification; your evaluator judges completion; your adapter actually applies the model/effort settings. These components and end-to-end quality must be validated in your environment. Historical mean-cost limits are **not hard spending caps**. A timeout cannot reliably stop a remote request or every descendant process.

## Why another tool?

[RouteLLM](https://github.com/lm-sys/RouteLLM) already serves and evaluates routers. [LiteLLM](https://docs.litellm.ai/docs/proxy/auto_routing) already offers automatic classification and routing. [Promptfoo](https://www.promptfoo.dev/docs/configuration/expected-outputs/) evaluates outputs. [OpenAI](https://developers.openai.com/api/docs/guides/model-selection) already recommends evaluating model and reasoning effort together.

FitMyTask explores a narrower question: **Can a small, inspectable layer connect your task acceptance records to your next model-and-effort choice?** It complements those tools; it does not claim to invent evaluation or routing. See [the design](docs/design.md).

## Contribute

Useful contributions: reproducible task packs, robust acceptance checks, evaluator adapters, classification error analysis, and negative results. Please do not submit private prompts, proprietary code, credentials, or unsupported performance claims. Start with [CONTRIBUTING.md](CONTRIBUTING.md).

MIT licensed. Built with AI assistance; maintainers are responsible for review.
