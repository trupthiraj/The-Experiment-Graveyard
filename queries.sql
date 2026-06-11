-- ============================================
-- THE EXPERIMENT GRAVEYARD
-- SQL Analysis Queries
-- Author: Trupthi Raj
-- ============================================


-- --------------------------------------------
-- QUERY 1: Sanity check
-- --------------------------------------------
SELECT
    COUNT(*) as total_experiments,
    SUM(CASE WHEN called_winner = true THEN 1 ELSE 0 END) as called_winners,
    SUM(CASE WHEN true_winner = true THEN 1 ELSE 0 END) as true_winners,
    SUM(CASE WHEN error_type = 'False Positive' THEN 1 ELSE 0 END) as false_positives,
    SUM(CASE WHEN peeked = true THEN 1 ELSE 0 END) as peeked_experiments,
    SUM(CASE WHEN underpowered = true THEN 1 ELSE 0 END) as underpowered_experiments
FROM experiments;


-- --------------------------------------------
-- QUERY 2: False positive rate by experiment type
-- Which feature areas have the worst decision quality?
-- --------------------------------------------
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


-- --------------------------------------------
-- QUERY 3: Peeking analysis
-- How much does stopping early inflate false positives?
-- --------------------------------------------
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


-- --------------------------------------------
-- QUERY 4: Decision Confidence Score
-- Your proprietary metric — how valid was each decision?
-- --------------------------------------------
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
    -- Decision Confidence Score (0-100)
    -- Penalises peeking, underpowered tests, and p-hacking risk
    ROUND(
        100
        - (CASE WHEN peeked = true THEN 30 ELSE 0 END)
        - (CASE WHEN underpowered = true THEN 25 ELSE 0 END)
        - (CASE WHEN p_hacking_risk = true THEN 20 ELSE 0 END)
        - (CASE WHEN p_value BETWEEN 0.01 AND 0.05 THEN 10 ELSE 0 END)
    , 0) as decision_confidence_score,
    -- False Positive Risk Index
    ROUND(
        (CASE WHEN peeked = true THEN 0.35 ELSE 0 END)
        + (CASE WHEN underpowered = true THEN 0.25 ELSE 0 END)
        + (CASE WHEN p_hacking_risk = true THEN 0.20 ELSE 0 END)
        + (CASE WHEN p_value BETWEEN 0.01 AND 0.05 THEN 0.15 ELSE 0 END)
    , 2) as false_positive_risk_index
FROM experiments;


-- --------------------------------------------
-- QUERY 5: Wasted Decision Rate
-- What % of shipped features were based on invalid experiments?
-- --------------------------------------------
SELECT
    ROUND(
        SUM(CASE WHEN called_winner = true AND decision_confidence_score < 50 THEN 1 ELSE 0 END)::numeric /
        NULLIF(SUM(CASE WHEN called_winner = true THEN 1 ELSE 0 END), 0) * 100
    , 1) as wasted_decision_rate_pct,
    SUM(CASE WHEN called_winner = true THEN 1 ELSE 0 END) as total_shipped_features,
    SUM(CASE WHEN called_winner = true AND decision_confidence_score < 50 THEN 1 ELSE 0 END) as poorly_validated_ships
FROM decision_confidence;


-- --------------------------------------------
-- QUERY 6: Year by year experiment health
-- Did the company get better or worse over time?
-- --------------------------------------------
SELECT
    EXTRACT(YEAR FROM start_date) as year,
    COUNT(*) as total_experiments,
    SUM(CASE WHEN error_type = 'False Positive' THEN 1 ELSE 0 END) as false_positives,
    ROUND(AVG(decision_confidence_score), 1) as avg_confidence_score,
    SUM(CASE WHEN peeked = true THEN 1 ELSE 0 END) as peeked_count
FROM experiments
JOIN decision_confidence USING (experiment_id)
GROUP BY EXTRACT(YEAR FROM start_date)
ORDER BY year;