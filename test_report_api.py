#!/usr/bin/env python3
"""
Test script for the Cost Analysis Report Generation API.

Usage:
    python test_report_api.py [--host http://localhost:5000] [--format docx|pdf]

Requirements:
    - requests library
    - requests[security] for SSL support (optional)
"""

import requests
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path


class ReportAPITester:
    """Test Cost Analysis Report Generation API."""
    
    def __init__(self, base_url='http://localhost:5000'):
        """Initialize tester with base URL."""
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/analytics/cost-analysis/report"
        self.session = requests.Session()
    
    def test_basic_docx(self):
        """Test basic DOCX report generation."""
        print("\n" + "="*60)
        print("TEST 1: Basic DOCX Report Generation")
        print("="*60)
        
        params = {
            'start_date': '2019-01-01',
            'end_date': '2019-12-31',
            'format': 'docx'
        }
        
        print(f"Endpoint: GET {self.endpoint}")
        print(f"Parameters: {params}")
        print("Generating report...")
        
        try:
            response = self.session.get(self.endpoint, params=params)
            
            if response.status_code == 200:
                print(f"✅ Status: {response.status_code}")
                print(f"Content-Type: {response.headers.get('Content-Type')}")
                print(f"Content-Length: {len(response.content)} bytes")
                
                # Save file
                filename = f"report_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Report saved to: {filename}")
                return True
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_basic_pdf(self):
        """Test basic PDF report generation."""
        print("\n" + "="*60)
        print("TEST 2: Basic PDF Report Generation")
        print("="*60)
        
        params = {
            'start_date': '2019-01-01',
            'end_date': '2019-12-31',
            'format': 'pdf'
        }
        
        print(f"Endpoint: GET {self.endpoint}")
        print(f"Parameters: {params}")
        print("Generating report...")
        
        try:
            response = self.session.get(self.endpoint, params=params)
            
            if response.status_code == 200:
                print(f"✅ Status: {response.status_code}")
                print(f"Content-Type: {response.headers.get('Content-Type')}")
                print(f"Content-Length: {len(response.content)} bytes")
                
                # Save file
                filename = f"report_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Report saved to: {filename}")
                return True
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_with_filters(self):
        """Test report with department filters."""
        print("\n" + "="*60)
        print("TEST 3: Report with Department Filters")
        print("="*60)
        
        params = {
            'start_date': '2019-06-01',
            'end_date': '2019-12-31',
            'format': 'pdf',
            'departments': '1,2'
        }
        
        print(f"Endpoint: GET {self.endpoint}")
        print(f"Parameters: {params}")
        print("Generating filtered report...")
        
        try:
            response = self.session.get(self.endpoint, params=params)
            
            if response.status_code == 200:
                print(f"✅ Status: {response.status_code}")
                print(f"Content-Type: {response.headers.get('Content-Type')}")
                print(f"Content-Length: {len(response.content)} bytes")
                
                filename = f"report_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Report saved to: {filename}")
                return True
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_with_price_filters(self):
        """Test report with price range filters."""
        print("\n" + "="*60)
        print("TEST 4: Report with Price Range Filters")
        print("="*60)
        
        params = {
            'start_date': '2019-01-01',
            'end_date': '2019-12-31',
            'format': 'docx',
            'price_min': '50.0',
            'price_max': '500.0'
        }
        
        print(f"Endpoint: GET {self.endpoint}")
        print(f"Parameters: {params}")
        print("Generating report with price filters...")
        
        try:
            response = self.session.get(self.endpoint, params=params)
            
            if response.status_code == 200:
                print(f"✅ Status: {response.status_code}")
                print(f"Content-Type: {response.headers.get('Content-Type')}")
                print(f"Content-Length: {len(response.content)} bytes")
                
                filename = f"report_price_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Report saved to: {filename}")
                return True
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_invalid_format(self):
        """Test error handling for invalid format."""
        print("\n" + "="*60)
        print("TEST 5: Error Handling - Invalid Format")
        print("="*60)
        
        params = {
            'start_date': '2019-01-01',
            'end_date': '2019-12-31',
            'format': 'xlsx'  # Invalid format
        }
        
        print(f"Endpoint: GET {self.endpoint}")
        print(f"Parameters: {params}")
        print("Testing invalid format handling...")
        
        try:
            response = self.session.get(self.endpoint, params=params)
            
            if response.status_code == 400:
                print(f"✅ Status: {response.status_code} (Expected)")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"❌ Status: {response.status_code} (Expected 400)")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_missing_required_params(self):
        """Test error handling for missing required parameters."""
        print("\n" + "="*60)
        print("TEST 6: Error Handling - Missing Required Parameters")
        print("="*60)
        
        params = {
            'end_date': '2019-12-31'
            # Missing start_date
        }
        
        print(f"Endpoint: GET {self.endpoint}")
        print(f"Parameters: {params}")
        print("Testing missing parameter validation...")
        
        try:
            response = self.session.get(self.endpoint, params=params)
            
            if response.status_code == 400:
                print(f"✅ Status: {response.status_code} (Expected)")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"❌ Status: {response.status_code} (Expected 400)")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_complex_filters(self):
        """Test report with complex multi-filter query."""
        print("\n" + "="*60)
        print("TEST 7: Complex Multi-Filter Query")
        print("="*60)
        
        params = {
            'start_date': '2019-01-01',
            'end_date': '2019-12-31',
            'format': 'pdf',
            'departments': '1,2,3',
            'price_min': '10.0',
            'price_max': '1000.0',
            'drug_categories': '1,2'
        }
        
        print(f"Endpoint: GET {self.endpoint}")
        print(f"Parameters: {params}")
        print("Generating report with complex filters...")
        
        try:
            response = self.session.get(self.endpoint, params=params)
            
            if response.status_code == 200:
                print(f"✅ Status: {response.status_code}")
                print(f"Content-Type: {response.headers.get('Content-Type')}")
                print(f"Content-Length: {len(response.content)} bytes")
                
                filename = f"report_complex_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Report saved to: {filename}")
                return True
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests and generate report."""
        print("\n" + "#"*60)
        print("# Cost Analysis Report Generation API - Test Suite")
        print("#"*60)
        
        results = {
            'Basic DOCX': self.test_basic_docx(),
            'Basic PDF': self.test_basic_pdf(),
            'With Department Filters': self.test_with_filters(),
            'With Price Filters': self.test_with_price_filters(),
            'Invalid Format Error': self.test_invalid_format(),
            'Missing Parameters Error': self.test_missing_required_params(),
            'Complex Multi-Filter': self.test_complex_filters(),
        }
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print("="*60)
        print(f"Results: {passed}/{total} tests passed")
        print("="*60)
        
        return passed == total


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test Cost Analysis Report Generation API'
    )
    parser.add_argument(
        '--host',
        default='http://localhost:5000',
        help='Base URL of the API (default: http://localhost:5000)'
    )
    parser.add_argument(
        '--test',
        choices=['docx', 'pdf', 'filters', 'price', 'error', 'complex', 'all'],
        default='all',
        help='Specific test to run (default: all)'
    )
    
    args = parser.parse_args()
    
    print(f"\n🧪 Cost Analysis Report API Tester")
    print(f"🎯 Target: {args.host}")
    
    # Check if server is reachable
    try:
        response = requests.get(f"{args.host}/api/analytics/cost-analysis/report?start_date=2019-01-01&end_date=2019-01-02")
        # We expect an error (missing format or data), but at least the server should respond
        print(f"✅ Server is reachable")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {args.host}")
        print("Please make sure the Flask server is running:")
        print("  python run.py")
        return 1
    except Exception as e:
        print(f"⚠️  Server response: {str(e)}")
    
    tester = ReportAPITester(args.host)
    
    if args.test == 'all':
        success = tester.run_all_tests()
    elif args.test == 'docx':
        success = tester.test_basic_docx()
    elif args.test == 'pdf':
        success = tester.test_basic_pdf()
    elif args.test == 'filters':
        success = tester.test_with_filters()
    elif args.test == 'price':
        success = tester.test_with_price_filters()
    elif args.test == 'error':
        success = tester.test_invalid_format() and tester.test_missing_required_params()
    elif args.test == 'complex':
        success = tester.test_complex_filters()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
