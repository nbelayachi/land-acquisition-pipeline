#!/usr/bin/env python3
"""
Business Workflow Validation Script
Validates the land acquisition campaign workflow and metrics from business perspective
Usage: Run in Spyder and paste the output back for review
"""

import pandas as pd
import numpy as np

def validate_business_workflow(excel_path):
    """
    Validate the land acquisition campaign workflow and metrics
    """
    print("="*80)
    print("LAND ACQUISITION BUSINESS WORKFLOW VALIDATION")
    print("="*80)
    print(f"File: {excel_path}")
    print()
    
    try:
        # Read key sheets
        df_raw = pd.read_excel(excel_path, sheet_name='All_Raw_Data')
        df_validation = pd.read_excel(excel_path, sheet_name='All_Validation_Ready')
        df_final = pd.read_excel(excel_path, sheet_name='Final_Mailing_List')
        df_funnel = pd.read_excel(excel_path, sheet_name='Enhanced_Funnel_Analysis')
        df_quality = pd.read_excel(excel_path, sheet_name='Address_Quality_Distribution')
        
        print("🏠 STEP 1: TARGET PARCELS FOR ACQUISITION")
        print("-" * 50)
        
        # Input parcels - these are the properties we want to acquire
        target_parcels = df_raw.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
        print(f"Target Parcels for Acquisition: {len(target_parcels)}")
        
        # Calculate total area of target properties
        df_raw_copy = df_raw.copy()
        df_raw_copy['Area_numeric'] = pd.to_numeric(df_raw_copy['Area'].astype(str).str.replace(',', '.'), errors='coerce')
        parcel_areas = df_raw_copy.groupby(['comune_input', 'foglio_input', 'particella_input'])['Area_numeric'].first()
        total_target_area = parcel_areas.sum()
        
        print(f"Total Target Area: {total_target_area:.2f} hectares")
        print(f"Average Parcel Size: {total_target_area/len(target_parcels):.2f} hectares")
        
        print("\nTarget Parcels by Municipality:")
        for comune in df_raw['comune_input'].unique():
            muni_parcels = df_raw[df_raw['comune_input'] == comune].groupby(['foglio_input', 'particella_input']).size()
            muni_area = df_raw_copy[df_raw_copy['comune_input'] == comune].groupby(['foglio_input', 'particella_input'])['Area_numeric'].first().sum()
            print(f"  {comune}: {len(muni_parcels)} parcels, {muni_area:.2f} ha")
        
        print()
        
        print("👥 STEP 2: PROPERTY OWNERS IDENTIFICATION")
        print("-" * 50)
        
        # All owners of target properties
        total_owners = df_raw['cf'].nunique()
        print(f"Total Property Owners Found: {total_owners}")
        
        # Ownership complexity analysis
        owners_per_parcel = df_raw.groupby(['comune_input', 'foglio_input', 'particella_input'])['cf'].nunique()
        print(f"Average Owners per Parcel: {owners_per_parcel.mean():.2f}")
        print(f"Max Owners on Single Parcel: {owners_per_parcel.max()}")
        
        # Multi-parcel owners
        parcels_per_owner = df_raw.groupby('cf')[['comune_input', 'foglio_input', 'particella_input']].apply(lambda x: len(x.drop_duplicates()))
        multi_parcel_owners = parcels_per_owner[parcels_per_owner > 1]
        print(f"Owners with Multiple Target Parcels: {len(multi_parcel_owners)}")
        
        print("\nOwnership Complexity by Municipality:")
        for comune in df_raw['comune_input'].unique():
            muni_data = df_raw[df_raw['comune_input'] == comune]
            muni_owners = muni_data['cf'].nunique()
            muni_records = len(muni_data)
            print(f"  {comune}: {muni_owners} owners, {muni_records} ownership records")
        
        print()
        
        print("📬 STEP 3: RESIDENTIAL ADDRESS COLLECTION")
        print("-" * 50)
        
        # Address collection and processing
        print(f"Residential Addresses Collected: {len(df_validation)}")
        print(f"Unique Owners in Address List: {df_validation['cf'].nunique()}")
        
        # Address multiplication factor
        address_multiplication = len(df_validation) / total_owners
        print(f"Address Multiplication Factor: {address_multiplication:.2f}x")
        print("  (Some owners have multiple residential addresses)")
        
        # Address quality breakdown
        if 'Address_Confidence' in df_validation.columns:
            quality_dist = df_validation['Address_Confidence'].value_counts()
            print("\nAddress Quality Assessment:")
            for quality, count in quality_dist.items():
                percentage = (count / len(df_validation)) * 100
                print(f"  {quality}: {count} addresses ({percentage:.1f}%)")
        
        print()
        
        print("🔧 STEP 4: ADDRESS ENHANCEMENT & GEOCODING")
        print("-" * 50)
        
        # Geocoding success
        if 'Geocoding_Status' in df_validation.columns:
            geocoding_stats = df_validation['Geocoding_Status'].value_counts()
            print("Geocoding Results:")
            for status, count in geocoding_stats.items():
                percentage = (count / len(df_validation)) * 100
                print(f"  {status}: {count} addresses ({percentage:.1f}%)")
        
        # Enhanced classification results
        print(f"\nAddress Enhancement Results:")
        for _, row in df_quality.iterrows():
            quality = row['Quality_Level']
            count = row['Count']
            percentage = row['Percentage']
            automation = row['Automation_Level']
            print(f"  {quality}: {count} addresses ({percentage:.1f}%) - {automation}")
        
        print()
        
        print("📋 STEP 5: ROUTING DECISIONS")
        print("-" * 50)
        
        # Routing distribution
        if 'Routing_Channel' in df_validation.columns:
            routing_dist = df_validation['Routing_Channel'].value_counts()
            print("Contact Routing Strategy:")
            for route, count in routing_dist.items():
                percentage = (count / len(df_validation)) * 100
                print(f"  {route}: {count} addresses ({percentage:.1f}%)")
        
        # Business impact of routing
        direct_mail_count = routing_dist.get('DIRECT_MAIL', 0) if 'Routing_Channel' in df_validation.columns else 0
        agency_count = routing_dist.get('AGENCY', 0) if 'Routing_Channel' in df_validation.columns else 0
        
        print(f"\nBusiness Impact:")
        print(f"  Ready for Direct Mailing: {direct_mail_count} contacts")
        print(f"  Require Agency Investigation: {agency_count} contacts")
        if direct_mail_count + agency_count > 0:
            automation_rate = (direct_mail_count / (direct_mail_count + agency_count)) * 100
            print(f"  Process Automation Rate: {automation_rate:.1f}%")
        
        print()
        
        print("📤 STEP 6: FINAL MAILING LIST PREPARATION")
        print("-" * 50)
        
        print(f"Final Mailing List Entries: {len(df_final)}")
        
        if len(df_final) > 0:
            print("Final Mailings by Municipality:")
            if 'Municipality' in df_final.columns:
                final_by_muni = df_final['Municipality'].value_counts()
                for muni, count in final_by_muni.items():
                    print(f"  {muni}: {count} mailings")
        
        # Calculate campaign efficiency
        campaign_efficiency = (len(df_final) / len(target_parcels)) * 100
        contact_efficiency = (len(df_final) / len(df_validation)) * 100 if len(df_validation) > 0 else 0
        
        print(f"\nCampaign Efficiency Metrics:")
        print(f"  Mailings per Target Parcel: {len(df_final) / len(target_parcels):.2f}")
        print(f"  Final Mailing Rate: {campaign_efficiency:.1f}% of target parcels")
        print(f"  Contact Conversion Rate: {contact_efficiency:.1f}% of identified contacts")
        
        print()
        
        print("📊 BUSINESS METRICS VALIDATION")
        print("-" * 50)
        
        # Validate key business metrics from funnel
        land_funnel = df_funnel[df_funnel['Funnel_Type'] == 'Land Acquisition']
        contact_funnel = df_funnel[df_funnel['Funnel_Type'] == 'Contact Processing']
        
        print("Land Acquisition Funnel Validation:")
        for _, row in land_funnel.iterrows():
            stage = row['Stage']
            count = row['Count']
            expected_count = None
            
            if 'Input Parcels' in stage:
                expected_count = len(target_parcels)
            elif 'Category A Filter' in stage:
                # This represents parcels suitable for residential development
                expected_count = "Variable based on property types"
            
            status = "✅" if expected_count == count or expected_count is None else "⚠️"
            print(f"  {status} {stage}: {count} (Expected: {expected_count})")
        
        print("\nContact Processing Funnel Validation:")
        for _, row in contact_funnel.iterrows():
            stage = row['Stage']
            count = row['Count']
            conversion = row.get('Conversion_Rate', 'N/A')
            
            expected_count = None
            if 'Owners Identified' in stage:
                expected_count = total_owners
            elif 'Address Pairs Created' in stage:
                expected_count = len(df_validation)
            elif 'Direct Mail Ready' in stage:
                expected_count = direct_mail_count
            elif 'Agency Required' in stage:
                expected_count = agency_count
            
            status = "✅" if expected_count == count or expected_count is None else "⚠️"
            print(f"  {status} {stage}: {count} ({conversion}% conversion, Expected: {expected_count})")
        
        print()
        
        print("🎯 CAMPAIGN SUCCESS INDICATORS")
        print("-" * 50)
        
        # Calculate key success metrics
        parcel_coverage = (len(df_final) / len(target_parcels)) * 100
        owner_reach = (df_validation['cf'].nunique() / total_owners) * 100
        
        print(f"✅ Target Parcel Coverage: {parcel_coverage:.1f}%")
        print(f"✅ Owner Reach Rate: {owner_reach:.1f}%")
        print(f"✅ Address Quality Rate: {(df_quality[df_quality['Quality_Level'].isin(['ULTRA_HIGH', 'HIGH'])]['Count'].sum() / len(df_validation) * 100):.1f}%")
        print(f"✅ Process Automation: {(direct_mail_count / len(df_validation) * 100):.1f}% ready for direct mail")
        
        # Business value assessment
        print(f"\n💼 BUSINESS VALUE ASSESSMENT:")
        ultra_high_addresses = df_quality[df_quality['Quality_Level'] == 'ULTRA_HIGH']['Count'].iloc[0] if len(df_quality[df_quality['Quality_Level'] == 'ULTRA_HIGH']) > 0 else 0
        high_addresses = df_quality[df_quality['Quality_Level'] == 'HIGH']['Count'].iloc[0] if len(df_quality[df_quality['Quality_Level'] == 'HIGH']) > 0 else 0
        
        print(f"  Zero-Touch Processing: {ultra_high_addresses} addresses ({ultra_high_addresses/len(df_validation)*100:.1f}%)")
        print(f"  Quick Review Required: {high_addresses} addresses ({high_addresses/len(df_validation)*100:.1f}%)")
        print(f"  Total Time Savings: {(ultra_high_addresses + high_addresses)/len(df_validation)*100:.1f}% of addresses optimized")
        
    except Exception as e:
        print(f"❌ Error in business workflow validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Path to your test campaign file
    campaign_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_1807\LandAcquisition_Casalpusterlengo_Castiglione_20250703_1807_Results.xlsx"
    
    print("🚀 Starting Business Workflow Validation...")
    print()
    
    validate_business_workflow(campaign_file)
    
    print()
    print("="*80)
    print("BUSINESS VALIDATION COMPLETE")
    print("This analysis focuses on the land acquisition campaign workflow")
    print("and validates metrics from a business perspective")
    print("="*80)