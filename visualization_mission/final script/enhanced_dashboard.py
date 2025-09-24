#!/usr/bin/env python3
"""
Enhanced Campaign Dashboard Generator with Advanced Analytics
============================================================
CODE ID: ENH-DASH-2025-001
VERSION: 2.0

ENHANCEMENT IMPLEMENTATIONS:
- ENH-QW-001: Enhanced dual funnel with efficiency indicators
- ENH-QW-002: Improved geographic distribution with area data  
- ENH-P3-001: Enhanced Funnel Analysis data processor
- ENH-P3-002: Sankey process flow diagram
- ENH-P3-003: Process efficiency metrics dashboard
- ENH-P4-001: Ownership complexity analyzer
- ENH-P4-003: B2B/B2C segmentation analysis

This script extends the original dashboard.py with advanced visualizations
while maintaining all existing functionality and data validation.
"""

import pandas as pd
import re
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
import numpy as np
import os

class EnhancedDashboardGenerator:
    """
    Enhanced dashboard generator with advanced analytics capabilities
    """
    def __init__(self, excel_path, input_file_path):
        self.excel_path = excel_path
        self.input_file_path = input_file_path
        self.data = self.load_data()
        self.colors = {
            'primary': '#1e40af', 'secondary': '#059669', 'success': '#16a34a',
            'warning': '#d97706', 'danger': '#dc2626', 'neutral': '#6b7280',
            'info': '#0ea5e9', 'purple': '#8b5cf6', 'pink': '#ec4899'
        }

    def load_data(self):
        """Load all necessary data sheets from the Excel files."""
        try:
            data = {}
            print("-> Loading all necessary data from Excel files...")
            # Original data sources
            data['Input_File'] = pd.read_excel(self.input_file_path, sheet_name='Sheet1')
            data['All_Raw_Data'] = pd.read_excel(self.excel_path, sheet_name='All_Raw_Data')
            data['Final_Mailing_List'] = pd.read_excel(self.excel_path, sheet_name='Final_Mailing_List')
            data['All_Validation_Ready'] = pd.read_excel(self.excel_path, sheet_name='All_Validation_Ready')
            data['Address_Quality_Distribution'] = pd.read_excel(self.excel_path, sheet_name='Address_Quality_Distribution')
            
            # ENH-P3-001: Enhanced funnel analysis data
            data['Enhanced_Funnel_Analysis'] = pd.read_excel(self.excel_path, sheet_name='Enhanced_Funnel_Analysis')
            
            # ENH-P4-001: Ownership complexity data
            data['Owners_By_Parcel'] = pd.read_excel(self.excel_path, sheet_name='Owners_By_Parcel')
            
            # ENH-P4-003: B2B/B2C segmentation data
            data['All_Companies_Found'] = pd.read_excel(self.excel_path, sheet_name='All_Companies_Found')
            data['Campaign_Summary'] = pd.read_excel(self.excel_path, sheet_name='Campaign_Summary')
            
            # Sanitize column names for consistency
            for key in data:
                data[key].columns = [str(c).strip() for c in data[key].columns]

            print("-> Enhanced data loading complete.")
            return data
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise

    def get_correct_unique_parcels(self, source_df, parcel_id_cols):
        """Helper function to get unique parcels from a DataFrame."""
        df = source_df.dropna(subset=parcel_id_cols)
        return df[parcel_id_cols].drop_duplicates().shape[0]

    def get_final_unique_parcels_from_mailing(self):
        """Parse unique parcels from the 'Parcels' column."""
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
        """Calculate all metrics with validated logic from raw data."""
        print("-> Calculating all metrics with validated logic from raw data...")
        
        input_df = self.data['Input_File'].copy()
        input_df['Area'] = input_df['Area'].astype(str).str.replace(',', '.').astype(float)
        
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

    # ENH-P3-001: Enhanced Funnel Analysis data processor
    def process_enhanced_funnel_data(self):
        """
        Process Enhanced_Funnel_Analysis sheet into Sankey-ready format
        Returns nodes and links for Sankey diagram
        """
        print("-> Processing Enhanced Funnel Analysis data for Sankey diagram...")
        
        funnel_df = self.data['Enhanced_Funnel_Analysis'].copy()
        
        # Create nodes from stages
        nodes = []
        links = []
        node_id = 0
        node_mapping = {}
        
        # Process each funnel type separately
        for funnel_type in funnel_df['Funnel_Type'].unique():
            funnel_data = funnel_df[funnel_df['Funnel_Type'] == funnel_type].sort_values('Stage')
            
            prev_count = None
            prev_node_id = None
            
            for _, row in funnel_data.iterrows():
                stage_name = f"{funnel_type}: {row['Stage']}"
                
                # Add node
                nodes.append({
                    'id': node_id,
                    'label': stage_name,
                    'count': row['Count'],
                    'hectares': row['Hectares'],
                    'conversion_rate': row.get('Conversion / Multiplier', 0),
                    'retention_rate': row['Retention_Rate'],
                    'funnel_type': funnel_type
                })
                
                node_mapping[stage_name] = node_id
                
                # Add link from previous stage
                if prev_node_id is not None:
                    links.append({
                        'source': prev_node_id,
                        'target': node_id,
                        'value': row['Count'],
                        'conversion_rate': row.get('Stage_Conversion_Rate', 0)
                    })
                
                prev_count = row['Count']
                prev_node_id = node_id
                node_id += 1
        
        return {
            'nodes': nodes,
            'links': links,
            'funnel_summary': funnel_df.groupby('Funnel_Type')['Count'].agg(['first', 'last', 'min', 'max']).to_dict()
        }

    # ENH-P4-001: Ownership complexity analyzer
    def analyze_ownership_complexity(self):
        """
        Analyze ownership complexity patterns from Owners_By_Parcel data
        """
        print("-> Analyzing ownership complexity patterns...")
        
        owners_df = self.data['Owners_By_Parcel'].copy()
        
        # Calculate complexity metrics
        complexity_analysis = {
            'total_parcels': len(owners_df),
            'single_owner_parcels': len(owners_df[owners_df['total_owners'] == 1]),
            'multi_owner_parcels': len(owners_df[owners_df['total_owners'] > 1]),
            'max_owners_per_parcel': owners_df['total_owners'].max(),
            'avg_owners_per_parcel': owners_df['total_owners'].mean(),
            'ownership_distribution': owners_df['total_owners'].value_counts().sort_index(),
            'complexity_by_municipality': owners_df.groupby('comune')['total_owners'].agg(['count', 'mean', 'max']),
            'area_by_complexity': owners_df.groupby('total_owners')['parcel_area_ha'].sum()
        }
        
        # Calculate complexity score (weighted by area and owner count)
        owners_df['complexity_score'] = (
            owners_df['total_owners'] * 0.7 + 
            (owners_df['parcel_area_ha'] / owners_df['parcel_area_ha'].max()) * 0.3
        )
        
        complexity_analysis['complexity_scores'] = owners_df[['comune', 'total_owners', 'parcel_area_ha', 'complexity_score']]
        
        return complexity_analysis

    # ENH-P4-003: B2B/B2C segmentation analysis
    def create_b2b_b2c_analysis(self):
        """
        Create B2B/B2C segmentation analysis from company and individual data
        Uses proper unique parcel logic: comune+foglio+particella combo
        """
        print("-> Creating B2B/B2C segmentation analysis with corrected area calculations...")
        
        companies_df = self.data['All_Companies_Found'].copy()
        validation_df = self.data['All_Validation_Ready'].copy()
        input_df = self.data['Input_File'].copy()
        
        # Create unique parcel identifiers for proper area calculation
        companies_df['parcel_id'] = companies_df['comune_input'].astype(str) + '-' + companies_df['foglio_input'].astype(str) + '-' + companies_df['particella_input'].astype(str)
        validation_df['parcel_id'] = validation_df['comune_input'].astype(str) + '-' + validation_df['foglio_input'].astype(str) + '-' + validation_df['particella_input'].astype(str)
        input_df['parcel_id'] = input_df['comune'].astype(str) + '-' + input_df['foglio'].astype(str) + '-' + input_df['particella'].astype(str)
        
        # Get unique B2B parcels and calculate area from input file
        unique_b2b_parcels = companies_df['parcel_id'].unique()
        b2b_area_df = input_df[input_df['parcel_id'].isin(unique_b2b_parcels)]
        
        # Get unique B2C parcels (individuals) and calculate area from input file
        individual_validation = validation_df[validation_df['Tipo_Proprietario'] == 'Privato']
        unique_b2c_parcels = individual_validation['parcel_id'].unique()
        b2c_area_df = input_df[input_df['parcel_id'].isin(unique_b2c_parcels)]
        
        # B2B Analysis (Companies) - using unique parcels
        b2b_analysis = {
            'total_companies': len(companies_df['cf'].unique()),  # Unique companies
            'companies_with_pec': len(companies_df[companies_df['pec_email'].notna()]['cf'].unique()),
            'b2b_area_total': b2b_area_df['Area'].sum(),
            'b2b_parcels_total': len(unique_b2b_parcels),
            'companies_by_municipality': companies_df.groupby('comune_input')['cf'].nunique(),
            'avg_company_parcel_size': b2b_area_df['Area'].mean() if len(b2b_area_df) > 0 else 0,
            'pec_availability_rate': (len(companies_df[companies_df['pec_email'].notna()]['cf'].unique()) / len(companies_df['cf'].unique())) * 100 if len(companies_df) > 0 else 0
        }
        
        # B2C Analysis (Individuals) - using unique parcels
        b2c_analysis = {
            'total_individuals': len(individual_validation['cf'].unique()),
            'b2c_area_total': b2c_area_df['Area'].sum(),
            'b2c_parcels_total': len(unique_b2c_parcels),
            'individuals_by_municipality': individual_validation.groupby('comune_input')['cf'].nunique(),
            'avg_individual_parcel_size': b2c_area_df['Area'].mean() if len(b2c_area_df) > 0 else 0,
            'address_quality_distribution': individual_validation['Address_Confidence'].value_counts()
        }
        
        # Comparative Analysis
        comparative_analysis = {
            'b2b_vs_b2c_ratio': len(unique_b2b_parcels) / len(unique_b2c_parcels) if len(unique_b2c_parcels) > 0 else 0,
            'area_distribution': {
                'B2B': b2b_analysis['b2b_area_total'],
                'B2C': b2c_analysis['b2c_area_total']
            },
            'avg_parcel_size_comparison': {
                'B2B': b2b_analysis['avg_company_parcel_size'],
                'B2C': b2c_analysis['avg_individual_parcel_size']
            }
        }
        
        return {
            'b2b': b2b_analysis,
            'b2c': b2c_analysis,
            'comparative': comparative_analysis
        }

    # ENH-QW-001: Enhanced dual funnel with efficiency indicators
    def create_enhanced_dual_funnel(self, metrics):
        """
        Create enhanced dual funnel with efficiency indicators and conversion rates
        """
        print("-> Creating enhanced dual funnel with efficiency indicators...")
        
        # Calculate efficiency indicators - Fixed redundancy with Raw Data step
        raw_data_count = len(self.data['All_Raw_Data'])
        technical_stages = ["Raw Data Retrieved", "Owner Records Validated", "Strategic Mailings"]
        technical_values = [raw_data_count,
                          metrics['validation']['technical_validation'], 
                          metrics['mailing']['strategic_mailings']]
        
        business_stages = ["Original Input Parcels", "Data Available Parcels", "Final Unique Parcels", "Final Property Owners"]
        business_values = [metrics['input']['total_parcels'], 
                          metrics['input']['data_available_parcels'], 
                          metrics['mailing']['unique_parcels'], 
                          metrics['mailing']['property_owners']]
        
        # Calculate conversion rates for hover information
        technical_conversions = []
        business_conversions = []
        
        for i in range(len(technical_values)):
            if i == 0:
                technical_conversions.append("100.0%")
            else:
                rate = (technical_values[i] / technical_values[0]) * 100
                technical_conversions.append(f"{rate:.1f}%")
        
        for i in range(len(business_values)):
            if i == 0:
                business_conversions.append("100.0%")
            else:
                rate = (business_values[i] / business_values[0]) * 100
                business_conversions.append(f"{rate:.1f}%")
        
        # Create enhanced funnel with custom hover templates
        fig_funnel = make_subplots(
            rows=1, cols=2,
            subplot_titles=[
                '<b>Technical Processing Funnel</b><br><sub>Record Filtering & Optimization</sub>', 
                '<b>Business Qualification Funnel</b><br><sub>Strategic Asset Targeting</sub>'
            ],
            specs=[[{"type": "funnel"}, {"type": "funnel"}]], 
            horizontal_spacing=0.1
        )
        
        # Enhanced technical funnel with efficiency indicators
        fig_funnel.add_trace(go.Funnel(
            y=technical_stages,
            x=technical_values,
            textinfo="value+percent initial",
            texttemplate="<b>%{value}</b><br>%{percentInitial}<br><i>Efficiency: %{customdata}</i>",
            customdata=technical_conversions,
            marker={"color": self.colors['secondary'], "line": {"width": 2, "color": "white"}},
            connector={"line": {"color": self.colors['secondary'], "dash": "solid", "width": 3}},
            hovertemplate="<b>%{y}</b><br>Count: %{value}<br>Retention: %{customdata}<br>Efficiency Score: %{percentInitial}<extra></extra>"
        ), row=1, col=1)
        
        # Enhanced business funnel with efficiency indicators  
        fig_funnel.add_trace(go.Funnel(
            y=business_stages,
            x=business_values,
            textinfo="value+percent initial",
            texttemplate="<b>%{value}</b><br>%{percentInitial}<br><i>Efficiency: %{customdata}</i>",
            customdata=business_conversions,
            marker={"color": self.colors['primary'], "line": {"width": 2, "color": "white"}},
            connector={"line": {"color": self.colors['primary'], "dash": "solid", "width": 3}},
            hovertemplate="<b>%{y}</b><br>Count: %{value}<br>Retention: %{customdata}<br>Efficiency Score: %{percentInitial}<extra></extra>"
        ), row=1, col=2)
        
        fig_funnel.update_layout(
            showlegend=False, 
            height=500, 
            margin=dict(t=100, b=20, l=20, r=20),
            title="Enhanced Process Flow Analysis with Efficiency Indicators"
        )
        
        return fig_funnel

    # ENH-QW-002: Enhanced geographic distribution with area data
    def create_enhanced_geographic_chart(self, metrics):
        """
        Create enhanced geographic distribution with area information and hover details
        """
        print("-> Creating enhanced geographic chart with area data...")
        
        # Get area data by municipality from Campaign_Summary
        campaign_summary = self.data['Campaign_Summary']
        geo_df = metrics['geographic_distribution'].copy()
        
        # Merge with area data
        area_data = campaign_summary.groupby('comune').agg({
            'Direct_Mail_Final_Area_Ha': 'sum',
            'Agency_Final_Area_Ha': 'sum', 
            'Input_Area_Ha': 'sum'
        }).reset_index()
        area_data['Total_Final_Area'] = area_data['Direct_Mail_Final_Area_Ha'] + area_data['Agency_Final_Area_Ha']
        
        # Merge geographic and area data
        enhanced_geo = pd.merge(geo_df, area_data, left_on='Municipality', right_on='comune', how='left')
        enhanced_geo['Total_Final_Area'] = enhanced_geo['Total_Final_Area'].fillna(0)
        
        # Create enhanced pie chart with area information
        fig_geo = go.Figure(go.Pie(
            labels=[f"{row['Municipality']}<br>{row['Total_Final_Area']:.1f} Ha" for _, row in enhanced_geo.iterrows()],
            values=enhanced_geo['Parcel Count'],
            textinfo='label+percent+value',
            texttemplate="<b>%{label}</b><br>%{value} parcels (%{percent})",
            hovertemplate="<b>%{label}</b><br>" +
                         "Parcels: %{value}<br>" +
                         "Percentage: %{percent}<br>" +
                         "Area: %{customdata:.1f} Ha<br>" +
                         "<extra></extra>",
            customdata=enhanced_geo['Total_Final_Area'],
            hole=.4,
            marker=dict(
                colors=[self.colors['primary'], self.colors['secondary'], self.colors['success'], 
                       self.colors['warning'], self.colors['info'], self.colors['purple']],
                line=dict(color='white', width=2)
            )
        ))
        
        fig_geo.update_layout(
            title_text='Enhanced Geographic Distribution<br><sub>Parcels and Area by Municipality</sub>',
            showlegend=True,
            height=500,  # Reduced height - was too big
            legend=dict(
                orientation="v", 
                yanchor="middle", 
                y=0.5, 
                xanchor="left", 
                x=1.05,  # Position legend to the right
                font=dict(size=10)
            ),
            margin=dict(t=60, b=20, l=20, r=150),  # More right margin for legend
            annotations=[dict(
                text=f"{enhanced_geo['Parcel Count'].sum()}<br>Total Parcels<br>{enhanced_geo['Total_Final_Area'].sum():.1f} Ha<br>Final Area",
                x=0.5, y=0.5, font_size=12, showarrow=False
            )]
        )
        
        return fig_geo


    # ENH-P3-003: Process efficiency metrics dashboard
    def create_efficiency_metrics(self):
        """
        Create process efficiency metrics with KPIs and recommendations
        """
        print("-> Creating process efficiency metrics...")
        
        funnel_df = self.data['Enhanced_Funnel_Analysis']
        
        # Calculate efficiency metrics
        efficiency_metrics = {
            'overall_conversion_rate': (funnel_df['Count'].iloc[-1] / funnel_df['Count'].iloc[0]) * 100,
            'bottleneck_stage': funnel_df.loc[funnel_df['Stage_Conversion_Rate'].idxmin(), 'Stage'] if 'Stage_Conversion_Rate' in funnel_df.columns else 'N/A',
            'automation_coverage': (len(funnel_df[funnel_df['Automation_Level'] == 'Fully-Auto']) / len(funnel_df)) * 100,
            'manual_stages': funnel_df[funnel_df['Automation_Level'] == 'Manual']['Stage'].tolist(),
            'stage_efficiencies': funnel_df.set_index('Stage')['Stage_Conversion_Rate'].to_dict() if 'Stage_Conversion_Rate' in funnel_df.columns else {}
        }
        
        return efficiency_metrics

    def create_ownership_complexity_charts(self, complexity_data):
        """
        Create ownership complexity visualization with clearer categorization
        """
        print("-> Creating ownership complexity charts...")
        
        ownership_dist = complexity_data['ownership_distribution']
        
        # Create clearer categories based on business complexity
        complexity_categories = {
            'Simple (1 owner)': 0,
            'Moderate (2 owners)': 0, 
            'Complex (3-5 owners)': 0,
            'Very Complex (6+ owners)': 0
        }
        
        # Categorize parcels by complexity level
        for owners, count in ownership_dist.items():
            if owners == 1:
                complexity_categories['Simple (1 owner)'] = count
            elif owners == 2:
                complexity_categories['Moderate (2 owners)'] = count
            elif 3 <= owners <= 5:
                complexity_categories['Complex (3-5 owners)'] += count
            else:  # 6+ owners
                complexity_categories['Very Complex (6+ owners)'] += count
        
        # Remove empty categories
        complexity_categories = {k: v for k, v in complexity_categories.items() if v > 0}
        
        # Create clearer labels with business context
        labels = []
        colors = []
        values = []
        
        for category, count in complexity_categories.items():
            percentage = (count / complexity_data['total_parcels']) * 100
            
            if 'Simple' in category:
                labels.append(f"Simple Ownership<br>{count} parcels ({percentage:.1f}%)<br>Single landowner")
                colors.append(self.colors['success'])
                business_note = "Quick processing"
            elif 'Moderate' in category:
                labels.append(f"Moderate Complexity<br>{count} parcels ({percentage:.1f}%)<br>Two co-owners")
                colors.append(self.colors['warning'])
                business_note = "Standard negotiation"
            elif 'Complex' in category:
                labels.append(f"Complex Ownership<br>{count} parcels ({percentage:.1f}%)<br>Multiple stakeholders")
                colors.append(self.colors['danger'])
                business_note = "Extended negotiation"
            else:  # Very Complex
                labels.append(f"Very Complex<br>{count} parcels ({percentage:.1f}%)<br>Many stakeholders")
                colors.append('#8B0000')  # Dark red for highest complexity
                business_note = "Specialized handling"
            
            values.append(count)
        
        fig_ownership = go.Figure(go.Pie(
            labels=labels,
            values=values,
            textinfo='label',
            textposition='auto',
            hole=.35,
            marker=dict(colors=colors, line=dict(color='white', width=2)),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>",
            textfont=dict(size=11)
        ))
        
        fig_ownership.update_layout(
            title='Ownership Complexity Analysis<br><sub>Business Processing Categories</sub>',
            showlegend=False,
            height=500,  # Reasonable height
            margin=dict(t=80, b=20, l=20, r=20),
            annotations=[dict(
                text=f"<b>{complexity_data['total_parcels']}</b><br>Total Parcels<br><br><b>{complexity_data['avg_owners_per_parcel']:.1f}</b><br>Avg owners<br>per parcel<br><br><b>{complexity_data['max_owners_per_parcel']}</b><br>Max owners<br>(most complex)",
                x=0.5, y=0.5, font_size=10, showarrow=False,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1
            )]
        )
        
        return fig_ownership

    def create_b2b_b2c_charts(self, segmentation_data):
        """
        Create B2B/B2C segmentation visualization charts
        """
        print("-> Creating B2B/B2C segmentation charts...")
        
        b2b_data = segmentation_data['b2b']
        b2c_data = segmentation_data['b2c']
        comparative = segmentation_data['comparative']
        
        # B2B vs B2C comparison
        fig_segment = go.Figure(go.Pie(
            labels=['B2B (Corporate)', 'B2C (Individual)'],
            values=[b2b_data['b2b_area_total'], b2c_data['b2c_area_total']],
            textinfo='label+percent+value',
            texttemplate="<b>%{label}</b><br>%{value:.1f} Ha<br>%{percent}",
            hole=.4,
            marker_colors=[self.colors['purple'], self.colors['info']]
        ))
        
        fig_segment.update_layout(
            title_text='B2B vs B2C Area Distribution<br><sub>Corporate vs Individual Ownership</sub>',
            annotations=[dict(
                text=f"Total<br>{b2b_data['b2b_area_total'] + b2c_data['b2c_area_total']:.1f} Ha",
                x=0.5, y=0.5, font_size=14, showarrow=False
            )]
        )
        
        return fig_segment

    def create_municipality_performance_table(self):
        """
        Create Municipality Performance Summary table for executives
        """
        print("-> Creating Municipality Performance Summary table...")
        
        campaign_summary = self.data['Campaign_Summary'].copy()
        
        # Calculate performance metrics
        campaign_summary['Success_Rate'] = (campaign_summary['After_API_Parcels'] / campaign_summary['Input_Parcels'] * 100).round(1)
        campaign_summary['Total_Final_Area'] = campaign_summary['Direct_Mail_Final_Area_Ha'] + campaign_summary['Agency_Final_Area_Ha']
        campaign_summary['Direct_Mail_Percentage'] = (campaign_summary['Direct_Mail_Final_Contacts'] / (campaign_summary['Direct_Mail_Final_Contacts'] + campaign_summary['Agency_Final_Contacts']) * 100).round(1)
        
        # Prepare table data (removed efficiency column)
        table_data = campaign_summary[['comune', 'Input_Parcels', 'Success_Rate', 'Total_Final_Area', 'Direct_Mail_Percentage']].copy()
        table_data = table_data.sort_values('Total_Final_Area', ascending=False)
        
        # Create Plotly table
        fig_municipality_table = go.Figure(data=[go.Table(
            columnwidth=[150, 80, 100, 100, 120],
            header=dict(
                values=['<b>Municipality</b>', '<b>Parcels</b>', '<b>Success Rate</b>', '<b>Area (Ha)</b>', '<b>Direct Mail %</b>'],
                fill_color='#1e40af',
                font=dict(color='white', size=12),
                height=35,
                align=['left', 'center', 'center', 'center', 'center']
            ),
            cells=dict(
                values=[
                    table_data['comune'],
                    table_data['Input_Parcels'],
                    [f"{rate}%" for rate in table_data['Success_Rate']],
                    [f"{area:.1f}" for area in table_data['Total_Final_Area']],
                    [f"{pct}%" for pct in table_data['Direct_Mail_Percentage']]
                ],
                fill_color=[
                    'white',
                    'white', 
                    ['#dcfce7' if rate >= 95 else '#fef3c7' if rate >= 90 else '#fee2e2' for rate in table_data['Success_Rate']],
                    ['#dcfce7' if area >= 100 else '#fef3c7' if area >= 50 else '#fee2e2' for area in table_data['Total_Final_Area']],
                    ['#dcfce7' if pct >= 85 else '#fef3c7' if pct >= 75 else '#fee2e2' for pct in table_data['Direct_Mail_Percentage']]
                ],
                font=dict(size=11),
                height=30,
                align=['left', 'center', 'center', 'center', 'center']
            )
        )])
        
        fig_municipality_table.update_layout(
            title='📊 Municipality Performance Summary<br><sub>Portfolio Analysis for Strategic Resource Allocation</sub>',
            height=300,
            margin=dict(t=80, b=20, l=20, r=20)
        )
        
        return fig_municipality_table

    def create_corporate_opportunities_table(self):
        """
        Create Corporate Opportunities (B2B) table for executives  
        """
        print("-> Creating Corporate Opportunities B2B table...")
        
        companies_df = self.data['All_Companies_Found'].copy()
        input_df = self.data['Input_File'].copy()
        
        # Create unique parcel identifiers and calculate areas
        companies_df['parcel_id'] = companies_df['comune_input'].astype(str) + '-' + companies_df['foglio_input'].astype(str) + '-' + companies_df['particella_input'].astype(str)
        input_df['parcel_id'] = input_df['comune'].astype(str) + '-' + input_df['foglio'].astype(str) + '-' + input_df['particella'].astype(str)
        
        # Aggregate by company
        company_summary = companies_df.groupby(['denominazione', 'pec_email']).agg({
            'parcel_id': 'nunique',
            'comune_input': 'first'
        }).reset_index()
        company_summary.columns = ['Company', 'PEC_Email', 'Parcel_Count', 'Municipality']
        
        # Calculate total area per company
        area_by_company = []
        for _, row in company_summary.iterrows():
            company_parcels = companies_df[companies_df['denominazione'] == row['Company']]['parcel_id'].unique()
            total_area = input_df[input_df['parcel_id'].isin(company_parcels)]['Area'].sum()
            area_by_company.append(total_area)
        
        company_summary['Total_Area'] = area_by_company
        
        company_summary['PEC_Status'] = company_summary['PEC_Email'].apply(lambda x: "✅ Available" if pd.notna(x) else "❌ Missing")
        
        # Clean company names for display
        company_summary['Company_Short'] = company_summary['Company'].str.replace(' con sede in.*', '', regex=True).str[:30]
        
        # Sort by area (highest value first)
        company_summary = company_summary.sort_values('Total_Area', ascending=False)
        
        # Take top 10 for executive view
        top_companies = company_summary.head(10)
        
        # Create Plotly table (removed priority column)
        fig_corporate_table = go.Figure(data=[go.Table(
            columnwidth=[180, 80, 100, 120, 120],
            header=dict(
                values=['<b>Company</b>', '<b>Parcels</b>', '<b>Area (Ha)</b>', '<b>PEC Status</b>', '<b>Municipality</b>'],
                fill_color='#059669',
                font=dict(color='white', size=12),
                height=35,
                align=['left', 'center', 'center', 'center', 'center']
            ),
            cells=dict(
                values=[
                    top_companies['Company_Short'],
                    top_companies['Parcel_Count'],
                    [f"{area:.1f}" for area in top_companies['Total_Area']],
                    top_companies['PEC_Status'],
                    top_companies['Municipality']
                ],
                fill_color=[
                    'white',
                    'white',
                    ['#dcfce7' if area >= 10 else '#fef3c7' if area >= 5 else 'white' for area in top_companies['Total_Area']],
                    ['#dcfce7' if '✅' in status else '#fee2e2' for status in top_companies['PEC_Status']],
                    'white'
                ],
                font=dict(size=11),
                height=30,
                align=['left', 'center', 'center', 'center', 'center']
            )
        )])
        
        fig_corporate_table.update_layout(
            title='🏢 Corporate Opportunities (B2B)<br><sub>High-Value Business Development Targets</sub>',
            height=350,
            margin=dict(t=80, b=20, l=20, r=20)
        )
        
        return fig_corporate_table

    def create_plotly_dashboard(self):
        """Generate the comprehensive enhanced HTML dashboard using Plotly."""
        print("-> Generating enhanced Plotly HTML dashboard...")
        metrics = self.calculate_validated_metrics()

        pio.templates.default = "plotly_white"

        # ENH-QW-001: Enhanced dual funnel
        fig_funnel = self.create_enhanced_dual_funnel(metrics)
        
        # ENH-QW-002: Enhanced geographic distribution (increased height)
        fig_geo = self.create_enhanced_geographic_chart(metrics)
        
        # ENH-P4-001: Ownership complexity analysis
        complexity_data = self.analyze_ownership_complexity()
        fig_ownership = self.create_ownership_complexity_charts(complexity_data)
        
        # ENH-P4-003: B2B/B2C segmentation analysis
        segmentation_data = self.create_b2b_b2c_analysis()
        fig_segment = self.create_b2b_b2c_charts(segmentation_data)
        
        # ENH-P3-003: Process efficiency metrics
        efficiency_data = self.create_efficiency_metrics()
        
        # Executive Tables
        fig_municipality_table = self.create_municipality_performance_table()
        fig_corporate_table = self.create_corporate_opportunities_table()

        # Enhanced area flow analysis with delta information
        area_stages = ['Original Input Area', 'Processed Area', 'Final Targeted Area']
        area_values = [metrics['input']['total_area'], metrics['validation']['processed_area'], metrics['mailing']['final_area']]
        
        # Calculate deltas and parcel loss information
        input_to_processed_delta = metrics['validation']['processed_area'] - metrics['input']['total_area']
        processed_to_final_delta = metrics['mailing']['final_area'] - metrics['validation']['processed_area']
        lost_parcels = metrics['input']['total_parcels'] - metrics['input']['data_available_parcels']
        
        fig_area = go.Figure()
        
        # Main bars
        fig_area.add_trace(go.Bar(
            x=area_stages, 
            y=area_values,
            text=[f"{v:.0f} Ha" for v in area_values], 
            textposition='auto',
            marker_color=[self.colors['neutral'], self.colors['warning'], self.colors['success']],
            name="Area (Ha)",
            hovertemplate="<b>%{x}</b><br>Area: %{y:.1f} Ha<br>" + 
                         "<extra></extra>"
        ))
        
        # Add delta indicators
        if input_to_processed_delta < 0:
            fig_area.add_annotation(
                x=0.5, y=max(area_values) * 0.85,
                text=f"Δ {input_to_processed_delta:.0f} Ha<br>({lost_parcels} parcels lost<br>due to data issues)",
                showarrow=True, arrowhead=2, arrowcolor=self.colors['danger'],
                bgcolor="rgba(220, 38, 38, 0.1)", bordercolor=self.colors['danger'],
                font=dict(size=10, color=self.colors['danger'])
            )
        
        fig_area.update_layout(
            title_text='Enhanced Area Flow Analysis<br><sub>Hectares with Data Loss Tracking</sub>', 
            yaxis_title="Hectares",
            showlegend=False,
            hovermode='x unified'
        )

        # Address Quality Chart (enhanced)
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

        # Convert all figures to HTML with displaylogo: false to remove Plotly watermark
        config = {'displaylogo': False, 'modeBarButtonsToRemove': ['pan2d', 'lasso2d']}
        
        funnel_html = pio.to_html(fig_funnel, full_html=False, include_plotlyjs='cdn', config=config)
        area_html = pio.to_html(fig_area, full_html=False, include_plotlyjs=False, config=config)
        geo_html = pio.to_html(fig_geo, full_html=False, include_plotlyjs=False, config=config)
        quality_html = pio.to_html(fig_quality, full_html=False, include_plotlyjs=False, config=config)
        consolidation_html = pio.to_html(fig_consolidation, full_html=False, include_plotlyjs=False, config=config)
        ownership_html = pio.to_html(fig_ownership, full_html=False, include_plotlyjs=False, config=config)
        segment_html = pio.to_html(fig_segment, full_html=False, include_plotlyjs=False, config=config)
        municipality_table_html = pio.to_html(fig_municipality_table, full_html=False, include_plotlyjs=False, config=config)
        corporate_table_html = pio.to_html(fig_corporate_table, full_html=False, include_plotlyjs=False, config=config)

        # Build enhanced HTML dashboard
        html_string = f"""
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Enhanced Campaign4 Dashboard</title><script src="https://cdn.plot.ly/plotly-latest.min.js"></script><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"><link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
<style>
    body {{ font-family: 'Inter', sans-serif; background: #f8f9fa; color: #212529; }}
    .dashboard-container {{ max-width: 1600px; margin: 0 auto; padding: 20px; }}
    .header {{ text-align: center; margin-bottom: 30px; }}
    .header h1 {{ font-size: 2.5rem; font-weight: 700; color: #1e40af; }}
    .header p {{ font-size: 1.1rem; color: #6b7280; }}
    .enhancement-badge {{ background: linear-gradient(45deg, #1e40af, #059669); color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.9rem; margin: 10px 5px; display: inline-block; }}
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
    .enhancement-section {{ background: linear-gradient(135deg, #f0f4ff, #e0f2fe); border-left: 5px solid #1e40af; }}
    .efficiency-metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
    .efficiency-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #059669; }}
    @media (max-width: 992px) {{ .chart-grid {{ grid-template-columns: 1fr; }} }}
</style>
</head><body><div class="dashboard-container">
    <div class="header">
        <h1><i class="fas fa-seedling"></i> Enhanced Campaign4 Dashboard</h1>
        <p>Advanced Land Acquisition Analytics with Process Intelligence</p>
        <div style="margin-top: 15px;">
            <span class="enhancement-badge">ENH-QW-001: Efficiency Indicators</span>
            <span class="enhancement-badge">ENH-QW-002: Enhanced Geography</span>
            <span class="enhancement-badge">ENH-P3: Process Analytics</span>
            <span class="enhancement-badge">ENH-P4: Ownership Intelligence</span>
        </div>
    </div>
    
    <h2 class="kpi-section-header">Pipeline Input & Availability</h2>
    <div class="kpi-grid">
        <div class="kpi-card"><div class="kpi-value">{metrics['input']['total_parcels']}</div><div class="kpi-label">Original Input Parcels</div><div class="kpi-explanation">Parcels from initial file</div></div>
        <div class="kpi-card"><div class="kpi-value">{metrics['input']['total_area']:.0f} Ha</div><div class="kpi-label">Original Input Area</div><div class="kpi-explanation">Total hectares in original file</div></div>
        <div class="kpi-card"><div class="kpi-value">{metrics['pipeline']['data_availability_rate']:.1f}%</div><div class="kpi-label">Data Availability Rate</div><div class="kpi-explanation">Input parcels with retrieved data</div></div>
    </div>

    <h2 class="kpi-section-header">Enhanced Process Efficiency Metrics</h2>
    <div class="efficiency-metrics">
        <div class="efficiency-card"><div class="kpi-value">{efficiency_data['overall_conversion_rate']:.1f}%</div><div class="kpi-label">Overall Conversion</div></div>
        <div class="efficiency-card"><div class="kpi-value">{efficiency_data['automation_coverage']:.1f}%</div><div class="kpi-label">Automation Coverage</div></div>
        <div class="efficiency-card"><div class="kpi-value">{len(efficiency_data['manual_stages'])}</div><div class="kpi-label">Manual Stages</div></div>
        <div class="efficiency-card"><div class="kpi-value">{complexity_data['max_owners_per_parcel']}</div><div class="kpi-label">Max Owners/Parcel</div></div>
        <div class="efficiency-card"><div class="kpi-value">{segmentation_data['b2b']['pec_availability_rate']:.1f}%</div><div class="kpi-label">B2B PEC Coverage</div></div>
    </div>

    <div class="chart-section enhancement-section">
        <div class="section-header"><h2><i class="fas fa-filter"></i> ENH-QW-001: Enhanced Pipeline Flow with Efficiency Indicators</h2></div>
        <div class="chart-container">{funnel_html}</div>
    </div>
    
    <div class="chart-section enhancement-section">
        <div class="section-header"><h2><i class="fas fa-map-marked-alt"></i> ENH-QW-002: Enhanced Geographic & Area Intelligence</h2></div>
        <div class="chart-container">
            <div style="display: grid; grid-template-columns: 1fr 1.2fr; gap: 20px; align-items: flex-start;">
                <div>{area_html}</div>
                <div style="min-height: 500px; width: 100%; overflow: visible;">{geo_html}</div>
            </div>
            <!-- Executive Table 1: Municipality Performance -->
            <div style="margin-top: 30px;">
                {municipality_table_html}
            </div>
        </div>
    </div>

    <div class="chart-section enhancement-section">
        <div class="section-header"><h2><i class="fas fa-users"></i> ENH-P4: Advanced Ownership & Segmentation Intelligence</h2></div>
        <div class="chart-container">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; align-items: flex-start;">
                <div style="min-height: 600px;">{ownership_html}</div>
                <div style="min-height: 600px;">{segment_html}</div>
            </div>
            <!-- Executive Table 3: Corporate Opportunities -->
            <div style="margin-top: 30px;">
                {corporate_table_html}
            </div>
        </div>
    </div>

    <div class="chart-section">
        <div class="section-header"><h2><i class="fas fa-chart-pie"></i> Address Quality & Owner Optimization Analysis</h2></div>
        <div class="chart-container"><div class="chart-grid">
            <div>{consolidation_html}</div>
            <div>{quality_html}</div>
        </div></div>
    </div>

    <div class="chart-section">
        <div class="section-header"><h2><i class="fas fa-info-circle"></i> Enhancement Summary</h2></div>
        <div class="chart-container">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div style="padding: 20px; background: #f8f9fa; border-radius: 8px;">
                    <h3 style="color: #1e40af; margin: 0 0 10px 0;">Quick Wins (ENH-QW)</h3>
                    <p><strong>✅ Enhanced Funnel:</strong> Added efficiency indicators and conversion rates</p>
                    <p><strong>✅ Geographic Intelligence:</strong> Area data and detailed hover information</p>
                </div>
                <div style="padding: 20px; background: #f0f9ff; border-radius: 8px;">
                    <h3 style="color: #059669; margin: 0 0 10px 0;">Process Analytics (ENH-P3)</h3>
                    <p><strong>✅ Enhanced Data Processing:</strong> Advanced funnel analysis processing</p>
                    <p><strong>✅ Efficiency Metrics:</strong> Bottleneck identification and optimization KPIs</p>
                </div>
                <div style="padding: 20px; background: #f0fdf4; border-radius: 8px;">
                    <h3 style="color: #8b5cf6; margin: 0 0 10px 0;">Ownership Intelligence (ENH-P4)</h3>
                    <p><strong>✅ Complexity Analysis:</strong> Multi-owner pattern identification</p>
                    <p><strong>✅ B2B/B2C Segmentation:</strong> Corporate vs individual insights</p>
                </div>
            </div>
        </div>
    </div>
</div></body></html>
"""
        return html_string

