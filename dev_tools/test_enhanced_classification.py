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

from enhanced_address_classification import EnhancedAddressClassifier

def test_enhanced_classification_on_real_data():
    """Test enhanced classification on real campaign data"""
    
    # Path to real campaign results
    results_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2018\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2018_Results.xlsx"
    
    print("🧪 TESTING ENHANCED ADDRESS CLASSIFICATION")
    print("=" * 60)
    print()
    
    try:
        # Read the validation ready data
        df = pd.read_excel(results_file, sheet_name='All_Validation_Ready')
        print(f"📊 Loaded {len(df)} addresses from real campaign data")
        print()
        
        # Initialize enhanced classifier
        classifier = EnhancedAddressClassifier()
        
        # Current vs Enhanced comparison
        comparison_results = []
        
        print("🔍 ANALYZING EACH ADDRESS:")
        print("-" * 40)
        
        for idx, row in df.iterrows():
            # Current classification (from data)
            current_confidence = row.get('Address_Confidence', 'UNKNOWN')
            current_routing = row.get('Routing_Channel', 'UNKNOWN')
            
            # Enhanced classification
            enhanced_result = classifier.classify_address_quality_enhanced(row)
            enhanced_confidence = enhanced_result['Address_Confidence']
            enhanced_routing = enhanced_result['Routing_Channel']
            
            # Track comparison
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
            
            # Show detailed analysis for first few addresses
            if idx < 5:
                print(f"\nAddress {idx + 1}:")
                print(f"  Original: {row.get('cleaned_ubicazione', '')[:60]}...")
                print(f"  Geocoded: {row.get('Geocoded_Address_Italian', '')[:60]}...")
                print(f"  Current:  {current_confidence} → {current_routing}")
                print(f"  Enhanced: {enhanced_confidence} → {enhanced_routing}")
                print(f"  Reasoning: {enhanced_result.get('Confidence_Reasoning', '')}")
                if enhanced_confidence != current_confidence:
                    print(f"  ⚡ IMPROVEMENT: {current_confidence} → {enhanced_confidence}")
        
        # Summary analysis
        print("\n" + "=" * 60)
        print("📊 CLASSIFICATION COMPARISON SUMMARY")
        print("=" * 60)
        
        # Current distribution
        current_dist = pd.Series([r['current_confidence'] for r in comparison_results]).value_counts()
        enhanced_dist = pd.Series([r['enhanced_confidence'] for r in comparison_results]).value_counts()
        
        print("\n🔄 CONFIDENCE DISTRIBUTION COMPARISON:")
        print(f"{'Confidence Level':<15} {'Current':<10} {'Enhanced':<10} {'Change':<10}")
        print("-" * 45)
        
        all_levels = set(current_dist.index) | set(enhanced_dist.index)
        for level in sorted(all_levels):
            current_count = current_dist.get(level, 0)
            enhanced_count = enhanced_dist.get(level, 0)
            change = enhanced_count - current_count
            change_str = f"+{change}" if change > 0 else str(change)
            print(f"{level:<15} {current_count:<10} {enhanced_count:<10} {change_str:<10}")
        
        # Improvements analysis
        improvements = [r for r in comparison_results if r['improvement']]
        print(f"\n🚀 IMPROVEMENTS DETECTED:")
        print(f"Total addresses with improved confidence: {len(improvements)}/{len(comparison_results)} ({len(improvements)/len(comparison_results)*100:.1f}%)")
        
        if improvements:
            print("\nImprovement breakdown:")
            improvement_types = {}
            for imp in improvements:
                change = f"{imp['current_confidence']} → {imp['enhanced_confidence']}"
                improvement_types[change] = improvement_types.get(change, 0) + 1
            
            for change, count in improvement_types.items():
                print(f"  {change}: {count} addresses")
        
        # Potential time savings
        print(f"\n⏰ POTENTIAL TIME SAVINGS:")
        
        # Count ULTRA_HIGH (immediate print ready)
        ultra_high_count = enhanced_dist.get('ULTRA_HIGH', 0)
        high_count = enhanced_dist.get('HIGH', 0)
        
        # Time calculation (assuming 8 minutes per address currently)
        current_review_time = len(df) * 8  # All addresses need review
        enhanced_review_time = (ultra_high_count * 0) + (high_count * 5) + ((len(df) - ultra_high_count - high_count) * 8)
        
        time_saved = current_review_time - enhanced_review_time
        
        print(f"Current review time: {current_review_time} minutes ({current_review_time/60:.1f} hours)")
        print(f"Enhanced review time: {enhanced_review_time} minutes ({enhanced_review_time/60:.1f} hours)")
        print(f"Time savings: {time_saved} minutes ({time_saved/60:.1f} hours, {time_saved/current_review_time*100:.1f}% reduction)")
        
        # Immediate print-ready analysis
        if ultra_high_count > 0:
            print(f"\n⚡ IMMEDIATE PRINT-READY ADDRESSES:")
            print(f"{ultra_high_count} addresses ({ultra_high_count/len(df)*100:.1f}%) can go directly to printing")
            print("Sample ULTRA_HIGH addresses:")
            
            ultra_high_addresses = [r for r in comparison_results if r['enhanced_confidence'] == 'ULTRA_HIGH']
            for i, addr in enumerate(ultra_high_addresses[:3]):
                print(f"  {i+1}. {addr['original_address'][:50]}...")
                print(f"     → {addr['geocoded_address'][:50]}...")
                print(f"     Reason: {addr['confidence_reasoning']}")
        
        # Export detailed results
        results_df = pd.DataFrame(comparison_results)
        output_file = "enhanced_classification_test_results.xlsx"
        results_df.to_excel(output_file, index=False)
        print(f"\n💾 Detailed results exported to: {output_file}")
        
        return comparison_results
        
    except FileNotFoundError:
        print(f"❌ Campaign results file not found: {results_file}")
        print("Please update the file path or run a campaign first")
        return None
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return None

