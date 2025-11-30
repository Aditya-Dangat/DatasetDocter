"""
DatasetDoctor - Main Entry Point

This is where everything starts. Run this file to start DatasetDoctor.

Usage:
    python src/main.py
    
Or from the project root:
    python -m src.main
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config import Config
from src.agents.orchestrator import OrchestratorAgent


def main():
    """
    Main function - This is what runs when you execute the script
    
    Can run in two modes:
    1. Command-line: python src/main.py <file>
    2. Web UI: python src/main.py --web
    """
    # Check if web mode
    if len(sys.argv) > 1 and sys.argv[1] == '--web':
        from ui.app import app
        Config.validate()
        print(f"\n🌐 Starting DatasetDoctor Web UI...")
        print(f"   Open your browser to: http://localhost:{Config.PORT}")
        print(f"   Press Ctrl+C to stop\n")
        app.run(host='0.0.0.0', port=Config.PORT, debug=Config.FLASK_DEBUG)
        return
    
    # Command-line mode
    print("🏥 DatasetDoctor - Your Data Quality Assistant")
    print("=" * 60)
    print()
    
    # Validate configuration
    Config.validate()
    
    # Create the orchestrator (the manager)
    orchestrator = OrchestratorAgent()
    
    # Check if file path provided as command-line argument
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if not os.path.exists(filepath):
            print(f"❌ Error: File not found: {filepath}")
            return
        
        # Process the dataset
        result = orchestrator.process_dataset(filepath)
        
        if result['success']:
            print(f"\n✅ {result['message']}")
            print(f"\n📊 Dataset Info:")
            dataset = result['dataset']
            print(f"   Name: {dataset.name}")
            print(f"   Shape: {dataset.shape}")
            print(f"   Columns: {', '.join(dataset.get_columns()[:5])}...")
            
            # Show diagnostic summary
            report = result['report']
            if report.issues:
                print(f"\n📋 Diagnostic Summary:")
                print(f"   Total Issues Found: {len(report.issues)}")
                print(f"   Quality Score: {report.quality_score:.1f}/100")
                print(f"\n   Issues by Type:")
                issues_by_type = report._count_issues_by_type()
                for issue_type, count in issues_by_type.items():
                    print(f"      - {issue_type}: {count}")
            else:
                print(f"\n✅ No issues found! Dataset is clean.")
        else:
            print(f"\n❌ {result['message']}")
            if result['report']:
                print(f"\nIssues found:")
                for issue in result['report'].issues:
                    print(f"   - {issue.description}")
    
    else:
        # No file provided - show help
        print("Usage:")
        print("  Command-line: python src/main.py <path_to_dataset>")
        print("  Web UI:       python src/main.py --web")
        print()
        print("Examples:")
        print("  python src/main.py examples/sample_messy_data.csv")
        print("  python src/main.py --web")
        print()
        print("💡 Tip: Use --web for a friendly browser interface!")


if __name__ == "__main__":
    main()

