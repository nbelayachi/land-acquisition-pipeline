import pandas as pd
import os

def analyze_municipality_results(file_path, mun_key):
    print(f"\n--- Analyzing {mun_key} Results: {file_path} ---")
    try:
        # --- Read Raw_Data sheet ---
        df_raw = pd.read_excel(file_path, sheet_name='Raw_Data')
        print(f"\n--- {mun_key} Raw_Data (Analysis Columns) ---")
        raw_columns_to_display = ['foglio_input', 'particella_input', 'Tipo_Proprietario', 'classamento', 'ubicazione']
        print(df_raw[raw_columns_to_display].to_markdown(index=False))

        # --- Read Validation_Ready sheet ---
        try:
            df_validation_ready = pd.read_excel(file_path, sheet_name='Validation_Ready')
            print(f"\n--- {mun_key} Validation_Ready (Analysis Columns) ---")
            validation_columns_to_display = ['foglio_input', 'particella_input', 'ubicazione', 'cleaned_ubicazione', 'Postal_Code', 'Address_Confidence', 'Quality_Notes', 'Interpolation_Risk']
            print(df_validation_ready[validation_columns_to_display].to_markdown(index=False))
        except ValueError:
            print(f"\n--- {mun_key} Validation_Ready Sheet Not Found ---")

        # --- Read Municipality_Summary sheet ---
        try:
            df_summary = pd.read_excel(file_path, sheet_name='Municipality_Summary')
            print(f"\n--- {mun_key} Municipality_Summary ---")
            print(df_summary.to_markdown(index=False))
        except ValueError:
            print(f"\n--- {mun_key} Municipality_Summary Sheet Not Found ---")

        # --- Read Funnel_Analysis sheet ---
        try:
            df_funnel = pd.read_excel(file_path, sheet_name='Funnel_Analysis')
            print(f"\n--- {mun_key} Funnel_Analysis ---")
            print(df_funnel.to_markdown(index=False))
        except ValueError:
            print(f"\n--- {mun_key} Funnel_Analysis Sheet Not Found ---")

    except Exception as e:
        print(f"Error reading or processing Excel file {file_path}: {e}")

# --- Script Start ---

# Use the path from the latest campaign run
base_campaign_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250630_1326"

print(f"Starting analysis for campaign: {base_campaign_path}")

# Iterate through all 5 municipality folders
for i in range(1, 6):
    mun_folder_name = f"Mun_{i:03d}"
    mun_folder_path = os.path.join(base_campaign_path, mun_folder_name)
    results_file_name = f"{mun_folder_name}_Results.xlsx"
    results_file_path = os.path.join(mun_folder_path, results_file_name)

    if os.path.exists(results_file_path):
        analyze_municipality_results(results_file_path, mun_folder_name)
    else:
        print(f"\n--- No results file found for {mun_folder_name} at {results_file_path} ---")

print("\n--- Analysis Complete ---")