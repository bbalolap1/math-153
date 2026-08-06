# mypy: disable-error-code="assignment,return-value,arg-type,attr-defined"
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from fractions import Fraction

import sympy

from .models import PracticeProblem, WorkedSolution

FOUNDATION = "Foundation / Version 0.0"
CHAPTERS_12 = "Chapters 1–2"
CHAPTERS_34 = "Chapters 3–4"
CHAPTER_5 = "Chapter 5"
MIXED_TEST = "Mixed Test Review"
FINAL_REVIEW = "Final Exam Review"


@dataclass(frozen=True)
class FamilySpec:
    family_id: str
    title: str
    group: str
    chapter: str
    section: str
    skills: tuple[str, ...]


_SPECS = [
    # Foundation
    ("F0-REAL-NUMBERS", "Real-number classification", FOUNDATION, "0", "0.1", ("number sets",)),
    (
        "F0-SIGNED-OPERATIONS",
        "Signed-number operations",
        FOUNDATION,
        "0",
        "0.2",
        ("signed arithmetic",),
    ),
    ("F0-FRACTIONS", "Fractions", FOUNDATION, "0", "0.3", ("fraction arithmetic",)),
    (
        "F0-ORDER-OPERATIONS",
        "Order of operations",
        FOUNDATION,
        "0",
        "0.4",
        ("order of operations",),
    ),
    ("F0-EXPONENT-RULES", "Exponent rules", FOUNDATION, "0", "0.5", ("exponent laws",)),
    (
        "F0-ALGEBRA-VOCAB",
        "Algebra vocabulary and evaluation",
        FOUNDATION,
        "0",
        "0.6",
        ("algebra language", "substitution"),
    ),
    # Chapters 1–2
    (
        "CH12-EXPRESSIONS",
        "Algebraic expressions",
        CHAPTERS_12,
        "1",
        "1.1",
        ("distribution", "like terms"),
    ),
    ("CH12-LINEAR-EQUATIONS", "Linear equations", CHAPTERS_12, "1", "1.2", ("equation solving",)),
    ("CH12-FACTORING", "Factoring", CHAPTERS_12, "1", "1.3", ("factoring",)),
    (
        "CH12-RATIONAL-EXPRESSIONS",
        "Rational expressions",
        CHAPTERS_12,
        "1",
        "1.4",
        ("factoring", "restrictions"),
    ),
    (
        "CH12-RADICALS",
        "Radicals and rational exponents",
        CHAPTERS_12,
        "2",
        "2.1",
        ("radical rules",),
    ),
    (
        "CH12-RADICAL-EQUATIONS",
        "Radical equations",
        CHAPTERS_12,
        "2",
        "2.2",
        ("radicals", "extraneous checks"),
    ),
    ("CH12-QUADRATICS", "Quadratic equations", CHAPTERS_12, "2", "2.3", ("quadratic methods",)),
    ("CH12-COMPLEX", "Complex numbers", CHAPTERS_12, "2", "2.4", ("complex arithmetic",)),
    ("CH12-ABSOLUTE", "Absolute value", CHAPTERS_12, "2", "2.5", ("absolute value", "intervals")),
    (
        "CH12-INEQUALITIES",
        "Inequalities",
        CHAPTERS_12,
        "2",
        "2.6",
        ("inequality solving", "interval notation"),
    ),
    # Chapters 3–4
    (
        "CH34-COORDINATE",
        "Coordinate plane",
        CHAPTERS_34,
        "3",
        "3.1",
        ("coordinates", "distance/midpoint"),
    ),
    ("CH34-LINES", "Lines", CHAPTERS_34, "3", "3.2", ("slope", "line equations")),
    ("CH34-TABLES", "Tables and missing values", CHAPTERS_34, "3", "3.3", ("table patterns",)),
    ("CH34-CIRCLES", "Circles", CHAPTERS_34, "3", "3.4", ("circle equations", "completing square")),
    ("CH34-FUNCTIONS", "Functions", CHAPTERS_34, "4", "4.1", ("function notation", "domain/range")),
    (
        "CH34-COMPOSITION",
        "Function composition",
        CHAPTERS_34,
        "4",
        "4.2",
        ("composition order", "substitution"),
    ),
    ("CH34-INVERSES", "Inverse functions", CHAPTERS_34, "4", "4.3", ("inverse operations",)),
    (
        "CH34-DIFFERENCE-QUOTIENT",
        "Difference quotient",
        CHAPTERS_34,
        "4",
        "4.4",
        ("substitution", "factoring"),
    ),
    (
        "CH34-QUADRATIC-FUNCTIONS",
        "Quadratic functions and graphs",
        CHAPTERS_34,
        "4",
        "4.5",
        ("vertex", "intercepts"),
    ),
    (
        "CH34-POLYNOMIALS",
        "Polynomial functions",
        CHAPTERS_34,
        "4",
        "4.6",
        ("zeros", "end behavior", "division"),
    ),
    (
        "CH34-RATIONAL-FUNCTIONS",
        "Rational functions",
        CHAPTERS_34,
        "4",
        "4.7",
        ("asymptotes", "holes", "domain"),
    ),
    # Chapter 5
    (
        "CH5-EXP-FUNCTIONS",
        "Exponential functions",
        CHAPTER_5,
        "5",
        "5.1",
        ("exponential behavior",),
    ),
    ("CH5-EXP-MODELS", "Exponential models", CHAPTER_5, "5", "5.2", ("growth/decay translation",)),
    (
        "CH5-COMPOUND-INTEREST",
        "Compound interest",
        CHAPTER_5,
        "5",
        "5.3",
        ("interest formulas", "calculator entry"),
    ),
    (
        "CH5-NATURAL-EXP",
        "Natural exponential function",
        CHAPTER_5,
        "5",
        "5.3",
        ("natural exponential",),
    ),
    ("CH5-LOGARITHMS", "Logarithms", CHAPTER_5, "5", "5.4", ("log/exponential conversion",)),
    ("CH5-LOG-PROPERTIES", "Logarithm properties", CHAPTER_5, "5", "5.5", ("log properties",)),
    (
        "CH5-LOG-EQUATIONS-FULL",
        "Logarithmic equations",
        CHAPTER_5,
        "5",
        "5.6",
        ("log equations", "domain checks"),
    ),
    (
        "CH5-EXP-EQUATIONS-FULL",
        "Exponential equations",
        CHAPTER_5,
        "5",
        "5.6",
        ("exponential equations", "logarithms"),
    ),
]
FAMILY_SPECS = {row[0]: FamilySpec(*row) for row in _SPECS}


