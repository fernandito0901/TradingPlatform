from __future__ import annotations
from pathlib import Path
import argparse


def gather_plan_files(base: Path) -> list[Path]:
    plans_dir = base / "plans"
    numbered = sorted(plans_dir.glob("P*.md")) if plans_dir.exists() else []
    dated = sorted(base.glob("20*/plan-*.md"))
    return numbered + dated


def gather_arch_docs(base: Path) -> list[Path]:
    arch_dir = base / "architecture"
    if arch_dir.exists():
        return sorted(arch_dir.glob("architecture-*.md"))
    return []


def build_index(base: Path) -> str:
    lines = [
        "# Planning Document Index",
        "",
        "This index lists all planning notes chronologically. Refer to these files for past design decisions and task planning.",
        "",
        "New planning notes should follow the file name pattern `P###.md` and must be linked here.",
        "",
        "## Files",
    ]
    for path in gather_plan_files(base):
        rel = path.relative_to(base)
        lines.append(f"- [{rel}]({rel})")
    lines.append("")
    lines.append("## Architecture")
    for arch in gather_arch_docs(base):
        rel = arch.relative_to(base)
        lines.append(f"- [{rel}]({rel})")
    lines.append("")
    return "\n".join(lines)


def write_index(base: Path, out_file: Path) -> None:
    content = build_index(base)
    out_file.write_text(content)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate PLAN_INDEX.md")
    parser.add_argument("--check", action="store_true", help="only check if up to date")
    args = parser.parse_args(argv)

    base = Path("design")
    out_file = base / "PLAN_INDEX.md"
    content = build_index(base)
    if args.check:
        current = out_file.read_text() if out_file.exists() else ""
        if current != content:
            print("PLAN_INDEX.md is out of date")
            return 1
        return 0
    out_file.write_text(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
