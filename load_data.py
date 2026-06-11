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

cursor = conn.cursor()
print("Connected to PostgreSQL")

# Create experiments table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS experiments (
        experiment_id VARCHAR(10) PRIMARY KEY,
        experiment_type VARCHAR(100),
        primary_metric VARCHAR(100),
        start_date DATE,
        end_date DATE,
        planned_duration_days INT,
        actual_duration_days INT,
        planned_sample_size INT,
        actual_sample_size INT,
        peeked BOOLEAN,
        has_true_effect BOOLEAN,
        true_effect_size NUMERIC(10,4),
        observed_effect_size NUMERIC(10,4),
        p_value NUMERIC(10,4),
        called_winner BOOLEAN,
        true_winner BOOLEAN,
        error_type VARCHAR(50),
        underpowered BOOLEAN,
        metrics_tested INT,
        p_hacking_risk BOOLEAN
    )
""")

conn.commit()
print(" Table created")

# Load CSV
experiments_df = pd.read_csv('experiments.csv')

# Insert rows
for _, row in experiments_df.iterrows():
    cursor.execute("""
        INSERT INTO experiments VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (experiment_id) DO NOTHING
    """, tuple(row))

conn.commit()
print(f" Loaded {len(experiments_df)} experiments into PostgreSQL")

cursor.close()
conn.close()
print(" Done")