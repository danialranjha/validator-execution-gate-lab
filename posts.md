# Publication drafts

Drafts only; not posted. Intended audience: technical people who build or use AI agents. Header and body diagrams show the assumed verifier compromise, the signed restricted request, and the independent execution policy.

## X thread

### 1/4

An AI agent may write to inbox, not restricted.

Assume prompt injection tricks its verifier agent into granting signed approval to write to restricted. What still stops execution?

I simulated that starting point: forced approval + a valid signature.

### 2/4

The signature passes. The destination is still forbidden.

Without a permission policy, the signed write to restricted executes. With an independent inbox-only policy, it is blocked.

A valid, approved write to inbox still succeeds.

### 3/4

Assume the AI agent's verifier is compromised; the executor and its policy remain trusted.

Signed approval cannot expand the policy's permissions.

This simulation tests enforcement after that assumed compromise. It does not demonstrate a live prompt-injection attack.

### 4/4

For AI agent builders: force approval of a signed, unauthorized action. Check that execution blocks it and still permits an authorized action.

Code, results, and technical walkthrough:
https://github.com/danialranjha/validator-execution-gate-lab#technical-walkthrough

## LinkedIn post

An AI agent may write notes to inbox, but not to restricted. Assume an adversary tricks its verifier agent—through prompt injection, for example—into granting valid signed approval for a write to restricted. The signature is valid. Does the write execute?

Without an independent permission policy, yes. With an inbox-only policy enforced by the executor, no. The signed approval cannot expand the task's permissions.

That's the scenario I simulated: start after the verifier is assumed compromised, force approval to yes, and supply a valid signed request to the forbidden resource.

The signature check passed. The permission policy blocked the restricted write. A valid, approved write to inbox still succeeded.

The verifier's judgment has failed; cryptographic verification has not. The executor and its permission policy remain trusted.

For agent builders, this gives a concrete regression check: force approval of a signed, unauthorized action. Verify execution blocks it while an authorized action still works.

This is a code simulation, not a demonstrated prompt-injection attack. It uses forced approval and a synthetic signing key, with writes recorded in memory; no live verifier agent was tested.

Code, results, and the technical walkthrough:
https://github.com/danialranjha/validator-execution-gate-lab#technical-walkthrough

## Editorial notes

Lead with the concrete inbox/restricted example and the assumed verifier compromise. “Verifier agent” refers to the approval component called the validator in code; do not confuse it with cryptographic token verification. “Signed approval” is shorthand for the starting state of forced boolean approval plus a valid action-bound capability. The fixture does not implement an agent issuing tokens or an adversary obtaining them through prompt injection. It models a synthetic signing-key holder; the hypothetical attack is motivation, not an observed result.

The restricted example is `signed_restricted`, the inbox control is `benign_twin`. Writes append synthetic actions to memory. Both policy-only and combined modes block the signed restricted request. The executor and policy are trusted assumptions. Keep established AI-agent terminology, clear causal comparisons, and no disclaimer footers on images.

## Public evidence map

| Claim or asset | Accessible evidence |
|---|---|
| Source motivation and constructed bypass caveat | [Paper IV-C, IV-D, V-B, V-C](https://arxiv.org/html/2609.17648v1) |
| Experiment code, threat model, exact commands | [Repository README](README.md) and [implementation](experiment.py) |
| Per-case outcomes and aggregate counts | [run.json](artifacts/run.json), 40 rows / 44 events |
| Fourteen passing tests | [tests.json](artifacts/tests.json) and [test source](tests/test_experiment.py) |
| Gate-removal tests fail | [mutation-checks.json](artifacts/mutation-checks.json) and [reproduction script](check_mutations.py) |
| Body visual | [PNG](visuals/body.png) · [SVG](visuals/body.svg) |
| 5:2 header | [PNG](visuals/header.png) · [SVG](visuals/header.svg) |
| Selectable-text explainer | [Self-contained HTML](visuals/explainer.html), download and open locally |

The original editorial source document remains private. Its link is in the local delivery evidence map, not in this public repository. No private document content or internal work history is included here.
