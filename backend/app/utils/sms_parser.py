import re
from datetime import datetime
from typing import Dict, List, Tuple

TRANSACTION_REGEX = re.compile(
    r"Rs\.?\s?(?P<amount>[0-9,]+\.?\d{0,2})\s?(?P<direction>debited|credited).*?(?:on|dt)\s?(?P<date>\d{1,2}[A-Za-z]{3}\d{2}).*?(?:Ref|Ref No|UPI Ref)\s?(?P<ref>\d+).*?-?(?P<bank>[A-Z]{2,})",
    re.IGNORECASE,
)


def parse_sms_block(sms_text: str) -> Tuple[List[Dict], List[str]]:
    transactions: List[Dict] = []
    unparsed: List[str] = []
    for line in sms_text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = TRANSACTION_REGEX.search(line)
        if not match:
            unparsed.append(line)
            continue
        amount = float(match.group("amount").replace(",", ""))
        direction = "credit" if match.group("direction").lower() == "credited" else "debit"
        date_str = match.group("date")
        parsed_date = datetime.strptime(date_str, "%d%b%y").date()
        transactions.append(
            {
                "date": parsed_date.isoformat(),
                "amount": amount,
                "direction": direction,
                "ref": match.group("ref"),
                "bank": match.group("bank"),
                "raw": line,
            }
        )
    return transactions, unparsed


def compute_financial_metrics(transactions: List[Dict]) -> Dict:
    inflow = sum(t["amount"] for t in transactions if t["direction"] == "credit")
    outflow = sum(t["amount"] for t in transactions if t["direction"] == "debit")
    savings_rate = (inflow - outflow) / inflow if inflow else 0
    volatility = 0.3  # placeholder heuristics
    health_score = max(0, min(100, int(70 + (savings_rate - volatility) * 30)))
    return {
        "monthly_summary": {"inflow": round(inflow, 2), "outflow": round(outflow, 2), "volatility": round(volatility, 2)},
        "financial_health_score": health_score,
        "nudges": [
            "Track discretionary spends weekly.",
            "Automate savings to improve stability.",
        ],
    }

