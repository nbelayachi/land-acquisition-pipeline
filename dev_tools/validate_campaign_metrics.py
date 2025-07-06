#!/usr/bin/env python3
"""
Campaign Metrics Validation Script
Analyzes and validates all metrics from a completed campaign Excel file
Usage: Run in Spyder and paste the output back for review
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_campaign_metrics(excel_path):
    """
    Comprehensive analysis of campaign metrics for validation
    """
    print("="*80)
    print("CAMPAIGN METRICS VALIDATION ANALYSIS")
    print("="*80)
    print(f"File: {excel_path}")
    print()
    
    try:
        # Read all sheets
        excel_file = pd.ExcelFile(excel_path)
        all_sheets = excel_file.sheet_names
        
        print(f"📊 SHEETS FOUND: {len(all_sheets)}")
        for i, sheet in enumerate(all_sheets, 1):
            print(f"  {i}. {sheet}")
        print()
        
        # Store analysis results
        analysis_results = {}
        
        # Analyze each sheet
        for sheet_name in all_sheets:
            print(f"🔍 ANALYZING: {sheet_name}")
            print("-" * 50)
            
            try:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                
                print(f"Rows: {len(df)}")
                print(f"Columns: {len(df.columns)}")
                print(f"Column Names: {list(df.columns)}")
                
                # Store basic info
                analysis_results[sheet_name] = {
                    'rows': len(df),
                    'columns': list(df.columns),
                    'data': df
                }
                
                # Sheet-specific analysis
                if sheet_name == 'Enhanced_Funnel_Analysis':
                    analyze_enhanced_funnel(df)
                elif sheet_name == 'Address_Quality_Distribution':
                    analyze_quality_distribution(df)
                elif sheet_name == 'Campaign_Summary':
                    analyze_campaign_summary(df)
                elif sheet_name == 'All_Validation_Ready':
                    analyze_validation_ready(df)
                elif sheet_name == 'Final_Mailing_List':
                    analyze_final_mailing_list(df)
                elif sheet_name == 'All_Raw_Data':
                    analyze_raw_data(df)
                
                print()
                
            except Exception as e:
                print(f"❌ Error reading {sheet_name}: {e}")
                print()
        
        # Cross-validation analysis
        perform_cross_validation(analysis_results)
        
    except Exception as e:
        print(f"❌ Error opening file: {e}")

def analyze_enhanced_funnel(df):
    """Analyze Enhanced_Funnel_Analysis sheet"""
    print("📈 ENHANCED FUNNEL ANALYSIS:")
    
    if len(df) > 0:
        # Group by funnel type
        if 'Funnel_Type' in df.columns:
            funnel_types = df['Funnel_Type'].unique()
            print(f"Funnel Types: {funnel_types}")
            
            for funnel_type in funnel_types:
                funnel_data = df[df['Funnel_Type'] == funnel_type]
                print(f"\n  {funnel_type} Pipeline:")
                
                if 'Stage' in df.columns and 'Count' in df.columns:
                    for _, row in funnel_data.iterrows():
                        stage = row['Stage']
                        count = row['Count']
                        hectares = row.get('Hectares', 'N/A')
                        conversion = row.get('Conversion_Rate', 'N/A')
                        print(f"    {stage}: {count} items, {hectares} ha, {conversion}% conversion")
        
        # Check for mathematical consistency
        print(f"\n  🔍 Data Quality Checks:")
        if 'Conversion_Rate' in df.columns:
            conversion_rates = df['Conversion_Rate'].dropna()
            invalid_rates = conversion_rates[(conversion_rates < 0) | (conversion_rates > 100)]
            if len(invalid_rates) > 0:
                print(f"    ⚠️  Invalid conversion rates found: {invalid_rates.tolist()}")
            else:
                print(f"    ✅ All conversion rates valid (0-100%)")
    else:
        print("  ❌ Sheet is empty")

def analyze_quality_distribution(df):
    """Analyze Address_Quality_Distribution sheet"""
    print("🎯 ADDRESS QUALITY DISTRIBUTION:")
    
    if len(df) > 0 and 'Quality_Level' in df.columns:
        total_addresses = 0
        quality_breakdown = {}
        
        for _, row in df.iterrows():
            quality = row['Quality_Level']
            count = row.get('Count', 0)
            percentage = row.get('Percentage', 0)
            
            quality_breakdown[quality] = {'count': count, 'percentage': percentage}
            total_addresses += count
            
            routing = row.get('Routing_Decision', 'N/A')
            automation = row.get('Automation_Level', 'N/A')
            
            print(f"  {quality}: {count} addresses ({percentage}%) → {routing} [{automation}]")
        
        print(f"\n  📊 Summary:")
        print(f"    Total Addresses: {total_addresses}")
        
        # Validate percentages add to 100%
        total_percentage = sum([item['percentage'] for item in quality_breakdown.values()])
        print(f"    Total Percentage: {total_percentage}%")
        if abs(total_percentage - 100) > 0.1:
            print(f"    ⚠️  Percentages don't sum to 100%!")
        else:
            print(f"    ✅ Percentages sum correctly")
    else:
        print("  ❌ Sheet is empty or missing required columns")

def analyze_campaign_summary(df):
    """Analyze Campaign_Summary sheet"""
    print("📋 CAMPAIGN SUMMARY:")
    
    if len(df) > 0:
        print(f"  Municipalities: {len(df)}")
        
        # Key metrics
        key_metrics = [
            'Total_Owners_Found', 'Unique_Owners', 'Unique_Owner_Address_Pairs',
            'High_Confidence_Contacts', 'Total_Area_Ha', 'After_CatA_Filter_Area_Ha'
        ]
        
        municipality_totals = {}
        for metric in key_metrics:
            if metric in df.columns:
                total = df[metric].sum()
                municipality_totals[metric] = total
                print(f"    {metric}: {total}")
        
        # Show municipality breakdown
        if 'comune' in df.columns:
            print(f"\n  📍 By Municipality:")
            for _, row in df.iterrows():
                comune = row.get('comune', 'Unknown')
                owners = row.get('Unique_Owners', 0)
                contacts = row.get('Unique_Owner_Address_Pairs', 0)
                print(f"    {comune}: {owners} owners → {contacts} contacts")
        
        return municipality_totals
    else:
        print("  ❌ Sheet is empty")
        return {}

def analyze_validation_ready(df):
    """Analyze All_Validation_Ready sheet"""
    print("✅ VALIDATION READY CONTACTS:")
    
    if len(df) > 0:
        print(f"  Total Contacts: {len(df)}")
        
        # Quality distribution if available
        if 'Geocoding_Quality' in df.columns:
            quality_dist = df['Geocoding_Quality'].value_counts()
            print(f"  Quality Distribution:")
            for quality, count in quality_dist.items():
                print(f"    {quality}: {count}")
        
        # Routing distribution if available
        if 'Routing_Channel' in df.columns:
            routing_dist = df['Routing_Channel'].value_counts()
            print(f"  Routing Distribution:")
            for routing, count in routing_dist.items():
                print(f"    {routing}: {count}")
        
        # Unique owners
        if 'cf' in df.columns:
            unique_owners = df['cf'].nunique()
            print(f"  Unique Owners: {unique_owners}")
        
        return len(df)
    else:
        print("  ❌ Sheet is empty")
        return 0

def analyze_final_mailing_list(df):
    """Analyze Final_Mailing_List sheet"""
    print("📬 FINAL MAILING LIST:")
    
    if len(df) > 0:
        print(f"  Total Entries: {len(df)}")
        
        # Count unique parcels and owners
        if 'Municipality' in df.columns and 'Foglio' in df.columns and 'Particella' in df.columns:
            unique_parcels = df.groupby(['Municipality', 'Foglio', 'Particella']).size()
            print(f"  Unique Parcels: {len(unique_parcels)}")
        
        if 'Full_Name' in df.columns:
            unique_owners = df['Full_Name'].nunique()
            print(f"  Unique Owners: {unique_owners}")
        
        return len(df)
    else:
        print("  ❌ Sheet is empty")
        return 0

def analyze_raw_data(df):
    """Analyze All_Raw_Data sheet"""
    print("📊 RAW DATA:")
    
    if len(df) > 0:
        print(f"  Total Raw Records: {len(df)}")
        
        # Owner type breakdown
        if 'cf' in df.columns:
            # Count numeric vs non-numeric CF (individuals vs companies)
            numeric_cf = df['cf'].str.isnumeric().sum()
            non_numeric_cf = len(df) - numeric_cf
            print(f"  Individuals (numeric CF): {numeric_cf}")
            print(f"  Companies (non-numeric CF): {non_numeric_cf}")
        
        # Property categories
        if 'categoria' in df.columns:
            categories = df['categoria'].value_counts()
            print(f"  Property Categories:")
            for cat, count in categories.items():
                print(f"    {cat}: {count}")
        
        return len(df)
    else:
        print("  ❌ Sheet is empty")
        return 0

def perform_cross_validation(analysis_results):
    """Cross-validate metrics between sheets"""
    print("="*80)
    print("CROSS-VALIDATION ANALYSIS")
    print("="*80)
    
    # Extract key counts
    validation_ready_count = 0
    campaign_summary_contacts = 0
    funnel_final_count = 0
    quality_total_addresses = 0
    
    # Get counts from different sheets
    if 'All_Validation_Ready' in analysis_results:
        validation_ready_count = analysis_results['All_Validation_Ready']['rows']
    
    if 'Campaign_Summary' in analysis_results:
        df_summary = analysis_results['Campaign_Summary']['data']
        if 'Unique_Owner_Address_Pairs' in df_summary.columns:
            campaign_summary_contacts = df_summary['Unique_Owner_Address_Pairs'].sum()
    
    if 'Enhanced_Funnel_Analysis' in analysis_results:
        df_funnel = analysis_results['Enhanced_Funnel_Analysis']['data']
        # Get the final stage count from Contact Processing pipeline
        contact_funnel = df_funnel[df_funnel['Funnel_Type'] == 'Contact Processing']
        if len(contact_funnel) > 0:
            final_stages = contact_funnel[contact_funnel['Stage'].str.contains('Ready|Required', na=False)]
            if len(final_stages) > 0:
                funnel_final_count = final_stages['Count'].sum()
    
    if 'Address_Quality_Distribution' in analysis_results:
        df_quality = analysis_results['Address_Quality_Distribution']['data']
        if 'Count' in df_quality.columns:
            quality_total_addresses = df_quality['Count'].sum()
    
    print("🔍 CROSS-VALIDATION CHECKS:")
    print(f"Validation Ready Count: {validation_ready_count}")
    print(f"Campaign Summary Total Contacts: {campaign_summary_contacts}")
    print(f"Funnel Final Stage Total: {funnel_final_count}")
    print(f"Quality Distribution Total: {quality_total_addresses}")
    
    # Validation checks
    print(f"\n✅ CONSISTENCY CHECKS:")
    
    # Check 1: Validation Ready vs Campaign Summary
    if validation_ready_count == campaign_summary_contacts:
        print(f"✅ Validation Ready ({validation_ready_count}) = Campaign Summary ({campaign_summary_contacts})")
    else:
        print(f"⚠️  Validation Ready ({validation_ready_count}) ≠ Campaign Summary ({campaign_summary_contacts})")
    
    # Check 2: Quality Distribution vs Validation Ready
    if quality_total_addresses == validation_ready_count:
        print(f"✅ Quality Distribution ({quality_total_addresses}) = Validation Ready ({validation_ready_count})")
    else:
        print(f"⚠️  Quality Distribution ({quality_total_addresses}) ≠ Validation Ready ({validation_ready_count})")
    
    # Check 3: Funnel vs other metrics
    if funnel_final_count == validation_ready_count:
        print(f"✅ Funnel Final ({funnel_final_count}) = Validation Ready ({validation_ready_count})")
    else:
        print(f"⚠️  Funnel Final ({funnel_final_count}) ≠ Validation Ready ({validation_ready_count})")

if __name__ == "__main__":
    # Path to your test campaign file
    campaign_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_1807\LandAcquisition_Casalpusterlengo_Castiglione_20250703_1807_Results.xlsx"
    
    print("🚀 Starting Campaign Metrics Validation...")
    print()
    
    analyze_campaign_metrics(campaign_file)
    
    print()
    print("="*80)
    print("VALIDATION COMPLETE - Please review results above")
    print("="*80)