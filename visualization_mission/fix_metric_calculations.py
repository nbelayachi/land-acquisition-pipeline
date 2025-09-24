#!/usr/bin/env python3
"""
Fix Metric Calculations
Analyze real data structure and fix incorrect calculations
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

def analyze_data_structure():
    """Analyze the actual data structure to understand correct metrics"""
    print("🔍 ANALYZING ACTUAL DATA STRUCTURE FOR CORRECT METRICS")
    print("=" * 60)
    
    excel_path = "data/Campaign4_Results.xlsx"
    input_file = "data/Input_Castiglione Casalpusterlengo CP.xlsx"
    
    try:
        # Load key sheets
        print("📊 Loading data sheets...")
        input_data = pd.read_excel(input_file, sheet_name='Sheet1')
        scorecard = pd.read_excel(excel_path, sheet_name='Campaign_Scorecard')
        all_validation = pd.read_excel(excel_path, sheet_name='All_Validation_Ready')
        final_mailing = pd.read_excel(excel_path, sheet_name='Final_Mailing_List')
        campaign_summary = pd.read_excel(excel_path, sheet_name='Campaign_Summary')
        enhanced_funnel = pd.read_excel(excel_path, sheet_name='Enhanced_Funnel_Analysis')
        owners_by_parcel = pd.read_excel(excel_path, sheet_name='Owners_By_Parcel')
        
        print("✅ Data loaded successfully")
        
        # 1. INPUT DATA ANALYSIS
        print("\n📄 INPUT DATA ANALYSIS:")
        print("=" * 40)
        print(f"   Total input parcels: {len(input_data)}")
        print(f"   Total input area: {input_data['Area'].sum():.1f} Ha")
        print(f"   Average parcel size: {input_data['Area'].mean():.2f} Ha")
        print(f"   Municipalities in input: {input_data['comune'].nunique()}")
        print(f"   Input municipalities: {sorted(input_data['comune'].unique())}")
        
        # 2. CAMPAIGN SCORECARD ANALYSIS
        print("\n🎯 CAMPAIGN SCORECARD ANALYSIS:")
        print("=" * 40)
        scorecard_data = {}
        for _, row in scorecard.iterrows():
            category = row['Category']
            people = row['Unique People']
            mailings = row['Mailings Sent']
            parcels = row['Parcels Affected']
            hectares = row['Hectares Affected']
            
            print(f"   {category}:")
            print(f"     • People: {people}")
            print(f"     • Mailings: {mailings}")
            print(f"     • Parcels: {parcels}")
            print(f"     • Hectares: {hectares:.1f} Ha")
            
            scorecard_data[category] = {
                'people': people,
                'mailings': mailings,
                'parcels': parcels,
                'hectares': hectares
            }
        
        # 3. ALL_VALIDATION_READY ANALYSIS
        print("\n🔍 ALL_VALIDATION_READY ANALYSIS:")
        print("=" * 40)
        print(f"   Total addresses: {len(all_validation)}")
        print(f"   Unique owners (cf): {all_validation['cf'].nunique()}")
        print(f"   Total validated area: {all_validation['Area'].sum():.1f} Ha")
        print(f"   Addresses per owner: {len(all_validation) / all_validation['cf'].nunique():.1f}")
        
        # Check coordinate coverage
        coord_coverage = (all_validation['Latitude'].notna() & all_validation['Longitude'].notna()).sum()
        print(f"   Addresses with coordinates: {coord_coverage} ({coord_coverage/len(all_validation)*100:.1f}%)")
        
        # Address confidence breakdown
        if 'Address_Confidence' in all_validation.columns:
            confidence_dist = all_validation['Address_Confidence'].value_counts()
            print(f"   Address confidence distribution:")
            for conf, count in confidence_dist.items():
                print(f"     • {conf}: {count} ({count/len(all_validation)*100:.1f}%)")
        
        # 4. FINAL_MAILING_LIST ANALYSIS
        print("\n📮 FINAL_MAILING_LIST ANALYSIS:")
        print("=" * 40)
        print(f"   Total mailings: {len(final_mailing)}")
        print(f"   Unique owners: {final_mailing['cf'].nunique()}")
        print(f"   Mailings per owner: {len(final_mailing) / final_mailing['cf'].nunique():.1f}")
        
        # Municipality breakdown
        if 'Municipality' in final_mailing.columns:
            muni_dist = final_mailing['Municipality'].value_counts()
            print(f"   Municipality distribution:")
            for muni, count in muni_dist.items():
                print(f"     • {muni}: {count} mailings")
        
        # 5. CAMPAIGN_SUMMARY ANALYSIS
        print("\n📊 CAMPAIGN_SUMMARY ANALYSIS:")
        print("=" * 40)
        # Clean the data
        cs_clean = campaign_summary[campaign_summary['comune'].notna() & (campaign_summary['comune'] != '')].reset_index(drop=True)
        print(f"   Municipalities processed: {len(cs_clean)}")
        print(f"   Total input parcels (Campaign_Summary): {cs_clean['Input_Parcels'].sum()}")
        print(f"   Total input area (Campaign_Summary): {cs_clean['Input_Area_Ha'].sum():.1f} Ha")
        print(f"   Direct mail contacts: {cs_clean['Direct_Mail_Final_Contacts'].sum()}")
        print(f"   Agency contacts: {cs_clean['Agency_Final_Contacts'].sum()}")
        
        # 6. ENHANCED_FUNNEL_ANALYSIS
        print("\n🔄 ENHANCED_FUNNEL_ANALYSIS:")
        print("=" * 40)
        print(f"   Funnel stages: {len(enhanced_funnel)}")
        for _, row in enhanced_funnel.iterrows():
            stage = row['Stage']
            count = row['Count']
            hectares = row['Hectares'] if pd.notna(row['Hectares']) else 'N/A'
            print(f"     • {stage}: {count} ({hectares} Ha)")
        
        # 7. OWNERS_BY_PARCEL ANALYSIS
        print("\n🏡 OWNERS_BY_PARCEL ANALYSIS:")
        print("=" * 40)
        print(f"   Parcels analyzed: {len(owners_by_parcel)}")
        print(f"   Average owners per parcel: {owners_by_parcel['total_owners'].mean():.1f}")
        print(f"   Max owners per parcel: {owners_by_parcel['total_owners'].max()}")
        print(f"   Multi-owner parcels: {(owners_by_parcel['total_owners'] > 1).sum()}")
        print(f"   Complex ownership (>5 owners): {(owners_by_parcel['total_owners'] > 5).sum()}")
        print(f"   Total parcel area: {owners_by_parcel['parcel_area_ha'].sum():.1f} Ha")
        
        # 8. CORRECT PIPELINE EFFICIENCY CALCULATION
        print("\n📈 CORRECT PIPELINE EFFICIENCY CALCULATION:")
        print("=" * 40)
        
        # Method 1: Input parcels to final mailings
        input_parcels = len(input_data)
        final_mailings = len(final_mailing)
        efficiency_v1 = (final_mailings / input_parcels) * 100
        print(f"   Method 1 (Input to Final Mailings): {final_mailings}/{input_parcels} = {efficiency_v1:.1f}%")
        
        # Method 2: Validation addresses to final mailings
        validation_addresses = len(all_validation)
        efficiency_v2 = (final_mailings / validation_addresses) * 100
        print(f"   Method 2 (Validation to Final): {final_mailings}/{validation_addresses} = {efficiency_v2:.1f}%")
        
        # Method 3: Check if we can track unique parcels through the pipeline
        if 'Foglio' in final_mailing.columns and 'Particella' in final_mailing.columns:
            # Count unique parcels in final mailing
            unique_final_parcels = final_mailing[['Foglio', 'Particella']].drop_duplicates()
            unique_parcels_count = len(unique_final_parcels)
            efficiency_v3 = (unique_parcels_count / input_parcels) * 100
            print(f"   Method 3 (Input Parcels to Final Parcels): {unique_parcels_count}/{input_parcels} = {efficiency_v3:.1f}%")
        
        # 9. AREA EXPANSION CALCULATION
        print("\n📐 AREA EXPANSION CALCULATION:")
        print("=" * 40)
        input_area = input_data['Area'].sum()
        validation_area = all_validation['Area'].sum()
        expansion_factor = validation_area / input_area
        print(f"   Input area: {input_area:.1f} Ha")
        print(f"   Validation area: {validation_area:.1f} Ha")
        print(f"   Expansion factor: {expansion_factor:.1f}x")
        
        # 10. SUMMARY OF CORRECTED METRICS
        print("\n✅ CORRECTED METRICS SUMMARY:")
        print("=" * 40)
        print(f"   Input: {input_parcels} parcels, {input_area:.1f} Ha")
        print(f"   Validation: {validation_addresses} addresses, {all_validation['cf'].nunique()} owners")
        print(f"   Final Mailing: {final_mailings} mailings, {final_mailing['cf'].nunique()} owners")
        print(f"   Pipeline Efficiency: {efficiency_v1:.1f}% (parcels to mailings)")
        print(f"   Address Optimization: {efficiency_v2:.1f}% (validation to final)")
        print(f"   Area Expansion: {expansion_factor:.1f}x")
        
        # Return corrected metrics
        return {
            'input_parcels': input_parcels,
            'input_area': input_area,
            'validation_addresses': validation_addresses,
            'validation_owners': all_validation['cf'].nunique(),
            'validation_area': validation_area,
            'final_mailings': final_mailings,
            'final_owners': final_mailing['cf'].nunique(),
            'pipeline_efficiency': efficiency_v1,
            'address_optimization': efficiency_v2,
            'area_expansion': expansion_factor,
            'scorecard_data': scorecard_data,
            'coord_coverage': coord_coverage,
            'coord_percentage': coord_coverage/len(all_validation)*100
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🔧 FIXING METRIC CALCULATIONS BASED ON REAL DATA")
    print("=" * 60)
    
    corrected_metrics = analyze_data_structure()
    
    if corrected_metrics:
        print(f"\n💡 CORRECTED UNDERSTANDING:")
        print("=" * 40)
        print("• Pipeline Efficiency should be calculated as: Final Mailings / Input Parcels")
        print("• Address Optimization should be: Final Mailings / Validation Addresses")
        print("• Area Expansion is correct: Validation Area / Input Area")
        print("• All metrics are now based on actual data structure")
        print("\n✅ Metrics are now correctly calculated from real data!")
    else:
        print("❌ Failed to analyze data structure")

if __name__ == "__main__":
    main()