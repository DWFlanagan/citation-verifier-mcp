#!/usr/bin/env python3
"""
Simple test script to verify the WebSocket MCP server is working correctly.
"""

import asyncio
import json
import sys

import websockets


async def test_mcp_server() -> None:
    """Test the MCP WebSocket server."""
    uri = "ws://localhost:8000/mcp"

    try:
        print("🔗 Connecting to WebSocket server at", uri)
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")

            # Test 1: Initialize
            init_message = {
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05", "capabilities": {}},
            }

            print("\n📤 Sending initialize message...")
            await websocket.send(json.dumps(init_message))
            response = await websocket.recv()
            init_response = json.loads(response)
            print("📥 Received:", init_response)

            # Test 2: List tools
            list_tools_message = {"id": 2, "method": "tools/list", "params": {}}

            print("\n📤 Sending tools/list message...")
            await websocket.send(json.dumps(list_tools_message))
            response = await websocket.recv()
            tools_response = json.loads(response)
            print("📥 Received:", tools_response)

            # Test 3: Call citation verification tool
            verify_citation_message = {
                "id": 3,
                "method": "tools/call",
                "params": {"name": "verify_citation", "arguments": {"doi": "10.1038/nature12373"}},
            }

            print("\n📤 Sending citation verification request...")
            await websocket.send(json.dumps(verify_citation_message))
            response = await websocket.recv()
            verify_response = json.loads(response)
            print("📥 Received citation verification result:")
            if "result" in verify_response and "content" in verify_response["result"]:
                content = verify_response["result"]["content"][0]["text"]
                print(content[:200] + "..." if len(content) > 200 else content)
            else:
                print(verify_response)

            print("\n✅ All tests completed successfully!")

    except ConnectionRefusedError:
        print("❌ Connection refused. Make sure the server is running:")
        print("   Run: ./launch_remote_server.sh")
        print("   Or:  uv run python start_server.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("🧪 Testing Citation Verifier Remote MCP Server")
    print("=" * 50)
    asyncio.run(test_mcp_server())
