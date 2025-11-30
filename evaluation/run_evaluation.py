#!/usr/bin/env python3
"""
Run Evaluation Suite

Tests DatasetDoctor against gold datasets and generates metrics report.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.evaluation.evaluator import Evaluator


def main():
    """Run the evaluation suite"""
    print("\n🏥 DatasetDoctor - Evaluation Suite")
    print("=" * 60)
    
    # Initialize evaluator
    evaluator = Evaluator()
    
    # Run evaluation
    summary = evaluator.evaluate_all()
    
    # Save results to JSON
    output_file = project_root / "evaluation" / f"metrics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {output_file}")
    
    # Return exit code based on results
    if summary.get('success') and summary.get('pass_rate', 0) >= 75:
        print("\n✅ Evaluation PASSED (≥75% datasets passed)")
        return 0
    else:
        print("\n⚠️  Evaluation needs improvement (<75% datasets passed)")
        return 1


if __name__ == "__main__":
    sys.exit(main())

