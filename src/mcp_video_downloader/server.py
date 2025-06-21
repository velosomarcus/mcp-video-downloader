"""
MCP Server with Video Download Tools

This module implements a Model Context Protocol (MCP) server that provides the following tools:
1. download_video: A video download tool using yt-dlp for downloading videos from various platforms

The server uses the MCP framework to expose these tools to AI assistants, allowing them to:
- Download videos from supported platforms like YouTube, Vimeo, etc.
- Save downloaded video files directly to the local filesystem via Docker volume mounts

Architecture:
- Uses async/await pattern for non-blocking operations
- Implements proper error handling and validation
- Provides detailed progress feedback for video downloads
- Supports various video formats and quality options
- Saves files to /downloads directory (mounted as Docker volume)

Dependencies:
- mcp: Model Context Protocol framework
- yt-dlp: YouTube-dl fork for video downloading
"""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yt_dlp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Downloads directory path - mounted as volume in Docker
DOWNLOADS_DIR = Path("/downloads")


class VideoDownloadError(Exception):
    """Custom exception for video download errors."""
    pass


def ensure_downloads_directory() -> None:
    """
    Ensure the downloads directory exists and is writable.
    
    Raises:
        VideoDownloadError: If the directory cannot be created or is not writable
    """
    try:
        DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
        # Test write permissions
        test_file = DOWNLOADS_DIR / ".write_test"
        test_file.touch()
        test_file.unlink()
    except Exception as e:
        raise VideoDownloadError(f"Cannot access downloads directory {DOWNLOADS_DIR}: {str(e)}")


