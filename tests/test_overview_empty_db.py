from trading_platform.webapp import create_app
import tempfile


def test_overview_empty_db(monkeypatch):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    monkeypatch.setenv("TP_DB", tmp.name)
    app = create_app()
    client = app.test_client()
    res = client.get("/api/overview")
    assert res.status_code == 200
