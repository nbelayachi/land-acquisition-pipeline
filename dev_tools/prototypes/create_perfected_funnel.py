"""
Perfected Funnel Structure
Fixed conversion rates, stage numbering, and structure issues
"""

import pandas as pd

def create_perfected_funnel():
    """Create perfected funnel structure based on analysis"""
    
    print("PERFECTED FUNNEL STRUCTURE")
    print("=" * 60)
    print("Based on: Casalpusterlengo_Castiglione_20250702_0018")
    print("Fixes: Conversion rates, stage numbering, structure clarity")
    print()
    
    # FUNNEL 1: LAND ACQUISITION PIPELINE
    land_acquisition_data = [
        {
            'Funnel_Type': 'Land Acquisition',
            'Stage': '1. Input Parcels',
            'Count': 10,
            'Hectares': 56.9,
            'Conversion_Rate': None,  # Starting point
            'Retention_Rate': 100.0,
            'Business_Rule': 'User input - parcels selected for acquisition analysis',
            'Automation_Level': 'Manual',
            'Notes': 'Campaign input from user selection'
        },
        {
            'Funnel_Type': 'Land Acquisition', 
            'Stage': '2. API Data Retrieved',
            'Count': 10,
            'Hectares': 56.9,
            'Conversion_Rate': 100.0,  # 10/10 successful
            'Retention_Rate': 100.0,
            'Business_Rule': 'API successfully retrieved ownership data for all parcels',
            'Automation_Level': 'Fully-Auto',
            'Notes': 'Perfect API success rate in this campaign'
        },
        {
            'Funnel_Type': 'Land Acquisition',
            'Stage': '3. Private Owners Only',
            'Count': 10,
            'Hectares': 56.9,
            'Conversion_Rate': 100.0,  # 10/10 were private
            'Retention_Rate': 100.0,
            'Business_Rule': 'Filter applied - no company owners found in this campaign',
            'Automation_Level': 'Fully-Auto',
            'Notes': 'All owners were individuals, no companies to filter'
        },
        {
            'Funnel_Type': 'Land Acquisition',
            'Stage': '4. Category A Filter',
            'Count': 8,
            'Hectares': 53.0,
            'Conversion_Rate': 80.0,  # 8/10 passed filter
            'Retention_Rate': 80.0,
            'Business_Rule': 'Category A filter removed 2 parcels (3.9 ha) - non-residential',
            'Automation_Level': 'Fully-Auto',
            'Notes': '20% loss due to property type filtering'
        }
    ]
    
    # FUNNEL 2: CONTACT PROCESSING PIPELINE  
    contact_processing_data = [
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '1. Owners Identified',
            'Count': 10,
            'Hectares': 53.0,
            'Conversion_Rate': 125.0,  # 10 owners from 8 parcels
            'Retention_Rate': 100.0,
            'Business_Rule': 'Owner identification - some parcels have multiple owners',
            'Automation_Level': 'Fully-Auto',
            'Notes': '1.25 owners per parcel on average'
        },
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '2. Address Pairs Created',
            'Count': 23,
            'Hectares': 53.0,
            'Conversion_Rate': 230.0,  # 23 addresses from 10 owners
            'Retention_Rate': 100.0,
            'Business_Rule': 'Address expansion - owners have multiple addresses (current, historical)',
            'Automation_Level': 'Fully-Auto',
            'Notes': '2.3 addresses per owner on average'
        },
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '3. Geocoding Completed',
            'Count': 23,
            'Hectares': 53.0,
            'Conversion_Rate': 100.0,  # 23/23 geocoded successfully
            'Retention_Rate': 100.0,
            'Business_Rule': 'All addresses successfully geocoded and quality assessed',
            'Automation_Level': 'Fully-Auto',
            'Notes': 'Perfect geocoding success rate'
        },
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '4. Direct Mail Ready',
            'Count': 12,
            'Hectares': 42.2,
            'Conversion_Rate': 52.2,  # 12/23 routed to direct mail
            'Retention_Rate': 52.2,
            'Business_Rule': 'ULTRA_HIGH + HIGH + some MEDIUM confidence → direct mailing',
            'Automation_Level': 'Semi-Auto',
            'Notes': 'Higher confidence addresses for internal processing'
        },
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '5. Agency Required',
            'Count': 11,
            'Hectares': 38.5,
            'Conversion_Rate': 47.8,  # 11/23 routed to agency
            'Retention_Rate': 47.8,
            'Business_Rule': 'LOW confidence + some MEDIUM confidence → agency investigation',
            'Automation_Level': 'Manual',
            'Notes': 'Lower confidence addresses need external expertise'
        }
    ]
    
    # QUALITY DISTRIBUTION (Not a funnel - it's a breakdown)
    quality_distribution_data = [
        {
            'Quality_Level': 'ULTRA_HIGH',
            'Count': 4,
            'Percentage': 17.4,
            'Review_Time_Minutes': 0,
            'Review_Type': 'Zero Touch',
            'Business_Value': 'Immediate print ready',
            'Automation_Level': 'Fully-Auto'
        },
        {
            'Quality_Level': 'HIGH',
            'Count': 1,
            'Percentage': 4.3,
            'Review_Time_Minutes': 5,
            'Review_Type': 'Quick Review',
            'Business_Value': '5-minute validation',
            'Automation_Level': 'Semi-Auto'
        },
        {
            'Quality_Level': 'MEDIUM',
            'Count': 13,
            'Percentage': 56.5,
            'Review_Time_Minutes': 104,  # 13 * 8 minutes
            'Review_Type': 'Standard Review',
            'Business_Value': 'Normal processing',
            'Automation_Level': 'Manual'
        },
        {
            'Quality_Level': 'LOW',
            'Count': 5,
            'Percentage': 21.7,
            'Review_Time_Minutes': 0,  # Routed to agency
            'Review_Type': 'Agency Routing',
            'Business_Value': 'External investigation',
            'Automation_Level': 'Manual'
        }
    ]
    
    # Create DataFrames
    funnel_df = pd.DataFrame(land_acquisition_data + contact_processing_data)
    quality_df = pd.DataFrame(quality_distribution_data)
    
    print("DUAL FUNNEL STRUCTURE")
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
            retention = row['Retention_Rate']
            business_rule = row['Business_Rule']
            automation = row['Automation_Level']
            notes = row['Notes']
            
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
    
    total_time = 0
    for idx, row in quality_df.iterrows():
        level = row['Quality_Level']
        count = row['Count']
        percentage = row['Percentage']
        time = row['Review_Time_Minutes']
        review_type = row['Review_Type']
        value = row['Business_Value']
        automation = row['Automation_Level']
        
        total_time += time
        
        print(f"{level:>11}: {count:2d} addresses ({percentage:4.1f}%) │ {time:3d} min │ {review_type}")
        print(f"            {value} │ {automation}")
        print()
    
    # Summary metrics
    traditional_time = 23 * 8  # 184 minutes
    time_savings = traditional_time - total_time
    efficiency_gain = (time_savings / traditional_time) * 100
    
    print("TIME EFFICIENCY ANALYSIS")
    print("─" * 30)
    print(f"Traditional process: {traditional_time} minutes (23 × 8 min)")
    print(f"Enhanced process:    {total_time} minutes")
    print(f"Time savings:        {time_savings} minutes ({efficiency_gain:.1f}% improvement)")
    print(f"Zero-touch addresses: {quality_df[quality_df['Quality_Level']=='ULTRA_HIGH']['Count'].iloc[0]} ({quality_df[quality_df['Quality_Level']=='ULTRA_HIGH']['Percentage'].iloc[0]:.1f}%)")
    
    # Key business metrics
    print(f"\nKEY BUSINESS METRICS")
    print("─" * 25)
    
    # From funnel data
    input_parcels = funnel_df[funnel_df['Stage'] == '1. Input Parcels']['Count'].iloc[0]
    final_parcels = funnel_df[funnel_df['Stage'] == '4. Category A Filter']['Count'].iloc[0]
    total_owners = funnel_df[funnel_df['Stage'] == '1. Owners Identified']['Count'].iloc[0]
    total_addresses = funnel_df[funnel_df['Stage'] == '2. Address Pairs Created']['Count'].iloc[0]
    direct_mail = funnel_df[funnel_df['Stage'] == '4. Direct Mail Ready']['Count'].iloc[0]
    
    print(f"Land Acquisition Efficiency: {final_parcels}/{input_parcels} = {(final_parcels/input_parcels)*100:.1f}%")
    print(f"Owner Discovery Rate: {total_owners}/{final_parcels} = {(total_owners/final_parcels):.2f} owners/parcel")
    print(f"Address Expansion Rate: {total_addresses}/{total_owners} = {(total_addresses/total_owners):.1f} addresses/owner")
    print(f"Direct Mail Efficiency: {direct_mail}/{total_addresses} = {(direct_mail/total_addresses)*100:.1f}%")
    print(f"Overall Contact Multiplication: {total_addresses}/{final_parcels} = {(total_addresses/final_parcels):.1f}x")
    
    # Export data
    funnel_df.to_csv("perfected_funnel_data.csv", index=False)
    quality_df.to_csv("quality_distribution_data.csv", index=False)
    
    print(f"\n📊 Data exported:")
    print(f"  - perfected_funnel_data.csv")
    print(f"  - quality_distribution_data.csv")
    
    return funnel_df, quality_df

