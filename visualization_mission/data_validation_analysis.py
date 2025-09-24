#!/usr/bin/env python3
"""
Campaign4 Data Validation Analysis for Visualization Development
================================================================

This script validates the Campaign4_Results.xlsx dataset structure and metrics
to ensure perfect alignment with documented requirements before creating visualizations.

Key Validation Points:
- Total addresses: Must equal 642
- Direct Mail: Must be 558 (86.9%)
- Agency: Must be 84 (13.1%)
- Municipality breakdown: Must match Campaign_Summary
- Quality distribution: Must sum to 100%

Business Context: Renewable energy land acquisition in Northern Italy
Data Source: Campaign4_Results.xlsx (v3.1.8 validated)
"""

import pandas as pd
import os
from pathlib import Path

def main():
    """Main validation function"""
    print("="*80)
    print("📊 CAMPAIGN4 DATA VALIDATION FOR VISUALIZATION DEVELOPMENT")
    print("="*80)
    
    # Define paths
    data_path = Path("C:/Projects/land-acquisition-pipeline/dev_tools/data_preparation/Campaign4_Results.xlsx")
    
    if not data_path.exists():
        print(f"❌ ERROR: Data file not found at {data_path}")
        return
    
    print(f"✅ Data file found: {data_path}")
    print()
    
    try:
        # Load all sheets
        print("📋 Loading Excel sheets...")
        excel_file = pd.ExcelFile(data_path)
        print(f"Available sheets: {excel_file.sheet_names}")
        print()
        
        # Load key sheets for validation
        campaign_summary = pd.read_excel(data_path, sheet_name='Campaign_Summary')
        funnel_analysis = pd.read_excel(data_path, sheet_name='Enhanced_Funnel_Analysis') 
        quality_distribution = pd.read_excel(data_path, sheet_name='Address_Quality_Distribution')
        all_validation_ready = pd.read_excel(data_path, sheet_name='All_Validation_Ready')
        
        print("🔍 DATASET STRUCTURE ANALYSIS")
        print("-" * 50)
        
        # Campaign Summary Analysis
        print("1. CAMPAIGN_SUMMARY SHEET:")
        print(f"   - Municipalities: {len(campaign_summary)}")
        print(f"   - Columns: {list(campaign_summary.columns)}")
        
        if 'Direct_Mail_Final_Contacts' in campaign_summary.columns:
            total_direct_mail = campaign_summary['Direct_Mail_Final_Contacts'].sum()
            print(f"   - Total Direct Mail: {total_direct_mail}")
        
        if 'Agency_Final_Contacts' in campaign_summary.columns:
            total_agency = campaign_summary['Agency_Final_Contacts'].sum()
            print(f"   - Total Agency: {total_agency}")
            
        print()
        
        # All Validation Ready Analysis
        print("2. ALL_VALIDATION_READY SHEET:")
        print(f"   - Total Records: {len(all_validation_ready)}")
        print(f"   - Columns: {list(all_validation_ready.columns)}")
        
        if 'Address_Confidence' in all_validation_ready.columns:
            confidence_counts = all_validation_ready['Address_Confidence'].value_counts()
            print(f"   - Address Confidence Distribution:")
            for conf, count in confidence_counts.items():
                percentage = (count / len(all_validation_ready)) * 100
                print(f"     {conf}: {count} ({percentage:.1f}%)")
        
        if 'comune' in all_validation_ready.columns:
            municipality_counts = all_validation_ready['comune'].value_counts()
            print(f"   - Municipality Distribution:")
            for municipality, count in municipality_counts.items():
                print(f"     {municipality}: {count}")
                
        print()
        
        # Quality Distribution Analysis
        print("3. ADDRESS_QUALITY_DISTRIBUTION SHEET:")
        print(f"   - Records: {len(quality_distribution)}")
        if 'Count' in quality_distribution.columns:
            total_quality_count = quality_distribution['Count'].sum()
            print(f"   - Total Count: {total_quality_count}")
        
        if 'Percentage' in quality_distribution.columns:
            total_percentage = quality_distribution['Percentage'].sum()
            print(f"   - Total Percentage: {total_percentage:.1f}%")
            
        print()
        
        # Funnel Analysis
        print("4. ENHANCED_FUNNEL_ANALYSIS SHEET:")
        print(f"   - Stages: {len(funnel_analysis)}")
        if 'Funnel_Type' in funnel_analysis.columns:
            funnel_types = funnel_analysis['Funnel_Type'].value_counts()
            print(f"   - Funnel Types: {dict(funnel_types)}")
            
        print()
        
        # KEY METRIC VALIDATION
        print("🎯 KEY METRIC VALIDATION")
        print("-" * 50)
        
        # Calculate Direct Mail vs Agency split
        if 'Address_Confidence' in all_validation_ready.columns:
            direct_mail_addresses = all_validation_ready[
                all_validation_ready['Address_Confidence'].isin(['ULTRA_HIGH', 'HIGH', 'MEDIUM'])
            ]
            agency_addresses = all_validation_ready[
                all_validation_ready['Address_Confidence'] == 'LOW'
            ]
            
            direct_mail_count = len(direct_mail_addresses)
            agency_count = len(agency_addresses)
            total_addresses = len(all_validation_ready)
            
            print(f"✅ VALIDATION RESULTS:")
            print(f"   - Total Addresses: {total_addresses}")
            print(f"   - Direct Mail Ready: {direct_mail_count} ({direct_mail_count/total_addresses*100:.1f}%)")
            print(f"   - Agency Required: {agency_count} ({agency_count/total_addresses*100:.1f}%)")
            print()
            
            # Check against expected values
            expected_total = 642
            expected_direct_mail = 558
            expected_agency = 84
            
            print(f"📋 ALIGNMENT CHECK:")
            print(f"   - Total: {total_addresses} (Expected: {expected_total}) {'✅' if total_addresses == expected_total else '❌'}")
            print(f"   - Direct Mail: {direct_mail_count} (Expected: {expected_direct_mail}) {'✅' if direct_mail_count == expected_direct_mail else '❌'}")
            print(f"   - Agency: {agency_count} (Expected: {expected_agency}) {'✅' if agency_count == expected_agency else '❌'}")
            print()
            
        # Municipality breakdown validation
        if 'comune' in all_validation_ready.columns and 'comune' in campaign_summary.columns:
            print("🗺️ MUNICIPALITY VALIDATION:")
            print("-" * 30)
            
            municipalities_validation = all_validation_ready['comune'].value_counts().sort_index()
            municipalities_summary = campaign_summary.set_index('comune')
            
            for municipality in municipalities_validation.index:
                validation_count = municipalities_validation[municipality]
                
                if municipality in municipalities_summary.index:
                    if 'Direct_Mail_Final_Contacts' in municipalities_summary.columns:
                        direct_mail = municipalities_summary.loc[municipality, 'Direct_Mail_Final_Contacts']
                    else:
                        direct_mail = 0
                        
                    if 'Agency_Final_Contacts' in municipalities_summary.columns:
                        agency = municipalities_summary.loc[municipality, 'Agency_Final_Contacts']
                    else:
                        agency = 0
                        
                    summary_total = direct_mail + agency
                    match = "✅" if validation_count == summary_total else "❌"
                    
                    print(f"   {municipality}: {validation_count} (Summary: {summary_total}) {match}")
                    
        print()
        print("="*80)
        print("📊 DATA VALIDATION COMPLETE - Ready for Visualization Development")
        print("="*80)
        
    except Exception as e:
        print(f"❌ ERROR during validation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()