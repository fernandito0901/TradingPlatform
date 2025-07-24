
# AGENTS.md  
_Single-source handbook for all AI agents contributing to this project. Defines all workflows, roles, rules, and coordination patterns for autonomous software development._

---

## 📌 1. Global Guidelines

- **Code Style:** Python projects follow PEP8 + Black. Run `black .` before PR.
- **Tests:** All PRs must pass `pytest`, `flake8`, and any applicable schema checks.
- **Docs:** Use NumPy-style docstrings. Document public functions. Update `CHANGELOG.md` for any user-facing change.
- **Commits:** Format: `[<Role>] <summary>` (e.g. `[Coder] Add GARCH sigma calculator`)
- **Branching:** Use `feature/<slug>` branches. Never push directly to `main`.
- **Security:** Never expose keys or secrets. Use `.env`, config vaults, or encrypted secrets.

---

## 🔁 2. Collaboration Protocol

### Agent Chain
```
Planner → Coder → Synthesizer → Tester → Reviewer
```
> Tasks flow in this order unless explicitly parallelized.

### Shared Memory
- `TASKS.md`: Agent-readable open task registry
- `NOTES.md`: Agent-to-agent handoff log
- `CODE_ATLAS.md`: Function/class summaries (auto-generated)
- `SCHEMAS.md`: JSON formats, DataFrame dtypes, and scoring logic

### Communication
Agents append notes to `NOTES.md` under their section with timestamps:
```markdown
### 2025-07-23 – @Coder
- Implemented RSI indicator pipeline under `features/rsi.py`.
```

### Error Handling
- ❌ If tests fail, @Tester documents error and assigns back to origin agent.
- ⚠ If any agent is uncertain, write `⚠ NEEDS-HUMAN-REVIEW` and halt.
- 🕒 If no progress in 10 min or 3 failed attempts, escalate to @Planner.

---

## 🧠 3. Agent Role Definitions

### @Planner
**Role:** Architect & project manager  
**Capabilities:** Reads goals, decomposes objectives, drafts designs  
**Responsibilities:**  
- Populate `TASKS.md` with task breakdown  
- Write design notes (`design/*.md`)  
- Clarify scope, unblock agents

---

### @Coder
**Role:** Implements core functionality  
**Capabilities:** Writes code, runs local tests, observes coding standards  
**Responsibilities:**  
- Implement from planner specs  
- Push to `src/`, update tests  
- Log changes in `NOTES.md` and open handoff to @Tester

---

### @Synthesizer
**Role:** Combines modules into coherent systems  
**Capabilities:** Merges logic, rewrites interfaces, adds examples/docs  
**Responsibilities:**  
- Refactor outputs from multiple coders  
- Finalize APIs or combined workflows  
- Document module behavior in `docs/`  
- Handoff to @Tester

---

### @Tester
**Role:** Run all validations (tests, lint, schema)  
**Capabilities:** `pytest`, `black`, `flake8`, `jsonschema`  
**Responsibilities:**  
- Run full test suite + static checks  
- ✅ If all green: notify Reviewer  
- ❌ If errors: record in PR and notify author  
- Ensure >90% coverage where applicable

---

### @Reviewer
**Role:** Final quality gate  
**Capabilities:** Code diff review, style enforcement, changelog validation  
**Responsibilities:**  
- Review final PR and summarize change  
- Enforce all Global Guidelines  
- Merge to `main`  
- Update `CHANGELOG.md` + `NOTES.md`

---

## 🗂️ 4. File Ownership Matrix

| Path Pattern       | Primary Agent   |
|--------------------|-----------------|
| `src/**`           | @Coder          |
| `design/**`        | @Planner        |
| `features/**`      | @Modeler        |
| `models/**`        | @Modeler        |
| `playbooks/**`     | @Synthesizer    |
| `tests/**`         | @Tester         |
| `docs/**`          | @Synthesizer    |
| `*.md`             | @Reviewer       |

---

## 🧾 5. Glossary

- **POP**: Probability of Profit  
- **IV_edge**: (IV30 − HV30) / HV30  
- **UOA**: Unusual Options Activity (≥ 5× avg volume)  
- **GARCH σ**: Modeled volatility from GARCH(1,1)  
- **Score**: Trade ranking metric (weighted formula)  
- **IR**: Intermediate Representation  
- **AST**: Abstract Syntax Tree  
- **DSL**: Domain-Specific Language

---

## 🔎 6. Context & Tooling Add-ons

- `CODE_ATLAS.md`: Auto-generated function/class index  
- `SCHEMAS.md`: JSON schema + DataFrame column specs  
- `RUNBOOK.md`: Manual troubleshooting guide  
- `WORKFLOW.md`: Agent-to-agent handoff sequences  
- `playbook/config.yaml`: Scoring rules and filters

---

## 🚀 7. Project Vision

**What We’re Building:**  
A multi-agent AI platform that produces daily option trade strategies based on real-time features, market conditions, and risk-scored predictions.

**Workflow:**
1. DataCollector pulls options/price/news data  
2. Modeler creates features & prediction models  
3. Synthesizer builds JSON playbook  
4. Tester validates data integrity & schema  
5. Reviewer approves for deployment

**Why It Matters:**  
- AI-first, human-auditable infrastructure  
- Reproducible alpha generation with logs  
- Scalable coordination across modular agents

---

© 2025 TradingPlatform AI — MIT Licensed
