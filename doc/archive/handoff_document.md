# Handoff Document: Land Acquisition Pipeline Project

## Project Overview

The Land Acquisition Pipeline is a Python-based command-line interface (CLI) tool designed to automate and streamline the process of obtaining landowner data and generating key metrics for land acquisition campaigns. It integrates with external APIs for cadastral data retrieval, geocoding, and PEC email lookup. The pipeline processes input data, enhances addresses, classifies address quality, and produces detailed output reports for analysis and decision-making.

## Version History and Key Enhancements (v2.9 to v2.9.5)

This project has undergone significant development and refinement, particularly in versions 2.9 through 2.9.5, focusing on improving data accuracy, output clarity, and usability.

### v2.9 (Initial State)
- Introduced geocoding enhancement and PEC email integration.
- Implemented initial funnel tracking for parcels and hectares.
- **Known Issue**: Documentation was out of sync with the actual code.

### v2.9.1 (Critical Bug Fixes)
- **Resolved Data Loss**: Fixed a critical bug where valid parcels were being dropped from the `Validation_Ready` sheet due to overly aggressive deduplication. The deduplication logic now considers `foglio_input` and `particella_input` to preserve unique parcels.
- **Improved Geocoding Validation**: Introduced a province-matching sanity check (`is_province_match`) to prevent incorrect geocoding results from being classified with high confidence.

### v2.9.2 (Business Logic & Metric Refinement)
- **SNC Address Reclassification**: Based on updated business rules, "SNC" addresses are now classified as `MEDIUM` confidence and routed to `AGENCY` (previously `HIGH` and `DIRECT_MAIL`). This ensures manual review for these addresses.
- **Revised Summary Metrics**: Overhauled the `create_municipality_summary` function to provide accurate, de-duplicated counts for contacts and area.
    - `Direct_Mail_Final_Contacts` and `Agency_Final_Contacts` now count unique owners (`cf`).
    - `Direct_Mail_Final_Area_Ha` and `Agency_Final_Area_Ha` now sum area of unique parcels (`foglio_input`, `particella_input`).
    - Renamed `Unique_Contacts_Generated` to `Unique_Owner_Address_Pairs` for clarity.
    - Removed `Hectares_Agency_Required` metric.

### v2.9.3 (Funnel Consistency)
- Ensured the `funnel_metrics` calculations within `create_municipality_output` used the same de-duplicated area logic as the main summary, resolving inconsistencies.

### v2.9.4 (Final Funnel Synchronization)
- Synchronized the `Funnel_Analysis` sheet generation to directly use the corrected metrics from the `Municipality_Summary`, guaranteeing consistency between the two reports.

### v2.9.5 (Single Consolidated Output File)
- **Major Architectural Change**: The pipeline now generates a single Excel file (`[Campaign_Name]_Results.xlsx`) per campaign, replacing the previous complex folder structure with individual municipality files.
- **Consolidated Sheets**: The single Excel file contains the following sheets:
    - `All_Raw_Data`: All raw data from all municipalities.
    - `All_Validation_Ready`: All validation-ready contacts from all municipalities, with `CP` and `comune` for traceability.
    - `All_Companies_Found`: All company data from all municipalities, with `CP` and `comune`.
    - `Campaign_Summary`: A summary where each row represents a municipality, providing an overview of key metrics.
    - `Funnel_Analysis`: A consolidated funnel analysis for all municipalities, stacked vertically, with `CP` and `comune` for each stage.
- **Removed**: Individual municipality folders and Excel files.

## Current Code Status (v2.9.5)

**✅ VERIFIED - June 30, 2025**: The v2.9.5 single-file output architecture is working and generating consolidated Excel files. A successful campaign run has been completed and analyzed.

**⚠️ KNOWN ISSUES IDENTIFIED**:
Based on analysis of actual campaign output (`LandAcquisition_Casalpusterlengo_Castiglione_20250630_1824_Results.xlsx`):

