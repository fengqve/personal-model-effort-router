# Contributing

Use Python 3.9+ and run `python3 -m unittest discover -s tests -v` and `python3 -m fitmytask demo` from the repository root. Runtime code uses the standard library.

Please open a focused issue or pull request describing the task, reproducible input, expected decision, and actual result. Include a regression case for policy changes. Preserve synthetic/observed separation and failure accounting.

Task/evidence contributions must state: consent to publish; frozen input and license; task family and risk; rubric and reviewer/evaluator; exact model/effort and harness revision; all attempts including failures; dates and accounting coverage; what was held out. Anonymization is not automatic. Never submit credentials, private URLs, personal identifiers, private chat history, unlicensed source material, or proprietary tasks without permission. Prefer small independently written public fixtures.

Do not infer model quality from synthetic examples, incomplete tasks, unavailable prices, model self-assessment, or a single successful attempt. Negative results and reproducible abstentions are useful contributions.

There is no hosted evidence upload service. Contributions are reviewed through GitHub. The local router never executes commands found in task or evidence data; only the command supplied explicitly to dispatch is executed. That command has the caller's permissions and is not sandboxed.
