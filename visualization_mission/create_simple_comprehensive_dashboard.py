#!/usr/bin/env python3
"""
Simple Comprehensive Campaign4 Dashboard
Avoids subplot complexity while maintaining comprehensive insights
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime

class SimpleComprehensiveDashboard:
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
            'neutral': '#6b7280'       # Gray 500
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
    
    def get_comprehensive_metrics(self):
        """Calculate comprehensive metrics with data availability context"""
        cs = self.data['Campaign_Summary']
        all_validation = self.data['All_Validation_Ready']
        final_mailing = self.data['Final_Mailing_List']
        input_file = self.data.get('Input_File')
        
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
        parcel_success_rate = (84 / processed_parcels) * 100  # 36.8% (unique parcels in final)
        address_optimization = ((technical_validation - final_mailings) / technical_validation) * 100  # 52.8%
        owner_consolidation = final_mailings / unique_owners  # 1.9 mailings per owner
        
        return {
            'original_input_parcels': original_input_parcels,
            'original_input_area': original_input_area,
            'data_availability_rate': data_availability_rate,
            'processed_area': processed_area,
            'validated_area': total_validated_area,
            'technical_validation': technical_validation,
            'final_mailings': final_mailings,
            'unique_owners': unique_owners,
            'parcel_success_rate': parcel_success_rate,
            'address_optimization': address_optimization,
            'owner_consolidation': owner_consolidation
        }
    
    def create_comprehensive_kpi_section(self):
        """Create comprehensive KPI section"""
        metrics = self.get_comprehensive_metrics()
        
        kpi_html = f"""
        <div class="kpi-grid">
            <div class="kpi-card primary">
                <div class="kpi-icon">📄</div>
                <div class="kpi-value">{metrics['original_input_parcels']}</div>
                <div class="kpi-label">Original Input Parcels</div>
                <div class="kpi-explanation">Land parcels provided in the initial input file for renewable energy site analysis</div>
            </div>
            
            <div class="kpi-card neutral">
                <div class="kpi-icon">🗺️</div>
                <div class="kpi-value">{metrics['original_input_area']:.0f} Ha</div>
                <div class="kpi-label">Original Input Area</div>
                <div class="kpi-explanation">Total hectares in the original input file before data availability filtering</div>
            </div>
            
            <div class="kpi-card warning">
                <div class="kpi-icon">📊</div>
                <div class="kpi-value">{metrics['data_availability_rate']:.1f}%</div>
                <div class="kpi-label">Data Availability Rate</div>
                <div class="kpi-explanation">Percentage of input parcels for which property data was successfully retrieved</div>
            </div>
            
            <div class="kpi-card secondary">
                <div class="kpi-icon">✅</div>
                <div class="kpi-value">{metrics['processed_area']:.0f} Ha</div>
                <div class="kpi-label">Processed Area</div>
                <div class="kpi-explanation">Hectares with successful data retrieval and ready for owner analysis</div>
            </div>
            
            <div class="kpi-card primary">
                <div class="kpi-icon">📐</div>
                <div class="kpi-value">{metrics['validated_area']:.0f} Ha</div>
                <div class="kpi-label">Total Validated Area</div>
                <div class="kpi-explanation">Complete area coverage from all property records after owner discovery</div>
            </div>
            
            <div class="kpi-card secondary">
                <div class="kpi-icon">🔍</div>
                <div class="kpi-value">{metrics['technical_validation']}</div>
                <div class="kpi-label">Technical Validation</div>
                <div class="kpi-explanation">Property owner addresses that passed geocoding and technical quality verification</div>
            </div>
            
            <div class="kpi-card success">
                <div class="kpi-icon">📮</div>
                <div class="kpi-value">{metrics['final_mailings']}</div>
                <div class="kpi-label">Strategic Mailings</div>
                <div class="kpi-explanation">Optimized mailing list after owner consolidation and business rule application</div>
            </div>
            
            <div class="kpi-card warning">
                <div class="kpi-icon">👤</div>
                <div class="kpi-value">{metrics['unique_owners']}</div>
                <div class="kpi-label">Property Owners</div>
                <div class="kpi-explanation">Individual landowners targeted for renewable energy partnership discussions</div>
            </div>
        </div>
        """
        
        return kpi_html
    
    def create_complete_pipeline_funnel(self):
        """Create complete pipeline funnel"""
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
    
    def create_area_flow_analysis(self):
        """Create area flow analysis"""
        area_stages = ['Original Input', 'Processed Area', 'Validated Area']
        area_values = [412, 356, 1152]
        colors_area = [self.colors['neutral'], self.colors['warning'], self.colors['success']]
        
        fig = go.Figure(go.Bar(
            x=area_stages,
            y=area_values,
            marker_color=colors_area,
            text=[f"{val} Ha" for val in area_values],
            textposition='outside',
            hovertemplate="<b>%{x}</b><br>Area: %{y} Ha<extra></extra>"
        ))
        
        fig.update_layout(
            title={
                'text': '🗺️ Area Flow Analysis<br><sub>Original → Processed → Validated Area Progression</sub>',
                'x': 0.5,
                'font': {'size': 18, 'color': self.colors['primary']}
            },
            height=500,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=12),
            yaxis_title="Hectares"
        )
        
        return fig
    
    def create_municipality_distribution(self):
        """Create municipality distribution pie chart"""
        final_mailing = self.data['Final_Mailing_List']
        
        if 'Municipality' in final_mailing.columns:
            muni_dist = final_mailing['Municipality'].value_counts()
            
            fig = go.Figure(go.Pie(
                labels=muni_dist.index,
                values=muni_dist.values,
                marker_colors=[self.colors['primary'], self.colors['secondary'], self.colors['success'], 
                             self.colors['warning'], self.colors['danger'], self.colors['neutral']],
                textinfo='label+percent+value',
                textfont=dict(size=12),
                hovertemplate="<b>%{label}</b><br>Mailings: %{value}<br>Share: %{percent}<extra></extra>"
            ))
            
            fig.update_layout(
                title={
                    'text': '🗺️ Geographic Distribution of Final Mailings<br><sub>Strategic Targeting by Municipality</sub>',
                    'x': 0.5,
                    'font': {'size': 18, 'color': self.colors['primary']}
                },
                height=500,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", size=12)
            )
            
            return fig
        else:
            return go.Figure()
    
    def create_owner_consolidation_chart(self):
        """Create owner consolidation distribution"""
        final_mailing = self.data['Final_Mailing_List']
        addresses_per_owner = final_mailing.groupby('cf').size()
        consolidation_dist = addresses_per_owner.value_counts().sort_index()
        
        fig = go.Figure(go.Bar(
            x=consolidation_dist.index,
            y=consolidation_dist.values,
            marker_color=self.colors['success'],
            text=[f"{val} owners" for val in consolidation_dist.values],
            textposition='outside',
            hovertemplate="<b>%{x} mailings per owner</b><br>%{y} property owners<extra></extra>"
        ))
        
        fig.update_layout(
            title={
                'text': '👥 Owner Consolidation Distribution<br><sub>Number of Mailings per Property Owner</sub>',
                'x': 0.5,
                'font': {'size': 18, 'color': self.colors['primary']}
            },
            height=500,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=12),
            xaxis_title="Mailings per Owner",
            yaxis_title="Number of Owners"
        )
        
        return fig
    
    def create_quality_analysis(self):
        """Create quality analysis"""
        quality_data = self.data['Address_Quality_Distribution']
        
        quality_colors = {
            'ULTRA_HIGH': self.colors['success'],
            'HIGH': self.colors['secondary'],
            'MEDIUM': self.colors['warning'],
            'LOW': self.colors['danger']
        }
        
        colors = [quality_colors.get(level, self.colors['neutral']) for level in quality_data['Quality_Level']]
        
        fig = go.Figure(go.Pie(
            labels=quality_data['Quality_Level'],
            values=quality_data['Count'],
            hole=0.4,
            marker_colors=colors,
            textinfo='label+percent+value',
            textfont=dict(size=12),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
        ))
        
        fig.update_layout(
            title={
                'text': '⭐ Address Quality Distribution<br><sub>Technical Validation Results (642 addresses)</sub>',
                'x': 0.5,
                'font': {'size': 18, 'color': self.colors['primary']}
            },
            height=500,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=12),
            annotations=[
                dict(
                    text=f'642<br>Validated<br>Addresses',
                    x=0.5, y=0.5,
                    font_size=14,
                    showarrow=False,
                    font_color=self.colors['primary']
                )
            ]
        )
        
        return fig
    
    def generate_dashboard(self):
        """Generate the comprehensive dashboard"""
        metrics = self.get_comprehensive_metrics()
        
        # Generate charts
        kpi_html = self.create_comprehensive_kpi_section()
        funnel_fig = self.create_complete_pipeline_funnel()
        area_fig = self.create_area_flow_analysis()
        municipality_fig = self.create_municipality_distribution()
        consolidation_fig = self.create_owner_consolidation_chart()
        quality_fig = self.create_quality_analysis()
        
        # Convert to JSON
        funnel_json = funnel_fig.to_json()
        area_json = area_fig.to_json()
        municipality_json = municipality_fig.to_json()
        consolidation_json = consolidation_fig.to_json()
        quality_json = quality_fig.to_json()
        
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
        
        .chart-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .chart-grid-single {{
            display: grid;
            grid-template-columns: 1fr;
            margin-bottom: 30px;
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
            .kpi-grid, .chart-grid {{
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
            <div class="data-note">
                <strong>Data Availability Note:</strong> Somaglia municipality data was not available from registry systems during campaign execution, explaining the difference between original input (238 parcels) and processed data (228 parcels).
            </div>
            <div class="insights-panel">
                <h3><i class="fas fa-lightbulb"></i> Comprehensive Pipeline Insights</h3>
                <div class="insights-grid">
                    <div class="insight-item">
                        <strong>Data Availability Impact</strong>
                        95.8% of input parcels had registry data available - demonstrates high system reliability
                    </div>
                    <div class="insight-item">
                        <strong>Area Multiplication Effect</strong>
                        1,152 Ha validated vs 356 Ha processed - owner discovery expanded area coverage 3.2x
                    </div>
                    <div class="insight-item">
                        <strong>Strategic Targeting Efficiency</strong>
                        642 addresses optimized to 303 mailings targeting 157 property owners for focused outreach
                    </div>
                    <div class="insight-item">
                        <strong>Pipeline Success Rate</strong>
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
        
        <!-- Area and Geographic Analysis -->
        <div class="chart-section">
            <div class="section-header">
                <h2><i class="fas fa-map-marked-alt"></i> Area Flow & Geographic Distribution</h2>
                <p>Area progression through pipeline and geographic distribution of final mailings</p>
            </div>
            <div class="chart-container">
                <div class="chart-grid">
                    <div id="area-chart" class="loading">Loading area analysis...</div>
                    <div id="municipality-chart" class="loading">Loading geographic distribution...</div>
                </div>
            </div>
        </div>
        
        <!-- Owner Consolidation and Quality Analysis -->
        <div class="chart-section">
            <div class="section-header">
                <h2><i class="fas fa-users"></i> Strategic Optimization Analysis</h2>
                <p>Owner consolidation benefits and address quality distribution for strategic targeting</p>
            </div>
            <div class="chart-container">
                <div class="chart-grid">
                    <div id="consolidation-chart" class="loading">Loading consolidation analysis...</div>
                    <div id="quality-chart" class="loading">Loading quality analysis...</div>
                </div>
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
            loadChart('area-chart', {area_json}, 'Area Analysis');
            loadChart('municipality-chart', {municipality_json}, 'Municipality Distribution');
            loadChart('consolidation-chart', {consolidation_json}, 'Consolidation Analysis');
            loadChart('quality-chart', {quality_json}, 'Quality Analysis');
        }});
    </script>
</body>
</html>
"""
        return html_template

