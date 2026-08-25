from verification.log_verification import validate


def test_empty_verification_file_is_valid(tmp_path):
    path = tmp_path / "verification.csv"
    path.write_text("case_id,verification_command,before_result,after_result,verification_status,verified_by,verification_timestamp,notes\n", encoding="utf-8")
    assert validate(path) == []
