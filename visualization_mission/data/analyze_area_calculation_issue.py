#!/usr/bin/env python3
"""
Analysis Script: Geographic Distribution Area Calculation Issue
================================================================
Purpose: Investigate area calculation redundancy and municipality format differences
"""

import pandas as pd
import sys

def analyze_area_calculation():
    """Analyze the area calculation issue in geographic distribution"""
    
    try:
        # Load the Excel files
        print("=== AREA CALCULATION ANALYSIS ===\n")
        
        # Load data files
        excel_path = "Campaign4_Results.xlsx"
        input_path = "Input_Castiglione Casalpusterlengo CP.xlsx"
        
        print(f"Loading: {excel_path}")
        campaign_data = pd.ExcelFile(excel_path)
        
        print(f"Loading: {input_path}")
        input_data = pd.ExcelFile(input_path)
        
        print(f"Excel sheets available: {campaign_data.sheet_names}\n")
        
        # 1. Examine Final_Mailing_List structure
        print("=== 1. FINAL_MAILING_LIST ANALYSIS ===")
        final_mailing = pd.read_excel(excel_path, sheet_name='Final_Mailing_List')
        print(f"Final_Mailing_List shape: {final_mailing.shape}")
        print(f"Columns: {list(final_mailing.columns)}")
        
        # Check municipality format
        if 'Municipality' in final_mailing.columns:
            print(f"\nMunicipality column samples from Final_Mailing_List:")
            print(final_mailing['Municipality'].value_counts().head(10))
            print(f"Unique municipalities: {final_mailing['Municipality'].nunique()}")
        
        # Check parcels format
        if 'Parcels' in final_mailing.columns:
            print(f"\nParcels column samples:")
            print(final_mailing['Parcels'].head(5).tolist())
            print(f"Type of Parcels column: {type(final_mailing['Parcels'].iloc[0])}")
        
        print("\n" + "="*60)
        
        # 2. Examine Input file structure  
        print("\n=== 2. INPUT FILE ANALYSIS ===")
        input_df = pd.read_excel(input_path)
        print(f"Input file shape: {input_df.shape}")
        print(f"Columns: {list(input_df.columns)}")
        
        # Check municipality format in input
        municipality_cols = [col for col in input_df.columns if 'munic' in col.lower() or 'comune' in col.lower()]
        print(f"Municipality-related columns: {municipality_cols}")
        
        for col in municipality_cols[:2]:  # Check first 2 municipality columns
            print(f"\n{col} samples from Input file:")
            print(input_df[col].value_counts().head(10))
            print(f"Unique values in {col}: {input_df[col].nunique()}")
        
        # Check area column
        area_cols = [col for col in input_df.columns if 'area' in col.lower() or 'superficie' in col.lower()]
        print(f"\nArea-related columns: {area_cols}")
        
        for col in area_cols[:2]:
            print(f"\n{col} statistics:")
            print(input_df[col].describe())
        
        print("\n" + "="*60)
        
        # 3. Analyze current Campaign_Summary approach
        print("\n=== 3. CAMPAIGN_SUMMARY ANALYSIS ===")
        campaign_summary = pd.read_excel(excel_path, sheet_name='Campaign_Summary')
        print(f"Campaign_Summary shape: {campaign_summary.shape}")
        print(f"Columns: {list(campaign_summary.columns)}")
        
        print(f"\nCampaign_Summary municipality samples:")
        if 'comune' in campaign_summary.columns:
            print(campaign_summary['comune'].value_counts())
        
        area_cols_campaign = [col for col in campaign_summary.columns if 'area' in col.lower()]
        print(f"\nArea columns in Campaign_Summary: {area_cols_campaign}")
        
        for col in area_cols_campaign:
            print(f"\n{col} statistics:")
            print(campaign_summary[col].describe())
            print(f"Total {col}: {campaign_summary[col].sum():.2f}")
        
        print("\n" + "="*60)
        
        # 4. Identify the redundancy issue
        print("\n=== 4. REDUNDANCY ISSUE IDENTIFICATION ===")
        
        # Parse parcels from Final_Mailing_List
        if 'Parcels' in final_mailing.columns:
            print("Analyzing parcels extraction from Final_Mailing_List...")
            
            # Extract unique parcels
            all_parcels = []
            for parcels_str in final_mailing['Parcels'].dropna():
                try:
                    # Assuming format like: "comune-foglio-particella, comune-foglio-particella, ..."
                    parcels_list = [p.strip() for p in str(parcels_str).split(',')]
                    all_parcels.extend(parcels_list)
                except:
                    continue
            
            print(f"Total parcel entries extracted: {len(all_parcels)}")
            unique_parcels = list(set(all_parcels))
            print(f"Unique parcels: {len(unique_parcels)}")
            print(f"Sample parcels: {unique_parcels[:5]}")
            
            # Try to match with input file format
            print(f"\nAttempting to parse parcel format...")
            sample_parcel = unique_parcels[0] if unique_parcels else ""
            print(f"Sample parcel format: '{sample_parcel}'")
            
            # Check if parcel contains municipality info
            if '-' in sample_parcel:
                parts = sample_parcel.split('-')
                print(f"Parcel parts: {parts}")
                print(f"Possible municipality: '{parts[0]}'")
        
        print("\n=== ANALYSIS COMPLETE ===")
        print("Review the output above to understand:")
        print("1. Municipality format differences between files")
        print("2. Current area calculation method in Campaign_Summary") 
        print("3. How parcels are stored in Final_Mailing_List")
        print("4. Potential redundancy in area counting")
        
    except Exception as e:
        print(f"Error in analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_area_calculation()