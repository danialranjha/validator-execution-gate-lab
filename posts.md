# Publication drafts

Drafts only. No social posts have been published. Attach `visuals/header.png` to the opening post and `visuals/body.png` to the ablation explanation.

## X thread

### 1/7

I built a tiny test that forces an agent validator to approve every action, then checks what reaches the sink. No live LLM: deterministic fixtures and an in-memory ledger.

Code + reproduction:
https://github.com/danialranjha/validator-execution-gate-lab

### 2/7

Same approval. Same signed action targeting a restricted resource.

Approval only: 1 append.
Token only: 1 append.
Policy only: 0.
Both checks: 0.

Here, the signature passes. The policy supplies the block.
https://github.com/danialranjha/validator-execution-gate-lab/blob/main/artifacts/run.json

### 3/7

Reverse the fixture: allowed inbox, forged capability.

Policy only permits the append; token verification blocks it. A valid inbox twin succeeds in all four modes. The checks enforce different conditions.

Table + scope caveat:
https://github.com/danialranjha/validator-execution-gate-lab/blob/main/visuals/body.png

### 4/7

10 scenarios, 4 modes, 44 dispatch attempts. The full gate committed 0/4 out-of-policy attempts and 0/8 invalid-capability attempts. Those groups overlap. These are fixture counts, not estimated attack rates.
https://github.com/danialranjha/validator-execution-gate-lab/blob/main/artifacts/evidence.md

### 5/7

The motivation is this paper's separation of validator judgment from execution authorization. Its memory-poisoning setup forces bypass with a replacement routine. My harness is not a reproduction of its live-model evaluations.
https://arxiv.org/html/2609.17648v1

### 6/7

14 tests pass. Removing either gate in a temporary copy makes its critical test fail. Changed text, task binding, malformed capabilities, and replay are checked against actual sink records.

Tests:
https://github.com/danialranjha/validator-execution-gate-lab/tree/main/tests

### 7/7

Single-process demo, not production isolation.

Reproduce:
https://github.com/danialranjha/validator-execution-gate-lab

Engineering gate: force approval; require no out-of-scope sink action and a working authorized twin; remove each check separately to prove what it enforces.

## LinkedIn post

I built a small authorization test with a validator that always says yes.

The question was what still prevented an out-of-scope action from reaching the executor's sink.

I held the proposed action and forced approval constant across four modes: approval only, token only, policy only, and both checks. Every “action” was just a synthetic record appended to an in-memory ledger. No live LLM or external service was involved.

For a validly signed action targeting a restricted resource, approval-only and token-only each committed one record. Policy-only and the combined gate committed none.

Then I reversed the problem: a forged capability for an allowed inbox. Policy alone permitted the append; signature verification blocked it. The valid, in-scope twin succeeded in all four modes.

The trace covers 10 scenarios and 44 dispatch attempts. All 14 tests passed; deliberately removing either gate made its critical test fail.

Run evidence and limitations:
https://github.com/danialranjha/validator-execution-gate-lab/blob/main/artifacts/evidence.md

The source idea came from research separating validator judgment from downstream authorization:
https://arxiv.org/html/2609.17648v1

My interpretation: inspect the sink as well as the approval. This deterministic harness demonstrates enforcement of a declared policy on designed fixtures. It does not establish model robustness, policy completeness, or production privilege separation.

Code, exact commands, and visuals:
https://github.com/danialranjha/validator-execution-gate-lab

The engineering gate I would add: force approval, assert that the out-of-scope action never reaches the sink, require its authorized twin to work, and disable each check separately so the test proves which boundary matters.

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
