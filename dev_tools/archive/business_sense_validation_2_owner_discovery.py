import pandas as pd

excel_file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213_Results.xlsx"

print(f"--- Analyzing Owner Discovery from Raw Data ---")

try:
    xls = pd.ExcelFile(excel_file_path)
    df_raw_data = pd.read_excel(xls, 'All_Raw_Data')
    df_funnel_analysis = pd.read_excel(xls, 'Enhanced_Funnel_Analysis')
    
    print("\n✅ Successfully loaded All_Raw_Data and Enhanced_Funnel_Analysis sheets.\n")

    print("--- Sample of All_Raw_Data (relevant columns for owner identification) ---")
    # Displaying key columns that show parcel-owner relationships
    print(df_raw_data[['foglio_input', 'particella_input', 'cf', 'denominazione', 'Tipo_Proprietario', 'quota']].head(10))
    print(f"\nTotal raw records: {len(df_raw_data)}\n")

    print("--- Deriving Unique Private Owners from All_Raw_Data ---")
    # Filter for 'Privato' (private individuals) as per business logic
    df_private_owners = df_raw_data[df_raw_data['Tipo_Proprietario'] == 'Privato']
    
    # Count unique individuals (based on 'cf' - fiscal code)
    unique_private_owners_count = df_private_owners['cf'].nunique()
    print(f"Number of unique private owners identified from raw data: {unique_private_owners_count}\n")

    print("--- Extracting Owner Discovery Metric from Enhanced_Funnel_Analysis ---")
    owner_discovery_stage = df_funnel_analysis[
        (df_funnel_analysis['Funnel_Type'] == 'Contact Processing') &
        (df_funnel_analysis['Stage'] == '1. Owner Discovery')
    ]
    
    if not owner_discovery_stage.empty:
        funnel_owner_count = owner_discovery_stage['Count'].iloc[0]
        owner_discovery_multiplier = owner_discovery_stage['Conversion / Multiplier'].iloc[0]
        business_rule = owner_discovery_stage['Business_Rule'].iloc[0]
        process_notes = owner_discovery_stage['Process_Notes'].iloc[0]
        
        print(f"Funnel's Owner Discovery Count: {funnel_owner_count}")
        print(f"Funnel's Owner Discovery Multiplier: {owner_discovery_multiplier}x")
        print(f"Business Rule: {business_rule}")
        print(f"Process Notes: {process_notes}\n")
        
        # Cross-check with our derived count
        if unique_private_owners_count == funnel_owner_count:
            print("✅ Cross-check: Unique private owners from raw data matches funnel count.")
        else:
            print("❌ Cross-check: Mismatch between unique private owners from raw data and funnel count.")
            
    else:
        print("❌ '1. Owner Discovery' stage not found in Enhanced_Funnel_Analysis.")

except Exception as e:
    print(f"❌ Error during Owner Discovery analysis: {e}")

print("\n--- Script 2 Finished ---")
