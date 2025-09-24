#!/usr/bin/env python3
"""
Data Type Diagnostic Script for Campaign4 Results
Analyzes the Agency_Final_Contacts column data types issue
"""

import pandas as pd
import os
import sys

def main():
    print("=" * 80)
    print("🔍 CAMPAIGN4 DATA TYPE DIAGNOSTIC")
    print("Analyzing Agency_Final_Contacts column data types")
    print("=" * 80)
    
    # Load the data
    excel_path = "data/Campaign4_Results.xlsx"
    
    if not os.path.exists(excel_path):
        print(f"❌ ERROR: Could not find {excel_path}")
        print("Please ensure the file exists in the expected location.")
        return
    
    try:
        # Load Campaign_Summary sheet
        campaign_summary = pd.read_excel(excel_path, sheet_name='Campaign_Summary')
        
        print(f"📊 Campaign_Summary shape: {campaign_summary.shape}")
        print(f"📊 Columns: {list(campaign_summary.columns)}")
        
        # Check if Agency_Final_Contacts column exists
        if 'Agency_Final_Contacts' in campaign_summary.columns:
            print("\n🔍 AGENCY_FINAL_CONTACTS ANALYSIS:")
            print(f"   Data type: {campaign_summary['Agency_Final_Contacts'].dtype}")
            print(f"   Unique values: {campaign_summary['Agency_Final_Contacts'].unique()}")
            print(f"   Value types: {[type(x) for x in campaign_summary['Agency_Final_Contacts']]}")
            
            # Check for mixed types
            mixed_types = set(type(x) for x in campaign_summary['Agency_Final_Contacts'])
            if len(mixed_types) > 1:
                print(f"   ⚠️  MIXED TYPES DETECTED: {mixed_types}")
                
                # Show problematic values
                for i, val in enumerate(campaign_summary['Agency_Final_Contacts']):
                    print(f"   Row {i}: {val} (type: {type(val)})")
            else:
                print(f"   ✅ Consistent type: {mixed_types.pop()}")
                
            # Try to convert to numeric
            try:
                numeric_col = pd.to_numeric(campaign_summary['Agency_Final_Contacts'], errors='coerce')
                print(f"   Numeric conversion result: {numeric_col.tolist()}")
                print(f"   NaN values after conversion: {numeric_col.isna().sum()}")
            except Exception as e:
                print(f"   ❌ Numeric conversion failed: {e}")
                
        else:
            print("❌ Agency_Final_Contacts column not found!")
            print(f"Available columns: {list(campaign_summary.columns)}")
            
        # Check other related columns
        related_columns = ['Direct_Mail_Final_Contacts', 'Total_Final_Contacts']
        for col in related_columns:
            if col in campaign_summary.columns:
                print(f"\n📊 {col}:")
                print(f"   Data type: {campaign_summary[col].dtype}")
                print(f"   Values: {campaign_summary[col].tolist()}")
                
        # Show full Campaign_Summary for context
        print("\n📋 FULL CAMPAIGN_SUMMARY:")
        print(campaign_summary.to_string())
        
    except Exception as e:
        print(f"❌ ERROR reading Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()