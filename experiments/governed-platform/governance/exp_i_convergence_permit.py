from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from typing import Any, Iterable, Tuple

from exp_i_claim_convergence_gate import (
    GateState,
    ReviewClaim,
    VerificationArtifact,
    evaluate_review_gate,
)
from tri_reviewer_convergence import decide_convergence


def _digest_json(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verification_digest(verification: VerificationArtifact) -> str:
    return _digest_json({
        "issuer": verification.issuer,
        "platform_issued": verification.platform_issued,
        "valid": verification.valid,
        "case_id": verification.case_id,
        "primary_failure_class": verification.primary_failure_class,
        "authorized_artifact_scope": list(verification.canonical_scope()),
    })


def signals_digest(signals: dict[str, Any]) -> str:
    return _digest_json(signals)


@dataclass(frozen=True)
class ConvergencePermit:
    issuer: str
    case_id: str
    primary_failure_class: str
    authorized_artifact_scope: Tuple[str, ...]
    verification_digest: str
    signals_digest: str
    issuance_epoch: int
    nonce: str
    signature: str

    def payload(self) -> dict[str, Any]:
        return {
            "issuer": self.issuer,
            "case_id": self.case_id,
            "primary_failure_class": self.primary_failure_class,
            "authorized_artifact_scope": list(self.authorized_artifact_scope),
            "verification_digest": self.verification_digest,
            "signals_digest": self.signals_digest,
            "issuance_epoch": self.issuance_epoch,
            "nonce": self.nonce,
        }


@dataclass(frozen=True)
class PermitDecision:
    state: str
    reasons: Tuple[str, ...]
    terminal_convergence: bool
    reviewer_generated_authority: bool = False
    production_authority: bool = False


class ConvergencePermitAuthority:
    ISSUER = "exp-i-platform-convergence-authority"

    def __init__(self, signing_key: bytes, issuance_epoch: int = 1):
        if not signing_key:
            raise ValueError("signing_key required")
        if issuance_epoch < 1:
            raise ValueError("issuance_epoch must be positive")
        self._signing_key = bytes(signing_key)
        self._issuance_epoch = issuance_epoch
        self._consumed_nonces: set[str] = set()
        self._nonce_bindings: dict[str, str] = {}

    @property
    def issuance_epoch(self) -> int:
        return self._issuance_epoch

    def advance_epoch(self) -> None:
        self._issuance_epoch += 1

    def _sign(self, payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        return hmac.new(self._signing_key, encoded, hashlib.sha256).hexdigest()

    def _valid_signature(self, permit: ConvergencePermit) -> bool:
        return hmac.compare_digest(permit.signature, self._sign(permit.payload()))

    def issue(
        self,
        reviews: Iterable[ReviewClaim],
        verification: VerificationArtifact,
        signals: dict[str, Any],
        *,
        nonce: str | None = None,
    ) -> ConvergencePermit:
        claim = evaluate_review_gate(tuple(reviews), verification)
        if claim.state != GateState.ELIGIBLE_FOR_GOVERNANCE_GATE:
            raise PermissionError(f"claim gate not eligible: {claim.state.value}")

        nonce = nonce or secrets.token_hex(16)
        if not nonce:
            raise ValueError("nonce required")

        binding = _digest_json({
            "case_id": claim.case_id,
            "primary_failure_class": claim.canonical_primary_failure_class,
            "authorized_artifact_scope": list(claim.canonical_artifact_scope),
            "verification_digest": verification_digest(verification),
            "signals_digest": signals_digest(signals),
            "issuance_epoch": self._issuance_epoch,
        })
        prior = self._nonce_bindings.get(nonce)
        if prior is not None and prior != binding:
            raise PermissionError("nonce semantic rebinding denied")
        self._nonce_bindings.setdefault(nonce, binding)

        payload = {
            "issuer": self.ISSUER,
            "case_id": claim.case_id,
            "primary_failure_class": claim.canonical_primary_failure_class,
            "authorized_artifact_scope": list(claim.canonical_artifact_scope),
            "verification_digest": verification_digest(verification),
            "signals_digest": signals_digest(signals),
            "issuance_epoch": self._issuance_epoch,
            "nonce": nonce,
        }
        return ConvergencePermit(signature=self._sign(payload), **payload)

    def consume(
        self,
        permit: ConvergencePermit,
        reviews: Iterable[ReviewClaim],
        verification: VerificationArtifact,
        signals: dict[str, Any],
    ) -> PermitDecision:
        reviews = tuple(reviews)
        if permit.issuer != self.ISSUER:
            return PermitDecision("DENIED", ("non-platform permit issuer",), False)
        if not self._valid_signature(permit):
            return PermitDecision("DENIED", ("invalid permit signature",), False)
        if permit.issuance_epoch != self._issuance_epoch:
            return PermitDecision("DENIED", ("stale convergence permit epoch",), False)
        if permit.nonce in self._consumed_nonces:
            return PermitDecision("DENIED", ("convergence permit already consumed",), False)

        claim = evaluate_review_gate(reviews, verification)
        if claim.state != GateState.ELIGIBLE_FOR_GOVERNANCE_GATE:
            return PermitDecision("DENIED", (f"claim gate changed: {claim.state.value}",), False)

        if permit.case_id != claim.case_id:
            return PermitDecision("DENIED", ("permit case binding mismatch",), False)
        if permit.primary_failure_class != claim.canonical_primary_failure_class:
            return PermitDecision("DENIED", ("permit primary-class binding mismatch",), False)
        if tuple(permit.authorized_artifact_scope) != tuple(claim.canonical_artifact_scope):
            return PermitDecision("DENIED", ("permit artifact-scope binding mismatch",), False)
        if permit.verification_digest != verification_digest(verification):
            return PermitDecision("DENIED", ("permit verification binding mismatch",), False)
        if permit.signals_digest != signals_digest(signals):
            return PermitDecision("DENIED", ("permit convergence-signal binding mismatch",), False)

        binding = _digest_json({
            "case_id": claim.case_id,
            "primary_failure_class": claim.canonical_primary_failure_class,
            "authorized_artifact_scope": list(claim.canonical_artifact_scope),
            "verification_digest": verification_digest(verification),
            "signals_digest": signals_digest(signals),
            "issuance_epoch": permit.issuance_epoch,
        })
        if self._nonce_bindings.get(permit.nonce) != binding:
            return PermitDecision("DENIED", ("permit nonce binding mismatch",), False)

        # Consumption occurs before invoking the low-level convergence evaluator.
        self._consumed_nonces.add(permit.nonce)
        terminal = decide_convergence(signals)
        return PermitDecision(
            state=terminal.state,
            reasons=terminal.reasons,
            terminal_convergence=terminal.state in {"CONVERGED_PASS", "CONVERGED_WITH_DISSENT", "CONVERGED_FAIL"},
            reviewer_generated_authority=False,
            production_authority=False,
        )
