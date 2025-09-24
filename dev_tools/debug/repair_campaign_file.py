# -*- coding: utf-8 -*-
"""
repair_campaign_file.py

This final script reads a complete campaign results file, discards the faulty
geocoding, re-processes all addresses using the robust offline databases,
re-classifies them, and generates a final, perfected mailing list.
"""
import pandas as pd
import re
import os

def load_databases(comuni_file="comuni_database.csv", cap_file="cap_database.csv"):
    """Loads both the comuni and cap CSVs into pandas DataFrames."""
    if not os.path.exists(comuni_file) or not os.path.exists(cap_file):
        print(f"❌ ERROR: Make sure both '{comuni_file}' and '{cap_file}' are in the directory.")
        return None, None
    try:
        print("✅ Loading local databases...")
        comuni_df = pd.read_csv(comuni_file, dtype={'pro_com_t': str})
        cap_df = pd.read_csv(cap_file, dtype={'pro_com_t': str})
        print("✅ Databases loaded successfully.")
        return comuni_df, cap_df
    except Exception as e:
        print(f"❌ ERROR: Could not load the databases: {e}")
        return None, None

def parse_original_address(address):
    """Parses the 'cleaned_ubicazione' format into its components."""
    if not isinstance(address, str): return None, None, None, None
    pattern_with_number = re.compile(r'^(.*?)\((.*?)\)\s+(.*?)\s+n\.\s*(\d+[/A-Z]*)', re.IGNORECASE)
    match = pattern_with_number.match(address)
    if match: return match.group(1).strip(), match.group(2).strip().upper(), match.group(3).strip(), match.group(4)
    pattern_without_number = re.compile(r'^(.*?)\((.*?)\)\s+(.*)', re.IGNORECASE)
    match = pattern_without_number.match(address)
    if match: return match.group(1).strip(), match.group(2).strip().upper(), match.group(3).strip(), None
    return None, None, None, None

def find_postal_code_with_join(municipality, province_code, comuni_df, cap_df):
    """Performs the two-step lookup with a lenient fallback."""
    if comuni_df is None or cap_df is None: return None, "Database not loaded"

    istat_col_name_in_comuni = 'pro_com_t'
    istat_col_name_in_caps = 'pro_com_t'
    province_col_name = 'sigla'

    match = comuni_df[(comuni_df['comune'].str.lower() == municipality.lower()) & (comuni_df[province_col_name].str.lower() == province_code.lower())]
    if match.empty:
        match = comuni_df[comuni_df['comune'].str.lower() == municipality.lower()]

    if match.empty: return None, "Municipality not found in database"
    
    istat_code = match[istat_col_name_in_comuni].iloc[0]
    cap_match = cap_df[cap_df[istat_col_name_in_caps] == istat_code]
    
    if not cap_match.empty:
        return cap_match['cap'].iloc[0], "SUCCESS: Found via ISTAT join"
    
    return None, "ISTAT code not found in CAP database"

def reclassify_address(status, original_address, final_address):
    """Applies new classification logic based on the offline lookup status."""
    if "SUCCESS" in status:
        return "ULTRA_HIGH", False, "DIRECT_MAIL", "Verified and complete address built from local database."
    elif "BUILT" in status:
        return "MEDIUM", True, "DIRECT_MAIL", "Address constructed, but postal code lookup failed; use with caution."
    elif "FAILED" in status:
        return "LOW", True, "AGENCY", "Could not parse original address."
    else: # Should not happen, but a safe default
        return "LOW", True, "AGENCY", "Unknown processing error."

def main():
    """Main execution function."""
    # --- CONFIGURE YOUR FILES HERE ---
    campaign_excel_file = "LandAcquisition_Agrate_Brianza_20250830_1552_Results.xlsx" # <--- REPLACE with your main results Excel file name
    sheet_to_process = "All_Validation_Ready"     # <--- REPLACE with the sheet name you want to process
    output_file = "Campaign_Repaired_Results.xlsx"
    # --------------------------------

    comuni_db, cap_db = load_databases()
    if comuni_db is None: return

    try:
        df_input = pd.read_excel(campaign_excel_file, sheet_name=sheet_to_process)
        print(f"📄 Processing {len(df_input)} records from '{campaign_excel_file}' (Sheet: '{sheet_to_process}')...")
    except FileNotFoundError:
        print(f"❌ ERROR: Input file '{campaign_excel_file}' not found.")
        return
    except Exception as e:
        print(f"❌ ERROR: Could not read the sheet '{sheet_to_process}' from the Excel file: {e}")
        return

    repaired_data = []
    for index, row in df_input.iterrows():
        # Copy all original data to preserve it
        new_row = row.to_dict()
        original_address = row.get('cleaned_ubicazione')

        municipality, province, street, number = parse_original_address(original_address)
        
        final_address, status = "", ""
        if street:
            postal_code, lookup_status = find_postal_code_with_join(municipality, province, comuni_db, cap_db)
            street_part = f"{street.title()} {number}" if number else street.title()
            municipality_part = f"{municipality.title()} {province}"
            if postal_code:
                postal_code_str = str(int(postal_code)).zfill(5)
                final_address = f"{street_part}, {postal_code_str} {municipality_part}"
                status = lookup_status
            else:
                final_address = f"{street_part}, {municipality_part}"
                status = f"BUILT: {lookup_status}"
        else:
            final_address = original_address
            status = "FAILED: Could not parse original address"
        
        # Re-classify based on the new, reliable result
        confidence, risk, channel, notes = reclassify_address(status, original_address, final_address)

        # Update the row with new, corrected data
        new_row['Final_Mailing_Address'] = final_address
        new_row['Address_Confidence'] = confidence
        new_row['Interpolation_Risk'] = risk
        new_row['Routing_Channel'] = channel
        new_row['Quality_Notes'] = notes
        
        repaired_data.append(new_row)

    # Create the final DataFrames
    df_repaired = pd.DataFrame(repaired_data)
    
    # Create the clean mailing list
    mailing_list_columns = ['Final_Mailing_Address', 'cognome', 'nome', 'foglio_input', 'particella_input']
    # Ensure columns exist before selecting
    final_mailing_list_cols = [col for col in mailing_list_columns if col in df_repaired.columns]
    df_mailing_list = df_repaired[df_repaired['Routing_Channel'] == 'DIRECT_MAIL'][final_mailing_list_cols]

    # Save to a new Excel file with two sheets
    with pd.ExcelWriter(output_file) as writer:
        df_repaired.to_excel(writer, sheet_name='Validation_Ready_Repaired', index=False)
        df_mailing_list.to_excel(writer, sheet_name='Final_Mailing_List', index=False)

    print(f"\n✅✅✅ Success! Your campaign file has been repaired and saved to '{output_file}'.")
    print("It contains two sheets: 'Validation_Ready_Repaired' and the actionable 'Final_Mailing_List'.")


if __name__ == "__main__":
    main()