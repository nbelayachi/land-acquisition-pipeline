"""
Test the corrected enhanced funnel implementation
Run this after the fix to validate that aggregation is working correctly
"""

import pandas as pd
import sys
import os

def test_corrected_implementation():
    """Test that the enhanced funnel implementation creates correct aggregated data"""
    
    print("=== TESTING CORRECTED ENHANCED FUNNEL IMPLEMENTATION ===\n")
    
    try:
        # Add the current directory to sys.path to import the pipeline
        sys.path.append('C:/Projects/land-acquisition-pipeline')
        from land_acquisition_pipeline import IntegratedLandAcquisitionPipeline
        
        pipeline = IntegratedLandAcquisitionPipeline()
        
        # Create sample campaign summary data (representing multiple municipalities)
        sample_campaign_summary = pd.DataFrame([
            {
                'CP': '26841', 'comune': 'Casalpusterlengo', 'provincia': 'Lodi',
                'Input_Parcels': 5, 'Input_Area_Ha': 6.25, 'After_API_Parcels': 5, 'After_API_Area_Ha': 6.25,
                'Private_Owner_Parcels': 5, 'Private_Owner_Area_Ha': 6.25, 'After_CatA_Filter_Parcels': 4, 'After_CatA_Filter_Area_Ha': 5.0,
                'Unique_Owners_on_Target_Parcels': 4, 'Unique_Owner_Address_Pairs': 12,
                'Direct_Mail_Final_Contacts': 6, 'Direct_Mail_Final_Area_Ha': 3.25,
                'Agency_Final_Contacts': 6, 'Agency_Final_Area_Ha': 1.75
            },
            {
                'CP': '26845', 'comune': 'Castiglione', 'provincia': 'Lodi', 
                'Input_Parcels': 5, 'Input_Area_Ha': 6.25, 'After_API_Parcels': 5, 'After_API_Area_Ha': 6.25,
                'Private_Owner_Parcels': 5, 'Private_Owner_Area_Ha': 6.25, 'After_CatA_Filter_Parcels': 4, 'After_CatA_Filter_Area_Ha': 5.0,
                'Unique_Owners_on_Target_Parcels': 4, 'Unique_Owner_Address_Pairs': 11,
                'Direct_Mail_Final_Contacts': 6, 'Direct_Mail_Final_Area_Ha': 3.25,
                'Agency_Final_Contacts': 5, 'Agency_Final_Area_Ha': 1.75
            }
        ])
        
        print("Sample Campaign Summary (2 municipalities):")
        print(f"  Total Input Parcels: {sample_campaign_summary['Input_Parcels'].sum()}")
        print(f"  Total Addresses: {sample_campaign_summary['Unique_Owner_Address_Pairs'].sum()}")
        print(f"  Total Direct Mail: {sample_campaign_summary['Direct_Mail_Final_Contacts'].sum()}")
        
        # Test the aggregation logic
        aggregated_summary = {
            'Input_Parcels': sample_campaign_summary['Input_Parcels'].sum(),
            'Input_Area_Ha': sample_campaign_summary['Input_Area_Ha'].sum(),
            'After_API_Parcels': sample_campaign_summary['After_API_Parcels'].sum(),
            'After_API_Area_Ha': sample_campaign_summary['After_API_Area_Ha'].sum(),
            'Private_Owner_Parcels': sample_campaign_summary['Private_Owner_Parcels'].sum(),
            'Private_Owner_Area_Ha': sample_campaign_summary['Private_Owner_Area_Ha'].sum(),
            'After_CatA_Filter_Parcels': sample_campaign_summary['After_CatA_Filter_Parcels'].sum(),
            'After_CatA_Filter_Area_Ha': sample_campaign_summary['After_CatA_Filter_Area_Ha'].sum(),
            'Unique_Owners_on_Target_Parcels': sample_campaign_summary['Unique_Owners_on_Target_Parcels'].sum(),
            'Unique_Owner_Address_Pairs': sample_campaign_summary['Unique_Owner_Address_Pairs'].sum(),
            'Direct_Mail_Final_Contacts': sample_campaign_summary['Direct_Mail_Final_Contacts'].sum(),
            'Direct_Mail_Final_Area_Ha': sample_campaign_summary['Direct_Mail_Final_Area_Ha'].sum(),
            'Agency_Final_Contacts': sample_campaign_summary['Agency_Final_Contacts'].sum(),
            'Agency_Final_Area_Ha': sample_campaign_summary['Agency_Final_Area_Ha'].sum()
        }
        
        aggregated_funnel_metrics = {
            'input_parcels': aggregated_summary['Input_Parcels'],
            'input_area_ha': aggregated_summary['Input_Area_Ha'],
            'after_api_parcels': aggregated_summary['After_API_Parcels'],
            'after_api_area_ha': aggregated_summary['After_API_Area_Ha']
        }
        
        aggregated_municipality = {
            'CP': '26841',
            'comune': 'Casalpusterlengo; Castiglione',
            'provincia': 'Lodi'
        }
        
        # Create enhanced funnel with aggregated data
        enhanced_funnel_df = pipeline.create_funnel_analysis_df(
            aggregated_summary, aggregated_funnel_metrics, aggregated_municipality
        )
        
        print("\nEnhanced Funnel Results:")
        print(f"  Funnel stages created: {len(enhanced_funnel_df)}")
        
        # Verify expected stage counts
        land_funnel = enhanced_funnel_df[enhanced_funnel_df['Funnel_Type'] == 'Land Acquisition']
        contact_funnel = enhanced_funnel_df[enhanced_funnel_df['Funnel_Type'] == 'Contact Processing']
        
        print(f"  Land Acquisition stages: {len(land_funnel)} (Expected: 4)")
        print(f"  Contact Processing stages: {len(contact_funnel)} (Expected: 5)")
        
        # Verify key metrics match aggregated data
        if len(land_funnel) > 0:
            input_parcels = land_funnel[land_funnel['Stage'] == '1. Input Parcels']['Count'].iloc[0]
            qualified_parcels = land_funnel[land_funnel['Stage'] == '4. Category A Filter']['Count'].iloc[0]
            print(f"  Input Parcels in funnel: {input_parcels} (Expected: {aggregated_summary['Input_Parcels']})")
            print(f"  Qualified Parcels in funnel: {qualified_parcels} (Expected: {aggregated_summary['After_CatA_Filter_Parcels']})")
        
        if len(contact_funnel) > 0:
            total_addresses = contact_funnel[contact_funnel['Stage'] == '2. Address Pairs Created']['Count'].iloc[0]
            direct_mail = contact_funnel[contact_funnel['Stage'] == '4. Direct Mail Ready']['Count'].iloc[0]
            print(f"  Total Addresses in funnel: {total_addresses} (Expected: {aggregated_summary['Unique_Owner_Address_Pairs']})")
            print(f"  Direct Mail in funnel: {direct_mail} (Expected: {aggregated_summary['Direct_Mail_Final_Contacts']})")
        
        # Check conversion rates are reasonable
        if 'Conversion_Rate' in enhanced_funnel_df.columns:
            conversion_rates = enhanced_funnel_df['Conversion_Rate'].dropna()
            invalid_rates = conversion_rates[conversion_rates > 100.0]
            print(f"  Conversion rates calculated: {len(conversion_rates)}")
            print(f"  Invalid conversion rates (>100%): {len(invalid_rates)}")
            
            if len(invalid_rates) > 0:
                print(f"  WARNING: Found invalid conversion rates: {invalid_rates.tolist()}")
            else:
                print("  All conversion rates are valid (<= 100%)")
        
        # Overall validation
        stage_count_correct = len(enhanced_funnel_df) == 9
        land_stages_correct = len(land_funnel) == 4
        contact_stages_correct = len(contact_funnel) == 5
        
        if stage_count_correct and land_stages_correct and contact_stages_correct:
            print("\nVALIDATION PASSED - Corrected implementation working correctly!")
            print("Expected: 9 total stages (4 Land + 5 Contact)")
            print(f"Actual: {len(enhanced_funnel_df)} total stages ({len(land_funnel)} Land + {len(contact_funnel)} Contact)")
            return True
        else:
            print("\nVALIDATION FAILED - Stage counts still incorrect")
            return False
            
    except Exception as e:
        print(f"ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test"""
    print("Enhanced Funnel Implementation - Correction Test")
    print("=" * 50)
    
    success = test_corrected_implementation()
    
    if success:
        print("\nCORRECTED IMPLEMENTATION IS READY!")
        print("You can now rerun a campaign to test with real data")
    else:
        print("\nCORRECTION NEEDS MORE WORK")
        
    return success

if __name__ == "__main__":
    main()