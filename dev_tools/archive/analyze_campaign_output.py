#!/usr/bin/env python3
"""
Campaign Output Analyzer - v2.9.5 Structure Verification
Analyzes the consolidated Excel output to verify structure and content.
"""

import pandas as pd
import os
from pathlib import Path

def analyze_campaign_file(file_path, output_file=None):
    """
    Comprehensive analysis of campaign Excel file structure and content.
    """
    # Set up output - either file or console
    if output_file:
        f = open(output_file, 'w', encoding='utf-8')
        def output(text=""):
            print(text, file=f)
            print(text)  # Also print to console for immediate feedback
    else:
        def output(text=""):
            print(text)
    
    output("="*80)
    output("LAND ACQUISITION PIPELINE - CAMPAIGN OUTPUT ANALYZER")
    output("="*80)
    output(f"Analyzing file: {file_path}")
    output()
    
    if not os.path.exists(file_path):
        output("❌ ERROR: File not found!")
        output("Please provide the correct path to your campaign results file.")
        if output_file:
            f.close()
        return
    
    try:
        # Get file info
        file_size = os.path.getsize(file_path) / (1024*1024)  # MB
        print(f"📁 File Size: {file_size:.2f} MB")
        print()
        
        # Load Excel file and get sheet names
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        output("📋 SHEET STRUCTURE ANALYSIS")
        output("="*50)
        output(f"Total Sheets: {len(sheet_names)}")
        
        expected_sheets = [
            "All_Raw_Data",
            "All_Validation_Ready", 
            "All_Companies_Found",
            "Campaign_Summary",
            "Funnel_Analysis"
        ]
        
        # Check for expected sheets
        output("\n✅ Expected Sheets Status:")
        for expected_sheet in expected_sheets:
            status = "✅ FOUND" if expected_sheet in sheet_names else "❌ MISSING"
            output(f"  {expected_sheet}: {status}")
        
        # Check for unexpected sheets
        unexpected_sheets = [sheet for sheet in sheet_names if sheet not in expected_sheets]
        if unexpected_sheets:
            output(f"\n⚠️  Unexpected Sheets Found: {unexpected_sheets}")
        
        output("\n" + "="*50)
        output("DETAILED SHEET ANALYSIS")
        output("="*50)
        
        # Analyze each sheet
        for i, sheet_name in enumerate(sheet_names, 1):
            print(f"\n{i}. SHEET: '{sheet_name}'")
            print("-" * (len(sheet_name) + 12))
            
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Basic info
                print(f"   Rows: {len(df)}")
                print(f"   Columns: {len(df.columns)}")
                
                # Show column names
                print(f"   Column Names:")
                for j, col in enumerate(df.columns, 1):
                    print(f"     {j:2d}. {col}")
                
                # Check for key traceability columns
                key_columns = ['CP', 'comune', 'provincia']
                present_key_cols = [col for col in key_columns if col in df.columns]
                missing_key_cols = [col for col in key_columns if col not in df.columns]
                
                if present_key_cols:
                    print(f"   ✅ Key Columns Present: {present_key_cols}")
                if missing_key_cols:
                    print(f"   ⚠️  Key Columns Missing: {missing_key_cols}")
                
                # Show unique values for traceability columns if present
                if 'CP' in df.columns:
                    unique_cps = df['CP'].nunique() if not df['CP'].isna().all() else 0
                    print(f"   🏗️  Unique CPs: {unique_cps}")
                    if unique_cps > 0 and unique_cps <= 10:
                        print(f"   CP Values: {sorted(df['CP'].dropna().unique())}")
                
                if 'comune' in df.columns:
                    unique_comuni = df['comune'].nunique() if not df['comune'].isna().all() else 0
                    print(f"   🏛️  Unique Municipalities: {unique_comuni}")
                    if unique_comuni > 0 and unique_comuni <= 10:
                        print(f"   Municipality Values: {sorted(df['comune'].dropna().unique())}")
                
                # Sheet-specific analysis
                if sheet_name == "All_Validation_Ready":
                    analyze_validation_ready_sheet(df)
                elif sheet_name == "All_Companies_Found":
                    analyze_companies_sheet(df)
                elif sheet_name == "Campaign_Summary":
                    analyze_campaign_summary_sheet(df)
                elif sheet_name == "Funnel_Analysis":
                    analyze_funnel_sheet(df)
                elif sheet_name == "All_Raw_Data":
                    analyze_raw_data_sheet(df)
                
                # Show first few rows (sample data)
                if len(df) > 0:
                    print(f"\n   📋 SAMPLE DATA (First 3 rows):")
                    sample_df = df.head(3)
                    for idx, row in sample_df.iterrows():
                        print(f"     Row {idx + 1}:")
                        for col_name, value in row.items():
                            # Truncate long values
                            str_value = str(value)
                            if len(str_value) > 50:
                                str_value = str_value[:47] + "..."
                            print(f"       {col_name}: {str_value}")
                        print()
                
            except Exception as e:
                print(f"   ❌ ERROR reading sheet: {str(e)}")
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        
    except Exception as e:
        output(f"❌ ERROR analyzing file: {str(e)}")
    
    # Close file if we opened one
    if output_file:
        f.close()
        output(f"\n📁 Analysis saved to: {output_file}")

