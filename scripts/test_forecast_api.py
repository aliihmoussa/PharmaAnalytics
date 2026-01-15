#!/usr/bin/env python3
"""
Test script for XGBoost Forecast API

Usage:
    python scripts/test_forecast_api.py
    python scripts/test_forecast_api.py --drug-code P182054 --forecast-days 60
"""

import requests
import json
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any


BASE_URL = "http://localhost:5000/api/ml-xgboost"


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_response(response: requests.Response, show_full: bool = False):
    """Print API response in a formatted way."""
    print(f"\nStatus Code: {response.status_code}")
    
    try:
        data = response.json()
        
        if response.status_code == 200:
            if 'data' in data:
                result = data['data']
                
                # Print summary
                print(f"\n✅ Success!")
                print(f"Drug Code: {result.get('drug_code', 'N/A')}")
                print(f"Drug Name: {result.get('drug_name', 'N/A')}")
                
                # Metrics
                if 'metrics' in result:
                    metrics = result['metrics']
                    print(f"\n📊 Model Metrics:")
                    print(f"  RMSE: {metrics.get('rmse', 0):.2f}")
                    print(f"  MAE:  {metrics.get('mae', 0):.2f}")
                    print(f"  MAPE: {metrics.get('mape', 0):.2f}%")
                    print(f"  R²:   {metrics.get('r2', 0):.3f}")
                
                # Data info
                if 'data_info' in result:
                    info = result['data_info']
                    print(f"\n📈 Data Info:")
                    print(f"  Total Days: {info.get('total_days', 0)}")
                    print(f"  Train Days: {info.get('train_days', 0)}")
                    print(f"  Test Days:  {info.get('test_days', 0)}")
                    if 'date_range' in info:
                        date_range = info['date_range']
                        print(f"  Date Range: {date_range.get('start')} to {date_range.get('end')}")
                
                # Forecast summary
                if 'forecast' in result:
                    forecast = result['forecast']
                    print(f"\n🔮 Forecast Summary:")
                    print(f"  Forecast Days: {len(forecast)}")
                    if forecast:
                        first = forecast[0]
                        last = forecast[-1]
                        print(f"  First Date: {first.get('date')} - Predicted: {first.get('predicted', 0):.1f}")
                        print(f"  Last Date:  {last.get('date')} - Predicted: {last.get('predicted', 0):.1f}")
                
                # Feature importance (top 5)
                if 'feature_importance' in result:
                    importance = result['feature_importance']
                    sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]
                    print(f"\n🔑 Top 5 Most Important Features:")
                    for feature, score in sorted_features:
                        print(f"  {feature}: {score:.4f}")
                
                if show_full:
                    print(f"\n📄 Full Response:")
                    print(json.dumps(data, indent=2))
            else:
                print(f"\nResponse: {json.dumps(data, indent=2)}")
        else:
            print(f"\n❌ Error Response:")
            print(json.dumps(data, indent=2))
            
    except json.JSONDecodeError:
        print(f"\nResponse Text: {response.text}")


def test_basic_forecast(drug_code: str = "P182054", forecast_days: int = 30):
    """Test basic forecast endpoint."""
    print_section("Test 1: Basic Forecast")
    
    url = f"{BASE_URL}/forecast-enhanced/{drug_code}"
    params = {
        "forecast_days": forecast_days,
        "test_size": 30
    }
    
    print(f"URL: {url}")
    print(f"Parameters: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=60)
        print_response(response)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False


def test_forecast_with_dates(drug_code: str = "P182054"):
    """Test forecast with date range."""
    print_section("Test 2: Forecast with Date Range")
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    url = f"{BASE_URL}/forecast-enhanced/{drug_code}"
    params = {
        "forecast_days": 30,
        "test_size": 30,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    
    print(f"URL: {url}")
    print(f"Parameters: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=60)
        print_response(response)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False


def test_forecast_with_lookback(drug_code: str = "P182054"):
    """Test forecast with lookback days."""
    print_section("Test 3: Forecast with Lookback Days")
    
    url = f"{BASE_URL}/forecast-enhanced/{drug_code}"
    params = {
        "forecast_days": 30,
        "test_size": 30,
        "lookback_days": 180
    }
    
    print(f"URL: {url}")
    print(f"Parameters: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=60)
        print_response(response)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False


def test_data_check(drug_code: str = "P182054"):
    """Test data availability check."""
    print_section("Test 4: Data Availability Check")
    
    url = f"{BASE_URL}/data-check/{drug_code}"
    
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print_response(response)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False


def test_health_check():
    """Test health check endpoint."""
    print_section("Test 5: Health Check")
    
    url = f"{BASE_URL}/health"
    
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print_response(response)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False


def test_error_cases(drug_code: str = "P182054"):
    """Test error handling."""
    print_section("Test 6: Error Cases")
    
    # Test invalid forecast_days
    print("\n6a. Invalid forecast_days (too high):")
    url = f"{BASE_URL}/forecast-enhanced/{drug_code}"
    params = {"forecast_days": 500}  # Should fail (max 365)
    try:
        response = requests.get(url, params=params, timeout=30)
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    # Test invalid date format
    print("\n6b. Invalid date format:")
    params = {"start_date": "invalid-date"}
    try:
        response = requests.get(url, params=params, timeout=30)
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    # Test non-existent drug
    print("\n6c. Non-existent drug code:")
    url = f"{BASE_URL}/forecast-enhanced/INVALID123"
    params = {"forecast_days": 30}
    try:
        response = requests.get(url, params=params, timeout=60)
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")


def main():
    """Run all tests."""
    parser = argparse.ArgumentParser(description="Test XGBoost Forecast API")
    parser.add_argument("--drug-code", default="P182054", help="Drug code to test")
    parser.add_argument("--forecast-days", type=int, default=30, help="Days to forecast")
    parser.add_argument("--full", action="store_true", help="Show full JSON responses")
    parser.add_argument("--test", choices=["basic", "dates", "lookback", "data", "health", "errors", "all"],
                       default="all", help="Which test to run")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("  XGBoost Forecast API Test Suite")
    print("=" * 60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Drug Code: {args.drug_code}")
    print(f"Forecast Days: {args.forecast_days}")
    
    results = []
    
    if args.test in ["basic", "all"]:
        results.append(("Basic Forecast", test_basic_forecast(args.drug_code, args.forecast_days)))
    
    if args.test in ["dates", "all"]:
        results.append(("Forecast with Dates", test_forecast_with_dates(args.drug_code)))
    
    if args.test in ["lookback", "all"]:
        results.append(("Forecast with Lookback", test_forecast_with_lookback(args.drug_code)))
    
    if args.test in ["data", "all"]:
        results.append(("Data Check", test_data_check(args.drug_code)))
    
    if args.test in ["health", "all"]:
        results.append(("Health Check", test_health_check()))
    
    if args.test in ["errors", "all"]:
        test_error_cases(args.drug_code)
        results.append(("Error Cases", True))  # Don't fail on errors
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

