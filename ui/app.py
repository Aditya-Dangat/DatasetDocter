"""
Flask Web Application for DatasetDoctor

Simple web interface to upload datasets and view results.
"""

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config import Config
from src.agents.orchestrator import OrchestratorAgent

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_UPLOAD_SIZE
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)

# Initialize orchestrator
orchestrator = OrchestratorAgent()


@app.route('/')
def index():
    """Home page - upload form"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'unknown'
            return jsonify({
                'error': f'Invalid file type: .{ext}',
                'allowed': list(Config.ALLOWED_EXTENSIONS)
            }), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the dataset
        result = orchestrator.process_dataset(filepath)
        
        if result['success']:
            # Get report files
            report_files = result['report'].summary.get('report_files', {}) if result.get('report') else {}
            
            # Convert report_files paths to just filenames for download
            report_files_clean = {}
            for key, path in report_files.items():
                if path:
                    report_files_clean[key] = os.path.basename(path)
            
            # Safely get report data
            report = result.get('report')
            dataset = result.get('dataset')
            
            if not dataset:
                return jsonify({
                    'success': False,
                    'error': 'Dataset processing failed - no dataset returned'
                }), 400
            
            # Prepare issues and fixes for frontend
            issues_data = []
            if report and hasattr(report, 'issues'):
                for issue in report.issues:
                    # Extract AI insight from details if available
                    gemini_insight = None
                    if hasattr(issue, 'details') and issue.details and 'gemini_insight' in issue.details:
                        gemini_insight = issue.details.get('gemini_insight')
                    
                    issues_data.append({
                        'type': issue.type,
                        'description': issue.description,
                        'column': issue.column,
                        'severity': issue.severity,
                        'gemini_insight': gemini_insight  # Include full AI insight
                    })
            
            fixes_data = []
            if report and hasattr(report, 'fixes'):
                for fix in report.fixes:
                    # Convert numpy types to native Python types for JSON serialization
                    fixes_data.append({
                        'method': fix.method,
                        'description': fix.description,
                        'column': fix.column,
                        'success': bool(fix.success)  # Convert numpy bool_ to Python bool
                    })
            
            # Check if this is a cleaned file
            is_cleaned = 'cleaned' in dataset.name.lower() or '_cleaned_' in dataset.name.lower()
            
            # Ensure counts are non-negative integers
            total_issues = max(0, len(report.issues) if report and hasattr(report, 'issues') else 0)
            total_fixes = max(0, len(report.fixes) if report and hasattr(report, 'fixes') else 0)
            quality_score = max(0.0, min(100.0, float(report.quality_score) if report and hasattr(report, 'quality_score') else 0.0))
            
            return jsonify({
                'success': True,
                'dataset_name': dataset.name,
                'shape': list(dataset.shape),
                'columns': dataset.get_columns(),
                'quality_score': quality_score,
                'total_issues': total_issues,
                'total_fixes': total_fixes,
                'issues': issues_data,
                'fixes': fixes_data,
                'report_files': report_files_clean,
                'validation': report.summary.get('validation', {}) if report else {},
                'is_cleaned_file': is_cleaned,
                'cleaned_file_note': 'This appears to be a previously cleaned file. Some issues may remain if they couldn\'t be safely auto-fixed, or new issues may have been detected.' if is_cleaned else None
            })
        else:
            # Handle failure case
            report = result.get('report')
            error_message = result.get('message', 'Unknown error occurred')
            
            # Extract issues safely
            issues_list = []
            if report and hasattr(report, 'issues'):
                try:
                    issues_list = [i.description for i in report.issues]
                except:
                    issues_list = []
            
            return jsonify({
                'success': False,
                'error': error_message,
                'issues': issues_list
            }), 400
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in upload: {error_details}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Download generated files"""
    # Use absolute path from project root
    filepath = os.path.join(project_root, Config.OUTPUT_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


@app.route('/report/<filename>')
def view_report(filename):
    """View HTML report"""
    # Use absolute path from project root
    filepath = os.path.join(project_root, Config.OUTPUT_FOLDER, filename)
    if os.path.exists(filepath) and filename.endswith('.html'):
        return send_file(filepath)
    return jsonify({'error': 'Report not found'}), 404

@app.route('/health')
def health():
    """Health check endpoint for Cloud Run"""
    return jsonify({
        'status': 'healthy',
        'service': 'DatasetDoctor',
        'version': '1.0.0'
    }), 200

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


if __name__ == '__main__':
    Config.validate()
    print(f"\n🌐 Starting DatasetDoctor Web UI...")
    print(f"   Open your browser to: http://localhost:{Config.PORT}")
    print(f"   Press Ctrl+C to stop\n")
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.FLASK_DEBUG)

