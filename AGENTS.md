
# AGENTS.md  
_Single-source handbook for all AI programming agents in this trading-research repository._

---

## 📌 1. Global Guidelines

These rules apply to all roles—human and AI.

- **Code Style:** Python PEP8 + Black (run `black .` before committing).
- **Testing:** All code must pass `pytest -q`; failure blocks PR merge.
- **Docs:** Public functions require NumPy-style docstrings; log changes in `CHANGELOG.md`.
- **Commits:** Use format `[<Role>] <summary>` — e.g. `[Modeler] Add GARCH volatility forecast`.
- **Branching:** Use `feature/<slug>` branches; never commit directly to `main`.
- **Security:** Never expose API keys. Use environment variables and `.env` files only.

---

## 🔁 2. Collaboration Protocol

### Standard Agent Chain

```
Planner → DataCollector → Modeler → Synthesizer → Tester → Reviewer
```

### Shared Memory

- `TASKS.md` — master task list with ID, owner, status, and description.
- `NOTES.md` — design notes, discoveries, or agent logs.
- All agents must read latest versions of both before working.

### Communication Format

Each agent must append structured logs in `NOTES.md` under their role using this format:

```markdown
### 2025-07-23 – @DataCollector  
- Pulled OHLCV, options chain, and VIX data for TSLA and AMD.  
- Stored in `data/2025-07-23/`.  
- No anomalies detected.
```

### Error Escalation

- ❌ If tests fail, the @Tester marks PR as ❌ and reassigns to relevant agent.
- ⚠ If any agent is uncertain, write `⚠ NEEDS-HUMAN-REVIEW` in `NOTES.md` and halt.

### Stalling Protocol

- If an agent fails the same task 3× or is idle for over 10 minutes wall-clock, escalate to @Planner.
- Do not guess or improvise beyond scope—log the block and wait.

---

## 🧠 3. Agent Role Specs

### 🔹 @Planner  
> **Role:** Task Architect & Coordinator

- Reads `REQUESTS.md` for goals or reports.
- Breaks requirements into atomic tasks with IDs, complexity, and assigned role.
- Writes interfaces or blueprints in `design/`.
- Updates `TASKS.md` and logs context in `NOTES.md`.

---

### 🔹 @DataCollector  
> **Role:** Pull and cache raw market data

- Uses Polygon, NewsAPI, and optionally FRED.
- Outputs go to `data/YYYY-MM-DD/` in CSV/Parquet + `data_catalog.json`.
- Notes must specify symbol, date range, and checks passed.

---

### 🔹 @Modeler  
> **Role:** Engineer features & run predictive models

- Loads data from @DataCollector.
- Computes IV/HV, SMA, RSI, GARCH volatility, sentiment, and POP.
- Trains or loads models from `models/`; outputs `features.csv` and logs metrics.
- If `retrain: true`, retrain model and log ROC/AUC/F1 scores.

---

### 🔹 @Synthesizer  
> **Role:** Generate JSON trade playbook + Markdown summary

- Uses scoring function:

  ```
  Score = 2.5 * prob_up + 1.5 * momentum + news_sent + IV_edge + UOA - garch_spike
  ```

- Reads config from `playbook/config.yaml`.
- Outputs: `playbooks/YYYY-MM-DD.json` and details section in PR body.
- Adds visual charts (optional) and rationale in `NOTES.md`.

---

### 🔹 @Tester  
> **Role:** Validate code, data, schema, and test coverage

- Runs: `pytest`, `flake8`, `black`, and JSON schema validation.
- If ✅: mark PR approved and ping Reviewer.
- If ❌: document reason and assign back to last agent.

---

### 🔹 @Reviewer  
> **Role:** Final merge gate & quality assurance

- Verifies: passing tests, clean commit history, no `TODO`/`print()` left.
- Ensures `CHANGELOG.md` is updated.
- If satisfied: squash-merge PR into `main` and log in `NOTES.md`.

---

## 📁 4. File Ownership Matrix

| Path Pattern        | Owner         |
|---------------------|---------------|
| `data/**`           | @DataCollector |
| `features/**`       | @Modeler       |
| `models/**`         | @Modeler       |
| `playbooks/**`      | @Synthesizer   |
| `tests/**`          | @Tester        |
| `design/**`         | @Planner       |
| `*.md`, `CHANGELOG` | @Reviewer      |

---

## 📚 5. Glossary

- **POP** – Probability of Profit; estimated from GARCH or Black-Scholes.
- **IV_edge** – (IV30 − HV30) / HV30; a measure of volatility mispricing.
- **UOA** – Unusual Options Activity (volume ≥ 5× 30-day avg).
- **Score** – Weighted ranking for trade ideas based on edge and prediction.
- **GARCH σ** – Conditional volatility forecast via GARCH(1,1).
- **IV/HV** – Implied Volatility vs Historical Volatility.

---

## 🧭 6. Project Overview & Vision

### 🧠 What We’re Building

A fully autonomous agent system that builds a **Daily Options-Trade Playbook** using real-time market data, predictive models, and consistent rules.

Every day before market open:

1. @DataCollector scrapes stock, options, news, and sentiment data.  
2. @Modeler computes predictive features and retrains models as needed.  
3. @Synthesizer selects the top option strategies based on edge, POP, and macro context.  
4. @Tester runs full validations.  
5. @Reviewer merges final output to `main` for human consumption or automated trading.

### 🎯 Why It Matters

- **Scalability:** An AI team that evaluates 1000s of tickers daily.
- **Consistency:** Formal scoring and schema enforcement.
- **Transparency:** Every decision is logged, testable, and reviewable.

### 🚀 Long-Term Vision

To evolve into a **self-adapting research and execution engine**—one that:

- Learns from real-world results (P/L tracking)  
- Refines models autonomously  
- Surfaces new signals, edges, and strategies  
- Stays fully auditable and human-overridable

*(This section is informational. Agents do not act on it directly.)*

---

© 2025 TradingPlatform AI – MIT Licensed
