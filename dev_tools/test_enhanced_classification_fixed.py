#!/usr/bin/env python3
"""
Test Enhanced Address Classification
Compare current vs enhanced classification on real campaign data
"""

import pandas as pd
import sys
import os

# Add parent directory to path to import from main pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from enhanced_address_classification import EnhancedAddressClassifier
except ImportError:
    print("Could not import EnhancedAddressClassifier. Running inline version...")
    
    import re
    
    class EnhancedAddressClassifier:
        """Enhanced address classification with improved number matching"""
        
        def __init__(self):
            self.config = {
                'exact_match_confidence': 'ULTRA_HIGH',
                'close_match_confidence': 'HIGH',
                'verified_confidence': 'MEDIUM',
                'unverified_confidence': 'LOW'
            }
        
        def extract_street_number_enhanced(self, address):
            """Enhanced number extraction with better pattern matching"""
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
                    'suffix': suffix,
                    'normalized': base_number
                }
            return None
        
        def calculate_number_similarity(self, original_num, geocoded_num):
            """Calculate similarity between original and geocoded numbers"""
            if not original_num or not geocoded_num:
                return {'similarity': 0.0, 'match_type': 'no_match', 'confidence': 'LOW'}
            
            orig_norm = self.normalize_number(original_num)
            geo_norm = self.normalize_number(geocoded_num)
            
            if not orig_norm or not geo_norm:
                return {'similarity': 0.0, 'match_type': 'no_match', 'confidence': 'LOW'}
            
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
                    'reason': f"Base number match: {orig_norm['base']}"
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
        
        def assess_address_completeness(self, geocoding_data):
            """Assess completeness of geocoded address information"""
            if not geocoding_data:
                return {'completeness_score': 0.0, 'missing_fields': ['all_geocoding_data']}
            
            required_fields = ['Street_Name', 'Postal_Code', 'City', 'Province_Name']
            present_required = sum(1 for field in required_fields if geocoding_data.get(field))
            
            completeness_score = present_required / len(required_fields)
            
            return {
                'completeness_score': completeness_score,
                'present_fields': present_required,
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
                        'Interpolation_Risk': False,
                        'Best_Address': original,
                        'Routing_Channel': 'AGENCY',
                        'Quality_Notes': 'SNC address - province match verified',
                        'Confidence_Reasoning': 'SNC addresses require local knowledge'
                    }
                else:
                    return {
                        'Address_Confidence': 'LOW',
                        'Interpolation_Risk': True,
                        'Best_Address': original,
                        'Routing_Channel': 'AGENCY',
                        'Quality_Notes': 'SNC address - geocoding failed',
                        'Confidence_Reasoning': 'Unverified SNC address'
                    }
            
            # Enhanced number comparison
            if original_num and geocoded_num:
                similarity = self.calculate_number_similarity(original_num, geocoded_num)
                
                # Create geocoding data dict from row
                geocoding_data = {
                    'Street_Name': row.get('Street_Name'),
                    'Postal_Code': row.get('Postal_Code'),
                    'City': row.get('City'),
                    'Province_Name': row.get('Province_Name')
                }
                
                completeness = self.assess_address_completeness(geocoding_data)
                
                if similarity['match_type'] == 'exact_match' and completeness['completeness_score'] >= 0.8:
                    return {
                        'Address_Confidence': 'ULTRA_HIGH',
                        'Interpolation_Risk': False,
                        'Best_Address': geocoded,
                        'Routing_Channel': 'DIRECT_MAIL',
                        'Quality_Notes': f'Perfect verification - {similarity["reason"]}',
                        'Confidence_Reasoning': 'Exact match + complete data'
                    }
                
                elif similarity['match_type'] in ['exact_match', 'base_match'] and completeness['completeness_score'] >= 0.6:
                    return {
                        'Address_Confidence': 'HIGH',
                        'Interpolation_Risk': False,
                        'Best_Address': geocoded,
                        'Routing_Channel': 'DIRECT_MAIL',
                        'Quality_Notes': f'Strong verification - {similarity["reason"]}',
                        'Confidence_Reasoning': 'Strong match + good data'
                    }
                
                elif similarity['match_type'] in ['adjacent_number', 'close_number']:
                    return {
                        'Address_Confidence': 'MEDIUM',
                        'Interpolation_Risk': True,
                        'Best_Address': original,
                        'Routing_Channel': 'DIRECT_MAIL',
                        'Quality_Notes': f'Close match - {similarity["reason"]} - using original',
                        'Confidence_Reasoning': 'Similar numbers, use original for safety'
                    }
                
                else:
                    return {
                        'Address_Confidence': 'MEDIUM',
                        'Interpolation_Risk': True,
                        'Best_Address': original,
                        'Routing_Channel': 'DIRECT_MAIL',
                        'Quality_Notes': f'Number mismatch - using original',
                        'Confidence_Reasoning': 'Different numbers, trust original'
                    }
            
            elif original_num and not geocoded_num:
                return {
                    'Address_Confidence': 'MEDIUM',
                    'Interpolation_Risk': False,
                    'Best_Address': original,
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Original has number but unverified',
                    'Confidence_Reasoning': 'Has number but no verification'
                }
            
            elif not original_num and geocoded_num:
                return {
                    'Address_Confidence': 'LOW',
                    'Interpolation_Risk': True,
                    'Best_Address': '',
                    'Routing_Channel': 'AGENCY',
                    'Quality_Notes': f'No original number, geocoding suggested one',
                    'Confidence_Reasoning': 'Geocoding interpolated number'
                }
            
            else:
                return {
                    'Address_Confidence': 'LOW',
                    'Interpolation_Risk': False,
                    'Best_Address': '',
                    'Routing_Channel': 'AGENCY',
                    'Quality_Notes': 'No street number available',
                    'Confidence_Reasoning': 'No numbering information'
                }

