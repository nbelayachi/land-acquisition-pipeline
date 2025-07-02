"""
Simple Analysis of v3.0.0 Results
Clean version without unicode issues
"""

import pandas as pd
import os

# Analyze the new campaign results
results_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250702_0018\LandAcquisition_Casalpusterlengo_Castiglione_20250702_0018_Results.xlsx"

print("ANALYZING v3.0.0 CAMPAIGN RESULTS")
print("=" * 50)
print(f"File: {os.path.basename(results_file)}")

try:
    # Read all sheets
    excel_file = pd.ExcelFile(results_file)
    print(f"Available sheets: {excel_file.sheet_names}")
    print(f"Total sheets: {len(excel_file.sheet_names)}")
    print()
    
    # Check for Strategic_Mailing_List (new feature)
    if 'Strategic_Mailing_List' in excel_file.sheet_names:
        print("NEW FEATURE DETECTED: Strategic_Mailing_List")
        strategic_df = pd.read_excel(results_file, sheet_name='Strategic_Mailing_List')
        print(f"   Rows: {len(strategic_df)}")
        print(f"   Columns: {list(strategic_df.columns)}")
        print()
        
        if len(strategic_df) > 0:
            print("   Sample data:")
            for idx, row in strategic_df.head(3).iterrows():
                municipality = row.get('Municipality', 'N/A')
                name = row.get('Full_Name', 'N/A')
                address = row.get('Mailing_Address', 'N/A')
                print(f"     {municipality} | {name} | {address[:50]}...")
        print()
    
    # Analyze enhanced classification
    if 'All_Validation_Ready' in excel_file.sheet_names:
        validation_df = pd.read_excel(results_file, sheet_name='All_Validation_Ready')
        print("ENHANCED CLASSIFICATION ANALYSIS")
        print("-" * 35)
        print(f"Total addresses: {len(validation_df)}")
        
        # Check confidence distribution
        if 'Address_Confidence' in validation_df.columns:
            confidence_counts = validation_df['Address_Confidence'].value_counts()
            print("\nConfidence Distribution:")
            for level, count in confidence_counts.items():
                percentage = (count / len(validation_df)) * 100
                print(f"   {level}: {count} ({percentage:.1f}%)")
            
            # Check for ULTRA_HIGH (new feature)
            ultra_high_count = confidence_counts.get('ULTRA_HIGH', 0)
            if ultra_high_count > 0:
                print(f"\nULTRA_HIGH CONFIDENCE DETECTED: {ultra_high_count} addresses")
                print("These are ready for immediate printing!")
                
                # Show samples
                ultra_addresses = validation_df[validation_df['Address_Confidence'] == 'ULTRA_HIGH']
                print("Sample ULTRA_HIGH addresses:")
                for idx, row in ultra_addresses.head(3).iterrows():
                    original = row.get('cleaned_ubicazione', 'N/A')
                    geocoded = row.get('Geocoded_Address_Italian', 'N/A')
                    print(f"   {original[:45]}...")
                    print(f"   -> {geocoded[:45]}...")
        
        # Check classification method
        if 'Classification_Method' in validation_df.columns:
            method_counts = validation_df['Classification_Method'].value_counts()
            print(f"\nClassification Methods:")
            for method, count in method_counts.items():
                print(f"   {method}: {count} addresses")
        
        # Routing analysis
        if 'Routing_Channel' in validation_df.columns:
            routing_counts = validation_df['Routing_Channel'].value_counts()
            print(f"\nRouting Distribution:")
            for channel, count in routing_counts.items():
                percentage = (count / len(validation_df)) * 100
                print(f"   {channel}: {count} ({percentage:.1f}%)")
        
        print()
    
    # Time savings calculation
    if 'Address_Confidence' in validation_df.columns:
        ultra_high = len(validation_df[validation_df['Address_Confidence'] == 'ULTRA_HIGH'])
        high = len(validation_df[validation_df['Address_Confidence'] == 'HIGH'])
        medium = len(validation_df[validation_df['Address_Confidence'] == 'MEDIUM'])
        low = len(validation_df[validation_df['Address_Confidence'] == 'LOW'])
        total = len(validation_df)
        
        print("TIME SAVINGS ANALYSIS")
        print("-" * 25)
        print(f"ULTRA_HIGH (0 min review): {ultra_high} addresses")
        print(f"HIGH (5 min review): {high} addresses") 
        print(f"MEDIUM (8 min review): {medium} addresses")
        print(f"LOW (agency): {low} addresses")
        print()
        
        # Calculate time
        old_time = total * 8  # 8 minutes per address
        new_time = (ultra_high * 0) + (high * 5) + (medium * 8) + (low * 0)
        time_saved = old_time - new_time
        efficiency = (time_saved / old_time) * 100 if old_time > 0 else 0
        
        print(f"Traditional review time: {old_time} minutes ({old_time/60:.1f} hours)")
        print(f"Enhanced review time: {new_time} minutes ({new_time/60:.1f} hours)")
        print(f"Time savings: {time_saved} minutes ({efficiency:.1f}% improvement)")
        print(f"Immediate print ready: {ultra_high}/{total} ({ultra_high/total*100:.1f}%)")
    
    print("\nAnalysis complete!")
    
except Exception as e:
    print(f"Error: {str(e)}")
    
# Compare with old version if available
print("\n" + "="*50)
print("COMPARING WITH PREVIOUS VERSION")
print("="*50)

old_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2018\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2018_Results.xlsx"

try:
    old_excel = pd.ExcelFile(old_file)
    new_excel = pd.ExcelFile(results_file)
    
    print(f"Old version sheets: {len(old_excel.sheet_names)}")
    print(f"New version sheets: {len(new_excel.sheet_names)}")
    
    # Find new sheets
    old_sheets = set(old_excel.sheet_names)
    new_sheets = set(new_excel.sheet_names)
    added_sheets = new_sheets - old_sheets
    
    if added_sheets:
        print(f"NEW SHEETS ADDED: {list(added_sheets)}")
    
    # Compare confidence distributions
    if 'All_Validation_Ready' in old_sheets and 'All_Validation_Ready' in new_sheets:
        old_val = pd.read_excel(old_file, sheet_name='All_Validation_Ready')
        new_val = pd.read_excel(results_file, sheet_name='All_Validation_Ready')
        
        print(f"\nValidation Ready Comparison:")
        print(f"Old: {len(old_val)} addresses")
        print(f"New: {len(new_val)} addresses")
        
        if 'Address_Confidence' in old_val.columns and 'Address_Confidence' in new_val.columns:
            old_conf = old_val['Address_Confidence'].value_counts()
            new_conf = new_val['Address_Confidence'].value_counts()
            
            print(f"\nConfidence Changes:")
            all_levels = set(old_conf.index) | set(new_conf.index)
            for level in sorted(all_levels):
                old_count = old_conf.get(level, 0)
                new_count = new_conf.get(level, 0)
                change = new_count - old_count
                change_str = f"+{change}" if change > 0 else str(change)
                print(f"   {level}: {old_count} -> {new_count} ({change_str})")

except Exception as e:
    print(f"Comparison error: {str(e)}")

print("\nAll analysis complete!")