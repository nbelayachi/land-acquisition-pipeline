import pandas as pd

excel_file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213_Results.xlsx"

print(f"--- Loading data from: {excel_file_path} ---")

try:
    xls = pd.ExcelFile(excel_file_path)

    df_raw_data = pd.read_excel(xls, 'All_Raw_Data')
    df_validation_ready = pd.read_excel(xls, 'All_Validation_Ready')
    df_funnel_analysis = pd.read_excel(xls, 'Enhanced_Funnel_Analysis')
    df_quality_distribution = pd.read_excel(xls, 'Address_Quality_Distribution')

    print("\n✅ Successfully loaded all required sheets.")

    print("\n--- Overview of All_Raw_Data ---")
    print(f"Shape: {df_raw_data.shape}")
    print(df_raw_data.head())

    print("\n--- Overview of All_Validation_Ready ---")
    print(f"Shape: {df_validation_ready.shape}")
    print(df_validation_ready.head())

    print("\n--- Overview of Enhanced_Funnel_Analysis ---")
    print(f"Shape: {df_funnel_analysis.shape}")
    print(df_funnel_analysis.head(10)) # Display more rows for funnel

    print("\n--- Overview of Address_Quality_Distribution ---")
    print(f"Shape: {df_quality_distribution.shape}")
    print(df_quality_distribution.head())

except Exception as e:
    print(f"❌ Error loading data: {e}")

print("\n--- Script 1 Finished ---")
