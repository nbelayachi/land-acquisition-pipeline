
# dev_tools/dashboards/master_visualization_suite.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import sys

# --- Configuration ---
# Set the plot style for a professional look
sns.set_theme(style="whitegrid", rc={"figure.figsize": (10, 6)})

# --- Helper Functions ---
def handle_error(e):
    """Creates a placeholder image with an error message for debugging in Power BI."""
    fig, ax = plt.subplots()
    error_text = f'An error occurred in the Python script:\n\n{e}'
    ax.text(0.5, 0.5, error_text, ha='center', va='center', wrap=True, fontsize=8)
    ax.axis('off')
    plt.show()

# --- Visualization Functions ---

def create_sankey_diagram(df):
    """Generates a Sankey diagram for the contact processing funnel."""
    try:
        contact_funnel = df[df['Funnel_Type'] == 'Contact Processing'].set_index('Stage')
        owner_count = contact_funnel.loc['1. Owner Discovery']['Count']
        address_count = contact_funnel.loc['2. Address Expansion']['Count']
        direct_mail_count = contact_funnel.loc['4. Direct Mail Ready']['Count']
        agency_count = contact_funnel.loc['5. Agency Investigation Required']['Count']

        labels = ['1. Owner Discovery', '2. Address Expansion', '3. Direct Mail Ready', '4. Agency Investigation Required']
        node_map = {label: i for i, label in enumerate(labels)}

        source_indices = [node_map['1. Owner Discovery'], node_map['2. Address Expansion'], node_map['2. Address Expansion']]
        target_indices = [node_map['2. Address Expansion'], node_map['3. Direct Mail Ready'], node_map['4. Agency Investigation Required']]
        values = [address_count, direct_mail_count, agency_count]

        fig = go.Figure(data=[go.Sankey(
            node=dict(pad=25, thickness=20, line=dict(color="black", width=0.5), label=labels, color="#307FE2"),
            link=dict(source=source_indices, target=target_indices, value=values)
        )])
        fig.update_layout(title_text="Contact Processing Flow", font_size=12)
        fig.show()
    except Exception as e:
        handle_error(e)

def create_hectare_distribution_plot(df):
    """Generates a violin plot showing the distribution of parcel sizes by municipality."""
    try:
        # Ensure correct data types
        df['Input_Area_Ha'] = pd.to_numeric(df['Input_Area_Ha'], errors='coerce')
        df.dropna(subset=['Input_Area_Ha', 'comune'], inplace=True)

        plt.figure(figsize=(12, 7))
        sns.violinplot(data=df, x='comune', y='Input_Area_Ha', inner='quartile', palette='viridis')
        plt.title('Distribution of Parcel Hectares by Municipality', fontsize=16)
        plt.xlabel('Municipality', fontsize=12)
        plt.ylabel('Hectares (ha)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    except Exception as e:
        handle_error(e)

# --- Main Execution Block ---

# This is the main entry point when the script is run by Power BI.

# Which visualization to run? 
# We will control this with a simple variable. You can change this in the script editor in Power BI.
# Options: "sankey", "hectare_distribution"
VISUALIZATION_TO_RUN = "sankey" 

try:
    if 'dataset' not in globals():
        raise NameError("The 'dataset' DataFrame was not found. Please drag data fields into the visual's 'Values' well in Power BI.")

    # --- Data Loading and Selection ---
    # Power BI passes all dragged-in fields into the 'dataset' DataFrame.
    # We will select the correct data based on the visualization we want to run.
    
    if VISUALIZATION_TO_RUN == "sankey":
        # The Sankey needs the funnel data
        required_cols = ['Funnel_Type', 'Stage', 'Count']
        if not all(col in dataset.columns for col in required_cols):
            raise ValueError(f"For the Sankey diagram, please ensure the following fields are in the 'Values' well: {required_cols}")
        create_sankey_diagram(dataset)

    elif VISUALIZATION_TO_RUN == "hectare_distribution":
        # The distribution plot needs the summary data
        required_cols = ['comune', 'Input_Area_Ha']
        if not all(col in dataset.columns for col in required_cols):
            raise ValueError(f"For the hectare distribution plot, please ensure the following fields are in the 'Values' well: {required_cols}")
        create_hectare_distribution_plot(dataset)

    else:
        raise ValueError(f"Unknown visualization type: '{VISUALIZATION_TO_RUN}'. Check the VISUALIZATION_TO_RUN variable.")

except Exception as e:
    handle_error(e)
