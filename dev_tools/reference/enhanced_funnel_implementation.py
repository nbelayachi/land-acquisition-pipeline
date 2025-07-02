"""
Enhanced Funnel Implementation for Land Acquisition Pipeline
Integration-ready code for replacing basic funnel analysis

This file contains the production-ready enhanced funnel implementation
to be integrated into land_acquisition_pipeline.py
"""

import pandas as pd
import numpy as np

def create_enhanced_funnel_analysis_df(self, df_summary, df_validation):
    """
    Create comprehensive funnel analysis with conversion rates and business intelligence
    
    Replaces the basic create_funnel_analysis_df() with enhanced dual funnel structure
    that provides executive KPIs, conversion rates, and process optimization metrics.
    
    Args:
        df_summary: Campaign summary DataFrame with parcel and owner metrics
        df_validation: Validation ready DataFrame with address quality data
        
    Returns:
        tuple: (enhanced_funnel_df, quality_distribution_df)
        
    Business Impact:
        - Provides executive-level KPIs for decision making
        - Enables process bottleneck identification
        - Quantifies automation opportunities
        - Supports PowerBI dashboard integration
    """
    
    # Extract campaign metadata
    campaign_cp = df_summary['CP'].iloc[0] if len(df_summary) > 0 else "Unknown"
    campaign_municipalities = df_summary['comune'].unique().tolist() if len(df_summary) > 0 else ["Unknown"]
    campaign_provincia = df_summary['provincia'].iloc[0] if len(df_summary) > 0 else "Unknown"
    
    # Calculate land acquisition metrics from summary
    total_input_parcels = df_summary['Input_Parcels'].sum()
    total_input_hectares = df_summary['Input_Area_Ha'].sum()
    total_after_api = df_summary['After_API_Parcels'].sum()
    total_after_api_ha = df_summary['After_API_Area_Ha'].sum()
    total_private_parcels = df_summary['Private_Owner_Parcels'].sum()
    total_private_ha = df_summary['Private_Owner_Area_Ha'].sum()
    total_category_a = df_summary['After_CatA_Filter_Parcels'].sum()
    total_category_a_ha = df_summary['After_CatA_Filter_Area_Ha'].sum()
    
    # Calculate contact processing metrics
    total_unique_owners = df_summary['Unique_Individual_Owners'].sum()
    total_address_pairs = df_summary['Unique_Owner_Address_Pairs'].sum()
    total_direct_mail = df_summary['Direct_Mail_Final_Contacts'].sum()
    total_agency = df_summary['Agency_Final_Contacts'].sum()
    
    # LAND ACQUISITION PIPELINE
    land_acquisition_data = [
        {
            'Funnel_Type': 'Land Acquisition',
            'Stage': '1. Input Parcels',
            'Count': total_input_parcels,
            'Hectares': round(total_input_hectares, 1),
            'Conversion_Rate': None,  # Starting point
            'Retention_Rate': 100.0,
            'Business_Rule': 'User input - parcels selected for acquisition analysis',
            'Automation_Level': 'Manual',
            'Process_Notes': 'Campaign input from user selection',
            'CP': campaign_cp,
            'comune': '; '.join(campaign_municipalities),
            'provincia': campaign_provincia
        },
        {
            'Funnel_Type': 'Land Acquisition',
            'Stage': '2. API Data Retrieved',
            'Count': total_after_api,
            'Hectares': round(total_after_api_ha, 1),
            'Conversion_Rate': round((total_after_api / total_input_parcels * 100) if total_input_parcels > 0 else 0, 1),
            'Retention_Rate': round((total_after_api / total_input_parcels * 100) if total_input_parcels > 0 else 0, 1),
            'Business_Rule': 'API successfully retrieved ownership data',
            'Automation_Level': 'Fully-Auto',
            'Process_Notes': f'API success rate: {round((total_after_api / total_input_parcels * 100) if total_input_parcels > 0 else 0, 1)}%',
            'CP': campaign_cp,
            'comune': '; '.join(campaign_municipalities),
            'provincia': campaign_provincia
        },
        {
            'Funnel_Type': 'Land Acquisition',
            'Stage': '3. Private Owners Only',
            'Count': total_private_parcels,
            'Hectares': round(total_private_ha, 1),
            'Conversion_Rate': round((total_private_parcels / total_after_api * 100) if total_after_api > 0 else 0, 1),
            'Retention_Rate': round((total_private_parcels / total_input_parcels * 100) if total_input_parcels > 0 else 0, 1),
            'Business_Rule': 'Filter applied - exclude company owners',
            'Automation_Level': 'Fully-Auto',
            'Process_Notes': f'Private owner rate: {round((total_private_parcels / total_after_api * 100) if total_after_api > 0 else 0, 1)}%',
            'CP': campaign_cp,
            'comune': '; '.join(campaign_municipalities),
            'provincia': campaign_provincia
        },
        {
            'Funnel_Type': 'Land Acquisition',
            'Stage': '4. Category A Filter',
            'Count': total_category_a,
            'Hectares': round(total_category_a_ha, 1),
            'Conversion_Rate': round((total_category_a / total_private_parcels * 100) if total_private_parcels > 0 else 0, 1),
            'Retention_Rate': round((total_category_a / total_input_parcels * 100) if total_input_parcels > 0 else 0, 1),
            'Business_Rule': 'Category A filter - remove non-residential properties',
            'Automation_Level': 'Fully-Auto',
            'Process_Notes': f'Property type filtering - {round((1 - total_category_a / total_private_parcels) * 100 if total_private_parcels > 0 else 0, 1)}% removed',
            'CP': campaign_cp,
            'comune': '; '.join(campaign_municipalities),
            'provincia': campaign_provincia
        }
    ]
    
    # CONTACT PROCESSING PIPELINE
    contact_processing_data = [
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '1. Owners Identified',
            'Count': total_unique_owners,
            'Hectares': round(total_category_a_ha, 1),
            'Conversion_Rate': round((total_unique_owners / total_category_a * 100) if total_category_a > 0 else 0, 1),
            'Retention_Rate': 100.0,
            'Business_Rule': 'Owner identification from qualified parcels',
            'Automation_Level': 'Fully-Auto',
            'Process_Notes': f'{round(total_unique_owners / total_category_a, 2) if total_category_a > 0 else 0} owners per parcel average',
            'CP': campaign_cp,
            'comune': '; '.join(campaign_municipalities),
            'provincia': campaign_provincia
        },
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '2. Address Pairs Created',
            'Count': total_address_pairs,
            'Hectares': round(total_category_a_ha, 1),
            'Conversion_Rate': round((total_address_pairs / total_unique_owners * 100) if total_unique_owners > 0 else 0, 1),
            'Retention_Rate': 100.0,
            'Business_Rule': 'Address expansion - multiple addresses per owner',
            'Automation_Level': 'Fully-Auto',
            'Process_Notes': f'{round(total_address_pairs / total_unique_owners, 1) if total_unique_owners > 0 else 0} addresses per owner average',
            'CP': campaign_cp,
            'comune': '; '.join(campaign_municipalities),
            'provincia': campaign_provincia
        },
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '3. Geocoding Completed',
            'Count': total_address_pairs,
            'Hectares': round(total_category_a_ha, 1),
            'Conversion_Rate': 100.0,  # Assuming all addresses are geocoded
            'Retention_Rate': 100.0,
            'Business_Rule': 'All addresses geocoded and quality assessed',
            'Automation_Level': 'Fully-Auto',
            'Process_Notes': 'Enhanced classification applied to all addresses',
            'CP': campaign_cp,
            'comune': '; '.join(campaign_municipalities),
            'provincia': campaign_provincia
        },
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '4. Direct Mail Ready',
            'Count': total_direct_mail,
            'Hectares': round(df_summary['Direct_Mail_Final_Area_Ha'].sum(), 1),
            'Conversion_Rate': round((total_direct_mail / total_address_pairs * 100) if total_address_pairs > 0 else 0, 1),
            'Retention_Rate': round((total_direct_mail / total_address_pairs * 100) if total_address_pairs > 0 else 0, 1),
            'Business_Rule': 'High confidence addresses routed for direct mailing',
            'Automation_Level': 'Semi-Auto',
            'Process_Notes': 'ULTRA_HIGH + HIGH + selected MEDIUM confidence addresses',
            'CP': campaign_cp,
            'comune': '; '.join(campaign_municipalities),
            'provincia': campaign_provincia
        },
        {
            'Funnel_Type': 'Contact Processing',
            'Stage': '5. Agency Required',
            'Count': total_agency,
            'Hectares': round(df_summary['Agency_Final_Area_Ha'].sum(), 1),
            'Conversion_Rate': round((total_agency / total_address_pairs * 100) if total_address_pairs > 0 else 0, 1),
            'Retention_Rate': round((total_agency / total_address_pairs * 100) if total_address_pairs > 0 else 0, 1),
            'Business_Rule': 'Low confidence addresses require agency investigation',
            'Automation_Level': 'Manual',
            'Process_Notes': 'LOW confidence + selected MEDIUM confidence addresses',
            'CP': campaign_cp,
            'comune': '; '.join(campaign_municipalities),
            'provincia': campaign_provincia
        }
    ]
    
    # Create enhanced funnel DataFrame
    enhanced_funnel_df = pd.DataFrame(land_acquisition_data + contact_processing_data)
    
    # Create address quality distribution DataFrame
    quality_distribution_df = create_quality_distribution_df(self, df_validation, campaign_cp, campaign_municipalities, campaign_provincia)
    
    return enhanced_funnel_df, quality_distribution_df

