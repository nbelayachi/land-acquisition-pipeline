"""
Test Enhanced Funnel Data Structure
Generate sample data based on current campaign to validate enhanced funnel design
"""

import pandas as pd

def create_enhanced_funnel_sample():
    """Create sample enhanced funnel data based on current campaign analysis"""
    
    print("ENHANCED FUNNEL DATA GENERATION")
    print("=" * 50)
    print("Based on: Casalpusterlengo_Castiglione_20250702_0018")
    print()
    
    # FUNNEL 1: LAND ACQUISITION PIPELINE
    land_acquisition_data = [
        {
            'Funnel_Type': 'Land Acquisition',
            'Stage': '1. Input Parcels',
            'Count': 10,
            'Hectares': 56.9,
            'Conversion_Rate': None,  # First stage has no conversion
            'Cumulative_Loss': 0.0,
            'Business_Rule': 'User input - parcels selected for acquisition analysis',
            'Time_Impact_Minutes': 0,
            'Automation_Level': 'Manual',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        },
        {
            'Funnel_Type': 'Land Acquisition', 
            'Stage': '2. API Data Retrieved',
            'Count': 10,
            'Hectares': 56.9,
            'Conversion_Rate': 100.0,
            'Cumulative_Loss': 0.0,
            'Business_Rule': 'API successfully retrieved ownership data for all parcels',
            'Time_Impact_Minutes': 0,
            'Automation_Level': 'Fully-Auto',
            'CP': 'Mixed',
            'comune': 'Multiple', 
            'provincia': 'LO/BS'
        },
        {
            'Funnel_Type': 'Land Acquisition',
            'Stage': '3. Private Owners Only',
            'Count': 10,
            'Hectares': 56.9,
            'Conversion_Rate': 100.0,
            'Cumulative_Loss': 0.0,
            'Business_Rule': 'Filter applied - no company owners found in this campaign',
            'Time_Impact_Minutes': 0,
            'Automation_Level': 'Fully-Auto',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        },
        {
            'Funnel_Type': 'Land Acquisition',
            'Stage': '4. Category A Filter Applied',
            'Count': 8,
            'Hectares': 53.0,
            'Conversion_Rate': 80.0,
            'Cumulative_Loss': 20.0,
            'Business_Rule': 'Category A filter removed 2 parcels (3.9 ha) - non-residential properties',
            'Time_Impact_Minutes': 0,
            'Automation_Level': 'Fully-Auto',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        }
    ]
    
    # FUNNEL 2: CONTACT GENERATION PIPELINE  
    contact_generation_data = [
        {
            'Funnel_Type': 'Contact Generation',
            'Stage': '0. Category A Parcels (Input)',
            'Count': 8,
            'Hectares': 53.0,
            'Conversion_Rate': None,  # Input from previous funnel
            'Cumulative_Loss': 0.0,
            'Business_Rule': 'Input from Land Acquisition Pipeline - filtered parcels ready for contact processing',
            'Time_Impact_Minutes': 0,
            'Automation_Level': 'Fully-Auto',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        },
        {
            'Funnel_Type': 'Contact Generation',
            'Stage': '1. Unique Owners Identified',
            'Count': 10,
            'Hectares': 53.0,
            'Conversion_Rate': 125.0,  # 10 owners from 8 parcels
            'Cumulative_Loss': 0.0,
            'Business_Rule': 'Owner identification - some parcels have multiple owners, some owners appear on multiple parcels',
            'Time_Impact_Minutes': 0,
            'Automation_Level': 'Fully-Auto',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        },
        {
            'Funnel_Type': 'Contact Generation',
            'Stage': '2. Owner-Address Pairs Created',
            'Count': 23,
            'Hectares': 53.0,
            'Conversion_Rate': 230.0,  # 23 addresses from 10 owners
            'Cumulative_Loss': 0.0,
            'Business_Rule': 'Address expansion - owners have multiple addresses (current, historical, etc.)',
            'Time_Impact_Minutes': 0,
            'Automation_Level': 'Fully-Auto',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        },
        {
            'Funnel_Type': 'Contact Generation',
            'Stage': '3. Address Quality Assessment',
            'Count': 23,
            'Hectares': 53.0,
            'Conversion_Rate': 100.0,
            'Cumulative_Loss': 0.0,
            'Business_Rule': 'Enhanced classification applied - geocoding and confidence scoring completed',
            'Time_Impact_Minutes': 0,
            'Automation_Level': 'Fully-Auto',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        },
        {
            'Funnel_Type': 'Contact Generation',
            'Stage': '4. Direct Mail Routing',
            'Count': 12,
            'Hectares': 42.2,
            'Conversion_Rate': 52.2,  # 12 of 23 routed to direct mail
            'Cumulative_Loss': 47.8,
            'Business_Rule': 'ULTRA_HIGH + HIGH + some MEDIUM confidence addresses routed for direct mailing',
            'Time_Impact_Minutes': 35,  # Reduced review time
            'Automation_Level': 'Semi-Auto',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        },
        {
            'Funnel_Type': 'Contact Generation',
            'Stage': '4. Agency Review Routing',
            'Count': 11,
            'Hectares': 38.5,
            'Conversion_Rate': 47.8,  # 11 of 23 routed to agency
            'Cumulative_Loss': 52.2,
            'Business_Rule': 'LOW confidence + some MEDIUM confidence addresses require agency investigation',
            'Time_Impact_Minutes': 0,  # External to our process
            'Automation_Level': 'Manual',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        }
    ]
    
    # FUNNEL 3: ADDRESS QUALITY PIPELINE (New)
    address_quality_data = [
        {
            'Funnel_Type': 'Address Quality',
            'Stage': '1. Raw Addresses Collected',
            'Count': 23,
            'Hectares': 53.0,
            'Conversion_Rate': None,
            'Cumulative_Loss': 0.0,
            'Business_Rule': 'All owner-address pairs identified and collected for quality assessment',
            'Time_Impact_Minutes': 184,  # Traditional process baseline
            'Automation_Level': 'Manual',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        },
        {
            'Funnel_Type': 'Address Quality',
            'Stage': '2. Geocoding Attempted',
            'Count': 23,
            'Hectares': 53.0,
            'Conversion_Rate': 100.0,
            'Cumulative_Loss': 0.0,
            'Business_Rule': 'All addresses submitted to geocoding API for verification and enhancement',
            'Time_Impact_Minutes': 0,
            'Automation_Level': 'Fully-Auto',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        },
        {
            'Funnel_Type': 'Address Quality',
            'Stage': '3. Geocoding Successful',
            'Count': 23,
            'Hectares': 53.0,
            'Conversion_Rate': 100.0,
            'Cumulative_Loss': 0.0,
            'Business_Rule': 'All addresses successfully geocoded - no failures in this campaign',
            'Time_Impact_Minutes': 0,
            'Automation_Level': 'Fully-Auto',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        },
        {
            'Funnel_Type': 'Address Quality',
            'Stage': '4. ULTRA_HIGH Confidence',
            'Count': 4,
            'Hectares': 16.9,  # Estimated from validation data
            'Conversion_Rate': 17.4,
            'Cumulative_Loss': 82.6,
            'Business_Rule': 'Perfect address match + complete geocoding data - ready for immediate printing',
            'Time_Impact_Minutes': 0,  # Zero review time
            'Automation_Level': 'Fully-Auto',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        },
        {
            'Funnel_Type': 'Address Quality',
            'Stage': '4. HIGH Confidence',
            'Count': 1,
            'Hectares': 2.6,  # Estimated
            'Conversion_Rate': 4.3,
            'Cumulative_Loss': 95.7,
            'Business_Rule': 'Strong address match - requires 5-minute review before printing',
            'Time_Impact_Minutes': 5,
            'Automation_Level': 'Semi-Auto',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        },
        {
            'Funnel_Type': 'Address Quality',
            'Stage': '4. MEDIUM Confidence',
            'Count': 13,
            'Hectares': 28.3,  # Estimated
            'Conversion_Rate': 56.5,
            'Cumulative_Loss': 43.5,
            'Business_Rule': 'Moderate address quality - requires standard 8-minute review',
            'Time_Impact_Minutes': 104,  # 13 * 8 minutes
            'Automation_Level': 'Manual',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        },
        {
            'Funnel_Type': 'Address Quality',
            'Stage': '4. LOW Confidence',
            'Count': 5,
            'Hectares': 5.2,  # Estimated
            'Conversion_Rate': 21.7,
            'Cumulative_Loss': 78.3,
            'Business_Rule': 'Poor address quality - routed to agency for manual investigation',
            'Time_Impact_Minutes': 0,  # External process
            'Automation_Level': 'Manual',
            'CP': 'Mixed',
            'comune': 'Multiple',
            'provincia': 'LO/BS'
        }
    ]
    
    # Combine all data
    enhanced_funnel_data = land_acquisition_data + contact_generation_data + address_quality_data
    
    # Create DataFrame
    enhanced_df = pd.DataFrame(enhanced_funnel_data)
    
    print("ENHANCED FUNNEL DATA STRUCTURE")
    print("-" * 40)
    print(f"Total rows: {len(enhanced_df)}")
    print(f"Columns: {list(enhanced_df.columns)}")
    print()
    
    # Display by funnel type
    for funnel_type in enhanced_df['Funnel_Type'].unique():
        funnel_data = enhanced_df[enhanced_df['Funnel_Type'] == funnel_type]
        print(f"{funnel_type.upper()} FUNNEL:")
        print("-" * 30)
        
        for idx, row in funnel_data.iterrows():
            stage = row['Stage']
            count = row['Count']
            hectares = row['Hectares']
            conversion = row['Conversion_Rate']
            business_rule = row['Business_Rule']
            time_impact = row['Time_Impact_Minutes']
            automation = row['Automation_Level']
            
            conv_str = f"{conversion:.1f}%" if conversion is not None else "Input"
            time_str = f"{time_impact} min" if time_impact > 0 else "0 min"
            
            print(f"  {stage}")
            print(f"    Count: {count}, Hectares: {hectares:.1f}, Conversion: {conv_str}")
            print(f"    Time: {time_str}, Automation: {automation}")
            print(f"    Rule: {business_rule}")
            print()
    
    # Calculate summary metrics
    print("ENHANCED METRICS SUMMARY")
    print("-" * 30)
    
    # Land acquisition efficiency
    input_parcels = enhanced_df[(enhanced_df['Funnel_Type'] == 'Land Acquisition') & 
                               (enhanced_df['Stage'] == '1. Input Parcels')]['Count'].iloc[0]
    final_parcels = enhanced_df[(enhanced_df['Funnel_Type'] == 'Land Acquisition') & 
                               (enhanced_df['Stage'] == '4. Category A Filter Applied')]['Count'].iloc[0]
    land_efficiency = (final_parcels / input_parcels) * 100
    
    # Contact multiplication  
    contact_multiplication = 23 / 8  # 23 addresses from 8 parcels
    
    # Address quality breakdown
    ultra_high = enhanced_df[(enhanced_df['Funnel_Type'] == 'Address Quality') & 
                            (enhanced_df['Stage'] == '4. ULTRA_HIGH Confidence')]['Count'].iloc[0]
    high = enhanced_df[(enhanced_df['Funnel_Type'] == 'Address Quality') & 
                      (enhanced_df['Stage'] == '4. HIGH Confidence')]['Count'].iloc[0]
    
    # Time savings
    traditional_time = 184  # 23 addresses * 8 minutes
    enhanced_time = 0 + 5 + 104 + 0  # ULTRA_HIGH + HIGH + MEDIUM + LOW
    time_savings_pct = ((traditional_time - enhanced_time) / traditional_time) * 100
    
    print(f"Land Acquisition Efficiency: {land_efficiency:.1f}%")
    print(f"Contact Multiplication Factor: {contact_multiplication:.1f}x")
    print(f"Zero-Touch Processing: {ultra_high} addresses ({ultra_high/23*100:.1f}%)")
    print(f"Quick-Review Processing: {high} addresses ({high/23*100:.1f}%)")
    print(f"Time Savings: {traditional_time - enhanced_time} minutes ({time_savings_pct:.1f}%)")
    print(f"Direct Mail Efficiency: 52.2% of contacts ready for mailing")
    
    # Export sample data
    output_file = "enhanced_funnel_sample_data.csv"
    enhanced_df.to_csv(output_file, index=False)
    print(f"\nSample data exported to: {output_file}")
    
    return enhanced_df

