import pandas as pd
import numpy as np

excel_file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213_Results.xlsx"

print(f"--- Validating Contact Processing Funnel Metrics ---")

try:
    xls = pd.ExcelFile(excel_file_path)
    df_raw_data = pd.read_excel(xls, 'All_Raw_Data')
    df_validation_ready = pd.read_excel(xls, 'All_Validation_Ready')
    df_funnel_analysis = pd.read_excel(xls, 'Enhanced_Funnel_Analysis')
    
    print("\n✅ Successfully loaded All_Raw_Data, All_Validation_Ready, and Enhanced_Funnel_Analysis sheets.\n")

    contact_funnel = df_funnel_analysis[df_funnel_analysis['Funnel_Type'] == 'Contact Processing']
    land_funnel = df_funnel_analysis[df_funnel_analysis['Funnel_Type'] == 'Land Acquisition']

    # Get the count and hectares from the last stage of Land Acquisition Funnel for calculations
    qualified_parcels_count = land_funnel[land_funnel['Stage'] == '4. Parcels w/ Residential Buildings']['Count'].iloc[0]
    qualified_parcels_hectares = land_funnel[land_funnel['Stage'] == '4. Parcels w/ Residential Buildings']['Hectares'].iloc[0]

    # --- Stage 1: Owner Discovery ---
    print("\n--- Stage 1: Owner Discovery ---")
    stage_name = '1. Owner Discovery'
    owner_discovery_row = contact_funnel[contact_funnel['Stage'] == stage_name].iloc[0]

    # Business Rationale
    print("Business Rationale: This metric quantifies the number of unique private owners identified on parcels that passed the residential building filter. It highlights the pipeline's ability to find multiple owners for a single parcel, which is common in Italy.")

    # Validation
    # Replicate the logic for unique owners on Cat.A parcels
    individuals_cat_a_filtered = df_raw_data[
        (df_raw_data['Tipo_Proprietario'] == 'Privato') &
        (df_raw_data['classamento'].str.contains('Cat.A', na=False, case=False))
    ]
    calculated_count = individuals_cat_a_filtered['cf'].nunique()
    calculated_hectares = qualified_parcels_hectares # Hectares should be the same as the previous funnel stage

    print(f"Metric: {stage_name} Count")
    print(f"  Calculated: {calculated_count}, Funnel: {owner_discovery_row['Count']}")
    if calculated_count == owner_discovery_row['Count']:
        print("  ✅ Count matches.")
    else:
        print("  ❌ Count mismatch.")

    print(f"Metric: {stage_name} Hectares")
    print(f"  Calculated: {calculated_hectares:.1f}, Funnel: {owner_discovery_row['Hectares']:.1f}")
    if np.isclose(calculated_hectares, owner_discovery_row['Hectares'], atol=0.1):
        print("  ✅ Hectares match.")
    else:
        print("  ❌ Hectares mismatch.")

    # Conversion / Multiplier
    conversion_multiplier = (calculated_count / qualified_parcels_count) if qualified_parcels_count > 0 else 0
    print(f"Metric: {stage_name} Conversion / Multiplier")
    print(f"  Calculated: {conversion_multiplier:.2f}, Funnel: {owner_discovery_row['Conversion / Multiplier']:.2f}")
    if np.isclose(conversion_multiplier, owner_discovery_row['Conversion / Multiplier'], atol=0.01):
        print("  ✅ Conversion / Multiplier matches.")
    else:
        print("  ❌ Conversion / Multiplier mismatch.")

    # Retention Rate
    # Retention rate for this stage is always 100% as it's the start of a new funnel type
    print(f"Metric: {stage_name} Retention_Rate")
    print(f"  Calculated: 100.0, Funnel: {owner_discovery_row['Retention_Rate']:.1f}")
    if np.isclose(100.0, owner_discovery_row['Retention_Rate'], atol=0.1):
        print("  ✅ Retention_Rate matches.")
    else:
        print("  ❌ Retention_Rate mismatch.")

    # --- Stage 2: Address Expansion ---
    print("\n--- Stage 2: Address Expansion ---")
    stage_name = '2. Address Expansion'
    address_expansion_row = contact_funnel[contact_funnel['Stage'] == stage_name].iloc[0]

    # Business Rationale
    print("Business Rationale: This metric shows the total number of unique owner-address pairs generated. It highlights the pipeline's ability to find all known residential addresses for each identified owner, maximizing potential contact points.")

    # Validation
    calculated_count = len(df_validation_ready) # Each row in validation_ready is a unique owner-address pair
    calculated_hectares = qualified_parcels_hectares # Hectares should be the same as the previous funnel stage

    print(f"Metric: {stage_name} Count")
    print(f"  Calculated: {calculated_count}, Funnel: {address_expansion_row['Count']}")
    if calculated_count == address_expansion_row['Count']:
        print("  ✅ Count matches.")
    else:
        print("  ❌ Count mismatch.")

    print(f"Metric: {stage_name} Hectares")
    print(f"  Calculated: {calculated_hectares:.1f}, Funnel: {address_expansion_row['Hectares']:.1f}")
    if np.isclose(calculated_hectares, address_expansion_row['Hectares'], atol=0.1):
        print("  ✅ Hectares match.")
    else:
        print("  ❌ Hectares mismatch.")

    # Conversion / Multiplier
    prev_stage_count = owner_discovery_row['Count']
    conversion_multiplier = (calculated_count / prev_stage_count) if prev_stage_count > 0 else 0
    print(f"Metric: {stage_name} Conversion / Multiplier")
    print(f"  Calculated: {conversion_multiplier:.2f}, Funnel: {address_expansion_row['Conversion / Multiplier']:.2f}")
    if np.isclose(conversion_multiplier, address_expansion_row['Conversion / Multiplier'], atol=0.01):
        print("  ✅ Conversion / Multiplier matches.")
    else:
        print("  ❌ Conversion / Multiplier mismatch.")

    # Retention Rate
    # Retention rate for this stage is calculated against the start of the Contact Processing funnel (Owner Discovery)
    retention_rate = (calculated_count / owner_discovery_row['Count'] * 100) if owner_discovery_row['Count'] > 0 else 0
    print(f"Metric: {stage_name} Retention_Rate")
    print(f"  Calculated: {retention_rate:.1f}, Funnel: {address_expansion_row['Retention_Rate']:.1f}")
    if np.isclose(retention_rate, address_expansion_row['Retention_Rate'], atol=0.1):
        print("  ✅ Retention_Rate matches.")
    else:
        print("  ❌ Retention_Rate mismatch.")

    # --- Stage 3: Address Validation & Enhancement ---
    print("\n--- Stage 3: Address Validation & Enhancement ---")
    stage_name = '3. Address Validation & Enhancement'
    address_validation_row = contact_funnel[contact_funnel['Stage'] == stage_name].iloc[0]

    # Business Rationale
    print("Business Rationale: This stage represents the process of geocoding and quality assessment for all collected addresses. It's a data enrichment step, ensuring addresses are validated and classified for optimal routing.")

    # Validation
    calculated_count = len(df_validation_ready) # All addresses are passed through this stage
    calculated_hectares = qualified_parcels_hectares # Hectares should be the same as the previous funnel stage

    print(f"Metric: {stage_name} Count")
    print(f"  Calculated: {calculated_count}, Funnel: {address_validation_row['Count']}")
    if calculated_count == address_validation_row['Count']:
        print("  ✅ Count matches.")
    else:
        print("  ❌ Count mismatch.")

    print(f"Metric: {stage_name} Hectares")
    print(f"  Calculated: {calculated_hectares:.1f}, Funnel: {address_validation_row['Hectares']:.1f}")
    if np.isclose(calculated_hectares, address_validation_row['Hectares'], atol=0.1):
        print("  ✅ Hectares match.")
    else:
        print("  ❌ Hectares mismatch.")

    # Conversion / Multiplier: Should be None as it's an enrichment step
    print(f"Metric: {stage_name} Conversion / Multiplier")
    print(f"  Funnel: {address_validation_row['Conversion / Multiplier']}")
    if pd.isna(address_validation_row['Conversion / Multiplier']):
        print("  ✅ Conversion / Multiplier is None (as expected for enrichment).")
    else:
        print("  ❌ Conversion / Multiplier is not None.")

    # Retention Rate
    retention_rate = (calculated_count / owner_discovery_row['Count'] * 100) if owner_discovery_row['Count'] > 0 else 0
    print(f"Metric: {stage_name} Retention_Rate")
    print(f"  Calculated: {retention_rate:.1f}, Funnel: {address_validation_row['Retention_Rate']:.1f}")
    if np.isclose(retention_rate, address_validation_row['Retention_Rate'], atol=0.1):
        print("  ✅ Retention_Rate matches.")
    else:
        print("  ❌ Retention_Rate mismatch.")

    # --- Stage 4: Direct Mail Ready ---
    print("\n--- Stage 4: Direct Mail Ready ---")
    stage_name = '4. Direct Mail Ready'
    direct_mail_row = contact_funnel[contact_funnel['Stage'] == stage_name].iloc[0]

    # Business Rationale
    print("Business Rationale: This metric represents the number of high-confidence addresses that are immediately ready for direct mail campaigns. These contacts require minimal to no manual review, optimizing efficiency and accelerating outreach.")

    # Validation
    calculated_count = len(df_validation_ready[df_validation_ready['Routing_Channel'] == 'DIRECT_MAIL'])
    # Hectares for Direct Mail Ready should be the sum of unique parcels associated with these direct mail contacts
    direct_mail_parcels_df = df_validation_ready[df_validation_ready['Routing_Channel'] == 'DIRECT_MAIL'][['foglio_input', 'particella_input', 'Area']].drop_duplicates()
    calculated_hectares = direct_mail_parcels_df['Area'].astype(str).str.replace(',', '.').astype(float).sum()

    print(f"Metric: {stage_name} Count")
    print(f"  Calculated: {calculated_count}, Funnel: {direct_mail_row['Count']}")
    if calculated_count == direct_mail_row['Count']:
        print("  ✅ Count matches.")
    else:
        print("  ❌ Count mismatch.")

    print(f"Metric: {stage_name} Hectares")
    print(f"  Calculated: {calculated_hectares:.1f}, Funnel: {direct_mail_row['Hectares']:.1f}")
    if np.isclose(calculated_hectares, direct_mail_row['Hectares'], atol=0.1):
        print("  ✅ Hectares match.")
    else:
        print("  ❌ Hectares mismatch.")

    # Conversion / Multiplier
    prev_stage_count = contact_funnel[contact_funnel['Stage'] == '3. Address Validation & Enhancement']['Count'].iloc[0]
    conversion_rate = (calculated_count / prev_stage_count * 100) if prev_stage_count > 0 else 0
    print(f"Metric: {stage_name} Conversion / Multiplier")
    print(f"  Calculated: {conversion_rate:.2f}, Funnel: {direct_mail_row['Conversion / Multiplier']:.2f}")
    if np.isclose(conversion_rate, direct_mail_row['Conversion / Multiplier'], atol=0.1):
        print("  ✅ Conversion / Multiplier matches.")
    else:
        print("  ❌ Conversion / Multiplier mismatch.")

    # Retention Rate
    retention_rate = (calculated_count / owner_discovery_row['Count'] * 100) if owner_discovery_row['Count'] > 0 else 0
    print(f"Metric: {stage_name} Retention_Rate")
    print(f"  Calculated: {retention_rate:.1f}, Funnel: {direct_mail_row['Retention_Rate']:.1f}")
    if np.isclose(retention_rate, direct_mail_row['Retention_Rate'], atol=0.1):
        print("  ✅ Retention_Rate matches.")
    else:
        print("  ❌ Retention_Rate mismatch.")

    # --- Stage 5: Agency Investigation Required ---
    print("\n--- Stage 5: Agency Investigation Required ---")
    stage_name = '5. Agency Investigation Required'
    agency_required_row = contact_funnel[contact_funnel['Stage'] == stage_name].iloc[0]

    # Business Rationale
    print("Business Rationale: This metric represents the number of lower-confidence addresses that require manual investigation by an external agency. While more costly, these contacts are still valuable and represent a necessary step to maximize landowner reach.")

    # Validation
    calculated_count = len(df_validation_ready[df_validation_ready['Routing_Channel'] == 'AGENCY'])
    # Hectares for Agency Required should be the sum of unique parcels associated with these agency contacts
    agency_parcels_df = df_validation_ready[df_validation_ready['Routing_Channel'] == 'AGENCY'][['foglio_input', 'particella_input', 'Area']].drop_duplicates()
    calculated_hectares = agency_parcels_df['Area'].astype(str).str.replace(',', '.').astype(float).sum()

    print(f"Metric: {stage_name} Count")
    print(f"  Calculated: {calculated_count}, Funnel: {agency_required_row['Count']}")
    if calculated_count == agency_required_row['Count']:
        print("  ✅ Count matches.")
    else:
        print("  ❌ Count mismatch.")

    print(f"Metric: {stage_name} Hectares")
    print(f"  Calculated: {calculated_hectares:.1f}, Funnel: {agency_required_row['Hectares']:.1f}")
    if np.isclose(calculated_hectares, agency_required_row['Hectares'], atol=0.1):
        print("  ✅ Hectares match.")
    else:
        print("  ❌ Hectares mismatch.")

    # Conversion / Multiplier
    prev_stage_count = contact_funnel[contact_funnel['Stage'] == '3. Address Validation & Enhancement']['Count'].iloc[0]
    conversion_rate = (calculated_count / prev_stage_count * 100) if prev_stage_count > 0 else 0
    print(f"Metric: {stage_name} Conversion / Multiplier")
    print(f"  Calculated: {conversion_rate:.2f}, Funnel: {agency_required_row['Conversion / Multiplier']:.2f}")
    if np.isclose(conversion_rate, agency_required_row['Conversion / Multiplier'], atol=0.1):
        print("  ✅ Conversion / Multiplier matches.")
    else:
        print("  ❌ Conversion / Multiplier mismatch.")

    # Retention Rate
    retention_rate = (calculated_count / owner_discovery_row['Count'] * 100) if owner_discovery_row['Count'] > 0 else 0
    print(f"Metric: {stage_name} Retention_Rate")
    print(f"  Calculated: {retention_rate:.1f}, Funnel: {agency_required_row['Retention_Rate']:.1f}")
    if np.isclose(retention_rate, agency_required_row['Retention_Rate'], atol=0.1):
        print("  ✅ Retention_Rate matches.")
    else:
        print("  ❌ Retention_Rate mismatch.")

except Exception as e:
    print(f"❌ Error during Contact Processing Funnel validation: {e}")

print("\n--- Script 8 Finished ---")
