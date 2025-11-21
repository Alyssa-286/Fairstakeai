"""
Generate realistic synthetic data for FairScore training.
Uses realistic ranges and patterns observed from real financial data.
"""
import csv
import random
from pathlib import Path

ROWS = 1000
OUT_FILE = Path(__file__).with_name("realistic_fairscore_dataset.csv")
FIELDNAMES = [
    "avg_inflow",
    "avg_outflow",
    "savings_rate",
    "volatility",
    "academic_score",
    "part_time_income",
    "emi_count",
    "label_score",
]

# Realistic income distributions for Indian context
INCOME_SEGMENTS = [
    (8000, 15000, 0.30),   # Lower income: 30%
    (15000, 30000, 0.40),  # Middle income: 40%
    (30000, 60000, 0.20),  # Upper-middle: 20%
    (60000, 100000, 0.10), # High income: 10%
]

def select_income_range():
    """Select income range based on realistic distribution"""
    rand = random.random()
    cumulative = 0
    for min_income, max_income, probability in INCOME_SEGMENTS:
        cumulative += probability
        if rand <= cumulative:
            return min_income, max_income
    return INCOME_SEGMENTS[-1][:2]

def generate_row() -> dict:
    # Select realistic income range
    min_income, max_income = select_income_range()
    avg_inflow = random.randint(min_income, max_income)
    
    # Realistic savings rate (5-35%, with higher income → higher savings tendency)
    base_savings = 0.10 if avg_inflow < 20000 else 0.15 if avg_inflow < 40000 else 0.20
    savings_rate = round(base_savings + random.uniform(-0.05, 0.15), 2)
    savings_rate = max(0.05, min(0.35, savings_rate))
    
    # Volatility decreases with higher income (more stable)
    base_volatility = 0.40 if avg_inflow < 20000 else 0.30 if avg_inflow < 40000 else 0.20
    volatility = round(base_volatility + random.uniform(-0.10, 0.10), 2)
    volatility = max(0.10, min(0.60, volatility))
    
    # Calculate outflow based on savings rate with some noise
    avg_outflow = int(avg_inflow * (1 - savings_rate) + random.randint(-1000, 1000))
    avg_outflow = max(0, avg_outflow)
    
    # Academic score (6.0-9.8 CGPA scale)
    academic_score = round(random.uniform(6.0, 9.8), 1)
    
    # Part-time income (more common in students/lower income)
    if avg_inflow < 20000:
        part_time_income = random.choice([0, 0, random.randint(2000, 8000)])
    else:
        part_time_income = random.choice([0, 0, 0, random.randint(3000, 15000)])
    
    # EMI count (more common in middle/upper income)
    if avg_inflow < 15000:
        emi_count = random.choice([0, 0, 0, 1])
    elif avg_inflow < 30000:
        emi_count = random.choice([0, 1, 1, 2])
    else:
        emi_count = random.randint(0, 4)
    
    # Calculate score with realistic weightage
    label_score = (
        50  # Base score
        + (savings_rate * 100)  # +5 to +35
        - (volatility * 50)     # -5 to -30
        + ((avg_inflow - avg_outflow) / 800)  # Savings impact
        + (academic_score * 2.5)  # +15 to +24.5
        + (part_time_income / 2000)  # +0 to +7.5
        - (emi_count * 4)  # -0 to -16
    )
    
    # Realistic score bounds (300-850 like FICO, scaled to 30-95)
    label_score = max(30, min(95, int(label_score)))
    
    return {
        "avg_inflow": avg_inflow,
        "avg_outflow": avg_outflow,
        "savings_rate": savings_rate,
        "volatility": volatility,
        "academic_score": academic_score,
        "part_time_income": part_time_income,
        "emi_count": emi_count,
        "label_score": label_score,
    }


def main():
    with OUT_FILE.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        for _ in range(ROWS):
            writer.writerow(generate_row())
    print(f"✓ Generated realistic dataset at {OUT_FILE} with {ROWS} rows.")
    print(f"  Income distribution: 30% low, 40% middle, 20% upper-middle, 10% high")
    print(f"  Scores range: 30-95 (based on savings, volatility, income, academics)")


if __name__ == "__main__":
    main()
