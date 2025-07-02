"""
Test script for enhanced funnel implementation
Run this in Spyder to validate the new funnel logic and mathematical consistency
"""

import pandas as pd
import numpy as np
import sys
import os

# Add the current directory to sys.path to import the pipeline
sys.path.append('C:/Projects/land-acquisition-pipeline')

def test_enhanced_funnel_syntax():
    """Test that the enhanced pipeline can be imported without syntax errors"""
    try:
        from land_acquisition_pipeline import IntegratedLandAcquisitionPipeline
        print("SUCCESS: Enhanced pipeline imported successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to import pipeline: {e}")
        return False

def test_enhanced_funnel_methods():
    """Test that the new methods exist and can be called"""
    try:
        from land_acquisition_pipeline import IntegratedLandAcquisitionPipeline
        
        # Create pipeline instance
        pipeline = IntegratedLandAcquisitionPipeline()
        
        # Test that new methods exist
        assert hasattr(pipeline, 'create_quality_distribution_df'), "create_quality_distribution_df method missing"
        assert hasattr(pipeline, 'calculate_executive_kpis'), "calculate_executive_kpis method missing"
        
        print("SUCCESS: All new methods exist in pipeline")
        return True
    except Exception as e:
        print(f"ERROR: Method validation failed: {e}")
        return False

