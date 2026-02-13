#!/usr/bin/env python3
"""Test script for autocomplete search endpoints."""

import requests
import json
import sys
from typing import Optional

BASE_URL = "http://localhost:5000/api/analytics"

def test_drugs_search(query: str, limit: Optional[int] = None) -> dict:
    """Test the drugs search endpoint."""
    params = {"q": query}
    if limit:
        params["limit"] = limit
    
    print(f"\n{'='*60}")
    print(f"Testing: GET /drugs/search?q={query}" + (f"&limit={limit}" if limit else ""))
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/drugs/search", params=params)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        print(f"Error: {e}")
        return {}

def test_departments_search(query: str, limit: Optional[int] = None) -> dict:
    """Test the departments search endpoint."""
    params = {"q": query}
    if limit:
        params["limit"] = limit
    
    print(f"\n{'='*60}")
    print(f"Testing: GET /departments/search?q={query}" + (f"&limit={limit}" if limit else ""))
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/departments/search", params=params)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        print(f"Error: {e}")
        return {}

def validate_drugs_response(data: dict) -> bool:
    """Validate drugs search response structure."""
    if "data" not in data:
        print("❌ Missing 'data' in response")
        return False
    
    response_data = data["data"]
    required_fields = ["results", "query", "count", "limit"]
    
    for field in required_fields:
        if field not in response_data:
            print(f"❌ Missing '{field}' in response")
            return False
    
    results = response_data["results"]
    if not isinstance(results, list):
        print("❌ 'results' should be a list")
        return False
    
    for result in results:
        if "id" not in result or "drug_code" not in result or "name" not in result:
            print(f"❌ Result missing required fields: {result}")
            return False
    
    print("✅ Drugs search response structure is valid")
    return True

def validate_departments_response(data: dict) -> bool:
    """Validate departments search response structure."""
    if "data" not in data:
        print("❌ Missing 'data' in response")
        return False
    
    response_data = data["data"]
    required_fields = ["results", "query", "count", "limit"]
    
    for field in required_fields:
        if field not in response_data:
            print(f"❌ Missing '{field}' in response")
            return False
    
    results = response_data["results"]
    if not isinstance(results, list):
        print("❌ 'results' should be a list")
        return False
    
    for result in results:
        if "id" not in result or "department_name" not in result:
            print(f"❌ Result missing required fields: {result}")
            return False
    
    print("✅ Departments search response structure is valid")
    return True

def run_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("AUTOCOMPLETE SEARCH ENDPOINTS - TEST SUITE")
    print("="*60)
    
    # Test drug searches
    print("\n--- DRUG SEARCH TESTS ---")
    
    # Test with short query (should fail)
    print("\n1. Test with query < 3 characters (should fail)")
    data = test_drugs_search("pa")
    if data.get("error"):
        print("✅ Correctly rejected short query")
    else:
        print("❌ Should have rejected short query")
    
    # Test with minimum length query
    print("\n2. Test with query = 3 characters")
    data = test_drugs_search("par")
    if data:
        validate_drugs_response(data)
    
    # Test with limit parameter
    print("\n3. Test with custom limit")
    data = test_drugs_search("par", limit=5)
    if data:
        validate_drugs_response(data)
        if data.get("data", {}).get("limit") == 5:
            print("✅ Limit parameter respected")
        else:
            print("❌ Limit parameter not respected")
    
    # Test department searches
    print("\n--- DEPARTMENT SEARCH TESTS ---")
    
    # Test with missing query (should fail)
    print("\n4. Test without query parameter (should fail)")
    try:
        response = requests.get(f"{BASE_URL}/departments/search")
        if response.status_code != 200:
            print(f"✅ Correctly rejected missing query (status: {response.status_code})")
        else:
            print("❌ Should have rejected missing query")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with numeric department ID
    print("\n5. Test department search with numeric ID")
    data = test_departments_search("1")
    if data:
        validate_departments_response(data)
    
    # Test with string query
    print("\n6. Test department search with string query")
    data = test_departments_search("dept")
    if data:
        validate_departments_response(data)
    
    # Test department search with limit
    print("\n7. Test department search with custom limit")
    data = test_departments_search("1", limit=10)
    if data:
        validate_departments_response(data)
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("\n📌 Make sure the Flask server is running on http://localhost:5000")
    print("   Run: python run.py")
    print("\nProceeding with tests in 3 seconds...")
    
    import time
    time.sleep(3)
    
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)