def main():
    print("🚀 Running Enhanced Campaign Dashboard Generator...")
    print("=" * 60)
    
    excel_path = r"Campaign4_Results.xlsx"
    input_file_path = r"Input_Castiglione Casalpusterlengo CP.xlsx"
    output_path = r"enhanced_campaign_dashboard.html"
    
    try:
        analyzer = EnhancedDashboardGenerator(excel_path, input_file_path)
        html_dashboard = analyzer.create_plotly_dashboard()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_dashboard)
        
        print("\n" + "="*60)
        print(f"✅ SUCCESS! Enhanced interactive dashboard saved to: {os.path.abspath(output_path)}")
        print("🎯 Enhancements implemented:")
        print("   - ENH-QW-001: Enhanced dual funnel with efficiency indicators (fixed redundancy)")
        print("   - ENH-QW-002: Geographic distribution with area data + delta tracking")
        print("   - ENH-P3-001: Enhanced funnel data processor")
        print("   - ENH-P3-003: Process efficiency metrics")
        print("   - ENH-P4-001: Ownership complexity analysis (business-focused categories)")
        print("   - ENH-P4-003: B2B/B2C segmentation analysis (corrected area calculations)")
        print("   - NEW: Municipality Performance Summary table (executive-focused)")
        print("   - NEW: Corporate Opportunities B2B table (high-value targets)")
        print("="*60)
        
    except FileNotFoundError as e:
        print(f"❌ FILE NOT FOUND: {e.filename}. Please ensure the Excel files are in the same directory as the script.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()