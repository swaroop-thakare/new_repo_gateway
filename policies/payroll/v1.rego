package arealis.compliance.payroll.v1

import future.keywords.if
import future.keywords.contains
import data.arealis.compliance.common.v1 as common_rules

default allow := true

# --- PAYROLL VIOLATION RULES (Updated for actual input structure) ---

violations contains msg if {
    # Rule: PAN verification is mandatory for salary payments.
    # Check if PAN is provided in additional_fields
    pan_number := object.get(input.transaction.additional_fields, "pan_number", "")
    pan_number == ""
    msg := "PAN number is mandatory for salary payments."
}

violations contains msg if {
    # Rule: Employee ID is mandatory.
    employee_id := object.get(input.transaction.additional_fields, "employee_id", "")
    employee_id == ""
    msg := "Employee ID is mandatory for salary payments."
}

violations contains msg if {
    # Rule: PAN verification must be successful.
    pan_verification := object.get(input.verifications.pan, "verification", "")
    pan_verification != "success"
    msg := "PAN verification must be successful for salary payments."
}

violations contains msg if {
    # Rule: Bank account verification must be valid.
    bank_status := object.get(input.verifications.bank, "account_status", "")
    bank_status != "VALID"
    msg := "Bank account verification must be valid for salary payments."
}

violations contains msg if {
    # Rule: Aadhaar seeding status must be linked.
    aadhaar_status := object.get(input.verifications.pan.data, "aadhaar_seeding_status", "")
    aadhaar_status != "LINKED"
    msg := "Aadhaar must be linked for salary payments."
}

# Import and apply common rules
violations contains msg if {
    common_rules.violations[msg] with input as input
}

# The final decision
allow := false if {
    count(violations) > 0
}