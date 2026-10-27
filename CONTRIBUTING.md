# Contributing

Useful contributions include reproducible task/acceptance packs, classification error analysis, honest negative outcomes, runtime configuration readback and verified host adapters. We do not need unsupported model rankings or another fixed cheapest-model table.

Run `python3 -B -m unittest discover -s tests -v` and `python3 skills/route-model-effort/scripts/route.py demo --objective quality` from the repository root. Runtime code has no third-party dependencies.

The source of truth for the complete Skill is `skills/route-model-effort` in the maintainer's agent-skills monorepo, as recorded in [PROVENANCE.md](PROVENANCE.md). This repository contains the release export plus public documentation and tests. Propose changes through an issue/PR; maintainers reconcile runtime changes into the source monorepo, validate and version them there, then refresh the export. Do not develop in installed Skill directories.

Task/evidence submissions need permission to publish, frozen inputs and license, family/risk/rubric, exact runtime configuration and its confirmation, all failures/attempts, accounting gaps and held-out status. Do not submit private chat history, proprietary source, credentials, private links or personal identifiers. Synthetic fixtures remain clearly synthetic; model self-reports do not prove completion or effective settings.

Per-task choices do not grant new permissions or silently change global defaults. Tests must preserve this boundary and the distinction between recommended, requested, confirmed and accepted outcomes.
