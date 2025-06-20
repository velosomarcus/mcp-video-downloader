"""
MCP Server with Video Download Tools

This module implements a Model Context Protocol (MCP) server that provides the following tools:
1. download_video: A video download tool using yt-dlp for downloading videos from various platforms

The server uses the MCP framework to expose these tools to AI assistants, allowing them to:
- Download videos from supported platforms like YouTube, Vimeo, etc.
- Stream downloaded files directly to the client as base64-encoded data

Architecture:
- Uses async/await pattern for non-blocking operations
- Implements proper error handling and validation
- Provides detailed progress feedback for video downloads
- Supports various video formats and quality options
- Streams file contents to client instead of saving to mounted volumes

Dependencies:
- mcp: Model Context Protocol framework
- yt-dlp: YouTube-dl fork for video downloading
- pydantic: Data validation and settings management
"""

import asyncio
import base64
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import yt_dlp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, BlobResourceContents

# User agent strings for the MCP server
DEFAULT_USER_AGENT_AUTONOMOUS = "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)"
DEFAULT_USER_AGENT_MANUAL = "ModelContextProtocol/1.0 (User-Specified; +https://github.com/modelcontextprotocol/servers)"


class VideoDownloadError(Exception):
    """Custom exception for video download errors."""
    pass


def encode_file_to_base64(file_path: str) -> str:
    """
    Encode a file to base64 string for streaming to client.
    
    Args:
        file_path: Path to the file to encode
    
    Returns:
        Base64 encoded string of the file contents
    """
    with open(file_path, 'rb') as f:
        file_data = f.read()
        return base64.b64encode(file_data).decode('utf-8')


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
    format_selector: str = "best[height<=720]",
    extract_audio: bool = False
) -> Dict[str, Any]:
    """
    Asynchronously download a video using yt-dlp and return file data.
    
    This function provides a high-level interface for downloading videos from
    various platforms. It downloads to a temporary directory and returns the
    file content as base64-encoded data for streaming to the client.
    
    Args:
        url: The URL of the video to download
        format_selector: yt-dlp format selector string (default: best quality up to 720p)
        extract_audio: Whether to extract audio only (default: False)
    
    Returns:
        Dictionary containing download results:
        - success: Boolean indicating if download succeeded
        - message: Status message
        - file_data: Base64-encoded file content (if successful)
        - file_name: Original filename (if successful)
        - file_size: Size of downloaded file in bytes (if successful)
        - mime_type: MIME type of the file (if successful)
        - duration: Video duration in seconds (if available)
        - title: Video title (if available)
        - progress_log: List of progress messages
    
    Raises:
        VideoDownloadError: If download fails or URL is invalid
    """
    
    # Create a temporary directory for downloads
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        
        # Initialize progress logger
        progress_logger = ProgressLogger()
        
        # Configure yt-dlp options with complete output suppression
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
            'noprogress': True,  # Disable progress output
            'logger': None,  # Disable logging
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
    the async event loop during downloads. It downloads the file and
    returns the file content as base64-encoded data.
    
    All stdout/stderr output is suppressed to prevent interference with MCP protocol.
    
    Args:
        url: Video URL to download
        ydl_opts: yt-dlp configuration options
    
    Returns:
        Dictionary with download results including base64-encoded file data
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
                    
                    # Check if file exists and encode it
                    if file_path.exists():
                        file_size = file_path.stat().st_size
                        file_data = encode_file_to_base64(str(file_path))
                        mime_type = get_mime_type(str(file_path))
                        
                        return {
                            'success': True,
                            'message': f'Successfully downloaded: {title}',
                            'file_data': file_data,
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
                            file_data = encode_file_to_base64(str(actual_file))
                            mime_type = get_mime_type(str(actual_file))
                            
                            return {
                                'success': True,
                                'message': f'Successfully downloaded: {title}',
                                'file_data': file_data,
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
                - Audio-only extraction
                - Progress tracking and detailed feedback
                - Streaming file content directly to client as base64-encoded data
                
                The tool will download the video to a temporary location, encode it as base64,
                and return the file data directly to the client along with metadata.
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
        
        if name == "download_video":
            # Handle the video download tool
            try:
                url = arguments["url"]
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
                        f"",
                        f"📁 File Details:",
                        f"  • Name: {result['file_name']}",
                        f"  • Size: {file_size_mb:.1f} MB",
                        f"  • Type: {result.get('mime_type', 'Unknown')}",
                        f"  • Format: {'Audio Only (MP3)' if audio_only else 'Video'}",
                        f"",
                        f"📤 File Status:",
                        f"  • Streamed to client: Yes",
                        f"  • Base64 encoded: Yes",
                        f"  • Data size: {len(result['file_data'])} characters",
                        f"",
                        f"💡 The file has been encoded and streamed to the client.",
                        f"   The client can decode and save it locally.",
                        f"",
                    ]
                    
                    response_parts.append("Progress Log:")
                    
                    # Add progress messages
                    for msg in result.get("progress_log", []):
                        response_parts.append(f"  • {msg}")
                    
                    # Add file data as a separate field (this will be handled by the client)
                    response_parts.extend([
                        f"",
                        f"📦 File Data (Base64):",
                        f"FILE_DATA_START",
                        result['file_data'],
                        f"FILE_DATA_END",
                        f"",
                        f"📝 Metadata:",
                        f"FILENAME: {result['file_name']}",
                        f"MIME_TYPE: {result.get('mime_type', 'application/octet-stream')}",
                        f"SIZE: {result['file_size']}"
                    ])
                    
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
