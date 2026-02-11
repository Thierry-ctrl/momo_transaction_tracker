"""
json_parser.py — Processes MoMo transaction messages from a raw JSON source

This script replaces the old CSV parser. It:
1. Reads `momo_messages.json` (our raw transaction source)
2. Processes and structures the data (simulating "parsing" logic)
3. Saves the result as `transactions.json` for the API to use
4. Demonstrates DSA concepts (Search Algorithms) on the parsed data
"""

import json
import os
import time


def parse_source_json(source_path, output_path):
    """
    Reads the raw source JSON and restructures it into the final API format.
    """
    print(f"Reading source data from: {source_path}")
    
    with open(source_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    transactions = []

    for item in raw_data:
        # Transform flat structure into nested structure (simulating parsing logic)
        transaction = {
            "id": int(item["id"]),
            "sender": {
                "phone": item["sender_phone"],
                "name": item["sender_name"]
            },
            "receiver": {
                "phone": item["receiver_phone"],
                "name": item["receiver_name"]
            },
            "amount": float(item["amount"]),
            "fee": float(item["fee"]),
            "balance_after": float(item["balance_after"]),
            "category": item["category"],
            "tx_ref": item["tx_ref"],
            "timestamp": item["timestamp"],
            "description": item["description"]
        }
        transactions.append(transaction)

    # Write the structured list to the final output file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(transactions, f, indent=2, ensure_ascii=False)

    return transactions


# ============================================================
# DSA SECTION: Comparing search algorithms
# ============================================================

def binary_search_by_amount(sorted_list, target_amount):
    """
    Binary Search — O(log n) time complexity
    Works only on a SORTED list.
    """
    low = 0
    high = len(sorted_list) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_amount = sorted_list[mid]["amount"]

        if mid_amount == target_amount:
            return sorted_list[mid]
        elif mid_amount < target_amount:
            low = mid + 1
        else:
            high = mid - 1

    return None


def dict_lookup_by_id(transactions_dict, txn_id):
    """
    Dictionary Lookup — O(1) time complexity
    """
    return transactions_dict.get(txn_id, None)


def linear_search_by_id(transactions_list, txn_id):
    """
    Linear Search — O(n) time complexity
    """
    for txn in transactions_list:
        if txn["id"] == txn_id:
            return txn
    return None


def run_dsa_comparison(transactions):
    """
    Runs all three search methods and prints timing results side-by-side.
    """
    print("\n" + "=" * 60)
    print("  DSA COMPARISON: Search Algorithm Performance")
    print("=" * 60)

    # Setup
    txn_dict = {txn["id"]: txn for txn in transactions}
    sorted_by_amount = sorted(transactions, key=lambda x: x["amount"])

    search_id = transactions[-1]["id"]
    search_amount = transactions[-1]["amount"]

    # Test 1: Linear Search
    start = time.perf_counter()
    for _ in range(10000):
        linear_search_by_id(transactions, search_id)
    linear_time = time.perf_counter() - start

    # Test 2: Dictionary Lookup
    start = time.perf_counter()
    for _ in range(10000):
        dict_lookup_by_id(txn_dict, search_id)
    dict_time = time.perf_counter() - start

    # Test 3: Binary Search
    start = time.perf_counter()
    for _ in range(10000):
        binary_search_by_amount(sorted_by_amount, search_amount)
    binary_time = time.perf_counter() - start

    # Results
    print(f"\n  Searching for ID={search_id} and Amount={search_amount}")
    print(f"  Each test runs 10,000 iterations\n")
    print(f"  {'Method':<30} {'Time (seconds)':<15} {'Complexity'}")
    print(f"  {'-'*30} {'-'*15} {'-'*12}")
    print(f"  {'Linear Search (by ID)':<30} {linear_time:<15.6f} {'O(n)'}")
    print(f"  {'Dictionary Lookup (by ID)':<30} {dict_time:<15.6f} {'O(1)'}")
    print(f"  {'Binary Search (by amount)':<30} {binary_time:<15.6f} {'O(log n)'}")

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
# MAIN
# ============================================================

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(script_dir, "momo_messages.json")
    output_path = os.path.join(script_dir, "transactions.json")

    if not os.path.exists(source_path):
        print(f" Error: Could not find '{source_path}'")
        exit(1)

    print("\n--- MoMo JSON Parser ---")
    
    # Run the parser
    transactions = parse_source_json(source_path, output_path)
    
    print(f" Success! Processed {len(transactions)} transactions")
    print(f" Output saved to: {output_path}")

    # Run DSA comparison
    run_dsa_comparison(transactions)

    print("\nDone! Start the API server with: python3 api/rest_api.py\n")
