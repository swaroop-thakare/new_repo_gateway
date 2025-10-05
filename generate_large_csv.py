#!/usr/bin/env python3
"""
Generate a large CSV file with 1 million transactions for testing.
"""

import csv
import random
import string
from datetime import datetime, timedelta

def generate_random_name():
    """Generate a random Indian name."""
    first_names = [
        "Rajesh", "Priya", "Amit", "Sneha", "Vikram", "Kavya", "Arjun", "Ananya",
        "Rohit", "Pooja", "Suresh", "Meera", "Kiran", "Deepa", "Ravi", "Sunita",
        "Manoj", "Kavita", "Suresh", "Rekha", "Vijay", "Sarita", "Nitin", "Ritu",
        "Pankaj", "Neha", "Sandeep", "Poonam", "Rakesh", "Shilpa"
    ]
    last_names = [
        "Kumar", "Sharma", "Patel", "Gupta", "Singh", "Verma", "Agarwal", "Jain",
        "Malhotra", "Chopra", "Bansal", "Goyal", "Khanna", "Saxena", "Tiwari",
        "Reddy", "Nair", "Iyer", "Menon", "Pillai", "Rao", "Naidu", "Shetty"
    ]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_transaction():
    """Generate a single transaction."""
    amount = random.randint(1000, 1000000)  # 1K to 10L
    beneficiary = generate_random_name()
    reference = f"REF-{random.randint(100000, 999999)}"
    
    return {
        'beneficiary': beneficiary,
        'amount': amount,
        'reference': reference
    }

def generate_large_csv(filename, num_transactions=1000000):
    """Generate a large CSV file."""
    print(f"Generating {num_transactions:,} transactions...")
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['beneficiary', 'amount', 'reference']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Write transactions in batches
        batch_size = 10000
        for batch in range(0, num_transactions, batch_size):
            batch_end = min(batch + batch_size, num_transactions)
            print(f"Writing batch {batch//batch_size + 1}/{(num_transactions + batch_size - 1)//batch_size} ({batch_end:,} transactions)")
            
            for i in range(batch, batch_end):
                transaction = generate_transaction()
                writer.writerow(transaction)
    
    print(f"Generated {filename} with {num_transactions:,} transactions")

if __name__ == "__main__":
    # Generate 1 million transactions
    generate_large_csv("test_1million.csv", 1000000)
    
    # Also generate a smaller test file
    generate_large_csv("test_10k.csv", 10000)
