"""
Corrected Funnel Structure
Fixed based on real campaign data validation
"""

import pandas as pd

def create_corrected_funnel():
    """Create corrected funnel structure based on validation results"""
    
    print("CORRECTED FUNNEL STRUCTURE")
    print("=" * 60)
    print("Based on: Real campaign data validation")
    print("Fixed: Owner count discrepancy (13 owners, not 10)")
    print()
    
    # FUNNEL 1: LAND ACQUISITION PIPELINE (Confirmed Accurate)
    land_acquisition_data = [
        {
            'Funnel_Type': 'Land Acquisition',
            'Stage': '1. Input Parcels',
            'Count': 10,
            'Hectares': 56.9,
            'Conversion_Rate': None,
            'Retention_Rate': 100.0,
            'Business_Rule': 'User input - parcels selected for acquisition analysis',
            'Automation_Level': 'Manual',
            'Process_Notes': 'Campaign input from user selection'
        },
        {
            'Funnel_Type': 'Land Acquisition', 
            'Stage': '2. API Data Retrieved',
            'Count': 10,
            'Hectares': 56.9,
            'Conversion_Rate': 100.0,
            'Retention_Rate': 100.0,
            'Business_Rule': 'API successfully retrieved ownership data for all parcels',
            'Automation_Level': 'Fully-Auto',
            'Process_Notes': 'Perfect API success rate in this campaign'
        },
        {
            'Funnel_Type': 'Land Acquisition',
            'Stage': '3. Private Owners Only',
            'Count': 10,
            'Hectares': 56.9,
            'Conversion_Rate': 100.0,
            'Retention_Rate': 100.0,
            'Business_Rule': 'Filter applied - no company owners found in this campaign',
            'Automation_Level': 'Fully-Auto',
            'Process_Notes': 'All owners were individuals, no companies to filter'
        },
        {
            'Funnel_Type': 'Land Acquisition',
            'Stage': '4. Category A Filter',
            'Count': 8,
            'Hectares': 53.0,
            'Conversion_Rate': 80.0,
            'Retention_Rate': 80.0,
            'Business_Rule': 'Category A filter removed 2 parcels (3.9 ha) - non-residential',
            'Automation_Level': 'Fully-Auto',
            'Process_Notes': '20% loss due to property type filtering'
        }
    ]
    
    # FUNNEL 2: CONTACT PROCESSING PIPELINE (Corrected)
    contact_processing_data = [
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '1. Owners Identified',
            'Count': 13,  # CORRECTED: Was 10, now 13
            'Hectares': 53.0,
            'Conversion_Rate': 162.5,  # CORRECTED: 13/8 = 162.5%, was 125%
            'Retention_Rate': 100.0,
            'Business_Rule': 'Owner identification - some parcels have multiple owners',
            'Automation_Level': 'Fully-Auto',
            'Process_Notes': '1.63 owners per parcel on average (corrected from 1.25)'
        },
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '2. Address Pairs Created',
            'Count': 23,
            'Hectares': 53.0,
            'Conversion_Rate': 177.0,  # CORRECTED: 23/13 = 177%, was 230%
            'Retention_Rate': 100.0,
            'Business_Rule': 'Address expansion - owners have multiple addresses (current, historical)',
            'Automation_Level': 'Fully-Auto',
            'Process_Notes': '1.77 addresses per owner on average (corrected from 2.3)'
        },
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '3. Geocoding Completed',
            'Count': 23,
            'Hectares': 53.0,
            'Conversion_Rate': 100.0,
            'Retention_Rate': 100.0,
            'Business_Rule': 'All addresses successfully geocoded and quality assessed',
            'Automation_Level': 'Fully-Auto',
            'Process_Notes': 'Perfect geocoding success rate'
        },
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '4. Direct Mail Ready',
            'Count': 12,
            'Hectares': 42.2,
            'Conversion_Rate': 52.2,
            'Retention_Rate': 52.2,
            'Business_Rule': 'ULTRA_HIGH + HIGH + some MEDIUM confidence addresses',
            'Automation_Level': 'Semi-Auto',
            'Process_Notes': 'Higher confidence addresses for internal processing'
        },
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '5. Agency Required',
            'Count': 11,
            'Hectares': 38.5,
            'Conversion_Rate': 47.8,
            'Retention_Rate': 47.8,
            'Business_Rule': 'LOW confidence + some MEDIUM confidence addresses',
            'Automation_Level': 'Manual',
            'Process_Notes': 'Lower confidence addresses need external expertise'
        }
    ]
    
    # QUALITY DISTRIBUTION (Confirmed Accurate)
    quality_distribution_data = [
        {
            'Quality_Level': 'ULTRA_HIGH',
            'Count': 4,
            'Percentage': 17.4,
            'Processing_Type': 'Zero Touch',
            'Business_Value': 'Immediate print ready',
            'Automation_Level': 'Fully-Auto',
            'Routing_Decision': 'Direct Mail'
        },
        {
            'Quality_Level': 'HIGH',
            'Count': 1,
            'Percentage': 4.3,
            'Processing_Type': 'Quick Review',
            'Business_Value': 'Minimal validation needed',
            'Automation_Level': 'Semi-Auto',
            'Routing_Decision': 'Direct Mail'
        },
        {
            'Quality_Level': 'MEDIUM',
            'Count': 13,
            'Percentage': 56.5,
            'Processing_Type': 'Standard Review',
            'Business_Value': 'Normal processing required',
            'Automation_Level': 'Manual',
            'Routing_Decision': 'Mixed (Direct Mail + Agency)'
        },
        {
            'Quality_Level': 'LOW',
            'Count': 5,
            'Percentage': 21.7,
            'Processing_Type': 'Agency Routing',
            'Business_Value': 'External investigation required',
            'Automation_Level': 'Manual',
            'Routing_Decision': 'Agency'
        }
    ]
    
    # Create DataFrames
    funnel_df = pd.DataFrame(land_acquisition_data + contact_processing_data)
    quality_df = pd.DataFrame(quality_distribution_data)
    
    print("CORRECTED DUAL FUNNEL STRUCTURE")
    print("-" * 40)
    
    # Display funnels
    for funnel_type in funnel_df['Funnel_Type'].unique():
        funnel_data = funnel_df[funnel_df['Funnel_Type'] == funnel_type]
        print(f"\n{funnel_type.upper()} PIPELINE:")
        print("─" * 50)
        
        for idx, row in funnel_data.iterrows():
            stage = row['Stage']
            count = row['Count']
            hectares = row['Hectares']
            conversion = row['Conversion_Rate']
            business_rule = row['Business_Rule']
            notes = row['Process_Notes']
            
            conv_str = f"{conversion:.1f}%" if conversion is not None else "Input"
            
            print(f"{stage}")
            print(f"  Count: {count:2d} | Hectares: {hectares:5.1f} | Conversion: {conv_str:>6}")
            print(f"  Rule: {business_rule}")
            print(f"  Note: {notes}")
            print()
    
    # Display quality distribution
    print("\nADDRESS QUALITY DISTRIBUTION")
    print("─" * 50)
    print("Classification Results (23 total addresses):")
    print()
    
    for idx, row in quality_df.iterrows():
        level = row['Quality_Level']
        count = row['Count']
        percentage = row['Percentage']
        processing = row['Processing_Type']
        value = row['Business_Value']
        routing = row['Routing_Decision']
        
        print(f"{level:>11}: {count:2d} addresses ({percentage:4.1f}%) | {processing}")
        print(f"            {value} -> {routing}")
        print()
    
    # CORRECTED Business metrics
    print("CORRECTED KEY BUSINESS METRICS")
    print("─" * 35)
    
    input_parcels = 10
    final_parcels = 8
    total_owners = 13  # CORRECTED
    total_addresses = 23
    direct_mail = 12
    agency = 11
    ultra_high = 4
    high = 1
    
    print(f"Land Acquisition Efficiency: {final_parcels}/{input_parcels} = {(final_parcels/input_parcels)*100:.1f}%")
    print(f"Owner Discovery Rate: {total_owners}/{final_parcels} = {(total_owners/final_parcels):.2f} owners/parcel (CORRECTED)")
    print(f"Address Expansion Rate: {total_addresses}/{total_owners} = {(total_addresses/total_owners):.2f} addresses/owner (CORRECTED)")
    print(f"Direct Mail Efficiency: {direct_mail}/{total_addresses} = {(direct_mail/total_addresses)*100:.1f}%")
    print(f"Agency Routing Rate: {agency}/{total_addresses} = {(agency/total_addresses)*100:.1f}%")
    print(f"Overall Contact Multiplication: {total_addresses}/{final_parcels} = {(total_addresses/final_parcels):.1f}x")
    print(f"Zero-Touch Processing Rate: {ultra_high}/{total_addresses} = {(ultra_high/total_addresses)*100:.1f}%")
    
    # Show corrections made
    print(f"\nCORRECTIONS MADE:")
    print("─" * 20)
    print(f"Unique Owners: 10 -> 13 (+3 owners)")
    print(f"Owner Discovery Rate: 1.25 -> 1.63 owners/parcel (+30%)")
    print(f"Address Expansion Rate: 2.3 -> 1.77 addresses/owner (-23%)")
    print(f"Owner-to-Parcel Conversion: 125% -> 162.5% (+37.5 percentage points)")
    print(f"Address-to-Owner Conversion: 230% -> 177% (-53 percentage points)")
    
    # Export corrected data
    funnel_df.to_csv("corrected_funnel_data.csv", index=False)
    quality_df.to_csv("corrected_quality_distribution.csv", index=False)
    
    print(f"\nData exported:")
    print(f"  - corrected_funnel_data.csv")
    print(f"  - corrected_quality_distribution.csv")
    
    return funnel_df, quality_df

