#!/usr/bin/env python3
"""
Diagnostic Script for Land Acquisition Pipeline v2.9.5 Issues
Run this in Spyder to identify the specific problems in the code
"""

import re
import os

def analyze_pipeline_code():
    """Analyze the main pipeline file to find the issues"""
    
    print("="*80)
    print("LAND ACQUISITION PIPELINE v2.9.5 - CODE DIAGNOSTIC")
    print("="*80)
    
    # Read the main pipeline file
    pipeline_file = "land_acquisition_pipeline.py"
    
    if not os.path.exists(pipeline_file):
        print("❌ ERROR: land_acquisition_pipeline.py not found!")
        return
    
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    print("📁 File loaded successfully")
    print(f"📊 File size: {len(code)} characters")
    print()
    
    # 1. Find create_consolidated_excel_output function
    print("🔍 SEARCHING FOR CONSOLIDATION FUNCTIONS:")
    print("="*50)
    
    consolidated_func = re.search(r'def create_consolidated_excel_output\(.*?\):', code)
    if consolidated_func:
        print("✅ Found create_consolidated_excel_output function")
        # Find the function body
        func_start = consolidated_func.start()
        lines = code[:func_start].count('\n') + 1
        print(f"   Located at line: {lines}")
    else:
        print("❌ create_consolidated_excel_output function NOT FOUND")
        
        # Check for alternative consolidation functions
        consolidation_patterns = [
            r'def.*consolidat.*\(',
            r'def.*excel.*output.*\(',
            r'def.*create.*output.*\(',
            r'def run_complete_campaign\('
        ]
        
        for pattern in consolidation_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                func_name = match.group()
                lines = code[:match.start()].count('\n') + 1
                print(f"   Alternative found: {func_name} at line {lines}")
    
    print()
    
    # 2. Find create_municipality_summary function
    print("🔍 SEARCHING FOR SUMMARY FUNCTIONS:")
    print("="*50)
    
    summary_func = re.search(r'def create_municipality_summary\(.*?\):', code)
    if summary_func:
        print("✅ Found create_municipality_summary function")
        lines = code[:summary_func.start()].count('\n') + 1
        print(f"   Located at line: {lines}")
    else:
        print("❌ create_municipality_summary function NOT FOUND")
        
        # Check for alternatives
        summary_patterns = [
            r'def.*summary.*\(',
            r'def.*municipality.*\(',
            r'def.*create.*summary.*\('
        ]
        
        for pattern in summary_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                func_name = match.group()
                lines = code[:match.start()].count('\n') + 1
                print(f"   Alternative found: {func_name} at line {lines}")
    
    print()
    
    # 3. Find funnel analysis function
    print("🔍 SEARCHING FOR FUNNEL FUNCTIONS:")
    print("="*50)
    
    funnel_func = re.search(r'def create_funnel_analysis_df\(.*?\):', code)
    if funnel_func:
        print("✅ Found create_funnel_analysis_df function")
        lines = code[:funnel_func.start()].count('\n') + 1
        print(f"   Located at line: {lines}")
    else:
        print("❌ create_funnel_analysis_df function NOT FOUND")
        
        # Check for alternatives
        funnel_patterns = [
            r'def.*funnel.*\(',
            r'def.*analysis.*\(',
            r'def.*create.*funnel.*\('
        ]
        
        for pattern in funnel_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                func_name = match.group()
                lines = code[:match.start()].count('\n') + 1
                print(f"   Alternative found: {func_name} at line {lines}")
    
    print()
    
    # 4. Search for area calculations
    print("🔍 SEARCHING FOR AREA CALCULATIONS:")
    print("="*50)
    
    area_patterns = [
        r'Private_Owner_Area_Ha',
        r'After_CatA_Filter_Area_Ha',
        r'\.sum\(\)',
        r'hectares.*=',
        r'area.*=.*sum',
        r'Area.*=.*\['
    ]
    
    for pattern in area_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE)
        count = len(list(matches))
        if count > 0:
            print(f"✅ Found {count} occurrences of: {pattern}")
            # Show specific lines
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for i, match in enumerate(matches):
                if i < 3:  # Show first 3 matches
                    lines = code[:match.start()].count('\n') + 1
                    print(f"   Line {lines}: {match.group()}")
        else:
            print(f"❌ Pattern not found: {pattern}")
    
    print()
    
    # 5. Search for companies processing
    print("🔍 SEARCHING FOR COMPANIES PROCESSING:")
    print("="*50)
    
    company_patterns = [
        r'Companies_Found',
        r'All_Companies_Found', 
        r'company.*sheet',
        r'Azienda',
        r'pec.*email',
        r'to_excel.*Companies'
    ]
    
    for pattern in company_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE)
        count = len(list(matches))
        if count > 0:
            print(f"✅ Found {count} occurrences of: {pattern}")
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for i, match in enumerate(matches):
                if i < 2:  # Show first 2 matches
                    lines = code[:match.start()].count('\n') + 1
                    print(f"   Line {lines}: {match.group()}")
        else:
            print(f"❌ Pattern not found: {pattern}")
    
    print()
    
    # 6. Search for decimal/comma issues
    print("🔍 SEARCHING FOR DECIMAL/FORMATTING ISSUES:")
    print("="*50)
    
    decimal_patterns = [
        r'\.replace\(',
        r'str\(',
        r'float\(',
        r'locale',
        r'format.*\.',
        r'round\(',
        r',.*\.'
    ]
    
    for pattern in decimal_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE)
        count = len(list(matches))
        if count > 0:
            print(f"✅ Found {count} occurrences of: {pattern}")
        else:
            print(f"❌ Pattern not found: {pattern}")
    
    print()
    print("="*80)
    print("DIAGNOSTIC COMPLETE")
    print("Run this script and share the output to proceed with fixes")
    print("="*80)

if __name__ == "__main__":
    analyze_pipeline_code()