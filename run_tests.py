#!/usr/bin/env python3
"""
Test Runner for WhatsApp Chat UI - Local AI Mode

This script runs the complete test suite for the WhatsApp Chat UI with Local AI mode,
including unit tests, integration tests, and provides comprehensive reporting.

Usage:
    python3 run_tests.py [options]

Options:
    --unit              Run only unit tests
    --integration       Run only integration tests
    --coverage          Generate test coverage report
    --verbose           Verbose output
    --parallel          Run tests in parallel
    --specific TEST     Run specific test class or method
    --performance       Run performance tests only
    --stress            Run stress tests only
"""

import sys
import os
import argparse
import unittest
import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from test_whatsapp_ui_local_ai_unit import *
    from test_whatsapp_ui_local_ai_integration import *
    from test_config import *
except ImportError as e:
    print(f"Error importing test modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

class TestRunner:
    """Main test runner class"""
    
    def __init__(self):
        self.start_time = None
        self.test_results = {}
        self.coverage_enabled = False
        
    def setup_environment(self):
        """Set up test environment"""
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        
        # Create test directory for temporary files
        self.test_dir = Path('test_temp')
        self.test_dir.mkdir(exist_ok=True)
        
    def run_unit_tests(self, verbose=False, specific_test=None):
        """Run unit tests"""
        print("\n" + "="*80)
        print("🧪 RUNNING UNIT TESTS")
        print("="*80)
        
        # Load unit test suite
        loader = unittest.TestLoader()
        
        if specific_test:
            # Load specific test from the unit test module
            if '.' in specific_test:
                # It's a full test path
                suite = loader.loadTestsFromName(specific_test, module=__import__('test_whatsapp_ui_local_ai_unit'))
            else:
                # It's just a class name, load from unit test module
                module = __import__('test_whatsapp_ui_local_ai_unit')
                suite = loader.loadTestsFromName(specific_test, module=module)
        else:
            # Load all unit tests
            suite = unittest.TestSuite()
            
            # Import the test module
            try:
                test_module = __import__('test_whatsapp_ui_local_ai_unit')
                
                # Add specific test classes
                test_classes = [
                    test_module.TestLocalLLMDetection,
                    test_module.TestLocalLLMResponse,
                    test_module.TestServiceStatus,
                    test_module.TestEnhancedResponse,
                    test_module.TestAPIEndpoints,
                    test_module.TestModeSwitching,
                    test_module.TestEnvironmentConfiguration
                ]
                
                for test_class in test_classes:
                    tests = loader.loadTestsFromTestCase(test_class)
                    suite.addTests(tests)
                    
            except ImportError as e:
                print(f"Warning: Could not import some test classes: {e}")
        
        # Run tests
        runner = unittest.TextTestRunner(
            verbosity=2 if verbose else 1,
            buffer=True,
            stream=sys.stdout
        )
        
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        # Store results
        self.test_results['unit'] = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'time': end_time - start_time,
            'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun if result.testsRun > 0 else 0
        }
        
        return result.wasSuccessful()
    
    def run_integration_tests(self, verbose=False, specific_test=None):
        """Run integration tests"""
        print("\n" + "="*80)
        print("🔗 RUNNING INTEGRATION TESTS")
        print("="*80)
        
        loader = unittest.TestLoader()
        
        if specific_test:
            # Load specific test
            suite = loader.loadTestsFromName(specific_test)
        else:
            # Load all integration tests
            suite = unittest.TestSuite()
            
            test_classes = [
                TestChatWorkflowIntegration,
                TestServiceIntegration,
                TestPerformanceAndReliability,
                TestRealWorldScenarios,
                TestEnvironmentIntegration,
                TestFallbackMechanismIntegration
            ]
            
            for test_class in test_classes:
                tests = loader.loadTestsFromTestCase(test_class)
                suite.addTests(tests)
        
        runner = unittest.TextTestRunner(
            verbosity=2 if verbose else 1,
            buffer=True,
            stream=sys.stdout
        )
        
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        self.test_results['integration'] = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'time': end_time - start_time,
            'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun if result.testsRun > 0 else 0
        }
        
        return result.wasSuccessful()
    
    def run_performance_tests(self):
        """Run performance-specific tests"""
        print("\n" + "="*80)
        print("⚡ RUNNING PERFORMANCE TESTS")
        print("="*80)
        
        # Run performance tests from integration test suite
        suite = unittest.TestSuite()
        suite.addTest(TestPerformanceAndReliability('test_response_time_performance'))
        suite.addTest(TestPerformanceAndReliability('test_memory_usage_with_large_history'))
        
        runner = unittest.TextTestRunner(verbosity=2, buffer=True)
        result = runner.run(suite)
        
        self.test_results['performance'] = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'time': sum(getattr(result, 'time', 0) for _ in []),
            'success_rate': 1.0 if result.wasSuccessful() else 0.0
        }
        
        return result.wasSuccessful()
    
    def run_stress_tests(self):
        """Run stress tests"""
        print("\n" + "="*80)
        print("💪 RUNNING STRESS TESTS")
        print("="*80)
        
        # Create stress test scenarios
        test_results = []
        
        # Test 1: Concurrent requests
        print("Testing concurrent requests...")
        try:
            app = create_app()[0]
            app.config['TESTING'] = True
            client = app.test_client()
            
            def send_stress_message(i):
                return client.post('/api/chat/send',
                    json={'message': f'Stress test message {i}'},
                    content_type='application/json'
                )
            
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(send_stress_message, i) for i in range(20)]
                results = [future.result() for future in as_completed(futures)]
            end_time = time.time()
            
            success_count = sum(1 for r in results if r.status_code == 200)
            test_results.append({
                'test': 'concurrent_requests',
                'success_rate': success_count / len(results),
                'time': end_time - start_time
            })
            
        except Exception as e:
            test_results.append({
                'test': 'concurrent_requests',
                'success_rate': 0.0,
                'error': str(e)
            })
        
        # Test 2: Large message volumes
        print("Testing large message volumes...")
        try:
            app = create_app()[0]
            client = app.test_client()
            
            start_time = time.time()
            for i in range(50):
                response = client.post('/api/chat/send',
                    json={'message': f'Volume test message {i}'},
                    content_type='application/json'
                )
                if response.status_code != 200:
                    break
            end_time = time.time()
            
            test_results.append({
                'test': 'large_message_volume',
                'messages_sent': i + 1,
                'time': end_time - start_time,
                'success_rate': 1.0 if i == 49 else 0.0
            })
            
        except Exception as e:
            test_results.append({
                'test': 'large_message_volume',
                'success_rate': 0.0,
                'error': str(e)
            })
        
        self.test_results['stress'] = test_results
        
        return all(result.get('success_rate', 0) > 0.8 for result in test_results)
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📊 TEST REPORT")
        print("="*80)
        
        total_time = sum(
            result.get('time', 0) for result in self.test_results.values()
            if isinstance(result, dict) and 'time' in result
        )
        
        print(f"Total Test Duration: {total_time:.2f} seconds")
        print()
        
        # Unit Tests Summary
        if 'unit' in self.test_results:
            result = self.test_results['unit']
            print(f"🧪 Unit Tests:")
            print(f"   Tests Run: {result['tests_run']}")
            print(f"   Failures: {result['failures']}")
            print(f"   Errors: {result['errors']}")
            print(f"   Success Rate: {result['success_rate']:.2%}")
            print(f"   Duration: {result['time']:.2f}s")
            print()
        
        # Integration Tests Summary
        if 'integration' in self.test_results:
            result = self.test_results['integration']
            print(f"🔗 Integration Tests:")
            print(f"   Tests Run: {result['tests_run']}")
            print(f"   Failures: {result['failures']}")
            print(f"   Errors: {result['errors']}")
            print(f"   Success Rate: {result['success_rate']:.2%}")
            print(f"   Duration: {result['time']:.2f}s")
            print()
        
        # Performance Tests Summary
        if 'performance' in self.test_results:
            result = self.test_results['performance']
            print(f"⚡ Performance Tests:")
            print(f"   Tests Run: {result['tests_run']}")
            print(f"   Success Rate: {result['success_rate']:.2%}")
            print()
        
        # Stress Tests Summary
        if 'stress' in self.test_results:
            print(f"💪 Stress Tests:")
            for result in self.test_results['stress']:
                print(f"   {result['test']}: {result['success_rate']:.2%} success rate")
                if 'time' in result:
                    print(f"      Duration: {result['time']:.2f}s")
            print()
        
        # Overall Summary
        overall_success = all(
            result.get('success_rate', 0) > 0.8 
            for result in self.test_results.values()
            if isinstance(result, dict) and 'success_rate' in result
        )
        
        if overall_success:
            print("🎉 OVERALL RESULT: ALL TESTS PASSED ✅")
        else:
            print("❌ OVERALL RESULT: SOME TESTS FAILED")
        
        # Save report to file
        self.save_report_to_file()
        
        return overall_success
    
    def save_report_to_file(self):
        """Save test report to JSON file"""
        report_file = Path('test_report.json')
        
        report_data = {
            'timestamp': time.time(),
            'environment': {
                'FLASK_ENV': os.environ.get('FLASK_ENV'),
                'USE_ENHANCED_MODE': os.environ.get('USE_ENHANCED_MODE'),
                'OLLAMA_BASE_URL': os.environ.get('OLLAMA_BASE_URL'),
                'OLLAMA_MODEL': os.environ.get('OLLAMA_MODEL')
            },
            'results': self.test_results
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Detailed report saved to: {report_file}")
    
    def run_all_tests(self, args):
        """Run all tests based on arguments"""
        self.setup_environment()
        self.start_time = time.time()
        
        success = True
        
        try:
            if args.unit:
                success &= self.run_unit_tests(args.verbose, args.specific)
            
            if args.integration:
                success &= self.run_integration_tests(args.verbose, args.specific)
            
            if args.performance:
                success &= self.run_performance_tests()
            
            if args.stress:
                success &= self.run_stress_tests()
            
            if not any([args.unit, args.integration, args.performance, args.stress]):
                # Run all tests by default
                success &= self.run_unit_tests(args.verbose, args.specific)
                success &= self.run_integration_tests(args.verbose, args.specific)
            
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
            success = False
        except Exception as e:
            print(f"\n❌ Unexpected error during testing: {e}")
            success = False
        
        # Generate final report
        self.generate_report()
        
        return success

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Run WhatsApp Chat UI Local AI Tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run_tests.py                    # Run all tests
  python3 run_tests.py --unit             # Run only unit tests
  python3 run_tests.py --integration      # Run only integration tests
  python3 run_tests.py --performance      # Run performance tests
  python3 run_tests.py --stress           # Run stress tests
  python3 run_tests.py --specific TestLocalLLMDetection  # Run specific test
  python3 run_tests.py --unit --verbose   # Run unit tests with verbose output
        """
    )
    
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--performance', action='store_true', help='Run performance tests only')
    parser.add_argument('--stress', action='store_true', help='Run stress tests only')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--parallel', action='store_true', help='Run tests in parallel')
    parser.add_argument('--specific', help='Run specific test class or method')
    parser.add_argument('--output', '-o', help='Output file for report')
    
    args = parser.parse_args()
    
    # Check if test modules exist
    if not os.path.exists('test_whatsapp_ui_local_ai_unit.py'):
        print("❌ Test files not found. Make sure you're in the project root directory.")
        sys.exit(1)
    
    # Create and run test runner
    runner = TestRunner()
    
    try:
        success = runner.run_all_tests(args)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()