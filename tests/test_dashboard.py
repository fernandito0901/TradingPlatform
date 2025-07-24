"""Tests for dashboard report generation."""

from pathlib import Path

from reports.dashboard import generate_dashboard


def test_generate_dashboard(tmp_path):
    html = generate_dashboard(
        0.8, 0.7, cv_auc=0.75, out_file=str(tmp_path / "dash.html")
    )
    text = Path(html).read_text()
    assert "Train AUC" in text
    assert "Test AUC" in text
    assert "CV AUC" in text
