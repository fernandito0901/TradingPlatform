from trading_platform.webapp import create_app


def test_overview_snapshot(monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=abc\n")

    def fake_snap():
        return {"tickers": [{"ticker": "AAPL", "close": 100}]}

    monkeypatch.setattr(
        "trading_platform.collector.api.fetch_snapshot_tickers", fake_snap
    )

    app = create_app(env_path=env)
    client = app.test_client()

    resp = client.get("/api/overview")
    assert resp.json[0]["ticker"] == "AAPL"
