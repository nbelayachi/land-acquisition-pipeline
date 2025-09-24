
# 📊 Dashboard Metrics Manual Validation Tutorial (Excel)

## 🎯 OVERVIEW
This tutorial provides step-by-step instructions to manually validate each dashboard metric using Excel filters and calculations. Each metric includes intermediate validation steps to ensure correctness.

---

## 📄 PREPARATION STEPS

### 1. Open Campaign4_Results.xlsx
- Open the Excel file: `Campaign4_Results.xlsx`
- Familiarize yourself with the 10 available sheets:
  1. Campaign_Scorecard
  2. Owners_By_Parcel
  3. Address_Quality_Distribution
  4. Enhanced_Funnel_Analysis
  5. All_Validation_Ready
  6. Final_Mailing_List
  7. All_Companies_Found
  8. Campaign_Summary
  9. Owners_Normalized
  10. All_Raw_Data

### 2. Open Input File
- Open: `Input_Castiglione Casalpusterlengo CP.xlsx`
- Navigate to Sheet1

---

## 🔢 METRIC VALIDATION PROCEDURES

### METRIC 1: Original Input Parcels (Should be 238)

**Step 1.1: Validate Input File**
- Go to: `Input_Castiglione Casalpusterlengo CP.xlsx` → Sheet1
- Count rows: Click on row header after last data row
- **Expected Result**: 238 rows of data (excluding header)
- **Manual Check**: =COUNTA(A:A)-1 (subtract header row)

**Step 1.2: Cross-check with Campaign_Summary**
- Go to: `Campaign4_Results.xlsx` → Campaign_Summary sheet
- Filter out empty rows: Filter column B (comune) → deselect blanks
- Sum column C (Input_Parcels): =SUM(C:C)
- **Expected Result**: Should total 228 (note: different from input due to data availability)
- **Validation Question**: Why is Campaign_Summary (228) different from Input (238)?

**Documentation**: Record both values and note the discrepancy explanation.

---

### METRIC 2: Original Input Area (Should be 412.2 Ha)

**Step 2.1: Calculate from Input File**
- Go to: `Input_Castiglione Casalpusterlengo CP.xlsx` → Sheet1
- Sum column G (Area): =SUM(G:G)
- **Expected Result**: 412.2 Ha

**Step 2.2: Cross-check with Campaign_Summary**
- Go to: `Campaign4_Results.xlsx` → Campaign_Summary sheet
- Filter out empty rows: Filter column B (comune) → deselect blanks
- Sum column D (Input_Area_Ha): =SUM(D:D)
- **Expected Result**: Should be 356.2 Ha (note: different due to data availability)

**Step 2.3: Validate Discrepancy**
- Check municipalities in input file vs Campaign_Summary
- Input has 7 municipalities, Campaign_Summary has 6
- **Missing Municipality**: Somaglia (should be documented in data availability notes)

**Documentation**: Record input area (412.2) vs processed area (356.2) and explain missing municipality.

---

### METRIC 3: Data Availability Rate (Should be ~95.8%)

**Step 3.1: Calculate Rate**
- Input parcels: 238 (from Metric 1)
- Processed parcels: 228 (from Campaign_Summary)
- Formula: =(228/238)*100
- **Expected Result**: 95.8%

**Step 3.2: Validate Missing Data**
- Compare municipalities between input file and Campaign_Summary
- Input: Carpenedolo, Casalpusterlengo, Castiglione Delle Stiviere, Fombio, Montichiari, Ospedaletto Lodigiano, Somaglia
- Campaign_Summary: Same list except missing Somaglia
- **Validation**: 10 parcels from Somaglia were not processed

**Documentation**: 95.8% availability rate with Somaglia municipality missing.

---

### METRIC 4: Total Validated Area (Should be 1,152 Ha)

**Step 4.1: Calculate from All_Validation_Ready**
- Go to: `Campaign4_Results.xlsx` → All_Validation_Ready sheet
- Sum column G (Area): =SUM(G:G)
- **Expected Result**: 1,152.5 Ha

**Step 4.2: Understand Area Expansion**
- Original input area: 412.2 Ha
- Validated area: 1,152.5 Ha
- Expansion factor: =1152.5/412.2 = 2.8x
- **Explanation**: Owner discovery process found additional properties owned by same owners

