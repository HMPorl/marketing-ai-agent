#!/usr/bin/env python3
"""Test script for WordPress CSV integration"""

from tools.excel_product_handler import ExcelProductHandler

def test_csv_integration():
    print("=== Testing WordPress CSV Integration ===\n")
    
    # Test CSV detection
    print("1. CSV Detection:")
    handler = ExcelProductHandler()
    csv_info = handler.get_csv_info()
    print(f"   CSV File Found: {csv_info['file_exists']}")
    print(f"   File Path: {csv_info['csv_file_path']}")
    print(f"   Products: {csv_info['total_products']}")
    
    # Test data loading
    print("\n2. Data Loading:")
    df = handler.load_product_data()
    print(f"   Loaded {len(df)} products")
    
    # Test product lookup
    print("\n3. Product Lookup:")
    test_codes = ['01/STIHL123', '03/HILTI001', '12/HONDA567']
    
    for code in test_codes:
        product = handler.get_product_by_code(code)
        print(f"   {code}: {'✓' if product['found'] else '✗'} {product['title']}")
        if product['found']:
            print(f"      Brand: {product['brand']}, Category: {product['category']}")
    
    # Test all products
    print("\n4. All Products:")
    for i, row in df.iterrows():
        print(f"   - {row['stock_number']}: {row['title']} ({row['brand']})")
    
    print("\n=== Integration Test Complete ===")

if __name__ == "__main__":
    test_csv_integration()