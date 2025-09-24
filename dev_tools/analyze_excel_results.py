
import pandas as pd

excel_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Carpenedolo_20250709_1141\LandAcquisition_Carpenedolo_20250709_1141_Results.xlsx"

try:
    xls = pd.ExcelFile(excel_path)
    sheet_names = xls.sheet_names
    print(f"Sheets found: {sheet_names}\n")

    for sheet_name in sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        print(f"--- Sheet: {sheet_name} ---")
        print(df.head().to_string())
        print("\n")

except FileNotFoundError:
    print(f"Error: The file was not found at {excel_path}")
except Exception as e:
    print(f"An error occurred: {e}")

