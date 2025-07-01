#!/usr/bin/env python3
"""
Simple Campaign Output Analyzer - Fixed Unicode Issues
Run this to analyze your campaign Excel file
"""

import pandas as pd
import os
from datetime import datetime

def analyze_campaign_simple(file_path, output_file=None):
    """Simple analysis of campaign Excel file"""
    
    if output_file:
        f = open(output_file, 'w', encoding='utf-8')
        def output(text=""):
            print(text)
            print(text, file=f)
    else:
        def output(text=""):
            print(text)
    
    output("="*70)
    output("CAMPAIGN OUTPUT ANALYSIS - v2.9.6 VERIFICATION")
    output("="*70)
    output(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output(f"File: {file_path}")
    output()
    
    if not os.path.exists(file_path):
        output("ERROR: File not found!")
        if output_file:
            f.close()
        return
    
    try:
        # Get file info
        file_size = os.path.getsize(file_path) / (1024*1024)
        output(f"File Size: {file_size:.2f} MB")
        output()
        
        # Load Excel file
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        output("SHEET STRUCTURE:")
        output("="*30)
        output(f"Total Sheets: {len(sheet_names)}")
        
        expected_sheets = [
            "All_Raw_Data",
            "All_Validation_Ready", 
            "All_Companies_Found",
            "Campaign_Summary",
            "Funnel_Analysis"
        ]
        
        output()
        output("Expected vs Found:")
        for expected_sheet in expected_sheets:
            status = "FOUND" if expected_sheet in sheet_names else "MISSING"
            output(f"  {expected_sheet}: {status}")
        
        # Check for unexpected sheets
        unexpected_sheets = [sheet for sheet in sheet_names if sheet not in expected_sheets]
        if unexpected_sheets:
            output(f"Unexpected Sheets: {unexpected_sheets}")
        
        output()
        output("DETAILED SHEET ANALYSIS:")
        output("="*30)
        
        # Analyze each sheet
        for i, sheet_name in enumerate(sheet_names, 1):
            output(f"\n{i}. {sheet_name}")
            output("-" * len(f"{i}. {sheet_name}"))
            
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                output(f"   Rows: {len(df)}")
                output(f"   Columns: {len(df.columns)}")
                
                # Show first 5 column names
                cols_to_show = df.columns[:5].tolist()
                output(f"   First 5 Columns: {cols_to_show}")
                
                # Check for key columns
                key_columns = ['CP', 'comune', 'provincia']
                present_keys = [col for col in key_columns if col in df.columns]
                missing_keys = [col for col in key_columns if col not in df.columns]
                
                if present_keys:
                    output(f"   Key Columns Present: {present_keys}")
                if missing_keys:
                    output(f"   Key Columns Missing: {missing_keys}")
                
                # Sheet-specific checks
                if sheet_name == "Campaign_Summary":
                    output("   CAMPAIGN SUMMARY CHECKS:")
                    if 'CP' in df.columns and 'comune' in df.columns and 'provincia' in df.columns:
                        output("     SUCCESS: All traceability columns present")
                    else:
                        output("     ISSUE: Missing traceability columns")
                    
                    if 'Unique_Owner_Address_Pairs' in df.columns:
                        total_pairs = df['Unique_Owner_Address_Pairs'].sum()
                        output(f"     Unique_Owner_Address_Pairs Total: {total_pairs}")
                        if total_pairs > 0:
                            output("     SUCCESS: Metric shows actual count (not 0)")
                        else:
                            output("     ISSUE: Metric still showing 0")
                    
                    # Check area calculations
                    area_cols = [col for col in df.columns if 'Area_Ha' in col]
                    if area_cols:
                        output(f"     Area Columns: {area_cols}")
                        for col in area_cols[:2]:  # Check first 2 area columns
                            if col in df.columns:
                                values = df[col].dropna()
                                if len(values) > 0:
                                    avg_val = values.mean()
                                    output(f"     {col} Average: {avg_val:.2f}")
                                    if avg_val > 100000:  # Suspiciously high
                                        output("       WARNING: Suspiciously high values (decimal issue?)")
                                    elif avg_val > 0:
                                        output("       SUCCESS: Realistic area values")
                
                elif sheet_name == "Funnel_Analysis":
                    output("   FUNNEL ANALYSIS CHECKS:")
                    if 'provincia' in df.columns:
                        output("     SUCCESS: Provincia column present")
                    else:
                        output("     ISSUE: Provincia column missing")
                    
                    if 'Hectares' in df.columns:
                        hectare_values = df['Hectares'].dropna()
                        hectare_values = hectare_values[hectare_values != '-']  # Remove dash entries
                        if len(hectare_values) > 0:
                            try:
                                numeric_hectares = pd.to_numeric(hectare_values, errors='coerce').dropna()
                                if len(numeric_hectares) > 0:
                                    avg_hectares = numeric_hectares.mean()
                                    output(f"     Average Hectares: {avg_hectares:.2f}")
                                    if avg_hectares > 100000:
                                        output("       WARNING: Suspiciously high hectare values")
                                    elif avg_hectares > 0:
                                        output("       SUCCESS: Realistic hectare values")
                            except:
                                output("     WARNING: Could not analyze hectare values")
                
                elif sheet_name == "All_Companies_Found":
                    output("   COMPANIES SHEET CHECKS:")
                    if len(df) > 0:
                        output(f"     SUCCESS: {len(df)} company records found")
                    else:
                        output("     INFO: Empty companies sheet (expected if no companies)")
                    
                    pec_cols = [col for col in df.columns if 'pec' in col.lower()]
                    if pec_cols:
                        output(f"     PEC Columns Present: {pec_cols}")
                    
            except Exception as e:
                output(f"   ERROR reading sheet: {str(e)}")
        
        output("\n" + "="*70)
        output("ANALYSIS COMPLETE")
        output("="*70)
        
    except Exception as e:
        output(f"ERROR analyzing file: {str(e)}")
    
    if output_file:
        f.close()
        output(f"\nAnalysis saved to: {output_file}")

def main():
    """Main function"""
    print("SIMPLE CAMPAIGN ANALYZER")
    print("Enter the path to your campaign Excel file:")
    
    file_path = input("File path: ").strip().strip('"').strip("'")
    
    # Generate output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"campaign_analysis_simple_{timestamp}.txt"
    
    print(f"\nAnalyzing... Results will be saved to: {output_filename}")
    
    analyze_campaign_simple(file_path, output_filename)
    
    print(f"\nDone! Copy the contents of {output_filename} to share with your agent.")

if __name__ == "__main__":
    main()