#!/usr/bin/env python3
"""
Data Exploration Script for Campaign4 Dashboard Analysis
This script explores the structure and content of the Excel files used by dashboard.py
"""

import pandas as pd
import numpy as np
import os

def explore_excel_file(file_path, file_description):
    """
    Comprehensive exploration of an Excel file's structure and content
    """
    print(f"\n{'='*80}")
    print(f"EXPLORING: {file_description}")
    print(f"File: {file_path}")
    print(f"{'='*80}")
    
    if not os.path.exists(file_path):
        print(f"❌ FILE NOT FOUND: {file_path}")
        return
    
    try:
        # Get all sheet names
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        print(f"\n📊 SHEET NAMES ({len(sheet_names)} sheets):")
        for i, sheet in enumerate(sheet_names, 1):
            print(f"  {i}. {sheet}")
        
        # Explore each sheet
        for sheet_name in sheet_names:
            print(f"\n{'-'*60}")
            print(f"SHEET: {sheet_name}")
            print(f"{'-'*60}")
            
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                print(f"📏 DIMENSIONS: {df.shape[0]} rows x {df.shape[1]} columns")
                
                if df.empty:
                    print("⚠️  EMPTY SHEET")
                    continue
                
                print(f"\n📋 COLUMN NAMES ({len(df.columns)} columns):")
                for i, col in enumerate(df.columns, 1):
                    print(f"  {i:2d}. {col}")
                
                print(f"\n🎯 DATA TYPES:")
                for col, dtype in df.dtypes.items():
                    print(f"  {col:<30}: {dtype}")
                
                print(f"\n🔍 SAMPLE DATA (first 3 rows):")
                print(df.head(3).to_string(max_colwidth=50))
                
                print(f"\n📈 BASIC STATISTICS:")
                print(f"  - Non-null values per column:")
                for col in df.columns:
                    null_count = df[col].isnull().sum()
                    non_null_count = len(df) - null_count
                    print(f"    {col:<30}: {non_null_count:>6} ({(non_null_count/len(df)*100):5.1f}%)")
                
                # Show unique values for categorical columns with few unique values
                print(f"\n🏷️  CATEGORICAL COLUMNS (<=20 unique values):")
                for col in df.columns:
                    if df[col].dtype == 'object' or df[col].nunique() <= 20:
                        unique_count = df[col].nunique()
                        if unique_count <= 20 and unique_count > 1:
                            unique_vals = df[col].value_counts().head(10)
                            print(f"  {col} ({unique_count} unique values):")
                            for val, count in unique_vals.items():
                                print(f"    '{val}': {count}")
                
                # Numeric columns summary
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    print(f"\n📊 NUMERIC COLUMNS SUMMARY:")
                    print(df[numeric_cols].describe().round(2))
                
            except Exception as e:
                print(f"❌ ERROR reading sheet {sheet_name}: {e}")
                continue
                
    except Exception as e:
        print(f"❌ ERROR reading file: {e}")

def analyze_dashboard_data_usage():
    """
    Analyze how the dashboard.py script uses the data
    """
    print(f"\n{'='*80}")
    print("DASHBOARD DATA USAGE ANALYSIS")
    print(f"{'='*80}")
    
    print("\n📋 DASHBOARD.PY USES THESE SHEETS:")
    sheets_used = {
        'Input_File': 'Sheet1 from Input_Castiglione Casalpusterlengo CP.xlsx',
        'All_Raw_Data': 'All_Raw_Data from Campaign4_Results.xlsx',
        'Final_Mailing_List': 'Final_Mailing_List from Campaign4_Results.xlsx',
        'All_Validation_Ready': 'All_Validation_Ready from Campaign4_Results.xlsx',
        'Address_Quality_Distribution': 'Address_Quality_Distribution from Campaign4_Results.xlsx'
    }
    
    for key, description in sheets_used.items():
        print(f"  - {key}: {description}")
    
    print(f"\n🎯 KEY COLUMNS USED BY DASHBOARD:")
    key_columns = {
        'Input File': ['comune', 'foglio', 'particella', 'Area'],
        'All_Raw_Data': ['comune_input', 'foglio_input', 'particella_input'],
        'Final_Mailing_List': ['Municipality', 'Parcels', 'cf'],
        'Address_Quality_Distribution': ['Quality Level', 'Count']
    }
    
    for sheet, cols in key_columns.items():
        print(f"  {sheet}:")
        for col in cols:
            print(f"    - {col}")

def identify_potential_improvements():
    """
    Identify potential areas for dashboard improvements
    """
    print(f"\n{'='*80}")
    print("POTENTIAL DASHBOARD IMPROVEMENTS")
    print(f"{'='*80}")
    
    improvements = [
        "📊 Time Series Analysis: Track campaign progression over time",
        "🗺️  Enhanced Geographic Visualization: Interactive maps with parcel locations",
        "💰 Financial Metrics: Cost per parcel, ROI calculations",
        "⚡ Performance Metrics: Processing time, success rates by municipality",
        "📈 Trend Analysis: Compare with previous campaigns",
        "🎯 Success Prediction: ML-based success probability scoring",
        "📱 Responsive Design: Mobile-friendly dashboard",
        "🔄 Real-time Updates: Live data refresh capabilities",
        "📋 Detailed Drill-down: Click-through from summary to detail views",
        "📊 Advanced Charts: Sankey diagrams, heat maps, box plots"
    ]
    
    for improvement in improvements:
        print(f"  {improvement}")

def main():
    """
    Main function to run comprehensive data exploration
    """
    print("🔍 COMPREHENSIVE DATA EXPLORATION FOR DASHBOARD ANALYSIS")
    print("=" * 80)
    
    # File paths
    campaign_results_path = "Campaign4_Results.xlsx"
    input_file_path = "Input_Castiglione Casalpusterlengo CP.xlsx"
    
    # Explore both Excel files
    explore_excel_file(campaign_results_path, "Campaign4 Results (Main Data)")
    explore_excel_file(input_file_path, "Input File (Original Parcels)")
    
    # Analyze dashboard usage
    analyze_dashboard_data_usage()
    
    # Identify improvements
    identify_potential_improvements()
    
    print(f"\n{'='*80}")
    print("✅ DATA EXPLORATION COMPLETE!")
    print("📁 Run this script in Spyder and share the output for detailed analysis.")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()