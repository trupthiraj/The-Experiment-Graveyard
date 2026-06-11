import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)
np.random.seed(42)

# Streaming platform experiment types
EXPERIMENT_TYPES = [
    'Autoplay next episode',
    'Personalised thumbnail',
    'Top 10 label',
    'Skip intro button',
    'Price discount popup',
    'Recommended row placement',
    'Continue watching prompt',
    'Social proof badge',
    'Download for offline prompt',
    'Email re-engagement'
]

# Metrics each experiment measures
METRICS = {
    'Autoplay next episode': 'watch_time',
    'Personalised thumbnail': 'click_through_rate',
    'Top 10 label': 'engagement_rate',
    'Skip intro button': 'episode_completion',
    'Price discount popup': 'subscription_conversion',
    'Recommended row placement': 'click_through_rate',
    'Continue watching prompt': 'watch_time',
    'Social proof badge': 'engagement_rate',
    'Download for offline prompt': 'feature_adoption',
    'Email re-engagement': 'reactivation_rate'
}

print(" Setup complete")

# Generate 200 experiments over 5 years
experiments = []
start_date = datetime(2020, 1, 1)
end_date = datetime(2024, 12, 31)

for i in range(200):
    # Random experiment type
    exp_type = random.choice(EXPERIMENT_TYPES)
    metric = METRICS[exp_type]
    
    # Random start date
    exp_start = start_date + timedelta(
        days=random.randint(0, (end_date - start_date).days - 30)
    )
    
    # Planned duration (14-60 days)
    planned_duration = random.randint(14, 60)
    
    # Did someone peek and stop early?
    peeked = random.random() < 0.45  # 45% of experiments were stopped early
    actual_duration = random.randint(3, planned_duration - 1) if peeked else planned_duration
    
    exp_end = exp_start + timedelta(days=actual_duration)
    
    # Sample size
    planned_sample = random.randint(1000, 50000)
    actual_sample = int(planned_sample * (actual_duration / planned_duration)) if peeked else planned_sample
    
    # True effect — most experiments have no real effect
    has_true_effect = random.random() < 0.30  # only 30% have a genuine effect
    true_effect_size = round(random.uniform(0.01, 0.08), 4) if has_true_effect else 0
    
    # Observed effect — noisy measurement
    noise = random.gauss(0, 0.03)
    observed_effect = round(true_effect_size + noise, 4)
    
    # P-value calculation
    if actual_sample > 0:
        standard_error = 0.05 / (actual_sample ** 0.5)
        z_score = observed_effect / standard_error if standard_error > 0 else 0
        from scipy import stats
        p_value = round(2 * (1 - stats.norm.cdf(abs(z_score))), 4)
    else:
        p_value = 1.0
    
    # Was it called a winner?
    called_winner = p_value < 0.05
    
    # Was it actually a winner?
    true_winner = has_true_effect and observed_effect > 0
    
    # Type of error
    if called_winner and not true_winner:
        error_type = 'False Positive'
    elif not called_winner and true_winner:
        error_type = 'False Negative'
    elif called_winner and true_winner:
        error_type = 'True Positive'
    else:
        error_type = 'True Negative'
    
    # Was it underpowered?
    min_sample_needed = 5000
    underpowered = actual_sample < min_sample_needed
    
    # Multiple metrics tested (p-hacking risk)
    metrics_tested = random.randint(1, 5)
    p_hacking_risk = metrics_tested > 2
    
    experiments.append({
        'experiment_id': f'EXP{i+1:03d}',
        'experiment_type': exp_type,
        'primary_metric': metric,
        'start_date': exp_start.strftime('%Y-%m-%d'),
        'end_date': exp_end.strftime('%Y-%m-%d'),
        'planned_duration_days': planned_duration,
        'actual_duration_days': actual_duration,
        'planned_sample_size': planned_sample,
        'actual_sample_size': actual_sample,
        'peeked': peeked,
        'has_true_effect': has_true_effect,
        'true_effect_size': true_effect_size,
        'observed_effect_size': observed_effect,
        'p_value': p_value,
        'called_winner': called_winner,
        'true_winner': true_winner,
        'error_type': error_type,
        'underpowered': underpowered,
        'metrics_tested': metrics_tested,
        'p_hacking_risk': p_hacking_risk
    })

experiments_df = pd.DataFrame(experiments)
experiments_df.to_csv('experiments.csv', index=False)

print(f" Experiments generated: {len(experiments_df)}")
print(f" Called winners: {experiments_df['called_winner'].sum()}")
print(f" True winners: {experiments_df['true_winner'].sum()}")
print(f" False positives: {(experiments_df['error_type'] == 'False Positive').sum()}")
print(f" Peeked experiments: {experiments_df['peeked'].sum()}")
print(f" Underpowered: {experiments_df['underpowered'].sum()}")
print(f" Saved to experiments.csv")