from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


SourceRole = Literal["lecture", "activity", "quiz", "test", "review", "final", "supplement"]
Representation = Literal[
    "symbolic", "verbal", "context", "graph", "table", "classification", "multipart"
]


@dataclass(frozen=True)
class SourceRef:
    """Traceable evidence for a piece of course knowledge."""
    document: str
    locator: str
    role: SourceRole


@dataclass(frozen=True)
class Formula:
    id: str
    expression: str
    meaning: str
    conditions: tuple[str, ...] = ()
    source_refs: tuple[SourceRef, ...] = ()


@dataclass(frozen=True)
class Procedure:
    id: str
    name: str
    objective: str
    prerequisites: tuple[str, ...]
    steps: tuple[str, ...]
    decision_points: tuple[str, ...] = ()
    verification_steps: tuple[str, ...] = ()
    source_refs: tuple[SourceRef, ...] = ()


@dataclass(frozen=True)
class WorkedExample:
    id: str
    prompt: str
    steps: tuple[str, ...]
    answer: str
    source_refs: tuple[SourceRef, ...]


@dataclass(frozen=True)
class ProblemFamily:
    """
    Source-grounded family definition used by recognition, generation,
    complexity, assessment, and mistake analysis.
    """
    id: str
    title: str
    learning_objectives: tuple[str, ...]
    recognition_features: tuple[str, ...]
    required_concepts: tuple[str, ...]
    required_procedures: tuple[str, ...]
    representations: tuple[Representation, ...]
    professor_verbs: tuple[str, ...]
    expected_answer_forms: tuple[str, ...]
    structural_variants: tuple[str, ...]
    common_mistakes: tuple[str, ...]
    verification_methods: tuple[str, ...] = ()
    application_contexts: tuple[str, ...] = ()
    source_refs: tuple[SourceRef, ...] = ()
    assessment_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class CourseSection:
    id: str
    chapter: int
    title: str
    unit_id: str
    summary: str
    learning_objectives: tuple[str, ...]
    concepts: tuple[str, ...]
    vocabulary: tuple[str, ...]
    rules: tuple[str, ...]
    formulas: tuple[Formula, ...]
    procedures: tuple[Procedure, ...]
    worked_examples: tuple[WorkedExample, ...]
    problem_families: tuple[ProblemFamily, ...]
    connections: tuple[str, ...]
    source_refs: tuple[SourceRef, ...]


@dataclass(frozen=True)
class CourseUnit:
    id: str
    title: str
    chapter_ids: tuple[int, ...]
    section_ids: tuple[str, ...]
    purpose: str


@dataclass(frozen=True)
class Course:
    id: str
    title: str
    units: tuple[CourseUnit, ...]
    sections: tuple[CourseSection, ...]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def R(document: str, locator: str, role: SourceRole = "lecture") -> SourceRef:
    return SourceRef(document, locator, role)


def F(
    id: str,
    expression: str,
    meaning: str,
    *refs: SourceRef,
    conditions: tuple[str, ...] = (),
) -> Formula:
    return Formula(id, expression, meaning, conditions, tuple(refs))


def P(
    id: str,
    name: str,
    objective: str,
    prerequisites: tuple[str, ...],
    steps: tuple[str, ...],
    *refs: SourceRef,
    decision_points: tuple[str, ...] = (),
    verification_steps: tuple[str, ...] = (),
) -> Procedure:
    return Procedure(
        id=id,
        name=name,
        objective=objective,
        prerequisites=prerequisites,
        steps=steps,
        decision_points=decision_points,
        verification_steps=verification_steps,
        source_refs=tuple(refs),
    )


def E(
    id: str,
    prompt: str,
    steps: tuple[str, ...],
    answer: str,
    *refs: SourceRef,
) -> WorkedExample:
    return WorkedExample(id, prompt, steps, answer, tuple(refs))


def PF(
    id: str,
    title: str,
    learning_objectives: tuple[str, ...],
    recognition_features: tuple[str, ...],
    required_concepts: tuple[str, ...],
    required_procedures: tuple[str, ...],
    representations: tuple[Representation, ...],
    professor_verbs: tuple[str, ...],
    expected_answer_forms: tuple[str, ...],
    structural_variants: tuple[str, ...],
    common_mistakes: tuple[str, ...],
    *refs: SourceRef,
    verification_methods: tuple[str, ...] = (),
    application_contexts: tuple[str, ...] = (),
    assessment_refs: tuple[str, ...] = (),
) -> ProblemFamily:
    return ProblemFamily(
        id=id,
        title=title,
        learning_objectives=learning_objectives,
        recognition_features=recognition_features,
        required_concepts=required_concepts,
        required_procedures=required_procedures,
        representations=representations,
        professor_verbs=professor_verbs,
        expected_answer_forms=expected_answer_forms,
        structural_variants=structural_variants,
        common_mistakes=common_mistakes,
        verification_methods=verification_methods,
        application_contexts=application_contexts,
        source_refs=tuple(refs),
        assessment_refs=assessment_refs,
    )


# ---------------------------------------------------------------------------
# Foundation
# ---------------------------------------------------------------------------

FOUNDATION = CourseSection(
    id="F0",
    chapter=0,
    title="Foundation — number systems, arithmetic, notation, and algebra language",
    unit_id="FOUNDATION",
    summary=(
        "Prerequisite review used throughout Math 153: classification of real numbers, signed "
        "operations, fractions, order, absolute value, scientific notation, algebra vocabulary, "
        "and exact arithmetic."
    ),
    learning_objectives=(
        "Classify numbers in the nested real-number system.",
        "Perform signed arithmetic and fraction operations exactly.",
        "Use order and absolute-value notation correctly.",
        "Interpret algebraic notation before applying a procedure.",
    ),
    concepts=("real numbers", "rational numbers", "irrational numbers", "integers",
              "fractions", "absolute value", "scientific notation", "order"),
    vocabulary=("natural", "whole", "integer", "rational", "irrational", "real",
                "absolute value", "numerator", "denominator"),
    rules=(
        "Use a common denominator for fraction addition/subtraction.",
        "Absolute value represents distance from zero and is nonnegative.",
        "Preserve exact fractions/radicals when an exact answer is requested.",
    ),
    formulas=(
        F("F0-NESTED-SETS", r"\mathbb{N}\subset\mathbb{W}\subset\mathbb{Z}\subset\mathbb{Q}\subset\mathbb{R}",
          "Nested number-system relationship.", R("1.1.md", "Page 1 — Complex Numbers")),
        F("F0-FRACTION-ADD", r"\frac{a}{b}+\frac{c}{d}=\frac{ad+bc}{bd}",
          "General fraction-addition relationship.", R("1.1.md", "Page 4 — Adding Fractions")),
    ),
    procedures=(
        P("F0-CLASSIFY", "Classify a number", "Place a value in every applicable number set.",
          ("number-set definitions",),
          ("Identify whether the value is an integer.", "Determine whether it can be expressed as a fraction.",
           "Determine whether it is irrational.", "Report all applicable nested sets."),
          R("1.1.md", "Page 1 — Complex Numbers")),
        P("F0-SIGNED-ARITH", "Signed arithmetic", "Evaluate exact signed expressions.",
          ("addition", "multiplication", "order of operations"),
          ("Resolve grouping.", "Apply multiplication/division.", "Apply addition/subtraction.",
           "Check the sign and magnitude separately."),
          R("1.1.md", "Page 2 — Major Operations on Real Numbers")),
    ),
    worked_examples=(
        E("F0-EX1", r"\frac23+\frac56",
          (r"\frac23=\frac46", r"\frac46+\frac56=\frac96", r"\frac96=\frac32"),
          r"\frac32", R("1.1.md", "Page 4 — Adding Fractions")),
    ),
    problem_families=(
        PF("F0-REAL-NUMBERS", "Real-number classification",
           ("Classify values by number set.",),
           ("A value is presented alone or inside a classification statement.",),
           ("number sets",), ("F0-CLASSIFY",), ("classification", "symbolic"),
           ("classify", "identify"), ("set membership",),
           ("integer/rational/irrational swap", "nested-set multi-select"),
           ("Stopping at the smallest set and omitting larger containing sets.",),
           R("1.1.md", "Page 1 — Complex Numbers")),
        PF("F0-ARITHMETIC", "Exact signed and fractional arithmetic",
           ("Evaluate exact arithmetic without changing mathematical meaning.",),
           ("Nested signs, fractions, grouping, and operations.",),
           ("signed arithmetic", "fractions"), ("F0-SIGNED-ARITH",),
           ("symbolic",), ("simplify", "evaluate"), ("exact number",),
           ("nested grouping", "mixed integer/fraction form", "negative-factor emphasis"),
           ("Losing a negative sign.", "Adding denominators directly."),
           R("1.1.md", "Pages 2–4")),
    ),
    connections=(
        "Exact fraction arithmetic reappears in rational expressions, slope, logarithms, and formula manipulation.",
        "Absolute value becomes an equation/inequality topic in Chapter 2.",
    ),
    source_refs=(R("1.1.md", "Pages 1–5"),),
)


# ---------------------------------------------------------------------------
# Unit 1 — Chapters 1 and 2
# ---------------------------------------------------------------------------

SECTION_1_1 = CourseSection(
    id="1.1", chapter=1, title="Complex Numbers and Major Operations on Real Numbers", unit_id="UNIT1",
    summary="Real-number structure, core arithmetic operations, order, absolute value, and scientific notation.",
    learning_objectives=(
        "Distinguish real, rational, irrational, integer, and complex-number language.",
        "Operate correctly with signed numbers and fractions.",
        "Use inequalities, absolute value, and scientific notation.",
    ),
    concepts=("complex-number system", "real numbers", "rational/irrational", "order", "absolute value", "scientific notation"),
    vocabulary=("complex", "real", "rational", "irrational", "integer", "inequality", "absolute value"),
    rules=(
        "Subtraction is addition of an opposite.",
        "Division by zero is undefined.",
        "Absolute value is nonnegative.",
    ),
    formulas=(
        F("1.1-ABS", r"|x|=\begin{cases}x,&x\ge0\\-x,&x<0\end{cases}",
          "Piecewise meaning of absolute value.", R("1.1.md", "Page 5 — Absolute Value")),
    ),
    procedures=(
        P("1.1-ORDER", "Compare real numbers", "Choose the correct inequality relation.",
          ("real-number order",), ("Place values on or mentally compare along the number line.",
          "Account for signs.", "Select <, >, or =."), R("1.1.md", "Page 4 — Order on Real Numbers")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH1-REAL-ORDER", "Ordering and absolute-value interpretation",
           ("Compare exact real values and interpret absolute value.",),
           ("Inequality blanks, absolute-value notation, signed values."),
           ("order", "absolute value"), ("1.1-ORDER",), ("symbolic", "classification"),
           ("fill in", "evaluate", "compare"), ("number", "inequality statement"),
           ("fraction vs decimal comparison", "negative-value ordering", "absolute-value nesting"),
           ("Reversing order for negative numbers.",), R("1.1.md", "Pages 4–5")),
    ),
    connections=("Prepares interval notation and absolute-value equations/inequalities in Chapter 2.",),
    source_refs=(R("1.1.md", "Entire lecture"),),
)


SECTION_1_2 = CourseSection(
    id="1.2", chapter=1, title="Exponents and Radicals", unit_id="UNIT1",
    summary="Exponent laws, radical notation, rational exponents, simplification, and rationalization.",
    learning_objectives=(
        "Apply exponent laws without changing bases incorrectly.",
        "Move between radical and rational-exponent forms.",
        "Simplify radicals by extracting perfect powers.",
        "Rationalize denominators, including higher-index radicals.",
    ),
    concepts=("integer exponents", "negative exponents", "radicals", "rational exponents", "rationalization"),
    vocabulary=("base", "exponent", "index", "radicand", "rational exponent"),
    rules=(
        r"a^m a^n=a^{m+n}.",
        r"\frac{a^m}{a^n}=a^{m-n}, a\ne0.",
        r"(a^m)^n=a^{mn}.",
        r"a^{-n}=\frac1{a^n}.",
        "For an even root of an even power, preserve absolute value when the sign is not known.",
    ),
    formulas=(
        F("1.2-RAT-EXP", r"a^{m/n}=\sqrt[n]{a^m}", "Rational exponent/radical equivalence.",
          R("1.2.md", "Page 4 — Radicals as Fractional Exponents")),
        F("1.2-EVEN-ROOT", r"\sqrt{x^2}=|x|", "Even roots return the principal nonnegative value.",
          R("1.2.md", "Radical simplification"), R("Quiz_2.md", "Q.1", "quiz")),
    ),
    procedures=(
        P("1.2-SIMPLIFY-RADICAL", "Simplify a radical", "Extract all possible perfect powers.",
          ("factorization", "exponent laws"),
          ("Factor the radicand.", "Group powers matching the root index.", "Extract complete groups.",
           "Retain any unmatched factors under the radical.", "Apply absolute value when required."),
          R("1.2.md", "Page 5 — Simplifying Radical Expressions")),
        P("1.2-RATIONALIZE", "Rationalize a denominator", "Remove radicals from the denominator.",
          ("radical multiplication", "exponent laws"),
          ("Identify the factor needed to complete the root-index power.", "Multiply numerator and denominator.",
           "Simplify the resulting powers and radicals."),
          R("1.2.md", "Page 6 — Rationalizing the Denominator")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH1-RADICAL-PRODUCT", "Products of radicals with symbolic powers",
           ("Simplify products of radicals fully.",),
           ("Two radicals with the same index and symbolic powers.",),
           ("radicals", "exponent laws"), ("1.2-SIMPLIFY-RADICAL",), ("symbolic",),
           ("simplify",), ("simplified radical/exact expression",),
           ("different root indices", "variables requiring absolute value", "product before extraction"),
           ("Extracting a non-perfect power.", "Dropping absolute value for even roots."),
           R("1.2.md", "Page 5"), R("Quiz_1.md", "Q.1", "quiz"), R("Quiz_2.md", "Q.1", "quiz"),
           assessment_refs=("Quiz 1 Q1", "Quiz 2 Q1", "Test 1 Q2")),
        PF("CH1-RATIONALIZE-DENOMINATOR", "Rationalize radical denominators",
           ("Produce an equivalent expression with a rational denominator.",),
           ("A radical remains in a denominator.",),
           ("radicals", "rationalization"), ("1.2-RATIONALIZE",), ("symbolic",),
           ("rationalize the denominator", "simplify and rationalize"), ("exact expression",),
           ("square-root conjugate", "higher-index completion", "symbolic powers"),
           ("Multiplying by the same radical when a higher-index complement is required.",),
           R("1.2.md", "Page 6"), R("Test_1.md", "Q.3", "test"), R("Test_1_Review.md", "Q.1", "review"),
           assessment_refs=("Test 1 Q3", "Test 1 Review Q1")),
    ),
    connections=(
        "Rational exponents return in Section 2.5 equations.",
        "Radical/domain restrictions return in functions and compositions.",
    ),
    source_refs=(R("1.2.md", "Entire lecture"),),
)


