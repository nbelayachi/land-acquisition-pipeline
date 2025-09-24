#!/usr/bin/env python3
"""
Investigate Input Data Discrepancy
Compare Campaign_Summary vs Raw Input Data vs All_Validation_Ready
"""

import pandas as pd
import os

def investigate_input_data():
    print("🔍 INVESTIGATING INPUT DATA DISCREPANCY")
    print("=" * 60)
    
    # File paths
    excel_path = "data/Campaign4_Results.xlsx"
    input_file = "data/Input_Castiglione Casalpusterlengo CP.xlsx"
    
    try:
        # Load Campaign_Summary
        campaign_summary = pd.read_excel(excel_path, sheet_name='Campaign_Summary')
        cs = campaign_summary
        clean_rows = cs['comune'].notna() & (cs['comune'] != '')
        cs_clean = cs[clean_rows].reset_index(drop=True)
        
        print("📊 CAMPAIGN_SUMMARY DATA:")
        print("=" * 40)
        print(f"   Rows: {len(cs_clean)}")
        print(f"   Input_Parcels sum: {cs_clean['Input_Parcels'].sum()}")
        print(f"   Input_Area_Ha sum: {cs_clean['Input_Area_Ha'].sum():.1f} Ha")
        
        print(f"\n   Municipality breakdown:")
        for _, row in cs_clean.iterrows():
            print(f"     {row['comune']}: {row['Input_Parcels']} parcels, {row['Input_Area_Ha']:.1f} Ha")
        
        # Load All_Validation_Ready to check area
        all_validation = pd.read_excel(excel_path, sheet_name='All_Validation_Ready')
        print(f"\n📋 ALL_VALIDATION_READY DATA:")
        print("=" * 40)
        print(f"   Total records: {len(all_validation)}")
        
        if 'Area' in all_validation.columns:
            total_area_validation = all_validation['Area'].sum()
            print(f"   Total Area: {total_area_validation:.1f} Ha")
            print(f"   Area range: {all_validation['Area'].min():.3f} to {all_validation['Area'].max():.1f} Ha")
            print(f"   Average area per record: {all_validation['Area'].mean():.2f} Ha")
        
        # Check for Raw_Data sheet
        try:
            print(f"\n📊 CHECKING FOR RAW_DATA SHEET:")
            print("=" * 40)
            
            # Get all sheet names
            with pd.ExcelFile(excel_path) as xls:
                sheet_names = xls.sheet_names
                print(f"   Available sheets: {sheet_names}")
            
            # Look for raw data sheets
            raw_sheets = [sheet for sheet in sheet_names if 'raw' in sheet.lower() or 'data' in sheet.lower()]
            if raw_sheets:
                print(f"   Found potential raw data sheets: {raw_sheets}")
                
                for sheet in raw_sheets:
                    try:
                        raw_data = pd.read_excel(excel_path, sheet_name=sheet)
                        print(f"   {sheet}: {len(raw_data)} records")
                        
                        if 'Area' in raw_data.columns:
                            raw_area = raw_data['Area'].sum()
                            print(f"     Total Area: {raw_area:.1f} Ha")
                        elif any('area' in col.lower() for col in raw_data.columns):
                            area_cols = [col for col in raw_data.columns if 'area' in col.lower()]
                            print(f"     Area columns found: {area_cols}")
                            for col in area_cols:
                                if pd.api.types.is_numeric_dtype(raw_data[col]):
                                    print(f"       {col} sum: {raw_data[col].sum():.1f}")
                        
                    except Exception as e:
                        print(f"   Error reading {sheet}: {e}")
            else:
                print("   No obvious raw data sheets found")
                
        except Exception as e:
            print(f"   Error checking sheets: {e}")
        
        # Load the input file
        if os.path.exists(input_file):
            print(f"\n📄 INPUT FILE ANALYSIS:")
            print("=" * 40)
            print(f"   File: {input_file}")
            
            # Get sheet names from input file
            with pd.ExcelFile(input_file) as xls:
                input_sheet_names = xls.sheet_names
                print(f"   Available sheets: {input_sheet_names}")
            
            # Analyze each sheet
            for sheet_name in input_sheet_names:
                try:
                    input_data = pd.read_excel(input_file, sheet_name=sheet_name)
                    print(f"\n   Sheet: {sheet_name}")
                    print(f"     Rows: {len(input_data)}")
                    print(f"     Columns: {list(input_data.columns)}")
                    
                    # Look for area columns
                    area_columns = [col for col in input_data.columns if 'area' in col.lower() or 'superficie' in col.lower()]
                    if area_columns:
                        print(f"     Area columns: {area_columns}")
                        for col in area_columns:
                            if pd.api.types.is_numeric_dtype(input_data[col]):
                                total_area = input_data[col].sum()
                                print(f"       {col} total: {total_area:.1f}")
                    
                    # Look for municipality info
                    muni_columns = [col for col in input_data.columns if 'comun' in col.lower() or 'municipality' in col.lower()]
                    if muni_columns:
                        print(f"     Municipality columns: {muni_columns}")
                        for col in muni_columns:
                            if input_data[col].dtype == 'object':
                                unique_munis = input_data[col].dropna().unique()
                                print(f"       {col} unique values: {list(unique_munis)}")
                    
                    # Check for parcel identifiers
                    parcel_columns = [col for col in input_data.columns if any(term in col.lower() for term in ['foglio', 'particella', 'parcel'])]
                    if parcel_columns:
                        print(f"     Parcel columns: {parcel_columns}")
                        
                        # Count unique parcels
                        if len(parcel_columns) >= 2:
                            unique_parcels = input_data[parcel_columns[:2]].drop_duplicates()
                            print(f"       Unique parcels: {len(unique_parcels)}")
                    
                except Exception as e:
                    print(f"   Error reading sheet {sheet_name}: {e}")
        else:
            print(f"\n❌ INPUT FILE NOT FOUND: {input_file}")
        
        # Compare areas
        print(f"\n🔄 AREA COMPARISON:")
        print("=" * 40)
        campaign_area = cs_clean['Input_Area_Ha'].sum()
        validation_area = all_validation['Area'].sum() if 'Area' in all_validation.columns else 0
        
        print(f"   Campaign_Summary Input_Area_Ha: {campaign_area:.1f} Ha")
        print(f"   All_Validation_Ready Area: {validation_area:.1f} Ha")
        print(f"   Ratio (Validation/Campaign): {validation_area/campaign_area:.1f}x")
        
        if validation_area > campaign_area * 2:
            print(f"   ⚠️  DISCREPANCY: Validation area is {validation_area/campaign_area:.1f}x larger")
            print(f"   This suggests Input_Area_Ha in Campaign_Summary might be incomplete")
        
        print(f"\n💡 RECOMMENDATIONS:")
        print("=" * 40)
        print("1. Check if Input_Area_Ha in Campaign_Summary represents subset of total input")
        print("2. Use All_Validation_Ready Area sum for total area metric")
        print("3. Verify input file contains complete parcel area data")
        print("4. Consider Input_Area_Ha might be filtered/processed area, not raw input")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_input_data()