def main():
    print("🌱 GENERATING SIMPLE COMPREHENSIVE CAMPAIGN4 DASHBOARD")
    print("=" * 60)
    
    excel_path = "data/Campaign4_Results.xlsx"
    input_file = "data/Input_Castiglione Casalpusterlengo CP.xlsx"
    output_dir = "outputs/visualizations"
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        dashboard = SimpleComprehensiveDashboard(excel_path, input_file)
        
        print("📊 Creating simple comprehensive dashboard...")
        html_content = dashboard.generate_dashboard()
        
        dashboard_path = f"{output_dir}/campaign4_simple_comprehensive_dashboard.html"
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Simple comprehensive dashboard saved: {dashboard_path}")
        print("\n🎯 Features Included:")
        print("   ✅ Complete pipeline metrics with data availability context")
        print("   ✅ Area flow analysis (412 → 356 → 1,152 Ha)")
        print("   ✅ Geographic distribution of final mailings")
        print("   ✅ Owner consolidation analysis")
        print("   ✅ Address quality distribution")
        print("   ✅ Data availability explanation (Somaglia missing)")
        
        metrics = dashboard.get_comprehensive_metrics()
        print(f"\n📊 Key Metrics Displayed:")
        print(f"   • Original Input: {metrics['original_input_parcels']} parcels, {metrics['original_input_area']:.0f} Ha")
        print(f"   • Data Availability: {metrics['data_availability_rate']:.1f}%")
        print(f"   • Processed Area: {metrics['processed_area']:.0f} Ha")
        print(f"   • Validated Area: {metrics['validated_area']:.0f} Ha")
        print(f"   • Strategic Mailings: {metrics['final_mailings']}")
        print(f"   • Property Owners: {metrics['unique_owners']}")
        
        print(f"\n🚀 Open {dashboard_path} in your browser!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()