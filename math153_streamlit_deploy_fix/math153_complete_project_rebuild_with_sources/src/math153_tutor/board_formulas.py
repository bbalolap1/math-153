from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoardFormula:
    """Professor-board reference rule for Math 153.

    These entries are reference knowledge, not generated assessment questions.
    The displayed LaTeX is kept close to the board transcription supplied by the student.
    """

    number: int | None
    topic: str
    name: str
    latex: str
    meaning: str
    conditions: tuple[str, ...] = ()


BOARD_FORMULAS: tuple[BoardFormula, ...] = (
    # Exponents and radicals — 1–10
    BoardFormula(1, "Exponents and Radicals", "Product rule for exponents", r"x^n x^m=x^{n+m}", "When multiplying like bases, add the exponents."),
    BoardFormula(2, "Exponents and Radicals", "Quotient rule for exponents", r"\frac{x^n}{x^m}=x^{n-m}", "When dividing like bases, subtract the exponents.", (r"x\ne0",)),
    BoardFormula(3, "Exponents and Radicals", "Power raised to a power", r"(x^n)^m=x^{nm}", "Multiply the exponents."),
    BoardFormula(4, "Exponents and Radicals", "Power of a product", r"(xy)^n=x^ny^n", "Distribute the exponent across a product."),
    BoardFormula(5, "Exponents and Radicals", "Power of a quotient", r"\left(\frac{x}{y}\right)^n=\frac{x^n}{y^n}", "Distribute the exponent to numerator and denominator.", (r"y\ne0",)),
    BoardFormula(6, "Exponents and Radicals", "Negative exponent", r"x^{-n}=\frac{1}{x^n}", "A negative exponent moves the factor across the fraction bar.", (r"x\ne0",)),
    BoardFormula(7, "Exponents and Radicals", "Root of a product", r"\sqrt[n]{xy}=\sqrt[n]{x}\sqrt[n]{y}", "Split a product under an nth root when the radicals are defined.", ("Radicals must be defined in the working number system.",)),
    BoardFormula(8, "Exponents and Radicals", "Root of a quotient", r"\sqrt[n]{\frac{x}{y}}=\frac{\sqrt[n]{x}}{\sqrt[n]{y}}", "Split a quotient under an nth root when defined.", (r"y\ne0", "Radicals must be defined in the working number system.")),
    BoardFormula(9, "Exponents and Radicals", "Radical to rational exponent", r"\sqrt[n]{x^m}=x^{m/n}", "Convert between radical and rational-exponent notation."),
    BoardFormula(10, "Exponents and Radicals", "Rationalizing an nth-root denominator", r"\frac{x}{\sqrt[n]{y^k}}\cdot\frac{\sqrt[n]{y^{n-k}}}{\sqrt[n]{y^{n-k}}}=\frac{x\sqrt[n]{y^{n-k}}}{y}", "Multiply by the missing radical power needed to make a complete nth power in the denominator.", (r"0<k<n",)),

    # Special factoring identities — 11–15
    BoardFormula(11, "Special Factoring Identities", "Perfect-square trinomial", r"a^2+2ab+b^2=(a+b)^2", "Recognize or expand a perfect-square binomial."),
    BoardFormula(12, "Special Factoring Identities", "Difference of squares", r"a^2-b^2=(a+b)(a-b)", "Factor a difference of two squares."),
    BoardFormula(13, "Special Factoring Identities", "Cube of a binomial", r"a^3+3a^2b+3ab^2+b^3=(a+b)^3", "Recognize or expand the cube of a binomial."),
    BoardFormula(14, "Special Factoring Identities", "Difference of cubes", r"a^3-b^3=(a-b)(a^2+ab+b^2)", "Factor a difference of cubes."),
    BoardFormula(15, "Special Factoring Identities", "Sum of cubes", r"a^3+b^3=(a+b)(a^2-ab+b^2)", "Factor a sum of cubes."),

    # Lines and slope — 16–23
    BoardFormula(16, "Lines and Slope", "Slope formula", r"m=\frac{y_2-y_1}{x_2-x_1}=\frac{y_1-y_2}{x_1-x_2}", "Compute vertical change divided by horizontal change.", (r"x_2\ne x_1",)),
    BoardFormula(17, "Lines and Slope", "Point-slope form", r"y-y_1=m(x-x_1)", "Write a line from a known point and slope."),
    BoardFormula(18, "Lines and Slope", "Slope-intercept form", r"y=mx+b", "Write a line using slope m and y-intercept b."),
    BoardFormula(19, "Lines and Slope", "Parallel lines", r"m_1=m_2", "Nonvertical parallel lines have equal slopes."),
    BoardFormula(20, "Lines and Slope", "Perpendicular lines", r"m_1m_2=-1", "Nonvertical/nonhorizontal perpendicular slopes are negative reciprocals."),
    BoardFormula(21, "Lines and Slope", "Vertical line", r"x=c", "A vertical line has constant x-coordinate."),
    BoardFormula(22, "Lines and Slope", "x-intercepts", r"(x,0)", "At an x-intercept the y-coordinate is zero."),
    BoardFormula(23, "Lines and Slope", "y-intercepts", r"(0,y)", "At a y-intercept the x-coordinate is zero."),

    # Coordinate geometry — 24–27
    BoardFormula(24, "Coordinate Geometry", "Distance formula", r"d(P_1,P_2)=\sqrt{(x_1-x_2)^2+(y_1-y_2)^2}", "Find the distance between two points."),
    BoardFormula(25, "Coordinate Geometry", "Midpoint formula", r"MP(P_1,P_2)=\left(\frac{x_1+x_2}{2},\frac{y_1+y_2}{2}\right)", "Average corresponding coordinates to find the midpoint."),
    BoardFormula(26, "Coordinate Geometry", "Perpendicular bisector", r"P\in\text{perpendicular bisector of }\overline{P_1P_2}\iff d(P,P_1)=d(P,P_2)", "The perpendicular bisector passes through the midpoint and is perpendicular to the segment; its points are equidistant from the endpoints."),
    BoardFormula(27, "Coordinate Geometry", "Equation of a circle", r"(x-h)^2+(y-k)^2=r^2", "A circle with center (h,k) and radius r."),

    # Quadratics — 28–30
    BoardFormula(28, "Quadratics", "Vertex form of a quadratic", r"f(x)=a(x-h)^2+k,\qquad h=-\frac{b}{2a},\qquad k=f\left(-\frac{b}{2a}\right)", "Rewrite or analyze a quadratic using its vertex (h,k).", (r"a\ne0",)),
    BoardFormula(29, "Quadratics", "Factored form from the roots", r"f(x)=ax^2+bx+c=a(x-r_1)(x-r_2)", "Write a quadratic from its roots r1 and r2.", (r"a\ne0",)),
    BoardFormula(30, "Quadratics", "Quadratic formula", r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}", "Solve ax^2+bx+c=0.", (r"a\ne0",)),

    # Logarithms — 31–36
    BoardFormula(31, "Logarithms", "Product rule", r"\log_b(xy)=\log_b(x)+\log_b(y)", "A product inside a logarithm becomes a sum of logarithms."),
    BoardFormula(32, "Logarithms", "Quotient rule", r"\log_b\left(\frac{x}{y}\right)=\log_b(x)-\log_b(y)", "A quotient inside a logarithm becomes a difference of logarithms."),
    BoardFormula(33, "Logarithms", "Power rule", r"\log_b(x^n)=n\log_b(x)", "Move an exponent in the logarithm argument to the front as a coefficient."),
    BoardFormula(34, "Logarithms", "Logarithm and exponential inverse rule", r"\log_b(b^x)=x", "Logarithms and exponentials with the same base undo each other."),
    BoardFormula(35, "Logarithms", "Exponential and logarithm inverse rule", r"b^{\log_b(x)}=x", "Exponentials and logarithms with the same base undo each other."),
    BoardFormula(36, "Logarithms", "Change-of-base formula", r"\frac{\log_c(a)}{\log_c(b)}=\log_b(a)", "Rewrite a logarithm using a convenient new base."),

    # Extra unnumbered board rule supplied with the transcription.
    BoardFormula(None, "Exponents and Radicals", "Even-index root of a matching power", r"\sqrt[n]{x^n}=|x|\quad\text{when }n\text{ is even}", "An even-index principal root is nonnegative."),
    BoardFormula(None, "Exponents and Radicals", "Odd-index root of a matching power", r"\sqrt[n]{x^n}=x\quad\text{when }n\text{ is odd}", "An odd-index root preserves the sign of x."),
)


