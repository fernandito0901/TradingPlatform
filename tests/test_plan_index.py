from pathlib import Path
from scripts.gen_plan_index import build_index


def test_build_index_contains_latest():
    content = build_index(Path("design"))
    assert "plans/P001.md" in content
