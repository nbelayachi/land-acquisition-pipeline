import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

excel_file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250704_0028\LandAcquisition_Casalpusterlengo_Castiglione_20250704_0028_Results.xlsx"

try:
    xls = pd.ExcelFile(excel_file_path)
    df_funnel = pd.read_excel(xls, 'Enhanced_Funnel_Analysis')
    df_quality = pd.read_excel(xls, 'Address_Quality_Distribution')
    df_validation_ready = pd.read_excel(xls, 'All_Validation_Ready')
    
    print("✅ Data loaded successfully for Plotly visualizations.")

except Exception as e:
    print(f"❌ Error loading data for Plotly: {e}")
    exit()

# --- Visualizations ---

# 1. Interactive Land Acquisition Funnel Chart
print("\nGenerating Interactive Land Acquisition Funnel Chart...")
land_acquisition_funnel_data = df_funnel[df_funnel['Funnel_Type'] == 'Land Acquisition']
fig_land_funnel = px.funnel(
    land_acquisition_funnel_data,
    x='Count',
    y='Stage',
    title='Land Acquisition Pipeline Flow (Parcels)',
    orientation='h',
    hover_data={
        'Hectares': ':.1f Ha',
        'Conversion / Multiplier': ':.2f%',
        'Retention_Rate': ':.1f%',
        'Business_Rule': True,
        'Process_Notes': True
    }
)
fig_land_funnel.update_layout(yaxis_title=None, xaxis_title='Number of Parcels')
fig_land_funnel.show()

# 2. Interactive Contact Processing Funnel Chart
print("\nGenerating Interactive Contact Processing Funnel Chart...")
contact_processing_funnel_data = df_funnel[df_funnel['Funnel_Type'] == 'Contact Processing']
fig_contact_funnel = px.funnel(
    contact_processing_funnel_data,
    x='Count',
    y='Stage',
    title='Contact Processing Pipeline Flow (Owners & Addresses)',
    orientation='h',
    hover_data={
        'Hectares': ':.1f Ha',
        'Conversion / Multiplier': ':.2f',
        'Retention_Rate': ':.1f%',
        'Stage_Conversion_Rate': ':.1f%',
        'Business_Rule': True,
        'Process_Notes': True
    }
)
fig_contact_funnel.update_layout(yaxis_title=None, xaxis_title='Count')
fig_contact_funnel.show()

# 3. Address Quality Distribution (Stacked Bar Chart)
print("\nGenerating Address Quality Distribution Chart...")
fig_quality_dist = px.bar(
    df_quality,
    x='Quality_Level',
    y='Percentage',
    color='Quality_Level',
    title='Address Quality Distribution',
    text='Percentage',
    hover_data={
        'Count': True,
        'Processing_Type': True,
        'Business_Value': True,
        'Automation_Level': True,
        'Routing_Decision': True
    }
)
fig_quality_dist.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig_quality_dist.update_layout(yaxis_title='Percentage of Total Addresses', xaxis_title='Address Quality Level')
fig_quality_dist.show()

# 4. Owner Discovery vs. Address Expansion Multipliers (Bar Chart)
print("\nGenerating Multiplier Comparison Chart...")
multipliers_data = df_funnel[
    (df_funnel['Stage'] == '1. Owner Discovery') |
    (df_funnel['Stage'] == '2. Address Expansion')
]

fig_multipliers = px.bar(
    multipliers_data,
    x='Stage',
    y='Conversion / Multiplier',
    title='Owner Discovery vs. Address Expansion Multipliers',
    text='Conversion / Multiplier',
    hover_data={
        'Count': True,
        'Hectares': ':.1f Ha',
        'Business_Rule': True,
        'Process_Notes': True
    }
)
fig_multipliers.update_traces(texttemplate='%{text:.2f}x', textposition='outside')
fig_multipliers.update_layout(yaxis_title='Multiplier (x)', xaxis_title=None)
fig_multipliers.show()

# 5. Scatter Plot: Address Confidence vs. Interpolation Risk (from All_Validation_Ready)
print("\nGenerating Address Confidence vs. Interpolation Risk Scatter Plot...")
fig_scatter = px.scatter(
    df_validation_ready,
    x='Address_Confidence',
    y='Interpolation_Risk',
    color='Routing_Channel',
    hover_data=['cleaned_ubicazione', 'Quality_Notes'],
    title='Address Confidence vs. Interpolation Risk',
    labels={'Interpolation_Risk': 'Has Interpolation Risk'}
)
fig_scatter.update_layout(xaxis_title='Address Confidence', yaxis_title='Interpolation Risk (True/False)')
fig_scatter.show()

print("\n--- Plotly Visualizations Generated ---")