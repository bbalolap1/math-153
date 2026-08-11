from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from .models import DifficultyLayer


@dataclass(frozen=True)
class ComplexityProfile:
    name: str
    weights: dict[DifficultyLayer, int]


PROFILES = {
    "Foundation": ComplexityProfile("Foundation", {
        DifficultyLayer.FOUNDATION: 20, DifficultyLayer.DIRECT: 35,
        DifficultyLayer.GUIDED: 30, DifficultyLayer.REPRESENTATION: 15,
    }),
    "Direct Practice": ComplexityProfile("Direct Practice", {
        DifficultyLayer.FOUNDATION: 20, DifficultyLayer.DIRECT: 50,
        DifficultyLayer.GUIDED: 30,
    }),
    "Mixed Practice": ComplexityProfile("Mixed Practice", {
        DifficultyLayer.DIRECT: 15, DifficultyLayer.GUIDED: 25,
        DifficultyLayer.REPRESENTATION: 25, DifficultyLayer.MIXED: 25,
        DifficultyLayer.PROFESSOR: 10,
    }),
    "Professor Style": ComplexityProfile("Professor Style", {
        DifficultyLayer.REPRESENTATION: 15, DifficultyLayer.MIXED: 25,
        DifficultyLayer.PROFESSOR: 40, DifficultyLayer.TIMED: 20,
    }),
    "Test Review": ComplexityProfile("Test Review", {
        DifficultyLayer.GUIDED: 10, DifficultyLayer.REPRESENTATION: 15,
        DifficultyLayer.MIXED: 25, DifficultyLayer.PROFESSOR: 30,
        DifficultyLayer.TIMED: 15, DifficultyLayer.CUMULATIVE: 5,
    }),
    "Final Exam Challenge": ComplexityProfile("Final Exam Challenge", {
        DifficultyLayer.GUIDED: 5, DifficultyLayer.REPRESENTATION: 10,
        DifficultyLayer.MIXED: 20, DifficultyLayer.PROFESSOR: 30,
        DifficultyLayer.TIMED: 20, DifficultyLayer.CUMULATIVE: 15,
    }),
}

LAYER_VARIANTS = {
    DifficultyLayer.FOUNDATION: (0,), DifficultyLayer.DIRECT: (1,),
    DifficultyLayer.GUIDED: (2,), DifficultyLayer.REPRESENTATION: (3,),
    DifficultyLayer.MIXED: (4,), DifficultyLayer.PROFESSOR: (5, 8),
    DifficultyLayer.TIMED: (6,), DifficultyLayer.CUMULATIVE: (7, 9),
}


def profile_layers(name: str, count: int) -> list[DifficultyLayer]:
    try:
        profile = PROFILES[name]
    except KeyError as exc:
        raise ValueError(f"Unknown complexity profile: {name}") from exc
    raw = {layer: count * weight / 100 for layer, weight in profile.weights.items()}
    allocated = {layer: int(value) for layer, value in raw.items()}
    remaining = count - sum(allocated.values())
    order = sorted(raw, key=lambda layer: raw[layer] - allocated[layer], reverse=True)
    for layer in order[:remaining]:
        allocated[layer] += 1
    layers: list[DifficultyLayer] = []
    while len(layers) < count:
        for layer in profile.weights:
            if allocated[layer] > 0:
                layers.append(layer)
                allocated[layer] -= 1
    return layers


def normalized_prompt_structure(prompt: str) -> str:
    value = re.sub(r"-?\d+(?:\.\d+)?", "#", prompt.casefold())
    return " ".join(value.split())


def application_context(prompt: str) -> str:
    lower = prompt.casefold()
    contexts = {
        "finance": ("interest", "loan", "investment", "payment"),
        "growth_decay": ("population", "decay", "half-life", "growth"),
        "rate_motion": ("rate", "travels", "distance", "speed", "work together"),
        "geometry": ("area", "perimeter", "circle", "rectangle", "volume"),
        "quadratic_model": ("projectile", "height", "maximum"),
    }
    return next((name for name, clues in contexts.items() if any(clue in lower for clue in clues)), "none")


def structural_signature(
    family_id: str, prompt: str, answer_type: str, representation: str
) -> tuple[str, str]:
    lower = prompt.casefold()
    flags = {
        "domain": "domain" in lower or "excluded" in lower,
        "factoring": "factor" in lower,
        "graph": "graph" in lower or "sketch" in lower,
        "composition": "circ" in lower or "composite" in lower,
        "table": "|---" in lower or representation == "table",
        "application": application_context(prompt) != "none",
        "multipart": "(a)" in lower and "(b)" in lower,
    }
    variant = "+".join(name for name, enabled in flags.items() if enabled) or answer_type
    signature = ";".join([
        f"family={family_id}", f"structure={normalized_prompt_structure(prompt)}",
        f"representation={representation}", f"variant={variant}",
    ])
    return variant, signature


def diversity_summary(problems: list[object]) -> dict[str, int]:
    return dict(Counter(getattr(problem, "structural_signature") for problem in problems))
