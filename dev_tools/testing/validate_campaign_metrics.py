

import pandas as pd
import numpy as np

def validate_metrics(excel_path):
    """
    Validates the metrics in a completed campaign Excel file.
    """
    print(f"--- Starting Metrics Validation for: {excel_path} ---\n")

    try:
        # Load all relevant sheets
        xls = pd.ExcelFile(excel_path)
        df_funnel = pd.read_excel(xls, 'Enhanced_Funnel_Analysis')
        df_quality = pd.read_excel(xls, 'Address_Quality_Distribution')
        df_validation_ready = pd.read_excel(xls, 'All_Validation_Ready')
        df_summary = pd.read_excel(xls, 'Campaign_Summary')
        print("✅ Successfully loaded all required sheets.\n")
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        return

    # --- Validation Checks ---
    results = {}

    # 1. Quality Distribution Percentage Sum
    quality_perc_sum = df_quality['Percentage'].sum()
    results['Quality Percentage Sum == 100%'] = np.isclose(quality_perc_sum, 100.0)

    # 2. Quality Distribution Counts vs. Validation Ready Sheet
    total_quality_count = df_quality['Count'].sum()
    total_validation_ready_rows = len(df_validation_ready)
    results['Quality Counts Match Validation Sheet'] = (total_quality_count == total_validation_ready_rows)

    # 3. MEDIUM Address Metrics Correction Validation (v3.1.7)
    try:
        # Check Final_Mailing_List includes MEDIUM addresses
        df_final_mailing = pd.read_excel(xls, 'Final_Mailing_List')
        if 'Address_Confidence' in df_final_mailing.columns:
            final_mailing_mediums = len(df_final_mailing[df_final_mailing['Address_Confidence'] == 'MEDIUM'])
            validation_mediums = len(df_validation_ready[df_validation_ready['Address_Confidence'] == 'MEDIUM'])
            results['MEDIUM Addresses in Final_Mailing_List'] = (final_mailing_mediums == validation_mediums)
        
        # Check Direct_Mail_Final_Contacts includes MEDIUM addresses
        direct_mail_total = df_summary['Direct_Mail_Final_Contacts'].sum()
        ultra_high_count = len(df_validation_ready[df_validation_ready['Address_Confidence'] == 'ULTRA_HIGH'])
        high_count = len(df_validation_ready[df_validation_ready['Address_Confidence'] == 'HIGH'])
        medium_count = len(df_validation_ready[df_validation_ready['Address_Confidence'] == 'MEDIUM'])
        expected_direct_mail = ultra_high_count + high_count + medium_count
        
        results['Direct_Mail_Final_Contacts includes MEDIUM'] = (direct_mail_total == expected_direct_mail)
        results['Direct_Mail_Final_Contacts Value'] = f"{direct_mail_total} (Expected: {expected_direct_mail})"
        
    except Exception as e:
        results['MEDIUM Address Validation'] = f"Error: {e}"

    # 4. Funnel: Owner Discovery Multiplier
    try:
        land_funnel = df_funnel[df_funnel['Funnel_Type'] == 'Land Acquisition']
        contact_funnel = df_funnel[df_funnel['Funnel_Type'] == 'Contact Processing']
        
        qualified_parcels = land_funnel[land_funnel['Stage'] == '4. Parcels w/ Residential Buildings']['Count'].iloc[0]
        discovered_owners = contact_funnel[contact_funnel['Stage'] == '1. Owner Discovery']['Count'].iloc[0]
        owner_multiplier = contact_funnel[contact_funnel['Stage'] == '1. Owner Discovery']['Conversion / Multiplier'].iloc[0]
        
        calculated_multiplier = discovered_owners / qualified_parcels if qualified_parcels > 0 else 0
        results['Owner Discovery Multiplier Correct'] = np.isclose(owner_multiplier, calculated_multiplier, atol=0.01)
        results['Owner Discovery Value'] = f"{owner_multiplier:.2f}x"

    except IndexError:
        results['Owner Discovery Multiplier Correct'] = "Error: Could not find required stage in funnel."

    # 4. Funnel: Address Expansion Multiplier
    try:
        address_pairs = contact_funnel[contact_funnel['Stage'] == '2. Address Expansion']['Count'].iloc[0]
        address_multiplier = contact_funnel[contact_funnel['Stage'] == '2. Address Expansion']['Conversion / Multiplier'].iloc[0]
        discovered_owners = contact_funnel[contact_funnel['Stage'] == '1. Owner Discovery']['Count'].iloc[0]

        calculated_addr_multiplier = address_pairs / discovered_owners if discovered_owners > 0 else 0
        results['Address Expansion Multiplier Correct'] = np.isclose(address_multiplier, calculated_addr_multiplier, atol=0.01)
        results['Address Expansion Value'] = f"{address_multiplier:.2f}x"
    except IndexError:
        results['Address Expansion Multiplier Correct'] = "Error: Could not find required stage in funnel."

    # 5. Summary vs. Detailed Sheets
    summary_direct_mail = df_summary['Direct_Mail_Final_Contacts'].sum()
    validation_direct_mail = len(df_validation_ready[df_validation_ready['Routing_Channel'] == 'DIRECT_MAIL'])
    results['Summary Direct Mail Matches Detail'] = (summary_direct_mail == validation_direct_mail)

    # --- Print Results ---
    print("📊 METRICS VALIDATION RESULTS:")
    print("="*40)
    for key, value in results.items():
        status = "✅ PASSED" if value is True else ("❌ FAILED" if value is False else f"ℹ️ INFO")
        print(f"{key:<40} | {status:<10} | Value: {value}")
    print("="*40)
    print("\n--- Validation script finished ---")

if __name__ == "__main__":
    # Path to the real-world campaign results file
    campaign_file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213_Results.xlsx"
    validate_metrics(campaign_file_path)
