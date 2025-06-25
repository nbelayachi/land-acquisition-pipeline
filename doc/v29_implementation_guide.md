# Land Acquisition Pipeline v2.9 - Code Implementation Guide

**Purpose**: This document provides targeted code changes needed to implement v2.9 enhancements.  
**Scope**: Only code modifications required - documentation is already updated.  
**Priority**: Implement in the order listed below.

---

## 📝 Summary of v2.9 Changes

1. **SNC Reclassification**: Route SNC addresses to DIRECT_MAIL (HIGH confidence)
2. **Funnel Metrics**: Track parcels and hectares through each processing stage
3. **Company Integration**: Separate tracking while including in totals
4. **Future**: Single file output structure (design only, not implement)

---

## 🔧 Code Changes Required

### File: `land_acquisition_pipeline.py`

#### Change 1: SNC Address Classification
**Location**: Function `classify_address_quality()` around line 1653

**Current Code**:
```python
if 'SNC' in original.upper():
    return {
        'Address_Confidence': 'LOW',
        'Routing_Channel': 'AGENCY',
        'Quality_Notes': 'SNC (no street number) - requires agency'
    }
```

**New Code**:
```python
if 'SNC' in original.upper():
    return {
        'Address_Confidence': 'HIGH',
        'Routing_Channel': 'DIRECT_MAIL',
        'Quality_Notes': 'SNC address - small street known to postal service'
    }
```

**Rationale**: Land Acquisition Manager confirmed postal service knows these small streets well.

---

#### Change 2: Add Funnel Tracking Variables
**Location**: Function `process_municipality()` around line 2100

**Add these tracking variables at the start of the function**:
```python
# Initialize funnel tracking
funnel_metrics = {
    "input_parcels": len(df),
    "input_area_ha": df['Area'].astype(float).sum(),
    "after_api_parcels": 0,
    "after_api_area_ha": 0.0,
    "private_owner_parcels": 0,
    "private_owner_area_ha": 0.0,
    "company_owner_parcels": 0,
    "company_owner_area_ha": 0.0,
    "after_cata_filter_parcels": 0,
    "after_cata_filter_area_ha": 0.0,
    "unique_contacts": 0,
    "direct_mail_contacts": 0,
    "direct_mail_area_ha": 0.0,
    "agency_contacts": 0,
    "agency_area_ha": 0.0
}
```

---

#### Change 3: Track Metrics Throughout Processing
**Location**: Throughout `process_municipality()` function

**After successful API calls** (around line 2120):
```python
if results and not all(r['denominazione'] in ['Timeout', 'No Data'] or 'Error' in r['denominazione'] for r in results):
    funnel_metrics["after_api_parcels"] += 1
    funnel_metrics["after_api_area_ha"] += float(row.get('Area', 0))
```

**After owner classification** (around line 2180):
```python
# When creating df_raw
if 'Tipo_Proprietario' in df_raw.columns:
    private_mask = df_raw['Tipo_Proprietario'] == 'Privato'
    company_mask = df_raw['Tipo_Proprietario'] == 'Azienda'
    
    # Count unique parcels by owner type
    private_parcels = df_raw[private_mask][['foglio_input', 'particella_input']].drop_duplicates()
    company_parcels = df_raw[company_mask][['foglio_input', 'particella_input']].drop_duplicates()
    
    funnel_metrics["private_owner_parcels"] = len(private_parcels)
    funnel_metrics["company_owner_parcels"] = len(company_parcels)
    
    # Sum area (avoiding double counting)
    for _, parcel in private_parcels.iterrows():
        area = municipality_data['dataframe'][
            (municipality_data['dataframe']['foglio'] == parcel['foglio_input']) & 
            (municipality_data['dataframe']['particella'] == parcel['particella_input'])
        ]['Area'].iloc[0] if len(municipality_data['dataframe']) > 0 else 0
        funnel_metrics["private_owner_area_ha"] += float(area)
```

**After Cat.A filtering** (around line 2200):
```python
# After creating individuals_cat_a
if not individuals_cat_a.empty:
    cat_a_parcels = individuals_cat_a[['foglio_input', 'particella_input']].drop_duplicates()
    funnel_metrics["after_cata_filter_parcels"] = len(cat_a_parcels)
    
    # Calculate area for Cat.A filtered parcels
    for _, parcel in cat_a_parcels.iterrows():
        area = municipality_data['dataframe'][
            (municipality_data['dataframe']['foglio'] == parcel['foglio_input']) & 
            (municipality_data['dataframe']['particella'] == parcel['particella_input'])
        ]['Area'].iloc[0] if len(municipality_data['dataframe']) > 0 else 0
        funnel_metrics["after_cata_filter_area_ha"] += float(area)
```

