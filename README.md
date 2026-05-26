# SAT Solver — Brute Force

A modern web-based SAT Solver built for Discrete Mathematics using Python Flask, HTML, CSS, and JavaScript.

The application analyzes propositional logic formulas using a brute-force satisfiability approach by testing all possible truth assignments for variables in a logical expression.

---

# Features

* Brute-force SAT solving engine
* Truth table generation
* SAT / UNSAT detection
* Tautology and contradiction detection
* Support for logical operators:

  * AND (∧ or &)
  * OR (∨ or |)
  * NOT (¬ or !)
  * Implication (→)
  * Biconditional (↔)
* Modern glassmorphism UI
* Animated futuristic interface
* Formula validation and syntax checking
* Dynamic result visualization
* Formula history using localStorage
* CSV export support
* Responsive design

---

# Technologies Used

## Frontend

* HTML
* CSS
* Vanilla JavaScript

## Backend

* Python
* Flask

---

# Project Structure

```bash
SAT-SOLVER/
│
├── app.py
├── requirements.txt
│
├── backend/
│   ├── __init__.py
│   ├── parser.py
│   ├── solver.py
│   └── utils.py
│
├── frontend/
│   ├── templates/
│   │   └── index.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       │
│       └── js/
│           └── scripts.js
│
└── docs/
    └── SAT_Solver_Project_Report.pdf
```

---

# How the SAT Solver Works

1. The user enters a propositional logic formula.
2. The parser validates and analyzes the formula.
3. Variables are extracted automatically.
4. The brute-force solver generates all possible truth assignments.
5. Each assignment is evaluated against the formula.
6. If a satisfying assignment exists, the system returns SAT.
7. If no assignment satisfies the formula, the system returns UNSAT.
8. A complete truth table is generated dynamically.

---

# Installation and Setup

## 1. Extract the Project Folder

Download and extract the SAT-SOLVER project folder.

---

## 2. Install Python Dependencies

Make sure Python 3 is installed on your machine.

Install required packages:

```bash
pip install -r requirements.txt
```

---

# Running the Project

## Start the Flask Server

Run the following command:

```bash
python app.py
```

---

## Open in Browser

After running the server, open:

```bash
http://localhost:5000
```

---

# Supported Operators

| Operator      | Symbol |
| ------------- | ------ |
| AND           | ∧ or & |
| OR            | ∨ or | |
| NOT           | ¬ or ! |
| Implication   | →      |
| Biconditional | ↔      |

---

# Example Formula

```text
(P ∨ Q) ∧ (¬P ∨ R)
```

---

# SAT Result Example

```text
SATISFIABLE

P = True
Q = False
R = True
```

---

# Unsat Example

```text
P ∧ ¬P
```

Result:

```text
UNSATISFIABLE
```

---

# Requirements

* Python 3.x
* Flask
* Modern web browser

---

# Notes

* This project uses a brute-force SAT solving approach.
* Every possible truth assignment is checked systematically.
* The application is designed for educational and academic purposes.

---

# Future Improvements

* Advanced SAT optimization algorithms
* Formula simplification
* Logic graph visualization
* More inference rule support
* Performance benchmarking

---

# Report Navigation

[📄 Read the Full SAT Solver Project Report (PDF)](./docs/SAT_Solver_Project_Report.pdf)

Open the report to view:

* Full project explanation
* Brute-force SAT method details
* Features and technologies
* System architecture
* Screenshots
* Output examples
* Project analysis
