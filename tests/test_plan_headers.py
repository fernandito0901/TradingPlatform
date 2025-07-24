from scripts.check_plan_headers import gather_plan_files, check_file, expected_header
from pathlib import Path


def test_expected_header():
    path = Path("design/plans/P001.md")
    assert expected_header(path) == "# Planning Notes - P001"


def test_gather_plan_files():
    files = gather_plan_files(Path("design"))
    assert any(f.name == "P001.md" for f in files)


def test_check_file_valid():
    path = Path("design/plans/P001.md")
    assert check_file(path) is None
