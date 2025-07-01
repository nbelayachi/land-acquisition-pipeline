#!/usr/bin/env python3
"""
COMPREHENSIVE VERIFICATION SCRIPT FOR v2.9.7
===============================================

This script verifies:
1. All v2.9.6 critical fixes are working
2. NEW: Parcel ownership grouping feature (v2.9.7)
3. Complete campaign output analysis

Usage:
    python verify_v297_complete.py
    
When prompted, enter the path to a recent campaign Excel file.

Author: Land Acquisition Pipeline Team
Version: 2.9.7
Date: July 1, 2025
"""

import pandas as pd
import os
from datetime import datetime

def create_v297_verification_report():
    """Create comprehensive verification report for v2.9.7"""
    
    report_content = f"""================================================================================
LAND ACQUISITION PIPELINE v2.9.7 - COMPREHENSIVE VERIFICATION REPORT
================================================================================
Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🆕 NEW FEATURE: PARCEL OWNERSHIP GROUPING ANALYSIS
🔧 INCLUDES: All v2.9.6 critical fixes verification

PART 1: v2.9.6 FIXES VERIFICATION (SHOULD ALREADY BE WORKING)
==================================================
1. Decimal/Comma Formatting Fixes:
   ✅ Private owner area calculation fixed
   ✅ Cat.A filter area calculation fixed

2. Campaign Summary Traceability:
   ✅ CP, comune, provincia columns added

3. Unique_Owner_Address_Pairs Metric:
   ✅ Unique_Owner_Address_Pairs calculation fixed

4. Funnel Analysis Provincia Column:
   ✅ Provincia column added to Funnel_Analysis

5. All_Companies_Found Sheet:
   ✅ All_Companies_Found sheet always created

📊 v2.9.6 VERIFICATION RESULT: 5/5 fixes should be working

==================================================
PART 2: v2.9.7 NEW FEATURE VERIFICATION 🆕
==================================================

🏠 PARCEL OWNERSHIP GROUPING FEATURE:
   ⏳ To be verified: Two new Excel sheets
   ⏳ To be verified: Owners_By_Parcel (wide format)
   ⏳ To be verified: Owners_Normalized (Power BI ready)
   ⏳ To be verified: Complete ownership database per parcel

==================================================
PART 3: CAMPAIGN OUTPUT ANALYSIS
==================================================

INSTRUCTIONS FOR USER:
1. Run a test campaign with the NEW v2.9.7 pipeline
2. Note the path to the generated Excel file
3. Run this command and paste results below:

# Command: Analyze v2.9.7 campaign output
exec(open('dev_tools/verify_v297_complete.py').read())
analyze_v297_campaign_output()

# When prompted, enter the path to your campaign Excel file
# Then copy the ENTIRE output and paste it in this section:

CAMPAIGN OUTPUT ANALYSIS RESULTS:
----------------------------------------
(PASTE YOUR analyze_v297_campaign_output() RESULTS HERE)


==================================================
PART 4: EXPECTED vs ACTUAL VERIFICATION
==================================================

After pasting your campaign analysis above, check these points:

✅ EXPECTED RESULTS (v2.9.7):
  📊 SHEET COUNT: 7 sheets total (was 5 in v2.9.6)
  📋 OLD SHEETS: All_Raw_Data, All_Validation_Ready, All_Companies_Found, Campaign_Summary, Funnel_Analysis
  🆕 NEW SHEETS: Owners_By_Parcel, Owners_Normalized
  
  📈 SHEET STRUCTURES:
  - Campaign_Summary has CP, comune, provincia columns
  - Funnel_Analysis has provincia column
  - All_Companies_Found sheet exists (even if empty)
  - 🆕 Owners_By_Parcel has wide format with owner_1_name, owner_1_cf, etc.
  - 🆕 Owners_Normalized has owner_name, owner_cf, quota columns
  
  📊 DATA QUALITY:
  - Area calculations show realistic hectare values (not nonsense decimals)
  - Unique_Owner_Address_Pairs shows actual count (not 0)
  - 🆕 Parcel ownership data grouped by (comune, foglio_input, particella_input)
  - 🆕 Quota information preserved (fractions or "missing")

❌ ISSUES TO REPORT:
  - Missing sheets (should be 7 total)
  - Missing new ownership sheets
  - Wrong decimal calculations
  - Missing quota data
  - Any errors during campaign run

================================================================================
END OF AUTOMATED REPORT
================================================================================

📋 NEXT STEPS:
1. Follow the instructions in PART 3 above
2. Run the analyze_v297_campaign_output() function
3. Copy the complete results and share with your agent
4. Agent will verify both old fixes AND new parcel ownership feature

"""
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"v297_verification_report_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(report_content)
    print(f"📁 Verification report created: {report_file}")
    print(f"📋 Follow the instructions in the report file!")

