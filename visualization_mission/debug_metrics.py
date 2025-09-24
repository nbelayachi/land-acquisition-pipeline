#!/usr/bin/env python3
"""
Debug Campaign4 Metrics
Analyze and fix KPI calculation issues
"""

import pandas as pd
import os

def debug_metrics():
    print("🔍 DEBUGGING CAMPAIGN4 METRICS")
    print("=" * 50)
    
    excel_path = "data/Campaign4_Results.xlsx"
    
    if not os.path.exists(excel_path):
        print(f"❌ File not found: {excel_path}")
        return
    
    try:
        # Load data
        data = {
            'Campaign_Summary': pd.read_excel(excel_path, sheet_name='Campaign_Summary'),
            'Enhanced_Funnel_Analysis': pd.read_excel(excel_path, sheet_name='Enhanced_Funnel_Analysis'),
            'Address_Quality_Distribution': pd.read_excel(excel_path, sheet_name='Address_Quality_Distribution'),
            'All_Validation_Ready': pd.read_excel(excel_path, sheet_name='All_Validation_Ready')
        }
        
        # Clean Campaign_Summary
        cs = data['Campaign_Summary']
        clean_rows = cs['comune'].notna() & (cs['comune'] != '')
        cs_clean = cs[clean_rows].reset_index(drop=True)
        
        print(f"📊 Campaign_Summary cleaned: {len(cs_clean)} rows")
        print(f"📊 All_Validation_Ready: {len(data['All_Validation_Ready'])} rows")
        
        # Debug key calculations
        print("\n🔍 KEY METRICS CALCULATION:")
        
        total_addresses = len(data['All_Validation_Ready'])
        print(f"   Total Addresses: {total_addresses}")
        
        direct_mail_values = cs_clean['Direct_Mail_Final_Contacts']
        print(f"   Direct Mail values: {direct_mail_values.tolist()}")
        print(f"   Direct Mail sum: {direct_mail_values.sum()}")
        print(f"   Direct Mail data type: {direct_mail_values.dtype}")
        
        agency_values = cs_clean['Agency_Final_Contacts']
        print(f"   Agency values: {agency_values.tolist()}")
        print(f"   Agency sum: {agency_values.sum()}")
        print(f"   Agency data type: {agency_values.dtype}")
        
        area_values = cs_clean['Input_Area_Ha']
        print(f"   Area values: {area_values.tolist()}")
        print(f"   Area sum: {area_values.sum()}")
        print(f"   Area data type: {area_values.dtype}")
        
        # Calculate percentages
        direct_mail_total = direct_mail_values.sum()
        agency_total = agency_values.sum()
        
        if total_addresses > 0:
            efficiency = (direct_mail_total / total_addresses) * 100
            automation_rate = ((total_addresses - agency_total) / total_addresses) * 100
            print(f"   Efficiency: {efficiency:.1f}%")
            print(f"   Automation Rate: {automation_rate:.1f}%")
        
        # Check for data quality issues
        print("\n🔍 DATA QUALITY CHECKS:")
        print(f"   Direct Mail + Agency = {direct_mail_total + agency_total}")
        print(f"   Expected total: {total_addresses}")
        print(f"   Difference: {total_addresses - (direct_mail_total + agency_total)}")
        
        # Check Enhanced_Funnel_Analysis
        funnel_data = data['Enhanced_Funnel_Analysis']
        print(f"\n📊 Enhanced_Funnel_Analysis: {len(funnel_data)} rows")
        if not funnel_data.empty:
            print(f"   Funnel types: {funnel_data['Funnel_Type'].unique()}")
            print(f"   Contact processing stages: {funnel_data[funnel_data['Funnel_Type'] == 'Contact Processing']['Stage'].tolist()}")
        
        # Check Address_Quality_Distribution
        quality_data = data['Address_Quality_Distribution']
        print(f"\n📊 Address_Quality_Distribution: {len(quality_data)} rows")
        if not quality_data.empty:
            print(f"   Quality levels: {quality_data['Quality_Level'].tolist()}")
            print(f"   Counts: {quality_data['Count'].tolist()}")
            print(f"   Total quality addresses: {quality_data['Count'].sum()}")
        
        return data, cs_clean
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_metrics()