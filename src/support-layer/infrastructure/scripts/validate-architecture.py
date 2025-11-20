"""
Test runner script for the layered architecture validation

This script runs all the architecture validation tests and generates
a comprehensive report.
"""
import sys
import subprocess
from pathlib import Path
import json
import time
from typing import Dict, Any, List

def run_tests(test_patterns: List[str], verbose: bool = True) -> Dict[str, Any]:
    """Run pytest tests and return results"""
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend(["--tb=short", "--json-report", "--json-report-file=test_results.json"])
    cmd.extend(test_patterns)
    
    print(f"Running: {' '.join(cmd)}")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    # Try to load JSON report
    json_report = None
    try:
        with open("test_results.json", "r") as f:
            json_report = json.load(f)
    except FileNotFoundError:
        print("Warning: JSON report not generated")
    
    return {
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "duration": end_time - start_time,
        "json_report": json_report
    }

def print_test_summary(results: Dict[str, Any]):
    """Print a summary of test results"""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if results["json_report"]:
        summary = results["json_report"]["summary"]
        print(f"Total Tests: {summary.get('total', 'Unknown')}")
        print(f"Passed: {summary.get('passed', 0)}")
        print(f"Failed: {summary.get('failed', 0)}")
        print(f"Skipped: {summary.get('skipped', 0)}")
        print(f"Errors: {summary.get('error', 0)}")
        print(f"Duration: {results['duration']:.2f}s")
        
        if summary.get('failed', 0) > 0 or summary.get('error', 0) > 0:
            print("\n❌ Some tests failed!")
            return False
        else:
            print("\n✅ All tests passed!")
            return True
    else:
        if results["return_code"] == 0:
            print("✅ Tests completed successfully")
            return True
        else:
            print("❌ Tests failed")
            print(f"Return code: {results['return_code']}")
            return False

def generate_architecture_report(test_results: Dict[str, Any]):
    """Generate architecture validation report"""
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "architecture_validation": {
            "status": "passed" if test_results["return_code"] == 0 else "failed",
            "duration": test_results["duration"],
            "details": test_results.get("json_report", {})
        },
        "recommendations": []
    }
    
    # Add recommendations based on test results
    if test_results["return_code"] != 0:
        report["recommendations"].extend([
            "Review failed tests and fix architecture violations",
            "Ensure all layer boundaries are properly respected",
            "Verify service structure follows components/shared pattern",
            "Check that dependency injection is properly implemented"
        ])
    else:
        report["recommendations"].extend([
            "Architecture validation passed - consider adding more comprehensive tests",
            "Monitor performance characteristics as the system grows",
            "Keep documentation updated as architecture evolves"
        ])
    
    # Save report
    with open("architecture_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Architecture validation report saved to: architecture_validation_report.json")

def main():
    """Main test runner"""
    print("🏗️  Corvus Corone Architecture Validation")
    print("=========================================")
    
    # Change to project directory
    project_root = Path(__file__).parent.parent
    original_cwd = Path.cwd()
    
    try:
        import os
        os.chdir(project_root)
        
        # Test categories to run
        test_categories = [
            {
                "name": "Architecture Structure Tests",
                "patterns": ["tests/integration/test_layered_architecture.py::TestLayerArchitecture"],
                "description": "Validates that the layered architecture is properly structured"
            },
            {
                "name": "Service Communication Tests", 
                "patterns": ["tests/integration/test_layered_architecture.py::TestServiceCommunication"],
                "description": "Tests inter-service communication patterns"
            },
            {
                "name": "Documentation Compliance Tests",
                "patterns": ["tests/integration/test_layered_architecture.py::TestDocumentationCompliance"],
                "description": "Validates that implementation matches documentation"
            },
            {
                "name": "Performance Tests (Quick)",
                "patterns": ["tests/integration/test_performance.py", "-m", "not slow"],
                "description": "Basic performance validation tests"
            }
        ]
        
        all_passed = True
        all_results = {}
        
        # Run each test category
        for category in test_categories:
            print(f"\n🔍 Running {category['name']}")
            print(f"   {category['description']}")
            print("-" * 60)
            
            results = run_tests(category["patterns"])
            all_results[category["name"]] = results
            
            category_passed = print_test_summary(results)
            all_passed = all_passed and category_passed
            
            if not category_passed:
                print(f"\n⚠️  {category['name']} had failures - check output above")
        
        # Overall summary
        print("\n" + "=" * 60)
        print("OVERALL ARCHITECTURE VALIDATION SUMMARY")
        print("=" * 60)
        
        if all_passed:
            print("🎉 All architecture validation tests passed!")
            print("\nThe layered architecture is properly implemented:")
            print("  ✅ Layer structure follows C4 model")
            print("  ✅ Service boundaries are respected")
            print("  ✅ Components/shared pattern is implemented")
            print("  ✅ Documentation is up to date")
            print("  ✅ Performance characteristics are acceptable")
        else:
            print("⚠️  Some architecture validation tests failed.")
            print("\nRecommended actions:")
            print("  • Review failed tests in detail")
            print("  • Fix layer boundary violations")
            print("  • Ensure proper service structure")
            print("  • Update documentation if needed")
        
        # Generate comprehensive report
        generate_architecture_report({
            "return_code": 0 if all_passed else 1,
            "duration": sum(r["duration"] for r in all_results.values()),
            "categories": all_results
        })
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"❌ Error running architecture validation: {e}")
        return 1
    
    finally:
        # Restore original directory
        os.chdir(original_cwd)

if __name__ == "__main__":
    sys.exit(main())