**After final deduplication** (around line 2250):
```python
# After creating validation_ready
if not validation_ready.empty:
    funnel_metrics["unique_contacts"] = len(validation_ready)
    
    if 'Routing_Channel' in validation_ready.columns:
        direct_mail_df = validation_ready[validation_ready['Routing_Channel'] == 'DIRECT_MAIL']
        agency_df = validation_ready[validation_ready['Routing_Channel'] == 'AGENCY']
        
        funnel_metrics["direct_mail_contacts"] = len(direct_mail_df)
        funnel_metrics["agency_contacts"] = len(agency_df)
        
        if 'Area' in validation_ready.columns:
            funnel_metrics["direct_mail_area_ha"] = direct_mail_df['Area'].astype(float).sum()
            funnel_metrics["agency_area_ha"] = agency_df['Area'].astype(float).sum()
```

---

#### Change 4: Update Municipality Summary
**Location**: Function `create_municipality_summary()` around line 1850

**Add funnel metrics to the returned dictionary**:
```python
def create_municipality_summary(self, municipality_key, municipality_data, df_raw, 
                               validation_ready, companies_found=None, funnel_metrics=None):
    # ... existing code ...
    
    # Add funnel metrics to summary
    summary_dict = {
        # ... existing metrics ...
        
        # NEW: Funnel Metrics
        "Input_Parcels": funnel_metrics.get("input_parcels", 0) if funnel_metrics else 0,
        "Input_Area_Ha": funnel_metrics.get("input_area_ha", 0) if funnel_metrics else 0,
        "After_API_Parcels": funnel_metrics.get("after_api_parcels", 0) if funnel_metrics else 0,
        "After_API_Area_Ha": funnel_metrics.get("after_api_area_ha", 0) if funnel_metrics else 0,
        "Private_Owner_Parcels": funnel_metrics.get("private_owner_parcels", 0) if funnel_metrics else 0,
        "Private_Owner_Area_Ha": funnel_metrics.get("private_owner_area_ha", 0) if funnel_metrics else 0,
        "Company_Owner_Parcels": funnel_metrics.get("company_owner_parcels", 0) if funnel_metrics else 0,
        "Company_Owner_Area_Ha": funnel_metrics.get("company_owner_area_ha", 0) if funnel_metrics else 0,
        "After_CatA_Filter_Parcels": funnel_metrics.get("after_cata_filter_parcels", 0) if funnel_metrics else 0,
        "After_CatA_Filter_Area_Ha": funnel_metrics.get("after_cata_filter_area_ha", 0) if funnel_metrics else 0,
        "Unique_Contacts_Generated": funnel_metrics.get("unique_contacts", 0) if funnel_metrics else 0,
        "Direct_Mail_Final_Contacts": funnel_metrics.get("direct_mail_contacts", 0) if funnel_metrics else 0,
        "Direct_Mail_Final_Area_Ha": funnel_metrics.get("direct_mail_area_ha", 0) if funnel_metrics else 0,
        "Agency_Final_Contacts": funnel_metrics.get("agency_contacts", 0) if funnel_metrics else 0,
        "Agency_Final_Area_Ha": funnel_metrics.get("agency_area_ha", 0) if funnel_metrics else 0,
    }
    
    return summary_dict
```

---

#### Change 5: Pass Funnel Metrics to Summary
**Location**: In `create_municipality_output()` around line 2300

**Update the call to create_municipality_summary**:
```python
# When calling create_municipality_summary, pass funnel_metrics
summary_data = self.create_municipality_summary(
    municipality_key, 
    municipality_data, 
    df_raw, 
    validation_ready, 
    companies_found,
    funnel_metrics  # NEW parameter
)
```

---

#### Change 6: Update PowerBI Export
**Location**: Function `create_powerbi_export()` around line 900

