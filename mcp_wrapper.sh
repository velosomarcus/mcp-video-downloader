#!/bin/bash
# Wrapper script to ensure clean JSON output for MCP protocol

# Redirect any potential stderr output to /dev/null to prevent JSON contamination
exec python -m mcp_video_downloader 2>/dev/null
