"""
Test Enhanced Address Classification - FIXED VERSION
Fixed the number extraction bug that was picking up postal codes
"""

import pandas as pd
import re

class EnhancedAddressClassifierFixed:
    """Enhanced address classification with FIXED number matching"""
    
    def extract_street_number_enhanced(self, address):
        """FIXED: Enhanced number extraction that avoids postal codes"""
        if not isinstance(address, str):
            return None
            
        # For Italian geocoded addresses in format: "Street Name, Number, PostalCode City Province"
        # We need to extract the number that comes AFTER the first comma but BEFORE the postal code
        
        # Try geocoded format first: "Street Name, Number, PostalCode..."
        geocoded_pattern = r',\s*(\d+[A-Za-z/]{0,3})\s*,'
        match = re.search(geocoded_pattern, address)
        if match:
            return match.group(1).upper().strip()
        
        # Original patterns for raw addresses
        patterns = [
            r'n\.?\s*(\d+[A-Za-z/]{0,3})(?!\d)',  # "n. 34" - avoid longer numbers
            r'\b(\d+[A-Za-z/]{0,3})(?:\s+[A-Z]|\s*$)',  # Number followed by letters or end
            r'^.*?(\d+[A-Za-z/]{0,3})(?:\s+\w+)*\s*$'   # Last resort
        ]
        
        for pattern in patterns:
            match = re.search(pattern, address, re.IGNORECASE)
            if match:
                number = match.group(1).upper().strip()
                # Avoid postal codes (usually 5 digits)
                if len(re.sub(r'[A-Z/]', '', number)) < 5:
                    return number
        
        return None
    
    def normalize_number(self, number_str):
        """Normalize number for comparison"""
        if not number_str:
            return None
            
        num_str = str(number_str).upper().strip()
        base_match = re.match(r'(\d+)', num_str)
        if base_match:
            base_number = base_match.group(1)
            suffix_match = re.search(r'(\d+)([A-Z/]+)', num_str)
            suffix = suffix_match.group(2) if suffix_match else ''
            
            return {
                'full': num_str,
                'base': base_number,
                'suffix': suffix
            }
        return None
    
    def calculate_number_similarity(self, original_num, geocoded_num):
        """Calculate similarity between original and geocoded numbers"""
        if not original_num or not geocoded_num:
            return {'similarity': 0.0, 'match_type': 'no_match', 'confidence': 'LOW', 'reason': 'Missing numbers'}
        
        orig_norm = self.normalize_number(original_num)
        geo_norm = self.normalize_number(geocoded_num)
        
        if not orig_norm or not geo_norm:
            return {'similarity': 0.0, 'match_type': 'no_match', 'confidence': 'LOW', 'reason': 'Invalid numbers'}
        
        if orig_norm['full'] == geo_norm['full']:
            return {
                'similarity': 1.0, 
                'match_type': 'exact_match', 
                'confidence': 'ULTRA_HIGH',
                'reason': f"Perfect match: {orig_norm['full']}"
            }
        
        if orig_norm['base'] == geo_norm['base']:
            return {
                'similarity': 0.9, 
                'match_type': 'base_match', 
                'confidence': 'HIGH',
                'reason': f"Base number match: {orig_norm['base']} (suffixes: '{orig_norm['suffix']}' vs '{geo_norm['suffix']}')"
            }
        
        try:
            orig_int = int(orig_norm['base'])
            geo_int = int(geo_norm['base'])
            diff = abs(orig_int - geo_int)
            
            if diff == 1:
                return {
                    'similarity': 0.7, 
                    'match_type': 'adjacent_number', 
                    'confidence': 'MEDIUM',
                    'reason': f"Adjacent numbers: {orig_int} vs {geo_int}"
                }
            elif diff == 2:
                return {
                    'similarity': 0.6, 
                    'match_type': 'close_number', 
                    'confidence': 'MEDIUM',
                    'reason': f"Close numbers: {orig_int} vs {geo_int}"
                }
            else:
                return {
                    'similarity': 0.1, 
                    'match_type': 'different_number', 
                    'confidence': 'LOW',
                    'reason': f"Different numbers: {orig_int} vs {geo_int}"
                }
                
        except ValueError:
            return {
                'similarity': 0.2, 
                'match_type': 'non_numeric', 
                'confidence': 'LOW',
                'reason': f"Non-numeric comparison"
            }
    
    def assess_address_completeness(self, row):
        """Assess completeness of geocoded address information"""
        required_fields = ['Street_Name', 'Postal_Code', 'City', 'Province_Name']
        present_count = 0
        
        for field in required_fields:
            value = row.get(field)
            if pd.notna(value) and str(value).strip() != '':
                present_count += 1
        
        completeness_score = present_count / len(required_fields)
        
        return {
            'completeness_score': completeness_score,
            'present_fields': present_count,
            'total_required': len(required_fields)
        }
    
    def is_province_match(self, original_address, geocoded_province_code):
        """Check if geocoded province matches original"""
        if not isinstance(original_address, str) or not isinstance(geocoded_province_code, str):
            return False
        
        match = re.search(r'\(([A-Z]{2})\)', original_address.upper())
        if match:
            original_province_code = match.group(1)
            return original_province_code == geocoded_province_code.upper()
        return False
    
    def classify_address_quality_enhanced(self, row):
        """Enhanced address quality classification"""
        
        original = str(row.get('cleaned_ubicazione', '')).strip()
        geocoded = str(row.get('Geocoded_Address_Italian', '')).strip()
        has_geocoding = row.get('Geocoding_Status') == 'Success'
        
        original_num = self.extract_street_number_enhanced(original)
        geocoded_num = self.extract_street_number_enhanced(geocoded) if has_geocoding else None
        
        # Handle SNC addresses
        if 'SNC' in original.upper():
            if has_geocoding and self.is_province_match(original, row.get('Province_Code')):
                return {
                    'Address_Confidence': 'MEDIUM',
                    'Routing_Channel': 'AGENCY',
                    'Quality_Notes': 'SNC address - province verified',
                    'Confidence_Reasoning': 'SNC addresses require local knowledge'
                }
            else:
                return {
                    'Address_Confidence': 'LOW',
                    'Routing_Channel': 'AGENCY',
                    'Quality_Notes': 'SNC address - unverified',
                    'Confidence_Reasoning': 'Unverified SNC address'
                }
        
        # Enhanced number comparison
        if original_num and geocoded_num:
            similarity = self.calculate_number_similarity(original_num, geocoded_num)
            completeness = self.assess_address_completeness(row)
            
            if similarity['match_type'] == 'exact_match' and completeness['completeness_score'] >= 0.75:
                return {
                    'Address_Confidence': 'ULTRA_HIGH',
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Perfect verification - {similarity["reason"]}',
                    'Confidence_Reasoning': 'Exact match + complete data',
                    'Number_Comparison': f"Original: '{original_num}' vs Geocoded: '{geocoded_num}'"
                }
            
            elif similarity['match_type'] in ['exact_match', 'base_match'] and completeness['completeness_score'] >= 0.5:
                return {
                    'Address_Confidence': 'HIGH',
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Strong verification - {similarity["reason"]}',
                    'Confidence_Reasoning': 'Strong match + good data',
                    'Number_Comparison': f"Original: '{original_num}' vs Geocoded: '{geocoded_num}'"
                }
            
            elif similarity['match_type'] in ['adjacent_number', 'close_number']:
                return {
                    'Address_Confidence': 'MEDIUM',
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Close match - using original',
                    'Confidence_Reasoning': 'Similar numbers, use original for safety',
                    'Number_Comparison': f"Original: '{original_num}' vs Geocoded: '{geocoded_num}'"
                }
            
            else:
                return {
                    'Address_Confidence': 'MEDIUM',
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Number mismatch - using original',
                    'Confidence_Reasoning': 'Different numbers, trust original',
                    'Number_Comparison': f"Original: '{original_num}' vs Geocoded: '{geocoded_num}'"
                }
        
        elif original_num and not geocoded_num:
            return {
                'Address_Confidence': 'MEDIUM',
                'Routing_Channel': 'DIRECT_MAIL',
                'Quality_Notes': f'Original has number but unverified',
                'Confidence_Reasoning': 'Has number but no verification'
            }
        
        elif not original_num and geocoded_num:
            return {
                'Address_Confidence': 'LOW',
                'Routing_Channel': 'AGENCY',
                'Quality_Notes': f'No original number',
                'Confidence_Reasoning': 'Geocoding interpolated number'
            }
        
        else:
            return {
                'Address_Confidence': 'LOW',
                'Routing_Channel': 'AGENCY',
                'Quality_Notes': 'No street number available',
                'Confidence_Reasoning': 'No numbering information'
            }

