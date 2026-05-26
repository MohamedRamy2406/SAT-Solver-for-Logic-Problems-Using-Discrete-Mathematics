"""
SAT solver engine — brute force only.

Generates every truth assignment, evaluates the formula, and reports
the first satisfying assignment (and all of them, up to a cap).
No CNF, no DPLL, no optimizations.
"""

import time
from itertools import product
from .parser import parse, collect_variables, evaluate, ast_to_string


# ---------- Truth table ----------

def truth_table(formula: str):
    ast = parse(formula)
    vars_ = collect_variables(ast)
    rows = []
    for combo in product([False, True], repeat=len(vars_)):
        env = dict(zip(vars_, combo))
        rows.append({"assignment": env, "result": evaluate(ast, env)})
    return {
        "variables": vars_,
        "rows": rows,
        "normalized": ast_to_string(ast),
    }


# ---------- Brute force solve ----------

def brute_force_solve(formula: str, trace_limit: int = 256):
    ast = parse(formula)
    vars_ = collect_variables(ast)
    start = time.perf_counter()

    trace = []
    satisfying = []
    checked = 0
    first_model = None

    for combo in product([False, True], repeat=len(vars_)):
        env = dict(zip(vars_, combo))
        result = evaluate(ast, env)
        checked += 1
        if len(trace) < trace_limit:
            trace.append({"assignment": env, "result": result})
        if result:
            if first_model is None:
                first_model = env
            satisfying.append(env)

    elapsed = (time.perf_counter() - start) * 1000
    return {
        "method": "brute-force",
        "variables": vars_,
        "satisfiable": first_model is not None,
        "model": first_model,
        "models_count": len(satisfying),
        "satisfying": satisfying[:64],
        "combinations_total": 2 ** len(vars_),
        "combinations_checked": checked,
        "trace": trace,
        "elapsed_ms": round(elapsed, 3),
        "normalized": ast_to_string(ast),
    }
