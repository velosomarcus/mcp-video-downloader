#!/bin/bash

# Test script for MCP Video Downloader with wrapper
echo "🧪 Testing MCP Video Downloader with wrapper script"

# Create a temporary file for MCP commands
TEMP_COMMANDS=$(mktemp)

# Write MCP commands to the temporary file
cat > "$TEMP_COMMANDS" << 'EOF'
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0"}}}
{"jsonrpc": "2.0", "method": "notifications/initialized"}
{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
EOF

echo "📝 Sending MCP commands through wrapper script..."
echo ""

# Send commands to the wrapper script
cat "$TEMP_COMMANDS" | ./run-mcp-video-downloader.sh

# Clean up
rm "$TEMP_COMMANDS"

echo ""
echo "✅ Test completed - Check that /downloads directory is used by default"
