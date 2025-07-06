import pandas as pd
import plotly.graph_objects as go
import sys

# This script is designed to be run from within the Power BI Python visual.
# It expects a DataFrame named 'dataset' to be passed in by Power BI.

# --- Data Preparation ---
# In a real Power BI scenario, you would drag the required fields into the 
# Python visual's 'Values' well. This creates the 'dataset' DataFrame.

# For standalone testing, you can uncomment the following lines and replace with your file path:
# if 'dataset' not in globals():
#     print("Running in standalone mode for testing.", file=sys.stderr)
#     file_path = 'C:/Projects/land-acquisition-pipeline/completed_campaigns/LandAcquisition_Casalpusterlengo_Castiglione_20250704_1706/LandAcquisition_Casalpusterlengo_Castiglione_20250704_1706_Results.xlsx'
#     dataset = pd.read_excel(file_path, sheet_name='Enhanced_Funnel_Analysis')
#     quality_dataset = pd.read_excel(file_path, sheet_name='Address_Quality_Distribution')

try:
    # --- Data Transformation for Sankey ---
    # We need to manually define the connections (links) and nodes for the diagram.
    
    # Filter for the relevant funnel
    contact_funnel = dataset[dataset['Funnel_Type'] == 'Contact Processing'].set_index('Stage')

    # Extract counts for each stage
    owner_count = contact_funnel.loc['1. Owner Discovery']['Count']
    address_count = contact_funnel.loc['2. Address Expansion']['Count']
    direct_mail_count = contact_funnel.loc['4. Direct Mail Ready']['Count']
    agency_count = contact_funnel.loc['5. Agency Investigation Required']['Count']

    # Define the nodes (stages) of our diagram
    labels = [
        '1. Owner Discovery',
        '2. Address Expansion',
        '3. Direct Mail Ready',
        '4. Agency Investigation Required'
    ]

    # Define the links (flows) between the nodes
    # The indices correspond to the 'labels' list above (e.g., 0 -> 1 is Owner Discovery -> Address Expansion)
    source_nodes = [0, 1, 1]  # From: Owner Discovery, Address Expansion, Address Expansion
    target_nodes = [1, 2, 3]  # To:   Address Expansion, Direct Mail, Agency
    values = [address_count, direct_mail_count, agency_count] # The size of the flow

    # --- Create the Sankey Figure ---
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=25,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color="#307FE2" # A professional blue
        ),
        link=dict(
            source=source_nodes,
            target=target_nodes,
            value=values
        )
    )])

    fig.update_layout(title_text="Contact Processing Flow", font_size=12)

    # --- Output for Power BI ---
    # Power BI expects the script to output an image. We'll use Plotly's capability to do this.
    # Note: In the Power BI service, you may need to configure a Python environment.
    fig.show()

except Exception as e:
    # If an error occurs, print it to the diagnostics log in Power BI
    print(f"ERROR: {e}", file=sys.stderr)
    # You can also create a placeholder image with the error message
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, f'An error occurred:\n{e}', ha='center', va='center', wrap=True)
    ax.axis('off')
    plt.show()
