"""Simple HTML dashboard for model performance metrics."""

from pathlib import Path


def generate_dashboard(
    train_auc: float,
    test_auc: float,
    cv_auc: float | None = None,
    out_file: str = "reports/dashboard.html",
) -> str:
    """Write an HTML dashboard with model AUC metrics.

    Parameters
    ----------
    train_auc : float
        AUC on training data.
    test_auc : float
        AUC on test data.
    cv_auc : float, optional
        Mean cross-validation AUC.
    out_file : str, optional
        Destination HTML file.

    Returns
    -------
    str
        Path to the written file.
    """
    html = ["<html><body>", "<h1>Model Performance</h1>", "<ul>"]
    html.append(f"  <li>Train AUC: {train_auc:.3f}</li>")
    html.append(f"  <li>Test AUC: {test_auc:.3f}</li>")
    if cv_auc is not None:
        html.append(f"  <li>CV AUC: {cv_auc:.3f}</li>")
    html.extend(["</ul>", "</body></html>"])
    html_str = "\n".join(html)
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    Path(out_file).write_text(html_str)
    return out_file
