"""
Vercel Python API - Production-Ready Backend
Routes all API requests to the unified FastAPI backend.
Works with Vercel's Python runtime by exposing a WSGI app.
"""
import sys
import os
import json

# Ensure backend module can be imported
_api_dir = os.path.dirname(os.path.abspath(__file__))
if _api_dir not in sys.path:
    sys.path.insert(0, _api_dir)

# Global state for lazy loading
_backend_app = None
_backend_error = None

def _initialize_backend():
    """Initialize the backend on first request"""
    global _backend_app, _backend_error

    if _backend_app is not None or _backend_error is not None:
        return

    try:
        # Import the backend ASGI app
        from backend import app as fastapi_app

        # Use a simple sync wrapper that calls the async app
        # This is a workaround for Vercel's WSGI-only support
        from starlette.testclient import TestClient

        # Create a test client that internally handles async
        _backend_app = TestClient(fastapi_app)

    except Exception as e:
        import traceback
        _backend_error = {
            "error": f"Failed to initialize backend: {str(e)}",
            "trace": traceback.format_exc()[:300],
        }

def app(environ, start_response):
    """WSGI application entry point for Vercel"""
    _initialize_backend()

    if _backend_error:
        status = "500 Internal Server Error"
        output = json.dumps(_backend_error).encode()
        response_headers = [
            ("Content-type", "application/json"),
            ("Content-Length", str(len(output))),
        ]
        start_response(status, response_headers)
        return [output]

    try:
        # Get the request info from WSGI environ
        method = environ["REQUEST_METHOD"]
        path = environ.get("PATH_INFO", "/")
        query_string = environ.get("QUERY_STRING", "")

        # Read the body
        content_length = int(environ.get("CONTENT_LENGTH") or 0)
        body = environ["wsgi.input"].read(content_length) if content_length > 0 else None

        # Build the full URL
        url = path
        if query_string:
            url += f"?{query_string}"

        # Use the test client to make a request to the FastAPI app
        # This allows us to call ASGI from sync/WSGI context
        response = _backend_app.request(
            method,
            url,
            content=body,
            headers={
                k[5:].lower().replace("_", "-"): v
                for k, v in environ.items()
                if k.startswith("HTTP_")
            },
        )

        # Return the response
        status = f"{response.status_code} {response.reason_phrase or 'OK'}"
        output = response.content
        response_headers = list(response.headers.items())

        # Ensure Content-Length is set
        if ("Content-Length", str(len(output))) not in response_headers:
            response_headers.append(("Content-Length", str(len(output))))

        start_response(status, response_headers)
        return [output]

    except Exception as e:
        import traceback
        error_msg = f"Error handling request: {str(e)}"
        output = json.dumps({
            "error": error_msg,
            "trace": traceback.format_exc()[:300]
        }).encode()

        status = "500 Internal Server Error"
        response_headers = [
            ("Content-type", "application/json"),
            ("Content-Length", str(len(output))),
        ]
        start_response(status, response_headers)
        return [output]
