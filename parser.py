import re


def _clean_value(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def _find_first(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def parse_bill(text):
    data = {}
    text = _clean_value(text or "")

    if not text:
        return data

    consumer_patterns = [
        r'Consumer\s*(?:No|Number)?\s*[:#]?\s*([A-Za-z0-9-]+)',
        r'Customer\s*(?:No|Number)?\s*[:#]?\s*([A-Za-z0-9-]+)',
    ]
    consumer_match = _find_first(text, consumer_patterns)
    if consumer_match:
        data["Consumer Number"] = consumer_match

    date_patterns = [
        r'(\d{2}[/-]\d{2}[/-]\d{4})',
        r'(\d{4}[/-]\d{2}[/-]\d{2})',
    ]
    date_match = _find_first(text, date_patterns)
    if date_match:
        data["Bill Date"] = date_match

    unit_patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:kWh|Units?)',
        r'Units\s*Consumed\s*[:#]?\s*(\d+(?:\.\d+)?)',
        r'Energy\s*Consumed\s*[:#]?\s*(\d+(?:\.\d+)?)',
    ]
    unit_match = _find_first(text, unit_patterns)
    if unit_match:
        data["Units"] = unit_match

    amount_patterns = [
        r'Total\s*Amount.*?(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)',
        r'Amount\s*Payable.*?(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)',
        r'Current\s*Bill.*?(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)',
        r'(?:₹|Rs\.?|INR)\s*([\d,]+(?:\.\d+)?)',
        r'\b([\d,]+(?:\.\d+)?)\b(?=\s*(?:INR|Rs|₹))',
    ]
    amount_match = _find_first(text, amount_patterns)
    if amount_match:
        data["Amount"] = amount_match.replace(",", "")

    return data