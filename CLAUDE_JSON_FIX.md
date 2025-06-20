# Claude IDE JSON Error Fix

## Problem

Claude IDE shows the error: `"Unexpected token 'd', "[download] "... is not a valid JSON"`

## Root Cause

The error occurs because yt-dlp (or other components) are outputting non-JSON text to stdout, which interferes with the MCP JSON protocol that Claude IDE expects.

## Solutions

### Solution 1: Updated Configuration (Try First)

Use this improved Claude Desktop configuration:

```json
{
  "mcpServers": {
    "video-downloader-streaming": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--env",
        "PYTHONUNBUFFERED=1",
        "mcp-video-downloader"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Solution 2: Wrapper Script (If Solution 1 Fails)

1. **Create wrapper script** (`mcp_wrapper.sh`):

```bash
#!/bin/bash
# Redirect stderr to prevent JSON contamination
exec python -m mcp_video_downloader 2>/dev/null
```

2. **Create wrapper Dockerfile** (`Dockerfile.wrapper`):

```dockerfile
FROM mcp-video-downloader

COPY mcp_wrapper.sh /usr/local/bin/mcp_wrapper.sh
RUN chmod +x /usr/local/bin/mcp_wrapper.sh

ENTRYPOINT ["/usr/local/bin/mcp_wrapper.sh"]
```

3. **Build wrapper image**:

```bash
chmod +x mcp_wrapper.sh
docker build -f Dockerfile.wrapper -t mcp-video-downloader-wrapper .
```

4. **Use wrapper configuration**:

```json
{
  "mcpServers": {
    "video-downloader-wrapper": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp-video-downloader-wrapper"]
    }
  }
}
```

### Solution 3: Direct Python (Alternative)

If Docker issues persist, use Python directly:

```json
{
  "mcpServers": {
    "video-downloader-python": {
      "command": "python",
      "args": ["-m", "mcp_video_downloader"],
      "cwd": "/path/to/your/mcp-video-downloader",
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Code Changes Made

### Server Improvements (`src/mcp_video_downloader/server.py`):

- Added `noprogress: True` to yt-dlp options
- Wrapped yt-dlp execution with `redirect_stdout` and `redirect_stderr`
- Enhanced progress logger error handling
- Suppressed all potential output sources

### Entry Point Fixes (`src/mcp_video_downloader/__init__.py`):

- Improved error handling in main function
- Ensured errors go to stderr, not stdout
- Added graceful shutdown handling

## Testing

Run the fix script to test and generate configurations:

```bash
python3 fix_claude_json.py
```

This will:

1. Test the basic MCP protocol
2. Generate appropriate configuration files
3. Create wrapper solutions if needed

## Quick Setup Steps

1. **Rebuild Docker image** (with latest fixes):

   ```bash
   docker build -t mcp-video-downloader .
   ```

2. **Test the configuration**:

   ```bash
   python3 fix_claude_json.py
   ```

3. **Update Claude Desktop**:

   - Copy configuration from generated file
   - Paste into Claude Desktop config
   - Restart Claude Desktop

4. **Test in Claude IDE**:
   ```
   "Download this video: https://youtu.be/dQw4w9WgXcQ"
   ```

## Troubleshooting

### If JSON errors persist:

1. Check Docker logs: `docker logs [container_id]`
2. Test manually: `echo '{"jsonrpc":"2.0","id":"1","method":"initialize",...}' | docker run -i mcp-video-downloader`
3. Use the wrapper solution (Solution 2)
4. Try Python direct execution (Solution 3)

### If downloads fail:

1. Check video URL is accessible
2. Verify ffmpeg is installed (for audio extraction)
3. Try smaller video files first
4. Check Docker container has internet access

## Key Changes Summary

- ✅ Suppressed all yt-dlp output to stdout/stderr
- ✅ Added proper JSON protocol protection
- ✅ Created wrapper solutions for problematic environments
- ✅ Enhanced error handling and logging
- ✅ Multiple configuration options for different scenarios

The streaming approach now properly maintains JSON protocol compliance while downloading and streaming video files to Claude IDE!