def analyze_validation_ready_sheet(df):
    """Specific analysis for All_Validation_Ready sheet."""
    print(f"   📧 VALIDATION READY ANALYSIS:")
    
    # Check for required columns
    required_cols = ['Address_Confidence', 'Routing_Channel', 'foglio_input', 'particella_input']
    present_req_cols = [col for col in required_cols if col in df.columns]
    missing_req_cols = [col for col in required_cols if col not in df.columns]
    
    if present_req_cols:
        print(f"      ✅ Required Columns Present: {present_req_cols}")
    if missing_req_cols:
        print(f"      ⚠️  Required Columns Missing: {missing_req_cols}")
    
    # Analyze routing channels
    if 'Routing_Channel' in df.columns:
        routing_counts = df['Routing_Channel'].value_counts()
        print(f"      📬 Routing Channel Distribution:")
        for channel, count in routing_counts.items():
            print(f"         {channel}: {count}")
    
    # Analyze address confidence
    if 'Address_Confidence' in df.columns:
        confidence_counts = df['Address_Confidence'].value_counts()
        print(f"      🎯 Address Confidence Distribution:")
        for confidence, count in confidence_counts.items():
            print(f"         {confidence}: {count}")

def analyze_companies_sheet(df):
    """Specific analysis for All_Companies_Found sheet."""
    print(f"   🏢 COMPANIES ANALYSIS:")
    
    # Check for PEC column
    pec_columns = [col for col in df.columns if 'pec' in col.lower() or 'email' in col.lower()]
    if pec_columns:
        print(f"      📧 PEC/Email Columns Found: {pec_columns}")
        for pec_col in pec_columns:
            non_empty_pecs = df[pec_col].notna().sum()
            print(f"         {pec_col}: {non_empty_pecs} non-empty values")
    else:
        print(f"      ⚠️  No PEC/Email columns found")

def analyze_campaign_summary_sheet(df):
    """Specific analysis for Campaign_Summary sheet."""
    print(f"   📊 CAMPAIGN SUMMARY ANALYSIS:")
    
    # Check for key metrics columns
    key_metrics = [
        'Direct_Mail_Final_Contacts', 'Agency_Final_Contacts',
        'Direct_Mail_Final_Area_Ha', 'Agency_Final_Area_Ha',
        'Unique_Owner_Address_Pairs'
    ]
    
    present_metrics = [col for col in key_metrics if col in df.columns]
    missing_metrics = [col for col in key_metrics if col not in df.columns]
    
    if present_metrics:
        print(f"      ✅ Key Metrics Present: {present_metrics}")
    if missing_metrics:
        print(f"      ⚠️  Key Metrics Missing: {missing_metrics}")
    
    # Show metric totals if available
    for metric in present_metrics:
        if df[metric].dtype in ['int64', 'float64']:
            total = df[metric].sum()
            print(f"         {metric} Total: {total}")

def analyze_funnel_sheet(df):
    """Specific analysis for Funnel_Analysis sheet."""
    print(f"   🔄 FUNNEL ANALYSIS:")
    
    # Check for stage columns
    funnel_indicators = ['stage', 'parcels', 'hectares', 'area']
    funnel_cols = [col for col in df.columns if any(indicator in col.lower() for indicator in funnel_indicators)]
    
    if funnel_cols:
        print(f"      🎯 Funnel-related Columns: {funnel_cols}")
    else:
        print(f"      ⚠️  No clear funnel columns identified")
    
    # Check for municipality breakdown
    if 'comune' in df.columns:
        unique_comuni = df['comune'].nunique()
        print(f"      🏛️  Municipalities in Funnel: {unique_comuni}")

def analyze_raw_data_sheet(df):
    """Specific analysis for All_Raw_Data sheet."""
    print(f"   📋 RAW DATA ANALYSIS:")
    
    # Check for owner type classification
    owner_indicators = ['tipo_proprietario', 'owner_type', 'privato', 'azienda']
    owner_cols = [col for col in df.columns if any(indicator in col.lower() for indicator in owner_indicators)]
    
    if owner_cols:
        print(f"      👥 Owner Classification Columns: {owner_cols}")
    else:
        print(f"      ⚠️  No clear owner classification columns")

def main():
    """Main function to run the analysis."""
    print("Please provide the path to your campaign results Excel file.")
    print("Examples:")
    print("  - completed_campaigns/LandAcquisition_Campaign_20250630_1824/LandAcquisition_Campaign_20250630_1824_Results.xlsx")
    print("  - C:/path/to/your/campaign_results.xlsx")
    print()
    
    # You can hardcode the path here or use input()
    file_path = input("Enter the full path to your Excel file: ").strip()
    
    # Remove quotes if present
    file_path = file_path.strip('"').strip("'")
    
    analyze_campaign_file(file_path)
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("1. Review the analysis above")
    print("2. Identify what needs to be fixed based on expected v2.9.5 structure")
    print("3. Share this output with your agent for improvement planning")
    print("="*80)

if __name__ == "__main__":
    main()