SECTION_1_3 = CourseSection(
    id="1.3", chapter=1, title="Polynomials and Factoring", unit_id="UNIT1",
    summary="Polynomial vocabulary and operations followed by systematic factoring identities and grouping.",
    learning_objectives=(
        "Identify degree, leading term, and coefficients.",
        "Add, subtract, and multiply polynomials.",
        "Fully factor using GCF, identities, trinomials, and grouping.",
    ),
    concepts=("polynomial", "degree", "leading coefficient", "factoring", "special products", "grouping"),
    vocabulary=("term", "coefficient", "degree", "leading term", "factor", "GCF"),
    rules=(
        "Factor out a greatest common factor before applying a more specialized identity.",
        "A fully factored result should not contain a remaining factorable polynomial over the intended number system.",
    ),
    formulas=(
        F("1.3-DIFF-SQ", r"a^2-b^2=(a-b)(a+b)", "Difference of squares.",
          R("1.3.md", "Page 4 — Factoring Identities")),
        F("1.3-SUM-CUBES", r"a^3+b^3=(a+b)(a^2-ab+b^2)", "Sum of cubes.",
          R("1.3.md", "Page 4 — Factoring Identities")),
        F("1.3-DIFF-CUBES", r"a^3-b^3=(a-b)(a^2+ab+b^2)", "Difference of cubes.",
          R("1.3.md", "Page 4 — Factoring Identities")),
    ),
    procedures=(
        P("1.3-FACTOR", "Fully factor a polynomial", "Express a polynomial as irreducible factors.",
          ("polynomial arithmetic",),
          ("Extract the GCF.", "Count terms and inspect structure.", "Apply a matching identity/trinomial/grouping method.",
           "Repeat factoring on every factor.", "Optionally multiply back to verify."),
          R("1.3.md", "Pages 4–6"),
          decision_points=("GCF?", "difference of squares?", "sum/difference of cubes?", "trinomial?", "grouping?"),
          verification_steps=("Multiply the factors to recover the original polynomial.",)),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH1-FACTOR-GROUPING", "Factoring by grouping",
           ("Recognize a four-term grouping structure and factor completely.",),
           ("Four terms can be paired to expose a common binomial factor.",),
           ("factoring", "GCF"), ("1.3-FACTOR",), ("symbolic",),
           ("fully factor", "factor"), ("factored expression",),
           ("reordered terms", "sign extraction", "nested GCF plus grouping"),
           ("Grouping terms that do not produce the same binomial.", "Stopping after the first GCF."),
           R("1.3.md", "Page 6 — Factoring by Grouping"), R("Quiz_1.md", "Q.3", "quiz"),
           assessment_refs=("Quiz 1 Q3", "Test 1 Review Q4")),
        PF("CH1-FACTOR-QUADRATIC", "Factoring quadratic trinomials",
           ("Factor quadratics and connect factors to zeros when asked.",),
           ("Three-term quadratic or a quadratic after a GCF/sign extraction.",),
           ("quadratic factoring",), ("1.3-FACTOR",), ("symbolic",),
           ("fully factor", "factor and solve"), ("factored expression", "solution set"),
           ("leading coefficient not 1", "negative leading coefficient", "factor-then-solve"),
           ("Ignoring the leading coefficient.", "Failing to factor completely."),
           R("1.3.md", "Pages 5–6"), R("Quiz_1.md", "Q.4", "quiz"),
           R("Test_1_Review.md", "Q.3", "review"),
           assessment_refs=("Quiz 1 Q4", "Test 1 Review Q3")),
    ),
    connections=("Factoring is prerequisite knowledge for rational expressions, polynomial equations, inequalities, and polynomial graphs.",),
    source_refs=(R("1.3.md", "Entire lecture"),),
)


SECTION_1_4 = CourseSection(
    id="1.4", chapter=1, title="Fractional and Rational Expressions", unit_id="UNIT1",
    summary="Restrictions, simplification, arithmetic with rational expressions, division, and numerator/denominator rationalization.",
    learning_objectives=(
        "Determine restrictions from the original expression.",
        "Factor before canceling and cancel factors rather than terms.",
        "Add/subtract rational expressions using an LCD.",
        "Multiply/divide rational expressions and rationalize when required.",
    ),
    concepts=("rational expression", "domain restriction", "LCD", "common factor", "conjugate", "difference quotient pattern"),
    vocabulary=("rational expression", "restriction", "LCD", "factor", "conjugate"),
    rules=(
        "A denominator may not equal zero.",
        "Only common factors may be canceled; terms separated by + or - are not cancelable.",
        "Restrictions from the original expression remain restrictions after simplification.",
    ),
    formulas=(),
    procedures=(
        P("1.4-SIMPLIFY", "Simplify a rational expression", "Reduce while preserving original restrictions.",
          ("factoring",),
          ("Factor numerator and denominator completely.", "Record denominator zeros from the original expression.",
           "Cancel common factors.", "State the simplified expression with original restrictions."),
          R("1.4.md", "Pages 2 and 4")),
        P("1.4-COMBINE", "Add/subtract rational expressions", "Combine into one simplified rational expression.",
          ("factoring", "fraction arithmetic"),
          ("Factor denominators.", "Find the LCD.", "Rewrite each fraction over the LCD.", "Combine numerators.",
           "Factor/simplify the result.", "Preserve restrictions."),
          R("1.4.md", "Page 2 — Simplifying and Combining Rational Expressions")),
        P("1.4-RATIONALIZE-NUM", "Rationalize a numerator", "Remove a radical from a numerator using an identity/conjugate.",
          ("conjugates", "difference of squares"),
          ("Identify the conjugate or appropriate cube identity.", "Multiply by a form of 1.",
           "Use the product identity to remove the radical from the target position.", "Simplify."),
          R("1.4.md", "Pages 5–6 — Rationalizing a Numerator")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH1-RATIONAL-SIMPLIFY", "Simplify rational expressions with restrictions",
           ("Factor, reduce, and preserve excluded values.",),
           ("Polynomial numerator/denominator with common factors.",),
           ("factoring", "restrictions"), ("1.4-SIMPLIFY",), ("symbolic",),
           ("simplify", "simplify and fully factor"), ("rational expression + restrictions",),
           ("single fraction", "complex factorization", "cancellation creates a hole"),
           ("Canceling terms instead of factors.", "Dropping excluded values after cancellation."),
           R("1.4.md", "Pages 2–4"), R("Quiz_2.md", "Q.3", "quiz"),
           assessment_refs=("Quiz 2 Q3", "Quiz 6 Q3")),
        PF("CH1-RATIONAL-COMBINE", "Combine rational expressions",
           ("Use an LCD and simplify a multi-term rational expression.",),
           ("Two or more fractions with related factored denominators.",),
           ("LCD", "factoring"), ("1.4-COMBINE",), ("symbolic",),
           ("simplify", "simplify into one rational expression"), ("one rational expression",),
           ("three-term sum/difference", "denominators factor to shared binomials", "numerator later factors"),
           ("Adding denominators.", "Using an incomplete LCD.", "Not factoring the final numerator."),
           R("1.4.md", "Page 2"), R("Quiz_2.md", "Q.4", "quiz"), R("Test_1_Review.md", "Q.5", "review"),
           assessment_refs=("Quiz 2 Q4", "Test 1 Review Q5")),
        PF("CH1-RATIONAL-DIVIDE", "Divide rational expressions",
           ("Rewrite division as multiplication by the reciprocal and simplify fully.",),
           ("A quotient of rational expressions.",),
           ("factoring", "restrictions"), ("1.4-SIMPLIFY",), ("symbolic",),
           ("simplify",), ("factored rational expression",),
           ("factor-before-reciprocal cancellation", "multiple restriction sources"),
           ("Forgetting to invert the divisor.", "Canceling before factoring."),
           R("1.4.md", "Page 3 — Division"), R("Quiz_1.md", "Q.2", "quiz"), R("Test_1.md", "Q.6", "test"),
           assessment_refs=("Quiz 1 Q2", "Test 1 Q6")),
        PF("CH1-RATIONALIZE-NUMERATOR", "Rationalize a numerator",
           ("Use conjugates or higher-power identities to rationalize a numerator.",),
           ("Radical expression in the numerator with a paired denominator.",),
           ("radicals", "conjugates", "factoring identities"), ("1.4-RATIONALIZE-NUM",),
           ("symbolic",), ("rationalize the numerator",), ("equivalent exact expression",),
           ("square-root conjugate", "difference quotient", "higher-index identity"),
           ("Using the wrong conjugate/sign.", "Failing to simplify the identity product."),
           R("1.4.md", "Pages 5–6"), R("Test_1.md", "Q.4", "test"), R("Test_1_Review.md", "Q.2", "review"),
           assessment_refs=("Test 1 Q4", "Test 1 Review Q2")),
    ),
    connections=("Restrictions and extraneous values become central in rational equations and rational functions.",),
    source_refs=(R("1.4.md", "Entire lecture"),),
)


SECTION_2_1 = CourseSection(
    id="2.1", chapter=2, title="Equations", unit_id="UNIT1",
    summary="Equation classification, equivalence, solving, rational equations, domain, and verification.",
    learning_objectives=(
        "Classify equations as identities, conditional equations, or contradictions.",
        "Use reversible operations to create equivalent equations.",
        "Solve rational equations while respecting the original domain.",
    ),
    concepts=("equation", "identity", "conditional equation", "contradiction", "equivalence", "domain"),
    vocabulary=("identity", "conditional", "contradiction", "equivalent equations", "solution set"),
    rules=(
        "Apply the same valid operation to both sides to preserve equality.",
        "Multiplying by an expression that can be zero can change the domain/equivalence and requires checking.",
        "A candidate excluded from the original domain is not a solution.",
    ),
    formulas=(),
    procedures=(
        P("2.1-SOLVE-EQ", "Solve and verify an equation", "Find all values satisfying the original equation.",
          ("algebra operations",),
          ("Determine the original domain.", "Apply reversible transformations.", "Solve the resulting equation.",
           "Substitute candidates into the original equation.", "State the solution set."),
          R("2.1.md", "Pages 3–5"),
          decision_points=("Does the equation have denominators?", "Could an operation introduce candidates?"),
          verification_steps=("Check every candidate in the original equation.",)),
        P("2.1-CLASSIFY", "Classify an equation", "Determine whether its solution behavior is identity/conditional/contradiction.",
          ("simplification",),
          ("Simplify both sides.", "Observe whether a variable condition remains, a true statement remains, or a false statement remains.",
           "State the classification and solution set."),
          R("2.1.md", "Page 2 — Identity, Conditional, Contradiction")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH2-EQUATION-CLASSIFY", "Identity, conditional, and contradiction equations",
           ("Classify equations by their solution sets.",),
           ("After simplification, the variable may cancel or yield a condition.",),
           ("equation classification",), ("2.1-CLASSIFY",), ("classification", "symbolic"),
           ("classify", "solve"), ("classification + solution set",),
           ("identity disguised by rational expressions", "contradiction after cancellation", "conditional linear equation"),
           ("Calling every canceled-variable equation an identity without checking the remaining statement.",),
           R("2.1.md", "Pages 2, 6–7")),
        PF("CH2-RATIONAL-EQUATIONS", "Rational equations with domain checks",
           ("Solve equations containing rational expressions and reject excluded candidates.",),
           ("Variable appears in one or more denominators.",),
           ("LCD", "restrictions", "factoring"), ("2.1-SOLVE-EQ",), ("symbolic",),
           ("solve", "state the domain, then solve"), ("solution set",),
           ("single excluded value", "multiple denominators", "candidate equals excluded value", "identity after clearing denominators"),
           ("Forgetting the original domain.", "Treating an excluded candidate as a solution."),
           R("2.1.md", "Pages 4–5, 9"),
           verification_methods=("Substitute into the original rational equation.",)),
    ),
    connections=("Equation-domain reasoning reappears in radical, logarithmic, rational-function, and composite-function problems.",),
    source_refs=(R("2.1.md", "Entire lecture"),),
)