FORMULA_BY_NUMBER: dict[int, BoardFormula] = {
    formula.number: formula for formula in BOARD_FORMULAS if formula.number is not None
}

FORMULAS_BY_TOPIC: dict[str, tuple[BoardFormula, ...]] = {
    topic: tuple(formula for formula in BOARD_FORMULAS if formula.topic == topic)
    for topic in dict.fromkeys(formula.topic for formula in BOARD_FORMULAS)
}


def formula_by_number(number: int) -> BoardFormula:
    """Return one of the professor's numbered board formulas."""
    return FORMULA_BY_NUMBER[number]


def formulas_for_topic(topic: str) -> tuple[BoardFormula, ...]:
    """Return all board formulas/rules in a topic group."""
    return FORMULAS_BY_TOPIC.get(topic, ())


def search_board_formulas(*terms: str) -> tuple[BoardFormula, ...]:
    """Find board references by topic/name/meaning for help and review features."""
    wanted = tuple(term.casefold().strip() for term in terms if term.strip())
    if not wanted:
        return BOARD_FORMULAS
    matches: list[BoardFormula] = []
    for formula in BOARD_FORMULAS:
        haystack = " ".join((formula.topic, formula.name, formula.meaning, formula.latex)).casefold()
        if any(term in haystack for term in wanted):
            matches.append(formula)
    return tuple(matches)
