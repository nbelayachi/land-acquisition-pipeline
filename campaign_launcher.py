# -*- coding: utf-8 -*-
"""
Enhanced Land Acquisition Campaign Launcher with Geocoding Support and Funnel Tracking
Clean interface for real estate campaigns with OneDrive integration and address enhancement

@author: Real Estate Pipeline Optimizer - Enhanced Edition
VERSION: 2.9 (with SNC reclassification and funnel metrics)
"""

import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

class EnhancedLandAcquisitionCampaignLauncher:
    def __init__(self):
        self.load_config()
        
    def load_config(self):
        """Load configuration file"""
        try:
            with open('land_acquisition_config.json', 'r') as f:
                config_data = json.load(f)
                self.config = config_data.get('land_acquisition_config', {})
        except FileNotFoundError:
            print("❌ Configuration file not found. Please run setup first.")
            exit(1)
    
    def check_geocoding_setup(self):
        """Check if geocoding is properly configured"""
        geocoding_config = self.config.get('geocoding_settings', {})
        geocoding_enabled = geocoding_config.get('enabled', False)
        geocoding_token = geocoding_config.get('token', '')
        
        if geocoding_enabled and geocoding_token and geocoding_token != "YOUR_GEOCODING_TOKEN_HERE":
            return True, "✅ ENABLED"
        elif geocoding_enabled and (not geocoding_token or geocoding_token == "YOUR_GEOCODING_TOKEN_HERE"):
            return False, "❌ MISSING TOKEN"
        else:
            return False, "❌ DISABLED"
    
    def show_welcome(self):
        """Display welcome screen with workflow context and geocoding info"""
        geocoding_enabled, geocoding_status = self.check_geocoding_setup()
        
        print("\n" + "="*80)
        print("🏗️ ENHANCED LAND ACQUISITION CAMPAIGN LAUNCHER v2.9")
        print("CP-Municipality Processing with OneDrive Team Sharing + Address Enhancement")
        print("="*80)
        print()
        print("📊 YOUR WORKFLOW:")
        print("Business Development → You (Process) → OneDrive → Team (Validate) → Mailing")
        print()
        print("💡 WHAT THIS DOES:")
        print("• Splits input by CP-Municipality automatically")
        print("• Processes each parcel through Italian Land Registry API")
        print("• Creates 'Validation_Ready' files for Land Acquisition Team")
        print("• Generates separate company files when companies are found")
        print("• Saves results to OneDrive for team access")
        print("• Exports Power BI data for dashboard analysis")
        print("• Tracks costs with manual balance method")
        print("• Supports Sezione field when provided")
        
        print("\n🆕 NEW IN v2.9:")
        print("• 📮 SNC addresses now go to DIRECT_MAIL (postal service knows them)")
        print("• 📊 Complete funnel tracking (parcels + hectares at each stage)")
        print("• 🏢 Separate company metrics while including in totals")
        print("• 📈 Enhanced Power BI dataset with funnel visibility")
        
        if geocoding_enabled:
            print("\n• 🗺️ ENHANCES ADDRESSES with ZIP codes and coordinates")
            print("• 📮 Creates postal-ready Italian formatted addresses")
            print("• 📍 Adds geographic data for mapping and analysis")
        else:
            print(f"\n• 🗺️ Address enhancement: {geocoding_status}")
            if "MISSING TOKEN" in geocoding_status:
                print("  ⚠️  Configure geocoding token to enable address enhancement")
        print()
    
    def show_geocoding_benefits(self):
        """Show benefits of geocoding enhancement"""
        geocoding_enabled, geocoding_status = self.check_geocoding_setup()
        
        if geocoding_enabled:
            print("🗺️ ADDRESS ENHANCEMENT BENEFITS:")
            print("• ZIP codes for direct mailing campaigns")
            print("• Properly formatted Italian postal addresses")
            print("• Geographic coordinates for mapping")
            print("• Province codes and administrative data")
            print("• Street name and number separation")
            print("• Enhanced data quality for validation team")
            print()
        else:
            print("🗺️ ADDRESS ENHANCEMENT:")
            print(f"   Status: {geocoding_status}")
            if "MISSING TOKEN" in geocoding_status:
                print("   To enable: Add your geocoding token to land_acquisition_config.json")
                print("   Get token at: https://geocoding.openapi.it/dashboard")
                print("   Benefits: ZIP codes, coordinates, formatted addresses")
            elif "DISABLED" in geocoding_status:
                print("   To enable: Set 'enabled': true in geocoding_settings")
            print()
    
    def get_manual_cost_input(self, timing="start"):
        """Get manual balance input from user"""
        if timing == "start":
            print(f"\n💰 COST TRACKING - START BALANCE")
            print("Please check your API balance before starting:")
            print("1. Go to https://catasto.openapi.it/dashboard")
            print("2. Check your current account balance")
            print()
            while True:
                try:
                    balance = float(input("Enter your current balance (€): "))
                    return balance
                except ValueError:
                    print("❌ Please enter a valid number (e.g., 45.50)")
        
        else:  # end
            print(f"\n💰 COST TRACKING - END BALANCE")
            print("Please check your API balance after processing:")
            print("1. Go to https://catasto.openapi.it/dashboard")
            print("2. Check your current account balance")
            print()
            while True:
                try:
                    balance = float(input("Enter your current balance (€): "))
                    return balance
                except ValueError:
                    print("❌ Please enter a valid number (e.g., 32.80)")
    
    def get_input_file(self):
        """Get input file from user with improved handling"""
        print("\n📁 Input File Selection:")
        print("-" * 30)
        
        # Look for Excel files in current directory and common locations
        input_search_dirs = [
            '.',
            'input',
            os.path.expanduser('~/Downloads'),
            os.path.expanduser('~/Desktop')
        ]
        
        excel_files = []
        for search_dir in input_search_dirs:
            if os.path.exists(search_dir):
                files = [f for f in os.listdir(search_dir) if f.endswith('.xlsx') and not f.startswith('~')]
                excel_files.extend([(os.path.join(search_dir, f), f) for f in files])
        
        if excel_files:
            print("Available input files:")
            for i, (full_path, filename) in enumerate(excel_files, 1):
                file_size = os.path.getsize(full_path) / 1024  # KB
                print(f"{i}. {filename} ({file_size:.1f} KB)")
            
            while True:
                try:
                    choice = int(input("\nSelect input file (number) or 0 to enter path manually: "))
                    if choice == 0:
                        break
                    elif 1 <= choice <= len(excel_files):
                        return excel_files[choice-1][0]
                    else:
                        print("❌ Invalid choice. Please try again.")
                except ValueError:
                    print("❌ Please enter a valid number.")
        
        # Manual file path entry
        file_path = input("\nEnter full path to input Excel file: ").strip().strip('"')
        
        if os.path.exists(file_path) and file_path.endswith('.xlsx'):
            return file_path
        else:
            print("❌ File not found or not an Excel file.")
            return self.get_input_file()
    
    def analyze_input_file(self, file_path):
        """Analyze input file structure for CP-Municipality breakdown"""
        try:
            df = pd.read_excel(file_path)
            
            # Validate required columns
            required_columns = ['tipo_catasto', 'CP', 'provincia', 'comune', 'foglio', 'particella', 'Area']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"❌ Missing required columns: {missing_columns}")
                return None
            
            # Check for optional Sezione column
            has_sezione = 'Sezione' in df.columns
            sezione_usage = 0
            if has_sezione:
                sezione_usage = df['Sezione'].notna().sum()
                if sezione_usage > 0:
                    print(f"📍 Sezione field detected: {sezione_usage}/{len(df)} parcels have sezione data")
                    print("   ✅ Sezione will be included in API calls where provided")
            
            # Analyze CP-Municipality structure
            cp_analysis = df.groupby('CP').agg({
                'comune': lambda x: list(x.unique()),
                'provincia': 'first',
                'foglio': 'count'
            }).rename(columns={'foglio': 'parcel_count'})
            
            municipality_count = df['comune'].nunique()
            total_parcels = len(df)
            
            analysis = {
                'total_parcels': total_parcels,
                'total_cps': len(cp_analysis),
                'total_municipalities': municipality_count,
                'cp_breakdown': cp_analysis.to_dict('index'),
                'has_sezione': has_sezione,
                'sezione_usage': sezione_usage,
                'dataframe': df
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing input file: {str(e)}")
            return None
    
    def display_input_analysis(self, analysis):
        """Display detailed input file analysis"""
        print(f"\n📊 INPUT FILE ANALYSIS")
        print("="*50)
        print(f"📍 Total Parcels: {analysis['total_parcels']:,}")
        print(f"🎯 Connection Points (CPs): {analysis['total_cps']}")
        print(f"🏘️  Municipalities: {analysis['total_municipalities']}")
        
        # Show sezione information if present
        if analysis.get('has_sezione', False) and analysis.get('sezione_usage', 0) > 0:
            sezione_percentage = (analysis['sezione_usage'] / analysis['total_parcels']) * 100
            print(f"📍 Sezione Usage: {analysis['sezione_usage']}/{analysis['total_parcels']} parcels ({sezione_percentage:.1f}%)")
            print("   ✅ Sezione data will be sent to API where available")
        
        # Show geocoding info
        geocoding_enabled, geocoding_status = self.check_geocoding_setup()
        if geocoding_enabled:
            print(f"🗺️  Address Enhancement: ✅ ENABLED (ZIP codes + coordinates)")
        else:
            print(f"🗺️  Address Enhancement: {geocoding_status}")
        
        # v2.9 features
        print(f"📊 Funnel Tracking: ✅ ENABLED (v2.9)")
        print(f"📮 SNC Routing: ✅ DIRECT_MAIL (v2.9)")
        
        print()
        
        print("📋 CP-Municipality Breakdown:")
        print("-" * 40)
        for cp, details in analysis['cp_breakdown'].items():
            municipalities = ", ".join(details['comune'])
            province = details['provincia']
            parcel_count = details['parcel_count']
            
            # Show sezione info for this CP if available
            sezione_info = ""
            if analysis.get('has_sezione', False) and analysis.get('sezione_usage', 0) > 0:
                df = analysis['dataframe']
                cp_sezione_count = df[df['CP'] == cp]['Sezione'].notna().sum()
                if cp_sezione_count > 0:
                    unique_sezioni = df[df['CP'] == cp]['Sezione'].dropna().unique()
                    sezione_info = f" (Sezioni: {', '.join(map(str, unique_sezioni))})"
            
            print(f"   🎯 CP {cp} ({province}):")
            print(f"      Municipalities: {municipalities}{sezione_info}")
            print(f"      Parcels: {parcel_count:,}")
            print()
    
    def preview_onedrive_structure(self, campaign_name, analysis):
        """Preview how results will be organized in OneDrive with geocoding info"""
        onedrive_path = self.config.get('output_structure', {}).get('onedrive_sync_path', 'OneDrive\\LandAcquisition\\Campaigns')
        geocoding_enabled, _ = self.check_geocoding_setup()
        
        print(f"\n📁 ONEDRIVE STRUCTURE PREVIEW")
        print("="*50)
        print(f"📂 {onedrive_path}\\{campaign_name}\\")
        
        # Show municipality folders
        for cp, details in analysis['cp_breakdown'].items():
            for comune in details['comune']:
                municipality_key = f"{cp}_{comune.replace(' ', '_')}"
                print(f"   📂 {municipality_key}\\")
                if geocoding_enabled:
                    print(f"      📄 Validation_Ready.xlsx  ← Enhanced with ZIP codes & coordinates")
                else:
                    print(f"      📄 Validation_Ready.xlsx  ← For Land Acquisition Team review")
                print(f"      📄 Companies_Found.xlsx    ← Companies detected (if any)")
                print(f"      📄 Funnel_Analysis.xlsx    ← NEW! Parcel/hectare flow (v2.9)")
                print(f"      📄 {municipality_key}_Complete_Results.xlsx")
        
        print(f"   📄 Campaign_Summary.xlsx  ← Overview for management")
        print(f"   📄 PowerBI_Dataset.csv   ← Enhanced with funnel metrics (v2.9)")
        print(f"   📄 Enhanced_Cost_Summary.txt  ← Campaign cost breakdown")
        print()
        print("👥 TEAM ACCESS:")
        if geocoding_enabled:
            print(f"   • Land Acquisition: Reviews enhanced 'Validation_Ready.xlsx' files")
            print(f"     - ZIP codes in 'Poste_Address' column")
            print(f"     - Postal-ready addresses in 'Geocoded_Address_Italian' column")
            print(f"     - Geographic coordinates for mapping")
            print(f"     - SNC addresses now marked for DIRECT_MAIL (v2.9)")
            print(f"   • Business Development: Reviews 'Companies_Found.xlsx' files")
            print(f"     - Company properties for B2B opportunities")
            print(f"   • Management: Views funnel metrics in new sheets (v2.9)")
        else:
            print(f"   • Land Acquisition: Reviews 'Validation_Ready.xlsx' files")
            print(f"     - SNC addresses now marked for DIRECT_MAIL (v2.9)")
            print(f"   • Business Development: Reviews 'Companies_Found.xlsx' files")
            print(f"   • Management: Views funnel metrics in new sheets (v2.9)")
        print(f"   • You: Use enhanced 'PowerBI_Dataset.csv' to update dashboard")
        print()
    
    def show_processing_summary(self, analysis):
        """Show processing summary with geocoding information"""
        print(f"\n📋 PROCESSING SUMMARY")
        print("="*50)
        
        parcel_count = analysis['total_parcels']
        municipality_count = analysis['total_municipalities']
        geocoding_enabled, geocoding_status = self.check_geocoding_setup()
        
        print(f"📊 Ready to Process:")
        print(f"   Total parcels: {parcel_count:,}")
        print(f"   Municipalities: {municipality_count}")
        print(f"   Cost tracking: Manual balance check (start/end)")
        
        if analysis.get('has_sezione', False) and analysis.get('sezione_usage', 0) > 0:
            print(f"   Sezione parcels: {analysis['sezione_usage']} will include Sezione in API calls")
        
        if geocoding_enabled:
            print(f"   🗺️  Address enhancement: ENABLED")
            print(f"      • ZIP codes will be added")
            print(f"      • Italian postal format addresses")
            print(f"      • Geographic coordinates")
            print(f"      • Administrative data (provinces, regions)")
        else:
            print(f"   🗺️  Address enhancement: {geocoding_status}")
        
        print(f"\n🆕 v2.9 Enhancements:")
        print(f"   📮 SNC addresses → DIRECT_MAIL (postal service knows them)")
        print(f"   📊 Funnel tracking → See parcel/hectare flow at each stage")
        print(f"   🏢 Company metrics → Separate tracking, total visibility")
        
        print()
        print(f"📁 Will create:")
        print(f"   • {municipality_count} municipality folders")
        if geocoding_enabled:
            print(f"   • {municipality_count} enhanced 'Validation_Ready.xlsx' files")
        else:
            print(f"   • {municipality_count} 'Validation_Ready.xlsx' files")
        print(f"   • Company files when companies are detected")
        print(f"   • Funnel analysis sheets showing data flow (v2.9)")
        print(f"   • 1 Power BI dataset with funnel metrics")
        print(f"   • 1 comprehensive campaign summary")
        print()
        
        return True
    
    def get_campaign_confirmation(self, campaign_name, analysis):
        """Get final confirmation before launching campaign"""
        geocoding_enabled, _ = self.check_geocoding_setup()
        
        print(f"\n🚀 CAMPAIGN LAUNCH CONFIRMATION")
        print("="*60)
        print(f"Campaign Name: {campaign_name}")
        print(f"CPs: {analysis['total_cps']} | Municipalities: {analysis['total_municipalities']} | Parcels: {analysis['total_parcels']:,}")
        
        if analysis.get('has_sezione', False) and analysis.get('sezione_usage', 0) > 0:
            print(f"Sezione Support: {analysis['sezione_usage']} parcels will include Sezione in API calls")
        
        if geocoding_enabled:
            print(f"Address Enhancement: ✅ ENABLED - ZIP codes and coordinates will be added")
        else:
            print(f"Address Enhancement: ❌ DISABLED")
        
        print(f"SNC Routing: ✅ DIRECT_MAIL (v2.9 - postal service update)")
        print(f"Funnel Tracking: ✅ ENABLED (v2.9 - complete visibility)")
        
        print()
        print("🔄 What will happen:")
        print("   1. ✅ Auto-create municipality folders")
        print("   2. 🔄 Process each municipality through Land Registry API")
        print("   3. 📊 Track parcels/hectares through each processing stage (v2.9)")
        print("   4. 🏢 Separate companies from individuals automatically")
        print("   5. 🧹 Generate cleaned 'Validation_Ready' sheets for individuals")
        if geocoding_enabled:
            print("   6. 🗺️  Enhance addresses with ZIP codes and coordinates")
            print("   7. 📮 Route SNC addresses to DIRECT_MAIL (v2.9)")
            print("   8. 🏢 Create 'Companies_Found.xlsx' files when applicable")
            print("   9. 📊 Create funnel analysis showing data flow (v2.9)")
            print("   10. 📊 Create Power BI dataset with all metrics")
            print("   11. 📋 Generate comprehensive campaign dashboard")
            print("   12. 📁 Copy results to OneDrive for team access")
        else:
            print("   6. 📮 Route SNC addresses to DIRECT_MAIL (v2.9)")
            print("   7. 🏢 Create 'Companies_Found.xlsx' files when applicable")
            print("   8. 📊 Create funnel analysis showing data flow (v2.9)")
            print("   9. 📊 Create Power BI dataset")
            print("   10. 📋 Generate campaign dashboard")
            print("   11. 📁 Copy results to OneDrive for team access")
        print()
        
        while True:
            confirm = input("🚀 Launch campaign? (y/n): ").lower().strip()
            if confirm in ['y', 'yes']:
                return True
            elif confirm in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    def generate_campaign_name(self, analysis):
        """Generate unique campaign name"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Include main CPs in name for clarity
        main_cps = list(analysis['cp_breakdown'].keys())[:2]  # First 2 CPs
        cp_suffix = "_".join(main_cps).replace(' ', '_')
        
        return f"LandAcquisition_{cp_suffix}_{timestamp}"
    
    def create_campaign_config(self, input_file, campaign_name, analysis):
        """Create comprehensive campaign configuration with geocoding info"""
        
        # Convert pandas/numpy types to native Python types for JSON serialization
        cp_breakdown_clean = {}
        for cp, details in analysis['cp_breakdown'].items():
            cp_breakdown_clean[str(cp)] = {
                'comune': details['comune'],  # Already a list of strings
                'provincia': str(details['provincia']),
                'parcel_count': int(details['parcel_count'])  # Convert numpy.int64 to int
            }
        
        geocoding_enabled, _ = self.check_geocoding_setup()
        
        campaign_config = {
            "campaign_name": campaign_name,
            "input_file": input_file,
            "created_date": datetime.now().isoformat(),
            "campaign_analysis": {
                "total_parcels": int(analysis['total_parcels']),
                "total_cps": int(analysis['total_cps']), 
                "total_municipalities": int(analysis['total_municipalities']),
                "cp_breakdown": cp_breakdown_clean,
                "has_sezione": bool(analysis.get('has_sezione', False)),
                "sezione_usage": int(analysis.get('sezione_usage', 0))
            },
            "processing_settings": {
                "focus_residential": True,
                "municipality_batch_size": 50,
                "validation_quality_threshold": 70,
                "api_token": self.config.get('api_settings', {}).get('token'),
                "powerbi_enabled": self.config.get('powerbi_integration', {}).get('enabled', True),
                "onedrive_enabled": self.config.get('output_structure', {}).get('auto_copy_to_onedrive', True),
                "geocoding_enabled": geocoding_enabled,
                "geocoding_token": self.config.get('geocoding_settings', {}).get('token') if geocoding_enabled else None,
                "funnel_tracking_enabled": True,  # v2.9
                "snc_direct_mail_routing": True  # v2.9
            },
            "expected_outputs": {
                "municipality_folders": int(analysis['total_municipalities']),
                "validation_ready_sheets": int(analysis['total_municipalities']),
                "powerbi_dataset": True,
                "campaign_dashboard": True,
                "geocoding_enhancement": geocoding_enabled,
                "funnel_analysis_sheets": True,  # v2.9
                "enhanced_company_tracking": True  # v2.9
            }
        }
        
        # Save campaign config
        campaigns_dir = "campaigns"
        os.makedirs(campaigns_dir, exist_ok=True)
        config_file = os.path.join(campaigns_dir, f"{campaign_name}_config.json")
        
        with open(config_file, 'w') as f:
            json.dump(campaign_config, f, indent=4)
        
        return config_file
    
    def create_team_notification_template(self, campaign_name, analysis):
        """Create email template for notifying team with geocoding info"""
        geocoding_enabled, _ = self.check_geocoding_setup()
        
        geocoding_section = ""
        if geocoding_enabled:
            geocoding_section = """

🗺️ NEW: ENHANCED ADDRESSES
• ZIP codes added to all addresses (see 'Poste_Address' column)
• Postal-ready formatted addresses (see 'Geocoded_Address_Italian' column)
• Geographic coordinates for mapping
• Province codes and administrative data
• Focus on geocoded addresses for better mailing success"""
        
        template = f"""
📧 EMAIL TEMPLATE FOR TEAM NOTIFICATION:

Subject: Enhanced Land Acquisition Campaign Completed - {campaign_name} (v2.9)

Hi Team,

Campaign "{campaign_name}" has been completed with v2.9 enhancements and results are available in OneDrive.

📁 Location: OneDrive > Italy - Documentos > Origination > 1. Land > Campaigns > test_workflow > Campaigns > {campaign_name}

🆕 NEW IN v2.9:
• SNC addresses now routed to DIRECT_MAIL (postal service knows these streets)
• Complete funnel visibility showing parcel/hectare flow through each stage
• Separate company tracking while maintaining total visibility
• Enhanced Power BI dataset with funnel metrics

📋 For Land Acquisition Team:
• {analysis['total_municipalities']} municipalities processed
• Review "Validation_Ready.xlsx" files in each municipality folder
• SNC addresses are now marked for DIRECT_MAIL (postal service update)
• Focus on addresses with complete data first
• Expected validation-ready records: ~{analysis['total_parcels'] // 3}
{geocoding_section}

🏢 For Business Development Team:
• Check "Companies_Found.xlsx" files in municipality folders
• Contains company-owned properties for B2B opportunities
• Includes company details and property information

📊 For Management:
• View "Campaign_Summary.xlsx" for overview
• NEW: Check "Funnel_Analysis" sheets for parcel/hectare flow visibility
• Power BI dataset now includes complete funnel metrics
• Geographic data available for mapping analysis

💰 Campaign Cost: Will be provided after manual balance check

📞 Questions? Contact [Your Name]

Best regards,
[Your Name]
        """
        return template.strip()
    
    def show_powerbi_next_steps(self, campaign_name):
        """Show steps to update Power BI dashboard with geocoding metrics"""
        geocoding_enabled, _ = self.check_geocoding_setup()
        
        print(f"\n📊 POWER BI NEXT STEPS (v2.9)")
        print("="*40)
        print("⚠️  Note: Power BI dataset now includes v2.9 funnel metrics")
        print()
        print("1. 📁 Find PowerBI_Dataset.csv in campaign folder")
        print("2. 📊 Open your Land Acquisition Power BI file (or create new)")
        print("3. 🔄 Import/refresh data with new CSV")
        print("4. 📈 Create funnel visualizations with new metrics:")
        print("   • Input_Parcels / Input_Area_Ha")
        print("   • After_API_Parcels / After_API_Area_Ha")
        print("   • Private vs Company owner distribution")
        print("   • Cat.A filter impact on parcels/hectares")
        print("   • Final routing distribution (Direct Mail vs Agency)")
        if geocoding_enabled:
            print("5. 🗺️  Add geocoding metrics if needed:")
            print("   • Address enhancement success rates")
            print("   • Geographic distribution (basic)")
            print("   • ZIP code coverage analysis")
        else:
            print("5. 📈 Create standard metrics charts")
        print("6. 📤 Share results with management")
        print()
        print("💡 v2.9 dataset includes:")
        print("   • Complete funnel metrics (parcels + hectares)")
        print("   • Campaign progress by CP/municipality")
        print("   • Company metrics (separate + total)")
        if geocoding_enabled:
            print("   • Geocoding success rates")
        print("   • Cost tracking with recovery metrics")
        print()
        print("🔮 Future enhancements will include:")
        print("   • Pre-built dashboard templates")
        print("   • Advanced geographic visualizations")
        print("   • Real-time progress tracking")
        print("   • Automated dashboard updates")
        print()
        print("🌐 Strategic Direction:")
        print("   • Evolution to cloud-based web application")
        print("   • User-friendly interface for all team members")
        print("   • Enhanced collaboration and real-time features")
        print()
    
    def run(self):
        """Main launcher workflow - enhanced with geocoding support"""
        self.show_welcome()
        self.show_geocoding_benefits()
        
        # Get start balance
        start_balance = self.get_manual_cost_input("start")
        
        # Get input file and analyze structure
        input_file = self.get_input_file()
        analysis = self.analyze_input_file(input_file)
        
        if not analysis:
            print("❌ Unable to analyze input file. Please check file format.")
            return
        
        self.display_input_analysis(analysis)
        
        # Generate campaign name
        campaign_name = self.generate_campaign_name(analysis)
        
        # Show processing summary
        self.show_processing_summary(analysis)
        
        # Preview OneDrive structure
        self.preview_onedrive_structure(campaign_name, analysis)
        
        # Get final confirmation
        if not self.get_campaign_confirmation(campaign_name, analysis):
            print("❌ Campaign cancelled by user.")
            return
        
        # Create campaign configuration
        config_file = self.create_campaign_config(input_file, campaign_name, analysis)
        
        print(f"\n✅ Campaign '{campaign_name}' configured successfully!")
        print(f"📁 Configuration: {config_file}")
        
        # Show processing instructions
        print(f"\n🚀 TO PROCESS THE CAMPAIGN:")
        print(f"python land_acquisition_pipeline.py --config {config_file} --start-balance {start_balance}")
        print()
        print("📊 You'll be prompted for end balance when processing is complete")
        print("💰 Cost will be calculated automatically from balance difference")
        
        geocoding_enabled, _ = self.check_geocoding_setup()
        if geocoding_enabled:
            print("🗺️  Addresses will be enhanced with ZIP codes and coordinates")
        else:
            print("⚠️  Address enhancement disabled - configure geocoding token to enable")
        
        print("📮 SNC addresses will be routed to DIRECT_MAIL (v2.9)")
        print("📊 Complete funnel tracking will show parcel/hectare flow")
        
        # Show team notification template
        template = self.create_team_notification_template(campaign_name, analysis)
        print(f"\n📧 TEAM NOTIFICATION TEMPLATE:")
        print("-" * 40)
        print(template)
        
        # Show Power BI steps
        self.show_powerbi_next_steps(campaign_name)

def main():
    """Main function"""
    try:
        launcher = EnhancedLandAcquisitionCampaignLauncher()
        launcher.run()
                
    except KeyboardInterrupt:
        print("\n\n❌ Campaign launcher cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Please check your configuration and input file format.")

if __name__ == "__main__":
    main()