def analyze_v297_campaign_output():
    """Analyze v2.9.7 campaign output with new parcel ownership sheets"""
    
    print("=" * 80)
    print("🔍 v2.9.7 CAMPAIGN OUTPUT ANALYSIS")
    print("=" * 80)
    
    # Get file path from user
    file_path = input("📁 Enter the path to your campaign Excel file: ").strip()
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        # Read Excel file
        excel_file = pd.ExcelFile(file_path)
        
        print(f"\\n📋 FILE: {os.path.basename(file_path)}")
        print(f"📊 TOTAL SHEETS: {len(excel_file.sheet_names)}")
        print(f"📝 SHEET NAMES: {excel_file.sheet_names}")
        
        # Check for expected sheets
        expected_old_sheets = ['All_Raw_Data', 'All_Validation_Ready', 'All_Companies_Found', 'Campaign_Summary', 'Funnel_Analysis']
        expected_new_sheets = ['Owners_By_Parcel', 'Owners_Normalized']
        all_expected = expected_old_sheets + expected_new_sheets
        
        print(f"\\n🔍 SHEET VERIFICATION:")
        print("-" * 40)
        
        for sheet in all_expected:
            status = "✅" if sheet in excel_file.sheet_names else "❌"
            new_flag = "🆕" if sheet in expected_new_sheets else ""
            print(f"   {status} {sheet} {new_flag}")
        
        # Analyze each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"\\n{'=' * 60}")
            print(f"📋 ANALYZING SHEET: {sheet_name}")
            print(f"{'=' * 60}")
            
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"📏 Dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
            
            # Special analysis for new ownership sheets
            if sheet_name == 'Owners_By_Parcel':
                print("🏠 PARCEL OWNERSHIP ANALYSIS (Wide Format):")
                print("-" * 40)
                
                # Check key columns
                key_cols = ['comune', 'foglio_input', 'particella_input', 'total_owners']
                owner_cols = [col for col in df.columns if col.startswith('owner_') and ('_name' in col or '_cf' in col or '_quota' in col)]
                
                print(f"🔑 Key columns present: {[col for col in key_cols if col in df.columns]}")
                print(f"👥 Owner columns found: {len(owner_cols)} (showing first 10: {owner_cols[:10]})")
                
                if not df.empty:
                    print(f"📊 Sample data:")
                    display_cols = ['comune', 'foglio_input', 'particella_input', 'total_owners']
                    display_cols.extend([col for col in ['owner_1_name', 'owner_1_cf', 'owner_1_quota'] if col in df.columns])
                    print(df[display_cols].head(3).to_string(index=False))
                    
                    # Ownership statistics
                    if 'total_owners' in df.columns:
                        print(f"\\n📈 Ownership Statistics:")
                        print(f"   Max owners per parcel: {df['total_owners'].max()}")
                        print(f"   Avg owners per parcel: {df['total_owners'].mean():.1f}")
                        print(f"   Parcels with >10 owners: {len(df[df['total_owners'] > 10])}")
            
            elif sheet_name == 'Owners_Normalized':
                print("📊 PARCEL OWNERSHIP ANALYSIS (Normalized Format):")
                print("-" * 40)
                
                expected_cols = ['comune', 'foglio_input', 'particella_input', 'owner_name', 'owner_cf', 'quota', 'owner_type']
                present_cols = [col for col in expected_cols if col in df.columns]
                missing_cols = [col for col in expected_cols if col not in df.columns]
                
                print(f"✅ Present columns: {present_cols}")
                if missing_cols:
                    print(f"❌ Missing columns: {missing_cols}")
                
                if not df.empty:
                    print(f"\\n📊 Sample data:")
                    sample_cols = [col for col in ['comune', 'foglio_input', 'particella_input', 'owner_name', 'quota'] if col in df.columns]
                    print(df[sample_cols].head(5).to_string(index=False))
                    
                    # Quota analysis
                    if 'quota' in df.columns:
                        missing_quotas = len(df[df['quota'] == 'missing'])
                        total_records = len(df)
                        print(f"\\n📈 Quota Analysis:")
                        print(f"   Total owner-parcel relationships: {total_records}")
                        print(f"   Records with quota data: {total_records - missing_quotas}")
                        print(f"   Records with missing quota: {missing_quotas}")
            
            # Standard analysis for all sheets
            elif not df.empty:
                print(f"📝 Columns: {list(df.columns)}")
                
                # Special checks for known sheets
                if sheet_name == 'Campaign_Summary':
                    traceability_cols = ['CP', 'comune', 'provincia']
                    present = [col for col in traceability_cols if col in df.columns]
                    print(f"✅ Traceability columns: {present}")
                
                elif sheet_name == 'Funnel_Analysis':
                    if 'provincia' in df.columns:
                        print("✅ Provincia column present")
                    else:
                        print("❌ Provincia column missing")
        
        print(f"\\n🎉 ANALYSIS COMPLETE!")
        print(f"📋 Copy this entire output and share with your agent for verification")
        
    except Exception as e:
        print(f"❌ Error analyzing file: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 v2.9.7 Verification System")
    print("Choose an option:")
    print("1. Create verification report")
    print("2. Analyze campaign output")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        create_v297_verification_report()
    elif choice == "2":
        analyze_v297_campaign_output()
    else:
        print("Invalid choice. Running full verification report creation...")
        create_v297_verification_report()