"""
WebSocket server tests - "Does the remote WebSocket server work?"

These tests verify that the WebSocket/FastAPI server can start and handle requests.
"""

import json
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
async def test_app() -> AsyncGenerator[TestClient, None]:
    """Create a test client for the FastAPI app."""
    from citation_verifier_mcp.websocket_server import app

    with TestClient(app) as client:
        yield client


class TestWebSocketServer:
    """Test the WebSocket server functionality."""

    def test_server_health_check(self, test_app: TestClient) -> None:
        """Test: Can we reach the server health endpoint?"""
        response = test_app.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert data["service"] == "citation-verifier-mcp"

    def test_server_info_endpoint(self, test_app: TestClient) -> None:
        """Test: Does the server info endpoint work?"""
        response = test_app.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "Citation Verifier MCP Server"
        assert "version" in data
        assert "description" in data
        assert "endpoints" in data

    def test_list_tools_endpoint(self, test_app: TestClient) -> None:
        """Test: Can we list available tools via HTTP MCP protocol?"""
        # Use MCP JSON-RPC protocol over HTTP POST
        mcp_request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        response = test_app.post("/", json=mcp_request)
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert "result" in data
        assert "tools" in data["result"]
        assert len(data["result"]["tools"]) == 1
        tool = data["result"]["tools"][0]
        assert tool["name"] == "verify_citation"

    def test_call_tool_endpoint_valid_doi(self, test_app: TestClient) -> None:
        """Test: Can we call the verification tool via HTTP MCP protocol with a valid DOI?"""
        from tests.conftest import VALID_DOI

        mcp_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "verify_citation", "arguments": {"doi": VALID_DOI}},
        }
        response = test_app.post("/", json=mcp_request)
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 2
        assert "result" in data
        # The result should contain the verification result
        assert "content" in data["result"]

    def test_call_tool_endpoint_invalid_doi(self, test_app: TestClient) -> None:
        """Test: Can we call the verification tool via HTTP MCP protocol with an invalid DOI?"""
        from tests.conftest import INVALID_DOI

        mcp_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "verify_citation", "arguments": {"doi": INVALID_DOI}},
        }
        response = test_app.post("/", json=mcp_request)
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 3
        assert "result" in data
        # The result should contain the verification result
        assert "content" in data["result"]

    def test_call_unknown_tool_returns_error(self, test_app: TestClient) -> None:
        """Test: Does calling an unknown tool return an error?"""
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "nonexistent_tool", "arguments": {}},
        }
        response = test_app.post("/", json=mcp_request)
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 4
        assert "error" in data
        assert "Unknown tool" in data["error"]["message"]

    def test_call_tool_missing_arguments(self, test_app: TestClient) -> None:
        """Test: Does calling a tool without required arguments return an error?"""
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "verify_citation",
                "arguments": {},  # Missing 'doi'
            },
        }
        response = test_app.post("/", json=mcp_request)
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 5
        # The server returns a result with error text, not an error field
        assert "result" in data
        assert "Error during citation verification" in str(data["result"])

    def test_invalid_json_request(self, test_app: TestClient) -> None:
        """Test: Does the server handle invalid JSON gracefully?"""
        response = test_app.post(
            "/", content="invalid json", headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Unprocessable Entity


class TestWebSocketConnection:
    """Test WebSocket functionality (basic connection tests)."""

    def test_websocket_connection_basic(self, test_app: TestClient) -> None:
        """Test: Can we establish a WebSocket connection?"""
        with test_app.websocket_connect("/mcp") as websocket:
            # Connection should be established
            assert websocket is not None

    def test_websocket_list_tools(self, test_app: TestClient) -> None:
        """Test: Can we list tools via WebSocket?"""
        with test_app.websocket_connect("/mcp") as websocket:
            # Send list tools request
            message = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
            websocket.send_text(json.dumps(message))

            # Receive response
            response = websocket.receive_text()
            data = json.loads(response)

            # WebSocket responses don't include jsonrpc field in this implementation
            assert data["id"] == 1
            assert "result" in data
            assert "tools" in data["result"]

    def test_websocket_call_tool(self, test_app: TestClient) -> None:
        """Test: Can we call a tool via WebSocket?"""
        from tests.conftest import VALID_DOI

        with test_app.websocket_connect("/mcp") as websocket:
            # Send tool call request
            message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "verify_citation", "arguments": {"doi": VALID_DOI}},
            }
            websocket.send_text(json.dumps(message))

            # Receive response
            response = websocket.receive_text()
            data = json.loads(response)

            # WebSocket responses don't include jsonrpc field in this implementation
            assert data["id"] == 2
            assert "result" in data
