# -*- coding: utf-8 -*-
"""
Final, definitive script to create a perfected mailing list.
VERSION 13: Implements a lenient fallback search to handle outdated province codes.
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
    """
    Performs a two-step lookup with a lenient fallback for the municipality search.
    """
    if comuni_df is None or cap_df is None: return None, "Database not loaded"

    province_col_name = 'sigla'
    istat_col_name = 'pro_com_t'

    # --- Step 1: Find the ISTAT code ---
    
    # Primary Search (Strict): Match municipality AND province
    municipality_match = comuni_df[
        (comuni_df['comune'].str.lower() == municipality.lower()) &
        (comuni_df[province_col_name].str.lower() == province_code.lower())
    ]
    
    # Fallback Search (Lenient): If strict search fails, match municipality only
    if municipality_match.empty:
        print(f"      -> Strict search failed. Trying lenient search for '{municipality}'...")
        municipality_match = comuni_df[comuni_df['comune'].str.lower() == municipality.lower()]

    if municipality_match.empty:
        return None, "Municipality not found in database"
        
    istat_code = municipality_match[istat_col_name].iloc[0]
    
    # --- Step 2: Use the ISTAT code to look up the postal code ---
    cap_match = cap_df[cap_df[istat_col_name] == istat_code]
    
    if not cap_match.empty:
        postal_code = cap_match['cap'].iloc[0]
        return postal_code, "SUCCESS: Found via ISTAT join"
        
    return None, "ISTAT code not found in CAP database"

def main():
    """Main execution function."""
    input_file = "re_geocoded_results.csv" 
    output_file = "final_mailing_list_offline.csv"

    comuni_database, cap_database = load_databases()
    if comuni_database is None or cap_database is None: return

    df_input = pd.read_csv(input_file).rename(columns={'cleaned_ubicazione': 'Original_Address'})
    print(f"📄 Processing {len(df_input)} records from '{input_file}'...")

    final_addresses = []
    for index, row in df_input.iterrows():
        original_address = row['Original_Address']
        
        municipality, province, street, number = parse_original_address(original_address)
        
        final_address, status = "", ""
        
        if street:
            postal_code, lookup_status = find_postal_code_with_join(municipality, province, comuni_database, cap_database)
            
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
            
        final_addresses.append({
            'Original_Address': original_address,
            'Final_Mailing_Address': final_address,
            'Processing_Status': status
        })

    final_df = pd.DataFrame(final_addresses)
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ Success! The final offline-built mailing list has been saved to '{output_file}'.")

if __name__ == "__main__":
    main()