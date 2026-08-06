# Architecture

The application is a small vertical slice: canonical family Markdown is parsed into Pydantic models; reviewed Python templates deterministically produce runtime problems; project validators wrap SymPy; a session service records separate learning dimensions to local SQLite; Streamlit owns only presentation state.

Dependencies flow `app → sessions → validation/storage` and `app → generation`. Content is not hardcoded in the UI. Learner records live under ignored `learner_data/`.

This architecture decision preserves Version 0.0 rather than introducing a new framework. Professor Mode, step graphs, builders, and adaptive scheduling remain later modules.
