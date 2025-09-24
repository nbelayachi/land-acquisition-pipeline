#!/usr/bin/env python3
"""
Clarify Pipeline Metrics
Investigate proper pipeline efficiency, area calculations, and owner consolidation logic
"""

import pandas as pd
import os

def clarify_metrics():
    print("🔍 CLARIFYING PIPELINE METRICS")
    print("=" * 60)
    
    excel_path = "data/Campaign4_Results.xlsx"
    
    try:
        # Load all sheets
        campaign_summary = pd.read_excel(excel_path, sheet_name='Campaign_Summary')
        all_validation = pd.read_excel(excel_path, sheet_name='All_Validation_Ready')
        final_mailing = pd.read_excel(excel_path, sheet_name='Final_Mailing_List')
        
        # Clean campaign summary
        cs = campaign_summary
        clean_rows = cs['comune'].notna() & (cs['comune'] != '')
        cs_clean = cs[clean_rows].reset_index(drop=True)
        
        print("📊 PIPELINE EFFICIENCY CALCULATION:")
        print("=" * 40)
        
        # Input parcels vs final mailings
        input_parcels = cs_clean['Input_Parcels'].sum()
        final_mailings = len(final_mailing)
        
        print(f"   Input Parcels: {input_parcels}")
        print(f"   Final Mailings: {final_mailings}")
        
        # Calculate parcel-to-mailing efficiency
        parcel_efficiency = (final_mailings / input_parcels) * 100
        print(f"   Parcel-to-Mailing Efficiency: {parcel_efficiency:.1f}%")
        print(f"   Explanation: {parcel_efficiency:.1f}% of input parcels resulted in actionable mailings")
        
        # Alternative: Check if we can track parcels through the pipeline
        if 'Foglio' in final_mailing.columns and 'Particella' in final_mailing.columns:
            # Count unique parcels in final mailing
            final_parcels = final_mailing[['Foglio', 'Particella']].drop_duplicates()
            unique_final_parcels = len(final_parcels)
            print(f"   Unique parcels in final mailing: {unique_final_parcels}")
            
            parcel_retention = (unique_final_parcels / input_parcels) * 100
            print(f"   Parcel Retention Rate: {parcel_retention:.1f}%")
            print(f"   Explanation: {parcel_retention:.1f}% of input parcels are represented in final mailings")
        
        print(f"\n📐 AREA CALCULATIONS:")
        print("=" * 40)
        
        input_area = cs_clean['Input_Area_Ha'].sum()
        print(f"   Input Area (Campaign_Summary): {input_area:.1f} Ha")
        
        # Check if All_Validation_Ready has area data
        if 'Area' in all_validation.columns:
            validation_area = all_validation['Area'].sum()
            print(f"   Area in All_Validation_Ready: {validation_area:.1f} Ha")
        
        # Check final mailing area if available
        if 'Area' in final_mailing.columns:
            final_area = final_mailing['Area'].sum()
            print(f"   Area in Final_Mailing_List: {final_area:.1f} Ha")
        elif 'Parcels' in final_mailing.columns:
            print(f"   Final_Mailing_List doesn't have Area column, but has Parcels info")
        
        print(f"   What 356 Ha represents: Input area sum from Campaign_Summary")
        
        print(f"\n👥 OWNER CONSOLIDATION ANALYSIS:")
        print("=" * 40)
        
        # All_Validation_Ready owner analysis
        validation_owners = all_validation['cf'].nunique()
        validation_addresses = len(all_validation)
        
        print(f"   All_Validation_Ready:")
        print(f"     Total addresses: {validation_addresses}")
        print(f"     Unique owners: {validation_owners}")
        print(f"     Addresses per owner: {validation_addresses/validation_owners:.1f}")
        
        # Final_Mailing_List owner analysis
        final_owners = final_mailing['cf'].nunique()
        final_addresses = len(final_mailing)
        
        print(f"   Final_Mailing_List:")
        print(f"     Total mailing records: {final_addresses}")
        print(f"     Unique owners: {final_owners}")
        print(f"     Mailings per owner: {final_addresses/final_owners:.1f}")
        
        # Owner consolidation effect
        owners_filtered_out = validation_owners - final_owners
        addresses_filtered_out = validation_addresses - final_addresses
        
        print(f"   Consolidation Effect:")
        print(f"     Owners filtered out: {owners_filtered_out}")
        print(f"     Addresses filtered out: {addresses_filtered_out}")
        print(f"     Address reduction: {addresses_filtered_out/validation_addresses*100:.1f}%")
        
        # Explain owner consolidation logic
        print(f"\n💡 OWNER CONSOLIDATION EXPLANATION:")
        print("   1. Multiple addresses per owner are identified")
        print("   2. Business rules determine which addresses to mail")
        print("   3. Some owners may be excluded entirely")
        print("   4. Result: Focused mailing to key property holders")
        
        # Check for address sequence logic
        if 'Address_Sequence' in final_mailing.columns and 'Addresses_Per_Owner' in final_mailing.columns:
            addresses_per_owner_dist = final_mailing['Addresses_Per_Owner'].value_counts().sort_index()
            print(f"\n   Addresses per owner distribution in final mailing:")
            for addr_count, owner_count in addresses_per_owner_dist.items():
                print(f"     {addr_count} address(es): {owner_count} owners")
        
        print(f"\n🎯 RECOMMENDED METRICS:")
        print("=" * 40)
        print(f"1. Pipeline Efficiency: {parcel_efficiency:.1f}% (mailings per input parcel)")
        print(f"2. Input Area: {input_area:.0f} Ha (total land analyzed)")
        print(f"3. Owner Consolidation: {final_addresses/final_owners:.1f} mailings per owner")
        print(f"4. Address Optimization: {addresses_filtered_out/validation_addresses*100:.1f}% reduction through smart filtering")
        
        # Quality focus clarification
        print(f"\n⭐ QUALITY FOCUS CLARIFICATION:")
        print("=" * 40)
        
        validation_quality = all_validation['Address_Confidence'].value_counts()
        print(f"   Address_Confidence in All_Validation_Ready:")
        for level, count in validation_quality.items():
            print(f"     {level}: {count}")
        
        print(f"   Note: Final_Mailing_List doesn't have Address_Confidence column")
        print(f"   The quality metrics apply to the validation stage (642 addresses)")
        print(f"   Final mailing (303) represents business-optimized subset")
        
        return {
            'input_parcels': input_parcels,
            'final_mailings': final_mailings,
            'parcel_efficiency': parcel_efficiency,
            'input_area': input_area,
            'validation_owners': validation_owners,
            'final_owners': final_owners,
            'address_reduction': addresses_filtered_out/validation_addresses*100
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    clarify_metrics()