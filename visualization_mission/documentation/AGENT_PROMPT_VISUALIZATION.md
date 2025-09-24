# 🎯 Agent Prompt: Campaign Visualization Development

## **EXACT PROMPT FOR VISUALIZATION AGENT**

```
I need you to create a comprehensive set of interactive visualizations for a Land Acquisition Pipeline campaign using validated data. This is for executive presentations to stakeholders in the renewable energy sector.

BEFORE starting any work, you MUST read these documents in order:

1. **VISUALIZATION_REQUIREMENTS_v318.md** - Complete technical and business requirements
2. **CAMPAIGN4_FOUNDATION_DATASET.md** - Validated dataset documentation and context
3. **BUSINESS_CONTEXT.md** - Full business background (renewable energy land acquisition)
4. **METRICS_GUIDE.md** - Detailed explanation of all metrics and calculations

CRITICAL FOUNDATION INFORMATION:
- **Data Source**: ../data/Campaign4_Results.xlsx (relative to visualization_mission folder)
- **Absolute Path**: C:\Projects\land-acquisition-pipeline\visualization_mission\data\Campaign4_Results.xlsx
- **Status**: Validated and corrected for v3.1.8 compliance
- **Total Records**: 642 validation-ready addresses across 6 municipalities
- **Key Metrics**: Direct_Mail_Final_Contacts (558), Agency_Final_Contacts (84)
- **Business Context**: Renewable energy land acquisition in Northern Italy

PRIMARY OBJECTIVE:
Create interactive visualizations using Plotly that demonstrate:
1. Campaign effectiveness (86.9% direct mail efficiency)
2. Process efficiency (dual funnel analysis)
3. Geographic performance (6 municipalities)
4. Address quality distribution (4-tier classification)

TECHNICAL REQUIREMENTS:
- **Primary Package**: Plotly (plotly.express, plotly.graph_objects)
- **Output Format**: Interactive HTML files + static PNG exports
- **Design**: Professional, business-ready for executive presentations
- **Data Processing**: Pandas for data manipulation

PRIORITY DELIVERABLES:
1. **Executive Dashboard** - Single-page overview with key KPIs
2. **Funnel Analysis** - Interactive dual funnel visualization
3. **Municipality Comparison** - Performance across 6 locations
4. **Quality Distribution** - Address confidence breakdown

VALIDATION REQUIREMENTS:
- All visualizations must match the validated Campaign4 dataset exactly
- Direct Mail percentage must show 86.9% (558/642)
- Agency percentage must show 13.1% (84/642)
- Total addresses must equal 642 across all charts

IMPORTANT NOTES:
- This dataset has been mathematically validated and corrected
- Agency_Final_Contacts counts addresses (84) not owners (41)
- The data represents real renewable energy land acquisition results
- Visualizations will be shown to business executives and stakeholders

Do you understand the requirements? Please confirm your understanding of:
1. The business context (renewable energy land acquisition)
2. The data source (Campaign4_Results.xlsx - validated)
3. The primary objective (executive-ready visualizations)
4. The technical requirements (Plotly-based interactive charts)
5. The validation requirements (exact metric alignment)

Only after confirming understanding should you proceed with the visualization development.
```

---

## **SUPPORTING CONTEXT FOR AGENT**

### **Why This Project Matters**
- **Business Impact**: Renewable energy project development in Italy
- **Financial Scale**: Large-scale land acquisition (500-1000 hectares)
- **Stakeholder Audience**: C-level executives, land acquisition teams
- **Success Metrics**: 86.9% direct mail efficiency, 2.9x contact multiplication

### **Data Quality Assurance**
- **Validation Status**: Mathematically verified across all sheets
- **Consistency**: All metrics cross-reference perfectly
- **Corrections Applied**: v3.1.8 Agency_Final_Contacts alignment
- **Foundation Ready**: Suitable for production visualization

### **Technical Environment**
- **Platform**: Python with Plotly
- **File Access**: Agent will have access to the project folder
- **Output Location**: `outputs/visualizations/` directory
- **Documentation**: Complete technical and business context provided

---

## **EXPECTED AGENT RESPONSE**

The agent should confirm understanding of:
1. **Business Context**: Renewable energy land acquisition in Italy
2. **Data Source**: Campaign4_Results.xlsx (validated and corrected)
3. **Objective**: Executive-ready visualizations demonstrating campaign effectiveness
4. **Technical Stack**: Plotly-based interactive visualizations
5. **Validation**: All metrics must match the validated dataset exactly

---

## **SUCCESS CRITERIA**

### **Agent Readiness Indicators**
- ✅ Confirms understanding of business context
- ✅ Acknowledges data validation status
- ✅ Understands executive presentation requirement
- ✅ Recognizes technical requirements (Plotly)
- ✅ Commits to exact metric alignment

### **Immediate Next Steps**
1. **Document Review**: Read all 4 required documents
2. **Data Loading**: Load and validate Campaign4_Results.xlsx
3. **Environment Setup**: Install required Python packages
4. **Development Start**: Begin with Priority 1 visualizations

---

**📊 Document Status**: ✅ **Ready for Agent Handoff**  
**🎯 Purpose**: **Visualization development initiation**  
**📅 Created**: 2025-07-15  
**🔄 Usage**: **Copy prompt exactly for new agent**