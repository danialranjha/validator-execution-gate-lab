# Publication drafts

Drafts only; not posted. Use the sketch-style header for the opening post and the body diagram for the example. The technical detail lives in the README.

## X thread

### 1/4

I made the approval step say “yes” to something it should never allow.

Could a separate rule still stop it?

I built a small code simulation to check. No live AI was involved.

### 2/4

The task: put a note in the allowed box.

The bad request: put it in the off-limits box instead.

With approval alone, the note got through. Add a separate rule check, and it stopped. The allowed note still worked.

### 3/4

My takeaway for AI agents: plan for the approval step to be wrong.

A second “yes” is not the useful test. Ask what still stops the action when that “yes” should have been “no.”

This demo tests a rule in code. It doesn't show how often an AI makes that mistake.

### 4/4

The full explanation, code, and results:
https://github.com/danialranjha/validator-execution-gate-lab#technical-walkthrough

The check to add: force a “yes.” The forbidden action must stop, and the allowed one must still work.

## LinkedIn post

What stops an AI agent when its approval step gets it wrong?

I built a small code simulation around that question. No live AI was involved.

The task was simple: put a note in the allowed box. I then tried the off-limits box and made the approval step say “yes” anyway.

With approval alone, the note got through.

With a separate rule checking where the note was allowed to go, it stopped. The note for the allowed box still went through.

My takeaway: when building an agent, test what happens after a bad approval. There needs to be something that can still stop the action.

This was a toy example. It tests a rule in code, not how often an AI makes mistakes.

I put the technical explanation, research source, code, and full results here:
https://github.com/danialranjha/validator-execution-gate-lab#technical-walkthrough

The check to add: force a “yes.” The forbidden action must stop, and the allowed one must still work.

## Editorial notes

“Box” is the plain-language name for a resource label in the program. Notes are only records in memory. The off-limits example is the recorded `signed_restricted` fixture; the allowed example is `benign_twin`. “Separate rule” refers to the independent policy check. Both policy-only and combined modes give the outcome described. The simulation forces approval; it does not demonstrate a live model being fooled.

The social text deliberately focuses on this one comparison. The README covers the second comparison (forged approval credentials), exact-action binding, replay, test counts, limitations, and source attribution. The four-part thread shares its technical evidence link in the closing post; the mapping below supports the whole thread and LinkedIn draft.

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
