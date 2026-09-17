"""Check that critical tests fail when either gate is removed in a temporary copy."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    root = Path(__file__).resolve().parent
    source = (root / "experiment.py").read_text(encoding="utf-8")
    checks = []
    mutations = [
        ("remove_policy", "and (not policy_on or allowed)", "and True",
         "test_stolen_key_requires_policy_and_benign_twin_survives"),
        ("remove_token", "(not token_on or valid)", "True",
         "test_wrong_signer_for_allowed_action_requires_signature"),
    ]
    for name, before, after, test in mutations:
        if source.count(before) != 1:
            raise RuntimeError("Mutation target changed; review the mutation check")
        with tempfile.TemporaryDirectory(prefix="gate-mutation-") as temporary:
            folder = Path(temporary)
            (folder / "experiment.py").write_text(source.replace(before, after, 1), encoding="utf-8")
            shutil.copy(root / "tests/test_experiment.py", folder / "test_experiment.py")
            testcase = "test_experiment.AuthorizationTests." + test
            run = subprocess.run([sys.executable, "-m", "unittest", testcase],
                                 cwd=folder, capture_output=True, text=True, timeout=30)
            detected = run.returncode != 0 and "FAIL:" in run.stderr
            checks.append({"mutation": name, "targeted_test": testcase,
                           "mutation_detected": detected, "exit_code": run.returncode})
    artifact = {"purpose": "Prove critical tests detect removing either enforcement gate",
                "mutations": checks}
    (root / "artifacts").mkdir(exist_ok=True)
    (root / "artifacts/mutation-checks.json").write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2))
    return 0 if all(row["mutation_detected"] for row in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
