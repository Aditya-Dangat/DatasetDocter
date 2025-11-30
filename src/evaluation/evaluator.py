"""
Evaluator - Main evaluation framework that tests agents against gold datasets
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from src.agents.orchestrator import OrchestratorAgent
from src.evaluation.metrics_calculator import MetricsCalculator
from src.core.diagnostics import DiagnosticReport


class Evaluator:
    """
    Evaluates DatasetDoctor agents against gold datasets
    
    Gold datasets are test files with known issues.
    We compare what agents find/fix vs what we expect.
    """
    
    def __init__(self, gold_datasets_dir: str = "evaluation/gold_datasets", 
                 expected_results_file: str = "evaluation/expected_results.json"):
        self.gold_datasets_dir = Path(gold_datasets_dir)
        self.expected_results_file = Path(expected_results_file)
        self.orchestrator = OrchestratorAgent()
        self.metrics_calculator = MetricsCalculator()
        self.expected_results = self._load_expected_results()
    
    def _load_expected_results(self) -> Dict[str, Any]:
        """Load expected results from JSON file"""
        try:
            if self.expected_results_file.exists():
                with open(self.expected_results_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"⚠️  Warning: Could not load expected results: {e}")
            return {}
    
    def evaluate_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """
        Evaluate a single gold dataset
        
        Args:
            dataset_name: Name of the gold dataset (e.g., 'missing_values')
        
        Returns:
            Evaluation results with metrics
        """
        print(f"\n📊 Evaluating: {dataset_name}")
        print("=" * 60)
        
        # Find the dataset file
        dataset_path = None
        for ext in ['.csv', '.json']:
            candidate = self.gold_datasets_dir / f"{dataset_name}{ext}"
            if candidate.exists():
                dataset_path = candidate
                break
        
        if not dataset_path:
            return {
                'success': False,
                'error': f"Dataset file not found: {dataset_name}"
            }
        
        # Get expected results
        expected = self.expected_results.get(dataset_name, {})
        expected_issues = expected.get('expected_issues', [])
        expected_fixes = expected.get('expected_fixes', [])
        min_quality_score = expected.get('min_quality_score', 0)
        min_fix_success_rate = expected.get('min_fix_success_rate', 0)
        
        # Process the dataset
        result = self.orchestrator.process_dataset(str(dataset_path))
        
        if not result['success']:
            return {
                'success': False,
                'error': result.get('message', 'Processing failed'),
                'dataset': dataset_name
            }
        
        report = result.get('report')
        if not report:
            return {
                'success': False,
                'error': 'No report generated',
                'dataset': dataset_name
            }
        
        # Calculate issue detection metrics
        issue_metrics = self.metrics_calculator.calculate_issue_metrics(
            detected_issues=report.issues,
            expected_issues=expected_issues
        )
        
        # Calculate fix metrics
        fix_metrics = self.metrics_calculator.calculate_fix_metrics(
            applied_fixes=report.fixes,
            expected_fixes=expected_fixes
        )
        
        # Calculate quality metrics
        quality_metrics = self.metrics_calculator.calculate_quality_metrics(
            final_quality_score=report.quality_score,
            min_quality_score=min_quality_score
        )
        
        # Overall evaluation
        overall_pass = (
            issue_metrics['recall'] >= 70 and  # Found at least 70% of issues
            fix_metrics['success_rate'] >= min_fix_success_rate and
            quality_metrics['meets_threshold']
        )
        
        return {
            'success': True,
            'dataset': dataset_name,
            'dataset_path': str(dataset_path),
            'overall_pass': overall_pass,
            'issue_metrics': issue_metrics,
            'fix_metrics': fix_metrics,
            'quality_metrics': quality_metrics,
            'detected_issues_count': len(report.issues),
            'expected_issues_count': len(expected_issues),
            'applied_fixes_count': len(report.fixes),
            'expected_fixes_count': len(expected_fixes),
            'final_quality_score': report.quality_score
        }
    
    def evaluate_all(self) -> Dict[str, Any]:
        """
        Evaluate all gold datasets
        
        Returns:
            Summary of all evaluations
        """
        print("\n" + "=" * 60)
        print("🧪 DatasetDoctor Evaluation Suite")
        print("=" * 60)
        
        # Find all gold datasets
        gold_datasets = []
        for file in self.gold_datasets_dir.glob("*.csv"):
            dataset_name = file.stem
            if dataset_name in self.expected_results:
                gold_datasets.append(dataset_name)
        
        if not gold_datasets:
            return {
                'success': False,
                'error': 'No gold datasets found'
            }
        
        print(f"\nFound {len(gold_datasets)} gold datasets:")
        for ds in gold_datasets:
            print(f"  - {ds}")
        
        # Evaluate each dataset
        results = {}
        total_datasets = len(gold_datasets)
        passed_datasets = 0
        
        for dataset_name in gold_datasets:
            result = self.evaluate_dataset(dataset_name)
            results[dataset_name] = result
            
            if result.get('success') and result.get('overall_pass'):
                passed_datasets += 1
                print(f"  ✅ {dataset_name}: PASSED")
            elif result.get('success'):
                print(f"  ⚠️  {dataset_name}: PARTIAL (see details below)")
            else:
                print(f"  ❌ {dataset_name}: FAILED - {result.get('error', 'Unknown error')}")
        
        # Calculate overall metrics
        all_issue_metrics = [r.get('issue_metrics', {}) for r in results.values() if r.get('success')]
        all_fix_metrics = [r.get('fix_metrics', {}) for r in results.values() if r.get('success')]
        
        avg_precision = sum(m.get('precision', 0) for m in all_issue_metrics) / len(all_issue_metrics) if all_issue_metrics else 0
        avg_recall = sum(m.get('recall', 0) for m in all_issue_metrics) / len(all_issue_metrics) if all_issue_metrics else 0
        avg_f1 = sum(m.get('f1_score', 0) for m in all_issue_metrics) / len(all_issue_metrics) if all_issue_metrics else 0
        
        summary = {
            'success': True,
            'total_datasets': total_datasets,
            'passed_datasets': passed_datasets,
            'pass_rate': round((passed_datasets / total_datasets * 100), 2) if total_datasets > 0 else 0,
            'average_precision': round(avg_precision, 2),
            'average_recall': round(avg_recall, 2),
            'average_f1_score': round(avg_f1, 2),
            'results': results
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("📈 Evaluation Summary")
        print("=" * 60)
        print(f"Total Datasets: {total_datasets}")
        print(f"Passed: {passed_datasets} ({summary['pass_rate']}%)")
        print(f"Average Precision: {summary['average_precision']}%")
        print(f"Average Recall: {summary['average_recall']}%")
        print(f"Average F1 Score: {summary['average_f1_score']}%")
        print("=" * 60)
        
        return summary

