"""
Real Campaign Validation Script
Analyzes actual campaign results to validate enhanced funnel implementation
"""

import pandas as pd
import numpy as np
import os

def validate_enhanced_funnel_output(results_file_path):
    """
    Validate enhanced funnel implementation using real campaign results
    
    Args:
        results_file_path: Path to the campaign results Excel file
    """
    
    print("=== REAL CAMPAIGN ENHANCED FUNNEL VALIDATION ===\n")
    print(f"Analyzing: {os.path.basename(results_file_path)}")
    
    if not os.path.exists(results_file_path):
        print(f"ERROR: File not found at {results_file_path}")
        return False
    
    try:
        # Read Excel file and get sheet names
        excel_file = pd.ExcelFile(results_file_path)
        sheet_names = excel_file.sheet_names
        
        print(f"Available sheets: {sheet_names}")
        
        # Check for enhanced funnel sheets
        has_enhanced_funnel = 'Enhanced_Funnel_Analysis' in sheet_names
        has_quality_distribution = 'Address_Quality_Distribution' in sheet_names
        has_old_funnel = 'Funnel_Analysis' in sheet_names
        
        print(f"\nSheet Validation:")
        print(f"  Enhanced_Funnel_Analysis: {'✅ FOUND' if has_enhanced_funnel else '❌ MISSING'}")
        print(f"  Address_Quality_Distribution: {'✅ FOUND' if has_quality_distribution else '❌ MISSING'}")
        print(f"  Old Funnel_Analysis: {'⚠️ FOUND (should be replaced)' if has_old_funnel else '✅ REPLACED'}")
        
        # Analyze Enhanced Funnel Analysis
        if has_enhanced_funnel:
            print(f"\n=== ENHANCED FUNNEL ANALYSIS ===")
            enhanced_funnel_df = pd.read_excel(results_file_path, sheet_name='Enhanced_Funnel_Analysis')
            
            print(f"Rows: {len(enhanced_funnel_df)}")
            print(f"Columns: {list(enhanced_funnel_df.columns)}")
            
            # Check for expected columns
            expected_columns = [
                'Funnel_Type', 'Stage', 'Count', 'Hectares', 'Conversion_Rate',
                'Retention_Rate', 'Business_Rule', 'Automation_Level', 'Process_Notes'
            ]
            
            missing_columns = [col for col in expected_columns if col not in enhanced_funnel_df.columns]
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
            else:
                print("✅ All expected columns present")
            
            # Analyze funnel types
            if 'Funnel_Type' in enhanced_funnel_df.columns:
                funnel_types = enhanced_funnel_df['Funnel_Type'].unique()
                print(f"Funnel types: {list(funnel_types)}")
                
                land_funnel = enhanced_funnel_df[enhanced_funnel_df['Funnel_Type'] == 'Land Acquisition']
                contact_funnel = enhanced_funnel_df[enhanced_funnel_df['Funnel_Type'] == 'Contact Processing']
                
                print(f"Land Acquisition stages: {len(land_funnel)}")
                print(f"Contact Processing stages: {len(contact_funnel)}")
                
                # Show key metrics
                if len(land_funnel) > 0:
                    input_parcels = land_funnel[land_funnel['Stage'].str.contains('Input Parcels', na=False)]['Count'].iloc[0] if len(land_funnel[land_funnel['Stage'].str.contains('Input Parcels', na=False)]) > 0 else 0
                    category_a = land_funnel[land_funnel['Stage'].str.contains('Category A', na=False)]['Count'].iloc[0] if len(land_funnel[land_funnel['Stage'].str.contains('Category A', na=False)]) > 0 else 0
                    
                    if input_parcels > 0:
                        land_efficiency = (category_a / input_parcels * 100)
                        print(f"Land Acquisition Efficiency: {land_efficiency:.1f}%")
                
                if len(contact_funnel) > 0:
                    addresses = contact_funnel[contact_funnel['Stage'].str.contains('Address Pairs', na=False)]['Count'].iloc[0] if len(contact_funnel[contact_funnel['Stage'].str.contains('Address Pairs', na=False)]) > 0 else 0
                    direct_mail = contact_funnel[contact_funnel['Stage'].str.contains('Direct Mail', na=False)]['Count'].iloc[0] if len(contact_funnel[contact_funnel['Stage'].str.contains('Direct Mail', na=False)]) > 0 else 0
                    
                    print(f"Total Addresses: {addresses}")
                    print(f"Direct Mail Ready: {direct_mail}")
                    if addresses > 0:
                        direct_mail_efficiency = (direct_mail / addresses * 100)
                        print(f"Direct Mail Efficiency: {direct_mail_efficiency:.1f}%")
                
                # Check conversion rates
                if 'Conversion_Rate' in enhanced_funnel_df.columns:
                    conversion_rates = enhanced_funnel_df['Conversion_Rate'].dropna()
                    print(f"Conversion rates calculated: {len(conversion_rates)} stages")
                    if len(conversion_rates) > 0:
                        print(f"Example conversion rates: {conversion_rates.head().tolist()}")
        
        # Analyze Address Quality Distribution
        if has_quality_distribution:
            print(f"\n=== ADDRESS QUALITY DISTRIBUTION ===")
            quality_df = pd.read_excel(results_file_path, sheet_name='Address_Quality_Distribution')
            
            print(f"Rows: {len(quality_df)}")
            print(f"Columns: {list(quality_df.columns)}")
            
            if 'Quality_Level' in quality_df.columns and 'Count' in quality_df.columns:
                total_addresses = quality_df['Count'].sum()
                print(f"Total addresses analyzed: {total_addresses}")
                
                for _, row in quality_df.iterrows():
                    quality = row.get('Quality_Level', 'Unknown')
                    count = row.get('Count', 0)
                    percentage = row.get('Percentage', 0)
                    automation = row.get('Automation_Level', 'Unknown')
                    routing = row.get('Routing_Decision', 'Unknown')
                    
                    print(f"  {quality}: {count} addresses ({percentage}%) - {automation} - {routing}")
                
                # Calculate zero-touch rate
                ultra_high_count = quality_df[quality_df['Quality_Level'] == 'ULTRA_HIGH']['Count'].iloc[0] if len(quality_df[quality_df['Quality_Level'] == 'ULTRA_HIGH']) > 0 else 0
                zero_touch_rate = (ultra_high_count / total_addresses * 100) if total_addresses > 0 else 0
                print(f"Zero-Touch Processing Rate: {zero_touch_rate:.1f}%")
        
        # Compare with Campaign Summary for consistency
        if 'Campaign_Summary' in sheet_names:
            print(f"\n=== CONSISTENCY CHECK WITH CAMPAIGN SUMMARY ===")
            summary_df = pd.read_excel(results_file_path, sheet_name='Campaign_Summary')
            
            if not summary_df.empty:
                print(f"Campaign Summary rows: {len(summary_df)}")
                
                # Check key metrics consistency
                if has_enhanced_funnel:
                    summary_parcels = summary_df['Input_Parcels'].sum() if 'Input_Parcels' in summary_df.columns else 0
                    summary_addresses = summary_df['Unique_Owner_Address_Pairs'].sum() if 'Unique_Owner_Address_Pairs' in summary_df.columns else 0
                    summary_direct_mail = summary_df['Direct_Mail_Final_Contacts'].sum() if 'Direct_Mail_Final_Contacts' in summary_df.columns else 0
                    
                    print(f"Summary - Input Parcels: {summary_parcels}")
                    print(f"Summary - Total Addresses: {summary_addresses}")
                    print(f"Summary - Direct Mail: {summary_direct_mail}")
                    
                    # Cross-check with enhanced funnel
                    if len(enhanced_funnel_df) > 0:
                        funnel_parcels = enhanced_funnel_df[enhanced_funnel_df['Stage'].str.contains('Input Parcels', na=False)]['Count'].iloc[0] if len(enhanced_funnel_df[enhanced_funnel_df['Stage'].str.contains('Input Parcels', na=False)]) > 0 else 0
                        funnel_addresses = enhanced_funnel_df[enhanced_funnel_df['Stage'].str.contains('Address Pairs', na=False)]['Count'].iloc[0] if len(enhanced_funnel_df[enhanced_funnel_df['Stage'].str.contains('Address Pairs', na=False)]) > 0 else 0
                        funnel_direct_mail = enhanced_funnel_df[enhanced_funnel_df['Stage'].str.contains('Direct Mail', na=False)]['Count'].iloc[0] if len(enhanced_funnel_df[enhanced_funnel_df['Stage'].str.contains('Direct Mail', na=False)]) > 0 else 0
                        
                        print(f"Funnel - Input Parcels: {funnel_parcels}")
                        print(f"Funnel - Total Addresses: {funnel_addresses}")
                        print(f"Funnel - Direct Mail: {funnel_direct_mail}")
                        
                        # Check consistency
                        parcels_match = abs(summary_parcels - funnel_parcels) <= 1
                        addresses_match = abs(summary_addresses - funnel_addresses) <= 1
                        direct_mail_match = abs(summary_direct_mail - funnel_direct_mail) <= 1
                        
                        print(f"\nConsistency Check:")
                        print(f"  Parcels: {'✅ MATCH' if parcels_match else '❌ MISMATCH'}")
                        print(f"  Addresses: {'✅ MATCH' if addresses_match else '❌ MISMATCH'}")
                        print(f"  Direct Mail: {'✅ MATCH' if direct_mail_match else '❌ MISMATCH'}")
        
        # Overall validation result
        print(f"\n=== VALIDATION SUMMARY ===")
        
        validation_passed = True
        issues = []
        
        if not has_enhanced_funnel:
            validation_passed = False
            issues.append("Enhanced_Funnel_Analysis sheet missing")
        
        if not has_quality_distribution:
            validation_passed = False
            issues.append("Address_Quality_Distribution sheet missing")
        
        if has_old_funnel:
            issues.append("Old Funnel_Analysis sheet still present (should be replaced)")
        
        if missing_columns:
            validation_passed = False
            issues.append(f"Missing required columns: {missing_columns}")
        
        if validation_passed:
            print("🎉 VALIDATION PASSED - Enhanced funnel implementation working correctly!")
        else:
            print("⚠️ VALIDATION ISSUES FOUND:")
            for issue in issues:
                print(f"  - {issue}")
        
        if issues:
            print("\nIssues detected:")
            for issue in issues:
                print(f"  ❌ {issue}")
        
        return validation_passed
        
    except Exception as e:
        print(f"ERROR during validation: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_campaign_performance(results_file_path):
    """
    Additional analysis of campaign performance metrics
    """
    
    print(f"\n=== CAMPAIGN PERFORMANCE ANALYSIS ===")
    
    try:
        # Read enhanced funnel and quality distribution
        enhanced_funnel_df = pd.read_excel(results_file_path, sheet_name='Enhanced_Funnel_Analysis')
        quality_df = pd.read_excel(results_file_path, sheet_name='Address_Quality_Distribution')
        
        # Calculate executive KPIs manually to verify
        land_funnel = enhanced_funnel_df[enhanced_funnel_df['Funnel_Type'] == 'Land Acquisition']
        contact_funnel = enhanced_funnel_df[enhanced_funnel_df['Funnel_Type'] == 'Contact Processing']
        
        if len(land_funnel) > 0 and len(contact_funnel) > 0:
            # Extract key metrics
            input_parcels = land_funnel[land_funnel['Stage'].str.contains('Input Parcels', na=False)]['Count'].iloc[0]
            qualified_parcels = land_funnel[land_funnel['Stage'].str.contains('Category A', na=False)]['Count'].iloc[0]
            total_addresses = contact_funnel[contact_funnel['Stage'].str.contains('Address Pairs', na=False)]['Count'].iloc[0]
            direct_mail = contact_funnel[contact_funnel['Stage'].str.contains('Direct Mail', na=False)]['Count'].iloc[0]
            
            # Calculate KPIs
            land_efficiency = (qualified_parcels / input_parcels * 100) if input_parcels > 0 else 0
            contact_multiplication = (total_addresses / qualified_parcels) if qualified_parcels > 0 else 0
            direct_mail_efficiency = (direct_mail / total_addresses * 100) if total_addresses > 0 else 0
            
            # Zero-touch rate from quality distribution
            ultra_high_count = quality_df[quality_df['Quality_Level'] == 'ULTRA_HIGH']['Count'].iloc[0] if len(quality_df[quality_df['Quality_Level'] == 'ULTRA_HIGH']) > 0 else 0
            zero_touch_rate = (ultra_high_count / total_addresses * 100) if total_addresses > 0 else 0
            
            print(f"📊 EXECUTIVE KPIs:")
            print(f"  Land Acquisition Efficiency: {land_efficiency:.1f}%")
            print(f"  Contact Multiplication Factor: {contact_multiplication:.1f}x")
            print(f"  Direct Mail Efficiency: {direct_mail_efficiency:.1f}%")
            print(f"  Zero-Touch Processing Rate: {zero_touch_rate:.1f}%")
            
            # Business insights
            print(f"\n💡 BUSINESS INSIGHTS:")
            if land_efficiency >= 80:
                print(f"  ✅ Excellent land retention ({land_efficiency:.1f}% kept through filters)")
            elif land_efficiency >= 60:
                print(f"  ⚠️ Good land retention ({land_efficiency:.1f}% kept through filters)")
            else:
                print(f"  ❌ Low land retention ({land_efficiency:.1f}% kept through filters)")
            
            if contact_multiplication >= 2.5:
                print(f"  ✅ Strong contact expansion ({contact_multiplication:.1f}x addresses per qualified parcel)")
            else:
                print(f"  ⚠️ Limited contact expansion ({contact_multiplication:.1f}x addresses per qualified parcel)")
            
            if zero_touch_rate >= 15:
                print(f"  ✅ High automation potential ({zero_touch_rate:.1f}% zero-touch ready)")
            elif zero_touch_rate >= 10:
                print(f"  ⚠️ Moderate automation potential ({zero_touch_rate:.1f}% zero-touch ready)")
            else:
                print(f"  ❌ Low automation potential ({zero_touch_rate:.1f}% zero-touch ready)")
            
        return True
        
    except Exception as e:
        print(f"ERROR in performance analysis: {e}")
        return False

def main():
    """Main validation function"""
    
    # File path for real campaign results
    results_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250702_1141\LandAcquisition_Casalpusterlengo_Castiglione_20250702_1141_Results.xlsx"
    
    print("Enhanced Funnel Implementation - Real Campaign Validation")
    print("=" * 60)
    
    # Run validation
    validation_success = validate_enhanced_funnel_output(results_file)
    
    if validation_success:
        # Run performance analysis
        analyze_campaign_performance(results_file)
        
        print(f"\n🎉 VALIDATION COMPLETE - Enhanced funnel implementation is working correctly!")
        print(f"✅ Ready for GitHub commit and documentation updates")
    else:
        print(f"\n⚠️ VALIDATION FAILED - Issues need to be resolved before commit")
    
    return validation_success

if __name__ == "__main__":
    main()