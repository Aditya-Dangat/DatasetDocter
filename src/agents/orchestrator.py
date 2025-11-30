"""
Orchestrator Agent - The "Manager"

This is the brain of DatasetDoctor. It coordinates all the other agents.

Think of it like a hospital manager:
- Receives a patient (dataset)
- Sends them to the right specialists (other agents)
- Coordinates the workflow
- Makes sure everything happens in the right order

Workflow:
1. Ingestor loads the dataset
2. Scanner finds problems
3. Fixer fixes the problems
4. Validator checks if fixes worked
5. Reporter creates the report
"""

from typing import Optional, Dict, Any
import time
from src.core.config import Config
from src.core.dataset import Dataset
from src.core.diagnostics import DiagnosticReport
from src.agents.ingestor import IngestorAgent
from src.agents.scanner import ScannerAgent
from src.agents.fixer import FixerAgent
from src.agents.validator import ValidatorAgent
from src.agents.reporter import ReporterAgent
from src.observability.logger import StructuredLogger
from src.observability.tracer import Tracer
from src.observability.metrics import MetricsCollector
from src.memory.session_service import InMemorySessionService
from src.memory.memory_bank import MemoryBank
from src.memory.context_manager import ContextManager
from src.communication.a2a_protocol import A2AProtocol
from src.tools.mcp_registry import get_registry
from src.tools.initialize_tools import ensure_tools_initialized


