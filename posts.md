# Publication drafts

Drafts only; not posted. Intended audience: technical people who build or use AI agents. Use the sketch-style header for the opening post and the body diagram for the execution-gate example. The full technical walkthrough lives in the README.

## X thread

### 1/4

Your AI agent approved the action. Does it have permission to execute it?

I built a small simulation to test the execution gate after a forced approval. No live model calls.

### 2/4

The request: write a note to a restricted resource.

Approval-only execution let it through. An independent permission check blocked it. The authorized write still succeeded.

Same request. Same approval. Different execution gate.

### 3/4

Approval and permission answer different questions.

Approval says “go ahead.” A permission check asks whether this action is allowed for this task and resource.

In this demo, that independent check stopped the unauthorized action.

### 4/4

Code, results, and the technical walkthrough:
https://github.com/danialranjha/validator-execution-gate-lab#technical-walkthrough

Regression check: force approval of an unauthorized action. Verify execution is blocked and the authorized case still succeeds.

## LinkedIn post

Your AI agent approved the action. Does it have permission to execute it?

I built a small simulation of an AI agent's execution gate. I forced the approval step to accept a request to write a note to a restricted resource.

With approval as the only check, the unauthorized write went through.

With an independent permission check at execution, it was blocked. The authorized write still succeeded.

The request even had a valid signature. In this case, the signature check passed; the permission policy supplied the block.

My takeaway for agent builders: test the execution boundary after approval has already failed. Permission enforcement needs to hold even when the approval step says yes.

This was a code simulation with actions recorded in memory. No live model was tested.

The README explains the threat model, signed requests, policy checks, and full results:
https://github.com/danialranjha/validator-execution-gate-lab#technical-walkthrough

The regression check: force approval of an unauthorized action. Verify execution is blocked and the authorized case still succeeds.

## Editorial notes

The request targets the program's `restricted` resource label. A “write” means appending a synthetic action to an in-memory ledger; it does not operate on real files. The unauthorized example is `signed_restricted`; the authorized example is `benign_twin`. “Permission check” means the independent policy. Policy-only and combined modes both give the outcome described. The simulation forces approval and does not show a live model being fooled.

Use established terms such as AI agent, approval, permission, signed request, and execution gate. Name the topic in the first line of each standalone post and each image headline. Keep the explanation concise without substituting vague pronouns or unrelated everyday analogies for the mechanism. The thread's closing link and evidence map support its claims; implementation detail remains in the README.

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
