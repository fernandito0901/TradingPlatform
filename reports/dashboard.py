"""Simple HTML dashboard for model performance metrics."""

from pathlib import Path


def generate_dashboard(
    train_auc: float, test_auc: float, out_file: str = "reports/dashboard.html"
) -> str:
    """Write an HTML dashboard with model AUC metrics.

    Parameters
    ----------
    train_auc : float
        AUC on training data.
    test_auc : float
        AUC on test data.
    out_file : str, optional
        Destination HTML file.

    Returns
    -------
    str
        Path to the written file.
    """
    html = f"""<html><body>
<h1>Model Performance</h1>
<ul>
  <li>Train AUC: {train_auc:.3f}</li>
  <li>Test AUC: {test_auc:.3f}</li>
</ul>
</body></html>"""
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    Path(out_file).write_text(html)
    return out_file
