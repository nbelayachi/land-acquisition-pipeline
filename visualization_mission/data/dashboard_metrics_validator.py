#!/usr/bin/env python3
"""
DASHBOARD METRICS VALIDATOR
==========================

CODE ID: VAL-002
Validates current dashboard metrics against source data to identify discrepancies
"""

import pandas as pd
import re

def validate_dashboard_metrics():
    """
    Validates all current dashboard calculations against source data
    """
    print("🔍 DASHBOARD METRICS VALIDATION")
    print("=" * 80)
    
    # Load data files
    try:
        print("Loading data files...")
        campaign_data = {}
        campaign_data['Input_File'] = pd.read_excel('Input_Castiglione Casalpusterlengo CP.xlsx', sheet_name='Sheet1')
        campaign_data['All_Raw_Data'] = pd.read_excel('Campaign4_Results.xlsx', sheet_name='All_Raw_Data')
        campaign_data['Final_Mailing_List'] = pd.read_excel('Campaign4_Results.xlsx', sheet_name='Final_Mailing_List')
        campaign_data['All_Validation_Ready'] = pd.read_excel('Campaign4_Results.xlsx', sheet_name='All_Validation_Ready')
        campaign_data['Address_Quality_Distribution'] = pd.read_excel('Campaign4_Results.xlsx', sheet_name='Address_Quality_Distribution')
        campaign_data['Enhanced_Funnel_Analysis'] = pd.read_excel('Campaign4_Results.xlsx', sheet_name='Enhanced_Funnel_Analysis')
        campaign_data['Campaign_Scorecard'] = pd.read_excel('Campaign4_Results.xlsx', sheet_name='Campaign_Scorecard')
        
        # Clean column names
        for key in campaign_data:
            campaign_data[key].columns = [str(c).strip() for c in campaign_data[key].columns]
        
        print("✅ Data files loaded successfully")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Validation results
    validation_results = {}
    
    # VALIDATE INPUT METRICS
    print(f"\n📊 VALIDATING INPUT METRICS")
    print("-" * 50)
    
    input_df = campaign_data['Input_File'].copy()
    input_df['Area'] = input_df['Area'].astype(str).str.replace(',', '.').astype(float)
    
    # Total parcels
    actual_input_parcels = len(input_df[['comune', 'foglio', 'particella']].drop_duplicates())
    expected_input_parcels = 237  # From data exploration
    validation_results['total_parcels'] = {
        'calculated': actual_input_parcels,
        'expected': expected_input_parcels,
        'status': '✅ PASS' if actual_input_parcels == expected_input_parcels else '❌ FAIL'
    }
    
    # Total area
    actual_total_area = input_df['Area'].sum()
    validation_results['total_area'] = {
        'calculated': round(actual_total_area, 2),
        'expected': 'Sum of input areas',
        'status': '✅ PASS' if actual_total_area > 0 else '❌ FAIL'
    }
    
    # Data available parcels
    raw_data_df = campaign_data['All_Raw_Data']
    actual_available_parcels = len(raw_data_df[['comune_input', 'foglio_input', 'particella_input']].drop_duplicates())
    expected_available_parcels = 225  # From Enhanced_Funnel_Analysis
    validation_results['data_available_parcels'] = {
        'calculated': actual_available_parcels,
        'expected': expected_available_parcels,
        'status': '⚠️ CHECK' if abs(actual_available_parcels - expected_available_parcels) <= 3 else '❌ FAIL'
    }
    
    print("INPUT METRICS VALIDATION:")
    for metric, result in validation_results.items():
        print(f"  {metric}: {result['calculated']} (expected: {result['expected']}) - {result['status']}")
    
    # VALIDATE MAILING METRICS
    print(f"\n📬 VALIDATING MAILING METRICS")
    print("-" * 50)
    
    # Strategic mailings (should be straightforward)
    actual_strategic_mailings = len(campaign_data['Final_Mailing_List'])
    expected_strategic_mailings = 303  # From data exploration
    validation_results['strategic_mailings'] = {
        'calculated': actual_strategic_mailings,
        'expected': expected_strategic_mailings,
        'status': '✅ PASS' if actual_strategic_mailings == expected_strategic_mailings else '❌ FAIL'
    }
    
    # Property owners
    actual_property_owners = campaign_data['Final_Mailing_List']['cf'].nunique()
    expected_property_owners = 144  # From Campaign_Scorecard
    validation_results['property_owners'] = {
        'calculated': actual_property_owners,
        'expected': expected_property_owners,
        'status': '⚠️ CHECK' if abs(actual_property_owners - expected_property_owners) <= 5 else '❌ FAIL'
    }
    
    # Unique parcels (complex parsing - this is where issues likely occur)
    print("\n🔍 ANALYZING PARCEL PARSING LOGIC...")
    df_mailing = campaign_data['Final_Mailing_List']
    parcels_list = []
    parsing_errors = 0
    
    for idx, row in df_mailing.iterrows():
        try:
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
                        parsing_errors += 1
                        continue
        except Exception as e:
            parsing_errors += 1
            continue
    
    unique_parcels_df = pd.DataFrame(parcels_list).drop_duplicates().reset_index(drop=True)
    actual_unique_parcels = len(unique_parcels_df)
    expected_unique_parcels = 152  # From Enhanced_Funnel_Analysis business funnel
    
    validation_results['unique_parcels'] = {
        'calculated': actual_unique_parcels,
        'expected': expected_unique_parcels,
        'parsing_errors': parsing_errors,
        'status': '⚠️ CHECK' if abs(actual_unique_parcels - expected_unique_parcels) <= 5 else '❌ FAIL'
    }
    
    print("MAILING METRICS VALIDATION:")
    for metric, result in validation_results.items():
        if metric in ['strategic_mailings', 'property_owners', 'unique_parcels']:
            status_line = f"  {metric}: {result['calculated']} (expected: {result['expected']}) - {result['status']}"
            if 'parsing_errors' in result:
                status_line += f" | Parsing errors: {result['parsing_errors']}"
            print(status_line)
    
    # CROSS-VALIDATE WITH ENHANCED FUNNEL ANALYSIS
    print(f"\n📈 CROSS-VALIDATING WITH ENHANCED FUNNEL ANALYSIS")
    print("-" * 50)
    
    funnel_df = campaign_data['Enhanced_Funnel_Analysis']
    
    # Find key stages
    input_stage = funnel_df[funnel_df['Stage'].str.contains('Input Parcels', na=False)]
    data_retrieved_stage = funnel_df[funnel_df['Stage'].str.contains('Data Retrieved', na=False)]
    
    if not input_stage.empty:
        funnel_input_parcels = input_stage.iloc[0]['Count']
        print(f"  Funnel Input Parcels: {funnel_input_parcels}")
        print(f"  Dashboard Input Parcels: {actual_input_parcels}")
        print(f"  Match: {'✅ PASS' if funnel_input_parcels == actual_input_parcels else '❌ FAIL'}")
    
    if not data_retrieved_stage.empty:
        funnel_data_retrieved = data_retrieved_stage.iloc[0]['Count']
        print(f"  Funnel Data Retrieved: {funnel_data_retrieved}")
        print(f"  Dashboard Available Parcels: {actual_available_parcels}")
        print(f"  Match: {'✅ PASS' if funnel_data_retrieved == actual_available_parcels else '❌ FAIL'}")
    
    # FINAL ASSESSMENT
    print(f"\n{'='*80}")
    print("📋 VALIDATION SUMMARY")
    print("=" * 80)
    
    passes = sum(1 for result in validation_results.values() if '✅' in result['status'])
    checks = sum(1 for result in validation_results.values() if '⚠️' in result['status'])
    fails = sum(1 for result in validation_results.values() if '❌' in result['status'])
    
    print(f"✅ PASSES: {passes}")
    print(f"⚠️  CHECKS NEEDED: {checks}")
    print(f"❌ FAILURES: {fails}")
    
    if fails > 0:
        print(f"\n🚨 CRITICAL ISSUES FOUND - Dashboard metrics need correction before enhancement")
    elif checks > 0:
        print(f"\n⚠️  MINOR DISCREPANCIES FOUND - Recommend validation before enhancement")
    else:
        print(f"\n✅ ALL METRICS VALIDATED - Dashboard ready for enhancement")
    
    return validation_results

