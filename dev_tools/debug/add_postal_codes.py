# -*- coding: utf-8 -*-
"""
Final, definitive script to create a perfected mailing list.
VERSION 9: Implements a primary/fallback search to handle API data inconsistencies.
"""
import pandas as pd
import requests
import json
import time
import os
import re
import urllib.parse

def load_cap_api_token(config_file="land_acquisition_config.json"):
    """Loads the CAP (zip code) API token from the configuration file."""
    if not os.path.exists(config_file):
        print(f"❌ ERROR: Configuration file '{config_file}' not found.")
        return None
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        if 'land_acquisition_config' in config:
            config = config['land_acquisition_config']
        token = config.get("cap_api_settings", {}).get("token")
        if not token or "YOUR" in token:
            print(f"❌ ERROR: CAP API token not found in 'cap_api_settings'.")
            return None
        print("✅ Zip Code (CAP) API token loaded successfully.")
        return token
    except Exception as e:
        print(f"❌ ERROR: Could not read config file: {e}")
        return None

def _perform_istat_lookup(search_term, province_code, token):
    """Internal function to perform a single ISTAT lookup."""
    try:
        query = urllib.parse.quote(search_term)
        url = f"https://cap.openapi.it/cerca_comuni?comune={query}"
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"      -> Calling ISTAT API for '{search_term}'...")
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None # Fail silently on HTTP error to allow fallback

        data = response.json()
        if not data.get('success') or not isinstance(data.get('data'), list) or not data.get('data'):
            return None # Fail silently on no data to allow fallback

        for result in data['data']:
            if result.get('sigla_provincia') == province_code:
                print(f"      -> Found match in province {province_code}: {result.get('comune')}")
                return result.get('istat')
        return None
    except Exception:
        return None

def get_istat_code(municipality, province_code, token):
    """
    Tries a primary search with the full name, then a fallback with the first word.
    """
    # 1. Primary Search (Full Name)
    formatted_municipality = municipality.title()
    istat_code = _perform_istat_lookup(formatted_municipality, province_code, token)
    if istat_code:
        return istat_code

    # 2. Fallback Search (First Word), only if primary fails and there are multiple words
    name_parts = municipality.split()
    if len(name_parts) > 1:
        print(f"      -> Primary search failed. Trying fallback for '{name_parts[0]}'.")
        fallback_municipality = name_parts[0].title()
        istat_code = _perform_istat_lookup(fallback_municipality, province_code, token)
        if istat_code:
            return istat_code
            
    return None

def get_postal_code_from_istat(istat_code, token):
    """Uses the 'comuni_advance' endpoint to get postal codes from an ISTAT code."""
    if not istat_code: return None
    try:
        url = f"https://cap.openapi.it/comuni_advance/{istat_code}"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data', {}).get('cap'):
                return data['data']['cap'][0]
    except Exception:
        return None
    return None

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

def inject_number_into_geocoded(geocoded_address, number_to_inject):
    """Inserts a street number into a geocoded address string."""
    if not isinstance(geocoded_address, str) or not number_to_inject: return geocoded_address
    parts = geocoded_address.split(',')
    if len(parts) > 1:
        parts[0] = f"{parts[0].strip()} {number_to_inject}"
        return ", ".join(parts).strip()
    else:
        return f"{geocoded_address.strip()} {number_to_inject}"

def main():
    """Main execution function."""
    input_file = "re_geocoded_results.csv"
    output_file = "final_mailing_list_with_postal_codes.csv"

    token = load_cap_api_token()
    if not token: return

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
        
        print(f"\nProcessing ({index + 1}/{len(df)}): {original_address}")
        
        final_address, fix_applied = '', ''

        if new_status == 'SUCCESS' and isinstance(new_geocoded, str):
            number = parse_original_address(original_address)[3]
            if number:
                final_address = inject_number_into_geocoded(new_geocoded, number)
                fix_applied = 'SUCCESS: Injected number from original'
            else:
                final_address = new_geocoded
                fix_applied = 'SUCCESS: No fix needed'
        else:
            municipality, province, street, number = parse_original_address(original_address)
            if street:
                istat_code = get_istat_code(municipality, province, token)
                time.sleep(1)
                
                postal_code = None
                if istat_code:
                    print(f"      -> Found ISTAT code: {istat_code}. Looking up postal code...")
                    postal_code = get_postal_code_from_istat(istat_code, token)
                    time.sleep(1)
                
                street_part = f"{street.title()} {number}" if number else street.title()
                municipality_part = f"{municipality.title()} {province}"
                
                if postal_code:
                    final_address = f"{street_part}, {postal_code} {municipality_part}"
                    fix_applied = 'CONSTRUCTED: Added postal code via multi-step lookup'
                else:
                    print("      -> Multi-step lookup failed to find a postal code.")
                    final_address = f"{street_part}, {municipality_part}"
                    fix_applied = 'CONSTRUCTED: Postal code lookup failed'
            else:
                final_address = original_address
                fix_applied = 'FAILED: Could not parse original address'

        print(f"  └──> Result: '{final_address}' [{fix_applied}]")

        final_addresses.append({
            'Original_Address': original_address,
            'Final_Mailing_Address': final_address,
            'Processing_Status': fix_applied
        })
    
    final_df = pd.DataFrame(final_addresses)
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Success! The final, perfected mailing list has been saved to '{output_file}'.")

if __name__ == "__main__":
    main()