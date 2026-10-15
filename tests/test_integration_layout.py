"""Guard the canonical project against accidental nested rebuild replacement."""
import hashlib
import subprocess
import sys
from pathlib import Path

from math153_tutor.paths import content_root, source_manifest_path, sources_root
from math153_tutor.source_manifest import read_manifest

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_evidence_resolves_to_unchanged_canonical_sources() -> None:
    entries = read_manifest(source_manifest_path())
    assert entries
    for entry in entries:
        path = ROOT / entry.actual_path
        assert path.is_relative_to(sources_root())
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry.content_hash
    assert list(content_root().glob("chapter_*/*.md"))


def test_direct_streamlit_script_runs_without_installed_project(tmp_path) -> None:
    # Ignore PYTHONPATH and remove editable project paths while retaining user-installed dependencies.
    code = '''
import os, sys
from pathlib import Path
from streamlit.testing.v1 import AppTest
root, data = sys.argv[1:]
sys.path[:] = [p for p in sys.path if root not in p]
for finder in list(sys.meta_path):
    if "editable" in str(finder).lower():
        sys.meta_path.remove(finder)
os.environ["MATH153_DATA_DIR"] = data
app = AppTest.from_file(str(Path(root) / "src/math153_tutor/app.py"), default_timeout=30).run()
assert not app.exception, str(app.exception)
assert app.title[0].value == "Math 153 — Welcome"
import math153_tutor
assert Path(math153_tutor.__file__).resolve() == Path(root) / "src/math153_tutor/__init__.py"
'''
    result = subprocess.run(
        [sys.executable, "-E", "-P", "-c", code, str(ROOT), str(tmp_path / "learner_data")],
        cwd=tmp_path, text=True, capture_output=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
