#!/usr/bin/env python3
"""
Agency_Final_Contacts Distribution Calculator
============================================

This script calculates how to distribute the corrected Agency_Final_Contacts
value (84) across the 6 municipalities in Campaign4_Results.xlsx.

Usage: Run this script in Spyder
"""

import pandas as pd
import numpy as np

def calculate_agency_distribution():
    """
    Calculate proportional distribution of Agency_Final_Contacts across municipalities.
    """
    
    excel_path = r"C:\Projects\land-acquisition-pipeline\dev_tools\data_preparation\Campaign4_Results.xlsx"
    
    print("=" * 70)
    print("AGENCY_FINAL_CONTACTS DISTRIBUTION CALCULATOR")
    print("=" * 70)
    print()
    
    try:
        # Load Campaign_Summary and All_Validation_Ready
        df_summary = pd.read_excel(excel_path, 'Campaign_Summary')
        df_validation = pd.read_excel(excel_path, 'All_Validation_Ready')
        
        print("Current Campaign_Summary Agency_Final_Contacts:")
        print(df_summary[['comune', 'Agency_Final_Contacts']].to_string(index=False))
        print(f"\nCurrent Total: {df_summary['Agency_Final_Contacts'].sum()}")
        print(f"Target Total: 84")
        print()
        
        # Method 1: Proportional Distribution (recommended)
        print("=" * 50)
        print("METHOD 1: PROPORTIONAL DISTRIBUTION")
        print("=" * 50)
        
        current_total = df_summary['Agency_Final_Contacts'].sum()
        target_total = 84
        scaling_factor = target_total / current_total
        
        print(f"Scaling factor: {scaling_factor:.4f}")
        print()
        
        # Calculate proportional values
        proportional_values = []
        for idx, row in df_summary.iterrows():
            current_value = row['Agency_Final_Contacts']
            new_value = int(round(current_value * scaling_factor))
            proportional_values.append(new_value)
            print(f"{row['comune']}: {current_value} → {new_value}")
        
        # Check if sum matches target
        proportional_sum = sum(proportional_values)
        print(f"\nProportional sum: {proportional_sum}")
        
        if proportional_sum != target_total:
            print(f"⚠️  Need to adjust by {target_total - proportional_sum}")
            
            # Adjust the largest values first
            if proportional_sum < target_total:
                diff = target_total - proportional_sum
                print(f"Adding {diff} to largest municipality")
                max_idx = proportional_values.index(max(proportional_values))
                proportional_values[max_idx] += diff
            elif proportional_sum > target_total:
                diff = proportional_sum - target_total
                print(f"Subtracting {diff} from largest municipality")
                max_idx = proportional_values.index(max(proportional_values))
                proportional_values[max_idx] -= diff
        
        print("\nFINAL PROPORTIONAL DISTRIBUTION:")
        for i, (idx, row) in enumerate(df_summary.iterrows()):
            print(f"{row['comune']}: {proportional_values[i]}")
        print(f"Total: {sum(proportional_values)}")
        
        # Method 2: Actual LOW confidence count by municipality
        print()
        print("=" * 50)
        print("METHOD 2: ACTUAL LOW CONFIDENCE BY MUNICIPALITY")
        print("=" * 50)
        
        if 'comune' in df_validation.columns and 'Address_Confidence' in df_validation.columns:
            # Count LOW confidence addresses by municipality
            low_by_comune = df_validation[df_validation['Address_Confidence'] == 'LOW'].groupby('comune').size()
            
            print("Actual LOW confidence addresses by municipality:")
            actual_values = []
            for idx, row in df_summary.iterrows():
                comune = row['comune']
                low_count = low_by_comune.get(comune, 0)
                actual_values.append(low_count)
                print(f"{comune}: {low_count}")
            
            actual_sum = sum(actual_values)
            print(f"\nActual sum: {actual_sum}")
            
            if actual_sum == target_total:
                print("✅ Perfect match! Use these values:")
                print()
                print("COPY THESE VALUES TO YOUR EXCEL:")
                for i, (idx, row) in enumerate(df_summary.iterrows()):
                    print(f"{row['comune']}: {actual_values[i]}")
            else:
                print(f"❌ Mismatch. Expected {target_total}, got {actual_sum}")
        else:
            print("❌ Cannot calculate - missing required columns")
        
        # Method 3: Excel formulas for manual calculation
        print()
        print("=" * 50)
        print("METHOD 3: EXCEL FORMULAS")
        print("=" * 50)
        
        print("If you want to use Excel formulas, use this approach:")
        print("1. Create a helper column with current proportions")
        print("2. Multiply by the scaling factor")
        print("3. Round to nearest integer")
        print()
        print(f"Scaling factor: {scaling_factor:.6f}")
        print("Formula: =ROUND(old_value * 0.518519, 0)")
        
        print()
        print("=" * 70)
        print("RECOMMENDATION")
        print("=" * 70)
        print("Use METHOD 2 (Actual LOW confidence by municipality) if the sum equals 84.")
        print("Otherwise, use METHOD 1 (Proportional distribution) with manual adjustments.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    calculate_agency_distribution()