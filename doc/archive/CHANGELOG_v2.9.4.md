# Changelog: Land Acquisition Pipeline v2.9.4

This document details the extensive debugging, refinement, and logic updates applied to the `land_acquisition_pipeline.py` script, bringing it to version 2.9.4. The changes address critical data integrity bugs and align the output metrics with key business requirements.

---

### 1. Initial State Analysis

- **Observation**: The existing documentation (e.g., `implementation_status.md`) was out of sync with the production script. Key features for v2.9, such as SNC reclassification and funnel metrics, were already implemented but contained latent bugs.
- **Action**: Proceeded with a test campaign to validate the actual behavior of the script, which uncovered several critical issues.

### 2. Bug Fixes and Logic Enhancements

#### Bug 1: Critical Data Loss of Valid Parcels

- **Problem**: In the initial test run, valid parcels were being dropped from the `Validation_Ready` sheet. For example, in `Mun_001`, parcel `67` was completely missing despite having valid owner and property data.
- **Root Cause**: The `drop_duplicates()` function in `create_municipality_output` was overly aggressive. It removed duplicates based only on the owner's fiscal code (`cf`) and the cleaned address string. This meant if a single owner had multiple properties (parcels) with addresses that were cleaned to the same value, all but the first property were incorrectly dropped.
- **Solution (v2.9.1)**: The `drop_duplicates()` call was modified to include `foglio_input` and `particella_input` in its subset. This ensures that each unique parcel is preserved as a unique entry, resolving the data loss.

#### Bug 2: Flawed Geocoding and Address Classification

- **Problem**: The geocoding service returned a grossly incorrect postal code for an address in `Mun_001` (`TERRANOVA DEI PASSERINI(LO)` was assigned a postal code from Southern Italy). The script then incorrectly classified this address as `HIGH` confidence because it contained "SNC", which was blindly trusted.
- **Root Cause**: The `classify_address_quality` function lacked a sanity check to validate the geocoding output against the input.
- **Solution (v2.9.1)**:
    1.  **Province Sanity Check**: A new helper function, `is_province_match`, was introduced to verify that the province code from the geocoded address matches the province code from the original input address.
    2.  **Enhanced Classification**: The `classify_address_quality` function was updated to use this sanity check. An address is now only given a higher confidence rating if it passes this validation.
- **Business Logic Revision (v2.9.2)**: Based on user feedback, the business rule for `SNC` addresses was revised. Instead of `HIGH` confidence and `DIRECT_MAIL`, they are now classified as `MEDIUM` confidence and routed to `AGENCY` for manual review.

#### Bug 3: Inaccurate and Misleading Summary Metrics

- **Problem**: The `Municipality_Summary` and `Funnel_Analysis` sheets contained incorrect and misleading metrics. Contact counts were inflated by counting every row, and area (hectares) was being double-counted for parcels with multiple owners.
- **Root Cause**: The summary calculations were based on simple row counts (`len()`) and sums (`sum()`) of the `Validation_Ready` DataFrame, which contained duplicate parcel information.
- **Solution (v2.9.2 & v2.9.3)**:
    1.  **De-duplicated Contact Counts**: The logic was rewritten to count the number of **unique owners** (based on `cf`) for each routing channel (`Direct_Mail_Final_Contacts`, `Agency_Final_Contacts`).
    2.  **De-duplicated Area Calculation**: The area calculation was fixed to sum the area of **unique parcels** (by de-duplicating on `foglio_input` and `particella_input`) within each routing channel.
    3.  **Metric Renaming**: The confusing `Unique_Contacts_Generated` metric was renamed to the more accurate `Unique_Owner_Address_Pairs`.
    4.  **Metric Removal**: The redundant `Hectares_Agency_Required` metric was removed from the `Municipality_Summary` sheet.

#### Bug 4: Inconsistent Funnel Analysis Sheet

- **Problem**: The `Funnel_Analysis` sheet was not updated with the corrected logic from Bug #3, causing its final rows to be inconsistent with the `Municipality_Summary` sheet.
- **Root Cause**: The code block that generated the funnel DataFrame was still using the old, flawed row-counting logic.
- **Solution (v2.9.4)**: The funnel creation logic was modified to pull its final values directly from the **already-calculated and corrected summary metrics**. This ensures the `Funnel_Analysis` and `Municipality_Summary` sheets are always perfectly synchronized.

### 3. Final Status

The script is now at **version 2.9.4**. It is considered stable, robust, and aligned with all specified business requirements. All identified bugs have been resolved, and the output data is accurate and reliable.

---

### 4. Metric Definitions (v2.9.4)

This section defines the key metrics found in the `Municipality_Summary` and `Funnel_Analysis` sheets and how they are calculated.

#### Key Output Metrics

- **Unique_Owner_Address_Pairs**
  - **Definition**: The total number of unique combinations of an owner (`cf`) and a cleaned address (`cleaned_ubicazione`). This represents the number of rows in the `Validation_Ready` sheet *after* initial filtering but *before* final routing and de-duplication for contact purposes.
  - **Calculation**: `count(unique(cf, cleaned_ubicazione))` from the `Validation_Ready` sheet.

- **Direct_Mail_Final_Contacts**
  - **Definition**: The final, de-duplicated count of **unique owners** (`cf`) who are targeted for the `DIRECT_MAIL` channel.
  - **Calculation**: `count(unique(cf))` for all rows where `Routing_Channel` is `DIRECT_MAIL`.

- **Agency_Final_Contacts**
  - **Definition**: The final, de-duplicated count of **unique owners** (`cf`) who are targeted for the `AGENCY` channel.
  - **Calculation**: `count(unique(cf))` for all rows where `Routing_Channel` is `AGENCY`.

- **Direct_Mail_Final_Area_Ha**
  - **Definition**: The final, de-duplicated sum of the area (in hectares) associated with the **unique parcels** (`foglio_input`, `particella_input`) routed to the `DIRECT_MAIL` channel. This prevents double-counting the area of a single parcel that may have multiple owners.
  - **Calculation**: `sum(area)` of unique parcels routed to `DIRECT_MAIL`.

- **Agency_Final_Area_Ha**
  - **Definition**: The final, de-duplicated sum of the area (in hectares) associated with the **unique parcels** (`foglio_input`, `particella_input`) routed to the `AGENCY` channel.
  - **Calculation**: `sum(area)` of unique parcels routed to `AGENCY`.

- **Interpolation_Risks_Detected**
  - **Definition**: The number of addresses in the `Validation_Ready` sheet that were flagged as having a potential interpolation risk during geocoding (e.g., a street number was added by the API or a number mismatch occurred).
  - **Calculation**: `count(rows)` where `Interpolation_Risk` is `True`.