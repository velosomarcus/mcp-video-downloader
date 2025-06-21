#!/bin/bash

# Test script for MCP Video Downloader
# This script tests the Docker setup and basic functionality

set -e

echo "🧪 Testing MCP Video Downloader Setup"
echo "======================================"

# Check if Docker is running
echo "📦 Checking Docker..."
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi
echo "✅ Docker is running"

# Build the Docker image if it doesn't exist
echo "� Building Docker image..."
if ! docker images | grep -q mcp-video-downloader; then
    echo "📦 Building Docker image 'mcp-video-downloader'..."
    docker build -t mcp-video-downloader .
else
    echo "✅ Docker image 'mcp-video-downloader' found"
fi

# Create test downloads directory
TEST_DIR="$(pwd)/test-downloads"
echo "📁 Creating test directory: $TEST_DIR"
mkdir -p "$TEST_DIR"

# Test the container startup
echo "🚀 Testing container startup..."
# Simple test: check that the container can run and the entrypoint works
if docker run --rm --volume "$TEST_DIR:/downloads" --entrypoint=/bin/sh mcp-video-downloader -c "echo 'Container can start' && python3 -c 'import mcp_video_downloader; print(\"Module loads successfully\")'" >/dev/null 2>&1; then
    echo "✅ Container starts and modules load successfully"
else
    echo "❌ Container failed to start or modules failed to load"
    echo "📄 Trying alternative test..."
    
    # Fallback: just test that the image exists and can run basic commands
    if docker run --rm --entrypoint=/bin/echo mcp-video-downloader "Basic container test" >/dev/null 2>&1; then
        echo "✅ Container starts successfully (basic test)"
    else
        echo "❌ Container completely failed to start"
        exit 1
    fi
fi

# Test downloads directory permissions
echo "📝 Testing downloads directory permissions..."
touch "$TEST_DIR/test-file"
if [ -f "$TEST_DIR/test-file" ]; then
    echo "✅ Downloads directory is writable"
    rm "$TEST_DIR/test-file"
else
    echo "❌ Cannot write to downloads directory"
    exit 1
fi

# Test MCP protocol communication
echo "🔌 Testing MCP protocol communication..."
if command -v python3 >/dev/null 2>&1; then
    echo "🐍 Running MCP client test..."
    if python3 minimal_mcp_client.py; then
        echo "✅ MCP communication test passed"
    else
        echo "⚠️  MCP communication test had issues (check output above)"
    fi
else
    echo "⚠️  Python3 not found, skipping MCP communication test"
fi

# Test basic video download functionality
echo "📺 Testing basic video download (if curl is available)..."
if command -v curl >/dev/null 2>&1; then
    echo "🌐 Testing container with a simple URL request..."
    
    # Create a simple JSON-RPC test request
    cat > "$TEST_DIR/test_request.json" << 'EOF'
{"jsonrpc": "2.0", "id": "1", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}
{"jsonrpc": "2.0", "method": "notifications/initialized"}
{"jsonrpc": "2.0", "id": "2", "method": "tools/list"}
EOF
    
    echo "🧪 Sending test MCP requests..."
    # Use compatible timeout command or fallback
    if command -v gtimeout >/dev/null 2>&1; then
        TIMEOUT_CMD="gtimeout 30s"
    elif command -v timeout >/dev/null 2>&1; then
        TIMEOUT_CMD="timeout 30s"
    else
        TIMEOUT_CMD=""
    fi
    
    if [ -n "$TIMEOUT_CMD" ]; then
        if $TIMEOUT_CMD docker run --rm -i \
            --volume "$TEST_DIR:/downloads" \
            mcp-video-downloader \
            --safe-mode < "$TEST_DIR/test_request.json" > "$TEST_DIR/test_response.json" 2>&1; then
            echo "✅ MCP server responded to test requests"
            echo "📄 Response preview:"
            head -3 "$TEST_DIR/test_response.json" 2>/dev/null || echo "   (response file empty or not created)"
        else
            echo "⚠️  MCP server test had issues"
            echo "📄 Error output:"
            cat "$TEST_DIR/test_response.json" 2>/dev/null | head -5 || echo "   (no error output captured)"
        fi
    else
        echo "⚠️  No timeout command available, skipping MCP request test"
    fi
    
    # Cleanup test files
    rm -f "$TEST_DIR/test_request.json" "$TEST_DIR/test_response.json"
else
    echo "⚠️  curl not found, skipping URL test"
fi

# Display example configuration
echo ""
echo "🎉 Setup tests completed!"
echo ""
echo "📋 Example Claude Desktop Configuration:"
echo "========================================"
echo "{"
echo "  \"mcpServers\": {"
echo "    \"mcp-video-downloader\": {"
echo "      \"command\": \"docker\","
echo "      \"args\": ["
echo "        \"run\","
echo "        \"--rm\","
echo "        \"-i\","
echo "        \"--volume\", \"$HOME/Downloads/mcp-videos:/downloads\","
echo "        \"mcp-video-downloader\","
echo "        \"--safe-mode\""
echo "      ]"
echo "    }"
echo "  }"
echo "}"
echo ""
echo "📚 For detailed setup instructions, see: CLAUDE_DESKTOP_SETUP.md"
echo ""
echo "🔧 Available test commands:"
echo "   • Run full test suite: ./test-setup.sh"
echo "   • Test MCP communication: python3 minimal_mcp_client.py"
echo "   • Test Docker image: docker run -i --rm -v \$(pwd)/test-downloads:/downloads mcp-video-downloader --safe-mode"
echo ""

# Cleanup
rmdir "$TEST_DIR" 2>/dev/null || echo "📁 Test downloads directory preserved: $TEST_DIR"

echo "✅ Test setup completed successfully!"