if __name__ == "__main__":
    print("Creating perfected funnel structure...")
    funnel_data, quality_data = create_perfected_funnel()
    print("\n✅ Perfected funnel structure complete!")
    
    # Validation
    print("\nVALIDATION CHECKS")
    print("─" * 20)
    
    # Check funnel consistency
    contact_funnel = funnel_data[funnel_data['Funnel_Type'] == 'Contact Processing']
    total_addresses = contact_funnel[contact_funnel['Stage'] == '2. Address Pairs Created']['Count'].iloc[0]
    direct_mail = contact_funnel[contact_funnel['Stage'] == '4. Direct Mail Ready']['Count'].iloc[0]
    agency = contact_funnel[contact_funnel['Stage'] == '5. Agency Required']['Count'].iloc[0]
    
    print(f"Address routing consistency: {total_addresses} = {direct_mail} + {agency} = {direct_mail + agency}")
    print(f"✅ Routing consistent: {total_addresses == direct_mail + agency}")
    
    # Check quality distribution
    quality_total = quality_data['Count'].sum()
    quality_percentage_total = quality_data['Percentage'].sum()
    
    print(f"Quality distribution total: {quality_total} addresses")
    print(f"Quality percentage total: {quality_percentage_total:.1f}%")
    print(f"✅ Quality distribution consistent: {quality_total == total_addresses and abs(quality_percentage_total - 100.0) < 0.1}")
    
    print("\n🎯 Funnel structure perfected and validated!")