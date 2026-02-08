#!/usr/bin/env python3
"""
MCP Client Module for Test Orchestrator Integration

This module provides a high-level async interface for the test orchestrator
to communicate with the Playwright MCP server.

Usage:
    from mcp_client import MCPClient

    client = MCPClient(port=8808)
    await client.connect()
    result = await client.call_tool("browser_navigate", {"url": "http://localhost:3000"})
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

logger = logging.getLogger(__name__)


class MCPClientError(Exception):
    """Exception for MCP client errors"""
    pass


class MCPClient:
    """
    High-level MCP client for Playwright browser automation.

    Provides async methods for calling Playwright MCP tools:
    - browser_navigate: Navigate to a URL
    - browser_click: Click an element
    - browser_type: Type text into an element
    - browser_fill_form: Fill multiple form fields
    - browser_wait_for: Wait for text/element/time
    - browser_console_messages: Get console messages
    - browser_network_requests: Get network requests
    - browser_evaluate: Evaluate JavaScript
    - browser_snapshot: Get accessibility snapshot
    - browser_take_screenshot: Take a screenshot
    """

    def __init__(self, host: str = "localhost", port: int = 8808):
        """Initialize MCP client.

        Args:
            host: MCP server host (default: localhost)
            port: MCP server port (default: 8808)
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.mcp_url = f"{self.base_url}/mcp"
        self._request_id = 0
        self._session_id: Optional[str] = None
        self._initialized = False
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if client is connected to MCP server"""
        return self._connected and self._initialized

    def _next_id(self) -> int:
        """Get next request ID"""
        self._request_id += 1
        return self._request_id

    async def connect(self) -> bool:
        """Connect to the MCP server and initialize session.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Run initialization in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._initialize_sync)
            self._connected = result
            return result
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            self._connected = False
            return False

    def _initialize_sync(self) -> bool:
        """Synchronous initialization (runs in thread pool)"""
        if self._initialized:
            return True

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-orchestrator", "version": "1.0.0"}
            }
        }

        try:
            response = self._send_request(payload)
            if "error" in response:
                logger.error(f"Initialize failed: {response['error']}")
                return False

            self._initialized = True

            # Send initialized notification
            self._send_notification("notifications/initialized")

            logger.info(f"Connected to MCP server at {self.base_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize MCP session: {e}")
            return False

    def _send_request(self, payload: dict) -> dict:
        """Send a JSON-RPC request to MCP server"""
        data = json.dumps(payload).encode('utf-8')
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id

        req = Request(self.mcp_url, data=data, headers=headers, method='POST')

        try:
            with urlopen(req, timeout=60) as resp:
                # Capture session ID if present
                if not self._session_id:
                    self._session_id = resp.headers.get('Mcp-Session-Id')

                body = resp.read().decode('utf-8')
                return self._parse_response(body)

        except HTTPError as e:
            body = e.read().decode('utf-8') if e.fp else str(e)
            raise MCPClientError(f"HTTP {e.code}: {body}")
        except URLError as e:
            raise MCPClientError(f"Connection failed: {e.reason}")

    def _parse_response(self, body: str) -> dict:
        """Parse response body, handling SSE format if needed"""
        body = body.strip()

        # Handle SSE format (event stream)
        if body.startswith('event:') or body.startswith('data:'):
            for line in body.split('\n'):
                if line.startswith('data:'):
                    json_data = line[5:].strip()
                    if json_data:
                        return json.loads(json_data)
            raise MCPClientError("No data in SSE response")

        # Regular JSON response
        return json.loads(body)

    def _send_notification(self, method: str, params: Optional[dict] = None):
        """Send a notification (no response expected)"""
        payload = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params:
            payload["params"] = params

        data = json.dumps(payload).encode('utf-8')
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id

        req = Request(self.mcp_url, data=data, headers=headers, method='POST')
        try:
            with urlopen(req, timeout=30):
                pass
        except (HTTPError, URLError):
            pass  # Ignore notification errors

    async def call_tool(self, tool_name: str, arguments: Optional[dict] = None) -> dict:
        """Call an MCP tool asynchronously.

        Args:
            tool_name: Name of the tool (e.g., "browser_navigate")
            arguments: Tool arguments dictionary

        Returns:
            Tool result dictionary with 'content' and other fields
        """
        if not self._initialized:
            connected = await self.connect()
            if not connected:
                raise MCPClientError("Not connected to MCP server")

        # Run tool call in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._call_tool_sync,
            tool_name,
            arguments or {}
        )

    def _call_tool_sync(self, tool_name: str, arguments: dict) -> dict:
        """Synchronous tool call (runs in thread pool)"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        try:
            response = self._send_request(payload)

            if "error" in response:
                err = response["error"]
                raise MCPClientError(f"Tool error: {err.get('message', 'Unknown error')}")

            result = response.get("result", {})

            # Extract content from result
            content = result.get("content", [])
            if isinstance(content, list) and len(content) > 0:
                # Get text content from first content item
                first_item = content[0]
                if isinstance(first_item, dict):
                    if first_item.get("type") == "text":
                        return {"content": first_item.get("text", "")}
                    elif first_item.get("type") == "image":
                        return {"content": first_item.get("data", ""), "type": "image"}

            return {"content": result}

        except MCPClientError:
            raise
        except Exception as e:
            raise MCPClientError(f"Tool call failed: {e}")

    async def list_tools(self) -> List[dict]:
        """Get list of available tools from MCP server.

        Returns:
            List of tool definitions
        """
        if not self._initialized:
            await self.connect()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._list_tools_sync)

    def _list_tools_sync(self) -> List[dict]:
        """Synchronous tools list (runs in thread pool)"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list"
        }

        response = self._send_request(payload)
        result = response.get("result", {})
        return result.get("tools", [])

    # Convenience methods for common operations

    async def navigate(self, url: str) -> dict:
        """Navigate browser to URL"""
        return await self.call_tool("browser_navigate", {"url": url})

    async def click(self, ref: str, element: Optional[str] = None) -> dict:
        """Click an element by ref"""
        args = {"ref": ref}
        if element:
            args["element"] = element
        return await self.call_tool("browser_click", args)

    async def type_text(self, ref: str, text: str, submit: bool = False) -> dict:
        """Type text into an element"""
        return await self.call_tool("browser_type", {
            "ref": ref,
            "text": text,
            "submit": submit
        })

    async def fill_form(self, fields: List[dict]) -> dict:
        """Fill multiple form fields"""
        return await self.call_tool("browser_fill_form", {"fields": fields})

    async def wait_for(self, text: Optional[str] = None, time: Optional[int] = None) -> dict:
        """Wait for text or time"""
        args = {}
        if text:
            args["text"] = text
        if time:
            args["time"] = time
        return await self.call_tool("browser_wait_for", args)

    async def get_console_messages(self, level: str = "error") -> dict:
        """Get browser console messages"""
        return await self.call_tool("browser_console_messages", {"level": level})

    async def get_network_requests(self, include_static: bool = False) -> dict:
        """Get network requests"""
        return await self.call_tool("browser_network_requests", {
            "includeStatic": include_static
        })

    async def evaluate(self, function: str, ref: Optional[str] = None) -> dict:
        """Evaluate JavaScript in browser"""
        args = {"function": function}
        if ref:
            args["ref"] = ref
        return await self.call_tool("browser_evaluate", args)

    async def take_screenshot(
        self,
        filename: Optional[str] = None,
        full_page: bool = False,
        image_type: str = "png"
    ) -> dict:
        """Take a screenshot"""
        args = {"type": image_type}
        if filename:
            args["filename"] = filename
        if full_page:
            args["fullPage"] = True
        return await self.call_tool("browser_take_screenshot", args)

    async def get_snapshot(self) -> dict:
        """Get accessibility snapshot of current page"""
        return await self.call_tool("browser_snapshot", {})

    async def press_key(self, key: str) -> dict:
        """Press a key"""
        return await self.call_tool("browser_press_key", {"key": key})

    async def hover(self, ref: str, element: Optional[str] = None) -> dict:
        """Hover over an element"""
        args = {"ref": ref}
        if element:
            args["element"] = element
        return await self.call_tool("browser_hover", args)

    async def resize(self, width: int, height: int) -> dict:
        """Resize browser window"""
        return await self.call_tool("browser_resize", {
            "width": width,
            "height": height
        })

    async def close(self) -> dict:
        """Close browser"""
        return await self.call_tool("browser_close", {})