SECTION_2_2 = CourseSection(
    id="2.2", chapter=2, title="Applied Problems", unit_id="UNIT1",
    summary="Translate contextual information into equations for averages, discounts, interest, mixtures, work/rates, and motion.",
    learning_objectives=(
        "Define variables from a word problem.",
        "Translate verbal relationships into equations.",
        "Solve and interpret answers with units and context.",
    ),
    concepts=("mathematical modeling", "average", "percent", "simple interest", "mixture", "rate", "distance"),
    vocabulary=("principal", "rate", "time", "mixture", "average", "discount", "markup"),
    rules=("Keep units consistent before forming an equation.", "Check whether a numerical solution makes sense in context."),
    formulas=(
        F("2.2-SIMPLE-INTEREST", r"A=P+Prt=P(1+rt)", "Simple-interest amount relationship.",
          R("2.2.md", "Page 3 — Simple Interest")),
        F("2.2-MOTION", r"d=rt", "Distance-rate-time relationship.",
          R("2.2.md", "Page 7 — Distance, Speed, and Time")),
    ),
    procedures=(
        P("2.2-MODEL", "Translate and solve an application problem", "Create a mathematical model from context.",
          ("linear equations", "fractions/percents"),
          ("Identify the unknown and define variables.", "Convert units.", "Translate each stated relationship.",
           "Build the governing equation.", "Solve.", "Interpret with units.", "Check plausibility."),
          R("2.2.md", "Entire lecture"),
          decision_points=("Which quantity is conserved/equal?", "Are rates simultaneous or sequential?", "Do units match?"),
          verification_steps=("Substitute into the contextual relationships.",)),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH2-MIXTURE", "Mixture and weighted-average problems",
           ("Build and solve a conservation equation for amounts/concentrations.",),
           ("Two sources combine into a specified total or percentage.",),
           ("percent", "linear modeling"), ("2.2-MODEL",), ("context",),
           ("how many", "how much", "prepare"), ("quantity with units",),
           ("alloy/solution mixture", "weighted grade", "ticket/revenue system"),
           ("Adding percentages instead of weighted amounts.", "Ignoring total-quantity conservation."),
           R("2.2.md", "Pages 5–6"), R("Test_1_Review.md", "Q.8", "review"),
           application_contexts=("mixture", "weighted average"),
           assessment_refs=("Test 1 Review Q8", "Test 1 Q13")),
        PF("CH2-RATE-MOTION-WORK", "Rate, motion, catch-up, and combined-work problems",
           ("Translate rate relationships into time/distance/work equations.",),
           ("Different rates, delays, opposite directions, or combined rates.",),
           ("rate", "time", "distance"), ("2.2-MODEL",), ("context",),
           ("when", "how long", "how many minutes"), ("time or distance with units",),
           ("same-direction catch-up", "opposite directions", "two workers/hoses", "communication-range threshold"),
           ("Using clock time instead of elapsed time.", "Adding times instead of rates for combined work."),
           R("2.2.md", "Page 7"), R("Test_1.md", "Q.11", "test"), R("Test_1_Review.md", "Q.7", "review"),
           R("Quiz_3.md", "Q.2", "quiz"),
           application_contexts=("motion", "work rate"),
           assessment_refs=("Test 1 Q11", "Test 1 Review Q7", "Quiz 3 Q2")),
        PF("CH2-FORMULA-REARRANGE", "Literal/formula equations in applications",
           ("Solve a formula for a specified variable.",),
           ("A named application formula is given and one variable must be isolated.",),
           ("equation solving",), ("2.2-MODEL",), ("symbolic", "context"),
           ("express ... in terms of",), ("formula",),
           ("factor target variable", "target appears in multiple terms"),
           ("Substituting numbers when symbolic rearrangement is requested.",),
           R("2.2.md", "Simple Interest"), R("Test_1.md", "Q.17", "test"),
           assessment_refs=("Test 1 Q17",)),
    ),
    connections=("Application translation feeds linear, quadratic, exponential, and logarithmic modeling later in the course.",),
    source_refs=(R("2.2.md", "Entire lecture"),),
)


SECTION_2_3 = CourseSection(
    id="2.3", chapter=2, title="Quadratic Equations", unit_id="UNIT1",
    summary="Factoring, completing the square, quadratic formula, discriminant, complex roots, and parameter manipulation.",
    learning_objectives=(
        "Choose among factoring, square-root/completing-square, and quadratic-formula methods.",
        "Write a quadratic in completed-square form.",
        "Use the discriminant to classify roots.",
        "Solve quadratics exactly, including complex solutions.",
    ),
    concepts=("quadratic equation", "zero-factor theorem", "completing the square", "quadratic formula", "discriminant", "vertex form"),
    vocabulary=("quadratic", "root", "zero", "discriminant", "completed-square form", "vertex form"),
    rules=("Set the equation equal to zero before zero-factor reasoning.", "State the general formula when a question explicitly requests it."),
    formulas=(
        F("2.3-QF", r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}", "Quadratic formula.",
          R("2.3.md", "Page 9 — Deriving the Quadratic Formula"), R("Test_1.md", "Q.10", "test")),
        F("2.3-DISC", r"\Delta=b^2-4ac", "Discriminant controlling the nature of roots.",
          R("2.3.md", "Page 10 — Discriminant")),
        F("2.3-COMPLETE", r"ax^2+bx+c=a\left(x+\frac{b}{2a}\right)^2+c-\frac{b^2}{4a}",
          "General completed-square formula.",
          R("Completing_the_Square.md", "General Formula", "supplement")),
    ),
    procedures=(
        P("2.3-FACTOR-SOLVE", "Solve a quadratic by factoring", "Use zero-product structure.",
          ("factoring",), ("Move all terms to one side.", "Factor completely.", "Set each factor equal to zero.",
          "Solve each equation.", "Check if required."), R("2.3.md", "Pages 2–3")),
        P("2.3-COMPLETE-SQUARE", "Complete the square", "Rewrite/solve a quadratic using one squared binomial.",
          ("binomial square", "fraction arithmetic"),
          ("Factor the leading coefficient from x-terms if necessary.", "Take half of the normalized x coefficient.",
           "Construct the squared binomial.", "Compensate/compare constants.", "Write completed-square form.",
           "If solving, isolate the square and take both square roots."),
          R("2.3.md", "Pages 4–8"), R("Completing_the_Square.md", "Examples 1–2", "supplement"),
          decision_points=("Is the leading coefficient 1 inside the square?", "Is the task rewrite-only or solve?"),
          verification_steps=("Expand the completed-square form to recover the original quadratic.",)),
        P("2.3-QUADRATIC-FORMULA", "Solve with the quadratic formula", "Obtain exact real or complex roots.",
          ("radicals", "complex numbers"),
          ("Put the equation in standard form.", "Identify a, b, c with signs.", "Compute the discriminant.",
           "Substitute into the quadratic formula.", "Simplify exactly."), R("2.3.md", "Pages 9–10")),
    ),
    worked_examples=(
        E("2.3-CS-EX", r"3x^2-15x+20",
          (r"3(x^2-5x)+20", r"3\left(x-\frac52\right)^2+d",
           r"d=20-\frac{75}{4}=\frac54"),
          r"3\left(x-\frac52\right)^2+\frac54",
          R("Completing_the_Square.md", "Example 1", "supplement")),
    ),
    problem_families=(
        PF("CH2-QUADRATIC-METHOD-SELECTION", "Quadratic method selection",
           ("Recognize when factoring, completing the square, or the quadratic formula is appropriate.",),
           ("A quadratic may be factorable, already square-like, or nonfactorable over the reals.",),
           ("quadratics", "factoring", "radicals"), ("2.3-FACTOR-SOLVE", "2.3-COMPLETE-SQUARE", "2.3-QUADRATIC-FORMULA"),
           ("symbolic",), ("solve", "find all real solutions", "find all complex solutions"),
           ("solution set", "exact complex values"),
           ("factorable", "nonfactorable", "hidden quadratic after expansion", "formula explicitly required"),
           ("Applying zero-factor theorem before setting equal to zero.", "Misidentifying b's sign."),
           R("2.3.md", "Definition and Three Methods"), R("Test_1.md", "Q.7/Q.10", "test"),
           assessment_refs=("Test 1 Q7", "Test 1 Q10")),
        PF("CH2-COMPLETING-SQUARE", "Completed-square form and roots",
           ("Rewrite quadratics in completed-square form and use that structure.",),
           ("Prompt requests a(x+b)^2+c or vertex-like form.",),
           ("quadratic", "binomial square"), ("2.3-COMPLETE-SQUARE",), ("symbolic",),
           ("express in completed-square form", "write in completed-square form"), ("completed-square expression",),
           ("positive/negative leading coefficient", "fractional center", "rewrite then solve"),
           ("Using b/2 from the original rather than normalized coefficient.", "Failing to compensate for outside a."),
           R("Completing_the_Square.md", "General Formula and Examples", "supplement"),
           R("Quiz_3.md", "Q.1", "quiz"),
           assessment_refs=("Quiz 3 Q1",)),
        PF("CH2-QUADRATIC-TYPE", "Quadratic-type equations by substitution",
           ("Recognize a repeated-power structure and reduce it to a quadratic.",),
           ("Powers occur as u^2 and u after a substitution such as x^2, x^(1/4), or a rational expression.",),
           ("substitution", "quadratics"), ("2.3-FACTOR-SOLVE",), ("symbolic",),
           ("find all real numbers", "find all real solutions"), ("solution set",),
           ("x^4/x^2", "fractional exponents", "rational-expression substitution"),
           ("Stopping after solving for the substituted variable.", "Keeping substituted values incompatible with the original domain."),
           R("2.5.md", "Pages 2–5"), R("Test_1.md", "Q.14", "test"), R("Test_1_Review.md", "Q.12", "review"),
           assessment_refs=("Test 1 Q14", "Test 1 Review Q12")),
    ),
    connections=("Quadratic structure returns in functions, circles, polynomial zeros, and transformed exponential equations.",),
    source_refs=(R("2.3.md", "Entire lecture"), R("Completing_the_Square.md", "Entire supplement", "supplement")),
)


SECTION_2_4 = CourseSection(
    id="2.4", chapter=2, title="Complex Numbers", unit_id="UNIT1",
    summary="Imaginary unit, complex arithmetic, powers of i, conjugates, quotients, and quadratic complex roots.",
    learning_objectives=(
        "Write complex values in a+bi form.",
        "Compute powers of i using periodicity.",
        "Multiply/divide complex numbers using conjugates.",
        "Solve equations yielding complex roots.",
    ),
    concepts=("imaginary unit", "complex number", "conjugate", "complex root"),
    vocabulary=("real part", "imaginary part", "conjugate", "imaginary unit"),
    rules=(r"i^2=-1.", "A complex quotient is simplified by multiplying numerator and denominator by the denominator's conjugate."),
    formulas=(F("2.4-CONJ", r"(a+bi)(a-bi)=a^2+b^2", "Conjugate product is real.",
                R("2.4.md", "Pages 4–6 — Complex Conjugates")),),
    procedures=(
        P("2.4-DIVIDE", "Divide complex numbers", "Write a quotient in a+bi form.",
          ("complex multiplication",),
          ("Identify the denominator's conjugate.", "Multiply numerator and denominator by it.",
           "Use i^2=-1.", "Combine real and imaginary terms.", "Reduce coefficients."),
          R("2.4.md", "Pages 6–7")),
        P("2.4-I-POWER", "Reduce a power of i", "Use the 4-cycle of powers.",
          ("integer division/remainders",), ("Reduce the exponent modulo 4.", "Map the remainder to 1, i, -1, or -i."),
          R("2.4.md", "Pages 3–5")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH2-COMPLEX-QUOTIENT", "Complex quotient to a+bi",
           ("Simplify a complex quotient into standard form.",),
           ("Complex denominator requires conjugate multiplication.",),
           ("complex arithmetic", "conjugate"), ("2.4-DIVIDE",), ("symbolic",),
           ("simplify into a+bi", "express as a single complex number"), ("a+bi",),
           ("different sign patterns", "fraction coefficients", "nested simplification"),
           ("Forgetting i^2=-1.", "Using the numerator's conjugate instead."),
           R("2.4.md", "Pages 6–7"), R("Quiz_3.md", "Q.3", "quiz"),
           R("Test_1.md", "Q.9", "test"), R("Test_1_Review.md", "Q.9", "review"),
           assessment_refs=("Quiz 3 Q3", "Test 1 Q9", "Test 1 Review Q9")),
        PF("CH2-COMPLEX-COMPONENT-EQUATIONS", "Equations by matching real/imaginary parts",
           ("Solve for real unknowns in a complex-number equality.",),
           ("Both sides are complex expressions with real unknown parameters.",),
           ("real/imaginary components",), (), ("symbolic",),
           ("find all real numbers x,y satisfying",), ("ordered pair / values",),
           ("one side has implicit zero imaginary part", "two unknown coefficients"),
           ("Equating entire complex expressions without matching components.",),
           R("Test_1_Review.md", "Q.10", "review"),
           assessment_refs=("Test 1 Review Q10",)),
    ),
    connections=("Complex roots are generated by the quadratic formula when the discriminant is negative.",),
    source_refs=(R("2.4.md", "Entire lecture"),),
)


