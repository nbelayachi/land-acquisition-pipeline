"""
Simple integration test for enhanced classification
"""

# Test the integration
print("Testing enhanced classification integration...")

# Test configuration
import json
try:
    with open('land_acquisition_config.json', 'r') as f:
        config = json.load(f)
    enhanced_config = config['land_acquisition_config']['enhanced_classification']
    print("✅ Configuration file loaded successfully")
    print(f"Enhanced classification enabled: {enhanced_config['enabled']}")
    print(f"ULTRA_HIGH threshold: {enhanced_config['ultra_high_completeness_threshold']}")
    print(f"HIGH threshold: {enhanced_config['high_completeness_threshold']}")
except Exception as e:
    print(f"❌ Config error: {e}")

# Test import
try:
    from land_acquisition_pipeline import IntegratedLandAcquisitionPipeline
    print("✅ Pipeline import successful")
except Exception as e:
    print(f"❌ Import error: {e}")

# Test initialization
try:
    pipeline = IntegratedLandAcquisitionPipeline('land_acquisition_config.json')
    print("✅ Pipeline initialization successful")
except Exception as e:
    print(f"❌ Initialization error: {e}")

# Test enhanced methods exist
methods = ['extract_street_number_enhanced', 'calculate_number_similarity', 'classify_address_quality_enhanced']
for method in methods:
    if hasattr(pipeline, method):
        print(f"✅ Method {method} exists")
    else:
        print(f"❌ Method {method} missing")

# Test sample classification
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
    result = pipeline.classify_address_quality(sample_row)
    print(f"✅ Classification test successful:")
    print(f"   Confidence: {result.get('Address_Confidence')}")
    print(f"   Method: {result.get('Classification_Method')}")
    print(f"   Notes: {result.get('Quality_Notes')}")
except Exception as e:
    print(f"❌ Classification test failed: {e}")

print("\n🎉 Integration test complete!")