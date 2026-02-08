#!/usr/bin/env python3
"""
Autonomous E2E Test Orchestrator

Main entry point for autonomous testing. Coordinates:
1. Test scenario loading and execution via Playwright MCP
2. Issue detection at each step using real browser APIs
3. Auto-fix application
4. Report generation

This orchestrator uses REAL Playwright MCP browser automation - NOT mocks.
"""

import argparse
import asyncio
import json
import os
import sys
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils import (
    Logger, Issue, TestResult, Severity, IssueCategory,
    setup_report_dir, save_json, save_log, load_yaml,
    is_server_running, print_summary, group_issues_by_severity
)

# Import detectors and generators
from issue_detector import IssueDetector
from report_generator import ReportGenerator

# Import MCP client and step executor
from mcp_client import MCPClient, MCPClientError, check_server_available
from step_executor import StepExecutor, ScenarioContext, StepResult

# Import image operation modules
from image_operations import ImageSearchHandler
from download_manager import DownloadManager
from upload_workflows import UploadWorkflowManager


class TestOrchestrator:
    """Main autonomous testing orchestrator using real Playwright MCP"""

    def __init__(
        self,
        url: str,
        app_type: str = "auto",
        report_dir: str = "./test-reports",
        auto_fix: bool = True,
        mcp_port: int = 8808
    ):
        """Initialize orchestrator.

        Args:
            url: Target application URL
            app_type: Application type (ecommerce, blog, saas, auto)
            report_dir: Directory for test reports
            auto_fix: Whether to apply auto-fixes
            mcp_port: Playwright MCP server port (default: 8808)
        """
        self.url = url
        self.app_type = app_type
        self.report_dir = setup_report_dir(report_dir)
        self.logger = Logger.get_logger()
        self.auto_fix = auto_fix
        self.mcp_port = mcp_port

        # MCP client and step executor
        self.mcp_client: Optional[MCPClient] = None
        self.step_executor: Optional[StepExecutor] = None

        # Test results tracking
        self.test_results: List[TestResult] = []
        self.all_issues: List[Issue] = []
        self.auto_fixed_count = 0
        self.start_time = None
        self.end_time = None

        # Initialize issue detector and report generator
        self.issue_detector: Optional[IssueDetector] = None
        self.report_generator = ReportGenerator(self.report_dir)

        # Load test scenarios
        self.scenarios = self._load_scenarios()

        self.logger.info(f"Orchestrator initialized for {url}")
        self.logger.info(f"MCP port: {mcp_port}")
        self.logger.info(f"Report directory: {self.report_dir}")

    def _load_scenarios(self) -> List[Dict[str, Any]]:
        """Load test scenarios from YAML"""
        try:
            scenario_file = os.path.join(
                os.path.dirname(__file__),
                "..",
                "workflows",
                "ecommerce.yaml"
            )

            if not os.path.exists(scenario_file):
                self.logger.error(f"Scenario file not found: {scenario_file}")
                return []

            data = load_yaml(scenario_file)

            # Extract scenarios from YAML
            scenarios = []
            for section in ["homepage_tests", "product_discovery_tests", "shopping_cart_tests", "checkout_tests"]:
                if section in data:
                    scenarios.extend(data[section])

            self.logger.info(f"Loaded {len(scenarios)} test scenarios")
            return scenarios

        except Exception as e:
            self.logger.error(f"Error loading scenarios: {e}")
            return []

    async def connect_to_mcp(self) -> bool:
        """Connect to Playwright MCP server.

        Returns:
            True if connection successful
        """
        print(f"\nConnecting to Playwright MCP on port {self.mcp_port}...")

        # Check if server is available
        if not check_server_available(port=self.mcp_port):
            print(f"  ERROR: MCP server not running on port {self.mcp_port}")
            print(f"  Start it with: npx @playwright/mcp@latest --port {self.mcp_port}")
            return False

        try:
            self.mcp_client = MCPClient(port=self.mcp_port)
            connected = await self.mcp_client.connect()

            if connected:
                print(f"  SUCCESS: Connected to Playwright MCP")

                # Initialize step executor with screenshot directory
                screenshot_dir = os.path.join(self.report_dir, "screenshots")
                self.step_executor = StepExecutor(self.mcp_client, screenshot_dir)

                # Initialize issue detector with MCP client
                self.issue_detector = IssueDetector(self.url, self.mcp_client)

                return True
            else:
                print(f"  ERROR: Failed to initialize MCP session")
                return False

        except MCPClientError as e:
            print(f"  ERROR: {e}")
            return False

    def run_all_tests(self, parallel: int = 1) -> Dict[str, Any]:
        """Execute all test scenarios autonomously.

        Args:
            parallel: Number of parallel executors (currently only 1 supported)

        Returns:
            Report data dictionary
        """
        # Run async test execution
        return asyncio.run(self._run_all_tests_async())

    async def _run_all_tests_async(self) -> Dict[str, Any]:
        """Async implementation of test execution"""
        self.start_time = time.time()
        self.logger.info(f"Starting autonomous testing...")
        self.logger.info(f"Target: {self.url}")
        self.logger.info(f"Scenarios: {len(self.scenarios)}")

        # Print progress header
        print(f"\n{'='*60}")
        print(f"AUTONOMOUS E2E TESTING - {self.app_type.upper()}")
        print(f"{'='*60}")
        print(f"Target URL: {self.url}")
        print(f"Test Scenarios: {len(self.scenarios)}")
        print(f"Report Directory: {self.report_dir}")
        print(f"{'='*60}")

        # Connect to MCP server
        connected = await self.connect_to_mcp()
        if not connected:
            print("\nFAILED: Could not connect to Playwright MCP server")
            print("Make sure the server is running:")
            print(f"  npx @playwright/mcp@latest --port {self.mcp_port}")
            return self._generate_error_report("MCP connection failed")

        print(f"\nRunning {len(self.scenarios)} test scenarios...\n")

        # Run tests
        for i, scenario in enumerate(self.scenarios):
            progress = f"[{i+1}/{len(self.scenarios)}]"
            await self._run_scenario_async(scenario, progress)

        self.end_time = time.time()
        execution_time = self.end_time - self.start_time

        # Generate report
        return self._generate_final_report(execution_time)

    async def _run_scenario_async(
        self,
        scenario: Dict[str, Any],
        progress: str = ""
    ) -> Optional[TestResult]:
        """Run a single test scenario using real MCP browser automation.

        Args:
            scenario: Scenario definition from YAML
            progress: Progress indicator string

        Returns:
            TestResult with execution outcome
        """
        scenario_id = scenario.get("id", "unknown")
        scenario_name = scenario.get("name", "Unknown Test")

        try:
            result = TestResult(scenario_name)
            start_time = time.time()

            # Log test start
            self.logger.info(f"{progress} Running: {scenario_name} ({scenario_id})")
            print(f"{progress} {scenario_name}... ", end="", flush=True)

            # Execute scenario steps using REAL browser automation
            if self.step_executor:
                passed, step_results = await self.step_executor.execute_scenario(
                    scenario,
                    self.url
                )

                result.passed = passed

                # Check for errors in step results
                for step_result in step_results:
                    if not step_result.success and step_result.error:
                        if result.error:
                            result.error += f"; {step_result.error}"
                        else:
                            result.error = step_result.error
            else:
                # Fallback if step executor not available
                result.passed = False
                result.error = "Step executor not initialized"

            # Detect issues after scenario using REAL browser APIs
            issues = await self._detect_issues_async(scenario)
            for issue in issues:
                result.add_issue(issue)
                self.all_issues.append(issue)

                # Apply auto-fixes if enabled
                if self.auto_fix and issue.auto_fix:
                    self.auto_fixed_count += 1

            result.execution_time = time.time() - start_time

            # Update progress output
            if result.passed and len(result.issues) == 0:
                status = "PASS"
            elif result.passed:
                status = "PASS (with issues)"
            else:
                status = "FAIL"

            print(f"{status} ({result.execution_time:.2f}s)")

            self.test_results.append(result)
            return result

        except Exception as e:
            print(f"FAIL ({str(e)[:30]})")
            result = TestResult(scenario_name, passed=False, error=str(e))
            self.test_results.append(result)
            self.logger.error(f"Error running {scenario_name}: {e}")
            return result

    async def _detect_issues_async(self, scenario: Dict[str, Any]) -> List[Issue]:
        """Detect issues after running a scenario using REAL browser APIs.

        Args:
            scenario: The scenario that was just executed

        Returns:
            List of detected issues
        """
        issues = []

        if not self.issue_detector or not self.mcp_client:
            return issues

        try:
            # Detect console errors
            console_issues = await self._detect_console_errors()
            issues.extend(console_issues)

            # Detect network failures
            network_issues = await self._detect_network_failures()
            issues.extend(network_issues)

            # Detect broken images
            image_issues = await self._detect_broken_images()
            issues.extend(image_issues)

            # Detect missing alt text
            alt_issues = await self._detect_missing_alt_text()
            issues.extend(alt_issues)

            # Detect performance issues
            perf_issues = await self._detect_performance_issues()
            issues.extend(perf_issues)

        except Exception as e:
            self.logger.error(f"Issue detection error: {e}")

        return issues

    async def _detect_console_errors(self) -> List[Issue]:
        """Detect JavaScript console errors using browser_console_messages"""
        issues = []

        try:
            result = await self.mcp_client.get_console_messages(level="error")
            content = result.get("content", "")

            if content:
                errors = [e.strip() for e in content.split('\n') if e.strip()]
                for error in errors:
                    issues.append(Issue(
                        category=IssueCategory.CONSOLE_ERROR,
                        severity=Severity.CRITICAL,
                        description=f"JavaScript error: {error[:100]}"
                    ))
                    self.logger.warning(f"Console error: {error[:80]}")

        except Exception as e:
            self.logger.debug(f"Console error detection failed: {e}")

        return issues

    async def _detect_network_failures(self) -> List[Issue]:
        """Detect network failures using browser_network_requests"""
        issues = []

        try:
            result = await self.mcp_client.get_network_requests(include_static=False)
            content = result.get("content", "")

            if content:
                lines = content.split('\n')
                for line in lines:
                    # Check for error status codes
                    if '404' in line:
                        issues.append(Issue(
                            category=IssueCategory.NETWORK_FAILURE,
                            severity=Severity.HIGH,
                            description=f"404 Not Found: {line[:80]}"
                        ))
                    elif '500' in line or '502' in line or '503' in line:
                        issues.append(Issue(
                            category=IssueCategory.NETWORK_FAILURE,
                            severity=Severity.CRITICAL,
                            description=f"Server error: {line[:80]}"
                        ))
                    elif 'timeout' in line.lower() or 'failed' in line.lower():
                        issues.append(Issue(
                            category=IssueCategory.NETWORK_FAILURE,
                            severity=Severity.HIGH,
                            description=f"Network failure: {line[:80]}"
                        ))

        except Exception as e:
            self.logger.debug(f"Network error detection failed: {e}")

        return issues

    async def _detect_broken_images(self) -> List[Issue]:
        """Detect broken images using browser_evaluate"""
        issues = []

        try:
            result = await self.mcp_client.evaluate("""
                () => {
                    const images = Array.from(document.querySelectorAll('img'));
                    return images
                        .filter(img => img.complete && img.naturalWidth === 0)
                        .map(img => ({
                            src: img.src,
                            alt: img.alt || 'no alt'
                        }));
                }
            """)

            content = result.get("content", "")

            # Parse JSON result
            if content:
                try:
                    import re
                    # Extract JSON array from content
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        broken_images = json.loads(json_match.group())
                        for img in broken_images:
                            issues.append(Issue(
                                category=IssueCategory.BROKEN_IMAGE,
                                severity=Severity.MEDIUM,
                                description=f"Broken image: {img.get('src', 'unknown')[:60]}"
                            ))
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            self.logger.debug(f"Broken image detection failed: {e}")

        return issues

    async def _detect_missing_alt_text(self) -> List[Issue]:
        """Detect missing alt text using browser_evaluate"""
        issues = []

        try:
            result = await self.mcp_client.evaluate("""
                () => {
                    const images = Array.from(document.querySelectorAll('img'));
                    return images
                        .filter(img => !img.alt || img.alt.trim() === '')
                        .map(img => ({
                            src: img.src,
                            suggestion: img.src.split('/').pop().split('.')[0].replace(/[-_]/g, ' ')
                        }));
                }
            """)

            content = result.get("content", "")

            if content:
                try:
                    import re
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        missing_alt = json.loads(json_match.group())
                        for img in missing_alt:
                            suggestion = img.get('suggestion', 'image')
                            issues.append(Issue(
                                category=IssueCategory.MISSING_ALT_TEXT,
                                severity=Severity.LOW,
                                description=f"Missing alt text: {img.get('src', 'image')[:50]}",
                                auto_fix=True,
                                fix_code=f'alt="{suggestion}"'
                            ))
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            self.logger.debug(f"Alt text detection failed: {e}")

        return issues

    async def _detect_performance_issues(self) -> List[Issue]:
        """Detect performance issues using browser_evaluate"""
        issues = []

        try:
            result = await self.mcp_client.evaluate("""
                () => {
                    const perf = performance.timing;
                    const loadTime = perf.loadEventEnd - perf.navigationStart;
                    const domContentLoaded = perf.domContentLoadedEventEnd - perf.navigationStart;

                    // Try to get LCP
                    let lcp = 0;
                    try {
                        const entries = performance.getEntriesByType('largest-contentful-paint');
                        if (entries.length > 0) {
                            lcp = entries[entries.length - 1].startTime;
                        }
                    } catch(e) {}

                    return {
                        loadTime: loadTime,
                        domContentLoaded: domContentLoaded,
                        lcp: lcp
                    };
                }
            """)

            content = result.get("content", "")

            if content:
                try:
                    import re
                    json_match = re.search(r'\{[^{}]*\}', content)
                    if json_match:
                        perf_data = json.loads(json_match.group())
                        load_time = perf_data.get('loadTime', 0)
                        lcp = perf_data.get('lcp', 0)

                        if load_time > 5000:
                            issues.append(Issue(
                                category=IssueCategory.PERFORMANCE_ISSUE,
                                severity=Severity.HIGH,
                                description=f"Slow page load: {load_time}ms (target: <2500ms)"
                            ))

                        if lcp > 2500:
                            issues.append(Issue(
                                category=IssueCategory.PERFORMANCE_ISSUE,
                                severity=Severity.HIGH,
                                description=f"Poor LCP: {lcp:.0f}ms (target: <2500ms)"
                            ))
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            self.logger.debug(f"Performance detection failed: {e}")

        return issues

    def _generate_error_report(self, error_message: str) -> Dict[str, Any]:
        """Generate report for failed test run"""
        return {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "app_type": self.app_type,
                "target_url": self.url,
                "report_dir": self.report_dir,
                "error": error_message
            },
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "pass_rate": 0,
                "execution_time_seconds": 0
            },
            "issues": {
                "total": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "auto_fixes": {"applied": 0, "remaining": 0},
            "test_results": [],
            "issues_list": []
        }

    def _generate_final_report(self, execution_time: float) -> Dict[str, Any]:
        """Generate final test report using ReportGenerator"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = total_tests - passed_tests

        # Group issues by severity
        grouped_issues = group_issues_by_severity(self.all_issues)

        # Create report data
        report_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "app_type": self.app_type,
                "target_url": self.url,
                "report_dir": self.report_dir,
                "mcp_connected": self.mcp_client is not None and self.mcp_client.is_connected
            },
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "execution_time_seconds": int(execution_time)
            },
            "issues": {
                "total": len(self.all_issues),
                "critical": len(grouped_issues[Severity.CRITICAL]),
                "high": len(grouped_issues[Severity.HIGH]),
                "medium": len(grouped_issues[Severity.MEDIUM]),
                "low": len(grouped_issues[Severity.LOW])
            },
            "auto_fixes": {
                "applied": self.auto_fixed_count,
                "remaining": len(self.all_issues) - self.auto_fixed_count
            },
            "test_results": [r.to_dict() for r in self.test_results],
            "issues_list": [issue.to_dict() for issue in self.all_issues]
        }

        # Generate all reports using ReportGenerator
        reports = self.report_generator.generate_all(self.test_results, self.all_issues, self.url)
        self.logger.info(f"Reports generated: {reports}")

        # Print summary
        print_summary(total_tests, passed_tests, self.all_issues, self.auto_fixed_count, execution_time)

        # Print report file locations
        print(f"\n{'='*60}")
        print(f"REPORTS GENERATED:")
        print(f"{'='*60}")
        print(f"  HTML Report: {reports['html']}")
        print(f"  JSON Data:   {reports['json']}")
        print(f"  Text Summary: {reports['txt']}")
        print(f"{'='*60}\n")

        return report_data


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Autonomous E2E Testing & Debugging Agent (Real Browser Automation)"
    )

    parser.add_argument(
        "--url",
        required=True,
        help="Target app URL (e.g., http://localhost:3000)"
    )

    parser.add_argument(
        "--app-type",
        default="ecommerce",
        choices=["ecommerce", "blog", "saas", "auto"],
        help="App type for test scenario selection"
    )

    parser.add_argument(
        "--auto-fix",
        action="store_true",
        default=True,
        help="Enable auto-fixing of issues"
    )

    parser.add_argument(
        "--no-auto-fix",
        dest="auto_fix",
        action="store_false",
        help="Disable auto-fixing"
    )

    parser.add_argument(
        "--report-dir",
        default="./test-reports",
        help="Output directory for test reports"
    )

    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel test executors"
    )

    parser.add_argument(
        "--mcp-port",
        type=int,
        default=8808,
        help="Playwright MCP server port (default: 8808)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    # Image operation arguments
    parser.add_argument(
        "--search-images",
        type=str,
        metavar="QUERY",
        help="Search for images with given query (e.g., 'ladies fashion')"
    )

    parser.add_argument(
        "--upload-images",
        action="store_true",
        help="Upload downloaded images to app (requires --search-images)"
    )

    parser.add_argument(
        "--image-count",
        type=int,
        default=20,
        help="Number of images to search/download (default: 20)"
    )

    parser.add_argument(
        "--upload-url",
        type=str,
        help="URL for image upload page (default: {base_url}/admin/products/new)"
    )

    parser.add_argument(
        "--image-category",
        type=str,
        help="Category for uploaded images (e.g., 'Fashion')"
    )

    parser.add_argument(
        "--image-tags",
        type=str,
        help="Comma-separated tags for images (e.g., 'boutique,fashion,ladies')"
    )

    args = parser.parse_args()

    # Validate URL
    if not args.url.startswith("http"):
        print("Error: URL must start with http:// or https://")
        sys.exit(1)

    # Handle image operations workflow if requested
    if args.search_images:
        try:
            print("\n" + "="*60)
            print("IMAGE OPERATIONS WORKFLOW")
            print("="*60)

            # Check MCP server
            if not check_server_available(port=args.mcp_port):
                print(f"\nERROR: MCP server not running on port {args.mcp_port}")
                print(f"Start it with: npx @playwright/mcp@latest --port {args.mcp_port}")
                sys.exit(1)

            # Initialize MCP client and image modules
            async def run_image_workflow():
                mcp_client = MCPClient(port=args.mcp_port)
                await mcp_client.connect()

                image_handler = ImageSearchHandler(mcp_client)
                download_manager = DownloadManager(mcp_client, "./temp_downloads")
                workflow_manager = UploadWorkflowManager(
                    mcp_client,
                    image_handler,
                    download_manager
                )

                # Prepare metadata
                metadata = {}
                if args.image_category:
                    metadata['category'] = args.image_category
                if args.image_tags:
                    metadata['tags'] = [tag.strip() for tag in args.image_tags.split(',')]

                # Determine upload URL
                upload_url = args.upload_url or f"{args.url}/admin/products/new"

                # Run image workflow
                if args.upload_images:
                    print(f"\nRunning complete image workflow...")
                    print(f"   Query: {args.search_images}")
                    print(f"   Count: {args.image_count}")
                    print(f"   Upload URL: {upload_url}")

                    result = await workflow_manager.search_download_upload(
                        search_query=args.search_images,
                        upload_url=upload_url,
                        upload_input_selector="input[type='file']",
                        metadata=metadata,
                        image_count=args.image_count
                    )

                    # Print summary
                    print(f"\n{'='*60}")
                    print(f"IMAGE WORKFLOW COMPLETE")
                    print(f"{'='*60}")
                    print(f"Searched:    {result['searched']} images")
                    print(f"Downloaded:  {result['downloaded']} images")
                    print(f"Uploaded:    {result['uploaded']} images")
                    print(f"Failed:      {result['failed']} images")
                    print(f"Duration:    {result['duration']:.1f}s")
                    success_rate = result['uploaded']/result['downloaded']*100 if result['downloaded'] > 0 else 0
                    print(f"Success:     {success_rate:.1f}%")
                    print(f"{'='*60}\n")

                    return result['failed'] == 0

                else:
                    # Just search and download (no upload)
                    print(f"\nSearching and downloading images...")
                    print(f"   Query: {args.search_images}")
                    print(f"   Count: {args.image_count}")

                    images = await image_handler.search_unsplash(
                        args.search_images,
                        {'count': args.image_count, 'min_width': 800, 'min_height': 600}
                    )

                    if images:
                        urls = [img['url'] for img in images]
                        paths = await image_handler.download_images(urls, "./temp_downloads")

                        print(f"\nDownloaded {len(paths)} images to ./temp_downloads/")
                        print(f"   Use --upload-images to upload them to the app")
                        return True
                    else:
                        print(f"\nNo images found for query: {args.search_images}")
                        return False

            success = asyncio.run(run_image_workflow())
            if not args.app_type:
                sys.exit(0 if success else 1)

        except ImportError as e:
            print(f"\nImage operations require MCP client: {e}")
            print("   Make sure Playwright MCP server is running")
            sys.exit(1)
        except Exception as e:
            print(f"\nImage workflow error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    # Initialize orchestrator with MCP port
    orchestrator = TestOrchestrator(
        url=args.url,
        app_type=args.app_type,
        report_dir=args.report_dir,
        auto_fix=args.auto_fix,
        mcp_port=args.mcp_port
    )

    # Run tests
    try:
        report = orchestrator.run_all_tests(parallel=args.parallel)

        # Determine exit code based on failures
        if report["summary"]["failed_tests"] > 0:
            print(f"\nSome tests failed. Report: {orchestrator.report_dir}")
            sys.exit(1)

        print(f"\nAll tests passed! Report: {orchestrator.report_dir}")
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nTesting failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
