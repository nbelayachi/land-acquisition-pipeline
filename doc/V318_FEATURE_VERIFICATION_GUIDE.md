# ✅ v3.1.8 Feature Verification Guide

This guide explains how to confirm that the v3.1.8 confidence-based contact logic is implemented correctly across the pipeline, launcher, and executive dashboard.

## 1. Create a Safe Test Workspace
1. Clone the repository into a **separate** folder so production assets remain untouched:
   ```bash
   git clone . ../land-acquisition-pipeline-sandbox
   cd ../land-acquisition-pipeline-sandbox
   ```
2. (Optional) Create a Python virtual environment and install any local dependencies required for your campaign workflow.

## 2. Quick Integrity Checks
Run lightweight checks to make sure the scripts load:
```bash
python -m compileall land_acquisition_pipeline.py campaign_launcher.py visualization_mission/SYNC/complete_robust_dashboard.py
python dev_tools/testing/validate_v318_agency_correction.py
```
The validation script now confirms that every metric aggregation uses the shared `split_contact_channels` helper and that no routing-based fallbacks remain.

## 3. Execute a Dry-Run Campaign
1. Launch the guided CLI and follow the prompts with a non-production Excel file (for example, `Input_Lombardia5.xlsx`):
   ```bash
   python campaign_launcher.py
   ```
2. When the launcher finishes, inspect the generated `<campaign>_Results.xlsx` inside `completed_campaigns/<campaign>`.
   * Open the **Campaign_Summary** sheet and confirm:
     - `Direct_Mail_Final_Contacts` + `Agency_Final_Contacts` equals `Unique_Owner_Address_Pairs`.
     - Direct mail counts track ULTRA_HIGH/HIGH/MEDIUM addresses, while agency counts match LOW-confidence rows.
   * Check **Enhanced_Funnel_Analysis** for matching counts in stages 4 and 5.

## 4. Cross-Validate with the Executive Dashboard
1. Adjust the paths at the bottom of `visualization_mission/SYNC/complete_robust_dashboard.py` to point to the newly produced Excel result and original input file.
2. Run the dashboard generator:
   ```bash
   python visualization_mission/SYNC/complete_robust_dashboard.py
   ```
3. Review the console summary and generated HTML. The "Final Mailing" stage should report the same counts and hectares you observed in the Excel output.

## 5. Optional Spot Checks
* Use `dev_tools/testing/validate_campaign_metrics.py <path_to_results.xlsx>` for additional automatic parity checks across all sheets.
* Filter the `All_Validation_Ready` sheet to verify that MEDIUM-confidence records appear in the strategic mailing list while LOW-confidence records are absent.

Following these steps ensures the confidence-based metrics introduced in v3.1.8 are consistent end-to-end before promoting a campaign to production.
