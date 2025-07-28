import sqlite3

from scripts import seed_demo


def test_seed_demo(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    demo_csv = data_dir / "demo_news.csv"
    demo_csv.write_text("title,url,published_at\nhi,http://x,2025-01-01\n")
    pnl = data_dir / "sample_pnl.csv"
    pnl.write_text("date,symbol,unrealized,realized,total\n2025-01-01,AAPL,0,0,1\n")
    reports = tmp_path / "reports"
    monkeypatch.setattr(seed_demo, "DATA_DIR", data_dir)
    monkeypatch.setattr(seed_demo, "REPORTS_DIR", reports)
    seed_demo.main()
    assert (reports / "pnl.csv").exists()
    conn = sqlite3.connect(reports / "scoreboard.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM news")
    assert cur.fetchone()[0] >= 1
    conn.close()
