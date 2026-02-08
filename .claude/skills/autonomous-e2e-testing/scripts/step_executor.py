#!/usr/bin/env python3
"""
Step Executor Engine

Executes YAML scenario steps using Playwright MCP tools.
Maps step actions to corresponding MCP tool calls.

Step Actions:
- navigate: browser_navigate
- click: browser_click
- type_text: browser_type
- fill_form: browser_fill_form
- wait_for: browser_wait_for
- check_console: browser_console_messages
- check_network: browser_network_requests
- screenshot: browser_take_screenshot
- evaluate: browser_evaluate
- scroll_to: browser_evaluate (scrollIntoView)
- find_element: browser_snapshot + parse
- refresh: browser_navigate (same URL)
- resize_viewport: browser_resize
"""

import asyncio
import json
import logging
import re
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from mcp_client import MCPClient, MCPClientError

logger = logging.getLogger(__name__)


@dataclass
class StepResult:
    """Result of executing a step"""
    step_name: str
    action: str
    success: bool
    duration_ms: int = 0
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    screenshot_path: Optional[str] = None


@dataclass
class ScenarioContext:
    """Context shared across steps in a scenario"""
    base_url: str
    variables: Dict[str, Any] = field(default_factory=dict)
    current_url: str = ""
    element_refs: Dict[str, str] = field(default_factory=dict)
    screenshots: List[str] = field(default_factory=list)
    console_messages: List[str] = field(default_factory=list)
    network_requests: List[Dict] = field(default_factory=list)


