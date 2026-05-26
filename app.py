"""
Flask entry point for the SAT Solver web app (brute-force only).

Run:
    pip install -r requirements.txt
    python app.py

Then open http://localhost:5000
"""

from flask import Flask, jsonify, request, render_template

from backend.solver import brute_force_solve, truth_table
from backend.parser import parse, collect_variables, evaluate
from backend.utils import variable_frequency, safe_error


app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static",
)


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/solve")
def api_solve():
    data = request.get_json(silent=True) or {}
    formula = (data.get("formula") or "").strip()
    if not formula:
        return jsonify({"error": "EmptyFormula", "message": "Formula is empty."}), 400
    try:
        return jsonify(brute_force_solve(formula))
    except Exception as e:
        return jsonify(safe_error(e)), 400


@app.post("/api/evaluate")
def api_evaluate():
    data = request.get_json(silent=True) or {}
    formula = (data.get("formula") or "").strip()
    env = data.get("assignment") or {}
    try:
        ast = parse(formula)
        vars_ = collect_variables(ast)
        full_env = {v: bool(env.get(v, False)) for v in vars_}
        return jsonify({
            "result": evaluate(ast, full_env),
            "assignment": full_env,
            "variables": vars_,
        })
    except Exception as e:
        return jsonify(safe_error(e)), 400


@app.post("/api/variables")
def api_variables():
    data = request.get_json(silent=True) or {}
    formula = (data.get("formula") or "").strip()
    try:
        return jsonify(variable_frequency(formula))
    except Exception as e:
        return jsonify(safe_error(e)), 400


@app.post("/api/truth-table")
def api_truth_table():
    data = request.get_json(silent=True) or {}
    formula = (data.get("formula") or "").strip()
    try:
        return jsonify(truth_table(formula))
    except Exception as e:
        return jsonify(safe_error(e)), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