# Synchronous wrapper for non-async contexts
class SyncMCPClient:
    """
    Synchronous wrapper for MCPClient.

    Use this in contexts where async is not available.
    """

    def __init__(self, host: str = "localhost", port: int = 8808):
        self._async_client = MCPClient(host, port)
        self._loop = None

    def _get_loop(self):
        """Get or create event loop"""
        if self._loop is None or self._loop.is_closed():
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop

    def connect(self) -> bool:
        """Connect to MCP server"""
        loop = self._get_loop()
        return loop.run_until_complete(self._async_client.connect())

    def call_tool(self, tool_name: str, arguments: Optional[dict] = None) -> dict:
        """Call an MCP tool"""
        loop = self._get_loop()
        return loop.run_until_complete(
            self._async_client.call_tool(tool_name, arguments)
        )

    def navigate(self, url: str) -> dict:
        """Navigate to URL"""
        loop = self._get_loop()
        return loop.run_until_complete(self._async_client.navigate(url))

    def click(self, ref: str, element: Optional[str] = None) -> dict:
        """Click element"""
        loop = self._get_loop()
        return loop.run_until_complete(self._async_client.click(ref, element))

    def evaluate(self, function: str) -> dict:
        """Evaluate JavaScript"""
        loop = self._get_loop()
        return loop.run_until_complete(self._async_client.evaluate(function))

    def get_console_messages(self, level: str = "error") -> dict:
        """Get console messages"""
        loop = self._get_loop()
        return loop.run_until_complete(
            self._async_client.get_console_messages(level)
        )

    def get_network_requests(self, include_static: bool = False) -> dict:
        """Get network requests"""
        loop = self._get_loop()
        return loop.run_until_complete(
            self._async_client.get_network_requests(include_static)
        )

    def take_screenshot(self, filename: Optional[str] = None) -> dict:
        """Take screenshot"""
        loop = self._get_loop()
        return loop.run_until_complete(
            self._async_client.take_screenshot(filename)
        )

    def get_snapshot(self) -> dict:
        """Get page snapshot"""
        loop = self._get_loop()
        return loop.run_until_complete(self._async_client.get_snapshot())


def check_server_available(host: str = "localhost", port: int = 8808) -> bool:
    """Check if MCP server is running and accessible"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


if __name__ == "__main__":
    # Test the client
    import sys

    print("Testing MCP Client...")

    if not check_server_available():
        print("ERROR: MCP server not running on port 8808")
        print("Start it with: npx @playwright/mcp@latest --port 8808")
        sys.exit(1)

    client = SyncMCPClient()

    try:
        connected = client.connect()
        if connected:
            print("SUCCESS: Connected to MCP server")

            # Try navigating
            print("Navigating to example.com...")
            result = client.navigate("https://example.com")
            print(f"Navigate result: {result}")

            # Get snapshot
            print("Getting page snapshot...")
            snapshot = client.get_snapshot()
            print(f"Snapshot: {str(snapshot)[:200]}...")

        else:
            print("ERROR: Failed to connect")
            sys.exit(1)

    except MCPClientError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
