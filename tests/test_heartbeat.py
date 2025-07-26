from trading_platform.webapp import create_app


def test_heartbeat_route():
    app = create_app()
    client = app.test_client()
    res = client.get("/api/heartbeat")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}
