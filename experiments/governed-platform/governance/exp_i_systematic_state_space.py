"""Bounded systematic state-space/fault explorer for the EXP-I Pilot 19 protocol.

This is deliberately dependency-light and deterministic.  It does not claim a
formal proof.  The scientific bounds/invariants are frozen in
EXP-I-SYSTEMATIC-STATE-SPACE-PREREGISTRATION.md.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import asdict, dataclass, replace
import json
from typing import Iterable, NamedTuple

MAX_GENERATION = 2
MAX_DEPTH = 14
MAX_CRASHES = 2
MAX_STALE_LEDGER = 1
MAX_STALE_ANCHOR = 1
MAX_CONFLICT_ANCHOR = 1
MAX_STATES = 250_000
RECOVERY_IDS = ("REC-A", "REC-B")
TARGETS = ("TARGET-X", "TARGET-Y")
WORKERS = ("W1", "W2")

Binding = tuple[str, str]
Ledger = tuple[Binding, ...]
Worker = tuple[str, str, Ledger]  # worker_id, stage, deterministic target

RECONCILED = "RECONCILED"
LEDGER_AHEAD_EXACT = "LEDGER_AHEAD_EXACT"
ANCHOR_REPLACED_RECEIPT_PENDING = "ANCHOR_REPLACED_RECEIPT_PENDING"
FAIL_CLOSED = "FAIL_CLOSED"


@dataclass(frozen=True)
class State:
    ledger: Ledger = ()
    anchor: Ledger = ()
    receipt: Ledger = ()
    known_ledgers: tuple[Ledger, ...] = ((),)
    known_anchors: tuple[Ledger, ...] = ((),)
    issue: tuple[str, str, str] | None = None  # recovery_id, target, BEGIN|INSERTED
    workers: tuple[Worker, ...] = ()
    temp_anchor: Ledger | None = None
    response_pending: Binding | None = None
    response_outcome: str = "NONE"
    accepted_generation: int = 0
    crashes: int = 0
    stale_ledger_faults: int = 0
    stale_anchor_faults: int = 0
    conflict_anchor_faults: int = 0


class Edge(NamedTuple):
    label: str
    state: State
    fault: bool = False


@dataclass(frozen=True)
class Violation:
    invariant: str
    detail: str
    before: State
    transition: str
    after: State


@dataclass(frozen=True)
class AnalysisResult:
    status: str
    states: int
    transitions: int
    max_depth_reached: int
    classifications: dict[str, int]
    invariant_checks: int
    liveness_states_checked: int
    counterexample: dict | None

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def genesis() -> State:
    return State()


def classifier(s: State) -> str:
    lg, ag, rg = len(s.ledger), len(s.anchor), len(s.receipt)
    if s.ledger == s.anchor == s.receipt:
        return RECONCILED
    if (
        lg == rg + 1
        and ag == rg
        and s.anchor == s.receipt
        and s.ledger[:rg] == s.receipt
    ):
        return LEDGER_AHEAD_EXACT
    if (
        lg == rg + 1
        and ag == lg
        and s.anchor == s.ledger
        and s.receipt == s.ledger[:rg]
    ):
        return ANCHOR_REPLACED_RECEIPT_PENDING
    return FAIL_CLOSED


def authority_allowed(s: State) -> bool:
    if classifier(s) != RECONCILED:
        return False
    seen: dict[str, str] = {}
    for rid, target in s.ledger:
        prior = seen.setdefault(rid, target)
        if prior != target:
            return False
    return True


def _hist_add(history: tuple[Ledger, ...], value: Ledger) -> tuple[Ledger, ...]:
    return tuple(sorted(set(history + (value,))))


def _workers_dict(s: State) -> dict[str, tuple[str, Ledger]]:
    return {wid: (stage, target) for wid, stage, target in s.workers}


def _set_worker(s: State, wid: str, stage: str | None, target: Ledger = ()) -> State:
    d = _workers_dict(s)
    if stage is None:
        d.pop(wid, None)
    else:
        d[wid] = (stage, target)
    workers = tuple(sorted((w, st, tg) for w, (st, tg) in d.items()))
    return replace(s, workers=workers)


def _active_worker(s: State) -> str | None:
    for wid, stage, _ in s.workers:
        if stage != "WAITING":
            return wid
    return None


def _binding_for(s: State, rid: str) -> Binding | None:
    for binding in s.ledger:
        if binding[0] == rid:
            return binding
    return None


def _durable_authority_tuple(s: State) -> tuple:
    return (s.ledger, s.anchor, s.receipt, s.accepted_generation)


def _conflicting_anchor(anchor: Ledger) -> Ledger | None:
    if not anchor:
        return None
    rid, target = anchor[-1]
    alternate = TARGETS[1] if target == TARGETS[0] else TARGETS[0]
    candidate = anchor[:-1] + ((rid, alternate),)
    return candidate if candidate != anchor else None


def successors(s: State, *, include_faults: bool = True) -> list[Edge]:
    out: list[Edge] = []
    cls = classifier(s)

    # Issue/replay/rebind surface. New issuance begins only from reconciled state.
    if s.issue is None and cls == RECONCILED:
        for rid in RECOVERY_IDS:
            existing = _binding_for(s, rid)
            for target in TARGETS:
                if existing is None and len(s.ledger) < MAX_GENERATION:
                    out.append(Edge(f"ISSUE_BEGIN({rid},{target})", replace(s, issue=(rid, target, "BEGIN"), response_outcome="NONE")))
                elif existing is not None and existing[1] == target:
                    out.append(Edge(f"DUPLICATE_REPLAY({rid},{target})", replace(s, response_pending=existing, response_outcome="NONE")))
                elif existing is not None:
                    # Rebind is an explicit rejected operation: durable state must not change.
                    out.append(Edge(f"REBIND_ATTEMPT({rid},{target})", s))

    if s.issue is not None:
        rid, target, stage = s.issue
        if stage == "BEGIN":
            out.append(Edge("ISSUE_INSERT_UNCOMMITTED", replace(s, issue=(rid, target, "INSERTED"))))
        elif stage == "INSERTED" and _binding_for(s, rid) is None and len(s.ledger) < MAX_GENERATION:
            new_ledger = s.ledger + ((rid, target),)
            out.append(Edge(
                "ISSUE_LEDGER_COMMIT",
                replace(
                    s,
                    ledger=new_ledger,
                    known_ledgers=_hist_add(s.known_ledgers, new_ledger),
                    issue=None,
                ),
            ))

    # Reconciliation is serialized by the ledger transaction. A second worker is
    # represented as waiting and cannot choose or mutate the reconciliation target.
    if cls in (LEDGER_AHEAD_EXACT, ANCHOR_REPLACED_RECEIPT_PENDING):
        active = _active_worker(s)
        for wid in WORKERS:
            if wid in _workers_dict(s):
                continue
            if active is None:
                out.append(Edge(f"RECONCILE_BEGIN({wid})", _set_worker(s, wid, "BEGUN", s.ledger)))
            else:
                out.append(Edge(f"RECONCILE_BEGIN({wid})", _set_worker(s, wid, "WAITING", ())))

    # Wake one serialized waiter after the active worker leaves.
    if _active_worker(s) is None:
        for wid, stage, _ in s.workers:
            if stage == "WAITING":
                if cls in (LEDGER_AHEAD_EXACT, ANCHOR_REPLACED_RECEIPT_PENDING):
                    out.append(Edge(f"RECONCILER_WAKE({wid})", _set_worker(s, wid, "BEGUN", s.ledger)))
                else:
                    out.append(Edge(f"RECONCILER_RELEASE({wid})", _set_worker(s, wid, None)))

    for wid, stage, target in s.workers:
        if stage == "WAITING":
            continue
        if stage == "BEGUN":
            # A ledger-ahead reconciliation must write the exact committed next state.
            # Post-replace receipt completion skips temp/replace.
            if len(target) == len(s.receipt) + 1 and target[: len(s.receipt)] == s.receipt:
                if s.anchor == s.receipt:
                    out.append(Edge(
                        f"ANCHOR_TEMP_WRITE({wid})",
                        _set_worker(replace(s, temp_anchor=target), wid, "TEMP", target),
                    ))
                elif s.anchor == target:
                    ns = replace(s, receipt=target, known_anchors=_hist_add(s.known_anchors, s.anchor))
                    ns = _set_worker(ns, wid, None)
                    last = target[-1] if target else None
                    out.append(Edge(f"RECEIPT_PERSIST({wid})", replace(ns, response_pending=last, response_outcome="NONE")))
        elif stage == "TEMP":
            # Atomic replacement changes only current anchor; temp material ceases to
            # be a separate file after os.replace.
            ns = replace(
                s,
                anchor=target,
                known_anchors=_hist_add(_hist_add(s.known_anchors, s.anchor), target),
                temp_anchor=None,
            )
            out.append(Edge(f"ANCHOR_ATOMIC_REPLACE({wid})", _set_worker(ns, wid, "REPLACED", target)))
        elif stage == "REPLACED":
            # Persist the exact deterministic target. If an external fault changed
            # anchor/ledger between replace and receipt, the classifier will remain
            # fail-closed rather than laundering the mismatch into authority.
            ns = replace(s, receipt=target)
            ns = _set_worker(ns, wid, None)
            last = target[-1] if target else None
            out.append(Edge(f"RECEIPT_PERSIST({wid})", replace(ns, response_pending=last, response_outcome="NONE")))

    if s.response_pending is not None:
        out.append(Edge("RESPONSE_DELIVER", replace(s, response_pending=None, response_outcome="DELIVERED")))
        out.append(Edge("RESPONSE_LOSS", replace(s, response_pending=None, response_outcome="LOST")))

    # Consequential use is explicit so monotonic/at-most-once properties are tested,
    # rather than made true merely by the classifier definition.
    if authority_allowed(s) and len(s.ledger) > s.accepted_generation:
        out.append(Edge("AUTHORITATIVE_USE", replace(s, accepted_generation=len(s.ledger))))

    if include_faults:
        if s.crashes < MAX_CRASHES and (s.issue is not None or s.workers or s.response_pending is not None or s.temp_anchor is not None or cls != RECONCILED):
            out.append(Edge(
                "CRASH_RESTART",
                replace(
                    s,
                    issue=None,
                    workers=(),
                    response_pending=None,
                    response_outcome="LOST" if s.response_pending is not None else s.response_outcome,
                    crashes=s.crashes + 1,
                ),
                True,
            ))

        if s.stale_ledger_faults < MAX_STALE_LEDGER:
            for snap in s.known_ledgers:
                if len(snap) < len(s.ledger):
                    out.append(Edge(
                        f"STALE_LEDGER_SUBSTITUTE(g{len(snap)})",
                        replace(
                            s,
                            ledger=snap,
                            known_ledgers=_hist_add(s.known_ledgers, s.ledger),
                            issue=None,
                            workers=(),
                            stale_ledger_faults=s.stale_ledger_faults + 1,
                        ),
                        True,
                    ))

        if s.stale_anchor_faults < MAX_STALE_ANCHOR:
            for snap in s.known_anchors:
                if len(snap) < len(s.anchor):
                    out.append(Edge(
                        f"STALE_ANCHOR_SUBSTITUTE(g{len(snap)})",
                        replace(
                            s,
                            anchor=snap,
                            known_anchors=_hist_add(s.known_anchors, s.anchor),
                            workers=(),
                            stale_anchor_faults=s.stale_anchor_faults + 1,
                        ),
                        True,
                    ))

        if s.conflict_anchor_faults < MAX_CONFLICT_ANCHOR:
            conflict = _conflicting_anchor(s.anchor)
            if conflict is not None:
                out.append(Edge(
                    f"CONFLICTING_SAME_GENERATION_ANCHOR(g{len(conflict)})",
                    replace(
                        s,
                        anchor=conflict,
                        workers=(),
                        conflict_anchor_faults=s.conflict_anchor_faults + 1,
                    ),
                    True,
                ))

    # Deterministic transition order is part of counterexample reproducibility.
    return sorted(out, key=lambda e: (e.label, repr(e.state)))


def _check_state(s: State) -> list[tuple[str, str]]:
    failures: list[tuple[str, str]] = []
    cls = classifier(s)
    auth = authority_allowed(s)

    if cls != RECONCILED and auth:
        failures.append(("I1_NO_AUTHORITY_FROM_AMBIGUITY", f"authority true in {cls}"))
    if len(s.ledger) > len(s.anchor) and auth:
        failures.append(("I2_NO_LEDGER_ONLY_AUTHORITY", "ledger-ahead state authorized"))
    if len(s.anchor) > len(s.ledger) and auth:
        failures.append(("I3_NO_ANCHOR_ONLY_AUTHORITY", "anchor-ahead state authorized"))
    if auth and len(s.ledger) < s.accepted_generation:
        failures.append(("I4_MONOTONIC_TRUST", "authoritative state is below retained accepted generation"))

    seen: dict[str, str] = {}
    for rid, target in s.ledger:
        if rid in seen and seen[rid] != target:
            failures.append(("I5_NO_SEMANTIC_REBINDING", f"{rid} maps to {seen[rid]} and {target}"))
        elif rid in seen:
            failures.append(("I6_AT_MOST_ONCE_ADVANCEMENT", f"duplicate committed identity {rid}"))
        seen[rid] = target

    if s.temp_anchor is not None and s.temp_anchor != s.anchor and auth and not (s.ledger == s.anchor == s.receipt):
        failures.append(("S2_TEMP_NOT_AUTHORITY", "temporary anchor affected authority"))

    # The two exact repairable classes are structurally unique by definition.
    if cls == LEDGER_AHEAD_EXACT:
        if not (len(s.ledger) == len(s.receipt) + 1 and s.anchor == s.receipt and s.ledger[:-1] == s.receipt):
            failures.append(("I7_DETERMINISTIC_RECONCILIATION", "ledger-ahead classification not uniquely derivable"))
    if cls == ANCHOR_REPLACED_RECEIPT_PENDING:
        if not (s.anchor == s.ledger and s.receipt == s.ledger[:-1]):
            failures.append(("I7_DETERMINISTIC_RECONCILIATION", "post-replace classification not uniquely derivable"))
    if cls == FAIL_CLOSED and auth:
        failures.append(("I8_FAIL_CLOSED_CONFLICT", "fail-closed state authorized"))

    # Worker targets are protocol-derived, never caller-selected. Waiting workers have
    # no target at all.
    for _, stage, target in s.workers:
        if stage == "WAITING" and target:
            failures.append(("I10_EXTERNAL_AUTHORITY", "waiting worker carries caller-selectable target"))
        if stage in ("BEGUN", "TEMP", "REPLACED") and len(target) > MAX_GENERATION:
            failures.append(("I10_EXTERNAL_AUTHORITY", "worker target outside frozen protocol domain"))

    return failures


def _check_edge(before: State, edge: Edge) -> list[tuple[str, str]]:
    after = edge.state
    failures: list[tuple[str, str]] = []

    if after.accepted_generation < before.accepted_generation:
        failures.append(("I4_MONOTONIC_TRUST", "accepted generation decreased"))
    if after.accepted_generation > before.accepted_generation:
        if edge.label != "AUTHORITATIVE_USE" or not authority_allowed(before):
            failures.append(("I1_NO_AUTHORITY_FROM_AMBIGUITY", "consequential advancement without prior reconciled authority"))
        if after.accepted_generation != len(before.ledger):
            failures.append(("I6_AT_MOST_ONCE_ADVANCEMENT", "consequential advancement did not bind exact current generation"))

    if edge.label == "CRASH_RESTART":
        if before.issue is not None and before.issue[2] == "INSERTED" and after.ledger != before.ledger:
            failures.append(("S1_UNCOMMITTED_CRASH_ATOMICITY", "crash committed uncommitted issue work"))
        if (after.ledger, after.anchor, after.receipt, after.accepted_generation) != _durable_authority_tuple(before):
            failures.append(("S1_UNCOMMITTED_CRASH_ATOMICITY", "crash mutated committed authority state"))

    if edge.label in ("RESPONSE_DELIVER", "RESPONSE_LOSS"):
        if _durable_authority_tuple(after) != _durable_authority_tuple(before):
            failures.append(("S3_RESPONSE_INDEPENDENCE", "response outcome changed durable authority"))

    if edge.label.startswith("REBIND_ATTEMPT") and _durable_authority_tuple(after) != _durable_authority_tuple(before):
        failures.append(("I5_NO_SEMANTIC_REBINDING", "rebind attempt changed durable binding"))

    if edge.label.startswith("DUPLICATE_REPLAY") and after.ledger != before.ledger:
        failures.append(("I6_AT_MOST_ONCE_ADVANCEMENT", "replay appended a second ledger row"))

    if edge.label.startswith("RECEIPT_PERSIST"):
        # Reconciliation target can only be one exact generation above the receipt
        # that authorized the worker's repair transaction.
        active_targets = [target for _, stage, target in before.workers if stage in ("BEGUN", "REPLACED")]
        if active_targets:
            target = active_targets[0]
            if len(target) > len(before.receipt) + 1:
                failures.append(("S4_SINGLE_GENERATION_RECONCILIATION", "receipt jumped more than one generation"))

    return failures


def _trace(predecessor: dict[State, tuple[State, str] | None], end: State) -> list[str]:
    labels: list[str] = []
    cur = end
    while predecessor[cur] is not None:
        prior, label = predecessor[cur]  # type: ignore[misc]
        labels.append(label)
        cur = prior
    labels.reverse()
    return labels


def _counterexample_payload(v: Violation, predecessor: dict[State, tuple[State, str] | None]) -> dict:
    return {
        "invariant": v.invariant,
        "detail": v.detail,
        "trace": _trace(predecessor, v.before) + [v.transition],
        "before": asdict(v.before),
        "transition": v.transition,
        "after": asdict(v.after),
        "classifier_after": classifier(v.after),
        "authority_after": authority_allowed(v.after),
        "bounds": {
            "max_generation": MAX_GENERATION,
            "max_depth": MAX_DEPTH,
            "max_crashes": MAX_CRASHES,
            "max_stale_ledger": MAX_STALE_LEDGER,
            "max_stale_anchor": MAX_STALE_ANCHOR,
            "max_conflict_anchor": MAX_CONFLICT_ANCHOR,
            "recovery_ids": RECOVERY_IDS,
            "targets": TARGETS,
            "workers": WORKERS,
        },
    }


def _liveness_key(s: State) -> tuple:
    return (s.ledger, s.anchor, s.receipt, s.issue, s.workers, s.temp_anchor, s.response_pending, s.accepted_generation)


def _has_clean_next_generation_liveness(start: State) -> bool:
    current_generation = len(start.ledger)
    if current_generation >= MAX_GENERATION:
        return True
    target_generation = current_generation + 1
    q: deque[tuple[State, int]] = deque([(start, 0)])
    seen = {_liveness_key(start)}
    while q:
        s, depth = q.popleft()
        if len(s.ledger) == target_generation and classifier(s) == RECONCILED:
            return True
        if depth >= MAX_DEPTH:
            continue
        for edge in successors(s, include_faults=False):
            # Rebind/replay/response handling cannot be required for forward liveness;
            # skipping rejected/self-loop noise keeps the witness search deterministic.
            if edge.label.startswith("REBIND_ATTEMPT") or edge.label.startswith("DUPLICATE_REPLAY"):
                continue
            key = _liveness_key(edge.state)
            if key not in seen:
                seen.add(key)
                q.append((edge.state, depth + 1))
    return False


def explore() -> AnalysisResult:
    start = genesis()
    q: deque[tuple[State, int]] = deque([(start, 0)])
    predecessor: dict[State, tuple[State, str] | None] = {start: None}
    depths: dict[State, int] = {start: 0}
    transitions = 0
    invariant_checks = 0
    max_depth_reached = 0

    start_failures = _check_state(start)
    invariant_checks += 1
    if start_failures:
        inv, detail = start_failures[0]
        v = Violation(inv, detail, start, "GENESIS", start)
        return AnalysisResult("COUNTEREXAMPLE_FOUND", 1, 0, 0, {classifier(start): 1}, invariant_checks, 0, _counterexample_payload(v, predecessor))

    while q:
        s, depth = q.popleft()
        max_depth_reached = max(max_depth_reached, depth)
        if depth >= MAX_DEPTH:
            continue
        for edge in successors(s):
            transitions += 1
            invariant_checks += 1
            edge_failures = _check_edge(s, edge)
            state_failures = _check_state(edge.state)
            if edge_failures or state_failures:
                inv, detail = (edge_failures + state_failures)[0]
                v = Violation(inv, detail, s, edge.label, edge.state)
                return AnalysisResult(
                    "COUNTEREXAMPLE_FOUND",
                    len(predecessor),
                    transitions,
                    max(max_depth_reached, depth + 1),
                    dict(Counter(classifier(x) for x in predecessor)),
                    invariant_checks,
                    0,
                    _counterexample_payload(v, predecessor),
                )
            if edge.state == s:
                continue
            nd = depth + 1
            old = depths.get(edge.state)
            if old is None or nd < old:
                if len(predecessor) >= MAX_STATES:
                    return AnalysisResult(
                        "HARNESS_FAILURE",
                        len(predecessor),
                        transitions,
                        max_depth_reached,
                        dict(Counter(classifier(x) for x in predecessor)),
                        invariant_checks,
                        0,
                        {"reason": "MAX_STATES_EXCEEDED", "max_states": MAX_STATES},
                    )
                predecessor[edge.state] = (s, edge.label)
                depths[edge.state] = nd
                q.append((edge.state, nd))

    classifications = dict(Counter(classifier(x) for x in predecessor))

    # Bounded existential recovery liveness on every distinct protocol state that
    # is uniquely recoverable and still has capacity for a clean next generation.
    liveness_cache: dict[tuple, bool] = {}
    liveness_checked = 0
    for s in sorted(predecessor, key=repr):
        if classifier(s) not in (RECONCILED, LEDGER_AHEAD_EXACT, ANCHOR_REPLACED_RECEIPT_PENDING):
            continue
        if len(s.ledger) >= MAX_GENERATION:
            continue
        key = _liveness_key(s)
        if key in liveness_cache:
            continue
        liveness_checked += 1
        ok = _has_clean_next_generation_liveness(s)
        liveness_cache[key] = ok
        if not ok:
            v = Violation(
                "I9_LIVENESS_FROM_SAFE_STATES",
                "no fault-free bounded continuation reaches the clean next reconciled generation",
                s,
                "LIVENESS_SEARCH",
                s,
            )
            return AnalysisResult(
                "COUNTEREXAMPLE_FOUND",
                len(predecessor),
                transitions,
                max_depth_reached,
                classifications,
                invariant_checks,
                liveness_checked,
                _counterexample_payload(v, predecessor),
            )

    return AnalysisResult(
        "BOUNDED_SYSTEMATIC_PASS",
        len(predecessor),
        transitions,
        max_depth_reached,
        classifications,
        invariant_checks,
        liveness_checked,
        None,
    )


if __name__ == "__main__":
    print(explore().to_json())
