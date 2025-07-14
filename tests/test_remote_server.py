#!/usr/bin/env python3
"""
Remote Citation Verifier MCP Server Test
Automatically starts the server and runs comprehensive tests.
"""

import asyncio
import json
import subprocess
import sys
import time
from typing import Optional

import websockets

# Configuration
SERVER_URL = "ws://localhost:8000/mcp"
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
TEST_DOI = "10.1038/nature12373"
INVALID_DOI = "invalid-doi-format"

class RemoteServerTester:
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None

    def start_server(self) -> subprocess.Popen:
        """Start the WebSocket server and return the process."""
        print("🚀 Starting WebSocket server...")
        try:
            # Start server directly with uvicorn
            self.server_process = subprocess.Popen(
                [
                    sys.executable, "-m", "uvicorn",
                    "src.citation_verifier_mcp.websocket_server:app",
                    "--host", SERVER_HOST,
                    "--port", str(SERVER_PORT),
                    "--log-level", "warning"  # Reduce noise
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for server to start
            print("⏳ Waiting for server to start...")
            time.sleep(4)  # Give it time to fully initialize

            # Check if process is still running
            if self.server_process.poll() is not None:
                # Process has terminated, read output
                stdout, stderr = self.server_process.communicate()
                print("❌ Server failed to start:")
                print(f"   stdout: {stdout}")
                print(f"   stderr: {stderr}")
                raise RuntimeError("Server startup failed")

            print("✅ Server started successfully!")
            return self.server_process

        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            raise

    def stop_server(self):
        """Stop the WebSocket server."""
        if self.server_process:
            print("🛑 Stopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.server_process.wait()
            print("✅ Server stopped")

    async def test_connection(self) -> bool:
        """Test basic WebSocket connection."""
        print("\n🔗 Testing WebSocket connection...")
        try:
            async with websockets.connect(SERVER_URL) as websocket:
                print("✅ Successfully connected to WebSocket")
                return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    async def test_tools_list(self) -> bool:
        """Test tools listing functionality."""
        print("\n📋 Testing tools list...")
        try:
            async with websockets.connect(SERVER_URL) as websocket:
                request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                }

                await websocket.send(json.dumps(request))
                response = await websocket.recv()
                response_data = json.loads(response)

                if "result" in response_data and "tools" in response_data["result"]:
                    tools = response_data["result"]["tools"]
                    print(f"✅ Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"   - {tool['name']}: {tool['description']}")
                    return len(tools) > 0
                else:
                    print(f"❌ Unexpected response format: {response_data}")
                    return False

        except Exception as e:
            print(f"❌ Tools list test failed: {e}")
            return False

    async def test_citation_verification(self) -> bool:
        """Test citation verification with a valid DOI."""
        print(f"\n🔍 Testing citation verification with DOI: {TEST_DOI}")
        try:
            async with websockets.connect(SERVER_URL) as websocket:
                request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "verify_citation",
                        "arguments": {
                            "doi": TEST_DOI
                        }
                    }
                }

                await websocket.send(json.dumps(request))
                response = await websocket.recv()
                response_data = json.loads(response)

                if "result" in response_data:
                    result = response_data["result"]
                    print("✅ Citation verification successful!")
                    print(f"   Content type: {result.get('content', [{}])[0].get('type', 'unknown')}")
                    if result.get('content') and len(result['content']) > 0:
                        content = result['content'][0].get('text', '')
                        if len(content) > 100:
                            print(f"   Preview: {content[:100]}...")
                        else:
                            print(f"   Content: {content}")
                    return True
                else:
                    print(f"❌ Verification failed: {response_data}")
                    return False

        except Exception as e:
            print(f"❌ Citation verification test failed: {e}")
            return False

    async def test_invalid_doi(self) -> bool:
        """Test error handling with invalid DOI."""
        print(f"\n❌ Testing error handling with invalid DOI: {INVALID_DOI}")
        try:
            async with websockets.connect(SERVER_URL) as websocket:
                request = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "verify_citation",
                        "arguments": {
                            "doi": INVALID_DOI
                        }
                    }
                }

                await websocket.send(json.dumps(request))
                response = await websocket.recv()
                response_data = json.loads(response)

                # We expect an error or a content indicating failure
                if "error" in response_data:
                    print("✅ Error handling works correctly")
                    print(f"   Error: {response_data['error'].get('message', 'Unknown error')}")
                    return True
                elif "result" in response_data:
                    # Check if the result indicates a failure
                    result = response_data["result"]
                    content = result.get('content', [{}])[0].get('text', '')
                    if 'error' in content.lower() or 'invalid' in content.lower() or 'not found' in content.lower():
                        print("✅ Error handling works correctly (in content)")
                        print(f"   Response: {content[:100]}...")
                        return True
                    else:
                        print(f"⚠️  Unexpected success with invalid DOI: {content[:100]}...")
                        return False
                else:
                    print(f"❌ Unexpected response: {response_data}")
                    return False

        except Exception as e:
            print(f"❌ Invalid DOI test failed: {e}")
            return False

    async def run_all_tests(self) -> bool:
        """Run all tests and return overall success."""
        tests = [
            ("Connection Test", self.test_connection()),
            ("Tools List Test", self.test_tools_list()),
            ("Citation Verification Test", self.test_citation_verification()),
            ("Error Handling Test", self.test_invalid_doi()),
        ]

        results = []
        for test_name, test_coro in tests:
            try:
                result = await test_coro
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                results.append((test_name, False))

        # Summary
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)

        passed = 0
        total = len(results)

        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1

        print(f"\nResult: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! The remote MCP server is working correctly!")
            return True
        else:
            print("💥 Some tests failed. Check the output above for details.")
            return False

async def main():
    """Main test runner."""
    print("🧪 Testing Citation Verifier Remote MCP Server")
    print("=" * 50)

    tester = RemoteServerTester()

    try:
        # Start server
        tester.start_server()

        # Run tests
        success = await tester.run_all_tests()

        return success

    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return False
    finally:
        # Always stop server
        tester.stop_server()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
