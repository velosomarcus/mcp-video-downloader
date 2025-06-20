# Universal MCP Video Downloader Setup

## Problem Solved

This setup provides a **streaming-based video downloader** that works seamlessly with any MCP client. Downloaded videos are streamed directly to the client as base64-encoded data, eliminating the need for persistent file storage or complex volume mounting.

## Solution Overview

We've implemented a **streaming-based solution** that works universally with any MCP client:

1. **Streaming Server**: Downloads videos to temporary storage and streams content as base64 data
2. **No File Persistence**: Videos are transferred directly to the client, no local storage needed
3. **Universal Compatibility**: Works with Claude Desktop, VS Code, Python clients, and any other MCP client

## Quick Start

### For Claude Desktop Users

1. **Use the wrapper script** in your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "video-downloader": {
      "command": "/Users/mveloso/Vsc/mcp-video-downloader/run-mcp-video-downloader.sh",
      "args": []
    }
  }
}
```

2. **That's it!** Downloaded videos will be streamed directly to Claude as base64 data.

### For Any Other MCP Client

Simply use the wrapper script or Docker directly:

```bash
./run-mcp-video-downloader.sh
```

Or directly with Docker:

```bash
docker run -i --rm mcp-video-downloader
```

## What Happens Now

### 🎯 Streaming-Based Behavior

- **Any MCP Client** → Downloads video to temporary storage → Streams file content as base64 to client
- **No Persistent Storage**: Files are cleaned up automatically after streaming
- **Direct Transfer**: Client receives file data immediately without needing to access container filesystem

### 📁 Data Flow

- **Download Process**: Videos downloaded to temporary directory inside container
- **Data Transfer**: File content encoded as base64 and streamed to MCP client
- **Cleanup**: Temporary files automatically removed after transfer
- **Client Handling**: MCP client receives file data and can save/process as needed

## How It Works

### 1. Streaming Server Architecture

```python
# Server downloads to temporary directory and streams content
with tempfile.TemporaryDirectory() as temp_dir:
    # Download video to temporary location
    output_dir = Path(temp_dir)
    # ... download process ...

    # Encode file to base64 and return to client
    file_data = encode_file_to_base64(str(file_path))
    return {
        'success': True,
        'file_data': file_data,  # Base64-encoded content
        'file_name': file_name,
        'file_size': file_size,
        'mime_type': mime_type
    }
```

### 2. MCP Protocol Integration

The server uses the MCP (Model Context Protocol) to:

- Accept download requests with video URLs and options
- Provide real-time progress updates during download
- Stream completed files as base64-encoded binary data
- Clean up temporary files automatically

### 3. Universal Client Compatibility

- ✅ **Claude Desktop**: Receives streamed file data directly
- ✅ **VS Code Extensions**: Gets file content via MCP protocol
- ✅ **Python Clients**: Can process base64 data as needed
- ✅ **Any MCP Client**: Standard MCP protocol ensures compatibility

## Server Response Format

When a video is successfully downloaded, the server returns structured data:

```json
{
  "success": true,
  "message": "Successfully downloaded: Video Title",
  "file_data": "base64-encoded-file-content...",
  "file_name": "Video Title.mp4",
  "file_size": 15728640,
  "mime_type": "video/mp4",
  "duration": 120,
  "title": "Video Title",
  "progress_log": ["Starting download...", "Download complete"]
}
```

## Available Tools

### download_video

Downloads videos from various platforms and streams the content to the client.

**Parameters:**

- `url` (required): Video URL to download
- `format_selector` (optional): Video quality/format (default: "best[height<=720]")
- `extract_audio` (optional): Extract audio only as MP3 (default: false)

**Example Usage:**

```python
# Download video in default quality
result = await client.call_tool("download_video", {"url": "https://example.com/video"})

# Download high quality video
result = await client.call_tool("download_video", {
    "url": "https://example.com/video",
    "format_selector": "best[height<=1080]"
})

# Extract audio only
result = await client.call_tool("download_video", {
    "url": "https://example.com/video",
    "extract_audio": true
})
```

## Advanced Usage

### Running with Docker

Direct Docker usage:

```bash
docker run -i --rm mcp-video-downloader
```

### Custom Configuration

The server automatically handles temporary file management and cleanup. No additional configuration is needed for basic usage.

### Integration with MCP Clients

The server follows the standard MCP protocol, making it compatible with any MCP client implementation.

## Troubleshooting

### Download Failures

1. **Check URL validity**: Ensure the video URL is accessible and supported by yt-dlp
2. **Network issues**: Verify internet connectivity and firewall settings
3. **Format availability**: Try different format selectors if specific quality fails
4. **Platform support**: Check if the video platform is supported by yt-dlp

### For Claude Desktop

1. **Update configuration**: Use absolute path to wrapper script in MCP config
2. **Restart Claude**: After changing MCP configuration
3. **Check logs**: Look for error messages in Claude's MCP logs
4. **Test connection**: Try a simple video download to verify setup

### For Custom Clients

1. **MCP protocol**: Ensure client properly implements MCP tool calling
2. **Base64 handling**: Verify client can process base64-encoded file data
3. **Error handling**: Check client error handling for failed downloads
4. **JSON parsing**: Ensure proper parsing of server response format

## Benefits

✅ **Universal Compatibility**: Works with any MCP client via standard protocol
✅ **Streaming Transfer**: Files transferred directly to client as base64 data  
✅ **No Storage Management**: Automatic temporary file cleanup
✅ **Easy Integration**: Standard MCP tool interface
✅ **Real-time Progress**: Live download progress updates
✅ **Flexible Formats**: Support for video and audio-only downloads  
✅ **Platform Support**: Works with YouTube, Vimeo, and many other platforms

## Files and Components

- `src/mcp_video_downloader/server.py` - Main MCP server implementation
- `run-mcp-video-downloader.sh` - Wrapper script for easy execution
- `Dockerfile` - Container configuration for deployment
- `pyproject.toml` - Python dependencies and project configuration

## Next Steps

1. **Configure your MCP client** to use the video downloader server
2. **Test with a short video download** to verify the streaming functionality
3. **Enjoy seamless video downloads** with automatic base64 streaming!

---

**Note**: This streaming-based solution works with Claude Desktop, VS Code MCP extensions, Python MCP clients, and any other MCP client implementation that supports the standard MCP protocol.
