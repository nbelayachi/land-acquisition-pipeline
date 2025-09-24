#!/usr/bin/env python3
"""
Investigate Mailing Count Discrepancy
558 Direct Mail Ready vs 303 Final Mailing List records
"""

import pandas as pd
import os

def investigate_counts():
    print("🔍 INVESTIGATING MAILING COUNT DISCREPANCY")
    print("=" * 60)
    
    excel_path = "data/Campaign4_Results.xlsx"
    
    if not os.path.exists(excel_path):
        print(f"❌ File not found: {excel_path}")
        return
    
    try:
        # Load relevant sheets
        campaign_summary = pd.read_excel(excel_path, sheet_name='Campaign_Summary')
        all_validation = pd.read_excel(excel_path, sheet_name='All_Validation_Ready')
        
        # Check if Final_Mailing_List exists
        try:
            final_mailing = pd.read_excel(excel_path, sheet_name='Final_Mailing_List')
            print(f"📋 Final_Mailing_List: {len(final_mailing)} records")
        except:
            print("📋 Final_Mailing_List sheet not found")
            final_mailing = None
        
        # Clean Campaign_Summary
        cs = campaign_summary
        clean_rows = cs['comune'].notna() & (cs['comune'] != '')
        cs_clean = cs[clean_rows].reset_index(drop=True)
        
        print(f"📊 Campaign_Summary: {len(cs_clean)} municipalities")
        print(f"📊 All_Validation_Ready: {len(all_validation)} addresses")
        
        # Analyze Direct Mail count calculation
        print("\n🔍 DIRECT MAIL COUNT ANALYSIS:")
        direct_mail_sum = cs_clean['Direct_Mail_Final_Contacts'].sum()
        print(f"   Campaign_Summary Direct_Mail sum: {direct_mail_sum}")
        
        # Count by confidence level in All_Validation_Ready
        if 'Address_Confidence' in all_validation.columns:
            confidence_counts = all_validation['Address_Confidence'].value_counts()
            print(f"   Address_Confidence distribution:")
            for level, count in confidence_counts.items():
                print(f"     {level}: {count}")
            
            # Direct mail ready = ULTRA_HIGH + HIGH + MEDIUM
            direct_mail_levels = ['ULTRA_HIGH', 'HIGH', 'MEDIUM']
            direct_mail_from_validation = all_validation[
                all_validation['Address_Confidence'].isin(direct_mail_levels)
            ]
            print(f"   Direct Mail Ready (from All_Validation_Ready): {len(direct_mail_from_validation)}")
        
        # Check routing channel
        if 'Routing_Channel' in all_validation.columns:
            routing_counts = all_validation['Routing_Channel'].value_counts()
            print(f"   Routing_Channel distribution:")
            for channel, count in routing_counts.items():
                print(f"     {channel}: {count}")
        
        # Analyze Final_Mailing_List if it exists
        if final_mailing is not None:
            print(f"\n📋 FINAL_MAILING_LIST ANALYSIS:")
            print(f"   Total records: {len(final_mailing)}")
            
            if 'cf' in final_mailing.columns:
                unique_owners = final_mailing['cf'].nunique()
                print(f"   Unique owners: {unique_owners}")
            
            if 'Address_Confidence' in final_mailing.columns:
                mailing_confidence = final_mailing['Address_Confidence'].value_counts()
                print(f"   Confidence distribution in mailing list:")
                for level, count in mailing_confidence.items():
                    print(f"     {level}: {count}")
            
            # Check for owner consolidation
            if 'cf' in final_mailing.columns:
                owner_addresses = final_mailing.groupby('cf').size()
                print(f"   Addresses per owner stats:")
                print(f"     Mean: {owner_addresses.mean():.1f}")
                print(f"     Max: {owner_addresses.max()}")
                print(f"     Owners with multiple addresses: {(owner_addresses > 1).sum()}")
        
        print("\n💡 POSSIBLE EXPLANATIONS:")
        print("1. Owner Consolidation: Multiple addresses per owner reduced to single mailing")
        print("2. Geographic Filtering: Some addresses excluded for operational reasons")
        print("3. Duplicate Removal: Same owner-address combinations consolidated")
        print("4. Business Rules: Additional filtering applied for final mailing list")
        
        # Recommend which count to use
        print("\n🎯 RECOMMENDATION:")
        if final_mailing is not None:
            print(f"   Use Final_Mailing_List count ({len(final_mailing)}) for actual mailing operations")
            print(f"   Use Direct_Mail_Ready count ({direct_mail_sum}) for pipeline efficiency metrics")
        else:
            print(f"   Use Direct_Mail_Ready count ({direct_mail_sum}) as primary metric")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_counts()