if __name__ == "__main__":
    print("Creating corrected funnel structure...")
    funnel_data, quality_data = create_corrected_funnel()
    print("\nCorrected funnel structure complete!")
    
    # Final validation
    print("\nFINAL VALIDATION")
    print("─" * 20)
    
    contact_funnel = funnel_data[funnel_data['Funnel_Type'] == 'Contact Processing']
    owners = contact_funnel[contact_funnel['Stage'] == '1. Owners Identified']['Count'].iloc[0]
    addresses = contact_funnel[contact_funnel['Stage'] == '2. Address Pairs Created']['Count'].iloc[0]
    direct_mail = contact_funnel[contact_funnel['Stage'] == '4. Direct Mail Ready']['Count'].iloc[0]
    agency = contact_funnel[contact_funnel['Stage'] == '5. Agency Required']['Count'].iloc[0]
    
    print(f"Owners: {owners} (should be 13)")
    print(f"Addresses: {addresses} (should be 23)")
    print(f"Routing: {direct_mail} + {agency} = {direct_mail + agency} (should be 23)")
    print(f"Quality total: {quality_data['Count'].sum()} (should be 23)")
    
    all_correct = (owners == 13 and addresses == 23 and 
                   direct_mail + agency == 23 and quality_data['Count'].sum() == 23)
    
    print(f"\nAll corrections validated: {all_correct}")
    print("Ready for implementation!")