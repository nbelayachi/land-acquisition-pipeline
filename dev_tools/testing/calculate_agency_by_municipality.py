#!/usr/bin/env python3
"""
Agency_Final_Contacts by Municipality Calculator
===============================================

Calculates the correct Agency_Final_Contacts count for each municipality
in Campaign4 based on LOW confidence addresses.

Usage: Run this script to get exact values for Campaign_Summary correction
"""

import pandas as pd

def calculate_agency_by_municipality():
    """
    Calculate correct Agency_Final_Contacts by municipality
    """
    
    excel_path = r"C:\Projects\land-acquisition-pipeline\dev_tools\data_preparation\Campaign4_Results.xlsx"
    
    print("=" * 70)
    print("AGENCY_FINAL_CONTACTS BY MUNICIPALITY CALCULATOR")
    print("=" * 70)
    print()
    
    try:
        # Load validation data and current summary
        df_validation = pd.read_excel(excel_path, 'All_Validation_Ready')
        df_summary = pd.read_excel(excel_path, 'Campaign_Summary')
        
        print("CURRENT CAMPAIGN_SUMMARY VALUES:")
        print("=" * 40)
        
        # Show current values
        current_summary = df_summary[['comune', 'Agency_Final_Contacts']].copy()
        print(current_summary.to_string(index=False))
        current_total = df_summary['Agency_Final_Contacts'].sum()
        print(f"\nCurrent Total: {current_total}")
        
        print()
        print("CORRECT VALUES (LOW CONFIDENCE ADDRESSES):")
        print("=" * 50)
        
        # Calculate correct values
        low_confidence = df_validation[df_validation['Address_Confidence'] == 'LOW']
        
        if 'comune' in low_confidence.columns:
            # Count LOW confidence addresses by municipality
            correct_counts = low_confidence.groupby('comune').size().reset_index(name='Correct_Agency_Final_Contacts')
            
            print(correct_counts.to_string(index=False))
            correct_total = correct_counts['Correct_Agency_Final_Contacts'].sum()
            print(f"\nCorrect Total: {correct_total}")
            
            print()
            print("MUNICIPALITY-BY-MUNICIPALITY CORRECTIONS:")
            print("=" * 50)
            
            # Merge with current summary to show changes
            comparison = pd.merge(df_summary[['comune', 'Agency_Final_Contacts']], 
                                correct_counts, 
                                on='comune', 
                                how='left')
            
            # Fill missing values with 0
            comparison['Correct_Agency_Final_Contacts'] = comparison['Correct_Agency_Final_Contacts'].fillna(0).astype(int)
            
            # Calculate differences
            comparison['Difference'] = comparison['Correct_Agency_Final_Contacts'] - comparison['Agency_Final_Contacts']
            
            print("Municipality | Current | Correct | Difference")
            print("-" * 48)
            
            for idx, row in comparison.iterrows():
                municipality = row['comune']
                current = int(row['Agency_Final_Contacts'])
                correct = int(row['Correct_Agency_Final_Contacts'])
                diff = int(row['Difference'])
                
                status = "✅" if diff == 0 else "🔄"
                print(f"{municipality:<12} | {current:>7} | {correct:>7} | {diff:>10} {status}")
            
            print("-" * 48)
            print(f"{'TOTAL':<12} | {current_total:>7} | {correct_total:>7} | {correct_total - current_total:>10}")
            
            print()
            print("EXACT VALUES TO ENTER IN CAMPAIGN_SUMMARY:")
            print("=" * 50)
            
            # Provide exact values for manual entry
            print("Copy these values into your Campaign_Summary Agency_Final_Contacts column:")
            print()
            
            for idx, row in comparison.iterrows():
                municipality = row['comune']
                correct = int(row['Correct_Agency_Final_Contacts'])
                print(f"  {municipality}: {correct}")
            
            print()
            print("VERIFICATION:")
            print("=" * 20)
            print(f"✅ Sum should equal: {correct_total}")
            print(f"✅ Should match Enhanced_Funnel_Analysis Agency: 84")
            print(f"✅ Should match Address_Quality_Distribution LOW: 84")
            
            print()
            print("DETAILED BREAKDOWN BY MUNICIPALITY:")
            print("=" * 45)
            
            # Show detailed address breakdown
            for municipality in comparison['comune']:
                mun_data = low_confidence[low_confidence['comune'] == municipality]
                address_count = len(mun_data)
                unique_owners = mun_data['cf'].nunique()
                avg_addresses = address_count / unique_owners if unique_owners > 0 else 0
                
                print(f"{municipality}:")
                print(f"  📍 Addresses: {address_count}")
                print(f"  👥 Unique owners: {unique_owners}")
                print(f"  📊 Avg addresses/owner: {avg_addresses:.1f}")
                print()
        
        else:
            print("❌ 'comune' column not found in validation data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    calculate_agency_by_municipality()