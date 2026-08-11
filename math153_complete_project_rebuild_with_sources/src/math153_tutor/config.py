from __future__ import annotations

MAX_QUESTIONS = 50
QUESTION_COUNT_OPTIONS = (5, 10, 15, 20, 25, 30, 40, 50)

DEFAULT_QUIZ_COUNT = 5
DEFAULT_TEST_COUNT = 15
DEFAULT_EXAM_COUNT = 30

# Quality gates are intentionally strict. If generation cannot meet them, the system should
# report missing source-supported constructions rather than silently repeat the same problem.
REQUIRE_NEAR_DUPLICATE_FREE_ASSESSMENTS = True
REQUIRE_SOURCE_REFS = True
REQUIRE_VALIDATED_EXPECTED_ANSWERS = True
MIN_CANONICAL_SECTIONS = 20
MIN_CANONICAL_FAMILIES = 35


def validate_question_count(count: int) -> None:
    if not 1 <= count <= MAX_QUESTIONS:
        raise ValueError(
            f"Question count must be between 1 and {MAX_QUESTIONS}; received {count}."
        )
