import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Load all results
main = pd.read_csv('results/4_decision_confidence.csv')
business_impact = pd.read_csv('results/simulation/business_impact.csv')
cost_by_type = pd.read_csv('results/simulation/cost_by_type.csv')
yearly = pd.read_csv('results/6_yearly_health.csv')
peeking_by_type = pd.read_csv('results/tableau/tableau_peeking_by_type.csv')
false_positive_by_type = pd.read_csv('results/2_false_positive_by_type.csv')

# Merge main with business impact
full = main.merge(
    business_impact[[
        'experiment_id',
        'false_positive_shipped',
        'total_cost_of_wrong_decision',
        'confidence_category'
    ]],
    on='experiment_id',
    how='left'
)

# Add experiment number for timeline
full['experiment_number'] = range(1, len(full) + 1)

# Create charts folder
os.makedirs('charts', exist_ok=True)

print("Data loaded — generating charts")

# ── CHART 1: The Graveyard Plot ────────────────────────
# Every experiment as a dot across time
# Colour = error type, Size = decision confidence score

color_map = {
    'True Positive': '#2ecc71',
    'False Positive': '#e74c3c',
    'True Negative': '#95a5a6',
    'False Negative': '#f39c12'
}

fig1 = px.scatter(
    full,
    x='experiment_number',
    y='decision_confidence_score',
    color='error_type',
    symbol='peeked',
    title='The Graveyard — 200 Experiments, 5 Years of Decisions',
    labels={
        'experiment_number': 'Experiment (chronological order)',
        'decision_confidence_score': 'Decision Confidence Score',
        'error_type': 'Outcome',
        'peeked': 'Stopped Early'
    },
    color_discrete_map=color_map,
    hover_data=['experiment_type', 'p_value', 'actual_sample_size']
)

fig1.add_hline(
    y=50,
    line_dash='dash',
    line_color='white',
    annotation_text='Confidence threshold (50)',
    annotation_position='top right'
)

fig1.update_layout(
    plot_bgcolor='#1a1a2e',
    paper_bgcolor='#1a1a2e',
    font=dict(family='Arial', size=13, color='white'),
    title_font_size=18,
    legend_title_text='Outcome'
)

fig1.update_traces(marker=dict(size=8, opacity=0.8))

fig1.write_html('charts/1_the_graveyard.html')
print(" Chart 1 saved — The Graveyard Plot")

# ── CHART 2: The Peeking Tax ───────────────────────────
# False positive rate for peeked vs non-peeked by experiment type

peeked_true = peeking_by_type[peeking_by_type['peeked'] == True].copy()
peeked_false = peeking_by_type[peeking_by_type['peeked'] == False].copy()

fig2 = go.Figure()

# Non-peeked line
fig2.add_trace(go.Scatter(
    x=peeked_false['experiment_type'],
    y=peeked_false['false_positive_rate'],
    mode='markers',
    name='Not Peeked',
    marker=dict(size=14, color='#2ecc71', symbol='circle'),
))

# Peeked line
fig2.add_trace(go.Scatter(
    x=peeked_true['experiment_type'],
    y=peeked_true['false_positive_rate'],
    mode='markers',
    name='Peeked (stopped early)',
    marker=dict(size=14, color='#e74c3c', symbol='circle'),
))

# Connect with lines
for exp_type in peeking_by_type['experiment_type'].unique():
    not_peeked_val = peeked_false[peeked_false['experiment_type'] == exp_type]['false_positive_rate'].values
    peeked_val = peeked_true[peeked_true['experiment_type'] == exp_type]['false_positive_rate'].values

    if len(not_peeked_val) > 0 and len(peeked_val) > 0:
        fig2.add_trace(go.Scatter(
            x=[exp_type, exp_type],
            y=[not_peeked_val[0], peeked_val[0]],
            mode='lines',
            line=dict(color='#888', width=1.5, dash='dot'),
            showlegend=False
        ))

fig2.update_layout(
    title='The Peeking Tax — How Stopping Early Inflates False Positives',
    xaxis_title='Experiment Type',
    yaxis_title='False Positive Rate (%)',
    plot_bgcolor='#1a1a2e',
    paper_bgcolor='#1a1a2e',
    font=dict(family='Arial', size=12, color='white'),
    title_font_size=18,
    xaxis_tickangle=45
)

fig2.write_html('charts/2_the_peeking_tax.html')
print(" Chart 2 saved — The Peeking Tax")

# ── CHART 3: The Cost Cascade ──────────────────────────
# Waterfall chart showing how £17.2M in damage accumulates

cost_by_type_sorted = cost_by_type.sort_values('total_cost', ascending=False)

