#!/usr/bin/env python3
"""
Campaign Output Analyzer - v2.9.5 Structure Verification
Analyzes the consolidated Excel output to verify structure and content.
Exports results to a text file for easy sharing.
"""

import pandas as pd
import os
from datetime import datetime
from pathlib import Path

class CampaignAnalyzer:
    def __init__(self, output_file=None):
        self.output_file = output_file
        if self.output_file:
            self.f = open(self.output_file, 'w', encoding='utf-8')
    
    def output(self, text=""):
        """Output to both file and console."""
        print(text)  # Always show on console
        if self.output_file:
            print(text, file=self.f)
    
    def close(self):
        """Close output file if opened."""
        if self.output_file:
            self.f.close()
    
    def analyze_campaign_file(self, file_path):
        """Comprehensive analysis of campaign Excel file structure and content."""
        self.output("="*80)
        self.output("LAND ACQUISITION PIPELINE - CAMPAIGN OUTPUT ANALYZER")
        self.output("="*80)
        self.output(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.output(f"Analyzing file: {file_path}")
        self.output()
        
        if not os.path.exists(file_path):
            self.output("❌ ERROR: File not found!")
            self.output("Please provide the correct path to your campaign results file.")
            return
        
        try:
            # Get file info
            file_size = os.path.getsize(file_path) / (1024*1024)  # MB
            self.output(f"📁 File Size: {file_size:.2f} MB")
            self.output()
            
            # Load Excel file and get sheet names
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            self.output("📋 SHEET STRUCTURE ANALYSIS")
            self.output("="*50)
            self.output(f"Total Sheets: {len(sheet_names)}")
            
            expected_sheets = [
                "All_Raw_Data",
                "All_Validation_Ready", 
                "All_Companies_Found",
                "Campaign_Summary",
                "Funnel_Analysis"
            ]
            
            # Check for expected sheets
            self.output("\n✅ Expected Sheets Status:")
            for expected_sheet in expected_sheets:
                status = "✅ FOUND" if expected_sheet in sheet_names else "❌ MISSING"
                self.output(f"  {expected_sheet}: {status}")
            
            # Check for unexpected sheets
            unexpected_sheets = [sheet for sheet in sheet_names if sheet not in expected_sheets]
            if unexpected_sheets:
                self.output(f"\n⚠️  Unexpected Sheets Found: {unexpected_sheets}")
            
            self.output("\n" + "="*50)
            self.output("DETAILED SHEET ANALYSIS")
            self.output("="*50)
            
            # Analyze each sheet
            for i, sheet_name in enumerate(sheet_names, 1):
                self.output(f"\n{i}. SHEET: '{sheet_name}'")
                self.output("-" * (len(sheet_name) + 12))
                
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    # Basic info
                    self.output(f"   Rows: {len(df)}")
                    self.output(f"   Columns: {len(df.columns)}")
                    
                    # Show column names
                    self.output(f"   Column Names:")
                    for j, col in enumerate(df.columns, 1):
                        self.output(f"     {j:2d}. {col}")
                    
                    # Check for key traceability columns
                    key_columns = ['CP', 'comune', 'provincia']
                    present_key_cols = [col for col in key_columns if col in df.columns]
                    missing_key_cols = [col for col in key_columns if col not in df.columns]
                    
                    if present_key_cols:
                        self.output(f"   ✅ Key Columns Present: {present_key_cols}")
                    if missing_key_cols:
                        self.output(f"   ⚠️  Key Columns Missing: {missing_key_cols}")
                    
                    # Show unique values for traceability columns if present
                    if 'CP' in df.columns:
                        unique_cps = df['CP'].nunique() if not df['CP'].isna().all() else 0
                        self.output(f"   🏗️  Unique CPs: {unique_cps}")
                        if unique_cps > 0 and unique_cps <= 10:
                            self.output(f"   CP Values: {sorted(df['CP'].dropna().unique())}")
                    
                    if 'comune' in df.columns:
                        unique_comuni = df['comune'].nunique() if not df['comune'].isna().all() else 0
                        self.output(f"   🏛️  Unique Municipalities: {unique_comuni}")
                        if unique_comuni > 0 and unique_comuni <= 10:
                            self.output(f"   Municipality Values: {sorted(df['comune'].dropna().unique())}")
                    
                    # Sheet-specific analysis
                    if sheet_name == "All_Validation_Ready":
                        self.analyze_validation_ready_sheet(df)
                    elif sheet_name == "All_Companies_Found":
                        self.analyze_companies_sheet(df)
                    elif sheet_name == "Campaign_Summary":
                        self.analyze_campaign_summary_sheet(df)
                    elif sheet_name == "Funnel_Analysis":
                        self.analyze_funnel_sheet(df)
                    elif sheet_name == "All_Raw_Data":
                        self.analyze_raw_data_sheet(df)
                    
                    # Show first few rows (sample data) - limited to prevent huge output
                    if len(df) > 0:
                        self.output(f"\n   📋 SAMPLE DATA (First 2 rows, key columns only):")
                        
                        # Select key columns to show
                        key_cols_to_show = []
                        priority_cols = ['CP', 'comune', 'provincia', 'Address_Confidence', 'Routing_Channel', 
                                       'Direct_Mail_Final_Contacts', 'Agency_Final_Contacts']
                        
                        for col in priority_cols:
                            if col in df.columns:
                                key_cols_to_show.append(col)
                        
                        # If no priority columns, show first 5 columns
                        if not key_cols_to_show:
                            key_cols_to_show = df.columns[:5].tolist()
                        
                        sample_df = df[key_cols_to_show].head(2)
                        for idx, row in sample_df.iterrows():
                            self.output(f"     Row {idx + 1}:")
                            for col_name, value in row.items():
                                # Truncate long values
                                str_value = str(value)
                                if len(str_value) > 50:
                                    str_value = str_value[:47] + "..."
                                self.output(f"       {col_name}: {str_value}")
                            self.output()
                    
                except Exception as e:
                    self.output(f"   ❌ ERROR reading sheet: {str(e)}")
            
            self.output("\n" + "="*80)
            self.output("ANALYSIS COMPLETE")
            self.output("="*80)
            
        except Exception as e:
            self.output(f"❌ ERROR analyzing file: {str(e)}")
    
    def analyze_validation_ready_sheet(self, df):
        """Specific analysis for All_Validation_Ready sheet."""
        self.output(f"   📧 VALIDATION READY ANALYSIS:")
        
        # Check for required columns
        required_cols = ['Address_Confidence', 'Routing_Channel', 'foglio_input', 'particella_input']
        present_req_cols = [col for col in required_cols if col in df.columns]
        missing_req_cols = [col for col in required_cols if col not in df.columns]
        
        if present_req_cols:
            self.output(f"      ✅ Required Columns Present: {present_req_cols}")
        if missing_req_cols:
            self.output(f"      ⚠️  Required Columns Missing: {missing_req_cols}")
        
        # Analyze routing channels
        if 'Routing_Channel' in df.columns:
            routing_counts = df['Routing_Channel'].value_counts()
            self.output(f"      📬 Routing Channel Distribution:")
            for channel, count in routing_counts.items():
                self.output(f"         {channel}: {count}")
        
        # Analyze address confidence
        if 'Address_Confidence' in df.columns:
            confidence_counts = df['Address_Confidence'].value_counts()
            self.output(f"      🎯 Address Confidence Distribution:")
            for confidence, count in confidence_counts.items():
                self.output(f"         {confidence}: {count}")
    
    def analyze_companies_sheet(self, df):
        """Specific analysis for All_Companies_Found sheet."""
        self.output(f"   🏢 COMPANIES ANALYSIS:")
        
        # Check for PEC column
        pec_columns = [col for col in df.columns if 'pec' in col.lower() or 'email' in col.lower()]
        if pec_columns:
            self.output(f"      📧 PEC/Email Columns Found: {pec_columns}")
            for pec_col in pec_columns:
                non_empty_pecs = df[pec_col].notna().sum()
                self.output(f"         {pec_col}: {non_empty_pecs} non-empty values")
        else:
            self.output(f"      ⚠️  No PEC/Email columns found")
    
    def analyze_campaign_summary_sheet(self, df):
        """Specific analysis for Campaign_Summary sheet."""
        self.output(f"   📊 CAMPAIGN SUMMARY ANALYSIS:")
        
        # Check for key metrics columns
        key_metrics = [
            'Direct_Mail_Final_Contacts', 'Agency_Final_Contacts',
            'Direct_Mail_Final_Area_Ha', 'Agency_Final_Area_Ha',
            'Unique_Owner_Address_Pairs'
        ]
        
        present_metrics = [col for col in key_metrics if col in df.columns]
        missing_metrics = [col for col in key_metrics if col not in df.columns]
        
        if present_metrics:
            self.output(f"      ✅ Key Metrics Present: {present_metrics}")
        if missing_metrics:
            self.output(f"      ⚠️  Key Metrics Missing: {missing_metrics}")
        
        # Show metric totals if available
        for metric in present_metrics:
            if df[metric].dtype in ['int64', 'float64']:
                total = df[metric].sum()
                self.output(f"         {metric} Total: {total}")
    
    def analyze_funnel_sheet(self, df):
        """Specific analysis for Funnel_Analysis sheet."""
        self.output(f"   🔄 FUNNEL ANALYSIS:")
        
        # Check for stage columns
        funnel_indicators = ['stage', 'parcels', 'hectares', 'area']
        funnel_cols = [col for col in df.columns if any(indicator in col.lower() for indicator in funnel_indicators)]
        
        if funnel_cols:
            self.output(f"      🎯 Funnel-related Columns: {funnel_cols}")
        else:
            self.output(f"      ⚠️  No clear funnel columns identified")
        
        # Check for municipality breakdown
        if 'comune' in df.columns:
            unique_comuni = df['comune'].nunique()
            self.output(f"      🏛️  Municipalities in Funnel: {unique_comuni}")
    
    def analyze_raw_data_sheet(self, df):
        """Specific analysis for All_Raw_Data sheet."""
        self.output(f"   📋 RAW DATA ANALYSIS:")
        
        # Check for owner type classification
        owner_indicators = ['tipo_proprietario', 'owner_type', 'privato', 'azienda']
        owner_cols = [col for col in df.columns if any(indicator in col.lower() for indicator in owner_indicators)]
        
        if owner_cols:
            self.output(f"      👥 Owner Classification Columns: {owner_cols}")
        else:
            self.output(f"      ⚠️  No clear owner classification columns")

def main():
    """Main function to run the analysis."""
    print("="*60)
    print("LAND ACQUISITION CAMPAIGN ANALYZER")
    print("="*60)
    print("This script will analyze your campaign Excel file structure")
    print("and export the results to a text file for easy sharing.")
    print()
    
    # Get file path
    print("Please provide the path to your campaign results Excel file.")
    print("Examples:")
    print("  - completed_campaigns/LandAcquisition_Campaign_20250630_1824/LandAcquisition_Campaign_20250630_1824_Results.xlsx")
    print("  - C:/path/to/your/campaign_results.xlsx")
    print()
    
    file_path = input("Enter the full path to your Excel file: ").strip()
    file_path = file_path.strip('"').strip("'")  # Remove quotes
    
    # Generate output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"campaign_analysis_{timestamp}.txt"
    
    print(f"\n🔍 Starting analysis...")
    print(f"📄 Results will be saved to: {output_filename}")
    print("="*60)
    
    # Run analysis
    analyzer = CampaignAnalyzer(output_filename)
    try:
        analyzer.analyze_campaign_file(file_path)
    finally:
        analyzer.close()
    
    print("="*60)
    print("✅ ANALYSIS COMPLETE!")
    print(f"📁 Full results saved to: {output_filename}")
    print("📋 You can now copy the contents of this file to share with your agent.")
    print("="*60)

if __name__ == "__main__":
    main()