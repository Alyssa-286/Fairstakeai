import csv
import random
from pathlib import Path

ROWS = 1000
OUT_FILE = Path(__file__).with_name("synthetic_fairscore_dataset.csv")
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


def generate_row() -> dict:
    avg_inflow = random.randint(8000, 30000)
    volatility = round(random.uniform(0.1, 0.6), 2)
    savings_rate = round(random.uniform(0.05, 0.35), 2)
    avg_outflow = int(avg_inflow * (1 - savings_rate) + random.randint(-500, 500))
    academic_score = round(random.uniform(6.0, 9.8), 1)
    part_time_income = random.choice([0, random.randint(2000, 8000)])
    emi_count = random.randint(0, 4)
    label_score = (
        45
        + (savings_rate * 120)
        - (volatility * 40)
        + ((avg_inflow - avg_outflow) / 500)
        + (academic_score * 2)
        + (part_time_income / 1500)
        - (emi_count * 3)
    )
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
    print(f"Generated dataset at {OUT_FILE} with {ROWS} rows.")


if __name__ == "__main__":
    main()


