# Validation

`validation.py` provides project-level numeric, exact numeric, expression, and unordered solution-set entry points. Inputs are constrained before SymPy parsing, equivalent values normalize symbolically, exact-form checks reject floating answers when required, and learner-facing results use stable error codes rather than raw exceptions. Interval, equation, units, and graph-feature validators remain future work.
