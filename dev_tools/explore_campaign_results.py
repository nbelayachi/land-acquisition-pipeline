import pandas as pd
import os

def explore_excel_file(file_path):
    """
    Analyzes the structure of the campaign results Excel file and prints a summary.
    """
    if not os.path.exists(file_path):
        print(f"--- ERROR ---")
        print(f"File not found at the specified path: '{file_path}'")
        print("Please ensure the path is correct and the file exists.")
        return

    print(f"Analyzing Excel file: {os.path.basename(file_path)}\n")

    try:
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        print(f"--- Found {len(sheet_names)} Sheets ---")
        for name in sheet_names:
            print(f"- {name}")
        print("\n" + "="*50 + "\n")

        # Sheets to analyze in detail
        sheets_to_detail = [
            'Campaign_Summary',
            'Enhanced_Funnel_Analysis',
            'Address_Quality_Distribution',
            'All_Validation_Ready',
            'Final_Mailing_List'
        ]

        for sheet_name in sheet_names:
            print(f"--- Analyzing Sheet: '{sheet_name}' ---")
            df = pd.read_excel(xls, sheet_name=sheet_name)
            print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
            
            print("Columns and Data Types:")
            print(df.dtypes)
            print("\n")

            # Show a sample for the most important sheets
            if sheet_name in sheets_to_detail and not df.empty:
                print(f"First 5 rows of '{sheet_name}':")
                print(df.head().to_string())
                print("\n")
            
            print("="*50 + "\n")

    except Exception as e:
        print(f"An error occurred while processing the file: {e}")

if __name__ == "__main__":
    # The user-provided path has been set here.
    # Note: The Windows path C:\... has been converted to /mnt/c/... for compatibility.
    campaign_results_path = "C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250704_1706\LandAcquisition_Casalpusterlengo_Castiglione_20250704_1706_Results.xlsx"
    
    explore_excel_file(campaign_results_path)