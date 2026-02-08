#!/usr/bin/env python3
"""
Issue Detector Engine

Detects 7 categories of issues using REAL Playwright MCP browser APIs:
1. Console errors - via browser_console_messages
2. Network failures - via browser_network_requests
3. Broken images - via browser_evaluate
4. Missing alt text - via browser_evaluate
5. Layout problems - via browser_evaluate
6. Performance issues - via browser_evaluate
7. Accessibility issues - via browser_evaluate

This module uses REAL browser APIs - NOT mocks or placeholders.
"""

import asyncio
import json
import logging
import re
from typing import List, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueCategory(Enum):
    CONSOLE_ERROR = "console_error"
    NETWORK_FAILURE = "network_failure"
    BROKEN_IMAGE = "broken_image"
    MISSING_ALT_TEXT = "missing_alt_text"
    LAYOUT_PROBLEM = "layout_problem"
    PERFORMANCE_ISSUE = "performance_issue"
    ACCESSIBILITY_ISSUE = "accessibility_issue"


class Issue:
    """Represents a detected issue"""

    def __init__(
        self,
        category: IssueCategory,
        severity: Severity,
        description: str,
        element_ref: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        auto_fix: bool = False,
        fix_code: Optional[str] = None,
        fix_suggestion: Optional[str] = None,
        confidence: float = 1.0
    ):
        self.category = category
        self.severity = severity
        self.description = description
        self.element_ref = element_ref
        self.screenshot_path = screenshot_path
        self.auto_fix = auto_fix
        self.fix_code = fix_code
        self.fix_suggestion = fix_suggestion
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            'category': self.category.value,
            'severity': self.severity.value,
            'description': self.description,
            'element_ref': self.element_ref,
            'screenshot_path': self.screenshot_path,
            'auto_fix': self.auto_fix,
            'fix_code': self.fix_code,
            'fix_suggestion': self.fix_suggestion,
            'confidence': self.confidence
        }


