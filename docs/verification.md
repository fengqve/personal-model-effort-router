# Verification — 2026-10-27

Verified locally on macOS with Python 3.9.6:

- `python3 -m unittest discover -s tests -v`: 22 tests passed.
- `python3 -m fitmytask demo`: selected fictional small/high, with `simulation: true`.
- Explicit fixture-file route with `--allow-synthetic`: same expected choice.
- Mock adapter execution: selected model/effort and Chinese task content delivered through stdin; output acceptance saved, and the result consumed by the next routing decision.
- Failure acceptance, malformed responses, nonzero adapter exit, timeout, preexisting output files, fallback opt-in and synthetic-dispatch blocking exercised offline.
- Wheel built with setuptools 82.0.1 in an isolated local virtual environment, installed from the wheel, and its `fitmytask demo` console entry point executed outside the source repository.
- English and Simplified Chinese README present; relative Markdown links checked.

The host's bundled setuptools 58.0.4 cannot correctly process this project's metadata when build isolation is bypassed. A trial with that unsupported builder produced UNKNOWN metadata and was rejected. Verification used a builder satisfying `pyproject.toml` instead. Normal pip build isolation resolves the declared build dependency; the no-install quickstart avoids packaging entirely.

Tests use fabricated records and local mock programs. They verify implementation behavior, not real model performance, task classification accuracy, provider integration, total savings, or user demand. No provider API requests were made by the tests. GitHub Actions is configured for Python 3.9/3.12 but has not run remotely. No Windows/Linux runtime claim is made from these local checks.

All example models and records are synthetic. No private task history or credentials are included in the release tree. Evidence pointers are validated as strings, not authenticated evidence. Actual integration needs its own verification and execution permissions.
