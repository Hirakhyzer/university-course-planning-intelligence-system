from courseplan.synthetic import PROGRAMS, SyntheticCourseConfig, generate_synthetic_university_data


def test_synthetic_shapes_and_keys():
    data = generate_synthetic_university_data(SyntheticCourseConfig(students=16, seed=3))
    assert set(data) == {"catalog", "professors", "sections", "students", "transcripts"}
    assert len(data["students"]) == 16
    assert data["students"]["goal_program"].nunique() == len(PROGRAMS)
    assert data["catalog"]["course_id"].is_unique
    assert data["sections"]["available_seats"].min() >= 0


def test_invalid_student_count_rejected():
    try:
        SyntheticCourseConfig(students=4)
    except ValueError:
        assert True
    else:
        raise AssertionError("invalid config should fail")
