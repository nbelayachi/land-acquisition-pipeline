import pandas as pd

excel_file_path = r"C:\Projects\land-acquisition-pipeline\completed_campaigns\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213\LandAcquisition_Casalpusterlengo_Castiglione_20250703_2213_Results.xlsx"

print(f"--- Analyzing Address Quality Classification and Routing ---")

try:
    xls = pd.ExcelFile(excel_file_path)
    df_validation_ready = pd.read_excel(xls, 'All_Validation_Ready')
    df_quality_distribution = pd.read_excel(xls, 'Address_Quality_Distribution')
    
    print("\n✅ Successfully loaded All_Validation_Ready and Address_Quality_Distribution sheets.\n")

    print("--- Sample of All_Validation_Ready (Address Confidence & Routing) ---")
    print(df_validation_ready[['cleaned_ubicazione', 'Address_Confidence', 'Routing_Channel', 'Quality_Notes']].head(10))
    print(f"\nTotal records in All_Validation_Ready: {len(df_validation_ready)}\n")

    print("--- Address_Quality_Distribution Summary ---")
    print(df_quality_distribution.to_string(index=False))
    print("\n")

    print("--- Cross-checking Quality Distribution Counts ---")
    validation_passed = True
    for index, row in df_quality_distribution.iterrows():
        quality_level = row['Quality_Level']
        expected_count = row['Count']
        
        actual_count = len(df_validation_ready[df_validation_ready['Address_Confidence'] == quality_level])
        
        if actual_count == expected_count:
            print(f"✅ {quality_level}: Count matches ({actual_count})")
        else:
            print(f"❌ {quality_level}: Count mismatch! Expected {expected_count}, Got {actual_count}")
            validation_passed = False

    if validation_passed:
        print("\n✅ All quality level counts in Address_Quality_Distribution match All_Validation_Ready.")
    else:
        print("\n❌ Some quality level counts do not match. Review discrepancies.")

    print("\n--- Business Sense of Address Quality & Routing ---")
    print("The pipeline classifies addresses into confidence levels to guide the most efficient and cost-effective outreach strategy:")
    print("\n- **ULTRA_HIGH Confidence (Zero Touch)**:")
    print("  These addresses are highly verified and ready for immediate direct mail. They represent the highest automation potential, minimizing manual review and accelerating campaign launch.")
    print("  Business Value: Immediate print ready, lowest cost per contact.")

    print("\n- **HIGH Confidence (Quick Review)**:")
    print("  These addresses are also suitable for direct mail but might require a quick, minimal review. They offer high efficiency with slightly more oversight.")
    print("  Business Value: Minimal validation needed, fast-track mailing.")

    print("\n- **MEDIUM Confidence (Standard Review)**:")
    print("  These addresses require standard manual processing. They are routed for direct mail but need careful review to ensure deliverability and avoid wasted mailing costs.")
    print("  Business Value: Normal processing required, potential for manual optimization.")

    print("\n- **LOW Confidence (Agency Investigation)**:")
    print("  These addresses have significant uncertainties and are routed to an external agency for investigation and field verification. This is the most manual and costly step.")
    print("  Business Value: External investigation required, higher cost per contact, but essential for reaching difficult-to-verify owners.")

    print("\nThis classification directly informs the 'Routing_Channel' (DIRECT_MAIL or AGENCY), allowing the business to make strategic decisions on resource allocation and campaign execution based on address quality.")

except Exception as e:
    print(f"❌ Error during Address Quality analysis: {e}")

print("\n--- Script 5 Finished ---")
