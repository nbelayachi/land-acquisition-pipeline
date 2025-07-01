#!/usr/bin/env python3
"""
Test and Report Script for v2.9.6 Fixes
This script will verify fixes AND run analysis on your campaign output
"""

import re
import os
from datetime import datetime

def create_comprehensive_report():
    """Create a comprehensive report of v2.9.6 status"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"v296_verification_report_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        def output(text=""):
            print(text)
            print(text, file=f)
        
        output("="*80)
        output("LAND ACQUISITION PIPELINE v2.9.6 - COMPREHENSIVE VERIFICATION REPORT")
        output("="*80)
        output(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output()
        
        # PART 1: Verify code fixes
        output("PART 1: CODE FIX VERIFICATION")
        output("="*50)
        
        try:
            with open("land_acquisition_pipeline.py", 'r', encoding='utf-8') as code_file:
                content = code_file.read()
            
            fixes_verified = 0
            total_fixes = 5
            
            # Fix 1: Decimal formatting
            output("1. Decimal/Comma Formatting Fixes:")
            if 'pd.to_numeric(private_area_df[\'Area\'].astype(str).str.replace(\',\', \'.\'), errors=\'coerce\').fillna(0).sum()' in content:
                output("   ✅ Private owner area calculation fixed")
                fixes_verified += 1
            else:
                output("   ❌ Private owner area calculation NOT fixed")
            
            if 'pd.to_numeric(cat_a_area_df[\'Area\'].astype(str).str.replace(\',\', \'.\'), errors=\'coerce\').fillna(0).sum()' in content:
                output("   ✅ Cat.A filter area calculation fixed")
            else:
                output("   ❌ Cat.A filter area calculation NOT fixed")
            
            # Fix 2: Campaign Summary traceability
            output("\n2. Campaign Summary Traceability:")
            if '"CP": municipality_data[\'CP\']' in content and '"comune": municipality_data[\'comune\']' in content:
                output("   ✅ CP, comune, provincia columns added")
                fixes_verified += 1
            else:
                output("   ❌ Traceability columns NOT added")
            
            # Fix 3: Unique_Owner_Address_Pairs
            output("\n3. Unique_Owner_Address_Pairs Metric:")
            if 'len(validation_ready) if not validation_ready.empty else 0, # FIXED' in content:
                output("   ✅ Unique_Owner_Address_Pairs calculation fixed")
                fixes_verified += 1
            else:
                output("   ❌ Unique_Owner_Address_Pairs calculation NOT fixed")
            
            # Fix 4: Funnel Analysis provincia
            output("\n4. Funnel Analysis Provincia Column:")
            if '"provincia": provincia, "Stage"' in content:
                output("   ✅ Provincia column added to Funnel_Analysis")
                fixes_verified += 1
            else:
                output("   ❌ Provincia column NOT added")
            
            # Fix 5: Companies sheet
            output("\n5. All_Companies_Found Sheet:")
            if 'empty_companies_df = pd.DataFrame(columns=[\'CP\', \'comune\', \'provincia\', \'denominazione\', \'cf\', \'pec_email\', \'pec_status\'])' in content:
                output("   ✅ All_Companies_Found sheet always created")
                fixes_verified += 1
            else:
                output("   ❌ All_Companies_Found sheet fix NOT applied")
            
            output(f"\n📊 CODE VERIFICATION RESULT: {fixes_verified}/{total_fixes} fixes applied")
            
        except Exception as e:
            output(f"❌ Error verifying code: {str(e)}")
        
        output("\n" + "="*50)
        output("PART 2: CAMPAIGN OUTPUT ANALYSIS")
        output("="*50)
        output()
        output("INSTRUCTIONS FOR USER:")
        output("1. Run a test campaign with the fixed pipeline")
        output("2. Note the path to the generated Excel file")
        output("3. Run the following commands and paste results below:")
        output()
        output("# Command 1: Analyze campaign output")
        output("exec(open('analyze_campaign_output_v2.py').read())")
        output()
        output("# When prompted, enter the path to your campaign Excel file")
        output("# Then copy the ENTIRE output and paste it in this section:")
        output()
        output("CAMPAIGN OUTPUT ANALYSIS RESULTS:")
        output("-" * 40)
        output("(PASTE YOUR analyze_campaign_output_v2.py RESULTS HERE)")
        output()
        output()
        output("="*50)
        output("PART 3: EXPECTED vs ACTUAL VERIFICATION")
        output("="*50)
        output()
        output("After pasting your campaign analysis above, check these points:")
        output()
        output("✅ EXPECTED RESULTS:")
        output("  - All 5 sheets present: All_Raw_Data, All_Validation_Ready, All_Companies_Found, Campaign_Summary, Funnel_Analysis")
        output("  - Campaign_Summary has CP, comune, provincia columns")
        output("  - Funnel_Analysis has provincia column")
        output("  - All_Companies_Found sheet exists (even if empty)")
        output("  - Area calculations show realistic hectare values (not nonsense decimals)")
        output("  - Unique_Owner_Address_Pairs shows actual count (not 0)")
        output()
        output("❌ ISSUES TO REPORT:")
        output("  - Missing sheets")
        output("  - Missing columns")
        output("  - Wrong decimal calculations")
        output("  - Any errors during campaign run")
        output()
        output("="*80)
        output("END OF AUTOMATED REPORT")
        output("="*80)
        output()
        output("📋 NEXT STEPS:")
        output("1. Follow the instructions in PART 2 above")
        output("2. Copy this entire file content and share with your agent")
        output("3. Agent will verify the fixes worked correctly")
        output()
    
    print(f"\n📁 Verification report created: {report_file}")
    print("📋 Follow the instructions in the report file, then share the complete file content!")
    
    return report_file

if __name__ == "__main__":
    create_comprehensive_report()