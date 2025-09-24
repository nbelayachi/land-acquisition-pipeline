#!/usr/bin/env python3
"""
Campaign4 Executive Dashboard for Renewable Energy Land Acquisition
===================================================================

This script creates comprehensive interactive visualizations for Campaign4 results,
designed for executive presentations to stakeholders in the renewable energy sector.

Business Context:
- Industry: Utility-scale renewable energy development (Solar PV + Battery Storage) 
- Geographic: Northern Italy (6 municipalities, 642 validated addresses)
- Key Metrics: 86.9% direct mail efficiency, 449.5 hectares processed
- Value Proposition: Automated landowner identification for 500-1000 hectare projects

Data Source: Campaign4_Results.xlsx (v3.1.8 validated)
Output: Interactive HTML dashboard + static PNG exports
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
import os
from pathlib import Path
from datetime import datetime

# Professional color scheme for renewable energy theme
COLORS = {
    'primary': '#2E8B57',      # Sea Green - renewable energy
    'secondary': '#4682B4',     # Steel Blue - technology/innovation
    'accent': '#228B22',        # Forest Green - sustainability
    'warning': '#FFB347',       # Light Orange - attention
    'success': '#32CD32',       # Lime Green - success
    'background': '#F8F9FA',    # Light Gray - clean background
    'text': '#2C3E50'          # Dark Blue-Gray - professional text
}

def load_campaign_data(data_path):
    """Load and validate Campaign4 dataset"""
    print("📊 Loading Campaign4 dataset...")
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    # Load all required sheets
    data = {}
    sheets = ['Campaign_Summary', 'Enhanced_Funnel_Analysis', 'Address_Quality_Distribution', 'All_Validation_Ready']
    
    for sheet in sheets:
        try:
            data[sheet] = pd.read_excel(data_path, sheet_name=sheet)
            print(f"   ✅ Loaded {sheet}: {len(data[sheet])} records")
        except Exception as e:
            print(f"   ❌ Failed to load {sheet}: {e}")
            
    return data

def create_executive_kpi_cards(data):
    """Create executive KPI summary cards"""
    campaign_summary = data['Campaign_Summary']
    all_validation = data['All_Validation_Ready']
    
    # Calculate key metrics
    total_addresses = len(all_validation)
    total_direct_mail = campaign_summary['Direct_Mail_Final_Contacts'].sum()
    total_agency = campaign_summary['Agency_Final_Contacts'].sum()
    total_area = campaign_summary['Input_Area_Ha'].sum()
    municipalities = len(campaign_summary)
    
    direct_mail_percentage = (total_direct_mail / total_addresses) * 100
    
    # Create KPI cards as subplots
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[
            f"Total Addresses<br><b>{total_addresses:,}</b>",
            f"Direct Mail Efficiency<br><b>{direct_mail_percentage:.1f}%</b>",
            f"Total Area Processed<br><b>{total_area:.1f} Ha</b>",
            f"Municipalities<br><b>{municipalities}</b>",
            f"Direct Mail Ready<br><b>{total_direct_mail:,}</b>",
            f"Agency Investigation<br><b>{total_agency:,}</b>"
        ],
        specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
               [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]]
    )
    
    # Add indicators (using gauge style for visual appeal)
    indicators = [
        (total_addresses, "Addresses", 1, 1),
        (direct_mail_percentage, "% Efficiency", 1, 2), 
        (total_area, "Hectares", 1, 3),
        (municipalities, "Municipalities", 2, 1),
        (total_direct_mail, "Direct Mail", 2, 2),
        (total_agency, "Agency", 2, 3)
    ]
    
    for value, title, row, col in indicators:
        fig.add_trace(
            go.Indicator(
                mode = "number",
                value = value,
                number = {"font": {"size": 40, "color": COLORS['primary']}},
                title = {"text": title, "font": {"size": 16, "color": COLORS['text']}}
            ),
            row=row, col=col
        )
    
    fig.update_layout(
        title="🎯 Campaign4 Executive Summary - Renewable Energy Land Acquisition",
        title_font_size=20,
        title_font_color=COLORS['text'],
        height=400,
        showlegend=False,
        paper_bgcolor='white',
        font=dict(family="Arial", size=12)
    )
    
    return fig

def create_funnel_visualization(data):
    """Create interactive dual funnel analysis"""
    funnel_data = data['Enhanced_Funnel_Analysis']
    
    # Separate funnels
    land_acquisition = funnel_data[funnel_data['Funnel_Type'] == 'Land Acquisition'].copy()
    contact_processing = funnel_data[funnel_data['Funnel_Type'] == 'Contact Processing'].copy()
    
    # Create dual funnel chart
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['Land Acquisition Funnel', 'Contact Processing Funnel'],
        specs=[[{"type": "funnel"}, {"type": "funnel"}]]
    )
    
    # Land Acquisition Funnel
    if not land_acquisition.empty:
        fig.add_trace(
            go.Funnel(
                y=land_acquisition['Stage'],
                x=land_acquisition['Count'],
                name="Land Acquisition",
                marker_color=COLORS['primary'],
                textinfo="value+percent initial",
                hovertemplate="<b>%{y}</b><br>" +
                            "Count: %{x}<br>" +
                            "Percentage: %{percentInitial}<br>" +
                            "<extra></extra>"
            ),
            row=1, col=1
        )
    
    # Contact Processing Funnel  
    if not contact_processing.empty:
        fig.add_trace(
            go.Funnel(
                y=contact_processing['Stage'],
                x=contact_processing['Count'],
                name="Contact Processing",
                marker_color=COLORS['secondary'],
                textinfo="value+percent initial",
                hovertemplate="<b>%{y}</b><br>" +
                            "Count: %{x}<br>" +
                            "Percentage: %{percentInitial}<br>" +
                            "<extra></extra>"
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        title="📊 Dual Funnel Analysis - Land Acquisition & Contact Processing Efficiency",
        title_font_size=18,
        height=600,
        showlegend=False,
        paper_bgcolor='white'
    )
    
    return fig

def create_municipality_comparison(data):
    """Create municipality performance comparison"""
    campaign_summary = data['Campaign_Summary']
    
    # Calculate efficiency metrics by municipality
    campaign_summary['Total_Contacts'] = campaign_summary['Direct_Mail_Final_Contacts'] + campaign_summary['Agency_Final_Contacts']
    campaign_summary['Direct_Mail_Percentage'] = (campaign_summary['Direct_Mail_Final_Contacts'] / campaign_summary['Total_Contacts']) * 100
    
    # Create grouped bar chart
    fig = go.Figure()
    
    # Direct Mail contacts
    fig.add_trace(go.Bar(
        name='Direct Mail Ready',
        x=campaign_summary['comune'],
        y=campaign_summary['Direct_Mail_Final_Contacts'],
        marker_color=COLORS['success'],
        hovertemplate="<b>%{x}</b><br>" +
                     "Direct Mail: %{y}<br>" +
                     "<extra></extra>"
    ))
    
    # Agency contacts
    fig.add_trace(go.Bar(
        name='Agency Investigation',
        x=campaign_summary['comune'],
        y=campaign_summary['Agency_Final_Contacts'],
        marker_color=COLORS['warning'],
        hovertemplate="<b>%{x}</b><br>" +
                     "Agency: %{y}<br>" +
                     "<extra></extra>"
    ))
    
    fig.update_layout(
        title="🗺️ Municipality Performance Comparison - Contact Distribution",
        title_font_size=18,
        xaxis_title="Municipality",
        yaxis_title="Number of Contacts",
        barmode='stack',
        height=500,
        paper_bgcolor='white',
        hovermode='x unified'
    )
    
    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_quality_distribution(data):
    """Create address quality distribution visualization"""
    quality_data = data['Address_Quality_Distribution']
    
    # Create donut chart for quality distribution
    fig = go.Figure(data=[go.Pie(
        labels=quality_data['Quality_Level'],
        values=quality_data['Count'],
        hole=0.4,
        marker_colors=[COLORS['success'], COLORS['primary'], COLORS['secondary'], COLORS['warning']],
        textinfo='label+percent+value',
        hovertemplate="<b>%{label}</b><br>" +
                     "Count: %{value}<br>" +
                     "Percentage: %{percent}<br>" +
                     "<extra></extra>"
    )])
    
    fig.update_layout(
        title="🎯 Address Quality Distribution - Confidence Classification",
        title_font_size=18,
        height=500,
        paper_bgcolor='white',
        annotations=[dict(text='Address<br>Quality', x=0.5, y=0.5, font_size=16, showarrow=False)]
    )
    
    return fig

def create_direct_mail_vs_agency_split(data):
    """Create Direct Mail vs Agency split visualization"""
    all_validation = data['All_Validation_Ready']
    
    # Calculate split
    direct_mail_count = len(all_validation[
        all_validation['Address_Confidence'].isin(['ULTRA_HIGH', 'HIGH', 'MEDIUM'])
    ])
    agency_count = len(all_validation[
        all_validation['Address_Confidence'] == 'LOW'
    ])
    
    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=['Direct Mail Ready', 'Agency Investigation'],
        values=[direct_mail_count, agency_count],
        hole=0.5,
        marker_colors=[COLORS['success'], COLORS['warning']],
        textinfo='label+percent+value',
        hovertemplate="<b>%{label}</b><br>" +
                     "Count: %{value}<br>" +
                     "Percentage: %{percent}<br>" +
                     "<extra></extra>"
    )])
    
    # Add center annotation
    total = direct_mail_count + agency_count
    efficiency = (direct_mail_count / total) * 100
    
    fig.update_layout(
        title="⚡ Contact Routing Efficiency - Direct Mail vs Agency Investigation",
        title_font_size=18,
        height=500,
        paper_bgcolor='white',
        annotations=[dict(
            text=f'{efficiency:.1f}%<br>Direct Mail<br>Efficiency', 
            x=0.5, y=0.5, 
            font_size=18, 
            font_color=COLORS['success'],
            showarrow=False
        )]
    )
    
    return fig

def save_visualizations(figures, output_dir):
    """Save all visualizations as HTML and PNG files"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    html_dir = output_dir / "html"
    png_dir = output_dir / "png"
    html_dir.mkdir(exist_ok=True)
    png_dir.mkdir(exist_ok=True)
    
    for name, fig in figures.items():
        # Save as HTML
        html_file = html_dir / f"{name}.html"
        fig.write_html(str(html_file))
        print(f"✅ Saved HTML: {html_file}")
        
        # Save as PNG (static export)
        try:
            png_file = png_dir / f"{name}.png"
            fig.write_image(str(png_file), width=1200, height=800, scale=2)
            print(f"✅ Saved PNG: {png_file}")
        except Exception as e:
            print(f"⚠️  PNG export failed for {name}: {e}")

