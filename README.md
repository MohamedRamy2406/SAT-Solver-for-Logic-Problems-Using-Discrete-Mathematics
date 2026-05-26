# SAT Solver — Brute Force

A complete SAT Solver web app for propositional logic. Built with **Flask** + vanilla **HTML/CSS/JS**. Uses a single brute-force SAT engine: it enumerates every truth assignment, evaluates the formula, and reports the first satisfying one.

## Features

- Modern glassmorphism UI with animated aurora background
- Formula input with operator palette (`∧ ∨ ¬ → ↔`) and ASCII shortcuts (`& | ! -> <->`)
- Brute-force SAT engine in Python
- Automatic truth table on every Solve
- CSV export of the truth table
- Built-in examples for the 8 classical rules of inference
- Local history of solved formulas

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open <http://localhost:5000>.

## Constraints

- NO CNF
- NO DPLL
- NO learning section
- Only brute-force SAT solving — single engine
