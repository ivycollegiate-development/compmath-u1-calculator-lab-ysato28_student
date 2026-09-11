"""Self-check tests for the Calculator with Guardrails lab.

Run:  python3 test_calculator.py
Each PASS is a guardrail working. Aim for at least the first 3 today.
"""

import io
import sys
from contextlib import redirect_stdout, redirect_stderr

import calculator


def run_calc(inputs):
    """Run calculator.main() with scripted stdin, return captured output."""
    buf_in = io.StringIO("\n".join(inputs) + "\n")
    old_stdin = sys.stdin
    sys.stdin = buf_in = io.StringIO("\n".join(inputs) + "\n")
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            calculator.main()
    except SystemExit:
        pass
    finally:
        sys.stdin = old_stdin
    return out.getvalue()


results = []


def check(name, fn):
    try:
        ok = fn()
        results.append((name, bool(ok), ""))
    except Exception as e:
        results.append((name, False, f"{type(e).__name__}: {e}"))


# Test 1: invalid input asks again instead of crashing
def t1():
    out = run_calc(["4", "hello", "2", "2", "q"])
    return "divide by zero" in out.lower() or "Result" in out


# Test 2: division by zero is handled, program keeps running
def t2():
    out = run_calc(["4", "5", "0", "1", "2", "3", "q"])
    return "crash" not in out.lower() and out.count("Result") >= 1


# Test 3: after an error, the program still accepts a working calculation
def t3():
    out = run_calc(["4", "5", "0", "1", "2", "3", "q"])
    return "Result: 5.0" in out


# Test 4: quit works cleanly
def t4():
    out = run_calc(["q"])
    return "Goodbye" in out


check("1. bad input does not crash", t1)
check("2. divide by zero handled", t2)
check("3. works again after bad input", t3)
check("4. quit works", t4)

print()
print("=== Self-check results ===")
passed = 0
for name, ok, err in results:
    mark = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    print(f"[{mark}] {name}" + (f"  ({err})" if err else ""))
print(f"{passed}/{len(results)} passing")