def create_combined_dashboard(figures):
    """Create a single comprehensive dashboard combining all visualizations"""
    # Create subplots layout
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=[
            "Executive KPI Summary",
            "Direct Mail vs Agency Split", 
            "Municipality Performance",
            "Address Quality Distribution",
            "Land Acquisition Funnel",
            "Contact Processing Performance"
        ],
        specs=[
            [{"type": "xy", "colspan": 2}, None],
            [{"type": "xy"}, {"type": "xy"}],
            [{"type": "xy"}, {"type": "xy"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # This would require reconstructing individual chart data
    # For now, we'll create a simple summary dashboard
    
    fig.update_layout(
        title="🌱 Campaign4 Executive Dashboard - Renewable Energy Land Acquisition Intelligence",
        title_font_size=24,
        height=1200,
        showlegend=True,
        paper_bgcolor='white'
    )
    
    return fig

def main():
    """Main execution function"""
    print("="*80)
    print("🌱 CAMPAIGN4 EXECUTIVE DASHBOARD GENERATOR")
    print("Renewable Energy Land Acquisition Intelligence")
    print("="*80)
    
    # Define paths
    data_path = Path("C:/Projects/land-acquisition-pipeline/dev_tools/data_preparation/Campaign4_Results.xlsx")
    output_dir = Path("../outputs/visualizations")
    
    try:
        # Load data
        data = load_campaign_data(data_path)
        
        # Validate key metrics
        all_validation = data['All_Validation_Ready']
        total_addresses = len(all_validation)
        direct_mail_count = len(all_validation[
            all_validation['Address_Confidence'].isin(['ULTRA_HIGH', 'HIGH', 'MEDIUM'])
        ])
        agency_count = len(all_validation[all_validation['Address_Confidence'] == 'LOW'])
        
        print(f"\n🔍 DATA VALIDATION:")
        print(f"   Total Addresses: {total_addresses}")
        print(f"   Direct Mail: {direct_mail_count} ({direct_mail_count/total_addresses*100:.1f}%)")
        print(f"   Agency: {agency_count} ({agency_count/total_addresses*100:.1f}%)")
        
        # Expected values check
        if total_addresses == 642 and direct_mail_count == 558 and agency_count == 84:
            print("   ✅ All metrics match expected values!")
        else:
            print("   ⚠️  Metrics don't match expected values - please verify data")
        
        print("\n📊 CREATING VISUALIZATIONS...")
        
        # Generate all visualizations
        figures = {
            "executive_kpi_cards": create_executive_kpi_cards(data),
            "funnel_analysis": create_funnel_visualization(data),
            "municipality_comparison": create_municipality_comparison(data),
            "quality_distribution": create_quality_distribution(data),
            "direct_mail_vs_agency": create_direct_mail_vs_agency_split(data)
        }
        
        # Save all visualizations
        save_visualizations(figures, output_dir)
        
        print("\n🎯 VISUALIZATION SUMMARY:")
        print(f"   - Executive KPI Cards: Key metrics overview")
        print(f"   - Funnel Analysis: Dual funnel efficiency tracking")
        print(f"   - Municipality Comparison: Geographic performance")
        print(f"   - Quality Distribution: Address confidence breakdown")
        print(f"   - Direct Mail vs Agency: Contact routing efficiency")
        
        print(f"\n📁 OUTPUT LOCATION: {output_dir}")
        print("   - HTML files: Interactive visualizations")
        print("   - PNG files: Static exports for presentations")
        
        print("\n" + "="*80)
        print("✅ EXECUTIVE DASHBOARD GENERATION COMPLETE")
        print("Ready for stakeholder presentations!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()