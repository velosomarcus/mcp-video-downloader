#!/usr/bin/env python3
"""
Debug version of the MCP server to help diagnose startup issues.
"""

import asyncio
import sys
import traceback

def debug_main():
    """Debug version of main with detailed error reporting."""
    try:
        print("Debug: Starting MCP Video Downloader...", file=sys.stderr)
        
        # Test imports
        print("Debug: Testing imports...", file=sys.stderr)
        from mcp_video_downloader.server import serve
        print("Debug: Imports successful", file=sys.stderr)
        
        # Test server initialization
        print("Debug: Starting server...", file=sys.stderr)
        asyncio.run(serve())
        
    except ImportError as e:
        print(f"Debug: Import error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Debug: Unexpected error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    debug_main()
