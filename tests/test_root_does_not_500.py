from trading_platform.webapp import create_app
from pathlib import Path


def test_root_route(tmp_path):
    app = create_app(env_path=tmp_path / ".env")
    Path(app.static_folder).mkdir(parents=True, exist_ok=True)
    (Path(app.static_folder) / "index.html").write_text("hi")
    with app.test_client() as c:
        resp = c.get("/")
        assert resp.json == {"status": "ok"}
