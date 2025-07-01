# 🔧 Technical Guide - Land Acquisition Pipeline v2.9.7

## 📊 **Architecture Overview**

### **Processing Flow**
```
Input Excel → Campaign Setup → Municipality Processing → Consolidated Output
     ↓              ↓                    ↓                      ↓
Property Data → API Calls → Owner Enhancement → Single Excel File
```

### **Key Components**
- **Catasto API**: Italian land registry data retrieval
- **Geocoding API**: Address enhancement with ZIP codes
- **PEC API**: Company email lookup
- **Funnel Tracking**: Parcel/hectare flow analysis

## 🔍 **Core Functions**

### **Main Pipeline** (`land_acquisition_pipeline.py`)

#### `run_complete_campaign()` (Line ~1195)
- **Purpose**: Main orchestrator for entire campaign
- **Key Change v2.9.6**: Now generates single consolidated output
- **Input**: Excel file path, campaign name
- **Output**: Single `[Campaign_Name]_Results.xlsx`

#### `create_consolidated_excel_output()` (Line ~1589) 
- **Purpose**: Creates single Excel with all 7 sheets
- **v2.9.7 Enhancement**: Added parcel ownership analysis sheets
- **Sheets**: Raw Data, Validation Ready, Companies, Summary, Funnel, Owners_By_Parcel, Owners_Normalized

#### `create_municipality_summary()` (Line ~819)
- **Purpose**: Generate business metrics per municipality
- **v2.9.6 Fix**: Added CP/comune/provincia traceability columns
- **Key Metrics**: Contact counts, area calculations, success rates

#### `create_funnel_analysis_df()` (Line ~1430)
- **Purpose**: Track parcels/hectares through processing stages
- **v2.9.6 Fix**: Added provincia column for complete traceability
- **Output**: 8 stages from input to final routing

#### `create_owners_by_parcel_sheets()` (Line ~1445) **🆕 v2.9.7**
- **Purpose**: Group all owners by input parcel for complete ownership analysis
- **Key Feature**: Groups by (comune, foglio_input, particella_input) regardless of classamento
- **Output**: Two DataFrames - wide format (user-friendly) and normalized (Power BI ready)
- **Business Value**: Complete ownership database for land acquisition negotiations

### **Critical Fixes Applied (v2.9.6)**

#### **Decimal Formatting** (Lines 1380-1393)
```python
# BEFORE (broken):
funnel_metrics["private_owner_area_ha"] = df['Area'].sum()

# AFTER (fixed):
private_area_df = df.drop_duplicates(subset=['foglio_input', 'particella_input'])
funnel_metrics["private_owner_area_ha"] = pd.to_numeric(
    private_area_df['Area'].astype(str).str.replace(',', '.'), 
    errors='coerce'
).fillna(0).sum()
```

#### **Traceability Columns** (Lines 876-879)
```python
summary_dict = {
    # NEW: Traceability columns
    "CP": municipality_data['CP'],
    "comune": municipality_data['comune'],
    "provincia": municipality_data.get('provincia', ''),
    # ... existing metrics
}
```

## 📈 **Data Flow**

### **Input Processing**
1. **Excel Import**: Property parcels with CP/municipality structure
2. **Structure Analysis**: Group by CP and comune
3. **API Integration**: Retrieve owner data from Catasto

### **Enhancement Pipeline**
1. **Owner Classification**: Private vs Company (CF analysis)
2. **Address Cleaning**: Remove apartment/floor info
3. **Geocoding**: Add ZIP codes and coordinates
4. **PEC Lookup**: Company email retrieval
5. **Quality Classification**: Address confidence scoring

### **Output Generation**
1. **Deduplication**: Unique owners per unique address
2. **Funnel Tracking**: Track at each processing stage
3. **Business Metrics**: Summary calculations
4. **Consolidated Export**: Single Excel with 5 sheets

## 🧪 **Testing & Verification**

### **Verification Tools**
- `simple_campaign_analyzer.py` - Output structure verification
- Built-in logging system with timestamps
- Backup creation before major operations

### **Expected Output Structure**
```
[Campaign_Name]_Results.xlsx
├── All_Raw_Data (128 rows typical)
├── All_Validation_Ready (23 rows typical)  
├── All_Companies_Found (0-N rows)
├── Campaign_Summary (5 rows = municipalities)
├── Funnel_Analysis (40 rows = 8 stages × 5 municipalities)
├── 🆕 Owners_By_Parcel (10 rows = unique parcels with up to 10 owners each)
└── 🆕 Owners_Normalized (128 rows = one row per owner-parcel relationship)
```

### **Key Validation Points**
- All 7 sheets present (including new ownership analysis sheets)
- Campaign_Summary has CP/comune/provincia columns
- Area values realistic (10-50 Ha typical, not 100,000+)
- Unique_Owner_Address_Pairs > 0
- Funnel_Analysis has provincia column
- **🆕 Owners_By_Parcel**: Shows complete ownership per input parcel
- **🆕 Owners_Normalized**: One row per owner-parcel relationship (Power BI ready)

## ⚙️ **Configuration**

### **API Settings** (`land_acquisition_config.json`)
```json
{
  "api_settings": {"token": "CATASTO_TOKEN"},
  "geocoding_settings": {"enabled": true, "token": "GEO_TOKEN"},
  "pec_integration": {"enabled": true, "token": "PEC_TOKEN"}
}
```

### **Performance Tuning**
- `sleep_between_calls`: API rate limiting (default: 2 seconds)
- `timeout_recovery`: Automatic retry for failed requests
- `cache_directory`: Persistent API response caching

## 🔄 **Error Handling**

### **Automatic Recovery Systems**
- **API Timeouts**: Saved for later recovery attempts
- **Geocoding Failures**: Graceful degradation with partial data
- **Missing Data**: Empty sheets created with proper structure

### **Logging & Debugging**
- Comprehensive logging in `logs/` directory
- Cache files in `cache/` for API response persistence
- Backup files created before major operations

## 🚨 **Critical Code Sections**

### **DO NOT MODIFY** (unless specifically requested)
- Decimal formatting logic (lines 1380-1393) - just fixed
- Consolidated output structure (lines 1445-1475) - working correctly
- Traceability column logic (lines 876-879) - properly implemented

### **Safe to Enhance**
- Additional business metrics
- New output formats
- Performance optimizations
- Extended API integrations

---

**💡 This technical guide covers the current v2.9.6 stable implementation. All critical issues have been resolved and the system is production-ready.**