def create_quality_distribution_df(self, df_validation, campaign_cp, campaign_municipalities, campaign_provincia):
    """
    Create address quality distribution analysis
    
    Args:
        df_validation: Validation ready DataFrame with address confidence data
        campaign_cp: Campaign CP identifier
        campaign_municipalities: List of municipalities
        campaign_provincia: Province identifier
        
    Returns:
        pd.DataFrame: Quality distribution with automation metrics
    """
    
    if len(df_validation) == 0:
        # Return empty DataFrame with correct structure if no validation data
        return pd.DataFrame(columns=[
            'Quality_Level', 'Count', 'Percentage', 'Processing_Type', 
            'Business_Value', 'Automation_Level', 'Routing_Decision',
            'CP', 'comune', 'provincia'
        ])
    
    # Calculate quality distribution
    quality_counts = df_validation['Address_Confidence'].value_counts()
    total_addresses = len(df_validation)
    
    # Define quality levels and their business characteristics
    quality_definitions = {
        'ULTRA_HIGH': {
            'Processing_Type': 'Zero Touch',
            'Business_Value': 'Immediate print ready',
            'Automation_Level': 'Fully-Auto',
            'Routing_Decision': 'Direct Mail'
        },
        'HIGH': {
            'Processing_Type': 'Quick Review',
            'Business_Value': 'Minimal validation needed',
            'Automation_Level': 'Semi-Auto',
            'Routing_Decision': 'Direct Mail'
        },
        'MEDIUM': {
            'Processing_Type': 'Standard Review',
            'Business_Value': 'Normal processing required',
            'Automation_Level': 'Manual',
            'Routing_Decision': 'Mixed (Direct Mail + Agency)'
        },
        'LOW': {
            'Processing_Type': 'Agency Routing',
            'Business_Value': 'External investigation required',
            'Automation_Level': 'Manual',
            'Routing_Decision': 'Agency'
        }
    }
    
    # Create quality distribution data
    quality_data = []
    for quality_level in ['ULTRA_HIGH', 'HIGH', 'MEDIUM', 'LOW']:
        count = quality_counts.get(quality_level, 0)
        percentage = round((count / total_addresses * 100) if total_addresses > 0 else 0, 1)
        
        quality_info = quality_definitions.get(quality_level, {
            'Processing_Type': 'Unknown',
            'Business_Value': 'Not defined',
            'Automation_Level': 'Manual',
            'Routing_Decision': 'Unknown'
        })
        
        quality_data.append({
            'Quality_Level': quality_level,
            'Count': count,
            'Percentage': percentage,
            'Processing_Type': quality_info['Processing_Type'],
            'Business_Value': quality_info['Business_Value'],
            'Automation_Level': quality_info['Automation_Level'],
            'Routing_Decision': quality_info['Routing_Decision'],
            'CP': campaign_cp,
            'comune': '; '.join(campaign_municipalities),
            'provincia': campaign_provincia
        })
    
    return pd.DataFrame(quality_data)

