#!/usr/bin/env python3

import re

# Test the IFSC codes from our test data
ifsc_codes = [
    "SBIN0567890",    # Vendor payment sender
    "PNB56789012",    # Vendor payment receiver
    "PNB56789012",    # Loan disbursement sender
    "HDFC0567890",    # Loan disbursement receiver
]

# The regex pattern from the Rego file
pattern = r"^[A-Z]{4}[0-9A-Z]{7}$"

print("Testing IFSC codes against regex pattern:")
print(f"Pattern: {pattern}")
print("=" * 50)

for ifsc in ifsc_codes:
    match = re.match(pattern, ifsc)
    print(f"IFSC: {ifsc}")
    print(f"Length: {len(ifsc)}")
    print(f"Match: {bool(match)}")
    print(f"Characters: {[c for c in ifsc]}")
    print("-" * 30)
