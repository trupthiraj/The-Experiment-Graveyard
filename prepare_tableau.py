import pandas as pd
import os

os.makedirs('results/tableau', exist_ok=True)

# Load all result files
decision_confidence = pd.read_csv('results/4_decision_confidence.csv')
business_impact = pd.read_csv('results/simulation/business_impact.csv')
cost_by_type = pd.read_csv('results/simulation/cost_by_type.csv')
yearly_health = pd.read_csv('results/6_yearly_health.csv')
peeking = pd.read_csv('results/3_peeking_analysis.csv')
false_positive_by_type = pd.read_csv('results/2_false_positive_by_type.csv')

# ── DATASET 1: Main experiment dataset ─────────────────
# Used for: Graveyard scatter + League Table
main = decision_confidence.merge(
    business_impact[[
        'experiment_id',
        'false_positive_shipped',
        'shipping_cost',
        'monthly_revenue_impact',
        'total_cost_of_wrong_decision',
        'confidence_category'
    ]],
    on='experiment_id',
    how='left'
)

# Add experiment number for timeline ordering
main['experiment_number'] = range(1, len(main) + 1)

main.to_csv('results/tableau/tableau_main.csv', index=False)
print(" Saved tableau_main.csv")

# ── DATASET 2: False positive by type + peeking ────────
# Used for: Dumbbell chart + League Table
fp_peeking = false_positive_by_type.copy()

# Add peeked vs non-peeked false positive rates per type
peeked_rates = pd.read_csv('results/4_decision_confidence.csv')

peeked_summary = peeked_rates.groupby(['experiment_type', 'peeked']).agg(
    total=('experiment_id', 'count'),
    false_positives=('error_type', lambda x: (x == 'False Positive').sum())
).reset_index()

peeked_summary['false_positive_rate'] = round(
    peeked_summary['false_positives'] / peeked_summary['total'] * 100, 1
)

peeked_summary.to_csv('results/tableau/tableau_peeking_by_type.csv', index=False)
print(" Saved tableau_peeking_by_type.csv")

# ── DATASET 3: Yearly health ───────────────────────────
# Used for: Year by year trend
yearly_health.to_csv('results/tableau/tableau_yearly.csv', index=False)
print(" Saved tableau_yearly.csv")

# ── DATASET 4: Cost breakdown ──────────────────────────
# Used for: Treemap
cost_by_type.to_csv('results/tableau/tableau_cost.csv', index=False)
print(" Saved tableau_cost.csv")

# ── DATASET 5: Opening statement numbers ──────────────
# Used for: The 3 big numbers panel
summary = pd.DataFrame([{
    'total_experiments': 200,
    'false_positives': 147,
    'total_cost': 17177000,
    'true_winners': 51,
    'peeked': 82,
    'underpowered': 33
}])
summary.to_csv('results/tableau/tableau_summary.csv', index=False)
print("Saved tableau_summary.csv")

print("\n All Tableau datasets ready")
print("Files saved in results/tableau/:")
print("  tableau_main.csv")
print("  tableau_peeking_by_type.csv")
print("  tableau_yearly.csv")
print("  tableau_cost.csv")
print("  tableau_summary.csv")