import pandas as pd
import numpy as np

excel_file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213_Results.xlsx"

print(f"--- Analyzing Address Expansion ---")

try:
    xls = pd.ExcelFile(excel_file_path)
    df_validation_ready = pd.read_excel(xls, 'All_Validation_Ready')
    df_funnel_analysis = pd.read_excel(xls, 'Enhanced_Funnel_Analysis')
    
    print("\n✅ Successfully loaded All_Validation_Ready and Enhanced_Funnel_Analysis sheets.\n")

    print("--- Deriving Address Expansion from All_Validation_Ready ---")
    # Count unique owners from the validation ready data (output of Owner Discovery)
    unique_owners_from_validation = df_validation_ready['cf'].nunique()
    print(f"Number of unique owners in All_Validation_Ready: {unique_owners_from_validation}")

    # Count total address pairs (rows) in All_Validation_Ready
    total_address_pairs = len(df_validation_ready)
    print(f"Total address pairs in All_Validation_Ready: {total_address_pairs}\n")

    # Calculate the Address Expansion Multiplier manually
    calculated_address_expansion_multiplier = total_address_pairs / unique_owners_from_validation if unique_owners_from_validation > 0 else 0
    print(f"Calculated Address Expansion Multiplier: {calculated_address_expansion_multiplier:.2f}x\n")

    print("--- Extracting Address Expansion Metric from Enhanced_Funnel_Analysis ---")
    address_expansion_stage = df_funnel_analysis[
        (df_funnel_analysis['Funnel_Type'] == 'Contact Processing') &
        (df_funnel_analysis['Stage'] == '2. Address Expansion')
    ]
    
    if not address_expansion_stage.empty:
        funnel_address_pairs_count = address_expansion_stage['Count'].iloc[0]
        funnel_address_expansion_multiplier = address_expansion_stage['Conversion / Multiplier'].iloc[0]
        business_rule = address_expansion_stage['Business_Rule'].iloc[0]
        process_notes = address_expansion_stage['Process_Notes'].iloc[0]
        
        print(f"Funnel's Address Expansion Count: {funnel_address_pairs_count}")
        print(f"Funnel's Address Expansion Multiplier: {funnel_address_expansion_multiplier}x")
        print(f"Business Rule: {business_rule}")
        print(f"Process Notes: {process_notes}\n")
        
        # Cross-check with our derived count and multiplier
        if total_address_pairs == funnel_address_pairs_count and \
           np.isclose(calculated_address_expansion_multiplier, funnel_address_expansion_multiplier, atol=0.01):
            print("✅ Cross-check: Address pairs count and multiplier from validation data matches funnel.")
            print("Business Sense: The 'Address Expansion' metric correctly shows the multiplication of addresses per unique owner, indicating the pipeline's ability to find all relevant contact points.")
        else:
            print("❌ Cross-check: Mismatch between address pairs count/multiplier from validation data and funnel.")
            
    else:
        print("❌ '2. Address Expansion' stage not found in Enhanced_Funnel_Analysis.")

except Exception as e:
    print(f"❌ Error during Address Expansion analysis: {e}")

print("\n--- Script 4 Finished ---")