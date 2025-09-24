# -*- coding: utf-8 -*-
"""
This script constructs a final, usable mailing list with a consistent format.
- It injects missing street numbers into partially successful geocoded results.
- For failed geocoding results, it parses the original address and
  constructs a new one in the proper mailing format.
"""
import pandas as pd
import re
import os

def parse_original_address(address):
    """
    Parses the 'cleaned_ubicazione' format into its components.
    Example: "AGRATE BRIANZA(MI) VIA MONTE GRAPPA n. 17"
    """
    if not isinstance(address, str):
        return None, None, None, None

    # Regex to capture Municipality, Province, Street, and Number
    pattern_with_number = re.compile(r'^(.*?)\((.*?)\)\s+(.*?)\s+n\.\s*(\d+[/A-Z]*)', re.IGNORECASE)
    match = pattern_with_number.match(address)

    if match:
        municipality = match.group(1).strip().title()
        province = match.group(2).strip().upper()
        street = match.group(3).strip().title()
        number = match.group(4)
        return municipality, province, street, number

    # Fallback pattern for addresses without a number
    pattern_without_number = re.compile(r'^(.*?)\((.*?)\)\s+(.*)', re.IGNORECASE)
    match = pattern_without_number.match(address)
    if match:
        municipality = match.group(1).strip().title()
        province = match.group(2).strip().upper()
        street = match.group(3).strip().title()
        return municipality, province, street, None
        
    return None, None, None, None

def inject_number_into_geocoded(geocoded_address, number_to_inject):
    """Inserts a street number into a geocoded address string."""
    if not isinstance(geocoded_address, str) or not number_to_inject:
        return geocoded_address

    parts = geocoded_address.split(',')
    if len(parts) > 1:
        parts[0] = f"{parts[0].strip()} {number_to_inject}"
        return ", ".join(parts).strip()
    else:
        return f"{geocoded_address.strip()} {number_to_inject}"

def main():
    """Main execution function."""
    input_file = "re_geocoded_results.csv"
    output_file = "final_mailing_list_constructed.csv"

    if not os.path.exists(input_file):
        print(f"❌ ERROR: Input file '{input_file}' not found.")
        return

    df = pd.read_csv(input_file)
    print(f"📄 Processing {len(df)} records from '{input_file}'...")

    final_addresses = []
    for index, row in df.iterrows():
        original_address = row['cleaned_ubicazione']
        new_geocoded = row['New_Geocoded_Address']
        new_status = row['New_Geocoding_Status']
        
        final_address = ''
        fix_applied = ''

        # Case 1: Geocoding was successful but may be missing a number.
        if new_status == 'SUCCESS' and isinstance(new_geocoded, str):
            number = parse_original_address(original_address)[3] # Extract number from original
            if number:
                final_address = inject_number_into_geocoded(new_geocoded, number)
                fix_applied = 'SUCCESS: Injected number from original address'
            else:
                final_address = new_geocoded
                fix_applied = 'SUCCESS: No fix needed'
        
        # Case 2: Geocoding failed. We must construct the address manually.
        else:
            municipality, province, street, number = parse_original_address(original_address)
            if street:
                # Reconstruct the address in the desired format
                street_part = f"{street} {number}" if number else street
                # Format: "Street Name Number, Municipality Province"
                final_address = f"{street_part}, {municipality} {province}"
                fix_applied = 'CONSTRUCTED: Geocoding failed, built from original'
            else:
                # If parsing fails, use original as last resort
                final_address = original_address
                fix_applied = 'FAILED: Could not parse original address'


        final_addresses.append({
            'Original_Address': original_address,
            'Final_Mailing_Address': final_address,
            'Processing_Status': fix_applied
        })
    
    final_df = pd.DataFrame(final_addresses)
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Success! A constructed mailing list has been saved to '{output_file}'.")
    print("This file contains an address in the correct mailing format for every entry.")

if __name__ == "__main__":
    main()