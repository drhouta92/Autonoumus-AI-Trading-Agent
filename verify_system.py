#!/usr/bin/env python3
"""
System Verification Script
Tests all core modules and validates the Micro-Cap AI Agent 2.5 setup
"""

import sys
import os

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)

def test_imports():
    """Test all module imports"""
    print_header("TESTING MODULE IMPORTS")
    
    modules = [
        'config',
        'utils',
        'brain_manager',
        'persistence_manager',
        'offline_learner',
        'micro_cap_discovery',
        'advanced_technical_analyzer',
        'micro_cap_risk_manager',
        'decision_engine',
        'agent_orchestrator',
        'data_fetcher',
        'catalyst_detector'
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n⚠️  {len(failed)} modules failed to import")
        return False
    else:
        print(f"\n✅ All {len(modules)} modules imported successfully!")
        return True

def test_config():
    """Test configuration"""
    print_header("TESTING CONFIGURATION")
    
    try:
        import config
        
        # Check API keys exist (even if placeholder)
        assert hasattr(config, 'FINNHUB_API_KEY'), "Missing FINNHUB_API_KEY"
        assert hasattr(config, 'ALPHA_VANTAGE_API_KEY'), "Missing ALPHA_VANTAGE_API_KEY"
        assert hasattr(config, 'POLYGON_API_KEY'), "Missing POLYGON_API_KEY"
        print("✅ API keys configured")
        
        # Check data sources
        assert hasattr(config, 'DATA_SOURCES'), "Missing DATA_SOURCES"
        assert len(config.DATA_SOURCES) > 0, "DATA_SOURCES is empty"
        print("✅ Data sources configured")
        
        # Check micro-cap parameters
        assert hasattr(config, 'MICRO_CAP_MAX_MARKET_CAP'), "Missing micro-cap parameters"
        assert hasattr(config, 'PENNY_STOCK_MAX_PRICE'), "Missing penny stock parameters"
        print("✅ Micro-cap parameters configured")
        
        # Check risk management
        assert hasattr(config, 'MAX_POSITION_SIZE'), "Missing risk parameters"
        assert hasattr(config, 'STOP_LOSS_PERCENT'), "Missing stop loss"
        print("✅ Risk management configured")
        
        # Check brain parameters
        assert hasattr(config, 'BRAIN_PERFORMANCE_THRESHOLD'), "Missing brain parameters"
        print("✅ Brain evolution configured")
        
        print("\n✅ Configuration test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration test failed: {e}")
        return False

def test_brain_manager():
    """Test brain manager"""
    print_header("TESTING BRAIN MANAGER")
    
    try:
        from brain_manager import BrainManager
        import config
        
        # Create brain
        brain = BrainManager(config)
        print("✅ Brain manager created")
        
        # Check current brain
        assert brain.current_brain is not None, "No current brain"
        print(f"✅ Brain generation: {brain.generation}")
        print(f"✅ Brain status: {brain.current_brain.kill_gate_status}")
        
        # Get statistics
        stats = brain.get_brain_statistics()
        assert 'current_generation' in stats, "Missing statistics"
        print(f"✅ Brain statistics available")
        
        # Record decision
        brain.record_decision('TEST', 'BUY', 0.75)
        assert len(brain.current_brain.decision_history) > 0, "Decision not recorded"
        print("✅ Decision recording works")
        
        # Clean up test files
        if os.path.exists('brain_state.json'):
            os.remove('brain_state.json')
        if os.path.exists('brain_history.db'):
            os.remove('brain_history.db')
        print("✅ Cleaned up test files")
        
        print("\n✅ Brain manager test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Brain manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_utilities():
    """Test utility functions"""
    print_header("TESTING UTILITIES")
    
    try:
        import utils
        
        # Test formatting
        assert '$1.23M' == utils.format_currency(1_234_567), "Currency format failed"
        print("✅ Currency formatting")
        
        assert '12.3%' == utils.format_percent(0.123), "Percent format failed"
        print("✅ Percent formatting")
        
        # Test calculations
        prices = [100, 105, 103, 108, 110]
        returns = utils.calculate_returns(prices)
        assert len(returns) == 4, "Returns calculation failed"
        print("✅ Returns calculation")
        
        # Test validation
        assert utils.validate_symbol('AAPL') == True, "Symbol validation failed"
        assert utils.validate_symbol('') == False, "Empty symbol should fail"
        print("✅ Symbol validation")
        
        # Test normalization
        assert utils.normalize_symbol(' aapl ') == 'AAPL', "Symbol normalization failed"
        print("✅ Symbol normalization")
        
        print("\n✅ Utilities test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Utilities test failed: {e}")
        return False

def test_file_structure():
    """Test file structure"""
    print_header("TESTING FILE STRUCTURE")
    
    required_files = [
        'main.py',
        'config.py',
        'brain_manager.py',
        'micro_cap_discovery.py',
        'advanced_technical_analyzer.py',
        'micro_cap_risk_manager.py',
        'decision_engine.py',
        'persistence_manager.py',
        'offline_learner.py',
        'agent_orchestrator.py',
        'utils.py',
        'data_fetcher.py',
        'catalyst_detector.py',
        'requirements.txt',
        'README.md',
        'ARCHITECTURE.md',
        'QUICKSTART.md',
        '.gitignore'
    ]
    
    missing = []
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename} (missing)")
            missing.append(filename)
    
    if missing:
        print(f"\n⚠️  {len(missing)} files missing")
        return False
    else:
        print(f"\n✅ All {len(required_files)} required files present!")
        return True

def run_all_tests():
    """Run all verification tests"""
    print_header("MICRO-CAP AI AGENT 2.5 - SYSTEM VERIFICATION")
    print("Testing all core components...\n")
    
    results = {
        'File Structure': test_file_structure(),
        'Module Imports': test_imports(),
        'Configuration': test_config(),
        'Utilities': test_utilities(),
        'Brain Manager': test_brain_manager()
    }
    
    print_header("VERIFICATION SUMMARY")
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\n{passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ System is ready for deployment")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please fix the issues above before deployment")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
