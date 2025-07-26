# Schemas

## Feature DataFrame
Columns produced by `features.pipeline`:
- `sma20`: 20 day simple moving average
- `rsi14`: 14 day relative strength index
- `iv30`: average 30 day implied volatility
- `hv30`: 30 day historical volatility
- `garch_sigma`: volatility estimate from GARCH(1,1)
- `news_sent`: news sentiment score
- `iv_edge`: difference between implied and historical volatility
- `garch_spike`: binary indicator when GARCH volatility exceeds HV
- `uoa`: unusual options activity ratio
- `target`: binary next-day up indicator

## Playbook JSON
Output of `playbook.generate_playbook`:
```json
{
  "date": "YYYY-MM-DD",
  "trades": [
    {"t": 1, "score": 0.5}
  ]
}
```
