"""
csv_parser.py — Parses MoMo transaction messages from CSV into JSON

This script:
1. Reads momo_messages.csv (our raw transaction data)
2. Converts each row into a structured JSON object
3. Saves the result as transactions.json
4. Demonstrates Binary Search vs Dictionary Lookup (DSA comparison)
"""

import csv
import json
import os
import time


def parse_csv_to_json(csv_path, json_path):
    """
    Reads the CSV file line by line and builds a list of transaction dictionaries.
    Each row becomes one JSON object in the output file.
    """
    transactions = []

    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # Build a clean transaction object from each CSV row
            transaction = {
                "id": int(row["id"]),
                "sender": {
                    "phone": row["sender_phone"],
                    "name": row["sender_name"]
                },
                "receiver": {
                    "phone": row["receiver_phone"],
                    "name": row["receiver_name"]
                },
                "amount": float(row["amount"]),
                "fee": float(row["fee"]),
                "balance_after": float(row["balance_after"]),
                "category": row["category"],
                "tx_ref": row["tx_ref"],
                "timestamp": row["timestamp"],
                "description": row["description"]
            }
            transactions.append(transaction)

    # Write the list of dictionaries to a JSON file
    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(transactions, jsonfile, indent=2, ensure_ascii=False)

    return transactions


# ============================================================
# DSA SECTION: Comparing search algorithms
# ============================================================

def binary_search_by_amount(sorted_list, target_amount):
    """
    Binary Search — O(log n) time complexity
    Works only on a SORTED list. We sort transactions by amount first,
    then search for a specific amount using divide-and-conquer.
    """
    low = 0
    high = len(sorted_list) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_amount = sorted_list[mid]["amount"]

        if mid_amount == target_amount:
            return sorted_list[mid]  # Found it!
        elif mid_amount < target_amount:
            low = mid + 1  # Target is in the right half
        else:
            high = mid - 1  # Target is in the left half

    return None  # Not found


def dict_lookup_by_id(transactions_dict, txn_id):
    """
    Dictionary Lookup — O(1) time complexity
    Python dictionaries use hash tables under the hood,
    so finding an item by key is basically instant.
    """
    return transactions_dict.get(txn_id, None)


def linear_search_by_id(transactions_list, txn_id):
    """
    Linear Search — O(n) time complexity
    We go through every single item until we find the right one.
    This is the slowest approach but works on any list.
    """
    for txn in transactions_list:
        if txn["id"] == txn_id:
            return txn
    return None


def run_dsa_comparison(transactions):
    """
    Runs all three search methods and prints timing results side-by-side.
    This is how we demonstrate DSA concepts in a practical way.
    """
    print("\n" + "=" * 60)
    print("  DSA COMPARISON: Search Algorithm Performance")
    print("=" * 60)

    # --- Setup ---
    # Build a dictionary (hash map) keyed by transaction ID
    txn_dict = {}
    for txn in transactions:
        txn_dict[txn["id"]] = txn

    # Sort a copy of the list by amount for binary search
    sorted_by_amount = sorted(transactions, key=lambda x: x["amount"])

    # The ID and amount we'll search for
    search_id = transactions[-1]["id"]       # Last transaction
    search_amount = transactions[-1]["amount"]

    # --- Test 1: Linear Search by ID ---
    start = time.perf_counter()
    for _ in range(10000):  # Repeat many times to make timing measurable
        linear_search_by_id(transactions, search_id)
    linear_time = time.perf_counter() - start

    # --- Test 2: Dictionary Lookup by ID ---
    start = time.perf_counter()
    for _ in range(10000):
        dict_lookup_by_id(txn_dict, search_id)
    dict_time = time.perf_counter() - start

    # --- Test 3: Binary Search by Amount ---
    start = time.perf_counter()
    for _ in range(10000):
        binary_search_by_amount(sorted_by_amount, search_amount)
    binary_time = time.perf_counter() - start

    # --- Print Results ---
    print(f"\n  Searching for ID={search_id} and Amount={search_amount}")
    print(f"  Each test runs 10,000 iterations\n")
    print(f"  {'Method':<30} {'Time (seconds)':<15} {'Complexity'}")
    print(f"  {'-'*30} {'-'*15} {'-'*12}")
    print(f"  {'Linear Search (by ID)':<30} {linear_time:<15.6f} {'O(n)'}")
    print(f"  {'Dictionary Lookup (by ID)':<30} {dict_time:<15.6f} {'O(1)'}")
    print(f"  {'Binary Search (by amount)':<30} {binary_time:<15.6f} {'O(log n)'}")

    # Show which method won
    fastest = min(linear_time, dict_time, binary_time)
    if fastest == dict_time:
        winner = "Dictionary Lookup"
    elif fastest == binary_time:
        winner = "Binary Search"
    else:
        winner = "Linear Search"

    print(f"\n  Winner: {winner}")
    print("=" * 60)


# ============================================================
# MAIN — Run everything
# ============================================================

if __name__ == "__main__":
    # Figure out where our files are
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "momo_messages.csv")
    json_path = os.path.join(script_dir, "transactions.json")

    print("\n--- MoMo CSV Parser ---")
    print(f"Reading from: {csv_path}")

    if not os.path.exists(csv_path):
        print(f" Error: Could not find '{csv_path}'")
        print("Make sure momo_messages.csv is in the dsa/ folder.")
        exit(1)

    # Step 1: Parse CSV to JSON
    transactions = parse_csv_to_json(csv_path, json_path)
    print(f" Success! Parsed {len(transactions)} transactions")
    print(f"JSON saved to: {json_path}")

    # Step 2: Run DSA comparison
    run_dsa_comparison(transactions)

    print("\nDone! You can now start the API server with: python3 api/rest_api.py\n")
