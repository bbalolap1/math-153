import zipfile
from types import SimpleNamespace

import pytest

from scripts.build_source_manifest import main as build_source_manifest

from scripts.extract_sources import safe_extract


def test_safe_extract_accepts_normal_members_and_rejects_zip_slip(tmp_path) -> None:
    safe_archive = tmp_path / "safe.zip"
    with zipfile.ZipFile(safe_archive, "w") as archive:
        archive.writestr("math153/Quiz_1.pdf", b"fixture")
    destination = tmp_path / "safe"
    safe_extract(safe_archive, destination)
    assert (destination / "math153/Quiz_1.pdf").read_bytes() == b"fixture"

    unsafe_archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(unsafe_archive, "w") as archive:
        archive.writestr("../../outside.txt", b"no")
    with pytest.raises(ValueError, match="Unsafe archive member"):
        safe_extract(unsafe_archive, tmp_path / "unsafe")


def test_manifest_script_emits_validation_from_markdown(tmp_path, monkeypatch) -> None:
    source = tmp_path / "sources" / "lectures"
    source.mkdir(parents=True)
    (source / "1.1.md").write_text("# 1.1 Complex Numbers\n\n## Example\n$i^2=-1$\n", encoding="utf-8")
    spec = SimpleNamespace(title="Complex numbers", section="1.1", skills=("complex arithmetic",))
    monkeypatch.setattr("scripts.build_source_manifest.FAMILY_SPECS", {"CH12-COMPLEX": spec})
    build_source_manifest(str(tmp_path))
    report = __import__("json").loads((tmp_path / "data/derived/source_validation.json").read_text())
    assert report["markdown_sources_discovered"] == 1
    assert report["markdown_sources_read"] == 1
    assert report["markdown_sources_unused"] == 0
