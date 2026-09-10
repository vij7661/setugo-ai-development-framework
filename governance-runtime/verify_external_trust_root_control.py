#!/usr/bin/env python3
"""Fail-closed verifier for the external GitHub ruleset protecting TESTING trust-root changes.

The live GitHub Actions token can verify externally visible branch-rule semantics but
cannot see repository-admin bypass actor configuration. That admin-only state is
qualified separately and preserved as authorized governance evidence.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from typing import Any, Mapping

REPOSITORY = "vij7661/setugo-ai-development-framework"
RULESET_ID = 22736961
TARGET_REF = "refs/heads/phase/testing"
REQUIRED_STATUS_CONTEXT = "falsify-qualification-boundary"


class ExternalControlError(RuntimeError):
    pass


def validate_ruleset_document(
    payload: Mapping[str, Any], *, require_admin_bypass_visibility: bool = True
) -> tuple[bool, str]:
    if payload.get("id") != RULESET_ID:
        return False, "unexpected ruleset id"
    if payload.get("target") != "branch":
        return False, "ruleset does not target branches"
    if payload.get("enforcement") != "active":
        return False, "ruleset enforcement is not active"

    conditions = payload.get("conditions")
    if not isinstance(conditions, Mapping):
        return False, "ruleset conditions are missing"
    ref_name = conditions.get("ref_name")
    if not isinstance(ref_name, Mapping):
        return False, "ruleset ref_name condition is missing"
    includes = ref_name.get("include")
    if not isinstance(includes, list) or TARGET_REF not in includes:
        return False, "phase/testing is not explicitly protected by the ruleset"

    bypass = payload.get("bypass_actors")
    if require_admin_bypass_visibility:
        if not isinstance(bypass, list):
            return False, "ruleset bypass state is missing"
        if bypass:
            return False, "ruleset contains bypass actors"
    elif isinstance(bypass, list) and bypass:
        return False, "ruleset contains bypass actors"

    rules = payload.get("rules")
    if not isinstance(rules, list):
        return False, "ruleset rules are missing"
    by_type = {
        rule.get("type"): rule
        for rule in rules
        if isinstance(rule, Mapping) and isinstance(rule.get("type"), str)
    }

    if "deletion" not in by_type:
        return False, "branch deletion protection is missing"
    if "non_fast_forward" not in by_type:
        return False, "force-push protection is missing"

    pull_request = by_type.get("pull_request")
    if not isinstance(pull_request, Mapping):
        return False, "pull-request protection is missing"
    pr_params = pull_request.get("parameters")
    if not isinstance(pr_params, Mapping):
        return False, "pull-request rule parameters are missing"
    if int(pr_params.get("required_approving_review_count", 0)) < 1:
        return False, "at least one approving review is required"
    if pr_params.get("required_review_thread_resolution") is not True:
        return False, "review-thread resolution is not required"

    status = by_type.get("required_status_checks")
    if not isinstance(status, Mapping):
        return False, "required-status-check protection is missing"
    status_params = status.get("parameters")
    if not isinstance(status_params, Mapping):
        return False, "required-status-check parameters are missing"
    if status_params.get("strict_required_status_checks_policy") is not True:
        return False, "strict required-status-check policy is disabled"
    checks = status_params.get("required_status_checks")
    if not isinstance(checks, list):
        return False, "required status checks are missing"
    contexts = {
        item.get("context")
        for item in checks
        if isinstance(item, Mapping)
    }
    if REQUIRED_STATUS_CONTEXT not in contexts:
        return False, f"required status context is missing: {REQUIRED_STATUS_CONTEXT}"

    if require_admin_bypass_visibility:
        return True, "external TESTING trust-root ruleset and bypass state satisfy the frozen control contract"
    return True, "externally visible TESTING trust-root rules satisfy the frozen runner-visible contract"


def fetch_live_ruleset() -> Mapping[str, Any]:
    url = f"https://api.github.com/repos/{REPOSITORY}/rulesets/{RULESET_ID}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "setugo-testing-trust-root-control",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            raw = response.read()
    except Exception as exc:
        raise ExternalControlError(
            f"unable to retrieve external trust-root ruleset: {type(exc).__name__}"
        ) from exc
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise ExternalControlError("external trust-root ruleset response is malformed") from exc
    if not isinstance(payload, Mapping):
        raise ExternalControlError("external trust-root ruleset response is not an object")
    return payload


def main() -> int:
    try:
        payload = fetch_live_ruleset()
        ok, reason = validate_ruleset_document(
            payload, require_admin_bypass_visibility=False
        )
    except ExternalControlError as exc:
        print(f"FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1
    if not ok:
        print(f"FAIL_CLOSED: {reason}", file=sys.stderr)
        return 1
    print(f"PASS_BOUNDED_EVIDENCE_ONLY: {reason}")
    print(
        "ADMIN_BYPASS_STATE: qualified separately by authorized repository-governance evidence; "
        "runner token does not claim visibility"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
