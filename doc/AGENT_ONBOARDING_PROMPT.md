# 🤖 Agent Onboarding Prompt
## **Mandatory Reading Before Starting Work**

---

## 📋 **EXACT PROMPT FOR NEXT AGENT**

```
I'm working on a Land Acquisition Pipeline for renewable energy projects in Italy. This is a production system with complex business context.

BEFORE you do anything or ask any questions, you MUST:

1. Read doc/BUSINESS_CONTEXT.md completely - This explains the renewable energy company, land acquisition workflow, stakeholders, and business objectives. This eliminates the need for me to re-explain business context.

2. Read doc/CURRENT_STATUS.md completely - This shows what's working excellently (most features) vs what needs business decisions (mailing list process gaps for 78.3% of contacts).

3. Read doc/TECHNICAL_REFERENCE.md completely - This covers the technical implementation, function details, and system architecture.

After reading these 3 documents, confirm you understand:
- The business context (renewable energy land acquisition in Italy)
- Current system status (v3.1.0 production-ready with process gaps)
- Technical architecture (APIs, data flow, output structure)
- The critical issue: 18 of 23 validation-ready contacts lack defined workflow

Only after confirming your understanding should you proceed with any tasks or improvements I request. This project documentation is designed to eliminate context re-explanation and enable immediate productive work.

Key points to remember:
- This is a production system used for real renewable energy land acquisition
- Metrics are shown to broad audiences and must be business-clear
- Documentation must be updated with any changes (PROJECT_MAINTENANCE_GUIDE.md)
- Business process gaps require business decisions, not technical fixes
```

---

## 🎯 **VALIDATION QUESTIONS FOR AGENT**

After reading documentation, agent should be able to answer:

1. **Business Context**: What industry and business problem does this solve?
2. **Current Capabilities**: What does v3.1.0 do well?
3. **Critical Gap**: What business process issue needs resolution?
4. **Technical Architecture**: What are the main processing steps?
5. **Output Structure**: What files are generated and for whom?

If agent can't answer these, they need to re-read the documentation.

---

**Purpose**: Ensure immediate productivity without context re-explanation  
**Success Criteria**: Agent understands business context and current state before starting work