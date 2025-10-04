package arealis.compliance.routing.v1

import future.keywords.if

# Unified router that dispatches to policy packages based on transaction.payment_type
# Works with direct input format (no input wrapper)
# Supports aliases for similar payment types

# Default allow; will be overridden by downstream package result
default allow := true

# ------------------- LOAN DISBURSEMENT -------------------
allow := a if {
    payment_type := object.get(input.transaction, "payment_type", "")
    payment_type == "LOAN_DISBURSEMENT"
    a := data.arealis.compliance.loan_disbursement.v1.allow
}

allow := a if {
    payment_type := object.get(input.transaction, "payment_type", "")
    payment_type == "loan_disbursement"
    a := data.arealis.compliance.loan_disbursement.v1.allow
}

violations contains msg if {
    payment_type := object.get(input.transaction, "payment_type", "")
    payment_type == "LOAN_DISBURSEMENT"
    msg := data.arealis.compliance.loan_disbursement.v1.violations[_]
}

violations contains msg if {
    payment_type := object.get(input.transaction, "payment_type", "")
    payment_type == "loan_disbursement"
    msg := data.arealis.compliance.loan_disbursement.v1.violations[_]
}

# ------------------- PAYROLL / SALARY -------------------
allow := a if {
    payment_type := object.get(input.transaction, "payment_type", "")
    payment_type == "PAYROLL"
    a := data.arealis.compliance.payroll.v1.allow
}

allow := a if {
    payment_type := object.get(input.transaction, "payment_type", "")
    payment_type == "payroll"
    a := data.arealis.compliance.payroll.v1.allow
}

allow := a if {
    payment_type := object.get(input.transaction, "payment_type", "")
    payment_type == "SALARY"
    a := data.arealis.compliance.payroll.v1.allow
}

violations contains msg if {
    payment_type := object.get(input.transaction, "payment_type", "")
    payment_type == "PAYROLL"
    msg := data.arealis.compliance.payroll.v1.violations[_]
}

violations contains msg if {
    payment_type := object.get(input.transaction, "payment_type", "")
    payment_type == "payroll"
    msg := data.arealis.compliance.payroll.v1.violations[_]
}

violations contains msg if {
    payment_type := object.get(input.transaction, "payment_type", "")
    payment_type == "SALARY"
    msg := data.arealis.compliance.payroll.v1.violations[_]
}

# ------------------- VENDOR PAYMENT -------------------
allow := a if {
    payment_type := object.get(input.transaction, "payment_type", "")
    payment_type == "VENDOR_PAYMENT"
    a := data.arealis.compliance.vendor_payment.v1.allow
}

allow := a if {
    payment_type := object.get(input.transaction, "payment_type", "")
    payment_type == "vendor_payment"
    a := data.arealis.compliance.vendor_payment.v1.allow
}

violations contains msg if {
    payment_type := object.get(input.transaction, "payment_type", "")
    payment_type == "VENDOR_PAYMENT"
    msg := data.arealis.compliance.vendor_payment.v1.violations[_]
}

violations contains msg if {
    payment_type := object.get(input.transaction, "payment_type", "")
    payment_type == "vendor_payment"
    msg := data.arealis.compliance.vendor_payment.v1.violations[_]
}

# ------------------- UNKNOWN PAYMENT TYPE -------------------
violations contains msg if {
    # If the payment_type is not one of the supported ones, flag it
    payment_type := object.get(input.transaction, "payment_type", "")
    not payment_type == "LOAN_DISBURSEMENT"
    not payment_type == "loan_disbursement"
    not payment_type == "PAYROLL"
    not payment_type == "payroll"
    not payment_type == "SALARY"
    not payment_type == "VENDOR_PAYMENT"
    not payment_type == "vendor_payment"
    msg := sprintf("Unknown payment_type: %v", [payment_type])
}

# Final decision override: if any violations, do not allow
allow := false if {
    count(violations) > 0
}


