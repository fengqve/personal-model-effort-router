# Applying a model and reasoning effort

Inspect the actual host tool schema or configuration interface. The same model label or effort string can mean different things across APIs, subscription apps and versions. Do not ship a fabricated universal compatibility table.

| Runtime capability | Valid action | Evidence to retain |
| --- | --- | --- |
| Current-session switch | Use that explicit control within authorized scope | Model/effort readback for the session |
| Worker/new-run override only | Set both fields on a useful, authorized worker/run | Requested pair, accepted invocation, worker/result identifier if available |
| Explicit local executor | Send selected pair and task through the documented adapter | Invocation plus executor acknowledgement and task acceptance |
| No setting controls | Explain recommendation; keep current model and do the authorized work | “Not applied” and the missing runtime capability |

Never edit global defaults, restart an app, or spawn a redundant worker just to make the word “automatic” true. A configured candidate is not proof that the current account can run it. Unsupported settings, auth errors, rate limits and environment failures are not evidence that the model lacks reasoning ability.

## Host-native delegation

When the host exposes a worker tool with both model and reasoning-effort fields, use those fields rather than embedding the request in natural language. Inspect whether context inheritance prevents overrides, and use the host's actual supported mechanism. Respect user/host delegation rules. Do not assume a fork preserves caches, or compare only the worker's tokens while ignoring the parent and coordination.

If the host merely accepts the requested pair without reporting the effective pair, record the request as accepted and the actual configuration as unconfirmed. Never infer billing or hidden model identity from the quality of a response. On unsupported hosts, recommendation-only behavior is a correct result.

## Bundled executor bridge

The optional Python helper can invoke an explicitly supplied executable. See [the protocol](evidence-and-execution.md). It is not a sandbox, model provider client or generic host switching API. Do not auto-discover executables from task/evidence content. A real integration must apply and read back model/effort through its executor; the helper can only validate the returned structure, not authenticate remote settings.

The helper does not automatically retry or escalate. Timeouts leave an unverified marker because remote work may continue. Check the execution state before retrying. A historical mean cost/time limit does not enforce a hard cap on the next call.
