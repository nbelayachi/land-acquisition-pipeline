"""
Analyze v3.0.0 Campaign Results
Identify new features and examine the enhanced classification performance
"""

import pandas as pd
import os

def analyze_v3_campaign_results():
    """Comprehensive analysis of v3.0.0 campaign results"""
    
    results_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2056\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2056_Results.xlsx"
    
    print("🔍 ANALYZING v3.0.0 CAMPAIGN RESULTS")
    print("=" * 60)
    print(f"📁 File: {os.path.basename(results_file)}")
    print()
    
    try:
        # Read all sheets to identify new features
        excel_file = pd.ExcelFile(results_file)
        print(f"📊 Available sheets: {excel_file.sheet_names}")
        print()
        
        # Check for new Strategic_Mailing_List sheet
        if 'Strategic_Mailing_List' in excel_file.sheet_names:
            print("🆕 NEW FEATURE DETECTED: Strategic_Mailing_List sheet")
            strategic_df = pd.read_excel(results_file, sheet_name='Strategic_Mailing_List')
            print(f"   Rows: {len(strategic_df)}")
            print(f"   Columns: {list(strategic_df.columns)}")
            
            if len(strategic_df) > 0:
                print("   Sample data:")
                for idx, row in strategic_df.head(3).iterrows():
                    print(f"     Row {idx + 1}: {row.get('Municipality', 'N/A')} | {row.get('Full_Name', 'N/A')} | {row.get('Mailing_Address', 'N/A')[:50]}...")
            print()
        
        # Analyze enhanced classification results
        if 'All_Validation_Ready' in excel_file.sheet_names:
            validation_df = pd.read_excel(results_file, sheet_name='All_Validation_Ready')
            print("🧠 ENHANCED CLASSIFICATION ANALYSIS")
            print("-" * 40)
            print(f"Total addresses processed: {len(validation_df)}")
            
            # Check for enhanced classification columns
            enhanced_columns = [col for col in validation_df.columns if 'Classification_Method' in col or 'ULTRA_HIGH' in str(validation_df.get('Address_Confidence', [])).upper()]
            if 'Classification_Method' in validation_df.columns:
                print("✅ Enhanced classification method tracking detected")
                method_dist = validation_df['Classification_Method'].value_counts()
                print(f"   Classification methods used: {dict(method_dist)}")
            
            # Analyze confidence distribution
            if 'Address_Confidence' in validation_df.columns:
                confidence_dist = validation_df['Address_Confidence'].value_counts()
                print(f"\n📊 Confidence Distribution:")
                for level, count in confidence_dist.items():
                    percentage = (count / len(validation_df)) * 100
                    print(f"   {level}: {count} addresses ({percentage:.1f}%)")
                
                # Check for ULTRA_HIGH confidence (new feature)
                ultra_high_count = confidence_dist.get('ULTRA_HIGH', 0)
                if ultra_high_count > 0:
                    print(f"\n🚀 ULTRA_HIGH CONFIDENCE DETECTED: {ultra_high_count} addresses")
                    print("   These addresses are ready for immediate printing!")
                    
                    # Show sample ULTRA_HIGH addresses
                    ultra_high_addresses = validation_df[validation_df['Address_Confidence'] == 'ULTRA_HIGH']
                    print("   Sample ULTRA_HIGH addresses:")
                    for idx, row in ultra_high_addresses.head(3).iterrows():
                        print(f"     {row.get('cleaned_ubicazione', 'N/A')[:50]}...")
                        print(f"     -> {row.get('Geocoded_Address_Italian', 'N/A')[:50]}...")
            
            # Check routing channel distribution
            if 'Routing_Channel' in validation_df.columns:
                routing_dist = validation_df['Routing_Channel'].value_counts()
                print(f"\n📮 Routing Distribution:")
                for channel, count in routing_dist.items():
                    percentage = (count / len(validation_df)) * 100
                    print(f"   {channel}: {count} addresses ({percentage:.1f}%)")
            
            print()
        
        # Compare with previous version results if available
        print("📈 PERFORMANCE COMPARISON")
        print("-" * 30)
        
        # Calculate time savings potential
        if 'Address_Confidence' in validation_df.columns:
            ultra_high = len(validation_df[validation_df['Address_Confidence'] == 'ULTRA_HIGH'])
            high = len(validation_df[validation_df['Address_Confidence'] == 'HIGH'])
            medium = len(validation_df[validation_df['Address_Confidence'] == 'MEDIUM'])
            low = len(validation_df[validation_df['Address_Confidence'] == 'LOW'])
            
            # Time calculation (8 minutes per address for manual review)
            total_addresses = len(validation_df)
            current_time = total_addresses * 8  # All need review
            enhanced_time = (ultra_high * 0) + (high * 5) + (medium * 8) + (low * 0)  # ULTRA_HIGH = 0 min, HIGH = 5 min
            
            time_saved = current_time - enhanced_time
            efficiency_gain = (time_saved / current_time) * 100 if current_time > 0 else 0
            
            print(f"Manual review time analysis:")
            print(f"   Traditional approach: {current_time} minutes ({current_time/60:.1f} hours)")
            print(f"   Enhanced approach: {enhanced_time} minutes ({enhanced_time/60:.1f} hours)")
            print(f"   Time savings: {time_saved} minutes ({efficiency_gain:.1f}% improvement)")
            print(f"   Immediate print-ready: {ultra_high} addresses ({ultra_high/total_addresses*100:.1f}%)")
        
        # Check for new parcel ownership features
        ownership_sheets = ['Owners_By_Parcel', 'Owners_Normalized']
        for sheet in ownership_sheets:
            if sheet in excel_file.sheet_names:
                df = pd.read_excel(results_file, sheet_name=sheet)
                print(f"\n🏠 {sheet.upper()} ANALYSIS")
                print(f"   Rows: {len(df)}")
                print(f"   Columns: {list(df.columns)}")
                
                if sheet == 'Owners_By_Parcel' and len(df) > 0:
                    # Analyze parcel ownership complexity
                    if 'total_owners' in df.columns:
                        avg_owners = df['total_owners'].mean()
                        max_owners = df['total_owners'].max()
                        print(f"   Average owners per parcel: {avg_owners:.1f}")
                        print(f"   Maximum owners per parcel: {max_owners}")
                        
                        # Show complex ownership examples
                        complex_parcels = df[df['total_owners'] > 2]
                        if len(complex_parcels) > 0:
                            print(f"   Complex ownership parcels: {len(complex_parcels)}")
        
        # Analyze address parsing improvements
        print(f"\n🔧 ADDRESS PARSING ANALYSIS")
        print("-" * 30)
        
        if 'All_Validation_Ready' in excel_file.sheet_names:
            # Check for improved street number extraction
            validation_df = pd.read_excel(results_file, sheet_name='All_Validation_Ready')
            
            problematic_streets = []
            for idx, row in validation_df.iterrows():
                original = str(row.get('cleaned_ubicazione', ''))
                if any(street in original.upper() for street in ['VIA 4 NOVEMBRE', 'VIA 2 GIUGNO', 'VIA 25 APRILE']):
                    confidence = row.get('Address_Confidence', 'UNKNOWN')
                    problematic_streets.append({
                        'address': original,
                        'confidence': confidence,
                        'notes': row.get('Quality_Notes', 'N/A')
                    })
            
            if problematic_streets:
                print("   Problematic street names (numbers in street names):")
                for street in problematic_streets:
                    print(f"     {street['address'][:60]} -> {street['confidence']}")
            else:
                print("   No problematic street number extractions detected")
        
        return {
            'total_sheets': len(excel_file.sheet_names),
            'new_features_detected': [
                'Strategic_Mailing_List' if 'Strategic_Mailing_List' in excel_file.sheet_names else None,
                'ULTRA_HIGH_confidence' if ultra_high_count > 0 else None,
                'Enhanced_classification' if 'Classification_Method' in validation_df.columns else None
            ],
            'ultra_high_count': ultra_high_count if 'ultra_high_count' in locals() else 0,
            'time_savings_percent': efficiency_gain if 'efficiency_gain' in locals() else 0
        }
        
    except Exception as e:
        print(f"❌ Error analyzing results: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 Starting v3.0.0 results analysis...")
    results = analyze_v3_campaign_results()
    
    if results:
        print(f"\n✅ Analysis complete!")
        print(f"📊 Summary:")
        print(f"   Total sheets: {results['total_sheets']}")
        print(f"   ULTRA_HIGH addresses: {results['ultra_high_count']}")
        print(f"   Estimated time savings: {results['time_savings_percent']:.1f}%")
        print(f"   New features: {[f for f in results['new_features_detected'] if f]}")
    else:
        print(f"\n❌ Analysis failed")