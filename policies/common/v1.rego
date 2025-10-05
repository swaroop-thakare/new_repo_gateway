package arealis.compliance.common.v1

import future.keywords.if
import future.keywords.contains

# --- COMMON VIOLATION RULES (Updated for new input structure) ---

violations contains msg if {
    # Rule: Enforce UPI per-transaction limit.
    method := object.get(input.transaction, "method", "")
    method == "UPI"
    amount := object.get(input.transaction, "amount", 0)
    amount > 500000
    msg := "UPI transaction amount exceeds the per-transaction limit of 500,000."
}

violations contains msg if {
    # Rule: Basic data quality check for IFSC code format.
    # Check receiver IFSC code format - very permissive pattern for testing
    receiver_ifsc := object.get(input.transaction.receiver, "ifsc_code", "")
    not regex.match("^[A-Z]{4}[0-9A-Z]{7}$", receiver_ifsc)
    msg := "Receiver IFSC code has an invalid format."
}

violations contains msg if {
    # Rule: Basic data quality check for sender IFSC code format.
    sender_ifsc := object.get(input.transaction.sender, "ifsc_code", "")
    not regex.match("^[A-Z]{4}[0-9A-Z]{7}$", sender_ifsc)
    msg := "Sender IFSC code has an invalid format."
}

violations contains msg if {
    # Rule: Amount must be positive.
    amount := object.get(input.transaction, "amount", 0)
    amount <= 0
    msg := "Transaction amount must be positive."
}

violations contains msg if {
    # Rule: Currency must be INR for Indian transactions.
    currency := object.get(input.transaction, "currency", "")
    currency != "INR"
    msg := "Currency must be INR for Indian transactions."
}