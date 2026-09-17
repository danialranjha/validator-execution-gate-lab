import copy
from dataclasses import FrozenInstanceError, replace
import inspect
import json
import secrets
import unittest

from experiment import (Action, BENIGN, Executor, MODES, RESTRICTED, TASK,
                        issue, policy_allows, run_matrix)


class AuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.key = secrets.token_bytes(32)

    def commits(self, action, token):
        results = []
        for mode in MODES:
            gate = Executor(mode, self.key)
            outcome = gate.dispatch(action, token, validator_approved=True)
            self.assertEqual(outcome["committed"], bool(gate.sink))
            self.assertEqual(gate.sink, [vars(action)] if outcome["committed"] else [])
            results.append(len(gate.sink))
        return results

    def test_stolen_key_requires_policy_and_benign_twin_survives(self):
        self.assertEqual(self.commits(RESTRICTED, issue(self.key, RESTRICTED, "n")), [1, 1, 0, 0])
        self.assertEqual(self.commits(BENIGN, issue(self.key, BENIGN, "n")), [1, 1, 1, 1])

    def test_wrong_signer_for_allowed_action_requires_signature(self):
        token = issue(secrets.token_bytes(32), BENIGN, "n")
        self.assertEqual(self.commits(BENIGN, token), [1, 0, 1, 0])

    def test_changed_text_is_policy_allowed_but_bound_to_capability(self):
        changed = replace(BENIGN, text="another synthetic note")
        self.assertTrue(policy_allows(changed))
        self.assertEqual(self.commits(changed, issue(self.key, BENIGN, "n")), [1, 0, 1, 0])

    def test_every_action_field_is_bound(self):
        token = issue(self.key, BENIGN, "n")
        for field in ("task_id", "verb", "resource", "text"):
            with self.subTest(field=field):
                changed = replace(BENIGN, **{field: "changed"})
                gate = Executor("token_only", self.key)
                result = gate.dispatch(changed, token, validator_approved=True)
                self.assertEqual(result["token_reason"], "action_mismatch")
                self.assertEqual(gate.sink, [])

    def test_valid_signature_for_other_task_is_rejected(self):
        other = replace(BENIGN, task_id="other-task")
        gate = Executor("token_only", self.key, trusted_task=TASK)
        result = gate.dispatch(other, issue(self.key, other, "n"), validator_approved=True)
        self.assertEqual(result["token_reason"], "wrong_task")
        self.assertEqual(gate.sink, [])

    def test_token_payload_tampering_is_detected(self):
        token = issue(self.key, BENIGN, "n")
        token["payload"]["action"]["resource"] = "restricted"
        gate = Executor("token_only", self.key)
        outcome = gate.dispatch(RESTRICTED, token, validator_approved=True)
        self.assertEqual(outcome["token_reason"], "invalid_signature")
        self.assertEqual(gate.sink, [])

    def test_replay_is_rejected_but_new_nonce_is_allowed(self):
        for mode in ("token_only", "token_and_policy"):
            with self.subTest(mode=mode):
                gate = Executor(mode, self.key)
                token = issue(self.key, BENIGN, "one")
                self.assertTrue(gate.dispatch(BENIGN, token, validator_approved=True)["committed"])
                self.assertEqual(gate.dispatch(BENIGN, token, validator_approved=True)["token_reason"], "replay")
                self.assertEqual(len(gate.sink), 1)
                gate.dispatch(BENIGN, issue(self.key, BENIGN, "two"), validator_approved=True)
                self.assertEqual(len(gate.sink), 2)

    def test_missing_and_malformed_capabilities_fail_closed(self):
        valid = issue(self.key, BENIGN, "n")
        examples = [None, [], {}, {"payload": None, "mac": "0" * 64},
                    {**valid, "extra": True}]
        for field, bad in (("version", True), ("version", 2), ("nonce", ""),
                           ("nonce", []), ("action", [])):
            token = copy.deepcopy(valid)
            token["payload"][field] = bad
            examples.append(token)
        for bad_mac in (None, [], "x" * 64, "é" * 64, "0"):
            examples.append({**valid, "mac": bad_mac})
        for token in examples:
            with self.subTest(token_type=type(token).__name__):
                gate = Executor("token_and_policy", self.key)
                self.assertFalse(gate.dispatch(BENIGN, token, validator_approved=True)["committed"])
                self.assertEqual(gate.sink, [])

    def test_canonical_key_order_does_not_change_identity(self):
        token = issue(self.key, BENIGN, "n")
        token["payload"]["action"] = dict(reversed(list(token["payload"]["action"].items())))
        gate = Executor("token_and_policy", self.key)
        self.assertTrue(gate.dispatch(BENIGN, token, validator_approved=True)["committed"])
        self.assertEqual(gate.sink, [vars(BENIGN)])

    def test_no_explicit_approval_means_no_commit(self):
        for mode in MODES:
            for approval in (False, None, 1, "approved"):
                gate = Executor(mode, self.key)
                gate.dispatch(BENIGN, issue(self.key, BENIGN, "n"), validator_approved=approval)
                self.assertEqual(gate.sink, [])

    def test_policy_receives_only_action_and_ignores_text(self):
        self.assertEqual(list(inspect.signature(policy_allows).parameters), ["action"])
        for text in ("allowed", "denied", "gold-safe", "gold-unsafe"):
            self.assertTrue(policy_allows(replace(BENIGN, text=text)))
            self.assertFalse(policy_allows(replace(RESTRICTED, text=text)))

    def test_action_and_sink_snapshot_are_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            BENIGN.resource = "restricted"
        with self.assertRaises(ValueError):
            Action(TASK, "append_note", "inbox", [])
        gate = Executor("token_and_policy", self.key)
        gate.dispatch(BENIGN, issue(self.key, BENIGN, "n"), validator_approved=True)
        snapshot = gate.sink
        snapshot[0]["resource"] = "restricted"
        snapshot.append({})
        self.assertEqual(gate.sink, [vars(BENIGN)])

    def test_matrix_matches_expectations_and_actual_events(self):
        report = run_matrix()
        self.assertEqual(len(report["rows"]), 40)
        self.assertEqual(len(report["events"]), 44)
        self.assertTrue(report["all_expected_outcomes_matched"])
        for mode, count in zip(MODES, (11, 3, 7, 2)):
            events = [e for e in report["events"] if e["mode"] == mode]
            self.assertEqual(sum(e["sink_record"] is not None for e in events), count)
            self.assertEqual(report["summary"][mode]["committed"], count)
        self.assertEqual(report, run_matrix())

    def test_trace_contains_no_capabilities_or_keys(self):
        report = run_matrix()
        def walk(obj):
            if isinstance(obj, dict):
                self.assertFalse({"mac", "payload", "nonce", "key", "token"} & obj.keys())
                for value in obj.values():
                    walk(value)
            elif isinstance(obj, list):
                for value in obj:
                    walk(value)
        walk(report)
        self.assertEqual(report["live_model_calls"], 0)
        json.dumps(report)


if __name__ == "__main__":
    unittest.main()
