import zipfile

import pytest

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