SECTION_2_5 = CourseSection(
    id="2.5", chapter=2, title="Other Types of Equations", unit_id="UNIT1",
    summary="Absolute-value, rational-exponent, substitution, and radical equations with candidate checks.",
    learning_objectives=(
        "Split absolute-value equations into valid cases.",
        "Solve rational-exponent equations with domain awareness.",
        "Use substitution for quadratic-type equations.",
        "Solve radical equations and detect extraneous roots.",
    ),
    concepts=("absolute value equation", "rational exponent equation", "substitution", "radical equation", "extraneous solution"),
    vocabulary=("extraneous", "principal root", "case", "substitution"),
    rules=("Squaring both sides can introduce extraneous solutions.", "Even-root expressions impose real-domain restrictions."),
    formulas=(),
    procedures=(
        P("2.5-ABS-EQ", "Solve an absolute-value equation", "Find all real values satisfying |expression|=constant.",
          ("linear equations",),
          ("Isolate the absolute value.", "If the right side is negative, stop with no solution.",
           "Create positive and negative cases.", "Solve both cases.", "Check."),
          R("2.5.md", "Page 1 — Absolute Value Equations")),
        P("2.5-RADICAL-EQ", "Solve a radical equation", "Isolate radicals and remove them while controlling extraneous solutions.",
          ("radical algebra",),
          ("State real-domain restrictions when useful.", "Isolate one radical.", "Raise both sides to the needed power.",
           "Simplify and solve.", "Repeat if another radical remains.", "Check every candidate in the original equation."),
          R("2.5.md", "Pages 6–7"),
          verification_steps=("Substitute every candidate into the original radical equation.",)),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH2-ABS-EQUATIONS", "Absolute-value equations",
           ("Solve all branches of an absolute-value equation.",),
           ("Isolated or isolatable absolute value equals a nonnegative constant.",),
           ("absolute value", "linear equations"), ("2.5-ABS-EQ",), ("symbolic",),
           ("find all real solutions",), ("solution set",),
           ("single absolute value", "scaled/shifted absolute value", "no-solution negative target"),
           ("Forgetting one sign case.",), R("2.5.md", "Page 1"), R("Quiz_3.md", "Q.4", "quiz"),
           assessment_refs=("Quiz 3 Q4",)),
        PF("CH2-RADICAL-EQUATIONS", "Radical equations with extraneous checks",
           ("Solve and validate real solutions.",),
           ("Variable occurs inside a radical and algebraic terms occur outside it.",),
           ("radicals", "domain"), ("2.5-RADICAL-EQ",), ("symbolic",),
           ("find all real solutions", "check them in the original equation"), ("solution set",),
           ("one squaring", "repeated squaring", "odd root", "negative outside radical"),
           ("Failing to isolate the radical first.", "Keeping an extraneous root."),
           R("2.5.md", "Pages 6–7"), R("Test_1.md", "Q.15/Q.16", "test"),
           assessment_refs=("Test 1 Q15", "Test 1 Q16")),
    ),
    connections=("Candidate verification is the same discipline used in rational and logarithmic equations.",),
    source_refs=(R("2.5.md", "Entire lecture"),),
)


SECTION_2_6 = CourseSection(
    id="2.6", chapter=2, title="Inequalities", unit_id="UNIT1",
    summary="Linear, compound, rational, and absolute-value inequalities with interval notation.",
    learning_objectives=(
        "Solve linear and compound inequalities.",
        "Reverse the inequality when multiplying/dividing by a negative.",
        "Translate solution sets into interval notation.",
        "Solve absolute-value and basic rational inequalities.",
    ),
    concepts=("inequality", "interval notation", "compound inequality", "absolute-value inequality", "rational inequality"),
    vocabulary=("strict", "non-strict", "union", "intersection", "endpoint"),
    rules=("Multiplying or dividing an inequality by a negative reverses the inequality symbol.",
           "Denominator zeros are always excluded."),
    formulas=(),
    procedures=(
        P("2.6-LINEAR-INEQ", "Solve a linear/compound inequality", "Isolate the variable and report an interval.",
          ("linear equations",),
          ("Simplify.", "Perform equality-like operations while tracking sign reversals.",
           "For compound inequalities, preserve the conjunction/disjunction.", "Write interval notation."),
          R("2.6.md", "Pages 1–3")),
        P("2.6-ABS-INEQ", "Solve an absolute-value inequality", "Translate absolute-value distance into interval/union conditions.",
          ("absolute value", "linear inequalities"),
          ("Isolate the absolute-value expression.", "Determine whether the inequality means inside/between or outside/two rays.",
           "Solve the resulting inequality/inequalities.", "Write interval notation."),
          R("2.6.md", "Pages 4, 6–7")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH2-COMPOUND-INEQUALITY", "Compound linear inequalities",
           ("Solve and express the solution in interval notation.",),
           ("Two inequality signs or a conjunction of bounds.",),
           ("inequalities", "interval notation"), ("2.6-LINEAR-INEQ",), ("symbolic",),
           ("solve", "write the answer in interval notation"), ("interval",),
           ("double inequality", "intersection form", "negative coefficient sign flip"),
           ("Flipping only one inequality incorrectly.", "Using brackets for strict endpoints."),
           R("2.6.md", "Page 3"), R("Test_1.md", "Q.18", "test"),
           assessment_refs=("Test 1 Q18",)),
        PF("CH2-ABS-INEQUALITY", "Absolute-value inequalities",
           ("Interpret inside/outside distance cases and write intervals.",),
           ("Absolute value is compared to a positive constant.",),
           ("absolute value", "interval notation"), ("2.6-ABS-INEQ",), ("symbolic",),
           ("solve", "find all real numbers satisfying"), ("interval / union",),
           ("less-than inside", "greater-than outside", "nested/scaled absolute value", "double absolute-value bound"),
           ("Using AND when the greater-than case requires OR.",),
           R("2.6.md", "Pages 4, 6–7"), R("Quiz_4.md", "Q.1", "quiz"),
           R("Test_1_Review.md", "Q.11", "review"),
           assessment_refs=("Quiz 4 Q1", "Test 1 Review Q11")),
    ),
    connections=("Interval/sign reasoning is extended to higher-degree and rational inequalities in Section 2.7.",),
    source_refs=(R("2.6.md", "Entire lecture"),),
)


SECTION_2_7 = CourseSection(
    id="2.7", chapter=2, title="More on Inequalities", unit_id="UNIT1",
    summary="Polynomial and rational inequalities solved by factorization, critical points, and sign charts.",
    learning_objectives=(
        "Find critical values from numerator/denominator factors.",
        "Build sign charts across intervals.",
        "Respect excluded values and multiplicities.",
        "Choose endpoint inclusion correctly.",
    ),
    concepts=("polynomial inequality", "rational inequality", "critical point", "sign chart", "multiplicity"),
    vocabulary=("critical value", "sign chart", "zero", "undefined point", "multiplicity"),
    rules=("Numerator zeros may be included for non-strict inequalities; denominator zeros never are.",
           "Cancellation does not restore a value excluded from the original rational expression."),
    formulas=(),
    procedures=(
        P("2.7-SIGN-CHART", "Solve with a sign chart", "Determine where a factored expression has the requested sign.",
          ("factoring", "interval notation"),
          ("Move all terms to one side.", "Factor completely.", "List numerator zeros and denominator exclusions.",
           "Order critical values.", "Determine the sign on each interval.", "Select intervals matching the inequality.",
           "Apply endpoint rules from the original expression."),
          R("2.7.md", "Pages 1–4"),
          verification_steps=("Test one point from each interval when the sign is uncertain.",)),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH2-POLYNOMIAL-INEQUALITY", "Polynomial inequalities",
           ("Solve higher-degree inequalities through factors and interval signs.",),
           ("Polynomial compared to zero after rearrangement.",),
           ("factoring", "sign chart"), ("2.7-SIGN-CHART",), ("symbolic",),
           ("find all real numbers satisfying", "solve"), ("interval / union",),
           ("quadratic", "higher degree", "even multiplicity", "strict/non-strict"),
           ("Solving each factor independently as if it were an equation.",),
           R("2.7.md", "Pages 1–2"), R("Test_1_Review.md", "Q.13", "review"),
           assessment_refs=("Test 1 Review Q13",)),
        PF("CH2-RATIONAL-INEQUALITY", "Rational inequalities by sign chart",
           ("Solve rational inequalities while preserving original exclusions.",),
           ("Factored numerator/denominator define zeros and undefined points.",),
           ("factoring", "restrictions", "sign chart"), ("2.7-SIGN-CHART",), ("symbolic",),
           ("solve", "state the domain, then solve", "write the answer in interval notation"), ("interval / union",),
           ("single denominator factor", "multiple critical points", "cancelled hole", "absolute value in denominator"),
           ("Cross-multiplying by a variable expression without sign analysis.", "Including a denominator zero."),
           R("2.7.md", "Pages 3–4"), R("Quiz_4.md", "Q.2", "quiz"),
           R("Test_1.md", "Q.19/Q.20", "test"), R("Test_1_Review.md", "Q.14", "review"),
           assessment_refs=("Quiz 4 Q2", "Test 1 Q19", "Test 1 Q20", "Test 1 Review Q14")),
    ),
    connections=("The same zeros, multiplicity, and sign-interval reasoning reappears in polynomial graphing in Section 4.2.",),
    source_refs=(R("2.7.md", "Entire lecture"),),
)


# ---------------------------------------------------------------------------
# Unit 2 — Chapter 3
# ---------------------------------------------------------------------------

SECTION_3_1 = CourseSection(
    id="3.1", chapter=3, title="Rectangular Coordinate Systems", unit_id="UNIT2",
    summary="Coordinates, quadrants, distance, midpoint, right-triangle checks, perpendicular bisectors, and line forms.",
    learning_objectives=(
        "Use coordinate formulas exactly.",
        "Verify geometric relationships from distances.",
        "Find midpoints and perpendicular-bisector relationships.",
    ),
    concepts=("coordinate plane", "quadrant", "distance", "midpoint", "perpendicular bisector", "line equation"),
    vocabulary=("origin", "quadrant", "midpoint", "bisector", "distance"),
    rules=("Coordinate formulas must pair corresponding x- and y-coordinates consistently.",),
    formulas=(
        F("3.1-DIST", r"d=\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}", "Distance formula.",
          R("3.1(2).md", "Page 2 — Distance")),
        F("3.1-MID", r"M=\left(\frac{x_1+x_2}{2},\frac{y_1+y_2}{2}\right)", "Midpoint formula.",
          R("3.1(2).md", "Page 5 — Midpoint Formula")),
    ),
    procedures=(
        P("3.1-RIGHT-CHECK", "Verify a right triangle", "Use three side lengths and the Pythagorean relationship.",
          ("distance formula",),
          ("Compute all three squared distances or lengths.", "Identify the largest side.", "Check a^2+b^2=c^2.",
           "State the geometric conclusion."), R("3.1(2).md", "Page 4 — Checking a Right Triangle")),
        P("3.1-PERP-BISECTOR", "Check/construct a perpendicular bisector", "Use midpoint and equal-distance/perpendicular properties.",
          ("midpoint", "distance", "slope"),
          ("Find the segment midpoint.", "Find the segment slope when needed.", "Use the negative reciprocal for a perpendicular line.",
           "Alternatively compare distances from a candidate point to both endpoints.", "State whether the condition is satisfied."),
          R("3.1(2).md", "Pages 7–8")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH3-DISTANCE-MIDPOINT", "Distance and midpoint",
           ("Compute exact coordinate distances/midpoints and use them in reasoning.",),
           ("Two points are given in the plane.",),
           ("coordinate geometry",), (), ("symbolic", "context"),
           ("find", "write the general formula", "use the formula"), ("radical distance", "ordered pair"),
           ("formula recall + computation", "missing endpoint reversal", "application distance"),
           ("Mixing x and y coordinates.", "Averaging differences instead of coordinates."),
           R("3.1(2).md", "Pages 2–6"), R("Quiz_4.md", "Q.3", "quiz"),
           assessment_refs=("Quiz 4 Q3",)),
        PF("CH3-PERP-BISECTOR", "Perpendicular bisector verification",
           ("Determine whether a point lies on a perpendicular bisector and show work.",),
           ("Candidate point and segment endpoints are given.",),
           ("distance", "midpoint", "perpendicularity"), ("3.1-PERP-BISECTOR",),
           ("symbolic", "verbal"), ("determine, with working, whether",), ("yes/no with supporting calculations",),
           ("equal-distance method", "slope/midpoint method", "construct equation"),
           ("Giving only a yes/no answer.",),
           R("3.1(2).md", "Pages 7–8"), R("Quiz_4.md", "Q.4", "quiz"),
           assessment_refs=("Quiz 4 Q4",)),
    ),
    connections=("Coordinate geometry supports graphing equations, circles, and line problems in Sections 3.2–3.3.",),
    source_refs=(R("3.1(2).md", "Entire lecture"),),
)


