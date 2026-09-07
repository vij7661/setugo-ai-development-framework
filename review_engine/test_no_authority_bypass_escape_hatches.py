from __future__ import annotations

import ast
import unittest
from pathlib import Path


FORBIDDEN_PRODUCTION_ESCAPE_HATCH_IDENTIFIERS = (
    "allow_governance_bypass",
    "governance_bypass_enabled",
    "skip_governance_validation",
    "disable_governance_checks",
    "allow_legacy_bypass",
    "ignore_governance_failure",
)
SUSPICIOUS_CONTROL_WORDS = frozenset({"bypass", "skip", "disable", "ignore", "override"})
AUTHORITY_WORDS = frozenset({
    "governance",
    "authority",
    "review",
    "validation",
    "qualification",
    "evidence",
    "promotion",
})


def _tokens(name: str) -> set[str]:
    normalized = name.lower().replace("-", "_")
    return {token for token in normalized.split("_") if token}


def _suspicious_control_name(name: str) -> bool:
    tokens = _tokens(name)
    return bool(tokens & SUSPICIOUS_CONTROL_WORDS and tokens & AUTHORITY_WORDS)


def _bool_control_names(tree: ast.AST) -> set[str]:
    """Find suspicious boolean switches, not ordinary guard/helper names."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            positional = list(node.args.args)
            defaults = [None] * (len(positional) - len(node.args.defaults)) + list(node.args.defaults)
            for arg, default in zip(positional, defaults):
                if isinstance(default, ast.Constant) and isinstance(default.value, bool) and _suspicious_control_name(arg.arg):
                    names.add(arg.arg)
            for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
                if isinstance(default, ast.Constant) and isinstance(default.value, bool) and _suspicious_control_name(arg.arg):
                    names.add(arg.arg)
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, bool):
            for target in node.targets:
                if isinstance(target, ast.Name) and _suspicious_control_name(target.id):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, bool) and _suspicious_control_name(node.target.id):
                names.add(node.target.id)
    return names


def _broad_exception_swallow_lines(tree: ast.AST) -> list[int]:
    """Detect obvious `except Exception/BaseException/bare: pass|continue` swallowing.

    This deliberately does not reject every broad exception handler. It targets
    the accidental fail-open shape where a broad exception is silently discarded.
    Semantic review and invariant tests remain the primary authority controls.
    """
    lines: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        broad = node.type is None or (
            isinstance(node.type, ast.Name) and node.type.id in {"Exception", "BaseException"}
        )
        if not broad:
            continue
        if any(isinstance(child, (ast.Pass, ast.Continue)) for statement in node.body for child in ast.walk(statement)):
            lines.append(node.lineno)
    return lines


class NoAuthorityBypassEscapeHatchTests(unittest.TestCase):
    def test_production_modules_do_not_define_explicit_or_obvious_semantic_escape_hatches(self):
        """Prevent common debug/test/legacy authority exceptions from shipping.

        The scan is recursive and AST-assisted, but remains defense in depth—not
        a proof against malicious or novel backdoors. The primary protection is
        still invariant discovery, preserved red evidence, frozen regressions,
        full-suite execution, and independent review.
        """
        root = Path(__file__).resolve().parent
        violations: list[str] = []
        for path in sorted(root.rglob("*.py")):
            if path.name.startswith("test_") or "__pycache__" in path.parts:
                continue
            relative = path.relative_to(root).as_posix()
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            for identifier in FORBIDDEN_PRODUCTION_ESCAPE_HATCH_IDENTIFIERS:
                if identifier in lowered:
                    violations.append(f"{relative}:literal:{identifier}")

            tree = ast.parse(text, filename=str(path))
            for name in sorted(_bool_control_names(tree)):
                violations.append(f"{relative}:boolean-control:{name}")
            for line in _broad_exception_swallow_lines(tree):
                violations.append(f"{relative}:broad-exception-swallow:line-{line}")

        self.assertEqual(violations, [], f"production governance bypass escape hatch detected: {violations}")


if __name__ == "__main__":
    unittest.main()