class OrchestratorAgent:
    """
    The Orchestrator - Coordinates all other agents
    
    This is the main controller. It doesn't do the actual work,
    but it tells other agents what to do and when.
    """
    
    def __init__(self):
        """Initialize the Orchestrator"""
        self.name = "OrchestratorAgent"
        
        # Initialize observability
        self.logger = StructuredLogger()
        self.tracer = Tracer()
        self.metrics = MetricsCollector()
        
        # Initialize memory & session management
        self.session_service = InMemorySessionService()
        self.memory_bank = MemoryBank()
        self.context_manager = ContextManager()  # Context engineering
        
        # Initialize A2A Protocol for agent communication
        self.a2a = A2AProtocol()
        
        # Initialize MCP tools registry
        ensure_tools_initialized()
        self.tool_registry = get_registry()
        
        # Initialize all agents
        self.ingestor = IngestorAgent()
        self.scanner = ScannerAgent()
        self.fixer = FixerAgent()
        self.validator = ValidatorAgent()
        self.reporter = ReporterAgent()
        
        # Register agents with A2A protocol
        self._register_agents()
    
    def process_dataset(self, filepath: str) -> Dict[str, Any]:
        """
        Main method - Process a dataset from start to finish
        
        This is the entry point. You call this with a file path,
        and it handles everything else.
        
        Args:
            filepath: Path to the dataset file
        
        Returns:
            Dictionary with results:
            {
                'success': True/False,
                'dataset': Dataset object (if successful),
                'report': DiagnosticReport,
                'message': Human-readable message
            }
        """
        # Start tracing and create session
        trace_id = self.tracer.start_trace("process_dataset")
        session_id = self.session_service.create_session(
            dataset_info={'filepath': filepath, 'trace_id': trace_id}
        )
        self.metrics.start_operation("process_dataset")
        self.logger.info(f"Starting dataset processing", trace_id=trace_id, session_id=session_id, filepath=filepath)
        
        print(f"🏥 DatasetDoctor: Starting processing of {filepath}")
        print("=" * 60)
        
        # Step 1: Ingest (Load the dataset)
        print("\n📥 Step 1: Ingesting dataset...")
        self.session_service.update_state(session_id, "ingesting", "IngestorAgent")
        self.metrics.start_operation("ingest")
        start_time = time.time()
        dataset, ingestion_errors = self.ingestor.ingest(filepath)
        ingest_duration = time.time() - start_time
        self.metrics.end_operation("ingest", success=(dataset is not None), duration=ingest_duration)
        self.tracer.add_span(trace_id, "ingest", "IngestorAgent", ingest_duration)
        if dataset:
            self.session_service.update_state(session_id, "ingested", "IngestorAgent", {"shape": dataset.shape})
            
            # Check if this is a previously cleaned file
            is_cleaned_file = 'cleaned' in filepath.lower() or '_cleaned_' in filepath
            if is_cleaned_file:
                print(f"   ℹ️  Note: This appears to be a previously cleaned file.")
                print(f"   ℹ️  Some issues may remain if they couldn't be safely auto-fixed.")
        
        if dataset is None:
            # Ingestion failed
            return {
                'success': False,
                'dataset': None,
                'report': ingestion_errors,
                'message': f"Failed to load dataset: {filepath}"
            }
        
        print(f"✅ Successfully loaded dataset: {dataset.name}")
        print(f"   Shape: {dataset.shape[0]} rows × {dataset.shape[1]} columns")
        
        # Context engineering: Create compact summary for large datasets
        if dataset.shape[0] > 1000:  # For large datasets, create summary first
            summary = self.context_manager.compact_dataset_summary(dataset)
            self.context_manager.cache_summary(dataset.name, summary)
            self.logger.info(f"Created compact summary for large dataset", 
                           trace_id=trace_id, summary_size_mb=summary['memory_usage_mb'])
        
        # Create a main diagnostic report
        main_report = DiagnosticReport(dataset.name)
        
        # Step 2: Scan (Find problems)
        print("\n🔍 Step 2: Scanning for issues...")
        self.session_service.update_state(session_id, "scanning", "ScannerAgent")
        
        # Example A2A: Scanner can query Fixer about fix strategies before scanning
        if main_report.issues:  # If we had issues from a previous scan
            self.a2a.notify("Orchestrator", "ScannerAgent", "scan_started", 
                          {"dataset_shape": dataset.shape})
        
        self.metrics.start_operation("scan")
        start_time = time.time()
        issues = self.scanner.scan(dataset)
        scan_duration = time.time() - start_time
        self.metrics.end_operation("scan", success=True, issues_found=len(issues), duration=scan_duration)
        self.tracer.add_span(trace_id, "scan", "ScannerAgent", scan_duration, {'issues_count': len(issues)})
        self.session_service.update_state(session_id, "scanned", "ScannerAgent", {"issues": len(issues)})
        
        # A2A: Scanner notifies Fixer about issues found
        if issues:
            self.a2a.notify("ScannerAgent", "FixerAgent", "issues_found", 
                          {"count": len(issues), "types": [i.type for i in issues]})
        for issue in issues:
            main_report.add_issue(issue)
        
        if issues:
            print(f"   ⚠️  Found {len(issues)} issue(s):")
            for issue in issues[:5]:  # Show first 5 issues
                print(f"      - {issue.description}")
            if len(issues) > 5:
                print(f"      ... and {len(issues) - 5} more")
        else:
            print("   ✅ No issues found! Dataset looks clean.")
        
        # Step 3: Fix (Apply fixes)
        print("\n🔧 Step 3: Applying fixes...")
        if main_report.issues:
            self.session_service.update_state(session_id, "fixing", "FixerAgent")
            
            # A2A: Fixer can query Validator about validation requirements
            validation_requirements = self.a2a.query(
                "FixerAgent", "ValidatorAgent",
                "What validation checks should I prepare for?",
                {"issue_types": [i.type for i in main_report.issues]}
            )
            
            # Check memory bank for similar patterns
            for issue in main_report.issues:
                similar_patterns = self.memory_bank.retrieve_similar_patterns({
                    'type': issue.type,
                    'column': issue.column,
                    'severity': issue.severity
                })
                if similar_patterns:
                    # Use learned pattern if available
                    best_pattern = similar_patterns[0]
                    self.logger.info(f"Using learned pattern from memory", 
                                   trace_id=trace_id, pattern=best_pattern)
            
            self.metrics.start_operation("fix")
            start_time = time.time()
            fixes = self.fixer.fix(dataset, main_report.issues)
            fix_duration = time.time() - start_time
            self.metrics.end_operation("fix", success=True, fixes_applied=len(fixes), duration=fix_duration)
            self.tracer.add_span(trace_id, "fix", "FixerAgent", fix_duration, {'fixes_count': len(fixes)})
            
            # A2A: Fixer notifies Validator that fixes are done
            self.a2a.notify("FixerAgent", "ValidatorAgent", "fixes_completed", 
                          {"fixes_count": len(fixes), "successful": sum(1 for f in fixes if f.success)})
            
            # Store successful fixes in memory
            for fix in fixes:
                if fix.success:
                    self.memory_bank.record_successful_fix(
                        fix.issue_type,
                        fix.method,
                        {'column': fix.column}
                    )
            
            self.session_service.update_state(session_id, "fixed", "FixerAgent", {"fixes": len(fixes)})
            for fix in fixes:
                main_report.add_fix(fix)
            
            if fixes:
                print(f"   ✅ Fixed {len(fixes)} issue(s):")
                for fix in fixes[:3]:  # Show first 3 fixes
                    print(f"      - {fix.description}")
                if len(fixes) > 3:
                    print(f"      ... and {len(fixes) - 3} more")
        else:
            print("   ℹ️  No issues to fix")
        
        # Step 4: Validate (Check fixes worked)
        print("\n✅ Step 4: Validating fixes...")
        self.metrics.start_operation("validate")
        start_time = time.time()
        validation_result = self.validator.validate(dataset, main_report)
        validate_duration = time.time() - start_time
        self.metrics.end_operation("validate", success=validation_result.get('success', False), duration=validate_duration)
        self.tracer.add_span(trace_id, "validate", "ValidatorAgent", validate_duration, validation_result)
        main_report.summary['validation'] = validation_result
        
        # Step 5: Report (Generate report)
        print("\n📊 Step 5: Generating report...")
        self.metrics.start_operation("report")
        start_time = time.time()
        report_files = self.reporter.generate_report(dataset, main_report)
        report_duration = time.time() - start_time
        self.metrics.end_operation("report", success=True, duration=report_duration)
        self.tracer.add_span(trace_id, "report", "ReporterAgent", report_duration)
        main_report.summary['report_files'] = report_files
        
        # End tracing and logging
        trace_info = self.tracer.end_trace(trace_id)
        self.metrics.end_operation("process_dataset", success=True, 
                                   quality_score=main_report.quality_score,
                                   total_duration=trace_info.get('total_duration', 0))
        self.logger.info(f"Processing complete", trace_id=trace_id, 
                        quality_score=main_report.quality_score,
                        issues_found=len(main_report.issues),
                        fixes_applied=len(main_report.fixes))
        
        # Auto-cleanup old files if enabled
        if Config.AUTO_CLEANUP_ENABLED:
            try:
                from src.utils.cleanup import FileCleanup
                cleanup = FileCleanup(
                    max_age_hours=Config.CLEANUP_MAX_AGE_HOURS,
                    keep_recent=Config.CLEANUP_KEEP_RECENT
                )
                cleanup_result = cleanup.cleanup_all(dry_run=False)
                if cleanup_result['total_deleted'] > 0:
                    self.logger.info(f"Auto-cleanup: Deleted {cleanup_result['total_deleted']} old files",
                                   trace_id=trace_id)
            except Exception as e:
                # Don't fail processing if cleanup fails
                self.logger.warning(f"Auto-cleanup failed: {e}", trace_id=trace_id)
        
        print("\n" + "=" * 60)
        print("✅ Processing complete!")
        
        return {
            'success': True,
            'dataset': dataset,
            'report': main_report,
            'message': f"Successfully processed {dataset.name}",
            'trace_id': trace_id
        }
    
    def _register_agents(self):
        """Register agents with A2A protocol for communication"""
        # Register handler functions for each agent
        # In a real implementation, each agent would have a handle_message method
        def fixer_handler(message):
            """Handle messages to FixerAgent"""
            if message.message_type == "query":
                # Fixer can respond to queries about fix strategies
                return {"response": "FixerAgent ready to apply fixes"}
            return None
        
        def validator_handler(message):
            """Handle messages to ValidatorAgent"""
            if message.message_type == "query":
                return {"response": "ValidatorAgent ready to validate"}
            return None
        
        self.a2a.register_agent("FixerAgent", fixer_handler)
        self.a2a.register_agent("ValidatorAgent", validator_handler)
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of the orchestrator and all agents"""
        # Get tool information
        tools_info = self.tool_registry.list_tools() if hasattr(self, 'tool_registry') else []
        tools_by_category = {}
        for tool in tools_info:
            category = tool.get('category', 'other')
            tools_by_category.setdefault(category, []).append(tool['name'])
        
        return {
            'orchestrator': {
                'name': self.name,
                'status': 'ready'
            },
            'agents': {
                'ingestor': self.ingestor.get_info(),
                'scanner': self.scanner.get_info(),
                'fixer': self.fixer.get_info(),
                'validator': self.validator.get_info(),
                'reporter': self.reporter.get_info(),
            },
            'mcp_tools': {
                'total_tools': len(tools_info),
                'tools_by_category': tools_by_category,
                'available_categories': list(tools_by_category.keys())
            },
            'a2a_messages': len(self.a2a.message_history)
        }

