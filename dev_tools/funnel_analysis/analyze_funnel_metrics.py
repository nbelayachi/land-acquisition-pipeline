"""
Analyze Funnel Analysis and Campaign Scorecard Metrics
Focus on upper management KPIs and PowerBI visualization readiness
"""

import pandas as pd
import numpy as np

def analyze_funnel_and_scorecard():
    """Comprehensive analysis of funnel metrics for upper management reporting"""
    
    results_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250702_0018\LandAcquisition_Casalpusterlengo_Castiglione_20250702_0018_Results.xlsx"
    
    print("🔍 FUNNEL ANALYSIS & SCORECARD REVIEW")
    print("=" * 60)
    print("Focus: Upper Management KPIs & PowerBI Readiness")
    print()
    
    try:
        excel_file = pd.ExcelFile(results_file)
        
        # 1. FUNNEL ANALYSIS EXAMINATION
        if 'Funnel_Analysis' in excel_file.sheet_names:
            print("📊 FUNNEL ANALYSIS STRUCTURE")
            print("-" * 40)
            
            funnel_df = pd.read_excel(results_file, sheet_name='Funnel_Analysis')
            print(f"Rows: {len(funnel_df)}")
            print(f"Columns: {list(funnel_df.columns)}")
            print()
            
            # Display all funnel data
            print("FUNNEL METRICS DATA:")
            for idx, row in funnel_df.iterrows():
                print(f"Row {idx + 1}:")
                for col in funnel_df.columns:
                    value = row[col]
                    print(f"  {col}: {value}")
                print()
            
            # Check for end-to-end process tracking
            print("END-TO-END PROCESS ANALYSIS:")
            print("Expected funnel stages for land acquisition:")
            expected_stages = [
                "Input Parcels",
                "Ownership Records Found", 
                "Addresses Processed",
                "Geocoding Success",
                "High Confidence Addresses",
                "Ultra High Confidence",
                "Direct Mail Ready",
                "Agency Routing Required"
            ]
            
            for stage in expected_stages:
                found = any(stage.lower() in str(col).lower() for col in funnel_df.columns)
                status = "✅ Found" if found else "❌ Missing"
                print(f"  {stage}: {status}")
            print()
            
        # 2. CAMPAIGN SCORECARD EXAMINATION
        if 'Campaign_Scorecard' in excel_file.sheet_names:
            print("📈 CAMPAIGN SCORECARD STRUCTURE")
            print("-" * 40)
            
            scorecard_df = pd.read_excel(results_file, sheet_name='Campaign_Scorecard')
            print(f"Rows: {len(scorecard_df)}")
            print(f"Columns: {list(scorecard_df.columns)}")
            print()
            
            # Display all scorecard data
            print("SCORECARD METRICS DATA:")
            for idx, row in scorecard_df.iterrows():
                print(f"Metric {idx + 1}:")
                for col in scorecard_df.columns:
                    value = row[col]
                    print(f"  {col}: {value}")
                print()
            
            # Check for upper management KPIs
            print("UPPER MANAGEMENT KPI ANALYSIS:")
            executive_kpis = [
                "Campaign Efficiency",
                "Time Savings",
                "Cost per Contact",
                "Automation Rate",
                "Manual Review Reduction",
                "Quality Score",
                "Processing Speed",
                "Success Rate"
            ]
            
            for kpi in executive_kpis:
                found = any(kpi.lower() in str(col).lower() or kpi.lower() in str(scorecard_df.values).lower() for col in scorecard_df.columns)
                status = "✅ Present" if found else "❌ Missing"
                print(f"  {kpi}: {status}")
            print()
        
        # 3. POWERBI VISUALIZATION READINESS
        print("💻 POWERBI VISUALIZATION READINESS")
        print("-" * 40)
        
        powerbi_requirements = {
            "Numerical Metrics": [],
            "Categorical Data": [],
            "Time Series Data": [],
            "Percentage Metrics": [],
            "Count Metrics": []
        }
        
        # Analyze both sheets for PowerBI compatibility
        for sheet_name in ['Funnel_Analysis', 'Campaign_Scorecard']:
            if sheet_name in excel_file.sheet_names:
                df = pd.read_excel(results_file, sheet_name=sheet_name)
                
                print(f"\n{sheet_name} PowerBI Analysis:")
                for col in df.columns:
                    col_data = df[col].dropna()
                    if len(col_data) > 0:
                        sample_value = col_data.iloc[0]
                        
                        # Classify data types for PowerBI
                        if pd.api.types.is_numeric_dtype(col_data):
                            if any(x in str(col).lower() for x in ['%', 'percent', 'rate']):
                                powerbi_requirements["Percentage Metrics"].append(f"{sheet_name}.{col}")
                                viz_type = "📊 Gauge/KPI Card"
                            elif any(x in str(col).lower() for x in ['count', 'total', 'number']):
                                powerbi_requirements["Count Metrics"].append(f"{sheet_name}.{col}")
                                viz_type = "🔢 Card/Bar Chart"
                            else:
                                powerbi_requirements["Numerical Metrics"].append(f"{sheet_name}.{col}")
                                viz_type = "📈 Line/Bar Chart"
                        elif any(x in str(col).lower() for x in ['date', 'time', 'timestamp']):
                            powerbi_requirements["Time Series Data"].append(f"{sheet_name}.{col}")
                            viz_type = "📅 Time Series"
                        else:
                            powerbi_requirements["Categorical Data"].append(f"{sheet_name}.{col}")
                            viz_type = "🏷️ Slicer/Filter"
                        
                        print(f"  {col}: {viz_type}")
        
        print(f"\nPOWERBI DATASET SUMMARY:")
        for category, fields in powerbi_requirements.items():
            print(f"  {category}: {len(fields)} fields")
            for field in fields[:3]:  # Show first 3 examples
                print(f"    - {field}")
            if len(fields) > 3:
                print(f"    ... and {len(fields) - 3} more")
        
        # 4. RECOMMENDATIONS
        print(f"\n🎯 RECOMMENDATIONS FOR IMPROVEMENT")
        print("-" * 40)
        
        recommendations = []
        
        # Check if key metrics are missing
        if 'Funnel_Analysis' in excel_file.sheet_names:
            funnel_df = pd.read_excel(results_file, sheet_name='Funnel_Analysis')
            if len(funnel_df) < 5:
                recommendations.append("Add more funnel stages for complete process visibility")
            if not any('conversion' in str(col).lower() for col in funnel_df.columns):
                recommendations.append("Add conversion rates between funnel stages")
        
        if 'Campaign_Scorecard' in excel_file.sheet_names:
            scorecard_df = pd.read_excel(results_file, sheet_name='Campaign_Scorecard')
            if not any('benchmark' in str(col).lower() for col in scorecard_df.columns):
                recommendations.append("Add benchmark comparisons for KPIs")
            if not any('target' in str(col).lower() for col in scorecard_df.columns):
                recommendations.append("Include target values for performance tracking")
        
        # PowerBI specific recommendations
        if len(powerbi_requirements["Time Series Data"]) == 0:
            recommendations.append("Add timestamp columns for trend analysis in PowerBI")
        if len(powerbi_requirements["Percentage Metrics"]) < 3:
            recommendations.append("Convert more metrics to percentages for executive dashboards")
        
        print("Priority improvements:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        if not recommendations:
            print("✅ Current metrics structure is well-designed for executive reporting")
        
        return {
            'funnel_columns': list(funnel_df.columns) if 'Funnel_Analysis' in excel_file.sheet_names else [],
            'scorecard_columns': list(scorecard_df.columns) if 'Campaign_Scorecard' in excel_file.sheet_names else [],
            'powerbi_ready': len(powerbi_requirements["Numerical Metrics"]) + len(powerbi_requirements["Percentage Metrics"]) > 5,
            'recommendations': recommendations
        }
        
    except Exception as e:
        print(f"❌ Error analyzing metrics: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 Starting funnel and scorecard analysis...")
    results = analyze_funnel_and_scorecard()
    
    if results:
        print(f"\n✅ Analysis complete!")
        print(f"📊 PowerBI Ready: {results['powerbi_ready']}")
        print(f"🎯 Recommendations: {len(results['recommendations'])}")
    else:
        print(f"\n❌ Analysis failed")