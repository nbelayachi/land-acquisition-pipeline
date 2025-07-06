import pandas as pd

excel_file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250704_0028\LandAcquisition_Casalpusterlengo_Castiglione_20250704_0028_Results.xlsx"

print(f"--- Examining MEDIUM Confidence Addresses in Validation_Ready ---")

try:
    xls = pd.ExcelFile(excel_file_path)
    df_validation_ready = pd.read_excel(xls, 'All_Validation_Ready')
    
    print("✅ Successfully loaded All_Validation_Ready sheet.\n")

    # Filter for MEDIUM confidence addresses
    df_medium_confidence = df_validation_ready[
        df_validation_ready['Address_Confidence'] == 'MEDIUM'
    ].copy() # Use .copy() to avoid SettingWithCopyWarning

    if df_medium_confidence.empty:
        print("No MEDIUM confidence addresses found in the Validation_Ready sheet.")
    else:
        print(f"Found {len(df_medium_confidence)} MEDIUM confidence addresses.\n")
        print("--- Details of MEDIUM Confidence Addresses ---")
        print("Note: 'Best_Address' being same as 'cleaned_ubicazione' indicates geocoded address was not useful.\n")
        
        # Display relevant columns
        display_cols = [
            'cleaned_ubicazione',
            'Geocoded_Address_Italian',
            'Best_Address',
            'Routing_Channel',
            'Quality_Notes',
            'Address_Confidence' # Keep this for context
        ]
        
        # Add a flag for easy identification of the problematic cases
        df_medium_confidence['Best_Address_Is_Original'] = \
            df_medium_confidence['Best_Address'] == df_medium_confidence['cleaned_ubicazione']

        print(df_medium_confidence[display_cols + ['Best_Address_Is_Original']].to_string())

except Exception as e:
    print(f"❌ Error during examination of MEDIUM confidence addresses: {e}")

print("\n--- Script Finished ---")