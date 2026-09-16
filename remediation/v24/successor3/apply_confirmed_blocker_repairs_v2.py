from __future__ import annotations

from pathlib import Path

import apply_confirmed_blocker_repairs as v1

TARGET_REL = "governance-runtime/test_v24_v6_decision_apply.py"
TARGET_OLD = '    rd=b.get("reevaluated_decision")\n    if isinstance(rd,dict):\n'
TARGET_NEW = '    if isinstance(rd,dict):\n'

_original_replace_once = v1.replace_once


def replace_once_disambiguated(rel: str, old: str, new: str) -> None:
    if rel == TARGET_REL and old == TARGET_OLD and new == TARGET_NEW:
        path = v1.ROOT / rel
        text = path.read_text(encoding="utf-8")
        exact_old = '    }\n' + old
        exact_new = '    }\n' + new
        count = text.count(exact_old)
        if count != 1:
            raise RuntimeError(
                f"DISAMBIGUATED_REPLACEMENT_COUNT:{rel}:{count}:expected=1"
            )
        path.write_text(text.replace(exact_old, exact_new, 1), encoding="utf-8")
        return
    _original_replace_once(rel, old, new)


def main() -> None:
    v1.replace_once = replace_once_disambiguated
    v1.verify_sources()
    v1.repair_prc()
    v1.repair_da1()
    v1.repair_ncp1()
    v1.strengthen_successor3_regressions()
    print("successor-3 exact-source transformation v2 complete")


if __name__ == "__main__":
    main()