def _difficulty(variant: int) -> str:
    return ("direct", "standard", "professor", "mixed")[min(variant // 3, 3)]


def _solution(
    rule: str,
    setup: str,
    calculation: list[str],
    answer: str,
    check: str,
    inference: str = "Choose the operation indicated by the representation.",
    prerequisite: str = "Accurate arithmetic and algebra.",
    family_reason: str = "The required operation defines this problem family.",
) -> WorkedSolution:
    return WorkedSolution(
        rule=rule,
        setup=setup,
        calculation=calculation,
        final_answer=answer,
        check=check,
        inference=inference,
        prerequisite=prerequisite,
        family_reason=family_reason,
    )


def _build(
    spec: FamilySpec, seed: int, variant: int
) -> tuple[str, str, str, str, list[str], WorkedSolution]:
    """Return prompt, answer type, answer, known wrong answer, choices, and solution."""
    r = random.Random(seed)
    k = variant % 10
    fid = spec.family_id
    x = sympy.Symbol("x")
    if fid == "F0-REAL-NUMBERS":
        samples = [
            ("-7", "integer,rational,real"),
            ("0", "whole,integer,rational,real"),
            ("3/5", "rational,real"),
            ("sqrt(11)", "irrational,real"),
            ("0.272727...", "rational,real"),
            ("7", "natural,whole,integer,rational,real"),
            ("pi", "irrational,real"),
            ("sqrt(49)", "natural,whole,integer,rational,real"),
            ("-2.5", "rational,real"),
            ("sqrt(2)/2", "irrational,real"),
        ]
        value, answer = samples[k]
        choices = ["natural", "whole", "integer", "rational", "irrational", "real"]
        return (
            f"Select every real-number set that contains ${value}$.",
            "multi_select",
            answer,
            "real",
            choices,
            _solution(
                "Use the nesting natural ⊂ whole ⊂ integer ⊂ rational ⊂ real; irrational numbers are real but not rational.",
                f"Determine whether {value} is a terminating/repeating ratio or a non-rational constant/root.",
                [f"Classification: {answer}."],
                answer,
                "Each selected set contains the displayed value.",
            ),
        )
    if fid == "F0-SIGNED-OPERATIONS":
        a, b, c = r.randint(-12, -2), r.randint(2, 10), r.randint(-6, 6)
        expr = f"({a}) - ({b}) + ({c})"
        ans = a - b + c
        return (
            f"Evaluate: ${expr}$.",
            "integer",
            str(ans),
            str(-ans),
            [],
            _solution(
                "Subtracting a number means adding its opposite.",
                expr,
                [f"{a}-{b}+{c}={ans}"],
                str(ans),
                "Estimate the sign and magnitude.",
            ),
        )
    if fid == "F0-FRACTIONS":
        a, b, c, d = r.randint(1, 8), r.randint(2, 9), r.randint(1, 8), r.randint(2, 9)
        op = ["+", "-", "*", "/"][k % 4]
        result = {
            "+": Fraction(a, b) + Fraction(c, d),
            "-": Fraction(a, b) - Fraction(c, d),
            "*": Fraction(a, b) * Fraction(c, d),
            "/": Fraction(a, b) / Fraction(c, d),
        }[op]
        answer = (
            f"{result.numerator}/{result.denominator}"
            if result.denominator != 1
            else str(result.numerator)
        )
        return (
            f"Compute and simplify: $\\frac{{{a}}}{{{b}}} {op} \\frac{{{c}}}{{{d}}}$.",
            "fraction",
            answer,
            f"{a + c}/{b + d}",
            [],
            _solution(
                "Use common denominators for addition/subtraction; multiply by the reciprocal for division.",
                f"{a}/{b} {op} {c}/{d}",
                [f"Reduce the resulting fraction to {answer}."],
                answer,
                "Substitute decimal approximations to check.",
            ),
        )
    if fid == "F0-ORDER-OPERATIONS":
        a, b, c = r.randint(2, 6), r.randint(2, 5), r.randint(1, 8)
        ans = -(a**2) + b * (c + 2)
        prompt = f"Evaluate: $-{a}^2+{b}({c}+2)$."
        return (
            prompt,
            "integer",
            str(ans),
            str(a**2 + b * (c + 2)),
            [],
            _solution(
                "Parentheses, exponents, multiplication/division, then addition/subtraction.",
                prompt,
                [f"-{a}^2=-{a**2}", f"{b}({c}+2)={b * (c + 2)}", f"Total={ans}"],
                str(ans),
                "The negative is outside the exponent.",
            ),
        )
    if fid == "F0-EXPONENT-RULES":
        m, n = r.randint(2, 6), r.randint(1, 5)
        power = m + n if k % 3 == 0 else m * n if k % 3 == 1 else m - n
        if k % 3 == 0:
            prompt, rule = f"Simplify: $x^{m}x^{n}$.", "Product rule: add exponents."
        elif k % 3 == 1:
            prompt, rule = f"Simplify: $(x^{m})^{n}$.", "Power rule: multiply exponents."
        else:
            prompt, rule = (
                f"Simplify: $x^{m}/x^{n}$, with $x\\ne0$.",
                "Quotient rule: subtract exponents.",
            )
        answer = f"x^{power}" if power else "1"
        return (
            prompt,
            "expression",
            answer,
            f"x^{m * n if k % 3 == 0 else m + n}",
            [],
            _solution(
                rule,
                prompt,
                [answer],
                answer,
                "Exponent laws preserve numeric checks for nonzero x.",
            ),
        )
    if fid == "F0-ALGEBRA-VOCAB":
        a, b, n = r.randint(2, 7), r.randint(-6, 6), r.randint(-4, 5)
        ans = a * n + b
        return (
            f"For $E={a}x+{b}$, evaluate $E$ when $x={n}$.",
            "integer",
            str(ans),
            str(a + b + n),
            [],
            _solution(
                "Substitute the given value for the variable.",
                f"E={a}({n})+{b}",
                [f"E={ans}"],
                str(ans),
                "Re-evaluate multiplication before addition.",
            ),
        )
    if fid == "CH12-EXPRESSIONS":
        a, b, c = r.randint(2, 6), r.randint(-5, 5), r.randint(-5, 5)
        coeff = a + 2
        const = a * b + c
        answer = f"{coeff}*x+({const})"
        return (
            f"Simplify: ${a}(x+{b})+2x+{c}$.",
            "expression",
            answer,
            f"{a + 2}*x+{b + c}",
            [],
            _solution(
                "Distribute, then combine like terms.",
                f"{a}x+{a * b}+2x+{c}",
                [answer],
                answer,
                "Expand the simplified form to compare.",
            ),
        )
    if fid == "CH12-LINEAR-EQUATIONS":
        sol, a, b = r.randint(-6, 8), r.randint(2, 7), r.randint(-8, 8)
        c = a * sol + b
        if k == 8:
            return (
                f"Solve: ${a}(x+1)={a}x+{a}$.",
                "multiple_choice",
                "all real numbers",
                "no solution",
                ["all real numbers", "no solution", str(sol)],
                _solution(
                    "Identical equations are true for every real x.",
                    "Distribute both sides.",
                    [f"{a}x+{a}={a}x+{a}"],
                    "all real numbers",
                    "Both sides match identically.",
                ),
            )
        if k == 7:
            return (
                f"Solve: ${a}(x+1)={a}x+{a + 1}$.",
                "multiple_choice",
                "no solution",
                "all real numbers",
                ["all real numbers", "no solution", str(sol)],
                _solution(
                    "A false constant statement is a contradiction.",
                    "Distribute and subtract the variable terms.",
                    [f"{a}={a + 1}, which is false."],
                    "no solution",
                    "No x can repair a false constant equality.",
                ),
            )
        return (
            f"Solve: ${a}x+{b}={c}$.",
            "solution_set",
            str(sol),
            str(-sol),
            [],
            _solution(
                "Use inverse operations while preserving equality.",
                f"{a}x={c - b}",
                [f"x=({c - b})/{a}={sol}"],
                str(sol),
                f"{a}({sol})+{b}={c}.",
            ),
        )
    if fid == "CH12-FACTORING":
        p, q = r.randint(1, 7), r.randint(1, 7)
        expr = sympy.expand((x - p) * (x + q))
        answer = f"(x-{p})*(x+{q})"
        return (
            f"Factor completely: ${sympy.sstr(expr)}$.",
            "expression",
            answer,
            f"(x+{p})*(x-{q})",
            [],
            _solution(
                "Find factors whose product is the constant and sum is the linear coefficient.",
                sympy.sstr(expr),
                [answer],
                answer,
                "Expand the factors to recover the original polynomial.",
            ),
        )
    if fid == "CH12-RATIONAL-EXPRESSIONS":
        a = r.randint(2, 8)
        answer = f"x+{a}"
        if k % 2 == 0:
            return (
                f"State every excluded value of $\\frac{{x^2-{a * a}}}{{x-{a}}}$ before simplifying.",
                "solution_set",
                str(a),
                str(-a),
                [],
                _solution(
                    "Restrictions come from zeros of the original denominator.",
                    f"x-{a}=0",
                    [f"x={a} is excluded; the expression simplifies to x+{a} elsewhere."],
                    str(a),
                    f"Substitution of x={a} makes the original denominator zero.",
                ),
            )
        return (
            f"Simplify $\\frac{{x^2-{a * a}}}{{x-{a}}}$. State the original restriction in your paper work.",
            "expression",
            answer,
            f"x-{a}",
            [],
            _solution(
                "Factor first; cancel factors, never terms.",
                f"(x-{a})(x+{a})/(x-{a}), x\\ne {a}",
                [f"x+{a}, x\\ne {a}"],
                answer,
                f"The original denominator excludes x={a}.",
            ),
        )
    if fid == "CH12-RADICALS":
        a, b = r.randint(2, 8), r.choice([2, 3, 5, 6, 7])
        n = a * a * b
        answer = f"{a}*sqrt({b})"
        return (
            f"Simplify: $\\sqrt{{{n}}}$.",
            "radical",
            answer,
            f"sqrt({n})",
            [],
            _solution(
                "Extract the largest perfect-square factor.",
                f"sqrt({a * a}*{b})",
                [answer],
                answer,
                f"({answer})^2={n}.",
            ),
        )
    if fid == "CH12-RADICAL-EQUATIONS":
        sol = r.randint(1, 9)
        c = r.randint(1, 5)
        rhs = (
            int(math.sqrt(sol + c)) if int(math.sqrt(sol + c)) ** 2 == sol + c else r.randint(2, 5)
        )
        sol = rhs * rhs - c
        return (
            f"Solve and check: $\\sqrt{{x+{c}}}={rhs}$.",
            "solution_set",
            str(sol),
            str(-sol),
            [],
            _solution(
                "Isolate the radical, square both sides, and check the original.",
                f"x+{c}={rhs**2}",
                [f"x={sol}"],
                str(sol),
                f"sqrt({sol + c})={rhs}; valid.",
            ),
        )
    if fid == "CH12-QUADRATICS":
        p, q = r.randint(-6, -1), r.randint(1, 7)
        expr = sympy.expand((x - p) * (x - q))
        answer = f"{p},{q}"
        return (
            f"Solve exactly: ${sympy.sstr(expr)}=0$.",
            "solution_set",
            answer,
            f"{-p},{-q}",
            [],
            _solution(
                "Set the quadratic to zero and use factoring or the quadratic formula.",
                f"(x-({p}))(x-({q}))=0",
                [f"x={p} or x={q}"],
                answer,
                "Substitute both roots in the original polynomial.",
            ),
        )
    if fid == "CH12-COMPLEX":
        a, b, c, d = [r.randint(-6, 6) for _ in range(4)]
        real = a * c - b * d
        imag = a * d + b * c
        answer = f"{real}+({imag})*I"
        return (
            f"Multiply: $({a}+{b}i)({c}+{d}i)$.",
            "complex_number",
            answer,
            f"{a * c + b * d}+({imag})*I",
            [],
            _solution(
                "Distribute and replace i² with −1.",
                "ac+adi+bci+bd i^2",
                [f"{real}+{imag}i"],
                answer,
                "Multiply using complex-number arithmetic.",
            ),
        )
    if fid == "CH12-ABSOLUTE":
        center = r.randint(-5, 5)
        radius = r.randint(1, 7)
        answer = f"{center - radius},{center + radius}"
        return (
            f"Solve: $|x-({center})|={radius}$.",
            "solution_set",
            answer,
            str(center + radius),
            [],
            _solution(
                "For |A|=k>0, solve A=k and A=−k.",
                f"x-{center}={radius} or x-{center}=-{radius}",
                [f"x={center - radius},{center + radius}"],
                answer,
                "Both values are the required distance from the center.",
            ),
        )
    if fid == "CH12-INEQUALITIES":
        a = r.randint(-5, 5)
        b = a + r.randint(2, 8)
        answer = f"({a},{b}]"
        return (
            f"Write in interval notation: $x>{a}$ and $x\\le {b}$.",
            "interval",
            answer,
            f"[{a},{b})",
            [],
            _solution(
                "Open endpoints represent strict inequalities; closed endpoints include equality.",
                f"{a}<x<={b}",
                [answer],
                answer,
                "Check both endpoint symbols.",
            ),
        )
    if fid == "CH34-COORDINATE":
        x1, y1, x2, y2 = [r.randint(-6, 6) for _ in range(4)]
        mx = Fraction(x1 + x2, 2)
        my = Fraction(y1 + y2, 2)
        answer = f"({mx},{my})"
        return (
            f"Find the midpoint of $({x1},{y1})$ and $({x2},{y2})$.",
            "ordered_pair",
            answer,
            f"({x2 - x1},{y2 - y1})",
            [],
            _solution(
                "Average corresponding coordinates.",
                f"(({x1}+{x2})/2,({y1}+{y2})/2)",
                [answer],
                answer,
                "The midpoint is halfway in each coordinate.",
            ),
        )
    if fid == "CH34-LINES":
        m = r.choice([-3, -2, 1, 2, 3])
        x1, y1 = r.randint(-4, 4), r.randint(-5, 5)
        b = y1 - m * x1
        answer = f"y={m}*x+({b})"
        return (
            f"Write the line with slope ${m}$ through $({x1},{y1})$ in slope-intercept form.",
            "equation",
            answer,
            f"y={-m}*x+({b})",
            [],
            _solution(
                "Use point-slope form, then solve for y.",
                f"y-{y1}={m}(x-{x1})",
                [answer],
                answer,
                f"At x={x1}, y={y1}.",
            ),
        )
    if fid == "CH34-TABLES":
        m, b = r.randint(2, 5), r.randint(-4, 4)
        xs = [0, 1, 2, 3]
        missing = r.randrange(4)
        vals = [m * v + b for v in xs]
        answer = str(vals[missing])
        cells = [str(v) if i != missing else "?" for i, v in enumerate(vals)]
        prompt = (
            "A table follows the rule $y="
            + str(m)
            + "x+"
            + str(b)
            + "$. Find the missing value.\n\n| x | "
            + " | ".join(map(str, xs))
            + " |\n|---|---|---|---|---|\n| y | "
            + " | ".join(cells)
            + " |"
        )
        return (
            prompt,
            "table",
            answer,
            str(vals[(missing + 1) % 4]),
            [],
            _solution(
                "Inspect the rule connecting each x-column to y.",
                f"For x={xs[missing]}, y={m}({xs[missing]})+{b}.",
                [f"y={answer}"],
                answer,
                "The y-values have constant difference equal to the slope.",
                "Infer which column is missing before calculating.",
                "Substitution and linear patterns.",
                "The information is represented as a table with a missing entry.",
            ),
        )
    if fid == "CH34-CIRCLES":
        h, k, radius = r.randint(-5, 5), r.randint(-5, 5), r.randint(1, 7)
        answer = f"(x-({h}))^2+(y-({k}))^2={radius**2}"
        return (
            f"Write the circle with center $({h},{k})$ and radius ${radius}$.",
            "equation",
            answer,
            f"(x+({h}))^2+(y+({k}))^2={radius}",
            [],
            _solution(
                "Circle standard form is (x−h)²+(y−k)²=r².",
                f"h={h}, k={k}, r={radius}",
                [answer],
                answer,
                "The center signs reverse inside each squared binomial.",
            ),
        )
    if fid == "CH34-FUNCTIONS":
        a, b, n = r.randint(2, 6), r.randint(-5, 5), r.randint(-4, 5)
        ans = a * n + b
        return (
            f"If $f(x)={a}x+{b}$, find $f({n})$.",
            "integer",
            str(ans),
            str(a + b + n),
            [],
            _solution(
                "Function notation directs substitution into the input.",
                f"f({n})={a}({n})+{b}",
                [str(ans)],
                str(ans),
                "Evaluate multiplication before addition.",
            ),
        )
    if fid == "CH34-COMPOSITION":
        a, b, n = r.randint(2, 5), r.randint(-4, 4), r.randint(-3, 5)
        ans = a * n * n + b
        return (
            f"Let $f(x)={a}x+{b}$ and $g(x)=x^2$. Find $(f\\circ g)({n})$.",
            "integer",
            str(ans),
            str((a * n + b) ** 2),
            [],
            _solution(
                "Evaluate the inner function before the outer function.",
                f"g({n})={n * n}; f({n * n})={a}({n * n})+{b}",
                [str(ans)],
                str(ans),
                "Composition order is f(g(input)).",
            ),
        )
    if fid == "CH34-INVERSES":
        a, b = r.randint(2, 7), r.randint(-6, 6)
        answer = f"(x-({b}))/{a}"
        return (
            f"Find $f^{{-1}}(x)$ for $f(x)={a}x+{b}$.",
            "expression",
            answer,
            f"{a}*x+({b})",
            [],
            _solution(
                "Write y=f(x), swap x and y, then solve for y.",
                f"x={a}y+{b}",
                [f"y={answer}"],
                answer,
                "Composing the inverse with f simplifies to x.",
            ),
        )
    if fid == "CH34-DIFFERENCE-QUOTIENT":
        a, b, c = r.randint(1, 4), r.randint(-5, 5), r.randint(-4, 4)
        answer = f"{2 * a}*x+{a}*h+({b})"
        return (
            f"For $f(x)={a}x^2+{b}x+{c}$, simplify $[f(x+h)-f(x)]/h$.",
            "expression",
            answer,
            f"{2 * a}*x+({b})",
            [],
            _solution(
                "Substitute x+h, subtract f(x), factor h, and cancel.",
                "[f(x+h)-f(x)]/h",
                [answer],
                answer,
                "Expanding the numerator confirms every remaining term.",
            ),
        )
    if fid == "CH34-QUADRATIC-FUNCTIONS":
        h, k, a = r.randint(-5, 5), r.randint(-5, 5), r.choice([-2, -1, 1, 2])
        answer = f"({h},{k})"
        return (
            f"Find the vertex of $y={a}(x-({h}))^2+({k})$.",
            "ordered_pair",
            answer,
            f"({-h},{k})",
            [],
            _solution(
                "Vertex form y=a(x−h)²+k has vertex (h,k).",
                f"h={h}, k={k}",
                [answer],
                answer,
                "At x=h the squared term is zero.",
            ),
        )
    if fid == "CH34-POLYNOMIALS":
        roots = [r.randint(-4, -1), r.randint(1, 5)]
        answer = ",".join(map(str, roots))
        poly = sympy.expand((x - roots[0]) * (x - roots[1]))
        return (
            f"Find all real zeros of $p(x)={sympy.sstr(poly)}$.",
            "solution_set",
            answer,
            str(-roots[0]),
            [],
            _solution(
                "Factor and apply the zero-product property.",
                f"p(x)=(x-({roots[0]}))(x-({roots[1]}))",
                [answer],
                answer,
                "Substitute both zeros.",
            ),
        )
    if fid == "CH34-RATIONAL-FUNCTIONS":
        a, b = r.randint(1, 6), r.randint(7, 12)
        answer = f"{a},{b}"
        return (
            f"State the domain exclusions of $R(x)=\\frac{{x-{a}}}{{(x-{a})(x-{b})}}$.",
            "solution_set",
            answer,
            str(b),
            [],
            _solution(
                "Exclude every zero of the original denominator, including canceled factors.",
                f"(x-{a})(x-{b})=0",
                [f"x\\ne {a},{b}"],
                answer,
                "The canceled factor creates a hole, not a restored domain value.",
            ),
        )
    if fid == "CH5-EXP-FUNCTIONS":
        base, n = r.choice([2, 3, 4, 5]), r.randint(-2, 5)
        value = Fraction(base**n, 1) if n >= 0 else Fraction(1, base ** (-n))
        answer = (
            str(value.numerator)
            if value.denominator == 1
            else f"{value.numerator}/{value.denominator}"
        )
        return (
            f"Evaluate $f(x)={base}^x$ at $x={n}$.",
            "fraction",
            answer,
            str(base * n),
            [],
            _solution(
                "Substitute the exponent; negative exponents produce reciprocals.",
                f"f({n})={base}^{n}",
                [answer],
                answer,
                "Exponential outputs are positive.",
            ),
        )
    if fid == "CH5-EXP-MODELS":
        initial = r.randrange(100, 1000, 50)
        pct = r.choice([5, 8, 12, 20])
        years = r.randint(2, 6)
        factor = 1 + pct / 100
        ans = round(initial * factor**years, 2)
        return (
            f"A quantity starts at {initial} and grows {pct}% per year. Find its value after {years} years, rounded to the nearest hundredth.",
            "decimal",
            f"{ans:.2f}",
            f"{initial * (pct / 100) * years:.2f}",
            [],
            _solution(
                "Exponential growth uses A=P(1+r)^t.",
                f"A={initial}(1+{pct / 100})^{years}",
                [f"A≈{ans:.2f}"],
                f"{ans:.2f}",
                "The result exceeds the initial value.",
                "Translate percent change into a growth factor.",
                "Percent and exponent evaluation.",
                "The repeated percent change defines an exponential model.",
            ),
        )
    if fid == "CH5-COMPOUND-INTEREST":
        p = r.randrange(500, 3000, 100)
        rate = r.choice([0.03, 0.04, 0.05, 0.06])
        n = r.choice([1, 2, 4, 12])
        years = r.randint(2, 8)
        ans = round(p * (1 + rate / n) ** (n * years), 2)
        return (
            f"Deposit ${p} at {rate * 100:.0f}% annual interest compounded {n} times per year for {years} years. Find the amount to the nearest cent.",
            "decimal",
            f"{ans:.2f}",
            f"{p * (1 + rate * years):.2f}",
            [],
            _solution(
                "Use A=P(1+r/n)^(nt).",
                f"A={p}(1+{rate}/{n})^({n}·{years})",
                [f"A≈{ans:.2f}"],
                f"{ans:.2f}",
                "The amount exceeds principal; retain full calculator precision until rounding.",
            ),
        )
    if fid == "CH5-NATURAL-EXP":
        a = r.randint(1, 5)
        t = r.randint(1, 4)
        ans = round(a * math.exp(t), 3)
        return (
            f"Evaluate $f(t)={a}e^t$ at $t={t}$, rounded to three decimals.",
            "decimal",
            f"{ans:.3f}",
            f"{a * 2.718 * t:.3f}",
            [],
            _solution(
                "Substitute into the natural exponential function.",
                f"f({t})={a}e^{t}",
                [f"≈{ans:.3f}"],
                f"{ans:.3f}",
                "Keep e unrounded until the final step.",
            ),
        )
    if fid == "CH5-LOGARITHMS":
        base = r.choice([2, 3, 5])
        exp = r.randint(2, 5)
        value = base**exp
        return (
            f"Evaluate exactly: $\\log_{{{base}}}({value})$.",
            "integer",
            str(exp),
            str(value / base),
            [],
            _solution(
                "log_b(A)=c exactly when b^c=A.",
                f"{base}^{exp}={value}",
                [str(exp)],
                str(exp),
                "Convert back to exponential form.",
            ),
        )
    if fid == "CH5-LOG-PROPERTIES":
        a, b = r.randint(2, 8), r.randint(2, 8)
        answer = f"log({a * b}*x)"
        return (
            f"Condense to one logarithm: $\\log({a}x)+\\log({b})$.",
            "logarithmic_expression",
            answer,
            f"log(({a}+{b})*x)",
            [],
            _solution(
                "Product rule: log A + log B = log(AB).",
                f"log(({a}x)({b}))",
                [answer],
                answer,
                "Arguments multiply; they do not add.",
            ),
        )
    if fid == "CH5-LOG-EQUATIONS-FULL":
        sol, shift = r.randint(2, 10), r.randint(1, 5)
        value = sol + shift
        return (
            f"Solve and check the domain: $\\ln(x+{shift})=\\ln({value})$.",
            "solution_set",
            str(sol),
            str(-sol),
            [],
            _solution(
                "State x+shift>0, then use the one-to-one property.",
                f"x+{shift}={value}",
                [f"x={sol}"],
                str(sol),
                f"{sol}+{shift}={value}>0; valid.",
                "Infer that domain checking remains required after comparing arguments.",
                "Linear equations and positivity.",
                "The unknown occurs inside a logarithm.",
            ),
        )
    if fid == "CH5-EXP-EQUATIONS-FULL":
        base = r.choice([2, 3, 5])
        sol = r.randint(2, 6)
        value = base**sol
        return (
            f"Solve exactly: ${base}^x={value}$.",
            "solution_set",
            str(sol),
            str(value / base),
            [],
            _solution(
                "Rewrite with a common base and equate exponents.",
                f"{base}^x={base}^{sol}",
                [f"x={sol}"],
                str(sol),
                f"{base}^{sol}={value}.",
            ),
        )
    raise ValueError(f"No builder for {fid}")


def generate_practice_problem(
    family_id: str, seed: int, variant: int | None = None
) -> PracticeProblem:
    """Generate one of at least ten controlled variants for every selectable family."""
    if family_id not in FAMILY_SPECS:
        raise ValueError(f"Unknown family: {family_id}")
    spec = FAMILY_SPECS[family_id]
    variant = seed % 10 if variant is None else variant % 10
    prompt, answer_type, expected, _wrong, choices, solution = _build(spec, seed, variant)
    if answer_type == "multiple_choice":
        wrong = next(choice for choice in choices if choice != expected)
    elif answer_type == "multi_select":
        wrong = next(choice for choice in choices if choice not in expected.split(","))
    elif answer_type == "interval":
        wrong = "(999999,1000000)"
    elif answer_type == "ordered_pair":
        wrong = "(999999,999999)"
    elif answer_type == "equation":
        wrong = "y=999999*x+999999"
    elif answer_type == "solution_set":
        wrong = "999999"
    elif answer_type == "complex_number":
        wrong = "999999+999999i"
    else:
        wrong = "999999"
    difficulty = _difficulty(variant)
    return PracticeProblem(
        problem_id=f"{family_id}-{seed}-{variant}",
        group=spec.group,
        chapter=spec.chapter,
        section=spec.section,
        family_id=family_id,
        family_title=spec.title,
        difficulty=difficulty,
        prompt=prompt,
        answer_type=answer_type,
        expected_answer=expected,
        wrong_answer=wrong,
        choices=choices,
        source_type="model_inference",
        source_file="unavailable_course_binaries",
        source_question_or_page="not_available",
        construction_notes=(
            "Controlled exam-review template; not claimed as copied or professor-verified. "
            f"Variant {variant + 1}/10 changes parameters and difficulty layer."
        ),
        rule_or_formula=solution.rule,
        required_skills=list(spec.skills),
        worked_solution=solution,
        parameter_seed=seed,
    )


def family_variants(family_id: str) -> list[PracticeProblem]:
    """Return the fixed ten-variant audit set for a family."""
    return [generate_practice_problem(family_id, 15300 + index, index) for index in range(10)]


PRESET_SESSIONS: dict[str, tuple[int, list[str]]] = {
    "Foundation refresher": (20, [f for f, s in FAMILY_SPECS.items() if s.group == FOUNDATION]),
    "Chapters 1–2 refresher": (30, [f for f, s in FAMILY_SPECS.items() if s.group == CHAPTERS_12]),
    "Chapters 3–4 refresher": (30, [f for f, s in FAMILY_SPECS.items() if s.group == CHAPTERS_34]),
    "Chapter 5 refresher": (30, [f for f, s in FAMILY_SPECS.items() if s.group == CHAPTER_5]),
    "Test simulation": (
        30,
        [f for f, s in FAMILY_SPECS.items() if s.group in {CHAPTER_5, CHAPTERS_12}],
    ),
    "Final-exam simulation": (40, list(FAMILY_SPECS)),
}


def build_session(family_ids: list[str], count: int, seed: int = 153) -> list[PracticeProblem]:
    """Assemble a reproducible mixed or focused session with working problems."""
    if not family_ids or count < 1:
        raise ValueError("A session needs at least one family and one question.")
    unknown = set(family_ids) - FAMILY_SPECS.keys()
    if unknown:
        raise ValueError(f"Unknown families: {sorted(unknown)}")
    return [
        generate_practice_problem(family_ids[i % len(family_ids)], seed + i, i % 10)
        for i in range(count)
    ]
