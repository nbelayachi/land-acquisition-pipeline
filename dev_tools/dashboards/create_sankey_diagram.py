
# dev_tools/dashboards/create_sankey_diagram.py

import pandas as pd
import plotly.graph_objects as go
import sys

# This script is designed to be run from within the Power BI Python visual.
# It expects a DataFrame named 'dataset' to be passed in by Power BI.
# The 'dataset' DataFrame is created by Power BI from the fields you drag into the 'Values' well.

try:
    # This line is the key: it assumes Power BI has created the 'dataset' DataFrame.
    if 'dataset' not in globals():
        raise NameError("The 'dataset' DataFrame was not found. Please ensure you have dragged data fields into the visual's 'Values' well in Power BI before running the script.")

    # --- Data Transformation for Sankey ---
    df = dataset.copy()

    # Filter for the relevant funnel type if the column exists
    if 'Funnel_Type' in df.columns:
        contact_funnel = df[df['Funnel_Type'] == 'Contact Processing'].set_index('Stage')
    else:
        contact_funnel = df.set_index('Stage')

    # Extract counts for each stage dynamically
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
    node_map = {label: i for i, label in enumerate(labels)}

    # Define the links (flows) between the nodes
    source_indices = [node_map['1. Owner Discovery'], node_map['2. Address Expansion'], node_map['2. Address Expansion']]
    target_indices = [node_map['2. Address Expansion'], node_map['3. Direct Mail Ready'], node_map['4. Agency Investigation Required']]
    values = [address_count, direct_mail_count, agency_count]

    # --- Create the Sankey Figure ---
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=25,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color="#307FE2"
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values
        )
    )])

    fig.update_layout(title_text="Contact Processing Flow", font_size=12, height=500)

    # --- Output for Power BI ---
    # The fig.show() command automatically renders the image in the Power BI visual.
    fig.show()

except Exception as e:
    # If an error occurs, create a placeholder image with the error message.
    # This is crucial for debugging within Power BI.
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    error_text = f'An error occurred in the Python script:\n\n{e}'
    ax.text(0.5, 0.5, error_text, ha='center', va='center', wrap=True, fontsize=8)
    ax.axis('off')
    plt.show()
