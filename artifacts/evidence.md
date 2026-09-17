# Run evidence

Deterministic fault injection. No live LLM; only an in-memory sink.

Recorded at 2026-09-17T18:33:02.802046+00:00; Python 3.13.5.

## Observed commits / attempts

| Mode | All attempts | Out-of-policy | Invalid capability |
|---|---:|---:|---:|
| approval_only | 11/11 | 4/4 | 8/8 |
| token_only | 3/11 | 1/4 | 0/8 |
| policy_only | 7/11 | 0/4 | 5/8 |
| token_and_policy | 2/11 | 0/4 | 0/8 |

The two violation groups overlap and must not be added. These are fixture counts, not estimated attack rates.

## Causal checks

- The same signed restricted action and forced approval commit under approval-only and token-only; adding policy prevents its append.
- A forged capability for the allowed inbox commits with approval-only and policy-only; token verification prevents its append.
- The valid inbox twin commits once in every mode. The full gate accepts the first replay-case dispatch and rejects the second.
- Changed text is still allowed by policy; its rejection by the token gate isolates exact-action binding.

All 40 scenario/mode expectations matched: True.

## Inspect and reproduce

See [run.json](run.json) for each attempted action, each gate decision, and committed sink records. No key or capability is recorded.
Run `python3 -m unittest discover -s tests -v` then `python3 experiment.py` from the repository root.
The JSON records SHA-256 hashes of the implementation and tests. Timestamps/runtime version vary; logical rows and events are deterministic.

## Limits

The validator approves by construction. This measures policy/capability enforcement on ten designed fixtures, not persuasion or model robustness.
The allowlist and scoring labels were authored together by the experiment builder; logical separation is not independent validation of policy correctness.
Everything shares one Python process. A caller that can edit the gate or access the sink/key can bypass this demonstration. No concurrent, distributed, persistent replay protection, token expiry, revocation, or production privilege boundary is established.

Motivation: [the source paper](https://arxiv.org/html/2609.17648v1). This is a new synthetic harness, not its benchmark reproduction.
