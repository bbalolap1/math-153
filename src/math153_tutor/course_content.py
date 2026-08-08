from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CourseLesson:
    title: str
    explanation: str
    formulas: tuple[str, ...]
    example_prompt: str
    example_steps: tuple[str, ...]


COURSE_LESSONS: dict[str, tuple[CourseLesson, ...]] = {
    "Foundation": (
        CourseLesson(
            "Real numbers and signed arithmetic",
            "Natural, whole, integer, rational, and irrational numbers form nested sets. "
            "For signed arithmetic, decide the sign and magnitude separately.",
            (r"\mathbb{N}\subset\mathbb{W}\subset\mathbb{Z}\subset\mathbb{Q}\subset\mathbb{R}",),
            r"Evaluate\quad -8+3(5-7)",
            (r"5-7=-2", r"3(-2)=-6", r"-8+(-6)=-14"),
        ),
        CourseLesson(
            "Fractions, order, and exponents",
            "Use a common denominator only for addition or subtraction. Apply grouping, "
            "exponents, multiplication/division, then addition/subtraction.",
            (r"\frac{a}{b}+\frac{c}{d}=\frac{ad+bc}{bd}", r"a^m a^n=a^{m+n}"),
            r"\frac{2}{3}+\frac{5}{6}",
            (r"\frac{2}{3}=\frac{4}{6}", r"\frac{4}{6}+\frac{5}{6}=\frac{9}{6}", r"\frac{9}{6}=\frac{3}{2}"),
        ),
    ),
    "Chapters 1–2": (
        CourseLesson(
            "Equations, factoring, and restrictions",
            "Preserve equality by performing the same reversible operation on both sides. "
            "Factoring reveals products and rational-expression restrictions.",
            (r"ax+b=c\Rightarrow x=\frac{c-b}{a}", r"a^2-b^2=(a-b)(a+b)"),
            r"3x-7=11",
            (r"3x=18", r"x=6", r"3(6)-7=11\;\checkmark"),
        ),
        CourseLesson(
            "Radicals, quadratics, and inequalities",
            "Radicals and rational exponents are equivalent representations. Check radical "
            "equations for extraneous solutions and reverse an inequality after division by a negative.",
            (r"\sqrt[n]{a^m}=a^{m/n}", r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}"),
            r"x^2-5x+6=0",
            (r"(x-2)(x-3)=0", r"x=2\text{ or }x=3", r"\{2,3\}"),
        ),
    ),
    "Chapters 3–4": (
        CourseLesson(
            "Lines and coordinate geometry",
            "Slope is vertical change divided by horizontal change. Choose point-slope, "
            "slope-intercept, or standard form according to the information given.",
            (r"m=\frac{y_2-y_1}{x_2-x_1}", r"y-y_1=m(x-x_1)"),
            r"\text{Find the line through }(1,2)\text{ and }(3,6)",
            (r"m=\frac{6-2}{3-1}=2", r"y-2=2(x-1)", r"y=2x"),
        ),
        CourseLesson(
            "Functions, composition, and graphs",
            "A function assigns one output to each allowed input. For composition, evaluate "
            "the inner function first; graph features connect algebra to geometry.",
            (r"(f\circ g)(x)=f(g(x))", r"(x-h)^2+(y-k)^2=r^2"),
            r"f(x)=2x+1,\;g(x)=x^2:\quad(f\circ g)(3)",
            (r"g(3)=9", r"f(9)=2(9)+1", r"(f\circ g)(3)=19"),
        ),
    ),
    "Chapter 5": (
        CourseLesson(
            "Exponential functions and models",
            "Exponential change multiplies by a constant factor. Identify principal, rate, "
            "frequency, and time before choosing an interest model.",
            (r"A=P\left(1+\frac{r}{n}\right)^{nt}", r"A=Pe^{rt}"),
            r"P=1000,\;r=0.06,\;n=12,\;t=2",
            (r"A=1000\left(1+\frac{0.06}{12}\right)^{24}", r"A\approx1127.16"),
        ),
        CourseLesson(
            "Logarithms and equations",
            "A logarithm asks for an exponent. Convert between logarithmic and exponential "
            "forms, apply log properties, and require every logarithm argument to be positive.",
            (r"\log_b(x)=y\Longleftrightarrow b^y=x", r"\log_b(MN)=\log_bM+\log_bN"),
            r"\ln(x-1)=\ln 5",
            (r"x-1>0", r"x-1=5", r"x=6\text{ and }6-1>0\;\checkmark"),
        ),
    ),
}
