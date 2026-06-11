# The Experiment Graveyard

> *5 years. 200 experiments. Most of them wrong.*

An audit of A/B testing quality at a fictional streaming platform. This project simulates 5 years of product experiments, identifies statistical failures, and calculates the business cost of shipping features based on invalid results.

---

## Live Dashboard
**[View The Experiment Graveyard on Tableau Public](https://public.tableau.com/app/profile/trupthi.raj/viz/TheExperimentGraveyard/TheExperimentGraveyard?publish=yes)**

---

## The Headline Finding

Of 200 experiments run over 5 years:
- **197 were called winners** by the team
- **Only 51 were true winners** with a genuine effect
- **147 were false positives** — noise mistaken for signal
- **£17,177,000** in total cost from wrong product decisions

The platform was confidently shipping features based on experiments that were never statistically valid.

---

## The Three Villains

### 1. Peeking
45% of experiments were stopped early because results looked promising. Experiments stopped early had an 81.3% false positive rate vs 70.1% for experiments that ran to completion. Impatience cost the platform its statistical integrity.

### 2. Underpowered Tests
33 experiments ran with sample sizes too small to detect a real effect. These tests could not reliably distinguish signal from noise, yet their results were acted on.

### 3. P-Hacking
57% of experiments tested more than 2 metrics and reported only the significant one. This inflates the chance of finding a false positive by testing multiple outcomes and cherry-picking the best result.

---

## Proprietary Metrics

### 1. Decision Confidence Score (0 to 100)
Measures how statistically valid each experiment decision was. Penalises peeking (minus 30), underpowered tests (minus 25), p-hacking risk (minus 20), and borderline p-values between 0.01 and 0.05 (minus 10).

### 2. False Positive Risk Index
A composite risk score per experiment combining peeking probability, underpowered risk, p-hacking exposure, and p-value proximity to the significance threshold.

### 3. Wasted Decision Rate
The percentage of shipped features that were based on experiments with a Decision Confidence Score below 50. In this audit: 10.7% of all shipped features were poorly validated.

---

## The Business Impact

Each false positive that got shipped as a feature carried two costs: the engineering cost to build it, and the ongoing monthly revenue damage from a feature that was hurting the product rather than helping it.

At an average of 18 months live before being reviewed:

| Experiment Type | False Positives Shipped | Total Cost |
|---|---|---|
| Price discount popup | 12 | £2,892,000 |
| Download for offline prompt | 19 | £2,470,000 |
| Autoplay next episode | 11 | £2,079,000 |
| Skip intro button | 16 | £2,048,000 |
| Personalised thumbnail | 15 | £1,800,000 |

Total across all experiment types: **£17,177,000**

---

## Strategic Recommendations

### 1. Enforce minimum run times
No experiment should be stopped before its planned duration without a pre-registered sequential testing protocol. Peeking without correction inflates false positive rates by 11 percentage points on average.

### 2. Run power calculations before every experiment
Every experiment should calculate the minimum sample size needed to detect a meaningful effect before it starts. Underpowered tests waste engineering time and produce unreliable results.

### 3. Pre-register primary metrics
Each experiment should declare one primary metric before it runs. Secondary metrics can be tracked but should not be used to call a winner. This eliminates p-hacking by removing the ability to cherry-pick post-hoc.

### 4. Introduce a Decision Confidence Score threshold
No experiment result below a Decision Confidence Score of 70 should trigger a ship decision without a secondary review. This single rule would have prevented 21 poorly validated feature launches in this audit.

### 5. Build an experiment health dashboard
Track peeking rate, average run duration, and false positive rate as ongoing operational metrics. The 5 Year Audit shows these numbers barely improved year on year — without visibility, the problem compounds silently.

---

## Project Structure
```
the-experiment-graveyard/
├── generate_experiments.py   # Generates 200 synthetic A/B experiments
├── load_data.py              # Loads experiment data into PostgreSQL
├── queries.sql               # All SQL queries and proprietary metric views
├── run_analysis.py           # Runs all queries and saves results as CSV
├── simulation.py             # Business impact simulation
├── charts.py                 # Generates 5 interactive Python charts
├── prepare_tableau.py        # Prepares merged datasets for Tableau
├── experiments.csv           # Synthetic experiment data (200 rows)
├── results/                  # All analysis outputs
│   ├── simulation/           # Business impact results
│   └── tableau/              # Tableau-ready datasets
└── charts/                   # Interactive HTML charts (open in browser)
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Experiment simulation, business impact modelling, visualisation |
| PostgreSQL | Database, all SQL analysis runs here |
| SQL | Window functions, CTEs, proprietary metric views |
| SciPy | Statistical calculations (z-scores, p-values) |
| Plotly | Interactive HTML charts |
| Tableau Public | Main dashboard, live and interactive |
| pandas / numpy | Data manipulation and modelling |

---

## How To Run

1. Clone the repository
2. Install dependencies: `pip install psycopg2-binary plotly pandas numpy scipy`
3. Set up PostgreSQL and update credentials in `load_data.py` and `run_analysis.py`
4. Run in order:
```bash
python generate_experiments.py
python load_data.py
python run_analysis.py
python simulation.py
python charts.py
python prepare_tableau.py
```
5. Open any file in `charts/` in your browser to view Python visualisations
6. View the live Tableau dashboard at the link above

---

## Author

**Trupthi Raj** — Data and Business Analyst
[LinkedIn](https://www.linkedin.com/in/trupthi-raj) · [GitHub](https://github.com/trupthiraj) · [Tableau Public](https://public.tableau.com/app/profile/trupthi.raj)

