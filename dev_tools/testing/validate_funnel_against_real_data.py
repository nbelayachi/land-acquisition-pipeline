"""
Validate Funnel Calculations Against Real Campaign Data
Cross-check our funnel structure against actual campaign results
"""

import pandas as pd

def validate_funnel_against_campaign():
    """Validate our funnel structure against the actual campaign data"""
    
    print("FUNNEL VALIDATION AGAINST REAL CAMPAIGN DATA")
    print("=" * 60)
    print("Campaign: Casalpusterlengo_Castiglione_20250702_0018")
    print()
    
    # Load actual campaign data from previous analysis
    results_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250702_0018\LandAcquisition_Casalpusterlengo_Castiglione_20250702_0018_Results.xlsx"
    
    try:
        # Read key data sheets
        validation_df = pd.read_excel(results_file, sheet_name='All_Validation_Ready')
        campaign_summary_df = pd.read_excel(results_file, sheet_name='Campaign_Summary') 
        funnel_analysis_df = pd.read_excel(results_file, sheet_name='Funnel_Analysis')
        scorecard_df = pd.read_excel(results_file, sheet_name='Campaign_Scorecard')
        
        print("REAL CAMPAIGN DATA ANALYSIS")
        print("-" * 40)
        
        # 1. VALIDATE LAND ACQUISITION PIPELINE
        print("1. LAND ACQUISITION PIPELINE VALIDATION")
        print("─" * 45)
        
        # Extract real data from Campaign_Summary
        real_input_parcels = campaign_summary_df['Input_Parcels'].sum()
        real_after_api = campaign_summary_df['After_API_Parcels'].sum() 
        real_private_parcels = campaign_summary_df['Private_Owner_Parcels'].sum()
        real_category_a = campaign_summary_df['After_CatA_Filter_Parcels'].sum()
        
        real_input_ha = campaign_summary_df['Input_Area_Ha'].sum()
        real_after_api_ha = campaign_summary_df['After_API_Area_Ha'].sum()
        real_private_ha = campaign_summary_df['Private_Owner_Area_Ha'].sum()
        real_category_a_ha = campaign_summary_df['After_CatA_Filter_Area_Ha'].sum()
        
        print(f"Real Data:")
        print(f"  Input Parcels: {real_input_parcels} parcels ({real_input_ha:.1f} ha)")
        print(f"  After API: {real_after_api} parcels ({real_after_api_ha:.1f} ha)")
        print(f"  Private Owners: {real_private_parcels} parcels ({real_private_ha:.1f} ha)")
        print(f"  Category A Filter: {real_category_a} parcels ({real_category_a_ha:.1f} ha)")
        
        print(f"\nOur Funnel Assumptions:")
        print(f"  Input Parcels: 10 parcels (56.9 ha)")
        print(f"  After API: 10 parcels (56.9 ha)")
        print(f"  Private Owners: 10 parcels (56.9 ha)")
        print(f"  Category A Filter: 8 parcels (53.0 ha)")
        
        # Check accuracy
        land_accurate = (real_input_parcels == 10 and 
                        real_after_api == 10 and
                        real_private_parcels == 10 and
                        real_category_a == 8)
        
        print(f"\n✅ Land Acquisition Pipeline: {'ACCURATE' if land_accurate else 'NEEDS CORRECTION'}")
        
        if not land_accurate:
            print(f"  DISCREPANCIES:")
            if real_input_parcels != 10:
                print(f"    Input: Real={real_input_parcels}, Funnel=10")
            if real_after_api != 10:
                print(f"    API: Real={real_after_api}, Funnel=10")
            if real_private_parcels != 10:
                print(f"    Private: Real={real_private_parcels}, Funnel=10")
            if real_category_a != 8:
                print(f"    Category A: Real={real_category_a}, Funnel=8")
        
        print()
        
        # 2. VALIDATE CONTACT PROCESSING PIPELINE
        print("2. CONTACT PROCESSING PIPELINE VALIDATION")
        print("─" * 45)
        
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
        
        # Check accuracy
        contact_accurate = (real_unique_owners == 10 and
                           real_address_pairs == 23 and
                           real_direct_mail == 12 and
                           real_agency == 11)
        
        print(f"\n✅ Contact Processing Pipeline: {'ACCURATE' if contact_accurate else 'NEEDS CORRECTION'}")
        
        if not contact_accurate:
            print(f"  DISCREPANCIES:")
            if real_unique_owners != 10:
                print(f"    Owners: Real={real_unique_owners}, Funnel=10")
            if real_address_pairs != 23:
                print(f"    Address Pairs: Real={real_address_pairs}, Funnel=23")
            if real_direct_mail != 12:
                print(f"    Direct Mail: Real={real_direct_mail}, Funnel=12")
            if real_agency != 11:
                print(f"    Agency: Real={real_agency}, Funnel=11")
        
        print()
        
        # 3. VALIDATE ADDRESS QUALITY DISTRIBUTION
        print("3. ADDRESS QUALITY DISTRIBUTION VALIDATION")
        print("─" * 45)
        
        # Extract real quality data from All_Validation_Ready
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
        
        # Check accuracy
        quality_accurate = (real_ultra_high == 4 and
                           real_high == 1 and
                           real_medium == 13 and
                           real_low == 5 and
                           real_total == 23)
        
        print(f"\n✅ Address Quality Distribution: {'ACCURATE' if quality_accurate else 'NEEDS CORRECTION'}")
        
        if not quality_accurate:
            print(f"  DISCREPANCIES:")
            if real_ultra_high != 4:
                print(f"    ULTRA_HIGH: Real={real_ultra_high}, Funnel=4")
            if real_high != 1:
                print(f"    HIGH: Real={real_high}, Funnel=1")
            if real_medium != 13:
                print(f"    MEDIUM: Real={real_medium}, Funnel=13")
            if real_low != 5:
                print(f"    LOW: Real={real_low}, Funnel=5")
            if real_total != 23:
                print(f"    Total: Real={real_total}, Funnel=23")
        
        print()
        
        # 4. VALIDATE EXISTING FUNNEL_ANALYSIS SHEET
        print("4. EXISTING FUNNEL_ANALYSIS VALIDATION")
        print("─" * 40)
        
        print("Current Funnel_Analysis sheet data:")
        print(f"Total rows: {len(funnel_analysis_df)}")
        
        # Group by funnel type and stage
        parcel_funnel = funnel_analysis_df[funnel_analysis_df['Funnel_Type'] == 'Parcel Journey']
        contact_funnel = funnel_analysis_df[funnel_analysis_df['Funnel_Type'] == 'Contact Journey']
        
        print("\nParcel Journey (from existing funnel):")
        for stage in sorted(parcel_funnel['Stage'].unique()):
            stage_data = parcel_funnel[parcel_funnel['Stage'] == stage]
            total_count = stage_data['Count'].sum()
            total_hectares = stage_data['Hectares'].sum()
            print(f"  {stage}: {total_count} parcels, {total_hectares:.1f} ha")
        
        print("\nContact Journey (from existing funnel):")
        for stage in sorted(contact_funnel['Stage'].unique()):
            stage_data = contact_funnel[contact_funnel['Stage'] == stage]
            total_count = stage_data['Count'].sum()
            total_hectares = stage_data['Hectares'].sum()
            print(f"  {stage}: {total_count} contacts, {total_hectares:.1f} ha")
        
        # 5. OVERALL VALIDATION SUMMARY
        print("\n" + "=" * 60)
        print("OVERALL VALIDATION SUMMARY")
        print("=" * 60)
        
        all_accurate = land_accurate and contact_accurate and quality_accurate
        
        if all_accurate:
            print("✅ ALL FUNNEL CALCULATIONS ARE ACCURATE!")
            print("   Our funnel structure perfectly matches the real campaign data.")
            print("   Ready for implementation and PowerBI integration.")
        else:
            print("❌ FUNNEL CALCULATIONS NEED CORRECTIONS!")
            print("   Some assumptions don't match the real campaign data.")
            print("   We need to update our funnel structure.")
        
        # Provide corrected values if needed
        if not all_accurate:
            print("\nCORRECTED FUNNEL VALUES:")
            print("─" * 30)
            print("Land Acquisition Pipeline:")
            print(f"  1. Input Parcels: {real_input_parcels} parcels ({real_input_ha:.1f} ha)")
            print(f"  2. API Data Retrieved: {real_after_api} parcels ({real_after_api_ha:.1f} ha)")
            print(f"  3. Private Owners Only: {real_private_parcels} parcels ({real_private_ha:.1f} ha)")
            print(f"  4. Category A Filter: {real_category_a} parcels ({real_category_a_ha:.1f} ha)")
            
            print("\nContact Processing Pipeline:")
            print(f"  1. Owners Identified: {real_unique_owners}")
            print(f"  2. Address Pairs Created: {real_address_pairs}")
            print(f"  3. Geocoding Completed: {real_address_pairs}")
            print(f"  4. Direct Mail Ready: {real_direct_mail}")
            print(f"  5. Agency Required: {real_agency}")
            
            print("\nAddress Quality Distribution:")
            print(f"  ULTRA_HIGH: {real_ultra_high} addresses ({real_ultra_high/real_total*100:.1f}%)")
            print(f"  HIGH: {real_high} addresses ({real_high/real_total*100:.1f}%)")
            print(f"  MEDIUM: {real_medium} addresses ({real_medium/real_total*100:.1f}%)")
            print(f"  LOW: {real_low} addresses ({real_low/real_total*100:.1f}%)")
        
        return {
            'land_accurate': land_accurate,
            'contact_accurate': contact_accurate,
            'quality_accurate': quality_accurate,
            'overall_accurate': all_accurate,
            'real_data': {
                'input_parcels': real_input_parcels,
                'category_a_parcels': real_category_a,
                'unique_owners': real_unique_owners,
                'address_pairs': real_address_pairs,
                'direct_mail': real_direct_mail,
                'agency': real_agency,
                'ultra_high': real_ultra_high,
                'high': real_high,
                'medium': real_medium,
                'low': real_low,
                'total_addresses': real_total
            }
        }
        
    except Exception as e:
        print(f"❌ Error validating against real data: {str(e)}")
        return None

if __name__ == "__main__":
    print("🔍 Starting funnel validation against real campaign data...")
    validation_results = validate_funnel_against_campaign()
    
    if validation_results and validation_results['overall_accurate']:
        print("\n🎯 VALIDATION SUCCESSFUL!")
        print("📋 Funnel structure is ready for implementation!")
    elif validation_results:
        print("\n⚠️  VALIDATION ISSUES FOUND!")
        print("📋 Review corrections above before implementation!")
    else:
        print("\n❌ VALIDATION FAILED!")
        print("📋 Check data file paths and try again!")