def calculate_executive_kpis(enhanced_funnel_df, quality_distribution_df):
    """
    Calculate executive-level KPIs from enhanced funnel data
    
    Args:
        enhanced_funnel_df: Enhanced funnel DataFrame
        quality_distribution_df: Quality distribution DataFrame
        
    Returns:
        dict: Executive KPIs for dashboard reporting
    """
    
    # Extract key metrics from funnel
    land_funnel = enhanced_funnel_df[enhanced_funnel_df['Funnel_Type'] == 'Land Acquisition']
    contact_funnel = enhanced_funnel_df[enhanced_funnel_df['Funnel_Type'] == 'Contact Processing']
    
    # Land acquisition efficiency
    input_parcels = land_funnel[land_funnel['Stage'] == '1. Input Parcels']['Count'].iloc[0]
    qualified_parcels = land_funnel[land_funnel['Stage'] == '4. Category A Filter']['Count'].iloc[0]
    land_efficiency = round((qualified_parcels / input_parcels * 100) if input_parcels > 0 else 0, 1)
    
    # Contact multiplication
    owners = contact_funnel[contact_funnel['Stage'] == '1. Owners Identified']['Count'].iloc[0]
    addresses = contact_funnel[contact_funnel['Stage'] == '2. Address Pairs Created']['Count'].iloc[0]
    contact_multiplication = round((addresses / qualified_parcels) if qualified_parcels > 0 else 0, 1)
    
    # Direct mail efficiency
    direct_mail = contact_funnel[contact_funnel['Stage'] == '4. Direct Mail Ready']['Count'].iloc[0]
    direct_mail_efficiency = round((direct_mail / addresses * 100) if addresses > 0 else 0, 1)
    
    # Automation metrics from quality distribution
    ultra_high_count = quality_distribution_df[quality_distribution_df['Quality_Level'] == 'ULTRA_HIGH']['Count'].iloc[0] if len(quality_distribution_df) > 0 else 0
    high_count = quality_distribution_df[quality_distribution_df['Quality_Level'] == 'HIGH']['Count'].iloc[0] if len(quality_distribution_df) > 0 else 0
    total_quality_addresses = quality_distribution_df['Count'].sum() if len(quality_distribution_df) > 0 else addresses
    
    zero_touch_rate = round((ultra_high_count / total_quality_addresses * 100) if total_quality_addresses > 0 else 0, 1)
    high_quality_rate = round(((ultra_high_count + high_count) / total_quality_addresses * 100) if total_quality_addresses > 0 else 0, 1)
    
    return {
        'land_acquisition_efficiency': land_efficiency,
        'contact_multiplication_factor': contact_multiplication,
        'direct_mail_efficiency': direct_mail_efficiency,
        'zero_touch_processing_rate': zero_touch_rate,
        'high_quality_processing_rate': high_quality_rate,
        'total_input_parcels': input_parcels,
        'qualified_parcels': qualified_parcels,
        'total_owners': owners,
        'total_addresses': addresses,
        'direct_mail_contacts': direct_mail,
        'ultra_high_addresses': ultra_high_count
    }