**Documentation**: 2.8x area expansion through owner discovery process.

---

### METRIC 5: Technical Validation Count (Should be 642)

**Step 5.1: Count All_Validation_Ready Records**
- Go to: `Campaign4_Results.xlsx` → All_Validation_Ready sheet
- Count data rows: =COUNTA(A:A)-1
- **Expected Result**: 642 addresses

**Step 5.2: Validate Unique Owners**
- Go to: All_Validation_Ready sheet
- Remove duplicates on column M (cf - fiscal code): Data → Remove Duplicates → Select column M
- Count unique values: Note the count
- **Expected Result**: Should be 174 unique owners

**Step 5.3: Calculate Addresses per Owner**
- Formula: =642/174 = 3.7 addresses per owner average
- **Explanation**: Some owners have multiple addresses

**Documentation**: 642 addresses from 174 unique owners (3.7 avg per owner).

---

### METRIC 6: Final Mailings Count (Should be 303)

**Step 6.1: Count Final_Mailing_List Records**
- Go to: `Campaign4_Results.xlsx` → Final_Mailing_List sheet
- Count data rows: =COUNTA(A:A)-1
- **Expected Result**: 303 mailings

**Step 6.2: Count Unique Final Owners**
- Remove duplicates on column F (cf): Data → Remove Duplicates → Select column F
- Count unique values
- **Expected Result**: Should be 157 unique owners

**Step 6.3: Count Unique Parcels in Final Mailing**
- Concatenate Foglio + Particella: Create new column =B2&"-"&C2
- Remove duplicates on this new column
- Count unique parcel combinations
- **Expected Result**: This gives the unique parcels that made it to final mailing

**Documentation**: 303 mailings to 157 owners covering X unique parcels.

---

### METRIC 7: Parcel Success Rate (Critical Validation)

**Step 7.1: Count Input Parcels by Municipality**
- Go to: `Input_Castiglione Casalpusterlengo CP.xlsx` → Sheet1
- Create pivot table: Insert → PivotTable
- Rows: comune (column E)
- Values: Count of tipo_catasto
- **Result**: Count per municipality

**Step 7.2: Count Final Parcels by Municipality**
- Go to: `Campaign4_Results.xlsx` → Final_Mailing_List sheet
- Extract municipality from Municipality column (remove province codes)
- Create pivot table with municipality counts
- **Result**: Count per municipality

**Step 7.3: Calculate Success Rate by Municipality**
- Compare input counts vs final counts per municipality
- Overall rate: (Total final parcels / Total input parcels) * 100
- **Critical Check**: This should be around 35-40%, NOT over 100%

**Documentation**: Municipality-by-municipality breakdown with overall success rate.

---

### METRIC 8: Address Optimization Rate

**Step 8.1: Count Validation Addresses**
- All_Validation_Ready: 642 addresses (from Metric 5)

**Step 8.2: Count Final Mailings**
- Final_Mailing_List: 303 mailings (from Metric 6)

**Step 8.3: Calculate Optimization Rate**
- Formula: =(303/642)*100 = 47.2%
- **Explanation**: 47.2% of validated addresses made it to final mailing

**Documentation**: 47.2% address optimization through filtering and consolidation.

---

### METRIC 9: Campaign Scorecard Validation

**Step 9.1: Validate Scorecard Totals**
- Go to: `Campaign4_Results.xlsx` → Campaign_Scorecard sheet
- Check each row:
  - Direct Mail Campaign: 144 people, 480 mailings, 137 parcels, 222.7 Ha
  - Agency Review: 70 people, 162 mailings, 85 parcels, 187.6 Ha
  - Company Outreach: 19 entities, 37 mailings, 37 parcels, 48.1 Ha

**Step 9.2: Cross-validate with Other Sheets**
- Direct Mail + Agency people: 144 + 70 = 214 people
- Compare with All_Validation_Ready unique owners: Should be close to 174
- **Discrepancy Check**: Investigate if numbers align logically

**Step 9.3: Validate Area Totals**
- Scorecard total area: 222.7 + 187.6 + 48.1 = 458.4 Ha
- Compare with other area calculations
- **Check**: Do the areas add up consistently?

