# -*- coding: utf-8 -*-
"""
finalize_campaign_results.py

The definitive script to repair and classify a campaign results file.
VERSION 8 (Definitive): Fixes the bug where the mailing list used the wrong
address column and ensures the Municipality column is correct.
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
    pattern_with_number = re.compile(r'^(.*?)\((.*?)\)\s+(.*?)\s+n\.\s*(\S+)', re.IGNORECASE)
    match = pattern_with_number.match(address)
    if match: return match.group(1).strip(), match.group(2).strip().upper(), match.group(3).strip(), match.group(4)
    pattern_without_number = re.compile(r'^(.*?)\((.*?)\)\s+(.*)', re.IGNORECASE)
    match = pattern_without_number.match(address)
    if match: return match.group(1).strip(), match.group(2).strip().upper(), match.group(3).strip(), None
    return None, None, None, None

def get_address_archetype(cleaned_address):
    """Determines the structural type of an address."""
    address_lower = cleaned_address.lower()
    if re.search(r'\s+n\.\s*\d', address_lower): return "Complete Street Address"
    if ' n. sn' in address_lower or ' n. sc' in address_lower: return "Official Numberless"
    if 'cascina' in address_lower: return "Location-Based"
    street_types = [' via ', ' viale ', ' piazza ', ' corso ', ' vicolo ']
    if any(stype in address_lower for stype in street_types): return "Street without Number"
    return "Unparseable"

def find_postal_code_with_join(municipality, province_code, comuni_df, cap_df):
    """Performs the two-step lookup with a lenient fallback."""
    if comuni_df is None or cap_df is None: return None
    istat_col_name, province_col_name = 'pro_com_t', 'sigla'
    match = comuni_df[(comuni_df['comune'].str.lower() == municipality.lower()) & (comuni_df[province_col_name].str.lower() == province_code.lower())]
    if match.empty: match = comuni_df[comuni_df['comune'].str.lower() == municipality.lower()]
    if match.empty: return None
    istat_code = match[istat_col_name].iloc[0]
    cap_match = cap_df[cap_df[istat_col_name] == istat_code]
    if not cap_match.empty: return cap_match['cap'].iloc[0]
    return None

def reclassify_address(postal_code_found, archetype):
    """Applies the final, approved classification logic."""
    if postal_code_found:
        if archetype == "Complete Street Address": return "ULTRA_HIGH", "DIRECT_MAIL", "Fully verified address with number and postal code."
        elif archetype == "Official Numberless": return "HIGH", "DIRECT_MAIL", "Verified numberless (SN/SC) address."
        elif archetype == "Street without Number": return "MEDIUM", "AGENCY", "QC Action: Address needs a specific street number."
        elif archetype == "Location-Based": return "MEDIUM", "AGENCY", "QC Action: Address is a location, not a standard street."
        else: return "LOW", "AGENCY", "QC Action: Address is unparseable."
    else: # Postal code lookup failed
        if archetype == "Complete Street Address" or archetype == "Official Numberless": return "LOW", "AGENCY", "QC Action: Postal code lookup failed. Verify municipality."
        else: return "LOW", "AGENCY", "QC Action: Incomplete address AND postal code lookup failed."

def main():
    """Main execution function."""
    campaign_excel_file = "LandAcquisition_Agrate_Brianza_20250830_1552_Results.xlsx"
    sheet_to_process = "All_Validation_Ready"
    output_file = "Campaign_Final_Classified.xlsx"
    
    comuni_db, cap_db = load_databases()
    if comuni_db is None: return

    try:
        df_input = pd.read_excel(campaign_excel_file, sheet_name=sheet_to_process)
        print(f"📄 Processing {len(df_input)} records from '{campaign_excel_file}' (Sheet: '{sheet_to_process}')...")
    except FileNotFoundError:
        print(f"❌ ERROR: Input file '{campaign_excel_file}' not found.")
        return
    except Exception as e:
        print(f"❌ ERROR: Could not read the sheet '{sheet_to_process}': {e}")
        return

    final_data = []
    for index, row in df_input.iterrows():
        new_row = row.to_dict()
        original_address = row.get('cleaned_ubicazione')
        municipality, province, street, number = parse_original_address(original_address)
        
        final_address, postal_code = original_address, None
        if street:
            postal_code = find_postal_code_with_join(municipality, province, comuni_db, cap_db)
            street_part = f"{street.title()} {number}" if number else street.title()
            municipality_part = f"{municipality.title()} {province}"
            if postal_code:
                postal_code_str = str(int(postal_code)).zfill(5)
                final_address = f"{street_part}, {postal_code_str} {municipality_part}"
            else:
                final_address = f"{street_part}, {municipality_part}"
        
        archetype = get_address_archetype(original_address)
        confidence, channel, notes = reclassify_address(bool(postal_code), archetype)

        new_row['Final_Mailing_Address'] = final_address
        new_row['Address_Confidence'] = confidence
        new_row['Routing_Channel'] = channel
        new_row['Quality_Notes'] = notes
        # Carry forward the parsed municipality and province for the mailing address
        new_row['Mailing_Municipality'] = municipality
        new_row['Mailing_Province'] = province
        
        final_data.append(new_row)

    df_final = pd.DataFrame(final_data)
    
    # --- DEFINITIVE MAILING LIST LOGIC ---
    print("✅ Generating final mailing list with correct grouping and address format...")
    df_direct_mail = df_final[df_final['Routing_Channel'] == 'DIRECT_MAIL'].copy()
    
    df_direct_mail['Full_Name'] = df_direct_mail['cognome'].fillna('') + ' ' + df_direct_mail['nome'].fillna('')
    df_direct_mail['Full_Name'] = df_direct_mail['Full_Name'].str.strip()
    df_direct_mail['Parcel_Str'] = df_direct_mail['foglio_input'].astype(str) + '-' + df_direct_mail['particella_input'].astype(str)
    
    owner_parcels = df_direct_mail.groupby('cf').agg(
        Fogli=('foglio_input', lambda x: '; '.join(sorted(x.astype(str).unique()))),
        Particelle=('particella_input', lambda x: '; '.join(sorted(x.astype(str).unique()))),
        Parcels=('Parcel_Str', lambda x: '; '.join(sorted(x.unique())))
    ).reset_index()

    # DEFINITIVE FIX 1: Use the new 'Final_Mailing_Address' for grouping, along with its parsed components.
    owner_addresses = df_direct_mail[[
        'cf', 'Full_Name', 'Final_Mailing_Address', 'Mailing_Municipality', 'Mailing_Province'
    ]].drop_duplicates()

    df_merged = pd.merge(owner_addresses, owner_parcels, on='cf')
    
    # DEFINITIVE FIX 2: Create the Municipality column from the mailing address's components.
    df_merged['Municipality'] = df_merged['Mailing_Municipality'].str.title() + ' (' + df_merged['Mailing_Province'] + ')'
    
    df_merged['Addresses_Per_Owner'] = df_merged.groupby('cf')['Final_Mailing_Address'].transform('nunique')
    df_merged['Address_Sequence'] = df_merged.groupby('cf').cumcount() + 1
    
    # DEFINITIVE FIX 3: Rename the correct column for the final output.
    df_mailing_list = df_merged.rename(columns={'Final_Mailing_Address': 'Mailing_Address'})
    
    final_columns = [
        'Municipality', 'Fogli', 'Particelle', 'Parcels', 'Full_Name', 'cf',
        'Mailing_Address', 'Addresses_Per_Owner', 'Address_Sequence'
    ]
    df_mailing_list = df_mailing_list[final_columns]
    # --- End of Mailing List Logic ---

    with pd.ExcelWriter(output_file) as writer:
        df_final.to_excel(writer, sheet_name='QC_Review_List', index=False)
        df_mailing_list.to_excel(writer, sheet_name='Final_Mailing_List', index=False)

    print(f"\n✅✅✅ Success! Your campaign file has been finalized and saved to '{output_file}'.")

if __name__ == "__main__":
    main()