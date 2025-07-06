import pandas as pd

excel_file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213_Results.xlsx"

print(f"--- Listing All Metrics from Key Sheets ---")

try:
    xls = pd.ExcelFile(excel_file_path)

    df_funnel_analysis = pd.read_excel(xls, 'Enhanced_Funnel_Analysis')
    df_summary = pd.read_excel(xls, 'Campaign_Summary')

    print("\n✅ Successfully loaded Enhanced_Funnel_Analysis and Campaign_Summary sheets.\n")

    print("--- Metrics in Enhanced_Funnel_Analysis ---")
    print("Columns:", df_funnel_analysis.columns.tolist())
    print("\nSample Data (first 10 rows):\n", df_funnel_analysis.head(10).to_string())

    print("\n--- Metrics in Campaign_Summary ---")
    print("Columns:", df_summary.columns.tolist())
    print("\nSample Data (first 5 rows):\n", df_summary.head().to_string())

except Exception as e:
    print(f"❌ Error loading data: {e}")

print("\n--- Script 6 Finished ---")
