
import pandas as pd
import sys

file_path = sys.argv[1]

try:
    # Read Raw_Data sheet
    df_raw = pd.read_excel(file_path, sheet_name='Raw_Data')
    print("--- Raw_Data (Head) ---")
    print(df_raw.head().to_markdown(index=False))
    print("\n--- Raw_Data (Relevant Columns) ---")
    print(df_raw[['foglio_input', 'particella_input', 'Tipo_Proprietario', 'classamento', 'cleaned_ubicazione', 'Geocoding_Status', 'Address_Confidence', 'Routing_Channel', 'Quality_Notes']].to_markdown(index=False))

    # Read Validation_Ready sheet
    df_validation_ready = pd.read_excel(file_path, sheet_name='Validation_Ready')
    print("\n--- Validation_Ready (Head) ---")
    print(df_validation_ready.head().to_markdown(index=False))
    print("\n--- Validation_Ready (Relevant Columns) ---")
    print(df_validation_ready[['foglio_input', 'particella_input', 'Tipo_Proprietario', 'classamento', 'cleaned_ubicazione', 'Geocoding_Status', 'Address_Confidence', 'Routing_Channel', 'Quality_Notes']].to_markdown(index=False))

except Exception as e:
    print(f"Error reading Excel file: {e}")
    sys.exit(1)

