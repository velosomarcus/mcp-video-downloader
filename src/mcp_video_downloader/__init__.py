from .server import serve

def main():
    """MCP Video Downloader - Entry point for the server."""
    import argparse
    import asyncio
    import sys
    import os
    
    # Ensure we don't have any unwanted output that could interfere with MCP JSON
    parser = argparse.ArgumentParser(
        description="MCP Video Downloader Server - Downloads videos and streams them to clients"
    )
    parser.add_argument("--help", action="help", help="Show this help message and exit")
    
    args = parser.parse_args()
    
    # Suppress any potential output from imported modules
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        # Exit gracefully without printing anything
        sys.exit(0)
    except Exception as e:
        # Print error to stderr to avoid interfering with stdout JSON
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
