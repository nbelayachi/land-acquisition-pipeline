"""
Test Enhanced Classification Integration
Validate that the enhanced classification is properly integrated into the main pipeline
"""

import pandas as pd
import json
import sys
import os

def test_enhanced_integration():
    """Test the enhanced classification integration"""
    
    print("TESTING ENHANCED CLASSIFICATION INTEGRATION")
    print("=" * 60)
    
    # Test configuration loading
    try:
        with open('config_enhanced.json', 'r') as f:
            config = json.load(f)
        
        enhanced_config = config.get('enhanced_classification', {})
        print(f"Enhanced classification enabled: {enhanced_config.get('enabled', False)}")
        print(f"ULTRA_HIGH threshold: {enhanced_config.get('ultra_high_completeness_threshold', 0.75)}")
        print(f"HIGH threshold: {enhanced_config.get('high_completeness_threshold', 0.5)}")
        print()
        
    except FileNotFoundError:
        print("ERROR: config_enhanced.json not found")
        return False
    
    # Test import of main pipeline
    try:
        sys.path.append('.')
        from land_acquisition_pipeline import IntegratedLandAcquisitionPipeline
        print("✅ Successfully imported IntegratedLandAcquisitionPipeline")
    except ImportError as e:
        print(f"❌ Failed to import pipeline: {e}")
        return False
    
    # Test pipeline initialization with enhanced config
    try:
        pipeline = IntegratedLandAcquisitionPipeline('config_enhanced.json')
        print("✅ Successfully initialized pipeline with enhanced config")
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")
        return False
    
    # Test enhanced classification methods exist
    required_methods = [
        'extract_street_number_enhanced',
        'normalize_number_for_comparison', 
        'calculate_number_similarity',
        'assess_address_completeness',
        'classify_address_quality_enhanced'
    ]
    
    for method in required_methods:
        if hasattr(pipeline, method):
            print(f"✅ Method {method} exists")
        else:
            print(f"❌ Method {method} missing")
            return False
    
    # Test classification on sample data
    print("\nTesting classification on sample data:")
    sample_row = {
        'cleaned_ubicazione': 'SALERANO SUL LAMBRO(LO) VICOLO CREMONA n. 34',
        'Geocoded_Address_Italian': 'Vicolo Cremona, 34, 26857 Salerano sul Lambro LO',
        'Geocoding_Status': 'Success',
        'Street_Name': 'Vicolo Cremona',
        'Postal_Code': '26857',
        'City': 'Salerano sul Lambro',
        'Province_Name': 'Lodi',
        'Province_Code': 'LO'
    }
    
    try:
        # Test enhanced classification
        result = pipeline.classify_address_quality(sample_row)
        print(f"Sample classification result:")
        print(f"  Confidence: {result.get('Address_Confidence', 'UNKNOWN')}")
        print(f"  Routing: {result.get('Routing_Channel', 'UNKNOWN')}")
        print(f"  Method: {result.get('Classification_Method', 'UNKNOWN')}")
        print(f"  Notes: {result.get('Quality_Notes', 'N/A')}")
        
        if result.get('Classification_Method') == 'enhanced':
            print("✅ Enhanced classification is working")
        else:
            print("❌ Enhanced classification not activated")
            return False
            
    except Exception as e:
        print(f"❌ Classification test failed: {e}")
        return False
    
    # Test number extraction
    print("\nTesting enhanced number extraction:")
    test_addresses = [
        'SALERANO SUL LAMBRO(LO) VICOLO CREMONA n. 34',
        'Vicolo Cremona, 34, 26857 Salerano sul Lambro LO',
        'OSPEDALETTO LODIGIANO(LO) CASCINA VILLAFRANCA DI MEZZO n. 1',
        'Cascina Villafranca di Mezzo, 1, 26864 Ospedaletto Lodigiano LO'
    ]
    
    for address in test_addresses:
        number = pipeline.extract_street_number_enhanced(address)
        print(f"  '{address[:40]}...' -> '{number}'")
    
    print("\n✅ All integration tests passed!")
    print("\nNext steps:")
    print("1. Copy your existing API tokens to config_enhanced.json")
    print("2. Run a test campaign with enhanced classification enabled")
    print("3. Compare results with original classification")
    
    return True

if __name__ == "__main__":
    success = test_enhanced_integration()
    if success:
        print("\n🎉 Enhanced classification successfully integrated!")
    else:
        print("\n❌ Integration test failed. Please check the errors above.")