# Build waterfall data
labels = ['Starting Point'] + list(cost_by_type_sorted['experiment_type']) + ['Total Cost']
values = [0] + list(cost_by_type_sorted['total_cost']) + [cost_by_type_sorted['total_cost'].sum()]
measures = ['absolute'] + ['relative'] * len(cost_by_type_sorted) + ['total']

fig3 = go.Figure(go.Waterfall(
    name='Cost',
    orientation='v',
    measure=measures,
    x=labels,
    y=values,
    text=[f'£{v:,.0f}' if v > 0 else '' for v in values],
    textposition='outside',
    connector=dict(line=dict(color='#888', width=1)),
    increasing=dict(marker=dict(color='#e74c3c')),
    totals=dict(marker=dict(color='#f39c12'))
))

fig3.update_layout(
    title='The Cost Cascade — How £17.2M in Wrong Decisions Accumulates',
    yaxis_title='Cumulative Cost (£)',
    plot_bgcolor='#1a1a2e',
    paper_bgcolor='#1a1a2e',
    font=dict(family='Arial', size=12, color='white'),
    title_font_size=18,
    xaxis_tickangle=45,
    showlegend=False
)

fig3.write_html('charts/3_the_cost_cascade.html')
print(" Chart 3 saved — The Cost Cascade")

# ── CHART 4: The Confidence Trap ───────────────────────
# Heatmap of experiment type vs confidence category
# Coloured by false positive count

heatmap_data = full.groupby(
    ['experiment_type', 'confidence_category']
).agg(
    false_positives=('error_type', lambda x: (x == 'False Positive').sum())
).reset_index()

heatmap_pivot = heatmap_data.pivot(
    index='experiment_type',
    columns='confidence_category',
    values='false_positives'
).fillna(0)

fig4 = go.Figure(data=go.Heatmap(
    z=heatmap_pivot.values,
    x=heatmap_pivot.columns.tolist(),
    y=heatmap_pivot.index.tolist(),
    colorscale=[
        [0, '#1a1a2e'],
        [0.5, '#c0392b'],
        [1, '#e74c3c']
    ],
    text=heatmap_pivot.values,
    texttemplate='%{text:.0f}',
    textfont=dict(size=14, color='white'),
    hoverongaps=False
))

fig4.update_layout(
    title='The Confidence Trap — False Positives by Feature Area and Confidence Level',
    xaxis_title='Confidence Category',
    yaxis_title='Experiment Type',
    plot_bgcolor='#1a1a2e',
    paper_bgcolor='#1a1a2e',
    font=dict(family='Arial', size=12, color='white'),
    title_font_size=18
)

fig4.write_html('charts/4_the_confidence_trap.html')
print(" Chart 4 saved — The Confidence Trap")

# ── CHART 5: Did They Get Better? ─────────────────────
# Year by year experiment health trend

fig5 = go.Figure()

fig5.add_trace(go.Scatter(
    x=yearly['year'],
    y=yearly['avg_confidence_score'],
    mode='lines+markers',
    name='Avg Confidence Score',
    line=dict(color='#2ecc71', width=3),
    marker=dict(size=10)
))

fig5.add_trace(go.Bar(
    x=yearly['year'],
    y=yearly['false_positives'],
    name='False Positives',
    marker=dict(color='#e74c3c', opacity=0.6),
    yaxis='y2'
))

fig5.update_layout(
    title='Did They Get Better? — Experiment Quality 2020 to 2024',
    xaxis_title='Year',
    yaxis=dict(
        title='Avg Decision Confidence Score',
        color='#2ecc71'
    ),
    yaxis2=dict(
        title='False Positives',
        overlaying='y',
        side='right',
        color='#e74c3c'
    ),
    plot_bgcolor='#1a1a2e',
    paper_bgcolor='#1a1a2e',
    font=dict(family='Arial', size=13, color='white'),
    title_font_size=18,
    legend=dict(
        bgcolor='rgba(0,0,0,0)',
        bordercolor='rgba(0,0,0,0)'
    )
)

fig5.write_html('charts/5_did_they_get_better.html')
print("Chart 5 saved — Did They Get Better?")

# ── END ───────────────────────────────────────────────
print("\n" + "="*50)
print("ALL CHARTS GENERATED")
print("="*50)
print("\nCharts saved in your charts folder:")
print("  1_the_graveyard.html")
print("  2_the_peeking_tax.html")
print("  3_the_cost_cascade.html")
print("  4_the_confidence_trap.html")
print("  5_did_they_get_better.html")
print("\nOpen any file in your browser to view it.")