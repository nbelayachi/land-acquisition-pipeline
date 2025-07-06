import pandas as pd

excel_file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250704_1622\LandAcquisition_Casalpusterlengo_Castiglione_20250704_1622_Results.xlsx"

print(f"--- Verifying Final_Mailing_List Content (Option B Implementation) ---")

try:
    xls = pd.ExcelFile(excel_file_path)
    df_validation_ready = pd.read_excel(xls, 'All_Validation_Ready')
    df_final_mailing_list = pd.read_excel(xls, 'Final_Mailing_List')
    
    print("✅ Successfully loaded All_Validation_Ready and Final_Mailing_List sheets.\n")

    # 1. Count addresses by confidence level in All_Validation_Ready
    confidence_counts = df_validation_ready['Address_Confidence'].value_counts()
    
    ultra_high_count = confidence_counts.get('ULTRA_HIGH', 0)
    high_count = confidence_counts.get('HIGH', 0)
    medium_count = confidence_counts.get('MEDIUM', 0)
    low_count = confidence_counts.get('LOW', 0)

    print("--- Counts from All_Validation_Ready ---")
    print(f"ULTRA_HIGH: {ultra_high_count}")
    print(f"HIGH:       {high_count}")
    print(f"MEDIUM:     {medium_count}")
    print(f"LOW:        {low_count}\n")

    # 2. Count total addresses in Final_Mailing_List
    total_in_final_mailing_list = len(df_final_mailing_list)
    print(f"Total addresses in Final_Mailing_List: {total_in_final_mailing_list}\n")

    # 3. Expected count in Final_Mailing_List (ULTRA_HIGH + HIGH + MEDIUM)
    expected_total_in_final_mailing_list = ultra_high_count + high_count + medium_count
    
    print("--- Verification ---")
    if total_in_final_mailing_list == expected_total_in_final_mailing_list:
        print(f"✅ SUCCESS: Final_Mailing_List count ({total_in_final_mailing_list}) matches expected count ({expected_total_in_final_mailing_list}).")
        print("  This confirms all ULTRA_HIGH, HIGH, and MEDIUM addresses are included.")
    else:
        print(f"❌ FAILURE: Final_Mailing_List count ({total_in_final_mailing_list}) does NOT match expected count ({expected_total_in_final_mailing_list}).")
        print("  Review the filtering logic.")

    # 4. Check for LOW confidence addresses in Final_Mailing_List (should not be there)
    low_in_final_mailing_list = df_final_mailing_list[
        df_final_mailing_list['Address_Confidence'] == 'LOW'
    ]
    
    if low_in_final_mailing_list.empty:
        print("✅ SUCCESS: No LOW confidence addresses found in Final_Mailing_List (as expected).")
    else:
        print(f"❌ FAILURE: {len(low_in_final_mailing_list)} LOW confidence addresses found in Final_Mailing_List (unexpected!).")
        print("  Review the filtering logic.")

except Exception as e:
    print(f"❌ Error during verification: {e}")

print("\n--- Script Finished ---")
