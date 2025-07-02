"""
Project Organization Script
Clean up and organize the land-acquisition-pipeline folder structure
"""

import os
import shutil
from pathlib import Path

def organize_project():
    """Organize the project structure for better maintainability"""
    
    base_path = Path("/mnt/c/Projects/land-acquisition-pipeline")
    
    print("PROJECT ORGANIZATION PLAN")
    print("=" * 50)
    print("Current structure needs organization for:")
    print("- Better file categorization")
    print("- Cleaner development workflow") 
    print("- Easier maintenance")
    print()
    
    # Define new structure
    new_structure = {
        "dev_tools/funnel_analysis/": [
            "analyze_funnel_metrics.py",
            "analyze_funnel_simple.py", 
            "analyze_cat_a_filter_impact.py",
            "evaluate_all_metrics.py"
        ],
        "dev_tools/testing/": [
            "test_enhanced_funnel_data.py",
            "validate_funnel_against_real_data.py",
            "validate_funnel_simple.py"
        ],
        "dev_tools/prototypes/": [
            "create_corrected_funnel.py",
            "create_final_funnel.py", 
            "create_perfected_funnel.py"
        ],
        "outputs/funnel_data/": [
            "final_funnel_data.csv",
            "final_quality_distribution.csv",
            "corrected_funnel_data.csv",
            "corrected_quality_distribution.csv",
            "enhanced_funnel_sample_data.csv",
            "perfected_funnel_data.csv",
            "quality_distribution_data.csv"
        ],
        "outputs/analysis_results/": [
            "analyze_results_simple.py"
        ]
    }
    
    print("PROPOSED ORGANIZATION")
    print("-" * 30)
    
    for folder, files in new_structure.items():
        print(f"\n📁 {folder}")
        for file in files:
            current_path = base_path / file
            exists = "✅" if current_path.exists() else "❌"
            print(f"   {exists} {file}")
    
    print(f"\nFILES TO ORGANIZE")
    print("-" * 20)
    
    all_files_to_move = []
    for files in new_structure.values():
        all_files_to_move.extend(files)
    
    # Check which files exist and need moving
    existing_files = []
    missing_files = []
    
    for file in all_files_to_move:
        file_path = base_path / file
        if file_path.exists():
            existing_files.append(file)
        else:
            missing_files.append(file)
    
    print(f"Files found and ready to organize: {len(existing_files)}")
    for file in existing_files:
        print(f"  ✅ {file}")
    
    if missing_files:
        print(f"\nFiles not found (may already be moved): {len(missing_files)}")
        for file in missing_files:
            print(f"  ❌ {file}")
    
    print(f"\nCLEANUP RECOMMENDATIONS")
    print("-" * 25)
    
    # Files that could be archived or removed
    cleanup_candidates = [
        "test_2.xlsx",  # Temporary test file
    ]
    
    print("Files that could be archived:")
    for file in cleanup_candidates:
        file_path = base_path / file
        exists = "✅ Found" if file_path.exists() else "❌ Not found"
        print(f"  {exists}: {file}")
    
    print(f"\nFOLDER STRUCTURE VALIDATION")
    print("-" * 30)
    
    # Check existing folder structure
    important_folders = [
        "doc",
        "dev_tools", 
        "campaigns",
        "completed_campaigns",
        "logs",
        "cache"
    ]
    
    for folder in important_folders:
        folder_path = base_path / folder
        exists = "✅ Exists" if folder_path.exists() else "❌ Missing"
        if folder_path.exists():
            file_count = len(list(folder_path.rglob("*"))) 
            print(f"  {exists}: {folder}/ ({file_count} items)")
        else:
            print(f"  {exists}: {folder}/")
    
    print(f"\nDOCUMENTATION STATUS")
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
        exists = "✅" if doc_path.exists() else "❌"
        print(f"  {exists} {doc}")
    
    print(f"\nORGANIZATION COMMANDS")
    print("-" * 25)
    print("To implement this organization, run these commands:")
    print()
    
    # Generate organization commands
    for target_folder, files in new_structure.items():
        target_path = base_path / target_folder
        print(f"# Create {target_folder}")
        print(f"mkdir -p {target_path}")
        print()
        
        for file in files:
            source = base_path / file
            destination = target_path / file
            if source.exists():
                print(f"mv {source} {destination}")
        print()
    
    print("# Remove temporary files")
    for file in cleanup_candidates:
        file_path = base_path / file
        if file_path.exists():
            print(f"rm {file_path}")
    
    print(f"\nORGANIZATION BENEFITS")
    print("-" * 25)
    benefits = [
        "Cleaner root directory",
        "Categorized development tools",
        "Separated outputs from source code", 
        "Better version control",
        "Easier onboarding for new developers",
        "Improved maintainability"
    ]
    
    for i, benefit in enumerate(benefits, 1):
        print(f"{i}. {benefit}")
    
    return {
        'files_to_organize': len(existing_files),
        'missing_files': len(missing_files), 
        'folders_needed': len(new_structure),
        'cleanup_items': len(cleanup_candidates)
    }

if __name__ == "__main__":
    print("🗂️  Starting project organization analysis...")
    results = organize_project()
    
    print(f"\n📊 ORGANIZATION SUMMARY")
    print("=" * 30)
    print(f"Files ready to organize: {results['files_to_organize']}")
    print(f"New folders needed: {results['folders_needed']}")
    print(f"Cleanup items: {results['cleanup_items']}")
    print()
    print("✅ Organization plan complete!")
    print("📋 Ready to implement folder restructuring!")