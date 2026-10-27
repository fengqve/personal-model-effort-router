# Verification — 2026-10-27

## Deterministic behavior

29 tests passed locally on macOS/Python 3.9.6: 12 core regressions, 12 CLI/adapter regressions, and 5 preference/availability/configuration-confirmation tests. Cases cover shared task inputs, failed/repeated attempts, unknown costs, quality/time/cost gates, unavailable candidates, unconfirmed/mismatched configuration, fallback, synthetic separation, timeout recovery and record reuse.

Skill quick validation, authoring/reference audit and the source monorepo validator passed. These are structural checks, not semantic quality proof.

## Independent Agent forward test

A separate Codex Agent read the source Skill and references without receiving the intended answer. It exercised:

- A user-requested one-worker task under an existing gpt-6-luna / max baseline. One actual worker API request submitted the pair and returned the correctly deduplicated/sorted JSON array. The host accepted the request but exposed no independent effective-model/effort readback. The evaluator retained that uncertainty; full cost and elapsed time were unknown.
- A scenario with no current-main-model switch and no permission for a new worker. It reported the limitation and did not create a worker or claim a switch.
- Offline synthetic preference demos: cost, latency and quality selected economy-low, fast-medium and careful-high respectively, all marked simulation.

This proves the observed behavior in these limited cases. It is not a model benchmark, classification accuracy measurement, cost-saving result or evidence of global automatic discovery.

## Still unverified

Installed host discovery; Claude Code/WorkBuddy or other host compatibility; provider-specific execution adapters; effective remote configuration readback; real personal model calibration; end-to-end economic benefit. Adapter statuses remain not-validated. The helper trusts evaluator declarations and does not authenticate remote evidence.

GitHub Actions is configured but has not run remotely. No global installation, settings change, paid provider-API calibration, or publication occurred during this revision. The exported Skill fingerprint matched its source release manifest. The optional helper wheel was built with setuptools 82.0.1 in a local virtual environment, installed, and its console entry point returned the expected quality-demo selection outside the source tree. Both README languages and local Markdown links were checked.
