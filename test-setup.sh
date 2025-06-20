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

# Check if the Docker image exists
echo "🔍 Checking Docker image..."
if ! docker images | grep -q mcp-video-downloader; then
    echo "❌ Docker image 'mcp-video-downloader' not found."
    echo "   Please run: docker build -t mcp-video-downloader ."
    exit 1
fi
echo "✅ Docker image found"

# Create test downloads directory
TEST_DIR="$(pwd)/test-downloads"
echo "📁 Creating test directory: $TEST_DIR"
mkdir -p "$TEST_DIR"

# Test the container startup
echo "🚀 Testing container startup..."
timeout 10s docker run --rm -i \
    --volume "$TEST_DIR:/downloads" \
    mcp-video-downloader \
    --safe-mode >/dev/null 2>&1 &
DOCKER_PID=$!

sleep 2

if kill -0 $DOCKER_PID 2>/dev/null; then
    echo "✅ Container starts successfully"
    kill $DOCKER_PID 2>/dev/null || true
else
    echo "❌ Container failed to start"
    exit 1
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

# Display example configuration
echo ""
echo "🎉 All tests passed! Your setup is ready."
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

# Cleanup
rmdir "$TEST_DIR" 2>/dev/null || true

echo "✅ Test completed successfully!"
