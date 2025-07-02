#!/usr/bin/env python3
"""
Comprehensive Test Runner for YouTube Automation Platform
Executes all test suites with detailed reporting and performance monitoring
"""

import os
import sys
import time
import json
import subprocess
import argparse
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import tempfile
import shutil


class TestRunner:
    """Advanced test runner with parallel execution and detailed reporting"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.test_results = []
        self.start_time = None
        self.end_time = None
        self.temp_dir = None
        
    def setup_test_environment(self):
        """Setup isolated test environment"""
        print("🔧 Setting up test environment...")
        
        # Create temporary directory for test artifacts
        self.temp_dir = tempfile.mkdtemp(prefix="youtube_automation_tests_")
        print(f"   Test artifacts directory: {self.temp_dir}")
        
        # Set environment variables for testing
        os.environ.update({
            "PYTHONPATH": str(self.project_root),
            "TEST_MODE": "true",
            "GPU_AVAILABLE": "false",  # Default to CPU-only for CI/CD
            "DATABASE_URL": "sqlite:///test_youtube_automation.db",
            "REDIS_URL": "redis://localhost:6379/15",  # Use test database
        })
        
        # Install test dependencies
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "-r", str(self.project_root / "tests" / "requirements.txt")
            ], check=True, capture_output=True)
            print("   ✓ Test dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠ Warning: Could not install test dependencies: {e}")
        
    def cleanup_test_environment(self):
        """Clean up test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            
        # Clean up test database files
        for db_file in self.project_root.glob("test_*.db"):
            try:
                db_file.unlink()
            except:
                pass
    
    def run_test_suite(self, suite_name: str, test_path: str, markers: List[str] = None, 
                      timeout: int = 3600, parallel: bool = True) -> Dict[str, Any]:
        """Run a specific test suite with configuration options"""
        
        print(f"\n🧪 Running {suite_name}...")
        start_time = time.time()
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            "--strict-markers",
            f"--maxfail=10",
            f"--timeout={timeout}",
            "--disable-warnings",
            f"--junitxml={self.temp_dir}/{suite_name}_results.xml",
            f"--html={self.temp_dir}/{suite_name}_report.html",
            "--self-contained-html"
        ]
        
        # Add markers if specified
        if markers:
            cmd.extend(["-m", " and ".join(markers)])
            
        # Add parallel execution for integration/e2e tests
        if parallel and suite_name in ["integration", "e2e", "performance"]:
            try:
                import pytest_xdist
                cmd.extend(["-n", "auto"])
            except ImportError:
                print("   ⚠ pytest-xdist not available, running sequentially")
        
        # Add coverage reporting
        if suite_name == "unit":
            cmd.extend([
                "--cov=backend",
                "--cov-report=html:" + str(Path(self.temp_dir) / "coverage_html"),
                "--cov-report=json:" + str(Path(self.temp_dir) / "coverage.json"),
                "--cov-fail-under=80"
            ])
        
        try:
            # Run tests with timeout
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            duration = time.time() - start_time
            
            # Parse test results
            success = result.returncode == 0
            output_lines = result.stdout.split('\n')
            
            # Extract test statistics
            stats = self._parse_pytest_output(output_lines)
            
            test_result = {
                "suite": suite_name,
                "success": success,
                "duration": duration,
                "return_code": result.returncode,
                "stats": stats,
                "output": result.stdout,
                "errors": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add coverage info for unit tests
            if suite_name == "unit":
                coverage_file = Path(self.temp_dir) / "coverage.json"
                if coverage_file.exists():
                    try:
                        with open(coverage_file) as f:
                            coverage_data = json.load(f)
                            test_result["coverage"] = {
                                "total_coverage": coverage_data["totals"]["percent_covered"],
                                "lines_covered": coverage_data["totals"]["covered_lines"],
                                "lines_total": coverage_data["totals"]["num_statements"]
                            }
                    except:
                        pass
            
            # Status reporting
            status_icon = "✅" if success else "❌"
            print(f"   {status_icon} {suite_name} completed in {duration:.1f}s")
            
            if stats:
                passed = stats.get("passed", 0)
                failed = stats.get("failed", 0)
                skipped = stats.get("skipped", 0)
                print(f"      📊 {passed} passed, {failed} failed, {skipped} skipped")
            
            if not success:
                print(f"      ⚠ Exit code: {result.returncode}")
                if result.stderr:
                    print(f"      💬 Errors: {result.stderr[:200]}...")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"   ⏱ {suite_name} timed out after {timeout}s")
            
            return {
                "suite": suite_name,
                "success": False,
                "duration": duration,
                "return_code": -1,
                "stats": {},
                "output": "Test timed out",
                "errors": f"Test suite exceeded {timeout}s timeout",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"   💥 {suite_name} failed with exception: {e}")
            
            return {
                "suite": suite_name,
                "success": False,
                "duration": duration,
                "return_code": -1,
                "stats": {},
                "output": "",
                "errors": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_pytest_output(self, output_lines: List[str]) -> Dict[str, int]:
        """Parse pytest output to extract test statistics"""
        stats = {}
        
        for line in output_lines:
            line = line.strip()
            if "failed" in line and "passed" in line:
                # Parse line like "5 failed, 10 passed, 2 skipped in 30.2s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part in ["failed", "passed", "skipped", "errors"]:
                        try:
                            stats[part] = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
                break
        
        return stats
    
    def run_all_tests(self, test_types: List[str] = None, parallel_suites: bool = True,
                     gpu_tests: bool = False, fast_mode: bool = False) -> Dict[str, Any]:
        """Run all test suites with specified configuration"""
        
        self.start_time = time.time()
        print(f"🚀 Starting comprehensive test run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Configure test suites
        test_suites = {
            "unit": {
                "path": "tests/unit_tests",
                "markers": ["unit"],
                "timeout": 600,  # 10 minutes
                "parallel": True
            },
            "integration": {
                "path": "tests/integration_tests", 
                "markers": ["integration"],
                "timeout": 1800,  # 30 minutes
                "parallel": True
            },
            "e2e": {
                "path": "tests/e2e_tests",
                "markers": ["e2e"],
                "timeout": 2400,  # 40 minutes
                "parallel": False  # E2E tests may conflict
            },
            "performance": {
                "path": "tests/performance_tests",
                "markers": ["performance"],
                "timeout": 3600,  # 60 minutes
                "parallel": True
            },
            "plugin": {
                "path": "tests/plugin_tests",
                "markers": ["plugin"],
                "timeout": 900,   # 15 minutes
                "parallel": True
            }
        }
        
        # Filter test types if specified
        if test_types:
            test_suites = {k: v for k, v in test_suites.items() if k in test_types}
        
        # Adjust for fast mode
        if fast_mode:
            for suite in test_suites.values():
                suite["timeout"] = min(suite["timeout"], 300)  # Max 5 minutes in fast mode
                if "markers" not in suite:
                    suite["markers"] = []
                suite["markers"].append("not slow")
        
        # Add GPU marker if GPU tests enabled
        if gpu_tests:
            os.environ["GPU_AVAILABLE"] = "true"
        else:
            for suite in test_suites.values():
                if "markers" not in suite:
                    suite["markers"] = []
                suite["markers"].append("not gpu_required")
        
        print(f"📋 Test suites to run: {', '.join(test_suites.keys())}")
        print(f"⚙️  Configuration: GPU={gpu_tests}, Fast={fast_mode}, Parallel={parallel_suites}")
        
        # Run test suites
        if parallel_suites and len(test_suites) > 1:
            # Run suites in parallel
            print("\n🔄 Running test suites in parallel...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_to_suite = {
                    executor.submit(
                        self.run_test_suite,
                        suite_name,
                        suite_config["path"],
                        suite_config.get("markers"),
                        suite_config["timeout"],
                        suite_config.get("parallel", True)
                    ): suite_name
                    for suite_name, suite_config in test_suites.items()
                }
                
                for future in concurrent.futures.as_completed(future_to_suite):
                    result = future.result()
                    self.test_results.append(result)
        else:
            # Run suites sequentially
            print("\n🔄 Running test suites sequentially...")
            
            for suite_name, suite_config in test_suites.items():
                result = self.run_test_suite(
                    suite_name,
                    suite_config["path"],
                    suite_config.get("markers"),
                    suite_config["timeout"],
                    suite_config.get("parallel", True)
                )
                self.test_results.append(result)
        
        self.end_time = time.time()
        
        # Generate comprehensive report
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        total_duration = self.end_time - self.start_time
        successful_suites = [r for r in self.test_results if r["success"]]
        failed_suites = [r for r in self.test_results if not r["success"]]
        
        # Calculate aggregate statistics
        total_tests = sum(
            sum(r["stats"].values()) for r in self.test_results 
            if r["stats"]
        )
        total_passed = sum(
            r["stats"].get("passed", 0) for r in self.test_results
        )
        total_failed = sum(
            r["stats"].get("failed", 0) for r in self.test_results
        )
        total_skipped = sum(
            r["stats"].get("skipped", 0) for r in self.test_results
        )
        
        # Coverage information (from unit tests)
        coverage_info = None
        for result in self.test_results:
            if result["suite"] == "unit" and "coverage" in result:
                coverage_info = result["coverage"]
                break
        
        report = {
            "summary": {
                "total_duration": total_duration,
                "suites_run": len(self.test_results),
                "suites_passed": len(successful_suites),
                "suites_failed": len(failed_suites),
                "total_tests": total_tests,
                "tests_passed": total_passed,
                "tests_failed": total_failed,
                "tests_skipped": total_skipped,
                "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
                "overall_success": len(failed_suites) == 0
            },
            "coverage": coverage_info,
            "suite_results": self.test_results,
            "artifacts_directory": self.temp_dir,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save report to file
        report_file = Path(self.temp_dir) / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        self.print_summary(report)
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print formatted test summary"""
        
        print("\n" + "="*80)
        print("🎯 TEST EXECUTION SUMMARY")
        print("="*80)
        
        summary = report["summary"]
        
        # Overall status
        overall_icon = "✅" if summary["overall_success"] else "❌"
        print(f"\n{overall_icon} Overall Status: {'SUCCESS' if summary['overall_success'] else 'FAILURE'}")
        
        # Statistics
        print(f"\n📊 Test Statistics:")
        print(f"   • Total Duration: {summary['total_duration']:.1f}s")
        print(f"   • Test Suites: {summary['suites_passed']}/{summary['suites_run']} passed")
        print(f"   • Test Cases: {summary['tests_passed']}/{summary['total_tests']} passed")
        print(f"   • Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['tests_skipped'] > 0:
            print(f"   • Skipped: {summary['tests_skipped']} tests")
        
        # Coverage information
        if report["coverage"]:
            cov = report["coverage"]
            print(f"\n📈 Code Coverage:")
            print(f"   • Total Coverage: {cov['total_coverage']:.1f}%")
            print(f"   • Lines Covered: {cov['lines_covered']}/{cov['lines_total']}")
        
        # Suite breakdown
        print(f"\n📋 Suite Breakdown:")
        for result in self.test_results:
            suite_icon = "✅" if result["success"] else "❌"
            stats = result["stats"]
            
            if stats:
                stats_str = f"({stats.get('passed', 0)}P/{stats.get('failed', 0)}F/{stats.get('skipped', 0)}S)"
            else:
                stats_str = "(no stats)"
            
            print(f"   {suite_icon} {result['suite'].ljust(12)} {result['duration']:.1f}s {stats_str}")
        
        # Failed suites details
        failed_suites = [r for r in self.test_results if not r["success"]]
        if failed_suites:
            print(f"\n❌ Failed Suites Details:")
            for result in failed_suites:
                print(f"   • {result['suite']}: {result['errors'][:100]}...")
        
        # Artifacts location
        print(f"\n📁 Test artifacts saved to: {self.temp_dir}")
        print(f"   • Detailed reports: {self.temp_dir}/*_report.html")
        print(f"   • JUnit XML: {self.temp_dir}/*_results.xml")
        if report["coverage"]:
            print(f"   • Coverage report: {self.temp_dir}/coverage_html/index.html")
        
        print("="*80)


def main():
    """Main function with CLI interface"""
    
    parser = argparse.ArgumentParser(
        description="Comprehensive test runner for YouTube Automation Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                     # Run all tests
  python run_tests.py --fast              # Run tests in fast mode (skip slow tests)
  python run_tests.py --types unit        # Run only unit tests
  python run_tests.py --types unit integration  # Run unit and integration tests
  python run_tests.py --gpu               # Include GPU-dependent tests
  python run_tests.py --no-parallel       # Run suites sequentially
        """
    )
    
    parser.add_argument(
        "--types",
        nargs="+",
        choices=["unit", "integration", "e2e", "performance", "plugin"],
        help="Test types to run (default: all)"
    )
    
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Fast mode: skip slow tests and reduce timeouts"
    )
    
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Include GPU-dependent tests (requires GPU)"
    )
    
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Run test suites sequentially instead of parallel"
    )
    
    parser.add_argument(
        "--keep-artifacts",
        action="store_true",
        help="Keep test artifacts after completion"
    )
    
    args = parser.parse_args()
    
    # Determine project root
    project_root = Path(__file__).parent
    
    # Initialize test runner
    runner = TestRunner(str(project_root))
    
    try:
        # Setup test environment
        runner.setup_test_environment()
        
        # Run tests
        report = runner.run_all_tests(
            test_types=args.types,
            parallel_suites=not args.no_parallel,
            gpu_tests=args.gpu,
            fast_mode=args.fast
        )
        
        # Determine exit code
        exit_code = 0 if report["summary"]["overall_success"] else 1
        
        # Keep artifacts if requested
        if args.keep_artifacts:
            print(f"\n📁 Test artifacts preserved at: {runner.temp_dir}")
        else:
            print(f"\n🧹 Cleaning up test artifacts...")
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⏹ Test execution interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        print(f"\n💥 Test execution failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        if not args.keep_artifacts:
            runner.cleanup_test_environment()


if __name__ == "__main__":
    main()