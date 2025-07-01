"""
Diagnose HIGH Confidence Address Classification
Examine why the 4 originally HIGH confidence addresses were reclassified
"""

import pandas as pd
import re

def diagnose_high_confidence_addresses():
    """Examine the 4 originally HIGH confidence addresses in detail"""
    
    results_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2018\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2018_Results.xlsx"
    
    print("DIAGNOSING HIGH CONFIDENCE ADDRESS CLASSIFICATION")
    print("=" * 60)
    
    try:
        df = pd.read_excel(results_file, sheet_name='All_Validation_Ready')
        
        # Find the originally HIGH confidence addresses
        high_confidence_addresses = df[df['Address_Confidence'] == 'HIGH'].copy()
        
        print(f"Found {len(high_confidence_addresses)} originally HIGH confidence addresses")
        print()
        
        for idx, row in high_confidence_addresses.iterrows():
            print(f"HIGH CONFIDENCE ADDRESS {idx + 1}:")
            print(f"  Original: {row.get('cleaned_ubicazione', '')}")
            print(f"  Geocoded: {row.get('Geocoded_Address_Italian', '')}")
            print(f"  Street Name: {row.get('Street_Name', '')}")
            print(f"  Street Number: {row.get('Street_Number', '')}")
            print(f"  Postal Code: {row.get('Postal_Code', '')}")
            print(f"  City: {row.get('City', '')}")
            print(f"  Province: {row.get('Province_Name', '')}")
            print(f"  Geocoding Status: {row.get('Geocoding_Status', '')}")
            
            # Extract numbers manually to see what's happening
            original_num = extract_number(row.get('cleaned_ubicazione', ''))
            geocoded_num = extract_number(row.get('Geocoded_Address_Italian', ''))
            
            print(f"  Original Number Extracted: '{original_num}'")
            print(f"  Geocoded Number Extracted: '{geocoded_num}'")
            print(f"  Numbers Match: {original_num == geocoded_num if original_num and geocoded_num else 'N/A'}")
            
            # Check completeness
            completeness = check_completeness(row)
            print(f"  Data Completeness: {completeness['score']:.1%} ({completeness['present']}/{completeness['total']} fields)")
            print(f"  Missing Fields: {completeness['missing']}")
            
            # Determine why it might not qualify for ULTRA_HIGH
            if original_num and geocoded_num and original_num == geocoded_num:
                if completeness['score'] >= 0.8:
                    print("  *** SHOULD BE ULTRA_HIGH: Exact match + complete data ***")
                elif completeness['score'] >= 0.6:
                    print("  *** SHOULD BE HIGH: Exact match + good data ***")
                else:
                    print(f"  MEDIUM: Exact match but incomplete data ({completeness['score']:.1%})")
            else:
                print(f"  MEDIUM: Number mismatch or missing numbers")
            
            print("-" * 60)
        
        return high_confidence_addresses
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def extract_number(address):
    """Extract street number from address"""
    if not isinstance(address, str):
        return None
        
    patterns = [
        r'n\.?\s*(\d+[A-Za-z/]{0,3})',
        r'\b(\d+[A-Za-z/]{0,3})(?:\s|$)',
        r',\s*(\d+[A-Za-z/]{0,3})',
        r'\s(\d+[A-Za-z/]{0,3})(?:\s|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, address, re.IGNORECASE)
        if match:
            return match.group(1).upper().strip()
    return None

def check_completeness(row):
    """Check data completeness"""
    required_fields = ['Street_Name', 'Postal_Code', 'City', 'Province_Name']
    present = []
    missing = []
    
    for field in required_fields:
        value = row.get(field)
        if pd.notna(value) and str(value).strip() != '':
            present.append(field)
        else:
            missing.append(field)
    
    return {
        'score': len(present) / len(required_fields),
        'present': len(present),
        'total': len(required_fields),
        'missing': missing
    }

# Run diagnosis
high_addresses = diagnose_high_confidence_addresses()
print("Diagnosis complete!")