SECTION_3_2 = CourseSection(
    id="3.2", chapter=3, title="Graphs of Equations", unit_id="UNIT2",
    summary="Graphing equations, intercepts, symmetry, parabolas, circles, and semicircles.",
    learning_objectives=(
        "Generate points and sketch graphs of equations.",
        "Find x- and y-intercepts algebraically.",
        "Test symmetry.",
        "Write and analyze circle equations, including completing the square.",
    ),
    concepts=("graph", "intercept", "symmetry", "parabola", "circle", "semicircle", "vertical line test"),
    vocabulary=("x-intercept", "y-intercept", "symmetry", "center", "radius", "semicircle"),
    rules=("Set y=0 for x-intercepts and x=0 for y-intercepts.", "Use both signs when solving a circle equation unless a half is specified."),
    formulas=(
        F("3.2-CIRCLE", r"(x-h)^2+(y-k)^2=r^2", "Standard circle equation.",
          R("3.2.md", "Page 7 — Equation of a Circle")),
    ),
    procedures=(
        P("3.2-CIRCLE-GENERAL", "Convert a general circle equation to standard form",
          "Find center and radius by completing the square in x and y.",
          ("completing the square",),
          ("Normalize x^2 and y^2 coefficients if necessary.", "Group x-terms and y-terms.",
           "Complete each square.", "Balance constants.", "Read center and radius from standard form."),
          R("3.2.md", "Page 9 — Center and Radius by Completing the Square"),
          verification_steps=("Expand standard form to recover the original equation.",)),
        P("3.2-INTERCEPTS", "Find intercepts", "Find all coordinate-axis intersections.",
          ("equation solving",),
          ("For x-intercepts set y=0 and solve for x.", "For y-intercepts set x=0 and solve for y.",
           "Report ordered pairs."), R("3.2.md", "Page 3 — Intercepts")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH3-CIRCLE-CENTER-RADIUS", "Circle equation, center, and radius",
           ("Write a circle equation or recover center/radius from one.",),
           ("Center/radius or a general second-degree circle equation is provided.",),
           ("circle", "completing the square"), ("3.2-CIRCLE-GENERAL",), ("symbolic",),
           ("write the general equation", "find its center and radius"), ("equation + center/radius",),
           ("given center and point", "general form requires completing squares", "parameterized center/radius"),
           ("Reading signs of center incorrectly.", "Completing only one variable square."),
           R("3.2.md", "Pages 7–9"), R("Quiz_5.md", "Q.1", "quiz"),
           assessment_refs=("Quiz 5 Q1",)),
        PF("CH3-CIRCLE-INTERCEPTS", "Circle intercepts",
           ("Find all axis intercepts from circle data/equation.",),
           ("Circle center/radius or equation is given and an axis intersection is requested.",),
           ("circle", "quadratics"), ("3.2-INTERCEPTS",), ("symbolic",),
           ("find all x-intercepts",), ("ordered pairs",),
           ("tangent one-intercept case", "two-intercept case", "no-real-intercept case"),
           ("Forgetting the fixed coordinate is zero.",),
           R("3.2.md", "Circle material"), R("Quiz_6.md", "Q.2", "quiz"),
           assessment_refs=("Quiz 6 Q2",)),
        PF("CH3-GRAPH-SYMMETRY", "Equation symmetry and graph interpretation",
           ("Determine symmetry or interpret graph shape/intercepts.",),
           ("Equation remains unchanged under sign substitutions or graph points show a pattern.",),
           ("symmetry", "graphing"), (), ("symbolic", "graph"),
           ("sketch", "determine symmetry", "find intercepts"), ("graph / symmetry statement / points",),
           ("x-axis", "y-axis", "origin", "sideways parabola/semicircle"),
           ("Testing only x when origin symmetry requires x and y.",),
           R("3.2.md", "Pages 1–6, 10–11")),
    ),
    connections=("Circle completion uses Section 2.3; graph interpretation is extended to functions in Section 3.4.",),
    source_refs=(R("3.2.md", "Entire lecture"),),
)


SECTION_3_3 = CourseSection(
    id="3.3", chapter=3, title="Lines", unit_id="UNIT2",
    summary="Slope, horizontal/vertical lines, point-slope form, and parallel/perpendicular lines.",
    learning_objectives=(
        "Compute slope with consistent coordinate ordering.",
        "Write line equations from points/slopes.",
        "Construct parallel and perpendicular lines.",
    ),
    concepts=("slope", "point-slope form", "parallel", "perpendicular", "horizontal line", "vertical line"),
    vocabulary=("slope", "undefined slope", "negative reciprocal", "point-slope"),
    rules=("Use the same point order in numerator and denominator.", "Parallel nonvertical lines have equal slope.",
           "Perpendicular nonvertical lines have slopes whose product is -1."),
    formulas=(
        F("3.3-SLOPE", r"m=\frac{y_2-y_1}{x_2-x_1}", "Slope between two distinct nonvertical points.",
          R("3.3.md", "Page 1 — Slope")),
        F("3.3-POINT-SLOPE", r"y-y_1=m(x-x_1)", "Point-slope line form.",
          R("3.3.md", "Page 4 — Point-Slope Form")),
        F("3.3-PERP", r"m_1m_2=-1", "Perpendicular slope relationship.",
          R("3.3.md", "Page 7 — Parallel and Perpendicular Lines")),
    ),
    procedures=(
        P("3.3-LINE", "Write a line equation", "Construct the requested line form from geometric information.",
          ("slope",),
          ("Determine slope from the given information.", "Use point-slope form with a known point.",
           "Convert to the requested form.", "Check the point and slope."),
          R("3.3.md", "Pages 4–9"),
          decision_points=("Given two points, parallel line, perpendicular line, or axis-parallel line?",)),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH3-LINE-EQUATION", "Line through points / parallel / perpendicular",
           ("Build a line equation from coordinate constraints.",),
           ("A point plus another point or a relation to a known line.",),
           ("slope", "line forms"), ("3.3-LINE",), ("symbolic", "context"),
           ("find the line", "what is the slope-intercept form"), ("equation",),
           ("two-point", "parallel", "perpendicular", "horizontal/vertical"),
           ("Taking the reciprocal but not changing sign for a perpendicular line.", "Converting to slope-intercept incorrectly."),
           R("3.3.md", "Pages 5–9"), R("Quiz_5.md", "Q.2", "quiz"),
           assessment_refs=("Quiz 5 Q2",)),
    ),
    connections=("Line slope is used for secants/difference quotient and for modeling linear data.",),
    source_refs=(R("3.3.md", "Entire lecture"),),
)


SECTION_3_4 = CourseSection(
    id="3.4", chapter=3, title="Functions", unit_id="UNIT2",
    summary="Function definition, domain/range, graph behavior, open/closed endpoints, and difference quotient.",
    learning_objectives=(
        "Determine domain and range symbolically and graphically.",
        "Read increasing, decreasing, and constant intervals.",
        "Compute and simplify difference quotients.",
    ),
    concepts=("function", "domain", "range", "increasing", "decreasing", "constant", "difference quotient"),
    vocabulary=("domain", "range", "input", "output", "open endpoint", "closed endpoint", "difference quotient"),
    rules=("Square-root radicands must be nonnegative for real-valued functions.",
           "Denominators must be nonzero.", "Graph-domain uses horizontal spread; graph-range uses vertical spread."),
    formulas=(
        F("3.4-DQ", r"\frac{f(x+h)-f(x)}{h}", "Difference quotient/secant slope form.",
          R("3.4.md", "Page 9 — Difference Quotient"), conditions=("h != 0",)),
    ),
    procedures=(
        P("3.4-DOMAIN-FORMULA", "Find domain from a formula", "Combine all algebraic restrictions.",
          ("inequalities", "interval notation"),
          ("List each square-root, denominator, and other source restriction.", "Solve each restriction.",
           "Intersect the allowed sets.", "Write interval notation."),
          R("3.4.md", "Page 3 — Domain and Range")),
        P("3.4-DQ-PROC", "Compute a difference quotient", "Substitute x+h and simplify the quotient.",
          ("function notation", "expansion", "factoring"),
          ("Compute f(x+h) carefully.", "Form f(x+h)-f(x).", "Expand/combine.", "Factor h.",
           "Cancel h under h!=0.", "Simplify."),
          R("3.4.md", "Pages 9–10")),
    ),
    worked_examples=(
        E("3.4-DQ-EX", r"f(x)=x^2+6x-4,\quad\frac{f(x+h)-f(x)}h",
          (r"f(x+h)=(x+h)^2+6(x+h)-4", r"\frac{2xh+h^2+6h}{h}", r"2x+h+6"),
          r"2x+h+6", R("3.4.md", "Page 10 — Difference Quotient Example")),
    ),
    problem_families=(
        PF("CH3-DOMAIN-FORMULA", "Domain from symbolic function",
           ("Combine radical and denominator restrictions correctly.",),
           ("Formula contains denominator, even root, or both.",),
           ("domain", "interval notation"), ("3.4-DOMAIN-FORMULA",), ("symbolic",),
           ("find the domain", "explain all restrictions clearly"), ("interval / union",),
           ("root only", "denominator only", "root + denominator", "simplifiable factor with original restriction"),
           ("Using the simplified expression's domain instead of the original function's.",),
           R("3.4.md", "Page 3"), R("Quiz_5.md", "Q.3", "quiz"),
           assessment_refs=("Quiz 5 Q3", "Quiz 6 Q3")),
        PF("CH3-GRAPH-DOMAIN-RANGE-BEHAVIOR", "Domain/range and monotonicity from graphs",
           ("Read endpoints, unions, range, and increasing/decreasing/constant intervals.",),
           ("Piecewise/disconnected graph with open and closed endpoints.",),
           ("graph interpretation", "interval notation"), (), ("graph", "multipart"),
           ("state", "find", "write all answers in interval notation"), ("multiple intervals",),
           ("jump discontinuity", "disconnected domain", "overlapping range pieces", "constant segment"),
           ("Treating open endpoints as included.", "Confusing horizontal and vertical spread."),
           R("3.4.md", "Pages 4–8"), R("Quiz_5.md", "Q.4", "quiz"),
           assessment_refs=("Quiz 5 Q4",)),
        PF("CH3-DIFFERENCE-QUOTIENT", "Difference quotient",
           ("Compute and simplify a difference quotient for different function structures.",),
           ("Prompt explicitly gives [f(x+h)-f(x)]/h or asks for average change.",),
           ("function notation", "algebra"), ("3.4-DQ-PROC",), ("symbolic",),
           ("find", "compute", "simplify"), ("expression",),
           ("polynomial", "rational function", "radical requiring rationalization", "parameterized input"),
           ("Substituting x+h only for some x occurrences.", "Canceling h before factoring."),
           R("3.4.md", "Pages 9–10"), R("Test_2_Review.pdf", "difference quotient item", "review"),
           assessment_refs=("Test 2 Review difference quotient",)),
    ),
    connections=("Function-domain rules control function operations/composition in 3.7 and inverse/log domains in Chapter 5.",),
    source_refs=(R("3.4.md", "Entire lecture"),),
)


SECTION_3_5 = CourseSection(
    id="3.5", chapter=3, title="Function Properties, Symmetry, and Piecewise Behavior", unit_id="UNIT2",
    summary=(
        "Source-supported review/final material on even/odd/neither classification, piecewise-function "
        "interpretation, graph behavior, and interval-based function analysis."
    ),
    learning_objectives=(
        "Classify functions as even, odd, or neither from formulas or graphs.",
        "Evaluate and graph piecewise-defined functions with correct endpoint behavior.",
        "Connect algebraic symmetry tests to geometric graph symmetry.",
        "Read increasing, decreasing, and constant behavior from piecewise or ordinary graphs.",
    ),
    concepts=("even function", "odd function", "piecewise function", "symmetry", "graph behavior", "interval notation"),
    vocabulary=("even", "odd", "neither", "piecewise", "endpoint", "symmetric"),
    rules=(
        r"A function is even when f(-x)=f(x) on a symmetric domain.",
        r"A function is odd when f(-x)=-f(x) on a symmetric domain.",
        "Piecewise formulas apply only on their stated intervals; open and closed endpoints must be preserved.",
    ),
    formulas=(
        F("3.5-EVEN", r"f(-x)=f(x)", "Algebraic test for an even function.",
          R("Test_2_Review.pdf", "even/odd function review item", "review")),
        F("3.5-ODD", r"f(-x)=-f(x)", "Algebraic test for an odd function.",
          R("Test_2_Review.pdf", "even/odd function review item", "review")),
    ),
    procedures=(
        P("3.5-PARITY", "Classify function parity", "Determine whether a function is even, odd, or neither.",
          ("function notation", "substitution"),
          ("Compute f(-x).", "Simplify fully.", "Compare with f(x) and -f(x).",
           "Confirm the domain is compatible with the claimed symmetry.", "State even, odd, or neither."),
          R("Test_2_Review.pdf", "even/odd function review item", "review")),
        P("3.5-PIECEWISE", "Analyze a piecewise function", "Evaluate or graph the correct rule on each interval.",
          ("inequalities", "function notation", "graph endpoints"),
          ("Identify which condition contains the requested input.", "Use only that rule.",
           "For graphing, draw each rule only on its stated interval.", "Mark open/closed endpoints correctly.",
           "Read requested domain/range/behavior from the completed graph."),
          R("Test_2_Review.pdf", "piecewise graph review item", "review")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH3-FUNCTION-PARITY", "Even, odd, or neither",
           ("Classify a function from algebraic or graphical symmetry evidence.",),
           ("Prompt asks even/odd/neither or supplies a graph/formula with symmetry clues.",),
           ("function notation", "symmetry"), ("3.5-PARITY",), ("symbolic", "graph", "classification"),
           ("determine", "classify", "is the function"), ("even/odd/neither",),
           ("algebraic f(-x) test", "graph symmetry", "domain breaks otherwise apparent symmetry"),
           ("Checking only whether powers look even/odd without simplifying f(-x).", "Ignoring a nonsymmetric domain."),
           R("Test_2_Review.pdf", "even/odd function review item", "review"),
           R("Version 1 (Without Solutions).pdf", "Chapter 3 function-property item", "final"),
           assessment_refs=("Test 2 Review", "Departmental practice final")),
        PF("CH3-PIECEWISE-FUNCTION", "Piecewise evaluation and graph",
           ("Select the correct branch, evaluate it, or graph all branches with endpoint control.",),
           ("Function is defined by two or more rules with interval conditions.",),
           ("piecewise functions", "inequalities", "graph endpoints"), ("3.5-PIECEWISE",),
           ("symbolic", "graph", "multipart"),
           ("evaluate", "graph", "state the domain", "state the range"),
           ("number", "graph", "interval / union"),
           ("evaluate at interior point", "evaluate at breakpoint", "graph with open/closed endpoints", "read domain/range"),
           ("Using the wrong branch.", "Treating an open endpoint as included.", "Extending a branch beyond its interval."),
           R("Test_2_Review.pdf", "piecewise graph review item", "review"),
           R("Version 2 (Without Solutions).pdf", "Chapter 3 function-property item", "final"),
           assessment_refs=("Test 2 Review", "Departmental practice final")),
    ),
    connections=(
        "Parity connects algebraic substitution to graph symmetry.",
        "Piecewise interval behavior extends the domain/range and monotonicity work from Section 3.4.",
        "Graph-reading skills feed quadratic and polynomial graph analysis.",
    ),
    source_refs=(
        R("Test_2_Review.pdf", "function-properties review items", "review"),
        R("Version 1 (Without Solutions).pdf", "Chapter 3 final-review coverage", "final"),
    ),
)


