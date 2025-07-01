# 🏠 Land Acquisition Pipeline v2.9.6

**Status**: ✅ **PRODUCTION READY** - All critical issues resolved  
**Last Updated**: July 1, 2025  
**Version**: 2.9.6 (Stable)

## 📋 **What This Does**

Automated Python CLI tool that processes Italian land registry data to identify property owners and generate business intelligence for land acquisition campaigns.

**Input**: Excel file with property parcels  
**Output**: Single consolidated Excel file with 5 sheets of analysis  
**Key Features**: Address enhancement, PEC email lookup, funnel tracking, smart routing

## 🚀 **Quick Start**

### Prerequisites
- Python 3.7+
- Required packages: `pandas`, `requests`, `openpyxl`, `tqdm`, `numpy`
- API tokens configured in `land_acquisition_config.json`

### Run a Campaign
```bash
python campaign_launcher.py
# Select your input Excel file
# Follow prompts to launch campaign
```

### Output Structure (v2.9.6)
Single file: `[Campaign_Name]_Results.xlsx` with 5 sheets:
- **All_Raw_Data**: Complete raw property owner data
- **All_Validation_Ready**: Processed contacts ready for outreach  
- **All_Companies_Found**: Company owners with PEC emails
- **Campaign_Summary**: Business metrics by municipality
- **Funnel_Analysis**: Parcel/hectare flow tracking

## 📊 **Current Status (v2.9.6)**

### ✅ **Working Features**
- **Single Consolidated Output**: One Excel file per campaign
- **Complete Funnel Tracking**: Parcels and hectares through all stages
- **Address Quality Intelligence**: Smart routing (DIRECT_MAIL vs AGENCY)
- **PEC Email Integration**: Automatic company email lookup
- **Geocoding Enhancement**: ZIP codes and coordinates
- **Proper Decimal Formatting**: Accurate area calculations
- **Complete Traceability**: CP/comune/provincia columns in all sheets

### 🔧 **Recent Fixes (v2.9.6)**
- Fixed decimal/comma confusion in area calculations
- Added missing traceability columns to Campaign_Summary
- Fixed Unique_Owner_Address_Pairs metric (was showing 0)
- Added provincia column to Funnel_Analysis
- Ensured All_Companies_Found sheet always created

### 📈 **Performance**
- **Contact Reduction**: 93% (128 raw → 23 validated contacts typical)
- **Processing Time**: ~2 minutes per municipality
- **API Success Rate**: 95%+ when data available
- **Geocoding Success**: 100% for valid addresses

## 📁 **File Structure**

```
land-acquisition-pipeline/
├── README.md                     ← You are here
├── land_acquisition_pipeline.py  ← Main pipeline
├── campaign_launcher.py          ← Campaign setup
├── land_acquisition_config.json  ← Configuration
├── doc/
│   ├── CHANGELOG.md              ← Version history
│   ├── HANDOFF_GUIDE.md          ← For new agents
│   └── TECHNICAL_GUIDE.md        ← Detailed technical docs
├── completed_campaigns/          ← Output directory
└── cache/                        ← API response cache
```

## 🛠️ **Configuration**

Edit `land_acquisition_config.json`:
```json
{
  "api_settings": {
    "token": "YOUR_CATASTO_API_TOKEN"
  },
  "geocoding_settings": {
    "enabled": true,
    "token": "YOUR_GEOCODING_TOKEN"
  },
  "pec_integration": {
    "enabled": true,
    "token": "YOUR_PEC_API_TOKEN"
  }
}
```

## 🆘 **Troubleshooting**

**Common Issues:**
- **Missing API tokens**: Check `land_acquisition_config.json`
- **Empty results**: Verify Sezione data for certain municipalities
- **Timeout errors**: Use built-in recovery system (automatic)

**Analysis Tools:**
- `simple_campaign_analyzer.py` - Verify output structure
- Check logs in `logs/` directory

## 📞 **Support**

- **Documentation**: See `doc/` folder for detailed guides
- **Logs**: Check `logs/land_acquisition_pipeline_[timestamp].log`
- **Version History**: See `doc/CHANGELOG.md`

---
**🎯 Ready for production use. All critical v2.9.6 fixes verified and tested.**