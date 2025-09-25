# -*- coding: utf-8 -*-
"""
Land Acquisition Campaign Launcher v3.1.8
Streamlined interface for renewable energy land acquisition campaigns
Supports enhanced funnel analytics, address quality intelligence, and executive KPIs

@version: 3.1.8 (Metric alignment + Business Intelligence + Cost Tracking)
@updated: July 2025
"""

import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

class LandAcquisitionCampaignLauncher:
    def __init__(self):
        self.version = "3.1.8"
        self.load_config()
        
    def load_config(self):
        """Load configuration file"""
        try:
            with open('land_acquisition_config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print("❌ Configuration file not found. Please ensure land_acquisition_config.json exists.")
            exit(1)
    
    def get_start_balance(self):
        """Get starting API balance for cost tracking"""
        print(f"\n💰 COST TRACKING - API BALANCE CHECK")
        print("Before processing, please check your current API balance:")
        print("1. Go to https://catasto.openapi.it/dashboard")
        print("2. Check your current account balance")
        print()
        
        while True:
            try:
                balance = float(input("Enter your current balance (€): "))
                if balance >= 0:
                    return balance
                else:
                    print("❌ Balance cannot be negative. Please enter a valid amount.")
            except ValueError:
                print("❌ Please enter a valid number (e.g., 45.50)")
    
    def show_welcome(self):
        """Display streamlined welcome screen"""
        print("\n" + "="*70)
        print(f"🏠 LAND ACQUISITION CAMPAIGN LAUNCHER v{self.version}")
        print("Renewable Energy Land Registry Processing Pipeline")
        print("="*70)
        print()
        print("📋 WHAT THIS DOES:")
        print("• Processes Italian land registry data for property owner identification")
        print("• Generates comprehensive business intelligence and executive KPIs")
        print("• Creates single consolidated Excel file with 10 enhanced sheets")
        print("• Provides 4-tier address quality classification and routing")
        print("• Exports PowerBI-ready dataset for dashboard integration")
        print()
        
        # Check configuration status
        api_configured = bool(self.config.get('api_settings', {}).get('token'))
        geocoding_enabled = self.config.get('geocoding_settings', {}).get('enabled', False)
        enhanced_funnel = self.config.get('enhanced_funnel_analysis', {}).get('enabled', True)
        powerbi_export = self.config.get('powerbi_integration', {}).get('enabled', True)
        
        print("🔧 CONFIGURATION STATUS:")
        print(f"   • API Integration: {'✅ READY' if api_configured else '❌ NEEDS SETUP'}")
        print(f"   • Address Enhancement: {'✅ ENABLED' if geocoding_enabled else '⚠️ DISABLED'}")
        print(f"   • Enhanced Funnel Analytics: {'✅ ENABLED' if enhanced_funnel else '❌ DISABLED'}")
        print(f"   • PowerBI Export: {'✅ ENABLED' if powerbi_export else '❌ DISABLED'}")
        print()
        
        print("🆕 CURRENT FEATURES (v3.1.8):")
        print("   • Enhanced Final_Mailing_List with owner grouping and sequence numbers")
        print("   • Refined address classification for better confidence levels")
        print("   • Business-friendly funnel metrics with executive KPIs")
        print("   • Corrected Direct_Mail/Agency contact metrics aligned with dashboard outputs")
        print("   • Comprehensive metrics documentation and validation")
        print("   • Zero-touch processing identification (17.4% automation)")
        print("   • Integrated cost tracking with start/end balance prompts")
        print()
    
    def get_input_file(self):
        """Streamlined input file selection"""
        print("📁 INPUT FILE SELECTION")
        print("-" * 30)
        
        # Look for Excel files in common locations
        search_locations = ['.', 'input', os.path.expanduser('~/Downloads'), os.path.expanduser('~/Desktop')]
        excel_files = []
        
        for location in search_locations:
            if os.path.exists(location):
                files = [f for f in os.listdir(location) if f.endswith('.xlsx') and not f.startswith('~')]
                excel_files.extend([(os.path.join(location, f), f) for f in files])
        
        if excel_files:
            print("Available files:")
            for i, (full_path, filename) in enumerate(excel_files[:10], 1):  # Limit to 10 files
                size_kb = os.path.getsize(full_path) / 1024
                print(f"   {i}. {filename} ({size_kb:.1f} KB)")
            
            while True:
                try:
                    choice = input(f"\nSelect file (1-{min(len(excel_files), 10)}) or enter custom path: ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= min(len(excel_files), 10):
                        return excel_files[int(choice)-1][0]
                    elif os.path.exists(choice) and choice.endswith('.xlsx'):
                        return choice
                    else:
                        print("❌ Invalid selection. Please try again.")
                except KeyboardInterrupt:
                    exit(0)
        else:
            file_path = input("Enter path to input Excel file: ").strip().strip('"')
            if os.path.exists(file_path) and file_path.endswith('.xlsx'):
                return file_path
            else:
                print("❌ File not found. Please check the path.")
                return self.get_input_file()
    
    def analyze_input_file(self, file_path):
        """Quick input file analysis"""
        try:
            df = pd.read_excel(file_path)
            
            # Validate required columns
            required_cols = ['tipo_catasto', 'CP', 'provincia', 'comune', 'foglio', 'particella', 'Area']
            missing = [col for col in required_cols if col not in df.columns]
            
            if missing:
                print(f"❌ Missing columns: {missing}")
                return None
            
            # Basic analysis
            analysis = {
                'total_parcels': len(df),
                'total_municipalities': df['comune'].nunique(),
                'total_area_ha': df['Area'].sum(),
                'has_sezione': bool('Sezione' in df.columns and df['Sezione'].notna().sum() > 0),
                'main_municipalities': df['comune'].value_counts().head(3).to_dict(),
                'dataframe': df
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error reading file: {str(e)}")
            return None
    
    def display_analysis(self, analysis):
        """Show concise analysis summary"""
        print(f"\n📊 INPUT ANALYSIS")
        print("-" * 25)
        print(f"Total Parcels: {analysis['total_parcels']:,}")
        print(f"Municipalities: {analysis['total_municipalities']}")
        print(f"Total Area: {analysis['total_area_ha']:.1f} hectares")
        
        if analysis['has_sezione']:
            print("✅ Sezione data detected")
        
        print(f"\nTop municipalities:")
        for comune, count in analysis['main_municipalities'].items():
            print(f"   • {comune}: {count} parcels")
        print()
    
    def generate_campaign_name(self, analysis):
        """Generate campaign name"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        main_comune = list(analysis['main_municipalities'].keys())[0].replace(' ', '_')
        return f"LandAcquisition_{main_comune}_{timestamp}"
    
    def show_expected_outputs(self):
        """Show what will be generated"""
        print("📄 EXPECTED OUTPUTS:")
        print("   • Single Excel file with 10 enhanced sheets:")
        print("     - Final_Mailing_List (enhanced with owner grouping)")
        print("     - Enhanced_Funnel_Analysis (executive KPIs)")
        print("     - Address_Quality_Distribution (4-tier classification)")
        print("     - All_Validation_Ready (complete contact data)")
        print("     - Campaign_Summary (business metrics)")
        print("     - And 5 additional analysis sheets")
        print("   • PowerBI_Dataset.csv (dashboard export)")
        print("   • Enhanced_Cost_Summary.txt (cost breakdown)")
        print()
    
    def get_confirmation(self, campaign_name, analysis):
        """Get final launch confirmation"""
        print(f"🚀 CAMPAIGN CONFIRMATION")
        print("="*40)
        print(f"Campaign: {campaign_name}")
        print(f"Parcels: {analysis['total_parcels']:,} | Area: {analysis['total_area_ha']:.1f} ha")
        print(f"Municipalities: {analysis['total_municipalities']}")
        
        print(f"\nProcessing will:")
        print(f"   1. Query Italian Land Registry API for ownership data")
        print(f"   2. Apply Category A filter for residential properties")
        print(f"   3. Generate 4-tier address quality classification")
        print(f"   4. Create enhanced funnel analysis with business KPIs")
        print(f"   5. Export single consolidated Excel + PowerBI dataset")
        print()
        
        while True:
            confirm = input("Launch campaign? (y/n): ").lower().strip()
            if confirm in ['y', 'yes']:
                return True
            elif confirm in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    def create_campaign_config(self, input_file, campaign_name, analysis):
        """Create streamlined campaign configuration"""
        config = {
            "campaign_name": campaign_name,
            "input_file": input_file,
            "created_date": datetime.now().isoformat(),
            "version": self.version,
            "analysis": {
                "total_parcels": analysis['total_parcels'],
                "total_municipalities": analysis['total_municipalities'], 
                "total_area_ha": round(analysis['total_area_ha'], 2),
                "has_sezione": analysis['has_sezione']
            },
            "features_enabled": {
                "enhanced_funnel_analysis": self.config.get('enhanced_funnel_analysis', {}).get('enabled', True),
                "powerbi_integration": self.config.get('powerbi_integration', {}).get('enabled', True),
                "geocoding_enhancement": self.config.get('geocoding_settings', {}).get('enabled', False),
                "address_quality_classification": True,
                "final_mailing_list_enhancement": True
            }
        }
        
        # Save configuration
        os.makedirs("campaigns", exist_ok=True)
        config_file = f"campaigns/{campaign_name}_config.json"
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config_file
    
    def show_next_steps(self, campaign_name, config_file, start_balance):
        """Show how to execute the campaign"""
        print(f"\n✅ Campaign '{campaign_name}' configured successfully!")
        print(f"📁 Configuration saved: {config_file}")
        print()
        print("🚀 TO EXECUTE CAMPAIGN:")
        print(f"   python land_acquisition_pipeline.py --config {config_file} --start-balance {start_balance}")
        print()
        print("⏱️  EXPECTED PROCESSING TIME:")
        print("   • ~2 minutes per municipality")
        print("   • Progress will be shown in real-time")
        print("   • Results saved to completed_campaigns/ folder")
        print()
        print("📊 AFTER COMPLETION:")
        print("   • Review the single consolidated Excel file")
        print("   • Import PowerBI_Dataset.csv to dashboards")
        print("   • Use Final_Mailing_List for team communications")
        print("   • Check Enhanced_Cost_Summary.txt for campaign costs")
        print("   • You'll be prompted for end balance to calculate costs")
        print()
    
    def run(self):
        """Main launcher workflow"""
        try:
            # Welcome and start balance
            self.show_welcome()
            start_balance = self.get_start_balance()
            
            # Input file selection and analysis
            input_file = self.get_input_file()
            analysis = self.analyze_input_file(input_file)
            if not analysis:
                return
            
            self.display_analysis(analysis)
            campaign_name = self.generate_campaign_name(analysis)
            
            # Show outputs and get confirmation
            self.show_expected_outputs()
            if not self.get_confirmation(campaign_name, analysis):
                print("❌ Campaign cancelled.")
                return
            
            # Create configuration and show next steps
            config_file = self.create_campaign_config(input_file, campaign_name, analysis)
            self.show_next_steps(campaign_name, config_file, start_balance)
            
        except KeyboardInterrupt:
            print("\n\n❌ Campaign launcher cancelled.")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please check your configuration and input file.")

def main():
    """Entry point"""
    launcher = LandAcquisitionCampaignLauncher()
    launcher.run()

if __name__ == "__main__":
    main()