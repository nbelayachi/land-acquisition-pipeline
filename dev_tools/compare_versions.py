"""
Compare v3.0.0 vs Previous Version Results
Side-by-side comparison to highlight improvements
"""

import pandas as pd

def compare_campaign_versions():
    """Compare the new v3.0.0 results with previous version"""
    
    # New v3.0.0 results
    new_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2056\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2056_Results.xlsx"
    
    # Previous version results  
    old_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2018\LandAcquisition_Casalpusterlengo_Castiglione_20250701_2018_Results.xlsx"
    
    print("🔄 COMPARING CAMPAIGN VERSIONS")
    print("=" * 50)
    print(f"📊 Old version: {old_file.split('\\')[-1]}")
    print(f"🆕 New version: {new_file.split('\\')[-1]}")
    print()
    
    try:
        # Compare sheet structures
        old_excel = pd.ExcelFile(old_file)
        new_excel = pd.ExcelFile(new_file)
        
        print("📋 SHEET COMPARISON")
        print("-" * 30)
        print(f"Old sheets ({len(old_excel.sheet_names)}): {old_excel.sheet_names}")
        print(f"New sheets ({len(new_excel.sheet_names)}): {new_excel.sheet_names}")
        
        # Identify new sheets
        new_sheets = set(new_excel.sheet_names) - set(old_excel.sheet_names)
        if new_sheets:
            print(f"🆕 NEW SHEETS: {list(new_sheets)}")
        print()
        
        # Compare validation ready data
        if 'All_Validation_Ready' in both_files(old_excel, new_excel):
            old_val = pd.read_excel(old_file, sheet_name='All_Validation_Ready')
            new_val = pd.read_excel(new_file, sheet_name='All_Validation_Ready')
            
            print("📊 VALIDATION READY COMPARISON")
            print("-" * 35)
            print(f"Addresses processed: Old={len(old_val)}, New={len(new_val)}")
            
            # Compare confidence distributions
            if 'Address_Confidence' in old_val.columns and 'Address_Confidence' in new_val.columns:
                old_conf = old_val['Address_Confidence'].value_counts()
                new_conf = new_val['Address_Confidence'].value_counts()
                
                print(f"\nConfidence Distribution Comparison:")
                print(f"{'Level':<12} {'Old Count':<10} {'New Count':<10} {'Change'}")
                print("-" * 45)
                
                all_levels = set(old_conf.index) | set(new_conf.index)
                for level in sorted(all_levels):
                    old_count = old_conf.get(level, 0)
                    new_count = new_conf.get(level, 0)
                    change = new_count - old_count
                    change_str = f"+{change}" if change > 0 else str(change) if change < 0 else "0"
                    print(f"{level:<12} {old_count:<10} {new_count:<10} {change_str}")
                
                # Highlight ULTRA_HIGH if present
                if 'ULTRA_HIGH' in new_conf.index:
                    ultra_high_count = new_conf['ULTRA_HIGH']
                    print(f"\n🚀 NEW FEATURE: {ultra_high_count} ULTRA_HIGH confidence addresses!")
            
            # Compare column structures
            old_cols = set(old_val.columns)
            new_cols = set(new_val.columns)
            added_cols = new_cols - old_cols
            removed_cols = old_cols - new_cols
            
            if added_cols:
                print(f"\n🆕 NEW COLUMNS: {list(added_cols)}")
            if removed_cols:
                print(f"❌ REMOVED COLUMNS: {list(removed_cols)}")
        
        # Analyze Strategic_Mailing_List if present
        if 'Strategic_Mailing_List' in new_excel.sheet_names:
            strategic_df = pd.read_excel(new_file, sheet_name='Strategic_Mailing_List')
            print(f"\n🎯 NEW STRATEGIC MAILING LIST")
            print("-" * 30)
            print(f"Rows: {len(strategic_df)}")
            print(f"Purpose: Grouped mailing addresses by parcel")
            
            if len(strategic_df) > 0:
                print("Sample entries:")
                for idx, row in strategic_df.head(2).iterrows():
                    municipality = row.get('Municipality', 'N/A')
                    name = row.get('Full_Name', 'N/A')
                    address = row.get('Mailing_Address', 'N/A')
                    print(f"  {municipality} | {name} | {address[:40]}...")
        
        # Calculate performance improvements
        print(f"\n📈 PERFORMANCE ANALYSIS")
        print("-" * 25)
        
        if 'Address_Confidence' in new_val.columns:
            ultra_high = len(new_val[new_val['Address_Confidence'] == 'ULTRA_HIGH'])
            high = len(new_val[new_val['Address_Confidence'] == 'HIGH'])
            total = len(new_val)
            
            immediate_ready = ultra_high
            quick_review = high
            
            print(f"Immediate print-ready: {immediate_ready}/{total} ({immediate_ready/total*100:.1f}%)")
            print(f"Quick review needed: {quick_review}/{total} ({quick_review/total*100:.1f}%)")
            
            # Time savings calculation
            old_time = total * 8  # 8 minutes per address
            new_time = (immediate_ready * 0) + (quick_review * 5) + ((total - immediate_ready - quick_review) * 8)
            savings = old_time - new_time
            
            print(f"Time savings: {savings} minutes ({savings/60:.1f} hours)")
            print(f"Efficiency improvement: {savings/old_time*100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in comparison: {str(e)}")
        return False

def both_files(excel1, excel2):
    """Return sheets present in both files"""
    return set(excel1.sheet_names) & set(excel2.sheet_names)

if __name__ == "__main__":
    print("🔍 Starting version comparison...")
    success = compare_campaign_versions()
    if success:
        print(f"\n✅ Comparison complete!")
    else:
        print(f"\n❌ Comparison failed")