---

### METRIC 10: Geographic Coverage Validation

**Step 10.1: Count Coordinates in All_Validation_Ready**
- Go to: All_Validation_Ready sheet
- Filter column AO (Latitude): Remove blanks
- Count remaining rows
- **Expected**: Should be 642 (100% coverage)

**Step 10.2: Validate Municipality Distribution**
- Create pivot table on Final_Mailing_List
- Rows: Municipality column
- Values: Count
- **Result**: Distribution by municipality
- **Cross-check**: Compare with input municipality distribution

---

### METRIC 11: Ownership Complexity Validation

**Step 11.1: Analyze Owners_By_Parcel**
- Go to: `Campaign4_Results.xlsx` → Owners_By_Parcel sheet
- Check column F (total_owners)
- Create frequency distribution: =COUNTIF(F:F,">1") for multi-owner parcels
- **Expected**: 84 multi-owner parcels

**Step 11.2: Validate Complex Ownership**
- Count parcels with >5 owners: =COUNTIF(F:F,">5")
- **Expected**: 8 complex ownership parcels

**Step 11.3: Calculate Area Impact**
- Sum parcel_area_ha for multi-owner parcels only
- Filter total_owners > 1, then sum column E
- **Result**: Area covered by complex ownership

---

## 🔍 CRITICAL VALIDATION CHECKPOINTS

### Checkpoint 1: Pipeline Flow Logic
1. Input parcels (238) should decrease through pipeline
2. Addresses (642) can be > parcels due to multiple owners per parcel
3. Final mailings (303) should be < addresses due to optimization
4. Final parcels should be < input parcels (success rate)

### Checkpoint 2: Area Consistency
1. Input area (412.2) < Validated area (1,152) due to owner discovery
2. Areas in Campaign_Scorecard should sum logically
3. Area expansion factor should be reasonable (2-3x)

### Checkpoint 3: Owner Logic
1. Validation owners (174) should be reasonable vs input parcels (238)
2. Final owners (157) should be ≤ validation owners (174)
3. Addresses per owner ratios should be logical

### Checkpoint 4: Municipality Consistency
1. All sheets should reference same municipalities (except missing data)
2. Municipality totals should cross-validate
3. Missing municipalities should be documented

---

## 📋 VALIDATION CHECKLIST

**Before Finalizing Dashboard:**
- [ ] Input metrics validated against source files
- [ ] Pipeline flow makes logical sense
- [ ] Area calculations are consistent
- [ ] Owner counts are logical
- [ ] Municipality data is consistent
- [ ] Scorecard totals cross-validate
- [ ] Geographic coverage is accurate
- [ ] All percentages are ≤ 100%
- [ ] Discrepancies are explained
- [ ] Documentation is complete

**Red Flags to Investigate:**
- ❌ Any efficiency rate > 100%
- ❌ Final counts > input counts (without logical explanation)
- ❌ Area discrepancies without explanation
- ❌ Municipality mismatches
- ❌ Owner count inconsistencies

---

## 📊 FINAL VALIDATION REPORT TEMPLATE

```
METRIC VALIDATION SUMMARY:
==========================

1. Original Input Parcels: ___ (Expected: 238)
2. Original Input Area: ___ Ha (Expected: 412.2)
3. Data Availability Rate: ___% (Expected: ~95.8%)
4. Total Validated Area: ___ Ha (Expected: 1,152)
5. Technical Validation Count: ___ (Expected: 642)
6. Final Mailings Count: ___ (Expected: 303)
7. Parcel Success Rate: ___% (Expected: 35-40%)
8. Address Optimization Rate: ___% (Expected: 47.2%)
9. Geographic Coverage: ___% (Expected: 100%)
10. Multi-owner Parcels: ___ (Expected: 84)

DISCREPANCIES FOUND:
===================
- [List any values that don't match expectations]
- [Explanations for discrepancies]
- [Actions needed to correct]

VALIDATION STATUS: ✅ APPROVED / ❌ NEEDS CORRECTION
```

---

**📋 Next Steps After Validation:**
1. Document all findings
2. Correct any calculation errors
3. Update dashboard with validated metrics
4. Re-test dashboard calculations
5. Prepare final executive presentation