def analyze_current_visualizations():
    """
    Analyzes current visualization effectiveness and improvement opportunities
    """
    print(f"\n{'='*80}")
    print("🎨 CURRENT VISUALIZATION ANALYSIS")
    print("=" * 80)
    
    current_visualizations = {
        "Dual Processing Funnel": {
            "Type": "go.Funnel (two side-by-side)",
            "Data Quality": "Good - uses validated metrics",
            "Business Value": "Medium - shows process but lacks context",
            "Improvement Opportunity": "Add efficiency indicators and cost implications",
            "Priority": "MEDIUM"
        },
        "Area Flow Analysis": {
            "Type": "go.Bar (3 stages)", 
            "Data Quality": "Good - clear area progression",
            "Business Value": "High - shows value preservation through pipeline",
            "Improvement Opportunity": "Add percentage retention indicators",
            "Priority": "LOW"
        },
        "Geographic Distribution": {
            "Type": "go.Pie (municipality breakdown)",
            "Data Quality": "Good - accurate municipality counts",
            "Business Value": "Low - too simplistic for decision making",
            "Improvement Opportunity": "Convert to interactive map or bubble chart",
            "Priority": "HIGH"
        },
        "Address Quality Distribution": {
            "Type": "go.Pie (4-tier quality)",
            "Data Quality": "Excellent - direct from quality analysis",
            "Business Value": "Medium - shows quality but not actionability",
            "Improvement Opportunity": "Add processing workflow and cost implications",
            "Priority": "MEDIUM"
        },
        "Owner Consolidation": {
            "Type": "go.Bar (mailings per owner)",
            "Data Quality": "Good - accurate consolidation metrics",
            "Business Value": "Medium - shows optimization results",
            "Improvement Opportunity": "Add relationship complexity analysis",
            "Priority": "MEDIUM"
        }
    }
    
    for viz_name, details in current_visualizations.items():
        print(f"\n📊 {viz_name}:")
        for key, value in details.items():
            print(f"   {key}: {value}")
    
    return current_visualizations

def main():
    """
    Run comprehensive dashboard validation
    """
    print("🔍 COMPREHENSIVE DASHBOARD VALIDATION")
    print("Code ID: VAL-002")
    print("=" * 80)
    
    # Run validation
    validation_results = validate_dashboard_metrics()
    visualization_analysis = analyze_current_visualizations()
    
    print(f"\n{'='*80}")
    print("✅ VALIDATION COMPLETE")
    print("📁 Results available for enhancement planning")
    print("=" * 80)

if __name__ == "__main__":
    main()