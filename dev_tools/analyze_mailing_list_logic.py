#!/usr/bin/env python3
"""
Mailing List Generation Logic Analysis
Analyzes what happens to different quality addresses in the final mailing process
Usage: Run in Spyder and paste the output back for review
"""

import pandas as pd
import numpy as np

def analyze_mailing_list_generation(excel_path):
    """
    Analyze the mailing list generation logic and address quality handling
    """
    print("="*80)
    print("MAILING LIST GENERATION LOGIC ANALYSIS")
    print("="*80)
    print(f"File: {excel_path}")
    print()
    
    try:
        # Read relevant sheets
        df_validation = pd.read_excel(excel_path, sheet_name='All_Validation_Ready')
        df_final = pd.read_excel(excel_path, sheet_name='Final_Mailing_List')
        df_quality = pd.read_excel(excel_path, sheet_name='Address_Quality_Distribution')
        
        print("📊 ADDRESS QUALITY BREAKDOWN:")
        print("-" * 50)
        
        # Show quality distribution
        for _, row in df_quality.iterrows():
            quality = row['Quality_Level']
            count = row['Count']
            percentage = row['Percentage']
            routing = row['Routing_Decision']
            automation = row['Automation_Level']
            
            print(f"{quality:12} {count:3} addresses ({percentage:5.1f}%) → {routing:25} [{automation}]")
        
        total_addresses = df_quality['Count'].sum()
        print(f"{'TOTAL':12} {total_addresses:3} addresses (100.0%)")
        print()
        
        print("🔍 VALIDATION READY DETAILED ANALYSIS:")
        print("-" * 50)
        
        # Analyze validation ready by quality
        if 'Address_Confidence' in df_validation.columns and 'Routing_Channel' in df_validation.columns:
            
            quality_routing_analysis = df_validation.groupby(['Address_Confidence', 'Routing_Channel']).size().unstack(fill_value=0)
            print("Address Quality × Routing Channel Matrix:")
            print(quality_routing_analysis)
            print()
            
            # Detailed breakdown by quality level
            for quality in ['ULTRA_HIGH', 'HIGH', 'MEDIUM', 'LOW']:
                quality_addresses = df_validation[df_validation['Address_Confidence'] == quality]
                if len(quality_addresses) > 0:
                    print(f"{quality} Quality Addresses ({len(quality_addresses)} total):")
                    
                    # Show routing breakdown
                    routing_dist = quality_addresses['Routing_Channel'].value_counts()
                    for route, count in routing_dist.items():
                        print(f"  {route}: {count} addresses")
                    
                    # Show sample addresses (first 3)
                    print("  Sample addresses:")
                    for i, (_, row) in enumerate(quality_addresses.head(3).iterrows()):
                        comune = row.get('comune_input', 'Unknown')
                        owner = f"{row.get('cognome', '')} {row.get('nome', '')}".strip()
                        address = row.get('cleaned_ubicazione', row.get('ubicazione', 'No address'))
                        routing = row.get('Routing_Channel', 'Unknown')
                        print(f"    {i+1}. {owner} in {comune} → {routing}")
                        print(f"       Address: {address}")
                    
                    if len(quality_addresses) > 3:
                        print(f"    ... and {len(quality_addresses) - 3} more {quality} addresses")
                    print()
        
        print("📤 FINAL MAILING LIST ANALYSIS:")
        print("-" * 50)
        
        print(f"Final Mailing Entries: {len(df_final)}")
        print("Final mailing details:")
        
        if len(df_final) > 0:
            for i, (_, row) in enumerate(df_final.iterrows()):
                municipality = row.get('Municipality', 'Unknown')
                foglio = row.get('Foglio', 'Unknown')
                particella = row.get('Particella', 'Unknown')
                owner = row.get('Full_Name', 'Unknown')
                address = row.get('Mailing_Address', 'Unknown')
                
                print(f"  {i+1}. {municipality} - Foglio {foglio}, Particella {particella}")
                print(f"     Owner: {owner}")
                print(f"     Address: {address}")
                print()
        
        print("🔍 MAILING LIST SELECTION CRITERIA ANALYSIS:")
        print("-" * 50)
        
        # Try to understand what criteria were used for final selection
        if len(df_final) > 0 and len(df_validation) > 0:
            
            print("Attempting to trace final mailing selection criteria...")
            
            # Check if final list corresponds to specific quality levels
            ultra_high_count = len(df_validation[df_validation['Address_Confidence'] == 'ULTRA_HIGH'])
            high_count = len(df_validation[df_validation['Address_Confidence'] == 'HIGH'])
            
            print(f"ULTRA_HIGH addresses: {ultra_high_count}")
            print(f"HIGH addresses: {high_count}")
            print(f"ULTRA_HIGH + HIGH: {ultra_high_count + high_count}")
            print(f"Final mailings: {len(df_final)}")
            
            if len(df_final) == ultra_high_count:
                print("✅ HYPOTHESIS: Final list = ULTRA_HIGH quality addresses only")
            elif len(df_final) == ultra_high_count + high_count:
                print("✅ HYPOTHESIS: Final list = ULTRA_HIGH + HIGH quality addresses")
            else:
                print("❓ HYPOTHESIS: Final list uses different selection criteria")
            
            # Check municipality distribution
            print(f"\nMunicipality distribution analysis:")
            val_by_muni = df_validation['comune_input'].value_counts()
            print("Validation Ready by municipality:")
            for muni, count in val_by_muni.items():
                print(f"  {muni}: {count} addresses")
            
            if 'Municipality' in df_final.columns:
                final_by_muni = df_final['Municipality'].value_counts()
                print("Final mailings by municipality:")
                for muni, count in final_by_muni.items():
                    print(f"  {muni}: {count} mailings")
        
        print()
        
        print("❓ MISSING PROCESS DOCUMENTATION:")
        print("-" * 50)
        
        # Calculate what's not addressed
        medium_addresses = len(df_validation[df_validation['Address_Confidence'] == 'MEDIUM'])
        low_addresses = len(df_validation[df_validation['Address_Confidence'] == 'LOW'])
        
        direct_mail_medium = len(df_validation[
            (df_validation['Address_Confidence'] == 'MEDIUM') & 
            (df_validation['Routing_Channel'] == 'DIRECT_MAIL')
        ])
        agency_medium = len(df_validation[
            (df_validation['Address_Confidence'] == 'MEDIUM') & 
            (df_validation['Routing_Channel'] == 'AGENCY')
        ])
        
        direct_mail_low = len(df_validation[
            (df_validation['Address_Confidence'] == 'LOW') & 
            (df_validation['Routing_Channel'] == 'DIRECT_MAIL')
        ])
        agency_low = len(df_validation[
            (df_validation['Address_Confidence'] == 'LOW') & 
            (df_validation['Routing_Channel'] == 'AGENCY')
        ])
        
        print(f"MEDIUM Quality Addresses ({medium_addresses} total):")
        print(f"  → DIRECT_MAIL: {direct_mail_medium} addresses")
        print(f"  → AGENCY: {agency_medium} addresses")
        print(f"  ❓ Business Process: What happens to these addresses?")
        print()
        
        print(f"LOW Quality Addresses ({low_addresses} total):")
        print(f"  → DIRECT_MAIL: {direct_mail_low} addresses")
        print(f"  → AGENCY: {agency_low} addresses")
        print(f"  ❓ Business Process: What happens to these addresses?")
        print()
        
        total_unaddressed = medium_addresses + low_addresses
        percentage_unaddressed = (total_unaddressed / total_addresses) * 100
        
        print("📋 PROCESS GAP SUMMARY:")
        print("-" * 30)
        print(f"Addresses in final mailing: {len(df_final)}")
        print(f"Addresses with unclear process: {total_unaddressed} ({percentage_unaddressed:.1f}%)")
        print()
        print("❓ BUSINESS QUESTIONS REQUIRING CLARIFICATION:")
        print("1. Are MEDIUM quality DIRECT_MAIL addresses sent in a separate batch?")
        print("2. Are MEDIUM quality AGENCY addresses investigated before mailing?")
        print("3. Are LOW quality addresses discarded or processed differently?")
        print("4. Is there a manual review process for non-ULTRA_HIGH addresses?")
        print("5. Should there be separate mailing lists for different quality levels?")
        
        print()
        
        print("💡 RECOMMENDED PROCESS IMPROVEMENTS:")
        print("-" * 40)
        print("1. **Document MEDIUM Quality Process**:")
        print("   - Create clear workflow for 13 MEDIUM addresses")
        print("   - Define manual review criteria and timeline")
        print("   - Specify when MEDIUM addresses get promoted to mailing")
        print()
        print("2. **Document LOW Quality Process**:")
        print("   - Define agency investigation workflow for 5 LOW addresses")
        print("   - Set timeline for address verification")
        print("   - Create feedback loop for address improvement")
        print()
        print("3. **Create Tiered Mailing Strategy**:")
        print("   - Immediate mailing: ULTRA_HIGH addresses")
        print("   - Quick review batch: HIGH + reviewed MEDIUM addresses")
        print("   - Investigation batch: AGENCY addresses after verification")
        print()
        print("4. **Add Process Tracking**:")
        print("   - Track status of MEDIUM/LOW addresses through review")
        print("   - Report on review completion rates")
        print("   - Measure address quality improvement over time")
        
    except Exception as e:
        print(f"❌ Error analyzing mailing list logic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Path to your test campaign file
    campaign_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_1807\LandAcquisition_Casalpusterlengo_Castiglione_20250703_1807_Results.xlsx"
    
    print("🚀 Starting Mailing List Logic Analysis...")
    print()
    
    analyze_mailing_list_generation(campaign_file)
    
    print()
    print("="*80)
    print("MAILING LIST ANALYSIS COMPLETE")
    print("Focus: Understanding what happens to MEDIUM and LOW quality addresses")
    print("="*80)