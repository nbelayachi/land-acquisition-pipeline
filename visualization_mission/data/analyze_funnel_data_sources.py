#!/usr/bin/env python3
"""
Analysis Script: Funnel Data Sources and Logic Verification
===========================================================
Purpose: Verify if funnel calculations are correct and identify data sources
"""

import pandas as pd
import sys

def analyze_funnel_sources():
    """Analyze funnel data sources and verify calculation logic"""
    
    try:
        print("=== FUNNEL DATA SOURCES ANALYSIS ===\n")
        
        # Load the Excel file
        excel_path = "Campaign4_Results.xlsx"
        input_path = "Input_Castiglione Casalpusterlengo CP.xlsx"
        
        print(f"Loading: {excel_path}")
        campaign_data = pd.ExcelFile(excel_path)
        
        print(f"Available sheets: {campaign_data.sheet_names}\n")
        
        # 1. Check Enhanced_Funnel_Analysis sheet
        print("=== 1. ENHANCED_FUNNEL_ANALYSIS SHEET ===")
        if 'Enhanced_Funnel_Analysis' in campaign_data.sheet_names:
            funnel_analysis = pd.read_excel(excel_path, sheet_name='Enhanced_Funnel_Analysis')
            print(f"Enhanced_Funnel_Analysis shape: {funnel_analysis.shape}")
            print(f"Columns: {list(funnel_analysis.columns)}")
            print(f"\nData preview:")
            print(funnel_analysis.head(10))
            
            # Check if hectares column exists
            if 'Hectares' in funnel_analysis.columns:
                print(f"\nHectares column statistics:")
                print(funnel_analysis['Hectares'].describe())
            
            # Check stages and counts
            if 'Stage' in funnel_analysis.columns and 'Count' in funnel_analysis.columns:
                print(f"\nStages and counts:")
                for _, row in funnel_analysis.iterrows():
                    stage = row.get('Stage', 'N/A')
                    count = row.get('Count', 'N/A')
                    hectares = row.get('Hectares', 'N/A')
                    print(f"  {stage}: {count} parcels, {hectares} Ha")
        else:
            print("Enhanced_Funnel_Analysis sheet not found!")
        
        print("\n" + "="*60)
        
        # 2. Check All_Raw_Data sheet
        print("\n=== 2. ALL_RAW_DATA ANALYSIS ===")
        if 'All_Raw_Data' in campaign_data.sheet_names:
            raw_data = pd.read_excel(excel_path, sheet_name='All_Raw_Data')
            print(f"All_Raw_Data shape: {raw_data.shape}")
            print(f"Columns: {list(raw_data.columns)}")
            
            # Check if this is really 2975 unique parcels
            print(f"Total rows in All_Raw_Data: {len(raw_data)}")
            
            # Try to identify unique parcels
            parcel_cols = [col for col in raw_data.columns if any(x in col.lower() for x in ['parcel', 'particella', 'foglio', 'comune'])]
            print(f"Parcel-related columns: {parcel_cols}")
            
            # Check for comune, foglio, particella combo
            if all(col in raw_data.columns for col in ['comune', 'foglio', 'particella']):
                raw_data['parcel_id'] = raw_data['comune'].astype(str) + '-' + raw_data['foglio'].astype(str) + '-' + raw_data['particella'].astype(str)
                unique_parcels_raw = raw_data['parcel_id'].nunique()
                print(f"Unique parcels in All_Raw_Data (comune-foglio-particella): {unique_parcels_raw}")
                print(f"Total rows: {len(raw_data)}")
                print(f"Duplicate factor: {len(raw_data) / unique_parcels_raw:.2f}")
        else:
            print("All_Raw_Data sheet not found!")
        
        print("\n" + "="*60)
        
        # 3. Check All_Validation_Ready
        print("\n=== 3. ALL_VALIDATION_READY ANALYSIS ===")
        if 'All_Validation_Ready' in campaign_data.sheet_names:
            validation_ready = pd.read_excel(excel_path, sheet_name='All_Validation_Ready')
            print(f"All_Validation_Ready shape: {validation_ready.shape}")
            print(f"Columns: {list(validation_ready.columns)}")
            
            # Check unique parcels
            if all(col in validation_ready.columns for col in ['comune', 'foglio', 'particella']):
                validation_ready['parcel_id'] = validation_ready['comune'].astype(str) + '-' + validation_ready['foglio'].astype(str) + '-' + validation_ready['particella'].astype(str)
                unique_parcels_validation = validation_ready['parcel_id'].nunique()
                print(f"Unique parcels in All_Validation_Ready: {unique_parcels_validation}")
                print(f"Total rows: {len(validation_ready)}")
        else:
            print("All_Validation_Ready sheet not found!")
        
        print("\n" + "="*60)
        
        # 4. Check Final_Mailing_List
        print("\n=== 4. FINAL_MAILING_LIST ANALYSIS ===")
        if 'Final_Mailing_List' in campaign_data.sheet_names:
            final_mailing = pd.read_excel(excel_path, sheet_name='Final_Mailing_List')
            print(f"Final_Mailing_List shape: {final_mailing.shape}")
            print(f"Columns: {list(final_mailing.columns)}")
            
            # Count unique owners/entities
            if 'Name' in final_mailing.columns:
                unique_owners = final_mailing['Name'].nunique()
                print(f"Unique owners/entities in Final_Mailing_List: {unique_owners}")
            
            # Analyze parcels column for unique parcel count
            if 'Parcels' in final_mailing.columns:
                all_parcels = []
                for parcels_str in final_mailing['Parcels'].dropna():
                    parcels_list = [p.strip() for p in str(parcels_str).split(',')]
                    all_parcels.extend(parcels_list)
                
                unique_parcels_final = len(set(all_parcels))
                print(f"Unique parcels referenced in Final_Mailing_List: {unique_parcels_final}")
                print(f"Total parcel references: {len(all_parcels)}")
        else:
            print("Final_Mailing_List sheet not found!")
        
        print("\n" + "="*60)
        
        # 5. Check Input file
        print("\n=== 5. INPUT FILE ANALYSIS ===")
        input_df = pd.read_excel(input_path)
        print(f"Input file shape: {input_df.shape}")
        
        # Check unique parcels in input
        parcel_cols = [col for col in input_df.columns if any(x in col.lower() for x in ['comune', 'foglio', 'particella'])]
        print(f"Parcel-related columns in input: {parcel_cols}")
        
        if len(parcel_cols) >= 3:
            # Try to create parcel ID
            comune_col = [c for c in parcel_cols if 'comune' in c.lower()][0]
            foglio_col = [c for c in parcel_cols if 'foglio' in c.lower()][0] 
            particella_col = [c for c in parcel_cols if 'particella' in c.lower()][0]
            
            input_df['parcel_id'] = input_df[comune_col].astype(str) + '-' + input_df[foglio_col].astype(str) + '-' + input_df[particella_col].astype(str)
            unique_parcels_input = input_df['parcel_id'].nunique()
            print(f"Unique parcels in Input file: {unique_parcels_input}")
            print(f"Total rows in Input: {len(input_df)}")
        
        print("\n=== FUNNEL LOGIC VERIFICATION ===")
        print("Based on the analysis above, verify:")
        print("1. Is 2975 from All_Raw_Data actually unique parcels?")
        print("2. Are Enhanced_Funnel_Analysis calculations correct?")
        print("3. What's the real conversion rate based on unique parcels?")
        print("4. How should area evolution be calculated at each stage?")
        
    except Exception as e:
        print(f"Error in analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_funnel_sources()