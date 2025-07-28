import re
from pathlib import Path


def gather_plan_files(base: Path) -> list[Path]:
    plans_dir = base / "plans"
    numbered = sorted(plans_dir.glob("P*.md")) if plans_dir.exists() else []
    dated = sorted(base.glob("20*/plan-*.md"))
    return numbered + dated


def expected_header(path: Path) -> str:
    if path.parent.name == "plans":
        num_match = re.search(r"P(\d+)", path.stem)
        if num_match:
            return f"# Planning Notes - P{num_match.group(1)}"
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", path.stem)
    if date_match:
        return f"# Planning Notes - {date_match.group(1)}"
    return ""


def check_file(path: Path) -> str | None:
    with open(path, "r") as fh:
        first_line = fh.readline().strip()
    exp = expected_header(path)
    if first_line != exp:
        return f"{path}: '{first_line}' != '{exp}'"
    return None


def main() -> int:
    base = Path("design")
    errors = []
    for file in gather_plan_files(base):
        err = check_file(file)
        if err:
            errors.append(err)
    if errors:
        for err in errors:
            print(err)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