def test_number_extraction_fix():
    """Test the fixed number extraction on the problematic addresses"""
    
    print("TESTING FIXED NUMBER EXTRACTION")
    print("=" * 50)
    
    classifier = EnhancedAddressClassifierFixed()
    
    test_cases = [
        {
            'description': 'Vicolo Cremona case',
            'original': 'SALERANO SUL LAMBRO(LO) VICOLO CREMONA n. 34',
            'geocoded': 'Vicolo Cremona, 34, 26857 Salerano sul Lambro LO'
        },
        {
            'description': 'Cascina Villafranca case',
            'original': 'OSPEDALETTO LODIGIANO(LO) CASCINA VILLAFRANCA DI MEZZO n. 1',
            'geocoded': 'Cascina Villafranca di Mezzo, 1, 26864 Ospedaletto Lodigiano LO'
        }
    ]
    
    for case in test_cases:
        print(f"\n{case['description']}:")
        print(f"  Original: {case['original']}")
        print(f"  Geocoded: {case['geocoded']}")
        
        orig_num = classifier.extract_street_number_enhanced(case['original'])
        geo_num = classifier.extract_street_number_enhanced(case['geocoded'])
        
        print(f"  Original Number: '{orig_num}'")
        print(f"  Geocoded Number: '{geo_num}'")
        print(f"  Match: {orig_num == geo_num}")
        
        if orig_num and geo_num:
            similarity = classifier.calculate_number_similarity(orig_num, geo_num)
            print(f"  Similarity: {similarity['match_type']} -> {similarity['confidence']}")
            print(f"  Reason: {similarity['reason']}")

