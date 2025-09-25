# Version Alignment Audit – v3.1.8

## Feature Verification
- **Direct mail metric logic** – `create_municipality_summary` now builds `direct_mail_df` by filtering `Address_Confidence` for `ULTRA_HIGH`, `HIGH`, and `MEDIUM`, so the `Direct_Mail_Final_Contacts` count is aligned with what the dashboard recomputes. (land_acquisition_pipeline.py, lines ~1214-1234)
- **Agency metric correction** – the same function now restricts agency contacts to `Address_Confidence == 'LOW'`, fixing the previously inconsistent total when compared to the dashboard’s robust calculations. (land_acquisition_pipeline.py, lines ~1234-1238)
- **Area aggregation** – both contact channels de-duplicate parcels before summing hectares, matching the executive dashboard’s methodology. (land_acquisition_pipeline.py, lines ~1239-1242)
- **Dashboard baseline** – the authoritative visualization logic lives in `visualization_mission/SYNC/complete_robust_dashboard.py` (VERSION 3.3) and recomputes the same parcel counts directly from the Excel outputs, confirming the corrected methodology. (visualization_mission/SYNC/complete_robust_dashboard.py, lines ~26-116)

## Version Reference Inventory
- `land_acquisition_pipeline.py` previously identified itself as **v2.9.x** in the header, logging banner, CLI description, and cost summary output even though the implemented features were v3.1.7/v3.1.8. ✅ Updated to 3.1.8 across those touchpoints.
- `campaign_launcher.py` exposed version **3.1.6** in the header, banner, and feature list. ✅ Updated to 3.1.8 with refreshed messaging.
- `README.md` marketed the project as **v3.1.6** and its “New in” section stopped at that release. ✅ Updated to 3.1.8 with metric-alignment highlights.
- `COMMIT_MESSAGE_v3.1.6.txt` documents the last reconciliation against v3.1.6 (left untouched for historical reference).

## Cleanup Opportunities (Next Steps to Discuss)
- Consolidate duplicate dashboard scripts scattered under `visualization_mission/` – the SYNC copy is the correct reference, so older variants in `data/` and `final script/` could be archived elsewhere.
- Review the large `dev_tools/` directory; many helpers are historical and may no longer be required in the main repository.
- Consider relocating campaign-specific outputs (e.g., `visualization_mission/outputs/`) into an archival bucket to keep the core pipeline workspace focused on production assets.
