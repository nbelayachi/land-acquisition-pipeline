# 🔧 Technical Reference - Land Acquisition Pipeline
## **Implementation Details & Function Guide**

---

## 🏗️ **SYSTEM ARCHITECTURE**

### **Core Technology**
- **Language**: Python 3.7+ 
- **Key Libraries**: pandas, requests, openpyxl, numpy
- **APIs**: Italian Catasto, Geocoding, PEC Email
- **Output**: Excel (10 sheets) + PowerBI CSV

### **Processing Flow**
```
Input Excel → API Processing → Enhancement → Quality Assessment → Output Generation
     ↓             ↓              ↓              ↓                    ↓
10 parcels    128 owner records   23 addresses   Quality routing    Consolidated Excel
56.9 ha       13 unique owners    100% geocoded  4-tier classification  + PowerBI CSV
```

---

## 📊 **OUTPUT STRUCTURE (v3.1.5)**

### **Excel File: `[Campaign_Name]_Results.xlsx`**
**10 Sheets Generated**:

1. **All_Raw_Data** - Complete property ownership records
2. **All_Validation_Ready** - Processed contacts with geocoding
3. **Final_Mailing_List** - Strategic mailing list, now including `cf`, `Addresses_Per_Owner`, and `Address_Sequence` columns, sorted by owner.
4. **All_Companies_Found** - Corporate owners with PEC emails
5. **Campaign_Summary** - Municipality-level business metrics
6. **Enhanced_Funnel_Analysis** - Dual pipeline metrics with business-friendly labels, including `Stage_Conversion_Rate`.
7. **Address_Quality_Distribution** - Quality intelligence breakdown with corrected rounding
8. **Owners_By_Parcel** - Complete ownership per parcel
9. **Owners_Normalized** - PowerBI-ready ownership data
10. **Campaign_Scorecard** - Executive summary

### **CSV Export: `PowerBI_Dataset.csv`**
- Municipality-level metrics for dashboard integration

---

## 🔧 **CORE FUNCTIONS**

### **Campaign Launcher (Modernized v3.1.5)**
```python
LandAcquisitionCampaignLauncher.run()
```
- **Purpose**: Streamlined campaign setup and configuration
- **Features**: Input file selection, analysis preview, configuration generation
- **Improvements**: Reduced from 669 to 285 lines, focused on v3.1.5 features
- **Location**: `campaign_launcher.py`

### **Main Pipeline Entry Point**
```python
run_complete_campaign(excel_file_path, campaign_name)
```
- **Purpose**: Main orchestrator for entire campaign
- **Input**: Excel file path, campaign name
- **Output**: Single consolidated Excel file
- **Location**: Line ~1195 in `land_acquisition_pipeline.py`

### **Data Processing Functions**

#### **`create_consolidated_excel_output()`** (Line ~1589)
- **Purpose**: Generates final Excel with all 10 sheets
- **Enhanced Features**: Funnel analysis, quality distribution, PowerBI export

#### **`create_funnel_analysis_df()`** (Line ~1430)
- **Purpose**: Creates a dual funnel analysis (Land Acquisition + Contact Processing) with business-friendly labels and metrics.
- **Output**: A DataFrame with `Conversion / Multiplier`, `Retention_Rate`, `Stage_Conversion_Rate`, business rules, and process notes for each stage.
- **v3.1.3 Update**: Refined `Retention_Rate` calculation for Contact Processing funnel to be relative to "Owner Discovery" count. Added new `Stage_Conversion_Rate` column for step-wise efficiency.

#### **`create_quality_distribution_df()`** 
- **Purpose**: Analyzes address quality and generates a distribution summary.
- **Classification**: ULTRA_HIGH, HIGH, MEDIUM, LOW confidence levels.
- **v3.1.1 Update**: Implemented a corrected rounding logic to ensure the sum of percentages is always exactly 100.0%.

#### **`calculate_executive_kpis()`**
- **Purpose**: Computes executive-level KPIs from the enhanced funnel data.
- **v3.1.2 Fix**: Updated the function to use the new business-friendly stage names from the `Enhanced_Funnel_Analysis` sheet, resolving a critical bug that caused the pipeline to fail.

### **Address Enhancement Functions**

#### **`classify_address_quality_enhanced()`**
- **Purpose**: 4-tier address confidence assessment
- **Logic**: Compares original vs geocoded data, assigns confidence score
- **v3.1.4 Update**: Refined logic to elevate certain `MEDIUM` confidence addresses to `HIGH` confidence if they are considered deliverable by the business (e.g., original address is reliable despite geocoding nuances).

#### **`extract_street_number_enhanced()`**
- **Purpose**: Conservative street number extraction from addresses

---

## 🧪 **VALIDATION & TESTING**

### **`validate_campaign_metrics.py`**
- **Purpose**: A dedicated script (`dev_tools/testing/validate_campaign_metrics.py`) to perform automated checks on the generated Excel output.
- **Checks Performed**:
    - Verifies that the sum of percentages in `Address_Quality_Distribution` is exactly 100%.
    - Confirms that the total counts in `Address_Quality_Distribution` match the number of rows in `All_Validation_Ready`.
    - Validates the `Owner Discovery Multiplier` and `Address Expansion Multiplier` calculations in `Enhanced_Funnel_Analysis`.
    - Ensures consistency between summary metrics in `Campaign_Summary` and detailed data in `All_Validation_Ready`.
- **Usage**: Run this script with a completed campaign Excel file to quickly verify metric accuracy and consistency.

---

## 📚 **ADDITIONAL DOCUMENTATION**

*   **`METRICS_GUIDE.md`**: A comprehensive guide detailing every metric across `Enhanced_Funnel_Analysis`, `Address_Quality_Distribution`, and `Campaign_Summary`. Includes business rationale, calculation details, and real-world examples.

---

**📊 Document Status**: ✅ **Technical Reference Complete**  
**🎯 Audience**: Developers and technical agents  
**📅 Last Updated**: 2025-07-06  
**🔄 Update Trigger**: When functions, APIs, or output structure changes