def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from a file path.
    
    Args:
        file_path: Path to the file
    
    Returns:
        File extension (e.g., '.mp4', '.mp3')
    """
    return Path(file_path).suffix


def get_mime_type(file_path: str) -> str:
    """
    Get the MIME type based on file extension.
    
    Args:
        file_path: Path to the file
    
    Returns:
        MIME type string
    """
    extension = get_file_extension(file_path).lower()
    mime_types = {
        '.mp4': 'video/mp4',
        '.webm': 'video/webm',
        '.mkv': 'video/x-matroska',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.mp3': 'audio/mpeg',
        '.m4a': 'audio/mp4',
        '.ogg': 'audio/ogg',
        '.wav': 'audio/wav',
        '.flac': 'audio/flac'
    }
    return mime_types.get(extension, 'application/octet-stream')


class ProgressLogger:
    """
    Progress logger for yt-dlp downloads.
    
    This class handles progress updates during video downloads and provides
    meaningful feedback about the download status. All output is captured
    internally to avoid interfering with MCP JSON protocol.
    """
    
    def __init__(self):
        self.status_messages = []
    
    def __call__(self, d: Dict[str, Any]) -> None:
        """
        Progress hook for yt-dlp.
        
        Args:
            d: Dictionary containing download progress information
        """
        try:
            if d['status'] == 'downloading':
                # Extract progress information safely
                percent = d.get('_percent_str', 'N/A')
                speed = d.get('_speed_str', 'N/A')
                filename = os.path.basename(d.get('filename', 'Unknown'))
                
                message = f"Downloading {filename}: {percent} at {speed}"
                self.status_messages.append(message)
            
            elif d['status'] == 'finished':
                filename = os.path.basename(d.get('filename', 'Unknown'))
                message = f"Download completed: {filename}"
                self.status_messages.append(message)
            
            elif d['status'] == 'error':
                message = f"Download error: {d.get('error', 'Unknown error')}"
                self.status_messages.append(message)
        except Exception:
            # Silently ignore any errors in progress logging to avoid
            # interfering with the main download process
            pass


async def download_video_async(
    url: str,
    format_selector: str = "best[height<=720]"
) -> Dict[str, Any]:
    """
    Asynchronously download a video using yt-dlp and save to downloads directory.
    
    This function provides a high-level interface for downloading videos from
    various platforms. It downloads directly to the mounted downloads directory
    for easy access by the client through the Docker volume.
    
    Args:
        url: The URL of the video to download
        format_selector: yt-dlp format selector string (default: best quality up to 720p)
    
    Returns:
        Dictionary containing download results:
        - success: Boolean indicating if download succeeded
        - message: Status message
        - file_path: Path to the downloaded file (if successful)
        - file_name: Original filename (if successful)
        - file_size: Size of downloaded file in bytes (if successful)
        - mime_type: MIME type of the file (if successful)
        - duration: Video duration in seconds (if available)
        - title: Video title (if available)
        - progress_log: List of progress messages
    
    Raises:
        VideoDownloadError: If download fails or URL is invalid
    """
    
    # Ensure downloads directory exists
    ensure_downloads_directory()
    
    # Initialize progress logger
    progress_logger = ProgressLogger()
    
    # Configure yt-dlp options to save directly to downloads directory
    ydl_opts = {
        'outtmpl': str(DOWNLOADS_DIR / '%(title)s.%(ext)s'),
        'format': format_selector,
        'noplaylist': True,  # Download single video only
        'extract_flat': False,
        'writeinfojson': False,  # Don't save metadata files
        'writesubtitles': False,  # Don't download subtitles
        'progress_hooks': [progress_logger],
        'quiet': True,  # Suppress most output
        'no_warnings': True,
        'noprogress': True,  # Disable progress output
        'logger': None,  # Disable logging
    }

    try:
        # Run yt-dlp in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: _download_with_ytdl(url, ydl_opts)
        )
        
        # Add progress log to result
        result['progress_log'] = progress_logger.status_messages
        
        return result
        
    except Exception as e:
        raise VideoDownloadError(f"Failed to download video: {str(e)}")


def _download_with_ytdl(url: str, ydl_opts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Internal function to perform the actual download with yt-dlp.
    
    This function is executed in a thread executor to prevent blocking
    the async event loop during downloads. It downloads the file directly
    to the downloads directory for easy access via Docker volume.
    
    All stdout/stderr output is suppressed to prevent interference with MCP protocol.
    
    Args:
        url: Video URL to download
        ydl_opts: yt-dlp configuration options
    
    Returns:
        Dictionary with download results including file path
    """
    
    import sys
    import os
    from contextlib import redirect_stdout, redirect_stderr
    
    # Suppress all output to prevent interference with MCP JSON protocol
    with open(os.devnull, 'w') as devnull:
        with redirect_stdout(devnull), redirect_stderr(devnull):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # Extract video information first
                    info = ydl.extract_info(url, download=False)
                    
                    if info is None:
                        raise VideoDownloadError("Could not extract video information")
                    
                    # Get video metadata
                    title = info.get('title', 'Unknown Title')
                    duration = info.get('duration', 0)
                    uploader = info.get('uploader', 'Unknown')
                    view_count = info.get('view_count', 0)
                    
                    # Perform the actual download
                    ydl.download([url])
                    
                    # Try to find the downloaded file
                    # yt-dlp may change the filename during download
                    expected_filename = ydl.prepare_filename(info)
                    file_path = Path(expected_filename)
                    
                    # Check if file exists
                    if file_path.exists():
                        file_size = file_path.stat().st_size
                        mime_type = get_mime_type(str(file_path))
                        
                        return {
                            'success': True,
                            'message': f'Successfully downloaded: {title}',
                            'file_path': str(file_path),
                            'file_name': file_path.name,
                            'file_size': file_size,
                            'mime_type': mime_type,
                            'title': title,
                            'duration': duration,
                            'uploader': uploader,
                            'view_count': view_count,
                        }
                    else:
                        # File might have been post-processed, try to find it
                        possible_files = list(file_path.parent.glob(f"{file_path.stem}.*"))
                        if possible_files:
                            actual_file = possible_files[0]
                            file_size = actual_file.stat().st_size
                            mime_type = get_mime_type(str(actual_file))
                            
                            return {
                                'success': True,
                                'message': f'Successfully downloaded: {title}',
                                'file_path': str(actual_file),
                                'file_name': actual_file.name,
                                'file_size': file_size,
                                'mime_type': mime_type,
                                'title': title,
                                'duration': duration,
                                'uploader': uploader,
                                'view_count': view_count,
                            }
                        else:
                            raise VideoDownloadError("Download completed but file not found")
                
                except yt_dlp.DownloadError as e:
                    raise VideoDownloadError(f"yt-dlp download error: {str(e)}")
                
                except Exception as e:
                    raise VideoDownloadError(f"Unexpected error during download: {str(e)}")