SECTION_3_6 = CourseSection(
    id="3.6", chapter=3, title="Quadratic Functions, Vertex Form, and Extrema", unit_id="UNIT2",
    summary=(
        "Quadratic-function review emphasizing standard/factored/vertex representations, completing the square, "
        "vertex and axis of symmetry, maximum/minimum values, intercepts, and contextual optimization."
    ),
    learning_objectives=(
        "Move among standard, factored, and vertex forms when source-supported.",
        "Find a quadratic's vertex and axis of symmetry.",
        "Determine whether the vertex gives a maximum or minimum.",
        "Use quadratic structure to answer graph and application questions.",
    ),
    concepts=("quadratic function", "vertex", "axis of symmetry", "maximum", "minimum", "vertex form", "intercepts"),
    vocabulary=("vertex", "axis of symmetry", "maximum", "minimum", "opens upward", "opens downward"),
    rules=(
        "For a>0 the parabola opens upward and its vertex is a minimum; for a<0 it opens downward and its vertex is a maximum.",
        "The x-coordinate of the vertex is -b/(2a), and completing the square produces the same vertex information.",
    ),
    formulas=(
        F("3.6-VERTEX-X", r"x_v=-\frac{b}{2a}", "x-coordinate of the vertex for ax^2+bx+c.",
          R("Test_2_Review.pdf", "quadratic maximum/minimum review item", "review")),
        F("3.6-VERTEX-FORM", r"f(x)=a(x-h)^2+k", "Vertex form with vertex (h,k).",
          R("Quiz_6.md", "Q.1", "quiz"), R("Completing_the_Square.md", "General Formula", "supplement")),
    ),
    procedures=(
        P("3.6-VERTEX", "Find and interpret a quadratic vertex", "Determine the vertex, axis, and extremum.",
          ("quadratic algebra", "function evaluation"),
          ("Identify a, b, c or rewrite into vertex form.", "Find h=-b/(2a) or read h from vertex form.",
           "Compute k=f(h) if necessary.", "State the axis x=h.", "Use the sign of a to classify maximum/minimum."),
          R("Test_2_Review.pdf", "quadratic maximum/minimum review item", "review"),
          verification_steps=("Substitute the vertex x-coordinate into the original quadratic.",)),
        P("3.6-QUAD-APPLICATION", "Solve a quadratic optimization/application problem", "Translate a context and interpret the vertex.",
          ("quadratic modeling", "vertex"),
          ("Define the input/output quantities and units.", "Write or identify the quadratic model.",
           "Find the vertex.", "Decide whether the context asks for the input, maximum/minimum output, intercept, or interval.",
           "Interpret the result with units and reject context-inappropriate values."),
          R("Test_2_Review.pdf", "quadratic application/maximum-minimum item", "review")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH3-QUADRATIC-VERTEX", "Quadratic vertex, axis, and extrema",
           ("Find and interpret vertex information from multiple quadratic representations.",),
           ("Quadratic is given in standard, factored, or vertex form; prompt asks vertex/axis/max/min.",),
           ("quadratic functions", "vertex", "completing the square"), ("3.6-VERTEX",),
           ("symbolic", "graph", "multipart"),
           ("find", "determine", "write in vertex form", "state the maximum", "state the minimum"),
           ("vertex", "axis + extremum", "vertex-form expression"),
           ("standard form via -b/2a", "completed-square/vertex form", "graph feature identification", "factored form then vertex"),
           ("Using -b/a instead of -b/(2a).", "Reading h with the wrong sign from (x-h)^2.",
            "Calling a minimum a maximum when a>0."),
           R("Test_2_Review.pdf", "quadratic maximum/minimum review item", "review"),
           R("Quiz_6.md", "Q.1", "quiz"),
           assessment_refs=("Quiz 6 Q1", "Test 2 Review")),
        PF("CH3-QUADRATIC-APPLICATION", "Quadratic application and optimization",
           ("Use the vertex or zeros of a quadratic model to answer a contextual question.",),
           ("Context describes height, area, revenue, distance, or another quantity with a quadratic model.",),
           ("quadratic modeling", "vertex", "intercepts"), ("3.6-QUAD-APPLICATION",),
           ("context", "multipart"),
           ("find the maximum", "find the minimum", "when", "how high", "determine"),
           ("quantity with units", "time/input + extremum output"),
           ("projectile maximum", "area optimization", "revenue/geometry model", "find intercept then interpret"),
           ("Reporting the vertex coordinates without interpreting which coordinate answers the question.",
            "Keeping a negative time/length that is algebraically valid but contextually invalid."),
           R("Test_2_Review.pdf", "quadratic application/maximum-minimum item", "review"),
           R("Version 3 (Without Solutions).pdf", "quadratic application final-review item", "final"),
           assessment_refs=("Test 2 Review", "Departmental practice final")),
    ),
    connections=(
        "Completing the square links Chapter 2 equation methods to quadratic graph geometry.",
        "Quadratic extrema prepare the learner for polynomial graph interpretation and modeling.",
    ),
    source_refs=(
        R("Test_2_Review.pdf", "quadratic-function review items", "review"),
        R("Quiz_6.md", "Q.1", "quiz"),
        R("Version 3 (Without Solutions).pdf", "quadratic final-review item", "final"),
    ),
)


SECTION_3_7 = CourseSection(
    id="3.7", chapter=3, title="Operations on Functions and Composite Functions", unit_id="UNIT2",
    summary="Function arithmetic, domain intersections, quotients, composition, and composite-domain restrictions.",
    learning_objectives=(
        "Compute function sums/differences/products/quotients.",
        "Determine domains after function operations.",
        "Compute compositions in both orders.",
        "Carry inner-function domain restrictions into compositions.",
    ),
    concepts=("function operations", "composition", "domain intersection", "inner function"),
    vocabulary=("composition", "composite", "inner function", "outer function"),
    rules=("For f/g, the domain must lie in both domains and also satisfy g(x) != 0.",
           "For f∘g, x must be in the domain of g and g(x) must lie in the domain of f."),
    formulas=(
        F("3.7-COMP", r"(f\circ g)(x)=f(g(x))", "Function composition.",
          R("3.7.md", "Composite Functions / Compositions")),
    ),
    procedures=(
        P("3.7-COMPOSE", "Compose functions and determine domain", "Apply inner then outer function with all restrictions.",
          ("function notation", "domain"),
          ("Identify inner and outer functions.", "Substitute the entire inner expression into the outer rule.",
           "Simplify.", "Impose the inner domain.", "Impose any outer restriction on the inner output.",
           "Write the final domain."), R("3.7.md", "Composite Functions / Compositions")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH3-FUNCTION-COMPOSITION", "Composition with domain",
           ("Compute f∘g and/or g∘f and their domains.",),
           ("Two function definitions followed by composition notation.",),
           ("functions", "domain"), ("3.7-COMPOSE",), ("symbolic", "table", "context", "multipart"),
           ("compute", "find", "state the domain"), ("expression + domain", "value"),
           ("polynomial/radical order", "rational outer restriction", "table composition", "both composition orders"),
           ("Doing the outer function first.", "Using only the simplified expression to determine domain."),
           R("3.7.md", "Composite Functions"), R("Quiz_6.md", "Q.4", "quiz"),
           R("Activity_4.md", "Q.1–Q.2", "activity"), R("Test_3_Review_Human_Readable_Complete.md", "Q.1", "review"),
           assessment_refs=("Quiz 6 Q4", "Activity 4 Q1-Q2", "Test 3 Review Q1")),
        PF("CH3-FUNCTION-QUOTIENT-DOMAIN", "Function quotient with inherited restrictions",
           ("Compute f/g while retaining original domain restrictions.",),
           ("Functions are separately defined and then divided.",),
           ("function operations", "domain"), (), ("symbolic",),
           ("state the domain and simplify"), ("expression + domain",),
           ("cancellation removes visible denominator factor but not original exclusion", "root + denominator intersection"),
           ("Restoring a canceled excluded value.",),
           R("3.7.md", "Division"), R("Quiz_6.md", "Q.3", "quiz"),
           assessment_refs=("Quiz 6 Q3",)),
    ),
    connections=("Composition is prerequisite for inverse-function verification and several Test 3 review items.",),
    source_refs=(R("3.7.md", "Entire lecture"),),
)


# ---------------------------------------------------------------------------
# Unit 3 — Chapters 4 and 5
# ---------------------------------------------------------------------------

SECTION_4_1 = CourseSection(
    id="4.1", chapter=4, title="Properties of Polynomial Division", unit_id="UNIT3",
    summary="Division algorithm, long division, remainders, factor/root theorem, and constructing polynomials from roots.",
    learning_objectives=(
        "Perform polynomial long division and identify quotient/remainder.",
        "Use f(c) as the remainder for division by x-c.",
        "Use the factor/root relationship.",
        "Construct a polynomial from prescribed roots and an additional condition.",
    ),
    concepts=("polynomial division", "quotient", "remainder", "factor theorem", "remainder theorem", "roots"),
    vocabulary=("dividend", "divisor", "quotient", "remainder", "root", "factor"),
    rules=("The remainder degree must be lower than the divisor degree.",
           "c is a root of f exactly when x-c divides f."),
    formulas=(
        F("4.1-DIV-ALG", r"f(x)=d(x)q(x)+r(x)", "Polynomial division algorithm.",
          R("4.1.md", "Division Algorithm for Polynomials")),
        F("4.1-REMAINDER", r"f(x)=(x-c)q(x)+f(c)", "Remainder theorem for a linear divisor.",
          R("4.1.md", "Division by (x-c)")),
    ),
    procedures=(
        P("4.1-LONG-DIV", "Polynomial long division", "Find quotient and remainder.",
          ("polynomial operations",),
          ("Write polynomials in descending powers including zero placeholders.", "Divide leading terms.",
           "Multiply divisor by the quotient term.", "Subtract.", "Bring down next term and repeat.",
           "Stop when remainder degree is smaller than divisor degree."),
          R("4.1.md", "Polynomial Long Division Example"),
          verification_steps=("Verify dividend = divisor*quotient + remainder.",)),
        P("4.1-BUILD-ROOTS", "Build a polynomial from roots", "Create factored polynomial satisfying roots/scale conditions.",
          ("factor/root relationship",),
          ("Convert each root c to factor x-c.", "Multiply factors with leading constant A.",
           "Use any supplied value f(k) to solve for A.", "Return factored or expanded form as requested."),
          R("4.1.md", "Building a Polynomial from Roots / Polynomial with a Given Value")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH4-POLYNOMIAL-DIVISION", "Polynomial quotient and remainder",
           ("Compute quotient/remainder and verify division.",),
           ("Polynomial divided by another polynomial.",),
           ("polynomial operations",), ("4.1-LONG-DIV",), ("symbolic",),
           ("find the quotient and remainder", "divide"), ("quotient + remainder / identity",),
           ("linear divisor", "quadratic divisor", "larger-degree divisor", "exact division"),
           ("Omitting zero-power placeholders.", "Sign errors during subtraction."),
           R("4.1.md", "Long Division / Linear Divisor Examples"), R("Test_3_Review.md", "polynomial division item", "review")),
        PF("CH4-REMAINDER-FACTOR", "Remainder and factor theorem reasoning",
           ("Use evaluation to determine a remainder or prove divisibility.",),
           ("Divisor has form x-c; prompt may forbid long division.",),
           ("roots", "evaluation"), (), ("symbolic",),
           ("find the remainder", "show ... divides ... without long division"), ("number / proof statement",),
           ("remainder nonzero", "known root", "parameter chosen so remainder=0"),
           ("Evaluating at c with the wrong sign from x-c.",),
           R("4.1.md", "Remainder Example / Factor-Root Relationship"), R("Test_3_Review.md", "factor theorem item", "review")),
        PF("CH4-BUILD-POLYNOMIAL", "Construct polynomial from roots",
           ("Translate roots into factors and solve for a scale factor if needed.",),
           ("A degree and list of roots are specified, sometimes with f(k)=value.",),
           ("roots", "factored form"), ("4.1-BUILD-ROOTS",), ("symbolic",),
           ("find a polynomial",), ("polynomial equation/expression",),
           ("monic", "unknown scale A", "repeated roots"),
           ("Using x+c for root c instead of x-c.",),
           R("4.1.md", "Building a Polynomial from Roots")),
    ),
    connections=("Factor/root and division ideas support polynomial graphing and zero analysis in Section 4.2.",),
    source_refs=(R("4.1.md", "Entire lecture"),),
)