def test_enhanced_classification_fixed():
    """Test fixed enhanced classification on real campaign data"""
    
    results_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2018\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2018_Results.xlsx"
    
    print("\n\nTESTING FIXED ENHANCED CLASSIFICATION")
    print("=" * 60)
    
    try:
        df = pd.read_excel(results_file, sheet_name='All_Validation_Ready')
        print(f"Loaded {len(df)} addresses from real campaign data")
        
        classifier = EnhancedAddressClassifierFixed()
        comparison_results = []
        
        print("\nANALYZING HIGH CONFIDENCE ADDRESSES:")
        print("-" * 50)
        
        # Focus on the originally HIGH confidence addresses
        high_confidence_addresses = df[df['Address_Confidence'] == 'HIGH']
        
        for idx, row in high_confidence_addresses.iterrows():
            current_confidence = row.get('Address_Confidence', 'UNKNOWN')
            enhanced_result = classifier.classify_address_quality_enhanced(row)
            enhanced_confidence = enhanced_result['Address_Confidence']
            
            print(f"\nAddress {idx + 1} (was HIGH):")
            print(f"  Original: {row.get('cleaned_ubicazione', '')}")
            print(f"  Geocoded: {row.get('Geocoded_Address_Italian', '')}")
            print(f"  Current:  {current_confidence}")
            print(f"  Enhanced: {enhanced_confidence}")
            print(f"  Reason: {enhanced_result.get('Confidence_Reasoning', '')}")
            if 'Number_Comparison' in enhanced_result:
                print(f"  Numbers: {enhanced_result['Number_Comparison']}")
            
            if enhanced_confidence in ['ULTRA_HIGH', 'HIGH']:
                print(f"  *** SUCCESS: Maintained or improved! ***")
            else:
                print(f"  WARNING: Downgraded from HIGH to {enhanced_confidence}")
        
        # Now test all addresses
        print(f"\n\nFULL CLASSIFICATION ANALYSIS:")
        print("-" * 50)
        
        for idx, row in df.iterrows():
            current_confidence = row.get('Address_Confidence', 'UNKNOWN')
            enhanced_result = classifier.classify_address_quality_enhanced(row)
            enhanced_confidence = enhanced_result['Address_Confidence']
            
            comparison_results.append({
                'index': idx + 1,
                'current_confidence': current_confidence,
                'enhanced_confidence': enhanced_confidence,
                'improvement': enhanced_confidence != current_confidence
            })
        
        # Summary
        current_dist = pd.Series([r['current_confidence'] for r in comparison_results]).value_counts()
        enhanced_dist = pd.Series([r['enhanced_confidence'] for r in comparison_results]).value_counts()
        
        print(f"\nCONFIDENCE DISTRIBUTION:")
        print(f"{'Level':<15} {'Current':<10} {'Enhanced':<10} {'Change'}")
        print("-" * 50)
        
        all_levels = ['ULTRA_HIGH', 'HIGH', 'MEDIUM', 'LOW']
        for level in all_levels:
            current_count = current_dist.get(level, 0)
            enhanced_count = enhanced_dist.get(level, 0)
            change = enhanced_count - current_count
            change_str = f"+{change}" if change > 0 else str(change) if change < 0 else "0"
            print(f"{level:<15} {current_count:<10} {enhanced_count:<10} {change_str}")
        
        ultra_high_count = enhanced_dist.get('ULTRA_HIGH', 0)
        high_count = enhanced_dist.get('HIGH', 0)
        
        print(f"\nTIME SAVINGS ANALYSIS:")
        current_review_time = len(df) * 8
        enhanced_review_time = (ultra_high_count * 0) + (high_count * 5) + ((len(df) - ultra_high_count - high_count) * 8)
        time_saved = current_review_time - enhanced_review_time
        
        print(f"Current review time: {current_review_time} minutes ({current_review_time/60:.1f} hours)")
        print(f"Enhanced review time: {enhanced_review_time} minutes ({enhanced_review_time/60:.1f} hours)")
        print(f"Time savings: {time_saved} minutes ({time_saved/60:.1f} hours)")
        print(f"Efficiency gain: {time_saved/current_review_time*100:.1f}%")
        
        if ultra_high_count > 0:
            print(f"\nIMMEDIATE PRINT-READY:")
            print(f"{ultra_high_count} addresses ({ultra_high_count/len(df)*100:.1f}%) ready for immediate printing")
        
        return comparison_results
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Run the tests
test_number_extraction_fix()
results = test_enhanced_classification_fixed()
print("\nFixed testing completed!")