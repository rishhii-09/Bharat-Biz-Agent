import re

def process_message(text: str):
    """
    Processes user message and extracts intent + entities
    """
    text = text.lower().strip()

    # -------------------------
    # CONFIRMATION INTENTS
    # -------------------------
    if text in ["yes", "haan", "ha", "confirm"]:
        return {
            "intent": "CONFIRM_ACTION",
            "confirmation": "YES"
        }

    if text in ["no", "nahi", "cancel"]:
        return {
            "intent": "CONFIRM_ACTION",
            "confirmation": "NO"
        }

    # -------------------------
    # CREATE INVOICE INTENT
    # -------------------------
    if "invoice" in text or "bill" in text:

        # Amount: ₹500 / rs 500 / 500
        amount_match = re.search(r"(₹\s*\d+|\d+\s*rs|\d+)", text)
        amount = None
        if amount_match:
            amount = int(re.findall(r"\d+", amount_match.group())[0])

        # Name: "ramesh ke naam"
        name_match = re.search(r"([a-zA-Z]+)\s+ke\s+naam", text)
        customer_name = name_match.group(1).capitalize() if name_match else None

        return {
            "intent": "CREATE_INVOICE",
            "customer_name": customer_name,
            "amount": amount
        }

    # -------------------------
    # FALLBACK
    # -------------------------
    return {
        "intent": "UNKNOWN"
    }
