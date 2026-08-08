from math153_tutor.course_materials import (
    list_course_materials,
    save_course_material,
    search_course_materials,
)


def test_course_material_round_trip_preserves_markdown_and_provenance(tmp_path) -> None:
    path = save_course_material(
        tmp_path,
        title='Week 3 "review"',
        section="Chapters 1–2",
        source_type="Notes",
        body="## Linear equations\n\nPreserve equality.",
        topic="equations",
    )

    assert path.suffix == ".md"
    materials = list_course_materials(tmp_path)
    assert len(materials) == 1
    assert materials[0].title == 'Week 3 "review"'
    assert materials[0].section == "Chapters 1–2"
    assert materials[0].source_type == "Notes"
    assert materials[0].body.startswith("## Linear equations")
    assert materials[0].verification_status == "learner_added_unverified"
    assert search_course_materials(materials, "preserve equality") == materials


def test_course_material_rejects_empty_body(tmp_path) -> None:
    try:
        save_course_material(
            tmp_path, title="Empty", section="Foundation", source_type="Notes", body="  "
        )
    except ValueError as error:
        assert str(error) == "Course material cannot be empty."
    else:
        raise AssertionError("Expected empty material to be rejected")
