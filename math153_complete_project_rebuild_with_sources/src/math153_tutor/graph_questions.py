from __future__ import annotations

from pydantic import BaseModel, Field


class GraphPoint(BaseModel, frozen=True):
    x: float
    y: float


class GraphQuestion(BaseModel):
    problem_id: str
    family_id: str
    prompt_latex: str
    expected_points: set[GraphPoint] = Field(default_factory=set)
    source_refs: list[str]
    difficulty_layer: str
    variant_reason: str
    expected_features: list[str] = Field(default_factory=list)


INTERCEPT_QUESTION = GraphQuestion(
    problem_id="CH3-CIRCLE-INTERCEPTS-GRAPH-0",
    family_id="CH3-CIRCLE-INTERCEPTS",
    prompt_latex=r"\text{Select both x-intercepts of }x^2+y^2=16.",
    expected_points={GraphPoint(x=-4, y=0), GraphPoint(x=4, y=0)},
    source_refs=["3.2.md:Circle material", "Quiz_6.md:Q.2"],
    difficulty_layer="L3",
    variant_reason="graph/coordinate representation of a source-supported circle intercept family",
    expected_features=["x-intercepts", "two symmetric points"],
)

POLYNOMIAL_ZERO_QUESTION = GraphQuestion(
    problem_id="CH4-POLY-SIGN-GRAPH-0",
    family_id="CH4-POLY-SIGN-GRAPH",
    prompt_latex=r"\text{Select the x-intercepts of }y=(x+2)(x-3).",
    expected_points={GraphPoint(x=-2, y=0), GraphPoint(x=3, y=0)},
    source_refs=["4.2.md:Graphing Polynomials"],
    difficulty_layer="L4",
    variant_reason="connect algebraic zeros to graphical intercepts",
    expected_features=["zeros", "x-intercepts"],
)


def validate_graph_points(question: GraphQuestion, selected: set[GraphPoint]) -> bool:
    return selected == question.expected_points
