# Universal MCP Video Downloader Setup

## Problem Solved

This setup addresses the issue where downloaded videos were trapped inside Docker containers and lost when containers exited. **Now works with ANY MCP client** including Claude Desktop, VS Code, and custom Python clients.

## Solution Overview

We've implemented a **universal solution** that works at the Docker level, making it compatible with any MCP client:

1. **Enhanced Server**: Automatically detects and uses mounted `/downloads` directory
2. **Wrapper Script**: Handles volume mounting transparently
3. **Universal Compatibility**: Works with Claude, VS Code, Python clients, and any other MCP client

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

2. **That's it!** Downloaded videos will automatically appear in `~/Downloads/mcp-videos/`

### For Any Other MCP Client

Simply use the wrapper script instead of direct Docker commands:

**Before:**

```bash
docker run -i --rm mcp-video-downloader
```

**After:**

```bash
./run-mcp-video-downloader.sh
```

## What Happens Now

### 🎯 Universal Behavior

- **Any MCP Client** → Uses wrapper script → Downloads appear in `~/Downloads/mcp-videos/`
- **Volume Mount**: Automatically configured as `-v ~/Downloads/mcp-videos:/downloads`
- **Smart Server**: Detects mounted directory and uses it by default

### 📁 File Locations

- **Downloaded Videos**: `~/Downloads/mcp-videos/`
- **Naming**: Based on video title (e.g., `"Video Title.mp4"`, `"Song Name.mp3"`)
- **Persistent**: Files remain after container exits

## How It Works

### 1. Enhanced Server Logic

```python
# Server now intelligently chooses download directory
if output_path is None:
    # Check if running with mounted downloads directory
    docker_downloads_dir = "/downloads"
    if os.path.exists(docker_downloads_dir) and os.access(docker_downloads_dir, os.W_OK):
        output_path = docker_downloads_dir  # Use mounted directory
    else:
        output_path = tempfile.gettempdir()  # Fallback to temp
```

### 2. Wrapper Script Magic

```bash
# Automatically transforms Docker command
docker run -i --rm mcp-video-downloader
# Becomes:
docker run -i --rm -v ~/Downloads/mcp-videos:/downloads mcp-video-downloader
```

### 3. Universal Compatibility

- ✅ **Claude Desktop**: Configure with wrapper script path
- ✅ **VS Code Extensions**: Use wrapper script in extension settings
- ✅ **Python Clients**: Call wrapper script instead of Docker
- ✅ **Any MCP Client**: Works with any client that can run shell commands

## Directory Structure

```
~/Downloads/mcp-videos/           # Your local downloads directory
├── "Cool Video Title.mp4"        # Downloaded videos
├── "Music Track.mp3"             # Audio-only downloads
└── "Another Video.mp4"          # More downloads...
```

## Advanced Usage

### Custom Download Directory

Modify the wrapper script to use a different directory:

```bash
# Edit run-mcp-video-downloader.sh
DOWNLOADS_DIR="/path/to/your/custom/directory"
```

### Manual Volume Mount

For direct Docker usage (advanced users):

```bash
docker run -i --rm \
  -v "$HOME/Downloads/mcp-videos:/downloads" \
  mcp-video-downloader
```

## Troubleshooting

### Downloads Not Appearing Locally

1. **Check if using wrapper script**: Make sure you're using `./run-mcp-video-downloader.sh`
2. **Verify directory creation**: Check if `~/Downloads/mcp-videos/` exists
3. **Check permissions**: Ensure directory is writable

### For Claude Desktop

1. **Update configuration**: Use absolute path to wrapper script
2. **Restart Claude**: After changing MCP configuration
3. **Check logs**: Look for volume mount confirmation messages

### For Custom Clients

1. **Use wrapper script**: Instead of direct Docker commands
2. **Check output**: Look for `Downloads will be saved to:` message
3. **Verify mount**: Should see volume mount in Docker command

## Benefits

✅ **Universal Compatibility**: Works with any MCP client
✅ **Persistent Downloads**: Files survive container restarts  
✅ **Easy Access**: Files in standard Downloads folder
✅ **No Client Changes**: Existing MCP clients work unchanged
✅ **Automatic Setup**: Wrapper handles all volume mounting
✅ **Clear Feedback**: Shows where files will be saved

## Files Created

- `run-mcp-video-downloader.sh` - Universal wrapper script
- `UNIVERSAL_SETUP.md` - This documentation
- Updated `server.py` - Enhanced with directory detection
- Updated Docker image with latest server code

## Next Steps

1. **Update your MCP client configuration** to use the wrapper script
2. **Test with a short video download** to verify setup
3. **Enjoy persistent video downloads** with any MCP client!

---

**Note**: This solution works with Claude Desktop, VS Code MCP extensions, Python MCP clients, and any other MCP client implementation.