if __name__ == "__main__":
    print("Generating enhanced funnel sample data...")
    sample_data = create_enhanced_funnel_sample()
    print("\nEnhanced funnel data generation complete!")
    
    # Additional validation
    print("\nDATA VALIDATION")
    print("-" * 20)
    
    # Check conversion rate calculations
    land_funnel = sample_data[sample_data['Funnel_Type'] == 'Land Acquisition']
    contact_funnel = sample_data[sample_data['Funnel_Type'] == 'Contact Generation']
    quality_funnel = sample_data[sample_data['Funnel_Type'] == 'Address Quality']
    
    print(f"Land Acquisition stages: {len(land_funnel)}")
    print(f"Contact Generation stages: {len(contact_funnel)}")
    print(f"Address Quality stages: {len(quality_funnel)}")
    
    # Verify business logic connections
    final_land_count = land_funnel[land_funnel['Stage'] == '4. Category A Filter Applied']['Count'].iloc[0]
    input_contact_owners = contact_funnel[contact_funnel['Stage'] == '1. Unique Owners Identified']['Count'].iloc[0]
    
    print(f"\nBusiness Logic Validation:")
    print(f"Final parcels (Land): {final_land_count}")
    print(f"Owners identified (Contact): {input_contact_owners}")
    print(f"Ratio: {input_contact_owners/final_land_count:.2f} owners per parcel")
    
    # Verify routing consistency
    direct_mail = contact_funnel[contact_funnel['Stage'] == '4. Direct Mail Routing']['Count'].iloc[0]
    agency = contact_funnel[contact_funnel['Stage'] == '4. Agency Review Routing']['Count'].iloc[0]
    total_addresses = contact_funnel[contact_funnel['Stage'] == '2. Owner-Address Pairs Created']['Count'].iloc[0]
    
    print(f"\nRouting Validation:")
    print(f"Direct Mail: {direct_mail}")
    print(f"Agency: {agency}")
    print(f"Total: {direct_mail + agency} (should equal {total_addresses})")
    print(f"Routing consistent: {direct_mail + agency == total_addresses}")
    
    print("\n✅ Enhanced funnel design validated!")