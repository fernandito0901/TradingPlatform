from importlib import import_module

app = import_module("trading_platform.webapp").create_app()


def test_root_route():
    with app.test_client() as c:
        resp = c.get("/")
        assert resp.status_code == 200