# Integration helper function for main pipeline
def integrate_enhanced_funnel_analysis(self, df_summary, df_validation):
    """
    Integration wrapper for enhanced funnel analysis
    
    This function replaces the existing create_funnel_analysis_df() call
    and provides backward compatibility while adding enhanced features.
    
    Usage in land_acquisition_pipeline.py:
        # Replace existing:
        # df_all_funnels = self.create_funnel_analysis_df(df_summary)
        
        # With enhanced:
        df_all_funnels, df_quality_distribution = self.integrate_enhanced_funnel_analysis(df_summary, df_validation)
        executive_kpis = calculate_executive_kpis(df_all_funnels, df_quality_distribution)
    """
    
    # Create enhanced funnel analysis
    enhanced_funnel_df, quality_distribution_df = create_enhanced_funnel_analysis_df(self, df_summary, df_validation)
    
    # Calculate executive KPIs
    executive_kpis = calculate_executive_kpis(enhanced_funnel_df, quality_distribution_df)
    
    # Log key metrics for monitoring
    self.logger.info(f"Enhanced funnel analysis complete:")
    self.logger.info(f"  Land efficiency: {executive_kpis['land_acquisition_efficiency']}%")
    self.logger.info(f"  Contact multiplication: {executive_kpis['contact_multiplication_factor']}x")
    self.logger.info(f"  Zero-touch processing: {executive_kpis['zero_touch_processing_rate']}%")
    self.logger.info(f"  Direct mail efficiency: {executive_kpis['direct_mail_efficiency']}%")
    
    return enhanced_funnel_df, quality_distribution_df, executive_kpis