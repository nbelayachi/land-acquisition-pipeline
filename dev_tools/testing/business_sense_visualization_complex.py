import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

excel_file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213_Results.xlsx"

try:
    xls = pd.ExcelFile(excel_file_path)
    df_funnel = pd.read_excel(xls, 'Enhanced_Funnel_Analysis')
    df_quality = pd.read_excel(xls, 'Address_Quality_Distribution')
    df_validation_ready = pd.read_excel(xls, 'All_Validation_Ready')
    
    print("✅ Data loaded successfully for complex Plotly visualizations.")

except Exception as e:
    print(f"❌ Error loading data for Plotly: {e}")
    exit()

# --- 1. Sankey Diagram for Land Acquisition Funnel (Parcels & Hectares) ---
print("\nGenerating Sankey Diagram for Land Acquisition Funnel...")

land_acquisition_funnel_data = df_funnel[df_funnel['Funnel_Type'] == 'Land Acquisition']

# Define nodes and links for Sankey
labels = land_acquisition_funnel_data['Stage'].tolist()

source = []
target = []
value_count = []
value_hectares = []

# Map stages to numerical indices
stage_to_index = {stage: i for i, stage in enumerate(labels)}

# Define flow for parcels
for i in range(len(land_acquisition_funnel_data) - 1):
    source.append(stage_to_index[land_acquisition_funnel_data.iloc[i]['Stage']])
    target.append(stage_to_index[land_acquisition_funnel_data.iloc[i+1]['Stage']])
    value_count.append(land_acquisition_funnel_data.iloc[i+1]['Count'])
    value_hectares.append(land_acquisition_funnel_data.iloc[i+1]['Hectares'])

fig_sankey_land = go.Figure(data=[
    go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color="blue"
        ),
        link=dict(
            source=source,
            target=target,
            value=value_count, # Use count for primary flow
            # Add custom hover text for hectares
            hovertemplate=
                'Stage: %{source.label} -> %{target.label}<br>' +
                'Parcels: %{value}<br>' +
                'Hectares: %{customdata:.1f} Ha<extra></extra>',
            customdata=value_hectares
        )
    )
])

fig_sankey_land.update_layout(title_text="Land Acquisition Funnel: Parcel & Hectare Flow", font_size=10)
fig_sankey_land.show()

# --- 2. Sankey Diagram for Contact Processing Funnel (Owners & Addresses Flow) ---
print("\nGenerating Sankey Diagram for Contact Processing Funnel...")

contact_processing_funnel_data = df_funnel[df_funnel['Funnel_Type'] == 'Contact Processing']

# Define nodes and links for Sankey
labels_contact = contact_processing_funnel_data['Stage'].tolist()

source_contact = []
target_contact = []
value_count_contact = []
value_hectares_contact = []

# Map stages to numerical indices
stage_to_index_contact = {stage: i for i, stage in enumerate(labels_contact)}

# Define flow for owners/addresses
for i in range(len(contact_processing_funnel_data) - 1):
    source_contact.append(stage_to_index_contact[contact_processing_funnel_data.iloc[i]['Stage']])
    target_contact.append(stage_to_index_contact[contact_processing_funnel_data.iloc[i+1]['Stage']])
    value_count_contact.append(contact_processing_funnel_data.iloc[i+1]['Count'])
    value_hectares_contact.append(contact_processing_funnel_data.iloc[i+1]['Hectares'])

# Add links for Direct Mail Ready and Agency Investigation Required from Address Validation & Enhancement
# Assuming 'Address Validation & Enhancement' is the source for these two branches
addr_validation_index = stage_to_index_contact['3. Address Validation & Enhancement']
direct_mail_index = stage_to_index_contact['4. Direct Mail Ready']
agency_index = stage_to_index_contact['5. Agency Investigation Required']

source_contact.append(addr_validation_index)
target_contact.append(direct_mail_index)
value_count_contact.append(contact_processing_funnel_data[contact_processing_funnel_data['Stage'] == '4. Direct Mail Ready']['Count'].iloc[0])
value_hectares_contact.append(contact_processing_funnel_data[contact_processing_funnel_data['Stage'] == '4. Direct Mail Ready']['Hectares'].iloc[0])

source_contact.append(addr_validation_index)
target_contact.append(agency_index)
value_count_contact.append(contact_processing_funnel_data[contact_processing_funnel_data['Stage'] == '5. Agency Investigation Required']['Count'].iloc[0])
value_hectares_contact.append(contact_processing_funnel_data[contact_processing_funnel_data['Stage'] == '5. Agency Investigation Required']['Hectares'].iloc[0])


fig_sankey_contact = go.Figure(data=[
    go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels_contact,
            color="green"
        ),
        link=dict(
            source=source_contact,
            target=target_contact,
            value=value_count_contact, # Use count for primary flow
            # Add custom hover text for hectares
            hovertemplate=
                'Stage: %{source.label} -> %{target.label}<br>' +
                'Count: %{value}<br>' +
                'Hectares: %{customdata:.1f} Ha<extra></extra>',
            customdata=value_hectares_contact
        )
    )
])

fig_sankey_contact.update_layout(title_text="Contact Processing Funnel: Owner & Address Flow", font_size=10)
fig_sankey_contact.show()

# --- 3. Sunburst Chart for Address Quality Breakdown ---
print("\nGenerating Sunburst Chart for Address Quality Breakdown...")

fig_sunburst = px.sunburst(
    df_validation_ready,
    path=['Routing_Channel', 'Address_Confidence'],
    title='Address Quality Breakdown by Routing Channel',
    color='Address_Confidence',
    color_discrete_map={
        'ULTRA_HIGH': '#2ca02c', # Green
        'HIGH': '#98df8a',    # Light Green
        'MEDIUM': '#ff7f0e',   # Orange
        'LOW': '#d62728'      # Red
    },
    hover_data={
        'cleaned_ubicazione': False, # Don't show individual addresses in hover
        'Quality_Notes': True
    }
)
fig_sunburst.show()

# --- 4. Enhanced Bar Chart for Multiplier Comparison ---
print("\nGenerating Enhanced Bar Chart for Multiplier Comparison...")

multipliers_data = df_funnel[
    (df_funnel['Stage'] == '1. Owner Discovery') |
    (df_funnel['Stage'] == '2. Address Expansion')
].copy() # Use .copy() to avoid SettingWithCopyWarning

# Ensure the 'Conversion / Multiplier' column is numeric
multipliers_data['Conversion / Multiplier'] = pd.to_numeric(multipliers_data['Conversion / Multiplier'])

fig_multipliers_enhanced = px.bar(
    multipliers_data,
    x='Stage',
    y='Conversion / Multiplier',
    title='Owner Discovery vs. Address Expansion Multipliers',
    text_auto=True, # Automatically show text labels
    color='Stage', # Color by stage for better distinction
    hover_data={
        'Count': True,
        'Hectares': ':.1f Ha',
        'Business_Rule': True,
        'Process_Notes': True,
        'Conversion / Multiplier': ':.2f' # Format hover text
    }
)
fig_multipliers_enhanced.update_layout(yaxis_title='Multiplier (x)', xaxis_title=None)
fig_multipliers_enhanced.show()

print("\n--- Complex Plotly Visualizations Generated ---")
