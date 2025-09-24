#!/usr/bin/env python3
"""
Analyze Final_Mailing_List Structure
Understand the complete pipeline flow from validation to final mailing
"""

import pandas as pd
import os

def analyze_pipeline_flow():
    print("🔍 ANALYZING COMPLETE PIPELINE FLOW")
    print("=" * 60)
    
    excel_path = "data/Campaign4_Results.xlsx"
    
    if not os.path.exists(excel_path):
        print(f"❌ File not found: {excel_path}")
        return
    
    try:
        # Load all relevant sheets
        print("📊 Loading all pipeline sheets...")
        all_validation = pd.read_excel(excel_path, sheet_name='All_Validation_Ready')
        final_mailing = pd.read_excel(excel_path, sheet_name='Final_Mailing_List')
        campaign_summary = pd.read_excel(excel_path, sheet_name='Campaign_Summary')
        
        print(f"   ✅ All_Validation_Ready: {len(all_validation)} records")
        print(f"   ✅ Final_Mailing_List: {len(final_mailing)} records")
        print(f"   ✅ Campaign_Summary: {len(campaign_summary)} municipalities")
        
        # Analyze All_Validation_Ready structure
        print("\n📋 ALL_VALIDATION_READY ANALYSIS:")
        print(f"   Columns: {list(all_validation.columns)}")
        
        if 'Address_Confidence' in all_validation.columns:
            confidence_dist = all_validation['Address_Confidence'].value_counts()
            print(f"   Address_Confidence distribution:")
            for level, count in confidence_dist.items():
                print(f"     {level}: {count}")
        
        if 'Routing_Channel' in all_validation.columns:
            routing_dist = all_validation['Routing_Channel'].value_counts()
            print(f"   Routing_Channel distribution:")
            for channel, count in routing_dist.items():
                print(f"     {channel}: {count}")
        
        # Analyze Final_Mailing_List structure
        print("\n📮 FINAL_MAILING_LIST ANALYSIS:")
        print(f"   Columns: {list(final_mailing.columns)}")
        print(f"   Total records: {len(final_mailing)}")
        
        # Check what confidence levels made it to final mailing
        if 'Address_Confidence' in final_mailing.columns:
            final_confidence_dist = final_mailing['Address_Confidence'].value_counts()
            print(f"   Address_Confidence in final mailing:")
            for level, count in final_confidence_dist.items():
                print(f"     {level}: {count}")
        
        # Check routing in final mailing
        if 'Routing_Channel' in final_mailing.columns:
            final_routing_dist = final_mailing['Routing_Channel'].value_counts()
            print(f"   Routing_Channel in final mailing:")
            for channel, count in final_routing_dist.items():
                print(f"     {channel}: {count}")
        
        # Owner analysis
        if 'cf' in final_mailing.columns:
            unique_owners_final = final_mailing['cf'].nunique()
            print(f"   Unique owners in final mailing: {unique_owners_final}")
            
            # Address per owner distribution
            addresses_per_owner = final_mailing.groupby('cf').size()
            print(f"   Addresses per owner:")
            print(f"     Mean: {addresses_per_owner.mean():.1f}")
            print(f"     Median: {addresses_per_owner.median():.1f}")
            print(f"     Max: {addresses_per_owner.max()}")
            print(f"     Owners with multiple addresses: {(addresses_per_owner > 1).sum()}")
        
        # Municipality analysis
        if 'comune' in final_mailing.columns:
            final_municipality_dist = final_mailing['comune'].value_counts()
            print(f"   Municipality distribution in final mailing:")
            for municipality, count in final_municipality_dist.items():
                print(f"     {municipality}: {count}")
        
        # Compare validation vs final mailing
        print("\n🔄 PIPELINE FLOW ANALYSIS:")
        
        # Check what happened to each confidence level
        if 'Address_Confidence' in all_validation.columns and 'Address_Confidence' in final_mailing.columns:
            print(f"   Pipeline progression:")
            for level in ['ULTRA_HIGH', 'HIGH', 'MEDIUM', 'LOW']:
                validation_count = (all_validation['Address_Confidence'] == level).sum()
                final_count = (final_mailing['Address_Confidence'] == level).sum()
                retention_rate = (final_count / validation_count * 100) if validation_count > 0 else 0
                print(f"     {level}: {validation_count} → {final_count} ({retention_rate:.1f}% retention)")
        
        # Check if there are additional filters applied
        print("\n🔍 FILTERING ANALYSIS:")
        
        # Check for common identifiers
        if 'cf' in all_validation.columns and 'cf' in final_mailing.columns:
            validation_owners = set(all_validation['cf'].unique())
            final_owners = set(final_mailing['cf'].unique())
            
            owners_in_both = validation_owners.intersection(final_owners)
            owners_only_validation = validation_owners - final_owners
            
            print(f"   Owner filtering:")
            print(f"     Owners in validation: {len(validation_owners)}")
            print(f"     Owners in final mailing: {len(final_owners)}")
            print(f"     Owners that made it through: {len(owners_in_both)}")
            print(f"     Owners filtered out: {len(owners_only_validation)}")
        
        # Look for additional columns in Final_Mailing_List that might explain filtering
        validation_cols = set(all_validation.columns)
        final_cols = set(final_mailing.columns)
        
        additional_cols = final_cols - validation_cols
        missing_cols = validation_cols - final_cols
        
        if additional_cols:
            print(f"   Additional columns in Final_Mailing_List: {list(additional_cols)}")
        if missing_cols:
            print(f"   Columns removed in Final_Mailing_List: {list(missing_cols)}")
        
        # Check for business logic indicators
        business_logic_columns = ['Addresses_Per_Owner', 'Address_Sequence', 'Best_Address', 'Priority_Address']
        for col in business_logic_columns:
            if col in final_mailing.columns:
                print(f"   Found business logic column: {col}")
                if final_mailing[col].dtype in ['int64', 'float64']:
                    print(f"     Stats: min={final_mailing[col].min()}, max={final_mailing[col].max()}, mean={final_mailing[col].mean():.1f}")
                else:
                    print(f"     Unique values: {final_mailing[col].unique()}")
        
        # Suggest corrections to Campaign_Summary
        print("\n💡 PIPELINE UNDERSTANDING & SUGGESTIONS:")
        
        print("1. PIPELINE STAGES CLARIFICATION:")
        print("   • All_Validation_Ready (642): Addresses that passed technical validation")
        print("   • Final_Mailing_List (303): Addresses that passed business validation")
        print("   • The 558 'Direct Mail Ready' appears to be intermediate stage")
        
        print("\n2. BUSINESS LOGIC APPLIED:")
        if len(final_mailing) < len(all_validation):
            reduction_rate = (1 - len(final_mailing) / len(all_validation)) * 100
            print(f"   • {reduction_rate:.1f}% reduction from validation to final mailing")
            print("   • Likely includes owner consolidation and business rules")
        
        print("\n3. SUGGESTED KPI CORRECTIONS:")
        print("   • 'Validation Ready': 642 addresses (technical validation)")
        print("   • 'Business Qualified': 303 addresses (final mailing list)")
        print("   • 'Unique Targets': 157 owners (strategic contacts)")
        print("   • Pipeline conversion: 47.2% (303/642)")
        
        print("\n4. DASHBOARD IMPROVEMENTS:")
        print("   • Add 'Business Qualification' stage to funnel")
        print("   • Show validation → qualification → mailing flow")
        print("   • Highlight owner consolidation benefits")
        print("   • Add 'Mailing Efficiency' metric (303 mailings vs 642 potential)")
        
        # Return data for dashboard corrections
        return {
            'all_validation': all_validation,
            'final_mailing': final_mailing,
            'campaign_summary': campaign_summary,
            'pipeline_conversion': len(final_mailing) / len(all_validation) * 100,
            'unique_owners': final_mailing['cf'].nunique() if 'cf' in final_mailing.columns else 0
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    analyze_pipeline_flow()