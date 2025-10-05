package arealis.compliance.loan_disbursement.v1

import future.keywords.if
import future.keywords.contains
import data.arealis.compliance.common.v1 as common_rules

default allow := true

# --- LOAN DISBURSEMENT VIOLATION RULES (Updated for actual input structure) ---

violations contains msg if {
    # Rule: PAN is mandatory for all loans.
    # Check if PAN is provided in additional_fields
    pan_number := object.get(input.transaction.additional_fields, "pan_number", "")
    pan_number == ""
    msg := "PAN is a mandatory part of KYC for all loan disbursements."
}

violations contains msg if {
    # Rule: CIBIL check is required for loans > 50,000.
    amount := object.get(input.transaction, "amount", 0)
    amount > 50000
    cibil_checked := object.get(input.verifications, "cibil_check_performed", false)
    cibil_checked != true
    msg := "CIBIL check is mandatory for loan disbursements over 50,000."
}

violations contains msg if {
    # Rule: CIBIL score must be above the minimum threshold.
    cibil_score := object.get(input.verifications, "cibil_score", 0)
    cibil_score < 680
    msg := sprintf("CIBIL score of %v is below the required minimum of 680.", [cibil_score])
}

violations contains msg if {
    # Rule: Loan account number is mandatory.
    loan_account := object.get(input.transaction.additional_fields, "loan_account_number", "")
    loan_account == ""
    msg := "Loan account number is mandatory for loan disbursements."
}

violations contains msg if {
    # Rule: Loan type is mandatory.
    loan_type := object.get(input.transaction.additional_fields, "loan_type", "")
    loan_type == ""
    msg := "Loan type is mandatory for loan disbursements."
}

violations contains msg if {
    # Rule: Interest rate must be specified.
    interest_rate := object.get(input.transaction.additional_fields, "interest_rate", 0)
    interest_rate <= 0
    msg := "Interest rate must be specified for loan disbursements."
}

violations contains msg if {
    # Rule: Borrower verification status must be approved.
    borrower_status := object.get(input.transaction.additional_fields, "borrower_verification_status", "")
    borrower_status != "APPROVED"
    msg := "Borrower verification status must be approved for loan disbursements."
}

# Import and apply common rules
violations contains msg if {
    common_rules.violations[msg] with input as input
}

# The final decision
allow := false if {
    count(violations) > 0
}