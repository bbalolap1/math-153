from __future__ import annotations

import json

from math153_tutor.build_validation import validate_build
from math153_tutor.paths import REPOSITORY_ROOT


if __name__ == "__main__":
    report = validate_build(REPOSITORY_ROOT)
    print(json.dumps(report.model_dump(), indent=2))
    if not report.passed:
        raise SystemExit(1)
