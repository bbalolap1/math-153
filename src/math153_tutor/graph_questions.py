from __future__ import annotations

from pydantic import BaseModel


class GraphPoint(BaseModel, frozen=True):
    x: float
    y: float


class GraphQuestion(BaseModel):
    problem_id: str
    family_id: str
    prompt_latex: str
    expected_points: set[GraphPoint]
    source_refs: list[str]
    difficulty_layer: str
    variant_reason: str


INTERCEPT_QUESTION = GraphQuestion(
    problem_id="CH34-GRAPH-INTERCEPTS-V0",
    family_id="CH34-QUADRATIC-FUNCTIONS",
    prompt_latex=r"\text{Select both x-intercepts of }y=x^2-4.",
    expected_points={GraphPoint(x=-2, y=0), GraphPoint(x=2, y=0)},
    source_refs=["MODEL-INFERENCE-PENDING-SOURCE-REVIEW"],
    difficulty_layer="L3",
    variant_reason="Representation bridge from factoring an equation to locating graph intercepts.",
)


def validate_graph_points(question: GraphQuestion, selected: set[GraphPoint]) -> bool:
    return selected == question.expected_points