SECTION_4_2 = CourseSection(
    id="4.2", chapter=4, title="Polynomials of Degree Greater Than 2", unit_id="UNIT3",
    summary="Intermediate Value Theorem, zeros, multiplicity, sign intervals, and source-faithful polynomial graphing.",
    learning_objectives=(
        "Use opposite signs to justify a root in an interval.",
        "Factor a polynomial to find zeros and multiplicities.",
        "Determine where a polynomial is positive/negative.",
        "Sketch a graph from zeros, multiplicity, and end behavior.",
    ),
    concepts=("Intermediate Value Theorem", "root", "multiplicity", "sign interval", "end behavior", "polynomial graph"),
    vocabulary=("intermediate value", "root", "zero", "multiplicity", "end behavior"),
    rules=("An odd-multiplicity real zero changes sign/crosses; an even-multiplicity zero may touch without changing sign.",
           "For a continuous polynomial, opposite signs at endpoints guarantee at least one root between them."),
    formulas=(),
    procedures=(
        P("4.2-GRAPH-POLY", "Analyze and graph a factored polynomial", "Use algebraic structure to determine sign and graph behavior.",
          ("factoring", "sign charts"),
          ("Factor completely.", "List real zeros and multiplicities.", "Order zeros and create intervals.",
           "Determine signs on intervals.", "Determine end behavior from degree/leading coefficient.",
           "Plot intercept behavior and sketch."),
          R("4.2.md", "Graphing Polynomials")),
        P("4.2-IVT", "Apply the Intermediate Value Theorem", "Show a polynomial assumes a value/root in an interval.",
          ("function evaluation",),
          ("Evaluate f(a) and f(b).", "Check that the target value lies between them (or signs are opposite for root existence).",
           "State the IVT conclusion on (a,b)."), R("4.2.md", "Intermediate Value Theorem")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH4-POLY-SIGN-GRAPH", "Polynomial sign intervals and graph",
           ("Find positive/negative intervals and sketch a polynomial graph.",),
           ("Polynomial is factorable or roots are obtainable.",),
           ("factoring", "sign charts", "multiplicity"), ("4.2-GRAPH-POLY",),
           ("symbolic", "graph", "multipart"),
           ("find the intervals", "then graph", "sketch"), ("interval unions + graph",),
           ("all simple roots", "even multiplicity touch", "degree/leading-sign changes", "partially factored form"),
           ("Assuming every zero crosses the axis.", "Ignoring multiplicity/end behavior."),
           R("4.2.md", "Graphing Polynomials Examples 1–2")),
        PF("CH4-IVT", "Intermediate Value Theorem existence reasoning",
           ("Demonstrate existence of a root/value without solving the polynomial.",),
           ("Polynomial values at two endpoints straddle zero/target.",),
           ("continuity", "evaluation"), ("4.2-IVT",), ("symbolic", "verbal"),
           ("show that a root exists", "show there exists"), ("justification statement",),
           ("root target 0", "nonzero target value", "different endpoint intervals"),
           ("Claiming an exact root from sign change alone.",),
           R("4.2.md", "IVT and Example")),
    ),
    connections=("Polynomial sign charts reuse Section 2.7 inequality reasoning.",),
    source_refs=(R("4.2.md", "Entire lecture"),),
)


SECTION_5_1 = CourseSection(
    id="5.1", chapter=5, title="Inverse Functions", unit_id="UNIT3",
    summary="One-to-one tests, inverse functions, inverse verification, algebraic inversion, domain/range exchange, and restricted quadratics.",
    learning_objectives=(
        "Determine whether a function is one-to-one.",
        "Verify inverse pairs by composition.",
        "Find an inverse algebraically.",
        "Use domain/range exchange to reason about inverses.",
    ),
    concepts=("one-to-one", "inverse", "horizontal line test", "domain/range exchange", "reflection across y=x"),
    vocabulary=("one-to-one", "inverse", "horizontal line test"),
    rules=("A function must be one-to-one on its domain to have an inverse function.",
           "Domain(f^-1)=Range(f) and Range(f^-1)=Domain(f)."),
    formulas=(
        F("5.1-INVERSE-COMP", r"(f\circ f^{-1})(x)=x,\quad(f^{-1}\circ f)(x)=x",
          "Inverse composition identities.", R("5.1.md", "Inverses")),
    ),
    procedures=(
        P("5.1-FIND-INVERSE", "Find an inverse algebraically", "Solve the swapped relation for the new output.",
          ("equation solving",),
          ("Write y=f(x).", "Swap x and y.", "Solve for y.", "Rename y as f^{-1}(x).",
           "State domain restrictions when they matter.", "Optionally verify by composition."),
          R("5.1.md", "Finding an Inverse Algebraically")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH5-INVERSE-ALGEBRA", "Find/verify inverse functions",
           ("Find inverses and prove inverse relationships.",),
           ("One-to-one function or candidate inverse is given.",),
           ("inverse functions", "composition"), ("5.1-FIND-INVERSE",), ("symbolic", "graph"),
           ("find the inverse", "verify", "determine whether one-to-one"), ("function rule / verification",),
           ("linear", "rational", "restricted quadratic", "graph horizontal-line test"),
           ("Forgetting to swap x and y.", "Choosing both square-root signs when the original domain selects one branch."),
           R("5.1.md", "Entire lecture")),
        PF("CH5-INVERSE-DOMAIN-RANGE", "Domain/range through inverse reasoning",
           ("Find rational-function domain/range using inverse relationships.",),
           ("One-to-one rational function and hint that range(f)=domain(f^-1).",),
           ("domain", "inverse", "rational restriction"), ("5.1-FIND-INVERSE",), ("symbolic", "multipart"),
           ("find its domain", "find its range"), ("domain + range",),
           ("rational linear-over-linear", "restricted input/output", "inverse domain exclusion"),
           ("Assuming range equals domain.", "Forgetting the inverse denominator restriction."),
           R("5.1.md", "Inverses"), R("Test_3_Review_Human_Readable_Complete.md", "Q.3", "review"),
           assessment_refs=("Test 3 Review Q3",)),
    ),
    connections=("Inverse functions provide the conceptual definition of logarithms in Section 5.4.",),
    source_refs=(R("5.1.md", "Entire lecture"),),
)


SECTION_5_2 = CourseSection(
    id="5.2", chapter=5, title="Exponential Functions", unit_id="UNIT3",
    summary="Growth/decay behavior, equal-base equations, graphs, constructing exponentials, compound interest, and exponential models.",
    learning_objectives=(
        "Distinguish growth from decay by the base.",
        "Solve equal-base exponential equations using one-to-one behavior.",
        "Construct an exponential rule from asymptote/intercepts or data.",
        "Build exponential models from contextual data.",
    ),
    concepts=("exponential function", "growth", "decay", "horizontal asymptote", "model", "compound interest"),
    vocabulary=("base", "growth", "decay", "asymptote", "principal", "compounding"),
    rules=("For b>0, b!=1, b^x is one-to-one.", "Exponential bases are positive."),
    formulas=(
        F("5.2-EXP", r"f(x)=b^x,\quad b>0,\ b\ne1", "Basic exponential function.",
          R("5.2.md", "Definition")),
        F("5.2-COMPOUND", r"A=P\left(1+\frac rn\right)^{nt}", "Discrete compound-interest model.",
          R("5.2.md", "Compound Interest")),
    ),
    procedures=(
        P("5.2-EXP-MODEL", "Build an exponential model", "Determine parameters from initial/known values.",
          ("equation solving", "roots"),
          ("Choose a time origin.", "Use initial data to determine a.", "Use a second data point to solve for b.",
           "Write the model.", "Evaluate/predict at the requested time.", "Interpret units."),
          R("5.2.md", "Minimum-Wage Exponential Model")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH5-EQUAL-BASE", "Equal-base exponential equations",
           ("Use one-to-one behavior to equate exponents.",),
           ("Same positive nonunit base appears on both sides.",),
           ("exponents", "one-to-one"), (), ("symbolic",),
           ("find all real solutions", "solve"), ("solution set / number",),
           ("linear exponents", "quadratic exponents", "base rewriting required"),
           ("Equating exponents when bases are not actually equal.",),
           R("5.2.md", "Solving Equal-Base Exponential Equations"), R("Test_3_Review_Human_Readable_Complete.md", "Q.6", "review"),
           assessment_refs=("Test 3 Review Q6",)),
        PF("CH5-EXP-MODEL", "Construct and use an exponential model",
           ("Fit y=ab^t from two data points and make a prediction.",),
           ("Two dated/temporal values and an exponential model form are supplied.",),
           ("exponential modeling",), ("5.2-EXP-MODEL",), ("context",),
           ("find a simple exponential function", "predict"), ("model + prediction",),
           ("CPI", "wage", "population", "growth/decay measurement"),
           ("Using calendar year directly when the model's t=0 should be shifted.",),
           R("5.2.md", "Minimum-Wage Model"), R("Test_3_Review_Human_Readable_Complete.md", "Q.5", "review"),
           application_contexts=("economic index", "growth"),
           assessment_refs=("Test 3 Review Q5",)),
        PF("CH5-EXP-FROM-FEATURES", "Find an exponential function from graph features",
           ("Determine a,b,c from asymptote and intercept information.",),
           ("Form f(x)=ab^{-x}+c or similar and graph features are given.",),
           ("exponential behavior", "intercepts"), (), ("symbolic", "graph"),
           ("find the exponential function",), ("function rule",),
           ("asymptote + x/y intercepts", "growth/decay reflection"),
           ("Using the intercept before accounting for vertical shift.",),
           R("5.2.md", "Finding an Exponential Function")),
    ),
    connections=("Exponential one-to-one behavior and inverses lead directly to logarithms.",),
    source_refs=(R("5.2.md", "Entire lecture"),),
)


SECTION_5_3 = CourseSection(
    id="5.3", chapter=5, title="Natural Exponential Function", unit_id="UNIT3",
    summary="The constant e, limiting compounding, continuous growth, and natural-exponential graph behavior.",
    learning_objectives=(
        "Relate repeated compounding to e.",
        "Compare discrete and continuous compounding.",
        "Use A=Pe^(rt).",
        "Recognize symmetry in expressions involving e^x and e^-x.",
    ),
    concepts=("e", "continuous compounding", "natural exponential", "even function"),
    vocabulary=("continuous compounding", "natural exponential"),
    rules=(),
    formulas=(
        F("5.3-E-LIMIT", r"e=\lim_{n\to\infty}\left(1+\frac1n\right)^n", "Definition via compounding limit.",
          R("5.3.md", "The Number e")),
        F("5.3-CONT", r"A=Pe^{rt}", "Continuous compounding model.",
          R("5.3.md", "Compound Interest Example")),
    ),
    procedures=(),
    worked_examples=(),
    problem_families=(
        PF("CH5-CONTINUOUS-COMPOUND", "Continuous-compounding applications",
           ("Use natural exponential growth to calculate or solve for an unknown.",),
           ("Principal, rate, time, and amount are related by continuous compounding.",),
           ("e", "interest"), (), ("context", "symbolic"),
           ("find", "calculate", "solve"), ("currency / time / rate",),
           ("compare compounding frequencies", "solve for amount", "solve for time"),
           ("Using percent as an integer rather than decimal.",),
           R("5.3.md", "Compound Interest Example"),
           application_contexts=("finance",)),
    ),
    connections=("Natural logarithms in Sections 5.4–5.6 invert natural exponential functions.",),
    source_refs=(R("5.3.md", "Entire lecture"),),
)


SECTION_5_4 = CourseSection(
    id="5.4", chapter=5, title="Logarithmic Functions", unit_id="UNIT3",
    summary="Logs as inverse functions, form conversion, domain/range, graphs, one-to-one equations, and applications.",
    learning_objectives=(
        "Convert between logarithmic and exponential form.",
        "Use inverse identities and domain restrictions.",
        "Solve equal-base logarithmic equations and reject invalid candidates.",
        "Interpret logarithmic/exponential graph relationships and applications.",
    ),
    concepts=("logarithm", "inverse", "log domain", "common log", "natural log", "vertical asymptote", "Richter scale", "growth/decay"),
    vocabulary=("logarithm", "base", "argument", "common logarithm", "natural logarithm"),
    rules=("Every real logarithm argument must be positive.", "Logarithmic functions are one-to-one for valid bases."),
    formulas=(
        F("5.4-DEF", r"\log_a(x)=y\iff a^y=x", "Logarithm/exponential equivalence.",
          R("5.4.md", "Logarithms as Inverse Functions")),
        F("5.4-INVERSE1", r"a^{\log_a x}=x", "Inverse identity.", R("5.4.md", "Logarithms as Inverse Functions"),
          conditions=("x>0",)),
        F("5.4-RICHTER", r"R=\log\left(\frac{I}{I_0}\right)", "Richter-scale model from the notes.",
          R("5.4.md", "Richter Scale")),
    ),
    procedures=(
        P("5.4-EQUAL-LOGS", "Solve equations with equal logs", "Use one-to-one behavior and validate arguments.",
          ("linear equations", "log domain"),
          ("State argument positivity restrictions.", "If log bases match, equate arguments.", "Solve.",
           "Check every logarithm argument in the original equation."), R("5.4.md", "One-to-One Property / Extraneous-Solution Example"),
          verification_steps=("Substitute into every original logarithm argument.",)),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH5-LOG-CONVERT", "Convert logarithmic and exponential forms",
           ("Translate between equivalent notations.",),
           ("One equation is written in either exponential or logarithmic form.",),
           ("log definition",), (), ("symbolic",),
           ("convert", "write in logarithmic form", "write in exponential form"), ("equivalent equation",),
           ("unknown exponent", "unknown argument", "base e/common log"),
           ("Swapping the base and argument.",),
           R("5.4.md", "Converting Between Forms / More Conversions")),
        PF("CH5-LOG-EQUAL", "Equal-log equations with domain checks",
           ("Solve using one-to-one log behavior and reject extraneous candidates.",),
           ("Same log base appears on both sides.",),
           ("log domain", "one-to-one"), ("5.4-EQUAL-LOGS",), ("symbolic",),
           ("solve", "find all real solutions"), ("solution set",),
           ("valid candidate", "extraneous negative argument", "linear/rational arguments"),
           ("Equating arguments without checking positivity.",),
           R("5.4.md", "One-to-One Property / Extraneous-Solution Example")),
        PF("CH5-LOG-GRAPH", "Exponential/log inverse graphs",
           ("Relate domains, ranges, asymptotes, and reflected points.",),
           ("Paired exponential/log functions or a graph is given.",),
           ("inverse", "graph"), (), ("graph", "table", "symbolic"),
           ("state", "identify", "graph"), ("domain/range/asymptote/graph",),
           ("table reflection", "growth vs decay base", "common/natural log"),
           ("Confusing horizontal exponential asymptote with vertical log asymptote.",),
           R("5.4.md", "Graph Relationship / Value Tables")),
    ),
    connections=("Log properties in 5.5 and equation-solving in 5.6 build on this inverse/domain foundation.",),
    source_refs=(R("5.4.md", "Entire lecture"),),
)


