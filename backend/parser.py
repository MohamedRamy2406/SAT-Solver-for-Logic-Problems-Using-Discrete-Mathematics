"""
Propositional logic parser.

Grammar (precedence low -> high):
    biconditional  ::=  implication ('<->' implication)*
    implication    ::=  or_expr ('->' or_expr)*        (right-assoc)
    or_expr        ::=  and_expr ('|' and_expr)*
    and_expr       ::=  not_expr ('&' not_expr)*
    not_expr       ::=  '!' not_expr | atom
    atom           ::=  VARIABLE | 'True' | 'False' | '(' biconditional ')'

Accepted symbols (normalized before tokenizing):
    AND : ∧ &  /\
    OR  : ∨ |  \/
    NOT : ¬ ! ~
    IMP : → -> =>
    IFF : ↔ <-> <=>
"""

import re


class ParseError(Exception):
    pass


# AST node types are simple tuples: ('var', name) | ('const', bool)
# ('not', a) | ('and', a, b) | ('or', a, b) | ('imp', a, b) | ('iff', a, b)


def normalize(formula: str) -> str:
    f = formula
    repl = [
        ("<->", "↔"), ("<=>", "↔"),
        ("->", "→"), ("=>", "→"),
        ("/\\", "∧"), ("\\/", "∨"),
        ("&&", "&"), ("||", "|"),
        ("~", "!"),
    ]
    for a, b in repl:
        f = f.replace(a, b)
    return f


TOKEN_RE = re.compile(r"\s*(?:(↔)|(→)|([∧&])|([∨|])|([¬!])|(\()|(\))|([A-Za-z_][A-Za-z0-9_]*))")


def tokenize(formula: str):
    f = normalize(formula)
    pos = 0
    tokens = []
    while pos < len(f):
        if f[pos].isspace():
            pos += 1
            continue
        m = TOKEN_RE.match(f, pos)
        if not m or m.start() != pos:
            raise ParseError(f"Unexpected character '{f[pos]}' at position {pos}")
        groups = m.groups()
        if groups[0]: tokens.append(("IFF", "↔"))
        elif groups[1]: tokens.append(("IMP", "→"))
        elif groups[2]: tokens.append(("AND", "∧"))
        elif groups[3]: tokens.append(("OR", "∨"))
        elif groups[4]: tokens.append(("NOT", "¬"))
        elif groups[5]: tokens.append(("LP", "("))
        elif groups[6]: tokens.append(("RP", ")"))
        elif groups[7]:
            name = groups[7]
            if name in ("True", "true", "T", "1"):
                tokens.append(("CONST", True))
            elif name in ("False", "false", "F", "0"):
                tokens.append(("CONST", False))
            else:
                tokens.append(("VAR", name))
        pos = m.end()
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else (None, None)

    def eat(self, kind=None):
        tok = self.peek()
        if tok[0] is None:
            raise ParseError("Unexpected end of formula")
        if kind and tok[0] != kind:
            raise ParseError(f"Expected {kind}, got {tok[0]} ('{tok[1]}')")
        self.i += 1
        return tok

    def parse(self):
        if not self.tokens:
            raise ParseError("Empty formula")
        node = self.parse_iff()
        if self.i != len(self.tokens):
            raise ParseError(f"Unexpected token '{self.tokens[self.i][1]}'")
        return node

    def parse_iff(self):
        left = self.parse_imp()
        while self.peek()[0] == "IFF":
            self.eat("IFF")
            right = self.parse_imp()
            left = ("iff", left, right)
        return left

    def parse_imp(self):
        left = self.parse_or()
        if self.peek()[0] == "IMP":
            self.eat("IMP")
            right = self.parse_imp()  # right-assoc
            return ("imp", left, right)
        return left

    def parse_or(self):
        left = self.parse_and()
        while self.peek()[0] == "OR":
            self.eat("OR")
            right = self.parse_and()
            left = ("or", left, right)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.peek()[0] == "AND":
            self.eat("AND")
            right = self.parse_not()
            left = ("and", left, right)
        return left

    def parse_not(self):
        if self.peek()[0] == "NOT":
            self.eat("NOT")
            return ("not", self.parse_not())
        return self.parse_atom()

    def parse_atom(self):
        tok = self.peek()
        if tok[0] == "LP":
            self.eat("LP")
            node = self.parse_iff()
            if self.peek()[0] != "RP":
                raise ParseError("Missing closing parenthesis ')'")
            self.eat("RP")
            return node
        if tok[0] == "VAR":
            self.eat("VAR")
            return ("var", tok[1])
        if tok[0] == "CONST":
            self.eat("CONST")
            return ("const", tok[1])
        raise ParseError(f"Unexpected token '{tok[1]}'")


def parse(formula: str):
    return Parser(tokenize(formula)).parse()


def collect_variables(ast):
    out = []
    seen = set()

    def walk(n):
        t = n[0]
        if t == "var":
            if n[1] not in seen:
                seen.add(n[1])
                out.append(n[1])
        elif t == "not":
            walk(n[1])
        elif t in ("and", "or", "imp", "iff"):
            walk(n[1]); walk(n[2])

    walk(ast)
    return out


def evaluate(ast, env: dict) -> bool:
    t = ast[0]
    if t == "const": return bool(ast[1])
    if t == "var": return bool(env[ast[1]])
    if t == "not": return not evaluate(ast[1], env)
    a = evaluate(ast[1], env)
    if t == "and": return a and evaluate(ast[2], env)
    if t == "or":  return a or  evaluate(ast[2], env)
    if t == "imp": return (not a) or evaluate(ast[2], env)
    if t == "iff": return a == evaluate(ast[2], env)
    raise ValueError(f"Unknown node {t}")


def ast_to_string(ast) -> str:
    t = ast[0]
    if t == "const": return "⊤" if ast[1] else "⊥"
    if t == "var": return ast[1]
    if t == "not": return f"¬{ast_to_string(ast[1])}"
    op = {"and": "∧", "or": "∨", "imp": "→", "iff": "↔"}[t]
    return f"({ast_to_string(ast[1])} {op} {ast_to_string(ast[2])})"
