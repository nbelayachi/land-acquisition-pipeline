#!/usr/bin/env python3
"""
Raw Data Structure Exploration Script
Analyzes the source data to understand business logic and metric calculations
Usage: Run in Spyder and paste the output back for review
"""

import pandas as pd
import numpy as np

def explore_raw_data_structure(excel_path):
    """
    Deep dive into raw data structure to understand business logic
    """
    print("="*80)
    print("RAW DATA STRUCTURE EXPLORATION")
    print("="*80)
    print(f"File: {excel_path}")
    print()
    
    try:
        # Read the raw data
        df_raw = pd.read_excel(excel_path, sheet_name='All_Raw_Data')
        print(f"📊 RAW DATA OVERVIEW:")
        print(f"Total Records: {len(df_raw)}")
        print(f"Columns: {len(df_raw.columns)}")
        print()
        
        # 1. PARCEL ANALYSIS
        print("🏠 PARCEL STRUCTURE ANALYSIS:")
        print("-" * 50)
        
        # Unique parcels (input level)
        if all(col in df_raw.columns for col in ['comune_input', 'foglio_input', 'particella_input']):
            unique_input_parcels = df_raw.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
            print(f"Unique Input Parcels: {len(unique_input_parcels)}")
            print(f"Records per Input Parcel:")
            parcel_record_counts = unique_input_parcels.value_counts().sort_index()
            for count, frequency in parcel_record_counts.items():
                print(f"  {count} records: {frequency} parcels")
            
            print(f"\nDetailed Input Parcel Breakdown:")
            for i, ((comune, foglio, particella), count) in enumerate(unique_input_parcels.head(10).items()):
                print(f"  {i+1}. {comune} - Foglio {foglio}, Particella {particella}: {count} records")
            if len(unique_input_parcels) > 10:
                print(f"  ... and {len(unique_input_parcels) - 10} more parcels")
        
        print()
        
        # 2. OWNER ANALYSIS  
        print("👤 OWNER STRUCTURE ANALYSIS:")
        print("-" * 50)
        
        if 'cf' in df_raw.columns:
            unique_owners = df_raw['cf'].nunique()
            print(f"Unique Owners (by CF): {unique_owners}")
            
            # Owner distribution across parcels
            owner_parcel_counts = df_raw.groupby('cf')['particella_input'].nunique()
            print(f"Owners appearing on multiple parcels:")
            multi_parcel_owners = owner_parcel_counts[owner_parcel_counts > 1]
            print(f"  Owners on >1 parcel: {len(multi_parcel_owners)}")
            if len(multi_parcel_owners) > 0:
                print(f"  Max parcels per owner: {multi_parcel_owners.max()}")
                print(f"  Top multi-parcel owners:")
                for cf, parcel_count in multi_parcel_owners.sort_values(ascending=False).head(5).items():
                    owner_name = df_raw[df_raw['cf'] == cf][['cognome', 'nome']].iloc[0]
                    print(f"    {owner_name['cognome']} {owner_name['nome']}: {parcel_count} parcels")
        
        print()
        
        # 3. PROPERTY TYPE ANALYSIS
        print("🏢 PROPERTY TYPE ANALYSIS:")
        print("-" * 50)
        
        if 'classamento' in df_raw.columns:
            classamento_dist = df_raw['classamento'].value_counts()
            print(f"Property Classifications (classamento):")
            for classamento, count in classamento_dist.items():
                percentage = (count / len(df_raw)) * 100
                print(f"  {classamento}: {count} records ({percentage:.1f}%)")
            
            # Category A filter analysis
            category_a = df_raw[df_raw['classamento'].str.startswith('A', na=False)]
            print(f"\nCategory A Properties: {len(category_a)} records")
            if len(category_a) > 0:
                unique_cat_a_parcels = category_a.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
                print(f"Unique Category A Parcels: {len(unique_cat_a_parcels)}")
        
        print()
        
        # 4. OWNERSHIP ANALYSIS
        print("📋 OWNERSHIP STRUCTURE ANALYSIS:")
        print("-" * 50)
        
        if 'quota' in df_raw.columns:
            print(f"Quota Information:")
            quota_types = df_raw['quota'].value_counts()
            print(f"Different quota values: {len(quota_types)}")
            for quota, count in quota_types.head(10).items():
                print(f"  '{quota}': {count} records")
            
            # Analyze shared ownership
            shared_parcels = df_raw.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
            shared_ownership = shared_parcels[shared_parcels > 1]
            print(f"\nShared Ownership Analysis:")
            print(f"  Parcels with multiple owners: {len(shared_ownership)}")
            print(f"  Parcels with single owner: {len(shared_parcels) - len(shared_ownership)}")
            if len(shared_ownership) > 0:
                print(f"  Max owners per parcel: {shared_ownership.max()}")
        
        print()
        
        # 5. INDIVIDUAL VS COMPANY ANALYSIS
        print("🏢 INDIVIDUAL VS COMPANY ANALYSIS:")
        print("-" * 50)
        
        if 'Tipo_Proprietario' in df_raw.columns:
            owner_types = df_raw['Tipo_Proprietario'].value_counts()
            print(f"Owner Types:")
            for owner_type, count in owner_types.items():
                percentage = (count / len(df_raw)) * 100
                print(f"  {owner_type}: {count} records ({percentage:.1f}%)")
        
        # Alternative CF analysis
        if 'cf' in df_raw.columns:
            print(f"\nCF (Tax Code) Analysis:")
            cf_patterns = df_raw['cf'].astype(str)
            numeric_cf = cf_patterns.str.isnumeric().sum()
            alpha_cf = len(df_raw) - numeric_cf
            print(f"  Numeric CF (companies): {numeric_cf}")
            print(f"  Alphanumeric CF (individuals): {alpha_cf}")
        
        print()
        
        # 6. GEOGRAPHIC DISTRIBUTION
        print("🗺️ GEOGRAPHIC DISTRIBUTION:")
        print("-" * 50)
        
        if 'comune_input' in df_raw.columns:
            municipality_dist = df_raw['comune_input'].value_counts()
            print(f"Municipalities ({len(municipality_dist)}):")
            for comune, count in municipality_dist.items():
                percentage = (count / len(df_raw)) * 100
                print(f"  {comune}: {count} records ({percentage:.1f}%)")
                
                # Unique parcels per municipality
                muni_parcels = df_raw[df_raw['comune_input'] == comune].groupby(['foglio_input', 'particella_input']).size()
                print(f"    → {len(muni_parcels)} unique parcels")
        
        print()
        
        # 7. AREA ANALYSIS
        print("📏 AREA ANALYSIS:")
        print("-" * 50)
        
        if 'Area' in df_raw.columns:
            # Convert area to numeric (handle comma decimal separator)
            area_values = pd.to_numeric(df_raw['Area'].astype(str).str.replace(',', '.'), errors='coerce')
            valid_areas = area_values.dropna()
            
            print(f"Area Statistics:")
            print(f"  Total records with area: {len(valid_areas)}")
            print(f"  Total area (ha): {valid_areas.sum():.2f}")
            print(f"  Average area per record: {valid_areas.mean():.2f} ha")
            print(f"  Min area: {valid_areas.min():.2f} ha")
            print(f"  Max area: {valid_areas.max():.2f} ha")
            
            # Area by unique parcel
            df_raw_copy = df_raw.copy()
            df_raw_copy['Area_numeric'] = area_values
            parcel_areas = df_raw_copy.groupby(['comune_input', 'foglio_input', 'particella_input'])['Area_numeric'].first()
            parcel_areas_clean = parcel_areas.dropna()
            
            print(f"\nArea by Unique Parcel:")
            print(f"  Unique parcels with area: {len(parcel_areas_clean)}")
            print(f"  Total parcel area: {parcel_areas_clean.sum():.2f} ha")
            print(f"  Average parcel size: {parcel_areas_clean.mean():.2f} ha")
        
        return df_raw
        
    except Exception as e:
        print(f"❌ Error analyzing raw data: {e}")
        return None