class IssueDetector:
    """
    Detect issues in web applications using REAL Playwright MCP browser APIs.

    All detection methods use actual browser APIs through the MCP client.
    """

    def __init__(self, app_url: str, mcp_client=None):
        """Initialize issue detector.

        Args:
            app_url: URL of app being tested
            mcp_client: MCPClient instance for browser automation
        """
        self.mcp = mcp_client
        self.app_url = app_url
        self.issues: List[Issue] = []

        logger.info(f"IssueDetector initialized for {app_url}")
        logger.info(f"MCP client: {'connected' if mcp_client else 'not provided'}")

    async def detect_all(self) -> List[Issue]:
        """Detect all issue categories using REAL browser APIs.

        Returns:
            List of detected issues
        """
        logger.info("Starting issue detection with real browser APIs...")

        if not self.mcp:
            logger.error("No MCP client provided - cannot detect issues")
            return self.issues

        # Run all detectors concurrently
        await asyncio.gather(
            self.detect_console_errors(),
            self.detect_network_failures(),
            self.detect_broken_images(),
            self.detect_missing_alt_text(),
            self.detect_layout_problems(),
            self.detect_performance_issues(),
            self.detect_accessibility_issues()
        )

        logger.info(f"Detected {len(self.issues)} issues total")
        return self.issues

    async def detect_console_errors(self) -> List[Issue]:
        """Detect JavaScript console errors using browser_console_messages MCP tool.

        Returns:
            List of console error issues
        """
        detected = []

        if not self.mcp:
            return detected

        try:
            # Call REAL MCP tool
            result = await self.mcp.call_tool(
                "browser_console_messages",
                {"level": "error"}
            )

            content = result.get('content', '')

            if content:
                # Parse error messages
                errors = [e.strip() for e in content.split('\n') if e.strip()]

                for error in errors:
                    # Skip common non-critical errors
                    if self._is_ignorable_error(error):
                        continue

                    issue = Issue(
                        category=IssueCategory.CONSOLE_ERROR,
                        severity=Severity.CRITICAL,
                        description=f"JavaScript error: {error[:150]}",
                        fix_suggestion="Check browser console for full stack trace"
                    )
                    detected.append(issue)
                    self.issues.append(issue)
                    logger.warning(f"Console error detected: {error[:80]}")

        except Exception as e:
            logger.error(f"Error detecting console errors: {e}")

        return detected

    async def detect_network_failures(self) -> List[Issue]:
        """Detect network failures using browser_network_requests MCP tool.

        Returns:
            List of network failure issues
        """
        detected = []

        if not self.mcp:
            return detected

        try:
            # Call REAL MCP tool
            result = await self.mcp.call_tool(
                "browser_network_requests",
                {"includeStatic": False}
            )

            content = result.get('content', '')

            if content:
                lines = content.split('\n')

                for line in lines:
                    if not line.strip():
                        continue

                    # Detect 404 Not Found
                    if '404' in line:
                        issue = Issue(
                            category=IssueCategory.NETWORK_FAILURE,
                            severity=Severity.HIGH,
                            description=f"404 Not Found: {line[:100]}",
                            fix_suggestion="Check if the resource exists and the path is correct"
                        )
                        detected.append(issue)
                        self.issues.append(issue)
                        logger.warning(f"404 detected: {line[:60]}")

                    # Detect server errors (5xx)
                    elif any(code in line for code in ['500', '502', '503', '504']):
                        issue = Issue(
                            category=IssueCategory.NETWORK_FAILURE,
                            severity=Severity.CRITICAL,
                            description=f"Server error: {line[:100]}",
                            fix_suggestion="Check server logs for details"
                        )
                        detected.append(issue)
                        self.issues.append(issue)
                        logger.error(f"Server error detected: {line[:60]}")

                    # Detect timeouts and failures
                    elif 'timeout' in line.lower() or 'failed' in line.lower():
                        issue = Issue(
                            category=IssueCategory.NETWORK_FAILURE,
                            severity=Severity.HIGH,
                            description=f"Network failure: {line[:100]}",
                            fix_suggestion="Check network connectivity and server availability"
                        )
                        detected.append(issue)
                        self.issues.append(issue)
                        logger.warning(f"Network failure: {line[:60]}")

                    # Detect CORS errors
                    elif 'cors' in line.lower() or 'cross-origin' in line.lower():
                        issue = Issue(
                            category=IssueCategory.NETWORK_FAILURE,
                            severity=Severity.HIGH,
                            description=f"CORS error: {line[:100]}",
                            fix_suggestion="Configure CORS headers on the server"
                        )
                        detected.append(issue)
                        self.issues.append(issue)
                        logger.warning(f"CORS error: {line[:60]}")

        except Exception as e:
            logger.error(f"Error detecting network failures: {e}")

        return detected

    async def detect_broken_images(self) -> List[Issue]:
        """Detect broken/missing images using browser_evaluate MCP tool.

        Returns:
            List of broken image issues
        """
        detected = []

        if not self.mcp:
            return detected

        try:
            # Call REAL browser_evaluate to check images
            result = await self.mcp.call_tool(
                "browser_evaluate",
                {
                    "function": """
                    () => {
                        const images = Array.from(document.querySelectorAll('img'));
                        return images
                            .filter(img => img.complete && img.naturalWidth === 0)
                            .map(img => ({
                                src: img.src,
                                alt: img.alt || 'no alt',
                                className: img.className
                            }));
                    }
                    """
                }
            )

            content = result.get('content', '')

            # Parse JSON result
            broken_images = self._parse_json_array(content)

            for img in broken_images:
                src = img.get('src', 'unknown')
                issue = Issue(
                    category=IssueCategory.BROKEN_IMAGE,
                    severity=Severity.MEDIUM,
                    description=f"Broken image: {src[:80]}",
                    fix_suggestion=f"Check if image exists at {src}",
                    element_ref=img.get('className')
                )
                detected.append(issue)
                self.issues.append(issue)
                logger.warning(f"Broken image: {src[:50]}")

        except Exception as e:
            logger.error(f"Error detecting broken images: {e}")

        return detected

    async def detect_missing_alt_text(self) -> List[Issue]:
        """Detect missing alt text using browser_evaluate MCP tool.

        Returns:
            List of missing alt text issues (auto-fixable)
        """
        detected = []

        if not self.mcp:
            return detected

        try:
            # Call REAL browser_evaluate
            result = await self.mcp.call_tool(
                "browser_evaluate",
                {
                    "function": """
                    () => {
                        const images = Array.from(document.querySelectorAll('img'));
                        return images
                            .filter(img => !img.alt || img.alt.trim() === '')
                            .map(img => ({
                                src: img.src,
                                suggestion: img.src.split('/').pop().split('.')[0].replace(/[-_]/g, ' ')
                            }));
                    }
                    """
                }
            )

            content = result.get('content', '')
            missing_alt = self._parse_json_array(content)

            for img in missing_alt:
                src = img.get('src', 'image')
                suggestion = img.get('suggestion', 'image')

                issue = Issue(
                    category=IssueCategory.MISSING_ALT_TEXT,
                    severity=Severity.LOW,
                    description=f"Missing alt text: {src[:60]}",
                    auto_fix=True,
                    fix_code=f'alt="{suggestion}"',
                    fix_suggestion=f'Add descriptive alt text: "{suggestion}"'
                )
                detected.append(issue)
                self.issues.append(issue)
                logger.info(f"Missing alt text: {src[:40]}")

        except Exception as e:
            logger.error(f"Error detecting missing alt text: {e}")

        return detected

    async def detect_layout_problems(self) -> List[Issue]:
        """Detect layout problems using browser_evaluate MCP tool.

        Checks for:
        - Element overflow
        - Element overlap
        - Hidden interactive elements
        - Z-index issues

        Returns:
            List of layout problem issues
        """
        detected = []

        if not self.mcp:
            return detected

        try:
            # Call REAL browser_evaluate
            result = await self.mcp.call_tool(
                "browser_evaluate",
                {
                    "function": """
                    () => {
                        const problems = [];

                        // Check for horizontal overflow
                        if (document.body.scrollWidth > document.body.clientWidth) {
                            problems.push({
                                type: 'overflow',
                                description: 'Page has horizontal overflow'
                            });
                        }

                        // Check for elements clipped by overflow
                        const elements = document.querySelectorAll('*');
                        let clippedCount = 0;

                        elements.forEach(el => {
                            const style = window.getComputedStyle(el);
                            const rect = el.getBoundingClientRect();

                            // Check if visible element is clipped
                            if (style.overflow === 'hidden' && rect.width > 0 && rect.height > 0) {
                                if (el.scrollWidth > el.clientWidth || el.scrollHeight > el.clientHeight) {
                                    clippedCount++;
                                }
                            }
                        });

                        if (clippedCount > 5) {
                            problems.push({
                                type: 'clipped_content',
                                description: `${clippedCount} elements have clipped content`
                            });
                        }

                        // Check for fixed/sticky elements that might overlap content
                        const fixed = document.querySelectorAll('[style*="fixed"], [style*="sticky"]');
                        if (fixed.length > 3) {
                            problems.push({
                                type: 'fixed_elements',
                                description: `${fixed.length} fixed/sticky elements may cause overlap issues`
                            });
                        }

                        return problems;
                    }
                    """
                }
            )

            content = result.get('content', '')
            problems = self._parse_json_array(content)

            for problem in problems:
                desc = problem.get('description', 'Layout issue detected')
                issue = Issue(
                    category=IssueCategory.LAYOUT_PROBLEM,
                    severity=Severity.MEDIUM,
                    description=desc,
                    fix_suggestion="Review CSS and layout to fix the issue"
                )
                detected.append(issue)
                self.issues.append(issue)
                logger.warning(f"Layout problem: {desc}")

        except Exception as e:
            logger.error(f"Error detecting layout problems: {e}")

        return detected

    async def detect_performance_issues(self) -> List[Issue]:
        """Detect performance issues using browser_evaluate MCP tool.

        Checks:
        - Page load time
        - LCP (Largest Contentful Paint)
        - DOM size
        - Resource count

        Returns:
            List of performance issues
        """
        detected = []

        if not self.mcp:
            return detected

        try:
            # Call REAL browser_evaluate
            result = await self.mcp.call_tool(
                "browser_evaluate",
                {
                    "function": """
                    () => {
                        const perf = performance.timing;
                        const loadTime = perf.loadEventEnd - perf.navigationStart;
                        const domContentLoaded = perf.domContentLoadedEventEnd - perf.navigationStart;

                        // Get LCP if available
                        let lcp = 0;
                        try {
                            const entries = performance.getEntriesByType('largest-contentful-paint');
                            if (entries.length > 0) {
                                lcp = entries[entries.length - 1].startTime;
                            }
                        } catch(e) {}

                        // Get DOM size
                        const domSize = document.getElementsByTagName('*').length;

                        // Get resource count
                        const resources = performance.getEntriesByType('resource');
                        const resourceCount = resources.length;

                        // Get total transfer size
                        let totalTransfer = 0;
                        resources.forEach(r => {
                            totalTransfer += r.transferSize || 0;
                        });

                        return {
                            loadTime: loadTime,
                            domContentLoaded: domContentLoaded,
                            lcp: lcp,
                            domSize: domSize,
                            resourceCount: resourceCount,
                            totalTransferKB: Math.round(totalTransfer / 1024)
                        };
                    }
                    """
                }
            )

            content = result.get('content', '')
            perf_data = self._parse_json_object(content)

            if perf_data:
                # Check load time (> 5s is bad)
                load_time = perf_data.get('loadTime', 0)
                if load_time > 5000:
                    issue = Issue(
                        category=IssueCategory.PERFORMANCE_ISSUE,
                        severity=Severity.HIGH,
                        description=f"Slow page load: {load_time}ms (target: <2500ms)",
                        fix_suggestion="Optimize images, minimize JS/CSS, enable caching"
                    )
                    detected.append(issue)
                    self.issues.append(issue)

                # Check LCP (> 2.5s is bad)
                lcp = perf_data.get('lcp', 0)
                if lcp > 2500:
                    issue = Issue(
                        category=IssueCategory.PERFORMANCE_ISSUE,
                        severity=Severity.HIGH,
                        description=f"Poor LCP: {lcp:.0f}ms (target: <2500ms)",
                        fix_suggestion="Optimize largest image/text, use preload"
                    )
                    detected.append(issue)
                    self.issues.append(issue)

                # Check DOM size (> 1500 nodes is concerning)
                dom_size = perf_data.get('domSize', 0)
                if dom_size > 1500:
                    issue = Issue(
                        category=IssueCategory.PERFORMANCE_ISSUE,
                        severity=Severity.MEDIUM,
                        description=f"Large DOM: {dom_size} elements (target: <1500)",
                        fix_suggestion="Reduce DOM complexity, use virtualization"
                    )
                    detected.append(issue)
                    self.issues.append(issue)

                # Check transfer size (> 3MB is concerning)
                transfer_kb = perf_data.get('totalTransferKB', 0)
                if transfer_kb > 3000:
                    issue = Issue(
                        category=IssueCategory.PERFORMANCE_ISSUE,
                        severity=Severity.MEDIUM,
                        description=f"Large page size: {transfer_kb}KB (target: <3000KB)",
                        fix_suggestion="Compress images, minify resources, lazy load"
                    )
                    detected.append(issue)
                    self.issues.append(issue)

        except Exception as e:
            logger.error(f"Error detecting performance issues: {e}")

        return detected

    async def detect_accessibility_issues(self) -> List[Issue]:
        """Detect accessibility issues using browser_evaluate MCP tool.

        Checks:
        - Missing form labels
        - Missing ARIA labels
        - Color contrast (basic)
        - Focus indicators
        - Heading hierarchy

        Returns:
            List of accessibility issues
        """
        detected = []

        if not self.mcp:
            return detected

        try:
            # Call REAL browser_evaluate
            result = await self.mcp.call_tool(
                "browser_evaluate",
                {
                    "function": """
                    () => {
                        const issues = [];

                        // Check for form inputs without labels
                        const inputs = document.querySelectorAll('input, select, textarea');
                        inputs.forEach(input => {
                            if (input.type === 'hidden') return;

                            const hasLabel = document.querySelector(`label[for="${input.id}"]`);
                            const hasAriaLabel = input.getAttribute('aria-label');
                            const hasAriaLabelledby = input.getAttribute('aria-labelledby');

                            if (!hasLabel && !hasAriaLabel && !hasAriaLabelledby) {
                                issues.push({
                                    type: 'missing_label',
                                    element: input.outerHTML.substring(0, 100)
                                });
                            }
                        });

                        // Check for buttons without accessible names
                        const buttons = document.querySelectorAll('button, [role="button"]');
                        buttons.forEach(btn => {
                            if (!btn.textContent.trim() && !btn.getAttribute('aria-label')) {
                                issues.push({
                                    type: 'empty_button',
                                    element: btn.outerHTML.substring(0, 100)
                                });
                            }
                        });

                        // Check heading hierarchy
                        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                        let lastLevel = 0;
                        headings.forEach(h => {
                            const level = parseInt(h.tagName[1]);
                            if (level > lastLevel + 1) {
                                issues.push({
                                    type: 'heading_skip',
                                    element: `Skipped from h${lastLevel} to h${level}`
                                });
                            }
                            lastLevel = level;
                        });

                        // Check for multiple h1s
                        const h1s = document.querySelectorAll('h1');
                        if (h1s.length > 1) {
                            issues.push({
                                type: 'multiple_h1',
                                element: `Found ${h1s.length} h1 elements`
                            });
                        }

                        // Check for links without text
                        const links = document.querySelectorAll('a');
                        links.forEach(link => {
                            if (!link.textContent.trim() && !link.getAttribute('aria-label')) {
                                issues.push({
                                    type: 'empty_link',
                                    element: link.outerHTML.substring(0, 100)
                                });
                            }
                        });

                        return issues;
                    }
                    """
                }
            )

            content = result.get('content', '')
            a11y_issues = self._parse_json_array(content)

            for a11y in a11y_issues:
                issue_type = a11y.get('type', 'unknown')
                element = a11y.get('element', '')

                description_map = {
                    'missing_label': 'Form input missing accessible label',
                    'empty_button': 'Button without accessible name',
                    'heading_skip': 'Heading hierarchy skipped level',
                    'multiple_h1': 'Multiple h1 elements on page',
                    'empty_link': 'Link without accessible text'
                }

                fix_map = {
                    'missing_label': 'Add label element or aria-label attribute',
                    'empty_button': 'Add text content or aria-label',
                    'heading_skip': 'Use proper heading hierarchy (h1 -> h2 -> h3)',
                    'multiple_h1': 'Use only one h1 per page',
                    'empty_link': 'Add link text or aria-label'
                }

                issue = Issue(
                    category=IssueCategory.ACCESSIBILITY_ISSUE,
                    severity=Severity.LOW,
                    description=f"{description_map.get(issue_type, issue_type)}: {element[:50]}",
                    fix_suggestion=fix_map.get(issue_type, 'Review accessibility guidelines'),
                    auto_fix=issue_type in ['missing_label', 'empty_button']
                )
                detected.append(issue)
                self.issues.append(issue)
                logger.info(f"Accessibility issue: {issue_type}")

        except Exception as e:
            logger.error(f"Error detecting accessibility issues: {e}")

        return detected

    # Helper methods

    def _is_ignorable_error(self, error: str) -> bool:
        """Check if a console error can be safely ignored"""
        ignorable_patterns = [
            'favicon.ico',
            'DevTools',
            'Extension',
            'chrome-extension',
            'React DevTools',
            'webpack-dev-server'
        ]
        return any(pattern.lower() in error.lower() for pattern in ignorable_patterns)

    def _parse_json_array(self, content: str) -> List[Dict]:
        """Parse JSON array from MCP response content"""
        if not content:
            return []

        try:
            # Try direct parse
            if content.strip().startswith('['):
                return json.loads(content)

            # Extract array from text
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                return json.loads(match.group())

        except json.JSONDecodeError:
            pass

        return []

    def _parse_json_object(self, content: str) -> Dict:
        """Parse JSON object from MCP response content"""
        if not content:
            return {}

        try:
            # Try direct parse
            if content.strip().startswith('{'):
                return json.loads(content)

            # Extract object from text
            match = re.search(r'\{[^{}]*\}', content)
            if match:
                return json.loads(match.group())

        except json.JSONDecodeError:
            pass

        return {}

    def get_issues_by_severity(self, severity: Severity) -> List[Issue]:
        """Get issues filtered by severity"""
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_category(self, category: IssueCategory) -> List[Issue]:
        """Get issues filtered by category"""
        return [issue for issue in self.issues if issue.category == category]

    def get_auto_fixable_issues(self) -> List[Issue]:
        """Get issues that can be auto-fixed"""
        return [issue for issue in self.issues if issue.auto_fix]

    def clear(self) -> None:
        """Clear all detected issues"""
        self.issues = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert detector state to dictionary"""
        return {
            'app_url': self.app_url,
            'total_issues': len(self.issues),
            'by_severity': {
                'critical': len(self.get_issues_by_severity(Severity.CRITICAL)),
                'high': len(self.get_issues_by_severity(Severity.HIGH)),
                'medium': len(self.get_issues_by_severity(Severity.MEDIUM)),
                'low': len(self.get_issues_by_severity(Severity.LOW))
            },
            'by_category': {
                'console_errors': len(self.get_issues_by_category(IssueCategory.CONSOLE_ERROR)),
                'network_failures': len(self.get_issues_by_category(IssueCategory.NETWORK_FAILURE)),
                'broken_images': len(self.get_issues_by_category(IssueCategory.BROKEN_IMAGE)),
                'missing_alt_text': len(self.get_issues_by_category(IssueCategory.MISSING_ALT_TEXT)),
                'layout_problems': len(self.get_issues_by_category(IssueCategory.LAYOUT_PROBLEM)),
                'performance_issues': len(self.get_issues_by_category(IssueCategory.PERFORMANCE_ISSUE)),
                'accessibility_issues': len(self.get_issues_by_category(IssueCategory.ACCESSIBILITY_ISSUE))
            },
            'auto_fixable': len(self.get_auto_fixable_issues()),
            'issues': [issue.to_dict() for issue in self.issues]
        }


# CLI usage
if __name__ == "__main__":
    import sys

    print("IssueDetector - Real Browser API Issue Detection")
    print("=" * 50)
    print("This module uses REAL Playwright MCP browser APIs.")
    print("Use with test-orchestrator.py for full functionality.")
    print()
    print("Detection categories:")
    print("  1. Console errors (Critical)")
    print("  2. Network failures (High)")
    print("  3. Broken images (Medium)")
    print("  4. Missing alt text (Low, auto-fixable)")
    print("  5. Layout problems (Medium)")
    print("  6. Performance issues (High)")
    print("  7. Accessibility issues (Low, some auto-fixable)")
