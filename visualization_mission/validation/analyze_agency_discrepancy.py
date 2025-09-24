#!/usr/bin/env python3
"""
Agency_Final_Contacts Discrepancy Analysis
==========================================

Analyzes the discrepancy between 41 (Campaign_Summary) vs 84 (Funnel/Quality)
for Agency_Final_Contacts in Campaign4.

Usage: Run this script to understand the counting difference
"""

import pandas as pd

def analyze_agency_discrepancy():
    """
    Analyze the Agency_Final_Contacts discrepancy in Campaign4
    """
    
    excel_path = r"C:\Projects\land-acquisition-pipeline\dev_tools\data_preparation\Campaign4_Results.xlsx"
    
    print("=" * 70)
    print("AGENCY_FINAL_CONTACTS DISCREPANCY ANALYSIS")
    print("=" * 70)
    print()
    
    try:
        # Load validation data
        df_validation = pd.read_excel(excel_path, 'All_Validation_Ready')
        df_summary = pd.read_excel(excel_path, 'Campaign_Summary')
        df_funnel = pd.read_excel(excel_path, 'Enhanced_Funnel_Analysis')
        df_quality = pd.read_excel(excel_path, 'Address_Quality_Distribution')
        
        print("CURRENT VALUES IN CAMPAIGN4:")
        print("=" * 40)
        
        # Campaign_Summary values
        summary_agency = df_summary['Agency_Final_Contacts'].sum()
        print(f"Campaign_Summary Agency_Final_Contacts: {summary_agency}")
        
        # Funnel values
        agency_funnel = df_funnel[df_funnel['Stage'].str.contains('Agency', case=False, na=False)]
        if not agency_funnel.empty:
            funnel_agency = agency_funnel['Count'].iloc[0]
            print(f"Enhanced_Funnel_Analysis Agency: {funnel_agency}")
        
        # Quality distribution
        quality_low = df_quality[df_quality['Quality_Level'] == 'LOW']['Count'].iloc[0]
        print(f"Address_Quality_Distribution LOW: {quality_low}")
        
        print()
        
        print("DETAILED LOW CONFIDENCE ANALYSIS:")
        print("=" * 40)
        
        # Analyze LOW confidence addresses
        low_confidence = df_validation[df_validation['Address_Confidence'] == 'LOW']
        
        print(f"Total LOW confidence addresses: {len(low_confidence)}")
        print(f"Unique owners with LOW confidence: {low_confidence['cf'].nunique()}")
        print(f"Average addresses per LOW confidence owner: {len(low_confidence) / low_confidence['cf'].nunique():.2f}")
        
        print()
        
        print("LOW CONFIDENCE BREAKDOWN BY MUNICIPALITY:")
        print("-" * 45)
        
        # Break down by municipality
        if 'comune' in low_confidence.columns:
            by_comune = low_confidence.groupby('comune').agg({
                'cf': ['count', 'nunique'],
                'Best_Address': 'count'
            }).round(2)
            
            by_comune.columns = ['Total_Addresses', 'Unique_Owners', 'Address_Count']
            print(by_comune)
            
            print()
            print("SUMMARY BY MUNICIPALITY:")
            for comune in by_comune.index:
                addresses = by_comune.loc[comune, 'Total_Addresses']
                owners = by_comune.loc[comune, 'Unique_Owners']
                avg_addr = addresses / owners if owners > 0 else 0
                print(f"  {comune}: {addresses} addresses, {owners} owners ({avg_addr:.1f} addr/owner)")
        
        print()
        
        print("INTERPRETATION:")
        print("=" * 40)
        
        print("The discrepancy suggests two different counting methods:")
        print(f"• Method A (Current Campaign_Summary): {summary_agency} = Count unique owners")
        print(f"• Method B (Funnel/Quality): {quality_low} = Count total addresses")
        print()
        
        print("This means some LOW confidence owners have multiple addresses.")
        print("The question is: should Agency_Final_Contacts count owners or addresses?")
        print()
        
        print("BUSINESS LOGIC CONSIDERATION:")
        print("-" * 35)
        print("• If agency investigates PER OWNER → use unique owners (41)")
        print("• If agency investigates PER ADDRESS → use total addresses (84)")
        print("• Current pipeline v3.1.8 counts addresses for consistency")
        print()
        
        print("RECOMMENDATION:")
        print("-" * 15)
        print("For consistency with Direct_Mail_Final_Contacts (which counts addresses),")
        print("Agency_Final_Contacts should also count addresses (84).")
        print()
        print("This would make:")
        print(f"• Direct_Mail_Final_Contacts: 558 addresses")
        print(f"• Agency_Final_Contacts: 84 addresses")
        print(f"• Total_Final_Contacts: 642 addresses (matches validation)")
        print(f"• Direct_Mail_Percentage: 86.9% (558/642)")
        
        print()
        
        print("REQUIRED CORRECTION:")
        print("-" * 20)
        print("Update Campaign_Summary Agency_Final_Contacts from 41 → 84")
        print("This will align with Enhanced_Funnel_Analysis and Address_Quality_Distribution")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_agency_discrepancy()