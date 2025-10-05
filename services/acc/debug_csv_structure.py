#!/usr/bin/env python3

import csv

def debug_csv_structure():
    """Debug the exact CSV structure"""
    
    print("🔍 Debugging CSV Structure")
    print("=" * 80)
    
    csv_file = "../../client_portal/test_final_correct.csv"
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            print(f"Total lines: {len(lines)}")
            print(f"Header line: {lines[0].strip()}")
            
            # Count columns in header
            header_columns = lines[0].strip().split(',')
            print(f"Header columns count: {len(header_columns)}")
            print(f"Header columns: {header_columns}")
            
            # Check each data row
            for i, line in enumerate(lines[1:], 1):
                if line.strip():
                    columns = line.strip().split(',')
                    print(f"\nRow {i}: {columns[1]} ({columns[0]})")
                    print(f"  Column count: {len(columns)}")
                    print(f"  Expected: {len(header_columns)}")
                    
                    if len(columns) != len(header_columns):
                        print(f"  ❌ MISMATCH! Row has {len(columns)} columns, header has {len(header_columns)}")
                        print(f"  Extra columns: {columns[len(header_columns):]}")
                    else:
                        print(f"  ✅ Column count matches")
                    
                    # Show critical fields for loan disbursement
                    if columns[0] == 'loan_disbursement':
                        print(f"  Critical fields:")
                        print(f"    pan_number (index 24): '{columns[24] if len(columns) > 24 else 'MISSING'}'")
                        print(f"    borrower_verification_status (index 32): '{columns[32] if len(columns) > 32 else 'MISSING'}'")
                        print(f"    loan_account_number (index 26): '{columns[26] if len(columns) > 26 else 'MISSING'}'")
                        print(f"    loan_type (index 27): '{columns[27] if len(columns) > 27 else 'MISSING'}'")
                    
                    if i >= 3:  # Only show first 3 rows
                        break
                        
    except FileNotFoundError:
        print(f"❌ CSV file not found: {csv_file}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_csv_structure()
