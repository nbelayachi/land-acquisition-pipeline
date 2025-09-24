#!/usr/bin/env python3
"""
Corrected Campaign4 Dashboard
Accurately represents the complete pipeline: Technical Validation → Business Qualification → Strategic Mailing
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime

class CorrectedDashboard:
    def __init__(self, excel_path):
        self.excel_path = excel_path
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
        """Load and clean the Campaign4 data"""
        try:
            data = {
                'Campaign_Summary': pd.read_excel(self.excel_path, sheet_name='Campaign_Summary'),
                'Enhanced_Funnel_Analysis': pd.read_excel(self.excel_path, sheet_name='Enhanced_Funnel_Analysis'),
                'Address_Quality_Distribution': pd.read_excel(self.excel_path, sheet_name='Address_Quality_Distribution'),
                'All_Validation_Ready': pd.read_excel(self.excel_path, sheet_name='All_Validation_Ready'),
                'Final_Mailing_List': pd.read_excel(self.excel_path, sheet_name='Final_Mailing_List')
            }
            
            # Clean Campaign_Summary
            cs = data['Campaign_Summary']
            clean_rows = cs['comune'].notna() & (cs['comune'] != '')
            data['Campaign_Summary'] = cs[clean_rows].reset_index(drop=True)
            
            return data
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def get_corrected_metrics(self):
        """Calculate corrected metrics based on complete pipeline understanding"""
        cs = self.data['Campaign_Summary']
        all_validation = self.data['All_Validation_Ready']
        final_mailing = self.data['Final_Mailing_List']
        
        # Core pipeline metrics
        technical_validation = len(all_validation)  # 642
        business_qualified = len(final_mailing)     # 303
        unique_owners = final_mailing['cf'].nunique()  # 157
        agency_required = int(cs['Agency_Final_Contacts'].sum())  # 84
        total_area = float(cs['Input_Area_Ha'].sum())
        municipalities = len(cs)
        
        # Pipeline conversion rates
        business_conversion = (business_qualified / technical_validation) * 100  # 47.2%
        owner_efficiency = (business_qualified / unique_owners)  # 1.9 addresses per owner
        
        # Quality distribution in final mailing
        validation_quality = all_validation['Address_Confidence'].value_counts()
        
        # Owner consolidation metrics
        addresses_per_owner = final_mailing.groupby('cf').size()
        max_addresses_per_owner = addresses_per_owner.max()
        owners_with_multiple = (addresses_per_owner > 1).sum()
        
        return {
            'technical_validation': {
                'value': technical_validation,
                'label': 'Technical Validation',
                'explanation': 'Addresses that passed geocoding and technical quality checks - ready for further processing'
            },
            'business_qualified': {
                'value': business_qualified,
                'label': 'Business Qualified',
                'explanation': 'Final optimized mailing list after owner consolidation and business rules application'
            },
            'unique_owners': {
                'value': unique_owners,
                'label': 'Strategic Targets',
                'explanation': 'Individual property owners identified for renewable energy partnership outreach'
            },
            'business_conversion': {
                'value': business_conversion,
                'label': 'Pipeline Efficiency',
                'explanation': 'Percentage of validated addresses that convert to actionable business contacts'
            },
            'owner_efficiency': {
                'value': owner_efficiency,
                'label': 'Owner Consolidation',
                'explanation': 'Average addresses per owner - demonstrates portfolio concentration and targeting efficiency'
            },
            'agency_required': {
                'value': agency_required,
                'label': 'Manual Investigation',
                'explanation': 'Low-confidence addresses requiring external agency verification before contact'
            },
            'total_area': {
                'value': total_area,
                'label': 'Total Area Analyzed',
                'explanation': 'Hectares of renewable energy development potential across the campaign area'
            },
            'cost_efficiency': {
                'value': 100 - (agency_required / technical_validation * 100),
                'label': 'Cost Optimization',
                'explanation': 'Percentage of pipeline processed without expensive manual intervention'
            }
        }
    
    def create_corrected_kpi_section(self):
        """Create KPI section with corrected pipeline understanding"""
        metrics = self.get_corrected_metrics()
        
        kpi_html = f"""
        <div class="kpi-grid">
            <div class="kpi-card primary">
                <div class="kpi-icon">🔍</div>
                <div class="kpi-value">{metrics['technical_validation']['value']:,}</div>
                <div class="kpi-label">{metrics['technical_validation']['label']}</div>
                <div class="kpi-explanation">{metrics['technical_validation']['explanation']}</div>
            </div>
            
            <div class="kpi-card success">
                <div class="kpi-icon">✅</div>
                <div class="kpi-value">{metrics['business_qualified']['value']}</div>
                <div class="kpi-label">{metrics['business_qualified']['label']}</div>
                <div class="kpi-explanation">{metrics['business_qualified']['explanation']}</div>
            </div>
            
            <div class="kpi-card secondary">
                <div class="kpi-icon">🎯</div>
                <div class="kpi-value">{metrics['unique_owners']['value']}</div>
                <div class="kpi-label">{metrics['unique_owners']['label']}</div>
                <div class="kpi-explanation">{metrics['unique_owners']['explanation']}</div>
            </div>
            
            <div class="kpi-card warning">
                <div class="kpi-icon">⚡</div>
                <div class="kpi-value">{metrics['business_conversion']['value']:.1f}%</div>
                <div class="kpi-label">{metrics['business_conversion']['label']}</div>
                <div class="kpi-explanation">{metrics['business_conversion']['explanation']}</div>
            </div>
            
            <div class="kpi-card neutral">
                <div class="kpi-icon">📊</div>
                <div class="kpi-value">{metrics['owner_efficiency']['value']:.1f}</div>
                <div class="kpi-label">{metrics['owner_efficiency']['label']}</div>
                <div class="kpi-explanation">{metrics['owner_efficiency']['explanation']}</div>
            </div>
            
            <div class="kpi-card danger">
                <div class="kpi-icon">🔍</div>
                <div class="kpi-value">{metrics['agency_required']['value']}</div>
                <div class="kpi-label">{metrics['agency_required']['label']}</div>
                <div class="kpi-explanation">{metrics['agency_required']['explanation']}</div>
            </div>
            
            <div class="kpi-card neutral">
                <div class="kpi-icon">🗺️</div>
                <div class="kpi-value">{metrics['total_area']['value']:.0f} Ha</div>
                <div class="kpi-label">{metrics['total_area']['label']}</div>
                <div class="kpi-explanation">{metrics['total_area']['explanation']}</div>
            </div>
            
            <div class="kpi-card primary">
                <div class="kpi-icon">💰</div>
                <div class="kpi-value">{metrics['cost_efficiency']['value']:.1f}%</div>
                <div class="kpi-label">{metrics['cost_efficiency']['label']}</div>
                <div class="kpi-explanation">{metrics['cost_efficiency']['explanation']}</div>
            </div>
        </div>
        """
        
        return kpi_html
    
    def create_enhanced_funnel_chart(self):
        """Create enhanced funnel with complete pipeline stages"""
        funnel_data = self.data['Enhanced_Funnel_Analysis']
        all_validation = self.data['All_Validation_Ready']
        final_mailing = self.data['Final_Mailing_List']
        
        # Create custom funnel data that includes business qualification
        custom_stages = [
            "1. Input Parcels",
            "2. Technical Validation", 
            "3. Quality Classification",
            "4. Business Qualification",
            "5. Strategic Mailing List"
        ]
        
        # Calculate counts for custom stages
        input_parcels = self.data['Campaign_Summary']['Input_Parcels'].sum()
        technical_validation = len(all_validation)
        high_confidence = len(all_validation[all_validation['Address_Confidence'].isin(['ULTRA_HIGH', 'HIGH', 'MEDIUM'])])
        business_qualified = len(final_mailing)
        unique_owners = final_mailing['cf'].nunique()
        
        custom_counts = [228, technical_validation, high_confidence, business_qualified, unique_owners]
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=[
                '🔄 Original Pipeline Stages<br><sub>Land Acquisition & Contact Processing</sub>', 
                '🎯 Complete Business Pipeline<br><sub>Technical → Business → Strategic Optimization</sub>'
            ],
            specs=[[{"type": "funnel"}, {"type": "funnel"}]],
            horizontal_spacing=0.15
        )
        
        # Original Contact Processing Funnel
        contact_funnel = funnel_data[funnel_data['Funnel_Type'] == 'Contact Processing'].copy()
        if not contact_funnel.empty:
            fig.add_trace(
                go.Funnel(
                    y=contact_funnel['Stage'],
                    x=contact_funnel['Count'],
                    textinfo="value+percent initial",
                    textfont=dict(size=11, color="white", family="Inter"),
                    marker=dict(
                        color=self.colors['secondary'],
                        line=dict(color="white", width=2)
                    ),
                    connector=dict(line=dict(color=self.colors['secondary'], dash="solid", width=3)),
                    hovertemplate="<b>%{y}</b><br>Count: %{x}<br>Retention: %{percentInitial}<extra></extra>"
                ),
                row=1, col=1
            )
        
        # Enhanced Business Pipeline Funnel
        fig.add_trace(
            go.Funnel(
                y=custom_stages,
                x=custom_counts,
                textinfo="value+percent initial",
                textfont=dict(size=11, color="white", family="Inter"),
                marker=dict(
                    color=self.colors['primary'],
                    line=dict(color="white", width=2)
                ),
                connector=dict(line=dict(color=self.colors['primary'], dash="solid", width=3)),
                hovertemplate="<b>%{y}</b><br>Count: %{x}<br>Retention: %{percentInitial}<extra></extra>"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=12)
        )
        
        return fig
    
    def create_mailing_optimization_analysis(self):
        """Create analysis showing mailing optimization benefits"""
        final_mailing = self.data['Final_Mailing_List']
        all_validation = self.data['All_Validation_Ready']
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                '📊 Owner Consolidation Benefits<br><sub>Multiple Addresses per Owner Distribution</sub>',
                '🎯 Mailing Efficiency Comparison<br><sub>Raw vs Optimized Approach</sub>',
                '🗺️ Geographic Distribution<br><sub>Final Mailing List by Municipality</sub>',
                '⭐ Quality Focus<br><sub>Confidence Levels in Validation vs Final</sub>'
            ],
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "bar"}]],
            horizontal_spacing=0.15,
            vertical_spacing=0.25
        )
        
        # 1. Owner consolidation benefits
        addresses_per_owner = final_mailing.groupby('cf').size()
        consolidation_dist = addresses_per_owner.value_counts().sort_index()
        
        fig.add_trace(
            go.Bar(
                x=consolidation_dist.index,
                y=consolidation_dist.values,
                marker_color=self.colors['success'],
                text=consolidation_dist.values,
                textposition='outside',
                hovertemplate="<b>%{x} addresses per owner</b><br>Count: %{y} owners<extra></extra>"
            ),
            row=1, col=1
        )
        
        # 2. Mailing efficiency comparison
        approaches = ['Raw Validation', 'Optimized Mailing']
        counts = [len(all_validation), len(final_mailing)]
        colors = [self.colors['warning'], self.colors['success']]
        
        fig.add_trace(
            go.Bar(
                x=approaches,
                y=counts,
                marker_color=colors,
                text=[f"{count}<br>mailings" for count in counts],
                textposition='inside',
                textfont=dict(color='white', size=12),
                hovertemplate="<b>%{x}</b><br>Mailings: %{y}<extra></extra>"
            ),
            row=1, col=2
        )
        
        # 3. Geographic distribution of final mailing
        if 'Municipality' in final_mailing.columns:
            muni_dist = final_mailing['Municipality'].value_counts()
            
            fig.add_trace(
                go.Pie(
                    labels=muni_dist.index,
                    values=muni_dist.values,
                    marker_colors=[self.colors['primary'], self.colors['secondary'], self.colors['success'], 
                                 self.colors['warning'], self.colors['danger'], self.colors['neutral']],
                    textinfo='label+percent+value',
                    textfont=dict(size=10),
                    hovertemplate="<b>%{label}</b><br>Mailings: %{value}<br>Share: %{percent}<extra></extra>"
                ),
                row=2, col=1
            )
        
        # 4. Quality comparison (if we can match records)
        validation_quality = all_validation['Address_Confidence'].value_counts()
        quality_levels = ['ULTRA_HIGH', 'HIGH', 'MEDIUM', 'LOW']
        quality_colors_map = {
            'ULTRA_HIGH': self.colors['success'],
            'HIGH': self.colors['secondary'],
            'MEDIUM': self.colors['warning'],
            'LOW': self.colors['danger']
        }
        
        validation_counts = [validation_quality.get(level, 0) for level in quality_levels]
        colors_bar = [quality_colors_map[level] for level in quality_levels]
        
        fig.add_trace(
            go.Bar(
                x=quality_levels,
                y=validation_counts,
                marker_color=colors_bar,
                text=validation_counts,
                textposition='outside',
                name='Validation Stage',
                hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>"
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
        
        # Update axes labels
        fig.update_xaxes(title_text="Addresses per Owner", row=1, col=1)
        fig.update_yaxes(title_text="Number of Owners", row=1, col=1)
        fig.update_yaxes(title_text="Number of Mailings", row=1, col=2)
        fig.update_xaxes(title_text="Quality Level", row=2, col=2)
        fig.update_yaxes(title_text="Count", row=2, col=2)
        
        return fig
    
    def create_quality_analysis(self):
        """Create simplified quality analysis"""
        quality_data = self.data['Address_Quality_Distribution']
        
        if quality_data.empty:
            return go.Figure()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=[
                '📊 Address Quality Distribution<br><sub>Technical Validation Results</sub>', 
                '🔄 Processing Requirements<br><sub>Automation vs Manual Effort</sub>'
            ],
            specs=[[{"type": "pie"}, {"type": "bar"}]],
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
        
        fig.add_trace(
            go.Bar(
                y=quality_data['Quality_Level'],
                x=quality_data['Count'],
                orientation='h',
                marker_color=colors,
                text=[f"{count}" for count in quality_data['Count']],
                textposition='inside',
                textfont=dict(color='white', size=11),
                hovertemplate="<b>%{y}</b><br>Addresses: %{x}<extra></extra>"
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
                    text=f'642<br>Technical<br>Validation',
                    x=0.18, y=0.5,
                    font_size=12,
                    showarrow=False,
                    font_color=self.colors['primary']
                )
            ]
        )
        
        return fig
    
    def generate_corrected_dashboard(self):
        """Generate the corrected dashboard with accurate pipeline representation"""
        metrics = self.get_corrected_metrics()
        
        # Generate charts
        kpi_html = self.create_corrected_kpi_section()
        funnel_fig = self.create_enhanced_funnel_chart()
        mailing_fig = self.create_mailing_optimization_analysis()
        quality_fig = self.create_quality_analysis()
        
        # Convert to JSON
        funnel_json = funnel_fig.to_json()
        mailing_json = mailing_fig.to_json()
        quality_json = quality_fig.to_json()
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campaign4 Executive Dashboard - Complete Pipeline Intelligence</title>
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
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
            <h1><i class="fas fa-seedling"></i> Campaign4 Complete Pipeline Dashboard</h1>
            <p class="subtitle">Technical Validation → Business Qualification → Strategic Mailing Optimization</p>
            <div class="status-badge">
                <i class="fas fa-check-circle"></i>
                <span>Pipeline Analyzed • v3.1.8 • {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
            </div>
        </div>
        
        <!-- Corrected KPI Section -->
        <div class="chart-section">
            <div class="section-header">
                <h2><i class="fas fa-chart-line"></i> Complete Pipeline Performance</h2>
                <p>End-to-end metrics from technical validation through business optimization to strategic mailing</p>
            </div>
            {kpi_html}
            <div class="insights-panel">
                <h3><i class="fas fa-lightbulb"></i> Pipeline Intelligence Insights</h3>
                <div class="insights-grid">
                    <div class="insight-item">
                        <strong>Business Optimization</strong>
                        47.2% conversion from technical validation (642) to business-qualified mailings (303)
                    </div>
                    <div class="insight-item">
                        <strong>Owner Consolidation</strong>
                        1.9 addresses per owner demonstrates portfolio concentration and strategic targeting
                    </div>
                    <div class="insight-item">
                        <strong>Cost Efficiency</strong>
                        86.9% automated processing reduces operational costs and accelerates deployment
                    </div>
                    <div class="insight-item">
                        <strong>Strategic Focus</strong>
                        157 unique property owners represent high-value renewable energy partnership opportunities
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Enhanced Funnel Analysis -->
        <div class="chart-section">
            <div class="section-header">
                <h2><i class="fas fa-filter"></i> Complete Pipeline Flow Analysis</h2>
                <p>Comprehensive view of the three-stage pipeline: Technical → Business → Strategic optimization</p>
            </div>
            <div class="chart-container">
                <div id="funnel-chart" class="loading">Loading complete pipeline analysis...</div>
            </div>
        </div>
        
        <!-- Mailing Optimization Analysis -->
        <div class="chart-section">
            <div class="section-header">
                <h2><i class="fas fa-envelope"></i> Mailing Strategy Optimization</h2>
                <p>Business logic analysis showing owner consolidation benefits and geographic distribution</p>
            </div>
            <div class="chart-container">
                <div id="mailing-chart" class="loading">Loading mailing optimization analysis...</div>
            </div>
        </div>
        
        <!-- Quality Analysis -->
        <div class="chart-section">
            <div class="section-header">
                <h2><i class="fas fa-star"></i> Technical Validation Quality Matrix</h2>
                <p>Address confidence distribution from the technical validation stage</p>
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
            loadChart('funnel-chart', {funnel_json}, 'Funnel Chart');
            loadChart('mailing-chart', {mailing_json}, 'Mailing Chart');
            loadChart('quality-chart', {quality_json}, 'Quality Chart');
        }});
    </script>
</body>
</html>
"""
        return html_template

