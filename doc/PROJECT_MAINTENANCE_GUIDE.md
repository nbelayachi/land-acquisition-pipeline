# 🔧 Project Maintenance Guide
**For All Future Agents - MANDATORY READING**

## 🎯 **Core Principle**
**This project is DYNAMIC** - every change must be followed by systematic maintenance to keep documentation current and folders organized.

---

## 📋 **MANDATORY WORKFLOW FOR ALL AGENTS**

### **After ANY Code Changes**
1. **Update Documentation** 
2. **Check File Organization**
3. **Archive Old Files**
4. **Update Version References**
5. **Verify Cross-References**

### **After Major Features**
1. **Update README.md** with new features
2. **Update CHANGELOG.md** with version entry
3. **Update HANDOFF_GUIDE.md** with new function locations
4. **Update PROJECT_STATUS** document
5. **Check for obsolete files to archive**

---

## 🏗️ **SYSTEMATIC APPROACH**

### **Step 1: Pre-Work Assessment**
Before making any changes, ask the user:
```
"Before I implement [change], I'll need to also:
1. Update the documentation to reflect these changes
2. Check if any files need archiving
3. Verify folder organization remains clean
4. Update version references if needed

Should I proceed with this full maintenance approach?"
```

### **Step 2: During Implementation**
- **Track all files created/modified**
- **Note any new functions or major changes**
- **Identify any superseded files**
- **Consider version impact**

### **Step 3: Post-Implementation Maintenance**
Execute this checklist EVERY TIME:

#### **Documentation Updates (3 Core Documents)**
- [ ] Update BUSINESS_CONTEXT.md if business process/metrics changed
- [ ] Update CURRENT_STATUS.md with new capabilities/issues
- [ ] Update TECHNICAL_REFERENCE.md if functions/outputs changed
- [ ] Add CHANGELOG.md entry for significant changes
- [ ] Update README.md if core capabilities changed
- [ ] Create/Update METRICS_GUIDE.md with detailed metric explanations and business rationale.

#### **Testing and Validation**
- [ ] Run `dev_tools/testing/validate_campaign_metrics.py` with a recent campaign output to verify metric accuracy and consistency.

#### **File Organization**
- [ ] Check dev_tools/ for new files that should be categorized
- [ ] Archive any superseded files
- [ ] Move analysis outputs to outputs/analysis_results/
- [ ] Ensure test files are in dev_tools/testing/
- [ ] Check for duplicate functionality

#### **Version Management**
- [ ] Update version numbers in relevant files
- [ ] Check for outdated version references
- [ ] Archive version-specific scripts if applicable

---

## 📁 **FOLDER STRUCTURE RULES**

### **Root Directory** (Keep Clean)
**ONLY these files allowed in root:**
- `README.md`
- `land_acquisition_pipeline.py`
- `campaign_launcher.py`
- `land_acquisition_config.json`
- `PROJECT_ORGANIZATION_COMPLETE.md`

**Everything else must be in subdirectories**

### **dev_tools/ Organization**
```
dev_tools/
├── (active development files - current work only)
├── testing/           ← ALL test scripts
├── reference/         ← Reference implementations
├── prototypes/        ← Development prototypes
├── funnel_analysis/   ← Analysis tools
├── test-data/         ← Test Excel files
└── archive/           ← Historical/obsolete files
```

### **doc/ Organization**
```
doc/
├── (current documentation - always up-to-date)
├── archive/           ← Historical documentation
├── project-status/    ← Implementation tracking
└── future-system/     ← Planning documents
```

### **Archive Rules**
**Always archive these file types:**
- Version-specific scripts (fix_v296.py, etc.)
- Backup files with timestamps
- Superseded analysis scripts
- One-time diagnostic scripts
- Old test files that have been replaced

---

## 🔄 **AGENT HANDOFF PROTOCOL**

### **Before Ending Session**
Every agent must execute this checklist:

#### **Documentation Currency Check**
- [ ] BUSINESS_CONTEXT.md reflects current business process
- [ ] CURRENT_STATUS.md shows accurate system state
- [ ] TECHNICAL_REFERENCE.md has latest function details
- [ ] README.md reflects current capabilities
- [ ] CHANGELOG.md has latest changes

#### **File Organization Audit**
- [ ] Root directory only contains essential files
- [ ] dev_tools/ is organized by category
- [ ] All test files are in dev_tools/testing/
- [ ] All old files are properly archived
- [ ] No duplicate functionality exists

#### **Version Consistency**
- [ ] All version numbers are consistent
- [ ] No outdated version references exist
- [ ] CHANGELOG matches actual implemented features