def trace_metric_calculations(excel_path):
    """
    Trace how key metrics are calculated from raw data
    """
    print("\n" + "="*80)
    print("METRIC CALCULATION TRACING")
    print("="*80)
    
    try:
        # Read all relevant sheets
        df_raw = pd.read_excel(excel_path, sheet_name='All_Raw_Data')
        df_validation = pd.read_excel(excel_path, sheet_name='All_Validation_Ready')
        df_summary = pd.read_excel(excel_path, sheet_name='Campaign_Summary')
        
        print("🔍 TRACING METRIC CALCULATIONS:")
        print("-" * 50)
        
        # 1. Input Parcels
        unique_input_parcels = df_raw.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
        print(f"1. Input Parcels: {len(unique_input_parcels)}")
        
        # 2. Category A Filter
        category_a_records = df_raw[df_raw['classamento'].str.startswith('A', na=False)]
        unique_cat_a_parcels = category_a_records.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
        print(f"2. After Category A Filter: {len(unique_cat_a_parcels)} parcels")
        print(f"   Category A Retention: {len(unique_cat_a_parcels)}/{len(unique_input_parcels)} = {(len(unique_cat_a_parcels)/len(unique_input_parcels)*100):.1f}%")
        
        # 3. Unique Owners
        unique_owners_total = df_raw['cf'].nunique()
        unique_owners_cat_a = category_a_records['cf'].nunique()
        print(f"3. Unique Owners (all): {unique_owners_total}")
        print(f"   Unique Owners (Cat A): {unique_owners_cat_a}")
        
        # 4. Owner-Address Pairs (from validation ready)
        validation_contacts = len(df_validation)
        print(f"4. Validation Ready Contacts: {validation_contacts}")
        
        # 5. Explain the "125% conversion"
        print(f"\n🔍 EXPLAINING THE 125% CONVERSION:")
        print(f"   Category A Parcels: {len(unique_cat_a_parcels)}")
        print(f"   Owners from those parcels: {unique_owners_cat_a}")
        print(f"   Ratio: {unique_owners_cat_a}/{len(unique_cat_a_parcels)} = {(unique_owners_cat_a/len(unique_cat_a_parcels)*100):.1f}%")
        print(f"   ➜ This means some parcels have multiple owners (shared ownership)")
        
        # 6. Validation Ready to Final Mailing
        df_final = pd.read_excel(excel_path, sheet_name='Final_Mailing_List')
        print(f"\n🔍 VALIDATION READY TO FINAL MAILING:")
        print(f"   Validation Ready: {validation_contacts} contacts")
        print(f"   Final Mailing List: {len(df_final)} entries")
        print(f"   Retention: {len(df_final)}/{validation_contacts} = {(len(df_final)/validation_contacts*100):.1f}%")
        
        # 7. Municipality breakdown analysis
        print(f"\n🔍 MUNICIPALITY BREAKDOWN ANALYSIS:")
        print("Raw data by municipality:")
        for comune in df_raw['comune_input'].unique():
            muni_raw = df_raw[df_raw['comune_input'] == comum]
            muni_validation = df_validation[df_validation['comune_input'] == comum] if 'comune_input' in df_validation.columns else pd.DataFrame()
            
            print(f"  {comum}:")
            print(f"    Raw records: {len(muni_raw)}")
            print(f"    Unique owners: {muni_raw['cf'].nunique()}")
            print(f"    Validation ready: {len(muni_validation)}")
        
    except Exception as e:
        print(f"❌ Error tracing calculations: {e}")

if __name__ == "__main__":
    # Path to your test campaign file
    campaign_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_1807\LandAcquisition_Casalpusterlengo_Castiglione_20250703_1807_Results.xlsx"
    
    print("🚀 Starting Raw Data Structure Exploration...")
    print()
    
    # Explore the raw data structure
    df_raw = explore_raw_data_structure(campaign_file)
    
    # Trace metric calculations
    trace_metric_calculations(campaign_file)
    
    print()
    print("="*80)
    print("EXPLORATION COMPLETE - Please review findings above")
    print("="*80)