from typing import Dict, List


def transactions_to_features(transactions: List[Dict]) -> Dict[str, float]:
    inflow = sum(t["amount"] for t in transactions if t["direction"] == "credit")
    outflow = sum(t["amount"] for t in transactions if t["direction"] == "debit")
    avg_inflow = inflow / max(1, len(transactions))
    avg_outflow = outflow / max(1, len(transactions))
    savings_rate = (inflow - outflow) / inflow if inflow else 0
    volatility = 0.25
    return {
        "avg_monthly_inflow": round(avg_inflow, 2),
        "avg_monthly_outflow": round(avg_outflow, 2),
        "savings_rate": round(savings_rate, 2),
        "volatility": round(volatility, 2),
    }

