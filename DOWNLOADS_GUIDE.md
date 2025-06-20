# Video Downloads Guide

## Overview

The MCP Video Downloader uses a **streaming-based architecture** that transfers downloaded videos directly to the client as base64-encoded data. No persistent storage or volume mounting is required.

## How File Transfer Works

**Streaming Architecture**: Videos are downloaded temporarily and immediately streamed to the client

All downloaded videos are transferred directly to your MCP client (such as Claude Desktop) through the protocol itself.

## How It Works

1. **Temporary Download**: Videos are downloaded to temporary storage inside the container
2. **Base64 Encoding**: Files are encoded as base64 data for transfer
3. **Direct Streaming**: Encoded content is sent directly via MCP protocol
4. **Automatic Cleanup**: Temporary files are removed after successful transfer

## Docker Command

Simple Docker command with no volume mounting required:

```bash
docker run -i --rm mcp-video-downloader
```

No additional configuration or volume mounting needed!

## File Availability

### Direct Transfer:

Downloaded videos are immediately available in your MCP client session. For Claude Desktop users, files are transferred directly and ready for use.

```python
# Get the downloads directory path
downloads_path = client.get_downloads_directory()
print(f"Files saved to: {downloads_path}")
```

### Via Finder (macOS):

```bash
open ~/Downloads/mcp-videos
```

### Via Terminal:

````bash

### Example Python Usage:

```python
from streaming_video_client import MCPVideoDownloaderClient

# Simple streaming client usage
client = MCPVideoDownloaderClient("docker run -i --rm mcp-video-downloader")

# Download video - file content is returned directly
file_content, metadata = client.download_video("https://youtube.com/watch?v=example")

# File content is available immediately
print(f"Downloaded {metadata['filename']} ({metadata['size']} bytes)")
````

## File Handling

Downloaded files come with rich metadata:

- **Filename**: Original video title with proper extension
- **Content**: Base64-encoded file data ready for use
- **Metadata**: Duration, format, size, and uploader information

## Benefits

1. ✅ **Zero Configuration**: No volume mounting or directory setup required
2. ✅ **Immediate Access**: Files are available instantly via MCP protocol
3. ✅ **Clean Operation**: No persistent files or cleanup needed
4. ✅ **Universal Compatibility**: Works with any MCP client
5. ✅ **Lightweight**: Minimal container footprint and dependencies
