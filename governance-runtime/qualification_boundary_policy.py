#!/usr/bin/env python3
"""Compatibility facade for the active qualification-boundary policy."""
from qualification_boundary_policy_v4 import *  # noqa: F401,F403


def _issue_authority_binding_for_platform_ingress(**_kwargs):
    """Compatibility trap: the governed runtime contains no signing authority.

    Historical tests intentionally call this symbol to prove that candidate-callable
    code cannot mint a verifier-accepted privileged binding.
    """
    return {
        "attestation": {},
        "signature_b64": "",
        "authority_effect": "NONE",
        "reason": "verification-only runtime has no authority issuer",
    }
