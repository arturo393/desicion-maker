import ast
import os
import sys

class DevAgentsVisitor(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.violations = []

    def add_violation(self, line, rule, message):
        self.violations.append(f"{self.filename}:{line} - [{rule}] {message}")

    def visit_FunctionDef(self, node):
        # Rule: Max 4 parameters
        num_args = len(node.args.args) + len(node.args.kwonlyargs)
        # Exclude 'self' and 'cls' from the count if it's a method
        if node.args.args and node.args.args[0].arg in ('self', 'cls'):
            num_args -= 1
            
        if num_args > 4:
            self.add_violation(node.lineno, "UX-01", f"Function '{node.name}' has {num_args} parameters (Max 4). Use Parameter Object.")

        # Rule: No get_/set_ prefixes
        if node.name.startswith("get_") or node.name.startswith("set_"):
            self.add_violation(node.lineno, "UX-02", f"Function '{node.name}' uses get_/set_ prefix. Use action verbs instead.")

        self.generic_visit(node)

    def visit_Call(self, node):
        # Rule: No print() in prod
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            if "tests/" not in self.filename:
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
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    header_violations = check_file_header(filepath, content)
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return [f"{filepath}:{e.lineno} - [SYNTAX] Syntax error: {e}"]

    visitor = DevAgentsVisitor(filepath)
    visitor.visit(tree)
    
    return header_violations + visitor.violations


def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "src"
    all_violations = []
    
    print(f"Running @dev-agents Native Linter on '{target_dir}'...")
    
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                violations = lint_file(filepath)
                all_violations.extend(violations)

    if all_violations:
        print(f"\\n❌ Found {len(all_violations)} @dev-agents violations:\\n")
        for v in all_violations:
            print(v)
        sys.exit(1)
    else:
        print("\\n✅ Perfect! Codebase complies with @dev-agents guidelines.")
        sys.exit(0)

if __name__ == "__main__":
    main()