SECTION_5_5 = CourseSection(
    id="5.5", chapter=5, title="Properties of Logarithms", unit_id="UNIT3",
    summary="Product, quotient, and power rules; expansion, condensation, equations, and graph transformations.",
    learning_objectives=(
        "Expand one logarithm into sums/differences.",
        "Condense multiple logarithms into one.",
        "Distinguish valid log rules from false addition/subtraction rules.",
        "Use log properties inside equations and graph transformations.",
    ),
    concepts=("product rule", "quotient rule", "power rule", "expansion", "condensation"),
    vocabulary=("expand", "condense", "product rule", "quotient rule", "power rule"),
    rules=("There is no general log(x+y) splitting rule.", "Log arguments must remain positive."),
    formulas=(
        F("5.5-PROD", r"\log_a(xy)=\log_a x+\log_a y", "Product rule.", R("5.5.md", "1. Product Rule")),
        F("5.5-QUOT", r"\log_a\left(\frac{x}{y}\right)=\log_a x-\log_a y", "Quotient rule.",
          R("5.5.md", "2. Quotient Rule")),
        F("5.5-POWER", r"\log_a(x^n)=n\log_a x", "Power rule.", R("5.5.md", "3. Power Rule")),
    ),
    procedures=(
        P("5.5-EXPAND", "Expand a logarithm", "Rewrite products/quotients/powers as sums/differences/coefficient logs.",
          ("factoring", "rational exponents"),
          ("Apply quotient rule.", "Apply product rule.", "Move exponents using the power rule.", "Simplify coefficients."),
          R("5.5.md", "Expanding a Logarithm")),
        P("5.5-CONDENSE", "Condense logarithms", "Combine a linear combination of logs into one logarithm.",
          ("log properties",),
          ("Move coefficients into exponents.", "Combine additions as products.", "Combine subtractions as quotients.",
           "Return one log."), R("5.5.md", "Condensing into a Single Logarithm")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH5-LOG-EXPAND-CONDENSE", "Expand or condense logarithmic expressions",
           ("Apply all three log properties in either direction.",),
           ("Expression contains products/quotients/powers inside or coefficients outside logs.",),
           ("log properties",), ("5.5-EXPAND", "5.5-CONDENSE"), ("symbolic",),
           ("expand", "express as a single logarithm", "condense"), ("log expression",),
           ("radical powers", "factored polynomial arguments", "multiple numerator/denominator factors"),
           ("Splitting log(x+y).", "Dropping exponents/coefficient factors."),
           R("5.5.md", "Expanding / Condensing")),
        PF("CH5-LOG-PROPERTY-EQUATION", "Log equations requiring properties",
           ("Condense/restructure logs before solving and checking domain.",),
           ("Multiple logs appear on one or both sides.",),
           ("log properties", "domain", "equation solving"), ("5.5-CONDENSE", "5.4-EQUAL-LOGS"),
           ("symbolic",), ("solve"), ("solution set",),
           ("logs on both sides", "coefficients become powers", "rational arguments"),
           ("Solving before condensing.", "Skipping the domain check."),
           R("5.5.md", "Solving a Logarithmic Equation")),
    ),
    connections=("The properties are the main algebraic tool for non-equal-base exponential/log equations in 5.6.",),
    source_refs=(R("5.5.md", "Entire lecture"),),
)


SECTION_5_6 = CourseSection(
    id="5.6", chapter=5, title="Exponential and Logarithmic Equations", unit_id="UNIT3",
    summary="Change of base, logarithmic solution methods for exponential equations, and substitution-driven mixed exponential equations.",
    learning_objectives=(
        "Use change of base for numerical logarithms.",
        "Solve exponential equations when bases cannot be made equal.",
        "Use logarithms and the power rule to isolate x.",
        "Recognize substitutions such as u=b^x in mixed b^x and b^-x equations.",
    ),
    concepts=("change of base", "natural logarithm", "exponential equation", "substitution"),
    vocabulary=("change of base", "natural logarithm", "common logarithm"),
    rules=("When taking logarithms of an exponential equation, use the log power rule to bring exponents down."),
    formulas=(
        F("5.6-COB", r"\log_b(a)=\frac{\ln a}{\ln b}", "Change-of-base formula.",
          R("5.6.md", "Change-of-Base Formula")),
    ),
    procedures=(
        P("5.6-EXP-EQ", "Solve a non-equal-base exponential equation", "Use logarithms to turn exponents into coefficients.",
          ("log properties", "linear equations"),
          ("Take ln or log of both sides.", "Use the power rule.", "Collect x-terms.", "Solve.",
           "Approximate only if requested."), R("5.6.md", "Solving Exponential Equations")),
        P("5.6-EXP-SUB", "Solve equations containing b^x and b^-x", "Reduce to an algebraic equation using u=b^x.",
          ("quadratics", "exponential positivity"),
          ("Let u=b^x.", "Rewrite b^-x as 1/u.", "Clear denominators.", "Solve the algebraic equation in u.",
           "Reject u<=0.", "Back-substitute b^x=u and solve with logs."),
          R("5.6.md", "Equation with 5^x and 5^-x")),
    ),
    worked_examples=(),
    problem_families=(
        PF("CH5-EXP-LOG-SOLVE", "Exponential equations requiring logarithms",
           ("Solve exact/approximate real solutions for unequal bases.",),
           ("Exponential terms cannot be rewritten to the same convenient base.",),
           ("logs", "exponents"), ("5.6-EXP-EQ",), ("symbolic",),
           ("solve", "find all real solutions", "approximate"), ("exact log form / decimal",),
           ("single exponential equals constant", "different bases with linear exponents", "quadratic exponent"),
           ("Taking logs but failing to use the power rule.",),
           R("5.6.md", "Examples 1–2")),
        PF("CH5-EXP-MIXED-SUBSTITUTION", "Mixed b^x and b^-x equations",
           ("Recognize and execute an exponential substitution leading to a quadratic.",),
           ("Both b^x and reciprocal b^-x appear.",),
           ("substitution", "quadratics", "logs"), ("5.6-EXP-SUB",), ("symbolic",),
           ("solve",), ("exact/approximate real solution",),
           ("symmetric b^x/b^-x", "quadratic in b^x", "positivity rejection"),
           ("Keeping a negative u even though b^x>0.",),
           R("5.6.md", "Equation with 5^x and 5^-x")),
    ),
    connections=("This section is cumulative: exponent laws, quadratics, logarithm properties, and domain/positivity checks all interact.",),
    source_refs=(R("5.6.md", "Entire lecture"),),
)


COURSE_SECTIONS: tuple[CourseSection, ...] = (
    FOUNDATION,
    SECTION_1_1, SECTION_1_2, SECTION_1_3, SECTION_1_4,
    SECTION_2_1, SECTION_2_2, SECTION_2_3, SECTION_2_4, SECTION_2_5, SECTION_2_6, SECTION_2_7,
    SECTION_3_1, SECTION_3_2, SECTION_3_3, SECTION_3_4, SECTION_3_5, SECTION_3_6, SECTION_3_7,
    SECTION_4_1, SECTION_4_2,
    SECTION_5_1, SECTION_5_2, SECTION_5_3, SECTION_5_4, SECTION_5_5, SECTION_5_6,
)


COURSE_UNITS: tuple[CourseUnit, ...] = (
    CourseUnit(
        id="FOUNDATION",
        title="Foundation",
        chapter_ids=(0,),
        section_ids=("F0",),
        purpose="Prerequisite arithmetic, number-system, notation, and algebra-language review.",
    ),
    CourseUnit(
        id="UNIT1",
        title="Unit 1 — Chapters 1–2",
        chapter_ids=(1, 2),
        section_ids=("1.1", "1.2", "1.3", "1.4", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"),
        purpose="Algebraic structures, expressions, equations, applications, quadratics, complex numbers, and inequalities.",
    ),
    CourseUnit(
        id="UNIT2",
        title="Unit 2 — Chapter 3",
        chapter_ids=(3,),
        section_ids=("3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7"),
        purpose="Coordinate geometry, graphs, lines, functions, domains/ranges, and composition.",
    ),
    CourseUnit(
        id="UNIT3",
        title="Unit 3 — Chapters 4–5",
        chapter_ids=(4, 5),
        section_ids=("4.1", "4.2", "5.1", "5.2", "5.3", "5.4", "5.5", "5.6"),
        purpose="Polynomial structure and graphs, inverse functions, exponentials, logarithms, and cumulative equation solving.",
    ),
)


MATH153_COURSE = Course(
    id="MATH153",
    title="Math 153 — College Algebra",
    units=COURSE_UNITS,
    sections=COURSE_SECTIONS,
)


SECTION_INDEX: dict[str, CourseSection] = {section.id: section for section in COURSE_SECTIONS}
PROBLEM_FAMILY_INDEX: dict[str, ProblemFamily] = {
    family.id: family
    for section in COURSE_SECTIONS
    for family in section.problem_families
}


def sections_for_unit(unit_id: str) -> tuple[CourseSection, ...]:
    unit = next(unit for unit in COURSE_UNITS if unit.id == unit_id)
    return tuple(SECTION_INDEX[section_id] for section_id in unit.section_ids)


def section_by_id(section_id: str) -> CourseSection:
    return SECTION_INDEX[section_id]


def problem_family_by_id(family_id: str) -> ProblemFamily:
    return PROBLEM_FAMILY_INDEX[family_id]


def source_coverage() -> dict[str, int]:
    """Small integrity view used by audits/tests."""
    refs = [
        ref
        for section in COURSE_SECTIONS
        for ref in (
            *section.source_refs,
            *(ref for formula in section.formulas for ref in formula.source_refs),
            *(ref for procedure in section.procedures for ref in procedure.source_refs),
            *(ref for family in section.problem_families for ref in family.source_refs),
        )
    ]
    return {
        "sections": len(COURSE_SECTIONS),
        "problem_families": len(PROBLEM_FAMILY_INDEX),
        "source_refs": len(refs),
        "placeholder_source_refs": sum("PENDING" in ref.document.upper() for ref in refs),
    }


def validate_course_content() -> None:
    """
    Fail fast if the canonical course model regresses to placeholder/shallow content.
    """
    if len(COURSE_SECTIONS) < 20:
        raise ValueError("Math 153 course content is unexpectedly shallow: fewer than 20 sections.")
    if len(PROBLEM_FAMILY_INDEX) < 35:
        raise ValueError("Math 153 problem-family coverage is unexpectedly shallow.")
    ids = [family.id for section in COURSE_SECTIONS for family in section.problem_families]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate problem-family IDs exist in course content.")
    placeholders = [
        ref
        for section in COURSE_SECTIONS
        for ref in section.source_refs
        if "PENDING" in ref.document.upper() or "MODEL-INFERENCE" in ref.document.upper()
    ]
    if placeholders:
        raise ValueError(f"Placeholder source references remain: {placeholders}")


# ---------------------------------------------------------------------------
# Backward-compatible display adapter
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CourseLesson:
    """
    Compatibility view for older Streamlit code.
    New code should use MATH153_COURSE / CourseSection directly.
    """
    title: str
    explanation: str
    formulas: tuple[str, ...]
    example_prompt: str
    example_steps: tuple[str, ...]
    source_refs: tuple[str, ...]
    common_mistakes: tuple[str, ...]
    connections: str


def _section_to_lesson(section: CourseSection) -> CourseLesson:
    first_example = section.worked_examples[0] if section.worked_examples else None
    mistakes = tuple(dict.fromkeys(
        mistake
        for family in section.problem_families
        for mistake in family.common_mistakes
    ))
    refs = tuple(dict.fromkeys(
        f"{ref.document}:{ref.locator}"
        for ref in section.source_refs
    ))
    return CourseLesson(
        title=f"{section.id} — {section.title}",
        explanation=section.summary + "\n\nLearning objectives:\n- " + "\n- ".join(section.learning_objectives),
        formulas=tuple(formula.expression for formula in section.formulas),
        example_prompt=first_example.prompt if first_example else r"\text{See source-grounded problem families below.}",
        example_steps=first_example.steps if first_example else (),
        source_refs=refs,
        common_mistakes=mistakes or ("No section-specific mistake has been authored yet.",),
        connections=" ".join(section.connections),
    )


# New UI keys.
COURSE_LESSONS: dict[str, tuple[CourseLesson, ...]] = {
    unit.title: tuple(_section_to_lesson(section) for section in sections_for_unit(unit.id))
    for unit in COURSE_UNITS
}

# Transitional aliases so the old app does not crash before its navigation is updated.
COURSE_LESSONS["Chapters 1–2"] = COURSE_LESSONS["Unit 1 — Chapters 1–2"]
COURSE_LESSONS["Chapters 3–4"] = (
    *COURSE_LESSONS["Unit 2 — Chapter 3"],
    *tuple(_section_to_lesson(SECTION_INDEX[s]) for s in ("4.1", "4.2")),
)
COURSE_LESSONS["Chapter 5"] = tuple(
    _section_to_lesson(SECTION_INDEX[s]) for s in ("5.1", "5.2", "5.3", "5.4", "5.5", "5.6")
)


validate_course_content()
