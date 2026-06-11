import psycopg2
import pandas as pd
import os

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="postgres",
    user="postgres",
    password="postgres123"
)

os.makedirs('results', exist_ok=True)
print(" Connected to PostgreSQL")

# ── QUERY 1: Sanity check ──────────────────────────────
print("\nRunning Query 1: Sanity check...")
q1 = """
    SELECT
        COUNT(*) as total_experiments,
        SUM(CASE WHEN called_winner = true THEN 1 ELSE 0 END) as called_winners,
        SUM(CASE WHEN true_winner = true THEN 1 ELSE 0 END) as true_winners,
        SUM(CASE WHEN error_type = 'False Positive' THEN 1 ELSE 0 END) as false_positives,
        SUM(CASE WHEN peeked = true THEN 1 ELSE 0 END) as peeked_experiments,
        SUM(CASE WHEN underpowered = true THEN 1 ELSE 0 END) as underpowered_experiments
    FROM experiments;
"""
df1 = pd.read_sql(q1, conn)
df1.to_csv('results/1_sanity_check.csv', index=False)
print(df1.to_string(index=False))
print(" Saved to results/1_sanity_check.csv")

# ── QUERY 2: False positive rate by experiment type ────
print("\nRunning Query 2: False positive rate by experiment type...")
q2 = """
    SELECT
        experiment_type,
        COUNT(*) as total_experiments,
        SUM(CASE WHEN called_winner = true THEN 1 ELSE 0 END) as called_winners,
        SUM(CASE WHEN error_type = 'False Positive' THEN 1 ELSE 0 END) as false_positives,
        ROUND(
            SUM(CASE WHEN error_type = 'False Positive' THEN 1 ELSE 0 END)::numeric /
            NULLIF(SUM(CASE WHEN called_winner = true THEN 1 ELSE 0 END), 0) * 100
        , 1) as false_positive_rate_pct
    FROM experiments
    GROUP BY experiment_type
    ORDER BY false_positive_rate_pct DESC NULLS LAST;
"""
df2 = pd.read_sql(q2, conn)
df2.to_csv('results/2_false_positive_by_type.csv', index=False)
print(df2.to_string(index=False))
print(" Saved to results/2_false_positive_by_type.csv")

# ── QUERY 3: Peeking analysis ──────────────────────────
print("\nRunning Query 3: Peeking analysis...")
q3 = """
    SELECT
        peeked,
        COUNT(*) as total_experiments,
        SUM(CASE WHEN called_winner = true THEN 1 ELSE 0 END) as called_winners,
        SUM(CASE WHEN error_type = 'False Positive' THEN 1 ELSE 0 END) as false_positives,
        ROUND(
            SUM(CASE WHEN error_type = 'False Positive' THEN 1 ELSE 0 END)::numeric /
            NULLIF(SUM(CASE WHEN called_winner = true THEN 1 ELSE 0 END), 0) * 100
        , 1) as false_positive_rate_pct,
        ROUND(AVG(actual_duration_days), 1) as avg_duration_days,
        ROUND(AVG(actual_sample_size), 0) as avg_sample_size
    FROM experiments
    GROUP BY peeked;
"""
df3 = pd.read_sql(q3, conn)
df3.to_csv('results/3_peeking_analysis.csv', index=False)
print(df3.to_string(index=False))
print(" Saved to results/3_peeking_analysis.csv")

