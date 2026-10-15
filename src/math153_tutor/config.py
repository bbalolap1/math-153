MAX_QUESTIONS = 50
QUESTION_COUNT_OPTIONS = (5, 10, 15, 20, 25, 30, 40, 50)


def validate_question_count(count: int) -> None:
    if not 1 <= count <= MAX_QUESTIONS:
        raise ValueError(f"Question count must be between 1 and {MAX_QUESTIONS}; received {count}.")
