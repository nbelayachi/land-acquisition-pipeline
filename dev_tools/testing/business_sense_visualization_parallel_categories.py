import pandas as pd
import plotly.express as px
import numpy as np # Import numpy for np.nan

excel_file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213_Results.xlsx"

print(f"--- Generating Parallel Categories Plot for Pipeline Flow ---")

try:
    xls = pd.ExcelFile(excel_file_path)
    df_raw_data = pd.read_excel(xls, 'All_Raw_Data')
    df_validation_ready = pd.read_excel(xls, 'All_Validation_Ready')
    
    print("✅ Successfully loaded All_Raw_Data and All_Validation_Ready sheets.\n")

    # --- Data Preparation for Parallel Categories Plot ---
    # Create a unique identifier for joining
    df_raw_data['unique_id'] = df_raw_data['foglio_input'].astype(str) + '_' + \
                               df_raw_data['particella_input'].astype(str) + '_' + \
                               df_raw_data['cf'].astype(str)

    df_validation_ready['unique_id'] = df_validation_ready['foglio_input'].astype(str) + '_' + \
                                       df_validation_ready['particella_input'].astype(str) + '_' + \
                                       df_validation_ready['cf'].astype(str)

    # Merge the dataframes. We'll keep only the records that made it to validation_ready
    # and bring in the relevant raw data columns.
    df_merged = pd.merge(
        df_validation_ready,
        df_raw_data[['unique_id', 'Tipo_Proprietario', 'classamento']],
        on='unique_id',
        how='left'
    )

    # Ensure 'classamento' column exists after merge. If not, create it with NaN.
    if 'classamento' not in df_merged.columns:
        df_merged['classamento'] = np.nan

    # Clean up classamento for better visualization (e.g., extract Cat.A)
    df_merged['Classamento_Category'] = df_merged['classamento'].apply(
        lambda x: 'Cat.A' if isinstance(x, str) and 'Cat.A' in x else 'Other'
    )

    # Ensure correct order for Address_Confidence for visualization
    confidence_order = ['ULTRA_HIGH', 'HIGH', 'MEDIUM', 'LOW']
    df_merged['Address_Confidence'] = pd.Categorical(df_merged['Address_Confidence'], categories=confidence_order, ordered=True)
    df_merged = df_merged.sort_values('Address_Confidence')

    # NEW: Map Address_Confidence to numerical values for coloring
    confidence_score_map = {'ULTRA_HIGH': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
    df_merged['Address_Confidence_Score'] = df_merged['Address_Confidence'].map(confidence_score_map)

    # --- Generate Parallel Categories Plot ---
    print("Generating Parallel Categories Plot...")
    fig = px.parallel_categories(
        df_merged,
        dimensions=['Tipo_Proprietario_x', 'Classamento_Category', 'Address_Confidence', 'Routing_Channel'],
        color="Address_Confidence_Score", # Use the new numerical column for coloring
        color_continuous_scale=px.colors.sequential.Viridis,
        title="Pipeline Flow: From Raw Data to Contact Routing Decisions"
    )
    fig.show()

    print("\n--- Business Insights from Parallel Categories Plot ---")
    print("This visualization allows us to trace the journey of each contact through key pipeline stages:")
    print("1.  **Tipo_Proprietario (Owner Type)**: See how many 'Privato' (Private) vs. 'Azienda' (Company) records enter the process. Typically, 'Privato' will dominate the flow towards direct mail.")
    print("2.  **Classamento_Category (Property Classification)**: Observe the impact of the 'Cat.A' filter. You can visually confirm that only records with 'Cat.A' classification (residential buildings) proceed to the later stages of address validation and routing for direct mail.")
    print("3.  **Address_Confidence**: See how the address quality (ULTRA_HIGH, HIGH, MEDIUM, LOW) is distributed among the contacts that passed the previous filters. This is where the geocoding and classification logic plays a crucial role.")
    print("4.  **Routing_Channel**: Finally, observe how the address confidence directly influences the final routing decision (DIRECT_MAIL vs. AGENCY). You can visually confirm that higher confidence addresses are routed to DIRECT_MAIL, while lower confidence ones go to AGENCY.")
    print("\nThis plot is invaluable for understanding the pipeline's filtering and classification logic at a glance, and for identifying any unexpected flows or bottlenecks in the data transformation process.")

except Exception as e:
    print(f"❌ Error generating Parallel Categories Plot: {e}")

print("\n--- Script Finished ---")
