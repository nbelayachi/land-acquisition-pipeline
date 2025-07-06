import pandas as pd

excel_file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213_Results.xlsx"

print(f"--- Validating Owner Discovery with Filtered Data ---")

try:
    xls = pd.ExcelFile(excel_file_path)
    df_raw_data = pd.read_excel(xls, 'All_Raw_Data')
    df_validation_ready = pd.read_excel(xls, 'All_Validation_Ready')
    df_funnel_analysis = pd.read_excel(xls, 'Enhanced_Funnel_Analysis')
    
    print("\n✅ Successfully loaded All_Raw_Data, All_Validation_Ready, and Enhanced_Funnel_Analysis sheets.\n")

    print("--- Replicating Filtering Logic for Owner Discovery ---")
    # Step 1: Filter for 'Privato' (private individuals)
    df_private_owners_raw = df_raw_data[df_raw_data['Tipo_Proprietario'] == 'Privato']
    print(f"Raw private owner records: {len(df_private_owners_raw)}")

    # Step 2: Apply Cat.A filter (residential buildings)
    # This is based on the logic in create_municipality_output where individuals_cat_a is derived
    individuals_cat_a = df_private_owners_raw[df_private_owners_raw['classamento'].str.contains('Cat.A', na=False, case=False)]
    print(f"Private owner records after Cat.A filter: {len(individuals_cat_a)}")

    # Step 3: Deduplicate based on 'cf' (fiscal code) to get unique owners on these target parcels
    unique_owners_on_target_parcels = individuals_cat_a['cf'].nunique()
    print(f"Number of unique private owners on Cat.A parcels: {unique_owners_on_target_parcels}\n")

    print("--- Extracting Owner Discovery Metric from Enhanced_Funnel_Analysis ---")
    owner_discovery_stage = df_funnel_analysis[
        (df_funnel_analysis['Funnel_Type'] == 'Contact Processing') &
        (df_funnel_analysis['Stage'] == '1. Owner Discovery')
    ]
    
    if not owner_discovery_stage.empty:
        funnel_owner_count = owner_discovery_stage['Count'].iloc[0]
        print(f"Funnel's Owner Discovery Count: {funnel_owner_count}\n")
        
        # Cross-check with our derived count from filtered data
        if unique_owners_on_target_parcels == funnel_owner_count:
            print("✅ Cross-check: Unique private owners from filtered raw data matches funnel count.")
            print("Business Sense: The 'Owner Discovery' metric correctly reflects unique private owners on residential-classified parcels, which are the primary targets for contact.")
        else:
            print("❌ Cross-check: Mismatch between unique private owners from filtered raw data and funnel count.")
            
    else:
        print("❌ '1. Owner Discovery' stage not found in Enhanced_Funnel_Analysis.")

except Exception as e:
    print(f"❌ Error during filtered Owner Discovery analysis: {e}")

print("\n--- Script 3 Finished ---")
