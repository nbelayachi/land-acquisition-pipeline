#!/usr/bin/env python3
"""
Quick fix to check Address_Quality_Distribution sheet structure
"""
import pandas as pd

def check_quality_sheet():
    """Check the actual structure of Address_Quality_Distribution sheet"""
    try:
        excel_path = "Campaign4_Results.xlsx"
        quality_data = pd.read_excel(excel_path, sheet_name='Address_Quality_Distribution')
        
        print("=== ADDRESS_QUALITY_DISTRIBUTION SHEET ANALYSIS ===")
        print(f"Shape: {quality_data.shape}")
        print(f"Columns: {list(quality_data.columns)}")
        print(f"\nData preview:")
        print(quality_data.head())
        
        return quality_data
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    check_quality_sheet()