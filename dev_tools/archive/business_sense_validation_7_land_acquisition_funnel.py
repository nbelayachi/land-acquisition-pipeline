import pandas as pd
import numpy as np

excel_file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213_Results.xlsx"

print(f"--- Validating Land Acquisition Funnel Metrics (Corrected) ---")

try:
    xls = pd.ExcelFile(excel_file_path)
    df_raw_data = pd.read_excel(xls, 'All_Raw_Data')
    df_funnel_analysis = pd.read_excel(xls, 'Enhanced_Funnel_Analysis')
    
    print("\n✅ Successfully loaded All_Raw_Data and Enhanced_Funnel_Analysis sheets.\n")

    land_funnel = df_funnel_analysis[df_funnel_analysis['Funnel_Type'] == 'Land Acquisition']

    # --- Stage 1: Input Parcels ---
    print("\n--- Stage 1: Input Parcels ---")
    stage_name = '1. Input Parcels'
    input_parcels_row = land_funnel[land_funnel['Stage'] == stage_name].iloc[0]

    # Business Rationale
    print("Business Rationale: This is the starting point of the campaign, representing the total number of parcels and associated land area initially selected by the Land Acquisition team for analysis.")

    # Validation
    # Correctly calculate unique parcels and their sum of areas from df_raw_data
    unique_input_parcels_df = df_raw_data[['foglio_input', 'particella_input', 'Area']].drop_duplicates()
    expected_count = unique_input_parcels_df.shape[0]
    expected_hectares = unique_input_parcels_df['Area'].astype(str).str.replace(',', '.').astype(float).sum()

    print(f"Metric: {stage_name} Count")
    print(f"  Calculated: {expected_count}, Funnel: {input_parcels_row['Count']}")
    if expected_count == input_parcels_row['Count']:
        print("  ✅ Count matches.")
    else:
        print("  ❌ Count mismatch.")

    print(f"Metric: {stage_name} Hectares")
    print(f"  Calculated: {expected_hectares:.1f}, Funnel: {input_parcels_row['Hectares']:.1f}")
    if np.isclose(expected_hectares, input_parcels_row['Hectares'], atol=0.1):
        print("  ✅ Hectares match.")
    else:
        print("  ❌ Hectares mismatch.")

    # --- Stage 2: Ownership Data Retrieved ---
    print("\n--- Stage 2: Ownership Data Retrieved ---")
    stage_name = '2. Ownership Data Retrieved'
    ownership_data_row = land_funnel[land_funnel['Stage'] == stage_name].iloc[0]

    # Business Rationale
    print("Business Rationale: This metric quantifies the success rate of retrieving ownership data from the Italian Land Registry API. It indicates how many of the input parcels yielded valid ownership information, which is crucial for proceeding with contact efforts.")

    # Validation: In the pipeline, this stage represents parcels for which API calls were successful.
    # Since df_raw_data contains records from successful API calls, the count and hectares should match the input.
    calculated_count = expected_count # Should be same as input parcels if all API calls were successful for these records
    calculated_hectares = expected_hectares # Should be same as input hectares

    print(f"Metric: {stage_name} Count")
    print(f"  Calculated: {calculated_count}, Funnel: {ownership_data_row['Count']}")
    if calculated_count == ownership_data_row['Count']:
        print("  ✅ Count matches.")
    else:
        print("  ❌ Count mismatch.")

    print(f"Metric: {stage_name} Hectares")
    print(f"  Calculated: {calculated_hectares:.1f}, Funnel: {ownership_data_row['Hectares']:.1f}")
    if np.isclose(calculated_hectares, ownership_data_row['Hectares'], atol=0.1):
        print("  ✅ Hectares match.")
    else:
        print("  ❌ Hectares mismatch.")

    # Conversion / Multiplier
    conversion_rate = (calculated_count / expected_count * 100) if expected_count > 0 else 0
    print(f"Metric: {stage_name} Conversion / Multiplier")
    print(f"  Calculated: {conversion_rate:.2f}, Funnel: {ownership_data_row['Conversion / Multiplier']:.2f}")
    if np.isclose(conversion_rate, ownership_data_row['Conversion / Multiplier'], atol=0.1):
        print("  ✅ Conversion / Multiplier matches.")
    else:
        print("  ❌ Conversion / Multiplier mismatch.")

    # Retention Rate
    retention_rate = (calculated_count / expected_count * 100) if expected_count > 0 else 0
    print(f"Metric: {stage_name} Retention_Rate")
    print(f"  Calculated: {retention_rate:.1f}, Funnel: {ownership_data_row['Retention_Rate']:.1f}")
    if np.isclose(retention_rate, ownership_data_row['Retention_Rate'], atol=0.1):
        print("  ✅ Retention_Rate matches.")
    else:
        print("  ❌ Retention_Rate mismatch.")

    # --- Stage 3: Parcels w/ Private Owners ---
    print("\n--- Stage 3: Parcels w/ Private Owners ---")
    stage_name = '3. Parcels w/ Private Owners'
    private_owners_row = land_funnel[land_funnel['Stage'] == stage_name].iloc[0]

    # Business Rationale
    print("Business Rationale: This metric filters parcels to include only those owned by private individuals, excluding companies and government entities. This is critical because the primary land acquisition strategy focuses on direct outreach to private landowners.")

    # Validation
    df_private_owners_filtered = df_raw_data[df_raw_data['Tipo_Proprietario'] == 'Privato']
    unique_private_parcels_df = df_private_owners_filtered[['foglio_input', 'particella_input', 'Area']].drop_duplicates()
    calculated_count = unique_private_parcels_df.shape[0]
    calculated_hectares = unique_private_parcels_df['Area'].astype(str).str.replace(',', '.').astype(float).sum()

    print(f"Metric: {stage_name} Count")
    print(f"  Calculated: {calculated_count}, Funnel: {private_owners_row['Count']}")
    if calculated_count == private_owners_row['Count']:
        print("  ✅ Count matches.")
    else:
        print("  ❌ Count mismatch.")

    print(f"Metric: {stage_name} Hectares")
    print(f"  Calculated: {calculated_hectares:.1f}, Funnel: {private_owners_row['Hectares']:.1f}")
    if np.isclose(calculated_hectares, private_owners_row['Hectares'], atol=0.1):
        print("  ✅ Hectares match.")
    else:
        print("  ❌ Hectares mismatch.")

    # Conversion / Multiplier (from previous stage: Ownership Data Retrieved)
    prev_stage_count = land_funnel[land_funnel['Stage'] == '2. Ownership Data Retrieved']['Count'].iloc[0]
    conversion_rate = (calculated_count / prev_stage_count * 100) if prev_stage_count > 0 else 0
    print(f"Metric: {stage_name} Conversion / Multiplier")
    print(f"  Calculated: {conversion_rate:.2f}, Funnel: {private_owners_row['Conversion / Multiplier']:.2f}")
    if np.isclose(conversion_rate, private_owners_row['Conversion / Multiplier'], atol=0.1):
        print("  ✅ Conversion / Multiplier matches.")
    else:
        print("  ❌ Conversion / Multiplier mismatch.")

    # Retention Rate (from Input Parcels)
    retention_rate = (calculated_count / expected_count * 100) if expected_count > 0 else 0
    print(f"Metric: {stage_name} Retention_Rate")
    print(f"  Calculated: {retention_rate:.1f}, Funnel: {private_owners_row['Retention_Rate']:.1f}")
    if np.isclose(retention_rate, private_owners_row['Retention_Rate'], atol=0.1):
        print("  ✅ Retention_Rate matches.")
    else:
        print("  ❌ Retention_Rate mismatch.")

    # --- Stage 4: Parcels w/ Residential Buildings ---
    print("\n--- Stage 4: Parcels w/ Residential Buildings ---")
    stage_name = '4. Parcels w/ Residential Buildings'
    residential_buildings_row = land_funnel[land_funnel['Stage'] == stage_name].iloc[0]

    # Business Rationale
    print("Business Rationale: This metric identifies parcels that have residential buildings (Catasto Category A). These are prioritized because they are most likely to have valid residential addresses for direct mailing campaigns, which is the most common outreach method.")

    # Validation
    individuals_cat_a_filtered = df_raw_data[
        (df_raw_data['Tipo_Proprietario'] == 'Privato') &
        (df_raw_data['classamento'].str.contains('Cat.A', na=False, case=False))
    ]
    unique_residential_parcels_df = individuals_cat_a_filtered[['foglio_input', 'particella_input', 'Area']].drop_duplicates()
    calculated_count = unique_residential_parcels_df.shape[0]
    calculated_hectares = unique_residential_parcels_df['Area'].astype(str).str.replace(',', '.').astype(float).sum()

    print(f"Metric: {stage_name} Count")
    print(f"  Calculated: {calculated_count}, Funnel: {residential_buildings_row['Count']}")
    if calculated_count == residential_buildings_row['Count']:
        print("  ✅ Count matches.")
    else:
        print("  ❌ Count mismatch.")

    print(f"Metric: {stage_name} Hectares")
    print(f"  Calculated: {calculated_hectares:.1f}, Funnel: {residential_buildings_row['Hectares']:.1f}")
    if np.isclose(calculated_hectares, residential_buildings_row['Hectares'], atol=0.1):
        print("  ✅ Hectares match.")
    else:
        print("  ❌ Hectares mismatch.")

    # Conversion / Multiplier (from previous stage: Parcels w/ Private Owners)
    prev_stage_count = land_funnel[land_funnel['Stage'] == '3. Parcels w/ Private Owners']['Count'].iloc[0]
    conversion_rate = (calculated_count / prev_stage_count * 100) if prev_stage_count > 0 else 0
    print(f"Metric: {stage_name} Conversion / Multiplier")
    print(f"  Calculated: {conversion_rate:.2f}, Funnel: {residential_buildings_row['Conversion / Multiplier']:.2f}")
    if np.isclose(conversion_rate, residential_buildings_row['Conversion / Multiplier'], atol=0.1):
        print("  ✅ Conversion / Multiplier matches.")
    else:
        print("  ❌ Conversion / Multiplier mismatch.")

    # Retention Rate (from Input Parcels)
    retention_rate = (calculated_count / expected_count * 100) if expected_count > 0 else 0
    print(f"Metric: {stage_name} Retention_Rate")
    print(f"  Calculated: {retention_rate:.1f}, Funnel: {residential_buildings_row['Retention_Rate']:.1f}")
    if np.isclose(retention_rate, residential_buildings_row['Retention_Rate'], atol=0.1):
        print("  ✅ Retention_Rate matches.")
    else:
        print("  ❌ Retention_Rate mismatch.")

except Exception as e:
    print(f"❌ Error during Land Acquisition Funnel validation: {e}")

print("\n--- Script 7 Finished ---")