def test_sample_funnel_data():
    """Test enhanced funnel with sample data matching the validation dataset"""
    try:
        from land_acquisition_pipeline import IntegratedLandAcquisitionPipeline
        
        pipeline = IntegratedLandAcquisitionPipeline()
        
        # Create sample data matching validation dataset structure
        sample_summary = {
            'Input_Parcels': 10,
            'Input_Area_Ha': 12.5,
            'After_API_Parcels': 10,
            'After_API_Area_Ha': 12.5,
            'Private_Owner_Parcels': 10,
            'Private_Owner_Area_Ha': 12.5,
            'After_CatA_Filter_Parcels': 8,
            'After_CatA_Filter_Area_Ha': 10.0,
            'Unique_Owners_on_Target_Parcels': 8,
            'Unique_Owner_Address_Pairs': 23,
            'Direct_Mail_Final_Contacts': 12,
            'Direct_Mail_Final_Area_Ha': 6.5,
            'Agency_Final_Contacts': 11,
            'Agency_Final_Area_Ha': 3.5
        }
        
        sample_funnel_metrics = {
            'input_parcels': 10,
            'input_area_ha': 12.5,
            'after_api_parcels': 10,
            'after_api_area_ha': 12.5
        }
        
        sample_municipality = {
            'CP': '26841',
            'comune': 'Casalpusterlengo',
            'provincia': 'Lodi'
        }
        
        # Test enhanced funnel creation
        enhanced_funnel_df = pipeline.create_funnel_analysis_df(
            sample_summary, sample_funnel_metrics, sample_municipality
        )
        
        print("SUCCESS: Enhanced funnel DataFrame created")
        print(f"   - Rows: {len(enhanced_funnel_df)}")
        print(f"   - Columns: {list(enhanced_funnel_df.columns)}")
        
        # Verify expected columns exist
        expected_columns = ['Funnel_Type', 'Stage', 'Count', 'Hectares', 'Conversion_Rate', 
                          'Retention_Rate', 'Business_Rule', 'Automation_Level', 'Process_Notes']
        
        for col in expected_columns:
            assert col in enhanced_funnel_df.columns, f"Missing column: {col}"
        
        print("SUCCESS: All expected columns present")
        
        # Test conversion rate calculations
        land_funnel = enhanced_funnel_df[enhanced_funnel_df['Funnel_Type'] == 'Land Acquisition']
        contact_funnel = enhanced_funnel_df[enhanced_funnel_df['Funnel_Type'] == 'Contact Processing']
        
        print(f"   - Land funnel stages: {len(land_funnel)}")
        print(f"   - Contact funnel stages: {len(contact_funnel)}")
        
        # Verify key metrics
        input_parcels = land_funnel[land_funnel['Stage'] == '1. Input Parcels']['Count'].iloc[0]
        qualified_parcels = land_funnel[land_funnel['Stage'] == '4. Category A Filter']['Count'].iloc[0]
        land_efficiency = (qualified_parcels / input_parcels * 100) if input_parcels > 0 else 0
        
        print(f"   - Land efficiency: {land_efficiency}% (Expected: 80.0%)")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Sample funnel test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quality_distribution():
    """Test quality distribution creation with sample data"""
    try:
        from land_acquisition_pipeline import IntegratedLandAcquisitionPipeline
        
        pipeline = IntegratedLandAcquisitionPipeline()
        
        # Create sample validation data with correct array lengths
        confidence_levels = ['ULTRA_HIGH'] * 4 + ['HIGH'] * 1 + ['MEDIUM'] * 13 + ['LOW'] * 5
        sample_validation_data = pd.DataFrame({
            'Address_Confidence': confidence_levels,
            'Best_Address': ['Address ' + str(i) for i in range(23)],
            'cf': ['CF' + str(i) for i in range(23)]
        })
        
        # Test quality distribution
        quality_df = pipeline.create_quality_distribution_df(
            sample_validation_data, 
            '26841', 
            ['Casalpusterlengo'], 
            'Lodi'
        )
        
        print("SUCCESS: Quality distribution DataFrame created")
        print(f"   - Rows: {len(quality_df)}")
        print(f"   - Quality levels: {quality_df['Quality_Level'].tolist()}")
        
        # Verify totals
        total_addresses = quality_df['Count'].sum()
        print(f"   - Total addresses: {total_addresses} (Expected: 23)")
        
        # Check ULTRA_HIGH percentage
        ultra_high_count = quality_df[quality_df['Quality_Level'] == 'ULTRA_HIGH']['Count'].iloc[0]
        ultra_high_pct = quality_df[quality_df['Quality_Level'] == 'ULTRA_HIGH']['Percentage'].iloc[0]
        print(f"   - ULTRA_HIGH: {ultra_high_count} addresses ({ultra_high_pct}%)")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Quality distribution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_executive_kpis():
    """Test executive KPI calculations"""
    try:
        from land_acquisition_pipeline import IntegratedLandAcquisitionPipeline
        
        pipeline = IntegratedLandAcquisitionPipeline()
        
        # Create sample enhanced funnel data
        enhanced_funnel_data = [
            {'Funnel_Type': 'Land Acquisition', 'Stage': '1. Input Parcels', 'Count': 10, 'Hectares': 12.5},
            {'Funnel_Type': 'Land Acquisition', 'Stage': '4. Category A Filter', 'Count': 8, 'Hectares': 10.0},
            {'Funnel_Type': 'Contact Processing', 'Stage': '1. Owners Identified', 'Count': 8, 'Hectares': 10.0},
            {'Funnel_Type': 'Contact Processing', 'Stage': '2. Address Pairs Created', 'Count': 23, 'Hectares': 10.0},
            {'Funnel_Type': 'Contact Processing', 'Stage': '4. Direct Mail Ready', 'Count': 12, 'Hectares': 6.5}
        ]
        
        enhanced_funnel_df = pd.DataFrame(enhanced_funnel_data)
        
        # Create sample quality distribution
        quality_data = [
            {'Quality_Level': 'ULTRA_HIGH', 'Count': 4, 'Percentage': 17.4},
            {'Quality_Level': 'HIGH', 'Count': 1, 'Percentage': 4.3},
            {'Quality_Level': 'MEDIUM', 'Count': 13, 'Percentage': 56.5},
            {'Quality_Level': 'LOW', 'Count': 5, 'Percentage': 21.7}
        ]
        
        quality_df = pd.DataFrame(quality_data)
        
        # Test KPI calculations
        kpis = pipeline.calculate_executive_kpis(enhanced_funnel_df, quality_df)
        
        print("SUCCESS: Executive KPIs calculated")
        print(f"   - Land Acquisition Efficiency: {kpis['land_acquisition_efficiency']}%")
        print(f"   - Contact Multiplication Factor: {kpis['contact_multiplication_factor']}x")
        print(f"   - Zero-Touch Processing Rate: {kpis['zero_touch_processing_rate']}%")
        print(f"   - Direct Mail Efficiency: {kpis['direct_mail_efficiency']}%")
        
        # Verify expected values
        assert kpis['land_acquisition_efficiency'] == 80.0, f"Expected 80.0%, got {kpis['land_acquisition_efficiency']}%"
        assert kpis['contact_multiplication_factor'] == 2.9, f"Expected 2.9x, got {kpis['contact_multiplication_factor']}x"
        assert kpis['zero_touch_processing_rate'] == 17.4, f"Expected 17.4%, got {kpis['zero_touch_processing_rate']}%"
        
        print("SUCCESS: All KPI values match expected results")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Executive KPI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=== ENHANCED FUNNEL IMPLEMENTATION TEST ===\n")
    
    tests = [
        ("Syntax Check", test_enhanced_funnel_syntax),
        ("Method Validation", test_enhanced_funnel_methods),
        ("Sample Funnel Data", test_sample_funnel_data),
        ("Quality Distribution", test_quality_distribution),
        ("Executive KPIs", test_executive_kpis)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
        print(f"{test_name}: {'PASSED' if result else 'FAILED'}\n")
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("=== TEST SUMMARY ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("ALL TESTS PASSED - Enhanced funnel implementation is ready!")
    else:
        print("Some tests failed - review the errors above")
        
    return passed == total

if __name__ == "__main__":
    main()