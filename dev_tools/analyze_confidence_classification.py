#!/usr/bin/env python3
"""
Analyze Address Confidence Classification
Examine real campaign data to understand current classification patterns
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_campaign_results(results_file_path):
    """Analyze the confidence classification from real campaign results"""
    
    print("🔍 CONFIDENCE CLASSIFICATION ANALYSIS")
    print("=" * 50)
    
    try:
        # Read the Excel file
        excel_file = pd.ExcelFile(results_file_path)
        print(f"📁 File: {results_file_path}")
        print(f"📊 Available sheets: {excel_file.sheet_names}")
        print()
        
        # Analyze each sheet that contains address classification
        for sheet_name in excel_file.sheet_names:
            print(f"📋 ANALYZING SHEET: {sheet_name}")
            print("-" * 30)
            
            df = pd.read_excel(results_file_path, sheet_name=sheet_name)
            print(f"Total rows: {len(df)}")
            print(f"Columns: {list(df.columns)}")
            
            # Look for confidence-related columns
            confidence_cols = [col for col in df.columns if 'confidence' in col.lower() or 'routing' in col.lower()]
            address_cols = [col for col in df.columns if 'address' in col.lower() or 'ubicazione' in col.lower()]
            
            if confidence_cols:
                print(f"🎯 Confidence columns found: {confidence_cols}")
                
                for col in confidence_cols:
                    if col in df.columns:
                        value_counts = df[col].value_counts()
                        print(f"\n{col} distribution:")
                        for value, count in value_counts.items():
                            percentage = (count / len(df)) * 100
                            print(f"  {value}: {count} ({percentage:.1f}%)")
            
            if address_cols:
                print(f"📍 Address columns found: {address_cols}")
                
                # Check for address quality indicators
                for col in address_cols:
                    if col in df.columns:
                        # Count non-null addresses
                        non_null = df[col].notna().sum()
                        print(f"  {col}: {non_null}/{len(df)} non-null ({non_null/len(df)*100:.1f}%)")
            
            print("\n" + "="*50 + "\n")
    
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def analyze_address_patterns(results_file_path):
    """Analyze address patterns to understand classification logic"""
    
    print("🏠 ADDRESS PATTERN ANALYSIS")
    print("=" * 50)
    
    try:
        # Read the most likely sheet with detailed address data
        # Usually "All_Validation_Ready" or similar
        excel_file = pd.ExcelFile(results_file_path)
        
        # Try to find the main data sheet
        main_sheet = None
        for sheet in excel_file.sheet_names:
            if 'validation' in sheet.lower() or 'ready' in sheet.lower() or 'all' in sheet.lower():
                main_sheet = sheet
                break
        
        if not main_sheet:
            main_sheet = excel_file.sheet_names[0]  # Use first sheet as fallback
        
        print(f"📊 Analyzing main sheet: {main_sheet}")
        df = pd.read_excel(results_file_path, sheet_name=main_sheet)
        
        # Look for key columns
        key_columns = {
            'confidence': [col for col in df.columns if 'confidence' in col.lower()],
            'routing': [col for col in df.columns if 'routing' in col.lower()],
            'address': [col for col in df.columns if 'address' in col.lower() or 'ubicazione' in col.lower()],
            'postal': [col for col in df.columns if 'postal' in col.lower() or 'zip' in col.lower()],
            'geocoding': [col for col in df.columns if 'geocod' in col.lower() or 'lat' in col.lower() or 'lon' in col.lower()]
        }
        
        print("🔍 Found columns by category:")
        for category, cols in key_columns.items():
            if cols:
                print(f"  {category}: {cols}")
        
        # Analyze confidence distribution if available
        confidence_col = None
        for col in df.columns:
            if 'confidence' in col.lower():
                confidence_col = col
                break
        
        if confidence_col:
            print(f"\n📈 CONFIDENCE DISTRIBUTION ({confidence_col}):")
            conf_dist = df[confidence_col].value_counts()
            for conf, count in conf_dist.items():
                percentage = (count / len(df)) * 100
                print(f"  {conf}: {count} addresses ({percentage:.1f}%)")
            
            # Cross-analysis with routing if available
            routing_col = None
            for col in df.columns:
                if 'routing' in col.lower():
                    routing_col = col
                    break
            
            if routing_col:
                print(f"\n🎯 CONFIDENCE vs ROUTING ANALYSIS:")
                cross_tab = pd.crosstab(df[confidence_col], df[routing_col], margins=True)
                print(cross_tab)
        
        # Sample some HIGH confidence addresses to understand quality
        if confidence_col:
            high_conf = df[df[confidence_col] == 'HIGH']
            if len(high_conf) > 0:
                print(f"\n🎯 HIGH CONFIDENCE SAMPLE (showing first 5 of {len(high_conf)}):")
                
                # Show relevant columns for first few HIGH confidence addresses
                display_cols = [col for col in df.columns if any(keyword in col.lower() 
                    for keyword in ['name', 'address', 'postal', 'confidence', 'routing', 'ubicazione'])]
                
                if display_cols:
                    sample = high_conf[display_cols].head()
                    for idx, row in sample.iterrows():
                        print(f"\nRecord {idx + 1}:")
                        for col in display_cols:
                            print(f"  {col}: {row[col]}")
        
    except Exception as e:
        print(f"❌ Error in pattern analysis: {e}")

if __name__ == "__main__":
    # Campaign results file path
    results_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2018\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2018_Results.xlsx"
    
    print("🚀 STARTING CONFIDENCE CLASSIFICATION ANALYSIS")
    print("=" * 60)
    print()
    
    # Run analysis
    analyze_campaign_results(results_file)
    analyze_address_patterns(results_file)
    
    print("✅ Analysis complete!")
    print("\nNext steps:")
    print("1. Review the confidence distribution")
    print("2. Examine HIGH confidence address quality")
    print("3. Identify optimization opportunities")
    print("4. Propose improved classification thresholds")