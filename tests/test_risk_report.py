"""Tests for risk report CLI."""

import pytest
from trading_platform import risk_report


def test_risk_metrics(tmp_path):
    csv = tmp_path / "score.csv"
    data = "date,playbook,auc,pnl\n2025-01-01,pb1,0.7,1\n2025-01-02,pb2,0.8,-0.5\n2025-01-03,pb3,0.9,1.5\n"
    csv.write_text(data)
    df = risk_report.risk_metrics(str(csv))
    assert list(df.columns) == ["date", "sharpe", "max_drawdown"]
    assert len(df) == 3
    # first row sharpe is 0 because std=0
    assert df.iloc[0]["sharpe"] == 0
    # max drawdown after second day is negative
    assert df.iloc[1]["max_drawdown"] < 0


def test_risk_metrics_missing_file(tmp_path):
    missing = tmp_path / "none.csv"
    with pytest.raises(FileNotFoundError):
        risk_report.risk_metrics(str(missing))