class StepExecutor:
    """
    Executes test scenario steps using Playwright MCP.

    Maps YAML step definitions to MCP tool calls and captures results.
    """

    def __init__(
        self,
        mcp_client: MCPClient,
        screenshot_dir: str = "./screenshots"
    ):
        """Initialize step executor.

        Args:
            mcp_client: Connected MCPClient instance
            screenshot_dir: Directory for saving screenshots
        """
        self.mcp = mcp_client
        self.screenshot_dir = screenshot_dir
        os.makedirs(screenshot_dir, exist_ok=True)

        # Action handlers mapping
        self.action_handlers = {
            "navigate": self._handle_navigate,
            "click": self._handle_click,
            "type_text": self._handle_type,
            "fill_form": self._handle_fill_form,
            "wait_for": self._handle_wait_for,
            "check_console": self._handle_check_console,
            "check_network": self._handle_check_network,
            "screenshot": self._handle_screenshot,
            "evaluate": self._handle_evaluate,
            "scroll_to": self._handle_scroll_to,
            "find_element": self._handle_find_element,
            "refresh": self._handle_refresh,
            "resize_viewport": self._handle_resize,
        }

    async def execute_scenario(
        self,
        scenario: Dict[str, Any],
        base_url: str
    ) -> Tuple[bool, List[StepResult]]:
        """Execute all steps in a scenario.

        Args:
            scenario: Scenario definition from YAML
            base_url: Base URL for the app

        Returns:
            Tuple of (success, list of step results)
        """
        context = ScenarioContext(base_url=base_url)
        results: List[StepResult] = []
        scenario_passed = True

        steps = scenario.get("steps", [])

        for i, step in enumerate(steps):
            step_num = i + 1
            action = step.get("action", "unknown")

            logger.debug(f"Executing step {step_num}/{len(steps)}: {action}")

            try:
                result = await self.execute_step(step, context)
                results.append(result)

                if not result.success:
                    logger.warning(f"Step {step_num} failed: {result.error}")
                    scenario_passed = False
                    # Continue execution to gather more information
                else:
                    logger.debug(f"Step {step_num} passed in {result.duration_ms}ms")

            except Exception as e:
                logger.error(f"Step {step_num} exception: {e}")
                results.append(StepResult(
                    step_name=f"Step {step_num}",
                    action=action,
                    success=False,
                    error=str(e)
                ))
                scenario_passed = False

        return scenario_passed, results

    async def execute_step(
        self,
        step: Dict[str, Any],
        context: ScenarioContext
    ) -> StepResult:
        """Execute a single step.

        Args:
            step: Step definition from YAML
            context: Scenario context with variables

        Returns:
            StepResult with execution outcome
        """
        action = step.get("action", "unknown")
        start_time = datetime.now()

        handler = self.action_handlers.get(action)

        if not handler:
            return StepResult(
                step_name=f"{action} step",
                action=action,
                success=False,
                error=f"Unknown action: {action}"
            )

        try:
            result = await handler(step, context)

            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            result.duration_ms = duration_ms

            return result

        except MCPClientError as e:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return StepResult(
                step_name=f"{action} step",
                action=action,
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )

    def _substitute_variables(self, value: str, context: ScenarioContext) -> str:
        """Substitute {{variable}} placeholders in value"""
        if not isinstance(value, str):
            return value

        # Replace {{base_url}}
        value = value.replace("{{base_url}}", context.base_url)

        # Replace {{variable_name}} with stored values
        pattern = r'\{\{(\w+)\}\}'
        matches = re.findall(pattern, value)

        for var_name in matches:
            if var_name in context.variables:
                value = value.replace(f"{{{{{var_name}}}}}", str(context.variables[var_name]))
            elif var_name in context.element_refs:
                value = value.replace(f"{{{{{var_name}}}}}", context.element_refs[var_name])

        return value

    # === Action Handlers ===

    async def _handle_navigate(
        self,
        step: Dict[str, Any],
        context: ScenarioContext
    ) -> StepResult:
        """Handle navigate action"""
        url = self._substitute_variables(step.get("url", ""), context)

        result = await self.mcp.navigate(url)
        context.current_url = url

        return StepResult(
            step_name=f"Navigate to {url}",
            action="navigate",
            success=True,
            data={"url": url, "result": result}
        )

    async def _handle_click(
        self,
        step: Dict[str, Any],
        context: ScenarioContext
    ) -> StepResult:
        """Handle click action"""
        ref = self._substitute_variables(step.get("ref", ""), context)
        element_desc = step.get("element", "")

        if not ref:
            return StepResult(
                step_name="Click element",
                action="click",
                success=False,
                error="No ref specified for click"
            )

        result = await self.mcp.click(ref, element_desc if element_desc else None)

        return StepResult(
            step_name=f"Click {element_desc or ref}",
            action="click",
            success=True,
            data={"ref": ref, "result": result}
        )

    async def _handle_type(
        self,
        step: Dict[str, Any],
        context: ScenarioContext
    ) -> StepResult:
        """Handle type_text action"""
        ref = self._substitute_variables(step.get("ref", ""), context)
        text = self._substitute_variables(step.get("text", ""), context)
        submit = step.get("submit", False)

        result = await self.mcp.type_text(ref, text, submit)

        return StepResult(
            step_name=f"Type '{text[:20]}...'",
            action="type_text",
            success=True,
            data={"ref": ref, "text": text, "result": result}
        )

    async def _handle_fill_form(
        self,
        step: Dict[str, Any],
        context: ScenarioContext
    ) -> StepResult:
        """Handle fill_form action"""
        fields = step.get("fields", [])

        # Get snapshot first to find form field refs
        snapshot_result = await self.mcp.get_snapshot()
        snapshot_content = snapshot_result.get("content", "")

        # Parse snapshot to find field refs (simplified matching)
        form_fields = []
        for field in fields:
            field_name = field.get("name", "")
            field_value = self._substitute_variables(field.get("value", ""), context)
            field_type = field.get("type", "textbox")

            # Try to find ref for this field in snapshot
            # This is a simplified approach - real implementation would parse snapshot properly
            ref = self._find_element_ref(snapshot_content, field_name)

            if ref:
                form_fields.append({
                    "name": field_name,
                    "type": field_type,
                    "ref": ref,
                    "value": field_value
                })

        if form_fields:
            result = await self.mcp.fill_form(form_fields)
            return StepResult(
                step_name=f"Fill form with {len(form_fields)} fields",
                action="fill_form",
                success=True,
                data={"fields": form_fields, "result": result}
            )
        else:
            return StepResult(
                step_name="Fill form",
                action="fill_form",
                success=False,
                error="Could not find form field references"
            )

    async def _handle_wait_for(
        self,
        step: Dict[str, Any],
        context: ScenarioContext
    ) -> StepResult:
        """Handle wait_for action"""
        text = step.get("text")
        timeout = step.get("timeout", 5000)
        wait_time = step.get("time")

        if wait_time:
            # Wait for specific time (in ms)
            result = await self.mcp.wait_for(time=wait_time // 1000)
            return StepResult(
                step_name=f"Wait {wait_time}ms",
                action="wait_for",
                success=True,
                data={"time_ms": wait_time}
            )
        elif text:
            result = await self.mcp.wait_for(text=text)
            return StepResult(
                step_name=f"Wait for '{text}'",
                action="wait_for",
                success=True,
                data={"text": text, "result": result}
            )
        else:
            # Default wait
            await asyncio.sleep(1)
            return StepResult(
                step_name="Wait 1 second",
                action="wait_for",
                success=True
            )

    async def _handle_check_console(
        self,
        step: Dict[str, Any],
        context: ScenarioContext
    ) -> StepResult:
        """Handle check_console action"""
        level = step.get("level", "error")

        result = await self.mcp.get_console_messages(level)
        content = result.get("content", "")

        # Parse console messages
        messages = [m.strip() for m in content.split('\n') if m.strip()]
        context.console_messages.extend(messages)

        # Check for errors
        has_errors = len(messages) > 0 and level == "error"

        return StepResult(
            step_name=f"Check console ({level})",
            action="check_console",
            success=not has_errors or level != "error",
            data={
                "level": level,
                "messages": messages,
                "error_count": len(messages) if level == "error" else 0
            }
        )

    async def _handle_check_network(
        self,
        step: Dict[str, Any],
        context: ScenarioContext
    ) -> StepResult:
        """Handle check_network action"""
        min_status = step.get("min_status", 200)
        max_status = step.get("max_status", 299)

        result = await self.mcp.get_network_requests(include_static=False)
        content = result.get("content", "")

        # Parse network requests
        lines = content.split('\n') if content else []

        failures = []
        for line in lines:
            # Check for error status codes
            if re.search(r'\b(404|500|502|503|504)\b', line):
                failures.append(line)
            elif 'failed' in line.lower() or 'timeout' in line.lower():
                failures.append(line)

        has_failures = len(failures) > 0

        return StepResult(
            step_name="Check network",
            action="check_network",
            success=not has_failures,
            data={
                "total_requests": len(lines),
                "failures": failures,
                "failure_count": len(failures)
            }
        )

    async def _handle_screenshot(
        self,
        step: Dict[str, Any],
        context: ScenarioContext
    ) -> StepResult:
        """Handle screenshot action"""
        name = step.get("name", f"screenshot-{datetime.now().strftime('%H%M%S')}")
        filename = f"{name}.png"
        filepath = os.path.join(self.screenshot_dir, filename)

        result = await self.mcp.take_screenshot(filename=filepath)

        context.screenshots.append(filepath)

        return StepResult(
            step_name=f"Screenshot: {name}",
            action="screenshot",
            success=True,
            screenshot_path=filepath,
            data={"filename": filename, "path": filepath}
        )

    async def _handle_evaluate(
        self,
        step: Dict[str, Any],
        context: ScenarioContext
    ) -> StepResult:
        """Handle evaluate action (JavaScript execution)"""
        function = step.get("function", "")
        store_as = step.get("store_as")
        assertions = step.get("assert", {})

        result = await self.mcp.evaluate(function)

        # Parse result content
        content = result.get("content", "")

        # Try to parse as JSON
        eval_result = None
        try:
            if isinstance(content, str):
                # Try to extract JSON from the content
                json_match = re.search(r'\{[^{}]*\}', content)
                if json_match:
                    eval_result = json.loads(json_match.group())
                else:
                    eval_result = {"raw": content}
            else:
                eval_result = content
        except json.JSONDecodeError:
            eval_result = {"raw": content}

        # Store result if requested
        if store_as and eval_result:
            context.variables[store_as] = eval_result

        # Check assertions
        assertion_passed = True
        assertion_errors = []

        for key, expected in assertions.items():
            if eval_result and isinstance(eval_result, dict):
                actual = eval_result.get(key)
                if not self._check_assertion(actual, expected):
                    assertion_passed = False
                    assertion_errors.append(f"{key}: expected {expected}, got {actual}")

        return StepResult(
            step_name="Evaluate JavaScript",
            action="evaluate",
            success=assertion_passed,
            data={
                "result": eval_result,
                "assertions": assertions,
                "assertion_errors": assertion_errors
            },
            error="; ".join(assertion_errors) if assertion_errors else None
        )

    async def _handle_scroll_to(
        self,
        step: Dict[str, Any],
        context: ScenarioContext
    ) -> StepResult:
        """Handle scroll_to action"""
        selector = step.get("selector", "")

        function = f"""
        () => {{
            const el = document.querySelector('{selector}');
            if (el) {{
                el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                return {{ scrolled: true }};
            }}
            return {{ scrolled: false }};
        }}
        """

        result = await self.mcp.evaluate(function)

        return StepResult(
            step_name=f"Scroll to {selector}",
            action="scroll_to",
            success=True,
            data={"selector": selector}
        )

    async def _handle_find_element(
        self,
        step: Dict[str, Any],
        context: ScenarioContext
    ) -> StepResult:
        """Handle find_element action - find element by text content"""
        contains = step.get("contains", "")
        store_as = step.get("store_as")

        # Get page snapshot
        snapshot_result = await self.mcp.get_snapshot()
        snapshot_content = snapshot_result.get("content", "")

        # Find element ref by matching text
        ref = self._find_element_ref(snapshot_content, contains)

        if ref and store_as:
            context.element_refs[store_as] = ref
            return StepResult(
                step_name=f"Find element '{contains}'",
                action="find_element",
                success=True,
                data={"contains": contains, "ref": ref, "stored_as": store_as}
            )
        else:
            return StepResult(
                step_name=f"Find element '{contains}'",
                action="find_element",
                success=False,
                error=f"Element containing '{contains}' not found"
            )

    async def _handle_refresh(
        self,
        step: Dict[str, Any],
        context: ScenarioContext
    ) -> StepResult:
        """Handle page refresh"""
        # Navigate to current URL again
        url = context.current_url or context.base_url

        result = await self.mcp.navigate(url)

        return StepResult(
            step_name="Refresh page",
            action="refresh",
            success=True,
            data={"url": url}
        )

    async def _handle_resize(
        self,
        step: Dict[str, Any],
        context: ScenarioContext
    ) -> StepResult:
        """Handle viewport resize"""
        width = step.get("width", 1280)
        height = step.get("height", 720)

        result = await self.mcp.resize(width, height)

        return StepResult(
            step_name=f"Resize to {width}x{height}",
            action="resize_viewport",
            success=True,
            data={"width": width, "height": height}
        )

    # === Helper Methods ===

    def _find_element_ref(self, snapshot: str, text: str) -> Optional[str]:
        """Find element ref in snapshot by matching text content.

        Args:
            snapshot: Accessibility snapshot content
            text: Text to search for

        Returns:
            Element ref if found, None otherwise
        """
        if not snapshot or not text:
            return None

        # Look for patterns like [ref=e42] or - ref: e42 followed by text
        # This is a simplified parser - real implementation would properly parse the snapshot
        lines = snapshot.split('\n')

        for i, line in enumerate(lines):
            if text.lower() in line.lower():
                # Try to find ref in this line or nearby
                ref_match = re.search(r'\[ref=(\w+)\]', line)
                if ref_match:
                    return ref_match.group(1)

                # Look for ref in preceding lines
                for j in range(max(0, i-3), i):
                    ref_match = re.search(r'\[ref=(\w+)\]', lines[j])
                    if ref_match:
                        return ref_match.group(1)

        return None

    def _check_assertion(self, actual: Any, expected: Any) -> bool:
        """Check if actual value matches expected assertion.

        Args:
            actual: Actual value from evaluation
            expected: Expected value (can be simple value or comparison string)

        Returns:
            True if assertion passes
        """
        if isinstance(expected, str):
            # Handle comparison operators
            if expected.startswith("> "):
                threshold = int(expected[2:])
                return actual is not None and actual > threshold
            elif expected.startswith("< "):
                threshold = int(expected[2:])
                return actual is not None and actual < threshold
            elif expected.startswith(">= "):
                threshold = int(expected[3:])
                return actual is not None and actual >= threshold
            elif expected.startswith("<= "):
                threshold = int(expected[3:])
                return actual is not None and actual <= threshold

        # Direct comparison
        return actual == expected


if __name__ == "__main__":
    # Test the step executor
    import sys

    async def test_executor():
        from mcp_client import MCPClient, check_server_available

        if not check_server_available():
            print("MCP server not running on port 8808")
            return

        client = MCPClient()
        await client.connect()

        executor = StepExecutor(client, "./test-screenshots")

        # Test scenario
        test_scenario = {
            "name": "Test Homepage",
            "steps": [
                {"action": "navigate", "url": "https://example.com"},
                {"action": "wait_for", "time": 1000},
                {"action": "screenshot", "name": "homepage"},
                {"action": "check_console", "level": "error"},
                {
                    "action": "evaluate",
                    "function": "() => ({ title: document.title })"
                }
            ]
        }

        context = ScenarioContext(base_url="https://example.com")

        for step in test_scenario["steps"]:
            result = await executor.execute_step(step, context)
            print(f"{result.action}: {'PASS' if result.success else 'FAIL'} ({result.duration_ms}ms)")
            if result.error:
                print(f"  Error: {result.error}")
            if result.data:
                print(f"  Data: {result.data}")

    asyncio.run(test_executor())
