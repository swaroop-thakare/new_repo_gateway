package arealis.compliance.vendor_payment.v1

import future.keywords.if
import future.keywords.contains
import data.arealis.compliance.common.v1 as common_rules

default allow := true

# --- VENDOR PAYMENT VIOLATION RULES (Updated for actual input structure) ---

violations contains msg if {
    # Rule: PAN is required for payments > 50,000.
    amount := object.get(input.transaction, "amount", 0)
    amount > 50000
    pan_number := object.get(input.transaction.additional_fields, "pan_number", "")
    pan_number == ""
    msg := "PAN is mandatory for vendor payments over 50,000."
}

violations contains msg if {
    # Rule: GSTIN is required for payments > 25,000.
    amount := object.get(input.transaction, "amount", 0)
    amount > 25000
    gst_number := object.get(input.transaction.additional_fields, "gst_number", "")
    gst_number == ""
    msg := "GSTIN is mandatory for vendor payments over 25,000."
}

violations contains msg if {
    # Rule: Vendor code is mandatory.
    vendor_code := object.get(input.transaction.additional_fields, "vendor_code", "")
    vendor_code == ""
    msg := "Vendor code is mandatory for vendor payments."
}

violations contains msg if {
    # Rule: Invoice number is mandatory.
    invoice_number := object.get(input.transaction.additional_fields, "invoice_number", "")
    invoice_number == ""
    msg := "Invoice number is mandatory for vendor payments."
}

violations contains msg if {
    # Rule: Invoice date is mandatory.
    invoice_date := object.get(input.transaction.additional_fields, "invoice_date", "")
    invoice_date == ""
    msg := "Invoice date is mandatory for vendor payments."
}

violations contains msg if {
    # Rule: PAN verification must be successful.
    pan_verification := object.get(input.verifications.pan, "verification", "")
    pan_verification != "success"
    msg := "PAN verification must be successful for vendor payments."
}

violations contains msg if {
    # Rule: Bank account verification must be valid.
    bank_status := object.get(input.verifications.bank, "account_status", "")
    bank_status != "VALID"
    msg := "Bank account verification must be valid for vendor payments."
}

# Import and apply common rules
violations contains msg if {
    common_rules.violations[msg] with input as input
}

# The final decision
allow := false if {
    count(violations) > 0
}