def test_enhanced_classification_on_real_data():
    """Test enhanced classification on real campaign data"""
    
    results_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2018\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2018_Results.xlsx"
    
    print("TESTING ENHANCED ADDRESS CLASSIFICATION")
    print("=" * 60)
    print()
    
    try:
        df = pd.read_excel(results_file, sheet_name='All_Validation_Ready')
        print(f"Loaded {len(df)} addresses from real campaign data")
        print()
        
        classifier = EnhancedAddressClassifier()
        comparison_results = []
        
        print("ANALYZING EACH ADDRESS:")
        print("-" * 40)
        
        for idx, row in df.iterrows():
            current_confidence = row.get('Address_Confidence', 'UNKNOWN')
            current_routing = row.get('Routing_Channel', 'UNKNOWN')
            
            enhanced_result = classifier.classify_address_quality_enhanced(row)
            enhanced_confidence = enhanced_result['Address_Confidence']
            enhanced_routing = enhanced_result['Routing_Channel']
            
            comparison_results.append({
                'index': idx + 1,
                'original_address': row.get('cleaned_ubicazione', ''),
                'geocoded_address': row.get('Geocoded_Address_Italian', ''),
                'current_confidence': current_confidence,
                'current_routing': current_routing,
                'enhanced_confidence': enhanced_confidence,
                'enhanced_routing': enhanced_routing,
                'confidence_reasoning': enhanced_result.get('Confidence_Reasoning', ''),
                'quality_notes': enhanced_result.get('Quality_Notes', ''),
                'improvement': enhanced_confidence != current_confidence
            })
            
            if idx < 5:
                print(f"\nAddress {idx + 1}:")
                print(f"  Original: {row.get('cleaned_ubicazione', '')[:60]}...")
                print(f"  Geocoded: {row.get('Geocoded_Address_Italian', '')[:60]}...")
                print(f"  Current:  {current_confidence} -> {current_routing}")
                print(f"  Enhanced: {enhanced_confidence} -> {enhanced_routing}")
                print(f"  Reasoning: {enhanced_result.get('Confidence_Reasoning', '')}")
                if enhanced_confidence != current_confidence:
                    print(f"  IMPROVEMENT: {current_confidence} -> {enhanced_confidence}")
        
        print("\n" + "=" * 60)
        print("CLASSIFICATION COMPARISON SUMMARY")
        print("=" * 60)
        
        current_dist = pd.Series([r['current_confidence'] for r in comparison_results]).value_counts()
        enhanced_dist = pd.Series([r['enhanced_confidence'] for r in comparison_results]).value_counts()
        
        print("\nCONFIDENCE DISTRIBUTION COMPARISON:")
        print(f"{'Level':<15} {'Current':<10} {'Enhanced':<10} {'Change':<10}")
        print("-" * 45)
        
        all_levels = set(current_dist.index) | set(enhanced_dist.index)
        for level in sorted(all_levels):
            current_count = current_dist.get(level, 0)
            enhanced_count = enhanced_dist.get(level, 0)
            change = enhanced_count - current_count
            change_str = f"+{change}" if change > 0 else str(change)
            print(f"{level:<15} {current_count:<10} {enhanced_count:<10} {change_str:<10}")
        
        improvements = [r for r in comparison_results if r['improvement']]
        print(f"\nIMPROVEMENTS DETECTED:")
        print(f"Addresses with improved confidence: {len(improvements)}/{len(comparison_results)} ({len(improvements)/len(comparison_results)*100:.1f}%)")
        
        if improvements:
            print("\nImprovement breakdown:")
            improvement_types = {}
            for imp in improvements:
                change = f"{imp['current_confidence']} -> {imp['enhanced_confidence']}"
                improvement_types[change] = improvement_types.get(change, 0) + 1
            
            for change, count in improvement_types.items():
                print(f"  {change}: {count} addresses")
        
        print(f"\nPOTENTIAL TIME SAVINGS:")
        
        ultra_high_count = enhanced_dist.get('ULTRA_HIGH', 0)
        high_count = enhanced_dist.get('HIGH', 0)
        
        current_review_time = len(df) * 8
        enhanced_review_time = (ultra_high_count * 0) + (high_count * 5) + ((len(df) - ultra_high_count - high_count) * 8)
        time_saved = current_review_time - enhanced_review_time
        
        print(f"Current review time: {current_review_time} minutes ({current_review_time/60:.1f} hours)")
        print(f"Enhanced review time: {enhanced_review_time} minutes ({enhanced_review_time/60:.1f} hours)")
        print(f"Time savings: {time_saved} minutes ({time_saved/60:.1f} hours, {time_saved/current_review_time*100:.1f}% reduction)")
        
        if ultra_high_count > 0:
            print(f"\nIMMEDIATE PRINT-READY ADDRESSES:")
            print(f"{ultra_high_count} addresses ({ultra_high_count/len(df)*100:.1f}%) can go directly to printing")
            
            ultra_high_addresses = [r for r in comparison_results if r['enhanced_confidence'] == 'ULTRA_HIGH']
            print("Sample ULTRA_HIGH addresses:")
            for i, addr in enumerate(ultra_high_addresses[:3]):
                print(f"  {i+1}. {addr['original_address'][:50]}...")
                print(f"     -> {addr['geocoded_address'][:50]}...")
                print(f"     Reason: {addr['confidence_reasoning']}")
        
        return comparison_results
        
    except FileNotFoundError:
        print(f"Campaign results file not found: {results_file}")
        return None
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        return None

if __name__ == "__main__":
    print("ENHANCED ADDRESS CLASSIFICATION TESTING")
    print("Testing enhanced classification against real campaign data...")
    print()
    
    results = test_enhanced_classification_on_real_data()
    
    print("\nTesting complete!")
    print("Next steps:")
    print("1. Review the classification improvements")
    print("2. Validate ULTRA_HIGH addresses manually")
    print("3. Consider implementing the enhancement")