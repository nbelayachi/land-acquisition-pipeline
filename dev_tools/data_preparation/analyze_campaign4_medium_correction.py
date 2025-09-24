#!/usr/bin/env python3
"""
Campaign 4 MEDIUM Address Metrics Validation Script
==================================================

This script analyzes the manually corrected Campaign4_Results.xlsx to validate
the MEDIUM address metrics correction implementation and identify dependent
metrics that need updates.

Usage: Run this script in Spyder with the Campaign4_Results.xlsx file
"""

import pandas as pd
import numpy as np
import os

def analyze_campaign4_medium_correction():
    """
    Comprehensive analysis of Campaign4_Results.xlsx to validate MEDIUM address
    metrics correction and identify all dependent calculations.
    """
    
    # File path
    excel_path = r"C:\Projects\land-acquisition-pipeline\dev_tools\data_preparation\Campaign4_Results.xlsx"
    
    print("=" * 80)
    print("CAMPAIGN 4 MEDIUM ADDRESS METRICS VALIDATION")
    print("=" * 80)
    print(f"Analyzing: {excel_path}")
    print()
    
    # Check if file exists
    if not os.path.exists(excel_path):
        print(f"❌ ERROR: File not found at {excel_path}")
        return
    
    try:
        # Load Excel file and get sheet names
        xls = pd.ExcelFile(excel_path)
        print(f"📊 Available sheets: {xls.sheet_names}")
        print()
        
        # Load key sheets
        sheets = {}
        for sheet_name in ['All_Raw_Data', 'All_Validation_Ready', 'Final_Mailing_List', 
                          'Campaign_Summary', 'Enhanced_Funnel_Analysis', 'Address_Quality_Distribution']:
            if sheet_name in xls.sheet_names:
                sheets[sheet_name] = pd.read_excel(xls, sheet_name)
                print(f"✅ Loaded {sheet_name}: {len(sheets[sheet_name])} rows")
            else:
                print(f"⚠️  Sheet {sheet_name} not found")
        
        print()
        print("=" * 80)
        print("1. ADDRESS CONFIDENCE ANALYSIS")
        print("=" * 80)
        
        # Analyze address confidence distribution
        if 'All_Validation_Ready' in sheets:
            df_validation = sheets['All_Validation_Ready']
            print(f"Total validation-ready addresses: {len(df_validation)}")
            
            if 'Address_Confidence' in df_validation.columns:
                confidence_counts = df_validation['Address_Confidence'].value_counts()
                print("\nAddress Confidence Distribution:")
                for conf, count in confidence_counts.items():
                    percentage = (count / len(df_validation)) * 100
                    print(f"  {conf}: {count} addresses ({percentage:.1f}%)")
                
                # Calculate expected Direct_Mail_Final_Contacts
                direct_mail_expected = confidence_counts.get('ULTRA_HIGH', 0) + \
                                     confidence_counts.get('HIGH', 0) + \
                                     confidence_counts.get('MEDIUM', 0)
                print(f"\n🎯 Expected Direct_Mail_Final_Contacts: {direct_mail_expected}")
                print(f"   (ULTRA_HIGH + HIGH + MEDIUM = {confidence_counts.get('ULTRA_HIGH', 0)} + {confidence_counts.get('HIGH', 0)} + {confidence_counts.get('MEDIUM', 0)})")
            else:
                print("❌ Address_Confidence column not found in All_Validation_Ready")
        
        print()
        print("=" * 80)
        print("2. FINAL MAILING LIST ANALYSIS")
        print("=" * 80)
        
        # Analyze Final_Mailing_List
        if 'Final_Mailing_List' in sheets:
            df_final = sheets['Final_Mailing_List']
            print(f"Final Mailing List addresses: {len(df_final)}")
            
            print(f"Available columns in Final_Mailing_List: {list(df_final.columns)}")
            
            # The Final_Mailing_List should contain only ULTRA_HIGH, HIGH, and MEDIUM addresses
            # but doesn't have Address_Confidence column (by design)
            expected_final_count = confidence_counts.get('ULTRA_HIGH', 0) + confidence_counts.get('HIGH', 0) + confidence_counts.get('MEDIUM', 0)
            
            print(f"\n📊 Expected Final_Mailing_List count: {expected_final_count}")
            print(f"📊 Actual Final_Mailing_List count: {len(df_final)}")
            
            if len(df_final) == expected_final_count:
                print("✅ Final_Mailing_List count matches expected (ULTRA_HIGH + HIGH + MEDIUM)")
            else:
                print("❌ Final_Mailing_List count mismatch")
                print(f"   Difference: {expected_final_count - len(df_final)}")
        
        print()
        print("=" * 80)
        print("3. CAMPAIGN SUMMARY METRICS")
        print("=" * 80)
        
        # Analyze Campaign_Summary metrics
        if 'Campaign_Summary' in sheets:
            df_summary = sheets['Campaign_Summary']
            print(f"Campaign Summary municipalities: {len(df_summary)}")
            
            # Show all available columns first
            print(f"\nAvailable columns in Campaign_Summary: {list(df_summary.columns)}")
            
            # Key metrics to check
            key_metrics = ['Direct_Mail_Final_Contacts', 'Agency_Final_Contacts', 
                          'Direct_Mail_Final_Area_Ha', 'Agency_Final_Area_Ha', 
                          'Total_Final_Contacts', 'Direct_Mail_Percentage']
            
            print("\nCampaign Summary Metrics:")
            for metric in key_metrics:
                if metric in df_summary.columns:
                    total_value = df_summary[metric].sum()
                    print(f"  {metric}: {total_value}")
                else:
                    print(f"  {metric}: NOT FOUND")
            
            # Calculate missing metrics
            print("\n" + "="*50)
            print("CALCULATED MISSING METRICS:")
            print("="*50)
            
            direct_mail_total = df_summary['Direct_Mail_Final_Contacts'].sum() if 'Direct_Mail_Final_Contacts' in df_summary.columns else 0
            agency_total = df_summary['Agency_Final_Contacts'].sum() if 'Agency_Final_Contacts' in df_summary.columns else 84  # LOW confidence addresses
            total_contacts = direct_mail_total + agency_total
            direct_mail_percentage = (direct_mail_total / total_contacts * 100) if total_contacts > 0 else 0
            
            print(f"Direct_Mail_Final_Contacts: {direct_mail_total}")
            print(f"Agency_Final_Contacts: {agency_total}")
            print(f"Total_Final_Contacts: {total_contacts}")
            print(f"Direct_Mail_Percentage: {direct_mail_percentage:.1f}%")
            
            # Check Direct_Mail_Final_Contacts vs expected
            if 'Direct_Mail_Final_Contacts' in df_summary.columns:
                actual_direct_mail = df_summary['Direct_Mail_Final_Contacts'].sum()
                print(f"\n📊 Current Direct_Mail_Final_Contacts: {actual_direct_mail}")
                if 'All_Validation_Ready' in sheets and 'Address_Confidence' in sheets['All_Validation_Ready'].columns:
                    print(f"📊 Expected Direct_Mail_Final_Contacts: {direct_mail_expected}")
                    if actual_direct_mail == direct_mail_expected:
                        print("✅ METRICS ALREADY CORRECTED!")
                    else:
                        print("❌ METRICS NEED CORRECTION!")
                        print(f"   Difference: {direct_mail_expected - actual_direct_mail}")
        
        print()
        print("=" * 80)
        print("4. ENHANCED FUNNEL ANALYSIS")
        print("=" * 80)
        
        # Analyze Enhanced_Funnel_Analysis
        if 'Enhanced_Funnel_Analysis' in sheets:
            df_funnel = sheets['Enhanced_Funnel_Analysis']
            print(f"Funnel Analysis stages: {len(df_funnel)}")
            
            # Find Direct Mail Ready stage
            direct_mail_stages = df_funnel[df_funnel['Stage'].str.contains('Direct Mail', case=False, na=False)]
            if not direct_mail_stages.empty:
                print("\nDirect Mail Related Stages:")
                for idx, row in direct_mail_stages.iterrows():
                    print(f"  {row['Stage']}: {row['Count']} contacts")
            
            # Find Agency stages
            agency_stages = df_funnel[df_funnel['Stage'].str.contains('Agency', case=False, na=False)]
            if not agency_stages.empty:
                print("\nAgency Related Stages:")
                for idx, row in agency_stages.iterrows():
                    print(f"  {row['Stage']}: {row['Count']} contacts")
        
        print()
        print("=" * 80)
        print("5. ADDRESS QUALITY DISTRIBUTION")
        print("=" * 80)
        
        # Analyze Address_Quality_Distribution
        if 'Address_Quality_Distribution' in sheets:
            df_quality = sheets['Address_Quality_Distribution']
            print(f"Quality Distribution levels: {len(df_quality)}")
            
            print("\nAddress Quality Distribution:")
            for idx, row in df_quality.iterrows():
                print(f"  {row['Quality_Level']}: {row['Count']} addresses ({row['Percentage']:.1f}%)")
            
            # Check percentage sum
            total_percentage = df_quality['Percentage'].sum()
            print(f"\nTotal percentage: {total_percentage:.1f}%")
            if abs(total_percentage - 100.0) < 0.1:
                print("✅ Percentages sum to 100%")
            else:
                print("❌ Percentages do not sum to 100%")
        
        print()
        print("=" * 80)
        print("6. ROUTING CHANNEL ANALYSIS")
        print("=" * 80)
        
        # Analyze routing channels
        if 'All_Validation_Ready' in sheets:
            df_validation = sheets['All_Validation_Ready']
            
            if 'Routing_Channel' in df_validation.columns:
                routing_counts = df_validation['Routing_Channel'].value_counts()
                print("Routing Channel Distribution:")
                for channel, count in routing_counts.items():
                    percentage = (count / len(df_validation)) * 100
                    print(f"  {channel}: {count} addresses ({percentage:.1f}%)")
                
                # Cross-reference with confidence levels
                print("\nRouting vs Confidence Cross-Analysis:")
                if 'Address_Confidence' in df_validation.columns:
                    cross_tab = pd.crosstab(df_validation['Address_Confidence'], 
                                          df_validation['Routing_Channel'])
                    print(cross_tab)
        
        print()
        print("=" * 80)
        print("7. EXACT VALUES FOR MANUAL UPDATES")
        print("=" * 80)
        
        if 'All_Validation_Ready' in sheets and 'Address_Confidence' in sheets['All_Validation_Ready'].columns:
            df_validation = sheets['All_Validation_Ready']
            confidence_counts = df_validation['Address_Confidence'].value_counts()
            
            direct_mail_contacts = confidence_counts.get('ULTRA_HIGH', 0) + confidence_counts.get('HIGH', 0) + confidence_counts.get('MEDIUM', 0)
            agency_contacts = confidence_counts.get('LOW', 0)
            total_contacts = direct_mail_contacts + agency_contacts
            direct_mail_percentage = (direct_mail_contacts / total_contacts * 100) if total_contacts > 0 else 0
            
            print("VALUES TO UPDATE IN YOUR EXCEL FILE:")
            print(f"✅ Direct_Mail_Final_Contacts: {direct_mail_contacts}")
            print(f"✅ Agency_Final_Contacts: {agency_contacts}")
            print(f"✅ Total_Final_Contacts: {total_contacts}")
            print(f"✅ Direct_Mail_Percentage: {direct_mail_percentage:.1f}%")
            
            # Enhanced_Funnel_Analysis updates
            print(f"✅ Enhanced_Funnel_Analysis 'Direct Mail Ready': {direct_mail_contacts}")
            print(f"✅ Enhanced_Funnel_Analysis 'Agency Investigation': {agency_contacts}")
        
        print()
        print("=" * 80)
        print("8. CALCULATION FORMULAS")
        print("=" * 80)
        
        print("NEW CORRECTED FORMULAS:")
        print("Direct_Mail_Final_Contacts = COUNT(ULTRA_HIGH) + COUNT(HIGH) + COUNT(MEDIUM)")
        print("Agency_Final_Contacts = COUNT(LOW)")
        print("Total_Final_Contacts = Direct_Mail_Final_Contacts + Agency_Final_Contacts")
        print("Direct_Mail_Percentage = (Direct_Mail_Final_Contacts / Total_Final_Contacts) * 100")
        
        print()
        print("=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_campaign4_medium_correction()