"""
Simple Funnel Analysis without Unicode issues
"""

import pandas as pd

# Analyze the campaign results
results_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250702_0018\LandAcquisition_Casalpusterlengo_Castiglione_20250702_0018_Results.xlsx"

print("FUNNEL ANALYSIS & SCORECARD REVIEW")
print("=" * 50)
print("Focus: Upper Management KPIs & PowerBI Readiness")
print()

try:
    excel_file = pd.ExcelFile(results_file)
    
    # 1. FUNNEL ANALYSIS EXAMINATION
    if 'Funnel_Analysis' in excel_file.sheet_names:
        print("FUNNEL ANALYSIS STRUCTURE")
        print("-" * 30)
        
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
        expected_stages = [
            "Input Parcels",
            "Ownership Records", 
            "Addresses Processed",
            "Geocoding Success",
            "High Confidence",
            "Ultra High Confidence",
            "Direct Mail Ready"
        ]
        
        for stage in expected_stages:
            found = any(stage.lower() in str(col).lower() for col in funnel_df.columns)
            status = "Found" if found else "Missing"
            print(f"  {stage}: {status}")
        print()
        
    # 2. CAMPAIGN SCORECARD EXAMINATION
    if 'Campaign_Scorecard' in excel_file.sheet_names:
        print("CAMPAIGN SCORECARD STRUCTURE")
        print("-" * 30)
        
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
            "Efficiency",
            "Time Savings",
            "Cost",
            "Automation",
            "Manual Review",
            "Quality",
            "Speed",
            "Success Rate"
        ]
        
        for kpi in executive_kpis:
            found = any(kpi.lower() in str(col).lower() or kpi.lower() in str(scorecard_df.values).lower() for col in scorecard_df.columns)
            status = "Present" if found else "Missing"
            print(f"  {kpi}: {status}")
        print()
    
    # 3. POWERBI VISUALIZATION READINESS
    print("POWERBI VISUALIZATION READINESS")
    print("-" * 30)
    
    # Analyze both sheets for PowerBI compatibility
    for sheet_name in ['Funnel_Analysis', 'Campaign_Scorecard']:
        if sheet_name in excel_file.sheet_names:
            df = pd.read_excel(results_file, sheet_name=sheet_name)
            
            print(f"{sheet_name} PowerBI Analysis:")
            for col in df.columns:
                col_data = df[col].dropna()
                if len(col_data) > 0:
                    # Classify data types for PowerBI
                    if pd.api.types.is_numeric_dtype(col_data):
                        if any(x in str(col).lower() for x in ['%', 'percent', 'rate']):
                            viz_type = "Gauge/KPI Card"
                        elif any(x in str(col).lower() for x in ['count', 'total', 'number']):
                            viz_type = "Card/Bar Chart"
                        else:
                            viz_type = "Line/Bar Chart"
                    elif any(x in str(col).lower() for x in ['date', 'time']):
                        viz_type = "Time Series"
                    else:
                        viz_type = "Slicer/Filter"
                    
                    print(f"  {col}: {viz_type}")
            print()
    
    # 4. RECOMMENDATIONS
    print("RECOMMENDATIONS FOR IMPROVEMENT")
    print("-" * 30)
    
    recommendations = []
    
    # Check if key metrics are missing
    if 'Funnel_Analysis' in excel_file.sheet_names:
        funnel_df = pd.read_excel(results_file, sheet_name='Funnel_Analysis')
        if len(funnel_df) < 5:
            recommendations.append("Add more funnel stages for visibility")
        if not any('conversion' in str(col).lower() for col in funnel_df.columns):
            recommendations.append("Add conversion rates between stages")
    
    if 'Campaign_Scorecard' in excel_file.sheet_names:
        scorecard_df = pd.read_excel(results_file, sheet_name='Campaign_Scorecard')
        if not any('benchmark' in str(col).lower() for col in scorecard_df.columns):
            recommendations.append("Add benchmark comparisons")
        if not any('target' in str(col).lower() for col in scorecard_df.columns):
            recommendations.append("Include target values")
    
    print("Priority improvements:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    if not recommendations:
        print("Current metrics structure looks good")
    
except Exception as e:
    print(f"Error: {str(e)}")

print("\nAnalysis complete!")