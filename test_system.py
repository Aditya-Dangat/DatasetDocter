#!/usr/bin/env python3
"""
Quick System Test - Verifies Everything Works

Run this to test all components of DatasetDoctor
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    try:
        from src.core.config import Config
        from src.core.dataset import Dataset
        from src.core.diagnostics import Issue, Fix, DiagnosticReport
        from src.agents.orchestrator import OrchestratorAgent
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
        from src.communication.a2a_protocol import A2AProtocol, A2AMessage
        from src.llm.gemini_client import GeminiClient
        print("   ✅ All imports successful")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\n🔍 Testing configuration...")
    try:
        from src.core.config import Config
        Config.validate()
        print(f"   ✅ Config valid")
        print(f"   - Upload folder: {Config.UPLOAD_FOLDER}")
        print(f"   - Output folder: {Config.OUTPUT_FOLDER}")
        print(f"   - Logs folder: {Config.LOGS_FOLDER}")
        return True
    except Exception as e:
        print(f"   ❌ Config error: {e}")
        return False

def test_agents():
    """Test agent initialization"""
    print("\n🔍 Testing agents...")
    try:
        from src.agents.orchestrator import OrchestratorAgent
        orchestrator = OrchestratorAgent()
        status = orchestrator.get_status()
        print(f"   ✅ Orchestrator initialized")
        print(f"   - Agents registered: {len(status['agents'])}")
        print(f"   - A2A messages: {status.get('a2a_messages', 0)}")
        return True
    except Exception as e:
        print(f"   ❌ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_observability():
    """Test observability components"""
    print("\n🔍 Testing observability...")
    try:
        from src.observability.logger import StructuredLogger
        from src.observability.tracer import Tracer
        from src.observability.metrics import MetricsCollector
        
        logger = StructuredLogger()
        logger.info("Test log message", trace_id="test-123")
        
        tracer = Tracer()
        trace_id = tracer.start_trace("test_operation")
        tracer.add_span(trace_id, "test_span", "TestAgent", 0.5)
        trace_info = tracer.end_trace(trace_id)
        
        metrics = MetricsCollector()
        metrics.start_operation("test_op")
        metrics.end_operation("test_op", success=True)
        
        print("   ✅ Logger working")
        print("   ✅ Tracer working")
        print("   ✅ Metrics working")
        return True
    except Exception as e:
        print(f"   ❌ Observability test failed: {e}")
        return False

def test_memory():
    """Test memory and session management"""
    print("\n🔍 Testing memory & session...")
    try:
        from src.memory.session_service import InMemorySessionService
        from src.memory.memory_bank import MemoryBank
        
        session_service = InMemorySessionService()
        session_id = session_service.create_session(dataset_info={"test": True})
        session = session_service.get_session(session_id)
        
        memory_bank = MemoryBank()
        memory_bank.store_pattern("test_pattern", {"type": "test"}, 0.9)
        patterns = memory_bank.retrieve_similar_patterns({"type": "test"})
        
        print("   ✅ Session service working")
        print("   ✅ Memory bank working")
        return True
    except Exception as e:
        print(f"   ❌ Memory test failed: {e}")
        return False

def test_a2a():
    """Test A2A protocol"""
    print("\n🔍 Testing A2A Protocol...")
    try:
        from src.communication.a2a_protocol import A2AProtocol, A2AMessage
        
        protocol = A2AProtocol()
        
        def handler(message):
            return {"response": "OK"}
        
        protocol.register_agent("TestAgent", handler)
        result = protocol.query("Agent1", "TestAgent", "Test question")
        
        print("   ✅ A2A Protocol working")
        print(f"   - Messages in history: {len(protocol.message_history)}")
        return True
    except Exception as e:
        print(f"   ❌ A2A test failed: {e}")
        return False

def test_full_pipeline():
    """Test the full pipeline with sample data"""
    print("\n🔍 Testing full pipeline...")
    try:
        from src.agents.orchestrator import OrchestratorAgent
        
        sample_file = Path("examples/sample_messy_data.csv")
        if not sample_file.exists():
            print(f"   ⚠️  Sample file not found: {sample_file}")
            return False
        
        orchestrator = OrchestratorAgent()
        result = orchestrator.process_dataset(str(sample_file))
        
        if result['success']:
            print("   ✅ Full pipeline successful")
            print(f"   - Quality score: {result['report'].quality_score}")
            print(f"   - Issues found: {len(result['report'].issues)}")
            print(f"   - Fixes applied: {len(result['report'].fixes)}")
            return True
        else:
            print(f"   ❌ Pipeline failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"   ❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 DatasetDoctor System Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Agents", test_agents),
        ("Observability", test_observability),
        ("Memory & Session", test_memory),
        ("A2A Protocol", test_a2a),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ {name} test crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

