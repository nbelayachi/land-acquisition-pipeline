import pandas as pd

# Use the Windows path for one of the result files
file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250627_1236\Mun_001\Mun_001_Results.xlsx"

try:
    print(f"--- Reading columns from: {file_path} ---")

    # Read the Raw_Data sheet
    df_raw = pd.read_excel(file_path, sheet_name='Raw_Data')
    print("\n--- Columns in Raw_Data sheet ---")
    print(df_raw.columns.tolist())

    # Also check Validation_Ready sheet
    try:
        df_validation = pd.read_excel(file_path, sheet_name='Validation_Ready')
        print("\n--- Columns in Validation_Ready sheet ---")
        print(df_validation.columns.tolist())
    except Exception as e:
        print(f"\nCould not read Validation_Ready sheet: {e}")

except FileNotFoundError:
    print(f"ERROR: File not found at {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")
