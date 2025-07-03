#!/usr/bin/env python3
"""
Verification Script for v2.9.6 Fixes
Run this to verify all fixes have been applied correctly
"""

import re

def verify_fixes():
    """Verify all v2.9.6 fixes have been applied correctly"""
    
    print("="*80)
    print("VERIFYING LAND ACQUISITION PIPELINE v2.9.6 FIXES")
    print("="*80)
    
    with open("land_acquisition_pipeline.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_verified = 0
    total_fixes = 5
    
    print("🔍 CHECKING APPLIED FIXES:")
    print("="*50)
    
    # Fix 1: Decimal formatting in area calculations
    print("1. Decimal/Comma Formatting Fixes:")
    
    if 'pd.to_numeric(private_area_df[\'Area\'].astype(str).str.replace(\',\', \'.\'), errors=\'coerce\').fillna(0).sum()' in content:
        print("   ✅ Private owner area calculation fixed")
        fixes_verified += 1
    else:
        print("   ❌ Private owner area calculation NOT fixed")
    
    if 'pd.to_numeric(company_area_df[\'Area\'].astype(str).str.replace(\',\', \'.\'), errors=\'coerce\').fillna(0).sum()' in content:
        print("   ✅ Company owner area calculation fixed")
    else:
        print("   ❌ Company owner area calculation NOT fixed")
    
    if 'pd.to_numeric(cat_a_area_df[\'Area\'].astype(str).str.replace(\',\', \'.\'), errors=\'coerce\').fillna(0).sum()' in content:
        print("   ✅ Cat.A filter area calculation fixed")
    else:
        print("   ❌ Cat.A filter area calculation NOT fixed")
    
    # Fix 2: Campaign Summary traceability columns
    print("\n2. Campaign Summary Traceability Columns:")
    
    if '"CP": municipality_data[\'CP\']' in content and '"comune": municipality_data[\'comune\']' in content and '"provincia": municipality_data.get(\'provincia\', \'\')' in content:
        print("   ✅ CP, comune, provincia columns added to Campaign_Summary")
        fixes_verified += 1
    else:
        print("   ❌ Traceability columns NOT added to Campaign_Summary")
    
    # Fix 3: Unique_Owner_Address_Pairs metric
    print("\n3. Unique_Owner_Address_Pairs Metric:")
    
    if 'len(validation_ready) if not validation_ready.empty else 0, # FIXED' in content:
        print("   ✅ Unique_Owner_Address_Pairs calculation fixed")
        fixes_verified += 1
    else:
        print("   ❌ Unique_Owner_Address_Pairs calculation NOT fixed")
    
    # Fix 4: Funnel Analysis provincia column
    print("\n4. Funnel Analysis Provincia Column:")
    
    if '"provincia": provincia, "Stage"' in content:
        print("   ✅ Provincia column added to Funnel_Analysis")
        fixes_verified += 1
    else:
        print("   ❌ Provincia column NOT added to Funnel_Analysis")
    
    # Fix 5: All_Companies_Found sheet always created
    print("\n5. All_Companies_Found Sheet:")
    
    if 'empty_companies_df = pd.DataFrame(columns=[\'CP\', \'comune\', \'provincia\', \'denominazione\', \'cf\', \'pec_email\', \'pec_status\'])' in content:
        print("   ✅ All_Companies_Found sheet always created (even if empty)")
        fixes_verified += 1
    else:
        print("   ❌ All_Companies_Found sheet fix NOT applied")
    
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    
    if fixes_verified == total_fixes:
        print(f"✅ ALL FIXES VERIFIED: {fixes_verified}/{total_fixes} fixes successfully applied!")
        print("\n🎯 NEXT STEPS:")
        print("1. Run a test campaign to verify functionality")
        print("2. Use analyze_campaign_output_v2.py to verify output structure")
        print("3. Check that all 5 sheets are present and correctly formatted")
        print("\n🚀 v2.9.6 is ready for testing!")
    else:
        print(f"⚠️  PARTIAL SUCCESS: {fixes_verified}/{total_fixes} fixes verified")
        print("❌ Some fixes may not have been applied correctly")
        print("📋 Review the verification output above for details")
    
    print("="*80)
    
    return fixes_verified == total_fixes

if __name__ == "__main__":
    verify_fixes()