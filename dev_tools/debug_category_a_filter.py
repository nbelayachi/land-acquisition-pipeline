#!/usr/bin/env python3
"""
Debug Category A Filter Script
Corrects the analysis of Category A filtering to understand the actual business logic
Usage: Run in Spyder and paste the output back for review
"""

import pandas as pd
import numpy as np

def debug_category_a_filtering(excel_path):
    """
    Properly analyze Category A filtering and data flow
    """
    print("="*80)
    print("CATEGORY A FILTER DEBUG ANALYSIS")
    print("="*80)
    print(f"File: {excel_path}")
    print()
    
    try:
        # Read raw data and validation ready
        df_raw = pd.read_excel(excel_path, sheet_name='All_Raw_Data')
        df_validation = pd.read_excel(excel_path, sheet_name='All_Validation_Ready')
        
        print("📊 RAW DATA CLASSIFICATION ANALYSIS:")
        print("-" * 50)
        
        # Show all classamento values
        print("All classamento values in raw data:")
        classamento_counts = df_raw['classamento'].value_counts()
        for classamento, count in classamento_counts.items():
            print(f"  {classamento}: {count} records")
        print()
        
        # Test different Category A filter patterns
        print("🔍 TESTING CATEGORY A FILTER PATTERNS:")
        print("-" * 50)
        
        # Pattern 1: Starts with 'Cat.A'
        cat_a_pattern1 = df_raw[df_raw['classamento'].str.startswith('Cat.A', na=False)]
        print(f"Pattern 'Cat.A': {len(cat_a_pattern1)} records")
        if len(cat_a_pattern1) > 0:
            cat_a_p1_parcels = cat_a_pattern1.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
            print(f"  Unique parcels: {len(cat_a_p1_parcels)}")
            print(f"  Classamento breakdown:")
            for classamento, count in cat_a_pattern1['classamento'].value_counts().items():
                print(f"    {classamento}: {count} records")
        print()
        
        # Pattern 2: Contains 'A/' (alternative pattern)
        cat_a_pattern2 = df_raw[df_raw['classamento'].str.contains('A/', na=False)]
        print(f"Pattern contains 'A/': {len(cat_a_pattern2)} records")
        if len(cat_a_pattern2) > 0:
            cat_a_p2_parcels = cat_a_pattern2.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
            print(f"  Unique parcels: {len(cat_a_p2_parcels)}")
            print(f"  Classamento breakdown:")
            for classamento, count in cat_a_pattern2['classamento'].value_counts().items():
                print(f"    {classamento}: {count} records")
        print()
        
        # Pattern 3: Starts with 'A' (my incorrect assumption)
        cat_a_pattern3 = df_raw[df_raw['classamento'].str.startswith('A', na=False)]
        print(f"Pattern starts with 'A': {len(cat_a_pattern3)} records")
        print()
        
        # Check what's actually in the validation ready data
        print("🔍 VALIDATION READY VS RAW DATA COMPARISON:")
        print("-" * 50)
        
        print(f"Raw Data Records: {len(df_raw)}")
        print(f"Validation Ready Records: {len(df_validation)}")
        
        # Check if validation ready contains Category A properties
        if 'classamento' in df_validation.columns:
            print("\nClassamento in Validation Ready:")
            val_classamento = df_validation['classamento'].value_counts()
            for classamento, count in val_classamento.items():
                print(f"  {classamento}: {count} records")
            
            # Check Category A in validation data
            val_cat_a = df_validation[df_validation['classamento'].str.startswith('Cat.A', na=False)]
            print(f"\nCategory A in Validation Ready: {len(val_cat_a)} records")
            if len(val_cat_a) > 0:
                val_cat_a_parcels = val_cat_a.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
                print(f"  Unique Category A parcels in validation: {len(val_cat_a_parcels)}")
        
        print()
        
        # Trace specific parcels from raw to validation
        print("🔍 PARCEL-LEVEL TRACING:")
        print("-" * 50)
        
        # Get unique parcels from validation ready
        if all(col in df_validation.columns for col in ['comune_input', 'foglio_input', 'particella_input']):
            validation_parcels = df_validation.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
            
            print(f"Parcels represented in Validation Ready: {len(validation_parcels)}")
            print("\nParcel-by-parcel analysis:")
            
            for (comune, foglio, particella), val_count in validation_parcels.items():
                # Find corresponding raw data
                parcel_raw = df_raw[
                    (df_raw['comune_input'] == comune) & 
                    (df_raw['foglio_input'] == foglio) & 
                    (df_raw['particella_input'] == particella)
                ]
                
                if len(parcel_raw) > 0:
                    # Get classamento types for this parcel
                    classamentos = parcel_raw['classamento'].unique()
                    print(f"  {comum} - F{foglio} P{particella}:")
                    print(f"    Raw records: {len(parcel_raw)}")
                    print(f"    Validation records: {val_count}")
                    print(f"    Classamentos: {list(classamentos)}")
                    
                    # Check if any are Category A
                    cat_a_in_parcel = any(c.startswith('Cat.A') for c in classamentos if pd.notna(c))
                    print(f"    Contains Category A: {cat_a_in_parcel}")
                    print()
        
        # Area analysis
        print("🔍 AREA FLOW ANALYSIS:")
        print("-" * 50)
        
        # Calculate areas properly
        df_raw_copy = df_raw.copy()
        df_raw_copy['Area_numeric'] = pd.to_numeric(df_raw_copy['Area'].astype(str).str.replace(',', '.'), errors='coerce')
        
        # Total input area (by unique parcels)
        input_parcel_areas = df_raw_copy.groupby(['comune_input', 'foglio_input', 'particella_input'])['Area_numeric'].first()
        total_input_area = input_parcel_areas.sum()
        print(f"Total Input Area: {total_input_area:.2f} ha")
        
        # Category A area (if any)
        cat_a_records = df_raw_copy[df_raw_copy['classamento'].str.startswith('Cat.A', na=False)]
        if len(cat_a_records) > 0:
            cat_a_parcel_areas = cat_a_records.groupby(['comune_input', 'foglio_input', 'particella_input'])['Area_numeric'].first()
            cat_a_total_area = cat_a_parcel_areas.sum()
            print(f"Category A Area: {cat_a_total_area:.2f} ha")
            print(f"Category A Parcels: {len(cat_a_parcel_areas)}")
        else:
            print("No Category A properties found with 'Cat.A' pattern")
        
        # Validation ready area representation
        if all(col in df_validation.columns for col in ['comune_input', 'foglio_input', 'particella_input', 'Area']):
            df_val_copy = df_validation.copy()
            df_val_copy['Area_numeric'] = pd.to_numeric(df_val_copy['Area'].astype(str).str.replace(',', '.'), errors='coerce')
            val_parcel_areas = df_val_copy.groupby(['comune_input', 'foglio_input', 'particella_input'])['Area_numeric'].first()
            val_total_area = val_parcel_areas.sum()
            print(f"Validation Ready Area: {val_total_area:.2f} ha")
            print(f"Validation Ready Unique Parcels: {len(val_parcel_areas)}")
        
    except Exception as e:
        print(f"❌ Error in Category A analysis: {e}")
        import traceback
        traceback.print_exc()

