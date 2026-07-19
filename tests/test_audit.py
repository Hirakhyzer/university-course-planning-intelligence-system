from courseplan.audit import append_record, verify_log


def test_audit_log_hash_chain(tmp_path):
    path = tmp_path / "audit.jsonl"
    append_record(path, {"event": "synthetic_course_plan", "students": 12})
    append_record(path, {"event": "advisor_report", "status": "created"})
    result = verify_log(path)
    assert result["valid"] is True
    assert result["records"] == 2
