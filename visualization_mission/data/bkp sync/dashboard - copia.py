#!/usr/bin/env python3
"""
Final Corrected Campaign Dashboard Generator

This script generates a comprehensive, interactive HTML dashboard using Plotly.
It integrates the final visual layout with the fully corrected and validated
data calculation logic. This definitive version calculates all key metrics
directly from raw data sheets for maximum accuracy and reliability.
"""

import pandas as pd
import re
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import os

class FinalDashboardGenerator:
    def __init__(self, excel_path, input_file_path):
        self.excel_path = excel_path
        self.input_file_path = input_file_path
        self.data = self.load_data()
        self.colors = {
            'primary': '#1e40af', 'secondary': '#059669', 'success': '#16a34a',
            'warning': '#d97706', 'danger': '#dc2626', 'neutral': '#6b7280'
        }

    def load_data(self):
        """Load all necessary data sheets from the Excel files."""
        try:
            data = {}
            print("-> Loading all necessary data from Excel files...")
            data['Input_File'] = pd.read_excel(self.input_file_path, sheet_name='Sheet1')
            data['All_Raw_Data'] = pd.read_excel(self.excel_path, sheet_name='All_Raw_Data')
            data['Final_Mailing_List'] = pd.read_excel(self.excel_path, sheet_name='Final_Mailing_List')
            data['All_Validation_Ready'] = pd.read_excel(self.excel_path, sheet_name='All_Validation_Ready')
            data['Address_Quality_Distribution'] = pd.read_excel(self.excel_path, sheet_name='Address_Quality_Distribution')
            
            # Sanitize column names for consistency to prevent KeyErrors
            for key in data:
                data[key].columns = [str(c).strip() for c in data[key].columns]

            print("-> Data loading complete.")
            return data
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise

    def get_correct_unique_parcels(self, source_df, parcel_id_cols):
        """Helper function to get unique parcels from a DataFrame."""
        df = source_df.dropna(subset=parcel_id_cols)
        return df[parcel_id_cols].drop_duplicates().shape[0]

    def get_final_unique_parcels_from_mailing(self):
        """
        Parses the 'Final_Mailing_List' using the 'Parcels' column as the
        source of truth to get a definitive list of unique parcels.
        """
        print("-> Parsing unique parcels from the 'Parcels' column...")
        df_mailing = self.data['Final_Mailing_List']
        parcels_list = []
        for _, row in df_mailing.iterrows():
            municipality_clean = re.sub(r'\s*\([^)]*\)', '', str(row['Municipality'])).strip()
            parcels_str = str(row['Parcels'])
            parcel_combinations = [p.strip() for p in parcels_str.split(';')]
            for combo in parcel_combinations:
                if '-' in combo:
                    try:
                        foglio_num, particella_num = combo.split('-', 1)
                        parcels_list.append({
                            'municipality_norm': municipality_clean,
                            'foglio': foglio_num.strip(),
                            'particella': particella_num.strip()
                        })
                    except ValueError:
                        continue
        
        unique_parcels_df = pd.DataFrame(parcels_list).drop_duplicates().reset_index(drop=True)
        unique_parcels_df = unique_parcels_df.astype(str)
        print(f"-> Found {len(unique_parcels_df)} unique parcels.")
        return unique_parcels_df

    def calculate_validated_metrics(self):
        """This is the 'Correct Data Engine'. It calculates all metrics with the validated logic from raw data."""
        print("-> Calculating all metrics with validated logic from raw data...")
        
        input_df = self.data['Input_File'].copy()
        input_df['Area'] = input_df['Area'].astype(str).str.replace(',', '.').astype(float)
        
        # --- METRIC CALCULATIONS (ALL VALIDATED & RECALCULATED FROM RAW DATA) ---
        total_input_parcels = self.get_correct_unique_parcels(input_df, ['comune', 'foglio', 'particella'])
        
        raw_data_df = self.data['All_Raw_Data']
        available_parcels_count = self.get_correct_unique_parcels(raw_data_df, ['comune_input', 'foglio_input', 'particella_input'])
        
        available_parcel_ids = raw_data_df[['comune_input', 'foglio_input', 'particella_input']].drop_duplicates()
        available_parcel_ids.columns = ['comune', 'foglio', 'particella']
        
        merged_for_area = pd.merge(
            available_parcel_ids.astype(str), 
            input_df[['comune', 'foglio', 'particella', 'Area']].astype(str), 
            on=['comune', 'foglio', 'particella']
        )
        processed_area = merged_for_area['Area'].astype(float).sum()

        final_unique_parcels_df = self.get_final_unique_parcels_from_mailing()
        matched_final_parcels = pd.merge(
            left=final_unique_parcels_df, right=input_df.astype(str),
            left_on=['municipality_norm', 'foglio', 'particella'],
            right_on=['comune', 'foglio', 'particella'], how='inner'
        )

        input_metrics = {
            'total_parcels': total_input_parcels,
            'total_area': input_df['Area'].sum(),
            'data_available_parcels': available_parcels_count
        }
        
        validation_metrics = {
            'technical_validation': len(self.data['All_Validation_Ready']),
            'processed_area': processed_area
        }

        mailing_metrics = {
            'unique_parcels': len(final_unique_parcels_df),
            'final_area': matched_final_parcels['Area'].astype(float).sum(),
            'strategic_mailings': len(self.data['Final_Mailing_List']),
            'property_owners': self.data['Final_Mailing_List']['cf'].nunique()
        }
        
        pipeline_metrics = {
            'data_availability_rate': (input_metrics['data_available_parcels'] / input_metrics['total_parcels']) * 100,
            'parcel_success_rate': (mailing_metrics['unique_parcels'] / input_metrics['total_parcels']) * 100,
            'address_optimization_rate': (mailing_metrics['strategic_mailings'] / validation_metrics['technical_validation']) * 100
        }
        
        geographic_distribution = matched_final_parcels['comune'].value_counts().reset_index()
        geographic_distribution.columns = ['Municipality', 'Parcel Count']
        
        return {
            'input': input_metrics,
            'validation': validation_metrics,
            'mailing': mailing_metrics,
            'pipeline': pipeline_metrics,
            'geographic_distribution': geographic_distribution,
            'address_quality': self.data['Address_Quality_Distribution'],
            'owner_consolidation': self.data['Final_Mailing_List'].groupby('cf').size().value_counts().sort_index()
        }

    def create_plotly_dashboard(self):
        """Generates the comprehensive, interactive HTML dashboard using Plotly."""
        print("-> Generating final Plotly HTML dashboard...")
        metrics = self.calculate_validated_metrics()

        pio.templates.default = "plotly_white"

        # Corrected Dual Funnel Chart
        fig_funnel = make_subplots(
            rows=1, cols=2,
            subplot_titles=['<b>Technical Processing Funnel</b><br><sub>(Record Filtering)</sub>', '<b>Business Qualification Funnel</b><br><sub>(Strategic Asset Targeting)</sub>'],
            specs=[[{"type": "funnel"}, {"type": "funnel"}]], horizontal_spacing=0.1
        )
        fig_funnel.add_trace(go.Funnel(
            y=["Owner Records Found", "Address Validation", "Strategic Mailings"],
            x=[metrics['validation']['technical_validation'], metrics['validation']['technical_validation'], metrics['mailing']['strategic_mailings']],
            textinfo="value+percent initial", marker={"color": self.colors['secondary']},
            connector={"line": {"color": self.colors['secondary'], "dash": "solid", "width": 3}}
        ), row=1, col=1)
        fig_funnel.add_trace(go.Funnel(
            y=["Original Input Parcels", "Data Available Parcels", "Final Unique Parcels", "Final Property Owners"],
            x=[metrics['input']['total_parcels'], metrics['input']['data_available_parcels'], metrics['mailing']['unique_parcels'], metrics['mailing']['property_owners']],
            textinfo="value+percent initial", marker={"color": self.colors['primary']},
            connector={"line": {"color": self.colors['primary'], "dash": "solid", "width": 3}}
        ), row=1, col=2)
        fig_funnel.update_layout(showlegend=False, height=500, margin=dict(t=100, b=20, l=20, r=20))

        # Area Flow Chart
        area_stages = ['Original Input Area', 'Processed Area', 'Final Targeted Area']
        area_values = [metrics['input']['total_area'], metrics['validation']['processed_area'], metrics['mailing']['final_area']]
        fig_area = go.Figure(go.Bar(
            x=area_stages, y=area_values,
            text=[f"{v:.0f} Ha" for v in area_values], textposition='auto',
            marker_color=[self.colors['neutral'], self.colors['warning'], self.colors['success']]
        ))
        fig_area.update_layout(title_text='Area Flow Analysis (Hectares)', yaxis_title="Hectares")

        # Geographic Distribution Chart
        geo_df = metrics['geographic_distribution']
        fig_geo = go.Figure(go.Pie(
            labels=geo_df['Municipality'], values=geo_df['Parcel Count'],
            textinfo='label+percent+value', hole=.4
        ))
        fig_geo.update_layout(title_text='Geographic Distribution of Final Parcels', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2))

        # Address Quality Chart
        quality_df = metrics['address_quality']
        fig_quality = go.Figure(data=[go.Pie(
            labels=quality_df.iloc[:, 0], values=quality_df.iloc[:, 1], hole=.4,
            marker_colors=[self.colors['success'], self.colors['secondary'], self.colors['warning'], self.colors['danger']],
            textinfo='label+percent+value', pull=[0.05, 0, 0, 0]
        )])
        fig_quality.update_layout(
            title_text='Address Quality Distribution', showlegend=False,
            annotations=[dict(text=f"{metrics['validation']['technical_validation']}<br>Validated", x=0.5, y=0.5, font_size=16, showarrow=False)]
        )

        # Owner Consolidation Chart
        consolidation_df = metrics['owner_consolidation']
        fig_consolidation = go.Figure(go.Bar(
            x=consolidation_df.index, y=consolidation_df.values,
            marker_color=self.colors['success'], text=consolidation_df.values, textposition='outside'
        ))
        fig_consolidation.update_layout(title_text='Owner Consolidation (Mailings per Owner)', xaxis_title="Mailings per Owner", yaxis_title="Number of Owners")

        # Convert Figures to HTML
        funnel_html = pio.to_html(fig_funnel, full_html=False, include_plotlyjs='cdn')
        area_html = pio.to_html(fig_area, full_html=False, include_plotlyjs=False)
        geo_html = pio.to_html(fig_geo, full_html=False, include_plotlyjs=False)
        quality_html = pio.to_html(fig_quality, full_html=False, include_plotlyjs=False)
        consolidation_html = pio.to_html(fig_consolidation, full_html=False, include_plotlyjs=False)

        # Build Final HTML
        html_string = f"""
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Campaign4 Comprehensive Dashboard</title><script src="https://cdn.plot.ly/plotly-latest.min.js"></script><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"><link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
<style>
    body {{ font-family: 'Inter', sans-serif; background: #f8f9fa; color: #212529; }}
    .dashboard-container {{ max-width: 1600px; margin: 0 auto; padding: 20px; }}
    .header {{ text-align: center; margin-bottom: 30px; }}
    .header h1 {{ font-size: 2.5rem; font-weight: 700; color: #1e40af; }}
    .header p {{ font-size: 1.1rem; color: #6b7280; }}
    .kpi-section-header {{ font-size: 1.5rem; font-weight: 600; color: #1f2937; margin-top: 40px; margin-bottom: 20px; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }}
    .kpi-card {{ background: white; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
    .kpi-value {{ font-size: 2.5rem; font-weight: 700; }}
    .kpi-label {{ font-size: 1rem; font-weight: 600; color: #374151; margin-bottom: 8px; }}
    .kpi-explanation {{ font-size: 0.8rem; color: #6b7280; }}
    .chart-section {{ background: white; border-radius: 16px; margin-top: 30px; box-shadow: 0 10px 15px rgba(0,0,0,0.05); }}
    .section-header {{ padding: 25px 30px 20px; border-bottom: 1px solid #e5e7eb; }}
    .section-header h2 {{ font-size: 1.5rem; font-weight: 600; }}
    .chart-container {{ padding: 20px; }}
    .chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }}
    @media (max-width: 992px) {{ .chart-grid {{ grid-template-columns: 1fr; }} }}
</style>
</head><body><div class="dashboard-container">
    <div class="header"><h1><i class="fas fa-seedling"></i> Campaign4 Comprehensive Dashboard</h1><p>Complete Land Acquisition Pipeline with Validated Data</p></div>
    
    <h2 class="kpi-section-header">Pipeline Input & Availability</h2>
    <div class="kpi-grid">
        <div class="kpi-card"><div class="kpi-value">{metrics['input']['total_parcels']}</div><div class="kpi-label">Original Input Parcels</div><div class="kpi-explanation">Parcels from initial file</div></div>
        <div class="kpi-card"><div class="kpi-value">{metrics['input']['total_area']:.0f} Ha</div><div class="kpi-label">Original Input Area</div><div class="kpi-explanation">Total hectares in original file</div></div>
        <div class="kpi-card"><div class="kpi-value">{metrics['pipeline']['data_availability_rate']:.1f}%</div><div class="kpi-label">Data Availability Rate</div><div class="kpi-explanation">Input parcels with retrieved data</div></div>
    </div>

    <h2 class="kpi-section-header">Data Processing & Validation Funnel</h2>
    <div class="kpi-grid">
        <div class="kpi-card"><div class="kpi-value">{metrics['validation']['processed_area']:.0f} Ha</div><div class="kpi-label">Processed Area</div><div class="kpi-explanation">Hectares with successful data retrieval</div></div>
        <div class="kpi-card"><div class="kpi-value">{metrics['validation']['technical_validation']}</div><div class="kpi-label">Technical Validation</div><div class="kpi-explanation">Owner addresses passing quality checks</div></div>
        <div class="kpi-card"><div class="kpi-value">{metrics['pipeline']['address_optimization_rate']:.1f}%</div><div class="kpi-label">Address Optimization</div><div class="kpi-explanation">Reduction from validated to mailed addresses</div></div>
    </div>

    <h2 class="kpi-section-header">Strategic & Business Outcomes</h2>
    <div class="kpi-grid">
        <div class="kpi-card"><div class="kpi-value">{metrics['mailing']['final_area']:.2f} Ha</div><div class="kpi-label">Final Targeted Area</div><div class="kpi-explanation">Total area of the 152 final unique parcels</div></div>
        <div class="kpi-card"><div class="kpi-value">{metrics['mailing']['strategic_mailings']}</div><div class="kpi-label">Strategic Mailings</div><div class="kpi-explanation">Optimized mailing list after consolidation</div></div>
        <div class="kpi-card"><div class="kpi-value">{metrics['mailing']['property_owners']}</div><div class="kpi-label">Final Property Owners</div><div class="kpi-explanation">Unique landowners targeted for outreach</div></div>
    </div>

    <div class="chart-section">
        <div class="section-header"><h2><i class="fas fa-filter"></i> Complete Pipeline Flow Analysis</h2></div>
        <div class="chart-container">{funnel_html}</div>
    </div>
    
    <div class="chart-section">
        <div class="section-header"><h2><i class="fas fa-map-marked-alt"></i> Area Flow & Geographic Distribution</h2></div>
        <div class="chart-container"><div class="chart-grid">
            <div>{area_html}</div>
            <div>{geo_html}</div>
        </div></div>
    </div>

    <div class="chart-section">
        <div class="section-header"><h2><i class="fas fa-users"></i> Strategic Optimization Analysis</h2></div>
        <div class="chart-container"><div class="chart-grid">
            <div>{consolidation_html}</div>
            <div>{quality_html}</div>
        </div></div>
    </div>
</div></body></html>
"""
        return html_string

def main():
    print("🔍 Running Final, Corrected Campaign Dashboard Generator...")
    print("=" * 60)
    
    excel_path = r"C:\Projects\land-acquisition-pipeline\visualization_mission\data\Campaign4_Results.xlsx"
    input_file_path = r"C:\Projects\land-acquisition-pipeline\visualization_mission\data\Input_Castiglione Casalpusterlengo CP.xlsx"
    output_path = r"C:\Projects\land-acquisition-pipeline\visualization_mission\outputs\visualizations\campaign_dashboard.html"
    
    try:
        analyzer = FinalDashboardGenerator(excel_path, input_file_path)
        html_dashboard = analyzer.create_plotly_dashboard()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_dashboard)
        
        print("\n" + "="*60)
        print(f"✅ SUCCESS! Interactive dashboard saved to: {os.path.abspath(output_path)}")
        print("You can now open this file in your web browser.")
        print("="*60)
        
    except FileNotFoundError as e:
        print(f"❌ FILE NOT FOUND: {e.filename}. Please ensure the Excel files are in the same directory as the script.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