### High Priority Issues:
1. **Missing `All_Companies_Found` Sheet**: Expected sheet is completely absent from output
2. **Campaign_Summary Missing Traceability**: No `CP`, `comune`, `provincia` columns to identify municipalities per row
3. **Decimal/Comma Formatting Issues**: Critical area calculations showing nonsense numbers
   - `Private_Owner_Area_Ha`: Likely comma/decimal confusion causing wrong hectare values
   - `After_CatA_Filter_Area_Ha`: Same decimal formatting issue
   - `Funnel_Analysis` hectares: Incorrect decimal calculations throughout funnel
   - **Impact**: Business decisions based on wrong land area calculations

### Medium Priority Issues:
4. **Broken Metric**: `Unique_Owner_Address_Pairs` showing 0 total across all municipalities
5. **Missing Column**: `provincia` column missing from `Funnel_Analysis` sheet

### Minor Issues:
6. **Municipality Name Inconsistency**: "Castiglione" vs "Castiglione Delle Stiviere" in different sheets

**Current Working Structure**:
- ✅ Single consolidated Excel file generation
- ✅ 4 of 5 expected sheets present
- ✅ Data flow and processing working
- ✅ Funnel tracking implemented
- ✅ Traceability working in most sheets (All_Raw_Data, All_Validation_Ready, Funnel_Analysis)

## Current v2.9.5 Actual Structure Analysis

**✅ COMPLETED - June 30, 2025**: Comprehensive analysis performed on actual campaign output.

### Actual Sheet Structure Found:
1. **`All_Validation_Ready`** ✅ **WORKING**
   - 23 rows, 52 columns
   - ✅ Contains `CP`, `comune`, `provincia` traceability
   - ✅ Address confidence and routing working: 12 DIRECT_MAIL, 11 AGENCY
   - ✅ All required columns present

2. **`Campaign_Summary`** ❌ **MULTIPLE ISSUES**
   - 5 rows, 24 columns (one per municipality expected)
   - ❌ Missing `CP`, `comune`, `provincia` columns
   - ❌ Broken metrics: `Unique_Owner_Address_Pairs` = 0
   - ❌ **CRITICAL**: Area calculations broken due to decimal/comma formatting
     - `Private_Owner_Area_Ha`: Nonsense values from decimal errors
     - `After_CatA_Filter_Area_Ha`: Wrong hectare calculations
   - ✅ Contact counts working: 9 Direct Mail, 3 Agency contacts

3. **`Funnel_Analysis`** ⚠️ **PARTIAL ISSUES**
   - 40 rows, 6 columns
   - ✅ Contains `CP`, `comune` traceability
   - ❌ Missing `provincia` column
   - ✅ Parcel counts working properly
   - ❌ **CRITICAL**: Hectares calculations broken (decimal formatting issues)

4. **`All_Raw_Data`** ✅ **WORKING**
   - 128 rows, 29 columns
   - ✅ Complete traceability with `CP`, `comune`, `provincia`
   - ✅ Owner classification working

5. **`All_Companies_Found`** ❌ **MISSING**
   - Expected sheet completely absent
   - Should contain company data with PEC emails

## Review Checklist for New Agent

**IMMEDIATE ACTIONS REQUIRED**:

1. **Fix Critical High Priority Issues**:
   - **URGENT**: Fix decimal/comma formatting in area calculations (wrong business data)
   - Implement missing `All_Companies_Found` sheet generation
   - Add `CP`, `comune`, `provincia` columns to `Campaign_Summary` sheet
   
2. **Fix Medium Priority Issues**:
   - Debug `Unique_Owner_Address_Pairs` metric calculation (currently showing 0)
   - Add `provincia` column to `Funnel_Analysis` sheet

3. **Review Codebase Focus Areas**:
   - **Critical**: Area calculation functions - decimal/comma handling throughout pipeline
   - `create_consolidated_excel_output` function (missing companies sheet logic)
   - `create_municipality_summary` function (missing traceability columns + decimal fixes)
   - `create_funnel_analysis_df` function (hectares decimal formatting)
   - Company processing and PEC integration pipeline

## Next Steps / Future Features

The user has indicated that there are other features needed beyond the output structure. Once the current version (v2.9.5) is fully verified, the new agent should engage with the user to understand and plan these next features.

---
*This document was automatically generated by the Gemini CLI agent.*
