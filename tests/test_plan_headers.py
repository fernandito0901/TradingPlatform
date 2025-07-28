from pathlib import Path

from scripts.check_plan_headers import check_file, expected_header, gather_plan_files


def test_expected_header():
    path = Path("design/plans/P009.md")
    assert expected_header(path) == "# Planning Notes - P009"


def test_gather_plan_files():
    files = gather_plan_files(Path("design"))
    assert any(f.name == "P009.md" for f in files)


def test_check_file_valid():
    path = Path("design/plans/P009.md")
    assert check_file(path) is None
