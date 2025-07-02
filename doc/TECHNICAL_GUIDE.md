# Technical Guide - Land Acquisition Pipeline v3.1.0

This document provides a technical overview of the `land_acquisition_pipeline.py` script with enhanced funnel analytics and executive KPIs.

## Core Functions

### `create_consolidated_excel_output()`
This is the final function in the pipeline, responsible for generating the consolidated multi-sheet Excel report with enhanced funnel analytics.

**Enhanced Funnel Analysis Generation**:
1. **Campaign-Level Aggregation**: Aggregates metrics from `df_campaign_summary` across all municipalities
2. **Dual Funnel Creation**: Calls `create_funnel_analysis_df()` with aggregated data to generate dual funnel structure
3. **Quality Distribution Analysis**: Creates `create_quality_distribution_df()` for automation metrics
4. **Executive KPI Calculation**: Computes land efficiency, contact multiplication, and zero-touch processing rates

**Strategic Mailing List Generation**:
1. Identifies all high-confidence mailing addresses for owners from the `df_all_validation_ready` DataFrame
2. Creates a lookup map linking each owner's `cf` to their list of valid addresses
3. Groups the `df_all_raw` data by owner (`cf`) within each municipality to aggregate all parcels belonging to that owner
4. Iterates through these groups, creating a row for each valid mailing address for each owner

### `create_funnel_analysis_df()`
**v3.1.0**: Creates enhanced dual funnel analysis with conversion rates and business intelligence.

**Land Acquisition Pipeline (4 stages)**:
1. **Input Parcels**: User-selected parcels for analysis
2. **API Data Retrieved**: Parcels with successful ownership data retrieval
3. **Private Owners Only**: Filtered to exclude company owners
4. **Category A Filter**: Residential properties only

**Contact Processing Pipeline (5 stages)**:
1. **Owners Identified**: Unique owners from qualified parcels
2. **Address Pairs Created**: Address expansion (multiple addresses per owner)
3. **Geocoding Completed**: All addresses geocoded and quality assessed
4. **Direct Mail Ready**: High confidence addresses for direct mailing
5. **Agency Required**: Low confidence addresses requiring investigation

Each stage includes conversion rates, retention rates, business rules, automation levels, and process notes.

### `create_quality_distribution_df()`
Analyzes address quality distribution with automation metrics:
- **ULTRA_HIGH**: Zero-touch processing (17.4% typical)
- **HIGH**: Quick review required
- **MEDIUM**: Standard manual processing
- **LOW**: Agency investigation required

### `calculate_executive_kpis()`
Computes executive-level KPIs from enhanced funnel data:
- **Land Acquisition Efficiency**: % of input parcels retained (80% typical)
- **Contact Multiplication Factor**: Addresses per qualified parcel (2.9x typical)
- **Direct Mail Efficiency**: % of addresses ready for direct mail (52.2% typical)
- **Zero-Touch Processing Rate**: % requiring no manual review (17.4% typical)

### `classify_address_quality_enhanced()`
This function assesses the quality of a mailing address by comparing the original data with the results from the geocoding API. It analyzes street number similarity and the completeness of the geocoded data to assign a confidence score (`ULTRA_HIGH`, `HIGH`, `MEDIUM`, `LOW`) and a recommended `Routing_Channel` (`DIRECT_MAIL` or `AGENCY`).

### `extract_street_number_enhanced()`
This helper function uses regular expressions to extract a street number from an address string. The patterns have been refined to be more conservative, now prioritizing numbers at the very end of a string or those explicitly marked with "n.". This prevents the logic from incorrectly extracting numbers that are part of a street's proper name (e.g., the "4" in "Via 4 Novembre").

## Output File Structure
The script generates a single `.xlsx` file containing 10 enhanced sheets:

### **Enhanced Analytics Sheets (v3.1.0)**
- **`Enhanced_Funnel_Analysis`**: Dual funnel with conversion rates, business rules, and automation levels
  - Columns: `Funnel_Type`, `Stage`, `Count`, `Hectares`, `Conversion_Rate`, `Retention_Rate`, `Business_Rule`, `Automation_Level`, `Process_Notes`, `CP`, `comune`, `provincia`
- **`Address_Quality_Distribution`**: Quality analysis with automation metrics
  - Columns: `Quality_Level`, `Count`, `Percentage`, `Processing_Type`, `Business_Value`, `Automation_Level`, `Routing_Decision`, `CP`, `comune`, `provincia`

### **Primary Output Sheets**
- **`Final_Mailing_List`**: Strategic mailing list grouped by input parcels with high-confidence addresses
  - Columns: `Municipality`, `Foglio`, `Particella`, `Parcels`, `Full_Name`, `Mailing_Address`
- **`All_Validation_Ready`**: Contains all individual owners of residential properties with detailed address analysis
- **`All_Companies_Found`**: Lists all company owners with their retrieved PEC emails
- **`Campaign_Summary`**: Business metrics by municipality with enhanced KPI integration
- **`All_Raw_Data`**: Complete raw property owner data

### **Analysis Sheets**
- **`Owners_By_Parcel`**: Complete ownership per parcel (user-friendly format)
- **`Owners_Normalized`**: Power BI ready ownership data
- **`Campaign_Scorecard`**: High-level executive summary

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