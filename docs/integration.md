# Agent-first integration

Read [the Skill](../skills/route-model-effort/SKILL.md) as the primary interface. Its [runtime guide](../skills/route-model-effort/references/runtime.md) distinguishes current-session switches, worker overrides, explicit executors and recommendation-only environments. Its [evidence/executor protocol](../skills/route-model-effort/references/evidence-and-execution.md) defines the optional helper.

The Skill asks the Agent to interpret preferences and prepare inputs; it does not ask users to operate a CLI. A supported host can discover the installed Skill, but implicit-invocation metadata is not a guaranteed per-request interception mechanism. First use may simply read the source file. Do not install into global directories or rewrite defaults without the user's intended scope.

Optional developer installation is `python3 -m pip install .`, exposing `model-effort-router`; this installs only the helper, not the Skill into any Agent. The no-install helper command is `python3 skills/route-model-effort/scripts/route.py ...`. No PyPI publication is claimed.

When importing v0.1 records, `configuration_confirmed` must be justified by runtime evidence. Missing confirmation now excludes the record from calibration; do not fill it with true just to restore a previous selection. The old FitMyTask module/command has been replaced in this unpublished preview.
