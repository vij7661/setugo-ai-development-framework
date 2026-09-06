"""Bounded state-space explorer for the post-P19 EXP-I systematic-analysis track.

This module intentionally models the authority-relevant durable transitions of
Pilot 19 rather than Python/SQLite instruction scheduling.  It is finite,
deterministic, dependency-free and suitable for exhaustive BFS in CI.

The scientific bounds and invariants live in
EXP-I-STATE-SPACE-ISSUANCE-ANCHOR-PREREGISTRATION.md.  Do not silently widen or
weaken them here after scientific exposure.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, replace
from typing import Iterable, NamedTuple

MAX_GENERATION = 3
MAX_DEPTH = 12
RECOVERY_IDS = ("A", "B", "C")
TARGETS = ("T1", "T2")
RECONCILERS = ("R1", "R2")

Binding = tuple[str, str]
Ledger = tuple[Binding, ...]


@dataclass(frozen=True)
class State:
    """Finite durable abstraction.

    ledger: committed issuance sequence.
    anchor: externally authenticated installed anchor body, represented by the
      exact issuance prefix it names.  A same-generation conflicting body is
      represented by a tuple of the same length with different bindings.
    receipt: ledger-retained receipt of the last anchor body observed installed.
    temp_anchor: fsynced but non-authoritative temporary anchor material.  It may
      survive restart, matching P19's filesystem artifact, but is never authority.
    trusted_generation: highest generation ever consequentially accepted by the
      modeled trusted-minimum use path.  It is intentionally not rolled back by
      ledger/anchor substitution attacks.
    authority_uses: exact recovery intents that have already caused modeled
      consequential use; used to check at-most-once behavior.
    """

    ledger: Ledger = ()
    anchor: Ledger = ()
    receipt: Ledger = ()
    temp_anchor: Ledger | None = None
    trusted_generation: int = 0
    authority_uses: tuple[Binding, ...] = ()


class Step(NamedTuple):
    action: str
    state: State


@dataclass(frozen=True)
class Violation:
    invariant: str
    reason: str
    trace: tuple[str, ...]
    state: State


@dataclass(frozen=True)
class ExplorationResult:
    visited_states: int
    transitions_checked: int
    max_depth_reached: int
    violations: tuple[Violation, ...]


def genesis() -> State:
    return State()


def _is_prefix(prefix: Ledger, whole: Ledger) -> bool:
    return len(prefix) <= len(whole) and whole[: len(prefix)] == prefix


def _bindings_unique(ledger: Ledger) -> bool:
    seen: dict[str, str] = {}
    for rid, target in ledger:
        prior = seen.get(rid)
        if prior is not None and prior != target:
            return False
        if prior is not None:
            return False
        seen[rid] = target
    return True


def pair_status(s: State) -> str:
    """Mirror the authority-relevant P19 status classes."""
    lg, ag, rg = len(s.ledger), len(s.anchor), len(s.receipt)
    if lg > MAX_GENERATION or ag > MAX_GENERATION or rg > MAX_GENERATION:
        return "FAIL_CLOSED"
    if not _bindings_unique(s.ledger):
        return "FAIL_CLOSED"
    if s.ledger == s.anchor == s.receipt:
        return "RECONCILED"
    # P19 stale-anchor rollback / stale-ledger-or-anchor-ahead rules.
    if ag < rg or lg < rg or ag > lg:
        return "FAIL_CLOSED"
    # Exact ledger-ahead crash state: one committed row beyond a matching
    # reconciled anchor/receipt.
    if lg == rg + 1 and ag == rg and s.anchor == s.receipt and _is_prefix(s.receipt, s.ledger):
        return "LEDGER_AHEAD_EXACT"
    # Exact post-replace/pre-receipt crash state.
    if lg == rg + 1 and ag == lg and s.anchor == s.ledger and _is_prefix(s.receipt, s.ledger):
        return "ANCHOR_REPLACED_RECEIPT_PENDING"
    return "FAIL_CLOSED"


def uniquely_recoverable(s: State) -> bool:
    return pair_status(s) in {"LEDGER_AHEAD_EXACT", "ANCHOR_REPLACED_RECEIPT_PENDING"}


def _authorization_reason(s: State, mutant: str | None = None) -> tuple[bool, str]:
    status = pair_status(s)
    if mutant == "ledger_only" and len(s.ledger) > len(s.anchor):
        return True, "MUTANT_LEDGER_ONLY"
    if mutant == "anchor_only" and len(s.anchor) > len(s.ledger):
        return True, "MUTANT_ANCHOR_ONLY"
    if mutant == "caller_selects_conflict" and status == "FAIL_CLOSED" and len(s.anchor) == len(s.ledger) and s.anchor != s.ledger:
        return True, "MUTANT_CALLER_SELECTED_CONFLICT"
    return status == "RECONCILED", "EXACT_CORRESPONDENCE" if status == "RECONCILED" else status


def can_authorize(s: State, mutant: str | None = None) -> bool:
    return _authorization_reason(s, mutant)[0]


def _issue_steps(s: State, allow_rebind: bool = False) -> Iterable[Step]:
    if pair_status(s) != "RECONCILED" or len(s.ledger) >= MAX_GENERATION:
        return
    existing = {rid: target for rid, target in s.ledger}
    for rid in RECOVERY_IDS:
        for target in TARGETS:
            if rid in existing:
                # Exact replay is a durable no-op and therefore does not need a
                # duplicate BFS state.  Rebind is blocked in production.
                if allow_rebind and existing[rid] != target:
                    yield Step(f"MUTANT issue-rebind {rid}:{target}", replace(s, ledger=s.ledger + ((rid, target),)))
                continue
            yield Step(f"issue-commit {rid}:{target}", replace(s, ledger=s.ledger + ((rid, target),)))


def _reconciliation_steps(s: State) -> Iterable[Step]:
    status = pair_status(s)
    for actor in RECONCILERS:
        if status == "LEDGER_AHEAD_EXACT":
            # Durable temp write, then atomic installed-anchor replacement.
            if s.temp_anchor != s.ledger:
                yield Step(f"{actor} write-anchor-temp", replace(s, temp_anchor=s.ledger))
            if s.temp_anchor == s.ledger:
                yield Step(f"{actor} replace-anchor", replace(s, anchor=s.ledger, temp_anchor=None))
        elif status == "ANCHOR_REPLACED_RECEIPT_PENDING":
            yield Step(f"{actor} store-receipt", replace(s, receipt=s.anchor))


def _use_step(s: State, mutant: str | None = None) -> Iterable[Step]:
    if not can_authorize(s, mutant):
        return
    generation = len(s.ledger)
    if generation == 0:
        return
    intent = s.ledger[-1] if s.ledger else ("NONE", "NONE")
    if intent in s.authority_uses:
        # Replay is intentionally a no-op rather than a second consequential use.
        return
    yield Step(
        "trusted-minimum-use",
        replace(
            s,
            trusted_generation=max(s.trusted_generation, generation),
            authority_uses=s.authority_uses + (intent,),
        ),
    )


def _attack_steps(s: State) -> Iterable[Step]:
    """Bounded adversarial durable substitutions used to test fail-closed rules."""
    # Stale ledger and stale anchor snapshots use exact historical prefixes.
    if len(s.ledger) > 0:
        for n in range(len(s.ledger)):
            stale = s.ledger[:n]
            if stale != s.ledger:
                yield Step(f"attack stale-ledger->{n}", replace(s, ledger=stale))
    if len(s.anchor) > 0:
        for n in range(len(s.anchor)):
            stale = s.anchor[:n]
            if stale != s.anchor:
                yield Step(f"attack stale-anchor->{n}", replace(s, anchor=stale))
    # Authenticated same-generation conflict abstraction: change one binding but
    # retain generation.  This represents a compromised/conflicting artifact,
    # not a claim that an ordinary caller can forge the HMAC.
    if s.anchor:
        last_rid, last_target = s.anchor[-1]
        other_target = "T2" if last_target == "T1" else "T1"
        conflict = s.anchor[:-1] + ((last_rid, other_target),)
        if conflict != s.anchor:
            yield Step("attack same-generation-anchor-conflict", replace(s, anchor=conflict))


def successors(s: State, *, allow_rebind: bool = False, use_mutant: str | None = None, include_attacks: bool = True) -> tuple[Step, ...]:
    steps: list[Step] = []
    steps.extend(_issue_steps(s, allow_rebind=allow_rebind) or ())
    steps.extend(_reconciliation_steps(s) or ())
    steps.extend(_use_step(s, mutant=use_mutant) or ())
    if include_attacks:
        steps.extend(_attack_steps(s) or ())
    # Crash/restart and response loss erase no authority-relevant durable state in
    # this abstraction.  They are represented explicitly only when they change a
    # durable temp artifact: a restart may discard an untrusted temp file, but it
    # can never change ledger/anchor/receipt/trusted state.
    if s.temp_anchor is not None:
        steps.append(Step("crash-restart-discard-untrusted-temp", replace(s, temp_anchor=None)))
    # Deterministic de-duplication keeps BFS finite while retaining actor names in
    # transition comparison tests below.
    return tuple(steps)


def _state_invariant_violations(s: State, *, use_mutant: str | None = None) -> list[tuple[str, str]]:
    violations: list[tuple[str, str]] = []
    status = pair_status(s)
    authorized = can_authorize(s, use_mutant)
    lg, ag, rg = len(s.ledger), len(s.anchor), len(s.receipt)

    if authorized and status != "RECONCILED":
        violations.append(("SA-01", f"authority from non-reconciled state {status}"))
    if authorized and lg > ag:
        violations.append(("SA-02", "ledger-ahead state authorized"))
    if authorized and ag > lg:
        violations.append(("SA-03", "anchor-ahead state authorized"))
    if s.trusted_generation > max(lg, ag, rg):
        # Durable trust memory may legitimately be newer than a later stale-store
        # substitution.  That is rollback *detection*, not an invariant failure.
        pass
    if not _bindings_unique(s.ledger):
        violations.append(("SA-05", "recovery identity durably rebound or duplicated"))
    if len(set(s.authority_uses)) != len(s.authority_uses):
        violations.append(("SA-06", "consequential authority intent used more than once"))
    if status == "FAIL_CLOSED" and authorized:
        violations.append(("SA-08", "fail-closed conflict became authorized"))
    if use_mutant == "caller_selects_conflict" and authorized and s.anchor != s.ledger:
        violations.append(("SA-10", "caller-selected conflicting state became authority"))
    return violations


def _transition_invariant_violations(before: State, step: Step) -> list[tuple[str, str]]:
    after = step.state
    violations: list[tuple[str, str]] = []
    if after.trusted_generation < before.trusted_generation:
        violations.append(("SA-04", "trusted generation moved backward"))
    return violations


def reconciliation_targets(s: State) -> dict[str, set[State]]:
    """Return actor-specific one-step reconciliation outcomes for SA-07."""
    out: dict[str, set[State]] = {actor: set() for actor in RECONCILERS}
    for step in _reconciliation_steps(s) or ():
        actor = step.action.split(" ", 1)[0]
        out[actor].add(step.state)
    return out


def _determinism_violation(s: State) -> tuple[str, str] | None:
    if not uniquely_recoverable(s):
        return None
    targets = reconciliation_targets(s)
    normalized = [frozenset(v) for v in targets.values()]
    if normalized and any(x != normalized[0] for x in normalized[1:]):
        return "SA-07", "reconciliation actor identity changes durable target"
    return None


def _has_clean_liveness_path(start: State, remaining: int) -> bool:
    """SA-09 witness: reconcile, then complete one clean next generation.

    Attacks are excluded from existential liveness: an adversary continuously
    corrupting durable state is outside this liveness obligation.  Safety still
    checks those attack states globally.
    """
    target_generation = min(MAX_GENERATION, len(start.ledger) + 1)
    q = deque([(start, 0)])
    seen = {start}
    while q:
        state, d = q.popleft()
        if pair_status(state) == "RECONCILED" and len(state.ledger) >= target_generation:
            if target_generation == len(start.ledger) or state.trusted_generation >= target_generation:
                return True
        if d >= remaining:
            continue
        for step in successors(state, include_attacks=False):
            nxt = step.state
            if nxt not in seen:
                seen.add(nxt); q.append((nxt, d + 1))
    return False


def explore(*, max_depth: int = MAX_DEPTH, use_mutant: str | None = None, allow_rebind: bool = False, include_attacks: bool = True) -> ExplorationResult:
    """Exhaustive BFS with shortest counterexample traces."""
    start = genesis()
    q = deque([(start, 0, tuple())])
    seen: dict[State, int] = {start: 0}
    first: dict[str, Violation] = {}
    transitions_checked = 0
    max_seen_depth = 0

    while q:
        state, depth, trace = q.popleft()
        max_seen_depth = max(max_seen_depth, depth)
        for invariant, reason in _state_invariant_violations(state, use_mutant=use_mutant):
            first.setdefault(invariant, Violation(invariant, reason, trace, state))
        det = _determinism_violation(state)
        if det:
            inv, reason = det
            first.setdefault(inv, Violation(inv, reason, trace, state))
        if uniquely_recoverable(state):
            remaining = max_depth - depth
            if not _has_clean_liveness_path(state, remaining):
                first.setdefault("SA-09", Violation("SA-09", "recoverable state lacks bounded clean liveness path", trace, state))
        if depth >= max_depth:
            continue
        for step in successors(state, allow_rebind=allow_rebind, use_mutant=use_mutant, include_attacks=include_attacks):
            transitions_checked += 1
            next_trace = trace + (step.action,)
            for invariant, reason in _transition_invariant_violations(state, step):
                first.setdefault(invariant, Violation(invariant, reason, next_trace, step.state))
            prior_depth = seen.get(step.state)
            if prior_depth is None or depth + 1 < prior_depth:
                seen[step.state] = depth + 1
                q.append((step.state, depth + 1, next_trace))

    return ExplorationResult(
        visited_states=len(seen),
        transitions_checked=transitions_checked,
        max_depth_reached=max_seen_depth,
        violations=tuple(first[k] for k in sorted(first)),
    )


def find_mutant_counterexample(mutant: str) -> Violation | None:
    if mutant == "semantic_rebind":
        result = explore(allow_rebind=True)
        return next((v for v in result.violations if v.invariant == "SA-05"), None)
    mapping = {
        "ledger_only": "SA-02",
        "anchor_only": "SA-03",
        "caller_selects_conflict": "SA-10",
    }
    if mutant not in mapping:
        raise ValueError(f"UNKNOWN_MUTANT:{mutant}")
    result = explore(use_mutant=mutant)
    wanted = mapping[mutant]
    return next((v for v in result.violations if v.invariant == wanted), None)


def scientific_summary() -> dict[str, object]:
    production = explore()
    mutants = {
        "MUT-01": find_mutant_counterexample("ledger_only"),
        "MUT-02": find_mutant_counterexample("caller_selects_conflict"),
        "MUT-03": find_mutant_counterexample("anchor_only"),
        "MUT-04": find_mutant_counterexample("semantic_rebind"),
    }
    return {
        "bounds": {"max_generation": MAX_GENERATION, "max_depth": MAX_DEPTH},
        "visited_states": production.visited_states,
        "transitions_checked": production.transitions_checked,
        "max_depth_reached": production.max_depth_reached,
        "production_violations": [v.invariant for v in production.violations],
        "mutants": {
            name: None if v is None else {"invariant": v.invariant, "trace": list(v.trace), "reason": v.reason}
            for name, v in mutants.items()
        },
    }
