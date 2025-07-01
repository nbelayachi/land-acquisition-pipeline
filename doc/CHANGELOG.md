# 📋 Changelog - Land Acquisition Pipeline

## [2.9.7] - 2025-07-01 🆕 PARCEL OWNERSHIP FEATURE

### ✨ **New Features**
- **Complete Parcel Ownership Analysis**: Groups all owners by input parcel (comune + foglio_input + particella_input)
- **Owners_By_Parcel Sheet**: User-friendly wide format showing up to 10 owners per parcel
- **Owners_Normalized Sheet**: Power BI ready format with one row per owner-parcel relationship
- **Quota Preservation**: Maintains ownership fractions/percentages from original data
- **Cross-Classamento Analysis**: Shows ALL owners regardless of property type (Cat.A, Cat.C, etc.)

### 🔧 **Technical Implementation**
- Added `create_owners_by_parcel_sheets()` function (line 1445)
- Modified `create_consolidated_excel_output()` to include new sheets
- Enhanced output from 5 to 7 Excel sheets
- Robust owner deduplication and grouping logic
- Sorting by municipality and owner count for easy analysis

### 📊 **Business Value**
- **Complete Ownership Database**: Know all stakeholders before negotiations
- **Co-ownership Analysis**: Identify complex ownership situations  
- **Power BI Integration**: Ready for advanced analytics and visualizations
- **Strategic Planning**: Prioritize parcels by ownership complexity

### 🎯 **User Request Fulfilled**
> "Group the owners data by parcel to have a complete dataset of the different owners per parcel, regardless of the classamento. The objective is to have all the landowners of the parcel."

**Status**: ✅ **IMPLEMENTED** - Ready for production use

---

## [2.9.6] - 2025-07-01 ✅ STABLE

### 🔧 Fixed (Critical Issues Resolved)
- **Decimal/Comma Formatting**: Fixed area calculations showing nonsense values
  - `Private_Owner_Area_Ha`, `Company_Owner_Area_Ha`, `After_CatA_Filter_Area_Ha`
  - Funnel_Analysis hectare calculations
- **Missing Traceability**: Added `CP`, `comune`, `provincia` columns to Campaign_Summary sheet
- **Broken Metric**: Fixed `Unique_Owner_Address_Pairs` showing 0 instead of actual count
- **Missing Column**: Added `provincia` column to Funnel_Analysis sheet  
- **Missing Sheet**: Ensured All_Companies_Found sheet always created (even if empty)

### ✅ Verified Working
- Single consolidated Excel output per campaign
- All 5 expected sheets generated correctly
- Realistic area calculations (11.39 Ha average verified)
- Complete traceability across all sheets
- Proper funnel tracking with 40 rows of analysis

---

## [2.9.5] - 2025-06-30 (Had Issues - Fixed in 2.9.6)

### 🆕 Added
- **Major**: Single consolidated Excel file output architecture
- Consolidated sheets: All_Raw_Data, All_Validation_Ready, All_Companies_Found, Campaign_Summary, Funnel_Analysis
- Removed individual municipality folder structure

### ⚠️ Issues (Fixed in 2.9.6)
- Missing All_Companies_Found sheet in some cases
- Campaign_Summary missing traceability columns
- Decimal formatting causing wrong area calculations
- Broken Unique_Owner_Address_Pairs metric

---

## [2.9.0-2.9.4] - 2025-06-26 to 2025-06-30

### Key Features Introduced
- **SNC Address Reclassification**: SNC addresses routed to DIRECT_MAIL
- **Funnel Tracking**: Complete parcel and hectare flow analysis
- **PEC Email Integration**: Automatic company email lookup
- **Address Quality Intelligence**: Smart routing based on address confidence
- **Enhanced Geocoding**: ZIP codes and 17+ geographic fields
- **Deduplication Logic**: 93% contact reduction while preserving unique parcels

### Business Impact
- Cost savings: €0.50+ per contact through smart routing
- Improved coverage: SNC addresses now viable for direct mail
- Complete visibility: Management can track entire acquisition funnel
- B2B opportunities: 100% company reachability via PEC emails

---

## [2.8.0 and Earlier] - 2025-06 and before

### Foundation Features
- Core Italian Land Registry (Catasto) API integration
- Property owner data retrieval and processing
- Address cleaning and enhancement
- Municipality-based processing structure
- Timeout recovery system
- Cost tracking and reporting
- OneDrive sync capability

---

## 🎯 **Current Status: PRODUCTION READY**

v2.9.6 represents a stable, fully-tested version with all critical issues resolved. All major features working correctly with verified output structure.