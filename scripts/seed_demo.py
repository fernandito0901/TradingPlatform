#!/usr/bin/env python
"""Seed demo data for a fresh deployment."""

import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine

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
    from sqlalchemy import func, select

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
    if dest.exists():
        return
    if demo_pnl.exists():
        shutil.copy(demo_pnl, dest)
    else:
        n = 30
        df = pd.DataFrame({"pnl": np.random.normal(10, 50, n).round(2)})
        df.to_csv(dest, index=False)


def main() -> None:
    db_path = REPORTS_DIR / "scoreboard.db"
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    seed_news(engine)
    seed_pnl()


if __name__ == "__main__":
    main()
