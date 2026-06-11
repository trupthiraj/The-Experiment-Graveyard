import pandas as pd
import numpy as np
import os

# Load decision confidence scores
df = pd.read_csv('results/4_decision_confidence.csv')
os.makedirs('results/simulation', exist_ok=True)

np.random.seed(42)

print(f" Loaded {len(df)} experiments")

# ── BUSINESS COST MODEL ────────────────────────────────
# Each experiment type has an estimated cost to ship
# and an estimated monthly revenue impact if wrong

SHIPPING_COSTS = {
    'Autoplay next episode': 45000,
    'Personalised thumbnail': 30000,
    'Top 10 label': 15000,
    'Skip intro button': 20000,
    'Price discount popup': 25000,
    'Recommended row placement': 35000,
    'Continue watching prompt': 20000,
    'Social proof badge': 10000,
    'Download for offline prompt': 40000,
    'Email re-engagement': 15000
}

# Monthly revenue impact of a wrongly shipped feature
# (negative = hurting the product)
WRONG_FEATURE_MONTHLY_IMPACT = {
    'Autoplay next episode': -8000,
    'Personalised thumbnail': -5000,
    'Top 10 label': -3000,
    'Skip intro button': -6000,
    'Price discount popup': -12000,
    'Recommended row placement': -7000,
    'Continue watching prompt': -4000,
    'Social proof badge': -2000,
    'Download for offline prompt': -5000,
    'Email re-engagement': -3000
}

# Average months a wrongly shipped feature stays live
AVG_MONTHS_LIVE = 18

# ── CALCULATE COSTS ────────────────────────────────────
results = []

for _, row in df.iterrows():
    shipping_cost = SHIPPING_COSTS.get(row['experiment_type'], 20000)
    monthly_impact = WRONG_FEATURE_MONTHLY_IMPACT.get(row['experiment_type'], -5000)

    # Was this a false positive that got shipped?
    false_positive_shipped = (
        row['error_type'] == 'False Positive' and
        row['called_winner'] == True
    )

    # Total cost of a wrongly shipped feature
    total_wrong_cost = shipping_cost + abs(monthly_impact * AVG_MONTHS_LIVE)

    # Decision confidence category
    if row['decision_confidence_score'] >= 75:
        confidence_category = 'High Confidence'
    elif row['decision_confidence_score'] >= 50:
        confidence_category = 'Medium Confidence'
    else:
        confidence_category = 'Low Confidence'

    results.append({
        'experiment_id': row['experiment_id'],
        'experiment_type': row['experiment_type'],
        'error_type': row['error_type'],
        'called_winner': row['called_winner'],
        'false_positive_shipped': false_positive_shipped,
        'decision_confidence_score': row['decision_confidence_score'],
        'confidence_category': confidence_category,
        'shipping_cost': shipping_cost if false_positive_shipped else 0,
        'monthly_revenue_impact': monthly_impact if false_positive_shipped else 0,
        'total_cost_of_wrong_decision': total_wrong_cost if false_positive_shipped else 0
    })

results_df = pd.DataFrame(results)
results_df.to_csv('results/simulation/business_impact.csv', index=False)
print(" Saved results/simulation/business_impact.csv")

# ── SUMMARY ────────────────────────────────────────────
false_positives_shipped = results_df[results_df['false_positive_shipped'] == True]

total_shipping_waste = false_positives_shipped['shipping_cost'].sum()
total_revenue_damage = abs(false_positives_shipped['monthly_revenue_impact'].sum() * AVG_MONTHS_LIVE)
total_cost = false_positives_shipped['total_cost_of_wrong_decision'].sum()

print("\n" + "="*55)
print("BUSINESS IMPACT OF FALSE POSITIVES")
print("="*55)
print(f"False positives shipped as features:  {len(false_positives_shipped)}")
print(f"Total engineering cost wasted:        £{total_shipping_waste:,.0f}")
print(f"Total revenue damage (18 months):     £{total_revenue_damage:,.0f}")
print(f"Total cost of wrong decisions:        £{total_cost:,.0f}")

# Cost by experiment type
print("\nCost breakdown by experiment type:")
by_type = false_positives_shipped.groupby('experiment_type').agg(
    count=('experiment_id', 'count'),
    total_cost=('total_cost_of_wrong_decision', 'sum')
).sort_values('total_cost', ascending=False).reset_index()
by_type.to_csv('results/simulation/cost_by_type.csv', index=False)
print(by_type.to_string(index=False))

# Cost by confidence category
print("\nCost breakdown by confidence category:")
by_confidence = results_df.groupby('confidence_category').agg(
    total_experiments=('experiment_id', 'count'),
    false_positives_shipped=('false_positive_shipped', 'sum'),
    total_cost=('total_cost_of_wrong_decision', 'sum')
).reset_index()
by_confidence.to_csv('results/simulation/cost_by_confidence.csv', index=False)
print(by_confidence.to_string(index=False))

print("\n Phase 3 complete")