def analyze_number_matching_improvements():
    """Analyze specific number matching improvements"""
    
    print("\n🔢 NUMBER MATCHING ANALYSIS")
    print("=" * 40)
    
    classifier = EnhancedAddressClassifier()
    
    # Test cases for number matching
    test_cases = [
        ("32", "32", "Exact match"),
        ("32", "32A", "Base number match with suffix"),
        ("32A", "32B", "Same base, different suffix"),
        ("32", "34", "Adjacent numbers"),
        ("32", "36", "Close numbers"),
        ("32", "45", "Different numbers"),
        ("32BIS", "32", "Original has suffix, geocoded doesn't"),
        ("SNC", None, "No civic number"),
    ]
    
    print(f"{'Original':<10} {'Geocoded':<10} {'Similarity':<12} {'Confidence':<12} {'Description'}")
    print("-" * 70)
    
    for orig, geo, desc in test_cases:
        if orig and geo:
            similarity = classifier.calculate_number_similarity(orig, geo)
            sim_score = f"{similarity['similarity']:.1f}"
            confidence = similarity['confidence']
            print(f"{orig:<10} {geo:<10} {sim_score:<12} {confidence:<12} {desc}")
        else:
            print(f"{orig or 'None':<10} {geo or 'None':<10} {'N/A':<12} {'N/A':<12} {desc}")

if __name__ == "__main__":
    print("🚀 ENHANCED ADDRESS CLASSIFICATION TESTING")
    print("Testing enhanced classification against real campaign data...")
    print()
    
    # Test on real data
    results = test_enhanced_classification_on_real_data()
    
    # Test number matching specifically
    analyze_number_matching_improvements()
    
    print("\n✅ Testing complete!")
    print("\nNext steps:")
    print("1. Review the classification improvements")
    print("2. Validate ULTRA_HIGH addresses manually")
    print("3. Consider implementing the enhancement")
    print("4. Start with A/B testing on subset of addresses")