# ── CREATE VIEW: Decision Confidence ──────────────────
print("\nCreating Decision Confidence view...")
cursor = conn.cursor()
cursor.execute("DROP VIEW IF EXISTS decision_confidence;")
cursor.execute("""
    CREATE VIEW decision_confidence AS
    SELECT
        experiment_id,
        experiment_type,
        primary_metric,
        called_winner,
        true_winner,
        error_type,
        peeked,
        underpowered,
        p_hacking_risk,
        p_value,
        actual_sample_size,
        actual_duration_days,
        ROUND(
            100
            - (CASE WHEN peeked = true THEN 30 ELSE 0 END)
            - (CASE WHEN underpowered = true THEN 25 ELSE 0 END)
            - (CASE WHEN p_hacking_risk = true THEN 20 ELSE 0 END)
            - (CASE WHEN p_value BETWEEN 0.01 AND 0.05 THEN 10 ELSE 0 END)
        , 0) as decision_confidence_score,
        ROUND(
            (CASE WHEN peeked = true THEN 0.35 ELSE 0 END)
            + (CASE WHEN underpowered = true THEN 0.25 ELSE 0 END)
            + (CASE WHEN p_hacking_risk = true THEN 0.20 ELSE 0 END)
            + (CASE WHEN p_value BETWEEN 0.01 AND 0.05 THEN 0.15 ELSE 0 END)
        , 2) as false_positive_risk_index
    FROM experiments;
""")
conn.commit()
print(" Decision Confidence view created")

# ── QUERY 4: Decision Confidence Scores ───────────────
print("\nRunning Query 4: Decision Confidence Scores...")
q4 = """
    SELECT * FROM decision_confidence
    ORDER BY decision_confidence_score ASC;
"""
df4 = pd.read_sql(q4, conn)
df4.to_csv('results/4_decision_confidence.csv', index=False)
print(f"Total experiments scored: {len(df4)}")
print(df4.head(10).to_string(index=False))
print(" Saved to results/4_decision_confidence.csv")

# ── QUERY 5: Wasted Decision Rate ─────────────────────
print("\nRunning Query 5: Wasted Decision Rate...")
q5 = """
    SELECT
        ROUND(
            SUM(CASE WHEN called_winner = true AND decision_confidence_score < 50 THEN 1 ELSE 0 END)::numeric /
            NULLIF(SUM(CASE WHEN called_winner = true THEN 1 ELSE 0 END), 0) * 100
        , 1) as wasted_decision_rate_pct,
        SUM(CASE WHEN called_winner = true THEN 1 ELSE 0 END) as total_shipped_features,
        SUM(CASE WHEN called_winner = true AND decision_confidence_score < 50 THEN 1 ELSE 0 END) as poorly_validated_ships
    FROM decision_confidence;
"""
df5 = pd.read_sql(q5, conn)
df5.to_csv('results/5_wasted_decision_rate.csv', index=False)
print(df5.to_string(index=False))
print(" Saved to results/5_wasted_decision_rate.csv")

# ── QUERY 6: Year by year experiment health ────────────
print("\nRunning Query 6: Year by year experiment health...")
q6 = """
    SELECT
        EXTRACT(YEAR FROM e.start_date) as year,
        COUNT(*) as total_experiments,
        SUM(CASE WHEN e.error_type = 'False Positive' THEN 1 ELSE 0 END) as false_positives,
        ROUND(AVG(dc.decision_confidence_score), 1) as avg_confidence_score,
        SUM(CASE WHEN e.peeked = true THEN 1 ELSE 0 END) as peeked_count
    FROM experiments e
    JOIN decision_confidence dc USING (experiment_id)
    GROUP BY EXTRACT(YEAR FROM e.start_date)
    ORDER BY year;
"""
df6 = pd.read_sql(q6, conn)
df6.to_csv('results/6_yearly_health.csv', index=False)
print(df6.to_string(index=False))
print(" Saved to results/6_yearly_health.csv")

# ── CLOSE ──────────────────────────────────────────────
conn.close()
print("\n" + "="*50)
print("ALL QUERIES COMPLETE")
print("="*50)
print("\nFiles saved in results folder:")
print("  1_sanity_check.csv")
print("  2_false_positive_by_type.csv")
print("  3_peeking_analysis.csv")
print("  4_decision_confidence.csv")
print("  5_wasted_decision_rate.csv")
print("  6_yearly_health.csv")