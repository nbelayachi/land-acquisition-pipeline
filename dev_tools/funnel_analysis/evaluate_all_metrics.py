"""
Exhaustive evaluation of all metrics across all sheets
Focus on operational metrics: counts, hectares, contacts
"""

import pandas as pd

results_file = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250702_0018\LandAcquisition_Casalpusterlengo_Castiglione_20250702_0018_Results.xlsx"

print("EXHAUSTIVE METRICS EVALUATION")
print("=" * 60)
print("Focus: Operational metrics, counts, hectares, contacts")
print()

try:
    excel_file = pd.ExcelFile(results_file)
    print(f"Available sheets: {excel_file.sheet_names}")
    print()
    
    # Dictionary to store all metrics found
    all_metrics = {}
    
    # 1. ANALYZE EACH SHEET SYSTEMATICALLY
    for sheet_name in excel_file.sheet_names:
        print(f"SHEET: {sheet_name}")
        print("-" * 40)
        
        df = pd.read_excel(results_file, sheet_name=sheet_name)
        print(f"Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Identify metric types in this sheet
        metrics_in_sheet = {
            'count_metrics': [],
            'hectare_metrics': [], 
            'contact_metrics': [],
            'parcel_metrics': [],
            'address_metrics': [],
            'other_metrics': []
        }
        
        for col in df.columns:
            col_lower = str(col).lower()
            
            # Classify metrics
            if any(word in col_lower for word in ['count', 'total', 'number', 'num']):
                metrics_in_sheet['count_metrics'].append(col)
            elif any(word in col_lower for word in ['hectare', 'ha', 'area', 'size']):
                metrics_in_sheet['hectare_metrics'].append(col)
            elif any(word in col_lower for word in ['contact', 'owner', 'people', 'mailing', 'mail']):
                metrics_in_sheet['contact_metrics'].append(col)
            elif any(word in col_lower for word in ['parcel', 'foglio', 'particella']):
                metrics_in_sheet['parcel_metrics'].append(col)
            elif any(word in col_lower for word in ['address', 'confidence', 'geocod', 'routing']):
                metrics_in_sheet['address_metrics'].append(col)
            else:
                metrics_in_sheet['other_metrics'].append(col)
        
        # Display metrics by category
        for category, cols in metrics_in_sheet.items():
            if cols:
                print(f"  {category.upper()}: {cols}")
        
        # Store unique values for key columns if small dataset
        if len(df) <= 50:
            print("  Sample data overview:")
            for col in df.columns:
                unique_vals = df[col].dropna().unique()
                if len(unique_vals) <= 10:
                    print(f"    {col}: {list(unique_vals)}")
                elif pd.api.types.is_numeric_dtype(df[col]):
                    print(f"    {col}: {df[col].min()}-{df[col].max()} (range)")
                else:
                    print(f"    {col}: {len(unique_vals)} unique values")
        
        all_metrics[sheet_name] = metrics_in_sheet
        print()
    
    # 2. CROSS-SHEET METRICS ANALYSIS
    print("CROSS-SHEET METRICS SUMMARY")
    print("=" * 40)
    
    # Consolidate all metrics by type
    consolidated_metrics = {
        'count_metrics': [],
        'hectare_metrics': [],
        'contact_metrics': [],
        'parcel_metrics': [],
        'address_metrics': []
    }
    
    for sheet_name, sheet_metrics in all_metrics.items():
        for category, cols in sheet_metrics.items():
            if category in consolidated_metrics:
                for col in cols:
                    consolidated_metrics[category].append(f"{sheet_name}.{col}")
    
    for category, metrics in consolidated_metrics.items():
        print(f"{category.upper()}: {len(metrics)} total")
        for metric in metrics:
            print(f"  - {metric}")
        print()
    
    # 3. FUNNEL LOGIC VALIDATION
    print("FUNNEL LOGIC VALIDATION")
    print("=" * 30)
    
    if 'Funnel_Analysis' in excel_file.sheet_names:
        funnel_df = pd.read_excel(results_file, sheet_name='Funnel_Analysis')
        
        # Group by funnel type to understand logic
        parcel_funnel = funnel_df[funnel_df['Funnel_Type'] == 'Parcel Journey']
        contact_funnel = funnel_df[funnel_df['Funnel_Type'] == 'Contact Journey']
        
        print("PARCEL FUNNEL STAGES:")
        parcel_stages = parcel_funnel['Stage'].unique()
        for stage in sorted(parcel_stages):
            stage_data = parcel_funnel[parcel_funnel['Stage'] == stage]
            total_count = stage_data['Count'].sum()
            total_hectares = stage_data['Hectares'].sum()
            print(f"  {stage}: {total_count} parcels, {total_hectares:.1f} hectares")
        
        print("\nCONTACT FUNNEL STAGES:")
        contact_stages = contact_funnel['Stage'].unique()
        for stage in sorted(contact_stages):
            stage_data = contact_funnel[contact_funnel['Stage'] == stage]
            total_count = stage_data['Count'].sum()
            total_hectares = stage_data['Hectares'].sum()
            print(f"  {stage}: {total_count} contacts, {total_hectares:.1f} hectares")
        
        # Check funnel logic consistency
        print("\nFUNNEL CONSISTENCY CHECK:")
        
        # Parcel funnel should decrease or stay same
        parcel_counts = []
        for stage in sorted(parcel_stages):
            stage_data = parcel_funnel[parcel_funnel['Stage'] == stage]
            parcel_counts.append(stage_data['Count'].sum())
        
        print(f"Parcel progression: {parcel_counts}")
        parcel_consistent = all(parcel_counts[i] >= parcel_counts[i+1] for i in range(len(parcel_counts)-1))
        print(f"Parcel funnel decreasing: {'Yes' if parcel_consistent else 'No - ISSUE'}")
        
        # Contact funnel logic (owners -> contacts -> routing)
        contact_counts = []
        for stage in sorted(contact_stages):
            stage_data = contact_funnel[contact_funnel['Stage'] == stage]
            contact_counts.append(stage_data['Count'].sum())
        
        print(f"Contact progression: {contact_counts}")
        
        # Check if high + low confidence = total contacts
        if len(contact_counts) >= 4:
            total_contacts = contact_counts[1]  # Stage 2: Unique Contacts
            high_conf = contact_counts[2]       # Stage 3: High-Confidence
            low_conf = contact_counts[3]        # Stage 4: Low-Confidence
            routing_total = high_conf + low_conf
            
            print(f"Routing logic check: {total_contacts} contacts = {high_conf} high + {low_conf} low = {routing_total}")
            routing_consistent = abs(total_contacts - routing_total) <= 1  # Allow for rounding
            print(f"Contact routing consistent: {'Yes' if routing_consistent else 'No - ISSUE'}")
    
    # 4. MISSING METRICS IDENTIFICATION
    print("\nMISSING OPERATIONAL METRICS")
    print("=" * 30)
    
    expected_operational_metrics = [
        "Total input parcels",
        "Total hectares input", 
        "Unique owners identified",
        "Total owner-address pairs",
        "Geocoding success rate",
        "ULTRA_HIGH confidence count",
        "HIGH confidence count", 
        "MEDIUM confidence count",
        "LOW confidence count",
        "Direct mail ready count",
        "Agency routing count",
        "Addresses requiring manual review",
        "Perfect match addresses",
        "Similar number matches"
    ]
    
    # Check which are present vs missing
    all_columns = []
    for sheet_metrics in all_metrics.values():
        for cols in sheet_metrics.values():
            all_columns.extend(cols)
    
    all_columns_text = ' '.join(all_columns).lower()
    
    for metric in expected_operational_metrics:
        metric_words = metric.lower().split()
        found = any(word in all_columns_text for word in metric_words)
        status = "Present" if found else "Missing"
        print(f"  {metric}: {status}")
    
    print("\nEVALUATION COMPLETE!")
    
except Exception as e:
    print(f"Error: {str(e)}")