"""
Analyze Category A Filter Impact on Owner Count
Understanding the relationship between parcel filtering and owner identification
"""

import pandas as pd

# Load real campaign data
results_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250702_0018\LandAcquisition_Casalpusterlengo_Castiglione_20250702_0018_Results.xlsx"

print("CATEGORY A FILTER IMPACT ANALYSIS")
print("=" * 50)

try:
    # Read key data
    validation_df = pd.read_excel(results_file, sheet_name='All_Validation_Ready')
    campaign_summary_df = pd.read_excel(results_file, sheet_name='Campaign_Summary')
    raw_data_df = pd.read_excel(results_file, sheet_name='All_Raw_Data')
    
    print("1. RAW DATA ANALYSIS")
    print("-" * 25)
    
    # Analyze raw data before any filtering
    print(f"Total raw ownership records: {len(raw_data_df)}")
    print(f"Unique owners in raw data: {raw_data_df['cf'].nunique()}")
    print(f"Unique parcels in raw data: {len(raw_data_df[['foglio_input', 'particella_input']].drop_duplicates())}")
    
    # Check property types in raw data
    if 'classamento' in raw_data_df.columns:
        raw_property_types = raw_data_df['classamento'].value_counts()
        print(f"\nProperty types in raw data:")
        for prop_type, count in raw_property_types.items():
            print(f"  {prop_type}: {count} records")
    
    print(f"\n2. VALIDATION READY DATA ANALYSIS")
    print("-" * 35)
    
    # Analyze validation ready data (after all filtering)
    print(f"Validation ready records: {len(validation_df)}")
    print(f"Unique owners in validation data: {validation_df['cf'].nunique()}")
    print(f"Unique parcels in validation data: {len(validation_df[['foglio_input', 'particella_input']].drop_duplicates())}")
    
    # Check property types in validation data
    if 'classamento' in validation_df.columns:
        val_property_types = validation_df['classamento'].value_counts()
        print(f"\nProperty types in validation data:")
        for prop_type, count in val_property_types.items():
            print(f"  {prop_type}: {count} records")
    
    print(f"\n3. UNDERSTANDING THE FUNNEL LOGIC")
    print("-" * 35)
    
    # The key insight: Category A filter operates BEFORE owner identification
    # But owners are counted AFTER Category A filter
    
    # From campaign summary
    total_owners_summary = campaign_summary_df['Unique_Individual_Owners'].sum()
    
    print("Current funnel understanding:")
    print("  Step 1: 10 parcels input")
    print("  Step 2: 10 parcels after API")
    print("  Step 3: 10 parcels private owners")
    print("  Step 4: 8 parcels after Cat.A filter")
    print("  Step 5: ? owners identified from the 8 remaining parcels")
    print()
    
    print("The question: Are the 13 owners from:")
    print("  Option A: All 10 original parcels (before Cat.A filter)?")
    print("  Option B: Only the 8 remaining parcels (after Cat.A filter)?")
    print()
    
    # Let's check by analyzing owners per parcel
    owners_by_parcel = validation_df.groupby(['foglio_input', 'particella_input']).agg({
        'cf': 'nunique',
        'Area': 'first',
        'classamento': 'first'
    }).reset_index()
    
    print("4. OWNERS BY PARCEL BREAKDOWN")
    print("-" * 30)
    print(f"Parcels in validation data: {len(owners_by_parcel)}")
    print()
    
    total_unique_owners = 0
    for idx, row in owners_by_parcel.iterrows():
        foglio = row['foglio_input'] 
        particella = row['particella_input']
        owner_count = row['cf']
        area = row['Area']
        classamento = row['classamento']
        total_unique_owners += owner_count
        
        print(f"  Parcel {foglio}-{particella}: {owner_count} owners, {area:.1f} ha, {classamento}")
    
    print(f"\nTotal owners by summing parcels: {total_unique_owners}")
    print(f"Unique owners (avoiding double-counting): {validation_df['cf'].nunique()}")
    
    # The difference indicates owners who appear on multiple parcels
    if total_unique_owners != validation_df['cf'].nunique():
        print(f"Difference: {total_unique_owners - validation_df['cf'].nunique()} (owners appearing on multiple parcels)")
    
    print(f"\n5. FUNNEL CORRECTION NEEDED")
    print("-" * 30)
    
    print("The correct interpretation should be:")
    print("  Land Acquisition Pipeline:")
    print("    1. Input Parcels: 10")
    print("    2. API Data Retrieved: 10") 
    print("    3. Private Owners Only: 10")
    print("    4. Category A Filter: 8")
    print()
    print("  Contact Processing Pipeline:")
    print("    Input: 8 parcels (after Cat.A filter)")
    print("    1. Owners Identified: 13 (from the 8 remaining parcels)")
    print("    2. Address Pairs Created: 23")
    print("    3. etc...")
    print()
    
    print("This means:")
    print(f"  Owner Discovery Rate: 13 owners / 8 parcels = {13/8:.2f} owners/parcel")
    print("  This is higher than our original calculation because:")
    print("  - We're only counting owners from qualified parcels")
    print("  - Some owners may appear on multiple qualified parcels")
    
    print(f"\n6. VALIDATION OF LOGIC")
    print("-" * 25)
    
    # Check if this interpretation makes sense
    qualified_parcels = len(owners_by_parcel)  # Should be 8
    unique_owners_from_qualified = validation_df['cf'].nunique()  # Should be 13
    
    print(f"Qualified parcels (Cat.A): {qualified_parcels}")
    print(f"Unique owners from qualified parcels: {unique_owners_from_qualified}")
    print(f"Owner discovery rate: {unique_owners_from_qualified/qualified_parcels:.2f} owners/parcel")
    
    logic_correct = (qualified_parcels == 8 and unique_owners_from_qualified == 13)
    print(f"\nLogic validation: {'CORRECT' if logic_correct else 'NEEDS REVIEW'}")
    
    if logic_correct:
        print("✅ The funnel logic is correct as implemented.")
        print("   The 13 owners are identified from the 8 Category A parcels.")
        print("   The higher owner/parcel ratio reflects:")
        print("   - Multiple owners per parcel")
        print("   - Focus on qualified parcels only")
    
except Exception as e:
    print(f"Error: {str(e)}")