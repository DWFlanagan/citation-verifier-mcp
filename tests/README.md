# Test Suite for Citation Verifier MCP

This directory contains comprehensive tests for the Citation Verifier MCP server. The tests are designed to be easy to understand and verify that core functionality works.

## Test Categories

### 🟢 Basic Functionality Tests (`test_basic_functionality.py`)

#### Question: "Does the MCP server start and work?"

- ✅ Can we initialize the MCP server?
- ✅ Is the citation verifier properly set up?
- ✅ Does the server report available tools?
- ✅ Can we verify a real DOI successfully?
- ✅ Does the system handle invalid DOIs gracefully?
- ✅ Can we call MCP tools with valid/invalid DOIs?
- ✅ Does calling unknown tools raise appropriate errors?
- ✅ Does the system fail gracefully when not initialized?

### 🌐 WebSocket Server Tests (`test_websocket_server.py`)

#### Question: "Does the remote WebSocket server work?"

- ✅ Can we reach the server health endpoint?
- ✅ Does the server info endpoint work?
- ✅ Can we list available tools via HTTP?
- ✅ Can we call verification tools via HTTP?
- ✅ Does the server handle errors gracefully?
- ✅ Can we establish WebSocket connections?
- ✅ Can we use MCP protocol over WebSocket?

### 🔄 Integration Tests (`test_integration.py`)

#### Question: "Does everything work together?"

- ✅ Can we verify citations end-to-end?
- ✅ Can the system handle multiple concurrent requests?
- ✅ Does error handling work robustly?
- ✅ Does result formatting work correctly?
- ✅ Are performance characteristics reasonable?
- ✅ Is the project structure correct?
- ✅ Are all dependencies available?

## Running Tests

### Quick Start

```bash
# Run all tests
./run_tests.sh

# Or manually with pytest
pytest tests/ -v
```

### Specific Test Categories

```bash
# Basic functionality only
pytest tests/test_basic_functionality.py -v

# WebSocket server only  
pytest tests/test_websocket_server.py -v

# Integration tests only
pytest tests/test_integration.py -v

# Skip slow network tests
pytest tests/ -v -m "not slow"

# Run only slow tests
pytest tests/ -v -m "slow"
```

### Development Testing

```bash
# Run tests with coverage
pytest tests/ --cov=src/citation_verifier_mcp

# Run tests in parallel (if you have pytest-xdist)
pytest tests/ -n auto

# Run tests with detailed output
pytest tests/ -v -s
```

## Test Data

The tests use these predefined DOIs:

- **Valid DOI**: `10.1038/nature12373` (real Nature paper)
- **Invalid DOI**: `10.1234/fake.citation.2024` (fake DOI)
- **Malformed DOI**: `not-a-doi` (invalid format)

## Understanding Test Results

### ✅ All Green - Everything Works

Your MCP server is working correctly and can:

- Start up properly
- Handle citation verification requests  
- Process valid and invalid DOIs
- Serve requests over WebSocket
- Handle errors gracefully

### ⚠️ Some Yellow - Network Issues

If slow tests fail but basic tests pass:

- Your code is correct
- You might have network connectivity issues
- The Crossref API might be temporarily unavailable
- This is usually not a problem with your code

### ❌ Red Tests - Something's Wrong

If basic tests fail:

- Check that dependencies are installed (`uv pip install -e ".[dev]"`)
- Ensure you're in the right directory
- Check that the MCP server code hasn't been modified incorrectly
- Look at the specific error messages for clues

## Adding New Tests

When adding features, add corresponding tests:

1. **New MCP tools**: Add tests to `test_basic_functionality.py`
2. **New API endpoints**: Add tests to `test_websocket_server.py`  
3. **New workflows**: Add tests to `test_integration.py`

Follow this pattern:

```python
async def test_your_new_feature(self) -> None:
    """Test: Does your new feature work?"""
    # Arrange - set up test data
    # Act - call your feature
    # Assert - check it worked
```

## Dependencies

The test suite requires:

- `pytest` - Test framework
- `pytest-asyncio` - For async test support
- `httpx` - For testing FastAPI endpoints
- `websockets` - For WebSocket testing

These are automatically installed when you run `./run_tests.sh` or install dev dependencies.
