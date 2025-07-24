from trading_platform.config import load_config


def test_load_config_reads_env(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=foo\nLOG_LEVEL=DEBUG\n")
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    cfg = load_config(["--symbols", "MSFT"], env_path=env)
    assert cfg.symbols == "MSFT"
    assert cfg.polygon_api_key == "foo"
    assert cfg.log_level == "DEBUG"
