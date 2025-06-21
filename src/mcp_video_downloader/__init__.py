from .server import serve

# Read version from package metadata (pyproject.toml)
def get_version():
    """Get version from pyproject.toml or package metadata."""
    try:
        # Try to read from installed package metadata first
        from importlib.metadata import version
        return version("mcp-video-downloader")
    except importlib.metadata.PackageNotFoundError:
        # Fallback: read directly from pyproject.toml
        try:
            import os
            import sys
            
            # Find pyproject.toml - go up from src/mcp_video_downloader to project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            pyproject_path = os.path.join(project_root, "pyproject.toml")
            
            if os.path.exists(pyproject_path):
                with open(pyproject_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("version = "):
                            # Extract version from: version = "0.1.0"
                            version_line = line.strip()
                            start = version_line.find('"') + 1
                            end = version_line.rfind('"')
                            if start > 0 and end > start:
                                return version_line[start:end]
        except Exception:
            pass
        
        return "unknown"

__version__ = get_version()

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
        print(f"MCP Video Downloader v{__version__}")
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
