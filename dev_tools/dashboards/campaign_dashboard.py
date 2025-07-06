
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium

def display_dashboard(df_dict):
    """Renders the main dashboard components."""
    st.title("Land Acquisition Campaign Dashboard")

    # --- High-Level KPIs ---
    st.header("Campaign Overview")
    summary_df = df_dict.get('Campaign_Summary')
    if summary_df is not None:
        total_parcels = summary_df['Input_Parcels'].sum()
        total_hectares = summary_df['Input_Area_Ha'].sum()
        final_contacts = summary_df['Direct_Mail_Final_Contacts'].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Input Parcels", f"{total_parcels}")
        col2.metric("Total Input Hectares", f"{total_hectares:.2f} ha")
        col3.metric("Final Direct Mail Contacts", f"{final_contacts}")
    st.markdown("---")

    # --- Funnel Visualization ---
    st.header("Campaign Performance Funnel")
    funnel_df = df_dict.get('Enhanced_Funnel_Analysis')
    if funnel_df is not None:
        land_funnel = funnel_df[funnel_df['Funnel_Type'] == 'Land Acquisition']
        contact_funnel = funnel_df[funnel_df['Funnel_Type'] == 'Contact Processing']

        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'funnel'}, {'type': 'funnel'}]],
            subplot_titles=("Land Acquisition Funnel", "Contact Processing Funnel")
        )
        fig.add_trace(go.Funnel(
            name='Parcels', y=land_funnel['Stage'], x=land_funnel['Count'],
            textinfo="value+percent initial"
        ), row=1, col=1)
        fig.add_trace(go.Funnel(
            name='Contacts', y=contact_funnel['Stage'], x=contact_funnel['Count'],
            textinfo="value+percent previous"
        ), row=1, col=2)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    # --- Geographic Distribution ---
    st.header("Geographic Distribution")
    validation_df = df_dict.get('All_Validation_Ready')
    if validation_df is not None and not validation_df.empty:
        map_center = [validation_df['Latitude'].mean(), validation_df['Longitude'].mean()]
        m = folium.Map(location=map_center, zoom_start=10)

        for idx, row in validation_df.iterrows():
            folium.Marker(
                [row['Latitude'], row['Longitude']],
                popup=f"<b>{row['comune_input']}</b><br>Parcel: {row['foglio_input']}-{row['particella_input']}<br>Owner: {row['cognome']} {row['nome']}"
            ).add_to(m)
        st_folium(m, width=700, height=500)
    st.markdown("---")

    # --- Detailed Data View ---
    st.header("Detailed Data Explorer")
    sheet_to_show = st.selectbox("Select a sheet to view:", list(df_dict.keys()))
    if sheet_to_show:
        st.dataframe(df_dict[sheet_to_show])

def main():
    st.set_page_config(layout="wide")
    st.sidebar.title("Campaign Analyzer")

    uploaded_file = st.sidebar.file_uploader("Upload Campaign Results Excel File", type=["xlsx"])

    if uploaded_file is not None:
        try:
            # Load all sheets from the Excel file
            xls = pd.ExcelFile(uploaded_file)
            df_dict = {sheet_name: pd.read_excel(xls, sheet_name) for sheet_name in xls.sheet_names}
            st.sidebar.success("File loaded successfully!")
            display_dashboard(df_dict)
        except Exception as e:
            st.error(f"Error processing file: {e}")
    else:
        st.info("Please upload a campaign results file to begin analysis.")

if __name__ == "__main__":
    main()
