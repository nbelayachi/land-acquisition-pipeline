#!/usr/bin/env python3
"""
Examine specific issues in the pipeline code
Run this to see the exact problematic code sections
"""

import re

def examine_pipeline_issues():
    """Examine the specific issues found in the pipeline"""
    
    print("="*80)
    print("EXAMINING SPECIFIC PIPELINE ISSUES")
    print("="*80)
    
    with open("land_acquisition_pipeline.py", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Issue 1: Check create_consolidated_excel_output function (line ~1435)
    print("🔍 ISSUE 1: EXAMINING create_consolidated_excel_output (Line ~1435)")
    print("="*70)
    
    start_line = 1430
    end_line = 1480
    
    for i in range(start_line, min(end_line, len(lines))):
        line_num = i + 1
        line = lines[i].rstrip()
        if 'def create_consolidated_excel_output' in line:
            print(f">>> FUNCTION START: Line {line_num}")
        print(f"{line_num:4d}: {line}")
        
        # Look for All_Companies_Found references
        if 'All_Companies_Found' in line or 'all_companies_found' in line:
            print(f"     ^^^ COMPANIES SHEET REFERENCE FOUND")
    
    print("\n" + "="*70)
    print("🔍 ISSUE 2: EXAMINING create_municipality_summary (Line ~819)")
    print("="*70)
    
    start_line = 815
    end_line = 900
    
    for i in range(start_line, min(end_line, len(lines))):
        line_num = i + 1
        line = lines[i].rstrip()
        if 'def create_municipality_summary' in line:
            print(f">>> FUNCTION START: Line {line_num}")
        print(f"{line_num:4d}: {line}")
        
        # Look for CP, comune, provincia references
        if any(x in line.lower() for x in ['cp', 'comune', 'provincia']):
            print(f"     ^^^ TRACEABILITY REFERENCE FOUND")
        
        # Look for Private_Owner_Area_Ha calculations
        if 'Private_Owner_Area_Ha' in line or 'private_owner_area_ha' in line:
            print(f"     ^^^ AREA CALCULATION FOUND")
    
    print("\n" + "="*70)
    print("🔍 ISSUE 3: EXAMINING DECIMAL FORMATTING in Area Calculations")
    print("="*70)
    
    # Look at specific area calculation lines
    decimal_lines = [826, 862, 863, 893, 897, 1294, 1380, 1381]
    
    for line_num in decimal_lines:
        if line_num <= len(lines):
            line = lines[line_num - 1].rstrip()
            print(f"{line_num:4d}: {line}")
            
            # Check for comma/decimal issues
            if ".replace(','," in line or "str.replace" in line:
                print(f"     ^^^ DECIMAL FORMATTING FOUND")
            if ".sum()" in line:
                print(f"     ^^^ AREA SUMMATION FOUND")
    
    print("\n" + "="*70)
    print("🔍 ISSUE 4: EXAMINING create_funnel_analysis_df (Line ~1421)")
    print("="*70)
    
    start_line = 1418
    end_line = 1440
    
    for i in range(start_line, min(end_line, len(lines))):
        line_num = i + 1
        line = lines[i].rstrip()
        if 'def create_funnel_analysis_df' in line:
            print(f">>> FUNCTION START: Line {line_num}")
        print(f"{line_num:4d}: {line}")
        
        # Look for provincia references
        if 'provincia' in line.lower():
            print(f"     ^^^ PROVINCIA REFERENCE FOUND")
    
    print("\n" + "="*70)
    print("🔍 ISSUE 5: LOOKING FOR Unique_Owner_Address_Pairs CALCULATION")
    print("="*70)
    
    # Search for this specific metric
    for i, line in enumerate(lines):
        line_num = i + 1
        if 'Unique_Owner_Address_Pairs' in line:
            print(f"{line_num:4d}: {line.rstrip()}")
            # Show context (2 lines before and after)
            for j in range(max(0, i-2), min(len(lines), i+3)):
                if j != i:
                    context_line = j + 1
                    print(f"{context_line:4d}: {lines[j].rstrip()}")
            print("     ^^^ CONTEXT FOR UNIQUE_OWNER_ADDRESS_PAIRS")
            break
    
    print("\n" + "="*80)
    print("EXAMINATION COMPLETE")
    print("Next: Run the fix scripts based on these findings")
    print("="*80)

if __name__ == "__main__":
    examine_pipeline_issues()