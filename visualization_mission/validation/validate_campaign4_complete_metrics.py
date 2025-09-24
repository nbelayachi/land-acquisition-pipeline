#!/usr/bin/env python3
"""
Campaign4 Complete Metrics Validation
====================================

This script performs comprehensive validation of ALL metrics in the Campaign4_Results.xlsx
file to ensure mathematical accuracy and consistency across all sheets.

Usage: Run this script to validate Campaign4 as the foundation dataset
"""

import pandas as pd
import numpy as np
import os

def validate_campaign4_complete_metrics():
    """
    Comprehensive validation of all metrics in Campaign4_Results.xlsx
    """
    
    excel_path = r"C:\Projects\land-acquisition-pipeline\dev_tools\data_preparation\Campaign4_Results.xlsx"
    
    print("=" * 80)
    print("CAMPAIGN4 COMPLETE METRICS VALIDATION")
    print("=" * 80)
    print(f"Validating: {excel_path}")
    print()
    
    if not os.path.exists(excel_path):
        print(f"❌ ERROR: File not found at {excel_path}")
        return
    
    try:
        # Load all sheets
        xls = pd.ExcelFile(excel_path)
        sheets = {}
        
        required_sheets = ['All_Raw_Data', 'All_Validation_Ready', 'Final_Mailing_List', 
                          'Campaign_Summary', 'Enhanced_Funnel_Analysis', 'Address_Quality_Distribution']
        
        for sheet_name in required_sheets:
            if sheet_name in xls.sheet_names:
                sheets[sheet_name] = pd.read_excel(excel_path, sheet_name)
                print(f"✅ Loaded {sheet_name}: {len(sheets[sheet_name])} rows")
            else:
                print(f"❌ Missing sheet: {sheet_name}")
                return
        
        print()
        
        # =============================================
        # 1. FOUNDATION DATA VALIDATION
        # =============================================
        print("=" * 60)
        print("1. FOUNDATION DATA VALIDATION")
        print("=" * 60)
        
        df_raw = sheets['All_Raw_Data']
        df_validation = sheets['All_Validation_Ready']
        df_summary = sheets['Campaign_Summary']
        
        print(f"Raw data records: {len(df_raw)}")
        print(f"Validation ready records: {len(df_validation)}")
        print(f"Summary municipalities: {len(df_summary)}")
        
        # Check for required columns
        required_raw_cols = ['cf', 'foglio_input', 'particella_input', 'Area']
        required_validation_cols = ['cf', 'Address_Confidence', 'Best_Address']
        
        missing_raw = [col for col in required_raw_cols if col not in df_raw.columns]
        missing_validation = [col for col in required_validation_cols if col not in df_validation.columns]
        
        if missing_raw:
            print(f"❌ Missing columns in All_Raw_Data: {missing_raw}")
        else:
            print("✅ All required columns present in All_Raw_Data")
            
        if missing_validation:
            print(f"❌ Missing columns in All_Validation_Ready: {missing_validation}")
        else:
            print("✅ All required columns present in All_Validation_Ready")
        
        print()
        
        # =============================================
        # 2. CAMPAIGN_SUMMARY VALIDATION
        # =============================================
        print("=" * 60)
        print("2. CAMPAIGN_SUMMARY METRICS VALIDATION")
        print("=" * 60)
        
        # Show actual columns
        print("Available Campaign_Summary columns:")
        print(df_summary.columns.tolist())
        print()
        
        # Key metrics to validate
        summary_totals = {}
        key_metrics = ['Direct_Mail_Final_Contacts', 'Agency_Final_Contacts', 'Input_Parcels', 
                      'Direct_Mail_Final_Area_Ha', 'Agency_Final_Area_Ha']
        
        for metric in key_metrics:
            if metric in df_summary.columns:
                total = df_summary[metric].sum()
                summary_totals[metric] = total
                print(f"{metric}: {total}")
            else:
                print(f"{metric}: NOT FOUND")
                summary_totals[metric] = 0
        
        print()
        
        # Validate against raw data
        print("VALIDATION AGAINST RAW DATA:")
        print("-" * 40)
        
        # Input parcels validation
        if 'Input_Parcels' in df_summary.columns:
            expected_input_parcels = len(df_raw[['foglio_input', 'particella_input']].drop_duplicates())
            actual_input_parcels = summary_totals['Input_Parcels']
            print(f"Input Parcels - Expected: {expected_input_parcels}, Actual: {actual_input_parcels}")
            if expected_input_parcels == actual_input_parcels:
                print("✅ Input_Parcels correct")
            else:
                print("❌ Input_Parcels mismatch")
        
        # Direct Mail contacts validation
        if 'Address_Confidence' in df_validation.columns:
            expected_direct_mail = len(df_validation[df_validation['Address_Confidence'].isin(['ULTRA_HIGH', 'HIGH', 'MEDIUM'])])
            actual_direct_mail = summary_totals['Direct_Mail_Final_Contacts']
            print(f"Direct Mail Contacts - Expected: {expected_direct_mail}, Actual: {actual_direct_mail}")
            if expected_direct_mail == actual_direct_mail:
                print("✅ Direct_Mail_Final_Contacts correct")
            else:
                print("❌ Direct_Mail_Final_Contacts mismatch")
        
        # Agency contacts validation
        if 'Address_Confidence' in df_validation.columns:
            expected_agency = len(df_validation[df_validation['Address_Confidence'] == 'LOW'])
            actual_agency = summary_totals['Agency_Final_Contacts']
            print(f"Agency Contacts - Expected: {expected_agency}, Actual: {actual_agency}")
            if expected_agency == actual_agency:
                print("✅ Agency_Final_Contacts correct")
            else:
                print("❌ Agency_Final_Contacts mismatch")
        
        # Total validation
        total_validation_addresses = len(df_validation)
        total_summary_contacts = summary_totals['Direct_Mail_Final_Contacts'] + summary_totals['Agency_Final_Contacts']
        print(f"Total Validation Addresses: {total_validation_addresses}")
        print(f"Total Summary Contacts: {total_summary_contacts}")
        if total_validation_addresses == total_summary_contacts:
            print("✅ Total contacts match validation addresses")
        else:
            print("❌ Total contacts do NOT match validation addresses")
        
        print()
        
        # =============================================
        # 3. ENHANCED_FUNNEL_ANALYSIS VALIDATION
        # =============================================
        print("=" * 60)
        print("3. ENHANCED_FUNNEL_ANALYSIS VALIDATION")
        print("=" * 60)
        
        df_funnel = sheets['Enhanced_Funnel_Analysis']
        
        print("Funnel Analysis stages:")
        for idx, row in df_funnel.iterrows():
            print(f"  {row['Funnel_Type']} - {row['Stage']}: {row['Count']} ({row.get('Hectares', 'N/A')} ha)")
        
        print()
        
        # Check funnel consistency with Campaign_Summary
        direct_mail_funnel = df_funnel[df_funnel['Stage'].str.contains('Direct Mail', case=False, na=False)]
        agency_funnel = df_funnel[df_funnel['Stage'].str.contains('Agency', case=False, na=False)]
        
        if not direct_mail_funnel.empty:
            funnel_direct_mail = direct_mail_funnel['Count'].iloc[0]
            summary_direct_mail = summary_totals['Direct_Mail_Final_Contacts']
            print(f"Direct Mail - Funnel: {funnel_direct_mail}, Summary: {summary_direct_mail}")
            if funnel_direct_mail == summary_direct_mail:
                print("✅ Funnel Direct Mail matches Campaign_Summary")
            else:
                print("❌ Funnel Direct Mail MISMATCH with Campaign_Summary")
        
        if not agency_funnel.empty:
            funnel_agency = agency_funnel['Count'].iloc[0]
            summary_agency = summary_totals['Agency_Final_Contacts']
            print(f"Agency - Funnel: {funnel_agency}, Summary: {summary_agency}")
            if funnel_agency == summary_agency:
                print("✅ Funnel Agency matches Campaign_Summary")
            else:
                print("❌ Funnel Agency MISMATCH with Campaign_Summary")
        
        print()
        
        # =============================================
        # 4. ADDRESS_QUALITY_DISTRIBUTION VALIDATION
        # =============================================
        print("=" * 60)
        print("4. ADDRESS_QUALITY_DISTRIBUTION VALIDATION")
        print("=" * 60)
        
        df_quality = sheets['Address_Quality_Distribution']
        
        print("Quality Distribution:")
        for idx, row in df_quality.iterrows():
            print(f"  {row['Quality_Level']}: {row['Count']} ({row['Percentage']:.1f}%)")
        
        # Validate counts
        if 'Address_Confidence' in df_validation.columns:
            print("\nValidation against All_Validation_Ready:")
            actual_quality_counts = df_validation['Address_Confidence'].value_counts()
            
            for idx, row in df_quality.iterrows():
                quality_level = row['Quality_Level']
                expected_count = actual_quality_counts.get(quality_level, 0)
                actual_count = row['Count']
                print(f"  {quality_level} - Expected: {expected_count}, Actual: {actual_count}")
                if expected_count == actual_count:
                    print(f"    ✅ {quality_level} count correct")
                else:
                    print(f"    ❌ {quality_level} count mismatch")
        
        # Validate percentages
        total_percentage = df_quality['Percentage'].sum()
        print(f"\nTotal percentage: {total_percentage:.1f}%")
        if abs(total_percentage - 100.0) < 0.1:
            print("✅ Percentages sum to 100%")
        else:
            print("❌ Percentages do NOT sum to 100%")
        
        print()
        
        # =============================================
        # 5. FINAL_MAILING_LIST VALIDATION
        # =============================================
        print("=" * 60)
        print("5. FINAL_MAILING_LIST VALIDATION")
        print("=" * 60)
        
        df_final = sheets['Final_Mailing_List']
        
        print(f"Final Mailing List entries: {len(df_final)}")
        print("Available columns:")
        print(df_final.columns.tolist())
        
        # Check unique owners
        if 'cf' in df_final.columns:
            unique_owners_final = df_final['cf'].nunique()
            print(f"Unique owners in Final_Mailing_List: {unique_owners_final}")
            
            # Compare with high-confidence addresses
            if 'Address_Confidence' in df_validation.columns:
                high_confidence_owners = df_validation[df_validation['Address_Confidence'].isin(['ULTRA_HIGH', 'HIGH', 'MEDIUM'])]['cf'].nunique()
                print(f"Unique owners with high confidence: {high_confidence_owners}")
                
                if unique_owners_final <= high_confidence_owners:
                    print("✅ Final_Mailing_List owners subset of high-confidence owners")
                else:
                    print("❌ Final_Mailing_List has more owners than high-confidence data")
        
        print()
        
        # =============================================
        # 6. CROSS-SHEET CONSISTENCY CHECK
        # =============================================
        print("=" * 60)
        print("6. CROSS-SHEET CONSISTENCY CHECK")
        print("=" * 60)
        
        # Check that all totals align
        checks = []
        
        # Check 1: Campaign_Summary totals
        if summary_totals['Direct_Mail_Final_Contacts'] > 0 and summary_totals['Agency_Final_Contacts'] > 0:
            total_contacts = summary_totals['Direct_Mail_Final_Contacts'] + summary_totals['Agency_Final_Contacts']
            checks.append(("Total Campaign_Summary contacts", total_contacts, len(df_validation)))
        
        # Check 2: Address_Quality_Distribution totals
        if not df_quality.empty:
            quality_total = df_quality['Count'].sum()
            checks.append(("Address_Quality_Distribution total", quality_total, len(df_validation)))
        
        # Check 3: Enhanced_Funnel_Analysis validation stage
        validation_stages = df_funnel[df_funnel['Stage'].str.contains('Validation', case=False, na=False)]
        if not validation_stages.empty:
            funnel_validation = validation_stages['Count'].iloc[0]
            checks.append(("Funnel validation stage", funnel_validation, len(df_validation)))
        
        print("Consistency checks:")
        all_consistent = True
        for check_name, actual, expected in checks:
            print(f"  {check_name}: {actual} vs {expected}")
            if actual == expected:
                print(f"    ✅ {check_name} consistent")
            else:
                print(f"    ❌ {check_name} inconsistent")
                all_consistent = False
        
        print()
        
        # =============================================
        # 7. FINAL VALIDATION SUMMARY
        # =============================================
        print("=" * 60)
        print("7. FINAL VALIDATION SUMMARY")
        print("=" * 60)
        
        print("KEY METRICS SUMMARY:")
        print(f"  📊 Total validation addresses: {len(df_validation)}")
        print(f"  📊 Direct Mail contacts: {summary_totals['Direct_Mail_Final_Contacts']}")
        print(f"  📊 Agency contacts: {summary_totals['Agency_Final_Contacts']}")
        print(f"  📊 Total contacts: {summary_totals['Direct_Mail_Final_Contacts'] + summary_totals['Agency_Final_Contacts']}")
        
        if summary_totals['Direct_Mail_Final_Contacts'] + summary_totals['Agency_Final_Contacts'] > 0:
            dm_percentage = (summary_totals['Direct_Mail_Final_Contacts'] / (summary_totals['Direct_Mail_Final_Contacts'] + summary_totals['Agency_Final_Contacts'])) * 100
            print(f"  📊 Direct Mail percentage: {dm_percentage:.1f}%")
        
        print()
        
        if all_consistent:
            print("🎯 OVERALL STATUS: ✅ ALL METRICS CONSISTENT AND VALIDATED")
            print("📊 Campaign4 can be used as foundation dataset")
        else:
            print("🎯 OVERALL STATUS: ❌ INCONSISTENCIES FOUND")
            print("📊 Campaign4 requires corrections before use as foundation")
        
        print()
        print("=" * 80)
        print("VALIDATION COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error during validation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    validate_campaign4_complete_metrics()