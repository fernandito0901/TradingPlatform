from reports.dashboard import generate_dashboard
from pathlib import Path


def test_generate_dashboard(tmp_path):
    html = generate_dashboard(0.8, 0.7, out_file=str(tmp_path / "dash.html"))
    text = Path(html).read_text()
    assert "Train AUC" in text
    assert "Test AUC" in text
