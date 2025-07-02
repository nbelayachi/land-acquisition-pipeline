"""
Simple Funnel Validation Against Real Data
"""

import pandas as pd

# Load real campaign data
results_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250702_0018\LandAcquisition_Casalpusterlengo_Castiglione_20250702_0018_Results.xlsx"

print("FUNNEL VALIDATION AGAINST REAL CAMPAIGN DATA")
print("=" * 60)

try:
    # Read key data sheets
    validation_df = pd.read_excel(results_file, sheet_name='All_Validation_Ready')
    campaign_summary_df = pd.read_excel(results_file, sheet_name='Campaign_Summary') 
    funnel_analysis_df = pd.read_excel(results_file, sheet_name='Funnel_Analysis')
    
    print("1. LAND ACQUISITION PIPELINE VALIDATION")
    print("-" * 45)
    
    # Extract real data from Campaign_Summary
    real_input_parcels = campaign_summary_df['Input_Parcels'].sum()
    real_after_api = campaign_summary_df['After_API_Parcels'].sum() 
    real_private_parcels = campaign_summary_df['Private_Owner_Parcels'].sum()
    real_category_a = campaign_summary_df['After_CatA_Filter_Parcels'].sum()
    
    real_input_ha = campaign_summary_df['Input_Area_Ha'].sum()
    real_category_a_ha = campaign_summary_df['After_CatA_Filter_Area_Ha'].sum()
    
    print(f"Real Data:")
    print(f"  Input Parcels: {real_input_parcels} parcels ({real_input_ha:.1f} ha)")
    print(f"  After API: {real_after_api} parcels")
    print(f"  Private Owners: {real_private_parcels} parcels")
    print(f"  Category A Filter: {real_category_a} parcels ({real_category_a_ha:.1f} ha)")
    
    print(f"\nOur Funnel Assumptions:")
    print(f"  Input Parcels: 10 parcels (56.9 ha)")
    print(f"  After API: 10 parcels")
    print(f"  Private Owners: 10 parcels")
    print(f"  Category A Filter: 8 parcels (53.0 ha)")
    
    land_matches = (real_input_parcels == 10 and real_category_a == 8)
    print(f"\nLand Pipeline Accurate: {land_matches}")
    
    print("\n2. CONTACT PROCESSING PIPELINE VALIDATION")
    print("-" * 45)
    
    # Extract real contact data
    real_unique_owners = campaign_summary_df['Unique_Individual_Owners'].sum()
    real_address_pairs = campaign_summary_df['Unique_Owner_Address_Pairs'].sum()
    real_direct_mail = campaign_summary_df['Direct_Mail_Final_Contacts'].sum()
    real_agency = campaign_summary_df['Agency_Final_Contacts'].sum()
    
    print(f"Real Data:")
    print(f"  Unique Owners: {real_unique_owners}")
    print(f"  Address Pairs: {real_address_pairs}")
    print(f"  Direct Mail: {real_direct_mail}")
    print(f"  Agency: {real_agency}")
    print(f"  Total Routing: {real_direct_mail + real_agency}")
    
    print(f"\nOur Funnel Assumptions:")
    print(f"  Unique Owners: 10")
    print(f"  Address Pairs: 23")
    print(f"  Direct Mail: 12")
    print(f"  Agency: 11")
    print(f"  Total Routing: 23")
    
    contact_matches = (real_unique_owners == 10 and real_address_pairs == 23 and 
                      real_direct_mail == 12 and real_agency == 11)
    print(f"\nContact Pipeline Accurate: {contact_matches}")
    
    print("\n3. ADDRESS QUALITY DISTRIBUTION VALIDATION")
    print("-" * 45)
    
    # Extract real quality data
    real_confidence_dist = validation_df['Address_Confidence'].value_counts()
    real_ultra_high = real_confidence_dist.get('ULTRA_HIGH', 0)
    real_high = real_confidence_dist.get('HIGH', 0)
    real_medium = real_confidence_dist.get('MEDIUM', 0)
    real_low = real_confidence_dist.get('LOW', 0)
    real_total = len(validation_df)
    
    print(f"Real Address Quality Distribution:")
    print(f"  ULTRA_HIGH: {real_ultra_high} ({real_ultra_high/real_total*100:.1f}%)")
    print(f"  HIGH: {real_high} ({real_high/real_total*100:.1f}%)")
    print(f"  MEDIUM: {real_medium} ({real_medium/real_total*100:.1f}%)")
    print(f"  LOW: {real_low} ({real_low/real_total*100:.1f}%)")
    print(f"  Total: {real_total}")
    
    print(f"\nOur Funnel Assumptions:")
    print(f"  ULTRA_HIGH: 4 (17.4%)")
    print(f"  HIGH: 1 (4.3%)")
    print(f"  MEDIUM: 13 (56.5%)")
    print(f"  LOW: 5 (21.7%)")
    print(f"  Total: 23")
    
    quality_matches = (real_ultra_high == 4 and real_high == 1 and 
                      real_medium == 13 and real_low == 5)
    print(f"\nQuality Distribution Accurate: {quality_matches}")
    
    print("\n4. EXISTING FUNNEL_ANALYSIS COMPARISON")
    print("-" * 40)
    
    # Check existing funnel data
    parcel_funnel = funnel_analysis_df[funnel_analysis_df['Funnel_Type'] == 'Parcel Journey']
    contact_funnel = funnel_analysis_df[funnel_analysis_df['Funnel_Type'] == 'Contact Journey']
    
    print("Existing Parcel Journey totals:")
    for stage in sorted(parcel_funnel['Stage'].unique()):
        stage_data = parcel_funnel[parcel_funnel['Stage'] == stage]
        total_count = stage_data['Count'].sum()
        total_hectares = stage_data['Hectares'].sum()
        print(f"  {stage}: {total_count} parcels, {total_hectares:.1f} ha")
    
    print("\nExisting Contact Journey totals:")
    for stage in sorted(contact_funnel['Stage'].unique()):
        stage_data = contact_funnel[contact_funnel['Stage'] == stage]
        total_count = stage_data['Count'].sum()
        total_hectares = stage_data['Hectares'].sum()
        print(f"  {stage}: {total_count} contacts, {total_hectares:.1f} ha")
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    all_accurate = land_matches and contact_matches and quality_matches
    
    if all_accurate:
        print("ALL FUNNEL CALCULATIONS ARE ACCURATE!")
        print("Our funnel structure matches the real campaign data perfectly.")
    else:
        print("FUNNEL CALCULATIONS NEED CORRECTIONS!")
        print("\nDiscrepancies found:")
        if not land_matches:
            print(f"  Land Pipeline: Real parcels {real_input_parcels}->{real_category_a}, Our model 10->8")
        if not contact_matches:
            print(f"  Contact Pipeline: Real contacts {real_address_pairs}, Our model 23")
        if not quality_matches:
            print(f"  Quality Distribution: Real vs Model mismatch")
    
    # Show any discrepancies in detail
    if not all_accurate:
        print(f"\nCORRECTED VALUES SHOULD BE:")
        print(f"Land Pipeline: {real_input_parcels} -> {real_after_api} -> {real_private_parcels} -> {real_category_a}")
        print(f"Contact Pipeline: {real_unique_owners} -> {real_address_pairs} -> {real_direct_mail} + {real_agency}")
        print(f"Quality: {real_ultra_high} ULTRA_HIGH, {real_high} HIGH, {real_medium} MEDIUM, {real_low} LOW")
    
except Exception as e:
    print(f"Error: {str(e)}")