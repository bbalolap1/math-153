# Streamlit deployment fix

The deployment failed because Poetry attempted to install the repository as the package `math153-tutor`, but the Python package lives in a nested src layout:

`math153_complete_project_rebuild_with_sources/src/math153_tutor`

The root `pyproject.toml` now explicitly declares that package location:

```toml
packages = [
    { include = "math153_tutor", from = "math153_complete_project_rebuild_with_sources/src" }
]
```

Do not use `package-mode = false` for this layout unless you also explicitly configure `PYTHONPATH`; the application imports `math153_tutor.*`, so installing the package is the cleaner fix.

Keep the Streamlit main module configured as:

`math153_complete_project_rebuild_with_sources/src/math153_tutor/app.py`
