#!/usr/bin/env python3
"""
Comprehensive Excel File Analysis
Analyzes all sheets in the specified Excel file for sanity checking metrics
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

def analyze_excel_file(file_path):
    """
    Comprehensive analysis of Excel file with all sheets
    """
    print(f"Analyzing Excel file: {file_path}")
    print("=" * 80)
    
    try:
        # Read all sheets
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        print(f"Total sheets found: {len(sheet_names)}")
        print(f"Sheet names: {sheet_names}")
        print("\n" + "=" * 80)
        
        # Store data for cross-sheet validation
        sheet_data = {}
        
        # Analyze each sheet
        for sheet_name in sheet_names:
            print(f"\nANALYZING SHEET: {sheet_name}")
            print("-" * 50)
            
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheet_data[sheet_name] = df
                
                # Basic info
                print(f"Rows: {len(df)}")
                print(f"Columns: {len(df.columns)}")
                print(f"Column names: {list(df.columns)}")
                
                # Data types
                print("\nData types:")
                for col in df.columns:
                    print(f"  {col}: {df[col].dtype}")
                
                # Check for missing values
                missing_counts = df.isnull().sum()
                if missing_counts.sum() > 0:
                    print("\nMissing values:")
                    for col, count in missing_counts.items():
                        if count > 0:
                            print(f"  {col}: {count} missing")
                
                # Show first few rows
                print("\nFirst 5 rows:")
                print(df.head())
                
                # Specific analysis based on sheet name
                if 'Enhanced_Funnel_Analysis' in sheet_name:
                    analyze_enhanced_funnel(df, sheet_name)
                elif 'Address_Quality_Distribution' in sheet_name:
                    analyze_address_quality(df, sheet_name)
                elif 'Campaign_Summary' in sheet_name:
                    analyze_campaign_summary(df, sheet_name)
                elif 'All_Validation_Ready' in sheet_name:
                    analyze_validation_ready(df, sheet_name)
                elif 'Final_Mailing_List' in sheet_name:
                    analyze_final_mailing_list(df, sheet_name)
                
                # Numeric column statistics
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    print(f"\nNumeric column statistics:")
                    print(df[numeric_cols].describe())
                
            except Exception as e:
                print(f"Error reading sheet {sheet_name}: {str(e)}")
                continue
            
            print("\n" + "=" * 80)
        
        # Cross-sheet validation
        print("\nCROSS-SHEET VALIDATION")
        print("-" * 50)
        perform_cross_sheet_validation(sheet_data)
        
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        return False
    
    return True

def analyze_enhanced_funnel(df, sheet_name):
    """Analyze Enhanced Funnel Analysis sheet specifically"""
    print(f"\nSPECIFIC ANALYSIS FOR {sheet_name}:")
    
    # Look for key metrics columns
    key_metrics = ['Stage', 'Count', 'Conversion_Rate', 'Percentage', 'Total', 'Contacts']
    found_metrics = [col for col in key_metrics if col in df.columns]
    
    if found_metrics:
        print(f"Found key metrics columns: {found_metrics}")
        
        # Show key metrics
        for col in found_metrics:
            if df[col].dtype in ['int64', 'float64']:
                print(f"  {col}: Total={df[col].sum()}, Mean={df[col].mean():.2f}")
    
    # Look for conversion rates
    conversion_cols = [col for col in df.columns if 'conversion' in col.lower() or 'rate' in col.lower()]
    if conversion_cols:
        print(f"Conversion rate columns: {conversion_cols}")
        for col in conversion_cols:
            if df[col].dtype in ['int64', 'float64']:
                print(f"  {col}: Min={df[col].min():.4f}, Max={df[col].max():.4f}, Mean={df[col].mean():.4f}")

def analyze_address_quality(df, sheet_name):
    """Analyze Address Quality Distribution sheet"""
    print(f"\nSPECIFIC ANALYSIS FOR {sheet_name}:")
    
    # Look for quality categories
    quality_cols = [col for col in df.columns if 'quality' in col.lower() or 'category' in col.lower()]
    if quality_cols:
        print(f"Quality columns: {quality_cols}")
        
        # Show distribution
        for col in quality_cols:
            if df[col].dtype == 'object':
                print(f"  {col} distribution:")
                print(df[col].value_counts().to_string())
    
    # Look for count columns
    count_cols = [col for col in df.columns if 'count' in col.lower() or 'total' in col.lower()]
    if count_cols:
        print(f"Count columns: {count_cols}")
        for col in count_cols:
            if df[col].dtype in ['int64', 'float64']:
                print(f"  {col}: Total={df[col].sum()}")

def analyze_campaign_summary(df, sheet_name):
    """Analyze Campaign Summary sheet"""
    print(f"\nSPECIFIC ANALYSIS FOR {sheet_name}:")
    
    # Look for municipality data
    if 'Municipality' in df.columns or 'City' in df.columns:
        muni_col = 'Municipality' if 'Municipality' in df.columns else 'City'
        print(f"Municipalities found: {df[muni_col].nunique()}")
        print(f"Municipality list: {df[muni_col].unique().tolist()}")
    
    # Look for key metrics
    metric_cols = [col for col in df.columns if any(word in col.lower() for word in ['total', 'count', 'contacts', 'parcels', 'addresses'])]
    if metric_cols:
        print(f"Key metric columns: {metric_cols}")
        for col in metric_cols:
            if df[col].dtype in ['int64', 'float64']:
                print(f"  {col}: Total={df[col].sum()}, Mean={df[col].mean():.2f}")

def analyze_validation_ready(df, sheet_name):
    """Analyze All Validation Ready sheet"""
    print(f"\nSPECIFIC ANALYSIS FOR {sheet_name}:")
    
    print(f"Total validation-ready records: {len(df)}")
    
    # Check for contact information
    contact_cols = [col for col in df.columns if any(word in col.lower() for word in ['name', 'address', 'phone', 'email', 'contact'])]
    if contact_cols:
        print(f"Contact information columns: {contact_cols}")
        
        # Check completeness
        for col in contact_cols:
            non_null_count = df[col].notna().sum()
            print(f"  {col}: {non_null_count}/{len(df)} ({non_null_count/len(df)*100:.1f}%) complete")

def analyze_final_mailing_list(df, sheet_name):
    """Analyze Final Mailing List sheet"""
    print(f"\nSPECIFIC ANALYSIS FOR {sheet_name}:")
    
    print(f"Final mailing list size: {len(df)}")
    
    # Check for required mailing fields
    mailing_cols = [col for col in df.columns if any(word in col.lower() for word in ['name', 'address', 'city', 'state', 'zip', 'postal'])]
    if mailing_cols:
        print(f"Mailing address columns: {mailing_cols}")
        
        # Check completeness
        for col in mailing_cols:
            non_null_count = df[col].notna().sum()
            print(f"  {col}: {non_null_count}/{len(df)} ({non_null_count/len(df)*100:.1f}%) complete")

def perform_cross_sheet_validation(sheet_data):
    """Perform cross-sheet validation checks"""
    
    # Check for numerical consistency
    print("Checking numerical consistency between sheets...")
    
    # Extract record counts from different sheets
    counts = {}
    
    for sheet_name, df in sheet_data.items():
        counts[sheet_name] = len(df)
        print(f"  {sheet_name}: {len(df)} records")
    
    # Look for potential issues
    if 'Final_Mailing_List' in counts and 'All_Validation_Ready' in counts:
        final_count = counts['Final_Mailing_List']
        validation_count = counts['All_Validation_Ready']
        
        if final_count > validation_count:
            print(f"⚠️  WARNING: Final mailing list ({final_count}) has more records than validation ready ({validation_count})")
        else:
            print(f"✓ Final mailing list size ({final_count}) is consistent with validation ready ({validation_count})")
    
    # Check for funnel consistency
    if 'Enhanced_Funnel_Analysis' in sheet_data:
        funnel_df = sheet_data['Enhanced_Funnel_Analysis']
        print("\nFunnel consistency check:")
        
        # Look for stage progression
        if 'Count' in funnel_df.columns and 'Stage' in funnel_df.columns:
            stages = funnel_df['Stage'].tolist()
            counts_list = funnel_df['Count'].tolist()
            
            print("Funnel stages and counts:")
            for i, (stage, count) in enumerate(zip(stages, counts_list)):
                print(f"  {i+1}. {stage}: {count}")
                
                # Check if each stage has fewer or equal records than previous
                if i > 0 and count > counts_list[i-1]:
                    print(f"    ⚠️  WARNING: Stage {stage} has more records than previous stage")

if __name__ == "__main__":
    file_path = "/mnt/c/Projects/land-acquisition-pipeline/completed_campaigns/LandAcquisition_Casalpusterlengo_Castiglione_20250703_1807/LandAcquisition_Casalpusterlengo_Castiglione_20250703_1807_Results.xlsx"
    
    if not Path(file_path).exists():
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
    
    success = analyze_excel_file(file_path)
    
    if success:
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("Review the output above for:")
        print("1. Sheet structure and data quality")
        print("2. Numerical consistency between sheets")
        print("3. Funnel progression logic")
        print("4. Data completeness issues")
        print("5. Any warnings or unusual values")
    else:
        print("Analysis failed - check error messages above")