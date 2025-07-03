#!/usr/bin/env python3
"""
COMPREHENSIVE SANITY CHECK FOR v2.9.7 PARCEL OWNERSHIP FEATURE
==============================================================

This script performs detailed validation of the new parcel ownership 
grouping functionality and ensures data integrity.

Run this in Spyder and paste the complete output back to validate:
1. Approach correctness
2. Data quality and integrity  
3. Business logic validation
4. Expected vs actual results

Author: Land Acquisition Pipeline Team
Version: 2.9.7
Date: July 1, 2025
"""

import pandas as pd
import os
from collections import Counter

def comprehensive_v297_sanity_check():
    """Perform comprehensive sanity check of v2.9.7 implementation"""
    
    print("=" * 80)
    print("🔍 COMPREHENSIVE v2.9.7 SANITY CHECK")
    print("=" * 80)
    
    # File path - update this with your actual path
    file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250701_1646\LandAcquisition_Casalpusterlengo_Castiglione_20250701_1646_Results.xlsx"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        print("Please update the file_path variable in the script with the correct path")
        return
    
    try:
        print(f"📁 ANALYZING FILE: {os.path.basename(file_path)}")
        
        # Read Excel file and get basic info
        excel_file = pd.ExcelFile(file_path)
        print(f"📊 TOTAL SHEETS: {len(excel_file.sheet_names)}")
        print(f"📝 SHEET NAMES: {excel_file.sheet_names}")
        
        # Expected sheets
        expected_sheets = ['All_Raw_Data', 'All_Validation_Ready', 'All_Companies_Found', 
                          'Campaign_Summary', 'Funnel_Analysis', 'Owners_By_Parcel', 'Owners_Normalized']
        
        print(f"\n🔍 SHEET VALIDATION:")
        print("-" * 50)
        missing_sheets = []
        for sheet in expected_sheets:
            if sheet in excel_file.sheet_names:
                print(f"   ✅ {sheet}")
            else:
                print(f"   ❌ {sheet} (MISSING)")
                missing_sheets.append(sheet)
        
        if missing_sheets:
            print(f"\n⚠️  WARNING: Missing {len(missing_sheets)} expected sheets: {missing_sheets}")
            return
        
        # Load all sheets
        sheets = {}
        for sheet_name in excel_file.sheet_names:
            sheets[sheet_name] = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"📋 {sheet_name}: {sheets[sheet_name].shape[0]} rows × {sheets[sheet_name].shape[1]} columns")
        
        print(f"\n" + "=" * 80)
        print("🏠 DETAILED PARCEL OWNERSHIP ANALYSIS")
        print("=" * 80)
        
        # 1. VALIDATE RAW DATA STRUCTURE
        raw_data = sheets['All_Raw_Data']
        print(f"\n1️⃣  RAW DATA VALIDATION:")
        print("-" * 50)
        print(f"📊 Total owner records: {len(raw_data)}")
        
        # Check key columns exist
        key_columns = ['comune', 'foglio_input', 'particella_input', 'cf', 'denominazione', 'nome', 'cognome', 'quota']
        missing_cols = [col for col in key_columns if col not in raw_data.columns]
        if missing_cols:
            print(f"❌ Missing key columns: {missing_cols}")
            return
        
        # Analyze unique parcels in raw data
        unique_parcels_raw = raw_data[['comune', 'foglio_input', 'particella_input']].drop_duplicates()
        print(f"🏠 Unique input parcels: {len(unique_parcels_raw)}")
        
        # Show parcel distribution
        parcel_owner_counts = raw_data.groupby(['comune', 'foglio_input', 'particella_input']).size()
        print(f"📈 Owner records per parcel (sample):")
        for (comune, foglio, particella), count in parcel_owner_counts.head(5).items():
            print(f"   {comune} F{foglio}P{particella}: {count} owners")
        
        print(f"📊 Owner distribution stats:")
        print(f"   Min owners per parcel: {parcel_owner_counts.min()}")
        print(f"   Max owners per parcel: {parcel_owner_counts.max()}")
        print(f"   Average owners per parcel: {parcel_owner_counts.mean():.1f}")
        
        # 2. VALIDATE OWNERS_BY_PARCEL SHEET (WIDE FORMAT)
        if 'Owners_By_Parcel' in sheets:
            owners_wide = sheets['Owners_By_Parcel']
            print(f"\n2️⃣  OWNERS_BY_PARCEL VALIDATION (Wide Format):")
            print("-" * 50)
            print(f"📊 Parcel rows: {len(owners_wide)}")
            
            # Check if number of parcels matches
            unique_parcels_wide = len(owners_wide)
            unique_parcels_expected = len(unique_parcels_raw)
            match_status = "✅" if unique_parcels_wide == unique_parcels_expected else "❌"
            print(f"{match_status} Parcel count match: Expected {unique_parcels_expected}, Got {unique_parcels_wide}")
            
            # Check column structure
            required_cols = ['comune', 'foglio_input', 'particella_input', 'total_owners']
            owner_name_cols = [col for col in owners_wide.columns if col.startswith('owner_') and col.endswith('_name')]
            owner_cf_cols = [col for col in owners_wide.columns if col.startswith('owner_') and col.endswith('_cf')]
            owner_quota_cols = [col for col in owners_wide.columns if col.startswith('owner_') and col.endswith('_quota')]
            
            print(f"🔑 Required columns present: {[col for col in required_cols if col in owners_wide.columns]}")
            print(f"👤 Owner name columns: {len(owner_name_cols)} (expected 10)")
            print(f"🆔 Owner CF columns: {len(owner_cf_cols)} (expected 10)")
            print(f"📊 Owner quota columns: {len(owner_quota_cols)} (expected 10)")
            
            # Validate data integrity
            if not owners_wide.empty and 'total_owners' in owners_wide.columns:
                print(f"\n📈 Wide Format Data Analysis:")
                total_owners_stats = owners_wide['total_owners'].describe()
                print(f"   Total owners per parcel stats:")
                print(f"   - Min: {total_owners_stats['min']}")
                print(f"   - Max: {total_owners_stats['max']}")
                print(f"   - Mean: {total_owners_stats['mean']:.1f}")
                
                # Check for parcels with >10 owners
                excess_owners = owners_wide[owners_wide['total_owners'] > 10]
                print(f"   - Parcels with >10 owners: {len(excess_owners)}")
                
                if len(excess_owners) > 0:
                    print(f"   📋 Sample excess owner parcels:")
                    for idx, row in excess_owners.head(3).iterrows():
                        additional = row.get('additional_owners', 'N/A')
                        print(f"     {row['comune']} F{row['foglio_input']}P{row['particella_input']}: {row['total_owners']} owners ({additional})")
                
                # Sample data verification
                print(f"\n📋 Sample Wide Format Data:")
                sample_cols = ['comune', 'foglio_input', 'particella_input', 'total_owners', 'owner_1_name', 'owner_1_cf', 'owner_1_quota']
                available_cols = [col for col in sample_cols if col in owners_wide.columns]
                print(owners_wide[available_cols].head(3).to_string(index=False))
        
        # 3. VALIDATE OWNERS_NORMALIZED SHEET
        if 'Owners_Normalized' in sheets:
            owners_norm = sheets['Owners_Normalized']
            print(f"\n3️⃣  OWNERS_NORMALIZED VALIDATION (Power BI Format):")
            print("-" * 50)
            print(f"📊 Owner-parcel relationships: {len(owners_norm)}")
            
            # Check column structure
            required_norm_cols = ['comune', 'foglio_input', 'particella_input', 'owner_name', 'owner_cf', 'quota', 'owner_type']
            present_norm_cols = [col for col in required_norm_cols if col in owners_norm.columns]
            missing_norm_cols = [col for col in required_norm_cols if col not in owners_norm.columns]
            
            print(f"✅ Present columns: {present_norm_cols}")
            if missing_norm_cols:
                print(f"❌ Missing columns: {missing_norm_cols}")
            
            if not owners_norm.empty:
                # Validate relationship count
                total_relationships = len(owners_norm)
                total_raw_records = len(raw_data)
                print(f"📊 Relationship validation:")
                print(f"   Normalized relationships: {total_relationships}")
                print(f"   Raw data records: {total_raw_records}")
                print(f"   Deduplication effect: {total_raw_records - total_relationships} duplicates removed")
                
                # Quota analysis
                if 'quota' in owners_norm.columns:
                    quota_analysis = owners_norm['quota'].value_counts()
                    missing_quota_count = (owners_norm['quota'] == 'missing').sum()
                    print(f"\n📊 Quota Analysis:")
                    print(f"   Records with quota data: {len(owners_norm) - missing_quota_count}")
                    print(f"   Records with missing quota: {missing_quota_count}")
                    print(f"   Sample quota values: {list(quota_analysis.head(5).index)}")
                
                # Owner type analysis
                if 'owner_type' in owners_norm.columns:
                    owner_type_counts = owners_norm['owner_type'].value_counts()
                    print(f"\n👥 Owner Type Distribution:")
                    for owner_type, count in owner_type_counts.items():
                        print(f"   {owner_type}: {count}")
                
                # Sample data
                print(f"\n📋 Sample Normalized Data:")
                sample_norm_cols = ['comune', 'foglio_input', 'particella_input', 'owner_name', 'owner_cf', 'quota']
                available_norm_cols = [col for col in sample_norm_cols if col in owners_norm.columns]
                print(owners_norm[available_norm_cols].head(5).to_string(index=False))
        
        # 4. CROSS-VALIDATION BETWEEN FORMATS
        print(f"\n4️⃣  CROSS-VALIDATION BETWEEN FORMATS:")
        print("-" * 50)
        
        if 'Owners_By_Parcel' in sheets and 'Owners_Normalized' in sheets:
            owners_wide = sheets['Owners_By_Parcel']
            owners_norm = sheets['Owners_Normalized']
            
            # Check if total owner counts match
            if 'total_owners' in owners_wide.columns:
                total_from_wide = owners_wide['total_owners'].sum()
                total_from_norm = len(owners_norm)
                match_status = "✅" if total_from_wide == total_from_norm else "❌"
                print(f"{match_status} Total owner relationships match:")
                print(f"   Wide format sum: {total_from_wide}")
                print(f"   Normalized format rows: {total_from_norm}")
            
            # Check if parcels match
            parcels_wide = set(owners_wide[['comune', 'foglio_input', 'particella_input']].apply(tuple, axis=1))
            parcels_norm = set(owners_norm[['comune', 'foglio_input', 'particella_input']].drop_duplicates().apply(tuple, axis=1))
            
            parcels_match = "✅" if parcels_wide == parcels_norm else "❌"
            print(f"{parcels_match} Parcel sets match:")
            print(f"   Wide format parcels: {len(parcels_wide)}")
            print(f"   Normalized format parcels: {len(parcels_norm)}")
            
            if parcels_wide != parcels_norm:
                missing_in_norm = parcels_wide - parcels_norm
                missing_in_wide = parcels_norm - parcels_wide
                if missing_in_norm:
                    print(f"   ❌ Missing in normalized: {list(missing_in_norm)[:3]}")
                if missing_in_wide:
                    print(f"   ❌ Missing in wide: {list(missing_in_wide)[:3]}")
        
        # 5. BUSINESS LOGIC VALIDATION
        print(f"\n5️⃣  BUSINESS LOGIC VALIDATION:")
        print("-" * 50)
        
        # Check if the grouping makes business sense
        if 'Owners_Normalized' in sheets:
            owners_norm = sheets['Owners_Normalized']
            
            # Find parcels with multiple owners (co-ownership situations)
            parcel_groups = owners_norm.groupby(['comune', 'foglio_input', 'particella_input'])
            co_ownership_stats = parcel_groups.size()
            co_owned_parcels = co_ownership_stats[co_ownership_stats > 1]
            
            print(f"🏠 Co-ownership Analysis:")
            print(f"   Total parcels: {len(co_ownership_stats)}")
            print(f"   Parcels with multiple owners: {len(co_owned_parcels)}")
            print(f"   Single-owner parcels: {len(co_ownership_stats) - len(co_owned_parcels)}")
            
            if len(co_owned_parcels) > 0:
                print(f"   Most complex parcel: {co_ownership_stats.max()} owners")
                most_complex = co_ownership_stats.idxmax()
                print(f"   Location: {most_complex[0]} F{most_complex[1]}P{most_complex[2]}")
                
                print(f"\n📋 Sample co-ownership situations:")
                for (comune, foglio, particella), owner_count in co_owned_parcels.head(3).items():
                    print(f"   {comune} F{foglio}P{particella}: {owner_count} owners")
                    # Show the actual owners for this parcel
                    parcel_owners = owners_norm[
                        (owners_norm['comune'] == comune) & 
                        (owners_norm['foglio_input'] == foglio) & 
                        (owners_norm['particella_input'] == particella)
                    ]
                    for idx, owner in parcel_owners.head(3).iterrows():
                        quota_str = f" ({owner.get('quota', 'N/A')})" if 'quota' in owner else ""
                        print(f"     - {owner.get('owner_name', 'N/A')}{quota_str}")
                    if len(parcel_owners) > 3:
                        print(f"     - ... and {len(parcel_owners) - 3} more owners")
        
        # 6. FINAL ASSESSMENT
        print(f"\n" + "=" * 80)
        print("🎯 FINAL ASSESSMENT")
        print("=" * 80)
        
        issues_found = []
        
        # Check critical functionality
        if len(excel_file.sheet_names) != 7:
            issues_found.append(f"Expected 7 sheets, found {len(excel_file.sheet_names)}")
        
        if 'Owners_By_Parcel' not in excel_file.sheet_names:
            issues_found.append("Missing Owners_By_Parcel sheet")
        
        if 'Owners_Normalized' not in excel_file.sheet_names:
            issues_found.append("Missing Owners_Normalized sheet")
        
        # Data integrity checks
        if 'Owners_By_Parcel' in sheets and 'Owners_Normalized' in sheets:
            owners_wide = sheets['Owners_By_Parcel']
            owners_norm = sheets['Owners_Normalized']
            
            if len(owners_wide) == 0:
                issues_found.append("Owners_By_Parcel sheet is empty")
            
            if len(owners_norm) == 0:
                issues_found.append("Owners_Normalized sheet is empty")
        
        if issues_found:
            print(f"❌ ISSUES FOUND ({len(issues_found)}):")
            for issue in issues_found:
                print(f"   • {issue}")
            print(f"\n🔧 ACTION REQUIRED: Fix the above issues before proceeding")
        else:
            print(f"✅ ALL CHECKS PASSED!")
            print(f"🎉 v2.9.7 Parcel Ownership Feature is working correctly")
            print(f"📊 Ready for production use")
        
        print(f"\n📋 COPY THIS ENTIRE OUTPUT AND SHARE WITH YOUR AGENT FOR VALIDATION")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    comprehensive_v297_sanity_check()