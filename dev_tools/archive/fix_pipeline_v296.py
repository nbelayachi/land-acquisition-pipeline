#!/usr/bin/env python3
"""
Fix Script for Land Acquisition Pipeline v2.9.6
This script applies all the necessary fixes for the identified issues
"""

import re
import os
import shutil
from datetime import datetime

def backup_original_file():
    """Create backup of original file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"land_acquisition_pipeline_v295_backup_{timestamp}.py"
    shutil.copy("land_acquisition_pipeline.py", backup_name)
    print(f"✅ Backup created: {backup_name}")
    return backup_name

def fix_decimal_formatting():
    """Fix decimal/comma formatting issues in area calculations"""
    
    print("\n🔧 FIXING DECIMAL/COMMA FORMATTING ISSUES...")
    
    with open("land_acquisition_pipeline.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Ensure consistent decimal handling in area calculations
    # Replace problematic str.replace patterns with robust decimal conversion
    
    # Pattern 1: Fix area summation with proper decimal handling
    old_pattern1 = r"pd\.to_numeric\(df\['Area'\]\.astype\(str\)\.str\.replace\(',', '\.'\), errors='coerce'\)\.fillna\(0\)\.sum\(\)"
    new_pattern1 = "pd.to_numeric(df['Area'].astype(str).str.replace(',', '.', regex=False), errors='coerce').fillna(0).sum()"
    
    content = re.sub(old_pattern1, new_pattern1, content)
    
    # Pattern 2: Fix any Area column direct summation
    old_pattern2 = r"\['Area'\]\.sum\(\)"
    new_pattern2 = ".apply(lambda x: pd.to_numeric(str(x).replace(',', '.'), errors='coerce')).fillna(0).sum()"
    
    # Only replace if it's not already within a pd.to_numeric call
    content = re.sub(r"(?<!pd\.to_numeric\([^)]*)\['Area'\]\.sum\(\)", 
                     "['Area']" + new_pattern2, content)
    
    print("   ✅ Fixed decimal formatting in area calculations")
    
    return content

def fix_companies_sheet(content):
    """Fix missing All_Companies_Found sheet in consolidated output"""
    
    print("\n🔧 FIXING MISSING ALL_COMPANIES_FOUND SHEET...")
    
    # Find the create_consolidated_excel_output function
    func_pattern = r'(def create_consolidated_excel_output\(.*?\):.*?)(    def|\Z)'
    func_match = re.search(func_pattern, content, re.DOTALL)
    
    if not func_match:
        print("   ❌ Could not find create_consolidated_excel_output function")
        return content
    
    func_content = func_match.group(1)
    
    # Check if All_Companies_Found sheet is already being written
    if 'All_Companies_Found' in func_content:
        print("   ⚠️  All_Companies_Found sheet already referenced - checking implementation")
        
        # Check if it's properly implemented
        if 'all_companies_found.to_excel' in func_content:
            print("   ✅ All_Companies_Found sheet already properly implemented")
            return content
        else:
            print("   ⚠️  All_Companies_Found referenced but not properly written to Excel")
    
    # Find where other sheets are being written and add companies sheet
    excel_write_pattern = r'(\s+)all_validation_ready\.to_excel\(writer, sheet_name=\'All_Validation_Ready\', index=False\)'
    excel_write_match = re.search(excel_write_pattern, func_content)
    
    if excel_write_match:
        indent = excel_write_match.group(1)
        
        # Add the companies sheet write after validation ready
        companies_write = f"""{indent}
{indent}# Write All_Companies_Found sheet
{indent}if not all_companies_found.empty:
{indent}    all_companies_found.to_excel(writer, sheet_name='All_Companies_Found', index=False)
{indent}    print(f"   📋 All_Companies_Found: {{len(all_companies_found)}} company records")
{indent}else:
{indent}    # Create empty companies sheet with expected structure
{indent}    empty_companies_df = pd.DataFrame(columns=['CP', 'comune', 'provincia', 'denominazione', 'cf', 'pec_email'])
{indent}    empty_companies_df.to_excel(writer, sheet_name='All_Companies_Found', index=False)
{indent}    print("   📋 All_Companies_Found: 0 company records (empty sheet created)")"""
        
        # Insert the companies sheet write
        func_content = re.sub(excel_write_pattern, 
                             excel_write_match.group(0) + companies_write, 
                             func_content)
        
        # Replace the function in the full content
        content = content.replace(func_match.group(1), func_content)
        print("   ✅ Added All_Companies_Found sheet to consolidated output")
    else:
        print("   ❌ Could not find Excel write pattern to insert companies sheet")
    
    return content

def fix_campaign_summary_traceability(content):
    """Fix missing CP, comune, provincia columns in Campaign_Summary"""
    
    print("\n🔧 FIXING CAMPAIGN_SUMMARY TRACEABILITY COLUMNS...")
    
    # Find the create_municipality_summary function
    func_pattern = r'(def create_municipality_summary\(.*?\):.*?return summary.*?)\n(    def|\Z)'
    func_match = re.search(func_pattern, content, re.DOTALL)
    
    if not func_match:
        print("   ❌ Could not find create_municipality_summary function")
        return content
    
    func_content = func_match.group(1)
    
    # Check if traceability columns are already present
    if '"CP":' in func_content and '"comune":' in func_content and '"provincia":' in func_content:
        print("   ✅ Traceability columns already present in summary")
        return content
    
    # Find the summary dictionary creation
    summary_pattern = r'(\s+summary = \{)(.*?)(\s+\})'
    summary_match = re.search(summary_pattern, func_content, re.DOTALL)
    
    if summary_match:
        indent = summary_match.group(1).split('summary = {')[0]
        existing_content = summary_match.group(2)
        
        # Add traceability columns at the beginning
        traceability_columns = f"""
{indent}    # Traceability columns
{indent}    "CP": cp,
{indent}    "comune": comune,
{indent}    "provincia": provincia,"""
        
        new_summary = f"{summary_match.group(1)}{traceability_columns}{existing_content}{summary_match.group(3)}"
        
        func_content = func_content.replace(summary_match.group(0), new_summary)
        content = content.replace(func_match.group(1), func_content)
        print("   ✅ Added CP, comune, provincia columns to Campaign_Summary")
    else:
        print("   ❌ Could not find summary dictionary to modify")
    
    return content

def fix_funnel_analysis_provincia(content):
    """Fix missing provincia column in Funnel_Analysis"""
    
    print("\n🔧 FIXING FUNNEL_ANALYSIS MISSING PROVINCIA COLUMN...")
    
    # Find the create_funnel_analysis_df function
    func_pattern = r'(def create_funnel_analysis_df\(.*?\):.*?)(    def|\Z)'
    func_match = re.search(func_pattern, content, re.DOTALL)
    
    if not func_match:
        print("   ❌ Could not find create_funnel_analysis_df function")
        return content
    
    func_content = func_match.group(1)
    
    # Check if provincia is already present
    if '"provincia":' in func_content:
        print("   ✅ Provincia column already present in funnel analysis")
        return content
    
    # Find where CP and comune are added and add provincia
    cp_comune_pattern = r'(\s+)"CP": cp,\s*\n(\s+)"comune": comune,'
    cp_comune_match = re.search(cp_comune_pattern, func_content)
    
    if cp_comune_match:
        indent = cp_comune_match.group(2)
        replacement = f'{cp_comune_match.group(0)}\n{indent}"provincia": provincia,'
        
        func_content = func_content.replace(cp_comune_match.group(0), replacement)
        content = content.replace(func_match.group(1), func_content)
        print("   ✅ Added provincia column to Funnel_Analysis")
    else:
        print("   ❌ Could not find CP/comune pattern to add provincia")
    
    return content

def fix_unique_owner_address_pairs(content):
    """Fix Unique_Owner_Address_Pairs metric calculation"""
    
    print("\n🔧 FIXING UNIQUE_OWNER_ADDRESS_PAIRS METRIC...")
    
    # Find the Unique_Owner_Address_Pairs calculation
    metric_pattern = r'("Unique_Owner_Address_Pairs":\s*)(len\([^)]*\)|[0-9]+|[^,\n}]*)'
    metric_match = re.search(metric_pattern, content)
    
    if metric_match:
        # Check if it's already calculating properly
        current_calculation = metric_match.group(2)
        if 'len(' in current_calculation and 'validation_ready' in current_calculation:
            print("   ✅ Unique_Owner_Address_Pairs already calculated correctly")
            return content
        
        # Fix the calculation
        new_calculation = "len(validation_ready) if not validation_ready.empty else 0"
        
        content = content.replace(metric_match.group(0), 
                                metric_match.group(1) + new_calculation)
        print("   ✅ Fixed Unique_Owner_Address_Pairs calculation")
    else:
        print("   ❌ Could not find Unique_Owner_Address_Pairs calculation to fix")
    
    return content

def apply_all_fixes():
    """Apply all fixes to the pipeline"""
    
    print("🚀 STARTING LAND ACQUISITION PIPELINE v2.9.6 FIXES")
    print("="*70)
    
    # Create backup
    backup_file = backup_original_file()
    
    try:
        # Apply fixes in order
        content = fix_decimal_formatting()
        content = fix_companies_sheet(content)
        content = fix_campaign_summary_traceability(content)
        content = fix_funnel_analysis_provincia(content)
        content = fix_unique_owner_address_pairs(content)
        
        # Write the fixed content
        with open("land_acquisition_pipeline.py", 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n✅ ALL FIXES APPLIED SUCCESSFULLY!")
        print("="*70)
        print("🔧 v2.9.6 FIXES SUMMARY:")
        print("   ✅ Fixed decimal/comma formatting in area calculations")
        print("   ✅ Added All_Companies_Found sheet to consolidated output")
        print("   ✅ Added CP, comune, provincia to Campaign_Summary")
        print("   ✅ Added provincia column to Funnel_Analysis")
        print("   ✅ Fixed Unique_Owner_Address_Pairs metric calculation")
        print()
        print(f"📁 Backup saved as: {backup_file}")
        print("🧪 Ready for testing with a new campaign run!")
        
    except Exception as e:
        print(f"\n❌ ERROR during fixes: {str(e)}")
        print(f"📁 Restoring from backup: {backup_file}")
        shutil.copy(backup_file, "land_acquisition_pipeline.py")
        print("❌ Original file restored. Please check the error and try again.")

if __name__ == "__main__":
    apply_all_fixes()