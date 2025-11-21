import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from enum import Enum

class AccountType(str, Enum):
    CARD = "CARD"
    WALLET = "WALLET"
    ACCOUNT = "ACCOUNT"

# Comprehensive regex patterns for transaction SMS parsing
class SMSPatterns:
    # Amount patterns
    AMOUNT = re.compile(r"(?:Rs\.?|INR|₹)\s?([0-9,]+\.?\d{0,2})", re.IGNORECASE)
    
    # Transaction type
    DEBIT = re.compile(r"debited|debited from|spent|withdrawn|purchase|paid", re.IGNORECASE)
    CREDIT = re.compile(r"credited|credited to|received|deposited", re.IGNORECASE)
    
    # Account patterns
    ACCOUNT_NUMBER = re.compile(r"(?:A/c|Account|a/c no\.?|XX)[\s:\-]*(\d{4,}|\*+\d{4}|XX\d{4})", re.IGNORECASE)
    CARD_NUMBER = re.compile(r"(?:card|Card No\.?|xx)[\s:\-]*(\d{4}|\*+\d{4})", re.IGNORECASE)
    
    # Balance patterns
    AVAILABLE_BALANCE = re.compile(r"(?:Avl Bal|Available Balance|Avl\.? ?Bal\.?|Balance)[\s:\-]*(?:Rs\.?|INR|₹)?\s?([0-9,]+\.?\d{0,2})", re.IGNORECASE)
    OUTSTANDING = re.compile(r"(?:Outstanding|O/s|Total Due)[\s:\-]*(?:Rs\.?|INR|₹)?\s?([0-9,]+\.?\d{0,2})", re.IGNORECASE)
    
    # Reference number
    REFERENCE = re.compile(r"(?:Ref|Ref No\.?|Reference|UPI Ref|NEFT Ref|IMPS Ref|UPI|UTR)[\s:\.#-]*([A-Za-z0-9]+)", re.IGNORECASE)
    
    # Merchant patterns (enhanced) - must start with letter to avoid matching phone numbers
    MERCHANT_AT = re.compile(r"(?:at|@)\s+([A-Za-z][A-Za-z0-9\s\-\.]+?)(?:\s*,|\s+UPI|\s+Ref|\s+on|\s+dated?|\s+\d{2}[-/]|\.|$)", re.IGNORECASE)
    MERCHANT_TO = re.compile(r"(?:to|toward|towards)\s+([A-Za-z][A-Za-z0-9\s\-\.]+?)(?:\s*,|\s+UPI|\s+Ref|\s+on|\s+via|\s+dated?|\s+\d{2}[-/]|\.|$)", re.IGNORECASE)
    MERCHANT_VIA = re.compile(r"(?:via\s+UPI|using)\s+(?:to\s+)?([A-Za-z][A-Za-z0-9\s\-\.]+?)(?:\s*,|\s+UPI|\s+Ref|\s+on|\s+dated?|\s+\d{2}[-/]|\.|$)", re.IGNORECASE)
    
    # Date patterns
    DATE_1 = re.compile(r"(?:on|dt|dated?)\s?(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", re.IGNORECASE)
    DATE_2 = re.compile(r"(?:on|dt)\s?(\d{1,2}[A-Za-z]{3}\d{2,4})", re.IGNORECASE)
    
    # Bank/Wallet identifiers
    BANK_CODE = re.compile(r"-\s?([A-Z]{2,})\s*$", re.IGNORECASE)
    WALLET = re.compile(r"(Paytm|Amazon Pay|PhonePe|Google Pay|GPay|Lazypay|Simpl|Mobikwik)", re.IGNORECASE)


