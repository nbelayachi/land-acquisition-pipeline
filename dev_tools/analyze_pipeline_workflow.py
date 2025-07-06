#!/usr/bin/env python3
"""
Pipeline Workflow Analysis Script
Analyzes the data transformation workflow from raw to final outputs
Usage: Run in Spyder and paste the output back for review
"""

import pandas as pd
import numpy as np

def analyze_pipeline_workflow(excel_path):
    """
    Analyze the complete pipeline workflow and data transformations
    """
    print("="*80)
    print("PIPELINE WORKFLOW ANALYSIS")
    print("="*80)
    print(f"File: {excel_path}")
    print()
    
    try:
        # Read all sheets
        sheets = {}
        sheet_names = ['All_Raw_Data', 'All_Validation_Ready', 'Final_Mailing_List', 
                      'Campaign_Summary', 'Enhanced_Funnel_Analysis', 'Address_Quality_Distribution']
        
        for sheet_name in sheet_names:
            try:
                sheets[sheet_name] = pd.read_excel(excel_path, sheet_name=sheet_name)
                print(f"✅ Loaded {sheet_name}: {len(sheets[sheet_name])} rows")
            except Exception as e:
                print(f"❌ Failed to load {sheet_name}: {e}")
        
        print()
        
        # 1. WORKFLOW STEP ANALYSIS
        print("🔄 PIPELINE WORKFLOW STEPS:")
        print("-" * 50)
        
        if 'All_Raw_Data' in sheets:
            df_raw = sheets['All_Raw_Data']
            
            # Step 1: Input Analysis
            print("STEP 1: INPUT ANALYSIS")
            unique_input_parcels = df_raw.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
            total_area = pd.to_numeric(df_raw['Area'].astype(str).str.replace(',', '.'), errors='coerce').sum()
            print(f"  Input Parcels: {len(unique_input_parcels)}")
            print(f"  Total Area: {total_area:.2f} ha")
            print(f"  Raw Records: {len(df_raw)}")
            print()
            
            # Step 2: Property Type Filtering
            print("STEP 2: PROPERTY TYPE FILTERING")
            if 'classamento' in df_raw.columns:
                category_breakdown = df_raw['classamento'].str[0].value_counts() if df_raw['classamento'].notna().any() else pd.Series()
                print("  Property Categories:")
                for cat, count in category_breakdown.items():
                    print(f"    Category {cat}: {count} records")
                
                # Category A analysis
                cat_a_records = df_raw[df_raw['classamento'].str.startswith('A', na=False)]
                cat_a_parcels = cat_a_records.groupby(['comune_input', 'foglio_input', 'particella_input']).size()
                cat_a_area = pd.to_numeric(cat_a_records.drop_duplicates(['comune_input', 'foglio_input', 'particella_input'])['Area'].astype(str).str.replace(',', '.'), errors='coerce').sum()
                
                print(f"  After Category A Filter:")
                print(f"    Parcels: {len(cat_a_parcels)}")
                print(f"    Area: {cat_a_area:.2f} ha")
                print(f"    Records: {len(cat_a_records)}")
            print()
            
            # Step 3: Owner Analysis
            print("STEP 3: OWNER IDENTIFICATION")
            if 'cf' in df_raw.columns:
                # All owners
                all_owners = df_raw['cf'].nunique()
                print(f"  Total Unique Owners: {all_owners}")
                
                # Owners from Category A properties
                cat_a_owners = cat_a_records['cf'].nunique() if 'cat_a_records' in locals() else 0
                print(f"  Owners from Category A: {cat_a_owners}")
                
                # Owner-parcel relationships
                owner_parcel_pairs = len(cat_a_records) if 'cat_a_records' in locals() else 0
                print(f"  Owner-Parcel Records: {owner_parcel_pairs}")
                
                # Multiple ownership analysis
                parcel_owner_counts = cat_a_records.groupby(['comune_input', 'foglio_input', 'particella_input'])['cf'].nunique() if 'cat_a_records' in locals() else pd.Series()
                if len(parcel_owner_counts) > 0:
                    avg_owners_per_parcel = parcel_owner_counts.mean()
                    max_owners_per_parcel = parcel_owner_counts.max()
                    print(f"  Average owners per parcel: {avg_owners_per_parcel:.2f}")
                    print(f"  Max owners per parcel: {max_owners_per_parcel}")
            print()
        
        # 2. ADDRESS PROCESSING ANALYSIS
        print("STEP 4: ADDRESS PROCESSING")
        if 'All_Validation_Ready' in sheets:
            df_validation = sheets['All_Validation_Ready']
            print(f"  Validation Ready Contacts: {len(df_validation)}")
            
            # Address quality analysis
            if 'Routing_Channel' in df_validation.columns:
                routing_dist = df_validation['Routing_Channel'].value_counts()
                print("  Routing Distribution:")
                for routing, count in routing_dist.items():
                    percentage = (count / len(df_validation)) * 100
                    print(f"    {routing}: {count} ({percentage:.1f}%)")
            
            # Quality confidence analysis
            if 'Address_Confidence' in df_validation.columns:
                confidence_dist = df_validation['Address_Confidence'].value_counts()
                print("  Address Confidence Distribution:")
                for confidence, count in confidence_dist.items():
                    percentage = (count / len(df_validation)) * 100
                    print(f"    {confidence}: {count} ({percentage:.1f}%)")
        print()
        
        # 3. FINAL OUTPUT ANALYSIS
        print("STEP 5: FINAL OUTPUT GENERATION")
        if 'Final_Mailing_List' in sheets:
            df_final = sheets['Final_Mailing_List']
            print(f"  Final Mailing Entries: {len(df_final)}")
            
            # Analyze what makes it to final mailing
            if len(df_final) > 0:
                print("  Final Mailing Analysis:")
                if 'Municipality' in df_final.columns:
                    muni_dist = df_final['Municipality'].value_counts()
                    for muni, count in muni_dist.items():
                        print(f"    {muni}: {count} mailings")
        print()
        
        # 4. LOSS ANALYSIS
        print("🔍 DATA LOSS ANALYSIS:")
        print("-" * 50)
        
        steps = []
        if 'All_Raw_Data' in sheets:
            steps.append(("Raw Records", len(sheets['All_Raw_Data'])))
            
            # Calculate Category A records
            cat_a_count = len(df_raw[df_raw['classamento'].str.startswith('A', na=False)]) if 'classamento' in df_raw.columns else len(df_raw)
            steps.append(("Category A Records", cat_a_count))
        
        if 'All_Validation_Ready' in sheets:
            steps.append(("Validation Ready", len(sheets['All_Validation_Ready'])))
        
        if 'Final_Mailing_List' in sheets:
            steps.append(("Final Mailing", len(sheets['Final_Mailing_List'])))
        
        # Calculate losses between steps
        for i in range(len(steps)-1):
            current_step, current_count = steps[i]
            next_step, next_count = steps[i+1]
            loss = current_count - next_count
            loss_percentage = (loss / current_count) * 100 if current_count > 0 else 0
            retention_percentage = (next_count / current_count) * 100 if current_count > 0 else 0
            
            print(f"  {current_step} → {next_step}:")
            print(f"    {current_count} → {next_count} (lost {loss}, {loss_percentage:.1f}% loss, {retention_percentage:.1f}% retention)")
        
        print()
        
        # 5. BUSINESS LOGIC VALIDATION
        print("🧮 BUSINESS LOGIC VALIDATION:")
        print("-" * 50)
        
        # Validate funnel metrics
        if 'Enhanced_Funnel_Analysis' in sheets:
            df_funnel = sheets['Enhanced_Funnel_Analysis']
            
            print("Enhanced Funnel Validation:")
            for funnel_type in df_funnel['Funnel_Type'].unique():
                funnel_data = df_funnel[df_funnel['Funnel_Type'] == funnel_type]
                print(f"  {funnel_type} Pipeline:")
                
                for _, row in funnel_data.iterrows():
                    stage = row['Stage']
                    count = row['Count']
                    conversion = row.get('Conversion_Rate', 'N/A')
                    
                    print(f"    {stage}: {count} items ({conversion}% conversion)")
                print()
        
        # 6. MUNICIPALITY-LEVEL ANALYSIS
        print("🗺️ MUNICIPALITY-LEVEL BREAKDOWN:")
        print("-" * 50)
        
        if 'All_Raw_Data' in sheets and 'All_Validation_Ready' in sheets:
            municipalities = df_raw['comune_input'].unique()
            
            for comune in municipalities:
                print(f"  {comum}:")
                
                # Raw data for this municipality
                muni_raw = df_raw[df_raw['comune_input'] == comum]
                muni_parcels = muni_raw.groupby(['foglio_input', 'particella_input']).size()
                muni_owners = muni_raw['cf'].nunique()
                
                # Validation ready for this municipality  
                muni_validation = df_validation[df_validation['comune_input'] == comum] if 'comune_input' in df_validation.columns else pd.DataFrame()
                
                print(f"    Raw records: {len(muni_raw)}")
                print(f"    Unique parcels: {len(muni_parcels)}")
                print(f"    Unique owners: {muni_owners}")
                print(f"    Validation ready: {len(muni_validation)}")
                
                if len(muni_validation) > 0 and 'Routing_Channel' in muni_validation.columns:
                    routing = muni_validation['Routing_Channel'].value_counts()
                    for route, count in routing.items():
                        print(f"      {route}: {count}")
                print()
    
    except Exception as e:
        print(f"❌ Error analyzing workflow: {e}")

if __name__ == "__main__":
    # Path to your test campaign file  
    campaign_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_1807\LandAcquisition_Casalpusterlengo_Castiglione_20250703_1807_Results.xlsx"
    
    print("🚀 Starting Pipeline Workflow Analysis...")
    print()
    
    analyze_pipeline_workflow(campaign_file)
    
    print()
    print("="*80)
    print("WORKFLOW ANALYSIS COMPLETE - Please review findings above")
    print("="*80)