### **Handoff Message Template**
```
"Project maintenance completed. Status:
✅ Documentation updated to reflect all changes
✅ File organization verified and cleaned
✅ [X] files archived from dev_tools/
✅ Version references updated to v[X.X.X]
✅ All cross-references verified

Next agent can immediately continue work with current, organized project structure."
```

---

## 💬 **CONVERSATION STARTERS FOR MAINTENANCE**

### **When User Requests Changes**
```
"I'll implement [requested change] and also perform the standard project maintenance:
1. Update documentation to reflect the changes
2. Check file organization and archive any outdated files  
3. Verify version consistency across all files
4. Ensure the project remains clean and organized

This ensures the next agent has a clear, up-to-date project structure. Shall I proceed?"
```

### **When Files Get Messy**
```
"I notice the project has accumulated some development files. 
Should I perform a maintenance cycle to:
1. Archive outdated scripts and analysis files
2. Organize dev_tools/ by category
3. Update documentation to reflect current state
4. Clean up any version inconsistencies

This will ensure optimal organization for future development."
```

### **When Documentation Lags**
```
"The documentation appears to be behind the current implementation. 
I should update:
1. README.md with latest features
2. CHANGELOG.md with recent changes
3. HANDOFF_GUIDE.md with new function locations
4. Technical guides with implementation details

This ensures new agents can immediately understand the current state."
```

---

## 🚨 **RED FLAGS - ALWAYS ADDRESS**

### **Immediate Action Required When You See:**
- **Root directory clutter** (>5 files)
- **Outdated version numbers** in documentation
- **dev_tools/ with >20 files** (needs archiving)
- **README.md last updated >1 week ago** for active project
- **Test files scattered** outside dev_tools/testing/
- **Multiple versions** of same functionality
- **Analysis outputs** in dev_tools/ instead of outputs/

### **Warning Signs**
- Version references don't match actual version
- CHANGELOG.md missing recent changes
- New functions not documented in guides
- Backup files in main directories
- Duplicate test scripts
- **Missing debugging documentation** when new error handling is added
- **Outdated artifact descriptions** when new CSV/Excel outputs are created
- **Undocumented fixes** when pipeline issues are resolved

---

## 📊 **MAINTENANCE METRICS**

### **Health Indicators**
- **Root Files**: ≤ 5 files
- **Documentation Age**: ≤ 1 week behind code
- **dev_tools Files**: ≤ 15 active files
- **Archive Usage**: Regular archiving of old files
- **Version Consistency**: 100% across all files

### **Maintenance Frequency**
- **After each major feature**: Full maintenance cycle
- **After bug fixes**: Documentation updates
- **Weekly for active projects**: Organization audit
- **Before agent handoff**: Complete checklist

---

## 🎯 **SUCCESS CRITERIA**

### **Well-Maintained Project**
- New agent can understand current state in <5 minutes
- All documentation reflects actual implementation
- File organization is logical and clean
- No duplicate or obsolete files in main directories
- Version references are consistent
- Clear progression from previous versions

### **Agent Success Metrics**
- Documentation updated with every change
- Files properly organized and archived
- Version consistency maintained
- Handoff notes comprehensive and accurate
- Project ready for next agent immediately

---

## 📝 **TEMPLATES FOR COMMON TASKS**

### **Archive Decision Tree**
```
File Type → Action
├── Version-specific (fix_v296.py) → Archive
├── Backup with timestamp → Archive  
├── Superseded analysis → Archive
├── One-time diagnostic → Archive
├── Old test versions → Archive
├── Current functionality → Keep
└── Recent development → Keep
```

### **Documentation Update Priority**
```
Priority 1: README.md (user-facing)
Priority 2: CHANGELOG.md (version history)
Priority 3: HANDOFF_GUIDE.md (agent continuity)
Priority 4: Technical guides (implementation details)
Priority 5: Project status (tracking documents)
```

---

## ⚡ **QUICK REFERENCE COMMANDS**

### **Organization Check**
```bash
# Count files in root (should be ≤5)
ls -la /root/project/ | wc -l

# Check dev_tools organization
ls -la dev_tools/

# Verify archive exists
ls -la dev_tools/archive/
```

### **Documentation Currency**
```bash
# Check last modified dates
ls -lat doc/*.md

# Verify version consistency
grep -r "v[0-9].*[0-9]" doc/ README.md
```

---

**🎯 Remember: A well-maintained project is a gift to the next agent and the user. Always leave the project better organized than you found it.**