def extract_transaction_info(sms_text: str) -> Dict:
    """
    Extract comprehensive transaction information from SMS.
    Returns dict with account, balance, transaction, merchant, date, bank info.
    """
    result = {
        "account": {
            "type": None,
            "number": None,
        },
        "balance": {
            "available": None,
            "outstanding": None,
        },
        "transaction": {
            "type": None,
            "amount": None,
            "referenceNo": None,
            "merchant": None,
        },
        "date": None,
        "bank": None,
    }
    
    # Extract amount
    amount_match = SMSPatterns.AMOUNT.search(sms_text)
    if amount_match:
        result["transaction"]["amount"] = amount_match.group(1).replace(",", "")
    
    # Extract transaction type
    if SMSPatterns.DEBIT.search(sms_text):
        result["transaction"]["type"] = "debit"
    elif SMSPatterns.CREDIT.search(sms_text):
        result["transaction"]["type"] = "credit"
    
    # Extract account info
    card_match = SMSPatterns.CARD_NUMBER.search(sms_text)
    account_match = SMSPatterns.ACCOUNT_NUMBER.search(sms_text)
    wallet_match = SMSPatterns.WALLET.search(sms_text)
    
    if wallet_match:
        result["account"]["type"] = AccountType.WALLET
        result["account"]["number"] = None
        result["bank"] = wallet_match.group(1)
    elif card_match:
        result["account"]["type"] = AccountType.CARD
        result["account"]["number"] = card_match.group(1).replace("*", "").replace("XX", "")
    elif account_match:
        result["account"]["type"] = AccountType.ACCOUNT
        result["account"]["number"] = account_match.group(1).replace("*", "").replace("XX", "")
    
    # Extract balance
    balance_match = SMSPatterns.AVAILABLE_BALANCE.search(sms_text)
    if balance_match:
        result["balance"]["available"] = balance_match.group(1).replace(",", "")
    
    outstanding_match = SMSPatterns.OUTSTANDING.search(sms_text)
    if outstanding_match:
        result["balance"]["outstanding"] = outstanding_match.group(1).replace(",", "")
    
    # Extract reference number
    ref_match = SMSPatterns.REFERENCE.search(sms_text)
    if ref_match:
        result["transaction"]["referenceNo"] = ref_match.group(1)
    
    # Extract merchant (try multiple patterns)
    merchant = None
    for pattern in [SMSPatterns.MERCHANT_AT, SMSPatterns.MERCHANT_TO, SMSPatterns.MERCHANT_VIA]:
        merchant_match = pattern.search(sms_text)
        if merchant_match:
            merchant = merchant_match.group(1).strip()
            # Clean up merchant name
            merchant = re.sub(r'\s+', ' ', merchant)  # Normalize whitespace
            merchant = merchant.rstrip('.-,')  # Remove trailing punctuation
            
            # Validate merchant name (must be at least 3 chars and not a phone number)
            if len(merchant) > 2 and not merchant.isdigit() and not re.match(r'^\d+$', merchant):
                result["transaction"]["merchant"] = merchant
                break
    
    # Extract date
    date_match = SMSPatterns.DATE_2.search(sms_text) or SMSPatterns.DATE_1.search(sms_text)
    if date_match:
        date_str = date_match.group(1)
        try:
            if "-" in date_str or "/" in date_str:
                # Format: 05-02-19 or 05/02/19
                for fmt in ["%d-%m-%y", "%d/%m/%y", "%d-%m-%Y", "%d/%m/%Y"]:
                    try:
                        parsed = datetime.strptime(date_str, fmt)
                        result["date"] = parsed.date().isoformat()
                        break
                    except:
                        continue
            else:
                # Format: 17Nov25
                if len(date_str) > 7:
                    parsed = datetime.strptime(date_str, "%d%b%Y")
                else:
                    parsed = datetime.strptime(date_str, "%d%b%y")
                result["date"] = parsed.date().isoformat()
        except:
            pass
    
    # Extract bank code
    if not result["bank"]:
        bank_match = SMSPatterns.BANK_CODE.search(sms_text)
        if bank_match:
            result["bank"] = bank_match.group(1)
    
    return result


def parse_sms_block(sms_text: str) -> Tuple[List[Dict], List[str]]:
    """
    Parse SMS block into structured transactions.
    Now includes: amount, type, date, ref, merchant, account, balance, bank.
    """
    transactions: List[Dict] = []
    unparsed: List[str] = []
    
    for line in sms_text.splitlines():
        line = line.strip()
        if not line or len(line) < 20:  # Skip very short lines
            continue
        
        # Extract comprehensive info
        info = extract_transaction_info(line)
        
        # Check if we got minimum required fields
        if info["transaction"]["amount"] and info["transaction"]["type"]:
            transactions.append({
                "date": info["date"] or "Unknown",
                "amount": float(info["transaction"]["amount"]),
                "direction": info["transaction"]["type"],
                "ref": info["transaction"]["referenceNo"] or "N/A",
                "merchant": info["transaction"]["merchant"] or "N/A",
                "account_type": info["account"]["type"] or "UNKNOWN",
                "account_number": info["account"]["number"] or "N/A",
                "balance": info["balance"]["available"] or "N/A",
                "bank": info["bank"] or "UNKNOWN",
                "raw": line,
            })
        else:
            unparsed.append(line)
    
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

