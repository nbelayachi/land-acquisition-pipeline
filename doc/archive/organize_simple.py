"""
Simple Project Organization Analysis
"""

import os
from pathlib import Path

base_path = Path("/mnt/c/Projects/land-acquisition-pipeline")

print("PROJECT ORGANIZATION ANALYSIS")
print("=" * 50)

# Files to organize
funnel_analysis_files = [
    "analyze_funnel_metrics.py",
    "analyze_funnel_simple.py", 
    "analyze_cat_a_filter_impact.py",
    "evaluate_all_metrics.py"
]

testing_files = [
    "test_enhanced_funnel_data.py",
    "validate_funnel_against_real_data.py",
    "validate_funnel_simple.py"
]

prototype_files = [
    "create_corrected_funnel.py",
    "create_final_funnel.py", 
    "create_perfected_funnel.py"
]

output_files = [
    "final_funnel_data.csv",
    "final_quality_distribution.csv",
    "corrected_funnel_data.csv",
    "corrected_quality_distribution.csv",
    "enhanced_funnel_sample_data.csv",
    "perfected_funnel_data.csv",
    "quality_distribution_data.csv"
]

other_analysis = [
    "analyze_results_simple.py"
]

print("FILES TO ORGANIZE")
print("-" * 25)

print("\nFunnel Analysis Scripts:")
for file in funnel_analysis_files:
    exists = "YES" if (base_path / file).exists() else "NO"
    print(f"  {exists}: {file}")

print("\nTesting Scripts:")
for file in testing_files:
    exists = "YES" if (base_path / file).exists() else "NO"
    print(f"  {exists}: {file}")

print("\nPrototype Scripts:")
for file in prototype_files:
    exists = "YES" if (base_path / file).exists() else "NO"
    print(f"  {exists}: {file}")

print("\nOutput CSV Files:")
for file in output_files:
    exists = "YES" if (base_path / file).exists() else "NO"
    print(f"  {exists}: {file}")

print("\nOther Analysis:")
for file in other_analysis:
    exists = "YES" if (base_path / file).exists() else "NO"
    print(f"  {exists}: {file}")

print("\nRECOMMENDED STRUCTURE")
print("-" * 25)
print("dev_tools/")
print("  funnel_analysis/")
print("    - analyze_funnel_metrics.py")
print("    - analyze_funnel_simple.py") 
print("    - analyze_cat_a_filter_impact.py")
print("    - evaluate_all_metrics.py")
print("  testing/")
print("    - test_enhanced_funnel_data.py")
print("    - validate_funnel_against_real_data.py")
print("    - validate_funnel_simple.py")
print("  prototypes/")
print("    - create_corrected_funnel.py")
print("    - create_final_funnel.py")
print("    - create_perfected_funnel.py")
print("outputs/")
print("  funnel_data/")
print("    - final_funnel_data.csv")
print("    - final_quality_distribution.csv")
print("    - corrected_funnel_data.csv")
print("    - corrected_quality_distribution.csv")
print("    - enhanced_funnel_sample_data.csv")
print("    - perfected_funnel_data.csv")
print("    - quality_distribution_data.csv")
print("  analysis_results/")
print("    - analyze_results_simple.py")

print("\nCURRENT FOLDER STATUS")
print("-" * 25)

important_folders = ["doc", "dev_tools", "campaigns", "completed_campaigns", "logs", "cache"]

for folder in important_folders:
    folder_path = base_path / folder
    exists = "EXISTS" if folder_path.exists() else "MISSING"
    print(f"  {exists}: {folder}/")

print("\nDOCUMENTATION STATUS")
print("-" * 25)

doc_files = [
    "doc/FUNNEL_METRICS_COMPREHENSIVE_GUIDE.md",
    "doc/ADDRESS_CLASSIFICATION_ENHANCEMENT.md", 
    "doc/ENHANCED_FUNNEL_DESIGN.md",
    "doc/HANDOFF_GUIDE.md",
    "doc/TECHNICAL_GUIDE.md",
    "doc/CHANGELOG.md"
]

for doc in doc_files:
    doc_path = base_path / doc
    exists = "YES" if doc_path.exists() else "NO"
    print(f"  {exists}: {doc}")

print("\nORGANIZATION BENEFITS")
print("-" * 25)
print("1. Cleaner root directory")
print("2. Categorized development tools")
print("3. Separated outputs from source code")
print("4. Better version control")
print("5. Easier maintenance")
print("6. Improved project structure")

print("\nREADY FOR IMPLEMENTATION!")
print("All files identified and organization plan complete.")