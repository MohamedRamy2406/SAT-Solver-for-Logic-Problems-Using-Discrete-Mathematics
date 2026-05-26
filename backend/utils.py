"""Small helpers shared across the API."""

from .parser import parse, collect_variables, ParseError


def variable_frequency(formula: str):
    ast = parse(formula)
    freq = {}

    def walk(n):
        t = n[0]
        if t == "var":
            freq[n[1]] = freq.get(n[1], 0) + 1
        elif t == "not":
            walk(n[1])
        elif t in ("and", "or", "imp", "iff"):
            walk(n[1]); walk(n[2])

    walk(ast)
    return {
        "variables": collect_variables(ast),
        "frequency": freq,
    }


def safe_error(e: Exception):
    if isinstance(e, ParseError):
        return {"error": "ParseError", "message": str(e)}
    return {"error": e.__class__.__name__, "message": str(e)}