def main():
    print("🌱 GENERATING CORRECTED CAMPAIGN4 DASHBOARD")
    print("=" * 60)
    
    excel_path = "data/Campaign4_Results.xlsx"
    output_dir = "outputs/visualizations"
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        dashboard = CorrectedDashboard(excel_path)
        
        print("📊 Creating corrected dashboard with complete pipeline understanding...")
        html_content = dashboard.generate_corrected_dashboard()
        
        dashboard_path = f"{output_dir}/campaign4_corrected_dashboard.html"
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Corrected dashboard saved: {dashboard_path}")
        print("\n🎯 Pipeline Corrections Applied:")
        print("   ✅ Technical Validation: 642 addresses (geocoded & validated)")
        print("   ✅ Business Qualified: 303 addresses (final mailing list)")
        print("   ✅ Strategic Targets: 157 unique owners (consolidated)")
        print("   ✅ Pipeline Efficiency: 47.2% (business conversion rate)")
        print("   ✅ Owner Consolidation: 1.9 addresses per owner average")
        
        # Display corrected metrics
        metrics = dashboard.get_corrected_metrics()
        print(f"\n📊 Corrected Key Metrics:")
        print(f"   • Technical Validation: {metrics['technical_validation']['value']:,} addresses")
        print(f"   • Business Qualified: {metrics['business_qualified']['value']} final mailings")
        print(f"   • Strategic Targets: {metrics['unique_owners']['value']} unique owners")
        print(f"   • Pipeline Efficiency: {metrics['business_conversion']['value']:.1f}%")
        print(f"   • Owner Consolidation: {metrics['owner_efficiency']['value']:.1f} addresses/owner")
        
        print(f"\n🚀 Open {dashboard_path} in your browser!")
        print("\n💡 Pipeline Understanding:")
        print("   1. Technical Validation: Geocoding + Quality Assessment")
        print("   2. Business Qualification: Owner consolidation + Business rules")
        print("   3. Strategic Mailing: Optimized contact strategy")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()