def analyze_funnel_vs_reality(excel_path):
    """
    Compare what the funnel claims vs what the data actually shows
    """
    print("\n" + "="*80)
    print("FUNNEL CLAIMS VS DATA REALITY")
    print("="*80)
    
    try:
        # Read sheets
        df_raw = pd.read_excel(excel_path, sheet_name='All_Raw_Data')
        df_validation = pd.read_excel(excel_path, sheet_name='All_Validation_Ready')
        df_funnel = pd.read_excel(excel_path, sheet_name='Enhanced_Funnel_Analysis')
        
        print("📊 FUNNEL CLAIMS:")
        print("-" * 30)
        land_funnel = df_funnel[df_funnel['Funnel_Type'] == 'Land Acquisition']
        for _, row in land_funnel.iterrows():
            stage = row['Stage']
            count = row['Count']
            hectares = row['Hectares']
            print(f"  {stage}: {count} items, {hectares} ha")
        
        print("\n📊 DATA REALITY:")
        print("-" * 30)
        
        # Reality check 1: Input parcels
        unique_input_parcels = df_raw.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
        df_raw_copy = df_raw.copy()
        df_raw_copy['Area_numeric'] = pd.to_numeric(df_raw_copy['Area'].astype(str).str.replace(',', '.'), errors='coerce')
        input_parcel_areas = df_raw_copy.groupby(['comune_input', 'foglio_input', 'particella_input'])['Area_numeric'].first()
        
        print(f"  Actual Input Parcels: {len(unique_input_parcels)}")
        print(f"  Actual Input Area: {input_parcel_areas.sum():.1f} ha")
        
        # Reality check 2: Category A parcels
        cat_a_records = df_raw[df_raw['classamento'].str.startswith('Cat.A', na=False)]
        if len(cat_a_records) > 0:
            cat_a_parcels = cat_a_records.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
            cat_a_parcel_areas = cat_a_records.groupby(['comune_input', 'foglio_input', 'particella_input'])['Area_numeric'].first()
            
            print(f"  Actual Category A Parcels: {len(cat_a_parcels)}")
            print(f"  Actual Category A Area: {cat_a_parcel_areas.sum():.1f} ha")
        else:
            print(f"  Actual Category A Parcels: 0")
            print(f"  Actual Category A Area: 0.0 ha")
        
        # Reality check 3: Validation ready
        if all(col in df_validation.columns for col in ['comune_input', 'foglio_input', 'particella_input']):
            val_parcels = df_validation.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
            print(f"  Validation Ready Parcels Represented: {len(val_parcels)}")
            print(f"  Validation Ready Contacts: {len(df_validation)}")
        
        print("\n🔍 DISCREPANCY ANALYSIS:")
        print("-" * 30)
        
        # Compare funnel vs reality
        funnel_cat_a = land_funnel[land_funnel['Stage'].str.contains('Category A', na=False)]
        if len(funnel_cat_a) > 0:
            funnel_cat_a_count = funnel_cat_a['Count'].iloc[0]
            funnel_cat_a_area = funnel_cat_a['Hectares'].iloc[0]
            
            actual_cat_a_count = len(cat_a_parcels) if len(cat_a_records) > 0 else 0
            actual_cat_a_area = cat_a_parcel_areas.sum() if len(cat_a_records) > 0 else 0
            
            print(f"Category A Parcels - Funnel: {funnel_cat_a_count}, Reality: {actual_cat_a_count}")
            print(f"Category A Area - Funnel: {funnel_cat_a_area}, Reality: {actual_cat_a_area:.1f}")
            
            if funnel_cat_a_count != actual_cat_a_count:
                print("❌ DISCREPANCY: Funnel count doesn't match reality!")
            if abs(funnel_cat_a_area - actual_cat_a_area) > 0.1:
                print("❌ DISCREPANCY: Funnel area doesn't match reality!")
    
    except Exception as e:
        print(f"❌ Error comparing funnel vs reality: {e}")

if __name__ == "__main__":
    # Path to your test campaign file
    campaign_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_1807\LandAcquisition_Casalpusterlengo_Castiglione_20250703_1807_Results.xlsx"
    
    print("🚀 Starting Category A Filter Debug Analysis...")
    print()
    
    debug_category_a_filtering(campaign_file)
    analyze_funnel_vs_reality(campaign_file)
    
    print()
    print("="*80)
    print("DEBUG ANALYSIS COMPLETE - Please review findings above")
    print("="*80)