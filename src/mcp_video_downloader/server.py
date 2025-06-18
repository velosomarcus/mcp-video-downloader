"""
Enhanced MCP Server with Hello World and Video Download Tools

This module implements a Model Context Protocol (MCP) server that provides two tools:
1. hello-world: A simple greeting tool (original functionality)
2. download_video: A video download tool using yt-dlp for downloading videos from various platforms

The server uses the MCP framework to expose these tools to AI assistants, allowing them to:
- Generate custom greetings
- Download videos from supported platforms like YouTube, Vimeo, etc.

Architecture:
- Uses async/await pattern for non-blocking operations
- Implements proper error handling and validation
- Provides detailed progress feedback for video downloads
- Supports various video formats and quality options

Dependencies:
- mcp: Model Context Protocol framework
- yt-dlp: YouTube-dl fork for video downloading
- pydantic: Data validation and settings management
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import yt_dlp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# User agent strings for the MCP server
DEFAULT_USER_AGENT_AUTONOMOUS = "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)"
DEFAULT_USER_AGENT_MANUAL = "ModelContextProtocol/1.0 (User-Specified; +https://github.com/modelcontextprotocol/servers)"


class VideoDownloadError(Exception):
    """Custom exception for video download errors."""
    pass


class ProgressLogger:
    """
    Progress logger for yt-dlp downloads.
    
    This class handles progress updates during video downloads and provides
    meaningful feedback about the download status.
    """
    
    def __init__(self):
        self.status_messages = []
    
    def __call__(self, d: Dict[str, Any]) -> None:
        """
        Progress hook for yt-dlp.
        
        Args:
            d: Dictionary containing download progress information
        """
        if d['status'] == 'downloading':
            # Extract progress information
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


async def download_video_async(
    url: str,
    output_path: Optional[str] = None,
    format_selector: str = "best[height<=720]",
    extract_audio: bool = False
) -> Dict[str, Any]:
    """
    Asynchronously download a video using yt-dlp.
    
    This function provides a high-level interface for downloading videos from
    various platforms. It handles format selection, output path management,
    and progress tracking.
    
    Args:
        url: The URL of the video to download
        output_path: Optional custom output directory (defaults to temp dir)
        format_selector: yt-dlp format selector string (default: best quality up to 720p)
        extract_audio: Whether to extract audio only (default: False)
    
    Returns:
        Dictionary containing download results:
        - success: Boolean indicating if download succeeded
        - message: Status message
        - file_path: Path to downloaded file (if successful)
        - file_size: Size of downloaded file in bytes (if successful)
        - duration: Video duration in seconds (if available)
        - title: Video title (if available)
        - progress_log: List of progress messages
    
    Raises:
        VideoDownloadError: If download fails or URL is invalid
    """
    
    # Set up output directory
    if output_path is None:
        output_path = tempfile.gettempdir()
    
    output_dir = Path(output_path)
    output_dir.mkdir(exist_ok=True)
    
    # Initialize progress logger
    progress_logger = ProgressLogger()
    
    # Configure yt-dlp options
    ydl_opts = {
        'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
        'format': 'bestaudio/best' if extract_audio else format_selector,
        'noplaylist': True,  # Download single video only
        'extract_flat': False,
        'writeinfojson': False,  # Don't save metadata files
        'writesubtitles': False,  # Don't download subtitles
        'progress_hooks': [progress_logger],
        'quiet': True,  # Suppress most output
        'no_warnings': True,
    }
    
    # Add audio extraction options if needed
    if extract_audio:
        ydl_opts.update({
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    
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
    the async event loop during downloads.
    
    Args:
        url: Video URL to download
        ydl_opts: yt-dlp configuration options
    
    Returns:
        Dictionary with download results
    """
    
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
            
            # Check if file exists and get its size
            if file_path.exists():
                file_size = file_path.stat().st_size
                
                return {
                    'success': True,
                    'message': f'Successfully downloaded: {title}',
                    'file_path': str(file_path),
                    'file_size': file_size,
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
                    
                    return {
                        'success': True,
                        'message': f'Successfully downloaded: {title}',
                        'file_path': str(actual_file),
                        'file_size': file_size,
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
    Run the enhanced MCP server with hello-world and video download tools.
    
    This function initializes the MCP server and registers two tools:
    1. hello-world: Simple greeting tool for testing
    2. download_video: Advanced video downloading tool using yt-dlp
    
    The server runs indefinitely, handling tool requests from MCP clients.
    """
    
    server = Server("mcp-hello-world-enhanced")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """
        List all available tools for the MCP server.
        
        Returns:
            List of Tool objects describing available functionality
        """
        return [
            # Original hello-world tool
            Tool(
                name="hello-world",
                description="A simple tool that returns a customized greeting message.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "greeting": {
                            "type": "string",
                            "description": "The greeting message to customize and return.",
                        }
                    },
                    "required": ["greeting"],
                },
            ),
            
            # New video download tool
            Tool(
                name="download_video",
                description="""
                Download videos from various platforms (YouTube, Vimeo, etc.) using yt-dlp.
                
                This tool supports:
                - Multiple video platforms through yt-dlp
                - Quality selection and format options
                - Audio-only extraction
                - Progress tracking and detailed feedback
                - Automatic file management
                
                The tool will download the video to a temporary directory and provide
                information about the downloaded file including path, size, and metadata.
                """.strip(),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL of the video to download. Supports YouTube, Vimeo, and many other platforms.",
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Optional: Custom output directory path. If not provided, uses system temp directory.",
                        },
                        "quality": {
                            "type": "string",
                            "enum": ["best", "worst", "720p", "480p", "360p"],
                            "description": "Video quality preference. 'best' downloads highest available quality, others limit maximum resolution.",
                            "default": "720p"
                        },
                        "audio_only": {
                            "type": "boolean",
                            "description": "If true, extracts audio only (MP3 format). If false, downloads video.",
                            "default": False
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
        
        if name == "hello-world":
            # Handle the original hello-world tool
            greeting = arguments.get("greeting", "Hello")
            response_text = f"{greeting} World!"
            
            return [TextContent(type="text", text=response_text)]
        
        elif name == "download_video":
            # Handle the video download tool
            try:
                url = arguments["url"]
                output_path = arguments.get("output_path")
                quality = arguments.get("quality", "720p")
                audio_only = arguments.get("audio_only", False)
                
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
                    output_path=output_path,
                    format_selector=format_selector,
                    extract_audio=audio_only
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
                        f"📁 File: {result['file_path']}",
                        f"💾 Size: {file_size_mb:.1f} MB",
                        f"🔧 Mode: {'Audio Only (MP3)' if audio_only else 'Video'}",
                        f"",
                        f"Progress Log:",
                    ]
                    
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
                text=f"❌ Unknown tool: {name}. Available tools: hello-world, download_video"
            )]

    # Initialize and run the server
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


if __name__ == "__main__":
    # This allows the module to be run directly for testing
    asyncio.run(serve())
    