import ast
import os
import sys

# Pydantic data models are their own Parameter Object; skip __init__ param count.
PYDANTIC_BASE = "BaseModel"

# ---------------------------------------------------------------------------
# UX-01 ratchet: (file, function) -> parameter count, for the functions that
# exceed the 4-parameter guideline TODAY.
#
# This is not an allowlist that silences the rule, and it is not "pending": the
# rule still applies to every new function. The linter fails in BOTH
# directions -- add a violation and it goes red, fix one and it also goes red
# until the number here is updated. So the count can only go down, and nobody
# can lower it silently.
#
# Why the guideline is not met yet: these are the domain's record-keeping
# entry points (a decision has criteria, weights, scores, a distribution, a
# winner, a rationale, a confidence...). Collapsing them into Parameter Objects
# is an API change across four modules and ~40 call sites, which is a redesign
# and not a fix -- it needs its own spec and its own review.
#
# What would change this decision: any of the three below.
#   1. A Parameter Object lands for one of these -- delete its entry here in
#      the same commit, and the linter enforces that you did.
#   2. The rule is raised to a number these functions meet without changing
#      their signatures.
#   3. UX-01 is dropped as a rule, which is a decision to make on its own
#      evidence rather than as a side effect of this table.
#
# SEC-01, UX-02, UX-03 and OBS-01 have no baseline: those are met in full.
# ---------------------------------------------------------------------------
UX01_BASELINE = {
    ("adaptive_router.py", "_compute_complexity"): 5,
    ("decision_commitment.py", "create"): 11,
    ("decision_gates.py", "apply"): 5,
    ("decision_journal.py", "log_decision"): 14,
    ("decision_journal.py", "log_outcome"): 5,
    ("outcome_tracker.py", "record"): 10,
    ("reasoning_trace.py", "record"): 10,
}


class DevAgentsVisitor(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.violations = []
        self._in_pydantic_model = False
        self.ux01_counts = {}

    def add_violation(self, line, rule, message):
        self.violations.append(f"{self.filename}:{line} - [{rule}] {message}")

    def visit_ClassDef(self, node):
        is_model = any(
            isinstance(base, ast.Name) and base.id == PYDANTIC_BASE
            for base in node.bases
        ) or any(
            isinstance(base, ast.Attribute) and base.attr == PYDANTIC_BASE
            for base in node.bases
        )
        prev = self._in_pydantic_model
        self._in_pydantic_model = is_model
        self.generic_visit(node)
        self._in_pydantic_model = prev

    def visit_FunctionDef(self, node):
        # Rule: Max 4 parameters (skip data-model __init__)
        is_model_init = self._in_pydantic_model and node.name == "__init__"
        num_args = len(node.args.args) + len(node.args.kwonlyargs)
        # Exclude 'self' and 'cls' from the count if it's a method
        if node.args.args and node.args.args[0].arg in ('self', 'cls'):
            num_args -= 1

        if not is_model_init and num_args > 4:
            self.ux01_counts[node.name] = num_args
            self.add_violation(node.lineno, "UX-01", f"Function '{node.name}' has {num_args} parameters (Max 4). Use Parameter Object.")

        # Rule: No get_/set_ prefixes
        if node.name.startswith("get_") or node.name.startswith("set_"):
            self.add_violation(node.lineno, "UX-02", f"Function '{node.name}' uses get_/set_ prefix. Use action verbs instead.")

        self.generic_visit(node)

    def visit_Call(self, node):
        # Rule: No print() in prod
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "print"
            and "tests/" not in self.filename
        ):
            self.add_violation(node.lineno, "OBS-01", "Found print() statement. Use structured logging (logger) instead.")
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        # Rule: No broad exceptions (except Exception or except:)
        if node.type is None:
            self.add_violation(node.lineno, "SEC-01", "Bare 'except:' found. Must catch specific exceptions.")
        elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
            # Allowed only if we log it, but as a strict linter, we warn
            self.add_violation(node.lineno, "SEC-01", "Broad 'except Exception:' found. Prefer specific exceptions.")
        self.generic_visit(node)


def check_file_header(filepath, content):
    """Check if file has a 3-line header docstring."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return ["Syntax Error"]

    violations = []
    docstring = ast.get_docstring(tree)
    if not docstring:
        violations.append(f"{filepath}:1 - [UX-03] Missing module-level docstring header.")
    else:
        lines = [line.strip() for line in docstring.split("\n") if line.strip()]
        if len(lines) < 3:
            violations.append(f"{filepath}:1 - [UX-03] Module docstring is too short ({len(lines)} lines). Requires a 3-line header (what it does, how to use it, what it DOES NOT do).")

    return violations


def lint_file(filepath):
    """Return (violations, ux01_counts) for one file."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    header_violations = check_file_header(filepath, content)

    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return [f"{filepath}:{e.lineno} - [SYNTAX] Syntax error: {e}"], {}

    visitor = DevAgentsVisitor(filepath)
    visitor.visit(tree)

    return header_violations + visitor.violations, visitor.ux01_counts


def check_ux01_ratchet(counts_by_file):
    """Compare the measured UX-01 set against the baseline, in both directions.

    Returns a list of human-readable problems. Empty means the ratchet held.
    """
    problems = []
    measured = {}
    for filepath, counts in counts_by_file.items():
        name = os.path.basename(filepath)
        for func, num_args in counts.items():
            key = (name, func)
            if key in measured:
                problems.append(
                    f"[UX-01] {key} appears in two files; key the baseline by a unique name"
                )
            measured[key] = num_args

    for key in sorted(set(measured) - set(UX01_BASELINE)):
        problems.append(
            f"[UX-01] {key[0]}::{key[1]} has {measured[key]} parameters and is NOT in "
            f"UX01_BASELINE -- this is a new violation, fix the signature"
        )

    for key in sorted(set(UX01_BASELINE) - set(measured)):
        problems.append(
            f"[UX-01] {key[0]}::{key[1]} is in UX01_BASELINE but no longer violates "
            f"(was {UX01_BASELINE[key]} parameters) -- it got fixed, delete the entry"
        )

    for key in sorted(set(UX01_BASELINE) & set(measured)):
        expected, actual = UX01_BASELINE[key], measured[key]
        if actual > expected:
            problems.append(
                f"[UX-01] {key[0]}::{key[1]} grew from {expected} to {actual} parameters -- "
                f"the ratchet only moves down"
            )
        elif actual < expected:
            problems.append(
                f"[UX-01] {key[0]}::{key[1]} dropped from {expected} to {actual} parameters "
                f"-- improvement, update UX01_BASELINE to {actual}"
            )
    return problems


def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "src"
    all_violations = []
    ux01_counts_by_file = {}

    print(f"Running @dev-agents Native Linter on '{target_dir}'...")

    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                violations, ux01_counts = lint_file(filepath)
                all_violations.extend(violations)
                ux01_counts_by_file[filepath] = ux01_counts

    ratchet_problems = check_ux01_ratchet(ux01_counts_by_file)

    # The baselined UX-01 items are reported by the ratchet, which knows whether
    # each one is allowed and whether the number moved. Printing them as plain
    # violations again would say nothing that the ratchet does not say better.
    shown = [v for v in all_violations if "[UX-01]" not in v] + ratchet_problems

    if shown:
        print(f"\\n❌ Found {len(shown)} @dev-agents violations:\\n")
        for v in shown:
            print(v)
        sys.exit(1)
    else:
        print("\\n✅ Perfect! Codebase complies with @dev-agents guidelines.")
        sys.exit(0)

if __name__ == "__main__":
    main()
