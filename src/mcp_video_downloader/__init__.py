from .server import serve

def main():
    """MCP Video Downloader - Entry point for the server."""
    import argparse
    import asyncio
    import sys
    import os
    
    # Simple argument parsing that doesn't interfere with MCP protocol
    parser = argparse.ArgumentParser(
        description="MCP Video Downloader Server - Downloads videos and streams them to clients",
        add_help=False  # Disable automatic help to avoid conflicts
    )
    parser.add_argument("--help", action="store_true", help="Show this help message and exit")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    
    # Parse known args to allow for future extensibility
    args, unknown = parser.parse_known_args()
    
    if args.help:
        parser.print_help()
        sys.exit(0)
    
    if args.version:
        print("MCP Video Downloader 1.0.0")
        sys.exit(0)
    
    # Start the MCP server
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        # Exit gracefully without printing anything
        sys.exit(0)
    except Exception as e:
        # Print error to stderr to avoid interfering with stdout JSON
        print(f"MCP Server Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
