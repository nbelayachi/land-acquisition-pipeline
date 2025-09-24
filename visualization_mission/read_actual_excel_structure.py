#!/usr/bin/env python3
"""
Read Actual Excel Structure
Understand the real data structure and columns in Campaign4_Results.xlsx
"""

import pandas as pd
import os
import sys # Import the sys module to redirect stdout

def read_excel_structure():
    """
    Reads the structure of two Excel files and prints the analysis.
    The output of this function will be redirected to a file.
    """
    print("📊 READING ACTUAL EXCEL STRUCTURE")
    print("=" * 60)
    
    excel_path = "data/Campaign4_Results.xlsx"
    input_file = "data/Input_Castiglione Casalpusterlengo CP.xlsx"
    
    try:
        # Get all sheet names
        with pd.ExcelFile(excel_path) as xls:
            sheet_names = xls.sheet_names
        
        print(f"📋 Available sheets in {excel_path}:")
        for i, sheet in enumerate(sheet_names, 1):
            print(f"   {i}. {sheet}")
        
        # Read each sheet and show structure
        for sheet_name in sheet_names:
            print(f"\n🔍 SHEET: {sheet_name}")
            print("=" * 40)
            
            try:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                print(f"   Rows: {len(df)}")
                print(f"   Columns: {len(df.columns)}")
                
                print(f"   Column names:")
                for i, col in enumerate(df.columns, 1):
                    print(f"     {i:2d}. {col}")
                
                # Show first few rows for key columns
                if len(df) > 0:
                    print(f"\n   Sample data (first 3 rows):")
                    sample = df.head(3)
                    for col in df.columns:
                        if df[col].dtype in ['object', 'int64', 'float64']:
                            sample_values = sample[col].tolist()
                            print(f"     {col}: {sample_values}")
            
            except Exception as e:
                print(f"   ❌ Error reading {sheet_name}: {e}")
        
        # Read input file structure
        print(f"\n📄 INPUT FILE STRUCTURE: {input_file}")
        print("=" * 60)
        
        if os.path.exists(input_file):
            with pd.ExcelFile(input_file) as xls:
                input_sheet_names = xls.sheet_names
            
            print(f"   Available sheets:")
            for i, sheet in enumerate(input_sheet_names, 1):
                print(f"     {i}. {sheet}")
            
            for sheet_name in input_sheet_names:
                print(f"\n   🔍 SHEET: {sheet_name}")
                print("   " + "=" * 30)
                
                try:
                    df = pd.read_excel(input_file, sheet_name=sheet_name)
                    print(f"     Rows: {len(df)}")
                    print(f"     Columns: {len(df.columns)}")
                    
                    print(f"     Column names:")
                    for i, col in enumerate(df.columns, 1):
                        print(f"       {i:2d}. {col}")
                    
                    # Show sample data
                    if len(df) > 0:
                        print(f"\n     Sample data (first 3 rows):")
                        sample = df.head(3)
                        for col in df.columns:
                            if df[col].dtype in ['object', 'int64', 'float64']:
                                sample_values = sample[col].tolist()
                                print(f"       {col}: {sample_values}")
                
                except Exception as e:
                    print(f"     ❌ Error reading {sheet_name}: {e}")
        else:
            print(f"   ❌ Input file not found: {input_file}")
        
        print(f"\n💡 SUMMARY:")
        print("=" * 40)
        print(f"1. Campaign4_Results.xlsx has {len(sheet_names)} sheets")
        print(f"2. Use this structure for accurate data analysis")
        print(f"3. Column names and data types are now known")
        print(f"4. Can create properly informed enhancement analysis")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Define the output file name
    output_filename = "excel_structure_report.txt"
    
    # Save the original stdout so we can restore it later
    original_stdout = sys.stdout  
    
    print(f"🚀 Generating report... The output will be saved to {output_filename}")

    # Use a 'with' statement to open the file and redirect stdout
    with open(output_filename, 'w', encoding='utf-8') as f:
        sys.stdout = f  # Redirect stdout to the file
        read_excel_structure() # Call the function whose output you want to capture
    
    # Restore the original stdout
    sys.stdout = original_stdout
    
    print(f"✅ Report successfully generated and saved to '{output_filename}'")