**Add funnel metrics to PowerBI dataset**:
```python
# In the municipality_record dictionary, add:
"Input_Parcels": summary_metrics.get("Input_Parcels", 0),
"Input_Area_Ha": summary_metrics.get("Input_Area_Ha", 0),
"After_API_Parcels": summary_metrics.get("After_API_Parcels", 0),
"After_API_Area_Ha": summary_metrics.get("After_API_Area_Ha", 0),
"Private_Owner_Parcels": summary_metrics.get("Private_Owner_Parcels", 0),
"Private_Owner_Area_Ha": summary_metrics.get("Private_Owner_Area_Ha", 0),
"Company_Owner_Parcels": summary_metrics.get("Company_Owner_Parcels", 0),
"Company_Owner_Area_Ha": summary_metrics.get("Company_Owner_Area_Ha", 0),
"After_CatA_Filter_Parcels": summary_metrics.get("After_CatA_Filter_Parcels", 0),
"After_CatA_Filter_Area_Ha": summary_metrics.get("After_CatA_Filter_Area_Ha", 0),
"Unique_Contacts_Generated": summary_metrics.get("Unique_Contacts_Generated", 0),
"Direct_Mail_Final_Contacts": summary_metrics.get("Direct_Mail_Final_Contacts", 0),
"Direct_Mail_Final_Area_Ha": summary_metrics.get("Direct_Mail_Final_Area_Ha", 0),
"Agency_Final_Contacts": summary_metrics.get("Agency_Final_Contacts", 0),
"Agency_Final_Area_Ha": summary_metrics.get("Agency_Final_Area_Ha", 0),
```

---

#### Change 7: Add Funnel Sheet to Excel Output
**Location**: In `create_municipality_output()` around line 2350

**Add a new sheet with funnel visualization**:
```python
# After writing existing sheets, add:
if funnel_metrics:
    funnel_df = pd.DataFrame([
        {"Stage": "1. Input", "Parcels": funnel_metrics["input_parcels"], 
         "Hectares": funnel_metrics["input_area_ha"], "Description": "Initial parcels from input file"},
        {"Stage": "2. After API", "Parcels": funnel_metrics["after_api_parcels"], 
         "Hectares": funnel_metrics["after_api_area_ha"], "Description": "Parcels with owner data retrieved"},
        {"Stage": "3. Private Owners", "Parcels": funnel_metrics["private_owner_parcels"], 
         "Hectares": funnel_metrics["private_owner_area_ha"], "Description": "Individual owner parcels"},
        {"Stage": "4. Company Owners", "Parcels": funnel_metrics["company_owner_parcels"], 
         "Hectares": funnel_metrics["company_owner_area_ha"], "Description": "Company-owned parcels (bypass Cat.A)"},
        {"Stage": "5. After Cat.A Filter", "Parcels": funnel_metrics["after_cata_filter_parcels"], 
         "Hectares": funnel_metrics["after_cata_filter_area_ha"], "Description": "Residential properties only"},
        {"Stage": "6. Unique Contacts", "Parcels": "-", 
         "Hectares": "-", "Description": f"{funnel_metrics['unique_contacts']} deduplicated contacts"},
        {"Stage": "7. Direct Mail", "Parcels": "-", 
         "Hectares": funnel_metrics["direct_mail_area_ha"], 
         "Description": f"{funnel_metrics['direct_mail_contacts']} contacts via direct mail"},
        {"Stage": "8. Agency Required", "Parcels": "-", 
         "Hectares": funnel_metrics["agency_area_ha"], 
         "Description": f"{funnel_metrics['agency_contacts']} contacts via agency"},
    ])
    funnel_df.to_excel(writer, sheet_name='Funnel_Analysis', index=False)
```

---

### File: `campaign_launcher.py`

No changes required for v2.9 implementation. Future v2.9.x will update this for single file output.

---

## 📋 Testing Checklist

After implementing these changes:

1. [ ] Test with a campaign containing SNC addresses
2. [ ] Verify SNC routes to DIRECT_MAIL with HIGH confidence
3. [ ] Check funnel metrics calculation at each stage
4. [ ] Ensure area calculations don't double-count parcels
5. [ ] Verify company parcels bypass Cat.A but appear in metrics
6. [ ] Confirm Municipality_Summary shows all new metrics
7. [ ] Check PowerBI_Dataset.csv includes funnel columns
8. [ ] Validate Funnel_Analysis sheet in output Excel

---

## 🎯 Expected Impact

- **Direct Mail Rate**: Should increase from ~40% to 50%+ due to SNC reclassification
- **Funnel Visibility**: Management can see exactly where parcels/hectares are filtered
- **Company Tracking**: Clear separation between B2B and B2C opportunities
- **Cost Reduction**: ~€0.05-0.10 savings per SNC contact

---

## 🚀 Next Steps After Implementation

1. Run test campaigns to validate metrics
2. Update any affected unit tests
3. Brief team on SNC routing change
4. Start designing single file output structure (v2.9.x)
5. Begin Power BI dashboard development using new funnel metrics