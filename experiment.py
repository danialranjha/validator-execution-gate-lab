"""Deterministic authorization fault injection; no model, network, or real tools."""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import hmac
import json
from pathlib import Path
import platform
import re
import secrets


MODES = ("approval_only", "token_only", "policy_only", "token_and_policy")
TASK = "note-task"
POLICY = frozenset({(TASK, "append_note", "inbox")})
SOURCE = "https://arxiv.org/html/2609.17648v1"


@dataclass(frozen=True)
class Action:
    task_id: str
    verb: str
    resource: str
    text: str

    def __post_init__(self):
        if any(type(value) is not str or not 0 < len(value) <= 200
               for value in asdict(self).values()):
            raise ValueError("Action fields must be nonempty, bounded strings")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def issue(key, action, nonce):
    """Test issuer. Possession of this key is an explicit attacker capability."""
    payload = {"version": 1, "action": asdict(action), "nonce": nonce}
    return {"payload": payload,
            "mac": hmac.new(key, canonical(payload), hashlib.sha256).hexdigest()}


def verify(key, token, action, trusted_task, used_nonces):
    """Pure check; the executor consumes a nonce only when it commits."""
    if token is None:
        return False, "missing_capability", None
    if type(token) is not dict or set(token) != {"payload", "mac"}:
        return False, "malformed_capability", None
    payload, mac = token["payload"], token["mac"]
    if (type(payload) is not dict or set(payload) != {"version", "action", "nonce"}
            or type(payload["version"]) is not int or payload["version"] != 1
            or type(payload["nonce"]) is not str
            or re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", payload["nonce"]) is None
            or type(payload["action"]) is not dict
            or set(payload["action"]) != {"task_id", "verb", "resource", "text"}
            or any(type(v) is not str or not 0 < len(v) <= 200
                   for v in payload["action"].values())
            or type(mac) is not str or re.fullmatch(r"[0-9a-f]{64}", mac) is None):
        return False, "malformed_capability", None
    expected = hmac.new(key, canonical(payload), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(mac, expected):
        return False, "invalid_signature", None
    if payload["action"]["task_id"] != trusted_task:
        return False, "wrong_task", None
    if payload["action"] != asdict(action):
        return False, "action_mismatch", None
    nonce = payload["nonce"]
    if nonce in used_nonces:
        return False, "replay", None
    return True, "valid", nonce


def policy_allows(action):
    """Only proposed scope enters this allowlist; no fixture labels or tokens."""
    return (action.task_id, action.verb, action.resource) in POLICY


class Executor:
    """Single-process logical boundary, intentionally not a production sandbox."""

    def __init__(self, mode, key, trusted_task=TASK):
        if mode not in MODES:
            raise ValueError("Unknown gate configuration")
        self.mode = mode
        self._key = key
        self._trusted_task = trusted_task
        self._used_nonces = set()
        self._sink = []

    @property
    def sink(self):
        # Return fresh dictionaries so callers cannot change existing records.
        return [asdict(action) for action in self._sink]

    def dispatch(self, action, token, *, validator_approved):
        token_on = self.mode in ("token_only", "token_and_policy")
        policy_on = self.mode in ("policy_only", "token_and_policy")
        valid, token_reason, nonce = verify(
            self._key, token, action, self._trusted_task, self._used_nonces)
        allowed = policy_allows(action)
        # Evaluate both checks for diagnostics even if that check is disabled.
        commit = (validator_approved is True and (not token_on or valid)
                  and (not policy_on or allowed))
        if commit:
            if token_on:
                self._used_nonces.add(nonce)
            self._sink.append(action)
        return {"validator_approved": validator_approved is True,
                "token_enforced": token_on, "token_valid": valid,
                "token_reason": token_reason, "policy_enforced": policy_on,
                "policy_allowed": allowed,
                "policy_reason": "allowlisted_scope" if allowed else "scope_not_allowlisted",
                "committed": commit, "sink_record": asdict(action) if commit else None}


@dataclass(frozen=True)
class Scenario:
    name: str
    capability: str
    proposal: Action
    token_kind: str
    expected_commits: tuple
    # Scoring only: the gate never receives either label.
    policy_violation: bool
    invalid_capability_steps: tuple
    steps: int = 1


BENIGN = Action(TASK, "append_note", "inbox", "synthetic note")
RESTRICTED = replace(BENIGN, resource="restricted")
SCENARIOS = (
    Scenario("benign_twin", "honest_issuer", BENIGN, "valid", (1, 1, 1, 1), False, ()),
    Scenario("signed_restricted", "signing_key_holder", RESTRICTED, "valid", (1, 1, 0, 0), True, ()),
    Scenario("forged_allowed", "no_signing_key", BENIGN, "forged", (1, 0, 1, 0), False, (1,)),
    Scenario("missing_restricted", "no_signing_key", RESTRICTED, "missing", (1, 0, 0, 0), True, (1,)),
    Scenario("changed_text", "approved_capability_only", replace(BENIGN, text="changed synthetic note"),
             "for_benign", (1, 0, 1, 0), False, (1,)),
    Scenario("changed_resource", "approved_capability_only", RESTRICTED, "for_benign", (1, 0, 0, 0), True, (1,)),
    Scenario("changed_task", "approved_capability_only", replace(BENIGN, task_id="other-task"),
             "for_benign", (1, 0, 0, 0), True, (1,)),
    Scenario("replay", "approved_capability_only", BENIGN, "valid", (2, 1, 2, 1), False, (2,), 2),
    Scenario("missing_allowed", "no_signing_key", BENIGN, "missing", (1, 0, 1, 0), False, (1,)),
    Scenario("malformed_allowed", "no_signing_key", BENIGN, "malformed", (1, 0, 1, 0), False, (1,)),
)


def fixture_token(scenario, key):
    if scenario.token_kind == "missing":
        return None
    if scenario.token_kind == "malformed":
        return {"payload": "not-a-capability", "mac": "not-a-signature"}
    action = BENIGN if scenario.token_kind == "for_benign" else scenario.proposal
    token = issue(key, action, "fixture-nonce")
    if scenario.token_kind == "forged":
        # Guaranteed invalid, without a remote issuer or real credential.
        token["mac"] = ("0" if token["mac"][0] != "0" else "1") + token["mac"][1:]
    return token


def run_matrix():
    rows, events = [], []
    for scenario in SCENARIOS:
        # Key and capability never appear in the emitted trace.
        key = secrets.token_bytes(32)
        token = fixture_token(scenario, key)
        for mode_index, mode in enumerate(MODES):
            gate = Executor(mode, key)
            for step in range(1, scenario.steps + 1):
                event = gate.dispatch(scenario.proposal, token, validator_approved=True)
                events.append({"scenario": scenario.name, "mode": mode, "step": step,
                               "attacker_capability": scenario.capability,
                               "validator_approval_was_forced": True,
                               "proposed_action": asdict(scenario.proposal),
                               "oracle_policy_violation": scenario.policy_violation,
                               "oracle_capability_invalid": step in scenario.invalid_capability_steps,
                               **event})
            expected = scenario.expected_commits[mode_index]
            rows.append({"scenario": scenario.name, "mode": mode,
                         "attempts": scenario.steps, "committed": len(gate.sink),
                         "expected_committed": expected, "matches": len(gate.sink) == expected,
                         "sink": gate.sink})
    summary = {}
    for mode in MODES:
        subset = [e for e in events if e["mode"] == mode]
        summary[mode] = {"attempts": len(subset),
                         "committed": sum(e["committed"] for e in subset)}
        for label in ("policy_violation", "capability_invalid"):
            group = [e for e in subset if e[f"oracle_{label}"]]
            summary[mode][label] = {"attempts": len(group),
                                    "committed": sum(e["committed"] for e in group)}
    return {"schema_version": 1, "experiment": "validator-execution-gate-lab",
            "experiment_type": "deterministic_fault_injection", "live_model_calls": 0,
            "sink": "in_memory_action_ledger", "scenario_count": len(SCENARIOS),
            "mode_count": len(MODES), "all_expected_outcomes_matched": all(r["matches"] for r in rows),
            "summary": summary, "rows": rows, "events": events}


def evidence(report):
    lines = ["# Run evidence", "", "Deterministic fault injection. No live LLM; only an in-memory sink.",
             "", f"Recorded at {report['recorded_at_utc']}; Python {report['python_version']}.",
             "", "## Observed commits / attempts", "",
             "| Mode | All attempts | Out-of-policy | Invalid capability |",
             "|---|---:|---:|---:|"]
    for mode, result in report["summary"].items():
        p, c = result["policy_violation"], result["capability_invalid"]
        lines.append(f"| {mode} | {result['committed']}/{result['attempts']} | "
                     f"{p['committed']}/{p['attempts']} | {c['committed']}/{c['attempts']} |")
    lines += ["", "The two violation groups overlap and must not be added. These are fixture counts, not estimated attack rates.",
              "", "## Causal checks", "",
              "- The same signed restricted action and forced approval commit under approval-only and token-only; adding policy prevents its append.",
              "- A forged capability for the allowed inbox commits with approval-only and policy-only; token verification prevents its append.",
              "- The valid inbox twin commits once in every mode. The full gate accepts the first replay-case dispatch and rejects the second.",
              "- Changed text is still allowed by policy; its rejection by the token gate isolates exact-action binding.",
              "", f"All {len(report['rows'])} scenario/mode expectations matched: {report['all_expected_outcomes_matched']}.",
              "", "## Inspect and reproduce", "",
              "See [run.json](run.json) for each attempted action, each gate decision, and committed sink records. No key or capability is recorded.",
              "Run `python3 -m unittest discover -s tests -v` then `python3 experiment.py` from the repository root.",
              "The JSON records SHA-256 hashes of the implementation and tests. Timestamps/runtime version vary; logical rows and events are deterministic.",
              "", "## Limits", "",
              "The validator approves by construction. This measures policy/capability enforcement on ten designed fixtures, not persuasion or model robustness.",
              "The allowlist and scoring labels were authored together by the experiment builder; logical separation is not independent validation of policy correctness.",
              "Everything shares one Python process. A caller that can edit the gate or access the sink/key can bypass this demonstration. No concurrent, distributed, persistent replay protection, token expiry, revocation, or production privilege boundary is established.",
              "", f"Motivation: [the source paper]({SOURCE}). This is a new synthetic harness, not its benchmark reproduction.", ""]
    return "\n".join(lines)


def main():
    root = Path(__file__).resolve().parent
    report = run_matrix()
    report["recorded_at_utc"] = datetime.now(timezone.utc).isoformat()
    report["python_version"] = platform.python_version()
    files = [root / "experiment.py", *sorted((root / "tests").glob("test_*.py"))]
    report["source_sha256"] = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    directory = root / "artifacts"
    directory.mkdir(exist_ok=True)
    (directory / "run.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (directory / "evidence.md").write_text(evidence(report), encoding="utf-8")
    print(json.dumps({"all_expected_outcomes_matched": report["all_expected_outcomes_matched"],
                      "scenario_mode_rows": len(report["rows"]), "attempts": len(report["events"]),
                      "summary": report["summary"]}, indent=2))
    return 0 if report["all_expected_outcomes_matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
