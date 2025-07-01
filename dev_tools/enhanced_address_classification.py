#!/usr/bin/env python3
"""
Enhanced Address Classification System
Improved logic for address confidence scoring with better number matching
"""

import re
import pandas as pd

class EnhancedAddressClassifier:
    """Enhanced address classification with improved number matching"""
    
    def __init__(self):
        # Configuration for number similarity thresholds
        self.config = {
            'exact_match_confidence': 'ULTRA_HIGH',  # New tier for immediate printing
            'close_match_confidence': 'HIGH',        # Similar numbers
            'verified_confidence': 'MEDIUM',         # Original verified but different
            'unverified_confidence': 'LOW'           # No verification possible
        }
    
    def extract_street_number_enhanced(self, address):
        """Enhanced number extraction with better pattern matching"""
        if not isinstance(address, str):
            return None
            
        # Enhanced patterns for Italian addresses
        patterns = [
            r'n\.?\s*(\d+[A-Za-z/]{0,3})',      # "n. 32", "n. 32/A", "n.32BIS"
            r'\b(\d+[A-Za-z/]{0,3})(?:\s|$)',   # "32", "32/A", "32BIS" followed by space or end
            r',\s*(\d+[A-Za-z/]{0,3})',        # ", 32", ", 32/A"
            r'\s(\d+[A-Za-z/]{0,3})(?:\s|$)'    # Space before number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, address, re.IGNORECASE)
            if match:
                return match.group(1).upper().strip()
        return None
    
    def normalize_number(self, number_str):
        """Normalize number for comparison (remove suffixes, handle variations)"""
        if not number_str:
            return None
            
        # Convert to string and uppercase
        num_str = str(number_str).upper().strip()
        
        # Extract just the numeric part
        base_match = re.match(r'(\d+)', num_str)
        if base_match:
            base_number = base_match.group(1)
            
            # Extract suffix if present
            suffix_match = re.search(r'(\d+)([A-Z/]+)', num_str)
            suffix = suffix_match.group(2) if suffix_match else ''
            
            return {
                'full': num_str,
                'base': base_number,
                'suffix': suffix,
                'normalized': base_number  # For comparison
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
        
        # Exact match (including suffixes)
        if orig_norm['full'] == geo_norm['full']:
            return {
                'similarity': 1.0, 
                'match_type': 'exact_match', 
                'confidence': 'ULTRA_HIGH',
                'reason': f"Perfect match: {orig_norm['full']}"
            }
        
        # Base number match (ignoring suffixes)
        if orig_norm['base'] == geo_norm['base']:
            return {
                'similarity': 0.9, 
                'match_type': 'base_match', 
                'confidence': 'HIGH',
                'reason': f"Base number match: {orig_norm['base']} (suffixes differ: {orig_norm['suffix']} vs {geo_norm['suffix']})"
            }
        
        # Close numbers (within range of 2)
        try:
            orig_int = int(orig_norm['base'])
            geo_int = int(geo_norm['base'])
            diff = abs(orig_int - geo_int)
            
            if diff == 1:
                return {
                    'similarity': 0.7, 
                    'match_type': 'adjacent_number', 
                    'confidence': 'MEDIUM',
                    'reason': f"Adjacent numbers: {orig_int} vs {geo_int} (diff: {diff})"
                }
            elif diff == 2:
                return {
                    'similarity': 0.6, 
                    'match_type': 'close_number', 
                    'confidence': 'MEDIUM',
                    'reason': f"Close numbers: {orig_int} vs {geo_int} (diff: {diff})"
                }
            elif diff <= 5:
                return {
                    'similarity': 0.4, 
                    'match_type': 'nearby_number', 
                    'confidence': 'LOW',
                    'reason': f"Nearby numbers: {orig_int} vs {geo_int} (diff: {diff})"
                }
            else:
                return {
                    'similarity': 0.1, 
                    'match_type': 'different_number', 
                    'confidence': 'LOW',
                    'reason': f"Different numbers: {orig_int} vs {geo_int} (diff: {diff})"
                }
                
        except ValueError:
            return {
                'similarity': 0.2, 
                'match_type': 'non_numeric', 
                'confidence': 'LOW',
                'reason': f"Non-numeric comparison: {orig_norm['base']} vs {geo_norm['base']}"
            }
    
    def assess_address_completeness(self, address, geocoding_data):
        """Assess completeness of geocoded address information"""
        if not geocoding_data:
            return {'completeness_score': 0.0, 'missing_fields': ['all_geocoding_data']}
        
        required_fields = ['street_name', 'postal_code', 'city', 'province_name']
        optional_fields = ['latitude', 'longitude', 'country']
        
        missing_required = []
        missing_optional = []
        
        for field in required_fields:
            if not geocoding_data.get(field):
                missing_required.append(field)
        
        for field in optional_fields:
            if not geocoding_data.get(field):
                missing_optional.append(field)
        
        # Calculate completeness score
        required_score = (len(required_fields) - len(missing_required)) / len(required_fields)
        optional_score = (len(optional_fields) - len(missing_optional)) / len(optional_fields)
        
        # Weight required fields more heavily
        completeness_score = (required_score * 0.8) + (optional_score * 0.2)
        
        return {
            'completeness_score': completeness_score,
            'missing_required': missing_required,
            'missing_optional': missing_optional,
            'has_coordinates': bool(geocoding_data.get('latitude') and geocoding_data.get('longitude'))
        }
    
    def classify_address_quality_enhanced(self, row):
        """Enhanced address quality classification"""
        
        original = str(row.get('cleaned_ubicazione', '')).strip()
        geocoded = str(row.get('Geocoded_Address_Italian', '')).strip()
        has_geocoding = row.get('Geocoding_Status') == 'Success'
        
        # Extract numbers using enhanced logic
        original_num = self.extract_street_number_enhanced(original)
        geocoded_num = self.extract_street_number_enhanced(geocoded) if has_geocoding else None
        
        # Handle SNC addresses (no civic number)
        if 'SNC' in original.upper():
            if has_geocoding and self.is_province_match(original, row.get('Province_Code')):
                return {
                    'Address_Confidence': 'MEDIUM',
                    'Interpolation_Risk': False,
                    'Best_Address': original,
                    'Routing_Channel': 'AGENCY',
                    'Quality_Notes': 'SNC address - province match verified',
                    'Confidence_Reasoning': 'SNC addresses require local knowledge for delivery'
                }
            else:
                return {
                    'Address_Confidence': 'LOW',
                    'Interpolation_Risk': True,
                    'Best_Address': original,
                    'Routing_Channel': 'AGENCY',
                    'Quality_Notes': 'SNC address - geocoding failed or province mismatch',
                    'Confidence_Reasoning': 'Unverified SNC address'
                }
        
        # Enhanced number comparison
        if original_num and geocoded_num:
            similarity = self.calculate_number_similarity(original_num, geocoded_num)
            
            # Assess address completeness
            geocoding_data = self.extract_geocoding_data_from_row(row)
            completeness = self.assess_address_completeness(geocoded, geocoding_data)
            
            # Decision logic based on similarity and completeness
            if similarity['match_type'] == 'exact_match' and completeness['completeness_score'] >= 0.8:
                return {
                    'Address_Confidence': 'ULTRA_HIGH',
                    'Interpolation_Risk': False,
                    'Best_Address': geocoded,
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Perfect address verification - {similarity["reason"]}',
                    'Confidence_Reasoning': 'Exact number match + complete geocoding data'
                }
            
            elif similarity['match_type'] in ['exact_match', 'base_match'] and completeness['completeness_score'] >= 0.6:
                return {
                    'Address_Confidence': 'HIGH',
                    'Interpolation_Risk': False,
                    'Best_Address': geocoded,
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Strong address verification - {similarity["reason"]}',
                    'Confidence_Reasoning': 'Strong number match + good geocoding data'
                }
            
            elif similarity['match_type'] in ['adjacent_number', 'close_number']:
                return {
                    'Address_Confidence': 'MEDIUM',
                    'Interpolation_Risk': True,
                    'Best_Address': original,  # Use original for close matches
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Close number match - {similarity["reason"]} - using original',
                    'Confidence_Reasoning': 'Similar numbers suggest correct area, use original for safety'
                }
            
            else:  # Different numbers
                return {
                    'Address_Confidence': 'MEDIUM',
                    'Interpolation_Risk': True,
                    'Best_Address': original,
                    'Routing_Channel': 'DIRECT_MAIL',
                    'Quality_Notes': f'Number mismatch - {similarity["reason"]} - using original',
                    'Confidence_Reasoning': 'Geocoding found different number, trust original'
                }
        
        # Original has number, geocoding failed
        elif original_num and not geocoded_num:
            return {
                'Address_Confidence': 'MEDIUM',
                'Interpolation_Risk': False,
                'Best_Address': original,
                'Routing_Channel': 'DIRECT_MAIL',
                'Quality_Notes': f'Original has number "{original_num}" but geocoding could not verify',
                'Confidence_Reasoning': 'Has street number but no geocoding verification'
            }
        
        # No original number, geocoding suggested one
        elif not original_num and geocoded_num:
            return {
                'Address_Confidence': 'LOW',
                'Interpolation_Risk': True,
                'Best_Address': '',
                'Routing_Channel': 'AGENCY',
                'Quality_Notes': f'No original number, geocoding suggested "{geocoded_num}"',
                'Confidence_Reasoning': 'Geocoding interpolated a number - uncertain accuracy'
            }
        
        # No numbers anywhere
        else:
            return {
                'Address_Confidence': 'LOW',
                'Interpolation_Risk': False,
                'Best_Address': '',
                'Routing_Channel': 'AGENCY',
                'Quality_Notes': 'No street number available in any source',
                'Confidence_Reasoning': 'No numbering information available'
            }
    
    def extract_geocoding_data_from_row(self, row):
        """Extract geocoding data from dataframe row"""
        geocoding_fields = [
            'Street_Name', 'Postal_Code', 'City', 'Province_Name', 
            'Latitude', 'Longitude', 'Country'
        ]
        
        geocoding_data = {}
        for field in geocoding_fields:
            value = row.get(field)
            if pd.notna(value) and value != '':
                # Convert field names to lowercase with underscores
                key = field.lower()
                geocoding_data[key] = value
        
        return geocoding_data
    
    def is_province_match(self, original_address, geocoded_province_code):
        """Check if geocoded province matches original (from existing logic)"""
        if not isinstance(original_address, str) or not isinstance(geocoded_province_code, str):
            return False
        
        match = re.search(r'\(([A-Z]{2})\)', original_address.upper())
        if match:
            original_province_code = match.group(1)
            return original_province_code == geocoded_province_code.upper()
        return False

# Example usage and testing
if __name__ == "__main__":
    classifier = EnhancedAddressClassifier()
    
    # Test cases based on real data
    test_cases = [
        {
            'cleaned_ubicazione': 'SALERANO SUL LAMBRO(LO) VICOLO CREMONA n. 34',
            'Geocoded_Address_Italian': 'Vicolo Cremona, 34, 26857 Salerano sul Lambro LO',
            'Geocoding_Status': 'Success',
            'Street_Name': 'Vicolo Cremona',
            'Postal_Code': '26857',
            'City': 'Salerano sul Lambro',
            'Province_Name': 'Lodi',
            'Province_Code': 'LO'
        }
    ]
    
    print("🧪 Testing Enhanced Address Classification")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Original: {test_case['cleaned_ubicazione']}")
        print(f"Geocoded: {test_case['Geocoded_Address_Italian']}")
        
        result = classifier.classify_address_quality_enhanced(test_case)
        
        print(f"Result:")
        for key, value in result.items():
            print(f"  {key}: {value}")