from trading_platform.db import bootstrap


def test_bootstrap_creates_news_table(tmp_path):
    db_file = tmp_path / "test.db"
    conn = bootstrap(db_file)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM news")
    assert cur.fetchone()[0] >= 0
    conn.close()
