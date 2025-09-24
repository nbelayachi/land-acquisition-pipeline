# -*- coding: utf-8 -*-
"""
Standalone script to re-geocode a list of addresses to check for API inconsistencies.
It reads an Excel file, processes the 'cleaned_ubicazione' column, and saves new results.
VERSION 3: Added a sample_size limit for quick testing.
"""

import pandas as pd
import requests
import json
import time
import os
import re

def load_geocoding_token(config_file="land_acquisition_config.json"):
    """Loads the geocoding token from the configuration file."""
    if not os.path.exists(config_file):
        print(f"❌ ERROR: Configuration file '{config_file}' not found.")
        print("Please ensure it is in the same directory and contains your geocoding token.")
        return None

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        if 'land_acquisition_config' in config:
            config = config['land_acquisition_config']

        token = config.get("geocoding_settings", {}).get("token")
        if not token or token == "YOUR_GEOCODING_TOKEN_HERE":
            print("❌ ERROR: Geocoding token not found or is set to the default value in the config file.")
            return None
        
        print("✅ Geocoding token loaded successfully.")
        return token
    except Exception as e:
        print(f"❌ ERROR: Could not read or parse the configuration file: {e}")
        return None

def geocode_address(address, token):
    """
    Calls the geocoding API for a single address and returns the result.
    """
    if not address or pd.isna(address):
        return "EMPTY_ADDRESS", None, None

    url = "https://geocoding.openapi.it/geocode"
    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {"address": str(address)}

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            return f"API_ERROR_{response.status_code}", None, None

        data = response.json()

        if data.get('success') and data.get('element'):
            element = data['element']
            geocoded_address = element.get('formattedAddress', '')
            street_number = element.get('streetNumber', '')
            return "SUCCESS", geocoded_address, street_number
        else:
            return "NO_DIRECT_RESULT", str(data), None

    except Exception as e:
        return f"REQUEST_EXCEPTION", str(e), None

def main():
    """Main execution function."""
    # --- NEW: Set a limit for the number of addresses to process ---
    sample_size = 30 
    
    input_file = "camp5_troubleshooting.xlsx"
    output_file = "re_geocoded_results.csv"
    
    token = load_geocoding_token()
    if not token:
        return

    if not os.path.exists(input_file):
        print(f"❌ ERROR: Input file '{input_file}' not found.")
        return
    
    try:
        df = pd.read_excel(input_file)
        # Limit the DataFrame to the sample size
        df_sample = df.head(sample_size)
        print(f"📄 Found {len(df)} addresses, will process a sample of {len(df_sample)}.")
    except Exception as e:
        print(f"❌ ERROR: Could not read the Excel file. You may need to install the 'openpyxl' library.")
        print("--> Try running: pip install openpyxl")
        print(f"--> Error details: {e}")
        return

    results = []
    # --- MODIFIED: Loop over the smaller sample DataFrame ---
    for index, row in df_sample.iterrows():
        original_address = row.get('cleaned_ubicazione')
        print(f"Processing ({index + 1}/{len(df_sample)}): {original_address}")
        
        status, new_geocoded_address, new_street_number = geocode_address(original_address, token)
        
        results.append({
            'cleaned_ubicazione': original_address,
            'Old_Geocoded_Address': row.get('Geocoded_Address_Italian'),
            'New_Geocoding_Status': status,
            'New_Geocoded_Address': new_geocoded_address,
            'New_Street_Number': new_street_number
        })
        
        time.sleep(2)

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n🎉 Done! The new results for the first {sample_size} addresses have been saved to '{output_file}'.")

if __name__ == "__main__":
    main()