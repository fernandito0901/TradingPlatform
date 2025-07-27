#!/usr/bin/env python
"""Seed demo data for a fresh deployment."""

from pathlib import Path
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, DateTime
import pandas as pd
import shutil

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPORTS_DIR = Path("./reports")


def seed_news(engine) -> None:
    meta = MetaData()
    news = Table(
        "news",
        meta,
        Column("id", Integer, primary_key=True),
        Column("title", String, nullable=False),
        Column("url", String, nullable=False),
        Column("published_at", DateTime),
    )
    meta.create_all(engine)
    conn = engine.connect()
    from sqlalchemy import select, func

    count = conn.execute(select(func.count()).select_from(news)).scalar()
    demo_news = DATA_DIR / "demo_news.csv"
    if count == 0 and demo_news.exists():
        df = pd.read_csv(demo_news)
        df.to_sql("news", conn, if_exists="append", index=False)
        conn.commit()
    conn.close()


def seed_pnl() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    dest = REPORTS_DIR / "pnl.csv"
    demo_pnl = DATA_DIR / "sample_pnl.csv"
    if not dest.exists() and demo_pnl.exists():
        shutil.copy(demo_pnl, dest)


def main() -> None:
    db_path = REPORTS_DIR / "scoreboard.db"
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    seed_news(engine)
    seed_pnl()


if __name__ == "__main__":
    main()
