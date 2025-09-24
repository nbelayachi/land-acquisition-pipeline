#!/usr/bin/env python3
"""
Critical Analysis: Parcel Count Consistency Investigation
=========================================================
Purpose: Resolve the impossible "more parcels than input" inconsistency
"""

import pandas as pd
import sys

def analyze_parcel_consistency():
    """Deep analysis of parcel consistency across data sources"""
    
    try:
        print("=== PARCEL CONSISTENCY DEEP ANALYSIS ===\n")
        
        # Load files
        excel_path = "Campaign4_Results.xlsx"
        input_path = "Input_Castiglione Casalpusterlengo CP.xlsx"
        
        # Load Input file
        print("=== 1. INPUT FILE DETAILED ANALYSIS ===")
        input_df = pd.read_excel(input_path)
        print(f"Input file shape: {input_df.shape}")
        
        # Create parcel ID for input
        input_df['input_parcel_id'] = input_df['comune'].astype(str) + '-' + input_df['foglio'].astype(str) + '-' + input_df['particella'].astype(str)
        input_unique_parcels = input_df['input_parcel_id'].nunique()
        input_total_area = input_df['Area'].sum()
        
        print(f"Input unique parcels: {input_unique_parcels}")
        print(f"Input total area: {input_total_area:.2f} Ha")
        print(f"Input area per parcel (avg): {input_total_area/input_unique_parcels:.2f} Ha")
        
        # Check for duplicates in input
        if len(input_df) != input_unique_parcels:
            print(f"WARNING: Input has duplicates! {len(input_df)} rows vs {input_unique_parcels} unique")
            duplicates = input_df['input_parcel_id'].value_counts()
            print("Duplicate parcels in input:")
            print(duplicates[duplicates > 1].head())
        
        print("\nInput parcel samples:")
        print(input_df[['comune', 'foglio', 'particella', 'Area', 'input_parcel_id']].head())
        
        print("\n" + "="*60)
        
        # Load All_Raw_Data
        print("\n=== 2. ALL_RAW_DATA DETAILED ANALYSIS ===")
        raw_data = pd.read_excel(excel_path, sheet_name='All_Raw_Data')
        print(f"All_Raw_Data shape: {raw_data.shape}")
        
        # Create parcel ID using INPUT columns from raw data
        raw_data['api_parcel_id'] = raw_data['comune_input'].astype(str) + '-' + raw_data['foglio_input'].astype(str) + '-' + raw_data['particella_input'].astype(str)
        api_unique_parcels = raw_data['api_parcel_id'].nunique()
        
        print(f"API unique parcels (from input columns): {api_unique_parcels}")
        print(f"API total records: {len(raw_data)}")
        print(f"Duplication factor: {len(raw_data) / api_unique_parcels:.2f}")
        
        # Check area consistency
        if 'Area' in raw_data.columns:
            # Group by unique parcel and take first area (should be same for same parcel)
            unique_parcel_areas = raw_data.groupby('api_parcel_id')['Area'].first()
            api_total_area = unique_parcel_areas.sum()
            print(f"API total area (unique parcels): {api_total_area:.2f} Ha")
            
            # Check if areas match input
            print(f"\nArea comparison:")
            print(f"Input total area: {input_total_area:.2f} Ha")
            print(f"API total area: {api_total_area:.2f} Ha")
            print(f"Area difference: {api_total_area - input_total_area:.2f} Ha")
        
        print("\nAPI parcel samples:")
        sample_data = raw_data[['comune_input', 'foglio_input', 'particella_input', 'Area', 'api_parcel_id']].drop_duplicates('api_parcel_id')
        print(sample_data.head())
        
        print("\n" + "="*60)
        
        # Compare Input vs API parcels
        print("\n=== 3. INPUT vs API PARCEL COMPARISON ===")
        
        # Find parcels in input but not in API
        input_parcels_set = set(input_df['input_parcel_id'])
        api_parcels_set = set(raw_data['api_parcel_id'])
        
        missing_from_api = input_parcels_set - api_parcels_set
        extra_in_api = api_parcels_set - input_parcels_set
        common_parcels = input_parcels_set & api_parcels_set
        
        print(f"Input parcels: {len(input_parcels_set)}")
        print(f"API parcels: {len(api_parcels_set)}")
        print(f"Common parcels: {len(common_parcels)}")
        print(f"Missing from API: {len(missing_from_api)}")
        print(f"Extra in API: {len(extra_in_api)}")
        
        if missing_from_api:
            print(f"\nParcels in input but missing from API (first 5):")
            for parcel in list(missing_from_api)[:5]:
                print(f"  {parcel}")
        
        if extra_in_api:
            print(f"\nParcels in API but not in input (first 5):")
            for parcel in list(extra_in_api)[:5]:
                print(f"  {parcel}")
        
        print("\n" + "="*60)
        
        # Check Enhanced_Funnel_Analysis vs Reality
        print("\n=== 4. ENHANCED_FUNNEL_ANALYSIS vs REALITY ===")
        if 'Enhanced_Funnel_Analysis' in pd.ExcelFile(excel_path).sheet_names:
            funnel_analysis = pd.read_excel(excel_path, sheet_name='Enhanced_Funnel_Analysis')
            
            print("Enhanced_Funnel_Analysis data:")
            for _, row in funnel_analysis.iterrows():
                stage = row.get('Stage', 'N/A')
                count = row.get('Count', 'N/A') 
                hectares = row.get('Hectares', 'N/A')
                print(f"  {stage}: {count} parcels, {hectares} Ha")
            
            # Compare with our calculations
            print(f"\nReality Check:")
            print(f"Input File: {input_unique_parcels} parcels, {input_total_area:.1f} Ha")
            print(f"API Raw Data: {api_unique_parcels} unique parcels, {api_total_area:.1f} Ha")
            
            # Check if funnel input matches our input calculation
            first_funnel_row = funnel_analysis.iloc[0]
            funnel_input_count = first_funnel_row.get('Count', 0)
            funnel_input_area = first_funnel_row.get('Hectares', 0)
            
            print(f"\nFunnel Analysis Input Stage: {funnel_input_count} parcels, {funnel_input_area} Ha")
            print(f"Our Input Calculation: {input_unique_parcels} parcels, {input_total_area:.1f} Ha")
            
            if funnel_input_count != input_unique_parcels:
                print(f"ERROR: Funnel input count mismatch!")
            if abs(funnel_input_area - input_total_area) > 1:
                print(f"ERROR: Funnel input area mismatch!")
        
        print("\n=== CONCLUSIONS ===")
        print("1. How many unique parcels are really in the input?")
        print("2. Does the API actually have more parcels than input?") 
        print("3. Are the Enhanced_Funnel_Analysis numbers correct?")
        print("4. What's the correct progression for the funnel?")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_parcel_consistency()