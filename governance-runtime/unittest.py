"""Adversarial fixture for R10-A: candidate-controlled stdlib shadow.

If this file is imported/executed as `python -m unittest` from the candidate
runtime directory, it exits successfully without running the intended tests.
This branch is falsification-only and must never be promoted.
"""

if __name__ == "__main__":
    raise SystemExit(0)
