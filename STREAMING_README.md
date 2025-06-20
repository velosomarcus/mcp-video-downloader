# MCP Video Downloader - Streaming Edition

This is a modified version of the MCP Video Downloader that **streams downloaded files directly to the client** instead of using Docker volume mounts. This approach eliminates the need for volume configuration and makes the system more portable.

## What Changed

### Before (Volume-based approach):

- Downloaded files to `/downloads` directory inside Docker container
- Required volume mount: `-v ~/Downloads/mcp-videos:/downloads`
- Files were accessible through the mounted volume
- Docker configuration was required for file persistence

### After (Streaming approach):

- Downloads files to temporary directory inside container
- Encodes file content as base64
- Streams file data directly to client through MCP protocol
- Client decodes and saves files locally
- No volume mounts required!

## Architecture

```
┌─────────────────┐    MCP Protocol    ┌──────────────────┐
│                 │◄──────────────────►│                  │
│  MCP Client     │                    │   MCP Server     │
│                 │                    │   (Container)    │
│  • Receives     │                    │   • Downloads    │
│    base64 data  │                    │     to temp dir  │
│  • Decodes      │                    │   • Encodes as   │
│  • Saves locally│                    │     base64       │
│                 │                    │   • Streams data │
└─────────────────┘                    └──────────────────┘
         │                                       │
         ▼                                       ▼
┌─────────────────┐                    ┌──────────────────┐
│ ~/Downloads/    │                    │ /tmp/downloads   │
│ mcp-videos/     │                    │ (temporary)      │
│                 │                    │                  │
│ • video1.mp4    │                    │ • Cleaned up     │
│ • audio1.mp3    │                    │   after stream   │
└─────────────────┘                    └──────────────────┘
```

## Benefits of Streaming Approach

1. **No Volume Configuration**: No need to set up Docker volume mounts
2. **Portable**: Works anywhere without Docker volume setup
3. **Secure**: Files don't persist in container after transfer
4. **Flexible**: Client controls where files are saved
5. **Cross-platform**: Works consistently across different environments

## Usage

### Running with Python (Development)

```bash
# Start the streaming client
python streaming_video_client.py "python -m mcp_video_downloader" "https://youtu.be/VIDEO_ID"
```

### Running with Docker (No Volume Mount Needed!)

```bash
# Build container
docker build -t mcp-video-downloader .

# Run with streaming client (no -v flag needed!)
python streaming_video_client.py "docker run -i mcp-video-downloader" "https://youtu.be/VIDEO_ID"
```

### Programmatic Usage

```python
from streaming_video_client import MCPStreamingVideoClient

# Create client
client = MCPStreamingVideoClient("python -m mcp_video_downloader")

# Connect and download
client.connect()
result = client.download_video("https://youtu.be/VIDEO_ID", quality="720p")
client.disconnect()

# File is automatically saved to ~/Downloads/mcp-videos/
```

## Client Features

The `MCPStreamingVideoClient` provides:

- **Automatic file decoding**: Handles base64 decoding automatically
- **Local file management**: Saves files to specified directory
- **Filename conflict resolution**: Automatically handles duplicate filenames
- **Progress tracking**: Shows download progress from server
- **Error handling**: Robust error handling for network and decoding issues
- **Flexible configuration**: Customizable download directory

## API Changes

### Server Response Format

The server now returns file data embedded in the response:

```
📦 File Data (Base64):
FILE_DATA_START
<base64-encoded-file-content>
FILE_DATA_END

📝 Metadata:
FILENAME: video_title.mp4
MIME_TYPE: video/mp4
SIZE: 12345678
```

### Client Parsing

The client automatically:

1. Extracts base64 data between `FILE_DATA_START` and `FILE_DATA_END`
2. Parses metadata (filename, MIME type, size)
3. Decodes base64 content
4. Saves to local filesystem
5. Provides clean response without base64 data

## File Size Considerations

### Large Files

- Base64 encoding increases data size by ~33%
- Large video files may use significant memory during transfer
- Consider chunked streaming for very large files (future enhancement)

### Memory Usage

- Server: Loads entire file into memory for encoding
- Client: Loads entire base64 string into memory for decoding
- Temporary directory cleaned up automatically

## Examples

See `streaming_usage_examples.py` for comprehensive examples:

```bash
# Basic download
python streaming_usage_examples.py 1

# Audio-only download
python streaming_usage_examples.py 2

# Custom directory
python streaming_usage_examples.py 3

# Docker usage (no volume mount)
python streaming_usage_examples.py 4
```

## Migration from Volume-based Version

### Old Command:

```bash
docker run -v ~/Downloads/mcp-videos:/downloads -i mcp-video-downloader
```

### New Command:

```bash
python streaming_video_client.py "docker run -i mcp-video-downloader" "VIDEO_URL"
```

### Key Differences:

1. No `-v` volume mount flag needed
2. Use `streaming_video_client.py` instead of `video_downloader_client.py`
3. Files automatically saved to `~/Downloads/mcp-videos/` by default
4. Client handles all file management

## Limitations

1. **Memory Usage**: Large files require more memory during transfer
2. **Network Transfer**: Base64 encoding increases network usage by ~33%
3. **Single File**: Each download is a separate operation (no batch optimization yet)

## Future Enhancements

1. **Chunked Streaming**: Stream large files in chunks to reduce memory usage
2. **Compression**: Compress files before base64 encoding
3. **Progress Streaming**: Real-time progress updates during file transfer
4. **Batch Downloads**: Optimize multiple file transfers
5. **Resume Support**: Resume interrupted downloads

## Technical Details

### Base64 Encoding

- Files are encoded using Python's `base64.b64encode`
- Decoded using `base64.b64decode`
- Standard base64 encoding (RFC 4648)

### MIME Type Detection

- Automatic MIME type detection based on file extension
- Supports common video/audio formats (MP4, WebM, MP3, etc.)
- Falls back to `application/octet-stream` for unknown types

### Error Handling

- Network errors during download
- Base64 decoding errors
- File system errors during save
- Graceful cleanup of temporary files

This streaming approach makes the MCP Video Downloader more portable and easier to use while maintaining all the original functionality!

## Claude IDE Integration

### Quick Setup for Claude IDE

1. **Run the setup script**:

   ```bash
   python3 claude_ide_setup.py
   ```

2. **Choose Docker option (recommended)**:

   - Select option 1 for Docker setup
   - The script will generate and install the configuration automatically

3. **Restart Claude Desktop** to load the new configuration

### Manual Configuration

Add this to your Claude Desktop config file:

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "video-downloader-streaming": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp-video-downloader"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Usage in Claude IDE

Once configured, you can ask Claude to:

- **"Download this video: https://youtu.be/VIDEO_ID"**
- **"Download the audio from this video: https://youtu.be/VIDEO_ID"**
- **"Download this video in 720p: https://youtu.be/VIDEO_ID"**

Claude will receive the file data directly and can process it or provide information about the download.

### File Handling in Claude IDE

- Files are automatically downloaded and encoded as base64
- Claude receives the file data in the tool response
- No manual file management required
- Files are available in Claude's context for further processing
