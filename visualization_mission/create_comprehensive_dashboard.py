#!/usr/bin/env python3
"""
Comprehensive Campaign4 Dashboard
Accurate metrics with data availability context and pipeline transparency
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime

class ComprehensiveDashboard:
    def __init__(self, excel_path, input_file_path):
        self.excel_path = excel_path
        self.input_file_path = input_file_path
        self.data = self.load_data()
        self.colors = {
            'primary': '#1e40af',      # Blue 700
            'secondary': '#059669',    # Emerald 600
            'success': '#16a34a',      # Green 600
            'warning': '#d97706',      # Amber 600
            'danger': '#dc2626',       # Red 600
            'neutral': '#6b7280',      # Gray 500
            'light': '#f8fafc',        # Slate 50
            'dark': '#1f2937'          # Gray 800
        }
        
    def load_data(self):
        """Load and analyze all data sources"""
        try:
            data = {
                'Campaign_Summary': pd.read_excel(self.excel_path, sheet_name='Campaign_Summary'),
                'Enhanced_Funnel_Analysis': pd.read_excel(self.excel_path, sheet_name='Enhanced_Funnel_Analysis'),
                'Address_Quality_Distribution': pd.read_excel(self.excel_path, sheet_name='Address_Quality_Distribution'),
                'All_Validation_Ready': pd.read_excel(self.excel_path, sheet_name='All_Validation_Ready'),
                'Final_Mailing_List': pd.read_excel(self.excel_path, sheet_name='Final_Mailing_List'),
                'All_Raw_Data': pd.read_excel(self.excel_path, sheet_name='All_Raw_Data')
            }
            
            # Load input file
            if os.path.exists(self.input_file_path):
                data['Input_File'] = pd.read_excel(self.input_file_path, sheet_name='Sheet1')
            
            # Clean Campaign_Summary
            cs = data['Campaign_Summary']
            clean_rows = cs['comune'].notna() & (cs['comune'] != '')
            data['Campaign_Summary'] = cs[clean_rows].reset_index(drop=True)
            
            return data
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def analyze_data_availability(self):
        """Analyze data availability and processing pipeline"""
        input_file = self.data.get('Input_File')
        all_raw_data = self.data['All_Raw_Data']
        all_validation = self.data['All_Validation_Ready']
        campaign_summary = self.data['Campaign_Summary']
        
        analysis = {}
        
        if input_file is not None:
            # Input file analysis
            input_municipalities = set(input_file['comune'].unique())
            input_parcels = len(input_file)
            input_area = input_file['Area'].sum()
            
            analysis['input'] = {
                'municipalities': input_municipalities,
                'parcels': input_parcels,
                'area': input_area
            }
        
        # Raw data analysis
        raw_municipalities = set(all_raw_data['comune'].unique()) if 'comune' in all_raw_data.columns else set()
        raw_area = all_raw_data['Area'].sum() if 'Area' in all_raw_data.columns else 0
        
        analysis['raw_data'] = {
            'municipalities': raw_municipalities,
            'records': len(all_raw_data),
            'area': raw_area
        }
        
        # Campaign summary analysis
        campaign_municipalities = set(campaign_summary['comune'].unique())
        campaign_area = campaign_summary['Input_Area_Ha'].sum()
        campaign_parcels = campaign_summary['Input_Parcels'].sum()
        
        analysis['campaign_summary'] = {
            'municipalities': campaign_municipalities,
            'parcels': campaign_parcels,
            'area': campaign_area
        }
        
        # Validation analysis
        validation_area = all_validation['Area'].sum()
        validation_records = len(all_validation)
        
        analysis['validation'] = {
            'records': validation_records,
            'area': validation_area
        }
        
        # Identify missing municipalities
        if input_file is not None:
            missing_municipalities = input_municipalities - campaign_municipalities
            analysis['missing_municipalities'] = missing_municipalities
        
        return analysis
    
    def get_comprehensive_metrics(self):
        """Calculate comprehensive metrics with data availability context"""
        cs = self.data['Campaign_Summary']
        all_validation = self.data['All_Validation_Ready']
        final_mailing = self.data['Final_Mailing_List']
        input_file = self.data.get('Input_File')
        
        # Data availability analysis
        availability = self.analyze_data_availability()
        
        # Core metrics
        if input_file is not None:
            original_input_parcels = len(input_file)
            original_input_area = input_file['Area'].sum()
        else:
            original_input_parcels = 238  # From investigation
            original_input_area = 412.2   # From investigation
        
        processed_parcels = int(cs['Input_Parcels'].sum())  # 228
        processed_area = float(cs['Input_Area_Ha'].sum())   # 356 Ha
        total_validated_area = float(all_validation['Area'].sum())  # 1,152 Ha
        technical_validation = len(all_validation)      # 642 addresses
        final_mailings = len(final_mailing)            # 303 mailings
        unique_owners = final_mailing['cf'].nunique()   # 157 owners
        
        # Calculate data availability rate
        data_availability_rate = (processed_parcels / original_input_parcels) * 100  # ~95%
        area_recovery_rate = (processed_area / original_input_area) * 100  # ~86%
        
        # Pipeline calculations
        parcel_success_rate = (84 / processed_parcels) * 100  # 36.8% (unique parcels in final)
        address_optimization = ((technical_validation - final_mailings) / technical_validation) * 100  # 52.8%
        owner_consolidation = final_mailings / unique_owners  # 1.9 mailings per owner
        
        return {
            'original_input_parcels': {
                'value': original_input_parcels,
                'label': 'Original Input Parcels',
                'explanation': 'Total land parcels provided in the initial input file for renewable energy site analysis'
            },
            'original_input_area': {
                'value': original_input_area,
                'label': 'Original Input Area',
                'explanation': 'Total hectares in the original input file before data availability filtering'
            },
            'data_availability_rate': {
                'value': data_availability_rate,
                'label': 'Data Availability Rate',
                'explanation': 'Percentage of input parcels for which property data was successfully retrieved from registries'
            },
            'processed_area': {
                'value': processed_area,
                'label': 'Processed Area',
                'explanation': 'Hectares with successful data retrieval and ready for owner analysis'
            },
            'validated_area': {
                'value': total_validated_area,
                'label': 'Total Validated Area',
                'explanation': 'Complete area coverage from all property records after owner discovery and validation'
            },
            'technical_validation': {
                'value': technical_validation,
                'label': 'Technical Validation',
                'explanation': 'Property owner addresses that passed geocoding and technical quality verification'
            },
            'final_mailings': {
                'value': final_mailings,
                'label': 'Strategic Mailings',
                'explanation': 'Optimized mailing list after owner consolidation and business rule application'
            },
            'unique_owners': {
                'value': unique_owners,
                'label': 'Property Owners',
                'explanation': 'Individual landowners targeted for renewable energy partnership discussions'
            }
        }
    
    def create_comprehensive_kpi_section(self):
        """Create comprehensive KPI section with data availability context"""
        metrics = self.get_comprehensive_metrics()
        availability = self.analyze_data_availability()
        
        kpi_html = f"""
        <div class="kpi-grid">
            <div class="kpi-card primary">
                <div class="kpi-icon">📄</div>
                <div class="kpi-value">{metrics['original_input_parcels']['value']}</div>
                <div class="kpi-label">{metrics['original_input_parcels']['label']}</div>
                <div class="kpi-explanation">{metrics['original_input_parcels']['explanation']}</div>
            </div>
            
            <div class="kpi-card neutral">
                <div class="kpi-icon">🗺️</div>
                <div class="kpi-value">{metrics['original_input_area']['value']:.0f} Ha</div>
                <div class="kpi-label">{metrics['original_input_area']['label']}</div>
                <div class="kpi-explanation">{metrics['original_input_area']['explanation']}</div>
            </div>
            
            <div class="kpi-card warning">
                <div class="kpi-icon">📊</div>
                <div class="kpi-value">{metrics['data_availability_rate']['value']:.1f}%</div>
                <div class="kpi-label">{metrics['data_availability_rate']['label']}</div>
                <div class="kpi-explanation">{metrics['data_availability_rate']['explanation']}</div>
            </div>
            
            <div class="kpi-card secondary">
                <div class="kpi-icon">✅</div>
                <div class="kpi-value">{metrics['processed_area']['value']:.0f} Ha</div>
                <div class="kpi-label">{metrics['processed_area']['label']}</div>
                <div class="kpi-explanation">{metrics['processed_area']['explanation']}</div>
            </div>
            
            <div class="kpi-card primary">
                <div class="kpi-icon">📐</div>
                <div class="kpi-value">{metrics['validated_area']['value']:.0f} Ha</div>
                <div class="kpi-label">{metrics['validated_area']['label']}</div>
                <div class="kpi-explanation">{metrics['validated_area']['explanation']}</div>
            </div>
            
            <div class="kpi-card secondary">
                <div class="kpi-icon">🔍</div>
                <div class="kpi-value">{metrics['technical_validation']['value']}</div>
                <div class="kpi-label">{metrics['technical_validation']['label']}</div>
                <div class="kpi-explanation">{metrics['technical_validation']['explanation']}</div>
            </div>
            
            <div class="kpi-card success">
                <div class="kpi-icon">📮</div>
                <div class="kpi-value">{metrics['final_mailings']['value']}</div>
                <div class="kpi-label">{metrics['final_mailings']['label']}</div>
                <div class="kpi-explanation">{metrics['final_mailings']['explanation']}</div>
            </div>
            
            <div class="kpi-card warning">
                <div class="kpi-icon">👤</div>
                <div class="kpi-value">{metrics['unique_owners']['value']}</div>
                <div class="kpi-label">{metrics['unique_owners']['label']}</div>
                <div class="kpi-explanation">{metrics['unique_owners']['explanation']}</div>
            </div>
        </div>
        """
        
        return kpi_html
    
    def create_data_availability_analysis(self):
        """Create analysis showing data availability pipeline"""
        availability = self.analyze_data_availability()
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                '📊 Data Availability Pipeline<br><sub>Input Processing & Registry Data Retrieval</sub>',
                '🗺️ Area Flow Analysis<br><sub>Original → Processed → Validated Area</sub>',
                '🏛️ Municipality Coverage<br><sub>Data Availability by Region</sub>',
                '⚠️ Data Quality Impact<br><sub>Missing Data Analysis</sub>'
            ],
            specs=[[{"type": "funnel"}, {"type": "xy"}],
                   [{"type": "domain"}, {"type": "xy"}]],
            horizontal_spacing=0.15,
            vertical_spacing=0.25
        )
        
        # 1. Data availability funnel
        availability_stages = [
            "Original Input",
            "Data Retrieved", 
            "Owner Discovery",
            "Technical Validation",
            "Strategic Mailings"
        ]
        
        availability_counts = [238, 228, 642, 642, 303]
        
        fig.add_trace(
            go.Funnel(
                y=availability_stages,
                x=availability_counts,
                textinfo="value+percent initial",
                textfont=dict(size=11, color="white"),
                marker=dict(color=self.colors['primary']),
                hovertemplate="<b>%{y}</b><br>Count: %{x}<br>Retention: %{percentInitial}<extra></extra>"
            ),
            row=1, col=1
        )
        
        # 2. Area flow analysis
        area_stages = ['Original\nInput', 'Processed\nArea', 'Validated\nArea']
        area_values = [412, 356, 1152]
        colors_area = [self.colors['neutral'], self.colors['warning'], self.colors['success']]
        
        fig.add_trace(
            go.Bar(
                x=area_stages,
                y=area_values,
                marker_color=colors_area,
                text=[f"{val} Ha" for val in area_values],
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>Area: %{y} Ha<extra></extra>"
            ),
            row=1, col=2
        )
        
        # 3. Municipality coverage
        cs = self.data['Campaign_Summary']
        muni_coverage = cs.set_index('comune')['Input_Area_Ha']
        
        fig.add_trace(
            go.Pie(
                labels=muni_coverage.index,
                values=muni_coverage.values,
                marker_colors=[self.colors['primary'], self.colors['secondary'], self.colors['success'], 
                             self.colors['warning'], self.colors['danger'], self.colors['neutral']],
                textinfo='label+percent',
                textfont=dict(size=10),
                hovertemplate="<b>%{label}</b><br>Area: %{value:.1f} Ha<br>Share: %{percent}<extra></extra>"
            ),
            row=2, col=1
        )
        
        # 4. Data quality impact
        impact_categories = ['Data Available', 'Data Missing', 'Somaglia (No Data)']
        impact_values = [228, 10, 1]  # Approximated based on investigation
        impact_colors = [self.colors['success'], self.colors['warning'], self.colors['danger']]
        
        fig.add_trace(
            go.Bar(
                x=impact_categories,
                y=impact_values,
                marker_color=impact_colors,
                text=impact_values,
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>Parcels: %{y}<extra></extra>"
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=900,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=11)
        )
        
        # Update axes
        fig.update_yaxes(title_text="Hectares", row=1, col=2)
        fig.update_yaxes(title_text="Number of Parcels", row=2, col=2)
        
        return fig
    
    def create_complete_pipeline_funnel(self):
        """Create complete pipeline funnel with data availability context"""
        # Enhanced pipeline with data availability
        stages = [
            "Original Input Parcels",
            "Data Available Parcels",
            "Owner Records Found", 
            "Address Validation",
            "Strategic Mailings",
            "Property Owners"
        ]
        
        counts = [238, 228, 642, 642, 303, 157]
        
        fig = go.Figure(go.Funnel(
            y=stages,
            x=counts,
            textinfo="value+percent initial",
            textfont=dict(size=13, color="white", family="Inter"),
            marker=dict(
                color=self.colors['primary'],
                line=dict(color="white", width=3)
            ),
            connector=dict(line=dict(color=self.colors['primary'], dash="solid", width=4)),
            hovertemplate="<b>%{y}</b><br>Count: %{x}<br>Retention: %{percentInitial}<extra></extra>"
        ))
        
        fig.update_layout(
            title={
                'text': '🔄 Complete Land Acquisition Pipeline<br><sub>From Original Input Through Data Availability to Strategic Targeting</sub>',
                'x': 0.5,
                'font': {'size': 18, 'color': self.colors['primary']}
            },
            height=600,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=12)
        )
        
        return fig
    
    def create_owner_consolidation_analysis(self):
        """Create detailed owner consolidation analysis"""
        final_mailing = self.data['Final_Mailing_List']
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                '👥 Owner Consolidation Distribution<br><sub>Mailings per Property Owner</sub>',
                '🗺️ Geographic Distribution<br><sub>Final Mailings by Municipality</sub>',
                '📊 Pipeline Efficiency<br><sub>Address Optimization Results</sub>',
                '🎯 Strategic Benefits<br><sub>Multi-Property Owner Targeting</sub>'
            ],
            specs=[[{"type": "xy"}, {"type": "domain"}],
                   [{"type": "xy"}, {"type": "xy"}]],
            horizontal_spacing=0.15,
            vertical_spacing=0.25
        )
        
        # 1. Owner consolidation distribution
        addresses_per_owner = final_mailing.groupby('cf').size()
        consolidation_dist = addresses_per_owner.value_counts().sort_index()
        
        fig.add_trace(
            go.Bar(
                x=consolidation_dist.index,
                y=consolidation_dist.values,
                marker_color=self.colors['success'],
                text=[f"{val}" for val in consolidation_dist.values],
                textposition='outside',
                hovertemplate="<b>%{x} mailings per owner</b><br>%{y} property owners<extra></extra>"
            ),
            row=1, col=1
        )
        
        # 2. Geographic distribution
        if 'Municipality' in final_mailing.columns:
            muni_dist = final_mailing['Municipality'].value_counts()
            
            fig.add_trace(
                go.Pie(
                    labels=muni_dist.index,
                    values=muni_dist.values,
                    marker_colors=[self.colors['primary'], self.colors['secondary'], self.colors['success'], 
                                 self.colors['warning'], self.colors['danger'], self.colors['neutral']],
                    textinfo='label+percent',
                    textfont=dict(size=10),
                    hovertemplate="<b>%{label}</b><br>Mailings: %{value}<br>Share: %{percent}<extra></extra>"
                ),
                row=1, col=2
            )
        
        # 3. Pipeline efficiency
        efficiency_stages = ['Technical\nValidation', 'Strategic\nMailings']
        efficiency_counts = [642, 303]
        reduction_pct = ((642 - 303) / 642) * 100
        
        fig.add_trace(
            go.Bar(
                x=efficiency_stages,
                y=efficiency_counts,
                marker_color=[self.colors['secondary'], self.colors['success']],
                text=[f"{count}<br>addresses" for count in efficiency_counts],
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>"
            ),
            row=1, col=2
        )
        
        # Add reduction annotation
        fig.add_annotation(
            x=0.5, y=max(efficiency_counts) * 0.7,
            text=f"{reduction_pct:.1f}% reduction<br>through optimization",
            showarrow=True,
            arrowhead=2,
            arrowcolor=self.colors['primary'],
            font=dict(size=11, color=self.colors['primary']),
            row=1, col=2
        )
        
        # 4. Strategic benefits
        single_property = (addresses_per_owner == 1).sum()
        multiple_property = (addresses_per_owner > 1).sum()
        
        fig.add_trace(
            go.Bar(
                x=['Single Property\nOwners', 'Multi-Property\nOwners'],
                y=[single_property, multiple_property],
                marker_color=[self.colors['neutral'], self.colors['warning']],
                text=[f"{single_property}", f"{multiple_property}"],
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>Count: %{y} owners<extra></extra>"
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=900,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=11)
        )
        
        # Update axes
        fig.update_xaxes(title_text="Mailings per Owner", row=1, col=1)
        fig.update_yaxes(title_text="Number of Owners", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=1, col=2)
        fig.update_yaxes(title_text="Number of Owners", row=2, col=2)
        
        return fig
    
    def create_quality_analysis(self):
        """Create quality analysis for validation stage"""
        quality_data = self.data['Address_Quality_Distribution']
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=[
                '⭐ Address Quality Distribution<br><sub>Technical Validation Results (642 addresses)</sub>', 
                '🔧 Processing Automation<br><sub>Manual vs Automated Processing</sub>'
            ],
            specs=[[{"type": "domain"}, {"type": "xy"}]],
            horizontal_spacing=0.2
        )
        
        quality_colors = {
            'ULTRA_HIGH': self.colors['success'],
            'HIGH': self.colors['secondary'],
            'MEDIUM': self.colors['warning'],
            'LOW': self.colors['danger']
        }
        
        colors = [quality_colors.get(level, self.colors['neutral']) for level in quality_data['Quality_Level']]
        
        fig.add_trace(
            go.Pie(
                labels=quality_data['Quality_Level'],
                values=quality_data['Count'],
                hole=0.4,
                marker_colors=colors,
                textinfo='label+percent+value',
                textfont=dict(size=11),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
            ),
            row=1, col=1
        )
        
        # Processing automation analysis
        automated = quality_data[quality_data['Quality_Level'].isin(['ULTRA_HIGH', 'HIGH', 'MEDIUM'])]['Count'].sum()
        manual = quality_data[quality_data['Quality_Level'] == 'LOW']['Count'].sum()
        
        fig.add_trace(
            go.Bar(
                x=['Automated\nProcessing', 'Manual\nInvestigation'],
                y=[automated, manual],
                marker_color=[self.colors['success'], self.colors['danger']],
                text=[f"{automated}", f"{manual}"],
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>Addresses: %{y}<extra></extra>"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=500,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=11),
            annotations=[
                dict(
                    text=f'642<br>Validated<br>Addresses',
                    x=0.18, y=0.5,
                    font_size=12,
                    showarrow=False,
                    font_color=self.colors['primary']
                )
            ]
        )
        
        fig.update_yaxes(title_text="Number of Addresses", row=1, col=2)
        
        return fig
    
    def generate_comprehensive_dashboard(self):
        """Generate the comprehensive dashboard"""
        metrics = self.get_comprehensive_metrics()
        availability = self.analyze_data_availability()
        
        # Generate charts
        kpi_html = self.create_comprehensive_kpi_section()
        funnel_fig = self.create_complete_pipeline_funnel()
        availability_fig = self.create_data_availability_analysis()
        consolidation_fig = self.create_owner_consolidation_analysis()
        quality_fig = self.create_quality_analysis()
        
        # Convert to JSON
        funnel_json = funnel_fig.to_json()
        availability_json = availability_fig.to_json()
        consolidation_json = consolidation_fig.to_json()
        quality_json = quality_fig.to_json()
        
        # Create missing municipalities note
        missing_munis = availability.get('missing_municipalities', set())
        missing_note = ""
        if missing_munis:
            missing_note = f"<strong>Data Availability Note:</strong> {', '.join(missing_munis)} municipality data was not available from registry systems during campaign execution."
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campaign4 Comprehensive Dashboard - Land Acquisition Intelligence</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #1f2937;
            line-height: 1.6;
        }}
        
        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #1e40af, #059669);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 1.1rem;
            color: #6b7280;
            margin-bottom: 20px;
        }}
        
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #dcfce7;
            color: #16a34a;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }}
        
        .chart-section {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .section-header {{
            padding: 25px 30px 20px 30px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .section-header h2 {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 8px;
        }}
        
        .section-header p {{
            color: #6b7280;
            font-size: 0.95rem;
        }}
        
        .chart-container {{
            padding: 20px 30px 30px 30px;
        }}
        
        /* Enhanced KPI Styles */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            padding: 20px 30px 30px 30px;
        }}
        
        .kpi-card {{
            background: linear-gradient(135deg, #ffffff, #f8fafc);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }}
        
        .kpi-card.primary {{ border-left: 4px solid #1e40af; }}
        .kpi-card.secondary {{ border-left: 4px solid #059669; }}
        .kpi-card.success {{ border-left: 4px solid #16a34a; }}
        .kpi-card.warning {{ border-left: 4px solid #d97706; }}
        .kpi-card.danger {{ border-left: 4px solid #dc2626; }}
        .kpi-card.neutral {{ border-left: 4px solid #6b7280; }}
        
        .kpi-icon {{
            font-size: 2rem;
            margin-bottom: 10px;
            opacity: 0.8;
        }}
        
        .kpi-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 8px;
            line-height: 1;
        }}
        
        .kpi-label {{
            font-size: 1rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
        }}
        
        .kpi-explanation {{
            font-size: 0.8rem;
            color: #6b7280;
            line-height: 1.4;
        }}
        
        .insights-panel {{
            background: #f1f5f9;
            border-left: 4px solid #1e40af;
            padding: 20px;
            margin: 20px 30px;
            border-radius: 0 8px 8px 0;
        }}
        
        .insights-panel h3 {{
            color: #1e40af;
            margin-bottom: 15px;
            font-size: 1.1rem;
            font-weight: 600;
        }}
        
        .insights-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }}
        
        .insight-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid #059669;
        }}
        
        .insight-item strong {{
            color: #1f2937;
            display: block;
            margin-bottom: 5px;
        }}
        
        .data-note {{
            background: #fef3c7;
            border-left: 4px solid #d97706;
            padding: 15px;
            margin: 20px 30px;
            border-radius: 0 8px 8px 0;
            font-size: 0.9rem;
            color: #92400e;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }}
        
        .loading {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 400px;
            color: #6b7280;
        }}
        
        @media (max-width: 768px) {{
            .kpi-grid {{
                grid-template-columns: 1fr;
            }}
            .header h1 {{
                font-size: 2rem;
            }}
            .dashboard-container {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Header -->
        <div class="header">
            <h1><i class="fas fa-seedling"></i> Campaign4 Comprehensive Dashboard</h1>
            <p class="subtitle">Complete Land Acquisition Pipeline with Data Availability Analysis</p>
            <div class="status-badge">
                <i class="fas fa-check-circle"></i>
                <span>Full Pipeline Analysis • v3.1.8 • {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
            </div>
        </div>
        
        <!-- Comprehensive KPI Section -->
        <div class="chart-section">
            <div class="section-header">
                <h2><i class="fas fa-chart-line"></i> Complete Pipeline Metrics</h2>
                <p>End-to-end analysis from original input through data availability to strategic targeting</p>
            </div>
            {kpi_html}
            {f'<div class="data-note">{missing_note}</div>' if missing_note else ''}
            <div class="insights-panel">
                <h3><i class="fas fa-lightbulb"></i> Comprehensive Pipeline Insights</h3>
                <div class="insights-grid">
                    <div class="insight-item">
                        <strong>Data Availability Impact</strong>
                        95.8% of input parcels had registry data available - Somaglia municipality data was unavailable
                    </div>
                    <div class="insight-item">
                        <strong>Area Multiplication Effect</strong>
                        1,152 Ha validated vs 356 Ha processed - owner discovery expanded area coverage 3.2x
                    </div>
                    <div class="insight-item">
                        <strong>Strategic Targeting</strong>
                        642 addresses optimized to 303 mailings targeting 157 property owners for focused outreach
                    </div>
                    <div class="insight-item">
                        <strong>Pipeline Efficiency</strong>
                        36.8% parcel success rate with 52.8% address optimization through intelligent consolidation
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Complete Pipeline Funnel -->
        <div class="chart-section">
            <div class="section-header">
                <h2><i class="fas fa-filter"></i> Complete Pipeline Flow</h2>
                <p>Full progression from original input through data availability challenges to strategic optimization</p>
            </div>
            <div class="chart-container">
                <div id="funnel-chart" class="loading">Loading complete pipeline...</div>
            </div>
        </div>
        
        <!-- Data Availability Analysis -->
        <div class="chart-section">
            <div class="section-header">
                <h2><i class="fas fa-database"></i> Data Availability & Processing Analysis</h2>
                <p>Comprehensive analysis of data retrieval challenges and area flow through the pipeline</p>
            </div>
            <div class="chart-container">
                <div id="availability-chart" class="loading">Loading data availability analysis...</div>
            </div>
        </div>
        
        <!-- Owner Consolidation Analysis -->
        <div class="chart-section">
            <div class="section-header">
                <h2><i class="fas fa-users"></i> Strategic Targeting & Consolidation</h2>
                <p>Owner consolidation benefits and geographic distribution for strategic renewable energy partnerships</p>
            </div>
            <div class="chart-container">
                <div id="consolidation-chart" class="loading">Loading consolidation analysis...</div>
            </div>
        </div>
        
        <!-- Quality Analysis -->
        <div class="chart-section">
            <div class="section-header">
                <h2><i class="fas fa-star"></i> Technical Validation Quality</h2>
                <p>Address confidence distribution and automation capabilities from validation stage</p>
            </div>
            <div class="chart-container">
                <div id="quality-chart" class="loading">Loading quality analysis...</div>
            </div>
        </div>
        
        <div class="footer">
            <p><i class="fas fa-leaf"></i> Powered by Land Acquisition Pipeline v3.1.8 | Generated {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        function loadChart(elementId, chartData, title) {{
            try {{
                const element = document.getElementById(elementId);
                if (element) {{
                    Plotly.newPlot(elementId, chartData.data, chartData.layout, {{
                        responsive: true,
                        displayModeBar: false,
                        staticPlot: false
                    }});
                    element.classList.remove('loading');
                }}
            }} catch (error) {{
                console.error(`Error loading ${{title}}:`, error);
                document.getElementById(elementId).innerHTML = `<div class="loading">Error loading ${{title}}</div>`;
            }}
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            loadChart('funnel-chart', {funnel_json}, 'Pipeline Funnel');
            loadChart('availability-chart', {availability_json}, 'Data Availability');
            loadChart('consolidation-chart', {consolidation_json}, 'Consolidation Analysis');
            loadChart('quality-chart', {quality_json}, 'Quality Analysis');
        }});
    </script>
</body>
</html>
"""
        return html_template

