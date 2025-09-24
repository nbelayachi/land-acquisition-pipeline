#!/usr/bin/env python3
"""
Counting Consistency Analysis for Campaign4
==========================================

This script checks if Direct_Mail_Final_Contacts and Agency_Final_Contacts 
count the same thing (addresses vs unique owners) for consistency.
"""

import pandas as pd
import numpy as np

def check_counting_consistency():
    """
    Check if metrics count addresses or unique owners consistently.
    """
    
    excel_path = r"C:\Projects\land-acquisition-pipeline\dev_tools\data_preparation\Campaign4_Results.xlsx"
    
    print("=" * 70)
    print("COUNTING CONSISTENCY ANALYSIS")
    print("=" * 70)
    print()
    
    try:
        # Load All_Validation_Ready
        df_validation = pd.read_excel(excel_path, 'All_Validation_Ready')
        
        print("DIRECT MAIL ANALYSIS (ULTRA_HIGH + HIGH + MEDIUM):")
        print("=" * 50)
        
        # Direct Mail: ULTRA_HIGH + HIGH + MEDIUM
        direct_mail_addresses = df_validation[df_validation['Address_Confidence'].isin(['ULTRA_HIGH', 'HIGH', 'MEDIUM'])]
        direct_mail_address_count = len(direct_mail_addresses)
        direct_mail_unique_owners = direct_mail_addresses['cf'].nunique()
        
        print(f"Direct Mail Addresses: {direct_mail_address_count}")
        print(f"Direct Mail Unique Owners: {direct_mail_unique_owners}")
        print(f"Average addresses per owner: {direct_mail_address_count / direct_mail_unique_owners:.2f}")
        print()
        
        print("AGENCY ANALYSIS (LOW confidence):")
        print("=" * 50)
        
        # Agency: LOW confidence
        agency_addresses = df_validation[df_validation['Address_Confidence'] == 'LOW']
        agency_address_count = len(agency_addresses)
        agency_unique_owners = agency_addresses['cf'].nunique()
        
        print(f"Agency Addresses: {agency_address_count}")
        print(f"Agency Unique Owners: {agency_unique_owners}")
        print(f"Average addresses per owner: {agency_address_count / agency_unique_owners:.2f}")
        print()
        
        print("CURRENT METRICS IN CAMPAIGN_SUMMARY:")
        print("=" * 50)
        
        df_summary = pd.read_excel(excel_path, 'Campaign_Summary')
        current_direct_mail = df_summary['Direct_Mail_Final_Contacts'].sum()
        current_agency = df_summary['Agency_Final_Contacts'].sum()
        
        print(f"Current Direct_Mail_Final_Contacts: {current_direct_mail}")
        print(f"Current Agency_Final_Contacts: {current_agency}")
        print(f"Current Total: {current_direct_mail + current_agency}")
        print()
        
        print("CONSISTENCY CHECK:")
        print("=" * 50)
        
        # Check what Direct_Mail_Final_Contacts is counting
        if current_direct_mail == direct_mail_address_count:
            direct_mail_counts = "ADDRESSES"
        elif current_direct_mail == direct_mail_unique_owners:
            direct_mail_counts = "UNIQUE OWNERS"
        else:
            direct_mail_counts = "UNKNOWN"
        
        # Check what Agency_Final_Contacts should count for consistency
        if direct_mail_counts == "ADDRESSES":
            recommended_agency = agency_address_count
            agency_should_count = "ADDRESSES"
        elif direct_mail_counts == "UNIQUE OWNERS":
            recommended_agency = agency_unique_owners
            agency_should_count = "UNIQUE OWNERS"
        else:
            recommended_agency = "UNKNOWN"
            agency_should_count = "UNKNOWN"
        
        print(f"✅ Direct_Mail_Final_Contacts ({current_direct_mail}) counts: {direct_mail_counts}")
        print(f"⚠️  Agency_Final_Contacts ({current_agency}) should count: {agency_should_count}")
        print(f"🎯 Recommended Agency_Final_Contacts: {recommended_agency}")
        print()
        
        print("FUNNEL ANALYSIS IMPACT:")
        print("=" * 50)
        
        df_funnel = pd.read_excel(excel_path, 'Enhanced_Funnel_Analysis')
        
        # Find current funnel values
        direct_mail_funnel = df_funnel[df_funnel['Stage'].str.contains('Direct Mail', case=False, na=False)]
        agency_funnel = df_funnel[df_funnel['Stage'].str.contains('Agency', case=False, na=False)]
        
        if not direct_mail_funnel.empty:
            current_funnel_direct = direct_mail_funnel['Count'].iloc[0]
            print(f"Current Funnel Direct Mail: {current_funnel_direct}")
            if current_funnel_direct == current_direct_mail:
                print("✅ Funnel matches Campaign_Summary for Direct Mail")
            else:
                print("❌ Funnel MISMATCH with Campaign_Summary for Direct Mail")
        
        if not agency_funnel.empty:
            current_funnel_agency = agency_funnel['Count'].iloc[0]
            print(f"Current Funnel Agency: {current_funnel_agency}")
            if current_funnel_agency == current_agency:
                print("✅ Funnel matches Campaign_Summary for Agency")
            else:
                print("❌ Funnel MISMATCH with Campaign_Summary for Agency")
        
        print()
        print("FINAL RECOMMENDATIONS:")
        print("=" * 50)
        
        if direct_mail_counts == "ADDRESSES":
            print("✅ RECOMMENDATION: Keep address-based counting")
            print(f"   Direct_Mail_Final_Contacts: {direct_mail_address_count} (addresses)")
            print(f"   Agency_Final_Contacts: {agency_address_count} (addresses)")
            print(f"   Total_Final_Contacts: {direct_mail_address_count + agency_address_count}")
            print(f"   Business Logic: Count all addresses requiring processing")
        else:
            print("✅ RECOMMENDATION: Use owner-based counting")
            print(f"   Direct_Mail_Final_Contacts: {direct_mail_unique_owners} (unique owners)")
            print(f"   Agency_Final_Contacts: {agency_unique_owners} (unique owners)")
            print(f"   Total_Final_Contacts: {direct_mail_unique_owners + agency_unique_owners}")
            print(f"   Business Logic: Count unique owners requiring contact")
        
        print()
        print("VALIDATION TOTAL:")
        print("=" * 50)
        total_validation_addresses = len(df_validation)
        total_validation_owners = df_validation['cf'].nunique()
        
        print(f"Total validation addresses: {total_validation_addresses}")
        print(f"Total validation unique owners: {total_validation_owners}")
        print(f"Expected total should match one of these values")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_counting_consistency()