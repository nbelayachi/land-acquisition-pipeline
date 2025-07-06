import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def create_funnel_visualizations(file_path):
    """
    Generates and saves interactive funnel visualizations from the campaign results.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return

    print(f"Reading data from: {os.path.basename(file_path)}\n")
    try:
        funnel_df = pd.read_excel(file_path, sheet_name='Enhanced_Funnel_Analysis')

        # --- Visualization 1: Dual Funnel Chart ---
        print("Generating Dual Funnel Visualization...")
        land_funnel = funnel_df[funnel_df['Funnel_Type'] == 'Land Acquisition']
        contact_funnel = funnel_df[funnel_df['Funnel_Type'] == 'Contact Processing']

        fig = make_subplots(
            rows=1, cols=2, 
            specs=[[{'type': 'funnel'}, {'type': 'funnel'}]],
            subplot_titles=("Land Acquisition Funnel", "Contact Processing Funnel")
        )

        fig.add_trace(go.Funnel(
            name = 'Parcels',
            y = land_funnel['Stage'],
            x = land_funnel['Count'],
            textinfo = "value+percent initial"
        ), row=1, col=1)

        fig.add_trace(go.Funnel(
            name = 'Contacts',
            y = contact_funnel['Stage'],
            x = contact_funnel['Count'],
            textinfo = "value+percent previous"
        ), row=1, col=2)

        fig.update_layout(title_text="Campaign Performance Funnel")
        fig.write_html("outputs/analysis_results/campaign_funnel.html")
        print("  -> Saved to outputs/analysis_results/campaign_funnel.html\n")

        print("--- Funnel visualization generated successfully! ---")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    campaign_results_path = "/mnt/c/Projects/land-acquisition-pipeline/completed_campaigns/LandAcquisition_Casalpusterlengo_Castiglione_20250704_1706/LandAcquisition_Casalpusterlengo_Castiglione_20250704_1706_Results.xlsx"
    
    # Ensure output directory exists
    os.makedirs("outputs/analysis_results", exist_ok=True)

    create_funnel_visualizations(campaign_results_path)
