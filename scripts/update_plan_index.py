import pathlib


def gather_plans(design_dir: pathlib.Path):
    """Gather plan documents grouped by month and numbered plans.

    Parameters
    ----------
    design_dir : pathlib.Path
        Root ``design`` directory containing plan files.

    Returns
    -------
    tuple[dict[str, list[pathlib.Path]], list[pathlib.Path]]
        Mapping of ``YYYY-MM`` months to their plan files and a list of
        numbered plans.
    """

    monthly: dict[str, list[pathlib.Path]] = {}
    for path in design_dir.glob("20[0-9][0-9]-[0-1][0-9]/plan-*.md"):
        month = path.parent.name
        monthly.setdefault(month, []).append(path)
    for files in monthly.values():
        files.sort()
    numbered = sorted(design_dir.joinpath("plans").glob("P*.md"))
    return monthly, numbered


def write_index(
    index_path: pathlib.Path,
    monthly: dict[str, list[pathlib.Path]],
    numbered: list[pathlib.Path],
):
    """Write PLAN_INDEX.md using gathered plan data.

    Parameters
    ----------
    index_path : pathlib.Path
        Destination index file to write.
    monthly : dict[str, list[pathlib.Path]]
        Mapping of months to dated plan files.
    numbered : list[pathlib.Path]
        Sequentially numbered plan files.
    """

    lines = [
        "# Planning Document Index",
        "",
        "This index lists all planning notes chronologically. Refer to these files for past design decisions and task planning.",
        "",
        "New planning notes should follow the file name pattern `plan-YYYY-MM-DD.md` and must be linked here.",
        "",
        "## Files",
    ]
    for month in sorted(monthly):
        lines.append(f"### {month}")
        for path in monthly[month]:
            rel = path.relative_to(index_path.parent)
            lines.append(f"- [{rel}]({rel})")
        lines.append("")
    if numbered:
        lines.append("### Numbered Plans")
        for path in numbered:
            rel = path.relative_to(index_path.parent)
            lines.append(f"- [{rel}]({rel})")
        lines.append("")
    for path in sorted(index_path.parent.glob("architecture-*.md")):
        rel = path.relative_to(index_path.parent)
        lines.append(f"- [{rel}]({rel})")
    index_path.write_text("\n".join(lines) + "\n")


def main() -> None:
    design_dir = pathlib.Path(__file__).resolve().parents[1] / "design"
    index_path = design_dir / "PLAN_INDEX.md"
    monthly, numbered = gather_plans(design_dir)
    write_index(index_path, monthly, numbered)


if __name__ == "__main__":
    main()
