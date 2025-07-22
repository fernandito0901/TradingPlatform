# AGENTS.md
*Single‑source handbook for all AI programming agents in this repo.*

---

## 1  Global Guidelines  <!-- apply to every agent -->
- **Code Style:** PEP8 + Black (run `black .` before committing).
- **Tests:** All Python code must pass `pytest -q` before PR merge.
- **Docs:** Public functions need a NumPy‑style docstring; update `CHANGELOG.md` for user‑facing changes.
- **Commit Msg:** `[Role] <one‑line summary>` – example: `[Coder] Implement GARCH sigma service`
- **Branching:** Work in `feature/<task‑slug>`; never push directly to `main`.
- **Security:** Never expose API keys; load from env vars.

---

## 2  Collaboration Protocol
1. **Planner → DataCollector → Modeler → Synthesizer → Tester → Reviewer**  
   Work on a task flows in that order unless explicitly parallelized.
2. **Shared Memory:**  
   - Use `TASKS.md` for open tasks & IDs.  
   - Use `NOTES.md` for design ideas or interim findings.  
   - Agents must read latest versions before starting new work.
3. **Messaging:**  
   Agents communicate by appending a Markdown bullet under their role heading in `NOTES.md`, prefixed with date/time.
4. **Error Handling:**  
   - If tests fail, Tester documents failure in PR and re‑assigns to Coder.  
   - If any agent is unsure, write “⚠ NEEDS‑HUMAN‑REVIEW” in `NOTES.md` and stop.
5. **Timeout / Deadlock:**  
   If an agent’s task exceeds 10 min wall‑clock or 3 consecutive failures, escalate to Planner.

---

## 3  Role Definitions
*(Each agent must read its matching block in addition to the Global Guidelines.)*

### @Planner
**Purpose** Architect & task decomposer  
**Key Inputs** `README.md`, feature requests, bug reports  
**Outputs** `TASKS.md` with bullet tasks including: ID · title · acceptance criteria · assignee role  
**Workflow**  
1. Parse requirement → draft design notes in `design/`.  
2. Break into tasks; estimate complexity; assign `@Coder`, `@Modeler`, etc.  
3. Update `NOTES.md` → hand off to next agent.  

### @DataCollector
**Purpose** Fetch raw market / option / news data  
**Key Tools** Polygon API, NewsAPI, Python `requests`, caching layer  
**Outputs** `data/{date}/` CSV or Parquet + `data_catalog.json` summary  
**Workflow**  
1. Read latest tasks where `assignee == DataCollector`.  
2. Pull data; validate row counts & schema.  
3. Commit data + update `NOTES.md` with path & any anomalies.

### @Modeler
**Purpose** Compute indicators & predictive features  
**Key Tools** pandas, NumPy, scikit‑learn (local), in‑repo `models/` libs  
**Outputs** `features/{date}/features.csv`; retrained model artifacts under `models/`; metrics in `NOTES.md`  
**Workflow**  
1. Load data paths from DataCollector note.  
2. Run feature pipeline: SMA, RSI, IV/HV, GARCH σ (or fallback).  
3. If retrain flag present, retrain LightGBM & log AUC / accuracy.  
4. Hand off to Synthesizer.

### @Synthesizer
**Purpose** Generate daily options‑trade playbook  
**Key Tools** Python helpers in `playbook/`, option‑pricing lib  
**Outputs** `playbooks/{date}.json` and a Markdown “DETAILS” section in PR  
**Workflow**  
1. Read `features.csv` & model predictions.  
2. Apply scoring rule:  
   `Score = 2.5·prob_up + 1.5·momentum + news_sent + IV_edge + UOA - garch_spike`.  
3. Select trades per rules in `playbook/config.yaml`.  
4. Write JSON → commit & open PR for Tester.

### @Tester
**Purpose** Validate code, data integrity, and playbook schema  
**Key Tools** pytest, jsonschema, flake8  
**Outputs** PR comment with ✅ / ❌; coverage report in `reports/`  
**Workflow**  
1. Run `pytest -q` and schema validation on playbook JSON.  
2. If failures → mark PR ❌ and ping Coder/Synthesizer.  
3. If all green → mark ✅ and ping Reviewer.

### @Reviewer
**Purpose** Enforce quality & merge PRs  
**Key Checklist**  
- All tests green  
- Code follows style  
- Docs updated  
- No TODOs or debug prints  
**Workflow**  
1. Review diff; request changes if needed.  
2. When satisfied, squash‑merge to `main`.  
3. Update `CHANGELOG.md`.  

---

## 4  File Ownership Matrix
| Path Pattern | Primary Agent |
|--------------|---------------|
| `data/**`            | DataCollector |
| `features/**`        | Modeler |
| `models/**`          | Modeler |
| `playbooks/**`       | Synthesizer |
| `tests/**`           | Tester |
| `design/**`          | Planner |
| `**/*.md` (docs)     | Reviewer |

---

## 5  Glossary
- **POP** – Probability of Profit (Monte‑Carlo or Black‑Scholes estimate).  
- **IV_edge** – (IV30 – HV30) / HV30.  
- **UOA** – Unusual Options Activity flag (volume ≥ 5× 30‑d avg).

---

## 6  Project Overview & Vision  <!-- informational; no actionable rules -->

**What we’re building**  
This repository hosts an *autonomous, multi‑agent trading‑research platform* that produces a **Daily Options‑Trade Playbook** before the U.S. market opens.  
Each morning the agents:

1. **Collect** fresh market, options‑chain, and news data (DataCollector).  
2. **Engineer features & update models** to quantify momentum, volatility edge, sentiment, and probability of price moves (Modeler).  
3. **Synthesize** a JSON playbook listing the highest‑score swing or day‑trade option strategies, complete with POP, Greeks, and rationale (Synthesizer).  
4. **Validate** the output via full test suites and schema checks (Tester).  
5. **Review & merge** the playbook to `main` so humans (or downstream bots) can act on it (Reviewer).  

A Planner / Coordinator agent keeps tasks aligned and resolves ambiguities.

**Why it matters**  
- **Speed & Scale:** AI agents can scan thousands of strikes, run GARCH forecasts, and parse news far faster than any single human analyst.  
- **Consistency:** Formalized scoring rules and automated tests ensure every playbook meets the same quality bar.  
- **Transparency:** The entire workflow is open‑source; every metric is reproducible, every decision traceable in `NOTES.md` and the commit history.  

**Long‑term goal**  
To evolve into a self‑adapting research stack that not only outputs trade ideas but also **learns from live P/L**, retrains itself, and surfaces new alpha signals—while remaining fully auditable by humans.

*(This section is descriptive only; agents do **not** need to act on it. It exists to give context to new contributors—human or AI—about what this project is aiming to achieve.)*

