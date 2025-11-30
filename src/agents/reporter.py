"""
Reporter Agent - The "Secretary" That Writes Reports

This agent's job is to create the final report.

Think of it like a secretary writing up the medical summary:
- Creates a human-readable HTML report
- Generates a machine-readable JSON file
- Creates a Python script to reproduce the cleaning
- Saves the cleaned dataset
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from src.core.dataset import Dataset
from src.core.diagnostics import DiagnosticReport
from src.llm.gemini_client import GeminiClient


class ReporterAgent:
    """
    The Reporter Agent - Generates final reports
    
    Simple workflow:
        1. Receives Dataset and DiagnosticReport
        2. Generates HTML report (human-readable)
        3. Generates JSON report (machine-readable)
        4. Generates Python cleaning script (reproducible)
        5. Saves cleaned dataset
    """
    
    def __init__(self, output_dir: str = "outputs"):
        """Initialize the Reporter Agent"""
        self.name = "ReporterAgent"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.gemini = GeminiClient()  # AI assistant for generating explanations
    
    def generate_report(self, dataset: Dataset, report: DiagnosticReport) -> Dict[str, Any]:
        """
        Main method - Generate all reports
        
        Args:
            dataset: The cleaned Dataset
            report: The DiagnosticReport with all issues and fixes
        
        Returns:
            Dictionary with paths to generated files
        """
        print(f"   📊 Generating reports...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = dataset.name.replace('.csv', '').replace('.json', '')
        
        # Generate JSON report
        json_path = self._generate_json_report(report, base_name, timestamp)
        
        # Generate Python script
        script_path = self._generate_cleaning_script(dataset, report, base_name, timestamp)
        
        # Save cleaned dataset
        cleaned_path = self._save_cleaned_dataset(dataset, base_name, timestamp)
        
        # Generate HTML report
        html_path = self._generate_html_report(dataset, report, base_name, timestamp)
        
        # Generate AI summary if Gemini is available
        ai_summary = None
        if self.gemini.is_available():
            try:
                ai_summary = self._generate_ai_summary(dataset, report)
                print(f"   🤖 AI Summary generated")
            except Exception as e:
                print(f"   ⚠️  AI summary generation failed: {e}")
        
        result = {
            'json_report': str(json_path),
            'python_script': str(script_path),
            'cleaned_dataset': str(cleaned_path),
            'html_report': str(html_path),
            'ai_summary': ai_summary
        }
        
        print(f"   ✅ Reports generated:")
        print(f"      - JSON: {json_path.name}")
        print(f"      - Python Script: {script_path.name}")
        print(f"      - Cleaned Dataset: {cleaned_path.name}")
        print(f"      - HTML Report: {html_path.name}")
        if ai_summary:
            print(f"      - AI Summary: Generated")
        
        return result
    
    def _generate_json_report(self, report: DiagnosticReport, base_name: str, timestamp: str) -> Path:
        """Generate machine-readable JSON report"""
        json_path = self.output_dir / f"{base_name}_report_{timestamp}.json"
        
        report_dict = report.to_dict()
        report_dict['generated_at'] = datetime.now().isoformat()
        
        with open(json_path, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        return json_path
    
    def _generate_cleaning_script(self, dataset: Dataset, report: DiagnosticReport, base_name: str, timestamp: str) -> Path:
        """Generate Python script to reproduce the cleaning"""
        script_path = self.output_dir / f"{base_name}_cleaning_script_{timestamp}.py"
        
        script_lines = [
            "# DatasetDoctor - Reproducible Cleaning Script",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Dataset: {dataset.name}",
            "",
            "import pandas as pd",
            "",
            "# Load original dataset",
            f"df = pd.read_csv('{dataset.name}')",
            "",
            "# Applied fixes:",
            ""
        ]
        
        # Add code for each fix
        for fix in report.fixes:
            if fix.issue_type == "missing_values":
                if fix.method == "median_imputation":
                    script_lines.append(f"# {fix.description}")
                    script_lines.append(f"df['{fix.column}'].fillna(df['{fix.column}'].median(), inplace=True)")
                elif fix.method == "mode_imputation":
                    script_lines.append(f"# {fix.description}")
                    script_lines.append(f"df['{fix.column}'].fillna(df['{fix.column}'].mode()[0], inplace=True)")
                script_lines.append("")
            elif fix.issue_type == "type_inconsistency":
                script_lines.append(f"# {fix.description}")
                script_lines.append(f"df['{fix.column}'] = pd.to_numeric(df['{fix.column}'], errors='coerce')")
                script_lines.append(f"df['{fix.column}'].fillna(df['{fix.column}'].median(), inplace=True)")
                script_lines.append("")
            elif fix.issue_type == "duplicates":
                script_lines.append(f"# {fix.description}")
                script_lines.append("df.drop_duplicates(inplace=True, keep='first')")
                script_lines.append("")
        
        script_lines.extend([
            "# Save cleaned dataset",
            f"df.to_csv('{base_name}_cleaned.csv', index=False)",
            "",
            "print('Dataset cleaned successfully!')"
        ])
        
        with open(script_path, 'w') as f:
            f.write('\n'.join(script_lines))
        
        return script_path
    
    def _save_cleaned_dataset(self, dataset: Dataset, base_name: str, timestamp: str) -> Path:
        """Save the cleaned dataset"""
        cleaned_path = self.output_dir / f"{base_name}_cleaned_{timestamp}.csv"
        dataset.save_cleaned(str(cleaned_path))
        return cleaned_path
    
    def _generate_html_report(self, dataset: Dataset, report: DiagnosticReport, base_name: str, timestamp: str) -> Path:
        """Generate human-readable HTML report with modern UI"""
        html_path = self.output_dir / f"{base_name}_report_{timestamp}.html"
        
        summary = report.get_summary()
        validation = report.summary.get('validation', {})
        quality_score = summary['quality_score']
        total_issues = summary['total_issues']
        total_fixes = summary['total_fixes']
        
        # Count critical/high priority issues
        critical_count = sum(1 for i in report.issues if i.severity in ['critical', 'high'])
        
        # Get issue icons
        def get_issue_icon(issue_type):
            icons = {
                'missing_values': '🔗',
                'type_inconsistency': '📅',
                'duplicates': '📋',
                'outliers': '📊'
            }
            return icons.get(issue_type, '⚠️')
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DatasetDoctor Report - {dataset.name}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary-purple: #7C3AED;
            --primary-blue: #3B82F6;
            --light-purple: #F3E8FF;
            --green: #10B981;
            --orange: #F59E0B;
            --red: #EF4444;
            --gray-50: #F9FAFB;
            --gray-100: #F3F4F6;
            --gray-200: #E5E7EB;
            --gray-300: #D1D5DB;
            --gray-500: #6B7280;
            --gray-600: #4B5563;
            --gray-700: #374151;
            --gray-900: #111827;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(180deg, #F3E8FF 0%, #FFFFFF 100%);
            min-height: 100vh;
            padding: 20px;
            position: relative;
        }}
        
        .background-animation {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            pointer-events: none;
            overflow: hidden;
        }}
        
        .background-animation::before,
        .background-animation::after {{
            content: '';
            position: absolute;
            border-radius: 50%;
            opacity: 0.1;
            animation: float 20s infinite ease-in-out;
        }}
        
        .background-animation::before {{
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, var(--primary-purple) 0%, transparent 70%);
            top: -250px;
            left: -250px;
        }}
        
        .background-animation::after {{
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, var(--primary-blue) 0%, transparent 70%);
            bottom: -200px;
            right: -200px;
            animation-delay: 10s;
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translate(0, 0) scale(1); }}
            33% {{ transform: translate(30px, -30px) scale(1.1); }}
            66% {{ transform: translate(-20px, 20px) scale(0.9); }}
        }}
        
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 40px;
            animation: fadeInDown 0.8s ease-out;
        }}
        
        .logo {{
            display: inline-block;
            margin-bottom: 20px;
        }}
        
        .logo-icon {{
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, var(--primary-purple) 0%, var(--primary-blue) 100%);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            box-shadow: 0 10px 30px rgba(124, 58, 237, 0.3);
        }}
        
        .logo-icon svg {{
            width: 36px;
            height: 36px;
        }}
        
        header h1 {{
            font-size: 40px;
            font-weight: 700;
            color: var(--gray-900);
            margin-bottom: 10px;
            background: linear-gradient(135deg, var(--primary-purple) 0%, var(--primary-blue) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .subtitle {{
            color: var(--gray-600);
            font-size: 16px;
            font-weight: 400;
        }}
        
        .report-meta {{
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }}
        
        .meta-item {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        
        .meta-label {{
            font-size: 12px;
            color: var(--gray-500);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .meta-value {{
            font-size: 16px;
            font-weight: 600;
            color: var(--gray-900);
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .card-title {{
            font-size: 12px;
            font-weight: 600;
            color: var(--gray-500);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .card-badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .card-badge.critical {{
            background: rgba(239, 68, 68, 0.1);
            color: var(--red);
        }}
        
        .card-badge.auto {{
            background: rgba(59, 130, 246, 0.1);
            color: var(--primary-blue);
        }}
        
        .card-content {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        
        .card-value-wrapper {{
            display: flex;
            align-items: baseline;
            gap: 8px;
        }}
        
        .card-value {{
            font-size: 40px;
            font-weight: 700;
            color: var(--gray-900);
        }}
        
        .card-unit {{
            font-size: 24px;
            font-weight: 500;
            color: var(--gray-500);
        }}
        
        .card-subtitle {{
            font-size: 14px;
            color: var(--gray-500);
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: var(--gray-200);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--green) 0%, #34D399 100%);
            border-radius: 4px;
            width: {quality_score}%;
            transition: width 1s ease-out;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .dashboard-section {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        }}
        
        .dashboard-section h3 {{
            font-size: 18px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 20px;
        }}
        
        .overview-content {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        
        .overview-item {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .overview-row {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }}
        
        .overview-label {{
            font-size: 12px;
            font-weight: 600;
            color: var(--gray-500);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .overview-value {{
            font-size: 24px;
            font-weight: 700;
            color: var(--gray-900);
        }}
        
        .issues-log-section {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            margin-bottom: 30px;
        }}
        
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }}
        
        .section-header h3 {{
            font-size: 18px;
            font-weight: 600;
            color: var(--gray-900);
        }}
        
        .priority-badge {{
            padding: 6px 16px;
            background: rgba(239, 68, 68, 0.1);
            color: var(--red);
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .issues-list {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        
        .issue-item {{
            display: flex;
            align-items: flex-start;
            gap: 16px;
            padding: 20px;
            background: var(--gray-50);
            border-radius: 16px;
            border-left: 4px solid var(--red);
            transition: all 0.3s ease;
        }}
        
        .issue-item:hover {{
            transform: translateX(4px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }}
        
        .issue-icon {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            flex-shrink: 0;
            background: rgba(239, 68, 68, 0.1);
        }}
        
        .issue-content {{
            flex: 1;
        }}
        
        .issue-title {{
            font-size: 16px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 8px;
        }}
        
        .issue-description {{
            font-size: 14px;
            color: var(--gray-600);
            margin-bottom: 12px;
            line-height: 1.5;
        }}
        
        .issue-action {{
            display: inline-block;
            padding: 6px 12px;
            background: white;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 500;
            color: var(--gray-700);
            margin-bottom: 8px;
        }}
        
        .issue-status {{
            display: inline-block;
            padding: 4px 12px;
            background: rgba(16, 185, 129, 0.1);
            color: var(--green);
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .fixes-section {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            margin-bottom: 30px;
        }}
        
        .fix-item {{
            display: flex;
            align-items: flex-start;
            gap: 16px;
            padding: 20px;
            background: var(--gray-50);
            border-radius: 16px;
            border-left: 4px solid var(--green);
            margin-bottom: 16px;
        }}
        
        .fix-icon {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            flex-shrink: 0;
            background: rgba(16, 185, 129, 0.1);
        }}
        
        .fix-content {{
            flex: 1;
        }}
        
        .fix-title {{
            font-size: 16px;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 8px;
        }}
        
        .fix-description {{
            font-size: 14px;
            color: var(--gray-600);
            margin-bottom: 12px;
        }}
        
        footer {{
            text-align: center;
            padding: 40px 0;
            color: var(--gray-500);
            font-size: 14px;
        }}
        
        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
            
            .summary-cards {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="background-animation"></div>
    <div class="container">
        <header>
            <div class="logo">
                <div class="logo-icon">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 17L12 22L22 17" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 12L12 17L22 12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
            <h1>DatasetDoctor Report</h1>
            <p class="subtitle">Data Quality Analysis Report</p>
        </header>
        
        <div class="report-meta">
            <div class="meta-item">
                <span class="meta-label">Dataset</span>
                <span class="meta-value">{dataset.name}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Generated</span>
                <span class="meta-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Shape</span>
                <span class="meta-value">{dataset.shape[0]} rows × {dataset.shape[1]} columns</span>
            </div>
        </div>
        
        <div class="summary-cards">
            <div class="card quality-card">
                <div class="card-header">
                    <span class="card-title">QUALITY SCORE</span>
                </div>
                <div class="card-content">
                    <div class="card-value-wrapper">
                        <span class="card-value">{quality_score:.1f}</span>
                        <span class="card-unit">/ 100</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                </div>
            </div>
            <div class="card issues-card">
                <div class="card-header">
                    <span class="card-title">ISSUES DETECTED</span>
                    {f'<span class="card-badge critical">{critical_count} Critical</span>' if critical_count > 0 else ''}
                </div>
                <div class="card-content">
                    <div class="card-value">{total_issues}</div>
                    <div class="card-subtitle">Across {dataset.shape[1]} columns</div>
                </div>
            </div>
            <div class="card fixes-card">
                <div class="card-header">
                    <span class="card-title">AUTO-FIXES APPLIED</span>
                    <span class="card-badge auto">Auto</span>
                </div>
                <div class="card-content">
                    <div class="card-value">{total_fixes}</div>
                    <div class="card-subtitle">Ready for export</div>
                </div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="dashboard-section dataset-overview">
                <h3>Dataset Overview</h3>
                <div class="overview-content">
                    <div class="overview-item">
                        <span class="overview-label">File</span>
                        <span class="overview-value">{dataset.name}</span>
                    </div>
                    <div class="overview-row">
                        <div class="overview-item">
                            <span class="overview-label">ROWS</span>
                            <span class="overview-value">{dataset.shape[0]:,}</span>
                        </div>
                        <div class="overview-item">
                            <span class="overview-label">COLUMNS</span>
                            <span class="overview-value">{dataset.shape[1]}</span>
                        </div>
                        <div class="overview-item">
                            <span class="overview-label">SIZE</span>
                            <span class="overview-value">{(dataset.shape[0] * dataset.shape[1] * 10 / 1024):.2f} KB</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="dashboard-section export-section" style="background: linear-gradient(135deg, #1F2937 0%, #111827 100%); color: white;">
                <h3 style="color: white;">Files Generated</h3>
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 12px;">
                        <span style="font-size: 20px;">📁</span>
                        <span style="flex: 1; font-size: 14px;">{base_name}_cleaned_{timestamp}.csv</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 12px;">
                        <span style="font-size: 20px;">🐍</span>
                        <span style="flex: 1; font-size: 14px;">{base_name}_cleaning_script_{timestamp}.py</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 12px;">
                        <span style="font-size: 20px;">{{ }}</span>
                        <span style="flex: 1; font-size: 14px;">{base_name}_report_{timestamp}.json</span>
                    </div>
                </div>
                <p style="font-size: 12px; color: rgba(255,255,255,0.6); text-align: center; margin-top: 20px;">
                    Your file is processed locally. No data is stored on our servers.
                </p>
            </div>
        </div>
"""
        
        # Issues section
        if report.issues:
            html_content += f"""
        <div class="issues-log-section">
            <div class="section-header">
                <h3>Issues & Fixes Log</h3>
                <span class="priority-badge">{critical_count} High Priority</span>
            </div>
            <div class="issues-list">
"""
            for issue in report.issues:
                icon = get_issue_icon(issue.type)
                html_content += f"""
                <div class="issue-item">
                    <div class="issue-icon">{icon}</div>
                    <div class="issue-content">
                        <div class="issue-title">{issue.type.replace('_', ' ').title()} in '{issue.column or "Unknown"}'</div>
                        <div class="issue-description">{issue.description}</div>
                        <div class="issue-action">Auto-detected</div>
                        <div class="issue-status">Fixed</div>
                    </div>
                </div>
"""
            html_content += """
            </div>
        </div>
"""
        
        # Fixes section
        if report.fixes:
            html_content += """
        <div class="fixes-section">
            <h3>Fixes Applied</h3>
"""
            for fix in report.fixes:
                status_icon = "✅" if fix.success else "❌"
                status_text = "Success" if fix.success else "Failed"
                html_content += f"""
            <div class="fix-item">
                <div class="fix-icon">🔧</div>
                <div class="fix-content">
                    <div class="fix-title">{fix.method.replace('_', ' ').title()} - {fix.column or 'N/A'}</div>
                    <div class="fix-description">{fix.description}</div>
                    <div class="issue-status">{status_icon} {status_text}</div>
                </div>
            </div>
"""
            html_content += """
        </div>
"""
        
        html_content += f"""
        <footer>
            <p>© 2025 DatasetDoctor. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>
"""
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)  # ✅ CORRECT - no .encode() needed
        
        return html_path
    
    def _generate_ai_summary(self, dataset: Dataset, report: DiagnosticReport) -> str:
        """
        Generate an AI-powered summary of the data quality report
        
        Uses Gemini to create a natural language summary of:
        - What issues were found
        - What fixes were applied
        - Overall data quality assessment
        """
        summary = report.get_summary()
        
        prompt_context = {
            'dataset_name': dataset.name,
            'shape': dataset.shape,
            'total_issues': summary.get('total_issues', 0),
            'total_fixes': summary.get('total_fixes', 0),
            'quality_score': summary.get('quality_score', 0),
            'issues_by_type': summary.get('issues_by_type', {}),
            'issues_by_severity': summary.get('issues_by_severity', {})
        }
        
        return self.gemini.generate_explanation(
            fix_applied=f"Processed dataset with {summary.get('total_issues', 0)} issues and {summary.get('total_fixes', 0)} fixes",
            before_state={'quality_score': 0, 'issues': summary.get('total_issues', 0)},
            after_state={'quality_score': summary.get('quality_score', 0), 'remaining_issues': 0}
        )
    
    def get_info(self) -> dict:
        """Get information about this agent"""
        gemini_status = "✅ Active" if self.gemini.is_available() else "❌ Not configured"
        return {
            'name': self.name,
            'role': 'Report Generation',
            'description': 'Generates HTML, JSON reports and Python cleaning scripts',
            'gemini_integration': gemini_status,
            'gemini_usage_count': self.gemini.get_usage_count() if self.gemini.is_available() else 0
        }

