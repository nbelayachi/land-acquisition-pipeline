# 📋 v3.1.8 Agency_Final_Contacts Testing Checklist

## **MANDATORY VALIDATION FOR NEXT CAMPAIGN**

### **🎯 Primary Validation Points:**

1. **✅ Agency_Final_Contacts Calculation**
   - Verify `Agency_Final_Contacts` = count of LOW confidence addresses
   - Should NOT include any MEDIUM confidence addresses
   - Compare with manual count: `df[df['Address_Confidence'] == 'LOW'].shape[0]`

2. **✅ Total Address Consistency**
   - Verify: `Direct_Mail_Final_Contacts + Agency_Final_Contacts = Total validation addresses`
   - Should equal `len(All_Validation_Ready)` exactly
   - No addresses should be missing or double-counted

3. **✅ Cross-Sheet Alignment**
   - `Enhanced_Funnel_Analysis` "Agency Investigation Required" = `Campaign_Summary` `Agency_Final_Contacts`
   - `PowerBI_Dataset.csv` `Agency_Final_Contacts` = sum of `Campaign_Summary` values
   - All sheets show consistent totals

4. **✅ Percentage Calculations**
   - Direct_Mail_Percentage = (Direct_Mail_Final_Contacts / Total_Final_Contacts) × 100
   - Should be ~86-87% (much higher than old 77.5%)
   - Verify percentages sum correctly across all metrics

### **🔧 Technical Validation:**

1. **Code Execution**
   - No errors during `create_municipality_summary()` execution
   - Both `direct_mail_df` and `agency_df` filters work correctly
   - Address_Confidence column exists in validation data

2. **Municipality Aggregation**
   - Test with multiple municipalities
   - Verify aggregation doesn't lose or duplicate addresses
   - Check area calculations align with address counts

3. **Edge Cases**
   - Test with campaign having no LOW confidence addresses
   - Test with campaign having only LOW confidence addresses
   - Verify error handling for missing Address_Confidence column

### **📊 Expected Results (Based on Campaign4):**

- **Direct_Mail_Final_Contacts**: Should be ~558 (87% of total)
- **Agency_Final_Contacts**: Should be ~84 (13% of total)
- **Total_Final_Contacts**: Should equal total validation addresses
- **Direct_Mail_Percentage**: Should be ~86.9%

### **❌ Red Flags to Watch For:**

- Agency_Final_Contacts = 162 (indicates old routing-based calculation)
- Total doesn't match validation addresses (indicates double-counting)
- Enhanced_Funnel_Analysis mismatches Campaign_Summary
- Direct_Mail_Percentage below 80% (indicates calculation error)

### **✅ Success Criteria:**

- All addresses accounted for (no missing or extra)
- Consistent totals across all sheets
- Direct_Mail_Percentage significantly higher than historical
- No code errors during execution
- Business logic aligns with confidence-based methodology

---

**🔍 Post-Campaign Validation:**
Run `validate_campaign_metrics.py` with new campaign output to verify all metrics are mathematically consistent.

**📅 Created**: 2025-07-15  
**📋 Status**: Ready for next campaign testing  
**🎯 Priority**: Critical - Must validate before production use