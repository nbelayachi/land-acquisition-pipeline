import pandas as pd
import os

def create_powerbi_dataset(file_path, output_dir="outputs/powerbi_dataset"):
    """
    Reads the campaign results Excel file and generates a set of CSVs 
    structured for optimal use in Power BI.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return

    print(f"Reading data from: {os.path.basename(file_path)}\n")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # --- Load Core Sheets ---
        raw_df = pd.read_excel(file_path, sheet_name='All_Raw_Data')
        validation_df = pd.read_excel(file_path, sheet_name='All_Validation_Ready')
        summary_df = pd.read_excel(file_path, sheet_name='Campaign_Summary')

        # --- 1. Dimension Table: dim_Municipality ---
        print("Creating: dim_Municipality.csv")
        dim_municipality = summary_df[['CP', 'comune', 'provincia']].copy()
        dim_municipality.rename(columns={'CP': 'municipality_id', 'comune': 'municipality_name', 'provincia': 'province'}, inplace=True)
        dim_municipality.drop_duplicates(inplace=True)
        dim_municipality.to_csv(os.path.join(output_dir, "dim_Municipality.csv"), index=False)
        print(f"  -> Saved {len(dim_municipality)} rows.")

        # --- 2. Dimension Table: dim_Owner ---
        print("Creating: dim_Owner.csv")
        dim_owner = validation_df[['cf', 'cognome', 'nome', 'data_nascita', 'luogo_nascita']].copy()
        dim_owner.rename(columns={'cf': 'owner_cf', 'cognome': 'last_name', 'nome': 'first_name', 'data_nascita': 'birth_date', 'luogo_nascita': 'birth_place'}, inplace=True)
        dim_owner.drop_duplicates(subset=['owner_cf'], inplace=True)
        dim_owner.to_csv(os.path.join(output_dir, "dim_Owner.csv"), index=False)
        print(f"  -> Saved {len(dim_owner)} rows.")

        # --- 3. Dimension Table: dim_Parcel ---
        print("Creating: dim_Parcel.csv")
        dim_parcel = raw_df[['CP', 'comune_input', 'foglio_input', 'particella_input', 'Area', 'classamento']].copy()
        dim_parcel['parcel_id'] = dim_parcel['CP'].astype(str) + '-' + dim_parcel['foglio_input'].astype(str) + '-' + dim_parcel['particella_input'].astype(str)
        dim_parcel.rename(columns={'CP': 'municipality_id', 'Area': 'hectares', 'classamento': 'cadastral_category'}, inplace=True)
        dim_parcel.drop_duplicates(subset=['parcel_id'], inplace=True)
        dim_parcel.to_csv(os.path.join(output_dir, "dim_Parcel.csv"), index=False)
        print(f"  -> Saved {len(dim_parcel)} rows.")

        # --- 4. Dimension Table: dim_Address ---
        print("Creating: dim_Address.csv")
        dim_address = validation_df[['cf', 'Best_Address', 'Address_Confidence', 'Routing_Channel', 'Latitude', 'Longitude']].copy()
        dim_address.rename(columns={'cf': 'owner_cf', 'Best_Address': 'address_text', 'Address_Confidence': 'confidence_level', 'Routing_Channel': 'routing_channel'}, inplace=True)
        dim_address.to_csv(os.path.join(output_dir, "dim_Address.csv"), index=False)
        print(f"  -> Saved {len(dim_address)} rows.")

        # --- 5. Fact Table: fact_CampaignMetrics ---
        print("Creating: fact_CampaignMetrics.csv")
        fact_metrics = summary_df.copy()
        fact_metrics.rename(columns={'CP': 'municipality_id'}, inplace=True)
        fact_metrics.to_csv(os.path.join(output_dir, "fact_CampaignMetrics.csv"), index=False)
        print(f"  -> Saved {len(fact_metrics)} rows.")

        print("\n--- Power BI dataset generated successfully! ---")
        print(f"All files saved in: {os.path.abspath(output_dir)}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    campaign_results_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250704_1706\LandAcquisition_Casalpusterlengo_Castiglione_20250704_1706_Results.xlsx"
    output_directory = "outputs/powerbi_dataset"
    
    create_powerbi_dataset(campaign_results_path, output_directory)