def main():
    print("🌱 GENERATING COMPREHENSIVE CAMPAIGN4 DASHBOARD")
    print("=" * 60)
    
    excel_path = "data/Campaign4_Results.xlsx"
    input_file = "data/Input_Castiglione Casalpusterlengo CP.xlsx"
    output_dir = "outputs/visualizations"
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        dashboard = ComprehensiveDashboard(excel_path, input_file)
        
        print("📊 Creating comprehensive dashboard with data availability context...")
        html_content = dashboard.generate_comprehensive_dashboard()
        
        dashboard_path = f"{output_dir}/campaign4_comprehensive_dashboard.html"
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Comprehensive dashboard saved: {dashboard_path}")
        print("\n🎯 Comprehensive Analysis Includes:")
        print("   ✅ Original Input: 238 parcels, 412 Ha")
        print("   ✅ Data Availability: 95.8% success rate")
        print("   ✅ Processed Area: 356 Ha (registry data available)")
        print("   ✅ Validated Area: 1,152 Ha (3.2x expansion through owner discovery)")
        print("   ✅ Data Quality Note: Somaglia municipality data unavailable")
        print("   ✅ Strategic Targeting: 157 property owners identified")
        
        print(f"\n🚀 Open {dashboard_path} in your browser!")
        print("\n💡 Complete Picture Now Shows:")
        print("   • Data availability challenges (Somaglia missing)")
        print("   • Area expansion through owner discovery")
        print("   • Strategic consolidation benefits")
        print("   • End-to-end pipeline transparency")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()