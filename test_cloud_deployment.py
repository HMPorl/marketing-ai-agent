#!/usr/bin/env python3
"""
Test script to verify cloud deployment readiness
"""

import os
import sys

def test_imports():
    """Test all required imports"""
    print("=== TESTING IMPORTS ===")
    
    try:
        import streamlit as st
        print("✓ streamlit")
    except ImportError as e:
        print(f"✗ streamlit: {e}")
        return False
        
    try:
        import pandas as pd
        print("✓ pandas")
    except ImportError as e:
        print(f"✗ pandas: {e}")
        return False
        
    try:
        import requests
        print("✓ requests")
    except ImportError as e:
        print(f"✗ requests: {e}")
        return False
        
    try:
        from bs4 import BeautifulSoup
        print("✓ beautifulsoup4")
    except ImportError as e:
        print(f"✗ beautifulsoup4: {e}")
        return False
        
    return True

def test_project_imports():
    """Test project-specific imports"""
    print("\n=== TESTING PROJECT IMPORTS ===")
    
    try:
        from tools.excel_product_handler import ExcelProductHandler
        print("✓ ExcelProductHandler")
    except ImportError as e:
        print(f"✗ ExcelProductHandler: {e}")
        return False
        
    try:
        from agents.product_description_generator import ProductDescriptionGenerator
        print("✓ ProductDescriptionGenerator")
    except ImportError as e:
        print(f"✗ ProductDescriptionGenerator: {e}")
        return False
        
    return True

def test_data_availability():
    """Test if data files are accessible"""
    print("\n=== TESTING DATA AVAILABILITY ===")
    
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")
    
    # Test different possible data paths
    possible_paths = [
        "./data/product_data",
        "data/product_data",
        os.path.join(os.path.dirname(__file__), "data", "product_data"),
        os.path.join(current_dir, "data", "product_data")
    ]
    
    for path in possible_paths:
        exists = os.path.exists(path)
        print(f"Path '{path}' exists: {exists}")
        
        if exists:
            try:
                files = os.listdir(path)
                csv_files = [f for f in files if f.endswith('.csv')]
                print(f"  CSV files: {csv_files}")
                
                if csv_files:
                    return True, path, csv_files
            except Exception as e:
                print(f"  Error listing files: {e}")
    
    return False, None, []

def test_excel_handler():
    """Test ExcelProductHandler initialization"""
    print("\n=== TESTING EXCEL HANDLER ===")
    
    try:
        from tools.excel_product_handler import ExcelProductHandler
        
        handler = ExcelProductHandler()
        print(f"Handler initialized: {handler is not None}")
        print(f"Data folder path: {handler.data_folder_path}")
        print(f"CSV file path: {handler.csv_file_path}")
        print(f"Has data: {handler.has_data}")
        
        if handler.has_data:
            print(f"Data summary: {handler.data_summary}")
            
            # Test product lookup
            test_product = handler.get_product_by_code('03/185')
            print(f"Test product found: {test_product.get('found', False) if test_product else False}")
            
            return True
        else:
            print("No data loaded")
            return False
            
    except Exception as e:
        print(f"Error testing handler: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    print("CLOUD DEPLOYMENT READINESS TEST")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ FAILED: Basic imports not working")
        return False
        
    if not test_project_imports():
        print("\n❌ FAILED: Project imports not working")
        return False
    
    # Test data availability
    data_available, data_path, csv_files = test_data_availability()
    if not data_available:
        print("\n⚠️ WARNING: No CSV data files found")
        print("The app will run but product generation won't work")
    else:
        print(f"\n✓ Data available at: {data_path}")
        print(f"✓ CSV files: {csv_files}")
    
    # Test handler
    if not test_excel_handler():
        print("\n❌ FAILED: ExcelProductHandler not working")
        return False
    
    print("\n" + "=" * 50)
    print("✅ DEPLOYMENT READINESS: PASSED")
    print("The app should work in Streamlit Cloud")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)