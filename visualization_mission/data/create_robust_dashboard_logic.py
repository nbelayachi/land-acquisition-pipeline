#!/usr/bin/env python3
"""
Robust Dashboard Logic Creation
===============================
Purpose: Build calculations directly from source data, bypassing Campaign_Summary errors
Flow: Input File → All_Raw_Data → All_Validation_Ready → Final_Mailing_List
"""

import pandas as pd
import numpy as np

def build_robust_calculations():
    """Create robust calculations directly from source sheets"""
    
    try:
        print("=== BUILDING ROBUST DASHBOARD CALCULATIONS ===\n")
        
        # Load all source files
        excel_path = "Campaign4_Results.xlsx"
        input_path = "Input_Castiglione Casalpusterlengo CP.xlsx"
        
        print("Loading source data sheets...")
        
        # 1. Load Input File (Ground Truth)
        input_df = pd.read_excel(input_path)
        input_df['parcel_id'] = input_df['comune'] + '-' + input_df['foglio'].astype(str) + '-' + input_df['particella'].astype(str)
        
        print(f"✓ Input File: {len(input_df)} parcels, {input_df['Area'].sum():.1f} Ha")
        
        # 2. Load All_Raw_Data (API Results)
        raw_data = pd.read_excel(excel_path, sheet_name='All_Raw_Data')
        raw_data['parcel_id'] = raw_data['comune_input'] + '-' + raw_data['foglio_input'].astype(str) + '-' + raw_data['particella_input'].astype(str)
        
        # Get unique parcels from API with their areas
        api_unique = raw_data.groupby('parcel_id').agg({
            'Area': 'first',
            'comune_input': 'first',
            'provincia': 'first'
        }).reset_index()
        
        print(f"✓ API Results: {len(api_unique)} unique parcels, {api_unique['Area'].sum():.1f} Ha")
        
        # 3. Load All_Validation_Ready (After Geocoding)
        validation_ready = pd.read_excel(excel_path, sheet_name='All_Validation_Ready')
        validation_ready['parcel_id'] = validation_ready['comune_input'] + '-' + validation_ready['foglio_input'].astype(str) + '-' + validation_ready['particella_input'].astype(str)
        
        # Get unique parcels after validation
        validation_unique = validation_ready.groupby('parcel_id').agg({
            'Area': 'first',
            'comune_input': 'first'
        }).reset_index()
        
        print(f"✓ Validation Ready: {len(validation_unique)} unique parcels, {validation_unique['Area'].sum():.1f} Ha")
        
        # 4. Load Final_Mailing_List (Final Output)
        final_mailing = pd.read_excel(excel_path, sheet_name='Final_Mailing_List')
        
        # Extract unique parcels from Final_Mailing_List
        final_parcels = set()
        for parcels_str in final_mailing['Parcels'].dropna():
            parcels_list = [p.strip() for p in str(parcels_str).split(';') if p.strip()]
            for parcel_group in parcels_list:
                individual_parcels = [p.strip() for p in parcel_group.split(',') if p.strip()]
                final_parcels.update(individual_parcels)
        
        # Match final parcels to municipality format
        final_parcel_data = []
        for parcel in final_parcels:
            if '-' in parcel:
                foglio, particella = parcel.split('-')
                # Find matching municipality from input file
                matching_input = input_df[
                    (input_df['foglio'].astype(str) == foglio) & 
                    (input_df['particella'].astype(str) == particella)
                ]
                if not matching_input.empty:
                    row = matching_input.iloc[0]
                    final_parcel_data.append({
                        'parcel_id': f"{row['comune']}-{foglio}-{particella}",
                        'municipality': row['comune'],
                        'area': row['Area'],
                        'foglio': foglio,
                        'particella': particella
                    })
        
        final_parcel_df = pd.DataFrame(final_parcel_data)
        
        print(f"✓ Final Mailing: {len(final_parcel_df)} unique parcels, {final_parcel_df['area'].sum():.1f} Ha")
        
        print("\n" + "="*60)
        
        # ROBUST FUNNEL CALCULATIONS
        print("\n=== ROBUST FUNNEL PROGRESSION ===")
        
        stages = {
            'Input File': {
                'parcels': len(input_df),
                'area': input_df['Area'].sum(),
                'description': 'Original target parcels from input file'
            },
            'API Retrieved': {
                'parcels': len(api_unique),  
                'area': api_unique['Area'].sum(),
                'description': 'Parcels successfully retrieved from API'
            },
            'Validation Ready': {
                'parcels': len(validation_unique),
                'area': validation_unique['Area'].sum(), 
                'description': 'Parcels with validated owner data'
            },
            'Final Mailing': {
                'parcels': len(final_parcel_df),
                'area': final_parcel_df['area'].sum(),
                'description': 'Parcels in final mailing campaign'
            }
        }
        
        print("Corrected Funnel Stages:")
        prev_parcels = None
        prev_area = None
        
        for stage_name, data in stages.items():
            parcels = data['parcels']
            area = data['area']
            desc = data['description']
            
            retention_p = f" ({parcels/prev_parcels*100:.1f}%)" if prev_parcels else ""
            retention_a = f" ({area/prev_area*100:.1f}%)" if prev_area else ""
            
            print(f"• {stage_name}: {parcels} parcels{retention_p}, {area:.1f} Ha{retention_a}")
            print(f"  └─ {desc}")
            
            prev_parcels = parcels
            prev_area = area
        
        print("\n" + "="*60)
        
        # GEOGRAPHIC DISTRIBUTION BY MUNICIPALITY
        print("\n=== GEOGRAPHIC DISTRIBUTION (FINAL MAILING) ===")
        
        geo_distribution = final_parcel_df.groupby('municipality').agg({
            'area': 'sum',
            'parcel_id': 'count'
        }).reset_index()
        geo_distribution = geo_distribution.rename(columns={'parcel_id': 'parcel_count'})
        geo_distribution = geo_distribution.sort_values('area', ascending=False)
        
        print("Final mailing distribution by municipality:")
        for _, row in geo_distribution.iterrows():
            municipality = row['municipality']
            parcels = row['parcel_count'] 
            area = row['area']
            print(f"• {municipality}: {parcels} parcels, {area:.1f} Ha")
        
        print(f"\nTotal: {geo_distribution['parcel_count'].sum()} parcels, {geo_distribution['area'].sum():.1f} Ha")
        
        print("\n" + "="*60)
        
        # PROCESS EFFICIENCY METRICS
        print("\n=== ROBUST PROCESS EFFICIENCY METRICS ===")
        
        input_parcels = stages['Input File']['parcels']
        api_parcels = stages['API Retrieved']['parcels']
        validation_parcels = stages['Validation Ready']['parcels']
        final_parcels = stages['Final Mailing']['parcels']
        
        input_area = stages['Input File']['area']
        final_area = stages['Final Mailing']['area']
        
        metrics = {
            'API Success Rate': f"{api_parcels/input_parcels*100:.1f}%",
            'Validation Success': f"{validation_parcels/api_parcels*100:.1f}%",
            'Final Conversion': f"{final_parcels/validation_parcels*100:.1f}%", 
            'Overall Pipeline Success': f"{final_parcels/input_parcels*100:.1f}%",
            'Area Retention': f"{final_area/input_area*100:.1f}%"
        }
        
        print("Corrected Business Metrics:")
        for metric, value in metrics.items():
            print(f"• {metric}: {value}")
        
        print("\n" + "="*60)
        
        # MUNICIPALITY PERFORMANCE (ROBUST VERSION)
        print("\n=== MUNICIPALITY PERFORMANCE (ROBUST CALCULATION) ===")
        
        # Calculate municipality performance from source data
        municipality_performance = []
        
        for municipality in input_df['comune'].unique():
            # Input data for this municipality
            muni_input = input_df[input_df['comune'] == municipality]
            input_count = len(muni_input)
            input_area = muni_input['Area'].sum()
            
            # API success for this municipality  
            muni_api = api_unique[api_unique['comune_input'] == municipality]
            api_count = len(muni_api)
            
            # Final mailing for this municipality
            muni_final = final_parcel_df[final_parcel_df['municipality'] == municipality]
            final_count = len(muni_final)
            final_area = muni_final['area'].sum()
            
            # Calculate success rate
            success_rate = (api_count / input_count * 100) if input_count > 0 else 0
            
            municipality_performance.append({
                'Municipality': municipality,
                'Input_Parcels': input_count,
                'Input_Area': input_area,
                'API_Success_Count': api_count,
                'Success_Rate': success_rate,
                'Final_Parcels': final_count,
                'Final_Area': final_area
            })
        
        performance_df = pd.DataFrame(municipality_performance)
        performance_df = performance_df.sort_values('Success_Rate', ascending=False)
        
        print("Municipality performance (robust calculation):")
        for _, row in performance_df.iterrows():
            muni = row['Municipality']
            success = row['Success_Rate']
            final_p = row['Final_Parcels']
            final_a = row['Final_Area']
            print(f"• {muni}: {success:.1f}% success, {final_p} final parcels, {final_a:.1f} Ha")
        
        print("\n=== ROBUST CALCULATIONS COMPLETE ===")
        print("This logic bypasses Campaign_Summary and calculates directly from:")
        print("1. Input File → All_Raw_Data → All_Validation_Ready → Final_Mailing_List")
        print("2. All calculations based on unique parcel tracking")
        print("3. Accurate area calculations at each stage")
        print("4. True conversion rates and business metrics")
        
        return {
            'stages': stages,
            'geo_distribution': geo_distribution, 
            'metrics': metrics,
            'municipality_performance': performance_df
        }
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = build_robust_calculations()