async def serve() -> None:
    """
    Run the MCP server with video download tool.
    
    This function initializes the MCP server and registers the following tools:
    1. download_video: Advanced video downloading tool using yt-dlp
    
    The server runs indefinitely, handling tool requests from MCP clients.
    """
    
    import sys
    print("Starting MCP Video Downloader Server...", file=sys.stderr)
    
    server = Server("mcp-video-downloader")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """
        List all available tools for the MCP server.
        
        Returns:
            List of Tool objects describing available functionality
        """
        return [
            
            # A video download tool
            Tool(
                name="download_video",
                description="""
                Download videos from various platforms (YouTube, Vimeo, etc.) using yt-dlp.
                
                This tool supports:
                - Multiple video platforms through yt-dlp
                - Quality selection and format options
                - Progress tracking and detailed feedback
                - Saving files directly to the local filesystem via Docker volume mount
                
                The tool will download the video to the /downloads directory (mounted as a volume),
                making it immediately available to the user's local filesystem.
                """.strip(),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL of the video to download. Supports YouTube, Vimeo, and many other platforms.",
                        },
                        "quality": {
                            "type": "string",
                            "enum": ["best", "worst", "720p", "480p", "360p"],
                            "description": "Video quality preference. 'best' downloads highest available quality, others limit maximum resolution.",
                            "default": "720p"
                        }
                    },
                    "required": ["url"],
                },
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Handle tool execution requests.
        
        This function routes tool calls to the appropriate handler based on the
        tool name and processes the arguments accordingly.
        
        Args:
            name: The name of the tool to execute
            arguments: Dictionary of arguments for the tool
        
        Returns:
            List of TextContent objects containing the tool's response
        """
        
        if name == "download_video":
            # Handle the video download tool
            try:
                url = arguments["url"]
                quality = arguments.get("quality", "720p")
                
                # Validate URL
                if not url or not isinstance(url, str):
                    return [TextContent(
                        type="text", 
                        text="Error: Invalid URL provided. Please provide a valid video URL."
                    )]
                
                # Map quality setting to yt-dlp format selector
                quality_map = {
                    "best": "best",
                    "worst": "worst", 
                    "720p": "best[height<=720]",
                    "480p": "best[height<=480]",
                    "360p": "best[height<=360]"
                }
                format_selector = quality_map.get(quality, "best[height<=720]")
                
                # Perform the download
                result = await download_video_async(
                    url=url,
                    format_selector=format_selector
                )
                
                if result["success"]:
                    # Format successful download response
                    file_size_mb = result["file_size"] / (1024 * 1024)
                    duration_min = result.get("duration", 0) / 60 if result.get("duration") else 0
                    
                    response_parts = [
                        f"✅ Video downloaded successfully!",
                        f"",
                        f"📹 Title: {result['title']}",
                        f"👤 Uploader: {result.get('uploader', 'Unknown')}",
                        f"⏱️ Duration: {duration_min:.1f} minutes" if duration_min > 0 else "",
                        f"👀 Views: {result.get('view_count', 'Unknown'):,}" if result.get('view_count') else "",
                        f"",
                        f"📁 File Details:",
                        f"  • Name: {result['file_name']}",
                        f"  • Size: {file_size_mb:.1f} MB",
                        f"  • Type: {result.get('mime_type', 'Unknown')}",
                        f"  • Format: Video",
                        f"",
                        f"� File Location:",
                        f"  • Container path: {result['file_path']}",
                        f"  • Local path: Available via mounted volume",
                        f"  • Status: Saved to local filesystem",
                        f"",
                        f"💡 The file has been saved to your local downloads directory",
                        f"   via the Docker volume mount. You can access it directly",
                        f"   from your filesystem at the configured mount point.",
                        f"",
                    ]
                    
                    response_parts.append("Progress Log:")
                    
                    # Add progress messages
                    for msg in result.get("progress_log", []):
                        response_parts.append(f"  • {msg}")
                    
                    response_text = "\n".join(filter(None, response_parts))
                    
                else:
                    response_text = f"❌ Download failed: {result['message']}"
                
                return [TextContent(type="text", text=response_text)]
            
            except VideoDownloadError as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Video download error: {str(e)}"
                )]
            
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Unexpected error: {str(e)}. Please check the URL and try again."
                )]
        
        else:
            # Unknown tool
            return [TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}. Available tools: download_video"
            )]

    # Initialize and run the server
    print("Initializing server options...", file=sys.stderr)
    options = server.create_initialization_options()
    print("Starting stdio server...", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        print("Server started, beginning main loop...", file=sys.stderr)
        await server.run(read_stream, write_stream, options)


if __name__ == "__main__":
    # This allows the module to be run directly for testing
    asyncio.run(serve())
